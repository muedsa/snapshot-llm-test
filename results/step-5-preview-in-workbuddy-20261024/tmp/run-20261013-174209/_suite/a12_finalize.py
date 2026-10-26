# -*- coding: utf-8 -*-
"""A12 finalize：复制终版 PNG/DSL，写 iterations/snapshot-usage/task-metrics，更新 suite-state。"""
from __future__ import annotations

import datetime as dt
import json
import os
import shutil
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A12"
TMP = ROOT / "tmp" / RUN_ID / "A12"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


# ---------- 1. 复制终版 ----------
for n in ["mobile", "tablet", "desktop", "stage"]:
    shutil.copyfile(TMP / f"{n}.snapshot", OUT / f"{n}.snapshot")
    shutil.copyfile(TMP / f"{n}-iter3.png", OUT / f"{n}.png")
print("copied finals")

reqs = read_jsonl(TMP / "requests.jsonl")
renders = [r for r in reqs if r.get("type") == "render"]
measures = [r for r in reqs if r.get("type") == "measure-batch"]
ok = [r for r in renders if r.get("status") == "ok"]
bad = [r for r in renders if r.get("status") != "ok"]


def iso(s):
    return dt.datetime.fromisoformat(s)


all_ts = [iso(r["start_ts"]) for r in reqs]
started = min(all_ts)
ended = max(iso(r["start_ts"]) + dt.timedelta(seconds=r.get("elapsed_s") or 0) for r in reqs)
elapsed = (ended - started).total_seconds()
first_ok = next(r for r in renders if r.get("status") == "ok")
first_usable = (iso(first_ok["start_ts"]) + dt.timedelta(seconds=first_ok["elapsed_s"])
                - started).total_seconds()
req_sum = round(sum(r.get("elapsed_s") or 0 for r in reqs), 3)
by_label = {r.get("label"): r for r in reqs}

# ---------- 2. iterations.jsonl ----------
iters = [
    {"id": "A12-it00", "parent": None, "type": "baseline",
     "dsl": "tmp/run-20261013-174209/A12/mobile.snapshot", "image": "tmp/run-20261013-174209/A12/mobile-base.png",
     "render_request_id": by_label["A12-mobile-baseline"]["id"], "viewed_at": "2026-10-19T15:10:00+08:00",
     "observed": ["v1 生成器按 0.62em/字符估算宽度；CJK 实为 1.0em，芯片/按钮文字被盒宽裁掉。",
                  "主标题 softWrap=true + maxLines=1，折行后只显示第一行，Vision 丢失。"],
     "changes": [], "result": "四图均存在文字截断（ONLII / 详见官网 / example.or）。", "status": "superseded"},
    {"id": "A12-it01", "parent": "A12-it00", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A12/mobile.snapshot", "image": "tmp/run-20261013-174209/A12/mobile-iter2.png",
     "render_request_id": by_label["A12-mobile-iter2-compact"]["id"], "viewed_at": "2026-10-19T15:11:00+08:00",
     "observed": ["紧凑版仍截断：云构中心 · ONLII、免费参加 · 扫码方式；大屏下半屏空白。"],
     "changes": ["压缩 hero 间距"], "result": "未解决根因。", "status": "superseded"},
    {"id": "A12-it02", "parent": "A12-it01", "type": "syntax-fix",
     "dsl": "tmp/run-20261013-174209/A12/probe-clip.snapshot", "image": "tmp/run-20261013-174209/A12/probe-clip.png",
     "render_request_id": by_label["A12-probe-clip"]["id"], "viewed_at": "2026-10-19T15:13:00+08:00",
     "observed": ["同一条文字在盒宽 120/130/140 时被裁、盒宽=实测 147 时完整：文字严格按盒宽裁切，无隐藏内边距。"],
     "changes": ["用 7 组不同盒宽探针确认裁切规则"], "result": "定位根因：盒宽必须 ≥ 实测墨迹宽。", "status": "accepted"},
    {"id": "A12-it03", "parent": "A12-it02", "type": "syntax-fix",
     "dsl": None, "image": None,
     "render_request_id": by_label["A12-measure-full(84items)"]["id"], "viewed_at": None,
     "observed": ["批量测量画布高 8232 超过服务上限 4096，返回 400 RENDER_ERROR。"],
     "changes": ["bm.batch_measure 增加按行高自动分块（每块 ≤3900px）"],
     "result": "批量测量恢复可用。", "status": "accepted"},
    {"id": "A12-it04", "parent": "A12-it03", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A12/mobile.snapshot", "image": "tmp/run-20261013-174209/A12/mobile-iter3.png",
     "render_request_id": by_label["A12-mobile-iter3-measured"]["id"], "viewed_at": "2026-10-19T15:20:00+08:00",
     "observed": ["实测字宽版：主标题两行 Structure / Vision 完整；三个芯片、CTA、website 全部完整；六卡完整；页脚完整。"],
     "changes": ["全串实测宽度决定芯片/CTA/页脚盒宽；主标题按 BOLD 实测字符宽度折行；大屏卡高均分内容垂直居中"],
     "result": "mobile 达标。", "status": "accepted"},
    {"id": "A12-it05", "parent": "A12-it04", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A12/tablet.snapshot", "image": "tmp/run-20261013-174209/A12/tablet-iter3.png",
     "render_request_id": by_label["A12-tablet-iter3-measured"]["id"], "viewed_at": "2026-10-19T15:21:00+08:00",
     "observed": ["两列布局，全部必显字段完整，页脚双行信息完整。"],
     "changes": [], "result": "tablet 达标。", "status": "accepted"},
    {"id": "A12-it06", "parent": "A12-it04", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A12/desktop.snapshot", "image": "tmp/run-20261013-174209/A12/desktop-iter3.png",
     "render_request_id": by_label["A12-desktop-iter3-measured"]["id"], "viewed_at": "2026-10-19T15:22:00+08:00",
     "observed": ["三列布局，字段完整，example.org 不再被裁。"],
     "changes": [], "result": "desktop 达标。", "status": "accepted"},
    {"id": "A12-it07", "parent": "A12-it04", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A12/stage.snapshot", "image": "tmp/run-20261013-174209/A12/stage-iter3.png",
     "render_request_id": by_label["A12-stage-iter3-measured"]["id"], "viewed_at": "2026-10-19T15:23:00+08:00",
     "observed": ["三列 + 卡高均分，下半屏空白消除，字段完整。"],
     "changes": [], "result": "stage 达标。", "status": "accepted"},
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

# ---------- 3. task-metrics.json ----------
metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A12",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A12/",
    "temp_dir": f"tmp/{RUN_ID}/A12/",
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
        "retry_requests": 0,
        "measure_requests": len(measures),
        "other_service_requests": 0,
        "dsl_versions": 3,
        "image_views": 4 + 4 + 1,
        "completed_visual_iterations": 5,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A12/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A12/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A12/mobile.png", "width": 360, "height": 800,
         "dsl": f"outputs/{RUN_ID}/A12/mobile.snapshot"},
        {"path": f"outputs/{RUN_ID}/A12/tablet.png", "width": 768, "height": 1024,
         "dsl": f"outputs/{RUN_ID}/A12/tablet.snapshot"},
        {"path": f"outputs/{RUN_ID}/A12/desktop.png", "width": 1440, "height": 900,
         "dsl": f"outputs/{RUN_ID}/A12/desktop.snapshot"},
        {"path": f"outputs/{RUN_ID}/A12/stage.png", "width": 1920, "height": 1080,
         "dsl": f"outputs/{RUN_ID}/A12/stage.snapshot"},
        {"path": f"outputs/{RUN_ID}/A12/design-tokens.json"},
        {"path": f"outputs/{RUN_ID}/A12/content-map.json"},
        {"path": f"outputs/{RUN_ID}/A12/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A12/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A12/mobile-base.png", "note": "基线：文字截断"},
        {"image": f"tmp/{RUN_ID}/A12/mobile-iter2.png", "note": "紧凑版：仍截断"},
        {"image": f"tmp/{RUN_ID}/A12/probe-clip.png", "note": "盒宽裁切规则探针"},
        {"image": f"outputs/{RUN_ID}/A12/mobile.png", "note": "mobile 终版"},
        {"image": f"outputs/{RUN_ID}/A12/tablet.png", "note": "tablet 终版"},
        {"image": f"outputs/{RUN_ID}/A12/desktop.png", "note": "desktop 终版"},
        {"image": f"outputs/{RUN_ID}/A12/stage.png", "note": "stage 终版"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- 4. snapshot-usage.md ----------
usage = f"""# A12 快照使用与自检报告

- run_id: `{RUN_ID}`；输出目录：`outputs/{RUN_ID}/A12/`；临时目录：`tmp/{RUN_ID}/A12/`
- 状态：completed（四断点全部达标，逐图实际查看）

## 交付物

| 文件 | 尺寸 | DSL |
|---|---|---|
| mobile.png | 360×800 | mobile.snapshot |
| tablet.png | 768×1024 | tablet.snapshot |
| desktop.png | 1440×900 | desktop.snapshot |
| stage.png | 1920×1080 | stage.snapshot |

附加：design-tokens.json（颜色/字号/间距/组件规则与四断点令牌）、
content-map.json（每个必显字段在四种画布中的原文、实际显示文本、文字盒、字号与完整性，C1–C6 卡片 ID 映射）。

## 需求核对

- 四尺寸均完整显示 title、subtitle、date、time、location、cta、website 与六张卡的 title/detail，
  一字不丢（逐图实际查看确认；主标题在手机断点折为 "Structure /" + "Vision" 两行，不改变词语）。
- 字号：主标题 40/48/56/64 ≥ 40；手机正文与卡 detail 16 ≥ 16、卡标题 18 ≥ 18；
  其余断点正文 20/20/22 ≥ 20。安全边距手机 16、其他 32。
- 文字盒无重叠、无出界（content-map.json 坐标程序化校验：4 画布 overlaps=NONE，out-of-canvas=NONE）。
- 适配完全由 DSL 重排（单列/两列/三列），无裁切、无拉伸、无整图 Image；CTA 为文字按钮，无二维码。
- 四断点共用同一套颜色令牌与四种核心构件（圆角卡、accent 竖条、序号圆点、胶囊标签），仅重排。

## 实际文档/工具应用

- open-snapshot 服务：POST /snapshot 渲染 DSL（text/plain → image/png）。
- 服务上限实测：画布任一边 ≤ 4096（批量测量 8232 高被 400 拒绝后按行高自动分块）。
- 裁切规则实测（probe-clip.png）：文字严格按所在盒宽裁切，softWrap=true 时按盒宽折行，
  maxLines 限制显示行数；盒宽 ≥ 实测墨迹宽即完整显示。
- 自建批量测量 tmp/run-20261013-174209/_suite/bm.py：一次渲染多行文字，PIL 按行带统计墨迹宽，
  全串 84 项 + 字符 611 项（BOLD/NORMAL 分开测）。

## 关键问题与修复

1. v1 按 0.62em/字符估算宽度，CJK 实为 1.0em → 芯片/CTA/页脚文字被盒宽裁掉
   （云构中心 · ONLII、免费参加 · 扫码方式、structure.example.or）。
   修复：全部字符串真实渲染测量，盒宽 = 实测 + 内边距。
2. 主标题 softWrap=true + maxLines=1，折行后只显示第一行（Vision 丢失）。
   修复：按 BOLD 实测字符宽度预算行数，maxLines=行数，盒高=行数×行高。
3. 大屏卡高固定导致下半屏大片空白。修复：按可用高度均分卡高（内容垂直居中），
   剩余空间匀给节标题前与行距。

## 未解决事项

无。
"""
(OUT / "snapshot-usage.md").write_text(usage, encoding="utf-8")
print("wrote snapshot-usage.md, task-metrics.json, iterations.jsonl")

# ---------- 5. suite-state.json ----------
state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A12":
        t["status"] = "completed"
        t["started_at"] = started.isoformat()
        t["ended_at"] = ended.isoformat()
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A12/mobile.png", f"outputs/{RUN_ID}/A12/mobile.snapshot",
            f"outputs/{RUN_ID}/A12/tablet.png", f"outputs/{RUN_ID}/A12/tablet.snapshot",
            f"outputs/{RUN_ID}/A12/desktop.png", f"outputs/{RUN_ID}/A12/desktop.snapshot",
            f"outputs/{RUN_ID}/A12/stage.png", f"outputs/{RUN_ID}/A12/stage.snapshot",
            f"outputs/{RUN_ID}/A12/design-tokens.json",
            f"outputs/{RUN_ID}/A12/content-map.json",
            f"outputs/{RUN_ID}/A12/snapshot-usage.md",
            f"outputs/{RUN_ID}/A12/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "tmp/run-20261013-174209/A12/mobile-base.png（基线：CJK 宽度低估导致截断）",
            "tmp/run-20261013-174209/A12/mobile-iter2.png（紧凑版：仍截断）",
            "tmp/run-20261013-174209/A12/probe-clip.png（7 组盒宽探针确认裁切规则）",
            "outputs/run-20261013-174209/A12/mobile.png（终版：标题两行/芯片/CTA/website 全完整）",
            "outputs/run-20261013-174209/A12/tablet.png（终版：两列全完整）",
            "outputs/run-20261013-174209/A12/desktop.png（终版：三列全完整）",
            "outputs/run-20261013-174209/A12/stage.png（终版：三列+卡高均分）",
            "content-map.json 程序化校验：4 画布无文字盒重叠、无出界",
            "tmp/run-20261013-174209/A12/requests.jsonl",
            "tmp/run-20261013-174209/A12/iterations.jsonl",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A13"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# events + checkpoint
ev = {
    "event": "task_completed", "task_id": "A12", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A12/",
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
