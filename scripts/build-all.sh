#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRV=/srv/ai
JOBS=$(nproc)

source /srv/ai/configs/rocm.env

echo "=== Building AI Stack on $(hostname) ==="
echo "CPU cores: $JOBS"
echo "ROCm: $ROCM_HOME"

# Each component has its own build script
for script in "$SCRIPT_DIR"/build-*.sh; do
    [ -f "$script" ] || continue
    echo ">>> Running $(basename $script)..."
    bash "$script"
done

echo "=== All builds complete ==="
