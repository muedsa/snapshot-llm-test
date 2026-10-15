#!/usr/bin/env python
"""B03 case-10 · 城南小剧场 · 本场演出（A2 海报）。

场景（自拟）：小剧场门口张贴的 A2 海报；同一张也用作售票页的缩略图。
独占手法：**描边大字（foregroundMode="STROKE"）+ 双色 textShadow 霓虹 +
          Transform 斜切信息条 + MIRROR 扫描渐变做舞台灯**。
              演出名用三层叠出来：底层实心洋红位移 8px、中层青色描边、
              顶层白色描边——服务端的文字没有渐变填充，
              于是用"位移 + 描边"模拟色差与灯管感，这是排印上的老办法，
              但每一层都是真实可渲染的 DSL 文字。
"""
from __future__ import annotations

from b03kit import (affine, assert_fits, em_width, footer, gbox, glow_text, guard,
                    para, radial, skew_tag, solid, spaced, strike_text, sweep, txt,
                    xform, MONO, W500, W600, W400, SERIF, BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1240, 1754

MAG, CYA, YEL, PAPER = "#FF3D9A", "#22D3EE", "#FFD166", "#F4F1EA"
BG1, BG2, BG3 = "#0B0714", "#140A22", "#0B0714"

SHOW = "夜航船"
BAND = "回声计划"
SUBJ = "新专辑《夜航船》首演 · 全场站票"
SETLIST = ["01  起航（器乐）", "02  夜航船", "03  铁皮屋顶",
           "04  低气压", "05  返航（安可）"]


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, [BG1, BG2, BG3], stops="0,0.52,1",
                  begin="TOP_CENTER", end="BOTTOM_CENTER"))

    # ---------------- 舞台灯：MIRROR 扫描渐变（角度对称的灯束）
    for i, (cx, cy, d, col) in enumerate((
            (300, 120, 900, MAG + "2E"), (940, 80, 860, CYA + "26"),
            (620, 40, 1100, YEL + "18"))):
        b.append(f'<Positioned left="{cx - d / 2:.0f}" top="{cy - d / 2:.0f}" '
                 f'width="{d}" height="{d}">'
                 f'<ClipOval clipBehavior="ANTI_ALIAS">'
                 f'<Container width="{d}" height="{d}" gradientType="SWEEP" '
                 f'gradientColors="{col},{col[:7]}00,{col}" '
                 f'gradientTileMode="MIRROR" gradientStartAngle="0" '
                 f'gradientEndAngle="6.2832"/></ClipOval></Positioned>')

    # 地平线：一条发光的地平线，把海报分成"舞台"和"信息"
    b.append(rect(0, 1010, W, 2, CYA + "66", 0))
    b.append(rect(0, 1004, W, 12, CYA + "14", 0))

    # ---------------- 顶部信息
    b.append(spaced("城南小剧场", 100, 96, 700, None, 30, PAPER, 14))
    b.append(spaced("CHENGNAN LIVE HOUSE", 100, 140, 700, None, 18, CYA, 6, W500))
    b.append(txt("第 118 期", W - 100 - 240, 100, 240, None, 24, MAG, W600,
                 align="END"))
    b.append(spaced("SAT 20:00", W - 100 - 240, 136, 240, None, 20, PAPER, 4,
                    W500, align="END"))

    # ---------------- 演出名：三层叠印
    size = 300
    sw = em_width(SHOW, size) * 1.06
    sx = (W - sw) / 2
    # 底层：实心洋红，位移 10px —— 模拟套色印刷的错位
    b.append(txt(SHOW, sx + 10, 300 + 10, sw + 20, size * 1.45, size, MAG, BLACK,
                 align="CENTER"))
    # 中层：青色描边 + 霓虹双影
    b.append(glow_text(SHOW, sx, 300, sw + 20, size * 1.45, size, "#220D1C",
                       "0 0 26 #22D3EEAA, 0 0 60 #22D3EE55",
                       weight=BLACK, align="CENTER"))
    b.append(f'<Positioned left="{sx:.0f}" top="300" width="{sw + 20:.0f}" '
             f'height="{size * 1.45:.0f}">'
             f'<Text textAlign="CENTER" fontSize="{size}" color="#220D1C" '
             f'foregroundColor="{CYA}" foregroundMode="STROKE" '
             f'foregroundStrokeWidth="5" fontFamily="{BLACK}">{SHOW}</Text></Positioned>')
    # 顶层：白色细描边压在最上，做出灯管的双线
    b.append(f'<Positioned left="{sx:.0f}" top="294" width="{sw + 20:.0f}" '
             f'height="{size * 1.45:.0f}">'
             f'<Text textAlign="CENTER" fontSize="{size}" color="#00000000" '
             f'foregroundColor="#FFFFFF" foregroundMode="STROKE" '
             f'foregroundStrokeWidth="1.6" fontFamily="{BLACK}">{SHOW}</Text>'
             f"</Positioned>")

    # ---------------- 副标题
    b.append(txt(BAND, 100, 760, 620, None, 44, PAPER, W600))
    b.append(spaced("ECHO PLAN", 100, 820, 620, None, 20, MAG, 8, W500))
    b.append(txt(SUBJ, 100, 848, 700, None, 22, "#B9A7C6"))

    # ---------------- 斜切信息条（文字必须和底色一起进 Transform，否则不会跟着斜）
    def skew_block(x, y, w, h, k, col, lab, val):
        return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
                f'<Transform matrix="({1:.6f},{k:.6f},0,0,{0:.6f},{1:.6f},0,0,'
                f'0,0,1,0,0,0,0,1)" alignment="CENTER">'
                f'<Container width="{w}" height="{h}" color="{col}" '
                f'borderRadius="8"/></Transform></Positioned>')

    b.append(skew_block(96, 920, 520, 88, 0.13, MAG, "日期", "12 月 6 日 · 周六"))
    b.append(skew_block(640, 920, 480, 88, -0.13, CYA, "场地", "城南小剧场 · 主厅"))
    # 文字画在斜切块之上同样的变换里（单独一层，保证和底色严格贴合）
    for x, w, k, lab, val, col in (
            (96, 520, 0.13, "日期", "12 月 6 日 · 周六", "#1A0A18"),
            (640, 480, -0.13, "场地", "城南小剧场 · 主厅", "#07161A")):
        b.append(xform(x, 920, w, 88, affine(1, k, 0, 1),
                       '<Container width="%d" height="88">'
                       '<Stack fit="EXPAND">%s%s</Stack></Container>' % (
                           w,
                           txt(lab, 34, 20, w - 68, None, 20, col, W600),
                           txt(val, 34, 48, w - 68, None, 28, col, W600))))

    # ---------------- 曲目
    b.append(spaced("曲目 SETLIST", 100, 1100, 500, None, 22, CYA, 6))
    b.append(rect(100, 1134, W - 200, 1, "#3A2A4A", 0))
    y = 1154
    for i, t in enumerate(SETLIST):
        col = YEL if i in (1, 3) else "#C8BCD4"
        b.append(txt(t, 100, y, 700, None, 24, col, W600 if i in (1, 3) else W500))
        b.append(txt(f"{4 + i * 3}:{(i * 17) % 60:02d}", W - 100 - 160, y + 3, 160,
                     None, 21, "#7E6F92", MONO, align="END"))
        y += 50
    b.append(rect(100, y + 6, W - 200, 1, "#3A2A4A", 0))

    # ---------------- 票价与购票
    ty = y + 40
    b.append(txt("票价", 100, ty, 160, None, 24, PAPER, W600))
    for i, (kind, price, note, col) in enumerate((
            ("早鸟", "88", "开演前 7 天截止", MAG),
            ("现场", "128", "含一杯气泡水", CYA))):
        x = 260 + i * 300
        b.append(rect(x, ty - 8, 272, 96, "#160C22", 10, border=f"1 SOLID {col}66"))
        b.append(txt(kind, x + 18, ty + 4, 90, None, 20, col, W600))
        b.append(txt("¥ " + price, x + 18, ty + 28, 180, None, 42, PAPER, BLACK))
        b.append(txt(note, x + 18, ty + 68, 240, None, 17, "#8E7FA4"))
    b.append(rect(880, ty - 8, 260, 104, MAG, 10))
    b.append(txt("购票", 898, ty + 2, 100, None, 20, "#1A0A18", W600))
    b.append(txt("扫码 / 剧场前台", 898, ty + 30, 230, None, 24, "#1A0A18", W600))
    b.append(txt("18 岁以下凭学生证半价", 898, ty + 66, 230, None, 17, "#3A0A22"))

    # ---------------- 底部
    b.append(txt("无障碍通道在剧场东侧 · 演出当晚 19:30 开放入场",
                 100, H - 168, 700, None, 20, "#8E7FA4"))
    b.append(txt("呈现", W - 100 - 320, H - 168, 320, None, 20, MAG, W600,
                 align="END"))
    footer(b, 100, H - 92, W - 200,
           "演出、乐队、曲目、票价与场地均为自拟演示内容 · " + DISCLAIM)
    guard(H - 20, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def case_note(size) -> str:
    return f"""# case-10 · 城南小剧场 · 本场演出（A2 海报）

## 用户情境

- **受众**：路过剧场门口的人（3 米外观看标题），以及来买票的人（1 米内读细节）。
- **什么时候用**：A2 张贴于门口与售票窗；同一张也是售票页的缩略图。
- **真正要回答的问题**：今晚演什么、谁演的、几点、去哪买票、多少钱。
- **领域**：演出海报 / 剧场宣传

## 这件独有的视觉决定

海报最要紧的是**标题在 3 米外能不能读出来**，所以标题用三层叠印做：

1. 底层实心洋红、位移 10px——模仿套色印刷的错位（riso 味）；
2. 中层青色描边（`foregroundMode="STROKE"`）+ 双色 `textShadow` 做霓虹光晕；
3. 顶层白色 1.6px 细描边压在最上，做出灯管的双线。

服务端的文字没有渐变填充，所以"发光"不是靠渐变糊出来的，
而是描边 + 双影阴影——每一层都是真实渲染的文字，不会糊、不会错位。

其余三件事也为"远看/近看"服务：
- 舞台灯用 `SWEEP` + `gradientTileMode="MIRROR"`，得到左右对称的角向灯束；
- 日期与场地用 `Transform` 斜切矩阵排成两条信息条，远看是两条斜线把视线引向中部；
- 曲目区用等宽数字排时间码，近看是可查的信息，远看是一列整齐的短行。

- 画布 {W}×{H}（A2 竖版）；标题 300px，最小正文 17px。

## 数据的可信度

演出、乐队、曲目、票价与场地**全部自拟**，不对应任何真实演出或售票信息。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-10 的记录。

## 素材情况

纯 DSL，无 `<Image>`；舞台灯与星点均由渐变与几何图元生成，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""