# Halo AI Troubleshooting Guide

This guide covers common issues with the halo-ai bare-metal AI stack for AMD Strix Halo and how to resolve them.

---

## Table of Contents

- [Service Won't Start](#service-wont-start)
- [GPU Not Detected](#gpu-not-detected)
- [Caddy / Web Access Issues](#caddy--web-access-issues)
- [LLM Not Responding](#llm-not-responding)
- [Network Issues](#network-issues)
- [Backup Issues](#backup-issues)
- [Common Commands Reference](#common-commands-reference)

---

## Service Won't Start

### Check service status and logs

Every halo-ai service is managed by systemd with a `halo-` prefix. Start troubleshooting by checking the service status and its journal output:

```bash
# Check status (shows recent errors inline)
sudo systemctl status halo-llama-server

# Stream live logs
journalctl -u halo-llama-server -f

# Show last 100 lines of logs
journalctl -u halo-llama-server -n 100

# Show logs since last boot
journalctl -u halo-llama-server -b
```

Replace `halo-llama-server` with any service name:

| Service | Unit name |
|---------|-----------|
| llama.cpp | `halo-llama-server` |
| Lemonade | `halo-lemonade` |
| Open WebUI | `halo-open-webui` |
| Vane | `halo-vane` |
| SearXNG | `halo-searxng` |
| Qdrant | `halo-qdrant` |
| n8n | `halo-n8n` |
| Whisper | `halo-whisper-server` |
| ComfyUI | `halo-comfyui` |
| Dashboard API | `halo-dashboard-api` |
| Dashboard UI | `halo-dashboard-ui` |
| Caddy | `halo-caddy` |
| Agent | `halo-agent` |
| Watchdog | `halo-watchdog` |

### Common systemd errors and fixes

**"Failed to start — Unit not found"**

The service unit file is missing from `/etc/systemd/system/`. Reinstall from the repo:

```bash
sudo cp /srv/ai/systemd/halo-*.service /srv/ai/systemd/halo-*.timer /etc/systemd/system/
sudo systemctl daemon-reload
```

**"code=exited, status=217/USER"**

The `User=` or `Group=` in the service file contains `<YOUR_USER>` instead of your actual username. Fix it:

```bash
# Replace <YOUR_USER> with your actual username in all service files
sudo sed -i "s/<YOUR_USER>/$(whoami)/g" /etc/systemd/system/halo-*.service
sudo systemctl daemon-reload
```

**"code=exited, status=203/EXEC"**

The `ExecStart=` binary does not exist. The service was not built correctly. Check that the binary path exists:

```bash
# Example: verify llama-server binary exists
ls -la /srv/ai/llama-cpp/build-vulkan/bin/llama-server
```

If missing, rebuild the service. See `/srv/ai/scripts/build-llama-cpp.sh` or `build-all.sh`.

**"code=exited, status=200/CHDIR"**

The `WorkingDirectory=` in the service file does not exist. Create it or check that the application was cloned/installed properly.

**Service keeps restarting (crash loop)**

All halo-ai services use `Restart=on-failure` with `RestartSec=5`. If a service is crash-looping:

```bash
# See the full failure reason
journalctl -u halo-<service> -n 50 --no-pager

# Temporarily stop and debug manually
sudo systemctl stop halo-<service>

# Run the ExecStart command manually to see direct output
# (copy the ExecStart line from the service file)
```

### Permission issues

**File ownership**

All files under `/srv/ai/` should be owned by your user:

```bash
# Check ownership
ls -la /srv/ai/

# Fix ownership recursively
sudo chown -R $(whoami):$(whoami) /srv/ai
```

**GPU access denied**

Services that use the GPU (llama-server, lemonade, whisper, comfyui) need the `video` and `render` groups. The service files include `SupplementaryGroups=video render`, but your user also needs to be in these groups:

```bash
# Check your groups
groups

# Add yourself to GPU groups if missing
sudo usermod -aG video,render $(whoami)

# You must log out and back in (or reboot) for group changes to take effect
```

**Caddy cannot bind to port 443**

The `halo-caddy.service` uses `AmbientCapabilities=CAP_NET_BIND_SERVICE` to allow binding to privileged ports without root. If Caddy still fails:

```bash
# Check if something else is using port 443
sudo ss -tlnp | grep :443

# Verify Caddy has the capability
sudo systemctl cat halo-caddy | grep AmbientCapabilities
```

### Port conflicts

If a service fails because the port is already in use:

```bash
# Find what is using a specific port
sudo ss -tlnp | grep :<PORT>

# Common ports:
# 3000  Open WebUI
# 3001  Vane
# 3003  Dashboard
# 5678  n8n
# 6333  Qdrant
# 8080  Lemonade
# 8081  llama.cpp
# 8082  Whisper
# 8083  Kokoro
# 8188  ComfyUI
# 8888  SearXNG
# 443   Caddy

# Kill the conflicting process
sudo kill $(sudo ss -tlnp | grep :<PORT> | awk '{print $NF}' | grep -oP '\d+')
```

---

## GPU Not Detected

### ROCm verification

Verify that ROCm is installed and can see the GPU:

```bash
# Check ROCm can detect the GPU
rocminfo

# Look specifically for gfx1151
rocminfo | grep gfx1151

# Check OpenCL detection
clinfo

# Check the ROCm environment is loaded
echo $ROCM_HOME    # Should be /opt/rocm
echo $PATH         # Should include /opt/rocm/bin
```

If `rocminfo` is not found, the ROCm environment is not loaded:

```bash
source /etc/profile.d/rocm.sh
```

If `/etc/profile.d/rocm.sh` does not exist, ROCm was not installed. Check that `/opt/rocm` exists and is a symlink to `/srv/ai/rocm/install`:

```bash
ls -la /opt/rocm
```

### GPU memory not showing 115GB

The AMD Strix Halo has 128GB unified memory, but the GPU needs the kernel parameter `ttm.pages_limit=30146560` to expose the full 115GB GTT (Graphics Translation Table) region.

**Check current kernel parameters:**

```bash
cat /proc/cmdline | tr ' ' '\n' | grep ttm
```

If `ttm.pages_limit=30146560` is missing, add it to your boot entry:

```bash
# Find your boot entry
ls /boot/loader/entries/

# Edit the entry (replace with your actual filename)
sudo nano /boot/loader/entries/<your-entry>.conf

# Add to the 'options' line:
#   ttm.pages_limit=30146560

# The full options line should look like:
#   options amd_iommu=off ttm.pages_limit=30146560 root=/dev/ArchinstallVg/root zswap.enabled=0 rootflags=subvol=@ rw rootfstype=btrfs
```

Reboot after making changes. Verify after reboot:

```bash
# Check available GPU memory
rocm-smi --showmeminfo vram

# Or check via sysfs
cat /sys/class/drm/card*/device/mem_info_gtt_total
```

### gfx1151 not recognized

The Strix Halo uses GPU architecture `gfx1151`, which requires **ROCm 7.13 or newer** (specifically the TheRock nightly builds). Older ROCm versions do not include gfx1151 support.

**Check your ROCm version:**

```bash
cat /opt/rocm/.info/version
# or
rocminfo | head -20
```

If the version is too old, re-download the nightly build:

```bash
cd /srv/ai/rocm
wget -q --show-progress 'https://rocm.nightlies.amd.com/tarball/therock-dist-linux-gfx1151-7.13.0a20260323.tar.gz' -O therock.tar.gz
mkdir -p install && tar -xf therock.tar.gz -C install
sudo ln -sfn /srv/ai/rocm/install /opt/rocm
```

**HSA_OVERRIDE_GFX_VERSION**

The environment variable `HSA_OVERRIDE_GFX_VERSION=11.5.1` is set in `/srv/ai/configs/rocm.env` and loaded by GPU services. If you are running GPU commands manually, source this file first:

```bash
source /srv/ai/configs/rocm.env
```

### Device permissions (/dev/kfd, /dev/renderD128)

ROCm requires access to `/dev/kfd` (kernel fusion driver) and `/dev/dri/renderD128` (render node).

**Check device permissions:**

```bash
ls -la /dev/kfd /dev/dri/renderD128
```

Expected output shows group `render` with mode `0660`:

```
crw-rw---- 1 root render ... /dev/kfd
crw-rw---- 1 root render ... /dev/dri/renderD128
```

**If permissions are wrong**, the udev rules may not be installed:

```bash
# Check the rules file
cat /etc/udev/rules.d/70-amdgpu.rules

# Should contain:
# SUBSYSTEM=="kfd", KERNEL=="kfd", TAG+="uaccess", GROUP="render", MODE="0660"
# SUBSYSTEM=="drm", KERNEL=="renderD*", TAG+="uaccess", GROUP="render", MODE="0660"

# If missing, install from repo
sudo cp /srv/ai/configs/system/70-amdgpu.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**If your user cannot access these devices:**

```bash
# Verify your user is in the render and video groups
groups $(whoami)

# If not, add and re-login
sudo usermod -aG video,render $(whoami)
```

---

## Caddy / Web Access Issues

### Cannot reach https://strixhalo

**1. Check that Caddy is running:**

```bash
sudo systemctl status halo-caddy
```

**2. Check DNS resolution:**

From the client machine (not the server), verify that `strixhalo` resolves to the correct IP:

```bash
ping strixhalo
# or
nslookup strixhalo
```

If it does not resolve, you need to add a DNS entry. See the [README](../README.md#accessing-your-halo-ai-server) for detailed instructions (router DNS, hosts file, or Pi-hole/AdGuard).

Quick fix using hosts file:

```bash
# On the client machine (replace with your server's IP)
sudo sh -c 'echo "xxx.xxx.xxx.xxx    strixhalo" >> /etc/hosts'
```

**3. Check the firewall:**

The nftables firewall only allows ports 22 (SSH) and 443 (Caddy) from your configured LAN subnet. If your LAN uses a different subnet (e.g., `192.168.1.0/24`), you need to update the firewall rules:

```bash
# Check current rules
sudo nft list ruleset

# Edit the config
sudo nano /srv/ai/configs/system/nftables.conf
# Change xxx.xxx.xxx.0/24 to your subnet

# Reload
sudo nft -f /srv/ai/configs/system/nftables.conf
```

**4. Test from the server itself:**

```bash
curl -k https://127.0.0.1
```

If this works but remote access does not, the issue is firewall or DNS related.

### Browser certificate warnings

Caddy generates a self-signed TLS certificate. Browsers will show a warning until you install the root CA certificate on your client devices.

**Export the certificate from the server:**

```bash
sudo cp $(find /var/lib/caddy/.local/share/caddy/pki/authorities/local -name "root.crt" 2>/dev/null) ~/halo-ai-ca.crt
chmod 644 ~/halo-ai-ca.crt
```

**Copy to your client:**

```bash
scp <YOUR_USER>@strixhalo:~/halo-ai-ca.crt .
```

**Install on your client** -- see the [README](../README.md#https-certificate-setup) for platform-specific instructions (Linux, macOS, Windows, Android, iOS).

Quick reference for Linux:

```bash
# Arch / Manjaro
sudo trust anchor --store halo-ai-ca.crt

# Ubuntu / Debian
sudo cp halo-ai-ca.crt /usr/local/share/ca-certificates/halo-ai-ca.crt
sudo update-ca-certificates
```

### "403 Forbidden" or authentication failures

Caddy uses HTTP Basic Auth. The default username is `admin` and the default password is `Caddy`.

**Check the Caddyfile:**

```bash
cat /srv/ai/configs/Caddyfile
```

Look at the `basicauth` block. The password hash should be a bcrypt string starting with `$2a$14$`. If you see the placeholder text `admin a`, the password hash was not written during install.

**Verify your password works:**

```bash
# Test authentication
curl -k -u admin:YourPassword https://127.0.0.1
```

### How to reset the Caddy password

```bash
# Generate a new bcrypt hash
caddy hash-password --plaintext 'YourNewPassword'

# Edit the Caddyfile and replace the hash after "admin"
nano /srv/ai/configs/Caddyfile

# The basicauth block should look like:
#     basicauth * {
#         admin $2a$14$<new-hash-here>
#     }

# Reload Caddy without downtime
sudo systemctl reload halo-caddy
```

### How to change from the default password "Caddy"

This should be done immediately after install:

```bash
# Generate hash for your new password
NEW_HASH=$(caddy hash-password --plaintext 'MySecurePassword')

# Replace the hash in the Caddyfile
sed -i "s|admin \$2a\$14\$.*|admin ${NEW_HASH}|" /srv/ai/configs/Caddyfile

# Reload Caddy
sudo systemctl reload halo-caddy
```

---

## LLM Not Responding

### llama-server health check

```bash
# Check if llama-server is running and healthy
curl -s http://127.0.0.1:8081/health | python3 -m json.tool

# Expected response:
# {"status": "ok"}

# Check Lemonade gateway (routes to llama-server)
curl -s http://127.0.0.1:8080/v1/models | python3 -m json.tool
```

If the health check returns no response, check if the service is running:

```bash
sudo systemctl status halo-llama-server
journalctl -u halo-llama-server -n 50 --no-pager
```

### Model not loaded

**Check that the model file exists:**

```bash
# The default model path from the service file
ls -lh /srv/ai/models/qwen3-30b-a3b-q4_k_m.gguf
```

If the model file is missing, download it:

```bash
/srv/ai/scripts/halo-models.sh list
/srv/ai/scripts/halo-models.sh download qwen3-30b-a3b
```

**Check that the model path in the service file matches an actual file:**

```bash
grep -- '--model' /etc/systemd/system/halo-llama-server.service
```

If you changed models, update the service file and reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart halo-llama-server
```

### Slow inference

Expected performance on Strix Halo:

| Model | Expected Speed |
|-------|---------------|
| Qwen3-30B-A3B (MoE, Q4_K_M) | ~90 tok/s |
| Llama 3 70B | ~18 tok/s |
| Llama 3 70B Q8 | ~10 tok/s |

**Check GPU utilization:**

```bash
# Real-time GPU monitoring
rocm-smi

# Watch continuously
watch -n 1 rocm-smi

# Check GPU memory usage
rocm-smi --showmeminfo vram
```

**Common causes of slow inference:**

1. **CPU fallback** -- If the GPU is not detected, llama.cpp will fall back to CPU inference, which is dramatically slower. Check logs for "offloaded 0 layers" or similar warnings:
   ```bash
   journalctl -u halo-llama-server | grep -i "offload\|layer\|gpu\|hip"
   ```

2. **Wrong backend** -- The service file uses `build-vulkan` by default. For HIP/ROCm (often faster):
   ```bash
   /srv/ai/scripts/halo-driver-swap.sh hip
   sudo systemctl restart halo-llama-server
   ```

3. **Thermal throttling** -- Check GPU temperature:
   ```bash
   rocm-smi --showtemp
   ```

### Out of memory

If llama-server crashes with OOM errors, the model is too large for available GPU memory.

```bash
# Check available GPU memory
rocm-smi --showmeminfo vram

# Check what is using GPU memory
rocm-smi --showpids
```

**Fixes:**

- Use a smaller quantization (e.g., Q4_K_M instead of Q8_0)
- Use a smaller model
- Ensure no other GPU process is consuming memory
- Verify the 115GB GTT is enabled (see [GPU memory not showing 115GB](#gpu-memory-not-showing-115gb))

The `-ngl 99` flag in the service file offloads all layers to GPU. If you are running out of VRAM, you can reduce this number to offload fewer layers (remaining layers run on CPU):

```bash
# Edit the service to use fewer GPU layers
sudo systemctl edit halo-llama-server
# Add under [Service]:
# ExecStart=
# ExecStart=/srv/ai/llama-cpp/build-vulkan/bin/llama-server --host 127.0.0.1 --port 8081 --no-mmap -ngl 50 -fa on --model /srv/ai/models/your-model.gguf
```

---

## Network Issues

### Firewall blocking connections

The halo-ai stack uses nftables with a default-deny policy. Only SSH (22), Caddy HTTPS (443, 8443), WireGuard (51820), and ICMP are allowed, and only from your configured LAN subnet (except WireGuard).

**Check current firewall rules:**

```bash
sudo nft list ruleset
```

**If your LAN subnet is different** (e.g., `192.168.1.0/24`):

```bash
# Edit the nftables config
sudo nano /srv/ai/configs/system/nftables.conf

# Change all occurrences of xxx.xxx.xxx.0/24 to your subnet
# Then reload:
sudo nft -f /srv/ai/configs/system/nftables.conf
```

**Temporarily disable the firewall** (for debugging only):

```bash
sudo nft flush ruleset
```

**Re-enable after debugging:**

```bash
sudo nft -f /srv/ai/configs/system/nftables.conf
```

### SSH cannot connect

**1. Check fail2ban:**

fail2ban may have banned your IP after failed login attempts:

```bash
# Check fail2ban status
sudo fail2ban-client status sshd

# Unban an IP
sudo fail2ban-client set sshd unbanip <YOUR_IP>
```

**2. Check SSH configuration:**

The installer hardens SSH with key-only authentication and restricts access to a single user:

```bash
cat /etc/ssh/sshd_config.d/90-halo-security.conf
```

This file contains:

```
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
PermitRootLogin no
AllowUsers <YOUR_USER>
```

If `AllowUsers` still says `<YOUR_USER>` instead of your actual username, fix it:

```bash
sudo sed -i "s/<YOUR_USER>/$(whoami)/" /etc/ssh/sshd_config.d/90-halo-security.conf
sudo systemctl restart sshd
```

**3. Ensure you are using key-based authentication:**

Password auth is disabled. You must have your public key in `~/.ssh/authorized_keys` on the server:

```bash
# On the server, check authorized keys
cat ~/.ssh/authorized_keys

# From the client, copy your key
ssh-copy-id <YOUR_USER>@<SERVER_IP>
```

**4. Check the firewall allows SSH from your subnet:**

```bash
sudo nft list ruleset | grep "dport 22"
```

### Services not reachable from other devices

All halo-ai services bind to `127.0.0.1` (localhost only) for security. They are only accessible from the server itself or through the Caddy reverse proxy.

**To access services from another device, you have two options:**

**Option 1: Use Caddy (recommended)**

Caddy listens on port 443 and routes traffic to the backend services:

| URL Path | Backend Service |
|----------|----------------|
| `https://strixhalo/` | Open WebUI (:3000) |
| `https://strixhalo/chat/*` | Open WebUI (:3000) |
| `https://strixhalo/research/*` | Vane (:3001) |
| `https://strixhalo/workflows/*` | n8n (:5678) |
| `https://strixhalo/api/*` | Lemonade (:8080) |
| `https://strixhalo/comfyui/*` | ComfyUI (:8188) |

**Option 2: SSH tunnel**

Forward specific ports through SSH:

```bash
# Forward Open WebUI and Vane
ssh -L 3000:localhost:3000 -L 3001:localhost:3001 <YOUR_USER>@strixhalo

# Forward everything
ssh -L 3000:localhost:3000 \
    -L 3001:localhost:3001 \
    -L 5678:localhost:5678 \
    -L 8080:localhost:8080 \
    -L 8081:localhost:8081 \
    -L 8188:localhost:8188 \
    -L 8888:localhost:8888 \
    <YOUR_USER>@strixhalo
```

Then access via `http://localhost:3000` etc. on your local machine.

---

## Backup Issues

### Backup script not found

The backup script lives at `/srv/ai/scripts/halo-backup.sh`. If it is missing, the repo checkout may have failed:

```bash
# Check if the script exists
ls -la /srv/ai/scripts/halo-backup.sh

# If missing, re-pull from the repo
cd /srv/ai
git checkout origin/main -- scripts/halo-backup.sh
chmod +x /srv/ai/scripts/halo-backup.sh
```

### Timer not firing

The backup runs daily via `halo-backup.timer`:

```bash
# Check if the timer is active
systemctl list-timers | grep halo-backup

# Check timer status
sudo systemctl status halo-backup.timer

# If inactive, enable and start it
sudo systemctl enable --now halo-backup.timer
```

The timer has `RandomizedDelaySec=1800` (30 minutes), so it will not fire at exactly midnight -- it will run sometime within 30 minutes of the scheduled time.

**Manually trigger a backup:**

```bash
sudo systemctl start halo-backup.service

# Check if it ran successfully
sudo systemctl status halo-backup.service
journalctl -u halo-backup -n 50 --no-pager
```

### Disk space

Backups and model files can consume significant disk space:

```bash
# Check overall disk usage
df -h /srv/ai

# Check what is using space
du -sh /srv/ai/*/

# Check model sizes
du -sh /srv/ai/models/*

# Check backup sizes
du -sh /srv/ai/backups/*
```

**If running low on space:**

- Remove old backups: `ls -la /srv/ai/backups/ && rm /srv/ai/backups/<old-backup>`
- Remove unused models: `ls -lh /srv/ai/models/ && rm /srv/ai/models/<unused-model>.gguf`
- Check Btrfs snapshot usage: `sudo btrfs subvolume list /srv/ai`
- Clean old snapshots: `sudo snapper list && sudo snapper delete <snapshot-id>`

---

## Common Commands Reference

### Start / stop / restart services

```bash
# Start a service
sudo systemctl start halo-llama-server

# Stop a service
sudo systemctl stop halo-llama-server

# Restart a service
sudo systemctl restart halo-llama-server

# Reload configuration without restart (Caddy only)
sudo systemctl reload halo-caddy

# Enable a service to start on boot
sudo systemctl enable halo-llama-server

# Disable a service from starting on boot
sudo systemctl disable halo-llama-server

# Start all core services
sudo systemctl start halo-llama-server halo-lemonade halo-open-webui halo-caddy

# Start everything
sudo systemctl start halo-llama-server halo-lemonade halo-open-webui halo-vane \
    halo-searxng halo-qdrant halo-n8n halo-whisper-server halo-comfyui \
    halo-dashboard-api halo-dashboard-ui halo-caddy

# Check status of all halo services
systemctl list-units 'halo-*' --all
```

### View logs

```bash
# Stream live logs for a service
journalctl -u halo-llama-server -f

# Last 100 lines
journalctl -u halo-llama-server -n 100 --no-pager

# Logs since last boot
journalctl -u halo-llama-server -b

# Logs from a specific time
journalctl -u halo-llama-server --since "1 hour ago"

# All halo service logs combined
journalctl -u 'halo-*' --since "10 min ago"

# Watchdog agent logs
journalctl -u halo-watchdog -n 50 --no-pager

# Agent logs
journalctl -u halo-agent -f
```

### Check GPU status

```bash
# GPU overview (temperature, utilization, memory)
rocm-smi

# Continuous monitoring
watch -n 1 rocm-smi

# GPU memory details
rocm-smi --showmeminfo vram

# GPU temperature
rocm-smi --showtemp

# Running GPU processes
rocm-smi --showpids

# Full GPU info
rocminfo

# OpenCL info
clinfo

# Verify gfx1151 architecture
rocminfo | grep gfx1151
```

### Check disk space

```bash
# Overall filesystem usage
df -h

# /srv/ai breakdown
du -sh /srv/ai/*/

# Model files
ls -lh /srv/ai/models/

# Btrfs filesystem usage (if using Btrfs)
sudo btrfs filesystem usage /srv/ai
```

### Run manual backup

```bash
# Trigger the backup service
sudo systemctl start halo-backup.service

# Or run the script directly
/srv/ai/scripts/halo-backup.sh /srv/ai/backups

# Check when the next automatic backup will run
systemctl list-timers | grep halo-backup
```

### Rotate Caddy password

```bash
# Generate a new password hash
caddy hash-password --plaintext 'YourNewSecurePassword'

# Edit the Caddyfile — replace the hash on the "admin" line inside basicauth
nano /srv/ai/configs/Caddyfile

# Reload Caddy (no downtime)
sudo systemctl reload halo-caddy
```

### Regenerate API keys

**SearXNG secret key:**

```bash
# Generate a new key
NEW_KEY=$(openssl rand -hex 32)
echo "New SearXNG key: $NEW_KEY"

# Update the settings file
sed -i "s/secret_key: .*/secret_key: \"$NEW_KEY\"/" /srv/ai/configs/searxng/settings.yml

# Restart SearXNG
sudo systemctl restart halo-searxng
```

**Dashboard API key:**

```bash
# Generate a new key
NEW_KEY=$(openssl rand -base64 32)
echo "New Dashboard key: $NEW_KEY"

# Write the new key
echo -n "$NEW_KEY" > /srv/ai/dashboard-api/data/dashboard-api-key.txt
chmod 600 /srv/ai/dashboard-api/data/dashboard-api-key.txt

# Restart the dashboard
sudo systemctl restart halo-dashboard-api
```

### Check firewall rules

```bash
# Show all active rules
sudo nft list ruleset

# Check if a specific port is allowed
sudo nft list ruleset | grep "dport 443"

# Reload firewall from config
sudo nft -f /srv/ai/configs/system/nftables.conf

# Temporarily flush all rules (allow everything — debug only!)
sudo nft flush ruleset
```

### Check fail2ban status

```bash
# Overall status
sudo fail2ban-client status

# SSH jail details (banned IPs, ban count)
sudo fail2ban-client status sshd

# Unban an IP address
sudo fail2ban-client set sshd unbanip xxx.xxx.xxx.xxx

# Check fail2ban logs
journalctl -u fail2ban -n 50 --no-pager

# Manually ban an IP
sudo fail2ban-client set sshd banip xxx.xxx.xxx.xxx
```

### Switch LLM backend

```bash
# Switch to Vulkan backend
/srv/ai/scripts/halo-driver-swap.sh vulkan

# Switch to HIP/ROCm backend
/srv/ai/scripts/halo-driver-swap.sh hip

# Restart llama-server after switching
sudo systemctl restart halo-llama-server
```

### Model management

```bash
# List available models
/srv/ai/scripts/halo-models.sh list

# Download a model
/srv/ai/scripts/halo-models.sh download <model-name>

# Activate a model (updates llama-server config and benchmarks)
/srv/ai/scripts/halo-models.sh activate <model-name>
```

### System updates

```bash
# Update all halo-ai components (creates a Btrfs snapshot first)
/srv/ai/scripts/halo-update.sh update
```
