#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-01 特辑总览：十属三层垂直剖面（1920×1080，16:9 信息图）。

数据来源（sources.json）：
- S1 WMO ICA 表 6：三层高度（极地/温带/热带）
- S4 WMO CIMO Guide 表：十属云底高度常用/更宽范围（温带，台站 ≤150 m）
- S3 WMO 2017：拉丁词根、跨层例外
- S5 NOAA JetStream：高中低分组
插画为 DSL 风格化示意图（非照片）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b04_common import (  # noqa: F403
    T, snapshot, rect, circle, hline, vline, polyline, grad,
    ZENITH, SKY_HI, SKY_MID, SKY_LOW, HORIZON, CLOUD, CLOUD_DIM,
    CLOUD_SHADE, CLOUD_DARK, INK_TXT, INK_DIM, ACCENT, GOLD, MONO,
    SERIF, INTER, SANS, WARN,
    cirrus_wisp, cc_grains, veil, sun_disk, ac_rows, rain_streaks,
    pannus_rags, sc_field, stratus_blanket, cumulus_heap, cb_tower,
)

W, H = 1920, 1080

# 垂直轴：0–18 km，y=150(18km) … y=1000(0km)
AX_X = 74
Y0, Y18 = 1000.0, 150.0
PXKM = (Y0 - Y18) / 18.0


def yy(km: float) -> float:
    return Y18 + (18.0 - km) * PXKM


def dsl() -> str:
    n = []
    # ---- 天空底（对流层顶深蓝 → 地平线灰白）----
    n.append(grad(0, 0, W, H, [ZENITH, "#24486E", SKY_HI, SKY_MID, SKY_LOW,
                               HORIZON],
                  stops=[0, 0.22, 0.45, 0.62, 0.82, 1.0],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))
    # ---- 标题 ----
    T("抬头读天", 60, 34, 420, 52, 40, "#FFFFFF", "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("国际云图集 · 十属三层垂直剖面", 62, 90, 560, 26, 17, "#D9E4EC",
      spacing=2, nodes=n)
    T("WMO International Cloud Atlas — 10 genera, 3 levels",
      1180, 44, 680, 24, 14, "#B9C9D8", "RIGHT", spacing=1, nodes=n)
    T("示意图 · 云底高度为温带常用范围（观测站 ≤150 m AMSL）",
      1180, 74, 680, 22, 12, "#9FB4C6", "RIGHT", nodes=n)

    # ---- 层面带（温带：高 5–13 / 中 2–7 / 低 0–2 km）----
    n.append(rect(96, yy(13), W - 260, yy(5) - yy(13), "#FFFFFF16"))
    n.append(rect(96, yy(7), W - 260, yy(2) - yy(7), "#FFFFFF12"))
    n.append(rect(96, yy(2), W - 260, yy(0) - yy(2), "#FFFFFF20"))
    T("高云族 5–13 km", 108, yy(9.0) - 12, 150, 22, 14, "#E8F0F6", "LEFT",
      "BOLD", nodes=n)
    T("中云族 2–7 km", 108, yy(4.5) - 12, 150, 22, 14, "#E8F0F6", "LEFT",
      "BOLD", nodes=n)
    T("低云族 0–2 km", 108, yy(1.0) - 10, 150, 20, 13, "#E8F0F6", "LEFT",
      "BOLD", nodes=n)

    # ---- 高度轴 ----
    n.append(vline(AX_X, Y18, Y0 - Y18, "#E8F0F6", 1.4))
    for t in range(0, 19, 2):
        ty = yy(t)
        n.append(hline(AX_X - 5, ty, 10, "#E8F0F6", 1.2))
        T(str(t), AX_X - 52, ty - 9, 40, 18, 12, "#E8F0F6", "RIGHT",
          "NORMAL", MONO, nodes=n)
    T("km", AX_X - 52, Y18 - 26, 40, 18, 12, "#E8F0F6", "RIGHT", "NORMAL",
      MONO, nodes=n)
    # 地平线
    n.append(hline(96, Y0, W - 260, "#D7E0E7", 2.0))

    # ---- 云属芯片 ----
    def chip(x, y, w, h, icon, cn, en_abbr, base, level_cn):
        n.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
                 f'height="{h:.2f}"><Container width="{w:.2f}" '
                 f'height="{h:.2f}" color="#1B3A5AD9" borderRadius="14" '
                 f'border="1 SOLID #FFFFFF40"/></Positioned>')
        n.extend(icon)
        T(cn, x + 14, y + h - 62, w - 28, 24, 19, "#FFFFFF", "LEFT", "BOLD",
          SERIF, nodes=n)
        T(en_abbr, x + 14, y + h - 38, w - 28, 18, 12, "#B9C9D8", "LEFT",
          "NORMAL", INTER, spacing=1, nodes=n)
        T(f"云底 {base}｜{level_cn}", x + 14, y + h - 20, w - 28, 16, 11,
          "#D9E4EC", "LEFT", "NORMAL", MONO, nodes=n)

    # 高云族三属（y 400–560）
    chip(260, 396, 250, 158,
         cirrus_wisp(280, 412, 210, 66, "#F2F7FA", n=6, seed=3),
         "卷云", "Cirrus · Ci", "6–12 km", "高")
    chip(545, 396, 250, 158,
         cc_grains(573, 414, 196, 60, cols=9, rows=3, seed=9),
         "卷积云", "Cirrocumulus · Cc", "6–12 km", "高")
    chip(830, 396, 250, 158,
         veil(858, 416, 190, 40, "#E4EDF3") + sun_disk(953, 442, 30,
                 "#F7E9C4", halo=True, halo_r=40),
         "卷层云", "Cirrostratus · Cs", "6–12 km", "高")

    # 中云族三属（y 690–848）
    chip(260, 686, 250, 158,
         ac_rows(282, 704, 206, 62, cols=6, rows=2, seed=5),
         "高积云", "Altocumulus · Ac", "2–6 km", "中")
    chip(545, 686, 250, 158,
         veil(573, 706, 190, 44, "#C9D6E0") + sun_disk(668, 728, 26,
                 "#E9E2CF"),
         "高层云", "Altostratus · As", "2–6 km", "中")
    chip(830, 686, 250, 158,
         veil(856, 700, 198, 40, "#A9BAC7") + rain_streaks(860, 740, 190,
                 24, n=7) + pannus_rags(862, 766, 186, 12),
         "雨层云", "Nimbostratus · Ns", "地表–3 km", "中·可贯穿三层")

    # 低云族四属（y 895–995，紧凑芯片）
    def chip_low(x, y, w, h, icon, cn, en_abbr, base):
        n.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
                 f'height="{h:.2f}"><Container width="{w:.2f}" '
                 f'height="{h:.2f}" color="#1B3A5AD9" borderRadius="12" '
                 f'border="1 SOLID #FFFFFF40"/></Positioned>')
        n.extend(icon)
        T(cn, x + 12, y + 62, 140, 24, 18, "#FFFFFF", "LEFT", "BOLD", SERIF,
          nodes=n)
        T(en_abbr, x + 12, y + 90, w - 24, 16, 10.5, "#B9C9D8", "LEFT",
          "NORMAL", INTER, nodes=n)
        T(f"云底 {base}", x + 12, y + 108, w - 24, 16, 10.5, "#D9E4EC",
          "LEFT", "NORMAL", MONO, nodes=n)

    chip_low(260, 880, 210, 130,
             stratus_blanket(272, 896, 110, 34, "#C3CEDA"),
             "层云", "Stratus · St", "地表–0.6 km")
    chip_low(505, 880, 210, 130,
             sc_field(517, 898, 110, 34, cols=4, rows=2, seed=11),
             "层积云", "Stratocumulus · Sc", "0.3–1.35 km")
    chip_low(750, 880, 210, 130,
             cumulus_heap(764, 896, 70, 34, seed=7),
             "积云", "Cumulus · Cu", "0.3–1.5 km")
    def cb_glyph(x, y, w, h):
        g = []
        aw = w * 1.18
        g.append(rect(x - (aw - w) / 2, y + 2, aw, h * 0.20, CLOUD, radius=6))
        g.append(rect(x + w * 0.18, y + h * 0.26, w * 0.64, h * 0.32,
                      CLOUD, radius=6))
        g.append(rect(x + w * 0.26, y + h * 0.52, w * 0.48, h * 0.24,
                      CLOUD_SHADE, radius=5))
        for i in range(3):
            rx = x + w * (0.30 + 0.20 * i)
            g.extend(polyline([(rx, y + h * 0.80), (rx - 3, y + h * 0.99)],
                              1.6, "#7C93A8"))
        return g

    chip_low(995, 880, 210, 130,
             cb_glyph(1012, 898, 84, 36),
             "积雨云", "Cumulonimbus · Cb", "0.6–1.5 km")

    # ---- 右侧：积雨云塔剪影（贯穿三层）----
    n.extend(cb_tower(1330, 210, 210, 780))
    T("积雨云塔：云底在低层，", 1330, 1010, 300, 20, 12.5, "#E8F0F6",
      "LEFT", nodes=n)
    T("顶部可达中、高层", 1330, 1030, 300, 20, 12.5, "#E8F0F6", "LEFT",
      nodes=n)

    # ---- 右侧面板：三纬度层面高度（ICA 表 6）----
    px, py = 1620, 150
    n.append(f'<Positioned left="{px}" top="{py}" width="240" height="300" '
             f'><Container width="240" height="300" color="#12283FD9" '
             f'borderRadius="14" border="1 SOLID #FFFFFF40"/></Positioned>')
    T("三个纬度的层面高度", px + 16, py + 14, 210, 22, 15, "#FFFFFF",
      "LEFT", "BOLD", SERIF, nodes=n)
    T("（WMO 国际云图集 表 6）", px + 16, py + 38, 210, 16, 10.5, "#9FB4C6",
      nodes=n)
    rows = [("", "极地", "温带", "热带"),
            ("高云族", "3–8", "5–13", "6–18"),
            ("中云族", "2–4", "2–7", "2–8"),
            ("低云族", "0–2", "0–2", "0–2")]
    for ri, row in enumerate(rows):
        ry = py + 62 + ri * 34
        for ci, cell in enumerate(row):
            cx = px + 16 + ci * 54
            if ci == 0:
                T(cell, cx, ry, 52, 20, 11.5, "#D9E4EC", "LEFT",
                  "BOLD" if ri else "NORMAL", nodes=n)
            else:
                T(cell, cx, ry, 52, 20, 11.5, "#FFFFFF", "RIGHT", "NORMAL",
                  MONO, nodes=n)
        if ri:
            n.append(hline(px + 16, ry - 6, 208, "#FFFFFF30", 0.8))
    T("单位：km", px + 16, py + 200, 208, 16, 10.5, "#9FB4C6", "RIGHT",
      nodes=n)

    # 跨层例外
    n.append(f'<Positioned left="{px}" top="{py + 320}" width="240" '
             f'height="190"><Container width="240" height="190" '
             f'color="#12283FD9" borderRadius="14" border="1 SOLID '
             f'#FFFFFF40"/></Positioned>')
    T("跨层例外", px + 16, py + 334, 208, 22, 15, "#FFFFFF", "LEFT", "BOLD",
      SERIF, nodes=n)
    exc = ["高层云常向上延伸更高",
           "雨层云通常贯穿三层",
           "积云/积雨云顶部可达中高层"]
    for i, e in enumerate(exc):
        T("· " + e, px + 16, py + 364 + i * 40, 208, 36, 11.5, "#D9E4EC",
          "LEFT", nodes=n)

    # 拉丁词根
    n.append(f'<Positioned left="{px}" top="{py + 530}" width="240" '
             f'height="220"><Container width="240" height="220" '
             f'color="#12283FD9" borderRadius="14" border="1 SOLID '
             f'#FFFFFF40"/></Positioned>')
    T("名字里的拉丁词根", px + 16, py + 544, 208, 22, 15, "#FFFFFF",
      "LEFT", "BOLD", SERIF, nodes=n)
    roots = [("cirrus/cirro", "羽毛·丝缕"),
             ("cumulus/cumulo", "堆积·蓬松"),
             ("stratus/strato", "平展·层状"),
             ("nimbus/nimbo", "降雨"),
             ("alto", "中层")]
    for i, (a, b) in enumerate(roots):
        T(a, px + 16, py + 574 + i * 30, 100, 18, 11, GOLD, "LEFT",
          "BOLD", INTER, nodes=n)
        T(b, px + 116, py + 574 + i * 30, 110, 18, 11, "#D9E4EC", "LEFT",
          nodes=n)

    # ---- 页脚 ----
    n.append(hline(60, 1058, W - 120, "#FFFFFF40", 1.0))
    T("来源：S1 WMO 国际云图集（层面高度 表 6）｜S4 WMO CIMO Guide 第 15 章"
      "（云底高度范围）｜S3 WMO 2017（词根与例外）｜S5 NOAA JetStream（分组）",
      60, 1066, 1200, 18, 10.5, "#B9C9D8", nodes=n)
    T("抬头读天 · 国际云图集十属  01 / 11", W - 460, 1066, 400, 18, 10.5,
      "#B9C9D8", "RIGHT", nodes=n)

    return snapshot(W, H, n, ZENITH)


if __name__ == "__main__":
    out = dsl()
    if WARN:
        print("WARN:", WARN)
    print("nodes ok, dsl bytes:", len(out.encode("utf-8")))
