"""A07 DSL generator: 全网示意图 (1600x1000) + 三条路线旅行卡 (720x1280).

Map geometry comes from solve_map2.py (tmp/<run>/A07/map-geometry.json): every drawn piece is
0/45/90 degrees, shared stations are one node, crossings use separate nodes, and no station
sits on a foreign line. The legend lives in its own bottom band so it cannot cover the map.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A07"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
D = json.load(open(os.path.join(OUT, "routes.json"), encoding="utf-8"))
GEO = json.load(open(os.path.join(TMP, "map-geometry.json"), encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "final"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG, CARD = "#F1F5F9FF", "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
LC = {"R": "#D92D20FF", "B": "#1D4ED8FF", "G": "#0E9F8FFF"}
BADGE = {"R": "#FEE4E2FF", "B": "#DBEAFEFF", "G": "#D1FAE5FF"}
LNAME = {l["id"]: l["name"] for l in D["network"]["lines"]}
ST = {s["id"]: s for s in D["network"]["stations"]}
INACC = set(D["network"]["inaccessible_stations"])
SHARED = D["network"]["interchanges"]
ROUTES = D["routes"]
POS = {k: tuple(v) for k, v in GEO["station_positions"].items()}
PIECES = [(lid, tuple(a), tuple(b)) for lid, a, b in GEO["segments"]]

P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, shadow=None, tl=None, tr=None, bl=None, br=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    for nm, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
        if v:
            a += f' borderRadius{nm}="{v}"'
    if border:
        a += f' border="{border}"'
    if shadow:
        a += f' boxShadow="{shadow}"'
    add(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align="CENTER_LEFT"):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align}">'
            f'<Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


def seg(x0, y0, x1, y1, color, th):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.6:
        return
    ang = math.atan2(dy, dx)
    m11, m12 = math.cos(ang), math.sin(ang)
    m21, m22 = -m12, m11
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    tx = mx - m11 * (length / 2) - m21 * (th / 2)
    ty = my - m12 * (length / 2) - m22 * (th / 2)
    mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
    add(f'<Positioned left="0" top="0"><Transform matrix="{mat}"><Container width="{length:.2f}" '
        f'height="{th}" color="{color}" borderRadius="{th/2}"/></Transform></Positioned>')


def disc(x, y, r, fill, ring=None, ring_w=5):
    box(round(x - r), round(y - r), 2 * r, 2 * r, fill, r, f"{ring_w} SOLID {ring}" if ring else None)


# ==================================================================================
# MAP 1600x1000
# ==================================================================================
W, H = 1600, 1000
add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

box(0, 0, W, 80, NAVY)
box(0, 0, 8, 80, "#0E9F8FFF")
text(40, 6, "虚构城市轨道 · 全网示意图", 30, "#FFFFFFFF", "BOLD")
text(40, 44, "非地理示意图：站间折线只用 45° 与 90°，长度与方位不代表真实距离", 20, "#94A3B8FF")
text(1000, 6, "16 站 · 3 条线路 · 3 个换乘站", 20, "#5EEAD4FF", "BOLD", CJ, 560, "CENTER_RIGHT")
text(1000, 32, "普通线条交叉处不是换乘", 20, "#FBBF24FF", "BOLD", CJ, 560, "CENTER_RIGHT")
text(1000, 56, "线路同时用颜色与字母标识 R / B / G", 20, "#94A3B8FF", "NORMAL", CJ, 560, "CENTER_RIGHT")

for lid, pa, pb in PIECES:
    seg(pa[0], pa[1], pb[0], pb[1], LC[lid], 12)
    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    box(round(mx - 14), round(my - 14), 28, 28, BADGE[lid], 14, f"2 SOLID {LC[lid]}")
    text(round(mx) - 14, round(my) - 12, lid, 19, LC[lid], "BOLD", MONO, 28, "CENTER")

for sid, (x, y) in sorted(POS.items()):
    st = ST[sid]
    shared = sid in SHARED
    disc(x, y, 16, "#FFFFFFFF", "#0F172AFF" if shared else LC[st["lines"][0]], 6 if shared else 4)
    if shared:
        disc(x, y, 7, "#0F172AFF")
    lx = x + 24
    text(lx, y - 30, f"{sid} {st['name']}", 22, INK, "BOLD")
    tag = " · ".join((["换乘"] if shared else []) + (["非无障碍"] if sid in INACC else [])) or "无障碍"
    text(lx, y - 2, tag, 20, "#B42318FF" if (shared or sid in INACC) else "#0B7A6EFF", "BOLD")

box(40, 840, 1520, 92, CARD, 12, f"1 SOLID {LINE}")
text(58, 850, "图例", 22, INK, "BOLD")
lx = 130
for lid in ("R", "B", "G"):
    seg(lx, 872, lx + 46, 872, LC[lid], 10)
    box(lx + 54, 858, 28, 28, BADGE[lid], 14, f"2 SOLID {LC[lid]}")
    text(lx + 61, 860, lid, 19, LC[lid], "BOLD", MONO, 28, "CENTER")
    text(lx + 92, 860, f"{lid} {LNAME[lid]}", 20, INK2)
    lx += 200
disc(lx + 14, 872, 13, "#FFFFFFFF", "#0F172AFF", 6)
disc(lx + 14, 872, 6, "#0F172AFF")
text(lx + 36, 860, "换乘站（共享站）", 20, INK2, "BOLD")
lx += 230
disc(lx + 14, 872, 12, "#FFFFFFFF", "#B42318FF", 5)
text(lx + 36, 860, "非无障碍站", 20, "#B42318FF", "BOLD")
lx += 180
disc(lx + 14, 872, 12, "#FFFFFFFF", "#0B7A6EFF", 5)
text(lx + 36, 860, "无障碍站", 20, "#0B7A6EFF", "BOLD")
text(58, 898, "普通线条交叉处没有站点标记，不构成换乘；只有共享站可以换乘。非无障碍站可以乘车通过，但不能作为无障碍旅程的起点、终点或换乘站。",
     20, MUTED)

text(40, 944, "无障碍站 " + str(D["network"]["accessible_count"]) + " / 16；非无障碍站：" +
     "、".join(f"{s} {ST[s]['name']}" for s in sorted(INACC)) + "（未据此删除任何线路或车站）。", 20, MUTED)
text(40, 970, "换乘站：" + "、".join(f"{s} {ST[s]['name']}" for s in SHARED) +
     "；其中无障碍换乘站：" + "、".join(f"{s} {ST[s]['name']}" for s in D["network"]["accessible_interchanges"]) + "。",
     20, MUTED)
text(1180, 970, "渲染：Snapshot DSL · 1600×1000", 20, MUTED2, "NORMAL", MONO, 380, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')
map_dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
with open(os.path.join(TMP, f"network-map.{VER}.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(map_dsl)

for lid, pa, pb in PIECES:
    dx, dy = abs(pb[0] - pa[0]), abs(pb[1] - pa[1])
    assert dx == 0 or dy == 0 or dx == dy, f"non-octilinear {lid} {pa}->{pb}"
assert not GEO["problems"], "geometry solver reported problems"
assert min(v[1] for v in POS.values()) - 40 > 80, "labels would collide with the header"
assert max(v[1] for v in POS.values()) + 40 < 840, "labels would collide with the legend band"
print("map:", len(map_dsl), "chars | pieces", len(PIECES), "| stations", len(POS))

# ==================================================================================
# TRAVEL CARD 720x1280
# ==================================================================================
P = []
add = P.append
MW, MH = 720, 1280
add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{MW}" height="{MH}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

box(0, 0, MW, 132, NAVY)
box(0, 0, 6, 132, "#0E9F8FFF")
text(28, 12, "虚构城市轨道 · 旅行卡", 28, "#FFFFFFFF", "BOLD")
text(28, 50, "三条普通旅程与无障碍可用性", 22, "#94A3B8FF")
text(28, 82, "换乘 = 改变线路；第一次上车不计换乘", 20, "#FBBF24FF", "BOLD")
text(28, 108, "站间边数 = 相邻站之间的段数（站数 = 边数 + 1）", 20, "#94A3B8FF")

y = 148
for r in ROUTES:
    p, a = r["plain_shortest"], r["accessible_shortest"]
    need = r["needs_accessible_alternative"]
    SEQ = p["station_sequence"]
    COLS, SLOT, X0 = 4, 160, 116
    rows = (len(SEQ) + COLS - 1) // COLS
    # heights derived from the content bands so nothing has to share a row band
    dots_bottom = 120 + (rows - 1) * 52 + 20
    ty = dots_bottom + 14
    # explicit band table so every block has its own row band
    card_h = 372 if need else (348 if rows >= 3 else 300)
    box(20, y, MW - 40, card_h, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A12 NORMAL")
    box(20, y, MW - 40, 6, LC[p["legs"][0]["line"]], tl=12, tr=12)
    text(40, y + 14, f"{r['from']} {r['from_name']} → {r['to']} {r['to_name']}", 24, INK, "BOLD")
    text(40, y + 48, f"{p['edge_count']} 段 · {p['station_count']} 站 · {p['transfer_count']} 次换乘",
         22, "#0B7A6EFF", "BOLD", MONO)

    # station chain: 4 per row, names in their own row so they can never touch the line
    for i, sid in enumerate(SEQ):
        row, col = divmod(i, COLS)
        cx = X0 + col * SLOT
        cy = y + 120 + row * 52
        line = next(lg["line"] for lg in p["legs"] if sid in lg["stations"])
        disc(cx, cy, 11, "#FFFFFFFF", LC[line], 5)
        if i < len(SEQ) - 1 and (i + 1) // COLS == row:
            nxt = SEQ[i + 1]
            ln = next(lg["line"] for lg in p["legs"] if nxt in lg["stations"])
            seg(cx + 11, cy, cx + SLOT - 11, cy, LC[ln], 6)
        text(cx - 74, cy - 38, ST[sid]["name"], 20, INK, "BOLD", CJ, 148, "CENTER")
        if sid in INACC:
            text(cx - 74, cy + 15, "非无障碍", 18, "#B42318FF", "BOLD", CJ, 148, "CENTER")

    text(40, y + ty, "线路段：" + " → ".join(
        f"{lg['line']}({'、'.join(ST[s]['name'] for s in lg['stations'])})" for lg in p["legs"]),
        20, INK2, "NORMAL", CJ, MW - 80, "CENTER_LEFT")
    text(40, y + ty + 26, "换乘站：" + ("无（一线直达）" if not p["transfer_stations"]
                                   else "、".join(f"{s} {ST[s]['name']}" for s in p["transfer_stations"])),
         20, INK2)

    if need and a:
        box(40, y + card_h - 108, MW - 80, 58, "#EFF6FFFF", 8, "1 SOLID #1D4ED8FF")
        tr_names = "、".join(f"{s} {ST[s]['name']}" for s in a["transfer_stations"]) or "一线直达"
        text(56, y + card_h - 102, f"无障碍替代路线：{a['edge_count']} 段 · {a['transfer_count']} 次换乘",
             20, "#1D4ED8FF", "BOLD")
        text(56, y + card_h - 80, f"换乘站：{tr_names}", 20, "#1D4ED8FF", "BOLD")
    if p["accessible_ok"]:
        box(40, y + card_h - 44, MW - 80, 32, "#D1FAE5FF", 8, "1 SOLID #0E9F8FFF")
        text(56, y + card_h - 39, "可作为无障碍旅程：起点、终点、换乘站均为无障碍站。", 20, "#0B7A6EFF", "BOLD")
    else:
        box(40, y + card_h - 44, MW - 80, 32, "#FEE4E2FF", 8, "1 SOLID #D92D20FF")
        bad = [s for s in p["contact_stations"] if s in INACC]
        text(56, y + card_h - 39, "不能作为无障碍旅程：途经 " +
             "、".join(f"{s} {ST[s]['name']}" for s in bad) + " 为非无障碍站。", 20, "#B42318FF", "BOLD")
    y += card_h + 14

box(20, y, MW - 40, 88, NAVY, 12)
text(40, y + 8, "说明", 22, "#5EEAD4FF", "BOLD")
text(40, y + 36, "非无障碍站（S03 书院 / S05 东桥 / S09 花园 / S14 公园）可以", 20, "#E2E8F0FF")
text(40, y + 62, "乘车通过，但不能作为无障碍旅程的起点、终点或换乘站。", 20, "#E2E8F0FF")

add('</Stack>')
add('</Container>')
add('</Snapshot>')
card_dsl = "\n".join(P) + "\n"
with open(os.path.join(TMP, f"travel-card.{VER}.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(card_dsl)
print("card:", len(card_dsl), "chars | content bottom", y + 88)
assert y + 88 <= MH, f"travel card overflows ({y + 88})"
print("travel card budget OK")
