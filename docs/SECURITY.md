# Security Guide

This document covers the full security posture of a halo-ai deployment: what is locked down by default, how each layer works, and how to modify it.


## Default Security Posture

Out of the box, halo-ai follows a deny-all, allow-by-exception model:

- **Every service binds to `127.0.0.1` only.** Open WebUI, llama.cpp, ComfyUI, n8n, Vane, Lemonade, Qdrant, SearXNG, Whisper --- none of them are reachable from the network. This is enforced in each systemd unit file via `--host 127.0.0.1` or equivalent flags.
- **The firewall drops all inbound traffic** except SSH (22/tcp), Caddy (443/tcp, 8443/tcp), WireGuard (51820/udp), and ICMP. SSH and Caddy are restricted to the LAN subnet.
- **SSH requires key authentication.** Password login is disabled. Only a single named user is permitted.
- **Caddy is the only network-facing service.** It provides TLS encryption and bcrypt-hashed basic authentication in front of all proxied services.
- **Systemd units are hardened** with `ProtectSystem=strict`, `PrivateTmp=yes`, `NoNewPrivileges=yes`, and `ProtectHome=read-only`.
- **GPU devices use restrictive permissions** (`0660`, group `render`). Only users in the `render` group can access the GPU.

The result: even if someone is on your LAN, they cannot reach any AI service without authenticating through Caddy or establishing an SSH tunnel.


## Firewall (nftables)

### How the rules work

The firewall configuration lives at `/srv/ai/configs/system/nftables.conf` and is loaded by the `nftables` systemd service.

```nft
table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        ct state established,related accept    # Return traffic for outbound connections
        iif lo accept                          # All localhost traffic (service-to-service)
        ip saddr xxx.xxx.xxx.0/24 tcp dport 22 accept    # SSH from LAN (replace with your LAN subnet)
        ip saddr xxx.xxx.xxx.0/24 tcp dport 443 accept   # Caddy from LAN (replace with your LAN subnet)
        ip saddr xxx.xxx.xxx.0/24 tcp dport 8443 accept  # Caddy alt port from LAN (replace with your LAN subnet)
        udp dport 51820 accept                 # WireGuard (from anywhere)
        ip protocol icmp accept                # Ping
        ip6 nexthdr icmpv6 accept              # Ping (IPv6)
        counter drop                           # Everything else
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}
```

Key design decisions:
- **Default policy is `drop`** --- anything not explicitly allowed is silently rejected.
- **SSH and Caddy are LAN-only** (`xxx.xxx.xxx.0/24` — replace with your LAN subnet). Adjust this to match your subnet.
- **WireGuard accepts from anywhere** because VPN clients may connect from external networks.
- **Loopback is fully open** because all inter-service communication happens on localhost.
- **Outbound is unrestricted** (`policy accept` on output) so services can fetch models, updates, and search results.

### How to modify rules

Edit the configuration file:

```bash
sudo nano /srv/ai/configs/system/nftables.conf
```

Apply changes:

```bash
sudo nft -f /srv/ai/configs/system/nftables.conf
```

Verify the active ruleset:

```bash
sudo nft list ruleset
```

To make changes persist across reboots, the file is loaded by `systemctl enable nftables`.

### How to add exceptions

To allow a new port (example: Prometheus on 9090 from LAN):

```nft
ip saddr xxx.xxx.xxx.0/24 tcp dport 9090 accept
```

Add this line before the `counter drop` rule in the input chain. To allow from any source, omit the `ip saddr` clause.

To change the allowed LAN subnet, replace every `xxx.xxx.xxx.0/24` with your subnet (e.g., `192.168.1.0/24` or `10.0.0.0/8`).


## SSH Hardening

### Configuration

SSH is hardened via a drop-in config at `/srv/ai/configs/system/90-halo-security.conf`, which is installed to `/etc/ssh/sshd_config.d/`:

```
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
PermitRootLogin no
AllowUsers <YOUR_USER>
```

What each setting does:

| Setting | Effect |
|---------|--------|
| `PasswordAuthentication no` | Only key-based authentication is accepted. Eliminates brute-force attacks. |
| `ChallengeResponseAuthentication no` | Disables keyboard-interactive auth, closing a bypass for password auth. |
| `UsePAM no` | Disables PAM, which could otherwise re-enable password prompts. |
| `PermitRootLogin no` | Root cannot log in via SSH under any circumstances. |
| `AllowUsers <YOUR_USER>` | Only the named user can connect. All other usernames are rejected before authentication. |

### Key-only authentication

Generate an Ed25519 key on your client machine:

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@strix-halo
```

After copying the key, verify you can log in without a password, then restart sshd:

```bash
sudo systemctl restart sshd
```

### fail2ban

fail2ban monitors SSH logs and bans IPs after repeated failed authentication attempts. While key-only auth already prevents brute-force, fail2ban reduces log noise and blocks scanners.

Install and enable:

```bash
sudo pacman -S fail2ban
sudo systemctl enable --now fail2ban
```

The default jail configuration (`/etc/fail2ban/jail.local`) for SSH:

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
```

This bans an IP for 1 hour after 3 failed attempts within 10 minutes.

Check ban status:

```bash
sudo fail2ban-client status sshd
```

Unban an IP:

```bash
sudo fail2ban-client set sshd unbanip <IP>
```


## Caddy Authentication

### How basicauth works

Caddy is the only service that listens on the network (ports 443 and 8443). It terminates TLS and requires HTTP Basic Authentication on every request. The credentials are checked against a bcrypt hash stored in the Caddyfile.

The Caddyfile at `/srv/ai/configs/Caddyfile`:

```
:443 {
    tls internal

    basicauth * {
        admin $2a$14$hyBjre0RT3lbdTzAtACFRuhlYeFAx4xsxVsk0IR2RkDy3KVJIi2Nq
    }

    handle_path /chat/* {
        reverse_proxy 127.0.0.1:3000
    }
    # ... other routes
}
```

The `basicauth *` directive means every request to every path must authenticate. The username is `admin` and the value after it is the bcrypt hash of the password.

### Changing the password

**The default password is `Caddy`. You MUST change this immediately after installation.**

1. Generate a new bcrypt hash:

    ```bash
    caddy hash-password --plaintext 'your-new-secure-password'
    ```

    This outputs a hash like `$2a$14$...`.

2. Edit the Caddyfile:

    ```bash
    nano /srv/ai/configs/Caddyfile
    ```

    Replace the existing hash on the `admin` line with the new one:

    ```
    basicauth * {
        admin $2a$14$<YOUR_NEW_HASH_HERE>
    }
    ```

3. Restart Caddy:

    ```bash
    sudo systemctl restart halo-caddy
    ```

4. Verify by visiting `https://<server-ip>` in a browser. You should be prompted for credentials.

### Adding additional users

Add more username/hash pairs on separate lines inside the `basicauth` block:

```
basicauth * {
    admin  $2a$14$...
    alice  $2a$14$...
}
```

Each user gets their own bcrypt hash generated with `caddy hash-password`.


## TLS Certificates

### How Caddy self-signed certs work

The `tls internal` directive tells Caddy to generate a self-signed certificate using its built-in CA (Caddy's root CA). This provides encryption in transit without requiring a domain name or public ACME server.

On first start, Caddy creates:
- A root CA certificate and key (stored in Caddy's data directory)
- A leaf certificate for the server, signed by the root CA

Browsers will show a certificate warning because the root CA is not trusted by default.

### Installing the root CA on devices

To eliminate browser warnings, install Caddy's root CA certificate on your devices.

1. Find the root certificate on the server:

    ```bash
    # Default location (may vary by Caddy data dir configuration)
    ls ~/.local/share/caddy/pki/authorities/local/root.crt
    ```

2. Copy it to your client machine:

    ```bash
    scp strix-halo:~/.local/share/caddy/pki/authorities/local/root.crt ~/caddy-root.crt
    ```

3. Install per platform:

    | Platform | Command / Steps |
    |----------|----------------|
    | **macOS** | `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/caddy-root.crt` |
    | **Linux** | Copy to `/usr/local/share/ca-certificates/caddy-root.crt`, run `sudo update-ca-certificates` |
    | **Windows** | Double-click the `.crt` file, install to "Trusted Root Certification Authorities" |
    | **iOS** | AirDrop or email the cert, install via Settings > Profile, then trust in Settings > General > About > Certificate Trust Settings |
    | **Android** | Settings > Security > Install from storage, select the `.crt` file |


## Systemd Hardening

Every halo-ai service unit includes security directives that restrict what the process can do. These are defense-in-depth measures --- even if a service is compromised, the damage is contained.

| Directive | Effect |
|-----------|--------|
| `ProtectSystem=strict` | Mounts `/usr`, `/boot`, and `/etc` as read-only. The service cannot modify system binaries or configuration. |
| `PrivateTmp=yes` | Gives the service its own `/tmp` directory, invisible to other processes. Prevents tmp-based attacks. |
| `NoNewPrivileges=yes` | The process (and its children) cannot gain new privileges via setuid, setgid, or capabilities. |
| `ProtectHome=read-only` | Home directories are mounted read-only. The service can read configs but cannot write to home. |
| `ReadWritePaths=/srv/ai` | Explicit exception: the service can write to `/srv/ai` (models, data, logs). Everything else is read-only or inaccessible. |
| `AmbientCapabilities=CAP_NET_BIND_SERVICE` | (Caddy only) Allows binding to ports below 1024 (443) without running as root. |
| `SupplementaryGroups=video render` | (GPU services only) Grants access to GPU devices without running as root. |

These directives are applied per-unit in `/srv/ai/systemd/`. To inspect the effective security of a service:

```bash
systemd-analyze security halo-llama-server
```

This outputs a security score (lower is more restricted). Aim for scores below 5.0.


## API Key Management

### Where keys are stored

| Key | Location | Generated by |
|-----|----------|-------------|
| Dashboard API key | `/srv/ai/dashboard-api/data/dashboard-api-key.txt` | Installer (`openssl rand -base64 32`) |
| SearXNG secret key | `/srv/ai/configs/searxng/settings.yml` | Installer (`openssl rand -hex 32`) |
| Caddy password hash | `/srv/ai/configs/Caddyfile` | Installer (`caddy hash-password`) |

### How to rotate keys

**Dashboard API key:**

```bash
openssl rand -base64 32 > /srv/ai/dashboard-api/data/dashboard-api-key.txt
sudo systemctl restart halo-dashboard-api
```

Update any clients that use this key.

**SearXNG secret key:**

```bash
NEW_KEY=$(openssl rand -hex 32)
# Edit /srv/ai/configs/searxng/settings.yml and replace the secret_key value
sudo systemctl restart halo-searxng
```

**Caddy password:** See the [Caddy Authentication](#changing-the-password) section above.

### Best practices

- Rotate keys periodically (at least every 90 days for high-value keys).
- Never commit keys to version control. The installer generates them at install time, and they live only on the server.
- Use separate keys per service. halo-ai does this by default.
- Back up keys before rotating so you can revert if something breaks.


## GPU Device Permissions

GPU devices (`/dev/kfd`, `/dev/dri/renderD*`) are configured via udev rules at `/srv/ai/configs/system/70-amdgpu.rules`:

```
SUBSYSTEM=="kfd", KERNEL=="kfd", TAG+="uaccess", GROUP="render", MODE="0660"
SUBSYSTEM=="drm", KERNEL=="renderD*", TAG+="uaccess", GROUP="render", MODE="0660"
```

### Why 0660?

The permission `0660` means:
- **Owner (root):** read + write
- **Group (render):** read + write
- **Others:** no access

This ensures that only users in the `render` group can access the GPU. The `TAG+="uaccess"` directive allows logind sessions (local console users) to also access the device.

Services that need GPU access include `SupplementaryGroups=video render` in their systemd unit, granting GPU access without running as root.

To add a user to the render group:

```bash
sudo usermod -aG render,video <username>
```

The user must log out and back in for group changes to take effect.


## Backup Encryption

The `halo-backup` service creates periodic backups of `/srv/ai`. Recommendations for securing backups:

### Encrypt backups at rest

Use `gpg` to encrypt backup archives:

```bash
# Encrypt
tar czf - /srv/ai/data | gpg --symmetric --cipher-algo AES256 -o backup-$(date +%Y%m%d).tar.gz.gpg

# Decrypt
gpg -d backup-20260325.tar.gz.gpg | tar xzf -
```

### Encrypt backups for remote storage

For backups sent to a remote server or cloud storage, use `age` (simpler than GPG):

```bash
# Generate a key pair (once)
age-keygen -o backup-key.txt

# Encrypt
tar czf - /srv/ai/data | age -r age1... -o backup-$(date +%Y%m%d).tar.gz.age

# Decrypt
age -d -i backup-key.txt backup-20260325.tar.gz.age | tar xzf -
```

### Recommendations

- Always encrypt backups that leave the server.
- Store encryption keys separately from the backups (not on the same drive or cloud account).
- Test restore procedures regularly.
- Exclude model files from backups if bandwidth is limited --- they can be re-downloaded. Focus on configs, data, and keys.


## Network Segmentation

### Services on localhost only

Every halo-ai service binds exclusively to `127.0.0.1`. This is enforced at the application level (via `--host 127.0.0.1` flags or equivalent configuration) and verified by the firewall's default-drop policy.

The network topology:

```
Internet / LAN
    |
    v
[nftables firewall] -- drops everything except SSH, Caddy, WireGuard, ICMP
    |
    v
[Caddy :443] -- TLS termination + basicauth
    |
    v
[localhost services] -- 127.0.0.1:3000, :3001, :5678, :8080, :8081, :8188, etc.
```

No service-to-service communication crosses the network boundary. For example:
- Open WebUI talks to llama.cpp server at `127.0.0.1:8081`
- Vane talks to SearXNG at `127.0.0.1:8888`
- n8n talks to the LLM API at `127.0.0.1:8080`

All of this happens over loopback. An attacker on the network sees only ports 22, 443, 8443, and 51820 --- and all of those require authentication.

To verify that no service is accidentally exposed:

```bash
ss -tlnp | grep -v 127.0.0.1
```

This should show only Caddy (on `0.0.0.0:443` / `0.0.0.0:8443`) and sshd (on `0.0.0.0:22`). If any other service appears, check its systemd unit and ensure the bind address is `127.0.0.1`.
