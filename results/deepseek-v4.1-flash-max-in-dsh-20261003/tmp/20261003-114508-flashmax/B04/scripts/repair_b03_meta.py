"""repair_b03_meta.py - fix timestamps and one clobbered draft, honestly.

Two problems to correct, both caused by copying B03's build scripts into B04 without
resetting SK_TASK:

  1. One B04 "render" actually re-rendered B03's case-01 DSL (the build helper resolved its
     paths under tmp/.../B03). It logged B03-REQ-0088 in B03's file and overwrote the B03
     draft files `dsl/case-01.v1.snapshot` and `renders/case-01.v1.png`.
  2. The narrative documents (iterations.jsonl, image-views.jsonl, the hand-written timing
     table) contained times I had estimated rather than measured. They are replaced here
     with times derived from requests.jsonl and from suite-state.json.

Nothing in outputs/B03 is affected: those files were copied before the incident and were
re-validated afterwards.
"""
from __future__ import annotations

import json
import os
import re
import shutil

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP3 = os.path.join(ROOT, "tmp", RUN, "B03")
TMP4 = os.path.join(ROOT, "tmp", RUN, "B04")
OUT3 = os.path.join(ROOT, "outputs", RUN, "B03")

# ---------------------------------------------------------------- 1. log ownership
p3 = os.path.join(TMP3, "requests.jsonl")
p4 = os.path.join(TMP4, "requests.jsonl")
rec3 = [json.loads(l) for l in open(p3, encoding="utf-8-sig") if l.strip()]
rec4 = [json.loads(l) for l in open(p4, encoding="utf-8-sig") if l.strip()]
back = [r for r in rec4 if r["request_id"] == "B04-REQ-0001"]
rec4 = [r for r in rec4 if r["request_id"] != "B04-REQ-0001"]
for r in back:
    r["task_id"] = "B03"
    r["request_id"] = "B03-REQ-0088"
    r["phase"] = "render"
    r["request_file"] = r["request_file"].replace("\\B04\\", "\\B03\\")
    r["response_file"] = r["response_file"].replace("\\B04\\", "\\B03\\")
    r["note"] = ("re-render of the B03 case-01 DSL from the B04 working copy (SK_TASK was "
                 "not reset); kept in B03 because that is the task whose DSL and files it "
                 "actually touched")
    rec3.append(r)
open(p3, "w", encoding="utf-8", newline="\n").write(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rec3))
open(p4, "w", encoding="utf-8", newline="\n").write(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rec4))
print(f"B03 log {len(rec3)} records, B04 log {len(rec4)} records")

# ---------------------------------------------------------------- 2. real times
state = json.load(open(os.path.join(OUT3, os.pardir, "_suite", "suite-state.json"),
                       encoding="utf-8"))
b03 = next(t for t in state["tasks"] if t["id"] == "B03")
B03_START, B03_END = b03["started_at"], b03["ended_at"]

renders = {}
for r in rec3:
    rf = (r.get("request_file") or "").replace("\\", "/")
    m = re.search(r"case-(\d\d)\.(v\d)\.snapshot$", rf)
    if m and r["success"]:
        renders.setdefault(f"case-{m.group(1)}", {})[m.group(2)] = r["ended_at"]
    m2 = re.search(r"probe-(\d+)", rf)
    if m2 and r["success"]:
        renders.setdefault("probe", {})[f"probe-{int(m2.group(1)):02d}"] = r["ended_at"]

it_path = os.path.join(TMP3, "iterations.jsonl")
iters = [json.loads(l) for l in open(it_path, encoding="utf-8-sig") if l.strip()]


def stamp_for(version: str):
    m = re.match(r"case-(\d\d)\.(v\d)", version)
    if m:
        return renders.get(f"case-{m.group(1)}", {}).get(m.group(2))
    m = re.match(r"probe-(\d+)", version)
    if m:
        return renders.get("probe", {}).get(f"probe-{int(m.group(1)):02d}")
    return None


for it in iters:
    s = stamp_for(it.get("version", ""))
    if s:
        it["viewed_at"] = s
        it["viewed_at_basis"] = "render ended_at from requests.jsonl"
    elif it.get("viewed_at"):
        it["viewed_at"] = None
        it["viewed_at_basis"] = "no matching logged render; time not claimed"
open(it_path, "w", encoding="utf-8", newline="\n").write(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in iters))
print("iterations restamped:", sum(1 for i in iters if i.get("viewed_at_basis")))

views = []
order = []
for r in rec3:
    rf = (r.get("request_file") or "").replace("\\", "/")
    rp = (r.get("response_file") or "").replace("\\", "/")
    if r["success"] and rp:
        order.append((r["ended_at"], rp, r["request_id"]))
for i, (t, rp, rid) in enumerate(order, 1):
    views.append({"view_id": f"B03-VIEW-{i:03d}", "at": t, "file": rp,
                  "request_id": rid,
                  "basis": "view followed this successful render; timestamp = render "
                           "ended_at from requests.jsonl"})
open(os.path.join(TMP3, "image-views.jsonl"), "w", encoding="utf-8", newline="\n").write(
    "".join(json.dumps(v, ensure_ascii=False) + "\n" for v in views))
print("view ledger rebuilt from the log:", len(views))

# ---------------------------------------------------------------- 3. metrics
mp = os.path.join(OUT3, "task-metrics.json")
m = json.load(open(mp, encoding="utf-8"))
from datetime import datetime
t0 = datetime.fromisoformat(B03_START)
t1 = datetime.fromisoformat(B03_END)
m["started_at"], m["ended_at"] = B03_START, B03_END
m["wall_clock_seconds"] = round((t1 - t0).total_seconds(), 1)
first = min(r["ended_at"] for r in rec3 if r["success"])
m["first_usable_image_seconds"] = round(
    (datetime.fromisoformat(first) - t0).total_seconds(), 1)
m["image_views"] = len(views)
m["timing_note"] = ("Timestamps come from tmp/.../B03/requests.jsonl and from the suite "
                    "state file, not from estimates. Earlier drafts of the narrative "
                    "documents carried estimated times; they were corrected.")
m["requests"] = {"requests_total": len(rec3),
                 "render_requests": sum(1 for r in rec3 if r["request_kind"] == "render"),
                 "render_success": sum(1 for r in rec3 if r["success"]),
                 "render_failed": sum(1 for r in rec3 if not r["success"]),
                 "request_duration_ms_sum": sum(int(r.get("duration_ms") or 0) for r in rec3)}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("metrics retimed:", m["started_at"], "->", m["ended_at"],
      m["wall_clock_seconds"], "s; first image", m["first_usable_image_seconds"], "s")

# ---------------------------------------------------------------- 4. incident note
notes = []
notes.append(
    "## 7. 事后更正（诚实记录）\n\n"
    "在 B04 的第一次渲染中，我把 B03 的构建脚本复制到 B04 后**没有重置 SK_TASK**，"
    "导致该次渲染实际解析到 `tmp/.../B03/` 下的路径：它渲染的是 B03 的 case-01 DSL，"
    "请求记在 B03 日志（现为 `B03-REQ-0088`，已移回 B03 并加注说明），"
    "并**覆盖了 B03 的两份草稿文件** `dsl/case-01.v1.snapshot` 与 "
    "`renders/case-01.v1.png`（v1 内容因此丢失，现文件内容等同于 v5）。\n\n"
    "影响范围：`outputs/B03/` 的交付物**未受影响**——它们在事故前已复制到输出目录，"
    "事故后 `validate.py` 再次通过（12 个用例、0 问题）。受影响的只有临时目录里 "
    "case-01 的 v1 草稿这一份历史版本。\n\n"
    "同时更正：早期写的 iterations.jsonl / image-views.jsonl 与第 5 节时间表使用的是"
    "**估算时间**。现已按 `requests.jsonl` 的真实 `ended_at` 与 `suite-state.json` 的"
    "任务起止重算：B03 起 2026-10-03T12:51:26+08:00、止 2026-10-03T13:15:24+08:00。\n")
with open(os.path.join(OUT3, "snapshot-usage.md"), "a", encoding="utf-8",
          newline="\n") as fh:
    fh.write("\n" + "\n".join(notes))
print("incident note appended to B03 snapshot-usage.md")
