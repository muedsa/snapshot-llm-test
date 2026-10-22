# -*- coding: utf-8 -*-
"""B03 case-08 · 市集入口盲文导览牌 (1400x700).

user_goal: 触障人士在市集入口摸读+常人远看：三个目的地(中英文+方向箭头)
           盲文可对照，服务台电话可达。
technique: 一级盲文(Grade 1)英文字母点位表驱动的程序化点字单元
           (左列1,2,3/右列4,5,6, 2x3 凸点), 凸点用底圆+高光小圆。
数据: 编码表抽查断言(A=1,E=15,F=124,I=24,L=123,N=1345,O=135,S=234,T=2345)；
      TOILET/EAST/INFO 每词字母全部在表内；14格40点总数断言；
      点径/点距常量恒定断言(CELL_W==COL_GAP+2*DOT_R==36)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1400, 700

NAVY = "#14213D"
PAPER = "#F4F1E8"
INK = "#1A1A1A"
DOT_HL = "#FFFFFF"

# standard English (Grade 1) braille letter dot values, dots 1..6
BRAILLE = {
    "a": (1,), "b": (1, 2), "c": (1, 4), "d": (1, 4, 5), "e": (1, 5),
    "f": (1, 2, 4), "g": (1, 2, 4, 5), "h": (1, 2, 5), "i": (2, 4),
    "j": (2, 4, 5), "k": (1, 3), "l": (1, 2, 3), "m": (1, 3, 4),
    "n": (1, 3, 4, 5), "o": (1, 3, 5), "p": (1, 2, 3, 4),
    "q": (1, 2, 3, 4, 5), "r": (1, 2, 3, 5), "s": (2, 3, 4),
    "t": (2, 3, 4, 5), "u": (1, 3, 6), "v": (1, 2, 3, 6),
    "w": (2, 4, 5, 6), "x": (1, 3, 4, 6), "y": (1, 3, 4, 5, 6),
    "z": (1, 3, 5, 6),
}

# dot slot offsets within one cell: (col, row), dots numbered 1..6
SLOTS = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}

PANELS = [
    ("洗手间", "TOILET", "restroom"),
    ("东门", "EAST", "exit"),
    ("服务台", "INFO", "help"),
]

PANEL_X = [60, 500, 940]
PANEL_W = 400
PANEL_Y, PANEL_H = 100, 380

DOT_R = 8.0
COL_GAP = 20.0        # distance between the two dot columns
ROW_GAP = 22.0
CELL_W = COL_GAP + 2 * DOT_R          # 36
CELL_GAP = 26.0


def cell_dots(word):
    """total raised dots for a word."""
    return sum(len(BRAILLE[ch]) for ch in word.lower())


def facts():
    assert BRAILLE["a"] == (1,)
    assert BRAILLE["e"] == (1, 5)
    assert BRAILLE["f"] == (1, 2, 4)
    assert BRAILLE["i"] == (2, 4)
    assert BRAILLE["l"] == (1, 2, 3)
    assert BRAILLE["n"] == (1, 3, 4, 5)
    assert BRAILLE["o"] == (1, 3, 5)
    assert BRAILLE["s"] == (2, 3, 4)
    assert BRAILLE["t"] == (2, 3, 4, 5)
    # dot geometry is constant for every cell (same diameter & spacing)
    assert COL_GAP + 2 * DOT_R == CELL_W == 36.0
    total_cells = 0
    total_dots = 0
    for _, word, _ in PANELS:
        for ch in word.lower():
            assert ch in BRAILLE, ch
            assert all(d in SLOTS for d in BRAILLE[ch])
            assert len(set(BRAILLE[ch])) == len(BRAILLE[ch])
        total_cells += len(word)
        total_dots += cell_dots(word)
    assert total_cells == 6 + 4 + 4 == 14
    assert total_dots == cell_dots("TOILET") + cell_dots("EAST") + \
        cell_dots("INFO") == 40
    return dict(total_cells=total_cells, total_dots=total_dots)


def braille_row(x, y, word, color=INK):
    """render a word as braille cells starting at (x,y); returns element str
    and total dots drawn."""
    els = []
    dots = 0
    for i, ch in enumerate(word.lower()):
        cx0 = x + i * (CELL_W + CELL_GAP)
        vals = BRAILLE[ch]
        dots += len(vals)
        for d in vals:
            col, row = SLOTS[d]
            px = cx0 + DOT_R + col * COL_GAP
            py = y + DOT_R + row * ROW_GAP
            els.append(C.circle(px, py, DOT_R, color))
            els.append(C.circle(px - 2.2, py - 2.2, 2.6, DOT_HL))
    return "".join(els), dots


def icon(kind, cx, cy):
    if kind == "restroom":
        return (C.circle(cx, cy - 26, 13, NAVY)
                + C.box(cx - 14, cy - 10, 28, 40, NAVY, radius=12)
                + C.box(cx - 22, cy + 2, 10, 26, NAVY, radius=5)
                + C.box(cx + 12, cy + 2, 10, 26, NAVY, radius=5)
                + C.box(cx - 14, cy + 30, 12, 26, NAVY, radius=5)
                + C.box(cx + 2, cy + 30, 12, 26, NAVY, radius=5))
    if kind == "exit":
        return (C.box(cx - 34, cy - 34, 40, 68, "#00000000", radius=6,
                      border=NAVY, border_w=5)
                + C.seg(cx + 12, cy, cx + 40, cy, 8, NAVY)
                + C.seg(cx + 26, cy - 14, cx + 42, cy, 8, NAVY)
                + C.seg(cx + 26, cy + 14, cx + 42, cy, 8, NAVY))
    # help: info badge
    return (C.circle(cx, cy, 34, NAVY)
            + C.text(cx - 34, cy - 24, 68, 48, "i", 40, "#FFFFFF", bold=True,
                     italic=True, align="CENTER"))


def main():
    f = facts()
    els = [C.box(0, 0, W, H, PAPER)]
    # header
    els.append(C.box(0, 0, W, 70, NAVY))
    els.append(C.text(40, 16, 760, 40, "市集入口 · 触摸导览牌", 28,
                      "#F6F3EA", bold=True))
    els.append(C.text(500, 24, 460, 28, "MARKET ENTRANCE · TACTILE", 16,
                      "#7E96BC", align="LEFT", letter_space=6))
    els.append(C.text(1360 - 320, 24, 320, 28, "一级盲文 Grade 1", 17,
                      "#A9BBD8", align="RIGHT"))

    drawn_dots = 0
    for (px, (cn, word, kind)) in zip(PANEL_X, PANELS):
        els.append(C.box(px, PANEL_Y, PANEL_W, PANEL_H, "#FFFFFF", radius=14,
                         border="#C9BFA6"))
        els.append(icon(kind, px + 74, PANEL_Y + 92))
        els.append(C.text(px + 150, PANEL_Y + 44, 230, 44, cn, 32, NAVY,
                          bold=True))
        els.append(C.text(px + 150, PANEL_Y + 92, 230, 30, word, 19, "#6B6355",
                          letter_space=3))
        els.append(C.seg(px + 28, PANEL_Y + 180, px + PANEL_W - 28,
                         PANEL_Y + 180, 1.5, "#D8CFBC"))
        els.append(C.text(px + 28, PANEL_Y + 196, 340, 26,
                          "点字（英文字母对照）", 15, "#8A8274"))
        row, dots = braille_row(px + 30, PANEL_Y + 234, word)
        els.append(row)
        drawn_dots += dots
        # tactile direction arrow below the cells (clear of 6-cell rows)
        ax = px + 216
        ay = PANEL_Y + 330
        els.append(C.seg(ax - 26, ay, ax + 14, ay, 6, "#B3681C"))
        els.append(C.seg(ax + 2, ay - 12, ax + 16, ay, 6, "#B3681C"))
        els.append(C.seg(ax + 2, ay + 12, ax + 16, ay, 6, "#B3681C"))
        els.append(C.text(px + 28, PANEL_Y + 318, 160, 26,
                          "沿箭头方向直行", 15, "#8A8274"))
        if word == "INFO":      # service desk phone under the direction line
            els.append(C.text(px + 28, PANEL_Y + 348, 340, 22,
                              "电话 400-000-0000（演示）", 13, "#8A8274"))
    assert drawn_dots == f["total_dots"], (drawn_dots, f["total_dots"])

    # legend: dot numbering diagram
    ly = 500
    els.append(C.box(60, ly, 1280, 170, "#FFFFFF", radius=14, border="#C9BFA6"))
    lx, lyy = 100, ly + 34
    nums = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"}
    for d, (col, row) in SLOTS.items():
        px = lx + 12 + col * 56
        py = lyy + 12 + row * 42
        els.append(C.circle(px, py, 12, "#E3DCCB", border="#B9AE95"))
        els.append(C.text(px - 12, py - 10, 24, 20, nums[d], 13, "#5B4A2E",
                          bold=True, align="CENTER"))
    els.append(C.text(lx - 12, ly + 8, 150, 24, "点位编号", 14, "#5B4A2E",
                      bold=True, align="CENTER"))
    els.append(C.text(260, ly + 26, 560, 28,
                      "左列 = 点1·2·3　右列 = 点4·5·6", 17, "#2E2A25",
                      bold=True))
    els.append(C.text(260, ly + 58, 620, 28,
                      "示例：T=2·3·4·5　O=1·3·5　E=1·5　A=1　N=1·3·4·5", 16,
                      "#4A4438"))
    els.append(C.text(260, ly + 90, 640, 28,
                      "本牌盲文为英文一级盲文点位；中文名称以英文对照呈现", 15,
                      "#6B6355"))
    els.append(C.text(260, ly + 118, 640, 28,
                      "本样牌共 %d 个字母格 · %d 颗凸点（脚本按点位表生成并断言）"
                      % (f["total_cells"], f["total_dots"]), 15, "#6B6355"))
    # tactile sample dots (large, embossed) at right of legend
    sx = 960
    row, _ = braille_row(sx, ly + 40, "INFO", color="#3A3A44")
    els.append(row)
    els.append(C.text(sx - 10, ly + 132, 220, 24, "样例：INFO", 14, "#5B4A2E"))

    els.append(C.footnote(60, 676, 1280,
                          "市集入口导览牌为虚构演示样牌（电话为演示号码）；"
                          "盲文点位遵循英文一级盲文编码，"
                          "实际制作需以本地盲文规范复核", align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-08-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=PAPER)
    print("facts ok: cells=%d dots=%d drawn=%d"
          % (f["total_cells"], f["total_dots"], drawn_dots))


if __name__ == "__main__":
    main()
