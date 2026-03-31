🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | **Português** | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### A stack de IA bare-metal para AMD Strix Halo

**87 tok/s. Zero containers. 115GB de memória GPU. Compilado a partir do código-fonte. Eu sei kung fu.**

*construído por CLI — carimbado pelo arquiteto*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **Novo por aqui?** Comece pelos [tutoriais](#tutoriais) — vídeos completos do início ao funcionamento autônomo.

---

## O que é isso?

Uma plataforma de IA completa para o **AMD Ryzen AI MAX+ 395** — inferência LLM, chat, pesquisa profunda, voz, geração de imagens, RAG e workflows. Pipelines autônomos para desenvolvimento de jogos, produção musical e produção de vídeo. 33 serviços, 17 agentes autônomos, 98 ferramentas, 5 bots no Discord. Tudo bare metal, tudo compilado a partir do código-fonte, tudo em um único chip com 128GB de memória unificada. Do boot ao pronto: 18,7 segundos.

**Fale com ele.** Fale com o Halo, veja o texto, ouça a resposta. Cada ferramenta, cada agente, cada recurso — controlado pela sua voz. Vibe coding em casa, pronto para usar, no seu próprio hardware. *"Abra as portas do compartimento, HAL."*

## Por que Bare Metal?

- **Containers adicionam 15-20% de overhead** em cargas de trabalho GPU. Quando você tem 115GB de memória unificada em um único chip, cada watt e cada byte devem ir para inferência, não para orquestração. *"Não tente entortar a colher. Em vez disso, apenas tente perceber a verdade: não existe container."*
- **Compilado a partir do código-fonte** significa otimizações nativas gfx1151 que binários pré-compilados não alcançam. É daí que vêm os 87 tok/s.
- **Sem timers. Sem cron. IA total.** Os agentes não verificam em um cronograma — eles observam condições e agem quando algo muda. Serviço caiu? Detectado e reparado antes de você perceber. GPU superaqueceu? Reportado no momento em que acontece. Não a cada 30 segundos. *No momento.* Desculpe Dave, mas essa stack não dorme.
- **Sobrevive ao rolling release do Arch.** Congele a stack, deixe o pacman atualizar, os agentes detectam se algo quebrou, descongele para rollback em 30 segundos. É por isso que o halo-ai roda no Arch sem medo. *"É apenas um arranhão."*
- **Você é dono de toda a stack.** Nenhum gerenciador de pacotes decide quando seu servidor de IA cai. *"Meu precioso."*

## Instalação Rápida

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

Instalador interativo — nome de usuário, senhas, hostname, quais serviços habilitar. Padrões sensatos. A senha padrão do Caddy é `Caddy` — altere imediatamente. *"Escolha sabiamente."*

## Recursos

### IA & Inferência
- **Chat LLM** — [Open WebUI](https://github.com/open-webui/open-webui) com RAG, multi-modelo, upload de documentos
- **Pesquisa profunda** — [Vane](https://github.com/ItzCrazyKns/Vane) com fontes citadas e busca privada
- **Geração de imagens** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) em 115GB GPU, SDXL, Flux
- **Geração de vídeo** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) em ROCm 6.3
- **Geração de música** — [MusicGen](https://github.com/facebookresearch/audiocraft) da Meta, inferência local na GPU
- **Fala para texto** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) compilado para gfx1151
- **Texto para fala** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) com 54 vozes naturais
- **Assistente de código** — Qwen2.5 Coder 7B no llama.cpp, 48,6 tok/s
- **Detecção de objetos** — [YOLO](https://github.com/ultralytics/ultralytics) v8, inferência em tempo real
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, compilado a partir do código-fonte
- **Tradução** — [Argos Translate](https://github.com/argosopentech/argos-translate), multi-idioma offline
- **Fine-tuning** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), treine seus próprios modelos localmente
- **API unificada** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, compatível com OpenAI/Ollama/Anthropic

### Agentes — [docs](docs/AGENTS.md)
- **17 agentes autônomos** no [AMD Gaia](https://github.com/amd/gaia) com 98 ferramentas
- **[Echo](https://github.com/stampby/echo)** — rosto público, ponte Reddit, Discord, redes sociais
- **[Meek](https://github.com/stampby/meek)** — chefe de segurança, 9 sub-agentes Reflex ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — caçador de bugs, segurança ofensiva, irmão do Halo
- **[Amp](https://github.com/stampby/amp)** — engenheiro de áudio, clonagem de voz, produção musical
- **[Sentinel](https://github.com/stampby/sentinel)** — revisão automática de PRs, controle de código
- **[Mechanic](https://github.com/stampby/mechanic)** — diagnósticos de hardware, monitoramento do sistema
- **[Forge](https://github.com/stampby/forge)** — construtor de jogos, pipeline de assets, deploy na Steam
- **[Dealer](https://github.com/stampby/dealer)** — mestre de jogo IA, cada partida é diferente
- **[Conductor](https://github.com/stampby/conductor)** — compositor IA, trilha sonora dinâmica para jogos
- **[Quartermaster](https://github.com/stampby/quartermaster)** — operações de servidores de jogos, auditoria semanal da Steam
- **[Crypto](https://github.com/stampby/crypto)** — arbitragem, monitoramento de mercado
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Segurança — [docs](docs/SECURITY.md)
- **SSH somente por chave** — sem senhas, usuário único, fail2ban. *"Você não vai passar."*
- **nftables default-drop** — somente LAN, nega todo o resto
- **Todos os serviços em localhost** — Caddy é o único ponto de entrada
- **Hardening systemd** — ProtectSystem, PrivateTmp, NoNewPrivileges em cada serviço
- **[Shadow](https://github.com/stampby/shadow)** — monitoramento de integridade de arquivos, vigilante da mesh SSH

### Proteção da Stack — [docs](docs/STACK-PROTECTION.md)
- **Freeze/thaw** — snapshot e rollback de toda a stack com um clique. *"Eu voltarei."*
- **Compilação a partir do código-fonte** — reconstruções semanais com otimizações nativas gfx1151
- **[Mixer](https://github.com/stampby/mixer)** — snapshots distribuídos em mesh, sem NAS, sem ponto único de falha
- **Man Cave UI** — status da stack, indicadores de atualização, botão de compilação

### Automação — [docs](docs/AUTONOMOUS-PIPELINE.md)
- **Workflows n8n** — lançamentos no GitHub disparam posts automáticos do Echo no Reddit
- **Triagem de issues** — novas issues auto-encaminhadas para Bounty, Meek ou Amp
- **Snapshots em mesh** — Shadow distribui backups a cada 6 horas
- **CI/CD** — GitHub Actions lint, build, release em cada tag

### Desenvolvimento Autônomo de Jogos — [Pipeline](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — jogo PvE co-op de extração no Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — gerenciador de servidores de jogos, deploy com um clique, emulação retrô
- **Mestre de jogo IA** — Dealer roda LLM local, cada dungeon é única. *"Quer enlouquecer? Vamos enlouquecer."*
- **Anti-cheat** — RAM criptografada, monitoramento em tempo real, marca permanente em trapaceiros. *"Você precisa se fazer uma pergunta: Estou me sentindo com sorte?"*
- **Pipeline completo** — design → build → teste → deploy, os agentes cuidam de tudo. *"A vida, uh, encontra um caminho."*

### Produção Musical Autônoma — [The Downcomers](https://github.com/stampby/amp)
- **Clonagem de voz** — voz do arquiteto via XTTS v2, lançamentos em marcos
- **Instrumentais IA** — blues/rock original, banda completa, sem covers
- **Audiobooks** — clássicos de domínio público, 1984 primeiro lançamento
- **API de voz** — TTS-as-a-Service, zero retenção de dados
- **Voz memorial** — capture a fala de entes queridos, construa um clone IA após a morte. *"Depois de todo esse tempo? Sempre."*
- **Distribuição** — DistroKid para Spotify, Apple Music, todas as plataformas

### Produção de Vídeo Autônoma — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Drama voxel** — série de 10 episódios, roteiro → voz → animação → renderização
- **Tutoriais narrados** — o arquiteto narra, walkthroughs completos
- **Co-host de streaming** — voz do arquiteto como comentarista IA ao vivo para Twitch/YouTube
- **Pipeline completo** — roteiro → atuação → renderização → distribuição, tudo autônomo. *"Luzes, câmera, ação."*

### Infraestrutura [Kansas City Shuffle]
- **Mesh SSH de 4 máquinas [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — snapshots btrfs em anel via SSH [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — acompanhamento de desempenho em tempo real, histórico ao longo do tempo
- **[Man Cave](https://github.com/stampby/man-cave)** — centro de controle com métricas de GPU, saúde dos serviços, atividade dos agentes
- **Zero cloud** — sem assinaturas, sem APIs, sem dependências de terceiros. *"Não existe nuvem. Existe apenas Zuul."*

## Serviços

| Serviço | Porta | Finalidade |
|---------|-------|------------|
| Lemonade | 8080 | API de IA unificada (compatível com OpenAI/Ollama/Anthropic) |
| llama.cpp | 8081 | Inferência LLM — backends duplos Vulkan + HIP |
| Open WebUI | 3000 | Chat com RAG, documentos, multi-modelo |
| Vane | 3001 | Pesquisa profunda com fontes citadas |
| SearXNG | 8888 | Meta-busca privada |
| Qdrant | 6333 | Banco de dados vetorial para RAG |
| n8n | 5678 | Automação de workflows |
| whisper.cpp | 8082 | Fala para texto |
| Kokoro | 8083 | Texto para fala (54 vozes) |
| ComfyUI | 8188 | Geração de imagens |
| Wan2.1 | — | Geração de vídeo (GPU Strix Halo) |
| MusicGen | — | Geração de música (GPU Strix Halo) |
| YOLO | — | Detecção de objetos (Strix Halo) |
| Tesseract | — | OCR — digitalização de documentos |
| Argos | — | Tradução offline |
| Axolotl | — | Fine-tuning de modelos (GPU Strix Halo) |
| Prometheus | 9090 | Coleta de métricas |
| Grafana | 3030 | Dashboards de monitoramento |
| Node Exporter | 9100 | Métricas do sistema |
| Home Assistant | 8123 | Automação residencial |
| Borg | — | Backups criptografados para GlusterFS |
| Dashboard | 3003 | Métricas de GPU + saúde dos serviços |
| Gaia API | 8090 | Servidor do framework de agentes |
| Gaia MCP | 8765 | Ponte Model Context Protocol |

Todos os serviços fazem bind em `127.0.0.1` — acesso via reverse proxy Caddy.

## Desempenho

| Modelo | Velocidade | VRAM |
|--------|-----------|------|
| Qwen3-30B-A3B (MoE) | **87 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

Benchmarks completos com temperaturas, memória e comparações de backends: [BENCHMARKS.md](BENCHMARKS.md)

## Infraestrutura [Kansas City Shuffle]

4 máquinas — mesh SSH — snapshots mixer — zero cloud [Kansas City Shuffle]

| Máquina | Função |
|---------|--------|
| ryzen | desktop — desenvolvimento |
| strix-halo | 128GB GPU — inferência IA |
| minisforum | Windows 11 — escritório / testes |
| sligar | 1080Ti — treinamento de voz |

Navegador > Caddy > Lemonade (API unificada) > todos os serviços:

| Serviço | O que faz |
|---------|-----------|
| llama.cpp | Inferência LLM |
| whisper.cpp | fala para texto |
| Kokoro | texto para fala |
| ComfyUI | geração de imagens |
| Open WebUI | chat + RAG |
| Vane | pesquisa profunda |
| n8n | automação de workflows |
| Gaia | 17 agentes, 78 ferramentas |
| Man Cave | centro de controle |

Detalhes completos da arquitetura: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Documentação

| Guia | O que cobre |
|------|-------------|
| [Arquitetura](docs/ARCHITECTURE.md) | Design do sistema, fluxo de dados, backends GPU |
| [Serviços](docs/SERVICES.md) | Portas, configurações, health checks |
| [Segurança](docs/SECURITY.md) | Firewall, SSH, TLS, rotação de senhas |
| [Proteção da Stack](docs/STACK-PROTECTION.md) | Por que atualizações do Arch não vão quebrar sua stack |
| [Benchmarks](BENCHMARKS.md) | Dados completos de desempenho |
| [Blueprints](docs/BLUEPRINTS.md) | Roadmap e recursos planejados |
| [Pipeline Autônomo](docs/AUTONOMOUS-PIPELINE.md) | Pipeline de produção zero-humano para jogos, música e vídeo |
| [Solução de Problemas](docs/TROUBLESHOOTING.md) | Problemas comuns e correções |
| [Acesso VPN](docs/VPN.md) | Configuração do WireGuard |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Ring bus, ClusterFS, auto-reparo, gerenciamento de mesh |
| [Mixer](https://github.com/stampby/mixer) | Snapshots SSH em mesh — backups distribuídos, sem ponto único de falha [Kansas City Shuffle] |
| [Changelog](CHANGELOG.md) | Histórico de versões |

## [Capturas de Tela](docs/SCREENSHOTS.md)

## Tutoriais

Vídeos passo a passo — do início ao fim, sem pular nada. Links não listados do YouTube.

| # | Vídeo | Status |
|---|-------|--------|
| 1 | A Visão — o que é o halo-ai e por quê | em breve |
| 2 | Configuração de Hardware — cabeamento da mesh, 4 máquinas | em breve |
| 3 | Instalação do Arch Linux — SO base, btrfs, primeiro boot | em breve |
| 4 | O Script de Instalação — 13 serviços compilados a partir do código-fonte | em breve |
| 5 | Segurança — nftables, SSH, Caddy, modelo deny-all | em breve |
| 6 | Lemonade + llama.cpp — API unificada, 87 tok/s | em breve |
| 7 | Chat + RAG — Open WebUI, upload de documentos, busca vetorial | em breve |
| 8 | Pesquisa Profunda — Vane, fontes citadas, busca privada | em breve |
| 9 | Geração de Imagens — ComfyUI em 115GB GPU | em breve |
| 10 | Voz — whisper.cpp, Kokoro TTS, 54 vozes | em breve |
| 11 | Workflows — automação n8n, webhooks GitHub | em breve |
| 12 | Os Agentes — Gaia UI, todos os 17 agentes, gerenciamento | em breve |
| 13 | Man Cave — centro de controle, proteção da stack, freeze/thaw | em breve |
| 14 | A Mesh — chaves SSH, 4 máquinas, mixer, Shadow | em breve |
| 15 | Windows na Mesh — Minisforum, VSS, Terminal | em breve |
| 16 | Bots do Discord — Echo, Bounty, Meek, Amp | em breve |
| 17 | Ponte Reddit — escanear, redigir, aprovar, publicar | em breve |
| 18 | Cadeia de Áudio — SM7B, Scarlett, PipeWire, roteamento | em breve |
| 19 | Clonagem de Voz — gravação, XTTS v2, treinamento | em breve |
| 20 | The Downcomers — primeira faixa, duplicação vocal, DistroKid | em breve |
| 21 | O Jogo — Undercroft, anti-cheat, Dealer AI | em breve |
| 22 | Benchmarks — llama-bench, GitHub Pages, histórico | em breve |
| 23 | CI/CD — GitHub Actions, releases, empacotamento | em breve |
| 24 | Demo Autônomo Completo — tag → agentes → post no Reddit | em breve |

*99% dos usuários não têm o Claude. Esses tutoriais tornam a experiência simples sem ele. "Para onde estamos indo, não precisamos de estradas."*

## Créditos

**Projetado e construído pelo arquiteto** — cada script, cada serviço, cada agente. A partir do código-fonte. Sem atalhos. *"Eu sou inevitável."*

Construído sobre o [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) da Light-Heart-Labs. Powered by [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Comunidade: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), e as comunidades Framework/Arch Linux.

## Licença

Apache 2.0
