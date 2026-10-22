# -*- coding: utf-8 -*-
"""B02 case-10 · 市集帐篷横幅 (1920x640, 帐篷檐口 5-8m 远距).

user_goal: 远处识别摊位并记住三样主打与会员招募。
Far-view budget: few elements, large type (title>=96, prices>=40).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1920, 640

HEADS = [("番茄", 6), ("黄瓜", 5), ("罗勒", 10)]


def main():
    C.assert_facts()
    price_map = dict(C.MARKET_PRICES)
    for n, p in HEADS:
        assert price_map[n] == p, n
    els = []
    # leaf-green ground + watermark leaf rows
    els.append(C.grad_box(0, 0, W, H, C.col(C.LEAFD, "#274B2E"), "LEFT_CENTER"))
    for row in range(3):
        for i in range(14):
            els.append(C.leaf_mark(70 + i * 140 + (row % 2) * 70,
                                   70 + row * 210, 26, "#35603C", stem=False,
                                   rot=45))
    # top/bottom ticks
    els.append(C.ruler_ticks(60, 24, W - 120, n=48, color="#7FA987", h=8))
    els.append(C.ruler_ticks(60, H - 32, W - 120, n=48, color="#7FA987", h=8))

    # left brand lockup
    els.append(C.box(70, 70, 420, 500, "#24472B", radius=20))
    els.append(C.leaf_mark(176, 190, 44, C.SUN))
    els.append(C.text(100, 270, 360, 74, "禾风里", 62, C.PAPER, bold=True,
                      align="CENTER"))
    els.append(C.text(100, 350, 360, 34, "社区共耕花园", 26, "#CDE0C4",
                      align="CENTER"))
    els.append(C.line_h(140, 404, 420, "#7FA987"))
    els.append(C.text(100, 424, 360, 60, "每周六 09:00–13:00\n东门市集 B12 摊",
                      22, "#CDE0C4", align="CENTER", line_h=30))

    # center headline
    els.append(C.text(560, 96, 860, 130, "今日现摘", 108, C.PAPER, bold=True))
    els.append(C.text(560, 236, 900, 60, "当季 8 种菜 · 摘下不到 2 小时",
                      34, "#CDE0C4"))
    # three price cards
    for i, (n, p) in enumerate(HEADS):
        x = 560 + i * 290
        member = round(p * C.FACTS["member_discount"])
        els.append(C.box(x, 330, 262, 200, C.PAPER, radius=18))
        els.append(C.text(x + 20, 348, 222, 56, n, 44, C.INK, bold=True,
                          align="CENTER"))
        els.append(C.text(x + 20, 410, 222, 66, "¥%d" % p, 58, C.CLAY,
                          bold=True, align="CENTER"))
        els.append(C.text(x + 20, 486, 222, 32, "会员 ¥%d/斤" % member, 20,
                          C.LEAFD, bold=True, align="CENTER"))

    # right join-us block
    els.append(C.box(1500, 96, 350, 434, C.CLAY, radius=20))
    # 2 lines only: service line spacing for size-56 renders ~85px regardless
    # of line_h, so 3 lines would clip inside this block
    els.append(C.text(1530, 140, 290, 190, "现场扫码\n即刻入会", 56, "#FFFFFF",
                      bold=True, align="CENTER", line_h=84))
    els.append(C.line_h(1550, 350, 1800, "#E8A98A"))
    els.append(C.text(1530, 374, 290, 100, "当季会员\n全部 8 折", 34, "#FFE9DF",
                      bold=True, align="CENTER", line_h=44))
    els.append(C.chip(1540, 476, 270, 40, "#FFFFFF", "摊主：小周 · 前台可问",
                      16, C.CLAYD, radius=20))

    els.append(C.footnote(70, H - 60, 900,
                          "禾风里社区共耕花园 · 虚构演示横幅；菜价为示例",
                          color="#9EC3A4"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-10-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg="#2F5A38")


if __name__ == "__main__":
    main()
