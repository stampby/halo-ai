#!/bin/bash
# halo-ai — designed and built by the architect
# halo-ai nightly backup — run via systemd timer or manually
# Usage: halo-backup.sh [/path/to/backup/destination]
# Service: halo-backup.service calls this with /srv/ai/backups
set -euo pipefail

# ── Halo AI branded output ────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

STEP_CURRENT=0
STEP_TOTAL=6

step() {
    STEP_CURRENT=$((STEP_CURRENT + 1))
    local msg="[$STEP_CURRENT/$STEP_TOTAL] $1"
    echo ''
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  ${msg}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "STEP $msg"
}

info()     { echo -e "  ${BLUE}>>>${NC} $1"; }
ok()       { echo -e "  ${GREEN} +${NC} $1"; }
warn()     { echo -e "  ${YELLOW} !${NC} $1"; }
fail()     { echo -e "  ${RED} x${NC} $1"; log "FATAL: $1"; exit 1; }
progress() { echo -e "  ${DIM}    ... $1${NC}"; }

# ── Logging ───────────────────────────────────────
LOG_DIR="/srv/ai/logs"
LOG_FILE="${LOG_DIR}/backup.log"
mkdir -p "$LOG_DIR"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

# ── Configuration ─────────────────────────────────
BACKUP_ROOT="${1:-/srv/ai/backups}"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/${DATE}"
MANIFEST="${BACKUP_DIR}/SHA256SUMS"
KEEP_DAYS=7
ITEMS_BACKED=0
ITEMS_SKIPPED=0

# ── Banner ────────────────────────────────────────
echo ''
echo -e "${CYAN}${BOLD}"
cat << 'BANNER'
    __  __      __           ___    ____
   / / / /___ _/ /___       /   |  /  _/
  / /_/ / __ `/ / __ \     / /| |  / /
 / __  / /_/ / / /_/ /    / ___ |_/ /
/_/ /_/\__,_/_/\____/    /_/  |_/___/
BANNER
echo -e "${NC}"
echo -e "${DIM}  Backup Utility${NC}"
echo -e "${DIM}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ''

log "=========================================="
log "Backup started — destination: ${BACKUP_DIR}"

# ── Helper: back up a path ────────────────────────
# backup_path <source> <label> [glob pattern]
backup_path() {
    local src="$1" label="$2" glob="${3:-}"

    if [ ! -e "$src" ]; then
        warn "${label}: source not found (${src}) — skipped"
        log "SKIP ${label}: ${src} not found"
        ITEMS_SKIPPED=$((ITEMS_SKIPPED + 1))
        return 0
    fi

    local dest="${BACKUP_DIR}/${label}"
    mkdir -p "$(dirname "$dest")"

    if [ -n "$glob" ]; then
        # Copy only matching files from a directory
        mkdir -p "$dest"
        local found=0
        while IFS= read -r -d '' file; do
            cp -a "$file" "$dest/"
            found=$((found + 1))
        done < <(find "$src" -maxdepth 1 -name "$glob" -print0 2>/dev/null)

        if [ "$found" -eq 0 ]; then
            warn "${label}: no files matching '${glob}' in ${src} — skipped"
            log "SKIP ${label}: no ${glob} files in ${src}"
            rmdir "$dest" 2>/dev/null || true
            ITEMS_SKIPPED=$((ITEMS_SKIPPED + 1))
            return 0
        fi
        ok "${label}: ${found} file(s) matching '${glob}'"
    elif [ -d "$src" ]; then
        cp -a "$src" "$dest"
        ok "${label}: directory copied"
    elif [ -f "$src" ]; then
        cp -a "$src" "$dest"
        ok "${label}: file copied"
    fi

    local size
    size=$(du -sh "$dest" 2>/dev/null | cut -f1)
    progress "${size}"
    log "OK ${label}: ${size}"
    ITEMS_BACKED=$((ITEMS_BACKED + 1))
}

# ── Step 1: Prepare ──────────────────────────────
step "Preparing backup directory"
mkdir -p "$BACKUP_DIR"
ok "Backup target: ${BACKUP_DIR}"
info "Retention: last ${KEEP_DAYS} daily backups"

# ── Step 2: Back up configuration ────────────────
step "Backing up configuration files"
backup_path "/srv/ai/configs"                        "configs"
backup_path "/srv/ai/searxng/settings.yml"           "searxng/settings.yml"

# ── Step 3: Back up application data ─────────────
step "Backing up application data"
backup_path "/srv/ai/dashboard-api/data"             "dashboard-api-data"
backup_path "/srv/ai/n8n/data"                       "n8n-data"
backup_path "/srv/ai/n8n/.n8n"                       "n8n-config"

# ── Step 4: Back up databases ────────────────────
step "Backing up databases and vector storage"
backup_path "/srv/ai/open-webui"                     "open-webui-db"        "*.db"
backup_path "/srv/ai/open-webui"                     "open-webui-sqlite"    "*.sqlite"
backup_path "/srv/ai/open-webui/data"                "open-webui-data"
backup_path "/srv/ai/qdrant/storage"                 "qdrant-storage"

# ── Step 5: Back up systemd service files ────────
step "Backing up systemd service files"
SYSTEMD_DEST="${BACKUP_DIR}/systemd-services"
mkdir -p "$SYSTEMD_DEST"
SYSTEMD_COUNT=0
for svc in /etc/systemd/system/halo-*; do
    if [ -e "$svc" ]; then
        cp -a "$svc" "$SYSTEMD_DEST/"
        SYSTEMD_COUNT=$((SYSTEMD_COUNT + 1))
    fi
done
if [ "$SYSTEMD_COUNT" -gt 0 ]; then
    ok "Systemd units: ${SYSTEMD_COUNT} file(s)"
    svc_size=$(du -sh "$SYSTEMD_DEST" 2>/dev/null | cut -f1)
    progress "${svc_size}"
    log "OK systemd-services: ${SYSTEMD_COUNT} files"
    ITEMS_BACKED=$((ITEMS_BACKED + 1))
else
    warn "No halo-* systemd units found in /etc/systemd/system/"
    log "SKIP systemd-services: none found"
    rmdir "$SYSTEMD_DEST" 2>/dev/null || true
    ITEMS_SKIPPED=$((ITEMS_SKIPPED + 1))
fi

# ── Step 6: Manifest & rotation ──────────────────
step "Generating manifest and rotating old backups"

# SHA256 manifest of all backed-up files
info "Generating SHA256 manifest..."
(cd "$BACKUP_DIR" && find . -type f ! -name "SHA256SUMS" -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > SHA256SUMS 2>/dev/null) || true

MANIFEST_LINES=$(wc -l < "$MANIFEST" 2>/dev/null || echo 0)
ok "Manifest: ${MANIFEST_LINES} entries written to SHA256SUMS"
log "Manifest: ${MANIFEST_LINES} file hashes"

# Rotate old backups — keep only the last KEEP_DAYS
info "Rotating backups (keeping last ${KEEP_DAYS})..."
ROTATED=0
while IFS= read -r old_dir; do
    if [ -d "$old_dir" ] && [ "$old_dir" != "$BACKUP_DIR" ]; then
        old_size=$(du -sh "$old_dir" 2>/dev/null | cut -f1)
        rm -rf "$old_dir"
        progress "Removed $(basename "$old_dir") (${old_size})"
        log "ROTATE removed $(basename "$old_dir") (${old_size})"
        ROTATED=$((ROTATED + 1))
    fi
done < <(ls -dt "${BACKUP_ROOT}"/*/ 2>/dev/null | tail -n +$((KEEP_DAYS + 1)))

if [ "$ROTATED" -gt 0 ]; then
    ok "Rotated ${ROTATED} old backup(s)"
else
    ok "No old backups to rotate"
fi

# ── Summary ───────────────────────────────────────
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
REMAINING=$(ls -d "${BACKUP_ROOT}"/*/ 2>/dev/null | wc -l)

echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  Backup Complete${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${BOLD}Location:${NC}    ${BACKUP_DIR}"
echo -e "  ${BOLD}Size:${NC}        ${TOTAL_SIZE}"
echo -e "  ${BOLD}Items OK:${NC}    ${ITEMS_BACKED}"
echo -e "  ${BOLD}Skipped:${NC}     ${ITEMS_SKIPPED}"
echo -e "  ${BOLD}Manifest:${NC}    ${MANIFEST_LINES} hashes"
echo -e "  ${BOLD}On disk:${NC}     ${REMAINING} backup(s) retained"
echo ''
echo -e "  ${DIM}To sync off-machine:${NC}"
echo -e "  ${DIM}rsync -az ${BACKUP_DIR}/ user@remote:/backups/halo-ai/${NC}"
echo ''

log "Backup complete — ${TOTAL_SIZE}, ${ITEMS_BACKED} items, ${ITEMS_SKIPPED} skipped, ${REMAINING} retained"
log "=========================================="
