# halo-ai Benchmark Results

**Date**: 2026-03-27 (updated)
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

## Boot Performance

| Phase | Time |
|-------|------|
| Firmware → services ready | **19.3s** |
