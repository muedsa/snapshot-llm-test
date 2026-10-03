# -*- coding: utf-8 -*-
"""B01 case-06 -- 手工皮具版型技术图（蓝图样式）.

Every dimension, seam allowance, stitch-hole pitch and hole count is derived from
the piece table in millimetres, so the drawing, the dimension lines and the
cutting list can never drift apart.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, tw  # noqa: E402

NAME = "c06-leather-pattern"
W, H = 1400, 1010
SC = 2.6          # px per mm

BG = "#07253FFF"
PANEL = "#062033FF"
GRID = "#0E3A5FFF"
LINE = "#8FD8FFFF"
CUT = "#EAF7FFFF"
DIMC = "#5FC8F0FF"
HOLEC = "#FFD166FF"
TXT = "#DCEEFBFF"
ACC = "#FF8A5BFF"
MUT = "#7FA8C4FF"

PIECES = [
    ("A", "封面外片", 105, 148, 2, "植鞣革 1.6 mm"),
    ("B", "封底外片", 105, 148, 2, "植鞣革 1.6 mm"),
    ("C", "书脊条", 32, 148, 1, "植鞣革 1.2 mm"),
    ("D", "搭扣带", 20, 60, 1, "植鞣革 2.0 mm"),
]
SA = 5.0          # seam allowance, mm
PITCH = 12.0      # stitch pitch, mm


def build(ver="v1", outdir=None):
    area = {p[0]: (p[2] + 2 * SA) * (p[3] + 2 * SA) for p in PIECES}
    holes = {}
    for pid, nm, wmm, hmm, qty, mat in PIECES:
        w = (wmm - 2 * SA) * SC
        h = (hmm - 2 * SA) * SC
        per = 2 * (w + h)
        n = max(8, int(round(per / (PITCH * SC))))
        holes[pid] = n
    total_area = sum(area[p[0]] * p[4] for p in PIECES) / 100.0   # cm^2
    data = {
        "scale_px_per_mm": SC, "seam_allowance_mm": SA, "stitch_pitch_mm": PITCH,
        "pieces": [{"id": p[0], "name": p[1], "w_mm": p[2], "h_mm": p[3], "qty": p[4],
                    "material": p[5], "cut_w_mm": p[2] + 2 * SA,
                    "cut_h_mm": p[3] + 2 * SA,
                    "area_cm2": round(area[p[0]] / 100.0, 2),
                    "stitch_holes": holes[p[0]]} for p in PIECES],
        "total_leather_cm2": round(total_area, 1),
        "total_stitch_holes": sum(holes.values()),
        "thread_m_estimate": round(sum(holes.values()) * PITCH * 3.4 / 1000.0, 1),
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 88, "#04182AFF")
    d.box(0, 0, 8, 88, ACC)
    d.text(32, 14, "版型技术图 · 皮质 A6 田野笔记本封套", 28, TXT, "BOLD")
    d.text(32, 52, "图号 LP-A6-02 · 比例 1:1 等比 · 尺寸单位 mm · 缝份 %.1f mm · 针距 %.1f mm"
           % (SA, PITCH), 16, MUT)
    d.ctext(1000, 16, "版次 R3 · 2026-03-14 · 绘制：工作室（虚构）", 16, MUT, w=368, h=24,
            align="CENTER_RIGHT")
    d.ctext(1000, 46, "材料面积合计 %.0f cm² · 缝合孔 %d 个"
            % (total_area, sum(holes.values())), 16, HOLEC, w=368, h=24,
            align="CENTER_RIGHT")

    # ---------------------------------------------------------------- drawing
    DX, DY, DW, DH = 32, 104, 940, 700
    d.box(DX, DY, DW, DH, PANEL, radius=10, border="1 SOLID " + GRID)
    for gx in range(0, DW, 20):
        d.box(DX + gx, DY, 1, DH, GRID)
    for gy in range(0, DH, 20):
        d.box(DX, DY + gy, DW, 1, GRID)
    for gx in range(0, DW, 100):
        d.box(DX + gx, DY, 1, DH, "#17507CFF")
    for gy in range(0, DH, 100):
        d.box(DX, DY + gy, DW, 1, "#17507CFF")

    pos = {"A": (110, 200), "B": (440, 200), "C": (770, 200), "D": (900, 200)}

    def arrow_h(x, y, direction):
        d.seg(x, y, x - direction * 9, y - 4, DIMC, 1.4, radius=False)
        d.seg(x, y, x - direction * 9, y + 4, DIMC, 1.4, radius=False)

    def arrow_v(x, y, direction):
        d.seg(x, y, x - 4, y - direction * 9, DIMC, 1.4, radius=False)
        d.seg(x, y, x + 4, y - direction * 9, DIMC, 1.4, radius=False)

    def dim_h(x0, x1, y, label):
        d.box(x0, y, x1 - x0, 1, DIMC)
        arrow_h(x0, y, -1)
        arrow_h(x1, y, 1)
        lw = tw(label, 13, MONO) + 12
        d.box((x0 + x1) / 2 - lw / 2, y - 22, lw, 18, PANEL, radius=3)
        d.ctext((x0 + x1) / 2 - lw / 2, y - 22, label, 13, DIMC, family=MONO, w=lw,
                h=18, align="CENTER")

    def dim_v(y0, y1, x, label):
        d.box(x, y0, 1, y1 - y0, DIMC)
        arrow_v(x, y0, -1)
        arrow_v(x, y1, 1)
        # offset the rotated label off the line so the line cannot strike through it
        d.rtext(x - 13, (y0 + y1) / 2, label, 13, DIMC, -90, family=MONO)

    for pid, nm, wmm, hmm, qty, mat in PIECES:
        px, py = pos[pid]
        cw, ch = wmm * SC, hmm * SC
        ow, oh = (wmm + 2 * SA) * SC, (hmm + 2 * SA) * SC
        # cut outline (with seam allowance)
        d.box(px - SA * SC, py - SA * SC, ow, oh, "#0A3050FF", radius=4,
              border="2 SOLID " + CUT)
        # fold / finished line
        d.dashed(px, py, px + cw, py, LINE, 1.2, 7, 5)
        d.dashed(px + cw, py, px + cw, py + ch, LINE, 1.2, 7, 5)
        d.dashed(px + cw, py + ch, px, py + ch, LINE, 1.2, 7, 5)
        d.dashed(px, py + ch, px, py, LINE, 1.2, 7, 5)
        # grain arrow
        cx, cy = px + cw / 2, py + ch / 2
        d.box(cx - cw * 0.25, cy - 1, cw * 0.5, 2, "#2E6E9EFF")
        arrow_h(cx + cw * 0.25, cy, 1)
        d.ctext(px + 8, py + 8, pid, 22, HOLEC, "BOLD", family=MONO, w=30, h=28)
        d.ctext(px + 8, py + 34, clip(nm, 14, cw - 16), 14, TXT, w=cw - 16, h=20)
        # stitch holes
        iw, ih = (wmm - 2 * SA) * SC, (hmm - 2 * SA) * SC
        ix, iy = px + SA * SC, py + SA * SC
        n = holes[pid]
        for k in range(n):
            t = k / float(n)
            per = 2 * (iw + ih)
            s = t * per
            if s < iw:
                hx, hy = ix + s, iy
            elif s < iw + ih:
                hx, hy = ix + iw, iy + (s - iw)
            elif s < 2 * iw + ih:
                hx, hy = ix + iw - (s - iw - ih), iy + ih
            else:
                hx, hy = ix, iy + ih - (s - 2 * iw - ih)
            d.disc(hx, hy, 3.4, HOLEC)
        # corner notches
        for nx, ny in ((px, py), (px + cw, py), (px, py + ch), (px + cw, py + ch)):
            d.box(nx - 2, ny - 6, 4, 12, ACC)
        dim_h(px - SA * SC, px - SA * SC + ow, py + oh + 38, "%.1f" % (wmm + 2 * SA))
        # only the two large pieces get a vertical dimension line: at this row
        # spacing a third one would sit on top of the neighbouring outline, and
        # B/C/D heights are already in the cutting list
        if pid in ("A", "B"):
            dim_v(py - SA * SC, py - SA * SC + oh, px - SA * SC - 30,
                  "%.1f" % (hmm + 2 * SA))

    d.text(130, 780, "C / D 两件的竖向尺寸见右栏裁断清单（158.0 / 70.0 mm）。", 13, MUT)

    # scale ruler
    RX, RY = 130, 740
    d.box(RX, RY, 260, 14, PANEL, radius=2, border="1 SOLID " + DIMC)
    for i in range(11):
        d.box(RX + i * 26, RY, 1.4, 14 if i % 5 else 20, DIMC)
        d.ctext(RX + i * 26 - 14, RY + 22, "%d" % (i * 10), 11, MUT, family=MONO,
                w=28, h=16, align="CENTER")
    d.text(RX + 280, RY - 2, "比例尺（mm）· 每格 10 mm", 13, MUT)

    # ---------------------------------------------------------------- right column
    RX0, RW0 = 992, 376
    d.box(RX0, 104, RW0, 300, PANEL, radius=10, border="1 SOLID " + GRID)
    d.text(RX0 + 18, 118, "裁断清单", 17, TXT, "BOLD")
    for i, p in enumerate(data["pieces"]):
        y = 148 + i * 60
        d.box(RX0 + 18, y + 6, 30, 30, "#0E3A5FFF", radius=4, border="1 SOLID " + LINE)
        d.ctext(RX0 + 18, y + 6, p["id"], 17, HOLEC, "BOLD", family=MONO, w=30, h=30,
                align="CENTER")
        d.ctext(RX0 + 58, y, p["name"], 15, TXT, w=140, h=22)
        d.ctext(RX0 + 58, y + 22, "%d × %.0f×%.0f mm" % (p["qty"], p["cut_w_mm"],
                                                         p["cut_h_mm"]), 13, MUT,
                family=MONO, w=180, h=18)
        d.ctext(RX0 + 246, y, "%.1f cm²" % p["area_cm2"], 14, DIMC, family=MONO,
                w=112, h=22, align="CENTER_RIGHT")
        d.ctext(RX0 + 246, y + 22, "%d 孔" % p["stitch_holes"], 13, HOLEC, family=MONO,
                w=112, h=18, align="CENTER_RIGHT")

    d.box(RX0, 420, RW0, 190, PANEL, radius=10, border="1 SOLID " + GRID)
    d.text(RX0 + 18, 434, "材料与五金", 17, TXT, "BOLD")
    mats = [("皮料", "植鞣革 1.6/1.2/2.0 mm · 共 %.0f cm²" % total_area),
            ("缝线", "0.6 mm 圆蜡线 · 约 %.1f m" % data["thread_m_estimate"]),
            ("五金", "12 mm 黄铜按扣 ×1 · 2 mm 铆钉 ×2"),
            ("边油", "哑光深棕，两遍打磨"),
            ("工具", "菱斩 4 mm · 间距规 · 挖槽器")]
    for i, (k, v) in enumerate(mats):
        y = 462 + i * 28
        d.text(RX0 + 18, y, k, 14, HOLEC)
        d.ctext(RX0 + 84, y - 1, clip(v, 14, 286), 14, TXT, w=286, h=20)

    d.box(RX0, 626, RW0, 178, PANEL, radius=10, border="1 SOLID " + GRID)
    d.text(RX0 + 18, 640, "图例", 17, TXT, "BOLD")
    leg = [(CUT, "实线：裁断线（含缝份）"), (LINE, "虚线：折线 / 成品轮廓"),
           (HOLEC, "圆点：缝合孔（针距 %.0f mm）" % PITCH), (ACC, "方块：对位记号"),
           ("#2E6E9EFF", "箭头：皮料延伸方向（背脊）")]
    for i, (col, lab) in enumerate(leg):
        y = 672 + i * 26
        d.box(RX0 + 18, y + 4, 22, 12, col, radius=3)
        d.ctext(RX0 + 50, y, clip(lab, 14, 300), 14, MUT, w=300, h=20)

    # ---------------------------------------------------------------- footer
    d.box(32, 824, 1336, 162, PANEL, radius=10, border="1 SOLID " + GRID)
    d.text(52, 838, "工序与注意", 17, TXT, "BOLD")
    steps = [
        ("01", "划线", "银笔沿版型描线，缝份线用间距规复核"),
        ("02", "打孔", "菱斩垂直下锤，四角对位孔先打"),
        ("03", "削边", "皮边削 45°，由粗到细三级打磨"),
        ("04", "缝合", "双针马鞍缝，起收针各回缝两针"),
        ("05", "封边", "边油两遍，每遍干 20 分钟再打磨"),
    ]
    for i, (no, k, v) in enumerate(steps):
        x = 52 + i * 264
        d.ctext(x, 872, no, 20, ACC, "BOLD", family=MONO, w=34, h=26)
        d.ctext(x + 40, 872, k, 16, TXT, "BOLD", w=200, h=24)
        d.ctext(x, 900, clip(v, 14, 236), 14, MUT, w=236, h=20)
    d.box(52, 950, 1296, 1, GRID)
    d.ctext(52, 958, "本图为 Snapshot DSL 演示作品：版型、工坊与图号均为虚构示例，尺寸按 mm 由脚本换算为像素。",
            13, MUT, w=1296, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps(info, ensure_ascii=False, indent=2))
