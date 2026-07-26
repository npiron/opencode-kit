"""
Data collectors for the OpenCode Kit dashboard.
Reads from ~/.config/opencode/ and ~/.local/share/opencode/ to gather
heartbeat, memory, scheduler, and configuration metrics.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ──────────────────────────────────────────────
HOME = Path.home()
CONFIG = HOME / ".config" / "opencode"
LOCAL = HOME / ".local" / "share" / "opencode"

HEARTBEAT_LOG = CONFIG / "heartbeat" / "heartbeat.log"
HEARTBEAT_LAST = CONFIG / "heartbeat" / "heartbeat.last"
CONSOLIDATION_LOCK = CONFIG / "heartbeat" / "consolidation.lock"
RATE_LIMITS = CONFIG / "heartbeat" / "rate-limits.json"
REPOS_WHITELIST = CONFIG / "heartbeat" / "repos-whitelist.txt"
SCHEDULER_LOG = LOCAL / "scheduler.log"
SCHEDULER_ERR = LOCAL / "scheduler.err"
OPENDCODE_DB = LOCAL / "opencode.db"
TASKS_DB = CONFIG / ".tasks.db"
TASKS_DB_WAL = CONFIG / ".tasks.db-wal"
OPENDCODE_JSONC = CONFIG / "opencode.jsonc"
AGENTS_DIR = CONFIG / "agents"
SKILLS_DIR = CONFIG / "skills"
SESSIONS_DIR = CONFIG / "memory" / "sessions"
PREFERENCES = CONFIG / "agents" / "preferences.md"
POULS_CYCLE = CONFIG / "tasks" / "pouls-cycle.md"


def read_file(path: Path) -> str | None:
    """Read file content, return None if missing."""
    try:
        return path.read_text()
    except (FileNotFoundError, PermissionError):
        return None


def read_lines(path: Path, tail: int = 0) -> list[str]:
    """Read file lines. tail>0 returns last N lines."""
    content = read_file(path)
    if content is None:
        return []
    lines = content.strip().split("\n")
    return lines[-tail:] if tail and tail < len(lines) else lines


def _parse_ts(raw: str) -> datetime | None:
    """Parse a timestamp that may include a timezone abbreviation like CEST.
    Always returns a naive datetime to avoid TypeError when subtracting from datetime.now()."""
    raw = raw.strip()
    # Try ISO format first
    try:
        dt = datetime.fromisoformat(raw)
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
    except ValueError:
        pass
    # Try stripping trailing timezone abbreviation (e.g. "2026-01-01 12:00:00 CEST")
    parts = raw.rsplit(" ", 1)
    if len(parts) == 2:
        try:
            return datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return None


def age_from_timestamp(path: Path) -> str:
    """Human-readable age from a file containing a timestamp."""
    raw = read_file(path)
    if not raw:
        return "N/A"
    ts = _parse_ts(raw)
    if ts is None:
        return "invalide"
    delta = datetime.now() - ts
    mins = int(delta.total_seconds() / 60)
    if mins < 1:
        return "à l'instant"
    if mins < 60:
        return f"{mins} min"
    hours = mins // 60
    if hours < 24:
        return f"{hours}h {mins % 60}m"
    days = hours // 24
    return f"{days}j {hours % 24}h"


def parse_heartbeat_log() -> list[dict]:
    """Parse heartbeat.log into structured entries."""
    lines = read_lines(HEARTBEAT_LOG)
    entries = []
    pattern = re.compile(
        r"\[(?P<ts>[\d\-: ]+)\] "
        r"CHECK: (?P<checked>\d+)(?: mails)? \| "
        r"PROCESS: (?P<processed>\d+)/(?P<total>\d+)(?: \((?P<status>[^)]+)\))? \| "
        r"CONSOLIDATE: (?P<consolidation>[^|]+) \| "
        r"JOURNAL: (?P<journal>.+)"
    )
    for line in lines:
        m = pattern.search(line)
        if m:
            entries.append(m.groupdict())
        elif "TEST OK" in line:
            entries.append({"ts": line.split(" - ")[1] if " - " in line else "", "type": "test"})
    return entries


def parse_scheduler_log(tail: int = 30) -> list[str]:
    """Return last N lines of scheduler log."""
    return read_lines(SCHEDULER_LOG, tail)


def parse_scheduler_err(tail: int = 20) -> list[str]:
    """Return last N lines of scheduler error log."""
    return read_lines(SCHEDULER_ERR, tail)


def count_sessions() -> dict:
    """Count L3 session archives."""
    session_files = sorted(SESSIONS_DIR.glob("*.md")) if SESSIONS_DIR.exists() else []
    total_size = sum(f.stat().st_size for f in session_files)
    return {
        "count": len(session_files),
        "total_size_kb": round(total_size / 1024, 1),
        "files": [f.name for f in session_files],
    }


def l1_stats() -> dict:
    """L1 (preferences.md) statistics."""
    lines = read_lines(PREFERENCES)
    return {
        "lines": len(lines),
        "size_bytes": PREFERENCES.stat().st_size if PREFERENCES.exists() else 0,
    }


def l2_stats() -> dict:
    """L2 (Knowledge Graph) placeholder - requires MCP connection."""
    return {"available": False, "note": "Nécessite une connexion au serveur MCP memory"}


def _strip_jsonc_comments(text: str) -> str:
    """Strip // and /* */ comments from JSONC, preserving URLs in strings."""
    result = []
    i = 0
    in_string = False
    in_block_comment = False
    in_line_comment = False
    n = len(text)

    while i < n:
        c = text[i]
        nc = text[i + 1] if i + 1 < n else ""

        if in_block_comment:
            if c == "*" and nc == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_line_comment:
            if c == "\n":
                in_line_comment = False
                result.append(c)
            i += 1
            continue

        if in_string:
            if c == "\\":
                result.append(c)
                result.append(nc)
                i += 2
                continue
            if c == '"':
                in_string = False
            result.append(c)
            i += 1
            continue

        # Not in string
        if c == '"':
            in_string = True
            result.append(c)
            i += 1
            continue

        if c == "/" and nc == "*":
            in_block_comment = True
            i += 2
            continue

        if c == "/" and nc == "/":
            in_line_comment = True
            i += 2
            continue

        result.append(c)
        i += 1

    return "".join(result)


def parse_opencode_config() -> dict:
    """Extract key settings from opencode.jsonc (JSON with comments)."""
    raw = read_file(OPENDCODE_JSONC)
    if not raw:
        return {"error": "Fichier introuvable"}
    cleaned = _strip_jsonc_comments(raw)
    # Replace template placeholders like {env:FOO} with valid JSON strings
    cleaned = re.sub(r'"\{env:[^}]*\}"', '"<<env_placeholder>>"', cleaned)
    try:
        cfg = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"error": f"Cannot parse: {e}"}

    model_raw = cfg.get("model", "N/A")
    provider_id = model_raw.split("/")[0] if isinstance(model_raw, str) and "/" in model_raw else "N/A"

    mcp_servers = cfg.get("mcp", {})
    hb_model = "N/A"
    agent = cfg.get("agent", {})
    if isinstance(agent, dict):
        hb = agent.get("heartbeat", {})
        if isinstance(hb, dict):
            hb_model = hb.get("model", "N/A")

    return {
        "default_agent": cfg.get("default_agent", "N/A"),
        "model_id": model_raw,
        "provider_id": provider_id,
        "mcp_count": len(mcp_servers) if isinstance(mcp_servers, dict) else 0,
        "mcp_names": sorted(mcp_servers.keys()) if isinstance(mcp_servers, dict) else [],
        "heartbeat_model": hb_model,
    }


def count_agents() -> dict:
    """Count agents in agents/ directory."""
    files = list(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.exists() else []
    return {"count": len(files), "names": [f.stem for f in sorted(files)]}


def count_skills() -> dict:
    """Count skills (each has a SKILL.md)."""
    count = 0
    names = []
    if SKILLS_DIR.exists():
        for d in sorted(SKILLS_DIR.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                count += 1
                names.append(d.name)
    return {"count": count, "names": names}


def rate_limits() -> dict:
    """Read rate-limit counters if available."""
    raw = read_file(RATE_LIMITS)
    if not raw:
        return {"available": False}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}


def whitelist_repos() -> list[str]:
    """Read repos whitelist."""
    return [l.strip() for l in read_lines(REPOS_WHITELIST) if l.strip()]


def tasks_db_stats() -> dict:
    """Size of .tasks.db and its WAL."""
    stats = {}
    for name, path in [("db", TASKS_DB), ("wal", TASKS_DB_WAL)]:
        try:
            stats[name] = round(path.stat().st_size / 1024, 1)
        except FileNotFoundError:
            stats[name] = 0
    return stats


def get_snapshot() -> dict:
    """Collect all metrics into a single snapshot."""
    hb_entries = parse_heartbeat_log()
    sessions = count_sessions()

    return {
        "timestamp": datetime.now().isoformat(),
        "heartbeat": {
            "last_beat_age": age_from_timestamp(HEARTBEAT_LAST),
            "last_beat_raw": (read_file(HEARTBEAT_LAST) or "").strip(),
            "last_consolidation_age": age_from_timestamp(CONSOLIDATION_LOCK),
            "entries": hb_entries[-10:],  # last 10 cycles
            "total_cycles": len(hb_entries),
            "is_alive": check_alive(),
        },
        "memory": {
            "l1": l1_stats(),
            "l2": l2_stats(),
            "l3": sessions,
        },
        "system": {
            "scheduler_log": parse_scheduler_log(20),
            "scheduler_err": parse_scheduler_err(10),
            "tasks_db": tasks_db_stats(),
        },
        "config": parse_opencode_config(),
        "agents": count_agents(),
        "skills": count_skills(),
        "rate_limits": rate_limits(),
        "whitelist": whitelist_repos(),
    }


def check_alive() -> bool:
    """Agent is alive if last heartbeat < 90 minutes ago."""
    raw = read_file(HEARTBEAT_LAST)
    if not raw:
        return False
    ts = _parse_ts(raw)
    if ts is None:
        return False
    return (datetime.now() - ts).total_seconds() < 5400
