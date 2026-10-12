# -*- coding: utf-8 -*-
"""B02 case-06 - 修理夜工作台工作单, 1754x1240 (A4 landscape at 1 px ~ 0.13 mm).

Touchpoint: a volunteer's hands are full and greasy; the sheet is clipped to the
workbench under a clip lamp and read at 40 cm, repeatedly, all evening. Task:
follow three steps, tick five safety checks, then declare an outcome that goes
straight into the library's records.

Format decision: A4 landscape because the sheet has three independent columns
(steps / safety / disposition) that must be readable at a glance while the hand is
occupied. The engineering grid is the page ground - the same 量具 idea as the
storefront fascia, at 1/6 the scale.

v03 (after viewing v02): column 3's 本场前 10 件 bar chart ended at y=800, and
section 06's head is drawn at y=800, so the last bar, its value label and the
"06 近 6 个月修好件数" heading occupied the same 22 px band - verified by crop.
Tightened column 3's upper stack instead of pushing section 06 down (moving LY
would have collided the two ruled writing boxes with the 签 line): parts pitch
30 -> 28, disposition pitch 34 -> 32, mix-bar pitch 26 -> 24. Last element now
ends at y=785, leaving an 18 px gap before the heading.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402
import data as DA  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 1754, 1240
M = 56
k = []
k.append(D.box(0, 0, W, H, color="#EFEAE0FF"))

# ------------------------------------------------- engineering grid ground
GRID = 38
gx = M
while gx < W - M:
    k.append(D.box(gx, M, 1, H - 2 * M, color="#E2DBCCB0"))
    gx += GRID
gy = M
while gy < H - M:
    k.append(D.box(M, gy, W - 2 * M, 1, color="#E2DBCCB0"))
    gy += GRID
for mx in range(M, W - M + 1, GRID * 6):
    k.append(D.box(mx, M, 1, H - 2 * M, color="#D6CEBCB8"))
for my in range(M, H - M + 1, GRID * 6):
    k.append(D.box(M, my, W - 2 * M, 1, color="#D6CEBCB8"))
k.append(G.screws(M - 16, M - 16, W - 2 * M + 32, H - 2 * M + 32, "#C9C1AF80",
                  inset=0, r=3))

# ------------------------------------------------- header band
HB = 148
k.append(D.box(M, M, W - 2 * M, HB, color=G.IRON_D))
k.append(D.box(M, M, W - 2 * M, 5, color=G.BRASS))
k.append(D.text_el("百工社", x=M + 32, y=M + 34, w=260, h=56, size=40,
                   color=G.WHITE, font=G.FONT_CJK, style="BOLD", ls=2.4, max_lines=1))
k.append(D.text_el("BAIGONG REPAIR NIGHT · WORK ORDER", x=M + 32, y=M + 94, w=520,
                   h=20, size=12, color=G.BRASS, font=G.FONT, ls=2.2, max_lines=1))
k.append(D.text_el("修理夜 · 工作单", x=M + 640, y=M + 36, w=420, h=44, size=34,
                   color=G.WHITE, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("%s　%s" % (DA.CLINIC_TITLE.replace("修理夜 · ", ""),
                                DA.CLINIC_SHORT), x=M + 640,
                   y=M + 86, w=440, h=24, size=16, color="#A9BDCCFF", font=G.FONT_CJK,
                   max_lines=1))
k.append(G.chip(W - M - 210, M + 44, "台位 03 / 08", fg=G.IRON_D, bg=G.BRASS,
                size=17, padx=20, h=40, radius=5)[0])
k.append(D.text_el("工单号 WO-2512-03", x=W - M - 330, y=M + 92, w=330, h=22,
                   size=15, color="#8FA6B7FF", font=G.FONT_MONO, align="RIGHT",
                   max_lines=1))

# ------------------------------------------------- intake row
IR = M + HB + 22
INTAKE = [("受理物品", "台灯 · 落地灯（忽明忽暗）"), ("工具编号", "T-0412"),
          ("所属义工", "王建国 V-07"), ("受理时间", "19:10")]
colw = (W - 2 * M - 3 * 24) / 4.0
for i, (lab, val) in enumerate(INTAKE):
    x = M + i * (colw + 24)
    k.append(D.text_el(lab, x=x, y=IR, w=colw, h=18, size=12, color=G.MUTE,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(val, x=x, y=IR + 20, w=colw, h=26, size=18, color=G.INK,
                       font=G.FONT_MONO if i == 1 else G.FONT_CJK, style="BOLD",
                       max_lines=1))
k.append(D.hline(M, W - M, IR + 58, G.LINE2, 1))

# ------------------------------------------------- columns
CT = IR + 82
COL1_X, COL1_W = M, 700
COL2_X, COL2_W = M + 740, 420
COL3_X, COL3_W = M + 1200, W - 2 * M - 1200

# --- column 1: three steps
k.append(G.section_head(COL1_X, CT, COL1_W, "01", "按这三步做", size=22))
STEPS = [
    ("断电，拆开后盖", "确认灯罩与镇流器没有烧黑", "断电 2 分钟"),
    ("测镇流器连续性", "万用表 R×1 档，测两根线", "读数"),
    ("换件后通电试", "装回后盖，通电 10 分钟观察", "不发热不闪"),
]
sy = CT + 56
for i, (title, sub, meter) in enumerate(STEPS):
    k.append(D.box(COL1_X, sy, COL1_W, 118, color=G.WHITE, radius=4,
                   border="1 SOLID #DCD4C4FF"))
    k.append(G.stroke_box(COL1_X + 22, sy + 24, 26, 26, G.LINE2, 2, radius=4,
                          fill="#FFFFFF"))
    k.append(D.text_el(str(i + 1), x=COL1_X + 56, y=sy + 22, w=60, h=26, size=13,
                       color=G.RUST, font=G.FONT_MONO, style="BOLD", max_lines=1))
    k.append(D.text_el(title, x=COL1_X + 56, y=sy + 42, w=360, h=28, size=20,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(sub, x=COL1_X + 56, y=sy + 74, w=400, h=22, size=14,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(meter, x=COL1_X + COL1_W - 210, y=sy + 46, w=190, h=24,
                       size=14, color=G.INK2, font=G.FONT_CJK, align="RIGHT",
                       max_lines=1))
    k.append(D.hline(COL1_X + COL1_W - 210, COL1_X + COL1_W - 22, sy + 82,
                     G.LINE2, 1.5))
    sy += 130

# --- column 2: safety checklist
k.append(G.section_head(COL2_X, CT, COL2_W, "02", "安全检查", size=22))
CHECK = [("已断电，插头已拔出", True),
         ("电容已放电 5 分钟", True),
         ("台面清空，无金属件", True),
         ("双手干燥，无戒指", True),
         ("旁人已告知通电时刻", False)]
sy = CT + 56
for lab, on in CHECK:
    k.append(G.stroke_box(COL2_X, sy + 3, 20, 20, G.LINE2, 1.8, radius=3,
                          fill="#FFFFFF"))
    if on:
        k.append(G.seg(COL2_X + 4, sy + 13, COL2_X + 8, sy + 17, G.PINE, 2.2))
        k.append(G.seg(COL2_X + 8, sy + 17, COL2_X + 17, sy + 5, G.PINE, 2.2))
    else:
        k.append(G.seg(COL2_X + 4, sy + 7, COL2_X + 16, sy + 19, G.RUST, 2))
    k.append(D.text_el(lab, x=COL2_X + 32, y=sy + 3, w=COL2_W - 32, h=22, size=15,
                       color=G.INK2, font=G.FONT_CJK, max_lines=1))
    sy += 34
k.append(D.text_el("一项未勾，不得通电。", x=COL2_X, y=sy + 6, w=COL2_W, h=20,
                   size=13, color=G.RUST, font=G.FONT_CJK, style="BOLD", max_lines=1))

# --- column 2 lower: torque / spec mini table
TY = sy + 44
k.append(D.hline(COL2_X, COL2_X + COL2_W, TY, G.LINE, 1))
k.append(D.text_el("常用规格", x=COL2_X, y=TY + 12, w=200, h=22, size=15,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
SPEC = [("E14 螺母", "2.0 N·m"), ("E27 灯座", "2.5 N·m"),
        ("两孔插排", "0.75 mm²"), ("台灯后盖", "4 颗 M3×12")]
ry = TY + 44
for a, b in SPEC:
    k.append(D.text_el(a, x=COL2_X, y=ry, w=220, h=22, size=14, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(b, x=COL2_X + 200, y=ry, w=COL2_W - 200, h=22, size=14,
                       color=G.IRON, font=G.FONT_MONO, align="RIGHT", max_lines=1))
    k.append(D.hline(COL2_X, COL2_X + COL2_W, ry + 26, G.LINE, 1))
    ry += 32

# --- column 3: parts + disposition + tonight's mix chart
k.append(G.section_head(COL3_X, CT, COL3_W, "03", "零件与结论", size=22))
PARTS = [("镇流器 EB-2H", "1", "有"), ("灯座 E27", "1", "有"), ("线卡", "2", "缺")]
ry = CT + 56
k.append(D.text_el("零件", x=COL3_X, y=ry, w=160, h=20, size=12, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("数", x=COL3_X + 250, y=ry, w=40, h=20, size=12, color=G.MUTE,
                   font=G.FONT_CJK, align="RIGHT", max_lines=1))
k.append(D.text_el("库存", x=COL3_X + 300, y=ry, w=70, h=20, size=12, color=G.MUTE,
                   font=G.FONT_CJK, align="RIGHT", max_lines=1))
ry += 26
k.append(D.hline(COL3_X, COL3_X + COL3_W, ry, G.LINE2, 1))
ry += 10
for nm, qty, stock in PARTS:
    k.append(D.text_el(nm, x=COL3_X, y=ry, w=240, h=22, size=15, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(qty, x=COL3_X + 240, y=ry, w=50, h=22, size=15, color=G.INK,
                       font=G.FONT_MONO, align="RIGHT", max_lines=1))
    has = stock == "有"
    k.append(D.text_el(stock, x=COL3_X + 300, y=ry, w=70, h=22, size=15,
                       color=G.PINE if has else G.RUST, font=G.FONT_CJK,
                       style="BOLD", align="RIGHT", max_lines=1))
    ry += 28
k.append(D.hline(COL3_X, COL3_X + COL3_W, ry, G.LINE, 1))

ry += 22
k.append(D.text_el("结论", x=COL3_X, y=ry, w=200, h=22, size=15, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
ry += 34
DISP = [("修好了，交回主人", True), ("待零件，贴标签存库", False),
        ("修不了，登记报废", False)]
for lab, on in DISP:
    k.append(D.box(COL3_X, ry, 22, 22, color=G.WHITE, radius=11,
                   border="2 SOLID %s" % (G.PINE if on else G.LINE2)))
    if on:
        k.append(D.box(COL3_X + 4, ry + 4, 14, 14, color=G.PINE, radius=7))
    k.append(D.text_el(lab, x=COL3_X + 34, y=ry + 1, w=COL3_W - 34, h=22, size=15,
                       color=G.INK2 if on else G.MUTE, font=G.FONT_CJK,
                       style="BOLD" if on else None, max_lines=1))
    ry += 32

# tonight's mix: real bar chart, counts sum to the first 10 jobs of the night
ry += 14
k.append(D.hline(COL3_X, COL3_X + COL3_W, ry, G.LINE, 1))
ry += 14
k.append(D.text_el("本场前 10 件", x=COL3_X, y=ry, w=200, h=20, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("按类型", x=COL3_X + COL3_W - 80, y=ry, w=80, h=20, size=13,
                   color=G.MUTE, font=G.FONT_CJK, align="RIGHT", max_lines=1))
ry += 30
MIX = [("灯具", 4, G.IRON), ("自行车", 3, G.BRASS), ("插排线缆", 2, G.PINE),
       ("衣物织补", 1, G.RUST)]
BAR_X, BAR_W = COL3_X + 76, COL3_W - 116
for nm, v, col in MIX:
    k.append(D.text_el(nm, x=COL3_X, y=ry - 2, w=70, h=20, size=13, color=G.INK2,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.box(BAR_X, ry, BAR_W, 16, color=G.LINE, radius=2))
    k.append(D.box(BAR_X, ry, BAR_W * v / 4.0, 16, color=col, radius=2))
    k.append(D.text_el("%d" % v, x=COL3_X + COL3_W - 34, y=ry - 3, w=34, h=22,
                       size=14, color=G.INK, font=G.FONT_MONO, align="RIGHT",
                       max_lines=1))
    ry += 24

# ------------------------------------------------- lower half: real form fields
LY = 800
k.append(D.hline(M, W - M, LY - 24, G.LINE2, 1))

# --- column 1 lower: symptom + repair narrative, ruled writing areas
k.append(G.section_head(COL1_X, LY, COL1_W, "04", "故障现象与判断", size=22))
for i, (lab, by, bh) in enumerate([("现象记录", 846, 96), ("更换与处理", 980, 90)]):
    k.append(D.text_el(lab, x=COL1_X, y=by, w=200, h=20, size=13, color=G.MUTE,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.box(COL1_X, by + 26, COL1_W, bh, color="#FBF9F4FF", radius=3,
                   border="1 SOLID #D6CEBCFF"))
    for ln in range(2):
        k.append(D.hline(COL1_X + 18, COL1_X + COL1_W - 18, by + 56 + ln * 32,
                         "#E2DBCCB0", 1))

# --- column 2 lower: ask another volunteer
k.append(G.section_head(COL2_X, LY, COL2_W, "05", "需要别的义工", size=22))
hy = LY + 54
for sp in DA.HELP_SPECIALTIES:
    k.append(G.stroke_box(COL2_X, hy + 2, 20, 20, G.LINE2, 1.8, radius=3,
                          fill="#FFFFFF"))
    k.append(D.text_el(sp, x=COL2_X + 32, y=hy + 2, w=COL2_W - 32, h=22, size=15,
                       color=G.INK2, font=G.FONT_CJK, max_lines=1))
    hy += 32
k.append(D.text_el("求助人", x=COL2_X, y=hy + 12, w=60, h=20, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.hline(COL2_X + 62, COL2_X + COL2_W, hy + 36, G.LINE2, 1.5))
k.append(D.text_el("接单人", x=COL2_X, y=hy + 46, w=60, h=20, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.hline(COL2_X + 62, COL2_X + COL2_W, hy + 70, G.LINE2, 1.5))
k.append(D.text_el("本月台账：修好 %d 件 · 待零件 %d 件 · 报废 %d 件"
                   % (DA.LEDGER[-1][1], DA.LEDGER_FAIL[0][1], DA.LEDGER_FAIL[1][1]),
                   x=COL2_X, y=1064, w=COL2_W, h=20, size=13, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))

# --- column 3 lower: 6-month fixed-items sparkline
k.append(G.section_head(COL3_X, LY, COL3_W, "06", "近 6 个月修好件数", size=22))
SP_X, SP_Y, SP_W, SP_H = COL3_X, LY + 62, COL3_W - 30, 108
vals = [v for _m, v in DA.LEDGER]
vmax = max(vals)
k.append(D.hline(SP_X, SP_X + SP_W, SP_Y + SP_H, G.LINE2, 1))
for i, ((mon, v), col) in enumerate(zip(DA.LEDGER,
                                        [G.IRON, G.IRON, G.IRON, G.BRASS, G.BRASS,
                                         G.RUST])):
    bw = (SP_W - 5 * 10) / 6.0
    bx = SP_X + i * (bw + 10)
    bh = SP_H * (v / float(vmax))
    k.append(D.box(bx, SP_Y + SP_H - bh, bw, bh, color=col, radius=2))
    k.append(D.text_el("%d" % v, x=bx - 8, y=SP_Y + SP_H - bh - 22, w=bw + 16,
                       h=20, size=12, color=G.INK2, font=G.FONT_MONO,
                       align="CENTER", max_lines=1))
    k.append(D.text_el(mon, x=bx - 8, y=SP_Y + SP_H + 6, w=bw + 16, h=18, size=11,
                       color=G.MUTE, font=G.FONT_CJK, align="CENTER", max_lines=1))
k.append(D.text_el("峰值 10 月 231 件（入冬前集中换灯管）", x=COL3_X, y=SP_Y + SP_H + 30,
                   w=COL3_W, h=20, size=12, color=G.MUTE, font=G.FONT_CJK,
                   max_lines=1))

# ------------------------------------------------- footer
FY = H - M - 52
k.append(G.footer(M, FY, W - 2 * M, left="百工社 · 修理夜工作单 · 沿河路 12 号",
                  right="工单随工具流转，月底随年报公开"))
k.append(D.text_el("签：____________", x=M + 470, y=FY - 26, w=200, h=22, size=13,
                   color=G.MUTE, font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("主人签：____________", x=M + 700, y=FY - 26, w=240, h=22,
                   size=13, color=G.MUTE, font=G.FONT_CJK, max_lines=1))

dsl = G.snapshot(k, W, H, bg="#EFEAE0FF")
G.show(dsl, "case-06 repair work order 1754x1240")

with open(os.path.join(TMP, "drafts", "case-06.v03.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-06")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
