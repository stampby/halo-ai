# halo-ai Benchmark Results

**Date**: 2026-03-24  
**Hardware**: AMD Ryzen AI MAX+ 395 (Strix Halo), 128GB LPDDR5x-8000  
**Kernel**: 6.19.9-arch1-1  
**ROCm**: 7.13 (TheRock nightly, gfx1151)  
**GPU Memory (GTT)**: 115 GB  
**Model**: Qwen3-30B-A3B (MoE, Q4_K_M, 18GB)

## Backend Comparison

| Backend | Gen Speed (200 tok) | Gen Speed (500 tok) | Prompt Speed |
|---------|:---:|:---:|:---:|
| **Vulkan (RADV) + Flash Attention** | **88.9 tok/s** | **88.9 tok/s** | 58-172 tok/s |
| HIP (ROCm) + rocWMMA FA | 70.2 tok/s | 68.4 tok/s | 217-302 tok/s |

**Vulkan wins for generation** (~20% faster). HIP wins for prompt processing. Default backend is now Vulkan + Flash Attention.

## Inference Performance (Vulkan + FA, default)

| Test | Prompt Tokens | Gen Tokens | Gen Speed | TTFT | Total |
|------|:---:|:---:|:---:|:---:|:---:|
| Short Q&A | 12 | 20 | 89 tok/s | <60ms | 0.3s |
| Technical explanation | 18 | 200 | 88.9 tok/s | 109ms | 2.5s |
| Long generation | 20 | 500 | 88.9 tok/s | 99ms | 6.0s |

### Key Metrics

- **Generation**: ~89 tok/s sustained (Vulkan + Flash Attention)
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

## Boot Performance

| Phase | Time |
|-------|------|
| Firmware → services ready | **19.3s** |
