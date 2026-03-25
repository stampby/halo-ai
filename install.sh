#!/bin/bash
# halo-ai installer for AMD Strix Halo (Arch Linux)
# Usage: curl -fsSL https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/install.sh | bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}[halo-ai]${NC} $1"; }
ok()    { echo -e "${GREEN}[halo-ai]${NC} $1"; }
warn()  { echo -e "${YELLOW}[halo-ai]${NC} $1"; }
fail()  { echo -e "${RED}[halo-ai]${NC} $1"; exit 1; }

# ── Preflight ──────────────────────────────────────
info "Checking system..."
[ "$(id -u)" -eq 0 ] && fail "Do not run as root. Run as your normal user (with sudo access)."
command -v pacman >/dev/null || fail "Arch Linux required."
lscpu | grep -q "Strix" || warn "This installer is designed for AMD Strix Halo. Proceeding anyway..."
grep -q "gfx1151" /opt/rocm/bin/rocminfo 2>/dev/null && ok "ROCm already installed" || NEED_ROCM=1

# ── Interactive configuration ─────────────────────
echo ''
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "  Interactive Setup — press Enter for defaults"
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ''

# Helper: prompt with default
prompt() {
    local var_name="$1" prompt_text="$2" default="$3"
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text [${default}]: " input
    eval "$var_name=\"${input:-$default}\""
}

# Helper: prompt for password (no echo)
prompt_secret() {
    local var_name="$1" prompt_text="$2"
    while true; do
        read -srp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text: " input
        echo ''
        if [ -n "$input" ]; then
            eval "$var_name=\"$input\""
            return
        fi
        warn "Password cannot be empty. Please try again."
    done
}

# 1. System username
DETECTED_USER=$(whoami)
prompt HALO_USER "System username" "$DETECTED_USER"
ok "Username: $HALO_USER"

# 2. Caddy password
echo ''
info "Caddy reverse proxy password (protects web access)"
prompt_secret CADDY_PASSWORD "Choose a Caddy password"
ok "Caddy password set (will be hashed during install)"

# 3. SearXNG secret key
SEARXNG_SECRET=$(openssl rand -hex 32)
echo ''
info "SearXNG secret key: auto-generated"
prompt SEARXNG_KEY "SearXNG secret key" "$SEARXNG_SECRET"
ok "SearXNG key: ${SEARXNG_KEY:0:16}..."

# 4. Dashboard API key
DASHBOARD_KEY=$(openssl rand -base64 32)
echo ''
info "Dashboard API key: auto-generated"
prompt DASHBOARD_API_KEY "Dashboard API key" "$DASHBOARD_KEY"
ok "Dashboard key: ${DASHBOARD_API_KEY:0:16}..."

# 5. Server hostname
echo ''
prompt HALO_HOSTNAME "Server hostname" "strixhalo"
ok "Hostname: $HALO_HOSTNAME"

# Add to /etc/hosts if not already present
if ! grep -q "$HALO_HOSTNAME" /etc/hosts 2>/dev/null; then
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") Add '127.0.0.1 $HALO_HOSTNAME' to /etc/hosts? [Y/n]: " add_hosts
    add_hosts="${add_hosts:-Y}"
    if [[ "$add_hosts" =~ ^[Yy]$ ]]; then
        echo "127.0.0.1    $HALO_HOSTNAME" | sudo tee -a /etc/hosts >/dev/null
        ok "Added $HALO_HOSTNAME to /etc/hosts"
    fi
fi

# 6. Service selection
echo ''
info "Select which services to enable via systemd."
info "Toggle with the number key, press Enter when done."
echo ''

ALL_SERVICES=(llama-server whisper lemonade open-webui n8n comfyui searxng qdrant dashboard caddy)
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

while true; do
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
        [1-9]|10)
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

echo ''
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "  Configuration complete — starting install"
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ''

# ── Base packages ──────────────────────────────────
info "Installing build dependencies..."
sudo pacman -S --noconfirm --needed base-devel cmake ninja git python python-pip python-virtualenv     sqlite vulkan-headers vulkan-icd-loader vulkan-radeon mariadb-libs grep snapper snap-pac     opencl-headers ocl-icd opencl-clhpp

# ── User groups ────────────────────────────────────
info "Setting up GPU access..."
sudo usermod -aG video,render "$HALO_USER"

# ── Directory structure ────────────────────────────
info "Creating /srv/ai/ with Btrfs subvolumes..."
sudo mkdir -p /srv/ai
for svc in rocm llama-cpp lemonade whisper-cpp open-webui vane searxng qdrant n8n kokoro comfyui models configs systemd scripts; do
    sudo btrfs subvolume create /srv/ai/$svc 2>/dev/null || true
done
sudo chown -R "$HALO_USER":"$HALO_USER" /srv/ai

# ── Clone halo-ai repo ────────────────────────────
info "Cloning halo-ai..."
cd /srv/ai
git init 2>/dev/null || true
git remote add origin https://github.com/bong-water-water-bong/halo-ai.git 2>/dev/null || true
git fetch origin main
git checkout -f main -- configs/ systemd/ scripts/ README.md .gitignore install.sh

# ── ROCm ───────────────────────────────────────────
if [ "${NEED_ROCM:-}" = "1" ]; then
    info "Downloading ROCm 7.13 for gfx1151..."
    cd /srv/ai/rocm
    wget -q --show-progress 'https://rocm.nightlies.amd.com/tarball/therock-dist-linux-gfx1151-7.13.0a20260323.tar.gz' -O therock.tar.gz
    mkdir -p install && tar -xf therock.tar.gz -C install
    sudo ln -sfn /srv/ai/rocm/install /opt/rocm
    echo 'export ROCM_HOME=/opt/rocm
export PATH=/opt/rocm/bin:$PATH
export LD_LIBRARY_PATH=/opt/rocm/lib:$LD_LIBRARY_PATH' | sudo tee /etc/profile.d/rocm.sh
    source /etc/profile.d/rocm.sh
    ok "ROCm installed. Verifying GPU..."
    rocminfo | grep -q gfx1151 && ok "gfx1151 detected" || warn "GPU not detected — may need reboot"
fi

# ── Python 3.12 + 3.13 ────────────────────────────
info "Compiling Python 3.12 and 3.13 from source..."
for VER in 3.12.13 3.13.3; do
    MAJOR=$(echo $VER | cut -d. -f1-2)
    PREFIX=/opt/python$(echo $MAJOR | tr -d .)
    if [ -x $PREFIX/bin/python$MAJOR ]; then ok "Python $MAJOR already installed"; continue; fi
    cd /tmp
    wget -q "https://www.python.org/ftp/python/$VER/Python-$VER.tar.xz"
    tar xf Python-$VER.tar.xz && cd Python-$VER
    ./configure --prefix=$PREFIX --enable-optimizations -q
    make -j$(nproc) -s && sudo make altinstall -s
    ok "Python $MAJOR compiled"
done

# ── Node.js 24 ─────────────────────────────────────
if ! node --version 2>/dev/null | grep -q "v24"; then
    info "Compiling Node.js 24 from source..."
    cd /tmp
    git clone --depth 1 --branch v24.5.0 https://github.com/nodejs/node.git nodejs-src
    cd nodejs-src
    /opt/python313/bin/python3.13 ./configure --prefix=/usr/local -q
    make -j$(nproc) -s && sudo make install -s
    sudo corepack enable
    ok "Node.js $(node --version) compiled"
fi

# ── Rust ───────────────────────────────────────────
if ! command -v cargo >/dev/null; then
    info "Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# ── Go (for Caddy) ─────────────────────────────────
if ! command -v go >/dev/null; then
    info "Installing Go..."
    cd /tmp && wget -q https://go.dev/dl/go1.24.3.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz
fi
export PATH=/usr/local/go/bin:~/go/bin:$PATH

# ── Build everything ───────────────────────────────
source /etc/profile.d/rocm.sh 2>/dev/null || true
export ROCBLAS_USE_HIPBLASLT=1

info "Building llama.cpp (HIP + Vulkan)..."
cd /srv/ai/llama-cpp
[ -d .git ] || git clone https://github.com/ggml-org/llama.cpp .
cmake -B build-hip -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DGGML_HIP_ROCWMMA_FATTN=ON -DCMAKE_BUILD_TYPE=Release -G Ninja -Wno-dev .
cmake --build build-hip -j$(nproc)
cmake -B build-vulkan -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release -G Ninja -Wno-dev .
cmake --build build-vulkan -j$(nproc)
cmake -B build-opencl -DGGML_OPENCL=ON -DCMAKE_BUILD_TYPE=Release -G Ninja -Wno-dev .
cmake --build build-opencl -j$(nproc)
ok "llama.cpp built (HIP + Vulkan + OpenCL)"

info "Building Lemonade..."
cd /srv/ai/lemonade
[ -d .git ] || git clone https://github.com/lemonade-sdk/lemonade .
cmake --preset default && cmake --build --preset default
ok "Lemonade built"

info "Building whisper.cpp..."
cd /srv/ai/whisper-cpp
[ -d .git ] || git clone https://github.com/ggerganov/whisper.cpp .
cmake -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DCMAKE_BUILD_TYPE=Release -G Ninja .
cmake --build build -j$(nproc)
ok "whisper.cpp built"

info "Building Qdrant..."
cd /srv/ai/qdrant
source ~/.cargo/env
[ -d .git ] || git clone https://github.com/qdrant/qdrant .
cargo build --release
ok "Qdrant built"

info "Building Caddy..."
go install github.com/caddyserver/caddy/v2/cmd/caddy@latest
ok "Caddy built"

info "Installing SearXNG..."
cd /srv/ai/searxng
[ -d .git ] || git clone https://github.com/searxng/searxng .
python3 -m venv .venv && source .venv/bin/activate
pip install -q setuptools msgspec && pip install -q --no-build-isolation -e .
deactivate
ok "SearXNG installed"

info "Installing Open WebUI..."
cd /srv/ai/open-webui
[ -d .git ] || git clone https://github.com/open-webui/open-webui .
/opt/python312/bin/python3.12 -m venv .venv && source .venv/bin/activate
sed -i 's/ddgs==9.11.2/ddgs>=9.11.3/' pyproject.toml 2>/dev/null
sed -i 's/rapidocr-onnxruntime==1.4.4/rapidocr-onnxruntime>=1.2.3/' pyproject.toml 2>/dev/null
pip install -q setuptools hatchling && pip install -q . 
deactivate
ok "Open WebUI installed"

info "Installing Vane (Perplexica)..."
cd /srv/ai/vane
[ -d .git ] || git clone https://github.com/ItzCrazyKns/Vane .
yarn install && yarn build
ok "Vane built"

info "Installing n8n..."
cd /srv/ai/n8n
[ -d .git ] || git clone https://github.com/n8n-io/n8n .
npm install -g pnpm && pnpm install --frozen-lockfile && pnpm build
ok "n8n built"

info "Installing ComfyUI..."
cd /srv/ai/comfyui
[ -d .git ] || git clone https://github.com/comfyanonymous/ComfyUI .
/opt/python313/bin/python3.13 -m venv .venv && source .venv/bin/activate
pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2.4
pip install -q -r requirements.txt
deactivate
ok "ComfyUI installed"

info "Installing Kokoro TTS..."
cd /srv/ai/kokoro
[ -d .git ] || git clone https://github.com/remsky/Kokoro-FastAPI .
/opt/python313/bin/python3.13 -m venv .venv && source .venv/bin/activate
pip install -q --no-deps -e .
pip install -q torch --index-url https://download.pytorch.org/whl/rocm6.2.4
pip install -q audioop-lts scipy transformers spacy inflect av uvicorn fastapi soundfile pydantic
pip install -q --no-deps 'misaki>=0.7.4' 'kokoro>=0.7.16'
python -m spacy download en_core_web_sm
deactivate
ok "Kokoro installed"

# ── System config ──────────────────────────────────
info "Configuring system..."

# GPU device permissions
echo 'SUBSYSTEM=="kfd", KERNEL=="kfd", TAG+="uaccess", GROUP="render", MODE="0666"
SUBSYSTEM=="drm", KERNEL=="renderD*", TAG+="uaccess", GROUP="render", MODE="0666"' | sudo tee /etc/udev/rules.d/70-amdgpu.rules

# Kernel param for GPU memory
ENTRY=$(ls /boot/loader/entries/*.conf | head -1)
grep -q ttm.pages_limit "$ENTRY" || sudo sed -i 's/^options /options ttm.pages_limit=30146560 /' "$ENTRY"

# Disable sleep/suspend
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# SSH hardening
echo "PasswordAuthentication no
PermitRootLogin no
AllowUsers $HALO_USER" | sudo tee /etc/ssh/sshd_config.d/90-halo-security.conf

# ── Apply interactive configuration ────────────────
info "Applying configuration from setup..."

# Write Caddy password hash to Caddyfile
if command -v caddy >/dev/null; then
    CADDY_HASH=$(caddy hash-password --plaintext "$CADDY_PASSWORD")
    sed -i "s|        admin a|        admin $CADDY_HASH|" /srv/ai/configs/Caddyfile
    ok "Caddy password hash written to Caddyfile"
else
    warn "Caddy not yet available — password will be configured on first run"
fi

# Write SearXNG secret key to settings.yml
sed -i "s|secret_key: \"CHANGEME-generate-a-new-secret-key\"|secret_key: \"$SEARXNG_KEY\"|" /srv/ai/configs/searxng/settings.yml
ok "SearXNG secret key written to settings.yml"

# Write Dashboard API key
mkdir -p /srv/ai/dashboard-api/data
echo -n "$DASHBOARD_API_KEY" > /srv/ai/dashboard-api/data/dashboard-api-key.txt
chmod 600 /srv/ai/dashboard-api/data/dashboard-api-key.txt
ok "Dashboard API key written to /srv/ai/dashboard-api/data/dashboard-api-key.txt"

# Install systemd units
sudo cp /srv/ai/systemd/halo-*.service /srv/ai/systemd/halo-*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable halo-watchdog.timer

# Enable selected services
for svc in "${SELECTED_SERVICES[@]}"; do
    unit="halo-${svc}.service"
    # Map service names to actual systemd unit names
    case "$svc" in
        dashboard) unit="halo-dashboard-api.service"; unit2="halo-dashboard-ui.service" ;;
        whisper)   unit="halo-whisper-server.service" ;;
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

# ── Done ───────────────────────────────────────────
echo ''
ok "========================================"
ok "  halo-ai installation complete!"
ok "========================================"
echo ''
info "Reboot to activate GPU memory (115GB GTT):"
echo "  sudo reboot"
echo ''
info "Enabled services: ${SELECTED_SERVICES[*]}"
info "Start all enabled services after reboot:"
START_UNITS=""
for svc in "${SELECTED_SERVICES[@]}"; do
    case "$svc" in
        dashboard) START_UNITS+="halo-dashboard-api halo-dashboard-ui " ;;
        whisper)   START_UNITS+="halo-whisper-server " ;;
        *)         START_UNITS+="halo-${svc} " ;;
    esac
done
echo "  sudo systemctl start $START_UNITS"
echo ''
info "Access via SSH tunnel:"
echo "  ssh -L 3000:localhost:3000 -L 3001:localhost:3001 $HALO_HOSTNAME"
echo "  Then open http://localhost:3000 (Open WebUI) or http://localhost:3001 (Perplexica)"
echo ''
info "Dashboard API key saved to: /srv/ai/dashboard-api/data/dashboard-api-key.txt"
