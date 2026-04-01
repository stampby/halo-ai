#!/usr/bin/env bash
# halo-ai — automated security audit
# Runs daily: posts fresh results to Discord #security
# Runs weekly (Mondays): archives full report as GitHub issue
#
# Usage:
#   halo-security-audit.sh              # daily Discord post
#   halo-security-audit.sh --weekly     # weekly GitHub archive + Discord

set -uo pipefail

REPO_DIR="/home/bcloud/halo-ai"
REPORT_DIR="$REPO_DIR/security-audits"
DISCORD_ENV="$REPO_DIR/discord-bots/.env"
GITHUB_REPO="stampby/halo-ai"
SECURITY_CHANNEL="1488326052718842076"
DATE=$(date -u +%Y-%m-%d)
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
WEEKLY="${1:-}"

mkdir -p "$REPORT_DIR"

# Load Discord token
set -a
source "$DISCORD_ENV"
set +a
MEEK_TOKEN="$DISCORD_MEEK_TOKEN"

# ── Helper ─────────────────────────────────────────────

count_grep() {
    local result
    result=$(eval "$1" 2>/dev/null | wc -l) || result=0
    echo "${result// /}"
}

# ── Scan Functions ─────────────────────────────────────

secrets_found=$(count_grep "grep -rn --include='*.py' --include='*.sh' --include='*.json' --include='*.yml' -iE '(api_key|token|password|secret)\s*[:=]\s*[A-Za-z0-9+/=]{20,}' '$REPO_DIR' | grep -v '.env' | grep -v test | grep -v CHANGEME | grep -v not-needed | grep -v node_modules | grep -v venv | grep -v __pycache__")

gitignore_issues=0
for pattern in '.env' '*.key' '*.pem' '*.p12'; do
    grep -q "$pattern" "$REPO_DIR/.gitignore" 2>/dev/null || gitignore_issues=$((gitignore_issues + 1))
done

shell_injection=$(count_grep "grep -rn --include='*.py' 'shell=True' '$REPO_DIR' | grep -v venv | grep -v __pycache__ | grep -v node_modules")

exposed_services=0
for f in "$REPO_DIR"/systemd/halo-*.service; do
    if grep -q "ExecStart" "$f" 2>/dev/null; then
        if grep "ExecStart" "$f" | grep -qE -- '--host\s+0\.0\.0\.0' 2>/dev/null; then
            exposed_services=$((exposed_services + 1))
        fi
    fi
done

ssh_nocheck=$(count_grep "grep -rn --include='*.py' --include='*.sh' 'StrictHostKeyChecking=no' '$REPO_DIR' | grep -v venv | grep -v __pycache__")

unauth_apps=0
for f in "$REPO_DIR"/man-cave/cave.py "$REPO_DIR"/arcade/api/server.py; do
    if [ -f "$f" ]; then
        if ! grep -qE 'Depends.*auth|Bearer|api_key|basicauth' "$f" 2>/dev/null; then
            unauth_apps=$((unauth_apps + 1))
        fi
    fi
done

pinned=$(grep -c '<' "$REPO_DIR/discord-bots/requirements.txt" 2>/dev/null | tr -d '[:space:]' || echo 0)
total_deps=$(grep -c '>=' "$REPO_DIR/discord-bots/requirements.txt" 2>/dev/null | tr -d '[:space:]' || echo 0)
: "${pinned:=0}" "${total_deps:=0}"
unpinned=$((total_deps - pinned))
[ "$unpinned" -lt 0 ] && unpinned=0

env_perms="n/a"
if [ -f "$DISCORD_ENV" ]; then
    env_perms=$(stat -c %a "$DISCORD_ENV" 2>/dev/null || echo "unknown")
fi

git_secrets=$(git -C "$REPO_DIR" log --all --diff-filter=A --name-only -- '*.env' 2>/dev/null | grep -c ".env" || echo 0)

# ── Supply Chain Audit (npm + pip) ─────────────────────

# Known malicious packages — add to this list as new threats emerge
KNOWN_BAD_NPM="plain-crypto-js event-stream flatmap-stream ua-parser-js coa rc colors faker"
KNOWN_BAD_PIP="ctx colorama-patch requests-wrapper python-binance-api"

npm_vulns=0
npm_malicious=0
pip_vulns=0

# Scan all node_modules for known malicious packages
for svc_dir in /srv/ai/n8n /srv/ai/vane /srv/ai/open-webui; do
    if [ -d "$svc_dir/node_modules" ]; then
        for bad_pkg in $KNOWN_BAD_NPM; do
            if [ -d "$svc_dir/node_modules/$bad_pkg" ]; then
                npm_malicious=$((npm_malicious + 1))
                echo "MALICIOUS: $bad_pkg found in $svc_dir" >&2
            fi
        done
        # Check for compromised axios versions specifically
        ax_ver=$(node -e "try{console.log(require('$svc_dir/node_modules/axios/package.json').version)}catch(e){}" 2>/dev/null)
        if [ "$ax_ver" = "1.14.1" ] || [ "$ax_ver" = "0.30.4" ]; then
            npm_malicious=$((npm_malicious + 1))
            echo "MALICIOUS: axios@$ax_ver (backdoored) in $svc_dir" >&2
        fi
    fi
    # Run npm audit if package.json exists
    if [ -f "$svc_dir/package.json" ] && command -v npm >/dev/null; then
        svc_crit=$(cd "$svc_dir" && npm audit --json 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    v=d.get('metadata',{}).get('vulnerabilities',{})
    print(v.get('critical',0) + v.get('high',0))
except: print(0)" 2>/dev/null || echo 0)
        npm_vulns=$((npm_vulns + svc_crit))
    fi
done

# Scan pip venvs for known malicious packages
for svc_dir in /srv/ai/comfyui /srv/ai/kokoro /srv/ai/open-webui /srv/ai/searxng; do
    if [ -d "$svc_dir/.venv" ]; then
        for bad_pkg in $KNOWN_BAD_PIP; do
            if "$svc_dir/.venv/bin/pip" show "$bad_pkg" >/dev/null 2>&1; then
                pip_vulns=$((pip_vulns + 1))
                echo "MALICIOUS: pip package $bad_pkg in $svc_dir" >&2
            fi
        done
    fi
done

supply_chain_total=$((npm_malicious + npm_vulns + pip_vulns))

# ── Severity Calculation ───────────────────────────────

critical=0; high=0; medium=0; low=0

[ "$git_secrets" -gt 0 ] && critical=$((critical + 1))
[ "$npm_malicious" -gt 0 ] && critical=$((critical + 1))
[ "$exposed_services" -gt 0 ] && critical=$((critical + 1))
[ "$npm_vulns" -gt 0 ] && high=$((high + 1))
[ "$pip_vulns" -gt 0 ] && high=$((high + 1))
[ "$secrets_found" -gt 0 ] && high=$((high + 1))
[ "$shell_injection" -gt 0 ] && high=$((high + 1))
[ "$unauth_apps" -gt 0 ] && high=$((high + 1))
[ "$ssh_nocheck" -gt 0 ] && medium=$((medium + 1))
[ "$unpinned" -gt 0 ] && medium=$((medium + 1))
[ "$gitignore_issues" -gt 0 ] && medium=$((medium + 1))
[ "$env_perms" != "600" ] && [ "$env_perms" != "n/a" ] && low=$((low + 1))

if [ "$critical" -gt 0 ]; then
    verdict="NEEDS ATTENTION"; emoji="🔴"
elif [ "$high" -gt 0 ]; then
    verdict="MONITORING"; emoji="🟡"
else
    verdict="STRONG"; emoji="🟢"
fi

# ── Status helpers ─────────────────────────────────────

ok_or_warn() { [ "$1" -eq 0 ] && echo "✅" || echo "⚠️"; }
pass_or_review() { [ "$1" -eq 0 ] && echo "PASS" || echo "REVIEW"; }

# ── Build Discord Message ──────────────────────────────

read -r -d '' discord_msg << MSGEOF || true
$emoji **Security Audit — $DATE**

Automated sweep by Meek. 12 checks across the full stack.

\`\`\`
Services exposed to network:   $exposed_services $(ok_or_warn $exposed_services)
Hardcoded secrets in code:     $secrets_found $(ok_or_warn $secrets_found)
shell=True usage:              $shell_injection $(ok_or_warn $shell_injection)
SSH host key verify disabled:  $ssh_nocheck $(ok_or_warn $ssh_nocheck)
Unauthenticated web apps:      $unauth_apps $(ok_or_warn $unauth_apps)
Unpinned pip dependencies:     $unpinned $(ok_or_warn $unpinned)
.gitignore coverage:           $gitignore_issues gaps $(ok_or_warn $gitignore_issues)
.env file permissions:         $env_perms $([ "$env_perms" = "600" ] && echo "✅" || echo "⚠️")
Secrets in git history:        $git_secrets $(ok_or_warn $git_secrets)
npm malicious packages:        $npm_malicious $(ok_or_warn $npm_malicious)
npm critical/high vulns:       $npm_vulns $(ok_or_warn $npm_vulns)
pip malicious packages:        $pip_vulns $(ok_or_warn $pip_vulns)
\`\`\`

**Severity: $critical critical · $high high · $medium medium · $low low**
**Verdict: $verdict**

Past audits: [GitHub Archive](https://github.com/$GITHUB_REPO/issues?q=label%3Asecurity-audit)
*Next scan in 24 hours. — Meek, Security Chief*
MSGEOF

# ── Save Report File ──────────────────────────────────

report_file="$REPORT_DIR/audit-$DATE.md"
cat > "$report_file" << MDEOF
# Security Audit — $TIMESTAMP

**Verdict:** $verdict
**Severity:** $critical critical · $high high · $medium medium · $low low

## Scan Results

| Check | Result | Status |
|-------|--------|--------|
| Services exposed to network | $exposed_services | $(pass_or_review $exposed_services) |
| Hardcoded secrets in code | $secrets_found | $(pass_or_review $secrets_found) |
| shell=True usage | $shell_injection | $(pass_or_review $shell_injection) |
| SSH StrictHostKeyChecking=no | $ssh_nocheck | $(pass_or_review $ssh_nocheck) |
| Unauthenticated web apps | $unauth_apps | $(pass_or_review $unauth_apps) |
| Unpinned pip dependencies | $unpinned | $(pass_or_review $unpinned) |
| .gitignore coverage | $gitignore_issues gaps | $(pass_or_review $gitignore_issues) |
| .env file permissions | $env_perms | $([ "$env_perms" = "600" ] && echo "PASS" || echo "REVIEW") |
| Secrets in git history | $git_secrets | $(pass_or_review $git_secrets) |
| npm malicious packages | $npm_malicious | $(pass_or_review $npm_malicious) |
| npm critical/high vulns | $npm_vulns | $(pass_or_review $npm_vulns) |
| pip malicious packages | $pip_vulns | $(pass_or_review $pip_vulns) |

## Environment

- **Date:** $TIMESTAMP
- **Branch:** $(git -C "$REPO_DIR" branch --show-current 2>/dev/null || echo 'unknown')
- **Commit:** $(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo 'unknown')
- **Scanner:** halo-security-audit.sh v2.0 (supply chain auditing)

---
*Automated scan by Meek, Security Chief*
MDEOF

echo "Report saved: $report_file"

# ── Post to Discord #security (replace previous) ──────

# Find and delete previous audit messages from Meek
prev_ids=$(curl -s -H "Authorization: Bot $MEEK_TOKEN" \
    "https://discord.com/api/v10/channels/$SECURITY_CHANNEL/messages?limit=20" \
    | python3 -c "
import sys, json
msgs = json.load(sys.stdin)
for m in msgs:
    if m['author'].get('bot') and 'Security Audit' in m.get('content','') and 'Meek' in m.get('content',''):
        print(m['id'])
" 2>/dev/null || echo "")

for mid in $prev_ids; do
    curl -s -X DELETE -H "Authorization: Bot $MEEK_TOKEN" \
        "https://discord.com/api/v10/channels/$SECURITY_CHANNEL/messages/$mid" >/dev/null 2>&1
    sleep 1
done

# Post fresh audit
payload=$(python3 -c "import json,sys; print(json.dumps({'content': sys.stdin.read()}))" <<< "$discord_msg")
curl -s -X POST \
    -H "Authorization: Bot $MEEK_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "https://discord.com/api/v10/channels/$SECURITY_CHANNEL/messages" >/dev/null 2>&1

echo "Posted to Discord #security"

# ── Weekly GitHub Archive ──────────────────────────────

if [ "$WEEKLY" = "--weekly" ]; then
    WEEK=$(date -u +%Y-W%V)

    gh issue create --repo "$GITHUB_REPO" \
        --title "Security Audit Archive — $WEEK" \
        --label "security-audit" \
        --body "$(cat "$report_file")"

    echo "Archived to GitHub: $GITHUB_REPO (week $WEEK)"
fi

echo "Audit complete: $DATE — $verdict"
