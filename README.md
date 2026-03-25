<div align="center">

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**89 tok/s. Zero containers. 115GB GPU memory. Compiled from source.**

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

</div>

---

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/bong-water-water-bong/halo-ai/main/install.sh | bash
```

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
| Dashboard | 3003 | GPU metrics + service health (DreamServer fork) |

All services bind to `127.0.0.1`. Access via [SSH tunnel or Caddy reverse proxy](SECURITY.md).

## Performance

| Model | Speed | Size |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **89 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |
| Llama 3 70B Q8 | ~10 tok/s | 70 GB |

Full benchmarks: [BENCHMARKS.md](BENCHMARKS.md)

## Architecture

```
    SSH / Caddy (only network entry point)
              │
    ┌─────────▼──────────┐
    │   Lemonade :8080   │  ← OpenAI-compatible API
    └──┬──────┬──────┬───┘
       ▼      ▼      ▼
  llama.cpp whisper  Kokoro    ← GPU inference (gfx1151, 115GB GTT)
       │
  Open WebUI :3000             ← Chat UI
  Vane :3001                   ← Deep research
  n8n :5678                    ← Workflows
  ComfyUI :8188                ← Image gen
  Qdrant :6333  SearXNG :8888  ← RAG + search
```

## Tools

```bash
halo-models.sh list              # Browse models for Strix Halo
halo-models.sh download <name>   # Download a model
halo-models.sh activate <name>   # Switch models (auto-benchmark)
halo-driver-swap.sh vulkan       # Switch to Vulkan backend
halo-driver-swap.sh hip          # Switch to HIP/ROCm backend
halo-update.sh update            # Update everything (snapshot-protected)
halo-proxy-setup.sh              # Enable Caddy reverse proxy
halo-backup.sh                   # Backup service data
```

## Autonomous Agent

The halo-ai agent runs continuously:
- Monitors all services every 30s, auto-restarts failures
- Btrfs snapshot before every repair
- GPU health, thermals, memory monitoring
- Auto-applies system security patches
- Tracks inference performance trends
- **Silent unless it cannot fix something**

## VS Code / GitHub Copilot (Optional)

<!-- Local Copilot is possible via the Lemonade VS Code extension but is not part of the core stack. -->
Local Copilot can be configured to run on your Strix Halo for private, offline code completion. See the fork for details: https://github.com/bong-water-water-bong/lemonade-vscode

## Docs

- [SECURITY.md](SECURITY.md) — Access model, SSH config, Caddy setup, firewall
- [BENCHMARKS.md](BENCHMARKS.md) — Full performance data
- [Credits](#credits--acknowledgements)

## Accessing Your Halo AI Server

Instead of remembering your server's IP address, set up a local hostname so that typing `https://strixhalo` in your browser takes you directly to the Halo AI web GUI.

> **Note:** Replace `<YOUR_SERVER_IP>` with the actual local IP of your Halo AI server (e.g., `xxx.xxx.xxx.100`).

### Method 1: Router DNS (Recommended)

Configure your router to resolve `strixhalo` — works for every device on your network automatically.

<details>
<summary><strong>ASUS (ASUSWRT / Merlin)</strong></summary>

1. Log in to your router at `http://router.asus.com` or `http://xxx.xxx.xxx.1`
2. Navigate to **LAN** → **DHCP Server**
3. Enable **Manual Assignment** and assign your server a static IP
4. For hostname resolution, add a custom DNS entry:
   - Hostname: `strixhalo`
   - IP: `<YOUR_SERVER_IP>`
5. Click **Apply**

On **Merlin** firmware, you can also SSH in and run:
```bash
echo "address=/strixhalo/<YOUR_SERVER_IP>" >> /jffs/configs/dnsmasq.conf.add
service restart_dnsmasq
```

</details>

<details>
<summary><strong>TP-Link</strong></summary>

1. Log in at `http://192.168.0.1` or `http://tplinkwifi.net`
2. Go to **DHCP** → **Address Reservation** and lock in your server's IP
3. TP-Link consumer routers don't support custom local DNS — use the hosts file method below

</details>

<details>
<summary><strong>Netgear</strong></summary>

1. Log in at `http://routerlogin.net`
2. **Advanced** → **Setup** → **LAN Setup** → **Address Reservation**
3. Assign a fixed IP to your server's MAC address
4. For hostname resolution, use the hosts file method below

</details>

<details>
<summary><strong>Linksys</strong></summary>

1. Log in at `http://192.168.1.1` or via the Linksys app
2. **Connectivity** → **Local Network** → **DHCP Reservations**
3. Assign your server a static IP
4. For hostname resolution, use the hosts file method below

</details>

<details>
<summary><strong>pfSense / OPNsense</strong></summary>

**pfSense:**
1. **Services** → **DNS Resolver** → **Host Overrides** → **Add**
2. Host: `strixhalo`, IP: `<YOUR_SERVER_IP>`
3. **Save** and **Apply Changes**

**OPNsense:**
1. **Services** → **Unbound DNS** → **Overrides** → **Host Overrides** → **Add**
2. Hostname: `strixhalo`, IP: `<YOUR_SERVER_IP>`
3. **Save** and **Apply**

</details>

<details>
<summary><strong>OpenWrt</strong></summary>

Via LuCI:
1. **Network** → **DHCP and DNS** → **Hostnames** → **Add**
2. Hostname: `strixhalo`, IP: `<YOUR_SERVER_IP>`
3. **Save & Apply**

Via SSH:
```bash
uci add dhcp domain
uci set dhcp.@domain[-1].name='strixhalo'
uci set dhcp.@domain[-1].ip='<YOUR_SERVER_IP>'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

</details>

### Method 2: Hosts File (Per Device)

Add the entry directly on each machine that needs access.

| OS | File | Entry |
|---|---|---|
| **Linux** | `/etc/hosts` | `<YOUR_SERVER_IP>    strixhalo` |
| **macOS** | `/etc/hosts` | `<YOUR_SERVER_IP>    strixhalo` |
| **Windows** | `C:\Windows\System32\drivers\etc\hosts` | `<YOUR_SERVER_IP>    strixhalo` |

```bash
# Linux / macOS
sudo sh -c 'echo "<YOUR_SERVER_IP>    strixhalo" >> /etc/hosts'

# macOS — also flush DNS cache
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
```

### Method 3: Local DNS Server (Pi-hole / AdGuard Home)

**Pi-hole:**
```bash
echo "<YOUR_SERVER_IP> strixhalo" | sudo tee -a /etc/pihole/custom.list
pihole restartdns
```

**AdGuard Home:**
1. **Filters** → **DNS rewrites** → **Add DNS rewrite**
2. Domain: `strixhalo`, Answer: `<YOUR_SERVER_IP>`

### API Access from the Command Line

```bash
# Chat with the LLM
curl https://strixhalo/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"default","messages":[{"role":"user","content":"Hello"}]}'

# Check Web UI status
curl -s -o /dev/null -w "%{http_code}" https://strixhalo/chat/

# Search via SearXNG
curl "https://strixhalo/search?q=local+AI&format=json"
```

### SSH Access

Generate an SSH key pair if you don't have one:

```bash
ssh-keygen -t ed25519
```

A public key looks like this:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKeyDoNotUseThis1234567890abcdef user@hostname
```

Add your public key to the server's `~/.ssh/authorized_keys`, then connect:

```bash
ssh <YOUR_USER>@strixhalo
```

---

## Credits & Acknowledgements

### DreamServer — The Project That Started It All

Before anything else, massive respect and gratitude to **[DreamServer](https://github.com/Light-Heart-Labs/DreamServer)** and the Light-Heart-Labs team.

DreamServer is the reason halo-ai exists. Full stop.

They were the first to look at the Strix Halo chip and see not just an inference engine, but a complete AI platform. While everyone else was benchmarking single models, Light-Heart-Labs built an entire ecosystem — LLM inference, chat UI, voice I/O, RAG pipelines, autonomous agents, image generation, workflow automation, privacy tools, and a monitoring dashboard — all integrated, all working together, all on one chip.

That vision is what halo-ai is built on. The architecture, the service selection, the idea that a single Strix Halo box can replace a rack of cloud services — that came from DreamServer. Their open-source dashboard panel is what powers the halo-ai control center. We did not just take inspiration — we directly forked their work and built on it.

**Fork**: [github.com/bong-water-water-bong/DreamServer](https://github.com/bong-water-water-bong/DreamServer)

### Lemonade SDK

**[Lemonade](https://github.com/lemonade-sdk/lemonade)** by AMD is the backbone of this stack. Their unified API layer provides OpenAI, Ollama, and Anthropic compatibility through a single endpoint. Their dedicated engineering on gfx1151 ROCm support, NPU+GPU hybrid inference, and the llamacpp-rocm nightly builds turned scattered hardware support into a production-ready platform. Without Lemonade, Strix Halo AI would still be a series of disconnected experiments.

### Upstream Projects

Every service in this stack is open source. We compile from source, but we build nothing — these teams do:

| Project | What It Does | License |
|---------|-------------|---------|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | The LLM inference engine that powers the entire stack | MIT |
| [Open WebUI](https://github.com/open-webui/open-webui) | Full-featured chat interface with RAG and multi-model support | MIT |
| [Vane (Perplexica)](https://github.com/ItzCrazyKns/Vane) | AI-powered deep research with cited sources | MIT |
| [whisper.cpp](https://github.com/ggerganov/whisper.cpp) | Fast, GPU-accelerated speech-to-text | MIT |
| [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) | High-quality text-to-speech API | Apache 2.0 |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Node-based image generation pipeline | GPL 3.0 |
| [SearXNG](https://github.com/searxng/searxng) | Privacy-respecting meta-search engine | AGPL 3.0 |
| [Qdrant](https://github.com/qdrant/qdrant) | High-performance vector database for RAG | Apache 2.0 |
| [n8n](https://github.com/n8n-io/n8n) | Workflow automation with 400+ integrations | Sustainable Use |
| [Caddy](https://github.com/caddyserver/caddy) | Reverse proxy with automatic TLS | Apache 2.0 |
| [ROCm / TheRock](https://github.com/ROCm/TheRock) | AMD GPU compute stack for gfx1151 | Various |

### Community

- [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes) — Docker toolboxes and comprehensive backend benchmarks
- [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup) — Framework laptop setup guides
- The **Framework laptop community** for extensive hardware testing
- The **Arch Linux** community for bleeding-edge packages
- Everyone contributing to ROCm gfx1151 support in kernel, Mesa, and userspace

## License

Apache 2.0
