#!/usr/bin/env python
"""B05 case-05 · 打印 A4 · 退租交接报告（双方签字页）

载体：A4 纵向 1240×1754（150dpi），一张放在桌面上的打印稿，带裁切标记。
受众：退租当天要把"一张纸"交给房东 / 中介 / 租客三方的人（持牌房东陆文君）。
用户意图：把 case-04 桌面上的差分结论压缩成一页可签字、可存档的凭证，
          并让三方在同一份口径上签字。
状态：结束态。差分已生成（2026-09-30 18:04），E-02 仍暂挂，金额 ¥200 待三方确认。
视觉主张：整页只有一种强调色（锚点牌黄）+ 一个责任数字；签字区占整页 1/6，
          因为这份纸的唯一任务是"被签字"，不是"被阅读"。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-05"
W, H = 1240, 1754
kids = []

# ======================================================= paper on a desk ====
kids.append(D.box(0, 0, W, H, color="#DCD6C9FF"))
# faint desk grain so the surface is not a dead field
for i in range(260):
    kids.append(D.box((i * 137) % W, (i * 311) % H, 2, 1, color="#00000010"))
kids.append(D.box(26, 26, W - 52, H - 52, color=K.PAPER,
                  shadow="0 14 54 0 #0E162228"))

# print registration marks
for (cx, cy, sx, sy) in ((26, 26, 1, 1), (W - 26, 26, -1, 1),
                         (26, H - 26, 1, -1), (W - 26, H - 26, -1, -1)):
    kids.append(D.box(cx - 26 if sx > 0 else cx + 10, cy - 0.5, 16, 1, color=K.INK_4))
    kids.append(D.box(cx - 0.5, cy - 26 if sy > 0 else cy + 10, 1, 16, color=K.INK_4))

# sheet text frame
X0, X1 = 96, 1144
IX = X1 - X0

# ============================================================== masthead ====
MY = 92
kids.append(D.box(X0, MY, 46, 46, color=K.YELLOW, radius=8,
                  border="2 SOLID #14181FFF"))
kids.append(D.text_el("房", x=X0, y=MY + 9, w=46, size=24, color="#14181FFF",
                      font=K.DISPLAY, align="CENTER"))
kids.append(D.text_el("房谱 HOMESPEC", x=X0 + 62, y=MY + 1, w=300, size=22,
                      color=K.INK, font=K.DISPLAY, ls=-0.3, wrap=False))
kids.append(D.text_el("住址履历 · 退租交接报告", x=X0 + 62, y=MY + 27, w=300,
                      size=13, color=K.INK_3, font=K.UI, ls=1.4, wrap=False))

kids.append(D.text_el("RQ-2026-0930-1602", x=X1 - 300, y=MY + 1, w=300, size=15,
                      color=K.INK, font=K.MONO, style="BOLD", align="RIGHT",
                      wrap=False))
kids.append(D.text_el("生成 2026-09-30 18:04 · 云栖里运营端签名 · 第 1 页 / 共 2 页",
                      x=X1 - 420, y=MY + 26, w=420, size=11, color=K.INK_3,
                      align="RIGHT", wrap=False))

kids.append(K.hazard_stripe(X0, MY + 74, IX, 9, c1=K.PAPER, pitch=17, thickness=0.46))

# ============================================================ address band ==
AY = MY + 106
kids.append(D.text_el("住址", x=X0, y=AY, w=60, size=10.5, color=K.INK_3,
                      font=K.MONO, ls=1.6, wrap=False))
kids.append(D.text_el("云栖里 3 号楼 1602 室", x=X0, y=AY + 20, w=420, size=26,
                      color=K.INK, font=K.DISPLAY, ls=-0.3, wrap=False))
kids.append(D.text_el("租客 林知远 · 房东 陆文君 · 经办 云栖里运营",
                      x=X0, y=AY + 56, w=460, size=12.5, color=K.INK_2, wrap=False))
kids.append(D.vline(X0 + 468, AY - 4, AY + 76, K.LINE, 1))

kids.append(D.text_el("履历区间", x=X0 + 490, y=AY, w=90, size=10.5, color=K.INK_3,
                      font=K.MONO, ls=1.6, wrap=False))
kids.append(D.text_el("2023-07-01 → 2026-09-30", x=X0 + 490, y=AY + 22, w=320,
                      size=19, color=K.INK, font=K.MONO, ls=-0.3, wrap=False))
kids.append(D.text_el("共 39 个月 · 2 次报修已闭环 · 本轮 12 个锚点",
                      x=X0 + 490, y=AY + 50, w=320, size=12, color=K.INK_2,
                      wrap=False))
kids.append(D.vline(X0 + 820, AY - 4, AY + 76, K.LINE, 1))

kids.append(D.text_el("电表", x=X0 + 842, y=AY, w=90, size=10.5, color=K.INK_3,
                      font=K.MONO, ls=1.6, wrap=False))
kids.append(D.text_el("1284", x=X0 + 842, y=AY + 22, w=64, size=19, color=K.INK_2,
                      font=K.MONO, wrap=False))
kids.append(K.arrow(X0 + 902, AY + 32, X0 + 938, AY + 32, K.INK_4, 1.6, 7))
kids.append(D.text_el("3611", x=X0 + 946, y=AY + 22, w=102, size=19, color=K.INK,
                      font=K.MONO, style="BOLD", align="RIGHT", wrap=False))
kids.append(D.text_el("kWh · 用电 2327 kWh / 39 个月", x=X0 + 842, y=AY + 50,
                      w=302, size=12, color=K.INK_2, wrap=False))

kids.append(K.hline(X0, X1, AY + 104, K.LINE_2, 1))

# ============================================================== headline =====
HY = AY + 140
kids.append(K.anchor_tag(X0, HY + 6, 86, 36, "判定", scale=0.88))
kids.append(D.text_el("责任划分", x=X0 + 100, y=HY + 14, w=200, size=15,
                      color=K.INK_2, font=K.SEMI, wrap=False))
kids.append(D.text_el("¥200", x=X0, y=HY + 46, w=210, size=54,
                      color=K.INK, font=K.DISPLAY, ls=-2.0, wrap=False))
kids.append(D.text_el("应由租客承担", x=X0 + 146, y=HY + 74, w=240, size=15,
                      color=K.INK_2, font=K.MED, wrap=False))

# four stat tiles, ink numbers per the kit rule; the accent bar carries the state
TW, TG = 148, 10
tx_ = X1 - (TW * 4 + TG * 3)
stats = [("可比锚点", "10", "/ 12 个已拍", K.BLUE),
         ("新增损伤", "2", "进入责任判定", K.RED),
         ("已修复", "2", "对应 2 次报修", K.GREEN),
         ("无法比对", "1", "暂挂 · 不判责", K.AMBER)]
for i, (name, big, sub, col) in enumerate(stats):
    x = tx_ + i * (TW + TG)
    kids.append(D.box(x, HY, TW, 96, color="#FFFFFFFF", radius=10,
                      border="1 SOLID " + K.LINE))
    kids.append(D.box(x, HY, 4, 96, color=col,
                      radii={"TopLeft": 10, "BottomLeft": 10}))
    kids.append(D.text_el(name, x=x + 16, y=HY + 14, w=TW - 30, size=11.5,
                          color=K.INK_3, wrap=False))
    kids.append(D.text_el(big, x=x + 16, y=HY + 34, w=70, size=32, color=K.INK,
                          font=K.DISPLAY, ls=-1.0, wrap=False))
    kids.append(D.text_el(sub, x=x + 16, y=HY + 72, w=TW - 30, size=10.5,
                          color=K.INK_3, wrap=False))

kids.append(D.text_el(
    "仅「新增损伤」进入责任判定 · 未变化与已修复均不计费 · 暂挂锚点不判责",
    x=X0, y=HY + 108, w=520, size=11.5, color=K.INK_3, wrap=False))

# ================================================================= table =====
TY = HY + 152
kids.append(D.text_el("逐锚点差分", x=X0, y=TY, w=200, size=17, color=K.INK,
                      font=K.SEMI, wrap=False))
kids.append(D.text_el("Δ = 2026-09-30 拍摄 − 2023-07-01 首拍 · 按判定优先级排序",
                      x=X0 + 150, y=TY + 4, w=520, size=11.5, color=K.INK_3,
                      wrap=False))
kids.append(D.text_el("房谱 HOMESPEC · 演示数据", x=X1 - 320, y=TY + 4, w=320,
                      size=11, color=K.INK_4, font=K.MONO, align="RIGHT",
                      wrap=False))

COLX = [X0, X0 + 86, X0 + 300, X0 + 386, X0 + 740, X0 + 856]
COLW = [80, 208, 80, 348, 110, 170]
HEAD = ["锚点", "位置", "判定", "系统判读", "责任", "金额"]
HY2 = TY + 30
kids.append(D.box(X0, HY2, IX, 34, color=K.PAPER_3, radius=6))
for i, hcap in enumerate(HEAD):
    kids.append(D.text_el(hcap, x=COLX[i] + (10 if i else 12), y=HY2 + 10,
                          w=COLW[i] - 14, size=11, color=K.INK_2,
                          font=K.MONO, style="BOLD", ls=1.2,
                          align="RIGHT" if i == 5 else "LEFT", wrap=False))

ROWS = [
    ("K-01", "厨房 · 水槽下左角", "new",
     "不锈钢水槽支架右后角 3 道划痕，深度 0.12mm", "责任 · 租客", "¥120"),
    ("W-02", "主卧 · 空调出风口下墙", "new",
     "出风口右下 2 个膨胀螺栓钉孔，直径 8mm，无渗水", "责任 · 租客", "¥80"),
    ("B-02", "卫生间 · 台盆下 U 型弯", "fixed",
     "2025-06 更换的 U 型弯与接头无渗水、无挂垢", "R-2506-042 已闭环", "—"),
    ("K-02", "厨房 · 龙头阀根", "fixed",
     "2024-03 更换的陶瓷阀芯与垫片无渗水", "R-2403-118 已闭环", "—"),
    ("A-01", "入户门内侧 · 合页侧", "same",
     "合页螺丝、门框漆面与 2023-07 一致", "无", "—"),
    ("A-02", "入户门锁舌盒", "same", "锁舌行程正常，无撬压痕", "无", "—"),
    ("B-01", "卫生间 · 马桶后墙角", "same",
     "墙砖釉面、硅胶收口无开裂、无霉斑", "无", "—"),
    ("W-01", "主卧 · 飘窗窗台左端", "same", "窗台漆面、密封胶条无变化", "无", "—"),
    ("E-01", "阳台 · 洗衣机进水口", "same",
     "角阀、手轮、进水软管接口无渗水", "无", "—"),
    ("E-02", "阳台 · 排水地漏盖", "hold",
     "返工拍摄逆光过曝，未识别到 E-02 标记牌", "暂挂 · 10-07 前补拍", "—"),
]
RHY, RH = HY2 + 44, 44
for i, (code, place, cat, detail, duty, money) in enumerate(ROWS):
    name, col, lt, _en = K.CATS[cat]
    yy = RHY + i * RH
    if i % 2 == 0:
        kids.append(D.box(X0, yy - 6, IX, RH - 2, color="#00000005"))
    kids.append(D.box(X0, yy - 6, 4, RH - 2, color=col))
    kids.append(K.anchor_tag(COLX[0] + 12, yy + 2, 62, 26, code, scale=0.6))
    kids.append(D.text_el(place, x=COLX[1], y=yy + 8, w=COLW[1], size=13,
                          color=K.INK, wrap=False))
    kids.append(D.text_el(name, x=COLX[2], y=yy + 10, w=COLW[2], size=12,
                          color=col, font=K.MED, wrap=False))
    kids.append(D.text_el(detail, x=COLX[3], y=yy + 9, w=COLW[3], size=12,
                          color=K.INK_2, wrap=False))
    kids.append(D.text_el(duty, x=COLX[4], y=yy + 10, w=COLW[4], size=11.5,
                          color=col if cat in ("new", "hold") else K.INK_3,
                          wrap=False))
    kids.append(D.text_el(money, x=COLX[5], y=yy + 8, w=COLW[5], size=14,
                          color=K.INK if money != "—" else K.INK_4,
                          font=K.MONO, style="BOLD", align="RIGHT", wrap=False))
    kids.append(K.hline(X0, X1, yy + RH - 8, K.LINE, 1))

TOTAL_Y = RHY + len(ROWS) * RH - 4
kids.append(D.text_el("合计（仅「新增损伤」进入判定）", x=X0, y=TOTAL_Y + 12,
                      w=300, size=12, color=K.INK_3, wrap=False))
kids.append(D.text_el("¥200", x=COLX[5], y=TOTAL_Y + 6, w=COLW[5], size=22,
                      color=K.INK, font=K.DISPLAY, align="RIGHT", wrap=False))

# =========================================================== middle block ====
MB_Y = TOTAL_Y + 62
MB_H = 236
# --- left: the two repairs this flat's history already contains
kids.append(D.box(X0, MB_Y, 512, MB_H, color="#FFFFFF", radius=10,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("本房履历中的报修", x=X0 + 22, y=MB_Y + 20, w=300,
                      size=13.5, color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("均已闭环，对应上表「已修复」", x=X0 + 300, y=MB_Y + 22,
                      w=200, size=11, color=K.INK_3, align="RIGHT", wrap=False))
for i, (rid, date, what, fix, who, cost, state) in enumerate(K.REP_AIR):
    ry = MB_Y + 58 + i * 84
    kids.append(K.hline(X0 + 22, X0 + 490, ry - 10, K.LINE, 1))
    kids.append(D.box(X0 + 22, ry, 4, 56, color=K.GREEN))
    kids.append(D.text_el(rid, x=X0 + 38, y=ry, w=120, size=13, color=K.INK,
                          font=K.MONO, style="BOLD", wrap=False))
    kids.append(D.text_el(date, x=X0 + 160, y=ry + 1, w=100, size=12,
                          color=K.INK_3, font=K.MONO, wrap=False))
    kids.append(D.text_el(what, x=X0 + 38, y=ry + 22, w=300, size=12.5,
                          color=K.INK_2, wrap=False))
    kids.append(D.text_el(fix + " · " + who, x=X0 + 38, y=ry + 42, w=300,
                          size=11.5, color=K.INK_3, wrap=False))
    kids.append(D.text_el("¥%d" % cost, x=X0 + 400, y=ry + 8, w=90, size=16,
                          color=K.INK, font=K.MONO, align="RIGHT", wrap=False))
    kids.append(D.text_el(state, x=X0 + 400, y=ry + 32, w=90, size=11,
                          color=K.GREEN, align="RIGHT", wrap=False))

# --- right: the held anchor, called out in amber because it is the open item
kids.append(D.box(X0 + 524, MB_Y, IX - 524, MB_H, color=K.AMBER_LT, radius=10,
                  border="1 SOLID " + K.A(K.AMBER, "4D")))
kids.append(D.text_el("未决项 · E-02", x=X0 + 546, y=MB_Y + 20, w=260, size=13.5,
                      color=K.AMBER, font=K.SEMI, wrap=False))
kids.append(K.anchor_tag(X0 + IX - 100, MB_Y + 16, 76, 30, "E-02", scale=0.72))
kids.append(D.text_el(
    "E-02 阳台排水地漏盖在返工拍摄中 4 张全部未通过识别，判定「暂挂」。",
    x=X0 + 546, y=MB_Y + 52, w=430, size=12.5, color=K.INK_2, wrap=False))
kids.append(D.text_el(
    "· 暂挂锚点不进入金额计算，也不判定任何一方责任。",
    x=X0 + 546, y=MB_Y + 78, w=430, size=12, color=K.INK_2, wrap=False))
kids.append(D.text_el(
    "· 10-07 24:00 前补拍通过，差分自动重算并追加本页第 2 页。",
    x=X0 + 546, y=MB_Y + 100, w=430, size=12, color=K.INK_2, wrap=False))
kids.append(D.text_el("重拍期限", x=X0 + 546, y=MB_Y + 136, w=90, size=11,
                      color=K.INK_3, wrap=False))
kids.append(D.text_el("2026-10-07", x=X0 + 546, y=MB_Y + 154, w=200, size=24,
                      color=K.INK, font=K.MONO, style="BOLD", ls=-0.5, wrap=False))
kids.append(D.text_el("逾期未补拍 → E-02 从结算表整体移除，本页金额不变。",
                      x=X0 + 546, y=MB_Y + 190, w=430, size=11.5, color=K.AMBER,
                      wrap=False))

# ============================================================ signatures ====
SG_Y = MB_Y + MB_H + 46
kids.append(D.text_el("三方确认", x=X0, y=SG_Y, w=200, size=17, color=K.INK,
                      font=K.SEMI, wrap=False))
kids.append(D.text_el("签字即确认上表判定与合计金额；异议请在签字前于第 2 页记录。",
                      x=X0 + 150, y=SG_Y + 4, w=640, size=11.5, color=K.INK_3,
                      wrap=False))

SGW = (IX - 2 * 24) / 3.0
signers = [("租客", "林知远", "身份证 3301**********0417", "2026-10-01"),
           ("房东", "陆文君", "持牌备案 杭租字 0113-4471", "2026-10-01"),
           ("经办", "云栖里运营 · 周敏", "运营工号 OPS-2071", "2026-10-01")]
for i, (role, name, meta, date) in enumerate(signers):
    x = X0 + i * (SGW + 24)
    kids.append(D.box(x, SG_Y + 30, SGW, 168, color="#FFFFFF", radius=10,
                      border="1 SOLID " + K.LINE))
    kids.append(D.box(x, SG_Y + 30, SGW, 34, color=K.PAPER_3,
                      radii={"TopLeft": 10, "TopRight": 10}))
    kids.append(D.text_el(role, x=x + 16, y=SG_Y + 41, w=80, size=12.5,
                          color=K.INK, font=K.SEMI, wrap=False))
    kids.append(D.text_el("确认人", x=x + SGW - 96, y=SG_Y + 42, w=80, size=10.5,
                          color=K.INK_3, align="RIGHT", wrap=False))
    # signature rule + printed name as the placeholder signature
    kids.append(D.dashed(x + 16, x + SGW - 16, SG_Y + 130, K.INK_4, 1, 8, 6))
    kids.append(D.text_el(name, x=x + 16, y=SG_Y + 94, w=SGW - 32, size=22,
                          color=K.INK, font=K.SERIF, wrap=False))
    kids.append(D.text_el(meta, x=x + 16, y=SG_Y + 136, w=SGW - 32, size=10.5,
                          color=K.INK_3, wrap=False))
    kids.append(D.text_el("签署日期", x=x + 16, y=SG_Y + 160, w=70, size=10,
                          color=K.INK_4, wrap=False))
    kids.append(D.text_el(date, x=x + SGW - 176, y=SG_Y + 158, w=160, size=12,
                          color=K.INK_2, font=K.MONO, align="RIGHT", wrap=False))

# =============================================================== footer ======
FY = SG_Y + 226
kids.append(K.hline(X0, X1, FY, K.LINE_2, 1))
kids.append(D.text_el(
    "判定规则：Δ > 0 判「新增损伤」并进入责任判定；Δ ≤ 0 且损伤消失判「已修复」；"
    "标记牌未识别或光线不合格判「暂挂」，暂挂不进入金额计算。",
    x=X0, y=FY + 20, w=760, size=11, color=K.INK_3, wrap=False))
kids.append(D.text_el(
    "本页为房谱 HOMESPEC 演示稿：品牌、住址、人物、单号、金额与读数均为自拟示例数据，"
    "不是任何实际部署系统的输出。",
    x=X0, y=FY + 44, w=760, size=11, color=K.INK_4, wrap=False))
# v02: the QR block is 72px at FY+16 and its two caption lines sat at FY+100 /
# FY+118, so the second line fell past the sheet edge and was cut (measured on
# the case-05 render). The block is now 62px at FY+14 with both captions inside
# the 1754px sheet: +82 and +96 leave 34px of clear margin below.
kids.append(K.qr_dummy(X1 - 76, FY + 14, 62, seed=1602, modules=21))
kids.append(D.text_el("扫码查看可核对的两张原图", x=X1 - 300, y=FY + 82, w=210,
                      size=10, color=K.INK_4, align="RIGHT", wrap=False))
kids.append(D.text_el("图块为示意，非可扫描二维码", x=X1 - 300, y=FY + 96,
                      w=210, size=9, color=K.INK_4, align="RIGHT", wrap=False))

r = bk.emit(CASE, kids, W, H)