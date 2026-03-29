"""
Spatial Player Agent — AI that plays retro games using perceptual hashing.
Based on Firespawn Studios' technique for giving AI a sense of place.

Uses aHash (average hash) to fingerprint screen locations, remembers what
actions work where, and learns from failures with temporal decay.

Designed to work with EmulatorJS via browser automation or direct
RetroArch integration.
"""

import hashlib
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
from PIL import Image
import io
import numpy as np


# ─── Perceptual Hashing ───

def ahash(image: Image.Image, hash_size: int = 8) -> int:
    """
    Compute average hash (aHash) of an image.
    1. Resize to hash_size × hash_size
    2. Convert to grayscale
    3. Compute mean brightness
    4. Each pixel → 1 if brighter than mean, 0 otherwise
    Returns a 64-bit integer fingerprint.
    """
    # Resize and grayscale
    img = image.resize((hash_size, hash_size), Image.LANCZOS).convert('L')
    pixels = np.array(img, dtype=np.float64).flatten()

    # Mean brightness
    mean = pixels.mean()

    # Build hash: 1 if brighter than mean, 0 otherwise
    bits = (pixels > mean).astype(int)
    hash_val = 0
    for bit in bits:
        hash_val = (hash_val << 1) | bit

    return hash_val


def hamming_distance(hash1: int, hash2: int) -> int:
    """Count differing bits between two hashes."""
    return bin(hash1 ^ hash2).count('1')


def is_same_location(hash1: int, hash2: int, threshold: int = 8) -> bool:
    """Are two hashes from the same location? (threshold = max differing bits)"""
    return hamming_distance(hash1, hash2) <= threshold


def screen_changed(hash_before: int, hash_after: int, threshold: int = 8) -> bool:
    """Did the screen change significantly after an action?"""
    return hamming_distance(hash_before, hash_after) > threshold


# ─── Location Memory ───

@dataclass
class LocationMemory:
    """Memory of a specific screen location."""
    hash_val: int
    visit_count: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0
    actions: dict = field(default_factory=lambda: defaultdict(lambda: {
        'success_count': 0,
        'fail_count': 0,
        'last_success': 0.0,
        'last_fail': 0.0,
    }))

    def record_success(self, action: str, frame: int):
        self.actions[action]['success_count'] += 1
        self.actions[action]['last_success'] = frame

    def record_failure(self, action: str, frame: int):
        self.actions[action]['fail_count'] += 1
        self.actions[action]['last_fail'] = frame

    def action_score(self, action: str, current_frame: int, decay_rate: float = 0.002) -> float:
        """
        Score an action at this location.
        Successes are weighted positively, failures negatively.
        Failures decay over time (old failures matter less).
        """
        data = self.actions[action]
        success_score = data['success_count']

        # Decay failures: e^(-decay_rate * frames_since_failure)
        if data['fail_count'] > 0 and data['last_fail'] > 0:
            frames_since = current_frame - data['last_fail']
            decay = math.exp(-decay_rate * frames_since)
            fail_score = data['fail_count'] * decay
        else:
            fail_score = 0

        return success_score - fail_score

    def best_action(self, available_actions: list, current_frame: int) -> str:
        """Pick the best action at this location based on memory."""
        scores = {}
        for action in available_actions:
            scores[action] = self.action_score(action, current_frame)

        # If all scores are similar (unexplored), pick randomly
        score_range = max(scores.values()) - min(scores.values()) if scores else 0
        if score_range < 0.5:
            import random
            return random.choice(available_actions)

        return max(scores, key=scores.get)

    def untried_actions(self, available_actions: list) -> list:
        """Actions never tried at this location."""
        return [a for a in available_actions if a not in self.actions or
                (self.actions[a]['success_count'] == 0 and self.actions[a]['fail_count'] == 0)]


# ─── Spatial Memory Database ───

class SpatialMemory:
    """
    The agent's spatial memory — maps screen hashes to location memories.
    Recognizes when it's been somewhere before and what worked there.
    """

    def __init__(self, match_threshold: int = 8):
        self.locations: dict[int, LocationMemory] = {}
        self.match_threshold = match_threshold
        self.current_frame = 0

    def find_location(self, screen_hash: int) -> Optional[LocationMemory]:
        """Find a known location matching this hash (within threshold)."""
        # Exact match first
        if screen_hash in self.locations:
            return self.locations[screen_hash]

        # Fuzzy match
        for stored_hash, memory in self.locations.items():
            if hamming_distance(screen_hash, stored_hash) <= self.match_threshold:
                return memory

        return None

    def observe(self, screen_hash: int) -> LocationMemory:
        """Observe a screen. Returns existing or creates new location memory."""
        location = self.find_location(screen_hash)
        if location is None:
            location = LocationMemory(
                hash_val=screen_hash,
                first_seen=self.current_frame,
            )
            self.locations[screen_hash] = location

        location.visit_count += 1
        location.last_seen = self.current_frame
        return location

    def record_action(self, hash_before: int, hash_after: int, action: str):
        """Record the result of an action."""
        location = self.find_location(hash_before)
        if location is None:
            return

        if screen_changed(hash_before, hash_after, self.match_threshold):
            location.record_success(action, self.current_frame)
        else:
            location.record_failure(action, self.current_frame)

    def tick(self):
        """Advance frame counter."""
        self.current_frame += 1

    def stats(self) -> dict:
        """Return memory statistics."""
        total_actions = sum(
            sum(a['success_count'] + a['fail_count'] for a in loc.actions.values())
            for loc in self.locations.values()
        )
        return {
            'known_locations': len(self.locations),
            'total_visits': sum(loc.visit_count for loc in self.locations.values()),
            'total_actions_recorded': total_actions,
            'current_frame': self.current_frame,
        }


# ─── Frame Stability Detection ───

class FrameStabilizer:
    """
    Detects when screen animations have settled.
    Prevents the agent from making decisions during transitions.
    """

    def __init__(self, stability_frames: int = 3, threshold: int = 4):
        self.history: list[int] = []
        self.stability_frames = stability_frames
        self.threshold = threshold

    def is_stable(self, screen_hash: int) -> bool:
        """Has the screen been stable for enough frames?"""
        self.history.append(screen_hash)
        if len(self.history) > self.stability_frames + 1:
            self.history.pop(0)

        if len(self.history) < self.stability_frames:
            return False

        # Check if last N frames are similar
        for i in range(1, len(self.history)):
            if hamming_distance(self.history[0], self.history[i]) > self.threshold:
                return False
        return True


# ─── Game Agent ───

# Standard retro game inputs
RETRO_ACTIONS = [
    'up', 'down', 'left', 'right',
    'a', 'b', 'start', 'select',
    'up+a', 'up+b', 'right+a', 'left+a',
    'down+a', 'down+b',
]


class SpatialGameAgent:
    """
    An AI agent that plays retro games using perceptual hashing for
    spatial memory. Remembers locations, learns from actions, explores
    intelligently.
    """

    def __init__(self, actions: list = None):
        self.memory = SpatialMemory()
        self.stabilizer = FrameStabilizer()
        self.actions = actions or RETRO_ACTIONS
        self.last_hash: Optional[int] = None
        self.last_action: Optional[str] = None
        self.exploration_rate = 0.3  # 30% random exploration
        self.total_decisions = 0
        self.total_successes = 0

    def process_frame(self, frame_image: Image.Image) -> Optional[str]:
        """
        Process a game frame and decide what to do.
        Returns an action string or None if screen isn't stable yet.
        """
        current_hash = ahash(frame_image)
        self.memory.tick()

        # Wait for screen to stabilize
        if not self.stabilizer.is_stable(current_hash):
            return None

        # Record result of last action
        if self.last_hash is not None and self.last_action is not None:
            self.memory.record_action(self.last_hash, current_hash, self.last_action)
            if screen_changed(self.last_hash, current_hash):
                self.total_successes += 1

        # Observe current location
        location = self.memory.observe(current_hash)

        # Decide action
        import random
        untried = location.untried_actions(self.actions)

        if untried and random.random() < 0.5:
            # Try something new here
            action = random.choice(untried)
        elif random.random() < self.exploration_rate:
            # Random exploration
            action = random.choice(self.actions)
        else:
            # Exploit best known action
            action = location.best_action(self.actions, self.memory.current_frame)

        self.last_hash = current_hash
        self.last_action = action
        self.total_decisions += 1

        return action

    def status(self) -> dict:
        """Agent status report."""
        stats = self.memory.stats()
        return {
            **stats,
            'total_decisions': self.total_decisions,
            'total_successes': self.total_successes,
            'success_rate': (self.total_successes / max(1, self.total_decisions)) * 100,
            'exploration_rate': self.exploration_rate,
        }

    def save_memory(self, path: str):
        """Serialize spatial memory to disk."""
        import json
        data = {
            'locations': {},
            'frame': self.memory.current_frame,
        }
        for hash_val, loc in self.memory.locations.items():
            actions_data = {}
            for act, act_data in loc.actions.items():
                actions_data[act] = dict(act_data)
            data['locations'][str(hash_val)] = {
                'hash': hash_val,
                'visit_count': loc.visit_count,
                'first_seen': loc.first_seen,
                'last_seen': loc.last_seen,
                'actions': actions_data,
            }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_memory(self, path: str):
        """Load spatial memory from disk."""
        import json
        with open(path) as f:
            data = json.load(f)
        self.memory.current_frame = data.get('frame', 0)
        for hash_str, loc_data in data.get('locations', {}).items():
            hash_val = int(hash_str)
            loc = LocationMemory(
                hash_val=hash_val,
                visit_count=loc_data['visit_count'],
                first_seen=loc_data['first_seen'],
                last_seen=loc_data['last_seen'],
            )
            for act, act_data in loc_data.get('actions', {}).items():
                loc.actions[act] = act_data
            self.memory.locations[hash_val] = loc


# ─── Demo / CLI ───

if __name__ == '__main__':
    agent = SpatialGameAgent()
    print("Spatial Player Agent — Earth C-137")
    print("Perceptual hashing with temporal decay")
    print(f"Actions: {len(agent.actions)}")
    print(f"Exploration rate: {agent.exploration_rate * 100}%")
    print()

    # Demo with synthetic frames
    print("Generating synthetic test frames...")
    for i in range(100):
        # Create a simple test image that changes over time
        img = Image.new('L', (160, 144), color=int((i % 10) * 25))
        action = agent.process_frame(img.convert('RGB'))
        if action:
            print(f"  Frame {i}: hash={ahash(img.convert('RGB')):016x} → {action}")

    print()
    print("Agent status:", agent.status())
