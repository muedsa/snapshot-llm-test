# -*- coding: utf-8 -*-
"""B01 case-03 -- 黑胶唱片封底 (LP back cover).

Side running times, total playing time, barcode bar widths and the corner groove
motif are all generated from the track list / catalog number, so the printed
numbers and the printed bars agree with each other.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, SERIF, clip, tw  # noqa: E402

NAME = "c03-vinyl-cover"
W, H = 1450, 1450

BG = "#121110FF"
DEEP = "#0A0A09FF"
CREAM = "#F2EDE4FF"
DIM = "#8A857CFF"
GOLD = "#C9A227FF"
TEAL = "#3E7C7BFF"
RULE = "#2A2724FF"

CATALOG = "NMLP-042"
TRACKS_A = [
    ("01", "夜航船", "Night Ferry", 4 * 60 + 12),
    ("02", "南十字", "Southern Cross", 5 * 60 + 38),
    ("03", "雾中灯塔", "Lighthouse in Fog", 3 * 60 + 55),
    ("04", "潮汐表", "Tide Table", 6 * 60 + 21),
    ("05", "甲板上的雨", "Rain on Deck", 4 * 60 + 47),
]
TRACKS_B = [
    ("06", "锚地清晨", "Anchorage, Morning", 5 * 60 + 3),
    ("07", "罗盘玫瑰", "Compass Rose", 4 * 60 + 29),
    ("08", "无线电静默", "Radio Silence", 7 * 60 + 14),
    ("09", "归港", "Homeport", 6 * 60 + 2),
]


def ms(t):
    return "%d:%02d" % (t // 60, t % 60)


def barcode_bits(seed_text):
    """Deterministic bar widths (in 1/9 inch units) derived from the catalog id."""
    h = 2166136261
    for ch in seed_text:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    bits, x = [], h
    for i in range(58):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        bits.append(1 + (x >> 7) % 4)
    return bits


def build(ver="v1", outdir=None):
    side_a = sum(t for *_, t in TRACKS_A)
    side_b = sum(t for *_, t in TRACKS_B)
    total = side_a + side_b
    bits = barcode_bits(CATALOG)
    data = {
        "catalog": CATALOG, "side_a_seconds": side_a, "side_b_seconds": side_b,
        "side_a_time": ms(side_a), "side_b_time": ms(side_b),
        "total_seconds": total, "total_time": "%d min %02d s" % (total // 60, total % 60),
        "track_count": len(TRACKS_A) + len(TRACKS_B),
        "barcode_modules": sum(bits), "barcode_bars": len(bits),
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- spine
    d.box(0, 0, 66, H, DEEP)
    d.box(66, 0, 2, H, "#00000000")
    d.rtext(33, H / 2, "北纬唱片  BEIWEI RECORDS   ·   %s   ·   夜航船 · 南十字摇篮曲   ·   33⅓ RPM   ·   STEREO"
            % CATALOG, 15, DIM, -90)

    # ---------------------------------------------------------------- groove texture
    # Painted first so every later element sits on top of it.  Concentric discs rather
    # than stroked arcs: a stroked ring costs ~2 elements per 6 px of arc and the
    # service caps one document at 4096 elements.
    for i, r in enumerate(range(268, 54, -5)):
        d.disc(1330, 1330, 2 * r, "#1B1815FF" if i % 2 else "#131110FF")
    d.disc(1330, 1330, 74, "#0E0D0CFF")
    d.disc(1330, 1330, 10, GOLD)

    # ---------------------------------------------------------------- label mark
    d.ring(140, 132, 34, 3, GOLD)
    d.disc(140, 132, 40, "#00000000")
    d.seg(140, 132, 140 + 34 * math.cos(math.radians(-58)),
          132 + 34 * math.sin(math.radians(-58)), GOLD, 3)
    d.seg(140, 132, 118, 158, GOLD, 3)
    d.seg(118, 158, 140 + 34 * math.cos(math.radians(-58)),
          132 + 34 * math.sin(math.radians(-58)), GOLD, 3)
    d.disc(140, 132, 10, BG)
    d.disc(140, 132, 5, GOLD)
    d.text(196, 106, "北纬唱片", 26, CREAM, "BOLD")
    d.text(196, 140, "BEIWEI RECORDS · 云岭", 14, DIM)

    d.ctext(900, 104, CATALOG, 20, GOLD, "BOLD", family=MONO, w=430, h=26,
            align="CENTER_RIGHT")
    d.ctext(900, 134, "33⅓ RPM · STEREO · 180 g 黑胶", 15, DIM, w=430, h=22,
            align="CENTER_RIGHT")
    d.ctext(900, 158, "2026 北纬唱片 第 42 号发行", 14, DIM, w=430, h=20,
            align="CENTER_RIGHT")

    d.box(120, 200, 1210, 1, RULE)
    # ---------------------------------------------------------------- titles
    d.text(120, 232, "夜航船", 72, CREAM, "BOLD", family=SERIF)
    d.text(126, 330, "南十字摇篮曲", 30, CREAM, family=SERIF)
    d.ctext(900, 300, "SOUTHERN CROSS LULLABIES", 20, GOLD, w=430, h=28,
            align="CENTER_RIGHT")
    d.ctext(900, 336, "九首为夜间航行而作的器乐曲", 16, DIM, w=430, h=24,
            align="CENTER_RIGHT")
    d.box(120, 396, 1210, 1, RULE)

    # ---------------------------------------------------------------- track lists
    def side(x0, x1, tag, colour, tracks, seconds):
        d.box(x0, 428, 26, 26, colour, radius=13)
        d.ctext(x0, 428, tag, 15, "#121110FF", "BOLD", family=MONO, w=26, h=26,
                align="CENTER")
        d.ctext(x0 + 38, 428, "SIDE " + tag, 17, CREAM, "BOLD", w=160, h=26)
        d.ctext(x1 - 180, 428, ms(seconds), 17, colour, "BOLD", family=MONO, w=180, h=26,
                align="CENTER_RIGHT")
        d.box(x0, 466, x1 - x0, 1, RULE)
        y = 486
        for i, (no, zh, en, dur) in enumerate(tracks):
            d.text(x0, y, no, 16, DIM, family=MONO)
            d.ctext(x0 + 44, y - 4, zh, 21, CREAM, w=250, h=30)
            d.ctext(x0 + 44, y + 24, en, 13, DIM, w=250, h=20)
            d.ctext(x1 - 90, y - 2, ms(dur), 17, CREAM, family=MONO, w=90, h=26,
                    align="CENTER_RIGHT")
            # tiny waveform motif whose bar count follows the track length
            bars = 18
            for b in range(bars):
                hh = 3 + 11 * abs(math.sin((i + 1) * 0.7 + b * 0.9 + dur * 0.01))
                d.box(x1 - 240 + b * 5, y + 6 + (12 - hh), 3, hh,
                      "#4A453EFF" if b % 3 else colour)
            d.box(x0, y + 54, x1 - x0, 1, "#201E1BFF")
            y += 66
        return y

    ya = side(120, 700, "A", GOLD, TRACKS_A, side_a)
    yb = side(870, 1330, "B", TEAL, TRACKS_B, side_b)

    # ---------------------------------------------------------------- credits
    CY = 846
    d.box(120, CY - 20, 1210, 1, RULE)
    creds = [
        ("制作", "林立 / 陈知远"),
        ("录音", "云岭声音工作室，2025 年 11 月"),
        ("混音与母带", "陈知远 @ North Lat 33"),
        ("弦乐", "云岭室内乐团（第 2、4、8 首）"),
        ("封面绘画", "沈鹭"),
        ("设计", "北纬唱片设计组"),
    ]
    for i, (k, v) in enumerate(creds):
        x = 120 + (i % 2) * 620
        y = CY + (i // 2) * 46
        d.text(x, y, k, 14, GOLD)
        d.ctext(x + 110, y - 2, clip(v, 15, 480), 15, CREAM, w=480, h=22)

    # ---------------------------------------------------------------- barcode
    BX, BY2, BW, BH2 = 120, 1020, 470, 104
    d.box(BX, BY2, BW, BH2, CREAM, radius=4)
    x = BX + 14
    unit = (BW - 28) / (sum(bits) + len(bits) * 0.9)
    for i, b in enumerate(bits):
        wbar = b * unit
        if x + wbar > BX + BW - 12:
            break
        if i % 2 == 0:
            d.box(x, BY2 + 12, wbar, BH2 - 42, "#121110FF")
        x += wbar + unit * 0.9
    d.ctext(BX, BY2 + BH2 - 26, "4 890123 456789", 15, "#121110FF", family=MONO,
            w=BW, h=20, align="CENTER")

    d.text(640, 1024, "℗ 2026 北纬唱片（虚构厂牌）", 15, CREAM)
    d.text(640, 1052, "© 2026 北纬唱片 · 保留所有权利", 15, DIM)
    d.text(640, 1080, "本封面为 Snapshot DSL 演示作品，乐队、厂牌与编号均属虚构", 14, DIM)
    d.text(640, 1108, "录制于云岭；母带于北纬 33° 完成", 14, DIM)

    # ---------------------------------------------------------------- legal rule
    d.box(120, 1160, 1210, 1, RULE)
    d.text(120, 1180, "STEREO  ·  %s  ·  TOTAL %s" % (CATALOG, ms(total)),
           15, DIM, family=MONO)
    d.ctext(1330 - 500, 1180, "SIDE A %s   /   SIDE B %s" % (ms(side_a), ms(side_b)),
            15, DIM, family=MONO, w=500, h=22, align="CENTER_RIGHT")
    d.ctext(120, 1220, "九首曲目 · 总时长 %d 分 %02d 秒 · 建议转速 33⅓ RPM · 播放前请清洁唱片"
            % (total // 60, total % 60), 15, DIM, w=900, h=22)
    d.text(120, 1270, "在夜间航行的船上，罗盘玫瑰指向的不是北方，而是记忆。", 17,
           "#6E6960FF", family=SERIF)
    d.box(120, 1320, 240, 3, GOLD)

    data["side_a_end_y"] = ya
    data["side_b_end_y"] = yb
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
