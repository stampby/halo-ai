# VPN Setup Guide

Remote access to your halo-ai server without exposing services to the internet.


## Why VPN?

SSH tunnels work well when you are on the same LAN or have a direct route to the server. But when you need:

- Access from outside your home network (coffee shop, phone, travel)
- Persistent connections that survive network changes
- Access from devices where SSH tunnels are impractical (phones, tablets)
- Multi-device access without per-device SSH key management

A VPN gives your remote devices a direct, encrypted path to the server as if they were on the LAN. All halo-ai services remain on localhost --- the VPN client routes traffic through the tunnel.

The nftables firewall already has WireGuard's default port (51820/udp) open and ready.


## Option 1: WireGuard (Recommended)

WireGuard is the best choice for a single-server setup. It is fast, simple, built into the Linux kernel, and has excellent mobile clients.

### Install WireGuard

```bash
sudo pacman -S wireguard-tools
```

### Generate keys

```bash
# Server keys
wg genkey | tee /etc/wireguard/server-private.key | wg pubkey > /etc/wireguard/server-public.key
chmod 600 /etc/wireguard/server-private.key

# Client keys (repeat for each device)
wg genkey | tee client-private.key | wg pubkey > client-public.key
```

### Configure the server

Create `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address = 10.100.0.1/24
ListenPort = 51820
PrivateKey = <server-private-key>

# Optional: enable IP forwarding for internet access through the tunnel
PostUp = sysctl -w net.ipv4.ip_forward=1
PostDown = sysctl -w net.ipv4.ip_forward=0

# Client 1 (laptop)
[Peer]
PublicKey = <client-public-key>
AllowedIPs = 10.100.0.2/32

# Client 2 (phone)
[Peer]
PublicKey = <client-public-key>
AllowedIPs = 10.100.0.3/32
```

Set permissions:

```bash
sudo chmod 600 /etc/wireguard/wg0.conf
```

### Port already open in nftables

The halo-ai firewall configuration (`/srv/ai/configs/system/nftables.conf`) already includes:

```nft
udp dport 51820 accept
```

No firewall changes needed. If you use a different port, add a corresponding rule.

You will also need to allow traffic from the WireGuard subnet to reach localhost services. Add to the nftables input chain:

```nft
ip saddr 10.100.0.0/24 tcp dport { 443, 8443 } accept
```

Or, if you want VPN clients to access services directly (bypassing Caddy):

```nft
ip saddr 10.100.0.0/24 accept
```

### Generate client configs

For each client device, create a config file:

```ini
[Interface]
Address = 10.100.0.2/24
PrivateKey = <client-private-key>
DNS = 1.1.1.1

[Peer]
PublicKey = <server-public-key>
Endpoint = <your-public-ip-or-ddns>:51820
AllowedIPs = 10.100.0.0/24
PersistentKeepalive = 25
```

Notes on `AllowedIPs`:
- `10.100.0.0/24` --- only route VPN subnet traffic through the tunnel (split tunnel). This is the recommended setting for halo-ai: you access AI services through the VPN while other internet traffic goes through your normal connection.
- `0.0.0.0/0` --- route all traffic through the tunnel (full tunnel). Use this on untrusted networks.

### QR code generation for mobile

The WireGuard mobile apps can scan a QR code instead of manually entering the config:

```bash
sudo pacman -S qrencode
qrencode -t ansiutf8 < client-phone.conf
```

This prints the QR code directly in the terminal. Open the WireGuard app on iOS or Android, tap "Add tunnel", and scan.

### Systemd service setup

Start and enable the WireGuard interface:

```bash
sudo systemctl enable --now wg-quick@wg0
```

Check status:

```bash
sudo wg show
```

This shows connected peers, last handshake time, and data transferred.

### Port forwarding

If the server is behind a router/NAT, forward UDP port 51820 from your router to the server's LAN IP. The exact steps depend on your router. Many routers also support dynamic DNS (DDNS) to give your server a stable hostname.


## Option 2: Tailscale (Easiest)

Tailscale is a zero-configuration VPN built on WireGuard. It handles NAT traversal, key management, and DNS automatically. The tradeoff is that it routes coordination through Tailscale's servers (traffic itself is peer-to-peer).

### Install and login

```bash
sudo pacman -S tailscale
sudo systemctl enable --now tailscaled
sudo tailscale up
```

Follow the printed URL to authenticate in your browser. The server appears in your Tailscale network immediately.

### Access via Tailscale IP

After joining, the server gets a Tailscale IP (e.g., `100.x.y.z`). You can reach it from any device on your Tailscale network.

To access halo-ai services through Caddy:

```
https://100.x.y.z
```

You may need to add the Tailscale subnet to your nftables rules:

```nft
ip saddr 100.64.0.0/10 tcp dport { 443, 8443 } accept
```

### MagicDNS

Tailscale's MagicDNS feature lets you access devices by name instead of IP:

```
https://strix-halo
```

Enable MagicDNS in the Tailscale admin console at https://login.tailscale.com/admin/dns.

### Advantages

- No port forwarding needed (works behind NAT, CGNAT, firewalls)
- No key management (handled by Tailscale)
- Automatic peer-to-peer connections (DERP relay as fallback)
- Works across platforms (Linux, macOS, Windows, iOS, Android)

### Considerations

- Requires a Tailscale account (free tier supports up to 100 devices)
- Coordination server is hosted by Tailscale (you can self-host with Headscale)
- Adds a dependency on an external service


## Option 3: Nebula (Cosmos-Style Mesh)

Nebula is the open-source overlay networking tool created by Slack, used by Cosmos's Constellation feature. It creates a peer-to-peer encrypted mesh network with its own PKI (Public Key Infrastructure). This is the most flexible option, especially for multi-node deployments.

### How Constellation/Nebula works

Nebula creates a virtual Layer 3 network where every node can communicate directly with every other node, regardless of their physical network topology. It uses:

- **Self-hosted PKI:** You run your own Certificate Authority. No external trust dependencies.
- **UDP hole punching:** Peers establish direct connections through NAT without port forwarding (in most cases).
- **Lighthouse nodes:** Well-known nodes that help peers find each other. They do not relay traffic --- once peers discover each other, communication is direct.
- **Certificate-based identity:** Each node has a signed certificate that defines its Nebula IP and group memberships. Revocation is instant by not re-issuing a certificate.

Cosmos uses this as "Constellation" to connect containers and services across multiple machines without exposing ports.

### Self-hosted PKI

Install Nebula:

```bash
# Download from GitHub releases
curl -fsSL https://github.com/slackhq/nebula/releases/latest/download/nebula-linux-amd64.tar.gz | tar xz
sudo mv nebula nebula-cert /usr/local/bin/
```

Create the Certificate Authority:

```bash
nebula-cert ca -name "halo-ai mesh"
```

This creates `ca.crt` and `ca.key`. The CA key is the root of trust for the entire network. Store `ca.key` securely and offline after signing all certificates.

Sign certificates for each node:

```bash
# Server (lighthouse)
nebula-cert sign -name "strix-halo" -ip "10.200.0.1/24" -groups "servers"

# Client (laptop)
nebula-cert sign -name "laptop" -ip "10.200.0.2/24" -groups "clients"

# Client (phone)
nebula-cert sign -name "phone" -ip "10.200.0.3/24" -groups "clients"
```

### Lighthouse setup

The lighthouse is the rendezvous point. It needs a stable public IP or a port forwarded to it.

Create `/etc/nebula/config.yml` on the server:

```yaml
pki:
  ca: /etc/nebula/ca.crt
  cert: /etc/nebula/strix-halo.crt
  key: /etc/nebula/strix-halo.key

static_host_map:
  "10.200.0.1": ["<public-ip>:4242"]

lighthouse:
  am_lighthouse: true
  interval: 60

listen:
  host: 0.0.0.0
  port: 4242

tun:
  dev: nebula1
  drop_local_broadcast: false
  drop_multicast: false

firewall:
  conntrack:
    tcp_timeout: 12m
    udp_timeout: 3m
    default_timeout: 10m

  outbound:
    - port: any
      proto: any
      host: any

  inbound:
    - port: any
      proto: any
      group: servers

    - port: 443
      proto: tcp
      group: clients

    - port: 8443
      proto: tcp
      group: clients
```

Add port 4242/udp to nftables:

```nft
udp dport 4242 accept
```

### Client configuration

On each client, create a config with `am_lighthouse: false`:

```yaml
pki:
  ca: /etc/nebula/ca.crt
  cert: /etc/nebula/laptop.crt
  key: /etc/nebula/laptop.key

static_host_map:
  "10.200.0.1": ["<public-ip>:4242"]

lighthouse:
  am_lighthouse: false
  hosts:
    - "10.200.0.1"

listen:
  host: 0.0.0.0
  port: 0

tun:
  dev: nebula1

firewall:
  outbound:
    - port: any
      proto: any
      host: any

  inbound:
    - port: any
      proto: any
      host: any
```

### Peer-to-peer UDP hole punching

Once a client contacts the lighthouse, the lighthouse tells both peers each other's public IP and port. They then establish a direct UDP connection using hole punching. This works through most consumer NATs without any port forwarding on the client side.

If direct connectivity fails (symmetric NAT), Nebula falls back to relaying through the lighthouse. This is slower but ensures connectivity.

### Systemd service

Create `/etc/systemd/system/nebula.service`:

```ini
[Unit]
Description=Nebula Mesh VPN
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/nebula -config /etc/nebula/config.yml
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now nebula
```

### Best for multi-node setups

Nebula shines when you have multiple halo-ai servers (or other machines) that need to communicate. Each node gets a Nebula IP, and the mesh handles routing automatically. There is no single point of failure (beyond the initial lighthouse discovery).


## Comparison

| Feature | WireGuard | Tailscale | Nebula |
|---------|-----------|-----------|--------|
| **Complexity** | Low | Very low | Medium |
| **Setup time** | 15 min | 5 min | 30 min |
| **External dependency** | None | Tailscale coordination server | None |
| **NAT traversal** | Port forward required | Automatic | UDP hole punching |
| **Key management** | Manual | Automatic | Self-hosted PKI |
| **Multi-node mesh** | Possible but manual | Automatic | Native |
| **Mobile clients** | Excellent (official apps) | Excellent (official apps) | Limited (community) |
| **Performance** | Kernel-level, fastest | WireGuard-based, fast | Userspace, good |
| **Auditability** | Full (open source, ~4K LOC) | Partial (client open source) | Full (open source) |
| **Port in nftables** | Already open (51820/udp) | No port needed | Needs adding (4242/udp) |


## Recommendation

**Single server (most users): WireGuard.** It is simple, fast, kernel-native, and the port is already open in the halo-ai firewall. Set it up once and it runs forever with no external dependencies.

**Quick setup / non-technical users: Tailscale.** If you want remote access in 5 minutes without touching firewall rules or generating keys, Tailscale is the answer. The free tier is sufficient for personal use.

**Multi-node / advanced users: Nebula.** If you run multiple halo-ai servers or want Cosmos-style mesh networking with self-hosted PKI, Nebula gives you full control. The upfront setup cost pays off as the network grows.

All three options keep halo-ai services on localhost. The VPN provides a secure tunnel to reach them --- it does not change the security model, it extends it.
