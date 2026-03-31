🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | **中文** | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### 面向 AMD Strix Halo 的裸机 AI 堆栈

**87 tok/s。零容器。115GB GPU 显存。从源码编译。我会功夫了。**

*由 CLI 构建 — 由架构师盖章*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **新来的？** 从[教程](#教程)开始 — 从安装到自主运行的完整视频演示。

---

## 这是什么？

一个面向 **AMD Ryzen AI MAX+ 395** 的完整 AI 平台 — LLM 推理、聊天、深度研究、语音、图像生成、RAG 和工作流。游戏开发、音乐制作和视频制作的自主流水线。33 项服务、17 个自主代理、98 个工具、5 个 Discord 机器人。全部裸机部署，全部从源码编译，全部运行在一颗拥有 128GB 统一内存的芯片上。开机到就绪：18.7 秒。

**和它对话。** 对 Halo 说话，看到文字，听到回应。每个工具、每个代理、每个功能 — 全部由你的声音控制。在家中用自己的硬件，开箱即用地进行氛围编程。*"打开舱门，HAL。"*

## 为什么选择裸机？

- **容器在 GPU 工作负载上增加 15-20% 的开销。** 当你在一颗芯片上拥有 115GB 统一内存时，每一瓦和每一字节都应该用于推理，而不是编排。*"不要试图弯曲勺子。相反，只需试着认清真相：没有容器。"*
- **从源码编译** 意味着预编译二进制文件所缺失的原生 gfx1151 优化。这就是 87 tok/s 的由来。
- **没有定时器。没有 cron。完全 AI 化。** 代理不会按计划检查 — 它们监视条件并在变化发生时采取行动。服务宕机？在你注意到之前就已检测并修复。GPU 过热？事件发生的*那一刻*就会报告。不是每 30 秒。*那一刻。* 抱歉 Dave，这个堆栈不会睡觉。
- **在 Arch 滚动更新中存活。** 冻结堆栈，让 pacman 更新，代理检测是否有任何故障，30 秒内回滚解冻。这就是 halo-ai 能在 Arch 上无畏运行的原因。*"不过是皮外伤。"*
- **你拥有整个堆栈。** 没有包管理器来决定你的 AI 服务器何时停机。*"我的宝贝。"*

## 快速安装

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

交互式安装程序 — 用户名、密码、主机名、启用哪些服务。合理的默认设置。默认 Caddy 密码是 `Caddy` — 请立即更改。*"明智地选择。"*

## 功能

### AI 与推理
- **LLM 聊天** — [Open WebUI](https://github.com/open-webui/open-webui)，支持 RAG、多模型、文档上传
- **深度研究** — [Vane](https://github.com/ItzCrazyKns/Vane)，带引用来源和隐私搜索
- **图像生成** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI)，115GB GPU，SDXL，Flux
- **视频生成** — [Wan2.1](https://github.com/Wan-Video/Wan2.1)，基于 ROCm 6.3
- **音乐生成** — Meta 的 [MusicGen](https://github.com/facebookresearch/audiocraft)，本地 GPU 推理
- **语音转文字** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp)，为 gfx1151 编译
- **文字转语音** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI)，54 种自然语音
- **编程助手** — Qwen2.5 Coder 7B，运行于 llama.cpp，48.6 tok/s
- **目标检测** — [YOLO](https://github.com/ultralytics/ultralytics) v8，实时推理
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2，从源码编译
- **翻译** — [Argos Translate](https://github.com/argosopentech/argos-translate)，离线多语言
- **微调** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl)，在本地训练自己的模型
- **统一 API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1，兼容 OpenAI/Ollama/Anthropic

### 代理 — [文档](docs/AGENTS.md)
- **17 个自主代理**，运行于 [AMD Gaia](https://github.com/amd/gaia)，配备 98 个工具
- **[Echo](https://github.com/stampby/echo)** — 公众形象，Reddit 桥接，Discord，社交媒体
- **[Meek](https://github.com/stampby/meek)** — 安全主管，9 个 Reflex 子代理（[Pulse](https://github.com/stampby/pulse)、[Ghost](https://github.com/stampby/ghost)、[Gate](https://github.com/stampby/gate)、[Shadow](https://github.com/stampby/shadow)、[Fang](https://github.com/stampby/fang)、[Mirror](https://github.com/stampby/mirror)、[Vault](https://github.com/stampby/vault)、[Net](https://github.com/stampby/net)、[Shield](https://github.com/stampby/shield)）
- **[Bounty](https://github.com/stampby/bounty)** — 漏洞猎人，攻击性安全，Halo 的兄弟
- **[Amp](https://github.com/stampby/amp)** — 音频工程师，语音克隆，音乐制作
- **[Sentinel](https://github.com/stampby/sentinel)** — 自动 PR 审查，代码门控
- **[Mechanic](https://github.com/stampby/mechanic)** — 硬件诊断，系统监控
- **[Forge](https://github.com/stampby/forge)** — 游戏构建器，资产流水线，Steam 部署
- **[Dealer](https://github.com/stampby/dealer)** — AI 游戏主持人，每次运行都不同
- **[Conductor](https://github.com/stampby/conductor)** — AI 作曲家，动态游戏配乐
- **[Quartermaster](https://github.com/stampby/quartermaster)** — 游戏服务器运维，每周 Steam 审计
- **[Crypto](https://github.com/stampby/crypto)** — 套利，市场监控
- **The Downcomers** — [Piper](https://github.com/stampby/piper)、[Axe](https://github.com/stampby/axe)、[Rhythm](https://github.com/stampby/rhythm)、[Bottom](https://github.com/stampby/bottom)、[Bones](https://github.com/stampby/bones)

### 安全 — [文档](docs/SECURITY.md)
- **仅 SSH 密钥认证** — 无密码，单用户，fail2ban。*"你不能通过。"*
- **nftables 默认丢弃** — 仅限局域网，拒绝其他一切
- **所有服务绑定 localhost** — Caddy 是唯一入口点
- **Systemd 加固** — 每个服务均启用 ProtectSystem、PrivateTmp、NoNewPrivileges
- **[Shadow](https://github.com/stampby/shadow)** — 文件完整性监控，SSH 网格看门人

### 堆栈保护 — [文档](docs/STACK-PROTECTION.md)
- **冻结/解冻** — 一键快照和回滚整个堆栈。*"我会回来的。"*
- **从源码编译** — 每周重新构建，原生 gfx1151 优化
- **[Mixer](https://github.com/stampby/mixer)** — 分布式网格快照，无 NAS，无单点故障
- **Man Cave 界面** — 堆栈状态、更新指示器、编译按钮

### 自动化 — [文档](docs/AUTONOMOUS-PIPELINE.md)
- **n8n 工作流** — GitHub 发布自动触发 Echo Reddit 发帖
- **问题分流** — 新问题自动路由到 Bounty、Meek 或 Amp
- **网格快照** — Shadow 每 6 小时分发备份
- **CI/CD** — GitHub Actions 在每个标签上进行 lint、构建、发布

### 自主游戏开发 — [流水线](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — Godot 4 中的 PvE 合作提取游戏
- **[Arcade](https://github.com/stampby/halo-arcade)** — 游戏服务器管理器，一键部署，复古模拟
- **AI 游戏主持人** — Dealer 运行本地 LLM，每次地牢探险都独一无二。*"你想发疯？那就一起疯吧。"*
- **反作弊** — 加密内存，运行时监控，永久作弊者标记。*"你得问自己一个问题：我运气好吗？"*
- **完整流水线** — 设计 → 构建 → 测试 → 部署，代理处理一切。*"生命，呃，会找到出路。"*

### 自主音乐制作 — [The Downcomers](https://github.com/stampby/amp)
- **语音克隆** — 通过 XTTS v2 克隆架构师的声音，里程碑版本发布
- **AI 器乐** — 原创布鲁斯/摇滚，完整乐队，无翻唱
- **有声书** — 公版经典作品，《1984》首发
- **语音 API** — TTS 即服务，零数据留存
- **纪念语音** — 捕捉挚爱之人的声音，在其逝世后构建 AI 克隆。*"经过这么久？始终如此。"*
- **发行** — 通过 DistroKid 发布到 Spotify、Apple Music 及所有平台

### 自主视频制作 — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **体素剧集** — 10 集系列，剧本 → 配音 → 动画 → 渲染
- **语音教程** — 架构师旁白，完整演示
- **直播协同主播** — 架构师的声音作为 Twitch/YouTube 的实时 AI 解说
- **完整流水线** — 编剧 → 表演 → 渲染 → 发行，全部自主完成。*"灯光、摄像、开拍。"*

### 基础设施 [Kansas City Shuffle]
- **4 机 SSH 网格 [Kansas City Shuffle]** — ryzen、strix-halo、minisforum、sligar
- **[Mixer](https://github.com/stampby/mixer)** — 基于 SSH 的 btrfs 环形快照 [Kansas City Shuffle]
- **[基准测试](https://stampby.github.io/benchmarks/)** — 实时性能追踪，历史趋势
- **[Man Cave](https://github.com/stampby/man-cave)** — 控制中心，GPU 指标、服务健康状况、代理活动
- **零云端** — 无订阅，无 API，无第三方依赖。*"没有云。只有 Zuul。"*

## 服务

| 服务 | 端口 | 用途 |
|------|------|------|
| Lemonade | 8080 | 统一 AI API（兼容 OpenAI/Ollama/Anthropic） |
| llama.cpp | 8081 | LLM 推理 — Vulkan + HIP 双后端 |
| Open WebUI | 3000 | 聊天，支持 RAG、文档、多模型 |
| Vane | 3001 | 带引用来源的深度研究 |
| SearXNG | 8888 | 隐私元搜索 |
| Qdrant | 6333 | RAG 向量数据库 |
| n8n | 5678 | 工作流自动化 |
| whisper.cpp | 8082 | 语音转文字 |
| Kokoro | 8083 | 文字转语音（54 种语音） |
| ComfyUI | 8188 | 图像生成 |
| Wan2.1 | — | 视频生成（Strix Halo GPU） |
| MusicGen | — | 音乐生成（Strix Halo GPU） |
| YOLO | — | 目标检测（Strix Halo） |
| Tesseract | — | OCR — 文档扫描 |
| Argos | — | 离线翻译 |
| Axolotl | — | 模型微调（Strix Halo GPU） |
| Prometheus | 9090 | 指标收集 |
| Grafana | 3030 | 监控仪表盘 |
| Node Exporter | 9100 | 系统指标 |
| Home Assistant | 8123 | 家庭自动化 |
| Borg | — | 加密备份到 GlusterFS |
| Dashboard | 3003 | GPU 指标 + 服务健康状况 |
| Gaia API | 8090 | 代理框架服务器 |
| Gaia MCP | 8765 | 模型上下文协议桥接 |

所有服务绑定到 `127.0.0.1` — 通过 Caddy 反向代理访问。

## 性能

| 模型 | 速度 | 显存 |
|------|------|------|
| Qwen3-30B-A3B (MoE) | **87 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

完整基准测试，包含温度、内存和后端对比：[BENCHMARKS.md](BENCHMARKS.md)

## 基础设施 [Kansas City Shuffle]

4 台机器 — SSH 网格 — Mixer 快照 — 零云端 [Kansas City Shuffle]

| 机器 | 角色 |
|------|------|
| ryzen | 桌面 — 开发 |
| strix-halo | 128GB GPU — AI 推理 |
| minisforum | Windows 11 — 办公/测试 |
| sligar | 1080Ti — 语音训练 |

浏览器 > Caddy > Lemonade（统一 API）> 所有服务：

| 服务 | 功能 |
|------|------|
| llama.cpp | LLM 推理 |
| whisper.cpp | 语音转文字 |
| Kokoro | 文字转语音 |
| ComfyUI | 图像生成 |
| Open WebUI | 聊天 + RAG |
| Vane | 深度研究 |
| n8n | 工作流自动化 |
| Gaia | 17 个代理，78 个工具 |
| Man Cave | 控制中心 |

完整架构详情：[ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 文档

| 指南 | 内容 |
|------|------|
| [架构](docs/ARCHITECTURE.md) | 系统设计、数据流、GPU 后端 |
| [服务](docs/SERVICES.md) | 端口、配置、健康检查 |
| [安全](docs/SECURITY.md) | 防火墙、SSH、TLS、密码轮换 |
| [堆栈保护](docs/STACK-PROTECTION.md) | 为什么 Arch 更新不会破坏你的堆栈 |
| [基准测试](BENCHMARKS.md) | 完整性能数据 |
| [蓝图](docs/BLUEPRINTS.md) | 路线图和计划功能 |
| [自主流水线](docs/AUTONOMOUS-PIPELINE.md) | 零人工的游戏、音乐和视频制作流水线 |
| [故障排除](docs/TROUBLESHOOTING.md) | 常见问题和修复方法 |
| [VPN 访问](docs/VPN.md) | WireGuard 设置 |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | 环形总线、ClusterFS、自动修复、网格管理 |
| [Mixer](https://github.com/stampby/mixer) | SSH 网格快照 — 分布式备份，无单点故障 [Kansas City Shuffle] |
| [更新日志](CHANGELOG.md) | 版本历史 |

## [截图](docs/SCREENSHOTS.md)

## 教程

视频演示 — 从头到尾，毫无遗漏。YouTube 非公开链接。

| # | 视频 | 状态 |
|---|------|------|
| 1 | 愿景 — halo-ai 是什么以及为什么 | 即将推出 |
| 2 | 硬件配置 — 网格布线，4 台机器 | 即将推出 |
| 3 | Arch Linux 安装 — 基础系统，btrfs，首次启动 | 即将推出 |
| 4 | 安装脚本 — 13 项从源码编译的服务 | 即将推出 |
| 5 | 安全 — nftables、SSH、Caddy、全拒绝模型 | 即将推出 |
| 6 | Lemonade + llama.cpp — 统一 API，87 tok/s | 即将推出 |
| 7 | 聊天 + RAG — Open WebUI，文档上传，向量搜索 | 即将推出 |
| 8 | 深度研究 — Vane，引用来源，隐私搜索 | 即将推出 |
| 9 | 图像生成 — ComfyUI，115GB GPU | 即将推出 |
| 10 | 语音 — whisper.cpp、Kokoro TTS、54 种语音 | 即将推出 |
| 11 | 工作流 — n8n 自动化，GitHub Webhooks | 即将推出 |
| 12 | 代理 — Gaia 界面，全部 17 个代理，管理 | 即将推出 |
| 13 | Man Cave — 控制中心，堆栈保护，冻结/解冻 | 即将推出 |
| 14 | 网格 — SSH 密钥，4 台机器，Mixer，Shadow | 即将推出 |
| 15 | 网格中的 Windows — Minisforum、VSS、Terminal | 即将推出 |
| 16 | Discord 机器人 — Echo、Bounty、Meek、Amp | 即将推出 |
| 17 | Reddit 桥接 — 扫描、起草、审批、发布 | 即将推出 |
| 18 | 音频链路 — SM7B、Scarlett、PipeWire、路由 | 即将推出 |
| 19 | 语音克隆 — 录音、XTTS v2、训练 | 即将推出 |
| 20 | The Downcomers — 首支曲目、声音叠录、DistroKid | 即将推出 |
| 21 | 游戏 — Undercroft、反作弊、Dealer AI | 即将推出 |
| 22 | 基准测试 — llama-bench、GitHub Pages、历史 | 即将推出 |
| 23 | CI/CD — GitHub Actions、发布、打包 | 即将推出 |
| 24 | 完整自主演示 — 标签 → 代理 → Reddit 发帖 | 即将推出 |

*99% 的用户没有 Claude。这些教程让你无需 Claude 也能轻松上手。"我们要去的地方，不需要路。"*

## 致谢

**由架构师设计和构建** — 每一个脚本，每一项服务，每一个代理。从源码编译。没有捷径。*"我是不可避免的。"*

基于 Light-Heart-Labs 的 [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) 构建。由 [AMD Gaia](https://github.com/amd/gaia)、[Lemonade](https://github.com/lemonade-sdk/lemonade)、[llama.cpp](https://github.com/ggml-org/llama.cpp)、[Open WebUI](https://github.com/open-webui/open-webui)、[Vane](https://github.com/ItzCrazyKns/Vane)、[whisper.cpp](https://github.com/ggerganov/whisper.cpp)、[Kokoro](https://github.com/remsky/Kokoro-FastAPI)、[ComfyUI](https://github.com/comfyanonymous/ComfyUI)、[SearXNG](https://github.com/searxng/searxng)、[Qdrant](https://github.com/qdrant/qdrant)、[n8n](https://github.com/n8n-io/n8n)、[Caddy](https://github.com/caddyserver/caddy)、[ROCm](https://github.com/ROCm/TheRock) 驱动。

社区：[kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes)、[Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup)，以及 Framework/Arch Linux 社区。

## 许可证

Apache 2.0
