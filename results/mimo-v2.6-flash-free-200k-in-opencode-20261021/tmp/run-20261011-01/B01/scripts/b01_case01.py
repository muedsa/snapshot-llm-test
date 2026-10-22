# -*- coding: utf-8 -*-
"""B01 case-01 · 汛眼 · 城市内涝值班图板 (1600x1100 dark command board).

Audience: 市防汛办值班员. Goal: 10 分钟内决定封路顺序与泵车派往。
Elements: 12 监测点积水深度排序条带 + 阈值线、3 处下穿隧道剖面风险卡、
泵车调度、处置规则条。数据全部自拟虚构。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b01_common as B  # noqa: E402

W, H = 1600, 1100
BG = "#0B1220"
PANEL = "#111C2E"
INK = "#E8EEF9"
MUTED = "#93A4BC"
CYAN = "#38BDF8"
RED = "#F04438"
ORANGE = "#F59E0B"
YELLOW = "#EAB308"
BLUE = "#3B82F6"
GREEN = "#34D399"

# 12 监测点（虚构演示数据）: name, depth_cm, trend(+1/-1/0), district
PTS = [
    ("人民路下穿隧道", 86, +1, "老城区"),
    ("解放桥泵站前", 62, +1, "桥东区"),
    ("火车站南广场", 55, 0, "站前区"),
    ("体育馆东路口", 48, +1, "新城南"),
    ("滨河路隧道", 41, -1, "滨江区"),
    ("东风渠桥下", 33, 0, "桥西区"),
    ("老城十字街", 27, 0, "老城区"),
    ("兴华路涵洞", 22, +1, "兴华区"),
    ("青年桥北", 18, 0, "桥东区"),
    ("五里亭路口", 12, 0, "城北区"),
    ("西关立交下", 9, -1, "西郊区"),
    ("站前北巷", 5, 0, "站前区"),
]


def sev(d):
    if d >= 80:
        return RED, "封路"
    if d >= 50:
        return ORANGE, "警戒"
    if d >= 30:
        return YELLOW, "关注"
    return BLUE, "正常"


TR = {1: "▲涨", -1: "▼退", 0: "—平"}


def main():
    els = []
    # ---------- header ----------
    els.append(B.grad_rect(0, 0, W, 6, "#38BDF8,#818CF8,#22D3EE",
                           "TOP_LEFT", "TOP_RIGHT"))
    els.append(B.text_el(40, 26, 360, 40, "汛眼 · 城市排水指挥", 26, CYAN,
                         bold=True))
    els.append(B.text_el(400, 22, 620, 48, "内涝风险值班图板", 34, INK,
                         bold=True))
    els.append(B.text_el(1030, 24, 350, 40, "2026-07-18 21:40 (+08:00)", 22,
                         MUTED, align="RIGHT"))
    els.append(B.chip_el(1400, 24, 160, 44, "#3B1010", "Ⅱ级响应", 24, RED,
                         radius=8, border="#7F1D1D", border_w=2))
    els.append(B.line_h(90, 40, 1560, "#1E2C44", 1))

    # ---------- left: 12 monitoring points ----------
    els.append(B.rect_at(40, 116, 968, 784, PANEL, radius=14))
    els.append(B.text_el(64, 136, 600, 36, "监测点积水深度排序", 26, INK,
                         bold=True))
    els.append(B.text_el(664, 142, 320, 28, "单位 cm · 21:40 实测", 20,
                         MUTED, align="RIGHT"))
    X0, BW = 340, 450          # bar track x0 / width (=100cm)
    TH = BW / 100.0
    # threshold guide lines 30 / 50 / 80
    for tv, tc in ((30, YELLOW), (50, ORANGE), (80, RED)):
        els.append(B.line_v(X0 + tv * TH, 186, 882, tc + "55", 1))
        els.append(B.text_el(X0 + tv * TH - 40, 180, 80, 24,
                             "%dcm" % tv, 17, tc, align="CENTER"))
    y = 204
    for name, d, tr, dist in PTS:
        c, lvl = sev(d)
        els.append(B.text_el(64, y + 2, 240, 30, name, 21, INK))
        els.append(B.text_el(64, y + 30, 240, 22, dist, 17, MUTED))
        els.append(B.rect_at(X0, y + 4, BW, 26, "#0C1626", radius=6))
        els.append(B.rect_at(X0, y + 4, d * TH, 26, c, radius=6))
        els.append(B.text_el(800, y + 2, 80, 30, "%d" % d, 24, c,
                             bold=True, align="RIGHT"))
        els.append(B.text_el(888, y + 6, 52, 26, TR[tr], 19, MUTED))
        els.append(B.chip_el(944, y + 2, 60, 28, "#0C1626", lvl,
                             17, c, radius=6, border=c, border_w=1))
        y += 54
    els.append(B.text_el(64, 858, 500, 26,
                         "阈值：≥80 封路 · 50–79 警戒 · 30–49 关注", 18, MUTED))

    # ---------- right: 3 tunnel cross sections + pump dispatch ----------
    els.append(B.text_el(1040, 130, 520, 34, "下穿隧道剖面 · 封路判定", 26,
                         INK, bold=True))
    tun = [
        ("人民路下穿隧道", 86, 6.2, "立即封路", RED),
        ("解放桥下穿段", 62, 5.0, "预警封控", ORANGE),
        ("火车站南通道", 55, 4.5, "预警封控", ORANGE),
    ]
    ty = 180
    for name, d, deep, act, c in tun:
        els.append(B.rect_at(1040, ty, 520, 176, PANEL, radius=14))
        els.append(B.text_el(1064, ty + 14, 320, 30, name, 22, INK, bold=True))
        els.append(B.chip_el(1380, ty + 14, 156, 32, "#0C1626", act, 19, c,
                             radius=6, border=c, border_w=1))
        # cross-section: box 472x92, water = d/100 of full height (满幅100cm)
        cx0, cy0, cw, ch = 1064, ty + 56, 472, 92
        els.append(B.rect_at(cx0, cy0, cw, ch, "#0A1322", radius=8,
                             border="#24344F", border_w=2))
        wh = d / 100.0 * ch
        els.append(B.grad_rect(cx0 + 2, cy0 + ch - wh - 2, cw - 4, wh,
                               "#1D4ED8,#38BDF8", "TOP_LEFT", "TOP_LEFT",
                               radius=6))
        els.append(B.text_el(cx0 + 14, cy0 + ch - wh + 4, 300, 26,
                             "积水 %dcm" % d, 19, "#EAF4FF", bold=True))
        els.append(B.text_el(cx0, ty + 150, cw, 24,
                             "路面以下 %.1fm 深 · 满幅剖面计 %d%%" % (deep, d),
                             18, "#C8D6EA"))
        ty += 192

    # pump dispatch
    els.append(B.rect_at(1040, 764, 520, 136, "#0F2032", radius=14,
                         border="#1E3A5F", border_w=2))
    els.append(B.text_el(1064, 778, 300, 30, "泵车调度（2 台在役）", 22, CYAN,
                         bold=True))
    els.append(B.text_el(1064, 814, 480, 28,
                         "泵车 A · 1200m³/h → 人民路下穿（22:00 前到场）",
                         19, INK))
    els.append(B.text_el(1064, 848, 480, 28,
                         "泵车 B · 800m³/h → 解放桥（22:10 前到场）", 19, INK))
    els.append(B.text_el(1064, 880, 480, 24, "增援：城管仓库待命 1 台",
                         18, MUTED))

    # ---------- bottom: rules ----------
    els.append(B.rect_at(40, 924, 1520, 140, "#0F1A2C", radius=14))
    rules = [
        ("封路顺序", "① 人民路下穿 → ② 解放桥 → ③ 火车站南\n匝道口提前 200m 设锥桶"),
        ("上报规则", "深度 30 分钟内涨 ≥20cm 即报带班领导\nⅡ级响应每 30 分钟滚动通报"),
        ("安全底线", "巡检员不下穿作业，水深 >30cm 撤离\n封路确认后回传现场照片"),
    ]
    rx = 72
    for title, body in rules:
        els.append(B.rect_at(rx, 948, 4, 92, CYAN, radius=2))
        els.append(B.text_el(rx + 18, 948, 200, 30, title, 21, CYAN,
                             bold=True))
        for i, ln in enumerate(body.split("\n")):
            B.fit(ln, 18, 420)
            els.append(B.text_el(rx + 18, 982 + i * 30, 440, 28, ln, 18,
                                 MUTED))
        rx += 506

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-01-%s.snapshot" % ver)
    B.emit(os.path.normpath(out), body, W, H, BG)


if __name__ == "__main__":
    main()
