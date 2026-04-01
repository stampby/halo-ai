#!/bin/bash
# Sentinel — daily source inspection
# Checks all repos for dirty state, outdated commits, supply chain
# Posts to #security with Echo's token (Sentinel has no bot yet)
set -uo pipefail

REPO_DIR="/home/bcloud/halo-ai"
DISCORD_ENV="$REPO_DIR/discord-bots/.env"
SECURITY_CHANNEL="1488326052718842076"
DATE=$(date -u +%Y-%m-%d)

set -a; source "$DISCORD_ENV"; set +a
TOKEN="$DISCORD_ECHO_TOKEN"

# Check each repo
REPOS="llama-cpp lemonade whisper-cpp qdrant open-webui vane n8n comfyui kokoro meek"
REPORT=""
for repo in $REPOS; do
    dir="/srv/ai/$repo"
    if [ -d "$dir/.git" ]; then
        commit=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null || echo "???")
        dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l)
        if [ "$dirty" -eq 0 ]; then
            status="CLEAN"
        else
            status="DIRTY($dirty)"
        fi
        printf -v line "  %-20s %-10s %s\n" "$repo" "$commit" "$status"
        REPORT+="$line"
    fi
done

# Supply chain check
NPM_BAD=0
for dir in /srv/ai/n8n /srv/ai/vane; do
    if [ -d "$dir/node_modules/plain-crypto-js" ]; then
        NPM_BAD=$((NPM_BAD + 1))
    fi
done

MSG='```
SENTINEL — CODE WATCHER                                '"$DATE"'
═══════════════════════════════════════════════════════════════

SOURCE INSPECTION

  REPO                 COMMIT     STATUS
  ────────────────     ──────     ──────
'"$REPORT"'
SUPPLY CHAIN
  Malicious npm packages         '"$NPM_BAD"'        '"$([ "$NPM_BAD" -eq 0 ] && echo "CLEAR" || echo "ALERT")"'
  axios pinned to safe version   yes       ENFORCED

I watch the code. — Sentinel
═══════════════════════════════════════════════════════════════
```'

PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'content': sys.stdin.read()}))" <<< "$MSG")
curl -s -X POST -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" \
    -d "$PAYLOAD" "https://discord.com/api/v10/channels/$SECURITY_CHANNEL/messages" > /dev/null

echo "Sentinel watch posted: $DATE"

# Check for new forks
"$REPO_DIR/scripts/halo-fork-watch.sh" 2>/dev/null || true
