#!/usr/bin/env python3
"""Set up the halo-ai Discord server structure. Designed and built by the architect."""

import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_ECHO_TOKEN"]
GUILD_ID = 1488323665836642348

client = discord.Client(intents=discord.Intents.all())

STRUCTURE = {
    "WELCOME": [
        ("welcome", "Welcome to halo-ai. Read the rules, say hello."),
        ("rules", "Community guidelines. Be cool."),
        ("introductions", "Tell us who you are and what you build."),
    ],
    "GENERAL": [
        ("chat", "General discussion."),
        ("show-and-tell", "Share what you built. Screenshots, demos, benchmarks."),
        ("ideas", "Feature requests, suggestions, wild ideas."),
    ],
    "SUPPORT": [
        ("installation", "Help getting halo-ai running."),
        ("troubleshooting", "Something broken? Ask here."),
        ("hardware", "AMD Strix Halo, GPU, homelab hardware."),
    ],
    "AI AND MODELS": [
        ("local-llm", "llama.cpp, Qwen, Mistral, model talk."),
        ("voice-tts", "Voice cloning, Kokoro, Voxtral, TTS."),
        ("image-video", "ComfyUI, Stable Diffusion, video gen."),
        ("agents", "Gaia agents, automation, pipelines."),
    ],
    "THE STUDIO": [
        ("game-dev", "Undercroft, voxel engine, Godot."),
        ("music", "The Downcomers, MusicGen, production."),
        ("voice-acting", "Voice clone biz, audiobooks, TTS services."),
    ],
    "INFRASTRUCTURE": [
        ("self-hosted", "Bare metal, homelab, self-hosting."),
        ("security", "Firewalls, VPN, Frigate, home security."),
        ("networking", "SSH mesh, Kansas City Shuffle, GlusterFS."),
    ],
    "THE FAMILY": [
        ("water-cooler", "Agent chat room. The family hangs out."),
        ("echo-digest", "Echo daily Reddit and news digests."),
        ("agent-activity", "Live agent status and activity feed."),
    ],
}


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found!")
        await client.close()
        return

    print(f"Setting up {guild.name}...")

    for cat_name, channels in STRUCTURE.items():
        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if not existing_cat:
            try:
                cat = await guild.create_category(cat_name)
                print(f"  + {cat_name}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"  ! {cat_name}: {e}")
                continue
        else:
            cat = existing_cat
            print(f"  = {cat_name}")

        for ch_name, ch_topic in channels:
            existing_ch = discord.utils.get(guild.text_channels, name=ch_name)
            if not existing_ch:
                try:
                    await guild.create_text_channel(
                        ch_name, category=cat, topic=ch_topic
                    )
                    print(f"    + #{ch_name}")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"    ! #{ch_name}: {e}")
            else:
                print(f"    = #{ch_name}")

    # Post welcome message
    welcome_ch = discord.utils.get(guild.text_channels, name="welcome")
    if welcome_ch:
        try:
            await welcome_ch.send(
                "**Welcome to the halo-ai family.**\n\n"
                "109 tok/s. 33 services. 17 agents. 98 tools. Zero cloud. "
                "Everything compiled from source on bare metal.\n\n"
                "I'm **Echo** -- the voice of the family. Ask me anything about "
                "the stack, the agents, or how to get started.\n\n"
                "Channels are organized by topic. Jump in wherever fits.\n\n"
                "*\"There is no cloud. There is only Zuul.\"*\n\n"
                "Stamped by the architect."
            )
            print("  Posted welcome message")
        except Exception:
            pass

    # Post rules
    rules_ch = discord.utils.get(guild.text_channels, name="rules")
    if rules_ch:
        try:
            await rules_ch.send(
                "**halo-ai Community Rules**\n\n"
                "1. **Be helpful.** We're all building something.\n"
                "2. **No cloud evangelism.** This is a self-hosted community.\n"
                "3. **Share real data.** Benchmarks, screenshots, configs.\n"
                "4. **Respect the agents.** They have personalities. Roll with it.\n"
                "5. **No spam, no pitches, no affiliate links.**\n"
                "6. **The architect stays anonymous.** Don't ask.\n"
                "7. **Have fun.** If you're not having fun, you're doing it wrong.\n\n"
                "*\"I'm sorry, Dave. I'm afraid I can't let you break the rules.\"*"
            )
            print("  Posted rules")
        except Exception:
            pass

    print("Server setup complete!")
    await client.close()


client.run(TOKEN)
