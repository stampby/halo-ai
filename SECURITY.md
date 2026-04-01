# halo-ai Security Model


> **No service in halo-ai is directly accessible from the network. This is by design.** *"None shall pass."*

Every service binds to `127.0.0.1` (localhost only). There is no way to reach Open WebUI, Vane, n8n, the LLM API, or any other service by connecting to the machine's IP address. This is critical because:

- **AI services have no built-in authentication** — Open WebUI, ComfyUI, llama.cpp server, and most AI tools were designed for local use. They have no concept of user authentication, rate limiting, or access control. Exposing them on `0.0.0.0` means anyone on your network can use your GPU, read your conversations, modify your workflows, and consume your resources.
- **LLM APIs accept arbitrary prompts** — An exposed OpenAI-compatible endpoint lets anyone on the network run inference against your models. On a 128GB machine running a 70B model, a single bad actor can saturate GPU compute and deny service to legitimate users.
- **Workflow engines are remote code execution** — n8n executes arbitrary workflows including shell commands, HTTP requests, and database queries. An exposed n8n instance is functionally equivalent to an open SSH session. *"Game over, man! Game over!"*

### How to Access Services

There are two supported methods. Both require SSH key authentication to strix-halo.

#### Method 1: SSH Tunnels (Recommended)

Add these tunnels to your SSH config. They activate automatically when you connect:

```
Host strix-halo
    HostName <YOUR_SERVER_IP>
    User <YOUR_USER>
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

    # Persistent connection
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 10m
    ServerAliveInterval 60
    ServerAliveCountMax 3

    # Service tunnels
    LocalForward 3000 127.0.0.1:3000   # Open WebUI
    LocalForward 3001 127.0.0.1:3001   # Vane (Perplexica)
    LocalForward 5678 127.0.0.1:5678   # n8n
    LocalForward 8080 127.0.0.1:8080   # Lemonade API
    LocalForward 8188 127.0.0.1:8188   # ComfyUI
```

Then `ssh strix-halo` and access services at `http://localhost:<port>` on your local machine. The SSH multiplexed connection stays alive for 10 minutes after your last session closes, so tunnels persist across terminal sessions.

This is the simplest and most secure method. No additional software required. Works from any machine with your SSH key.

#### Method 2: Caddy Reverse Proxy (Multi-User / Remote Access)

For accessing services from multiple devices or when SSH tunnels are impractical, deploy [Caddy](https://github.com/caddyserver/caddy) as an authenticated reverse proxy. Caddy is the only service that listens on the network.

```
# /srv/ai/configs/Caddyfile
:443 {
    tls internal

    basicauth * {
        admin $2a$14$... # bcrypt hash
    }

    handle_path /chat/* {
        reverse_proxy 127.0.0.1:3000
    }
    handle_path /research/* {
        reverse_proxy 127.0.0.1:3001
    }
    handle_path /workflows/* {
        reverse_proxy 127.0.0.1:5678
    }
    handle_path /api/* {
        reverse_proxy 127.0.0.1:8080
    }
    handle_path /comfyui/* {
        reverse_proxy 127.0.0.1:8188
    }
}
```

Caddy provides:
- **TLS encryption** (automatic self-signed or ACME certificates)
- **Basic authentication** (bcrypt-hashed passwords)
- **Single network-facing port** (443) — all other ports remain localhost-only
- **Compiled from source** using Go

### SSH Hardening

The SSH daemon on strix-halo is locked down:

*"You want to get into this machine? You need to know the secret handshake." — Morpheus, probably*

```
PasswordAuthentication no       # Keys only — no brute force
ChallengeResponseAuthentication no
UsePAM no
PermitRootLogin no              # No root access
AllowUsers <YOUR_USER>               # Single authorized user
```

### Software Stack for Secure Access

| Component | Role | Source |
|-----------|------|--------|
| **OpenSSH** | Primary access method — key-only, multiplexed tunnels | System package |
| **Caddy** | Reverse proxy with TLS + auth (optional, for multi-device) | Compiled from source (Go) |
| **systemd** | All services bound to `127.0.0.1` via unit files | System |
| **ufw/nftables** | Firewall — allow SSH (22) and Caddy (443) only | System |


## Firewall (nftables)

All ports are blocked except SSH and Caddy:

```
table inet filter {
    chain input {
        policy drop;
        ct state established,related accept
        iif lo accept              # localhost (all services)
        tcp dport 22 accept        # SSH (key-only)
        tcp dport 443 accept       # Caddy (TLS + auth)
        tcp dport 8443 accept      # Caddy alt port
        ip protocol icmp accept    # ping
        counter drop               # everything else — "Shall we play a game?" No.
    }
}
```

Managed by systemd: `sudo systemctl status nftables`

---

## Latest Security Audit — 2026-04-01

**Verdict:** NEEDS ATTENTION
**Severity:** 1 critical · 3 high · 2 medium · 1 low
**Scanner:** halo-security-audit.sh v3.0 (supply chain + install script auditing)
**Commit:** 42a9f2c

| Check | Result | Status |
|-------|--------|--------|
| Services exposed to network | 0 | PASS |
| Hardcoded secrets in code | 0 | PASS |
| shell=True usage | 5 | REVIEW |
| SSH StrictHostKeyChecking=no | 6 | REVIEW |
| Unauthenticated web apps | 2 | REVIEW |
| Unpinned pip dependencies | 5 | REVIEW |
| .gitignore coverage | 0 gaps | PASS |
| .env file permissions | 644 | REVIEW |
| Secrets in git history | 2 | REVIEW |
| npm malicious packages | 0 | PASS |
| npm critical/high vulns | 0 | PASS |
| pip malicious packages | 0 | PASS |
| Install script issues | 11 | REVIEW |
| Scripts written to /tmp | 0 | PASS |
| Input validation (user/host) | 2/2 | PASS |
| Shellcheck warnings | 0 | PASS |
| Downloads without checksum | 10 | REVIEW |

*Automated daily by Meek (Security Chief) at 06:00 UTC. Weekly archives filed as GitHub issues.*

---

## Incident Response — axios Supply Chain Attack (2026-03-31)

**Severity:** CRITICAL
**Attack:** North Korean group UNC1069 backdoored `axios@1.14.1` and `axios@0.30.4` with a RAT dropper (`plain-crypto-js`)
**Impact:** halo-ai install script pulls n8n and Vane via npm/pnpm/yarn — both depend on axios
**Caught by:** Zach ([@zmcnaney](https://github.com/zmcnaney))

### Response Timeline (March 31, 2026 UTC)

| Time | Action |
|------|--------|
| 21:35 | Axios pinned to 1.14.0 (last safe version) via npm/pnpm overrides |
| 21:42 | Supply chain auditing added to Meek's security pipeline |
| 21:54 | `--ignore-scripts` added to all npm/pnpm/yarn installs |
| 22:52 | Install script hardened (11 HIGH findings fixed), Meek upgraded to v3.0 |

### Mitigations

- **Version pinning:** axios locked to 1.14.0 via npm/pnpm overrides in install.sh
- **Post-install audit:** auto-detects and removes `plain-crypto-js` and compromised axios versions
- **Script blocking:** `--ignore-scripts` on all package installs prevents postinstall RAT execution
- **Credential rotation:** all 7 Discord bot tokens regenerated
- **Stack freeze:** no updates until install script stable, 24hr wait policy on all future updates
- **Automated scanning:** Meek v3.0 checks for known malicious npm/pip packages daily

### If You Installed Before the Patch

1. **Roll back:** `sudo snapper -c root undochange <snapshot>`
2. **Rotate ALL credentials:** SSH keys, API keys, .env values, Discord tokens
3. **Re-run the installer** with the patched version (v0.9.1+)

### References

- [Snyk: axios npm compromised](https://snyk.io/blog/axios-npm-package-compromised-supply-chain-attack-delivers-cross-platform/)
- [StepSecurity: axios supply chain attack](https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan)

---

## Automated Security Pipeline

Three agents run daily on Strix Halo via systemd timers:

| Agent | Schedule | Scope | Reports to |
|-------|----------|-------|------------|
| **Meek** (Security Chief) | 06:00 UTC daily | 17-check audit: secrets, supply chain, install script | Discord #security (pinned) |
| **Bounty** (Bug Hunter) | 08:00 UTC daily | Dry-run verification, shellcheck, GitHub issues | Discord #security |
| **Sentinel** (Code Watcher) | 10:00 UTC daily | Repo dirty state, axios pin enforcement, source inspection | Discord #security |

Weekly full audit archived as GitHub issue (Mondays 06:30 UTC) with label `security-audit`.

### Known Malicious Package Watchlist

```
plain-crypto-js  event-stream  flatmap-stream  ua-parser-js
coa  rc  colors  faker
```

All packages scanned across `/srv/ai/n8n`, `/srv/ai/vane`, `/srv/ai/open-webui`, `/srv/ai/comfyui`, `/srv/ai/kokoro`, `/srv/ai/searxng`.

---

*Designed and built by the architect*
