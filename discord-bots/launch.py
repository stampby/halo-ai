# halo-ai — stamped by the architect
"""Launch all Discord bots in parallel."""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
)

from echo_bot import EchoBot
from bounty_bot import BountyBot
from meek_bot import MeekBot
from amp_bot import AmpBot
from mechanic_bot import MechanicBot
from muse_bot import MuseBot


async def main():
    bots = []

    if os.environ.get("DISCORD_ECHO_TOKEN"):
        bots.append(("echo", EchoBot(token_env="DISCORD_ECHO_TOKEN")))
    if os.environ.get("DISCORD_BOUNTY_TOKEN"):
        bots.append(("bounty", BountyBot(token_env="DISCORD_BOUNTY_TOKEN")))
    if os.environ.get("DISCORD_MEEK_TOKEN"):
        bots.append(("meek", MeekBot(token_env="DISCORD_MEEK_TOKEN")))
    if os.environ.get("DISCORD_AMP_TOKEN"):
        bots.append(("amp", AmpBot(token_env="DISCORD_AMP_TOKEN")))
    if os.environ.get("DISCORD_MECHANIC_TOKEN"):
        bots.append(("mechanic", MechanicBot(token_env="DISCORD_MECHANIC_TOKEN")))
    if os.environ.get("DISCORD_MUSE_TOKEN"):
        bots.append(("muse", MuseBot(token_env="DISCORD_MUSE_TOKEN")))

    if not bots:
        print("No bot tokens found. Set DISCORD_*_TOKEN in .env")
        print("See .env.example for required variables.")
        sys.exit(1)

    # Register all bots so they know about each other (collision avoidance)
    from bot_base import HaloBot
    for name, bot in bots:
        HaloBot.register(bot)

    print(f"Launching {len(bots)} agents: {', '.join(n for n, _ in bots)}")
    print("Collision avoidance: Echo yields to specialists on their topics")

    tasks = []
    for name, bot in bots:
        tasks.append(asyncio.create_task(_run_bot(name, bot)))

    await asyncio.gather(*tasks)


async def _run_bot(name, bot):
    try:
        await bot.start(bot.token)
    except Exception as e:
        logging.getLogger("launch").error(f"Bot '{name}' failed to start: {e}")


if __name__ == "__main__":
    asyncio.run(main())
