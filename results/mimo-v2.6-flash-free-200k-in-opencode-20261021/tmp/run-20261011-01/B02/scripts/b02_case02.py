# -*- coding: utf-8 -*-
"""B02 case-02 · 地块认养证 (1240x1754 A4, 开放日现场打印).

user_goal: 拿到有仪式感的凭证并知晓三条基本义务。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1240, 1754


def main():
    C.assert_facts()
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # double frame
    els.append(C.box(48, 48, W - 96, H - 96, "#00000000", radius=6,
                     border=C.SOIL, border_w=3))
    els.append(C.box(62, 62, W - 124, H - 124, "#00000000", radius=4,
                     border=C.SOIL, border_w=1))

    # header
    els.append(C.text(100, 120, W - 200, 40, C.LATIN, 16, C.MUTED,
                      align="CENTER"))
    els.append(C.text(100, 166, W - 200, 84, "地块认养证", 60, C.INK,
                      bold=True, align="CENTER"))
    els.append(C.leaf_mark(W / 2, 300, 22, C.LEAF))
    els.append(C.ruler_ticks(160, 344, W - 320, n=30, color=C.SOIL))
    els.append(C.text(100, 374, W - 200, 34,
                      "编号  HF-2026-07  ·  认养期  2026.04 — 2027.03",
                      20, C.CLAY, bold=True, align="CENTER"))

    # holder block
    els.append(C.box(120, 440, W - 240, 200, C.PAPER2, radius=12,
                     border=C.LINE))
    els.append(C.text(160, 472, 300, 36, "认养人", 22, C.MUTED))
    els.append(C.text(160, 512, 500, 56, "林知夏  一家", 40, C.INK, bold=True))
    els.append(C.text(160, 578, 520, 30, "手机尾号 6621 · 东门邻里", 19,
                      C.MUTED))
    els.append(C.line_v(700, 470, 610, C.LINE))
    els.append(C.text(740, 472, 340, 36, "地块", 22, C.MUTED))
    els.append(C.text(740, 512, 340, 56, "07 号地", 40, C.LEAFD, bold=True))
    els.append(C.text(740, 578, 360, 30,
                      "%s · 东侧第三畦 · 全园共 %d 块" % (
                          C.FACTS["plot_size"], C.FACTS["plots"]), 19, C.MUTED))

    # plot sketch (mini geometry, accurate ratio 3m x 4m)
    px, py, pw, ph = 420, 690, 400, 300   # 3:4 ratio? -> width 3m=300? use 3:4
    # draw plot as 3m(w) x 4m(h): 1m = 75px  -> 225 x 300
    pw, ph = 225, 300
    px = (W - pw) / 2.0
    els.append(C.text(100, 666, W - 200, 30, "地块示意（3m × 4m，比例真实）",
                      18, C.MUTED, align="CENTER"))
    els.append(C.box(px, py, pw, ph, C.LEAFL, radius=8, border=C.LEAFD,
                     border_w=2))
    # four 0.75m beds with 0.25m path: beds 1.35m wide? keep simple: 4 rows
    bed_h = (ph - 5 * 10) / 4.0
    for i in range(4):
        els.append(C.box(px + 14, py + 10 + i * (bed_h + 10), pw - 28, bed_h,
                         C.SOIL, radius=6))
        els.append(C.text(px + 22, py + 16 + i * (bed_h + 10), pw - 44,
                          bed_h, ["春茬：番茄+罗勒", "夏茬：黄瓜",
                                  "秋茬：生菜", "冬茬：空心菜"][i], 17,
                          "#EFE6D8"))
    els.append(C.text(px, py + ph + 12, pw, 26, "北 ↑ · 灌溉口在西北角", 16,
                      C.MUTED, align="CENTER"))
    # flanking info cards (balance the plot band, add real value)
    for cx0, ttl, items, mc in [
        (120, "园方提供", ["种子与种苗", "共享工具房", "灌溉用水",
                          "每月 1 次种植答疑"], C.LEAFD),
        (780, "认养人获得", ["地块全部产出", "市集会员 8 折",
                            "菜篮订阅优先", "季度收成报告"], C.CLAY),
    ]:
        els.append(C.box(cx0, py, 340, 300, C.PAPER2, radius=12,
                         border=C.LINE))
        els.append(C.text(cx0 + 24, py + 20, 292, 32, ttl, 22, mc, bold=True))
        els.append(C.line_h(cx0 + 24, py + 58, cx0 + 316, C.LINE))
        iy = py + 76
        for it in items:
            els.append(C.circle(cx0 + 34, iy + 12, 5, mc))
            els.append(C.text(cx0 + 52, iy, 264, 30, it, 19, C.INK))
            iy += 48

    # three duties
    els.append(C.section(120, 1040, W - 240, "认养人须知（三条）", size=26))
    duties = [
        ("自种自收", "地块产出归认养人；连续 6 周无人打理且联系不上，园方代管后收回"),
        ("共享劳动日", "每季至少参加 2 次共享劳动日（园方提前一周在群里排班）"),
        ("边界与工具", "不占用公共步道；工具借还登记，损耗照价 3 成补齐"),
    ]
    dy = 1104
    for i, (t, d) in enumerate(duties, 1):
        els.append(C.circle(158, dy + 22, 22, C.CLAY))
        els.append(C.text(136, dy + 6, 44, 34, str(i), 22, "#FFFFFF",
                          bold=True, align="CENTER"))
        els.append(C.text(196, dy, 400, 34, t, 24, C.INK, bold=True))
        els.append(C.text(196, dy + 38, W - 356, 56, d, 19, C.MUTED,
                          line_h=28))
        dy += 108

    # signatures + seal
    els.append(C.line_h(120, 1470, 560, C.SOIL, 2))
    els.append(C.line_h(680, 1470, 1120, C.SOIL, 2))
    els.append(C.text(120, 1484, 440, 30, "认养人签字", 19, C.MUTED))
    els.append(C.text(680, 1484, 440, 30, "园方（禾风里管委会）", 19, C.MUTED))
    els.append(C.seal(852, 1500, 150, "2026.04.20", "认养专用章"))

    els.append(C.footnote(120, 1650, W - 240,
                          "本证为禾风里社区共耕花园（虚构演示项目）内部凭证；"
                          "认养规则与编号仅作演示，不具备法律效力。", align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-02-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
