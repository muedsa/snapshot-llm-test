#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-02 观测三步法：一指量天（1080×1440，3:4 方法图）。

来源：S1（层面与属）/ S5 NOAA（视宽 1°–5°、现象判别）/ S6 HKO（一指宽≈1°、
30° 规则、夜间 As/Ns 惯例、St/Ns 降水判别、见雷必是 Cb）/ S7–S9（22° 晕）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b04_common import (  # noqa: F403
    T, snapshot, rect, circle, hline, vline, polyline, grad,
    ZENITH, SKY_HI, SKY_MID, SKY_LOW, HORIZON, CLOUD, CLOUD_DIM,
    CLOUD_SHADE, CLOUD_DARK, INK_TXT, INK_DIM, ACCENT, ACCENT_SOFT, GOLD,
    MONO, SERIF, INTER, SANS, PAPER_WARM, WARN,
    veil, sun_disk, rain_streaks, sc_field, cc_grains, ac_rows,
    cirrus_wisp, stratus_blanket, cumulus_heap, cb_tower, foot_bar,
)

W, H = 1080, 1440
M = 60  # 页边距


def dsl() -> str:
    n = []
    # 纸面
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("02", M, 44, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("一指量天", M + 62, 34, 500, 52, 40, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=4, nodes=n)
    T("云的观测三步法 —— 定层 · 量元素 · 看现象", M + 64, 88, 700, 26, 16,
      INK_DIM, nodes=n)
    n.append(hline(M, 122, W - 2 * M, "#D8CFBB", 1.2))

    # ================= 第一步：定层 =================
    y0 = 140
    n.append(f'<Positioned left="{M}" top="{y0}" width="{W - 2 * M}" '
             f'height="300"><Container width="{W - 2 * M}" height="300" '
             f'color="#FFFFFF" borderRadius="16" border="1 SOLID '
             f'#E3DAC6"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{y0}" width="6" height="300">'
             f'<Container width="6" height="300" color="{SKY_HI}" '
             f'borderRadius="3"/></Positioned>')
    T("第一步", M + 26, y0 + 20, 120, 26, 15, SKY_HI, "LEFT", "BOLD",
      nodes=n)
    T("定层：云底在哪一层？", M + 26, y0 + 44, 520, 36, 25, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    T("知道云底高度，候选属就缩小到该层的 2–4 个。", M + 26, y0 + 86, 520,
      24, 14, INK_DIM, nodes=n)
    # 三层小图（右）
    bx, bw = M + 560, 380
    bands = [("高云族", "5–13 km", "Ci · Cc · Cs", SKY_HI, 0),
             ("中云族", "2–7 km", "Ac · As · Ns", SKY_MID, 1),
             ("低云族", "0–2 km", "St · Sc · Cu · Cb", SKY_LOW, 2)]
    for i, (nm, rng, gen, col, idx) in enumerate(bands):
        by = y0 + 24 + i * 84
        n.append(f'<Positioned left="{bx}" top="{by}" width="{bw}" '
                 f'height="72"><Container width="{bw}" height="72" '
                 f'color="{col}55" borderRadius="10" border="1 SOLID '
                 f'{col}"/></Positioned>')
        T(nm, bx + 14, by + 10, 120, 22, 15, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(rng, bx + 14, by + 36, 120, 20, 13, INK_TXT, "LEFT", "NORMAL",
          MONO, nodes=n)
        T(gen, bx + 150, by + 22, 220, 24, 14, INK_DIM, "LEFT", nodes=n)
    # 跨层注意
    notes = ["积云/积雨云顶部可达中、高层", "雨层云通常贯穿三层",
             "高层云常向上延伸更高"]
    for i, t in enumerate(notes):
        T("· " + t, M + 26, y0 + 128 + i * 26, 520, 24, 13, INK_DIM,
          nodes=n)
    T("（高度范围：温带常用值，WMO 国际云图集 表 6）", M + 26, y0 + 216,
      520, 22, 11.5, "#98A6B2", nodes=n)

    # ================= 第二步：量元素 =================
    y0 = 468
    n.append(f'<Positioned left="{M}" top="{y0}" width="{W - 2 * M}" '
             f'height="300"><Container width="{W - 2 * M}" height="300" '
             f'color="#FFFFFF" borderRadius="16" border="1 SOLID '
             f'#E3DAC6"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{y0}" width="6" height="300">'
             f'<Container width="6" height="300" color="{SKY_MID}" '
             f'borderRadius="3"/></Positioned>')
    T("第二步", M + 26, y0 + 20, 120, 26, 15, SKY_MID, "LEFT", "BOLD",
      nodes=n)
    T("量元素：伸直手臂，一指宽 ≈ 1°", M + 26, y0 + 44, 620, 36, 25,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("看云里单个「元素」占几个指宽——同族云的元素大小截然不同。",
      M + 26, y0 + 86, 560, 24, 14, INK_DIM, nodes=n)
    # 三个视宽圆
    sizes = [(26, "小指尖", "＜1°", "卷积云 Cc", SKY_HI),
             (52, "一指至三指", "1–5°", "高积云 Ac", SKY_MID),
             (92, "三指以上", "＞5°", "层积云 Sc", SKY_LOW)]
    for i, (d, fing, ang, gen, col) in enumerate(sizes):
        cx = M + 90 + i * 190
        cy = y0 + 190
        n.append(circle(cx, cy, d, "#FFFFFF"))
        n.append(f'<Positioned left="{cx - d / 2}" top="{cy - d / 2}" '
                 f'width="{d}" height="{d}"><Container width="{d}" '
                 f'height="{d}" color="transparent" shape="CIRCLE" '
                 f'border="1.5 SOLID {col}"/></Positioned>')
        T(fing, cx - 80, cy + d / 2 + 14, 160, 20, 13, INK_TXT, "CENTER",
          "BOLD", nodes=n)
        T(ang, cx - 80, cy + d / 2 + 34, 160, 20, 13, ACCENT, "CENTER",
          "BOLD", MONO, nodes=n)
        T(gen, cx - 80, cy + d / 2 + 54, 160, 20, 13, INK_DIM, "CENTER",
          nodes=n)
    T("· 尺子规则：1 cm 直尺臂长处一指宽 ≈ 视角 1°", M + 26, y0 + 130,
      560, 24, 13, INK_DIM, nodes=n)
    T("· 判别积云/层积云：元素仰角 ＞30° 且视宽 ＞5° → 层积云 Sc",
      M + 26, y0 + 156, 560, 24, 13, INK_DIM, nodes=n)
    T("（视宽与角度规则：WMO ICA 定义，香港天文台云电子书）", M + 26,
      y0 + 250, 560, 22, 11.5, "#98A6B2", nodes=n)

    # ================= 第三步：看现象 =================
    y0 = 796
    n.append(f'<Positioned left="{M}" top="{y0}" width="{W - 2 * M}" '
             f'height="300"><Container width="{W - 2 * M}" height="300" '
             f'color="#FFFFFF" borderRadius="16" border="1 SOLID '
             f'#E3DAC6"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{y0}" width="6" height="300">'
             f'<Container width="6" height="300" color="{ACCENT}" '
             f'borderRadius="3"/></Positioned>')
    T("第三步", M + 26, y0 + 20, 120, 26, 15, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("看现象：光与雨的回答", M + 26, y0 + 44, 620, 36, 25, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    rows = [
        ("日/月旁 22° 晕圈", "卷层云 Cs", "六角冰晶折射，最小偏向角约 22°"),
        ("薄处几度内彩色华（红外蓝内）", "高积云 Ac · 层积云 Sc", ""),
        ("日轮如磨砂玻璃、地上无影", "高层云 As", "不产生晕"),
        ("日轮轮廓清晰可辨", "层云 St", ""),
        ("完全遮日 + 连续雨雪", "雨层云 Ns", "云底随降水降低"),
        ("阵雨、雷电或冰雹", "积雨云 Cb", "见到雷电即可断定是 Cb"),
        ("毛毛雨、冰针或雪粒", "层云 St", ""),
    ]
    ry = y0 + 92
    for i, (ph, gen, note) in enumerate(rows):
        if i % 2 == 0:
            n.append(rect(M + 20, ry - 4, W - 2 * M - 40, 27, "#F6F1E6",
                          radius=6))
        T(ph, M + 30, ry, 380, 22, 13.5, INK_TXT, "LEFT", nodes=n)
        T(gen, M + 420, ry, 250, 22, 13.5, ACCENT, "LEFT", "BOLD",
          nodes=n)
        if note:
            T(note, M + 680, ry, 300, 22, 11.5, INK_DIM, "LEFT", nodes=n)
        ry += 27

    # ================= 易混三对 =================
    y0 = 1124
    T("三对易混属的硬规则", M, y0, 700, 30, 20, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    pairs = [("高层云 As", "雨层云 Ns",
              "夜间难辨时：无雨雪即按惯例记为 As"),
             ("层积云 Sc", "高积云 Ac",
              "元素仰角 ＞30° 且视宽 ＞5° → Sc"),
             ("层云 St", "雨层云 Ns",
              "以降水性质区分：毛毛雨 vs 连续降雨")]
    for i, (a, b, rule) in enumerate(pairs):
        py = y0 + 40 + i * 62
        n.append(f'<Positioned left="{M}" top="{py}" width="{W - 2 * M}" '
                 f'height="52"><Container width="{W - 2 * M}" height="52" '
                 f'color="#FFFFFF" borderRadius="10" border="1 SOLID '
                 f'#E3DAC6"/></Positioned>')
        T(a, M + 18, py + 15, 170, 24, 15, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T("vs", M + 196, py + 15, 40, 24, 13, "#98A6B2", "CENTER",
          nodes=n)
        T(b, M + 240, py + 15, 170, 24, 15, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(rule, M + 430, py + 15, 560, 24, 13.5, ACCENT, "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, 1382, W - 2 * M,
             "S1 层面表 6｜S5 NOAA JetStream｜S6 香港天文台｜S7–S9 22° 晕",
             "02 / 11", n)

    return snapshot(W, H, n, PAPER_WARM)


if __name__ == "__main__":
    out = dsl()
    if WARN:
        print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
