#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-06 高积云 Altocumulus (Ac) 图鉴页（1080×1350，4:5 图鉴体例，含视宽标尺）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
易混规则、30° 规则）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
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


def ac_masses(x: float, y: float, w: float, h: float, cols: int, rows: int,
              seed: int = 7) -> list[str]:
    """高积云块：白顶 + 灰底的圆胖云块（laminae / rounded masses，有阴影）。"""
    import random
    rnd = random.Random(seed)
    out = []
    for r in range(rows):
        for c in range(cols):
            gx = x + w * (c + 0.5) / cols
            gy = y + h * (r + 0.5) / rows
            d = min(w / cols, h / rows) * (0.62 + 0.22 * rnd.random())
            out.append(circle(gx, gy + d * 0.16, d, CLOUD_SHADE))
            out.append(circle(gx, gy - d * 0.10, d * 0.92, CLOUD))
    return out


def corona_disk(cx: float, cy: float, r_core: float, r_ring: float) -> list[str]:
    """华 corona：光源 + 外红内蓝双环（几度内）。"""
    out = []
    for rr, cc in [(r_ring, "#C96A5E"), (r_ring - 3, "#7E97C4")]:
        out.append(f'<Positioned left="{cx - rr:.2f}" top="{cy - rr:.2f}" '
                   f'width="{rr * 2:.2f}" height="{rr * 2:.2f}">'
                   f'<Container width="{rr * 2:.2f}" height="{rr * 2:.2f}" '
                   f'shape="CIRCLE" color="transparent" '
                   f'border="2.5 SOLID {cc}"/></Positioned>')
    out.append(circle(cx, cy, r_core, "#F2E3BC"))
    return out


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("06", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("高积云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Altocumulus · Ac ｜ 中云族 ｜ 水滴 + 冰晶", M + 64, 92, 620, 26, 16,
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

    # —— 插画①：高积云块阵（左上，白顶灰底）——
    n.extend(ac_masses(M + 70, py + 56, 400, 108, cols=6, rows=3, seed=7))
    T("rounded masses 圆胖云块 · 有阴影", M + 70, py + 176, 400, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画②：华 corona（右上）——
    n.extend(corona_disk(M + 600, py + 108, 26, 56))
    T("corona 华：外红内蓝，仅几度内", M + 500, py + 176, 400, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画③：视宽标尺（中指/小指/三指，底部）——
    ty = py + 240
    T("元素视宽标尺（臂长处）", M + 70, ty, 400, 20, 12.5, "#EAF1F7",
      "LEFT", "BOLD", nodes=n)
    fingers = [("小指 ≈ 1°", "Cc", 14), ("1–2 指 ≈ 1–5°", "Ac", 30),
               ("三指 ≈ ＞5°", "Sc", 52)]
    for i, (lab, tag, d) in enumerate(fingers):
        fx = M + 120 + i * 240
        fy = ty + 66
        hl = (tag == "Ac")
        col = "#FFFFFF" if hl else "#D8E2EA"
        n.append(f'<Positioned left="{fx - d / 2:.2f}" '
                 f'top="{fy - d / 2:.2f}" width="{d:.2f}" height="{d:.2f}">'
                 f'<Container width="{d:.2f}" height="{d:.2f}" '
                 f'shape="CIRCLE" color="transparent" '
                 f'border="2 {"SOLID" if hl else "SOLID"} '
                 f'{ACCENT if hl else col}"/></Positioned>')
        n.append(circle(fx, fy, d * 0.55, CLOUD if hl else "#B9C9D8"))
        T(lab, fx - 110, fy + 44, 220, 20, 11.5,
          ACCENT if hl else "#EAF1F7", "CENTER", "BOLD" if hl else "NORMAL",
          nodes=n)
        T(tag, fx - 40, fy - 8, 80, 18, 12,
          ACCENT if hl else "#EAF1F7", "CENTER", "BOLD", MONO, nodes=n)

    T("示意图（DSL 绘制，非照片）", M + 620, py + ph - 40, 300, 20, 11.5,
      "#C4D2DE", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成"),
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
    T("2–6 km", M + 16, dy + 62, 170, 28, 20, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("6 500–20 000 ft", M + 16, dy + 90, 190, 18, 11.5, INK_DIM,
      "LEFT", "NORMAL", MONO, nodes=n)
    T("更宽范围：—（与高层云共用合并单元格）", M + 200, dy + 62, 340, 40,
      11, INK_DIM, "LEFT", nodes=n)

    T("下部水滴，上部过冷水滴 + 冰晶", M + 400, dy + 42, 260, 40, 14,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("白、灰或灰白相间；局部有阴影；由片状、圆胖块或卷构成",
      M + 400, dy + 84, 260, 32, 10.5, INK_DIM, "LEFT", nodes=n)

    T("1°–5°", M + 700, dy + 42, 240, 40, 26, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("大于小指、小于三指（臂长处）；最常多个层次同时出现",
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
        ("种 species · 4", ["stratiformis 成层高积云（云块成层）",
                            "lenticularis 荚状高积云（透镜形）",
                            "castellanus 堡状高积云（塔状突起）",
                            "floccus 絮状高积云（小簇堆）"]),
        ("变种 varieties · 7", ["translucidus 透光 / perlucidus 漏光",
                                "opacus 荫蔽光 / undulatus 波状",
                                "radiatus 辐辏状 / lacunosus 网状",
                                "duplicatus 复高积云（叠置层）"]),
        ("附属/从属 · 2", ["mamma 乳状云（云底垂悬半球）",
                           "virga 幡状云（纤维状下垂）",
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
             f'<Container width="6" height="150" color="{SKY_MID}" '
             f'borderRadius="3"/></Positioned>')
    T("观测提示（只引来源结论）", M + 26, wy + 16, 500, 24, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    tips_l = ["最常见的中云；常多个层次在不同高度同时出现",
              "云块视宽 1–5°：大于小指（Cc ＜1°）、小于三指（Sc ＞5°）",
              "与层积云判别 30° 规则：云块多在地平线上 30° 以上且 ＞5° → 层积云"]
    tips_r = ["薄处常见华（corona，外红内蓝）与彩云（irisation）",
              "有时下垂纤维状幡状云（virga）",
              "有时看似纤维状或正在消散；远看云块可似合并"]
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
    T("alto- + cumulus = 中层 + 堆积", M + 20, ey + 34, 430, 26, 16,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("alto 原意为「高」，此处表「中层」（与低层的积云相别）",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("云底 2–6 km + 云块 1–5°、有阴影 → 高积云；＜1° 无阴影 → 卷积云；"
      "＞5° 且高于 30° → 层积云", M + 510, ey + 34, 440, 44, 12.5, INK_TXT,
      "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 高积云页 · S4 CIMO 表 15-1 · S5 NOAA JetStream · "
             "S6 香港天文台《云》电子书",
             "06 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
