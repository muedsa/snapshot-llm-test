"""A20 · 24-marker dense annotation with near labels + 6 routed center labels."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A20"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, H = 1600, 1100
BG = "#F7F4EC"
INK = "#152437"
MUTED = "#5B6B7C"
LINE = "#D9D2C2"
MAP = [280, 160, 1320, 920]
FONT = "Inter,Noto Sans CJK SC"
BW, BH = 126, 30
CENTER = {"M06", "M08", "M09", "M10", "M11", "M12"}


def load():
    return json.loads((ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json").read_text(encoding="utf-8"))


def px(m):
    return 280 + 10.4 * m["x"], 920 - 7.6 * m["y"]


def rect_dist(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2])
    dy = max(r[1] - p[1], 0, p[1] - r[3])
    return math.hypot(dx, dy)


def rect_overlap(a, b, gap=4):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def cand_boxes(p):
    x, y = p
    out = []
    for dx, dy in [(16, -BH / 2), (-16 - BW, -BH / 2), (-BW / 2, -16 - BH), (-BW / 2, 16),
                   (12, 12), (12, -BH - 12), (-BW - 12, 12), (-BW - 12, -BH - 12)]:
        out.append([x + dx, y + dy, x + dx + BW, y + dy + BH])
    return out


def boxes_hit_point(box, points, own=None):
    for mid, p in points.items():
        if mid == own:
            # own point must not be covered by its own box either
            pass
        if rect_dist(p, box) < 8:  # radius 6/4 + safety
            return True
    return False


def solve(markers):
    pts = {m["id"]: px(m) for m in markers}
    # reserved center boxes
    left = {m: [360, y, 360 + BW, y + BH] for m, y in zip(["M06", "M08", "M09"], [420, 470, 520])}
    right = {m: [1108, y, 1108 + BW, y + BH] for m, y in zip(["M10", "M11", "M12"], [560, 610, 660])}
    reserved = list(left.values()) + list(right.values())
    labels = dict(left); labels.update(right)
    outer = [m for m in markers if m["id"] not in CENTER]
    # order outer by fewest valid candidates / closeness to center
    best = None

    def rec(i, cur):
        nonlocal best
        if i == len(outer):
            best = dict(cur); return True
        m = outer[i]; p = pts[m["id"]]
        for b in cand_boxes(p):
            if b[0] < 20 or b[1] < 140 or b[2] > W - 20 or b[3] > H - 30:
                continue
            if boxes_hit_point(b, pts, m["id"]):
                continue
            if any(rect_overlap(b, r, 4) for r in reserved):
                continue
            if any(rect_overlap(b, r, 4) for r in cur.values()):
                continue
            cur[m["id"]] = b
            if rec(i + 1, cur):
                return True
            cur.pop(m["id"], None)
        return False

    # heuristic: sort by y then x
    outer.sort(key=lambda m: (pts[m["id"]][1], pts[m["id"]][0]))
    if not rec(0, {}):
        raise RuntimeError("no near-label packing")
    labels.update(best)
    return labels, left, right


def main() -> int:
    markers = load()
    labels, left, right = solve(markers)
    pts = {m["id"]: px(m) for m in markers}
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color=BG)),
             Pos(48, 44, T("索引分布 / 24 点", size=30, color=INK, weight="BOLD", family=FONT)),
             Pos(48, 84, T("坐标 0–100 · 指数 · 原点左下", size=20, color=MUTED, family=FONT)),
             Pos(280, 160, C(width=1040, height=760, color="#FBF9F3", border="1 SOLID #C9C0AE"))]
    # grid / axes
    for i in range(0, 101, 10):
        x = 280 + 10.4 * i
        y = 920 - 7.6 * i
        nodes.append(Pos(x, 160, C(width=1, height=760, color="#E7E1D4")))
        nodes.append(Pos(280, y, C(width=1040, height=1, color="#E7E1D4")))
        nodes.append(Pos(x - 12, 926, C(width=24, height=1, color="#8C8170")))
        nodes.append(Pos(x - 18, 940, T(str(i), size=16, color=MUTED, family=FONT)))
        nodes.append(Pos(250, y - 10, C(width=6, height=1, color="#8C8170")))
        nodes.append(Pos(216, y - 10, T(str(i), size=16, color=MUTED, family=FONT)))
    nodes += [Pos(1360, 900, T("x", size=20, color=MUTED, weight="BOLD", family=FONT)),
              Pos(250, 128, T("y", size=20, color=MUTED, weight="BOLD", family=FONT)),
              Pos(1360, 950, T("指数", size=18, color=MUTED, family=FONT))]
    # leader lines for center labels (drawn before labels/points)
    lines = {}
    for m in markers:
        mid = m["id"]
        if mid not in CENTER:
            continue
        p = pts[mid]; b = labels[mid]
        # nearest point on box border to p
        bx = min(max(p[0], b[0]), b[2]); by = min(max(p[1], b[1]), b[3])
        # choose point on border toward p
        if p[0] < b[0]: bx = b[0]
        elif p[0] > b[2]: bx = b[2]
        if p[1] < b[1]: by = b[1]
        elif p[1] > b[3]: by = b[3]
        dx, dy = bx - p[0], by - p[1]
        d = math.hypot(dx, dy)
        sx, sy = p[0] + dx / d * 6, p[1] + dy / d * 6
        lines[mid] = [(sx, sy), (bx, by)]
        mx, my = (sx + bx) / 2, (sy + by) / 2
        ln = math.hypot(bx - sx, by - sy); ang = math.atan2(by - sy, bx - sx)
        c, s = math.cos(ang), math.sin(ang)
        mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
        nodes.append(Pos(mx - ln / 2, my - 0.75,
                         f'<Transform matrix="{mat}" alignment="CENTER">' +
                         C(width=f"{ln:.2f}", height="1.5", color="#64748B", borderRadius="1") + "</Transform>"))
    # points
    top3 = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]
    topids = {m["id"] for m in top3}
    for m in markers:
        x, y = pts[m["id"]]
        if m["id"] in topids:
            nodes.append(Pos(x - 15, y - 15, C(width=30, height=30, color="transparent", border="2 SOLID #B45309", borderRadius=15)))
        nodes.append(Pos(x - 6, y - 6, C(width=12, height=12, color="#1D4ED8", borderRadius=6)))
    # labels
    for m in markers:
        b = labels[m["id"]]; mid = m["id"]
        color = "#B45309" if mid in topids else "#17253A"
        border = "#B45309" if mid in topids else "#CFC6B4"
        nodes.append(Pos(b[0], b[1], C(width=BW, height=BH, color="#FFFDF7", border=f"1 SOLID {border}", borderRadius=6)))
        nodes.append(Pos(b[0] + 6, b[1] + 5, T(f'{mid} {m["name"]} {m["value"]}', size=20, color=color, family=FONT)))
    dsl = f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    (TMP / "dsl" / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    # save placement for audit
    (TMP / "layout-raw.json").write_text(json.dumps({"labels": labels, "points": pts, "top3": [m["id"] for m in top3]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A20", VERSION, "labels", len(labels), "top3", [m["id"] for m in top3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
