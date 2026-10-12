"""件-06 现场围挡与交通导改图（1600×1200，作业前说明图）。

内容任务：让班组长在开工前 30 分钟照图布设——边界在哪、占哪条道、锥怎么摆、
人站在哪里、行人和公交怎么绕。这是一张"给干活的人看的图"，不是宣传示意图。
比例：平面 1 m ≈ 5 px；剖面纵向 1 m ≈ 12 px（为看清围挡与支撑而放大）。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1600, 1200
S = 5.0          # 平面：每米像素
SV = 12.0        # 剖面：纵向每米像素


def build():
    st = B.data()
    f = st["featured"]["tree"]
    wo = json.load(open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
                        encoding="utf-8"))
    order = [o for o in wo["orders"] if o["tree"] == f["id"]][0]
    fr = f["height_m"] + 6.0                      # 禁入半径 m
    r = fr * S
    circ = 2 * math.pi * fr
    hard, tape = round(circ / 3), round(circ * 2 / 3)

    d, tf = B.doc(W, H, ground="light")
    MX = 64
    # ---- 标题 ----
    B.tlab(d, tf, "h-t", MX, 36, 1000, 50, "现场布置：围挡、导改与人员站位", 34,
           d.P["t0"], style="BOLD")
    B.tlab(d, tf, "h-s", MX, 88, 1100, 28,
           "%s ｜ %s 126 号门前 ｜ 开工前 30 分钟按本图布设 ｜ 平面 1 m ≈ 5 px"
           % (f["id"], f["road"]), 18, d.P["t2"])
    B.chip(d, tf, "h-state", W - MX - 300, 44, 300, 46, "作业前 · 未布设",
           "#FFFFFF", B.AMBER, size=18)

    # ---- 平面 ----
    py0 = 138
    B.panel(d, MX, py0, W - 2 * MX, 486, "#FFFDF8", radius=14,
            border="1 SOLID " + d.P["border"])
    B.tlab(d, tf, "pl-t", MX + 20, py0 + 12, 500, 28, "① 平面", 20, d.P["t1"],
           style="BOLD")
    bx, bw = MX + 20, W - 2 * MX - 40
    # 带：建筑退界 / 人行道 / 车行道（上下行）/ 人行道
    d.rect(bx, py0 + 52, bw, 62, "#EFE9DC")
    B.tlab(d, tf, "z-b", bx + 8, py0 + 66, 260, 26, "沿街建筑退界", 15, d.P["t2"])
    d.rect(bx, py0 + 114, bw, 74, "#F7F3EA")
    d.rect(bx, py0 + 114, bw, 3, d.P["line"])
    B.tlab(d, tf, "z-s", bx + 8, py0 + 132, 260, 26, "人行道（宽 3.2 m）", 15, d.P["t2"])
    d.rect(bx, py0 + 188, bw, 82, "#E9E2D4")
    d.rect(bx, py0 + 270, bw, 82, "#E9E2D4")
    d.rect(bx, py0 + 268, bw, 4, "#FFFDF8")
    for i in range(12):
        d.rect(bx + 14 + i * 64, py0 + 266, 36, 8, "#FFFFFF")
    B.tlab(d, tf, "z-r", bx + 8, py0 + 214, 300, 26, "车行道 · 近侧车道", 15, d.P["t2"])
    B.tlab(d, tf, "z-r2", bx + 8, py0 + 296, 300, 26, "车行道 · 对向车道", 15, d.P["t2"])
    d.rect(bx, py0 + 352, bw, 3, d.P["line"])
    d.rect(bx, py0 + 355, bw, 62, "#F7F3EA")
    B.tlab(d, tf, "z-s2", bx + 8, py0 + 372, 260, 26, "对侧人行道", 15, d.P["t2"])
    # 树与禁入圆
    cx, cy = bx + 700, py0 + 150
    B.disc(d, cx, cy, r, "#FBECE8")
    B.disc_outline(d, cx, cy, r, 3, B.RUST)
    d.line(cx, cy, cx + r, cy, 2, B.RUST)
    B.mono(d, tf, "pl-r", cx + 16, cy - 28, 110, 26, "R %.1f m" % fr, 16, B.RUST)
    B.tree_glyph(d, cx, cy + 14, 46, 30, 8, tilt_deg=f["tilt_deg"], crown=B.LEAF,
                 trunk="#8A6440")
    B.mono(d, tf, "pl-id", cx - 300, cy - 6, 150, 26, f["id"], 15, d.P["t0"],
           align="END")
    d.line(cx - 146, cy + 7, cx - 14, cy + 10, 1, d.P["t2"])
    # 封闭段（近侧车道）：过渡 30 m / 缓冲 10 m / 作业 20 m / 下游 10 m
    segs = [("上游过渡", 30, B.AMBER), ("缓冲", 10, "#F0D9A8"),
            ("作业区", 20, B.RUST), ("下游", 10, "#F0D9A8")]
    x = cx - 2 * S - 10 * S - 20 * S          # 作业区中心对齐树
    zx = x
    for name, m, col in segs:
        w = m * S
        d.rect(zx, py0 + 190, w, 78, col, radius=2)
        zx += w
        d.rect(zx - 2, py0 + 402, 2, 26, d.P["t1"])
        B.mono(d, tf, "dm-%s" % name, zx - w, py0 + 432, w, 26,
               "%d m" % m, 15, d.P["t1"], align="CENTER")
        B.tlab(d, tf, "dl-%s" % name, zx - w, py0 + 376, w, 26, name, 15, d.P["t2"],
               align="CENTER")
    d.rect(x - 2, py0 + 402, 2, 26, d.P["t1"])
    B.tlab(d, tf, "dm-0", x - 60, py0 + 432, 58, 26, "起点", 15, d.P["t1"],
           align="END")
    # 锥：过渡区斜线 + 封闭段边界
    taper = [(x - 150 + i * 30, py0 + 268 - i * 13) for i in range(6)]
    for i, (px_, py_) in enumerate(taper):
        B.disc(d, px_, py_, 8, B.AMBER)
        B.disc(d, px_, py_, 3, "#FFFDF8")
    CONE_S = 30                                    # 间距 6 m @ 5 px/m
    n_side = 1 + 120 // CONE_S                     # 每条端部行 5 只
    for i in range(n_side):
        B.disc(d, x + i * CONE_S, py0 + 270, 8, B.AMBER)
        B.disc(d, x + i * CONE_S, py0 + 270, 3, "#FFFDF8")
    for i in range(n_side):
        B.disc(d, zx - i * CONE_S, py0 + 270, 8, B.AMBER)
        B.disc(d, zx - i * CONE_S, py0 + 270, 3, "#FFFDF8")
    cones = 6 + 2 * n_side

    # 标志牌
    for i, (sx, lab) in enumerate([(x - 260, "前方施工"), (x - 130, "车道变窄"),
                                   (zx + 30, "限速 30"), (zx + 140, "解除封闭")]):
        d.rect(sx, py0 + 296, 84, 30, d.P["teal"], radius=4)
        B.tlab(d, tf, "sg%d" % i, sx, py0 + 300, 84, 24, lab, 13, "#FFFFFF",
               align="CENTER")
    # 引导员
    for i, (gx_, lab) in enumerate([(x - 160, "引导员 A（上游）"),
                                    (zx + 6, "引导员 B（下游）")]):
        B.disc(d, gx_, py0 + 311, 11, d.P["t0"])
        B.tlab(d, tf, "fl%d" % i, gx_ - 62, py0 + 332, 148, 24, lab, 14, d.P["t1"],
               align="CENTER")
    B.tlab(d, tf, "cone-n", x - 470, py0 + 332, 240, 26,
           "交通锥 %d 只（间距 6 m）" % cones, 15, d.P["t2"])
    # 停车位取消
    for i in range(3):
        B.outline_rect(d, cx - 120 + i * 84, py0 + 192, 78, 40, B.RUST, thick=2)
        d.line(cx - 120 + i * 84, py0 + 192, cx - 42 + i * 84, py0 + 232, 2, B.RUST)
        d.line(cx - 42 + i * 84, py0 + 192, cx - 120 + i * 84, py0 + 232, 2, B.RUST)
    d.line(cx - 85, py0 + 234, cx - 85, py0 + 276, 1, B.RUST)
    d.rect(cx - 124, py0 + 276, 236, 30, "#FFFDF8", radius=6)
    B.tlab(d, tf, "pk", cx - 116, py0 + 280, 220, 24, "临时取消停车位 3 个", 15,
           B.RUST)
    # 公交站与候车线
    d.rect(cx + 260, py0 + 58, 150, 46, "#CFC7B6", radius=4)
    B.tlab(d, tf, "bs", cx + 260, py0 + 68, 150, 26, "快速公交站", 15, "#4A4436",
           align="CENTER")
    # 候车线改移：箭头按 5 px/m 画出，长度 = 18 m
    SHIFT = 18 * S
    ax0 = cx + r + 31
    d.line(ax0, py0 + 130, ax0 + SHIFT, py0 + 130, 3, d.P["teal"])
    d.line(ax0 + SHIFT, py0 + 130, ax0 + SHIFT - 12, py0 + 123, 3, d.P["teal"])
    d.line(ax0 + SHIFT, py0 + 130, ax0 + SHIFT - 12, py0 + 137, 3, d.P["teal"])
    B.tlab(d, tf, "det", ax0 + SHIFT + 14, py0 + 118, 320, 26,
           "候车线东移 18 m（箭头等比，避开禁入圆）", 15, d.P["teal"])
    # 行人绕行
    PED = 130                                      # px，左右各 130
    d.line(cx - PED, py0 + 180, cx + PED, py0 + 180, 3, d.P["leaf"])
    d.line(cx + PED, py0 + 180, cx + PED - 18, py0 + 172, 3, d.P["leaf"])
    d.line(cx + PED, py0 + 180, cx + PED - 18, py0 + 188, 3, d.P["leaf"])
    ped_m = round(2 * PED / S)
    B.tlab(d, tf, "ped", cx - 130, py0 + 148, 140, 26, "行人沿内侧绕行", 15, d.P["leaf"])
    # 比例尺
    for xx, lab in [(bx + bw - 260, "0"), (bx + bw - 210, "10"), (bx + bw - 160, "20 m")]:
        d.rect(xx, py0 + 404, 2, 14, d.P["t0"])
        B.mono(d, tf, "sc-%s" % lab, xx - 14, py0 + 422, 60, 24, lab, 14, d.P["t2"])
    d.rect(bx + bw - 260, py0 + 410, 100, 3, d.P["t0"])
    d.line(bx + bw - 80, py0 + 424, bx + bw - 80, py0 + 392, 3, d.P["t0"])
    d.line(bx + bw - 80, py0 + 392, bx + bw - 88, py0 + 406, 3, d.P["t0"])
    d.line(bx + bw - 80, py0 + 392, bx + bw - 72, py0 + 406, 3, d.P["t0"])
    B.mono(d, tf, "north", bx + bw - 70, py0 + 396, 40, 26, "N", 15, d.P["t0"])

    # ---- 剖面 ----
    SX, SW = MX, 700
    px, py, pw = B.card(d, tf, "sec", SX, 648, SW, 300)
    B.tlab(d, tf, "sec-t", px, py, 500, 28, "② 横断面（纵向放大）", 20, d.P["t1"],
           style="BOLD")
    gy = py + 244
    d.rect(px, gy, pw, 3, d.P["t1"])                    # 地面
    d.rect(px, gy - 4, pw * 0.42, 4, "#E9E2D4")         # 人行道面
    d.rect(px + pw * 0.42, gy - 4, pw * 0.58, 4, "#DCD3C4")
    tx = px + 210
    B.tree_glyph(d, tx, gy - 4, 14.2 * SV * 0.62, 52, 12, tilt_deg=f["tilt_deg"],
                 crown=B.LEAF, trunk="#8A6440")
    for off in (-1, 0, 1):
        d.line(tx, gy - 4 - 14.2 * SV * 0.62 * 0.62, tx + off * 46, gy - 6, 3,
               "#8A6440")
    for i in range(9):
        d.rect(px + 40 + i * 26, gy - 4 - 1.2 * SV, 22, 1.2 * SV, B.RUST)
    B.mono(d, tf, "sec-f", px + 40, gy - 4 - 1.2 * SV - 26, 200, 24,
           "围挡 1.2 m", 15, B.RUST)
    B.mono(d, tf, "sec-h", tx + 70, gy - 4 - 14.2 * SV * 0.62 - 6, 200, 26,
           "树高 %.1f m" % f["height_m"], 16, d.P["t1"])
    B.tlab(d, tf, "sec-b", px, gy + 12, pw, 26,
           "支撑脚距干 1.8 m ｜ 主撑朝迎风侧（东南）", 15, d.P["t2"])

    # ---- 图例与数量 ----
    LX, LW = MX + SW + 32, W - MX - (MX + SW + 32)
    px, py, pw = B.card(d, tf, "lgd", LX, 648, LW, 300)
    B.tlab(d, tf, "lgd-t", px, py, 400, 28, "③ 图例与本次用量", 20, d.P["t1"],
           style="BOLD")
    items = [(B.RUST, "禁入圆 / 硬质围挡", "%s m" % B.fmt(hard)),
             (B.AMBER, "交通锥（间距 6 m）", "%d 只" % cones),
             ("#F0D9A8", "缓冲与下游段", "警示带 %s m" % B.fmt(tape)),
             (d.P["teal"], "导向标志 / 候车线改移", "4 块"),
             (d.P["t0"], "引导员站位", "2 名"),
             (B.LEAF, "行人绕行方向（内侧）", "%d m" % ped_m),
             ("#CFC7B6", "树体支撑（三脚钢撑）", "1 套")]
    yy = py + 40
    for i, (col, lab, q) in enumerate(items):
        d.rect(px, yy + 4, 24, 18, col, radius=3)
        B.tlab(d, tf, "lg%d" % i, px + 36, yy, 380, 26, lab, 17, d.P["t1"])
        B.mono(d, tf, "lq%d" % i, px + pw - 190, yy, 190, 26, q, 17, d.P["t0"],
               align="END")
        yy += 34

    # ---- 布设顺序 ----
    px, py, pw = B.card(d, tf, "seq", MX, 972, W - 2 * MX, 152)
    B.tlab(d, tf, "seq-t", px, py, 600, 28, "④ 布设顺序（撤场按反序）", 20, d.P["t1"],
           style="BOLD")
    steps = [("T−30", "上游开双闪，摆第 1 块标志"),
             ("T−25", "沿过渡区撒锥，先上游"),
             ("T−20", "贴车位告知，挪站牌"),
             ("T−10", "围硬质围挡，留出入口"),
             ("T−0", "进圆内支撑，专人监护"),
             ("完工", "先撤围挡留锥，再撤标志")]
    sw = (pw - 5 * 12) / 6.0
    for i, (t, s) in enumerate(steps):
        x = px + i * (sw + 12)
        B.panel(d, x, py + 38, sw, 66, d.P["card2"], radius=10,
                border="1 SOLID " + d.P["border"])
        B.mono(d, tf, "sq%d-t" % i, x + 12, py + 44, 90, 24, t, 16, B.AMBER)
        B.tlab(d, tf, "sq%d-s" % i, x + 12, py + 66, sw - 24, 34, s, 14, d.P["t1"],
               lines=2, valign="TOP")
        if i < 5:
            d.line(x + sw + 2, py + 71, x + sw + 10, py + 71, 2, d.P["t2"])

    B.credit(d, tf, "foot", MX, 1140, W - 2 * MX, [
        "演示图：数据由 b05data.py（固定种子 %d）生成，汀州市 / 建设路 / 树号均为虚构。"
        "禁入半径 = 树高 + 6 m、过渡区 30 m（对应限速 40 km/h）为产品自定现场规则，不是国标。" % st["seed"],
        "本图为班组内部布设示意，不替代交通组织设计文件；占用市政道路与取消车位须经交警与"
        "公交公司会签后实施。未做真实用户验证。"], size=15)
    return d, tf, dict(case="case-06", kind="现场围挡与交通导改图（作业前）",
                       tree=f["id"], exclusion_radius_m=round(fr, 1),
                       hard_fence_m=hard, tape_m=tape, cones=cones,
                       detour_m=ped_m, shift_m=18)
