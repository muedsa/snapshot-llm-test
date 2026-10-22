# -*- coding: utf-8 -*-
"""Geometric overlap analysis: for each unit, which LATER-drawn unit covers
its center, and what visible fraction remains (approx, from disk/rect math).
Identifies occlusion pairs the pixel-check flagged."""
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a23_common as C  # noqa: E402


def rect_corners(cx, cy, w, h, rot):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2),
                   (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return pts


def poly_contains(pts, px, py):
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xin = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xin:
                inside = not inside
    return inside


for k in range(6):
    st = C.frame_state(k)
    order = [u["id"] for u in C.UNITS]  # draw order U01..U12
    print("=== F%d ===" % (k + 1))
    for i, u in enumerate(C.UNITS):
        cx, cy, rot = st[u["id"]]
        # sample unit area, count how much is covered by later-drawn units
        tot, vis = 0, 0
        if u["shape"] == "circle":
            r = u["w"] / 2.0
            step = max(1.0, r / 8)
            y = -r + step / 2
            while y < r:
                x = -r + step / 2
                while x < r:
                    if x * x + y * y <= r * r:
                        tot += 1
                        px, py = cx + x, cy + y
                        covered = False
                        for u2 in C.UNITS[i + 1:]:
                            c2x, c2y, r2 = st[u2["id"]]
                            if u2["shape"] == "circle":
                                rr = u2["w"] / 2.0
                                if (px - c2x) ** 2 + (py - c2y) ** 2 <= rr ** 2:
                                    covered = True
                                    break
                            else:
                                pts = rect_corners(c2x, c2y, u2["w"], u2["h"],
                                                   r2)
                                if poly_contains(pts, px, py):
                                    covered = True
                                    break
                        if not covered:
                            vis += 1
                    x += step
                y += step
        else:
            step = 4.0
            y = -u["h"] / 2 + step / 2
            while y < u["h"] / 2:
                x = -u["w"] / 2 + step / 2
                while x < u["w"] / 2:
                    tot += 1
                    px, py = cx + x, cy + y
                    covered = False
                    for u2 in C.UNITS[i + 1:]:
                        c2x, c2y, r2 = st[u2["id"]]
                        if u2["shape"] == "circle":
                            rr = u2["w"] / 2.0
                            if (px - c2x) ** 2 + (py - c2y) ** 2 <= rr ** 2:
                                covered = True
                                break
                        else:
                            pts = rect_corners(c2x, c2y, u2["w"], u2["h"], r2)
                            if poly_contains(pts, px, py):
                                covered = True
                                break
                    if not covered:
                        vis += 1
                    x += step
                y += step
        frac = vis / float(tot) if tot else 1.0
        if frac < 0.9:
            # find top coverer at center
            cxs, cys = cx, cy
            coverers = []
            for u2 in C.UNITS[i + 1:]:
                c2x, c2y, r2 = st[u2["id"]]
                if u2["shape"] == "circle":
                    rr = u2["w"] / 2.0
                    if math.hypot(cxs - c2x, cys - c2y) <= rr:
                        coverers.append(u2["id"])
                else:
                    pts = rect_corners(c2x, c2y, u2["w"], u2["h"], r2)
                    if poly_contains(pts, cxs, cys):
                        coverers.append(u2["id"])
            print("  %s frac=%.2f covered-by=%s" % (u["id"], frac, coverers))
