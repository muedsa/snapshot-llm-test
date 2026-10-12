"""A18 validator (final): audits the DSL that was actually emitted, segment by segment.

Reads the finished document, recovers every circle centre and every connector strand from
the Transform matrices, then checks the geometry the brief demands:
  * 15 units per act, each fully inside its own act panel
  * unit-unit centre distance >= 36, unit-node >= 40 (diameters 36 / 44)
  * per-act colour multiset = {blue 5, orange 5, grey 5}
  * no connector strand passes within (unit radius + 1) of another unit's centre, nor
    within (node radius + 1) of a node centre
  * act III: three nodes, each taking five units with >= 2 colours
"""
from __future__ import annotations

import collections
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
import geom_v9  # noqa: E402
import gen_story as G  # noqa: E402

UNIT_R, NODE_R = 18.0, 22.0
FILLS = {"blue": "#2563EBFF", "orange": "#EA580CFF", "grey": "#94A3B8FF"}


def seg_point_distance(ax, ay, bx, by, px, py):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def parse(dsl: str):
    circles, segs = [], []
    pat = (r'<Transform matrix="\(([^)]+)\)"><Container width="([\d.]+)" '
           r'height="([\d.]+)" color="(#[0-9A-F]{8})" borderRadius="([\d.]+)"')
    for m in re.finditer(pat, dsl):
        mat = [float(v) for v in m.group(1).split(",")]
        w, h = float(m.group(2)), float(m.group(3))
        m11, m12, tx, ty = mat[0], mat[1], mat[12], mat[13]
        if abs(w - 36) < 0.01 and abs(h - 36) < 0.01:
            circles.append({"kind": "unit", "cx": tx + 18, "cy": ty + 18, "color": m.group(4)})
        elif abs(w - 44) < 0.01 and abs(h - 44) < 0.01 and m.group(4) == "#0F172AFF":
            circles.append({"kind": "node", "cx": tx + 22, "cy": ty + 22, "color": m.group(4)})
        elif abs(h - 2.0) < 0.01 and w > 4:
            segs.append({"x0": tx, "y0": ty, "x1": tx + m11 * w, "y1": ty + m12 * w})
    return circles, segs


def main() -> None:
    geom_v9.install()
    dsl = G.build("abc", G.make_units(), arrows=True)
    with open(os.path.join(HERE, "three-act-story.v9.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(dsl)
    circles, segs = parse(dsl)
    panel_x = [G.MARGIN + i * (G.PW + G.GAP) for i in range(3)]

    def act_of(x):
        for i, px in enumerate(panel_x):
            if px - 40 <= x <= px + G.PW + 40:
                return i
        return None

    acts = collections.defaultdict(lambda: {"units": [], "nodes": []})
    for c in circles:
        a = acts[act_of(c["cx"])]
        (a["units"] if c["kind"] == "unit" else a["nodes"]).append(c)
    problems = []
    report = {"schema": "a18-story-audit/1", "seed": G.SEED,
              "geometry": {"unit_diameter": 36, "node_diameter": 44,
                           "act1_rings": [118, 196], "act2_rings": [105, 182],
                           "act3_fan_radius": 88},
              "colour_multiset_required": {"blue": 5, "orange": 5, "grey": 5},
              "acts": [], "problems": problems}
    seg_act = collections.defaultdict(list)
    for s in segs:
        a = act_of(s["x0"])
        if a is not None:
            seg_act[a].append(s)
    for idx in range(3):
        a = acts[idx]
        counts = collections.Counter(u["color"] for u in a["units"])
        rec = {"act": idx + 1, "act_label": G.ACTS[idx][0], "act_name": G.ACTS[idx][1],
               "panel": {"x": round(panel_x[idx], 2), "y": G.TOP, "w": round(G.PW, 2),
                         "h": G.PANEL_H},
               "node_count": len(a["nodes"]),
               "nodes": [{"x": round(n["cx"], 2), "y": round(n["cy"], 2)} for n in a["nodes"]],
               "colour_counts": {k: counts.get(v, 0) for k, v in FILLS.items()},
               "units": [{"x": round(u["cx"], 2), "y": round(u["cy"], 2), "colour": u["color"]}
                         for u in a["units"]]}
        if len(a["units"]) != 15:
            problems.append(f"act {idx + 1}: {len(a['units'])} units, expected 15")
        if any(v != 5 for v in rec["colour_counts"].values()):
            problems.append(f"act {idx + 1}: colour counts {rec['colour_counts']}")
        for i, u in enumerate(a["units"]):
            if not (panel_x[idx] + UNIT_R <= u["cx"] <= panel_x[idx] + G.PW - UNIT_R
                    and G.TOP + UNIT_R <= u["cy"] <= G.TOP + G.PANEL_H - UNIT_R):
                problems.append(f"act {idx + 1}: unit ({u['cx']:.1f},{u['cy']:.1f}) not fully visible")
            for j in range(i + 1, len(a["units"])):
                d = math.hypot(u["cx"] - a["units"][j]["cx"], u["cy"] - a["units"][j]["cy"])
                if d < 36 - 0.6:
                    problems.append(f"act {idx + 1}: unit pair {d:.2f} < 36")
            for n in a["nodes"]:
                d = math.hypot(u["cx"] - n["cx"], u["cy"] - n["cy"])
                if d < UNIT_R + NODE_R + 2 - 0.6:
                    problems.append(f"act {idx + 1}: unit touches node ({d:.2f})")
        conflicts = 0
        for s in seg_act[idx]:
            for u in a["units"]:
                d = seg_point_distance(s["x0"], s["y0"], s["x1"], s["y1"], u["cx"], u["cy"])
                if d < UNIT_R + 1 - 0.6:
                    if (math.hypot(s["x1"] - u["cx"], s["y1"] - u["cy"]) < UNIT_R + 3
                            or math.hypot(s["x0"] - u["cx"], s["y0"] - u["cy"]) < UNIT_R + 3):
                        continue
                    problems.append(f"act {idx + 1}: connector passes through unit "
                                    f"({u['cx']:.1f},{u['cy']:.1f}) clearance {d:.2f}")
                    conflicts += 1
            for n in a["nodes"]:
                d = seg_point_distance(s["x0"], s["y0"], s["x1"], s["y1"], n["cx"], n["cy"])
                if d < NODE_R + 1 - 0.6:
                    if (math.hypot(s["x0"] - n["cx"], s["y0"] - n["cy"]) < NODE_R + 3
                            or math.hypot(s["x1"] - n["cx"], s["y1"] - n["cy"]) < NODE_R + 3):
                        continue
                    problems.append(f"act {idx + 1}: connector overlaps a node, clearance {d:.2f}")
                    conflicts += 1
        rec["connector_conflicts"] = conflicts
        report["acts"].append(rec)
    intake = {f"N{i + 1}": {"units": [], "colours": []} for i in range(len(acts[2]["nodes"]))}
    for u in acts[2]["units"]:
        nearest = min(range(len(acts[2]["nodes"])),
                      key=lambda i: math.hypot(u["cx"] - acts[2]["nodes"][i]["cx"],
                                               u["cy"] - acts[2]["nodes"][i]["cy"]))
        key = f"N{nearest + 1}"
        intake[key]["units"].append([round(u["cx"], 1), round(u["cy"], 1)])
        intake[key]["colours"].append(u["color"])
    report["acts"][2]["node_intake"] = {
        k: {"count": len(v["units"]), "colours": sorted(set(v["colours"]))}
        for k, v in intake.items()}
    for k, v in intake.items():
        if len(v["units"]) != 5:
            problems.append(f"act 3: {k} nearest-node intake {len(v['units'])} != 5")
        if len(set(v["colours"])) < 2:
            problems.append(f"act 3: {k} has a single colour {sorted(set(v['colours']))}")
    report["checks"] = {
        "15_units_per_act": all(len(a["units"]) == 15 for a in report["acts"]),
        "colour_multiset_5_5_5_every_act": all(set(a["colour_counts"].values()) == {5}
                                               for a in report["acts"]),
        "all_units_fully_visible": not any("not fully visible" in p for p in problems),
        "no_unit_overlap": not any("unit pair" in p for p in problems),
        "no_unit_touches_node": not any("touches node" in p for p in problems),
        "no_connector_crosses_unit": not any("passes through unit" in p for p in problems),
        "no_connector_overlaps_node": not any("overlaps a node" in p for p in problems),
        "three_nodes": report["acts"][2]["node_count"] == 3,
        "act3_each_node_5_units_two_colours": all(
            v["count"] == 5 and len(v["colours"]) >= 2
            for v in report["acts"][2]["node_intake"].values()),
        "no_problems": not problems,
    }
    with open(os.path.join(HERE, "story-audit.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    for k, v in report["checks"].items():
        print(f"  {k}: {v}")
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems[:25]:
            print("   -", p)
        sys.exit(2)
    print("story-audit.json written; all checks pass")


if __name__ == "__main__":
    main()
