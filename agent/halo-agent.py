#!/usr/bin/env python3
"""
halo-ai Agent
Autonomous service guardian for the halo-ai stack on Strix Halo.

- Keeps all services alive
- Monitors GPU, memory, disk, thermals
- Checks for upstream updates and security patches
- Auto-repairs failures
- Only reports when it CANNOT fix something
"""

import subprocess
import json
import time
import logging
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

# ── Configuration ──────────────────────────────────────
DATA_DIR = Path("/srv/ai/agent/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = DATA_DIR / "halo-agent.log"
STATE_FILE = DATA_DIR / "state.json"
UPDATE_CHECK_INTERVAL = 3600  # Check for updates every hour
SERVICE_CHECK_INTERVAL = 30   # Check services every 30 seconds
HEALTH_CHECK_INTERVAL = 60    # Check GPU/mem/disk every 60 seconds
MAX_RESTART_ATTEMPTS = 3
RESTART_COOLDOWN = 300        # 5 min cooldown after 3 failed restarts

# ── Logging ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("halo-agent")

# ── Services ───────────────────────────────────────────
SERVICES = {
    "halo-llama-server": {"port": 8081, "health": "/health", "critical": True, "gpu": True},
    "halo-lemonade": {"port": 8080, "health": "/health", "critical": True, "gpu": False},
    "halo-open-webui": {"port": 3000, "health": "/health", "critical": True, "gpu": False},
    "halo-vane": {"port": 3001, "health": "/", "critical": False, "gpu": False},
    "halo-searxng": {"port": 8888, "health": "/", "critical": False, "gpu": False},
    "halo-qdrant": {"port": 6333, "health": "/", "critical": False, "gpu": False},
    "halo-n8n": {"port": 5678, "health": "/healthz", "critical": False, "gpu": False},
    "halo-comfyui": {"port": 8188, "health": "/", "critical": False, "gpu": True},
    "halo-dashboard-api": {"port": 3002, "health": "/health", "critical": False, "gpu": False},
    "halo-dashboard-ui": {"port": 3003, "health": "/", "critical": False, "gpu": False},
}

REPOS = {
    "llama-cpp": "/srv/ai/llama-cpp",
    "lemonade": "/srv/ai/lemonade",
    "open-webui": "/srv/ai/open-webui",
    "vane": "/srv/ai/vane",
    "searxng": "/srv/ai/searxng",
    "qdrant": "/srv/ai/qdrant",
    "n8n": "/srv/ai/n8n",
    "comfyui": "/srv/ai/comfyui",
    "whisper-cpp": "/srv/ai/whisper-cpp",
    "kokoro": "/srv/ai/kokoro",
}

# ── State Management ───────────────────────────────────
@dataclass
class ServiceState:
    restart_count: int = 0
    last_restart: Optional[str] = None
    last_failure: Optional[str] = None
    cooldown_until: Optional[str] = None
    consecutive_failures: int = 0

@dataclass  
class AgentState:
    services: dict = field(default_factory=dict)
    last_update_check: Optional[str] = None
    last_health_report: Optional[str] = None
    updates_available: dict = field(default_factory=dict)
    total_repairs: int = 0
    total_failures: int = 0
    started_at: Optional[str] = None

def load_state() -> AgentState:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            state = AgentState()
            state.__dict__.update(data)
            return state
        except Exception:
            pass
    return AgentState(started_at=datetime.now().isoformat())

def save_state(state: AgentState):
    STATE_FILE.write_text(json.dumps(state.__dict__, indent=2, default=str))

# ── Shell Helpers ──────────────────────────────────────
def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)

def notify(title, message, level="critical"):
    """Send notification — only called when agent CANNOT fix something."""
    log.error(f"ALERT: {title} — {message}")
    # Desktop notification
    run(f'notify-send -u {level} "halo-ai agent" "{title}: {message}"')
    # systemd journal
    run(f'logger -t halo-agent -p user.err "{title}: {message}"')

# ── Service Monitoring ─────────────────────────────────
def check_service(name, config):
    """Check if a service is running and healthy."""
    code, out, _ = run(f"systemctl is-active {name}")
    if out != "active":
        return False, "not running"
    
    # HTTP health check
    port = config["port"]
    health = config["health"]
    code, out, _ = run(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 5 http://127.0.0.1:{port}{health}")
    if code != 0 or out not in ("200", "301", "302", "307", "308"):
        return False, f"health check failed (HTTP {out})"
    
    return True, "healthy"

def snapshot_before_repair(reason):
    """Take a Btrfs snapshot before any repair action."""
    run(f'snapper -c root create --type single --cleanup-algorithm number '
        f'--description "halo-agent pre-repair: {reason} {datetime.now():%Y%m%d-%H%M%S}"')

def repair_service(name, config, state: AgentState):
    """Attempt to repair a failed service."""
    svc_state = state.services.get(name, ServiceState().__dict__)
    restart_count = svc_state.get("restart_count", 0)
    cooldown = svc_state.get("cooldown_until")
    
    # Check cooldown
    if cooldown:
        cooldown_time = datetime.fromisoformat(cooldown)
        if datetime.now() < cooldown_time:
            return False  # Still in cooldown, don't spam restarts
    
    if restart_count >= MAX_RESTART_ATTEMPTS:
        # Enter cooldown
        svc_state["cooldown_until"] = (datetime.now() + timedelta(seconds=RESTART_COOLDOWN)).isoformat()
        svc_state["restart_count"] = 0
        state.services[name] = svc_state
        state.total_failures += 1
        notify("Service repair failed", f"{name} failed {MAX_RESTART_ATTEMPTS} restart attempts. Cooldown {RESTART_COOLDOWN}s.")
        return False
    
    # Snapshot before repair
    snapshot_before_repair(f"{name} restart")
    
    # Try restart
    log.info(f"Restarting {name} (attempt {restart_count + 1}/{MAX_RESTART_ATTEMPTS})")
    code, _, err = run(f"systemctl restart {name}", timeout=60)
    time.sleep(5)
    
    healthy, status = check_service(name, config)
    
    svc_state["restart_count"] = restart_count + 1
    svc_state["last_restart"] = datetime.now().isoformat()
    
    if healthy:
        log.info(f"Repaired {name} successfully")
        svc_state["restart_count"] = 0
        svc_state["consecutive_failures"] = 0
        svc_state["cooldown_until"] = None
        state.total_repairs += 1
    else:
        svc_state["last_failure"] = datetime.now().isoformat()
        svc_state["consecutive_failures"] = svc_state.get("consecutive_failures", 0) + 1
        log.warning(f"Repair attempt for {name} failed: {status}")
    
    state.services[name] = svc_state
    return healthy

# ── GPU Monitoring ─────────────────────────────────────
def check_gpu():
    """Check GPU health."""
    issues = []
    
    # Check /dev/kfd exists
    if not Path("/dev/kfd").exists():
        issues.append("GPU device /dev/kfd missing — possible driver crash")
    
    # Check temperature
    for hwmon in Path("/sys/class/hwmon").iterdir():
        name_file = hwmon / "name"
        if name_file.exists() and "amdgpu" in name_file.read_text():
            temp_file = hwmon / "temp1_input"
            if temp_file.exists():
                temp = int(temp_file.read_text().strip()) // 1000
                if temp > 90:
                    issues.append(f"GPU temperature critical: {temp}°C")
                elif temp > 80:
                    log.warning(f"GPU temperature elevated: {temp}°C")
    
    # Check amdgpu module
    code, out, _ = run("lsmod | grep amdgpu")
    if code != 0:
        issues.append("amdgpu kernel module not loaded")
    
    return issues

# ── System Monitoring ──────────────────────────────────
def check_system():
    """Check system health."""
    issues = []
    
    # Memory
    code, out, _ = run("awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo")
    if out and int(out) < 4096:
        issues.append(f"Available memory critically low: {out}MB")
    
    # Disk
    code, out, _ = run("df /srv/ai --output=pcent | tail -1 | tr -d ' %'")
    if out and int(out) > 90:
        issues.append(f"Disk usage at {out}% on /srv/ai")
    
    # CPU governor (should be performance)
    code, out, _ = run("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if out != "performance":
        log.info(f"CPU governor is '{out}', setting to performance")
        run("for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance | tee $c > /dev/null; done")
    
    return issues

# ── Update Checking ────────────────────────────────────
def check_updates(state: AgentState):
    """Check for upstream updates (non-destructive, just reports)."""
    updates = {}
    
    for name, path in REPOS.items():
        git_dir = Path(path) / ".git"
        if not git_dir.exists():
            continue
        
        code, _, _ = run(f"cd {path} && git fetch --quiet", timeout=30)
        if code != 0:
            continue
        
        code, out, _ = run(f"cd {path} && git rev-list --count HEAD..@{{u}}")
        if out and int(out) > 0:
            code, hash_out, _ = run(f"cd {path} && git rev-parse --short HEAD")
            updates[name] = {"behind": int(out), "current_commit": hash_out}
    
    # System packages
    code, out, _ = run("pacman -Qu 2>/dev/null | wc -l")
    if out and int(out) > 0:
        updates["system-packages"] = {"count": int(out)}
    
    # Kernel
    code, running, _ = run("uname -r")
    code, installed, _ = run("pacman -Q linux 2>/dev/null | awk '{print $2}'")
    if running and installed:
        installed_fmt = installed.replace(".arch", "-arch")
        if running != installed_fmt:
            updates["kernel"] = {"running": running, "installed": installed}
    
    state.updates_available = updates
    state.last_update_check = datetime.now().isoformat()
    
    if updates:
        update_summary = ", ".join(
            f"{k}: {v.get('behind', v.get('count', 'new'))} behind" 
            for k, v in updates.items()
        )
        log.info(f"Updates available: {update_summary}")
    
    return updates

# ── Inference Verification ─────────────────────────────
def verify_inference():
    """Quick inference test to ensure LLM is actually working."""
    code, out, _ = run(
        'curl -s http://127.0.0.1:8081/v1/chat/completions '
        '-H "Content-Type: application/json" '
        '-d \'{"model":"q","messages":[{"role":"user","content":"hi /no_think"}],"max_tokens":5,"temperature":0}\'',
        timeout=30
    )
    if code != 0:
        return False, 0
    
    try:
        result = json.loads(out)
        tok_s = result["timings"]["predicted_per_second"]
        return True, tok_s
    except (json.JSONDecodeError, KeyError):
        return False, 0

# ── Main Loop ──────────────────────────────────────────
def main():
    state = load_state()
    if not state.started_at:
        state.started_at = datetime.now().isoformat()
    
    log.info("=" * 50)
    log.info("halo-ai agent starting")
    log.info(f"Monitoring {len(SERVICES)} services, {len(REPOS)} repos")
    log.info("=" * 50)
    
    last_service_check = 0
    last_health_check = 0
    last_update_check = 0
    last_inference_check = 0
    
    while True:
        now = time.time()
        
        # ── Service checks (every 30s) ────────────────
        if now - last_service_check >= SERVICE_CHECK_INTERVAL:
            for name, config in SERVICES.items():
                healthy, status = check_service(name, config)
                if not healthy:
                    log.warning(f"{name}: {status}")
                    repair_service(name, config, state)
            last_service_check = now
        
        # ── Health checks (every 60s) ─────────────────
        if now - last_health_check >= HEALTH_CHECK_INTERVAL:
            gpu_issues = check_gpu()
            sys_issues = check_system()
            
            for issue in gpu_issues + sys_issues:
                notify("System health", issue)
            
            last_health_check = now
        
        # ── Inference verification (every 5 min) ──────
        if now - last_inference_check >= 300:
            ok, tok_s = verify_inference()
            if not ok:
                log.warning("Inference verification failed")
                # Don't alert — service check will handle restart
            elif tok_s < 50:
                log.warning(f"Inference degraded: {tok_s:.1f} tok/s (expected >80)")
            last_inference_check = now
        
        # ── Update checks (every hour) ────────────────
        if now - last_update_check >= UPDATE_CHECK_INTERVAL:
            check_updates(state)
            last_update_check = now
        
        # ── Save state ────────────────────────────────
        save_state(state)
        
        # ── Sleep ─────────────────────────────────────
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Agent stopped by user")
    except Exception as e:
        log.error(f"Agent crashed: {e}", exc_info=True)
        notify("Agent crashed", str(e))
        sys.exit(1)
