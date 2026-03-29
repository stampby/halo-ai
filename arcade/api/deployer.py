"""
Arcade Deployer — One-click game server deployment engine.
Handles SteamCMD install, config generation, systemd setup, port forwarding.
"""

import subprocess
import json
import os
import shlex
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader

from .port_allocator import allocate, deallocate, list_allocations
from .router_manager import add_game_forwards, apply_firewall

GAMES_DIR = Path(__file__).parent.parent / "games"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "configs"
INSTALL_BASE = "/opt/arcade"
STEAMCMD_PATH = "/home/steam/steamcmd/steamcmd.sh"
STRIX_HOST = "10.0.0.131"
STRIX_USER = "bcloud"
SSH_OPTS = "-o ConnectTimeout=30 -o StrictHostKeyChecking=no"

jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _ssh_strix(cmd: str, timeout: int = 600) -> tuple[int, str]:
    """Execute command on Strix Halo via SSH."""
    full_cmd = f"ssh {SSH_OPTS} {STRIX_USER}@{STRIX_HOST} {shlex.quote(cmd)}"
    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "SSH timeout"


def load_game_template(game_id: str) -> dict:
    """Load a game template from the games directory."""
    template_path = GAMES_DIR / f"{game_id}.json"
    if not template_path.exists():
        raise FileNotFoundError(f"No game template for: {game_id}")
    with open(template_path) as f:
        return json.load(f)


def check_resources(template: dict) -> dict:
    """Check if target host has enough resources for deployment."""
    rc, output = _ssh_strix(
        "free -m | awk '/Mem:/{print $7}'; "
        "df -BG --output=avail /opt | tail -1 | tr -d ' G'; "
        "nproc"
    )
    if rc != 0:
        return {"ok": False, "error": "Cannot reach target host"}

    lines = output.strip().split("\n")
    available_ram_mb = int(lines[0])
    available_disk_gb = int(lines[1])
    available_cores = int(lines[2])

    min_ram = template.get("min_ram_mb", 2048)
    min_disk = template.get("min_disk_gb", 10)

    return {
        "ok": available_ram_mb >= min_ram and available_disk_gb >= min_disk,
        "ram_available_mb": available_ram_mb,
        "ram_required_mb": min_ram,
        "disk_available_gb": available_disk_gb,
        "disk_required_gb": min_disk,
        "cores": available_cores,
    }


def deploy_server(game_id: str, server_name: str = "",
                  cluster_id: str = "", maps: Optional[list] = None) -> dict:
    """
    Full one-click deployment:
    1. Allocate ports
    2. Check resources
    3. Install via SteamCMD
    4. Generate configs
    5. Create systemd service
    6. Configure port forwards
    7. Start server
    """
    template = load_game_template(game_id)
    results = {"steps": [], "success": False}

    # 1. Allocate ports
    try:
        allocation = allocate(game_id, server_name, cluster_id, STRIX_HOST)
        results["allocation"] = allocation
        results["steps"].append({"step": "allocate_ports", "ok": True})
    except Exception as e:
        results["steps"].append({"step": "allocate_ports", "ok": False, "error": str(e)})
        return results

    instance = allocation["instance"]
    ports = allocation["ports"]
    inst_dir = f"{INSTALL_BASE}/{game_id}-{instance}"

    # 2. Check resources
    resources = check_resources(template)
    results["resources"] = resources
    results["steps"].append({"step": "check_resources", "ok": resources["ok"],
                             "details": resources})
    if not resources["ok"]:
        deallocate(game_id, instance)
        return results

    # 3. Install via SteamCMD
    steam_app_id = template.get("steam_app_id")
    if steam_app_id:
        rc, output = _ssh_strix(
            f"sudo mkdir -p {inst_dir} && "
            f"sudo chown steam:steam {inst_dir} && "
            f"sudo -u steam {STEAMCMD_PATH} "
            f"+force_install_dir {inst_dir} "
            f"+login anonymous +app_update {steam_app_id} validate +quit"
        )
        results["steps"].append({
            "step": "steamcmd_install", "ok": rc == 0,
            "output": output[-500:] if output else ""
        })
        if rc != 0:
            deallocate(game_id, instance)
            return results

    # 4. Generate configs from templates
    config_files = template.get("config_files", [])
    for cfg in config_files:
        try:
            tmpl = jinja_env.get_template(cfg["template"])
            rendered = tmpl.render(
                server_name=server_name or f"[EarthC137] {template['display_name']}",
                game_port=ports["game"],
                query_port=ports["query"],
                rcon_port=ports["rcon"],
                web_port=ports["web"],
                cluster_id=cluster_id,
                cluster_dir=f"{INSTALL_BASE}/clusters/{cluster_id}" if cluster_id else "",
                admin_password="EarthC137Admin",
                instance=instance,
                ports=ports,
                **template.get("default_settings", {})
            )
            dest = f"{inst_dir}/{cfg['path']}"
            dest_dir = os.path.dirname(dest)
            _ssh_strix(f"sudo -u steam mkdir -p {dest_dir}")
            # Write config via heredoc
            _ssh_strix(
                f"sudo -u steam bash -c 'cat > {dest} << ARCADECFGEOF\n{rendered}\nARCADECFGEOF'"
            )
            results["steps"].append({"step": f"config_{cfg['template']}", "ok": True})
        except Exception as e:
            results["steps"].append({"step": f"config_{cfg['template']}",
                                     "ok": False, "error": str(e)})

    # 5. Create systemd service
    service_name = f"arcade-{game_id}-{instance}"
    startup_cmd = template["startup_command"]

    # Render startup command with port values
    for key, val in ports.items():
        startup_cmd = startup_cmd.replace(f"{{{{{key}}}}}", str(val))
    startup_cmd = startup_cmd.replace("{{server_name}}", server_name or f"EarthC137-{game_id}")
    startup_cmd = startup_cmd.replace("{{cluster_dir}}",
                                      f"{INSTALL_BASE}/clusters/{cluster_id}" if cluster_id else "")
    startup_cmd = startup_cmd.replace("{{install_dir}}", inst_dir)

    service_unit = f"""[Unit]
Description=Arcade: {template['display_name']} #{instance} - {server_name}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=steam
Group=steam
WorkingDirectory={inst_dir}
ExecStart={inst_dir}/{startup_cmd}
ExecStop=/bin/kill -INT $MAINPID
TimeoutStopSec=120
Restart=on-failure
RestartSec=30
LimitNOFILE=100000

[Install]
WantedBy=multi-user.target
"""
    rc, _ = _ssh_strix(
        f"echo '{service_unit}' | sudo tee /etc/systemd/system/{service_name}.service > /dev/null && "
        f"sudo systemctl daemon-reload"
    )
    results["steps"].append({"step": "systemd_service", "ok": rc == 0})

    # 6. Port forwards on router
    forwards = add_game_forwards(game_id, instance, ports, STRIX_HOST)
    apply_firewall()
    results["steps"].append({"step": "port_forwards", "ok": all(f["ok"] for f in forwards),
                             "forwards": forwards})

    # 7. Start server
    rc, _ = _ssh_strix(f"sudo systemctl enable --now {service_name}")
    results["steps"].append({"step": "start_server", "ok": rc == 0})

    results["success"] = all(s["ok"] for s in results["steps"])
    results["service_name"] = service_name
    results["connect_info"] = {
        "host": "1n1.freemyip.com",
        "game_port": ports["game"],
        "query_port": ports["query"],
    }

    return results


def destroy_server(game_id: str, instance: int) -> dict:
    """Full teardown: stop, remove service, remove files, free ports."""
    service_name = f"arcade-{game_id}-{instance}"
    inst_dir = f"{INSTALL_BASE}/{game_id}-{instance}"
    results = {"steps": []}

    # Stop and disable
    rc, _ = _ssh_strix(f"sudo systemctl disable --now {service_name} 2>/dev/null")
    results["steps"].append({"step": "stop_service", "ok": True})

    # Remove service file
    rc, _ = _ssh_strix(
        f"sudo rm -f /etc/systemd/system/{service_name}.service && "
        f"sudo systemctl daemon-reload"
    )
    results["steps"].append({"step": "remove_service", "ok": rc == 0})

    # Remove port forwards
    from .router_manager import remove_game_forwards
    remove_game_forwards(game_id, instance)
    apply_firewall()
    results["steps"].append({"step": "remove_forwards", "ok": True})

    # Free ports
    deallocate(game_id, instance)
    results["steps"].append({"step": "free_ports", "ok": True})

    # NOTE: not deleting game files automatically — too dangerous
    # User must manually: rm -rf {inst_dir}
    results["files_path"] = inst_dir
    results["note"] = f"Game files preserved at {inst_dir}. Delete manually if desired."

    return results


def server_status(game_id: str, instance: int) -> dict:
    """Get status of a deployed server."""
    service_name = f"arcade-{game_id}-{instance}"
    rc, output = _ssh_strix(
        f"systemctl is-active {service_name} 2>/dev/null; "
        f"systemctl show {service_name} --property=ActiveEnterTimestamp 2>/dev/null"
    )
    lines = output.strip().split("\n")
    active = lines[0] if lines else "unknown"
    uptime = lines[1].split("=", 1)[1] if len(lines) > 1 and "=" in lines[1] else ""

    return {
        "service": service_name,
        "status": active,
        "uptime_since": uptime,
    }
