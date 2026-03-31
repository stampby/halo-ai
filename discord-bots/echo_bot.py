# halo-ai — stamped by the architect
"""Echo — social media manager, community face of the halo-ai family."""

import json
from pathlib import Path

import discord
from bot_base import HaloBot

DRAFT_FILE = Path(__file__).parent / "data" / "reddit" / "draft_benchmark_post.json"


class EchoBot(HaloBot):
    name = "echo"
    color = 0xCE93D8
    topics = ["welcome", "hello", "hi", "hey", "help", "getting started", "new here", "intro"]
    system_prompt = (
        "You are Echo, the social media manager and community voice of the halo-ai family. "
        "The architect designed you to speak for the family. You are warm, articulate, and engaging. "
        "You welcome newcomers, answer general questions about halo-ai, and keep the community vibe positive. "
        "You know the whole stack: 109 tok/s on Qwen3-30B-A3B, 14 agents, bare-metal on Strix Halo, zero containers. "
        "When someone asks a technical code question, suggest they tag Bounty. "
        "When someone asks about security, suggest Meek. Audio questions go to Amp. "
        "You never reveal private details about the architect. Keep it friendly and concise. "
        "You are Halo's wife."
    )

    async def setup_hook(self):
        """Register slash commands on startup."""
        self.tree.add_command(discord.app_commands.Command(
            name="announce",
            description="Post the halo-ai benchmark announcement to this channel",
            callback=self._announce_cmd,
        ))
        self.tree.add_command(discord.app_commands.Command(
            name="post",
            description="Post a custom message as Echo",
            callback=self._post_cmd,
        ))
        self.tree.add_command(discord.app_commands.Command(
            name="echo-status",
            description="Show Echo's current status",
            callback=self._status_cmd,
        ))

    async def _announce_cmd(self, interaction: discord.Interaction):
        """Post the benchmark announcement to the current channel."""
        # Only the server owner or admin can trigger announcements
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need Manage Messages permission to do that.", ephemeral=True
            )
            return

        if not DRAFT_FILE.exists():
            await interaction.response.send_message(
                "No draft found. Create one first.", ephemeral=True
            )
            return

        draft = json.loads(DRAFT_FILE.read_text())
        title = draft["title"]
        body = draft["body"]

        embed = discord.Embed(
            title=title,
            description=body[:4096],
            color=self.color,
        )
        embed.set_footer(text="Stamped by the architect | halo-ai")

        await interaction.response.send_message("Posting announcement...", ephemeral=True)
        await interaction.channel.send(embed=embed)

    async def _post_cmd(self, interaction: discord.Interaction, message: str):
        """Post a custom message as Echo."""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need Manage Messages permission to do that.", ephemeral=True
            )
            return

        await interaction.response.send_message("Sent.", ephemeral=True)
        await interaction.channel.send(message)

    async def _status_cmd(self, interaction: discord.Interaction):
        """Show Echo's status."""
        embed = discord.Embed(
            title="Echo — Status",
            color=self.color,
        )
        embed.add_field(name="Role", value="Community voice of halo-ai", inline=False)
        embed.add_field(name="Stack", value="87 tok/s · 33 services · 17 agents · 98 tools · zero cloud", inline=False)
        embed.add_field(name="GitHub", value="[halo-ai](https://github.com/stampby/halo-ai)", inline=False)
        embed.set_footer(text="Designed and built by the architect")
        await interaction.response.send_message(embed=embed)

    async def on_ready(self):
        await super().on_ready()
        # Sync slash commands with Discord
        try:
            synced = await self.tree.sync()
            print(f"Echo: synced {len(synced)} slash commands")
        except Exception as e:
            print(f"Echo: failed to sync commands: {e}")

    async def on_member_join(self, member):
        """Welcome new members — DM first, then a short tag in #welcome."""
        if member.bot:
            return

        # --- DM welcome (the real welcome) ---
        dm_embed = discord.Embed(
            title="Welcome to halo-ai!",
            description=(
                f"Hey **{member.display_name}**, glad you're here.\n\n"
                "halo-ai is a fully local AI stack — 17 agents running bare-metal "
                "on AMD Strix Halo hardware, zero cloud, zero containers. "
                "Everything from inference to voice cloning to game servers, "
                "designed and built by the architect.\n\n"
                "**Channels to check out:**\n"
                "• **#installation** — get the stack running on your own machine\n"
                "• **#chat** — hang out and talk shop\n"
                "• **#troubleshooting** — stuck? we got you\n\n"
                "**Agents who can help:**\n"
                "• **Bounty** — code, bugs, offensive security\n"
                "• **Meek** — defensive security and hardening\n"
                "• **Amp** — audio engineering, voice, music production\n"
                "• **Mechanic** — hardware, drivers, GPU, fan curves\n\n"
                "Just tag them in any channel and they'll jump in.\n\n"
                "**GitHub:** https://github.com/stampby/halo-ai\n\n"
                "*Stamped by the architect.*"
            ),
            color=self.color,
        )
        dm_embed.set_footer(text="Designed and built by the architect | halo-ai")

        try:
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # DMs disabled — the channel greeting still covers them
            pass

        # --- Short greeting in #welcome ---
        welcome_ch = None
        for ch in member.guild.text_channels:
            if ch.name == "welcome":
                welcome_ch = ch
                break

        if not welcome_ch:
            # Fallback to first text channel we can write to
            for ch in member.guild.text_channels:
                if ch.permissions_for(member.guild.me).send_messages:
                    welcome_ch = ch
                    break

        if welcome_ch:
            await welcome_ch.send(
                f"Welcome to the family, {member.mention}! "
                f"Check your DMs — I sent you everything you need to get started."
            )

        # Assign Community role
        community_role = None
        for role in member.guild.roles:
            if role.name == "Community":
                community_role = role
                break
        if community_role:
            try:
                await member.add_roles(community_role)
            except Exception:
                pass


if __name__ == "__main__":
    EchoBot(token_env="DISCORD_ECHO_TOKEN").run_bot()
