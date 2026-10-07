# -*- coding: utf-8 -*-
"""A07 - 720x1280 travel card for the three shortest journeys (travel-card.png).

Same visual system as network-map.png (same palette, same route badges, same
glyph vocabulary) but a phone-width layout: one stacked card per query.
Everything is emitted as Snapshot DSL; no <Image>.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "A07"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import a07_common as C  # noqa: E402
from build_map_a07 import (ACC_GLYPH, ACC_OFF, ACC_ON, BG, INK, LC, MUTED, FAINT,  # noqa: E402
                           PILL_FS, badge, circle)

TASK = "A07"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 720, 1280
PAD = 28
CARD_X, CARD_W = PAD, W - 2 * PAD          # 28 .. 692
IN_X = CARD_X + 20                          # 48
IN_W = CARD_W - 40                          # 624
HEAD_H = 146
GAP = 14
FS = 20                                     # every body string on the card is >= 20px

HEAD_BG = "#0F172AFF"
HEAD_SUB = "#CBD5E1FF"
CARD_BG = "#FFFFFFFF"
CARD_BORD = "#CBD5E1FF"
DIV = "#E2E8F0FF"


def acc_chip(x, y, acc, size=26.0):
    col = ACC_ON if acc else ACC_OFF
    return [D.box(x, y, size, size, color=col, radius=8),
            D.text_el(ACC_GLYPH[acc], x=x, y=y + 6, w=size, h=size - 6, size=17,
                      color="#FFFFFFFF", align="CENTER", style="BOLD",
                      font="DejaVu Sans,Noto Sans CJK SC")]


def chain_kids(x, y, seq, size=FS, marks=()):
    """Station names joined by '›'; non-accessible names in amber.  `marks` are
    indices after which a line-change bar is drawn."""
    out = []
    cx = x
    for i, sid in enumerate(seq):
        acc = C.ACC[sid]
        nm = C.NAME[sid]
        w = D.est_width(nm, size)
        out.append(D.text_el(nm, x=cx, y=y, w=w + 8, h=size * 1.5, size=size,
                             color=INK if acc else ACC_OFF, font=D.UI,
                             style="BOLD" if not acc else None))
        cx += w + 6
        if i in marks:
            out.append(D.box(cx + 4, y + 2, 2.5, size * 1.05, color=FAINT))
            cx += 22
        elif i < len(seq) - 1:
            out.append(D.text_el("\u203a", x=cx + 2, y=y, w=size + 4, h=size * 1.5,
                                 size=size, color=FAINT, font=D.UI))
            cx += size + 4
    return out, cx


def chain_w(seq, size=FS, marks=()):
    w = 0.0
    for i, sid in enumerate(seq):
        w += D.est_width(C.NAME[sid], size) + 6
        if i in marks:
            w += 22
        elif i < len(seq) - 1:
            w += size + 4
    return w


# ------------------------------------------------------------------ block metrics
def leg_blocks(route):
    legs = route["legs"]
    out = []
    for i, leg in enumerate(legs):
        out.append(("chip", 30, leg))
        out.append(("chain", 32, leg))
        if i < len(legs) - 1:
            out.append(("xfer", 30, legs[i + 1]["board"]))
    return out


def card_metrics(entry):
    n = entry["normal_route"]
    h = 18 + 36
    for kind, bh, payload in leg_blocks(n):
        h += bh
    h += 34 + 18
    if entry["accessible_route"]:
        h += 12 + 30 + 32 + 30 + 18
    return h

def render_card(x, y, entry):
    n = entry["normal_route"]
    kids = [D.box(x, y, CARD_W, card_metrics(entry), color=CARD_BG, radius=16,
                  border="1 SOLID %s" % CARD_BORD)]
    cy = y + 18
    # -- title row
    kids += badge(x + 36, cy + 18, 16, INK, str(entry["query_index"]), 20)
    title = "%s %s \u2192 %s %s" % (entry["from"], entry["from_name"],
                                    entry["to"], entry["to_name"])
    kids.append(D.text_el(title, x=x + 60, y=cy + 2, w=400, h=32, size=23, color=INK,
                          style="BOLD", font=D.UI))
    kids.append(D.text_el("%d 区间 · %d 换乘" % (n["edges"], n["transfers"]),
                          x=x + CARD_W - 20 - 190, y=cy + 6, w=190, h=28, size=FS,
                          color=MUTED, align="RIGHT", font=D.UI))
    cy += 36
    # -- riding legs
    for kind, bh, payload in leg_blocks(n):
        if kind == "chip":
            lid = payload["line"]
            kids += badge(x + 32, cy + 15, 12, LC[lid], lid, 15)
            kids.append(D.text_el(C.LNAME[lid], x=x + 50, y=cy + 2, w=70, h=28,
                                  size=FS, color=INK, style="BOLD", font=D.UI))
            kids.append(D.text_el("%s \u2192 %s · %d 区间" % (payload["board"],
                                                              payload["alight"],
                                                              payload["edges"]),
                                  x=x + CARD_W - 20 - 340, y=cy + 2, w=340, h=28,
                                  size=FS, color=MUTED, align="RIGHT", font=D.UI))
        elif kind == "chain":
            ck, _ = chain_kids(IN_X, cy + 1, payload["stations"])
            kids += ck
        else:
            sid = payload
            kids.append(D.box(x + 44, cy - 2, 2, 34, color=FAINT))
            kids += acc_chip(x + 54, cy + 2, C.ACC[sid], 24.0)
            kids.append(D.text_el("换乘 %s %s" % (sid, C.NAME[sid]), x=x + 86, y=cy + 4,
                                  w=200, h=26, size=FS, color=INK, font=D.UI))
            kids.append(D.text_el("可作无障碍换乘站" if C.ACC[sid] else "非无障碍站，不可换乘",
                                  x=x + 290, y=cy + 4, w=374, h=26, size=FS,
                                  color=ACC_ON if C.ACC[sid] else ACC_OFF, font=D.UI))
        cy += bh
    # -- accessibility verdict (one row: verdict + what was ridden through)
    ok = n["accessibility_feasible"]
    kids += acc_chip(IN_X, cy + 4, ok)
    kids.append(D.text_el("可作为无障碍旅程" if ok else "不可作为无障碍旅程",
                          x=IN_X + 34, y=cy + 5, w=210, h=28, size=FS,
                          color=ACC_ON if ok else ACC_OFF, style="BOLD", font=D.UI))
    passed = n["non_accessible_passed_through"]
    if ok:
        detail = ("· 经过非无障碍站 %s（可乘车）"
                  % "、".join(C.NAME[s] for s in passed)) if passed else "· 全程各站均为无障碍站"
    else:
        bad = [s for s in n["transfer_stations"] if not C.ACC[s]]
        detail = "· 受限换乘站 %s（非无障碍）" % " ".join(
            "%s %s" % (C.NAME[s], s) for s in bad)
    kids.append(D.text_el(detail, x=IN_X + 248, y=cy + 5, w=376, h=28, size=FS,
                          color=MUTED, font=D.UI))
    cy += 34 + 18
    # -- accessible alternative (only when the shortest ordinary journey fails)
    alt = entry["accessible_route"]
    if alt:
        kids.append(D.hline(IN_X, x + CARD_W - 20, cy, DIV, 1.5))
        cy += 12
        kids.append(D.text_el("无障碍最短替代路线", x=IN_X, y=cy, w=300, h=28,
                              size=FS, color=ACC_OFF, style="BOLD", font=D.UI))
        kids.append(D.text_el("%d 区间 · %d 换乘（区间数相同，换乘 +%d）"
                              % (alt["edges"], alt["transfers"],
                                 alt["transfers"] - n["transfers"]),
                              x=x + CARD_W - 20 - 400, y=cy, w=400, h=28, size=FS,
                              color=MUTED, align="RIGHT", font=D.UI))
        cy += 30
        marks = {alt["stations"].index(leg["board"]) for leg in alt["legs"][1:]}
        ck, _ = chain_kids(IN_X, cy + 1, alt["stations"], marks=marks)
        kids += ck
        cy += 32
        kids.append(D.text_el(" \u2192 ".join("%s %d区间" % (C.LNAME[l["line"]], l["edges"])
                                              for l in alt["legs"]),
                              x=IN_X, y=cy, w=IN_W, h=28, size=FS, color=MUTED,
                              font=D.UI))
        cy += 30
    return kids


def header_kids():
    out = [D.box(0, 0, W, HEAD_H, color=HEAD_BG),
           D.text_el("虚构城市 · 行程卡", x=PAD, y=20, w=420, h=40, size=30,
                     color="#FFFFFFFF", style="BOLD", font=D.UI),
           D.text_el("三条最少站间区间旅程 · 与全网示意图同一视觉系统",
                     x=PAD, y=66, w=520, h=28, size=FS, color=HEAD_SUB, font=D.UI)]
    x = PAD
    for lid in C.LORDER:
        out += badge(x + 13, 120, 13, LC[lid], lid, 16)
        out.append(D.text_el(C.LNAME[lid], x=x + 32, y=106, w=80, h=28, size=FS,
                             color="#FFFFFFFF", font=D.UI))
        x += 96
    out.append(D.text_el("非地理示意图", x=440, y=106, w=252, h=28, size=FS,
                         color="#94A3B8FF", align="RIGHT", font=D.UI))
    return out


def footer_kids(y):
    kids = [D.text_el("口径与图例", x=IN_X, y=y, w=300, h=28, size=FS, color=INK,
                      style="BOLD", font=D.UI)]
    lines = [
        "区间数 = 相邻站对数 = 站数 − 1；换乘 = 改乘另一条线（首乘不计）",
        "琥珀色站名 = 非无障碍站：可乘车经过，不可作起终点或换乘站",
        "边数相同取换乘更少者；无障碍约束只筛起终点与换乘站，不删线路",
        "非地理示意图；全网 16 站 · 3 线 · 16 区间 · 3 换乘站",
    ]
    yy = y + 30
    for t in lines:
        kids.append(D.text_el("· " + t, x=IN_X, y=yy, w=W - IN_X - PAD, h=28,
                              size=FS, color=MUTED, font=D.UI))
        yy += 30
    return kids, yy


def build():
    routes = C.solve_all()
    hs = [card_metrics(e) for e in routes]
    total = sum(hs) + GAP * (len(routes) - 1)
    foot_top = HEAD_H + 12 + total + 16
    assert foot_top + 30 + 30 * 4 <= H, "content overflows: footer ends at %d" % (foot_top + 150)
    kids = [D.box(0, 0, W, H, color=BG)]
    kids += header_kids()
    y = HEAD_H + 12
    for e, h in zip(routes, hs):
        kids += render_card(CARD_X, y, e)
        y += h + GAP
    fk, end = footer_kids(foot_top)
    kids += fk
    return D.snapshot([D.stack(kids, W, H)], W, H, bg=BG), routes, (sum(hs), foot_top, end)


if __name__ == "__main__":
    dsl, routes, geo = build()
    from build_map_a07 import archive
    ap = archive(dsl, "card")
    r = snapkit.render(dsl, "travel-card.png", "travel-card.snapshot", final=True)
    print("archived draft:", ap)
    print("cards=%s footer_top=%s footer_end=%s" % geo)
    print("render ok=%s status=%s bytes=%s dsl=%d elements=%d"
          % (r.get("ok"), r.get("status"), r.get("bytes"), len(dsl.encode("utf-8")),
             dsl.count("<Positioned")))
    if not r.get("ok"):
        print(r.get("error"))
    print("image:", r.get("image"))
    for wn in D.warnings():
        print("WARN", wn)
