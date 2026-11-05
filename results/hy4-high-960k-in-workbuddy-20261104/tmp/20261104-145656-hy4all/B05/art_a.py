#!/usr/bin/env python3
"""B05 cases 01-05: brand poster, live map, route decision, on-road alert, rider view."""
from __future__ import annotations
import math, sys, os
from pathlib import Path
sys.path.insert(0, os.environ["TOOLS"])
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dsl import Canvas, LATIN, CN, MONO
import dslx as X
from common import DATA, A, label, rule, dot

D = DATA


def case_01():
    """Brand concept poster: water-level rings over a flooded skyline."""
    W = H = 1200
    c = Canvas(W, H, "#050D1A")
    X.gradient(c, 0, 0, W, H, ["#14527A", "#0A2340", "#050D1A"],
               gtype="RADIAL", center="CENTER", grad_radius=0.9)
    X.gradient(c, 160, 40, 880, 560, ["#1E6FA0", "#0A2340"],
               gtype="RADIAL", center="CENTER", grad_radius=0.9, opacity=0.30)

    # concentric water-level rings + ticks
    for ro, ri, col, op in [(344, 340, "#38BDF8", 0.34), (302, 296, "#22D3EE", 0.26),
                            (252, 250, "#38BDF8", 0.18), (206, 204, "#22D3EE", 0.14)]:
        X.donut(c, 600, 420, ro, ri, col, opacity=op)
    X.ring_ticks(c, 600, 420, 336, 320, [i * 15 for i in range(24)], "#2E5A7E", 2)

    # skyline (kept BEHIND the gauge)
    BASE = 690
    heights = [150, 224, 118, 286, 190, 244, 108, 306, 168, 214, 262, 132, 232, 158, 272, 142]
    for i, h in enumerate(heights):
        x = 36 + i * 74
        c.rect(x, BASE - h, 58, h, "#0B2138")
        for r in range(18, h - 10, 30):
            c.hline(x + 9, BASE - h + r, 40, 2, "#1D4E74")
    # water line + waves
    c.hline(0, BASE, W, 3, "#38BDF8")
    X.wave(c, 0, BASE, W, 180, "#22D3EE", amp=22, waves=5, baseline=16, opacity=0.30)
    X.wave(c, 0, BASE + 16, W, 164, "#0EA5E9", amp=18, waves=6, baseline=28, opacity=0.20)
    c.hline(0, 870, W, 2, "#1E5A7E")

    # centre gauge drawn LAST so the skyline cannot cover the number
    c.circle(600, 420, 150, "#071A2E", opacity=0.96)
    X.donut(c, 600, 420, 152, 148, "#38BDF8", opacity=0.55)
    X.arc(c, 600, 420, 138, 120, -90, 180, "#F59E0B", opacity=0.95)
    X.arc(c, 600, 420, 138, 120, 180, 270, "#16314B", opacity=0.9)
    c.text(490, 306, 220, 34, "当前最深积水", 18, "#8FB8DC", align="CENTER")
    c.text(470, 340, 260, 120, "45", 104, "#FFFFFF", bold=True, align="CENTER", font=LATIN)
    c.text(500, 458, 200, 32, "cm · 已封控", 19, "#FBBF24", align="CENTER")
    c.text(460, 494, 280, 30, "江汉路地铁 B 口", 17, "#9FC4E8", align="CENTER")

    # top bar
    c.text(66, 44, 620, 40, "ANCHOR  ·  城市暴雨安全同伴", 22, "#9FC4E8", bold=True)
    c.text(600, 44, 300, 40, "2026.07.12  临江市", 19, "#7FA3C9", align="RIGHT", font=MONO)
    X.chip(c, 920, 42, 214, 42, "暴雨红色预警", "#B91C1C", "#FFFFFF", 18, radius=21)

    # title block
    c.text(66, 884, 300, 196, "泊", 150, "#F8FAFC", bold=True)
    c.text(322, 940, 700, 76, "A N C H O R", 44, "#7DD3FC", bold=True, font=LATIN, spacing=6)
    c.text(68, 1086, 940, 46, "暴雨里，知道哪条路还走得通。", 29, "#DCEBFA")

    # bottom capability chips
    for i, (t, w) in enumerate([("积水地图", 176), ("路线重规划", 176), ("分级预警", 176)]):
        X.chip(c, 66 + i * 192, 1140, w, 44, t, "#123A5E", "#BFE3FF", 18,
               radius=22, border="1 SOLID #2B6C9B")
    c.text(760, 1140, 374, 44, "众包上报 + 6 个液位计", 18, "#7FA3C9", align="RIGHT", font=MONO)

    meta = dict(id="case-01", title="水位之上 · 品牌概念主视觉",
                audience="第一次听说「泊」的临江市民、应用商店访客、社区宣传栏读者",
                use_context="1200×1200 方形海报，手机应用商店头图 / 社区公告栏 / 发布会主视觉",
                user_goal="在几秒内理解「泊」是做什么的、为什么暴雨天需要它",
                content_basis="虚构产品「泊 / ANCHOR」与虚构城市「临江市」；45cm 为演示水位",
                visual_intent="以同心水位环 + 城市天际线 + 贯穿的水位线建立原创视觉隐喻；中央仪表盘给出可信数据锚点",
                dimensions=[W, H],
                dsl_capabilities="RADIAL 渐变、ClipPath donut 双圆 EVEN_ODD 镂空、A 弧扇段仪表、C 三次贝塞尔波浪、ring_ticks 刻度、Opacity、chip、大字 letterSpacing",
                scenario="品牌认知：让人第一次理解产品的存在与价值")
    return c.render(), meta


def case_02():
    """Phone home: full-screen live flood-risk map with a glass bottom sheet."""
    W, H = 760, 1520
    c = Canvas(W, H, "#06121E")
    # dark map base
    c.rect(0, 0, W, H, "#071624")
    X.gradient(c, 0, 0, W, H, ["#0A2136", "#06101C"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    # street grid
    for gx in range(40, W, 96):
        c.line(gx, 0, gx + 46, H, 3, "#12293F")
    for gy in range(150, H, 120):
        c.line(0, gy, W, gy - 30, 3, "#12293F")
    for gx in range(40, W, 192):
        c.line(gx, 0, gx + 92, H, 6, "#173A55")
    # river band
    X.clip(c, 0, 760, W, 190,
           "M0 60 C 160 10 300 130 460 70 C 600 20 680 110 760 60 L760 190 L0 190 Z",
           "#0C3350", opacity=0.85)
    c.text(28, 790, 300, 28, "临江 / 水位上涨", 16, "#4E8BB5", font=MONO)

    # risk blobs
    blobs = [(196, 360, 132, "#22C55E", 0.16), (560, 470, 156, "#F59E0B", 0.20),
             (300, 690, 178, "#EF4444", 0.22), (600, 880, 120, "#22C55E", 0.14),
             (170, 980, 110, "#EAB308", 0.16)]
    for bx, by, r, col, op in blobs:
        c.circle(bx, by, r, col, opacity=op)
        c.circle(bx, by, r * 0.55, col, opacity=op * 1.3)

    # point markers with labels
    pts = [
        (300, 690, "江汉路 B 口", "45cm", "#EF4444", -1),
        (560, 470, "光谷环岛", "28cm", "#F59E0B", 1),
        (196, 360, "建设大道", "8cm", "#22C55E", 1),
        (170, 980, "梧桐里东门", "12cm", "#EAB308", -1),
        (600, 880, "沿江公园", "5cm", "#22C55E", 1),
    ]
    for px, py, name, cm, col, side in pts:
        c.circle(px, py, 13, col, border="3 SOLID #FFFFFF")
        c.circle(px, py, 4, "#FFFFFF")
        lw = 182
        lx = px + 22 if side > 0 else px - 22 - lw
        lx = max(10, min(lx, W - lw - 10))
        c.rect(lx, py - 20, lw, 40, "#0B1E31", radius=10,
               border="1 SOLID " + A(col, 0.8))
        c.text(lx + 8, py - 18, lw - 16, 22, name, 16, "#FFFFFF", bold=True)
        c.text(lx + 8, py + 2, lw - 16, 18, cm + " · 实时", 14, "#DCEBFA", font=LATIN)

    # status bar / search
    c.rect(0, 0, W, 92, "#081726", opacity=0.92)
    c.text(28, 22, 300, 34, "临江市  ·  17:46", 21, "#EAF4FF", bold=True)
    X.chip(c, 552, 24, 180, 40, "红色预警", "#B91C1C", "#FFFFFF", 17, radius=20)
    c.rect(28, 108, 704, 60, "#10263C", radius=16, border="1 SOLID #24527A")
    c.circle(62, 138, 11, "#7DD3FC", border="2 SOLID #7DD3FC")
    c.line(70, 146, 78, 154, 2, "#7DD3FC")
    c.text(96, 118, 500, 40, "搜索地点 / 上报一处积水", 20, "#9FC4E8")

    # glass bottom sheet (blurred background copy, sharp text on top)
    bg = ('<Container width="704" height="330" color="#0C2136" />'
          '<Positioned left="-24" top="-10" width="72" height="350"><Container color="#1D6E96" /></Positioned>'
          '<Positioned left="656" top="-10" width="72" height="350"><Container color="#7A4A12" /></Positioned>')
    X.blur_card(c, 28, 1088, 704, 330, bg, sigma=8, radius=26,
                border="1 SOLID #FFFFFF33")
    c.text(52, 1102, 656, 36, "你在 云枢大厦 · 江汉路", 24, "#FFFFFF", bold=True)
    c.text(52, 1138, 656, 26, "附近 3 处积水 · 2 处已封控", 17, "#BBD8F2")
    rule(c, 52, 1174, 656, "#33506E", 1)
    rows = [("江汉路地铁 B 口", "45cm 封控", "#EF4444"),
            ("梧桐里东门", "12cm 可通行", "#EAB308"),
            ("建设大道", "8cm 通畅", "#22C55E")]
    for i, (n, s, col) in enumerate(rows):
        yy = 1188 + i * 48
        c.circle(66, yy + 18, 7, col)
        c.text(86, yy, 360, 36, n, 19, "#E8F3FC")
        c.text(452, yy, 252, 36, s, 18, col, align="RIGHT", bold=True)
    c.rect(52, 1340, 656, 60, "#0EA5E9", radius=14)
    c.text(52, 1340, 656, 60, "查看回家路线  →", 23, "#042033",
           bold=True, align="CENTER")

    # bottom nav
    c.rect(0, 1436, W, 84, "#081726")
    navs = ["地图", "路线", "上报", "我的"]
    for i, n in enumerate(navs):
        cx = 95 + i * 190
        col = "#38BDF8" if i == 0 else "#5A7695"
        c.rect(cx - 16, 1452, 32, 26, col, radius=7, opacity=0.9)
        c.text(cx - 60, 1482, 120, 28, n, 16, col, align="CENTER")

    meta = dict(id="case-02", title="此刻的城市 · 实时积水地图首页",
                audience="临江市通勤者林岚，17:46 下班前查看全城积水",
                use_context="760×1520 竖屏手机 App 首页，单手握持、户外强光下快速扫视",
                user_goal="一眼看清全城哪些路段积水、自己附近风险如何",
                content_basis="虚构演示：6 个监测点水位与风险分级，数值与 case-03/08 一致",
                visual_intent="全屏深色地图 + 彩色风险热力晕 + 毛玻璃底部浮层，营造「实时态势」沉浸感",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 渐变、c.line 街道网格、ClipPath C 曲线河道、Opacity 热力晕、ClipRRect+ImageFiltered 毛玻璃浮层、chip、圆角卡片",
                scenario="态势感知：打开 App 后第一屏，理解「现在城市怎么样」")
    return c.render(), meta


def case_03():
    """Route decision: three comparable route cards + one clear recommendation."""
    W, H = 760, 1460
    c = Canvas(W, H, "#EEF3FA")
    c.rect(0, 0, W, 210, "#102A46")
    X.gradient(c, 0, 0, W, 210, ["#123A5E", "#0C2038"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.text(40, 26, 680, 30, "17:46  ·  暴雨红色预警", 18, "#8FC7F0", font=MONO)
    c.text(40, 62, 680, 62, "回家，走哪条路？", 40, "#FFFFFF", bold=True)
    c.text(40, 130, 680, 34, "云枢大厦 · 江汉路  →  梧桐里", 21, "#BBD8F2")
    # origin/destination strip
    c.circle(66, 186, 9, "#38BDF8")
    c.text(86, 172, 240, 30, "17:46 出发", 17, "#CDE5FA")
    c.line(76, 186, 684, 186, 2, "#3E6E96")
    c.circle(684, 186, 9, "#34D399")
    c.text(430, 172, 240, 30, "梧桐里 预计 18:17", 17, "#CDE5FA", align="RIGHT")

    for i, r in enumerate(D["routes"]):
        y = 236 + i * 272
        best = r["best"]
        c.rect(36, y, 688, 244, "#FFFFFF" if not best else "#EAF7F0", radius=20,
               border=("3 SOLID #16A34A" if best else "1 SOLID #D5E0EE"),
               shadow="0 6 18 0 #173A5A22 NORMAL")
        c.rect(36, y, 8, 244, "#16A34A" if best else "#94A9C2", radius=4)
        c.text(62, y + 18, 440, 40, r["name"], 25, "#0F2942", bold=True)
        X.chip(c, 560, y + 20, 140, 38,
               "推荐" if best else r["risk"] + "风险",
               "#16A34A" if best else ("#FEE2E2" if r["risk"] == "高" else "#E0F2FE"),
               "#FFFFFF" if best else ("#B91C1C" if r["risk"] == "高" else "#075985"),
               17, radius=19)
        # mini path
        py = y + 92
        c.line(70, py, 690, py, 3, "#C9D8E8")
        for j, xx in enumerate([70, 260, 450, 690]):
            c.circle(xx, py, 9, "#16A34A" if best else "#64748B")
        for j in range(r["water"]):
            c.circle(360 + j * 150, py, 15, "#EF4444", opacity=0.85)
            c.text(348 + j * 150, py + 16, 40, 20, "水", 14, "#B91C1C", align="CENTER")
        c.text(70, py + 22, 300, 26, r["via"], 16, "#5B708C")
        # metrics
        mx = [70, 280, 490]
        vals = [("%d 分钟" % r["mins"]), ("%d 处积水" % r["water"]),
                ("风险 " + r["risk"])]
        caps = ["预计用时", "途经积水", "综合评级"]
        for k in range(3):
            c.text(mx[k], y + 150, 200, 36, vals[k], 23,
                   "#0F2942" if k == 0 else ("#B91C1C" if (k == 2 and r["risk"] == "高") else "#1D4E74"),
                   bold=True, font=LATIN if k == 0 else None)
            c.text(mx[k], y + 186, 200, 24, caps[k], 15, "#7C90A8")
        c.text(62, y + 214, 620, 26, r["note"], 17,
               "#166534" if best else "#6B7E96")

    # decision bar
    c.rect(36, 1070, 688, 330, "#0B2541", radius=22)
    X.gradient(c, 36, 1070, 688, 330, ["#103B62", "#0A2240"],
               gtype="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT", radius=22)
    c.text(64, 1092, 632, 34, "泊 的建议", 19, "#7DD3FC", bold=True, font=MONO)
    c.text(64, 1130, 632, 66, "走路线 B", 46, "#FFFFFF", bold=True)
    c.text(64, 1200, 632, 80,
           "梧桐里东门 12cm 可通行。比最快路线多 9 分钟，"
           "但避开 45cm 已封控的江汉路 B 口。",
           21, "#CDE5FA")
    c.rect(64, 1300, 632, 72, "#22D3EE", radius=16)
    c.text(64, 1300, 632, 72, "开始导航  ·  预计 18:17 到家", 24, "#042033",
           bold=True, align="CENTER")

    meta = dict(id="case-03", title="三条路，怎么走 · 出门决策卡",
                audience="准备从公司回家的通勤者林岚",
                use_context="760×1460 竖屏手机，室内/地铁口短暂停留时做一次决策",
                user_goal="在 3 条路线中选出安全可通行的一条并直接开始导航",
                content_basis="虚构演示：3 条路线用时/积水点/风险，与 case-02/08 的水位一致",
                visual_intent="浅色卡片对比清单，用等宽三列指标并列比较，推荐项用绿色描边与角标突出，底部深色结论条收束决策",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 渐变头部与结论条、boxShadow 卡片投影、圆角卡片、迷你路径 line/circle、chip 状态标签、富层级文字",
                scenario="决策：把「哪条路走得通」从猜测变成一次可比较的选择")
    return c.render(), meta


def case_04():
    """On-road alert: extreme minimal, one huge number, one action."""
    W, H = 700, 1400
    c = Canvas(W, H, "#B91C1C")
    X.gradient(c, 0, 0, W, H, ["#F97316", "#DC2626", "#7F1D1D"],
               gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER",
               stops=[0, 0.42, 1])
    # faint rings
    for ro, ri, op in [(300, 297, 0.18), (240, 238, 0.14), (180, 178, 0.10)]:
        X.donut(c, 350, 540, ro, ri, "#FFFFFF", opacity=op)

    c.text(48, 46, 420, 34, "泊  ·  途中预警", 21, "#FFE4D6", bold=True, font=MONO)
    X.chip(c, 520, 44, 132, 38, "红色", "#FFFFFF", "#B91C1C", 18, radius=19)
    c.text(48, 100, 604, 30, "17:52  ·  距你约 300 米", 19, "#FFE4D6")

    c.text(48, 300, 604, 44, "前方路段积水", 26, "#FFF1E8", align="CENTER")
    c.text(48, 348, 604, 250, "45", 220, "#FFFFFF", bold=True,
           align="CENTER", font=LATIN)
    c.text(495, 476, 150, 76, "cm", 44, "#FFE4D6", bold=True,
           align="CENTER", font=LATIN)
    c.text(48, 608, 604, 44, "江汉路地铁 B 口  ·  已封控", 26, "#FFFFFF",
           bold=True, align="CENTER")

    # horizontal water-level ruler
    RX, RY, RW = 70, 748, 560
    c.text(70, 700, 360, 28, "水位标尺 / 通行参考", 17, "#FFE4D6", font=MONO)
    c.rect(RX, RY, RW * 0.25, 26, "#22C55E", radius=6)
    c.rect(RX + RW * 0.25, RY, RW * 0.25, 26, "#EAB308")
    c.rect(RX + RW * 0.50, RY, RW * 0.50, 26, "#7F1D1D")
    for cm in (0, 15, 30, 45, 60):
        xx = RX + RW * cm / 60
        c.rect(xx - 1, RY - 12, 2, 50, "#FFFFFF", opacity=0.8)
        c.text(xx - 34, RY + 34, 68, 24, "%d" % cm, 16, "#FFE4D6",
               align="CENTER", font=LATIN)
    mx = RX + RW * 45 / 60
    c.poly([(mx, RY - 26), (mx - 13, RY - 48), (mx + 13, RY - 48)], "#FFFFFF")
    c.text(mx - 70, RY - 88, 140, 30, "45cm", 20, "#FFFFFF",
           bold=True, align="CENTER", font=LATIN)
    c.text(70, 826, 560, 28, "超过 30cm 禁止通行 · 已由 3 位邻居上报 + P2 液位计确认",
           16, "#FFE4D6")

    # actions
    c.rect(70, 1000, 560, 92, "#FFFFFF", radius=20)
    c.text(70, 1000, 560, 92, "改走梧桐里东门（12cm）", 27, "#B91C1C",
           bold=True, align="CENTER")
    c.rect(70, 1112, 560, 84, "#FFFFFF00", radius=20, border="2 SOLID #FFFFFF")
    c.text(70, 1112, 560, 84, "查看附近避难点", 24, "#FFFFFF",
           bold=True, align="CENTER")
    c.text(70, 1230, 560, 30, "预计为你多花 9 分钟，避开 45cm 封控点",
           18, "#FFE4D6", align="CENTER")
    c.text(70, 1320, 560, 26, "ANCHOR · 临江市 2026.07.12", 15, "#FFD9C7",
           align="CENTER", font=MONO)

    meta = dict(id="case-04", title="前方 300 米 · 45 厘米 · 途中预警",
                audience="正走在回家路上的林岚，手机锁屏 / 通知横幅",
                use_context="700×1400 竖屏极简锁屏通知，雨中单手、强光、只有 2 秒注意力",
                user_goal="立刻知道前方路不能走，并一键改道",
                content_basis="虚构演示：江汉路 B 口 45cm 封控，与 case-01/02/03/08 一致",
                visual_intent="整屏橙红渐变 + 一个 220px 的巨大数字 + 一条水位标尺，把信息压缩到单一焦点与单一动作",
                dimensions=[W, H],
                dsl_capabilities="LINEAR 三段渐变+gradientStops、donut 低透明度光环、ClipPath 三角形指针、Opacity、大字拉丁数字、圆角按钮",
                scenario="状态突变：途中收到封控预警，必须立刻改道")
    return c.render(), meta


def case_05():
    """Rider view: wide landscape, high-contrast amber/black, order risk overlay."""
    W, H = 1440, 900
    c = Canvas(W, H, "#0B0C10")
    # top bar
    c.rect(0, 0, W, 76, "#14161C")
    c.text(36, 18, 420, 40, "ANCHOR  ·  骑手版", 24, "#FBBF24", bold=True, font=MONO)
    c.text(470, 20, 420, 36, "周骁  /  R-2087", 20, "#C9D2DE")
    X.chip(c, 1200, 16, 204, 44, "在线 · 3 单", "#A3E635", "#10240A", 19, radius=22)

    # left map
    c.rect(28, 100, 924, 728, "#10131A", radius=18)
    for gx in range(60, 950, 92):
        c.line(gx, 110, gx + 40, 820, 2, "#1E2532")
    for gy in range(140, 830, 96):
        c.line(28, gy, 950, gy - 26, 2, "#1E2532")
    c.line(28, 470, 950, 420, 7, "#2A3342")
    # risky zone
    c.circle(560, 360, 190, "#EF4444", opacity=0.16)
    c.circle(560, 360, 110, "#EF4444", opacity=0.18)
    c.circle(560, 360, 13, "#EF4444", border="3 SOLID #FFFFFF")
    c.text(590, 330, 300, 30, "江汉路 B 口 45cm", 19, "#FCA5A5", bold=True)
    c.text(590, 360, 300, 26, "封控 · 建议绕行", 16, "#F87171")
    # safe detour
    pts = [(120, 700), (250, 640), (360, 600), (470, 540), (560, 470),
           (700, 470), (820, 430), (900, 360)]
    X.polyline(c, pts, 5, "#A3E635")
    for x, y in (pts[0], pts[-1]):
        c.circle(x, y, 10, "#A3E635")
    c.text(96, 716, 260, 28, "起点 · 梧桐里站", 17, "#D9F99D")
    c.text(760, 330, 190, 28, "终点 · 云枢", 17, "#D9F99D")
    c.text(48, 786, 500, 26, "荧光绿 = 系统推荐绕行路线（避开 45cm 封控点）",
           16, "#8FA07A", font=MONO)

    # right column
    c.text(990, 104, 420, 40, "接单前看一眼", 30, "#FFFFFF", bold=True)
    c.text(990, 156, 420, 26, "当前 17:46 · 降雨峰值 17:40–19:20", 16, "#8B98AB")
    c.text(990, 200, 260, 96, "2 / 3", 78, "#FBBF24", bold=True, font=LATIN)
    c.text(1230, 232, 180, 44, "单需绕行", 22, "#E5E9F0", bold=True)

    # time window band
    c.text(990, 306, 420, 28, "风险时间窗", 18, "#8B98AB", font=MONO)
    BX, BY, BW = 990, 342, 420
    c.rect(BX, BY, BW, 40, "#1B2029", radius=8)
    c.rect(BX, BY, BW * 0.55, 40, "#B91C1C", radius=8)
    c.rect(BX + BW * 0.55, BY, BW * 0.45, 40, "#166534", radius=8)
    for i, t in enumerate(["18:00", "18:30", "19:00", "19:30", "20:00"]):
        xx = BX + BW * i / 4
        c.text(xx - 34, BY + 48, 68, 24, t, 15, "#9AA7B8",
               align="CENTER", font=LATIN)
    c.text(990, 418, 420, 26, "18:00–19:10 高风险   ·   19:10 后趋于安全",
           16, "#D6BFA0")

    # conclusion card
    c.rect(990, 462, 420, 96, "#FBBF24", radius=14)
    c.text(1010, 474, 380, 72, "建议 18:10 后再接\n江汉路方向订单", 23, "#1A1206",
           bold=True)

    # order list
    orders = [("#1042", "云枢大厦", "可送达", "#A3E635"),
              ("#1043", "江汉路 B 口", "需绕行", "#FBBF24"),
              ("#1044", "光谷环岛", "需绕行", "#FBBF24")]
    for i, (code, dest, st, col) in enumerate(orders):
        yy = 582 + i * 76
        c.rect(990, yy, 420, 66, "#161A22", radius=12, border="1 SOLID #262C38")
        c.text(1008, yy + 8, 140, 28, code, 19, "#FFFFFF", bold=True, font=MONO)
        c.text(1008, yy + 36, 240, 24, dest, 16, "#9AA7B8")
        X.chip(c, 1240, yy + 15, 150, 36, st, A(col, 0.18), col, 16, radius=18)

    c.text(36, 852, 1368, 28,
           "数据来自 6 个液位计 + 38 条众包上报  ·  17:46 更新  ·  虚构演示",
           16, "#6C7787", font=MONO)

    meta = dict(id="case-05", title="接单前的风险叠加 · 骑手横屏视图",
                audience="外卖骑手周骁，电动车支架上的横屏设备",
                use_context="1440×900 横屏车载/支架，骑行中高震动、强光、需高对比一眼可读",
                user_goal="接单前判断哪些订单会被积水阻断、什么时候再接更安全",
                content_basis="虚构演示：3 单、2 单需绕行、风险时间窗；水位与前面各画面一致",
                visual_intent="黑底 + 琥珀黄与荧光绿高对比；左地图右分栏，风险时间窗用红/绿横向色带表达",
                dimensions=[W, H],
                dsl_capabilities="line 街道网格、Opacity 风险晕、polyline 折线路径、chip 状态标签、8 位色透明度、横向色带、大数字",
                scenario="职业场景：同一产品为不同角色提供不同媒介与信息优先级")
    return c.render(), meta


CASES = {1: case_01, 2: case_02, 3: case_03, 4: case_04, 5: case_05}
