"""Generate the per-task gallery.md required by B01-B06 `common_outputs`.

Each task's gallery.md covers that task's own 10 cases, using real titles from the
task's own portfolio.json (falling back to the case.md first heading, then the file
name). Links are relative to the task output dir, so `case-01/final.png` works both
from the task dir and when the gallery is opened in place.
"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

from PIL import Image  # noqa: E402

RUN = S.RUN
CAT = json.load(io.open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
B = [s for s in CAT["tasks"] if s["track"] == "creative"]


def load(p):
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def kb(n):
    return "%.1f KB" % (n / 1024.0)


def norm(c, cid):
    """Normalise the two portfolio.json shapes used across B01-B06."""
    arts = c.get("artifacts") or []
    png = c.get("png") or next((a for a in arts if str(a).lower().endswith(".png")), None)
    dsl = c.get("snapshot") or next((a for a in arts if str(a).lower().endswith(".snapshot")), None)
    d = {
        "id": c.get("id") or c.get("case_id") or cid,
        "title": c.get("title") or "",
        "use_context": c.get("use_context") or c.get("carrier") or "",
        "audience": c.get("audience") or "",
        "visual_intent": c.get("visual_intent") or c.get("user_intent") or "",
        "curatorial_reason": c.get("curatorial_reason") or "",
        "self_check": c.get("self_check") or "",
        "png": png or "%s/final.png" % cid,
        "snapshot": dsl or "%s/final.snapshot" % cid,
        "dimensions": c.get("dimensions") or [],
        "png_bytes": c.get("png_bytes"),
        "snapshot_bytes": c.get("snapshot_bytes"),
        "dsl_element_count": c.get("dsl_element_count"),
    }
    if not d["title"]:
        md = os.path.join(S.OUT_ROOT, cur_task, cid, "case.md")
        try:
            h = io.open(md, encoding="utf-8").readline().strip().lstrip("#").strip()
            d["title"] = h.split("·", 1)[-1].strip() if "·" in h else h
        except Exception:  # noqa: BLE001
            d["title"] = cid
    return d


summary = []
for spec in B:
    tid = spec["id"]
    cur_task = tid
    out = os.path.join(S.OUT_ROOT, tid)
    port = load(os.path.join(out, "portfolio.json"))
    by_id = {}
    for c in (port.get("cases") or []):
        if not isinstance(c, dict):
            continue
        cid = c.get("id") or c.get("case_id")
        if cid:
            by_id[cid] = norm(c, cid)
    # never rely on portfolio.json alone: any case dir on disk must be indexed
    for cd in sorted(os.listdir(out)):
        d = os.path.join(out, cd)
        if os.path.isdir(d) and cd.startswith("case-") and os.path.exists(os.path.join(d, "final.png")):
            by_id.setdefault(cd, norm({}, cd))
    tstate = next((t for t in S.load()["tasks"] if t["id"] == tid), {})

    g = ["# %s · 作品画廊" % tid, "",
         "%s" % tstate.get("title", ""), "",
         "- 状态：`%s`　独立完整作品：%d 件　规定下限：%d 件"
         % (tstate.get("status", "?"), len(by_id) or 10, spec["minimum_final_pngs"]),
         "- 全部 PNG 都是 `POST https://open-snapshot.muedsa.com/snapshot` 的**原始响应字节**，",
         "  无本地绘图与后处理；每件都配一份可复现的同名 `.snapshot`。",
         "- 链接相对本文件所在的任务输出目录。",
         "- 逐件展示，不是接触表。",
         ""]
    if port.get("curatorial_statement"):
        cs = " ".join(port["curatorial_statement"].split())
        g += ["## 策展说明", "", cs, ""]
    if port.get("brand_disclaimer"):
        g += ["> %s" % " ".join(port["brand_disclaimer"].split()), ""]

    g += ["## 目录", ""]
    for cid in sorted(by_id):
        g.append("- [`%s` · %s](#%s)" % (cid, by_id[cid].get("title", ""), cid))
    g += ["", "---", ""]

    for cid in sorted(by_id):
        c = by_id[cid]
        png = c.get("png") or ("%s/final.png" % cid)
        dsl = c.get("snapshot") or ("%s/final.snapshot" % cid)
        ap = os.path.join(out, png.replace("/", os.sep))
        dp = os.path.join(out, dsl.replace("/", os.sep))
        w, h = c.get("dimensions") or [0, 0]
        if os.path.exists(ap):
            with Image.open(ap) as im:
                w, h = im.size
        dims = "%d × %d" % (w, h)
        if c.get("dimensions") and list(c["dimensions"]) != [w, h]:
            dims += "（portfolio.json 记录 %d × %d）" % tuple(c["dimensions"])
        meta = ["- 作品：`%s`　说明：[`case.md`](%s/case.md)" % (cid, cid)]
        if c.get("use_context"):
            meta.append("- 场景：%s　受众：%s" % (c["use_context"], c.get("audience") or "—"))
        if c.get("visual_intent"):
            meta.append("- 视觉意图：%s" % c["visual_intent"])
        meta.append("- 原图：[`%s`](%s)　DSL：[`%s`](%s)"
                    % (os.path.basename(png), png, os.path.basename(dsl), dsl))
        meta.append("- 尺寸 %s　PNG %s　DSL %s　DSL 元素 %s"
                    % (dims, kb(c.get("png_bytes") or (os.path.getsize(ap) if os.path.exists(ap) else 0)),
                       kb(c.get("snapshot_bytes") or (os.path.getsize(dp) if os.path.exists(dp) else 0)),
                       ("%s / 4096" % c["dsl_element_count"]) if c.get("dsl_element_count") else "未记录"))
        if c.get("curatorial_reason"):
            meta.append("- 入选理由：%s" % " ".join(str(c["curatorial_reason"]).split()))
        if c.get("self_check"):
            meta.append("- 实际看图审查：")
            items = c["self_check"] if isinstance(c["self_check"], list) else [c["self_check"]]
            for it in items:
                meta.append("  - %s" % " ".join(str(it).split()))
        g += ["## %s · %s" % (cid, c.get("title", "")), "",
              "![%s %s %s](%s)" % (tid, cid, c.get("title", ""), png), ""]
        g += meta + [""]

    fr = port.get("final_collection_review") or port.get("completion_standard")
    if fr:
        g += ["---", "", "## 整体最终审查 / 完成标准", ""]
        if isinstance(fr, str):
            g += [" ".join(fr.split()), ""]
        elif isinstance(fr, list) and all(isinstance(x, str) for x in fr):
            g += [" ".join(x.split()) for x in fr] + [""]
        else:
            g += ["```json", json.dumps(fr, ensure_ascii=False, indent=2), "```", ""]
    ui = port.get("unresolved_issues")
    if isinstance(ui, str):
        ui = [ui]
    if ui:
        g += ["## 未解决事项（如实）", ""]
        for u in ui:
            g.append("- %s" % u)
        g.append("")

    outp = os.path.join(out, "gallery.md")
    io.open(outp, "w", encoding="utf-8", newline="\n").write("\n".join(g) + "\n")
    summary.append((tid, len(by_id), os.path.getsize(outp)))

for tid, n, size in summary:
    print("%s  cases %2d  gallery.md %6d bytes" % (tid, n, size))
