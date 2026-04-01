#!/bin/bash
# halo-ai — stamped by the architect
# Set up GitHub webhook to trigger n8n on releases
# Run this once after n8n is configured

set -euo pipefail

REPO="stampby/halo-ai"
# n8n webhook URL (through Caddy reverse proxy)
WEBHOOK_URL="${1:-https://strixhalo/webhooks/github-release}"

echo "Setting up GitHub webhook for ${REPO}"
echo "Webhook URL: ${WEBHOOK_URL}"

gh api repos/${REPO}/hooks \
  --method POST \
  -f name=web \
  -f "config[url]=${WEBHOOK_URL}" \
  -f "config[content_type]=json" \
  -f "config[insecure_ssl]=0" \
  -F "events[]=release" \
  -F active=true

echo "Webhook created. Releases on ${REPO} will trigger n8n → Echo → Reddit pipeline."
echo ""
echo "Pipeline flow:"
echo "  GitHub Release → n8n webhook → Echo LLM draft → Queue → Approve → Reddit post"
echo "  + Discord notification"
