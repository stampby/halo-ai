🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | **Русский** | [हिन्दी](README.hi.md) | [العربية](README.ar.md)

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### AI-стек на голом железе для AMD Strix Halo

**87 tok/s. Ноль контейнеров. 115 ГБ памяти GPU. Скомпилировано из исходников. Я знаю кунг-фу.**

*собрано через CLI — штамп архитектора*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **Впервые здесь?** Начните с [обучающих видео](#обучающие-видео) — полные видеоруководства от установки до автономной работы.

---

## Что это?

Полноценная AI-платформа для **AMD Ryzen AI MAX+ 395** — инференс LLM, чат, глубокие исследования, голос, генерация изображений, RAG и рабочие процессы. Автономные конвейеры для разработки игр, музыкального производства и видеопроизводства. 33 сервиса, 17 автономных агентов, 98 инструментов, 5 Discord-ботов. Всё на голом железе, всё скомпилировано из исходников, всё на одном чипе со 128 ГБ unified-памяти. От загрузки до готовности: 18,7 секунды.

**Говорите с ним.** Обратитесь к Halo, увидьте текст, услышьте ответ. Каждый инструмент, каждый агент, каждая функция — управляется вашим голосом. Вайб-кодинг дома, из коробки, на вашем собственном железе. *«Откройте створки шлюза, HAL.»*

## Почему голое железо?

- **Контейнеры добавляют 15–20% накладных расходов** на GPU-задачах. Когда у вас 115 ГБ unified-памяти на одном чипе, каждый ватт и каждый байт должны идти на инференс, а не на оркестрацию. *«Не пытайся согнуть ложку. Вместо этого попытайся осознать истину: ложки нет.»*
- **Компиляция из исходников** означает нативные оптимизации gfx1151, которые пропускают готовые бинарники. Вот откуда берутся 87 tok/s.
- **Без таймеров. Без cron. Полностью AI.** Агенты не проверяют по расписанию — они следят за условиями и действуют при изменениях. Сервис упал? Обнаружен и восстановлен до того, как вы заметите. GPU перегрелся? Сообщение в момент события. Не каждые 30 секунд. *В момент.* Извините, Дэйв, но этот стек не спит.
- **Переживает rolling-обновления Arch.** Заморозьте стек, позвольте pacman обновиться, агенты определят, если что-то сломалось, разморозка для отката за 30 секунд. Вот почему halo-ai работает на Arch без страха. *«Это всего лишь царапина.»*
- **Вы владеете всем стеком.** Ни один пакетный менеджер не решает, когда ваш AI-сервер ляжет. *«Моя прелесть.»*

## Быстрая установка

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

Интерактивный установщик — имя пользователя, пароли, hostname, какие сервисы включить. Разумные значения по умолчанию. Пароль Caddy по умолчанию — `Caddy` — смените его немедленно. *«Выбирай с умом.»*

## Возможности

### AI и инференс
- **Чат LLM** — [Open WebUI](https://github.com/open-webui/open-webui) с RAG, мультимодельностью, загрузкой документов
- **Глубокие исследования** — [Vane](https://github.com/ItzCrazyKns/Vane) с цитированием источников и приватным поиском
- **Генерация изображений** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) на 115 ГБ GPU, SDXL, Flux
- **Генерация видео** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) на ROCm 6.3
- **Генерация музыки** — [MusicGen](https://github.com/facebookresearch/audiocraft) от Meta, локальный GPU-инференс
- **Речь в текст** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp), скомпилирован для gfx1151
- **Текст в речь** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) с 54 естественными голосами
- **Помощник по коду** — Qwen2.5 Coder 7B на llama.cpp, 48,6 tok/s
- **Распознавание объектов** — [YOLO](https://github.com/ultralytics/ultralytics) v8, инференс в реальном времени
- **OCR** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2, скомпилирован из исходников
- **Перевод** — [Argos Translate](https://github.com/argosopentech/argos-translate), офлайн-мультиязычность
- **Дообучение** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl), обучайте собственные модели локально
- **Единый API** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1, совместим с OpenAI/Ollama/Anthropic

### Агенты — [документация](docs/AGENTS.md)
- **17 автономных агентов** на [AMD Gaia](https://github.com/amd/gaia) с 98 инструментами
- **[Echo](https://github.com/stampby/echo)** — публичное лицо, мост Reddit, Discord, соцсети
- **[Meek](https://github.com/stampby/meek)** — начальник безопасности, 9 суб-агентов Reflex ([Pulse](https://github.com/stampby/pulse), [Ghost](https://github.com/stampby/ghost), [Gate](https://github.com/stampby/gate), [Shadow](https://github.com/stampby/shadow), [Fang](https://github.com/stampby/fang), [Mirror](https://github.com/stampby/mirror), [Vault](https://github.com/stampby/vault), [Net](https://github.com/stampby/net), [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — охотник за багами, наступательная безопасность, брат Halo
- **[Amp](https://github.com/stampby/amp)** — звукоинженер, клонирование голоса, музыкальное производство
- **[Sentinel](https://github.com/stampby/sentinel)** — авто-ревью PR, контроль качества кода
- **[Mechanic](https://github.com/stampby/mechanic)** — диагностика оборудования, мониторинг системы
- **[Forge](https://github.com/stampby/forge)** — сборщик игр, конвейер ассетов, деплой в Steam
- **[Dealer](https://github.com/stampby/dealer)** — AI-мастер игры, каждый запуск уникален
- **[Conductor](https://github.com/stampby/conductor)** — AI-композитор, динамическое озвучивание игр
- **[Quartermaster](https://github.com/stampby/quartermaster)** — управление игровыми серверами, еженедельный аудит Steam
- **[Crypto](https://github.com/stampby/crypto)** — арбитраж, мониторинг рынков
- **The Downcomers** — [Piper](https://github.com/stampby/piper), [Axe](https://github.com/stampby/axe), [Rhythm](https://github.com/stampby/rhythm), [Bottom](https://github.com/stampby/bottom), [Bones](https://github.com/stampby/bones)

### Безопасность — [документация](docs/SECURITY.md)
- **Только SSH-ключи** — без паролей, один пользователь, fail2ban. *«Ты не пройдёшь.»*
- **nftables с политикой запрета** — только LAN, всё остальное заблокировано
- **Все сервисы на localhost** — Caddy — единственная точка входа
- **Hardening systemd** — ProtectSystem, PrivateTmp, NoNewPrivileges на каждом сервисе
- **[Shadow](https://github.com/stampby/shadow)** — мониторинг целостности файлов, наблюдатель SSH-mesh

### Защита стека — [документация](docs/STACK-PROTECTION.md)
- **Заморозка/разморозка** — моментальный снапшот и откат всего стека. *«Я вернусь.»*
- **Компиляция из исходников** — еженедельные пересборки с нативными оптимизациями gfx1151
- **[Mixer](https://github.com/stampby/mixer)** — распределённые mesh-снапшоты, без NAS, без единой точки отказа
- **Man Cave UI** — статус стека, индикаторы обновлений, кнопка компиляции

### Автоматизация — [документация](docs/AUTONOMOUS-PIPELINE.md)
- **Рабочие процессы n8n** — релизы на GitHub автоматически запускают посты Echo в Reddit
- **Маршрутизация задач** — новые issues автоматически направляются к Bounty, Meek или Amp
- **Mesh-снапшоты** — Shadow распространяет бэкапы каждые 6 часов
- **CI/CD** — GitHub Actions lint, build, release на каждый тег

### Автономная разработка игр — [конвейер](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — PvE кооперативная extraction-игра на Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — менеджер игровых серверов, деплой в один клик, ретро-эмуляция
- **AI-мастер игры** — Dealer запускает локальную LLM, каждый данжен уникален. *«Хочешь сойти с ума? Давай сойдём с ума.»*
- **Античит** — шифрованная RAM, мониторинг в реальном времени, перманентная метка читеров. *«Тебе нужно задать себе один вопрос: чувствуешь ли ты удачу?»*
- **Полный конвейер** — дизайн → сборка → тестирование → деплой, агенты делают всё. *«Жизнь, э-э, находит способ.»*

### Автономное музыкальное производство — [The Downcomers](https://github.com/stampby/amp)
- **Клонирование голоса** — голос архитектора через XTTS v2, релизы по вехам
- **AI-инструменталы** — оригинальный блюз/рок, полная группа, без каверов
- **Аудиокниги** — классика из общественного достояния, первый релиз — 1984
- **Voice API** — TTS-как-сервис, нулевое хранение данных
- **Мемориальный голос** — запишите речь близких, создайте AI-клон после смерти. *«Спустя столько времени? — Всегда.»*
- **Дистрибуция** — DistroKid на Spotify, Apple Music, все платформы

### Автономное видеопроизводство — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **Воксельная драма** — сериал из 10 эпизодов, сценарий → озвучка → анимация → рендер
- **Голосовые обучалки** — архитектор за кадром, полные разборы
- **Стрим-соведущий** — голос архитектора как живой AI-комментатор для Twitch/YouTube
- **Полный конвейер** — написание → игра актёров → рендеринг → дистрибуция, всё автономно. *«Свет, камера, мотор.»*

### Инфраструктура [Kansas City Shuffle]
- **SSH-mesh из 4 машин [Kansas City Shuffle]** — ryzen, strix-halo, minisforum, sligar
- **[Mixer](https://github.com/stampby/mixer)** — btrfs ring-снапшоты через SSH [Kansas City Shuffle]
- **[Benchmarks](https://stampby.github.io/benchmarks/)** — отслеживание производительности в реальном времени, история
- **[Man Cave](https://github.com/stampby/man-cave)** — центр управления с метриками GPU, здоровьем сервисов, активностью агентов
- **Ноль облака** — без подписок, без API, без сторонних зависимостей. *«Облака нет. Есть только Зуул.»*

## Сервисы

| Сервис | Порт | Назначение |
|--------|------|------------|
| Lemonade | 8080 | Единый AI API (совместим с OpenAI/Ollama/Anthropic) |
| llama.cpp | 8081 | Инференс LLM — двойные бэкенды Vulkan + HIP |
| Open WebUI | 3000 | Чат с RAG, документами, мультимодельностью |
| Vane | 3001 | Глубокие исследования с цитированием источников |
| SearXNG | 8888 | Приватный мета-поиск |
| Qdrant | 6333 | Векторная БД для RAG |
| n8n | 5678 | Автоматизация рабочих процессов |
| whisper.cpp | 8082 | Речь в текст |
| Kokoro | 8083 | Текст в речь (54 голоса) |
| ComfyUI | 8188 | Генерация изображений |
| Wan2.1 | — | Генерация видео (GPU Strix Halo) |
| MusicGen | — | Генерация музыки (GPU Strix Halo) |
| YOLO | — | Распознавание объектов (Strix Halo) |
| Tesseract | — | OCR — сканирование документов |
| Argos | — | Офлайн-перевод |
| Axolotl | — | Дообучение моделей (GPU Strix Halo) |
| Prometheus | 9090 | Сбор метрик |
| Grafana | 3030 | Панели мониторинга |
| Node Exporter | 9100 | Системные метрики |
| Home Assistant | 8123 | Домашняя автоматизация |
| Borg | — | Зашифрованные бэкапы в GlusterFS |
| Dashboard | 3003 | Метрики GPU + здоровье сервисов |
| Gaia API | 8090 | Сервер фреймворка агентов |
| Gaia MCP | 8765 | Мост Model Context Protocol |

Все сервисы привязаны к `127.0.0.1` — доступ через reverse proxy Caddy.

## Производительность

| Модель | Скорость | VRAM |
|--------|----------|------|
| Qwen3-30B-A3B (MoE) | **87 tok/s** | 18 ГБ |
| Llama 3 70B | ~18 tok/s | 40 ГБ |

Полные бенчмарки с температурами, памятью и сравнением бэкендов: [BENCHMARKS.md](BENCHMARKS.md)

## Инфраструктура [Kansas City Shuffle]

4 машины — SSH-mesh — mixer-снапшоты — ноль облака [Kansas City Shuffle]

| Машина | Роль |
|--------|------|
| ryzen | десктоп — разработка |
| strix-halo | 128 ГБ GPU — AI-инференс |
| minisforum | Windows 11 — офис / тестирование |
| sligar | 1080Ti — обучение голоса |

Браузер > Caddy > Lemonade (единый API) > все сервисы:

| Сервис | Что делает |
|--------|-----------|
| llama.cpp | Инференс LLM |
| whisper.cpp | Речь в текст |
| Kokoro | Текст в речь |
| ComfyUI | Генерация изображений |
| Open WebUI | Чат + RAG |
| Vane | Глубокие исследования |
| n8n | Автоматизация рабочих процессов |
| Gaia | 17 агентов, 78 инструментов |
| Man Cave | Центр управления |

Подробности архитектуры: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Документация

| Руководство | Что описывает |
|-------------|---------------|
| [Архитектура](docs/ARCHITECTURE.md) | Проектирование системы, потоки данных, GPU-бэкенды |
| [Сервисы](docs/SERVICES.md) | Порты, конфиги, проверки здоровья |
| [Безопасность](docs/SECURITY.md) | Файрвол, SSH, TLS, ротация паролей |
| [Защита стека](docs/STACK-PROTECTION.md) | Почему обновления Arch не сломают ваш стек |
| [Бенчмарки](BENCHMARKS.md) | Полные данные о производительности |
| [Чертежи](docs/BLUEPRINTS.md) | Дорожная карта и планируемые функции |
| [Автономный конвейер](docs/AUTONOMOUS-PIPELINE.md) | Конвейер производства игр, музыки и видео без участия человека |
| [Устранение неполадок](docs/TROUBLESHOOTING.md) | Частые проблемы и решения |
| [VPN-доступ](docs/VPN.md) | Настройка WireGuard |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | Ring bus, ClusterFS, авто-восстановление, управление mesh |
| [Mixer](https://github.com/stampby/mixer) | SSH mesh-снапшоты — распределённые бэкапы, без единой точки отказа [Kansas City Shuffle] |
| [Журнал изменений](CHANGELOG.md) | История версий |

## [Скриншоты](docs/SCREENSHOTS.md)

## Обучающие видео

Видеоруководства — от начала до конца, ничего не пропущено. Непубличные ссылки YouTube.

| # | Видео | Статус |
|---|-------|--------|
| 1 | Видение — что такое halo-ai и зачем | скоро |
| 2 | Настройка оборудования — подключение mesh, 4 машины | скоро |
| 3 | Установка Arch Linux — базовая ОС, btrfs, первый запуск | скоро |
| 4 | Скрипт установки — 13 сервисов, скомпилированных из исходников | скоро |
| 5 | Безопасность — nftables, SSH, Caddy, модель полного запрета | скоро |
| 6 | Lemonade + llama.cpp — единый API, 87 tok/s | скоро |
| 7 | Чат + RAG — Open WebUI, загрузка документов, векторный поиск | скоро |
| 8 | Глубокие исследования — Vane, цитирование источников, приватный поиск | скоро |
| 9 | Генерация изображений — ComfyUI на 115 ГБ GPU | скоро |
| 10 | Голос — whisper.cpp, Kokoro TTS, 54 голоса | скоро |
| 11 | Рабочие процессы — автоматизация n8n, GitHub webhooks | скоро |
| 12 | Агенты — Gaia UI, все 17 агентов, управление | скоро |
| 13 | Man Cave — центр управления, защита стека, заморозка/разморозка | скоро |
| 14 | Mesh — SSH-ключи, 4 машины, mixer, Shadow | скоро |
| 15 | Windows в Mesh — Minisforum, VSS, Terminal | скоро |
| 16 | Discord-боты — Echo, Bounty, Meek, Amp | скоро |
| 17 | Мост Reddit — сканирование, черновик, одобрение, публикация | скоро |
| 18 | Аудиоцепочка — SM7B, Scarlett, PipeWire, маршрутизация | скоро |
| 19 | Клонирование голоса — запись, XTTS v2, обучение | скоро |
| 20 | The Downcomers — первый трек, дублирование вокала, DistroKid | скоро |
| 21 | Игра — Undercroft, античит, Dealer AI | скоро |
| 22 | Бенчмарки — llama-bench, GitHub Pages, история | скоро |
| 23 | CI/CD — GitHub Actions, релизы, упаковка | скоро |
| 24 | Полная автономная демонстрация — тег → агенты → пост в Reddit | скоро |

*99% пользователей не имеют Claude. Эти обучалки делают процесс лёгким и без него. «Там, куда мы направляемся, дороги нам не нужны.»*

## Благодарности

**Спроектировано и построено архитектором** — каждый скрипт, каждый сервис, каждый агент. Из исходников. Без срезанных углов. *«Я неизбежен.»*

Основано на [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) от Light-Heart-Labs. Работает на [AMD Gaia](https://github.com/amd/gaia), [Lemonade](https://github.com/lemonade-sdk/lemonade), [llama.cpp](https://github.com/ggml-org/llama.cpp), [Open WebUI](https://github.com/open-webui/open-webui), [Vane](https://github.com/ItzCrazyKns/Vane), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Kokoro](https://github.com/remsky/Kokoro-FastAPI), [ComfyUI](https://github.com/comfyanonymous/ComfyUI), [SearXNG](https://github.com/searxng/searxng), [Qdrant](https://github.com/qdrant/qdrant), [n8n](https://github.com/n8n-io/n8n), [Caddy](https://github.com/caddyserver/caddy), [ROCm](https://github.com/ROCm/TheRock).

Сообщество: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes), [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup) и сообщества Framework/Arch Linux.

## Лицензия

Apache 2.0
