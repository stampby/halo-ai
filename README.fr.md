🌐 [English](README.md) | **Français** | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### La stack IA bare-metal pour AMD Strix Halo

**91 tok/s. Zéro conteneur. 123 Go de mémoire GPU. Compilé depuis les sources. Je connais le kung-fu.**

*construit en CLI — estampillé par l'architecte*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **Nouveau ici ?** Commencez par les [tutoriels](#tutoriels) — des guides vidéo complets, de l'installation au fonctionnement autonome.

---

## C'est quoi ?

Une plateforme IA complète pour le **AMD Ryzen AI MAX+ 395** — inférence LLM, chat, recherche approfondie, voix, génération d'images, RAG et workflows. Pipelines autonomes pour le développement de jeux, la production musicale et la production vidéo. 33 services, 17 agents autonomes, 98 outils, 5 bots Discord. Tout en bare metal, tout compilé depuis les sources, tout sur une seule puce avec 128 Go de mémoire unifiée. Du démarrage à opérationnel : 18,7 secondes.

**Parlez-lui.** Parlez à Halo, voyez le texte, écoutez la réponse. Chaque outil, chaque agent, chaque fonctionnalité — contrôlé par votre voix. Du vibe coding à la maison, prêt à l'emploi, sur votre propre matériel. *« Ouvrez les portes du module, HAL. »*

## Pourquoi le bare metal ?

- **Les conteneurs ajoutent 15 à 20 % de surcharge** sur les charges GPU. Quand vous disposez de 123 Go de mémoire unifiée sur une seule puce, chaque watt et chaque octet doivent servir l'inférence, pas l'orchestration. *« N'essaie pas de plier la cuillère. Essaie plutôt de réaliser la vérité : il n'y a pas de conteneur. »*
- **Compilé depuis les sources** signifie des optimisations natives gfx1151 que les binaires pré-compilés ratent. C'est de là que viennent les 91 tok/s.
- **Pas de minuteries. Pas de cron. Du pur IA.** Les agents ne vérifient pas selon un calendrier — ils surveillent les conditions et agissent quand quelque chose change. Un service tombe ? Détecté et réparé avant que vous ne le remarquiez. Le GPU surchauffe ? Signalé à l'instant même. Pas toutes les 30 secondes. *À l'instant.* Désolé Dave, mais cette stack ne dort jamais.
- **Survit aux mises à jour rolling d'Arch.** Gelez la stack, laissez pacman mettre à jour, les agents détectent si quelque chose a cassé, dégel pour rollback en 30 secondes. C'est pourquoi halo-ai tourne sur Arch sans crainte. *« C'est qu'une égratignure. »*
- **Vous possédez toute la stack.** Aucun gestionnaire de paquets ne décide quand votre serveur IA s'arrête. *« Mon préééécieux. »*

## Installation rapide

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

Installateur interactif — nom d'utilisateur, mots de passe, nom d'hôte, services à activer. Valeurs par défaut sensées. Le mot de passe Caddy par défaut est `Caddy` — changez-le immédiatement. *« Choisissez judicieusement. »*

## Fonctionnalités

### IA et inférence
- **Chat LLM** — [Open WebUI](https://github.com/open-webui/open-webui) avec RAG, multi-modèle, téléversement de documents
- **Recherche approfondie** — [Vane](https://github.com/ItzCrazyKns/Vane) avec sources citées et recherche privée
- **Génération d'images** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) sur 123 Go GPU, SDXL, Flux
- **Génération vidéo** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) sur ROCm 6.3
- **Génération musicale** — [MusicGen](https://github.com/facebookresearch/audiocraft) par Meta, inférence GPU locale
- **Parole-vers-texte** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) compilé pour gfx1151
- **Texte-vers-parole** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) avec 54 voix naturelles
- **Assistant code** — Qwen2.5 Coder 7B sur llama.cpp, 48,6 tok/s
- **Détection d'objets** — [YOLO](https://github.com/ultralytics/ultralytics) v8, inférence en temps réel
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, compilé depuis les sources
- **Traduction** — [Argos Translate](https://github.com/argosopentech/argos-translate), multilingue hors ligne
- **Ajustement fin** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), entraînez vos propres modèles localement
- **API unifiée** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, compatible OpenAI/Ollama/Anthropic

### Agents — [docs](docs/AGENTS.md)
- **17 agents autonomes** sur [AMD Gaia](https://github.com/amd/gaia) avec 98 outils
- **[Echo](https://github.com/stampby/echo)** — visage public, passerelle Reddit, Discord, réseaux sociaux
- **[Meek](https://github.com/stampby/meek)** — chef de la sécurité, 9 sous-agents Reflex ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — chasseur de bugs, sécurité offensive, frère de Halo
- **[Amp](https://github.com/stampby/amp)** — ingénieur audio, clonage vocal, production musicale
- **[Sentinel](https://github.com/stampby/sentinel)** — revue automatique de PR, contrôle du code
- **[Mechanic](https://github.com/stampby/mechanic)** — diagnostics matériel, surveillance système
- **[Forge](https://github.com/stampby/forge)** — constructeur de jeux, pipeline d'assets, déploiement Steam
- **[Dealer](https://github.com/stampby/dealer)** — maître du jeu IA, chaque partie est différente
- **[Conductor](https://github.com/stampby/conductor)** — compositeur IA, musique dynamique de jeu
- **[Quartermaster](https://github.com/stampby/quartermaster)** — opérations serveurs de jeux, audit Steam hebdomadaire
- **[Crypto](https://github.com/stampby/crypto)** — arbitrage, surveillance des marchés
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Sécurité — [docs](docs/SECURITY.md)
- **SSH par clé uniquement** — pas de mots de passe, utilisateur unique, fail2ban. *« Vous ne passerez pas ! »*
- **nftables default-drop** — LAN uniquement, tout le reste est refusé
- **Tous les services sur localhost** — Caddy est le seul point d'entrée
- **Durcissement systemd** — ProtectSystem, PrivateTmp, NoNewPrivileges sur chaque service
- **[Shadow](https://github.com/stampby/shadow)** — surveillance de l'intégrité des fichiers, veille du mesh SSH

### Protection de la stack — [docs](docs/STACK-PROTECTION.md)
- **Gel/dégel** — snapshot et rollback en un clic de toute la stack. *« Je reviendrai. »*
- **Compilation depuis les sources** — recompilations hebdomadaires avec optimisations natives gfx1151
- **[Mixer](https://github.com/stampby/mixer)** — snapshots mesh distribués, pas de NAS, pas de point unique de défaillance
- **Interface Man Cave** — état de la stack, indicateurs de mise à jour, bouton de compilation

### Automatisation — [docs](docs/AUTONOMOUS-PIPELINE.md)
- **Workflows n8n** — les releases GitHub déclenchent automatiquement des posts Reddit via Echo
- **Triage des issues** — les nouvelles issues sont automatiquement routées vers Bounty, Meek ou Amp
- **Snapshots mesh** — Shadow distribue les sauvegardes toutes les 6 heures
- **CI/CD** — GitHub Actions : lint, build, release à chaque tag

### Développement de jeux autonome — [Pipeline](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — jeu d'extraction PvE co-op dans Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — gestionnaire de serveurs de jeux, déploiement en un clic, émulation rétro
- **Maître du jeu IA** — Dealer fait tourner un LLM local, chaque exploration de donjon est unique. *« Tu veux qu'on devienne dingues ? Allons-y ! »*
- **Anti-triche** — RAM chiffrée, surveillance en temps réel, marquage permanent des tricheurs. *« Tu dois te poser une question : est-ce que j'ai de la chance ? »*
- **Pipeline complet** — conception → construction → test → déploiement, les agents gèrent tout. *« La vie, euh, trouve toujours un chemin. »*

### Production musicale autonome — [The Downcomers](https://github.com/stampby/amp)
- **Clonage vocal** — voix de l'architecte via XTTS v2, sorties par jalons
- **Instrumentaux IA** — blues/rock original, groupe complet, pas de reprises
- **Livres audio** — classiques du domaine public, 1984 en première sortie
- **API vocale** — TTS-as-a-Service, zéro rétention de données
- **Voix mémorielle** — capturer la parole de proches, construire un clone IA après leur décès. *« Après tout ce temps ? — Toujours. »*
- **Distribution** — DistroKid vers Spotify, Apple Music, toutes les plateformes

### Production vidéo autonome — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Drame en voxel** — série de 10 épisodes, scénario → voix → animation → rendu
- **Tutoriels vocaux** — l'architecte narre, guides complets
- **Co-présentateur en streaming** — la voix de l'architecte comme commentateur IA en direct pour Twitch/YouTube
- **Pipeline complet** — écriture → jeu d'acteur → rendu → distribution, tout en autonome. *« Lumières, caméra, action. »*

### Infrastructure [Kansas City Shuffle]
- **Mesh SSH de 4 machines [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — snapshots btrfs en anneau via SSH [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — suivi des performances en direct, historique dans le temps
- **[Man Cave](https://github.com/stampby/man-cave)** — centre de contrôle avec métriques GPU, santé des services, activité des agents
- **Zéro cloud** — pas d'abonnements, pas d'APIs, pas de dépendances tierces. *« Il n'y a pas de cloud. Il n'y a que Zuul. »*

## Services

| Service | Port | Fonction |
|---------|------|----------|
| Lemonade | 8080 | API IA unifiée (compatible OpenAI/Ollama/Anthropic) |
| llama.cpp | 8081 | Inférence LLM — double backend Vulkan + HIP |
| Open WebUI | 3000 | Chat avec RAG, documents, multi-modèle |
| Vane | 3001 | Recherche approfondie avec sources citées |
| SearXNG | 8888 | Méta-recherche privée |
| Qdrant | 6333 | Base vectorielle pour le RAG |
| n8n | 5678 | Automatisation de workflows |
| whisper.cpp | 8082 | Parole-vers-texte |
| Kokoro | 8083 | Texte-vers-parole (54 voix) |
| ComfyUI | 8188 | Génération d'images |
| Wan2.1 | — | Génération vidéo (GPU Strix Halo) |
| MusicGen | — | Génération musicale (GPU Strix Halo) |
| YOLO | — | Détection d'objets (Strix Halo) |
| Tesseract | — | OCR — numérisation de documents |
| Argos | — | Traduction hors ligne |
| Axolotl | — | Ajustement fin de modèles (GPU Strix Halo) |
| Prometheus | 9090 | Collecte de métriques |
| Grafana | 3030 | Tableaux de bord de surveillance |
| Node Exporter | 9100 | Métriques système |
| Home Assistant | 8123 | Domotique |
| Borg | — | Sauvegardes chiffrées vers GlusterFS |
| Dashboard | 3003 | Métriques GPU + santé des services |
| Gaia API | 8090 | Serveur du framework d'agents |
| Gaia MCP | 8765 | Pont Model Context Protocol |

Tous les services écoutent sur `127.0.0.1` — accès via le reverse proxy Caddy.

## Performances

| Modèle | Vitesse | VRAM |
|--------|---------|------|
| Qwen3-30B-A3B (MoE) | **83-91 tok/s** | 18 Go |
| Llama 3 70B | ~18 tok/s | 40 Go |

Benchmarks complets avec thermiques, mémoire et comparaisons de backends : [BENCHMARKS.md](BENCHMARKS.md)

## Infrastructure [Kansas City Shuffle]

4 machines — mesh SSH — snapshots mixer — zéro cloud [Kansas City Shuffle]

| Machine | Rôle |
|---------|------|
| ryzen | bureau — développement |
| strix-halo | 128 Go GPU — inférence IA |
| minisforum | Windows 11 — bureautique / tests |
| sligar | 1080Ti — entraînement vocal |

Navigateur > Caddy > Lemonade (API unifiée) > tous les services :

| Service | Ce qu'il fait |
|---------|---------------|
| llama.cpp | Inférence LLM |
| whisper.cpp | Parole-vers-texte |
| Kokoro | Texte-vers-parole |
| ComfyUI | Génération d'images |
| Open WebUI | Chat + RAG |
| Vane | Recherche approfondie |
| n8n | Automatisation de workflows |
| Gaia | 17 agents, 78 outils |
| Man Cave | Centre de contrôle |

Architecture détaillée : [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Documentation

| Guide | Contenu |
|-------|---------|
| [Architecture](docs/ARCHITECTURE.md) | Conception système, flux de données, backends GPU |
| [Services](docs/SERVICES.md) | Ports, configurations, vérifications de santé |
| [Sécurité](docs/SECURITY.md) | Pare-feu, SSH, TLS, rotation des mots de passe |
| [Protection de la stack](docs/STACK-PROTECTION.md) | Pourquoi les mises à jour Arch ne casseront pas votre stack |
| [Benchmarks](BENCHMARKS.md) | Données de performance complètes |
| [Blueprints](docs/BLUEPRINTS.md) | Feuille de route et fonctionnalités prévues |
| [Pipeline autonome](docs/AUTONOMOUS-PIPELINE.md) | Pipeline zéro-humain pour jeux, musique et vidéo |
| [Dépannage](docs/TROUBLESHOOTING.md) | Problèmes courants et solutions |
| [Accès VPN](docs/VPN.md) | Configuration WireGuard |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Bus en anneau, ClusterFS, auto-réparation, gestion du mesh |
| [Mixer](https://github.com/stampby/mixer) | Snapshots SSH mesh — sauvegardes distribuées, pas de point unique de défaillance [Kansas City Shuffle] |
| [Changelog](CHANGELOG.md) | Historique des versions |

## [Captures d'écran](docs/SCREENSHOTS.md)

## Tutoriels

Guides vidéo — du début à la fin, rien n'est sauté. Liens YouTube non répertoriés.

| # | Vidéo | Statut |
|---|-------|--------|
| 1 | La Vision — ce qu'est halo-ai et pourquoi | à venir |
| 2 | Configuration matérielle — câblage du mesh, 4 machines | à venir |
| 3 | Installation d'Arch Linux — OS de base, btrfs, premier démarrage | à venir |
| 4 | Le script d'installation — 13 services compilés depuis les sources | à venir |
| 5 | Sécurité — nftables, SSH, Caddy, modèle deny-all | à venir |
| 6 | Lemonade + llama.cpp — API unifiée, 91 tok/s | à venir |
| 7 | Chat + RAG — Open WebUI, téléversement de documents, recherche vectorielle | à venir |
| 8 | Recherche approfondie — Vane, sources citées, recherche privée | à venir |
| 9 | Génération d'images — ComfyUI sur 123 Go GPU | à venir |
| 10 | Voix — whisper.cpp, Kokoro TTS, 54 voix | à venir |
| 11 | Workflows — automatisation n8n, webhooks GitHub | à venir |
| 12 | Les Agents — interface Gaia, les 17 agents, gestion | à venir |
| 13 | Man Cave — centre de contrôle, protection de la stack, gel/dégel | à venir |
| 14 | Le Mesh — clés SSH, 4 machines, mixer, Shadow | à venir |
| 15 | Windows dans le mesh — Minisforum, VSS, Terminal | à venir |
| 16 | Bots Discord — Echo, Bounty, Meek, Amp | à venir |
| 17 | Passerelle Reddit — scanner, rédiger, approuver, publier | à venir |
| 18 | Chaîne audio — SM7B, Scarlett, PipeWire, routage | à venir |
| 19 | Clonage vocal — enregistrement, XTTS v2, entraînement | à venir |
| 20 | The Downcomers — premier morceau, doublage vocal, DistroKid | à venir |
| 21 | Le Jeu — Undercroft, anti-triche, Dealer IA | à venir |
| 22 | Benchmarks — llama-bench, GitHub Pages, historique | à venir |
| 23 | CI/CD — GitHub Actions, releases, packaging | à venir |
| 24 | Démo autonome complète — tag → agents → post Reddit | à venir |

*99 % des utilisateurs n'ont pas Claude. Ces tutoriels rendent l'expérience simple sans lui. « Là où on va, on n'a pas besoin de routes. »*

## Crédits

**Conçu et construit par l'architecte** — chaque script, chaque service, chaque agent. Depuis les sources. Pas de raccourcis. *« Je suis inévitable. »*

Basé sur [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) par Light-Heart-Labs. Propulsé par [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Communauté : [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), et les communautés Framework/Arch Linux.

## Licence

Apache 2.0
