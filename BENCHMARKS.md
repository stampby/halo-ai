# halo-ai Benchmark Results

**Date**: 2026-03-24  
**Hardware**: AMD Ryzen AI MAX+ 395 (Strix Halo), 128GB LPDDR5x-8000  
**Kernel**: 6.19.9-arch1-1  
**ROCm**: 7.13 (TheRock nightly, gfx1151)  
**GPU Memory (GTT)**: 115 GB  
**Backend**: llama.cpp HIP + rocWMMA Flash Attention  
**Model**: Qwen3-30B-A3B (MoE, Q4_K_M, 18GB)

## Inference Performance

| Test | Prompt Tokens | Gen Tokens | Prompt Speed | Gen Speed | TTFT | Total |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| Short Q&A | 12 | 20 | 217 tok/s | 73.3 tok/s | 55ms | 0.33s |
| Technical explanation | 13 | 200 | 222 tok/s | 70.2 tok/s | 59ms | 2.91s |
| Long generation | 31 | 500 | 302 tok/s | 68.4 tok/s | 103ms | 7.42s |
| Code generation | 16 | 300 | 257 tok/s | 69.0 tok/s | 62ms | 4.41s |
| Reasoning (CoT) | 32 | 200 | 288 tok/s | 67.6 tok/s | 111ms | 3.07s |

### Summary

- **Generation**: 67-73 tok/s sustained (varies with reasoning complexity)
- **Prompt processing**: 217-302 tok/s (scales with prompt length)
- **Time to first token**: 55-111ms
- **GPU utilization during inference**: 97%
- **GPU temperature under sustained load**: 55°C (well within limits)

### Why MoE Models Excel on Strix Halo

Qwen3-30B-A3B is a Mixture of Experts model — 30B total parameters but only ~3B active per token. This is the ideal architecture for Strix Halo because:

- **Memory bandwidth is the bottleneck**, not compute. Strix Halo's ~215 GB/s LPDDR5x bandwidth is shared between CPU and GPU.
- **MoE activates fewer parameters per token**, meaning less data moved per inference step.
- **The full 30B model fits in 18GB**, leaving 97GB free for larger models, longer contexts, or multiple models.

Dense 70B models achieve ~15-20 tok/s on the same hardware — usable but significantly slower due to bandwidth saturation.

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
| GPU Power (inference) | ~4W (integrated, shared power) |

## Service Memory Footprint

All 10 services running simultaneously:

| Service | Memory | Notes |
|---------|--------|-------|
| llama-server (Qwen3-30B) | 657 MB | + 18GB GPU for model weights |
| Open WebUI | 3,238 MB | Includes embedding models |
| Qdrant | 514 MB | Vector DB (grows with data) |
| ComfyUI | 509 MB | PyTorch ROCm loaded |
| n8n | 438 MB | Workflow engine |
| DreamServer Dashboard | ~55 MB | UI + API |
| SearXNG | 94 MB | Search proxy |
| Vane (Perplexica) | 35 MB | Next.js server |
| Lemonade | 20 MB | C++ router |
| **Total service overhead** | **~5.6 GB** | |

**System total**: 27 GB RAM used, 97 GB available, 115 GB GPU-addressable.

## Boot Performance

| Phase | Time |
|-------|------|
| Firmware (UEFI) | 6.9s |
| Bootloader (systemd-boot) | 3.5s |
| Kernel | 5.4s |
| Userspace to all services | 3.4s |
| **Total** | **19.3s** |

Zero failed units. No errors.
