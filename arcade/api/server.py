"""
Arcade API — FastAPI server for game server management.
Integrates with Man Cave as a panel tile.
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json

from .port_allocator import (
    allocate, deallocate, list_allocations, get_full_port_map, PORT_MAP
)
from .deployer import (
    deploy_server, destroy_server, server_status,
    load_game_template, check_resources
)
from .router_manager import get_current_forwards

app = FastAPI(
    title="Arcade — Game Server Management",
    description="One-click game server deployment. Designed and built by the architect.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Pydantic Models ---

class DeployRequest(BaseModel):
    game_id: str
    server_name: str = ""
    cluster_id: str = ""
    maps: Optional[list[str]] = None
    whitelist_only: bool = True

class WhitelistRequest(BaseModel):
    steam_id: str
    player_name: str = ""

class ServerAction(BaseModel):
    action: str  # start, stop, restart


# --- Dashboard ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main arcade dashboard."""
    allocations = list_allocations()
    games = []
    for game_id in PORT_MAP:
        try:
            template = load_game_template(game_id)
            games.append(template)
        except FileNotFoundError:
            pass
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "allocations": allocations,
        "available_games": games,
    })


# --- Game Catalog ---

@app.get("/api/games")
async def list_games():
    """List all available game templates."""
    games = []
    for game_id in PORT_MAP:
        try:
            template = load_game_template(game_id)
            games.append({
                "game_id": game_id,
                "display_name": template["display_name"],
                "category": PORT_MAP[game_id][1],
                "steam_app_id": template.get("steam_app_id"),
                "min_ram_mb": template.get("min_ram_mb", 2048),
                "min_disk_gb": template.get("min_disk_gb", 10),
                "supports_clustering": template.get("supports_clustering", False),
                "maps": template.get("maps", []),
            })
        except FileNotFoundError:
            continue
    return {"games": games}


@app.get("/api/games/{game_id}")
async def get_game(game_id: str):
    """Get details for a specific game."""
    try:
        return load_game_template(game_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Game template not found: {game_id}")


# --- Server Management ---

@app.get("/api/servers")
async def list_servers():
    """List all deployed server instances."""
    allocations = list_allocations()
    servers = []
    for alloc in allocations:
        status = server_status(alloc["game_id"], alloc["instance"])
        servers.append({**alloc, **status})
    return {"servers": servers}


@app.post("/api/servers/deploy")
async def deploy(req: DeployRequest):
    """One-click deploy a game server."""
    try:
        result = deploy_server(
            game_id=req.game_id,
            server_name=req.server_name,
            cluster_id=req.cluster_id,
            maps=req.maps,
        )
        if not result["success"]:
            raise HTTPException(500, result)
        return result
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(409, str(e))


@app.post("/api/servers/{game_id}/{instance}/action")
async def server_action(game_id: str, instance: int, action: ServerAction):
    """Start, stop, or restart a server."""
    service_name = f"arcade-{game_id}-{instance}"
    from .deployer import _ssh_strix

    if action.action not in ("start", "stop", "restart"):
        raise HTTPException(400, "Action must be start, stop, or restart")

    rc, output = _ssh_strix(f"sudo systemctl {action.action} {service_name}")
    if rc != 0:
        raise HTTPException(500, f"Failed to {action.action}: {output}")

    return {"ok": True, "action": action.action, "service": service_name}


@app.delete("/api/servers/{game_id}/{instance}")
async def remove_server(game_id: str, instance: int):
    """Full teardown of a server instance."""
    result = destroy_server(game_id, instance)
    return result


@app.get("/api/servers/{game_id}/{instance}/status")
async def get_server_status(game_id: str, instance: int):
    """Get status of a specific server."""
    return server_status(game_id, instance)


# --- Port Map ---

@app.get("/api/ports")
async def port_map():
    """Full port allocation map."""
    return get_full_port_map()


@app.get("/api/ports/forwards")
async def port_forwards():
    """Current router port forward rules."""
    return {"rules": get_current_forwards()}


# --- Resources ---

@app.get("/api/resources")
async def resources():
    """Check available resources on target host."""
    # Use a lightweight template for resource check
    return check_resources({"min_ram_mb": 0, "min_disk_gb": 0})


# --- Whitelist ---

@app.get("/api/servers/{game_id}/{instance}/whitelist")
async def get_whitelist(game_id: str, instance: int):
    """Get whitelist for a server."""
    from .deployer import _ssh_strix
    inst_dir = f"/opt/arcade/{game_id}-{instance}"
    # Try common whitelist file locations
    rc, output = _ssh_strix(
        f"cat {inst_dir}/whitelist.txt 2>/dev/null || "
        f"cat {inst_dir}/ShooterGame/Saved/PlayersJoinNoCheckList.txt 2>/dev/null || "
        f"echo ''"
    )
    players = [line.strip() for line in output.strip().split("\n")
               if line.strip() and not line.startswith("#")]
    return {"players": players}


@app.post("/api/servers/{game_id}/{instance}/whitelist")
async def add_to_whitelist(game_id: str, instance: int, req: WhitelistRequest):
    """Add a player to the whitelist."""
    from .deployer import _ssh_strix
    inst_dir = f"/opt/arcade/{game_id}-{instance}"
    entry = f"{req.steam_id}  # {req.player_name}"
    _ssh_strix(
        f"echo '{entry}' | sudo -u steam tee -a "
        f"{inst_dir}/ShooterGame/Saved/PlayersJoinNoCheckList.txt > /dev/null"
    )
    return {"ok": True, "added": req.steam_id}


# --- WebSocket for live logs ---

@app.websocket("/ws/logs/{game_id}/{instance}")
async def log_stream(websocket: WebSocket, game_id: str, instance: int):
    """Stream live server logs via WebSocket."""
    await websocket.accept()
    service_name = f"arcade-{game_id}-{instance}"
    process = await asyncio.create_subprocess_exec(
        "ssh", f"{STRIX_USER}@{STRIX_HOST}",
        f"journalctl -u {service_name} -f --no-hostname -o cat",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            await websocket.send_text(line.decode().rstrip())
    except Exception:
        pass
    finally:
        process.kill()
        await websocket.close()


STRIX_USER = "bcloud"


# --- Setup Wizard ---

from .setup_wizard import (
    SetupConfig, run_full_detection, complete_setup as do_complete_setup,
    load_config, is_setup_complete
)

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    """Setup wizard page."""
    if is_setup_complete():
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/")
    return templates.TemplateResponse("setup.html", {"request": request})


@app.get("/api/setup/detect")
async def detect_all():
    """Run full hardware/network/software detection."""
    config = load_config()
    return run_full_detection(config)


class SetupComplete(BaseModel):
    admin_password: str = ""
    whitelist_only_default: bool = True
    default_max_players: int = 20
    motd: str = ""
    wireguard_enabled: bool = True


@app.post("/api/setup/complete")
async def finish_setup(req: SetupComplete):
    """Complete the setup wizard."""
    config = load_config()
    config.admin_password = req.admin_password
    config.whitelist_only_default = req.whitelist_only_default
    config.default_max_players = req.default_max_players
    config.motd = req.motd or config.motd
    config.wireguard_enabled = req.wireguard_enabled
    return do_complete_setup(config)


# --- WireGuard Invites ---

from .wireguard_invites import create_invite, list_invites, revoke_invite

class InviteRequest(BaseModel):
    player_name: str
    steam_id: str = ""


@app.get("/api/invites")
async def get_invites():
    """List all VPN invites."""
    return {"invites": list_invites()}


@app.post("/api/invites")
async def new_invite(req: InviteRequest):
    """Create a WireGuard invite for a friend."""
    try:
        result = create_invite(req.player_name, req.steam_id)
        return result
    except RuntimeError as e:
        raise HTTPException(500, str(e))


@app.delete("/api/invites/{player_name}")
async def remove_invite(player_name: str):
    """Revoke a friend's VPN access."""
    ok = revoke_invite(player_name)
    if not ok:
        raise HTTPException(404, "Invite not found")
    return {"ok": True}
