<div align="center">

<img src="https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**109 tok/s. Zero containers. 115GB GPU memory. Compiled from source.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## meet the ai family

<div align="center">

<img src="https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/assets/avatars/family.svg" alt="the ai family" width="720">

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
| **Gaia API** | 8090 | AMD agent framework — OpenAI-compatible agent server |
| **Gaia MCP** | 8765 | Model Context Protocol bridge for agent tools |

All services bind to `127.0.0.1` — access via `https://strixhalo` through the Caddy reverse proxy.

## The AI Family

14 autonomous agents run as individual systemd services, powered by [AMD Gaia](https://github.com/amd/gaia). Each agent is a Lego block — install or remove at will.

**Core family:**

| Agent | Role | Service |
|-------|------|---------|
| **halo** | The stack — system orchestrator | `halo-halo.service` |
| **echo** | Social media — public face of the family | `halo-echo.service` |
| **meek** | Security chief — commands the Reflex group | `halo-meek.service` |
| **amp** | Audio engineer — music, voice, sound | `halo-amp.service` |
| **bounty** | Bug hunter — offensive security | `halo-bounty.service` |

**Reflex group** (meek's team — 9 security agents):

| Agent | Role | Service |
|-------|------|---------|
| **pulse** | Health — system vitals | `halo-pulse.service` |
| **ghost** | Secrets — credential scanning | `halo-ghost.service` |
| **gate** | Firewall — network boundaries | `halo-gate.service` |
| **shadow** | Integrity — file change detection | `halo-shadow.service` |
| **fang** | Intrusion — threat detection | `halo-fang.service` |
| **mirror** | PII scan — privacy enforcement | `halo-mirror.service` |
| **vault** | Backup — data protection | `halo-vault.service` |
| **net** | Network — connectivity monitoring | `halo-net.service` |
| **shield** | Protection — system hardening | `halo-shield.service` |

```bash
# Manage agents like Lego blocks
manage.sh install all       # spin up everyone
manage.sh remove fang       # pull out just fang
manage.sh install pulse     # add pulse back
manage.sh status            # see who's running
```

## Performance

| Model | Speed | Size |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **109 tok/s** | 18 GB |
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

14 autonomous agents running as systemd services, powered by [AMD Gaia](https://github.com/amd/gaia). Each is a Lego block — add or remove at will.

See [The AI Family](docs/AGENTS.md) for full documentation, personas, and management commands.

## Docs

| Guide | What it covers |
|-------|----------------|
| [The AI Family](docs/AGENTS.md) | 14 agents — personas, roles, management, Gaia backend |
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, GPU backends |
| [Services](docs/SERVICES.md) | All services — ports, configs, health checks |
| [Security](docs/SECURITY.md) | Firewall, SSH, TLS certs, password rotation |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues, fixes, command reference |
| [VPN Access](docs/VPN.md) | WireGuard, Tailscale, Nebula setup |
| [Stack Protection](docs/STACK-PROTECTION.md) | Why Arch updates won't break your AI stack |
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
