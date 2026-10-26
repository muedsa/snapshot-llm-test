#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-11 积云 → 积雨云 Cumulus / Cumulonimbus (Cu/Cb) 图鉴页。

1080×1920（9:16 竖幅）：从淡积云到积雨云的垂直发展序列——「云的工厂」。
来源：S5 NOAA（定义逐字）/ S4 CIMO 表 15-1（云底高度）/ S6 HKO（Cu→Cb 演化标志、
冰雹雷闪电必为 Cb、附属云清单）/ S3（拉丁词根）。插画为 DSL 绘制示意图，非照片。
"""
from __future__ import annotations

import math
import random
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

W, H = 1080, 1920
M = 60
CW = W - 2 * M


# ---------------------------------------------------------------- 积云团
def cumulus_mound(x: float, y: float, w: float, h: float,
                  seed: int = 7, shade: bool = True) -> list[str]:
    """积云团：3–5 个重叠圆叠成花椰菜状，顶亮底暗。"""
    rnd = random.Random(seed)
    out = []
    mounds = []
    for i in range(5):
        mx = x + w * (0.12 + 0.19 * i)
        mr = w * (0.16 + 0.05 * rnd.random())
        my = y + h * (0.52 - 0.30 * (1 - abs(i - 2) / 2.4))
        mounds.append((mx, my, mr))
    # 底部平暗底（cloud base 相对暗而平）
    out.append(rect(x, y + h * 0.52, w, h * 0.48, CLOUD_SHADE, radius=8))
    for mx, my, mr in mounds:
        out.append(circle(mx, my, mr * 2, CLOUD))
        if shade:
            out.append(circle(mx, my + mr * 0.34, mr * 1.3, CLOUD_DIM))
    # 顶部受日面亮斑
    out.append(circle(mounds[2][0], y + h * 0.30, w * 0.16, "#FFFFFF"))
    return out


def cumulus_tower(x: float, y: float, w: float, h: float,
                  stage: str = "mediocris") -> list[str]:
    """积云垂直发展三阶段。stage: humilis / mediocris / congestus"""
    rnd = random.Random(11)
    out = []
    if stage == "humilis":
        # 淡积云：扁平的云顶，垂直伸展有限
        out.append(rect(x, y + h * 0.62, w, h * 0.38, CLOUD_SHADE,
                        radius=8))
        for i, (mx, mr, my) in enumerate([(0.22, 0.20, 0.60),
                                          (0.50, 0.26, 0.50),
                                          (0.78, 0.20, 0.60)]):
            out.append(circle(x + w * mx, y + h * my, w * mr * 2, CLOUD))
    elif stage == "mediocris":
        # 中积云：中等垂直发展，轮廓清晰
        out.append(rect(x, y + h * 0.50, w, h * 0.50, CLOUD_SHADE,
                        radius=8))
        for mx, mr, my in [(0.20, 0.22, 0.46), (0.42, 0.30, 0.34),
                           (0.64, 0.30, 0.32), (0.84, 0.22, 0.46)]:
            out.append(circle(x + w * mx, y + h * my, w * mr * 2, CLOUD))
        out.append(circle(x + w * 0.52, y + h * 0.24, w * 0.17, "#FFFFFF"))
    else:
        # 浓积云 congestus：塔状，顶部花椰菜清晰
        out.append(rect(x, y + h * 0.34, w, h * 0.66, CLOUD_SHADE,
                        radius=8))
        for mx, mr, my in [(0.16, 0.20, 0.32), (0.36, 0.28, 0.24),
                           (0.58, 0.28, 0.18), (0.80, 0.22, 0.28),
                           (0.50, 0.30, 0.12)]:
            out.append(circle(x + w * mx, y + h * my, w * mr * 2, CLOUD))
        out.append(circle(x + w * 0.55, y + h * 0.12, w * 0.18, "#FFFFFF"))
        # 塔身旁侧小簇
        out.append(circle(x + w * 0.06, y + h * 0.46, w * 0.13, CLOUD))
    return out


def anvil_cloud(x: float, y: float, w: float, h: float) -> list[str]:
    """积雨云：砧顶（incus）+ 塔身 + 云底碎云。"""
    out = []
    # 砧顶：横向铺展的宽帽（上凸弧）
    out.append(rect(x, y, w, h * 0.16, CLOUD, radius=10))
    pts = []
    for k in range(17):
        kt = k / 16
        pts.append((x + w * kt, y + h * (0.10 - 0.10 * math.sin(math.pi * kt))))
    pts += [(x + w, y + h * 0.16), (x, y * 0.16 + h * 0.16)]
    out.extend(polyline(pts, 2.0, CLOUD))
    # 塔身：上部纤维（冰晶）→ 下部浓暗
    out.append(rect(x + w * 0.28, y + h * 0.14, w * 0.44, h * 0.30,
                    CLOUD_DIM, radius=8))
    out.append(rect(x + w * 0.22, y + h * 0.42, w * 0.56, h * 0.26,
                    CLOUD_SHADE, radius=8))
    # 云底：暗而平 + 碎雨云
    out.append(rect(x + w * 0.10, y + h * 0.66, w * 0.80, h * 0.14,
                    "#5E7285", radius=8))
    for i, (fx, fw) in enumerate([(0.12, 0.18), (0.34, 0.22), (0.60, 0.16),
                                  (0.78, 0.14)]):
        out.append(rect(x + w * fx, y + h * (0.82 + 0.05 * (i % 2)),
                        w * fw, h * 0.06, "#4A5C6E", radius=4))
    return out


def precipitation(x: float, y: float, w: float, h: float,
                  n_str: int = 12, hail: bool = False) -> list[str]:
    """阵性降水幡（praecipitatio）：密而不连续；可选冰雹点。"""
    out = []
    for i in range(n_str):
        rx = x + w * (0.06 + 0.088 * i)
        ln = h * (0.6 + 0.4 * ((i * 7) % 3) / 2)
        out.extend(polyline([(rx, y), (rx - 6, y + ln)], 1.8, "#7E93A6"))
    if hail:
        for i in range(4):
            hx = x + w * (0.15 + 0.22 * i)
            out.append(circle(hx, y + h * 0.75, 5, "#DCE6EE"))
    return out


def virga_fan(x: float, y: float, w: float, h: float) -> list[str]:
    """幡状云 virga：不下落的纤维尾。"""
    out = []
    for i in range(7):
        vx = x + w * (0.08 + 0.13 * i)
        out.extend(polyline([(vx, y), (vx - 4, y + h)], 1.4, "#8FA5B8"))
    return out


def lightning(x: float, y: float, w: float, h: float) -> list[str]:
    """闪电：折线（DSL 绘制）。"""
    pts = [(x + w * 0.5, y)]
    for i, (dx, dy) in enumerate([(-0.10, 0.22), (0.08, 0.44), (-0.06, 0.66),
                                  (0.04, 0.88)]):
        pts.append((x + w * (0.5 + dx), y + h * dy))
    return polyline(pts, 2.4, "#F5D78E")


def dsl() -> str:
    n = []
    n.append(grad(0, 0, W, H, ["#FBF8F1", PAPER_WARM], stops=[0, 1],
                  gtype="LINEAR", begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ================= 页头 =================
    T("11", M, 40, 70, 44, 20, ACCENT, "LEFT", "BOLD", MONO, nodes=n)
    T("积云 → 积雨云", M + 62, 30, 520, 54, 40, INK_TXT, "LEFT", "BOLD",
      SERIF, spacing=4, nodes=n)
    T("Cumulus · Cu ／ Cumulonimbus · Cb ｜ 低云族 ｜ 水滴 + 冰晶（对流塔）",
      M + 64, 92, 700, 26, 15, INK_DIM, nodes=n)
    n.append(f'<Positioned left="{W - M - 210}" top="44" width="210" '
             f'height="34"><Container width="210" height="34" '
             f'color="{SKY_LOW}" borderRadius="17"/></Positioned>')
    T("低云族 · 0.3–1.5 km", W - M - 210, 51, 210, 22, 13.5, "#FFFFFF",
      "CENTER", "BOLD", nodes=n)
    T("抬头读天 · 国际云图集十属", W - M - 300, 92, 300, 22, 12, "#98A6B2",
      "RIGHT", nodes=n)
    n.append(hline(M, 126, CW, "#D8CFBB", 1.2))

    # ================= 主图：垂直发展序列（4 阶段） =================
    py, ph = 142, 560
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="{SKY_MID}" borderRadius="16"/></Positioned>')
    # 天空分层（越高越深）
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph * 0.24}"><Container width="{CW}" '
             f'height="{ph * 0.24:.1f}" color="{ZENITH}" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.24}" width="{CW}" '
             f'height="{ph * 0.22:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.22:.1f}" color="{SKY_HI}"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py + ph * 0.46}" width="{CW}" '
             f'height="{ph * 0.54:.1f}"><Container width="{CW}" '
             f'height="{ph * 0.54:.1f}" color="#B9CCDC" '
             f'borderRadius="16"/></Positioned>')
    n.append(f'<Positioned left="{M}" top="{py}" width="{CW}" '
             f'height="{ph}"><Container width="{CW}" height="{ph}" '
             f'color="transparent" borderRadius="16" '
             f'border="1 SOLID #FFFFFF30"/></Positioned>')

    # 高度轴（右侧）
    ax_x = M + CW - 92
    n.extend(alt_axis(ax_x, py + 24, ph - 76, 12.0,
                      ticks=(2, 4, 6, 8, 10, 12), label_size=11,
                      color="#DCE8F2"))
    # 积云常用范围带
    n.extend(range_bar(ax_x + 12, py, 14, ph, 0.3, 1.5, 12.0,
                       "#FFFFFF55", ax_x, ph - 76))
    # 积雨云常用范围带（0.6–1.5 km）
    n.extend(range_bar(ax_x + 30, py, 14, ph, 0.6, 1.5, 12.0,
                       "#F5D78E40", ax_x, ph - 76))

    # —— 四阶段发展序列（从左到右）——
    stage_w = 214
    gap = 16
    stages = [
        ("① 淡积云 humilis", "扁平云顶，垂直伸展有限",
         lambda x, y, w, h: cumulus_tower(x, y, w, h, "humilis")),
        ("② 中积云 mediocris", "中等发展，轮廓清晰",
         lambda x, y, w, h: cumulus_tower(x, y, w, h, "mediocris")),
        ("③ 浓积云 congestus", "塔状，花椰菜顶清晰",
         lambda x, y, w, h: cumulus_tower(x, y, w, h, "congestus")),
        ("④ 积雨云 Cb", "砧顶铺展，阵性降水",
         lambda x, y, w, h: anvil_cloud(x, y, w, h)),
    ]
    for i, (title, sub, draw) in enumerate(stages):
        sx = M + 40 + i * (stage_w + gap)
        sy = py + 88
        sh = 330
        # 阶段底槽
        n.append(f'<Positioned left="{sx - 6}" top="{sy - 8}" '
                 f'width="{stage_w}" height="{sh + 70}">'
                 f'<Container width="{stage_w}" height="{sh + 70}" '
                 f'color="#FFFFFF14" borderRadius="10"/></Positioned>')
        n.extend(draw(sx, sy, stage_w - 12, sh))
        T(title, sx - 6, sy + sh + 14, stage_w + 10, 20, 12.5, "#FFFFFF",
          "LEFT", "BOLD", SERIF, nodes=n)
        T(sub, sx - 6, sy + sh + 38, stage_w + 10, 18, 10.5, "#D7E2EC",
          "LEFT", nodes=n)

    # 发展箭头（连接四阶段）
    for i in range(3):
        ax0 = M + 40 + i * (stage_w + gap) + stage_w - 14
        ay = py + 96
        n.extend(polyline([(ax0, ay + 60), (ax0 + 22, ay + 60)], 1.6,
                          "#F5D78E"))
        n.extend(polyline([(ax0 + 22, ay + 60), (ax0 + 14, ay + 54)], 1.6,
                          "#F5D78E"))
        n.extend(polyline([(ax0 + 22, ay + 60), (ax0 + 14, ay + 66)], 1.6,
                          "#F5D78E"))

    # 底部：降水 + 闪电
    n.extend(precipitation(M + 700, py + 400, 300, 90, 11, hail=True))
    n.extend(lightning(M + 770, py + 420, 40, 60))
    T("praecipitatio 降水幡 · 阵性降水，常较强但不持久",
      M + 660, py + ph - 44, 360, 18, 10.5, "#D7E2EC", "LEFT", nodes=n)

    T("示意图（DSL 绘制，非照片）", M + 40, py + ph - 44, 300, 20, 11.5,
      "#C4D2DE", "LEFT", nodes=n)

    # ================= 数据条 =================
    dy, dh = 726, 118
    cards = [
        (0, 372, "云底高度（WMO CIMO 表 15-1，温带）"),
        (384, 288, "构成与降水"),
        (684, 276, "Cu→Cb 演化标志"),
    ]
    for cx0, cw0, title in cards:
        n.append(f'<Positioned left="{M + cx0}" top="{dy}" width="{cw0}" '
                 f'height="{dh}"><Container width="{cw0}" height="{dh}" '
                 f'color="#FFFFFF" borderRadius="12" '
                 f'border="1 SOLID #E4DCC8"/></Positioned>')
        T(title, M + cx0 + 16, dy + 14, cw0 - 32, 20, 12, INK_DIM,
          "LEFT", nodes=n)
    # 卡 A：两属并列
    T("Cu 0.3–1.5 km ／ Cb 0.6–1.5 km", M + 16, dy + 40, 340, 28, 16,
      INK_TXT, "LEFT", "BOLD", MONO, nodes=n)
    T("Cu 1 000–5 000 ft ／ Cb 2 000–5 000 ft", M + 16, dy + 74, 340, 18,
      11.5, INK_DIM, "LEFT", "NORMAL", MONO, nodes=n)
    T("更宽范围 0.3–2 km（1 000–6 500 ft）；顶部可达中高层（WMO 2017）",
      M + 16, dy + 94, 340, 18, 11, "#98A6B2", "LEFT", nodes=n)
    # 卡 B
    T("水滴 → 冰晶", M + 400, dy + 40, 260, 28, 16, INK_TXT, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("Cu 受日面亮白、云底暗平；Cb 顶部柔软纤维（冰晶）",
      M + 400, dy + 74, 260, 18, 11, INK_DIM, "LEFT", nodes=n)
    T("降水：阵性、常较强但不持久", M + 400, dy + 94, 260, 18, 11,
      INK_DIM, "LEFT", nodes=n)
    # 卡 C
    T("穹顶清晰 → 顶部纤维", M + 700, dy + 40, 250, 28, 15, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    T("穹顶轮廓清晰（水滴）→ 柔软纤维（冰晶）即 Cu→Cb（HKO）",
      M + 700, dy + 74, 250, 34, 11, INK_DIM, "LEFT", nodes=n)
    T("见冰雹/雷/闪电 → 必为积雨云", M + 700, dy + 96, 250, 18, 11,
      ACCENT, "LEFT", "BOLD", nodes=n)

    # ================= ICA 清单 =================
    ly, lh = 866, 176
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
    # 种（Cu 4 + Cb 2）
    T("种 species · Cu 4 ／ Cb 2", cx1, ly + 62, col_w - 10, 20, 12,
      ACCENT, "LEFT", "BOLD", nodes=n)
    for i, sp in enumerate(["Cu：fractus（碎积云）",
                            "Cu：humilis（淡积云）",
                            "Cu：mediocris（中积云）",
                            "Cu：congestus（浓积云）",
                            "Cb：calvus（秃积雨云）",
                            "Cb：capillatus（毛发状）"]):
        T("·  " + sp, cx1, ly + 84 + i * 15, col_w - 10, 15, 10.5,
          INK_TXT, "LEFT", nodes=n)
    # 变种
    T("变种 varieties · 1 ／ 0", cx2, ly + 62, col_w - 10, 20, 12,
      ACCENT, "LEFT", "BOLD", nodes=n)
    for i, v in enumerate(["Cu：radiatus（辐辏状）",
                           "Cb：无",
                           "—",
                           "—"]):
        T("·  " + v, cx2, ly + 84 + i * 24, col_w - 10, 18, 11,
          INK_TXT, "LEFT", nodes=n)
    # 附属/从属
    T("附属/从属", cx3, ly + 62, col_w - 10, 20, 12, ACCENT, "LEFT",
      "BOLD", nodes=n)
    for i, a in enumerate(["Cu：pileus（幡状）",
                           "Cb：incus（砧顶）",
                           "Cb：mamma · virga",
                           "Cb：praecipitatio 降水幡",
                           "Cb：arcus · tuba（管状）",
                           "Cb：pannus · velum"]):
        T("·  " + a, cx3, ly + 84 + i * 15, col_w - 10, 15, 10.5,
          INK_TXT, "LEFT", nodes=n)

    # ================= 观测提示 =================
    ty = ly + lh + 18
    n.append(f'<Positioned left="{M}" top="{ty}" width="{CW}" '
             f'height="150"><Container width="{CW}" height="150" '
             f'color="#F6F2E8" borderRadius="12"/></Positioned>')
    T("观测提示（只引来源结论）", M + 16, ty + 12, 400, 20, 13, INK_TXT,
      "LEFT", "BOLD", SERIF, nodes=n)
    tips_l = ["晴天日照对流成云：上午出现、增长、傍晚消散（NOAA）",
              "见冰雹、雷、闪电 → 必为积雨云（HKO）",
              "积云「云的工厂」：顶部可产密卷云/高积云/高层云/层积云（HKO）"]
    tips_r = ["降水性积云在头顶时特征难辨，易与高层云/雨层云混淆（HKO）",
              "广布积雨云云底可貌似雨层云；阵性降水可区分（HKO）",
              "远看积云可似合并；保持分离仍记为积云（HKO）"]
    for i, t in enumerate(tips_l):
        T("·  " + t, M + 16, ty + 40 + i * 34, CW / 2 - 24, 30, 11.5,
          INK_TXT, "LEFT", nodes=n)
    for i, t in enumerate(tips_r):
        T("·  " + t, M + 16 + CW / 2, ty + 40 + i * 34, CW / 2 - 24, 30,
          11.5, INK_TXT, "LEFT", nodes=n)

    # ================= 拉丁词根 =================
    ry = ty + 150 + 14
    n.append(f'<Positioned left="{M}" top="{ry}" width="{CW}" '
             f'height="96"><Container width="{CW}" height="96" '
             f'color="#FFFFFF" borderRadius="12" '
             f'border="1 SOLID #E4DCC8"/></Positioned>')
    T("拉丁词根", M + 16, ry + 10, 200, 20, 12.5, ACCENT, "LEFT", "BOLD",
      nodes=n)
    T("cumulus = 堆积、堆；nimbus = 雨云", M + 16, ry + 32, 420, 24, 15,
      INK_TXT, "LEFT", "BOLD", SERIF, nodes=n)
    T("积云即「堆起来的云」；nimbus/nimbo 为降水词缀——雨层云、积雨云皆带此根",
      M + 16, ry + 58, CW - 32, 18, 11, INK_DIM, "LEFT", nodes=n)
    # 30 秒判别
    T("30 秒判别", M + 500, ry + 10, 200, 20, 12.5, ACCENT, "LEFT",
      "BOLD", nodes=n)
    T("棉堆状、轮廓清晰 → 积云；见砧顶/闪电/冰雹 → 积雨云；"
      "暗灰连续降水层 → 雨层云", M + 500, ry + 32, CW - 500 - 16, 48, 11.5,
      INK_TXT, "LEFT", nodes=n)

    # ================= 页脚 =================
    foot_bar(M, H - 40, CW,
             "S2 WMO ICA 积云/积雨云页 · S4 CIMO 表 15-1 · "
             "S5 NOAA JetStream · S6 香港天文台《云》电子书",
             "11 / 11", n)

    return snapshot(W, H, n, bg="#FBF8F1")


if __name__ == "__main__":
    print("use b04_run.py")
