# halo-ai Benchmark Results

**Date**: 2026-04-01 (live benchmarks — llama.cpp b8599)
**Hardware**: AMD Ryzen AI MAX+ 395 (Strix Halo), 128GB LPDDR5x-8000
**Kernel**: 6.19.9-arch1-1
**ROCm**: 7.13.0 (TheRock nightly, gfx1151)
**GPU Memory (GTT)**: 123 GB
**Model**: Qwen3-30B-A3B (MoE, Q4_K_M, 18GB)

## Backend Comparison

| Backend | Gen Speed (200 tok) | Gen Speed (500 tok) | Prompt Speed |
|---------|:---:|:---:|:---:|
| **Vulkan (RADV) + Flash Attention** | **83.9 tok/s** | **83.6 tok/s** | 241-268 tok/s |
| OpenCL (secondary instance) | — | — | Running on :8083 |

**Default backend is Vulkan + Flash Attention** (port 8081). OpenCL instance runs on port 8083 as a secondary. *"These go to eleven."*

## Inference Performance (Vulkan + FA, default)

Live benchmark results with 42 services running simultaneously:

| Test | Prompt Tokens | Gen Tokens | Gen Speed | TTFT | Total |
|------|:---:|:---:|:---:|:---:|:---:|
| Short prompt | 1 | 14 | 91.3 tok/s | 15ms | 0.2s |
| Medium prompt | 43 | 200 | 83.9 tok/s | 160ms | 3.2s |
| Code generation | 31 | 403 | 83.6 tok/s | 121ms | 6.1s |
| Long sustained | 34 | 1000 | 82.9 tok/s | 141ms | 12.4s |

### Key Metrics

- **Generation**: 82.9-91.3 tok/s sustained (Vulkan + Flash Attention)
- **Prompt processing**: 68-268 tok/s depending on input length
- **Time to first token**: 15-160ms
- **GPU temperature**: 59°C with all services running (fan curve active)

### Why MoE Models Excel on Strix Halo

Qwen3-30B-A3B is a Mixture of Experts model — 30B total parameters but only ~3B active per token. This is ideal for Strix Halo because memory bandwidth (~215 GB/s) is the bottleneck, not compute. MoE activates fewer parameters per token = less data moved = faster generation.

Dense 70B models achieve ~15-20 tok/s on the same hardware — usable but significantly slower. *"Clever girl."*

## GPU & Memory Profile

| Metric | Value |
|--------|-------|
| GPU | Radeon 8060S (RDNA 3.5, 40 CUs, gfx1151) |
| GTT Total | 123 GB |
| GTT Used (all services) | 25.5 GB |
| GTT Free | 97.5 GB |
| GPU Temp (42 services running) | 59°C |

## Service Memory Footprint

All 42 services running simultaneously:

| Service | RSS Memory |
|---------|--------|
| llama-server Vulkan (Qwen3-30B, :8081) | 6,378 MB |
| llama-server OpenCL (Qwen3-30B, :8083) | 21,361 MB |
| Open WebUI | 586 MB |
| ComfyUI | 550 MB |
| Qdrant | 408 MB |
| Home Assistant | 379 MB |
| n8n | 373 MB |
| Vane (Next.js) | 248 MB |
| fail2ban | 238 MB |
| whisper-server | 172 MB |
| Gaia (UI + API + MCP) | 339 MB |
| Lemonade | 33 MB |
| Caddy | 68 MB |

**System**: 42 services + 17 agents running. 123 GB GPU-addressable.

## Thermal & Fan Configuration

These benchmarks were measured with a **custom quiet fan curve** applied via the `ec-su_axb35` kernel module. The Bosgame M5's stock fan profile is aggressive and unnecessary. This curve keeps the system silent under load while maintaining safe temperatures.

### Fan Control Driver

```bash
# Install the kernel module (Bosgame M5 / GMKtec EVO-X2 / Sixunited AXB35 boards)
git clone https://github.com/cmetz/ec-su_axb35-linux.git
cd ec-su_axb35-linux
make && sudo make install
sudo modprobe ec_su_axb35
```

### Quiet Fan Curve (used for all benchmarks)

Fans stay OFF until 70°C, then ramp gradually. Hysteresis prevents flapping.

```bash
# Ramp UP thresholds (°C): level 0→1, 1→2, 2→3, 3→4, 4→5
echo "70,78,85,92,97" | sudo tee /sys/class/ec_su_axb35/fan1/rampup_curve
echo "70,78,85,92,97" | sudo tee /sys/class/ec_su_axb35/fan2/rampup_curve
echo "72,80,87,93,97" | sudo tee /sys/class/ec_su_axb35/fan3/rampup_curve

# Ramp DOWN thresholds (°C): level 1→0, 2→1, 3→2, 4→3, 5→4
echo "55,65,75,85,92" | sudo tee /sys/class/ec_su_axb35/fan1/rampdown_curve
echo "55,65,75,85,92" | sudo tee /sys/class/ec_su_axb35/fan2/rampdown_curve
echo "50,60,72,85,92" | sudo tee /sys/class/ec_su_axb35/fan3/rampdown_curve
```

Or use the unified CLI: `halo fan quiet`

### Measured Thermals

| Condition | GPU Temp | Fan1 | Fan2 | Fan3 | Noise |
|-----------|----------|------|------|------|-------|
| Idle | 31°C | 0 rpm | 0 rpm | 0 rpm | Silent |
| Sustained inference (83 tok/s) | 55-65°C | 0 rpm | 0 rpm | 0 rpm | Silent |
| Heavy GPU + all 42 services | 59°C | 0 rpm | 0 rpm | ~500 rpm | Silent |
| Stress test (120W sustained) | 85-90°C | ~2000 rpm | ~2000 rpm | ~1500 rpm | Noticeable |

**Key takeaway**: At 83+ tok/s sustained inference with 42 services running, the GPU stays at 59°C with **all fans off**. The quiet fan curve achieves recording-studio silence for audio work while maintaining full performance. *The silence of the fans.*

### Persist Across Reboots

```bash
# Auto-load module
echo "ec_su_axb35" | sudo tee /etc/modules-load.d/ec-su-axb35.conf

# Systemd service applies curves on boot
# See systemd/halo-fancontrol.service
sudo systemctl enable halo-fancontrol
```

## Complete Homelab AI Stack (2026-04-01)

42 services — all built from source — zero cloud. *"I know kung fu."*

### LLM Inference

| Model | Prompt Speed | Gen Speed | VRAM | Backend |
|-------|-------------|-----------|------|---------|
| **Qwen3-30B-A3B** (MoE) | 68-268 tok/s | **83-91 tok/s** | 18 GB | Vulkan + FA |
| **Qwen2.5-Coder-7B** | **515.7 tok/s** | **48.6 tok/s** | 4.1 GB | llama.cpp HIP |
| Llama 3 70B (dense) | — | ~18 tok/s | 40 GB | Vulkan |

### Video Generation

| Component | Model | Size | Resolution | GPU Memory | Status |
|-----------|-------|------|-----------|------------|--------|
| **Wan2.1** | T2V-1.3B | 17 GB | 832×480 | 5.8 GB | Working — text-to-video |
| **ComfyUI + FLUX.1** | FLUX.1 schnell | ~12 GB | Up to 4K | 123 GB available | 5.2x faster than SDXL on ROCm 7 |
| **ComfyUI + SDXL** | SD XL Base 1.0 | ~6.5 GB | Up to 4K | 123 GB available | Fallback — image + AnimateDiff |

### Music Generation

| Component | Model | Size | Sample Rate | Status |
|-----------|-------|------|-------------|--------|
| **MusicGen** | facebook/musicgen-small | 1.1 GB | 32 kHz | Working — end-to-end tested, audio generated |

### Voice & Speaker ID

| Component | Version | Purpose | Status |
|-----------|---------|---------|--------|
| **whisper.cpp** | compiled gfx1151 | Speech-to-text | Working (medium.en deployed, large-v3-turbo queued) |
| **Kokoro** | 54 voices | Text-to-speech | Working |
| **pyannote-audio** | v4.0.4 | Speaker identification | Working — voice is identity |
| **XTTS v2** | — | Voice cloning | Working — architect's voice |

### Object Detection

| Component | Version | Speed | Status |
|-----------|---------|-------|--------|
| **YOLO** | v8.4.32 | CPU inference | Working — GPU pending ROCm gfx1151 stable |

### Code Assistant

| Metric | Result |
|--------|--------|
| Model | Qwen2.5-Coder-7B-Instruct Q4_K_M |
| Prompt processing | **515.7 tok/s** |
| Generation | **48.6 tok/s** |
| VRAM | 4.1 GB |
| Helper | `~/llama.cpp/code-assist.sh` |

### OCR & Translation

| Component | Version | Built From | Status |
|-----------|---------|-----------|--------|
| **Tesseract** | 5.5.2 | C++ source | AVX512, OpenMP, SSE4.1 |
| **Argos Translate** | 1.11.0 | Python source | Offline multi-language |

### Fine-Tuning

| Component | Version | Framework | Status |
|-----------|---------|-----------|--------|
| **Axolotl** | 0.16.0 | PyTorch+ROCm | QLoRA, LoRA, full fine-tune |

### Monitoring & Ops

| Component | Version | Built From | Port |
|-----------|---------|-----------|------|
| **Prometheus** | 3.11.0-rc.0 | Go source | :9090 |
| **Node Exporter** | 1.10.2 | Go source | :9100 |
| **Grafana** | latest | Go source | :3030 |
| **Borg Backup** | 2.0.0b22 | Python/C source | — |
| **Home Assistant** | latest | Python source | :8123 |
| **Frigate NVR** | latest | Python source | — |

### Halo Memory & Intelligence

| Component | Status | Details |
|-----------|--------|---------|
| **Halo Memory** | Working | User profiles, conversations, preferences, voice enrollment |
| **Speaker ID** | Ready | pyannote voice profiles — your voice is your login |
| **Agent routing** | Working | 17 agents, each owns their services, Halo routes |

### Disk Usage (Strix Halo)

| Component | Size |
|-----------|------|
| Wan2.1 (venv + model) | 30 GB |
| MusicGen (venv + model) | 16 GB |
| YOLO (venv + model) | ~8 GB |
| Axolotl (venv) | ~24 GB |
| pyannote (venv) | ~8 GB |
| Qwen2.5-Coder-7B model | 4.4 GB |
| Python 3.12 (/opt) | ~200 MB |
| **Total new services** | **~91 GB** |

### ROCm Compatibility Notes

- **LD_PRELOAD fix**: System ROCm 7.13 vs PyTorch bundled ROCm 7.0 — `LD_PRELOAD=/opt/rocm/lib/libamdhip64.so` resolves segfaults
- **gfx1151**: Bleeding edge GPU arch — Vulkan backend outperforms HIP for generation
- **Python 3.14**: Too new for some packages — Python 3.12 built from source for MusicGen
- **xformers**: Patched out of MusicGen, replaced with native torch attention

### Stack Totals

| Metric | Count |
|--------|-------|
| **Total services** | **42** |
| **Autonomous agents** | **17** |
| **Total tools** | **98+** |
| **GPU VRAM available** | **123 GB** |
| **Boot to ready** | **19.3s** |
| **Machines in mesh** | **4** |
| **Cloud dependencies** | **0** | *"I'm not even supposed to be here today."* |

*Built by CLI — stamped by the architect.*

## Boot Performance

*"Ludicrous speed — GO!"*

| Phase | Time |
|-------|------|
| Firmware → services ready | **19.3s** |


## Update Log

- **2026-04-01**: Full live benchmark scrub. Corrected all values from real measurements with 42 services running. GTT: 123 GB (was 115). Gen: 83-91 tok/s. Prompt: 68-268 tok/s. Services: 42 (was 25). llama.cpp b8599.
- **2026-03-31**: Updated to llama.cpp b8591. Vulkan gen: 86.91 tok/s.
- **2026-03-30**: Initial benchmarks published.
