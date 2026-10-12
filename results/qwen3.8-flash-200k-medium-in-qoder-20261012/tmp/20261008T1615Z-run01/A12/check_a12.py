"""A12 independent check: reads only the delivered PNGs, the delivered .snapshot bodies,
inputs/content.json and content-map.json. No pixel position is hardcoded here — every box
comes from content-map.json, which the layout engine wrote from the boxes it emitted, so a
layout that drifted would show up as a mismatch rather than being agreed with.

Checks: canvas size, byte provenance (PNG == raw service response, delivered DSL == the DSL
that was sent), verbatim retention of all 19 input strings on all four canvases, no raster or
external asset, type floors, safe margins, pairwise text-box overlap, and per-box ink evidence
(text really painted, and not flush against the right/bottom edge of its own box, which is
what a clipped run looks like when the renderer truncates instead of adding an ellipsis).
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "A12"
TEMP = ROOT / "tmp" / RID / "A12"
SRC = ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json"
BP = ["mobile", "tablet", "desktop", "stage"]
BODY_ROLES = ("meta", "body", "card_detail", "card_title", "cta", "website",
              "meta_label", "index", "kicker", "subtitle")

content = json.loads(SRC.read_text(encoding="utf-8"))
cmap = json.loads((TEMP / "content-map.json").read_text(encoding="utf-8"))

# every string that must survive verbatim, with how often it must appear per canvas
REQUIRED = [content["title"], content["subtitle"], content["date"], content["time"],
            content["location"], content["cta"], content["website"]]
for c in content["cards"]:
    REQUIRED += [c["title"], c["detail"]]

res = {"schema_version": 1, "path_base": "suite_root", "task_id": "A12", "run_id": RID,
       "checked_from": {"outputs": "outputs/%s/A12" % RID,
                        "content_map": "tmp/%s/A12/content-map.json" % RID,
                        "source_content": "tasks/A12-responsive-system/inputs/content.json"},
       "canvases": {}, "failures": []}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def add(bpc, tag, ok, detail=""):
    if not ok:
        res["failures"].append(f"{bpc}: {tag} {detail}")
    res["canvases"][bpc]["checks"].append({"tag": tag, "ok": bool(ok), "detail": detail})


for bp in BP:
    png, dsl_path = OUT / f"{bp}.png", OUT / f"{bp}.snapshot"
    fields = cmap["fields"][bp]
    b = cmap["canvases"][bp]
    W, H = b["size"]
    M = b["safe_margin"]
    entry = {"png": f"outputs/{RID}/A12/{bp}.png", "dsl": f"{bp}.snapshot",
             "png_bytes": png.stat().st_size, "dsl_bytes": dsl_path.stat().st_size,
             "checks": []}
    res["canvases"][bp] = entry
    dsl = dsl_path.read_text(encoding="utf-8")

    # ---- provenance -------------------------------------------------------------
    # newest final render of this canvas (the delivery directory keeps every attempt)
    raw = sorted((OUT / "requests").glob(f"A12-final*-{bp}-*.response.bin"),
                 key=lambda p: p.stat().st_mtime)
    img = Image.open(png).convert("RGBA")
    add(bp, "canvas_size", img.size == (W, H), f"actual {img.size}, required {(W, H)}")
    add(bp, "png_is_raw_service_response",
        bool(raw) and sha(raw[-1]) == sha(png), str([p.name for p in raw]))
    entry["served_by"] = raw[-1].name.replace(".response.bin", "") if raw else None
    add(bp, "dsl_matches_generated_body", sha(dsl_path) == sha(TEMP / f"{bp}.snapshot"))
    add(bp, "no_raster_or_external_asset",
        "<Image" not in dsl and "http" not in dsl.lower() and "base64" not in dsl.lower())
    add(bp, "dsl_is_self_closed", dsl.startswith("<Snapshot") and dsl.endswith("</Snapshot>"))

    # ---- verbatim retention -----------------------------------------------------
    payloads = re.findall(r"<Text\b[^>]*>(.*?)</Text>", dsl, re.S)
    joined = "".join(payloads)
    missing = [s for s in REQUIRED if s not in joined]
    add(bp, "all_input_strings_verbatim", not missing, "missing " + repr(missing))
    counts = {}
    for s in REQUIRED:
        counts[s] = joined.count(s)
    dupes = {s: c for s, c in counts.items() if c != 1}
    add(bp, "each_input_string_appears_once", not dupes, repr(dupes))
    in_fields = [f for f, r in fields.items() if r["provenance"] == "input"]
    add(bp, "content_map_input_fields_recorded", len(in_fields) == len(REQUIRED),
        f"recorded {len(in_fields)} of {len(REQUIRED)} input fields")
    add(bp, "content_map_text_equals_source",
        all(r["text"] in REQUIRED or r["provenance"] == "derived"
            for r in fields.values()))

    # ---- floors / margins / overlap --------------------------------------------
    fl = cmap["layout_report"][bp]["floors"]
    under = [f for f, r in fields.items()
             if (r["role"] == "card_title" and r["font_pt"] < fl.get("cardTitle", 0))
             or (r["role"] in BODY_ROLES and r["font_pt"] < fl["body"])
             or (r["role"] == "title" and r["font_pt"] < fl.get("title", 0))]
    add(bp, "type_floors", not under, repr(under))
    add(bp, "min_font_pt_at_least_floor",
        min(r["font_pt"] for r in fields.values()) >= fl["body"],
        str(min(r["font_pt"] for r in fields.values())))
    outside = [f for f, r in fields.items()
               if r["box"][0] < M - 0.5 or r["box"][1] < M - 0.5
               or r["box"][0] + r["box"][2] > W - M + 0.5
               or r["box"][1] + r["box"][3] > H - M + 0.5]
    add(bp, "safe_margin", not outside, repr(outside))
    boxes = [(f, r["box"]) for f, r in fields.items()]
    ov = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (f1, (a1, b1, w1, h1)), (f2, (a2, b2, w2, h2)) = boxes[i], boxes[j]
            ox = min(a1 + w1, a2 + w2) - max(a1, a2)
            oy = min(b1 + h1, b2 + h2) - max(b1, b2)
            if ox > 0.5 and oy > 0.5:
                ov.append(f"{f1}x{f2}")
    add(bp, "no_text_box_overlap", not ov, repr(ov))

    # ---- pixel evidence ---------------------------------------------------------
    px = img.load()
    flush, blank, clipped = [], [], []
    ink_min = []
    for f, r in fields.items():
        x, y, w, h = [int(round(v)) for v in r["box"]]
        x2, y2 = min(x + w, W), min(y + h, H)
        corners = [px[x + 1, y + 1], px[x2 - 2, y + 1], px[x + 1, y2 - 2], px[x2 - 2, y2 - 2]]
        bg = corners[0]
        n_ink, right, bottom = 0, 0, 0
        for yy in range(y, y2):
            for xx in range(x, x2):
                p = px[xx, yy]
                if max(abs(p[k] - bg[k]) for k in range(3)) > 28:
                    n_ink += 1
                    if xx >= x2 - 1:
                        right += 1
                    if yy >= y2 - 1:
                        bottom += 1
        if n_ink < 20:
            blank.append(f)
        if right > 0 or bottom > 0:
            flush.append(f"{f}:{right}/{bottom}")
        ink_min.append(n_ink)
    add(bp, "every_text_box_has_ink", not blank, repr(blank))
    add(bp, "no_glyph_flush_with_box_edge", not flush, repr(flush))
    entry["ink_pixels_min"] = min(ink_min)
    entry["text_boxes"] = len(fields)
    entry["layout"] = cmap["layout_report"][bp]["layout"]
    entry["sha256_png"] = sha(png)[:16]
    entry["sha256_dsl"] = sha(dsl_path)[:16]

res["summary"] = {
    "canvases": len(BP),
    "total_checks": sum(len(v["checks"]) for v in res["canvases"].values()),
    "passed": sum(1 for v in res["canvases"].values() for c in v["checks"] if c["ok"]),
    "required_strings": len(REQUIRED),
    "failures": res["failures"],
}
(TEMP / "check-report.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(res["summary"], ensure_ascii=False, indent=1))
for bp in BP:
    bad = [c["tag"] for c in res["canvases"][bp]["checks"] if not c["ok"]]
    print(bp, "OK" if not bad else "FAIL " + repr(bad))
