# strix-halo AI Stack

Bare-metal AI inference stack compiled from source for AMD Ryzen AI MAX+ 395 (Strix Halo).

## Hardware
- **CPU**: AMD Ryzen AI MAX+ 395 (16C/32T, Zen 5, AVX-512, up to 5.19 GHz)
- **GPU**: Radeon 8060S (RDNA 3.5, 40 CUs, gfx1151)
- **NPU**: AMD XDNA 2 (50 TOPS)
- **RAM**: 128GB LPDDR5x-8000 unified memory (~215 GB/s bandwidth)
- **Storage**: 1.9TB YMTC NVMe (Btrfs on LVM)
- **OS**: Arch Linux, kernel 6.19.9

## Why Bare Metal (No Containers)

This stack runs directly on the host — no Docker, Podman, LXD, or VMs. This is a deliberate architectural choice driven by the unique properties of Strix Halo's unified memory architecture.

### The Memory Problem

Strix Halo's killer feature is 128GB of LPDDR5x shared between CPU and GPU. Every byte of memory that goes to container overhead is a byte stolen from model inference. At Q4 quantization, that's roughly 1 billion parameters per GB — container overhead directly translates to smaller models or shorter context windows.

| Approach | GPU Memory Visible | Performance | Overhead |
|----------|-------------------|-------------|----------|
| **Bare metal** | ~115 GB (full GTT) | 100% | Zero |
| Docker/Podman | ~78-104 GB | 70-90% | Per-container page tables, duplicated libs |
| LXD/Incus | ~100-110 GB | 90-95% | Kernel memory structs per container |

On a discrete GPU with dedicated VRAM, container overhead doesn't touch GPU memory. On a unified memory APU like Strix Halo, **everything competes for the same pool**. A 10% overhead means losing ~12GB — that's the difference between fitting a 70B model or not.

### The GPU Passthrough Tax

ROCm GPU access in containers requires passing through `/dev/kfd` and `/dev/dri`, mapping the ROCm library tree, and matching host/container driver versions. Community benchmarks on Strix Halo consistently show:

- **10-30% slower inference** in Docker vs bare metal
- **Model loading past 64GB significantly slower** in containers (tracked in llama.cpp #15018)
- **Additional configuration complexity** for GPU memory allocation (gttsize, TTM limits) that interacts poorly with container memory cgroups

### What We Use Instead

Zero-overhead isolation using tools the OS already provides:

| Layer | What It Provides |
|-------|-----------------|
| **systemd units** | Process isolation, auto-restart, resource limits (MemoryMax, CPUQuota), logging via journald |
| **DynamicUser=yes** | Each service runs as its own ephemeral user — no shared state, no privilege escalation |
| **Python venvs** | Dependency isolation per Python service — immune to system package updates |
| **Btrfs subvolumes** | Per-service data isolation, instant snapshots, atomic rollback. Clean uninstall = `btrfs subvolume delete` |
| **Snapper** | Automatic hourly/daily/weekly snapshots with retention policies. Pre/post snapshots on every pacman operation (snap-pac) |

This gives us:
- **Dependency isolation** (the actual problem containers solve) via venvs and separate Node.js installs
- **Process isolation** via systemd with cgroup resource limits
- **Rollback** via Btrfs snapshots (better than container images — we can roll back the entire system atomically)
- **Zero memory overhead** — every byte goes to model inference
- **Direct GPU access** — no passthrough, no driver version mismatches, no performance penalty

### When Containers Would Make Sense

If this were a multi-tenant server, a cloud deployment, or running on hardware with dedicated GPU VRAM, containers would be the right call. For a single-purpose local AI inference machine with unified memory, bare metal is the correct choice.

## Services

| Service | Port | Purpose | Isolation |
|---------|------|---------|-----------|
| Lemonade | 8080 | Unified LLM API (OpenAI-compatible) | systemd + bare metal (GPU) |
| llama.cpp | 8081 | LLM inference (HIP + Vulkan) | systemd + bare metal (GPU) |
| Open WebUI | 3000 | Chat interface | systemd + Python venv |
| Vane (Perplexica) | 3001 | Deep research engine | systemd + Node.js |
| SearXNG | 8888 | Private web search | systemd + Python venv |
| Qdrant | 6333 | Vector DB for RAG | systemd + Rust static binary |
| n8n | 5678 | Workflow automation | systemd + Node.js |
| whisper.cpp | 8082 | Speech-to-text | systemd + bare metal (GPU) |
| Kokoro | (TBD) | Text-to-speech | systemd + Python venv |
| ComfyUI | 8188 | Image generation | systemd + Python venv (GPU) |

## Service Connectivity

```
                    ┌─────────────┐
                    │  Open WebUI  │ :3000
                    │  Vane        │ :3001
                    │  n8n         │ :5678
                    └──────┬──────┘
                           │ OpenAI-compatible API
                    ┌──────▼──────┐
                    │  Lemonade   │ :8080
                    └──────┬──────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         llama.cpp    whisper.cpp    Kokoro
         (HIP+Vulkan) (STT)         (TTS)
              │
         ┌────┴────┐
         │ ROCm    │ → /dev/kfd, /dev/dri (direct access)
         │ gfx1151 │
         └─────────┘

    Vane ──→ SearXNG :8888  (web search)
    Open WebUI ──→ Qdrant :6333  (RAG/embeddings)
    n8n ──→ Lemonade :8080  (LLM calls from workflows)
```

## Directory Layout

Each service lives in its own Btrfs subvolume under `/srv/ai/`:

```
/srv/ai/
├── configs/          ← Shared configuration files
├── systemd/          ← Service unit files
├── scripts/          ← Build and maintenance scripts
├── rocm/             ← ROCm SDK (TheRock nightly, gfx1151)
├── llama-cpp/        ← llama.cpp (HIP + Vulkan builds)
├── lemonade/         ← Lemonade server
├── whisper-cpp/      ← whisper.cpp
├── open-webui/       ← Open WebUI (Python venv)
├── vane/             ← Vane/Perplexica (Node.js)
├── searxng/          ← SearXNG (Python venv)
├── qdrant/           ← Qdrant vector DB (Rust)
├── n8n/              ← n8n workflows (Node.js)
├── kokoro/           ← Kokoro TTS (Python venv)
├── comfyui/          ← ComfyUI (Python venv)
└── models/           ← Shared model storage (GGUF, safetensors, etc.)
```

## GPU Memory Configuration

Kernel parameter `amdgpu.gttsize=117760` allocates ~115GB for GPU compute via GTT (Graphics Translation Table). This is set in the systemd-boot entry at `/boot/loader/entries/`.

## Snapshot Policy

Snapper manages automatic Btrfs snapshots:
- **Hourly**: 24 retained
- **Daily**: 14 retained
- **Weekly**: 4 retained
- **Monthly**: 6 retained
- **Yearly**: 10 retained
- **Pacman operations**: Pre/post snapshot on every install/remove/upgrade (snap-pac)
