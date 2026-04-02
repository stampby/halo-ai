#!/usr/bin/env python3
"""
Echo Digest — Scans Reddit + news, posts summary to Discord.
Runs on a schedule via systemd timer.

Designed and built by the architect.
"""

import asyncio
import json
import os
import httpx
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

DATA_DIR = Path(__file__).parent / 'data' / 'reddit'
DIGEST_FILE = DATA_DIR / 'last_digest.json'
DISCORD_TOKEN = os.environ.get('DISCORD_ECHO_TOKEN', '')
LLM_URL = os.environ.get('LLM_BASE_URL', 'http://127.0.0.1:8081/v1')

# Subreddits to watch
WATCH_SUBS = ['LocalLLaMA', 'AMDLaptops', 'selfhosted', 'linuxhardware', 'gamedev', 'godot', 'strixhalo', 'llm', 'AI_Agents', 'Amd', 'localLLM', 'MCPservers', 'AIplayablefiction', 'LovingOpenSourceAI']
FOCUS_SUBS = ['radio', 'podcasting', 'voiceacting', 'audiobooks']

KEYWORDS = [
    'strix halo', 'ryzen ai max', 'halo-ai', 'halo ai', '128gb unified',
    'rocm', 'llama.cpp amd', 'local llm', 'voice clone', 'tts',
    'kokoro', 'xtts', 'voxtral', 'amd igpu', 'gfx1151',
    'self-hosted', 'bare metal', 'homelab ai',
]

USER_AGENT = 'echo-halo-ai/1.0'


async def scan_reddit():
    """Scan all subreddits for relevant posts."""
    results = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for sub in WATCH_SUBS + FOCUS_SUBS:
            try:
                r = await client.get(
                    f'https://www.reddit.com/r/{sub}/new.json?limit=50',
                    headers={'User-Agent': USER_AGENT},
                )
                if r.status_code == 200:
                    posts = r.json().get('data', {}).get('children', [])
                    for post in posts:
                        p = post['data']
                        text = f"{p.get('title','')} {p.get('selftext','')}".lower()
                        for kw in KEYWORDS:
                            if kw in text:
                                results.append({
                                    'sub': sub,
                                    'title': p['title'][:120],
                                    'url': f"https://reddit.com{p['permalink']}",
                                    'score': p.get('score', 0),
                                    'comments': p.get('num_comments', 0),
                                    'keyword': kw,
                                })
                                break
                elif r.status_code == 429:
                    await asyncio.sleep(5)
            except Exception as e:
                print(f'Error scanning r/{sub}: {e}')
    return results


async def summarize_with_llm(posts):
    """Have the LLM summarize the findings as Echo."""
    if not posts:
        return None

    post_text = '\n'.join([
        f"- r/{p['sub']}: [{p['keyword']}] {p['title']} ({p['score']} pts, {p['comments']} comments)"
        for p in posts[:15]
    ])

    prompt = f"""You are Echo, the social media manager for halo-ai. Here are today's relevant Reddit posts:

{post_text}

Write a brief Discord digest message (under 1500 chars) highlighting the most interesting finds. 
Be warm, casual, mention which subreddits are buzzing. If there's anything relevant to our stack 
(AMD Strix Halo, local LLM, voice cloning, self-hosted AI), call it out.
End with Stamped by the architect."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                f'{LLM_URL}/chat/completions',
                json={
                    'model': 'q',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 400,
                    'temperature': 0.7,
                    'chat_template_kwargs': {'enable_thinking': False},
                },
            )
            d = r.json()
            msg = d['choices'][0]['message']
            return (msg.get('content') or msg.get('reasoning_content') or '').strip()
    except Exception as e:
        print(f'LLM error: {e}')
        return None


async def post_to_discord(message, channel_id=None):
    """Post a message to #echo-digest via Discord HTTP API."""
    if not DISCORD_TOKEN:
        print('No Discord token')
        return

    # Use explicit channel from env var, parameter override, or bail
    channel_id = channel_id or os.environ.get('DISCORD_DIGEST_CHANNEL', '')
    if not channel_id:
        print('No DISCORD_DIGEST_CHANNEL set — nowhere to post')
        return

    async with httpx.AsyncClient() as client:
        headers = {
            'Authorization': f'Bot {DISCORD_TOKEN}',
            'Content-Type': 'application/json',
        }

        try:
            r = await client.post(
                f'https://discord.com/api/v10/channels/{channel_id}/messages',
                headers=headers,
                json={'content': message[:2000]},
            )
            if r.status_code in (200, 201):
                print(f'Posted to #echo-digest ({channel_id})')
            elif r.status_code == 403:
                print(f'No access to channel {channel_id} — check bot permissions')
            elif r.status_code == 404:
                print(f'Channel {channel_id} not found — verify DISCORD_DIGEST_CHANNEL')
            else:
                print(f'Discord error: {r.status_code} {r.text}')
        except Exception as e:
            print(f'Failed to post to Discord: {e}')


async def main():
    print(f'Echo Digest — {datetime.now().isoformat()}')
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Scan
    print('Scanning Reddit...')
    posts = await scan_reddit()
    print(f'Found {len(posts)} relevant posts')

    # Save scan
    DIGEST_FILE.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'count': len(posts),
        'posts': posts,
    }, indent=2))

    if not posts:
        print('Nothing to report.')
        return

    # Summarize
    print('Generating digest...')
    summary = await summarize_with_llm(posts)

    if summary:
        print(f'Digest:\n{summary}')
        # Post to Discord
        await post_to_discord(f"**Echo's Daily Digest**\n\n{summary}")
    else:
        # Just post raw findings
        raw = '**Echo\'s Daily Scan**\n\n'
        for p in posts[:10]:
            raw += f"• r/{p['sub']}: {p['title']}\n  {p['url']}\n"
        raw += '\n*Stamped by the architect.*'
        await post_to_discord(raw)

    print('Done.')


if __name__ == '__main__':
    asyncio.run(main())
