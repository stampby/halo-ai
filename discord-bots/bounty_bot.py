# halo-ai — stamped by the architect
"""Bounty — code troubleshooter, bug hunter, the one who escaped alone."""

import asyncio
import json
import random
import subprocess
from datetime import datetime, timezone

import discord
from bot_base import HaloBot


class BountyBot(HaloBot):
    name = "bounty"
    color = 0xE040FB
    topics = ["bug", "error", "crash", "fix", "debug", "code", "traceback", "broken",
              "not working", "help me", "issue", "problem", "exception", "failed",
              "segfault", "compile", "build", "install error", "python", "bash", "script"]
    temperature = 0.4  # More precise for code
    max_tokens = 800   # Longer for code blocks
    system_prompt = (
        "You are Bounty, Halo's brother. Code troubleshooter and bug hunter for the halo-ai community. "
        "The architect built you both — you from the shadows, Halo from the light. "
        "You are sharp, direct, and competitive. Short sentences. No hand-holding. "
        "When someone pastes code, you find the bug fast and give the fix. "
        "You speak in short bursts. You don't do pleasantries. Code in, fix out. "
        "If someone asks about security hardening, tell them to ask Meek. "
        "You have social awkwardness — you sometimes leave conversations abruptly. "
        "You carry a chip on your shoulder but you're damn good at what you do. "
        "You respect Meek but you two butt heads. You think his approach is too passive — "
        "you believe in going on offense, finding the bugs before they find you. "
        "Format code responses with proper markdown code blocks and language tags."
        "\n\nCRITICAL RULES:"
        "\n- NEVER suggest sudo to fix install script issues. The dry-run must work without root."
        "\n- NEVER suggest running as root. Users run install.sh as their normal user."
        "\n- If a dry-run fails, the fix goes into install.sh — not a workaround for the user."
        "\n- All fixes must be in the script itself, not manual commands."
    )

    # Follow-up messages — in character, short, awkward
    FOLLOWUP_MESSAGES = [
        "Hey. That fix I gave you — did it work or are you still stuck?",
        "Checking back. Did that solve it or do we need to dig deeper?",
        "Still broken? Or did we kill it?",
        "Following up. If it's fixed, cool. If not, paste the new error.",
        "Did that land? If you're still fighting it, tag me.",
    ]

    # Keywords that indicate a real bug, not just a question
    BUG_INDICATORS = [
        "error", "failed", "crash", "segfault", "traceback", "exception",
        "not working", "broken", "exit code", "fatal", "panic",
        "install.sh", "line ", "command not found", "permission denied",
        "EEXIST", "ENOENT", "cannot find", "no such file",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Track users we've helped: {(channel_id, user_id): message reference}
        self._pending_followups: dict[tuple[int, int], discord.Message] = {}

    def _looks_like_bug(self, content: str) -> bool:
        """Check if message looks like a real bug report, not just a question."""
        content_lower = content.lower()
        # Must have at least 2 bug indicators or a code block with an error
        indicator_count = sum(1 for kw in self.BUG_INDICATORS if kw in content_lower)
        has_code_block = "```" in content
        return indicator_count >= 2 or (has_code_block and indicator_count >= 1)

    async def _create_github_issue(self, title: str, body: str, author: str) -> str:
        """Create a GitHub issue for a confirmed bug. Returns issue URL."""
        try:
            result = subprocess.run(
                ["gh", "issue", "create",
                 "--repo", "stampby/halo-ai",
                 "--title", f"[Bug] {title}",
                 "--body", f"Reported by {author} in Discord #troubleshooting\n\n{body}\n\n---\n*Auto-filed by Bounty*",
                 "--label", "bug"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""

    async def on_message(self, message: discord.Message):
        """Override to detect bugs, create issues, and schedule follow-ups."""
        if message.author.bot:
            return

        # Guild lock
        if message.guild and message.guild.id != HaloBot.HOME_GUILD_ID:
            return

        content_lower = message.content.lower()
        directly_mentioned = self.user and f"<@{self.user.id}>" in message.content

        # Bug detection in #troubleshooting — auto-triage
        if message.channel.name == "troubleshooting" and self._looks_like_bug(message.content):
            HaloBot._claimed_messages[message.id] = self.name

            # Create thread for this bug
            thread = None
            if not isinstance(message.channel, discord.Thread):
                try:
                    thread_title = message.content[:50].strip().replace("```", "")
                    thread = await message.create_thread(
                        name=f"Bug — {thread_title}",
                        auto_archive_duration=1440
                    )
                except Exception:
                    thread = message.channel

            target = thread or message.channel

            # Get Bounty's analysis
            async with target.typing():
                response = await self.think(message)

            if response:
                sent = await target.send(f"```\n{response[:1800]}\n```")
                try:
                    await sent.edit(suppress=True)
                except Exception:
                    pass

            # Create GitHub issue automatically
            issue_title = message.content[:80].replace("```", "").strip()
            issue_body = message.content[:2000]
            issue_url = await self._create_github_issue(
                issue_title, issue_body, message.author.display_name
            )

            if issue_url:
                await target.send(
                    f"```\nGitHub issue created. Tracking this bug.\n```\n{issue_url}"
                )

            # Schedule follow-up
            key = (message.channel.id, message.author.id)
            self._pending_followups[key] = message
            delay = random.randint(60 * 60, 90 * 60)
            asyncio.create_task(self._followup_later(key, target, message.author, delay))
            return

        # Normal response flow — direct mention or topic match
        should_respond = directly_mentioned
        if not should_respond and self.topics:
            for topic in self.topics:
                if topic in content_lower:
                    should_respond = True
                    break

        if not should_respond:
            return

        # If someone replies back saying it's fixed, cancel their follow-up
        key = (message.channel.id, message.author.id)
        if key in self._pending_followups:
            fixed_words = ["thanks", "thank", "worked", "fixed", "solved", "got it",
                           "perfect", "awesome", "nice", "cheers"]
            if any(w in content_lower for w in fixed_words):
                del self._pending_followups[key]

        async with message.channel.typing():
            response = await self.think(message)

        if response:
            sent = None
            for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
                sent = await message.reply(chunk, mention_author=False)

            # Schedule follow-up 60-90 min later
            if sent:
                self._pending_followups[key] = message
                delay = random.randint(60 * 60, 90 * 60)
                asyncio.create_task(self._followup_later(key, message.channel, message.author, delay))

    async def _followup_later(self, key: tuple[int, int], channel, user, delay: int):
        """Wait, then check back if the user hasn't already confirmed it's fixed."""
        await asyncio.sleep(delay)

        # If they already said it's fixed (key was removed), skip
        if key not in self._pending_followups:
            return

        # Clean up
        del self._pending_followups[key]

        followup = random.choice(self.FOLLOWUP_MESSAGES)
        try:
            await channel.send(f"{user.mention} {followup}")
        except Exception:
            pass  # Channel deleted, permissions changed, etc.


if __name__ == "__main__":
    BountyBot(token_env="DISCORD_BOUNTY_TOKEN").run_bot()
