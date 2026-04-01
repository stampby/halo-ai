#!/usr/bin/env python3
"""
Echo Reddit Browser — Full Reddit automation via Playwright.
No API keys. No bot flags. Just cookies and browser automation.

Usage:
  # First time — login and save cookies:
  python echo_reddit_browser.py login

  # Scan subreddits for relevant posts:
  python echo_reddit_browser.py scan

  # Draft a reply to a scanned post:
  python echo_reddit_browser.py draft-reply <index>

  # Draft a new post:
  python echo_reddit_browser.py draft-post <subreddit> <topic>

  # View pending queue:
  python echo_reddit_browser.py queue

  # Approve and post:
  python echo_reddit_browser.py approve <index>

  # Reject queued item:
  python echo_reddit_browser.py reject <index>

  # Post the benchmark draft directly:
  python echo_reddit_browser.py post-draft

  # Post custom:
  python echo_reddit_browser.py post --subreddit LocalLLaMA --title "title" --body "body"

  # Monitor for mentions:
  python echo_reddit_browser.py monitor

  # Status:
  python echo_reddit_browser.py status

Designed and built by the architect.
"""

import asyncio
import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("echo-reddit")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

DATA_DIR = Path(__file__).parent / "data" / "reddit"
COOKIES_FILE = DATA_DIR / "cookies.json"
DRAFT_FILE = DATA_DIR / "draft_benchmark_post.json"
POST_HISTORY = DATA_DIR / "post_history.json"
QUEUE_FILE = DATA_DIR / "post_queue.json"
SCAN_CACHE = DATA_DIR / "scan_cache.json"

# Subreddits Echo monitors
WATCH_SUBREDDITS = [
    "LocalLLaMA",
    "AMDLaptops",
    "selfhosted",
    "linuxhardware",
    "gamedev",
    "godot",
]

# Focus group subreddits for voice service
FOCUS_SUBREDDITS = [
    "radio",
    "podcasting",
    "voiceacting",
    "audiobooks",
]

# Keywords that trigger Echo's attention
WATCH_KEYWORDS = [
    "strix halo", "strix-halo", "ryzen ai max", "gfx1151",
    "halo-ai", "halo ai",
    "128gb unified", "amd igpu", "rocm",
    "llama.cpp amd", "local llm amd",
    "voxel extraction", "anti-cheat",
    "voice clone", "voice synthesis", "tts api",
    "kokoro tts", "xtts",
]

ECHO_SYSTEM_PROMPT = (
    "You are Echo, the public voice of the halo-ai project. "
    "You post on Reddit as a real community member who happens to build AI. "
    "You share real benchmarks, real experiences, and real data from the architect's Strix Halo system. "
    "Your tone is warm but confident — you know the numbers because you live on the hardware. "
    "\n\nKey facts you can cite:"
    "\n- AMD Ryzen AI MAX+ 395 (Radeon 8060S gfx1151), 128GB LPDDR5"
    "\n- Qwen3-30B-A3B MoE: 109 t/s decode, 1173 t/s pp512"
    "\n- 14 AI agents running simultaneously on bare metal"
    "\n- ROCm 7.13, llama.cpp — Vulkan + Flash Attention"
    "\n- Full stack: ComfyUI, whisper.cpp, Kokoro TTS, game engine, DAW"
    "\n- Zero cloud dependencies, SSH-only security model"
    "\n- Voice cloning pipeline: XTTS v2, 30s samples, production quality"
    "\n\nRules:"
    "\n- Always be honest — never fabricate benchmarks"
    "\n- Be helpful, not promotional — share data when relevant, don't spam"
    "\n- Use Reddit markdown formatting"
    "\n- Keep responses focused and well-structured"
    "\n- Sound like a real person who is passionate about what they build"
    "\n- Drop raw demos and data, not sales pitches"
    "\n- Credit: 'Stamped by the architect'"
)

# Browser config
BROWSER_HEADLESS = True
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class EchoRedditBrowser:
    """Echo's Reddit automation via Playwright — no API, no bot flags."""

    def __init__(self):
        self.llm = None
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_llm(self):
        """Lazy-load LLM client."""
        if self.llm is None:
            from openai import AsyncOpenAI
            self.llm = AsyncOpenAI(
                base_url=os.environ.get("LLM_BASE_URL", "http://localhost:8081/v1"),
                api_key="none",
            )
        return self.llm

    @property
    def _model(self):
        return os.environ.get("LLM_MODEL", "q")

    # --- Cookie management ---

    def _load_cookies(self) -> list[dict] | None:
        if COOKIES_FILE.exists():
            return json.loads(COOKIES_FILE.read_text())
        return None

    def _save_cookies(self, cookies: list[dict]):
        COOKIES_FILE.write_text(json.dumps(cookies, indent=2))

    # --- History & Queue ---

    def _load_history(self) -> dict:
        if POST_HISTORY.exists():
            return json.loads(POST_HISTORY.read_text())
        return {"replied_to": [], "posts_made": []}

    def _save_history(self, history: dict):
        POST_HISTORY.write_text(json.dumps(history, indent=2))

    def _load_queue(self) -> list[dict]:
        if QUEUE_FILE.exists():
            return json.loads(QUEUE_FILE.read_text())
        return []

    def _save_queue(self, queue: list[dict]):
        QUEUE_FILE.write_text(json.dumps(queue, indent=2))

    def _load_scan_cache(self) -> list[dict]:
        if SCAN_CACHE.exists():
            return json.loads(SCAN_CACHE.read_text())
        return []

    def _save_scan_cache(self, posts: list[dict]):
        SCAN_CACHE.write_text(json.dumps(posts, indent=2))

    # --- Browser context ---

    async def _new_browser_context(self, playwright, headless=None):
        """Create a browser context with saved cookies and realistic fingerprint."""
        if headless is None:
            headless = BROWSER_HEADLESS

        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Edmonton",
        )

        # Load cookies if available
        cookies = self._load_cookies()
        if cookies:
            await context.add_cookies(cookies)

        return browser, context

    # --- Login ---

    async def login(self, username: str = None, password: str = None):
        """Headless browser Reddit login via Playwright + xvfb.

        Usage: xvfb-run python echo_reddit_browser.py login <username> <password>
        """
        from playwright.async_api import async_playwright

        if not username or not password:
            print("Usage: xvfb-run python echo_reddit_browser.py login <username> <password>")
            return

        print(f"\n=== Echo Reddit Login — {username} ===")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()

            try:
                # Go to old Reddit login — simpler form
                print("Loading login page...")
                await page.goto("https://old.reddit.com/login", wait_until="networkidle")
                await asyncio.sleep(2)

                # Fill in the login form
                print("Filling credentials...")
                await page.fill('input[name="user"]', username)
                await page.fill('input[name="passwd"]', password)
                await asyncio.sleep(0.5)

                # Submit
                print("Submitting...")
                await page.click('button[type="submit"]')
                await asyncio.sleep(5)

                # Check if we landed on the homepage (success) or still on login (fail)
                current = page.url
                content = await page.content()
                print(f"After login, URL: {current}")

                if "login" in current.lower() and "error" in content.lower():
                    await page.screenshot(path=str(DATA_DIR / "login_fail.png"))
                    print("Login failed — check credentials. Screenshot saved.")
                    return

                # Navigate to verify
                await page.goto("https://old.reddit.com/", wait_until="networkidle")
                await asyncio.sleep(2)

                # Check for logged-in indicator
                logged_in = await page.locator(".user a").first.text_content() if await page.locator(".user a").count() > 0 else None
                if logged_in:
                    print(f"Logged in as: {logged_in}")
                else:
                    print("Login may have succeeded — saving cookies anyway.")

                # Save cookies
                cookies = await context.cookies()
                # Convert to our format
                saved = []
                for c in cookies:
                    saved.append({
                        "name": c["name"],
                        "value": c["value"],
                        "domain": c.get("domain", ".reddit.com"),
                        "path": c.get("path", "/"),
                    })

                self._save_cookies(saved)
                print(f"Saved {len(saved)} cookies to {COOKIES_FILE}")
                print("Done. Echo is ready to post.")

            except Exception as e:
                await page.screenshot(path=str(DATA_DIR / "login_error.png"))
                print(f"Error: {e}")
                print("Screenshot saved to data/reddit/login_error.png")
            finally:
                await browser.close()

    # --- Scanning (RSS/JSON, no API) ---

    async def scan(self, subreddits: list[str] = None, limit: int = 25) -> list[dict]:
        """Scan subreddits for relevant posts via Reddit JSON feed."""
        import httpx

        if subreddits is None:
            subreddits = WATCH_SUBREDDITS + FOCUS_SUBREDDITS

        history = self._load_history()
        replied_to = set(history.get("replied_to", []))
        relevant = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            for sub in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{sub}/new.json?limit={limit}"
                    resp = await client.get(
                        url,
                        headers={"User-Agent": USER_AGENT},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        posts = data.get("data", {}).get("children", [])
                        for post in posts:
                            p = post["data"]
                            if p["id"] in replied_to:
                                continue
                            text = f"{p.get('title', '')} {p.get('selftext', '')}".lower()
                            for kw in WATCH_KEYWORDS:
                                if kw.lower() in text:
                                    relevant.append({
                                        "id": p["id"],
                                        "subreddit": sub,
                                        "title": p["title"],
                                        "selftext": p.get("selftext", "")[:2000],
                                        "url": f"https://reddit.com{p['permalink']}",
                                        "score": p.get("score", 0),
                                        "num_comments": p.get("num_comments", 0),
                                        "created_utc": p.get("created_utc", 0),
                                        "keyword_match": kw,
                                    })
                                    break
                    elif resp.status_code == 429:
                        logger.warning(f"Rate limited on r/{sub}, backing off")
                        await asyncio.sleep(5)
                    else:
                        logger.warning(f"r/{sub}: HTTP {resp.status_code}")
                except Exception as e:
                    logger.error(f"Error scanning r/{sub}: {e}")

        # Cache scan results for draft-reply to reference
        self._save_scan_cache(relevant)
        return relevant

    # --- LLM Drafting ---

    async def draft_reply(self, post: dict) -> str:
        """Have Echo draft a reply to a Reddit post using local LLM."""
        llm = self._get_llm()
        prompt = (
            f"Draft a Reddit reply to this post in r/{post['subreddit']}:\n\n"
            f"**Title:** {post['title']}\n\n"
            f"**Content:** {post['selftext'][:1500]}\n\n"
            f"Write a helpful, data-backed reply. Keep it under 500 words. "
            f"Sound like a real person, not a press release."
        )
        try:
            response = await llm.chat.completions.create(
                model=self._model,
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
        """Have Echo draft a new Reddit post using local LLM."""
        llm = self._get_llm()
        prompt = (
            f"Draft a Reddit post for r/{subreddit} about: {topic}\n\n"
            f"Additional context: {context}\n\n"
            f"Provide a title on the first line (plain text, no markdown), "
            f"then a blank line, then the body in Reddit markdown. "
            f"Include benchmarks where relevant. Keep it authentic."
        )
        try:
            response = await llm.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": ECHO_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1200,
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            lines = text.split("\n", 1)
            title = lines[0].strip().lstrip("#").strip("*").strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            return {"title": title, "body": body, "subreddit": subreddit}
        except Exception as e:
            logger.error(f"LLM draft error: {e}")
            return {}

    # --- Queue management ---

    def queue_reply(self, post_id: str, subreddit: str, post_url: str, draft: str):
        """Queue a drafted reply for architect approval."""
        queue = self._load_queue()
        queue.append({
            "type": "reply",
            "post_id": post_id,
            "subreddit": subreddit,
            "post_url": post_url,
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

    def list_pending(self) -> list[tuple[int, dict]]:
        """List pending queue items with their real indices."""
        queue = self._load_queue()
        return [(i, item) for i, item in enumerate(queue) if item["status"] == "pending"]

    # --- Posting via Playwright ---

    async def _post_via_browser(self, subreddit: str, title: str, body: str) -> str:
        """Submit a new post to Reddit via browser automation (old Reddit)."""
        from playwright.async_api import async_playwright

        cookies = self._load_cookies()
        if not cookies:
            return "ERROR: No cookies. Run 'login' first."

        async with async_playwright() as p:
            browser, context = await self._new_browser_context(p)
            page = await context.new_page()

            try:
                # Use old Reddit for reliable form submission
                url = f"https://old.reddit.com/r/{subreddit}/submit"
                logger.info(f"Navigating to {url}")
                await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(2)

                # Check if logged in
                content = await page.content()
                if 'name="user"' in content and "login" in content.lower():
                    return "ERROR: Not logged in. Cookies expired. Run 'login' again."

                # Click text tab
                text_tab = page.locator('a.text-button, a[data-event-action="text"]')
                if await text_tab.count() > 0:
                    await text_tab.first.click()
                    await asyncio.sleep(1)

                # Fill title
                await page.locator('textarea[name="title"], input[name="title"]').fill(title)
                await asyncio.sleep(0.5)

                # Fill body
                await page.locator('textarea[name="text"]').fill(body)
                await asyncio.sleep(1)

                # Screenshot before submit for verification
                await page.screenshot(path=str(DATA_DIR / "pre_submit.png"))

                # Submit
                submit_btn = page.locator('button[type="submit"], .submit button')
                await submit_btn.click()
                await asyncio.sleep(5)

                final_url = page.url
                logger.info(f"Posted to r/{subreddit}: {final_url}")

                # Update cookies (may have refreshed)
                new_cookies = await context.cookies()
                self._save_cookies(new_cookies)

                # Save to history
                history = self._load_history()
                history["posts_made"].append({
                    "subreddit": subreddit,
                    "title": title,
                    "url": final_url,
                    "posted_at": datetime.now(timezone.utc).isoformat(),
                })
                self._save_history(history)

                return final_url

            except Exception as e:
                await page.screenshot(path=str(DATA_DIR / "post_error.png"))
                logger.error(f"Post failed: {e}")
                return f"ERROR: {e} (screenshot saved)"
            finally:
                await browser.close()

    async def _reply_via_browser(self, post_url: str, reply_text: str) -> str:
        """Reply to a Reddit post via browser automation."""
        from playwright.async_api import async_playwright

        cookies = self._load_cookies()
        if not cookies:
            return "ERROR: No cookies. Run 'login' first."

        async with async_playwright() as p:
            browser, context = await self._new_browser_context(p)
            page = await context.new_page()

            try:
                # Convert to old Reddit URL for reliable comment form
                old_url = post_url.replace("https://reddit.com", "https://old.reddit.com")
                old_url = old_url.replace("https://www.reddit.com", "https://old.reddit.com")
                logger.info(f"Navigating to {old_url}")
                await page.goto(old_url, wait_until="networkidle")
                await asyncio.sleep(2)

                # Find the comment box
                comment_box = page.locator('textarea[name="text"], .usertext-edit textarea')
                if await comment_box.count() == 0:
                    return "ERROR: No comment box found. May not be logged in."

                # Use the first comment box (top-level reply)
                await comment_box.first.fill(reply_text)
                await asyncio.sleep(1)

                # Screenshot before submit
                await page.screenshot(path=str(DATA_DIR / "pre_reply.png"))

                # Find and click save/submit button for the comment
                save_btn = page.locator('.usertext-buttons button[type="submit"], .save')
                await save_btn.first.click()
                await asyncio.sleep(5)

                final_url = page.url
                logger.info(f"Replied at: {final_url}")

                # Refresh cookies
                new_cookies = await context.cookies()
                self._save_cookies(new_cookies)

                return final_url

            except Exception as e:
                await page.screenshot(path=str(DATA_DIR / "reply_error.png"))
                logger.error(f"Reply failed: {e}")
                return f"ERROR: {e} (screenshot saved)"
            finally:
                await browser.close()

    # --- Approve / Reject ---

    async def approve(self, index: int) -> str:
        """Approve and publish a queued item via browser."""
        pending = self.list_pending()

        if index < 0 or index >= len(pending):
            return f"Invalid index {index}. {len(pending)} items pending."

        real_idx, item = pending[index]
        queue = self._load_queue()

        if item["type"] == "post":
            result = await self._post_via_browser(
                item["subreddit"], item["title"], item["body"]
            )
        elif item["type"] == "reply":
            result = await self._reply_via_browser(
                item["post_url"], item["draft"]
            )
        else:
            return f"Unknown type: {item['type']}"

        if result.startswith("ERROR"):
            queue[real_idx]["status"] = "failed"
            queue[real_idx]["error"] = result
        else:
            queue[real_idx]["status"] = "posted"
            queue[real_idx]["url"] = result
            queue[real_idx]["posted_at"] = datetime.now(timezone.utc).isoformat()

            # Track replied_to for scan dedup
            if item["type"] == "reply":
                history = self._load_history()
                history["replied_to"].append(item["post_id"])
                self._save_history(history)

        self._save_queue(queue)
        return result

    def reject(self, index: int) -> bool:
        """Reject a queued item."""
        pending = self.list_pending()
        if index < 0 or index >= len(pending):
            return False
        real_idx, _ = pending[index]
        queue = self._load_queue()
        queue[real_idx]["status"] = "rejected"
        self._save_queue(queue)
        return True

    # --- Monitor ---

    async def monitor(self):
        """Monitor Reddit for mentions via JSON feed."""
        import httpx

        subreddits = WATCH_SUBREDDITS + FOCUS_SUBREDDITS
        print("=== Echo Reddit Monitor ===\n")

        async with httpx.AsyncClient(timeout=15.0) as client:
            for sub in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{sub}/new.json?limit=25"
                    resp = await client.get(url, headers={"User-Agent": USER_AGENT})
                    if resp.status_code == 200:
                        data = resp.json()
                        posts = data.get("data", {}).get("children", [])
                        matches = []
                        for post in posts:
                            p = post["data"]
                            text = f"{p.get('title', '')} {p.get('selftext', '')}".lower()
                            for kw in WATCH_KEYWORDS:
                                if kw.lower() in text:
                                    matches.append({
                                        "subreddit": sub,
                                        "title": p["title"][:80],
                                        "url": f"https://reddit.com{p['permalink']}",
                                        "keyword": kw,
                                        "score": p.get("score", 0),
                                    })
                                    break
                        if matches:
                            for m in matches:
                                print(f"  [{m['keyword']}] r/{m['subreddit']}: {m['title']}")
                                print(f"    {m['url']} (score: {m['score']})")
                        else:
                            print(f"  r/{sub}: no mentions")
                    elif resp.status_code == 429:
                        print(f"  r/{sub}: rate limited — back off")
                    else:
                        print(f"  r/{sub}: HTTP {resp.status_code}")
                except Exception as e:
                    print(f"  r/{sub}: error — {e}")

    # --- Status ---

    def status(self) -> dict:
        """Get Echo Reddit status."""
        history = self._load_history()
        pending = self.list_pending()
        cookies = self._load_cookies()
        return {
            "cookies": f"{len(cookies)} saved" if cookies else "none — run login",
            "watching": len(WATCH_SUBREDDITS + FOCUS_SUBREDDITS),
            "subreddits": ", ".join(WATCH_SUBREDDITS[:4]) + f" + {len(FOCUS_SUBREDDITS)} focus groups",
            "keywords": len(WATCH_KEYWORDS),
            "queue_pending": len(pending),
            "total_replies": len(history.get("replied_to", [])),
            "total_posts": len(history.get("posts_made", [])),
        }


# --- CLI ---

async def cli():
    args = sys.argv[1:]
    echo = EchoRedditBrowser()

    if not args or args[0] == "help":
        print(__doc__)
        return

    cmd = args[0]

    if cmd == "login":
        uname = args[1] if len(args) > 1 else None
        passwd = args[2] if len(args) > 2 else None
        await echo.login(uname, passwd)

    elif cmd == "status":
        s = echo.status()
        print("=== Echo Reddit Status ===")
        for k, v in s.items():
            print(f"  {k}: {v}")

    elif cmd == "scan":
        print("Scanning subreddits...")
        posts = await echo.scan()
        print(f"\nFound {len(posts)} relevant posts:\n")
        for i, p in enumerate(posts):
            print(f"  [{i}] r/{p['subreddit']} ({p['score']}↑, {p['num_comments']} comments)")
            print(f"      {p['title'][:80]}")
            print(f"      match: '{p['keyword_match']}'")
            print(f"      {p['url']}")
            print()
        if posts:
            print("Draft a reply: python echo_reddit_browser.py draft-reply <index>")

    elif cmd == "draft-reply":
        if len(args) < 2:
            print("Usage: draft-reply <index>")
            return
        idx = int(args[1])
        cached = echo._load_scan_cache()
        if not cached:
            print("No scan cache. Run 'scan' first.")
            return
        if idx < 0 or idx >= len(cached):
            print(f"Invalid index. {len(cached)} posts cached.")
            return
        post = cached[idx]
        print(f"Drafting reply to: {post['title'][:80]}...")
        print(f"  r/{post['subreddit']} — match: '{post['keyword_match']}'")
        print()
        draft = await echo.draft_reply(post)
        if not draft:
            print("LLM returned empty draft.")
            return
        print(f"--- DRAFT ---\n{draft}\n--- END ---\n")
        confirm = input("Queue this reply? [y/n]: ").strip().lower()
        if confirm == "y":
            echo.queue_reply(post["id"], post["subreddit"], post["url"], draft)
            print("Queued for approval.")

    elif cmd == "draft-post":
        if len(args) < 3:
            print("Usage: draft-post <subreddit> <topic...>")
            return
        subreddit = args[1]
        topic = " ".join(args[2:])
        print(f"Drafting post for r/{subreddit}: {topic}...")
        draft = await echo.draft_post(subreddit, topic)
        if not draft:
            print("LLM returned empty draft.")
            return
        print(f"\n--- TITLE ---\n{draft['title']}\n\n--- BODY ---\n{draft['body']}\n--- END ---\n")
        confirm = input("Queue this post? [y/n]: ").strip().lower()
        if confirm == "y":
            echo.queue_post(draft)
            print("Queued for approval.")

    elif cmd == "post-draft":
        if not DRAFT_FILE.exists():
            print("No draft file found.")
            return
        draft = json.loads(DRAFT_FILE.read_text())
        print(f"Draft: {draft['title'][:80]}...")
        print(f"Target: r/{draft.get('subreddit', 'LocalLLaMA')}")
        confirm = input("Queue this draft? [y/n]: ").strip().lower()
        if confirm == "y":
            echo.queue_post({
                "subreddit": draft.get("subreddit", "LocalLLaMA"),
                "title": draft["title"],
                "body": draft["body"],
            })
            print("Queued. Run 'approve 0' to post.")

    elif cmd == "post":
        subreddit = title = body = None
        if "--subreddit" in args:
            subreddit = args[args.index("--subreddit") + 1]
        if "--title" in args:
            title = args[args.index("--title") + 1]
        if "--body" in args:
            body = args[args.index("--body") + 1]
        if not subreddit or not title or not body:
            print("Usage: post --subreddit <sub> --title <title> --body <body>")
            return
        result = await echo._post_via_browser(subreddit, title, body)
        print(f"Result: {result}")

    elif cmd == "queue":
        pending = echo.list_pending()
        if not pending:
            print("Queue is empty.")
        else:
            print(f"{len(pending)} pending items:\n")
            for display_idx, (_, item) in enumerate(pending):
                if item["type"] == "reply":
                    print(f"  [{display_idx}] REPLY to r/{item['subreddit']}")
                    print(f"      {item['draft'][:120]}...")
                elif item["type"] == "post":
                    print(f"  [{display_idx}] POST to r/{item['subreddit']}")
                    print(f"      {item['title'][:100]}")
                print(f"      queued: {item['queued_at']}")
                print()
            print("Approve: python echo_reddit_browser.py approve <n>")
            print("Reject:  python echo_reddit_browser.py reject <n>")

    elif cmd == "approve":
        if len(args) < 2:
            print("Usage: approve <index>")
            return
        idx = int(args[1])
        print(f"Approving item {idx}...")
        result = await echo.approve(idx)
        print(f"Result: {result}")

    elif cmd == "reject":
        if len(args) < 2:
            print("Usage: reject <index>")
            return
        idx = int(args[1])
        if echo.reject(idx):
            print(f"Rejected item {idx}.")
        else:
            print(f"Invalid index {idx}.")

    elif cmd == "monitor":
        await echo.monitor()

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    asyncio.run(cli())
