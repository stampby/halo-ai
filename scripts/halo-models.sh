#!/bin/bash
# halo-ai — designed and built by the architect
# halo-ai Model Manager
set -euo pipefail

MODELS_DIR="/srv/ai/models"
SERVICE="halo-llama-server.service"
UNIT="/etc/systemd/system/$SERVICE"

# Models curated for 123GB GTT Strix Halo
declare -A CATALOG
CATALOG["qwen3-30b-a3b"]="unsloth/Qwen3-30B-A3B-GGUF|Qwen3-30B-A3B-Q4_K_M.gguf|18G|~91 tok/s|Best balance of speed and quality (MoE)"
CATALOG["qwen3-coder-30b"]="unsloth/Qwen3-Coder-30B-A3B-GGUF|Qwen3-Coder-30B-A3B-Q4_K_M.gguf|18G|~100 tok/s|Code-focused MoE — ideal for Copilot"
CATALOG["llama3-8b"]="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF|Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf|5G|~120 tok/s|Fast small model"
CATALOG["llama3-70b"]="bartowski/Meta-Llama-3.1-70B-Instruct-GGUF|Meta-Llama-3.1-70B-Instruct-Q4_K_M.gguf|40G|~18 tok/s|Large dense model"
CATALOG["llama3-70b-q8"]="bartowski/Meta-Llama-3.1-70B-Instruct-GGUF|Meta-Llama-3.1-70B-Instruct-Q8_0.gguf|70G|~10 tok/s|70B at highest quality — only Strix Halo can fit this"
CATALOG["deepseek-v3"]="bartowski/DeepSeek-V3-0324-GGUF|DeepSeek-V3-0324-Q4_K_M.gguf|95G|~8 tok/s|Frontier MoE — pushes 123GB limit"
CATALOG["gemma3-27b"]="bartowski/gemma-3-27b-it-GGUF|gemma-3-27b-it-Q4_K_M.gguf|16G|~45 tok/s|Google's best open model"
CATALOG["mistral-small"]="bartowski/Mistral-Small-3.1-24B-Instruct-2503-GGUF|Mistral-Small-3.1-24B-Instruct-2503-Q4_K_M.gguf|14G|~50 tok/s|Fast and capable"
CATALOG["qwen3-235b"]="ubergarm/Qwen3-235B-A22B-GGUF|Qwen3-235B-A22B-UD-Q2_K_XL.gguf|95G|~8 tok/s|Frontier 235B MoE — peak intelligence"
CATALOG["gpt-oss-120b"]="bartowski/GPT-OSS-120B-GGUF|GPT-OSS-120B-Q4_K_M.gguf|59G|~21 tok/s|Frontier dense — fits comfortably in 123GB"
CATALOG["gemma4-26b"]="unsloth/gemma-4-26B-A4B-it-GGUF|gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf|16G|~90 tok/s|Google Gemma 4 MoE — 140+ languages, multimodal, Apache 2.0"

list_catalog() {
    echo "Available models for Strix Halo (123GB GTT):"
    echo ""
    printf "%-22s %-6s %-12s %s\n" "NAME" "SIZE" "SPEED" "DESCRIPTION"
    printf "%-22s %-6s %-12s %s\n" "----" "----" "-----" "-----------"
    for name in $(echo "${!CATALOG[@]}" | tr ' ' '\n' | sort); do
        IFS='|' read -r repo file size speed desc <<< "${CATALOG[$name]}"
        local status=""
        [ -f "$MODELS_DIR/$file" ] && status=" [installed]"
        printf "%-22s %-6s %-12s %s%s\n" "$name" "$size" "$speed" "$desc" "$status"
    done
}

list_installed() {
    echo "Installed models:"
    echo ""
    for f in "$MODELS_DIR"/*.gguf; do
        [ -f "$f" ] || continue
        size=$(du -h "$f" | cut -f1)
        name=$(basename "$f")
        # Check if active
        active=""
        grep -q "$name" "$UNIT" 2>/dev/null && active=" [ACTIVE]"
        echo "  $name ($size)$active"
    done
    
    echo ""
    echo "GTT memory: $(awk '{printf "%.0fGB", $1/1073741824}' /sys/class/drm/card*/device/mem_info_gtt_used 2>/dev/null) used / $(awk '{printf "%.0fGB", $1/1073741824}' /sys/class/drm/card*/device/mem_info_gtt_total 2>/dev/null) total"
}

download_model() {
    local name="$1"
    if [ -z "${CATALOG[$name]+x}" ]; then
        echo "Unknown model: $name"
        echo "Run '$0 list' to see available models"
        exit 1
    fi
    
    IFS='|' read -r repo file size speed desc <<< "${CATALOG[$name]}"
    local url="https://huggingface.co/$repo/resolve/main/$file"
    local dest="$MODELS_DIR/$file"
    
    if [ -f "$dest" ]; then
        echo "$file already downloaded"
        return 0
    fi
    
    echo "Downloading $name ($size)..."
    echo "  $desc"
    echo "  Expected speed: $speed"
    echo ""
    curl -L --progress-bar -o "$dest" "$url"
    
    if [ -s "$dest" ]; then
        echo ""
        echo "Downloaded: $(du -h "$dest" | cut -f1)"
    else
        rm -f "$dest"
        echo "Download failed"
        exit 1
    fi
}

activate_model() {
    local name="$1"
    local file=""
    
    # Check if it's a catalog name or a filename
    if [ -n "${CATALOG[$name]+x}" ]; then
        IFS='|' read -r repo file size speed desc <<< "${CATALOG[$name]}"
    elif [ -f "$MODELS_DIR/$name" ]; then
        file="$name"
    elif [ -f "$MODELS_DIR/${name}.gguf" ]; then
        file="${name}.gguf"
    else
        echo "Model not found: $name"
        echo "Download it first: $0 download $name"
        exit 1
    fi
    
    local path="$MODELS_DIR/$file"
    if [ ! -f "$path" ]; then
        echo "Model file not found: $path"
        echo "Download it first: $0 download $name"
        exit 1
    fi
    
    echo "Activating $file..."
    
    # Snapshot before model swap
    sudo snapper -c root create --type single --cleanup-algorithm number \
        --description "halo-models activate $name $(date +%Y%m%d-%H%M%S)" 2>/dev/null
    
    # Update service
    sudo sed -i "s|--model .*\.gguf|--model $path|" "$UNIT"
    sudo systemctl daemon-reload
    sudo systemctl restart "$SERVICE"
    sleep 10
    
    if systemctl is-active --quiet "$SERVICE"; then
        echo "Model activated. Running quick benchmark..."
        curl -s http://127.0.0.1:8081/v1/chat/completions \
          -H 'Content-Type: application/json' \
          -d "{\"model\":\"q\",\"messages\":[{\"role\":\"user\",\"content\":\"Write about AI. /no_think\"}],\"max_tokens\":100,\"temperature\":0}" | python3 -c "
import json,sys; t=json.load(sys.stdin)['timings']
print(f'  Speed: {t[\"predicted_per_second\"]:.1f} tok/s')
print(f'  Prompt: {t[\"prompt_per_second\"]:.1f} tok/s')
"
    else
        echo "ERROR: Service failed to start with new model"
        journalctl -u "$SERVICE" --no-pager -n 5
    fi
}

remove_model() {
    local name="$1"
    local file=""
    
    if [ -n "${CATALOG[$name]+x}" ]; then
        IFS='|' read -r repo file size speed desc <<< "${CATALOG[$name]}"
    else
        file="$name"
    fi
    
    local path="$MODELS_DIR/$file"
    if [ ! -f "$path" ]; then
        echo "Not found: $path"
        exit 1
    fi
    
    # Check if active
    if grep -q "$file" "$UNIT" 2>/dev/null; then
        echo "Cannot remove active model. Switch to another model first."
        exit 1
    fi
    
    local size=$(du -h "$path" | cut -f1)
    rm "$path"
    echo "Removed $file ($size freed)"
}

case "${1:-help}" in
    list|ls)      list_catalog ;;
    installed|i)  list_installed ;;
    download|dl)  download_model "${2:?Usage: $0 download <model-name>}" ;;
    activate|use) activate_model "${2:?Usage: $0 activate <model-name>}" ;;
    remove|rm)    remove_model "${2:?Usage: $0 remove <model-name>}" ;;
    *)
        echo "halo-ai Model Manager"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "  list                List available models for Strix Halo"
        echo "  installed           Show downloaded models"
        echo "  download <name>     Download a model"
        echo "  activate <name>     Switch to a model (restarts inference)"
        echo "  remove <name>       Delete a downloaded model"
        echo ""
        echo "Examples:"
        echo "  $0 list"
        echo "  $0 download qwen3-coder-30b"
        echo "  $0 activate qwen3-coder-30b"
        ;;
esac
