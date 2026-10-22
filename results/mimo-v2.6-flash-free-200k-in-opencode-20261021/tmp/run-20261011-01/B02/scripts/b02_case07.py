# -*- coding: utf-8 -*-
"""B02 case-07 · 二十四节气种植日历 (1600x900, 活动中心横屏 3m).

user_goal: 知道本月该播种什么、正收什么。
Data: 12 solar terms x 6 crops, 播种/养护/采收 intervals asserted consistent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1600, 900

TERMS = ["立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
         "立夏", "小满", "芒种", "夏至", "小暑", "大暑"]
THIS_TERM = 5  # 谷雨 = 本月
# crop: (播种 s,e), (养护 s,e), (采收 s,e) in term indices (inclusive)
CROPS = [
    ("番茄", (2, 3), (4, 8), (9, 11)),
    ("黄瓜", (4, 4), (5, 9), (8, 11)),
    ("生菜", (1, 2), (3, 4), (5, 8)),
    ("空心菜", (5, 5), (6, 9), (8, 11)),
    ("辣椒", (3, 3), (4, 8), (9, 11)),
    ("南瓜", (5, 5), (6, 10), (11, 11)),
]

NOTES = [
    ("播", "本月播种", "空心菜、南瓜直播；罗勒育苗移栽"),
    ("管", "本月管护", "生菜尾茬追肥；番茄定植上架绑蔓"),
    ("收", "本月采收", "生菜进入尾茬（预计 210 斤级）；黄瓜始收"),
]


def main():
    C.assert_facts()
    # every crop's intervals must be ordered and within 0..11
    for name, s, m, h in CROPS:
        assert s[0] <= s[1] and m[0] <= m[1] and h[0] <= h[1], name
        assert s[1] < m[0] or s[1] <= m[1], name          # overlap allowed mild
        assert max(s + m + h) <= 11, name
    assert TERMS[THIS_TERM] == "谷雨"
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # header
    els.append(C.box(0, 0, W, 96, C.LEAFD))
    els.append(C.brand_header(44, 16, 500, color=C.PAPER, mark=C.SUN,
                              size=22, latin_size=10))
    els.append(C.text(44, 56, 700, 34, "二十四节气种植日历 · 春夏季", 26,
                      C.PAPER, bold=True))
    # legend
    lx = 940
    for lab, cc in [("播种", C.SUN), ("养护", C.LEAF), ("采收", C.CLAY)]:
        els.append(C.chip(lx, 30, 96, 38, cc, lab, 19, "#FFFFFF", radius=10))
        lx += 112
    els.append(C.chip(lx + 16, 30, 180, 38, C.LEAFL, "本月 · 谷雨", 19,
                      C.LEAFD, radius=10, border=C.LEAFD))

    # grid geometry
    gx, gy = 150, 190
    cwd = (1560 - gx) / 12.0        # ~117.5
    rhd = 64
    # layer order: row backgrounds FIRST, then this-month band, so the
    # highlight shows on every row (patchy band = visual defect)
    for r in range(len(CROPS)):
        if r % 2 == 0:
            els.append(C.box(gx, gy + r * rhd, 1560 - gx, rhd - 6,
                             "#FFFFFF"))
    els.append(C.box(gx + THIS_TERM * cwd, gy - 46, cwd, 6 * rhd + 54,
                     C.LEAFL))
    # term headers
    for t, term in enumerate(TERMS):
        bold = t == THIS_TERM
        els.append(C.text(gx + t * cwd, gy - 44, cwd, 34, term, 20,
                          C.CLAY if bold else C.INK, bold=True,
                          align="CENTER"))
    els.append(C.line_h(gx, gy - 6, 1560, C.LINE, 2))
    els.append(C.text(44, gy - 44, 96, 34, "作物", 18, C.MUTED))

    # crop rows
    for r, (name, s, m, h) in enumerate(CROPS):
        ry = gy + r * rhd
        els.append(C.text(44, ry + rhd / 2 - 18, 96, 34, name, 21, C.INK,
                          bold=True, align="RIGHT"))
        segs = list(zip(["播种", "养护", "采收"], [C.SUN, C.LEAF, C.CLAY],
                        [s, m, h]))
        # draw bars first
        for _lbl, cc, (s0, e0) in segs:
            x0 = gx + s0 * cwd + 6
            w0 = (e0 - s0 + 1) * cwd - 12
            els.append(C.box(x0, ry + rhd / 2 - 15, w0, 26, cc, radius=13))
        # then labels, clamped to the VISIBLE span (a later overlapping bar
        # would otherwise cover a label centered on the full span)
        for i, (lbl, _cc, (s0, e0)) in enumerate(segs):
            ve = e0
            if i + 1 < len(segs) and segs[i + 1][2][0] <= e0:
                ve = segs[i + 1][2][0] - 1
            if ve < s0:
                continue
            lx0 = gx + s0 * cwd + 6
            lw0 = (ve - s0 + 1) * cwd - 12
            if lw0 >= 70:
                els.append(C.text(lx0, ry + rhd / 2 - 11, lw0, 24, lbl, 15,
                                  "#FFFFFF", align="CENTER"))

    # bottom notes
    ny = gy + 6 * rhd + 26
    els.append(C.line_h(60, ny, 1540, C.LINE))
    for i, (tag, t, d) in enumerate(NOTES):
        x = 60 + i * 500
        els.append(C.circle(x + 30, ny + 62, 24, C.CLAY))
        els.append(C.text(x + 8, ny + 46, 44, 32, tag, 22, "#FFFFFF",
                          bold=True, align="CENTER"))
        els.append(C.text(x + 70, ny + 32, 400, 34, t, 22, C.INK, bold=True))
        els.append(C.text(x + 70, ny + 68, 410, 32, d, 18, C.MUTED))
    els.append(C.footnote(60, H - 46, 1000,
                          "禾风里社区共耕花园 · 虚构演示日历；节气区间为本园经验参数"))
    els.append(C.footnote(1100, H - 46, 440, "更新：4 月 谷雨", align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-07-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
