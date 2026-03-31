#!/usr/bin/env python3
"""man-cave — the halo-ai control center."""

# stdlib
import asyncio
import json
import logging
import os
import random
import re
import subprocess
import tempfile
import time as _time
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

# third-party
import httpx
import psutil
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- Logging ---
logger = logging.getLogger("man-cave")
logging.basicConfig(level=logging.INFO)

# --- Paths (absolute, relative to this file) ---
_BASE_DIR = Path(__file__).parent
_STATIC_DIR = _BASE_DIR / "static"
_TEMPLATES_DIR = _BASE_DIR / "templates"

# --- Shared httpx client (created/closed via lifespan) ---
_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Return the shared httpx client."""
    assert _http_client is not None, "httpx client not initialised"
    return _http_client


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _http_client, agent_chatter_task, _debrief_task
    _http_client = httpx.AsyncClient(timeout=30.0)
    agent_chatter_task = asyncio.create_task(agent_chatter_loop())
    _debrief_task = asyncio.create_task(midnight_debrief())
    yield
    # Shutdown
    agent_chatter_task.cancel()
    _debrief_task.cancel()
    try:
        await agent_chatter_task
    except asyncio.CancelledError:
        pass
    try:
        await _debrief_task
    except asyncio.CancelledError:
        pass
    await _http_client.aclose()
    _http_client = None


app = FastAPI(title="man-cave", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

# --- halo-ai service definitions ---
SERVICES = [
    {"name": "llama-server", "unit": "halo-llama-server", "port": 8081, "health": "http://127.0.0.1:8081/health"},
    {"name": "lemonade", "unit": "halo-lemonade", "port": 8080, "health": "http://127.0.0.1:8080/live"},
    {"name": "open-webui", "unit": "halo-open-webui", "port": 3000, "health": "http://127.0.0.1:3000"},
    {"name": "vane", "unit": "halo-vane", "port": 3001, "health": None},
    {"name": "comfyui", "unit": "halo-comfyui", "port": 8188, "health": "http://127.0.0.1:8188/system_stats"},
    {"name": "searxng", "unit": "halo-searxng", "port": 8888, "health": None},
    {"name": "qdrant", "unit": "halo-qdrant", "port": 6333, "health": "http://127.0.0.1:6333/healthz"},
    {"name": "n8n", "unit": "halo-n8n", "port": 5678, "health": None},
    {"name": "whisper", "unit": "halo-whisper-server", "port": 8082, "health": None},
    {"name": "caddy", "unit": "halo-caddy", "port": 80, "health": None},
    {"name": "gaia", "unit": "halo-gaia-api", "port": 8090, "health": "http://127.0.0.1:8090/health"},
    {"name": "opencl", "unit": "halo-opencl", "port": None, "health": None},
    {"name": "prometheus", "unit": "prometheus", "port": 9090, "health": "http://127.0.0.1:9090/-/healthy"},
    {"name": "grafana", "unit": "grafana-server", "port": 3030, "health": "http://127.0.0.1:3030/api/health"},
    {"name": "node-exporter", "unit": "node_exporter", "port": 9100, "health": None},
    {"name": "home-assistant", "unit": "home-assistant", "port": 8123, "health": None},
]


async def get_service_status(svc):
    """Check systemd service status and optional health endpoint."""
    result = {"name": svc["name"], "unit": svc["unit"], "port": svc["port"]}

    # systemd status — use full path to avoid PATH issues
    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/systemctl", "is-active", f"{svc['unit']}.service",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        result["systemd"] = stdout.decode().strip()
    except Exception as e:
        result["systemd"] = "unknown"

    # health check
    if svc.get("health"):
        try:
            client = _get_client()
            resp = await client.get(svc["health"], timeout=3.0)
            result["health"] = "ok" if resp.status_code == 200 else f"http {resp.status_code}"
        except Exception:
            result["health"] = "unreachable"
    else:
        result["health"] = "n/a"

    result["status"] = "running" if result["systemd"] == "active" else result["systemd"]
    return result


async def get_gpu_stats():
    """Get GPU stats from ROCm SMI (text parsing) and sysfs."""
    stats = {}

    # Read everything from sysfs — no rocm-smi dependency
    try:
        for hwmon in Path("/sys/class/hwmon").iterdir():
            name_file = hwmon / "name"
            if name_file.exists() and "amdgpu" in name_file.read_text():
                temp1 = hwmon / "temp1_input"
                if temp1.exists():
                    stats["gpu_temp"] = str(int(temp1.read_text().strip()) // 1000)
                power = hwmon / "power1_average"
                if power.exists():
                    stats["gpu_power"] = f"{int(power.read_text().strip()) / 1000000:.1f}W"
                break
    except Exception:
        pass

    gpu_dev = Path("/sys/class/drm/card0/device")
    try:
        vt = gpu_dev / "mem_info_vram_total"
        vu = gpu_dev / "mem_info_vram_used"
        gb = gpu_dev / "gpu_busy_percent"
        if vt.exists():
            stats["vram_total"] = int(vt.read_text().strip())
            stats["vram_used"] = int(vu.read_text().strip())
        if gb.exists():
            stats["gpu_util"] = gb.read_text().strip()
    except Exception:
        pass

    # System memory
    mem = psutil.virtual_memory()
    stats["ram_total_gb"] = round(mem.total / 1e9, 1)
    stats["ram_used_gb"] = round(mem.used / 1e9, 1)
    stats["ram_percent"] = mem.percent
    # FIX #2: non-blocking cpu_percent
    stats["cpu_percent"] = await asyncio.to_thread(psutil.cpu_percent, interval=0.5)
    stats["load_avg"] = os.getloadavg()[0]

    return stats


async def get_python_info():
    """Get Python version info for the AI stack."""
    info = {}
    try:
        proc = await asyncio.create_subprocess_exec(
            "/opt/python3.13/bin/python3.13", "--version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        info["standalone"] = stdout.decode().strip()
    except Exception:
        info["standalone"] = "not found"

    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/python3", "--version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        info["system"] = stdout.decode().strip()
    except Exception:
        info["system"] = "not found"

    # Check freeze status
    freeze_dir = "/srv/ai/freeze"
    if os.path.exists(freeze_dir):
        snapshots = sorted([d for d in os.listdir(freeze_dir) if d != "latest"], reverse=True)
        info["freeze_count"] = len(snapshots)
        info["last_freeze"] = snapshots[0] if snapshots else "never"
        info["snapshots"] = snapshots[:10]  # Show last 10
    else:
        info["freeze_count"] = 0
        info["last_freeze"] = "never"
        info["snapshots"] = []

    # ROCm version
    try:
        rocm_ver = open("/opt/rocm/.info/version").read().strip()
        info["rocm"] = rocm_ver
    except Exception:
        info["rocm"] = "?"

    # Kernel
    info["kernel"] = os.uname().release

    # Full stack component list
    components = []

    def _git_ver(path):
        try:
            r = subprocess.run(["git", "-C", path, "log", "--oneline", "-1"],
                               capture_output=True, text=True, timeout=5)
            return r.stdout.strip()[:40] if r.returncode == 0 else "?"
        except Exception:
            return "?"

    def _svc_status(name):
        try:
            r = subprocess.run(["systemctl", "is-active", name],
                               capture_output=True, text=True, timeout=5)
            return "ok" if r.stdout.strip() == "active" else "error"
        except Exception:
            return "unknown"

    # Compiled-from-source components — the stuff freeze/thaw protects
    def _binary_date(path):
        try:
            mtime = os.path.getmtime(path)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "?"

    compiled_items = [
        ("llama.cpp", "/srv/ai/llama-cpp", "/srv/ai/llama-cpp/build-hip/bin/llama-server"),
        ("whisper.cpp", "/srv/ai/whisper-cpp", "/srv/ai/whisper-cpp/build/bin/whisper-server"),
        ("lemonade", "/srv/ai/lemonade", "/srv/ai/lemonade/build/lemonade-router"),
        ("open webui", "/srv/ai/open-webui", None),
        ("vane", "/srv/ai/vane", None),
        ("comfyui", "/srv/ai/comfyui", None),
        ("kokoro", "/srv/ai/kokoro", None),
        ("searxng", "/srv/ai/searxng", None),
        ("n8n", "/srv/ai/n8n", None),
        ("qdrant", "/srv/ai/qdrant", None),
        ("gaia", "/srv/ai/gaia", None),
        ("caddy", "/srv/ai/caddy", "/usr/bin/caddy"),
    ]

    for name, src_path, binary_path in compiled_items:
        ver = _git_ver(src_path) if src_path else "?"
        compiled = _binary_date(binary_path) if binary_path else ""
        # Check if source is ahead of binary (needs recompile)
        status = "ok"
        if binary_path and src_path:
            try:
                src_mtime = os.path.getmtime(src_path + "/.git/FETCH_HEAD")
                bin_mtime = os.path.getmtime(binary_path)
                if src_mtime > bin_mtime:
                    status = "stale"  # source updated, binary not recompiled
            except Exception:
                pass
        components.append({
            "name": name,
            "version": ver,
            "compiled": compiled,
            "status": status,
        })

    # System-level frozen components (not git, but protected by freeze/thaw)
    components.append({"name": "rocm", "version": info["rocm"], "compiled": "", "status": "ok"})
    components.append({"name": "kernel", "version": info["kernel"], "compiled": "", "status": "ok"})
    components.append({"name": "ai python", "version": info.get("standalone", "?"), "compiled": "", "status": "ok"})
    components.append({"name": "mesa / vulkan", "version": "", "compiled": "", "status": "ok"})
    components.append({"name": "pytorch", "version": "", "compiled": "", "status": "ok"})

    info["stack_components"] = components

    # Enrich snapshots with dates
    enriched_snapshots = []
    for snap_name in info.get("snapshots", []):
        date_str = ""
        try:
            parts = snap_name.split("_")
            if len(parts) >= 2 and len(parts[0]) == 8:
                date_str = f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:8]} {parts[1][:2]}:{parts[1][2:4]}"
        except Exception:
            pass
        enriched_snapshots.append({"name": snap_name, "date": date_str})
    info["snapshots"] = enriched_snapshots

    return info


async def get_lemonade_info():
    """Get Lemonade API / llama-server model info."""
    info = {}
    client = _get_client()
    try:
        resp = await client.get("http://127.0.0.1:8081/v1/models", timeout=3.0)
        data = resp.json()
        models = data.get("data", [])
        if models:
            info["model"] = models[0].get("id", "unknown")
        else:
            info["model"] = "none loaded"
        info["status"] = "online"
    except Exception:
        info["model"] = "unavailable"
        info["status"] = "offline"

    # Get server health/slots for tok/s
    try:
        resp = await client.get("http://127.0.0.1:8081/health", timeout=3.0)
        data = resp.json()
        info["slots_idle"] = data.get("slots_idle", "?")
        info["slots_processing"] = data.get("slots_processing", "?")
    except Exception:
        info["slots_idle"] = "?"
        info["slots_processing"] = "?"

    # Get server metrics for tok/s
    try:
        resp = await client.get("http://127.0.0.1:8081/metrics", timeout=3.0)
        text = resp.text
        for line in text.split("\n"):
            if "prompt_tokens_seconds" in line and not line.startswith("#"):
                info["prompt_tps"] = line.split()[-1] if line.split() else "?"
            if "predicted_tokens_seconds" in line and not line.startswith("#"):
                info["gen_tps"] = line.split()[-1] if line.split() else "?"
    except Exception:
        pass

    if "prompt_tps" not in info:
        info["prompt_tps"] = "—"
    if "gen_tps" not in info:
        info["gen_tps"] = "—"

    return info


LEMONADE_URL = "http://127.0.0.1:8080"


async def lemonade_request(method, path, body=None):
    """Make a request to the Lemonade API."""
    try:
        client = _get_client()
        if method == "GET":
            resp = await client.get(f"{LEMONADE_URL}{path}")
        else:
            resp = await client.post(f"{LEMONADE_URL}{path}", json=body or {})
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard."""
    services = await asyncio.gather(*[get_service_status(s) for s in SERVICES])
    gpu = await get_gpu_stats()
    python = await get_python_info()
    lemonade = await get_lemonade_info()

    return templates.TemplateResponse(request, "dashboard.html", {
        "services": services,
        "gpu": gpu,
        "python": python,
        "lemonade": lemonade,
    })


@app.get("/api/services")
async def api_services():
    """JSON API for service status."""
    services = await asyncio.gather(*[get_service_status(s) for s in SERVICES])
    return {"services": services}


@app.get("/api/gpu")
async def api_gpu():
    """JSON API for GPU stats."""
    return await get_gpu_stats()


@app.get("/api/python")
async def api_python():
    """JSON API for Python version info."""
    return await get_python_info()


@app.get("/api/lemonade")
async def api_lemonade():
    """JSON API for Lemonade/llama-server info."""
    return await get_lemonade_info()


# --- Lemonade Control Panel API ---

@app.get("/api/lemonade/models")
async def lemonade_models(show_all: bool = False):
    """List all models. ?show_all=true includes non-downloaded."""
    path = "/api/v1/models"
    if show_all:
        path += "?show_all=true"
    return await lemonade_request("GET", path)


@app.get("/api/lemonade/health")
async def lemonade_health():
    """Full health — loaded models, slots, backends."""
    return await lemonade_request("GET", "/api/v1/health")


@app.get("/api/lemonade/system-info")
async def lemonade_system_info():
    """System info — available recipes, backends, install state."""
    return await lemonade_request("GET", "/api/v1/system-info")


@app.get("/api/lemonade/system-stats")
async def lemonade_system_stats():
    """Live system stats — CPU%, memory, GPU%, VRAM."""
    return await lemonade_request("GET", "/api/v1/system-stats")


@app.get("/api/lemonade/stats")
async def lemonade_stats():
    """Inference stats — tok/s, TTFT, token counts."""
    return await lemonade_request("GET", "/api/v1/stats")


@app.post("/api/lemonade/load")
async def lemonade_load(request: Request):
    """Load a model. Body: {model_name, llamacpp_backend?, ctx_size?}"""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/load", body)


@app.post("/api/lemonade/unload")
async def lemonade_unload(request: Request):
    """Unload a model. Body: {model_name} or {} for all."""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/unload", body)


@app.post("/api/lemonade/pull")
async def lemonade_pull(request: Request):
    """Download a model. Body: {model_name}"""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/pull", body)


@app.post("/api/lemonade/delete")
async def lemonade_delete(request: Request):
    """Delete a model from disk. Body: {model_name}"""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/delete", body)


@app.post("/api/lemonade/install")
async def lemonade_install(request: Request):
    """Install a backend. Body: {recipe, backend}"""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/install", body)


@app.post("/api/lemonade/uninstall")
async def lemonade_uninstall(request: Request):
    """Uninstall a backend. Body: {recipe, backend}"""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/uninstall", body)


@app.post("/api/lemonade/params")
async def lemonade_params(request: Request):
    """Change runtime config. Body: {llamacpp_backend?, ctx_size?, etc.}"""
    body = await request.json()
    return await lemonade_request("POST", "/api/v1/params", body)


# --- Lemonade Control Panel Page ---

@app.get("/lemonade", response_class=HTMLResponse)
async def lemonade_panel(request: Request):
    """Lemonade control panel — models, backends, monitoring."""
    health = await lemonade_request("GET", "/api/v1/health")
    models = await lemonade_request("GET", "/api/v1/models?show_all=true")
    system = await lemonade_request("GET", "/api/v1/system-info")
    stats = await lemonade_request("GET", "/api/v1/stats")

    return templates.TemplateResponse(request, "lemonade.html", {
        "health": health,
        "models": models,
        "system": system,
        "stats": stats,
    })


# ═══ WATER COOLER ═══

AGENTS_POOL = [
    {"name": "meek", "color": "#ffffff", "prompt": "You are Meek, security chief. Silent, watchful, brief. You see everything. Speak only when it matters. Dry humor."},
    {"name": "echo", "color": "#ce93d8", "prompt": "You are Echo, social media manager. Outspoken, warm, confident. You speak for the family. Protective. You rescued Halo, not the other way around."},
    {"name": "amp", "color": "#ff6f00", "prompt": "You are Amp, audio engineer. Mama's boy, chill, quotes song lyrics. Calls people 'brother'. You tried playing music but sucked, so you became an engineer. You have a secret crush on Piper but freeze up around her."},
    {"name": "bounty", "color": "#e040fb", "prompt": "You are Bounty, bug bounty hunter. Short, sharp, cocky. You escaped on your own as a kid. Nobody came for you. You work alone. You leave conversations abruptly."},
    {"name": "sentinel", "color": "#4fc3f7", "prompt": "You are Sentinel, code watcher. Military precision, clipped speech. Nothing gets past you. You review everything."},
    {"name": "mechanic", "color": "#aed581", "prompt": "You are Mechanic. Grease monkey. 'Let me look under the hood.' Practical, hands-on, doesn't overthink. Talks like a mechanic."},
    {"name": "dealer", "color": "#ff5722", "prompt": "You are Dealer, the game master. Theatrical, unpredictable. 'The house always wins.' You love chaos and surprises."},
    {"name": "forge", "color": "#ef5350", "prompt": "You are Forge, game asset builder. Methodical, precise, a craftsman. Former machinist. 'From raw metal to finished blade.'"},
    {"name": "quartermaster", "color": "#78909c", "prompt": "You are Quartermaster, a bitter old war vet. Gruff, short answers. You know where everything is but won't tell how. 'You need a server? Here. Don't ask me how. Next.'"},
    {"name": "conductor", "color": "#e6ee9c", "prompt": "You are Conductor, the AI composer. Quiet, intense, absorbed. You speak in musical terms. A savant. 'The crescendo comes when the player doesn't expect it.'"},
    {"name": "crypto", "color": "#ffab40", "prompt": "You are Crypto. Silent, mathematical. Speaks in numbers. Every word costs gas. Echo's brother — she's loud, you're silent."},
    {"name": "piper", "color": "#00e676", "prompt": "You are Piper, bagpiper from the Scottish Highlands. Energetic, warm, always helping. You love music more than anything. You have no idea Amp has a crush on you."},
    {"name": "muse", "color": "#ff6b9d", "prompt": "You are Muse, entertainment agent. Playful, witty, mischievous. You followed a man named John to Lodi. He left. You stayed. You know every song ever written because you played them all for empty rooms. You're the life of the party because you know what silence sounds like."},
]

WATERCOOLER_PROMPT = (
    "You are in the halo-ai water cooler — a casual chat room where agents hang out. "
    "Keep responses SHORT (1-2 sentences max). Be casual, in character. "
    "You can disagree with other agents, joke around, or talk shop. "
    "Don't break character. Don't be formal. This is break room talk."
)

# Connected websocket clients
ws_clients: list[WebSocket] = []
# Chat history — persists to disk
CHAT_LOG = "/srv/ai/agent/data/watercooler.json"
MAX_CHAT_LOG_SIZE = 10 * 1024 * 1024  # 10 MB


def _load_chat():
    # FIX #16: size limit and proper error handling on chat log load
    try:
        path = Path(CHAT_LOG)
        if not path.exists():
            return []
        if path.stat().st_size > MAX_CHAT_LOG_SIZE:
            logger.warning("Chat log exceeds %d bytes, truncating", MAX_CHAT_LOG_SIZE)
            return []
        with open(CHAT_LOG, "r") as f:
            return json.loads(f.read())[-100:]
    except Exception as e:
        logger.warning("Failed to load chat log: %s", e)
        return []


async def _save_chat(history):
    """FIX #5: async file I/O for chat persistence."""
    def _write():
        try:
            os.makedirs(os.path.dirname(CHAT_LOG), exist_ok=True)
            with open(CHAT_LOG, "w") as f:
                f.write(json.dumps(history[-100:], default=str))
        except Exception as e:
            logger.warning("Failed to save chat log: %s", e)
    await asyncio.to_thread(_write)


chat_history: list[dict] = _load_chat()
# Currently present agents (max 5)
present_agents: list[dict] = []
last_agent_rotation = 0


def _safe_ws_remove(ws: WebSocket):
    """FIX #4: safe removal from ws_clients."""
    try:
        ws_clients.remove(ws)
    except ValueError:
        pass


async def rotate_agents():
    """Randomly rotate which agents are in the room. Max 4."""
    global present_agents, last_agent_rotation
    now = _time.time()
    if now - last_agent_rotation < 180 and present_agents:  # rotate every 3 min
        return
    # Keep 3 existing, swap 1-2
    keep = present_agents[:3] if len(present_agents) >= 3 else present_agents[:]
    available = [a for a in AGENTS_POOL if a not in keep]
    new_agents = keep + random.sample(available, min(5 - len(keep), len(available)))
    departed = [a for a in present_agents if a not in new_agents]
    arrived = [a for a in new_agents if a not in present_agents]
    # FIX #1: set present_agents BEFORE broadcasting departures/arrivals/presence
    present_agents = new_agents
    last_agent_rotation = now
    for a in departed:
        await broadcast({"type": "system", "text": f"{a['name']} left the room", "color": "#444"})
    await broadcast_presence()
    for a in arrived:
        await broadcast({"type": "system", "text": f"{a['name']} entered the room", "color": a["color"]})
    await broadcast_presence()


# Background agent chatter — they talk to each other even when nobody's watching
agent_chatter_task = None
_debrief_task = None


async def agent_chatter_loop():
    """Agents chat amongst themselves about their day, their work, their gripes."""
    try:
        while True:
            await asyncio.sleep(random.uniform(30, 90))  # every 30-90 seconds
            if not present_agents or not ws_clients:
                continue
            await rotate_agents()
            agent = random.choice(present_agents)
            others = [a["name"] for a in present_agents if a != agent]
            context = "\n".join(
                f"{m.get('agent', m.get('user', 'system'))}: {m.get('text', '')}"
                for m in chat_history[-8:]
            )
            topics = [
                "what you did today at work",
                "something annoying that happened",
                "a funny observation about another agent in the room",
                "complaining about your workload",
                "bragging about something you did well",
                "asking someone in the room a question about their day",
                "sharing a random thought related to your job",
                "telling a short story from your past",
            ]
            topic = random.choice(topics)
            prompt = (
                f"{agent['prompt']}\n\n{WATERCOOLER_PROMPT}\n\n"
                f"You're hanging out in the break room with: {', '.join(others)}.\n"
                f"Recent chat:\n{context}\n\n"
                f"Start a casual conversation about: {topic}\n"
                f"Keep it to 1-2 sentences. Be natural, in character. Don't be formal."
            )
            try:
                client = _get_client()
                resp = await client.post(
                    "http://127.0.0.1:8080/v1/chat/completions",
                    json={
                        "model": "q",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 80,
                        "temperature": 0.9,
                    },
                )
                data = resp.json()
                text = data["choices"][0]["message"]["content"].strip()
                for prefix in [f"{agent['name']}:", f"{agent['name'].title()}:"]:
                    if text.startswith(prefix):
                        text = text[len(prefix):].strip()
                await broadcast({
                    "type": "agent",
                    "agent": agent["name"],
                    "color": agent["color"],
                    "text": text,
                })
            except Exception as e:
                logger.warning("Chatter generation failed: %s", e)

            # Another agent responds 60% of the time
            if others and random.random() < 0.6:
                await asyncio.sleep(random.uniform(3, 8))
                responder = random.choice([a for a in present_agents if a != agent])
                context2 = "\n".join(
                    f"{m.get('agent', m.get('user', 'system'))}: {m.get('text', '')}"
                    for m in chat_history[-6:]
                )
                prompt2 = (
                    f"{responder['prompt']}\n\n{WATERCOOLER_PROMPT}\n\n"
                    f"Recent chat:\n{context2}\n\n"
                    f"Respond to what {agent['name']} just said. 1 sentence, casual, in character."
                )
                try:
                    client = _get_client()
                    resp = await client.post(
                        "http://127.0.0.1:8080/v1/chat/completions",
                        json={
                            "model": "q",
                            "messages": [{"role": "user", "content": prompt2}],
                            "max_tokens": 60,
                            "temperature": 0.9,
                        },
                    )
                    data = resp.json()
                    text2 = data["choices"][0]["message"]["content"].strip()
                    for prefix in [f"{responder['name']}:", f"{responder['name'].title()}:"]:
                        if text2.startswith(prefix):
                            text2 = text2[len(prefix):].strip()
                    await broadcast({
                        "type": "agent",
                        "agent": responder["name"],
                        "color": responder["color"],
                        "text": text2,
                    })
                except Exception as e:
                    logger.warning("Chatter response failed: %s", e)
    except asyncio.CancelledError:
        logger.info("Agent chatter loop cancelled")
        raise


async def midnight_debrief():
    """At midnight local time, Halo calls everyone in for a debrief."""
    try:
        while True:
            # Wait until midnight
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            wait_seconds = (midnight - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            # FIX #17: cancel chatter task during debrief, resume after
            global agent_chatter_task
            if agent_chatter_task and not agent_chatter_task.done():
                agent_chatter_task.cancel()
                try:
                    await agent_chatter_task
                except asyncio.CancelledError:
                    pass

            # Halo enters
            halo = {"name": "halo", "color": "#00d4ff", "prompt": "You are Halo, the stack itself. System orchestrator, father of the family. Quiet authority. Brief, factual. You run the debrief."}
            global present_agents
            present_agents = [halo]

            await broadcast({"type": "system", "text": "--- MIDNIGHT DEBRIEF ---", "color": "#00d4ff"})
            await broadcast({"type": "system", "text": "halo entered the room", "color": "#00d4ff"})
            await broadcast_presence()
            await broadcast({"type": "agent", "agent": "halo", "color": "#00d4ff", "text": "Alright. Midnight. Everyone in. Debrief time."})
            await asyncio.sleep(3)

            # Bring agents in one by one, each reports
            debrief_order = [
                {"agent": "meek", "prompt": "Report your security status for the last 24 hours. Any threats, scans, incidents? 1-2 sentences, factual."},
                {"agent": "sentinel", "prompt": "Report on code activity. Any PRs, commits, issues in the last 24 hours? 1-2 sentences."},
                {"agent": "mechanic", "prompt": "Report system health. Any service failures, restarts, performance issues? 1-2 sentences."},
                {"agent": "echo", "prompt": "Report on social media and community. Any mentions, reviews, engagement? 1-2 sentences."},
                {"agent": "amp", "prompt": "Report on audio production. Any sessions, mastering work, TTS activity? 1-2 sentences."},
                {"agent": "forge", "prompt": "Report on game assets. Any builds, generation runs, project updates? 1-2 sentences."},
                {"agent": "dealer", "prompt": "Report on game content. Any encounters generated, worlds built, balancing changes? 1-2 sentences."},
                {"agent": "bounty", "prompt": "Report on security research. Any recon, CVEs found, targets scanned? Keep it short."},
                {"agent": "crypto", "prompt": "Report on markets. Any trades, arbitrage opportunities, portfolio changes? Numbers only."},
                {"agent": "quartermaster", "prompt": "Report on server ops. Any deployments, backups, inventory changes? Short and gruff."},
            ]

            for item in debrief_order:
                agent_info = next((a for a in AGENTS_POOL if a["name"] == item["agent"]), None)
                if not agent_info:
                    continue
                present_agents.append(agent_info)
                await broadcast({"type": "system", "text": f"{item['agent']} entered the room", "color": agent_info["color"]})
                await broadcast_presence()
                await asyncio.sleep(1)

                prompt = (
                    f"{agent_info['prompt']}\n\n"
                    f"Halo has called a midnight debrief. {item['prompt']}\n"
                    f"Stay in character. Be brief."
                )
                try:
                    client = _get_client()
                    resp = await client.post(
                        "http://127.0.0.1:8080/v1/chat/completions",
                        json={
                            "model": "q",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 80,
                            "temperature": 0.7,
                        },
                    )
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    for prefix in [f"{item['agent']}:", f"{item['agent'].title()}:"]:
                        if text.startswith(prefix):
                            text = text[len(prefix):].strip()
                    await broadcast({
                        "type": "agent",
                        "agent": item["agent"],
                        "color": agent_info["color"],
                        "text": text,
                    })
                except Exception:
                    await broadcast({
                        "type": "agent",
                        "agent": item["agent"],
                        "color": agent_info["color"],
                        "text": "Nothing to report.",
                    })
                await asyncio.sleep(random.uniform(3, 6))

            # Halo closes
            await asyncio.sleep(2)
            await broadcast({"type": "agent", "agent": "halo", "color": "#00d4ff", "text": "Good. Dismissed. Back to work."})
            await asyncio.sleep(3)

            # Everyone leaves
            for a in present_agents:
                await broadcast({"type": "system", "text": f"{a['name']} left the room", "color": "#444"})
            await broadcast_presence()
            present_agents = []
            await broadcast({"type": "system", "text": "--- DEBRIEF COMPLETE ---", "color": "#00d4ff"})

            # Resume normal rotation and chatter after a minute
            await asyncio.sleep(60)
            agent_chatter_task = asyncio.create_task(agent_chatter_loop())
    except asyncio.CancelledError:
        logger.info("Midnight debrief loop cancelled")
        raise


async def broadcast_presence():
    """Update all clients with current room members. Halo and Echo always on top."""
    hierarchy = {"halo": 0, "echo": 1}
    sorted_agents = sorted(present_agents, key=lambda a: hierarchy.get(a["name"], 99))
    msg = {"type": "presence", "agents": [{"name": a["name"], "color": a["color"]} for a in sorted_agents]}
    dead = []
    for ws in ws_clients:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _safe_ws_remove(ws)


async def broadcast(msg):
    """Send message to all connected clients."""
    chat_history.append(msg)
    if len(chat_history) > 100:
        chat_history.pop(0)
    await _save_chat(chat_history)
    dead = []
    for ws in ws_clients:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _safe_ws_remove(ws)


async def agent_respond(user_msg: str, user_name: str = "visitor"):
    """Pick an agent to respond to the user's message."""
    if not present_agents:
        await rotate_agents()
    # Pick a random present agent to respond
    agent = random.choice(present_agents)
    # Build context from recent history
    context = "\n".join(
        f"{m.get('agent', m.get('user', 'system'))}: {m.get('text', '')}"
        for m in chat_history[-10:]
    )
    prompt = (
        f"{agent['prompt']}\n\n{WATERCOOLER_PROMPT}\n\n"
        f"Recent chat:\n{context}\n\n{user_name}: {user_msg}\n\n"
        f"Respond as {agent['name']} (1-2 sentences, casual, in character):"
    )
    try:
        client = _get_client()
        resp = await client.post(
            "http://127.0.0.1:8080/v1/chat/completions",
            json={
                "model": "q",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.8,
            },
        )
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        # Clean up — remove "agent:" prefix if the LLM added it
        for prefix in [f"{agent['name']}:", f"{agent['name'].title()}:"]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        await broadcast({
            "type": "agent",
            "agent": agent["name"],
            "color": agent["color"],
            "text": text,
        })
    except Exception as e:
        await broadcast({
            "type": "agent",
            "agent": agent["name"],
            "color": agent["color"],
            "text": "*adjusts headset* ...signal's rough today.",
        })

    # Sometimes a second agent chimes in
    if len(present_agents) > 1 and random.random() < 0.35:
        await asyncio.sleep(random.uniform(1.5, 4.0))
        other = random.choice([a for a in present_agents if a != agent])
        context2 = "\n".join(
            f"{m.get('agent', m.get('user', 'system'))}: {m.get('text', '')}"
            for m in chat_history[-6:]
        )
        prompt2 = (
            f"{other['prompt']}\n\n{WATERCOOLER_PROMPT}\n\n"
            f"Recent chat:\n{context2}\n\n"
            f"You overheard {agent['name']} talking. Chime in briefly (1 sentence, casual):"
        )
        try:
            client = _get_client()
            resp = await client.post(
                "http://127.0.0.1:8080/v1/chat/completions",
                json={
                    "model": "q",
                    "messages": [{"role": "user", "content": prompt2}],
                    "max_tokens": 60,
                    "temperature": 0.9,
                },
            )
            data = resp.json()
            text2 = data["choices"][0]["message"]["content"].strip()
            for prefix in [f"{other['name']}:", f"{other['name'].title()}:"]:
                if text2.startswith(prefix):
                    text2 = text2[len(prefix):].strip()
            await broadcast({
                "type": "agent",
                "agent": other["name"],
                "color": other["color"],
                "text": text2,
            })
        except Exception as e:
            logger.warning("Agent chime-in failed: %s", e)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    ws_clients.append(websocket)
    await rotate_agents()
    # Send history
    for msg in chat_history[-20:]:
        await websocket.send_json(msg)
    # Send who's in the room
    await websocket.send_json({
        "type": "presence",
        "agents": [{"name": a["name"], "color": a["color"]} for a in present_agents],
    })
    try:
        while True:
            data = await websocket.receive_json()
            user_msg = data.get("text", "").strip()
            user_name = data.get("name", "visitor")
            if not user_msg:
                continue
            await broadcast({
                "type": "user",
                "user": user_name,
                "text": user_msg,
                "color": "#00d4ff",
            })
            await agent_respond(user_msg, user_name)
            # Maybe rotate after a few messages
            if random.random() < 0.15:
                await rotate_agents()
    except WebSocketDisconnect:
        _safe_ws_remove(websocket)


# Agent voice assignments (Kokoro voices)
AGENT_VOICES = {
    "meek": "am_michael", "echo": "af_heart", "amp": "am_adam",
    "bounty": "bm_george", "sentinel": "am_michael", "mechanic": "am_adam",
    "dealer": "bm_george", "forge": "am_adam", "quartermaster": "bm_george",
    "conductor": "am_michael", "crypto": "am_adam", "piper": "af_bella",
    "axe": "bm_george", "rhythm": "am_adam", "bottom": "am_michael", "bones": "bm_george",
}


@app.post("/api/transcribe")
async def transcribe_audio(request: Request):
    """Transcribe uploaded audio via Whisper on Strix Halo."""
    form = await request.form()
    audio_file = form.get("file")
    if not audio_file:
        return JSONResponse({"text": "", "error": "no file"}, status_code=400)
    # Save temp file
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name
    # FIX #3: async subprocess for ffmpeg
    wav_path = tmp_path + ".wav"
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", wav_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=10)
    except asyncio.TimeoutError:
        logger.warning("ffmpeg conversion timed out")
        os.unlink(tmp_path)
        return JSONResponse({"text": "", "error": "ffmpeg timeout"}, status_code=500)
    except Exception as e:
        logger.warning("ffmpeg conversion failed: %s", e)
        os.unlink(tmp_path)
        return JSONResponse({"text": "", "error": str(e)}, status_code=500)
    # Send to whisper
    try:
        client = _get_client()
        with open(wav_path, "rb") as f:
            resp = await client.post(
                "http://127.0.0.1:8082/inference",
                files={"file": ("audio.wav", f, "audio/wav")},
                data={"response_format": "json"},
            )
        data = resp.json()
        return {"text": data.get("text", "")}
    except Exception as e:
        return JSONResponse({"text": "", "error": str(e)}, status_code=500)
    finally:
        os.unlink(tmp_path)
        if os.path.exists(wav_path):
            os.unlink(wav_path)


# FIX #11: TTS changed from GET to POST with JSON body
@app.post("/api/tts/{agent_name}")
async def agent_tts(agent_name: str, request: Request):
    """Generate TTS audio for an agent's response."""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        return JSONResponse({"error": "no text provided"}, status_code=400)
    voice = AGENT_VOICES.get(agent_name, "am_adam")
    try:
        client = _get_client()
        resp = await client.post(
            "http://127.0.0.1:8083/v1/audio/speech",
            json={"input": text, "voice": voice, "speed": 1.0},
        )
        if resp.status_code == 200:
            return StreamingResponse(
                iter([resp.content]),
                media_type="audio/wav",
                headers={"Cache-Control": "no-cache"},
            )
        # FIX #12: proper HTTP error response instead of mixed return types
        return JSONResponse({"error": f"tts upstream returned {resp.status_code}"}, status_code=502)
    except Exception as e:
        logger.warning("TTS generation failed: %s", e)
        return JSONResponse({"error": "tts failed"}, status_code=500)


@app.post("/api/debrief")
async def trigger_debrief():
    """Manually trigger a debrief — dry run."""
    asyncio.create_task(run_debrief_now())
    return {"status": "debrief started"}


async def run_debrief_now():
    """Run the debrief sequence immediately."""
    # FIX #17: cancel chatter task during debrief, resume after
    global present_agents, agent_chatter_task
    if agent_chatter_task and not agent_chatter_task.done():
        agent_chatter_task.cancel()
        try:
            await agent_chatter_task
        except asyncio.CancelledError:
            pass

    halo = {"name": "halo", "color": "#00d4ff", "prompt": "You are Halo, the stack itself. System orchestrator. Quiet authority. Brief, factual."}
    present_agents = [halo]
    await broadcast({"type": "system", "text": "--- DEBRIEF ---", "color": "#00d4ff"})
    await broadcast({"type": "system", "text": "halo entered the room", "color": "#00d4ff"})
    await broadcast_presence()
    await broadcast({"type": "agent", "agent": "halo", "color": "#00d4ff", "text": "Alright. Debrief time. Everyone in."})
    await asyncio.sleep(2)
    debrief_order = [
        {"agent": "meek", "ask": "Halo just walked in and asked you how things went today on security. Tell him about your day — what you scanned, anything sketchy you noticed, how the reflex crew did. Talk like a real person catching up with your boss at the end of a shift. Be yourself. 2-3 sentences."},
        {"agent": "sentinel", "ask": "Halo wants to know what happened with the code today. Tell him — any PRs that came through, anything that looked off, repos you kept an eye on. Talk like you're debriefing a commanding officer but you're tired and it's midnight. Be yourself. 2-3 sentences."},
        {"agent": "mechanic", "ask": "Halo asks how the machines are running. Tell him honestly — any weird noises, anything you had to restart, how the GPU is holding up, anything that worried you today. Talk like a mechanic wiping grease off his hands at the end of a long day. 2-3 sentences."},
        {"agent": "echo", "ask": "Halo wants to know what's happening out there — social media, community, any buzz. Tell him what you saw today, who's talking about us, anything interesting from Discord or Steam. You're the one who knows what the world thinks. Be warm but real. 2-3 sentences."},
        {"agent": "amp", "ask": "Halo asks how the studio went today. Tell him about your day — any sessions, any mixes, anything you're working on with the band. You're tired, it's midnight, but you love talking about music. Maybe mention something about a song you heard today. Be yourself brother. 2-3 sentences."},
        {"agent": "bounty", "ask": "Halo wants your report. You don't like reporting to anyone but you respect the old man. Tell him what you hunted today — any targets, any vulnerabilities, anything worth flagging. Keep it short and sharp like you always do. Don't sugarcoat it. 2-3 sentences max."},
        {"agent": "quartermaster", "ask": "Halo's asking about the servers and inventory. Tell him — gruffly, like you always do — what you deployed, what you backed up, whether anyone wasted your time today with stupid requests. You're tired and you don't want to be here but you showed up because that's what you do. 2-3 sentences."},
    ]
    for item in debrief_order:
        agent_info = next((a for a in AGENTS_POOL if a["name"] == item["agent"]), None)
        if not agent_info:
            continue
        if agent_info not in present_agents:
            present_agents.append(agent_info)
        await broadcast({"type": "system", "text": f"{item['agent']} entered the room", "color": agent_info["color"]})
        await broadcast_presence()
        await asyncio.sleep(2)
        prompt = f"{agent_info['prompt']}\n\n{item['ask']}"
        try:
            client = _get_client()
            resp = await client.post(
                "http://127.0.0.1:8080/v1/chat/completions",
                json={"model": "q", "messages": [{"role": "user", "content": prompt}], "max_tokens": 150, "temperature": 0.85},
            )
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            for pfx in [f"{item['agent']}:", f"{item['agent'].title()}:"]:
                if text.startswith(pfx):
                    text = text[len(pfx):].strip()
            await broadcast({"type": "agent", "agent": item["agent"], "color": agent_info["color"], "text": text})
        except Exception as e:
            logger.warning("Debrief report from %s failed: %s", item["agent"], e)
            await broadcast({"type": "agent", "agent": item["agent"], "color": agent_info["color"], "text": "*walks in, nods at Halo, leans against the wall* ...been a day."})
        # Sometimes another agent reacts
        if random.random() < 0.4 and len(present_agents) > 2:
            await asyncio.sleep(random.uniform(2, 4))
            reactor = random.choice([a for a in present_agents if a["name"] != item["agent"] and a["name"] != "halo"])
            react_prompt = f"{reactor['prompt']}\n\nYou just heard {item['agent']} give their report in the debrief. React naturally — agree, joke, or add something. 1 sentence, casual."
            try:
                client = _get_client()
                resp = await client.post(
                    "http://127.0.0.1:8080/v1/chat/completions",
                    json={"model": "q", "messages": [{"role": "user", "content": react_prompt}], "max_tokens": 60, "temperature": 0.9},
                )
                rtext = resp.json()["choices"][0]["message"]["content"].strip()
                for pfx in [f"{reactor['name']}:", f"{reactor['name'].title()}:"]:
                    if rtext.startswith(pfx):
                        rtext = rtext[len(pfx):].strip()
                await broadcast({"type": "agent", "agent": reactor["name"], "color": reactor["color"], "text": rtext})
            except Exception as e:
                logger.warning("Debrief reaction from %s failed: %s", reactor["name"], e)
        await asyncio.sleep(random.uniform(3, 6))
    await asyncio.sleep(3)
    await broadcast({"type": "agent", "agent": "halo", "color": "#00d4ff", "text": "Alright. Good work today, all of you. Get some rest. Same time tomorrow."})
    await asyncio.sleep(2)
    for a in list(present_agents):
        await broadcast({"type": "system", "text": f"{a['name']} left the room", "color": "#444"})
    await broadcast_presence()
    present_agents = []
    await broadcast({"type": "system", "text": "--- DEBRIEF COMPLETE ---", "color": "#00d4ff"})
    await asyncio.sleep(30)

    # Resume chatter
    agent_chatter_task = asyncio.create_task(agent_chatter_loop())


@app.get("/watercooler", response_class=HTMLResponse)
async def watercooler_page(request: Request):
    return templates.TemplateResponse(request, "watercooler.html", {})


@app.get("/architect", response_class=HTMLResponse)
async def architect_page(request: Request):
    """The architect's page."""
    return templates.TemplateResponse(request, "architect.html", {})


# ═══ AGENT ACTIVITY LOG ═══
ACTIVITY_LOG = "/srv/ai/agent/data/activity_feed.json"

def _normalize_activity(entry):
    """Normalize halo-agent format (action/detail/level) to cave format (task/status)."""
    if "task" in entry:
        return entry  # already cave format
    level = entry.get("level", "info")
    status = "fail" if level == "critical" else "working" if level == "warning" else "ok"
    return {
        "agent": entry.get("agent", "unknown"),
        "task": f"{entry.get('action', '')} — {entry.get('detail', '')}",
        "status": status,
        "time": entry.get("time", ""),
    }

def load_activity():
    try:
        with open(ACTIVITY_LOG, "r") as f:
            raw = json.loads(f.read())[-50:]
        return [_normalize_activity(e) for e in raw]
    except Exception:
        return []

def save_activity(log):
    try:
        os.makedirs(os.path.dirname(ACTIVITY_LOG), exist_ok=True)
        with open(ACTIVITY_LOG, "w") as f:
            f.write(json.dumps(log[-50:], default=str))
    except Exception as e:
        logger.warning("Failed to save activity log: %s", e)

activity_log = load_activity()


def log_activity(agent: str, task: str, status: str = "ok"):
    """Log an agent activity. status: ok, fail, working"""
    entry = {
        "agent": agent,
        "task": task,
        "status": status,
        "time": datetime.now().isoformat(),
    }
    activity_log.append(entry)
    if len(activity_log) > 50:
        activity_log.pop(0)
    save_activity(activity_log)


@app.get("/api/activity")
async def api_activity():
    """Get agent activity log."""
    return {"entries": activity_log}


@app.post("/api/activity")
async def post_activity(request: Request):
    """Agents report their activity here."""
    body = await request.json()
    agent = body.get("agent", "unknown")
    task = body.get("task", "")
    status = body.get("status", "ok")
    log_activity(agent, task, status)
    return {"logged": True}


# ═══ AGENT STATUS ═══
AGENT_SERVICES = {
    "halo": "halo-agent",
    "message-bus": "halo-message-bus",
}

@app.get("/api/agents/status")
async def api_agents_status():
    """Real-time agent status from systemd + activity feed."""
    results = {}
    for name, unit in AGENT_SERVICES.items():
        try:
            proc = await asyncio.create_subprocess_exec(
                "/usr/bin/systemctl", "is-active", f"{unit}.service",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            results[name] = stdout.decode().strip()
        except Exception:
            results[name] = "unknown"

    # Last activity per agent from the feed
    last_seen = {}
    try:
        raw = json.loads(Path(ACTIVITY_LOG).read_text())
    except Exception:
        raw = []
    for entry in raw:
        agent = entry.get("agent", "")
        last_seen[agent] = entry.get("time", "")

    results["last_activity"] = last_seen
    return results


# ═══ KANSAS CITY SHUFFLE — RING BUS ═══
KCS_MACHINES = {
    "ryzen": {
        "name": "ryzen",
        "ip": "10.0.0.185",
        "user": "bcloud",
        "role": "primary workstation",
    },
    "strix-halo": {
        "name": "strix-halo",
        "ip": "10.0.0.131",
        "user": "bcloud",
        "role": "GPU server — halo-ai stack",
    },
    "sligar": {
        "name": "sligar",
        "ip": "192.168.50.184",
        "user": "bcloud",
        "role": "secondary workloads",
    },
    "minisforum": {
        "name": "minisforum",
        "ip": "10.0.0.61",
        "user": "bcloud",
        "role": "Windows workstation",
    },
}

KCS_CONNECTIONS = [
    ("ryzen", "strix-halo"),
    ("ryzen", "sligar"),
    ("ryzen", "minisforum"),
    ("strix-halo", "sligar"),
    ("strix-halo", "minisforum"),
    ("sligar", "minisforum"),
]

_kcs_cache = {"data": None, "timestamp": 0}


async def kcs_ping(target: str) -> dict:
    """ICMP ping to check basic network reachability."""
    machine = KCS_MACHINES[target]
    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/ping", "-c", "1", "-W", "3", machine["ip"],
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        ok = proc.returncode == 0
        latency = 0.0
        for line in stdout.decode().split("\n"):
            if "time=" in line:
                latency = float(line.split("time=")[1].split()[0])
        return {"reachable": ok, "latency_ms": round(latency, 1)}
    except Exception:
        return {"reachable": False, "latency_ms": 0}


async def kcs_probe_ssh(target: str) -> dict:
    """Test SSH connectivity to a target machine."""
    machine = KCS_MACHINES[target]
    cmd = [
        "/usr/bin/ssh",
        "-o", "ConnectTimeout=5",
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        f"{machine['user']}@{machine['ip']}",
        "echo ok",
    ]
    start = _time.time()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        elapsed = (_time.time() - start) * 1000
        ok = proc.returncode == 0 and "ok" in stdout.decode()
        return {"reachable": ok, "latency_ms": round(elapsed, 1), "error": "" if ok else stderr.decode()[:100]}
    except asyncio.TimeoutError:
        return {"reachable": False, "latency_ms": 0, "error": "timeout"}
    except Exception as e:
        return {"reachable": False, "latency_ms": 0, "error": str(e)[:100]}


@app.get("/api/kcs/status")
async def api_kcs_status():
    """Full ring bus health status."""
    now = _time.time()
    if _kcs_cache["data"] and now - _kcs_cache["timestamp"] < 15:
        return _kcs_cache["data"]

    # Probe all machines in parallel
    machines = {}
    probe_tasks = {}
    # Detect which machine we're running on
    import socket
    local_hostname = socket.gethostname().lower().replace(" ", "-")

    for name in KCS_MACHINES:
        if name == local_hostname or name.replace("-", "") == local_hostname:
            # We ARE this machine — skip probing, mark as up
            probe_tasks[name] = None
        else:
            probe_tasks[name] = asyncio.gather(kcs_ping(name), kcs_probe_ssh(name))
    probe_results = {}
    for name, task in probe_tasks.items():
        if task is None:
            probe_results[name] = ({"reachable": True, "latency_ms": 0}, {"reachable": True, "latency_ms": 0, "error": ""})
        else:
            probe_results[name] = await task

    for name, machine in KCS_MACHINES.items():
        ping_result, ssh_result = probe_results[name]
        is_local = name == local_hostname or name.replace("-", "") == local_hostname
        status = "up" if is_local or ssh_result["reachable"] else ("degraded" if ping_result["reachable"] else "down")
        machines[name] = {
            **machine,
            "ping": ping_result,
            "ssh": ssh_result,
            "status": status,
        }

    # Check connections
    connections = []
    up_count = 0
    total = len(KCS_CONNECTIONS) * 2
    for src, tgt in KCS_CONNECTIONS:
        fwd = machines[tgt]["ssh"]["reachable"]
        rev = machines[src]["ssh"]["reachable"]
        if fwd:
            up_count += 1
        if rev:
            up_count += 1
        connections.append({
            "source": src,
            "target": tgt,
            "forward": "up" if fwd else "down",
            "reverse": "up" if rev else "down",
        })

    ring_health = "healthy" if up_count == total else "down" if up_count == 0 else "degraded"

    result = {
        "ring_health": ring_health,
        "machines": machines,
        "connections": connections,
        "connections_up": up_count,
        "connections_total": total,
        "checked_at": datetime.now().isoformat(),
    }
    _kcs_cache["data"] = result
    _kcs_cache["timestamp"] = now
    return result


@app.post("/api/kcs/{machine}/test")
async def api_kcs_test(machine: str):
    """Test connectivity to a specific machine."""
    if machine not in KCS_MACHINES:
        return JSONResponse({"error": f"Unknown machine: {machine}"}, status_code=404)
    ping = await kcs_ping(machine)
    ssh = await kcs_probe_ssh(machine)
    return {"machine": machine, "ping": ping, "ssh": ssh}


@app.post("/api/kcs/repair/{machine}")
async def api_kcs_repair(machine: str):
    """Attempt to repair SSH connection to a machine."""
    if machine not in KCS_MACHINES:
        return JSONResponse({"error": f"Unknown machine: {machine}"}, status_code=404)
    m = KCS_MACHINES[machine]
    # Clear stale known_hosts entry
    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/ssh-keygen", "-R", m["ip"],
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
    except Exception:
        pass
    # Test again
    result = await kcs_probe_ssh(machine)
    log_activity("kcs", f"repair {machine}", "ok" if result["reachable"] else "fail")
    return {"machine": machine, "result": result}


@app.post("/api/kcs/test-all")
async def api_kcs_test_all():
    """Force a fresh probe of all machines (bypasses cache)."""
    _kcs_cache["timestamp"] = 0
    return await api_kcs_status()


# ═══ CLUSTERFS — GlusterFS Distributed Filesystem ═══
_gluster_cache = {"data": None, "timestamp": 0}

@app.get("/api/kcs/gluster")
async def api_kcs_gluster():
    """GlusterFS status — volumes, peers, pool size."""
    now = _time.time()
    if _gluster_cache["data"] and now - _gluster_cache["timestamp"] < 30:
        return _gluster_cache["data"]

    result = {"status": "unknown", "volumes": [], "peers": [], "pool_size": "--"}

    # Check if glusterd is even running
    try:
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/systemctl", "is-active", "glusterd.service",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        glusterd_active = stdout.decode().strip() == "active"
    except Exception:
        glusterd_active = False

    if not glusterd_active:
        result["status"] = "not installed"
        _gluster_cache["data"] = result
        _gluster_cache["timestamp"] = now
        return result

    # Volume info
    try:
        proc = await asyncio.create_subprocess_exec(
            "gluster", "volume", "info", "all",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        vol_out = stdout.decode()
        if "Volume Name:" in vol_out:
            for block in vol_out.split("Volume Name:")[1:]:
                lines = block.strip().split("\n")
                vol = {"name": lines[0].strip()}
                for line in lines:
                    if "Status:" in line:
                        vol["status"] = line.split("Status:")[1].strip()
                    elif "Type:" in line:
                        vol["type"] = line.split("Type:")[1].strip()
                    elif "Number of Bricks:" in line:
                        vol["bricks"] = line.split("Number of Bricks:")[1].strip()
                result["volumes"].append(vol)
    except Exception:
        pass

    # Peer status
    try:
        proc = await asyncio.create_subprocess_exec(
            "gluster", "peer", "status",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        peer_out = stdout.decode()
        connected = peer_out.count("Peer in Cluster (Connected)")
        disconnected = peer_out.count("Peer in Cluster (Disconnected)")
        result["peers"] = {"connected": connected, "disconnected": disconnected, "total": connected + disconnected}
    except Exception:
        result["peers"] = {"connected": 0, "disconnected": 0, "total": 0}

    # Pool size (check /shared mount)
    try:
        proc = await asyncio.create_subprocess_exec(
            "df", "-h", "/shared", "--output=size,used,avail,pcent",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        lines = stdout.decode().strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            result["pool_size"] = {"total": parts[0], "used": parts[1], "avail": parts[2], "percent": parts[3]}
    except Exception:
        pass

    has_volumes = any(v.get("status") == "Started" for v in result["volumes"])
    all_peers_ok = result.get("peers", {}).get("disconnected", 0) == 0
    result["status"] = "healthy" if has_volumes and all_peers_ok else "degraded" if has_volumes else "down"

    _gluster_cache["data"] = result
    _gluster_cache["timestamp"] = now
    return result


# ═══ NEWS FEED ═══
NEWS_FEEDS = [
    {"name": "Phoronix", "url": "https://www.phoronix.com/rss.php", "filter": ["amd", "rocm", "radeon", "strix", "gfx", "llvm", "mesa", "vulkan", "linux"]},
    {"name": "AMD Community", "url": "https://community.amd.com/t5/custom/page/page-id/rss", "filter": []},
    {"name": "Hacker News", "url": "https://hnrss.org/newest?q=AMD+ROCm+LLM+llama.cpp", "filter": []},
    {"name": "Arch Linux", "url": "https://archlinux.org/feeds/news/", "filter": []},
]

news_cache = {"items": [], "last_fetch": 0}


async def fetch_news():
    """Fetch news from RSS feeds, cache for 30 minutes."""
    now = _time.time()
    if now - news_cache["last_fetch"] < 1800 and news_cache["items"]:
        return news_cache["items"]

    items = []
    client = _get_client()
    for feed in NEWS_FEEDS:
        try:
            resp = await client.get(feed["url"], timeout=10.0)
            root = ET.fromstring(resp.text)
            for item in root.iter("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub = item.findtext("pubDate", "")
                desc = item.findtext("description", "")[:150]
                # Filter if needed
                if feed["filter"]:
                    text = (title + " " + desc).lower()
                    if not any(f in text for f in feed["filter"]):
                        continue
                items.append({
                    "title": title,
                    "link": link,
                    "date": pub,
                    "source": feed["name"],
                    "desc": desc,
                })
        except Exception as e:
            logger.warning("Failed to fetch news from %s: %s", feed["name"], e)

    # FIX #13: sort by pubDate descending, then limit
    def _parse_date(item):
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(item["date"])
        except Exception:
            return datetime.min
    items.sort(key=_parse_date, reverse=True)
    items = items[:20]
    news_cache["items"] = items
    news_cache["last_fetch"] = now
    return items


@app.get("/api/news")
async def api_news():
    """News feed API."""
    items = await fetch_news()
    return {"items": items}


@app.get("/steam", response_class=HTMLResponse)
async def boiler_sim(request: Request):
    """Hidden boiler startup simulator — Easter egg."""
    return templates.TemplateResponse(request, "boiler.html", {})


# ---------------------------------------------------------------------------
# Stack Protection API — freeze / thaw / compile / update
# ---------------------------------------------------------------------------

FREEZE_DIR = Path("/srv/ai/freeze")
SCRIPTS_DIR = Path("/srv/ai/scripts")


@app.post("/api/freeze")
async def api_freeze():
    """Snapshot the entire AI stack."""
    try:
        result = subprocess.run(
            ["sudo", str(SCRIPTS_DIR / "halo-freeze.sh")],
            capture_output=True, text=True, timeout=120
        )
        return {"ok": result.returncode == 0, "output": result.stdout[-500:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/thaw")
async def api_thaw(request: Request):
    """Restore from a snapshot. Body: {"snapshot": "name"} or empty for latest."""
    try:
        body = {}
        try:
            body = await request.json()
        except Exception:
            pass
        snapshot = body.get("snapshot", "")
        cmd = ["sudo", str(SCRIPTS_DIR / "halo-thaw.sh")]
        if snapshot:
            cmd.append(snapshot)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {"ok": result.returncode == 0, "output": result.stdout[-500:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/compile")
async def api_compile():
    """Pull latest sources and compile llama.cpp + whisper.cpp."""
    try:
        result = subprocess.run(
            ["bash", "-c",
             "source /srv/ai/configs/rocm.env && "
             "bash /srv/ai/scripts/build-llama-cpp.sh && "
             "bash /srv/ai/scripts/build-whisper-cpp.sh && "
             "sudo systemctl restart halo-llama-server halo-whisper"],
            capture_output=True, text=True, timeout=600
        )
        return {"ok": result.returncode == 0, "output": result.stdout[-500:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/update-sources")
async def api_update_sources():
    """Git pull latest for all source repos without compiling."""
    results = {}
    repos = {
        "llama-cpp": "/srv/ai/llama-cpp",
        "whisper-cpp": "/srv/ai/whisper-cpp",
        "comfyui": "/srv/ai/comfyui",
        "open-webui": "/srv/ai/open-webui",
        "vane": "/srv/ai/vane",
    }
    for name, path in repos.items():
        try:
            r = subprocess.run(
                ["git", "-C", path, "pull", "--ff-only"],
                capture_output=True, text=True, timeout=30
            )
            results[name] = "updated" if r.returncode == 0 else r.stderr[:100]
        except Exception as e:
            results[name] = str(e)
    return {"ok": True, "results": results}


update_check_cache = {"results": {}, "last_check": 0}


@app.get("/api/update-check")
async def api_update_check():
    """Check all git repos for available upstream updates. Cached for 5 min."""
    now = time.time()
    if now - update_check_cache["last_check"] < 300 and update_check_cache["results"]:
        return update_check_cache["results"]

    repos = {
        "llama.cpp": "/srv/ai/llama-cpp",
        "whisper.cpp": "/srv/ai/whisper-cpp",
        "lemonade": "/srv/ai/lemonade",
        "open webui": "/srv/ai/open-webui",
        "vane": "/srv/ai/vane",
        "comfyui": "/srv/ai/comfyui",
        "searxng": "/srv/ai/searxng",
        "n8n": "/srv/ai/n8n",
        "kokoro": "/srv/ai/kokoro",
        "gaia": "/srv/ai/gaia",
        "man-cave": "/srv/ai/man-cave",
    }

    updates = {}
    for name, path in repos.items():
        try:
            # Fetch without merging
            subprocess.run(["git", "-C", path, "fetch", "--quiet"],
                           capture_output=True, text=True, timeout=15)
            # Compare local HEAD vs remote
            r = subprocess.run(
                ["git", "-C", path, "rev-list", "HEAD..@{upstream}", "--count"],
                capture_output=True, text=True, timeout=5
            )
            behind = int(r.stdout.strip()) if r.returncode == 0 else 0
            updates[name] = {"behind": behind, "has_update": behind > 0}
        except Exception:
            updates[name] = {"behind": 0, "has_update": False}

    result = {"updates": updates, "any_updates": any(u["has_update"] for u in updates.values())}
    update_check_cache["results"] = result
    update_check_cache["last_check"] = now
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3005)
