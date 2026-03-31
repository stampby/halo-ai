🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | **हिन्दी** | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### AMD Strix Halo के लिए bare-metal AI stack

**87 tok/s। शून्य containers। 115GB GPU memory। source से compiled। मुझे kung fu आता है।**

*CLI से बनाया — architect द्वारा stamped*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **यहाँ नए हैं?** [tutorials](#tutorials) से शुरू करें — install से लेकर autonomous operation तक पूरे video walkthroughs।

---

## यह क्या है?

**AMD Ryzen AI MAX+ 395** के लिए एक पूर्ण AI platform — LLM inference, chat, deep research, voice, image generation, RAG, और workflows। Game development, music production, और video production के लिए autonomous pipelines। 33 services, 17 autonomous agents, 98 tools, 5 Discord bots। सब bare metal, सब source से compiled, सब एक chip पर 128GB unified memory के साथ। Boot से ready: 18.7 सेकंड।

**इससे बात करें।** Halo से बोलें, text देखें, response सुनें। हर tool, हर agent, हर feature — आपकी आवाज़ से नियंत्रित। घर पर vibe coding, out of the box, अपने hardware पर। *"Pod bay के दरवाज़े खोलो, HAL।"*

## Bare Metal क्यों?

- **Containers GPU workloads पर 15-20% overhead जोड़ते हैं।** जब एक chip पर 115GB unified memory हो, तो हर watt और हर byte inference में जाना चाहिए, orchestration में नहीं। *"चम्मच को मोड़ने की कोशिश मत करो। बस यह सच्चाई समझो: कोई container नहीं है।"*
- **Source से compiled** का मतलब native gfx1151 optimizations जो pre-built binaries में नहीं मिलतीं। 87 tok/s यहीं से आता है।
- **कोई timers नहीं। कोई cron नहीं। पूर्ण AI।** Agents schedule पर check नहीं करते — वे conditions देखते हैं और बदलाव होने पर act करते हैं। Service down हो गई? आपके ध्यान देने से पहले detect और repair। GPU overheat? उसी पल report। हर 30 सेकंड पर नहीं। *उसी पल।* माफ़ करना Dave, यह stack सोता नहीं।
- **Arch rolling release में टिकता है।** Stack freeze करो, pacman को update करने दो, agents detect करें अगर कुछ टूटा, 30 सेकंड में thaw करके rollback। इसीलिए halo-ai बिना डर के Arch पर चलता है। *"बस एक खरोंच है।"*
- **पूरा stack आपका है।** कोई package manager तय नहीं करता कि आपका AI server कब बंद हो। *"मेरा प्रेशस।"*

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

Interactive installer — username, passwords, hostname, कौन सी services enable करनी हैं। समझदार defaults। Default Caddy password `Caddy` है — तुरंत बदलें। *"समझदारी से चुनो।"*

## Features

### AI & Inference
- **LLM chat** — [Open WebUI](https://github.com/open-webui/open-webui) RAG, multi-model, document upload के साथ
- **Deep research** — [Vane](https://github.com/ItzCrazyKns/Vane) cited sources और private search के साथ
- **Image generation** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 115GB GPU पर, SDXL, Flux
- **Video generation** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) ROCm 6.3 पर
- **Music generation** — [MusicGen](https://github.com/facebookresearch/audiocraft) Meta द्वारा, local GPU inference
- **Speech-to-text** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) gfx1151 के लिए compiled
- **Text-to-speech** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) 54 प्राकृतिक आवाज़ों के साथ
- **Code assistant** — Qwen2.5 Coder 7B llama.cpp पर, 48.6 tok/s
- **Object detection** — [YOLO](https://github.com/ultralytics/ultralytics) v8, real-time inference
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, source से compiled
- **Translation** — [Argos Translate](https://github.com/argosopentech/argos-translate), offline multi-language
- **Fine-tuning** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), अपने models locally train करें
- **Unified API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, OpenAI/Ollama/Anthropic compatible

### Agents — [docs](docs/AGENTS.md)
- **17 autonomous agents** [AMD Gaia](https://github.com/amd/gaia) पर 98 tools के साथ
- **[Echo](https://github.com/stampby/echo)** — public face, Reddit bridge, Discord, social media
- **[Meek](https://github.com/stampby/meek)** — security chief, 9 Reflex sub-agents ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — bug hunter, offensive security, Halo का भाई
- **[Amp](https://github.com/stampby/amp)** — audio engineer, voice cloning, music production
- **[Sentinel](https://github.com/stampby/sentinel)** — auto PR review, code gating
- **[Mechanic](https://github.com/stampby/mechanic)** — hardware diagnostics, system monitoring
- **[Forge](https://github.com/stampby/forge)** — game builder, asset pipeline, Steam deploy
- **[Dealer](https://github.com/stampby/dealer)** — AI game master, हर बार अलग
- **[Conductor](https://github.com/stampby/conductor)** — AI composer, dynamic game scoring
- **[Quartermaster](https://github.com/stampby/quartermaster)** — game server ops, weekly Steam audit
- **[Crypto](https://github.com/stampby/crypto)** — arbitrage, market monitoring
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Security — [docs](docs/SECURITY.md)
- **SSH key-only** — कोई passwords नहीं, single user, fail2ban। *"तुम नहीं गुज़रोगे।"*
- **nftables default-drop** — केवल LAN, बाकी सब deny
- **सभी services localhost पर** — Caddy एकमात्र entry point है
- **Systemd hardening** — हर service पर ProtectSystem, PrivateTmp, NoNewPrivileges
- **[Shadow](https://github.com/stampby/shadow)** — file integrity monitoring, SSH mesh watcher

### Stack Protection — [docs](docs/STACK-PROTECTION.md)
- **Freeze/thaw** — पूरे stack का one-click snapshot और rollback। *"मैं वापस आऊंगा।"*
- **Source से compile** — native gfx1151 optimizations के साथ weekly rebuilds
- **[Mixer](https://github.com/stampby/mixer)** — distributed mesh snapshots, कोई NAS नहीं, कोई single point of failure नहीं
- **Man Cave UI** — stack status, update indicators, compile button

### Automation — [docs](docs/AUTONOMOUS-PIPELINE.md)
- **n8n workflows** — GitHub releases Echo Reddit posts को automatically trigger करते हैं
- **Issue triage** — नए issues automatically Bounty, Meek, या Amp को route होते हैं
- **Mesh snapshots** — Shadow हर 6 घंटे backups distribute करता है
- **CI/CD** — हर tag पर GitHub Actions lint, build, release

### Autonomous Game Development — [Pipeline](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — Godot 4 में PvE co-op extraction game
- **[Arcade](https://github.com/stampby/halo-arcade)** — game server manager, one-click deploy, retro emulation
- **AI game master** — Dealer local LLM चलाता है, हर dungeon run अनोखा है। *"पागल होना है? चलो पागल होते हैं।"*
- **Anti-cheat** — encrypted RAM, runtime monitoring, cheaters पर स्थायी ब्रांडिंग। *"अपने आप से एक सवाल पूछो: क्या मैं lucky हूँ?"*
- **Full pipeline** — design → build → test → deploy, agents सब संभालते हैं। *"ज़िंदगी, उह, रास्ता ढूँढ लेती है।"*

### Autonomous Music Production — [The Downcomers](https://github.com/stampby/amp)
- **Voice cloning** — XTTS v2 के ज़रिए architect की आवाज़, milestone releases
- **AI instrumentals** — original blues/rock, पूरा band, कोई covers नहीं
- **Audiobooks** — public domain classics, पहली release 1984
- **Voice API** — TTS-as-a-Service, zero data retention
- **Memorial voice** — प्रियजनों की आवाज़ capture करें, मृत्यु के बाद AI clone बनाएं। *"इतने समय बाद भी? हमेशा।"*
- **Distribution** — DistroKid से Spotify, Apple Music, सभी platforms पर

### Autonomous Video Production — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Voxel drama** — 10-episode series, script → voice → animation → render
- **Voice tutorials** — architect narrates करते हैं, पूरे walkthroughs
- **Streaming co-host** — Twitch/YouTube के लिए architect की आवाज़ live AI commentator के रूप में
- **Full pipeline** — writing → acting → rendering → distribution, सब autonomous। *"Lights, camera, action।"*

### Infrastructure [Kansas City Shuffle]
- **4-machine SSH mesh [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — SSH पर btrfs ring snapshots [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — live performance tracking, समय के साथ history
- **[Man Cave](https://github.com/stampby/man-cave)** — GPU metrics, service health, agent activity के साथ control center
- **Zero cloud** — कोई subscriptions नहीं, कोई APIs नहीं, कोई third-party dependencies नहीं। *"कोई cloud नहीं है। बस Zuul है।"*

## Services

| Service | Port | उद्देश्य |
|---------|------|---------|
| Lemonade | 8080 | Unified AI API (OpenAI/Ollama/Anthropic compatible) |
| llama.cpp | 8081 | LLM inference — Vulkan + HIP dual backends |
| Open WebUI | 3000 | RAG, documents, multi-model के साथ chat |
| Vane | 3001 | Cited sources के साथ deep research |
| SearXNG | 8888 | Private meta-search |
| Qdrant | 6333 | RAG के लिए Vector DB |
| n8n | 5678 | Workflow automation |
| whisper.cpp | 8082 | Speech-to-text |
| Kokoro | 8083 | Text-to-speech (54 आवाज़ें) |
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
| Borg | — | GlusterFS पर encrypted backups |
| Dashboard | 3003 | GPU metrics + service health |
| Gaia API | 8090 | Agent framework server |
| Gaia MCP | 8765 | Model Context Protocol bridge |

सभी services `127.0.0.1` पर bind होती हैं — Caddy reverse proxy के ज़रिए access करें।

## Performance

| Model | Speed | VRAM |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **87 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

Thermals, memory, और backend comparisons के साथ पूरे benchmarks: [BENCHMARKS.md](BENCHMARKS.md)

## Infrastructure [Kansas City Shuffle]

4 machines — SSH mesh — mixer snapshots — zero cloud [Kansas City Shuffle]

| Machine | भूमिका |
|---------|------|
| ryzen | desktop — development |
| strix-halo | 128GB GPU — AI inference |
| minisforum | Windows 11 — office / testing |
| sligar | 1080Ti — voice training |

Browser > Caddy > Lemonade (unified API) > सभी services:

| Service | क्या करता है |
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

पूरा architecture विवरण: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Docs

| Guide | क्या शामिल है |
|-------|----------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, GPU backends |
| [Services](docs/SERVICES.md) | Ports, configs, health checks |
| [Security](docs/SECURITY.md) | Firewall, SSH, TLS, password rotation |
| [Stack Protection](docs/STACK-PROTECTION.md) | Arch updates आपका stack क्यों नहीं तोड़ेंगे |
| [Benchmarks](BENCHMARKS.md) | पूरा performance data |
| [Blueprints](docs/BLUEPRINTS.md) | Roadmap और planned features |
| [Autonomous Pipeline](docs/AUTONOMOUS-PIPELINE.md) | Zero-human game, music, और video production pipeline |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | सामान्य समस्याएं और समाधान |
| [VPN Access](docs/VPN.md) | WireGuard setup |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Ring bus, ClusterFS, auto-repair, mesh management |
| [Mixer](https://github.com/stampby/mixer) | SSH mesh snapshots — distributed backups, कोई single point of failure नहीं [Kansas City Shuffle] |
| [Changelog](CHANGELOG.md) | Version history |

## [Screenshots](docs/SCREENSHOTS.md)

## Tutorials

Video walkthroughs — शुरू से अंत तक, कुछ भी नहीं छोड़ा। Unlisted YouTube links।

| # | Video | स्थिति |
|---|-------|--------|
| 1 | The Vision — halo-ai क्या है और क्यों | जल्द आ रहा है |
| 2 | Hardware Setup — mesh wiring, 4 machines | जल्द आ रहा है |
| 3 | Arch Linux Install — base OS, btrfs, first boot | जल्द आ रहा है |
| 4 | The Install Script — source से compiled 13 services | जल्द आ रहा है |
| 5 | Security — nftables, SSH, Caddy, deny-all model | जल्द आ रहा है |
| 6 | Lemonade + llama.cpp — unified API, 87 tok/s | जल्द आ रहा है |
| 7 | Chat + RAG — Open WebUI, document upload, vector search | जल्द आ रहा है |
| 8 | Deep Research — Vane, cited sources, private search | जल्द आ रहा है |
| 9 | Image Generation — 115GB GPU पर ComfyUI | जल्द आ रहा है |
| 10 | Voice — whisper.cpp, Kokoro TTS, 54 आवाज़ें | जल्द आ रहा है |
| 11 | Workflows — n8n automation, GitHub webhooks | जल्द आ रहा है |
| 12 | The Agents — Gaia UI, सभी 17 agents, management | जल्द आ रहा है |
| 13 | Man Cave — control center, stack protection, freeze/thaw | जल्द आ रहा है |
| 14 | The Mesh — SSH keys, 4 machines, mixer, Shadow | जल्द आ रहा है |
| 15 | Windows in the Mesh — Minisforum, VSS, Terminal | जल्द आ रहा है |
| 16 | Discord Bots — Echo, Bounty, Meek, Amp | जल्द आ रहा है |
| 17 | Reddit Bridge — scan, draft, approve, post | जल्द आ रहा है |
| 18 | Audio Chain — SM7B, Scarlett, PipeWire, routing | जल्द आ रहा है |
| 19 | Voice Cloning — recording, XTTS v2, training | जल्द आ रहा है |
| 20 | The Downcomers — पहला track, vocal doubling, DistroKid | जल्द आ रहा है |
| 21 | The Game — Undercroft, anti-cheat, Dealer AI | जल्द आ रहा है |
| 22 | Benchmarks — llama-bench, GitHub Pages, history | जल्द आ रहा है |
| 23 | CI/CD — GitHub Actions, releases, packaging | जल्द आ रहा है |
| 24 | Full Autonomous Demo — tag → agents → Reddit post | जल्द आ रहा है |

*99% users के पास Claude नहीं है। ये tutorials इसके बिना भी अनुभव को आसान बनाते हैं। "जहाँ हम जा रहे हैं, वहाँ सड़कों की ज़रूरत नहीं।"*

## Credits

**Architect द्वारा designed और built** — हर script, हर service, हर agent। Source से। कोई shortcuts नहीं। *"मैं अपरिहार्य हूँ।"*

[DreamServer](https://github.com/Light-Heart-Labs/DreamServer) by Light-Heart-Labs पर बनाया। [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock) द्वारा संचालित।

Community: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), और Framework/Arch Linux communities।

## License

Apache 2.0
