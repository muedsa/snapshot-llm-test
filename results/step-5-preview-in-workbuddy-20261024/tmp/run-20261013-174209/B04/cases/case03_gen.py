#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-03 卷云 Cirrus (Ci) 图鉴页（1080×1350，4:5 图鉴体例）。

来源：S2/S5（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（种/变种/附属清单、
辨识规则）/ S3（拉丁词根、1803 Howard）。插画为 DSL 绘制示意图，非照片。
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
M = 60  # 页边距
CW = W - 2 * M  # 960 内容宽


def ci_hook(cx: float, cy: float, s: float, color: str = "#FFFFFF") -> list[str]:
    """钩卷云 uncinus：一条上挑尾丝 + 顶部小钩（逗号形）。"""
    pts = []
    # 尾丝：自左下向右上挑
    for k in range(8):
        kt = k / 7
        pts.append((cx - s * 0.55 + s * 1.0 * kt,
                    cy + s * 0.55 - s * 0.85 * kt))
    # 钩：在顶端卷一小圈（约 270°）
    for k in range(9):
        a = math.radians(-90 + 30 * k)
        pts.append((cx + s * 0.45 + math.cos(a) * s * 0.22,
                    cy - s * 0.30 + math.sin(a) * s * 0.22))
    return polyline(pts, 2.4, color)


def ci_tangle(x: float, y: float, w: float, h: float,
              color: str = "#F0F5F9") -> list[str]:
    """乱卷云 intortus：交叉缠结的丝缕。"""
    out = []
    for i, (k, amp, ph) in enumerate([(1.6, 0.5, 0.0), (1.2, 0.42, 1.1),
                                      (2.0, 0.55, 2.2)]):
        pts = []
        for j in range(13):
            jt = j / 12
            pts.append((x + w * jt,
                        y + h * (0.5 + 0.5 * math.sin(jt * math.pi * k + ph)
                                 * (0.4 + 0.2 * i))))
        out.extend(polyline(pts, 2.0, color))
    return out


def dsl() -> str:
    n = []
    # 纸面
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("03", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("卷云", M + 62, 30, 400, 54, 44, INK_TXT, "LEFT", "BOLD", SERIF,
      spacing=6, nodes=n)
    T("Cirrus · Ci ｜ 高云族 ｜ 冰晶云", M + 64, 92, 600, 26, 16, INK_DIM,
      nodes=n)
    # 右上：族别签
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_HI}" borderRadius="17"/></Positioned>')
    T("高云族 · 5–13 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
      "CENTER", "BOLD", nodes=n)
    T("抬头读天 · 国际云图集十属", W - M - 300, 92, 300, 22, 12, "#98A6B2",
      "RIGHT", nodes=n)
    n.append(hline(M, 126, CW, "#D8CFBB", 1.2))

    # ================= 主图：天空剖面 =================
    py, ph = 142, 420
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="{ZENITH}" borderRadius="16"/></Positioned>')
    # 天色三段（高→低）
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

    # 高度轴（右侧）+ 卷云云底常用范围带
    ax_x = M + CW - 96
    n.extend(alt_axis(ax_x, py + 26, ph - 78, 14.0,
                      ticks=(2, 4, 6, 8, 10, 12), label_size=11,
                      color="#DCE8F2"))
    # 6–12 km 常用范围条
    n.extend(range_bar(ax_x + 12, py, 14, ph, 6.0, 12.0, 14.0,
                       "#FFFFFF55", ax_x, ph - 78))

    # —— 插画：三种卷云质地 ——
    # ① 毛卷云 fibratus：平直丝缕带（左上）
    n.extend(cirrus_band := [])  # 占位（无操作）
    for i in range(4):
        yy = py + 74 + i * 26
        pts = []
        for k in range(21):
            kt = k / 20
            pts.append((M + 90 + 330 * kt,
                        yy + 9 * math.sin(kt * math.pi * (1.1 + 0.35 * i))))
        n.extend(polyline(pts, 2.0, "#F4F8FB"))
    T("fibratus 毛卷云 · 平直丝缕", M + 90, py + 190, 320, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # ② 钩卷云 uncinus：三枚逗号钩（右上）
    for i, (hx, hy, s) in enumerate([(M + 520, py + 92, 44),
                                     (M + 640, py + 118, 52),
                                     (M + 560, py + 150, 38)]):
        n.extend(ci_hook(hx, hy, s))
    T("uncinus 钩卷云 · 逗号钩", M + 480, py + 190, 300, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # ③ 密卷云 spissatus：灰白厚片（中）
    n.append(f'<Positioned left="{M + 90}" top="{py + 240}" width="300" '
             f'height="46"><Container width="300" height="46" '
             f'color="#D9E4EC" borderRadius="23"/></Positioned>')
    n.append(f'<Positioned left="{M + 120}" top="{py + 248}" width="240" '
             f'height="18"><Container width="240" height="18" '
             f'color="#F4F8FB" borderRadius="9"/></Positioned>')
    T("spissatus 密卷云 · 灰白厚片", M + 90, py + 296, 320, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # ④ 乱卷云 intortus：缠结丝缕（右下）
    n.extend(ci_tangle(M + 470, py + 250, 330, 56))
    T("intortus 乱卷云 · 缠结丝缕", M + 470, py + 316, 320, 18, 11,
      "#C9DAE8", "LEFT", nodes=n)

    # 底部注：冰晶 + 示意图
    T("示意图（DSL 绘制，非照片）· 卷云几乎全由冰晶组成", M + 90,
      py + ph - 40, 620, 20, 11.5, "#9FB4C6", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 586, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成"),
        (684, 276, "质地与亮度"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="14" '
                 f'border="1 SOLID #E3DAC6"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12.5, ACCENT,
          "LEFT", "BOLD", nodes=n)

    # 卡 A：常用范围（km+ft 一行）+ 更宽范围注
    T("常用范围", M + 16, dy + 42, 150, 20, 12, INK_DIM, "LEFT", nodes=n)
    T("6–12 km", M + 16, dy + 62, 170, 28, 20, INK_TXT, "LEFT", "BOLD",
      MONO, nodes=n)
    T("20 000–40 000 ft", M + 16, dy + 90, 190, 18, 11.5, INK_DIM,
      "LEFT", "NORMAL", MONO, nodes=n)
    T("更宽范围：—（积雨云消散的卷云，冬季可远低于 6 km）", M + 200,
      dy + 62, 340, 40, 11, INK_DIM, "LEFT", nodes=n)

    # 卡 B：构成
    T("冰晶", M + 400, dy + 48, 200, 32, 22, INK_TXT, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("透明程度取决于冰晶的分离程度；穿过日面时几乎不削弱其亮度，"
      "异常厚时可遮蔽日轮轮廓", M + 400, dy + 82, 260, 32, 10.5,
      INK_DIM, "LEFT", nodes=n)

    # 卡 C：质地与亮度
    T("纤维状或丝绢光泽，或两者兼有", M + 700, dy + 44, 250, 20, 12,
      INK_TXT, "LEFT", "BOLD", nodes=n)
    T("日出前/日落后常染亮黄或红色，比低云更早被照亮、更晚褪色；"
      "任何时刻近地平线的卷云常带黄色（低角度光路长）", M + 700,
      dy + 68, 250, 46, 10.5, INK_DIM, "LEFT", nodes=n)

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
        ("种 species · 4", ["fibratus 毛卷云（纤维状）",
                            "uncinus 钩卷云（逗号钩）",
                            "spissatus 密卷云（灰白厚片）",
                            "castellanus 堡卷云（塔状突起）"]),
        ("变种 varieties · 4", ["intortus 乱卷云（缠结）",
                                "radiatus 辐辏卷云（辐射排列）",
                                "vertebratus 脊状卷云（鱼骨形）",
                                "duplicatus 复卷云（叠置层）"]),
        ("附属/从属 · 1", ["mamma 乳状云（云底垂悬半球）",
                           "—", "—", "—"]),
    ]
    for i, (ct, items) in enumerate(cols):
        cx0 = M + 26 + i * 306
        T(ct, cx0, ly + 82, 280, 22, 13.5, ACCENT, "LEFT", "BOLD",
          nodes=n)
        for j, it in enumerate(items):
            T(("· " + it) if it != "—" else it, cx0, ly + 110 + j * 26,
              290, 24, 12, INK_TXT if it != "—" else "#B9C4CE",
              "LEFT", nodes=n)

    # ================= 天气意义与观测提示 =================
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
    tips_l = ["卷云比邻近任何属更白；日落最晚褪色、日出最先显色（HKO）",
              "与卷积云之别：卷云呈纤维/丝绢，卷积云呈颗粒/波纹",
              "与卷层云之别：仅卷云为不连续结构、水平范围有限"]
    tips_r = ["密卷云常源自积雨云消散后的卷云（CIMO 表 15-1 注）",
              "钩卷云的钩为 ICA 正式描述的形态特征（uncinus）",
              "出现晕并非卷云特征——晕是卷层云在场的明确证据"]
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
    T("cirrus = 羽毛 · 丝缕", M + 20, ey + 34, 430, 26, 17, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    T("1803 年 Luke Howard 以拉丁词建立云的命名体系（WMO，S3）",
      M + 20, ey + 62, 430, 18, 10.5, INK_DIM, "LEFT", nodes=n)

    n.append(f'<Positioned left="{M + 490}" top="{ey}" width="470" '
             f'height="86"><Container width="470" height="86" '
             f'color="#FFFFFF" borderRadius="14" '
             f'border="1 SOLID #E3DAC6"/></Positioned>')
    T("30 秒判别", M + 510, ey + 12, 200, 20, 12, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("有纤维/丝绢光泽 → 卷云；见颗粒波纹 → 卷积云；"
      "成连续薄幕且见晕 → 卷层云", M + 510, ey + 34, 440, 44, 12.5,
      INK_TXT, "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 卷云页 · S4 CIMO 表 15-1 · "
             "S5 NOAA JetStream · S6 香港天文台《云》电子书",
             "03 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    out = dsl()
    print("WARN:", WARN)
    print("bytes", len(out.encode("utf-8")))
