#!/bin/bash
# halo-ai — designed and built by the architect
# halo-ai WireGuard VPN setup
# Usage: halo-vpn-setup.sh              — initial server + first client setup
#        halo-vpn-setup.sh add-client <name>  — add another client
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

info()     { echo -e "  ${BLUE}>>>${NC} $1"; }
ok()       { echo -e "  ${GREEN} +${NC} $1"; }
warn()     { echo -e "  ${YELLOW} !${NC} $1"; }
fail()     { echo -e "  ${RED} x${NC} $1"; exit 1; }
progress() { echo -e "  ${DIM}    ... $1${NC}"; }

# Helper: prompt with default
prompt() {
    local var_name="$1" prompt_text="$2" default="$3"
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text [${default}]: " input
    printf -v "$var_name" '%s' "${input:-$default}"
}

WG_DIR="/etc/wireguard"
WG_CONF="$WG_DIR/wg0.conf"

# ── Helper: detect server LAN IP ──────────────────
detect_lan_ip() {
    # Prefer the default route interface
    local iface ip
    iface=$(ip -4 route show default 2>/dev/null | awk '{print $5; exit}')
    if [ -n "$iface" ]; then
        ip=$(ip -4 addr show "$iface" 2>/dev/null | awk '/inet /{print $2; exit}' | cut -d/ -f1)
    fi
    if [ -z "$ip" ]; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
    echo "${ip:-<your-server-ip>}"
}

# ── Helper: find next available client IP ─────────
next_client_ip() {
    local subnet_base="$1"  # e.g. 10.100.0
    local last=1
    if [ -f "$WG_CONF" ]; then
        # Find the highest .X used in AllowedIPs
        last=$(grep -oP "${subnet_base//./\\.}\.\K[0-9]+" "$WG_CONF" | sort -n | tail -1)
        [ -z "$last" ] && last=1
    fi
    echo "$((last + 1))"
}

# ── Helper: extract subnet base from CIDR ─────────
subnet_base() {
    echo "$1" | cut -d. -f1-3
}

# ══════════════════════════════════════════════════
#  ADD CLIENT MODE
# ══════════════════════════════════════════════════
add_client() {
    local client_name="$1"

    [ -f "$WG_CONF" ] || fail "WireGuard is not set up yet. Run halo-vpn-setup.sh first."
    [ "$(id -u)" -eq 0 ] || fail "Run with sudo: sudo halo-vpn-setup.sh add-client $client_name"

    echo ''
    echo -e "${CYAN}${BOLD}  Halo AI VPN — Adding client: ${client_name}${NC}"
    echo ''

    # Read existing config to determine subnet
    local server_subnet
    server_subnet=$(grep -oP 'Address\s*=\s*\K[0-9./]+' "$WG_CONF" | head -1)
    local base
    base=$(subnet_base "$server_subnet")

    local server_pubkey
    server_pubkey=$(cat "$WG_DIR/server-public.key")

    local server_endpoint
    server_endpoint=$(detect_lan_ip)

    local next_ip
    next_ip=$(next_client_ip "$base")
    local client_ip="${base}.${next_ip}"

    info "Client IP: $client_ip"

    # Generate client keypair
    local client_privkey client_pubkey
    client_privkey=$(wg genkey)
    client_pubkey=$(echo "$client_privkey" | wg pubkey)

    # Add peer to running interface
    wg set wg0 peer "$client_pubkey" allowed-ips "${client_ip}/32"
    ok "Peer added to running wg0 interface"

    # Append peer to config file for persistence
    cat >> "$WG_CONF" <<EOF

# Client: $client_name
[Peer]
PublicKey = $client_pubkey
AllowedIPs = ${client_ip}/32
EOF
    ok "Peer appended to $WG_CONF"

    # Build client config
    local client_conf_path
    client_conf_path="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)/halo-vpn-${client_name}.conf"

    cat > "$client_conf_path" <<EOF
[Interface]
Address = ${client_ip}/24
PrivateKey = $client_privkey
DNS = 1.1.1.1

[Peer]
PublicKey = $server_pubkey
Endpoint = ${server_endpoint}:51820
AllowedIPs = ${base}.0/24
PersistentKeepalive = 25
EOF

    chmod 600 "$client_conf_path"
    # Set ownership to the real user if running via sudo
    [ -n "${SUDO_USER:-}" ] && chown "$SUDO_USER":"$SUDO_USER" "$client_conf_path"

    ok "Client config saved to $client_conf_path"

    # Show QR code if qrencode is available
    if command -v qrencode >/dev/null 2>&1; then
        echo ''
        info "Scan this QR code with the WireGuard mobile app:"
        echo ''
        qrencode -t ansiutf8 < "$client_conf_path"
    else
        echo ''
        info "Install qrencode for QR codes: sudo pacman -S qrencode"
    fi

    echo ''
    echo -e "${GREEN}${BOLD}  Client '${client_name}' added successfully.${NC}"
    echo ''
    return 0
}

# ── Dispatch: add-client mode ─────────────────────
if [ "${1:-}" = "add-client" ]; then
    [ -n "${2:-}" ] || fail "Usage: halo-vpn-setup.sh add-client <name>"
    add_client "$2"
    exit 0
fi

# ══════════════════════════════════════════════════
#  INITIAL SETUP MODE
# ══════════════════════════════════════════════════

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
echo -e "${DIM}  WireGuard VPN Setup${NC}"
echo -e "${DIM}  github.com/stampby/halo-ai${NC}"
echo ''

# ── Preflight ─────────────────────────────────────
step "Preflight checks"
[ "$(id -u)" -eq 0 ] || fail "This script needs root. Run with: sudo halo-vpn-setup.sh"
command -v pacman >/dev/null || fail "Arch Linux required."

if [ -f "$WG_CONF" ]; then
    warn "WireGuard config already exists at $WG_CONF"
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") Overwrite existing config? [y/N]: " overwrite
    [[ "$overwrite" =~ ^[Yy]$ ]] || fail "Aborted. Use 'halo-vpn-setup.sh add-client <name>' to add clients."
fi
ok "Preflight passed"

# ── Install wireguard-tools ───────────────────────
step "Installing wireguard-tools"
if command -v wg >/dev/null 2>&1; then
    ok "wireguard-tools already installed"
else
    progress "Installing via pacman..."
    pacman -S --noconfirm --needed wireguard-tools
    ok "wireguard-tools installed"
fi

# ── Generate server keypair ───────────────────────
step "Generating server keypair"
mkdir -p "$WG_DIR"
chmod 700 "$WG_DIR"

umask 077
wg genkey | tee "$WG_DIR/server-private.key" | wg pubkey > "$WG_DIR/server-public.key"
chmod 600 "$WG_DIR/server-private.key"

SERVER_PRIVKEY=$(cat "$WG_DIR/server-private.key")
SERVER_PUBKEY=$(cat "$WG_DIR/server-public.key")

ok "Server keypair generated"
info "Public key: $SERVER_PUBKEY"

# ── Configuration prompts ─────────────────────────
step "Configuration"

DETECTED_IP=$(detect_lan_ip)
info "Detected server LAN IP: $DETECTED_IP"
echo ''

prompt VPN_SUBNET "VPN subnet" "10.100.0.0/24"
SUBNET_BASE=$(subnet_base "$VPN_SUBNET")
SERVER_VPN_IP="${SUBNET_BASE}.1"

prompt SERVER_ENDPOINT "Server endpoint (public IP or DDNS)" "$DETECTED_IP"
prompt LISTEN_PORT "WireGuard listen port" "51820"

ok "Server VPN IP: ${SERVER_VPN_IP}/24"
ok "Endpoint: ${SERVER_ENDPOINT}:${LISTEN_PORT}"
ok "Subnet: $VPN_SUBNET"

# ── Create server config ─────────────────────────
step "Creating WireGuard server config"

cat > "$WG_CONF" <<EOF
# Halo AI WireGuard server config
# Generated by halo-vpn-setup.sh

[Interface]
Address = ${SERVER_VPN_IP}/24
ListenPort = $LISTEN_PORT
PrivateKey = $SERVER_PRIVKEY

PostUp = sysctl -w net.ipv4.ip_forward=1
PostDown = sysctl -w net.ipv4.ip_forward=0
EOF

chmod 600 "$WG_CONF"
ok "Server config written to $WG_CONF"

# ── Enable systemd service ────────────────────────
step "Enabling WireGuard service"
systemctl enable --now wg-quick@wg0
ok "wg-quick@wg0 enabled and started"

# Verify
if wg show wg0 >/dev/null 2>&1; then
    ok "WireGuard interface wg0 is up"
else
    warn "Interface may not be fully up yet — check with: sudo wg show"
fi

# ── Generate first client ─────────────────────────
step "Generating first client config"

prompt CLIENT_NAME "First client name" "client1"

CLIENT_PRIVKEY=$(wg genkey)
CLIENT_PUBKEY=$(echo "$CLIENT_PRIVKEY" | wg pubkey)
CLIENT_IP="${SUBNET_BASE}.2"

# Add peer to running interface
wg set wg0 peer "$CLIENT_PUBKEY" allowed-ips "${CLIENT_IP}/32"

# Append peer to server config
cat >> "$WG_CONF" <<EOF

# Client: $CLIENT_NAME
[Peer]
PublicKey = $CLIENT_PUBKEY
AllowedIPs = ${CLIENT_IP}/32
EOF

ok "Peer added to wg0"

# Build client config
CLIENT_CONF_PATH="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)/halo-vpn-${CLIENT_NAME}.conf"

cat > "$CLIENT_CONF_PATH" <<EOF
[Interface]
Address = ${CLIENT_IP}/24
PrivateKey = $CLIENT_PRIVKEY
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBKEY
Endpoint = ${SERVER_ENDPOINT}:${LISTEN_PORT}
AllowedIPs = ${SUBNET_BASE}.0/24
PersistentKeepalive = 25
EOF

chmod 600 "$CLIENT_CONF_PATH"
# Set ownership to the real user if running via sudo
[ -n "${SUDO_USER:-}" ] && chown "$SUDO_USER":"$SUDO_USER" "$CLIENT_CONF_PATH"

ok "Client config saved to $CLIENT_CONF_PATH"

# Show QR code if qrencode is available
if command -v qrencode >/dev/null 2>&1; then
    echo ''
    info "Scan this QR code with the WireGuard mobile app:"
    echo ''
    qrencode -t ansiutf8 < "$CLIENT_CONF_PATH"
else
    echo ''
    info "For QR codes on mobile, install qrencode:"
    echo -e "  ${DIM}sudo pacman -S qrencode${NC}"
    echo -e "  ${DIM}qrencode -t ansiutf8 < $CLIENT_CONF_PATH${NC}"
fi

# ── Done ──────────────────────────────────────────
echo ''
echo ''
echo -e "${GREEN}${BOLD}  WireGuard VPN is ready!${NC}"
echo ''
echo -e "  ${CYAN}Server:${NC}"
echo -e "    VPN IP:     ${SERVER_VPN_IP}"
echo -e "    Endpoint:   ${SERVER_ENDPOINT}:${LISTEN_PORT}"
echo -e "    Public key: ${SERVER_PUBKEY}"
echo ''
echo -e "  ${CYAN}Client (${CLIENT_NAME}):${NC}"
echo -e "    VPN IP:     ${CLIENT_IP}"
echo -e "    Config:     ${CLIENT_CONF_PATH}"
echo ''
echo -e "  ${BOLD}Add more clients:${NC}"
echo -e "    ${DIM}sudo halo-vpn-setup.sh add-client <name>${NC}"
echo ''
echo -e "  ${BOLD}Check status:${NC}"
echo -e "    ${DIM}sudo wg show${NC}"
echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
