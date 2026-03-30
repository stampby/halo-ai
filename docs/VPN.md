# VPN Access

Remote access to your Halo AI server without exposing services to the internet. *"Fly, you fools!" — directly into the tunnel.*

## WireGuard (Built-in)

WireGuard is the recommended way to access your Halo AI server remotely. It's already in the Linux kernel, has zero dependencies, and port 51820 is open in the default firewall config. *"I'm in." — every 90s hacker movie, but this time for real.*

### Quick Setup

```bash
halo-vpn-setup.sh
```

The script handles everything interactively:

1. Installs `wireguard-tools` if not already present
2. Generates a server keypair and stores it securely in `/etc/wireguard/`
3. Prompts for a VPN subnet (default: `10.100.0.0/24`)
4. Detects your server's LAN IP automatically
5. Creates `/etc/wireguard/wg0.conf` with proper permissions
6. Enables the `wg-quick@wg0` systemd service
7. Generates your first client config and saves it to `~/halo-vpn-client.conf`
8. Displays a QR code for mobile setup (if `qrencode` is installed)

### Manual Setup

If you prefer to configure WireGuard by hand:

**Install wireguard-tools:**

```bash
sudo pacman -S wireguard-tools
```

**Generate server keys:**

```bash
wg genkey | tee /tmp/server-private.key | wg pubkey > /tmp/server-public.key
sudo mkdir -p /etc/wireguard
sudo mv /tmp/server-private.key /etc/wireguard/server-private.key
sudo mv /tmp/server-public.key /etc/wireguard/server-public.key
sudo chmod 600 /etc/wireguard/server-private.key
```

**Create `/etc/wireguard/wg0.conf`:**

```ini
[Interface]
Address = 10.100.0.1/24
ListenPort = 51820
PrivateKey = <contents of server-private.key>

# Enable IP forwarding so VPN clients can reach LAN services
PostUp = sysctl -w net.ipv4.ip_forward=1
PostDown = sysctl -w net.ipv4.ip_forward=0

[Peer]
# Client 1
PublicKey = <client-public-key>
AllowedIPs = 10.100.0.2/32
```

```bash
sudo chmod 600 /etc/wireguard/wg0.conf
```

**Enable the WireGuard interface:**

```bash
sudo systemctl enable --now wg-quick@wg0
```

**Generate a client keypair:**

```bash
wg genkey | tee client-private.key | wg pubkey > client-public.key
```

Create a client config file (`client.conf`):

```ini
[Interface]
Address = 10.100.0.2/24
PrivateKey = <client-private-key>
DNS = 1.1.1.1

[Peer]
PublicKey = <server-public-key>
Endpoint = <your-server-ip>:51820
AllowedIPs = 10.100.0.0/24
PersistentKeepalive = 25
```

Notes on `AllowedIPs`:
- `10.100.0.0/24` -- only route VPN subnet traffic through the tunnel (split tunnel). Recommended for Halo AI: access AI services through the VPN while other internet traffic takes your normal route.
- `0.0.0.0/0` -- route all traffic through the tunnel (full tunnel). Use this on untrusted networks. *"Trust no one." — Mulder was right.*

**Display a QR code for mobile:**

```bash
sudo pacman -S qrencode
qrencode -t ansiutf8 < client.conf
```

**Verify the connection:**

```bash
sudo wg show
```

This displays connected peers, last handshake time, and data transferred.

### Adding Clients

Each new client needs its own keypair and a unique IP on the VPN subnet.

Using the setup script:

```bash
halo-vpn-setup.sh add-client laptop
halo-vpn-setup.sh add-client phone
```

The script generates the keypair, adds the peer to the running WireGuard interface, updates `wg0.conf`, and saves the client config to `~/halo-vpn-<name>.conf`.

Manually:

```bash
# Generate keys for the new client
wg genkey | tee newclient-private.key | wg pubkey > newclient-public.key

# Add the peer to the running interface (no restart needed)
sudo wg set wg0 peer $(cat newclient-public.key) allowed-ips 10.100.0.3/32

# Also add the [Peer] block to /etc/wireguard/wg0.conf so it persists across restarts
```

Pick the next available IP in the subnet (`.3`, `.4`, `.5`, etc.).

### Mobile Access

The WireGuard apps for iOS and Android can import configs via QR code:

1. Generate the client config (either with `halo-vpn-setup.sh add-client phone` or manually)
2. Display the QR code: `qrencode -t ansiutf8 < ~/halo-vpn-phone.conf`
3. Open the WireGuard app on your phone
4. Tap **Add a tunnel** > **Create from QR code**
5. Scan the terminal QR code
6. Enable the tunnel -- your phone now has direct access to Halo AI services

### Firewall Notes

The halo-ai nftables config (`/srv/ai/configs/system/nftables.conf`) already has port 51820/udp open. No firewall changes needed.

If the server is behind a router/NAT, forward UDP port 51820 from your router to the server's LAN IP.

## Alternative: Tailscale

Tailscale is a zero-config VPN built on WireGuard. It handles NAT traversal, key management, and DNS automatically. The tradeoff is an external dependency on Tailscale's coordination servers (traffic itself is peer-to-peer).

```bash
sudo pacman -S tailscale
sudo systemctl enable --now tailscaled
sudo tailscale up
```

Follow the printed URL to authenticate. Your server appears in your Tailscale network immediately and is reachable from any device on your Tailscale account. No port forwarding, no key management.

The free tier supports up to 100 devices. If you want to self-host the coordination server, look into [Headscale](https://github.com/juanfont/headscale). *"There is no cloud. There is only Zuul." — you know the drill.*

## Alternative: Nebula

Nebula is an open-source mesh VPN created by Slack, used by Cosmos Cloud's Constellation feature. It creates a peer-to-peer encrypted mesh with self-hosted PKI and UDP hole punching.

Only recommended for multi-server deployments where you need a full mesh between multiple Halo AI nodes or other infrastructure. For a single server, WireGuard is simpler and faster.

See the [Cosmos Cloud documentation](https://cosmos-cloud.io/) for how Constellation uses Nebula, or the [Nebula GitHub repo](https://github.com/slackhq/nebula) for standalone setup.

## Dynamic DNS (DDNS)

If your ISP gives you a dynamic IP, set up DDNS so your VPN endpoint stays reachable.

### Quick Setup
```bash
halo-ddns-setup.sh
```

### Providers

| Provider | Cost | Account Required | URL |
|----------|------|-----------------|-----|
| **FreeMyIP** (recommended) | Free | No | https://freemyip.com |
| DuckDNS | Free | GitHub/Google login | https://www.duckdns.org |
| No-IP | Free tier | Yes | https://www.noip.com |
| Dynu | Free | Yes | https://www.dynu.com |
| Afraid.org (FreeDNS) | Free | Yes | https://freedns.afraid.org |

### FreeMyIP Setup
1. Go to https://freemyip.com
2. Enter desired hostname, click "Claim"
3. Copy the update token from the page
4. Run `halo-ddns-setup.sh` and paste the token
5. Done — IP updates automatically every 5 minutes

### Using with WireGuard
Once DDNS is configured, update your WireGuard client config's Endpoint:
```
Endpoint = yourhostname.freemyip.com:51820
```

### Port Forwarding
For remote VPN access through your router, forward **UDP port 51820** to your server's LAN IP (xxx.xxx.xxx.xxx).
