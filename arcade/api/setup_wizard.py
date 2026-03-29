"""
Arcade Setup Wizard — Cosmos-inspired first-run configuration.
Detects hardware, configures firewall, sets up DDNS, creates admin.
Progressive disclosure: simple defaults, expandable advanced.
"""

import subprocess
import json
import os
import secrets
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

CONFIG_PATH = Path(__file__).parent.parent / "arcade.json"


class SetupConfig(BaseModel):
    # Step 1: Target host
    target_host: str = "10.0.0.131"
    target_user: str = "bcloud"
    steam_user: str = "steam"
    install_base: str = "/opt/arcade"
    steamcmd_path: str = "/home/steam/steamcmd/steamcmd.sh"
    linuxgsm_path: str = "/home/steam/LinuxGSM"

    # Step 2: Network
    router_host: str = "10.0.0.1"
    router_user: str = "BCloud"
    ddns_hostname: str = "1n1.freemyip.com"
    wireguard_enabled: bool = True
    wireguard_port: int = 51820
    wireguard_subnet: str = "10.100.0.0/24"

    # Step 3: Security
    admin_password: str = ""
    whitelist_only_default: bool = True
    api_key: str = ""

    # Step 4: Defaults
    default_max_players: int = 20
    default_difficulty: float = 5.0
    motd: str = "Welcome to Earth C-137! Designed and built by the architect."

    # Auto-detected
    target_ram_mb: int = 0
    target_disk_gb: int = 0
    target_cores: int = 0
    setup_complete: bool = False


def detect_hardware(host: str, user: str) -> dict:
    """Auto-detect target host hardware."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", f"{user}@{host}",
             "free -m | awk '/Mem:/{print $2,$7}'; "
             "df -BG --output=avail /opt 2>/dev/null | tail -1 | tr -d ' G'; "
             "nproc; "
             "hostname; "
             "cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2"],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split("\n")
        mem = lines[0].split() if lines else ["0", "0"]
        return {
            "ok": result.returncode == 0,
            "total_ram_mb": int(mem[0]) if len(mem) > 0 else 0,
            "available_ram_mb": int(mem[1]) if len(mem) > 1 else 0,
            "disk_gb": int(lines[1]) if len(lines) > 1 else 0,
            "cores": int(lines[2]) if len(lines) > 2 else 0,
            "hostname": lines[3].strip() if len(lines) > 3 else "unknown",
            "cpu": lines[4].strip() if len(lines) > 4 else "unknown",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def detect_network(router_host: str, router_user: str) -> dict:
    """Auto-detect router and network configuration."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", f"{router_user}@{router_host}",
             "nvram get ddns_hostname_x; "
             "nvram get wan0_ipaddr; "
             "nvram get dnspriv_enable; "
             "nvram get qos_enable; "
             "nvram get vts_rulelist | wc -c"],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split("\n")
        return {
            "ok": result.returncode == 0,
            "ddns_hostname": lines[0] if lines else "",
            "wan_ip": lines[1] if len(lines) > 1 else "",
            "dns_over_tls": lines[2] == "1" if len(lines) > 2 else False,
            "qos_enabled": lines[3] == "1" if len(lines) > 3 else False,
            "port_forwards_size": int(lines[4]) if len(lines) > 4 else 0,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def detect_steamcmd(host: str, user: str) -> dict:
    """Check if SteamCMD is installed on target."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", f"{user}@{host}",
             "ls /home/steam/steamcmd/steamcmd.sh 2>/dev/null && echo 'found' || echo 'missing'; "
             "ls /home/steam/LinuxGSM/linuxgsm.sh 2>/dev/null && echo 'found' || echo 'missing'"],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split("\n")
        return {
            "steamcmd": lines[0] == "found" if lines else False,
            "linuxgsm": lines[1] == "found" if len(lines) > 1 else False,
        }
    except Exception as e:
        return {"steamcmd": False, "linuxgsm": False, "error": str(e)}


def detect_wireguard() -> dict:
    """Check WireGuard status on this machine."""
    try:
        result = subprocess.run(
            ["wg", "show", "wg0"], capture_output=True, text=True, timeout=5
        )
        peers = result.stdout.count("peer:")
        return {
            "ok": result.returncode == 0,
            "interface": "wg0",
            "peers": peers,
        }
    except Exception:
        return {"ok": False, "peers": 0}


def run_full_detection(config: SetupConfig) -> dict:
    """Run all detection steps and return complete status."""
    return {
        "hardware": detect_hardware(config.target_host, config.target_user),
        "network": detect_network(config.router_host, config.router_user),
        "steamcmd": detect_steamcmd(config.target_host, config.target_user),
        "wireguard": detect_wireguard(),
    }


def save_config(config: SetupConfig):
    """Save setup config to disk."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config.model_dump(), f, indent=2)


def load_config() -> SetupConfig:
    """Load setup config from disk."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return SetupConfig(**json.load(f))
    return SetupConfig()


def is_setup_complete() -> bool:
    """Check if first-run setup has been completed."""
    if CONFIG_PATH.exists():
        config = load_config()
        return config.setup_complete
    return False


def complete_setup(config: SetupConfig) -> dict:
    """Finalize setup: create directories, generate API key, save config."""
    # Generate API key if not set
    if not config.api_key:
        config.api_key = secrets.token_urlsafe(32)

    # Generate admin password if not set
    if not config.admin_password:
        config.admin_password = secrets.token_urlsafe(16)

    # Create directories on target
    subprocess.run(
        ["ssh", "-o", "ConnectTimeout=10",
         f"{config.target_user}@{config.target_host}",
         f"sudo mkdir -p {config.install_base}/clusters && "
         f"sudo chown -R {config.steam_user}:{config.steam_user} {config.install_base}"],
        capture_output=True, timeout=15
    )

    # Update detected hardware
    hw = detect_hardware(config.target_host, config.target_user)
    if hw["ok"]:
        config.target_ram_mb = hw["total_ram_mb"]
        config.target_disk_gb = hw["disk_gb"]
        config.target_cores = hw["cores"]

    config.setup_complete = True
    save_config(config)

    return {
        "ok": True,
        "api_key": config.api_key,
        "admin_password": config.admin_password,
        "target": f"{config.target_user}@{config.target_host}",
        "ddns": config.ddns_hostname,
    }
