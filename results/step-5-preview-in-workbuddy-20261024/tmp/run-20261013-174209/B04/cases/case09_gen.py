#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-09 层积云 Stratocumulus (Sc) 图鉴页（1080×1350，4:5 图鉴体例）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
30° 判别规则）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
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


def sc_tessellation(x: float, y: float, w: float, h: float, cols: int,
                    rows: int, seed: int = 11) -> list[str]:
    """层积云嵌合：暗底 + 亮顶云块（蜂窝状 tessellations）。"""
    import random
    rnd = random.Random(seed)
    out = []
    out.append(f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" '
               f'height="{h:.2f}"><Container width="{w:.2f}" '
               f'height="{h:.2f}" color="#7E93A6" '
               f'borderRadius="12"/></Positioned>')
    cw, ch = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            gx = x + cw * (c + 0.5)
            gy = y + ch * (r + 0.5)
            bw = cw * (0.72 + 0.16 * rnd.random())
            bh = ch * (0.52 + 0.14 * rnd.random())
            out.append(rect(gx - bw / 2, gy - bh / 2, bw, bh, "#C9D6E0",
                            radius=bh * 0.45))
            out.append(rect(gx - bw * 0.38, gy - bh * 0.62, bw * 0.76,
                            bh * 0.42, "#E4EDF4", radius=bh * 0.3))
    return out


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("09", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("层积云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Stratocumulus · Sc ｜ 低云族 ｜ 水滴云", M + 64, 92, 620, 26, 16,
      INK_DIM, nodes=n)
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_LOW}" borderRadius="17"/></Positioned>')
    T("低云族 · 0–2 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
      "CENTER", "BOLD", nodes=n)
    T("抬头读天 · 国际云图集十属", W - M - 300, 92, 300, 22, 12, "#98A6B2",
      "RIGHT", nodes=n)
    n.append(hline(M, 126, CW, "#D8CFBB", 1.2))

    # ================= 主图 =================
    py, ph = 142, 420
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="{SKY_LOW}" borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph * 0.24}"><Container width="{CW}" '
             f'height="{ph * 0.24:.1f}" color="{ZENITH}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.24}" width="{CW}" '
             f'height="{ph * 0.28}"><Container width="{CW}" '
             f'height="{ph * 0.28:.1f}" color="{SKY_HI}"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.52}" width="{CW}" '
             f'height="{ph * 0.48:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.48:.1f}" color="{SKY_MID}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="transparent" borderRadius="16" '
             f'border="1 SOLID #FFFFFF30"/></Positioned>')

    ax_x = M + CW - 96
    n.extend(alt_axis(ax_x, py + 26, ph - 78, 4.0,
                      ticks=(0.5, 1, 1.5, 2, 3, 4), label_size=11,
                      color="#DCE8F2"))
    n.extend(range_bar(ax_x + 12, py, 14, ph, 0.3, 1.35, 4.0,
                       "#FFFFFF55", ax_x, ph - 78))

    # —— 插画①：蜂窝状云块（左上）——
    n.extend(sc_tessellation(M + 60, py + 54, 430, 118, cols=7, rows=3,
                             seed=11))
    T("tessellations 蜂窝状云块 · 带暗部", M + 60, py + 184, 430, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画②：30° 判别示意（右上）——
    # 地平线 + 30° 仰角扇区 + 云块
    gx0, gy0 = M + 560, py + 150
    n.extend(polyline([(gx0 - 20, gy0), (gx0 + 330, gy0)], 1.6, "#EAF1F7"))
    T("地平线", gx0 + 300, gy0 + 6, 70, 16, 10, "#EAF1F7", "RIGHT",
      nodes=n)
    # 30° 扇形（两条射线 + 弧）
    n.extend(polyline([(gx0, gy0), (gx0 + 150, gy0 - 87)], 1.4, "#F2D8A0"))
    arc = []
    for k in range(13):
        a = math.radians(-30 * k / 12)
        arc.append((gx0 + 110 * math.cos(a), gy0 + 110 * math.sin(a)))
    n.extend(polyline(arc, 1.4, "#F2D8A0"))
    T("30°", gx0 + 96, gy0 - 56, 60, 18, 12, "#F2D8A0", "LEFT", "BOLD",
      MONO, nodes=n)
    # 云块（置于 30° 以上）
    for fx, fy, d in [(gx0 + 74, gy0 - 62, 34), (gx0 + 128, gy0 - 96, 40),
                      (gx0 + 186, gy0 - 74, 30)]:
        n.append(circle(fx, fy, d, "#C9D6E0"))
        n.append(circle(fx, fy - d * 0.12, d * 0.8, "#E4EDF4"))
    T("云块多在地平线上 30° 以上、视宽 ＞5° → 层积云", gx0 - 10, gy0 + 26,
      400, 20, 11.5, "#EAF1F7", "LEFT", nodes=n)

    # —— 插画③：薄处华（corona）小注（底部）——
    T("层不厚时薄处有时可见华（corona）或彩云（irisation）",
      M + 60, py + 250, 620, 40, 11.5, "#EAF1F7", "LEFT", nodes=n)
    T("示意图（DSL 绘制，非照片）", M + 620, py + ph - 40, 300, 20, 11.5,
      "#C4D2DE", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与元素"),
        (684, 276, "与高积云判别"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="14" '
                 f'border="1 SOLID #E3DAC6"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12.5, ACCENT,
          "LEFT", "BOLD", nodes=n)

    T("常用范围", M + 16, dy + 42, 150, 20, 12, INK_DIM, "LEFT", nodes=n)
    T("0.3–1.35 km", M + 16, dy + 62, 200, 28, 20, INK_TXT, "LEFT",
      "BOLD", MONO, nodes=n)
    T("1 000–4 500 ft", M + 16, dy + 90, 190, 18, 11.5, INK_DIM,
      "LEFT", "NORMAL", MONO, nodes=n)
    T("更宽范围：0.3–2 km（1 000–6 500 ft）", M + 200, dy + 62, 340, 40,
      11, INK_DIM, "LEFT", nodes=n)

    T("水滴为主", M + 400, dy + 42, 260, 40, 14, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("灰或灰白云块、片或层，常带暗部；嵌合、圆胖块或卷（幡状云除外）",
      M + 400, dy + 84, 260, 32, 10.5, INK_DIM, "LEFT", nodes=n)

    T("＞5°（三指）", M + 700, dy + 42, 250, 40, 16, INK_TXT, "LEFT",
      "BOLD", MONO, nodes=n)
    T("规则云块视宽 ＞5°：大于高积云（1–5°）与卷积云（＜1°）",
      M + 700, dy + 86, 250, 30, 10.5, INK_DIM, "LEFT", nodes=n)

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
        ("种 species · 4", ["stratiformis 成层状（云块成层）",
                            "lenticularis 荚状（透镜形）",
                            "castellanus 堡状（塔状突起）",
                            "cumulogenitus 积云性（积云铺展而成）"]),
        ("变种 varieties · 7", ["translucidus 透光 / perlucidus 漏光",
                                "opacus 荫光 / undulatus 波状",
                                "radiatus 辐辏状 / lacunosus 网状",
                                "duplicatus 复层积云（叠置两层）"]),
        ("附属/从属 · 3", ["mamma 乳状云（云底垂悬半球）",
                           "virga 幡状云（下垂不落地）",
                           "praecipitatio 降水幡（可达地面）",
                           "—"]),
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
             f'<Container width="6" height="150" color="{SKY_LOW}" '
             f'borderRadius="3"/></Positioned>')
    T("观测提示（只引来源结论）", M + 26, wy + 16, 500, 24, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    tips_l = ["30° 规则：云块多在地平线上 30° 以上且视宽 ＞5° → 层积云",
              "与高积云之别：高积云块视宽 1–5°、云底 2–6 km",
              "积云垂直伸展铺展可成 cumulogenitus 层积云"]
    tips_r = ["层不厚时薄处有时可见华（corona）或彩云（irisation）",
              "云底降低或失去地形抬升支撑时可发展成层云",
              "除幡状云外，云块无纤维结构——与卷云/高层云相别"]
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
             f'color="{SKY_LOW}22" borderRadius="14" '
             f'border="1 SOLID {SKY_LOW}66"/></Positioned>')
    T("拉丁词根", M + 20, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("stratus + cumulus = 层 + 堆积", M + 20, ey + 34, 430, 26, 16,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("strato = 平展·层状；cumulo = 堆积·蓬松——成层的蓬松云块",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("云块 ＞5° 且高于地平 30° → 层积云；1–5° → 高积云；"
      "均匀灰层无云块 → 层云", M + 510, ey + 34, 440, 44, 12.5, INK_TXT,
      "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 层积云页 · S4 CIMO 表 15-1 · S5 NOAA JetStream · "
             "S6 香港天文台《云》电子书",
             "09 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
