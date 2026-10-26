#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 卷积云 Cirrocumulus (Cc) 图鉴页（1080×1350，4:5 图鉴体例）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
易混规则）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
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
    alt_axis, range_bar, foot_bar, cc_grains,
)

W, H = 1080, 1350
M = 60
CW = W - 2 * M


def cc_sheet(x: float, y: float, w: float, h: float, cols: int, rows: int,
             r_min: float, r_max: float, color: str = "#F4F8FB",
             seed: int = 5) -> list[str]:
    """卷积云粒：按行列排布的极小云粒（无阴影、白色）。"""
    import random
    rnd = random.Random(seed)
    out = []
    for r in range(rows):
        for c in range(cols):
            gx = x + w * (c + 0.5) / cols
            gy = y + h * (r + 0.5) / rows
            d = r_min + (r_max - r_min) * rnd.random()
            out.append(circle(gx, gy, d, color))
    return out


def cc_lacunosis(x: float, y: float, w: float, h: float) -> list[str]:
    """网状卷积云 lacunosus：粒群 + 规则圆孔（孔内透出天色）。"""
    out = []
    out.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
               f'height="{h:.2f}"><Container width="{w:.2f}" '
               f'height="{h:.2f}" color="#E4EDF4" '
               f'borderRadius="12"/></Positioned>')
    for r in range(3):
        for c in range(5):
            hx = x + w * (0.1 + 0.2 * c)
            hy = y + h * (0.17 + 0.33 * r)
            d = min(w, h) * 0.10
            out.append(f'<Positioned left="{hx - d / 2:.2f}" '
                       f'top="{hy - d / 2:.2f}" width="{d:.2f}" '
                       f'height="{d:.2f}"><Container width="{d:.2f}" '
                       f'height="{d:.2f}" shape="CIRCLE" '
                       f'color="{SKY_HI}"/></Positioned>')
    return out


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("04", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("卷积云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Cirrocumulus · Cc ｜ 高云族 ｜ 冰晶云", M + 64, 92, 600, 26, 16,
      INK_DIM, nodes=n)
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_HI}" borderRadius="17"/></Positioned>')
    T("高云族 · 5–13 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
      "CENTER", "BOLD", nodes=n)
    T("抬头读天 · 国际云图集十属", W - M - 300, 92, 300, 22, 12, "#98A6B2",
      "RIGHT", nodes=n)
    n.append(hline(M, 126, CW, "#D8CFBB", 1.2))

    # ================= 主图 =================
    py, ph = 142, 420
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="{ZENITH}" borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph * 0.42}"><Container width="{CW}" '
             f'height="{ph * 0.42:.1f}" color="{ZENITH}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.42}" width="{CW}" '
             f'height="{ph * 0.34}"><Container width="{CW}" '
             f'height="{ph * 0.34:.1f}" color="{SKY_HI}"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.76}" width="{CW}" '
             f'height="{ph * 0.24:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.24:.1f}" color="{SKY_MID}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="transparent" borderRadius="16" '
             f'border="1 SOLID #FFFFFF30"/></Positioned>')

    ax_x = M + CW - 96
    n.extend(alt_axis(ax_x, py + 26, ph - 78, 14.0,
                      ticks=(2, 4, 6, 8, 10, 12), label_size=11,
                      color="#DCE8F2"))
    n.extend(range_bar(ax_x + 12, py, 14, ph, 6.0, 12.0, 14.0,
                       "#FFFFFF55", ax_x, ph - 78))

    # —— 插画：三种质地 ——
    # ① 成层状 stratiformis：大体等距云粒阵（左上）
    n.extend(cc_sheet(M + 70, py + 56, 340, 92, cols=10, rows=4,
                      r_min=7, r_max=13, seed=5))
    T("stratiformis 成层状 · 云粒阵", M + 70, py + 158, 340, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # ② 网状 lacunosus：粒群 + 圆孔（右上）
    n.extend(cc_lacunosis(M + 470, py + 52, 350, 100))
    T("lacunosus 网状 · 粒间圆孔", M + 470, py + 158, 340, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # ③ 絮状 floccus + 堡状 castellanus（中下）
    for fx, fy, d in [(M + 110, py + 226, 26), (M + 190, py + 246, 20),
                      (M + 260, py + 222, 23), (M + 330, py + 252, 17)]:
        n.append(circle(fx, fy, d, "#F4F8FB"))
        n.append(rect(fx - d * 0.35, fy + d * 0.30, d * 0.7, d * 0.5,
                      "#D9E4EC", radius=6))
    for bx in (M + 520, M + 610, M + 700):
        n.append(rect(bx, py + 238, 14, 34, "#F4F8FB", radius=6))
        n.append(circle(bx + 7, py + 234, 16, "#F4F8FB"))
    T("floccus 絮状（左）· castellanus 堡状（右）", M + 70, py + 290, 660,
      18, 11, "#C9DAE8", "LEFT", nodes=n)

    # ④ 幡状云 virga：云粒下垂丝（底部注）
    for i in range(6):
        vx = M + 90 + i * 36
        n.extend(polyline([(vx, py + 320), (vx - 5, py + 356)], 1.6,
                          "#AFC6D8"))
    T("virga 幡状云：冰晶下悬不落地", M + 90, py + 362, 500, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    T("示意图 · 云粒视宽多 ＜1°（小指）", M + 620,
      py + ph - 40, 300, 20, 11.5, "#9FB4C6", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与光学"),
        (684, 276, "元素视宽"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="14" '
                 f'border="1 SOLID #E3DAC6"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12.5, ACCENT,
          "LEFT", "BOLD", nodes=n)

    T("常用范围", M + 16, dy + 42, 150, 20, 12, INK_DIM, "LEFT", nodes=n)
    T("6–12 km", M + 16, dy + 62, 170, 28, 20, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("20 000–40 000 ft", M + 16, dy + 90, 190, 18, 11.5, INK_DIM,
      "LEFT", "NORMAL", MONO, nodes=n)
    T("更宽范围：—（高云三属共用 6 000–12 000 m；积雨云消散的卷积云冬季可远低于 6 km）",
      M + 200, dy + 56, 340, 44, 11, INK_DIM, "LEFT", nodes=n)

    T("冰晶为主，无阴影", M + 400, dy + 44, 260, 24, 15, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("白色云片或薄层，无暗影；常由卷云或卷层云转变而来，"
      "或为其消散残留，存留时间短", M + 400, dy + 72, 260, 44, 10.5,
      INK_DIM, "LEFT", nodes=n)

    T("＜1°", M + 700, dy + 42, 240, 40, 26, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("≈ 臂长处小指宽（1 cm 尺 ≈ 1°）；排列成较规律的颗粒或波纹",
      M + 700, dy + 86, 240, 30, 10.5, INK_DIM, "LEFT", nodes=n)

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
        ("种 species · 4", ["stratiformis 成层卷积云（云粒成层）",
                            "lenticularis 荚状卷积云（透镜形）",
                            "castellanus 堡状卷积云（塔状突起）",
                            "floccus 絮状卷积云（小簇堆）"]),
        ("变种 varieties · 2", ["undulatus 波状卷积云（起伏排列）",
                                "lacunosus 网状卷积云（粒间圆孔）",
                                "—", "—"]),
        ("附属/从属 · 2", ["mamma 乳状云（云底垂悬半球）",
                           "virga 幡状云（冰晶下垂不落地）",
                           "—", "—"]),
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
             f'<Container width="6" height="150" color="{SKY_HI}" '
             f'borderRadius="3"/></Positioned>')
    T("观测提示（只引来源结论）", M + 26, wy + 16, 500, 24, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    tips_l = ["与卷积云之别（卷云）：卷云呈纤维/丝绢，卷积云呈颗粒/波纹",
              "易混：边缘带极小云粒的消散中积云（Ac）——需结合云底高度判断",
              "常由卷云/卷层云转变而来，存留时间短，出现后形态变化快"]
    tips_r = ["云粒视宽 ＜1°，排列较规律；逐个云粒无阴影",
              "出现 virga 时冰晶下垂但通常不抵达地面",
              "高云三属共处 6–12 km：先定层，再按质地分辨三属"]
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
             f'color="{SKY_HI}18" borderRadius="14" '
             f'border="1 SOLID {SKY_HI}55"/></Positioned>')
    T("拉丁词根", M + 20, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("cirro- + cumulus = 高空 + 堆积", M + 20, ey + 34, 430, 26, 16,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("cirro- 表「羽·丝缕」（高云三属共用）；cumulo 表「堆积·蓬松」",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("云底 6–12 km + 颗粒/波纹、无阴影 → 卷积云；"
      "纤维丝缕 → 卷云；连续薄幕见晕 → 卷层云", M + 510, ey + 34, 440, 44,
      12.5, INK_TXT, "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 卷积云页 · S4 CIMO 表 15-1 · "
             "S5 NOAA JetStream · S6 香港天文台《云》电子书",
             "04 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
