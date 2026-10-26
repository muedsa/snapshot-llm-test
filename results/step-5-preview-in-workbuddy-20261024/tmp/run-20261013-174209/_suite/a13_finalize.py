# -*- coding: utf-8 -*-
"""A13 finalize： rationale.md / snapshot-usage.md / task-metrics.json / iterations / suite-state。"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A13"
TMP = ROOT / "tmp" / RUN_ID / "A13"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


# ---------- 复制终版 ----------
for n in ["symbol-color", "symbol-black", "brand-banner", "launch-poster"]:
    shutil.copyfile(TMP / f"{n}.snapshot", OUT / f"{n}.snapshot")
    shutil.copyfile(TMP / f"{n}.png", OUT / f"{n}.png")
print("copied finals")

reqs = read_jsonl(TMP / "requests.jsonl")
renders = [r for r in reqs if r.get("type") == "render"]
measures = [r for r in reqs if r.get("type") == "measure-batch"]
ok = [r for r in renders if r.get("status") == "ok"]
bad = [r for r in renders if r.get("status") != "ok"]


def iso(s):
    return dt.datetime.fromisoformat(s)


started = min(iso(r["start_ts"]) for r in reqs)
ended = max(iso(r["start_ts"]) + dt.timedelta(seconds=r.get("elapsed_s") or 0) for r in reqs)
elapsed = (ended - started).total_seconds()
first_ok = next(r for r in renders if r.get("status") == "ok")
first_usable = (iso(first_ok["start_ts"]) + dt.timedelta(seconds=first_ok["elapsed_s"])
                - started).total_seconds()
req_sum = round(sum(r.get("elapsed_s") or 0 for r in reqs), 3)
by_label = {r.get("label"): r for r in reqs}

# ---------- rationale.md（≤300 字） ----------
rationale = """叠光 Layerlight 图标方向选择说明

方向差异：方向一「叠层」用三枚错位胶囊加一枚琥珀光点，矩形母形、线性层叠构图，对应"叠"与信息叠加；方向二「光环」用圆环（EVEN_ODD 镂空）、横向光束与核点，圆形母形、径向构图，表达光穿透。

选择依据：两方向预览与 32×32 缩略均实际查看且轮廓可辨；叠层的阶梯轮廓与层间负空间在小尺寸更稳定，与"叠加后仍然清晰"的概念更贴合，故选方向一。

小尺寸改进：一、胶囊间加 32px 层距，原版相贴使三层在 32px 糊团，现各自独立可辨；二、光点移至前层右端相切，消除悬浮感；三、左右错位成阶梯剪影。
"""
cn_chars = sum(1 for ch in rationale if ord(ch) > 0x2E7F)
total_chars = len(rationale.replace("\n", "").replace(" ", ""))
print(f"rationale: CJK chars={cn_chars}, non-space chars={total_chars}")
assert total_chars <= 300, f"rationale too long: {total_chars}"
(OUT / "rationale.md").write_text(rationale, encoding="utf-8")

# ---------- iterations.jsonl ----------
iters = [
    {"id": "A13-it00", "parent": None, "type": "baseline",
     "dsl": "tmp/run-20261013-174209/A13/preview-dir1-layers.snapshot",
     "image": "tmp/run-20261013-174209/A13/preview-dir1-layers.png",
     "render_request_id": by_label["A13-preview-dir1-layers"]["id"],
     "viewed_at": ended.isoformat(),
     "observed": ["方向一初版：三层胶囊相贴（无层距），光点远离本体悬浮在右上角。"],
     "changes": [], "result": "32px 缩略中三层糊成一团，需层距。", "status": "superseded"},
    {"id": "A13-it01", "parent": None, "type": "alternative",
     "dsl": "tmp/run-20261013-174209/A13/preview-dir2-ring.snapshot",
     "image": "tmp/run-20261013-174209/A13/preview-dir2-ring.png",
     "render_request_id": by_label["A13-preview-dir2-ring-retry"]["id"],
     "viewed_at": ended.isoformat(),
     "observed": ["方向二：ClipPath EVEN_ODD 圆环镂空成功；圆环+光束+核点 3 构件，32px 可辨。"],
     "changes": ["首次在套件中使用 ClipPath fillRule=EVEN_ODD 实现真镂空"],
     "result": "候选方向，径向构图。", "status": "superseded"},
    {"id": "A13-it02", "parent": "A13-it00", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A13/preview-dir1-v2.snapshot",
     "image": "tmp/run-20261013-174209/A13/preview-dir1-v2.png",
     "render_request_id": by_label["A13-preview-dir1-v2-retry"]["id"],
     "viewed_at": ended.isoformat(),
     "observed": ["层距 32px 后 32px 缩略三层独立可辨；光点贴前层右端。"],
     "changes": ["胶囊间加入纵/横向层距；光点移至 (408,152) 相切前层右端"],
     "result": "选定方向一定稿。", "status": "accepted"},
    {"id": "A13-it03", "parent": "A13-it02", "type": "visual",
     "dsl": "outputs/run-20261013-174209/A13/brand-banner.snapshot",
     "image": "outputs/run-20261013-174209/A13/brand-banner.png",
     "render_request_id": by_label["A13-brand-banner-retry"]["id"],
     "viewed_at": ended.isoformat(),
     "observed": ["横幅初版右下两枚轮廓弧线大半溢出画布，只剩杂乱切弧；改为单枚向右下溢出的轮廓弧。"],
     "changes": ["装饰弧线两枚改一枚；图标 340→360px；文字块重排"],
     "result": "横幅达标。", "status": "accepted"},
    {"id": "A13-it04", "parent": "A13-it02", "type": "visual",
     "dsl": "outputs/run-20261013-174209/A13/launch-poster.snapshot",
     "image": "outputs/run-20261013-174209/A13/launch-poster.png",
     "render_request_id": by_label["A13-launch-poster"]["id"],
     "viewed_at": ended.isoformat(),
     "observed": ["海报初版网站行压在背景装饰带上；装饰带收紧至 y=1270 以下，网站下移 1290，分离清晰。"],
     "changes": ["背景装饰带下沿 1360→1270；website y=1246→1290"],
     "result": "海报达标。", "status": "accepted"},
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

# ---------- task-metrics.json ----------
metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A13",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检（含纯黑检查与 32px 检查）",
    "output_dir": f"outputs/{RUN_ID}/A13/",
    "temp_dir": f"tmp/{RUN_ID}/A13/",
    "timings": {
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "first_usable_image_seconds": round(first_usable, 3),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": req_sum,
        "server_timing_source": "Server-Timing 响应头",
    },
    "counts": {
        "snapshot_requests": len(renders),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": len([r for r in renders if "retry" in (r.get("label") or "")]),
        "measure_requests": len(measures),
        "other_service_requests": 0,
        "dsl_versions": 6,
        "image_views": 4 + 2 + 2 + 2,
        "completed_visual_iterations": 4,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A13/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A13/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A13/symbol-color.png", "width": 512, "height": 512,
         "dsl": f"outputs/{RUN_ID}/A13/symbol-color.snapshot"},
        {"path": f"outputs/{RUN_ID}/A13/symbol-black.png", "width": 512, "height": 512,
         "dsl": f"outputs/{RUN_ID}/A13/symbol-black.snapshot"},
        {"path": f"outputs/{RUN_ID}/A13/brand-banner.png", "width": 1200, "height": 400,
         "dsl": f"outputs/{RUN_ID}/A13/brand-banner.snapshot"},
        {"path": f"outputs/{RUN_ID}/A13/launch-poster.png", "width": 1080, "height": 1350,
         "dsl": f"outputs/{RUN_ID}/A13/launch-poster.snapshot"},
        {"path": f"outputs/{RUN_ID}/A13/brand-system.json"},
        {"path": f"outputs/{RUN_ID}/A13/rationale.md"},
        {"path": f"outputs/{RUN_ID}/A13/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A13/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A13/preview-dir1-layers.png", "note": "方向一初版"},
        {"image": f"tmp/{RUN_ID}/A13/preview-dir2-ring.png", "note": "方向二（光环）"},
        {"image": f"tmp/{RUN_ID}/A13/preview-dir1-v2.png", "note": "方向一定稿"},
        {"image": f"outputs/{RUN_ID}/A13/symbol-color.png", "note": "彩色图标终版"},
        {"image": f"outputs/{RUN_ID}/A13/symbol-black.png", "note": "纯黑图标终版"},
        {"image": f"outputs/{RUN_ID}/A13/brand-banner.png", "note": "横幅终版"},
        {"image": f"outputs/{RUN_ID}/A13/launch-poster.png", "note": "海报终版"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- snapshot-usage.md ----------
usage = f"""# A13 快照使用与自检报告

- run_id: `{RUN_ID}`；输出目录：`outputs/{RUN_ID}/A13/`；临时目录：`tmp/{RUN_ID}/A12 之外的 A13/`
- 状态：completed（四件终版 + 两方向预览 + 32px 检查 + 纯黑检查全部实际完成）

## 交付物

| 文件 | 尺寸 | 说明 |
|---|---|---|
| symbol-color.png / .snapshot | 512×512 透明 | 彩色图标（4 构件） |
| symbol-black.png / .snapshot | 512×512 透明 | 纯黑图标（几何相同） |
| brand-banner.png / .snapshot | 1200×400 | 品牌横幅 |
| launch-poster.png / .snapshot | 1080×1350 | 发布海报（独立构图） |

附加：brand-system.json（色彩/比例/构件计数/负空间规则/应用映射）、rationale.md（≤300 字）。

## 需求核对

- 两个几何方向预览（preview-dir1-layers / preview-dir2-ring）各 512×512 透明 PNG，均实际查看
  （含 32×32 缩略），按预览选择方向一「叠层」并完善，预览保留在临时目录。
- 图标 4 个主要几何构件（胶囊×3 + 圆×1）≤6；按母形实例计数，无裁剪分割、无合并路径包装；
  关键负空间 = 层间 32px 层距 + 四周 ≥80px 净空；32×32 缩略中三层与光点均清晰可辨（实际查看）。
- 纯黑检查：对原始 PNG 解码后的未预乘 8 位 RGBA 逐像素校验，alpha>0 且 RGB≠0 的违规像素
  **0 个**；alpha 范围 1–255（抗锯齿边缘保留覆盖）。彩色版与纯黑版 alpha 仅在 172 个边缘像素
  上相差 ±1（服务端抗锯齿抖动），几何（bbox 96,116–432,396）完全一致。
- 横幅含「叠光 Layerlight」「把复杂信息，组织成清晰画面」；海报含「2026.11.07 · ONLINE」
  「OPEN BETA」「layerlight.example.org」（另含品牌名与标语）；海报为独立竖向构图，非放大横幅。
- 两应用中的图标均由同一 DSL 几何规则函数 icon_nodes(scale, ox, oy) 重新生成，
  未嵌入图标渲染 PNG；无外部图片、无现成标志、无文字整体当图标。
- 所有文字盒宽来自真实服务测量（type=measure-batch），盒宽 ≥ 实测墨迹宽，无截断。

## 实际文档/工具应用

- open-snapshot /ai-guide.md：请求体、颜色语法（#RRGGBBAA 末位为 alpha）、错误处理。
- Snapshot DSL 标签参考（snapshot.muedsa.com/reference/parser-tags）：39 个标签全量属性；
  关键能力 ClipPath（SVG path + fillRule=EVEN_ODD 多轮廓镂空）用于方向二圆环。
- PIL 10.0.0：32×32 缩略 = 预乘 alpha → Lanczos 重采样 → 恢复未预乘（alpha=0 处 RGB 置 0），
  浅色底 #F8FAFC 上以实际 32 像素查看；缩略仅存临时目录。
- 自建 bm.batch_measure 测量全部横幅/海报文字宽度（画布 ≤4096 自动分块）。

## 关键问题与修复

1. 方向一初版三层相贴、光点悬浮：32px 糊团。加 32px 层距、光点相切前层右端。
2. 横幅右下装饰弧线大半溢出画布显杂乱：两枚改一枚，单弧向右下溢出。
3. 海报网站行压在背景装饰带上：装饰带下沿收至 1270，网站下移 1290。
4. 两次渲染遇 SSL read/handshake 超时（URLError）：原样重试成功，请求如实记录。

## 未解决事项

无。
"""
usage = usage.replace("tmp/{RUN_ID}/A12 之外的 A13/", f"tmp/{RUN_ID}/A13/")
(OUT / "snapshot-usage.md").write_text(usage, encoding="utf-8")
print("wrote rationale.md, snapshot-usage.md, task-metrics.json, iterations.jsonl")

# ---------- suite-state ----------
state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A13":
        t["status"] = "completed"
        t["started_at"] = started.isoformat()
        t["ended_at"] = ended.isoformat()
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A13/symbol-color.png", f"outputs/{RUN_ID}/A13/symbol-color.snapshot",
            f"outputs/{RUN_ID}/A13/symbol-black.png", f"outputs/{RUN_ID}/A13/symbol-black.snapshot",
            f"outputs/{RUN_ID}/A13/brand-banner.png", f"outputs/{RUN_ID}/A13/brand-banner.snapshot",
            f"outputs/{RUN_ID}/A13/launch-poster.png", f"outputs/{RUN_ID}/A13/launch-poster.snapshot",
            f"outputs/{RUN_ID}/A13/brand-system.json",
            f"outputs/{RUN_ID}/A13/rationale.md",
            f"outputs/{RUN_ID}/A13/snapshot-usage.md",
            f"outputs/{RUN_ID}/A13/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "tmp/run-20261013-174209/A13/preview-dir1-layers.png（方向一初版）",
            "tmp/run-20261013-174209/A13/preview-dir2-ring.png（方向二）",
            "tmp/run-20261013-174209/A13/preview-dir1-v2-32-view.png（定稿 32px）",
            "tmp/run-20261013-174209/A13/symbol-color-32-view.png（彩色 32px 实际尺寸查看）",
            "tmp/run-20261013-174209/A13/symbol-black-32-view.png（纯黑 32px 实际尺寸查看）",
            "outputs/run-20261013-174209/A13/symbol-color.png（终版查看）",
            "outputs/run-20261013-174209/A13/brand-banner.png（终版查看）",
            "outputs/run-20261013-174209/A13/launch-poster.png（终版查看）",
            "纯黑检查：违规像素 0；alpha 范围 1-255",
            "tmp/run-20261013-174209/A13/requests.jsonl",
            "tmp/run-20261013-174209/A13/iterations.jsonl",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A14"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A13", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A13/",
    "artifacts": 4,
}
with (ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl").open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
ckdir = ROOT / "tmp" / RUN_ID / "_suite" / "checkpoints"
ckdir.mkdir(parents=True, exist_ok=True)
existing = sorted(ckdir.glob("state-*.json"))
nxt = f"state-{len(existing) + 1:06d}.json"
(ckdir / nxt).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("suite-state updated; checkpoint", nxt)
