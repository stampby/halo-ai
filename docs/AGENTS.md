# Agent Marketplace

## Overview

Halo AI supports optional autonomous agents that handle tasks you shouldn't have to. Each agent runs as a systemd service, can be enabled or disabled at any time, and integrates with the web dashboard at `https://strixhalo/agents/`.

Agents follow a shared pattern: a lightweight watcher service that monitors events, takes action based on configurable rules, and reports status back to the halo-ai dashboard.

## Available Agents

### Meek — Security Agent (Public)

**Repo:** [github.com/bong-water-water-bong/meek](https://github.com/bong-water-water-bong/meek)

Meek runs 9 Reflex agents that guard your system around the clock. Each Reflex agent watches a specific attack surface and responds autonomously — blocking threats, rotating credentials, and alerting you through the dashboard.

Reflex agents include watchers for SSH brute-force attempts, port scanning, failed authentication, firewall anomalies, certificate expiry, DNS poisoning, service health, log tampering, and unauthorized access patterns.

Meek integrates directly with fail2ban, systemd journals, and the Caddy reverse proxy to provide layered defense without manual intervention.

### Echo — Social Media Agent (Private)

Echo monitors and posts across 5 platforms, managing your project's social media presence while keeping you in control.

**Supported platforms:**
- GitHub (releases, discussions, announcements)
- Discord (server updates, community engagement)
- Mastodon (status updates, project news)
- Bluesky (cross-posts, engagement tracking)
- RSS (feed generation for all activity)

Echo is privacy-focused: all content is reviewed before posting (unless auto-post is enabled for specific event types), no analytics tracking is added to links, and all data stays on your machine. Echo runs locally as a systemd service — nothing is routed through third-party services.

## Recommended Homelab Agents (Planned)

The following agents are planned or under consideration. They follow the same systemd service pattern and dashboard integration as Meek and Echo.

| Agent | Role | Description |
|---|---|---|
| **Meek** | Security | Already built — guards your system with 9 Reflex agents |
| **Echo** | Social Media | Already built — manages project presence across 5 platforms |
| **Torrent** | Media Management | Monitor and manage downloads, integrate with *arr stack (Sonarr, Radarr, Prowlarr) |
| **Watt** | Power Management | Monitor power consumption, GPU power states, auto sleep/wake schedules |
| **Therm** | Temperature Control | GPU/CPU temps, fan curves, thermal throttling alerts |
| **Clerk** | Log Management | Aggregate, rotate, and analyze logs across all services |
| **Scout** | Update Manager | Track upstream releases, auto-update services safely with rollback |
| **Relay** | Notification Hub | Unified alerts via Discord, email, Pushover, SMS |
| **Census** | Resource Monitor | CPU, RAM, disk, GPU utilization dashboards and historical trends |
| **Keeper** | Password/Secret Manager | Rotate keys, manage credentials across services |

## Managing Agents

### Enable/Disable

```bash
sudo systemctl enable --now <agent>-watch.service   # Enable
sudo systemctl disable --now <agent>-watch.service   # Disable
```

Check status:

```bash
sudo systemctl status <agent>-watch.service          # Current status
journalctl -u <agent>-watch.service --since today    # Today's logs
```

### Web GUI

Agents can be managed through the dashboard at `https://strixhalo/agents/`:

- Toggle agents on/off
- View real-time status and uptime
- Configure settings and thresholds
- View reports and alerts
- Review action history

### Custom Agents

You can create custom agents that plug into the halo-ai ecosystem. A conforming agent needs:

1. **A systemd service** — named `<agent>-watch.service`, running as a dedicated user.
2. **A status endpoint** — HTTP on localhost that returns JSON with at minimum `{"status": "ok", "agent": "<name>"}`.
3. **Dashboard registration** — a config file at `/etc/halo-ai/agents/<name>.conf` with the agent's display name, port, description, and icon.
4. **Log output to journald** — use `systemd-cat` or structured logging so logs appear in the dashboard.

Example minimal agent config:

```ini
[agent]
name = MyAgent
port = 9100
description = Does something useful
icon = wrench
enabled = true
```

Place this at `/etc/halo-ai/agents/myagent.conf` and the dashboard will pick it up on the next refresh. Your agent's status endpoint should be reachable at `http://127.0.0.1:9100/status`.
