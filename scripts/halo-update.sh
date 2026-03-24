#!/bin/bash
# halo-ai update script
# Takes Btrfs snapshots before any updates, rolls back on failure
set -euo pipefail

LOG=/var/log/halo-update.log
timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(timestamp) [INFO] $1" | tee -a "$LOG"; }
error() { echo "$(timestamp) [ERROR] $1" | tee -a "$LOG"; }

# ── PRE-UPDATE SNAPSHOTS ───────────────────────────
pre_snapshot() {
    log "=== PRE-UPDATE SNAPSHOT ==="
    log "Creating system snapshots before update..."
    
    # Root filesystem snapshot
    ROOT_SNAP=$(sudo snapper -c root create --type pre --cleanup-algorithm number         --description "halo-ai pre-update $(date +%Y%m%d-%H%M%S)" --print-number)
    log "Root snapshot #$ROOT_SNAP created"
    
    # Home filesystem snapshot
    HOME_SNAP=$(sudo snapper -c home create --type pre --cleanup-algorithm number         --description "halo-ai pre-update $(date +%Y%m%d-%H%M%S)" --print-number)
    log "Home snapshot #$HOME_SNAP created"
    
    # Per-service Btrfs snapshots
    for svc in llama-cpp lemonade whisper-cpp open-webui vane searxng qdrant n8n kokoro comfyui; do
        if [ -d "/srv/ai/$svc/.git" ]; then
            local hash=$(cd /srv/ai/$svc && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
            log "  $svc: current commit $hash"
        fi
    done
    
    echo "$ROOT_SNAP" > /tmp/halo-update-root-snap
    echo "$HOME_SNAP" > /tmp/halo-update-home-snap
    log "Snapshots saved. Root=#$ROOT_SNAP Home=#$HOME_SNAP"
}

# ── POST-UPDATE SNAPSHOTS ──────────────────────────
post_snapshot() {
    local ROOT_SNAP=$(cat /tmp/halo-update-root-snap 2>/dev/null)
    local HOME_SNAP=$(cat /tmp/halo-update-home-snap 2>/dev/null)
    
    if [ -n "$ROOT_SNAP" ]; then
        sudo snapper -c root create --type post --pre-number "$ROOT_SNAP"             --cleanup-algorithm number --description "halo-ai post-update $(date +%Y%m%d-%H%M%S)"
        log "Root post-snapshot created (paired with #$ROOT_SNAP)"
    fi
    if [ -n "$HOME_SNAP" ]; then
        sudo snapper -c home create --type post --pre-number "$HOME_SNAP"             --cleanup-algorithm number --description "halo-ai post-update $(date +%Y%m%d-%H%M%S)"
        log "Home post-snapshot created (paired with #$HOME_SNAP)"
    fi
    
    rm -f /tmp/halo-update-root-snap /tmp/halo-update-home-snap
}

# ── ROLLBACK ───────────────────────────────────────
rollback() {
    local ROOT_SNAP=$(cat /tmp/halo-update-root-snap 2>/dev/null)
    local HOME_SNAP=$(cat /tmp/halo-update-home-snap 2>/dev/null)
    
    error "UPDATE FAILED — ROLLING BACK"
    
    if [ -n "$ROOT_SNAP" ]; then
        log "Rolling back root to snapshot #$ROOT_SNAP..."
        sudo snapper -c root undochange "$ROOT_SNAP"..0
        log "Root rolled back"
    fi
    if [ -n "$HOME_SNAP" ]; then
        log "Rolling back home to snapshot #$HOME_SNAP..."
        sudo snapper -c home undochange "$HOME_SNAP"..0
        log "Home rolled back"
    fi
    
    error "Rollback complete. Review /var/log/halo-update.log"
    error "Services may need restart: sudo systemctl restart halo-*"
    notify-send -u critical "halo-ai" "Update failed and was rolled back. Check logs." 2>/dev/null || true
    exit 1
}

# ── STOP SERVICES ──────────────────────────────────
stop_services() {
    log "Stopping all halo-ai services..."
    for svc in halo-llama-server halo-lemonade halo-open-webui halo-vane halo-searxng halo-qdrant halo-n8n halo-comfyui halo-whisper-server; do
        sudo systemctl stop $svc 2>/dev/null || true
    done
    log "All services stopped"
}

# ── START SERVICES ─────────────────────────────────
start_services() {
    log "Starting all halo-ai services..."
    sudo systemctl start halo-qdrant halo-searxng halo-lemonade halo-llama-server
    sleep 5
    sudo systemctl start halo-open-webui halo-vane halo-n8n halo-comfyui
    sleep 3
    
    local failures=0
    for svc in halo-llama-server halo-lemonade halo-open-webui halo-vane halo-searxng halo-qdrant halo-n8n; do
        if ! systemctl is-active --quiet $svc 2>/dev/null; then
            error "Service $svc failed to start after update"
            ((failures++))
        fi
    done
    
    if [ $failures -gt 0 ]; then
        return 1
    fi
    log "All services started successfully"
    return 0
}

# ── UPDATE SYSTEM PACKAGES ─────────────────────────
update_system() {
    log "Checking system package updates..."
    local updates=$(pacman -Qu 2>/dev/null | wc -l)
    if [ "$updates" -eq 0 ]; then
        log "System packages are up to date"
        return 0
    fi
    
    log "Updating $updates system packages..."
    sudo pacman -Syu --noconfirm 2>&1 | tee -a "$LOG" | tail -5
    log "System packages updated"
}

# ── UPDATE AI SERVICES ─────────────────────────────
update_services() {
    source /etc/profile.d/rocm.sh 2>/dev/null || true
    export ROCBLAS_USE_HIPBLASLT=1
    
    log "Updating AI services from upstream..."
    
    for svc in llama-cpp lemonade whisper-cpp open-webui vane searxng qdrant n8n kokoro comfyui; do
        if [ -d "/srv/ai/$svc/.git" ]; then
            cd /srv/ai/$svc
            local before=$(git rev-parse --short HEAD)
            git fetch origin 2>/dev/null
            local behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)
            
            if [ "$behind" -gt 0 ]; then
                log "  $svc: $behind commits behind, updating..."
                git pull --ff-only 2>&1 | tail -3 | tee -a "$LOG"
                local after=$(git rev-parse --short HEAD)
                log "  $svc: updated $before -> $after"
            else
                log "  $svc: up to date ($before)"
            fi
        fi
    done
}

# ── REBUILD CHANGED SERVICES ──────────────────────
rebuild_services() {
    source /etc/profile.d/rocm.sh 2>/dev/null || true
    
    # Check if llama.cpp needs rebuild
    if [ -d /srv/ai/llama-cpp/.git ]; then
        cd /srv/ai/llama-cpp
        if ! git diff --quiet HEAD@{1} -- CMakeLists.txt src/ ggml/ 2>/dev/null; then
            log "Rebuilding llama.cpp (source changed)..."
            cmake --build build-hip -j$(nproc) 2>&1 | tail -5
            cmake --build build-vulkan -j$(nproc) 2>&1 | tail -5
            log "llama.cpp rebuilt"
        fi
    fi
    
    # Check if lemonade needs rebuild
    if [ -d /srv/ai/lemonade/.git ]; then
        cd /srv/ai/lemonade
        if ! git diff --quiet HEAD@{1} -- CMakeLists.txt src/ 2>/dev/null; then
            log "Rebuilding Lemonade (source changed)..."
            cmake --build --preset default 2>&1 | tail -5
            log "Lemonade rebuilt"
        fi
    fi
    
    # Check if whisper.cpp needs rebuild
    if [ -d /srv/ai/whisper-cpp/.git ]; then
        cd /srv/ai/whisper-cpp
        if ! git diff --quiet HEAD@{1} -- CMakeLists.txt src/ 2>/dev/null; then
            log "Rebuilding whisper.cpp (source changed)..."
            cmake --build build -j$(nproc) 2>&1 | tail -5
            log "whisper.cpp rebuilt"
        fi
    fi
    
    # Python services - reinstall if requirements changed
    for pydir in open-webui searxng kokoro comfyui; do
        if [ -d "/srv/ai/$pydir/.git" ]; then
            cd /srv/ai/$pydir
            if ! git diff --quiet HEAD@{1} -- requirements*.txt pyproject.toml 2>/dev/null; then
                log "Reinstalling $pydir (deps changed)..."
                source .venv/bin/activate 2>/dev/null
                pip install -q -e . 2>/dev/null || pip install -q -r requirements.txt 2>/dev/null
                deactivate 2>/dev/null
                log "$pydir reinstalled"
            fi
        fi
    done
    
    # Node services - rebuild if package.json changed
    for nodedir in vane n8n; do
        if [ -d "/srv/ai/$nodedir/.git" ]; then
            cd /srv/ai/$nodedir
            if ! git diff --quiet HEAD@{1} -- package.json yarn.lock pnpm-lock.yaml 2>/dev/null; then
                log "Rebuilding $nodedir (deps changed)..."
                if [ -f yarn.lock ]; then yarn install && yarn build; fi
                if [ -f pnpm-lock.yaml ]; then pnpm install && pnpm build; fi
                log "$nodedir rebuilt"
            fi
        fi
    done
}

# ── MAIN ───────────────────────────────────────────
main() {
    log "========================================"
    log "  halo-ai update starting"
    log "========================================"
    
    # Step 1: Snapshot BEFORE anything changes
    pre_snapshot
    
    # Step 2: Stop services
    stop_services
    
    # Step 3: Update (with rollback on failure)
    trap rollback ERR
    
    update_system
    update_services
    rebuild_services
    
    # Step 4: Start services and verify
    if ! start_services; then
        rollback
    fi
    
    trap - ERR
    
    # Step 5: Post-update snapshot (captures the good state)
    post_snapshot
    
    log "========================================"
    log "  halo-ai update complete"
    log "========================================"
    
    # Verify inference still works
    local test=$(curl -s http://127.0.0.1:8081/v1/chat/completions         -H 'Content-Type: application/json'         -d '{"model":"test","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' 2>/dev/null | grep -c 'choices' || echo 0)
    
    if [ "$test" -eq 0 ]; then
        error "Post-update inference test FAILED"
        rollback
    else
        log "Post-update inference test passed"
    fi
}

# Parse args
case "${1:-update}" in
    update)  main ;;
    snapshot) pre_snapshot ;;
    rollback) 
        echo "Available snapshots:"
        sudo snapper -c root list | tail -20
        echo ""
        echo "To rollback: sudo snapper -c root undochange <pre_num>..<post_num>"
        ;;
    status)
        echo "=== Recent snapshots ==="
        sudo snapper -c root list | tail -10
        echo ""
        echo "=== Update log ==="
        tail -20 /var/log/halo-update.log 2>/dev/null
        ;;
    *) echo "Usage: $0 {update|snapshot|rollback|status}" ;;
esac
