# -*- coding: utf-8 -*-
"""B06 case-01 · 服药钟面 — 一天四次用药的 24 小时时间轴

Problem: 医嘱的「每日三次，饭后服用」是纯文字，老人要在脑中换算成具体时刻，
还要记住哪两种不能同服。
Redesign: 一天 = 一个 24 小时环面，用药按真实角度落在环上，已服/待服一眼可分。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import (arc, box, circle, emit, polar, seg, text, tw_slot)

W, H = 780, 1688
BG = "#071A2B"
L = 46                     # left margin
RGT = W - L                # right edge = 734
CW = RGT - L               # content width = 688

# ---------------- demo data (self-authored; NOT medical advice) -------------
NOW_H, NOW_LABEL = 7.75, "07:45"
DAY = "10月21日 周三"

MEDS = [
    {"n": 1, "name": "氨氯地平片", "cls": "降压", "dose": "5mg × 1 片",
     "t": 7.5, "when": "07:30", "note": "早餐后服用", "color": "#2FBF71"},
    {"n": 2, "name": "二甲双胍缓释片", "cls": "降糖", "dose": "0.5g × 1 片",
     "t": 8.0, "when": "08:00", "note": "随餐服用", "color": "#2E86DE"},
    {"n": 3, "name": "华法林钠片", "cls": "抗凝", "dose": "2.5mg × 1 片",
     "t": 18.0, "when": "18:00", "note": "时刻固定，勿随意调整",
     "color": "#E4572E"},
    {"n": 4, "name": "阿托伐他汀钙片", "cls": "调脂", "dose": "20mg × 1 片",
     "t": 21.5, "when": "21:30", "note": "睡前服用", "color": "#F2A93B"},
]
for m in MEDS:
    m["taken"] = m["t"] <= NOW_H
nexts = [m for m in MEDS if not m["taken"]]
nxt = min(nexts, key=lambda m: m["t"])
gap = nxt["t"] - NOW_H
gap_h, gap_m = int(gap), int(round((gap - int(gap)) * 60))

# ---------------- assertions ----------------
assert len(MEDS) == 4
assert sum(1 for m in MEDS if m["taken"]) == 1
assert nxt["n"] == 2 and abs(gap - 0.25) < 1e-9
assert MEDS == sorted(MEDS, key=lambda m: m["t"]), "列表须按时刻排序"
assert MEDS[3]["t"] - MEDS[2]["t"] >= 2.0, "演示规则要求两药间隔 ≥2 小时"

CX, CY, R = 390.0, 452.0, 196.0

# ---------------- C2 ring geometry ----------------
B = [box(0, 0, W, H, BG)]
B.append(arc(CX, CY, R, 0, 360, 22, "#173549"))
B.append(arc(CX, CY, R, 0, NOW_H / 24.0 * 360.0, 22, "#2A6E8F"))

for h in range(24):
    a = h / 24.0 * 360.0
    major = (h % 6 == 0)
    x1, y1 = polar(CX, CY, R - 22 - (34 if major else 16), a)
    x2, y2 = polar(CX, CY, R - 22, a)
    B.append(seg(x1, y1, x2, y2, 5 if major else 3,
                 "#5C7C99" if major else "#2C4A63"))

# hour labels OUTSIDE the ring -> cannot collide with the centre readout
LAB_R = R + 62
for h in (0, 6, 12, 18):
    lx, ly = polar(CX, CY, LAB_R, h / 24.0 * 360.0)
    B.append(text(lx - 30, ly - 18, 60, 36, "%02d" % h, 25, "#7FA3BE",
                  align="CENTER", font="Inter"))

# med dots at their true angle
for m in MEDS:
    dx, dy = polar(CX, CY, R, m["t"] / 24.0 * 360.0)
    B.append(circle(dx, dy, 25, m["color"]))
    B.append(text(dx - 25, dy - 17, 50, 34, str(m["n"]), 25, "#06131F",
                  bold=True, align="CENTER", font="Inter"))
    if m["taken"]:
        B.append(circle(dx + 19, dy + 19, 13, "#FFFFFF"))
        B.append(text(dx + 11, dy + 7, 17, 24, "✓", 15, "#0B2135",
                      bold=True, align="CENTER"))

# next-dose needle
na = nxt["t"] / 24.0 * 360.0
nx, ny = polar(CX, CY, R - 30, na)
B.append(seg(CX, CY, nx, ny, 4, nxt["color"], radius=2))
B.append(circle(CX, CY, 9, nxt["color"]))

# centre readout — width 300 keeps every line inside the ring chord
B.append(text(CX - 150, CY - 112, 300, 32, "下一次服药", 23, "#7FA3BE",
              align="CENTER"))
B.append(text(CX - 150, CY - 78, 300, 84, nxt["when"], 64, "#FFFFFF",
              bold=True, align="CENTER", font="Inter"))
B.append(text(CX - 150, CY + 6, 300, 40, "%d 小时 %d 分钟后" % (gap_h, gap_m),
              27, "#F2A93B", bold=True, align="CENTER"))
B.append(text(CX - 150, CY + 50, 300, 32, "② " + nxt["name"], 22, "#C9DDEE",
              align="CENTER"))

# ---------------- header (drawn after ring so nothing is covered) ----------
B.append(text(L, 40, 240, 40, NOW_LABEL, 27, "#E8F3FB", bold=True,
              font="Inter"))
B.append(box(640, 46, 26, 17, "#E8F3FB", radius=3))
B.append(box(672, 42, 15, 24, "#E8F3FB", radius=2))
B.append(box(696, 40, 40, 28, "#E8F3FB", radius=6))
B.append(box(737, 47, 4, 14, "#E8F3FB", radius=2))
B.append(text(L, 96, 500, 54, "今日用药", 42, "#FFFFFF", bold=True))
B.append(text(L, 154, 500, 34, DAY + " · 4 次", 23, "#7FA3BE"))

# ---------------- below the ring ----------------
y = CY + R + 84
B.append(text(L, y, CW, 30, "环面 = 一天 24 小时 · 外圈刻度 = 每 2 小时",
              20, "#5C7C99", align="CENTER"))
y += 44
B.append(circle(L + 12, y + 14, 12, "#FFFFFF"))
B.append(text(L + 4, y + 2, 17, 24, "✓", 15, "#0B2135", bold=True,
              align="CENTER"))
B.append(text(L + 34, y, 160, 30, "已完成", 21, "#7FA3BE"))
B.append(circle(L + 172, y + 14, 12, "#33566F"))
B.append(text(L + 194, y, 160, 30, "待服用", 21, "#7FA3BE"))
y += 52

# ---------------- med list ----------------
B.append(text(L, y, 400, 40, "今日 4 次", 30, "#FFFFFF", bold=True))
B.append(text(RGT - 234, y + 4, 234, 32, "按时刻排序", 21, "#5C7C99",
              align="RIGHT"))
y += 50

ROW_H, ROW_GAP = 96, 12
for m in MEDS:
    B.append(box(L, y, CW, ROW_H, "#0E2739", radius=16, border="#1D3F55",
                 border_w=2))
    B.append(box(L, y, 6, ROW_H, m["color"], radius=3))
    B.append(circle(L + 48, y + 34, 19, m["color"]))
    B.append(text(L + 29, y + 20, 38, 30, str(m["n"]), 22, "#06131F",
                  bold=True, align="CENTER", font="Inter"))
    B.append(text(L + 80, y + 12, 150, 40, m["when"], 28, "#FFFFFF",
                  bold=True, font="Inter"))
    B.append(text(L + 80, y + 50, 260, 32, m["name"], 22, "#C9DDEE"))
    B.append(text(L + 80, y + 76, 260, 26, m["note"], 18, "#5C7C99"))
    B.append(text(RGT - 290, y + 12, 274, 32, m["cls"], 20, m["color"],
                  align="RIGHT"))
    B.append(text(RGT - 290, y + 46, 274, 32, m["dose"], 21, "#9FBBD0",
                  align="RIGHT", font="Inter"))
    y += ROW_H + ROW_GAP

# ---------------- C3 interaction warning ----------------
IY = y + 8
IH = 176
B.append(box(L, IY, CW, IH, "#2A1B12", radius=18, border="#E4572E",
             border_w=2))
B.append(box(L, IY, 6, IH, "#E4572E", radius=3))
B.append(circle(L + 46, IY + 42, 17, "#E4572E"))
B.append(text(L + 29, IY + 28, 34, 30, "!", 24, "#12060A", bold=True,
              align="CENTER", font="Inter"))
B.append(text(L + 76, IY + 24, 500, 36, "相互作用提醒", 27, "#FF9E7A",
              bold=True))
B.append(text(L + 26, IY + 72, 636, 76,
              "③ 华法林钠片 与 ④ 阿托伐他汀钙片 同用时，\n"
              "可能增加出血风险。", 24, "#FFE3D6", line_h=1.4))
B.append(box(L + 26, IY + 148, 636, 30, "#3A241A", radius=10))
B.append(text(L + 40, IY + 152, 608, 26,
              "处理：两者间隔 ≥ 2 小时，并按医嘱复查凝血指标。", 20,
              "#FFC9B4", bold=True))

# ---------------- C4 missed-dose ----------------
MY = IY + IH + 16
MH = 84
B.append(box(L, MY, CW, MH, "#0E2739", radius=16, border="#2C4A63",
             border_w=2))
B.append(text(L + 24, MY + 10, 640, 30, "漏服怎么办", 23, "#FFFFFF",
              bold=True))
B.append(text(L + 24, MY + 44, 640, 30,
              "距下次服药 ≥ 4 小时可补服一次；不足 4 小时跳过，勿服双份。",
              19, "#9FBBD0"))

# ---------------- footer ----------------
FY = MY + MH + 12
B.append(text(L, FY, CW, 46,
              "演示数据 · 药名、剂量、时刻与相互作用均为自拟示例，不构成用药建议；\n"
              "实际用法以医师处方与药品说明书为准。", 17, "#4E6E88",
              line_h=1.4))

# ---------------- layout guard ----------------
end = FY + 46
assert end <= H, "内容超出画布: %d > %d" % (end, H)
print("layout ends at %d / %d  (%d px spare)" % (end, H, H - end))

VER = sys.argv[1] if len(sys.argv) > 1 else "v2"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-01-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-01 %s: now=%s next=%s gap=%dh%dm" % (VER, NOW_LABEL,
                                                 nxt["when"], gap_h, gap_m))
