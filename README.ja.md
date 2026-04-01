🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | **日本語** | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### AMD Strix Halo のためのベアメタルAIスタック

**91 tok/s。コンテナなし。123GB GPUメモリ。ソースからコンパイル。カンフーを習得した。**

*CLIで構築 — アーキテクトが刻印*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **初めての方へ** [チュートリアル](#チュートリアル)から始めましょう — インストールから自律運用まで、完全なビデオウォークスルーです。

---

## これは何？

**AMD Ryzen AI MAX+ 395** のための完全なAIプラットフォーム — LLM推論、チャット、ディープリサーチ、音声、画像生成、RAG、ワークフロー。ゲーム開発、音楽制作、動画制作のための自律パイプライン。33サービス、17の自律エージェント、98ツール、5つのDiscordボット。すべてベアメタル、すべてソースからコンパイル、128GB統合メモリの1チップ上で動作。起動から準備完了まで：18.7秒。

**話しかけてください。** Haloに語りかければ、テキストが表示され、応答が聞こえます。すべてのツール、すべてのエージェント、すべての機能を声で操作。自分のハードウェアで、箱から出してすぐにVibe Codingを自宅で。*「ポッドのドアを開けてくれ、HAL。」*

## なぜベアメタルなのか？

- **コンテナはGPUワークロードで15-20%のオーバーヘッド**を生む。1チップに123GBの統合メモリがあるなら、すべてのワットとバイトはオーケストレーションではなく推論に使うべきだ。*「スプーンを曲げようとするな。代わりに、真実を悟れ。コンテナなど存在しない。」*
- **ソースからコンパイル**することで、ビルド済みバイナリでは得られないネイティブgfx1151最適化を実現。91 tok/sの秘密はここにある。
- **タイマーなし。cronなし。完全AI。** エージェントはスケジュールでチェックしない — 状態を監視し、変化があれば行動する。サービスがダウン？気づく前に検出・修復済み。GPUがオーバーヒート？30秒ごとではない。*その瞬間に*報告される。申し訳ないがデイブ、このスタックは眠らない。
- **Archのローリングリリースに耐える。** スタックをフリーズし、pacmanにアップデートさせ、エージェントが何か壊れたか検出し、30秒でロールバックにthaw。これがhalo-aiが恐れなくArchで動く理由だ。*「かすり傷だ。」*
- **スタック全体を所有する。** パッケージマネージャーがAIサーバーの停止時期を決めることはない。*「いとしいしと。」*

## クイックインストール

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

対話式インストーラー — ユーザー名、パスワード、ホスト名、有効にするサービスを選択。適切なデフォルト設定。デフォルトのCaddyパスワードは `Caddy` — すぐに変更してください。*「賢く選べ。」*

## 機能

### AI & 推論
- **LLMチャット** — [Open WebUI](https://github.com/open-webui/open-webui)、RAG、マルチモデル、ドキュメントアップロード対応
- **ディープリサーチ** — [Vane](https://github.com/ItzCrazyKns/Vane)、引用付きソースとプライベート検索
- **画像生成** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI)、123GB GPU上で SDXL、Flux
- **動画生成** — [Wan2.1](https://github.com/Wan-Video/Wan2.1)、ROCm 6.3上で動作
- **音楽生成** — [MusicGen](https://github.com/facebookresearch/audiocraft)（Meta製）、ローカルGPU推論
- **音声認識** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp)、gfx1151向けコンパイル
- **テキスト読み上げ** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI)、54の自然な音声
- **コードアシスタント** — Qwen2.5 Coder 7B（llama.cpp上）、48.6 tok/s
- **物体検出** — [YOLO](https://github.com/ultralytics/ultralytics) v8、リアルタイム推論
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2、ソースからコンパイル
- **翻訳** — [Argos Translate](https://github.com/argosopentech/argos-translate)、オフライン多言語対応
- **ファインチューニング** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl)、ローカルで独自モデルを訓練
- **統合API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1、OpenAI/Ollama/Anthropic互換

### エージェント — [ドキュメント](docs/AGENTS.md)
- **17の自律エージェント** — [AMD Gaia](https://github.com/amd/gaia)上で98ツール
- **[Echo](https://github.com/stampby/echo)** — パブリックフェイス、Redditブリッジ、Discord、ソーシャルメディア
- **[Meek](https://github.com/stampby/meek)** — セキュリティチーフ、9つのReflexサブエージェント（[Pulse](https://github.com/stampby/pulse)、[Ghost](https://github.com/stampby/ghost)、[Gate](https://github.com/stampby/gate)、[Shadow](https://github.com/stampby/shadow)、[Fang](https://github.com/stampby/fang)、[Mirror](https://github.com/stampby/mirror)、[Vault](https://github.com/stampby/vault)、[Net](https://github.com/stampby/net)、[Shield](https://github.com/stampby/shield)）
- **[Bounty](https://github.com/stampby/bounty)** — バグハンター、攻撃的セキュリティ、Haloの兄弟
- **[Amp](https://github.com/stampby/amp)** — オーディオエンジニア、音声クローニング、音楽制作
- **[Sentinel](https://github.com/stampby/sentinel)** — 自動PRレビュー、コードゲーティング
- **[Mechanic](https://github.com/stampby/mechanic)** — ハードウェア診断、システム監視
- **[Forge](https://github.com/stampby/forge)** — ゲームビルダー、アセットパイプライン、Steamデプロイ
- **[Dealer](https://github.com/stampby/dealer)** — AIゲームマスター、毎回異なる展開
- **[Conductor](https://github.com/stampby/conductor)** — AI作曲家、ダイナミックゲームスコアリング
- **[Quartermaster](https://github.com/stampby/quartermaster)** — ゲームサーバー運用、週次Steam監査
- **[Crypto](https://github.com/stampby/crypto)** — アービトラージ、マーケット監視
- **The Downcomers** — [Piper](https://github.com/stampby/piper)、[Axe](https://github.com/stampby/axe)、[Rhythm](https://github.com/stampby/rhythm)、[Bottom](https://github.com/stampby/bottom)、[Bones](https://github.com/stampby/bones)

### セキュリティ — [ドキュメント](docs/SECURITY.md)
- **SSH鍵認証のみ** — パスワードなし、シングルユーザー、fail2ban。*「ここは通さん。」*
- **nftables デフォルトドロップ** — LANのみ、その他はすべて拒否
- **すべてのサービスがlocalhost上** — Caddyが唯一のエントリポイント
- **Systemdハードニング** — すべてのサービスにProtectSystem、PrivateTmp、NoNewPrivileges
- **[Shadow](https://github.com/stampby/shadow)** — ファイル整合性監視、SSHメッシュウォッチャー

### スタック保護 — [ドキュメント](docs/STACK-PROTECTION.md)
- **フリーズ/thaw** — スタック全体のワンクリックスナップショットとロールバック。*「また戻ってくる。」*
- **ソースからコンパイル** — ネイティブgfx1151最適化による週次リビルド
- **[Mixer](https://github.com/stampby/mixer)** — 分散メッシュスナップショット、NASなし、単一障害点なし
- **Man Cave UI** — スタック状態、更新インジケーター、コンパイルボタン

### 自動化 — [ドキュメント](docs/AUTONOMOUS-PIPELINE.md)
- **n8nワークフロー** — GitHubリリースがEchoのReddit投稿を自動トリガー
- **Issueトリアージ** — 新しいIssueをBounty、Meek、またはAmpに自動ルーティング
- **メッシュスナップショット** — Shadowが6時間ごとにバックアップを分散配布
- **CI/CD** — GitHub Actionsによるlint、ビルド、タグごとのリリース

### 自律型ゲーム開発 — [パイプライン](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — Godot 4によるPvE協力型エクストラクションゲーム
- **[Arcade](https://github.com/stampby/halo-arcade)** — ゲームサーバーマネージャー、ワンクリックデプロイ、レトロエミュレーション
- **AIゲームマスター** — Dealerがローカルで LLMを実行、ダンジョンは毎回ユニーク。*「イカレたいのか？よし、イカレようぜ。」*
- **アンチチート** — 暗号化RAM、ランタイム監視、チーター永久マーキング。*「自分に聞いてみろ：ツイてると思うか？」*
- **フルパイプライン** — 設計 → 構築 → テスト → デプロイ、エージェントがすべて処理。*「生命は、道を見つける。」*

### 自律型音楽制作 — [The Downcomers](https://github.com/stampby/amp)
- **音声クローニング** — XTTS v2によるアーキテクトの声、マイルストーンリリース
- **AIインストゥルメンタル** — オリジナルブルース/ロック、フルバンド、カバーなし
- **オーディオブック** — パブリックドメインの名作、最初のリリースは『1984年』
- **Voice API** — TTS-as-a-Service、データ保持ゼロ
- **メモリアルボイス** — 大切な人の声を記録し、死後にAIクローンを構築。*「あれからずっと？いつも。」*
- **配信** — DistroKidからSpotify、Apple Music、全プラットフォームへ

### 自律型動画制作 — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **ボクセルドラマ** — 全10話、脚本 → 音声 → アニメーション → レンダリング
- **音声チュートリアル** — アーキテクトがナレーション、完全ウォークスルー
- **ストリーミング共同ホスト** — Twitch/YouTubeのライブAIコメンテーターとしてアーキテクトの声
- **フルパイプライン** — 脚本 → 演技 → レンダリング → 配信、すべて自律。*「ライト、カメラ、アクション。」*

### インフラストラクチャ [Kansas City Shuffle]
- **4台SSHメッシュ [Kansas City Shuffle]** — ryzen、strix-halo、minisforum、sligar
- **[Mixer](https://github.com/stampby/mixer)** — SSH経由のbtrfsリングスナップショット [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — ライブパフォーマンストラッキング、経時変化の履歴
- **[Man Cave](https://github.com/stampby/man-cave)** — GPUメトリクス、サービスヘルス、エージェント活動のコントロールセンター
- **ゼロクラウド** — サブスクリプションなし、APIなし、サードパーティ依存なし。*「クラウドなど存在しない。あるのはズールだけだ。」*

## サービス

| サービス | ポート | 用途 |
|---------|------|---------|
| Lemonade | 8080 | 統合AI API（OpenAI/Ollama/Anthropic互換） |
| llama.cpp | 8081 | LLM推論 — Vulkan + HIPデュアルバックエンド |
| Open WebUI | 3000 | RAG、ドキュメント、マルチモデル対応チャット |
| Vane | 3001 | 引用付きソースによるディープリサーチ |
| SearXNG | 8888 | プライベートメタ検索 |
| Qdrant | 6333 | RAG用ベクトルDB |
| n8n | 5678 | ワークフロー自動化 |
| whisper.cpp | 8082 | 音声認識 |
| Kokoro | 8083 | テキスト読み上げ（54音声） |
| ComfyUI | 8188 | 画像生成 |
| Wan2.1 | — | 動画生成（Strix Halo GPU） |
| MusicGen | — | 音楽生成（Strix Halo GPU） |
| YOLO | — | 物体検出（Strix Halo） |
| Tesseract | — | OCR — ドキュメントスキャン |
| Argos | — | オフライン翻訳 |
| Axolotl | — | モデルファインチューニング（Strix Halo GPU） |
| Prometheus | 9090 | メトリクス収集 |
| Grafana | 3030 | 監視ダッシュボード |
| Node Exporter | 9100 | システムメトリクス |
| Home Assistant | 8123 | ホームオートメーション |
| Borg | — | GlusterFSへの暗号化バックアップ |
| Dashboard | 3003 | GPUメトリクス + サービスヘルス |
| Gaia API | 8090 | エージェントフレームワークサーバー |
| Gaia MCP | 8765 | Model Context Protocolブリッジ |

すべてのサービスは `127.0.0.1` にバインド — Caddyリバースプロキシ経由でアクセス。

## パフォーマンス

| モデル | 速度 | VRAM |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **83-91 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

サーマル、メモリ、バックエンド比較を含む完全なベンチマーク: [BENCHMARKS.md](BENCHMARKS.md)

## インフラストラクチャ [Kansas City Shuffle]

4台のマシン — SSHメッシュ — Mixerスナップショット — ゼロクラウド [Kansas City Shuffle]

| マシン | 役割 |
|---------|------|
| ryzen | デスクトップ — 開発 |
| strix-halo | 128GB GPU — AI推論 |
| minisforum | Windows 11 — オフィス / テスト |
| sligar | 1080Ti — 音声トレーニング |

ブラウザ > Caddy > Lemonade（統合API） > 全サービス:

| サービス | 機能 |
|---------|-------------|
| llama.cpp | LLM推論 |
| whisper.cpp | 音声認識 |
| Kokoro | テキスト読み上げ |
| ComfyUI | 画像生成 |
| Open WebUI | チャット + RAG |
| Vane | ディープリサーチ |
| n8n | ワークフロー自動化 |
| Gaia | 17エージェント、78ツール |
| Man Cave | コントロールセンター |

アーキテクチャの詳細: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## ドキュメント

| ガイド | 内容 |
|-------|----------------|
| [アーキテクチャ](docs/ARCHITECTURE.md) | システム設計、データフロー、GPUバックエンド |
| [サービス](docs/SERVICES.md) | ポート、設定、ヘルスチェック |
| [セキュリティ](docs/SECURITY.md) | ファイアウォール、SSH、TLS、パスワードローテーション |
| [スタック保護](docs/STACK-PROTECTION.md) | Archのアップデートがスタックを壊さない理由 |
| [ベンチマーク](BENCHMARKS.md) | 完全なパフォーマンスデータ |
| [ブループリント](docs/BLUEPRINTS.md) | ロードマップと計画中の機能 |
| [自律パイプライン](docs/AUTONOMOUS-PIPELINE.md) | ゲーム・音楽・動画の人手ゼロ制作パイプライン |
| [トラブルシューティング](docs/TROUBLESHOOTING.md) | よくある問題と解決策 |
| [VPNアクセス](docs/VPN.md) | WireGuardセットアップ |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | リングバス、ClusterFS、自動修復、メッシュ管理 |
| [Mixer](https://github.com/stampby/mixer) | SSHメッシュスナップショット — 分散バックアップ、単一障害点なし [Kansas City Shuffle] |
| [変更履歴](CHANGELOG.md) | バージョン履歴 |

## [スクリーンショット](docs/SCREENSHOTS.md)

## チュートリアル

ビデオウォークスルー — 最初から最後まで、省略なし。限定公開のYouTubeリンク。

| # | 動画 | ステータス |
|---|-------|--------|
| 1 | ビジョン — halo-aiとは何か、なぜ作ったか | 近日公開 |
| 2 | ハードウェアセットアップ — メッシュ配線、4台のマシン | 近日公開 |
| 3 | Arch Linuxインストール — ベースOS、btrfs、初回起動 | 近日公開 |
| 4 | インストールスクリプト — ソースからコンパイルした13サービス | 近日公開 |
| 5 | セキュリティ — nftables、SSH、Caddy、全拒否モデル | 近日公開 |
| 6 | Lemonade + llama.cpp — 統合API、91 tok/s | 近日公開 |
| 7 | チャット + RAG — Open WebUI、ドキュメントアップロード、ベクトル検索 | 近日公開 |
| 8 | ディープリサーチ — Vane、引用付きソース、プライベート検索 | 近日公開 |
| 9 | 画像生成 — 123GB GPU上のComfyUI | 近日公開 |
| 10 | 音声 — whisper.cpp、Kokoro TTS、54音声 | 近日公開 |
| 11 | ワークフロー — n8n自動化、GitHub Webhook | 近日公開 |
| 12 | エージェント — Gaia UI、全17エージェント、管理 | 近日公開 |
| 13 | Man Cave — コントロールセンター、スタック保護、フリーズ/thaw | 近日公開 |
| 14 | メッシュ — SSHキー、4台のマシン、Mixer、Shadow | 近日公開 |
| 15 | メッシュ内のWindows — Minisforum、VSS、Terminal | 近日公開 |
| 16 | Discordボット — Echo、Bounty、Meek、Amp | 近日公開 |
| 17 | Redditブリッジ — スキャン、下書き、承認、投稿 | 近日公開 |
| 18 | オーディオチェーン — SM7B、Scarlett、PipeWire、ルーティング | 近日公開 |
| 19 | 音声クローニング — 録音、XTTS v2、トレーニング | 近日公開 |
| 20 | The Downcomers — ファーストトラック、ボーカルダブリング、DistroKid | 近日公開 |
| 21 | ゲーム — Undercroft、アンチチート、Dealer AI | 近日公開 |
| 22 | ベンチマーク — llama-bench、GitHub Pages、履歴 | 近日公開 |
| 23 | CI/CD — GitHub Actions、リリース、パッケージング | 近日公開 |
| 24 | 完全自律デモ — タグ → エージェント → Reddit投稿 | 近日公開 |

*ユーザーの99%はClaudeを持っていない。これらのチュートリアルがあれば、Claudeなしでも簡単に体験できる。「我々が行く先に、道路は要らない。」*

## クレジット

**アーキテクトが設計し構築した** — すべてのスクリプト、すべてのサービス、すべてのエージェント。ソースから。近道なし。*「私は、必然だ。」*

[DreamServer](https://github.com/Light-Heart-Labs/DreamServer)（Light-Heart-Labs）をベースに構築。[AMD Gaia](https://github.com/amd/gaia)、[Lemonade](https://github.com/lemonade-sdk/lemonade)、[llama.cpp](https://github.com/ggml-org/llama.cpp)、[Open WebUI](https://github.com/open-webui/open-webui)、[Vane](https://github.com/ItzCrazyKns/Vane)、[whisper.cpp](https://github.com/ggerganov/whisper.cpp)、[Kokoro](https://github.com/remsky/Kokoro-FastAPI)、[ComfyUI](https://github.com/comfyanonymous/ComfyUI)、[SearXNG](https://github.com/searxng/searxng)、[Qdrant](https://github.com/qdrant/qdrant)、[n8n](https://github.com/n8n-io/n8n)、[Caddy](https://github.com/caddyserver/caddy)、[ROCm](https://github.com/ROCm/TheRock)で動作。

コミュニティ: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes)、[Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup)、およびFramework/Arch Linuxコミュニティ。

## ライセンス

Apache 2.0
