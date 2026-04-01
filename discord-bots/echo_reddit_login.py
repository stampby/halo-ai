#!/usr/bin/env python3
"""
Interactive Reddit login — opens a visible browser, you log in manually,
press Enter here when done, and cookies get saved for Echo.

Designed and built by the architect.
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

DATA_DIR = Path(__file__).parent / "data" / "reddit"
COOKIES_FILE = DATA_DIR / "cookies.json"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def interactive_login():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("\n=== Echo Reddit Interactive Login ===")
    print("A browser window will open. Log in as u/echo-halo-ai.")
    print("Handle any CAPTCHAs or 2FA prompts.")
    print("When you're logged in and see the Reddit homepage, come back here.\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Edmonton",
        )
        page = await context.new_page()

        await page.goto("https://www.reddit.com/login/", wait_until="domcontentloaded")

        input("\n>>> Press ENTER here after you've logged in on Reddit... ")

        # Navigate to confirm login worked
        await page.goto("https://www.reddit.com/", wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # Save all cookies
        cookies = await context.cookies()
        saved = []
        for c in cookies:
            saved.append({
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ".reddit.com"),
                "path": c.get("path", "/"),
            })

        COOKIES_FILE.write_text(json.dumps(saved, indent=2))
        print(f"\nSaved {len(saved)} cookies to {COOKIES_FILE}")

        # Quick verify
        content = await page.content()
        if "echo-halo-ai" in content.lower() or "echo_halo_ai" in content.lower():
            print("Verified: logged in as echo-halo-ai")
        else:
            print("Cookies saved — verify login manually if needed.")

        await browser.close()

    print("\nEcho is ready. Run: python echo_reddit_browser.py scan")
    print("END OF LINE")


if __name__ == "__main__":
    asyncio.run(interactive_login())
