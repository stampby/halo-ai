<div align="center">

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**Zero containers. Zero overhead. Every byte goes to inference.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## What is this?

A complete, self-hosted AI platform compiled entirely from source for the **AMD Ryzen AI MAX+ 395 (Strix Halo)** APU. LLM inference, chat UI, deep research, voice I/O, image generation, RAG, and workflow automation — all running bare metal on a single chip with 128GB of unified memory.

This is not a Docker wrapper. Every binary is compiled from source with `gfx1151` GPU targets, ROCm Flash Attention, and kernel-level GPU memory tuning. The result: **full 115GB GPU-accessible memory** for model inference with zero container overhead.

## Why this exists

Every other Strix Halo AI setup makes the same mistake: **containers on unified memory hardware.**

| Project | Approach | GPU Memory Available | Performance |
|---------|----------|---------------------|-------------|
| [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) | Docker Compose (13+ containers) | ~78-104 GB | 70-90% |
| [amd-strix-halo-toolboxes](https://github.com/kyuz0/amd-strix-halo-toolboxes) | Docker/Distrobox images | ~78-104 GB | 70-90% |
| [Framework llm-setup](https://github.com/Gygeek/Framework-strix-halo-llm-setup) | Shell scripts + Docker | Varies | ~85% |
| [Lemonade (official)](https://github.com/lemonade-sdk/lemonade) | AppImage / source | Full | ~100% |
| **halo-ai (this project)** | **Bare metal, compiled from source** | **Full 115 GB** | **100%** |

On a discrete GPU with dedicated VRAM, container overhead doesn't touch GPU memory. On Strix Halo, **CPU and GPU share the same 128GB pool**. Every page table, every duplicated library, every container runtime structure competes with your model for the same memory. A 10% overhead means losing ~12GB — the difference between fitting a 70B model or not.

### What we do differently

- **Compiled from source** with `-DAMDGPU_TARGETS=gfx1151` and `-DGGML_HIP_ROCWMMA_FATTN=ON`
- **Kernel-level GPU memory tuning** — `amdgpu.gttsize=117760` allocates 115GB for compute
- **systemd process isolation** — zero memory overhead, cgroup resource limits, journald logging
- **Python venvs** — dependency isolation without container duplication
- **Btrfs subvolumes per service** — instant snapshots, atomic rollback, clean removal
- **Snapper automatic snapshots** — hourly/daily/weekly retention + pre/post on every pacman operation

## Hardware Target

This stack is built exclusively for:

| Component | Spec |
|-----------|------|
| **APU** | AMD Ryzen AI MAX+ 395 (Strix Halo) |
| **CPU** | 16 Zen 5 cores / 32 threads, 5.19 GHz, AVX-512 |
| **GPU** | Radeon 8060S — RDNA 3.5, 40 CUs, gfx1151 |
| **NPU** | AMD XDNA 2 — 50 TOPS |
| **Memory** | 128GB LPDDR5x-8000 unified (~215 GB/s) |
| **GPU Compute** | 115 GB via GTT (kernel-tuned) |

## What you can run

With 115GB of GPU-accessible unified memory:

| Model | Quantization | Size | Fits? | Speed |
|-------|-------------|------|-------|-------|
| Llama 3 8B | Q4_K_M | ~5 GB | Yes | ~45 tok/s |
| Qwen 3 30B-A3B (MoE) | Q4_K_M | ~18 GB | Yes | ~72 tok/s |
| Llama 3 70B | Q4_K_M | ~40 GB | Yes | ~15-20 tok/s |
| Llama 3 70B | Q8_0 | ~70 GB | Yes | ~8-12 tok/s |
| DeepSeek V3 (MoE) | Q4_K_M | ~95 GB | Yes | ~5-10 tok/s |
| GPT-OSS 120B (MoE) | Q4 | ~63 GB | Yes | ~40-47 tok/s |

No consumer discrete GPU can fit a 70B Q8 model. Strix Halo can.

## Services

| Service | Port | Built From | Purpose |
|---------|------|------------|---------|
| **Lemonade** | 8080 | [lemonade-sdk/lemonade](https://github.com/lemonade-sdk/lemonade) | Unified AI API (OpenAI + Ollama + Anthropic compatible) |
| **llama.cpp** | 8081 | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | LLM inference (HIP + Vulkan dual backends) |
| **Open WebUI** | 3000 | [open-webui/open-webui](https://github.com/open-webui/open-webui) | Chat interface with RAG, document upload, multi-model |
| **Vane** | 3001 | [ItzCrazyKns/Vane](https://github.com/ItzCrazyKns/Vane) | Deep research engine (Perplexica) |
| **SearXNG** | 8888 | [searxng/searxng](https://github.com/searxng/searxng) | Private meta-search engine |
| **Qdrant** | 6333 | [qdrant/qdrant](https://github.com/qdrant/qdrant) | Vector database for RAG embeddings |
| **n8n** | 5678 | [n8n-io/n8n](https://github.com/n8n-io/n8n) | Workflow automation (400+ integrations) |
| **whisper.cpp** | 8082 | [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) | Speech-to-text (ROCm accelerated) |
| **Kokoro** | 8083 | [remsky/Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) | Text-to-speech |
| **ComfyUI** | 8188 | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Image generation (PyTorch ROCm) |

## Architecture

```
User Interfaces                    AI Research
┌──────────────┐                  ┌──────────────┐
│  Open WebUI  │ :3000            │    Vane      │ :3001
│  n8n         │ :5678            │  (Perplexica)│
└──────┬───────┘                  └──────┬───────┘
       │ OpenAI-compatible API           │
       ▼                                 ▼
┌──────────────────────────────────────────────┐
│              Lemonade Server                  │ :8080
│  OpenAI + Ollama + Anthropic API compatible  │
└───────┬──────────────┬───────────────┬───────┘
        ▼              ▼               ▼
   llama.cpp      whisper.cpp       Kokoro
   HIP + Vulkan   (STT)            (TTS)
        │
   ┌────┴──────────────────────────────┐
   │  ROCm 7.13  →  gfx1151           │
   │  /dev/kfd + /dev/dri (direct)     │
   │  115 GB GTT  │  ~215 GB/s BW     │
   └───────────────────────────────────┘

Supporting Services:
  SearXNG :8888 ← Vane (web search)
  Qdrant  :6333 ← Open WebUI (RAG embeddings)
  n8n     :5678 → Lemonade (LLM in workflows)
```

## Isolation Without Containers

| Layer | What It Provides | Overhead |
|-------|-----------------|----------|
| **systemd units** | Process isolation, auto-restart, `MemoryMax`/`CPUQuota`, journald logging | 0 bytes |
| **Python venvs** | Per-service dependency isolation — immune to system updates | ~50 MB each |
| **Btrfs subvolumes** | Per-service data isolation, instant snapshots, atomic rollback | 0 bytes (metadata) |
| **Snapper** | Automatic hourly/daily/weekly snapshots + pre/post on pacman ops | 0 bytes (COW) |
| **udev rules** | Persistent GPU device permissions (`/dev/kfd`, `/dev/dri`) | 0 bytes |

Clean uninstall of any service: `btrfs subvolume delete /srv/ai/<service>`

## Directory Layout

```
/srv/ai/
├── configs/          ← Shared configuration (ROCm env, SearXNG, Qdrant)
├── systemd/          ← All service unit files
├── scripts/          ← Build and maintenance scripts
├── models/           ← Shared model storage (GGUF, safetensors)
│
├── rocm/             ← ROCm 7.13 SDK (TheRock nightly, gfx1151)
├── llama-cpp/        ← llama.cpp (build-hip/ + build-vulkan/)
├── lemonade/         ← Lemonade 10.0.1 (lemonade-server + lemonade-router)
├── whisper-cpp/      ← whisper.cpp (ROCm accelerated)
│
├── open-webui/       ← Open WebUI (Python 3.13 venv)
├── vane/             ← Vane/Perplexica (Node.js 24.5)
├── searxng/          ← SearXNG (Python 3.14 venv)
├── qdrant/           ← Qdrant 1.17.0 (Rust static binary)
├── n8n/              ← n8n 2.14.0 (Node.js 24.5)
├── kokoro/           ← Kokoro TTS (Python 3.13 venv + PyTorch ROCm)
└── comfyui/          ← ComfyUI (Python 3.13 venv + PyTorch ROCm 6.2.4)
```

Each directory is a Btrfs subvolume with independent snapshot capability.

## Build Stack

Everything compiled from source:

| Component | Version | Compiler/Toolchain |
|-----------|---------|-------------------|
| ROCm | 7.13 (TheRock nightly) | AMD Clang 23.0 |
| llama.cpp | latest | HIP + Vulkan, gfx1151, rocWMMA FA |
| Lemonade | 10.0.1 | CMake + Ninja |
| whisper.cpp | latest | HIP, gfx1151 |
| Qdrant | 1.17.0 | Rust 1.94, cargo release |
| Node.js | 24.5.0 | GCC 15.2, `--prefix=/usr/local` |
| Python | 3.13.3 | GCC 15.2, `--enable-optimizations` |
| Open WebUI | latest | pip (Python 3.13 venv) |
| Vane | latest | Yarn 4.13 (Node.js 24.5) |
| n8n | 2.14.0 | pnpm (Node.js 24.5) |
| ComfyUI | latest | PyTorch 2.7.1+rocm6.2.4 |

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

## License

Apache 2.0

## Credits & Acknowledgements

This project stands on the shoulders of incredible open-source work. Special thanks to:

### Core Inspiration
- **[DreamServer](https://github.com/Light-Heart-Labs/DreamServer)** by Light-Heart-Labs — The original vision of a complete, integrated AI stack for Strix Halo. DreamServer's architecture of orchestrating 13+ services behind a unified interface was the direct inspiration for halo-ai. Their pioneering work proving that Strix Halo could run a full AI platform — not just a single model — showed what was possible. halo-ai takes that vision and rebuilds it bare-metal for maximum performance on unified memory hardware.

- **[Lemonade](https://github.com/lemonade-sdk/lemonade)** by AMD / Lemonade SDK — The unified AI serving layer that makes this entire stack practical. Lemonade's OpenAI + Ollama + Anthropic API compatibility means every frontend in this stack can talk to every backend through one interface. Their dedicated work on gfx1151 ROCm support, NPU+GPU hybrid inference, and the llamacpp-rocm nightly builds has been essential for making Strix Halo a viable AI platform. Without Lemonade, local AI on AMD hardware would still be a series of disconnected experiments.

### Upstream Projects
Every service in this stack is open source. We compile from source but contribute nothing without these teams:

| Project | Team | License | Contribution |
|---------|------|---------|-------------|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | Georgi Gerganov et al. | MIT | The inference engine that started it all |
| [Open WebUI](https://github.com/open-webui/open-webui) | Timothy Baek et al. | MIT | The best self-hosted chat interface |
| [Vane (Perplexica)](https://github.com/ItzCrazyKns/Vane) | ItzCrazyKns | MIT | AI-powered deep research |
| [whisper.cpp](https://github.com/ggerganov/whisper.cpp) | Georgi Gerganov | MIT | Fast speech-to-text |
| [Kokoro](https://github.com/remsky/Kokoro-FastAPI) | remsky | Apache 2.0 | High-quality TTS |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | comfyanonymous | GPL 3.0 | Node-based image generation |
| [SearXNG](https://github.com/searxng/searxng) | SearXNG team | AGPL 3.0 | Privacy-respecting search |
| [Qdrant](https://github.com/qdrant/qdrant) | Qdrant team | Apache 2.0 | Vector search for RAG |
| [n8n](https://github.com/n8n-io/n8n) | n8n GmbH | Sustainable Use | Workflow automation |
| [ROCm / TheRock](https://github.com/ROCm/TheRock) | AMD | Various | GPU compute stack for gfx1151 |

### Community
- The **Framework laptop community** for extensive Strix Halo testing and benchmarks
- **kyuz0** for [amd-strix-halo-toolboxes](https://github.com/kyuz0/amd-strix-halo-toolboxes) Docker images and benchmark data
- **Gygeek** for [Framework-strix-halo-llm-setup](https://github.com/Gygeek/Framework-strix-halo-llm-setup) guides
- The **Arch Linux** community for bleeding-edge packages
- Everyone contributing to ROCm gfx1151 support in kernel, Mesa, and userspace

## Watchdog Agent

halo-ai includes a watchdog agent that runs every 5 minutes via systemd timer. It:

- Monitors all service health and auto-restarts failed services
- Checks GPU device availability and temperature
- Monitors disk usage and available memory
- Checks all upstream repos for updates (git fetch)
- Checks for kernel and system package updates
- **Only alerts when auto-repair fails** — silent when everything is healthy

Notifications go to the desktop (via `notify-send`) and systemd journal. Check the log:
```bash
journalctl -t halo-watchdog        # Watchdog entries
cat /var/log/halo-watchdog.log     # Full log
```
