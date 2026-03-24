#!/bin/bash
# halo-ai watchdog agent
# Monitors all services, auto-repairs, checks for updates
# Only reports when there's an issue it couldn't fix

set -euo pipefail
LOG=/var/log/halo-watchdog.log
NOTIFY_EMAIL=""  # Set if you want email notifications
SERVICES=(llama-server lemonade open-webui vane searxng qdrant n8n whisper-server comfyui)
REPOS=(
    "/srv/ai/llama-cpp|https://github.com/ggml-org/llama.cpp"
    "/srv/ai/lemonade|https://github.com/lemonade-sdk/lemonade"
    "/srv/ai/open-webui|https://github.com/open-webui/open-webui"
    "/srv/ai/vane|https://github.com/ItzCrazyKns/Vane"
    "/srv/ai/searxng|https://github.com/searxng/searxng"
    "/srv/ai/qdrant|https://github.com/qdrant/qdrant"
    "/srv/ai/n8n|https://github.com/n8n-io/n8n"
    "/srv/ai/whisper-cpp|https://github.com/ggerganov/whisper.cpp"
    "/srv/ai/comfyui|https://github.com/comfyanonymous/ComfyUI"
    "/srv/ai/kokoro|https://github.com/remsky/Kokoro-FastAPI"
)

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(timestamp) [INFO] $1" >> "$LOG"; }
warn() { echo "$(timestamp) [WARN] $1" >> "$LOG"; }
error() { echo "$(timestamp) [ERROR] $1" >> "$LOG"; }
report() {
    # Only called when auto-repair fails
    local msg="$1"
    error "$msg"
    # Send desktop notification
    notify-send -u critical "halo-ai watchdog" "$msg" 2>/dev/null || true
    # Log to systemd journal for visibility
    logger -t halo-watchdog -p user.err "$msg"
}

# ─── SERVICE HEALTH CHECK ───────────────────────────────
check_services() {
    local failures=0
    for svc in "${SERVICES[@]}"; do
        if ! systemctl is-active --quiet "halo-${svc}.service" 2>/dev/null; then
            warn "Service halo-${svc} is down, attempting restart..."
            if systemctl restart "halo-${svc}.service" 2>/dev/null; then
                sleep 3
                if systemctl is-active --quiet "halo-${svc}.service"; then
                    log "Service halo-${svc} recovered after restart"
                else
                    report "Service halo-${svc} FAILED to restart — manual intervention required"
                    ((failures++))
                fi
            else
                report "Service halo-${svc} restart command failed"
                ((failures++))
            fi
        fi
    done
    return $failures
}

# ─── GPU HEALTH CHECK ──────────────────────────────────
check_gpu() {
    if [ ! -c /dev/kfd ]; then
        report "GPU device /dev/kfd missing — possible driver crash"
        return 1
    fi
    
    # Check if amdgpu module is loaded
    if ! lsmod | grep -q amdgpu; then
        report "amdgpu kernel module not loaded"
        return 1
    fi
    
    # Check GPU temperature (warn above 85C)
    local gpu_temp
    gpu_temp=$(cat /sys/class/drm/card*/device/hwmon/hwmon*/temp1_input 2>/dev/null | head -1)
    if [ -n "$gpu_temp" ]; then
        gpu_temp=$((gpu_temp / 1000))
        if [ "$gpu_temp" -gt 85 ]; then
            report "GPU temperature critical: ${gpu_temp}C"
            return 1
        fi
    fi
    return 0
}

# ─── DISK HEALTH CHECK ─────────────────────────────────
check_disk() {
    local usage
    usage=$(df /srv/ai --output=pcent | tail -1 | tr -d ' %')
    if [ "$usage" -gt 90 ]; then
        report "Disk usage at ${usage}% on /srv/ai — running low"
        return 1
    fi
    return 0
}

# ─── UPDATE CHECK ──────────────────────────────────────
check_updates() {
    local updates_available=0
    for entry in "${REPOS[@]}"; do
        IFS='|' read -r path url <<< "$entry"
        if [ -d "$path/.git" ]; then
            cd "$path"
            git fetch --quiet 2>/dev/null || continue
            local local_hash remote_hash
            local_hash=$(git rev-parse HEAD 2>/dev/null)
            remote_hash=$(git rev-parse '@{u}' 2>/dev/null || echo "$local_hash")
            if [ "$local_hash" != "$remote_hash" ]; then
                local behind
                behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)
                if [ "$behind" -gt 0 ]; then
                    log "Update available: $(basename $path) is $behind commits behind upstream"
                    ((updates_available++))
                fi
            fi
        fi
    done
    
    # Check system updates
    local sys_updates
    sys_updates=$(pacman -Qu 2>/dev/null | wc -l)
    if [ "$sys_updates" -gt 0 ]; then
        log "System: $sys_updates package updates available"
    fi
    
    # Check kernel
    local running_kernel installed_kernel
    running_kernel=$(uname -r)
    installed_kernel=$(pacman -Q linux 2>/dev/null | awk '{print $2}' | sed 's/\.arch/-arch/')
    if [ "$running_kernel" != "$installed_kernel" ]; then
        log "Kernel update pending: running $running_kernel, installed $installed_kernel (reboot needed)"
    fi
    
    return 0
}

# ─── MEMORY CHECK ──────────────────────────────────────
check_memory() {
    local mem_available
    mem_available=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
    if [ "$mem_available" -lt 4096 ]; then
        report "Available memory critically low: ${mem_available}MB — models may fail to load"
        return 1
    fi
    return 0
}

# ─── MAIN ──────────────────────────────────────────────
main() {
    local issues=0
    
    check_services || ((issues+=$?))
    check_gpu || ((issues++))
    check_disk || ((issues++))
    check_memory || ((issues++))
    check_updates
    
    if [ "$issues" -eq 0 ]; then
        log "All checks passed"
    fi
}

main
