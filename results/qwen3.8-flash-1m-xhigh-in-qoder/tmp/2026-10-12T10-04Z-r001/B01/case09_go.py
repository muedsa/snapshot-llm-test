"""B01 case-09 - 叠光围棋社 角上死活解说图 (1200x1200, 和纸 + 木纹棋盘).

Scenario: an amateur 3-dan student re-reading a corner life-and-death lesson after class.
The verdict printed on the plate is not folklore: a small Go rules engine (groups,
liberties, captures, suicide ban) enumerates *every* legal way the enclosed points can be
filled, and "死 / 活" is whatever that enumeration shows. The three diagrams, the counts
and the conclusions all come out of the same engine.

Run:  python tmp/<run_id>/B01/case09_go.py
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1200, 1200
PAPER, BOARD, BOARD_D = "#F2ECDF", "#E4C893", "#D8B87E"
INK, INK2, INK3 = "#23252C", "#4A4740", "#6E6A60"
RED, GREEN, BLUE = "#A83224", "#2E6B4F", "#2F5DA8"
STONE_B, STONE_W = "#22242A", "#FBF8F1"
LETTERS = "abcdefghj"        # Go convention: no "i"

# ---- positions on an unbounded grid; the drawings crop the corner ------------------
SPACE_SQ = [(0, 0), (1, 0), (0, 1), (1, 1)]                       # 方四
WALL_SQ = [(2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
OUT_SQ = [(3, 0), (3, 1), (3, 2), (2, 3), (1, 3), (0, 3)]
SPACE_3 = [(0, 0), (1, 0), (2, 0)]                                # 直三
WALL_3 = [(3, 0), (3, 1), (2, 1), (1, 1), (0, 1)]
OUT_3 = [(4, 0), (4, 1), (4, 2), (3, 2), (2, 2), (1, 2), (0, 2), (0, 3)]


def position(space, wall, out):
    b = {p: "B" for p in wall}
    b.update({p: "W" for p in out})
    return b


def neighbours(p):
    """The drawn crop is the board corner, so x<0 / y<0 do not exist."""
    x, y = p
    return [(q, w) for q, w in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            if q >= 0 and w >= 0]


def group(bd, start):
    col, seen, stack = bd[start], {start}, [start]
    while stack:
        p = stack.pop()
        for q in neighbours(p):
            if bd.get(q) == col and q not in seen:
                seen.add(q)
                stack.append(q)
    return seen


def liberties(bd, grp):
    out = set()
    for p in grp:
        for q in neighbours(p):
            if q not in bd:
                out.add(q)
    return out


def play(bd, p, col):
    """Place a stone, clear enemy groups without liberties, reject suicide."""
    if p in bd:
        return None
    nb = dict(bd)
    nb[p] = col
    captured = 0
    for q in neighbours(p):
        if nb.get(q) and nb[q] != col:
            g = group(nb, q)
            if not liberties(nb, g):
                captured += len(g)
                for r in g:
                    del nb[r]
    if not liberties(nb, group(nb, p)) and not captured:
        return None                                   # suicide is illegal
    return nb, captured


def diagonals(p):
    x, y = p
    return [(x + a, y + b) for a in (-1, 1) for b in (-1, 1) if x + a >= 0 and y + b >= 0]


def areas(bd, at):
    """(eye regions, true eyes) for the group at `at`: each liberty expands into the
    whole empty area around it; an area is a true eye only if every diagonal of every
    one of its points is owned by the group or lies inside the same area."""
    grp = group(bd, at)
    col = bd[at]
    libs = liberties(bd, grp)
    seen, eyes, regions = set(), 0, 0
    for p in sorted(libs):
        if p in seen:
            continue
        comp, stack, leaked = set(), [p], False
        while stack:
            q = stack.pop()
            if q in comp:
                continue
            comp.add(q)
            if len(comp) > 40:
                leaked = True
            stack += [r for r in neighbours(q) if r not in bd and r not in comp]
        seen |= comp & libs
        regions += 1
        # a diagonal that is empty but outside this area makes it a false eye
        if not leaked and all(d in comp or (bd.get(d) == col and d in grp)
                              for q in comp for d in diagonals(q)):
            eyes += 1
    return regions, eyes


def eye_regions(bd, at):
    return areas(bd, at)[1]


def region_count(bd, at):
    return areas(bd, at)[0]


def enclosed(bd, grp, cap=40):
    """Empty points reachable from the group's liberties; None if it leaks outside."""
    seen, stack = set(), sorted(liberties(bd, grp))
    while stack:
        q = stack.pop()
        if q in seen:
            continue
        seen.add(q)
        if len(seen) > cap:
            return None
        stack += [r for r in neighbours(q) if r not in bd and r not in seen]
    return sorted(seen)


def solve(bd, black_at, first):
    """Exhaustive search: every legal order of filling the enclosed points."""
    space = enclosed(bd, group(bd, black_at))
    assert space, "the group is not enclosed"
    seqs, alive, dead, other, illegal = [], 0, 0, 0, 0
    order = "BW" if first == "B" else "WB"

    def walk(state, depth, path):
        nonlocal alive, dead, other, illegal
        black = [q for q in state if state[q] == "B"]
        if not black:
            dead += 1
            seqs.append((path, "死"))
            return
        n = eye_regions(state, black[0])
        if n >= 2:
            alive += 1
            seqs.append((path, "活"))
            return
        if depth >= len(space) + 2:
            other += 1
            seqs.append((path, f"真眼 {n} 个"))
            return
        col = order[depth % 2]
        for q in space:
            if q in state:
                continue
            r = play(state, q, col)
            if r:
                walk(r[0], depth + 1, path + [(q, col)])
            else:
                illegal += 1

    walk(bd, 0, [])
    return {"space": [list(q) for q in space], "total": alive + dead + other,
            "alive": alive, "dead": dead, "other": other, "illegal_moves": illegal,
            "paths": [[[(f"{a}{b}", c) for (a, b), c in path], verdict]
                      for path, verdict in seqs]}


def board_draw(s, bd, x0, y0, cell, n, numbers=None, r=None, labels=True):
    r = r or cell * 0.44
    span = (n - 1) * cell
    s.rect(x0 - cell * 0.55, y0 - cell * 0.55, span + cell * 1.1, span + cell * 1.1,
           BOARD, radius=6, border=f"2 SOLID {BOARD_D}")
    for k in range(n):
        s.line(x0, y0 + k * cell, x0 + span, y0 + k * cell, "#8A6B3A", 1.4)
        s.line(x0 + k * cell, y0, x0 + k * cell, y0 + span, "#8A6B3A", 1.4)
    for (gx, gy) in [(3, 3), (6, 3), (3, 6), (6, 6), (n // 2, n // 2)]:
        if gx < n and gy < n:
            s.dot(x0 + gx * cell, y0 + gy * cell, 3.4, "#8A6B3A")
    if labels:
        for k in range(n):
            s.text("cl", LETTERS[k], x0 + k * cell, y0 - cell * 0.98, 20, INK3,
                   align="center", font=MONO)
            s.text("rw", str(n - k), x0 - cell * 1.05, y0 + k * cell - 10, 20, INK3,
                   align="right", font=MONO)
    for p, col in bd.items():
        if p[0] >= n or p[1] >= n:
            continue
        cx, cy = x0 + p[0] * cell, y0 + p[1] * cell
        s.dot(cx, cy, r, STONE_B if col == "B" else STONE_W,
              ring="#8A6B3A" if col == "W" else None, ring_w=1.5)
        s.dot(cx - r * 0.32, cy - r * 0.36, r * 0.2,
              "#4A4E58" if col == "B" else "#E3DED2")
        if numbers and p in numbers:
            s.text("mv", str(numbers[p]), cx, cy - 10, 20,
                   STONE_W if col == "B" else STONE_B, align="center", font=MONO)


def build():
    sq_bd = position(SPACE_SQ, WALL_SQ, OUT_SQ)
    sq_grp = group(sq_bd, (2, 1))
    sq_regions = eye_regions(sq_bd, (2, 1))
    sq_libs = sorted(liberties(sq_bd, sq_grp))
    assert sq_regions == 1 and region_count(sq_bd, (2, 1)) == 1 and len(sq_libs) == 3,         (sq_regions, sq_libs)
    sq = solve(sq_bd, (2, 1), "B")
    assert len(sq["space"]) == 4, sq["space"]
    assert sq["alive"] == 0 and sq["dead"] == 16 and sq["other"] == 0, sq

    base = position(SPACE_3, WALL_3, OUT_3)
    s3 = solve(base, (3, 0), "B")
    a1 = play(base, (1, 0), "B")[0]                       # black takes the middle
    a1_regions = eye_regions(a1, (1, 0))
    a1_space = sorted(liberties(a1, group(a1, (1, 0))))
    assert a1_regions == 2 and region_count(a1, (1, 0)) == 2, a1_regions
    b1 = play(base, (0, 0), "B")[0]                       # black takes an end
    b2 = play(b1, (1, 0), "W")[0]                         # white points the middle
    b3 = play(b2, (2, 0), "B")[0]                         # black captures one
    assert eye_regions(b3, (0, 0)) == 1, b3
    doomed = sorted(group(b3, (0, 0)))                     # the whole black corner
    kill = play(b3, (1, 0), "W")
    assert kill and kill[1] == len(doomed), (kill, doomed)
    b_final, b_caps = kill
    assert not any(v == "B" for v in b_final.values())

    s = Sheet(W, H, min_font=20, bg=PAPER)
    s.text("brand", "叠光围棋社 · 死活讲堂 NO.09", 56, 40, 22, BLUE, bold=True, font=MONO)
    s.text("title", "角上眼位：方四为什么一定是死棋", 56, 72, 40, INK, bold=True)
    s.text("sub", "局部图（主图 7×7，变化图 6×6）· 黑棋外气为 0 · 结论由穷举填子次序得出",
           56, 140, 22, INK3)

    board_draw(s, sq_bd, 132, 252, 64, 7, r=27)
    for p in [tuple(q) for q in sq["space"]]:             # mark the enclosed points
        cx, cy = 132 + p[0] * 52, 252 + p[1] * 52
        s.rect(cx - 9, cy - 9, 18, 18, "#00000000", border=f"2.5 SOLID {RED}",
               radius=3)
    endm = s.para("m1", f"主图：黑 {len(sq_grp)} 子围住 {len(sq['space'])} 个空点（红框）· "
                        f"外气 0 · 真眼仅 {sq_regions} 个，不足两眼 → 死。",
                  56, 716, 20, INK, bold=True, width=620)
    assert endm - 8 <= 790, endm   # para() returns the next line top

    # ---- right column: the verdict, computed
    rx = 700
    s.rect(rx, 196, 444, 334, "#EAE2D0", radius=6)
    s.text("vh", "穷举结果", rx + 24, 214, 26, INK, bold=True)
    rows = [("黑先填，合法次序", f"{sq['total']} 种"),
            ("其中被规则禁着", f"{sq['illegal_moves']} 手"),
            ("黑棋被提", f"{sq['dead']} 种"), ("黑棋做出两眼", f"{sq['alive']} 种"),
            ("直三·黑占中间", f"真眼 {a1_regions} 个"),
            ("直三·黑占端点", "被白点中间"), ("主图结论", "死棋")]
    yy = 252
    for k, v in rows:
        s.text("rk", k, rx + 24, yy, 20, INK2)
        s.text("rv", v, rx + 420, yy, 20, RED if v in ("死棋", "被白点中间")
               else GREEN if "真眼" in v else INK, bold=True, align="right", font=MONO)
        yy += 26
    end = s.para("vn", "判定口径：一个空点区只有斜角全被本方控制才算真眼，"
                      "凑满两个真眼才算活。", rx + 24, yy + 4, 20, INK3, width=396)
    assert end - 8 <= 526, end

    s.rect(rx, 550, 444, 250, "#EAE2D0", radius=6)
    s.text("lh", "图例与算法", rx + 24, 566, 26, INK, bold=True)
    s.dot(rx + 40, 622, 15, STONE_B)
    s.text("l1", "黑棋（被围的一块）", rx + 62, 612, 20, INK2)
    s.dot(rx + 40, 656, 15, STONE_W, ring="#8A6B3A", ring_w=1.5)
    s.text("l2", "白棋（封住外气）", rx + 62, 646, 20, INK2)
    s.rect(rx + 268, 613, 18, 18, "#00000000", border=f"2.5 SOLID {RED}", radius=3)
    s.text("l3", "被围空点", rx + 294, 612, 20, INK2)
    s.rect(rx + 268, 647, 18, 18, "#00000000", border=f"2.5 SOLID {GREEN}", radius=3)
    s.text("l4", "真眼 / 被提", rx + 294, 646, 20, INK2)
    steps = ["4 个空点轮流填满共 24 条次序；",
             f"引擎逐手判自杀与提子，{sq['illegal_moves']} 手禁着跳过，",
             f"剩下 {sq['total']} 条合法次序走到同一终局：",
             "白棋落下第 4 子时，黑角整块无气被提。"]
    yy = 682
    for st in steps:
        assert tw(st, 20) <= 396, (st, tw(st, 20))
        s.text("rs", st, rx + 24, yy, 20, INK2)
        yy += 26
    assert yy - 26 + 21.2 <= 796, yy

    # ---- two variation boards (6x6 corner crops)
    vy = 812
    s.text("vh1", "变化图 A · 直三，黑先占中间 → 活", 56, vy, 24, INK, bold=True)
    board_draw(s, a1, 100, vy + 68, 36, 6, numbers={(1, 0): 1}, r=15)
    for p in [tuple(q) for q in a1_space]:
        s.rect(100 + p[0] * 36 - 7, vy + 68 + p[1] * 36 - 7, 14, 14, "#00000000",
               border=f"2.5 SOLID {GREEN}", radius=3)
    endv1 = s.para("vt1", f"黑 1 落在中间，剩下两个空点互不相连（绿框），白棋哪一侧落子都是"
                          f"自杀 → 黑棋有 {a1_regions} 个真眼，活。",
                   300, vy + 68, 20, INK2, width=280)
    assert endv1 - 8 <= 1060, endv1
    s.text("vh2", "变化图 B · 直三，黑先占端点 → 死", 620, vy, 24, INK, bold=True)
    board_draw(s, b_final, 664, vy + 68, 36, 6, numbers={(1, 0): 4}, r=15)
    for p in [tuple(q) for q in doomed]:
        s.rect(664 + p[0] * 36 - 7, vy + 68 + p[1] * 36 - 7, 14, 14, "#00000000",
               border=f"2.5 SOLID {RED}", radius=3)
    endv = s.para("vt2", f"黑 1 占端点，白 2 点中间，黑 3 提一子但仍只有一个眼，白 4 回提："
                        f"整块黑棋 {b_caps} 子被吃（红框为被提位置）。",
                  864, vy + 68, 20, INK2, width=280)
    assert endv - 8 <= 1060, endv
    s.line(56, 1088, 1144, 1088, "#D9CFB8", 1)
    s.text("fn", "教学演示：棋形与次序为自编示例；规则按禁自杀、提子优先，未考虑劫争与外气对杀。",
           56, 1098, 20, INK3)
    return s, {"fangsi": {"sequences": sq["total"], "black_alive": sq["alive"],
                          "black_captured": sq["dead"], "unfinished": sq["other"],
                          "paths": sq["paths"]},
               "square": {"stones": len(sq_grp), "liberties": [list(p) for p in sq_libs],
                          "regions": sq_regions},
               "zhisan": {"sequences": s3["total"], "alive": s3["alive"],
                          "dead": s3["dead"], "unfinished": s3["other"],
                          "paths": s3["paths"]},
               "zhisan_middle": {"regions": a1_regions,
                                 "eye_points": [list(p) for p in a1_space]},
               "zhisan_end": {"captured": b_caps, "doomed": [list(p) for p in doomed]},
               "rule": "禁自杀；提子优先；眼位＝气点的连通分量数"}


if __name__ == "__main__":
    s, data = build()
    (TMP / "case09.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case09-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
    print(json.dumps(data["fangsi"] | data["square"] | data["zhisan"] |
                     data["zhisan_middle"] | data["zhisan_end"],
                     ensure_ascii=False, default=str))
