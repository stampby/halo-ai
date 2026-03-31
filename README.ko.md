🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | **한국어** | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### AMD Strix Halo를 위한 베어메탈 AI 스택

**87 tok/s. 컨테이너 제로. 115GB GPU 메모리. 소스에서 직접 컴파일. 나는 쿵후를 안다.**

*CLI로 구축 — 아키텍트가 각인*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **처음이신가요?** [튜토리얼](#튜토리얼)부터 시작하세요 — 설치부터 자율 운영까지 전체 영상 안내가 준비되어 있습니다.

---

## 이것은 무엇인가?

**AMD Ryzen AI MAX+ 395**를 위한 완전한 AI 플랫폼 — LLM 추론, 채팅, 심층 연구, 음성, 이미지 생성, RAG, 워크플로우. 게임 개발, 음악 제작, 영상 제작을 위한 자율 파이프라인. 33개의 서비스, 17개의 자율 에이전트, 98개의 도구, 5개의 Discord 봇. 모두 베어메탈, 모두 소스에서 컴파일, 128GB 통합 메모리를 가진 단일 칩에서 모두 실행. 부팅부터 준비까지: 18.7초.

**말을 걸어보세요.** Halo에게 말하면, 텍스트를 보고, 응답을 들을 수 있습니다. 모든 도구, 모든 에이전트, 모든 기능 — 음성으로 제어합니다. 집에서 바로, 자신의 하드웨어에서, 바이브 코딩. *"포드 베이 문을 열어줘, HAL."*

## 왜 베어메탈인가?

- **컨테이너는 GPU 워크로드에 15-20% 오버헤드를 추가합니다.** 단일 칩에 115GB 통합 메모리가 있을 때, 모든 와트와 바이트는 오케스트레이션이 아닌 추론에 사용되어야 합니다. *"숟가락을 구부리려 하지 마라. 대신 진실을 깨달으려 해라: 컨테이너는 없다."*
- **소스에서 컴파일**하면 사전 빌드된 바이너리가 놓치는 네이티브 gfx1151 최적화를 적용할 수 있습니다. 87 tok/s는 거기서 나옵니다.
- **타이머 없음. Cron 없음. 완전한 AI.** 에이전트는 일정에 따라 확인하지 않습니다 — 조건을 감시하고 변화가 있을 때 행동합니다. 서비스가 다운되면? 당신이 알아차리기 전에 감지하고 복구합니다. GPU가 과열되면? 발생하는 그 순간 보고합니다. 30초마다가 아닙니다. *그 순간.* 미안하지만 Dave, 이 스택은 잠들지 않습니다.
- **Arch 롤링 릴리스에서도 생존합니다.** 스택을 동결하고, pacman이 업데이트하게 하고, 에이전트가 문제를 감지하면 30초 만에 롤백합니다. 이것이 halo-ai가 두려움 없이 Arch에서 실행되는 이유입니다. *"이건 그저 가벼운 상처일 뿐."*
- **전체 스택을 소유합니다.** 패키지 매니저가 AI 서버의 다운 시점을 결정하지 않습니다. *"나의 보물."*

## 빠른 설치

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

대화형 설치 — 사용자 이름, 비밀번호, 호스트명, 활성화할 서비스를 선택합니다. 합리적인 기본값. 기본 Caddy 비밀번호는 `Caddy`입니다 — 즉시 변경하세요. *"현명하게 선택하라."*

## 기능

### AI 및 추론
- **LLM 채팅** — RAG, 멀티 모델, 문서 업로드가 포함된 [Open WebUI](https://github.com/open-webui/open-webui)
- **심층 연구** — 출처 인용과 비공개 검색이 가능한 [Vane](https://github.com/ItzCrazyKns/Vane)
- **이미지 생성** — 115GB GPU의 [ComfyUI](https://github.com/comfyanonymous/ComfyUI), SDXL, Flux
- **영상 생성** — ROCm 6.3 기반 [Wan2.1](https://github.com/Wan-Video/Wan2.1)
- **음악 생성** — Meta의 [MusicGen](https://github.com/facebookresearch/audiocraft), 로컬 GPU 추론
- **음성-텍스트 변환** — gfx1151용으로 컴파일된 [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- **텍스트-음성 변환** — 54개의 자연스러운 음성을 가진 [Kokoro](https://github.com/remsky/Kokoro-FastAPI)
- **코드 어시스턴트** — llama.cpp의 Qwen2.5 Coder 7B, 48.6 tok/s
- **객체 감지** — [YOLO](https://github.com/ultralytics/ultralytics) v8, 실시간 추론
- **OCR** — 소스에서 컴파일된 [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2
- **번역** — [Argos Translate](https://github.com/argosopentech/argos-translate), 오프라인 다국어
- **파인튜닝** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), 로컬에서 자체 모델 훈련
- **통합 API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, OpenAI/Ollama/Anthropic 호환

### 에이전트 — [문서](docs/AGENTS.md)
- **17개의 자율 에이전트** — 98개의 도구를 갖춘 [AMD Gaia](https://github.com/amd/gaia) 기반
- **[Echo](https://github.com/stampby/echo)** — 공개 얼굴, Reddit 브릿지, Discord, 소셜 미디어
- **[Meek](https://github.com/stampby/meek)** — 보안 책임자, 9개의 Reflex 하위 에이전트 ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — 버그 헌터, 공격적 보안, Halo의 형제
- **[Amp](https://github.com/stampby/amp)** — 오디오 엔지니어, 음성 복제, 음악 제작
- **[Sentinel](https://github.com/stampby/sentinel)** — 자동 PR 리뷰, 코드 게이팅
- **[Mechanic](https://github.com/stampby/mechanic)** — 하드웨어 진단, 시스템 모니터링
- **[Forge](https://github.com/stampby/forge)** — 게임 빌더, 에셋 파이프라인, Steam 배포
- **[Dealer](https://github.com/stampby/dealer)** — AI 게임 마스터, 매번 다른 플레이
- **[Conductor](https://github.com/stampby/conductor)** — AI 작곡가, 동적 게임 스코어링
- **[Quartermaster](https://github.com/stampby/quartermaster)** — 게임 서버 운영, 주간 Steam 감사
- **[Crypto](https://github.com/stampby/crypto)** — 차익거래, 시장 모니터링
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### 보안 — [문서](docs/SECURITY.md)
- **SSH 키 전용** — 비밀번호 없음, 단일 사용자, fail2ban. *"너는 지나갈 수 없다."*
- **nftables 기본 차단** — LAN만 허용, 나머지 모두 거부
- **모든 서비스 localhost 바인딩** — Caddy가 유일한 진입점
- **Systemd 강화** — 모든 서비스에 ProtectSystem, PrivateTmp, NoNewPrivileges 적용
- **[Shadow](https://github.com/stampby/shadow)** — 파일 무결성 모니터링, SSH 메시 감시

### 스택 보호 — [문서](docs/STACK-PROTECTION.md)
- **동결/해동** — 전체 스택의 원클릭 스냅샷과 롤백. *"돌아오겠다."*
- **소스에서 컴파일** — 네이티브 gfx1151 최적화로 주간 재빌드
- **[Mixer](https://github.com/stampby/mixer)** — 분산 메시 스냅샷, NAS 없음, 단일 장애점 없음
- **Man Cave UI** — 스택 상태, 업데이트 표시, 컴파일 버튼

### 자동화 — [문서](docs/AUTONOMOUS-PIPELINE.md)
- **n8n 워크플로우** — GitHub 릴리스가 Echo Reddit 게시물을 자동으로 트리거
- **이슈 분류** — 새 이슈를 Bounty, Meek, Amp에게 자동 라우팅
- **메시 스냅샷** — Shadow가 6시간마다 백업 배포
- **CI/CD** — 모든 태그에서 GitHub Actions lint, 빌드, 릴리스

### 자율 게임 개발 — [파이프라인](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — Godot 4 기반 PvE 협동 추출 게임
- **[Arcade](https://github.com/stampby/halo-arcade)** — 게임 서버 매니저, 원클릭 배포, 레트로 에뮬레이션
- **AI 게임 마스터** — Dealer가 로컬 LLM을 실행, 매번 던전이 유니크합니다. *"미쳐볼래? 미쳐보자."*
- **안티 치트** — 암호화된 RAM, 런타임 모니터링, 치터 영구 낙인. *"스스로에게 물어봐야 해: 운이 좋다고 느끼나?"*
- **전체 파이프라인** — 설계 → 빌드 → 테스트 → 배포, 에이전트가 모든 것을 처리합니다. *"생명은, 음, 길을 찾는 법이지."*

### 자율 음악 제작 — [The Downcomers](https://github.com/stampby/amp)
- **음성 복제** — XTTS v2를 통한 아키텍트의 음성, 마일스톤 릴리스
- **AI 연주** — 오리지널 블루스/록, 풀 밴드, 커버 없음
- **오디오북** — 퍼블릭 도메인 고전, 1984 첫 릴리스
- **Voice API** — TTS-as-a-Service, 데이터 보존 제로
- **추모 음성** — 사랑하는 이의 음성을 캡처하고, 사후 AI 클론을 구축합니다. *"그 모든 시간이 지나고도? 항상."*
- **배포** — DistroKid를 통해 Spotify, Apple Music, 모든 플랫폼

### 자율 영상 제작 — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **복셀 드라마** — 10부작 시리즈, 대본 → 음성 → 애니메이션 → 렌더링
- **음성 튜토리얼** — 아키텍트가 내레이션, 전체 안내
- **스트리밍 공동 진행** — Twitch/YouTube를 위한 아키텍트 음성 라이브 AI 코멘테이터
- **전체 파이프라인** — 집필 → 연기 → 렌더링 → 배포, 모두 자율적. *"라이트, 카메라, 액션."*

### 인프라 [Kansas City Shuffle]
- **4대 머신 SSH 메시 [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — SSH를 통한 btrfs 링 스냅샷 [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — 실시간 성능 추적, 시간별 이력
- **[Man Cave](https://github.com/stampby/man-cave)** — GPU 메트릭, 서비스 상태, 에이전트 활동을 갖춘 제어 센터
- **제로 클라우드** — 구독 없음, API 없음, 서드파티 의존성 없음. *"클라우드는 없다. 오직 Zuul만 있을 뿐."*

## 서비스

| 서비스 | 포트 | 용도 |
|---------|------|---------|
| Lemonade | 8080 | 통합 AI API (OpenAI/Ollama/Anthropic 호환) |
| llama.cpp | 8081 | LLM 추론 — Vulkan + HIP 듀얼 백엔드 |
| Open WebUI | 3000 | RAG, 문서, 멀티 모델 채팅 |
| Vane | 3001 | 출처 인용 기반 심층 연구 |
| SearXNG | 8888 | 비공개 메타 검색 |
| Qdrant | 6333 | RAG용 벡터 DB |
| n8n | 5678 | 워크플로우 자동화 |
| whisper.cpp | 8082 | 음성-텍스트 변환 |
| Kokoro | 8083 | 텍스트-음성 변환 (54개 음성) |
| ComfyUI | 8188 | 이미지 생성 |
| Wan2.1 | — | 영상 생성 (Strix Halo GPU) |
| MusicGen | — | 음악 생성 (Strix Halo GPU) |
| YOLO | — | 객체 감지 (Strix Halo) |
| Tesseract | — | OCR — 문서 스캔 |
| Argos | — | 오프라인 번역 |
| Axolotl | — | 모델 파인튜닝 (Strix Halo GPU) |
| Prometheus | 9090 | 메트릭 수집 |
| Grafana | 3030 | 모니터링 대시보드 |
| Node Exporter | 9100 | 시스템 메트릭 |
| Home Assistant | 8123 | 홈 자동화 |
| Borg | — | GlusterFS로의 암호화 백업 |
| Dashboard | 3003 | GPU 메트릭 + 서비스 상태 |
| Gaia API | 8090 | 에이전트 프레임워크 서버 |
| Gaia MCP | 8765 | Model Context Protocol 브릿지 |

모든 서비스는 `127.0.0.1`에 바인딩됩니다 — Caddy 리버스 프록시를 통해 접근합니다.

## 성능

| 모델 | 속도 | VRAM |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **87 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

열, 메모리, 백엔드 비교가 포함된 전체 벤치마크: [BENCHMARKS.md](BENCHMARKS.md)

## 인프라 [Kansas City Shuffle]

4대 머신 — SSH 메시 — Mixer 스냅샷 — 제로 클라우드 [Kansas City Shuffle]

| 머신 | 역할 |
|---------|------|
| ryzen | 데스크톱 — 개발 |
| strix-halo | 128GB GPU — AI 추론 |
| minisforum | Windows 11 — 오피스 / 테스트 |
| sligar | 1080Ti — 음성 훈련 |

브라우저 > Caddy > Lemonade (통합 API) > 모든 서비스:

| 서비스 | 기능 |
|---------|-------------|
| llama.cpp | LLM 추론 |
| whisper.cpp | 음성-텍스트 변환 |
| Kokoro | 텍스트-음성 변환 |
| ComfyUI | 이미지 생성 |
| Open WebUI | 채팅 + RAG |
| Vane | 심층 연구 |
| n8n | 워크플로우 자동화 |
| Gaia | 17개 에이전트, 78개 도구 |
| Man Cave | 제어 센터 |

전체 아키텍처 상세: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 문서

| 가이드 | 내용 |
|-------|----------------|
| [아키텍처](docs/ARCHITECTURE.md) | 시스템 설계, 데이터 흐름, GPU 백엔드 |
| [서비스](docs/SERVICES.md) | 포트, 설정, 헬스 체크 |
| [보안](docs/SECURITY.md) | 방화벽, SSH, TLS, 비밀번호 순환 |
| [스택 보호](docs/STACK-PROTECTION.md) | Arch 업데이트가 스택을 망가뜨리지 않는 이유 |
| [벤치마크](BENCHMARKS.md) | 전체 성능 데이터 |
| [블루프린트](docs/BLUEPRINTS.md) | 로드맵 및 계획된 기능 |
| [자율 파이프라인](docs/AUTONOMOUS-PIPELINE.md) | 제로 휴먼 게임, 음악, 영상 제작 파이프라인 |
| [문제 해결](docs/TROUBLESHOOTING.md) | 일반적인 문제와 해결책 |
| [VPN 접속](docs/VPN.md) | WireGuard 설정 |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | 링 버스, ClusterFS, 자동 복구, 메시 관리 |
| [Mixer](https://github.com/stampby/mixer) | SSH 메시 스냅샷 — 분산 백업, 단일 장애점 없음 [Kansas City Shuffle] |
| [변경 이력](CHANGELOG.md) | 버전 이력 |

## [스크린샷](docs/SCREENSHOTS.md)

## 튜토리얼

영상 안내 — 처음부터 끝까지, 생략 없음. 비공개 YouTube 링크.

| # | 영상 | 상태 |
|---|-------|--------|
| 1 | 비전 — halo-ai가 무엇이고 왜 만들었는가 | 준비 중 |
| 2 | 하드웨어 설정 — 메시 배선, 4대 머신 | 준비 중 |
| 3 | Arch Linux 설치 — 기본 OS, btrfs, 첫 부팅 | 준비 중 |
| 4 | 설치 스크립트 — 소스에서 컴파일된 13개 서비스 | 준비 중 |
| 5 | 보안 — nftables, SSH, Caddy, 전면 차단 모델 | 준비 중 |
| 6 | Lemonade + llama.cpp — 통합 API, 87 tok/s | 준비 중 |
| 7 | 채팅 + RAG — Open WebUI, 문서 업로드, 벡터 검색 | 준비 중 |
| 8 | 심층 연구 — Vane, 출처 인용, 비공개 검색 | 준비 중 |
| 9 | 이미지 생성 — 115GB GPU의 ComfyUI | 준비 중 |
| 10 | 음성 — whisper.cpp, Kokoro TTS, 54개 음성 | 준비 중 |
| 11 | 워크플로우 — n8n 자동화, GitHub 웹훅 | 준비 중 |
| 12 | 에이전트 — Gaia UI, 17개 전체 에이전트, 관리 | 준비 중 |
| 13 | Man Cave — 제어 센터, 스택 보호, 동결/해동 | 준비 중 |
| 14 | 메시 — SSH 키, 4대 머신, Mixer, Shadow | 준비 중 |
| 15 | 메시 속의 Windows — Minisforum, VSS, Terminal | 준비 중 |
| 16 | Discord 봇 — Echo, Bounty, Meek, Amp | 준비 중 |
| 17 | Reddit 브릿지 — 스캔, 초안, 승인, 게시 | 준비 중 |
| 18 | 오디오 체인 — SM7B, Scarlett, PipeWire, 라우팅 | 준비 중 |
| 19 | 음성 복제 — 녹음, XTTS v2, 훈련 | 준비 중 |
| 20 | The Downcomers — 첫 트랙, 보컬 더빙, DistroKid | 준비 중 |
| 21 | 게임 — Undercroft, 안티 치트, Dealer AI | 준비 중 |
| 22 | 벤치마크 — llama-bench, GitHub Pages, 이력 | 준비 중 |
| 23 | CI/CD — GitHub Actions, 릴리스, 패키징 | 준비 중 |
| 24 | 전체 자율 데모 — 태그 → 에이전트 → Reddit 게시 | 준비 중 |

*99%의 사용자는 Claude가 없습니다. 이 튜토리얼은 Claude 없이도 경험을 수월하게 만들어줍니다. "우리가 가는 곳에는 도로가 필요 없다."*

## 크레딧

**아키텍트가 설계하고 구축했습니다** — 모든 스크립트, 모든 서비스, 모든 에이전트. 소스부터. 지름길 없음. *"나는 필연이다."*

[DreamServer](https://github.com/Light-Heart-Labs/DreamServer) by Light-Heart-Labs 기반으로 구축. [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock)으로 구동.

커뮤니티: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup), 그리고 Framework/Arch Linux 커뮤니티.

## 라이선스

Apache 2.0
