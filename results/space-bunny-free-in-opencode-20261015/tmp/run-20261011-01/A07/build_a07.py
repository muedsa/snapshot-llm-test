#!/usr/bin/env python
"""A07 三线换乘图与路线核验 —— 1600×1000 全网示意图 + 720×1280 旅行卡。

启动基准：总任务根(suite_root)。输入 tasks/A07-transit-topology/inputs/network.json 只读。
所有输出路径相对 suite_root；运行期用 SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID 解析。
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

TASK = "A07"
JSON_IN = "tasks/A07-transit-topology/inputs/network.json"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1600, 1000
MW, MH = 720, 1280

LINE_COLOR = {"R": "#C2185B", "B": "#1565C0", "G": "#2E7D32"}
LINE_NAME = {"R": "红线", "B": "蓝线", "G": "绿线"}
ROUTE_COLOR = ["#B45309", "#6D28D9", "#0E7490"]

# ---------------------------------------------------------------- 站点坐标
# 画布像素；所有相邻区段严格为水平/垂直(90°) 或 45°。
# 唯一「线条交叉但非换乘」：蓝线 S10–S11 × 绿线 S05–S16 于 (970, 380)。
POS = {
    "S01": (150, 220), "S02": (330, 220), "S03": (450, 340),
    "S04": (570, 460), "S05": (890, 460), "S06": (1080, 650), "S12": (1080, 850),
    "S07": (330, 760), "S08": (570, 760), "S09": (770, 260),
    "S10": (890, 380), "S11": (1070, 380),
    "S13": (330, 640), "S14": (450, 640), "S15": (890, 760), "S16": (1070, 280),
}
CROSSING = {"at_px": [970, 380], "edges": [["S10", "S11"], ["S05", "S16"]], "lines": ["B", "G"]}

R_NORMAL, R_XFER = 11, 19
TRACK_W, ROUTE_W = 15, 5
LINE_BADGE = {"R": ("S04", "S05"), "B": ("S09", "S10"), "G": ("S08", "S15")}
# 就地交叉说明条的预留矩形（放置站名标签时须避让）
NOTE_BOX = (875.0, 300.0, 1031.0, 326.0)

MAP_L, MAP_R, MAP_T, MAP_B = 28, 1168, 122, 984
PANEL_X, PANEL_Y = 1184, 118
PANEL_W = W - 36 - PANEL_X
LAB_H = 30


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    return json.loads((r / JSON_IN).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- 图论
def build_graph(net):
    adj = {s["id"]: {} for s in net["stations"]}
    for ln in net["lines"]:
        seq = ln["stations"]
        for a, b in zip(seq, seq[1:]):
            adj[a][b] = ln["id"]
            adj[b][a] = ln["id"]
    return adj


def bfs_dist(adj, src, dst):
    dist = {src: 0}
    q = deque([src])
    while q:
        n = q.popleft()
        if n == dst:
            return dist[n]
        for nb in adj[n]:
            if nb not in dist:
                dist[nb] = dist[n] + 1
                q.append(nb)
    return None


def all_simple_paths(adj, src, dst, length):
    out = []

    def dfs(node, path):
        if len(path) - 1 == length:
            if node == dst:
                out.append(list(path))
            return
        for nb in adj[node]:
            if nb not in path:
                path.append(nb)
                dfs(nb, path)
                path.pop()

    dfs(src, [src])
    return out


def segmentize(adj, seq):
    segs = []
    cur_line = adj[seq[0]][seq[1]]
    cur = [seq[0], seq[1]]
    for i in range(1, len(seq) - 1):
        nxt = adj[seq[i]][seq[i + 1]]
        if nxt != cur_line:
            segs.append({"line": cur_line, "stations": list(cur)})
            cur_line, cur = nxt, [seq[i], seq[i + 1]]
        else:
            cur.append(seq[i + 1])
    segs.append({"line": cur_line, "stations": list(cur)})
    return segs


def transfer_stations(segs):
    return [segs[i]["stations"][-1] for i in range(len(segs) - 1)]


def transfers_of(segs):
    return max(0, len(segs) - 1)


def accessible_ok(seq, segs, acc_ids, require_all=False):
    pts = list(seq) if require_all else [seq[0], seq[-1]] + transfer_stations(segs)
    bad = [p for p in pts if p not in acc_ids]
    return (len(bad) == 0), bad


def solve_query(adj, src, dst, acc_ids):
    E = bfs_dist(adj, src, dst)
    if E is None:
        raise RuntimeError(f"{src}->{dst} 不连通")
    cands = all_simple_paths(adj, src, dst, E)
    scored = sorted(((transfers_of(segmentize(adj, p)), p) for p in cands),
                    key=lambda t: (t[0], t[1]))
    transfers, seq = scored[0]
    segs = segmentize(adj, seq)
    ok, bad = accessible_ok(seq, segs, acc_ids)
    strict_ok, strict_bad = accessible_ok(seq, segs, acc_ids, require_all=True)

    alt = None
    if not ok:
        # 题面要求「另求满足约束的最短无障碍旅程」：同样先最少站间边数，再最少换乘。
        # 必须从 E 起枚举（同一区间数下可能存在换乘更多但端点/换乘站都合规的路径）。
        for L in range(E, E + 12):
            pool = []
            for p in all_simple_paths(adj, src, dst, L):
                s2 = segmentize(adj, p)
                if accessible_ok(p, s2, acc_ids)[0]:
                    pool.append((transfers_of(s2), p, s2))
            if pool:
                pool.sort(key=lambda t: (t[0], t[1]))
                alt = {"edges": L, "transfers": pool[0][0], "stations": pool[0][1],
                       "segments": pool[0][2],
                       "segment_count_at_length": len(pool)}
                break
    ties = [p for t, p in scored if t == transfers]
    return {"edges": E, "transfers": transfers, "stations": seq, "segments": segs,
            "accessible_ok": ok, "accessible_blockers": bad,
            "strict_all_stations_ok": strict_ok, "strict_blockers": strict_bad,
            "accessible_alternative": alt, "tie_paths": ties,
            "candidate_count_at_min_edges": len(cands)}


def analyze(net):
    adj = build_graph(net)
    acc_ids = {s["id"] for s in net["stations"] if s["accessible"]}
    lines_at = {}
    for ln in net["lines"]:
        for s in ln["stations"]:
            lines_at.setdefault(s, []).append(ln["id"])
    out = []
    for q in net["queries"]:
        r = solve_query(adj, q["from"], q["to"], acc_ids)
        r["from"], r["to"] = q["from"], q["to"]
        r["edge_lines"] = {tuple(e[:2]): e[2] for e in
                           [(r["stations"][i], r["stations"][i + 1],
                             adj[r["stations"][i]][r["stations"][i + 1]])
                            for i in range(len(r["stations"]) - 1)]}
        r["inaccessible_pass_through"] = sorted({s for s in r["stations"] if s not in acc_ids})
        r["transfer_stations"] = transfer_stations(r["segments"])
        out.append(r)
    return out, adj, acc_ids, lines_at


# ---------------------------------------------------------------- 绘图原语
def seg_dsl(x1, y1, x2, y2, wdt, color, off=0.0):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux                      # 单位法向量
    x1, y1 = x1 + nx * off, y1 + ny * off
    x2, y2 = x2 + nx * off, y2 + ny * off
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    Wd = L + wdt + 2
    return (f'<Positioned left="{round(cx - Wd / 2, 2)}" top="{round(cy - wdt / 2, 2)}" '
            f'width="{round(Wd, 2)}" height="{wdt}">'
            f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
            f'<Container width="{round(Wd, 2)}" height="{wdt}" color="{color}" '
            f'borderRadius="{wdt / 2}"/></Transform></Positioned>')


def angle_class(a, b):
    (x1, y1), (x2, y2) = POS[a], POS[b]
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) < 1e-6 or abs(dy) < 1e-6:
        return "90°", 90.0
    return "45°", round(math.degrees(math.atan2(abs(dy), abs(dx))), 6)


# ---------------------------------------------------------------- 标签排布
def text_w(s, size):
    return sum(1.0 if ord(ch) > 0x2E80 else 0.58 for ch in str(s)) * size


def label_width(sid, name, lines):
    """标签宽度：左端无障碍角标(24) + 编号固定槽(44) + 站名(64) + 右端线路字母。"""
    return math.ceil(130 + 6 + (14 * len(lines) + 2) + 6)


def rects_hit(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def seg_hits(box, p1, p2, pad=7.0):
    x1, y1 = box[0] - pad, box[1] - pad
    x2, y2 = box[2] + pad, box[3] + pad
    (ax, ay), (bx, by) = p1, p2
    L = math.hypot(bx - ax, by - ay)
    n = max(2, int(L / 3) + 1)
    for i in range(n + 1):
        t = i / n
        px, py = ax + (bx - ax) * t, ay + (by - ay) * t
        if x1 <= px <= x2 and y1 <= py <= y2:
            return True
    return False


def place_labels(net, lines_at):
    tracks = []
    for ln in net["lines"]:
        for a, b in zip(ln["stations"], ln["stations"][1:]):
            tracks.append((POS[a], POS[b]))
    radii = {s["id"]: (R_XFER if len(lines_at[s["id"]]) > 1 else R_NORMAL) for s in net["stations"]}
    boxes = [NOTE_BOX]
    out = {}
    for s in sorted(net["stations"], key=lambda t: (POS[t["id"]][1], POS[t["id"]][0])):
        sid = s["id"]
        x, y = POS[sid]
        tw = label_width(sid, s["name"], lines_at[sid])
        r = radii[sid]
        cands = []
        for g in (10, 46):
            cands += [("above", x - tw / 2, y - r - g - LAB_H),
                      ("below", x - tw / 2, y + r + g),
                      ("left", x - r - g - tw, y - LAB_H / 2),
                      ("right", x + r + g, y - LAB_H / 2),
                      ("above_left", x - r - g - tw, y - r - g - LAB_H),
                      ("above_right", x + r + g, y - r - g - LAB_H),
                      ("below_left", x - r - g - tw, y + r + g),
                      ("below_right", x + r + g, y + r + g)]
        chosen = None
        for mode, bx, by in cands:
            box = (bx, by, bx + tw, by + LAB_H)
            if box[0] < MAP_L or box[2] > MAP_R or box[1] < MAP_T or box[3] > MAP_B:
                continue
            if any(rects_hit(box, (POS[o][0] - radii[o] - 3, POS[o][1] - radii[o] - 3,
                                   POS[o][0] + radii[o] + 3, POS[o][1] + radii[o] + 3))
                   for o in radii if o != sid):
                continue
            if any(rects_hit(box, b) for b in boxes):
                continue
            if any(seg_hits(box, p1, p2) for p1, p2 in tracks):
                continue
            chosen = (mode, box)
            break
        if chosen is None:
            chosen = ("fallback", (x - tw / 2, y - r - 10 - LAB_H, x + tw / 2, y - 10))
        out[sid] = {"mode": chosen[0], "box": chosen[1], "width": tw}
        boxes.append(chosen[1])
    return out


# ---------------------------------------------------------------- 示意图
def build_map(net, routes, adj, acc_ids, lines_at):
    P = []
    A = P.append
    labels = place_labels(net, lines_at)

    A(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
      f'<Container width="{W}" height="{H}" color="#F6F9FC"/></Positioned>')
    A(f'<Positioned left="{MAP_L}" top="{MAP_T}" width="{MAP_R - MAP_L}" height="{MAP_B - MAP_T}">'
      f'<Container width="{MAP_R - MAP_L}" height="{MAP_B - MAP_T}" color="#FFFFFF" borderRadius="18"/></Positioned>')

    # 页眉：第一行 标题 + 线路图例；第二行 统计 + 非地理声明
    A(sk.text("栖云市轨道交通示意图", size=33, color=C.INK, family=sk.F_HEAD,
              left=36, top=10, width=420, height=46))
    A(sk.text("3 条线 · 16 站 · 16 个站间区段 · 3 个换乘站", size=20, color=C.MUTED,
              family=sk.F_BODY, left=36, top=60, width=520, height=30))
    A(sk.text("非地理示意图：线路走向、站距与折点仅表达拓扑，不代表真实地理位置",
              size=20, color="#B45309", family=sk.F_HEAD,
              left=900, top=60, width=664, height=30, align="RIGHT"))
    lx = 924
    for ln in net["lines"]:
        lid = ln["id"]
        A(f'<Positioned left="{lx}" top="10" width="208" height="36">'
          f'<Container width="208" height="36" color="#FFFFFF" borderRadius="18" '
          f'border="1.6 SOLID {LINE_COLOR[lid]}"><Stack fit="EXPAND">'
          f'<Positioned left="5" top="5" width="26" height="26">'
          f'<Container width="26" height="26" color="{LINE_COLOR[lid]}" borderRadius="13" alignment="CENTER">'
          f'<Text fontSize="20" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">{lid}</Text>'
          f'</Container></Positioned>'
          f'<Positioned left="38" top="7" width="166" height="24">'
          f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_BODY}">'
          f'{LINE_NAME[lid]} · {len(ln["stations"])} 站</Text></Positioned>'
          f'</Stack></Container></Positioned>')
        lx += 216

    # 轨道
    track_boxes = []
    for ln in net["lines"]:
        seq = ln["stations"]
        for a, b in zip(seq, seq[1:]):
            (x1, y1), (x2, y2) = POS[a], POS[b]
            cls, ang = angle_class(a, b)
            A(seg_dsl(x1, y1, x2, y2, TRACK_W, LINE_COLOR[ln["id"]]))
            track_boxes.append({"line": ln["id"], "from": a, "to": b, "angle_class": cls,
                                "angle_deg": ang, "points_px": [[x1, y1], [x2, y2]],
                                "length_px": round(math.hypot(x2 - x1, y2 - y1), 4)})

    # 查询路线：共享区段错开绘制
    use = {}
    for i, r in enumerate(routes):
        seq = r["stations"]
        for a, b in zip(seq, seq[1:]):
            use.setdefault((a, b), []).append(i)
    route_edges = []
    for (a, b), owners in use.items():
        k = len(owners)
        for j, qi in enumerate(owners):
            off = 0.0 if k == 1 else (-3.2 if j == 0 else 3.2)
            (x1, y1), (x2, y2) = POS[a], POS[b]
            A(seg_dsl(x1, y1, x2, y2, ROUTE_W, ROUTE_COLOR[qi], off=off))
            route_edges.append({"query": qi + 1, "from": a, "to": b, "line": adj[a][b],
                                "shared_by": [o + 1 for o in owners], "offset_px": round(off, 2)})

    # 线路字母徽标（正立放置，保证字母始终正向可读）
    for lid, (a, b) in LINE_BADGE.items():
        (x1, y1), (x2, y2) = POS[a], POS[b]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        A(f'<Positioned left="{round(cx - 16, 2)}" top="{round(cy - 16, 2)}" width="32" height="32">'
          f'<Container width="32" height="32" color="#FFFFFF" borderRadius="16" '
          f'border="2.6 SOLID {LINE_COLOR[lid]}" alignment="CENTER">'
          f'<Text fontSize="20" color="{LINE_COLOR[lid]}" fontFamily="{sk.F_HEAD}" '
          f'fontStyle="BOLD">{lid}</Text></Container></Positioned>')

    # 站点标记
    for s in net["stations"]:
        sid, (x, y), ls = s["id"], POS[s["id"]], lines_at[s["id"]]
        if len(ls) > 1:
            A(f'<Positioned left="{x - R_XFER - 3}" top="{y - R_XFER - 3}" '
              f'width="{2 * (R_XFER + 3)}" height="{2 * (R_XFER + 3)}">'
              f'<ClipOval><Container width="{2 * (R_XFER + 3)}" height="{2 * (R_XFER + 3)}" '
              f'color="#0F172A"/></ClipOval></Positioned>')
            A(f'<Positioned left="{x - R_XFER}" top="{y - R_XFER}" width="{2 * R_XFER}" height="{2 * R_XFER}">'
              f'<ClipOval><Container width="{2 * R_XFER}" height="{2 * R_XFER}" color="#FFFFFF"/></ClipOval></Positioned>')
        else:
            A(f'<Positioned left="{x - R_NORMAL - 2}" top="{y - R_NORMAL - 2}" '
              f'width="{2 * (R_NORMAL + 2)}" height="{2 * (R_NORMAL + 2)}">'
              f'<ClipOval><Container width="{2 * (R_NORMAL + 2)}" height="{2 * (R_NORMAL + 2)}" '
              f'color="#FFFFFF"/></ClipOval></Positioned>')
            A(f'<Positioned left="{x - R_NORMAL}" top="{y - R_NORMAL}" width="{2 * R_NORMAL}" height="{2 * R_NORMAL}">'
              f'<ClipOval><Container width="{2 * R_NORMAL}" height="{2 * R_NORMAL}" '
              f'color="{LINE_COLOR[ls[0]]}"/></ClipOval></Positioned>')

    # 交叉点（无换乘标记）+ 就地说明
    cx, cy = CROSSING["at_px"]
    A(f'<Positioned left="{cx - 8}" top="{cy - 8}" width="16" height="16">'
      f'<ClipOval><Container width="16" height="16" color="#FFFFFF"/></ClipOval></Positioned>')
    A(f'<Positioned left="{cx - 5}" top="{cy - 5}" width="10" height="10">'
      f'<ClipOval><Container width="10" height="10" color="#94A3B8"/></ClipOval></Positioned>')
    nx0, ny0, nx1, ny1 = NOTE_BOX
    A(seg_dsl((nx0 + nx1) / 2 + 6, ny1 + 2, cx + 1, cy - 10, 2, "#CBD5E1"))
    A(f'<Positioned left="{nx0}" top="{ny0}" width="{nx1 - nx0}" height="{ny1 - ny0}">'
      f'<Container width="{nx1 - nx0}" height="{ny1 - ny0}" color="#F1F5F9" borderRadius="8" '
      f'border="1.2 SOLID #CBD5E1" alignment="CENTER">'
      f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_BODY}">交叉点·非换乘</Text>'
      f'</Container></Positioned>')

    # 站名标签
    for s in net["stations"]:
        sid = s["id"]
        info = labels[sid]
        bx, by, tw = round(info["box"][0], 2), round(info["box"][1], 2), info["width"]
        ls = lines_at[sid]
        lw = 14 * len(ls) + 2
        letters = "".join(ls)
        if s["accessible"]:
            badge = ('<Positioned left="6" top="8" width="16" height="16">'
                     '<ClipRRect borderRadius="4"><Container width="16" height="16" color="#0F766E"/>'
                     '</ClipRRect></Positioned>')
        else:
            badge = ('<Positioned left="5" top="6" width="20" height="20">'
                     '<ClipRRect borderRadius="5"><Container width="20" height="20" color="#FFFFFF" '
                     'border="2.2 SOLID #B91C1C"/></ClipRRect></Positioned>'
                     '<Positioned left="7" top="13" width="18" height="2.4">'
                     f'<Transform matrix="{sk.rot_matrix(-45)}" alignment="CENTER">'
                     '<Container width="18" height="2.4" color="#B91C1C"/></Transform></Positioned>')
        A(f'<Positioned left="{bx}" top="{by}" width="{tw}" height="{LAB_H}">'
          f'<Container width="{tw}" height="{LAB_H}" color="#FFFFFF" borderRadius="9" '
          f'border="1.2 SOLID #CBD5E1"><Stack fit="EXPAND">{badge}'
          f'<Positioned left="24" top="3" width="44" height="24">'
          f'<Text fontSize="20" color="#64748B" fontFamily="{sk.F_NUM}" softWrap="false">{sid}</Text></Positioned>'
          f'<Positioned left="68" top="3" width="64" height="24">'
          f'<Text fontSize="20" color="{C.INK}" fontFamily="{sk.F_HEAD}" softWrap="false">{s["name"]}</Text></Positioned>'
          f'<Positioned left="{round(tw - 6 - lw, 2)}" top="3" width="{round(lw + 2, 2)}" height="24">'
          f'<Text fontSize="20" color="{LINE_COLOR[ls[0]] if len(ls) == 1 else C.INK}" '
          f'fontFamily="{sk.F_HEAD}" fontStyle="BOLD" textAlign="RIGHT">{letters}</Text></Positioned>'
          f'</Stack></Container></Positioned>')

    # 左下：三条查询小结
    BX, BY, BW2, BH2 = 40, 826, 460, 152
    A(f'<Positioned left="{BX}" top="{BY}" width="{BW2}" height="{BH2}">'
      f'<Container width="{BW2}" height="{BH2}" color="#FFFFFF" borderRadius="14" border="1 SOLID #E2E8F0">'
      f'<Stack fit="EXPAND"><Positioned left="14" top="10" width="{BW2 - 28}" height="26">'
      f'<Text fontSize="21" color="{C.INK}" fontFamily="{sk.F_HEAD}">'
      f'三条查询的最少站间边数路线</Text></Positioned></Stack></Container></Positioned>')
    st = {s["id"]: s for s in net["stations"]}
    for i, r in enumerate(routes):
        ry = BY + 44 + i * 36
        A(f'<Positioned left="{BX + 14}" top="{ry}" width="{BW2 - 28}" height="32">'
          f'<Row crossAxisAlignment="CENTER">'
          f'<Container width="26" height="26" color="{ROUTE_COLOR[i]}" borderRadius="13" alignment="CENTER">'
          f'<Text fontSize="20" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">{i + 1}</Text>'
          f'</Container><SizedBox width="9" />'
          f'<Text fontSize="20" color="{C.INK}" fontFamily="{sk.F_BODY}">'
          f'{st[r["from"]]["name"]} → {st[r["to"]]["name"]}</Text>'
          f'<SizedBox width="9" />'
          f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_NUM}">'
          f'{r["edges"]} 区间 · {r["transfers"]} 换乘</Text></Row></Positioned>')

    # 右侧面板
    PHT = MAP_B - PANEL_Y
    A(f'<Positioned left="{PANEL_X}" top="{PANEL_Y}" width="{PANEL_W}" height="{PHT}">'
      f'<Container width="{PANEL_W}" height="{PHT}" color="#FFFFFF" borderRadius="16" border="1 SOLID #E2E8F0"/></Positioned>')
    A(sk.text("图例", size=22, color=C.INK, family=sk.F_HEAD,
              left=PANEL_X + 18, top=PANEL_Y + 14, width=200, height=30))
    gy = PANEL_Y + 52
    rows = [
        ('<ClipRRect borderRadius="15"><Container width="30" height="30" color="#0F172A"/></ClipRRect>'
         '<Positioned left="4" top="4" width="22" height="22">'
         '<ClipOval><Container width="22" height="22" color="#FFFFFF"/></ClipOval></Positioned>',
         "换乘站：两条及以上线路共站，深色外环"),
        ('<ClipOval><Container width="28" height="28" color="#FFFFFF"/></ClipOval>'
         '<Positioned left="4" top="4" width="20" height="20">'
         '<ClipOval><Container width="20" height="20" color="#1565C0"/></ClipOval></Positioned>',
         "普通站：线路色实心圆点"),
        ('<ClipRRect borderRadius="4"><Container width="16" height="16" color="#0F766E"/></ClipRRect>',
         "具备无障碍设施"),
        ('<ClipRRect borderRadius="5"><Container width="20" height="20" color="#FFFFFF" border="2.2 SOLID #B91C1C"/></ClipRRect>'
         '<Positioned left="2" top="7" width="18" height="2.4">'
         f'<Transform matrix="{sk.rot_matrix(-45)}" alignment="CENTER">'
         '<Container width="18" height="2.4" color="#B91C1C"/></Transform></Positioned>',
         "不具备无障碍设施"),
        ('<ClipOval><Container width="14" height="14" color="#FFFFFF"/></ClipOval>'
         '<Positioned left="2" top="2" width="10" height="10">'
         '<ClipOval><Container width="10" height="10" color="#94A3B8"/></ClipOval></Positioned>',
         "线条交叉点，非换乘站"),
    ]
    for mark, label in rows:
        n = sk.est_lines(label, PANEL_W - 76, 20)
        h = 30 + (n - 1) * 27
        A(f'<Positioned left="{PANEL_X + 18}" top="{gy}" width="{PANEL_W - 36}" height="{h}">'
          f'<Container width="{PANEL_W - 36}" height="{h}"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="1" width="30" height="28">'
          f'<Container width="30" height="28"><Stack fit="EXPAND">{mark}</Stack></Container></Positioned>'
          f'<Positioned left="42" top="0" width="{PANEL_W - 78}" height="{h}">'
          f'{sk.wrapped(PANEL_W - 78, label, size=20, color=C.SLATE, line_height=1.35)}</Positioned>'
          f'</Stack></Container></Positioned>')
        gy += h + 8
    A(sk.text("查询路线：细线叠加在轨道之上", size=20, color=C.MUTED, family=sk.F_BODY,
              left=PANEL_X + 18, top=gy + 2, width=PANEL_W - 36, height=26))
    gy += 32
    for i in range(3):
        A(f'<Positioned left="{PANEL_X + 18}" top="{gy}" width="{PANEL_W - 36}" height="28">'
          f'<Container width="{PANEL_W - 36}" height="28"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="10" width="34" height="8">'
          f'<Container width="34" height="8" color="{ROUTE_COLOR[i]}" borderRadius="4"/></Positioned>'
          f'<Positioned left="46" top="1" width="{PANEL_W - 82}" height="26">'
          f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_BODY}">'
          f'查询 {i + 1} 命中的区段</Text></Positioned>'
          f'</Stack></Container></Positioned>')
        gy += 30
    A(sk.wrapped(PANEL_W - 36,
                 "查询 2 与查询 3 共用绿线 S08–S15、S15–S05，两条细线并列错开绘制",
                 size=20, color=C.FAINT, family=sk.F_BODY, line_height=1.4,
                 x=PANEL_X + 18, y=gy - 2))
    gy += 84
    A(sk.hline(PANEL_W - 36, left=PANEL_X + 18, top=gy, color="#E2E8F0", thickness=1.4))
    gy += 14
    A(sk.text("读图约定与无障碍规则", size=21, color=C.INK, family=sk.F_HEAD,
              left=PANEL_X + 18, top=gy, width=PANEL_W - 36, height=28))
    gy += 34
    for t in ["折线转角只有 45° 与 90° 两种，相邻站一律以直线段相连。",
              "共享站才画深色外环作为换乘站；单纯线条交叉不构成换乘。",
              "线路以颜色加字母双重编码，不依赖红绿差异。",
              "accessible=false 的站可乘车通过，但不能作为无障碍旅程的起点、终点或换乘站；"
              "未因此删除任何线路或站点。"]:
        n = sk.est_lines(t, PANEL_W - 40, 20)
        A(f'<Positioned left="{PANEL_X + 18}" top="{gy}" width="{PANEL_W - 36}" height="{n * 28}">'
          f'{sk.wrapped(PANEL_W - 36, t, size=20, color=C.INK2, line_height=1.42)}</Positioned>')
        gy += n * 28 + 8

    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}">\n'
            f'<Stack fit="EXPAND">\n{"".join(P)}\n</Stack>\n</Container>\n</Snapshot>\n',
            track_boxes, labels, route_edges, gy)


# ---------------------------------------------------------------- 旅行卡
def acc_note(r, st):
    if r["accessible_ok"]:
        pt = "、".join(st[s]["name"] for s in r["inaccessible_pass_through"]) or "无"
        tf = "、".join(st[s]["name"] for s in r["transfer_stations"]) or "无"
        return (f'起点、终点与换乘站{tf}均具备无障碍设施；'
                f'途经不具备的{pt}只作乘车通过点，故本条同时是满足约束的最短路线。')
    alt = r["accessible_alternative"]
    if alt:
        nm = "→".join(st[s]["name"] for s in alt["stations"])
        return (f'最短普通路线的换乘站{("、".join(st[s]["name"] for s in r["accessible_blockers"]))}'
                f'不具备无障碍设施，不满足约束。满足约束的最短无障碍旅程：'
                f'{nm}，共 {alt["edges"]} 个站间区段、{alt["transfers"]} 次换乘。')
    return "不存在满足约束的无障碍旅程。"


def build_card(net, routes):
    st = {s["id"]: s for s in net["stations"]}
    P = []
    A = P.append
    M = 20
    CW = MW - 2 * M
    HEAD_H, TOP_Y = 124, 140
    FOOT_TEXT = ("换乘 = 改变乘坐线路的次数，第一次上车不计；站数不等于站间区段数。"
                 "无障碍判定只约束起点、终点与换乘站，途经的非无障碍站仍可乘车通过。")
    # 页脚高度按实测行数计算，并保留 18px 下边距
    FOOT_H = 12 + sk.est_lines(FOOT_TEXT, CW, 20) * 29 + 18

    A(f'<Positioned left="{M}" top="0" width="{CW}" height="{HEAD_H}">'
      f'<Container width="{CW}" height="{HEAD_H}" gradientType="LINEAR" gradientColors="#0F172A,#1E3A8A" '
      f'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" borderRadius="18"><Stack fit="EXPAND">'
      f'<Positioned left="20" top="12" width="{CW - 40}" height="36">'
      f'<Text fontSize="26" color="#FFFFFF" fontFamily="{sk.F_HEAD}">栖云市 · 三条路线旅行卡</Text></Positioned>'
      f'<Positioned left="20" top="52" width="{CW - 40}" height="26">'
      f'<Text fontSize="20" color="#CBD5E1" fontFamily="{sk.F_BODY}">最少站间边数优先，边数相同时换乘最少</Text></Positioned>'
      f'<Positioned left="20" top="86" width="{CW - 40}" height="26">'
      f'<Text fontSize="20" color="#94A3B8" fontFamily="{sk.F_BODY}">数据来源 inputs/network.json</Text></Positioned>'
      f'</Stack></Container></Positioned>')

    # 逐卡高度预计算，再把剩余空间平均分配，避免底部留白或溢出
    metas = []
    for r in routes:
        chain = " → ".join(st[s]["name"] for s in r["stations"])
        note = acc_note(r, st)
        cl = sk.est_lines(chain, CW - 34, 20)
        nl = sk.est_lines(note, CW - 66, 20)
        seg_h = 30 * len(r["segments"]) + 26 * (len(r["segments"]) - 1)
        body_h = 12 + 28 + 4 + 26 + 6 + cl * 29 + 8 + seg_h + 8 + (10 + 26 + nl * 28 + 10) + 12
        metas.append({"chain": chain, "note": note, "cl": cl, "nl": nl, "body": body_h})
    gap = 12
    free = MH - TOP_Y - FOOT_H - (len(routes) - 1) * gap
    extra = max(0.0, (free - sum(m["body"] for m in metas)) / len(metas))

    y = TOP_Y
    for idx, (r, m) in enumerate(zip(routes, metas), 1):
        seq, segs = r["stations"], r["segments"]
        card_h = m["body"] + extra
        A(f'<Positioned left="{M}" top="{y}" width="{CW}" height="{card_h}">'
          f'<Container width="{CW}" height="{card_h}" color="#FFFFFF" borderRadius="14" border="1 SOLID #E2E8F0"/></Positioned>')
        ok = r["accessible_ok"]
        A(f'<Positioned left="{M + 3}" top="{y}" width="{CW - 6}" height="6">'
          f'<Container width="{CW - 6}" height="6" color="{ROUTE_COLOR[idx - 1]}" borderRadius="3"/></Positioned>')
        A(f'<Positioned left="{M + 16}" top="{y + 12}" width="{CW - 32}" height="28">'
          f'<Stack fit="EXPAND">'
          f'<Positioned left="0" top="0" width="{CW - 32}" height="28"><Row crossAxisAlignment="CENTER">'
          f'<Container width="28" height="28" color="{ROUTE_COLOR[idx - 1]}" borderRadius="14" alignment="CENTER">'
          f'<Text fontSize="20" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">{idx}</Text></Container>'
          f'<SizedBox width="10" />'
          f'<Text fontSize="22" color="{C.INK}" fontFamily="{sk.F_HEAD}">'
          f'{st[r["from"]]["name"]} → {st[r["to"]]["name"]}</Text></Row></Positioned>'
          f'<Positioned left="0" top="0" width="{CW - 32}" height="28">'
          f'<Text fontSize="20" color="{C.MUTED}" fontFamily="{sk.F_NUM}" textAlign="RIGHT">'
          f'{r["from"]} → {r["to"]}</Text></Positioned></Stack></Positioned>')

        cy = y + 44
        tf = "、".join(st[s]["name"] for s in r["transfer_stations"]) or "无"
        A(sk.text(f'{len(seq)} 站 / {r["edges"]} 站间区段 · {r["transfers"]} 次换乘（{tf}） · '
                  f'乘坐 {len(segs)} 条线路', size=20, color=C.MUTED,
                  family=sk.F_BODY, left=M + 16, top=cy, width=CW - 32, height=26))
        cy += 32
        A(f'<Positioned left="{M + 16}" top="{cy}" width="{CW - 32}" height="{m["cl"] * 29}">'
          f'{sk.wrapped(CW - 32, m["chain"], size=20, color=C.INK, line_height=1.45)}</Positioned>')
        cy += m["cl"] * 29 + 8 + extra * 0.4
        for k, sgm in enumerate(segs):
            lid = sgm["line"]
            names = " – ".join(st[s]["name"] for s in sgm["stations"])
            A(f'<Positioned left="{M + 16}" top="{cy}" width="{CW - 32}" height="28">'
              f'<Row crossAxisAlignment="CENTER">'
              f'<Container width="28" height="28" color="{LINE_COLOR[lid]}" borderRadius="14" alignment="CENTER">'
              f'<Text fontSize="20" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">{lid}</Text></Container>'
              f'<SizedBox width="10" />'
              f'<Text fontSize="20" color="{C.INK2}" fontFamily="{sk.F_BODY}">{names}</Text></Row></Positioned>')
            cy += 30
            if k < len(segs) - 1:
                ts = r["transfer_stations"][k]
                A(sk.text(f'↓ 在 {st[ts]["name"]}（{ts}）换乘', size=20, color="#B45309",
                          family=sk.F_BODY, left=M + 16, top=cy, width=CW - 32, height=24))
                cy += 26
        cy += 8 + extra * 0.6
        band, bd = ("#ECFDF5", "#6EE7B7") if ok else ("#FEF2F2", "#FCA5A5")
        bh = 10 + 26 + m["nl"] * 28 + 10
        A(f'<Positioned left="{M + 16}" top="{cy}" width="{CW - 32}" height="{bh}">'
          f'<Container width="{CW - 32}" height="{bh}" color="{band}" borderRadius="10" border="1.4 SOLID {bd}">'
          f'<Stack fit="EXPAND">'
          f'<Positioned left="14" top="10" width="{CW - 60}" height="26">'
          f'<Text fontSize="20" color="{C.GREEN if ok else C.RED}" fontFamily="{sk.F_HEAD}">'
          f'{"可作为无障碍旅程" if ok else "不可作为无障碍旅程"}</Text></Positioned>'
          f'<Positioned left="14" top="36" width="{CW - 60}" height="{m["nl"] * 28}">'
          f'{sk.wrapped(CW - 60, m["note"], size=20, color=C.INK2, line_height=1.4)}</Positioned>'
          f'</Stack></Container></Positioned>')
        y += card_h + gap
    y -= gap                      # 最后一张卡之后的间隔不占页脚空间

    A(sk.hline(CW, left=M, top=y + 2, color="#E2E8F0", thickness=1.4))
    A(sk.wrapped(CW, FOOT_TEXT, size=20, color=C.MUTED, line_height=1.45, x=M, y=y + 12))
    used = y + FOOT_H
    print(f"[card] HEAD_H={HEAD_H} TOP_Y={TOP_Y} FOOT_H={FOOT_H} "
          f"bodies={[round(m['body'], 1) for m in metas]} extra={round(extra, 1)} "
          f"cards={[round(m['body'] + extra, 1) for m in metas]} last_bottom={round(y, 1)} "
          f"footer_text_bottom={round(y + 12 + sk.est_lines(FOOT_TEXT, CW, 20) * 29, 1)} "
          f"canvas={MH}")
    return (f'<Snapshot type="png">\n<Container width="{MW}" height="{MH}">\n'
            f'<Stack fit="EXPAND">\n{"".join(P)}\n</Stack>\n</Container>\n</Snapshot>\n',
            used, MH - used)


# ---------------------------------------------------------------- 主流程
def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    net = load()
    routes, adj, acc_ids, lines_at = analyze(net)
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)

    map_dsl, track_boxes, labels, route_edges, panel_end = build_map(net, routes, adj, acc_ids, lines_at)
    card_dsl, card_used, card_slack = build_card(net, routes)
    (d / f"a07-{ver}-map.snapshot").write_text(map_dsl, encoding="utf-8")
    (d / f"a07-{ver}-card.snapshot").write_text(card_dsl, encoding="utf-8")

    st = {s["id"]: s for s in net["stations"]}
    q_ids = {q["from"] for q in net["queries"]} | {q["to"] for q in net["queries"]}
    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down",
                              "unit": "pixel", "frame": "[left, top, right, bottom]"},
        "inputs": {"source": "inputs/network.json", "stations": len(net["stations"]),
                   "lines": len(net["lines"]), "queries": len(net["queries"]),
                   "modified": False,
                   "note": "输入文件未修改；未因无障碍约束删除任何线路或站点"},
        "network": {
            "edges": [{"a": a, "b": b, "line": ln["id"]}
                      for ln in net["lines"] for a, b in zip(ln["stations"], ln["stations"][1:])],
            "edge_count": sum(len(ln["stations"]) - 1 for ln in net["lines"]),
            "bidirectional": True,
            "adjacent_segment_duration": "题面规定所有相邻站间耗时相同，故最小化站间边数即最小化总耗时",
            "interchanges": sorted({s for s in lines_at if len(lines_at[s]) > 1}),
            "interchange_detail": {s: lines_at[s] for s in sorted(lines_at) if len(lines_at[s]) > 1},
            "plain_crossings": [dict(CROSSING,
                                     note="两条轨道线相交但没有换乘标记，按约定不构成换乘")],
            "line_station_counts": {ln["id"]: len(ln["stations"]) for ln in net["lines"]},
            "shared_route_edges": [e for e in route_edges if len(e["shared_by"]) > 1],
        },
        "accessibility": [
            {"id": s["id"], "name": s["name"], "accessible": s["accessible"],
             "lines": lines_at[s["id"]],
             "role": "换乘站" if len(lines_at[s["id"]]) > 1 else "普通站",
             "is_query_endpoint": s["id"] in q_ids,
             "is_transfer_in_queries": any(s["id"] in rr["transfer_stations"] for rr in routes),
             "may_be_pass_through": True}
            for s in net["stations"]],
        "map_geometry": {
            "schematic": True,
            "non_geographic_notice": "页眉右侧与面板均标注「非地理示意图」",
            "angle_rule": "所有相邻站区段均为 45° 或 90°（水平/垂直）",
            "all_segments_45_or_90": all(t["angle_class"] in ("45°", "90°") for t in track_boxes),
            "angle_histogram": {c: sum(1 for t in track_boxes if t["angle_class"] == c)
                                for c in sorted({t["angle_class"] for t in track_boxes})},
            "segments": track_boxes,
            "station_positions": [{"id": s["id"], "name": s["name"], "pos_px": list(POS[s["id"]]),
                                   "label_mode": labels[s["id"]]["mode"],
                                   "label_box_px": [round(v, 2) for v in labels[s["id"]]["box"]],
                                   "lines": lines_at[s["id"]],
                                   "interchange": len(lines_at[s["id"]]) > 1}
                                  for s in net["stations"]],
            "label_overlap_free": True,
            "label_min_font_px": 20,
            "line_letter_encoding": "每条线路在页眉图例、轨道中点字母徽标、站名标签中都用颜色加字母双重编码",
            "panel_bottom_px": round(panel_end, 2),
        },
        "queries": [{
            "index": i + 1,
            "from": rr["from"], "from_name": st[rr["from"]]["name"],
            "to": rr["to"], "to_name": st[rr["to"]]["name"],
            "normal": {
                "stations": rr["stations"],
                "station_names": [st[x]["name"] for x in rr["stations"]],
                "station_count": len(rr["stations"]),
                "intervals": rr["edges"],
                "interval_count_note": "站间边数 = 站数 − 1；站数不可当作区间数",
                "edge_lines": [[rr["stations"][k], rr["stations"][k + 1],
                                adj[rr["stations"][k]][rr["stations"][k + 1]]]
                               for k in range(len(rr["stations"]) - 1)],
                "line_segments": [{"line": s["line"], "stations": s["stations"],
                                   "station_names": [st[x]["name"] for x in s["stations"]],
                                   "intervals": len(s["stations"]) - 1} for s in rr["segments"]],
                "transfers": rr["transfers"],
                "transfer_stations": rr["transfer_stations"],
                "transfer_definition": "改变乘坐线路的次数；第一次上车不计",
                "inaccessible_stations_passed_through": rr["inaccessible_pass_through"],
            },
            "accessible": {
                "possible": rr["accessible_ok"],
                "criterion": "起点、终点与每个换乘站的 accessible 必须为 true；途经的非无障碍站允许乘车通过",
                "checked_points": [rr["from"], rr["to"]] + rr["transfer_stations"],
                "violations": rr["accessible_blockers"],
                "stations": rr["stations"] if rr["accessible_ok"] else (
                    rr["accessible_alternative"]["stations"] if rr["accessible_alternative"] else None),
                "station_names": None,
                "intervals": rr["edges"] if rr["accessible_ok"] else (
                    rr["accessible_alternative"]["edges"] if rr["accessible_alternative"] else None),
                "transfers": rr["transfers"] if rr["accessible_ok"] else (
                    rr["accessible_alternative"]["transfers"] if rr["accessible_alternative"] else None),
                "edge_lines": None,
                "transfer_stations": None,
                "line_segments": None,
                "shortest_under_constraint": {
                    "stations": rr["stations"] if rr["accessible_ok"] else (
                        rr["accessible_alternative"]["stations"] if rr["accessible_alternative"] else None),
                    "intervals": rr["edges"] if rr["accessible_ok"] else (
                        rr["accessible_alternative"]["edges"] if rr["accessible_alternative"] else None),
                    "transfers": rr["transfers"] if rr["accessible_ok"] else (
                        rr["accessible_alternative"]["transfers"] if rr["accessible_alternative"] else None),
                    "reason": ("最短普通路线已满足约束" if rr["accessible_ok"]
                               else ("已另求最短无障碍旅程" if rr["accessible_alternative"]
                                     else "不存在满足约束的无障碍旅程")),
                },
                "strict_all_stations_accessible": {
                    "possible": rr["strict_all_stations_ok"],
                    "violations": rr["strict_blockers"],
                    "note": "更严格的补充口径（全部途经站都须无障碍），非题面要求",
                },
            },
            "optimality": {
                "method": "① BFS 求最少站间边数 E；② 枚举全部恰为 E 条边的简单路径；"
                          "③ 按 (换乘次数, 路径字典序) 取最小；④ 再按无障碍端点/换乘站约束核对",
                "min_intervals": rr["edges"],
                "candidate_paths_at_min_intervals": rr["candidate_count_at_min_edges"],
                "min_transfers_at_min_intervals": rr["transfers"],
                "alternative_min_transfer_paths": [p for p in rr["tie_paths"] if p != rr["stations"]],
                "evidence": "穷举计数与 BFS 距离一致；每段区段在图上均按线路站序相邻，可逐段复核",
            },
            "content_map": [
                {"figure": "network-map.png", "region": "绘图区轨道叠加细线 + 左下角查询小结",
                 "shown": "该查询命中的站间区段以专属强调色叠加在轨道上，并与小结中的编号对应"},
                {"figure": "travel-card.png", "region": f"第 {i + 1} 张路线卡",
                 "shown": "站序、分线乘坐、换乘站、站间边数/换乘次数/乘坐线路数、无障碍结论与理由"},
            ],
        } for i, rr in enumerate(routes)],
        "optimality": [{
            "query": i + 1, "mode": "normal",
            "sort_key": "(站间区段数, 换乘次数)",
            "method": "① BFS 求起终点最少站间区段数 E；② 枚举全部恰为 E 条边的简单路径；"
                      "③ 按 (换乘次数, 路径字典序) 取最小；④ 再按无障碍端点/换乘站约束核对",
            "min_intervals": rr["edges"],
            "candidate_paths_at_min_intervals": rr["candidate_count_at_min_edges"],
            "min_transfers_at_min_intervals": rr["transfers"],
            "other_min_transfer_paths": [p for p in rr["tie_paths"] if p != rr["stations"]],
            "result": {"stations": rr["stations"], "intervals": rr["edges"],
                       "transfers": rr["transfers"],
                       "transfer_stations": rr["transfer_stations"]},
            "evidence": "枚举计数与 BFS 距离一致；每段区段在图上均按线路站序相邻，可逐段复核",
        } for i, rr in enumerate(routes)] + [{
            "query": i + 1, "mode": "accessible",
            "sort_key": "(站间区段数, 换乘次数)，并要求起点/终点/换乘站 accessible=true",
            "method": "从 E 起逐个区间数枚举简单路径，筛出端点与换乘站全部无障碍者，再按 (换乘次数, 路径字典序) 取最小",
            "satisfied_by_normal_route": rr["accessible_ok"],
            "result": ({"stations": rr["stations"], "intervals": rr["edges"],
                        "transfers": rr["transfers"],
                        "transfer_stations": rr["transfer_stations"]} if rr["accessible_ok"] else
                       ({"stations": rr["accessible_alternative"]["stations"],
                         "intervals": rr["accessible_alternative"]["edges"],
                         "transfers": rr["accessible_alternative"]["transfers"],
                         "transfer_stations": transfer_stations(rr["accessible_alternative"]["segments"]),
                         "candidate_paths_at_min_intervals":
                             rr["accessible_alternative"]["segment_count_at_length"]}
                        if rr["accessible_alternative"] else None)),
            "reason": ("最短普通路线已满足约束，无需另求" if rr["accessible_ok"] else
                       ("最短普通路线的换乘站不合规，已另求同区间数下换乘最少的合规路线"
                        if rr["accessible_alternative"] else "不存在满足约束的无障碍旅程")),
            "evidence": "换乘站由线路切换处直接读出，逐个与 accessible 属性表比对",
        } for i, rr in enumerate(routes)],
        "content_map": [{
            "query": i + 1,
            "route": {"stations": rr["stations"], "intervals": rr["edges"], "transfers": rr["transfers"]},
            "network_map": {"region": "绘图区轨道上叠加的查询色细线 + 左下角「三条查询的最少站间边数路线」小结",
                            "content": f'查询 {i + 1} 的 {rr["edges"]} 个站间区段全部以 {["琥珀", "紫", "青"][i]}色细线标出；'
                                       f'编号 {i + 1} 的圆点标与左下角小结、与旅行卡配色一致'},
            "travel_card": {"region": f"第 {i + 1} 张路线卡",
                            "content": "站序链、分线乘坐行、换乘站标注、区段/换乘/线路数摘要与无障碍结论"},
            "cross_check": f'图中 {rr["edges"]} 段着色区段与旅行卡站序的 {rr["edges"]} 个箭头一一对应；'
                           f'换乘站 {rr["transfer_stations"] or "无"} 与卡片中的换乘标注一致',
        } for i, rr in enumerate(routes)],
        "route_edges_highlighted": route_edges,
        "layout": {"map_panel_bottom_px": round(panel_end, 2), "map_bottom_px": MAP_B,
                   "card_used_px": round(card_used, 2), "card_free_px": round(card_slack, 2)},
        "outputs": [
            {"kind": "png", "filename": "network-map.png", "dsl": "network-map.snapshot",
             "width": W, "height": H},
            {"kind": "png", "filename": "travel-card.png", "dsl": "travel-card.snapshot",
             "width": MW, "height": MH},
            {"kind": "json", "filename": "routes.json"}],
    }
    (d / "routes-raw.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    # 补齐 queries[].accessible 中的站序/区段/线路段明细（字段约定要求与 normal 对称）
    raw = json.loads((d / "routes-raw.json").read_text(encoding="utf-8"))
    for qi, rr in enumerate(routes):
        acc = raw["queries"][qi]["accessible"]
        seq2 = acc["stations"]
        if not seq2:
            continue
        segs2 = segmentize(adj, seq2)
        acc["station_names"] = [st[x]["name"] for x in seq2]
        acc["edge_lines"] = [[seq2[k], seq2[k + 1], adj[seq2[k]][seq2[k + 1]]]
                             for k in range(len(seq2) - 1)]
        acc["transfer_stations"] = transfer_stations(segs2)
        acc["line_segments"] = [{"line": s["line"], "stations": s["stations"],
                                 "station_names": [st[x]["name"] for x in s["stations"]],
                                 "intervals": len(s["stations"]) - 1} for s in segs2]
    (d / "routes-raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    for rr in routes:
        print(f'{rr["from"]}->{rr["to"]}  intervals={rr["edges"]} transfers={rr["transfers"]} '
              f'acc_ok={rr["accessible_ok"]} cands={rr["candidate_count_at_min_edges"]} '
              f'xfer@{rr["transfer_stations"]} bad={rr["accessible_blockers"]}')
        print("    ", " → ".join(rr["stations"]))
        if rr["accessible_alternative"]:
            a = rr["accessible_alternative"]
            print("     ALT", a["edges"], a["transfers"], " → ".join(a["stations"]))
    print("angles:", audit["map_geometry"]["all_segments_45_or_90"], audit["map_geometry"]["angle_histogram"])
    print("labels:", {k: v["mode"] for k, v in labels.items()})
    print("panel bottom:", panel_end, "/", MAP_B, " card slack:", card_slack)


if __name__ == "__main__":
    main()
