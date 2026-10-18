"""Build honest partial suite artifacts for completed tasks A01–A19, A22–A24."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(".").resolve()
RUN = "20261018T1140"
OUT = ROOT / "outputs" / RUN
SUITE = OUT / "_suite"
SUITE.mkdir(parents=True, exist_ok=True)

order = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]
completed = [f"A{i:02d}" for i in range(1, 20)] + ["A22", "A23", "A24"]
blocked = ["A20", "A21"]
pending = [f"B{i:02d}" for i in range(1, 7)]

# gather paired final images
images = []
for p in sorted(OUT.glob("A*/**/*.png")):
    d = p.with_suffix(".snapshot")
    if d.exists():
        images.append((p.relative_to(OUT).as_posix(), d.relative_to(OUT).as_posix()))
assert len(images) == 57, len(images)

# state
state = json.loads((SUITE / "suite-state.json").read_text(encoding="utf-8"))
state["status"] = "partial"
state["updated_at"] = "2026-10-18T14:15:00+08:00"
state["current_task"] = None
state["current_round"] = None
state["stop_reason"] = "Context/execution budget exhausted after 22 completed tasks; A20/A21 subagent runs were interrupted without final outputs; B01–B06 not started."
state["notes"] = ("Honest partial state. Completed A01–A19, A22–A24 with real service PNG/DSL and reports. "
                  "A20 (24-label dense annotation) and A21 (three-round launch) have no final PNG/DSL: their delegated runs were interrupted before delivery. "
                  "B01–B06 (10 works each) were not started. Suite minimum 124 final images; 57 paired images present.")
for t in state.get("tasks", []):
    tid = t.get("id")
    if tid in completed:
        t["status"] = "completed"
    elif tid in blocked:
        t["status"] = "blocked"
        t["issues"] = ["No final PNG/DSL: delegated run interrupted before delivery."]
    elif tid in pending:
        t["status"] = "pending"
state["last_checkpoint"] = "tmp/%s/_suite/checkpoints/state-000023.json" % RUN
state["suite_artifacts"] = {
    "index": f"outputs/{RUN}/_suite/index.md",
    "gallery": f"outputs/{RUN}/_suite/gallery.md",
    "snapshot_usage": f"outputs/{RUN}/_suite/snapshot-usage.md",
    "task_metrics": f"outputs/{RUN}/_suite/task-metrics.json",
    "suite_state": f"outputs/{RUN}/_suite/suite-state.json",
}
(SUITE / "suite-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
cp = ROOT / "tmp" / RUN / "_suite" / "checkpoints" / "state-000023.json"
cp.parent.mkdir(parents=True, exist_ok=True)
cp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
with open(ROOT / "tmp" / RUN / "_suite" / "events.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"ts": "2026-10-18T14:15:00+08:00", "event": "suite_partial_checkpoint",
                        "completed": 22, "images": 57, "blocked": blocked, "pending": pending}, ensure_ascii=False) + "\n")

# metrics aggregate
task_metrics = []
for t in completed:
    p = OUT / t / "task-metrics.json"
    if p.exists():
        task_metrics.append((t, json.loads(p.read_text(encoding="utf-8"))))
sum_counts = {k: 0 for k in ["snapshot_requests", "successful_snapshot_requests", "failed_snapshot_requests",
                             "retry_requests", "other_service_requests", "dsl_versions", "image_views",
                             "completed_visual_iterations", "incomplete_visual_iterations"]}
for _, m in task_metrics:
    for k in sum_counts:
        sum_counts[k] += int(m.get("counts", {}).get(k, 0) or 0)
suite_metrics = {
    "schema_version": 1, "path_base": "suite_root", "run_id": RUN, "profile": "all",
    "status": "partial", "started_at": "2026-10-18T11:49:56+08:00",
    "last_updated": "2026-10-18T14:15:00+08:00", "elapsed_seconds": 8710,
    "counts": {
        "total_tasks": 30, "completed_tasks": 22, "blocked_tasks": 2, "pending_tasks": 6,
        "final_images": 57, "expected_minimum_images": 124,
        "final_png_dsl_pairs": 57,
        **sum_counts,
        "task_metrics_entries": len(task_metrics),
    },
    "completed": completed, "blocked": blocked, "pending": pending,
    "missing": {
        "A20": "No final annotation PNG/DSL; label/line geometry attempt did not satisfy all constraints; delegated run interrupted.",
        "A21": "No round-01/02/03 final PNG/DSL; delegated run interrupted before delivery.",
        "B01–B06": "Not started; each requires at least 10 independent works (60 images).",
    },
    "tasks": [{"id": t, "status": "completed", "metrics": m.get("counts", {})} for t, m in task_metrics],
    "source": "per-task outputs/<run>/<task>/task-metrics.json; missing tasks have no metrics",
}
(SUITE / "task-metrics.json").write_text(json.dumps(suite_metrics, ensure_ascii=False, indent=2), encoding="utf-8")

# index
lines = [f"# Snapshot 全套 · {RUN} · 部分完成索引", "",
         f"- 状态：**partial**（22/30 完成，57 张最终 PNG；最低要求 124 张）",
         "- 完成：A01–A19、A22、A23、A24",
         "- 阻塞：A20（24 点密集标注，无最终 PNG/DSL）、A21（三轮发布物，无最终 PNG/DSL）",
         "- 未开始：B01–B06（每题至少 10 件，共 60 件）",
         "- 总画廊：[gallery.md](gallery.md) · 过程：[snapshot-usage.md](snapshot-usage.md) · 指标：[task-metrics.json](task-metrics.json)",
         "", "## 任务状态", "", "| 任务 | 状态 | 入口/产物 | 备注 |", "|---|---|---|---|"]
notes = {
    "A20": "无最终图；标签/引导线几何未通过完整验收，代理运行被中断",
    "A21": "无最终图；三轮交付未产出服务 PNG/DSL",
}
for t in order:
    if t in completed:
        n = "已完成并核验"
        ent = f"[{t}/](../{t}/)"
    elif t in blocked:
        n = notes[t]
        ent = f"[{t}/](../{t}/)" if (OUT / t).exists() else "—"
    else:
        n = "未开始"
        ent = "—"
    lines.append(f"| {t} | {t in completed and 'completed' or (t in blocked and 'blocked' or 'pending')} | {ent} | {n} |")
lines += ["", "## 已交付统计", "",
          f"- 最终 PNG/DSL 配对：{len(images)}",
          f"- 服务请求：{sum_counts['snapshot_requests']}（成功 {sum_counts['successful_snapshot_requests']}，失败 {sum_counts['failed_snapshot_requests']}，重试 {sum_counts['retry_requests']}）",
          f"- 看图次数：{sum_counts['image_views']}；完整视觉迭代：{sum_counts['completed_visual_iterations']}",
          "- 缺失：A20/A21 及 B01–B06；未把缺失题当作完成。",
          "", "## 恢复方法", "",
          "1. A20：继续完成 24 标签非重叠放置与引导线审计，渲染 `outputs/" + RUN + "/A20/annotated-map.png`。",
          "2. A21：按 rounds/round-02.md、round-03.md 连续完成三轮六图并保存。",
          "3. B01–B06：每题至少 10 件独立作品，逐件真实渲染、查看、写 case.md 与 portfolio。",
          "4. 全部完成后重建 `_suite/gallery.md`、`task-metrics.json`、`suite-state.json` 为 completed。"]
(SUITE / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# gallery
g = [f"# 全画廊 · {RUN}（部分）", "",
     f"仅列出实际交付的 {len(images)} 张最终 PNG 与同名 `.snapshot`；缺失题不占位。", ""]
for t in completed:
    ims = [(p, d) for p, d in images if p.startswith(t + "/")]
    if not ims:
        continue
    g += [f"## {t}（{len(ims)} 张）", ""]
    for p, d in ims:
        label = p.split("/", 1)[1]
        g += [f"### {t} · {label}", f"![{t} {label}](../{p})", "",
              f"- 原图：[{p}](../{p})", f"- DSL：[{d}](../{d})", ""]
(SUITE / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")

# suite usage
usage = f"""# 全套 Snapshot 使用与审查记录（部分）

## 结果
- run_id：`{RUN}`；22/30 题完成；57 张最终 PNG 与同名 DSL；最低要求 124 张，未达成。
- 完成：A01–A19、A22、A23、A24。缺失：A20、A21、B01–B06。
- 缺失原因：A20 的 24 标签/引导线几何未达到完整验收，代理运行被中断；A21 三轮六图未产出；B01–B06 未开始。没有把缺失或未看图任务标为完成。

## 实际应用
- 全部作品使用 open-snapshot `POST /snapshot`，真实 200 `image/png`；DSL 由本地程序生成并保留。
- 使用 Text `text` 属性保字面 `<>&`、嵌套 span/Raw、Transform、ClipPath/多边形、ImageFiltered、Opacity、ELEVATION、透明 PNG 等；未使用 Image 嵌入。
- 关键计算：A01 净收入 918,624；A04 26.0%→16.6%；A11 Decimal 税费 236.66、应付 4,215.96；A14 八卡标题断行；A16 Q3 利润 32、Q4 54；A19 64 对象与像素等价遮挡；A22 三轮 260 完工；A23 12 单元 6 帧；A24 双团队 260 分排程。

## 文档与踩坑
- ai-guide、parser-tags、layout guide 实际阅读并缓存；字体用 Inter/Noto CJK/Noto Mono/DejaVu。
- 服务多次 TLS/empty reply/超时：A18 2 次、A21/A20 中断、A22 2 次、A24 2 次；失败响应/重试均保留。
- 全 Positioned 的嵌套 Stack 会无限布局，需要非定位 SizedBox；Text 内空格会被 trim，标题/富文本用 Raw 或 text 属性；CMYK/SVG/GIF/动画时间轴不原生支持（A23 已如实替代）。

## 审查
- 已完成图逐张 `read_image` 查看，密集题另做局部/接触表；缺失题没有声称已看。
- 总画廊 57 张，链接相对 `_suite/`；所有链接指向现有输出文件。
- 未完成：A20、A21、B01–B06；恢复步骤见 `index.md`。
"""
(SUITE / "snapshot-usage.md").write_text(usage, encoding="utf-8")
print("suite partial", len(images), sum_counts)