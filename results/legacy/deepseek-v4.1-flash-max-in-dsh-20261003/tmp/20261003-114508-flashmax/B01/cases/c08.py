# -*- coding: utf-8 -*-
"""B01 case-08 -- 播客单集波形与章节卡（方形，社交/节目页用）.

The waveform is generated from the same chapter table that prints the chapter
list, so the loud sections, the quiet gaps and the chapter boundaries agree.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, mix, tw  # noqa: E402

NAME = "c08-podcast-wave"
W, H = 1400, 1400

BG = "#101418FF"
PANEL = "#171C22FF"
LINE = "#2A323CFF"
TXT = "#F1F5F9FF"
DIM = "#8B98A8FF"
SUB = "#5F6B7AFF"
ACC = "#E8B44AFF"
ACC2 = "#5AC8B0FF"
ACC3 = "#E06C75FF"
ACC4 = "#7AA2F7FF"

DURATION = 58 * 60 + 12          # 58:12
CHAPTERS = [
    ("00:00", 0, "开场：我们为什么重新做这档节目", ACC2),
    ("02:14", 134, "嘉宾介绍：一位在河口工作了 11 年的人", ACC4),
    ("09:40", 580, "第一次转折：数据第一次说了相反的话", ACC3),
    ("21:05", 1265, "田野录音：凌晨四点的潮位站", ACC),
    ("33:18", 1998, "争论：模型到底该不该相信直觉", ACC3),
    ("45:50", 2750, "结论：三个可以带走的判断", ACC2),
    ("54:02", 3242, "尾声与下期预告", ACC4),
]
QUOTES = [
    ("21:47", "潮水不会因为我们的表格而改变时间。", "—— 受访者，河口站"),
    ("36:12", "如果模型和现场冲突，先去看现场。", "—— 本期嘉宾"),
    ("51:03", "所有长期观察，最后都变成耐心问题。", "—— 主播"),
]


def envelope(t, i):
    """Deterministic speech-like envelope: chapter gain x syllable ripple x pauses."""
    ch = 0
    for k, (_, start, _, _) in enumerate(CHAPTERS):
        if t >= start:
            ch = k
    gains = [0.72, 0.86, 0.95, 0.62, 0.98, 0.80, 0.55]
    g = gains[ch]
    ripple = 0.55 + 0.45 * abs(math.sin(t * 2.7 + i * 0.31))
    micro = 0.7 + 0.3 * abs(math.sin(t * 11.3 + i * 1.7))
    # silent gaps: before every chapter start and every ~7 minutes
    pause = 1.0
    for _, start, _, _ in CHAPTERS:
        if 0 <= start - t < 3.2:
            pause = 0.06
    if (t % 412) < 2.4:
        pause = 0.08
    return max(0.02, g * ripple * micro * pause)


def build(ver="v1", outdir=None):
    data = {
        "episode": "EP.042", "duration_seconds": DURATION,
        "duration_text": "%d:%02d" % (DURATION // 60, DURATION % 60),
        "chapters": [{"at": c[0], "seconds": c[1], "title": c[2]} for c in CHAPTERS],
        "chapter_count": len(CHAPTERS),
        "longest_chapter_min": round(max((CHAPTERS[i + 1][1] - CHAPTERS[i][1])
                                         for i in range(len(CHAPTERS) - 1)) / 60.0, 1),
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.text(56, 44, "潮位线", 22, ACC, "BOLD", spacing=2)
    d.text(56, 74, "一档关于长期观察的播客 · 第 3 季", 15, SUB)
    d.ctext(760, 44, "EP.042", 22, DIM, "BOLD", family=MONO, w=584, h=30,
            align="CENTER_RIGHT")
    d.ctext(760, 76, "2026-10-01 发布 · 时长 %s" % data["duration_text"], 15, SUB,
            w=584, h=22, align="CENTER_RIGHT")
    d.text(56, 128, "凌晨四点的潮位站", 54, TXT, "BOLD")
    d.text(56, 200, "嘉宾：周砚（河口观测站）·  主播：林一 ·  录制于 2026-09-18",
           18, DIM)
    d.disc(56 + 8, 262, 16, ACC3)
    d.text(76, 252, "含现场录音与一段未剪辑的争论", 16, SUB)

    # ---------------------------------------------------------------- waveform
    CX, CY, CW, CH = 48, 296, 1304, 372
    d.card(CX, CY, CW, CH, PANEL, radius=14, border="1 SOLID " + LINE)
    N = 216
    bx0, bx1 = CX + 24, CX + CW - 24
    mid = CY + 168
    maxh = 116
    for i in range(N):
        t = i / float(N) * DURATION
        amp = envelope(t, i)
        h = 6 + amp * maxh
        col = ACC2
        for _, start, _, c in CHAPTERS:
            if t >= start:
                col = c
        x = bx0 + i * ((bx1 - bx0) / float(N))
        wbar = (bx1 - bx0) / float(N) - 1.4
        d.box(x, mid - h, wbar, h * 2, col, radius=wbar / 2.0)
    # chapter dividers + labels above the wave
    for at, start, title, col in CHAPTERS:
        x = bx0 + (start / float(DURATION)) * (bx1 - bx0)
        d.dashed(x, CY + 22, x, mid + 150, "#FFFFFF38", 1.2, 6, 5)
        d.box(x, CY + 14, 3, 12, col)
        if start < DURATION * 0.62:
            d.ctext(x - 90, CY + 34, at, 13, col, family=MONO, w=90, h=18,
                    align="CENTER_RIGHT")
    # baseline + playhead (label sits under the wave so it cannot cover a chapter tag)
    d.box(bx0, mid, bx1 - bx0, 1, "#33404EFF")
    ph = bx0 + 0.62 * (bx1 - bx0)
    d.box(ph, CY + 12, 2, CH - 46, ACC)
    d.box(ph - 62, CY + CH - 62, 124, 26, ACC, radius=6)
    d.ctext(ph - 62, CY + CH - 62, "62% · 36:04", 14, "#101418FF", "BOLD", family=MONO,
            w=124, h=26, align="CENTER")
    d.ctext(bx0, CY + CH - 26, "0:00", 13, SUB, family=MONO, w=60, h=18)
    d.ctext(bx1 - 60, CY + CH - 26, "%d:%02d" % (DURATION // 60, DURATION % 60), 13,
            SUB, family=MONO, w=60, h=18, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- chapters
    d.card(48, 692, 1304, 268, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(72, 706, "章节", 18, TXT, "BOLD")
    d.ctext(900, 708, "共 %d 章 · 最长一章 %.1f 分钟" % (len(CHAPTERS),
                                                     data["longest_chapter_min"]),
            15, DIM, w=428, h=22, align="CENTER_RIGHT")
    for i, (at, start, title, col) in enumerate(CHAPTERS):
        c, r = i % 2, i // 2
        x = 72 + c * 648
        y = 740 + r * 52
        d.box(x, y, 5, 34, col, radius=2)
        d.ctext(x + 16, y, at, 17, col, "BOLD", family=MONO, w=64, h=24)
        d.ctext(x + 88, y - 1, clip(title, 16, 540), 16, TXT, w=540, h=26)
        if i < len(CHAPTERS) - 1:
            nxt = CHAPTERS[i + 1][1]
            d.ctext(x + 88, y + 21, "时长 %d:%02d" % ((nxt - start) // 60, (nxt - start) % 60),
                    12, SUB, family=MONO, w=200, h=16)

    # ---------------------------------------------------------------- quotes
    d.card(48, 984, 640, 360, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(72, 998, "本集金句", 18, TXT, "BOLD")
    for i, (at, q, who) in enumerate(QUOTES):
        y = 1034 + i * 100
        d.text(72, y, at, 15, ACC, family=MONO)
        d.ctext(72, y + 22, clip(q, 19, 592), 19, TXT, w=592, h=28)
        d.ctext(72, y + 54, clip(who, 14, 592), 14, SUB, w=592, h=20)

    d.card(712, 984, 640, 360, PANEL, radius=14, border="1 SOLID " + LINE)
    d.text(736, 998, "收听与制作", 18, TXT, "BOLD")
    rows = [("制作", "林一 / 周砚"), ("声音设计", "苏澜"), ("现场录音", "河口观测站（授权使用）"),
            ("音乐", "「退潮」— 白鹭乐队（虚构）"), ("时长", data["duration_text"]),
            ("订阅", "搜索「潮位线」· 每周四更新")]
    for i, (k, v) in enumerate(rows):
        y = 1032 + i * 34
        d.text(736, y, k, 14, ACC2)
        d.ctext(836, y - 1, clip(v, 15, 496), 15, TXT, w=496, h=22)
    d.box(736, 1240, 592, 1, LINE)
    d.ctext(736, 1250, "本图为 Snapshot DSL 演示作品：节目、嘉宾与引语均为虚构，波形由脚本按章节包络生成。",
            13, SUB, w=592, h=36)
    d.ctext(736, 1300, "章节边界、时长与波形停顿一一对应，可直接核对。", 13, SUB,
            w=592, h=20)

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
