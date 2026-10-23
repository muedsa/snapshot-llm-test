"""渲染运行器：run_id 初始化、DSL 渲染与批量渲染、文档抓取、状态更新。

启动基准：总任务根目录（cwd）或 SNAPSHOT_TASK_ROOT。
记录中的路径一律相对总任务根（path_base=suite_root）。

子命令：
  init  RUN_ID            创建 outputs/<rid>/_suite、tmp/<rid>/_suite 与初始 suite-state.json
  render TASK ID DSL OUT  渲染单个 DSL 到最终 PNG（保留服务原始字节）
  batch  TASK JSON        按 JSON 清单批量渲染
  draft  TASK JSON OUT    只写 DSL 草稿到临时目录（不请求服务）
  iter   TASK JSON        追加一条 iterations.jsonl 记录
  state  TASK JSON        更新 suite-state.json 中某题的状态字段
  check  TASK             打印本题输出/临时目录文件清单与 PNG 尺寸校验
"""

from __future__ import annotations

import json
import struct
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite as S  # noqa: E402


def png_size(path: Path) -> tuple[int, int] | None:
    try:
        b = path.read_bytes()[:24]
        if b[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        w, h = struct.unpack(">II", b[16:24])
        return w, h
    except Exception:
        return None


def do_init(run_id: str, profile: str = "all") -> None:
    out, tmp = S.suite_dirs()
    out.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "docs").mkdir(parents=True, exist_ok=True)
    (tmp / "checkpoints").mkdir(parents=True, exist_ok=True)
    root = S.suite_root()
    cfg = json.loads((root / "run-config.json").read_text(encoding="utf-8"))
    tpl = json.loads((root / "templates" / "suite-state-template.json").read_text(encoding="utf-8"))
    sp, stp = S.state_path(), (out / "suite-state.json")
    if not stp.exists():
        tpl["run_id"] = run_id
        tpl["profile"] = profile
        tpl["status"] = "in_progress"
        tpl["started_at"] = S.now_iso()
        tpl["suite_version"] = cfg.get("suite_version")
        tpl["task_order"] = json.loads((root / "catalog.json").read_text(encoding="utf-8"))["task_order"]
        tpl["paths"] = {
            "suite_root": "$SNAPSHOT_TASK_ROOT 或启动目录",
            "output_dir": f"outputs/{run_id}/_suite",
            "temp_dir": f"tmp/{run_id}/_suite",
            "output_root_env": "SNAPSHOT_OUTPUT_ROOT",
            "temp_root_env": "SNAPSHOT_TEMP_ROOT",
        }
        tpl["gitignore"] = {
            "path": ".gitignore",
            "template": "templates/gitignore-template.txt",
            "rules": [l.strip() for l in
                      (root / ".gitignore").read_text(encoding="utf-8").splitlines()
                      if l.strip() and not l.strip().startswith("#")],
        }
        stp.write_text(json.dumps(tpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    S.append_event({"ts": S.now_iso(), "event": "run_init", "run_id": run_id, "profile": profile})
    print(f"init ok: {S.rel(stp)}")


def _write_req(task_id, rid, kind, dsl_text, dsl_path, resp, body, label):
    """按 AGENTS.md 规定字段写一条 requests.jsonl。"""
    err = S.error_summary(body) if resp["status"] >= 400 or resp["status"] == 0 else None
    rec = {
        "request_id": rid,
        "task_id": task_id,
        "kind": kind,
        "label": label,
        "method": "POST",
        "url_path": "/snapshot",
        "started_at": resp["started_at"],
        "ended_at": resp["ended_at"],
        "timezone": S.TZ_NAME,
        "elapsed_ms": resp["elapsed_ms"],
        "http_status": resp["status"],
        "content_type": resp["content_type"],
        "request_path": S.rel(dsl_path) if dsl_path else None,
        "response_path": S.rel(resp.get("_dest")) if resp.get("_dest") else None,
        "response_headers_path": S.rel(resp["_dest"].with_suffix(
            resp["_dest"].suffix + ".headers.txt")) if resp.get("_dest") else None,
        "response_bytes": len(body),
        "retry_after": resp.get("retry_after"),
        "error_summary": err,
        "request_id_header": resp["headers"].get("x-request-id"),
        "server_timing": resp["headers"].get("server-timing"),
        "ratelimit_remaining": resp["headers"].get("x-ratelimit-remaining"),
    }
    S.log_request(task_id, rec)
    return rec


def do_render(task_id: str, spec: dict) -> dict:
    """渲染单个 spec：{"dsl_file"|"dsl", "out_png", "label", "rid", "debug"}。"""
    out_dir, tmp_dir = S.task_dirs(task_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    label = spec.get("label") or spec.get("out_png") or "render"
    rid = spec.get("rid") or f"req-{task_id.lower()}-{uuid.uuid4().hex[:12]}"
    dsl_text = spec.get("dsl")
    if not dsl_text:
        dsl_path = Path(spec["dsl_file"])
        if not dsl_path.is_absolute():
            dsl_path = S.suite_root() / dsl_path
        dsl_text = dsl_path.read_text(encoding="utf-8")
    # 请求正文原文保留（临时目录，.snapshot 后缀）
    draft = tmp_dir / f"req-{rid.split('-')[-1]}.snapshot"
    draft.write_text(dsl_text, encoding="utf-8")
    status, body, resp = S.snapshot_request(task_id, dsl_text, label,
                                            kind=spec.get("kind", "render"),
                                            debug_query=spec.get("debug", False))
    dest = out_dir / spec["out_png"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    draft.with_suffix(draft.suffix + ".headers.txt").write_text(
        f"HTTP/1.1 {status}\n" +
        "".join(f"{k}: {v}\n" for k, v in resp["headers"].items()), encoding="utf-8")
    (tmp_dir / "responses").mkdir(parents=True, exist_ok=True)
    (tmp_dir / "responses" / f"{rid}.body").write_bytes(body)
    resp["_dest"] = dest
    rec = _write_req(task_id, rid, spec.get("kind", "render"), dsl_text, draft, resp, body, label)
    ok = rec["http_status"] == 200 and (resp["content_type"] or "").startswith("image/")
    return {"request_id": rid, "ok": ok, "png": S.rel(dest),
            "http_status": rec["http_status"], "content_type": rec["content_type"],
            "elapsed_ms": rec["elapsed_ms"], "error": rec["error_summary"],
            "request_id_header": rec["request_id_header"], "server_timing": rec["server_timing"]}


def do_batch(task_id: str, path: str) -> list[dict]:
    path = Path(path)
    if not path.is_absolute():
        path = S.suite_root() / path
    spec = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for i, s in enumerate(spec, 1):
        s = dict(s)
        s.setdefault("rid", f"req-{task_id.lower()}-{uuid.uuid4().hex[:12]}")
        r = do_render(task_id, s)
        print(json.dumps(r, ensure_ascii=False))
        results.append(r)
    return results


def do_iter(task_id: str, path: str) -> None:
    path = Path(path)
    if not path.is_absolute():
        path = S.suite_root() / path
    S.log_iteration(task_id, json.loads(path.read_text(encoding="utf-8")))
    print("iteration logged")


def do_state(task_id: str, path: str) -> None:
    path = Path(path)
    if not path.is_absolute():
        path = S.suite_root() / path
    patch = json.loads(path.read_text(encoding="utf-8"))
    state = S.load_state()
    for t in state.get("tasks", []):
        if t["id"] == task_id:
            for k, v in patch["task"].items():
                if k in ("artifacts", "completed_rounds", "completed_cases",
                         "visual_review_evidence", "unresolved_issues") and isinstance(v, list):
                    t[k] = v
                else:
                    t[k] = v
            break
    else:
        raise SystemExit(f"task {task_id} 不在 suite-state 中")
    state["current_task"] = task_id
    state["current_round"] = patch.get("round")
    state["current_case"] = patch.get("case")
    S.save_state(state)
    ck = S.snapshot_checkpoint(state)
    S.append_event({"ts": S.now_iso(), "event": "task_update", "task_id": task_id,
                    "status": patch["task"].get("status"), "checkpoint": ck})
    print(f"state saved; checkpoint {ck}")


def do_check(task_id: str) -> None:
    out_dir, tmp_dir = S.task_dirs(task_id)
    print(f"task {task_id}")
    print(f"  OUTPUT_DIR {S.rel(out_dir)}")
    print(f"  TEMP_DIR   {S.rel(tmp_dir)}")
    if not out_dir.exists():
        print("  (输出目录不存在)")
        return
    for p in sorted(out_dir.rglob("*")):
        if p.is_file():
            extra = ""
            if p.suffix.lower() == ".png":
                sz = png_size(p)
                extra = f"  {sz[0]}x{sz[1]}" if sz else "  !! 非 PNG 字节"
            print(f"  {S.rel(p)}  {p.stat().st_size:>9,}B{extra}")
    nreq = len((tmp_dir / "requests.jsonl").read_text(encoding="utf-8").splitlines()) \
        if (tmp_dir / "requests.jsonl").exists() else 0
    niter = len((tmp_dir / "iterations.jsonl").read_text(encoding="utf-8").splitlines()) \
        if (tmp_dir / "iterations.jsonl").exists() else 0
    print(f"  requests.jsonl={nreq}  iterations.jsonl={niter}")


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "init":
        do_init(arg, sys.argv[3] if len(sys.argv) > 3 else "all")
    elif cmd == "render":
        print(json.dumps(do_render(arg, json.loads(sys.argv[3])), ensure_ascii=False))
    elif cmd == "batch":
        do_batch(arg, sys.argv[3])
    elif cmd == "iter":
        do_iter(arg, sys.argv[3])
    elif cmd == "state":
        do_state(arg, sys.argv[3])
    elif cmd == "check":
        do_check(arg)
    else:
        print(__doc__)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
