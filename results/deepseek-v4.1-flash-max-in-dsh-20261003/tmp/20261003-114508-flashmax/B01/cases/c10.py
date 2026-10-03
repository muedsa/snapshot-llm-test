# -*- coding: utf-8 -*-
"""B01 case-10 -- 茶叶风味轮（评茶用，方形挂图）.

The wheel is a real radial layout: inner ring = six tea families, middle ring =
twelve sub-styles, outer ring = thirty-six descriptors.  Sector angles are
derived from the number of children each family has, and every label is rotated
so it reads outward on the right half and inward on the left half.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, mix, tw  # noqa: E402

NAME = "c10-tea-wheel"
W, H = 1500, 1500

BG = "#14100EFF"
PANEL = "#1E1815FF"
TXT = "#F5EFE6FF"
DIM = "#A99B8AFF"
SUB = "#7A6E60FF"
GOLD = "#D9A441FF"

# family -> (colour, [ (sub-style, [descriptors...]) ])
FAMILIES = [
    ("绿茶", "#3F8F5BFF", [
        ("蒸青", ["海苔", "青豆", "鲜爽"]),
        ("炒青", ["栗香", "豆香", "回甘"]),
        ("烘青", ["兰花香", "清甜", "柔滑"]),
    ]),
    ("白茶", "#B9AE94FF", [
        ("白毫银针", ["毫香", "蜜韵", "清泉"]),
        ("白牡丹", ["花香", "枣香", "绵柔"]),
    ]),
    ("黄茶", "#C9A227FF", [
        ("黄芽", ["锅巴香", "甜玉米", "醇和"]),
        ("黄小茶", ["熟栗", "嫩香", "甘润"]),
    ]),
    ("青茶", "#2E7D8F", [
        ("清香型", ["兰韵", "奶香", "喉韵"]),
        ("浓香型", ["焙火", "焦糖", "果干"]),
        ("陈香型", ["木质", "药香", "陈韵"]),
    ]),
    ("红茶", "#A8412EFF", [
        ("小种", ["松烟", "桂圆", "蜜糖"]),
        ("工夫", ["花果", "薯香", "甜醇"]),
    ]),
    ("黑茶", "#5A4230FF", [
        ("熟普", ["陈香", "木香", "滑厚"]),
        ("六堡", ["槟榔", "松烟", "醇陈"]),
        ("茯砖", ["菌花香", "陈皮", "绵甜"]),
    ]),
]
R0, R1, R2, R3 = 96.0, 236.0, 384.0, 560.0     # ring boundaries in px
CX, CY = 720.0, 790.0


def build(ver="v1", outdir=None):
    n_sub = sum(len(f[2]) for f in FAMILIES)
    n_desc = sum(len(s[1]) for f in FAMILIES for s in f[2])
    data = {
        "rings": {"inner_px": R0, "family_band_px": R1 - R0, "style_band_px": R2 - R1,
                  "descriptor_band_px": R3 - R2},
        "family_count": len(FAMILIES), "style_count": n_sub,
        "descriptor_count": n_desc,
        "families": [{"name": f[0], "colour": f[1],
                      "styles": [s[0] for s in f[2]],
                      "descriptors": [x for s in f[2] for x in s[1]]} for f in FAMILIES],
        "usage": "从内到外依次定位：茶类 → 制法 → 风味描述；评审时按出现强度圈选。",
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.text(56, 44, "茶叶风味轮", 40, TXT, "BOLD")
    d.text(56, 100, "评茶用 · 6 个茶类 · %d 种制法 · %d 个风味描述" % (n_sub, n_desc),
           18, DIM)
    d.ctext(860, 46, "色环代表茶类，外环文字由内向外阅读", 16, DIM, w=584, h=24,
            align="CENTER_RIGHT")
    d.ctext(860, 76, "使用方法：先定位茶类，再找制法，最后圈出 3–5 个主调", 16, SUB,
            w=584, h=24, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- wheel base
    d.disc(CX, CY, R3 * 2 + 12, PANEL)
    d.disc(CX, CY, R3 * 2 - 4, "#191411FF")

    ang = -90.0
    fam_span = 360.0 / len(FAMILIES)
    for fi, (fname, col, styles) in enumerate(FAMILIES):
        a0 = ang + fi * fam_span
        a1 = a0 + fam_span
        # inner family ring
        d.arc_fill(CX, CY, R0, R1, col, a0 + 0.6, a1 - 0.6, step=7.0)
        # middle style ring, split in proportion to the descriptors each style carries
        total_desc = sum(len(s[1]) for s in styles)
        sa = a0
        for si, (sname, descs) in enumerate(styles):
            span = (a1 - a0) * len(descs) / float(total_desc)
            shade = mix(col, "#120E0CFF", 0.18 + 0.16 * (si % 3))
            d.arc_fill(CX, CY, R1 + 2, R2, shade, sa + 0.5, sa + span - 0.5, step=7.0)
            # style label, radial
            mid = math.radians(sa + span / 2.0)
            rm = (R1 + R2) / 2.0
            lab = sname
            wlab = tw(lab, 17) + 4
            if math.cos(mid) >= 0:
                px = CX + math.cos(mid) * (R1 + 14 + wlab / 2.0)
                py = CY + math.sin(mid) * (R1 + 14 + wlab / 2.0)
                d.rtext(px, py, lab, 17, TXT, math.degrees(mid), "BOLD")
            else:
                px = CX + math.cos(mid) * (R2 - 14 - wlab / 2.0)
                py = CY + math.sin(mid) * (R2 - 14 - wlab / 2.0)
                d.rtext(px, py, lab, 17, TXT, math.degrees(mid) + 180, "BOLD")
            # outer descriptor band
            da = sa
            for dtext in descs:
                dspan = span / len(descs)
                dm = math.radians(da + dspan / 2.0)
                dcol = mix(col, "#F5EFE6FF", 0.42)
                d.arc_fill(CX, CY, R2 + 3, R3, dcol, da + 0.6, da + dspan - 0.6, step=9.0)
                wl = tw(dtext, 18) + 4
                if math.cos(dm) >= 0:
                    px = CX + math.cos(dm) * (R2 + 16 + wl / 2.0)
                    py = CY + math.sin(dm) * (R2 + 16 + wl / 2.0)
                    d.rtext(px, py, dtext, 18, "#221B16FF", math.degrees(dm))
                else:
                    px = CX + math.cos(dm) * (R3 - 16 - wl / 2.0)
                    py = CY + math.sin(dm) * (R3 - 16 - wl / 2.0)
                    d.rtext(px, py, dtext, 18, "#221B16FF", math.degrees(dm) + 180)
                # thin divider between descriptors
                d.seg(CX + math.cos(math.radians(da)) * (R2 + 3),
                      CY + math.sin(math.radians(da)) * (R2 + 3),
                      CX + math.cos(math.radians(da)) * R3,
                      CY + math.sin(math.radians(da)) * R3, "#14100EFF", 1.4)
                da += dspan
            sa += span
            # family label
            fm = math.radians((a0 + a1) / 2.0)
            rfm = (R0 + R1) / 2.0
            wf = tw(fname, 26) + 6
            if math.cos(fm) >= 0:
                px = CX + math.cos(fm) * (R0 + 18 + wf / 2.0)
                py = CY + math.sin(fm) * (R0 + 18 + wf / 2.0)
                d.rtext(px, py, fname, 26, "#FFFFFFFF", math.degrees(fm), "BOLD")
            else:
                px = CX + math.cos(fm) * (R1 - 18 - wf / 2.0)
                py = CY + math.sin(fm) * (R1 - 18 - wf / 2.0)
                d.rtext(px, py, fname, 26, "#FFFFFFFF", math.degrees(fm) + 180, "BOLD")
            # radial separator between families
            d.seg(CX + math.cos(math.radians(a0)) * R0, CY + math.sin(math.radians(a0)) * R0,
                  CX + math.cos(math.radians(a0)) * R3, CY + math.sin(math.radians(a0)) * R3,
                  "#14100EFF", 2.4)

    # centre
    d.disc(CX, CY, R0 * 2 - 6, "#0F0C0AFF")
    d.disc(CX, CY, R0 * 2 - 30, PANEL, border="2 SOLID " + GOLD)
    d.ctext(CX - 60, CY - 40, "茶", 40, GOLD, "BOLD", w=120, h=52, align="CENTER")
    d.ctext(CX - 60, CY + 18, "风味轮", 15, DIM, w=120, h=20, align="CENTER")

    # ---------------------------------------------------------------- legend
    LX, LY = 56, 1400
    for i, (fname, col, styles) in enumerate(FAMILIES):
        x = LX + i * 150
        d.box(x, LY, 16, 16, col, radius=4)
        d.text(x + 24, LY - 3, fname, 17, TXT, "BOLD")
        d.ctext(x + 24, LY + 20, "%d 种制法" % len(styles), 12, SUB, w=110, h=18)
    d.ctext(880, LY - 4, "本图为 Snapshot DSL 演示作品：风味描述为评茶常用词的示例整理，非任何机构标准。",
            13, SUB, w=564, h=20, align="CENTER_RIGHT")
    d.ctext(880, LY + 20, "色环仅按茶类着色，深浅表示同一茶类下的不同制法。", 13, SUB,
            w=564, h=20, align="CENTER_RIGHT")

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps({k: v for k, v in info.items() if k != "families"},
                     ensure_ascii=False, indent=2))
