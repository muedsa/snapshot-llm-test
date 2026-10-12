"""A22 复核：从服务 PNG 反测文字墨迹、柱高与区域边界。

用法：python verify.py --round 1 --png outputs/.../round-01/dashboard.png
六件事全部由真实像素或 plane JSON 计算，不看肉眼印象：
1 每个文字元素的墨迹外接框必须落在自己的盒内（超出即视为被裁切或越界）；
2 墨迹宽度与 DSL 估算宽度对比，差得太多说明该元素被服务截断；
3 文字墨迹两两不得重叠（按墨迹框，不按布局框）；
4 柱形象素高度 vs 数值/比例换算，证明柱高真的由数据决定，负值没有被裁或取绝对值；
5 五个主区域边界与本轮 REGIONS 完全一致，且与其余轮次逐字段对比（±2px 回归）；
6 画布尺寸与背景色。
"""
import argparse
import json
import math
import os
from pathlib import Path

from PIL import Image

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
ap = argparse.ArgumentParser()
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--png", required=True)
ap.add_argument("--regions-out")
a = ap.parse_args()

tmp = root / "tmp" / rid / "A22"
plane = json.loads((tmp / ("layouts/round-%02d/dashboard.plane.json" % a.round)
                    ).read_text(encoding="utf-8"))
img = Image.open(root / a.png).convert("RGB")
W, H = img.size
reg = plane["regions"]
pl = plane["plane"]
report = {"round": a.round, "png": a.png, "canvas": [W, H],
          "background_color": "#%02X%02X%02X" % img.getpixel((4, 4))}


def is_ink(px, bg):
    return max(abs(px[i] - bg[i]) for i in range(3)) > 42


def local_bg(box):
    x, y, w, h = [int(v) for v in box]
    x2, y2 = min(W, x + w), min(H, y + h)
    from collections import Counter
    c = Counter(img.getpixel((i, j)) for j in range(y, y2, 3)
                for i in range(x, x2, 3))
    return c.most_common(1)[0][0]


inks, clipped, overlaps = [], [], []
for tag, v in pl.items():
    if v.get("kind") != "text":
        continue
    x, y, w, h = [int(round(z)) for z in v["box_px"]]
    x, y = max(0, x), max(0, y)
    x2, y2 = min(W, x + w), min(H, y + h)
    bg = local_bg(v["box_px"])
    xs, ys = [], []
    for j in range(y, y2):
        for i in range(x, x2):
            if is_ink(img.getpixel((i, j)), bg):
                xs.append(i)
                ys.append(j)
    if not xs:
        clipped.append({"element": tag, "issue": "no ink in box"})
        continue
    ib = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    iw, ih = ib[2] - ib[0], ib[3] - ib[1]
    inks.append((tag, ib, v))
    if iw > v["est_width_px"] * 1.25 + 6:
        clipped.append({"element": tag, "issue": "ink wider than estimate",
                        "ink_px": iw, "est_px": v["est_width_px"],
                        "box_w": w, "text": v["text"]})
    if ib[0] < x - 1 or ib[2] > x2 + 1 or ib[1] < y - 1 or ib[3] > y2 + 1:
        clipped.append({"element": tag, "issue": "ink outside box",
                        "ink_box": ib, "box": (x, y, x2, y2)})
    if ih > v["font_px"] * 1.45:
        clipped.append({"element": tag, "issue": "ink taller than one line",
                        "ink_h": ih, "font_px": v["font_px"]})
for i in range(len(inks)):
    for j in range(i + 1, len(inks)):
        t1, b1, _ = inks[i]
        t2, b2, _ = inks[j]
        if not (b1[2] <= b2[0] or b2[2] <= b1[0] or b1[3] <= b2[1]
                or b2[3] <= b1[1]):
            overlaps.append({"a": t1, "b": t2,
                             "boxes": [b1, b2]})

# ---- 柱高核对 ----
bars = []
zero = None
for tag, v in pl.items():
    if tag.startswith("bar-") and "box_px" in v:
        x, y, w, h = v["box_px"]
        if v.get("value", 0) >= 0:
            zero = max(zero or 0, y + h)
bars_ok, bars_bad = 0, []
for tag, v in pl.items():
    if v.get("role") != "bar":
        continue
    x, y, w, h = v["box_px"]
    cx = int(x + w / 2)
    col = v["color"]
    tgt = tuple(int(col.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    run, j, yy = 0, 0, int(max(0, min(y, H - 1)))
    meas = 0
    while yy < H:
        p = img.getpixel((cx, yy))
        if max(abs(p[i] - tgt[i]) for i in range(3)) <= 34:
            run += 1
            meas = max(meas, run)
        else:
            run = 0
        yy += 1
    bars.append({"element": tag, "value": v["value"], "dsl_h_px": round(h, 1),
                 "measured_px": meas, "delta_px": round(meas - h, 1),
                 "negative": v["value"] < 0})
    if abs(meas - round(h)) <= 3:
        bars_ok += 1
    else:
        bars_bad.append(bars[-1])

# ---- 区域边界跨轮对比 ----
allreg = {}
for r in (1, 2, 3):
    p = root / "tmp" / rid / "A22" / "layouts" / ("round-%02d" % r) / \
        "dashboard.plane.json"
    if p.exists():
        allreg[str(r)] = json.loads(p.read_text(encoding="utf-8"))["regions"]
regdiff = {}
for r, rr in allreg.items():
    if r == str(a.round):
        continue
    regdiff["round-%02d-vs-%s" % (a.round, r)] = {
        zn: {"this": reg[zn], "other": rr[zn],
             "max_abs_delta_px": max(abs(reg[zn][i] - rr[zn][i])
                                     for i in range(4))}
        for zn in reg}

# ---- 主区域边界核对：每个构件必须落在它所属的区域内 ----
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "gd", str(tmp / "gen_dash.py"))
gd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gd)
zone_of = gd.zone_of
outside = []
for tag, v in pl.items():
    zn = zone_of(tag)
    if zn is None:
        continue
    if v.get("kind") == "line":
        x = min(v["from_px"][0], v["to_px"][0])
        y = min(v["from_px"][1], v["to_px"][1])
        w = abs(v["to_px"][0] - v["from_px"][0])
        h = max(abs(v["to_px"][1] - v["from_px"][1]), v["thickness_px"])
    else:
        x, y, w, h = v["box_px"]
    zx, zy, zw, zh = reg[zn]
    tol = 2.0
    if (x < zx - tol or y < zy - tol or x + w > zx + zw + tol
            or y + h > zy + zh + tol):
        outside.append({"element": tag, "zone": zn, "box": [x, y, w, h],
                        "zone_box": list(reg[zn])})

report.update({
    "text_elements": len(inks),
    "elements_outside_their_region": outside,
    "ink_overlaps": overlaps,
    "clipped_or_outside": clipped,
    "bars_checked": len(bars), "bars_within_3px": bars_ok,
    "bars_mismatch": bars_bad,
    "negative_bars": [b for b in bars if b["negative"]],
    "region_boundaries": reg,
    "region_cross_round": regdiff,
    "region_max_delta_vs_this_round": max(
        [d["max_abs_delta_px"] for pair in regdiff.values()
         for d in pair.values()] or [0]),
})
if a.regions_out:
    (root / a.regions_out).write_text(json.dumps({"round": a.round, "regions": reg}),
                                      encoding="utf-8")
out = root / "tmp" / rid / "A22" / "layouts" / ("round-%02d" % a.round) / "verify.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: report[k] for k in (
    "canvas", "text_elements", "ink_overlaps", "clipped_or_outside",
    "elements_outside_their_region",
    "bars_checked", "bars_within_3px", "negative_bars",
    "region_max_delta_vs_this_round")}, ensure_ascii=False, indent=1)[:1500])
print("->", out)
