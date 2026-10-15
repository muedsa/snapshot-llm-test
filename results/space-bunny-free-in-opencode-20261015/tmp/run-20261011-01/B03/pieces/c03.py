#!/usr/bin/env python
"""B03 case-03 · 玻璃瓶打样剖面确认单。

场景（自拟）：包装厂打样师与客户在评审会上逐项确认瓶型、注胶量与公差，
              确认后会打印 A3 挂图贴在样间。
独占手法：**ClipPath 的 SVG `A` 弧命令**画真实瓶型（瓶肩圆弧、瓶口圆角、瓶底倒圆），
          再用第二条裁剪路径挖出内腔，剩下的玻璃壁就是真实壁厚；
          瓶口局部用 `viewBox` + `fit="CONTAIN"` 开一个 8 倍的观察窗——
          裁剪路径的坐标映射被当成"放大镜"用。
"""
from __future__ import annotations

from b03kit import (assert_fits, clip, dashed_h, dashed_v, em_width, footer, gbox,
                    guard, line_h, para, solid, txt, MONO, W500, W600, W400, SERIF,
                    BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1480, 1100

CYAN, AMBER, RED, GREEN, WHITE = "#5BD1E6", "#F5B44A", "#FF6B6B", "#5FD3A0", "#E8F4FF"
PALE, GRID = "#8FB4D4", "#16304C"
PAPER = "#0F1D30"

OUTER = ("M29 320 L29 320 A10 10 0 0 1 39 330 L81 330 A10 10 0 0 1 91 320 "
         "L91 196 A14 14 0 0 1 77 182 L77 40 L77 34 A4 4 0 0 1 73 30 "
         "L47 30 A4 4 0 0 1 43 34 L43 182 A14 14 0 0 1 29 196 Z")
CAVITY = ("M33 308 L33 318 L87 318 L87 196 A10 10 0 0 1 73 186 "
          "L73 40 L47 40 L47 186 A10 10 0 0 1 33 196 Z")

OX1, OX2, OY = 110.0, 300.0, 240.0
TOPX, TOPY = 540.0, 340.0
PX, PW = 730.0, 1420.0 - 730.0

SPEC = [
    ("总高", "300.0", "±1.5", "300.6", False),
    ("瓶身外径", "φ62.0", "±0.8", "62.4", False),
    ("内径", "φ54.0", "±0.5", "54.8", True),
    ("瓶口外径", "φ34.0", "±0.4", "34.6", True),
    ("侧壁厚", "4.0", "±0.4", "4.1", False),
    ("底厚", "12.0", "±1.0", "12.4", False),
    ("肩高", "34.0", "±1.2", "34.0", False),
    ("灌装线容量", "500 mL", "±8", "492 mL", True),
]
PENDING = [
    "① 瓶口外径 34.6 — 超上限 0.2 mm，压盖机工位需重新对位后复测",
    "② 内径 54.8 — 偏大 0.8 mm，灌装线由 500 mL 下移至 492 mL",
    "③ 垂直度 1.4 mm — 超出 ≤1.0 限值，隔板输送段需重新校直",
]


def glass_fill(w, h):
    return (f'<Container width="{w:.2f}" height="{h:.2f}" gradientType="LINEAR"'
            f' gradientColors="#8FE2F770,#3C7FA828" gradientStops="0,1"'
            f' gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/>')


def build() -> str:
    b = []
    # ---------------- 底：深蓝晒图纸 + 网格
    b.append(gbox(0, 0, W, H, ["#0A1424", "#081120"], stops="0,1"))
    for gx in range(40, W, 40):
        b.append(rect(gx, 0, 1, H, "#1D3A5C" if gx % 200 else "#26496E", 0))
    for gy in range(40, H, 40):
        b.append(rect(0, gy, W, 1, "#16304C" if gy % 200 else "#1D3A5C", 0))

    # ---------------- 页头
    b.append(txt("打样确认单 · 自拟演示", 60, 52, 700, None, 20, CYAN, W600))
    b.append(txt("海盐柚子 500 mL 玻璃瓶 · 第二次打样剖面", 60, 86, 1000, None,
                 40, WHITE, W600))
    b.append(txt("瓶型编号 GL-500-H18 · 模具 M-0217 · 出图 2026-03-11 · 单位 mm",
                 60, 140, 1000, None, 19, PALE))
    b.append(dashed_h(60, W - 60, 172, "#234A70", 1.5, 9, 7))

    # ---------------- 视图标题
    for tx, name in ((OX1 - 20, "① 正视图"), (OX2 - 20, "② 纵剖面"),
                     (TOPX - 60, "③ 俯视图")):
        b.append(txt(name, tx, 198, 220, None, 22, CYAN, W600))

    # ---------------- ① ② 瓶型（同一局部路径，两次裁剪）
    def bottle_view(ox, section):
        bw, bh = 120.0, 340.0
        b.append(clip(ox, OY, bw, bh, OUTER, glass_fill(bw, bh)))
        b.append(clip(ox, OY, bw, bh, CAVITY,
                      f'<Container width="{bw}" height="{bh}" color="{PAPER}"/>'))
        if section:
            b.append(gbox(ox + 33, OY + 300, 54, 18, [AMBER, "#A86C24"], radius=0,
                          begin="TOP_CENTER", end="BOTTOM_CENTER"))
            b.append(solid(ox + 33, OY + 300, 54, 3, "#FFD08A"))
            b.append(dashed_h(ox + 30, ox + 90, OY + 168, AMBER, 2, 10, 7))
        b.append(dashed_v(ox + 60, OY - 16, OY + bh + 16, "#2F5C86", 1.5, 14, 5, 6))

    bottle_view(OX1, False)
    bottle_view(OX2, True)

    # ---------------- 尺寸标注（只保留正视图三条主线，其余进表）
    def vdim(x, y0, y1, label, col=CYAN, lw=96):
        b.append(segment(x, y0, x, y1, col, 1.5))
        for yy in (y0, y1):
            b.append(segment(x - 6, yy, x + 6, yy, col, 1.5))
        assert_fits(label, 18, lw, label)
        b.append(txt(label, x + 9, (y0 + y1) / 2 - 13, lw, None, 18, col))

    def hdim(y, x0, x1, label, col=CYAN):
        b.append(segment(x0, y, x1, y, col, 1.5))
        for xx in (x0, x1):
            b.append(segment(xx, y - 6, xx, y + 6, col, 1.5))
        mid = (x0 + x1) / 2
        assert_fits(label, 18, 160, label)
        b.append(txt(label, mid - 80, y + 9, 160, None, 18, col, align="CENTER"))

    vdim(222, OY + 30, OY + 330, "总高 300")
    hdim(OY + 420, OX1 + 29, OX1 + 91, "φ62.0")
    hdim(OY + 250, OX1 + 43, OX1 + 77, "φ34.0", PALE)
    # 壁厚引出线（向左出图，不与任何标注抢位置）
    b.append(segment(OX1 + 31, OY + 292, OX1 - 16, OY + 272, PALE, 1.5))
    b.append(txt("壁厚 4.0", 20, OY + 256, 92, None, 18, PALE, align="END"))
    # 注胶环 / 灌装线引出线
    b.append(segment(OX2 + 87, OY + 309, OX2 + 116, OY + 286, AMBER, 1.5))
    b.append(txt("注胶环 18", OX2 + 120, OY + 274, 140, None, 18, AMBER))
    b.append(segment(OX2 + 91, OY + 168, OX2 + 116, OY + 168, AMBER, 1.5))
    b.append(txt("灌装线 492 mL", OX2 + 120, OY + 156, 150, None, 18, AMBER))

    # ---------------- ③ 俯视图
    for d, col in ((62, "#7FD6EE66"), (54, PAPER), (34, "#7FD6EEAA"), (26, PAPER)):
        b.append(solid(TOPX - d / 2, TOPY - d / 2, d, d, col))
    for d in (62, 54, 34, 26):
        b.append(circle(TOPX, TOPY, d, None, border="1.5 SOLID #6FC9E0"))
    b.append(dashed_h(TOPX - 58, TOPX + 58, TOPY, "#2F5C86", 1.5, 14, 5, 6))
    b.append(dashed_v(TOPX, TOPY - 58, TOPY + 58, "#2F5C86", 1.5, 14, 5, 6))
    b.append(txt("φ62 外径", TOPX + 40, TOPY - 34, 140, None, 18, CYAN))
    b.append(txt("φ54 内径", TOPX + 40, TOPY - 6, 140, None, 18, PALE))
    b.append(txt("φ34 口 / φ26 孔", TOPX + 40, TOPY + 22, 140, None, 18, PALE))

    # ---------------- ④ 瓶口 8 倍观察窗
    DX, DY, DW, DH = 60, 640, 400, 240
    b.append(rect(DX - 16, DY - 42, DW + 32, DH + 116, "#0A1626", 10,
                  border="1 SOLID #234A70"))
    b.append(txt("④ 瓶口局部 8×", DX, DY - 32, 300, None, 21, CYAN, W600))
    b.append(txt("开窗 35 20 50 30 · CONTAIN", DX + 126, DY - 30, DW + 22 - 126,
                 None, 18, PALE, align="END"))
    b.append(clip(DX, DY, DW, DH, OUTER, glass_fill(DW, DH),
                  view_box="35 20 50 30", fit="CONTAIN"))
    b.append(clip(DX, DY, DW, DH, CAVITY, f'<Container width="{DW}" height="{DH}" '
                                           f'color="#0A1626"/>',
                  view_box="35 20 50 30", fit="CONTAIN"))
    b.append(dashed_v(DX + DW / 2, DY, DY + DH, "#2F5C86", 1.5, 12, 5, 6))
    b.append(txt("口外径实测 34.6（超上限 0.2）", DX, DY + DH + 12, DW, None, 19,
                 "#F0A98A", align="CENTER"))
    b.append(txt("口内壁与外口沿同心度不足，是本次超差的主因", DX, DY + DH + 38, DW,
                 None, 18, PALE, align="CENTER"))

    # ---------------- 右栏
    b.append(gbox(PX, 190, PW, 782, ["#0E1C2F", "#0B1626"], radius=12,
                  border="1 SOLID #234A70"))
    b.append(txt("关键尺寸与本次实测", PX + 26, 212, PW - 52, None, 23, WHITE, W600))
    b.append(txt("超差项用琥珀色标出，共 3 项；其余 5 项在公差内", PX + 26, 246,
                 PW - 52, None, 18, PALE))

    CX = [PX + 26, PX + 276, PX + 420, PX + 546]
    CW = [250, 144, 126, 148]
    TY = 284
    b.append(rect(PX + 26, TY, PW - 52, 40, "#16304C", 6))
    for i, t in enumerate(["项目", "图纸值", "公差", "本次实测"]):
        b.append(txt(t, CX[i] + 8, TY + 9, CW[i] - 16, None, 18, CYAN, W600,
                     align=None if i == 0 else "END"))
    ry = TY + 50
    for i, (name, draw, tol, real, bad) in enumerate(SPEC):
        rh = 46
        if i % 2 == 0:
            b.append(rect(PX + 26, ry, PW - 52, rh, "#102340", 4))
        col = AMBER if bad else WHITE
        if bad:
            b.append(rect(PX + 26, ry + 9, 3, rh - 18, AMBER, 2))
        b.append(txt(name, CX[0] + 16, ry + 12, CW[0] - 24, None, 20, col, W500))
        b.append(txt(draw, CX[1], ry + 13, CW[1] - 16, None, 19, "#B9D3EA", MONO,
                     align="END"))
        b.append(txt(tol, CX[2], ry + 13, CW[2] - 16, None, 19, "#B9D3EA", MONO,
                     align="END"))
        b.append(txt(real, CX[3], ry + 12, CW[3] - 16, None, 20, col, MONO, align="END"))
        ry += rh

    # ---- 待确认 3 项
    py = ry + 22
    b.append(rect(PX + 26, py, PW - 52, 4, AMBER, 2))
    b.append(txt("待确认 3 项（对应下一步动作）", PX + 26, py + 16, PW - 52, None,
                 21, AMBER, W600))
    yy = py + 50
    for t in PENDING:
        assert_fits(t, 18, PW - 52, t)
        b.append(txt(t, PX + 26, yy, PW - 52, None, 18, "#D9E5F2"))
        yy += 28

    # ---- 结论
    cy = yy + 10
    b.append(gbox(PX + 26, cy, PW - 52, 74, ["#12261C", "#0D1B14"], radius=8,
                  border="1 SOLID #2F6B4E"))
    b.append(solid(PX + 26, cy, 4, 74, GREEN))
    b.append(txt("本次打样结论：有条件通过", PX + 44, cy + 14, PW - 90, None, 21,
                 GREEN, W600))
    b.append(txt("3 项超差均在模具微调范围，不影响第 3 次打样开模。",
                 PX + 44, cy + 42, PW - 90, None, 18, "#BFD8C9"))
    guard(cy + 74, 0, 190 + 782 - 14, "结论框")

    # ---------------- 页脚
    footer(b, 60, 1010, W - 120,
           "瓶型、尺寸、公差与实测值均为自拟演示数据，非真实打样或客户记录 · " + DISCLAIM)
    guard(1060, 0, H, "页脚")
    return canvas(W, H, "".join(b), bg="#0A1424")


def case_note(size) -> str:
    return f"""# case-03 · 玻璃瓶打样剖面确认单

## 用户情境

- **受众**：包装厂打样师 + 客户对接人（评审会上一起看，会后打印挂图）。
- **什么时候、在哪里用**：评审会投屏，或打印 A3 贴在样间墙上随时比对实物。
- **真正要回答的问题**：瓶型对不对？壁厚与注胶量够不够？哪几项超差、下一步做什么？
- **领域**：包装结构 / 模具打样

## 这件独有的视觉决定

整张图的瓶型不是用矩形拼的，而是用**一条 `ClipPath` SVG 路径 + `A` 弧命令**
画出真实轮廓：瓶肩圆弧、瓶口圆角、瓶底倒圆都是弧。再用第二条裁剪路径挖出内腔，
剩下的部分就是真实壁厚；剖面底部填一块琥珀色表示注胶环（玻璃垫）。

同一路径还被用成**放大镜**：`viewBox="35 20 50 30"` + `fit="CONTAIN"` 把瓶口那一小块
映射到 400×240 的窗口里，等效 8 倍——裁剪路径的坐标映射第一次被当成「局部视图」使用，
而不是只用来裁形。

标注只保留正视图的三条主线（总高 / φ62 / φ34）加两条引出线；
肩高、底厚、壁厚这类数值交给右侧表格，避免一张图上同时出现两套同一信息。

- 画布 {W}×{H}；标注与表格文字 18–22px。

## 数据的可信度

瓶型编号、模具号、图纸尺寸、公差与实测值**全部自拟**，不是任何真实产品的
图纸或检测记录。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-03 的记录。

## 素材情况

纯 DSL，无 `<Image>`，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""