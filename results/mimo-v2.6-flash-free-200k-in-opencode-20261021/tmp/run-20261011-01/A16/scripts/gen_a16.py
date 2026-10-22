# -*- coding: utf-8 -*-
"""A16 corrected-report DSL generator (1280x900).

Builds a trustworthy quarterly-review report from inputs/source.csv:
- grouped revenue/cost bars on a SHARED ZERO baseline
- profit breakdown panel
- one data-grounded title, legend, unit 万元, all four quarters

Bar height = round(value * PX_PER_WAN) measured up from the shared zero
line y=ZERO_Y, so bar height directly encodes the value (verifiable via
the axes.scale recorded in corrected-data.json).

Usage: python gen_a16.py --dsl <path>
"""
import argparse
import pathlib

W, H = 1280, 900

BG = "#F5F7FB"
CARD = "#FFFFFF"
BORDER = "#E5E9F2"
DARK = "#1A2740"
MUTED = "#64748B"
GRID = "#E8EDF5"
REV = "#2563EB"          # revenue bar
COST = "#F59E0B"         # cost bar
PROFIT = "#16A34A"       # profit accent
CALLOUT_BG = "#FEF3E2"
CALLOUT_BORDER = "#F6D9A8"
FOOT = "#94A3B8"
CARD_BORDER_ATTR = f"1 SOLID {BORDER}"

# ---- chart geometry (shared zero baseline) ----
ZERO_Y = 500             # pixel y of value 0
PX_PER_WAN = 1.2         # pixels per 万元
PLOT_X0, PLOT_X1 = 170, 1160
BAR_W, BAR_GAP = 84, 16
CENTERS = [294, 541, 789, 1036]

# source.csv (万元)
DATA = [
    ("Q1", 120, 90, 30),
    ("Q2", 135, 108, 27),
    ("Q3", 128, 96, 32),
    ("Q4", 180, 126, 54),
]


def rect(x, y, w, h, color, radius=0, border=None):
    a = f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">' \
        f'<Container color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return a + "/></Positioned>"


def family(weight):
    if weight == "bold":
        return "Inter", "BOLD"
    if weight == "sb":
        return "Inter Semi Bold", None
    return "Inter", None


def text(x, glyph_top, s, fs, color, weight="reg", width=420):
    """Emit a left-aligned Text; glyph_top is the intended visible glyph top."""
    top = glyph_top - round(0.24 * fs)
    fam, style = family(weight)
    a = (f'<Positioned left="{x}" top="{top}" width="{width}" '
         f'height="{2 * fs + 8}"><Text fontSize="{fs}" color="{color}" '
         f'fontFamily="{fam}"')
    if style:
        a += f' fontStyle="{style}"'
    a += f' text="{s}"/></Positioned>'
    return a


def bar_top(v):
    return round(ZERO_Y - v * PX_PER_WAN)


def shapes():
    s = [rect(0, 0, W, H, BG)]
    # header chart card
    s.append(rect(64, 130, 1152, 430, CARD, radius=12, border=CARD_BORDER_ATTR))
    # gridlines 0/50/100/150/200
    for v in (0, 50, 100, 150, 200):
        y = bar_top(v)
        s.append(rect(PLOT_X0, y, PLOT_X1 - PLOT_X0, 1, GRID))
    # legend swatches
    s.append(rect(946, 162, 15, 15, REV, radius=3))
    s.append(rect(1046, 162, 15, 15, COST, radius=3))
    # bars: revenue (left) + cost (right) per quarter, from shared zero
    for i, (q, rev, cost, profit) in enumerate(DATA):
        c = CENTERS[i]
        rx, cx2 = c - BAR_W - BAR_GAP // 2, c + BAR_GAP // 2
        s.append(rect(rx, bar_top(rev), BAR_W, round(rev * PX_PER_WAN),
                      REV, radius=4))
        s.append(rect(cx2, bar_top(cost), BAR_W, round(cost * PX_PER_WAN),
                      COST, radius=4))
    # profit breakdown card
    s.append(rect(64, 590, 696, 240, CARD, radius=12, border=CARD_BORDER_ATTR))
    # focus callout card
    s.append(rect(790, 590, 426, 240, CALLOUT_BG, radius=12,
                  border=f"1 SOLID {CALLOUT_BORDER}"))
    return s


def texts():
    t = []
    # header
    t.append(text(64, 44, "季度复盘：Q4收入与利润双高", 32, DARK, "bold",
                  width=720))
    t.append(text(64, 92, "Q4收入180万元、利润54万元，均为全年最高；"
                          "Q3收入环比回落5.2%", 16, MUTED, width=880))
    # chart card labels
    t.append(text(96, 156, "收入与成本对比", 22, DARK, "bold"))
    t.append(text(96, 196, "单位：万元", 14, MUTED))
    # legend (correct mapping: revenue=blue, cost=amber)
    t.append(text(968, 158, "收入", 16, DARK, "reg", width=60))
    t.append(text(1068, 158, "成本", 16, DARK, "reg", width=60))
    # y-axis ticks (right side of plot start, left aligned at x=120)
    for v in (200, 150, 100, 50, 0):
        t.append(text(120, bar_top(v) - 9, str(v), 14, MUTED, width=44))
    # per-quarter labels, value labels, profit delta
    for i, (q, rev, cost, profit) in enumerate(DATA):
        c = CENTERS[i]
        rx, cx2 = c - BAR_W - BAR_GAP // 2, c + BAR_GAP // 2
        focus = (q == "Q4")
        # value labels above bars
        t.append(text(rx, bar_top(rev) - 24, str(rev), 16,
                      REV if not focus else REV, "bold", width=BAR_W + 20))
        t.append(text(cx2, bar_top(cost) - 24, str(cost), 16, "#B45309",
                      "bold", width=BAR_W + 20))
        # quarter label below zero line
        t.append(text(c - 22, 512, q, 16, DARK if focus else MUTED,
                      "bold" if focus else "reg", width=60))
        # profit under quarter
        t.append(text(c - 40, 536, f"利润{profit}", 14, PROFIT,
                      "reg", width=100))
    # profit breakdown panel
    t.append(text(96, 620, "利润明细（收入−成本）", 22, DARK, "bold"))
    for i, (q, rev, cost, profit) in enumerate(DATA):
        px_ = 96 + i * 165
        t.append(text(px_, 676, q, 16, MUTED, "reg", width=60))
        t.append(text(px_, 706, f"{profit} 万元", 26, DARK, "bold", width=150))
        rate = round(cost / rev * 100)
        t.append(text(px_, 750, f"成本率{rate}%", 14, MUTED, "reg", width=140))
    # focus callout
    t.append(text(818, 620, "重点观察 · Q4", 22, DARK, "bold"))
    t.append(text(818, 664, "Q4收入180万元、成本126万元，", 16, DARK))
    t.append(text(818, 692, "利润54万元，收入与利润均全年最高，", 16, DARK))
    t.append(text(818, 720, "成本率70%也最低；建议以Q4为标杆，", 16, DARK))
    t.append(text(818, 748, "复盘其成本结构并推广到全年。", 16, DARK))
    # footer
    t.append(text(64, 856, "数据来源：source.csv · 收入−成本=利润 · "
                           "纵轴自0起（共同零点）· 单位：万元", 13, FOOT,
                  width=760))
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    args = ap.parse_args()
    parts = ['<Snapshot type="png" background="%s">' % BG,
             '  <SizedBox width="%d" height="%d">' % (W, H),
             '    <Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    parts += ["    " + ln for ln in shapes()]
    parts += ["    " + ln for ln in texts()]
    parts += ["    </Stack>", "  </SizedBox>", "</Snapshot>", ""]
    out = pathlib.Path(args.dsl)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out.as_posix()} ({len(shapes())} shapes, {len(texts())} texts)")


if __name__ == "__main__":
    main()
