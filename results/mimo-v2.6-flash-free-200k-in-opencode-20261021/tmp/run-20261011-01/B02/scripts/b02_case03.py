# -*- coding: utf-8 -*-
"""B02 case-03 · 周六市集价目牌 (1080x1350, 摊位立牌 1m 处快速扫读).

user_goal: 3 秒找到想买的菜、单价与会员折后价。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1080, 1350


def main():
    C.assert_facts()
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # header band
    els.append(C.box(0, 0, W, 150, C.LEAFD))
    els.append(C.brand_header(56, 26, 560, color=C.PAPER, mark=C.SUN,
                              size=26, latin_size=12))
    els.append(C.text(56, 76, 700, 56, "周六市集 · 今日菜价", 38, C.PAPER,
                      bold=True))
    els.append(C.chip(796, 40, 228, 52, C.CLAY, C.FACTS["market_day"]
                      .replace("每周", "周"), 20, "#FFFFFF", radius=26))
    els.append(C.text(796, 100, 228, 30, "摊位 B12 · 东门第二排", 15, "#CDE0C4",
                      align="CENTER"))

    # price grid: 8 crops x (单价, 会员价)
    cols, rows = 2, 4
    gx, gy = 56, 190
    cw, ch = (W - 2 * 56 - 24) / cols, 200
    for i, (name, price) in enumerate(C.MARKET_PRICES):
        r, c = divmod(i, cols)
        x = gx + c * (cw + 24)
        y = gy + r * (ch + 20)
        member = round(price * C.FACTS["member_discount"])
        els.append(C.box(x, y, cw, ch, C.PAPER2, radius=16, border=C.LINE,
                         shadow="0 4 14 0 #6B4A2F1A NORMAL"))
        els.append(C.text(x + 28, y + 22, 260, 52, name, 40, C.INK, bold=True))
        els.append(C.leaf_mark(x + cw - 56, y + 44, 16, C.LEAF, stem=False))
        els.append(C.text(x + 28, y + 84, 300, 30, "本地当季 · 现摘", 18,
                          C.MUTED))
        # price row
        els.append(C.text(x + 28, y + 124, 250, 58, "%d" % price, 46, C.CLAY,
                          bold=True))
        els.append(C.text(x + 118, y + 142, 120, 32, "元/斤", 19, C.MUTED))
        els.append(C.box(x + cw - 218, y + 118, 190, 62, C.LEAFL, radius=12))
        els.append(C.text(x + cw - 206, y + 124, 166, 30, "会员", 17, C.LEAFD,
                          bold=True))
        els.append(C.text(x + cw - 206, y + 148, 120, 30, "%d 元" % member, 22,
                          C.LEAFD, bold=True))

    # rules bar
    ry = gy + rows * (ch + 20) + 6
    els.append(C.box(56, ry, W - 112, 128, C.LEAFL, radius=16))
    rules = ["会员 8 折（出示群内电子卡）", "每样限购 5 斤", "微信/现金均可"]
    for i, rr in enumerate(rules):
        els.append(C.circle(92, ry + 36 + i * 34, 5, C.CLAY))
        els.append(C.text(110, ry + 22 + i * 34, 560, 30, rr, 20, C.INK))
    els.append(C.box(640, ry + 22, 384, 84, "#FFFFFF", radius=12,
                     border=C.LEAF))
    els.append(C.text(660, ry + 32, 344, 30, "卖完为止 · 明早 8 点补货", 19,
                      C.LEAFD, bold=True))
    els.append(C.text(660, ry + 62, 344, 30, "可预订下周菜篮，见旁侧卡片", 17,
                      C.MUTED))

    # footer
    els.append(C.line_h(56, H - 92, W - 56, C.LINE))
    els.append(C.footnote(56, H - 78, 700,
                          "禾风里社区共耕花园 · 虚构演示价目；菜价随行就市"))
    els.append(C.footnote(700, H - 78, 324, "更新 4.20 09:00", align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-03-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
