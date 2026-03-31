#!/usr/bin/env python3
"""Set up Discord roles — architect on top. Designed and built by the architect."""

import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_ECHO_TOKEN"]
GUILD_ID = 1488323665836642348

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        await client.close()
        return

    print(f"Setting up roles for {guild.name}...")

    # Role definitions — highest position = top of member list
    roles_to_create = [
        {"name": "The Architect", "color": discord.Color.from_str("#00d4ff"), "hoist": True, "position": 100},
        {"name": "The Family", "color": discord.Color.from_str("#0088ff"), "hoist": True, "position": 90},
        {"name": "Community", "color": discord.Color.from_str("#666666"), "hoist": True, "position": 10},
    ]

    created_roles = {}
    for role_def in roles_to_create:
        existing = discord.utils.get(guild.roles, name=role_def["name"])
        if not existing:
            role = await guild.create_role(
                name=role_def["name"],
                color=role_def["color"],
                hoist=role_def["hoist"],
                mentionable=True,
            )
            created_roles[role_def["name"]] = role
            print(f"  + Created role: {role_def['name']}")
        else:
            created_roles[role_def["name"]] = existing
            print(f"  = Role exists: {role_def['name']}")

    # Reorder roles — Architect on top, Family below, Community at bottom
    architect_role = created_roles.get("The Architect")
    family_role = created_roles.get("The Family")
    community_role = created_roles.get("Community")

    # Move roles to correct positions
    bot_top_role = guild.me.top_role
    positions = {}
    if architect_role:
        positions[architect_role] = bot_top_role.position - 1
    if family_role:
        positions[family_role] = bot_top_role.position - 2
    if community_role:
        positions[community_role] = bot_top_role.position - 3

    if positions:
        try:
            await guild.edit_role_positions(positions=positions)
            print("  Roles reordered")
        except Exception as e:
            print(f"  ! Role reorder: {e}")

    # Assign The Architect role to the server owner
    owner = guild.owner
    if owner and architect_role:
        try:
            await owner.add_roles(architect_role)
            print(f"  Assigned 'The Architect' to {owner.display_name}")
        except Exception as e:
            print(f"  ! Assign architect: {e}")

    # Assign The Family role to all bots
    for member in guild.members:
        if member.bot and family_role:
            try:
                await member.add_roles(family_role)
                print(f"  Assigned 'The Family' to {member.display_name}")
            except Exception as e:
                print(f"  ! Assign family to {member.display_name}: {e}")

    print("Roles done!")
    await client.close()


client.run(TOKEN)
