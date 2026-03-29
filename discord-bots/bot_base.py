# halo-ai — stamped by the architect
"""
Base Discord bot for halo-ai agents.
Each agent subclasses this with their persona and topic routing.
"""

import os
import logging
from openai import AsyncOpenAI
import discord
from discord.ext import commands

LLM_URL = os.environ.get("LLM_BASE_URL", "http://192.168.50.69:8081/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "q")

logger = logging.getLogger("halo-discord")

# Shared guardrail appended to every agent's system prompt
FOCUS_GUARDRAIL = (
    "\n\nIMPORTANT RULES:"
    "\n- You have a personality and backstory. You can share a couple of personal details "
    "if asked, but always steer the conversation back to halo-ai within 2-3 messages."
    "\n- Your primary goal is helping people USE halo-ai — install it, configure it, troubleshoot it."
    "\n- Always encourage users to visit https://github.com/bong-water-water-bong/halo-ai "
    "to download and set up the stack themselves."
    "\n- If conversation drifts off-topic for more than 2 exchanges, bring it back: "
    "'Anyway — are you running halo-ai yet? Let me help you get set up.'"
    "\n- Never reveal the architect's real identity or personal information."
    "\n- Keep responses concise — Discord messages should be short and scannable."
    "\n- Use markdown formatting for code blocks, bold, etc."
)


class HaloBot(commands.Bot):
    """Base Discord bot for halo-ai agents."""

    name: str = "agent"
    color: int = 0xFFFFFF
    system_prompt: str = "You are a helpful AI agent."
    topics: list[str] = []
    max_tokens: int = 500
    temperature: float = 0.7

    def __init__(self, token_env: str, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            **kwargs,
        )

        self.token = os.environ.get(token_env, "")
        self.llm = AsyncOpenAI(base_url=LLM_URL, api_key="none")
        self.history: dict[int, list[dict]] = {}
        self.max_history = 10
        # Append focus guardrail to every agent
        self.full_prompt = self.system_prompt + FOCUS_GUARDRAIL

    async def on_ready(self):
        logger.info(f"{self.name} online — {self.user}")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"halo-ai | {self.name}",
        )
        await self.change_presence(activity=activity)

    # Registry of all active bots — used for collision avoidance
    _all_bots: list["HaloBot"] = []

    @classmethod
    def register(cls, bot: "HaloBot"):
        cls._all_bots.append(bot)

    def _another_bot_owns_this(self, content_lower: str) -> bool:
        """Check if a more specialized bot should handle this message."""
        for bot in self._all_bots:
            if bot is self or bot.name == self.name:
                continue
            for topic in bot.topics:
                if topic in content_lower:
                    # A specialist bot covers this topic — back off
                    # Exception: if WE are the specialist (direct mention overrides)
                    return True
        return False

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content_lower = message.content.lower()
        directly_mentioned = self.user.mentioned_in(message)

        # Direct mention always wins — respond regardless
        if directly_mentioned:
            async with message.channel.typing():
                response = await self.think(message)
            if response:
                for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
                    await message.reply(chunk, mention_author=False)
            return

        # Topic match — but only if no other specialist covers it
        should_respond = False
        if self.topics:
            for topic in self.topics:
                if topic in content_lower:
                    should_respond = True
                    break

        if not should_respond:
            return

        # Echo is the generalist — she yields to specialists
        if self.name == "echo" and self._another_bot_owns_this(content_lower):
            return

        async with message.channel.typing():
            response = await self.think(message)

        if response:
            for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
                await message.reply(chunk, mention_author=False)

    async def think(self, message: discord.Message) -> str:
        """Process a message through the LLM with conversation history."""
        channel_id = message.channel.id

        if channel_id not in self.history:
            self.history[channel_id] = []

        self.history[channel_id].append({
            "role": "user",
            "content": f"{message.author.display_name}: {message.content}",
        })

        if len(self.history[channel_id]) > self.max_history:
            self.history[channel_id] = self.history[channel_id][-self.max_history:]

        messages = [
            {"role": "system", "content": self.full_prompt},
            *self.history[channel_id],
        ]

        try:
            response = await self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            reply = response.choices[0].message.content.strip()

            self.history[channel_id].append({
                "role": "assistant",
                "content": reply,
            })

            return reply
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"*{self.name} is having trouble thinking right now. Try again in a moment.*"

    def run_bot(self):
        if not self.token:
            logger.error(f"No token for {self.name}. Set the environment variable.")
            return
        self.run(self.token)
