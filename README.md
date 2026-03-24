<div align="center">

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**Zero containers. Zero overhead. Every byte goes to inference.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/install.sh | bash
```

One command. Compiles everything from source for your Strix Halo. Takes ~45 minutes on a fresh Arch install. Reboot when done.

## What is this?

A complete, self-hosted AI platform compiled entirely from source for the **AMD Ryzen AI MAX+ 395 (Strix Halo)** APU. LLM inference, chat UI, deep research, voice I/O, image generation, RAG, and workflow automation — all running bare metal on a single chip with 128GB of unified memory.

## Design Philosophy

halo-ai is designed to run as a **dedicated, always-on AI server** built on a **minimal Arch Linux installation** — no desktop environment, no unnecessary packages, no bloat. The base system is a fresh `archinstall` with only the essentials: kernel, networking, SSH, Btrfs on LVM, and the packages required to compile the stack from source.

This is not a workstation setup where AI runs alongside a desktop. This is a headless server whose sole purpose is AI inference and serving. Every system resource — CPU cycles, memory, GPU compute, disk I/O — is dedicated to running models and serving requests. The minimal Arch base means:

- **No desktop environment** consuming GPU memory or CPU cycles
- **No package manager overhead** — every component is compiled from source with hardware-specific optimizations (`-DAMDGPU_TARGETS=gfx1151`, `-DGGML_HIP_ROCWMMA_FATTN=ON`)
- **No container runtime** stealing memory from the unified pool — on Strix Halo, CPU and GPU share the same 128GB, so every byte matters
- **Kernel-tuned GPU memory** — `ttm.pages_limit=30146560` reserves 115GB of the unified pool for GPU compute
- **Always-on configuration** — sleep, suspend, hibernate, and lid switch are all disabled; power button is ignored
- **Automatic recovery** — a watchdog agent monitors all services every 5 minutes, auto-restarts failures, and only alerts when self-repair fails

The result: a quiet, headless box that boots into a fully operational AI platform and stays running 24/7.

## What Makes This Different

There are excellent projects in the Strix Halo AI space — [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) for a full orchestrated stack, [Lemonade](https://github.com/lemonade-sdk/lemonade) for AMD-optimized inference, [amd-strix-halo-toolboxes](https://github.com/kyuz0/amd-strix-halo-toolboxes) for containerized benchmarking, and [Framework community guides](https://github.com/Gygeek/Framework-strix-halo-llm-setup) for getting started. We recommend all of them.

halo-ai occupies a specific niche that none of them currently fill: **a complete AI stack compiled entirely from source, running bare metal, on a minimal headless server, optimized end-to-end for the Strix Halo unified memory architecture.**

- **Source-compiled for gfx1151** — Every GPU-accelerated binary is built with `-DAMDGPU_TARGETS=gfx1151` and ROCm Flash Attention (`rocWMMA`). No pre-built binaries, no AppImages, no generic builds. The compiler sees your exact hardware.
- **Unified memory as a first-class concern** — Strix Halo shares 128GB between CPU and GPU. halo-ai is architected around this: kernel-tuned GTT allocation (115GB for GPU), no container runtimes competing for the same memory pool, systemd isolation instead of Docker. Every architectural decision maximizes memory available for model inference.
- **Full stack, not just inference** — This is not a llama.cpp wrapper. It is 10 integrated services — LLM inference, chat UI, deep research, voice I/O, image generation, RAG, search, and workflow automation — all running on one chip with zero external dependencies.
- **Server-first, security-first** — Built for 24/7 headless operation on a minimal Arch install. No service is directly exposed to the network. Access is exclusively through SSH or an authenticated reverse proxy.

## Security Model

> **No service in halo-ai is directly accessible from the network. This is by design.**

Every service binds to `127.0.0.1` (localhost only). There is no way to reach Open WebUI, Vane, n8n, the LLM API, or any other service by connecting to the machine's IP address. This is critical because:

- **AI services have no built-in authentication** — Open WebUI, ComfyUI, llama.cpp server, and most AI tools were designed for local use. They have no concept of user authentication, rate limiting, or access control. Exposing them on `0.0.0.0` means anyone on your network can use your GPU, read your conversations, modify your workflows, and consume your resources.
- **LLM APIs accept arbitrary prompts** — An exposed OpenAI-compatible endpoint lets anyone on the network run inference against your models. On a 128GB machine running a 70B model, a single bad actor can saturate GPU compute and deny service to legitimate users.
- **Workflow engines are remote code execution** — n8n executes arbitrary workflows including shell commands, HTTP requests, and database queries. An exposed n8n instance is functionally equivalent to an open SSH session.

### How to Access Services

There are two supported methods. Both require SSH key authentication to strix-halo.

#### Method 1: SSH Tunnels (Recommended)

Add these tunnels to your SSH config. They activate automatically when you connect:

```
Host strix-halo
    HostName 10.0.0.200
    User <YOUR_USER>
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

    # Persistent connection
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 10m
    ServerAliveInterval 60
    ServerAliveCountMax 3

    # Service tunnels
    LocalForward 3000 127.0.0.1:3000   # Open WebUI
    LocalForward 3001 127.0.0.1:3001   # Vane (Perplexica)
    LocalForward 5678 127.0.0.1:5678   # n8n
    LocalForward 8080 127.0.0.1:8080   # Lemonade API
    LocalForward 8188 127.0.0.1:8188   # ComfyUI
```

Then `ssh strix-halo` and access services at `http://localhost:<port>` on your local machine. The SSH multiplexed connection stays alive for 10 minutes after your last session closes, so tunnels persist across terminal sessions.

This is the simplest and most secure method. No additional software required. Works from any machine with your SSH key.

#### Method 2: Caddy Reverse Proxy (Multi-User / Remote Access)

For accessing services from multiple devices or when SSH tunnels are impractical, deploy [Caddy](https://github.com/caddyserver/caddy) as an authenticated reverse proxy. Caddy is the only service that listens on the network.

```
# /srv/ai/configs/Caddyfile
:443 {
    tls internal

    basicauth * {
        admin $2a$14$... # bcrypt hash
    }

    handle_path /chat/* {
        reverse_proxy 127.0.0.1:3000
    }
    handle_path /research/* {
        reverse_proxy 127.0.0.1:3001
    }
    handle_path /workflows/* {
        reverse_proxy 127.0.0.1:5678
    }
    handle_path /api/* {
        reverse_proxy 127.0.0.1:8080
    }
    handle_path /comfyui/* {
        reverse_proxy 127.0.0.1:8188
    }
}
```

Caddy provides:
- **TLS encryption** (automatic self-signed or ACME certificates)
- **Basic authentication** (bcrypt-hashed passwords)
- **Single network-facing port** (443) — all other ports remain localhost-only
- **Compiled from source** using Go

### SSH Hardening

The SSH daemon on strix-halo is locked down:

```
PasswordAuthentication no       # Keys only — no brute force
ChallengeResponseAuthentication no
UsePAM no
PermitRootLogin no              # No root access
AllowUsers <YOUR_USER>               # Single authorized user
```

### Software Stack for Secure Access

| Component | Role | Source |
|-----------|------|--------|
| **OpenSSH** | Primary access method — key-only, multiplexed tunnels | System package |
| **Caddy** | Reverse proxy with TLS + auth (optional, for multi-device) | Compiled from source (Go) |
| **systemd** | All services bound to `127.0.0.1` via unit files | System |
| **ufw/nftables** | Firewall — allow SSH (22) and Caddy (443) only | System |

## Hardware Target

This stack is built exclusively for the Strix Halo unified memory architecture:

| Component | Spec |
|-----------|------|
| **APU** | AMD Ryzen AI MAX+ 395 (Strix Halo) |
| **CPU** | 16 Zen 5 cores / 32 threads, 5.19 GHz, AVX-512 |
| **GPU** | Radeon 8060S — RDNA 3.5, 40 CUs, gfx1151 |
| **NPU** | AMD XDNA 2 — 50 TOPS |
| **Memory** | 128GB LPDDR5x-8000 unified (~215 GB/s) |
| **GPU Compute** | 115 GB via GTT (kernel-tuned) |

The killer feature of Strix Halo is unified memory — CPU and GPU share the full 128GB pool. With kernel-level GTT tuning, 115GB is accessible for GPU compute. No consumer discrete GPU comes close. This means models that would require a \$10,000+ multi-GPU setup elsewhere run on a single chip here.

## What you can run

| Model | Quantization | Size | Speed |
|-------|-------------|------|-------|
| Llama 3 8B | Q4_K_M | ~5 GB | ~45 tok/s |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | ~18 GB | ~72 tok/s |
| Llama 3 70B | Q4_K_M | ~40 GB | ~15-20 tok/s |
| Llama 3 70B | Q8_0 | ~70 GB | ~8-12 tok/s |
| DeepSeek V3 (MoE) | Q4_K_M | ~95 GB | ~5-10 tok/s |
| GPT-OSS 120B (MoE) | Q4 | ~63 GB | ~40-47 tok/s |

## Services

All services bind to `127.0.0.1` only. Access via SSH tunnel or reverse proxy.

| Service | Port | Purpose |
|---------|------|---------|
| **Lemonade** | 8080 | Unified AI API (OpenAI + Ollama + Anthropic compatible) |
| **llama.cpp** | 8081 | LLM inference (HIP + Vulkan dual backends) |
| **Open WebUI** | 3000 | Chat interface with RAG, document upload, multi-model |
| **Vane** | 3001 | Deep research engine (Perplexica) |
| **SearXNG** | 8888 | Private meta-search engine |
| **Qdrant** | 6333 | Vector database for RAG embeddings |
| **n8n** | 5678 | Workflow automation (400+ integrations) |
| **whisper.cpp** | 8082 | Speech-to-text (ROCm accelerated) |
| **Kokoro** | 8083 | Text-to-speech |
| **ComfyUI** | 8188 | Image generation (PyTorch ROCm) |

## Architecture

```
                    SSH Tunnel / Caddy Reverse Proxy
                    ┌─────────────────────────────┐
                    │  Only entry point (port 22   │
                    │  or 443 with TLS + auth)     │
                    └──────────┬──────────────────-┘
                               │ localhost only
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────┐       ┌──────────────┐
│  Open WebUI  │      │    Vane      │       │     n8n      │
│  :3000       │      │  :3001       │       │   :5678      │
└──────┬───────┘      └──────┬───────┘       └──────┬───────┘
       │ OpenAI-compatible API│                      │
       ▼                     ▼                       ▼
┌──────────────────────────────────────────────────────────┐
│                   Lemonade Server :8080                   │
│          OpenAI + Ollama + Anthropic API compatible       │
└───────┬──────────────────┬───────────────────┬───────────┘
        ▼                  ▼                   ▼
   llama.cpp          whisper.cpp           Kokoro
   HIP + Vulkan       (STT)                (TTS)
        │
   ┌────┴──────────────────────────────┐
   │  ROCm 7.13  →  gfx1151           │
   │  /dev/kfd + /dev/dri (direct)     │
   │  115 GB GTT  │  ~215 GB/s BW     │
   └───────────────────────────────────┘

Supporting Services (localhost only):
  SearXNG :8888 ← Vane (web search)
  Qdrant  :6333 ← Open WebUI (RAG embeddings)
```

## Isolation Without Containers

| Layer | What It Provides | Overhead |
|-------|-----------------|----------|
| **systemd units** | Process isolation, auto-restart, `MemoryMax`/`CPUQuota`, journald logging | 0 bytes |
| **Python venvs** | Per-service dependency isolation — immune to system updates | ~50 MB each |
| **Btrfs subvolumes** | Per-service data isolation, instant snapshots, atomic rollback | 0 bytes (metadata) |
| **Snapper** | Automatic hourly/daily/weekly snapshots + pre/post on pacman ops | 0 bytes (COW) |
| **udev rules** | Persistent GPU device permissions (`/dev/kfd`, `/dev/dri`) | 0 bytes |
| **localhost binding** | All services on 127.0.0.1 — network-inaccessible without SSH/proxy | 0 bytes |

## Directory Layout

```
/srv/ai/
├── configs/          ← Shared configuration (ROCm env, SearXNG, Caddyfile)
├── systemd/          ← All service unit files
├── scripts/          ← Build and maintenance scripts
├── models/           ← Shared model storage (GGUF, safetensors)
│
├── rocm/             ← ROCm 7.13 SDK (TheRock nightly, gfx1151)
├── llama-cpp/        ← llama.cpp (build-hip/ + build-vulkan/)
├── lemonade/         ← Lemonade 10.0.1 (lemonade-server + lemonade-router)
├── whisper-cpp/      ← whisper.cpp (ROCm accelerated)
│
├── open-webui/       ← Open WebUI 0.8.10 (Python 3.12 venv)
├── vane/             ← Vane/Perplexica (Node.js 24.5)
├── searxng/          ← SearXNG (Python 3.14 venv)
├── qdrant/           ← Qdrant 1.17.0 (Rust static binary)
├── n8n/              ← n8n 2.14.0 (Node.js 24.5)
├── kokoro/           ← Kokoro TTS (Python 3.13 venv + PyTorch ROCm)
└── comfyui/          ← ComfyUI (Python 3.13 venv + PyTorch ROCm 6.2.4)
```

Each directory is a Btrfs subvolume with independent snapshot capability.

## Build Stack

Everything compiled from source on the target hardware:

| Component | Version | Compiler/Toolchain |
|-----------|---------|-------------------|
| ROCm | 7.13 (TheRock nightly) | AMD Clang 23.0 |
| llama.cpp | latest | HIP + Vulkan, gfx1151, rocWMMA FA |
| Lemonade | 10.0.1 | CMake + Ninja |
| whisper.cpp | latest | HIP, gfx1151 |
| Qdrant | 1.17.0 | Rust 1.94, cargo release |
| Caddy | latest | Go 1.24 |
| Node.js | 24.5.0 | GCC 15.2 |
| Python | 3.12.13 / 3.13.3 / 3.14.3 | GCC 15.2, `--enable-optimizations` |
| Open WebUI | 0.8.10 | pip (Python 3.12 venv) |
| Vane | latest | Yarn 4.13 (Node.js 24.5) |
| n8n | 2.14.0 | pnpm (Node.js 24.5) |
| ComfyUI | latest | PyTorch 2.7.1+rocm6.2.4 |

## Watchdog Agent

A watchdog agent runs every 5 minutes via systemd timer:

- Monitors all service health and auto-restarts failed services
- Checks GPU device availability and temperature
- Monitors disk usage and available memory
- Checks all upstream repos for available updates
- Checks for kernel and system package updates
- **Only alerts when auto-repair fails** — silent when everything is healthy

```bash
journalctl -t halo-watchdog
cat /var/log/halo-watchdog.log
```

## Snapshot Policy

Snapper manages automatic Btrfs snapshots on `/` and `/home`:

| Retention | Count |
|-----------|-------|
| Hourly | 24 |
| Daily | 14 |
| Weekly | 4 |
| Monthly | 6 |
| Yearly | 10 |
| Pacman pre/post | Automatic (snap-pac) |

## Credits & Acknowledgements


## UpdatingAll updates are protected by automatic Btrfs snapshots with auto-rollback. One command does everything:```bash/srv/ai/scripts/halo-update.sh update```That single command:1. **Snapshots** root + home before anything changes2. **Stops** all services cleanly3. **Updates** system packages + pulls all upstream repos4. **Rebuilds** only what changed (CMake for C++, pip for Python, yarn/pnpm for Node.js)5. **Starts** services and runs inference verification test6. **Rolls back automatically** if anything fails — system returns to pre-update state7. **Snapshots** the good state after success — creating a paired pre/post record### Why This MattersOn a bare-metal server with 10+ services compiled from source, a bad upstream commit in any one of them can take the entire stack down. On a containerized setup you just roll back one image. On bare metal you need filesystem-level protection.halo-ai solves this with Btrfs copy-on-write snapshots at every critical point:- **Before system updates** — `pacman -Syu` can break GPU drivers, kernel modules, or Python/Node.js- **Before service updates** — upstream git pulls can introduce breaking changes- **Before auto-repairs** — the watchdog snapshots before restarting a failed service- **Before rebuilds** — recompiling llama.cpp or Lemonade with new source can produce broken binariesRollback is instant (Btrfs COW — no data copying) and atomic (the entire filesystem reverts, not just individual files).### Manual Controls```bash# Take a manual snapshot right now/srv/ai/scripts/halo-update.sh snapshot# View available rollback points/srv/ai/scripts/halo-update.sh rollback# Check update history/srv/ai/scripts/halo-update.sh status# Snapper direct accesssnapper -c root list                    # List all root snapshotssnapper -c root undochange 10..11       # Undo changes between snapshot 10 and 11snapper -c root diff 10..11             # See what changed between snapshots```### Snapshot RetentionSnapshots are automatically cleaned up so they do not consume unlimited disk space:| Type | Retention ||------|-----------|| Hourly (timeline) | 24 || Daily (timeline) | 14 || Weekly (timeline) | 4 || Monthly (timeline) | 6 || Yearly (timeline) | 10 || Pacman pre/post (snap-pac) | 50 || Update pre/post (halo-update) | 50 || Watchdog repair | 50 |All snapshots use Btrfs COW — they consume zero additional space until the original data is modified. Even then, only the changed blocks are stored. On a 1.9TB drive this is negligible.
