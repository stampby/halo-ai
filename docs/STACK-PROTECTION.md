# Stack Protection — Why Your AI Stack Won't Break

halo-ai runs on Arch Linux, a rolling release distro. That means system packages
update constantly — and those updates can break your AI stack if you're not careful.

**We solved this.** The AI stack is completely isolated from the system. Arch can
update Python, ROCm, the kernel — nothing breaks. *"You can't kill me. I'm already dead." — the stack, to pacman.*

## The Problem

Arch Linux rolling updates can:
- Bump Python 3.13 → 3.14 (breaks every venv on the system)
- Update ROCm runtime (breaks PyTorch wheels compiled for older versions)
- Update mesa/vulkan drivers (breaks GPU compute)
- Update the kernel (breaks GPU driver modules)

Any one of these kills your AI inference. On a server that's supposed to run 24/7,
that's not acceptable. *"You break it, you buy it." — except we have a receipt.*

## The Solution: Total Isolation

The AI stack owns its entire dependency chain. Nothing depends on system packages.

```
System Python (/usr/bin/python)     ← Arch manages this, we don't care
AI Python (/opt/python3.13/)        ← Compiled from source, we own it
AI Venv (/srv/ai/comfyui/.venv/)    ← Built on OUR Python, not system's
ROCm (/opt/rocm/)                   ← Compiled from source, we own it
PyTorch wheels                      ← Cached locally for offline rebuild
```

### Layer 1: Standalone Python

Python 3.13.3 is compiled from source and installed at `/opt/python3.13/`.
All AI virtual environments use this interpreter — not the system Python.

```bash
# The AI stack uses this:
/opt/python3.13/bin/python3.13 -m venv /srv/ai/comfyui/.venv

# NOT this:
/usr/bin/python3  # ← this is Arch's, it changes every update
```

### Layer 2: Package Pinning

Critical system packages are pinned in `/etc/pacman.conf`:

```
IgnorePkg = python python-pip
```

This means `pacman -Syu` will skip Python updates. When you're ready to update
Python, you do it deliberately — not as a surprise side effect.

### Layer 3: Pre-Update Backup Hook

A pacman hook at `/etc/pacman.d/hooks/ai-stack-backup.hook` automatically
snapshots your AI venv before any system update that touches Python, ROCm,
or the kernel. If something breaks, you have the receipt.

### Layer 4: Freeze & Thaw

Two commands give you full control:

#### `halo-freeze.sh` — Snapshot the working state

Run this whenever your stack is working perfectly:

```bash
halo-freeze.sh
```

This saves:
- Exact Python version
- All pip package versions (86+ packages, pinned to exact builds)
- PyTorch/ROCm wheel files cached locally (980MB, for offline rebuild)
- Git commit hashes for every source-built component
- System package versions for reference

#### `halo-thaw.sh` — Restore from snapshot

If an update breaks something:

```bash
halo-thaw.sh                    # restore latest snapshot
halo-thaw.sh 20260326_133905    # restore specific snapshot
```

This rebuilds the entire AI venv from cached wheels — no network needed.
Takes about 60 seconds. *"Great Scott!" — that fast.*

## What to Do Before a System Update

```bash
# 1. Freeze the current working state
halo-freeze.sh

# 2. Run the update
sudo pacman -Syu

# 3. Test the AI stack
python -c "import torch; print(torch.cuda.is_available())"

# 4. If it broke, thaw immediately
halo-thaw.sh
sudo systemctl restart halo-comfyui
```

## Current Frozen State

| Component | Version | Source |
|-----------|---------|--------|
| Python | 3.13.3 | Compiled from source (`/opt/python3.13/`) |
| PyTorch | 2.9.1+rocm7.11.0 | AMD gfx1151-native wheels |
| ROCm | 7.11.0 (bundled in wheels) | AMD official |
| ROCm runtime | 7.13.0 | Compiled from source (`/opt/rocm/`) |
| GPU arch | gfx1151 | AMD Radeon 8060S (Strix Halo iGPU) |
| ComfyUI | pinned commit | Source at `/srv/ai/comfyui/` |
| llama.cpp | pinned commit | Compiled from source |

## Philosophy

> Compile everything from source. Own the whole stack. Never let a package
> manager decide when your AI server goes down.

The system packages power the desktop and the OS. The AI stack at `/srv/ai/`
and `/opt/` is self-contained. Arch can roll all day long and nothing breaks.

## Weekly Source Compiles

Every week, the entire AI stack is recompiled from source. This isn't a panic
response — it's scheduled maintenance that keeps the stack current and proves
stability before anything goes to production.

**What gets compiled weekly:**
- llama.cpp (latest main)
- whisper.cpp (latest main)
- Kokoro TTS
- ComfyUI + custom nodes
- Open WebUI
- Vane (Perplexica)
- ROCm runtime (when upstream moves)
- Python (when upstream releases)

**Why this works:**
- Problems surface in a controlled environment, not in production at 2 AM
- Every compile is a stability test — if it builds and benchmarks clean, it ships
- We catch upstream breaking changes before they cascade
- The frozen snapshot is always from a verified-good compile, never a guess

**The cycle:**

```
Step 1: Pull latest source for all components
Step 2: Compile everything from source
Step 3: Run benchmarks (tok/s, latency, VRAM usage)
Step 4: If benchmarks match or beat previous — freeze, deploy, restart services
Step 5: If regression — rollback to last freeze, flag the upstream commit
```

This is why the stack runs at 87 tok/s and stays there. Weekly compiles aren't
overhead — they're the reason nothing breaks. *"The way is shut. It was made by those who are compiled, and the compiled keep it."*
