🌐 [English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Português](README.pt.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [हिन्दी](README.hi.md) | **العربية**

<div align="center">

<picture>
  <img src="https://raw.githubusercontent.com/stampby/halo-ai/main/assets/avatars/halo-ai.svg" alt="halo ai" width="200">
</picture>

# halo-ai

### حزمة الذكاء الاصطناعي المباشرة على العتاد لمعالج AMD Strix Halo

**87 tok/s. بدون حاويات. 115GB ذاكرة GPU. مُجمَّع من المصدر. أنا أعرف الكونغ فو.**

*بُني بسطر الأوامر — بختم المعماري*

[![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=archlinux&logoColor=white)](https://archlinux.org)
[![ROCm](https://img.shields.io/badge/ROCm_7.13-ED1C24?style=flat&logo=amd&logoColor=white)](https://rocm.docs.amd.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-halo--ai-5865F2?style=flat&logo=discord&logoColor=white)](https://discord.gg/dSyV646eBs)

</div>

---

> **جديد هنا؟** ابدأ مع [الدروس التعليمية](#الدروس-التعليمية) — شروحات فيديو كاملة من التثبيت إلى التشغيل الذاتي.

---

## ما هذا؟

منصة ذكاء اصطناعي متكاملة لمعالج **AMD Ryzen AI MAX+ 395** — استدلال LLM، محادثة، بحث عميق، صوت، توليد صور، RAG، وسير عمل. خطوط إنتاج ذاتية لتطوير الألعاب وإنتاج الموسيقى وإنتاج الفيديو. 33 خدمة، 17 وكيلاً ذاتياً، 98 أداة، 5 بوتات Discord. كل شيء مباشر على العتاد، كل شيء مُجمَّع من المصدر، كل شيء على شريحة واحدة بذاكرة موحدة 128GB. من الإقلاع إلى الجاهزية: 18.7 ثانية.

**تحدث إليه.** تكلم مع Halo، شاهد النص، اسمع الرد. كل أداة، كل وكيل، كل ميزة — يتحكم بها صوتك. برمجة بالحدس في المنزل، جاهزة للاستخدام، على عتادك الخاص. *"افتح أبواب حجرة المركبة، HAL."*

## لماذا مباشر على العتاد؟

- **الحاويات تضيف 15-20% حملاً زائداً** على أحمال عمل GPU. عندما تمتلك 115GB من الذاكرة الموحدة على شريحة واحدة، كل واط وكل بايت يجب أن يذهب للاستدلال، لا للتنسيق. *"لا تحاول ثني الملعقة. بدلاً من ذلك، حاول فقط أن تدرك الحقيقة: لا وجود للحاوية."*
- **التجميع من المصدر** يعني تحسينات gfx1151 الأصلية التي تفوتها الحزم المُعدَّة مسبقاً. من هنا تأتي سرعة 87 tok/s.
- **بدون مؤقتات. بدون cron. ذكاء اصطناعي كامل.** الوكلاء لا يتحققون وفق جدول — بل يراقبون الظروف ويتصرفون عند حدوث تغيير. خدمة توقفت؟ تُكتشف وتُصلح قبل أن تلاحظ. GPU يسخن؟ يُبلَّغ عنه لحظة حدوثه. ليس كل 30 ثانية. *اللحظة ذاتها.* آسف يا ديف، لكن هذه الحزمة لا تنام.
- **تنجو من تحديثات Arch المتدحرجة.** جمّد الحزمة، دع pacman يحدّث، الوكلاء يكتشفون إن تعطل شيء، ذوّب للتراجع في 30 ثانية. لهذا يعمل halo-ai على Arch بلا خوف. *"إنه مجرد خدش."*
- **أنت تملك الحزمة بالكامل.** لا مدير حزم يقرر متى يتوقف خادم الذكاء الاصطناعي خاصتك. *"كنزي العزيز."*

## التثبيت السريع

```bash
curl -fsSL https://raw.githubusercontent.com/stampby/halo-ai/main/install.sh | bash
```

مثبّت تفاعلي — اسم المستخدم، كلمات المرور، اسم المضيف، أي الخدمات تُفعَّل. إعدادات افتراضية معقولة. كلمة مرور Caddy الافتراضية هي `Caddy` — غيّرها فوراً. *"اختر بحكمة."*

## الميزات

### الذكاء الاصطناعي والاستدلال
- **محادثة LLM** — [Open WebUI](https://github.com/open-webui/open-webui) مع RAG، نماذج متعددة، رفع مستندات
- **بحث عميق** — [Vane](https://github.com/ItzCrazyKns/Vane) بمصادر موثقة وبحث خاص
- **توليد الصور** — [ComfyUI](https://github.com/comfyanonymous/ComfyUI) على 115GB GPU، SDXL، Flux
- **توليد الفيديو** — [Wan2.1](https://github.com/Wan-Video/Wan2.1) على ROCm 6.3
- **توليد الموسيقى** — [MusicGen](https://github.com/facebookresearch/audiocraft) من Meta، استدلال GPU محلي
- **تحويل الكلام لنص** — [whisper.cpp](https://github.com/ggerganov/whisper.cpp) مُجمَّع لـ gfx1151
- **تحويل النص لكلام** — [Kokoro](https://github.com/remsky/Kokoro-FastAPI) مع 54 صوتاً طبيعياً
- **مساعد برمجة** — Qwen2.5 Coder 7B على llama.cpp، بسرعة 48.6 tok/s
- **كشف الأجسام** — [YOLO](https://github.com/ultralytics/ultralytics) v8، استدلال في الوقت الحقيقي
- **التعرف الضوئي على الحروف** — [Tesseract](https://github.com/tesseract-ocr/tesseract) v5.5.2، مُجمَّع من المصدر
- **الترجمة** — [Argos Translate](https://github.com/argosopentech/argos-translate)، متعددة اللغات بدون اتصال
- **الضبط الدقيق** — [Axolotl](https://github.com/axolotl-ai-cloud/axolotl)، درّب نماذجك محلياً
- **واجهة برمجة موحدة** — [Lemonade](https://github.com/lemonade-sdk/lemonade) v10.0.1، متوافق مع OpenAI/Ollama/Anthropic

### الوكلاء — [التوثيق](docs/AGENTS.md)
- **17 وكيلاً ذاتياً** على [AMD Gaia](https://github.com/amd/gaia) مع 98 أداة
- **[Echo](https://github.com/stampby/echo)** — الواجهة العامة، جسر Reddit، Discord، وسائل التواصل
- **[Meek](https://github.com/stampby/meek)** — رئيس الأمن، 9 وكلاء Reflex فرعيين ([Pulse](https://github.com/stampby/pulse)، [Ghost](https://github.com/stampby/ghost)، [Gate](https://github.com/stampby/gate)، [Shadow](https://github.com/stampby/shadow)، [Fang](https://github.com/stampby/fang)، [Mirror](https://github.com/stampby/mirror)، [Vault](https://github.com/stampby/vault)، [Net](https://github.com/stampby/net)، [Shield](https://github.com/stampby/shield))
- **[Bounty](https://github.com/stampby/bounty)** — صياد الأخطاء، أمن هجومي، أخو Halo
- **[Amp](https://github.com/stampby/amp)** — مهندس صوت، استنساخ صوتي، إنتاج موسيقي
- **[Sentinel](https://github.com/stampby/sentinel)** — مراجعة PR تلقائية، بوابة الكود
- **[Mechanic](https://github.com/stampby/mechanic)** — تشخيص العتاد، مراقبة النظام
- **[Forge](https://github.com/stampby/forge)** — بناء الألعاب، خط إنتاج الأصول، نشر Steam
- **[Dealer](https://github.com/stampby/dealer)** — سيد اللعبة بالذكاء الاصطناعي، كل جولة مختلفة
- **[Conductor](https://github.com/stampby/conductor)** — مؤلف موسيقي بالذكاء الاصطناعي، موسيقى ألعاب ديناميكية
- **[Quartermaster](https://github.com/stampby/quartermaster)** — إدارة خوادم الألعاب، تدقيق Steam أسبوعي
- **[Crypto](https://github.com/stampby/crypto)** — مراجحة، مراقبة السوق
- **The Downcomers** — [Piper](https://github.com/stampby/piper)، [Axe](https://github.com/stampby/axe)، [Rhythm](https://github.com/stampby/rhythm)، [Bottom](https://github.com/stampby/bottom)، [Bones](https://github.com/stampby/bones)

### الأمان — [التوثيق](docs/SECURITY.md)
- **مفاتيح SSH فقط** — بدون كلمات مرور، مستخدم واحد، fail2ban. *"لن تمر."*
- **nftables بحظر افتراضي** — شبكة محلية فقط، رفض كل شيء آخر
- **جميع الخدمات على localhost** — Caddy هو نقطة الدخول الوحيدة
- **تقوية Systemd** — ProtectSystem، PrivateTmp، NoNewPrivileges على كل خدمة
- **[Shadow](https://github.com/stampby/shadow)** — مراقبة سلامة الملفات، مراقب شبكة SSH

### حماية الحزمة — [التوثيق](docs/STACK-PROTECTION.md)
- **تجميد/إذابة** — لقطة واستعادة بنقرة واحدة لكامل الحزمة. *"سأعود."*
- **تجميع من المصدر** — إعادة بناء أسبوعية بتحسينات gfx1151 الأصلية
- **[Mixer](https://github.com/stampby/mixer)** — لقطات شبكية موزعة، بدون NAS، بدون نقطة فشل واحدة
- **واجهة Man Cave** — حالة الحزمة، مؤشرات التحديث، زر التجميع

### الأتمتة — [التوثيق](docs/AUTONOMOUS-PIPELINE.md)
- **سير عمل n8n** — إصدارات GitHub تُطلق منشورات Echo على Reddit تلقائياً
- **فرز المشكلات** — المشكلات الجديدة تُوجَّه تلقائياً إلى Bounty أو Meek أو Amp
- **لقطات شبكية** — Shadow يوزع النسخ الاحتياطية كل 6 ساعات
- **CI/CD** — GitHub Actions فحص، بناء، إصدار عند كل وسم

### تطوير الألعاب الذاتي — [خط الإنتاج](docs/AUTONOMOUS-PIPELINE.md)
- **[Voxel Extraction](https://github.com/stampby/voxel-extraction)** — لعبة استخراج PvE تعاونية في Godot 4
- **[Arcade](https://github.com/stampby/halo-arcade)** — مدير خوادم الألعاب، نشر بنقرة واحدة، محاكاة ريترو
- **سيد اللعبة بالذكاء الاصطناعي** — Dealer يشغل LLM محلي، كل جولة زنزانة فريدة. *"تريد أن تجنّ؟ هيا بنا نجنّ."*
- **مكافحة الغش** — ذاكرة مشفرة، مراقبة وقت التشغيل، وسم دائم للغشاشين. *"عليك أن تسأل نفسك سؤالاً واحداً: هل أشعر بالحظ؟"*
- **خط إنتاج كامل** — تصميم ← بناء ← اختبار ← نشر، الوكلاء يتولون كل شيء. *"الحياة، آه، تجد طريقها."*

### إنتاج الموسيقى الذاتي — [The Downcomers](https://github.com/stampby/amp)
- **استنساخ الصوت** — صوت المعماري عبر XTTS v2، إصدارات مرحلية
- **موسيقى تصويرية بالذكاء الاصطناعي** — بلوز/روك أصلي، فرقة كاملة، بدون أغلفة
- **كتب صوتية** — أعمال الملكية العامة، 1984 أول إصدار
- **واجهة صوتية** — خدمة تحويل النص لكلام، بدون احتفاظ بالبيانات
- **صوت تذكاري** — التقاط كلام الأحبة، بناء نسخة ذكاء اصطناعي بعد الوفاة. *"بعد كل هذا الوقت؟ دائماً."*
- **التوزيع** — DistroKid إلى Spotify، Apple Music، جميع المنصات

### إنتاج الفيديو الذاتي — [halo-ai Studios](docs/AUTONOMOUS-PIPELINE.md)
- **دراما Voxel** — سلسلة من 10 حلقات، سيناريو ← صوت ← رسوم متحركة ← عرض
- **دروس صوتية** — المعماري يروي، شروحات كاملة
- **مضيف بث مشارك** — صوت المعماري كمعلق مباشر بالذكاء الاصطناعي لـ Twitch/YouTube
- **خط إنتاج كامل** — كتابة ← تمثيل ← عرض ← توزيع، كل شيء ذاتي. *"أضواء، كاميرا، حركة."*

### البنية التحتية [Kansas City Shuffle]
- **شبكة SSH من 4 أجهزة [Kansas City Shuffle]** — ryzen، strix-halo، minisforum، sligar
- **[Mixer](https://github.com/stampby/mixer)** — لقطات btrfs حلقية عبر SSH [Kansas City Shuffle]
- **[المعايير](https://stampby.github.io/benchmarks/)** — تتبع الأداء المباشر، السجل عبر الزمن
- **[Man Cave](https://github.com/stampby/man-cave)** — مركز التحكم بمقاييس GPU، صحة الخدمات، نشاط الوكلاء
- **صفر سحابة** — بدون اشتراكات، بدون واجهات خارجية، بدون تبعيات لطرف ثالث. *"لا توجد سحابة. يوجد فقط Zuul."*

## الخدمات

| الخدمة | المنفذ | الغرض |
|---------|------|---------|
| Lemonade | 8080 | واجهة AI موحدة (متوافقة مع OpenAI/Ollama/Anthropic) |
| llama.cpp | 8081 | استدلال LLM — واجهتا Vulkan + HIP |
| Open WebUI | 3000 | محادثة مع RAG، مستندات، نماذج متعددة |
| Vane | 3001 | بحث عميق بمصادر موثقة |
| SearXNG | 8888 | محرك بحث وصفي خاص |
| Qdrant | 6333 | قاعدة بيانات متجهية لـ RAG |
| n8n | 5678 | أتمتة سير العمل |
| whisper.cpp | 8082 | تحويل الكلام لنص |
| Kokoro | 8083 | تحويل النص لكلام (54 صوتاً) |
| ComfyUI | 8188 | توليد الصور |
| Wan2.1 | — | توليد الفيديو (GPU Strix Halo) |
| MusicGen | — | توليد الموسيقى (GPU Strix Halo) |
| YOLO | — | كشف الأجسام (Strix Halo) |
| Tesseract | — | OCR — مسح المستندات |
| Argos | — | ترجمة بدون اتصال |
| Axolotl | — | ضبط دقيق للنماذج (GPU Strix Halo) |
| Prometheus | 9090 | جمع المقاييس |
| Grafana | 3030 | لوحات المراقبة |
| Node Exporter | 9100 | مقاييس النظام |
| Home Assistant | 8123 | أتمتة المنزل |
| Borg | — | نسخ احتياطية مشفرة إلى GlusterFS |
| Dashboard | 3003 | مقاييس GPU + صحة الخدمات |
| Gaia API | 8090 | خادم إطار الوكلاء |
| Gaia MCP | 8765 | جسر Model Context Protocol |

جميع الخدمات تعمل على `127.0.0.1` — الوصول عبر Caddy reverse proxy.

## الأداء

| النموذج | السرعة | VRAM |
|-------|-------|------|
| Qwen3-30B-A3B (MoE) | **87 tok/s** | 18 GB |
| Llama 3 70B | ~18 tok/s | 40 GB |

معايير كاملة مع الحرارة والذاكرة ومقارنات الواجهات الخلفية: [BENCHMARKS.md](BENCHMARKS.md)

## البنية التحتية [Kansas City Shuffle]

4 أجهزة — شبكة SSH — لقطات mixer — صفر سحابة [Kansas City Shuffle]

| الجهاز | الدور |
|---------|------|
| ryzen | سطح المكتب — التطوير |
| strix-halo | 128GB GPU — استدلال الذكاء الاصطناعي |
| minisforum | Windows 11 — مكتب / اختبار |
| sligar | 1080Ti — تدريب الصوت |

المتصفح > Caddy > Lemonade (واجهة موحدة) > جميع الخدمات:

| الخدمة | ما تفعله |
|---------|-------------|
| llama.cpp | استدلال LLM |
| whisper.cpp | تحويل الكلام لنص |
| Kokoro | تحويل النص لكلام |
| ComfyUI | توليد الصور |
| Open WebUI | محادثة + RAG |
| Vane | بحث عميق |
| n8n | أتمتة سير العمل |
| Gaia | 17 وكيلاً، 78 أداة |
| Man Cave | مركز التحكم |

تفاصيل البنية الكاملة: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## التوثيق

| الدليل | ما يغطيه |
|-------|----------------|
| [البنية](docs/ARCHITECTURE.md) | تصميم النظام، تدفق البيانات، واجهات GPU |
| [الخدمات](docs/SERVICES.md) | المنافذ، الإعدادات، فحوصات الصحة |
| [الأمان](docs/SECURITY.md) | جدار الحماية، SSH، TLS، تدوير كلمات المرور |
| [حماية الحزمة](docs/STACK-PROTECTION.md) | لماذا لن تكسر تحديثات Arch حزمتك |
| [المعايير](BENCHMARKS.md) | بيانات الأداء الكاملة |
| [المخططات](docs/BLUEPRINTS.md) | خارطة الطريق والميزات المخططة |
| [خط الإنتاج الذاتي](docs/AUTONOMOUS-PIPELINE.md) | خط إنتاج الألعاب والموسيقى والفيديو بدون تدخل بشري |
| [استكشاف الأخطاء](docs/TROUBLESHOOTING.md) | المشكلات الشائعة وحلولها |
| [وصول VPN](docs/VPN.md) | إعداد WireGuard |
| [Kansas City Shuffle](docs/KANSAS-CITY-SHUFFLE.md) | حلقة الناقل، ClusterFS، إصلاح تلقائي، إدارة الشبكة |
| [Mixer](https://github.com/stampby/mixer) | لقطات SSH الشبكية — نسخ احتياطية موزعة، بدون نقطة فشل واحدة [Kansas City Shuffle] |
| [سجل التغييرات](CHANGELOG.md) | تاريخ الإصدارات |

## [لقطات الشاشة](docs/SCREENSHOTS.md)

## الدروس التعليمية

شروحات فيديو — من البداية للنهاية، بدون حذف أي شيء. روابط YouTube غير مدرجة.

| # | الفيديو | الحالة |
|---|-------|--------|
| 1 | الرؤية — ما هو halo-ai ولماذا | قريباً |
| 2 | إعداد العتاد — توصيل الشبكة، 4 أجهزة | قريباً |
| 3 | تثبيت Arch Linux — نظام أساسي، btrfs، أول إقلاع | قريباً |
| 4 | سكربت التثبيت — 13 خدمة مُجمَّعة من المصدر | قريباً |
| 5 | الأمان — nftables، SSH، Caddy، نموذج رفض الكل | قريباً |
| 6 | Lemonade + llama.cpp — واجهة موحدة، 87 tok/s | قريباً |
| 7 | المحادثة + RAG — Open WebUI، رفع المستندات، بحث متجهي | قريباً |
| 8 | البحث العميق — Vane، مصادر موثقة، بحث خاص | قريباً |
| 9 | توليد الصور — ComfyUI على 115GB GPU | قريباً |
| 10 | الصوت — whisper.cpp، Kokoro TTS، 54 صوتاً | قريباً |
| 11 | سير العمل — أتمتة n8n، GitHub webhooks | قريباً |
| 12 | الوكلاء — واجهة Gaia، جميع الوكلاء الـ 17، الإدارة | قريباً |
| 13 | Man Cave — مركز التحكم، حماية الحزمة، تجميد/إذابة | قريباً |
| 14 | الشبكة — مفاتيح SSH، 4 أجهزة، mixer، Shadow | قريباً |
| 15 | Windows في الشبكة — Minisforum، VSS، Terminal | قريباً |
| 16 | بوتات Discord — Echo، Bounty، Meek، Amp | قريباً |
| 17 | جسر Reddit — مسح، مسودة، موافقة، نشر | قريباً |
| 18 | سلسلة الصوت — SM7B، Scarlett، PipeWire، التوجيه | قريباً |
| 19 | استنساخ الصوت — تسجيل، XTTS v2، تدريب | قريباً |
| 20 | The Downcomers — أول مقطوعة، مضاعفة صوتية، DistroKid | قريباً |
| 21 | اللعبة — Undercroft، مكافحة الغش، Dealer AI | قريباً |
| 22 | المعايير — llama-bench، GitHub Pages، السجل | قريباً |
| 23 | CI/CD — GitHub Actions، إصدارات، تعبئة | قريباً |
| 24 | عرض ذاتي كامل — وسم ← وكلاء ← منشور Reddit | قريباً |

*99% من المستخدمين ليس لديهم Claude. هذه الدروس تجعل التجربة سهلة بدونه. "حيث نحن ذاهبون، لا نحتاج طرقاً."*

## الشكر

**صُمم وبُني بيد المعماري** — كل سكربت، كل خدمة، كل وكيل. من المصدر. بدون اختصارات. *"أنا حتمي."*

بُني على [DreamServer](https://github.com/Light-Heart-Labs/DreamServer) من Light-Heart-Labs. يعمل بـ [AMD Gaia](https://github.com/amd/gaia)، [Lemonade](https://github.com/lemonade-sdk/lemonade)، [llama.cpp](https://github.com/ggml-org/llama.cpp)، [Open WebUI](https://github.com/open-webui/open-webui)، [Vane](https://github.com/ItzCrazyKns/Vane)، [whisper.cpp](https://github.com/ggerganov/whisper.cpp)، [Kokoro](https://github.com/remsky/Kokoro-FastAPI)، [ComfyUI](https://github.com/comfyanonymous/ComfyUI)، [SearXNG](https://github.com/searxng/searxng)، [Qdrant](https://github.com/qdrant/qdrant)، [n8n](https://github.com/n8n-io/n8n)، [Caddy](https://github.com/caddyserver/caddy)، [ROCm](https://github.com/ROCm/TheRock).

المجتمع: [kyuz0](https://github.com/kyuz0/amd-strix-halo-toolboxes)، [Gygeek](https://github.com/Gygeek/Framework-strix-halo-llm-setup)، ومجتمعات Framework/Arch Linux.

## الرخصة

Apache 2.0
