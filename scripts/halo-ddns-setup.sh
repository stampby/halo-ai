#!/bin/bash
# halo-ai — designed and built by the architect
# halo-ai DDNS setup for dynamic IP environments
# Keeps your WireGuard VPN endpoint reachable when your ISP changes your IP
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

# ── Halo AI branded output ────────────────────────
STEP_CURRENT=0
STEP_TOTAL=7

step() {
    STEP_CURRENT=$((STEP_CURRENT + 1))
    echo ''
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  [$STEP_CURRENT/$STEP_TOTAL]${NC} ${BOLD}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

info()  { echo -e "  ${BLUE}>>>${NC} $1"; }
ok()    { echo -e "  ${GREEN} +${NC} $1"; }
warn()  { echo -e "  ${YELLOW} !${NC} $1"; }
fail()  { echo -e "  ${RED} x${NC} $1"; exit 1; }
progress() { echo -e "  ${DIM}    ... $1${NC}"; }

# Helper: prompt with default
prompt() {
    local var_name="$1" prompt_text="$2" default="$3"
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text [${default}]: " input
    printf -v "$var_name" '%s' "${input:-$default}"
}

# ── Banner ─────────────────────────────────────────
clear
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
echo -e "${DIM}  Dynamic DNS Setup${NC}"
echo -e "${DIM}  Keep your VPN endpoint reachable with a dynamic IP${NC}"
echo ''

# ── Preflight ──────────────────────────────────────
step "Preflight checks"
[ "$(id -u)" -eq 0 ] && fail "Do not run as root. Run as your normal user (with sudo access)."
command -v curl >/dev/null || fail "curl is required but not installed."
ok "curl available"

if [ -f /etc/wireguard/wg0.conf ]; then
    ok "WireGuard config found at /etc/wireguard/wg0.conf"
else
    warn "No WireGuard config found. DDNS will be set up, but endpoint update will be skipped."
fi

# ── Choose provider ────────────────────────────────
step "Choose DDNS provider"
echo ''
echo -e "  ${BOLD}Available DDNS providers:${NC}"
echo ''
echo -e "  ${GREEN}1)${NC} ${BOLD}FreeMyIP${NC} ${GREEN}(recommended)${NC} — completely free, no account needed"
echo -e "  ${DIM}2)${NC} DuckDNS — free, needs GitHub/Google login"
echo -e "  ${DIM}3)${NC} No-IP — free tier, needs account"
echo -e "  ${DIM}4)${NC} Dynu — free, needs account"
echo -e "  ${DIM}5)${NC} Afraid.org (FreeDNS) — free, community DNS"
echo ''

prompt PROVIDER_CHOICE "Select provider" "1"

case "$PROVIDER_CHOICE" in
    2)
        step "DuckDNS instructions"
        info "DuckDNS Setup:"
        echo ''
        echo -e "  1. Go to ${BOLD}https://www.duckdns.org${NC} and sign in with GitHub or Google"
        echo -e "  2. Create a subdomain (e.g., myhalo.duckdns.org)"
        echo -e "  3. Copy your token from the DuckDNS dashboard"
        echo -e "  4. Update URL format:"
        echo -e "     ${DIM}https://www.duckdns.org/update?domains=SUBDOMAIN&token=TOKEN&ip=${NC}"
        echo ''
        echo -e "  Create a cron job or systemd timer to hit the update URL every 5 minutes."
        echo -e "  Then update your WireGuard client Endpoint to: ${BOLD}SUBDOMAIN.duckdns.org:51820${NC}"
        echo ''
        info "For automated setup, re-run this script and choose FreeMyIP (option 1)."
        exit 0
        ;;
    3)
        step "No-IP instructions"
        info "No-IP Setup:"
        echo ''
        echo -e "  1. Go to ${BOLD}https://www.noip.com${NC} and create a free account"
        echo -e "  2. Create a hostname (e.g., myhalo.ddns.net)"
        echo -e "  3. Install the No-IP Dynamic Update Client (DUC):"
        echo -e "     ${DIM}yay -S noip-duc${NC}"
        echo -e "  4. Configure: ${DIM}sudo noip-duc --username USER --password PASS -g HOSTNAME${NC}"
        echo ''
        echo -e "  ${YELLOW}Note:${NC} Free tier requires manual confirmation every 30 days."
        echo -e "  Then update your WireGuard client Endpoint to: ${BOLD}HOSTNAME.ddns.net:51820${NC}"
        exit 0
        ;;
    4)
        step "Dynu instructions"
        info "Dynu Setup:"
        echo ''
        echo -e "  1. Go to ${BOLD}https://www.dynu.com${NC} and create a free account"
        echo -e "  2. Add a DDNS hostname from their free domains"
        echo -e "  3. Update URL format:"
        echo -e "     ${DIM}https://api.dynu.com/nic/update?hostname=HOSTNAME&password=MD5HASH${NC}"
        echo ''
        echo -e "  Then update your WireGuard client Endpoint to: ${BOLD}HOSTNAME:51820${NC}"
        exit 0
        ;;
    5)
        step "Afraid.org (FreeDNS) instructions"
        info "Afraid.org Setup:"
        echo ''
        echo -e "  1. Go to ${BOLD}https://freedns.afraid.org${NC} and create an account"
        echo -e "  2. Add a subdomain under one of the public domains"
        echo -e "  3. Go to Dynamic DNS and copy your direct update URL"
        echo -e "  4. Update URL format:"
        echo -e "     ${DIM}https://freedns.afraid.org/dynamic/update.php?TOKEN${NC}"
        echo ''
        echo -e "  Then update your WireGuard client Endpoint to: ${BOLD}SUBDOMAIN.DOMAIN:51820${NC}"
        exit 0
        ;;
    1|"")
        # Continue with FreeMyIP automated setup below
        ;;
    *)
        fail "Invalid choice: $PROVIDER_CHOICE"
        ;;
esac

# ── FreeMyIP configuration ─────────────────────────
step "FreeMyIP configuration"
info "FreeMyIP is completely free and requires no account."
echo ''
echo -e "  ${BOLD}Instructions:${NC}"
echo -e "  1. Go to ${BOLD}https://freemyip.com${NC}"
echo -e "  2. Enter your desired hostname and click ${BOLD}Claim${NC}"
echo -e "  3. Copy the ${BOLD}update token${NC} shown on the page"
echo ''

prompt DDNS_HOSTNAME "Hostname (e.g., myhalo.freemyip.com)" "myhalo.freemyip.com"

# Validate hostname ends with .freemyip.com
if [[ "$DDNS_HOSTNAME" != *.freemyip.com ]]; then
    DDNS_HOSTNAME="${DDNS_HOSTNAME}.freemyip.com"
    warn "Added .freemyip.com suffix: $DDNS_HOSTNAME"
fi

read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") Update token from freemyip.com: " DDNS_TOKEN
[ -z "$DDNS_TOKEN" ] && fail "Token cannot be empty."

ok "Hostname: $DDNS_HOSTNAME"
ok "Token: ${DDNS_TOKEN:0:8}..."

# ── Create update script ──────────────────────────
step "Creating DDNS update script"
SCRIPT_DIR="/srv/ai/scripts"
UPDATE_SCRIPT="$SCRIPT_DIR/halo-ddns-update.sh"

sudo mkdir -p "$SCRIPT_DIR"

sudo tee "$UPDATE_SCRIPT" > /dev/null << UPDATESCRIPT
#!/bin/bash
# halo-ai DDNS updater — FreeMyIP
# Runs via systemd timer every 5 minutes
HOSTNAME="$DDNS_HOSTNAME"
TOKEN="$DDNS_TOKEN"
UPDATE_URL="https://freemyip.com/update?token=\${TOKEN}&domain=\${HOSTNAME}"

RESPONSE=\$(curl -fsSL "\$UPDATE_URL" 2>&1)

if [ \$? -eq 0 ]; then
    echo "\$(date '+%Y-%m-%d %H:%M:%S') DDNS update OK: \$RESPONSE"
else
    echo "\$(date '+%Y-%m-%d %H:%M:%S') DDNS update FAILED: \$RESPONSE" >&2
    exit 1
fi
UPDATESCRIPT

sudo chmod 755 "$UPDATE_SCRIPT"
ok "Created $UPDATE_SCRIPT"

# ── Create systemd service and timer ───────────────
step "Setting up systemd timer"

sudo tee /etc/systemd/system/halo-ddns-update.service > /dev/null << 'SVCEOF'
[Unit]
Description=Halo AI DDNS Update (FreeMyIP)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/srv/ai/scripts/halo-ddns-update.sh
StandardOutput=journal
StandardError=journal
SVCEOF

sudo tee /etc/systemd/system/halo-ddns-update.timer > /dev/null << 'TIMEREOF'
[Unit]
Description=Halo AI DDNS Update Timer — every 5 minutes

[Timer]
OnBootSec=30
OnUnitActiveSec=5min
AccuracySec=30

[Install]
WantedBy=timers.target
TIMEREOF

sudo systemctl daemon-reload
sudo systemctl enable --now halo-ddns-update.timer
ok "Enabled halo-ddns-update.timer (every 5 minutes)"

# ── Update WireGuard client config ─────────────────
step "Updating WireGuard client endpoint"

CLIENT_CONFIGS=( $(find ~/. -maxdepth 1 -name 'halo-vpn-*.conf' 2>/dev/null || true) )

if [ ${#CLIENT_CONFIGS[@]} -gt 0 ]; then
    for conf in "${CLIENT_CONFIGS[@]}"; do
        if grep -q "^Endpoint" "$conf" 2>/dev/null; then
            # Replace the Endpoint IP with the DDNS hostname, preserving the port
            sudo sed -i "s|^Endpoint = .*:|Endpoint = ${DDNS_HOSTNAME}:|" "$conf"
            ok "Updated Endpoint in $(basename "$conf") to ${DDNS_HOSTNAME}"
        fi
    done
elif [ -f ~/halo-vpn-client.conf ]; then
    sudo sed -i "s|^Endpoint = .*:|Endpoint = ${DDNS_HOSTNAME}:|" ~/halo-vpn-client.conf
    ok "Updated Endpoint in halo-vpn-client.conf to ${DDNS_HOSTNAME}"
else
    warn "No WireGuard client configs found in ~/halo-vpn-*.conf"
    info "When you generate a client config, set Endpoint to: ${BOLD}${DDNS_HOSTNAME}:51820${NC}"
fi

# ── Test the update ────────────────────────────────
step "Testing DDNS update"
progress "Running first update..."

if sudo "$UPDATE_SCRIPT"; then
    ok "DDNS update successful"
else
    warn "First update failed — check your token and hostname"
    info "You can test manually: curl \"https://freemyip.com/update?token=${DDNS_TOKEN:0:8}...&domain=${DDNS_HOSTNAME}\""
fi

# ── Done ───────────────────────────────────────────
echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}  DDNS setup complete!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ''
echo -e "  ${BOLD}Hostname:${NC}  $DDNS_HOSTNAME"
echo -e "  ${BOLD}Provider:${NC}  FreeMyIP"
echo -e "  ${BOLD}Update:${NC}    Every 5 minutes via systemd timer"
echo -e "  ${BOLD}Script:${NC}    $UPDATE_SCRIPT"
echo ''
echo -e "  ${DIM}Check timer status:  systemctl status halo-ddns-update.timer${NC}"
echo -e "  ${DIM}Check update logs:   journalctl -u halo-ddns-update.service${NC}"
echo -e "  ${DIM}Run manual update:   sudo $UPDATE_SCRIPT${NC}"
echo ''
echo -e "  ${BOLD}WireGuard client Endpoint should be set to:${NC}"
echo -e "  ${GREEN}${DDNS_HOSTNAME}:51820${NC}"
echo ''
