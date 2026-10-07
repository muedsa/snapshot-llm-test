"""B03 case-02 · 边缘语言 · 取餐牌与会员卡印刷稿.

Primary capability under test: the corner / border / clip family.
  borderRadiusTopLeft / TopRight / BottomLeft / BottomRight (four independent
  radii), per-side borders (borderLeft / borderTop / borderRight /
  borderBottom overriding the uniform one), ClipRRect with per-corner radii,
  ClipOval, and the practical difference between "colour + radius" and a real
  clip path.

Scene: 云吞巷 (fictional) hands its print shop one spec sheet for a pickup
ticket, a member card and a stamp card. The sheet is a working document: the
printer needs exact dimensions, bleed, cut rules and ink notes.

Stage 1 = dedicated capability probe, stage 2 = the work.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

PAPER = "#F2EEE6FF"
WHITE = "#FFFFFF"
INK = "#1C1917FF"
INK2 = "#57534EFF"
INK3 = "#A8A29EFF"
RED = "#C2410CFF"
GREEN = "#15803DFF"
GOLD = "#B45309FF"

# ------------------------------------------------------------------- content
ORDER = {"no": "A-0721", "table": "T-12", "items": [
    ("鲜虾云吞面", "大碗", 1, 28.0),
    ("牛筋丸", "中碗", 2, 16.0),
    ("冻柠茶", "去冰", 1, 12.0)], "pay": "微信支付", "mins": 6}
MEMBER = {"name": "林 砚", "tier": "金桔 GOLD", "no": "YT-0042 8817",
          "pts": 3840, "exp": "2027-04-30", "since": "2023-11"}
PUNCHED, TOTAL_PUNCH = 6, 10
JOB = {"no": "YH-2609-014", "date": "2026-09-28", "press": "文盛印务 / 3 色胶印",
       "stock": "350g 卡纸 + 250g 卡纸裱合", "bleed": "3 mm",
       "size": "取餐牌 90×124 mm · 会员卡 85.6×54 mm · 集章卡 85×37.5 mm"}


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1280, 900
    k = [W.t2("PROBE c02 · 圆角 / 单边边框 / 裁剪能力探针", 40, 20, size=19,
              color=INK, style="BOLD", w=900, h=26),
         W.t2("纸色底，每格只测一种写法", 40, 48, size=12, color=INK3, w=600,
              h=18)]

    def cell(col, row, label, widget, note="", w=280, h=200):
        x = 40 + col * 400
        y = 88 + row * 250
        k.append(box(x, y, w, h, color="#E7E1D8FF", radius=10,
                     border="1 SOLID #D6D3D1FF"))
        k.append(el("Positioned", {"left": x + 20, "top": y + 16,
                                   "width": w - 40, "height": h - 58},
                    [widget]))
        k.append(W.t2(label, x + 14, y + h - 40, size=12, color=INK, w=w - 26,
                      h=D.est_lines(label, 12, w - 26) * 17))
        if note:
            k.append(W.t2(note, x + 14, y + h - 20, size=10, color=INK3,
                          w=w - 26, h=14))

    R = {"borderRadiusTopLeft": "64", "borderRadiusTopRight": "6",
         "borderRadiusBottomLeft": "6", "borderRadiusBottomRight": "64"}
    cell(0, 0, "A 四角独立圆角 TL64 TR6 BL6 BR64",
         el("Container", dict({"width": 200, "height": 120,
                               "color": "#0F172AFF"}, **R)),
         "四角互不影响")
    cell(1, 0, "B 统一圆角 64 对照",
         el("Container", {"width": 200, "height": 120, "color": "#0F172AFF",
                          "borderRadius": "64"}),
         "与 A 的差别就是「独立四角」")
    cell(2, 0, "C 单边边框 borderLeft 10 SOLID",
         el("Container", {"width": 200, "height": 120, "color": "#0F172AFF",
                          "border": "1 SOLID #FFFFFF44",
                          "borderLeft": "10 SOLID #F97316FF"}),
         "单边覆盖统一边框对应边")
    cell(0, 1, "D 上+下单边边框",
         el("Container", {"width": 200, "height": 120, "color": "#0F172AFF",
                          "borderTop": "8 SOLID #22D3EEFF",
                          "borderBottom": "8 SOLID #22D3EEFF"}),
         "只写两边时另两边无边框")
    cell(1, 1, "E 圆角 + 单边边框（边框是否跟着倒角）",
         el("Container", {"width": 200, "height": 120, "color": "#0F172AFF",
                          "border": "6 SOLID #FDE047FF",
                          "borderLeft": "14 SOLID #FDE047FF",
                          "borderRadiusTopLeft": "40",
                          "borderRadiusBottomLeft": "40"}),
         "倒角处的边框走向")
    cell(2, 1, "F ClipRRect 四角独立圆角",
         el("ClipRRect", dict({"clipBehavior": "ANTI_ALIAS"}, **R),
            [el("Container", {"width": 200, "height": 120,
                              "gradientType": "LINEAR",
                              "gradientColors": "#FDE68AFF,#FCA5A5FF",
                              "gradientBegin": "(0,0)",
                              "gradientEnd": "(1,1)"})]),
         "ClipRRect 与 Container 同格式")
    cell(0, 2, "G ClipOval 真实椭圆裁剪",
         el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
            [el("Container", {"width": 200, "height": 120,
                              "gradientType": "RADIAL",
                              "gradientColors": "#22D3EEFF,#0EA5E9FF",
                              "gradientCenter": "(0.4,0.35)",
                              "gradientRadius": "0.7"})]),
         "椭圆/圆形只能靠 ClipOval 或 shape=CIRCLE")
    cell(1, 2, "H ClipRect HARD_EDGE 硬边",
         el("ClipRect", {"clipBehavior": "HARD_EDGE"},
            [el("Container", {"width": 200, "height": 120,
                              "gradientType": "LINEAR",
                              "gradientColors": "#34D399FF,#065F46FF",
                              "gradientBegin": "(0,0)",
                              "gradientEnd": "(1,0)"})]),
         "硬边 = 像素对齐，无抗锯齿")
    cell(2, 2, "I ClipRRect r=200 的胶囊（超过半高）",
         el("ClipRRect", {"borderRadius": "200",
                          "clipBehavior": "ANTI_ALIAS"},
            [el("Container", {"width": 200, "height": 120,
                              "color": "#F472B6FF"})]),
         "半径大于半边长时的钳制行为")

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=PAPER)
    r = W.P.probe(dsl, "c02-edges")
    print("  probe c02-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1600, 1010
SUB = 700.0 / 25.4 * 90.0        # 90 mm on the sheet, arbitrary scale


def mm(v):
    return v * 700.0 / 25.4 / 90.0


def build():
    k = []
    # ---------------- header ----------------
    k.append(box(0, 0, CW, 100, color=WHITE))
    k.append(W.rule(0, 99, CW, "#D6D3D1FF", 1))
    k.append(W.t2("云吞巷 · 票券与卡片边缘规格稿", 56, 22, size=28, color=INK,
                  style="BOLD", w=700, h=38))
    k.append(W.t2("YUNTUN ALLEY / EDGE SPECIFICATION SHEET", 58, 62, size=11,
                  color=INK3, ls=3.0, w=640, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 900, "top": 20, "width": 644,
                               "height": 26},
                [el("Text", {"color": INK, "fontSize": "17",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "工单 %s" % JOB["no"]})]))
    k.append(el("Positioned", {"left": 900, "top": 46, "width": 644,
                               "height": 20},
                [el("Text", {"color": INK2, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "出稿 %s · %s" % (JOB["date"],
                                                      JOB["press"])})]))
    k.append(el("Positioned", {"left": 900, "top": 68, "width": 644,
                               "height": 20},
                [el("Text", {"color": INK2, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "用纸 %s" % JOB["stock"]})]))

    # ---------------- sheet ----------------
    F = W.Frame(56, 124, 1488, 830, fill="#FFFFFF", radius=16,
                border="1 SOLID #D6D3D1FF")
    F.add(F.tx("样张 · PROOFS", 32, 28, size=13, color=INK2, ls=2.4, w=400,
               h=18, font=D.MONO))
    F.add(F.rt("出血 %s · 裁切线 0.25 pt 实线 · 拼版 6P", 1456, 28, size=12,
               color=INK3, w=520, h=18, font=D.MONO))
    F.add(F.r(32, 56, 1424, "#E7E1D8FF", 1))

    # ===== pickup ticket A : diagonal cut corners =====
    TA_X, TA_Y, TA_W, TA_H = 76, 92, 250, 346
    F.add(F.tx("A · 取餐牌（对角切角）", TA_X, 62, size=12, color=INK, w=300,
               h=18))
    tk = []
    tk.append(el("Text", {"color": INK, "fontSize": "14",
                          "fontFamily": D.MONO, "letterSpacing": "1.4",
                          "text": "云吞巷 YUNTUN"}))
    tk.append(el("Text", {"color": INK3, "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "取餐牌 PICKUP"}))
    tk.append(el("SizedBox", {"height": "7"}))
    tk.append(el("Container", {"height": "1", "color": "#E7E1D8FF"}))
    tk.append(el("SizedBox", {"height": "8"}))
    tk.append(el("Text", {"color": INK, "fontSize": "30",
                          "fontFamily": D.MONO, "text": ORDER["no"]}))
    tk.append(el("SizedBox", {"height": "6"}))
    tk.append(el("Text", {"color": INK3, "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "台号 %s · 预计 %d 分钟"
                                  % (ORDER["table"], ORDER["mins"])}))
    tk.append(el("SizedBox", {"height": "7"}))
    for name, spec, qty, price in ORDER["items"]:
        tk.append(el("SizedBox", {"height": "22"}))
        tk.append(el("Row", {"mainAxisAlignment": "SPACE_BETWEEN"}, [
            el("Text", {"color": INK, "fontSize": "14",
                        "fontFamily": D.UI, "text": name}),
            el("Text", {"color": INK2, "fontSize": "11",
                        "fontFamily": D.MONO,
                        "text": "%s x%d · %d" % (spec, qty, price)})]))
    tk.append(el("SizedBox", {"height": "7"}))
    tk.append(el("Container", {"height": "1", "color": "#E7E1D8FF"}))
    tk.append(el("SizedBox", {"height": "8"}))
    tk.append(el("Row", {"mainAxisAlignment": "SPACE_BETWEEN"}, [
        el("Text", {"color": INK, "fontSize": "13", "fontFamily": D.UI,
                    "text": "合计"}),
        el("Text", {"color": INK, "fontSize": "18", "fontFamily": D.MONO,
                    "text": "%.0f 元" % sum(i[3] for i in ORDER["items"])})]))
    tk.append(el("SizedBox", {"height": "7"}))
    tk.append(el("Text", {"color": INK3, "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "%s · 凭此牌取餐" % ORDER["pay"]}))
    F.add(F.at(TA_X, TA_Y, TA_W, TA_H,
               el("Container",
                  {"width": TA_W, "height": TA_H, "color": WHITE,
                   "border": "1 SOLID #D6D3D1FF",
                   "borderRadiusTopLeft": "46", "borderRadiusBottomRight": "46",
                   "padding": "(18,24)"},
                  [el("Column", {"crossAxisAlignment": "STRETCH"}, tk)])))

    # ===== pickup ticket B : single-side border band =====
    TB_X = 380
    F.add(F.tx("B · 取餐牌（左侧色带）", TB_X, 62, size=12, color=INK, w=300,
               h=18))
    tb = []
    tb.append(el("Text", {"color": WHITE, "fontSize": "14",
                          "fontFamily": D.MONO, "letterSpacing": "1.4",
                          "text": "云吞巷 YUNTUN"}))
    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO, "text": "外带 TAKEAWAY"}))
    tb.append(el("SizedBox", {"height": "7"}))
    tb.append(el("Container", {"height": "1", "color": "#FFFFFF33"}))
    tb.append(el("SizedBox", {"height": "8"}))
    tb.append(el("Text", {"color": WHITE, "fontSize": "30",
                          "fontFamily": D.MONO, "text": "B-0448"}))
    tb.append(el("SizedBox", {"height": "6"}))
    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "预计 11 分钟 · 堂食"}))
    tb.append(el("SizedBox", {"height": "7"}))
    for name, spec, qty, price in (
            ("干炒牛河", "大", 1, 32), ("白灼菜心", "份", 1, 18),
            ("冻柠茶", "少冰", 2, 12)):
        tb.append(el("SizedBox", {"height": "22"}))
        tb.append(el("Row", {"mainAxisAlignment": "SPACE_BETWEEN"}, [
            el("Text", {"color": WHITE, "fontSize": "14",
                        "fontFamily": D.UI, "text": name}),
            el("Text", {"color": "#FED7AAFF", "fontSize": "11",
                        "fontFamily": D.MONO,
                        "text": "%s x%d · %d" % (spec, qty, price)})]))
    tb.append(el("SizedBox", {"height": "7"}))
    tb.append(el("Container", {"height": "1", "color": "#FFFFFF33"}))
    tb.append(el("SizedBox", {"height": "8"}))
    tb.append(el("Row", {"mainAxisAlignment": "SPACE_BETWEEN"}, [
        el("Text", {"color": WHITE, "fontSize": "13", "fontFamily": D.UI,
                    "text": "合计"}),
        el("Text", {"color": WHITE, "fontSize": "18",
                    "fontFamily": D.MONO, "text": "86 元"})]))
    tb.append(el("SizedBox", {"height": "7"}))
    tb.append(el("Text", {"color": "#FED7AAFF", "fontSize": "10",
                          "fontFamily": D.MONO,
                          "text": "会员 %s 可积分" % MEMBER["no"][:8]}))
    F.add(F.at(TB_X, TA_Y, TA_W, TA_H,
               el("Container",
                  {"width": TA_W, "height": TA_H,
                   "gradientType": "LINEAR",
                   "gradientColors": "#7C2D12FF,#C2410CFF",
                   "gradientBegin": "(0,0)", "gradientEnd": "(0.6,1)",
                   "borderRadiusTopRight": "40", "borderRadiusBottomLeft": "40",
                   "border": "1 SOLID #7C2D12FF",
                   "padding": "(18,24)"},
                  [el("Column", {"crossAxisAlignment": "STRETCH"}, tb)])))

    # dimension lines for ticket A (panel-local coordinates)
    F.add(W.dim_h(TA_X, TA_X + TA_W, TA_Y + TA_H + 22, "250 px = 90 mm",
                  color="#8A8175FF", size=10))
    F.add(W.dim_v(TA_Y, TA_Y + TA_H, TA_X - 18, "346 px", color="#8A8175FF"))

    # ===== member card =====
    MC_X, MC_Y, MC_W, MC_H = 700, 92, 340, 214
    F.add(F.tx("C · 会员卡（对角小圆角）", MC_X, 62, size=12, color=INK, w=320,
               h=18))
    mc = [F.at(20, 20, 64, 64,
               el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
                  [el("Stack", {"fit": "EXPAND"}, [
                      el("Container", {"width": 64, "height": 64,
                                       "color": None,
                                       "alignment": "CENTER",
                                       "gradientType": "RADIAL",
                                       "gradientColors":
                                           "#FDE68AFF,#F59E0BFF",
                                       "gradientFocal": "(0.4,0.35)",
                                       "gradientFocalRadius": "0.5"}),
                      el("Text", {"text": "林", "fontSize": "30",
                                  "fontFamily": D.CJK_SERIF,
                                  "color": "#7C2D12FF",
                                  "textAlign": "CENTER"})])]))]
    mc.append(F.tx(MEMBER["tier"], 100, 24, size=15, color="#FDE68AFF",
                   w=200, h=22, style="BOLD", ls=1.4))
    mc.append(F.tx("会员卡 MEMBER CARD", 100, 48, size=10, color="#FCD34DCC",
                   w=200, h=15, ls=1.8, font=D.MONO))
    mc.append(F.r(20, 106, 300, "#FFFFFF22", 1))
    for i, (lab, val) in enumerate((("卡号", MEMBER["no"]),
                                    ("积分", "%d 分" % MEMBER["pts"]),
                                    ("有效期至", MEMBER["exp"]))):
        lx = 20 + i * 104
        mc.append(F.tx(lab, lx, 122, size=10, color="#FCD34DAA", w=100, h=15))
        mc.append(F.tx(val, lx, 140, size=13, color=WHITE, w=104, h=19,
                       font=D.MONO))
    mc.append(F.tx("自 %s 起 · 积分 1 元 = 1 分" % MEMBER["since"], 20, 176,
                   size=10, color="#FCD34D88", w=300, h=15))
    F.add(F.at(MC_X, MC_Y, MC_W, MC_H,
               el("Container",
                  {"width": MC_W, "height": MC_H, "gradientType": "LINEAR",
                   "gradientColors": "#0F172AFF,#312E81FF",
                   "gradientBegin": "(0,0)", "gradientEnd": "(1,1)",
                   "borderRadiusTopLeft": "26", "borderRadiusBottomRight": "26",
                   "borderTop": "4 SOLID #F59E0BFF",
                   "border": "1 SOLID #FFFFFF22"},
                  [el("Stack", {"fit": "EXPAND"}, mc)])))

    # ===== stamp card =====
    SC_X, SC_Y, SC_W, SC_H = 700, 352, 340, 150
    F.add(F.tx("D · 集章卡（10 格 · 椭圆冲孔）", SC_X, 324, size=12, color=INK,
               w=340, h=18))
    sc = [F.tx("云吞巷 · 集章卡", 18, 14, size=13, color=INK, w=240, h=19,
               style="BOLD"),
          F.rt("%d / %d" % (PUNCHED, TOTAL_PUNCH), 322, 16, size=13,
               color=RED, w=90, h=19, font=D.MONO)]
    for i in range(TOTAL_PUNCH):
        cx = 34 + i * 30
        filled = i < PUNCHED
        sc.append(F.at(cx - 11, 52, 22, 22,
                       el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
                          [el("Container", {
                              "width": 22, "height": 22,
                              "color": (RED if filled else "#FFFFFF00"),
                              "border": ("0 SOLID #FFFFFF00" if filled
                                         else "2 SOLID #D6D3D1FF")})])))
    sc.append(F.tx("满 %d 章送一份云吞" % TOTAL_PUNCH, 18, 90, size=11,
                   color=INK2, w=240, h=16))
    sc.append(F.tx("不设有效期 · 可与会员卡同用", 18, 112, size=10, color=INK3,
                   w=240, h=15))
    sc.append(W.hatch(18, 130, 304, 8, "#E7E1D8FF", period_px=4.0, axis="x",
                      alpha_end="00"))
    F.add(F.at(SC_X, SC_Y, SC_W, SC_H,
               el("Container",
                  {"width": SC_W, "height": SC_H, "color": "#FFFDF7FF",
                   "borderRadiusTopRight": "24", "borderRadiusBottomLeft": "24",
                   "border": "1 SOLID #E7E1D8FF",
                   "padding": "(0,0)"},
                  [el("Stack", {"fit": "EXPAND"}, sc)])))
    F.add(W.dim_h(MC_X, MC_X + MC_W, SC_Y + SC_H + 20,
                  "340 px = 85 mm", color="#8A8175FF", size=10))

    # ===== edge recipe column =====
    RX = 1092
    F.add(F.tx("边缘配方 · EDGE RECIPES", RX, 62, size=12, color=INK, ls=2.0,
               w=340, h=18, font=D.MONO))
    RECIPES = [
        ("对角切角", {"borderRadiusTopLeft": "46",
                      "borderRadiusBottomRight": "46"},
         "borderRadiusTopLeft/ BottomRight = 46"),
        ("镜像切角", {"borderRadiusTopRight": "40",
                      "borderRadiusBottomLeft": "40"},
         "TopRight / BottomLeft = 40"),
        ("单边色带", {"borderLeft": "14 SOLID #C2410C"},
         "borderLeft 覆盖 border 对应边"),
        ("上下描边", {"borderTop": "8 SOLID #0F766E", "borderBottom": "8 SOLID #0F766E"},
         "只写两边，另两边无边框"),
        ("对角小圆角", {"borderRadiusTopLeft": "26",
                        "borderRadiusBottomRight": "26"},
         "会员卡：TL/BR 26，另两角 6"),
        ("胶囊冲孔", {"clip": "ClipOval"},
         "10 个 ClipOval，半径 11"),
    ]
    ry = 92
    for name, recipe, note in RECIPES:
        F.add(F.at(RX, ry, 150, 58, el(
            "Container",
            dict({"width": 150, "height": 58, "color": PAPER,
                  "border": "1 SOLID #E7E1D8FF",
                  "borderRadius": "10",
                  "alignment": "CENTER"},
                 **{k: v for k, v in recipe.items() if k != "clip"}),
            [el("Text", {"text": name, "fontSize": "13",
                         "fontFamily": D.UI, "color": INK,
                         "textAlign": "CENTER"})])))
        F.add(F.tx(note, RX + 164, ry + 8, size=10, color=INK3, w=200,
                   h=D.est_lines(note, 10, 200) * 15))
        ry += 68
    PUNCH_NOTE = ("冲孔用 ClipOval + 描边模拟：DSL 没有真正的「挖空」布尔运算，"
                 "纸色圆盘 + 内圈是行业里最接近的近似，样张已注明。")
    F.add(F.tx(PUNCH_NOTE, RX, ry + 6, size=10, color=INK3, w=364,
               h=D.est_lines(PUNCH_NOTE, 10, 364) * 15))

    # ===== bottom notes =====
    NY = 560
    F.add(F.r(32, NY, 1424, "#E7E1D8FF", 1))
    F.add(F.tx("印刷说明 · PRODUCTION NOTES", 32, NY + 18, size=12, color=INK2,
               ls=2.2, w=400, h=18, font=D.MONO))
    NOTES = [
        ("出血", "四边外扩 %s；成品尺寸按裁切线计。" % JOB["bleed"]),
        ("裁切", "0.25 pt 实线，黑色，勿转专色。"),
        ("圆角", "最小 2 mm；小于 2 mm 的角请印厂改为刀模。"),
        ("色带", "左侧 3.5 mm 色带用专色 PANTONE 1585 C。"),
        ("卡面", "会员卡双面，背面仅烫金边，宽度与正面描边一致。"),
        ("刀线", "集章卡 10 孔由模切刀完成，间距公差 ±0.3 mm。"),
    ]
    ny = NY + 46
    for i, (lab, txt) in enumerate(NOTES):
        col = i % 3
        row = i // 3
        nx = 32 + col * 480
        yy = ny + row * 46
        F.add(F.tx(lab, nx, yy, size=12, color=INK, w=70, h=18,
                   style="BOLD"))
        F.add(F.tx(txt, nx + 76, yy + 1, size=11, color=INK2, w=380,
                   h=D.est_lines(txt, 11, 380) * 16))
    F.add(F.r(32, ny + 108, 1424, "#E7E1D8FF", 1))
    F.add(F.tx("尺寸表 · SHEET SIZES", 32, ny + 124, size=12, color=INK2,
               ls=2.2, w=400, h=18, font=D.MONO))
    SZ = [("取餐牌 A", "90 × 124 mm", "对角切角 5.2 mm", "350g 卡纸"),
          ("取餐牌 B", "90 × 124 mm", "镜像切角 4.7 mm", "350g 卡纸"),
          ("会员卡", "85.6 × 54 mm", "对角圆角 3.1 mm", "250g 裱合"),
          ("集章卡", "85 × 37.5 mm", "镜像切角 2.8 mm", "350g 卡纸")]
    ty = ny + 152
    for i, (name, size, radius, stock) in enumerate(SZ):
        x = 32 + i * 360
        F.add(F.at(x, ty, 340, 46,
                   el("Container", {"width": 340, "height": 46,
                                    "color": PAPER, "borderRadius": "8",
                                    "border": "1 SOLID #E7E1D8FF"},
                      [el("Stack", {"fit": "EXPAND"}, [
                          F.tx(name, 12, 6, size=13, color=INK, w=160, h=19),
                          F.rt(size, 328, 7, size=12, color=INK2, w=120, h=18,
                               font=D.MONO),
                          F.tx(radius, 12, 26, size=11, color=INK3, w=180,
                               h=16),
                          F.rt(stock, 328, 26, size=11, color=INK3, w=140,
                               h=16)])])))
    k.append(F.render())

    # ---------------- footer ----------------
    k.append(W.rule(56, 976, 1488, "#D6D3D1FF", 1))
    k.append(W.t2("云吞巷（虚构商户）· 本稿为演示用设计交付物，票号、会员资料、"
                  "工单与印厂信息均为自拟，不代表任何真实订单或授权。",
                  56, 984, size=10, color=INK3, w=1000, h=16))
    k.append(el("Positioned", {"left": 1000, "top": 982, "width": 544,
                               "height": 20},
                [el("Text", {"color": INK3, "fontSize": "11",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s / %s / rev.C" % (JOB["no"],
                                                          JOB["date"])})]))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=PAPER)
    r = W.P.render_final(dsl, "case-02", "final")
    print("  case-02", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-02 stage 1: capability probe")
    probe()
    print("== case-02 stage 2: work")
    build()