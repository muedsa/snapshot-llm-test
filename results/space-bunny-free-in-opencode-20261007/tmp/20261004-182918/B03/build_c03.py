"""B03 case-03 · 拣选层级 · 仓储手持终端.

Primary capability under test: boxShadow.
  ELEVATION_* names (0/1/2/3/4/6/8/9/12/16/24), the custom
  `x y blurRadius spreadRadius color blurStyle` form, several shadows in one
  attribute, coloured shadows, and the measured fact that ClipRect /
  ClipRRect / ClipOval crop a child's shadow while a Stack's own
  clipBehavior="HARD_EDGE" does not.

Scene: a rugged handheld terminal for a fulfilment-centre picker. The screen
must express "which bin is inside which" at a glance, so nesting depth is
carried by shadow depth, and a scrolling candidate list needs a viewport that
cuts both rows and their shadows cleanly.

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

BG = "#E2E8F0FF"
CARD = "#F8FAFCFF"
INK = "#0F172AFF"
INK2 = "#475569FF"
INK3 = "#94A3B8FF"
LINE = "#CBD5E1FF"
ORANGE = "#EA580CFF"
GREEN = "#16A34AFF"

TASK = {"wave": "07", "id": "W-26-1004-073", "picker": "陈桐",
        "zone": "华东三仓 E3", "done": 23, "total": 41}

LEVELS = [
    (1, "A-03-02", "下层 · 地面", 604, 118,
     "ELEVATION_1", "整托 · 12 箱已开"),
    (2, "B-12-01", "中层 · 第 2 层", 548, 118,
     "ELEVATION_4", "当前所在层"),
    (3, "C-07-03", "上层 · 需梯具", 492, 118,
     "ELEVATION_8", "最后 2 箱"),
]

SKU = {"name": "陶瓷马克杯 350 ml 米白", "code": "SKU-88214-MW",
       "loc": "B-12-01 中层", "need": 6, "picked": 2,
       "batch": "LOT-2608-14", "unit": "箱"}

CANDIDATES = [
    ("B-12-01", "中层", "陶瓷马克杯 350 ml 米白", "6 箱", True),
    ("B-12-04", "中层", "陶瓷马克杯 350 ml 墨绿", "6 箱", False),
    ("B-12-07", "中层", "玻璃奶瓶 200 ml", "4 箱", False),
    ("B-11-02", "中层", "棉麻餐巾 米色", "8 箱", False),
    ("B-11-05", "中层", "竹制托盘", "3 箱", False),
    ("B-10-09", "中层", "玻璃保鲜盒 1.2 L", "5 箱", False),
]


def probe():
    Wc, Hc = 1560, 800
    k = [W.t2("PROBE c03 · boxShadow 语法与裁剪边界", 40, 20, size=19,
              color=INK, style="BOLD", w=900, h=26),
         W.t2("浅底 + 精确白框：任何越界阴影都会立刻看出来", 40, 48, size=12,
              color=INK2, w=700, h=18)]

    def cell(col, row, label, widget, note="", w=290, h=170):
        x = 40 + col * 400
        y = 86 + row * 220
        k.append(box(x, y, w, h, color="#F1F5F9FF", radius=10,
                     border="1 SOLID #CBD5E1FF"))
        k.append(el("Positioned", {"left": x + 18, "top": y + 16,
                                   "width": w - 36, "height": h - 56},
                    [widget]))
        k.append(W.t2(label, x + 12, y + h - 38, size=11, color=INK, w=w - 24,
                      h=D.est_lines(label, 11, w - 24) * 16))
        if note:
            k.append(W.t2(note, x + 12, y + h - 19, size=10, color=INK3,
                          w=w - 24, h=13))

    BASE = {"width": 120, "height": 66, "color": "#FFFFFFFF",
            "borderRadius": "12"}
    for i, name in enumerate(["ELEVATION_1", "ELEVATION_2", "ELEVATION_4",
                              "ELEVATION_8"]):
        cell(i, 0, name, el("Container", dict(BASE, boxShadow=name)),
             "内置层级名")
    cell(0, 1, '自定义 "4 10 22 -2 #0F172A1F"',
         el("Container", dict(BASE, boxShadow="4 10 22 -2 #0F172A1F")),
         "负 spread 让阴影收紧")
    cell(1, 1, "双色阴影（近+远）",
         el("Container", dict(BASE, boxShadow="0 2 6 0 #0F172A1F,"
                                              "0 14 34 -6 #0F172A24")),
         "逗号分隔，函数内逗号不拆")
    cell(2, 1, "彩色阴影",
         el("Container", dict(BASE, boxShadow="0 10 24 -4 #EA580C55")),
         "状态色投影")
    VP = {"width": 254, "height": 96}
    BIG = el("Container", {"width": 226, "height": 70, "color": "#FFFFFFFF",
                           "borderRadius": "10",
                           "boxShadow": "0 12 26 0 #DC262666"})
    cell(1, 2, "Stack HARD_EDGE 视口：阴影穿出视口（红晕跑到格子里）",
         el("Positioned", {"left": 0, "top": 0, **VP},
            [el("Stack", {"fit": "EXPAND", "clipBehavior": "HARD_EDGE"},
               [el("Positioned", {"left": 14, "top": 13,
                                  "width": 226, "height": 70}, [BIG])])]),
         "254x96 视口 / 226x70 卡，投影必然越界")
    cell(2, 2, "ClipRRect 视口：同一张卡，投影被切在视口边",
         el("Positioned", {"left": 0, "top": 0, **VP},
            [el("ClipRRect", {"borderRadius": "4",
                              "clipBehavior": "HARD_EDGE"},
               [el("Stack", {"fit": "EXPAND"},
                  [el("Positioned", {"left": 14, "top": 13,
                                     "width": 226, "height": 70},
                     [BIG])])])]),
         "这正是列表滚动视口需要的行为")
    cell(0, 2, "blurStyle INNER / OUTER / SOLID 三连",
         el("Stack", {"fit": "LOOSE"}, [
             box(0, 0, 78, 62, color="#FFFFFF80", radius=10,
                 shadow="0 2 9 4 #0F172A66 INNER"),
             box(104, 0, 78, 62, color="#FFFFFFFF", radius=10,
                 shadow="0 4 10 0 #0F172A22 OUTER"),
             box(208, 0, 78, 62, color="#FFFFFFFF", radius=10,
                 shadow="0 1 3 0 #0F172A22 SOLID")]))

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=BG)
    r = W.P.probe(dsl, "c03-shadow")
    print("  probe c03-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


CW, CH = 1440, 1024


def build():
    k = []
    # ---------------- rugged top bar ----------------
    k.append(box(0, 0, CW, 96, color="#0F172AFF"))
    k.append(box(0, 92, CW, 4, color=ORANGE))
    k.append(W.t2("拣选终端 · PICKER", 36, 14, size=12, color="#94A3B8FF",
                  ls=3.0, w=400, h=18, font=D.MONO))
    k.append(W.t2("华东三仓 E3", 36, 36, size=26, color="#F8FAFCFF",
                  style="BOLD", w=420, h=34))
    k.append(el("Positioned", {"left": 520, "top": 18, "width": 380,
                               "height": 26},
                [el("Text", {"color": "#F8FAFCFF", "fontSize": "18",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "任务 %s" % TASK["id"]})]))
    k.append(el("Positioned", {"left": 520, "top": 44, "width": 380,
                               "height": 22},
                [el("Text", {"color": "#94A3B8FF", "fontSize": "13",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "波次 %s · 拣货员 %s"
                                     % (TASK["wave"], TASK["picker"])})]))
    # progress block, right
    pw, ph = 300, 60
    px0, py0 = 1100, 18
    k.append(box(px0, py0, pw, ph, color="#1E293BFF", radius=12))
    k.append(box(px0 + 16, py0 + 40, pw - 32, 8, color="#334155FF", radius=4))
    k.append(box(px0 + 16, py0 + 40, (pw - 32) * TASK["done"] / float(TASK["total"]),
                 8, gradient=W.hgrad("#F97316FF", "#FB923CFF"), radius=4))
    k.append(W.t2("本波次进度", px0 + 16, py0 + 12, size=11, color="#94A3B8FF",
                  w=140, h=16))
    k.append(el("Positioned", {"left": px0 + 140, "top": py0 + 8, "width": 144,
                               "height": 26},
                [el("Text", {"color": "#FBBF24FF", "fontSize": "19",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%d / %d" % (TASK["done"],
                                                   TASK["total"])})]))

    # ---------------- left: bin hierarchy ----------------
    P1X, P1Y, P1W, P1H = 36, 124, 660, 596
    f = W.Frame(P1X, P1Y, P1W, P1H, fill=CARD, radius=18)
    f.add(f.tx("货位层级 · 影子深度 = 嵌套层数", 28, 24, size=13, color=INK,
               ls=1.6, w=520, h=19, style="BOLD"))
    f.add(f.rt("需梯具", P1W - 28, 26, size=11, color="#B45309FF", w=80, h=17,
               font=D.MONO))
    f.add(f.r(28, 56, P1W - 56, LINE, 1))
    ly = 74
    for depth, loc, sub, w, h, sh, note in LEVELS:
        indent = 28 + (depth - 1) * 28
        f.add(f.at(indent, ly, w, h, el(
            "Container",
            {"width": w, "height": h, "color": "#FFFFFFFF",
             "borderRadius": "14", "boxShadow": sh,
             "border": "2 SOLID %s" % (ORANGE if depth == 2 else LINE)},
            [el("Stack", {"fit": "EXPAND"}, [
                f.at(16, 14, 44, 44, el(
                    "Container", {"width": 44, "height": 44,
                                  "borderRadius": "12",
                                  "color": ("#FFEDD5FF" if depth == 2
                                            else "#E2E8F0FF")},
                    [el("Stack", {"fit": "EXPAND"}, [
                        f.ctr("L%d" % depth, 0, 12, 44, size=17,
                              color=(ORANGE if depth == 2 else INK2),
                              font=D.MONO)])])),
                f.tx(loc, 74, 16, size=20, color=INK, w=200, h=27,
                     font=D.MONO, style="BOLD"),
                f.tx(sub, 74, 46, size=12, color=INK3, w=240, h=18),
                f.rt(note, w - 16, 20, size=11,
                     color=(ORANGE if depth == 2 else INK3), w=180, h=17,
                     font=D.MONO)])])))
        if depth < 3:
            f.add(f.at(indent + 22, ly + h + 4, 22, 10, el(
                "Container", {"width": 22, "height": 10, "color": LINE,
                              "alignment": "CENTER"},
                [el("Text", {"text": "v", "fontSize": "9",
                             "fontFamily": D.MONO, "color": INK3})])))
        ly += h + 24
    f.add(f.tx("影子：L1 ELEVATION_1 / L2 ELEVATION_4 / L3 ELEVATION_8。"
               "列表容器 ClipRect 视口把行和阴影一起裁掉，避免滚动时出现"
               "半截投影。", 28, ly + 6, size=11, color=INK2, w=P1W - 56,
               h=D.est_lines("影子：L1 ELEVATION_1 / L2 ELEVATION_4 / "
                             "L3 ELEVATION_8。列表容器 ClipRect 视口把行和阴影"
                             "一起裁掉，避免滚动时出现半截投影。", 11,
                             P1W - 56) * 16))
    k.append(f.render())

    # ---------------- right: current task ----------------
    P2X, P2Y, P2W, P2H = 716, 124, 688, 596
    g = W.Frame(P2X, P2Y, P2W, P2H, fill=CARD, radius=18)
    g.add(g.tx("当前任务 · CURRENT", 28, 24, size=13, color=INK, ls=1.6,
               w=400, h=19, style="BOLD"))
    g.add(g.r(28, 56, P2W - 56, LINE, 1))
    # SKU card: ELEVATION_16 + a second coloured shadow so it reads as active
    barcode = el("Stack", {"fit": "LOOSE", "alignment": "CENTER"},
                 [box(i * 3.0, 0, 1.6 if i % 3 else 2.6, 20,
                      color="#0F172AFF") for i in range(24)])
    thumb = el("Container",
               {"width": 74, "height": 92, "borderRadius": "10",
                "gradientType": "LINEAR",
                "gradientColors": "#E7E5E4FF,#D6D3D1FF",
                "gradientBegin": "(0,0)", "gradientEnd": "(0.6,1)"},
               [el("Stack", {"fit": "LOOSE"},
                   [box(10, 26, 54, 26, color="#A8A29EFF", radius=4),
                    box(16, 30, 42, 18, color="#FFFFFFCC", radius=2)])])
    sku_kids = [
        g.at(20, 18, 74, 92, thumb),
        g.tx(SKU["name"], 110, 20, size=21, color=INK, w=380, h=29,
             style="BOLD"),
        g.tx(SKU["code"], 110, 54, size=12, color=INK3, w=200, h=18,
             font=D.MONO),
        g.tx("批次 %s" % SKU["batch"], 110, 76, size=12, color=INK3, w=200,
             h=18, font=D.MONO),
        g.tx("货位 %s" % SKU["loc"], 110, 98, size=13, color=ORANGE, w=220,
             h=19, font=D.MONO, style="BOLD"),
        g.rt("需 %d 箱" % SKU["need"], P2W - 56 - 18, 18, size=14, color=INK,
             w=140, h=20, font=D.MONO),
        g.rt("已拣 %d" % SKU["picked"], P2W - 56 - 18, 42, size=30, color=GREEN,
             w=140, h=38, font=D.MONO),
        g.at(20, 122, 74, 22, barcode),
    ]
    g.add(g.at(28, 74, P2W - 56, 158, el(
        "Container",
        {"width": P2W - 56, "height": 158, "color": "#FFFFFFFF",
         "borderRadius": "18",
         "boxShadow": "0 18 42 -8 #0F172A2E,0 4 10 -2 #EA580C44",
         "border": "1 SOLID #FED7AAFF"},
        [el("Stack", {"fit": "EXPAND"}, sku_kids)])))
    # big touch targets
    by = 246
    for i, (sym, fill, fg) in enumerate((("−", "#FFFFFFFF", INK),
                                         ("+", GREEN, "#FFFFFF"))):
        bx = 28 + i * 160
        g.add(g.at(bx, by, 148, 76, el(
            "Container", {"width": 148, "height": 76, "color": fill,
                          "borderRadius": "16", "boxShadow": "ELEVATION_2",
                          "border": "1 SOLID #CBD5E1FF",
                          "alignment": "CENTER"},
            [el("Text", {"text": sym, "fontSize": "40", "fontFamily": D.LATIN,
                         "color": fg})])))
    g.add(g.at(356, by, P2W - 56 - 356, 76, el(
        "Container", {"width": P2W - 56 - 356, "height": 76,
                      "borderRadius": "16", "boxShadow": "0 6 14 -2 #EA580C66",
                      "gradientType": "LINEAR",
                      "gradientColors": "#F97316FF,#EA580CFF",
                      "gradientBegin": "(0,0)", "gradientEnd": "(1,1)",
                      "alignment": "CENTER"},
        [el("Text", {"text": "扫描确认", "fontSize": "22",
                     "fontFamily": D.UI, "color": "#FFFFFF",
                     "fontStyle": "BOLD"})])))
    # scrolling candidate list inside a ClipRect viewport
    VPX, VPY, VPW, VPH = 28, 352, P2W - 56, 176
    g.add(g.tx("候选货位（可滚动 · ClipRect 视口）", VPX, VPY - 22, size=11,
               color=INK3, w=420, h=17))
    rows = []
    ry = 0
    for loc, lvl, name, qty, active in CANDIDATES:
        rows.append(el("Positioned",
                       {"left": 0, "top": ry, "width": VPW, "height": 62},
                       [el("Container",
                           {"width": VPW, "height": 62, "color": "#FFFFFFFF",
                            "borderRadius": "12",
                            "boxShadow": "ELEVATION_2",
                            "border": "2 SOLID %s" % (ORANGE if active
                                                       else "#E2E8F0FF")},
                           [el("Stack", {"fit": "EXPAND"}, [
                               g.tx(loc, 14, 8, size=15, color=INK, w=90,
                                    h=21, font=D.MONO, style="BOLD"),
                               g.tx(lvl, 14, 32, size=11, color=INK3, w=90,
                                    h=16),
                               g.tx(name, 112, 20, size=13,
                                    color=(INK if active else INK2), w=280,
                                    h=19),
                               g.rt(qty, VPW - 14, 20, size=14,
                                    color=(ORANGE if active else INK2),
                                    w=80, h=20, font=D.MONO)])])]))
        ry += 70
    g.add(g.at(VPX, VPY, VPW, VPH,
               el("ClipRect", {"clipBehavior": "HARD_EDGE"},
                  [el("Stack", {"fit": "LOOSE"}, rows)])))
    g.add(g.r(VPX, VPY + VPH + 6, VPW, LINE, 1))
    g.add(g.tx("视口高度 176 px，第 3 行之后被裁掉：行与投影同时断开，"
               "不会出现半截阴影。", VPX, VPY + VPH + 16, size=11,
               color=INK2, w=VPW,
               h=D.est_lines("视口高度 176 px，第 3 行之后被裁掉：行与投影同时"
                             "断开，不会出现半截阴影。", 11, VPW) * 16))
    k.append(g.render())

    # ---------------- bottom: wave board ----------------
    BX, BY, BW, BH = 36, 744, 1368, 244
    b = W.Frame(BX, BY, BW, BH, fill=CARD, radius=18)
    b.add(b.tx("波次 %s · 作业板" % TASK["wave"], 28, 22, size=13, color=INK,
               ls=1.6, w=400, h=19, style="BOLD"))
    b.add(b.r(28, 52, BW - 56, LINE, 1))
    STOPS = ["接单", "上架", "拣货", "复核", "打包", "出库"]
    sw = (BW - 56) / 6.0
    for i, s in enumerate(STOPS):
        sx = 28 + i * sw
        done = i < 3
        b.add(b.at(sx, 70, sw - 14, 92, el(
            "Container",
            {"width": sw - 14, "height": 92,
             "color": "#FFFFFFFF", "borderRadius": "12",
             "boxShadow": ("ELEVATION_4" if done else "ELEVATION_1"),
             "border": "1 SOLID #E2E8F0FF"},
            [el("Stack", {"fit": "EXPAND"}, [
                b.ctr("0%d" % (i + 1), 0, 12, sw - 14, size=11,
                      color=INK3, font=D.MONO),
                b.ctr(s, 0, 34, sw - 14, size=17,
                      color=(INK if done else INK3), style="BOLD"),
                b.ctr("完成" if done else "待开始", 0, 62, sw - 14, size=11,
                      color=(GREEN if done else INK3))])])))
        if i < 5:
            b.add(b.at(sx + sw - 12, 112, 10, 8,
                       el("Container", {"width": 10, "height": 8,
                                        "color": "#CBD5E1FF"})))
    b.add(b.tx("影子图例", 28, 180, size=11, color=INK3, ls=2.0, w=140, h=17,
               font=D.MONO))
    LEG = [("ELEVATION_1", "列表行"), ("ELEVATION_4", "当前层"),
           ("ELEVATION_16", "作业卡"), ("0 6 14 -2 #EA580C66", "主按钮投影")]
    lx = 130
    for sh, name in LEG:
        b.add(b.at(lx, 178, 54, 34, el(
            "Container", {"width": 54, "height": 34, "color": "#FFFFFFFF",
                          "borderRadius": "8", "boxShadow": sh})))
        b.add(b.tx(name, lx + 64, 186, size=12, color=INK2, w=140, h=18))
        lx += 230
    b.add(b.rt("阴影是这台的唯一层级语言：抬得越高 = 离手越近 = 越先做。",
               BW - 28, 186, size=12, color=INK2, w=460, h=18))
    k.append(b.render())

    k.append(W.t2("演示数据：仓、单号、SKU、批次、波次进度均为自拟；层级阴影"
                  "是真实界面里常见的信息编码，不是装饰。", 36, 1000,
                  size=11, color=INK3, w=1100, h=17))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.render_final(dsl, "case-03", "final")
    print("  case-03", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-03 stage 1: capability probe")
    probe()
    print("== case-03 stage 2: work")
    build()