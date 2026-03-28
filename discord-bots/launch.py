# halo-ai — designed and built by the architect
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

    if not bots:
        print("No bot tokens found. Set DISCORD_*_TOKEN in .env")
        print("See .env.example for required variables.")
        sys.exit(1)

    print(f"Launching {len(bots)} agents: {', '.join(n for n, _ in bots)}")

    tasks = []
    for name, bot in bots:
        tasks.append(asyncio.create_task(bot.start(bot.token)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
