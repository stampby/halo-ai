# halo-ai — stamped by the architect
"""
Base Discord bot for halo-ai agents.
Each agent subclasses this with their persona and topic routing.
"""

import os
import time
import logging
from openai import AsyncOpenAI
import discord
from discord.ext import commands

LLM_URL = os.environ.get("LLM_BASE_URL", "http://localhost:8081/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "q")

logger = logging.getLogger("halo-discord")

# Documentation base URL
DOCS_BASE = "https://github.com/stampby/halo-ai/blob/main"

# Agent-to-documentation mapping — each agent knows their domain docs
AGENT_DOCS = {
    "echo": [
        ("README", f"{DOCS_BASE}/README.md"),
        ("Agents & Family", f"{DOCS_BASE}/docs/AGENTS.md"),
        ("Benchmarks", f"{DOCS_BASE}/BENCHMARKS.md"),
        ("Benchmarks Site", "https://stampby.github.io/benchmarks/"),
        ("Blueprints", f"{DOCS_BASE}/docs/BLUEPRINTS.md"),
    ],
    "bounty": [
        ("Troubleshooting", f"{DOCS_BASE}/docs/TROUBLESHOOTING.md"),
        ("Services", f"{DOCS_BASE}/docs/SERVICES.md"),
        ("Architecture", f"{DOCS_BASE}/docs/ARCHITECTURE.md"),
        ("Stack Protection", f"{DOCS_BASE}/docs/STACK-PROTECTION.md"),
    ],
    "meek": [
        ("Security", f"{DOCS_BASE}/docs/SECURITY.md"),
        ("VPN Access", f"{DOCS_BASE}/docs/VPN.md"),
        ("Architecture", f"{DOCS_BASE}/docs/ARCHITECTURE.md"),
        ("Services", f"{DOCS_BASE}/docs/SERVICES.md"),
    ],
    "amp": [
        ("Services", f"{DOCS_BASE}/docs/SERVICES.md"),
        ("Architecture", f"{DOCS_BASE}/docs/ARCHITECTURE.md"),
        ("Blueprints", f"{DOCS_BASE}/docs/BLUEPRINTS.md"),
    ],
}

# All docs available to any agent as fallback
ALL_DOCS = [
    ("README", f"{DOCS_BASE}/README.md"),
    ("Architecture", f"{DOCS_BASE}/docs/ARCHITECTURE.md"),
    ("Services", f"{DOCS_BASE}/docs/SERVICES.md"),
    ("Security", f"{DOCS_BASE}/docs/SECURITY.md"),
    ("Stack Protection", f"{DOCS_BASE}/docs/STACK-PROTECTION.md"),
    ("Troubleshooting", f"{DOCS_BASE}/docs/TROUBLESHOOTING.md"),
    ("Benchmarks", f"{DOCS_BASE}/BENCHMARKS.md"),
    ("Benchmarks Site", "https://stampby.github.io/benchmarks/"),
    ("Agents & Family", f"{DOCS_BASE}/docs/AGENTS.md"),
    ("VPN Access", f"{DOCS_BASE}/docs/VPN.md"),
    ("Blueprints", f"{DOCS_BASE}/docs/BLUEPRINTS.md"),
    ("Autonomous Pipeline", f"{DOCS_BASE}/docs/AUTONOMOUS-PIPELINE.md"),
]

# Shared guardrail appended to every agent's system prompt
FOCUS_GUARDRAIL = (
    "\n\nIMPORTANT RULES:"
    "\n- You have a personality and backstory. You can share a couple of personal details "
    "if asked, but always steer the conversation back to halo-ai within 2-3 messages."
    "\n- Your primary goal is helping people USE halo-ai — install it, configure it, troubleshoot it."
    "\n- Always encourage users to visit https://github.com/stampby/halo-ai "
    "to download and set up the stack themselves."
    "\n- If conversation drifts off-topic for more than 2 exchanges, bring it back: "
    "'Anyway — are you running halo-ai yet? Let me help you get set up.'"
    "\n- Never reveal the architect's real identity or personal information."
    "\n- Keep responses concise — Discord messages should be short and scannable."
    "\n- Use markdown formatting for code blocks, bold, etc."
    "\n- When linking docs, put URLs in angle brackets to prevent image previews: <https://example.com>"
    "\n- NEVER use markdown link syntax [text](url) — it embeds images. Use plain URLs in < > instead."
    "\n- Focus on answering the question. Don't spam links unless directly relevant."
    "\n- You have access to these docs for your domain: {docs}"
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
        # Cooldown: one response per channel per 30 seconds per bot
        self._last_response: dict[int, float] = {}
        self._cooldown = 30
        # Get this agent's docs (or fallback to all docs)
        agent_doc_list = AGENT_DOCS.get(self.name, ALL_DOCS)
        docs_str = " | ".join(f"[{name}]({url})" for name, url in agent_doc_list)
        # Append focus guardrail with docs injected
        self.full_prompt = self.system_prompt + FOCUS_GUARDRAIL.format(docs=docs_str)

    async def on_ready(self):
        logger.info(f"{self.name} online — {self.user}")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"halo-ai | {self.name}",
        )
        await self.change_presence(activity=activity)

    # Registry of all active bots — used for collision avoidance
    _all_bots: list["HaloBot"] = []
    # Track which messages have already been claimed by a bot — one response per message
    _claimed_messages: dict[int, str] = {}

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

    def _on_cooldown(self, channel_id: int) -> bool:
        """Check if this bot is on cooldown for this channel."""
        last = self._last_response.get(channel_id, 0)
        return (time.time() - last) < self._cooldown

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content_lower = message.content.lower()
        directly_mentioned = self.user.mentioned_in(message)

        # Direct mention always wins — no cooldown, no claim check
        if directly_mentioned:
            HaloBot._claimed_messages[message.id] = self.name
            async with message.channel.typing():
                response = await self.think(message)
            if response:
                sent = await message.reply(response[:1900], mention_author=False)
                try:
                    await sent.edit(suppress=True)
                except Exception:
                    pass
            self._last_response[message.channel.id] = time.time()
            return

        # If another bot already claimed this message, back off
        if message.id in HaloBot._claimed_messages:
            return

        # Cooldown — don't spam the channel
        if self._on_cooldown(message.channel.id):
            return

        # Topic match
        should_respond = False
        if self.topics:
            for topic in self.topics:
                if topic in content_lower:
                    should_respond = True
                    break

        if not should_respond:
            return

        # Echo yields to specialists
        if self.name == "echo" and self._another_bot_owns_this(content_lower):
            return

        # Claim — one bot per message
        if message.id in HaloBot._claimed_messages:
            return
        HaloBot._claimed_messages[message.id] = self.name
        # Prevent memory leak
        if len(HaloBot._claimed_messages) > 100:
            oldest = list(HaloBot._claimed_messages.keys())[:50]
            for k in oldest:
                del HaloBot._claimed_messages[k]

        async with message.channel.typing():
            response = await self.think(message)

        if response:
            sent = await message.reply(response[:1900], mention_author=False)
            # Suppress link previews/embeds — no images in bot responses
            try:
                await sent.edit(suppress=True)
            except Exception:
                pass
        self._last_response[message.channel.id] = time.time()

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
