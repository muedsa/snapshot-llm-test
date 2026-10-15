#!/usr/bin/env python
"""套件进度管理：suite-state.json / events.jsonl / checkpoints。

路径基准：suite_root。所有记录中的本地路径为相对路径。
用法：
  python suite_state.py init
  python suite_state.py start A01
  python suite_state.py done  A01 artifacts="a=outputs/run-.../A01/a.png" evidence="..." 
  python suite_state.py block  A01 reason="..." recovery="..."
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261011-01")
OUT_SUITE = f"outputs/{RUN_ID}/_suite"
TMP_SUITE = f"tmp/{RUN_ID}/_suite"
TASK_IDS = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]


def root() -> Path:
    return Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


def state_path() -> Path:
    return root() / OUT_SUITE / "suite-state.json"


def load() -> dict:
    p = state_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    tmpl = json.loads((root() / "templates/suite-state-template.json").read_text(encoding="utf-8"))
    tmpl["run_id"] = RUN_ID
    tmpl["profile"] = "all"
    tmpl["status"] = "not_started"
    tmpl["task_order"] = TASK_IDS
    return tmpl


def save(st: dict) -> None:
    st["updated_at"] = now()
    state_path().parent.mkdir(parents=True, exist_ok=True)
    state_path().write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def event(kind: str, task: str | None, **kw) -> None:
    rec = {"ts": now(), "event": kind, "task_id": task, "run_id": RUN_ID, "path_base": "suite_root"}
    rec.update(kw)
    p = root() / TMP_SUITE / "events.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def checkpoint(st: dict, note: str) -> str:
    d = root() / TMP_SUITE / "checkpoints"
    d.mkdir(parents=True, exist_ok=True)
    n = len(list(d.glob("state-*.json"))) + 1
    rel = f"{TMP_SUITE}/checkpoints/state-{n:06d}.json"
    (root() / rel).write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    st["last_checkpoint"] = rel
    return rel


def get_task(st: dict, tid: str) -> dict:
    for t in st["tasks"]:
        if t["id"] == tid:
            return t
    raise SystemExit(f"unknown task {tid}")


def parse_kv(items):
    """解析 key=value；value 可为 JSON（数组/对象/数字/布尔）或纯字符串。

    PowerShell 传参会吞掉内层双引号，因此也支持 `@文件路径` 从 JSON 文件读入。
    """
    out = {}
    for it in items:
        if "=" not in it:
            continue
        k, v = it.split("=", 1)
        if v.startswith("@"):
            out[k] = json.loads((root() / v[1:]).read_text(encoding="utf-8"))
            continue
        s = v.strip()
        if s.startswith("[") or s.startswith("{"):
            try:
                out[k] = json.loads(s)
                continue
            except json.JSONDecodeError:
                # 引号被 shell 吞掉时，退回「去掉残留引号再解析」
                try:
                    out[k] = json.loads(s.replace("'", '"'))
                    continue
                except json.JSONDecodeError:
                    out[k] = v
                    continue
        out[k] = v
    return out


def main():
    cmd = sys.argv[1]
    args = parse_kv(sys.argv[2:])
    st = load()

    if cmd == "init":
        st["status"] = "in_progress"
        st["started_at"] = st.get("started_at") or now()
        save(st)
        event("suite_init", None, note="套件启动，profile=all，30 题")
    elif cmd == "start":
        tid = sys.argv[2]
        t = get_task(st, tid)
        t.update(status="in_progress", started_at=now(),
                 output_dir=f"outputs/{RUN_ID}/{tid}",
                 temp_dir=f"tmp/{RUN_ID}/{tid}")
        st["current_task"] = tid
        st["current_round"] = args.get("round")
        st["current_case"] = args.get("case")
        save(st)
        event("task_start", tid, round=args.get("round"), case=args.get("case"))
    elif cmd == "progress":
        tid = sys.argv[2]
        st["current_task"] = tid
        st["current_round"] = args.get("round") or st.get("current_round")
        st["current_case"] = args.get("case") or st.get("current_case")
        if "round" in args:
            get_task(st, tid)["completed_rounds"] = args["round"]
        if "case" in args:
            get_task(st, tid)["completed_cases"] = args["case"]
        save(st)
        event("task_progress", tid, round=args.get("round"), case=args.get("case"),
              note=args.get("note"))
    elif cmd == "done":
        tid = sys.argv[2]
        t = get_task(st, tid)
        t.update(status="completed", ended_at=now(),
                 artifacts=args.get("artifacts", t.get("artifacts") or []),
                 visual_review_evidence=args.get("evidence", t.get("visual_review_evidence") or []),
                 unresolved_issues=args.get("unresolved", t.get("unresolved_issues") or []),
                 resume_notes=args.get("note"))
        if args.get("round"):
            t["completed_rounds"] = args["round"]
        if args.get("case"):
            t["completed_cases"] = args["case"]
        nxt = next((x for x in TASK_IDS[TASK_IDS.index(tid) + 1:]
                    if get_task(st, x)["status"] == "pending"), None)
        st["current_task"] = nxt
        save(st)
        cp = checkpoint(st, f"{tid} completed")
        event("task_done", tid, next=nxt, checkpoint=cp)
        print(f"{tid} completed -> next {nxt}; checkpoint {cp}")
    elif cmd == "block":
        tid = sys.argv[2]
        t = get_task(st, tid)
        t.update(status=args.get("status", "blocked"), ended_at=now(),
                 unresolved_issues=args.get("issues", t.get("unresolved_issues") or []),
                 resume_notes=f'reason={args.get("reason", "")}; recovery={args.get("recovery", "")}')
        save(st)
        event("task_blocked", tid, reason=args.get("reason"), recovery=args.get("recovery"))
    elif cmd == "checkpoint":
        save(st)
        print(checkpoint(st, args.get("note", "manual")))
    elif cmd == "artifacts":
        st["suite_artifacts"] = json.loads(args["paths"]) if "paths" in args else []
        save(st)
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()