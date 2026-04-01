#!/bin/bash
# Bounty — daily bug patrol
# Checks install script, dry-run, community issues
# Posts to #security with Bounty's token
set -uo pipefail

REPO_DIR="/home/bcloud/halo-ai"
DISCORD_ENV="$REPO_DIR/discord-bots/.env"
SECURITY_CHANNEL="1488326052718842076"
DATE=$(date -u +%Y-%m-%d)

set -a; source "$DISCORD_ENV"; set +a
TOKEN="$DISCORD_BOUNTY_TOKEN"

# Run dry-run
DRY_EXIT=0
DRY_OUTPUT=$(bash "$REPO_DIR/install.sh" --dry-run 2>&1)
DRY_EXIT=$?
STEPS=$(echo "$DRY_OUTPUT" | grep -c '/17\]' || echo 0)

# Count open issues
OPEN_ISSUES=$(curl -s "https://api.github.com/repos/stampby/halo-ai/issues?state=open" | python3 -c "import sys,json; print(len([i for i in json.load(sys.stdin) if 'pull_request' not in i]))" 2>/dev/null || echo "?")

# Shellcheck
SC_WARNS=0
if command -v shellcheck >/dev/null; then
    SC_WARNS=$(shellcheck -S warning "$REPO_DIR/install.sh" 2>/dev/null | grep -c "^In " || echo 0)
fi

# Git status
DIRTY=$(git -C "$REPO_DIR" status --porcelain 2>/dev/null | wc -l)

MSG='```
BOUNTY — BUG HUNTER                                    '"$DATE"'
═══════════════════════════════════════════════════════════════

DAILY PATROL

  Dry-run                    '"$STEPS"'/17 steps    '"$([ "$DRY_EXIT" -eq 0 ] && echo "PASS" || echo "FAIL")"'
  Shellcheck warnings        '"$SC_WARNS"'           '"$([ "$SC_WARNS" -eq 0 ] && echo "CLEAN" || echo "REVIEW")"'
  Open GitHub issues         '"$OPEN_ISSUES"'
  Uncommitted changes        '"$DIRTY"'              '"$([ "$DIRTY" -eq 0 ] && echo "CLEAN" || echo "DIRTY")"'

Code in. Fix out. — Bounty
═══════════════════════════════════════════════════════════════
```'

PAYLOAD=$(python3 -c "import json,sys; print(json.dumps({'content': sys.stdin.read()}))" <<< "$MSG")
curl -s -X POST -H "Authorization: Bot $TOKEN" -H "Content-Type: application/json" \
    -d "$PAYLOAD" "https://discord.com/api/v10/channels/$SECURITY_CHANNEL/messages" > /dev/null

echo "Bounty patrol posted: $DATE"
