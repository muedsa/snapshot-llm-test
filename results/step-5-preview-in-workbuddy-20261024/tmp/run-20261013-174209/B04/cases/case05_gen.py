#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-05 卷层云 Cirrostratus (Cs) 图鉴页（1080×1350，4:5 图鉴体例，含 22° 晕几何）。

来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种、晕证据论、
>30° 投影规则、霾色辨伪）/ S7 NWS + S8 Wikipedia + S9 Meteo.es（22° 晕角度与民谚）。
插画为 DSL 绘制示意图，非照片。
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


def hex_prism(cx: float, cy: float, r: float, color: str = "#DCE8F2",
              thick: float = 1.8) -> list[str]:
    """六棱柱截面：尖角朝左右的六边形（顶点 30°–330°）。"""
    pts = [(cx + r * math.cos(math.radians(30 + 60 * i)),
            cy + r * math.sin(math.radians(30 + 60 * i)))
           for i in range(6)]
    return polyline(pts + [pts[0]], thick, color)


def ray_deviation(cx: float, cy: float, r: float) -> list[str]:
    """22° 晕光路：水平入射 → 穿棱柱 → 偏离 ≈22° 出射 + 角弧标注。"""
    out = []
    # 入射面（左上斜面）中点与出射面（左下斜面）中点
    def face_mid(a0, a1):
        am = math.radians((a0 + a1) / 2)
        return (cx + r * math.cos(am), cy + r * math.sin(am))
    p_in = face_mid(120, 150)   # 上面左上斜面的中点（左上方）
    p_out = face_mid(210, 240)  # 下面左下斜面的中点（左下方）
    # 入射光线（自左来，略向上倾斜打到上入射面）
    out.extend(polyline([(p_in[0] - 150, p_in[1] - 86), p_in], 2.2,
                        "#FFFFFF"))
    # 棱柱内光路
    out.extend(polyline([p_in, p_out], 2.0, "#F2D8A0"))
    # 出射光线：沿出射面法线偏转约 22°（向下）
    ang = math.radians(22)
    ex = p_out[0] + 170 * math.cos(ang)
    ey = p_out[1] + 170 * math.sin(ang)
    out.extend(polyline([p_out, (ex, ey)], 2.2, "#F7E9C4"))
    # 原方向虚线（水平）
    out.extend(polyline([(p_out[0] - 40, p_out[1]),
                         (p_out[0] + 130, p_out[1])], 1.0, "#FFFFFF60"))
    # 22° 角弧
    arc = []
    for k in range(13):
        a = math.radians(22 * k / 12)
        rr = 74
        arc.append((p_out[0] + rr * math.cos(a), p_out[1] + rr * math.sin(a)))
    out.extend(polyline(arc, 1.4, "#F2D8A0"))
    out.append(T("≈22°", p_out[0] + 84, p_out[1] + 26, 70, 18, 12,
                 "#F2D8A0", "LEFT", "BOLD", MONO))
    return out


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("05", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("卷层云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Cirrostratus · Cs ｜ 高云族 ｜ 冰晶云", M + 64, 92, 600, 26, 16,
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

    # —— 插画①：薄幕 + 日轮 + 22° 晕（左上）——
    n.append(f'<Positioned left="{M + 60}" top="{py + 52}" width="420" '
             f'height="150"><Container width="420" height="150" '
             f'color="#E4EDF366" borderRadius="16"/></Positioned>')
    # 晕：外蓝边 + 内红边 + 本体圈（三层细环）
    sx, sy, hr = M + 300, py + 118, 62
    for rr, cc in [(hr + 5, "#9CC0E8"), (hr, "#FFFFFF50"), (hr - 5,
                   "#E8A9A0")]:
        n.append(f'<Positioned left="{sx - rr:.2f}" top="{sy - rr:.2f}" '
                 f'width="{rr * 2:.2f}" height="{rr * 2:.2f}">'
                 f'<Container width="{rr * 2:.2f}" height="{rr * 2:.2f}" '
                 f'shape="CIRCLE" color="transparent" '
                 f'border="2 SOLID {cc}"/></Positioned>')
    n.append(circle(sx, sy, 34, "#F7E9C4"))
    T("halo 22° 晕：外缘蓝、内缘红", M + 60, py + 210, 420, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # —— 插画②：22° 晕几何（六棱柱 + 光路）——
    hx, hy = M + 690, py + 130
    n.extend(hex_prism(hx, hy, 52))
    n.extend(ray_deviation(hx, hy, 52))
    T("冰晶六棱柱：最小偏向角 21.76°–22.37°", M + 520, py + 218, 400, 18,
      11, "#C9DAE8", "LEFT", nodes=n)

    # —— 插画③：fibrous/smooth 质地注记（底部）——
    T("薄幕均匀成层，纤维状或光滑外观；不全覆盖时边缘清晰，否则多毛边",
      M + 60, py + 250, 480, 40, 11.5, "#C9DAE8", "LEFT", nodes=n)
    T("示意图（DSL 绘制，非照片）", M + 60, py + ph - 40, 620, 20, 11.5,
      "#9FB4C6", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与光学"),
        (684, 276, "与霾 / 薄层云的区分"),
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
    T("更宽范围：—（高云三属共用 6 000–12 000 m）", M + 200, dy + 62,
      340, 40, 11, INK_DIM, "LEFT", nodes=n)

    T("薄层几乎全由冰晶组成", M + 400, dy + 42, 260, 24, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    T("日面高时整层从不厚到能挡住地面物影；晕几乎必然出现，是卷层云在场的明确证据",
      M + 400, dy + 70, 260, 46, 10.5, INK_DIM, "LEFT", nodes=n)

    T("霾貌似卷层云，但其独特黄/褐色可区分", M + 700, dy + 42, 250, 44,
      11.5, INK_TXT, "LEFT", nodes=n)
    T("乳状薄雾（或薄层云）的乳白幕 vs 卷层云：看有无晕、看颜色",
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
        ("种 species · 2", ["fibratus 毛卷层云（纤维状幕）",
                            "nebulosus 雾卷层云（无结构幕）",
                            "—", "—"]),
        ("变种 varieties · 2", ["undulatus 波状卷层云（幕面起伏）",
                                "duplicatus 复卷层云（叠置两层）",
                                "—", "—"]),
        ("附属/从属 · 无", ["（ICA 未列附属/从属云）", "—", "—", "—"]),
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
    tips_l = ["见晕 → 卷层云在场的明确证据（晕见于日月穿薄冰晶幕）",
              "日高角 ＞30° 时地面物影仍可辨；低于 30° 光路长、影弱难见",
              "外观与厚度随时间变化很小，显得移动缓慢"]
    tips_r = ["民谚「日晕三更雨」：晕示锋面接近，12–36 h 内雨（Meteo.es）",
              "与薄层云/霾之别：卷层云见晕、无色偏；霾带黄或褐色",
              "与卷云之别：卷层云为连续薄幕、可蔽全天；卷云不连续"]
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
    T("cirro- + stratus = 高空 + 平展层", M + 20, ey + 34, 430, 26, 16,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("stratus/strato = 平展·层状；cirro- = 羽毛·丝缕（高云三属共用）",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("连续薄幕 + 日月见 22° 晕 → 卷层云；纤维丝缕不连续 → 卷云；"
      "颗粒波纹 → 卷积云", M + 510, ey + 34, 440, 44, 12.5, INK_TXT,
      "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 卷层云页 · S4 CIMO 表 15-1 · S5 NOAA JetStream · "
             "S6 HKO《云》· S7 NWS · S8 Wikipedia · S9 Meteo.es",
             "05 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
