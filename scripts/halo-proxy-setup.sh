#!/bin/bash
# halo-ai — designed and built by the architect
set -euo pipefail
echo "halo-ai Reverse Proxy Setup"
echo ""
read -s -p "Set access password: " PASS; echo ""
HASH=$(caddy hash-password --plaintext "$PASS" 2>/dev/null || /usr/local/bin/caddy hash-password --plaintext "$PASS")

cat > /srv/ai/configs/Caddyfile << CADDYEOF
{
    admin off
}
:8443 {
    tls internal
    basicauth * {
        admin $HASH
    }
    handle_path /research/* { reverse_proxy 127.0.0.1:3001 }
    handle_path /workflows/* { reverse_proxy 127.0.0.1:5678 }
    handle_path /api/* { reverse_proxy 127.0.0.1:8080 }
    handle_path /comfyui/* { reverse_proxy 127.0.0.1:8188 }
    handle_path /dashboard/* { reverse_proxy 127.0.0.1:3003 }
    reverse_proxy 127.0.0.1:3000
}
CADDYEOF

sudo systemctl enable --now halo-caddy.service
echo "Caddy running on https://$(hostname -I | awk '{print $1}'):8443"
