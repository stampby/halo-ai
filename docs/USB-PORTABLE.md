# halo-ai on a USB — Portable AI in Your Pocket

*"Plug in. Boot up. Start talking."*

Carry your entire AI stack on a USB drive. Plug it into any AMD Strix Halo machine, boot from USB, and you're running 42 services with voice control in under 30 seconds. No install required on the host machine. Nothing touches the host drive.

---

## What You Need

| Item | Spec | Why |
|------|------|-----|
| **USB SSD** | 256GB+, USB 3.2 Gen 2 | Speed matters — cheap thumb drives won't cut it |
| **AMD Strix Halo machine** | Ryzen AI MAX+ 395, 128GB | The hardware that runs the stack |
| **An Arch Linux machine** | To build the image | Your existing halo-ai install works |

### Recommended USB Drives

| Drive | Size | Speed | Price |
|-------|------|-------|-------|
| Samsung T7 | 500GB | 1,050 MB/s | ~$50 |
| SanDisk Extreme | 256GB | 1,050 MB/s | ~$35 |
| Kingston XS2000 | 500GB | 2,000 MB/s | ~$55 |

Do not use a regular USB flash drive. They are too slow for an OS and will wear out quickly.

---

## Build the USB

### Recommended — Build on your PC first, flash to USB after

Build everything to an image file on your local drive. If anything fails halfway through, your USB is untouched — just delete the image and try again. No bricked USB, no wasted time.

```bash
# Step 1 — Build the image on your PC (takes 2-3 hours)
sudo ./scripts/halo-build-usb.sh --image halo-usb.img

# Step 2 — Verify it completed successfully
ls -lh halo-usb.img    # Should be ~45GB+

# Step 3 — Flash to USB (takes ~5 minutes on USB 3.2)
lsblk                  # Find your USB drive — CAREFUL, pick the right one
sudo dd if=halo-usb.img of=/dev/sdX bs=4M status=progress
```

The image file stays on your PC. You can re-flash any time without rebuilding.

### Alternative — Build directly to USB drive

If you want to skip the image step and build straight to USB:

```bash
lsblk                                      # Find your USB drive
sudo ./scripts/halo-build-usb.sh /dev/sdX   # Build directly (erases USB)
```

Warning: if the build fails halfway, the USB may be in a broken state. The image method above is safer.

---

## What Gets Installed

The USB contains a complete Arch Linux system with:

- Full halo-ai stack (42 services)
- Qwen3-30B-A3B model (18GB)
- Whisper speech-to-text
- Kokoro text-to-speech (54 voices)
- FLUX.1 image generation
- All 17 autonomous agents
- Voice assistant autostart
- Btrfs with snapshots
- Autologin (no password screen)

Nothing is installed on the host machine. Everything lives on the USB.

---

## Boot From USB

1. Plug the USB into any Strix Halo machine
2. Press **F12** (or F2/DEL) during boot to open boot menu
3. Select the USB drive (shows as "halo-ai")
4. System boots → autologin → voice assistant starts

### First Boot

On first boot, run the installer to compile everything from source:

```bash
cd ~/halo-ai
./install.sh --dry-run    # Validate first
./install.sh              # Build everything
sudo reboot
```

After reboot, the voice assistant starts automatically. Open the lid, start talking.

---

## Voice Assistant

The USB includes a voice loop service that starts on boot:

1. **Whisper listens** — captures your speech via microphone
2. **LLM thinks** — sends text to Qwen3-30B-A3B locally
3. **Kokoro speaks** — reads the response back to you

No internet required. No cloud. Everything runs on the USB + local GPU.

```
You: "What's the weather forecast?"
Halo: "I don't have internet access right now, 
       but I can help with anything on this machine."

You: "Run a security audit"
Halo: "Running Meek's 17-check audit now..."
```

---

## Security

- Default password is `halo` — **change it immediately**: `passwd`
- SSH is enabled with key-only auth
- All services bound to localhost
- Btrfs snapshots enabled via Snapper
- Same security model as the full install

---

## Troubleshooting

**USB not showing in boot menu**
- Enable USB boot in BIOS/UEFI settings
- Disable Secure Boot (Arch Linux is unsigned)
- Try a different USB port (use USB 3.x ports)

**Slow performance**
- Use a USB SSD, not a flash drive
- Use a USB 3.2 port, not USB 2.0
- Check `lsusb -t` to verify connection speed

**No audio**
- Check PipeWire is running: `systemctl --user status pipewire`
- Verify microphone: `arecord -l`
- Check audio output: `aplay -l`

**Model not loading**
- Verify GPU memory: `cat /sys/class/drm/card*/device/mem_info_gtt_total`
- Check kernel parameter: `cat /proc/cmdline | grep ttm`
- Ensure 123GB GTT is available

---

## Share the USB

Built a working USB? Share it with the community:

1. Create an image: `sudo dd if=/dev/sdX of=halo-usb.img bs=4M status=progress`
2. Compress: `zstd halo-usb.img -o halo-usb.img.zst`
3. Share the `.img.zst` file — anyone can flash it to their own USB

**Do NOT share the image if you've logged into personal accounts or stored credentials on it.** Build a clean image for sharing.

---

*Can't get the install script working? Skip it. Flash the USB. Boot. Done.*

*Designed and built by the architect*
