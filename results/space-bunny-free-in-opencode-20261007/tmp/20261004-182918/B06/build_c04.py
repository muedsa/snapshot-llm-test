# -*- coding: utf-8 -*-
"""case-04 · 一个箭头不够用：体检报告的三条线

媒介：A4 竖版（1240 × 1754 @150dpi），贴在冰箱门上。
所有阈值均为公开的真实数值；每位受检者的实测值为自拟的演示数据。
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R            # noqa: E402
import kit as K            # noqa: E402

# 所有阈值均为公开的真实数值；value 为自拟的演示实测值。
ITEMS = [
    dict(name="丙氨酸氨基转移酶 ALT", short="ALT", ref="5 – 40",
         unit="IU/L", vmax=330, value=47, flag="↑",
         zones=[(5, 40, "#0F766EFF", "参考范围 5–40"),
                (40, 60, "#E2E8F0FF", "40–60 灰区"),
                (60, 300, "#F59E0BFF", "60 确认值：肝细胞损伤"),
                (300, 330, "#BE123CFF", "≥300 极度肝细胞损伤")],
         ticks=[(20, "20 排除值"), (40, None), (60, None), (300, None)],
         act="47 越过了参考上限 40，但没到 60 的确认值 → 熬夜、饮酒、脂肪肝、药物都可能造成；"
             "低于 20 才可排除许多与 ALT 升高有关的疾病。按科普建议调生活方式，1–3 个月后复查。",
         tone="#F59E0BFF"),
    dict(name="甲胎蛋白 AFP", short="AFP", ref="< 25",
         unit="µg/L", vmax=450, value=12, flag="",
         zones=[(0, 25, "#0F766EFF", "参考范围 <25"),
                (25, 400, "#E2E8F0FF", "25–400 这一段对诊断肝癌没有意义"),
                (400, 450, "#BE123CFF", "≥400 肝癌诊断阈值")],
         ticks=[(25, None), (400, None)],
         act="12，完全在参考范围内 → 正常。顺带记住一件事：AFP 这个指标的参考范围"
             "对『诊断肝癌』这个用途是没有意义的，真正的阈值是 400，是参考上限的 16 倍。",
         tone="#0F766EFF"),
    dict(name="空腹血糖", short="GLU", ref="3.9 – 6.1",
         unit="mmol/L", vmax=24, value=7.4, flag="↑",
         zones=[(0, 2.2, "#BE123CFF", "≤2.2 危急低"),
                (3.9, 6.1, "#0F766EFF", "参考范围 3.9–6.1"),
                (7.0, 11.1, "#F59E0BFF", "7.0 诊断阈值（任一次 ≥11.1）"),
                (22.2, 24, "#BE123CFF", "≥22.2 危急高")],
         ticks=[(2.2, None), (3.9, None), (6.1, None), (7.0, None), (11.1, None), (22.2, None)],
         act="7.4 越过了 7.0 这条糖尿病诊断阈值，但离 22.2 的危急值还很远 → "
             "该做的是带报告找医生（可加做糖化血红蛋白），不是上网搜「7.4 严不严重」。",
         tone="#BE123CFF"),
    dict(name="血小板计数 PLT", short="PLT", ref="125 – 350",
         unit="×10⁹/L", vmax=380, value=132, flag="",
         zones=[(125, 350, "#0F766EFF", "")],
         alt_zone=(100, 300, "#1D4ED8FF", "另一实验室参考范围 100–300"),
         ticks=[(125, "125 本院下限"), (350, "350 本院上限")],
         act="132 在本院范围内，但注意：有的机构把血小板参考值写成 100–300，"
             "有的写成 125–350 → 换医院复查前，先确认那张单子上的参考区间是哪一套。",
         tone="#1D4ED8FF"),
]

W, H = 1240, 1754          # A4 竖版 @150dpi
MG = 54                    # 页边距
CW = W - 2 * MG            # 1132
C = K.C04
D = R.fresh()
kids = []


class Placer(object):
    """Three-row collision-avoiding label placer. The DSL silently drops text
    that does not fit its box, so overlap must be prevented, not hoped away."""

    def __init__(self, rows_y):
        self.rows_y = rows_y
        self.used = [[] for _ in rows_y]

    def put(self, text, x, color, size=11, align="center", font=None):
        w = K.tw(text, size) + 10
        x0 = x - w / 2.0 if align == "center" else x
        for ri in range(len(self.rows_y)):
            if all(not (x0 < b and a < x0 + w) for (a, b) in self.used[ri]):
                self.used[ri].append((x0, x0 + w))
                return K.D.text_el(text, x=x0, y=self.rows_y[ri], w=w, h=size * 1.42,
                                   size=size, color=color, font=font or K.UI)
        return None


# ------------------------------------------------------------------ header
kids += [K.box(0, 0, W, 196, color=K.INK), K.box(0, 0, 8, 196, color=C)]
kids.append(K.one_line(MG, 24, "一个 ↑ 箭头，撑不起三个决定", size=46,
                       color=K.WHITE, font=K.BLACK))
kids.append(K.one_line(MG, 92, "报告上印的只有参考范围——那是 95% 健康人的区间，"
                               "所以 100 个健康人里必有 5 个带箭头",
                       size=20, color=K.A(C, 0.88)))
kids.append(K.one_line(MG, 126, "真正决定「要不要治」的医学决定水平，和决定「要不要抢救」的危急值，"
                                "报告上根本没有印",
                       size=20, color=K.A("#FFFFFF", 0.62)))
kids += K.chip(990, 32, "case-04 · 体检报告", fill=K.A(C, 0.22), fg="#FBC7D6",
               size=16, padx=18, h=34)[0]
kids.append(K.one_line(W - MG, 92, "10 件作品的第 4 件", size=15,
                       color=K.A("#FFFFFF", 0.42), anchor="RIGHT"))

# ------------------------------------------------------------------- legend
kids.append(K.one_line(MG, 214, "三条线", size=20, color=K.INK, font=K.SEMI))
kids.append(K.one_line(MG + 62, 218, "报告只印第一条", size=14, color=K.MUTE))
LEG = [("#0F766EFF", "参考范围", "95% 正常人群的取值区间。越线只说明「不在多数人里」，不等于有病。"),
       ("#F59E0BFF", "医学决定水平", "临床上据此判断「要治 / 不用治」的关键阈值，比参考范围窄得多。"),
       ("#BE123CFF", "危急值", "危及生命，必须立即处理。绝大多数人一辈子碰不到。")]
lw = (CW - 2 * 18) / 3.0
for i, (c, t, d) in enumerate(LEG):
    x = MG + i * (lw + 18)
    kids += [K.box(x, 246, lw, 104, color=K.WHITE, radius=14, border=K.bd(K.HAIR),
                   shadow="0 4 18 0 #0F172A0E")]
    kids.append(K.box(x + 18, 264, 8, 34, color=c, radius=4))
    kids.append(K.one_line(x + 36, 264, t, size=18, color=K.INK, font=K.SEMI))
    for j, ln in enumerate(K.wraps(d, 13, lw - 54)):
        kids.append(K.one_line(x + 36, 290 + j * 18, ln, size=13, color=K.INK3))

# ------------------------------------------------------------- indicator rows
LCW = 262                      # left column: name + what the lab really prints
AX = MG + 24 + LCW + 26        # axis starts right of the left column
AW = MG + CW - 24 - AX
RY, RH = 372, 244
for i, it in enumerate(ITEMS):
    y = RY + i * RH
    ch = RH - 10
    kids.append(K.box(MG, y, CW, ch, color=K.WHITE, radius=16, border=K.bd(K.HAIR),
                      shadow="0 4 18 0 #0F172A0E"))
    kids.append(K.box(MG, y, 5, ch, color=it["tone"], radius=2))
    kids.append(K.one_line(MG + 24, y + 12, it["name"], size=19, color=K.INK,
                           font=K.SEMI, w=LCW + 60))
    kids.append(K.one_line(MG + 24, y + 40, "单位 " + it["unit"], size=13, color=K.MUTE))
    # what the lab report actually prints - the whole point of the piece
    kids.append(K.box(MG + 24, y + 66, LCW, 80, color="#F8FAFCFF", radius=10))
    kids.append(K.one_line(MG + 36, y + 72, "化验单上真正印的（全部）", size=10, color=K.MUTE))
    kids.append(K.one_line(MG + 36, y + 86, it["short"], size=14, color=K.INK3,
                           font=K.SEMI, w=80))
    kids.append(K.one_line(MG + 24 + LCW - 12, y + 83, "%s %s" % (it["value"], it["flag"]),
                           size=19, color="#BE123CFF" if it["flag"] else K.INK,
                           font=K.BLACK, anchor="RIGHT"))
    kids.append(K.one_line(MG + 36, y + 114, "参考 " + it["ref"], size=12, color=K.MUTE))
    kids.append(K.one_line(MG + 24, y + 154, "↓ 右边这三条线，报告上一条都没印",
                           size=12, color=K.A(it["tone"], 0.95)))
    # the measured value, printed by us rather than by the lab
    vw = 178
    kids.append(K.box(AX + AW - vw, y + 12, vw, 50, color=K.A(it["tone"], 0.12),
                      radius=12, border=K.bd(K.A(it["tone"], 0.5))))
    kids.append(K.one_line(AX + AW - vw + 16, y + 21, "本人实测", size=13, color=K.INK3))
    kids.append(K.one_line(AX + AW - 16, y + 17, "%s %s" % (it["value"], it["flag"]),
                           size=27, color=K.mix(it["tone"], "#0B1220", 0.2),
                           font=K.BLACK, anchor="RIGHT"))

    # ---- the axis
    by, bh = y + 76, 24
    kids.append(K.box(AX, by, AW, bh, color="#F8FAFCFF", radius=6))
    for (a, b, c, _lab) in it["zones"]:
        x0 = AX + AW * (a / float(it["vmax"]))
        x1 = AX + AW * (b / float(it["vmax"]))
        kids.append(K.box(x0, by, max(2.0, x1 - x0), bh, color=c, radius=6))
    cap = Placer([by + bh + 8, by + bh + 26, by + bh + 44])
    az = it.get("alt_zone")
    if az:
        x0 = AX + AW * (az[0] / float(it["vmax"]))
        x1 = AX + AW * (az[1] / float(it["vmax"]))
        kids.append(K.box(x0, by - 16, max(2.0, x1 - x0), 8, color=az[2], radius=3))
        e = cap.put(az[3], x0 + 6, az[2], 11, "left")
        if e:
            kids.append(e)
    for (a, b, c, lab) in it["zones"]:
        if not lab:
            continue
        x0 = AX + AW * (a / float(it["vmax"]))
        x1 = AX + AW * (b / float(it["vmax"]))
        col = K.MUTE if c == "#E2E8F0FF" else K.mix(c, "#0B1220", 0.38)
        e = cap.put(lab, (x0 + x1) / 2.0, col, 11,
                    "left" if (x1 - x0) < 46 else "center")
        if e:
            kids.append(e)
    for (v, lab) in it["ticks"]:
        tx = AX + AW * (v / float(it["vmax"]))
        kids.append(K.box(tx - 0.5, by - 7, 1.0, bh + 14, color=K.A("#0B1220", 0.14)))
        if lab:
            e = cap.put(lab, tx, K.MUTE, 10, "center")
            if e:
                kids.append(e)
    # needle
    vx = AX + AW * (it["value"] / float(it["vmax"]))
    kids.append(K.box(vx - 2, by - 26, 4, bh + 26, color=K.INK))
    kids.append(K.box(vx - 42, by - 48, 84, 26, color=K.INK, radius=6))
    kids.append(K.ctr(vx, by - 43, str(it["value"]), w=84, size=15, color="#FFFFFF",
                      font=K.BLACK))
    # action strip
    kids.append(K.box(MG + 24, y + ch - 42, CW - 48, 32, color="#F8FAFCFF", radius=8))
    kids.append(K.box(MG + 24, y + ch - 42, 4, 32, color=it["tone"], radius=2))
    kids.append(K.one_line(MG + 38, y + ch - 36, "→ " + it["act"], size=13, color=K.INK3,
                           w=CW - 76, h=19))

# -------------------------------------------------------------- action table
TY = RY + 4 * RH + 10
kids.append(K.one_line(MG, TY, "看到箭头之后，按这张表做事", size=22, color=K.INK,
                       font=K.SEMI))
rows = [("参考值上限 15.0、你的结果 15.1", "这 0.1 的差值很可能没有什么意义",
         "结合年龄性别与前期准备情况判断，必要时复查", "#F1F5F9FF", K.INK3),
        ("首次异常，或结果落在临界值附近", "单次轻微波动很常见，趋势比单次数值更重要",
         "1–3 个月后复查，尽量在同一机构、同一方法下", K.A(C, 0.10), K.INK),
        ("同一项目，不同机构的参考区间不一样", "方法 / 仪器 / 试剂不同，参考值就不同",
         "换院前先确认那张单子用的是哪一套参考区间", "#F1F5F9FF", K.INK3),
        ("明显偏离 / 严重偏离 / 出现危急值", "已经不是观察的问题",
         "立即就医，把这张图和报告一起带去", K.A("#BE123C", 0.14), "#BE123CFF")]
hy = TY + 36
kids.append(K.box(MG, hy, CW, 30, color=K.INK, radius=8))
for cx, cw2, t in [(MG + 14, 420, "你看到的现象"), (MG + 500, 300, "它实际意味着"),
                   (MG + 830, 300, "该做什么")]:
    kids.append(K.one_line(cx, hy + 8, t, size=14, color="#FFFFFF", font=K.SEMI, w=cw2))
for i, (a, b, c, fill, fg) in enumerate(rows):
    ry = hy + 36 + i * 36
    kids.append(K.box(MG, ry, CW, 32, color=fill, radius=8))
    kids.append(K.one_line(MG + 14, ry + 8, a, size=14, color=fg, w=420))
    kids.append(K.one_line(MG + 500, ry + 8, b, size=14, color=K.INK3, w=300))
    kids.append(K.one_line(MG + 830, ry + 8, c, size=14, color=fg, w=300))

# -------------------------------------------------------------------- footer
FY = H - 108
kids.append(K.one_line(MG, FY, "参考范围、医学决定水平、危急值与复查建议依据：天津市卫生健康委员会科普"
                               "『化验单看到箭头先别慌』（wsjk.tj.gov.cn）；",
                       size=13, color=K.MUTE, w=1120))
kids.append(K.one_line(MG, FY + 20, "杭州市卫生健康委员会『体检报告中的参考值，你读懂了吗』"
                                   "（wsjkw.hangzhou.gov.cn，2023-02-01）；中国医学科普网"
                                   "『避免误区，正确解读体检报告单』（cnmsp.net）；",
                       size=13, color=K.MUTE, w=1120))
kids.append(K.one_line(MG, FY + 40, "百度健康医学科普『为什么体检报告数据看不懂』（health.baidu.com）"
                                   "（血小板两套参考范围的例子）。",
                       size=13, color=K.MUTE, w=1120))
kids.append(K.one_line(MG, FY + 60, "「34 岁受检者」及其四项实测值为我自拟的演示数据，不代表任何真实个人；"
                                   "本页不构成医疗建议，请以医生解读为准。",
                       size=13, color=K.MUTE, w=1120))
kids.append(K.one_line(W - MG, H - 34, "B06 · case-04", size=14, color=K.A(K.MUTE, 0.6),
                       anchor="RIGHT"))

dsl = K.root(kids, W, H, K.PAPER)
R.emit("case-04", dsl, final=("--final" in sys.argv))
