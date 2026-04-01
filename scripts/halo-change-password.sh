#!/bin/bash
# halo-ai — designed and built by the architect
# halo-change-password.sh — Change the Caddy reverse proxy password
# Part of halo-ai: https://github.com/stampby/halo-ai
set -euo pipefail

CADDYFILE="/srv/ai/configs/Caddyfile"
DEFAULT_HASH='$2a$14$hyBjre0RT3lbdTzAtACFRuhlYeFAx4xsxVsk0IR2RkDy3KVJIi2Nq'

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

# ── Banner ─────────────────────────────────────────
echo ''
echo -e "${CYAN}${BOLD}"
cat << 'BANNER'
         .=============.
        //  .: ✦ :.  \\
       ||               ||
        \\  ': ✦ :'  //
         '============='
             || ||
        ╔════╧══╧════╗
        ║  █▀█  ▀█▀  ║
        ║  █▀█   █   ║
        ║  █ █  ▄█▄  ║
        ╚════════════╝
BANNER
echo -e "${NC}"
echo -e "${BOLD}  Halo AI — Change Caddy Password${NC}"
echo -e "${DIM}  Protects web access to all Halo AI services${NC}"
echo ''

# ── Preflight ──────────────────────────────────────
if [ ! -f "$CADDYFILE" ]; then
    echo -e "${RED}${BOLD}  ERROR:${NC} Caddyfile not found at $CADDYFILE"
    exit 1
fi

if ! command -v caddy >/dev/null 2>&1; then
    echo -e "${RED}${BOLD}  ERROR:${NC} caddy binary not found in PATH"
    exit 1
fi

# Check if still using the default password
if grep -qF "$DEFAULT_HASH" "$CADDYFILE"; then
    echo -e "${RED}${BOLD}  WARNING: Default password is still in use!${NC}"
    echo -e "${RED}  You MUST change it now to secure your server.${NC}"
    echo ''
fi

# ── Prompt for new password ────────────────────────
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  Enter a new Caddy password${NC}"
echo -e "${DIM}  Minimum 8 characters recommended${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ''

while true; do
    read -srp "$(echo -e "${BLUE}[halo-ai]${NC}") New password: " password
    echo ''

    if [ -z "$password" ]; then
        echo -e "  ${YELLOW} !${NC} Password cannot be empty. Try again."
        continue
    fi

    if [ "${#password}" -lt 8 ]; then
        echo -e "  ${YELLOW} !${NC} Password is shorter than 8 characters. Use a stronger password."
        continue
    fi

    read -srp "$(echo -e "${BLUE}[halo-ai]${NC}") Confirm password: " confirm
    echo ''

    if [ "$password" != "$confirm" ]; then
        echo -e "  ${RED} x${NC} Passwords do not match. Try again."
        echo ''
        continue
    fi

    break
done

# ── Generate bcrypt hash ───────────────────────────
echo ''
echo -e "  ${DIM}    ... Generating bcrypt hash${NC}"
NEW_HASH=$(caddy hash-password --plaintext "$password")

if [ -z "$NEW_HASH" ]; then
    echo -e "${RED}${BOLD}  ERROR:${NC} Failed to generate password hash"
    exit 1
fi

# ── Update Caddyfile ───────────────────────────────
echo -e "  ${DIM}    ... Updating Caddyfile${NC}"

# Extract the current hash (the line with "caddy $2a$..." or "caddy $2b$...")
# Replace whatever hash is on the caddy line in the basicauth block
# Escape sed metacharacters in the bcrypt hash (contains $, /, etc.)
ESCAPED_HASH=$(printf '%s\n' "$NEW_HASH" | sed -e 's/[&/\$]/\\&/g')
sed -i "s|        caddy \$2[aby]\$[^[:space:]]*|        caddy ${ESCAPED_HASH}|" "$CADDYFILE"

# Verify the update took effect
if grep -qF "$NEW_HASH" "$CADDYFILE"; then
    echo -e "  ${GREEN} +${NC} Caddyfile updated successfully"
else
    echo -e "${RED}${BOLD}  ERROR:${NC} Failed to update Caddyfile. Please update manually."
    echo -e "  ${DIM}New hash: ${NEW_HASH}${NC}"
    exit 1
fi

# ── Restart Caddy ──────────────────────────────────
echo -e "  ${DIM}    ... Restarting Caddy${NC}"
if sudo systemctl restart halo-caddy.service 2>/dev/null; then
    echo -e "  ${GREEN} +${NC} Caddy restarted"
else
    echo -e "  ${YELLOW} !${NC} Could not restart Caddy via systemd. Try: sudo systemctl restart halo-caddy"
fi

# ── Done ───────────────────────────────────────────
echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  Password changed successfully!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ''
echo -e "  ${DIM}Login:    admin / (your new password)${NC}"
echo -e "  ${DIM}Access:   https://$(hostname)${NC}"
echo ''
