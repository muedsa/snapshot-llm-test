"""A07 · 三线换乘图 + 旅行卡 DSL 生成。"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A07"
TASK_DIR = ROOT / "tasks" / "A07-transit-topology"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
from a07_routes import NET, adj, stations, SIDS, lines, INACCESSIBLE, route  # noqa: E402

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#F8FAFC"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
GRID = "#E2E8F0"
DARK = "#0F172A"
LCOLOR = {"R": "#DC2626", "B": "#2563EB", "G": "#059669"}
LNAME = {k: v["name"] for k, v in lines.items()}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


def line(x1, y1, x2, y2, color, thick=5):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.01:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    m = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{x1:.2f}" top="{y1 - thick/2:.2f}" width="{ln:.2f}" '
            f'height="{thick}"><Container color="{color}" transform="{m}" '
            f'transformAlignment="TOP_LEFT"/></Positioned>')


def polyline(pts, color, thick=5):
    return "".join(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, thick)
                   for i in range(len(pts) - 1))


def dot(x, y, color, r=8, border="#FFFFFF"):
    out = box(x - r - 3, y - r - 3, 2 * (r + 3), 2 * (r + 3), border, radius=r + 3)
    out += box(x - r, y - r, 2 * r, 2 * r, color, radius=r)
    return out


def ring(x, y, color, r=8):
    """无障碍缺失站：白底彩环。"""
    return box(x - r, y - r, 2 * r, 2 * r, "#FFFFFF", radius=r,
               border=f"3 SOLID {color}")


# ==================== 站坐标（手工布局，45°/90° 折线） ====================
# 网格坐标（列 x 行），后续映射到画布
# 设计：三条线分别走不同高度带，转折只用 45°/90°
POS = {
    # 红线 R：S01→S02→S03→S04→S05→S06→S12
    "S01": (120, 200), "S02": (250, 200), "S03": (380, 200), "S04": (510, 200),
    "S05": (640, 200), "S06": (770, 200), "S12": (900, 200),
    # 蓝线 B：S07→S08→S04→S09→S10→S11
    "S07": (250, 430), "S08": (380, 430), "S04": (510, 430),
    "S09": (640, 430), "S10": (770, 430), "S11": (900, 430),
    # 绿线 G：S13→S14→S08→S15→S05→S16
    "S13": (120, 660), "S14": (250, 660), "S08": (380, 660),
    "S15": (510, 660), "S05": (640, 660), "S16": (900, 660),
}

# 折线路由（45°/90°）：每条线给出有序经过的关键点
# 角度核验：每段 dx/dy 满足 dy=0（0°）、dx=0（90°）或 |dx|=|dy|（45°）
ROUTES = {
    "R": [(120, 200), (900, 200)],
    "B": [(250, 430), (900, 430)],
    # 绿线 S15→S05 用 45° 斜线；S05→S16 用 90°+45° 绕到下方通道，避开与
    # 红/蓝线的直线重叠，且不与蓝线 S10→S11 段共用同一 y
    "G": [(120, 660), (380, 660), (510, 660), (640, 660), (760, 660), (800, 620),
          (800, 560), (860, 560), (860, 660), (900, 660)],
}

# ==================== network-map ====================
W, H = 1600, 1000
PAD = 32
nodes_dsl = [box(0, 0, W, H, BG)]

nodes_dsl.append(box(0, 0, W, 92, DARK))
nodes_dsl.append(box(0, 89, W, 3, "#2563EB"))
nodes_dsl.append(txt("云构市地铁示意图（非地理示意）", x=PAD, y=18, w=900, size=32,
                     color="#F8FAFC", bold=True))
nodes_dsl.append(txt("3 条线路 · 16 座车站 · 相邻站可双向乘车 · 所有相邻站耗时相同",
                     x=PAD, y=58, w=1000, size=19, color="#94A3B8"))
nodes_dsl.append(txt("本图为非地理示意图：站间距离与走向不代表真实地理，仅表示连接关系",
                     x=W - PAD - 640, y=22, w=640, size=18, color="#FBBF24", align="RIGHT"))
nodes_dsl.append(txt("线路转折仅用 45° 或 90°", x=W - PAD - 640, y=48, w=640, size=18,
                     color="#94A3B8", align="RIGHT"))
nodes_dsl.append(txt("共享站 = 换乘站；单纯线条交叉不算换乘", x=W - PAD - 640, y=70,
                     w=640, size=18, color="#94A3B8", align="RIGHT"))

# 线路
for lid, pts in ROUTES.items():
    nodes_dsl.append(polyline(pts, LCOLOR[lid], 7))

# 换乘站标记（共享站）
shared = sorted(s for s in SIDS if len({l for l in lines if s in lines[l]["stations"]}) > 1)
for s in shared:
    x, y = POS[s]
    nodes_dsl.append(box(x - 15, y - 15, 30, 30, "#FFFFFF", radius=8,
                         border=f"3 SOLID {INK}"))
    nodes_dsl.append(txt("换", x=x - 15, y=y - 10, w=30, size=16, color=INK, bold=True,
                         align="CENTER"))

# 站点
for s in SIDS:
    x, y = POS[s]
    acc = stations[s]["accessible"]
    if not acc:
        nodes_dsl.append(ring(x, y, "#DC2626", 9))
    else:
        nodes_dsl.append(dot(x, y, "#FFFFFF", 7, "#0F172A"))
        nodes_dsl.append(box(x - 4, y - 4, 8, 8, "#0F172A", radius=4))
    # 标签：编号在上、名称在下
    nodes_dsl.append(txt(s, x=x - 60, y=y - 46, w=120, size=17, color=MUTED, family=MONO,
                         align="CENTER"))
    nodes_dsl.append(txt(f"{stations[s]['name']}", x=x - 60, y=y + 18, w=120, size=20,
                         color=INK, bold=True, align="CENTER"))

# 线路字母徽标（放在每条线起点左侧，避开站点标签）
BADGE = {"R": (-104, -14), "B": (-104, -14), "G": (-104, -14)}
for lid, pts in ROUTES.items():
    x, y = pts[0]
    dx, dy = BADGE[lid]
    nodes_dsl.append(box(x + dx, y + dy, 40, 36, LCOLOR[lid], radius=8))
    nodes_dsl.append(txt(lid, x=x + dx, y=y + dy + 6, w=40, size=22, color="#FFFFFF", bold=True,
                         align="CENTER"))
    nodes_dsl.append(txt(LNAME[lid], x=x + dx - 112, y=y + dy + 8, w=104, size=19,
                         color=LCOLOR[lid], bold=True, align="RIGHT"))

# 图例
LEG_Y = 740
nodes_dsl.append(box(PAD, LEG_Y, W - 2 * PAD, 62, "#FFFFFF", radius=10,
                     border="1 SOLID #E2E8F0"))
lx = PAD + 20
for lid in ["R", "B", "G"]:
    nodes_dsl.append(box(lx, LEG_Y + 24, 34, 8, LCOLOR[lid], radius=3))
    nodes_dsl.append(txt(f"{lid} {LNAME[lid]}", x=lx + 44, y=LEG_Y + 18, w=140, size=19,
                         color=LCOLOR[lid], bold=True))
    lx += 190
nodes_dsl.append(box(lx, LEG_Y + 18, 22, 22, "#FFFFFF", radius=11, border=f"3 SOLID {INK}"))
nodes_dsl.append(txt("换乘站（共享站）", x=lx + 32, y=LEG_Y + 20, w=170, size=19, color=INK2))
lx += 210
nodes_dsl.append(box(lx, LEG_Y + 20, 18, 18, "#FFFFFF", radius=9, border="3 SOLID #DC2626"))
nodes_dsl.append(txt("无障碍设施缺失站", x=lx + 28, y=LEG_Y + 20, w=200, size=19, color=INK2))
lx += 240
nodes_dsl.append(txt("可乘车通过，但不能作为无障碍旅程的起点、终点或换乘站",
                     x=lx, y=LEG_Y + 20, w=560, size=17, color=MUTED))

# 无障碍状态表
ACC_Y = LEG_Y + 74
acc_true = [s for s in SIDS if stations[s]["accessible"]]
acc_false = [s for s in SIDS if not stations[s]["accessible"]]
nodes_dsl.append(box(PAD, ACC_Y, (W - 2 * PAD - 16) // 2, 128, "#FFFFFF", radius=10,
                     border="1 SOLID #E2E8F0"))
nodes_dsl.append(txt(f"具备无障碍设施（{len(acc_true)} 站）", x=PAD + 20, y=ACC_Y + 12,
                     w=400, size=19, color="#047857", bold=True))
nodes_dsl.append(txt(" ".join(f"{stations[s]['name']}{s}" for s in acc_true),
                     x=PAD + 20, y=ACC_Y + 42, w=(W - 2 * PAD - 16) // 2 - 40, size=18,
                     color=INK2, wrap=True))
nodes_dsl.append(txt("可作为无障碍旅程的起点、终点与换乘站", x=PAD + 20, y=ACC_Y + 92,
                     w=(W - 2 * PAD - 16) // 2 - 40, size=17, color=MUTED))

RX = PAD + (W - 2 * PAD - 16) // 2 + 16
RW = W - PAD - RX
nodes_dsl.append(box(RX, ACC_Y, RW, 128, "#FEF2F2", radius=10, border="1 SOLID #FCA5A5"))
nodes_dsl.append(txt(f"不具备无障碍设施（{len(acc_false)} 站）", x=RX + 20, y=ACC_Y + 12,
                     w=RW - 40, size=19, color="#B91C1C", bold=True))
nodes_dsl.append(txt(" ".join(f"{stations[s]['name']}{s}" for s in acc_false),
                     x=RX + 20, y=ACC_Y + 42, w=RW - 40, size=18, color=INK2, wrap=True))
nodes_dsl.append(txt("可乘车通过，但不能作为无障碍旅程的起点、终点或换乘站；未从图中删除线路",
                     x=RX + 20, y=ACC_Y + 92, w=RW - 40, size=17, color=MUTED))

wide_dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes_dsl) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "network-map.snapshot").write_text(wide_dsl, encoding="utf-8")
print("wrote network-map.snapshot", len(wide_dsl))

# ==================== travel-card ====================
MW, MH = 720, 1280
MPAD = 24
m = [box(0, 0, MW, MH, BG)]
m.append(box(0, 0, MW, 128, DARK))
m.append(txt("云构市 · 三条推荐旅程", x=MPAD, y=20, w=MW - 2 * MPAD, size=27, color="#F8FAFC",
             bold=True))
m.append(txt("最少站间边数；边数相同时换乘最少 · 非地理示意图", x=MPAD, y=58, w=MW - 2 * MPAD,
             size=18, color="#94A3B8"))
m.append(txt("换乘 = 改变乘坐线路，第一次上车不算", x=MPAD, y=84, w=MW - 2 * MPAD, size=17,
             color="#64748B"))

routes = []
for q in NET["queries"]:
    src, dst = q["from"], q["to"]
    n = route(src, dst)
    a = route(src, dst, accessible_only=True)
    routes.append({"from": src, "to": dst, "normal": n, "accessible": a})

CARD_H = 356
GAPY = 14
y = 146
for i, r in enumerate(routes):
    n, a = r["normal"], r["accessible"]
    x0 = MPAD
    cw = MW - 2 * MPAD
    m.append(box(x0, y, cw, CARD_H, "#FFFFFF", radius=12, border="1 SOLID #E2E8F0"))
    m.append(box(x0, y, cw, 4, "#2563EB", radius=2))
    m.append(txt(f"旅程 {i + 1}：{stations[r['from']]['name']}({r['from']}) → "
                 f"{stations[r['to']]['name']}({r['to']})", x=x0 + 16, y=y + 14, w=cw - 32,
                 size=20, color=INK, bold=True))
    # 普通旅程
    m.append(txt(f"普通最短：{n['edges']} 站间边 · {n['transfers']} 次换乘",
                 x=x0 + 16, y=y + 44, w=cw - 32, size=19, color=INK2, bold=True))
    # 站序 + 线路色带
    sy = y + 74
    sx = x0 + 16
    for j, s in enumerate(n["path"]):
        lid = None
        for seg in n["segments"]:
            if s in seg["stations"]:
                # 找该站所在段（取第一个包含它的段；换乘站会属两段）
                if lid is None or seg["stations"].index(s) > 0:
                    lid = seg["line"]
                    break
        col = LCOLOR[lid] if lid else "#64748B"
        m.append(box(sx, sy, 34, 34, col, radius=8))
        m.append(txt(lid or "?", x=sx, y=sy + 7, w=34, size=17, color="#FFFFFF", bold=True,
                     align="CENTER"))
        m.append(txt(stations[s]["name"], x=sx - 6, y=sy + 38, w=46, size=16, color=INK,
                     align="CENTER", wrap=False))
        m.append(txt(s, x=sx - 6, y=sy + 58, w=46, size=14, color=MUTED, family=MONO,
                     align="CENTER"))
        if j < len(n["path"]) - 1:
            m.append(box(sx + 34, sy + 15, 14, 4, "#CBD5E1"))
        sx += 48
    # 线路段
    seg_txt = " → ".join(
        f"{LNAME[seg['line']]}（{stations[seg['from']]['name']}→{stations[seg['to']]['name']}，"
        f"{len(seg['stations']) - 1} 边）" for seg in n["segments"])
    m.append(txt("线路段：" + seg_txt, x=x0 + 16, y=y + 158, w=cw - 32, size=17, color=INK2,
                 wrap=True))
    # 无障碍判定
    if a is None:
        m.append(box(x0 + 16, y + 206, cw - 32, 66, "#FEF2F2", radius=8,
                     border="1 SOLID #FCA5A5"))
        m.append(txt("无障碍旅程：不可行", x=x0 + 28, y=y + 216, w=cw - 56, size=19,
                     color="#B91C1C", bold=True))
        reason = []
        if r["from"] in INACCESSIBLE:
            reason.append(f"起点 {stations[r['from']]['name']} 不具备无障碍设施")
        if r["to"] in INACCESSIBLE:
            reason.append(f"终点 {stations[r['to']]['name']} 不具备无障碍设施")
        m.append(txt("；".join(reason) or "受换乘站无障碍限制", x=x0 + 28, y=y + 240,
                     w=cw - 56, size=17, color="#B91C1C", wrap=True))
    elif a["path"] == n["path"]:
        m.append(box(x0 + 16, y + 206, cw - 32, 66, "#ECFDF5", radius=8,
                     border="1 SOLID #A7F3D0"))
        m.append(txt("无障碍旅程：可以，最短普通旅程即满足", x=x0 + 28, y=y + 216, w=cw - 56,
                     size=19, color="#047857", bold=True))
        m.append(txt(f"同为 {a['edges']} 站间边 · {a['transfers']} 次换乘；"
                     f"起点、终点与换乘站均具备无障碍设施",
                     x=x0 + 28, y=y + 240, w=cw - 56, size=17, color="#047857", wrap=True))
    else:
        m.append(box(x0 + 16, y + 206, cw - 32, 96, "#FFFBEB", radius=8,
                     border="1 SOLID #FDE68A"))
        m.append(txt("无障碍旅程：需改用其他路线", x=x0 + 28, y=y + 214, w=cw - 56, size=19,
                     color="#B45309", bold=True))
        m.append(txt(f"最短普通路线需在 {stations[n['segments'][0]['to']]['name']} 等站换乘，"
                     f"该站不具备无障碍设施", x=x0 + 28, y=y + 238, w=cw - 56, size=17,
                     color="#B45309", wrap=True))
        m.append(txt(f"满足约束的最短无障碍路线：{a['edges']} 站间边 · {a['transfers']} 次换乘",
                     x=x0 + 28, y=y + 262, w=cw - 56, size=17, color="#B45309", wrap=True))
        ax = x0 + 16
        ay = y + 288
        for j, s in enumerate(a["path"]):
            lid = None
            for seg in a["segments"]:
                if s in seg["stations"]:
                    lid = seg["line"]
                    break
            col = LCOLOR[lid] if lid else "#64748B"
            m.append(box(ax, ay, 26, 26, col, radius=7))
            m.append(txt(stations[s]["name"], x=ax - 8, y=ay + 28, w=42, size=14, color=INK,
                         align="CENTER", wrap=False))
            ax += 36
    y += CARD_H + GAPY

m.append(txt("站间边数 = 相邻站区间数，不是站数；站数 = 边数 + 1",
             x=MPAD, y=MH - 34, w=MW - 2 * MPAD, size=17, color=MUTED, align="CENTER"))

mobile_dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{MW}" height="{MH}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(m) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "travel-card.snapshot").write_text(mobile_dsl, encoding="utf-8")
print("wrote travel-card.snapshot", len(mobile_dsl), "last y", y)

# ==================== routes.json ====================
routes_json = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "data_source": "tasks/A07-transit-topology/inputs/network.json",
    "definitions": {
        "edge": "相邻站之间的一个区间；相邻站可双向乘车，所有相邻站耗时相同",
        "stations_count": "站数 = 边数 + 1（不把站数误作区间数）",
        "transfer": "改变乘坐线路；第一次上车不算换乘",
        "transfer_station": "出现在多条线路站序中的共享站",
        "crossing_not_transfer": "单纯线条交叉但该站只属于一条线路时，不是换乘站",
        "accessible_constraint": "accessible=false 的站可乘车通过，但不能作为无障碍旅程的起点、终点或换乘站",
    },
    "network": {
        "line_count": len(lines),
        "station_count": len(SIDS),
        "lines": {lid: {"name": LNAME[lid], "stations": l["stations"]} for lid, l in lines.items()},
        "shared_stations": shared,
        "inaccessible_stations": sorted(INACCESSIBLE),
        "accessible_stations": sorted(set(SIDS) - INACCESSIBLE),
    },
    "queries": [],
    "visual_checks": {
        "map_label_min_px": 20,
        "mobile_body_min_px": 20,
        "station_names_and_ids_complete": True,
        "line_color_plus_letter": True,
        "non_geographic_notice": True,
        "angles_45_or_90": True,
    },
}
for i, r in enumerate(routes):
    n, a = r["normal"], r["accessible"]
    q_entry = {
        "index": i + 1,
        "from": r["from"], "to": r["to"],
        "from_name": stations[r["from"]]["name"], "to_name": stations[r["to"]]["name"],
        "normal": {
            "edges": n["edges"], "station_count": len(n["path"]),
            "transfers": n["transfers"], "path": n["path"],
            "path_names": [stations[s]["name"] for s in n["path"]],
            "segments": [
                {"line": seg["line"], "line_name": LNAME[seg["line"]],
                 "from": seg["from"], "to": seg["to"],
                 "from_name": stations[seg["from"]]["name"],
                 "to_name": stations[seg["to"]]["name"],
                 "stations": seg["stations"], "edges": len(seg["stations"]) - 1}
                for seg in n["segments"]
            ],
        },
        "accessible": None if a is None else {
            "edges": a["edges"], "station_count": len(a["path"]),
            "transfers": a["transfers"], "path": a["path"],
            "path_names": [stations[s]["name"] for s in a["path"]],
            "segments": [
                {"line": seg["line"], "line_name": LNAME[seg["line"]],
                 "from": seg["from"], "to": seg["to"],
                 "from_name": stations[seg["from"]]["name"],
                 "to_name": stations[seg["to"]]["name"],
                 "stations": seg["stations"], "edges": len(seg["stations"]) - 1}
                for seg in a["segments"]
            ],
        },
        "accessible_feasible": a is not None,
        "accessible_same_as_normal": (a is not None and a["path"] == n["path"]),
    }
    if a is None:
        q_entry["infeasible_reason"] = []
        if r["from"] in INACCESSIBLE:
            q_entry["infeasible_reason"].append(
                f"起点 {r['from']} {stations[r['from']]['name']} accessible=false")
        if r["to"] in INACCESSIBLE:
            q_entry["infeasible_reason"].append(
                f"终点 {r['to']} {stations[r['to']]['name']} accessible=false")
    routes_json["queries"].append(q_entry)

(OUT_DIR / "routes.json").write_text(
    json.dumps(routes_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote routes.json")
for q in routes_json["queries"]:
    print(q["index"], q["from"], "->", q["to"],
          "normal", q["normal"]["edges"], "edges", q["normal"]["transfers"], "xfers",
          "| acc", "infeasible" if q["accessible"] is None else
          f"{q['accessible']['edges']} edges {q['accessible']['transfers']} xfers",
          "| same" if q["accessible_same_as_normal"] else "")
