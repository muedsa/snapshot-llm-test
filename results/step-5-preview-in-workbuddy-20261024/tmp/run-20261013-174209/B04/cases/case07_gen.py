#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-07 高层云 Altostratus (As) 图鉴页（1080×1350，4:5 图鉴体例）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
磨砂玻璃日面、无晕无影、夜间惯例）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b04_common import (  # noqa: F403
    T, snapshot, rect, circle, hline, vline, polyline, grad,
    ZENITH, SKY_HI, SKY_MID, SKY_LOW, HORIZON, CLOUD, CLOUD_DIM,
    CLOUD_SHADE, CLOUD_DARK, INK_TXT, INK_DIM, ACCENT, ACCENT_SOFT, GOLD,
    MONO, SERIF, INTER, SANS, PAPER_WARM, WARN,
    alt_axis, range_bar, foot_bar,
)

W, H = 1080, 1350
M = 60
CW = W - 2 * M


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("07", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("高层云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Altostratus · As ｜ 中云族 ｜ 水滴 + 冰晶", M + 64, 92, 620, 26, 16,
      INK_DIM, nodes=n)
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_MID}" borderRadius="17"/></Positioned>')
    T("中云族 · 2–7 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
      "CENTER", "BOLD", nodes=n)
    T("抬头读天 · 国际云图集十属", W - M - 300, 92, 300, 22, 12, "#98A6B2",
      "RIGHT", nodes=n)
    n.append(hline(M, 126, CW, "#D8CFBB", 1.2))

    # ================= 主图 =================
    py, ph = 142, 420
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="{SKY_MID}" borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph * 0.30}"><Container width="{CW}" '
             f'height="{ph * 0.30:.1f}" color="{ZENITH}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.30}" width="{CW}" '
             f'height="{ph * 0.34}"><Container width="{CW}" '
             f'height="{ph * 0.34:.1f}" color="{SKY_HI}"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.64}" width="{CW}" '
             f'height="{ph * 0.36:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.36:.1f}" color="{SKY_MID}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="transparent" borderRadius="16" '
             f'border="1 SOLID #FFFFFF30"/></Positioned>')

    ax_x = M + CW - 96
    n.extend(alt_axis(ax_x, py + 26, ph - 78, 10.0,
                      ticks=(2, 4, 6, 8, 10), label_size=11,
                      color="#DCE8F2"))
    n.extend(range_bar(ax_x + 12, py, 14, ph, 2.0, 6.0, 10.0,
                       "#FFFFFF55", ax_x, ph - 78))

    # —— 插画①：灰蓝云幕 + 磨砂玻璃日面（左上）——
    n.append(f'<Positioned left="{M + 60}" top="{py + 56}" width="420" '
             f'height="132"><Container width="420" height="132" '
             f'color="#8FA5B8" borderRadius="14"/></Positioned>')
    # 厚薄不匀致亮度差（三条亮带）
    for i, (by, bh, cc) in enumerate([(64, 16, "#A9BCC9"), (96, 22,
                                                            "#B7C7D3"),
                                       (136, 10, "#9FB2C0")]):
        n.append(f'<Positioned left="{M + 76}" top="{py + by}" '
                 f'width="388" height="{bh}"><Container width="388" '
                 f'height="{bh}" color="{cc}" borderRadius="7"/>'
                 f'</Positioned>')
    # 纤维状条纹（striated）
    for i in range(7):
        sy = py + 66 + i * 18
        pts = [(M + 80 + 390 * k / 24, sy + 4 * math.sin(k * 0.9 + i))
               for k in range(25)]
        n.extend(polyline(pts, 1.2, "#C9D6E055"))
    # 磨砂玻璃日面（模糊轮廓、无锐边）
    n.append(circle(M + 210, py + 122, 30, "#E8E2CF"))
    n.append(f'<Positioned left="{M + 180}" top="{py + 92}" width="60" '
             f'height="60"><Container width="60" height="60" '
             f'shape="CIRCLE" color="transparent" '
             f'border="2 SOLID #E8E2CF40"/></Positioned>')
    T("ground-glass sun 磨砂玻璃日面", M + 60, py + 200, 420, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画②：幡状云 + 碎雨云（右上）——
    for i in range(5):
        vx = M + 540 + i * 52
        n.extend(polyline([(vx, py + 70), (vx - 7, py + 122)], 1.8,
                          "#7E93A6"))
    for i, (fx, fw) in enumerate([(0.0, 0.22), (0.28, 0.26), (0.62, 0.24),
                                  (0.82, 0.16)]):
        n.append(f'<Positioned left="{M + 520 + 330 * fx:.2f}" '
                 f'top="{py + 140 + 10 * (i % 2)}" '
                 f'width="{330 * fw:.2f}" height="22">'
                 f'<Container width="{330 * fw:.2f}" height="22" '
                 f'color="#5E7285" borderRadius="11"/></Positioned>')
    T("virga 幡状云 + pannus 碎雨云", M + 520, py + 186, 400, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画③：底部注记 ——
    T("灰或蓝灰色云幕，纹状、纤维状或均匀；可全扫或部分蔽天；不产生晕",
      M + 60, py + 250, 700, 40, 11.5, "#EAF1F7", "LEFT", nodes=n)
    T("示意图（DSL 绘制，非照片）", M + 620, py + ph - 40, 300, 20, 11.5,
      "#C4D2DE", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与日面"),
        (684, 276, "与雨层云的分辨"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="14" '
                 f'border="1 SOLID #E3DAC6"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12.5, ACCENT,
          "LEFT", "BOLD", nodes=n)

    T("常用范围", M + 16, dy + 42, 150, 20, 12, INK_DIM, "LEFT", nodes=n)
    T("2–6 km", M + 16, dy + 62, 170, 28, 20, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("6 500–20 000 ft", M + 16, dy + 90, 190, 18, 11.5, INK_DIM,
      "LEFT", "NORMAL", MONO, nodes=n)
    T("更宽范围：—（与高积云共用合并单元格；增厚伴云底降低可发展成雨层云）",
      M + 200, dy + 56, 340, 48, 11, INK_DIM, "LEFT", nodes=n)

    T("日面如磨砂玻璃", M + 400, dy + 42, 260, 40, 14, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("薄处隐约可见日轮轮廓；无晕；地面不见物影；厚薄不均可致幕面亮度差异",
      M + 400, dy + 84, 260, 32, 10.5, INK_DIM, "LEFT", nodes=n)

    T("日/月轮廓可辨 → 高层云", M + 700, dy + 42, 250, 40, 13, INK_TXT,
      "LEFT", "BOLD", nodes=n)
    T("夜间无雨雪时，As/Ns 难辨按惯例记为高层云", M + 700, dy + 88, 250,
      30, 10.5, INK_DIM, "LEFT", nodes=n)

    # ================= 种 / 变种 / 附属 =================
    ly, lh = 726, 300
    n.append(f'<Positioned left="{M}" top="{ly}" width="{CW}" '
             f'height="{lh}"><Container width="{CW}" height="{lh}" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{ly}" width="6" height="{lh}">'
             f'<Container width="6" height="{lh}" color="{ACCENT}" '
             f'borderRadius="3"/></Positioned>')
    T("WMO ICA 分类（种 → 变种 → 附属/从属）", M + 26, ly + 18, 620, 26,
      17, INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("引自香港天文台《云》电子书（转引 WMO 国际云图集）；中文为通行译名，"
      "英文为 ICA 原名", M + 26, ly + 48, 700, 20, 11, "#98A6B2",
      "LEFT", nodes=n)

    cols = [
        ("种 species · 无", ["（ICA 未列种）", "—", "—", "—"]),
        ("变种 varieties · 5", ["translucidus 透光高层云",
                                "opacus 荫光高层云",
                                "duplicatus 复高层云（叠置两层）",
                                "undulatus 波状 / radiatus 辐辏状"]),
        ("附属/从属 · 4", ["mamma 乳状云 / virga 幡状云",
                           "praecipitatio 降水幡（可达地面）",
                           "pannus 碎雨云", "—"]),
    ]
    for i, (ct, items) in enumerate(cols):
        cx0 = M + 26 + i * 306
        T(ct, cx0, ly + 82, 280, 22, 13.5, ACCENT, "LEFT", "BOLD",
          nodes=n)
        for j, it in enumerate(items):
            T(("· " + it) if it != "—" else it, cx0, ly + 110 + j * 26,
              290, 24, 12, INK_TXT if it != "—" else "#B9C4CE",
              "LEFT", nodes=n)

    # ================= 观测提示 =================
    wy = 1048
    n.append(f'<Positioned left="{M}" top="{wy}" width="{CW}" '
             f'height="150"><Container width="{CW}" height="150" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{wy}" width="6" height="150">'
             f'<Container width="6" height="150" color="{SKY_MID}" '
             f'borderRadius="3"/></Positioned>')
    T("观测提示（只引来源结论）", M + 26, wy + 16, 500, 24, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    tips_l = ["日月轮廓隐约可辨（磨砂玻璃感）→ 高层云而非雨层云",
              "无晕、地面无物影——与卷层云的两条硬边界",
              "厚薄不匀时幕面亮度不均；云底较不均匀"]
    tips_r = ["有时下垂幡状云（virga），偶尔抵达地面致极弱降水",
              "由高层云继续增厚、云底降低可发展成雨层云",
              "夜间难辨 As/Ns 时：无雨雪按惯例记为高层云"]
    for j, t in enumerate(tips_l):
        T("· " + t, M + 26, wy + 48 + j * 28, 460, 26, 12, INK_DIM,
          "LEFT", nodes=n)
    for j, t in enumerate(tips_r):
        T("· " + t, M + 500, wy + 48 + j * 28, 440, 26, 12, INK_DIM,
          "LEFT", nodes=n)

    # ================= 词根 + 易混判别 =================
    ey = 1218
    n.append(f'<Positioned left="{M}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="{SKY_MID}1A" borderRadius="14" '
             f'border="1 SOLID {SKY_MID}55"/></Positioned>')
    T("拉丁词根", M + 20, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("alto- + stratus = 中层 + 平展层", M + 20, ey + 34, 430, 26, 16,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("alto 原意为「高」，此处表「中层」（与高层的卷层云、低层的层云相别）",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("灰幕 + 日月如磨砂玻璃可辨 → 高层云；完全蔽天且持续降水 → 雨层云；"
      "薄幕见晕 → 卷层云", M + 510, ey + 34, 440, 44, 12.5, INK_TXT,
      "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 高层云页 · S4 CIMO 表 15-1 · S5 NOAA JetStream · "
             "S6 香港天文台《云》电子书",
             "07 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
