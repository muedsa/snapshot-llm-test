#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-03 剪纸风国家公园导览图（1920×1080，16:9 横版壁画）。
鹭洲湿地公园游客中心大幅导览图。
主导手法：ClipPath EVEN_ODD 多轮廓镂空剪纸（团花/云朵卷曲/鱼鳞/亭窗/
芦苇中缝/烛穗环/船帆月牙）+ 分层剪影 + ClipOval 日月 + 云纹滚边。
路径纪律：viewBox 一律 "0 0 w h"（探测实证），路径用局部坐标；
曲线全部采样为 M/L 折线（不依赖未探测的 Q/C）；
EVEN_ODD 仅用于「实体内含镂空」，实体子路径严禁重叠（重叠处会变镂空）。"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, clip_path, clip_oval, container_rotate,
                        assert_canvas, WARN,
                        INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE,
                        ORANGE_DEEP, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER,
                        rect, circle, chip)

W, H = 1920, 1080

# 纸剪配色（B02 调色板的 tonal 变体）
C_FAR = "#A9C6BC"    # 远山
C_MID = "#6E968C"    # 中景丘
C_WATER = "#2E5A54"  # 水面
C_RIDGE = "#8FB5A8"  # 水波
C_SKY = "#C7DAD2"    # 图面天空（较 SKY 加深，托出白云剪影）


# ---------------------------------------------------------------- 路径助手
def P(pts, close=True):
    """点列 → SVG path（仅 M/L/Z）。"""
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    d += "".join(f" L {x:.1f} {y:.1f}" for x, y in pts[1:])
    return d + " Z" if close else d


def epts(cx, cy, rx, ry, n=40, a0=0.0, a1=360.0):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def bump_pts(cx, ybase, r, a0=0.0, a1=180.0, n=12):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             ybase + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def cf(x, y, w, h, path, color, rule="NON_ZERO", nodes=None):
    """ClipPath 填充块：viewBox="0 0 w h"，路径为局部坐标。"""
    node = clip_path(x, y, w, h, path,
                     f'<Container width="{w:.2f}" height="{h:.2f}" '
                     f'color="{color}"/>',
                     viewbox=f"0 0 {w:.0f} {h:.0f}", fill_rule=rule)
    if nodes is not None:
        nodes.append(node)
    return node


def ering(x, y, w, h, rx, ry, color, nodes=None, n=40):
    """EVEN_ODD 椭圆环（可选椭圆内孔）。"""
    cf(x, y, w, h,
       P(epts(w / 2, h / 2, w / 2, h / 2, n)) + " " +
       P(epts(w / 2, h / 2, rx, ry, n)), color, "EVEN_ODD", nodes)


def ring(x, y, d, r_in, color, nodes=None, n=40):
    ering(x, y, d, d, r_in, r_in, color, nodes, n)


def brect(x, y, w, h, bw, color, nodes=None, radius=0.0):
    """透明填充 + 边框的矩形（纸剪框线）。"""
    br = f' borderRadius="{radius:.2f}"' if radius else ""
    node = (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
            f'color="transparent" border="{bw} SOLID {color}"{br}/>'
            f'</Positioned>')
    if nodes is not None:
        nodes.append(node)
    return node


# ---------------------------------------------------------------- 纸剪构件
def scallop_strip(x, y, w, h, r, color, nodes=None):
    """下缘云纹滚边的纸剪条（横幅/图板）。"""
    n_b = max(1, int(round(w / (2 * r))))
    step = w / n_b
    pts = [(0.0, 0.0), (w, 0.0), (w, h - r)]
    for i in range(n_b, 0, -1):
        pts += bump_pts(i * step - step / 2, h - r, r, 0, 180, 10)
    pts += [(0.0, h - r)]
    cf(x, y, w, h, P(pts), color, "NON_ZERO", nodes)


def cloud(x, y, w, h, color, nodes=None):
    """纸剪云：底边平直 + 上缘 4 枚上凸 bump；中部两 bump 内置卷曲镂空。"""
    n_b = 4
    step = w / n_b
    pts = [(0.0, h), (w, h)]
    rrs = []
    for i in range(n_b, 0, -1):
        rr = step * (0.42 if i % 2 else 0.34)
        rrs.append(rr)
        pts += bump_pts(i * step - step / 2, h, rr, 0, -180, 12)
    d = P(pts)
    for i in (2, 3):  # 中部两枚 bump 的卷曲（严格位于剪影内）
        rr = rrs[n_b - i]
        cx = i * step - step / 2
        d += " " + P(epts(cx, h - 0.65 * rr, 0.28 * rr, 0.28 * rr, 14))
    cf(x, y, w, h, d, color, "EVEN_ODD", nodes)


def reed_blade(bx, base, h, lean, color, nodes=None):
    """芦苇叶（局部坐标 40×(h+10)，盒 (bx-18, base-h-8)）。"""
    hy = h + 8.0                       # 局部叶基 y
    left = [(8, hy), (3 + lean * 0.35, h * 0.5 + 8), (14 + lean * 0.8, 14)]
    right = [(28, hy), (33 + lean * 0.35, h * 0.5 + 8), (22 + lean * 0.8, 12)]
    sl = [(15.8, h), (15.8 + lean * 0.4, h * 0.45 + 8),
          (15.8 + lean * 0.72, 30)]
    sr = [(20.2, h), (20.2 + lean * 0.4, h * 0.45 + 8),
          (20.2 + lean * 0.72, 30)]
    cf(bx - 18, base - h - 8, 40, h + 10,
       P(left + right[::-1]) + " " + P(sl + sr[::-1]), color, "EVEN_ODD",
       nodes)


def cattail(bx, base, h, lean, color, nodes=None):
    """芦苇 + 烛穗（穗为 EVEN_ODD 椭圆环）。"""
    reed_blade(bx, base, h, lean, color, nodes)
    reed_blade(bx + lean * 0.9, base, h * 0.96, lean * 0.9, color, nodes)
    hx, hy = bx + lean, base - h - 28
    ering(hx - 12, hy - 30, 24, 56, 5.5, 22, color, nodes, 24)


def fish(x, y, w, h, color, nodes=None):
    """纸剪鱼：尾（NON_ZERO，先画）+ 身（EVEN_ODD 鳞/眼镂空）。"""
    tail = P([(w * 0.80, h * 0.5), (w, h * 0.06), (w * 0.92, h * 0.5),
              (w, h * 0.94)])
    cf(x, y, w, h, tail, color, "NON_ZERO", nodes)
    body = P(epts(w * 0.40, h * 0.5, w * 0.40, h * 0.46, 28))
    for fx, fy, fr in [(0.28, 0.30, 0.075), (0.42, 0.5, 0.085),
                       (0.28, 0.70, 0.075), (0.56, 0.33, 0.06),
                       (0.56, 0.67, 0.06)]:
        body += " " + P(epts(fx * w, fy * h, fr * w, fr * h, 14))
    body += " " + P(epts(0.14 * w, 0.40 * h, 0.032 * w, 0.048 * h, 12))
    cf(x, y, w, h, body, color, "EVEN_ODD", nodes)


def boat(x, y, w, h, color, nodes=None):
    """纸剪帆船：船体 + 桅 + 帆（帆内 EVEN_ODD 月牙镂空；实体零重叠）。"""
    hull = P([(0, h * 0.34), (w, h * 0.34), (w * 0.88, h * 0.82),
              (w * 0.12, h * 0.82)])
    mast = P([(w * 0.47, 0), (w * 0.53, 0), (w * 0.53, h * 0.34),
              (w * 0.47, h * 0.34)])
    sail = P([(w * 0.56, h * 0.05), (w * 0.56, h * 0.34), (w * 0.93, h * 0.34)])
    sail_in = P([(w * 0.64, h * 0.15), (w * 0.64, h * 0.27),
                 (w * 0.84, h * 0.27)])
    cf(x, y, w, h, hull + " " + mast + " " + sail + " " + sail_in,
       color, "EVEN_ODD", nodes)


def pavilion(x, y, w, h, color, nodes=None):
    """纸剪望湖亭：飞檐 + 柱身 + 台基；门窗 EVEN_ODD 镂空（实体零重叠）。"""
    roof = P([(w * 0.06, h * 0.42), (w * 0.20, h * 0.20),
              (w * 0.30, h * 0.10), (w * 0.70, h * 0.10),
              (w * 0.80, h * 0.20), (w * 0.94, h * 0.42),
              (w * 0.86, h * 0.46), (w * 0.14, h * 0.46)])
    ridge = P([(w * 0.47, 0), (w * 0.53, 0), (w * 0.53, h * 0.10),
               (w * 0.47, h * 0.10)])
    body = P([(w * 0.20, h * 0.46), (w * 0.20, h * 0.80),
              (w * 0.80, h * 0.80), (w * 0.80, h * 0.46)])
    base = P([(w * 0.12, h * 0.80), (w * 0.88, h * 0.80),
              (w * 0.94, h * 0.94), (w * 0.06, h * 0.94)])
    door = P([(w * 0.44, h * 0.80), (w * 0.44, h * 0.62),
              (w * 0.50, h * 0.55), (w * 0.56, h * 0.62),
              (w * 0.56, h * 0.80)])
    win_l = P([(w * 0.25, h * 0.56), (w * 0.25, h * 0.72),
               (w * 0.37, h * 0.72), (w * 0.37, h * 0.56)])
    win_r = P([(w * 0.63, h * 0.56), (w * 0.63, h * 0.72),
               (w * 0.75, h * 0.72), (w * 0.75, h * 0.56)])
    cf(x, y, w, h, roof + " " + ridge + " " + body + " " + base + " " +
       door + " " + win_l + " " + win_r, color, "EVEN_ODD", nodes)


def qbez(p0, c, p1, steps=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1])
            for i in range(steps + 1) for t in (i / steps,)]


def ray(cx, cy, ang, r0, r1, w, color, nodes=None):
    """日光芒：旋转细矩形（Container transform 矩阵）。"""
    mx = cx + (r0 + r1) / 2 * math.cos(math.radians(ang))
    my = cy + (r0 + r1) / 2 * math.sin(math.radians(ang))
    container_rotate(mx - (r1 - r0) / 2, my - w / 2, r1 - r0, w, ang,
                     attrs=f'color="{color}"', nodes=nodes)


# ---------------------------------------------------------------- 主构图
def dsl() -> str:
    n = []
    # ================= 纸底与外框 =================
    n.append(rect(0, 0, W, H, PAPER))
    brect(24, 24, W - 48, H - 48, 2, INK, n)
    brect(36, 36, W - 72, H - 72, 1, "#3E7C7455", n)

    # ================= 左栏：团花徽记 + 标题 + 横幅 =================
    d = P(epts(48, 48, 46, 46, 44)) + " " + P(epts(48, 48, 11, 11, 20))
    for k in range(6):
        a = math.radians(k * 60 - 90)
        d += " " + P(epts(48 + 27 * math.cos(a), 48 + 27 * math.sin(a),
                         7.5, 7.5, 14))
    cf(84, 88, 96, 96, d, INK, "EVEN_ODD", n)
    T("LUHOU WETLAND PARK", 196, 100, 420, 20, 14, REED, "LEFT", "NORMAL",
      MONO, spacing=3, nodes=n)
    T("湿地导览图", 196, 126, 420, 40, 30, TEAL, "LEFT", "BOLD", SERIF,
      nodes=n)
    T("鹭洲湿地公园", 84, 232, 540, 84, 62, INK, "LEFT", "BOLD", SERIF,
      nodes=n)
    scallop_strip(84, 340, 520, 58, 12, TEAL, n)
    T("秋迁季 · 11 月观鸟指南", 84, 354, 520, 30, 22, WHITE, "CENTER",
      "BOLD", SANS, spacing=2, nodes=n)

    # ================= 左栏：信息卡 =================
    n.append(rect(84, 428, 520, 296, WHITE, 14))
    brect(84, 428, 520, 296, 1.5, TEAL, n, 14)
    rows = [
        ("开放时间", "旺季 08:30–20:00 · 淡季 09:00–17:00"),
        ("闭园维护", "每周二闭园检修"),
        ("门票", "成人 ¥30 · 优惠 ¥15 · 1.2m 以下免票"),
        ("观光车", "¥20/人 · 环线约 40 分钟"),
        ("咨询电话", "0512-6688-0000"),
        ("地址", "滨江区鹭洲路 1 号 · 地铁 4 号线鹭洲站 B 口"),
    ]
    for i, (lab, val) in enumerate(rows):
        ry = 452 + i * 42
        n.append(chip(108, ry, 84, 26, lab, TEAL, WHITE, 14))
        T(val, 208, ry + 2, 372, 24, 15, INK, "LEFT", "NORMAL", SANS,
          nodes=n)
    T("862 公顷湿地 · 287 种鸟类 · 426 种植物", 84, 744, 520, 22, 14,
      REED, "CENTER", "NORMAL", SANS, nodes=n)

    # ================= 左栏：图例 =================
    T("图例 · LEGEND", 84, 788, 300, 26, 17, INK, "LEFT", "BOLD", SANS,
      spacing=1, nodes=n)
    legend = [
        ("观鸟屋", "pavilion", "观鸟点 4 处"),
        ("木栈道", "walk", "环湖 3.6 km"),
        ("游船码头", "boat", "北码头"),
        ("访客中心", "house", "服务 08:30–17:00"),
    ]
    for i, (lab, kind, sub) in enumerate(legend):
        lx = 84 + (i % 2) * 268
        ly = 826 + (i // 2) * 76
        clip_oval(lx, ly, 44, 44,
                  f'<Container width="44" height="44" color="{SKY}" '
                  f'border="1.5 SOLID {TEAL}"/>', n)
        gx, gy = lx, ly
        if kind == "pavilion":
            cf(gx, gy, 44, 44,
               P([(6, 26), (13, 14), (17, 11), (27, 11), (31, 14),
                  (38, 26), (34, 28), (10, 28)]) + " " +
               P([(13, 28), (13, 38), (31, 38), (31, 28)]) + " " +
               P([(19, 38), (19, 32), (22, 30), (25, 32), (25, 38)]),
               INK, "EVEN_ODD", n)
        elif kind == "walk":
            for k in range(3):
                n.append(rect(gx + 9, gy + 15 + k * 8, 26, 3.4, INK, 1.7))
        elif kind == "boat":
            cf(gx, gy, 44, 44,
               P([(6, 26), (38, 26), (33, 36), (11, 36)]) + " " +
               P([(20, 8), (23, 8), (23, 26), (20, 26)]) + " " +
               P([(25, 10), (25, 26), (38, 26)]) + " " +
               P([(29, 15), (29, 23), (34, 23)]),
               INK, "EVEN_ODD", n)
        else:
            cf(gx, gy, 44, 44,
               P([(8, 22), (22, 8), (36, 22), (36, 38), (8, 38)]) + " " +
               P([(18, 38), (18, 29), (26, 29), (26, 38)]),
               INK, "EVEN_ODD", n)
        T(lab, lx + 54, ly + 1, 200, 24, 16, INK, "LEFT", "BOLD", SANS,
          nodes=n)
        T(sub, lx + 54, ly + 25, 200, 18, 11, REED, "LEFT", "NORMAL",
          SANS, nodes=n)
    T("鹭洲湿地公园管理处 · 本图为导览示意，请以园内实地标识为准", 84,
      996, 560, 18, 11, REED, "LEFT", "NORMAL", SANS, nodes=n)

    # ================= 右栏：导览图面板（云纹滚边底） =================
    MX, MY, MW, MH = 660, 84, 1200, 936
    n_b, br = 15, 40
    step = MW / n_b
    mpts = [(0, 0), (MW, 0), (MW, MH - br)]
    for i in range(n_b, 0, -1):
        mpts += bump_pts(i * step - step / 2, MH - br, br, 0, 180, 14)
    mpts += [(0, MH - br)]
    cf(MX, MY, MW, MH, P(mpts), C_SKY, "NON_ZERO", n)

    # 太阳：EVEN_ODD 圆环 + 八道芒
    ering(MX + 834, MY + 60, 132, 132, 46, 46, ORANGE, n)
    for k in range(8):
        ray(MX + 900, MY + 126, k * 45, 74, 100, 7, ORANGE, n)

    # 云朵两枚（卷曲镂空）
    cloud(MX + 240, MY + 86, 300, 96, WHITE, n)
    cloud(MX + 520, MY + 216, 220, 72, WHITE, n)

    # 远山脊 + 中景丘（折线剪影）
    ridge = [(0, 220), (0, 150), (110, 100), (230, 140), (340, 88),
             (460, 132), (560, 72), (690, 128), (810, 84), (930, 138),
             (1050, 92), (1160, 130), (1200, 112)]
    cf(MX, MY + 300, MW, 220, P(ridge), C_FAR, "NON_ZERO", n)
    hills = [(0, 260), (0, 185), (180, 122), (340, 168), (520, 112),
             (700, 172), (900, 124), (1080, 150), (1200, 140)]
    cf(MX, MY + 440, MW, 260, P(hills), C_MID, "NON_ZERO", n)

    # 望湖亭（坐中景丘脊，基线与脊线相接）
    pavilion(MX + 980, MY + 436, 200, 152, INK, n)

    # 水面（止于滚边槽线上方，留出近岸浅滩带）
    n.append(rect(MX, MY + 616, MW, 264, C_WATER))
    for i in range(16):
        n.append(rect(MX + 40 + i * 72, MY + 640 + (i % 4) * 26,
                      44, 2.6, C_RIDGE))

    # 鱼三尾（尾先画，身后叠）
    fish(MX + 290, MY + 716, 110, 44, ORANGE, n)
    fish(MX + 700, MY + 736, 90, 36, ORANGE, n)
    fish(MX + 200, MY + 780, 120, 48, ORANGE, n)
    # 帆船（浮于水面）
    boat(MX + 900, MY + 782, 170, 90, PAPER, n)

    # 木栈道踏步石（访客中心 → 望湖亭；支线 → 苇岸餐厅）
    for tx, ty in qbez((MX + 340, MY + 866), (MX + 520, MY + 821),
                       (MX + 820, MY + 726)):
        n.append(circle(tx, ty, 7, PAPER))
    for tx, ty in qbez((MX + 820, MY + 726), (MX + 960, MY + 716),
                       (MX + 1075, MY + 592)):
        n.append(circle(tx, ty, 7, PAPER))
    for tx, ty in qbez((MX + 550, MY + 808), (MX + 590, MY + 761),
                       (MX + 628, MY + 716)):
        n.append(circle(tx, ty, 7, PAPER))

    # 前景芦苇（EVEN_ODD 叶缝 + 烛穗环）
    cattail(MX + 30, MY + 884, 150, -26, INK, n)
    cattail(MX + 96, MY + 884, 210, 14, INK, n)
    cattail(MX + 150, MY + 884, 170, -10, INK, n)
    cattail(MX + 1060, MY + 884, 190, 18, INK, n)
    cattail(MX + 1116, MY + 884, 150, -20, INK, n)
    cattail(MX + 1160, MY + 884, 220, 8, INK, n)

    # 景点标记 1/2/3
    markers = [
        ("1", "观鸟屋", MX + 220, MY + 616),
        ("2", "苇岸餐厅", MX + 630, MY + 676),
        ("3", "访客中心", MX + 220, MY + 864),
    ]
    for num, lab, mx, my in markers:
        clip_oval(mx - 24, my - 24, 48, 48,
                  f'<Container width="48" height="48" color="{ORANGE}"/>', n)
        T(num, mx - 24, my - 13, 48, 26, 18, WHITE, "CENTER", "BOLD",
          INTER, nodes=n)
        n.append(chip(mx + 30, my - 14, 116, 28, lab, PAPER, INK, 14))

    # 指北针（EVEN_ODD 圆环 + 纸剪箭）
    ering(MX + 1092, MY + 108, 64, 64, 44, 44, INK, n)
    cf(MX + 1108, MY + 122, 32, 34,
       P([(16, 0), (30, 26), (16, 20), (2, 26)]), ORANGE, "NON_ZERO", n)
    T("N", MX + 1092, MY + 64, 64, 24, 16, INK, "CENTER", "BOLD", SANS,
      nodes=n)

    # 比例尺（近岸浅滩带上）
    sb_x, sb_y = MX + 460, MY + 864
    for i in range(5):
        n.append(rect(sb_x + i * 44, sb_y, 44, 8,
                      INK if i % 2 == 0 else PAPER))
    brect(sb_x, sb_y, 220, 8, 1, INK, n)
    T("0", sb_x - 10, sb_y + 12, 40, 16, 11, INK, "CENTER", "NORMAL", MONO,
      nodes=n)
    T("200 m", sb_x + 68, sb_y + 12, 70, 16, 11, INK, "CENTER", "NORMAL",
      MONO, nodes=n)
    T("400", sb_x + 180, sb_y + 12, 50, 16, 11, INK, "CENTER", "NORMAL",
      MONO, nodes=n)

    out = snapshot(W, H, n, PAPER)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-03-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
