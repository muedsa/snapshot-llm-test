"""B06 能力探针：把十件将用到、但 B05 没用过的新图元各画一份，真实渲染后看图判断。

探针目标（逐个在 case.md/notes 里记结论）：
 A ClipRect 硬边裁剪          B ClipOval 椭圆裁剪
 C half_disc（含负 top 的 Positioned）  D pie_ring 圆环扇区逼近
 E clock_ticks 24 h 刻度       F step_fn 阶梯
 G waterfall 价格瀑布          H cube_stack 方糖堆
 I diverging_bar 发散条        J punch_card 打孔卡
 K matrix（Transform 16 值列主序，旋转＋斜切＋平移）
 L BackdropFilter 毛玻璃浮层（若不可用则记为不可用）
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import b06kit as K  # noqa: E402

W, H = 1500, 1560


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    K.tlab(d, tf, "p-title", 40, 26, 900, 46, "B06 图元探针（只用于能力判断，不进交付）",
           30, P["t0"])
    K.tlab(d, tf, "p-sub", 40, 74, 1100, 26,
           "12 项各画一份：绿框＝渲染正常，红框＝失败或走样，结论记在 case.md", 15, P["t2"])

    cells = [
        (40, 120, "A ClipRect"), (400, 120, "B ClipOval"), (760, 120, "C half_disc"),
        (1120, 120, "D pie_ring"),
        (40, 420, "E clock_ticks"), (400, 420, "F step_fn"), (760, 420, "G waterfall"),
        (1120, 420, "H cube_stack"),
        (40, 720, "I diverging_bar"), (400, 720, "J punch_card"),
        (760, 720, "K matrix"), (1120, 720, "L backdrop"),
    ]
    for cx, cy, lab in cells:
        K.outline_rect(d, cx, cy, 320, 260, P["axis"], radius=12, thick=2)
        K.tlab(d, tf, "lab-" + lab[:1], cx + 12, cy + 10, 296, 24, lab, 15, P["t1"])

    # A ClipRect：把一条超宽的进度条裁进 280 宽窗口
    inner = d.box(560, 40, color=P["teal"], radius=20)
    K.clip_rect(d, 60, 190, 280, 40, K.pos_raw(0, 0, 560, 40, inner))
    d.pos(60, 240, 280, 22, d.box(280, 22,
          inner=d.text("窗口 280，内容 560", P["t2"], 14, align="CENTER")))

    # B ClipOval：方块裁成圆
    K.clip_oval(d, 420, 170, 280, 200,
                '<Positioned left="0" top="0" width="280" height="200">%s</Positioned>'
                % d.box(280, 200, color=P["gold"]))
    # C half_disc（内部含负 top）
    K.half_disc(d, 780, 190, 260, 130, P["grass"], side="top", mask=K.BASE)
    K.half_disc(d, 780, 330, 200, 100, P["teal"], side="bottom", mask=K.BASE)
    # D pie_ring
    K.pie_ring(d, 1280, 250, 96, 58, -90, 40, P["teal"])
    K.pie_ring(d, 1280, 250, 96, 58, 40, 130, P["coral"])
    K.pie_ring(d, 1280, 250, 96, 58, 130, 240, P["gold"])

    # E clock_ticks
    K.clock_ticks(d, 200, 570, 104, 78, every=15, major_every=60)
    # F step_fn
    K.step_fn(d, tf, "f", 430, 500, 260, 150,
              [(0.15, 0.0, "免费"), (0.35, 0.35, "首时"), (0.5, 1.0, "之后")], P["teal"])
    # G waterfall
    K.waterfall(d, tf, "g", 790, 480, 280,
                [("小计", 30.0, 30.0), ("满减", -8.0, 22.0), ("包装", 2.5, 24.5),
                 ("配送", 1.9, 26.4)], P["teal"], P["coral"], row_h=44, gap=6, size=14)
    # H cube_stack
    K.cube_stack(d, tf, "h", 1150, 660, 9, cube=24, gap=4, per_row=4,
                 color=P["card2"], edge=P["teal"])

    # I diverging_bar
    for i, v in enumerate([1.4, -0.9, 2.2, 0.4, -1.8]):
        K.diverging_bar(d, tf, "i%d" % i, 60, 790 + i * 34, 240, 0.5, v * 0.2, 20,
                        P["gold"], P["coral"], radius=6)
    # J punch_card
    K.punch_card(d, tf, "j", 420, 700, 260, 200, r=11, color=P["border"])
    # K matrix：旋转 + 斜切 + 平移
    K.matrix(d, 800, 780, 240, 120, d.box(240, 120, color=P["violet"], radius=8),
             rot=-12, sx=1.0, sy=1.0, tx=0, ty=0)
    K.matrix(d, 800, 940, 240, 60, d.box(240, 60, color=P["cyan"], radius=6),
             rot=0, sx=1.0, sy=1.0, kx=0.35, tx=-30, ty=0)
    # L BackdropFilter
    d.pos(1140, 760, 280, 180, d.box(280, 180, color=P["panel2"], radius=14,
          grad=None, inner=d.text("底：色块", P["t0"], 16, align="CENTER")))
    d.parts.append(
        '<Positioned left="1170" top="820" width="220" height="110">'
        '<ClipRect clipBehavior="HARD_EDGE">'
        '<BackdropFilter sigmaX="18" sigmaY="18">'
        '<Container width="220" height="110" color="#39C2C033">'
        '<Text value="毛玻璃?" fontInterceptors="[]" fontSize="16" color="#E9EEF1"'
        ' textAlign="CENTER"/></Container></BackdropFilter></ClipRect></Positioned>')

    K.credit(d, tf, "credit", 40, 1010, 1400, [
        "探针目的：确认真实渲染是否支持 ClipRect / ClipOval / half_disc 负偏移 / pie_ring /",
        "clock_ticks / step_fn / waterfall / cube_stack / diverging_bar / punch_card /",
        "Transform matrix（列主序 16 Float，alignment=TOP_LEFT）/ BackdropFilter＋ClipRect 组合。",
        "曲线与扇形仍为图元逼近，交付件内需注明；本探针 PNG 只存 tmp，不进 outputs 交付清单。",
    ])
    info = {"kind": "capability-probe", "cells": 12,
            "canvas": [W, H], "uses": ["ClipRect", "ClipOval", "half_disc", "pie_ring",
                                       "clock_ticks", "step_fn", "waterfall", "cube_stack",
                                       "diverging_bar", "punch_card", "Transform matrix",
                                       "BackdropFilter"]}
    return d, tf, info
