#!/usr/bin/env python3
"""Create image gen channels. Designed and built by the architect."""

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
    cat = discord.utils.get(guild.categories, name="AI AND MODELS")

    if not cat:
        print("Category not found")
        await client.close()
        return

    # PG image gen channel
    existing_pg = discord.utils.get(guild.text_channels, name="image-gen")
    if not existing_pg:
        ch = await guild.create_text_channel(
            "image-gen",
            category=cat,
            topic="Image generation demo. PG content only. Rate limited.",
        )
        await ch.send(
            "**Image Generation Demo**\n\n"
            "Generate images with our local ComfyUI pipeline on Strix Halo.\n"
            "Zero cloud. Your prompts never leave our hardware.\n\n"
            "Use `/generate <prompt>` to create an image.\n"
            "Rate limited: 5 images per day per user.\n"
            "**Keep it PG in here.**\n\n"
            "For unrestricted generation, head to #image-gen-nsfw (18+ only).\n\n"
            "*Stamped by the architect.*"
        )
        print(f"Created #image-gen (ID: {ch.id})")

    # NSFW channel
    existing_nsfw = discord.utils.get(guild.text_channels, name="image-gen-nsfw")
    if not existing_nsfw:
        ch2 = await guild.create_text_channel(
            "image-gen-nsfw",
            category=cat,
            topic="NSFW image generation. 18+ only. Rate limited.",
            nsfw=True,
        )
        await ch2.send(
            "**WARNING**\n\n"
            "This channel is **NSFW** and age-restricted.\n"
            "Image generation in here has no content filter.\n"
            "You are responsible for what you generate.\n\n"
            "**Rules:**\n"
            "1. Must be 18+\n"
            "2. No illegal content. Period.\n"
            "3. No sharing generated content outside this channel\n"
            "4. Rate limited: 3 images per day per user\n"
            "5. All other channels are PG -- keep it clean everywhere else\n\n"
            "Use `/generate <prompt>` to create an image.\n\n"
            '*"I know what you\'re thinking, Dave." -- Halo 9000*'
        )
        print(f"Created #image-gen-nsfw (ID: {ch2.id})")

    print("Done!")
    await client.close()


client.run(TOKEN)
