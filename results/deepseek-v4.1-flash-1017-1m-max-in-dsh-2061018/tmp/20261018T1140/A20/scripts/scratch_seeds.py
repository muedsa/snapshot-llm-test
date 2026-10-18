"""Scratch checker for the hand-designed A20 label layout seeds."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_lib as G  # noqa: E402

SEEDS = {
    "M01": (344, 286), "M02": (470, 324), "M03": (539, 262), "M04": (494, 419),
    "M05": (620, 368), "M06": (548, 455), "M07": (726, 320), "M08": (627, 512),
    "M09": (678, 477), "M10": (847, 506), "M11": (868, 545), "M12": (648, 566),
    "M13": (899, 411), "M14": (408, 563), "M15": (476, 639), "M16": (606, 721),
    "M17": (712, 757), "M18": (972, 582), "M19": (1003, 647), "M20": (996, 472),
    "M21": (1190, 335), "M22": (1118, 707), "M23": (872, 791), "M24": (394, 768),
}


def main() -> int:
    markers = G.load_markers()
    metrics = G.load_metrics()
    boxes = {}
    sizes = {}
    for m in markers:
        w, h = G.label_size(m["id"], metrics)
        sizes[m["id"]] = (w, h)
        boxes[m["id"]] = G.box(w, h, *SEEDS[m["id"]])
    pts = {m["id"]: G.anchor(m) for m in markers}
    print("sizes:", {k: round(v[0], 1) for k, v in sizes.items()})
    bad = 0
    print("\n-- box/box pairs (need >=4)")
    ids = list(boxes)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            d = G.rect_dist(boxes[ids[i]], boxes[ids[j]])
            if d < 4 - 1e-9:
                bad += 1
                print(f"  {ids[i]}-{ids[j]}: {d:.2f}")
    print("bad pairs:", bad)
    print("\n-- box/point (need > radius 6)")
    for mid in ids:
        for m in markers:
            d = G.anchor_rect_dist(pts[m["id"]], boxes[mid])
            if d <= 6 + 1e-9:
                print(f"  box {mid} vs point {m['id']}: {d:.2f} (own={mid == m['id']})")
    print("\n-- distances anchor->own box")
    leaders = []
    for m in markers:
        d = G.anchor_rect_dist(pts[m["id"]], boxes[m["id"]])
        print(f"  {m['id']}: {d:.3f} {'LEADER' if d > 24 else ''}")
        if d > 24:
            leaders.append(m["id"])
    print("leaders:", leaders)
    print("\n-- bounds")
    for mid, b in boxes.items():
        print(f"  {mid}: [{b[0]:.1f},{b[1]:.1f},{b[2]:.1f},{b[3]:.1f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
