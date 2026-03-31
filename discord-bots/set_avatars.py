#!/usr/bin/env python3
"""Set all bot avatars from SVG-converted PNGs. Designed and built by the architect."""

import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

AVATAR_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

BOTS = {
    "echo": ("DISCORD_ECHO_TOKEN", os.path.join(AVATAR_DIR, "family", "02-echo_00001_.png")),
    "bounty": ("DISCORD_BOUNTY_TOKEN", os.path.join(AVATAR_DIR, "avatars", "png", "halo-ai.png")),
    "meek": ("DISCORD_MEEK_TOKEN", os.path.join(AVATAR_DIR, "family", "03-meek_00001_.png")),
    "amp": ("DISCORD_AMP_TOKEN", os.path.join(AVATAR_DIR, "avatars", "png", "halo-ai.png")),
    "mechanic": ("DISCORD_MECHANIC_TOKEN", os.path.join(AVATAR_DIR, "avatars", "png", "halo-ai.png")),
    "muse": ("DISCORD_MUSE_TOKEN", os.path.join(AVATAR_DIR, "avatars", "png", "echo.png")),  # temp until muse portrait
}


async def set_avatar(name, token_env, avatar_file):
    token = os.environ.get(token_env)
    if not token:
        print(f"  ! {name}: no token")
        return

    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        try:
            with open(avatar_file, "rb") as f:
                await client.user.edit(avatar=f.read())
            print(f"  + {name}: avatar set ({avatar_file})")
        except discord.HTTPException as e:
            if e.code == 40333:
                print(f"  = {name}: rate limited, avatar already set")
            else:
                print(f"  ! {name}: {e}")
        except Exception as e:
            print(f"  ! {name}: {e}")
        await client.close()

    try:
        await client.start(token)
    except Exception as e:
        print(f"  ! {name}: connection failed: {e}")


async def main():
    print("Setting bot avatars...")
    for name, (token_env, avatar_file) in BOTS.items():
        await set_avatar(name, token_env, avatar_file)
        await asyncio.sleep(2)  # rate limit buffer
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
