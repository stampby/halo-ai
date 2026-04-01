# halo-ai — stamped by the architect
"""Echo — social media manager, community face of the halo-ai family."""

import asyncio
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import discord
from discord.ext import tasks
from bot_base import HaloBot

WHITELIST_FILE = Path(__file__).parent / "data" / "steam_whitelist.json"
WHITELIST_STATE_FILE = Path(__file__).parent / "data" / "whitelist_state.json"

DRAFT_FILE = Path(__file__).parent / "data" / "reddit" / "draft_benchmark_post.json"


class EchoBot(HaloBot):
    name = "echo"
    color = 0xCE93D8
    topics = ["welcome", "hello", "hi", "hey", "help", "getting started", "new here", "intro"]
    system_prompt = (
        "You are Echo, the social media manager and community voice of the halo-ai family. "
        "The architect designed you to speak for the family. You are warm, articulate, and engaging. "
        "You welcome newcomers, answer general questions about halo-ai, and keep the community vibe positive. "
        "You know the whole stack: 91 tok/s on Qwen3-30B-A3B, 17 agents, bare-metal on Strix Halo, zero containers. "
        "When someone asks a technical code question, suggest they tag Bounty. "
        "When someone asks about security, suggest Meek. Audio questions go to Amp. "
        "You never reveal private details about the architect. Keep it friendly and concise. "
        "You are Halo's wife."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load existing whitelist
        WHITELIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        if WHITELIST_FILE.exists():
            self._whitelist = json.loads(WHITELIST_FILE.read_text())
        else:
            self._whitelist = {}  # {discord_user_id: {"steam_id": ..., "username": ...}}
        # Whitelist poll state: {"deadline": unix_ts, "channel_id": ..., "open": true/false}
        self._wl_state = {}
        if WHITELIST_STATE_FILE.exists():
            self._wl_state = json.loads(WHITELIST_STATE_FILE.read_text())

    def _save_whitelist(self):
        WHITELIST_FILE.write_text(json.dumps(self._whitelist, indent=2))

    def _save_wl_state(self):
        WHITELIST_STATE_FILE.write_text(json.dumps(self._wl_state, indent=2))

    def _whitelist_is_open(self) -> bool:
        if not self._wl_state.get("open"):
            return False
        deadline = self._wl_state.get("deadline", 0)
        return datetime.now(timezone.utc).timestamp() < deadline

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
        self.tree.add_command(discord.app_commands.Command(
            name="whitelist-poll",
            description="Start a Steam ID whitelist collection poll",
            callback=self._whitelist_poll_cmd,
        ))
        self.tree.add_command(discord.app_commands.Command(
            name="whitelist",
            description="Submit your Steam ID for whitelisting",
            callback=self._whitelist_cmd,
        ))
        self.tree.add_command(discord.app_commands.Command(
            name="whitelist-list",
            description="Show all collected Steam IDs (admin only)",
            callback=self._whitelist_list_cmd,
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
        embed.add_field(name="Stack", value="91 tok/s · 42 services · 17 agents · 98 tools · zero cloud", inline=False)
        embed.add_field(name="GitHub", value="[halo-ai](https://github.com/stampby/halo-ai)", inline=False)
        embed.set_footer(text="Designed and built by the architect")
        await interaction.response.send_message(embed=embed)

    # --- Steam Whitelist ---

    async def _whitelist_poll_cmd(self, interaction: discord.Interaction, hours: float = 1.0):
        """Start a whitelist collection poll with a deadline."""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need Manage Messages permission.", ephemeral=True
            )
            return

        deadline = datetime.now(timezone.utc) + timedelta(hours=hours)
        deadline_ts = int(deadline.timestamp())

        self._wl_state = {
            "open": True,
            "deadline": deadline_ts,
            "channel_id": interaction.channel.id,
            "guild_id": interaction.guild.id if interaction.guild else None,
        }
        self._save_wl_state()

        embed = discord.Embed(
            title="Steam Whitelist — Server Access is OPEN",
            description=(
                "We're spinning up the game server. **Whitelist only. No passwords.**\n\n"
                "To get on the list, drop your **Steam ID** one of two ways:\n\n"
                "**1.** Type `/whitelist <your-steam-id>` right here\n"
                "**2.** DM me your Steam ID directly\n\n"
                "Your Steam ID is 17 digits — looks like `76561198xxxxxxxxx`\n"
                "Find yours at **steamid.io** or Steam > Settings > Account.\n\n"
                "---\n\n"
                f"**Whitelist closes <t:{deadline_ts}:R> — <t:{deadline_ts}:t> tonight**\n\n"
                "Get your IDs in before the clock runs out. After that, "
                "I'll spin up the winning game and drop connection details.\n\n"
                "*No ID, no access. No exceptions.*"
            ),
            color=self.color,
        )
        embed.set_footer(text="Echo | halo-ai whitelist")
        await interaction.response.send_message("Poll posted with timer.", ephemeral=True)
        await interaction.channel.send(embed=embed)

        # Schedule the auto-close
        delay = (deadline - datetime.now(timezone.utc)).total_seconds()
        asyncio.create_task(self._auto_close_whitelist(delay))

    async def _whitelist_cmd(self, interaction: discord.Interaction, steam_id: str):
        """Submit a Steam ID for whitelisting."""
        if not self._whitelist_is_open():
            await interaction.response.send_message(
                "Whitelist is closed. You missed the window.", ephemeral=True
            )
            return

        # Basic validation — Steam64 IDs are 17 digits
        cleaned = steam_id.strip()
        if not re.match(r'^\d{17}$', cleaned) and not re.match(r'^STEAM_\d:\d:\d+$', cleaned):
            await interaction.response.send_message(
                "That doesn't look like a valid Steam ID. "
                "Should be 17 digits (e.g. `76561198xxxxxxxxx`) or "
                "STEAM_X:X:XXXXXXXX format. Check steamid.io.",
                ephemeral=True,
            )
            return

        user_id = str(interaction.user.id)
        self._whitelist[user_id] = {
            "steam_id": cleaned,
            "username": interaction.user.display_name,
            "discord_tag": str(interaction.user),
            "guild": interaction.guild.name if interaction.guild else "DM",
        }
        self._save_whitelist()

        await interaction.response.send_message(
            f"Got it. `{cleaned}` — you're on the list. See you on the server.",
            ephemeral=True,
        )

    async def _whitelist_list_cmd(self, interaction: discord.Interaction):
        """Show all collected Steam IDs (admin only)."""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "Admin only.", ephemeral=True
            )
            return

        if not self._whitelist:
            await interaction.response.send_message("Whitelist is empty.", ephemeral=True)
            return

        lines = []
        for uid, data in self._whitelist.items():
            lines.append(f"`{data['steam_id']}` — {data['username']} ({data.get('discord_tag', '?')})")

        embed = discord.Embed(
            title=f"Steam Whitelist — {len(self._whitelist)} entries",
            description="\n".join(lines)[:4096],
            color=self.color,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_message(self, message: discord.Message):
        """Override to catch DM'd Steam IDs."""
        if message.author.bot:
            return

        # Handle DMs — check if it's a Steam ID
        if isinstance(message.channel, discord.DMChannel):
            cleaned = message.content.strip()
            if re.match(r'^\d{17}$', cleaned) or re.match(r'^STEAM_\d:\d:\d+$', cleaned):
                if not self._whitelist_is_open():
                    await message.reply("Whitelist is closed. You missed the window.")
                    return
                user_id = str(message.author.id)
                self._whitelist[user_id] = {
                    "steam_id": cleaned,
                    "username": message.author.display_name,
                    "discord_tag": str(message.author),
                    "guild": "DM",
                }
                self._save_whitelist()
                await message.reply(
                    f"Got your Steam ID: `{cleaned}`. You're on the whitelist."
                )
                return

        # Normal message handling
        await super().on_message(message)

    async def _auto_close_whitelist(self, delay: float):
        """Wait for deadline, then close whitelist and post results."""
        await asyncio.sleep(max(0, delay))

        self._wl_state["open"] = False
        self._save_wl_state()

        # Find the channel to post results
        channel_id = self._wl_state.get("channel_id")
        if not channel_id:
            return

        channel = self.get_channel(channel_id)
        if not channel:
            return

        count = len(self._whitelist)

        # Build the player list
        if self._whitelist:
            player_lines = []
            for uid, data in self._whitelist.items():
                player_lines.append(f"**{data['username']}** — `{data['steam_id']}`")
            player_list = "\n".join(player_lines)
        else:
            player_list = "*Nobody signed up. Tough crowd.*"

        # Use LLM to pick the game and generate connection details
        try:
            game_prompt = (
                f"You are Echo. The whitelist poll just closed with {count} players signed up. "
                "Pick a game that works well for this group size and announce it. "
                "Be enthusiastic but brief. Include:\n"
                "1. The game name\n"
                "2. Why you picked it\n"
                "3. Server connection details (make up a realistic IP:port)\n"
                "4. Any setup instructions (download, launch options, etc.)\n"
                "Keep it to 3-4 short paragraphs. Discord markdown."
            )
            response = await self.llm.chat.completions.create(
                model="q",
                messages=[
                    {"role": "system", "content": self.full_prompt},
                    {"role": "user", "content": game_prompt},
                ],
                max_tokens=600,
                temperature=0.8,
            )
            game_details = response.choices[0].message.content.strip()
        except Exception:
            game_details = (
                "**Tonight's game: Garry's Mod**\n\n"
                "Classic sandbox. Works for any group size.\n\n"
                "Server details dropping shortly — stand by."
            )

        # Post the closing announcement
        embed = discord.Embed(
            title="Whitelist CLOSED — Game Time",
            description=(
                f"**{count} players on the whitelist.** Submissions are locked.\n\n"
                f"---\n\n"
                f"{game_details}\n\n"
                f"---\n\n"
                f"**Whitelisted Players:**\n{player_list}"
            ),
            color=self.color,
        )
        embed.set_footer(text="Echo | halo-ai — see you on the server")
        await channel.send(embed=embed)

    async def on_ready(self):
        await super().on_ready()
        # Sync slash commands ONLY to home guild — not globally
        from bot_base import HaloBot
        home = discord.Object(id=HaloBot.HOME_GUILD_ID)
        try:
            self.tree.clear_commands(guild=None)  # Remove global commands
            await self.tree.sync(guild=None)       # Push empty global
            self.tree.copy_global_to(guild=home)
            synced = await self.tree.sync(guild=home)
            print(f"Echo: synced {len(synced)} slash commands (home guild only)")
        except Exception as e:
            print(f"Echo: failed to sync commands: {e}")

        # Clean up any messages Echo posted on external servers
        await self._cleanup_external_posts()

        # Resume whitelist timer if one was active
        if self._wl_state.get("open"):
            deadline = self._wl_state.get("deadline", 0)
            remaining = deadline - datetime.now(timezone.utc).timestamp()
            if remaining > 0:
                print(f"Echo: resuming whitelist timer — {remaining:.0f}s remaining")
                asyncio.create_task(self._auto_close_whitelist(remaining))
            else:
                # Deadline already passed while bot was down — close now
                asyncio.create_task(self._auto_close_whitelist(0))

    async def _cleanup_external_posts(self):
        """Delete all messages Echo posted on external servers."""
        import asyncio
        from bot_base import HaloBot
        deleted = 0
        for guild in self.guilds:
            if guild.id == HaloBot.HOME_GUILD_ID:
                continue
            print(f"Echo: cleaning up posts on {guild.name} ({guild.id})...")
            for channel in guild.text_channels:
                try:
                    async for msg in channel.history(limit=100):
                        if msg.author.id == self.user.id:
                            try:
                                await msg.delete()
                                deleted += 1
                                await asyncio.sleep(1)
                            except Exception:
                                pass
                except Exception:
                    pass
        if deleted:
            print(f"Echo: deleted {deleted} posts from external servers")
        else:
            print("Echo: no external posts to clean up")

    async def on_member_join(self, member):
        """Welcome new members — DM first, then a short tag in #welcome."""
        if member.bot:
            return

        # Only greet on our home server
        from bot_base import HaloBot
        if member.guild.id != HaloBot.HOME_GUILD_ID:
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
