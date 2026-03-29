"""
Arcade Port Allocator — Zero conflicts, deterministic allocation.
Each game type gets a 100-port block, each instance gets 10 ports.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "arcade.db"

# Master port map — game_id: (block_base, category)
PORT_MAP = {
    # SURVIVAL TIER 1 (10000-10999)
    "ark_se":       (10000, "survival"),
    "ark_sa":       (10100, "survival"),
    "rust":         (10200, "survival"),
    "valheim":      (10300, "survival"),
    "sdtd":         (10400, "survival"),      # 7 Days to Die
    "zomboid":      (10500, "survival"),
    "dayz":         (10600, "survival"),
    "conan":        (10700, "survival"),
    "vrising":      (10800, "survival"),
    "enshrouded":   (10900, "survival"),

    # SURVIVAL TIER 2 (11000-11999)
    "palworld":     (11000, "survival"),
    "dst":          (11100, "survival"),       # Don't Starve Together
    "unturned":     (11200, "survival"),
    "starbound":    (11300, "survival"),
    "eco":          (11400, "survival"),
    "barotrauma":   (11500, "survival"),

    # MINECRAFT / VOXEL (12000-12999)
    "minecraft":    (12000, "voxel"),
    "mc_bedrock":   (12100, "voxel"),
    "mc_proxy":     (12200, "voxel"),
    "vintage_story":(12300, "voxel"),
    "terraria":     (12600, "voxel"),

    # FPS SOURCE (13000-13999)
    "cs2":          (13000, "fps"),
    "tf2":          (13100, "fps"),
    "gmod":         (13200, "fps"),
    "l4d2":         (13300, "fps"),
    "black_mesa":   (13400, "fps"),

    # FPS OTHER (14000-14999)
    "insurgency":   (14000, "fps"),
    "squad":        (14100, "fps"),
    "kf2":          (14200, "fps"),
    "arma3":        (14300, "fps"),
    "pavlov":       (14400, "fps"),
    "mordhau":      (14500, "fps"),
    "scp_sl":       (14600, "fps"),

    # STRATEGY / SIM (15000-15999)
    "factorio":     (15000, "strategy"),
    "satisfactory": (15100, "strategy"),
    "openttd":      (15200, "strategy"),
    "assetto":      (15300, "strategy"),

    # VOICE / UTILITY (16000-16999)
    "mumble":       (16000, "utility"),
    "teamspeak":    (16100, "utility"),
}

# Port offsets within each 10-port instance block
PORT_OFFSETS = {
    "game":     0,   # UDP — main game port
    "game2":    1,   # UDP — secondary game port (raw/steam)
    "query":    2,   # UDP — query/status
    "rcon":     3,   # TCP — remote console
    "web":      4,   # TCP — web admin panel
    "filex":    5,   # TCP — file transfer
    "beacon":   6,   # UDP — discovery/beacon
    "extra1":   7,   # reserved
    "extra2":   8,   # reserved
    "extra3":   9,   # reserved
}

MAX_INSTANCES = 10


def init_db():
    """Initialize the port allocation database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS port_allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            instance INTEGER NOT NULL,
            server_name TEXT,
            cluster_id TEXT,
            port_base INTEGER NOT NULL,
            game_port INTEGER NOT NULL,
            query_port INTEGER NOT NULL,
            rcon_port INTEGER NOT NULL,
            status TEXT DEFAULT 'reserved',
            target_host TEXT DEFAULT '127.0.0.1',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(game_id, instance)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS port_forwards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            allocation_id INTEGER REFERENCES port_allocations(id),
            port INTEGER NOT NULL,
            protocol TEXT NOT NULL,
            description TEXT,
            forwarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def allocate(game_id: str, server_name: str = "", cluster_id: str = "",
             target_host: str = "127.0.0.1") -> dict:
    """
    Allocate the next available instance for a game.
    Returns full port mapping or raises if no slots available.
    """
    if game_id not in PORT_MAP:
        raise ValueError(f"Unknown game: {game_id}. Available: {list(PORT_MAP.keys())}")

    block_base, category = PORT_MAP[game_id]
    conn = sqlite3.connect(str(DB_PATH))

    # Find next available instance
    used = {row[0] for row in conn.execute(
        "SELECT instance FROM port_allocations WHERE game_id = ? AND status != 'deleted'",
        (game_id,)
    ).fetchall()}

    instance = None
    for i in range(MAX_INSTANCES):
        if i not in used:
            instance = i
            break

    if instance is None:
        conn.close()
        raise RuntimeError(f"No available instances for {game_id} (max {MAX_INSTANCES})")

    # Calculate ports
    inst_base = block_base + (instance * 10)
    ports = {name: inst_base + offset for name, offset in PORT_OFFSETS.items()}

    # Check for conflicts with ALL active allocations
    all_ports = set(ports.values())
    existing = conn.execute(
        "SELECT game_port, query_port, rcon_port FROM port_allocations WHERE status != 'deleted'"
    ).fetchall()
    existing_ports = set()
    for row in existing:
        existing_ports.update(row)

    conflicts = all_ports & existing_ports
    if conflicts:
        conn.close()
        raise RuntimeError(f"Port conflict detected: {conflicts}")

    # Reserve
    conn.execute("""
        INSERT INTO port_allocations (game_id, instance, server_name, cluster_id,
            port_base, game_port, query_port, rcon_port, status, target_host)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
    """, (game_id, instance, server_name, cluster_id,
          inst_base, ports["game"], ports["query"], ports["rcon"], target_host))

    conn.execute("""
        INSERT INTO audit_log (event, details)
        VALUES ('allocate', ?)
    """, (f"{game_id} instance {instance} -> ports {inst_base}-{inst_base+9} on {target_host}",))

    conn.commit()
    conn.close()

    return {
        "game_id": game_id,
        "instance": instance,
        "server_name": server_name,
        "cluster_id": cluster_id,
        "category": category,
        "target_host": target_host,
        "ports": ports,
        "port_base": inst_base,
    }


def deallocate(game_id: str, instance: int):
    """Mark an instance as deleted, freeing its ports."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "UPDATE port_allocations SET status = 'deleted', updated_at = CURRENT_TIMESTAMP "
        "WHERE game_id = ? AND instance = ?",
        (game_id, instance)
    )
    conn.execute("INSERT INTO audit_log (event, details) VALUES ('deallocate', ?)",
                 (f"{game_id} instance {instance}",))
    conn.commit()
    conn.close()


def list_allocations(game_id: Optional[str] = None, status: str = "active") -> list:
    """List all port allocations, optionally filtered by game."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    if game_id:
        rows = conn.execute(
            "SELECT * FROM port_allocations WHERE game_id = ? AND status = ?",
            (game_id, status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM port_allocations WHERE status = ?", (status,)
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_full_port_map() -> dict:
    """Return the complete master port map with allocation status."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    allocations = conn.execute(
        "SELECT * FROM port_allocations WHERE status != 'deleted'"
    ).fetchall()
    conn.close()

    result = {}
    for game_id, (base, category) in PORT_MAP.items():
        instances = []
        for i in range(MAX_INSTANCES):
            inst_base = base + (i * 10)
            alloc = next((dict(a) for a in allocations
                         if a["game_id"] == game_id and a["instance"] == i), None)
            instances.append({
                "instance": i,
                "port_base": inst_base,
                "ports": {name: inst_base + offset for name, offset in PORT_OFFSETS.items()},
                "status": alloc["status"] if alloc else "available",
                "server_name": alloc["server_name"] if alloc else None,
            })
        result[game_id] = {
            "block_base": base,
            "category": category,
            "instances": instances,
        }
    return result


# Auto-init on import
init_db()
