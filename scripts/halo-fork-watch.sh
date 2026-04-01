#!/usr/bin/env bash
# halo-ai — Fork watcher
# Checks for new forks, posts to Discord #announcements
# Designed and built by the architect
set -euo pipefail

source /home/bcloud/halo-ai/discord-bots/.env

ANNOUNCEMENTS_CHANNEL="1488378606919876630"
TOKEN="$DISCORD_ECHO_TOKEN"
STATE_FILE="/home/bcloud/halo-ai/discord-bots/data/known_forks.txt"

mkdir -p "$(dirname "$STATE_FILE")"
touch "$STATE_FILE"

# Get current forks from GitHub
forks=$(gh api repos/stampby/halo-ai/forks --jq '.[].owner.login' 2>/dev/null || echo "")

if [ -z "$forks" ]; then
    exit 0
fi

# Check for new forks
while IFS= read -r user; do
    [ -z "$user" ] && continue
    if ! grep -qxF "$user" "$STATE_FILE"; then
        # New fork detected
        echo "$user" >> "$STATE_FILE"

        payload=$(python3 -c "
import json, sys
msg = '\`\`\`\nNew Fork — ' + sys.argv[1] + '\n\nhalo-ai was just forked by ' + sys.argv[1] + '.\nWelcome to the family.\n\nDesigned and built by the architect\n\`\`\`'
print(json.dumps({'content': msg}))
" "$user")

        curl -s -X POST \
            -H "Authorization: Bot $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$payload" \
            "https://discord.com/api/v10/channels/$ANNOUNCEMENTS_CHANNEL/messages" >/dev/null

        echo "New fork: $user — posted to #announcements"
    fi
done <<< "$forks"
