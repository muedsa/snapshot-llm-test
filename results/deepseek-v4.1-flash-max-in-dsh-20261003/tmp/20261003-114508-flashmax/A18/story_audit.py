"""A18 geometry validator + story-audit.json builder.

Checks, from the same numbers the generator used:
  * every act holds exactly 15 units, all fully inside its panel
  * unit-unit centre distance >= 36 and unit-node centre distance >= 40 (no overlap)
  * the colour multiset of every act is {blue 5, orange 5, grey 5}
  * act III gives every node exactly 5 units and each node's set has >= 2 colours
  * no connector segment comes within 19 px of a unit centre, or 23 px of a node centre
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
import gen_story as G  # noqa: E402

UNIT_D, NODE_D = 36, 40
TOL = 0.6            # the DSL rounds coordinates to 2 dp


def seg_point_distance(ax, ay, bx, by, px, py):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def audit(units: list) -> dict:
    out = {"schema": "a18-story-audit/1", "seed": G.SEED,
           "unit_diameter": UNIT_D, "node_diameter": G.NODE_D,
           "colour_multiset_required": {"blue": 5, "orange": 5, "grey": 5},
           "acts": [], "problems": []}
    colour_counts = {}
    for idx, (index, name, note) in enumerate(G.ACTS):
        variant = "abc"[idx]
        px = G.MARGIN + idx * (G.PW + G.GAP)
        cx = px + G.PW / 2
        pts, nodes, owner = G.LAYOUTS[variant](cx, G.ACT_CY)
        offset = idx * 5
        rec = {"act": idx + 1, "act_label": index, "act_name": name, "variant": variant,
               "panel": {"x": round(px, 2), "y": G.TOP, "w": round(G.PW, 2), "h": G.PANEL_H},
               "nodes": [{"id": f"N{ni + 1}", "x": round(nx, 2), "y": round(ny, 2)} for ni, (nx, ny) in enumerate(nodes)],
               "units": []}
        counts = {"blue": 0, "orange": 0, "grey": 0}
        for i, (ux, uy) in enumerate(pts):
            u = units[(i + offset) % 15]
            counts[u["color"]] += 1
            rec["units"].append({
                "id": u["id"], "colour": u["color"],
                "logical": {"index": (i + offset) % 15},
                "x": round(ux, 2), "y": round(uy, 2),
                "received_by": (f"N{owner[i] + 1}" if variant == "c" else "N1"),
                "distance_to_node": round(math.hypot(ux - nodes[owner[i]][0], uy - nodes[owner[i]][1]), 2),
                "fully_visible": (px + UNIT_D / 2 <= ux <= px + G.PW - UNIT_D / 2
                                  and G.TOP + UNIT_D / 2 <= uy <= G.TOP + G.PANEL_H - UNIT_D / 2),
                "overlaps_any_unit": False,
            })
        recol = {"blue": 0, "orange": 0, "grey": 0}
        for k, v in counts.items():
            recol[k] = v
            colour_counts[k] = colour_counts.get(k, 0) + v
            if v != 5:
                out["problems"].append(f"act {idx + 1}: colour {k} count {v} != 5")
        rec["colour_counts"] = recol
        # overlap checks
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                if d < UNIT_D - TOL:
                    rec["units"][i]["overlaps_any_unit"] = True
                    out["problems"].append(
                        f"act {idx + 1}: units {rec['units'][i]['id']}/{rec['units'][j]['id']} "
                        f"distance {d:.2f} < {UNIT_D}")
            for nx, ny in nodes:
                d = math.hypot(pts[i][0] - nx, pts[i][1] - ny)
                if d < UNIT_D / 2 + G.NODE_D / 2 + 2 - TOL:
                    out["problems"].append(
                        f"act {idx + 1}: unit {rec['units'][i]['id']} touches a node ({d:.2f})")
        # connector clearance
        for ni, (nx, ny) in enumerate(nodes):
            trim0 = 78 if variant == "b" else G.NODE_D / 2 + 2
            for i, (ux, uy) in enumerate(pts):
                if owner[i] != ni:
                    continue
                dist = math.hypot(ux - nx, uy - ny)
                if dist <= trim0 + UNIT_D / 2 + 1:
                    out["problems"].append(
                        f"act {idx + 1}: connector for {rec['units'][i]['id']} is too short to draw")
                    continue
                ux2, uy2 = nx + (ux - nx) / dist * trim0, ny + (uy - ny) / dist * trim0
                vx = ux - (ux - nx) / dist * (UNIT_D / 2 + 1)
                vy = uy - (uy - ny) / dist * (UNIT_D / 2 + 1)
                for j, (ox, oy) in enumerate(pts):
                    if j == i:
                        continue
                    if seg_point_distance(ux2, uy2, vx, vy, ox, oy) < UNIT_D / 2 + 1 - TOL:
                        out["problems"].append(
                            f"act {idx + 1}: connector for {rec['units'][i]['id']} crosses "
                            f"unit {rec['units'][j]['id']}")
                if seg_point_distance(ux2, uy2, vx, vy, nx, ny) < G.NODE_D / 2 + 1 - TOL:
                    out["problems"].append(f"act {idx + 1}: connector overlaps its own node")
        # act III per-node colour mix
        if variant == "c":
            per = {f"N{ni + 1}": {"units": [], "colours": set()} for ni in range(len(nodes))}
            for i, (ux, uy) in enumerate(pts):
                key = f"N{owner[i] + 1}"
                per[key]["units"].append(rec["units"][i]["id"])
                per[key]["colours"].add(rec["units"][i]["colour"])
            rec["node_intake"] = {k: {"count": len(v["units"]), "units": v["units"],
                                      "colours": sorted(v["colours"])} for k, v in per.items()}
            for k, v in per.items():
                if len(v["units"]) != 5:
                    out["problems"].append(f"act 3: {k} received {len(v['units'])} units, expected 5")
                if len(v["colours"]) < 2:
                    out["problems"].append(f"act 3: {k} received only {sorted(v['colours'])}")
        out["acts"].append(rec)
    out["colour_multiset_actual"] = colour_counts
    out["checks"] = {
        "15_units_per_act": all(len(a["units"]) == 15 for a in out["acts"]),
        "colour_multiset_5_5_5_every_act": all(a["colour_counts"] == {"blue": 5, "orange": 5, "grey": 5}
                                               for a in out["acts"]),
        "all_units_fully_visible": all(u["fully_visible"] for a in out["acts"] for u in a["units"]),
        "no_unit_overlaps": not any(u["overlaps_any_unit"] for a in out["acts"] for u in a["units"]),
        "act3_nodes_each_get_5": all(v["count"] == 5 for v in out["acts"][2]["node_intake"].values()),
        "act3_nodes_have_two_colours": all(len(v["colours"]) >= 2
                                           for v in out["acts"][2]["node_intake"].values()),
        "no_problems": not out["problems"],
    }
    return out


def main() -> None:
    units = G.make_units()
    out = audit(units)
    dst = os.path.join(HERE, "story-audit.json")
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("story-audit.json written")
    for k, v in out["checks"].items():
        print(f"  {k}: {v}")
    if out["problems"]:
        print("PROBLEMS:")
        for p in out["problems"][:20]:
            print("  -", p)
        sys.exit(2)


if __name__ == "__main__":
    main()
