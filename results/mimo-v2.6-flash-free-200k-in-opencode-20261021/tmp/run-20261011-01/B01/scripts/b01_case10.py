# -*- coding: utf-8 -*-
"""B01 case-10 · 金杯拉花赛 · 评审屏 (1600x900 舞台大屏).

Audience: 评委、观众与直播（赛场大屏远景可读）。
Goal: 四位选手两轮成绩、排名变化与评分维度一目了然。
Fictional contest; all scores asserted in-script (G3).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1600, 900
BG = "#17120C"
PANEL = "#221A11"
INK = "#F6EAD2"
MUTED = "#A08A66"
GOLD = "#E5A83C"
CREAM = "#F5D48A"

# name, team, r1(fl, ar, fn), r2(fl, ar, fn)
PLAYERS = [
    ("周小麦", "麦田咖啡", (36.5, 37.5, 17.0), (35.0, 37.0, 17.0)),
    ("王岸", "山岚咖啡", (35.0, 36.0, 17.5), (36.0, 36.5, 17.5)),
    ("何雨", "雨石工作室", (35.5, 36.5, 17.5), (35.5, 35.5, 17.5)),
    ("陆一舟", "一舟烘焙", (34.0, 35.0, 17.0), (37.0, 37.5, 17.0)),
]
DIM = [("风味 40", "#E5A83C"), ("图案 40", "#C77DBB"), ("完成度 20", "#7FA8C9")]
MEDAL = ["#E5A83C", "#C9CDD4", "#C98A4B", "#6E5A44"]


def r1(t):
    return round(sum(t), 1)


def main():
    rows = []
    for name, team, a, b in PLAYERS:
        rows.append((name, team, a, b, round(r1(a) + r1(b), 1)))
    order = sorted(rows, key=lambda x: -x[4])
    totals = [x[4] for x in rows]
    assert len(set(totals)) == 4, totals                 # no ties
    assert abs(order[0][4] - 180.0) < 1e-9               # 周小麦 180.0 冠军
    r1_rank = {x[0]: i + 1 for i, x in enumerate(
        sorted(rows, key=lambda x: -r1(x[2])))}
    fin_rank = {x[0]: i + 1 for i, x in enumerate(order)}

    els = []
    els.append(B.grad_rect(0, 0, W, H, "#17120C,#241A0E", "TOP_LEFT",
                           "BOTTOM_RIGHT"))
    els.append(B.grad_rect(0, 0, W, 8, "#E5A83C,#C77DBB,#7FA8C9",
                           "TOP_LEFT", "TOP_RIGHT"))

    # ---------------- header ----------------
    els.append(B.text_el(60, 26, 500, 32, "金杯拉花赛 · 第 7 届", 23, GOLD,
                         bold=True))
    els.append(B.text_el(60, 60, 700, 46, "评审屏 · 总成绩", 34, INK, bold=True))
    els.append(B.text_el(640, 70, 560, 28,
                         "两轮已完赛 · 均分制：风味 40 + 图案 40 + 完成度 20",
                         19, MUTED))
    els.append(B.chip_el(1330, 44, 210, 44, "#2E2414", "决赛轮已结束", 21,
                         CREAM, radius=22, border=GOLD, border_w=2))

    # ---------------- player cards ----------------
    cx = 60
    for name, team, a, b, tot in order:
        rk = fin_rank[name]
        is_win = rk == 1
        els.append(B.rect_at(cx, 130, 365, 396, "#2A2013", radius=16,
                             border=GOLD if is_win else "#4A3A25",
                             border_w=3 if is_win else 1))
        els.append(B.circle_el(cx + 50, 186, 30, MEDAL[rk - 1], shadow=None))
        els.append(B.text_el(cx + 22, 172, 56, 32, str(rk), 26, "#17120C",
                             bold=True, align="CENTER"))
        els.append(B.text_el(cx + 96, 158, 250, 34, name, 26, INK, bold=True))
        els.append(B.text_el(cx + 96, 194, 250, 26, team, 17, MUTED))
        if is_win:
            els.append(B.chip_el(cx + 240, 152, 110, 34, "#E5A83C", "冠军",
                                 19, "#17120C", radius=17))
        els.append(B.text_el(cx + 24, 244, 200, 64, "%.1f" % tot, 52, CREAM,
                             bold=True))
        els.append(B.text_el(cx + 24, 312, 320, 26,
                             "第一轮 %.1f  →  第二轮 %.1f" % (r1(a), r1(b)),
                             19, INK))
        # stacked round-2 bar
        bx = cx + 24
        for (lab, c), v in zip(DIM, b):
            seg = v / 100.0 * 317
            els.append(B.rect_at(bx, 352, seg, 22, c, radius=0))
            bx += seg
        els.append(B.rect_at(cx + 24, 352, 317, 22, "#00000000", radius=8,
                             border="#4A3A25", border_w=1))
        lx = cx + 24
        for (lab, c), v in zip(DIM, b):
            els.append(B.rect_at(lx, 390, 14, 14, c, radius=3))
            els.append(B.text_el(lx + 20, 386, 96, 22, lab.split()[0], 15,
                                 MUTED))
            lx += 106
        # rank change
        chg = r1_rank[name] - rk
        if chg > 0:
            txt, c = "↑ %d 位" % chg, "#4ADE80"
        elif chg < 0:
            txt, c = "↓ %d 位" % (-chg), "#F87171"
        else:
            txt, c = "— 持平", MUTED
        els.append(B.chip_el(cx + 24, 430, 150, 36, "#17120C", txt, 18, c,
                             radius=18, border=c, border_w=1))
        els.append(B.text_el(cx + 190, 436, 160, 26, "首轮第 %d" % r1_rank[name],
                             17, MUTED, align="RIGHT"))
        cx += 380

    # ---------------- score table ----------------
    els.append(B.text_el(60, 556, 600, 32, "两轮分明细（单位：分）", 23, INK,
                         bold=True))
    ty = 596
    COLS = [("选手", 240), ("风味", 110), ("图案", 110), ("完成度", 120),
            ("轮小计", 130), ("风味", 110), ("图案", 110), ("完成度", 120),
            ("轮小计", 130), ("总分", 130), ("排名变化", 180)]
    xs = [60]
    for _l, wd in COLS:
        xs.append(xs[-1] + wd)
    els.append(B.rect_at(60, ty, 1480, 36, "#2E2414", radius=8))
    for i, ((lab, wd), x) in enumerate(zip(COLS, xs[:-1])):
        tag = "第一轮" if 1 <= i <= 4 else ("第二轮" if 5 <= i <= 8 else "")
        els.append(B.text_el(x + 8, ty + 6, wd - 12, 24, lab, 16, MUTED))
    els.append(B.text_el(xs[1], ty - 26, 240, 22, "", 14, MUTED))
    ty += 42
    for name, team, a, b, tot in order:
        rk = fin_rank[name]
        els.append(B.rect_at(60, ty, 1480, 46, PANEL, radius=8))
        els.append(B.text_el(76, ty + 10, 220, 26,
                             "%d  %s" % (rk, name), 19, INK, bold=True))
        vals = ["%.1f" % v for v in a] + ["%.1f" % r1(a)] + \
            ["%.1f" % v for v in b] + ["%.1f" % r1(b)]
        for v, x, wd in zip(vals, xs[1:9], [w for _l, w in COLS[1:9]]):
            els.append(B.text_el(x, ty + 10, wd, 26, v, 18, INK,
                                 align="CENTER"))
        els.append(B.text_el(xs[9], ty + 8, COLS[9][1], 30, "%.1f" % tot, 21,
                             CREAM, bold=True, align="CENTER"))
        chg = r1_rank[name] - rk
        txt = ("↑ %d" % chg) if chg > 0 else (("↓ %d" % -chg) if chg < 0
                                              else "持平")
        c = "#4ADE80" if chg > 0 else ("#F87171" if chg < 0 else MUTED)
        els.append(B.text_el(xs[10], ty + 10, COLS[10][1], 26, txt, 18, c,
                             bold=True, align="CENTER"))
        ty += 52

    els.append(B.text_el(60, 862, 1000, 24,
                         "金杯拉花赛 · 选手与成绩为虚构演示数据 · "
                         "评分去极值后取均值", 16, MUTED))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-10-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
