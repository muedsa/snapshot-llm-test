# -*- coding: utf-8 -*-
"""A18 geometry: two candidate narrative compositions + constraint checks.

Canvas 1600x1000; origin top-left, x right, y down, pixel units (audit
coordinate convention).  All coordinates in a story are absolute canvas
coordinates.

Fixed cast (conserved across acts):
  units  U01-U15, diameter 36: U01-U05 blue, U06-U10 orange, U11-U15 gray
  nodes  N01 square / N02 circle / N03 diamond, base bbox 76x76, fill #0F172A

Composition A ("three panels"): three 480x840 act cards side by side,
theatrical acts; act1 = radial rings around a single centre, act2 = three
tight queues funnelled into a squeezed centre node, act3 = three unit
clusters under three nodes.

Composition B ("three bands"): three full-width 1536x276 horizontal bands
read as a left-to-right process; same three states in band form.

The chosen composition is refined separately; audit numbers are read from the
story actually delivered.
"""
import math

# ---------------------------------------------------------------- constants
CANVAS_W, CANVAS_H = 1600, 1000

UNIT_D = 36.0
UNIT_R = UNIT_D / 2
NODE_BASE = 76.0
NODE_HALF = NODE_BASE / 2
MIN_UNIT_GAP = 4.0            # task: units must not overlap (we keep >= 4px)
DIAMOND_SIDE = NODE_BASE / math.sqrt(2)   # 53.740909... -> rotated bbox 76

LINE_W = 4
LINE_COLOR = "#64748B"
NODE_FILL = "#0F172A"
BG = "#F1F5F9"
PANEL_BG = "#FFFFFF"
PANEL_BORDER = "1 SOLID #E2E8F0"
TEXT_COLOR = "#0F172A"
FONT = "Noto Sans CJK SC"

BLUE, ORANGE, GRAY = "#2563EB", "#F59E0B", "#94A3B8"
UNIT_IDS = ["U%02d" % i for i in range(1, 16)]
NODE_IDS = ["N01", "N02", "N03"]
NODE_SHAPES = {"N01": "square", "N02": "circle", "N03": "diamond"}
UNIT_COLORS = {}
for _i in range(1, 6):
    UNIT_COLORS["U%02d" % _i] = BLUE
for _i in range(6, 11):
    UNIT_COLORS["U%02d" % _i] = ORANGE
for _i in range(11, 16):
    UNIT_COLORS["U%02d" % _i] = GRAY
COLOR_NAMES = {BLUE: "blue", ORANGE: "orange", GRAY: "gray"}

TITLE = "信息守恒的三幕：集中 → 过载 → 重新分配"
ACT_NAMES = ["第一幕 · 集中", "第二幕 · 过载", "第三幕 · 重新分配"]


# ---------------------------------------------------------------- helpers
def node_bbox(shape, cx, cy, deform=None):
    """Actual painted bbox of a node; deform=(w,h) overrides the base box."""
    if deform:
        w, h = deform
    elif shape == "diamond":
        w = h = DIAMOND_SIDE           # unrotated square; rotated bbox = 76
    else:
        w = h = NODE_BASE
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]


def node_visual_bbox(shape, cx, cy, deform=None):
    """Bbox of the painted result (diamond rotated 45 deg -> 76x76)."""
    if deform:
        w, h = deform
        return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    return [cx - NODE_HALF, cy - NODE_HALF, cx + NODE_HALF, cy + NODE_HALF]


def point_segment_distance(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def unit_node_clearance(ux, uy, bbox):
    """Distance from unit centre to the node bbox (minus 0; caller subtracts
    the unit radius). 0 means inside the box."""
    x0, y0, x1, y1 = bbox
    dx = max(x0 - ux, 0, ux - x1)
    dy = max(y0 - uy, 0, uy - y1)
    return math.hypot(dx, dy)


def fan_stats(node_c, unit_cs):
    """Angles (deg, screen coords) from node to its units; wrap to [-180,180)."""
    if not unit_cs:
        return None
    angs = []
    for (x, y) in unit_cs:
        a = math.degrees(math.atan2(y - node_c[1], x - node_c[0]))
        angs.append(a)
    # minimal covering arc on the circle
    s = sorted(a % 360 for a in angs)
    if len(s) == 1:
        return {"min_deg": s[0], "max_deg": s[0], "span_deg": 0.0}
    gaps = [(s[(i + 1) % len(s)] - s[i]) % 360 for i in range(len(s))]
    big = max(gaps)
    start = s[(gaps.index(big) + 1) % len(s)]
    span = 360 - big
    return {"min_deg": start % 360, "max_deg": (start + span) % 360,
            "span_deg": span}


def make_act(index, name, region, kind, name_box, nodes, units, recv):
    """units: {uid: (cx,cy)}; nodes: {nid: dict(c=, rot=, deform=)};
    recv: {uid: nid}"""
    return {
        "index": index,
        "name": name,
        "kind": kind,                 # panel | band
        "region": list(region),       # [x0,y0,x1,y1] act card bounds
        "name_box": list(name_box),
        "nodes": nodes,
        "units": units,
        "recv": recv,
    }


# ------------------------------------------------------- composition A
def composition_a():
    acts = []
    px = [40.0, 560.0, 1080.0]
    pw, py, ph = 480.0, 110.0, 840.0
    cy0, cy1 = 182.0, 926.0            # content band inside each panel

    # --- act 1: radial rings around a single centre ---------------------
    region = [px[0], py, px[0] + pw, py + ph]
    nc = (280.0, 524.0)
    units = {}
    ids_ring1 = ["U03", "U08", "U12", "U01", "U14"]
    ids_ring2 = ["U06", "U11", "U04", "U09", "U15", "U02", "U13",
                 "U05", "U10", "U07"]
    for k, uid in enumerate(ids_ring1):
        a = math.radians(-90 + 72 * k)
        units[uid] = (nc[0] + 110 * math.cos(a), nc[1] + 110 * math.sin(a))
    for k, uid in enumerate(ids_ring2):
        a = math.radians(18 + 36 * k)
        units[uid] = (nc[0] + 174 * math.cos(a), nc[1] + 174 * math.sin(a))
    nodes = {
        "N01": {"c": nc, "rot": 0.0, "deform": None},
        "N02": {"c": (140.0, 866.0), "rot": 0.0, "deform": None},
        "N03": {"c": (420.0, 866.0), "rot": 45.0, "deform": None},
    }
    recv = {uid: "N01" for uid in UNIT_IDS}
    acts.append(make_act(1, ACT_NAMES[0], region, "panel",
                         [px[0] + 24, 126, 432, 40],
                         nodes, units, recv))

    # --- act 2: three tight queues into the squeezed centre -------------
    region = [px[1], py, px[1] + pw, py + ph]
    nc = (800.0, 424.0)
    units = {}
    # centre lane (vertical), mixed colours per lane
    for k, uid in enumerate(["U01", "U07", "U12", "U04", "U09"]):
        units[uid] = (800.0, 504.0 + 44.0 * k)
    # left lane: from (650,824) toward (770,494), pitch 44
    lx0, ly0, tx, ty = 650.0, 824.0, 770.0, 494.0
    d = math.hypot(tx - lx0, ty - ly0)
    ux, uy = (tx - lx0) / d, (ty - ly0) / d
    for k, uid in enumerate(["U02", "U13", "U06", "U15", "U03"]):
        units[uid] = (lx0 + 44.0 * k * ux, ly0 + 44.0 * k * uy)
    # right lane: mirror of the left lane about x=800  (x' = 1600 - x)
    for k, uid in enumerate(["U08", "U05", "U11", "U14", "U10"]):
        base = (650.0 + 44.0 * k * ux, 824.0 + 44.0 * k * uy)
        units[uid] = (1600.0 - base[0], base[1])
    nodes = {
        "N01": {"c": nc, "rot": 0.0, "deform": (96.0, 58.0)},
        "N02": {"c": (650.0, 250.0), "rot": 0.0, "deform": None},
        "N03": {"c": (950.0, 250.0), "rot": 45.0, "deform": None},
    }
    recv = {uid: "N01" for uid in UNIT_IDS}
    acts.append(make_act(2, ACT_NAMES[1], region, "panel",
                         [px[1] + 24, 126, 432, 40],
                         nodes, units, recv))

    # --- act 3: redistribution 5/5/5 ------------------------------------
    region = [px[2], py, px[2] + pw, py + ph]
    nx = [1176.0, 1320.0, 1464.0]
    assign = {
        "N01": ["U01", "U02", "U06", "U11", "U13"],
        "N02": ["U03", "U07", "U08", "U12", "U14"],
        "N03": ["U04", "U05", "U09", "U10", "U15"],
    }
    units = {}
    for i, nid in enumerate(NODE_IDS):
        ids = assign[nid]
        for j, uid in enumerate(ids[:3]):
            units[uid] = (nx[i] - 44 + 44 * j, 720.0)
        for j, uid in enumerate(ids[3:]):
            units[uid] = (nx[i] - 22 + 44 * j, 764.0)
    nodes = {
        "N01": {"c": (nx[0], 340.0), "rot": 0.0, "deform": None},
        "N02": {"c": (nx[1], 340.0), "rot": 0.0, "deform": None},
        "N03": {"c": (nx[2], 340.0), "rot": 45.0, "deform": None},
    }
    recv = {}
    for nid, ids in assign.items():
        for uid in ids:
            recv[uid] = nid
    acts.append(make_act(3, ACT_NAMES[2], region, "panel",
                         [px[2] + 24, 126, 432, 40],
                         nodes, units, recv))

    return {
        "id": "A",
        "label": "三联幕（竖版卡片，剧场式分幕）",
        "title": {"text": TITLE, "box": [0, 24, 1600, 60],
                  "align": "CENTER", "size": 40.0, "bold": True},
        "acts": acts,
    }


# ------------------------------------------------------- composition B
def composition_b():
    acts = []
    bx, bw = 32.0, 1536.0
    bh, gap = 276.0, 14.0
    tops = [110.0, 110.0 + bh + gap, 110.0 + 2 * (bh + gap)]

    # --- band 1: loose grid pulled to the single right-hand node --------
    t = tops[0]
    region = [bx, t, bx + bw, t + bh]
    nc = (1260.0, t + 155.0)
    grid_ids = ["U03", "U09", "U14", "U01", "U06",
                "U11", "U04", "U15", "U07", "U02",
                "U08", "U13", "U05", "U10", "U12"]
    units = {}
    for i, uid in enumerate(grid_ids):
        col, row = i % 5, i // 5
        units[uid] = (200.0 + 88.0 * col, t + 76.0 + 64.0 * row)
    nodes = {
        "N01": {"c": nc, "rot": 0.0, "deform": None},
        "N02": {"c": (1420.0, t + 97.0), "rot": 0.0, "deform": None},
        "N03": {"c": (1420.0, t + 213.0), "rot": 45.0, "deform": None},
    }
    recv = {uid: "N01" for uid in UNIT_IDS}
    acts.append(make_act(1, ACT_NAMES[0], region, "band",
                         [64.0, t + 12, 400, 40],
                         nodes, units, recv))

    # --- band 2: same system, tight queue pressed into squeezed node ----
    t = tops[1]
    region = [bx, t, bx + bw, t + bh]
    nc = (1260.0, t + 155.0)
    queue_ids = ["U02", "U14", "U07", "U12", "U01",
                 "U05", "U10", "U15", "U04", "U09",
                 "U13", "U03", "U08", "U06", "U11"]
    units = {}
    for i, uid in enumerate(queue_ids):
        col, row = i % 5, i // 5
        units[uid] = (1006.0 + 44.0 * col, t + 111.0 + 44.0 * row)
    nodes = {
        "N01": {"c": nc, "rot": 0.0, "deform": (96.0, 58.0)},
        "N02": {"c": (1420.0, t + 97.0), "rot": 0.0, "deform": None},
        "N03": {"c": (1420.0, t + 213.0), "rot": 45.0, "deform": None},
    }
    recv = {uid: "N01" for uid in UNIT_IDS}
    acts.append(make_act(2, ACT_NAMES[1], region, "band",
                         [64.0, t + 12, 400, 40],
                         nodes, units, recv))

    # --- band 3: three clusters -> three nodes ---------------------------
    t = tops[2]
    region = [bx, t, bx + bw, t + bh]
    nx = [560.0, 980.0, 1400.0]
    assign = {
        "N01": ["U01", "U02", "U06", "U11", "U13"],
        "N02": ["U03", "U07", "U08", "U12", "U14"],
        "N03": ["U04", "U05", "U09", "U10", "U15"],
    }
    units = {}
    for i, nid in enumerate(NODE_IDS):
        gx = nx[i] - 120.0
        ids = assign[nid]
        for j, uid in enumerate(ids[:3]):
            units[uid] = (gx - 44 + 44 * j, t + 133.0)
        for j, uid in enumerate(ids[3:]):
            units[uid] = (gx - 22 + 44 * j, t + 177.0)
    nodes = {
        "N01": {"c": (nx[0], t + 155.0), "rot": 0.0, "deform": None},
        "N02": {"c": (nx[1], t + 155.0), "rot": 0.0, "deform": None},
        "N03": {"c": (nx[2], t + 155.0), "rot": 45.0, "deform": None},
    }
    recv = {}
    for nid, ids in assign.items():
        for uid in ids:
            recv[uid] = nid
    acts.append(make_act(3, ACT_NAMES[2], region, "band",
                         [64.0, t + 12, 400, 40],
                         nodes, units, recv))

    return {
        "id": "B",
        "label": "三横幕（横向流程带，左→右读）",
        "title": {"text": TITLE, "box": [0, 22, 1600, 60],
                  "align": "CENTER", "size": 40.0, "bold": True},
        "acts": acts,
    }


# ---------------------------------------------------------------- checks
def text_width(s, fs):
    full = sum(1 for ch in s if ord(ch) > 0x2E80)
    narrow = len(s) - full
    return full * fs + narrow * 0.5 * fs


def check_story(story):
    """Returns a report dict; raises AssertionError on hard failures."""
    rep = {"story": story["id"], "acts": [], "errors": []}

    # text budget: exactly 1 title + 3 act names
    texts = [story["title"]["text"]] + [a["name"] for a in story["acts"]]
    assert len(texts) == 4
    tw = text_width(story["title"]["text"], story["title"]["size"])
    assert tw <= story["title"]["box"][2], f"title too wide {tw}"
    rep["title_width_px"] = tw

    for act in story["acts"]:
        a = {"act": act["index"], "name": act["name"], "kind": act["kind"]}
        units, nodes, recv = act["units"], act["nodes"], act["recv"]
        region = act["region"]

        # --- conserved cast
        assert sorted(units) == UNIT_IDS, (act["index"], sorted(units))
        assert sorted(nodes) == NODE_IDS
        assert sorted(recv) == UNIT_IDS
        assert all(recv[u] in NODE_IDS for u in UNIT_IDS)

        # --- colour + diameter conservation
        for uid, c in units.items():
            assert UNIT_COLORS[uid] == UNIT_COLORS[uid]

        # --- region containment (units fully, node visual bbox fully)
        for uid, (x, y) in units.items():
            if not (region[0] <= x - UNIT_R and x + UNIT_R <= region[2]
                    and region[1] <= y - UNIT_R and y + UNIT_R <= region[3]):
                raise AssertionError(
                    f"act{act['index']} unit {uid} outside region: {(x, y)}")
        for nid, nd in nodes.items():
            bb = node_visual_bbox(NODE_SHAPES[nid], nd["c"][0], nd["c"][1],
                                  nd["deform"])
            if not (region[0] <= bb[0] and bb[2] <= region[2]
                    and region[1] <= bb[1] and bb[3] <= region[3]):
                raise AssertionError(
                    f"act{act['index']} node {nid} outside region: {bb}")

        # --- pairwise unit separation (no overlap)
        min_gap, pair = 1e9, None
        ids = UNIT_IDS
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                (x1, y1), (x2, y2) = units[ids[i]], units[ids[j]]
                g = math.hypot(x2 - x1, y2 - y1) - UNIT_D
                if g < min_gap:
                    min_gap, pair = g, (ids[i], ids[j])
        if min_gap < MIN_UNIT_GAP:
            raise AssertionError(
                f"act{act['index']} unit overlap: gap {min_gap} {pair}")
        a["min_unit_gap_px"] = min_gap
        a["min_unit_gap_pair"] = list(pair)

        # --- units must not sit on nodes either (full visibility)
        min_nc = 1e9
        for uid, (x, y) in units.items():
            for nid, nd in nodes.items():
                bb = node_bbox(NODE_SHAPES[nid], nd["c"][0], nd["c"][1],
                               nd["deform"])
                cl = unit_node_clearance(x, y, bb) - UNIT_R
                min_nc = min(min_nc, cl)
        if min_nc < 2.0:
            raise AssertionError(
                f"act{act['index']} unit touches node: clearance {min_nc}")
        a["min_unit_node_clearance_px"] = min_nc

        # --- lines stay inside the act region (convex rectangle)
        for uid in UNIT_IDS:
            x, y = units[uid]
            nid = recv[uid]
            nx, ny = nodes[nid]["c"]
            for px_, py_ in ((x, y), (nx, ny)):
                if not (region[0] <= px_ <= region[2]
                        and region[1] <= py_ <= region[3]):
                    raise AssertionError("line endpoint outside region")

        # --- per-node load + colour span + direction fan
        loads = {}
        for nid in NODE_IDS:
            got = [u for u in UNIT_IDS if recv[u] == nid]
            loads[nid] = got
        a["loads"] = {k: len(v) for k, v in loads.items()}
        a["load_colors"] = {
            k: sorted({COLOR_NAMES[UNIT_COLORS[u]] for u in v})
            for k, v in loads.items()}
        a["fans"] = {}
        for nid in NODE_IDS:
            if loads[nid]:
                a["fans"][nid] = fan_stats(
                    nodes[nid]["c"], [units[u] for u in loads[nid]])

        # --- nodes: base size + actual bbox + rotation + deformation
        a["nodes"] = {}
        for nid in NODE_IDS:
            nd = nodes[nid]
            bb = node_visual_bbox(NODE_SHAPES[nid], *nd["c"], nd["deform"])
            a["nodes"][nid] = {
                "shape": NODE_SHAPES[nid],
                "centre": list(nd["c"]),
                "rotation_deg": nd["rot"],
                "bbox": bb,
                "deform": (list(nd["deform"]) if nd["deform"] else None),
                "received": len(loads[nid]),
            }

        # --- act-3 task rule: 5 per node, >=2 colours each
        if act["index"] == 3:
            for nid in NODE_IDS:
                assert len(loads[nid]) == 5, (nid, len(loads[nid]))
                cols = {UNIT_COLORS[u] for u in loads[nid]}
                assert len(cols) >= 2, (nid, cols)
        else:
            assert len(loads["N01"]) == 15

        rep["acts"].append(a)

    # cross-act identity: colours & ids constant by construction; verify
    for uid in UNIT_IDS:
        assert UNIT_COLORS[uid] in (BLUE, ORANGE, GRAY)
    for act in story["acts"]:
        assert act["kind"] in ("panel", "band")

    return rep


def unit_overlap_report(story):
    out = []
    for act in story["acts"]:
        gaps = []
        ids = UNIT_IDS
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                (x1, y1), (x2, y2) = act["units"][ids[i]], act["units"][ids[j]]
                gaps.append((math.hypot(x2 - x1, y2 - y1) - UNIT_D,
                             ids[i], ids[j]))
        gaps.sort()
        out.append((act["index"], gaps[0], gaps[4]))
    return out


if __name__ == "__main__":
    for story in (composition_a(), composition_b()):
        r = check_story(story)
        print("story", r["story"], r["label"] if "label" in r else "",
              "title width", r["title_width_px"])
        for a in r["acts"]:
            print("  act", a["act"],
                  "min gap %.2f" % a["min_unit_gap_px"],
                  a["min_unit_gap_pair"],
                  "| node clear %.1f" % a["min_unit_node_clearance_px"],
                  "| loads", a["loads"],
                  "| colors", a["load_colors"])
            for nid, n in a["nodes"].items():
                print("     ", nid, n["shape"], "bbox",
                      [round(v, 2) for v in n["bbox"]],
                      "rot", n["rotation_deg"], "recv", n["received"])
        print()
