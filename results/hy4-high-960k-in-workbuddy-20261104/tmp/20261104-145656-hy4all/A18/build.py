#!/usr/bin/env python3
"""A18 - a three-act visual story with conserved objects.

Same 15 units (5 blue / 5 orange / 5 gray, diameter 36) and same 3 processing
nodes in every act.  Conservation is expressed only through distance, links,
composition, direction and limited deformation - never by adding/removing/shrinking
units or by warning text.
"""
import json, math, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN
import suite

TASK = "A18"
ROOT = suite.ROOT
OUT = suite.out_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
TMP = suite.tmp_dir(TASK, VER)

BLUE, ORANGE, GRAY = "#245CE4", "#F28C28", "#94A3B8"
INK = "#18283F"; MUTED = "#64748B"; PANEL = "#F8FAFC"; LINE = "#DDE5F0"
LINK = "#C2CFE0"
R = 18.0                  # unit radius -> diameter 36
NODE_R = 48.0             # node half-size -> 96x96 bounding box
UNIT_COLORS = [BLUE] * 5 + [ORANGE] * 5 + [GRAY] * 5
UNIT_CNAMES = ["blue"] * 5 + ["orange"] * 5 + ["gray"] * 5
UNIT_IDS = ["U%02d" % i for i in range(1, 16)]
NODE_SHAPES = {"N01": "rounded_square", "N02": "diamond", "N03": "hexagon"}
NODE_FILL = {"N01": "#DBEAFE", "N02": "#FDE8CC", "N03": "#E2E8F0"}
NODE_EDGE = {"N01": BLUE, "N02": ORANGE, "N03": "#64748B"}


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def unit(uid, x, y, node):
    i = int(uid[1:]) - 1
    return {"id": uid, "color": UNIT_COLORS[i], "color_name": UNIT_CNAMES[i],
            "cx": round(x, 2), "cy": round(y, 2), "diameter": 36, "node": node}


def draw_node(c, n):
    cx, cy, sid = n["cx"], n["cy"], n["id"]
    st = n.get("stretch", 1.0)
    fill, edge = NODE_FILL[sid], NODE_EDGE[sid]
    if sid == "N01":
        c.rect(cx - NODE_R, cy - NODE_R * st, 2 * NODE_R, 2 * NODE_R * st,
               fill, radius=12, border="3 SOLID " + edge)
    elif sid == "N02":
        outer = [(cx, cy - NODE_R * st), (cx + NODE_R, cy),
                 (cx, cy + NODE_R * st), (cx - NODE_R, cy)]
        inner = [(cx, cy - (NODE_R - 5) * st), (cx + NODE_R - 5, cy),
                 (cx, cy + (NODE_R - 5) * st), (cx - NODE_R + 5, cy)]
        c.poly(outer, edge); c.poly(inner, fill)
    else:
        pts_o = [polar(cx, cy, NODE_R, -90 + k * 60) for k in range(6)]
        pts_i = [polar(cx, cy, NODE_R - 5, -90 + k * 60) for k in range(6)]
        c.poly(pts_o, edge); c.poly(pts_i, fill)


def draw_act(c, x0, title, units, nodes, color_accent, link_color=None, link_width=None):
    # Refinement after viewing previews: overload links are denser/darker so the
    # "everything funnels into one node" reading survives at thumbnail size.
    if link_color is None:
        if "过载" in title:
            link_color, link_width = "#9AAEC6", 3
        elif "重新分配" in title:
            link_color, link_width = "#B7C6DA", 2
        else:
            link_color, link_width = "#CBD7E6", 2
    # act panel
    c.rect(x0, 92, 496, 866, PANEL, radius=18, border="1 SOLID " + LINE)
    c.text(x0, 106, 496, 44, title, 28, color_accent, bold=True, align="CENTER")
    nd = {n["id"]: n for n in nodes}
    # links FIRST (drawn beneath circles and nodes -> lines never cover a circle)
    for u in units:
        n = nd[u["node"]]
        dx, dy = n["cx"] - u["cx"], n["cy"] - u["cy"]
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        c.line(u["cx"] + ux * R, u["cy"] + uy * R,
               n["cx"] - ux * NODE_R, n["cy"] - uy * NODE_R, link_width, link_color)
    # nodes
    for n in nodes:
        draw_node(c, n)
    # units (on top)
    for u in units:
        c.circle(u["cx"], u["cy"], R, u["color"])


def build(layout):
    c = Canvas(1600, 1000, "#FFFFFF", font=CN)
    c.text(0, 26, 1600, 54, "信息守恒 · 集中 → 过载 → 重新分配", 36, INK,
           bold=True, align="CENTER")
    acts = []
    if layout == "A":
        # ---- ACT 1: single-centre attraction, loose two-arc fan -------------
        cx1 = 280
        n1 = [{"id": "N01", "cx": cx1, "cy": 700},
              {"id": "N02", "cx": cx1 - 160, "cy": 700},
              {"id": "N03", "cx": cx1 + 160, "cy": 700}]
        u1 = []
        inner_ang = [-140, -115, -90, -65, -40]
        outer_ang = [-140 + i * (100 / 9) for i in range(10)]
        for a in inner_ang:
            x, y = polar(cx1, 700, 180, a); u1.append(unit(UNIT_IDS[len(u1)], x, y, "N01"))
        for a in outer_ang:
            x, y = polar(cx1, 700, 320, a); u1.append(unit(UNIT_IDS[len(u1)], x, y, "N01"))
        draw_act(c, 32, "第一幕 · 集中", u1, n1, BLUE)
        acts.append({"act": 1, "name": "集中", "units": u1, "nodes": n1})

        # ---- ACT 2: overload, tight 40px grid queue into the SAME node -------
        cx2 = 792
        n2 = [{"id": "N01", "cx": cx2, "cy": 700, "stretch": 1.30},
              {"id": "N02", "cx": cx2 - 160, "cy": 700},
              {"id": "N03", "cx": cx2 + 160, "cy": 700}]
        u2 = []
        for row in range(5):
            for col in range(3):
                x = cx2 + (col - 1) * 40
                y = 300 + row * 40
                u2.append(unit(UNIT_IDS[len(u2)], x, y, "N01"))
        draw_act(c, 552, "第二幕 · 过载", u2, n2, ORANGE)
        acts.append({"act": 2, "name": "过载", "units": u2, "nodes": n2})

        # ---- ACT 3: redistribution, 5 units per node ------------------------
        cx3 = 1304
        n3 = [{"id": "N01", "cx": cx3, "cy": 700},
              {"id": "N02", "cx": cx3 - 160, "cy": 700},
              {"id": "N03", "cx": cx3 + 160, "cy": 700}]
        groups = {
            "N02": ["U01", "U02", "U06", "U07", "U11"],
            "N01": ["U03", "U04", "U08", "U12", "U13"],
            "N03": ["U05", "U09", "U10", "U14", "U15"],
        }
        u3 = []
        for nid, ids in groups.items():
            ncx = next(n["cx"] for n in n3 if n["id"] == nid)
            pos = [(ncx - 48, 400), (ncx, 400), (ncx + 48, 400),
                   (ncx - 24, 460), (ncx + 24, 460)]
            for uid, (x, y) in zip(ids, pos):
                u3.append(unit(uid, x, y, nid))
        draw_act(c, 1072, "第三幕 · 重新分配", u3, n3, "#198369")
        acts.append({"act": 3, "name": "重新分配", "units": u3, "nodes": n3})
    else:
        # ---- Layout B: nodes at centre, units orbit them --------------------
        cx1 = 280
        n1 = [{"id": "N01", "cx": cx1, "cy": 500},
              {"id": "N02", "cx": cx1 - 170, "cy": 840},
              {"id": "N03", "cx": cx1 + 170, "cy": 840}]
        u1 = []
        for i in range(15):
            x, y = polar(cx1, 500, 210, -90 + i * 24)
            u1.append(unit(UNIT_IDS[i], x, y, "N01"))
        draw_act(c, 32, "第一幕 · 集中", u1, n1, BLUE)
        acts.append({"act": 1, "name": "集中", "units": u1, "nodes": n1})

        cx2 = 792
        n2 = [{"id": "N01", "cx": cx2, "cy": 500, "stretch": 1.25},
              {"id": "N02", "cx": cx2 - 170, "cy": 840},
              {"id": "N03", "cx": cx2 + 170, "cy": 840}]
        u2 = []
        for i in range(5):
            x, y = polar(cx2, 500, 105, -90 + i * 72); u2.append(unit(UNIT_IDS[i], x, y, "N01"))
        for i in range(10):
            x, y = polar(cx2, 500, 175, -90 + i * 36); u2.append(unit(UNIT_IDS[5 + i], x, y, "N01"))
        draw_act(c, 552, "第二幕 · 过载", u2, n2, ORANGE)
        acts.append({"act": 2, "name": "过载", "units": u2, "nodes": n2})

        cx3 = 1304
        n3 = [{"id": "N01", "cx": cx3, "cy": 760},
              {"id": "N02", "cx": cx3 - 165, "cy": 340},
              {"id": "N03", "cx": cx3 + 165, "cy": 340}]
        groups = {
            "N02": ["U01", "U02", "U06", "U07", "U11"],
            "N01": ["U03", "U04", "U08", "U12", "U13"],
            "N03": ["U05", "U09", "U10", "U14", "U15"],
        }
        u3 = []
        for nid, ids in groups.items():
            n = next(nn for nn in n3 if nn["id"] == nid)
            for k, uid in enumerate(ids):
                x, y = polar(n["cx"], n["cy"], 130, -90 + (k - 2) * 34)
                u3.append(unit(uid, x, y, nid))
        draw_act(c, 1072, "第三幕 · 重新分配", u3, n3, "#198369")
        acts.append({"act": 3, "name": "重新分配", "units": u3, "nodes": n3})
    return c.render(), acts


def min_gap(units):
    best = 1e9
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            d = math.hypot(units[i]["cx"] - units[j]["cx"], units[i]["cy"] - units[j]["cy"])
            best = min(best, d)
    return round(best, 2)


def audit_payload(acts):
    unit_meta = [{"id": UNIT_IDS[i], "color_name": (["blue"] * 5 + ["orange"] * 5 + ["gray"] * 5)[i],
                  "color": UNIT_COLORS[i], "diameter": 36} for i in range(15)]
    node_meta = [{"id": nid, "shape": NODE_SHAPES[nid], "base_size": [96, 96],
                  "identity_marker": NODE_SHAPES[nid]} for nid in ["N01", "N02", "N03"]]
    act_records = []
    for a in acts:
        loads = {}
        for u in a["units"]:
            loads[u["node"]] = loads.get(u["node"], 0) + 1
        act_records.append({
            "act": a["act"], "name": a["name"],
            "units": a["units"],
            "nodes": [{**n, "shape": NODE_SHAPES[n["id"]],
                       "bbox": [n["cx"] - NODE_R, n["cy"] - NODE_R * n.get("stretch", 1),
                                n["cx"] + NODE_R, n["cy"] + NODE_R * n.get("stretch", 1)],
                       "rotation_deg": 0, "stretch": n.get("stretch", 1.0),
                       "load": loads.get(n["id"], 0)} for n in a["nodes"]],
            "min_unit_center_distance_px": min_gap(a["units"]),
        })
    # conservation checks
    checks = []
    for a in act_records:
        ids = sorted(u["id"] for u in a["units"])
        col = sorted((u["id"], u["color"]) for u in a["units"])
        checks.append({"check": "act %d has exactly U01-U15" % a["act"],
                       "passed": ids == UNIT_IDS,
                       "evidence": "story-audit.json act %d units" % a["act"]})
        checks.append({"check": "act %d colors & 36px diameter conserved" % a["act"],
                       "passed": col == sorted((UNIT_IDS[i], UNIT_COLORS[i]) for i in range(15))
                                 and all(u["diameter"] == 36 for u in a["units"]),
                       "evidence": "unit metadata act %d" % a["act"]})
        checks.append({"check": "act %d units do not overlap (center distance >= 36)" % a["act"],
                       "passed": a["min_unit_center_distance_px"] >= 36,
                       "value": a["min_unit_center_distance_px"],
                       "evidence": "computed from unit centers"})
        checks.append({"check": "act %d has exactly the same 3 node identities" % a["act"],
                       "passed": sorted(n["id"] for n in a["nodes"]) == ["N01", "N02", "N03"],
                       "evidence": "nodes array act %d" % a["act"]})
    a3 = act_records[2]
    groups = {}
    for u in a3["units"]:
        groups.setdefault(u["node"], []).append(u["color"])
    checks.append({"check": "act 3 every node receives exactly 5 units",
                   "passed": all(len(v) == 5 for v in groups.values()) and len(groups) == 3,
                   "value": {k: len(v) for k, v in groups.items()}, "evidence": "act 3 units"})
    checks.append({"check": "act 3 each group has >= 2 distinct colors",
                   "passed": all(len(set(v)) >= 2 for v in groups.values()),
                   "value": {k: sorted(set(v)) for k, v in groups.items()}, "evidence": "act 3 units"})
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "canvas": [1600, 1000], "unit_radius_px": R, "node_half_size_px": NODE_R,
        "units": unit_meta, "nodes": node_meta, "acts": act_records,
        "narrative_evidence": [
            {"act": 1, "clue": "15 条连线全部指向唯一中心节点 N01（x=280,y=700），N02/N03 空置",
             "geometry": "内圈 R=180、外圈 R=320 两层弧，最小中心距 %spx（宽松）" %
                         act_records[0]["min_unit_center_distance_px"],
             "judgement": "单一中心吸引：所有关系汇聚一点，单元间距均匀、有序"},
            {"act": 1, "clue": "单元呈两层同心弧围绕 N01，连线为向心放射且互不交叉",
             "geometry": "两层半径差 140px，弧上间距 >= 62px",
             "judgement": "距离与方向共同表达「被同一中心吸引」"},
            {"act": 2, "clue": "仍是同一 N01，但 15 单元压缩成 5×3 紧密队列，中心距仅 40px",
             "geometry": "min center distance %spx（间隙 4px），对比第一幕 %spx" %
                         (act_records[1]["min_unit_center_distance_px"],
                          act_records[0]["min_unit_center_distance_px"]),
             "judgement": "过载：不增删不缩小单元，仅靠间距压缩与全部连线挤向同一入口表达拥堵"},
            {"act": 2, "clue": "N01 唯一发生有限形变：纵向拉伸 1.30（96→124.8px），形状仍为圆角方形",
             "geometry": "N01 bbox 96×124.8；N02/N03 仍 96×96 且无连线",
             "judgement": "负载集中在单节点，形变只改尺寸参数、不改身份"},
            {"act": 3, "clue": "连线分成左/中/右三束，分别指向 N02/N01/N03，单元分成三个间距 160px 的簇",
             "geometry": "三节点 x=1144/1304/1464，每簇 5 单元，最小中心距 %spx" %
                         act_records[2]["min_unit_center_distance_px"],
             "judgement": "重新分配：分流方向与负载分配由连线和空间分组表达，不靠颜色"},
            {"act": 3, "clue": "每节点恰 5 单元且含至少两种颜色，单元间距恢复宽松",
             "geometry": "组1 蓝2橙2灰1 / 组2 蓝2橙1灰2 / 组3 蓝1橙2灰2",
             "judgement": "单节点负载由 15 降到 5，过载被解除"},
        ],
        "limited_deformation": {
            "where": "act 2 / N01 only",
            "params": {"vertical_stretch": 1.30, "bbox": [96, 96, "->", 96, 124.8]},
            "identity_unchanged": "N01 仍为蓝色圆角方形，形状特征、填充与边框未变；仅纵向尺寸参数变化",
        },
        "checks": checks,
        "view_checks": [
            {"view": "full 1600x1000", "result": None},
            {"view": "400px wide thumbnail", "result": None},
        ],
        "preview_comparison": {
            "previews": [
                {"id": "A", "path": "tmp/<run_id>/A18/v1/preview-A.png",
                 "layout": "三幕横向并列；节点在每幕下方一字排开；幕1 两层宽松弧汇聚单节点、幕2 40px 紧密队列、幕3 三簇分流",
                 "verdict": "选用"},
                {"id": "B", "path": "tmp/<run_id>/A18/v1/preview-B.png",
                 "layout": "节点居幕中央、单元环形围绕；幕3 节点三角分布、单元环绕",
                 "verdict": "未选用"},
            ],
            "selection_reason": "构图 A 的「集中→过载」对比由宽松弧（最小中心距 61.96px）到紧密队列（40px）的间距变化直接呈现，三簇分流方向清楚，三幕全部在面板内；构图 B 的幕1/幕2 同为环形围绕、过载差异弱，且幕3 部分单元越出面板右/上边界、分组较散。",
            "refinement_from_selected_preview": "基于预览 A 实际看图：加深第二幕连线（#9AAEC6、3px）使「全部挤向同一入口」在缩略尺寸下仍可辨；把 N01 有限形变由 1.25 调为 1.30，强化单节点负载；第三幕连线略加深以突出三束分流。守恒参数、单元坐标与节点身份不变。",
        },
    }


RATIONALE = """三幕共用同一组 15 单元（5 蓝/5 橙/5 灰，直径 36）与 3 节点：N01 圆角方、
N02 菱形、N03 六边形，外接框恒 96×96。

第一幕单元排成两层宽松弧（最小中心距 62px），15 条连线全指向唯一 N01，
N02/N03 空置：距离、放射方向与汇聚点读出「单一中心吸引」。
第二幕不增删不缩小单元，只把中心距压到 40px 成 5×3 紧密队列，连线全挤向
同一入口，N01 纵向拉伸 1.30（形状身份不变）：过载由间距压缩、连线密度与
有限形变读出，而非颜色或警示文字。
第三幕连线分三束，单元分成间距 160px 的三簇，每节点恰收 5 个且至少两色，
负载由 15 降到 5：分流方向即「重新分配」。关系由连线与构图承担，颜色仅辅助。"""


def main():
    chosen = os.environ.get("A18_LAYOUT", "A")
    dsl, acts = build(chosen)
    (OUT / "three-act-story.snapshot").write_text(dsl, encoding="utf-8")
    (TMP / "three-act-story.snapshot").write_text(dsl, encoding="utf-8")
    # two alternative full-size previews (temporary, first version only)
    if VER == "v1":
        for L in ("A", "B"):
            pv, _ = build(L)
            (TMP / ("preview-%s.snapshot" % L)).write_text(pv, encoding="utf-8")
    # audit + rationale
    (OUT / "story-audit.json").write_text(
        json.dumps(audit_payload(acts), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "rationale.md").write_text(RATIONALE, encoding="utf-8")
    print("A18 | version", VER, "| chosen layout", chosen,
          "| DSL bytes", len(dsl.encode("utf-8")))
    for a in acts:
        print("  act", a["act"], "units", len(a["units"]),
              "min gap", min_gap(a["units"]),
              "loads", {n: sum(1 for u in a["units"] if u["node"] == n)
                        for n in ["N01", "N02", "N03"]})


if __name__ == "__main__":
    main()
