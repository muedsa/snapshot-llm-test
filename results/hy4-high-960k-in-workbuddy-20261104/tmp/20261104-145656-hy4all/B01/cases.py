#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 — 十张真实场景的炫酷用例：10 个独立构图/配色/信息结构/媒介的作品。

每件由完整、自包含的 Snapshot DSL 构造（纯 DSL，无外部图片素材）。
所有场景、品牌、人物与数值均为自拟演示内容，不宣称真实部署。
"""
import math
import random
import sys, os
sys.path.insert(0, os.environ["TOOLS"])
import suite
sys.path.insert(0, str(suite.SUITE_TMP))
import designkit as K
from dsl import CN, LATIN, MONO, cdata
SERIF = K.SERIF


# ============================================================ case-01 到站牌
def draw_01(c):
    W, H = 1600, 900
    c.rect(0, 0, W, H, "#070E18")
    K.dot_grid(c, 0, 0, W, H, 56, 1.1, "#20456B", opacity=0.28)
    K.linear(c, 0, 0, W, 120, ["#102C4E", "#0A1626"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.rect(0, 116, W, 4, "#F5B942")
    c.rect(40, 34, 10, 52, "#F5B942", radius=3)
    c.rect(56, 48, 10, 38, "#F5B942", radius=3, opacity=0.75)
    c.rect(72, 62, 10, 24, "#F5B942", radius=3, opacity=0.5)
    c.text(100, 22, 780, 52, "滨江公园站  BINJIANG PARK", 34, "#EAF3FF", bold=True)
    c.text(100, 78, 780, 30, "METRO LINE 2 / 换乘 4 号线  ·  站台层实时到站信息", 17, "#7C9BB8")
    c.text(1180, 26, 380, 40, "18:42:06", 40, "#F5B942", align="RIGHT", bold=True, font=LATIN)
    c.text(1180, 74, 380, 28, "WED / 2026-11-04 / PLATFORM", 16, "#7C9BB8", align="RIGHT", font=LATIN)

    cols = [(48, "线路 / LINE"), (500, "终点站 / DESTINATION"),
            (880, "站台"), (1060, "预计到站 / ETA"), (1360, "状态 / STATUS")]
    for x, t in cols:
        c.text(x, 156, 330, 28, t, 16, "#5E7A98", bold=True)

    rows = [
        ("2", "#E2483D", "往东 / EASTBOUND", "浦东国际机场", "Pudong Intl Airport", "1 站台", "2", "即将进站", "#34D399"),
        ("4", "#2E7DD1", "往西 / WESTBOUND", "宜山路", "Yishan Road", "3 站台", "5", "准点", "#34D399"),
        ("2", "#E2483D", "往东 / EASTBOUND", "徐泾东", "Xujing East", "2 站台", "8", "准点", "#7C9BB8"),
        ("6", "#F0A93B", "往南 / SOUTHBOUND", "东方体育中心", "Oriental Sports Ctr", "4 站台", "12", "候车", "#7C9BB8"),
    ]
    for i, (ln, col, direc, dest, en, plat, eta, st, stc) in enumerate(rows):
        y = 204 + i * 140
        c.rect(40, y, 1520, 124, "#0E1C2E", radius=10)
        c.rect(40, y, 6, 124, col, radius=3)
        c.rect(60, y + 62, 1460, 1, "#1C2E44")
        c.rect(70, y + 32, 60, 60, col, radius=12)
        c.text(70, y + 32, 60, 60, ln, 30, "#FFFFFF", align="CENTER", bold=True, font=LATIN)
        c.text(150, y + 28, 330, 40, direc, 22, "#EAF3FF", bold=True)
        c.text(150, y + 72, 330, 28, "LINE " + ln + " SERVICE", 15, "#6E89A6", font=LATIN)
        c.text(500, y + 28, 350, 44, dest, 28, "#FFFFFF", bold=True)
        c.text(500, y + 74, 350, 28, en, 16, "#6E89A6", font=LATIN)
        c.text(880, y + 42, 160, 44, plat, 25, "#C6DCF7", align="CENTER", bold=True)
        c.text(1060, y + 22, 280, 62, eta, 54, "#F5B942", align="CENTER", bold=True, font=LATIN)
        c.text(1060, y + 86, 280, 26, "MIN", 15, "#6E89A6", align="CENTER", font=LATIN)
        c.circle(1375, y + 62, 7, stc)
        c.text(1395, y + 44, 155, 40, st, 21, stc, bold=True)

    c.rect(0, 782, W, 118, "#0A1626")
    c.rect(0, 780, W, 2, "#1C3350")
    c.text(48, 800, 900, 34, "末班车 23:15  ·  无障碍电梯 B 口  ·  失物招领请至服务台", 19, "#8FA8C4")
    c.text(1000, 802, 560, 32, "NEXT TRAIN INFO / 每 30 秒刷新", 16, "#5E7A98", align="RIGHT", font=LATIN)
    c.text(48, 844, 1100, 28, "本信息牌为演示作品，线路、时刻与站名均为示例数据，不代表实际运营信息。", 15, "#4A6480")
    c.text(1180, 844, 380, 28, "SNAPSHOT / DEMO BOARD", 14, "#3E5872", align="RIGHT", font=LATIN)


# ============================================================ case-02 咖啡配方卡
def draw_02(c):
    W, H = 1000, 1400
    K.radial(c, 0, 0, W, H, ["#FCF6EA", "#F0E2C9"], grad_radius=1.0)
    K.dot_grid(c, 0, 0, W, H, 60, 1.0, "#DCC9A8", opacity=0.5)
    c.rect(60, 60, 10, 54, "#B5603C")
    c.text(86, 54, 600, 48, "一滴 · DRIP LAB", 34, "#3A2418", bold=True, font=SERIF)
    c.text(86, 106, 600, 28, "HOUSE BREW RECIPE / No.07", 16, "#A08A6C", font=LATIN, spacing=2)
    c.text(620, 62, 320, 40, "V60 · 01 滤杯", 22, "#B5603C", align="RIGHT", bold=True)
    c.text(620, 104, 320, 28, "单人份 / 250 ml", 16, "#A08A6C", align="RIGHT")
    K.rule(c, 60, 150, 880, "#D9C6A6", 2)

    c.circle(300, 400, 168, "#F6ECD8")
    segs = [("酸", "#E0A03A", 0.72), ("甜", "#C96F4A", 0.55),
            ("醇", "#7C8B6B", 0.80), ("苦", "#5A4636", 0.35)]
    for i, (nm, col, v) in enumerate(segs):
        a0, a1 = -90 + i * 90 + 6, -90 + (i + 1) * 90 - 6
        K.arc(c, 300, 400, 150, 120, a0, a1, "#E3D3B6")
        K.arc(c, 300, 400, 150, 120, a0, a0 + (a1 - a0) * v, col)
    c.circle(300, 400, 112, "#FCF6EA")
    c.text(200, 362, 200, 44, "风味轮", 26, "#3A2418", align="CENTER", bold=True, font=SERIF)
    c.text(200, 408, 200, 30, "FLAVOR MAP", 14, "#A08A6C", align="CENTER", font=LATIN, spacing=1)
    for i, (nm, col, v) in enumerate(segs):
        ang = math.radians(-45 + i * 90)
        lx, ly = 300 + 186 * math.cos(ang), 400 + 186 * math.sin(ang)
        c.text(lx - 60, ly - 16, 120, 32, "%s %d" % (nm, int(v * 100)), 18, col,
               align="CENTER", bold=True)

    c.rect(560, 230, 380, 330, "#FFFFFF", radius=16, border="1 SOLID #E3D3B6")
    c.text(584, 248, 330, 34, "冲煮参数 / PARAMETERS", 20, "#3A2418", bold=True)
    params = [("粉量", "15 g"), ("研磨", "中细 / 白砂糖"), ("水温", "92 C"),
              ("粉水比", "1 : 16.7"), ("总时长", "2:10")]
    for i, (k, v) in enumerate(params):
        yy = 296 + i * 52
        c.text(584, yy, 170, 36, k, 19, "#8A7355")
        c.text(740, yy, 180, 36, v, 20, "#3A2418", align="RIGHT", bold=True, font=LATIN)
        if i < 4:
            K.rule(c, 584, yy + 44, 332, "#EDE0C8", 1)

    c.text(60, 592, 700, 40, "注水时间轴 / POUR SCHEDULE", 24, "#3A2418", bold=True)
    stages = [("闷蒸", "00:00 - 00:30", "注水 30 g", "#C96F4A", 0.12),
              ("第一段", "00:30 - 01:15", "累计 140 g", "#D98A4E", 0.46),
              ("第二段", "01:15 - 01:50", "累计 220 g", "#E0A03A", 0.78),
              ("收尾", "01:50 - 02:10", "总量 250 g", "#7C8B6B", 1.0)]
    c.rect(138, 650, 4, 400, "#E3D3B6")
    for i, (nm, tm, amt, col, frac) in enumerate(stages):
        yy = 660 + i * 100
        c.circle(140, yy + 16, 11, col, border="3 SOLID #FCF6EA")
        c.text(180, yy - 2, 210, 34, nm, 22, "#3A2418", bold=True)
        c.text(400, yy - 2, 230, 34, tm, 17, "#8A7355", font=LATIN)
        c.text(650, yy - 2, 270, 34, amt, 20, col, align="RIGHT", bold=True)
        c.rect(180, yy + 40, 740, 14, "#EDE0C8", radius=7)
        c.rect(180, yy + 40, 740 * frac, 14, col, radius=7)

    c.text(60, 1084, 700, 36, "风味描述 / TASTING NOTES", 20, "#3A2418", bold=True)
    notes = [("柑橘", "#E0A03A"), ("红糖", "#C96F4A"),
             ("乌龙茶", "#7C8B6B"), ("干净回甘", "#5A4636")]
    for i, (nm, col) in enumerate(notes):
        xx = 60 + i * 230
        K.capsule(c, xx, 1128, 210, 46, "#FFFFFF", border="1 SOLID #E3D3B6")
        c.circle(xx + 28, 1151, 8, col)
        c.text(xx + 46, 1130, 158, 42, nm, 19, "#3A2418", bold=True)
    K.rule(c, 60, 1208, 880, "#D9C6A6", 2)
    c.text(60, 1224, 880, 30, "示例配方：品牌、豆况、水温与注水时序均为自拟演示，非实际门店产品。", 16, "#A08A6C")
    c.text(60, 1258, 880, 30, "请按实际豆况与口味调整；图中数值仅用于展示信息组织方式。", 16, "#A08A6C")
    c.text(60, 1318, 880, 40, "BREW SLOW, TASTE SLOW.", 22, "#B5603C", font=LATIN, spacing=3, bold=True)


# ============================================================ case-03 电子票
def draw_03(c):
    W, H = 1280, 720
    c.rect(0, 0, W, H, "#0C0716")
    K.radial(c, 0, 0, W, H, ["#2A1040", "#0C0716"], grad_radius=0.9)
    K.glow(c, 250, 170, 230, 160, "#E0409B", sigma=70, opacity=0.55)
    K.glow(c, 1090, 600, 240, 170, "#25D0E0", sigma=70, opacity=0.5)
    K.starfield(c, 0, 0, W, H, 80, "#FFFFFF", seed=9, rmin=0.6, rmax=1.8)
    K.notched_card(c, 60, 90, 1160, 540, "#160E2B", nr=30)
    K.linear(c, 60, 90, 1160, 10, ["#FF3D9A", "#8B5CF6", "#22D3EE"],
             begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.text(110, 138, 700, 32, "ECHO FESTIVAL 2026  /  ADMIT ONE", 16, "#C9A6F0",
           font=LATIN, spacing=2, bold=True)
    c.text(110, 184, 720, 96, "回声音乐节", 64, "#FFFFFF", bold=True)
    K.linear(c, 110, 288, 520, 6, ["#FF3D9A", "#22D3EE"],
             begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.text(110, 314, 700, 36, "2026.08.14  SAT  |  16:00 GATE  /  18:00 SHOW", 19,
           "#D8C7F2", font=LATIN)
    c.text(110, 356, 700, 36, "滨江草地公园  ·  A 区站席  /  RIVERSIDE PARK", 19, "#D8C7F2")
    chips = [("GATE", "A3"), ("ZONE", "A 站席"), ("NO.", "A-0826")]
    for i, (k, v) in enumerate(chips):
        xx = 110 + i * 215
        c.text(xx, 428, 195, 26, k, 14, "#9C82C4", font=LATIN, bold=True, spacing=1)
        c.text(xx, 456, 195, 42, v, 24, "#FFFFFF", bold=True)
    c.dashed_vline(830, 140, 440, 2, "#5A4478", dash=8, gap=8)
    c.text(842, 152, 90, 26, "撕下副券", 12, "#9C82C4")
    K.qr_matrix(c, 898, 168, 220, "#0C0716", "#F4EAFF", cells=13, seed=21)
    c.text(898, 398, 220, 26, "SCAN AT GATE", 13, "#9C82C4", align="CENTER",
           font=LATIN, spacing=2)
    K.linear(c, 878, 448, 290, 26, ["#FF3D9A", "#FBBF24", "#34D399", "#22D3EE", "#8B5CF6"],
             stops=[0, 0.25, 0.5, 0.75, 1], begin="CENTER_LEFT", end="CENTER_RIGHT", corner=13)
    K.barcode(c, 878, 498, 290, 40, "#E8D9FF", seed=5)
    c.text(878, 550, 290, 30, "NO. 0826-7741-ECHO", 14, "#9C82C4", align="CENTER",
           font=LATIN, spacing=1)
    c.text(60, 662, 800, 30, "示例票券：品牌、场次、座位与点阵码均为虚构演示，不可用于入场。", 15, "#7E6AA0")
    c.text(920, 662, 300, 30, "ECHO / 2026", 16, "#C9A6F0", align="RIGHT",
           font=LATIN, bold=True, spacing=2)


# ============================================================ case-04 配速腕带
def draw_04(c):
    W, H = 1800, 520
    K.linear(c, 0, 0, W, H, ["#FCFCF8", "#EDF1E6"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(50, 26, 1000, 52, "CITY MARATHON  /  配速腕带", 34, "#1E2A20", bold=True)
    c.text(50, 84, 1000, 30, "TARGET SUB 3:30  |  AVG PACE 4:58 /km  |  42.195 km", 18,
           "#6B7A68", font=LATIN)
    c.text(1300, 30, 450, 48, "3:29:40", 46, "#D2452F", align="RIGHT", bold=True, font=LATIN)
    c.text(1300, 86, 450, 28, "FINISH TARGET", 16, "#6B7A68", align="RIGHT", font=LATIN, spacing=2)

    bx, by, bw, bh = 50, 150, 1700, 250
    c.rect(bx, by, bw, bh, "#FFFFFF", radius=18, border="1 SOLID #D8DECF")

    def kx(km):
        return bx + 40 + (bw - 80) * km / 42.195

    zones = [("起跑", "#7FB069", 0, 5), ("稳定", "#4E9C81", 5, 21.1),
             ("巡航", "#3E8FA8", 21.1, 30), ("攻坚", "#E0952F", 30, 40),
             ("冲刺", "#D2452F", 40, 42.195)]
    for nm, col, a, b in zones:
        x0, x1 = kx(a), kx(b)
        c.rect(x0, by + 12, x1 - x0, 30, col)
        if x1 - x0 > 90:
            c.text(x0 + 6, by + 16, x1 - x0 - 12, 24, nm, 13, "#FFFFFF", bold=True)

    elev = []
    for i in range(81):
        km = 42.195 * i / 80
        e = by + 150 - (18 * math.sin(i / 9.0) + 10 * math.sin(i / 3.1) + 6 * math.cos(i / 1.7))
        elev.append((kx(km), e))
    K.polygon(c, [(kx(0), by + 190)] + elev + [(kx(42.195), by + 190)], "#E2EBD9")
    K.polyline(c, elev, 2.5, "#5B9B7A")
    c.text(bx + 24, by + 54, 300, 26, "海拔剖面 / ELEVATION", 14, "#6B7A68", font=LATIN)

    c.rect(bx + 20, by + 196, bw - 40, 1, "#D8DECF")
    for km in range(0, 43):
        x = kx(min(km, 42.195))
        h = 10 if km % 5 == 0 else 5
        c.rect(x, by + 196, 1, h, "#A9B69F")
    for km in [0, 5, 10, 15, 20, 25, 30, 35, 40, 42.195]:
        x = kx(km)
        lab = "42.2K" if km > 42 else "%dK" % int(km)
        c.text(x - 34, by + 212, 68, 24, lab, 13, "#4C5A48", align="CENTER", bold=True, font=LATIN)

    splits = [(5, "0:24:50"), (10, "0:49:40"), (21.1, "1:44:50"),
              (30, "2:29:00"), (40, "3:18:40"), (42.195, "3:29:40")]
    for km, t in splits:
        x = kx(km)
        c.circle(x, by + bh + 14, 5, "#1E2A20")
        c.text(x - 72, by + bh + 24, 144, 26, t, 14, "#1E2A20", align="CENTER",
               bold=True, font=LATIN)
        c.text(x - 72, by + bh + 48, 144, 22, ("%gK" % round(km, 1)), 12,
               "#8A9683", align="CENTER", font=LATIN)

    for i, (nm, col, a, b) in enumerate(zones):
        xx = 50 + i * 335
        c.rect(xx, 484, 22, 14, col, radius=3)
        c.text(xx + 30, 480, 300, 24, "%s  %g - %gK" % (nm, a, b), 14, "#4C5A48")
    c.text(1250, 120, 500, 22, "示例配速带：目标成绩与海拔为演示数据。", 13,
           "#8A9683", align="RIGHT")


# ============================================================ case-05 台风预警
def draw_05(c):
    W, H = 1080, 1080
    c.rect(0, 0, W, H, "#08131E")
    K.radial(c, 0, 0, W, H, ["#12283B", "#08131E"], grad_radius=0.85)
    c.rect(0, 0, W, 120, "#0B1C2B")
    c.rect(0, 116, W, 4, "#F97316")
    c.text(48, 18, 720, 48, "台风「海燕」· 路径预警", 38, "#F8FAFC", bold=True)
    c.text(48, 72, 720, 30, "TYPHOON HAIYAN  /  ORANGE ALERT  /  NO.11", 16,
           "#7E9AB5", font=LATIN)
    c.text(760, 30, 280, 42, "橙色预警", 30, "#F97316", align="RIGHT", bold=True)
    c.text(760, 76, 280, 26, "发布 11-04 18:00", 15, "#7E9AB5", align="RIGHT")

    cx, cy, r = 400, 580, 290
    for i in range(1, 5):
        K.ring(c, cx, cy, r * i / 4 + 1, r * i / 4 - 1, "#1D3A52", steps=72)
    c.rect(cx - r, cy, r * 2, 1, "#1D3A52")
    c.rect(cx, cy - r, 1, r * 2, "#1D3A52")
    for lab, lx, ly in [("N", cx, cy - r - 26), ("E", cx + r + 18, cy),
                        ("S", cx, cy + r + 18), ("W", cx - r - 26, cy)]:
        c.text(lx - 22, ly - 14, 44, 28, lab, 16, "#5B7A96", align="CENTER",
               bold=True, font=LATIN)
    for i in range(1, 5):
        c.text(cx + 4, cy - r * i / 4 - 16, 80, 20, "%dkm" % (i * 100), 12,
               "#4A6A85", font=LATIN)

    pts = []
    for i in range(80):
        t = i / 79.0
        ang = math.radians(150 + 420 * t)
        rad = 280 * (1 - t) + 18
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang) * 0.82))
    K.polyline(c, pts, 3, "#FBBF24", opacity=0.9)
    for i in (25, 50, 72):
        p1, p2 = pts[i], pts[i + 1]
        ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
        c.arrow_head(p2[0], p2[1], ang, 13, "#FBBF24")
    K.glow(c, pts[-1][0], pts[-1][1], 46, 46, "#F97316", sigma=26, opacity=0.7)
    c.circle(pts[-1][0], pts[-1][1], 16, "#F97316")
    c.circle(pts[-1][0], pts[-1][1], 7, "#FFFFFF")
    c.text(pts[-1][0] + 24, pts[-1][1] - 14, 160, 28, "当前中心", 15, "#FBBF24", bold=True)

    px = 730
    c.rect(px, 160, 310, 700, "#0D2030", radius=14, border="1 SOLID #1D3A52")
    c.text(px + 20, 176, 270, 30, "当前实况 / CURRENT", 15, "#7E9AB5", font=LATIN, bold=True)
    c.text(px + 20, 210, 270, 46, "超强台风级", 28, "#F97316", bold=True)
    items = [("中心气压", "925 hPa"), ("最大风速", "52 m/s"), ("移动方向", "西北偏西"),
             ("移动速度", "18 km/h"), ("七级风圈", "380 km")]
    for i, (k, v) in enumerate(items):
        yy = 274 + i * 54
        c.text(px + 20, yy, 140, 28, k, 15, "#7E9AB5")
        c.text(px + 158, yy, 132, 28, v, 16, "#F8FAFC", align="RIGHT", bold=True, font=LATIN)
        K.rule(c, px + 20, yy + 40, 270, "#173046", 1)

    c.text(px + 20, 566, 270, 28, "预警等级 / SEVERITY", 14, "#7E9AB5", font=LATIN, bold=True)
    scale = ["#3B82F6", "#22C55E", "#FACC15", "#F97316", "#DC2626"]
    for i, col in enumerate(scale):
        c.rect(px + 20 + i * 54, 602, 48, 16, col, radius=3)
    K.triangle(c, [(px + 20 + 3 * 54 + 24, 598), (px + 20 + 3 * 54 + 14, 584),
                   (px + 20 + 3 * 54 + 34, 584)], "#FFFFFF")
    c.text(px + 20, 626, 270, 24, "蓝      黄      橙      红", 13, "#9FB6CC")

    c.text(px + 20, 672, 270, 28, "影响时间轴 / OUTLOOK", 14, "#7E9AB5", font=LATIN, bold=True)
    c.rect(px + 34, 716, 2, 180, "#1D3A52")
    tl = [("现在", "距岸 260 km", "52 m/s"), ("+6h", "距岸 170 km", "50 m/s"),
          ("+12h", "距岸 90 km", "45 m/s"), ("+24h", "登陆 / 减弱", "32 m/s")]
    for i, (t, d, w) in enumerate(tl):
        yy = 716 + i * 44
        c.circle(px + 35, yy + 8, 6, "#F97316" if i < 2 else "#FBBF24")
        c.text(px + 52, yy - 2, 58, 26, t, 15, "#F8FAFC", bold=True, font=LATIN)
        c.text(px + 110, yy - 2, 112, 26, d, 13, "#9FB6CC")
        c.text(px + 222, yy - 2, 68, 26, w, 12, "#F97316", align="RIGHT", font=LATIN)

    c.text(48, 1010, 720, 30, "示意预警图：台风名称、路径与数值均为演示，非真实气象发布。", 15, "#5B7A96")
    c.text(760, 1010, 280, 30, "CIVIL DEFENSE / DEMO", 14, "#5B7A96",
           align="RIGHT", font=LATIN)


# ============================================================ case-06 黑胶唱片
def draw_06(c):
    W, H = 1080, 1080
    c.rect(0, 0, W, H, "#171009")
    K.radial(c, 0, 0, W, H, ["#2A1A0E", "#120C07"], grad_radius=0.9)
    K.glow(c, 410, 470, 330, 330, "#C98A3C", sigma=80, opacity=0.20)
    cx, cy, R = 400, 470, 310
    c.circle(cx, cy, R, "#0C0A08", border="2 SOLID #3A2A18")
    for rr in range(298, 138, -9):
        K.ring(c, cx, cy, rr, rr - 1, "#2A2018", steps=64)
    K.arc(c, cx, cy, 304, 282, -60, 20, "#4A3822", opacity=0.5)
    K.radial(c, cx - 150, cy - 150, 300, 300,
             ["#E8A94B", "#C4702C", "#8A3E1E"], stops=[0, 0.6, 1],
             grad_radius=0.5, corner=150)
    c.text(cx - 130, cy - 108, 260, 40, "SIDE A", 18, "#3A1E0C", align="CENTER",
           bold=True, font=LATIN, spacing=4)
    c.text(cx - 140, cy - 66, 280, 48, "午夜电台", 34, "#2A1408", align="CENTER",
           bold=True, font=SERIF)
    c.circle(cx, cy, 9, "#171009")
    c.circle(cx, cy, 4, "#0A0806")
    c.text(cx - 140, cy + 24, 280, 28, "MIDNIGHT RADIO", 14, "#4A2A12",
           align="CENTER", font=LATIN, spacing=2)
    c.text(cx - 140, cy + 58, 280, 26, "33 1/3 RPM  |  STEREO", 12, "#5A3418",
           align="CENTER", font=LATIN)

    c.line(690, 170, 520, 330, 9, "#B9A98C")
    c.circle(690, 170, 22, "#8A7C64", border="4 SOLID #C9B79A")
    K.rot(c, 490, 316, 70, 34, -38, '<Container color="#D8C7A8" borderRadius="6" />')

    c.text(760, 120, 280, 30, "NOW PLAYING", 14, "#C98A3C", font=LATIN, spacing=3, bold=True)
    c.text(760, 156, 280, 46, "午夜电台", 30, "#F3E3C6", bold=True, font=SERIF)
    c.text(760, 206, 280, 26, "MIDNIGHT RADIO / 2026", 13, "#9A8462", font=LATIN)
    K.rule(c, 760, 246, 280, "#4A3822", 1)
    tracks = [("A1", "开场白 / INTRO", "1:42"), ("A2", "午夜电台", "4:18"),
              ("A3", "雨里的霓虹", "3:56"), ("A4", "旧唱片", "5:02"),
              ("A5", "散场灯 / OUTRO", "2:30")]
    for i, (no, nm, dur) in enumerate(tracks):
        yy = 264 + i * 58
        c.text(760, yy, 40, 28, no, 14, "#C98A3C", bold=True, font=LATIN)
        c.text(804, yy, 176, 28, nm, 16, "#E8D6B8", bold=(i == 1))
        c.text(980, yy, 60, 28, dur, 14, "#9A8462", align="RIGHT", font=LATIN)
        if i < 4:
            K.rule(c, 760, yy + 40, 280, "#332616", 1)
    rnd = random.Random(4)
    for i in range(28):
        h = rnd.uniform(12, 54)
        c.rect(760 + i * 10, 640 - h, 7, h, "#C98A3C", radius=2,
               opacity=round(rnd.uniform(0.45, 1.0), 2))

    K.rule(c, 60, 850, 960, "#4A3822", 1)
    c.text(60, 870, 700, 32, "巷声唱片 / LANEWAY RECORDS  |  LR-026", 16, "#9A8462", font=LATIN)
    c.text(60, 906, 940, 30, "示例唱片卡：曲目、艺人、编号与厂牌均为虚构演示内容。", 15, "#7A6648")
    c.text(60, 948, 940, 40, "PLAY IT LOUD, PLAY IT WARM.", 22, "#C98A3C",
           font=LATIN, spacing=2, bold=True)


# ============================================================ case-07 用药提醒
def draw_07(c):
    W, H = 1080, 1350
    c.rect(0, 0, W, H, "#F2F7F3")
    K.radial(c, 0, 0, W, 440, ["#E4F1E7", "#F2F7F3"], grad_radius=1.0)
    K.linear(c, 0, 0, W, 170, ["#24765A", "#1B5040"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.circle(72, 72, 26, "#FFFFFF")
    c.text(72, 56, 52, 32, "+", 26, "#24765A", align="CENTER", bold=True, font=LATIN)
    c.text(114, 30, 640, 52, "本周用药计划", 40, "#FFFFFF", bold=True)
    c.text(114, 90, 640, 32, "WEEKLY MEDICATION PLAN  /  大字版", 17, "#BFE3D2", font=LATIN)
    c.text(760, 42, 280, 34, "第 45 周", 22, "#FFFFFF", align="RIGHT", bold=True)
    c.text(760, 84, 280, 28, "11/02 - 11/08", 17, "#BFE3D2", align="RIGHT", font=LATIN)
    c.text(48, 190, 960, 30, "为 李奶奶 准备  ·  每日三次，饭后服用", 20, "#3E5B4E", bold=True)

    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    dates = ["2", "3", "4", "5", "6", "7", "8"]
    for i, d in enumerate(days):
        x = 140 + i * 127
        c.rect(x, 236, 119, 50, "#FFFFFF", radius=10, border="1 SOLID #D6E6DA")
        c.text(x, 240, 119, 26, d, 18, "#1E5B47", align="CENTER", bold=True)
        c.text(x, 264, 119, 20, dates[i], 13, "#8AA79A", align="CENTER", font=LATIN)

    meals = [("早", "早餐后", "07:30"), ("午", "午餐后", "12:30"), ("晚", "晚餐后", "19:00")]
    meds = [("#E8734A"), ("#4E8FD1"), ("#7FB069"), ("#B07BC6")]
    for rr, (mk, mn, mt) in enumerate(meals):
        y = 300 + rr * 160
        c.rect(48, y, 84, 140, "#FFFFFF", radius=12, border="1 SOLID #D6E6DA")
        c.text(48, y + 16, 84, 42, mk, 30, "#1E5B47", align="CENTER", bold=True)
        c.text(48, y + 62, 84, 26, mn, 13, "#5E7A6C", align="CENTER")
        c.text(48, y + 96, 84, 24, mt, 14, "#8AA79A", align="CENTER", font=LATIN)
        for i in range(7):
            x = 140 + i * 127
            c.rect(x, y, 119, 140, "#FFFFFF", radius=12, border="1 SOLID #E1EDE4")
            rnd = random.Random(rr * 7 + i + 1)
            picks = [0, 1] if rnd.random() < 0.55 else [0]
            if rr == 0 and i % 3 == 0:
                picks = [0, 2]
            if rr == 2 and i % 2 == 0:
                picks = [1, 3]
            for j, mi in enumerate(picks):
                col = meds[mi]
                px = x + 14 + j * 48
                c.rect(px, y + 26, 38, 18, col, radius=9)
                c.rect(px, y + 26, 19, 18, "#FFFFFF", radius=9, opacity=0.35)
                c.text(px - 2, y + 50, 42, 24, "1粒" if rnd.random() < 0.5 else "2粒",
                       12, "#5E7A6C", align="CENTER")
            c.circle(x + 100, y + 118, 8, "#CFE6D7")

    c.rect(48, 800, 984, 300, "#FFFFFF", radius=16, border="1 SOLID #D6E6DA")
    c.text(72, 816, 600, 36, "药品对照 / MEDICATION KEY", 22, "#1E5B47", bold=True)
    names = [("A", "#E8734A", "降压片", "1 粒 / 早餐后"),
             ("B", "#4E8FD1", "维生素 D", "1 粒 / 午、晚餐后"),
             ("C", "#7FB069", "钙片", "2 粒 / 早餐后"),
             ("D", "#B07BC6", "助眠片", "1 粒 / 睡前")]
    for i, (k, col, nm, dose) in enumerate(names):
        xx = 72 + (i % 2) * 470
        yy = 868 + (i // 2) * 100
        c.rect(xx, yy, 30, 30, col, radius=8)
        c.text(xx, yy - 2, 30, 34, k, 18, "#FFFFFF", align="CENTER", bold=True, font=LATIN)
        c.text(xx + 42, yy - 6, 380, 34, nm, 21, "#234B3C", bold=True)
        c.text(xx + 42, yy + 30, 380, 28, dose, 16, "#6E8A7A")

    c.text(48, 1128, 984, 32, "提醒：饭前 / 饭后以药袋说明为准；如有不适请咨询医师或药师。", 18, "#3E5B4E")
    c.text(48, 1168, 984, 32, "示例内容：人物、药品与剂量均为虚构演示，不构成医嘱。", 17, "#8AA79A")
    K.capsule(c, 48, 1214, 320, 52, "#1E5B47")
    c.text(48, 1216, 320, 48, "家属电话  138-0000-0000", 17, "#FFFFFF", align="CENTER", bold=True)
    c.text(760, 1222, 272, 40, "WEEK 45 / 7 DAYS", 16, "#8AA79A", align="RIGHT", font=LATIN)


# ============================================================ case-08 黑板酒单
def draw_08(c):
    W, H = 1000, 1400
    c.rect(0, 0, W, H, "#16241C")
    K.radial(c, 0, 0, W, H, ["#1D2F24", "#101B14"], grad_radius=0.9)
    K.dot_grid(c, 0, 0, W, H, 58, 0.8, "#3A5241", opacity=0.25)
    c.rect(36, 36, W - 72, H - 72, "#00000000", border="2 SOLID #6E8C73", radius=10, opacity=0.55)
    c.rect(48, 48, W - 96, H - 96, "#00000000", border="1 SOLID #3F5A46", radius=6, opacity=0.6)
    c.text(0, 92, W, 62, "巷口 · TAPROOM", 52, "#F2EEDC", align="CENTER", bold=True, font=SERIF)
    c.text(0, 160, W, 32, "ON TAP  /  今日酒头  ·  NO.08", 18, "#A9C1A8",
           align="CENTER", font=LATIN, spacing=3)
    c.dashed_hline(120, 212, 760, 2, "#6E8C73", dash=12, gap=12)
    K.diamond(c, 500, 212, 9, 9, "#C9D86B")

    taps = [("01", "微醺小猫", "PALE ALE / 淡色艾尔", "4.8", "28", "38"),
            ("02", "雾都列车", "HAZY IPA / 浑浊 IPA", "6.2", "55", "45"),
            ("03", "夜航西飞", "STOUT / 世涛", "5.6", "42", "42"),
            ("04", "白日梦", "WITBIER / 小麦白", "4.5", "15", "38"),
            ("05", "松间月", "PILSNER / 皮尔森", "5.0", "32", "40"),
            ("06", "落日橘", "SOUR / 水果酸啤", "4.2", "10", "46")]
    for i, (no, zh, en, abv, ibu, price) in enumerate(taps):
        y = 250 + i * 130
        if i % 2 == 0:
            c.rect(70, y - 6, 860, 120, "#FFFFFF", radius=8, opacity=0.035)
        c.circle(112, y + 44, 30, "#00000000", border="2 SOLID #C9D86B")
        c.text(112, y + 26, 60, 36, no, 22, "#C9D86B", align="CENTER", bold=True, font=LATIN)
        c.text(162, y + 6, 360, 42, zh, 27, "#F2EEDC", bold=True)
        c.text(162, y + 50, 380, 26, en, 15, "#9FB59C", font=LATIN)
        c.text(560, y + 10, 150, 24, "ABV " + abv + "%", 15, "#D9C98A", font=LATIN)
        c.rect(560, y + 40, 150, 8, "#33483A", radius=4)
        c.rect(560, y + 40, 150 * float(abv) / 8.0, 8, "#C9D86B", radius=4)
        c.text(730, y + 10, 120, 24, "IBU " + ibu, 15, "#D9C98A", font=LATIN)
        c.rect(730, y + 40, 110, 8, "#33483A", radius=4)
        c.rect(730, y + 40, 110 * int(ibu) / 70.0, 8, "#E0952F", radius=4)
        c.text(856, y + 22, 74, 44, "¥" + price, 22, "#F2EEDC", align="RIGHT", bold=True)
        c.rect(70, y + 108, 860, 1, "#3F5A4680")

    c.text(0, 1050, W, 38, "HAPPY HOUR  17:00 - 19:00  ·  第二杯半价", 24,
           "#C9D86B", align="CENTER", bold=True)
    c.dashed_hline(120, 1104, 760, 2, "#6E8C73", dash=12, gap=12)
    K.diamond(c, 500, 1104, 9, 9, "#C9D86B")
    c.text(0, 1140, W, 32, "精酿小馆  ·  每日 16:00 - 24:00  ·  堂饮 / 外带", 18,
           "#9FB59C", align="CENTER")
    c.text(0, 1180, W, 32, "示例菜单：酒款、度数、苦度与价格均为虚构演示。", 16,
           "#6E8C73", align="CENTER")
    K.star(c, 500, 1266, 46, 20, 6, "#3F5A46", rotation=-90)
    c.text(0, 1310, W, 30, "DRINK LOCAL, STAY AWHILE.", 18, "#6E8C73",
           align="CENTER", font=LATIN, spacing=2)


# ============================================================ case-09 观星导览
def draw_09(c):
    W, H = 1200, 1500
    K.radial(c, 0, 0, W, H, ["#182A63", "#080E28"], grad_radius=0.9)
    K.starfield(c, 0, 0, W, H, 260, "#FFFFFF", seed=17, rmin=0.6, rmax=2.4)
    K.starfield(c, 0, 0, W, H, 40, "#9FD8FF", seed=23, rmin=1.4, rmax=3.0, opacity=0.9)
    c.text(60, 56, 800, 56, "今夜观星 · 猎户座", 46, "#EAF2FF", bold=True)
    c.text(60, 118, 800, 32, "TONIGHT'S SKY  /  ORION  /  2026-11-04", 17,
           "#8FA8D8", font=LATIN, spacing=2)
    c.text(880, 68, 260, 42, "21:30", 34, "#FBBF24", align="RIGHT", bold=True, font=LATIN)
    c.text(880, 114, 260, 26, "最佳观测", 16, "#8FA8D8", align="RIGHT")

    stars = {
        "参宿四": (330, 360, "#FF9A6B"), "参宿五": (600, 330, "#BFD4FF"),
        "参宿一": (390, 640, "#FFFFFF"), "参宿二": (460, 650, "#FFFFFF"),
        "参宿三": (530, 660, "#FFFFFF"), "参宿六": (330, 930, "#BFD4FF"),
        "参宿七": (620, 950, "#9FD8FF"),
    }
    lines = [("参宿四", "参宿五"), ("参宿四", "参宿一"), ("参宿五", "参宿三"),
             ("参宿一", "参宿二"), ("参宿二", "参宿三"), ("参宿一", "参宿六"),
             ("参宿三", "参宿七"), ("参宿六", "参宿七")]
    for a, b in lines:
        pa, pb = stars[a][:2], stars[b][:2]
        c.line(pa[0], pa[1], pb[0], pb[1], 2, "#5C78B8", opacity=0.75)
    for nm, (x, y, col) in stars.items():
        K.glow(c, x, y, 16, 16, col, sigma=12, opacity=0.55)
        c.circle(x, y, 6, col)
        c.circle(x, y, 2.4, "#FFFFFF")
        c.text(x + 14, y - 16, 150, 26, nm, 15, "#B9C9EE")

    px = 860
    c.rect(px, 300, 290, 520, "#0E1B40", radius=16, border="1 SOLID #2B4080")
    c.text(px + 20, 316, 250, 30, "观测条件 / CONDITIONS", 14, "#8FA8D8", font=LATIN, bold=True)
    cond = [("观测时间", "21:30-23:00"), ("方位", "东南方 SE"),
            ("地平高度", "42 度"), ("月相", "娥眉月 18%"),
            ("视宁度", "良好 / GOOD"), ("光污染", "Bortle 4")]
    for i, (k, v) in enumerate(cond):
        yy = 358 + i * 56
        c.text(px + 20, yy, 120, 28, k, 15, "#8FA8D8")
        c.text(px + 140, yy, 130, 28, v, 15, "#EAF2FF", align="RIGHT", bold=True)
        K.rule(c, px + 20, yy + 40, 250, "#223463", 1)
    c.circle(px + 145, 726, 34, "#E8E2C8")
    c.circle(px + 163, 718, 29, "#0E1B40")
    c.text(px + 20, 776, 250, 26, "肉眼可见 3 等星以上", 14, "#8FA8D8", align="CENTER")
    c.text(px + 20, 802, 250, 26, "建议双筒望远镜 7x50", 14, "#8FA8D8", align="CENTER")

    K.wave_band(c, 0, 1180, 1200, 1180, 26, 1.6, "#0C1436", thickness=170, phase=0.4)
    K.wave_band(c, 0, 1120, 1200, 1120, 14, 2.4, "#101B48", thickness=220, phase=1.2, opacity=0.85)
    c.text(60, 1096, 400, 30, "东南地平线 / SE HORIZON", 14, "#6E86BE", font=LATIN)
    c.rect(0, 1380, W, 120, "#080E28")
    c.text(60, 1394, 800, 32, "示意星图：星点、方位与观测条件为演示数据，非实时天文数据。", 16, "#6E86BE")
    c.text(60, 1432, 800, 32, "找到腰带三星，向东南抬头 42 度即可定位猎户座。", 17, "#9FB6E6")
    c.text(900, 1398, 240, 40, "ORION / NOV", 16, "#FBBF24", align="RIGHT",
           font=LATIN, spacing=2)


# ============================================================ case-10 捐书书架
def draw_10(c):
    W, H = 1200, 800
    K.linear(c, 0, 0, W, H, ["#FDF6E7", "#F5E8CC"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    K.dot_grid(c, 0, 0, W, H, 62, 1.0, "#E2CFA6", opacity=0.45)
    c.text(50, 32, 800, 52, "为巷口社区图书馆添一本书", 38, "#3E2A18", bold=True)
    c.text(50, 90, 800, 30, "BOOK DRIVE  /  社区捐书计划  ·  第 3 期", 17,
           "#9A7A50", font=LATIN, spacing=1)
    c.text(740, 32, 300, 50, "6,840", 44, "#C05A32", align="RIGHT", bold=True, font=LATIN)
    c.text(740, 86, 300, 26, "/ 10,000 册已募集", 16, "#9A7A50", align="RIGHT")
    K.arc(c, 1090, 76, 42, 32, -90, -90 + 360 * 0.684, "#C05A32")
    K.arc(c, 1090, 76, 42, 32, -90 + 360 * 0.684, 270, "#E6D3AC")
    c.text(1040, 58, 100, 36, "68%", 20, "#C05A32", align="CENTER", bold=True, font=LATIN)

    bookcols = ["#C05A32", "#2E6E8E", "#D9A441", "#5B7F52", "#8A5A9C",
                "#B8724A", "#3E6F7A", "#A8543F", "#6A7FA0"]
    rnd = random.Random(31)
    for s in range(5):
        base = 150 + s * 78
        c.rect(50, base + 62, 1100, 10, "#8A5E38", radius=3)
        c.rect(50, base + 70, 1100, 5, "#6E4726", radius=2)
        x = 64
        while x < 1130:
            bw = rnd.randint(24, 40)
            bh = rnd.randint(30, 58)
            filled = rnd.random() < 0.684
            if filled:
                col = bookcols[rnd.randrange(len(bookcols))]
                c.rect(x, base + 62 - bh, bw, bh, col, radius=2)
                c.rect(x + 2, base + 62 - bh + 4, 2, bh - 8, "#FFFFFF", radius=1, opacity=0.35)
                c.rect(x, base + 62 - bh + 8, bw, 2, "#0000002E")
            else:
                c.rect(x, base + 62 - bh, bw, bh, "#E9D9B8", border="1 SOLID #CBB488", radius=2)
            x += bw + 3

    K.rule(c, 60, 566, 1080, "#D9C39A", 2)
    c.rect(80, 616, 1040, 6, "#E6D3AC", radius=3)
    c.rect(80, 616, 1040 * 0.684, 6, "#C05A32", radius=3)
    ms = [(0, "2,000", "已达成"), (0.30, "5,000", "已达成"),
          (0.684, "6,840", "当前"), (1.0, "10,000", "目标")]
    for f, val, lab in ms:
        x = 80 + 1040 * f
        c.circle(x, 619, 9, "#FFFFFF", border="3 SOLID " + ("#C05A32" if f <= 0.684 else "#B9A278"))
        c.text(x - 70, 576, 140, 26, val, 17, "#3E2A18", align="CENTER", bold=True, font=LATIN)
        c.text(x - 70, 636, 140, 24, lab, 14, "#9A7A50", align="CENTER")

    c.text(60, 684, 420, 26, "已有 428 位邻居参与", 16, "#7A5C38", bold=True)
    for i in range(18):
        c.circle(340 + i * 20, 697, 7, bookcols[i % len(bookcols)], opacity=0.85)
    K.capsule(c, 900, 680, 250, 44, "#C05A32")
    c.text(900, 682, 250, 40, "扫码参与捐书", 18, "#FFFFFF", align="CENTER", bold=True)
    c.text(60, 712, 400, 26, "参与方式", 17, "#7A5C38", bold=True)
    steps = ["带书到巷口社区中心", "前台登记并贴标", "领取手作纪念书签"]
    for i, s in enumerate(steps):
        xx = 60 + i * 370
        c.circle(xx + 16, 754, 14, "#C05A32")
        c.text(xx + 16, 742, 32, 26, str(i + 1), 14, "#FFFFFF", align="CENTER",
               bold=True, font=LATIN)
        c.text(xx + 38, 740, 320, 28, s, 15, "#5E452A")
    c.text(60, 776, 800, 20, "示例公益项目：品牌、募集数值与参与人数均为虚构演示。", 12, "#A88A5E")


# ============================================================ 元数据
CASES = [
    dict(id="case-01", title="滨江公园站 · 实时到站信息牌", W=1600, H=900, draw=draw_01,
         audience="晚高峰在站台候车的通勤乘客", use_context="地铁站台悬挂 LED 屏、约 3–8 米远距离站立观看",
         user_goal="在几十秒内确认下一班车还有几分钟、在哪一站台上车",
         content_basis="自拟站名/线路/时刻，均为演示数据，非实际运营信息",
         visual_intent="深色 LED 点阵质感 + 琥珀色倒计时数字 + 四行分割翻页式信息带",
         dsl_capabilities="Stack/Positioned 绝对布局、Container 圆角与边框、LINEAR 渐变、Opacity、dot_grid 点阵、Text 字距、dashed 线",
         criteria=[("C1", "四条线路行信息完整可辨，倒计时为最醒目元素", "ViewImage 逐行核对"),
                   ("C2", "线路徽标、终点站、站台、到站、状态五列对齐无重叠", "ViewImage 对齐检查"),
                   ("C3", "页脚演示声明可见、无裁切", "ViewImage 底部检查")]),
    dict(id="case-02", title="一滴 DRIP LAB · 手冲配方卡", W=1000, H=1400, draw=draw_02,
         audience="在家用手冲器具冲煮的咖啡爱好者", use_context="竖版卡片贴在咖啡角或 iPad 上近距离阅读",
         user_goal="按参数与注水时序复现一杯风味稳定的咖啡",
         content_basis="自拟品牌、豆况、参数与风味，均为演示数据，非门店产品",
         visual_intent="暖奶油纸张质感 + 四象限风味轮圆弧仪表 + 纵向注水时间轴 + 水量进度条",
         dsl_capabilities="RADIAL 渐变、ClipPath 圆弧(arc)、Container 边框/圆角、Text 富文本、圆角胶囊、dashed/实线分隔",
         criteria=[("C1", "风味轮四段弧与四组标签完整、数值可辨", "ViewImage 检查"),
                   ("C2", "注水时间轴四阶段与参数表无重叠、进度条比例正确", "ViewImage 检查"),
                   ("C3", "演示声明与底部标语完整无裁切", "ViewImage 底部检查")]),
    dict(id="case-03", title="ECHO 回声音乐节 · 霓虹电子票", W=1280, H=720, draw=draw_03,
         audience="入场口的音乐节观众与检票员", use_context="手机屏幕出示或打印的横向电子票、近距离核验",
         user_goal="快速核验场次、区域与票号并撕下副券入场",
         content_basis="自拟音乐节、场次、座位与点阵码（装饰性示意码，非可扫码）",
         visual_intent="近黑底 + 品红/青霓虹光晕 + SVG 凹口票券 + 全息渐变条 + 点阵码",
         dsl_capabilities="RADIAL/LINEAR 渐变、ImageFiltered 光晕、ClipPath SVG 凹口票券、starfield、qr_matrix 点阵、barcode、dashed 撕线",
         criteria=[("C1", "票券左右凹口与霓虹渐变条清晰、主标题完整", "ViewImage 检查"),
                   ("C2", "虚线撕口、点阵码、全息条与票号分区无重叠", "ViewImage 检查"),
                   ("C3", "演示声明可见，明确不可用于入场", "ViewImage 底部检查")]),
    dict(id="case-04", title="城市马拉松 · 配速腕带", W=1800, H=520, draw=draw_04,
         audience="全程马拉松跑者", use_context="超宽长条打印后缠在手腕、跑动中低头扫视",
         user_goal="一眼核对当前公里目标配速、累计用时与海拔起伏",
         content_basis="自拟目标成绩与海拔剖面，均为演示数据",
         visual_intent="超宽腕带形制 + 五色配速分区带 + 海拔面积折线 + 公里刻度与分段计时点",
         dsl_capabilities="LINEAR 渐变、ClipPath 多边形面积图、polyline 折线、圆点刻度、分区色带、弧形进度",
         criteria=[("C1", "五个配速分区与公里刻度覆盖 0–42.195K 且无错位", "ViewImage 检查"),
                   ("C2", "六个分段计时点与其数值对齐、不被裁切", "ViewImage 检查"),
                   ("C3", "海拔曲线与图例、演示声明完整", "ViewImage 检查")]),
    dict(id="case-05", title="台风「海燕」· 路径预警图", W=1080, H=1080, draw=draw_05,
         audience="沿海社区居民与应急值守人员", use_context="社区公告屏/手机推送的方形预警图、中距离阅读",
         user_goal="判断台风当前强度、移动路径与未来 24 小时影响",
         content_basis="自拟台风名、路径、气压与风速，均为演示，非真实气象发布",
         visual_intent="雷达同心环 + 螺旋路径与箭头 + 橙色预警等级标尺 + 实况/时间轴侧栏",
         dsl_capabilities="RADIAL 渐变、ClipPath 同心环(EVEN_ODD)、arrow_head 箭头、ImageFiltered 光晕、polyline 螺旋、三角形标记",
         criteria=[("C1", "雷达四环、方位标与螺旋路径箭头完整", "ViewImage 检查"),
                   ("C2", "当前中心光晕、等级标尺与时间轴四项无重叠", "ViewImage 检查"),
                   ("C3", "演示声明与发布信息完整", "ViewImage 检查")]),
    dict(id="case-06", title="巷声唱片 · 黑胶 Now Playing 卡", W=1080, H=1080, draw=draw_06,
         audience="独立唱片店顾客与黑胶爱好者", use_context="唱片架旁的方形展示卡/社媒方图、近距离观看",
         user_goal="了解正在播放的唱片、曲目与厂牌信息",
         content_basis="自拟厂牌、专辑、曲目与编号，均为虚构演示",
         visual_intent="同心沟纹黑胶 + 径向渐变中心标签 + 旋转唱臂 + 曲目表与动态均衡条",
         dsl_capabilities="RADIAL 渐变、ClipPath 同心环与圆弧、Transform 旋转、ImageFiltered 光晕、polyline 均衡条、富文本",
         criteria=[("C1", "唱片沟纹、中心标签文字与唱臂方向清晰", "ViewImage 检查"),
                   ("C2", "五首曲目与时长对齐、均衡条不遮挡文字", "ViewImage 检查"),
                   ("C3", "厂牌与演示声明完整", "ViewImage 检查")]),
    dict(id="case-07", title="李奶奶的每周药盒 · 用药提醒", W=1080, H=1350, draw=draw_07,
         audience="需按时服药的长者及其照护家属", use_context="贴在冰箱或药盒上的大字竖版卡片、近距离阅读",
         user_goal="确认每天早/午/晚各该吃哪几种药、各几粒",
         content_basis="自拟人物、药品与剂量，均为虚构演示，不构成医嘱",
         visual_intent="柔和薄荷绿 + 7 列 × 3 行网格 + 胶囊药丸图形 + 药品颜色对照表",
         dsl_capabilities="RADIAL/LINEAR 渐变、Container 圆角边框、Opacity 胶囊高光、胶囊标签、网格布局",
         criteria=[("C1", "7 天 × 3 餐网格完整、药丸与剂量可辨", "ViewImage 检查"),
                   ("C2", "药品对照四项与提醒文字无重叠、字号足够大", "ViewImage 检查"),
                   ("C3", "非医嘱声明与家属电话完整", "ViewImage 检查")]),
    dict(id="case-08", title="巷口 TAPROOM · 今日酒头黑板", W=1000, H=1400, draw=draw_08,
         audience="精酿酒吧点单顾客", use_context="吧台上方竖版黑板、约 1–2 米站立阅读",
         user_goal="比较六款酒头的风格、酒精度、苦度与价格后点单",
         content_basis="自拟酒款、ABV/IBU 与价格，均为虚构演示",
         visual_intent="深绿黑板粉笔质感 + 手写式衬线标题 + 六行酒单与 ABV/IBU 迷你条 + 双层粉笔边框",
         dsl_capabilities="RADIAL 渐变、dot_grid 粉笔噪点、dashed 花边、ClipPath 菱形/星形、迷你进度条、Opacity 行底纹",
         criteria=[("C1", "六行酒单名称、风格、ABV/IBU 条与价格完整", "ViewImage 检查"),
                   ("C2", "列对齐、迷你条比例正确、无遮挡", "ViewImage 检查"),
                   ("C3", "Happy Hour 与演示声明完整", "ViewImage 检查")]),
    dict(id="case-09", title="今夜观星 · 猎户座导览卡", W=1200, H=1500, draw=draw_09,
         audience="城市郊区初次观星的亲子/爱好者", use_context="户外手机竖屏或打印导览卡、低光环境近距离阅读",
         user_goal="按图找到猎户座并了解今晚的观测条件",
         content_basis="自拟星点、方位与观测条件，均为演示，非实时天文数据",
         visual_intent="深靛蓝夜空 + 星点/亮星光晕 + 星座连线与星名 + 观测条件侧栏 + 波浪地平线",
         dsl_capabilities="RADIAL 渐变、starfield 星点、ImageFiltered 亮星光晕、polyline 星座连线、wave_band 波浪地平线、月相圆",
         criteria=[("C1", "猎户座七颗主星与连线、星名完整可辨", "ViewImage 检查"),
                   ("C2", "观测条件六项与月相图无重叠", "ViewImage 检查"),
                   ("C3", "非实时天文数据声明与底部说明完整", "ViewImage 检查")]),
    dict(id="case-10", title="社区捐书计划 · 渐满的书架", W=1200, H=800, draw=draw_10,
         audience="社区居民与潜在捐书者", use_context="社区中心墙面横版海报/公众号头图、中距离阅读",
         user_goal="了解募集进度并知道如何参与捐书",
         content_basis="自拟公益项目、募集数值与参与人数，均为虚构演示",
         visual_intent="把 68% 进度转化为「五层书架被彩色书脊逐渐填满」的原创视觉隐喻 + 里程碑轨道 + 参与三步",
         dsl_capabilities="LINEAR 渐变、dot_grid、ClipPath 圆弧进度环、参数化书脊网格、里程碑轨道、胶囊按钮",
         criteria=[("C1", "五层书架与彩色书脊/空位示意清晰，隐喻成立", "ViewImage 检查"),
                   ("C2", "68% 进度环、四个里程碑与数值对齐", "ViewImage 检查"),
                   ("C3", "参与三步、CTA 与演示声明完整无裁切", "ViewImage 检查")]),
]
