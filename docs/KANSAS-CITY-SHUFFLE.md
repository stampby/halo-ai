# Kansas City Shuffle — Ring Bus

**Bracket's SSH Mixer** — Zero-cost distributed infrastructure across the halo-ai machine mesh.

> Designed and built by the architect.

## Overview

The Kansas City Shuffle is the SSH mesh management system for halo-ai. It connects all machines in a full-mesh topology (Ring Bus), monitors connectivity, auto-repairs broken links, and provides a distributed filesystem (ClusterFS via GlusterFS) across the entire fleet.

**No cloud. No monthly bills. No single point of failure. Just your hard drives.**

## Ring Bus Topology

```
                    ┌──────────┐
                    │  ryzen   │
                    │ 10.0.0.61│
                    │ primary  │
                    └────┬─────┘
                   ╱      │      ╲
                 SSH     SSH      SSH
                ╱        │          ╲
     ┌──────────────┐   │    ┌──────────┐
     │  strix-halo  │───┼────│  sligar  │
     │  10.0.0.131  │   │    │ 10.0.0.x │
     │  GPU / ops   │───┼────│ secondary│
     └──────────────┘   │    └──────────┘
                ╲        │        ╱
                 SSH     SSH    SSH
                   ╲     │    ╱
                  ┌──────────────┐
                  │  minisforum  │
                  │ 10.0.0.185   │
                  │  Windows     │
                  └──────────────┘
```

### Machines

| Machine | IP | Role | Hardware |
|---------|-----|------|----------|
| **ryzen** | 10.0.0.61 | Primary workstation | Ryzen 9800X3D, Navi 48 |
| **strix-halo** | 10.0.0.131 | GPU server, ops center | Ryzen AI MAX+ 395, 128GB |
| **sligar** | TBD | Secondary workloads | i7-8700K, GTX 1080Ti |
| **minisforum** | 10.0.0.185 | Windows workstation | Needs Win11 reinstall |

### Connections (12 bidirectional links — full mesh)

- ryzen ↔ strix-halo
- ryzen ↔ sligar
- ryzen ↔ minisforum
- strix-halo ↔ sligar
- strix-halo ↔ minisforum
- sligar ↔ minisforum

## ClusterFS (GlusterFS)

Distributed filesystem across all three machines. Zero configuration required — the Kansas City Shuffle agent handles setup, monitoring, and repair automatically.

### What it does

- Pools available disk space from all machines into a shared `/shared/` mount
- Replicated volume — data exists on multiple machines simultaneously
- No single point of failure — if one machine goes down, files are still accessible
- Auto-heals when machines reconnect

### Peer setup (handled by agent)

```bash
# On each machine (automated):
gluster peer probe 10.0.0.61   # ryzen
gluster peer probe 10.0.0.131  # strix-halo
gluster peer probe <sligar-ip> # sligar

# Create replicated volume:
gluster volume create pool replica 3 \
    10.0.0.61:/gluster/brick1/data \
    10.0.0.131:/gluster/brick1/data \
    <sligar-ip>:/gluster/brick1/data

gluster volume start pool
mount -t glusterfs localhost:pool /pool
```

## Man Cave Panel

The Kansas City Shuffle panel lives on the Man Cave landing page (`/cave/`). It shows:

- **Triangle visualization** — 3 machine nodes with live status dots (green/orange/red)
- **Connection lines** — SVG lines between nodes change color based on SSH health
- **Latency readout** — SSH round-trip time to each machine
- **Ring health** — overall status: healthy / degraded / down
- **ClusterFS status** — GlusterFS volume health, free space, peer count
- **Controls** — test all connections, repair individual machines

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/kcs/status` | GET | Full ring bus health (15s cache) |
| `/api/kcs/{machine}/test` | POST | Probe single machine |
| `/api/kcs/repair/{machine}` | POST | Attempt SSH repair |
| `/api/kcs/test-all` | POST | Force refresh all (bypasses cache) |
| `/api/kcs/gluster` | GET | GlusterFS status, volumes, peers, pool size |

### Status response structure

```json
{
  "ring_health": "healthy",
  "machines": {
    "ryzen": {
      "name": "ryzen",
      "ip": "192.168.50.185",
      "status": "up",
      "ping": {"reachable": true, "latency_ms": 0.8},
      "ssh": {"reachable": true, "latency_ms": 45.2, "error": ""}
    }
  },
  "connections": [
    {"source": "ryzen", "target": "strix-halo", "forward": "up", "reverse": "up"}
  ],
  "connections_up": 6,
  "connections_total": 6
}
```

## Auto-Repair Agent

The halo-agent (autonomous service guardian) monitors the ring bus every 60 seconds and GlusterFS every 120 seconds.

### Ring Bus repair flow

1. SSH probe to each machine fails
2. Agent clears stale `known_hosts` entry
3. Retries SSH connection
4. If restored → reports `ringbus_repaired` to activity feed
5. If still down → reports `ringbus_repair_failed` as critical
6. On natural recovery → reports `ringbus_recovered`

### GlusterFS repair flow

1. Check `gluster volume status all`
2. If down → restart `glusterd` service
3. Check peer status for disconnected nodes
4. Report changes to activity feed and message bus

## Troubleshooting

### Connection shows red (SSH down)

1. Check if the machine is powered on and connected to the network
2. Try manual SSH: `ssh bcloud@10.0.0.61`
3. Check SSH key: `ssh-add -l` (should show ed25519 key)
4. Check firewall on target: `sudo nft list ruleset | grep ssh`
5. Check sshd is running: `systemctl status sshd`

### Connection shows orange (ping OK, SSH down)

1. Machine is reachable but SSH is refusing connections
2. Check sshd: `systemctl status sshd` on the target
3. Check authorized_keys: `cat ~/.ssh/authorized_keys` on the target
4. Check if host key changed: `ssh-keygen -R <ip>` then retry

### ClusterFS shows "not installed"

GlusterFS needs to be installed on all three machines:

```bash
# On Arch Linux:
sudo pacman -S glusterfs
sudo systemctl enable --now glusterd
```

### ClusterFS shows degraded

1. Check which peers are disconnected: `gluster peer status`
2. Check volume: `gluster volume info shared`
3. Heal: `gluster volume heal shared`

### Ring bus keeps flapping

1. Check network stability — run `ping -c 100 <ip>` and check for packet loss
2. If WiFi, consider wired connection for mesh stability
3. Check MTU settings if using jumbo frames

## SSH Key Setup

All machines use the same ed25519 key for `bcloud` user:

```bash
# Generate (if not done):
ssh-keygen -t ed25519

# Copy to each machine:
ssh-copy-id bcloud@10.0.0.61   # ryzen
ssh-copy-id bcloud@10.0.0.131  # strix-halo
ssh-copy-id bcloud@<sligar-ip> # sligar
```

## Files

| File | Purpose |
|------|---------|
| `man-cave/cave.py` | API endpoints (KCS + GlusterFS) |
| `man-cave/templates/dashboard.html` | Ring Bus panel UI |
| `man-cave/static/js/cave.js` | Status polling, repair controls |
| `agent/halo-agent.py` | Ring bus + GlusterFS watchers |
| `systemd/halo-message-bus.service` | Agent message bus |
