"""Summarize DSH session token usage for a session and its descendants."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import zstandard

PROJECT = Path(os.environ["USERPROFILE"]) / ".dsh" / "sessions" / "--D-mine-test-ds--"
ROOT_ID = "session-4fc04984-a367-4c82-a2e8-5ad13719bf66"


def load(session_dir: Path):
    path = session_dir / "session.v4.jsonl.zstd"
    with open(path, "rb") as fh:
        text = zstandard.ZstdDecompressor().stream_reader(fh).read().decode("utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def identify():
    sessions = {}
    for d in PROJECT.iterdir():
        if not d.is_dir():
            continue
        f = d / "session.v4.jsonl.zstd"
        if not f.exists():
            continue
        try:
            with open(f, "rb") as fh:
                head = zstandard.ZstdDecompressor().stream_reader(fh).read(2048).decode("utf-8", "replace")
            first = json.loads(head.splitlines()[0])
        except Exception:
            continue
        if first.get("type") != "session":
            continue
        sessions[first["id"]] = {"dir": d, "header": first}
    keep = {}
    queue = [ROOT_ID]
    while queue:
        sid = queue.pop(0)
        if sid in keep or sid not in sessions:
            continue
        keep[sid] = sessions[sid]
        for cid, info in sessions.items():
            if info["header"].get("parentSession") == sid:
                queue.append(cid)
    return keep


def summarize(sid, info):
    events = load(info["dir"])
    seen = set()
    rows = []
    for ev in events:
        if ev.get("type") != "assistant/message":
            continue
        data = ev.get("data") or {}
        usage = data.get("usage")
        if not usage:
            continue
        msg = data.get("message") or {}
        mid = msg.get("id") or ev.get("id") or f"seq-{ev.get('seq')}"
        key = str(mid)
        if key in seen:
            continue
        seen.add(key)
        src = data.get("source") or {}
        provider = src.get("provider")
        model = src.get("model")
        if not model:
            desc = next((e.get("data") for e in events if e.get("type") == "subagent/descriptor"), None) or {}
            provider = provider or desc.get("agentProvider")
            model = desc.get("agentModel")
        rows.append({
            "session_id": sid,
            "message_id": key,
            "seq": ev.get("seq"),
            "time": ev.get("time"),
            "turn": data.get("turn"),
            "step": data.get("step"),
            "provider": provider,
            "model": model,
            "input": int(usage.get("inputTokens") or 0),
            "output": int(usage.get("outputTokens") or 0),
            "cache_read": int(usage.get("cacheReadTokens") or 0),
            "cache_write": int(usage.get("cacheWriteTokens") or 0),
            "total": int(usage.get("totalTokens") or 0),
        })
    header = info["header"]
    descriptor = next((e.get("data") for e in events if e.get("type") == "subagent/descriptor"), None) or {}
    return {
        "id": sid,
        "parent": header.get("parentSession"),
        "origin": header.get("origin", "root"),
        "depth": header.get("delegationDepth"),
        "created_at": header.get("createdAt"),
        "label": descriptor.get("label"),
        "agent_model": descriptor.get("agentModel"),
        "calls": len(rows),
        "calls_with_usage": len(rows),
        "input": sum(r["input"] for r in rows),
        "output": sum(r["output"] for r in rows),
        "cache_read": sum(r["cache_read"] for r in rows),
        "cache_write": sum(r["cache_write"] for r in rows),
        "total": sum(r["total"] for r in rows),
        "first_ms": min((r["time"] for r in rows), default=None),
        "last_ms": max((r["time"] for r in rows), default=None),
        "models": dict(Counter(f"{r['provider']}/{r['model']}" for r in rows)),
        "rows": rows,
    }


def main():
    sessions = identify()
    out = {sid: summarize(sid, info) for sid, info in sessions.items()}
    print(json.dumps({sid: {k: v for k, v in s.items() if k != "rows"} for sid, s in out.items()}, ensure_ascii=False, indent=2))
    total = {k: sum(s[k] for s in out.values()) for k in ("calls", "input", "output", "cache_read", "cache_write", "total")}
    print("TOTAL", json.dumps(total, ensure_ascii=False))


if __name__ == "__main__":
    main()
