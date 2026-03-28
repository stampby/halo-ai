#!/bin/bash
# halo-ai — designed and built by the architect
# halo-thaw.sh — Restore AI stack from a frozen snapshot
# Usage: halo-thaw.sh [timestamp]  (defaults to latest)

set -euo pipefail

FREEZE_DIR="/srv/ai/freeze"
SNAPSHOT="${1:-latest}"

if [ "$SNAPSHOT" = "latest" ]; then
    SNAPSHOT_PATH="$FREEZE_DIR/latest"
else
    SNAPSHOT_PATH="$FREEZE_DIR/$SNAPSHOT"
fi

if [ ! -d "$SNAPSHOT_PATH" ]; then
    echo "ERROR: Snapshot not found: $SNAPSHOT_PATH"
    echo "Available snapshots:"
    ls -1 "$FREEZE_DIR" 2>/dev/null | grep -v latest
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  halo-thaw — restoring AI stack"
echo "  from: $SNAPSHOT_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show what we're restoring
echo "Frozen state:"
cat "$SNAPSHOT_PATH/versions.txt"
echo ""

read -p "Restore this snapshot? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

# 1. Stop services
echo "[1/5] Stopping AI services..."
sudo systemctl stop halo-comfyui 2>/dev/null || true
sudo systemctl stop halo-llama-server 2>/dev/null || true

# Cleanup trap — restart services even if thaw fails
cleanup() {
    echo "Thaw interrupted or failed — restarting services..."
    sudo systemctl start halo-comfyui 2>/dev/null || true
    sudo systemctl start halo-llama-server 2>/dev/null || true
}
trap cleanup ERR INT TERM

# 2. Rebuild venv from frozen requirements
echo "[2/5] Rebuilding venv from frozen state..."
cd /srv/ai/comfyui
rm -rf .venv
/opt/python3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate

# Try offline first (from cached wheels), fall back to network
if [ -d "$SNAPSHOT_PATH/wheels" ] && [ "$(ls -A "$SNAPSHOT_PATH/wheels" 2>/dev/null)" ]; then
    echo "  Installing core from cached wheels..."
    pip install --no-index --find-links "$SNAPSHOT_PATH/wheels" \
        torch torchvision torchaudio triton 2>/dev/null || \
    pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ \
        torch==2.9.1+rocm7.11.0 torchvision==0.24.0+rocm7.11.0 \
        torchaudio==2.9.0+rocm7.11.0 triton==3.5.1+rocm7.11.0
else
    echo "  No cached wheels, installing from network..."
    pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ \
        torch==2.9.1+rocm7.11.0 torchvision==0.24.0+rocm7.11.0 \
        torchaudio==2.9.0+rocm7.11.0 triton==3.5.1+rocm7.11.0
fi

# 3. Install remaining packages
echo "[3/5] Installing remaining packages..."
pip install -r requirements.txt 2>&1 | tail -3

# 4. Verify GPU
echo "[4/5] Verifying GPU..."
python -c "
import torch
assert torch.cuda.is_available(), 'GPU not available!'
x = torch.randn(512, 512, device='cuda', dtype=torch.float16)
y = x @ x
print(f'  GPU OK: {torch.cuda.get_device_name(0)}')
print(f'  PyTorch: {torch.__version__}')
print(f'  fp16 matmul: passed')
"

# 5. Restart services
echo "[5/5] Restarting services..."
sudo systemctl start halo-comfyui
sudo systemctl start halo-llama-server 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  RESTORED from $SNAPSHOT_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
