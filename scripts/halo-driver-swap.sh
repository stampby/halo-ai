#!/bin/bash
# halo-ai — designed and built by the architect
# halo-ai Vulkan/ROCm driver swap tool
# Instantly switch llama.cpp between backends without reinstalling anything
#
# Usage:
#   halo-driver-swap.sh vulkan    # Vulkan (RADV) - fastest generation
#   halo-driver-swap.sh hip       # HIP (ROCm) - fastest prompt processing, long context
#   halo-driver-swap.sh opencl    # OpenCL (ROCm) - compute workloads
#   halo-driver-swap.sh status    # Show current backend
#   halo-driver-swap.sh list      # Show all available backends
#   halo-driver-swap.sh bench     # Quick benchmark on current backend

set -euo pipefail

SERVICE="halo-llama-server.service"
UNIT="/etc/systemd/system/$SERVICE"
HIP_BIN="/srv/ai/llama-cpp/build-hip/bin/llama-server"
VK_BIN="/srv/ai/llama-cpp/build-vulkan/bin/llama-server"
CL_BIN="/srv/ai/llama-cpp/build-opencl/bin/llama-server"

status() {
    local current
    current=$(grep ExecStart= "$UNIT" | grep -o 'build-[a-z]*/bin' | cut -d/ -f1 | sed 's/build-//')
    echo "Current backend: $current"
    
    if systemctl is-active --quiet "$SERVICE"; then
        echo "Service: running"
        # Quick speed test
        local result
        result=$(curl -s http://127.0.0.1:8081/v1/chat/completions \
            -H 'Content-Type: application/json' \
            -d '{"model":"q","messages":[{"role":"user","content":"hi /no_think"}],"max_tokens":20,"temperature":0}' 2>/dev/null)
        if [ -n "$result" ]; then
            echo "$result" | python3 -c "
import json,sys
r=json.load(sys.stdin)
t=r['timings']
print(f'Speed: {t[\"predicted_per_second\"]:.1f} tok/s')
" 2>/dev/null
        fi
    else
        echo "Service: stopped"
    fi
}

swap_to() {
    local backend="$1"
    local bin
    local flags
    
    case "$backend" in
        vulkan|vk)
            bin="$VK_BIN"
            flags="--no-mmap -ngl 99 -fa on"
            echo "Switching to Vulkan (RADV)"
            echo "  Best for: token generation speed"
            ;;
        hip|rocm)
            bin="$HIP_BIN"
            flags="--no-mmap -ngl 99"
            echo "Switching to HIP (ROCm)"
            echo "  Best for: prompt processing, long context, Flash Attention via rocWMMA"
            ;;
        opencl|cl)
            bin="$CL_BIN"
            flags="--no-mmap -ngl 99"
            echo "Switching to OpenCL (ROCm)"
            echo "  Best for: general GPU compute, compatibility testing"
            if [ ! -f "$CL_BIN" ]; then
                echo "OpenCL backend not built yet. Build with:"
                echo "  cd /srv/ai/llama-cpp && cmake -B build-opencl -DGGML_OPENCL=ON -DCMAKE_BUILD_TYPE=Release -G Ninja . && cmake --build build-opencl -j\$(nproc)"
                exit 1
            fi
            ;;
        *)
            echo "Unknown backend: $backend"
            echo "Options: vulkan, hip, opencl"
            exit 1
            ;;
    esac
    
    # Snapshot before swap
    echo "Taking snapshot before driver swap..."
    sudo snapper -c root create --type single --cleanup-algorithm number \
        --description "halo-driver-swap to $backend $(date +%Y%m%d-%H%M%S)" 2>/dev/null
    
    # Stop service
    echo "Stopping llama-server..."
    sudo systemctl stop "$SERVICE"
    
    # Update service file — escape sed metacharacters in bin/flags
    local escaped_bin escaped_flags
    escaped_bin=$(printf '%s\n' "$bin" | sed -e 's/[&/\]/\\&/g')
    escaped_flags=$(printf '%s\n' "$flags" | sed -e 's/[&/\]/\\&/g')
    sudo sed -i "s|ExecStart=.*llama-server.*|ExecStart=${escaped_bin} --host 127.0.0.1 --port 8081 ${escaped_flags} --model /srv/ai/models/qwen3-30b-a3b-q4_k_m.gguf|" "$UNIT"
    sudo systemctl daemon-reload
    
    # Start service
    echo "Starting llama-server with $backend backend..."
    sudo systemctl start "$SERVICE"
    sleep 8
    
    if systemctl is-active --quiet "$SERVICE"; then
        echo "Service started successfully"
        status
    else
        echo "ERROR: Service failed to start. Check: journalctl -u $SERVICE"
        exit 1
    fi
}

bench() {
    echo "=== Quick Benchmark ==="
    status
    echo ""
    
    for tokens in 20 200 500; do
        result=$(curl -s http://127.0.0.1:8081/v1/chat/completions \
            -H 'Content-Type: application/json' \
            -d "{\"model\":\"q\",\"messages\":[{\"role\":\"user\",\"content\":\"Write about AI. /no_think\"}],\"max_tokens\":$tokens,\"temperature\":0}" 2>/dev/null)
        echo "$result" | python3 -c "
import json,sys
r=json.load(sys.stdin)
t=r['timings']
print(f'{t[\"predicted_n\"]:>4} tokens: {t[\"predicted_per_second\"]:>6.1f} tok/s  (prompt: {t[\"prompt_per_second\"]:>6.1f} tok/s)')
" 2>/dev/null
    done
}

list() {
    echo "Available backends:"
    [ -f "$VK_BIN" ]  && echo "  ✓ vulkan  - Vulkan (RADV)"       || echo "  ✗ vulkan  - not built"
    [ -f "$HIP_BIN" ] && echo "  ✓ hip     - HIP (ROCm)"          || echo "  ✗ hip     - not built"
    [ -f "$CL_BIN" ]  && echo "  ✓ opencl  - OpenCL (ROCm)"       || echo "  ✗ opencl  - not built"
    echo ""
    status
}

case "${1:-status}" in
    vulkan|vk)      swap_to vulkan ;;
    hip|rocm)       swap_to hip ;;
    opencl|cl)      swap_to opencl ;;
    status)         status ;;
    list)           list ;;
    bench)          bench ;;
    *)
        echo "halo-ai Driver Swap Tool"
        echo ""
        echo "Usage: $0 {vulkan|hip|opencl|status|list|bench}"
        echo ""
        echo "  vulkan  - Switch to Vulkan (RADV) — fastest generation (~91 tok/s)"
        echo "  hip     - Switch to HIP (ROCm) — fastest prompt processing, best for long context"
        echo "  opencl  - Switch to OpenCL (ROCm) — general GPU compute"
        echo "  status  - Show current backend and speed"
        echo "  list    - Show all available backends"
        echo "  bench   - Quick benchmark on current backend"
        echo ""
        echo "Backends are pre-compiled. Swap takes ~10 seconds."
        echo "A Btrfs snapshot is taken before every swap for safety."
        ;;
esac
