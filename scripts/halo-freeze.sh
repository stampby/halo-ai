#!/bin/bash
# halo-ai — designed and built by the architect
# halo-freeze.sh — Lock the entire AI stack so Arch can't break it
# Run this after a working build to snapshot the exact state
# Run halo-thaw.sh to restore from snapshot

set -euo pipefail

FREEZE_DIR="/srv/ai/freeze"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SNAPSHOT="$FREEZE_DIR/$TIMESTAMP"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  halo-freeze — locking AI stack"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p "$SNAPSHOT"

# 1. Record exact versions of everything
echo "[1/6] Recording versions..."
cat > "$SNAPSHOT/versions.txt" << VERSIONS
# halo-ai stack freeze — $TIMESTAMP
kernel=$(uname -r)
python=$(/opt/python3.13/bin/python3.13 --version 2>&1)
rocm=$(/opt/rocm/bin/rocminfo 2>/dev/null | grep -m1 'Runtime Version' | awk '{print $NF}' || echo "unknown")
torch=$(/srv/ai/comfyui/.venv/bin/python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "not installed")
torch_hip=$(/srv/ai/comfyui/.venv/bin/python -c "import torch; print(torch.version.hip)" 2>/dev/null || echo "n/a")
gpu=$(/opt/rocm/bin/rocminfo 2>/dev/null | grep -m1 'gfx' | awk '{print $2}' || echo "unknown")
comfyui=$(cd /srv/ai/comfyui && git rev-parse HEAD 2>/dev/null || echo "unknown")
VERSIONS
cat "$SNAPSHOT/versions.txt"

# 2. Freeze pip packages
echo ""
echo "[2/6] Freezing pip packages..."
/srv/ai/comfyui/.venv/bin/pip freeze > "$SNAPSHOT/requirements.frozen.txt"
wc -l < "$SNAPSHOT/requirements.frozen.txt" | xargs -I{} echo "  {} packages frozen"

# 3. Save pip wheel cache for offline rebuild
echo "[3/6] Caching wheels for offline rebuild..."
mkdir -p "$SNAPSHOT/wheels"
/srv/ai/comfyui/.venv/bin/pip wheel \
    torch==2.9.1+rocm7.11.0 \
    torchvision==0.24.0+rocm7.11.0 \
    torchaudio==2.9.0+rocm7.11.0 \
    triton==3.5.1+rocm7.11.0 \
    --index-url https://repo.amd.com/rocm/whl/gfx1151/ \
    --wheel-dir "$SNAPSHOT/wheels" \
    --no-deps 2>/dev/null && echo "  Core wheels cached" || echo "  Wheel cache skipped (network issue)"

# 4. Snapshot the venv Python binary
echo "[4/6] Snapshotting Python interpreter..."
cp /opt/python3.13/bin/python3.13 "$SNAPSHOT/python3.13.bin"
cp /srv/ai/comfyui/.venv/pyvenv.cfg "$SNAPSHOT/pyvenv.cfg"
echo "  Python 3.13.3 binary saved"

# 5. Pin git commits for all source-built components
echo "[5/6] Pinning git commits..."
cat > "$SNAPSHOT/git-pins.txt" << PINS
comfyui=$(cd /srv/ai/comfyui && git rev-parse HEAD 2>/dev/null || echo "unknown")
llama_cpp=$(cd /srv/ai/llama-cpp && git rev-parse HEAD 2>/dev/null || echo "unknown")
whisper_cpp=$(cd /srv/ai/whisper-cpp && git rev-parse HEAD 2>/dev/null || echo "unknown")
open_webui=$(cd /srv/ai/open-webui && git rev-parse HEAD 2>/dev/null || echo "unknown")
vane=$(cd /srv/ai/vane && git rev-parse HEAD 2>/dev/null || echo "unknown")
PINS
cat "$SNAPSHOT/git-pins.txt"

# 6. Record system packages that matter
echo ""
echo "[6/6] Recording system package state..."
pacman -Q linux linux-headers python mesa vulkan-radeon libdrm 2>/dev/null > "$SNAPSHOT/system-packages.txt"
cat "$SNAPSHOT/system-packages.txt"

# Create "latest" symlink
ln -sfn "$SNAPSHOT" "$FREEZE_DIR/latest"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  FROZEN: $SNAPSHOT"
echo "  To restore: halo-thaw.sh $TIMESTAMP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
