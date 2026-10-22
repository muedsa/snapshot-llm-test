# -*- coding: utf-8 -*-
"""B02 case-01 · 开放日报名海报 (1080x1528, 公告栏/灯箱 2-3m).

user_goal: 30 秒知道开放日时间地点并扫码报名。
Facts used: market_day rhythm, address, plots/households (plan shared_facts).
Fictional QR placeholder (pixel pattern, NOT functional) is declared on-poster.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1080, 1528


def main():
    C.assert_facts()
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # top brand band
    els.append(C.box(0, 0, W, 108, C.LEAFD))
    els.append(C.brand_header(56, 30, 500, color=C.PAPER, mark=C.SUN,
                              size=26, latin_size=12))
    els.append(C.text(660, 34, 364, 40, C.LATIN, 14, "#CDE0C4",
                      align="RIGHT"))
    # decorative ruler ticks under band
    els.append(C.ruler_ticks(56, 120, 968, n=28, color=C.SOIL))

    # hero title
    els.append(C.text(56, 190, 968, 96, "一块地，一季收成", 64, C.INK,
                      bold=True))
    els.append(C.text(56, 292, 968, 60, "禾风里 · 开放日报名", 36, C.CLAY,
                      bold=True))
    els.append(C.leaf_mark(980, 232, 26, C.LEAF))

    # when / where card
    els.append(C.box(56, 390, 968, 280, C.PAPER2, radius=18, border=C.LINE,
                     border_w=1, shadow="0 6 18 0 #6B4A2F22 NORMAL"))
    els.append(C.section(88, 424, 900, "时间与地点", size=26))
    rows = [
        ("开放日", "4 月 20 日（周六）09:00–16:00"),
        ("市集时段", C.FACTS["market_day"] + " 同场"),
        ("地点", C.FACTS["address"] + " · 禾风里社区花园东门"),
        ("认养规模", "%d 块 %s 地块 · 已开放 %d 户认养" % (
            C.FACTS["plots"], C.FACTS["plot_size"], C.FACTS["households"])),
    ]
    ry = 482
    for k, v in rows:
        els.append(C.text(88, ry, 170, 34, k, 22, C.MUTED))
        C.fit(v, 24, 640, "row-%s" % k)
        els.append(C.text(262, ry - 2, 700, 38, v, 24, C.INK, bold=True))
        ry += 42

    # three highlights
    els.append(C.section(56, 700, 968, "来做什么", size=26))
    hi = [
        ("逛", "看 12 块地怎么种", "番茄黄瓜正挂果，随手可问种植户"),
        ("学", "厨余堆肥三步法", "现场教，学完可领一袋成品堆肥"),
        ("订", "周六市集尝鲜", "8 种当季菜，会员 8 折"),
    ]
    hy = 760
    for tag, t, d in hi:
        els.append(C.box(56, hy, 968, 104, C.PAPER2, radius=14, border=C.LINE))
        els.append(C.circle(118, hy + 52, 30, C.LEAF))
        els.append(C.text(88, hy + 34, 60, 40, tag, 26, C.PAPER, bold=True,
                          align="CENTER"))
        els.append(C.text(170, hy + 16, 600, 40, t, 26, C.INK, bold=True))
        els.append(C.text(170, hy + 56, 760, 32, d, 19, C.MUTED))
        hy += 124

    # QR placeholder + signup
    els.append(C.box(56, 1160, 968, 280, C.LEAFL, radius=18))
    qr = gen_qr(96, 1196, 208)
    els.append(qr)
    els.append(C.text(344, 1204, 640, 46, "扫码填写报名表", 30, C.LEAFD,
                      bold=True))
    els.append(C.text(344, 1256, 640, 64, "或到东门传达室登记姓名+手机尾号",
                      20, C.INK))
    els.append(C.chip(344, 1330, 300, 44, C.PAPER, "儿童需家长陪同", 18,
                      C.CLAY, border=C.CLAY))
    els.append(C.chip(660, 1330, 300, 44, C.PAPER, "雨天照常 · 部分棚内", 18,
                      C.LEAFD, border=C.LEAFD))
    els.append(C.footnote(344, 1392, 640,
                          "示意图案为占位图案，非真实二维码"))

    # footer
    els.append(C.line_h(56, 1470, 1024, C.LINE))
    els.append(C.footnote(56, 1482, 640, "主办：禾风里社区共耕花园（虚构演示项目）"))
    els.append(C.footnote(600, 1482, 424, "咨询：前台 010-8888-0000",
                          align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-01-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


def gen_qr(x, y, s):
    """deterministic decorative QR-like placeholder (NOT functional)."""
    rnd = random.Random(420)
    cells = 21
    cs = s / float(cells)
    out = [C.box(x - 8, y - 8, s + 16, s + 16, "#FFFFFF", radius=10,
                 border=C.LEAF, border_w=2)]
    for r in range(cells):
        for c in range(cells):
            finder = ((r < 7 and c < 7) or (r < 7 and c >= cells - 7)
                      or (r >= cells - 7 and c < 7))
            if finder:
                continue
            if rnd.random() < 0.45:
                out.append(C.box(x + c * cs, y + r * cs, cs + 0.3, cs + 0.3,
                                 C.INK))
    for (fr, fc) in [(0, 0), (0, cells - 7), (cells - 7, 0)]:
        fx, fy = x + fc * cs, y + fr * cs
        out.append(C.box(fx, fy, cs * 7, cs * 7, "#00000000",
                         border=C.INK, border_w=int(cs * 1.6)))
        out.append(C.box(fx + cs * 2, fy + cs * 2, cs * 3, cs * 3, C.INK))
    return "".join(out)


if __name__ == "__main__":
    main()
