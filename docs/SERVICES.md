# Halo AI Services Reference

Detailed documentation for every service in the halo-ai stack. All services bind to `127.0.0.1` and are managed via systemd. *"I'm not locked in here with you. You're locked in here with me." — every service on localhost.*

---

## llama-server

LLM inference engine. The core of the stack -- all text generation flows through this service. *"The spice must flow."*

| Property | Value |
|----------|-------|
| **Port** | 8081 |
| **Binary** | `/srv/ai/llama-cpp/build-vulkan/bin/llama-server` (default) |
| **Systemd unit** | `halo-llama-server.service` |
| **Config file** | `/etc/systemd/system/halo-llama-server.service` (model path and flags are in ExecStart) |
| **Environment** | `/srv/ai/configs/rocm.env` |
| **Runs as** | User (with video, render groups) |

### Commands

```bash
sudo systemctl start halo-llama-server
sudo systemctl stop halo-llama-server
sudo systemctl restart halo-llama-server
journalctl -u halo-llama-server -f
```

### Health Check

```bash
curl -s http://127.0.0.1:8081/health
# Returns: {"status":"ok"}

# Quick inference test
curl -s http://127.0.0.1:8081/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"q","messages":[{"role":"user","content":"hello"}],"max_tokens":5}'
```

### Common Issues

- **Out of memory**: Model too large for available GTT. Check `ttm.pages_limit` kernel param is set to 30146560. Verify with: `dmesg | grep ttm`
- **GPU not found**: Ensure user is in `video` and `render` groups. Check `/dev/kfd` exists. Run `rocminfo | grep gfx1151`.
- **Slow startup**: Large models take 10-30 seconds to load into GPU memory. The watchdog waits before marking as failed.
- **Wrong backend**: The ExecStart line determines which backend (Vulkan/HIP/OpenCL) is active. Use `halo-driver-swap.sh status` to check.

### Dependencies

- None (base service). Lemonade depends on this.

---

## whisper-server

GPU-accelerated speech-to-text using whisper.cpp. Transcribes audio input to text.

| Property | Value |
|----------|-------|
| **Port** | 8082 |
| **Binary** | `/srv/ai/whisper-cpp/build/bin/whisper-server` |
| **Systemd unit** | `halo-whisper-server.service` |
| **Config file** | `/etc/systemd/system/halo-whisper-server.service` |
| **Environment** | `/srv/ai/configs/rocm.env` |
| **Model** | `/srv/ai/models/whisper-large-v3-turbo.bin` |
| **Runs as** | User (with video, render groups) |

### Commands

```bash
sudo systemctl start halo-whisper-server
sudo systemctl stop halo-whisper-server
sudo systemctl restart halo-whisper-server
journalctl -u halo-whisper-server -f
```

### Health Check

```bash
curl -s http://127.0.0.1:8082/health
```

### Common Issues

- **Model file missing**: Download whisper-large-v3-turbo.bin to `/srv/ai/models/`. The model is not included in the repo.
- **HIP build failure**: whisper.cpp is built with HIP only (not Vulkan). Requires ROCm at `/opt/rocm`.
- **High GPU memory usage**: whisper-large-v3-turbo uses several GB of GPU memory. May compete with llama-server for GTT.

### Dependencies

- None. Lemonade can route speech requests to this service.

---

## Lemonade

Unified AI API gateway. Provides OpenAI, Ollama, and Anthropic API compatibility through a single endpoint. Routes requests to llama-server, whisper, and Kokoro.

| Property | Value |
|----------|-------|
| **Port** | 8080 |
| **Binary** | `/srv/ai/lemonade/build/lemonade-router` |
| **Systemd unit** | `halo-lemonade.service` |
| **Config file** | `/etc/systemd/system/halo-lemonade.service` |
| **Environment** | `/srv/ai/configs/rocm.env` |
| **Runs as** | User (with video, render groups) |

### Commands

```bash
sudo systemctl start halo-lemonade
sudo systemctl stop halo-lemonade
sudo systemctl restart halo-lemonade
journalctl -u halo-lemonade -f
```

### Health Check

```bash
curl -s http://127.0.0.1:8080/v1/models
# Returns list of available models

curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"default","messages":[{"role":"user","content":"hello"}],"max_tokens":5}'
```

### Common Issues

- **502 errors**: llama-server is not running or not yet ready. Lemonade needs llama-server to be healthy before it can serve LLM requests.
- **Build failure**: Lemonade uses CMake presets. Run `cmake --preset default && cmake --build --preset default` from `/srv/ai/lemonade/`.

### Dependencies

- **halo-llama-server.service** (Wants + After): Lemonade routes LLM requests to llama-server on port 8081.

---

## Open WebUI

Full-featured chat interface with RAG, document upload, multi-model support, and user management.

| Property | Value |
|----------|-------|
| **Port** | 3000 |
| **Binary** | `/srv/ai/open-webui/.venv/bin/open-webui` |
| **Systemd unit** | `halo-open-webui.service` |
| **Config file** | `/etc/systemd/system/halo-open-webui.service` |
| **Data directory** | `/srv/ai/open-webui/data` |
| **Python** | 3.12 (venv at `/srv/ai/open-webui/.venv/`) |
| **Runs as** | User |

### Commands

```bash
sudo systemctl start halo-open-webui
sudo systemctl stop halo-open-webui
sudo systemctl restart halo-open-webui
journalctl -u halo-open-webui -f
```

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/
# Returns: 200
```

### Common Issues

- **Cannot connect to LLM**: Open WebUI uses `OLLAMA_BASE_URL=http://localhost:8080` (Lemonade). Ensure both Lemonade and llama-server are running.
- **Database locked**: SQLite concurrency issue. Restart the service. Persistent data is in `/srv/ai/open-webui/data/`.
- **Python dependency conflict**: Open WebUI requires Python 3.12 specifically. The venv uses `/opt/python312/bin/python3.12`.
- **First-run setup**: On first access, you must create an admin account through the web UI.

### Dependencies

- **halo-lemonade.service** (After): Connects to Lemonade as its LLM backend.
- **halo-qdrant.service** (optional): Used for RAG vector storage.

---

## n8n

Workflow automation platform with 400+ integrations. Can connect to Lemonade for AI-powered workflows.

| Property | Value |
|----------|-------|
| **Port** | 5678 |
| **Binary** | `/usr/local/bin/node /srv/ai/n8n/packages/cli/bin/n8n` |
| **Systemd unit** | `halo-n8n.service` |
| **Config file** | `/etc/systemd/system/halo-n8n.service` |
| **Data directory** | `/srv/ai/n8n/data` |
| **Runs as** | User |

### Commands

```bash
sudo systemctl start halo-n8n
sudo systemctl stop halo-n8n
sudo systemctl restart halo-n8n
journalctl -u halo-n8n -f
```

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5678/healthz
# Returns: 200
```

### Common Issues

- **Port conflict**: n8n defaults to 5678. If something else uses that port, change `N8N_PORT` in the service unit.
- **pnpm build failure**: Rebuild with `cd /srv/ai/n8n && pnpm install --frozen-lockfile && pnpm build`.
- **Workflow data loss**: Workflow definitions and credentials are stored in `/srv/ai/n8n/data/`. Included in nightly backups.

### Dependencies

- None (standalone). Workflows can optionally call Lemonade API at `http://localhost:8080`.

---

## ComfyUI

Node-based image generation pipeline. Runs Stable Diffusion models on the AMD GPU via ROCm PyTorch.

| Property | Value |
|----------|-------|
| **Port** | 8188 |
| **Binary** | `/srv/ai/comfyui/.venv/bin/python main.py` |
| **Systemd unit** | `halo-comfyui.service` |
| **Config file** | `/etc/systemd/system/halo-comfyui.service` |
| **Working directory** | `/srv/ai/comfyui` |
| **Environment** | `/srv/ai/configs/rocm.env` |
| **Python** | 3.13 (venv at `/srv/ai/comfyui/.venv/`) |
| **Runs as** | User (with video, render groups) |

### Commands

```bash
sudo systemctl start halo-comfyui
sudo systemctl stop halo-comfyui
sudo systemctl restart halo-comfyui
journalctl -u halo-comfyui -f
```

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8188/
# Returns: 200
```

### Common Issues

- **PyTorch ROCm mismatch**: ComfyUI uses PyTorch built for ROCm 6.2.4. If ROCm is updated, PyTorch may need to be reinstalled: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2.4`
- **Out of GPU memory**: Image generation models compete with LLM models for GPU memory. Consider stopping llama-server for large image generation jobs.
- **Missing models**: Stable Diffusion checkpoints must be placed in `/srv/ai/comfyui/models/checkpoints/`.

### Dependencies

- None (standalone). Accessed via Caddy at `/comfyui/*`.

---

## SearXNG

Privacy-respecting meta-search engine. Aggregates results from multiple public search engines without tracking.

| Property | Value |
|----------|-------|
| **Port** | 8888 |
| **Binary** | `/srv/ai/searxng/.venv/bin/python -m searx.webapp` |
| **Systemd unit** | `halo-searxng.service` |
| **Config file** | `/srv/ai/configs/searxng/settings.yml` |
| **Environment** | `SEARXNG_SETTINGS_PATH=/srv/ai/configs/searxng/settings.yml` |
| **Runs as** | User |

### Commands

```bash
sudo systemctl start halo-searxng
sudo systemctl stop halo-searxng
sudo systemctl restart halo-searxng
journalctl -u halo-searxng -f
```

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8888/
# Returns: 200

# Test search
curl -s "http://127.0.0.1:8888/search?q=test&format=json" | head -c 200
```

### Common Issues

- **Secret key not set**: The default `settings.yml` has a placeholder. The installer replaces it with a random key. If you see errors about the secret key, regenerate with `openssl rand -hex 32` and update `settings.yml`.
- **Rate limited by upstream**: SearXNG queries public search engines. If too many requests are made, upstream engines may temporarily block. This is normal and resolves itself.

### Dependencies

- None (standalone). Vane depends on this for deep research queries.

---

## Qdrant

High-performance vector database compiled from Rust. Stores embeddings for RAG (Retrieval-Augmented Generation).

| Property | Value |
|----------|-------|
| **Port** | 6333 |
| **Binary** | `/srv/ai/qdrant/target/release/qdrant` |
| **Systemd unit** | `halo-qdrant.service` |
| **Config file** | `/srv/ai/configs/qdrant.yaml` (referenced in ExecStart) |
| **Storage** | `/srv/ai/qdrant/storage/` |
| **Runs as** | User |

### Commands

```bash
sudo systemctl start halo-qdrant
sudo systemctl stop halo-qdrant
sudo systemctl restart halo-qdrant
journalctl -u halo-qdrant -f
```

### Health Check

```bash
curl -s http://127.0.0.1:6333/healthz
# Returns: {"title":"qdrant - vectorass engine","version":"..."}

curl -s http://127.0.0.1:6333/collections
# Returns list of vector collections
```

### Common Issues

- **Slow Rust compilation**: Initial `cargo build --release` takes a long time. This is expected.
- **Storage growth**: Vector data in `/srv/ai/qdrant/storage/` can grow large with many documents. Monitor disk usage.
- **Config not found**: Ensure `/srv/ai/configs/qdrant.yaml` exists and is readable.

### Dependencies

- None (standalone). Open WebUI uses Qdrant for RAG embeddings.

---

## Dashboard API

GPU metrics and service health monitoring API. Forked from DreamServer. Reads GPU temperature, memory usage, and service status.

| Property | Value |
|----------|-------|
| **Port** | 3002 |
| **Binary** | `/srv/ai/dashboard-api/.venv/bin/uvicorn main:app` |
| **Systemd unit** | `halo-dashboard-api.service` |
| **Config file** | `/etc/systemd/system/halo-dashboard-api.service` |
| **Data directory** | `/srv/ai/dashboard-api/data/` |
| **API key** | `/srv/ai/dashboard-api/data/dashboard-api-key.txt` |
| **Runs as** | User (with video, render groups) |

### Commands

```bash
sudo systemctl start halo-dashboard-api
sudo systemctl stop halo-dashboard-api
sudo systemctl restart halo-dashboard-api
journalctl -u halo-dashboard-api -f
```

### Health Check

```bash
curl -s http://127.0.0.1:3002/health
# or
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3002/
```

### Common Issues

- **API key missing**: The installer generates a key at `/srv/ai/dashboard-api/data/dashboard-api-key.txt`. If missing, generate with `openssl rand -base64 32`.
- **GPU metrics unavailable**: Requires user to be in `video` and `render` groups. Needs access to `/sys/class/drm/` and `/dev/kfd`.

### Dependencies

- None (standalone). Dashboard UI connects to this.

---

## Dashboard UI

Web frontend for the GPU metrics dashboard. Displays real-time GPU stats, service health, and system information. Forked from DreamServer.

| Property | Value |
|----------|-------|
| **Port** | 3003 |
| **Binary** | `/usr/local/bin/node node_modules/.bin/vite preview` |
| **Systemd unit** | `halo-dashboard-ui.service` |
| **Config file** | `/etc/systemd/system/halo-dashboard-ui.service` |
| **Working directory** | `/srv/ai/dashboard-ui` |
| **Runs as** | User |

### Commands

```bash
sudo systemctl start halo-dashboard-ui
sudo systemctl stop halo-dashboard-ui
sudo systemctl restart halo-dashboard-ui
journalctl -u halo-dashboard-ui -f
```

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3003/
# Returns: 200
```

### Common Issues

- **Blank page**: Dashboard API must be running for the UI to display data. Start `halo-dashboard-api` first.
- **Vite build stale**: If the UI shows old data or errors, rebuild: `cd /srv/ai/dashboard-ui && npm run build`.

### Dependencies

- **halo-dashboard-api.service** (After): The UI fetches all data from the API on port 3002.

---

## Caddy

Reverse proxy with automatic TLS. The only service that listens on a network-facing port (443). Protects all web services with basic authentication. *"I am the keymaster. Are you the gatekeeper?"*

| Property | Value |
|----------|-------|
| **Port** | 443 (HTTPS) |
| **Binary** | `/usr/local/bin/caddy` |
| **Systemd unit** | `halo-caddy.service` |
| **Config file** | `/srv/ai/configs/Caddyfile` |
| **TLS certificates** | `/var/lib/caddy/.local/share/caddy/pki/authorities/local/` |
| **Runs as** | User (with `CAP_NET_BIND_SERVICE` for port 443) |

### Commands

```bash
sudo systemctl start halo-caddy
sudo systemctl stop halo-caddy
sudo systemctl restart halo-caddy
sudo systemctl reload halo-caddy    # Reload config without downtime
journalctl -u halo-caddy -f
```

### Health Check

```bash
curl -sk https://127.0.0.1/ -o /dev/null -w "%{http_code}"
# Returns: 401 (basic auth required) or 200 (with credentials)

curl -sk -u admin:YourPassword https://127.0.0.1/ -o /dev/null -w "%{http_code}"
# Returns: 200
```

### Route Map

| Path | Backend |
|------|---------|
| `/chat/*` | Open WebUI :3000 |
| `/research/*` | Vane :3001 |
| `/workflows/*` | n8n :5678 |
| `/api/*` | Lemonade :8080 |
| `/comfyui/*` | ComfyUI :8188 |
| `/` (default) | Open WebUI :3000 |

### Common Issues

- **Certificate warnings**: Caddy uses an internal CA. Export and install the root certificate on client devices (see README for instructions).
- **Password reset**: Generate a new hash with `caddy hash-password --plaintext 'newpassword'` and update the Caddyfile.
- **Cannot bind port 443**: The service unit grants `CAP_NET_BIND_SERVICE`. If it still fails, check if another process is using port 443.
- **Config syntax error**: Validate with `caddy validate --config /srv/ai/configs/Caddyfile` before reloading.

### Dependencies

- None directly, but all backend services should be running for routes to work. Caddy will return 502 for any stopped backend.

---

## Vane

Deep research engine (Perplexica fork). Takes a research question, searches the web via SearXNG, gathers context, and uses the LLM to synthesize a cited answer.

| Property | Value |
|----------|-------|
| **Port** | 3001 |
| **Binary** | `/usr/local/bin/node /srv/ai/vane/.next/standalone/server.js` |
| **Systemd unit** | `halo-vane.service` |
| **Config file** | `/etc/systemd/system/halo-vane.service` |
| **Working directory** | `/srv/ai/vane` |
| **Environment** | `SEARXNG_API_URL=http://localhost:8888` |
| **Runs as** | User |

### Commands

```bash
sudo systemctl start halo-vane
sudo systemctl stop halo-vane
sudo systemctl restart halo-vane
journalctl -u halo-vane -f
```

### Health Check

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/
# Returns: 200
```

### Common Issues

- **No search results**: SearXNG must be running. Vane queries `http://localhost:8888` for web search results.
- **LLM timeouts**: Deep research sends large context to the LLM. If llama-server is slow or down, Vane will time out.
- **Build failure**: Vane uses yarn. Rebuild with `cd /srv/ai/vane && yarn install && yarn build`.

### Dependencies

- **halo-searxng.service** (After): Web search backend.
- **halo-lemonade.service** (After): LLM API for synthesis.

---

## Kokoro

High-quality text-to-speech API. Converts text responses to spoken audio. *54 voices — "These go to eleven."*

| Property | Value |
|----------|-------|
| **Port** | 8083 |
| **Binary** | `/srv/ai/kokoro/.venv/bin/uvicorn` (or similar FastAPI entry) |
| **Systemd unit** | Not in the default service selection menu (manual setup) |
| **Working directory** | `/srv/ai/kokoro` |
| **Python** | 3.13 (venv at `/srv/ai/kokoro/.venv/`) |
| **Runs as** | User |

### Commands

```bash
# If a systemd unit is created:
sudo systemctl start halo-kokoro
sudo systemctl stop halo-kokoro
sudo systemctl restart halo-kokoro

# Manual start:
cd /srv/ai/kokoro && .venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8083
```

### Health Check

```bash
curl -s http://127.0.0.1:8083/health
# or
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8083/
```

### Common Issues

- **PyTorch ROCm version**: Kokoro uses PyTorch for ROCm 6.2.4. If ROCm changes, reinstall PyTorch.
- **spaCy model missing**: Run `.venv/bin/python -m spacy download en_core_web_sm` if you see spaCy errors.
- **No systemd unit shipped**: Kokoro is installed but does not have a dedicated service file in the default set. You may need to create one manually or start it through another mechanism.

### Dependencies

- None (standalone). Lemonade can route TTS requests to Kokoro.

---

## Agent

Autonomous service guardian. Runs continuously, monitors all services every 30 seconds, auto-restarts failures, monitors GPU health and thermals, and tracks inference performance. Takes Btrfs snapshots before any repair action. *"I am always watching, Wazowski. Always watching."*

| Property | Value |
|----------|-------|
| **Port** | None (not a web service) |
| **Binary** | `/usr/bin/python3 /srv/ai/agent/halo-agent.py` |
| **Systemd unit** | `halo-agent.service` |
| **Config file** | `/etc/systemd/system/halo-agent.service` |
| **Runs as** | root (needs to restart other services) |
| **Watchdog** | 120 second systemd watchdog |

### Commands

```bash
sudo systemctl start halo-agent
sudo systemctl stop halo-agent
sudo systemctl restart halo-agent
journalctl -u halo-agent -f
journalctl -t halo-agent      # Filter by syslog identifier
```

### Health Check

```bash
systemctl is-active halo-agent
# Returns: active

systemctl status halo-agent
# Shows uptime, memory usage, last log lines
```

### Common Issues

- **Agent restarting repeatedly**: Check `journalctl -u halo-agent` for Python errors. The agent uses `Restart=always` with 10 second delay.
- **Watchdog timeout**: If the agent does not send a watchdog ping within 120 seconds, systemd kills and restarts it.
- **Cannot restart services**: Agent runs as root. If it cannot restart services, check systemd unit file permissions.

### Dependencies

- **halo-llama-server.service** (Wants): Monitors this service.
- **halo-lemonade.service** (Wants): Monitors this service.

---

## Watchdog

Periodic health check script. Runs as a oneshot service triggered by a timer every 5 minutes. Checks services, GPU, disk, memory, and available updates.

| Property | Value |
|----------|-------|
| **Port** | None (not a web service) |
| **Script** | `/srv/ai/scripts/halo-watchdog.sh` |
| **Systemd unit** | `halo-watchdog.service` (oneshot) |
| **Timer** | `halo-watchdog.timer` (every 5 min, first at 2 min after boot) |
| **Log file** | `/var/log/halo-watchdog.log` |
| **Runs as** | root |

### Commands

```bash
# The timer triggers the service automatically
sudo systemctl start halo-watchdog.timer    # Enable periodic checks
sudo systemctl stop halo-watchdog.timer     # Disable periodic checks

# Run manually
sudo systemctl start halo-watchdog.service

# View logs
journalctl -u halo-watchdog -f
cat /var/log/halo-watchdog.log
```

### Health Checks Performed

1. **Service health**: Checks all halo services are active. Auto-restarts failed services (with Btrfs snapshot first).
2. **GPU health**: Verifies `/dev/kfd` exists, `amdgpu` module is loaded, GPU temperature is below 85C.
3. **Disk usage**: Warns if `/srv/ai` is above 90% full.
4. **Memory**: Warns if available RAM drops below 4GB.
5. **Update check**: Fetches upstream repos and reports available updates. Checks pacman system updates and kernel version.

### Common Issues

- **Log file growing**: `/var/log/halo-watchdog.log` is not rotated by default. Set up logrotate or periodically truncate.
- **Snapshot failures**: If Btrfs snapper is not configured, snapshot commands fail silently (by design).

### Dependencies

- None. Monitors all other services.

---

## Backup

Nightly backup utility. Takes snapshots of configuration files, application data, databases, and systemd units. Generates SHA256 manifests and rotates old backups.

| Property | Value |
|----------|-------|
| **Port** | None (not a web service) |
| **Script** | `/srv/ai/scripts/halo-backup.sh` |
| **Systemd unit** | `halo-backup.service` (oneshot) |
| **Timer** | `halo-backup.timer` (daily with 30 min random delay) |
| **Backup destination** | `/srv/ai/backups/` |
| **Log file** | `/srv/ai/logs/backup.log` |
| **Retention** | 7 daily backups |
| **Runs as** | User |

### What Gets Backed Up

- `/srv/ai/configs/` (all configuration files)
- `/srv/ai/dashboard-api/data/` (API key, metrics)
- `/srv/ai/n8n/data/` and `/srv/ai/n8n/.n8n/` (workflows, credentials)
- `/srv/ai/open-webui/*.db`, `*.sqlite`, and `/srv/ai/open-webui/data/` (chat history, users)
- `/srv/ai/qdrant/storage/` (vector embeddings)
- `/etc/systemd/system/halo-*` (all systemd service files)

### Commands

```bash
# Run manually
/srv/ai/scripts/halo-backup.sh /srv/ai/backups

# Or via systemd
sudo systemctl start halo-backup.service

# Enable/disable nightly timer
sudo systemctl enable halo-backup.timer
sudo systemctl disable halo-backup.timer

# View backup log
cat /srv/ai/logs/backup.log
```

### Common Issues

- **Disk space**: Backups can be large, especially with Qdrant storage. Monitor `/srv/ai/backups/` size.
- **Off-machine sync**: Backups stay local by default. Use `rsync -az /srv/ai/backups/ user@remote:/backups/halo-ai/` to sync to another machine.
- **Permissions**: The backup script runs as the regular user. It cannot back up files owned by root unless permissions allow.

### Dependencies

- None. Runs independently of all services.

---

### Meek (Security Agent)

- **Purpose**: Autonomous security monitoring with the Reflex agent group
- **Schedule**: Continuous monitoring + daily full scans
- **Config**: /srv/ai/meek/
- **Reports**: /srv/ai/meek/reports/
- **Agents**: Pulse, Ghost, Gate, Shadow, Fang, Mirror, Vault, Net, Shield
- **Commands**: `meek scan`, `meek status`, `meek report`, `meek watch`
- **Systemd**: meek-watch.service (continuous), meek-scan.timer (daily at 06:00)
- **Recommendation**: Enabled by default for continuous security monitoring
