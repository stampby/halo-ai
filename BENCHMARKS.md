# halo-ai Benchmark Results

**Date**: 2026-03-30 (updated)
**Hardware**: AMD Ryzen AI MAX+ 395 (Strix Halo), 128GB LPDDR5x-8000
**Kernel**: 6.19.9-arch1-1
**ROCm**: 7.13 (TheRock nightly, gfx1151)
**GPU Memory (GTT)**: 115 GB
**Model**: Qwen3-30B-A3B (MoE, Q4_K_M, 18GB)

## Backend Comparison

| Backend | Gen Speed (200 tok) | Gen Speed (500 tok) | Prompt Speed |
|---------|:---:|:---:|:---:|
| **Vulkan (RADV) + Flash Attention** | **109 tok/s** | **109 tok/s** | 58-172 tok/s |
| HIP (ROCm) + rocWMMA FA | 70.2 tok/s | 68.4 tok/s | 217-302 tok/s |

**Vulkan wins for generation** (~55% faster). HIP wins for prompt processing. Default backend is now Vulkan + Flash Attention.

## Inference Performance (Vulkan + FA, default)

| Test | Prompt Tokens | Gen Tokens | Gen Speed | TTFT | Total |
|------|:---:|:---:|:---:|:---:|:---:|
| Short Q&A | 12 | 20 | 109 tok/s | <60ms | 0.2s |
| Technical explanation | 18 | 200 | 109 tok/s | 109ms | 2.0s |
| Long generation | 20 | 500 | 109 tok/s | 99ms | 4.8s |

### Key Metrics

- **Generation**: ~109 tok/s sustained (Vulkan + Flash Attention)
- **Time to first token**: <110ms
- **GPU utilization**: 97% during inference
- **GPU temperature**: 55°C under sustained load (well within limits)

### Why MoE Models Excel on Strix Halo

Qwen3-30B-A3B is a Mixture of Experts model — 30B total parameters but only ~3B active per token. This is ideal for Strix Halo because memory bandwidth (~215 GB/s) is the bottleneck, not compute. MoE activates fewer parameters per token = less data moved = faster generation.

Dense 70B models achieve ~15-20 tok/s on the same hardware — usable but significantly slower.

## GPU & Memory Profile

| Metric | Value |
|--------|-------|
| GPU | Radeon 8060S (RDNA 3.5, 40 CUs, gfx1151) |
| GTT Allocated | 115 GB |
| GTT Used (model loaded) | 21 GB |
| GTT Free | 94 GB |
| GPU Temp (idle) | 26°C |
| GPU Temp (sustained inference) | 55°C |
| GPU Utilization (inference) | 97% |

## Service Memory Footprint

All services running simultaneously:

| Service | Memory |
|---------|--------|
| llama-server (Qwen3-30B) | 657 MB + 18GB GPU |
| Open WebUI | 3,238 MB |
| Qdrant | 514 MB |
| ComfyUI | 509 MB |
| n8n | 438 MB |
| DreamServer Dashboard | ~55 MB |
| SearXNG | 94 MB |
| Vane (Perplexica) | 35 MB |
| Lemonade | 20 MB |
| **Total service overhead** | **~5.6 GB** |

**System**: 27 GB RAM used, 97 GB available, 115 GB GPU-addressable.

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
| Sustained inference (109 tok/s) | 55-65°C | 0 rpm | 0 rpm | 0 rpm | Silent |
| Heavy GPU + all 25 services | 65-75°C | ~800 rpm | ~800 rpm | ~500 rpm | Barely audible |
| Stress test (120W sustained) | 85-90°C | ~2000 rpm | ~2000 rpm | ~1500 rpm | Noticeable |

**Key takeaway**: At 109 tok/s sustained inference, the GPU stays under 70°C with **all fans off**. The quiet fan curve achieves recording-studio silence for audio work while maintaining full performance.

### Persist Across Reboots

```bash
# Auto-load module
echo "ec_su_axb35" | sudo tee /etc/modules-load.d/ec-su-axb35.conf

# Systemd service applies curves on boot
# See systemd/halo-fancontrol.service
sudo systemctl enable halo-fancontrol
```

## Complete Homelab AI Stack (2026-03-30)

25 services — all built from source — zero cloud. *"I know kung fu."*

### LLM Inference

| Model | Prompt Speed | Gen Speed | VRAM | Backend |
|-------|-------------|-----------|------|---------|
| **Qwen3-30B-A3B** (MoE) | 58-172 tok/s | **109 tok/s** | 18 GB | Vulkan + FA |
| **Qwen2.5-Coder-7B** | **515.7 tok/s** | **48.6 tok/s** | 4.1 GB | llama.cpp HIP |
| Llama 3 70B (dense) | — | ~18 tok/s | 40 GB | Vulkan |

### Video Generation

| Component | Model | Size | Resolution | GPU Memory | Status |
|-----------|-------|------|-----------|------------|--------|
| **Wan2.1** | T2V-1.3B | 17 GB | 832×480 | 5.8 GB | Working — text-to-video |
| **ComfyUI + SDXL** | Various | — | Up to 4K | 115 GB available | Working — image + AnimateDiff |

### Music Generation

| Component | Model | Size | Sample Rate | Status |
|-----------|-------|------|-------------|--------|
| **MusicGen** | facebook/musicgen-small | 1.1 GB | 32 kHz | Working — end-to-end tested, audio generated |

### Voice & Speaker ID

| Component | Version | Purpose | Status |
|-----------|---------|---------|--------|
| **whisper.cpp** | compiled gfx1151 | Speech-to-text | Working |
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
| **Total services** | **25** |
| **Autonomous agents** | **17** |
| **Total tools** | **98+** |
| **GPU VRAM available** | **115 GB** |
| **Boot to ready** | **19.3s** |
| **Machines in mesh** | **4** |
| **Cloud dependencies** | **0** |

*Built by CLI — stamped by the architect.*

## Boot Performance

| Phase | Time |
|-------|------|
| Firmware → services ready | **19.3s** |
