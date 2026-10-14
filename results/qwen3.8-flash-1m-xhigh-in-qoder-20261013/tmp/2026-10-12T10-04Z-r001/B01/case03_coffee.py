"""B01 case-03 - 叠光烘焙实验室 手冲参数卡 (1080x1350, warm paper).

Scenario: a customer at a specialty roastery deciding how to brew this bag. The flavour
wheel is a real polar construction - 24 sectors in 3 rings, drawn as annular paths - and
the roast's own intensity polygon is computed from the tasting scores, so the wheel and
the bars can never disagree. Brew timing is a scaled timeline, not decoration.

Run:  python tmp/<run_id>/B01/case03_coffee.py
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, f, place, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1080, 1350
BG = "#FBF6EE"
INK, INK2, INK3 = "#2B2118", "#5C4A38", "#8A7660"
ACCENT = "#B4551F"

FAMILIES = [
    ("柑橘", "#E8A33D"), ("核果", "#D4703A"), ("浆果", "#A83246"), ("热带果", "#E0C14A"),
    ("花香", "#C77FA8"), ("茶香", "#7C9964"), ("焦糖", "#8C5A2B"), ("巧克力", "#5A3A22"),
    ("坚果", "#A98963"), ("香料", "#8A4B2A"), ("草本", "#4F7A55"), ("土壤", "#6B5844"),
]
# 24 descriptors, two per family, with the roast's own 0-10 score
NOTES = [
    ("橙皮", 7.5), ("柠檬酸", 6.0), ("白桃", 5.5), ("杏干", 4.0),
    ("红醋栗", 6.5), ("蓝莓", 3.0), ("芒果", 4.5), ("百香果", 2.5),
    ("茉莉", 5.0), ("玫瑰", 3.5), ("乌龙", 4.0), ("绿茶", 2.0),
    ("太妃", 6.0), ("红糖", 5.0), ("牛奶巧克力", 4.5), ("可可", 3.0),
    ("榛果", 5.5), ("杏仁", 3.5), ("丁香", 2.5), ("肉桂", 2.0),
    ("薄荷", 1.5), ("罗勒", 1.0), ("雪松", 2.0), ("湿土", 1.0),
]
POURS = [(0, 0, "注水闷蒸 60 g"), (60, 45, "第一段至 150 g"), (105, 90, "第二段至 220 g"),
         (150, 120, "第三段至 300 g"), (195, 190, "滤干")]
TOTAL_S = 220


def mix(hex_a, hex_b, t):
    """Blend two hex colours: t=0 keeps a, t=1 keeps b."""
    ca = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(c1 + (c2 - c1) * t):02X}"
                         for c1, c2 in zip(ca, cb))


def build():
    s = Sheet(W, H, min_font=20, bg=BG)
    s.text("brand", "叠光烘焙实验室 · SHUANGUANG ROAST LAB", 56, 40, 22, ACCENT,
           bold=True, font=MONO)
    s.text("title", "云谷日晒 2026 批次 · 手冲参数卡", 56, 72, 38, INK, bold=True)
    s.para("sub", "埃塞俄比亚 · 古吉 · 74111 · 日晒 · 1950-2100 m · 烘焙度 浅中"
                  "（品牌与数据为本题自拟示例）", 56, 138, 22, INK3, 968)

    # ---------------- flavour wheel ----------------
    cx, cy = 300, 442
    r0, r1, r2, r3 = 46, 86, 128, 164
    s.rect(cx - r3 - 14, cy - r3 - 14, 2 * (r3 + 14), 2 * (r3 + 14), "#FFFFFF",
           radius=20)
    for i, (fam, col) in enumerate(FAMILIES):
        a0, a1 = i * 30, (i + 1) * 30
        s.donut_segment(cx, cy, r2, r3, a0 + 1, a1 - 1, col)
        s.donut_segment(cx, cy, r1, r2, a0 + 1, a1 - 1, mix(col, "#FBF6EE", 0.30))
        s.donut_segment(cx, cy, r0, r1, a0 + 1, a1 - 1, mix(col, "#FBF6EE", 0.55))
    # intensity polygon from the 24 scores
    pts = []
    for i, (name, score) in enumerate(NOTES):
        ang = math.radians(i * 15 - 90 + 7.5)
        rr = r0 + (r2 - r0) * score / 10.0
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d = "M " + " L ".join(f"{f(x - (cx - r3 - 14))} {f(y - (cy - r3 - 14))}"
                          for x, y in pts) + " Z"
    s.path(cx - r3 - 14, cy - r3 - 14, 2 * (r3 + 14), 2 * (r3 + 14), d, "#2B211833")
    for x, y in pts:
        s.dot(x, y, 3.5, INK)
    s.dot(cx, cy, r0 - 14, "#FBF6EE")
    s.text("wc1", "平均强度", cx, cy - 30, 20, INK3, align="center")
    s.text("wc2", f"{sum(v for _, v in NOTES) / len(NOTES):.1f} / 10", cx, cy - 6, 26,
           INK, bold=True, align="center", font=MONO)
    for i, (fam, col) in enumerate(FAMILIES):
        ang = math.radians(i * 30 + 15 - 90)
        x = cx + (r3 + 24) * math.cos(ang)
        y = cy + (r3 + 24) * math.sin(ang)
        s.text("fl", fam, x, y - 10, 20, INK2, align="center")

    # ---------------- right column: parameters ----------------
    px = 620
    s.rect(px, 320, 404, 300, "#FFFFFF", radius=16)
    s.text("ph", "冲煮参数", px + 24, 340, 26, INK, bold=True)
    rows = [("粉量", "18 g", "研磨度", "6.5"),
            ("水量", "300 g", "粉水比", "1:16.7"),
            ("水温", "92 °C", "器具", "V60-02"),
            ("总时长", "3:40", "闷蒸", "45 s"),
            ("TDS", "1.32 %", "萃取率", "21.4 %")]
    y = 384
    for k1, v1, k2, v2 in rows:
        s.text("k", k1, px + 24, y, 22, INK3)
        s.text("v", v1, px + 104, y - 2, 24, INK, bold=True, font=MONO)
        s.text("k", k2, px + 216, y, 22, INK3)
        s.text("v", v2, px + 300, y - 2, 24, INK, bold=True, font=MONO)
        y += 46

    # ---------------- pour timeline ----------------
    ty = 660
    s.rect(56, ty, 968, 190, "#FFFFFF", radius=16)
    s.text("th", "注水节奏（0 → 3 分 40 秒）", 80, ty + 16, 26, INK, bold=True)
    x0, x1 = 140, 940
    scale = (x1 - x0) / TOTAL_S
    s.rect(x0, ty + 96, x1 - x0, 3, "#E4D8C6")
    for sec in range(0, TOTAL_S + 1, 30):
        s.rect(x0 + sec * scale - 1, ty + 90, 2, 15, "#D8C9B4")
        s.text("tk", f"{sec // 60}:{sec % 60:02d}", x0 + sec * scale, ty + 112, 20,
               INK3, align="center", font=MONO)
    lab = []
    for start, at, label in POURS:
        x = x0 + at * scale
        s.rect(x - 5, ty + 62, 10, 10, ACCENT, shape="CIRCLE")
        s.line(x, ty + 72, x, ty + 96, ACCENT, 2)
        lab.append((label, x - tw(label, 20) / 2, tw(label, 20)))
    for text, x, w in place(lab, min_gap=12):
        s.text("pl", text, x, ty + 52, 20, INK2)
    s.text("pn", "累计注水量 60 → 150 → 220 → 300 g，最后一段保持水面平稳",
           80, ty + 148, 20, INK3)

    # ---------------- tasting bars ----------------
    by = 880
    s.rect(56, by, 968, 300, "#FFFFFF", radius=16)
    s.text("bh", "杯测打分（0-10，与风味轮同一组数据）", 80, by + 20, 26, INK, bold=True)
    top = sorted(NOTES, key=lambda n: -n[1])[:9]
    col_w = 320
    for i, (name, score) in enumerate(top):
        c_, r_ = i % 3, i // 3
        x = 80 + c_ * col_w
        y = by + 66 + r_ * 52
        s.text("nb", name, x, y - 2, 22, INK2)
        bw = 138
        s.rect(x + 118, y + 6, bw, 10, "#EFE4D4", radius=5)
        s.rect(x + 118, y + 6, bw * score / 10.0, 10, ACCENT, radius=5)
        s.text("nv", f"{score:.1f}", x + 118 + bw + 10, y - 2, 22, INK, bold=True,
               font=MONO)
    s.para("bn", "风味轮三环＝12 个家族 × 深浅，24 个 descriptor 的分数连线即本批次轮廓；"
                 "低分项仍保留在轮上，不省略。", 80, by + 236, 20, INK3, 900)

    s.rect(56, 1200, 968, 1, "#E4D8C6")
    s.text("f1", "建议：先按 92 °C / 1:16.7 起步，酸感过锐可降到 90 °C 或调粗半格。",
           56, 1220, 22, INK2)
    s.text("f2", "叠光烘焙实验室 · 示例配方，非任何真实品牌发布", 56, 1256, 20, INK3,
           font=MONO)
    return s


if __name__ == "__main__":
    s = build()
    (TMP / "case03.snapshot").write_text(s.dsl(), encoding="utf-8")
    print(__import__("json").dumps(s.audit(), ensure_ascii=False))
