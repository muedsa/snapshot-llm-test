"""单题生成器运行器：一个题目脚本一次跑完 写 DSL → 渲染 → 留痕。

启动基准：总任务根目录（cwd）或 SNAPSHOT_TASK_ROOT；SNAPSHOT_RUN_ID 必须已设置。

题目生成脚本用法（放在 tmp/<run_id>/<task_id>/gen/ 下）：
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import taskgen as TG
    from kit import *
    t = TG.Task("A01")
    t.render("operations", dsl, "operations.png", label="经营驾驶舱 v1",
             iteration={"version": "v1", ...})
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite as S  # noqa: E402
import render as R  # noqa: E402


class Task:
    """封装一题的目录、渲染与留痕。"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.out_dir, self.tmp_dir = S.task_dirs(task_id)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        (self.tmp_dir / "dsl").mkdir(parents=True, exist_ok=True)
        (self.tmp_dir / "previews").mkdir(parents=True, exist_ok=True)
        (self.tmp_dir / "responses").mkdir(parents=True, exist_ok=True)

    # --- 路径 -------------------------------------------------------------
    def rel_out(self, name: str) -> str:
        return S.rel(self.out_dir / name)

    def rel_tmp(self, name: str) -> str:
        return S.rel(self.tmp_dir / name)

    def write_dsl(self, name: str, dsl_text: str) -> Path:
        dest = self.tmp_dir / "dsl" / f"{name}.snapshot"
        dest.write_text(dsl_text, encoding="utf-8")
        return dest

    # --- 渲染 -------------------------------------------------------------
    def render(self, name: str, dsl_text: str, out_png: str, *, label: str = "",
               iteration: dict | None = None, final: bool = True) -> dict:
        """渲染一次：final=True 写入输出目录作为最终产物，False 写入临时 previews/。"""
        path = self.write_dsl(name, dsl_text)
        rid = f"req-{self.task_id.lower()}-{uuid.uuid4().hex[:12]}"
        spec = {"dsl_file": S.rel(path), "label": label or out_png, "rid": rid}
        if final:
            spec["out_png"] = out_png
        else:
            # 预览不落输出目录：先渲染到临时，再挪位置
            spec["out_png"] = out_png
            res = R.do_render(self.task_id, spec)
            moved = self.tmp_dir / "previews" / Path(out_png).name
            moved.write_bytes(self.out_dir.joinpath(out_png).read_bytes())
            R.png_move_note = S.rel(moved)
            res["png"] = R.png_move_note
            res["preview"] = True
            return res
        res = R.do_render(self.task_id, spec)
        res["dsl"] = S.rel(path)
        return res

    # --- 留痕 -------------------------------------------------------------
    def iter(self, rec: dict) -> None:
        rec.setdefault("task_id", self.task_id)
        rec.setdefault("timezone", S.TZ_NAME)
        S.log_iteration(self.task_id, rec)

    def tool(self, rec: dict) -> None:
        rec.setdefault("task_id", self.task_id)
        S.log_tool(self.task_id, rec)

    # --- 交付 -------------------------------------------------------------
    def write_json(self, name: str, obj) -> str:
        (self.out_dir / name).write_text(
            json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return self.rel_out(name)

    def write_text(self, name: str, text: str) -> str:
        (self.out_dir / name).write_text(text, encoding="utf-8")
        return self.rel_out(name)

    def sizes(self) -> dict:
        out = {}
        for p in sorted(self.out_dir.rglob("*.png")):
            out[S.rel(p)] = R.png_size(p)
        return out


def png_signature(path: str) -> dict:
    """读 PNG 的 IHDR 尺寸与文件哈希，用于核验最终图来自服务真实响应。"""
    import hashlib
    p = Path(path)
    if not p.is_absolute():
        p = S.suite_root() / p
    b = p.read_bytes()
    return {
        "path": S.rel(p),
        "bytes": len(b),
        "sha256_16": hashlib.sha256(b).hexdigest()[:16],
        "is_png": b[:8] == b"\x89PNG\r\n\x1a\n",
        "size": R.png_size(p),
    }


def state_patch(task_id: str, **kw) -> None:
    """把本题状态写进 suite-state.json 并存检查点。"""
    state = S.load_state()
    out_dir, tmp_dir = S.task_dirs(task_id)
    for t in state.get("tasks", []):
        if t["id"] == task_id:
            for k, v in kw.items():
                if k in ("artifacts", "completed_rounds", "completed_cases",
                         "visual_review_evidence", "unresolved_issues") and isinstance(v, list):
                    t[k] = v
                elif k == "resume_notes":
                    t[k] = v
                else:
                    t[k] = v
            if "output_dir" not in kw:
                t["output_dir"] = S.rel(out_dir)
            if "temp_dir" not in kw:
                t["temp_dir"] = S.rel(tmp_dir)
            break
    else:
        raise SystemExit(f"{task_id} 不在 suite-state 中")
    state["current_task"] = task_id
    S.save_state(state)
    ck = S.snapshot_checkpoint(state)
    S.append_event({"ts": S.now_iso(), "event": "task_update", "task_id": task_id,
                    "status": kw.get("status"), "checkpoint": ck})
    return ck


def mark_started(task_id: str) -> None:
    """置为 in_progress。started_at 只取最早一次：脚本每次运行都会调用本函数，
    无条件覆写会把真实开始时间挪到最近一次渲染上（A01 曾因此丢了 16:37 的起点）。"""
    kw = {"status": "in_progress"}
    for t in S.load_state().get("tasks", []):
        if t["id"] == task_id and not t.get("started_at"):
            kw["started_at"] = S.now_iso()
        break
    state_patch(task_id, **kw)


def mark_completed(task_id: str, *, artifacts, visual_review_evidence,
                   metrics_path: str | None = None, unresolved_issues=None,
                   note: str | None = None) -> None:
    state_patch(task_id, status="completed", ended_at=S.now_iso(),
                artifacts=artifacts, visual_review_evidence=visual_review_evidence,
                unresolved_issues=unresolved_issues or [],
                resume_notes=note)
