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
