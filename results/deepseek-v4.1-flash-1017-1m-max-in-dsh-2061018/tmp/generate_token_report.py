"""Generate a de-duplicated token report for one DSH session tree."""
from __future__ import annotations

import csv
import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import zstandard

PROJECT = Path(os.environ["USERPROFILE"]) / ".dsh" / "sessions" / "--D-mine-test-ds--"
ROOT_ID = "session-4fc04984-a367-4c82-a2e8-5ad13719bf66"
TZ = timezone(timedelta(hours=8))


def read_session(session_dir: Path):
    path = session_dir / "session.v4.jsonl.zstd"
    with open(path, "rb") as fh:
        text = zstandard.ZstdDecompressor().stream_reader(fh).read().decode("utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def find_tree():
    found = {}
    for d in PROJECT.iterdir():
        f = d / "session.v4.jsonl.zstd"
        if not (d.is_dir() and f.exists()):
            continue
        try:
            with open(f, "rb") as fh:
                head = zstandard.ZstdDecompressor().stream_reader(fh).read(4096).decode("utf-8", "replace")
            first = json.loads(head.splitlines()[0])
        except Exception:
            continue
        if first.get("type") == "session":
            found[first["id"]] = {"dir": d, "header": first}
    tree, queue = {}, [ROOT_ID]
    while queue:
        sid = queue.pop(0)
        if sid in tree or sid not in found:
            continue
        tree[sid] = found[sid]
        for cid, info in found.items():
            if info["header"].get("parentSession") == sid and cid not in tree:
                queue.append(cid)
    return tree


def human(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, TZ).isoformat()


def parse(sid, info):
    events = read_session(info["dir"])
    descriptor = next((e.get("data") for e in events if e.get("type") == "subagent/descriptor"), None) or {}
    rows, seen = [], set()
    for ev in events:
        if ev.get("type") != "assistant/message":
            continue
        data = ev.get("data") or {}
        usage = data.get("usage")
        if not usage:
            continue
        msg = data.get("message") or {}
        mid = msg.get("id") or ev.get("id")
        key = str(mid) if mid else f"seq:{ev.get('seq')}"
        if key in seen:
            continue
        seen.add(key)
        src = msg.get("source") or data.get("source") or {}
        rows.append({
            "session_id": sid,
            "message_id": key,
            "seq": ev.get("seq"),
            "time_ms": ev.get("time"),
            "time": human(ev.get("time")),
            "turn": data.get("turn"),
            "step": data.get("step"),
            "provider": src.get("provider"),
            "model": src.get("model") or (descriptor.get("agentModel") if not src.get("model") else None),
            "input_tokens": int(usage.get("inputTokens") or 0),
            "output_tokens": int(usage.get("outputTokens") or 0),
            "cache_read_tokens": int(usage.get("cacheReadTokens") or 0),
            "cache_write_tokens": int(usage.get("cacheWriteTokens") or 0),
            "total_tokens": int(usage.get("totalTokens") or 0),
        })
    rows.sort(key=lambda r: (r["time_ms"] or 0, r["seq"] or 0))
    header = info["header"]
    return {
        "id": sid,
        "parent": header.get("parentSession"),
        "origin": header.get("origin", "root"),
        "depth": header.get("delegationDepth"),
        "created_at": human(header.get("createdAt")),
        "label": descriptor.get("label"),
        "agent_model": descriptor.get("agentModel"),
        "rows": rows,
        "calls": len(rows),
        "input": sum(r["input_tokens"] for r in rows),
        "output": sum(r["output_tokens"] for r in rows),
        "cache_read": sum(r["cache_read_tokens"] for r in rows),
        "cache_write": sum(r["cache_write_tokens"] for r in rows),
        "total": sum(r["total_tokens"] for r in rows),
        "first": human(min((r["time_ms"] for r in rows), default=None)),
        "last": human(max((r["time_ms"] for r in rows), default=None)),
        "models": dict(Counter(f"{r['provider']}/{r['model']}" for r in rows)),
    }


def main():
    tree = find_tree()
    parsed = {sid: parse(sid, info) for sid, info in tree.items()}
    root = parsed[ROOT_ID]
    root_ids = {r["message_id"] for r in root["rows"]}
    # dedupe across tree by message id; identical IDs in a fork are replay, not new usage.
    seen, dedup = set(), []
    for sid, s in parsed.items():
        for r in s["rows"]:
            if r["message_id"] in seen:
                continue
            seen.add(r["message_id"])
            rr = dict(r)
            rr["is_replay"] = sid != ROOT_ID and r["message_id"] in root_ids
            dedup.append(rr)
    # incremental for the continuation fork (rows not present in root)
    forks = [s for s in parsed.values() if s["id"] != ROOT_ID and s["origin"] == "root"]
    fork_incremental = {}
    for s in forks:
        new = [r for r in s["rows"] if r["message_id"] not in root_ids]
        fork_incremental[s["id"]] = {
            "calls": len(new),
            "input": sum(r["input_tokens"] for r in new),
            "output": sum(r["output_tokens"] for r in new),
            "cache_read": sum(r["cache_read_tokens"] for r in new),
            "cache_write": sum(r["cache_write_tokens"] for r in new),
            "total": sum(r["total_tokens"] for r in new),
            "first": human(min((r["time_ms"] for r in new), default=None)),
            "last": human(max((r["time_ms"] for r in new), default=None)),
        }
    subtotal_subagents = {
        "calls": sum(s["calls"] for s in parsed.values() if s["origin"] == "subagent"),
        "input": sum(s["input"] for s in parsed.values() if s["origin"] == "subagent"),
        "output": sum(s["output"] for s in parsed.values() if s["origin"] == "subagent"),
        "cache_read": sum(s["cache_read"] for s in parsed.values() if s["origin"] == "subagent"),
        "cache_write": sum(s["cache_write"] for s in parsed.values() if s["origin"] == "subagent"),
        "total": sum(s["total"] for s in parsed.values() if s["origin"] == "subagent"),
    }
    root_subagent = {k: root[k] + subtotal_subagents[k] for k in ("calls", "input", "output", "cache_read", "cache_write", "total")}
    dedup_total = {k: sum(r[k] for r in dedup) for k in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "total_tokens")}
    raw_full = {k: sum(s[k] for s in parsed.values()) for k in ("calls", "input", "output", "cache_read", "cache_write", "total")}
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(TZ).isoformat(),
        "root_session": ROOT_ID,
        "source": {
            "path_base": "user_home",
            "path": ".dsh/sessions/--D-mine-test-ds--/<session-id>/session.v4.jsonl.zstd",
            "format": "DSH session v4 JSONL, zstd stream",
            "usage_source": "assistant/message.data.usage (per model call)",
            "deduplication": "unique data.message.id across the tree; fork replay rows excluded from deduplicated total",
        },
        "sessions": {sid: {k: v for k, v in s.items() if k != "rows"} for sid, s in parsed.items()},
        "subagent_subtotal": subtotal_subagents,
        "root_plus_subagents": root_subagent,
        "continuation_fork_incremental": fork_incremental,
        "deduplicated_tree": {
            "calls": len(dedup),
            "input": dedup_total["input_tokens"],
            "output": dedup_total["output_tokens"],
            "cache_read": dedup_total["cache_read_tokens"],
            "cache_write": dedup_total["cache_write_tokens"],
            "total": dedup_total["total_tokens"],
        },
        "raw_full_sum": raw_full,
        "definitions": {
            "input": "uncached prompt/input tokens reported by the provider",
            "cache_read": "prompt tokens served from prompt cache; billed/usage counted separately by provider",
            "output": "generated completion tokens",
            "total": "sum of input + output + cache_read + cache_write",
            "calls": "assistant messages with a usage record; one per model response",
        },
    }
    outdir = Path("exports")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "session-4fc04984-a367-4c82-a2e8-5ad13719bf66-token-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    # details: all unique calls, mark replay
    detail = outdir / "session-4fc04984-a367-4c82-a2e8-5ad13719bf66-token-detail.csv"
    fields = ["session_id", "message_id", "seq", "time", "turn", "step", "provider", "model",
              "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens",
              "total_tokens", "is_replay", "in_deduplicated_total"]
    with open(detail, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in dedup:
            w.writerow({**{k: r.get(k) for k in fields[:-2]},
                        "is_replay": r["is_replay"],
                        "in_deduplicated_total": True})
        # include replayed fork rows for audit, but mark excluded
        for s in forks:
            for r in s["rows"]:
                if r["message_id"] in root_ids:
                    w.writerow({**{k: r.get(k) for k in fields[:-2]},
                                "is_replay": True,
                                "in_deduplicated_total": False})
    print(json.dumps({
        "sessions": {sid: {k: s[k] for k in ("origin", "calls", "input", "output", "cache_read", "total", "first", "last")} for sid, s in parsed.items()},
        "subagents": subtotal_subagents,
        "root_plus_subagents": root_subagent,
        "fork_incremental": fork_incremental,
        "deduplicated": summary["deduplicated_tree"],
        "raw_full": raw_full,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
