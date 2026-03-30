# Auto-Repair Demo — Proof of Concept

> Designed and built by the architect.

## What This Shows

halo-ai's autonomous service guardian detects service failures and repairs them **without human intervention**. The agent watches all 12 services every 5 seconds, detects state changes, and takes action.

## Demo: Kill a Service, Watch It Come Back

```
═══════════════════════════════════════════════════════════
  KANSAS CITY SHUFFLE — AUTO-REPAIR DEMO
═══════════════════════════════════════════════════════════

STEP 1: CURRENT SERVICE STATE
  All 12 services active on strix-halo (10.0.0.131)
  llama-server: active | lemonade: active | open-webui: active | vane: active
  searxng: active | qdrant: active | n8n: active | comfyui: active
  man-cave: active | caddy: active | halo-agent: active | message-bus: active

STEP 2: RING BUS STATUS (Kansas City Shuffle)
  Ring Health: DEGRADED (3/4 machines — sligar offline)
  ryzen          UP         104.8ms
  strix-halo     UP         0ms (local)
  sligar         DOWN       (offline)
  minisforum     UP         256.5ms

STEP 3: MESSAGE BUS
  Status: ok
  Topics: 6 (security, bugs, releases, community, builds, monitoring)

═══════════════════════════════════════════════════════════
  STEP 4: SIMULATING FAILURE — KILLING halo-searxng
═══════════════════════════════════════════════════════════

  [14:19:40] Stopping halo-searxng to simulate a crash...
  [14:19:40] halo-searxng is now DOWN.
  [14:19:40] Waiting for halo-agent to detect the failure...

═══════════════════════════════════════════════════════════
  STEP 5: AGENT DETECTED — 5 SECONDS LATER
═══════════════════════════════════════════════════════════

  ⚠ [14:19:41] [halo] service_down — halo-searxng went down
  ⚠ [14:19:41] [halo] repairing — restarting halo-searxng (attempt 1)
  ✓ [14:19:46] [halo] repaired — halo-searxng is back online
  ✓ [14:19:51] [halo] service_recovered — halo-searxng is back

═══════════════════════════════════════════════════════════
  STEP 6: VERIFIED — SERVICE IS BACK
═══════════════════════════════════════════════════════════

  halo-searxng: active

═══════════════════════════════════════════════════════════
  DEMO COMPLETE
═══════════════════════════════════════════════════════════

  The agent detected the failure, restarted the service,
  and reported the recovery — all autonomously.
  Zero human intervention. This is halo-ai.
```

## Timeline

| Time | Event |
|------|-------|
| 14:19:40 | Service killed (`systemctl stop halo-searxng`) |
| 14:19:41 | Agent detected failure (1 second) |
| 14:19:41 | Agent initiated repair (`systemctl restart`) |
| 14:19:46 | Service confirmed back online (5 seconds total) |
| 14:19:51 | Recovery reported to activity feed |

**Total recovery time: 5 seconds. Zero human interaction.**

## How It Works

1. `halo-agent` watches all services via `systemctl is-active` + optional HTTP health checks
2. On state change (healthy → down), agent reports to activity feed and attempts repair
3. Repair = `systemctl restart <service>`, then verify with health check
4. If repair fails after 3 attempts, enters 5-minute cooldown
5. All events published to the message bus (port 8100) for other agents to consume
6. Man Cave dashboard shows live activity feed with status dots

## What Else the Agent Watches

- **GPU temperature** — alerts at 85°C, critical at 90°C
- **Memory** — warns below 4GB available
- **Disk** — warns at 80%, critical at 90%
- **Ring Bus** — SSH mesh connectivity every 60 seconds
- **GlusterFS** — distributed filesystem health every 120 seconds
- **Upstream updates** — git fetch when network is quiet, reports commits behind
- **Inference performance** — spot-checks tok/s, reports degradation

## Hardware

- AMD Ryzen AI MAX+ 395 (Strix Halo)
- 128GB unified memory
- Arch Linux, bare metal, zero containers
- 12 services, 17 agents, 25+ systemd units
