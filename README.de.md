🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | **Deutsch** | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### Der Bare-Metal-KI-Stack für AMD Strix Halo

**91 tok/s. Keine Container. 123GB GPU-Speicher. Aus dem Quellcode kompiliert. Ich kann Kung Fu.**

*gebaut per CLI — gestempelt vom Architekten*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **Neu hier?** Starte mit den [Tutorials](#tutorials) — vollständige Video-Anleitungen von der Installation bis zum autonomen Betrieb.

---

## Was ist das?

Eine vollständige KI-Plattform für den **AMD Ryzen AI MAX+ 395** — LLM-Inferenz, Chat, Deep Research, Sprache, Bildgenerierung, RAG und Workflows. Autonome Pipelines für Spieleentwicklung, Musikproduktion und Videoproduktion. 33 Dienste, 17 autonome Agenten, 98 Tools, 5 Discord-Bots. Alles Bare Metal, alles aus dem Quellcode kompiliert, alles auf einem Chip mit 128GB Unified Memory. Boot bis Betriebsbereit: 18,7 Sekunden.

**Sprich damit.** Sprich zu Halo, sieh den Text, höre die Antwort. Jedes Tool, jeder Agent, jede Funktion — gesteuert durch deine Stimme. Vibe Coding zu Hause, sofort einsatzbereit, auf deiner eigenen Hardware. *„Öffne die Schleusentore, HAL."*

## Warum Bare Metal?

- **Container verursachen 15-20% Overhead** bei GPU-Workloads. Wenn du 123GB Unified Memory auf einem einzigen Chip hast, sollte jedes Watt und jedes Byte für Inferenz verwendet werden, nicht für Orchestrierung. *„Versuche nicht, den Löffel zu verbiegen. Erkenne stattdessen nur die Wahrheit: Es gibt keinen Container."*
- **Aus dem Quellcode kompiliert** bedeutet native gfx1151-Optimierungen, die vorgefertigte Binärdateien verfehlen. Daher kommen die 91 tok/s.
- **Keine Timer. Kein Cron. Vollständig KI.** Agenten prüfen nicht nach Zeitplan — sie überwachen Bedingungen und handeln, wenn sich etwas ändert. Dienst fällt aus? Erkannt und repariert, bevor du es bemerkst. GPU überhitzt? Gemeldet in dem Moment, in dem es passiert. Nicht alle 30 Sekunden. *In dem Moment.* Es tut mir leid Dave, aber dieser Stack schläft nicht.
- **Überlebt Arch Rolling Release.** Stack einfrieren, pacman aktualisieren lassen, Agenten erkennen ob etwas kaputt gegangen ist, in 30 Sekunden auftauen zum Rollback. Deshalb läuft halo-ai furchtlos auf Arch. *„Ist nur 'ne Fleischwunde."*
- **Du besitzt den gesamten Stack.** Kein Paketmanager entscheidet, wann dein KI-Server ausfällt. *„Mein Schatz."*

## Schnellinstallation

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

Interaktiver Installer — Benutzername, Passwörter, Hostname, welche Dienste aktiviert werden sollen. Sinnvolle Standardwerte. Standard-Caddy-Passwort ist `Caddy` — sofort ändern. *„Wähle weise."*

## Funktionen

### KI & Inferenz
- **LLM-Chat** — [Open WebUI](https://github.com/open-webui/open-webui) mit RAG, Multi-Model, Dokumenten-Upload
- **Deep Research** — [Vane](https://github.com/ItzCrazyKns/Vane) mit zitierten Quellen und privater Suche
- **Bildgenerierung** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) auf 123GB GPU, SDXL, Flux
- **Videogenerierung** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) auf ROCm 6.3
- **Musikgenerierung** — [MusicGen](https://github.com/facebookresearch/audiocraft) von Meta, lokale GPU-Inferenz
- **Sprache-zu-Text** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) kompiliert für gfx1151
- **Text-zu-Sprache** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) mit 54 natürlichen Stimmen
- **Code-Assistent** — Qwen2.5 Coder 7B auf llama.cpp, 48,6 tok/s
- **Objekterkennung** — [YOLO](https://github.com/ultralytics/ultralytics) v8, Echtzeit-Inferenz
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, aus dem Quellcode kompiliert
- **Übersetzung** — [Argos Translate](https://github.com/argosopentech/argos-translate), offline mehrsprachig
- **Feinabstimmung** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), trainiere deine eigenen Modelle lokal
- **Einheitliche API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, OpenAI/Ollama/Anthropic-kompatibel

### Agenten — [Doku](docs/AGENTS.md)
- **17 autonome Agenten** auf [AMD Gaia](https://github.com/amd/gaia) mit 98 Tools
- **[Echo](https://github.com/stampby/echo)** — öffentliches Gesicht, Reddit-Bridge, Discord, Social Media
- **[Meek](https://github.com/stampby/meek)** — Sicherheitschef, 9 Reflex-Subagenten ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — Bug-Jäger, offensive Sicherheit, Halos Bruder
- **[Amp](https://github.com/stampby/amp)** — Toningenieur, Voice Cloning, Musikproduktion
- **[Sentinel](https://github.com/stampby/sentinel)** — automatisches PR-Review, Code-Gating
- **[Mechanic](https://github.com/stampby/mechanic)** — Hardware-Diagnose, Systemüberwachung
- **[Forge](https://github.com/stampby/forge)** — Spieleentwickler, Asset-Pipeline, Steam-Deploy
- **[Dealer](https://github.com/stampby/dealer)** — KI-Spielleiter, jeder Durchlauf anders
- **[Conductor](https://github.com/stampby/conductor)** — KI-Komponist, dynamische Spielmusik
- **[Quartermaster](https://github.com/stampby/quartermaster)** — Gameserver-Betrieb, wöchentliches Steam-Audit
- **[Crypto](https://github.com/stampby/crypto)** — Arbitrage, Marktüberwachung
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Sicherheit — [Doku](docs/SECURITY.md)
- **Nur SSH-Schlüssel** — keine Passwörter, einzelner Benutzer, fail2ban. *„Du kommst hier nicht vorbei!"*
- **nftables Default-Drop** — nur LAN, alles andere ablehnen
- **Alle Dienste auf localhost** — Caddy ist der einzige Zugangspunkt
- **Systemd-Härtung** — ProtectSystem, PrivateTmp, NoNewPrivileges bei jedem Dienst
- **[Shadow](https://github.com/stampby/shadow)** — Dateiintegritätsüberwachung, SSH-Mesh-Wächter

### Stack-Schutz — [Doku](docs/STACK-PROTECTION.md)
- **Einfrieren/Auftauen** — Ein-Klick-Snapshot und Rollback des gesamten Stacks. *„Ich komme wieder."*
- **Aus dem Quellcode kompiliert** — wöchentliche Neuerstellungen mit nativen gfx1151-Optimierungen
- **[Mixer](https://github.com/stampby/mixer)** — verteilte Mesh-Snapshots, kein NAS, kein Single Point of Failure
- **Man Cave UI** — Stack-Status, Update-Anzeigen, Kompilier-Button

### Automatisierung — [Doku](docs/AUTONOMOUS-PIPELINE.md)
- **n8n Workflows** — GitHub-Releases lösen automatisch Echo-Reddit-Posts aus
- **Issue-Triage** — neue Issues werden automatisch an Bounty, Meek oder Amp weitergeleitet
- **Mesh-Snapshots** — Shadow verteilt Backups alle 6 Stunden
- **CI/CD** — GitHub Actions Lint, Build, Release bei jedem Tag

### Autonome Spieleentwicklung — [Pipeline](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — PvE-Koop-Extraktionsspiel in Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — Gameserver-Manager, Ein-Klick-Deploy, Retro-Emulation
- **KI-Spielleiter** — Dealer betreibt lokales LLM, jeder Dungeon-Durchlauf ist einzigartig. *„Willst du durchdrehen? Lass uns durchdrehen."*
- **Anti-Cheat** — verschlüsselter RAM, Laufzeitüberwachung, permanente Cheater-Brandmarkung. *„Du musst dir eine Frage stellen: Fühlst du dich glücklich?"*
- **Vollständige Pipeline** — Design → Build → Test → Deploy, Agenten erledigen alles. *„Das Leben, äh, findet einen Weg."*

### Autonome Musikproduktion — [The Downcomers](https://github.com/stampby/amp)
- **Voice Cloning** — Stimme des Architekten via XTTS v2, Meilenstein-Releases
- **KI-Instrumentals** — originaler Blues/Rock, volle Band, keine Cover
- **Hörbücher** — gemeinfreie Klassiker, 1984 als erstes Release
- **Voice API** — TTS-as-a-Service, keine Datenspeicherung
- **Erinnerungsstimme** — Sprache von Angehörigen aufzeichnen, KI-Klon nach dem Tod erstellen. *„Nach all dieser Zeit? Immer."*
- **Vertrieb** — DistroKid zu Spotify, Apple Music, alle Plattformen

### Autonome Videoproduktion — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Voxel-Drama** — 10-teilige Serie, Skript → Stimme → Animation → Rendering
- **Sprach-Tutorials** — vom Architekten erzählt, vollständige Anleitungen
- **Streaming-Co-Host** — Stimme des Architekten als Live-KI-Kommentator für Twitch/YouTube
- **Vollständige Pipeline** — Drehbuch → Schauspiel → Rendering → Vertrieb, alles autonom. *„Licht, Kamera, Action."*

### Infrastruktur [Kansas City Shuffle]
- **4-Maschinen SSH-Mesh [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — btrfs-Ring-Snapshots über SSH [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — Live-Performance-Tracking, Verlauf über Zeit
- **[Man Cave](https://github.com/stampby/man-cave)** — Kontrollzentrum mit GPU-Metriken, Dienst-Gesundheit, Agenten-Aktivität
- **Keine Cloud** — keine Abonnements, keine APIs, keine Drittanbieter-Abhängigkeiten. *„Es gibt keine Cloud. Es gibt nur Zuul."*

## Dienste

| Dienst | Port | Zweck |
|--------|------|-------|
| Lemonade | 8080 | Einheitliche KI-API (OpenAI/Ollama/Anthropic-kompatibel) |
| llama.cpp | 8081 | LLM-Inferenz — Vulkan + HIP Dual-Backends |
| Open WebUI | 3000 | Chat mit RAG, Dokumente, Multi-Model |
| Vane | 3001 | Deep Research mit zitierten Quellen |
| SearXNG | 8888 | Private Meta-Suche |
| Qdrant | 6333 | Vektor-DB für RAG |
| n8n | 5678 | Workflow-Automatisierung |
| whisper.cpp | 8082 | Sprache-zu-Text |
| Kokoro | 8083 | Text-zu-Sprache (54 Stimmen) |
| ComfyUI | 8188 | Bildgenerierung |
| Wan2.1 | — | Videogenerierung (Strix Halo GPU) |
| MusicGen | — | Musikgenerierung (Strix Halo GPU) |
| YOLO | — | Objekterkennung (Strix Halo) |
| Tesseract | — | OCR — Dokumentenscannen |
| Argos | — | Offline-Übersetzung |
| Axolotl | — | Modell-Feinabstimmung (Strix Halo GPU) |
| Prometheus | 9090 | Metrik-Erfassung |
| Grafana | 3030 | Monitoring-Dashboards |
| Node Exporter | 9100 | System-Metriken |
| Home Assistant | 8123 | Heimautomatisierung |
| Borg | — | Verschlüsselte Backups auf GlusterFS |
| Dashboard | 3003 | GPU-Metriken + Dienst-Gesundheit |
| Gaia API | 8090 | Agent-Framework-Server |
| Gaia MCP | 8765 | Model Context Protocol Bridge |

Alle Dienste binden an `127.0.0.1` — Zugriff über Caddy Reverse Proxy.

## Leistung

| Modell | Geschwindigkeit | VRAM |
|--------|----------------|------|
| Qwen3-30B-A3B (MoE) | **83-91 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

Vollständige Benchmarks mit Thermals, Speicher und Backend-Vergleichen: [BENCHMARKS.md](BENCHMARKS.md)

## Infrastruktur [Kansas City Shuffle]

4 Maschinen — SSH-Mesh — Mixer-Snapshots — keine Cloud [Kansas City Shuffle]

| Maschine | Rolle |
|----------|-------|
| ryzen | Desktop — Entwicklung |
| strix-halo | 128GB GPU — KI-Inferenz |
| minisforum | Windows 11 — Büro / Tests |
| sligar | 1080Ti — Sprachtraining |

Browser > Caddy > Lemonade (einheitliche API) > alle Dienste:

| Dienst | Funktion |
|--------|----------|
| llama.cpp | LLM-Inferenz |
| whisper.cpp | Sprache-zu-Text |
| Kokoro | Text-zu-Sprache |
| ComfyUI | Bildgenerierung |
| Open WebUI | Chat + RAG |
| Vane | Deep Research |
| n8n | Workflow-Automatisierung |
| Gaia | 17 Agenten, 78 Tools |
| Man Cave | Kontrollzentrum |

Vollständige Architekturdetails: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Dokumentation

| Leitfaden | Inhalt |
|-----------|--------|
| [Architektur](docs/ARCHITECTURE.md) | Systemdesign, Datenfluss, GPU-Backends |
| [Dienste](docs/SERVICES.md) | Ports, Konfigurationen, Health Checks |
| [Sicherheit](docs/SECURITY.md) | Firewall, SSH, TLS, Passwortrotation |
| [Stack-Schutz](docs/STACK-PROTECTION.md) | Warum Arch-Updates deinen Stack nicht zerstören |
| [Benchmarks](BENCHMARKS.md) | Vollständige Leistungsdaten |
| [Blueprints](docs/BLUEPRINTS.md) | Roadmap und geplante Funktionen |
| [Autonome Pipeline](docs/AUTONOMOUS-PIPELINE.md) | Pipeline ohne menschliches Zutun für Spiel-, Musik- und Videoproduktion |
| [Fehlerbehebung](docs/TROUBLESHOOTING.md) | Häufige Probleme und Lösungen |
| [VPN-Zugang](docs/VPN.md) | WireGuard-Einrichtung |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Ring-Bus, ClusterFS, Auto-Reparatur, Mesh-Verwaltung |
| [Mixer](https://github.com/stampby/mixer) | SSH-Mesh-Snapshots — verteilte Backups, kein Single Point of Failure [Kansas City Shuffle] |
| [Changelog](CHANGELOG.md) | Versionsgeschichte |

## [Screenshots](docs/SCREENSHOTS.md)

## Tutorials

Video-Anleitungen — von Anfang bis Ende, nichts ausgelassen. Ungelistete YouTube-Links.

| # | Video | Status |
|---|-------|--------|
| 1 | Die Vision — was halo-ai ist und warum | demnächst |
| 2 | Hardware-Setup — Mesh-Verkabelung, 4 Maschinen | demnächst |
| 3 | Arch Linux Installation — Basis-OS, btrfs, erster Start | demnächst |
| 4 | Das Installationsskript — 13 Dienste aus dem Quellcode kompiliert | demnächst |
| 5 | Sicherheit — nftables, SSH, Caddy, Deny-All-Modell | demnächst |
| 6 | Lemonade + llama.cpp — einheitliche API, 91 tok/s | demnächst |
| 7 | Chat + RAG — Open WebUI, Dokumenten-Upload, Vektorsuche | demnächst |
| 8 | Deep Research — Vane, zitierte Quellen, private Suche | demnächst |
| 9 | Bildgenerierung — ComfyUI auf 123GB GPU | demnächst |
| 10 | Sprache — whisper.cpp, Kokoro TTS, 54 Stimmen | demnächst |
| 11 | Workflows — n8n-Automatisierung, GitHub Webhooks | demnächst |
| 12 | Die Agenten — Gaia UI, alle 17 Agenten, Verwaltung | demnächst |
| 13 | Man Cave — Kontrollzentrum, Stack-Schutz, Einfrieren/Auftauen | demnächst |
| 14 | Das Mesh — SSH-Schlüssel, 4 Maschinen, Mixer, Shadow | demnächst |
| 15 | Windows im Mesh — Minisforum, VSS, Terminal | demnächst |
| 16 | Discord-Bots — Echo, Bounty, Meek, Amp | demnächst |
| 17 | Reddit-Bridge — scannen, entwerfen, genehmigen, posten | demnächst |
| 18 | Audio-Kette — SM7B, Scarlett, PipeWire, Routing | demnächst |
| 19 | Voice Cloning — Aufnahme, XTTS v2, Training | demnächst |
| 20 | The Downcomers — erster Track, Vocal Doubling, DistroKid | demnächst |
| 21 | Das Spiel — Undercroft, Anti-Cheat, Dealer AI | demnächst |
| 22 | Benchmarks — llama-bench, GitHub Pages, Verlauf | demnächst |
| 23 | CI/CD — GitHub Actions, Releases, Paketierung | demnächst |
| 24 | Vollständige Autonomie-Demo — Tag → Agenten → Reddit-Post | demnächst |

*99% der Nutzer haben kein Claude. Diese Tutorials machen das Erlebnis mühelos auch ohne. „Wo wir hinfahren, brauchen wir keine Straßen."*

## Danksagungen

**Entworfen und gebaut vom Architekten** — jedes Skript, jeder Dienst, jeder Agent. Aus dem Quellcode. Keine Abkürzungen. *„Ich bin unvermeidlich."*

Aufgebaut auf [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) von Light-Heart-Labs. Angetrieben von [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Community: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup) und die Framework/Arch Linux Communities.

## Lizenz

Apache 2.0
