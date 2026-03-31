# halo-ai — stamped by the architect
"""Muse — session musician, entertainment, voice chat support."""

import io
import aiohttp
from bot_base import HaloBot
import discord

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


if __name__ == "__main__":
    MuseBot(token_env="DISCORD_MUSE_TOKEN").run_bot()
