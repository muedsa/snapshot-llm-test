#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-10 层云 Stratus (St) 图鉴页（1080×1350，4:5 图鉴体例）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
St/Ns 以降水区分、雾被抬升成云）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
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


def stratus_blanket(x: float, y: float, w: float, h: float) -> list[str]:
    """层云幕：均一灰层 + 底边微起伏。"""
    out = [rect(x, y, w, h * 0.74, "#B7C4CF", radius=10)]
    pts = []
    for k in range(13):
        kt = k / 12
        pts.append((x + w * kt, y + h * (0.74 + 0.035 * math.sin(kt * 9))))
    pts += [(x + w, y + h), (x, y + h)]
    out.extend(polyline(pts, 2.0, "#B7C4CF"))
    return out


def ragged_patch(x: float, y: float, w: float, h: float) -> list[str]:
    """碎层云 fractus：不规则破片。"""
    out = []
    for bx, by, bw, bh in [(0.00, 0.30, 0.46, 0.44),
                           (0.52, 0.06, 0.42, 0.50),
                           (0.14, 0.56, 0.60, 0.36)]:
        out.append(rect(x + w * bx, y + h * by, w * bw, h * bh,
                        "#A9B7C2", radius=7))
    return out


def drizzle(x: float, y: float, w: float, h: float,
            n_str: int = 8) -> list[str]:
    """毛毛雨：细短斜线（不落地）。"""
    out = []
    for i in range(n_str):
        rx = x + w * (0.06 + 0.12 * i)
        out.extend(polyline([(rx, y), (rx - 3, y + h)], 1.5, "#93A6B4"))
    return out


def sun_outline(x: float, y: float, d: float) -> list[str]:
    """透日轮廓（层云时日月轮廓可辨）。"""
    out = [circle(x, y, d, "#EFE0B8")]
    out.append(f'<Positioned left="{x - d/2 - 4:.2f}" '
               f'top="{y - d/2 - 4:.2f}" width="{d + 8:.2f}" '
               f'height="{d + 8:.2f}"><Container width="{d + 8:.2f}" '
               f'height="{d + 8:.2f}" shape="CIRCLE" color="transparent" '
               f'border="1.5 SOLID #D9C58E"/></Positioned>')
    return out


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("10", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("层云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Stratus · St ｜ 低云族 ｜ 水滴云", M + 64, 92, 620, 26, 16,
      INK_DIM, nodes=n)
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_LOW}" borderRadius="17"/></Positioned>')
    T("低云族 · 地表–0.6 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
      "CENTER", "BOLD", nodes=n)
    T("抬头读天 · 国际云图集十属", W - M - 300, 92, 300, 22, 12, "#98A6B2",
      "RIGHT", nodes=n)
    n.append(hline(M, 126, CW, "#D8CFBB", 1.2))

    # ================= 主图 =================
    py, ph = 142, 400
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="{SKY_LOW}" borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph * 0.30}"><Container width="{CW}" '
             f'height="{ph * 0.30:.1f}" color="{ZENITH}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.30}" width="{CW}" '
             f'height="{ph * 0.22:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.22:.1f}" color="{SKY_HI}"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.52}" width="{CW}" '
             f'height="{ph * 0.48:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.48:.1f}" color="{SKY_MID}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="transparent" borderRadius="16" '
             f'border="1 SOLID #FFFFFF30"/></Positioned>')

    ax_x = M + CW - 96
    n.extend(alt_axis(ax_x, py + 26, ph - 78, 2.0,
                      ticks=(0.5, 1, 1.5, 2), label_size=11,
                      color="#DCE8F2"))
    # 层云云底：地表–2 km（CIMO 常用范围）
    n.extend(range_bar(ax_x + 12, py, 14, ph, 0.0, 0.6, 2.0,
                       "#FFFFFF55", ax_x, ph - 78))

    # —— 插画①：层云幕 + 毛毛雨（左上）——
    n.extend(stratus_blanket(M + 60, py + 74, 400, 96))
    n.extend(drizzle(M + 80, py + 178, 340, 46, 9))
    T("nebulosus 雾状层云 + 毛毛雨（drizzle）", M + 60, py + 236, 430, 18,
      11, "#EAF1F7", "LEFT", nodes=n)

    # —— 插画②：碎层云 fractus（中）——
    n.extend(ragged_patch(M + 500, py + 96, 240, 74))
    T("fractus 碎层云：不规则破片", M + 500, py + 186, 260, 18, 11,
      "#EAF1F7", "LEFT", nodes=n)

    # —— 插画③：透日轮廓（右）——
    n.extend(sun_outline(M + 800, py + 120, 40))
    T("日轮轮廓可辨", M + 740, py + 172, 120, 18, 11, "#EAF1F7",
      "CENTER", nodes=n)

    # —— 插画④：底部注记 ——
    T("灰色云层，底边相当均匀；可产生毛毛雨、冰粒或雪粒；"
      "厚层遮日时日月轮廓不可见",
      M + 60, py + 288, 700, 40, 11.5, "#EAF1F7", "LEFT", nodes=n)
    T("示意图（DSL 绘制，非照片）", M + 620, py + ph - 40, 300, 20, 11.5,
      "#C4D2DE", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 566, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与降水"),
        (684, 276, "与雨层云的分别"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="12" '
                 f'border="1 SOLID #E4DCC8"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12, INK_DIM,
          "LEFT", nodes=n)

    # 卡 A 内容
    T("地表–0.6 km", M + 16, dy + 40, 200, 30, 20, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("地表–2 000 ft", M + 16, dy + 74, 200, 20, 11.5, INK_DIM, "LEFT",
      "NORMAL", MONO, nodes=n)
    T("更宽：地表–1.2 km（地表–4 000 ft）", M + 16, dy + 94, 340, 18, 11,
      "#98A6B2", "LEFT", nodes=n)
    # 卡 B 内容
    T("小水滴为主", M + 400, dy + 40, 260, 30, 20, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("厚度大时可有毛毛雨、冰粒或雪粒", M + 400, dy + 74, 260, 18, 11,
      INK_DIM, "LEFT", nodes=n)
    T("极低温时可例外出现晕", M + 400, dy + 94, 260, 18, 11, INK_DIM,
      "LEFT", nodes=n)
    # 卡 C 内容
    T("以降水区分", M + 700, dy + 40, 250, 30, 20, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("云底均匀且不降水 → 层云", M + 700, dy + 74, 250, 18, 11, INK_DIM,
      "LEFT", nodes=n)
    T("暗灰 + 连续雨/雪 → 雨层云", M + 700, dy + 94, 250, 18, 11,
      INK_DIM, "LEFT", nodes=n)

    # ================= ICA 清单 =================
    ly, lh = 706, 148
    n.append(f'<Positioned left="{M}" top="{ly}" width="{CW}" '
             f'height="{lh}"><Container width="{CW}" height="{lh}" '
             f'color="#FFFFFF" borderRadius="12" '
             f'border="1 SOLID #E4DCC8"/></Positioned>')
    T("WMO ICA 分类（种 → 变种 → 附属/从属）", M + 16, ly + 12, 500, 22,
      15, INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("引自香港天文台《云》电子书（引译 WMO 国际云图集）；中文为通行译名，"
      "英文为 ICA 原名", M + 16, ly + 36, 760, 18, 11, INK_DIM, "LEFT",
      nodes=n)

    col_w = (CW - 32) / 3
    cx1 = M + 16
    cx2 = M + 16 + col_w
    cx3 = M + 16 + 2 * col_w
    T("种 species · 2", cx1, ly + 62, col_w - 10, 20, 12.5, ACCENT,
      "LEFT", "BOLD", nodes=n)
    for i, sp in enumerate(["nebulosus（雾状层云）",
                            "fractus（碎层云）"]):
        T("·  " + sp, cx1, ly + 86 + i * 24, col_w - 10, 20, 12,
          INK_TXT, "LEFT", nodes=n)
    T("变种 varieties · 3", cx2, ly + 62, col_w - 10, 20, 12.5, ACCENT,
      "LEFT", "BOLD", nodes=n)
    for i, v in enumerate(["translucidus（半透明）",
                           "opacus（不透明）",
                           "undulatus（波状）"]):
        T("·  " + v, cx2, ly + 86 + i * 24, col_w - 10, 20, 12,
          INK_TXT, "LEFT", nodes=n)
    T("附属/从属 · 1", cx3, ly + 62, col_w - 10, 20, 12.5, ACCENT,
      "LEFT", "BOLD", nodes=n)
    for i, a in enumerate(["praecipitatio 降水幡（可达地面）",
                           "—"]):
        T("·  " + a, cx3, ly + 86 + i * 24, col_w - 10, 20, 12,
          INK_TXT, "LEFT", nodes=n)

    # ================= 观测提示 =================
    ty = ly + lh + 18
    n.append(f'<Positioned left="{M}" top="{ty}" width="{CW}" '
             f'height="128"><Container width="{CW}" height="128" '
             f'color="#F6F2E8" borderRadius="12"/></Positioned>')
    T("观测提示（只引来源结论）", M + 16, ty + 12, 400, 20, 13, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    tips_l = ["日轮轮廓清晰可辨；层厚遮日则轮廓不可见",
              "层云不产生晕，唯极低温时可例外（HKO）",
              "层积云云底降低或失去抬升支撑时可发展为层云"]
    tips_r = ["雾层因升温或风速增大被抬升亦可形成层云",
              "与雨层云之别：层云以是否产生降水区分",
              "夜间 As/Ns 难辨时按降水有无记录（HKO）"]
    for i, t in enumerate(tips_l):
        T("·  " + t, M + 16, ty + 40 + i * 24, CW / 2 - 24, 20, 11.5,
          INK_TXT, "LEFT", nodes=n)
    for i, t in enumerate(tips_r):
        T("·  " + t, M + 16 + CW / 2, ty + 40 + i * 24, CW / 2 - 24, 20,
          11.5, INK_TXT, "LEFT", nodes=n)

    # ================= 拉丁词根 =================
    ry = ty + 128 + 14
    n.append(f'<Positioned left="{M}" top="{ry}" width="{CW}" '
             f'height="74"><Container width="{CW}" height="74" '
             f'color="#FFFFFF" borderRadius="12" '
             f'border="1 SOLID #E4DCC8"/></Positioned>')
    T("拉丁词根", M + 16, ry + 10, 200, 20, 12.5, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("stratum = 层、垫层", M + 16, ry + 32, 320, 24, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    T("拉丁语中性名词；层云即「平铺的层」——低而均匀、水平范围大",
      M + 16, ry + 56, CW - 32, 18, 11, INK_DIM, "LEFT", nodes=n)
    # 30 秒判别
    T("30 秒判别", M + 380, ry + 10, 200, 20, 12.5, ACCENT, "LEFT",
      "BOLD", nodes=n)
    T("灰幕 + 日月轮廓可辨 → 层云；完全蔽天且持续降水 → 雨层云；"
      "均匀灰层无云块 → 层云", M + 380, ry + 32, CW - 380 - 16, 40, 11.5,
      INK_TXT, "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 层云页 · S4 CIMO 表 15-1 · S5 NOAA JetStream · "
             "S6 香港天文台《云》电子书",
             "10 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    print("use b04_run.py")
