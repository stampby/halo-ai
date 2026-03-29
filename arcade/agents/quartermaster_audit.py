"""
Quartermaster Weekly Audit Agent
Scrapes LinuxGSM + Steam for new/changed game servers.
Validates existing configs. Reports to Man Cave dashboard.

Run weekly via cron or systemd timer.
"""

import json
import subprocess
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

GAMES_DIR = Path(__file__).parent.parent / "games"
LINUXGSM_REPO = "/home/steam/LinuxGSM"
AUDIT_LOG = Path(__file__).parent.parent / "audit_reports"
STRIX_HOST = "10.0.0.131"


def get_linuxgsm_server_list() -> dict:
    """Parse LinuxGSM's serverlist.csv for all supported servers."""
    csv_path = Path(LINUXGSM_REPO) / "lgsm" / "data" / "serverlist.csv"

    # If running remotely, fetch via SSH
    if not csv_path.exists():
        result = subprocess.run(
            ["ssh", f"bcloud@{STRIX_HOST}",
             f"cat /home/steam/LinuxGSM/lgsm/data/serverlist.csv 2>/dev/null"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            # Try local
            if not csv_path.exists():
                return {}
        content = result.stdout
    else:
        content = csv_path.read_text()

    servers = {}
    for line in content.strip().split("\n"):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split(",")
        if len(parts) >= 4:
            # Format: shortname,servername,gamename,steamappid
            shortname = parts[0].strip()
            servername = parts[1].strip()
            gamename = parts[2].strip()
            appid = parts[3].strip() if len(parts) > 3 else ""
            servers[shortname] = {
                "linuxgsm_id": shortname,
                "server_name": servername,
                "game_name": gamename,
                "steam_app_id": appid,
            }
    return servers


def get_our_templates() -> dict:
    """Load all our game template files."""
    templates = {}
    for f in GAMES_DIR.glob("*.json"):
        with open(f) as fh:
            data = json.load(fh)
            templates[data["game_id"]] = data
    return templates


def find_new_games(lgsm_servers: dict, our_templates: dict) -> list:
    """Find games in LinuxGSM that we don't have templates for."""
    our_lgsm_ids = {t.get("linuxgsm_id") for t in our_templates.values() if t.get("linuxgsm_id")}
    our_steam_ids = {str(t.get("steam_app_id")) for t in our_templates.values() if t.get("steam_app_id")}

    new_games = []
    for shortname, info in lgsm_servers.items():
        if shortname not in our_lgsm_ids and info["steam_app_id"] not in our_steam_ids:
            new_games.append(info)
    return new_games


def validate_existing_configs(our_templates: dict, lgsm_servers: dict) -> list:
    """Check our configs against LinuxGSM for drift."""
    issues = []
    for game_id, template in our_templates.items():
        lgsm_id = template.get("linuxgsm_id")
        if lgsm_id and lgsm_id in lgsm_servers:
            lgsm_info = lgsm_servers[lgsm_id]
            # Check steam app ID matches
            if str(template.get("steam_app_id")) != lgsm_info["steam_app_id"]:
                issues.append({
                    "game_id": game_id,
                    "issue": "steam_app_id_mismatch",
                    "ours": template.get("steam_app_id"),
                    "lgsm": lgsm_info["steam_app_id"],
                })
    return issues


def check_port_conflicts() -> list:
    """Verify no port conflicts in the allocation database."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from api.port_allocator import list_allocations

    allocations = list_allocations()
    all_ports = {}
    conflicts = []

    for alloc in allocations:
        for port_key in ("game_port", "query_port", "rcon_port"):
            port = alloc.get(port_key)
            if port:
                if port in all_ports:
                    conflicts.append({
                        "port": port,
                        "server1": f"{all_ports[port]['game_id']}-{all_ports[port]['instance']}",
                        "server2": f"{alloc['game_id']}-{alloc['instance']}",
                    })
                else:
                    all_ports[port] = alloc

    return conflicts


def generate_report() -> dict:
    """Run full audit and generate report."""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "quartermaster",
    }

    # 1. Fetch LinuxGSM server list
    lgsm_servers = get_linuxgsm_server_list()
    report["lgsm_total_servers"] = len(lgsm_servers)

    # 2. Load our templates
    our_templates = get_our_templates()
    report["our_total_templates"] = len(our_templates)

    # 3. Find new games
    new_games = find_new_games(lgsm_servers, our_templates)
    report["new_games_available"] = len(new_games)
    report["new_games"] = new_games[:20]  # Top 20

    # 4. Validate configs
    issues = validate_existing_configs(our_templates, lgsm_servers)
    report["config_issues"] = issues
    report["configs_drifted"] = len(issues)

    # 5. Check port conflicts
    conflicts = check_port_conflicts()
    report["port_conflicts"] = conflicts
    report["conflict_count"] = len(conflicts)

    # 6. Summary
    report["summary"] = (
        f"Audit complete. "
        f"{len(new_games)} new games available, "
        f"{len(issues)} config issues, "
        f"{len(conflicts)} port conflicts."
    )

    return report


def save_report(report: dict):
    """Save audit report to disk."""
    AUDIT_LOG.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = AUDIT_LOG / f"audit_{date_str}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved: {path}")

    # Keep only last 12 reports (3 months of weekly)
    reports = sorted(AUDIT_LOG.glob("audit_*.json"))
    for old in reports[:-12]:
        old.unlink()


def main():
    print(f"[quartermaster] Starting weekly audit — {datetime.now().isoformat()}")
    report = generate_report()
    save_report(report)
    print(f"[quartermaster] {report['summary']}")

    if report["new_games_available"] > 0:
        print(f"[quartermaster] New games detected:")
        for g in report["new_games"][:10]:
            print(f"  - {g['game_name']} ({g['linuxgsm_id']}, steam:{g['steam_app_id']})")

    if report["configs_drifted"] > 0:
        print(f"[quartermaster] Config issues:")
        for i in report["config_issues"]:
            print(f"  - {i['game_id']}: {i['issue']}")

    if report["conflict_count"] > 0:
        print(f"[quartermaster] PORT CONFLICTS DETECTED:")
        for c in report["port_conflicts"]:
            print(f"  - Port {c['port']}: {c['server1']} vs {c['server2']}")

    return report


if __name__ == "__main__":
    main()
