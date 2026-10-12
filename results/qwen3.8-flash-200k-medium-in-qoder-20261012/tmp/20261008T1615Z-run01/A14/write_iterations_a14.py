"""A14 iterations.jsonl — one record per version/view, anchored to a real request id.

v01 was overwritten in place by v02 at the deliverable path, so the superseded version is
archived under preview/v01/ from the raw response bytes render.py kept; the image_path of a
v01 record points there, not at the current file.
"""
import json
import os
import shutil
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A14"
REQS = [json.loads(l) for l in (TEMP / "requests.jsonl").read_text(encoding="utf-8")
        .splitlines() if l.strip()]
BY_VER = {r["dsl_version"]: r for r in REQS}
PRE = TEMP / "preview" / "v01"
PRE.mkdir(parents=True, exist_ok=True)
for r in REQS:
    if r["dsl_version"].startswith("v01-"):
        cid = r["dsl_version"].split("-")[1]
        dst = PRE / f"card-{cid}.png"
        if not dst.exists():
            shutil.copyfile(ROOT / r["raw_copy_file"], dst)

OUT = TEMP / "iterations.jsonl"
done = set()
if OUT.exists():
    done = {json.loads(l)["iteration_id"] for l in
            OUT.read_text(encoding="utf-8").splitlines() if l.strip()}

# actual image views in this session, taken from the tool-call clock
VIEWS = {
    ("v01", "K01"): "2026-10-09T01:30:18+00:00", ("v01", "K04"): "2026-10-09T01:30:18+00:00",
    ("v01", "K06"): "2026-10-09T01:30:40+00:00", ("v01", "K08"): "2026-10-09T01:30:40+00:00",
    ("v01", "K02"): "2026-10-09T01:31:11+00:00", ("v01", "K07"): "2026-10-09T01:31:11+00:00",
    ("v02", "K02"): "2026-10-09T01:32:42+00:00", ("v02", "K03"): "2026-10-09T01:32:42+00:00",
    ("v02", "K05"): "2026-10-09T01:32:49+00:00", ("v02", "K08"): "2026-10-09T01:32:49+00:00",
    ("v02", "K01"): "2026-10-09T01:32:55+00:00", ("v02", "K04"): "2026-10-09T01:32:55+00:00",
    ("v02", "K06"): "2026-10-09T01:33:03+00:00", ("v02", "K07"): "2026-10-09T01:33:03+00:00",
}
PROBLEMS = {
    "v01": ("标题盒按估算行数留了高度，实际渲染行数更少：K01/K02/K08 标题与讲者之间出现 100-130px "
            "空洞（像素核对：K02 计划 2 行、实渲 1 行；K08 计划 3 行、实渲 2 行）"),
    "v02": "无：八张标题行数与计划一致，未越界、未裁切，安全边距内只有背景色",
}
CHANGES = {
    "v01": "首版：grid A/B 参数化规则、状态色+符号+文字三重编码、pick_size 高度预算、"
           "标题/讲者块垂直居中",
    "v02": "新增 A14 本地 Fit 子类（CJK 1.00em、去掉 0.96 冗余 slack、拉丁粗体 0.60em），"
           "标题盒改 CENTER_LEFT 对齐；grid 触发条件由字号兜底改为 36pt 下限实际行数",
}


def add(iid, version, parent, itype, req_part, problems, changes, result, completed,
        cid, viewed=True, vat=None, img=None):
    if iid in done:
        return
    r = BY_VER[f"{version}-{cid}"]
    rec = {"iteration_id": iid, "task_id": "A14", "version_id": f"{version}-{cid}",
           "parent_version": parent, "type": itype,
           "requirement_part": req_part,
           "image_path": img or (str((ROOT / r["response_file"]).relative_to(ROOT))
                                 if viewed and version == "v02" else
                                 (f"tmp/{RID}/A14/preview/v01/card-{cid}.png"
                                  if version == "v01" else None)),
           "image_viewed_at": (vat or r["ended_at"]) if viewed else None,
           "viewed": viewed,
           "observed_problems": problems, "changes": changes,
           "result": result, "completed": completed,
           "request_id": r["request_id"], "path_base": "suite_root"}
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


for cid in ["K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08"]:
    viewed = ("v01", cid) in VIEWS
    add(f"A14-baseline-{cid}", "v01", None, "baseline",
        "八张 1200×630 卡片、统一主色/日期/品牌/状态体系、标题≥36pt≤3行、边距40",
        "初次生成即渲染，随后查看" if viewed else
        "初次生成即渲染；v01 未逐张查看就被 v02 取代（只查看了 6 张）",
        CHANGES["v01"], "已渲染" if viewed else "已渲染，未单独查看", viewed,
        cid, viewed=viewed, vat=VIEWS.get(("v01", cid)))
    if viewed:
        add(f"A14-visual-{cid}", "v02", f"A14-baseline-{cid}", "visual",
            "标题区域排版不得因整图缩小；行数须与盒高一致",
            PROBLEMS["v01"], CHANGES["v02"],
            f"查看 v02：{PROBLEMS['v02']}", True, cid, vat=VIEWS[("v02", cid)])
    else:
        add(f"A14-baseline-{cid}-v02", "v02", f"A14-baseline-{cid}", "baseline",
            "首次真实查看发生在 v02", "未见 v01，v02 为本题该卡的首次视觉基线",
            CHANGES["v02"], f"查看 v02：{PROBLEMS['v02']}", False, cid,
            vat=VIEWS[("v02", cid)])
print(OUT.read_text(encoding="utf-8").count("\n"), "records")
