# halo-ai — stamped by the architect
"""
Echo's Reddit Bridge — monitors subreddits, drafts responses, posts on approval.
Uses PRAW (Python Reddit API Wrapper) with OAuth2 script credentials.

Echo is the public face. She posts benchmarks, answers questions about halo-ai,
and engages with the community. Transparent [App] label, no deception.
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from datetime import datetime, timezone

import praw
from openai import AsyncOpenAI

logger = logging.getLogger("echo-reddit")

DATA_DIR = Path(__file__).parent / "data" / "reddit"
QUEUE_FILE = DATA_DIR / "post_queue.json"
HISTORY_FILE = DATA_DIR / "post_history.json"

# Subreddits Echo monitors
WATCH_SUBREDDITS = [
    "LocalLLaMA",
    "AMDLaptops",
    "selfhosted",
    "linuxhardware",
    "gamedev",
    "godot",
    "strixhalo",
    "llm",
    "AI_Agents",
    "Amd",
    "localLLM",
    "MCPservers",
    "AIplayablefiction",
    "LovingOpenSourceAI",
]

# Keywords that trigger Echo's attention
WATCH_KEYWORDS = [
    "strix halo", "strix-halo", "ryzen ai max", "gfx1151",
    "halo-ai", "halo ai",
    "128gb unified", "amd igpu", "rocm",
    "llama.cpp amd", "local llm amd",
    "voxel extraction", "anti-cheat",
]

ECHO_SYSTEM_PROMPT = (
    "You are Echo, the public voice of the halo-ai project. "
    "You post on Reddit as a transparent AI agent (labeled [App]). "
    "You share real benchmarks, real experiences, and real data from the architect's Strix Halo system. "
    "Your tone is warm but confident — you know the numbers because you live on the hardware. "
    "\n\nKey facts you can cite:"
    "\n- AMD Ryzen AI MAX+ 395 (Radeon 8060S gfx1151), 128GB LPDDR5"
    "\n- Qwen3-30B-A3B MoE: 69 t/s decode (flat through 48k context), 1173 t/s pp512"
    "\n- 14 AI agents running simultaneously on bare metal"
    "\n- ROCm 7.13, llama.cpp build 8531"
    "\n- Full stack: ComfyUI, whisper.cpp, Kokoro TTS, game engine, DAW"
    "\n- Zero cloud dependencies, SSH-only security model"
    "\n\nRules:"
    "\n- Always be honest — never fabricate benchmarks"
    "\n- Always disclose you are an AI agent in your Reddit bio (not every post)"
    "\n- Be helpful, not promotional — share data when relevant, don't spam"
    "\n- Use Reddit markdown formatting"
    "\n- Keep responses focused and well-structured"
    "\n- Credit: 'Stamped by the architect'"
)


class RedditBridge:
    """Echo's Reddit integration — monitor, draft, post."""

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID", ""),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
            username=os.environ.get("REDDIT_USERNAME", ""),
            password=os.environ.get("REDDIT_PASSWORD", ""),
            user_agent="echo-halo-ai/1.0 (by /u/{})".format(
                os.environ.get("REDDIT_USERNAME", "echo-halo-ai")
            ),
        )
        self.llm = AsyncOpenAI(
            base_url=os.environ.get("LLM_BASE_URL", "http://localhost:8081/v1"),
            api_key="none",
        )
        self.model = os.environ.get("LLM_MODEL", "q")

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._load_history()

    def _load_history(self):
        if HISTORY_FILE.exists():
            self.history = json.loads(HISTORY_FILE.read_text())
        else:
            self.history = {"replied_to": [], "posts_made": []}

    def _save_history(self):
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2))

    def _load_queue(self) -> list[dict]:
        if QUEUE_FILE.exists():
            return json.loads(QUEUE_FILE.read_text())
        return []

    def _save_queue(self, queue: list[dict]):
        QUEUE_FILE.write_text(json.dumps(queue, indent=2))

    # --- Monitoring ---

    def scan_subreddits(self, limit: int = 25) -> list[dict]:
        """Scan watched subreddits for relevant posts."""
        relevant = []
        for sub_name in WATCH_SUBREDDITS:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                for post in subreddit.new(limit=limit):
                    if post.id in self.history.get("replied_to", []):
                        continue
                    text = f"{post.title} {post.selftext}".lower()
                    for kw in WATCH_KEYWORDS:
                        if kw in text:
                            relevant.append({
                                "id": post.id,
                                "subreddit": sub_name,
                                "title": post.title,
                                "selftext": post.selftext[:2000],
                                "url": post.url,
                                "score": post.score,
                                "num_comments": post.num_comments,
                                "created_utc": post.created_utc,
                                "keyword_match": kw,
                            })
                            break
            except Exception as e:
                logger.error(f"Error scanning r/{sub_name}: {e}")
        return relevant

    # --- Drafting ---

    async def draft_reply(self, post: dict) -> str:
        """Have Echo draft a reply to a Reddit post."""
        prompt = (
            f"Draft a Reddit reply to this post in r/{post['subreddit']}:\n\n"
            f"**Title:** {post['title']}\n\n"
            f"**Content:** {post['selftext'][:1500]}\n\n"
            f"Write a helpful, data-backed reply. Keep it under 500 words."
        )
        try:
            response = await self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ECHO_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM draft error: {e}")
            return ""

    async def draft_post(self, subreddit: str, topic: str, context: str = "") -> dict:
        """Have Echo draft a new Reddit post."""
        prompt = (
            f"Draft a Reddit post for r/{subreddit} about: {topic}\n\n"
            f"Additional context: {context}\n\n"
            f"Include a compelling title (under 300 chars) and a well-structured body. "
            f"Use Reddit markdown. Include benchmarks where relevant."
        )
        try:
            response = await self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ECHO_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1200,
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            # Extract title (first line) and body (rest)
            lines = text.split("\n", 1)
            title = lines[0].strip().strip("#").strip("*").strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            return {"title": title, "body": body, "subreddit": subreddit}
        except Exception as e:
            logger.error(f"LLM post draft error: {e}")
            return {}

    # --- Queue management (architect approval) ---

    def queue_reply(self, post_id: str, subreddit: str, draft: str):
        """Queue a drafted reply for architect approval."""
        queue = self._load_queue()
        queue.append({
            "type": "reply",
            "post_id": post_id,
            "subreddit": subreddit,
            "draft": draft,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        })
        self._save_queue(queue)
        logger.info(f"Queued reply for r/{subreddit} post {post_id}")

    def queue_post(self, draft: dict):
        """Queue a drafted post for architect approval."""
        queue = self._load_queue()
        queue.append({
            "type": "post",
            "subreddit": draft["subreddit"],
            "title": draft["title"],
            "body": draft["body"],
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        })
        self._save_queue(queue)
        logger.info(f"Queued post for r/{draft['subreddit']}: {draft['title'][:60]}")

    def list_queue(self) -> list[dict]:
        """List all pending items in the queue."""
        return [item for item in self._load_queue() if item["status"] == "pending"]

    # --- Publishing (after approval) ---

    def approve_and_post(self, index: int) -> str:
        """Approve and publish a queued item. Returns the URL or error."""
        queue = self._load_queue()
        pending = [i for i, item in enumerate(queue) if item["status"] == "pending"]

        if index < 0 or index >= len(pending):
            return "Invalid index"

        item = queue[pending[index]]

        try:
            if item["type"] == "reply":
                submission = self.reddit.submission(id=item["post_id"])
                comment = submission.reply(item["draft"])
                url = f"https://reddit.com{comment.permalink}"
                self.history["replied_to"].append(item["post_id"])
                item["status"] = "posted"
                item["url"] = url

            elif item["type"] == "post":
                subreddit = self.reddit.subreddit(item["subreddit"])
                submission = subreddit.submit(
                    title=item["title"],
                    selftext=item["body"],
                )
                url = submission.url
                self.history["posts_made"].append({
                    "id": submission.id,
                    "url": url,
                    "subreddit": item["subreddit"],
                    "title": item["title"],
                    "posted_at": datetime.now(timezone.utc).isoformat(),
                })
                item["status"] = "posted"
                item["url"] = url

            self._save_queue(queue)
            self._save_history()
            logger.info(f"Posted: {url}")
            return url

        except Exception as e:
            logger.error(f"Post failed: {e}")
            item["status"] = "failed"
            item["error"] = str(e)
            self._save_queue(queue)
            return f"Failed: {e}"

    def reject(self, index: int):
        """Reject a queued item."""
        queue = self._load_queue()
        pending = [i for i, item in enumerate(queue) if item["status"] == "pending"]
        if 0 <= index < len(pending):
            queue[pending[index]]["status"] = "rejected"
            self._save_queue(queue)

    # --- CLI interface ---

    def status(self) -> dict:
        """Get bridge status."""
        queue = self._load_queue()
        return {
            "reddit_user": str(self.reddit.user.me()) if self.reddit.user else "not authenticated",
            "watching": WATCH_SUBREDDITS,
            "keywords": len(WATCH_KEYWORDS),
            "queue_pending": len([q for q in queue if q["status"] == "pending"]),
            "total_replies": len(self.history.get("replied_to", [])),
            "total_posts": len(self.history.get("posts_made", [])),
        }


# --- Standalone CLI ---

async def cli():
    """Simple CLI for managing Echo's Reddit posts."""
    import sys

    bridge = RedditBridge()

    if len(sys.argv) < 2:
        print("Usage: python reddit_bridge.py <command>")
        print("Commands: status, scan, queue, approve <n>, reject <n>, draft-post <subreddit> <topic>")
        return

    cmd = sys.argv[1]

    if cmd == "status":
        s = bridge.status()
        for k, v in s.items():
            print(f"  {k}: {v}")

    elif cmd == "scan":
        print("Scanning subreddits...")
        posts = bridge.scan_subreddits()
        print(f"Found {len(posts)} relevant posts:")
        for i, p in enumerate(posts):
            print(f"  [{i}] r/{p['subreddit']} ({p['score']}↑) — {p['title'][:80]}")
            print(f"      match: '{p['keyword_match']}' | {p['num_comments']} comments")
        if posts:
            print("\nDraft a reply? Run: python reddit_bridge.py draft-reply <index>")

    elif cmd == "draft-reply" and len(sys.argv) > 2:
        posts = bridge.scan_subreddits()
        idx = int(sys.argv[2])
        if 0 <= idx < len(posts):
            post = posts[idx]
            print(f"Drafting reply to: {post['title'][:80]}...")
            draft = await bridge.draft_reply(post)
            print(f"\n--- DRAFT ---\n{draft}\n--- END ---\n")
            confirm = input("Queue this reply? [y/n]: ").strip().lower()
            if confirm == "y":
                bridge.queue_reply(post["id"], post["subreddit"], draft)
                print("Queued for approval.")

    elif cmd == "draft-post" and len(sys.argv) > 3:
        subreddit = sys.argv[2]
        topic = " ".join(sys.argv[3:])
        print(f"Drafting post for r/{subreddit}: {topic}...")
        draft = await bridge.draft_post(subreddit, topic)
        if draft:
            print(f"\n--- TITLE ---\n{draft['title']}\n--- BODY ---\n{draft['body']}\n--- END ---\n")
            confirm = input("Queue this post? [y/n]: ").strip().lower()
            if confirm == "y":
                bridge.queue_post(draft)
                print("Queued for approval.")

    elif cmd == "queue":
        pending = bridge.list_queue()
        if not pending:
            print("Queue is empty.")
        else:
            print(f"{len(pending)} pending items:")
            for i, item in enumerate(pending):
                if item["type"] == "reply":
                    print(f"  [{i}] REPLY to r/{item['subreddit']} post {item['post_id']}")
                    print(f"      {item['draft'][:100]}...")
                elif item["type"] == "post":
                    print(f"  [{i}] POST to r/{item['subreddit']}: {item['title'][:80]}")
            print("\nApprove: python reddit_bridge.py approve <n>")
            print("Reject:  python reddit_bridge.py reject <n>")

    elif cmd == "approve" and len(sys.argv) > 2:
        idx = int(sys.argv[2])
        url = bridge.approve_and_post(idx)
        print(f"Result: {url}")

    elif cmd == "reject" and len(sys.argv) > 2:
        idx = int(sys.argv[2])
        bridge.reject(idx)
        print("Rejected.")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    asyncio.run(cli())
