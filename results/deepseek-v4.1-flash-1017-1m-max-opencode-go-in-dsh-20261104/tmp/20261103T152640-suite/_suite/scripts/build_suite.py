# -*- coding: utf-8 -*-
"""Build suite-level deliverables: index.md, gallery.md, task-metrics.json, snapshot-usage.md."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

OUT_ROOT = SUITE_ROOT / "outputs" / RUN_ID
SUITE = OUT_ROOT / "_suite"
SUITE.mkdir(parents=True, exist_ok=True)

state = json.loads((SUITE / "suite-state.json").read_text(encoding="utf-8"))
tasks_dir = SUITE_ROOT / "tasks"

TITLES = {}
for d in tasks_dir.iterdir():
    if not d.is_dir():
        continue
    tid = d.name.split("-")[0]
    md = d / "TASK.md"
    title = d.name
    if md.exists():
        for line in md.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^#\s+(.+)$", line.strip())
            if m:
                title = m.group(1).strip()
                break
    TITLES[tid] = title

ORDER = [t["id"] for t in state["tasks"]]
STATUS = {t["id"]: t["status"] for t in state["tasks"]}
STATUS_CN = {"completed": "已完成", "pending": "未开始", "in_progress": "进行中",
             "partial": "部分完成", "blocked": "阻塞"}

def task_files(tid: str):
    d = OUT_ROOT / tid
    if not d.exists():
        return [], []
    pngs = sorted([p for p in d.rglob("*.png")])
    snaps = {}
    for p in d.rglob("*.snapshot"):
        snaps[str(p.relative_to(d).with_suffix(""))] = p
    return pngs, snaps

def metrics(tid: str):
    p = OUT_ROOT / tid / "task-metrics.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

done = [t for t in ORDER if STATUS[t] == "completed"]
pending = [t for t in ORDER if STATUS[t] != "completed"]

# ---------------------------------------------------------------- index.md
lines = [f"# Snapshot 全套任务索引（run {RUN_ID}）", "",
         f"- 运行配置：profile `{state.get('profile')}`，服务 `{state.get('service_base_url')}`",
         f"- 输出根：`outputs/{RUN_ID}/`；临时根：`tmp/{RUN_ID}/`（相对任务根）",
         f"- 状态：`{state.get('status')}`，已完成 **{len(done)}** / {len(ORDER)} 题",
         f"- 开始：{state.get('started_at')}；最后更新：{state.get('updated_at')}",
         "- 总画廊：[gallery.md](gallery.md)；使用与踩坑：[snapshot-usage.md](snapshot-usage.md)；"
         "总指标：[task-metrics.json](task-metrics.json)", ""]
if pending:
    lines.append(f"> 本次交付为**部分完成**：以下 {len(pending)} 题尚未交付 —— {', '.join(pending)}。"
                 "已完成题目的产物、报告与指标均已落盘，恢复方式见 `suite-state.json` 与各题 `resume_notes`。")
    lines.append("")
lines += ["## 逐题状态", "",
          "| # | 题目 | 状态 | 最终图 | 单题入口 | 说明 |",
          "|---|---|---|---|---|---|"]
for i, tid in enumerate(ORDER, start=1):
    pngs, snaps = task_files(tid)
    title = TITLES.get(tid, tid)
    short = title.split("·")[-1].strip() if "·" in title else title
    entry = f"[{tid}](../{tid}/)" if pngs else "—"
    imgs = f"{len(pngs)} 张" if pngs else "—"
    lines.append(f"| {i} | {short} | {STATUS_CN.get(STATUS[tid], STATUS[tid])} | {imgs} | {entry} | "
                 f"[报告](../{tid}/snapshot-usage.md) |")
lines += ["", "## 产物结构", "",
          "- `outputs/<run_id>/<task_id>/`：最终 PNG、同名 `.snapshot`、专用审计 JSON、`snapshot-usage.md`、`task-metrics.json`",
          "- `tmp/<run_id>/<task_id>/`：请求原始字节、`requests.jsonl`、`iterations.jsonl`、脚本、草稿、局部裁图",
          "- `tmp/<run_id>/_suite/`：共享脚本、下载文档缓存、事件流与编号检查点",
          "- `outputs/<run_id>/_suite/`：本索引、画廊、总报告、总指标、`suite-state.json`", ""]
if pending:
    lines += ["## 未完成题目与恢复方式", "",
              "以下题目尚未开始或未完成，目录已按 run_id 预建，恢复时从 `suite-state.json` 的 `current_task` 继续：",
              ""]
    for tid in pending:
        lines.append(f"- `{tid}` {TITLES.get(tid, '')}：{STATUS_CN.get(STATUS[tid], STATUS[tid])}")
    lines.append("")
(SUITE / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- gallery.md
g = [f"# 全套画廊（run {RUN_ID}）", "",
     f"共 {sum(len(task_files(t)[0]) for t in done)} 张最终图片，来自 {len(done)} 个已完成任务。"
     "每张图给出预览、原 PNG 与同名 DSL 链接（相对本文件）。", ""]
for tid in done:
    pngs, snaps = task_files(tid)
    if not pngs:
        continue
    g += [f"## {tid} · {TITLES.get(tid, tid)}", ""]
    for p in pngs:
        relp = p.relative_to(OUT_ROOT / tid).as_posix()
        rel = f"../{tid}/{relp}"
        stem = relp[:-4]
        snap = snaps.get(stem)
        title = stem.replace("/", " · ")
        g.append(f"### {title}")
        g.append("")
        g.append(f"![{tid} {title}]({rel})")
        g.append("")
        links = [f"[原 PNG]({rel})"]
        if snap:
            links.append(f"[DSL]({rel[:-4]}.snapshot)")
        g.append(" · ".join(links))
        g.append("")
missing = [t for t in pending]
if missing:
    g += ["## 未交付题目", "",
          "以下题目在本轮交付中尚未产出最终图片，因此不在上文中占位：" +
          "、".join(f"`{t}`" for t in missing), ""]
(SUITE / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- task-metrics.json
per = []
tot = {"render_requests": 0, "render_ok": 0, "render_failed": 0, "retried_requests": 0,
       "images_opened": 0, "iterations_total": 0, "wall_clock_s": 0.0, "images": 0}
for tid in ORDER:
    m = metrics(tid)
    pngs, _ = task_files(tid)
    if m:
        r = m["request_totals"]
        tot["render_requests"] += r["render_requests"]
        tot["render_ok"] += r["render_ok"]
        tot["render_failed"] += r["render_failed"]
        tot["retried_requests"] += r.get("retried_requests", 0)
        tot["images_opened"] += m["visual_review"]["images_opened"]
        tot["iterations_total"] += m["visual_review"]["iterations_total"]
        tot["wall_clock_s"] += m["wall_clock_s"]
    tot["images"] += len(pngs)
    per.append({"task_id": tid, "status": STATUS[tid], "title": TITLES.get(tid, ""),
                "final_images": len(pngs),
                "render_requests": m["request_totals"]["render_requests"] if m else 0,
                "images_opened": m["visual_review"]["images_opened"] if m else 0,
                "iterations": m["visual_review"]["iterations_total"] if m else 0,
                "wall_clock_s": m["wall_clock_s"] if m else 0,
                "metrics_file": f"outputs/{RUN_ID}/{tid}/task-metrics.json" if m else None})
suite_metrics = {
    "schema_version": 1, "run_id": RUN_ID, "path_base": "suite_root",
    "started_at": state["started_at"], "updated_at": api.iso_now(),
    "status": state["status"],
    "counts": {"tasks_total": len(ORDER), "completed": len(done), "pending": len(pending)},
    "totals": {**{k: (round(v, 1) if isinstance(v, float) else v) for k, v in tot.items()}},
    "scope_note": "总指标按题累加各题顶层 task-metrics.json；shared 准备请求不重复计入各题。",
    "time_source": "各题 tmp/<run_id>/<task_id>/task-clock.json；时区 Asia/Shanghai",
    "tasks": per,
}
(SUITE / "task-metrics.json").write_text(json.dumps(suite_metrics, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
print("built index/gallery/metrics:", len(done), "completed,", tot["images"], "images,",
      round(tot["wall_clock_s"] / 60, 1), "min")
