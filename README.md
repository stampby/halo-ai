<div align="center">

🌐 **English** | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### The bare-metal AI stack for AMD Strix Halo

**91 tok/s. 42 services. 123GB GPU memory. Compiled from source. I know kung fu.**

*built by CLI — stamped by the architect*

[![CI](https://github.com/stampby/halo-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/stampby/halo-ai/actions/workflows/ci.yml)
[![CodeQL](https://github.com/stampby/halo-ai/actions/workflows/codeql.yml/badge.svg)](https://github.com/stampby/halo-ai/actions/workflows/codeql.yml)
[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **New here?** Start with the [tutorials](#tutorials) — full video walkthroughs from install to autonomous operation.

---

## What is this?

A complete AI platform for the **AMD Ryzen AI MAX+ 395** — LLM inference, chat, deep research, voice, image generation, RAG, and workflows. Autonomous pipelines for game development, music production, and video production. 42 services, 17 autonomous agents, 98 tools, 7 Discord bots. All bare metal, all compiled from source, all on one chip with 128GB unified memory. Boot to ready: 19.3 seconds.

**Talk to it.** Speak to Halo, see the text, hear the response. Every tool, every agent, every feature — controlled by your voice. Vibe coding at home, out of the box, on your own hardware. *"Open the pod bay doors, HAL."*

## Why Bare Metal?

- **Containers add 15-20% overhead** on GPU workloads. When you have 123GB of unified memory on a single chip, every watt and every byte should go to inference, not orchestration. *"Do not try and bend the spoon. Instead, only try to realize the truth: there is no container."*
- **Compiled from source** means native gfx1151 optimizations that pre-built binaries miss. That's where 91 tok/s comes from.
- **No timers. No cron. Total AI.** Agents don't check on a schedule — they watch conditions and act when something changes. Service goes down? Detected and repaired before you notice. GPU overheats? Reported the moment it happens. Not every 30 seconds. *The moment.* I'm sorry Dave, but this stack doesn't sleep.
- **Survives Arch rolling release.** Freeze the stack, let pacman update, agents detect if anything broke, thaw to rollback in 30 seconds. This is why halo-ai runs on Arch without fear. *"It's just a flesh wound."*
- **You own the whole stack.** No package manager decides when your AI server goes down. *"My precious."*

## Install — Two Ways

### Option A — Install Script (on your machine)

> Compiles 18 components from source. Always dry-run first.

**Requirements:** AMD Strix Halo, Arch Linux, internet, 2-3 hours.

```bash
git clone https://github.com/stampby/halo-ai.git
cd halo-ai
./install.sh --dry-run    # Validate first
./install.sh              # Build everything
sudo reboot
```

Follow the prompts. Defaults are sensible. Password auto-generated if left blank.

### Option B — USB Drive (plug in and boot)

> Skip the install entirely. Full stack on a USB SSD. Plug into any Strix Halo machine, boot, talk.

**Requirements:** 256GB+ USB SSD (Samsung T7 recommended), any Strix Halo machine.

```bash
git clone https://github.com/stampby/halo-ai.git
cd halo-ai
sudo ./scripts/halo-build-usb.sh /dev/sdX    # Build to USB
```

Boot from USB → autologin → voice assistant starts. Nothing touches the host machine.

Full guide: [USB-PORTABLE.md](docs/USB-PORTABLE.md)

### What NOT to do

- **Do not run as root** — `./install.sh` not `sudo ./install.sh`
- **Do not skip the dry-run** on first install
- **Do not pipe curl to bash** — clone the repo first

### Security

- All downloads verified with **SHA256 checksums**
- Python sources **GPG-verified** when possible
- All services bound to `127.0.0.1` behind Caddy auth
- SSH key-only, root login disabled, fail2ban active
- Meek runs a **17-check security audit** every 24 hours
- **axios supply chain attack mitigated** — version pinned, postinstall scripts blocked
- **Dependabot** + **CodeQL** scanning on every push
- npm/pip supply chain monitoring via Sentinel

### Accessing from other machines

All services are on `127.0.0.1` behind Caddy. To access from other devices on your LAN, add these to your hosts file:

**Linux/Mac** — `/etc/hosts`:
```
10.0.0.131    strixhalo chat.strixhalo research.strixhalo search.strixhalo n8n.strixhalo comfyui.strixhalo gaia.strixhalo
```

**Windows** — run PowerShell as Administrator:
```
Add-Content C:\Windows\System32\drivers\etc\hosts "10.0.0.131    strixhalo chat.strixhalo research.strixhalo search.strixhalo n8n.strixhalo comfyui.strixhalo gaia.strixhalo"
```

Replace `10.0.0.131` with your Strix Halo's IP. Then open any service in your browser:

| URL | Service |
|-----|---------|
| `http://strixhalo` | Landing page |
| `http://chat.strixhalo` | Open WebUI |
| `http://research.strixhalo` | Deep Research (Vane) |
| `http://gaia.strixhalo` | Gaia Agent UI |
| `http://comfyui.strixhalo` | Image Generation |
| `http://n8n.strixhalo` | Workflow Automation |
| `http://search.strixhalo` | Private Search |

### Re-running

The installer is fully **idempotent** — safe to run multiple times. Existing configs are preserved, already-installed tools are skipped, secrets are not overwritten.

## Features

### AI & Inference
- **LLM chat** — [Open WebUI](https://github.com/open-webui/open-webui) with RAG, multi-model, document upload
- **Deep research** — [Vane](https://github.com/ItzCrazyKns/Vane) with cited sources and private search
- **Image generation** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) on 123GB GPU, SDXL, Flux
- **Video generation** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) on ROCm 6.3
- **Music generation** — [MusicGen](https://github.com/facebookresearch/audiocraft) by Meta, local GPU inference
- **Speech-to-text** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) compiled for gfx1151
- **Text-to-speech** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) with 54 natural voices
- **Code assistant** — Qwen2.5 Coder 7B on llama.cpp, 48.6 tok/s
- **Object detection** — [YOLO](https://github.com/ultralytics/ultralytics) v8, real-time inference
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, compiled from source
- **Translation** — [Argos Translate](https://github.com/argosopentech/argos-translate), offline multi-language
- **Fine-tuning** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), train your own models locally
- **Unified API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, OpenAI/Ollama/Anthropic compatible

### Agents — [docs](docs/AGENTS.md)
- **17 autonomous agents** on [AMD Gaia](https://github.com/amd/gaia) with 98 tools
- **[Echo](https://github.com/stampby/echo)** — public face, Reddit bridge, Discord, social media
- **[Meek](https://github.com/stampby/meek)** — security chief, 9 Reflex sub-agents ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — bug hunter, offensive security, Halo's brother
- **[Amp](https://github.com/stampby/amp)** — audio engineer, voice cloning, music production
- **[Sentinel](https://github.com/stampby/sentinel)** — auto PR review, code gating
- **[Mechanic](https://github.com/stampby/mechanic)** — hardware diagnostics, system monitoring
- **[Forge](https://github.com/stampby/forge)** — game builder, asset pipeline, Steam deploy
- **[Dealer](https://github.com/stampby/dealer)** — AI game master, every run different
- **[Conductor](https://github.com/stampby/conductor)** — AI composer, dynamic game scoring
- **[Quartermaster](https://github.com/stampby/quartermaster)** — game server ops, weekly Steam audit
- **[Crypto](https://github.com/stampby/crypto)** — arbitrage, market monitoring
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Security — [docs](docs/SECURITY.md)
- **SSH key-only** — no passwords, single user, fail2ban. *"You shall not pass."*
- **nftables default-drop** — LAN only, deny everything else
- **All services on localhost** — Caddy is the only entry point
- **Systemd hardening** — ProtectSystem, PrivateTmp, NoNewPrivileges on every service
- **[Shadow](https://github.com/stampby/shadow)** — file integrity monitoring, SSH mesh watcher

### Security Bulletin

> **2026-04-01 — axios Supply Chain Attack (CRITICAL)**
>
> `axios@1.14.1` and `axios@0.30.4` were backdoored by North Korean group UNC1069 with a RAT dropper (`plain-crypto-js`). halo-ai's install script was affected via n8n and Vane npm dependencies. Patched within 90 minutes. All credentials rotated.
>
> **If you installed before v0.9.1:** Roll back via `sudo snapper -c root undochange <snapshot>`, rotate ALL credentials, re-run the installer.
>
> Full incident report: [Security Advisory GHSA-mfc3-9wg8-25xf](https://github.com/stampby/halo-ai/security/advisories/GHSA-mfc3-9wg8-25xf) — credited to [@zmcnaney](https://github.com/zmcnaney)
>
> **Mitigations in place:** axios pinned to 1.14.0, `--ignore-scripts` on all npm installs, Meek v3.0 daily audits (17 checks), Dependabot alerts + CodeQL scanning enabled, automated supply chain monitoring via Sentinel.

### Security Automation — [docs](SECURITY.md)
- **Meek** — 17-check security audit daily at 06:00 UTC, auto-pinned to Discord #security
- **Bounty** — bug patrol + dry-run verification daily at 08:00 UTC
- **Sentinel** — source inspection + supply chain monitoring daily at 10:00 UTC
- **Dependabot** — weekly dependency update PRs (pip + npm + GitHub Actions)
- **CodeQL** — code scanning on every push (Python, JavaScript/TypeScript, Actions)
- **Private vulnerability reporting** — enabled, report issues securely via GitHub Security tab

### Stack Protection — [docs](docs/STACK-PROTECTION.md)
- **Freeze/thaw** — one-click snapshot and rollback of the entire stack. *"I'll be back."*
- **Compile from source** — weekly rebuilds with native gfx1151 optimizations
- **[Mixer](https://github.com/stampby/mixer)** — distributed mesh snapshots, no NAS, no single point of failure
- **Man Cave UI** — stack status, update indicators, compile button

### Automation — [docs](docs/AUTONOMOUS-PIPELINE.md)
- **n8n workflows** — GitHub releases trigger Echo Reddit posts automatically
- **Issue triage** — new issues auto-routed to Bounty, Meek, or Amp
- **Mesh snapshots** — Shadow distributes backups every 6 hours
- **CI/CD** — GitHub Actions lint, build, release on every tag

### Autonomous Game Development — [Pipeline](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — PvE co-op extraction game in Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — game server manager, one-click deploy, retro emulation
- **AI game master** — Dealer runs local LLM, every dungeon run is unique. *"You wanna get nuts? Let's get nuts."*
- **Anti-cheat** — encrypted RAM, runtime monitoring, permanent cheater branding. *"You have to ask yourself one question: Do I feel lucky?"*
- **Full pipeline** — design → build → test → deploy, agents handle everything. *"Life, uh, finds a way."*

### Autonomous Music Production — [The Downcomers](https://github.com/stampby/amp)
- **Voice cloning** — architect's voice via XTTS v2, milestone releases
- **AI instrumentals** — original blues/rock, full band, no covers
- **Audiobooks** — public domain classics, 1984 first release
- **Voice API** — TTS-as-a-Service, zero data retention
- **Memorial voice** — capture loved ones' speech, build AI clone after death. *"After all this time? Always."*
- **Distribution** — DistroKid to Spotify, Apple Music, all platforms

### Autonomous Video Production — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Voxel drama** — 10-episode series, script → voice → animation → render
- **Voice tutorials** — architect narrates, full walkthroughs
- **Streaming co-host** — architect's voice as live AI commentator for Twitch/YouTube
- **Full pipeline** — writing → acting → rendering → distribution, all autonomous. *"Lights, camera, action."*

### Infrastructure [Kansas City Shuffle]
- **4-machine SSH mesh [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — btrfs ring snapshots over SSH [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — live performance tracking, history over time
- **[Man Cave](https://github.com/stampby/man-cave)** — control center with GPU metrics, service health, agent activity
- **Zero cloud** — no subscriptions, no APIs, no third-party dependencies. *"There is no cloud. There is only Zuul."*

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
| Wan2.1 | — | Video generation (Strix Halo GPU) |
| MusicGen | — | Music generation (Strix Halo GPU) |
| YOLO | — | Object detection (Strix Halo) |
| Tesseract | — | OCR — document scanning |
| Argos | — | Offline translation |
| Axolotl | — | Model fine-tuning (Strix Halo GPU) |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3030 | Monitoring dashboards |
| Node Exporter | 9100 | System metrics |
| Home Assistant | 8123 | Home automation |
| Borg | — | Encrypted backups to GlusterFS |
| Dashboard | 3003 | GPU metrics + service health |
| Gaia API | 8090 | Agent framework server |
| Gaia MCP | 8765 | Model Context Protocol bridge |

All services bind to `127.0.0.1` — access via Caddy reverse proxy.

## Performance

| Model | Speed | VRAM |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **83-91 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |
| Qwen3-235B-A22B (Frontier MoE) | ~8 tok/s | 95 GB |
| GPT-OSS-120B (Frontier Dense) | ~21 tok/s | 59 GB |

Full benchmarks with thermals, memory, and backend comparisons: [BENCHMARKS.md](BENCHMARKS.md)

## Infrastructure [Kansas City Shuffle]

4 machines — SSH mesh — mixer snapshots — zero cloud [Kansas City Shuffle]

| Machine | Role |
|---------|------|
| ryzen | desktop — development |
| strix-halo | 128GB GPU — AI inference |
| minisforum | Windows 11 — office / testing |
| sligar | 1080Ti — voice training |

Browser > Caddy > Lemonade (unified API) > all services:

| Service | What it does |
|---------|-------------|
| llama.cpp | LLM inference |
| whisper.cpp | speech-to-text |
| Kokoro | text-to-speech |
| ComfyUI | image generation |
| Open WebUI | chat + RAG |
| Vane | deep research |
| n8n | workflow automation |
| Gaia | 17 agents, 78 tools |
| Man Cave | control center |

Full architecture details: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Docs

| Guide | What it covers |
|-------|----------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, GPU backends |
| [Services](docs/SERVICES.md) | Ports, configs, health checks |
| [Security](docs/SECURITY.md) | Firewall, SSH, TLS, password rotation |
| [Stack Protection](docs/STACK-PROTECTION.md) | Why Arch updates won't break your stack |
| [Benchmarks](BENCHMARKS.md) | Full performance data |
| [Blueprints](docs/BLUEPRINTS.md) | Roadmap and planned features |
| [Autonomous Pipeline](docs/AUTONOMOUS-PIPELINE.md) | Zero-human game, music, and video production pipeline |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [VPN Access](docs/VPN.md) | WireGuard setup |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Ring bus, ClusterFS, auto-repair, mesh management |
| [Mixer](https://github.com/stampby/mixer) | SSH mesh snapshots — distributed backups, no single point of failure [Kansas City Shuffle] |
| [Changelog](CHANGELOG.md) | Version history |

## [Screenshots](docs/SCREENSHOTS.md) · [Tutorials & Videos](#tutorials--videos)

## Tutorials & Videos

| Video | Description | Link |
|-------|-------------|------|
| **halo ai on usb** | Full stack on a USB SSD — plug in, boot, talk | [Watch](https://youtu.be/0OIQANS04x4) |
| The Vision | What halo-ai is and why | coming soon |
| Hardware Setup | Mesh wiring, 4 machines, SSH keys | coming soon |
| The Install Script | 42 services compiled from source | coming soon |
| Security | 17-check audit, supply chain protection | coming soon |
| Lemonade + llama.cpp | Unified API, 91 tok/s, Vulkan + FA | coming soon |
| The Agents | 17 autonomous agents, 98 tools | coming soon |
| Man Cave | Control center, freeze/thaw, stack protection | coming soon |
| Voice & Audio | whisper.cpp, Kokoro, voice cloning, SM7B chain | coming soon |
| The Mesh | 4 machines, SSH ring, mixer snapshots | coming soon |
| Full Autonomous Demo | Tag → agents → deploy, zero human | coming soon |

## Voice Talent

**Your voice. Your revenue. Every language on Earth.**

halo-ai is building a community-powered voice platform. We need voice talent from every country, every language. 50/50 revenue share — you earn half of every dollar your voice generates.

👉 **[Apply to join](dashboard-ui/voice-talent.html)** — be the first voice for your country.

## Privacy

**Zero telemetry. Zero tracking. Zero data collection.**

halo-ai does not collect, transmit, or store any data about you, your hardware, your usage, or your content. Nothing phones home. Nothing reports back. There are no analytics, no crash reports, no "anonymous" usage statistics.

Your data stays on your machine. Period.

This is not a service. This is not a platform. This is a tool — built by the architect, for anyone who wants to run AI on their own hardware without asking permission.

## Credits

**Designed and built by the architect** — every script, every service, every agent. From source. No shortcuts. *"I am inevitable."*

Built on [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) by Light-Heart-Labs. Powered by [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Community: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), and the Framework/Arch Linux communities.

## License

Apache 2.0
