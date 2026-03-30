# halo-ai — stamped by the architect
#!/usr/bin/env python3
"""
halo — autonomous service guardian

No timers. No intervals. Halo watches conditions and acts when they change.
Every action is reported to the activity feed. Total AI. No half measures.

Pattern: Watch → Detect → Act → Report
"""

import subprocess
import json
import time
import logging
import shlex
import sys
import os
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

# ── Configuration ──────────────────────────────────────
DATA_DIR = Path("/srv/ai/agent/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = DATA_DIR / "halo-agent.log"
STATE_FILE = DATA_DIR / "state.json"
FEED_FILE = DATA_DIR / "activity_feed.json"
MAX_RESTART_ATTEMPTS = 3
RESTART_COOLDOWN = 300
MAX_FEED_ENTRIES = 500

# ── Logging ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("halo")

# ── Services ───────────────────────────────────────────
SERVICES = {
    "halo-llama-server": {"port": 8081, "health": "/health", "critical": True, "gpu": True},
    "halo-lemonade": {"port": 8080, "health": "/health", "critical": True, "gpu": False},
    "halo-open-webui": {"port": 3000, "health": "/health", "critical": True, "gpu": False},
    "halo-vane": {"port": 3001, "health": None, "critical": False, "gpu": False},
    "halo-searxng": {"port": 8888, "health": "/", "critical": False, "gpu": False},
    "halo-qdrant": {"port": 6333, "health": "/", "critical": False, "gpu": False},
    "halo-n8n": {"port": 5678, "health": "/healthz", "critical": False, "gpu": False},
    "halo-comfyui": {"port": 8188, "health": "/", "critical": False, "gpu": True},
    "halo-man-cave": {"port": 3005, "health": "/", "critical": False, "gpu": False},
    "halo-gaia-api": {"port": 8090, "health": "/health", "critical": False, "gpu": False},
    "halo-gaia-ui": {"port": 4200, "health": "/api/health", "critical": False, "gpu": False},
    "halo-caddy": {"port": 80, "health": None, "critical": True, "gpu": False},
}

REPOS = {
    "llama-cpp": "/srv/ai/llama-cpp",
    "lemonade": "/srv/ai/lemonade",
    "open-webui": "/srv/ai/open-webui",
    "vane": "/srv/ai/vane",
    "searxng": "/srv/ai/searxng",
    "qdrant": "/srv/ai/qdrant",
    "n8n": "/srv/ai/n8n",
    "comfyui": "/srv/ai/comfyui",
    "whisper-cpp": "/srv/ai/whisper-cpp",
    "kokoro": "/srv/ai/kokoro",
    "gaia": "/srv/ai/gaia",
}

# ── Activity Feed ─────────────────────────────────────
def report(agent: str, action: str, detail: str, level: str = "info"):
    """Every agent action goes to the feed. This is how the family communicates."""
    entry = {
        "agent": agent,
        "action": action,
        "detail": detail,
        "level": level,
        "time": datetime.now().isoformat(),
    }

    # Log it
    log_fn = getattr(log, level, log.info)
    log_fn(f"[{agent}] {action} — {detail}")

    # Append to feed file
    try:
        feed = json.loads(FEED_FILE.read_text()) if FEED_FILE.exists() else []
    except (json.JSONDecodeError, OSError):
        feed = []
    feed.append(entry)
    if len(feed) > MAX_FEED_ENTRIES:
        feed = feed[-MAX_FEED_ENTRIES:]
    FEED_FILE.write_text(json.dumps(feed, indent=2))

    # Publish to message bus (fire-and-forget)
    _publish_to_bus(agent, action, detail, level)

    return entry


def _publish_to_bus(agent: str, action: str, detail: str, level: str = "info"):
    """Fire-and-forget publish to the halo-ai message bus."""
    topic = "monitoring"
    if "security" in action or "scan" in action:
        topic = "security"
    elif "build" in action or "compile" in action:
        topic = "builds"
    elif "ringbus" in action:
        topic = "monitoring"
    try:
        data = json.dumps({
            "from_agent": agent,
            "topic": topic,
            "event_type": action,
            "payload": {"detail": detail, "level": level},
        }).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:8100/publish",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass  # best-effort — don't block the watchdog


# ── State ─────────────────────────────────────────────
@dataclass
class AgentState:
    services: dict = field(default_factory=dict)
    last_known: dict = field(default_factory=dict)  # last known state per service
    updates_available: dict = field(default_factory=dict)
    total_repairs: int = 0
    total_failures: int = 0
    started_at: Optional[str] = None
    gpu_temp_last: int = 0
    mem_available_last: int = 0
    disk_usage_last: int = 0


def load_state() -> AgentState:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            state = AgentState()
            state.__dict__.update(data)
            return state
        except (json.JSONDecodeError, OSError):
            pass
    return AgentState(started_at=datetime.now().isoformat())


def save_state(state: AgentState):
    STATE_FILE.write_text(json.dumps(state.__dict__, indent=2, default=str), encoding="utf-8")


# ── Shell Helpers ─────────────────────────────────────
def run(cmd, timeout=30, shell=False):
    try:
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=shell)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except (OSError, ValueError) as e:
        return -1, "", str(e)


# ── Watchers ──────────────────────────────────────────
# Each watcher observes a condition and only acts when it CHANGES.

def watch_services(state: AgentState):
    """Watch all services. Only act when a service state CHANGES."""
    for name, config in SERVICES.items():
        # Check current state
        code, out, _ = run(["systemctl", "is-active", name])
        is_active = out == "active"

        # Health check if active
        healthy = False
        if is_active and config["health"]:
            hc, hout, _ = run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                               "--connect-timeout", "3",
                               f"http://127.0.0.1:{config['port']}{config['health']}"])
            healthy = hc == 0 and hout in ("200", "301", "302", "307", "308")
        elif is_active:
            healthy = True  # no health endpoint, trust systemd

        current = "healthy" if healthy else "down"
        previous = state.last_known.get(name, "unknown")

        # Only act on STATE CHANGE
        if current != previous:
            if current == "down" and previous != "unknown":
                # Service just went down — act
                report("halo", "service_down", f"{name} went down", "warning")
                repair_service(name, config, state)
            elif current == "healthy" and previous == "down":
                # Service came back — report recovery
                report("halo", "service_recovered", f"{name} is back", "info")
            elif current == "healthy" and previous == "unknown":
                # First check — just note it
                pass

            state.last_known[name] = current
        elif current == "down":
            # Still down from before — try repair again
            svc = state.services.get(name, {})
            cooldown = svc.get("cooldown_until")
            if cooldown and datetime.now() < datetime.fromisoformat(cooldown):
                pass  # in cooldown, wait
            else:
                repair_service(name, config, state)


def watch_gpu(state: AgentState):
    """Watch GPU temperature. Only report on significant changes."""
    temp = 0
    for hwmon in Path("/sys/class/hwmon").iterdir():
        name_file = hwmon / "name"
        if name_file.exists() and "amdgpu" in name_file.read_text():
            temp_file = hwmon / "temp1_input"
            if temp_file.exists():
                temp = int(temp_file.read_text().strip()) // 1000

    if not Path("/dev/kfd").exists():
        if state.last_known.get("gpu_device") != "missing":
            report("pulse", "gpu_missing", "/dev/kfd gone — possible driver crash", "critical")
            state.last_known["gpu_device"] = "missing"
        return

    state.last_known["gpu_device"] = "present"

    # Only report on significant temp changes (>5 degree jumps or thresholds)
    last_temp = state.gpu_temp_last
    if abs(temp - last_temp) >= 5 or (temp > 85 and last_temp <= 85) or (temp > 90 and last_temp <= 90):
        if temp > 90:
            report("pulse", "gpu_critical", f"GPU at {temp}°C — critical", "critical")
        elif temp > 85:
            report("pulse", "gpu_hot", f"GPU at {temp}°C — elevated", "warning")
        elif temp < 70 and last_temp > 85:
            report("pulse", "gpu_cooled", f"GPU cooled to {temp}°C", "info")
        state.gpu_temp_last = temp


def watch_system(state: AgentState):
    """Watch memory and disk. Only report on significant changes."""
    # Memory
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable"):
                    mem_mb = int(line.split()[1]) // 1024
                    break
    except Exception:
        mem_mb = 99999

    if mem_mb < 4096 and state.mem_available_last >= 4096:
        report("pulse", "memory_low", f"Available memory: {mem_mb}MB", "warning")
    elif mem_mb >= 4096 and state.mem_available_last < 4096:
        report("pulse", "memory_recovered", f"Memory back to {mem_mb}MB", "info")
    state.mem_available_last = mem_mb

    # Disk
    try:
        code, out, _ = run("df /srv/ai --output=pcent | tail -1 | tr -d ' %'", shell=True)
        disk_pct = int(out) if out else 0
    except Exception:
        disk_pct = 0

    if disk_pct > 90 and state.disk_usage_last <= 90:
        report("pulse", "disk_critical", f"Disk at {disk_pct}%", "critical")
    elif disk_pct > 80 and state.disk_usage_last <= 80:
        report("pulse", "disk_warning", f"Disk at {disk_pct}%", "warning")
    elif disk_pct < 80 and state.disk_usage_last >= 80:
        report("pulse", "disk_recovered", f"Disk back to {disk_pct}%", "info")
    state.disk_usage_last = disk_pct

    # CPU governor — fix silently if wrong
    code, out, _ = run(["cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"])
    if out != "performance":
        run("for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance | tee $c > /dev/null; done", shell=True)
        report("halo", "governor_fixed", f"CPU governor was '{out}', set to performance", "info")


def watch_updates(state: AgentState):
    """Watch for upstream updates. Only fetch when network is quiet."""
    # Check network load first
    try:
        with open("/proc/net/dev") as f:
            lines = f.readlines()
        b1 = sum(int(l.split()[1]) + int(l.split()[9]) for l in lines if ":" in l and "lo" not in l)
        time.sleep(1)
        with open("/proc/net/dev") as f:
            lines = f.readlines()
        b2 = sum(int(l.split()[1]) + int(l.split()[9]) for l in lines if ":" in l and "lo" not in l)
        mbps = ((b2 - b1) * 8) / 1_000_000
        if mbps > 50:
            return  # network busy, skip
    except Exception:
        pass

    updates = {}
    for name, path in REPOS.items():
        git_dir = Path(path) / ".git"
        if not git_dir.exists():
            continue
        code, _, _ = run(["git", "-C", path, "fetch", "--quiet"], timeout=30)
        if code != 0:
            continue
        code, out, _ = run(["git", "-C", path, "rev-list", "--count", "HEAD..@{u}"])
        if out and int(out) > 0:
            updates[name] = int(out)

    # Only report if updates changed
    if updates != state.updates_available:
        if updates:
            summary = ", ".join(f"{k}: {v} behind" for k, v in updates.items())
            report("sentinel", "updates_available", summary, "info")
        state.updates_available = updates


def watch_inference(state: AgentState):
    """Watch inference performance. Only report degradation."""
    code, out, _ = run([
        "curl", "-s", "http://127.0.0.1:8081/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-d", '{"model":"q","messages":[{"role":"user","content":"hi /no_think"}],"max_tokens":5,"temperature":0}',
    ], timeout=30)

    if code != 0:
        return

    try:
        result = json.loads(out)
        tok_s = result["timings"]["predicted_per_second"]
    except (json.JSONDecodeError, KeyError):
        return

    history = state.__dict__.setdefault("perf_history", [])
    history.append({"time": datetime.now().isoformat(), "tok_s": tok_s})
    if len(history) > 50:
        history[:] = history[-50:]

    if len(history) >= 5:
        avg = sum(p["tok_s"] for p in history[-5:]) / 5
        if tok_s < avg * 0.7 and tok_s > 0:
            report("mechanic", "performance_degraded",
                   f"{tok_s:.1f} tok/s (avg {avg:.1f})", "warning")


# ── Repair ────────────────────────────────────────────
def repair_service(name, config, state: AgentState):
    """Attempt repair. Report everything."""
    svc = state.services.get(name, {"restart_count": 0, "cooldown_until": None})

    if svc.get("cooldown_until"):
        try:
            if datetime.now() < datetime.fromisoformat(svc["cooldown_until"]):
                return False
        except Exception:
            pass

    if svc.get("restart_count", 0) >= MAX_RESTART_ATTEMPTS:
        svc["cooldown_until"] = (datetime.now() + timedelta(seconds=RESTART_COOLDOWN)).isoformat()
        svc["restart_count"] = 0
        state.services[name] = svc
        state.total_failures += 1
        report("halo", "repair_failed",
               f"{name} failed {MAX_RESTART_ATTEMPTS} attempts — cooldown {RESTART_COOLDOWN}s", "critical")
        return False

    report("halo", "repairing", f"restarting {name} (attempt {svc.get('restart_count', 0) + 1})", "warning")

    code, _, err = run(["systemctl", "restart", name], timeout=60)
    time.sleep(5)  # brief wait for service to initialize

    # Verify
    code, out, _ = run(["systemctl", "is-active", name])
    if out == "active":
        svc["restart_count"] = 0
        svc["cooldown_until"] = None
        state.services[name] = svc
        state.total_repairs += 1
        report("halo", "repaired", f"{name} is back online", "info")
        return True
    else:
        svc["restart_count"] = svc.get("restart_count", 0) + 1
        state.services[name] = svc
        report("halo", "repair_attempt_failed", f"{name} still down after restart", "warning")
        return False


# ── Ring Bus Watcher ─────────────────────────────────
RING_BUS_MACHINES = {
    "ryzen": "10.0.0.185",
    "strix-halo": "10.0.0.131",
    "sligar": "192.168.50.184",
    "minisforum": "10.0.0.61",
}

def watch_ring_bus(state: AgentState):
    """Watch SSH ring bus connectivity. Attempt repair on failure."""
    for name, ip in RING_BUS_MACHINES.items():
        code, out, err = run([
            "ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            f"bcloud@{ip}", "echo ok",
        ], timeout=10)
        current = "up" if code == 0 and "ok" in out else "down"
        previous = state.last_known.get(f"ringbus_{name}", "unknown")

        if current != previous:
            if current == "down" and previous != "unknown":
                report("halo", "ringbus_down", f"SSH to {name} ({ip}) failed: {err[:80]}", "warning")
                # Attempt repair: clear known_hosts and retry
                run(["ssh-keygen", "-R", ip])
                code2, out2, _ = run([
                    "ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                    "-o", "BatchMode=yes", f"bcloud@{ip}", "echo ok",
                ], timeout=15)
                if code2 == 0 and "ok" in out2:
                    report("halo", "ringbus_repaired", f"SSH to {name} restored", "info")
                    current = "up"
                else:
                    report("halo", "ringbus_repair_failed", f"{name} still unreachable", "critical")
            elif current == "up" and previous == "down":
                report("halo", "ringbus_recovered", f"SSH to {name} is back", "info")
            state.last_known[f"ringbus_{name}"] = current


# ── GlusterFS Watcher ────────────────────────────────
def watch_glusterfs(state: AgentState):
    """Watch GlusterFS volume health. Report on changes."""
    code, out, _ = run(["gluster", "volume", "status", "all"], timeout=15)
    if code != 0:
        current = "down"
    else:
        current = "healthy" if "Started" in out else "degraded"

    previous = state.last_known.get("glusterfs", "unknown")
    if current != previous:
        if current == "down" and previous != "unknown":
            report("halo", "glusterfs_down", "GlusterFS volume offline", "critical")
            # Attempt restart
            run(["systemctl", "restart", "glusterd"], timeout=30)
            time.sleep(5)
            code2, out2, _ = run(["gluster", "volume", "status", "all"], timeout=15)
            if code2 == 0 and "Started" in out2:
                report("halo", "glusterfs_repaired", "GlusterFS restored after restart", "info")
                current = "healthy"
            else:
                report("halo", "glusterfs_repair_failed", "GlusterFS still down", "critical")
        elif current == "healthy" and previous == "down":
            report("halo", "glusterfs_recovered", "GlusterFS is back", "info")
        state.last_known["glusterfs"] = current

    # Check peer status
    code, out, _ = run(["gluster", "peer", "status"], timeout=10)
    if code == 0:
        connected = out.count("Peer in Cluster (Connected)")
        disconnected = out.count("Peer in Cluster (Disconnected)")
        if disconnected > 0:
            prev_disc = state.last_known.get("gluster_disconnected", 0)
            if disconnected != prev_disc:
                report("halo", "gluster_peer_issue", f"{disconnected} peer(s) disconnected, {connected} connected", "warning")
            state.last_known["gluster_disconnected"] = disconnected
        else:
            state.last_known["gluster_disconnected"] = 0


# ── Log Rotation ──────────────────────────────────────
def rotate_logs():
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 10 * 1024 * 1024:
        rotated = LOG_FILE.with_suffix(".log.old")
        if rotated.exists():
            rotated.unlink()
        LOG_FILE.rename(rotated)
        report("halo", "log_rotated", "agent log exceeded 10MB", "info")


# ── Main Loop — Watchdog ──────────────────────────────
def main():
    state = load_state()
    if not state.started_at:
        state.started_at = datetime.now().isoformat()

    report("halo", "started", f"watching {len(SERVICES)} services, {len(REPOS)} repos")

    last_update_watch = 0
    last_inference_watch = 0

    while True:
        now = time.time()

        # Services — watch continuously, act on change
        watch_services(state)

        # GPU + System — watch continuously, act on change
        watch_gpu(state)
        watch_system(state)

        # Ring Bus — SSH mesh health, every 60 seconds
        if now - state.__dict__.get("_last_ringbus_watch", 0) >= 60:
            watch_ring_bus(state)
            state.__dict__["_last_ringbus_watch"] = now

        # GlusterFS — distributed filesystem, every 120 seconds
        if now - state.__dict__.get("_last_gluster_watch", 0) >= 120:
            watch_glusterfs(state)
            state.__dict__["_last_gluster_watch"] = now

        # Updates — only when network is quiet, no more than every 2 hours
        if now - last_update_watch >= 7200:
            watch_updates(state)
            last_update_watch = now

        # Inference — spot check, no more than every 10 minutes
        if now - last_inference_watch >= 600:
            watch_inference(state)
            last_inference_watch = now

        # Housekeeping
        rotate_logs()
        save_state(state)

        # Brief pause — not a timer, just prevents CPU spinning
        # Halo is always awake, just breathing between checks
        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        report("halo", "stopped", "stopped by user")
    except Exception as e:
        report("halo", "crashed", str(e), "critical")
        sys.exit(1)
