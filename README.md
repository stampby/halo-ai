<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**109 tok/s. Zero containers. 115GB GPU memory. Compiled from source.**

*stamped by the architect*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## What is this?

A complete AI platform for the **AMD Ryzen AI MAX+ 395** — LLM inference, chat, deep research, voice, image generation, RAG, and workflows. 13 services, 11 autonomous agents, 78 tools. All bare metal, all compiled from source, all on one chip with 128GB unified memory.

## Why Bare Metal?

- **Containers add 15-20% overhead** on GPU workloads. When you have 115GB of unified memory on a single chip, every watt and every byte should go to inference, not orchestration.
- **Compiled from source** means native gfx1151 optimizations that pre-built binaries miss. That's where 109 tok/s comes from.
- **Weekly source compiles** catch upstream breaking changes before they cascade. Freeze/thaw rollback means nothing breaks.
- **You own the whole stack.** No package manager decides when your AI server goes down.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/install.sh | bash
```

Interactive installer — username, passwords, hostname, which services to enable. Sensible defaults. Default Caddy password is `Caddy` — change it immediately.

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Lemonade | 8080 | Unified AI API (OpenAI/Ollama/Anthropic compatible) |
| llama.cpp | 8081 | LLM inference — Vulkan + HIP dual backends |
| Open WebUI | 3000 | Chat with RAG, documents, multi-model |
| Vane | 3001 | Deep research with cited sources |
| SearXNG | 8888 | Private meta-search |
| Qdrant | 6333 | Vector DB for RAG |
| n8n | 5678 | Workflow automation |
| whisper.cpp | 8082 | Speech-to-text |
| Kokoro | 8083 | Text-to-speech (54 voices) |
| ComfyUI | 8188 | Image generation |
| Dashboard | 3003 | GPU metrics + service health |
| Gaia API | 8090 | Agent framework server |
| Gaia MCP | 8765 | Model Context Protocol bridge |

All services bind to `127.0.0.1` — access via Caddy reverse proxy.

## Performance

| Model | Speed | VRAM |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **109 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

Full benchmarks with thermals, memory, and backend comparisons: [BENCHMARKS.md](BENCHMARKS.md)

## Architecture

```
    Browser --> https://strixhalo
              |
    +---------v----------+
    |   Caddy :443       |  <-- TLS + auth
    |   Lemonade :8080   |  <-- OpenAI-compatible API
    +--+------+------+---+
       v      v      v
  llama.cpp whisper  Kokoro    <-- GPU inference (gfx1151, 115GB GTT)
       |
  Open WebUI  Vane  n8n       <-- Apps
  ComfyUI  Qdrant  SearXNG    <-- Tools
```

## Docs

| Guide | What it covers |
|-------|----------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, GPU backends |
| [Services](docs/SERVICES.md) | Ports, configs, health checks |
| [Security](docs/SECURITY.md) | Firewall, SSH, TLS, password rotation |
| [Stack Protection](docs/STACK-PROTECTION.md) | Why Arch updates won't break your stack |
| [Benchmarks](BENCHMARKS.md) | Full performance data |
| [Blueprints](docs/BLUEPRINTS.md) | Roadmap and planned features |
| [Autonomous Pipeline](docs/AUTONOMOUS-PIPELINE.md) | Zero-human game studio pipeline |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [VPN Access](docs/VPN.md) | WireGuard setup |

## Credits

**Designed and built by the architect** — every script, every service, every agent. From source. No shortcuts.

Built on [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) by Light-Heart-Labs. Powered by [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Community: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), and the Framework/Arch Linux communities.

## License

Apache 2.0
