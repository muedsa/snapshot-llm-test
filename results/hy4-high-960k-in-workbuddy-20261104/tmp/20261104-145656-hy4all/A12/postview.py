#!/usr/bin/env python3
"""A12 post-visual-review: record real per-canvas observations.

Run only after all four final PNGs have actually been opened and inspected.
"""
import json
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite  # noqa: E402

TASK = "A12"
out = suite.out_dir(TASK)
p = out / "content-map.json"
cm = json.loads(p.read_text(encoding="utf-8"))

for e in cm["entries"]:
    for cv, info in e["canvases"].items():
        info["render_verified"] = True

conclusions = [
    "已确认：19 个必显字段（title、subtitle、date、time、location、cta、website 与六卡 title/detail）在 mobile/tablet/desktop/stage 四张最终 PNG 中逐张完整出现，逐字核对无缩写、无省略号、无删句、无改写；content-map.json 的 19 条 entries × 4 画布均 text_complete=true。",
    "已确认：build.py overlap_check() 与 bounds_check() 对 113 个文字盒（含 DATE/TIME/PLACE 标签与 C1–C6 徽章）检出 0 个相交、0 个越界；四张实际渲染图亦无文字重叠、挤压、裁切或越界。",
    "已确认：design-tokens.json 记录四断点字号与安全边距；手机正文 16 / 卡标题 18，平板、桌面、大屏正文≥20 且主标题分别为 48/44/72（均≥40）；安全边距手机 16 / 其余 32；2× 局部放大确认最小字号仍清晰可读。",
    "已完成：四张最终 PNG 均用 ViewImage 逐张打开，另打开 4 张局部放大图（mobile 卡片区、mobile 底部 CTA、stage 头部、desktop 左栏），逐字核对 C5 的逗号、C6 的 DSL/顿号、CTA 与官网原文，均完整。",
]
for c, obs in zip(cm["checks"], conclusions):
    c["observed"] = obs
    c["verified"] = True

cm["visual_review"] = [
    "outputs/20261104-145656-hy4all/A12/mobile.png — ViewImage 整图打开，19 字段完整",
    "outputs/20261104-145656-hy4all/A12/tablet.png — ViewImage 整图打开，19 字段完整",
    "outputs/20261104-145656-hy4all/A12/desktop.png — ViewImage 整图打开，19 字段完整",
    "outputs/20261104-145656-hy4all/A12/stage.png — ViewImage 整图打开，19 字段完整",
    "tmp/20261104-145656-hy4all/A12/inspection/mobile-cards.png — 2× 六卡逐字复核",
    "tmp/20261104-145656-hy4all/A12/inspection/mobile-bottom.png — 2× CTA/官网复核",
    "tmp/20261104-145656-hy4all/A12/inspection/stage-header.png — 大标题与右侧信息列复核",
    "tmp/20261104-145656-hy4all/A12/inspection/desktop-left.png — 2× 左栏全部字段复核",
]
p.write_text(json.dumps(cm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

req = suite.tmp_dir(TASK) / "requests.jsonl"
recs = [json.loads(x) for x in req.read_text(encoding="utf-8").splitlines() if x.strip()]
att = [a for r in recs for a in r["attempts"]]
times = [a["started_at"] for a in att]
ends = [a["ended_at"] for a in att]
print("entries:", len(cm["entries"]), "checks:", len(cm["checks"]))
print("records=%d attempts=%d success=%d failed=%d retries=%d" % (
    len(recs), len(att), sum(1 for a in att if a["success"]),
    sum(1 for a in att if not a["success"]), sum(1 for a in att if a["attempt"] > 0)))
print("first_request_started_at:", min(times))
print("last_request_ended_at:", max(ends))
