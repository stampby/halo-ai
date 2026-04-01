🌐 [English](README.md) | [Français](README.fr.md) | **Español** | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### El stack de IA bare-metal para AMD Strix Halo

**91 tok/s. Cero contenedores. 123GB de memoria GPU. Compilado desde el código fuente. Ya sé kung fu.**

*construido por CLI — firmado por el arquitecto*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **¿Nuevo aquí?** Empieza con los [tutoriales](#tutoriales) — videos completos paso a paso desde la instalación hasta la operación autónoma.

---

## ¿Qué es esto?

Una plataforma de IA completa para el **AMD Ryzen AI MAX+ 395** — inferencia LLM, chat, investigación profunda, voz, generación de imágenes, RAG y flujos de trabajo. Pipelines autónomos para desarrollo de videojuegos, producción musical y producción de video. 33 servicios, 17 agentes autónomos, 98 herramientas, 5 bots de Discord. Todo bare metal, todo compilado desde el código fuente, todo en un solo chip con 128GB de memoria unificada. De arranque a listo: 18.7 segundos.

**Háblale.** Habla con Halo, ve el texto, escucha la respuesta. Cada herramienta, cada agente, cada función — controlada por tu voz. Vibe coding en casa, listo para usar, en tu propio hardware. *"Abre las puertas del hangar, HAL."*

## ¿Por qué bare metal?

- **Los contenedores añaden un 15-20% de sobrecarga** en cargas de trabajo GPU. Cuando tienes 123GB de memoria unificada en un solo chip, cada vatio y cada byte debe ir a la inferencia, no a la orquestación. *"No intentes doblar la cuchara. En su lugar, solo intenta comprender la verdad: no hay contenedor."*
- **Compilado desde el código fuente** significa optimizaciones nativas para gfx1151 que los binarios precompilados no tienen. De ahí vienen los 91 tok/s.
- **Sin temporizadores. Sin cron. IA total.** Los agentes no revisan por horario — observan condiciones y actúan cuando algo cambia. ¿Un servicio se cayó? Detectado y reparado antes de que lo notes. ¿La GPU se sobrecalienta? Reportado en el momento en que sucede. No cada 30 segundos. *En el momento.* Lo siento Dave, pero este stack no duerme.
- **Sobrevive al rolling release de Arch.** Congela el stack, deja que pacman actualice, los agentes detectan si algo se rompió, descongela para revertir en 30 segundos. Por eso halo-ai corre en Arch sin miedo. *"Es solo un rasguño."*
- **Eres dueño de todo el stack.** Ningún gestor de paquetes decide cuándo tu servidor de IA se cae. *"Mi tesoro."*

## Instalación rápida

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

Instalador interactivo — usuario, contraseñas, hostname, qué servicios habilitar. Valores sensatos por defecto. La contraseña predeterminada de Caddy es `Caddy` — cámbiala inmediatamente. *"Elige sabiamente."*

## Características

### IA e inferencia
- **Chat LLM** — [Open WebUI](https://github.com/open-webui/open-webui) con RAG, multi-modelo, carga de documentos
- **Investigación profunda** — [Vane](https://github.com/ItzCrazyKns/Vane) con fuentes citadas y búsqueda privada
- **Generación de imágenes** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) en 123GB de GPU, SDXL, Flux
- **Generación de video** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) en ROCm 6.3
- **Generación de música** — [MusicGen](https://github.com/facebookresearch/audiocraft) de Meta, inferencia GPU local
- **Voz a texto** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) compilado para gfx1151
- **Texto a voz** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) con 54 voces naturales
- **Asistente de código** — Qwen2.5 Coder 7B en llama.cpp, 48.6 tok/s
- **Detección de objetos** — [YOLO](https://github.com/ultralytics/ultralytics) v8, inferencia en tiempo real
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, compilado desde el código fuente
- **Traducción** — [Argos Translate](https://github.com/argosopentech/argos-translate), multi-idioma sin conexión
- **Fine-tuning** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), entrena tus propios modelos localmente
- **API unificada** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, compatible con OpenAI/Ollama/Anthropic

### Agentes — [documentación](docs/AGENTS.md)
- **17 agentes autónomos** en [AMD Gaia](https://github.com/amd/gaia) con 98 herramientas
- **[Echo](https://github.com/stampby/echo)** — cara pública, puente Reddit, Discord, redes sociales
- **[Meek](https://github.com/stampby/meek)** — jefe de seguridad, 9 sub-agentes Reflex ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — cazador de bugs, seguridad ofensiva, hermano de Halo
- **[Amp](https://github.com/stampby/amp)** — ingeniero de audio, clonación de voz, producción musical
- **[Sentinel](https://github.com/stampby/sentinel)** — revisión automática de PRs, control de código
- **[Mechanic](https://github.com/stampby/mechanic)** — diagnóstico de hardware, monitoreo del sistema
- **[Forge](https://github.com/stampby/forge)** — constructor de juegos, pipeline de assets, deploy en Steam
- **[Dealer](https://github.com/stampby/dealer)** — maestro de juego IA, cada partida es diferente
- **[Conductor](https://github.com/stampby/conductor)** — compositor IA, banda sonora dinámica para juegos
- **[Quartermaster](https://github.com/stampby/quartermaster)** — operaciones de servidores de juegos, auditoría semanal de Steam
- **[Crypto](https://github.com/stampby/crypto)** — arbitraje, monitoreo de mercado
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Seguridad — [documentación](docs/SECURITY.md)
- **Solo claves SSH** — sin contraseñas, usuario único, fail2ban. *"No puedes pasar."*
- **nftables default-drop** — solo LAN, deniega todo lo demás
- **Todos los servicios en localhost** — Caddy es el único punto de entrada
- **Hardening de systemd** — ProtectSystem, PrivateTmp, NoNewPrivileges en cada servicio
- **[Shadow](https://github.com/stampby/shadow)** — monitoreo de integridad de archivos, vigilante del mesh SSH

### Protección del stack — [documentación](docs/STACK-PROTECTION.md)
- **Congelar/descongelar** — snapshot y rollback de todo el stack con un solo clic. *"Volveré."*
- **Compilar desde el código fuente** — recompilaciones semanales con optimizaciones nativas para gfx1151
- **[Mixer](https://github.com/stampby/mixer)** — snapshots distribuidos en mesh, sin NAS, sin punto único de fallo
- **Interfaz Man Cave** — estado del stack, indicadores de actualización, botón de compilación

### Automatización — [documentación](docs/AUTONOMOUS-PIPELINE.md)
- **Flujos de trabajo n8n** — releases de GitHub activan publicaciones de Echo en Reddit automáticamente
- **Triaje de issues** — nuevos issues auto-dirigidos a Bounty, Meek o Amp
- **Snapshots en mesh** — Shadow distribuye backups cada 6 horas
- **CI/CD** — GitHub Actions lint, build, release en cada tag

### Desarrollo autónomo de videojuegos — [Pipeline](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — juego de extracción PvE cooperativo en Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — gestor de servidores de juegos, deploy con un clic, emulación retro
- **Maestro de juego IA** — Dealer ejecuta LLM local, cada mazmorra es única. *"¿Quieres volverte loco? ¡Vamos a volvernos locos!"*
- **Anti-cheat** — RAM encriptada, monitoreo en tiempo de ejecución, marca permanente para tramposos. *"Tienes que hacerte una pregunta: ¿Te sientes con suerte?"*
- **Pipeline completo** — diseño → construcción → pruebas → deploy, los agentes se encargan de todo. *"La vida encuentra su camino."*

### Producción musical autónoma — [The Downcomers](https://github.com/stampby/amp)
- **Clonación de voz** — voz del arquitecto vía XTTS v2, lanzamientos por hitos
- **Instrumentales IA** — blues/rock original, banda completa, sin covers
- **Audiolibros** — clásicos de dominio público, 1984 primer lanzamiento
- **API de voz** — TTS como servicio, cero retención de datos
- **Voz memorial** — captura el habla de seres queridos, construye un clon IA después de su muerte. *"¿Después de todo este tiempo? Siempre."*
- **Distribución** — DistroKid a Spotify, Apple Music, todas las plataformas

### Producción de video autónoma — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Drama voxel** — serie de 10 episodios, guion → voz → animación → render
- **Tutoriales con voz** — el arquitecto narra, recorridos completos
- **Co-presentador de streaming** — voz del arquitecto como comentarista IA en vivo para Twitch/YouTube
- **Pipeline completo** — escritura → actuación → renderizado → distribución, todo autónomo. *"Luces, cámara, acción."*

### Infraestructura [Kansas City Shuffle]
- **Mesh SSH de 4 máquinas [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — snapshots btrfs en anillo sobre SSH [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — seguimiento de rendimiento en vivo, historial a lo largo del tiempo
- **[Man Cave](https://github.com/stampby/man-cave)** — centro de control con métricas GPU, salud de servicios, actividad de agentes
- **Cero nube** — sin suscripciones, sin APIs, sin dependencias de terceros. *"No hay nube. Solo hay Zuul."*

## Servicios

| Servicio | Puerto | Propósito |
|----------|--------|-----------|
| Lemonade | 8080 | API de IA unificada (compatible con OpenAI/Ollama/Anthropic) |
| llama.cpp | 8081 | Inferencia LLM — backends dual Vulkan + HIP |
| Open WebUI | 3000 | Chat con RAG, documentos, multi-modelo |
| Vane | 3001 | Investigación profunda con fuentes citadas |
| SearXNG | 8888 | Meta-búsqueda privada |
| Qdrant | 6333 | Base de datos vectorial para RAG |
| n8n | 5678 | Automatización de flujos de trabajo |
| whisper.cpp | 8082 | Voz a texto |
| Kokoro | 8083 | Texto a voz (54 voces) |
| ComfyUI | 8188 | Generación de imágenes |
| Wan2.1 | — | Generación de video (GPU Strix Halo) |
| MusicGen | — | Generación de música (GPU Strix Halo) |
| YOLO | — | Detección de objetos (Strix Halo) |
| Tesseract | — | OCR — escaneo de documentos |
| Argos | — | Traducción sin conexión |
| Axolotl | — | Fine-tuning de modelos (GPU Strix Halo) |
| Prometheus | 9090 | Recolección de métricas |
| Grafana | 3030 | Paneles de monitoreo |
| Node Exporter | 9100 | Métricas del sistema |
| Home Assistant | 8123 | Automatización del hogar |
| Borg | — | Backups encriptados a GlusterFS |
| Dashboard | 3003 | Métricas GPU + salud de servicios |
| Gaia API | 8090 | Servidor del framework de agentes |
| Gaia MCP | 8765 | Puente Model Context Protocol |

Todos los servicios se vinculan a `127.0.0.1` — acceso vía Caddy reverse proxy.

## Rendimiento

| Modelo | Velocidad | VRAM |
|--------|-----------|------|
| Qwen3-30B-A3B (MoE) | **83-91 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

Benchmarks completos con temperaturas, memoria y comparaciones de backends: [BENCHMARKS.md](BENCHMARKS.md)

## Infraestructura [Kansas City Shuffle]

4 máquinas — mesh SSH — snapshots mixer — cero nube [Kansas City Shuffle]

| Máquina | Rol |
|---------|-----|
| ryzen | escritorio — desarrollo |
| strix-halo | 128GB GPU — inferencia IA |
| minisforum | Windows 11 — oficina / pruebas |
| sligar | 1080Ti — entrenamiento de voz |

Navegador > Caddy > Lemonade (API unificada) > todos los servicios:

| Servicio | Qué hace |
|----------|----------|
| llama.cpp | Inferencia LLM |
| whisper.cpp | voz a texto |
| Kokoro | texto a voz |
| ComfyUI | generación de imágenes |
| Open WebUI | chat + RAG |
| Vane | investigación profunda |
| n8n | automatización de flujos de trabajo |
| Gaia | 17 agentes, 78 herramientas |
| Man Cave | centro de control |

Detalles completos de la arquitectura: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Documentación

| Guía | Qué cubre |
|------|-----------|
| [Arquitectura](docs/ARCHITECTURE.md) | Diseño del sistema, flujo de datos, backends GPU |
| [Servicios](docs/SERVICES.md) | Puertos, configuraciones, health checks |
| [Seguridad](docs/SECURITY.md) | Firewall, SSH, TLS, rotación de contraseñas |
| [Protección del stack](docs/STACK-PROTECTION.md) | Por qué las actualizaciones de Arch no romperán tu stack |
| [Benchmarks](BENCHMARKS.md) | Datos completos de rendimiento |
| [Planos](docs/BLUEPRINTS.md) | Hoja de ruta y funciones planificadas |
| [Pipeline autónomo](docs/AUTONOMOUS-PIPELINE.md) | Pipeline de producción de juegos, música y video sin intervención humana |
| [Solución de problemas](docs/TROUBLESHOOTING.md) | Problemas comunes y soluciones |
| [Acceso VPN](docs/VPN.md) | Configuración de WireGuard |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Ring bus, ClusterFS, auto-reparación, gestión del mesh |
| [Mixer](https://github.com/stampby/mixer) | Snapshots SSH en mesh — backups distribuidos, sin punto único de fallo [Kansas City Shuffle] |
| [Registro de cambios](CHANGELOG.md) | Historial de versiones |

## [Capturas de pantalla](docs/SCREENSHOTS.md)

## Tutoriales

Videos paso a paso — de principio a fin, sin saltar nada. Enlaces de YouTube no listados.

| # | Video | Estado |
|---|-------|--------|
| 1 | La visión — qué es halo-ai y por qué | próximamente |
| 2 | Configuración de hardware — cableado del mesh, 4 máquinas | próximamente |
| 3 | Instalación de Arch Linux — SO base, btrfs, primer arranque | próximamente |
| 4 | El script de instalación — 13 servicios compilados desde el código fuente | próximamente |
| 5 | Seguridad — nftables, SSH, Caddy, modelo deny-all | próximamente |
| 6 | Lemonade + llama.cpp — API unificada, 91 tok/s | próximamente |
| 7 | Chat + RAG — Open WebUI, carga de documentos, búsqueda vectorial | próximamente |
| 8 | Investigación profunda — Vane, fuentes citadas, búsqueda privada | próximamente |
| 9 | Generación de imágenes — ComfyUI en 123GB de GPU | próximamente |
| 10 | Voz — whisper.cpp, Kokoro TTS, 54 voces | próximamente |
| 11 | Flujos de trabajo — automatización n8n, webhooks de GitHub | próximamente |
| 12 | Los agentes — Gaia UI, los 17 agentes, gestión | próximamente |
| 13 | Man Cave — centro de control, protección del stack, congelar/descongelar | próximamente |
| 14 | El mesh — claves SSH, 4 máquinas, mixer, Shadow | próximamente |
| 15 | Windows en el mesh — Minisforum, VSS, Terminal | próximamente |
| 16 | Bots de Discord — Echo, Bounty, Meek, Amp | próximamente |
| 17 | Puente Reddit — escanear, redactar, aprobar, publicar | próximamente |
| 18 | Cadena de audio — SM7B, Scarlett, PipeWire, enrutamiento | próximamente |
| 19 | Clonación de voz — grabación, XTTS v2, entrenamiento | próximamente |
| 20 | The Downcomers — primer tema, doblaje vocal, DistroKid | próximamente |
| 21 | El juego — Undercroft, anti-cheat, Dealer AI | próximamente |
| 22 | Benchmarks — llama-bench, GitHub Pages, historial | próximamente |
| 23 | CI/CD — GitHub Actions, releases, empaquetado | próximamente |
| 24 | Demo autónoma completa — tag → agentes → publicación en Reddit | próximamente |

*El 99% de los usuarios no tiene Claude. Estos tutoriales hacen que la experiencia sea sencilla sin él. "A donde vamos, no necesitamos caminos."*

## Créditos

**Diseñado y construido por el arquitecto** — cada script, cada servicio, cada agente. Desde el código fuente. Sin atajos. *"Yo soy inevitable."*

Construido sobre [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) de Light-Heart-Labs. Impulsado por [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Comunidad: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), y las comunidades de Framework/Arch Linux.

## Licencia

Apache 2.0
