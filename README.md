<div align="center">

<img src="assets/family/01-halo-ai_00001_.png?v=2" width="280" alt="halo ai"/>

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**90 tok/s. Zero containers. 115GB GPU memory. Compiled from source.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## meet the ai family

<div align="center">

<img src="assets/family/13-family-group_00001_.png?v=2" width="720" alt="the ai family"/>

</div>

---

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/install.sh | bash
```

The installer walks you through setup — username, passwords, hostname, and which services to enable. All settings have sensible defaults. Default Caddy password is `Caddy` — **change it immediately after install.**

## What is this?

A complete AI platform for the **AMD Ryzen AI MAX+ 395** — LLM inference, chat, deep research, voice, image generation, RAG, and workflows. All bare metal, all compiled from source, all on one chip with 128GB unified memory.

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Lemonade | 8080 | Unified AI API (OpenAI/Ollama/Anthropic compatible) |
| llama.cpp | 8081 | LLM inference — Vulkan + HIP dual backends |
| Open WebUI | 3000 | Chat with RAG, documents, multi-model |
| Vane | 3001 | Deep research (Perplexica) |
| SearXNG | 8888 | Private search |
| Qdrant | 6333 | Vector DB for RAG |
| n8n | 5678 | Workflow automation |
| whisper.cpp | 8082 | Speech-to-text |
| Kokoro | 8083 | Text-to-speech |
| ComfyUI | 8188 | Image generation |
| Dashboard | 3003 | GPU metrics + service health |

All services bind to `127.0.0.1` — access via `https://strixhalo` through the Caddy reverse proxy.

## Performance

| Model | Speed | Size |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **90 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |
| Llama 3 70B Q8 | ~10 tok/s | 70 GB |

Full benchmarks: [BENCHMARKS.md](BENCHMARKS.md)

## Architecture

```
    Browser → https://strixhalo
              │
    ┌─────────▼──────────┐
    │   Caddy :443       │  ← TLS + auth
    │   Lemonade :8080   │  ← OpenAI-compatible API
    └──┬──────┬──────┬───┘
       ▼      ▼      ▼
  llama.cpp whisper  Kokoro    ← GPU inference (gfx1151, 115GB GTT)
       │
  Open WebUI  Vane  n8n       ← Apps
  ComfyUI  Qdrant  SearXNG    ← Tools
```

## Agents

Optional autonomous agents that extend your halo-ai stack. Enable, disable, or configure through the web GUI.

| Agent | Role | Status |
|---|---|---|
| **[Meek](https://github.com/bong-water-water-bong/meek)** | Security monitoring — 9 Reflex agents guard your system 24/7 | Public |
| **Echo** | Social media manager — monitors and posts across 5 platforms | Private |
| *More coming soon* | | |

All agents integrate with the halo-ai dashboard and can be toggled on/off at any time.

See [Agent Marketplace](docs/AGENTS.md) for full documentation.

## Docs

| Guide | What it covers |
|-------|----------------|
| [Agent Marketplace](docs/AGENTS.md) | Available agents, planned agents, custom agent guide |
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, GPU backends |
| [Services](docs/SERVICES.md) | All services — ports, configs, health checks |
| [Security](docs/SECURITY.md) | Firewall, SSH, TLS certs, password rotation |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues, fixes, command reference |
| [VPN Access](docs/VPN.md) | WireGuard, Tailscale, Nebula setup |
| [Benchmarks](BENCHMARKS.md) | Full performance data |
| [Server Access](docs/SECURITY.md#caddy-authentication) | Hostname setup, HTTPS certs, API access |

## Tools

```bash
halo-models.sh list              # Browse models
halo-models.sh download <name>   # Download a model
halo-models.sh activate <name>   # Switch models (auto-benchmark)
halo-driver-swap.sh vulkan       # Switch GPU backend
halo-backup.sh                   # Manual backup
```

## Credits

Built on [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) by Light-Heart-Labs — the project that proved a single Strix Halo chip can replace a rack of cloud services. Their open-source dashboard powers the halo-ai control center.

Powered by [Lemonade SDK](https://github.com/lemonade-sdk/lemonade) (AMD), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), and [ROCm](https://github.com/ROCm/TheRock).

Community: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), and the Framework/Arch Linux communities.

## License

Apache 2.0
