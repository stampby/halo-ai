#!/usr/bin/env python3
"""
halo-ai Agent Message Bus
==========================
Simple HTTP-based IPC layer for agent-to-agent communication.
Runs on Strix Halo (192.168.50.69:8100).

Usage:
    # Start the bus
    python message_bus.py

    # From any agent
    from agent.message_bus import MessageBusClient
    client = MessageBusClient("bounty")
    client.subscribe("security")
    client.publish("security", "vuln_found", {"cve": "CVE-2026-1234"})
"""

import asyncio
import json
import os
import time
import threading
import httpx
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BUS_HOST = "0.0.0.0"
BUS_PORT = 8100
PERSIST_DIR = Path("/var/lib/halo-ai/messages")
MAX_QUEUE_SIZE = 10_000

VALID_TOPICS = {
    "security",
    "bugs",
    "releases",
    "community",
    "builds",
    "monitoring",
}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class PublishRequest(BaseModel):
    from_agent: str
    topic: str
    event_type: str
    payload: dict = {}


class SubscribeRequest(BaseModel):
    agent: str
    topics: list[str]
    webhook_url: Optional[str] = None


class Message(BaseModel):
    from_agent: str
    topic: str
    event_type: str
    payload: dict
    timestamp: str


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------
class MessageStore:
    def __init__(self, persist: bool = True):
        self._queues: dict[str, list[dict]] = {t: [] for t in VALID_TOPICS}
        self._subscribers: dict[str, dict] = {}  # agent -> {topics, webhook_url}
        self._persist = persist
        if self._persist:
            PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    # -- publish --------------------------------------------------------
    def add(self, msg: dict) -> dict:
        topic = msg["topic"]
        if topic not in VALID_TOPICS:
            raise ValueError(f"Invalid topic: {topic}. Valid: {VALID_TOPICS}")

        msg["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._queues[topic].append(msg)

        # cap queue size
        if len(self._queues[topic]) > MAX_QUEUE_SIZE:
            self._queues[topic] = self._queues[topic][-MAX_QUEUE_SIZE:]

        if self._persist:
            self._persist_message(msg)

        return msg

    # -- query ----------------------------------------------------------
    def get_topic(self, topic: str, limit: int = 50) -> list[dict]:
        if topic not in VALID_TOPICS:
            raise ValueError(f"Invalid topic: {topic}")
        return self._queues[topic][-limit:]

    def get_for_agent(self, agent: str, limit: int = 50) -> list[dict]:
        info = self._subscribers.get(agent)
        if not info:
            return []
        msgs = []
        for t in info["topics"]:
            msgs.extend(self._queues.get(t, []))
        msgs.sort(key=lambda m: m["timestamp"])
        return msgs[-limit:]

    # -- subscriptions --------------------------------------------------
    def subscribe(self, agent: str, topics: list[str], webhook_url: Optional[str] = None):
        for t in topics:
            if t not in VALID_TOPICS:
                raise ValueError(f"Invalid topic: {t}")
        self._subscribers[agent] = {
            "topics": list(set(topics)),
            "webhook_url": webhook_url,
        }

    def unsubscribe(self, agent: str):
        self._subscribers.pop(agent, None)

    def get_subscribers_for_topic(self, topic: str) -> list[dict]:
        out = []
        for agent, info in self._subscribers.items():
            if topic in info["topics"]:
                out.append({"agent": agent, **info})
        return out

    def list_subscribers(self) -> dict:
        return dict(self._subscribers)

    # -- persistence ----------------------------------------------------
    def _persist_message(self, msg: dict):
        try:
            topic_dir = PERSIST_DIR / msg["topic"]
            topic_dir.mkdir(parents=True, exist_ok=True)
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_file = topic_dir / f"{date_str}.jsonl"
            with open(log_file, "a") as f:
                f.write(json.dumps(msg) + "\n")
        except OSError:
            pass  # non-fatal, in-memory is primary


# ---------------------------------------------------------------------------
# Webhook delivery (fire-and-forget, async)
# ---------------------------------------------------------------------------
async def deliver_webhooks(store: MessageStore, msg: dict):
    subs = store.get_subscribers_for_topic(msg["topic"])
    for sub in subs:
        url = sub.get("webhook_url")
        if not url:
            continue
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(url, json=msg)
        except Exception:
            pass  # best-effort delivery


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="halo-ai Message Bus", version="1.0.0")
store = MessageStore(persist=True)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "halo-ai-message-bus",
        "uptime_topics": list(VALID_TOPICS),
        "subscribers": len(store.list_subscribers()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/publish")
async def publish(req: PublishRequest):
    msg = {
        "from_agent": req.from_agent,
        "topic": req.topic,
        "event_type": req.event_type,
        "payload": req.payload,
    }
    try:
        result = store.add(msg)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # fire-and-forget webhook delivery
    asyncio.create_task(deliver_webhooks(store, result))

    return {"status": "published", "message": result}


@app.post("/subscribe")
async def subscribe(req: SubscribeRequest):
    try:
        store.subscribe(req.agent, req.topics, req.webhook_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "status": "subscribed",
        "agent": req.agent,
        "topics": req.topics,
        "webhook_url": req.webhook_url,
    }


@app.delete("/subscribe/{agent}")
async def unsubscribe(agent: str):
    store.unsubscribe(agent)
    return {"status": "unsubscribed", "agent": agent}


@app.get("/subscribe/{agent}")
async def get_agent_messages(agent: str, limit: int = 50):
    msgs = store.get_for_agent(agent, limit)
    return {"agent": agent, "count": len(msgs), "messages": msgs}


@app.get("/messages/{topic}")
async def get_topic_messages(topic: str, limit: int = 50):
    try:
        msgs = store.get_topic(topic, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"topic": topic, "count": len(msgs), "messages": msgs}


@app.get("/subscribers")
async def list_subscribers():
    return store.list_subscribers()


# ---------------------------------------------------------------------------
# Client class — import this from any agent
# ---------------------------------------------------------------------------
class MessageBusClient:
    """
    Lightweight client for the halo-ai message bus.

    Usage:
        client = MessageBusClient("bounty")
        client.subscribe(["security", "bugs"])
        client.publish("security", "vuln_found", {"cve": "CVE-2026-1234"})
        msgs = client.get_messages()
    """

    def __init__(self, agent_name: str, bus_url: str = "http://192.168.50.69:8100"):
        self.agent = agent_name
        self.bus_url = bus_url.rstrip("/")

    def publish(self, topic: str, event_type: str, payload: dict = None) -> dict:
        """Publish an event to a topic."""
        import httpx
        resp = httpx.post(f"{self.bus_url}/publish", json={
            "from_agent": self.agent,
            "topic": topic,
            "event_type": event_type,
            "payload": payload or {},
        }, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

    def subscribe(self, topics: list[str] | str, webhook_url: str = None) -> dict:
        """Subscribe to one or more topics."""
        if isinstance(topics, str):
            topics = [topics]
        import httpx
        resp = httpx.post(f"{self.bus_url}/subscribe", json={
            "agent": self.agent,
            "topics": topics,
            "webhook_url": webhook_url,
        }, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

    def get_messages(self, limit: int = 50) -> list[dict]:
        """Get messages for this agent's subscribed topics."""
        import httpx
        resp = httpx.get(
            f"{self.bus_url}/subscribe/{self.agent}",
            params={"limit": limit},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json().get("messages", [])

    def get_topic(self, topic: str, limit: int = 50) -> list[dict]:
        """Get messages for a specific topic."""
        import httpx
        resp = httpx.get(
            f"{self.bus_url}/messages/{topic}",
            params={"limit": limit},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json().get("messages", [])

    def health(self) -> dict:
        """Check bus health."""
        import httpx
        resp = httpx.get(f"{self.bus_url}/health", timeout=5.0)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║   halo-ai Agent Message Bus v1.0     ║")
    print("║   Listening on 0.0.0.0:8100          ║")
    print("╚══════════════════════════════════════╝")
    uvicorn.run(app, host=BUS_HOST, port=BUS_PORT, log_level="info")
