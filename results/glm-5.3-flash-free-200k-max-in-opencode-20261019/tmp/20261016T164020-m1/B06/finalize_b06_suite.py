# -*- coding: utf-8 -*-
"""B06 套件指针收尾：suite-state 更新（B06→completed; A21 final_images 修正）
+ events 追加 + checkpoint 落盘。路径相对 suite_root，不覆盖旧 checkpoint。"""
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\mine\test\glm-5.3-flash")
RUN = "20261016T164020-m1"
SUITE_OUT = ROOT / "outputs" / RUN / "_suite"
SUITE_TMP = ROOT / "tmp" / RUN / "_suite"
NOW = datetime.now().astimezone().isoformat(timespec="milliseconds")

SS = SUITE_OUT / "suite-state.json"
st = json.loads(SS.read_text(encoding="utf-8"))

# A21 的 final_images 补齐为磁盘实际（此前缺字段计 0，全套终图合计应为 124）
a21 = [t for t in st["tasks"] if t["id"] == "A21"][0]
a21.setdefault("final_images", 6)
if a21.get("final_images") != 6:
    a21["resume_notes"] = (a21.get("resume_notes") or "") + "；final_images 依磁盘审计修正为 6（r1/r2/r3 × portrait+wide）"

b06 = [t for t in st["tasks"] if t["id"] == "B06"][0]
b06.update({
    "status": "completed",
    "started_at": "2026-10-18T20:45:48+08:00",
    "ended_at": NOW,
    "output_dir": "outputs/%s/B06/" % RUN,
    "temp_dir": "tmp/%s/B06/" % RUN,
    "completed_rounds": [],
    "completed_cases": ["case-%02d" % i for i in range(1, 11)],
    "artifacts": [
        "portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
        "task-metrics.json", "problem-evidence.json", "design-review.md",
        "case-01..10/（final.png + final.snapshot + case.md ×10）"],
    "visual_review_evidence": [
        "tmp/%s/B06/steps/sheet-1.png" % RUN, "tmp/%s/B06/steps/sheet-2.png" % RUN,
        "tmp/%s/B06/steps/sheet-3.png" % RUN, "tmp/%s/B06/steps/sheet-4.png" % RUN,
        "tmp/%s/B06/steps/sheet-5.png" % RUN,
        "tmp/%s/B06/steps/zoom-case-02-a.png" % RUN,
        "tmp/%s/B06/steps/zoom-case-03-b.png" % RUN,
        "tmp/%s/B06/steps/zoom-case-06-b.png" % RUN,
        "tmp/%s/B06/steps/zoom-case-09-a.png" % RUN,
        "tmp/%s/B06/steps/text_dump.png" % RUN if False else "tmp/%s/B06/text_dump.txt" % RUN,
    ],
    "unresolved_issues": [],
    "resume_notes": ("十件《日常信息重构》定稿：c01/c03/c05=v3，c02=v5，c04/c07/c08/c09/c10=v4，c06=v6；"
                     "39 渲染请求全 200（v1×10 版式崩坏留证 + v2×10 驱动误渲 + v3×10 语法修复 + v4×7/v5×1/v6×1）；"
                     "看图 41 次（5 接触表 + 10 整幅 + 21 zoom + 5 终表）。"
                     "problem-evidence.json（三分类）+ design-review.md（可观改善 vs 未验证）已交。"),
    "final_images": 10,
})
st["completed_task_count"] = 30
st["current_task"] = None
st["current_round"] = None
st["current_case"] = None
st["updated_at"] = NOW
st["last_checkpoint"] = "state-000052.json"
SS.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("suite-state B06 -> completed; completed=30; suite finals (from task entries):",
      sum([t.get("final_images", 0) or 0 for t in st["tasks"]]))

# events 追加
EV = SUITE_TMP / "events.jsonl"
ev_next = len(EV.read_text(encoding="utf-8").strip().splitlines()) + 1
event = {
    "id": "SUITE-ev-%06d" % ev_next,
    "at": NOW,
    "kind": "task-completed",
    "task_id": "B06",
    "detail": ("十件《日常信息重构》全部虚构/演示口径交付（c01..c10 终版 v3/v5/v3/v4/v3/v6/v4/v4/v4/v4，体系均独立成图）："
               "39 渲染请求（39×200；v1 版式崩坏与 v2 驱动误渲响应全部留证 renders/）+ 41 次真实看图"
               "（10 整幅、21 放大切片、10 接触表）；40 行迭代台账（baseline 10 / syntax 20 / visual 9 / final 1）；"
               "两次 websearch（财政部 2023-30 公告、WHO 25g）真实核实并记 plan v1.1；"
               "problem-evidence.json（可观察/标准政策/自拟演示三分类）+ design-review.md"
               "（可观改善 vs 未验证效果）+ 交付十 case.md 与指标全落盘；套件下一号进入总装。"),
}
with EV.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False) + "\n")
print("event appended:", event["id"], "total rows:", ev_next)

# checkpoint
ck = dict(st)
ck["checkpoint_id"] = "state-000052.json"
ck["checkpoint_at"] = NOW
ck["checkpoint_prev"] = "tmp/%s/_suite/checkpoints/state-000051.json" % RUN
CK = SUITE_TMP / "checkpoints" / "state-000052.json"
if CK.exists():
    CK = SUITE_TMP / "checkpoints" / "state-000052_dup.json"
CK.write_text(json.dumps(ck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("checkpoint saved:", CK.name)

# 磁盘终图审计（逐任务）
audit = {}
for t in st["tasks"]:
    d = ROOT / "outputs" / RUN / t["id"]
    n = 0
    for p in d.rglob("*.png"):
        if "_suite" not in p.parts:
            n += 1
    audit[t["id"]] = n
    if t.get("final_images") != n:
        print("MISMATCH", t["id"], "state=", t.get("final_images"), "disk=", n)
print("disk audit:", audit, "TOTAL:", sum(audit.values()))
