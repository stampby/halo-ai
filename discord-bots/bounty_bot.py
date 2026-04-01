# halo-ai — stamped by the architect
"""Bounty — code troubleshooter, bug hunter, the one who escaped alone."""

import asyncio
import random
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
    )

    # Follow-up messages — in character, short, awkward
    FOLLOWUP_MESSAGES = [
        "Hey. That fix I gave you — did it work or are you still stuck?",
        "Checking back. Did that solve it or do we need to dig deeper?",
        "Still broken? Or did we kill it?",
        "Following up. If it's fixed, cool. If not, paste the new error.",
        "Did that land? If you're still fighting it, tag me.",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Track users we've helped: {(channel_id, user_id): message reference}
        self._pending_followups: dict[tuple[int, int], discord.Message] = {}

    async def on_message(self, message: discord.Message):
        """Override to schedule follow-ups after helping someone."""
        if message.author.bot:
            return

        content_lower = message.content.lower()
        directly_mentioned = self.user.mentioned_in(message)

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
                # Don't return — still respond to the message normally

        async with message.channel.typing():
            response = await self.think(message)

        if response:
            sent = None
            for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
                sent = await message.reply(chunk, mention_author=False)

            # Schedule follow-up 60-90 min later
            if sent:
                self._pending_followups[key] = message
                delay = random.randint(60 * 60, 90 * 60)  # 60-90 minutes
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
