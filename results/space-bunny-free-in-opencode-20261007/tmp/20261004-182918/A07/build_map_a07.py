# -*- coding: utf-8 -*-
"""A07 - 1600x1000 three-line metro schematic (network-map.png).

Everything on the canvas is emitted as Snapshot DSL: line runs are rotated
Containers inside <Transform matrix=...>, station markers are circles, every
label is a Text.  No <Image>, no external asset.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "A07"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import a07_common as C  # noqa: E402

TASK = "A07"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 1600, 1000
BG = "#EEF2F6FF"
PANEL = "#FFFFFFFF"
PBORD = "#CBD5E1FF"
INK = "#0F172AFF"
MUTED = "#55637AFF"
FAINT = "#94A3B8FF"
HALO = "#FFFFFFF5"
LC = {"R": "#E11D48FF", "B": "#1D4ED8FF", "G": "#047857FF"}
ACC_ON = "#0F766EFF"
ACC_OFF = "#B45309FF"
ACC_GLYPH = {True: "\u2713", False: "\u2715"}
LW = 11.0                      # line core width
GAP = 8.0                      # half length of the bridge gap at a non-transfer crossing
UNDER = {"R": 2, "B": 1, "G": 0}   # smaller number == drawn on top (wins the crossing)
ZORDER = sorted(C.LORDER, key=lambda l: -UNDER[l])   # draw the top line last

MAP = dict(x=24, y=90, w=1204, h=654)
INFO = dict(x=1244, y=90, w=332, h=654)
LEG = dict(x=24, y=752, w=1552, h=136)

# station label anchors: direction + optional pixel nudges
ANCH = {
    "S01": ("S", 8, 0), "S02": ("N", 0, 0), "S03": ("S", 0, 0), "S04": ("N", 0, 0),
    "S05": ("N", 0, 0), "S06": ("W", 0, 0), "S07": ("S", 56, 0), "S08": ("N", 0, 0),
    "S09": ("E", 0, 0), "S10": ("SE", 0, 0), "S11": ("N", 0, 0), "S12": ("S", 0, 0),
    "S13": ("S", 8, 0), "S14": ("N", -56, 0), "S15": ("S", 0, 0), "S16": ("NE", 0, 0),
}
FS = 20                       # every map label is >= 20px
BADGE = 26.0
PILL_W = 54.0
PILL_FS = 17


def fsz(v):
    return int(round(v))


# ------------------------------------------------------------------ primitives
def circle(cx, cy, r, fill=None, border=None, bw=3.0):
    return D.box(cx - r, cy - r, 2 * r, 2 * r, color=fill, radius=r, border=border,
                 extra=None if border is None else {"border": "%s SOLID %s" % (bw, border)})


def rot_rect(x0, y0, x1, y1, width, color, radius=None):
    """A bar of `width` spanning (x0,y0)->(x1,y1) via one column-major 4x4 matrix."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.5:
        return None
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    th = -math.degrees(math.atan2(y1 - y0, x1 - x0))
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    a, b, cc, d = round(c, 6), round(-s, 6), round(s, 6), round(c, 6)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (a, b, cc, d)
    r = width / 2.0 if radius is None else radius
    inner = D.el("Container", {"width": round(L, 2), "height": width, "color": color,
                                "borderRadius": r})
    tr = D.el("Transform", {"matrix": m, "alignment": "CENTER"}, [inner])
    return D.el("Positioned", {"left": round(mx - L / 2.0, 2), "top": round(my - width / 2.0, 2),
                               "width": round(L, 2), "height": width}, [tr])


def badge(cx, cy, r, fill, glyph, gfs, gcolor="#FFFFFFFF", ring=None, ringw=2.5):
    out = []
    if ring:
        out.append(circle(cx, cy, r + ringw / 2.0 + 0.5, fill=ring))
    out.append(circle(cx, cy, r, fill=fill))
    out.append(D.text_el(glyph, x=cx - r, y=cy - gfs * 0.78, w=2 * r, h=2.4 * gfs,
                         size=gfs, color=gcolor, align="CENTER", font="Inter,Noto Sans CJK SC",
                         style="BOLD"))
    return out


# ------------------------------------------------------------------ crossings
CROSS = C.find_crossings()


def split_at(p, q, cuts):
    """Split run p->q into sub-runs, removing +-GAP around each cut parameter."""
    subs = []
    segs = sorted(cuts)
    cur = 0.0
    for t in segs:
        subs.append((cur, max(cur, t - GAP / math.hypot(q[0] - p[0], q[1] - p[1]))))
        cur = t + GAP / math.hypot(q[0] - p[0], q[1] - p[1])
    subs.append((cur, 1.0))
    out = []
    for t0, t1 in subs:
        if t1 - t0 < 0.004:
            continue
        out.append(((p[0] + t0 * (q[0] - p[0]), p[1] + t0 * (q[1] - p[1])),
                    (p[0] + t1 * (q[0] - p[0]), p[1] + t1 * (q[1] - p[1]))))
    return out


def line_kids(lid):
    """All runs of one line, with bridge gaps where a lower-priority line crosses."""
    toks = C.PATH[lid]
    kids = []
    for a, b in zip(toks, toks[1:]):
        p = C._pt(a, toks)
        q = C._pt(b, toks)
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        cuts = []
        for cr in CROSS:
            if lid not in cr["lines"]:
                continue
            other = [l for l in cr["lines"] if l != lid][0]
            if UNDER[other] < UNDER[lid]:
                continue                      # this line is on top, stays continuous
            t = C.seg_point_param(p, q, cr["point"])
            if t is not None and 0.001 < t < 0.999:
                cuts.append(t)
        for (s, e) in split_at(p, q, cuts):
            r = rot_rect(s[0], s[1], e[0], e[1], LW, LC[lid])
            if r:
                kids.append(r)
    return kids


# ------------------------------------------------------------------ station labels
def label_box(sid):
    d, dx, dy = ANCH[sid]
    cx, cy = C.POS[sid]
    txt = "%s %s" % (sid, C.NAME[sid])
    tw = D.est_width(txt, FS)
    pw = (PILL_W + 8) if sid in C.INTERCHANGE else 0
    w = BADGE + 8 + tw + 10 + pw
    h = 30.0
    gap = 26.0
    if d == "E":
        x = cx + 11 + gap
    elif d == "W":
        x = cx - 11 - gap - w
    elif d in ("NE", "SE"):
        x = cx + 8
    elif d in ("NW", "SW"):
        x = cx - 8 - w
    else:
        x = cx - w / 2.0
    if d in ("N", "NE", "NW"):
        y = cy - 11 - gap - h
    elif d in ("E", "W"):
        y = cy - h / 2.0
    else:
        y = cy + 11 + gap
    return x + dx, y + dy, w, h, txt, tw


def label_kids(sid):
    x, y, w, h, txt, tw = label_box(sid)
    out = [D.box(x, y, w, h, color=HALO, radius=7)]
    acc = C.ACC[sid]
    col = ACC_ON if acc else ACC_OFF
    out.append(D.box(x + 4, y + 2, BADGE, BADGE, color=col, radius=8))
    out.append(D.text_el(ACC_GLYPH[acc], x=x + 4, y=y + 2 + 6, w=BADGE, h=BADGE - 6,
                         size=17, color="#FFFFFFFF", align="CENTER", style="BOLD",
                         font="DejaVu Sans,Noto Sans CJK SC"))
    out.append(D.text_el(txt, x=x + BADGE + 12, y=y + 3, w=tw + 12, h=h - 6, size=FS,
                         color=INK, font=D.UI, style="BOLD" if sid in C.INTERCHANGE else None))
    if sid in C.INTERCHANGE:
        px = x + BADGE + 12 + tw + 12
        out.append(D.box(px, y + 3, PILL_W, 24, color=INK, radius=12))
        out.append(D.text_el("换乘", x=px, y=y + 6, w=PILL_W, h=20, size=PILL_FS,
                             color="#FFFFFFFF", align="CENTER"))
    return out


# ------------------------------------------------------------------ route letters
BADGE_FRAC = {("B", "S04", "S09"): 0.25, ("G", "S15", "S05"): 0.78,
              ("R", "S05", "S06"): 0.62}


def frac_point(lid, a, b, f):
    toks = C.PATH[lid]
    ia, ib = toks.index(a), toks.index(b)
    segs = []
    for i in range(min(ia, ib), max(ia, ib)):
        p = C._pt(toks[i], toks)
        q = C._pt(toks[i + 1], toks)
        segs.append((p, q, math.hypot(q[0] - p[0], q[1] - p[1])))
    total = sum(s[2] for s in segs)
    want = f * total
    for p, q, L in segs:
        if want <= L:
            t = want / L
            return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
        want -= L
    return segs[-1][1]


def letter_badges():
    out = []
    for lid in C.LORDER:
        seq = C.LSEQ[lid]
        for a, b in zip(seq, seq[1:]):
            f = BADGE_FRAC.get((lid, a, b), 0.5)
            p = frac_point(lid, a, b, f)
            out += badge(p[0], p[1], 10.5, LC[lid], lid, 14, ring="#FFFFFFFF", ringw=3.0)
    return out


def terminus_badges():
    out = []
    for lid in C.LORDER:
        toks = C.PATH[lid]
        for tok in (toks[0], toks[-1]):
            p = C._pt(tok, toks)
            out += badge(p[0], p[1], 19, LC[lid], lid, 23, ring="#FFFFFFFF", ringw=3.0)
    return out


# ------------------------------------------------------------------ panels
def header_kids():
    out = [D.box(0, 0, W, 92, color="#FFFFFFFF"),
           D.hline(0, W, 91, PBORD, 2)]
    out.append(D.text_el("虚构城市 · 三线地铁示意图", x=44, y=14, w=760, h=44, size=34,
                         color=INK, style="BOLD", font=D.UI))
    out.append(D.text_el(
        "非地理示意图：站间距与转折仅作示意，不代表真实距离 · 相邻站双向可走且耗时相同 · "
        "16 站 / 3 线 / 16 区间 / 3 换乘站", x=44, y=56, w=1120, h=30, size=FS,
        color=MUTED, font=D.UI))
    out.append(D.text_el("红绿两色相近，故每条线路同时用颜色 + 字母双重编码",
                         x=1000, y=20, w=556, h=28, size=FS, color=MUTED,
                         align="RIGHT", font=D.UI))
    return out


def legend_kids():
    out = [D.box(LEG["x"], LEG["y"], LEG["w"], LEG["h"], color=PANEL, radius=14,
                 border="1 SOLID %s" % PBORD)]
    y0 = LEG["y"] + 8
    cols = [44, 416, 776, 1176]
    heads = ["图例 · 线路（颜色 + 字母双重编码）", "站点与交叉符号",
             "无障碍设施（站点属性）", "图面说明"]
    for cx, t in zip(cols, heads):
        out.append(D.text_el(t, x=cx, y=y0, w=380, h=26, size=20, color=MUTED,
                             style="BOLD", font=D.UI))
        out.append(D.hline(cx, min(cx + 356, 1556), y0 + 30, "#E2E8F0FF", 1.5))
    rows = [y0 + 42, y0 + 72, y0 + 102]
    # -- column 1: the three lines
    for i, lid in enumerate(C.LORDER):
        y = rows[i]
        out.append(rot_rect(cols[0], y + 15, cols[0] + 52, y + 15, 9, LC[lid], 4.5))
        out += badge(cols[0] + 72, y + 15, 17, LC[lid], lid, 21, ring=None)
        out.append(D.text_el("%s %s · %d站 %d区间" % (
            lid, C.LNAME[lid], len(C.LSEQ[lid]), len(C.LSEQ[lid]) - 1),
            x=cols[0] + 98, y=y + 3, w=270, h=26, size=20, color=INK, font=D.UI))
    # -- column 2: station symbols + the non-transfer crossing
    cx = cols[1]
    out.append(circle(cx + 12, rows[0] + 15, 10, fill="#FFFFFFFF", border=INK, bw=3.0))
    out.append(D.text_el("普通站（只属于一条线）", x=cx + 32, y=rows[0] + 3, w=300, h=26,
                         size=20, color=INK, font=D.UI))
    out.append(circle(cx + 12, rows[1] + 15, 21, fill=None, border="#0F172A8C", bw=2.0))
    out.append(circle(cx + 12, rows[1] + 15, 14, fill="#FFFFFFFF", border=INK, bw=4.0))
    out.append(D.text_el("换乘站（两条线共站）", x=cx + 42, y=rows[1] + 3, w=300, h=26,
                         size=20, color=INK, font=D.UI))
    y = rows[2]
    out.append(rot_rect(cx, y + 8, cx + 40, y + 24, 9, LC["B"], 4.5))
    out.append(rot_rect(cx + 8, y + 24, cx + 32, y + 8, 9, LC["G"], 4.5))
    out.append(D.text_el("跨线交叉 · 缺口表示不可换乘", x=cx + 48, y=y + 3, w=340,
                         h=26, size=20, color=INK, font=D.UI))
    # -- column 3: accessibility badges
    cx = cols[2]
    out.append(D.box(cx + 2, rows[0] + 2, BADGE, BADGE, color=ACC_ON, radius=8))
    out.append(D.text_el("\u2713", x=cx + 2, y=rows[0] + 8, w=BADGE, h=BADGE - 6, size=17,
                         color="#FFFFFFFF", align="CENTER", style="BOLD",
                         font="DejaVu Sans,Noto Sans CJK SC"))
    out.append(D.text_el("可作无障碍旅程的起点、终点与换乘站", x=cx + 36, y=rows[0] + 3,
                         w=360, h=26, size=20, color=INK, font=D.UI))
    out.append(D.box(cx + 2, rows[1] + 2, BADGE, BADGE, color=ACC_OFF, radius=8))
    out.append(D.text_el("\u2715", x=cx + 2, y=rows[1] + 8, w=BADGE, h=BADGE - 6, size=17,
                         color="#FFFFFFFF", align="CENTER", style="BOLD",
                         font="DejaVu Sans,Noto Sans CJK SC"))
    out.append(D.text_el("可乘车经过，不可作起点、终点或换乘站", x=cx + 36, y=rows[1] + 3,
                         w=360, h=26, size=20, color=INK, font=D.UI))
    # -- column 4: reading notes
    cx = cols[3]
    notes = ["非地理示意图，站距不代表真实距离",
             "线路转折只用 45° / 90° 走向",
             "区间数 = 站数 − 1，不等于站数"]
    for i, t in enumerate(notes):
        out.append(D.text_el("· " + t, x=cx, y=rows[i] + 3, w=390, h=26, size=20,
                             color=INK, font=D.UI))
    return out


def info_kids(routes):
    x0 = INFO["x"] + 20
    out = [D.box(INFO["x"], INFO["y"], INFO["w"], INFO["h"], color=PANEL, radius=14,
                 border="1 SOLID %s" % PBORD)]
    out.append(D.text_el("全网总览", x=x0, y=INFO["y"] + 14, w=292, h=32, size=23,
                         color=INK, style="BOLD", font=D.UI))
    y = INFO["y"] + 54

    def section(title):
        nonlocal y
        out.append(D.text_el(title, x=x0, y=y, w=292, h=26, size=20, color=MUTED,
                             style="BOLD", font=D.UI))
        out.append(D.hline(x0, INFO["x"] + INFO["w"] - 20, y + 27, "#E2E8F0FF", 1.5))
        y += 33

    def row(txt, size=19, color=INK, xoff=0, bold=False):
        nonlocal y
        out.append(D.text_el(txt, x=x0 + xoff, y=y, w=294 - xoff, h=26, size=size,
                             color=color, font=D.UI, style="BOLD" if bold else None))
        y += 26

    section("线路")
    for lid in C.LORDER:
        n = len(C.LSEQ[lid])
        out += badge(x0 + 11, y + 12, 11, LC[lid], lid, 14)
        row("%s %s　%d站 %d区间" % (lid, C.LNAME[lid], n, n - 1), size=20, xoff=30)
    section("换乘站（%d 处）" % len(C.INTERCHANGE))
    for sid in C.INTERCHANGE:
        row("%s %s · %s" % (sid, C.NAME[sid],
                            "／".join(C.LNAME[l] for l in C.LINES_AT[sid])), size=20)
    section("无障碍设施")
    okc = sum(1 for s in C.STATIONS if C.ACC[s])
    row("无障碍站 %d ／ %d" % (okc, len(C.STATIONS)), size=20)
    bad = [s for s in C.STATIONS if not C.ACC[s]]
    row("非无障碍站 %d（仍在线路上）" % len(bad), size=20, color=ACC_OFF, bold=True)
    for i in range(0, len(bad), 2):
        row("　".join("%s %s" % (s, C.NAME[s]) for s in bad[i:i + 2]), size=20,
            color=MUTED, xoff=6)
    section("几何与规模")
    row("跨线交叉 %d 处：%s × %s" % (len(CROSS), C.LNAME["G"], C.LNAME["B"]), size=20)
    row("站间区间 %d 段 · 双向可走" % len(C.EDGES), size=20)
    section("旅行卡上的三条旅程")
    for e in routes:
        n = e["normal_route"]
        out += badge(x0 + 11, y + 12, 11, INK, str(e["query_index"]), 14)
        row("%s → %s %d区间 %d换乘" % (e["from_name"], e["to_name"], n["edges"],
                                      n["transfers"]), size=20, xoff=30)
        if e["accessible_route"]:
            a = e["accessible_route"]
            out.append(D.text_el("└ 无障碍替代 %d区间·%d换乘" % (a["edges"], a["transfers"]),
                                 x=x0 + 36, y=y, w=258, h=26, size=20,
                                 color=ACC_OFF, font=D.UI))
            y += 24
    return out


# ------------------------------------------------------------------ assembly
def build():
    routes = C.solve_all()
    problems, _ = C.validate()
    assert not problems, problems

    kids = [D.box(0, 0, W, H, color=BG)]
    kids.append(D.box(MAP["x"], MAP["y"], MAP["w"], MAP["h"], color=PANEL, radius=14,
                      border="1 SOLID %s" % PBORD))
    for lid in ZORDER:
        kids += line_kids(lid)
    kids += letter_badges()
    kids += terminus_badges()
    for sid in C.STATIONS:
        cx, cy = C.POS[sid]
        if sid in C.INTERCHANGE:
            kids.append(circle(cx, cy, 21, fill=None, border="#0F172A8C", bw=2.0))
            kids.append(circle(cx, cy, 14, fill="#FFFFFFFF", border=INK, bw=4.0))
        else:
            kids.append(circle(cx, cy, 10, fill="#FFFFFFFF", border=INK, bw=3.0))
    # the single non-transfer crossing: bridge gap + explicit annotation
    for cr in CROSS:
        px, py = cr["point"]
        kids.append(D.vline(px, py + 12, py + 104, MUTED, 1.5))
        kids.append(D.box(px - 106, py + 108, 212, 32, color=HALO, radius=7))
        kids.append(D.text_el("跨线交叉 · 不可换乘", x=px - 106, y=py + 112, w=212, h=28,
                              size=20, color=MUTED, align="CENTER", font=D.UI))
    for sid in C.STATIONS:
        kids += label_kids(sid)
    kids += legend_kids()
    kids += info_kids(routes)
    kids += header_kids()
    kids.append(D.text_el(
        "读图约定：区间数 = 路线经过的相邻站对数 = 站数 − 1；换乘 = 改变乘坐线路，第一次上车不计换乘；",
        x=44, y=904, w=1512, h=28, size=20, color=MUTED, font=D.UI))
    kids.append(D.text_el(
        "未无障碍站可乘车经过，但不能作为无障碍旅程的起点、终点或换乘站；本图为非地理示意图，几何与文字全部由 DSL 计算生成。",
        x=44, y=936, w=1512, h=28, size=20, color=MUTED, font=D.UI))
    return D.snapshot([D.stack(kids, W, H)], W, H, bg=BG), routes


def journey_overlay(routes):
    """Unused on the map itself: the amber casing read as a 4th line, so the
    journeys are cross-referenced from the info panel instead (see info_kids)."""
    return []


def label_collision_report():
    boxes = {sid: label_box(sid) for sid in C.STATIONS}
    bad = []
    ids = list(boxes)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = boxes[ids[i]], boxes[ids[j]]
            if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]:
                bad.append((ids[i], ids[j]))
    for sid, (x, y, w, h, _, _) in boxes.items():
        if x < MAP["x"] + 4 or y < MAP["y"] + 4 or x + w > MAP["x"] + MAP["w"] - 4 or y + h > MAP["y"] + MAP["h"] - 4:
            bad.append((sid, "outside map panel"))
        for other in C.STATIONS:
            if other == sid:
                continue
            cx, cy = C.POS[other]
            if x - 11 < cx < x + w + 11 and y - 11 < cy < y + h + 11:
                bad.append((sid, "covers marker " + other))
    return bad


def archive(dsl, tag):
    """Keep every rendered DSL revision in the temp dir (never overwritten)."""
    d = os.path.join(TMP, "drafts")
    os.makedirs(d, exist_ok=True)
    ns = []
    for f in os.listdir(d):
        if f.startswith(tag + "-v") and f.endswith(".snapshot"):
            try:
                ns.append(int(f[len(tag) + 3:-10]))
            except ValueError:
                pass
    p = os.path.join(d, "%s-v%02d.snapshot" % (tag, max(ns or [0]) + 1))
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    return p


if __name__ == "__main__":
    dsl, routes = build()
    print("label collisions:", label_collision_report())
    ap = archive(dsl, "map")
    r = snapkit.render(dsl, "network-map.png", "network-map.snapshot", final=True)
    print("archived draft:", ap)
    print("render ok=%s status=%s bytes=%s dsl=%d elements=%d"
          % (r.get("ok"), r.get("status"), r.get("bytes"), len(dsl.encode("utf-8")),
             dsl.count("<Positioned")))
    if not r.get("ok"):
        print(r.get("error"))
    print("image:", r.get("image"))
    for wn in D.warnings():
        print("WARN", wn)
    print("crossings:", [(c["lines"], tuple(round(v, 1) for v in c["point"])) for c in CROSS])
