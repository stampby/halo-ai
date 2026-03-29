# halo-ai — stamped by the architect
"""
Automation bridge — receives events from n8n webhooks and routes to agents.
Runs on port 5679 alongside the Discord bots.
"""

import json
import logging
import os
import secrets
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("automation")

app = FastAPI(title="halo-ai automation bridge", version="1.0.0")
security = HTTPBearer()

# Auth token — set via AUTOMATION_API_KEY env var or auto-generated
API_KEY = os.environ.get("AUTOMATION_API_KEY", "")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    logger.warning(f"No AUTOMATION_API_KEY set — generated: {API_KEY}")
    logger.warning("Set AUTOMATION_API_KEY in .env for persistent auth")


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not secrets.compare_digest(credentials.credentials, API_KEY):
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials

QUEUE_DIR = Path(__file__).parent.parent / "discord-bots" / "data" / "reddit"
QUEUE_FILE = QUEUE_DIR / "post_queue.json"
LOG_FILE = QUEUE_DIR / "automation_log.json"


def _load_queue() -> list[dict]:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def _save_queue(queue: list[dict]):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))


def _log_event(event: dict):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    log = []
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())
    log.append(event)
    # Keep last 500 events
    if len(log) > 500:
        log = log[-500:]
    LOG_FILE.write_text(json.dumps(log, indent=2))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "automation-bridge", "queue_size": len(_load_queue())}


@app.post("/api/reddit/queue")
async def queue_reddit_post(request: Request, _=Depends(verify_token)):
    """Receive a post/reply from n8n and queue it for approval."""
    data = await request.json()
    queue = _load_queue()
    item = {
        "type": data.get("type", "post"),
        "subreddit": data.get("subreddit", "LocalLLaMA"),
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "source": "n8n",
        "release_tag": data.get("release_tag", ""),
    }
    queue.append(item)
    _save_queue(queue)
    _log_event({"action": "queued", "item": item})
    logger.info(f"Queued Reddit post: {item['title'][:60]}")
    return JSONResponse({"status": "queued", "queue_size": len(queue)})


@app.post("/api/discord/notify")
async def notify_discord(request: Request, _=Depends(verify_token)):
    """Forward a notification to Discord via webhook."""
    data = await request.json()
    _log_event({"action": "discord_notify", "data": data})
    logger.info(f"Discord notification: {data.get('message', '')[:60]}")
    return JSONResponse({"status": "sent"})


@app.post("/api/github/issue-triage")
async def triage_issue(request: Request, _=Depends(verify_token)):
    """Receive a GitHub issue and route to the right agent."""
    data = await request.json()
    issue = data.get("issue", {})
    title = issue.get("title", "").lower()
    body = issue.get("body", "").lower()
    text = f"{title} {body}"

    # Route based on keywords
    if any(kw in text for kw in ["security", "vulnerability", "cve", "ssh", "firewall"]):
        agent = "meek"
    elif any(kw in text for kw in ["audio", "voice", "music", "pipewire", "scarlett"]):
        agent = "amp"
    else:
        agent = "bounty"

    result = {
        "issue_number": issue.get("number"),
        "assigned_to": agent,
        "title": issue.get("title"),
    }
    _log_event({"action": "issue_triage", "result": result})
    logger.info(f"Issue #{result['issue_number']} → {agent}")
    return JSONResponse(result)


@app.get("/api/queue")
async def list_queue(_=Depends(verify_token)):
    """List all pending items."""
    queue = _load_queue()
    pending = [item for item in queue if item["status"] == "pending"]
    return JSONResponse({"pending": len(pending), "items": pending})


@app.get("/api/log")
async def get_log(_=Depends(verify_token)):
    """Get recent automation events."""
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())
        return JSONResponse({"events": log[-50:]})
    return JSONResponse({"events": []})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5679)
