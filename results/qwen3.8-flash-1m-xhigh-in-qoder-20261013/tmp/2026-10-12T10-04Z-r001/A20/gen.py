"""A20 - render the annotated map from the solved label plan.

Draw order is part of the contract: grid and axes, then leader lines, then the dot
bodies, then the label plates and their text - so no leader or plate can ever cover a
glyph it is supposed to point at.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A20"))

from snap import (  # noqa: E402
    C, Node, Positioned, Snapshot, Stack, Text, num, segment,
)
import layout as L  # noqa: E402

W, H = L.W, L.H
MX, MY, MW, MH = L.MAP_X, L.MAP_Y, L.MAP_W, L.MAP_H
INK, INK2, INK3 = L.INK, L.INK2, L.INK3
BG, PANEL, EDGE = L.BG, L.PANEL, L.EDGE
SANS, MONO = L.SANS, L.MONO
LEAD, HOT = L.LEAD, L.HOT
DOT_FILL = "#1F4FA8"
TOP3 = "#B3261E"
TITLE = "24 个采样点的密集标注：编号 · 名称 · 指数值"


def plate(box, colour=EDGE):
    return Positioned(C(width=num(box[2] - box[0]), height=num(box[3] - box[1]),
                        color=PANEL, borderRadius="6", border=f"1 SOLID {colour}"),
                      left=num(box[0]), top=num(box[1]))


def label_text(it, box):
    return Positioned(Node("Text", {"fontSize": num(L.LABEL_FS), "color": INK,
                                    "fontFamily": MONO, "textAlign": "LEFT"},
                           [], it["text"]),
                      left=num(box[0] + L.PAD), top=num(box[1] + L.PAD - 2))


def axes():
    els = []
    els.append(Positioned(C(width=num(MW), height=num(MH), color=PANEL, borderRadius="10",
                           border=f"2 SOLID {EDGE}"), left=num(MX), top=num(MY)))
    for v in range(0, 101, 20):
        px = MX + 10.4 * v
        py = MY + MH - 7.6 * v
        els.append(Positioned(C(width="1", height=num(MH), color="#EAEFF6"),
                              left=num(px), top=num(MY)))
        els.append(Positioned(C(width=num(MW), height="1", color="#EAEFF6"),
                              left=num(MX), top=num(py)))
        els.append(Positioned(Node("Text", {"fontSize": "20", "color": INK3,
                                            "fontFamily": MONO}, [], str(v)),
                              left=num(px - 16), top=num(MY + MH + 10)))
        els.append(Positioned(Node("Text", {"fontSize": "20", "color": INK3,
                                            "fontFamily": MONO}, [], str(v)),
                              left=num(MX - 52), top=num(py - 11)))
    els.append(Positioned(Node("Text", {"fontSize": "22", "color": INK2,
                                        "fontFamily": SANS}, [],
                             "x 逻辑坐标（0–100，原点左下，向右）"),
                          left=num(MX + 180), top=num(MY + MH + 44)))
    els.append(Positioned(Node("Text", {"fontSize": "22", "color": INK2,
                                        "fontFamily": SANS}, [],
                             "y 逻辑坐标（0–100，向上）"),
                          left="34", top=num(MY - 44)))
    els.append(Positioned(Node("Text", {"fontSize": "22", "color": INK2,
                                        "fontFamily": SANS}, [],
                             "主图区左上 (280,160)，宽 1040、高 760；"
                             "像素锚点 = (280 + 10.4·x, 920 − 7.6·y)"),
                          left=num(MX), top=num(MY + MH + 78)))
    return els


def build(items, placed, top3):
    els = [C(width=num(W), height=num(H), color=BG)]
    els.append(Positioned(Node("Text", {"fontSize": "34", "color": INK,
                                        "fontFamily": SANS, "fontStyle": "BOLD"},
                             [], TITLE), left=num(L.MAP_X - 240), top="46"))
    els.append(Positioned(Node("Text", {"fontSize": "22", "color": INK2,
                                        "fontFamily": SANS},
                             [], "value 单位：指数（无量纲，取值 38–93）"),
                          left=num(L.MAP_X - 240), top="92"))
    body = axes()
    leaders, dots, labels = [], [], []
    for it in sorted(items, key=lambda z: z["id"]):
        pl = placed[it["id"]]
        if pl["poly"]:
            for a, b in L.poly_segments(pl["poly"]):
                leaders.append(segment(a[0], a[1], b[0], b[1], 2, LEAD))
        dot_colour = HOT if it["id"] in top3 else DOT_FILL
        d = it["diameter_px"]
        cx, cy = it["anchor"]
        node = C(width=num(d), height=num(d), color=dot_colour, shape="CIRCLE")
        if it["id"] in top3:
            node = Stack(C(width=num(d + 10), height=num(d + 10), color="#B3261E33",
                           shape="CIRCLE"),
                         C(width=num(d), height=num(d), color=dot_colour,
                           shape="CIRCLE"),
                         alignment="CENTER", clipBehavior="NONE")
        dots.append(Positioned(node, left=num(cx - (d + 10) / 2 if it["id"] in top3
                             else cx - d / 2),
                               top=num(cy - (d + 10) / 2 if it["id"] in top3
                                       else cy - d / 2)))
        labels.append(plate(pl["box"], HOT if it["id"] in top3 else EDGE))
        labels.append(label_text(it, pl["box"]))
    els += body + leaders + dots + labels
    # legend for the three highest values, outside the map on the left
    ly = MY + 16
    els.append(Positioned(Node("Text", {"fontSize": "22", "color": INK,
                                        "fontFamily": SANS, "fontStyle": "BOLD"},
                             [], "value 前三（指数）"), left="34", top=num(ly)))
    for tid in top3:
        it = next(z for z in items if z["id"] == tid)
        ly += 30
        els.append(Positioned(C(width="12", height="12", color=HOT, shape="CIRCLE"),
                              left="36", top=num(ly + 4)))
        els.append(Positioned(Node("Text", {"fontSize": "22", "color": INK2,
                                            "fontFamily": MONO},
                                 [], f"{it['id']} {it['value']}"),
                              left="54", top=num(ly)))
        ly += 26
    els.append(Positioned(Node("Text", {"fontSize": "20", "color": INK3,
                                        "fontFamily": SANS},
                             [], "红圈与红框 = value 前三；密集中心 M08–M12 的圆径缩到 8 px，"
                               "其余点为 12 px；右侧五条引导线连回中心五点。"),
                          left=num(MX), top=num(MY + MH + 106)))
    return Snapshot(Node("Stack", {"alignment": "TOP_LEFT", "clipBehavior": "HARD_EDGE"},
                         [C(width=num(W), height=num(H), color=BG)] + els),
                    background=BG, type="png")


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--forced", default="M08,M09,M10,M11,M12")
ap.add_argument("--shrink", default="M08,M09,M10,M11,M12")
a = ap.parse_args()
markers = L.load_markers()
forced = tuple(x for x in a.forced.split(",") if x)
shrink = {x for x in a.shrink.split(",") if x}
items, placed = L.solve(markers, shrink, forced)
top3 = [m["id"] for m in sorted(markers, key=lambda z: (-z["value"], z["id"]))[:3]]
TMP = ROOT / "tmp" / RUN / "A20"
(TMP / f"{a.ver}-annotated-map.snapshot").write_text(
    build(items, placed, top3).render() + "\n", encoding="utf-8")
polys = {it["id"]: placed[it["id"]]["poly"] for it in items}
data = {
    "coordinate_system": {
        "logical": "x,y in 0..100, origin bottom-left, x right, y up",
        "canvas": "1600x1100, origin top-left, x right, y down, pixels",
        "map_area": {"left_top": [MX, MY], "width": MW, "height": MH,
                     "right_bottom": [MX + MW, MY + MH]},
        "mapping": "pixel anchor = (280 + 10.4 * x, 920 - 7.6 * y)，不取整",
    },
    "top3_by_value": top3,
    "shrunk_dots": sorted(shrink),
    "labels": [{
        "id": it["id"], "name": it["name"], "value": it["value"],
        "logical_xy": it["logical"],
        "anchor_px_unrounded": [it["anchor"][0], it["anchor"][1]],
        "dot_diameter_px": it["diameter_px"],
        "text": it["text"], "font_size": L.LABEL_FS,
        "label_box": placed[it["id"]]["box"],
        "box_text_insets": [L.PAD, L.PAD - 2],
        "anchor_to_box_distance_px": placed[it["id"]]["dist"],
        "leader_required": placed[it["id"]]["dist"] > L.LEADER_LIMIT,
        "leader_polyline": placed[it["id"]]["poly"],
        "slot": placed[it["id"]]["slot"],
    } for it in sorted(items, key=lambda z: z["id"])],
}
(TMP / f"{a.ver}-label-layout.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"top3": top3, "leaders": sum(1 for v in polys.values() if v),
                  "shrunk": sorted(shrink)}, ensure_ascii=False))
