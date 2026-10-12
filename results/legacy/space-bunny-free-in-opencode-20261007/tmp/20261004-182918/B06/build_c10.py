# -*- coding: utf-8 -*-
"""case-10 · 同一颗药，三种剂型，三个不同的时点

媒介：横版 1400 × 1080，贴在药盒旁 / 手机横屏。
三种剂型的服用时点、达峰时间与血糖阈值取自真实官方科普；
血糖曲线为定性示意，不是任何人的实测或预测值，本页不构成用药建议。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

IND = "#4F46E5"            # 肠溶片
ORD = "#B45309"            # 普通片
ERX = "#0D9488"            # 缓释片

# ------------------------------------------------------ 真实：血糖阈值与参考值
GL_LO, GL_HI = 3.9, 6.1        # 健康人空腹血糖参考范围（天津卫健委科普）
DIAG = 7.0                     # 空腹 ≥7.0 或任一次 ≥11.1 应考虑糖尿病诊断
CRIT_HI, CRIT_LO = 22.2, 2.2   # 危急值

# --------- 示意曲线（定性形状，不是我实测或预测的数值；峰值取常见餐后量级）
DAY = [(0.0, 5.9), (3.0, 5.4), (5.0, 5.0), (6.5, 5.1), (8.0, 6.3), (9.5, 9.4),
       (11.0, 7.9), (12.5, 6.9), (13.8, 9.1), (15.5, 7.1), (16.8, 6.3),
       (18.5, 7.0), (20.0, 9.2), (21.8, 7.5), (24.0, 6.1)]
MEALS = [(8.0, "早餐"), (12.5, "午餐"), (18.5, "晚餐")]

# --------------------------------------- 真实：三种剂型的服用时点（官方科普）
LANES = [
    (ERX, "缓释片", "每天 1 次", [18.5], "晚餐时或餐后立即",
     "药物缓缓释放，血药浓度达峰平均 7 小时",
     "晚餐时吃，白天的血药浓度正好覆盖两餐后的高血糖。"),
    (ORD, "普通片", "每天 3 次", [8.0, 12.5, 18.5], "餐中或餐后立即",
     "在胃内崩解释放，对胃肠道刺激相对较大",
     "说明书推荐随餐或餐后即刻；空腹吃更容易恶心腹胀。"),
    (IND, "肠溶片", "每天 3 次", [7.5, 12.0, 18.0], "餐前 15–30 分钟",
     "在胃内不崩解，到肠道才释放",
     "餐前半小时吃，血药浓度高峰与餐后血糖高峰趋于一致。"),
]

W, H = 1400, 1080
MG = 48
CW = W - 2 * MG
D = R.fresh()
kids = []


def hhmm(v):
    h = int(v)
    m = int(round((v - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return "%d:%02d" % (h, m)


# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 150, color=K.INK), K.box(0, 0, 8, 150, color=IND)]
kids.append(K.one_line(MG, 20, "同一颗药，三种剂型，三个不同的时点", size=42,
                       color="#FFFFFF", font=K.BLACK))
kids.append(K.one_line(MG, 78, "说明书里那行「餐前 / 餐中 / 餐后」的小字，解释了原因，却没人把它翻译成"
                       "「今天几点吃」", size=18, color=K.A(IND, 0.9)))
kids.append(K.one_line(MG, 110, "把这张小卡贴在药盒旁：三条泳道 + 一日血糖曲线，看一眼就知道该在哪个点吃",
                       size=18, color=K.A("#FFFFFF", 0.55)))
kids += K.chip(1160, 26, "case-10 · 用药时点", fill=K.A(IND, 0.26), fg="#C7C9FF",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(W - MG, 78, "10 件作品的第 10 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# =========================================== main: 24h glucose curve + 3 lanes
PX, PY, PW, PH = MG, 176, CW, 520
kids.append(K.box(PX, PY, PW, PH, color="#FFFFFF", radius=18, border=K.bd(K.HAIR),
                  shadow="0 4 18 0 #0F172A0E"))
kids.append(K.one_line(PX + 24, PY + 16, "上面是示意的一日血糖曲线，下面是三条剂型泳道",
                       size=20, color=K.INK, font=K.SEMI))
kids.append(K.one_line(PX + 24, PY + 44, "曲线是定性示意（形状取自「餐后血糖高峰」的定性描述，"
                                        "不是任何人的实测或预测值），只用来对齐时点。",
                       size=12, color=K.MUTE, w=700))
LG = [("参考范围 %s–%s" % (GL_LO, GL_HI), K.mix(ERX, "#0B1220", 0.2), "#E6F5F2FF"),
      ("诊断阈值 %s" % DIAG, K.mix(ORD, "#0B1220", 0.2), "#FDF0DCFF"),
      ("危急值 ≤%s 或 ≥%s（图外）" % (CRIT_LO, CRIT_HI), "#BE123C", "#FCE7ECFF")]
lgx = PX + PW - 24
for t, col, fill in reversed(LG):
    w = K.chip(0, 0, t, size=12, padx=11, h=26)[1]
    lgx -= w
    kids += K.chip(lgx, PY + 16, t, fill=fill, fg=col, size=12, padx=11, h=26)[0]
    lgx -= 10

GX, GY, GW, GH = 214, 288, CW - 214 - 44, 196
VLO, VHI = 3.0, 10.5


def mxh(h):
    return GX + GW * h / 24.0


def myg(v):
    return GY + GH * (VHI - v) / (VHI - VLO)


# 1) the illustrative area first, so the bands and the curve stay readable on top
CURVE = []
for i in range(len(DAY) - 1):
    (h0, v0), (h1, v1) = DAY[i], DAY[i + 1]
    steps = 6
    for k in range(steps):
        t = k / float(steps)
        CURVE.append((mxh(h0 + (h1 - h0) * t), myg(v0 + (v1 - v0) * t)))
CURVE.append((mxh(24.0), myg(DAY[-1][1])))
kids += K.area(CURVE, myg(VLO), K.A(IND, 0.09), step=6)
# 2) reference band + threshold rules
kids.append(K.box(GX, myg(GL_HI), GW, myg(GL_LO) - myg(GL_HI), color=K.A(ERX, 0.13)))
kids.append(K.hline(GX, GX + GW, myg(DIAG), K.A(ORD, 0.8), 1.6))
kids.append(K.one_line(GX + 8, myg(DIAG) - 19, "7.0 糖尿病诊断阈值", size=11,
                       color=K.mix(ORD, "#0B1220", 0.1), w=150))
kids.append(K.one_line(GX + GW - 190, myg(GL_HI) + 4, "参考范围 3.9–6.1", size=11,
                       color=K.mix(ERX, "#0B1220", 0.15), w=190, anchor="RIGHT"))
for v in (0, 3, 6, 9, 12):
    kids.append(K.box(mxh(v), myg(GL_LO), 1.2, 6, color=K.A(K.INK, 0.15)))
# meals and their windows
for h, nm in MEALS:
    kids.append(K.vline(mxh(h), GY + 2, GY + GH, K.A(K.INK, 0.16), 1.2))
    kids.append(K.box(mxh(h) - 34, GY - 26, 68, 22, color=K.INK, radius=6))
    kids.append(K.ctr(mxh(h), GY - 23, "%s %s" % (nm, hhmm(h)), w=68, size=11,
                      color="#FFFFFF", font=K.SEMI))
    kids.append(K.box(mxh(h) - 5, myg(VLO) - 2, 10, 6, color=K.A(K.INK, 0.3), radius=2))
# 3) the curve, its peak, and the axis labels
kids += K.polyline(CURVE, IND, 2.6)
PEAK = min(DAY, key=lambda p: -p[1])
kids.append(K.dot(mxh(PEAK[0]), myg(PEAK[1]), 5.5, K.mix(IND, "#FFFFFF", 0.15),
                  line=IND, lw=2))
kids.append(K.box(mxh(PEAK[0]) + 12, myg(PEAK[1]) - 11, 116, 22,
                  color=K.mix(IND, "#FFFFFF", 0.88), radius=6,
                  border=K.bd(K.A(IND, 0.3))))
kids.append(K.one_line(mxh(PEAK[0]) + 12, myg(PEAK[1]) - 8,
                       "餐后峰 9.4（示意）", size=11, color=K.mix(IND, "#0B1220", 0.15),
                       w=116, align="CENTER"))
for v, lb in ((GL_HI, "6.1"), (GL_LO, "3.9")):
    kids.append(K.one_line(GX - 12, myg(v) - 8, lb, size=11, color=K.MUTE, w=40,
                           anchor="RIGHT"))
kids.append(K.box(GX - 56, GY - 26, 44, 22, color="#F1F5F9FF", radius=6))
kids.append(K.ctr(GX - 34, GY - 23, "mmol/L", w=44, size=10, color=K.MUTE))
# hour ruler
for h in range(0, 25, 3):
    kids.append(K.ctr(mxh(h), GY + GH + 12, "%02d:00" % h, w=56, size=11, color=K.MUTE))

# ---------------------------------------------------------------- three lanes
LY0, LH, LGAP = 516, 52, 8
TX = 272
for li, (col, name, freq, times, when, why, so) in enumerate(LANES):
    y = LY0 + li * (LH + LGAP)
    kids.append(K.box(PX + 24, y, PW - 48, LH, color=K.mix(col, "#FFFFFF", 0.94),
                      radius=12))
    kids.append(K.box(PX + 24, y, 5, LH, color=col,
                      radii={"TopLeft": 12, "BottomLeft": 12}))
    kids.append(K.one_line(PX + 40, y + 9, name, size=16, color=col, font=K.BLACK))
    kids.append(K.one_line(PX + 40, y + 32, freq, size=11, color=K.MUTE))
    kids.append(K.box(TX, y + 6, PX + PW - 24 - TX, LH - 12, color="#FFFFFF", radius=8))
    for t in times:
        px = mxh(t)
        kids.append(K.vrule(px, y, y + LH, K.A(col, 0.35), 1.4))
        kids.append(K.dot(px, y + LH / 2.0, 9, col))
        kids.append(K.dot(px, y + LH / 2.0, 4, "#FFFFFF"))
    if li == 0:
        px = mxh(times[0])
        kids += K.arrow(px + 14, y + LH / 2.0, PX + PW - 34, y + LH / 2.0,
                        K.A(col, 0.75), 1.8, 8)
        kids.append(K.one_line(px + 22, y + 6, "达峰平均 7 小时", size=11,
                               color=K.mix(col, "#0B1220", 0.1)))
        kids.append(K.one_line(PX + PW - 140, y + LH - 20, "→ 次日 01:30 达峰",
                               size=11, color=K.mix(col, "#0B1220", 0.1), w=112,
                               anchor="RIGHT"))
    kids += K.chip(PX + 124, y + 12, when, fill="#FFFFFF", fg=K.mix(col, "#0B1220", 0.2),
                   size=12, padx=12, h=28, line=K.A(col, 0.35))[0]

# ========================================================= bottom: why + what
BY0, BH = 716, 250
CW3 = (CW - 2 * 12) / 3.0
WHY = [(col, name, why, so) for (col, name, freq, times, when, why, so) in LANES]
for i, (col, name, why, so) in enumerate(WHY):
    x = MG + i * (CW3 + 12)
    kids.append(K.box(x, BY0, CW3, BH, color="#FFFFFF", radius=16,
                      border=K.bd(K.HAIR), shadow="0 4 18 0 #0F172A0E"))
    kids.append(K.box(x, BY0, CW3, 6, color=col, radii={"TopLeft": 16, "TopRight": 16}))
    kids.append(K.one_line(x + 20, BY0 + 20, name, size=17, color=col, font=K.BLACK))
    kids.append(K.one_line(x + 20, BY0 + 48, "为什么是这个时间点", size=12,
                           color=K.mix(col, "#0B1220", 0.3), font=K.SEMI))
    kids.append(K.box(x + 20, BY0 + 72, CW3 - 40, 66, color="#F8FAFCFF", radius=10))
    for j, ln in enumerate(K.wraps(why, 14, CW3 - 62)):
        kids.append(K.one_line(x + 30, BY0 + 84 + j * 21, ln, size=14, color=K.INK,
                               font=K.SEMI))
    kids.append(K.one_line(x + 20, BY0 + 156, "所以", size=12, color=K.MUTE))
    for j, ln in enumerate(K.wraps(so, 13, CW3 - 40)[:3]):
        kids.append(K.one_line(x + 20, BY0 + 176 + j * 19, ln, size=13, color=K.INK3))
    kids.append(K.hline(x + 20, x + CW3 - 20, BY0 + BH - 34, K.HAIR, 1.0))
    kids.append(K.one_line(x + 20, BY0 + BH - 24, "来源：药监局 / 卫健委科普（见页脚）",
                           size=11, color=K.MUTE, w=CW3 - 40))

# -------------------------------------------------------------------- footer
FEET = ["服用时点（真实公开科普）：深圳市市场监督管理局（amr.sz.gov.cn/…/post_9023439.html）"
        "——普通剂型餐中或餐后立即服；缓释制剂一天一次；肠溶剂型建议餐前 15–30 分钟服。",
        "桓台县卫健局科普（huantai.gov.cn/…/doc_64afc098026c6831d80b8fc1.html）——普通片在胃内崩解释放、"
        "胃肠刺激较大；肠溶片在胃内不吸收，故餐前半小时服；缓释制剂达峰平均 7 小时，晚餐时服可在白天达峰。",
        "血糖阈值（真实）：天津市卫健委科普（wsjk.tj.gov.cn/…/202501/t20250117_6836861.html）"
        "——空腹血糖参考 3.9–6.1 mmol/L；≥7.0 或任一次 ≥11.1 应考虑糖尿病诊断；≥22.2 或 ≤2.2 为危急值。",
        "本页血糖曲线是定性示意，形状取自「餐后血糖高峰」的定性描述，不是任何人的实测或预测数值；"
        "剂量与服药对象未在图中给出，本页不构成任何用药或医疗建议，就诊请遵医嘱。"]
for i, t in enumerate(FEET):
    kids.append(K.one_line(MG, 984 + i * 18, t, size=12, color=K.MUTE, w=CW - 90))
kids.append(K.one_line(W - MG, 1054, "B06 · case-10", size=13,
                       color=K.A(K.MUTE, 0.6), anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-10", dsl, final=("--final" in sys.argv))
print("peak %s at %s ; lanes %d" % (PEAK[1], hhmm(PEAK[0]), len(LANES)))
print("elements ok")