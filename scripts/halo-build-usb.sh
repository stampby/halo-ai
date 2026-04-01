#!/bin/bash
# halo-ai — USB Image Builder
# Creates a bootable Arch Linux USB with the full halo-ai stack.
# Plug into any AMD Strix Halo machine, boot, talk.
#
# Usage:
#   sudo ./halo-build-usb.sh /dev/sdX          # Build directly to USB drive
#   sudo ./halo-build-usb.sh --image halo.img   # Build to image file (for later dd)
#
# Requirements:
#   - Arch Linux host with pacstrap, arch-install-scripts
#   - 256GB+ USB SSD (Samsung T7, SanDisk Extreme, etc.)
#   - Internet connection (~25GB downloads)
#   - 2-3 hours (compiling from source)
#
# Designed and built by the architect
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

ok()       { echo -e "  ${GREEN}+${NC} $*"; }
warn()     { echo -e "  ${YELLOW}!${NC} $*"; }
err()      { echo -e "  ${RED}x${NC} $*"; exit 1; }
step()     { echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${BOLD}${BLUE}  $*${NC}"; echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

# ── Parse arguments ──────────────────────────
TARGET=""
IMAGE_MODE=0
IMAGE_FILE=""

if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  sudo $0 /dev/sdX              # Build to USB drive"
    echo "  sudo $0 --image halo-usb.img  # Build to image file"
    exit 1
fi

if [ "$1" = "--image" ]; then
    IMAGE_MODE=1
    IMAGE_FILE="${2:-halo-usb.img}"
    echo -e "${BOLD}Building image: $IMAGE_FILE${NC}"
else
    TARGET="$1"
    if [ ! -b "$TARGET" ]; then
        err "$TARGET is not a block device"
    fi
    echo -e "${BOLD}Target drive: $TARGET${NC}"
fi

# ── Safety check ─────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    err "Must run as root: sudo $0 $*"
fi

if [ -z "$IMAGE_MODE" ] || [ "$IMAGE_MODE" -eq 0 ]; then
    echo -e "${RED}${BOLD}WARNING: This will ERASE ALL DATA on $TARGET${NC}"
    echo -e "${DIM}Press Enter to continue or Ctrl+C to abort...${NC}"
    read -r
fi

MOUNT="/tmp/halo-usb-build"
mkdir -p "$MOUNT"

# ── Create image file if needed ──────────────
if [ "$IMAGE_MODE" -eq 1 ]; then
    step "Creating 240GB image file"
    truncate -s 240G "$IMAGE_FILE"
    LOOP=$(losetup --find --show --partscan "$IMAGE_FILE")
    TARGET="$LOOP"
    ok "Image: $IMAGE_FILE → $TARGET"
fi

# ── Partition ────────────────────────────────
step "Partitioning $TARGET"

parted -s "$TARGET" mklabel gpt
parted -s "$TARGET" mkpart ESP fat32 1MiB 513MiB
parted -s "$TARGET" set 1 esp on
parted -s "$TARGET" mkpart root btrfs 513MiB 100%

sleep 2

# Detect partition names (handles both /dev/sdX1 and /dev/loopXp1)
if [ -b "${TARGET}1" ]; then
    EFI_PART="${TARGET}1"
    ROOT_PART="${TARGET}2"
elif [ -b "${TARGET}p1" ]; then
    EFI_PART="${TARGET}p1"
    ROOT_PART="${TARGET}p2"
else
    err "Cannot find partitions on $TARGET"
fi

ok "EFI: $EFI_PART"
ok "Root: $ROOT_PART"

# ── Format ───────────────────────────────────
step "Formatting partitions"

mkfs.fat -F32 "$EFI_PART"
mkfs.btrfs -f -L halo-usb "$ROOT_PART"

ok "FAT32 EFI + Btrfs root"

# ── Create subvolumes ────────────────────────
step "Creating Btrfs subvolumes"

mount "$ROOT_PART" "$MOUNT"
btrfs subvolume create "$MOUNT/@"
btrfs subvolume create "$MOUNT/@home"
btrfs subvolume create "$MOUNT/@srv"
btrfs subvolume create "$MOUNT/@snapshots"
umount "$MOUNT"

# Remount with subvolumes
mount -o compress=zstd,subvol=@ "$ROOT_PART" "$MOUNT"
mkdir -p "$MOUNT"/{boot/efi,home,srv/ai,.snapshots}
mount "$EFI_PART" "$MOUNT/boot/efi"
mount -o compress=zstd,subvol=@home "$ROOT_PART" "$MOUNT/home"
mount -o compress=zstd,subvol=@srv "$ROOT_PART" "$MOUNT/srv"
mount -o compress=zstd,subvol=@snapshots "$ROOT_PART" "$MOUNT/.snapshots"

ok "Subvolumes: @, @home, @srv, @snapshots"

# ── Bootstrap Arch ───────────────────────────
step "Bootstrapping Arch Linux"

pacstrap -K "$MOUNT" base base-devel linux linux-firmware \
    amd-ucode btrfs-progs grub efibootmgr \
    networkmanager openssh git curl wget \
    python python-pip python-virtualenv \
    cmake ninja rust go nodejs npm \
    pipewire pipewire-pulse wireplumber \
    vulkan-headers vulkan-icd-loader vulkan-radeon \
    mesa libva-mesa-driver \
    snapper snap-pac

ok "Base system installed"

# ── Generate fstab ───────────────────────────
step "Generating fstab"

genfstab -U "$MOUNT" >> "$MOUNT/etc/fstab"
ok "fstab generated"

# ── Configure system ─────────────────────────
step "Configuring system"

# Timezone
arch-chroot "$MOUNT" ln -sf /usr/share/zoneinfo/America/Moncton /etc/localtime
arch-chroot "$MOUNT" hwclock --systohc

# Locale
echo "en_CA.UTF-8 UTF-8" > "$MOUNT/etc/locale.gen"
arch-chroot "$MOUNT" locale-gen
echo "LANG=en_CA.UTF-8" > "$MOUNT/etc/locale.conf"

# Hostname
echo "halo-usb" > "$MOUNT/etc/hostname"

# Hosts
cat > "$MOUNT/etc/hosts" << 'HOSTS'
127.0.0.1   localhost
::1         localhost
127.0.0.1   halo-usb
HOSTS

# User
arch-chroot "$MOUNT" useradd -m -G wheel,video,render -s /bin/bash bcloud
arch-chroot "$MOUNT" bash -c 'echo "bcloud:halo" | chpasswd'
echo "bcloud ALL=(ALL:ALL) NOPASSWD: ALL" > "$MOUNT/etc/sudoers.d/bcloud"
chmod 440 "$MOUNT/etc/sudoers.d/bcloud"

# Autologin on TTY1
mkdir -p "$MOUNT/etc/systemd/system/getty@tty1.service.d"
cat > "$MOUNT/etc/systemd/system/getty@tty1.service.d/autologin.conf" << 'AUTO'
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin bcloud --noclear %I $TERM
AUTO

# Enable services
arch-chroot "$MOUNT" systemctl enable NetworkManager sshd

# GPU kernel parameters
mkdir -p "$MOUNT/etc/cmdline.d"
echo "amd_iommu=off ttm.pages_limit=30146560 zswap.enabled=0" > "$MOUNT/etc/cmdline.d/halo.conf"

ok "System configured — user: bcloud, autologin enabled"

# ── Install GRUB ─────────────────────────────
step "Installing GRUB bootloader"

arch-chroot "$MOUNT" grub-install --target=x86_64-efi \
    --efi-directory=/boot/efi --bootloader-id=halo-ai --removable

# Add kernel parameters to GRUB
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=".*"/GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=off ttm.pages_limit=30146560 zswap.enabled=0"/' \
    "$MOUNT/etc/default/grub"

arch-chroot "$MOUNT" grub-mkconfig -o /boot/grub/grub.cfg

ok "GRUB installed (UEFI, removable)"

# ── Clone halo-ai ────────────────────────────
step "Cloning halo-ai"

arch-chroot "$MOUNT" su - bcloud -c \
    "git clone https://github.com/stampby/halo-ai.git ~/halo-ai"

ok "halo-ai cloned"

# ── Voice autostart service ──────────────────
step "Creating voice autostart"

cat > "$MOUNT/etc/systemd/system/halo-voice-assistant.service" << 'VOICE'
[Unit]
Description=halo-ai Voice Assistant — whisper listens, LLM thinks, Kokoro speaks
After=halo-llama-server.service halo-whisper-server.service halo-lemonade.service
Wants=halo-llama-server.service halo-whisper-server.service halo-lemonade.service

[Service]
Type=simple
User=bcloud
Group=bcloud
ExecStart=/srv/ai/scripts/halo-voice-loop.sh
Restart=on-failure
RestartSec=5
SupplementaryGroups=video render audio

[Install]
WantedBy=multi-user.target
VOICE

# Voice loop script
mkdir -p "$MOUNT/srv/ai/scripts"
cat > "$MOUNT/srv/ai/scripts/halo-voice-loop.sh" << 'VLOOP'
#!/bin/bash
# halo-ai Voice Loop — listen, think, speak, repeat
# Designed and built by the architect
set -euo pipefail

WHISPER_URL="http://127.0.0.1:8082"
LLM_URL="http://127.0.0.1:8081/v1"
KOKORO_URL="http://127.0.0.1:8083"

echo "Voice assistant ready. Listening..."

while true; do
    # Record audio (5 seconds of silence = stop)
    AUDIO_FILE=$(mktemp /tmp/halo-voice-XXXX.wav)
    arecord -f S16_LE -r 16000 -c 1 -d 10 "$AUDIO_FILE" 2>/dev/null || continue

    # Transcribe with whisper
    TEXT=$(curl -s -X POST "$WHISPER_URL/inference" \
        -F "file=@$AUDIO_FILE" \
        -F "response_format=json" | python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))" 2>/dev/null)

    rm -f "$AUDIO_FILE"

    [ -z "$TEXT" ] && continue
    echo "You: $TEXT"

    # Think with LLM
    RESPONSE=$(curl -s "$LLM_URL/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"q\",\"messages\":[{\"role\":\"user\",\"content\":\"$TEXT /no_think\"}],\"max_tokens\":200,\"temperature\":0.7}" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)

    echo "Halo: $RESPONSE"

    # Speak with Kokoro
    curl -s -X POST "$KOKORO_URL/v1/audio/speech" \
        -H "Content-Type: application/json" \
        -d "{\"input\":\"$RESPONSE\",\"voice\":\"af_heart\"}" \
        --output /tmp/halo-speak.wav 2>/dev/null

    aplay /tmp/halo-speak.wav 2>/dev/null || true
done
VLOOP

chmod +x "$MOUNT/srv/ai/scripts/halo-voice-loop.sh"
chown -R 1000:1000 "$MOUNT/srv/ai/scripts"

ok "Voice assistant service created"

# ── Post-install instructions ────────────────
step "Finalizing"

cat > "$MOUNT/home/bcloud/README-USB.txt" << 'README'
halo-ai USB — Portable AI Stack
================================

This USB boots into a full halo-ai stack.

FIRST BOOT:
  1. Boot from this USB (F12/F2 at BIOS)
  2. Login: bcloud / halo (change this!)
  3. Run the installer:
     cd ~/halo-ai && ./install.sh
  4. Reboot

AFTER INSTALL:
  Open lid → autologin → voice assistant starts
  "Hey Halo" → talk → listen → repeat

CHANGE PASSWORD:
  passwd

Designed and built by the architect
README

chown 1000:1000 "$MOUNT/home/bcloud/README-USB.txt"

ok "USB image ready"

# ── Cleanup ──────────────────────────────────
step "Unmounting"

umount -R "$MOUNT"

if [ "$IMAGE_MODE" -eq 1 ]; then
    losetup -d "$LOOP"
    ok "Image saved: $IMAGE_FILE"
    echo ""
    echo -e "${GREEN}${BOLD}Flash to USB:${NC}"
    echo -e "  sudo dd if=$IMAGE_FILE of=/dev/sdX bs=4M status=progress"
    echo ""
else
    ok "USB drive ready — boot from it"
fi

echo ""
echo -e "${GREEN}${BOLD}  ╔═══════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}  ║>>  HALO USB — READY TO BOOT    >>║${NC}"
echo -e "${GREEN}${BOLD}  ╚═══════════════════════════════════╝${NC}"
echo ""
echo -e "  ${DIM}Designed and built by the architect${NC}"
