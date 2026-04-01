#!/bin/bash
# halo-ai USB Build Demo — simulated walkthrough
# Shows every step of building a portable AI USB stick
# Safe to run — nothing is installed, nothing is erased
# Designed and built by the architect
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

MOUNT="/tmp/halo-usb-demo"
mkdir -p "$MOUNT"

ok()   { echo -e "  ${GREEN}+${NC} $*"; }
warn() { echo -e "  ${YELLOW}!${NC} $*"; }
step() { echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${BOLD}${BLUE}  $*${NC}"; echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }
pause() { sleep "${1:-1.5}"; }

clear
echo -e "${CYAN}${BOLD}"
cat << 'BANNER'

  ╔═══════════════════════════════════════════════════╗
  ║                                                   ║
  ║   H A L O · A I   ━━   U S B   B U I L D E R     ║
  ║                                                   ║
  ║   Portable AI Stack — Plug In. Boot Up. Talk.     ║
  ║                                                   ║
  ╚═══════════════════════════════════════════════════╝

BANNER
echo -e "${NC}"
echo -e "${DIM}  Target: Samsung T7 500GB USB SSD (/dev/sda)${NC}"
echo -e "${DIM}  Host: AMD Ryzen AI MAX+ 395 (Strix Halo), 128GB${NC}"
echo -e "${DIM}  Stack: halo-ai — 42 services, 17 agents, zero cloud${NC}"
echo -e "${DIM}  Designed and built by the architect${NC}"
echo ""
pause 3

# ── Step 1 ───────────────────────────────────
step "[1/12] Detecting USB drive"
pause
echo -e "  ${DIM}NAME   MAJ:MIN SIZE TYPE MOUNTPOINT${NC}"
echo -e "  sda      8:0  500G disk"
echo -e "  ├─sda1   8:1  512M part  (EFI)"
echo -e "  └─sda2   8:2  499G part  (root)"
pause
ok "Samsung T7 500GB detected at /dev/sda"
ok "USB 3.2 Gen 2 — 1,050 MB/s"
pause

# ── Step 2 ───────────────────────────────────
step "[2/12] Partitioning drive"
pause
echo -e "  ${DIM}Creating GPT partition table...${NC}"
pause 0.5
echo -e "  ${DIM}Partition 1: ESP (FAT32) — 512MB${NC}"
pause 0.5
echo -e "  ${DIM}Partition 2: Root (Btrfs) — 499GB${NC}"
pause 0.5
mkdir -p "$MOUNT/boot/efi"
ok "GPT + EFI + Btrfs"
pause

# ── Step 3 ───────────────────────────────────
step "[3/12] Creating Btrfs subvolumes"
pause
for sub in @ @home @srv @snapshots; do
    echo -e "  ${DIM}btrfs subvolume create $sub${NC}"
    mkdir -p "$MOUNT/$sub"
    pause 0.3
done
ok "Subvolumes: @, @home, @srv, @snapshots"
ok "Compression: zstd (saves space, faster reads)"
pause

# ── Step 4 ───────────────────────────────────
step "[4/12] Bootstrapping Arch Linux"
pause
echo -e "  ${DIM}pacstrap: base base-devel linux linux-firmware amd-ucode${NC}"
pause 0.5
echo -e "  ${DIM}pacstrap: btrfs-progs grub efibootmgr networkmanager openssh${NC}"
pause 0.5
echo -e "  ${DIM}pacstrap: python cmake ninja rust go nodejs npm${NC}"
pause 0.5
echo -e "  ${DIM}pacstrap: pipewire vulkan-radeon mesa snapper${NC}"
pause 0.5
for dir in etc usr var bin sbin lib lib64 opt proc sys dev run tmp; do
    mkdir -p "$MOUNT/$dir" 2>/dev/null
done
ok "Arch Linux base system installed"
ok "Kernel: linux 6.19.9"
ok "Microcode: amd-ucode"
pause

# ── Step 5 ───────────────────────────────────
step "[5/12] Configuring system"
pause
echo -e "  ${DIM}Timezone: America/Moncton${NC}"
pause 0.3
echo -e "  ${DIM}Locale: en_CA.UTF-8${NC}"
pause 0.3
echo -e "  ${DIM}Hostname: halo-usb${NC}"
pause 0.3
echo -e "  ${DIM}User: bcloud (wheel, video, render)${NC}"
pause 0.3
echo -e "  ${DIM}Autologin: enabled on TTY1${NC}"
pause 0.3
echo -e "  ${DIM}Kernel params: amd_iommu=off ttm.pages_limit=30146560${NC}"
pause 0.3
ok "System configured — autologin, 123GB GPU memory enabled"
pause

# ── Step 6 ───────────────────────────────────
step "[6/12] Installing GRUB bootloader"
pause
echo -e "  ${DIM}grub-install --target=x86_64-efi --removable${NC}"
pause 0.5
echo -e "  ${DIM}Bootloader ID: halo-ai${NC}"
pause 0.5
mkdir -p "$MOUNT/boot/efi/EFI/BOOT"
ok "GRUB installed — boots on any UEFI machine"
pause

# ── Step 7 ───────────────────────────────────
step "[7/12] Cloning halo-ai"
pause
echo -e "  ${DIM}git clone https://github.com/stampby/halo-ai.git${NC}"
pause
mkdir -p "$MOUNT/home/bcloud/halo-ai"
ok "halo-ai repo cloned"
ok "install.sh ready for first boot"
pause

# ── Step 8 ───────────────────────────────────
step "[8/12] Installing AI stack"
pause
echo ""
services=(
    "ROCm 7.13 (GPU runtime)"
    "llama.cpp (LLM inference — Vulkan + HIP)"
    "Lemonade (Unified AI API gateway)"
    "whisper.cpp (Speech-to-text)"
    "Kokoro (Text-to-speech — 54 voices)"
    "Open WebUI (Chat with RAG)"
    "Vane (Deep research)"
    "SearXNG (Private search)"
    "Qdrant (Vector database)"
    "n8n (Workflow automation)"
    "ComfyUI (Image generation)"
    "Caddy (Reverse proxy + TLS)"
    "Meek (Security — 17-check audit)"
)
for svc in "${services[@]}"; do
    echo -e "  ${GREEN}+${NC} $svc"
    pause 0.3
done
echo ""
ok "42 services compiled from source"
pause

# ── Step 9 ───────────────────────────────────
step "[9/12] Downloading AI models"
pause
echo ""
echo -e "  ${DIM}Downloading Qwen3-30B-A3B (18GB)...${NC}"
echo -e "  ${DIM}[████████████████████████████████████████] 100%${NC}"
pause 0.5
echo -e "  ${DIM}Downloading Whisper large-v3-turbo (1.6GB)...${NC}"
echo -e "  ${DIM}[████████████████████████████████████████] 100%${NC}"
pause 0.5
echo -e "  ${DIM}Downloading FLUX.1 schnell (12GB)...${NC}"
echo -e "  ${DIM}[████████████████████████████████████████] 100%${NC}"
pause 0.5
echo ""
ok "Models: LLM (91 tok/s) + STT (5.4x realtime) + Image Gen"
pause

# ── Step 10 ──────────────────────────────────
step "[10/12] Creating voice assistant"
pause
echo -e "  ${DIM}Installing halo-voice-assistant.service${NC}"
pause 0.3
echo -e "  ${DIM}  Whisper listens → LLM thinks → Kokoro speaks${NC}"
pause 0.3
echo -e "  ${DIM}  Starts automatically on boot${NC}"
pause 0.3
echo -e "  ${DIM}  No internet required${NC}"
pause 0.3
ok "Voice loop: listen → think → speak → repeat"
pause

# ── Step 11 ──────────────────────────────────
step "[11/12] Security hardening"
pause
echo -e "  ${DIM}SSH key-only authentication${NC}"
pause 0.2
echo -e "  ${DIM}All services bound to 127.0.0.1${NC}"
pause 0.2
echo -e "  ${DIM}Btrfs snapshots via Snapper${NC}"
pause 0.2
echo -e "  ${DIM}Meek 17-check security audit${NC}"
pause 0.2
echo -e "  ${DIM}Supply chain monitoring (axios mitigated)${NC}"
pause 0.2
echo -e "  ${DIM}Dependabot + CodeQL scanning${NC}"
pause 0.2
ok "Hardened — same security as full install"
pause

# ── Step 12 ──────────────────────────────────
step "[12/12] Finalizing USB"
pause
echo ""
echo -e "  ${DIM}USB Layout:${NC}"
echo -e "  ${DIM}  /boot/efi     — GRUB (UEFI, removable)${NC}"
echo -e "  ${DIM}  /              — Arch Linux (Btrfs, zstd)${NC}"
echo -e "  ${DIM}  /srv/ai        — Full AI stack${NC}"
echo -e "  ${DIM}  /srv/ai/models — LLM + Whisper + FLUX${NC}"
echo -e "  ${DIM}  /home/bcloud   — User + halo-ai repo${NC}"
echo ""

# Disk usage
echo -e "  ${DIM}Disk Usage:${NC}"
echo -e "  ${DIM}  Arch Linux base     ~3 GB${NC}"
echo -e "  ${DIM}  Build tools          ~2 GB${NC}"
echo -e "  ${DIM}  AI stack (compiled)  ~8 GB${NC}"
echo -e "  ${DIM}  Qwen3-30B model     ~18 GB${NC}"
echo -e "  ${DIM}  Whisper turbo        ~1.6 GB${NC}"
echo -e "  ${DIM}  FLUX.1 schnell      ~12 GB${NC}"
echo -e "  ${DIM}  ─────────────────────────${NC}"
echo -e "  ${DIM}  Total               ~45 GB${NC}"
echo -e "  ${DIM}  Free (on 500GB)    ~455 GB${NC}"
echo ""
pause

ok "USB build complete"

# ── Final banner ─────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}"
cat << 'DONE'

  ╔═══════════════════════════════════════════════════╗
  ║                                                   ║
  ║   H A L O · U S B   ━━   R E A D Y               ║
  ║                                                   ║
  ║   91 tok/s · 42 services · 17 agents              ║
  ║   Voice in · Voice out · Zero cloud                ║
  ║                                                   ║
  ║   Plug into any Strix Halo. Boot. Talk.            ║
  ║                                                   ║
  ╚═══════════════════════════════════════════════════╝

DONE
echo -e "${NC}"
echo -e "  ${DIM}Boot sequence:${NC}"
echo -e "  ${DIM}  1. Plug USB into Strix Halo machine${NC}"
echo -e "  ${DIM}  2. Press F12 → select halo-ai${NC}"
echo -e "  ${DIM}  3. Autologin → voice assistant starts${NC}"
echo -e "  ${DIM}  4. Talk to Halo${NC}"
echo ""
echo -e "  ${DIM}Your entire AI stack. In your pocket.${NC}"
echo -e "  ${DIM}Designed and built by the architect${NC}"
echo ""

# Cleanup
rm -rf "$MOUNT"
