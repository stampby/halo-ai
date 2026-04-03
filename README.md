<div align="center">

🌐 **English** | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### the bare-metal ai stack for amd strix halo

**91 tok/s · 42 services · 128gb unified · compiled from source · zero cloud**

*stamped by the architect*

[![CI](https://github.com/stampby/halo-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/stampby/halo-ai/actions/workflows/ci.yml)
[![CodeQL](https://github.com/stampby/halo-ai/actions/workflows/254939804/badge.svg)](https://github.com/stampby/halo-ai/actions/workflows/254939804)
[![Stars](https://img.shields.io/github/stars/stampby/halo-ai?style=flat&logo=github&label=Stars)](https://github.com/stampby/halo-ai/stargazers)
[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)
[![Wiki](https://img.shields.io/badge/Wiki-documentation-00d4ff?style=flat&logo=github&logoColor=white)](https://github.com/stampby/halo-ai/wiki)

</div>

---

> **[wiki](https://github.com/stampby/halo-ai/wiki)** — full documentation · **[discord](https://discord.gg/dSyV646eBs)** — community + support · **[tutorials](https://www.youtube.com/@DirtyOldMan-1971)** — video walkthroughs

---

## what is this

a complete ai platform on a single chip. llm chat, deep research, voice, image gen, workflows, and 17 autonomous agents — all compiled from source on amd strix halo with 128gb unified memory. no containers. no cloud. boot to ready in 19 seconds.

## install

```bash
git clone https://github.com/stampby/halo-ai.git
cd halo-ai
./install.sh --dry-run    # validate first
./install.sh              # build everything
sudo reboot
```

18 components compiled from source. ~2.5 hours. do not run as root. [full guide →](https://github.com/stampby/halo-ai/wiki/Install-Guide)

## what you get

| | |
|---|---|
| **inference** | llama.cpp hip + vulkan, 91 tok/s on qwen3-30b |
| **chat** | open webui with rag, documents, multi-model |
| **research** | vane — cited sources, private search |
| **voice** | whisper.cpp stt + kokoro tts (54 voices) |
| **image** | comfyui on 123gb gpu |
| **workflows** | n8n automation |
| **agents** | 17 autonomous on amd gaia, 98 tools |
| **security** | meek 17-check audit, fail2ban, nftables |
| **search** | searxng private meta-search |
| **vector db** | qdrant for rag |
| **control** | man cave — gpu metrics, service health |

[full stack details →](https://github.com/stampby/halo-ai/wiki/Software-Stack)

## the family

17 agents. each with a role, a personality, and a version number.

| agent | role | ver |
|-------|------|-----|
| **halo** | command center — relay mode, routes through family | v2.0 |
| **echo** | community — discord, reddit, digest, social | v2.1 |
| **bounty** | bug hunter — auto-threads, dry-run patrol | v2.0 |
| **meek** | security — 17-check audit, supply chain scanning | v3.0 |
| **mechanic** | hardware — gpu, drivers, diagnostics | v1.0 |
| **amp** | audio — voice, tts, music | v1.0 |
| **sentinel** | code watcher — source inspection, repo integrity | v2.0 |
| **muse** | entertainment — games, trivia | v1.0 |

[full family + backstories →](https://github.com/stampby/halo-ai/wiki/The-Family)

## benchmarks

| model | quant | decode | prompt |
|-------|-------|--------|--------|
| qwen3-30b-a3b | q4_k_m | **91 tok/s** | 154 tok/s |
| llama 3.1 8b | q4_k_m | 185 tok/s | 2100 tok/s |
| llama 3.1 70b | q4_k_m | 18 tok/s | 210 tok/s |

128gb unified = run 30b models at full speed with room to spare. [competitive comparison →](https://github.com/stampby/halo-ai/wiki/Benchmarks)

## security

- all downloads sha256 + gpg verified
- all services on 127.0.0.1 behind caddy auth
- ssh key-only, root disabled, fail2ban
- meek audits the stack daily — 17 checks
- axios supply chain attack mitigated — [advisory](https://github.com/stampby/halo-ai/security/advisories/GHSA-3gp9-qwch-x5wv)
- dependabot + codeql on every push

[full security details →](https://github.com/stampby/halo-ai/wiki/Security)

## privacy

**zero telemetry. zero tracking. zero data collection.** nothing phones home. your data stays on your machine.

## credits

built on [DreamServer](https://github.com/Light-Heart-Labs/DreamServer). powered by [AMD Gaia](https://github.com/amd/gaia), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Lemonade](https://github.com/lemonade-sdk/lemonade), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

---

*stamped by the architect*

Apache 2.0
