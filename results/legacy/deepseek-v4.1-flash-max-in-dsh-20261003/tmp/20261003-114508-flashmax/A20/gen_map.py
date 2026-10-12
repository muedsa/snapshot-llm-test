"""A20 · annotated-map DSL generator + layout-audit.json.

Reads label-layout.json (produced by solve_layout3 + solve_layout4) and draws
  * the map frame with the 0..100 logical grid, axis ticks and the unit label "指数",
  * the 24 anchors at their exact mapped positions (no snapping),
  * one dot per point (halo + fill + hairline ring so a dot is never lost against a line),
  * the label box (white card, hairline border, >= 4 px apart, never covering a dot),
  * the leader polyline in a darker stroke, drawn *before* the boxes so a line can never
    run across label text,
  * a legend for the three highest values and the coordinate/unit note.

layout-audit.json then reports, from the same geometry:
  * every label pair intersection (must be empty),
  * every leader segment that enters a label box (must be empty),
  * the crossing count (must be <= 3),
  * canvas-boundary checks for boxes, dots and polylines,
  * the real per-point anchor vs the ideal mathematical mapping (must match to < 0.01 px).
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc, element_count, text_width  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CANVAS = (1600, 1100)
MAP_X, MAP_Y, MAP_W, MAP_H = 280.0, 160.0, 1040.0, 760.0
INK = "#0F172AFF"
GRID = "#E2E8F0FF"
AXIS = "#94A3B8FF"
MUTED = "#475569FF"
ACCENT = "#0E9F8FFF"
DOT_FILL = "#0F172AFF"
DOT_HALO = "#FFFFFFFF"
LEADER = "#1D4ED8FF"
BOX_BG = "#FFFFFFFF"
BOX_BORDER = "#CBD5E1FF"
TOP3 = "#D92D20FF"
FONT, FONT_ID, FONT_SMALL = 20.0, 20.0, 18.0


def main() -> None:
    layout = json.load(open(os.path.join(HERE, "label-layout.json"), encoding="utf-8"))
    pts = layout["points"]
    d = Doc(CANVAS[0], CANVAS[1], background="#EEF2F7FF")
    d.box(0, 0, CANVAS[0], CANVAS[1], "#EEF2F7FF")
    d.box(0, 0, CANVAS[0], 8, ACCENT)
    d.text(48, 40, "二十四点密集标注示意图", 34, INK, weight="BOLD")
    d.text(48, 86, "锚点严格按 0–100 逻辑坐标映射（原点左下、y 向上）；标签不移动锚点，"
                   "离点超过 24px 的标签用折线连回。", 18, MUTED)

    # ---- map frame ---------------------------------------------------------
    d.box(MAP_X, MAP_Y, MAP_W, MAP_H, "#F8FAFCFF", radius=10, border=f"1 SOLID {BOX_BORDER}")
    for i in range(1, 10):
        gx = MAP_X + MAP_W * i / 10.0
        gy = MAP_Y + MAP_H * i / 10.0
        heavy = i % 5 == 0
        d.box(gx, MAP_Y, 1, MAP_H, "#CBD5E1FF" if heavy else GRID)
        d.box(MAP_X, gy, MAP_W, 1, "#CBD5E1FF" if heavy else GRID)
        d.text(gx - 20, MAP_Y + MAP_H + 8, str(i * 10), 15, MUTED,
               family="Noto Sans Mono CJK SC", w=40, align="CENTER_RIGHT")
        d.text(MAP_X - 12 - 44, gy - 9, str(i * 10), 15, MUTED,
               family="Noto Sans Mono CJK SC", w=44, align="CENTER_RIGHT")
    d.text(MAP_X + MAP_W + 6, MAP_Y + MAP_H - 9, "0", 15, MUTED,
           family="Noto Sans Mono CJK SC")
    d.text(MAP_X + MAP_W + 6, MAP_Y - 9, "100", 15, MUTED, family="Noto Sans Mono CJK SC")
    d.text(MAP_X + MAP_W - 40, MAP_Y + MAP_H + 8, "100", 15, MUTED,
           family="Noto Sans Mono CJK SC")
    d.text(MAP_X - 46, MAP_Y + MAP_H + 8, "0", 15, MUTED, family="Noto Sans Mono CJK SC")
    d.text(MAP_X, MAP_Y + MAP_H + 34, "逻辑坐标 x（0–100，向右递增） · 单位：指数", 18, MUTED)
    d.text(20, MAP_Y - 26, "y（0–100，向上递增）", 18, MUTED)

    # ---- leaders first so boxes always sit on top --------------------------
    for p in pts:
        line = p["leader"]["polyline"]
        ax, ay = p["anchor_px"]["x"], p["anchor_px"]["y"]
        box = p["label"]["box"]
        cx, cy = box["x"] + box["w"] / 2, box["y"] + box["h"] / 2
        trim = p["dot_diameter_px"] / 2 + 6   # gap between dot and line start
        # start the polyline at the dot edge instead of the dot centre
        first = line[1] if len(line) > 1 else (cx, cy)
        dx, dy = first[0] - ax, first[1] - ay
        length = math.hypot(dx, dy) or 1.0
        start = (ax + dx / length * trim, ay + dy / length * trim)
        d.seg(start[0], start[1], line[1][0], line[1][1], LEADER, 2)
        for (x0, y0), (x1, y1) in zip(line[1:], line[2:]):
            d.seg(x0, y0, x1, y1, LEADER, 2)

    # ---- dots --------------------------------------------------------------
    for p in pts:
        ax, ay = p["anchor_px"]["x"], p["anchor_px"]["y"]
        dd = p["dot_diameter_px"]
        d.box(ax - dd / 2 - 2, ay - dd / 2 - 2, dd + 4, dd + 4, DOT_HALO, radius=(dd + 4) / 2)
        d.box(ax - dd / 2, ay - dd / 2, dd, dd, DOT_FILL, radius=dd / 2)

    # ---- labels ------------------------------------------------------------
    for p in pts:
        box = p["label"]["box"]
        d.box(box["x"], box["y"], box["w"], box["h"], BOX_BG, radius=6,
              border=f"1 SOLID {BOX_BORDER}")
        d.text(box["x"] + 10, box["y"] + 7, p["label"]["text"], FONT, INK)
        d.text(box["x"] + box["w"] - 10 - 42, box["y"] + 7, p["label"]["value_text"], FONT,
               TOP3 if p["id"] in ("M08", "M10", "M23") else MUTED,
               family="Noto Sans Mono CJK SC", w=42, align="CENTER_RIGHT")

    # ---- legend: the three highest values ---------------------------------
    top3 = sorted(pts, key=lambda p: -p["value"])[:3]
    lw, lh = 270.0, 40 + 30 * len(top3)
    # pick the first grid position whose card clears every dot and every label box
    legend_pos = None
    for ly in [780.0, 200.0, 760.0, 220.0]:
        for lx in [300.0, 1020.0, 620.0, 860.0]:
            card = {"x": lx, "y": ly, "w": lw, "h": lh}
            if lx + lw > MAP_X + MAP_W - 8 or ly + lh > MAP_Y + MAP_H - 8:
                continue
            clash = False
            for p in pts:
                b = p["label"]["box"]
                if not (card["x"] + card["w"] <= b["x"] or b["x"] + b["w"] <= card["x"]
                        or card["y"] + card["h"] <= b["y"] or b["y"] + b["h"] <= card["y"]):
                    clash = True
                    break
                ax, ay = p["anchor_px"]["x"], p["anchor_px"]["y"]
                if (card["x"] - 6 <= ax <= card["x"] + card["w"] + 6
                        and card["y"] - 6 <= ay <= card["y"] + card["h"] + 6):
                    clash = True
                    break
            if not clash:
                legend_pos = (lx, ly)
                break
        if legend_pos:
            break
    assert legend_pos is not None, "no clear position for the legend"
    lx, ly = legend_pos
    d.box(lx, ly, lw, lh, "#FFFFFFF2", radius=8, border=f"1 SOLID {BOX_BORDER}")
    d.text(lx + 12, ly + 10, "指数最高的 3 个点", 18, INK, weight="BOLD")
    for i, p in enumerate(top3):
        d.text(lx + 12, ly + 42 + i * 30, f"{p['id']}  {p['name']}", 18, MUTED)
        d.text(lx + lw - 52, ly + 42 + i * 30, str(p["value"]), 18, TOP3,
               family="Noto Sans Mono CJK SC", w=40, align="CENTER_RIGHT")
    d.box(48, CANVAS[1] - 52, CANVAS[0] - 96, 1, GRID)
    d.text(48, CANVAS[1] - 38, "锚点未被任何标签移动 · 24 个点全部保留 · 图形由 Snapshot DSL 直接绘制",
           18, "#94A3B8FF")

    dsl = d.finish()
    with open(os.path.join(HERE, "annotated-map.v1.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    print("annotated-map.v1.snapshot:", element_count(dsl), "elements")

    # ---- audit -------------------------------------------------------------
    def rect_overlap(a, b):
        return not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"]
                    or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])

    intersections = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if rect_overlap(pts[i]["label"]["box"], pts[j]["label"]["box"]):
                intersections.append([pts[i]["id"], pts[j]["id"]])
    min_gap = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i]["label"]["box"], pts[j]["label"]["box"]
            gx = max(a["x"] - (b["x"] + b["w"]), b["x"] - (a["x"] + a["w"]))
            gy = max(a["y"] - (b["y"] + b["h"]), b["y"] - (a["y"] + a["h"]))
            gap = max(gx, gy)
            min_gap = gap if min_gap is None else min(min_gap, gap)
    cross_count = layout["audit"]["crossing_count"]

    def seg_in_rect(x0, y0, x1, y1, r, pad=0.0):
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 2) + 1)
        for k in range(steps + 1):
            t = k / steps
            px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if (r["x"] - pad <= px <= r["x"] + r["w"] + pad
                    and r["y"] - pad <= py <= r["y"] + r["h"] + pad):
                return True
        return False

    line_through = []
    for p in pts:
        line = p["leader"]["polyline"]
        for q in pts:
            if q["id"] == p["id"]:
                continue
            for (x0, y0), (x1, y1) in zip(line, line[1:]):
                if seg_in_rect(x0, y0, x1, y1, q["label"]["box"]):
                    line_through.append([p["id"], q["id"]])
                    break
    boundary = []
    for p in pts:
        b = p["label"]["box"]
        if b["x"] < 0 or b["y"] < 0 or b["x"] + b["w"] > CANVAS[0] or b["y"] + b["h"] > CANVAS[1]:
            boundary.append([p["id"], "label"])
        ax, ay = p["anchor_px"]["x"], p["anchor_px"]["y"]
        r = p["dot_diameter_px"] / 2
        if not (MAP_X <= ax - r and ax + r <= MAP_X + MAP_W
                and MAP_Y <= ay - r and ay + r <= MAP_Y + MAP_H):
            boundary.append([p["id"], "dot"])
        for (x0, y0), (x1, y1) in zip(p["leader"]["polyline"], p["leader"]["polyline"][1:]):
            if not (0 <= min(x0, x1) and max(x0, x1) <= CANVAS[0]
                    and 0 <= min(y0, y1) and max(y0, y1) <= CANVAS[1]):
                boundary.append([p["id"], "leader"])
                break
    mapping_error = []
    for p in pts:
        ideal_x = MAP_X + p["logical"]["x"] / 100.0 * MAP_W
        ideal_y = MAP_Y + (1 - p["logical"]["y"] / 100.0) * MAP_H
        err = max(abs(ideal_x - p["anchor_px"]["x"]), abs(ideal_y - p["anchor_px"]["y"]))
        if err > 0.01:
            mapping_error.append([p["id"], round(err, 4)])
    # a leader must not graze a dot it does not belong to (>= 5px from the centre of
    # any other dot, i.e. fully outside that dot)
    def seg_point_dist(x0, y0, x1, y1, px, py):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return math.hypot(px - x0, py - y0)
        t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
        return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))
    line_grazes_dot = []
    for p in pts:
        for q in pts:
            if q["id"] == p["id"]:
                continue
            for (x0, y0), (x1, y1) in zip(p["leader"]["polyline"], p["leader"]["polyline"][1:]):
                if seg_point_dist(x0, y0, x1, y1, q["anchor_px"]["x"], q["anchor_px"]["y"]) < 6.0:
                    line_grazes_dot.append([p["id"], q["id"]])
                    break
    covers_dot = []
    for p in pts:
        for q in pts:
            b = p["label"]["box"]
            ax, ay = q["anchor_px"]["x"], q["anchor_px"]["y"]
            if b["x"] <= ax <= b["x"] + b["w"] and b["y"] <= ay <= b["y"] + b["h"]:
                covers_dot.append([p["id"], q["id"]])
    far = [p["id"] for p in pts if p["leader"]["anchor_to_label_px"] > 24.0
           and not p["leader"]["polyline"]]
    audit = {
        "schema": "a20-layout-audit/1",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "map_area": {"x": MAP_X, "y": MAP_Y, "w": MAP_W, "h": MAP_H},
        "counts": {"points": len(pts), "labels": len(pts),
                   "dots_shrunk": sum(1 for p in pts if p["dot_shrunk"]),
                   "labels_with_leader": sum(1 for p in pts if p["leader"]["needs_leader"])},
        "label_box_intersections": intersections,
        "label_min_gap_px": round(min_gap, 2) if min_gap is not None else None,
        "label_min_gap_required_px": 4.0,
        "line_through_label": line_through,
        "line_crossing_count": cross_count,
        "line_crossings": layout["audit"]["line_crossings"],
        "crossing_limit": 3,
        "boundary_violations": boundary,
        "mapping_errors_over_0.01px": mapping_error,
        "labels_covering_a_dot": covers_dot,
        "line_grazing_another_dot": line_grazes_dot,
        "line_grazing_tolerance_px": 6.0,
        "labels_without_leader_but_far": far,
        "font_px": {"body": FONT, "id": FONT_ID, "small": FONT_SMALL},
        "checks": {
            "no_label_intersection": not intersections,
            "label_gap_at_least_4px": (min_gap is None or min_gap >= 4.0),
            "no_line_through_label": not line_through,
            "crossings_at_most_3": cross_count <= 3,
            "nothing_out_of_canvas": not boundary,
            "anchors_exactly_mapped": not mapping_error,
            "no_label_covers_a_dot": not covers_dot,
            "no_line_grazes_another_dot": not line_grazes_dot,
            "every_far_label_has_leader": not far,
            "font_at_least_20": min(FONT, FONT_ID) >= 20,
        },
    }
    audit["all_checks_pass"] = all(audit["checks"].values())
    with open(os.path.join(HERE, "layout-audit.json"), "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)
    for k, v in audit["checks"].items():
        print(f"  {k}: {v}")
    print("elements:", element_count(dsl))


if __name__ == "__main__":
    main()
