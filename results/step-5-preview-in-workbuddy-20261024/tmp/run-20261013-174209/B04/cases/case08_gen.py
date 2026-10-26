#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-08 雨层云 Nimbostratus (Ns) 图鉴页（1080×1350，4:5 图鉴体例）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
形成机制、与层云之别）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
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
    T("08", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("雨层云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Nimbostratus · Ns ｜ 中云族 ｜ 可贯穿三层", M + 64, 92, 620, 26, 16,
      INK_DIM, nodes=n)
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_MID}" borderRadius="17"/></Positioned>')
    T("中云族 · 地表–3 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
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
             f'height="{ph * 0.26}"><Container width="{CW}" '
             f'height="{ph * 0.26:.1f}" color="{ZENITH}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.26}" width="{CW}" '
             f'height="{ph * 0.30}"><Container width="{CW}" '
             f'height="{ph * 0.30:.1f}" color="{SKY_HI}"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.56}" width="{CW}" '
             f'height="{ph * 0.44:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.44:.1f}" color="#7E93A6" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="transparent" borderRadius="16" '
             f'border="1 SOLID #FFFFFF30"/></Positioned>')

    ax_x = M + CW - 96
    n.extend(alt_axis(ax_x, py + 26, ph - 78, 10.0,
                      ticks=(2, 4, 6, 8, 10), label_size=11,
                      color="#DCE8F2"))
    # 雨层云云底：地表–3 km（常用范围，CIMO）
    n.extend(range_bar(ax_x + 12, py, 14, ph, 0.0, 3.0, 10.0,
                       "#FFFFFF55", ax_x, ph - 78))

    # —— 插画①：暗灰雨幕 + 连续雨幡（左上）——
    n.append(f'<Positioned left="{M + 60}" top="{py + 52}" width="430" '
             f'height="70"><Container width="430" height="70" '
             f'color="#5E7285" borderRadius="12"/></Positioned>')
    n.append(f'<Positioned left="{M + 76}" top="{py + 58}" width="398" '
             f'height="22"><Container width="398" height="22" '
             f'color="#6E8194" borderRadius="11"/></Positioned>')
    # 连续降水幡（praecipitatio，密而连续）
    for i in range(16):
        rx = M + 78 + i * 26
        n.extend(polyline([(rx, py + 122), (rx - 9, py + 208)], 1.8,
                          "#8FA5B8"))
    T("praecipitatio 连续降水幡（雨或雪）", M + 60, py + 216, 430, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画②：云底碎雨云 pannus（右上）——
    for i, (fx, fw) in enumerate([(0.02, 0.20), (0.26, 0.24), (0.54, 0.18),
                                  (0.76, 0.22)]):
        n.append(f'<Positioned left="{M + 520 + 330 * fx:.2f}" '
                 f'top="{py + 150 + 12 * (i % 2)}" '
                 f'width="{330 * fw:.2f}" height="26">'
                 f'<Container width="{330 * fw:.2f}" height="26" '
                 f'color="#4A5C6E" borderRadius="13"/></Positioned>')
    T("pannus 碎雨云：云底下散乱云块", M + 520, py + 200, 400, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画③：日轮被完全遮住（右上小图）——
    n.append(f'<Positioned left="{M + 700}" top="{py + 60}" width="90" '
             f'height="90"><Container width="90" height="90" '
             f'shape="CIRCLE" color="transparent" '
             f'border="2 SOLID #E8E2CF40"/></Positioned>')
    n.append(f'<Positioned left="{M + 726}" top="{py + 86}" width="38" '
             f'height="4"><Container width="38" height="4" '
             f'color="#E8E2CF80" borderRadius="2"/></Positioned>')
    T("日轮完全不可辨", M + 660, py + 156, 180, 18, 11, "#EAF1F7",
      "CENTER", nodes=n)

    # —— 插画④：底部注记 ——
    T("暗灰云层，厚到完全遮住太阳；常带来连续性雨或雪；云底随降水降低",
      M + 60, py + 260, 700, 40, 11.5, "#EAF1F7", "LEFT", nodes=n)
    T("示意图（DSL 绘制，非照片）", M + 620, py + ph - 40, 300, 20, 11.5,
      "#C4D2DE", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与降水"),
        (684, 276, "与层云的分别"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="14" '
                 f'border="1 SOLID #E3DAC6"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12.5, ACCENT,
          "LEFT", "BOLD", nodes=n)

    T("常用范围", M + 16, dy + 42, 150, 20, 12, INK_DIM, "LEFT", nodes=n)
    T("地表–3 km", M + 16, dy + 62, 200, 28, 20, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("地表–10 000 ft", M + 16, dy + 90, 190, 18, 11.5, INK_DIM,
      "LEFT", "NORMAL", MONO, nodes=n)
    T("天气图上视为中云；可延伸至其他层；云底随降水持续降低",
      M + 200, dy + 62, 340, 40, 11, INK_DIM, "LEFT", nodes=n)

    T("连续性雨或雪", M + 400, dy + 42, 260, 40, 14, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("暗灰云层弥散于降水之中；厚到完全遮住日轮；云底常有散乱碎云",
      M + 400, dy + 84, 260, 32, 10.5, INK_DIM, "LEFT", nodes=n)

    T("以降水区分", M + 700, dy + 42, 250, 40, 13, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("与层云外形相似，但层云不产生持续降水；有持续降水即为雨层云",
      M + 700, dy + 88, 250, 30, 10.5, INK_DIM, "LEFT", nodes=n)

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
        ("变种 varieties · 无", ["（ICA 未列变种）", "—", "—", "—"]),
        ("附属/从属 · 3", ["virga 幡状云（下垂不落地）",
                           "praecipitatio 降水幡（抵达地面）",
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
    tips_l = ["由增厚的高层云发展而来，或发展盛的积雨云铺展增厚而成",
              "云底随降水持续降低——常被误认为低云（天气图上视为中云）",
              "与层云之别：以是否产生持续降水区分"]
    tips_r = ["日轮完全不可辨（高层云尚可辨磨砂轮廓）",
              "云底常见散乱碎雨云（pannus），有时与云底合并",
              "雨层云与高层云都可延伸至高层——定层不能只凭云底"]
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
    T("nimbus = 降雨", M + 20, ey + 34, 430, 26, 16, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("nimbus/nimbo = 降雨；stratus 表「平展层」——雨层云即「会下雨的层」",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("暗灰幕 + 持续降水 + 日轮全遮 → 雨层云；日月如磨砂玻璃 → 高层云；"
      "均匀层无持续降水 → 层云", M + 510, ey + 34, 440, 44, 12.5, INK_TXT,
      "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 雨层云页 · S4 CIMO 表 15-1 · S5 NOAA JetStream · "
             "S6 香港天文台《云》电子书",
             "08 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
