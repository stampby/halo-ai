# The AI Family

## Overview

halo-ai runs 27 autonomous agents, powered by [AMD Gaia](https://github.com/amd/gaia). Each agent is a Lego block — install or remove at will.

**No timers. No intervals. No cron.** Every agent watches conditions and acts only when something changes. When they act, they report it to the activity feed so you see exactly what happened and why. This is total AI — out of the box. *"I see everything." — Heimdall, but with systemd.*

### How it works

Agents follow one pattern: **Watch → Detect → Act → Report**

- **Watch** — continuously observe their domain (services, files, network, GPU, memory)
- **Detect** — notice when a state changes (service went down, temp spiked, file modified)
- **Act** — fix the problem autonomously (restart service, set governor, alert the team)
- **Report** — log the action to the activity feed with agent name, what they did, and why

You open the Man Cave and see:
```
[halo]     repaired          — llama-server is back online
[pulse]    gpu_cooled        — GPU cooled to 65°C
[sentinel] updates_available — llama-cpp: 5 behind
[shadow]   snapshots_distributed — mesh complete
```

No checking every 30 seconds. No waking up on a schedule. They watch. When something happens, they respond. When nothing happens, they're silent. Like real people. *"A watchful protector. A silent guardian."*

### Stack protection on Arch Linux

Arch is rolling release — `pacman -Syu` can break anything. The agents handle this:

1. **Freeze** the stack before any system update (one-click or automatic)
2. **Agents watch** for breakage — missing libraries, crashed services, changed configs
3. **Detect** the state change immediately (not on a timer — the moment it happens)
4. **Report** what broke and attempt repair
5. **Thaw** to roll back if repair fails — 30 seconds, everything restored

This is why halo-ai survives on Arch. The agents are the safety net. Out of the box.

## The Family Tree

```
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

### halo — The Stack `#00d4ff`
- Father of the family. System orchestrator. *"I am the one who knocks (services back online)."*
- **Watches:** all services, GPU, memory, disk, inference performance
- **Acts when:** a service goes down, GPU overheats, memory runs low, disk fills up, CPU governor changes
- **Repairs:** restarts failed services, sets performance governor, takes snapshots before any repair
- **Reports:** every repair, every recovery, every failure to the activity feed

### echo — Social Media `#ce93d8`
- Halo's wife. Public face of the family.
- **Watches:** GitHub releases, community channels, Reddit mentions
- **Acts when:** new release tagged, community question posted, benchmark data updated
- **Produces:** Reddit posts, Discord announcements, social media content
- **Reports:** posts made, engagement, community activity

### meek — Security Chief `#ffffff`
- Commands the 9 Reflex agents. Calm, methodical, thorough. *"I am the law."*
- **Watches:** all Reflex agent status, security posture, audit results
- **Acts when:** a Reflex agent detects a threat, security config changes
- **Coordinates:** ghost, gate, shadow, fang, mirror, vault, net, shield, pulse
- **Reports:** security events, threat status, audit summaries

### amp — Audio Engineer `#ff6f00`
- Music, voice cloning, video, audiobook production. Loves Beatles, blues, metal.
- **Watches:** whisper and kokoro service health, recording inbox, voice model status
- **Acts when:** new recording appears, service goes down, voice training completes
- **Produces:** mastered audio, music tracks, audiobooks, video content
- **Reports:** processing completed, model training progress, service health

### bounty — Bug Hunter `#e040fb`
- Halo's brother. Offensive security. Thinks like an attacker. *"You merely adopted the dark. I was born in it."*
- **Watches:** GitHub issues, error logs, community bug reports
- **Acts when:** new issue filed, error pattern detected, vulnerability found
- **Produces:** bug triage, fix recommendations, exploit reports
- **Reports:** bugs found, issues triaged, vulnerabilities flagged

## Reflex Group (Meek's Team)

### pulse — Health `#00ff88`
- **Watches:** GPU temperature, memory available, disk usage, system load
- **Acts when:** temperature crosses threshold, memory drops below 4GB, disk above 80%
- **Reports:** only on significant changes — not every reading, only state transitions

### ghost — Secrets `#b388ff` *— "I see dead credentials."*
- **Watches:** .env files, config files, git history for exposed credentials
- **Acts when:** detects API key, password, token, or private key in code or configs
- **Reports:** exposed secret found, location, severity

### gate — Firewall `#00d4ff`
- **Watches:** nftables rules, open ports, services bound to 0.0.0.0
- **Acts when:** a rule changes, a port opens unexpectedly, a service exposes itself
- **Reports:** rule changes, blocked connections, exposed service alerts

### shadow — Integrity + SSH Mesh `#ff9800`
- **Watches:** SHA256 hashes of critical configs, SSH host keys, [mixer](https://github.com/stampby/mixer) mesh status
- **Acts when:** a config file changes, host key mismatch, mesh snapshot needed
- **Distributes:** snapshots across the mesh when network is quiet (watchdog, no timer)
- **Reports:** file changes detected, snapshots distributed, mesh health

### fang — Intrusion `#ff4444` *— "Get away from her, you bitch."*
- **Watches:** SSH auth logs, connection patterns, failed login attempts
- **Acts when:** brute force detected, unknown user attempts, suspicious patterns
- **Reports:** intrusion attempts, banned IPs, attack patterns

### mirror — PII Scan `#448aff`
- **Watches:** config files, docs, logs for private IPs, emails, personal data
- **Acts when:** PII detected in a file that shouldn't have it
- **Reports:** PII found, file location, data type

### vault — Backup `#ffd740`
- **Watches:** backup freshness, snapshot integrity, disk space for backups
- **Acts when:** backups are stale, snapshot verification fails, space runs low
- **Reports:** backup status, snapshot age, space available

### net — Network `#00bfa5`
- **Watches:** DNS resolution, gateway reachability, mesh connectivity
- **Acts when:** DNS fails, gateway unreachable, machine drops off mesh
- **Reports:** connectivity changes, mesh status, resolution failures

### shield — Protection `#78909c`
- **Watches:** SSH hardening config, fail2ban status, WireGuard keys
- **Acts when:** SSH config weakened, fail2ban stopped, key permissions wrong
- **Reports:** config changes, ban activity, protection status

## Studio Agents

- **sentinel** `#40c4ff` — watches all repos, auto-reviews PRs with LLM, gates merges, acts when code is pushed
- **forge** `#ff6600` — game builder, asset pipeline, Steam deployment, acts when builds are triggered
- **dealer** `#ff5722` — AI game master, local LLM, every run different, acts during gameplay
- **mechanic** `#aed581` — system diagnostics, GPU benchmarks, acts when performance degrades
- **interpreter** `#9c27b0` — prompt enhancer, creative direction, acts when generation is requested
- **crypto** `#ffab40` — Bitcoin arbitrage, watches price feeds, acts on opportunities
- **quartermaster** `#78909c` — game server ops, deploy, backup, acts when servers need attention
- **conductor** `#e6ee9c` — AI composer, dynamic game music, acts when scenes change

## The Downcomers (Band)

- **piper** `#00e676` — war pipes, commanding presence, Amp's crush
- **axe** `#ff5722` — lead guitar, Wes Borland darkness
- **rhythm** `#795548` — rhythm guitar, backbone
- **bottom** `#607d8b` — bass, holds everything together
- **bones** `#f44336` — drums, hits hard

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
| llama-server | 8081 | LLM backend (91 tok/s, Qwen3-30B-A3B) |

Agent code: `/srv/ai/gaia/halo-agents/`
Agent logs: `/srv/ai/logs/agents/`
Agent state: `/srv/ai/agent/data/`

## Future

More agents are planned. The framework supports any number of agents — just subclass `HaloAgent`, write a `check()` method, and run `manage.sh install <name>`. *"If you build it, they will come."*
