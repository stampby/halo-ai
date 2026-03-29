# halo-ai studios — Autonomous Pipeline

17 agents. Zero human interaction with the outside world. The architect builds agents. Agents run the business.

*stamped by the architect*

---

## The Pipeline

```
code → sentinel → meek → bounty → forge → amp → echo → revenue
```

### Development

sentinel (code watcher)
  ├── Reviews PRs (static analysis + LLM)
  ├── Security scan → meek
  ├── Bug check → bounty
  ├── Clean? → auto-merge
  └── Blocked? → request changes

meek (security chief)
  ├── Vulnerability scan
  ├── Dependency audit
  ├── Anti-cheat integrity check
  └── ghost → validates no leaked credentials

bounty (QA / bug hunter)
  ├── Automated test suite
  ├── Regression testing
  ├── Performance benchmarks
  └── Bug report triage

### Build

forge (game builder)
  ├── Export: Linux, Windows, macOS
  ├── Asset pipeline: interpreter → ComfyUI → Blockbench
  ├── Audio pipeline: amp → SFX / music / voice
  └── Build validation

interpreter (creative director)
  ├── Enhances all generation prompts
  ├── Visual style consistency
  └── Art direction

amp (audio + video)
  ├── SFX generation and mastering
  ├── Music production (The Downcomers)
  ├── Voice clone pipeline (XTTS v2)
  ├── Video production (ComfyUI)
  ├── Trailer audio + game trailers
  └── Voice lines for in-game dialogue

conductor (AI composer)
  ├── Original scores and arrangements
  ├── Dynamic game music (adapts to gameplay)
  ├── Band instrumentals
  └── Spatial audio

### Media & Distribution

amp (production)
  ├── Music: AI instrumentals + clone vocals → master
  ├── Audiobooks: public domain → clone narration → master
  ├── Video: music videos, trailers, promo clips
  └── All rendered locally on Strix Halo (128GB)

echo (distribution)
  ├── DistroKid → Spotify, Apple Music, all platforms
  ├── Findaway → Audible, Apple Books
  ├── YouTube → music videos, trailers
  ├── Reddit → community posts, benchmarks
  ├── Discord → announcements, support
  └── Social media → promotional content

### Deployment

forge:steam (deployer)
  ├── VDF manifests
  ├── Pre-upload security check (meek)
  ├── SteamCMD upload
  └── Rollback capability (vault)

vault (backup)
  ├── Pre-deploy snapshot
  ├── Post-deploy snapshot
  └── Build artifact archival

pulse (monitoring)
  ├── Deployment health
  ├── Download counts, crash reports
  └── Alert on anomalies → echo

### Community

echo (public face)
  ├── Discord: patch notes, player chat
  ├── Steam: store page, community posts
  ├── Reddit: r/LocalLLaMA, r/gamedev, r/selfhosted
  ├── Bug reports → bounty
  └── Feature requests → log and prioritize

shield (moderation)
  ├── Content moderation
  ├── Toxicity filtering
  └── Player report handling

fang (anti-cheat)
  ├── Real-time cheat detection
  ├── Ban enforcement
  └── Exploit reporting → bounty

### In-Game Runtime

dealer (game master AI)
  ├── Local LLM on player's machine
  ├── Every run is different — AI-driven, never scripted
  ├── Enemy tactics, world generation, dynamic events
  ├── Intelligent loot placement
  ├── Difficulty adaptation
  └── Room narration (atmospheric, unique)

### Infrastructure (always on)

halo — service management, health monitoring, escalation
pulse — uptime, resource usage, alert cascade
net — multiplayer, DDoS protection, DDNS
gate — auth, DLC validation, rate limiting
ghost — secrets, credentials, rotation
shadow — file integrity, SSH mesh, mixer snapshots
mirror — PII scanning, GDPR, compliance
vault — btrfs snapshots, instant rollback

---

## Revenue

All revenue streams managed by the autonomous pipeline. Agents handle production, distribution, and promotion. One person. Zero employees.

### Games

| Stream | Price | Agent |
|--------|-------|-------|
| Base game (Undercroft) | $19.95 | forge → Steam / itch.io |
| DLC dungeon packs | $4.99–$9.99 | forge → Steam |
| Community marketplace | Creator-set | quartermaster |
| Reddit playable demo | Free (funnel to full game) | echo → Devvit |
| In-game cosmetics | $0.99–$4.99 | forge |

### Music — The Downcomers

| Stream | Model | Agent |
|--------|-------|-------|
| Spotify, Apple Music, all platforms | Per-stream royalties | amp → DistroKid |
| YouTube music videos | Ad revenue | amp + echo |
| Bandcamp direct sales | Per-sale, fan pricing | echo |
| Sync licensing (TV, film, ads) | Per-use fee | amp |
| Live performance royalties | ASCAP/BMI | amp |

### Audiobooks

| Stream | Model | Agent |
|--------|-------|-------|
| Audible / Apple Books / Google Play | Per-sale royalties | amp → Findaway |
| Public domain catalog | Passive income, unlimited titles | amp (clone narration) |
| Custom narration commissions | Per-finished-hour | amp |
| Podcast narration | Per-episode | amp |

### Voice & TTS

| Stream | Model | Agent |
|--------|-------|-------|
| Commercial voice licensing | Per-project | amp |
| TTS API service | Per-call or subscription | amp → API |
| Audiobook narration for hire | Per-finished-hour | amp |
| Voice packs for game devs | Per-pack | amp + forge |
| Personal assistant voice | Licensing | amp |

### Video

| Stream | Model | Agent |
|--------|-------|-------|
| YouTube channel | Ad revenue | amp + echo |
| Game trailers | Drives game sales | amp + forge |
| Tutorial / dev diary | Ad revenue + engagement | echo |
| Music video production for others | Per-project | amp |

### Infrastructure & Services

| Stream | Model | Agent |
|--------|-------|-------|
| AMD developer challenges | Hardware prizes | echo |
| GitHub Sponsors / Patreon | Monthly supporters | echo |
| Consulting / custom AI stack builds | Per-project | architect |
| Game server hosting | Subscription | quartermaster + arcade |
| halo-ai enterprise licensing | Per-seat | — |

### Future

| Stream | Model | Agent |
|--------|-------|-------|
| Crypto arbitrage | Automated trading | crypto |
| Tie Die Farms | Cash / barter | — |
| AI agent marketplace | Per-agent licensing | forge |
| Voice model marketplace | Per-model | amp |

---

## Message Bus

All agents communicate via the message bus (port 8100).

Topics: security, bugs, releases, community, builds, monitoring, game

---

## Hardware

- **Strix Halo** — all agents, inference, rendering, production
- **Ryzen** — development, testing, recording
- **Sligar** — voice model training, GPU compute
- **Minisforum** — game testing, office, Windows builds
