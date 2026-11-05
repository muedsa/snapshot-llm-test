#!/usr/bin/env python3
"""Apply the real v2 visual fixes found by ViewImage review, in one pass.

Every replacement is asserted to match exactly once so a silent miss is impossible.
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent
A = BASE / "art_a.py"
B = BASE / "art_b.py"


def rep(path, old, new, tag):
    t = path.read_text(encoding="utf-8")
    n = t.count(old)
    assert n == 1, "%s: expected 1 match, got %d" % (tag, n)
    path.write_text(t.replace(old, new), encoding="utf-8")
    print("patched", tag)


# ---- case-02: unit-price labels must sit OUTSIDE the bars ------------------
rep(A, '''    BX, BW = 370, 590
    for i, (name, spec, total) in enumerate(rows):
        v = price_per_100g(float(spec[:-1]), total)
        is_best = (name == best[0])
        y = 160 + i * 116
        if is_best:
            c.rect(36, y - 8, 1128, 104, "#FFF8E1", radius=16,
                   border="2 SOLID #E0A83B")
        c.text(56, y + 6, 290, 34, name, 23, "#12293F", bold=True)
        c.text(56, y + 44, 290, 28, spec + "  ·  总价 ¥%.2f" % total, 16,
               "#5B708C")
        # bar
        bl = BW * v / maxv
        c.rect(BX, y + 12, BW, 34, "#E2EAF3", radius=8)
        c.rect(BX, y + 12, bl, 34,
               "#E0A83B" if is_best else "#4A86C8", radius=8)
        c.text(BX + BW - 210, y + 14, 200, 30,
               "¥%.2f / 100g" % v, 22,
               "#B45309" if is_best else "#1D4E74", bold=True,
               align="RIGHT", font=LATIN)
        if is_best:
            X.chip(c, 980, y + 4, 150, 34, "最划算", "#E0A83B", "#FFFFFF",
                   16, radius=17)
        c.text(56, y + 76, 1000, 22,
               "每 100g 单价 = 总价 ÷ 净含量 × 100", 14, "#8AA0B8", font=MONO)''',
     '''    BX, BW = 370, 460
    for i, (name, spec, total) in enumerate(rows):
        v = price_per_100g(float(spec[:-1]), total)
        is_best = (name == best[0])
        y = 160 + i * 116
        if is_best:
            c.rect(36, y - 8, 1128, 104, "#FFF8E1", radius=16,
                   border="2 SOLID #E0A83B")
        c.text(56, y + 6, 290, 34, name, 23, "#12293F", bold=True)
        c.text(56, y + 44, 290, 28, spec + "  ·  总价 ¥%.2f" % total, 16,
               "#5B708C")
        # bar (ends at x=830); label lives in its own column to the right
        bl = BW * v / maxv
        c.rect(BX, y + 12, BW, 34, "#E2EAF3", radius=8)
        c.rect(BX, y + 12, bl, 34,
               "#E0A83B" if is_best else "#4A86C8", radius=8)
        c.text(846, y + 14, 140, 30,
               "¥%.2f / 100g" % v, 19,
               "#B45309" if is_best else "#1D4E74", bold=True,
               align="RIGHT", font=LATIN)
        if is_best:
            X.chip(c, 1006, y + 4, 140, 34, "最划算", "#E0A83B", "#FFFFFF",
                   16, radius=17)
        c.text(56, y + 76, 1000, 22,
               "每 100g 单价 = 总价 ÷ 净含量 × 100", 14, "#8AA0B8", font=MONO)''',
     "case-02 bars/labels")

rep(A, '''    c.text(60, 800, 900, 30, "按每周买 3 袋算，一个月约省 ¥%.2f" %
           ((maxv - price_per_100g(float(best[1][:-1]), best[2])) * 5 * 4),
           18, "#BBD8F2")''',
     '''    c.text(60, 800, 900, 30, "按每月 20 份的单价差累计估算，约省 ¥%.2f" %
           ((maxv - price_per_100g(float(best[1][:-1]), best[2])) * 20),
           18, "#BBD8F2")''',
     "case-02 wording")

# ---- case-06: remove mixed-language word ----------------------------------
rep(B, '''    c.text(68, 998, 960, 50,
           "站牌是一列 22:15 / 22:31 / 22:43 / 23:05… 的时刻，得逐行比对、还要自己 subtract 出等待时间。",
           19, "#DCD6F7")''',
     '''    c.text(68, 998, 960, 50,
           "站牌是一列 22:15 / 22:31 / 22:43 / 23:05… 的时刻，得逐行比对、还要自己算出等待时间。",
           19, "#DCD6F7")''',
     "case-06 wording")

# ---- case-07: remove crossing connector, enlarge root, fix grey-bucket label
rep(B, '''    X.curve(c, (650, 450), (650, 560), (1090, 560), (1090, 628),
            3, "#C9B9A8")''',
     '''    # the "none of the above" branch is labelled locally instead of a
    # long curve that would cross the three question->bucket connectors''',
     "case-07 crossing curve")

rep(B, '''    c.circle(root[0], root[1], 68, "#123A33")
    c.text(root[0] - 118, root[1] - 30, 236, 60, "这是什么东西？", 22,
           "#FFFFFF", bold=True, align="CENTER")''',
     '''    c.circle(root[0], root[1], 82, "#123A33")
    c.text(root[0] - 130, root[1] - 28, 260, 56, "这是什么东西？", 20,
           "#FFFFFF", bold=True, align="CENTER")''',
     "case-07 root node")

rep(B, '''    c.text(940, 596, 300, 28, "三个都不是 → 其他", 16, "#8A7A5C",
           align="CENTER")''',
     '''    c.text(990, 590, 200, 28, "三个都不是 → 这里", 15, "#8A7A5C",
           align="CENTER")
    c.rect(1088, 618, 4, 10, "#C9B9A8")''',
     "case-07 grey bucket label")

print("all v2 fixes applied")
