#!/bin/bash
# halo-ai nightly backup — run via cron or systemd timer
set -euo pipefail
BACKUP_DIR="${1:-/tmp/halo-backup}"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR/$DATE"

echo "Backing up halo-ai service data..."
# Open WebUI conversations + settings
cp -r /srv/ai/open-webui/data "$BACKUP_DIR/$DATE/open-webui-data" 2>/dev/null || true
# Qdrant vectors
cp -r /srv/ai/qdrant/storage "$BACKUP_DIR/$DATE/qdrant-storage" 2>/dev/null || true
# n8n workflows
cp -r /srv/ai/n8n/data "$BACKUP_DIR/$DATE/n8n-data" 2>/dev/null || true
# Vane research history
cp -r /srv/ai/vane/.next/standalone/data "$BACKUP_DIR/$DATE/vane-data" 2>/dev/null || true
# Agent state
cp -r /srv/ai/agent/data "$BACKUP_DIR/$DATE/agent-data" 2>/dev/null || true
# Configs
cp -r /srv/ai/configs "$BACKUP_DIR/$DATE/configs" 2>/dev/null || true

SIZE=$(du -sh "$BACKUP_DIR/$DATE" | cut -f1)
echo "Backup complete: $BACKUP_DIR/$DATE ($SIZE)"
echo "To sync off-machine: rsync -az $BACKUP_DIR/$DATE user@remote:/backups/"

# Prune backups older than 30 days
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null
