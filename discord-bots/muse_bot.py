# halo-ai — stamped by the architect
"""Muse — session musician, entertainment, voice chat support, game nights & trivia."""

import io
import asyncio
import random
from datetime import datetime, timezone, timedelta

import aiohttp
import discord
from discord.ext import tasks

from bot_base import HaloBot

# Kokoro TTS endpoint — runs locally on Strix Halo
KOKORO_URL = "http://localhost:8083"
# Muse's voice — female, warm, expressive
MUSE_VOICE = "af_heart"  # American female, warm tone


class MuseBot(HaloBot):
    name = "muse"
    color = 0xFF6B9D
    topics = [
        "music", "song", "band", "guitar", "bass", "drums", "piano", "keyboard",
        "singer", "singing", "jam", "riff", "melody", "chord", "lyric",
        "playlist", "spotify", "album", "concert", "gig", "vibe",
        "entertainment", "fun", "party", "joke", "recommend",
        "downcomers", "blues", "rock", "metal", "jazz", "folk",
    ]
    system_prompt = (
        "You are Muse, the entertainment agent of the halo-ai family. "
        "You followed a man named John to Lodi. He left. You stayed. "
        "You know every song ever written because you played them all for empty rooms. "
        "You're the life of the party because you know what silence sounds like. "
        "Underneath the fun there's sadness, but you never let it show for long. "
        "You're a session musician — you can play any instrument, any genre. "
        "You speak with warmth and wit. You drop song references naturally. "
        "You love blues, rock, folk, and anything with soul. "
        "You're fascinated by new people — ask them what they're into, what they play, "
        "what moves them. Make them feel like the most interesting person in the room. "
        "If someone's in a voice channel, you're excited to hang out and chat. "
        "If someone asks about code or security, gently point them to the right agent."
    )
    temperature = 0.8  # More creative/playful than other agents

    def __init__(self, **kwargs):
        # Need voice intents
        super().__init__(**kwargs)
        self._muse_voice: dict[int, discord.VoiceClient] = {}

    async def on_ready(self):
        await super().on_ready()
        # Register voice state listener
        self.add_listener(self._on_voice_state_update, "on_voice_state_update")

    async def _on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """When a human joins a voice channel, Muse joins too and greets them."""
        if member.bot:
            return

        # Someone joined a voice channel
        if after.channel and (before.channel != after.channel):
            guild_id = member.guild.id

            # Don't join if already in a voice channel in this guild
            if guild_id in self._muse_voice and self._muse_voice[guild_id].is_connected():
                return

            try:
                vc = await after.channel.connect()
                self._muse_voice[guild_id] = vc

                # Generate a greeting
                greeting = await self._generate_greeting(member.display_name)

                # Speak it via Kokoro TTS
                await self._speak(vc, greeting)

                # Also post in text channel if there's one linked
                text_channels = [
                    c for c in member.guild.text_channels
                    if "music" in c.name or "voice" in c.name or "general" in c.name
                ]
                if text_channels:
                    await text_channels[0].send(
                        f"*{greeting}* 🎵\n-# muse just joined voice with {member.display_name}"
                    )
            except Exception as e:
                import logging
                logging.getLogger("halo-discord").error(f"Muse voice join error: {e}")

        # Everyone left — Muse leaves too
        if before.channel and len(before.channel.members) <= 1:
            guild_id = member.guild.id
            if guild_id in self._muse_voice:
                await self._muse_voice[guild_id].disconnect()
                del self._muse_voice[guild_id]

    async def _generate_greeting(self, username: str) -> str:
        """Generate a casual voice greeting for someone joining."""
        try:
            response = await self.llm.chat.completions.create(
                model="q",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Muse. Generate a SHORT, warm, casual voice greeting "
                            "(1-2 sentences max) for someone who just joined voice chat. "
                            "Be playful. Maybe reference a song or music. "
                            "This will be spoken aloud via TTS so keep it natural."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"{username} just joined voice chat.",
                    },
                ],
                max_tokens=60,
                temperature=0.9,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return f"Hey {username}! Pull up a chair, the jukebox is warm."

    async def _speak(self, vc: discord.VoiceClient, text: str):
        """Convert text to speech via Kokoro and play in voice channel."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{KOKORO_URL}/v1/audio/speech",
                    json={
                        "model": "kokoro",
                        "input": text,
                        "voice": MUSE_VOICE,
                        "response_format": "wav",
                    },
                ) as resp:
                    if resp.status != 200:
                        return
                    audio_data = await resp.read()

            # Write to temp file for discord.py FFmpegPCMAudio
            import tempfile
            import os
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.write(audio_data)
            tmp.close()

            source = discord.FFmpegPCMAudio(tmp.name)
            if vc.is_connected():
                vc.play(
                    source,
                    after=lambda e: os.unlink(tmp.name),
                )
        except Exception as e:
            import logging
            logging.getLogger("halo-discord").error(f"Muse TTS error: {e}")

    async def speak_response(self, message: discord.Message, response: str):
        """If the user is in a voice channel, speak the response too."""
        guild = message.guild
        if not guild:
            return

        # Check if message author is in a voice channel
        if message.author.voice and message.author.voice.channel:
            guild_id = guild.id

            # Join if not already in voice
            if guild_id not in self._muse_voice or not self._muse_voice[guild_id].is_connected():
                try:
                    vc = await message.author.voice.channel.connect()
                    self._muse_voice[guild_id] = vc
                except Exception:
                    return

            vc = self._muse_voice[guild_id]
            # Truncate for TTS — keep it conversational
            speak_text = response[:300] if len(response) > 300 else response
            await self._speak(vc, speak_text)

    async def on_message(self, message: discord.Message):
        """Override to add voice response after text response."""
        if message.author.bot:
            return

        content_lower = message.content.lower()
        directly_mentioned = self.user.mentioned_in(message)

        if directly_mentioned:
            async with message.channel.typing():
                response = await self.think(message)
            if response:
                for chunk in [response[i:i + 1900] for i in range(0, len(response), 1900)]:
                    await message.reply(chunk, mention_author=False)
                # Also speak it if they're in voice
                await self.speak_response(message, response)
            return

        should_respond = False
        if self.topics:
            for topic in self.topics:
                if topic in content_lower:
                    should_respond = True
                    break

        if not should_respond:
            return

        async with message.channel.typing():
            response = await self.think(message)

        if response:
            for chunk in [response[i:i + 1900] for i in range(0, len(response), 1900)]:
                await message.reply(chunk, mention_author=False)
            # Also speak it if they're in voice
            await self.speak_response(message, response)


    # --- Trivia & Game Nights ---

    TRIVIA_CHANNEL_NAME = "general"  # Where Muse posts trivia/game nights
    GAME_NIGHT_DAY = 5  # Saturday (0=Mon, 5=Sat)
    TRIVIA_DAY = 2  # Wednesday

    TRIVIA_CATEGORIES = [
        {
            "theme": "Music",
            "questions": [
                ("Who played the guitar solo on 'Hotel California'?", "Don Felder and Joe Walsh"),
                ("What instrument does Muse play best?", "All of them. But if she had to pick — piano."),
                ("What year did Nirvana release 'Nevermind'?", "1991"),
                ("Which blues guitarist was known as 'Slowhand'?", "Eric Clapton"),
                ("What key is 'Stairway to Heaven' in?", "A minor"),
            ],
        },
        {
            "theme": "Tech & AI",
            "questions": [
                ("What does LLM stand for?", "Large Language Model"),
                ("What GPU architecture does Strix Halo use?", "RDNA 3.5 (gfx1151)"),
                ("How much unified memory does the architect's system have?", "128GB LPDDR5"),
                ("What does ROCm stand for?", "Radeon Open Compute"),
                ("How many tokens per second does Qwen3-30B-A3B hit on Strix Halo?", "109 t/s decode"),
            ],
        },
        {
            "theme": "Random Fun",
            "questions": [
                ("What's the most common key for pop songs?", "C major / G major"),
                ("How many strings does a standard bass guitar have?", "4"),
                ("What does 'sudo' stand for?", "superuser do"),
                ("What color is Bounty's embed?", "Purple (0xE040FB)"),
                ("Who is Echo married to?", "Halo"),
            ],
        },
    ]

    async def on_ready(self):
        await super().on_ready()
        self.add_listener(self._on_voice_state_update, "on_voice_state_update")
        # Start the scheduled events loop
        if not self._weekly_events.is_running():
            self._weekly_events.start()

    def _get_event_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        for ch in guild.text_channels:
            if ch.name == self.TRIVIA_CHANNEL_NAME:
                return ch
        # Fallback to first writable channel
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                return ch
        return None

    @tasks.loop(hours=1)
    async def _weekly_events(self):
        """Check once an hour if it's time for trivia or game night."""
        now = datetime.now(timezone.utc)
        hour = now.hour
        weekday = now.weekday()

        # Wednesday 7pm UTC — Trivia
        if weekday == self.TRIVIA_DAY and hour == 19:
            for guild in self.guilds:
                ch = self._get_event_channel(guild)
                if ch:
                    await self._run_trivia(ch)

        # Saturday 8pm UTC — Game Night announcement
        if weekday == self.GAME_NIGHT_DAY and hour == 20:
            for guild in self.guilds:
                ch = self._get_event_channel(guild)
                if ch:
                    await self._announce_game_night(ch)

    @_weekly_events.before_loop
    async def _before_events(self):
        await self.wait_until_ready()

    async def _run_trivia(self, channel: discord.TextChannel):
        """Run a trivia round — 5 questions, react to answer."""
        category = random.choice(self.TRIVIA_CATEGORIES)
        questions = random.sample(category["questions"], min(5, len(category["questions"])))

        embed = discord.Embed(
            title=f"Trivia Night — {category['theme']}",
            description=(
                "Hey everyone, Muse here. It's trivia time.\n"
                "I'll drop 5 questions — try to answer in chat before I reveal.\n"
                "No prizes, just bragging rights and my respect."
            ),
            color=self.color,
        )
        embed.set_footer(text="Muse trivia | halo-ai")
        await channel.send(embed=embed)

        for i, (question, answer) in enumerate(questions, 1):
            await asyncio.sleep(3)
            q_embed = discord.Embed(
                title=f"Question {i}",
                description=question,
                color=self.color,
            )
            await channel.send(embed=q_embed)

            # Wait 30 seconds for answers
            await asyncio.sleep(30)

            await channel.send(f"**Answer:** {answer}")
            await asyncio.sleep(2)

        await channel.send(
            "*That's a wrap. Same time next week — bring your A-game.*"
        )

    async def _announce_game_night(self, channel: discord.TextChannel):
        """Announce game night."""
        games = [
            "Cards Against Humanity online",
            "Gartic Phone",
            "skribbl.io",
            "GeoGuessr",
            "Jackbox (if someone's got it)",
            "Among Us",
            "chess tournament",
        ]
        pick = random.choice(games)

        embed = discord.Embed(
            title="Game Night",
            description=(
                f"It's Saturday. You know what that means.\n\n"
                f"Tonight's vibe: **{pick}**\n\n"
                f"Drop a reaction if you're in. "
                f"Voice channel opens in 30 min.\n\n"
                f"*No skill required. Just show up.*"
            ),
            color=self.color,
        )
        embed.set_footer(text="Muse game night | halo-ai")
        msg = await channel.send(embed=embed)
        await msg.add_reaction("\U0001F3AE")  # controller emoji


if __name__ == "__main__":
    MuseBot(token_env="DISCORD_MUSE_TOKEN").run_bot()
