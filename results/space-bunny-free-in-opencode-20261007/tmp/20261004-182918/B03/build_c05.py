"""B03 case-05 · 三种取景 · 海洋浮标观测卡.

Primary capability under test: the clip family.
  ClipRect / ClipOval / ClipRRect, their clipBehavior values
  (NONE / HARD_EDGE / ANTI_ALIAS / ANTI_ALIAS_WITH_SAVE_LAYER), per-corner
  radii on ClipRRect, radius clamping, nested clips, and — measured, not
  assumed — whether `shape="CIRCLE"` clips children (it does not) and whether
  a `ClipPath` tag exists (it does not).

Scene: a coastal monitoring buoy publishes the same 24-hour wave-energy
spectrum three ways: a full-width panorama, a circular porthole magnifier, and
a rounded card. The spectrum itself is a real dispersion model computed in
Python, so all three views show the same numbers.

Stage 1 = dedicated capability probe, stage 2 = the work.
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

BG = "#06121CFF"
PANEL = "#0E2233FF"
INK = "#EAF6FF FF".replace(" ", "")
INK = "#EAF6FFFF"
INK2 = "#8FB6CEFF"
INK3 = "#5C8299FF"
AMBER = "#FCD34DFF"

BUOY = {"id": "屿东 07", "en": "YUDONG-07", "pos": "24.31°N 119.84°E",
        "time": "2026-10-05 09:45 UTC+8", "status": "ONLINE 8/8",
        "hs": 1.62, "tp": 7.4, "dir": "SE 128°", "sst": 27.4, "at": 1012.8}

NT, NF = 24, 10


def energy(t, f):
    """Dispersion-ish spectrum: a Gaussian peak whose frequency drifts with
    the tide, modulated by the group envelope."""
    fp = 0.17 + 0.035 * math.sin(2 * math.pi * (t - 3.0) / 12.4206)
    g = math.exp(-((f - fp) ** 2) / (2 * 0.085 ** 2))
    tail = 0.22 * math.exp(-((f - fp * 2.35) ** 2) / (2 * 0.06 ** 2))
    env = 0.55 + 0.45 * math.sin(2 * math.pi * (t - 1.5) / 12.4206 + 0.6)
    return max(0.0, min(1.0, (g + tail) * env))


RAMP = [(0.00, (8, 24, 38)), (0.28, (14, 68, 122)), (0.52, (26, 148, 178)),
        (0.72, (124, 214, 178)), (0.88, (250, 214, 120)), (1.00, (252, 138, 96))]


def cmap(v):
    v = max(0.0, min(1.0, v))
    for i in range(len(RAMP) - 1):
        a, ca = RAMP[i]
        b, cb = RAMP[i + 1]
        if a <= v <= b:
            u = (v - a) / (b - a)
            return "#%02X%02X%02XFF" % tuple(
                int(round(ca[j] + (cb[j] - ca[j]) * u)) for j in range(3))
    return "#FC8A60FF"


FMAX = 0.60


def grid_kids(x0, y0, gw, gh, t0=0.0, t1=24.0, f0=0.0, f1=FMAX, gap=0.0,
              nt=NT, nf=NF):
    cw, ch = gw / float(nt), gh / float(nf)
    out = []
    for j in range(nf):
        f = f0 + (f1 - f0) * (j + 0.5) / nf
        for i in range(nt):
            t = t0 + (t1 - t0) * (i + 0.5) / nt
            out.append(box(x0 + i * cw + gap, y0 + j * ch + gap,
                           max(0.5, cw - 2 * gap), max(0.5, ch - 2 * gap),
                           color=cmap(energy(t, f))))
    return out


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1360, 1000
    k = [W.t2("PROBE c05 · 裁剪能力边界", 40, 20, size=19, color=INK,
              style="BOLD", w=800, h=26),
         W.t2("每格内是一个故意超出边界的子节点；边界画成红框", 40, 48,
              size=12, color=INK2, w=800, h=18)]

    def cell(col, row, label, widget, note="", w=300, h=190):
        x = 40 + col * 330
        y = 84 + row * 236
        k.append(box(x, y, w, h, color="#FFFFFF08", radius=10,
                     border="1 SOLID #FFFFFF18"))
        k.append(el("Positioned", {"left": x + 12, "top": y + 12,
                                   "width": w - 24, "height": h - 52},
                    [widget]))
        k.append(box(x + 12, y + 12, w - 24, h - 52, color=None,
                     border="1 SOLID #FF4D6D88"))
        k.append(W.t2(label, x + 12, y + h - 38, size=11, color=INK, w=w - 24,
                      h=D.est_lines(label, 11, w - 24) * 16))
        if note:
            k.append(W.t2(note, x + 12, y + h - 19, size=10, color=INK3,
                          w=w - 24, h=13))

    BIG = lambda c: el("Container", {"width": 460, "height": 300,
                                     "color": c})
    cell(0, 0, "A 无裁剪（基线）",
         el("Stack", {"fit": "LOOSE"}, [BIG("#2DD4BFFF")]),
         "子节点 460x300 全部画出")
    cell(1, 0, "B Container shape=CIRCLE 不裁子节点",
         el("Container", {"width": 276, "height": 138, "shape": "CIRCLE",
                          "color": "#2DD4BFFF"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "shape 只影响自身装饰，不裁子树")
    cell(2, 0, "C ClipOval 真实裁剪",
         el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "圆形裁剪")
    cell(3, 0, "D ClipRect HARD_EDGE",
         el("ClipRect", {"clipBehavior": "HARD_EDGE"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "像素对齐，无抗锯齿")
    cell(0, 1, "E ClipRect ANTI_ALIAS（边缘锯齿对比）",
         el("ClipRect", {"clipBehavior": "ANTI_ALIAS"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "半透明边缘")
    cell(1, 1, "F ClipRect ANTI_ALIAS_WITH_SAVE_LAYER",
         el("ClipRect", {"clipBehavior": "ANTI_ALIAS_WITH_SAVE_LAYER"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "离屏缓存后再裁")
    cell(2, 1, "G ClipRRect 四角独立圆角",
         el("ClipRRect", {"borderRadiusTopLeft": "70",
                          "borderRadiusBottomRight": "70",
                          "clipBehavior": "ANTI_ALIAS"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "与 Container 圆角格式一致")
    cell(3, 1, "H ClipRRect r=400（远超半高）",
         el("ClipRRect", {"borderRadius": "400",
                          "clipBehavior": "ANTI_ALIAS"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "自动钳制为胶囊")
    cell(0, 2, "I 嵌套 ClipOval > ClipRRect",
         el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
            [el("ClipRRect", {"borderRadius": "26",
                              "clipBehavior": "ANTI_ALIAS"},
               [el("Stack", {"fit": "LOOSE"},
                   [el("Container", {"width": 460, "height": 300,
                                     "color": "#F43F5EFF"}),
                    el("Positioned", {"left": 40, "top": 40, "width": 120,
                                      "height": 60},
                       [el("Container", {"width": 120, "height": 60,
                                         "color": "#FDE047FF",
                                         "borderRadius": "10"})])])])]),
         "两层裁剪相乘")
    cell(1, 2, "J 裁剪会吃掉子节点投影",
         el("ClipRect", {"clipBehavior": "HARD_EDGE"},
            [el("Stack", {"fit": "LOOSE"},
               [box(30, 20, 180, 90, color="#FFFFFFFF", radius=10,
                    shadow="0 12 24 0 #F43F5EFF")])]),
         "红框外没有阴影 = 被裁")
    cell(2, 2, "K Stack HARD_EDGE 不吃投影",
         el("Stack", {"fit": "LOOSE", "clipBehavior": "HARD_EDGE"},
            [box(30, 20, 180, 90, color="#FFFFFFFF", radius=10,
                 shadow="0 12 24 0 #F43F5EFF")]),
         "同一张卡，阴影穿出")
    cell(3, 2, "L clipBehavior=NONE 等于不裁",
         el("ClipRect", {"clipBehavior": "NONE"},
            [el("Stack", {"fit": "LOOSE"}, [BIG("#F43F5EFF")])]),
         "显式写 NONE 与不写等价于裁剪关闭")

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=BG)
    r = W.P.probe(dsl, "c05-clip")
    print("  probe c05-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()

    # M: prove ClipPath is NOT a registered tag (separate canvas so the 400
    # cannot hide the other readings)
    d2 = ('<Snapshot type="png" background="%s"><Container width="300" '
          'height="160"><Stack fit="LOOSE">'
          '<ClipPath><Container width="400" height="300" color="#FF0000FF" />'
          '</ClipPath></Stack></Container></Snapshot>' % BG)
    r2 = W.P.probe(d2, "c05-clippath-missing")
    print("  probe c05-2 ClipPath ->", r2.get("ok"), r2.get("status"),
          (r2.get("error") or "")[:150])
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1600, 1060
PW, PY, PH = 496, 116, 500
XS = [40, 552, 1064]


def build():
    k = []
    k.append(box(0, 0, CW, 92, color="#081826FF"))
    k.append(W.rule(0, 91, CW, "#1B3purpose".replace("purpose", "648") + "FF",
                    1))
    k.append(W.t2("屿东 07 · 海洋浮标观测卡", 40, 14, size=24, color=INK,
                  style="BOLD", w=460, h=32))
    k.append(W.t2("YUDONG-07 / WAVE ENERGY SPECTRUM", 42, 48, size=11,
                  color=INK3, ls=3.0, w=560, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 820, "top": 14, "width": 740,
                               "height": 28},
                [el("Text", {"color": INK, "fontSize": "18",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s  ·  %s" % (BUOY["id"], BUOY["pos"])})]))
    k.append(el("Positioned", {"left": 820, "top": 44, "width": 740,
                               "height": 22},
                [el("Text", {"color": INK2, "fontSize": "13",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s  ·  %s" % (BUOY["time"],
                                                     BUOY["status"])})]))

    # ---------- 1. panorama, hard clipped ----------
    p1 = W.frame(XS[0], PY, PW, PH)
    p1.add(p1.tx("① 全景 · ClipRect", 24, 20, size=13, color=INK, ls=1.4,
                 w=300, h=19, style="BOLD"))
    p1.add(p1.rt("24 h × 10 频段", PW - 24, 22, size=11, color=INK3, w=180,
                 h=17, font=D.MONO))
    p1.add(p1.r(24, 50, PW - 48, "#1B3648FF", 1))
    GX, GY, GW, GH = 52, 76, 420, 300
    pan = grid_kids(GX, GY, GW, GH)
    for j in range(NF):
        p1.add(p1.rt("%.2f" % (FMAX * (NF - j - 0.5) / NF), GX - 8,
                     GY + j * (GH / NF) + 8, size=9, color=INK3, w=42, h=13,
                     font=D.MONO))
    for i in range(0, NT, 3):
        p1.add(p1.ctr("%02d" % i, GX + i * (GW / NT) - 16,
                      GY + GH + 6, 32, size=9, color=INK3, font=D.MONO))
    p1.add(p1.tx("时/h", GX - 44, GY + GH + 6, size=9, color=INK3, w=40, h=13))
    p1.add(p1.at(24, 66, PW - 48, 350,
                 el("ClipRect", {"clipBehavior": "HARD_EDGE"},
                    [el("Stack", {"fit": "LOOSE"}, pan)])))
    ry = 428
    for lab, val, col in (("Hs", "%.2f m" % BUOY["hs"], INK),
                          ("Tp", "%.1f s" % BUOY["tp"], INK),
                          ("浪向", BUOY["dir"], INK2)):
        p1.add(p1.tx(lab, 24, ry, size=11, color=INK3, w=70, h=17))
        p1.add(p1.rt(val, PW - 24, ry - 1, size=14, color=col, w=140, h=20,
                     font=D.MONO))
        ry += 22
    k.append(p1.render())

    # ---------- 2. circular porthole ----------
    p2 = W.frame(XS[1], PY, PW, PH)
    p2.add(p2.tx("② 圆形镜头 · ClipOval", 24, 20, size=13, color=INK, ls=1.4,
                 w=320, h=19, style="BOLD"))
    p2.add(p2.rt("放大 2.1× · 15:24–18:36", PW - 24, 22, size=11, color=INK3,
                 w=220, h=17, font=D.MONO))
    p2.add(p2.r(24, 50, PW - 48, "#1B3648FF", 1))
    D_ = 330
    cx, cy = PW / 2.0, 66 + D_ / 2.0
    zoom = grid_kids(cx - D_ / 2.0, cy - D_ / 2.0, D_, D_,
                     t0=15.4, t1=18.6, f0=0.08, f1=0.34, gap=0.8,
                     nt=32, nf=26)
    p2.add(p2.at(cx - D_ / 2.0, cy - D_ / 2.0, D_, D_,
                 el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
                    [el("Stack", {"fit": "LOOSE"}, zoom)])))
    p2.add(p2.at(cx - D_ / 2.0, cy - D_ / 2.0, D_, D_,
                 el("Container", {"width": D_, "height": D_,
                                  "shape": "CIRCLE", "color": None,
                                  "border": "3 SOLID #7DD3FC88"})))
    p2.add(p2.ctr("频段 0.08 – 0.34 Hz", 0, 66 + D_ + 6, PW, size=11,
                  color=INK2))
    p2.add(p2.ctr("主峰随潮周期漂移：fp(t) = 0.17 + 0.035·sin(2π(t−3)/12.42)",
                  0, 66 + D_ + 26, PW, size=10, color=INK3, font=D.MONO))
    ry = 428
    for lab, val, col in (("峰频", "0.19 Hz", INK), ("峰周期", "5.3 s", INK),
                          ("谱宽", "0.085 Hz", INK2)):
        p2.add(p2.tx(lab, 24, ry, size=11, color=INK3, w=70, h=17))
        p2.add(p2.rt(val, PW - 24, ry - 1, size=14, color=col, w=140, h=20,
                     font=D.MONO))
        ry += 22
    k.append(p2.render())

    # ---------- 3. rounded card + behaviour strip ----------
    p3 = W.frame(XS[2], PY, PW, PH)
    p3.add(p3.tx("③ 圆角卡 · ClipRRect", 24, 20, size=13, color=INK, ls=1.4,
                 w=320, h=19, style="BOLD"))
    p3.add(p3.rt("对角大圆角 + 内嵌缩略图", PW - 24, 22, size=11, color=INK3,
                 w=240, h=17))
    p3.add(p3.r(24, 50, PW - 48, "#1B3648FF", 1))
    RW, RH = PW - 48, 210
    mini = grid_kids(16, 16, RW - 32, RH - 44, gap=0.4)
    p3.add(p3.at(24, 66, RW, RH,
                 el("ClipRRect", {"borderRadiusTopLeft": "64",
                                  "borderRadiusBottomRight": "64",
                                  "clipBehavior": "ANTI_ALIAS"},
                    [el("Stack", {"fit": "LOOSE"}, mini)])))
    p3.add(p3.at(300, 78, 156, 100,
                 el("ClipRRect", {"borderRadius": "12",
                                  "clipBehavior": "ANTI_ALIAS"},
                    [el("Stack", {"fit": "LOOSE"},
                        grid_kids(0, 0, 156, 100, t0=15.4, t1=18.6,
                                  f0=0.08, f1=0.34, gap=0.0,
                                  nt=18, nf=12))])))
    p3.add(p3.at(300, 78, 156, 100,
                 el("Container", {"width": 156, "height": 100, "color": None,
                                  "borderRadius": "12",
                                  "border": "1 SOLID #FFFFFF55"})))
    CAP3 = ("卡内右上角是第二层 ClipRRect 缩略图（15:24–18:36 / 0.08–0.34 Hz）。"
            "两层裁剪相乘：内层圆角先裁，外层对角圆角再裁。")
    p3.add(p3.tx(CAP3, 24, 288, size=11, color=INK2, w=PW - 48,
                 h=D.est_lines(CAP3, 11, PW - 48) * 16))
    ry = 334
    p3.add(p3.tx("clipBehavior 对同一圆角的边缘", 24, ry, size=11,
                 color=INK3, w=300, h=17))
    for j, (cb, note) in enumerate((("ANTI_ALIAS", "边缘半像素过渡"),
                                    ("HARD_EDGE", "像素对齐无过渡"),
                                    ("ANTI_ALIAS_WITH_SAVE_LAYER", "离屏缓存后裁"),
                                    ("NONE", "完全不裁"))):
        bxx = 24 + j * 114
        p3.add(p3.at(bxx, ry + 24, 100, 74,
                     el("ClipRRect",
                        {"borderRadius": "26", "clipBehavior": cb},
                        [el("Stack", {"fit": "LOOSE"},
                            [el("Container", {"width": 200, "height": 150,
                                              "color": "#F43F5EFF"})])])))
        p3.add(p3.at(bxx, ry + 24, 100, 74,
                     el("Container", {"width": 100, "height": 74,
                                      "color": None, "borderRadius": "26",
                                      "border": "1 SOLID #FFFFFF33"})))
        p3.add(p3.ctr(cb.replace("ANTI_ALIAS_WITH_SAVE_LAYER", "SAVE_LAYER"), bxx, ry + 104, 100, size=9, color=INK2,
                      font=D.MONO))
        p3.add(p3.ctr(note, bxx, ry + 119, 100, size=9, color=INK3))
    p3.add(p3.tx("表层水温 27.4 ℃ · 气压 1012.8 hPa · 缩略图窗口 15:24–18:36",
                 24, 478, size=10, color=INK3, w=PW - 48, h=15))
    k.append(p3.render())

    # ---------- bottom: honest limits ----------
    BX, BY, BW, BH = 40, 636, 1520, 372
    b = W.frame(BX, BY, BW, BH)
    b.add(b.tx("裁剪能做什么 / 不能做什么", 28, 20, size=13, color=INK,
               ls=1.4, w=460, h=19, style="BOLD"))
    b.add(b.r(28, 50, BW - 56, "#1B3648FF", 1))
    LIM = [
        ("ClipOval", "椭圆 / 圆形裁剪，只有这一个形状可选（连 `shape=\"OVAL\"` "
                     "都注册不了，只有 CIRCLE）。"),
        ("ClipRect", "轴对齐矩形；`clipBehavior` 四档实测都能用。"),
        ("ClipRRect", "圆角矩形，四角可独立取值，半径超过半边长自动钳制。"),
        ("shape=\"CIRCLE\"", "只改变「自身」的装饰形状，「不裁剪子节点」——"
                             "探针 B 里 460×300 的红块照样溢出。"),
        ("ClipPath", "解析器注册表里「没有」这个标签（38 个标签中只有 "
                     "ClipRect / ClipOval / ClipRRect）。想要任意形状的裁剪，"
                     "只能用这三个之一近似。"),
        ("裁剪与投影", "Clip* 会把子节点的 boxShadow 一起裁掉（探针 J）；"
                       "Stack 自己的 clipBehavior 不会（探针 K）。"),
    ]
    for i, (name, txt) in enumerate(LIM):
        col, row = i % 2, i // 2
        nx = 28 + col * 736
        ny = 68 + row * 62
        b.add(b.ab(nx, ny, 10, 10, color="#7DD3FCFF", radius=2))
        b.add(b.tx(name, nx + 20, ny - 2, size=12, color=AMBER, w=200, h=18,
                   font=D.MONO))
        b.add(b.tx(txt, nx + 20, ny + 18, size=11, color=INK2, w=680,
                   h=D.est_lines(txt, 11, 680) * 16))
    # colour ramp legend
    lx, ly, lwid = 28, 268, 700
    b.add(b.tx("能量色标", lx, ly - 20, size=11, color=INK3, w=120, h=17))
    for i in range(60):
        b.add(b.ab(lx + i * (lwid / 60.0), ly, lwid / 60.0 - 0.6, 16,
                   color=cmap(i / 59.0)))
    b.add(b.tx("0", lx, ly + 20, size=9, color=INK3, w=30, h=13,
               font=D.MONO))
    b.add(b.rt("E(f,t) 归一化 1.00", lx + lwid, ly + 20, size=9, color=INK3,
               w=180, h=13, font=D.MONO))
    b.add(b.rt("频段轴向上为低频", lx + lwid + 190, ly - 20, size=11,
               color=INK3, w=200, h=17))
    b.add(b.tx("浮标编号、站位、时次与所有观测量均为演示用虚构值；谱型由"
               "E(f,t)=[exp(−(f−fp)²/2σ²)+0.22·exp(−(f−2.35fp)²/2σ₂²)]·"
               "(0.55+0.45·sin(2π(t−1.5)/12.42+0.6)) 计算，三种取景共用"
               "同一函数，所以三张图的数值必然一致。", 28, 306, size=11,
               color=INK3, w=BW - 56,
               h=D.est_lines("浮标编号、站位、时次与所有观测量均为演示用虚构值；"
                             "谱型由 E(f,t)=[exp(−(f−fp)²/2σ²)+0.22·exp(−"
                             "(f−2.35fp)²/2σ₂²)]·(0.55+0.45·sin(2π(t−1.5)/"
                             "12.42+0.6)) 计算，三种取景共用同一函数，所以三张图"
                             "的数值必然一致。", 11, BW - 56) * 16))
    k.append(b.render())

    k.append(W.t2("Snapshot DSL 里没有路径、没有布尔运算、没有遮罩：所有"
                  "「取景」只能靠 ClipRect / ClipOval / ClipRRect 三种裁剪"
                  "近似，这是本件作品的边界。", 40, 1024, size=11,
                  color=INK3, w=1400, h=17))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.render_final(dsl, "case-05", "final")
    print("  case-05", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-05 stage 1: capability probe")
    probe()
    print("== case-05 stage 2: work")
    build()