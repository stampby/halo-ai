# Halo AI Architecture

## Overview

Halo AI is a bare-metal AI stack for the AMD Ryzen AI MAX+ 395 (Strix Halo). Every component is compiled from source on Arch Linux -- no Docker, no containers, no package managers for AI services. The entire platform runs on a single chip with 128GB of unified memory, delivering 89 tok/s on Qwen3-30B-A3B.

The stack provides LLM inference, chat UI, deep research, speech-to-text, text-to-speech, image generation, RAG pipelines, workflow automation, private search, and autonomous monitoring -- all integrated, all on localhost.

## Hardware

| Component | Specification |
|-----------|---------------|
| CPU/GPU | AMD Ryzen AI MAX+ 395 (Strix Halo) -- gfx1151 |
| Total Memory | 128 GB unified (shared between CPU and GPU) |
| GPU-Accessible Memory | 115 GB GTT (Graphics Translation Table) |
| GPU Compute | ROCm 7.13 (TheRock nightly builds for gfx1151) |
| Kernel Parameter | `ttm.pages_limit=30146560` to unlock full GPU memory |
| Filesystem | Btrfs with subvolumes and Snapper snapshots |
| OS | Arch Linux (bleeding-edge kernel and Mesa) |

The 115GB GPU memory is what makes this platform viable. Models up to 70B parameters (quantized) can be loaded entirely into GPU memory on a single chip, with no PCIe bottleneck since CPU and GPU share the same memory bus.

## Service Map

```
Port    Service             Role
----    -------             ----
443     Caddy               Reverse proxy, TLS termination, basic auth
8080    Lemonade            Unified AI API gateway (OpenAI/Ollama/Anthropic compatible)
8081    llama-server        LLM inference engine (Vulkan or HIP backend)
8082    whisper-server      Speech-to-text (whisper.cpp)
8083    Kokoro              Text-to-speech (Kokoro-FastAPI)
8188    ComfyUI             Image generation (Stable Diffusion, node-based)
3000    Open WebUI          Chat interface with RAG, multi-model support
3001    Vane                Deep research with cited sources (Perplexica fork)
3002    Dashboard API       GPU metrics, service health monitoring (DreamServer fork)
3003    Dashboard UI        Web frontend for dashboard metrics
5678    n8n                 Workflow automation (400+ integrations)
6333    Qdrant              Vector database for RAG embeddings
8888    SearXNG             Privacy-respecting meta-search engine
```

All services bind to `127.0.0.1`. None are directly reachable from the network.

## Request Flow

### Web Browser Access

```
Browser (any device on LAN)
    |
    | HTTPS :443
    v
Caddy (reverse proxy)
    |-- basic auth (bcrypt password)
    |-- auto-generated TLS certificate (internal CA)
    |
    |-- /chat/*        --> Open WebUI :3000
    |-- /research/*    --> Vane :3001
    |-- /workflows/*   --> n8n :5678
    |-- /api/*         --> Lemonade :8080
    |-- /comfyui/*     --> ComfyUI :8188
    |-- / (default)    --> Open WebUI :3000
```

### SSH Tunnel Access

```
Client machine
    |
    | ssh -L 3000:localhost:3000 -L 3001:localhost:3001 user@strixhalo
    |
    v
Direct localhost access to any service port
```

## Data Flow

### LLM Chat Request

```
User input (browser)
    |
    v
Open WebUI :3000
    |-- Connects to Lemonade as its "Ollama" backend (OLLAMA_BASE_URL=http://localhost:8080)
    |
    v
Lemonade :8080 (API gateway)
    |-- Routes to appropriate backend based on request type
    |-- Provides OpenAI, Ollama, and Anthropic API compatibility
    |
    v
llama-server :8081
    |-- Loads model from /srv/ai/models/
    |-- Runs inference on GPU (115GB GTT memory)
    |-- Returns generated tokens
    |
    v
Response streams back through Lemonade --> Open WebUI --> Browser
```

### Deep Research Request

```
User query (browser)
    |
    v
Vane :3001
    |-- Sends search queries to SearXNG :8888
    |-- SearXNG fetches results from public search engines
    |-- Vane sends gathered context + query to Lemonade :8080
    |-- Lemonade forwards to llama-server :8081
    |-- LLM synthesizes answer with citations
    |
    v
Research response with sourced citations --> Browser
```

### RAG (Retrieval-Augmented Generation) Flow

```
Document upload --> Open WebUI
    |-- Text extracted, chunked, embedded
    |-- Embeddings stored in Qdrant :6333
    |
User query --> Open WebUI
    |-- Query embedded, nearest vectors retrieved from Qdrant
    |-- Retrieved context + query sent to Lemonade --> llama-server
    |-- LLM generates answer grounded in document context
    |
    v
Answer with document references --> Browser
```

### Voice Input/Output

```
Audio input --> Open WebUI or direct API call
    |
    v
whisper-server :8082
    |-- GPU-accelerated transcription (whisper-large-v3)
    |-- Returns text
    |
    v
Text --> Lemonade :8080 --> llama-server :8081 (LLM generates response)
    |
    v
Kokoro :8083
    |-- Text-to-speech synthesis
    |-- Returns audio
    |
    v
Audio response --> Browser
```

## File System Layout

Everything lives under `/srv/ai/`, organized as Btrfs subvolumes for snapshot isolation.

```
/srv/ai/
|-- rocm/                   # ROCm 7.13 runtime (symlinked to /opt/rocm)
|   `-- install/            # Extracted TheRock tarball for gfx1151
|
|-- llama-cpp/              # llama.cpp source and builds
|   |-- build-hip/          # HIP/ROCm backend binary
|   |-- build-vulkan/       # Vulkan backend binary
|   `-- build-opencl/       # OpenCL backend binary
|
|-- lemonade/               # Lemonade SDK source and build
|   `-- build/              # lemonade-router binary
|
|-- whisper-cpp/            # whisper.cpp source and build
|   `-- build/              # whisper-server binary
|
|-- open-webui/             # Open WebUI (Python 3.12 venv)
|   |-- .venv/              # Virtual environment
|   `-- data/               # SQLite DB, uploads, user data
|
|-- vane/                   # Vane/Perplexica (Node.js)
|   `-- .next/              # Built Next.js standalone app
|
|-- searxng/                # SearXNG (Python venv)
|   `-- .venv/              # Virtual environment
|
|-- qdrant/                 # Qdrant (Rust, compiled)
|   |-- target/release/     # qdrant binary
|   `-- storage/            # Vector data on disk
|
|-- n8n/                    # n8n (Node.js, pnpm)
|   `-- data/               # Workflow data, credentials
|
|-- kokoro/                 # Kokoro-FastAPI (Python 3.13 venv)
|   `-- .venv/              # Virtual environment
|
|-- comfyui/                # ComfyUI (Python 3.13 venv, ROCm PyTorch)
|   `-- .venv/              # Virtual environment
|
|-- dashboard-api/          # Dashboard API (DreamServer fork, Python)
|   |-- .venv/              # Virtual environment
|   `-- data/               # API key, metrics DB
|
|-- dashboard-ui/           # Dashboard UI (DreamServer fork, Node.js/Vite)
|
|-- agent/                  # Autonomous agent (halo-agent.py)
|
|-- models/                 # GGUF model files
|   |-- qwen3-30b-a3b-q4_k_m.gguf
|   `-- whisper-large-v3.bin
|
|-- configs/                # All configuration files
|   |-- Caddyfile           # Caddy reverse proxy config
|   |-- rocm.env            # ROCm environment variables
|   |-- searxng/            # SearXNG settings.yml
|   `-- system/             # System-level configs (udev, SSH, nftables, kernel)
|
|-- systemd/                # Systemd unit files (source of truth)
|
|-- scripts/                # Management tools
|   |-- halo-models.sh      # Model download and activation
|   |-- halo-driver-swap.sh # GPU backend switching
|   |-- halo-update.sh      # System-wide update tool
|   |-- halo-proxy-setup.sh # Caddy proxy enablement
|   |-- halo-backup.sh      # Backup utility
|   |-- halo-watchdog.sh    # Service health monitor
|   |-- build-all.sh        # Full rebuild script
|   |-- build-llama-cpp.sh  # llama.cpp rebuild
|   `-- build-whisper-cpp.sh# whisper.cpp rebuild
|
|-- backups/                # Nightly backup destination
`-- logs/                   # Application logs (backup.log, etc.)
```

Key paths outside `/srv/ai/`:

| Path | Purpose |
|------|---------|
| `/opt/rocm` | Symlink to `/srv/ai/rocm/install` |
| `/opt/python312/` | Python 3.12 (compiled, used by Open WebUI) |
| `/opt/python313/` | Python 3.13 (compiled, used by ComfyUI, Kokoro) |
| `/etc/systemd/system/halo-*.service` | Installed systemd units (copied from `/srv/ai/systemd/`) |
| `/etc/profile.d/rocm.sh` | ROCm PATH and LD_LIBRARY_PATH |
| `/etc/udev/rules.d/70-amdgpu.rules` | GPU device permissions |
| `/etc/ssh/sshd_config.d/90-halo-security.conf` | SSH hardening |
| `/var/log/halo-watchdog.log` | Watchdog agent log |
| `/var/lib/caddy/` | Caddy data directory (TLS certificates) |

## Security Model

### Network Perimeter

All AI services bind exclusively to `127.0.0.1`. The only network-accessible services are:

| Port | Service | Access |
|------|---------|--------|
| 22 | SSH | LAN only (xxx.xxx.xxx.0/24), key-only authentication |
| 443 | Caddy | LAN only (xxx.xxx.xxx.0/24), basic auth + TLS |
| 51820 | WireGuard | Anywhere (future VPN, placeholder in firewall) |

### Layers

1. **nftables firewall** (`/srv/ai/configs/system/nftables.conf`):
   - Default policy: DROP all inbound
   - Allow established/related connections
   - Allow loopback (localhost)
   - Allow SSH and HTTPS from LAN subnet only (xxx.xxx.xxx.0/24)
   - Allow WireGuard (UDP 51820) from anywhere
   - Allow ICMP (ping)
   - Drop everything else with counter

2. **fail2ban**: Bans IPs after repeated failed SSH attempts.

3. **SSH hardening** (`/srv/ai/configs/system/90-halo-security.conf`):
   - Password authentication disabled
   - Root login disabled
   - AllowUsers restricted to the configured user
   - PAM disabled
   - Ed25519 keys recommended

4. **Caddy basic auth**: bcrypt-hashed password protects all web endpoints. Default password is `Caddy` and must be changed immediately after install.

5. **Caddy internal TLS**: Auto-generates a self-signed CA and TLS certificates. The CA cert can be exported and trusted on client devices for warning-free HTTPS.

6. **Systemd hardening**: Every service unit includes:
   - `ProtectSystem=strict` (read-only filesystem except allowed paths)
   - `PrivateTmp=yes` (isolated /tmp)
   - `NoNewPrivileges=yes` (no privilege escalation)
   - `ProtectHome=read-only`
   - `ReadWritePaths=/srv/ai` (only writable path)
   - Non-root `User=` and `Group=` (except agent/watchdog which need root for restarts)

7. **Sleep/suspend disabled**: `sleep.target`, `suspend.target`, `hibernate.target`, and `hybrid-sleep.target` are all masked to prevent accidental service interruption on a headless server.

## Systemd Services

### Service Units

All services follow the naming convention `halo-<name>.service` and are installed to `/etc/systemd/system/`.

| Unit | Type | User | Depends On |
|------|------|------|------------|
| `halo-llama-server.service` | simple | user | network |
| `halo-lemonade.service` | simple | user | network, llama-server |
| `halo-whisper-server.service` | simple | user | network |
| `halo-open-webui.service` | simple | user | network, lemonade |
| `halo-vane.service` | simple | user | network, searxng, lemonade |
| `halo-n8n.service` | simple | user | network |
| `halo-comfyui.service` | simple | user | network |
| `halo-searxng.service` | simple | user | network |
| `halo-qdrant.service` | simple | user | network |
| `halo-dashboard-api.service` | simple | user | network |
| `halo-dashboard-ui.service` | simple | user | network, dashboard-api |
| `halo-caddy.service` | simple | user | network |
| `halo-agent.service` | simple | root | network, llama-server, lemonade |
| `halo-watchdog.service` | oneshot | root | network |
| `halo-backup.service` | oneshot | user | (none) |
| `halo-opencl.service` | simple | user | network |

### Timers

| Timer | Schedule | Triggers |
|-------|----------|----------|
| `halo-watchdog.timer` | Every 5 minutes (first run 2 min after boot) | `halo-watchdog.service` |
| `halo-backup.timer` | Daily (with up to 30 min random delay) | `halo-backup.service` |

### Dependency Chain

```
network.target
    |
    |-- halo-llama-server
    |       |
    |       `-- halo-lemonade (Wants + After llama-server)
    |               |
    |               |-- halo-open-webui (After lemonade)
    |               `-- halo-vane (After lemonade + searxng)
    |
    |-- halo-searxng
    |       |
    |       `-- halo-vane (After searxng + lemonade)
    |
    |-- halo-whisper-server
    |-- halo-qdrant
    |-- halo-n8n
    |-- halo-comfyui
    |-- halo-caddy
    |
    |-- halo-dashboard-api
    |       |
    |       `-- halo-dashboard-ui (After dashboard-api)
    |
    `-- halo-agent (Wants llama-server + lemonade)
```

All services use `Restart=on-failure` with `RestartSec=5` (agent uses `Restart=always` with `RestartSec=10` and `WatchdogSec=120`).

### Management Commands

```bash
# Start/stop all halo services
sudo systemctl start halo-llama-server halo-lemonade halo-open-webui ...
sudo systemctl stop halo-llama-server halo-lemonade halo-open-webui ...

# Check status of all halo services
systemctl list-units 'halo-*' --all

# View logs for a service
journalctl -u halo-llama-server -f

# Reload Caddy config without restart
sudo systemctl reload halo-caddy
```

## GPU Backends

llama.cpp is compiled three times, producing three separate binaries in `/srv/ai/llama-cpp/`. The `halo-driver-swap.sh` script switches between them by editing the systemd unit file.

### HIP (ROCm)

- **Binary**: `/srv/ai/llama-cpp/build-hip/bin/llama-server`
- **Build flags**: `-DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DGGML_HIP_ROCWMMA_FATTN=ON`
- **Best for**: Prompt processing speed, long context windows
- **Why**: Flash Attention via rocWMMA, optimized matrix math through hipBLAS/hipBLASLt
- **Environment**: `ROCBLAS_USE_HIPBLASLT=1`, ROCm env from `/srv/ai/configs/rocm.env`
- **Notes**: Requires ROCm runtime at `/opt/rocm`. This is the default backend in the systemd unit.

### Vulkan (RADV)

- **Binary**: `/srv/ai/llama-cpp/build-vulkan/bin/llama-server`
- **Build flags**: `-DGGML_VULKAN=ON`
- **Best for**: Token generation speed (fastest tok/s, ~89 tok/s on Qwen3-30B-A3B)
- **Why**: Mesa RADV driver is highly optimized on Arch Linux. Lower overhead for small batch inference.
- **Notes**: Does not require ROCm. Works with standard Mesa Vulkan drivers. The default ExecStart in the shipped systemd unit actually points to the Vulkan binary despite the unit being named "HIP/ROCm" in its description.

### OpenCL (ROCm)

- **Binary**: `/srv/ai/llama-cpp/build-opencl/bin/llama-server`
- **Build flags**: `-DGGML_OPENCL=ON`
- **Best for**: General GPU compute, compatibility testing, fallback
- **Why**: Broadest hardware compatibility. Useful when HIP or Vulkan have driver issues.
- **Port**: 8083 (separate from the primary llama-server on 8081, can run simultaneously via `halo-opencl.service`)
- **Notes**: Requires `opencl-headers`, `ocl-icd`, `opencl-clhpp` packages.

### Switching Backends

```bash
halo-driver-swap.sh vulkan    # Switch to Vulkan
halo-driver-swap.sh hip       # Switch to HIP/ROCm
halo-driver-swap.sh opencl    # Switch to OpenCL
halo-driver-swap.sh status    # Show current backend + speed
halo-driver-swap.sh bench     # Quick benchmark on current backend
```

Each swap takes a Btrfs snapshot before modifying the systemd unit, stops the service, updates the `ExecStart` line, reloads systemd, and restarts. Total downtime is approximately 10 seconds.
