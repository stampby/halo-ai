"""
Arcade Router Manager — Auto-configures port forwards on ASUS routers via SSH.
Pushes nvram rules and restarts firewall. Zero manual config.
"""

import subprocess
import shlex
from typing import Optional


ROUTER_HOST = "10.0.0.1"
ROUTER_USER = "BCloud"
SSH_OPTS = "-o ConnectTimeout=10 -o StrictHostKeyChecking=no"


def _ssh(cmd: str, timeout: int = 15) -> tuple[int, str]:
    """Execute command on router via SSH."""
    full_cmd = f"ssh {SSH_OPTS} {ROUTER_USER}@{ROUTER_HOST} {shlex.quote(cmd)}"
    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, "SSH timeout"


def get_current_forwards() -> str:
    """Get current port forwarding rules from router."""
    rc, output = _ssh("nvram get vts_rulelist")
    return output.strip() if rc == 0 else ""


def add_port_forward(name: str, port: int, protocol: str, target_ip: str,
                     target_port: Optional[int] = None) -> bool:
    """Add a single port forward rule to the router."""
    target_port = target_port or port
    proto = protocol.upper()

    # ASUS vts_rulelist format: <name>protocol>extport>intip>intport>
    rule = f"<{name}>{proto}>{port}>{target_ip}>{target_port}>"

    # Get existing rules and append
    current = get_current_forwards()
    if rule in current:
        return True  # Already exists

    new_rules = current + rule
    rc, output = _ssh(f"nvram set vts_rulelist='{new_rules}' && nvram commit")
    return rc == 0


def add_game_forwards(game_id: str, instance: int, ports: dict,
                      target_ip: str) -> list[dict]:
    """Add all port forwards for a game server instance."""
    results = []
    prefix = f"{game_id}-{instance}"

    # Game port (UDP)
    results.append({
        "port": ports["game"], "protocol": "UDP",
        "ok": add_port_forward(f"{prefix}-game", ports["game"], "UDP", target_ip)
    })

    # Query port (UDP)
    results.append({
        "port": ports["query"], "protocol": "UDP",
        "ok": add_port_forward(f"{prefix}-query", ports["query"], "UDP", target_ip)
    })

    # RCON port (TCP)
    results.append({
        "port": ports["rcon"], "protocol": "TCP",
        "ok": add_port_forward(f"{prefix}-rcon", ports["rcon"], "TCP", target_ip)
    })

    # Web admin if applicable (TCP)
    if ports.get("web"):
        results.append({
            "port": ports["web"], "protocol": "TCP",
            "ok": add_port_forward(f"{prefix}-web", ports["web"], "TCP", target_ip)
        })

    return results


def remove_game_forwards(game_id: str, instance: int) -> bool:
    """Remove all port forwards for a game server instance."""
    prefix = f"{game_id}-{instance}"
    current = get_current_forwards()

    # Remove all rules matching this prefix
    import re
    pattern = f"<{re.escape(prefix)}-[^>]*>[^>]*>[^>]*>[^>]*>[^>]*>"
    cleaned = re.sub(pattern, "", current)

    if cleaned != current:
        rc, _ = _ssh(f"nvram set vts_rulelist='{cleaned}' && nvram commit")
        return rc == 0
    return True


def apply_firewall() -> bool:
    """Restart router firewall to apply port forward changes."""
    rc, _ = _ssh("service restart_firewall")
    return rc == 0
