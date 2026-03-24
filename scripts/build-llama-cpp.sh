#!/bin/bash
set -euo pipefail
source /srv/ai/configs/rocm.env

SRC=/srv/ai/llama-cpp
cd "$SRC"

if [ ! -d .git ]; then
    git clone https://github.com/ggml-org/llama.cpp .
else
    git pull
fi

# HIP (ROCm) build
cmake -B build-hip -S .     -DGGML_HIP=ON     -DAMDGPU_TARGETS="gfx1151"     -DGGML_HIP_ROCWMMA_FATTN=ON     -DCMAKE_BUILD_TYPE=Release     -G Ninja
cmake --build build-hip --config Release -j$(nproc)

# Vulkan build
cmake -B build-vulkan -S .     -DGGML_VULKAN=ON     -DCMAKE_BUILD_TYPE=Release     -G Ninja
cmake --build build-vulkan --config Release -j$(nproc)

echo 'llama.cpp: HIP + Vulkan builds complete'
