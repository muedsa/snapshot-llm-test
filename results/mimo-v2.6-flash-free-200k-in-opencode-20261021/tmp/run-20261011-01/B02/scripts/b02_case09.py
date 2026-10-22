# -*- coding: utf-8 -*-
"""B02 case-09 · 三季度收成报告 (1600x900, 公示栏/社群 1m).

user_goal: 看懂本季产出、参与度与资金去向。
Data: q3_total/q3_break from FACTS (sum asserted), expense shares sum 100.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1600, 900

EXPENSE = [("育苗与种子", 32), ("工具维护", 24), ("肥料与基质", 18),
           ("灌溉水电", 14), ("其他", 12)]
NEXT_SEASON = ["南侧新增 2 块香草畦（供菜篮）",
               "滴灌改造，预计节水 30%",
               "亲子自然课扩至每周两场"]


def main():
    C.assert_facts()
    assert sum(p for _n, p in EXPENSE) == 100
    assert sum(v for _n, v in C.FACTS["q3_break"]) == C.FACTS["q3_total"]
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # header
    els.append(C.box(0, 0, W, 96, C.LEAFD))
    els.append(C.brand_header(44, 16, 500, color=C.PAPER, mark=C.SUN,
                              size=22, latin_size=10))
    els.append(C.text(44, 56, 760, 34, "三季度收成报告 · 7–9 月", 26, C.PAPER,
                      bold=True))
    els.append(C.text(1000, 30, 556, 44, "公示：认养户 + 捐赠方", 22, "#CDE0C4",
                      align="RIGHT"))

    # KPI tiles
    ky = 124
    kpis = [
        ("总收成", "%d" % C.FACTS["q3_total"], "公斤", "较上季 +18%",
         C.CLAY),
        ("志愿参与", "%d" % C.FACTS["volunteers"], "人 · 12 个劳动日",
         "累计 486 人次时", C.LEAF),
        ("堆肥转化", "2.4→0.8", "吨厨余变堆肥", "转化率 33%", C.SOIL),
    ]
    for i, (t, big, unit, sub, cc) in enumerate(kpis):
        x = 48 + i * 512
        els.append(C.box(x, ky, 480, 150, C.PAPER2, radius=16, border=C.LINE,
                         shadow="0 6 16 0 #6B4A2F1A NORMAL"))
        els.append(C.box(x, ky, 8, 150, cc, radius=4))
        els.append(C.text(x + 30, ky + 18, 260, 30, t, 21, C.MUTED))
        els.append(C.text(x + 30, ky + 52, 300, 64, big, 52, cc, bold=True))
        els.append(C.text(x + 300, ky + 76, 170, 34, unit, 18, C.MUTED))
        els.append(C.chip(x + 300, ky + 24, 160, 36, C.LEAFL, sub, 15,
                          C.LEAFD, radius=10))

    # left: harvest breakdown bars
    by = 308
    els.append(C.section(48, by, 740, "品类构成（公斤）", size=24))
    mx = max(v for _n, v in C.FACTS["q3_break"])
    ry = by + 54
    for name, v in C.FACTS["q3_break"]:
        els.append(C.text(48, ry - 2, 84, 30, name, 19, C.INK, bold=True))
        els.append(C.box(144, ry, 520, 24, "#EDE4D2", radius=12))
        els.append(C.box(144, ry, 520 * v / float(mx), 24, C.CLAY, radius=12))
        els.append(C.text(676, ry - 2, 110, 30, "%d" % v, 19, C.CLAY,
                          bold=True))
        ry += 42

    # left-bottom: where the harvest went (completes the report story)
    els.append(C.box(48, 668, 740, 86, C.PAPER2, radius=14, border=C.LINE))
    els.append(C.text(72, 684, 150, 30, "收成去向", 20, C.INK, bold=True))
    dests = [("市集售出 42%", C.CLAY), ("菜篮配送 46%", C.LEAF),
             ("食堂捐赠 12%", C.SOIL)]
    dx0 = 216
    for lbl, cc in dests:
        els.append(C.chip(dx0, 690, 172, 40, cc, lbl, 16, "#FFFFFF",
                          radius=12))
        dx0 += 186

    # right: expense shares + next season
    ex = 830
    els.append(C.section(ex, by, 722, "支出构成（本季支出 ¥18,600）", size=24))
    sy = by + 54
    # stacked share bar
    sx = ex
    palette = [C.CLAY, C.LEAF, C.SUN, C.SOIL, C.LEAFD]
    for (name, p), cc in zip(EXPENSE, palette):
        seg = 722 * p / 100.0
        els.append(C.box(sx, sy, seg, 34, cc))
        if seg > 70:
            els.append(C.text(sx, sy + 6, seg, 26, "%d%%" % p, 16, "#FFFFFF",
                              bold=True, align="CENTER"))
        sx += seg
    sy += 50
    for i, ((name, p), cc) in enumerate(zip(EXPENSE, palette)):
        col_i, row_i = divmod(i, 3)
        x = ex + col_i * 366
        y = sy + row_i * 36
        els.append(C.box(x, y + 6, 16, 16, cc, radius=4))
        els.append(C.text(x + 26, y, 250, 30, name, 17, C.INK))
        els.append(C.text(x + 276, y, 60, 30, "%d%%" % p, 17, C.MUTED,
                          bold=True))
    # next season
    nsy = by + 250
    els.append(C.box(ex, nsy, 722, 170, C.LEAFL, radius=14))
    els.append(C.text(ex + 26, nsy + 16, 400, 32, "下季计划", 22, C.LEAFD,
                      bold=True))
    ny = nsy + 54
    for n in NEXT_SEASON:
        els.append(C.circle(ex + 36, ny + 11, 5, C.CLAY))
        els.append(C.text(ex + 54, ny, 640, 30, n, 18, C.INK))
        ny += 36

    els.append(C.line_h(48, H - 76, 1552, C.LINE))
    els.append(C.footnote(48, H - 62, 1100,
                          "禾风里社区共耕花园 · 虚构演示报告；产量、支出与计划均为示例数据"))
    els.append(C.footnote(1150, H - 62, 402, "编制：管委会财务组 · 10 月 5 日",
                          align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-09-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
