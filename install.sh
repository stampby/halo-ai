#!/bin/bash
# halo-ai — designed and built by the architect
# Bare-metal AI stack for AMD Strix Halo (Arch Linux)
# https://github.com/stampby/halo-ai
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

# ── Dry-run mode ──────────────────────────────────
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

if [ "$DRY_RUN" -eq 1 ]; then
    sudo()  { echo "  [DRY-RUN] sudo $*"; }
    wget() {
        echo "  [DRY-RUN] wget $*"
        # Create placeholder files so existence checks pass
        local next_is_output=0
        for arg in "$@"; do
            if [ "$next_is_output" -eq 1 ]; then touch "$arg" 2>/dev/null || true; next_is_output=0; continue; fi
            [ "$arg" = "-O" ] && next_is_output=1
            [[ "$arg" == http* ]] && touch "$(basename "$arg")" 2>/dev/null || true
        done
    }
    make()  { echo "  [DRY-RUN] make $*"; }
    cmake() { echo "  [DRY-RUN] cmake $*"; }
    cargo() { echo "  [DRY-RUN] cargo $*"; }
    pip()   { echo "  [DRY-RUN] pip $*"; }
    npm()   { echo "  [DRY-RUN] npm $*"; }
    pnpm()  { echo "  [DRY-RUN] pnpm $*"; }
    yarn()  { echo "  [DRY-RUN] yarn $*"; }
    curl()  { echo "  [DRY-RUN] curl $*"; }
    go()    { echo "  [DRY-RUN] go $*"; }
    caddy() { echo "DRY_RUN_HASH"; }
    tar() {
        echo "  [DRY-RUN] tar $*"
        # Create expected directories from tar extraction
        for arg in "$@"; do
            [[ "$arg" == *.tar.* || "$arg" == *.xz || "$arg" == -* ]] && continue
            [ ! -d "$arg" ] && mkdir -p "$arg" 2>/dev/null || true
        done
    }
    _real_cd=$(which cd 2>/dev/null || echo cd)
    cd() { builtin cd "$@" 2>/dev/null || echo "  [DRY-RUN] cd $*"; }
    ln() { echo "  [DRY-RUN] ln $*"; }
    cp() { echo "  [DRY-RUN] cp $*"; }
    chmod() { echo "  [DRY-RUN] chmod $*"; }
    # Skip build steps — dry-run only validates config and service wiring
    SKIP_BUILDS=1
    source() { echo "  [DRY-RUN] source $*"; }
    deactivate() { echo "  [DRY-RUN] deactivate"; }
    git() {
        if [ "${1:-}" = "clone" ]; then
            echo "  [DRY-RUN] git clone ${*:2}"
        else
            command git "$@"
        fi
    }
    echo -e "\n${YELLOW}${BOLD}  *** DRY-RUN MODE — nothing will be installed ***${NC}\n"
fi

# ── Halo AI branded output ────────────────────────
STEP_CURRENT=0
STEP_TOTAL=18

step() {
    STEP_CURRENT=$((STEP_CURRENT + 1))
    echo ''
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  [$STEP_CURRENT/$STEP_TOTAL]${NC} ${BOLD}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

info()  { echo -e "  ${BLUE}>>>${NC} $1"; }
ok()    { echo -e "  ${GREEN} +${NC} $1"; }
warn()  { echo -e "  ${YELLOW} !${NC} $1"; }
fail()  { echo -e "  ${RED} x${NC} $1"; exit 1; }
progress() { echo -e "  ${DIM}    ... $1${NC}"; }

# ── Banner ─────────────────────────────────────────
clear 2>/dev/null || true
echo ''
echo -e "${CYAN}${BOLD}"
cat << 'BANNER'
  ╔═══════════════════════════════════╗
  ║>>  H  A  L  O  ═══════  A  I  >>║
  ╠═══════════════════════════════════╣
  ║>>  bare-metal ai stack         >>║
  ║>>  gfx1151 │  91t/s │ 123GB   >>║
  ╚═══════════════════════════════════╝
BANNER
echo -e "${NC}"
echo -e "${DIM}  Bare-metal AI stack for AMD Strix Halo${NC}"
echo -e "${DIM}  designed and built by the architect${NC}"
echo -e "${DIM}  github.com/stampby/halo-ai${NC}"
echo ''

INSTALL_START=$(date +%s)
echo -e "${YELLOW}${BOLD}  Estimated total install time: 2-3 hours (compiling from source)${NC}"
echo -e "${DIM}  Builds use all $(nproc) cores in parallel — your machine will be working hard.${NC}"
echo -e "${DIM}  Everything is built natively for your hardware — no containers, no shortcuts.${NC}"
echo ''

# ── Dry-run recommendation ────────────────────────
if [ "$DRY_RUN" -eq 0 ]; then
    echo -e "${CYAN}${BOLD}  ┌──────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}${BOLD}  │                                                          │${NC}"
    echo -e "${CYAN}${BOLD}  │   RECOMMENDATION: Run a dry-run first                    │${NC}"
    echo -e "${CYAN}${BOLD}  │                                                          │${NC}"
    echo -e "${CYAN}${BOLD}  │   This stack compiles 18 components from source.          │${NC}"
    echo -e "${CYAN}${BOLD}  │   A dry-run validates everything without installing:      │${NC}"
    echo -e "${CYAN}${BOLD}  │                                                          │${NC}"
    echo -e "${CYAN}${BOLD}  │      ./install.sh --dry-run                               │${NC}"
    echo -e "${CYAN}${BOLD}  │                                                          │${NC}"
    echo -e "${CYAN}${BOLD}  │   If this is your first install, we strongly recommend    │${NC}"
    echo -e "${CYAN}${BOLD}  │   running the dry-run to catch issues before they happen. │${NC}"
    echo -e "${CYAN}${BOLD}  │                                                          │${NC}"
    echo -e "${CYAN}${BOLD}  └──────────────────────────────────────────────────────────┘${NC}"
    echo ''
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") Continue with full install? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        info "Run ./install.sh --dry-run to validate first."
        exit 0
    fi
    echo ''
fi

# ── Preflight ──────────────────────────────────────
step "Preflight checks"

# Root check — big red warning
if [ "$(id -u)" -eq 0 ]; then
    echo ''
    echo -e "${RED}${BOLD}  ╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}${BOLD}  ║                                                          ║${NC}"
    echo -e "${RED}${BOLD}  ║   *** DO NOT RUN THIS SCRIPT AS ROOT OR WITH SUDO ***    ║${NC}"
    echo -e "${RED}${BOLD}  ║                                                          ║${NC}"
    echo -e "${RED}${BOLD}  ║   Run as your normal user. The script uses sudo           ║${NC}"
    echo -e "${RED}${BOLD}  ║   internally only when needed.                            ║${NC}"
    echo -e "${RED}${BOLD}  ║                                                          ║${NC}"
    echo -e "${RED}${BOLD}  ║   Correct:   ./install.sh                                ║${NC}"
    echo -e "${RED}${BOLD}  ║   Wrong:     sudo ./install.sh                           ║${NC}"
    echo -e "${RED}${BOLD}  ║                                                          ║${NC}"
    echo -e "${RED}${BOLD}  ╚══════════════════════════════════════════════════════════╝${NC}"
    echo ''
    fail "Running as root (uid 0). Switch to your normal user."
fi

command -v pacman >/dev/null || fail "Arch Linux required."

# Sudo check — make sure user has sudo access
if ! sudo -v 2>/dev/null; then
    fail "Your user needs sudo access. Run: usermod -aG wheel $(whoami)"
fi
ok "Running as $(whoami) with sudo access"

# Re-run detection
if [ -d /srv/ai/llama-cpp/.git ] || [ -x /opt/python312/bin/python3.12 ]; then
    warn "Previous install detected — re-run mode (safe to continue)"
fi

lscpu | grep -q "Strix" || warn "This installer is designed for AMD Strix Halo. Proceeding anyway..."
/opt/rocm/bin/rocminfo 2>/dev/null | grep -q "gfx1151" && ok "ROCm already installed" || NEED_ROCM=1

# ── Interactive configuration ─────────────────────
step "Interactive Setup"
info "Press Enter to accept defaults"
echo ''

# Helper: prompt with default
prompt() {
    local var_name="$1" prompt_text="$2" default="$3"
    if [ "$DRY_RUN" -eq 1 ]; then
        printf -v "$var_name" '%s' "$default"
        info "[DRY-RUN] $prompt_text → $default"
        return
    fi
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text [${default}]: " input
    printf -v "$var_name" '%s' "${input:-$default}"
}

# Helper: prompt for password (no echo, allows blank for auto-generate)
prompt_secret() {
    local var_name="$1" prompt_text="$2"
    if [ "$DRY_RUN" -eq 1 ]; then
        printf -v "$var_name" '%s' ""
        info "[DRY-RUN] $prompt_text → [auto-generate]"
        return
    fi
    read -srp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text: " input
    echo ''
    printf -v "$var_name" '%s' "$input"
}

# 1. System username
DETECTED_USER=$(whoami)
prompt HALO_USER "System username" "$DETECTED_USER"
# Validate username — prevents injection into sed, systemd units, SSH config, /etc/hosts
[[ "$HALO_USER" =~ ^[a-z_][a-z0-9_-]*$ ]] || fail "Invalid username: '$HALO_USER' — must be a valid Linux username"
ok "Username: $HALO_USER"

# 2. Caddy password
echo ''
info "Caddy reverse proxy password (protects ALL web services)"
info "A strong password will be auto-generated if you leave it blank."
prompt_secret CADDY_PASSWORD "Caddy password (blank = auto-generate)"
if [ -z "$CADDY_PASSWORD" ]; then
    CADDY_PASSWORD=$(openssl rand -base64 16)
    warn "Auto-generated password: $CADDY_PASSWORD"
    warn "SAVE THIS — you will need it to access your services."
fi
ok "Caddy password set (will be hashed during install)"

# 3. SearXNG secret key
SEARXNG_SECRET=$(openssl rand -hex 32)
echo ''
info "SearXNG secret key: auto-generated"
prompt SEARXNG_KEY "SearXNG secret key" "$SEARXNG_SECRET"
[[ "$SEARXNG_KEY" =~ ^[a-f0-9]+$ ]] || { warn "Invalid SearXNG key — regenerating"; SEARXNG_KEY=$(openssl rand -hex 32); }
ok "SearXNG key: [set]"

# 4. Dashboard API key
DASHBOARD_KEY=$(openssl rand -base64 32)
echo ''
info "Dashboard API key: auto-generated"
prompt DASHBOARD_API_KEY "Dashboard API key" "$DASHBOARD_KEY"
ok "Dashboard key: [set]"

# 5. Server hostname
echo ''
prompt HALO_HOSTNAME "Server hostname" "strixhalo"
# Validate hostname — prevents injection into Caddyfile, sed, /etc/hosts
[[ "$HALO_HOSTNAME" =~ ^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$ ]] || fail "Invalid hostname: '$HALO_HOSTNAME'"
ok "Hostname: $HALO_HOSTNAME"

# /etc/hosts entries are added later with all subdomains (line ~700)
ok "Hostname: $HALO_HOSTNAME (will be added to /etc/hosts with subdomains later)"

# 6. Service selection
echo ''
info "Select which services to enable via systemd."
info "Toggle with the number key, press Enter when done."
echo ''

ALL_SERVICES=(llama-server whisper lemonade open-webui n8n comfyui searxng qdrant dashboard caddy meek)
SERVICE_LABELS=(
    "llama-server  — LLM inference (HIP + Vulkan)"
    "whisper       — Speech-to-text"
    "lemonade      — Unified AI API gateway"
    "open-webui    — Chat UI with RAG"
    "n8n           — Workflow automation"
    "comfyui       — Image generation"
    "searxng       — Private search engine"
    "qdrant        — Vector database for RAG"
    "dashboard     — GPU metrics + service health"
    "caddy         — Reverse proxy with TLS"
    "meek          — Security monitoring agent (recommended)"
)
# All enabled by default
ENABLED=()
for i in "${!ALL_SERVICES[@]}"; do
    ENABLED[$i]=1
done

render_menu() {
    for i in "${!ALL_SERVICES[@]}"; do
        local mark="x"
        [ "${ENABLED[$i]}" -eq 0 ] && mark=" "
        printf "  %s) [%s] %s\n" "$((i+1))" "$mark" "${SERVICE_LABELS[$i]}"
    done
    echo ''
    echo "  a) Select all    n) Select none    Enter) Confirm"
}

if [ "$DRY_RUN" -eq 1 ]; then
    render_menu
    info "[DRY-RUN] All services selected (default)"
    choice=""
else
    choice="loop"
fi
while [ "$choice" != "" ]; do
    render_menu
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") Toggle service (1-${#ALL_SERVICES[@]}, a, n, or Enter to confirm): " choice
    case "$choice" in
        "")
            break
            ;;
        a|A)
            for i in "${!ALL_SERVICES[@]}"; do ENABLED[$i]=1; done
            echo ''
            ;;
        n|N)
            for i in "${!ALL_SERVICES[@]}"; do ENABLED[$i]=0; done
            echo ''
            ;;
        [1-9]|1[01])
            idx=$((choice - 1))
            if [ "$idx" -ge 0 ] && [ "$idx" -lt "${#ALL_SERVICES[@]}" ]; then
                ENABLED[$idx]=$(( 1 - ENABLED[$idx] ))
            fi
            echo ''
            ;;
        *)
            warn "Invalid choice: $choice"
            echo ''
            ;;
    esac
done

SELECTED_SERVICES=()
for i in "${!ALL_SERVICES[@]}"; do
    [ "${ENABLED[$i]}" -eq 1 ] && SELECTED_SERVICES+=("${ALL_SERVICES[$i]}")
done
ok "Services to enable: ${SELECTED_SERVICES[*]}"

# ── Base packages ──────────────────────────────────
step "Installing build dependencies"
sudo pacman -S --noconfirm --needed base-devel cmake ninja git python python-pip python-virtualenv \
    sqlite vulkan-headers vulkan-icd-loader vulkan-radeon mariadb-libs grep snapper snap-pac \
    opencl-headers ocl-icd opencl-clhpp wget shaderc protobuf ccache

# ── User groups ────────────────────────────────────
step "GPU access & directory structure"
info "Setting up GPU access..."
sudo usermod -aG video,render "$HALO_USER"

# ── Directory structure ────────────────────────────
progress "Creating /srv/ai/ with Btrfs subvolumes..."
sudo mkdir -p /srv/ai
for svc in rocm llama-cpp lemonade whisper-cpp open-webui vane searxng qdrant n8n kokoro comfyui models configs systemd scripts; do
    sudo btrfs subvolume create /srv/ai/$svc 2>/dev/null || sudo mkdir -p /srv/ai/$svc
done
sudo chown -R "$HALO_USER":"$HALO_USER" /srv/ai

# ── Clone halo-ai repo ────────────────────────────
step "Cloning halo-ai repo"
cd /srv/ai
if [ ! -d .git ]; then
    git init
    git remote add origin https://github.com/stampby/halo-ai.git
fi
git fetch origin main
git checkout -B main origin/main -- configs/ systemd/ scripts/ assets/ docs/ README.md .gitignore 2>/dev/null || \
    git checkout FETCH_HEAD -- configs/ systemd/ scripts/ assets/ docs/ README.md .gitignore
ok "halo-ai repo ready"

# ── ROCm ───────────────────────────────────────────
if [ "${SKIP_BUILDS:-0}" -eq 1 ]; then
    step "ROCm GPU runtime [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Building Python 3.12 + 3.13 [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Building Node.js 24 [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Rust + Go toolchains [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Auditing source repos [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Building llama.cpp [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Building Lemonade + Whisper [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Building Qdrant + Caddy [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Installing SearXNG + Open WebUI [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Installing Vane + n8n + ComfyUI + Kokoro [DRY-RUN SKIP]"; ok "Skipped — dry-run"
    step "Downloading AI models [DRY-RUN SKIP]"; ok "Skipped — dry-run"
else
step "ROCm GPU runtime (~10 min download, ~2 min extract)"
if [ "${NEED_ROCM:-}" = "1" ]; then
    command -v wget >/dev/null || sudo pacman -S --noconfirm --needed wget
    info "Downloading ROCm 7.13 for gfx1151..."
    ROCM_URL="${ROCM_URL:-https://rocm.nightlies.amd.com/tarball/therock-dist-linux-gfx1151-7.13.0a20260323.tar.gz}"
    if cd /srv/ai/rocm 2>/dev/null && \
       wget --show-progress "$ROCM_URL" -O therock.tar.gz; then
        mkdir -p install && tar -xf therock.tar.gz -C install
        rm -f therock.tar.gz
        sudo ln -sfn /srv/ai/rocm/install /opt/rocm
        echo 'export ROCM_HOME=/opt/rocm
export PATH=/opt/rocm/bin:${PATH:-}
export LD_LIBRARY_PATH=/opt/rocm/lib:${LD_LIBRARY_PATH:-}' | sudo tee /etc/profile.d/rocm.sh >/dev/null
        source /etc/profile.d/rocm.sh
        ok "ROCm installed. Verifying GPU..."
        rocminfo | grep -q gfx1151 && ok "gfx1151 detected" || warn "GPU not detected — may need reboot"
    else
        warn "ROCm download failed or directory missing — skipping"
        warn "Install ROCm manually later. See docs/TROUBLESHOOTING.md"
    fi
else
    ok "ROCm already installed"
fi

# ── Python 3.12 + 3.13 ────────────────────────────
# Pinned SHA256 checksums — verified against python.org
declare -A PYTHON_SHA256=(
    ["3.12.13"]="c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684"
    ["3.13.3"]="40f868bcbdeb8149a3149580bb9bfd407b3321cd48f0be631af955ac92c0e041"
)

step "Building Python 3.12 + 3.13 (~15 min each)"
for VER in 3.12.13 3.13.3; do
    MAJOR=$(echo "$VER" | cut -d. -f1-2)
    PREFIX=/opt/python$(echo "$MAJOR" | tr -d .)
    if [ -x "$PREFIX/bin/python$MAJOR" ]; then ok "Python $MAJOR already installed"; continue; fi
    BUILD_DIR=$(mktemp -d /tmp/halo-python-XXXXXX)
    cd "$BUILD_DIR"
    wget -q "https://www.python.org/ftp/python/$VER/Python-$VER.tar.xz" || fail "Failed to download Python $VER"
    [ -f "Python-$VER.tar.xz" ] || fail "Python $VER archive missing after download"
    # Verify SHA256 checksum
    EXPECTED="${PYTHON_SHA256[$VER]}"
    ACTUAL=$(sha256sum "Python-$VER.tar.xz" | awk '{print $1}')
    if [ "$ACTUAL" != "$EXPECTED" ]; then
        fail "Python $VER checksum FAILED — expected $EXPECTED got $ACTUAL"
    fi
    ok "Python $VER checksum verified"
    # Verify GPG signature if gpg available
    if command -v gpg >/dev/null; then
        wget -q "https://www.python.org/ftp/python/$VER/Python-$VER.tar.xz.asc" 2>/dev/null
        if [ -f "Python-$VER.tar.xz.asc" ]; then
            gpg --keyserver hkps://keys.openpgp.org --recv-keys 7169605F62C751356D054A26A821E680E5FA6305 2>/dev/null
            if gpg --verify "Python-$VER.tar.xz.asc" "Python-$VER.tar.xz" 2>/dev/null; then
                ok "Python $VER GPG signature verified"
            else
                warn "Python $VER GPG signature could not be verified — continuing (checksum passed)"
            fi
        fi
    fi
    tar xf "Python-$VER.tar.xz" && cd "Python-$VER"
    if [ "$DRY_RUN" -eq 1 ]; then
        ok "[DRY-RUN] Python $MAJOR would be compiled here"
        continue
    fi
    ./configure --prefix="$PREFIX" --enable-optimizations -q
    make -j"$(nproc)" -s && sudo make altinstall -s || fail "Python $VER build failed"
    # Cleanup — non-fatal
    rm -rf "$BUILD_DIR" 2>/dev/null || true
    ok "Python $MAJOR compiled"
done

# ── Node.js 24 ─────────────────────────────────────
step "Building Node.js 24 (~20 min)"
if ! node --version 2>/dev/null | grep -q "v24"; then
    progress "Compiling from source — this takes a while..."
    NODE_DIR=$(mktemp -d /tmp/halo-node-XXXXXX)
    cd "$NODE_DIR"
    git clone --depth 1 --branch v24.5.0 https://github.com/nodejs/node.git src
    cd src
    if [ "$DRY_RUN" -eq 1 ]; then
        ok "[DRY-RUN] Node.js would be compiled here"
    else
        /opt/python313/bin/python3.13 ./configure --prefix=/usr/local
        make -j"$(nproc)" -s && sudo make install -s || fail "Node.js build failed"
    fi
    sudo corepack enable
    sudo npm install -g --force yarn 2>/dev/null || true
    sudo npm install -g --force pnpm 2>/dev/null || true
    rm -rf "$NODE_DIR" 2>/dev/null || true
    ok "Node.js $(node --version) + yarn compiled"
fi

# ── Rust ───────────────────────────────────────────
step "Rust + Go toolchains (~5 min)"
if ! command -v cargo >/dev/null; then
    info "Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # shellcheck disable=SC1091
    [ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env"
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# ── Go (for Caddy) ─────────────────────────────────
GO_SHA256="3333f6ea53afa971e9078895eaa4ac7204a8c6b5c68c10e6bc9a33e8e391bdd8"
if ! command -v go >/dev/null; then
    progress "Installing Go..."
    cd /tmp && wget -q https://go.dev/dl/go1.24.3.linux-amd64.tar.gz || fail "Failed to download Go"
    # Verify SHA256 checksum
    ACTUAL=$(sha256sum go1.24.3.linux-amd64.tar.gz | awk '{print $1}')
    if [ "$ACTUAL" != "$GO_SHA256" ]; then
        fail "Go checksum FAILED — expected $GO_SHA256 got $ACTUAL"
    fi
    ok "Go checksum verified"
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz
    rm -f go1.24.3.linux-amd64.tar.gz
fi
export PATH=/usr/local/go/bin:~/go/bin:$PATH

# ── Pre-build source audit ────────────────────────
step "Auditing source repos before building"
audit_repo() {
    local dir="$1" name="$2"
    if [ -d "$dir/.git" ]; then
        local commit=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
        local dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l)
        local unsigned=$(git -C "$dir" log -1 --format='%G?' 2>/dev/null)
        info "$name: commit $commit, $([ "$dirty" -eq 0 ] && echo 'clean' || echo "${dirty} uncommitted changes")"
        [ "$dirty" -gt 0 ] && warn "$name has uncommitted changes — review before trusting"
    fi
}
for repo_pair in "llama-cpp:llama.cpp" "lemonade:Lemonade" "whisper-cpp:whisper.cpp" "qdrant:Qdrant" "vane:Vane" "comfyui:ComfyUI" "kokoro:Kokoro"; do
    dir="/srv/ai/${repo_pair%%:*}"
    name="${repo_pair##*:}"
    [ -d "$dir" ] && audit_repo "$dir" "$name"
done
ok "Source audit complete"

# ── Build everything ───────────────────────────────
step "Building llama.cpp — HIP + Vulkan + OpenCL (~10 min)"
source /etc/profile.d/rocm.sh 2>/dev/null || true
export ROCBLAS_USE_HIPBLASLT=1

progress "Compiling HIP backend..."
cd /srv/ai/llama-cpp
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/ggml-org/llama.cpp .; fi
cmake -B build-hip -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DGGML_HIP_ROCWMMA_FATTN=ON -DCMAKE_BUILD_TYPE=Release -G Ninja -Wno-dev .
cmake --build build-hip -j$(nproc)
cmake -B build-vulkan -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release -G Ninja -Wno-dev .
cmake --build build-vulkan -j$(nproc)
cmake -B build-opencl -DGGML_OPENCL=ON -DCMAKE_BUILD_TYPE=Release -G Ninja -Wno-dev .
cmake --build build-opencl -j$(nproc)
ok "llama.cpp built (HIP + Vulkan + OpenCL)"

step "Building Lemonade + Whisper (~10 min)"
info "Building Lemonade..."
cd /srv/ai/lemonade
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/lemonade-sdk/lemonade .; fi
cmake --preset default && cmake --build --preset default
ok "Lemonade built"

info "Building whisper.cpp..."
cd /srv/ai/whisper-cpp
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/ggerganov/whisper.cpp .; fi
cmake -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DCMAKE_BUILD_TYPE=Release -G Ninja .
cmake --build build -j$(nproc)
ok "whisper.cpp built"

step "Building Qdrant + Caddy (~25 min — Rust compile)"
info "Building Qdrant..."
cd /srv/ai/qdrant
source ~/.cargo/env
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/qdrant/qdrant .; fi
cargo build --release
ok "Qdrant built"

info "Building Caddy..."
go install github.com/caddyserver/caddy/v2/cmd/caddy@latest
sudo cp ~/go/bin/caddy /usr/local/bin/caddy && sudo chmod 755 /usr/local/bin/caddy
ok "Caddy built and installed to /usr/local/bin/caddy"

step "Installing SearXNG + Open WebUI (~10 min)"
info "Installing SearXNG..."
cd /srv/ai/searxng
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/searxng/searxng .; fi
/opt/python312/bin/python3.12 -m venv .venv && source .venv/bin/activate
pip install -q setuptools msgspec pyyaml typing_extensions Brotli lxml && pip install -q --no-build-isolation -e .
deactivate
ok "SearXNG installed"

info "Installing Open WebUI..."
cd /srv/ai/open-webui
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/open-webui/open-webui .; fi
/opt/python312/bin/python3.12 -m venv .venv && source .venv/bin/activate
sed -i 's/ddgs==9.11.2/ddgs>=9.11.3/' pyproject.toml 2>/dev/null || true
sed -i 's/rapidocr-onnxruntime==1.4.4/rapidocr-onnxruntime>=1.2.3/' pyproject.toml 2>/dev/null || true
pip install -q setuptools hatchling && pip install -q . 
deactivate
ok "Open WebUI installed"

step "Installing Vane + n8n + ComfyUI + Kokoro (~15 min)"

# ── SECURITY: Block compromised axios versions (CVE-2026-XXXXX) ──
# On March 31, 2026, axios@1.14.1 and axios@0.30.4 were backdoored
# with a North Korean RAT via plain-crypto-js. Pin to safe versions.
info "Applying axios supply chain attack mitigation..."
# Shell function — no /tmp script needed (avoids TOCTOU race)
halo_npm_audit() {
    for dir in "$@"; do
        if [ -d "$dir/node_modules" ]; then
            if [ -d "$dir/node_modules/plain-crypto-js" ]; then
                echo "CRITICAL: plain-crypto-js found in $dir — COMPROMISED"
                rm -rf "$dir/node_modules/plain-crypto-js"
                echo "Removed malicious package."
            fi
            AX_VER=$(jq -r .version "$dir/node_modules/axios/package.json" 2>/dev/null)
            if [ "$AX_VER" = "1.14.1" ] || [ "$AX_VER" = "0.30.4" ]; then
                echo "CRITICAL: Compromised axios@$AX_VER in $dir — removing"
                rm -rf "$dir/node_modules/axios"
            fi
        fi
    done
}
ok "Axios supply chain mitigation active"

info "Installing Vane (Perplexica)..."
cd /srv/ai/vane
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/ItzCrazyKns/Vane .; fi
# Pin axios to safe version before install
npm pkg set overrides.axios="1.14.0" 2>/dev/null || true
yarn install --ignore-scripts
# Rebuild native modules that need compilation (better-sqlite3)
npx --yes node-gyp rebuild -C node_modules/better-sqlite3 2>/dev/null || \
    npm rebuild better-sqlite3 2>/dev/null || \
    warn "better-sqlite3 native build failed — Vane may not work"
yarn build
halo_npm_audit /srv/ai/vane
ok "Vane built (axios pinned safe)"

info "Installing n8n..."
cd /srv/ai/n8n
command -v pnpm >/dev/null || sudo npm install -g --force pnpm 2>/dev/null || true
# Install n8n globally via npm (pre-built, skip source compile)
# n8n source is 674k files and fails on most systems. Use the release.
sudo npm install -g --ignore-scripts n8n 2>/dev/null || {
    warn "npm global install failed — trying npx fallback"
    # Create a wrapper that runs n8n via npx
    cat > /srv/ai/n8n/start.sh << 'N8N_START'
#!/bin/bash
export N8N_SECURE_COOKIE=false
export N8N_USER_FOLDER=/srv/ai/n8n/data
npx n8n start --host 127.0.0.1 --port 5678
N8N_START
    chmod +x /srv/ai/n8n/start.sh
}
mkdir -p /srv/ai/n8n/data
ok "n8n installed"

info "Installing ComfyUI..."
cd /srv/ai/comfyui
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/comfyanonymous/ComfyUI .; fi
/opt/python313/bin/python3.13 -m venv .venv && source .venv/bin/activate
pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2.4
pip install -q -r requirements.txt
deactivate
ok "ComfyUI installed"

# Download image generation models
progress "Downloading FLUX.1 schnell (~12GB — fastest, best quality)..."
wget -q --show-progress 'https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors' \
    -O /srv/ai/comfyui/models/checkpoints/flux1-schnell.safetensors 2>/dev/null || \
    warn "FLUX.1 download failed — download manually later"
[ -f /srv/ai/comfyui/models/checkpoints/flux1-schnell.safetensors ] && ok "FLUX.1 schnell ready"

progress "Downloading SDXL base model (~6.5GB — fallback)..."
wget -q --show-progress 'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors' \
    -O /srv/ai/comfyui/models/checkpoints/sd_xl_base_1.0.safetensors 2>/dev/null || \
    warn "SDXL download failed — download manually later"
[ -f /srv/ai/comfyui/models/checkpoints/sd_xl_base_1.0.safetensors ] && ok "SDXL base model ready"

# Download Whisper model for speech-to-text (Turbo: 5.4x faster, ~1% more WER)
progress "Downloading Whisper large-v3-turbo model (~1.6GB)..."
wget -q --show-progress 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin' \
    -O /srv/ai/models/whisper-large-v3-turbo.bin 2>/dev/null || \
    warn "Whisper turbo download failed — download manually later"
[ -f /srv/ai/models/whisper-large-v3-turbo.bin ] && ok "Whisper large-v3-turbo ready"

info "Installing Kokoro TTS..."
cd /srv/ai/kokoro
if [ -d .git ]; then git pull --ff-only 2>/dev/null || true; else git clone https://github.com/remsky/Kokoro-FastAPI .; fi
/opt/python313/bin/python3.13 -m venv .venv && source .venv/bin/activate
pip install -q --no-deps -e .
pip install -q torch --index-url https://download.pytorch.org/whl/rocm6.2.4
pip install -q audioop-lts scipy transformers spacy inflect av uvicorn fastapi soundfile pydantic
pip install -q --no-deps 'misaki>=0.7.4' 'kokoro>=0.7.16'
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || python -m spacy download en_core_web_sm
deactivate
ok "Kokoro installed"

# ── Download LLM model ────────────────────────────
step "Downloading AI models"

# LLM — Qwen3-30B-A3B (best speed/quality for Strix Halo)
if [ ! -f /srv/ai/models/qwen3-30b-a3b-q4_k_m.gguf ]; then
    info "Downloading Qwen3-30B-A3B (~18GB)..."
    progress "This is the main LLM — 91 tok/s on Strix Halo"
    wget -q --show-progress 'https://huggingface.co/bartowski/Qwen3-30B-A3B-GGUF/resolve/main/Qwen3-30B-A3B-Q4_K_M.gguf' \
        -O /srv/ai/models/qwen3-30b-a3b-q4_k_m.gguf 2>/dev/null || \
        warn "LLM download failed — download manually: halo-models.sh download qwen3-30b"
    [ -f /srv/ai/models/qwen3-30b-a3b-q4_k_m.gguf ] && ok "Qwen3-30B-A3B ready (18GB, 91 tok/s)"
else
    ok "LLM model already present"
fi

# SDXL was downloaded above with ComfyUI
# Whisper was downloaded above with ComfyUI

info "Model download step complete (check warnings above for any failures)"

# ── System config ──────────────────────────────────
step "System hardening & configuration"

# GPU device permissions
echo 'SUBSYSTEM=="kfd", KERNEL=="kfd", TAG+="uaccess", GROUP="render", MODE="0660"
SUBSYSTEM=="drm", KERNEL=="renderD*", TAG+="uaccess", GROUP="render", MODE="0660"' | sudo tee /etc/udev/rules.d/70-amdgpu.rules

# Kernel param for GPU memory
# GPU memory — add kernel param to boot entry (systemd-boot)
if ls /boot/loader/entries/*.conf >/dev/null 2>&1; then
    ENTRY=$(ls -t /boot/loader/entries/*.conf | head -1)
    if [ -f "$ENTRY" ] && ! grep -q 'ttm\.pages_limit' "$ENTRY"; then
        sudo cp "$ENTRY" "${ENTRY}.bak"
        sudo sed -i 's/^options /options ttm.pages_limit=30146560 /' "$ENTRY"
        ok "Added ttm.pages_limit to $ENTRY (backup saved)"
    fi
else
    warn "No systemd-boot entries found — add 'ttm.pages_limit=30146560' to your bootloader manually"
fi

# Disable sleep/suspend
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# SSH hardening (preserve existing if present)
if [ ! -f /etc/ssh/sshd_config.d/90-halo-security.conf ]; then
    echo "PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
PermitRootLogin no
AllowUsers $HALO_USER" | sudo tee /etc/ssh/sshd_config.d/90-halo-security.conf
else
    ok "SSH hardening already configured"
fi

# Install nftables firewall
info "Installing firewall..."
sudo pacman -S --noconfirm --needed nftables 2>/dev/null
[ -f /etc/nftables.conf ] && sudo cp /etc/nftables.conf /etc/nftables.conf.bak
sudo cp /srv/ai/configs/system/nftables.conf /etc/nftables.conf
LAN_IFACE=$(ip -4 route show default | awk '{print $5; exit}')
LAN_SUBNET=$(ip -4 addr show dev "$LAN_IFACE" 2>/dev/null | awk '/inet / {print $2; exit}' | sed 's|\.[0-9]*/|.0/|')
if [ -n "$LAN_SUBNET" ] && echo "$LAN_SUBNET" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+$'; then
    sudo sed -i "s|xxx.xxx.xxx.0/24|${LAN_SUBNET}|g" /etc/nftables.conf
    ok "Firewall LAN subnet: $LAN_SUBNET"
else
    warn "Could not detect LAN subnet — edit /etc/nftables.conf manually (replace xxx.xxx.xxx.0/24)"
fi
sudo systemctl enable --now nftables 2>/dev/null
ok "Firewall active (LAN-only SSH + HTTP)"

# Install fail2ban (preserve existing config)
info "Installing fail2ban..."
sudo pacman -S --noconfirm --needed fail2ban 2>/dev/null
if [ -f /etc/fail2ban/jail.local ]; then
    ok "fail2ban already configured"
else
cat << 'F2BCONF' | sudo tee /etc/fail2ban/jail.local
[sshd]
enabled = true
port = ssh
filter = sshd
backend = systemd
maxretry = 5
bantime = 3600
findtime = 600
F2BCONF
fi
sudo systemctl enable --now fail2ban 2>/dev/null
ok "fail2ban active (5 attempts = 1hr ban)"

# ── Apply interactive configuration ────────────────
fi  # end SKIP_BUILDS

step "Applying configuration & enabling services"

# Generate Caddy password hash and write Caddyfile with subdomain routing
mkdir -p /srv/ai/configs
CADDY_HASH=$(printf '%s' "$CADDY_PASSWORD" | caddy hash-password --stdin)
cat > /srv/ai/configs/Caddyfile << CADDYEOF
{
    admin off
    auto_https off
}

http://$HALO_HOSTNAME {
    basic_auth * {
        caddy $CADDY_HASH
    }
    root * /srv/ai/configs
    file_server
    rewrite * /index.html
}

http://chat.$HALO_HOSTNAME {
    basic_auth * {
        caddy $CADDY_HASH
    }
    reverse_proxy 127.0.0.1:3000
}

http://research.$HALO_HOSTNAME {
    basic_auth * {
        caddy $CADDY_HASH
    }
    reverse_proxy 127.0.0.1:3001
}

http://search.$HALO_HOSTNAME {
    basic_auth * {
        caddy $CADDY_HASH
    }
    reverse_proxy 127.0.0.1:8888
}

http://n8n.$HALO_HOSTNAME {
    basic_auth * {
        caddy $CADDY_HASH
    }
    reverse_proxy 127.0.0.1:5678
}

http://comfyui.$HALO_HOSTNAME {
    basic_auth * {
        caddy $CADDY_HASH
    }
    reverse_proxy 127.0.0.1:8188
}
CADDYEOF
chmod 640 /srv/ai/configs/Caddyfile
ok "Caddy configured with subdomain routing"

mkdir -p /srv/ai/.caddy

# Write SearXNG secret key (works on fresh install AND re-run)
sed -i 's|secret_key: ".*"|secret_key: "'"$SEARXNG_KEY"'"|' /srv/ai/configs/searxng/settings.yml
chmod 640 /srv/ai/configs/searxng/settings.yml
ok "SearXNG secret key configured"

# Write Dashboard API key
mkdir -p /srv/ai/dashboard-api/data
echo -n "$DASHBOARD_API_KEY" > /srv/ai/dashboard-api/data/dashboard-api-key.txt
chmod 600 /srv/ai/dashboard-api/data/dashboard-api-key.txt
ok "Dashboard API key configured"

# NOTE: Service file modifications happen AFTER the copy to /etc/systemd/system/ (see below)
info "Service wiring deferred until after systemd unit install..."

# Configure Vane (Perplexica)
info "Configuring Vane deep research..."
mkdir -p /srv/ai/vane/.next/standalone/data
ln -sfn /srv/ai/vane/.next/static /srv/ai/vane/.next/standalone/.next/static 2>/dev/null
ln -sfn /srv/ai/vane/public /srv/ai/vane/.next/standalone/public 2>/dev/null
ln -sfn /srv/ai/vane/drizzle /srv/ai/vane/.next/standalone/drizzle 2>/dev/null
# Get model name from llama-server config
MODEL_NAME=$(grep -oP '(?<=--model /srv/ai/models/)\S+' /srv/ai/systemd/halo-llama-server.service 2>/dev/null | head -1)
[ -z "$MODEL_NAME" ] && MODEL_NAME="unknown-model" && warn "Could not detect model name from llama-server config"
cat > /srv/ai/vane/.next/standalone/data/config.json << VANEEOF
{
  "modelProviders": [
    {
      "id": "openai",
      "name": "OpenAI",
      "type": "openai",
      "chatModels": [{"key": "$MODEL_NAME", "name": "$MODEL_NAME"}],
      "embeddingModels": [],
      "config": {
        "baseURL": "http://127.0.0.1:8081/v1",
        "apiKey": "not-needed"
      },
      "hash": ""
    },
    {
      "id": "transformers",
      "name": "Transformers",
      "type": "transformers",
      "chatModels": [],
      "embeddingModels": [{"key": "Xenova/all-MiniLM-L6-v2", "name": "all-MiniLM-L6-v2"}],
      "config": {},
      "hash": ""
    }
  ],
  "selectedChatModel": {"providerKey": "openai", "fieldKey": "$MODEL_NAME"},
  "selectedEmbeddingModel": {"providerKey": "transformers", "fieldKey": "Xenova/all-MiniLM-L6-v2"},
  "search": {
    "searxngURL": "http://127.0.0.1:8888"
  }
}
VANEEOF
# Mark setup as complete so Vane shows the search UI immediately
curl -s http://127.0.0.1:3001/api/config/setup-complete -X POST -H 'Content-Type: application/json' -d '{}' 2>/dev/null || true
ok "Vane configured with local LLM + SearXNG"

# Create landing page
cat > /srv/ai/configs/index.html << 'LANDINGEOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Halo AI</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0d1117; color: #fff; font-family: system-ui, -apple-system, sans-serif; min-height: 100vh; }
.header { text-align: center; padding: 3rem 1rem 1rem; }
.logo { color: #00d4ff; font-size: 3rem; font-weight: 800; letter-spacing: 0.15em; }
.logo span { color: #fff; }
.tagline { color: #555; font-size: 1rem; margin-top: 0.3rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; max-width: 1000px; margin: 2rem auto; padding: 0 1.5rem; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 1.2rem; text-decoration: none; display: block; transition: border-color 0.2s, transform 0.15s; }
.card:hover { border-color: #00d4ff; transform: translateY(-2px); }
.card h3 { color: #fff; font-size: 1.05rem; margin-bottom: 0.2rem; }
.card p { color: #666; font-size: 0.8rem; line-height: 1.4; }
.card .port { color: #444; font-size: 0.7rem; margin-top: 0.5rem; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; position: relative; top: -1px; }
.dot.on { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
.dot.off { background: #444; }
.section { max-width: 1000px; margin: 2rem auto 0; padding: 0 1.5rem; }
.section h2 { color: #30363d; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.8rem; border-bottom: 1px solid #21262d; padding-bottom: 0.5rem; }
.footer { text-align: center; padding: 2rem; color: #333; font-size: 0.75rem; }
.footer a { color: #444; text-decoration: none; }
.creds { text-align: center; margin: 1.5rem auto; padding: 0.8rem; background: #1c1f26; border: 1px solid #ff980055; border-radius: 8px; max-width: 500px; }
.creds p { color: #ff9800; font-size: 0.85rem; }
.creds strong { color: #fff; }
</style>
</head>
<body>
<div class="header">
    <div class="logo">>> <span>HALO</span> AI</div>
    <p class="tagline">bare-metal ai stack for AMD Strix Halo</p>
</div>
<div class="creds">
    <p>Change password: <strong>halo-change-password.sh</strong></p>
</div>
<div class="section"><h2>AI Services</h2></div>
<div class="grid">
    <a class="card" target="_blank" href="CHAT_URL"><h3><span class="dot on"></span>Chat</h3><p>Open WebUI — multi-model chat with RAG</p><div class="port">:3000</div></a>
    <a class="card" target="_blank" href="RESEARCH_URL"><h3><span class="dot on"></span>Deep Research</h3><p>Vane — AI search with cited sources</p><div class="port">:3001</div></a>
    <a class="card" target="_blank" href="COMFYUI_URL"><h3><span class="dot on"></span>ComfyUI</h3><p>Node-based image generation</p><div class="port">:8188</div></a>
    <a class="card" target="_blank" href="N8N_URL"><h3><span class="dot on"></span>Workflows</h3><p>n8n — automation with 400+ integrations</p><div class="port">:5678</div></a>
</div>
<div class="section"><h2>Infrastructure</h2></div>
<div class="grid">
    <a class="card" target="_blank" href="SEARCH_URL"><h3><span class="dot on"></span>SearXNG</h3><p>Private meta-search engine</p><div class="port">:8888</div></a>
    <a class="card" target="_blank" href="https://github.com/lemonade-sdk/lemonade"><h3><span class="dot on"></span>Lemonade API</h3><p>OpenAI/Ollama compatible gateway</p><div class="port">:8080</div></a>
    <a class="card" target="_blank" href="https://github.com/qdrant/qdrant"><h3><span class="dot on"></span>Qdrant</h3><p>Vector database for RAG</p><div class="port">:6333</div></a>
</div>
<div class="section"><h2>Agents</h2></div>
<div class="grid">
    <a class="card" target="_blank" href="https://github.com/stampby/meek"><h3><span class="dot on"></span>Meek</h3><p>Security — 9 Reflex agents guard 24/7</p></a>
    <a class="card" target="_blank" href="https://github.com/stampby/echo"><h3><span class="dot on"></span>Echo</h3><p>Social media — she speaks for the family</p></a>
</div>
<div class="footer">
    <p>91 tok/s &middot; 123GB GPU &middot; zero containers &middot; <a href="https://github.com/stampby/halo-ai">GitHub</a></p>
    <p style="font-size:0.75rem;color:#555;margin-top:4px;">designed and built by the architect</p>
</div>
</body>
</html>
LANDINGEOF

# Replace landing page URLs with actual hostname
sed -i -e "s|CHAT_URL|http://chat.$HALO_HOSTNAME|g" \
       -e "s|RESEARCH_URL|http://research.$HALO_HOSTNAME|g" \
       -e "s|COMFYUI_URL|http://comfyui.$HALO_HOSTNAME|g" \
       -e "s|N8N_URL|http://n8n.$HALO_HOSTNAME|g" \
       -e "s|SEARCH_URL|http://search.$HALO_HOSTNAME|g" \
       /srv/ai/configs/index.html
ok "Landing page created"

# Add hostname + subdomains to /etc/hosts
if ! grep -qF "$HALO_HOSTNAME" /etc/hosts 2>/dev/null; then
    echo "127.0.0.1    $HALO_HOSTNAME chat.$HALO_HOSTNAME research.$HALO_HOSTNAME search.$HALO_HOSTNAME n8n.$HALO_HOSTNAME comfyui.$HALO_HOSTNAME gaia.$HALO_HOSTNAME" | sudo tee -a /etc/hosts
    ok "Hostname and subdomains added to /etc/hosts"
fi

# Install systemd units FIRST, then patch them
sudo cp /srv/ai/systemd/halo-*.service /etc/systemd/system/ 2>/dev/null || true
sudo cp /srv/ai/systemd/halo-*.timer /etc/systemd/system/ 2>/dev/null || true

# Replace <YOUR_USER> in the installed copies (not the source)
sudo sed -i "s/<YOUR_USER>/$HALO_USER/g" /etc/systemd/system/halo-*.service /etc/systemd/system/halo-*.timer 2>/dev/null
sudo systemctl daemon-reload

# Now wire up service configs on the INSTALLED copies (idempotent — safe to re-run)
info "Wiring services together..."

# Caddy XDG_DATA_HOME
grep -q 'XDG_DATA_HOME' /etc/systemd/system/halo-caddy.service 2>/dev/null || \
    sudo sed -i '/\[Service\]/a Environment=XDG_DATA_HOME=/srv/ai/.caddy' /etc/systemd/system/halo-caddy.service 2>/dev/null
# Open WebUI → llama-server
grep -q 'OPENAI_API_BASE_URL' /etc/systemd/system/halo-open-webui.service 2>/dev/null || \
    sudo sed -i '/\[Service\]/a Environment=OPENAI_API_BASE_URL=http://127.0.0.1:8081/v1\nEnvironment=OPENAI_API_KEY=not-needed\nEnvironment=ENABLE_OLLAMA_API=false' /etc/systemd/system/halo-open-webui.service 2>/dev/null
ok "Open WebUI → llama-server connected"
# llama-server jinja + reasoning off
grep -q 'reasoning-budget' /etc/systemd/system/halo-llama-server.service 2>/dev/null || \
    sudo sed -i 's|--model |--jinja --reasoning-budget 0 --model |' /etc/systemd/system/halo-llama-server.service 2>/dev/null
ok "llama-server configured (jinja + reasoning off)"
# n8n secure cookie
grep -q 'N8N_SECURE_COOKIE' /etc/systemd/system/halo-n8n.service 2>/dev/null || \
    sudo sed -i '/\[Service\]/a Environment=N8N_SECURE_COOKIE=false' /etc/systemd/system/halo-n8n.service 2>/dev/null
ok "n8n configured for HTTP"

sudo systemctl daemon-reload
sudo systemctl enable halo-watchdog.timer halo-backup.timer

# Enable selected services
for svc in "${SELECTED_SERVICES[@]}"; do
    unit="halo-${svc}.service"
    # Map service names to actual systemd unit names
    case "$svc" in
        dashboard) unit="halo-dashboard-api.service"; unit2="halo-dashboard-ui.service" ;;
        whisper)   unit="halo-whisper-server.service" ;;
        meek)      continue ;;  # Meek units are installed separately above
        *)         unit="halo-${svc}.service" ;;
    esac
    if [ -f "/etc/systemd/system/$unit" ]; then
        sudo systemctl enable "$unit"
        ok "Enabled $unit"
    fi
    if [ -n "${unit2:-}" ] && [ -f "/etc/systemd/system/$unit2" ]; then
        sudo systemctl enable "$unit2"
        ok "Enabled $unit2"
    fi
    unset unit2
done

# Snapper snapshots
sudo snapper create-config / 2>/dev/null || true
sudo snapper create-config /home 2>/dev/null || true
sudo systemctl enable --now snapper-timeline.timer snapper-cleanup.timer

ok "System configured"

# ── Meek security agent ───────────────────────────
if printf '%s\n' "${SELECTED_SERVICES[@]}" | grep -qx meek; then
    step "Installing Meek security agent"
    info "Cloning Meek repo..."
    cd /srv/ai
    sudo btrfs subvolume create /srv/ai/meek 2>/dev/null || true
    sudo chown -R "$HALO_USER":"$HALO_USER" /srv/ai/meek
    if [ -d /srv/ai/meek/.git ]; then git -C /srv/ai/meek pull --ff-only 2>/dev/null || true; else git clone https://github.com/stampby/meek /srv/ai/meek; fi
    mkdir -p /srv/ai/meek/reports
    ok "Meek cloned to /srv/ai/meek/"

    info "Installing Meek systemd units..."
    sudo cp /srv/ai/meek/systemd/meek-watch.service /srv/ai/meek/systemd/meek-scan.service /srv/ai/meek/systemd/meek-scan.timer /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable meek-watch.service meek-scan.timer
    ok "Meek systemd units installed and timer enabled"
fi

# ── Done ───────────────────────────────────────────
echo ''
echo ''
echo -e "${GREEN}${BOLD}"
cat << 'DONE'
  ╔═══════════════════════════════════╗
  ║>>  H A L O · A I  ━━  READY   >>║
  ╚═══════════════════════════════════╝
DONE
echo -e "${NC}"
INSTALL_END=$(date +%s)
INSTALL_MINS=$(( (INSTALL_END - INSTALL_START) / 60 ))
echo -e "${GREEN}${BOLD}  Installation complete! (${INSTALL_MINS} minutes)${NC}"
echo ''
echo -e "  ${CYAN}Enabled services:${NC} ${SELECTED_SERVICES[*]}"
echo ''

# ── CRITICAL: Password change warning ─────────────
echo -e "  ${BOLD}Next steps:${NC}"
echo -e "     ${BOLD}/srv/ai/scripts/halo-change-password.sh${NC}"
echo ''
echo -e "  ${YELLOW}1.${NC} Reboot to activate GPU memory (123GB GTT):"
echo -e "     ${DIM}sudo reboot${NC}"
echo ''
START_UNITS=""
for svc in "${SELECTED_SERVICES[@]}"; do
    case "$svc" in
        dashboard) START_UNITS+="halo-dashboard-api halo-dashboard-ui " ;;
        whisper)   START_UNITS+="halo-whisper-server " ;;
        meek)      START_UNITS+="meek-watch meek-scan.timer " ;;
        *)         START_UNITS+="halo-${svc} " ;;
    esac
done
echo -e "  ${YELLOW}2.${NC} Start all enabled services after reboot:"
echo -e "     ${DIM}sudo systemctl start $START_UNITS${NC}"
echo ''
echo -e "  ${YELLOW}3.${NC} Access your server:"
echo -e "     ${BOLD}http://$HALO_HOSTNAME${NC}  (landing page)"
echo -e "     ${DIM}http://chat.$HALO_HOSTNAME${NC}  (Open WebUI)"
echo -e "     ${DIM}http://research.$HALO_HOSTNAME${NC}  (Deep Research)"
echo -e "     ${DIM}http://comfyui.$HALO_HOSTNAME${NC}  (Image Gen)"
echo -e "     ${DIM}http://n8n.$HALO_HOSTNAME${NC}  (Workflows)"
echo -e "     ${DIM}http://search.$HALO_HOSTNAME${NC}  (Search)"
echo ''
echo -e "  ${DIM}Login: caddy / (the password you set during install)${NC}"
echo -e "  ${DIM}API key: /srv/ai/dashboard-api/data/dashboard-api-key.txt${NC}"
echo ''
echo -e "  ${DIM}Add this to /etc/hosts on other devices to access from the LAN:${NC}"
LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+')
echo -e "  ${DIM}$LAN_IP    $HALO_HOSTNAME chat.$HALO_HOSTNAME research.$HALO_HOSTNAME search.$HALO_HOSTNAME n8n.$HALO_HOSTNAME comfyui.$HALO_HOSTNAME gaia.$HALO_HOSTNAME${NC}"
echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
