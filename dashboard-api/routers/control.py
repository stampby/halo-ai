"""
halo-ai Operator Control API
Service management, mesh status, snapshot control.
Individual service control with safety warnings.
Designed and built by the architect.
"""

import subprocess
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/control", tags=["control"])

# Services that can be managed
MANAGED_SERVICES = [
    "halo-llama-server", "halo-whisper-server", "halo-lemonade",
    "halo-open-webui", "halo-n8n", "halo-comfyui", "halo-searxng",
    "halo-qdrant", "halo-caddy", "halo-vane", "halo-dashboard-api",
    "halo-dashboard-ui", "halo-echo-bot", "halo-gaia-api",
    "halo-gaia-mcp", "halo-gaia-ui", "halo-agent", "halo-message-bus",
]

# Critical services that need extra warnings
CRITICAL_SERVICES = [
    "halo-llama-server",  # kills all inference
    "halo-caddy",         # kills all web access
    "halo-lemonade",      # kills API gateway
]

# Stack freeze state
STACK_FROZEN = True


class ServiceAction(BaseModel):
    service: str
    action: str  # start, stop, restart
    confirmed: bool = False


class MeshNode(BaseModel):
    hostname: str
    ip: str
    user: str = "bcloud"


def run_cmd(cmd: list, timeout: int = 10) -> dict:
    """Run a system command safely."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "timeout"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}


# ── Service Status ────────────────────────────

@router.get("/services")
async def list_services():
    """Get status of all managed services."""
    services = []
    for svc in MANAGED_SERVICES:
        status = run_cmd(["systemctl", "is-active", svc])
        enabled = run_cmd(["systemctl", "is-enabled", svc])

        # Get detailed info
        info = run_cmd(["systemctl", "show", svc,
                       "--property=MainPID,ActiveEnterTimestamp,MemoryCurrent"])

        props = {}
        for line in info["stdout"].split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                props[k] = v

        services.append({
            "name": svc,
            "display": svc.replace("halo-", ""),
            "active": status["stdout"] == "active",
            "enabled": enabled["stdout"] == "enabled",
            "critical": svc in CRITICAL_SERVICES,
            "pid": props.get("MainPID", ""),
            "uptime": props.get("ActiveEnterTimestamp", ""),
            "memory": props.get("MemoryCurrent", ""),
        })
    return {"services": services, "frozen": STACK_FROZEN}


@router.get("/services/{service}")
async def service_detail(service: str):
    """Get detailed info for a single service."""
    svc = f"halo-{service}" if not service.startswith("halo-") else service
    if svc not in MANAGED_SERVICES:
        raise HTTPException(404, f"Unknown service: {svc}")

    status = run_cmd(["systemctl", "status", svc, "--no-pager", "-l"])
    logs = run_cmd(["journalctl", "-u", svc, "-n", "20", "--no-pager"])

    return {
        "name": svc,
        "status": status["stdout"],
        "logs": logs["stdout"],
        "critical": svc in CRITICAL_SERVICES,
        "frozen": STACK_FROZEN,
    }


@router.post("/services/action")
async def service_action(action: ServiceAction):
    """Start, stop, or restart a service with safety checks."""
    svc = action.service
    if not svc.startswith("halo-"):
        svc = f"halo-{svc}"
    if svc not in MANAGED_SERVICES:
        raise HTTPException(404, f"Unknown service: {svc}")

    if action.action not in ("start", "stop", "restart"):
        raise HTTPException(400, "Action must be start, stop, or restart")

    # Safety: critical services need confirmation
    if svc in CRITICAL_SERVICES and action.action in ("stop", "restart"):
        if not action.confirmed:
            return {
                "warning": True,
                "message": f"{svc} is CRITICAL. Stopping it will affect all connected services. Send again with confirmed=true to proceed.",
                "blast_radius": _get_blast_radius(svc),
            }

    # Safety: stack freeze warning for restarts
    if STACK_FROZEN and action.action == "restart":
        if not action.confirmed:
            return {
                "warning": True,
                "message": "Stack is FROZEN. Restarting services during freeze is not recommended. Send again with confirmed=true to override.",
            }

    # Execute
    result = run_cmd(["sudo", "systemctl", action.action, svc])
    return {
        "success": result["success"],
        "service": svc,
        "action": action.action,
        "message": result["stderr"] if not result["success"] else f"{svc} {action.action}ed",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _get_blast_radius(service: str) -> list:
    """What breaks if this service goes down."""
    radius = {
        "halo-llama-server": [
            "All LLM inference stops",
            "Open WebUI loses backend",
            "Gaia agents lose LLM access",
            "Discord bots lose LLM",
            "Voice assistant stops thinking",
        ],
        "halo-caddy": [
            "All web access stops",
            "No browser access to any service",
            "External users disconnected",
        ],
        "halo-lemonade": [
            "API gateway down",
            "OpenAI/Ollama compatible endpoints stop",
            "Clients using Lemonade API disconnect",
        ],
    }
    return radius.get(service, ["Unknown impact"])


# ── Mesh Status ────────────────────────────────

MESH_NODES = [
    {"hostname": "ryzen", "ip": "10.0.0.185", "role": "dev · primary"},
    {"hostname": "strix-halo", "ip": "10.0.0.131", "role": "gpu · 42 services"},
    {"hostname": "pi5", "ip": "10.0.0.216", "role": "pi-hole · mdns"},
    {"hostname": "beebox", "ip": "10.0.0.125", "role": "companion · glusterfs"},
    {"hostname": "minisforum", "ip": "10.0.0.61", "role": "windows · office"},
    {"hostname": "router", "ip": "10.0.0.1", "role": "et12 · gateway"},
]


@router.get("/mesh")
async def mesh_status():
    """Get SSH mesh status — ping all nodes."""
    nodes = []
    for node in MESH_NODES:
        ping = run_cmd(["ping", "-c", "1", "-W", "1", node["ip"]])
        nodes.append({
            **node,
            "online": ping["success"],
        })
    return {"nodes": nodes}


@router.post("/mesh/add")
async def add_mesh_node(node: MeshNode):
    """Add a new node to the SSH mesh."""
    # Test connectivity
    ping = run_cmd(["ping", "-c", "1", "-W", "2", node.ip])
    if not ping["success"]:
        raise HTTPException(400, f"Cannot reach {node.ip}")

    MESH_NODES.append({
        "hostname": node.hostname,
        "ip": node.ip,
        "role": "new node",
    })
    return {"success": True, "message": f"{node.hostname} added to mesh"}


@router.delete("/mesh/{hostname}")
async def remove_mesh_node(hostname: str):
    """Remove a node from the SSH mesh."""
    global MESH_NODES
    before = len(MESH_NODES)
    MESH_NODES = [n for n in MESH_NODES if n["hostname"] != hostname]
    if len(MESH_NODES) == before:
        raise HTTPException(404, f"Node {hostname} not found")
    return {"success": True, "message": f"{hostname} removed from mesh"}


# ── Snapshots ──────────────────────────────────

@router.get("/snapshots")
async def list_snapshots():
    """List btrfs snapshots."""
    result = run_cmd(["sudo", "snapper", "-c", "root", "list", "--columns",
                      "number,date,description", "--machine-readable", "csv"])
    if not result["success"]:
        return {"snapshots": [], "error": result["stderr"]}

    snapshots = []
    for line in result["stdout"].split("\n")[1:]:  # skip header
        parts = line.split(",")
        if len(parts) >= 3:
            snapshots.append({
                "number": parts[0],
                "date": parts[1],
                "description": parts[2] if len(parts) > 2 else "",
            })
    return {"snapshots": snapshots[-10:]}  # last 10


@router.post("/snapshots/create")
async def create_snapshot(description: str = "manual snapshot"):
    """Create a btrfs snapshot."""
    result = run_cmd([
        "sudo", "snapper", "-c", "root", "create",
        "--type", "single", "--description", description
    ])
    return {
        "success": result["success"],
        "message": "Snapshot created" if result["success"] else result["stderr"],
    }


@router.post("/snapshots/rollback/{number}")
async def rollback_snapshot(number: int, confirmed: bool = False):
    """Rollback to a snapshot. Requires confirmation."""
    if not confirmed:
        return {
            "warning": True,
            "message": f"Rolling back to snapshot #{number} will revert all changes since that point. This cannot be undone. Send again with confirmed=true.",
        }

    result = run_cmd([
        "sudo", "snapper", "-c", "root", "undochange", str(number) + "..0"
    ])
    return {
        "success": result["success"],
        "message": f"Rolled back to snapshot #{number}" if result["success"] else result["stderr"],
    }


# ── Stack Freeze ───────────────────────────────

@router.get("/freeze")
async def freeze_status():
    """Get stack freeze status."""
    return {"frozen": STACK_FROZEN}


@router.post("/freeze/toggle")
async def toggle_freeze(confirmed: bool = False):
    """Toggle stack freeze."""
    global STACK_FROZEN
    if not confirmed:
        action = "THAW" if STACK_FROZEN else "FREEZE"
        return {
            "warning": True,
            "message": f"About to {action} the stack. Send again with confirmed=true.",
        }
    STACK_FROZEN = not STACK_FROZEN
    return {
        "frozen": STACK_FROZEN,
        "message": "Stack FROZEN" if STACK_FROZEN else "Stack THAWED — updates allowed",
    }
