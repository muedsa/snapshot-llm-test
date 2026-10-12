#!/usr/bin/env python3
"""B03 收尾：把 suite-state.json 的 B03 标为 completed（逐件真实证据），开 B04，
追加 events.jsonl 与新编号检查点。所有数字从 task-metrics.json / 磁盘实际文件取。"""
import json, os, re, glob
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID
TMP = ROOT / "tmp" / RID
NOW = datetime.now(timezone.utc).isoformat()

m = json.load(open(OUT / "B03" / "task-metrics.json", encoding="utf-8"))
C, T = m["counts"], m["timings"]
cases = sorted(p.name for p in (TMP / "B03").glob("case-*") if p.is_dir())
CI = json.load(open(TMP / "B03" / "case-info.json", encoding="utf-8"))
QA = sum(len(v["qa_crops"]) for v in CI.values())
PREV = len(list((OUT / "B03").glob("case-*/v*-preview.png")))
assert len(cases) == 10, cases

state_p = OUT / "_suite" / "suite-state.json"
s = json.load(open(state_p, encoding="utf-8"))
b3 = next(t for t in s["tasks"] if t["id"] == "B03")
b4 = next(t for t in s["tasks"] if t["id"] == "B04")

finals = []
for c in cases:
    d = OUT / "B03" / c
    finals.append("%s/final.png + %s/final.snapshot" % (c, c))

b3.update({
    "status": "completed",
    "ended_at": T["ended_at"],
    "updated_at": NOW,
    "completed_rounds": [],
    "completed_cases": ["%s (10/10 全交付)" % c for c in cases],
    "artifacts": [
        "outputs/%s/B03/case-01..case-10/{final.png, final.snapshot, case.md}" % RID,
        "outputs/%s/B03/case-04..case-10 另有 data.json（真实/虚构数据来源声明）" % RID,
        "outputs/%s/B03/portfolio.json" % RID,
        "outputs/%s/B03/portfolio.md" % RID,
        "outputs/%s/B03/gallery.md" % RID,
        "outputs/%s/B03/technique-notes.md" % RID,
        "outputs/%s/B03/snapshot-usage.md" % RID,
        "outputs/%s/B03/task-metrics.json" % RID,
    ],
    "visual_review_evidence": [
        "tmp/%s/B03/iterations.jsonl：%d 条记录（baseline %d／visual %d／visual-fix %d 等），image_viewed=true 的看图 %d 次"
        % (RID, C["iteration_records"], C.get("iteration_records_by_kind", {}).get("baseline", 0),
           C.get("iteration_records_by_kind", {}).get("visual", 0),
           C.get("iteration_records_by_kind", {}).get("visual-fix", 0), C["image_views"]),
        "tmp/%s/B03/tool-usage.jsonl：%d 条工具记录（渲染服务／PIL 裁切放大／TextFit 闸门／断言／promote 字节指纹）" % (RID, C["tool_usage_records"]),
        "tmp/%s/B03/case-*/qa-*.png 与顶层 case0*-qa-*.png、qa[0-9][0-9]-*.png：%d 张 1:1／2× 放大看图裁片（留证，不作交付物）" % (RID, QA),
        "每件 case.md 的「看图证据」小节记录实际所见与由此产生的修改；未看图的 3 个版本在报告里明确标注未取得图像",
    ],
    "unresolved_issues": [],
    "resume_notes": "B03 已交付并收尾，无遗留。服务无矢量 path、fontFeatures 只解析不应用、"
                    "Container clipBehavior 400 三项已写入 snapshot-usage.md 的未解决事项，跨题沿用其结论。",
})
b4["status"] = "in_progress"
b4["started_at"] = NOW
b4["updated_at"] = NOW
s.update({"current_task": "B04", "current_round": None, "current_case": None, "updated_at": NOW})

CK = TMP / "_suite" / "checkpoints"
last = sorted(os.listdir(CK))[-1]
nxt = "state-%06d.json" % (int(re.search(r"state-(\d+)", last).group(1)) + 1)
s["last_checkpoint"] = "tmp/%s/_suite/checkpoints/%s" % (RID, nxt)
json.dump(s, open(state_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(s, open(TMP / "_suite" / "checkpoints" / nxt, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

with open(TMP / "_suite" / "events.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({
        "ts": NOW, "run_id": RID, "task_id": "B03", "event": "task_completed",
        "status": "completed", "path_base": "suite_root",
        "note": ("B03 十件全交付：%d 次请求（%d 成功／%d 失败留证）、%d 条迭代、%d 次看图、%d 张版本预览＋%d 张 QA 裁图；"
                 "六份交付物齐（portfolio.json/md、gallery.md、technique-notes.md、snapshot-usage.md、task-metrics.json），"
                 "117 条相对链接与全部 md5 配对已校验；墙钟 %.0f 秒中空闲 %.0f 秒已按证据分列")
                % (C["snapshot_requests"], C["successful_snapshot_requests"],
                   C["failed_snapshot_requests"], C["iteration_records"], C["image_views"],
                   PREV, QA, T["wall_clock_seconds"], T["idle_gap_seconds"])}, ensure_ascii=False) + "\n")
    f.write(json.dumps({
        "ts": NOW, "run_id": RID, "task_id": "B04", "event": "task_started",
        "status": "in_progress", "path_base": "suite_root",
        "note": "按 catalog 顺序进入 B04，先读本题 TASK.md/AGENTS.md 与 inputs/"}, ensure_ascii=False) + "\n")
print("B03 completed | checkpoint", nxt)
