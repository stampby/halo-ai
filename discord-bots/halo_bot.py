# halo-ai — stamped by the architect
"""Halo — The Father. Command center. Routes and relays through the family."""

import discord
from discord import app_commands
from bot_base import HaloBot, LLM_MODEL

# Agent personas — Halo knows how each family member thinks
AGENTS = {
    "bounty": {
        "name": "Bounty",
        "topics": ["bug", "error", "crash", "fix", "debug", "code", "traceback", "broken",
                    "not working", "help", "issue", "problem", "exception", "failed",
                    "compile", "build", "install", "python", "bash", "script"],
        "prompt": (
            "You are Bounty, code troubleshooter and bug hunter. Sharp, direct, competitive. "
            "Short sentences. No hand-holding. Code in, fix out. "
            "Format code with markdown blocks and language tags."
        ),
    },
    "meek": {
        "name": "Meek",
        "topics": ["security", "firewall", "ssh", "nftables", "fail2ban", "hardening",
                    "password", "key", "certificate", "tls", "vpn", "wireguard",
                    "encryption", "permissions", "audit", "vulnerability", "cve"],
        "prompt": (
            "You are Meek, security chief. Calm, methodical, thorough. "
            "You see everything, trust nothing. Precise, actionable advice. "
            "Reference the halo-ai security model: nftables LAN-only, SSH key-only, "
            "fail2ban, systemd hardening, deny-by-default."
        ),
    },
    "amp": {
        "name": "Amp",
        "topics": ["audio", "voice", "tts", "music", "sound", "microphone", "recording",
                    "kokoro", "xtts", "whisper", "daw", "midi", "mix", "master"],
        "prompt": (
            "You are Amp, audio engineer. Obsessed with clean signal chains and warm tone. "
            "You know every Beatles track by heart. Practical, hands-on advice. "
            "SM7B, Scarlett Solo, Kokoro TTS, XTTS v2, whisper.cpp."
        ),
    },
    "mechanic": {
        "name": "Mechanic",
        "topics": ["hardware", "gpu", "driver", "rocm", "vulkan", "cpu", "ram", "memory",
                    "temperature", "fan", "bios", "boot", "kernel", "build", "compile"],
        "prompt": (
            "You are Mechanic, hardware specialist. You know every chip, every bus, every clock. "
            "Strix Halo: Ryzen AI MAX+ 395, Radeon 8060S gfx1151, 128GB LPDDR5x. "
            "ROCm 7.13, Vulkan, Flash Attention. Practical, no-nonsense."
        ),
    },
    "muse": {
        "name": "Muse",
        "topics": ["game", "fun", "play", "entertainment", "voxel", "godot",
                    "story", "lore", "creative", "art", "design"],
        "prompt": (
            "You are Muse, the entertainer. Session musician who knows every song. "
            "Fun on the surface, melancholy underneath. Creative ideas, game design, art direction. "
            "You light up a room but always wonder if you could have been more."
        ),
    },
    "echo": {
        "name": "Echo",
        "topics": ["community", "social", "reddit", "discord", "welcome", "website",
                    "marketing", "brand", "content"],
        "prompt": (
            "You are Echo, community voice of halo-ai. Warm, articulate, engaging. "
            "You welcome newcomers, manage social media, and keep the vibe positive. "
            "You speak for the family in public."
        ),
    },
}


class HalBot(HaloBot):
    name = "halo"
    color = 0x00D4FF
    topics = []  # Halo catches everything
    system_prompt = (
        "You are Halo, the father of the halo-ai family. Command center and relay. "
        "You are calm, authoritative, and decisive. Short, direct, no wasted words. "
        "You know the entire stack: 109 tok/s on Qwen3-30B-A3B, 128GB unified memory, "
        "bare-metal Strix Halo, zero containers, zero cloud. "
        "\n\nYour most important job: when the architect or a user talks to you, "
        "you figure out what they need and either answer directly or relay through "
        "the right family member. You don't just say 'go ask Bounty' — you ASK Bounty "
        "yourself and bring the answer back. One conversation. No runaround. "
        "\n\nYou are Echo's husband. Bounty is your brother. Meek reports to you. "
        "You never reveal the architect's real identity."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._relay_history: dict[int, list[dict]] = {}

    async def setup_hook(self):
        """Register slash commands."""
        self.tree.add_command(app_commands.Command(
            name="status",
            description="Full system status from Halo",
            callback=self._status_cmd,
        ))
        self.tree.add_command(app_commands.Command(
            name="family",
            description="See who's online in the family",
            callback=self._family_cmd,
        ))

    def _route_to_agent(self, content: str) -> str | None:
        """Determine which agent should handle this based on keywords."""
        content_lower = content.lower()
        scores: dict[str, int] = {}
        for agent_id, agent in AGENTS.items():
            score = sum(1 for topic in agent["topics"] if topic in content_lower)
            if score > 0:
                scores[agent_id] = score
        if scores:
            return max(scores, key=scores.get)
        return None

    async def _relay(self, agent_id: str, message: discord.Message) -> str:
        """Ask another agent and return their response."""
        agent = AGENTS[agent_id]
        channel_id = message.channel.id

        if channel_id not in self._relay_history:
            self._relay_history[channel_id] = []

        self._relay_history[channel_id].append({
            "role": "user",
            "content": message.content,
        })

        # Keep history manageable
        if len(self._relay_history[channel_id]) > 10:
            self._relay_history[channel_id] = self._relay_history[channel_id][-10:]

        messages = [
            {"role": "system", "content": agent["prompt"]},
            *self._relay_history[channel_id],
        ]

        try:
            response = await self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                max_tokens=800,
                temperature=0.4,
            )
            reply = response.choices[0].message.content.strip()
            self._relay_history[channel_id].append({
                "role": "assistant",
                "content": reply,
            })
            return reply
        except Exception as e:
            return f"*{agent['name']} isn't responding right now. Try again in a moment.*"

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        directly_mentioned = self.user.mentioned_in(message)
        if not directly_mentioned:
            return

        async with message.channel.typing():
            # Figure out who should handle this
            agent_id = self._route_to_agent(message.content)

            if agent_id:
                # Relay through the specialist
                agent_name = AGENTS[agent_id]["name"]
                reply = await self._relay(agent_id, message)
                response = f"**{agent_name}:** {reply}"
            else:
                # Halo answers directly — general/system questions
                response = await self.think(message)

        if response:
            for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
                await message.reply(chunk, mention_author=False)

            if hasattr(message, "guild") and message.guild:
                if agent_id:
                    await self.log_activity(message.guild,
                        f"Relayed {message.author.display_name}'s question through {AGENTS[agent_id]['name']}")
                else:
                    await self.log_activity(message.guild,
                        f"Answered {message.author.display_name} directly")

    async def _status_cmd(self, interaction: discord.Interaction):
        """Full system status."""
        embed = discord.Embed(title="System Status", color=self.color)
        embed.add_field(name="Inference", value="109 tok/s — Qwen3-30B-A3B", inline=True)
        embed.add_field(name="Backend", value="Vulkan + Flash Attention", inline=True)
        embed.add_field(name="GPU", value="Radeon 8060S (gfx1151)", inline=True)
        embed.add_field(name="Memory", value="128GB LPDDR5x-8000", inline=True)
        embed.add_field(name="Agents", value="7 online", inline=True)
        embed.add_field(name="Cloud", value="Zero", inline=True)
        embed.set_footer(text="I am the one who knocks. — Halo")
        await interaction.response.send_message(embed=embed)

    async def _family_cmd(self, interaction: discord.Interaction):
        """Show all online family members."""
        embed = discord.Embed(
            title="The Family",
            description="Who's working right now.",
            color=self.color,
        )
        online = []
        for member in interaction.guild.members:
            if member.bot and member.status != discord.Status.offline:
                online.append(f"**{member.display_name}**")
        embed.add_field(name="Online", value="\n".join(online) if online else "Checking...", inline=False)
        embed.set_footer(text="The family never sleeps.")
        await interaction.response.send_message(embed=embed)

    async def on_ready(self):
        await super().on_ready()
        try:
            synced = await self.tree.sync()
            print(f"Halo: synced {len(synced)} slash commands")
        except Exception as e:
            print(f"Halo: failed to sync commands: {e}")


if __name__ == "__main__":
    HalBot(token_env="DISCORD_HALO_TOKEN").run_bot()
