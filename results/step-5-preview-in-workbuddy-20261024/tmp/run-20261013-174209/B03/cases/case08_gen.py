#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-08 儿童自然认知 App 启动页景深插画 1080×1920（9:16）。
虚构产品「叶子 · 自然认知」3–8 岁儿童自然认知 App 启动页。
主导手法：ImageFiltered 分层景深（远景大 sigma 虚化 → 前景锐利）+
Opacity 层间雾带 + Stack 层次 + ClipPath 叶形徽标。
景深数据自洽：sigma 序列 14 → 8 → 3 → 0（四层）。
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, rect, circle, assert_canvas, WARN,
                        grad, opacity, image_filtered, clip_path,
                        INK, TEAL, PAPER, ORANGE, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER, snapshot)

W, H = 1080, 1920

# 四层景深：远→近（sigma 递减、色相渐进、雾带分隔）
LAYER_SKY = ["#BFE3F2", "#F2D9B8"]          # 晨空
LAYER_FAR = "#9FC4A8"    # 远林
LAYER_MID = "#6FA87E"    # 中林
LAYER_NEAR = "#3F7D54"   # 近草
LEAF_C = "#4E9A5F"
LEAF_D = "#2F6B41"
TRUNK = "#7A5238"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def leaf_path(w: float, h: float, n: int = 22) -> str:
    """叶形轮廓：两条对称二次贝塞尔（叶尖→叶基→叶尖），采样折线。"""
    tip = (w * 0.5, 0.0)
    base = (w * 0.5, h)
    pts = []
    for i in range(n + 1):
        t = i / n
        # 右半：P0=tip, P1=(w, h*0.30), P2=base
        x = (1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * w + t ** 2 * base[0]
        y = (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * h * 0.30 + t ** 2 * base[1]
        pts.append((x, y))
    for i in range(n, -1, -1):
        t = i / n
        x = (1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * 0.0 + t ** 2 * base[0]
        y = (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * h * 0.30 + t ** 2 * base[1]
        pts.append((x, y))
    d = "M " + " L ".join(f"{px:.2f},{py:.2f}" for px, py in pts) + " Z"
    return d


def tree_cluster(cx, base_y, r, color, n_trees=3, nodes=None):
    """一簇树冠（圆组）+ 短干。"""
    offs = [(-r * 0.95, -r * 0.1), (0, -r * 0.42), (r * 0.95, -r * 0.1)]
    out = []
    for dx, dy in offs:
        out.append(f'<Positioned left="{cx + dx - r:.2f}" top="{base_y + dy - r:.2f}" '
                   f'width="{2*r:.2f}" height="{2*r:.2f}">'
                   f'<Container width="{2*r:.2f}" height="{2*r:.2f}" '
                   f'shape="CIRCLE" color="{color}"/></Positioned>')
    tw = max(6.0, r * 0.22)
    out.append(f'<Positioned left="{cx - tw/2:.2f}" top="{base_y - r * 0.55:.2f}" '
               f'width="{tw:.2f}" height="{r * 0.8:.2f}">'
               f'<Container width="{tw:.2f}" height="{r * 0.8:.2f}" '
               f'color="{TRUNK}"/></Positioned>')
    if nodes is not None:
        nodes.extend(out)
    return "".join(out)


def blurred(x, y, w, h, children, sx, sy, nodes):
    """景深层：ImageFiltered 只接受单一子级（probe3 实证），
    多个 Positioned 先包 Stack；盒取全画布以保持画布坐标系。"""
    nodes.append(image_filtered(
        0, 0, W, H,
        f'<Stack alignment="TOP_LEFT" fit="EXPAND" '
        f'clipBehavior="NONE">{children}</Stack>', sx, sy, nodes=None))


def dsl() -> str:
    n = []

    # ================= L0 天空（无景深，清晰） =================
    n.append(grad(0, 0, W, H, LAYER_SKY, stops=[0, 0.42], gtype="LINEAR",
                  begin="TOP_CENTER", end="BOTTOM_CENTER", nodes=n))
    # 太阳 + 光晕（RADIAL）
    n.append(grad(620, 140, 420, 420, ["#FFF6D8CC", "#FFF6D800"],
                  stops=[0, 1], gtype="RADIAL", center="CENTER",
                  radius=0.5, nodes=n))
    n.append(circle(760, 250, 130, "#FFF3C4"))
    # 云（椭圆组，远景小虚化由 L1 的 sigma 覆盖本层不加）
    for cx, cy, rw, rh in [(220, 300, 130, 46), (300, 268, 90, 34),
                           (760, 430, 110, 38), (180, 520, 96, 30)]:
        n.append(f'<Positioned left="{cx - rw}" top="{cy - rh}" '
                 f'width="{2*rw}" height="{2*rh}">'
                 f'<Container width="{2*rw}" height="{2*rh}" '
                 f'shape="CIRCLE" color="#FFFFFFCC"/></Positioned>')

    # ================= L1 远景树林（sigma 14 强虚化） =================
    far_trees = "".join(tree_cluster(x, 1010, r, LAYER_FAR)
                        for x, r in [(150, 120), (390, 150), (640, 110),
                                     (790, 130), (880, 100)])
    blurred(0, 640, W, 470, far_trees, 14, 14, n)
    # 雾带 1（L0/L1 之间）
    n.append(grad(0, 600, W, 160, ["#CFE6F200", "#DCEFE6B0", "#CFE6F200"],
                  stops=[0, 0.5, 1], gtype="LINEAR", begin="TOP_CENTER",
                  end="BOTTOM_CENTER", nodes=n))

    # ================= L2 中景树林（sigma 8 中虚化） =================
    mid_trees = "".join(tree_cluster(x, 1230, r, LAYER_MID)
                        for x, r in [(260, 150), (560, 190), (760, 160)])
    blurred(0, 980, W, 420, mid_trees, 8, 8, n)
    # 雾带 2
    n.append(grad(0, 960, W, 150, ["#D8EBDC00", "#D8EBDCA0", "#D8EBDC00"],
                  stops=[0, 0.5, 1], gtype="LINEAR", begin="TOP_CENTER",
                  end="BOTTOM_CENTER", nodes=n))

    # ================= L3 近景草花（sigma 3 微虚化） =================
    near_stuff = []
    # 草丛（三角叶组）
    for cx, hgt, wd in [(120, 200, 70), (210, 260, 84), (330, 170, 60),
                        (900, 240, 78), (990, 190, 64)]:
        near_stuff.append(
            f'<Positioned left="{cx - wd/2}" top="{1400 - hgt}" width="{wd}" '
            f'height="{hgt}">'
            f'<Container width="{wd}" height="{hgt}" color="{LAYER_NEAR}" '
            f'shape="CIRCLE"/></Positioned>')
    # 花（瓣组 + 心）
    for cx, cy, pr, pc in [(300, 1352, 26, "#F2A65A"), (310, 1358, 22, "#F2A65A"),
                           (830, 1330, 30, "#E87EA1"), (812, 1342, 24, "#E87EA1")]:
        for k in range(5):
            a = math.radians(k * 72 - 90)
            px, py = cx + pr * 0.62 * math.cos(a), cy + pr * 0.62 * math.sin(a)
            near_stuff.append(
                f'<Positioned left="{px - pr*0.55:.2f}" top="{py - pr*0.55:.2f}" '
                f'width="{pr*1.1:.2f}" height="{pr*1.1:.2f}">'
                f'<Container width="{pr*1.1:.2f}" height="{pr*1.1:.2f}" '
                f'shape="CIRCLE" color="{pc}"/></Positioned>')
        near_stuff.append(
            f'<Positioned left="{cx - pr*0.34:.2f}" top="{cy - pr*0.34:.2f}" '
            f'width="{pr*0.68:.2f}" height="{pr*0.68:.2f}">'
            f'<Container width="{pr*0.68:.2f}" height="{pr*0.68:.2f}" '
            f'shape="CIRCLE" color="#F7D147"/></Positioned>')
    # 茎
    for cx, cy in [(300, 1352), (830, 1330)]:
        near_stuff.append(
            f'<Positioned left="{cx - 3}" top="{cy}" width="6" height="120">'
            f'<Container width="6" height="120" color="{LAYER_NEAR}"/>'
            f'</Positioned>')
    blurred(0, 1240, W, 300, "".join(near_stuff), 3, 3, n)

    # ================= L4 前景大叶（锐利，压左右下角） =================
    # 左叶（ClipPath 叶形，旋转 -28°）；盒 300×460 旋 28° 包围盒 481×547，
    # 盒中心 (250,1600) → 旋转后范围 x[10,490] y[1327,1873] 收于画布内
    lw, lh = 300, 460

    def leaf_widget(color):
        return (f'<ClipPath path="{leaf_path(lw, lh)}" '
                f'viewBox="0 0 {lw} {lh}" fit="FILL" fillRule="NON_ZERO">'
                f'<Container width="{lw}" height="{lh}" '
                f'color="{color}"/></ClipPath>')

    n.append(rotate(100, 1370, lw, lh, leaf_widget(LEAF_C), -28, nodes=n))
    # 右叶（旋转 24°，深色）；盒中心 (830,1620) → x[600,1060] y[1349,1891]
    n.append(rotate(680, 1390, lw, lh, leaf_widget(LEAF_D), 24, nodes=n))

    # ================= 中央徽标 + 文案 =================
    # 徽标：圆角方底 + 叶形镂空 + 高光
    bx, by, bs = 390, 700, 300
    n.append(rect(bx, by, bs, bs, "#FFFFFF", 68))
    n.append(rect(bx, by, bs, bs, "transparent").replace(
        'color="transparent"',
        'color="transparent" border="6 SOLID #FFFFFF"'))
    n.append(clip_path(bx + 40, by + 40, bs - 80, bs - 80,
                       leaf_path(bs - 80, bs - 80),
                       f'<Container width="{bs - 80}" height="{bs - 80}" '
                       f'color="{LEAF_C}"/>', nodes=n))
    # 叶尖高光
    n.append(clip_path(bx + 96, by + 66, 60, 130,
                       leaf_path(60, 130),
                       '<Container width="60" height="130" '
                       'color="#8FD0A0"/>', nodes=n))
    # 徽标投影（boxShadow 多层）
    n.append(rect(bx, by, bs, bs, "transparent").replace(
        'color="transparent"',
        'color="transparent" boxShadow="0 18 44 0 #2F6B4150, 0 4 12 0 #2F6B4130"'))

    T("叶子", 240, 1060, 600, 120, 96, "#2F5B3C", "CENTER", "BOLD",
      SERIF, shadow="0 4 0 #2F6B4122", nodes=n)
    T("自然认知 · 给孩子一座会说话的公园", 240, 1190, 600, 40, 26,
      "#4A6B52", "CENTER", "NORMAL", SANS, spacing=2, nodes=n)
    # 装饰小圆点（童趣）
    for i, (dx, dy, r, c) in enumerate([(250, 1160, 8, "#F2A65A"),
                                        (830, 1160, 8, "#E87EA1")]):
        n.append(circle(dx, dy, r, c))

    # ================= 底部 loading =================
    T("正在播撒种子…", 240, 1700, 600, 30, 20, "#4A6B52", "CENTER",
      "NORMAL", SANS, spacing=4, nodes=n)
    # 三点 loading（Opacity 呼吸层次）
    for i in range(3):
        n.append(opacity(430 + i * 60, 1760, 22, 22,
                         f'<Container width="22" height="22" shape="CIRCLE" '
                         f'color="#4E9A5F"/>',
                         0.35 + 0.3 * i, nodes=n))
    T("3–8 岁自然启蒙 · 离线可用 · 无广告", 240, 1820, 600, 26, 16,
      "#6B8A72", "CENTER", "NORMAL", SANS, nodes=n)

    out = snapshot(W, H, n, SKY)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-08-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
