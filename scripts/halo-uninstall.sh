#!/bin/bash
# halo-ai — designed and built by the architect
# halo-ai uninstall — complete removal of all halo-ai components
# Usage: halo-uninstall.sh [--keep-data]
#   --keep-data   Soft uninstall: removes services/configs but keeps
#                 /srv/ai/backups/ and /srv/ai/models/ (the expensive stuff)
set -euo pipefail

# ── Halo AI branded output ────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

STEP_CURRENT=0
STEP_TOTAL=21
KEEP_DATA=false

for arg in "$@"; do
    case "$arg" in
        --keep-data) KEEP_DATA=true ;;
        --help|-h)
            echo "Usage: halo-uninstall.sh [--keep-data]"
            echo "  --keep-data   Keep /srv/ai/backups and /srv/ai/models"
            exit 0
            ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

step() {
    STEP_CURRENT=$((STEP_CURRENT + 1))
    local msg="[$STEP_CURRENT/$STEP_TOTAL] $1"
    echo ''
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  ${msg}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

info()     { echo -e "  ${BLUE}>>>${NC} $1"; }
ok()       { echo -e "  ${GREEN} +${NC} $1"; }
warn()     { echo -e "  ${YELLOW} !${NC} $1"; }
fail()     { echo -e "  ${RED} x${NC} $1"; exit 1; }
skip()     { echo -e "  ${DIM}    ... $1 (not found, skipping)${NC}"; }
removed()  { echo -e "  ${RED} -${NC} $1"; }

remove_path() {
    local target="$1"
    local label="${2:-$1}"
    if [ -e "$target" ]; then
        rm -rf "$target"
        removed "$label"
    else
        skip "$label"
    fi
}

# ── Root check ───────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    fail "This script must be run as root (sudo)"
fi

# ── Banner ───────────────────────────────────────
echo ''
echo -e "${RED}${BOLD}"
cat << 'BANNER'
    __  __      __           ___    ____
   / / / /___ _/ /___       /   |  /  _/
  / /_/ / __ `/ / __ \     / /| |  / /
 / __  / /_/ / / /_/ /    / ___ |_/ /
/_/ /_/\__,_/_/\____/    /_/  |_/___/
BANNER
echo -e "${NC}"
echo -e "${RED}${BOLD}  ██  UNINSTALLER  ██${NC}"
echo -e "${DIM}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ''

if [ "$KEEP_DATA" = true ]; then
    echo -e "${YELLOW}${BOLD}  MODE: Soft uninstall (--keep-data)${NC}"
    echo -e "${DIM}  Will preserve /srv/ai/backups/ and /srv/ai/models/${NC}"
    STEP_TOTAL=20
else
    echo -e "${RED}${BOLD}  MODE: Full uninstall — EVERYTHING will be removed${NC}"
fi

# ── Step 1: Warning banner ───────────────────────
step "WARNING"

echo ''
echo -e "${RED}${BOLD}  ╔══════════════════════════════════════════════╗${NC}"
echo -e "${RED}${BOLD}  ║                                              ║${NC}"
echo -e "${RED}${BOLD}  ║   This will completely remove halo-ai from   ║${NC}"
echo -e "${RED}${BOLD}  ║   your system. This action is IRREVERSIBLE.  ║${NC}"
echo -e "${RED}${BOLD}  ║                                              ║${NC}"
if [ "$KEEP_DATA" = true ]; then
echo -e "${RED}${BOLD}  ║   Backups and models will be preserved.      ║${NC}"
else
echo -e "${RED}${BOLD}  ║   All data, configs, and services will be    ║${NC}"
echo -e "${RED}${BOLD}  ║   permanently deleted.                       ║${NC}"
fi
echo -e "${RED}${BOLD}  ║                                              ║${NC}"
echo -e "${RED}${BOLD}  ╚══════════════════════════════════════════════╝${NC}"
echo ''

echo -e "  The following will be removed:"
echo -e "    ${RED}-${NC} All halo-* systemd services and timers"
echo -e "    ${RED}-${NC} meek-watch, meek-scan services"
echo -e "    ${RED}-${NC} echo-listen, echo-digest services"
if [ "$KEEP_DATA" = true ]; then
echo -e "    ${RED}-${NC} /srv/ai/ (except backups/ and models/)"
else
echo -e "    ${RED}-${NC} /srv/ai/ (entire directory)"
fi
echo -e "    ${RED}-${NC} /etc/nftables.conf"
echo -e "    ${RED}-${NC} /etc/ssh/sshd_config.d/90-halo-security.conf"
echo -e "    ${RED}-${NC} /etc/udev/rules.d/70-amdgpu.rules"
echo -e "    ${RED}-${NC} /etc/sysctl.d/99-wireguard.conf"
echo -e "    ${RED}-${NC} /etc/wireguard/wg0.conf"
echo -e "    ${RED}-${NC} /etc/fail2ban/jail.local"
echo -e "    ${RED}-${NC} /etc/profile.d/rocm.sh"
echo -e "    ${RED}-${NC} strixhalo entry from /etc/hosts"
echo -e "    ${RED}-${NC} Caddy data directories"
echo ''

# ── Step 2: Confirmation ────────────────────────
step "Confirmation required"

echo ''
echo -e "  ${YELLOW}Type ${BOLD}UNINSTALL${NC}${YELLOW} to confirm (anything else aborts):${NC}"
echo -n "  > "
read -r confirmation

if [ "$confirmation" != "UNINSTALL" ]; then
    echo ''
    echo -e "  ${GREEN}Aborted.${NC} No changes were made."
    exit 0
fi

echo ''
echo -e "  ${RED}Confirmed. Beginning removal...${NC}"

# ── Step 3: Stop all halo-* services ────────────
step "Stopping halo-* services"

HALO_UNITS=$(systemctl list-units --all --no-legend 'halo-*' 2>/dev/null | awk '{print $1}' || true)
if [ -n "$HALO_UNITS" ]; then
    for unit in $HALO_UNITS; do
        systemctl stop "$unit" 2>/dev/null && ok "Stopped $unit" || warn "Could not stop $unit"
    done
else
    skip "No running halo-* units found"
fi

# ── Step 4: Disable all halo-* services/timers ──
step "Disabling halo-* services and timers"

HALO_FILES=$(find /etc/systemd/system/ -maxdepth 1 -name 'halo-*' -printf '%f\n' 2>/dev/null || true)
if [ -n "$HALO_FILES" ]; then
    for unit in $HALO_FILES; do
        systemctl disable "$unit" 2>/dev/null && ok "Disabled $unit" || warn "Could not disable $unit (may already be disabled)"
    done
else
    skip "No halo-* units to disable"
fi

# ── Step 5: Remove halo-* systemd unit files ────
step "Removing halo-* systemd unit files"

HALO_UNIT_FILES=$(find /etc/systemd/system/ -maxdepth 1 -name 'halo-*' 2>/dev/null || true)
if [ -n "$HALO_UNIT_FILES" ]; then
    for f in $HALO_UNIT_FILES; do
        rm -f "$f"
        removed "$f"
    done
else
    skip "No halo-* unit files in /etc/systemd/system/"
fi

# ── Step 6: Remove meek systemd units ───────────
step "Removing meek-* systemd units"

for unit in meek-watch.service meek-watch.timer meek-scan.service meek-scan.timer; do
    target="/etc/systemd/system/$unit"
    if [ -e "$target" ]; then
        systemctl stop "$unit" 2>/dev/null || true
        systemctl disable "$unit" 2>/dev/null || true
        rm -f "$target"
        removed "$unit"
    else
        skip "$unit"
    fi
done

# ── Step 7: Remove echo systemd units ───────────
step "Removing echo-* systemd units"

for unit in echo-listen.service echo-listen.timer echo-digest.service echo-digest.timer; do
    target="/etc/systemd/system/$unit"
    if [ -e "$target" ]; then
        systemctl stop "$unit" 2>/dev/null || true
        systemctl disable "$unit" 2>/dev/null || true
        rm -f "$target"
        removed "$unit"
    else
        skip "$unit"
    fi
done

# ── Step 8: Remove /srv/ai/ ─────────────────────
step "Removing /srv/ai/"

if [ -d "/srv/ai" ]; then
    if [ "$KEEP_DATA" = true ]; then
        info "Soft uninstall: preserving backups/ and models/"

        # Move the keepers to a temp location
        TMPKEEP=$(mktemp -d /tmp/halo-keep.XXXXXX)
        if [ -d "/srv/ai/backups" ]; then
            mv /srv/ai/backups "$TMPKEEP/backups"
            ok "Preserved /srv/ai/backups/ ($(du -sh "$TMPKEEP/backups" 2>/dev/null | cut -f1))"
        fi
        if [ -d "/srv/ai/models" ]; then
            mv /srv/ai/models "$TMPKEEP/models"
            ok "Preserved /srv/ai/models/ ($(du -sh "$TMPKEEP/models" 2>/dev/null | cut -f1))"
        fi

        # Remove everything else
        rm -rf /srv/ai
        removed "/srv/ai/ (except preserved data)"

        # Restore the keepers
        mkdir -p /srv/ai
        [ -d "$TMPKEEP/backups" ] && mv "$TMPKEEP/backups" /srv/ai/backups
        [ -d "$TMPKEEP/models" ] && mv "$TMPKEEP/models" /srv/ai/models
        rm -rf "$TMPKEEP"

        ok "Restored backups/ and models/ to /srv/ai/"
    else
        local_size=$(du -sh /srv/ai 2>/dev/null | cut -f1 || echo "unknown")
        info "Removing /srv/ai/ ($local_size)"
        rm -rf /srv/ai
        removed "/srv/ai/"
    fi
else
    skip "/srv/ai/"
fi

# ── Step 9: Remove /etc/nftables.conf ───────────
step "Removing /etc/nftables.conf"

if [ -f /etc/nftables.conf ]; then
    rm -f /etc/nftables.conf
    removed "/etc/nftables.conf"
    info "You may want to restore your distro default firewall rules"
else
    skip "/etc/nftables.conf"
fi

# ── Step 10: Remove SSH hardening ───────────────
step "Removing /etc/ssh/sshd_config.d/90-halo-security.conf"

remove_path "/etc/ssh/sshd_config.d/90-halo-security.conf" "SSH hardening config"

# ── Step 11: Remove udev rules ──────────────────
step "Removing /etc/udev/rules.d/70-amdgpu.rules"

remove_path "/etc/udev/rules.d/70-amdgpu.rules" "AMDGPU udev rules"

# ── Step 12: Remove sysctl config ───────────────
step "Removing /etc/sysctl.d/99-wireguard.conf"

remove_path "/etc/sysctl.d/99-wireguard.conf" "WireGuard sysctl config"

# ── Step 13: Remove WireGuard config ────────────
step "Removing /etc/wireguard/wg0.conf"

if [ -f /etc/wireguard/wg0.conf ]; then
    # Bring down the interface first
    wg-quick down wg0 2>/dev/null || true
    rm -f /etc/wireguard/wg0.conf
    removed "WireGuard wg0 config (interface brought down)"
else
    skip "/etc/wireguard/wg0.conf"
fi

# ── Step 14: Remove fail2ban config ─────────────
step "Removing /etc/fail2ban/jail.local"

remove_path "/etc/fail2ban/jail.local" "fail2ban jail.local"

# ── Step 15: Remove ROCm profile ────────────────
step "Removing /etc/profile.d/rocm.sh"

remove_path "/etc/profile.d/rocm.sh" "ROCm profile script"

# ── Step 16: Remove strixhalo from /etc/hosts ───
step "Cleaning strixhalo from /etc/hosts"

if grep -q 'strixhalo' /etc/hosts 2>/dev/null; then
    sed -i '/strixhalo/d' /etc/hosts
    removed "strixhalo entries from /etc/hosts"
else
    skip "strixhalo in /etc/hosts"
fi

# ── Step 17: Remove Caddy data ──────────────────
step "Removing Caddy data directories"

remove_path "/root/.local/share/caddy" "Caddy data (/root/.local/share/caddy/)"
remove_path "/srv/ai/.caddy" "Caddy data (/srv/ai/.caddy/)"

# ── Step 18: Optionally remove ROCm ─────────────
step "Optional: ROCm (/opt/rocm)"

if [ -d "/opt/rocm" ]; then
    rocm_size=$(du -sh /opt/rocm 2>/dev/null | cut -f1 || echo "unknown")
    echo -e "  ${YELLOW}ROCm is installed at /opt/rocm ($rocm_size)${NC}"
    echo -e "  ${YELLOW}Remove it? This affects ALL GPU compute on the system.${NC}"
    echo -n "  Type YES to remove, anything else to keep: "
    read -r rocm_confirm
    if [ "$rocm_confirm" = "YES" ]; then
        rm -rf /opt/rocm
        removed "ROCm ($rocm_size)"
    else
        ok "Kept /opt/rocm"
    fi
else
    skip "/opt/rocm"
fi

# ── Step 19: Optionally remove compiled Python ──
step "Optional: Compiled Python (/opt/python312, /opt/python313)"

for pydir in /opt/python312 /opt/python313; do
    if [ -d "$pydir" ]; then
        py_size=$(du -sh "$pydir" 2>/dev/null | cut -f1 || echo "unknown")
        echo -e "  ${YELLOW}Found $pydir ($py_size)${NC}"
        echo -n "  Type YES to remove, anything else to keep: "
        read -r py_confirm
        if [ "$py_confirm" = "YES" ]; then
            rm -rf "$pydir"
            removed "$pydir"
        else
            ok "Kept $pydir"
        fi
    else
        skip "$pydir"
    fi
done

# ── Step 20: Optionally remove compiled Node.js ─
step "Optional: Compiled Node.js"

NODE_PATH=$(command -v node 2>/dev/null || true)
if [ -n "$NODE_PATH" ]; then
    NODE_PREFIX=$(dirname "$(dirname "$NODE_PATH")")
    echo -e "  ${YELLOW}Node.js found at: $NODE_PATH${NC}"
    echo -e "  ${RED}${BOLD}  WARNING: This is a system-wide removal!${NC}"
    echo -e "  ${RED}  This will affect ALL applications using Node.js.${NC}"
    echo -e "  ${YELLOW}  Prefix: $NODE_PREFIX${NC}"
    echo -n "  Type YES-NODE to remove (extra confirmation required): "
    read -r node_confirm
    if [ "$node_confirm" = "YES-NODE" ]; then
        if [ "$NODE_PREFIX" = "/usr/local" ] || [ "$NODE_PREFIX" = "/opt/node" ]; then
            rm -f "$NODE_PREFIX"/bin/node "$NODE_PREFIX"/bin/npm "$NODE_PREFIX"/bin/npx
            rm -rf "$NODE_PREFIX"/lib/node_modules
            removed "Node.js from $NODE_PREFIX"
        else
            warn "Node.js is installed via package manager ($NODE_PREFIX). Use your package manager to remove it."
        fi
    else
        ok "Kept Node.js"
    fi
else
    skip "Node.js (not found in PATH)"
fi

# ── Step 21: Optionally remove Rust toolchain ───
step "Optional: Rust toolchain (~/.cargo, ~/.rustup)"

REAL_HOME="${SUDO_USER:+$(getent passwd "$SUDO_USER" | cut -d: -f6)}"
REAL_HOME="${REAL_HOME:-$HOME}"

RUST_FOUND=false
for cargo_dir in "$REAL_HOME/.cargo" /root/.cargo; do
    if [ -d "$cargo_dir" ]; then
        RUST_FOUND=true
        break
    fi
done

if [ "$RUST_FOUND" = true ]; then
    echo -e "  ${YELLOW}Rust toolchain found${NC}"
    echo -n "  Type YES to remove ~/.cargo and ~/.rustup, anything else to keep: "
    read -r rust_confirm
    if [ "$rust_confirm" = "YES" ]; then
        for home_dir in "$REAL_HOME" /root; do
            remove_path "$home_dir/.cargo" "$home_dir/.cargo"
            remove_path "$home_dir/.rustup" "$home_dir/.rustup"
        done
    else
        ok "Kept Rust toolchain"
    fi
else
    skip "Rust toolchain"
fi

# ── Reload systemd ──────────────────────────────
echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${CYAN}  Reloading systemd daemon${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

systemctl daemon-reload
ok "systemd daemon reloaded"

# ── Completion message ───────────────────────────
echo ''
echo ''
echo -e "${GREEN}${BOLD}"
cat << 'DONE'
    ╔══════════════════════════════════════════════╗
    ║                                              ║
    ║       halo-ai has been uninstalled.          ║
    ║                                              ║
    ╚══════════════════════════════════════════════╝
DONE
echo -e "${NC}"

if [ "$KEEP_DATA" = true ]; then
    echo -e "  ${YELLOW}Preserved data:${NC}"
    [ -d "/srv/ai/backups" ] && echo -e "    ${GREEN}+${NC} /srv/ai/backups/"
    [ -d "/srv/ai/models" ]  && echo -e "    ${GREEN}+${NC} /srv/ai/models/"
    echo ''
fi

echo -e "  ${DIM}You may also want to:${NC}"
echo -e "    ${DIM}- Remove halo-ai git repo if cloned locally${NC}"
echo -e "    ${DIM}- Restart sshd if SSH config was removed${NC}"
echo -e "    ${DIM}- Restore /etc/nftables.conf from your distro defaults${NC}"
echo -e "    ${DIM}- Reboot to ensure all changes take effect${NC}"
echo ''
