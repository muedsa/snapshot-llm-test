#!/usr/bin/env python
"""B05 case-08 · 手机长图 900×1900 · 分享给下一任租客的「这套房的故事」

载体：手机长图（竖向分享卡）900×1900。不是 App 界面截图——它是陆文君从
      房谱里"导出为一张图"，直接发到微信群里的那种东西。宽 900、高 1900，
      比例 0.474，是社交软件里被点开就是全屏、不能缩放的那种长条图。
受众：下一任租客（未署名，画像：看房阶段，关心"这房以前出过什么问题"）。
用户意图：30 秒看完这套房 39 个月里发生了什么，并且知道"哪些事他们已经
      提前替我做完了"。
状态：生成于退租结算完成后 2026-10-01。含 2 处新增损伤的坦白说明，
      以及 E-02 暂挂这一件"还没做完的事"。
视觉主张：叙事性长图，正文用衬线（Noto Serif CJK SC）读起来像一份交接说明，
      与前面所有无衬线的操作界面明确区分；顶部把"这套房被照顾过"做成
      一句人话，下面才是数据。

v02 修正（v01 实际看图后）：
  * v01 底部三块（电表抄见 / 页脚 / 虚构声明）互相压住并超出 1900 画布 →
    全局竖直预算重排：封面 496，网格卡 88px，页脚与声明合成一条 148px 底栏；
  * 时间轴首尾标签超出左右版心 → 标签宽 100，首尾改为左右对齐；
  * 左侧"聊天背景"竖条与圆点在成品长图里读作无意义装饰 → 移除。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-08"
W, H = 900, 1900
kids = []

M = 72
CW = W - 2 * M
NIGHT = K.NIGHT
SERIF = K.SERIF


def st(x, y, s, size=15, color="#F2F6FA", w=None, align=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=SERIF,
                     align=align)


def sect(n, y, title, accent=K.A(K.YELLOW, "CC"), rule_col="#22303F"):
    """`01 / 三十九个月里，这套房发生了什么` + a rule under it."""
    return [D.text_el("%02d" % n, x=M, y=y, w=60, size=13, color=accent,
                      font=K.MONO, style="BOLD", ls=1.4, wrap=False),
            D.text_el(title, x=M + 44, y=y - 2, w=CW - 44, size=20,
                      color="#FFFFFF", font=SERIF, wrap=False),
            D.hline(M, W - M, y + 34, rule_col, 1)]


# ================================================================ ground ====
kids.append(D.box(0, 0, W, H, color=NIGHT))

# ============================================================== cover ======
CV_H = 496
kids.append(K.gradient_v(0, 0, W, CV_H, "#14202E", NIGHT, steps=40))
kids.append(K.blueprint(W, CV_H, step=36, alpha="14"))

kids.append(D.box(M, 66, 44, 44, color=K.YELLOW, radius=8,
                  border="2 SOLID #14181FFF"))
kids.append(D.text_el("房", x=M, y=74, w=44, size=23, color="#14181FFF",
                      font=K.DISPLAY, align="CENTER", wrap=False))
kids.append(D.text_el("房谱 HOMESPEC", x=M + 58, y=68, w=320, size=20,
                      color="#FFFFFF", font=K.SEMI, ls=0.2, wrap=False))
kids.append(D.text_el("住址履历 · 交接说明", x=M + 58, y=92, w=320, size=12,
                      color="#8FA3B6", ls=1.6, wrap=False))
kids.append(D.text_el("2026-10-01 生成", x=W - M - 200, y=76, w=200, size=12,
                      color="#7C8B9D", font=K.MONO, align="RIGHT", wrap=False))

kids.append(st(M, 152, "这套房住了 3 年零 3 个月，", 34, "#FFFFFF"))
kids.append(st(M, 200, "换过 2 处零件，", 34, "#FFFFFF"))
kids.append(st(M, 248, "2 个地方有新的划痕和钉孔。", 34, K.A(K.YELLOW, "E8")))
kids.append(st(M, 300, "这些我们没有藏。下面是逐条明细。", 15, "#9FB2C4"))

# v02: at 54px pitch the third card's bottom (y+54) crossed the cover's hazard
# stripe, so the stack starts at 330 with a 52px pitch and 46px cards.
tags = [("K-02", "厨房 · 龙头阀根", "2024-03 换阀芯，至今不渗", K.GREEN),
        ("B-02", "卫生间 · 台盆下 U 型弯", "2025-06 换 U 型弯，已闭环", K.GREEN),
        ("K-01", "厨房 · 水槽下左角", "本次新增划痕 3 道", K.RED)]
ty = 330
for code, place, note, col in tags:
    kids.append(D.box(M, ty, CW, 46, color="#16202BFF", radius=10,
                      border="1 SOLID #22303F"))
    kids.append(K.anchor_tag(M + 14, ty + 9, 62, 28, code, scale=0.58))
    kids.append(D.text_el(place, x=M + 90, y=ty + 8, w=320, size=13.5,
                          color="#FFFFFF", font=K.MED, wrap=False))
    kids.append(D.text_el(note, x=M + 90, y=ty + 26, w=420, size=11,
                          color=col, wrap=False))
    kids.append(K.circle(W - M - 26, ty + 23, 5, col))
    ty += 52

kids.append(K.hazard_stripe(0, CV_H - 12, W, 12, c1=NIGHT, pitch=20))

# ======================================================= 01 · 三十九个月 =====
S1 = CV_H + 40
kids += sect(1, S1, "三十九个月里，这套房发生了什么")

TL_Y = S1 + 56
TL_X0, TL_X1 = M + 58, W - M - 58
kids.append(D.box(TL_X0 - 6, TL_Y + 22, TL_X1 - TL_X0 + 12, 3, color="#2A3A4C"))
MARKS = [(0.00, "2023-07", ("入住首拍", "12 个锚点建档"), K.BLUE, "first"),
         (0.19, "2024-03", ("R-2403-118", "换龙头阀芯 ¥180"), K.GREEN, "mid"),
         (0.62, "2025-06", ("R-2506-042", "换 U 型弯 ¥260"), K.GREEN, "mid"),
         (0.92, "2026-09", ("退租拍摄", "12 张入库"), K.BLUE, "mid"),
         (1.00, "2026-10", ("差分完成", "新增损伤 ¥200"), K.RED, "last")]
for t, date, (l1, l2), col, anchor in MARKS:
    mx = TL_X0 + (TL_X1 - TL_X0) * t
    below = anchor in ("first", "mid") and MARKS.index(
        (t, date, (l1, l2), col, anchor)) % 2 == 0
    if anchor == "last":
        below = False
    kids.append(D.vline(mx, TL_Y + (14 if below else 26), TL_Y + 23.5,
                        "#2A3A4C", 1))
    kids.append(K.circle(mx, TL_Y + 23.5, 7, NIGHT))
    kids.append(K.circle(mx, TL_Y + 23.5, 5, col))
    ly = TL_Y + (40 if below else -32)
    if anchor == "first":
        lx, al, lw_ = M, "LEFT", 116
    elif anchor == "last":
        lx, al, lw_ = W - M - 116, "RIGHT", 116
    else:
        lx, al, lw_ = mx - 58, "CENTER", 116
    kids.append(D.text_el(date, x=lx, y=ly, w=lw_, size=11, color=col,
                          font=K.MONO, align=al, wrap=False))
    for i, ln in enumerate((l1, l2)):
        kids.append(D.text_el(ln, x=lx, y=ly + 15 + i * 13, w=lw_, size=10,
                              color="#9FB2C4", align=al, wrap=False))

# ======================================================= 02 · 逐锚点状态 =====
S2 = TL_Y + 96
kids += sect(2, S2, "12 个锚点现在各自是什么状态")

GY = S2 + 50
GW = (CW - 2 * 14) / 3.0
GH = 88
ORDER = ["A-01", "A-02", "A-03", "K-01", "K-02", "K-03",
         "B-01", "B-02", "W-01", "W-02", "E-01", "E-02"]
STATUS = {"A-01": ("same", "与 2023-07 一致"), "A-02": ("same", "锁舌正常"),
          "A-03": ("skip", "本轮未拍"), "K-01": ("new", "新增划痕 3 道"),
          "K-02": ("fixed", "2024-03 已闭环"), "K-03": ("skip", "本轮未拍"),
          "B-01": ("same", "无开裂霉斑"), "B-02": ("fixed", "2025-06 已闭环"),
          "W-01": ("same", "漆面无变化"), "W-02": ("new", "新增钉孔 2 个"),
          "E-01": ("same", "接口无渗水"), "E-02": ("hold", "暂挂 · 待补拍")}
for i, aid in enumerate(ORDER):
    cat, note = STATUS[aid]
    if cat in K.CATS:
        cname, col = K.CATS[cat][0], K.CATS[cat][1]
    else:
        cname, col = "未拍摄", K.INK_3
    gx = M + (i % 3) * (GW + 14)
    gy = GY + (i // 3) * (GH + 10)
    kids.append(D.box(gx, gy, GW, GH, color="#16202BFF", radius=10,
                      border="1 SOLID " + ("#2A3A4C" if cat != "new"
                                           else K.A(K.RED, "66"))))
    kids.append(K.anchor_tag(gx + 14, gy + 13, 62, 28, aid, scale=0.60))
    kids.append(D.text_el(cname, x=gx + GW - 92, y=gy + 17, w=78, size=11.5,
                          color=col, font=K.MED, align="RIGHT", wrap=False))
    kids.append(D.hline(gx + 14, gx + GW - 14, gy + 50, "#22303F", 1))
    kids.append(D.text_el(note, x=gx + 14, y=gy + 58, w=GW - 28, size=11,
                          color="#8FA3B6", wrap=False))

# ======================================================= 03 · 两处新增 =======
S3 = GY + 4 * (GH + 10) + 14
# The two new-damage cards sit under the section rule, then section 04 continues
# without its own rule so the amber card reads as part of the same judgement
# rather than a new chapter.
kids += sect(3, S3, "两处新增损伤，共 ¥200", accent=K.A(K.RED, "CC"),
             rule_col=K.A(K.RED, "33"))

NEW = [("K-01", "不锈钢水槽支架右后角 3 道划痕，深度 0.12mm", "¥120"),
       ("W-02", "出风口右下 2 个膨胀螺栓钉孔，直径 8mm，无渗水", "¥80")]
ny = S3 + 50
for code, detail, amt in NEW:
    kids.append(D.box(M, ny, CW, 66, color="#22161AFF", radius=10,
                      border="1 SOLID " + K.A(K.RED, "4D")))
    kids.append(D.box(M, ny, 4, 66, color=K.RED,
                      radii={"TopLeft": 10, "BottomLeft": 10}))
    kids.append(K.anchor_tag(M + 18, ny + 19, 66, 28, code, scale=0.62))
    kids.append(D.text_el(detail, x=M + 100, y=ny + 15, w=CW - 200, size=12.5,
                          color="#F2F6FA", wrap=False))
    kids.append(D.text_el("判定：租客责任", x=M + 100, y=ny + 37, w=200,
                          size=11, color=K.A(K.RED, "D0"), wrap=False))
    kids.append(D.text_el(amt, x=W - M - 96, y=ny + 19, w=80, size=22,
                          color="#FFFFFF", font=K.DISPLAY, align="RIGHT",
                          ls=-0.8, wrap=False))
    ny += 74

# ======================================================= 04 · 还没做完 ======
OP_Y = ny + 16
kids.append(D.box(M, OP_Y, CW, 82, color=K.mix(K.AMBER, NIGHT, 0.86), radius=10,
                  border="1 SOLID " + K.A(K.AMBER, "4D")))
kids.append(K.anchor_tag(M + 18, OP_Y + 14, 66, 28, "E-02", scale=0.62))
kids.append(D.text_el("有一件事还没做完：E-02 阳台地漏", x=M + 100, y=OP_Y + 14,
                      w=440, size=13, color=K.A(K.AMBER, "E0"), font=K.SEMI,
                      wrap=False))
kids.append(D.text_el("退租时拍了 4 张都没拍到标记牌，系统判「暂挂」，所以这个位置",
                      x=M + 100, y=OP_Y + 36, w=CW - 130, size=11.5,
                      color="#C8D4E0", wrap=False))
kids.append(D.text_el("既不计入损伤，也不当成没问题。补拍期限 2026-10-07",
                      x=M + 100, y=OP_Y + 54, w=CW - 130, size=11.5,
                      color="#C8D4E0", wrap=False))

# ======================================================= 05 · 你会拿到什么 ====
GT_Y = OP_Y + 82 + 28
kids += sect(5, GT_Y, "你搬进来时，会拿到什么")

GET = [("12", "个锚点标记牌", "贴在你家同样的位置，编号不变", K.YELLOW),
       ("39", "个月的历史照片", "每个锚点按时间排好，可逐张对比", K.BLUE),
       ("2", "条维修闭环记录", "换了什么、谁做的、质保多久", K.GREEN),
       ("¥200", "本次已结算", "从押金扣，已在 10-01 确认", K.INK_3)]
GY2 = GT_Y + 50
GW2 = (CW - 3 * 12) / 4.0
for i, (big, lab, note, col) in enumerate(GET):
    gx = M + i * (GW2 + 12)
    kids.append(D.box(gx, GY2, GW2, 100, color="#16202BFF", radius=10,
                      border="1 SOLID #22303F"))
    kids.append(D.text_el(big, x=gx + 16, y=GY2 + 14, w=GW2 - 32, size=29,
                          color=col, font=K.DISPLAY, ls=-1.2, wrap=False))
    kids.append(D.text_el(lab, x=gx + 16, y=GY2 + 48, w=GW2 - 32, size=12,
                          color="#FFFFFF", font=K.MED, wrap=False))
    for j, ln in enumerate(K.wrap_cjk(note, GW2 - 32, 10.5)[:2]):
        kids.append(D.text_el(ln, x=gx + 16, y=GY2 + 66 + j * 14, w=GW2 - 32,
                              size=10.5, color="#8FA3B6", wrap=False))

# ======================================================= 06 · 抄表 ==========
MR_Y = GY2 + 100 + 26
kids.append(D.box(M, MR_Y, CW, 58, color="#131C27FF", radius=10,
                  border="1 SOLID #22303F"))
kids.append(D.text_el("电表", x=M + 18, y=MR_Y + 12, w=60, size=11,
                      color="#7C8B9D", wrap=False))
kids.append(D.text_el("1284", x=M + 18, y=MR_Y + 30, w=70, size=15,
                      color="#7C8B9D", font=K.MONO, wrap=False))
kids.append(K.arrow(M + 80, MR_Y + 38, M + 112, MR_Y + 38, "#3D4C5C", 1.6, 7))
kids.append(D.text_el("3611", x=M + 120, y=MR_Y + 30, w=80, size=15,
                      color="#FFFFFF", font=K.MONO, style="BOLD", wrap=False))
kids.append(D.text_el("kWh", x=M + 120, y=MR_Y + 46, w=40, size=9.5,
                      color="#7C8B9D", font=K.MONO, wrap=False))
kids.append(D.vline(M + 224, MR_Y + 12, MR_Y + 46, "#22303F", 1))
kids.append(D.text_el("你只需核对这两个数", x=M + 246, y=MR_Y + 18, w=300,
                      size=12.5, color="#F2F6FA", font=K.MED, wrap=False))
kids.append(D.text_el("水电表读数在 App 里也能自己查。", x=M + 246, y=MR_Y + 38,
                      w=300, size=11, color="#8FA3B6", wrap=False))

# ====================================================== footer bar =========
BAR_Y = H - 158
kids.append(D.box(0, BAR_Y, W, 158, color="#080D13FF"))
kids.append(D.hline(M, W - M, BAR_Y + 16, "#1C2733", 1))
kids.append(D.text_el("房谱 HOMESPEC · 云栖里 3 号楼 1602 室 · 履历 2023-07-01 → 2026-09-30",
                      x=M, y=BAR_Y + 30, w=CW - 130, size=11, color="#5F7285",
                      font=K.MONO, wrap=False))
kids.append(D.text_el("这张长图由房东 陆文君 于 2026-10-01 导出并分享。",
                      x=M, y=BAR_Y + 50, w=CW - 130, size=11, color="#5F7285",
                      wrap=False))
kids.append(D.text_el("扫码可看 12 个锚点的原始照片与逐条判定",
                      x=M, y=BAR_Y + 70, w=CW - 130, size=11, color="#5F7285",
                      wrap=False))
kids.append(D.hline(M, W - M, BAR_Y + 90, "#1C2733", 1))
# v03: a 116-char CJK line at 10.5px needs ~2 lines in 640px, and the second
# line fell off the 1900 canvas. The copy is split explicitly into measured lines
# instead of relying on soft wrap, and the wrap width is 600 — at 632 the last
# glyphs landed on the QR block's quiet zone (measured in v03's render).
_kids = K.wrap_cjk(
    "虚构声明：房谱 HOMESPEC 是本作品集从零构想的产品。品牌、住址、人物、单号、"
    "金额与读数均为自拟示例数据，不是任何实际部署系统的输出；本组画面未做任何"
    "真实用户验证。", 600, 10.5)
for _i, _ln in enumerate(_kids[:2]):
    kids.append(D.text_el(_ln, x=M, y=BAR_Y + 100 + _i * 15, w=600,
                          size=10.5, color="#4E6072", wrap=False))
kids.append(D.text_el("上一任租客 林知远 · 房东 陆文君 · 经办 云栖里运营 周敏",
                      x=M, y=BAR_Y + 130, w=600, size=10.5, color="#4E6072",
                      wrap=False))
kids.append(K.qr_dummy(W - M - 84, BAR_Y + 30, 84, seed=1602, dark="#D8E4EE",
                       modules=21))
kids.append(D.text_el("图块为示意，非可扫描二维码", x=W - M - 116, y=BAR_Y + 118,
                      w=116, size=9, color="#4E6072", align="RIGHT",
                      wrap=False))

r = bk.emit(CASE, kids, W, H, bg=NIGHT)