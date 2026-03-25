#!/bin/bash
# halo-ai installer for AMD Strix Halo (Arch Linux)
# Usage: curl -fsSL https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/install.sh | bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

# ── Halo AI branded output ────────────────────────
STEP_CURRENT=0
STEP_TOTAL=17

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
  ║>>  gfx1151 │ 89t/s │ 115GB    >>║
  ╚═══════════════════════════════════╝
BANNER
echo -e "${NC}"
echo -e "${DIM}  Bare-metal AI stack for AMD Strix Halo${NC}"
echo -e "${DIM}  github.com/bong-water-water-bong/halo-ai${NC}"
echo ''

INSTALL_START=$(date +%s)
echo -e "${YELLOW}${BOLD}  Estimated total install time: 2-3 hours (compiling from source)${NC}"
echo -e "${DIM}  Builds use all $(nproc) cores in parallel — your machine will be working hard.${NC}"
echo -e "${DIM}  Everything is built natively for your hardware — no containers, no shortcuts.${NC}"
echo ''

# ── Preflight ──────────────────────────────────────
step "Preflight checks"
[ "$(id -u)" -eq 0 ] && fail "Do not run as root. Run as your normal user (with sudo access)."
command -v pacman >/dev/null || fail "Arch Linux required."
lscpu | grep -q "Strix" || warn "This installer is designed for AMD Strix Halo. Proceeding anyway..."
grep -q "gfx1151" /opt/rocm/bin/rocminfo 2>/dev/null && ok "ROCm already installed" || NEED_ROCM=1

# ── Interactive configuration ─────────────────────
step "Interactive Setup"
info "Press Enter to accept defaults"
echo ''

# Helper: prompt with default
prompt() {
    local var_name="$1" prompt_text="$2" default="$3"
    read -rp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text [${default}]: " input
    printf -v "$var_name" '%s' "${input:-$default}"
}

# Helper: prompt for password (no echo)
prompt_secret() {
    local var_name="$1" prompt_text="$2"
    while true; do
        read -srp "$(echo -e "${BLUE}[halo-ai]${NC}") $prompt_text: " input
        echo ''
        if [ -n "$input" ]; then
            printf -v "$var_name" '%s' "$input"
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
info "Default: Caddy — change this immediately after install!"
prompt CADDY_PASSWORD "Caddy password" "Caddy"
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
sudo pacman -S --noconfirm --needed base-devel cmake ninja git python python-pip python-virtualenv     sqlite vulkan-headers vulkan-icd-loader vulkan-radeon mariadb-libs grep snapper snap-pac     opencl-headers ocl-icd opencl-clhpp

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
    git remote add origin https://github.com/bong-water-water-bong/halo-ai.git
fi
git fetch origin main
git checkout -B main origin/main -- configs/ systemd/ scripts/ assets/ docs/ README.md .gitignore 2>/dev/null || \
    git checkout FETCH_HEAD -- configs/ systemd/ scripts/ assets/ docs/ README.md .gitignore
ok "halo-ai repo ready"

# ── ROCm ───────────────────────────────────────────
step "ROCm GPU runtime (~10 min download, ~2 min extract)"
if [ "${NEED_ROCM:-}" = "1" ]; then
    command -v wget >/dev/null || sudo pacman -S --noconfirm --needed wget
    info "Downloading ROCm 7.13 for gfx1151..."
    if cd /srv/ai/rocm 2>/dev/null && \
       wget -q --show-progress 'https://rocm.nightlies.amd.com/tarball/therock-dist-linux-gfx1151-7.13.0a20260323.tar.gz' -O therock.tar.gz 2>/dev/null; then
        mkdir -p install && tar -xf therock.tar.gz -C install
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
step "Building Python 3.12 + 3.13 (~15 min each)"
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
step "Building Node.js 24 (~20 min)"
if ! node --version 2>/dev/null | grep -q "v24"; then
    progress "Compiling from source — this takes a while..."
    cd /tmp
    [ -d nodejs-src ] && rm -rf nodejs-src
    git clone --depth 1 --branch v24.5.0 https://github.com/nodejs/node.git nodejs-src
    cd nodejs-src
    /opt/python313/bin/python3.13 ./configure --prefix=/usr/local -q
    make -j$(nproc) -s && sudo make install -s
    sudo corepack enable
    ok "Node.js $(node --version) compiled"
fi

# ── Rust ───────────────────────────────────────────
step "Rust + Go toolchains (~5 min)"
if ! command -v cargo >/dev/null; then
    info "Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# ── Go (for Caddy) ─────────────────────────────────
if ! command -v go >/dev/null; then
    progress "Installing Go..."
    cd /tmp && wget -q https://go.dev/dl/go1.24.3.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz
fi
export PATH=/usr/local/go/bin:~/go/bin:$PATH

# ── Build everything ───────────────────────────────
step "Building llama.cpp — HIP + Vulkan + OpenCL (~10 min)"
source /etc/profile.d/rocm.sh 2>/dev/null || true
export ROCBLAS_USE_HIPBLASLT=1

progress "Compiling HIP backend..."
cd /srv/ai/llama-cpp
[ -d .git ] || git clone https://github.com/ggml-org/llama.cpp .
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
[ -d .git ] || git clone https://github.com/lemonade-sdk/lemonade .
cmake --preset default && cmake --build --preset default
ok "Lemonade built"

info "Building whisper.cpp..."
cd /srv/ai/whisper-cpp
[ -d .git ] || git clone https://github.com/ggerganov/whisper.cpp .
cmake -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DCMAKE_BUILD_TYPE=Release -G Ninja .
cmake --build build -j$(nproc)
ok "whisper.cpp built"

step "Building Qdrant + Caddy (~25 min — Rust compile)"
info "Building Qdrant..."
cd /srv/ai/qdrant
source ~/.cargo/env
[ -d .git ] || git clone https://github.com/qdrant/qdrant .
cargo build --release
ok "Qdrant built"

info "Building Caddy..."
go install github.com/caddyserver/caddy/v2/cmd/caddy@latest
ok "Caddy built"

step "Installing SearXNG + Open WebUI (~10 min)"
info "Installing SearXNG..."
cd /srv/ai/searxng
[ -d .git ] || git clone https://github.com/searxng/searxng .
python3 -m venv .venv && source .venv/bin/activate
pip install -q setuptools msgspec pyyaml typing_extensions Brotli lxml && pip install -q --no-build-isolation -e .
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

step "Installing Vane + n8n + ComfyUI + Kokoro (~15 min)"
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
step "System hardening & configuration"

# GPU device permissions
echo 'SUBSYSTEM=="kfd", KERNEL=="kfd", TAG+="uaccess", GROUP="render", MODE="0660"
SUBSYSTEM=="drm", KERNEL=="renderD*", TAG+="uaccess", GROUP="render", MODE="0660"' | sudo tee /etc/udev/rules.d/70-amdgpu.rules

# Kernel param for GPU memory
ENTRY=$(ls /boot/loader/entries/*.conf | head -1)
grep -q ttm.pages_limit "$ENTRY" || sudo sed -i 's/^options /options ttm.pages_limit=30146560 /' "$ENTRY"

# Disable sleep/suspend
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# SSH hardening
echo "PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
PermitRootLogin no
AllowUsers $HALO_USER" | sudo tee /etc/ssh/sshd_config.d/90-halo-security.conf

# Install nftables firewall
info "Installing firewall..."
sudo pacman -S --noconfirm --needed nftables 2>/dev/null
sudo cp /srv/ai/configs/system/nftables.conf /etc/nftables.conf
sudo sed -i "s|xxx.xxx.xxx.0/24|$(ip route | grep 'src' | head -1 | awk '{print $1}')|g" /etc/nftables.conf
sudo systemctl enable --now nftables 2>/dev/null
ok "Firewall active (LAN-only SSH + HTTP)"

# Install fail2ban
info "Installing fail2ban..."
sudo pacman -S --noconfirm --needed fail2ban 2>/dev/null
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
sudo systemctl enable --now fail2ban 2>/dev/null
ok "fail2ban active (5 attempts = 1hr ban)"

# ── Apply interactive configuration ────────────────
step "Applying configuration & enabling services"

# Generate Caddy password hash and write Caddyfile with subdomain routing
CADDY_HASH=$(caddy hash-password --plaintext "$CADDY_PASSWORD")
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

# Add Caddy XDG_DATA_HOME to systemd unit
grep -q 'XDG_DATA_HOME' /srv/ai/systemd/halo-caddy.service || \
    sed -i '/\[Service\]/a Environment=XDG_DATA_HOME=/srv/ai/.caddy' /srv/ai/systemd/halo-caddy.service
mkdir -p /srv/ai/.caddy

# Write SearXNG secret key
sed -i "s|secret_key: \"CHANGEME-generate-a-new-secret-key\"|secret_key: \"$SEARXNG_KEY\"|" /srv/ai/configs/searxng/settings.yml
chmod 640 /srv/ai/configs/searxng/settings.yml
ok "SearXNG secret key configured"

# Write Dashboard API key
mkdir -p /srv/ai/dashboard-api/data
echo -n "$DASHBOARD_API_KEY" > /srv/ai/dashboard-api/data/dashboard-api-key.txt
chmod 600 /srv/ai/dashboard-api/data/dashboard-api-key.txt
ok "Dashboard API key configured"

# Configure Open WebUI → llama-server connection
info "Wiring services together..."
grep -q 'OPENAI_API_BASE_URL' /srv/ai/systemd/halo-open-webui.service || \
    sed -i '/\[Service\]/a Environment=OPENAI_API_BASE_URL=http://127.0.0.1:8081/v1\nEnvironment=OPENAI_API_KEY=not-needed\nEnvironment=ENABLE_OLLAMA_API=false' /srv/ai/systemd/halo-open-webui.service
ok "Open WebUI → llama-server connected"

# Configure llama-server with jinja + disable thinking mode
sed -i 's|--model |--jinja --reasoning-budget 0 --model |' /srv/ai/systemd/halo-llama-server.service 2>/dev/null
ok "llama-server configured (jinja + reasoning off)"

# Configure n8n for HTTP (no secure cookie)
grep -q 'N8N_SECURE_COOKIE' /srv/ai/systemd/halo-n8n.service || \
    sed -i '/\[Service\]/a Environment=N8N_SECURE_COOKIE=false' /srv/ai/systemd/halo-n8n.service
ok "n8n configured for HTTP"

# Configure Vane (Perplexica)
info "Configuring Vane deep research..."
mkdir -p /srv/ai/vane/.next/standalone/data
ln -sfn /srv/ai/vane/.next/static /srv/ai/vane/.next/standalone/.next/static 2>/dev/null
ln -sfn /srv/ai/vane/public /srv/ai/vane/.next/standalone/public 2>/dev/null
ln -sfn /srv/ai/vane/drizzle /srv/ai/vane/.next/standalone/drizzle 2>/dev/null
# Get model name from llama-server config
MODEL_NAME=$(grep -oP '(?<=--model /srv/ai/models/)\S+' /srv/ai/systemd/halo-llama-server.service | head -1)
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
    <p>Default login &mdash; <strong>caddy</strong> / <strong>caddy</strong> &mdash; change after first login</p>
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
    <a class="card" target="_blank" href="https://github.com/bong-water-water-bong/meek"><h3><span class="dot on"></span>Meek</h3><p>Security — 9 Reflex agents guard 24/7</p></a>
    <a class="card" target="_blank" href="https://github.com/bong-water-water-bong/echo"><h3><span class="dot on"></span>Echo</h3><p>Social media — she speaks for the family</p></a>
</div>
<div class="footer">
    <p>90 tok/s &middot; 115GB GPU &middot; zero containers &middot; <a href="https://github.com/bong-water-water-bong/halo-ai">GitHub</a></p>
</div>
</body>
</html>
LANDINGEOF

# Replace landing page URLs with actual hostname
sed -i "s|CHAT_URL|http://chat.$HALO_HOSTNAME|g" /srv/ai/configs/index.html
sed -i "s|RESEARCH_URL|http://research.$HALO_HOSTNAME|g" /srv/ai/configs/index.html
sed -i "s|COMFYUI_URL|http://comfyui.$HALO_HOSTNAME|g" /srv/ai/configs/index.html
sed -i "s|N8N_URL|http://n8n.$HALO_HOSTNAME|g" /srv/ai/configs/index.html
sed -i "s|SEARCH_URL|http://search.$HALO_HOSTNAME|g" /srv/ai/configs/index.html
ok "Landing page created"

# Add hostname + subdomains to /etc/hosts
if ! grep -q "$HALO_HOSTNAME" /etc/hosts 2>/dev/null; then
    echo "127.0.0.1    $HALO_HOSTNAME chat.$HALO_HOSTNAME research.$HALO_HOSTNAME search.$HALO_HOSTNAME n8n.$HALO_HOSTNAME comfyui.$HALO_HOSTNAME" | sudo tee -a /etc/hosts
    ok "Hostname and subdomains added to /etc/hosts"
fi

# Replace <YOUR_USER> in all systemd units
sudo sed -i "s/<YOUR_USER>/$HALO_USER/g" /etc/systemd/system/halo-*.service /etc/systemd/system/halo-*.timer 2>/dev/null

# Install systemd units
sudo cp /srv/ai/systemd/halo-*.service /srv/ai/systemd/halo-*.timer /etc/systemd/system/ 2>/dev/null
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
    [ -d /srv/ai/meek/.git ] || git clone https://github.com/bong-water-water-bong/meek /srv/ai/meek
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
if [ "$CADDY_PASSWORD" = "Caddy" ]; then
echo ''
echo -e "${RED}${BOLD}  ╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}${BOLD}  ║                                                              ║${NC}"
echo -e "${RED}${BOLD}  ║   *** SECURITY WARNING: DEFAULT PASSWORD IN USE ***          ║${NC}"
echo -e "${RED}${BOLD}  ║                                                              ║${NC}"
echo -e "${RED}${BOLD}  ║   The Caddy reverse proxy is using the default password.     ║${NC}"
echo -e "${RED}${BOLD}  ║   Anyone who knows this password can access ALL services.    ║${NC}"
echo -e "${RED}${BOLD}  ║                                                              ║${NC}"
echo -e "${RED}${BOLD}  ║   You MUST change it immediately after first boot:           ║${NC}"
echo -e "${RED}${BOLD}  ║                                                              ║${NC}"
echo -e "${RED}${BOLD}  ║      /srv/ai/scripts/halo-change-password.sh                 ║${NC}"
echo -e "${RED}${BOLD}  ║                                                              ║${NC}"
echo -e "${RED}${BOLD}  ╚══════════════════════════════════════════════════════════════╝${NC}"
echo ''
fi

echo -e "  ${BOLD}Next steps:${NC}"
echo ''
echo -e "  ${RED}${BOLD}0.${NC} ${RED}${BOLD}CHANGE THE DEFAULT CADDY PASSWORD:${NC}"
echo -e "     ${BOLD}/srv/ai/scripts/halo-change-password.sh${NC}"
echo ''
echo -e "  ${YELLOW}1.${NC} Reboot to activate GPU memory (115GB GTT):"
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
echo -e "  ${DIM}$LAN_IP    $HALO_HOSTNAME chat.$HALO_HOSTNAME research.$HALO_HOSTNAME search.$HALO_HOSTNAME n8n.$HALO_HOSTNAME comfyui.$HALO_HOSTNAME${NC}"
echo ''
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
