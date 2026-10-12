"""A21：从真实渲染 PNG 反测每个文字元素的墨迹包围盒，再据此复核碰撞。

排版盒可以相碰（上下留白），墨迹不能——这里量的是服务返回图片里的实际像素，
不是 DSL 估算值。用法：
  python tmp/<run_id>/A21/ink_audit.py --round 2 \
      --png launch-portrait=tmp/.../r02-portrait-v02.png \
      --png launch-wide=tmp/.../r02-wide-v01.png
"""
import argparse
import json
import os
from pathlib import Path

from PIL import Image

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "A21"

ap = argparse.ArgumentParser()
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--png", action="append", default=[], help="name=path 的服务原始 PNG")
a = ap.parse_args()

LAY = TMP / "layouts" if a.round == 1 else TMP / "layouts" / ("round-%02d" % a.round)
TH = 60                    # 深色主题：只看亮像素（半透明叠光板最大通道 < 60）
TH_LIGHT = 100             # 浅色主题：与背景通道差 > 100 才算墨迹（板组最高约 64）


def base_bg(img):
    from collections import Counter
    data = list(img.convert("RGB").getdata())[::4]
    return Counter(data).most_common(1)[0][0]


def ink_test(bg):
    """返回 (判断函数, 说明)：深色底找亮像素，浅色底找比背景暗得多的像素。"""
    if max(bg) < 128:
        return (lambda px: max(px) > TH), "max_channel > %d" % TH
    return (lambda px: max(abs(px[0] - bg[0]), abs(px[1] - bg[1]),
                           abs(px[2] - bg[2])) > TH_LIGHT), "channel_delta_vs_bg > %d" % TH_LIGHT


def ink_box(img, box, is_ink):
    x, y, w, h = [int(v) for v in box]
    crop = img.crop((x, y, x + w, y + h)).convert("RGB")
    px = crop.load()
    pts = [(i, j) for j in range(crop.height) for i in range(crop.width)
           if is_ink(px[i, j])]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [x + min(xs), y + min(ys), x + max(xs) + 1, y + max(ys) + 1]


def overlap(pa, pb):
    ox = min(pa[2], pb[2]) - max(pa[0], pb[0])
    oy = min(pa[3], pb[3]) - max(pa[1], pb[1])
    return (ox, oy) if (ox > 0 and oy > 0) else None


report = {}
for spec in a.png:
    name, path = spec.split("=", 1)
    plane = json.loads((LAY / (name + ".plane.json")).read_text(encoding="utf-8"))
    img = Image.open(root / path if not Path(path).is_absolute() else path)
    BG = base_bg(img)
    is_ink, rule = ink_test(BG)
    texts = {k: v for k, v in plane["plane"].items() if "text" in v}
    inks = {}
    for tag, v in texts.items():
        ib = ink_box(img, v["box_px"], is_ink)
        if ib:
            inks[tag] = ib
    keys = sorted(inks)
    hits = []
    min_gap, min_pair = None, None
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            pa, pb = inks[ka], inks[kb]
            ov = overlap(pa, pb)
            if ov:
                hits.append({"pair": [ka, kb], "ink_overlap_px": list(ov)})
                continue
            xo = min(pa[2], pb[2]) - max(pa[0], pb[0])
            if xo > 0:                      # 水平有交叠 -> 量垂直净距
                gap = max(pa[1], pb[1]) - min(pa[3], pb[3])
                if min_gap is None or gap < min_gap:
                    min_gap, min_pair = gap, [ka, kb]
    # 顶/底扩展带：整条带内不得有任何非背景像素（含装饰，不只是文字）
    zs = plane["extension_zones"]
    band = {}
    for zn, z in zs.items():
        zx, zy, zw, zh = [int(v) for v in z]
        crop = img.crop((zx, zy, zx + zw, zy + zh)).convert("RGB")
        px = crop.load()
        bad = [(i, j) for j in range(crop.height) for i in range(crop.width)
               if any(abs(px[i, j][c] - BG[c]) > 6 for c in range(3))]
        band[zn] = {"rect": [zx, zy, zw, zh], "non_bg_pixels": len(bad),
                    "sample": [[zx + i, zy + j] for i, j in bad[:5]]}
    report[name] = {"png": path, "size": list(img.size),
                    "measured_background": list(BG), "ink_rule": rule,
                    "text_elements": len(texts), "ink_measured": len(inks),
                    "ink_overlaps": hits,
                    "min_vertical_ink_gap_px": min_gap,
                    "min_vertical_ink_gap_pair": min_pair,
                    "extension_bands_from_png": band}
    assert not hits, "%s 墨迹重叠 %s" % (name, hits)
    for zn, b in band.items():
        assert b["non_bg_pixels"] == 0, "%s 扩展带 %s 有 %s 个非背景像素" % (
            name, zn, b["non_bg_pixels"])

out = LAY / "ink-audit.json"
out.write_text(json.dumps({"round": a.round, "basis": "服务返回 PNG 的实际像素",
                           "threshold_max_channel": TH, "images": report},
                          ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in report.items():
    print(k, "墨迹元素", v["ink_measured"], "重叠", len(v["ink_overlaps"]),
          "同列最小墨迹间隙", v["min_vertical_ink_gap_px"], v["min_vertical_ink_gap_pair"],
          "| 扩展带非背景像素", [b["non_bg_pixels"] for b in
                                     v["extension_bands_from_png"].values()])
