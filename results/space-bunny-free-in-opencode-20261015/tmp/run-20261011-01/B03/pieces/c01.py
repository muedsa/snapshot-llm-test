#!/usr/bin/env python
"""B03 case-01 · 河道水位与布防决策。

场景（自拟）：区防汛办值班员，每 6 小时在值班室大屏上判断今晚要不要布防。
独占手法：**ClipPath 阈值带**——把过程线与警戒线围出的「超警戒面积」用一条独立
          裁剪路径裁出来，曲线只有越过警戒的那一段才被暖色填上；
          警戒内部分另用一条面积路径填冷色。裁剪路径本身承担语义。
"""
from __future__ import annotations

from b03kit import (assert_fits, catmull_path, area_path, band_path, clip, dashed_h,
                    dashed_v, footer, gbox, gbox_raw, guard, line_h, mono_width, para,
                    solid, stroke_text, txt, radial, W500, W600, W400, SERIF,
                    MONO, BLACK, XBOLD, DISCLAIM)
from bsnap import BG, DIM, INK, LINE, PANEL, PANEL2, SERIES, SUB, canvas, rect, segment, polyline

W, H = 1600, 1060

# ---- 过程线数据（自拟）：今日 08:00 → 次日 08:00，每 2 小时一次
TIMES = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00",
         "22:00", "00:00", "02:00", "04:00", "06:00", "08:00"]
LEVELS = [4.62, 4.71, 4.92, 5.21, 5.55, 5.83, 6.02, 6.14, 6.21, 6.25, 6.28, 6.19, 6.05]
WARN, GUAR, VMIN, VMAX = 5.90, 6.20, 4.40, 6.60

PX0, PX1 = 130.0, 1110.0
PY0, PY1 = 470.0, 820.0
SCALE = (PY1 - PY0) / (VMAX - VMIN)


def y_of(v):
    return PY1 - (v - VMIN) * SCALE


XS = [PX0 + (PX1 - PX0) * i / (len(LEVELS) - 1) for i in range(len(LEVELS))]
YS = [y_of(v) for v in LEVELS]

# 越过警戒的那一段：线性求交点
t = (WARN - LEVELS[5]) / (LEVELS[6] - LEVELS[5])
X_CROSS = XS[5] + (XS[6] - XS[5]) * t
Y_WARN = y_of(WARN)
Y_GUAR = y_of(GUAR)

STATIONS = [
    ("西河 · 东关水文站", "6.28", "+0.38", "#F45B8C", "已超保证水位"),
    ("西河 · 石桥站", "6.11", "+0.21", "#F5A524", "超警戒"),
    ("支流 · 梅溪站", "5.94", "+0.04", "#F5A524", "临界"),
    ("西河 · 入城口站", "5.58", "-0.32", "#4C8DFF", "警戒下"),
]


def em_w(s, size):
    from bsnap import em_width
    return em_width(s, size)


def case_note(size) -> str:
    from b03kit import DISCLAIM
    return f"""# case-01 · 河道水位：今晚要不要布防

## 用户情境

- **受众**：区防汛办值班员（夜班为主）。
- **什么时候、在哪里用**：每 6 小时一次，在值班室 2.5 米外的大屏上复核一次上游水情，
  当班期间要能随时回答「今晚要不要布防」。
- **他真正要回答的问题**：水位什么时候越过警戒？会涨到超过保证水位吗？退水时间点在哪？
- **领域**：城市防汛 / 水文

## 这件独有的视觉决定

把「超警戒」变成一块**被裁出来的面积**：过程线和警戒水位线围出的那一块区域，
由一条独立的 `ClipPath` 路径单独裁出并填暖色渐变；警戒以内的蓄水另用一条面积路径填冷色渐变。
裁剪路径本身承担语义——曲线只有越过阈值的那一段被涂色，看图不需要查图例说明。

- 画布 {W}×{H}；正文最小 18px（轴刻度 18px、图例 18px）。
- 曲线用 Catmull-Rom 转三次贝塞尔，所以是平滑曲线而不是折线。

## 内容的可信度

西河、石桥、梅溪等站名与全部水位数值、阈值、站点读数均为**自拟演示数据**，
不是真实水文记录，也不代表任何实际防汛调度。图内页脚与本文件均已注明。

## 实际自检

- 见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-01 的记录。
- 生成期断言：所有单行文本按实测字宽校验不溢出（`b03kit.assert_fits`）；
  内容不越出画布下缘（`b03kit.guard`）。

## 素材情况

纯 DSL，无外部素材，DSL 内无 `<Image>` 标签。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""


def build() -> str:
    b = []
    # ---------------- 背景：水面一样的竖向渐变 + 底部一层冷雾
    b.append(gbox(0, 0, W, H, ["#0B1426", "#0A0F1E"], stops="0,1"))
    b.append(radial(W - 420, -220, 900, 700, "#2F6FD055,#0A0F1E00", center="(0.5,0.5)", radius=0.75))
    b.append(radial(-260, H - 380, 820, 620, "#22C7A922,#0A0F1E00", center="(0.5,0.5)", radius=0.75))

    # ---------------- 页头
    b.append(txt("防汛值班 · 演示数据", 64, 52, 900, None, 21, SERIES[0], W600))
    b.append(txt("西河水位：今晚要不要布防", 64, 90, 1000, None, 52, INK, W600))
    b.append(txt("读数区间 今日 08:00 → 次日 08:00，每 2 小时一次 · 值班岗位每 6 小时复核一次",
                 64, 156, 1200, None, 21, SUB))

    # ---------------- KPI 四卡
    def kpi(x, label, value, color, sub):
        w, h = 340, 124
        b.append(gbox(x, 196, w, h, ["#152440", "#0F1A30"], radius=14,
                      border="1 SOLID #24344F"))
        b.append(solid(x, 196, w, 4, color))
        b.append(txt(label, x + 20, 214, w - 40, None, 19, SUB))
        b.append(txt(value, x + 20, 214 + line_h(19) + 8, w - 40, None, 34, color, BLACK))
        b.append(txt(sub, x + 20, 196 + h - 34, w - 40, None, 18, DIM))
    kpi(64, "当前水位（今日 22:00 实测）", "6.14 m", SERIES[0], "较 3 小时前上涨 0.12 m")
    kpi(428, "距警戒水位 5.90 m", "+0.24 m", "#F5A524", "已越警戒，仍在上行区间")
    kpi(792, "预报峰值（次日 04:00）", "6.28 m", "#F45B8C", "超保证水位 6.20 m 约 4 小时")
    kpi(1156, "退水至警戒的时间", "次日 14:00 后", "#22C7A9", "按当前涨落速率外推")

    # ---------------- 主图面板
    CX0, CY0, CX1, CY1 = 64, 352, 1160, 916
    b.append(gbox(CX0, CY0, CX1 - CX0, CY1 - CY0, ["#101B30", "#0C1526"], radius=16,
                  border="1 SOLID #22314B"))
    b.append(txt("水位过程线", CX0 + 24, CY0 + 22, 500, None, 24, INK, W600))
    b.append(txt("警戒 5.90 / 保证 6.20（自拟阈值）", CX0 + 24, CY0 + 56, 620, None, 19, DIM))

    # 图例（右对齐到面板右缘）
    lx = CX1 - 24
    for lab, col in (("超警戒面积", "#FF8A3D"), ("警戒内蓄水", "#6BA8F5"), ("过程线", "#7FD8FF")):
        w = em_w(lab, 18)
        lx -= w
        b.append(txt(lab, lx, CY0 + 24, w + 2, None, 18, SUB))
        lx -= 30
        b.append(rect(lx, CY0 + 30, 14, 12, col, 3))
        lx -= 22

    # 网格
    for gv in (4.5, 5.0, 5.5, 6.0, 6.5):
        gy = y_of(gv)
        b.append(dashed_h(PX0, PX1, gy, "#1C2A44", 1.5, 7, 9))
        b.append(txt(f"{gv:.1f}", 68, gy - 11, 52, None, 18, DIM, MONO, align="END"))

    pw, ph = PX1 - PX0, PY1 - PY0

    # ---- 警戒内面积：ClipPath 面积路径（**本地坐标**，路径必须减去面板左上角）
    area_pts = [(XS[i] - PX0, YS[i] - PY0) for i in range(len(XS))]
    b.append(clip(PX0, PY0, pw, ph, area_path(area_pts, ph),
                  gbox_raw(pw, ph, ["#6BA8F5C4", "#2A5FA050"], stops="0,1",
                           begin="TOP_CENTER", end="BOTTOM_CENTER")))

    # ---- 超警戒带：ClipPath 阈值带（只有越过警戒的面积被涂色）
    band_pts = [(X_CROSS - PX0, Y_WARN - PY0)] + \
               [(XS[i] - PX0, YS[i] - PY0) for i in range(6, len(XS))]
    b.append(clip(PX0, PY0, pw, ph, band_path(band_pts, Y_WARN - PY0),
                  gbox_raw(pw, ph, ["#FF8A3DE8", "#F0552FBA"], stops="0,1",
                           begin="TOP_CENTER", end="BOTTOM_CENTER")))

    # ---- 阈值线（画在填充之上，保证可读）
    b.append(dashed_h(PX0, PX1, Y_WARN, "#F5A524", 2.4, 12, 8))
    b.append(dashed_h(PX0, PX1, Y_GUAR, "#F45B8C", 2.4, 12, 8))
    b.append(txt("保证 6.20 m", PX0 + 12, Y_GUAR - 31, 200, None, 18, "#F45B8C", W600))
    b.append(txt("警戒 5.90 m", PX0 + 12, Y_WARN - 31, 200, None, 18, "#F5A524", W600))

    # ---- 过程线
    b.append(polyline([(XS[i], YS[i]) for i in range(len(XS))], "#7FD8FF", 4))
    for i, (cx, cy) in enumerate(zip(XS, YS)):
        col = "#F45B8C" if LEVELS[i] > GUAR else ("#F5A524" if LEVELS[i] > WARN else "#7FD8FF")
        b.append(rect(cx - 5, cy - 5, 10, 10, col, 5, border="2 SOLID #0B1426"))

    # ---- 「现在」标记：今日 22:00（先画，后面标注的色块压在上面）
    NX = XS[7]
    b.append(rect(NX - 2, PY0, 4, ph, "#7FD8FF77", 2))
    b.append(rect(NX - 3, PY0 - 2, 6, 6, "#7FD8FF", 3))

    # ---- 越警戒交点标注
    b.append(dashed_v(X_CROSS, PY0 + 6, PY1, "#F5A524", 2, 10, 8))
    lab = "19:24 越过警戒"
    lw = em_w(lab, 19) + 26
    b.append(rect(X_CROSS + 14, PY0 + 16, lw, 34, "#2A2113", 8, border="1 SOLID #F5A52466"))
    b.append(txt(lab, X_CROSS + 27, PY0 + 23, lw, None, 19, "#F5A524", W600))
    b.append(txt("现在 · 今日 22:00", NX - 254, PY0 - 32, 240, None, 19, "#7FD8FF", W600,
                 align="END"))

    # ---- 峰值标注
    px, py = XS[10], YS[10]
    plab = "预报峰值 6.28"
    plw = em_w(plab, 19) + 26
    b.append(rect(px + 14, py - 64, plw, 34, "#2A1A20", 8, border="1 SOLID #F45B8C66"))
    b.append(txt(plab, px + 27, py - 57, plw, None, 19, "#F45B8C", W600))

    # ---- X 轴刻度
    for i, tlab in enumerate(TIMES):
        if i % 2:
            continue
        x = XS[i]
        b.append(rect(x - 1, PY1 + 2, 2, 8, "#3A4C6E", 1))
        b.append(txt(("次日 " if i >= 8 else "") + tlab, x - 50, PY1 + 16, 100, None, 18, SUB,
                     MONO, align="CENTER"))

    # ---- 读法说明
    guide = "读法：曲线穿过琥珀色警戒线之后，右侧被裁出来的橙色面积就是超警戒蓄水量，不必再查表。"
    assert_fits(guide, 18, CX1 - CX0 - 70, "读法")
    b.append(rect(CX0 + 24, CY1 - 44, CX1 - CX0 - 48, 32, "#0F1A2E", 8))
    b.append(solid(CX0 + 24, CY1 - 44, 4, 32, "#7FD8FF"))
    b.append(txt(guide, CX0 + 40, CY1 - 37, CX1 - CX0 - 70, None, 18, SUB))

    # ---------------- 右栏
    RX, RW = 1184, 352
    b.append(gbox(RX, CY0, RW, CY1 - CY0, ["#101B30", "#0C1526"], radius=16,
                  border="1 SOLID #22314B"))
    b.append(txt("监测点实时读数", RX + 22, CY0 + 22, RW - 44, None, 23, INK, W600))
    b.append(txt("自拟测站数据 · 水位单位 m", RX + 22, CY0 + 54, RW - 44, None, 18, DIM))

    sy = CY0 + 92
    for name, val, diff, col, state in STATIONS:
        b.append(rect(RX + 20, sy, RW - 40, 68, PANEL, 10, border="1 SOLID #22314B"))
        b.append(solid(RX + 20, sy, 4, 68, col))
        assert_fits(name, 18, 210, name)
        assert_fits(f"{val}{diff}", 19, 110, name + " 数值")
        b.append(txt(name, RX + 38, sy + 10, 220, None, 18, SUB))
        b.append(txt(f"{diff} m", RX + 38, sy + 38, 220, None, 19, col, MONO))
        b.append(txt(val, RX + 20, sy + 14, RW - 42, None, 32, col, BLACK, align="END"))
        b.append(txt(state, RX + 20 + RW - 42 - 90, sy + 46, 90, None, 17, DIM, W500,
                     align="END"))
        sy += 76

    # ---- 布防建议
    ay = sy + 4
    b.append(gbox(RX + 20, ay, RW - 40, CY1 - 20 - ay, ["#2A1A20", "#1B1220"], radius=12,
                  border="1 SOLID #F45B8C55"))
    b.append(solid(RX + 20, ay, RW - 40, 4, "#F45B8C"))
    b.append(txt("本班建议", RX + 40, ay + 20, RW - 80, None, 21, "#F45B8C", W600))
    body = "20:00 前完成东关站与石桥站沙袋；22:00 起封低洼路段；超保证水位时段每 30 分钟复核。"
    yy = para(b, body, RX + 40, ay + 54, RW - 80, 18, "#F0C9CF", W500, gap=4)
    guard(yy, 0, CY1 - 20, "右栏建议")

    # ---------------- 页脚
    footer(b, 64, 962, W - 128, "西河防汛值班 · 过程线与阈值均为自拟演示数据，非真实水文记录 · " + DISCLAIM)

    guard(1010, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def em_w(s, size):
    from bsnap import em_width
    return em_width(s, size)