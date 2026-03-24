#!/bin/bash
set -euo pipefail
source /srv/ai/configs/rocm.env

SRC=/srv/ai/whisper-cpp
cd "$SRC"

if [ ! -d .git ]; then
    git clone https://github.com/ggerganov/whisper.cpp .
else
    git pull
fi

cmake -B build -S .     -DGGML_HIP=ON     -DAMDGPU_TARGETS="gfx1151"     -DCMAKE_BUILD_TYPE=Release     -G Ninja
cmake --build build --config Release -j$(nproc)

echo 'whisper.cpp: build complete'
