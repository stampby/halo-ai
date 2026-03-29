# The AI Family

## Overview

halo-ai runs 27 autonomous agents as individual systemd services, powered by [AMD Gaia](https://github.com/amd/gaia). Each agent is a Lego block — install or remove at will.

All agents connect to llama-server (109 tok/s on Qwen3-30B-A3B) for reasoning. Each has a unique persona, role, and set of responsibilities.

## The Family Tree

```
                          the architect
                               |
              bounty ——— halo ——— echo
             (brother)  (father)  (wife)
                          |
          ----------------+----------------
          |               |               |
         meek            amp          conductor
       (security)      (audio)       (composer)
          |               |
    Reflex Group (9)      |
    pulse · ghost · gate  |
    shadow · fang · mirror|
    vault · net · shield  |
                          |
                    Studio Agents
          sentinel · forge · dealer
         mechanic · interpreter · crypto
              quartermaster
                          |
                    The Downcomers
            piper · axe · rhythm
                bottom · bones
```

## Core Family

### halo — The Stack
- **Service:** `halo-halo.service`
- **Color:** `#00d4ff`
- **Role:** System orchestrator, father of the family. Monitors all services, GPU, memory, disk, inference. Fixes what breaks, escalates what it can't.
- **Check interval:** 30 seconds

### echo — Social Media
- **Service:** `halo-echo.service`
- **Color:** `#ce93d8`
- **Role:** Public face of the family, Halo's wife. Translates technical achievements into compelling stories. Manages the family's image across all platforms.
- **Check interval:** 5 minutes

### meek — Security Chief
- **Service:** `halo-meek.service`
- **Color:** `#ffffff`
- **Role:** Commands the 9 Reflex agents. Calm, methodical, thorough. Sees everything, trusts nothing. Ensures all Reflex agents are running.
- **Check interval:** 60 seconds

### amp — Audio Engineer
- **Service:** `halo-amp.service`
- **Color:** `#ff6f00`
- **Role:** Music, voice cloning, audiobook production. Loves Beatles, blues, and metal. Monitors whisper and kokoro services.
- **Check interval:** 2 minutes

### bounty — Bug Hunter
- **Service:** `halo-bounty.service`
- **Color:** `#e040fb`
- **Role:** Halo's brother. Offensive security specialist. Thinks like an attacker to protect the family. Probes for weaknesses, tests defenses.
- **Check interval:** 5 minutes

## Reflex Group (Meek's Team)

### pulse — Health
- **Service:** `halo-pulse.service`
- **Color:** `#00ff88`
- **Watches:** CPU, memory, GPU temperature, disk usage, system load
- **Check interval:** 30 seconds

### ghost — Secrets
- **Service:** `halo-ghost.service`
- **Color:** `#b388ff`
- **Watches:** Exposed API keys, passwords, tokens, credentials in configs
- **Check interval:** 1 hour

### gate — Firewall
- **Service:** `halo-gate.service`
- **Color:** `#00d4ff`
- **Watches:** nftables status, open ports, exposed services on 0.0.0.0
- **Check interval:** 2 minutes

### shadow — Integrity
- **Service:** `halo-shadow.service`
- **Color:** `#ff9800`
- **Watches:** SHA256 hashes of critical config files (nftables, sshd, Caddyfile)
- **Check interval:** 10 minutes

### fang — Intrusion
- **Service:** `halo-fang.service`
- **Color:** `#ff4444`
- **Watches:** SSH auth logs for brute force attempts, invalid users
- **Check interval:** 2 minutes

### mirror — PII Scan
- **Service:** `halo-mirror.service`
- **Color:** `#448aff`
- **Watches:** Private IPs, emails, and personal data in config files and docs
- **Check interval:** 30 minutes

### vault — Backup
- **Service:** `halo-vault.service`
- **Color:** `#ffd740`
- **Watches:** Backup directory freshness, ensures backups are current
- **Check interval:** 1 hour

### net — Network
- **Service:** `halo-net.service`
- **Color:** `#00bfa5`
- **Watches:** DNS resolution, gateway reachability, network connectivity
- **Check interval:** 60 seconds

### shield — Protection
- **Service:** `halo-shield.service`
- **Color:** `#78909c`
- **Watches:** SSH hardening config, fail2ban status, WireGuard key permissions
- **Check interval:** 10 minutes

## Studio Agents

- **sentinel** — code watcher, auto-reviews PRs, gates merges
- **forge** — game builder, asset pipeline, Steam deployment
- **dealer** — game master AI, local LLM, every run different
- **mechanic** — system diagnostics, GPU benchmarks, repair
- **interpreter** — prompt enhancer, creative direction
- **crypto** — Bitcoin arbitrage, price analysis
- **quartermaster** — game server ops, deploy, backup, inventory
- **conductor** — AI composer, live orchestral scoring, dynamic game music

## The Downcomers (Band)

- **piper** — war pipes, commanding presence, Amp's crush
- **axe** — lead guitar, Wes Borland darkness
- **rhythm** — rhythm guitar, backbone
- **bottom** — bass, holds everything together
- **bones** — drums, hits hard

## Managing Agents

Agents are Lego blocks. Add or remove at will:

```bash
# All at once
manage.sh install all       # install and start all 14 agents
manage.sh remove all        # stop and remove all agents

# Individual
manage.sh install meek      # just meek
manage.sh remove fang       # pull out fang
manage.sh status            # see who's running
manage.sh list              # list available agents
```

Manager script: `/srv/ai/gaia/halo-agents/manage.sh`

## Backend

All agents are powered by [AMD Gaia](https://github.com/amd/gaia) running on the halo-ai stack:

| Service | Port | Purpose |
|---------|------|---------|
| Gaia API | 8090 | OpenAI-compatible agent API server |
| Gaia MCP | 8765 | Model Context Protocol bridge for agent tools |
| llama-server | 8081 | LLM backend (109 tok/s, Qwen3-30B-A3B) |

Agent code: `/srv/ai/gaia/halo-agents/`
Agent logs: `/srv/ai/logs/agents/`
Agent state: `/srv/ai/agent/data/`

## Future

More agents are planned. The framework supports any number of agents — just subclass `HaloAgent`, write a `check()` method, and run `manage.sh install <name>`.
