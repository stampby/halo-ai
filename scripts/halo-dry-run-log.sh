#!/bin/bash
# halo-ai dry-run with full terminal recording
# Posts results to Discord #changelog
# Designed and built by the architect

set -uo pipefail

LOGFILE="/tmp/halo-dry-run-$(date +%Y%m%d-%H%M%S).log"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")

echo "=== halo-ai dry-run — $TIMESTAMP ===" | tee "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# Run the full dry-run, capture everything with timestamps
script -qc "bash /home/bcloud/halo-ai/install.sh --dry-run" -a "$LOGFILE" 2>&1

EXIT_CODE=$?

echo "" >> "$LOGFILE"
echo "=== EXIT CODE: $EXIT_CODE ===" >> "$LOGFILE"
echo "=== COMPLETED: $(date -u +"%Y-%m-%d %H:%M UTC") ===" >> "$LOGFILE"

# Strip ANSI color codes for clean text
CLEAN_LOG="/tmp/halo-dry-run-clean-$(date +%Y%m%d-%H%M%S).txt"
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$LOGFILE" | sed 's/\r//g' > "$CLEAN_LOG"

# Count steps passed
STEPS=$(grep -c '\[.*\/17\]' "$CLEAN_LOG" 2>/dev/null || echo 0)
ERRORS=$(grep -ci 'error\|fail' "$CLEAN_LOG" 2>/dev/null || echo 0)

echo ""
echo "Log saved: $CLEAN_LOG"
echo "Steps: $STEPS | Errors: $ERRORS | Exit: $EXIT_CODE"

# Post summary to Discord #changelog if token available
if [ -f /home/bcloud/halo-ai/discord-bots/.env ]; then
    source /home/bcloud/halo-ai/discord-bots/.env
    CHANGELOG_ID="1488836467039010936"

    if [ "$EXIT_CODE" -eq 0 ]; then
        STATUS="PASS"
    else
        STATUS="FAIL (exit $EXIT_CODE)"
    fi

    MSG='```
DRY-RUN                                                '"$TIMESTAMP"'
═══════════════════════════════════════════════════════════════
Status:  '"$STATUS"'
Steps:   '"$STEPS"'/17
Errors:  '"$ERRORS"'
═══════════════════════════════════════════════════════════════
```'

    # Post one clean code block — no file attachment, no noise
    curl -s -X POST \
        -H "Authorization: Bot $DISCORD_ECHO_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$(python3 -c "import json,sys; print(json.dumps({'content': sys.stdin.read()}))" <<< "$MSG")" \
        "https://discord.com/api/v10/channels/$CHANGELOG_ID/messages" > /dev/null

    echo "Posted to Discord #changelog"
fi

echo "stamped by the architect"
