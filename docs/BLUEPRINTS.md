# Halo AI — Blueprints

Implementation plans for the next evolution of halo-ai. Each blueprint is a standalone deliverable. *"Roads? Where we're going, we don't need roads."*

---

## BP-01: Unified `halo` CLI

**Priority:** Critical
**Effort:** 1 session
**Files:** `scripts/halo` (single entry point)

One command. Tab-completable. Replaces all standalone scripts. *"One ring to rule them all."*

```
halo status                    # full system overview
halo services                  # all services, green/red/yellow
halo agents                    # all 14 agents at a glance
halo agents install <name>     # add a Lego block
halo agents remove <name>      # pull one out
halo models list               # available + installed models
halo models use <name>         # swap model (auto-restarts llama-server)
halo models download <name>    # pull from HuggingFace
halo driver <vulkan|hip|opencl> # swap GPU backend
halo freeze                    # snapshot the stack
halo thaw [timestamp]          # restore from snapshot
halo update                    # safe update with rollback
halo backup                    # run backup now
halo fan <quiet|balanced|max>  # fan profile
halo fan curve 70,78,85,92,97  # custom curve
halo password                  # change Caddy password
halo logs <service|agent>      # tail logs
halo bench                     # quick benchmark
halo vpn add-client <name>     # WireGuard client
halo uninstall                 # clean removal
```

**Implementation:**
- Single bash script with subcommand routing (case statement)
- Calls existing scripts internally — no rewrite, just unified interface
- Install to `/usr/local/bin/halo`
- Bash completion file at `/etc/bash_completion.d/halo`
- ZSH completion at `/usr/share/zsh/site-functions/_halo`
- Colored output, step counters, branded banners (existing style)
- `halo --version` shows stack version, kernel, GPU, model, speed

---

## BP-02: `halo status` — Single-Glance Dashboard

**Priority:** Critical
**Effort:** 1 session
**Part of:** BP-01

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  halo-ai status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Inference    109.2 tok/s   Qwen3-30B-A3B     ✓
  Backend      Vulkan (RADV)                    ✓
  GPU          35°C          Radeon 8060S       ✓
  Memory       27 / 128 GB   (79% free)        ✓
  Disk         45%           /srv/ai            ✓
  Uptime       4d 12h 33m                       ✓

  Services     11/13 active
    ✓ llama  webui  vane  searxng  qdrant  n8n  comfyui  caddy
    ✓ gaia-api  gaia-mcp
    ✗ lemonade  whisper

  Agents       14/14 active
    ✓ halo  echo  meek  amp  bounty
    ✓ pulse  ghost  gate  shadow  fang  mirror  vault  net  shield

  Fan          quiet (fan1: off, fan2: off, fan3: 500rpm)
  Updates      3 packages, 2 repos behind
  Last backup  2h ago (vault: healthy)
  Snapshot     #108 (pre-audit-redeploy)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Data sources:**
- Inference speed: `curl localhost:8081/v1/chat/completions` quick probe
- GPU temp: `/sys/class/hwmon/*/temp1_input`
- Memory: `/proc/meminfo`
- Disk: `df /srv/ai`
- Services: `systemctl is-active`
- Agents: `systemctl is-active halo-{name}`
- Fan: `/sys/class/ec_su_axb35/fan*/rpm`
- Updates: `pacman -Qu | wc -l` + git fetch counts
- Backup: check `/srv/ai/backups/` newest dir age
- Snapshot: `snapper list | tail -1`

---

## BP-03: First-Run Wizard (Web)

**Priority:** High
**Effort:** 2 sessions
**Files:** `dashboard-ui/src/pages/Setup.jsx`, `dashboard-api/routers/setup.py`

When a fresh install opens `https://strixhalo` for the first time:

**Step 1 — Secure Your Server**
- Force password change (don't let them skip)
- Show the hash update live
- "Your server is now locked."

**Step 2 — Meet Your Hardware**
- Auto-detect: GPU, VRAM, CPU cores, RAM, disk
- Show what was detected
- "128GB unified memory. 115GB GPU-addressable. 40 CUs."

**Step 3 — Choose Your Model**
- Show model catalog with speed/size/quality ratings
- Default: Qwen3-30B-A3B (recommended for your hardware)
- One-click download + activate

**Step 4 — First Conversation**
- Embedded chat widget
- "Ask me anything. I'm running at 109 tok/s on your hardware."
- User sees it work. That's the moment. *"Whoa."*

**Step 5 — Meet the Family**
- Show the family SVG
- Brief intro to each agent
- Toggle agents on/off (Lego blocks)
- "Your AI team is ready."

**Step 6 — Done**
- Redirect to main dashboard
- Mark setup complete (won't show again)

---

## BP-04: Hardware Auto-Detection

**Priority:** High
**Effort:** 1 session
**Files:** `scripts/halo-detect.sh`, called by `install.sh`

Detect and auto-configure:

| Hardware | Detection | Auto-Config |
|----------|-----------|-------------|
| Strix Halo (gfx1151) | `lspci \| grep gfx1151` | ROCm env, GPU memory params, ttm.pages_limit |
| Scarlett Solo 4th Gen | `lsusb \| grep 1235:8218` | ALSA routing, no-suspend, fan control |
| Stream Deck | `lsusb \| grep 0fd9` | udev rules, key mapping service |
| LAN subnet | `ip route` | nftables rules (replace xxx.xxx.xxx.0/24) |
| Fan controller | `/sys/class/ec_su_axb35/` | Load module, apply quiet curve |
| BIOS power mode | `/sys/class/ec_su_axb35/apu/power_mode` | Set to performance |
| NVMe drives | `lsblk` | Detect available storage for models |

Output: `/srv/ai/configs/hardware.json` — detected hardware manifest.
Installer reads this and skips prompts for detected hardware.

---

## BP-05: Agent Dashboard Feed

**Priority:** Medium
**Effort:** 1 session
**Files:** `dashboard-api/routers/agents.py`, `dashboard-ui/src/pages/Agents.jsx`

Live feed in the web dashboard showing agent activity:

```
[pulse]   All vitals normal — 35°C, 79% memory free         2m ago
[gate]    Firewall locked — nftables active, 0 exposed ports 5m ago
[ghost]   Scan complete — no secrets found                   1h ago
[shadow]  Integrity check passed — 3 files monitored         10m ago
[fang]    No intrusion attempts detected                     2m ago
[vault]   Last backup: 2h ago, 3.2GB, SHA256 verified        1h ago
[meek]    All 9 Reflex agents reporting healthy               1m ago
[halo]    11/13 services active. 2 need attention.           30s ago
```

Each agent writes to a shared JSON log at `/srv/ai/agent/data/feed.json`. Dashboard polls it. Color-coded by agent. Clickable to see details.

---

## BP-06: Offline Model Pack

**Priority:** Medium
**Effort:** 1 session
**Files:** `scripts/halo-models.sh` (add `pack` and `load` subcommands)

```bash
# On a machine with internet:
halo models pack qwen3-30b-a3b    # downloads + creates USB-ready archive

# On air-gapped machine:
halo models load /mnt/usb/halo-models-qwen3-30b-a3b.tar
```

For the privacy pitch — full stack setup with zero internet after initial install.

---

## BP-07: Vault ↔ Backup Integration

**Priority:** Medium
**Effort:** 1 session

Vault agent becomes the backup system:
- Runs `halo-backup.sh` on schedule
- Verifies SHA256 manifests
- Reports in the agent feed
- Alerts if backup is stale or verification fails
- Tracks backup history in its state file
- Dashboard shows backup health in Vault's card

---

## Build Order

```
Phase 1 (next session):
  BP-01  halo CLI          — unified entry point
  BP-02  halo status       — single-glance dashboard

Phase 2 (following session):
  BP-03  First-run wizard  — out-of-box experience
  BP-04  Hardware detect   — auto-configure everything

Phase 3 (polish):
  BP-05  Agent feed        — live dashboard activity
  BP-06  Offline models    — air-gapped installs
  BP-07  Vault integration — backup through agents
```

---

*These blueprints are the path from "impressive stack" to "product people fight over." "Inconceivable!" No — just not built yet.*
