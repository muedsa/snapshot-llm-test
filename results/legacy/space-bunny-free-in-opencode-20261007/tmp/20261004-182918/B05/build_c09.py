#!/usr/bin/env python
"""B05 case-09 · 打印 A5 横向 1050×760 · 冰箱上的维修速查卡

载体：A5 横向卡片 1050×760（148×105mm），左侧四个装订孔，贴在冰箱门上。
      这不是 App 界面，也不是网页——它是一张会被磁铁压住、半年后还有人看的
      纸。版式因此是"卡片"逻辑：巨大的可读字号、极少颜色、一张表对齐。
受众：任何一个住在这套房里的人（不假设会用 App）。半年后水管又漏了，
      他只想知道"找谁、上次换了什么、报修时该说什么"。
用户意图：3 秒找到"该找谁"，30 秒知道"上次这个位置换了什么件"，
      并在打电话时把这三句话说清楚。
状态：2026-10-01 打印更新。卡上同时写明"E-02 还没确认过"这件没做完的事。
视觉主张：整张卡只有一个强调色（锚点牌黄）+ 三个真实联系方式，其余全是
      "上次换了什么"——因为半年后最重要的是知道这个位置已经被修过；
      左上角的黄黑标记牌图案让它和现场那些牌属于同一套东西。

v02 修正（v01 实际看图后）：
  * 表格第 7 列「备注」宽度算错，整列溢出卡片右缘并被裁掉 → 取消「维修方」
    列（老周 已在右上角联系方式里），7 列改 6 列，逐列宽度按 est_width 重排；
  * 第三行「如果渗水，新开单」同样溢出 → 并入新的备注列，宽度按实测文本量给；
  * 表格底与页脚之间有 ~180px 空洞 → 填入两块真实内容：自己先看三样 /
    打电话说四句，这正是这张卡被贴在冰箱上的原因；
  * 二维码及其说明落在卡片下缘之外 → 上移页脚，页脚带 72px 二维码。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-09"
W, H = 1050, 760
kids = []

# ======================================================== fridge surface ====
kids.append(K.gradient_v(0, 0, W, H, "#C6CCD0", "#E6EAEC", steps=28))
# brushed-steel streaks on top of the gradient, low contrast, deterministic
for i in range(170):
    y = (i * 37) % H
    x = (i * 173) % W
    w_ = 120 + (i * 53) % 460
    kids.append(D.box(x, y, w_, 1,
                      color=K.A("#FFFFFF", "1F" if i % 3 == 0 else "10")))
# a soft overhead reflection so the steel is not a flat field
kids.append(D.box(120, -80, 460, 300, color=None, extra={
    "gradientType": "RADIAL", "gradientColors": "#FFFFFF42,#FFFFFF00",
    "gradientCenter": "(0.5,0.5)", "gradientRadius": "0.7"}))
kids.append(D.box(-100, 480, 420, 260, color=None, extra={
    "gradientType": "RADIAL", "gradientColors": "#8A949C33,#8A949C00",
    "gradientCenter": "(0.5,0.5)", "gradientRadius": "0.7"}))

# ============================================================== the card ====
CX, CY, CW_, CH_ = 60, 54, W - 120, H - 108
kids.append(D.box(CX + 6, CY + 10, CW_, CH_, color="#00000026", radius=14))
kids.append(D.box(CX, CY, CW_, CH_, color="#FFFFFF", radius=14,
                  shadow="0 12 40 0 #3A444D2E"))
kids.append(D.box(CX, CY, CW_, CH_, color=None, radius=14,
                  border="1 SOLID #C8CED4"))

# four punched holes down the left edge, as a real card would have
for i in range(4):
    kids.append(K.circle(CX + 28, CY + 148 + i * 148, 9, "#C4CAD0"))
    kids.append(K.circle(CX + 28, CY + 148 + i * 148, 6.5, "#D8DCDF"))

PAD = 46
IX0 = CX + PAD
IX1 = CX + CW_ - PAD
IWD = IX1 - IX0

# ============================================================== header ======
kids.append(D.box(IX0, CY + 28, 46, 46, color=K.YELLOW, radius=8,
                  border="2 SOLID #14181FFF"))
kids.append(D.text_el("房", x=IX0, y=CY + 36, w=46, size=24, color="#14181FFF",
                      font=K.DISPLAY, align="CENTER", wrap=False))
kids.append(D.text_el("这套房 · 维修速查卡", x=IX0 + 62, y=CY + 30, w=400,
                      size=26, color=K.INK, font=K.DISPLAY, ls=-0.6,
                      wrap=False))
kids.append(D.text_el("云栖里 3 号楼 1602 室 · 房谱 HOMESPEC · 打印于 2026-10-01",
                      x=IX0 + 62, y=CY + 62, w=520, size=12.5, color=K.INK_3,
                      wrap=False))
HD_X = IX1 - 306
kids.append(D.box(HD_X, CY + 26, 306, 54, color=K.PAPER_3, radius=10))
kids.append(D.text_el("紧急", x=HD_X + 16, y=CY + 36, w=44, size=11,
                      color=K.RED, font=K.MONO, ls=1.4, wrap=False))
kids.append(D.text_el("水管 / 地漏 → 老周 138****6621", x=HD_X + 58, y=CY + 32,
                      w=232, size=12.5, color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("其他问题 → 房东 陆文君 139****3308", x=HD_X + 58,
                      y=CY + 52, w=232, size=12.5, color=K.INK_2, wrap=False))

kids.append(K.hazard_stripe(IX0, CY + 96, IWD, 10, c1="#FFFFFF", pitch=18,
                            thickness=0.46))

# ====================================================== the repaired spots ===
TY = CY + 122
kids.append(D.text_el("这三个位置修过，最容易再坏", x=IX0, y=TY, w=300,
                      size=15, color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("再坏时先报同样的件，别让它第三次进同一个门。",
                      x=IX0 + 306, y=TY + 3, w=IWD - 306, size=11.5,
                      color=K.INK_3, wrap=False))

# 6 columns. Measured: at 11.5px a 9-char CJK string needs ~104px, so 备注 is
# 190px and the latin-heavy columns keep 108–168px.
COLX = [IX0 + 12, IX0 + 76, IX0 + 272, IX0 + 380, IX0 + 488, IX0 + 656]
COLW = [64, 190, 104, 104, 164, 190]
HEAD = ["锚点", "位置", "报修单号", "上次维修日", "换了什么", "备注"]
ROWS = [
    ("K-02", "厨房 · 龙头阀根", "R-2403-118", "2024-03-09",
     "陶瓷阀芯 + 垫片", "老周 · 质保至 2026-03", K.GREEN),
    ("B-02", "卫生间 · 台盆下 U 型弯", "R-2506-042", "2025-06-21",
     "U 型弯 + 密封圈", "老周 · 质保至 2027-06", K.GREEN),
    ("E-02", "阳台 · 洗衣机进水口", "—", "—",
     "未修过 · 首次记录 2023-07", "未修过 · 渗水请开新单", K.INK_3),
]
HY = TY + 30
kids.append(D.box(IX0, HY, IWD, 28, color=K.PAPER_3, radius=6))
for i, cap in enumerate(HEAD):
    kids.append(D.text_el(cap, x=COLX[i], y=HY + 8, w=COLW[i], size=11,
                          color=K.INK_2, font=K.SEMI, ls=0.6, wrap=False))

# v03: at 60px rows the table ended at y=444 and the two 94px blocks then ran
# into the footer rule at 602. Rows are 54px on a 62px pitch, which frees 16px.
ry = HY + 32
for code, place, rid, date, part, note, col in ROWS:
    rh = 54
    kids.append(D.box(IX0, ry, IWD, rh, color="#FFFFFF", radius=8,
                      border="1 SOLID " + K.LINE))
    kids.append(D.box(IX0, ry, 4, rh, color=col,
                      radii={"TopLeft": 8, "BottomLeft": 8}))
    kids.append(K.anchor_tag(COLX[0], ry + 13, 60, 28, code, scale=0.58))
    kids.append(D.text_el(place, x=COLX[1], y=ry + 17, w=COLW[1], size=12.5,
                          color=K.INK, wrap=False))
    if rid == "—":
        kids.append(D.text_el("无记录", x=COLX[2], y=ry + 18, w=COLW[2],
                              size=11.5, color=K.INK_4, wrap=False))
        kids.append(D.text_el("—", x=COLX[3], y=ry + 18, w=COLW[3], size=12,
                              color=K.INK_4, font=K.MONO, wrap=False))
    else:
        kids.append(D.text_el(rid, x=COLX[2], y=ry + 18, w=COLW[2], size=11.5,
                              color=K.INK, font=K.MONO, wrap=False))
        kids.append(D.text_el(date, x=COLX[3], y=ry + 18, w=COLW[3], size=11.5,
                              color=K.INK_2, font=K.MONO, wrap=False))
    kids.append(D.text_el(part, x=COLX[4], y=ry + 17, w=COLW[4], size=12,
                          color=K.INK if rid != "—" else K.INK_3,
                          font=K.MED if rid != "—" else K.UI, wrap=False))
    kids.append(D.text_el(note, x=COLX[5], y=ry + 18, w=COLW[5], size=11,
                          color=col if col != K.INK_3 else K.INK_3,
                          wrap=False))
    ry += rh + 8

# =============================================== the honest unfinished bit ===
OP_Y = ry + 2
kids.append(D.box(IX0, OP_Y, IWD, 58, color=K.AMBER_LT, radius=8,
                  border="1 SOLID " + K.A(K.AMBER, "4D")))
kids.append(K.anchor_tag(IX0 + 14, OP_Y + 15, 60, 28, "E-02", scale=0.58))
kids.append(D.text_el("E-02 阳台排水地漏盖：这一项还没确认过",
                      x=IX0 + 88, y=OP_Y + 12, w=400, size=13, color=K.AMBER,
                      font=K.SEMI, wrap=False))
# v02: at 560px this line ran under the divider and the right-hand sentence ran
# past the card edge; both columns are re-measured against IX1 = 944.
kids.append(D.text_el("退租时拍了 4 张都没拍到标记牌，判「暂挂」。这一块到底有没有问"
                      "题目前没人能回答——不是没问题，是还不知道。",
                      x=IX0 + 88, y=OP_Y + 32, w=496, size=11, color=K.INK_2,
                      wrap=False))
kids.append(D.vline(IX0 + 600, OP_Y + 10, OP_Y + 48, K.A(K.AMBER, "4D"), 1))
kids.append(D.text_el("如果这里渗水或返味，", x=IX0 + 616, y=OP_Y + 14, w=210,
                      size=11, color=K.AMBER, font=K.SEMI, wrap=False))
kids.append(D.text_el("请直接开新单，不要按「已修过」处理。", x=IX0 + 616,
                      y=OP_Y + 32, w=222, size=11, color=K.INK_2, wrap=False))

# =============================================== why the card exists: how to ==
HY2 = OP_Y + 58 + 16
HW = (IWD - 20) / 2.0
BLOCK_H = 92
# left: three things to check before calling anyone
kids.append(D.box(IX0, HY2, HW, BLOCK_H, color=K.PAPER, radius=8,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("先自己看这三样", x=IX0 + 16, y=HY2 + 10, w=200,
                      size=12.5, color=K.INK, font=K.SEMI, wrap=False))
CHECK = [("1", "标记牌还在不在", "拍了牌，这次维修才会进履历"),
         ("2", "具体是哪个编号", "报 K-02，别只说「厨房」"),
         ("3", "上次换了什么件", "对照上面的表，报同样的件")]
for i, (n, t1, t2) in enumerate(CHECK):
    yy = HY2 + 30 + i * 20
    kids.append(K.circle(IX0 + 26, yy + 8, 8, K.alpha_mix(K.BLUE, .88)))
    kids.append(D.text_el(n, x=IX0 + 18, y=yy + 2, w=16, size=9.5,
                          color="#FFFFFF", font=K.SEMI, align="CENTER",
                          wrap=False))
    kids.append(D.text_el(t1, x=IX0 + 40, y=yy, w=140, size=11.5, color=K.INK,
                          font=K.MED, wrap=False))
    kids.append(D.text_el(t2, x=IX0 + 184, y=yy + 1, w=HW - 200, size=10.5,
                          color=K.INK_3, wrap=False))
# right: the four sentences to say on the phone
kids.append(D.box(IX0 + HW + 20, HY2, HW, BLOCK_H, color=K.PAPER, radius=8,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("打电话时说这四句", x=IX0 + HW + 36, y=HY2 + 10, w=220,
                      size=12.5, color=K.INK, font=K.SEMI, wrap=False))
SAY = ["我住云栖里 1602，房东陆文君",
       "位置是 K-02，厨房龙头阀根那个标记牌",
       "上次 2024-03 换过陶瓷阀芯和垫片",
       "我拍了标记牌，照片在房谱里能看到"]
for i, s_ in enumerate(SAY):
    yy = HY2 + 30 + i * 15
    kids.append(D.box(IX0 + HW + 36, yy + 5, 5, 5, color=K.YELLOW, radius=1))
    kids.append(D.text_el(s_, x=IX0 + HW + 50, y=yy, w=HW - 66, size=10.5,
                          color=K.INK_2, wrap=False))

# ============================================================== footer ======
# v03: at FY = cardBottom-92 the QR caption's glyphs (y+3 .. y+13) landed on the
# card border, so the footer band is 104px and the QR is 60.
FY = CY + CH_ - 104
kids.append(K.hline(IX0, IX1, FY, K.LINE, 1))
kids.append(D.text_el("住址履历：12 个锚点 · 2023-07-01 → 2026-09-30 · 累计维修 ¥440",
                      x=IX0, y=FY + 14, w=540, size=11.5, color=K.INK_3,
                      wrap=False))
kids.append(D.text_el("看到这张卡上有你不认识的修法，说明有人绕过房谱直接找人修了——"
                      "拍一张那个位置的标记牌，履历里就有了。", x=IX0, y=FY + 34,
                      w=600, size=11.5, color=K.INK_2, wrap=False))
# v02: at FY+8 with size 72 the block's quiet zone plus the caption at FY+86
# both fell below the card edge; the footer band is 92px so the QR is 62 and the
# caption sits at FY+74.
kids.append(K.qr_dummy(IX1 - 60, FY + 8, 60, seed=1602, dark="#141B26",
                       modules=21))
kids.append(D.text_el("扫码进入履历（图块为示意）", x=IX1 - 210, y=FY + 74,
                      w=210, size=9.5, color=K.INK_4, align="RIGHT",
                      wrap=False))

r = bk.emit(CASE, kids, W, H, bg="#D7DBDEFF")