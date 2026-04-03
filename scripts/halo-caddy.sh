#!/bin/bash
# halo-ai Caddy manager — add services, set password, restart
# Designed and built by the architect
set -euo pipefail

CADDYFILE="/srv/ai/configs/Caddyfile"
HOSTNAME=$(grep -oP 'http://\K[^/\s{]+' "$CADDYFILE" 2>/dev/null | head -1 | cut -d. -f2- || echo "strixhalo")
[ -z "$HOSTNAME" ] && HOSTNAME="strixhalo"

case "${1:-help}" in
    add)
        NAME="${2:?Usage: $0 add <name> <port>}"
        PORT="${3:?Usage: $0 add <name> <port>}"
        HASH=$(grep -oP 'caddy \K\$2a\$.*' "$CADDYFILE" | head -1)

        if grep -q "http://${NAME}.${HOSTNAME}" "$CADDYFILE" 2>/dev/null; then
            echo "$NAME already exists"
            exit 1
        fi

        cat >> "$CADDYFILE" << EOF

http://${NAME}.${HOSTNAME} {
    basic_auth * {
        caddy ${HASH}
    }
    reverse_proxy 127.0.0.1:${PORT}
}
EOF
        echo "Added: http://${NAME}.${HOSTNAME} → :${PORT}"
        sudo systemctl restart halo-caddy
        echo "Caddy restarted"
        ;;

    remove)
        NAME="${2:?Usage: $0 remove <name>}"
        # Remove the block for this service
        sed -i "/http:\/\/${NAME}.${HOSTNAME}/,/^}/d" "$CADDYFILE"
        echo "Removed: ${NAME}.${HOSTNAME}"
        sudo systemctl restart halo-caddy
        echo "Caddy restarted"
        ;;

    password)
        PASS="${2:?Usage: $0 password <new-password>}"
        HASH=$(caddy hash-password --plaintext "$PASS")
        sed -i "s|\$2a\$.*|${HASH}|g" "$CADDYFILE"
        echo "Password updated for all services"
        sudo systemctl restart halo-caddy
        echo "Caddy restarted"
        ;;

    list)
        echo "Services:"
        grep -oP 'http://\K[^{]+' "$CADDYFILE" | while read -r url; do
            port=$(grep -A3 "http://$url" "$CADDYFILE" | grep -oP '127.0.0.1:\K\d+' || echo "static")
            echo "  $url → :$port"
        done
        ;;

    restart)
        sudo systemctl restart halo-caddy
        echo "Caddy restarted"
        ;;

    *)
        echo "halo-ai Caddy Manager"
        echo ""
        echo "Usage:"
        echo "  $0 list                    Show all services"
        echo "  $0 add <name> <port>       Add a new service"
        echo "  $0 remove <name>           Remove a service"
        echo "  $0 password <new-pass>     Change password for all services"
        echo "  $0 restart                 Restart Caddy"
        echo ""
        echo "Examples:"
        echo "  $0 add grafana 3030"
        echo "  $0 remove grafana"
        echo "  $0 password mysecretpass"
        ;;
esac
