#!/usr/bin/env python
# B03 · 十件作品探索 DSL 的创意边界。
# 每一件都在一个真实使用场景里落地一种**已验证可用**的手法，
# 不是「滤镜名 + 小方块」的能力示范板。
# 启动基准：总任务根 (suite_root)。用法：python build_b03.py [all|1..10] [ver]
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
from bsnap import (BG, DIM, INK, LINE, PANEL, PANEL2, SERIES, SUB, W500, W600,
                   bullets, canvas, circle, em_width, footer, header, kpi_row,
                   line_h, polyline, rect, segment, txt, wrap)

DRAFTS = ROOT / "tmp/run-20261011-01/B03/drafts"
CREAM = "#F5F0E6"
INKD = "#141A22"
CARD = "#1B2430"


def _mat(deg: float) -> str:
    """把二维旋转角度转成服务要求的 16 个 Float、列主序、无空格的 4x4 矩阵。"""
    c, s2 = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (f"{c:.5f},{s2:.5f},0,0,{-s2:.5f},{c:.5f},0,0,"
            f"0,0,1,0,0,0,0,1")


# ══════════════ 01 ClipPath 的 EVEN_ODD 镂空 → 爵士演出海报
def c01():
    """真实场景：社区爵士酒吧的月度演出海报。

    手法：ClipPath 用**两条同向轮廓 + fillRule="EVEN_ODD"** 挖出中间的圆孔。
    这是文档里明确写的镂空用法；首版试过 NON_ZERO，同向轮廓挖不出孔，
    实测图上中心仍然是实心的——这条差异写在 technique-notes 里。
    """
    W, H = 1000, 1400
    b = [rect(0, 0, W, H, INKD)]
    # 海报主体：EVEN_ODD 挖出方环，镂空处直接放标题——底色透上来才是「真镂空」
    b.append('<Positioned left="170" top="300" width="660" height="660">'
             '<ClipPath path="M0 0 H100 V100 H0 Z M18 18 H82 V82 H18 Z" '
             'viewBox="0 0 100 100" fit="CONTAIN" fillRule="EVEN_ODD">'
             '<Container color="#E0A93B"/></ClipPath></Positioned>')
    b.append(txt("BLUE", 170, 470, 660, None, 120, INK, W600, align="CENTER"))
    b.append(txt("HOUR", 170, 604, 660, None, 54, "#E0A93B", W600,
                 align="CENTER"))
    b.append(txt("午夜场", 170, 676, 660, None, 30, "#8FA8C4", align="CENTER"))
    # 方环四角加细线，指明这是被裁出来的轮廓而不是画出来的框
    for _sx, _sy in ((170, 300), (830, 300), (170, 960), (830, 960)):
        b.append(circle(_sx, _sy, 14, "#E0A93B"))

    b.append(txt("社区爵士酒吧", 80, 90, 600, None, 26, "#E0A93B"))
    b.append(txt("七月演出", 80, 140, 800, None, 92, INK, W600))
    # 原 258 会让字下沿正好落在方环上沿 300 上（图上相切），上移到 240 留净空
    b.append(txt("BLUE HOUR 午夜场", 80, 240, 800, None, 34, "#8FA8C4"))
    prog = [("07.05", " Lena Ito 四重奏"), ("07.12", " 老城三重奏"),
            ("07.19", "  Guest 专场"), ("07.26", "  月末即兴")]
    y = 960
    for d, t in prog:
        b.append(rect(80, y, 840, 1, "#24303E"))
        b.append(txt(d, 80, y + 16, 160, None, 30, "#E0A93B", W600))
        b.append(txt(t, 260, y + 18, 600, None, 26, INK))
        y += 72
    b.append(txt("每周五 21:00 · 旧仓街 27 号 · 凭本海报半价", 80, y + 14, 840,
                 None, 24, "#8FA8C4"))
    footer(b, 80, H - 64, 840, "海报为设计稿；场次与地址为示例")
    return canvas(W, H, "".join(b), INKD)


# ══════════════ 02 Text 的 STROKE 描边模式 → 夜跑队服
def c02():
    """真实场景：夜跑团的队服背面大字。

    手法：Text 的 `foregroundMode="STROKE"` 出**空心描边字**，
    再在同一位置叠一层同字号的实心字错位 6px，做出「套色没对准」的印刷感。
    空心字在实心深底上是另一套视觉语言，适合做队服背号。
    """
    W, H = 1200, 1200
    b = [rect(0, 0, W, H, "#101B16")]
    # 底纹：斜向细线，模拟网眼布
    for i in range(-40, 120):
        b.append(segment(i * 14, 0, i * 14 + 900, H, "#16261F", 1))
    b.append(txt("夜潮夜跑团", 80, 90, 600, None, 28, "#4ADE80"))
    
    # 主标题：**只描边不填充**的空心字，笔画内部透出网眼布底纹
    b.append(f'<Positioned left="110" top="300" width="980" height="330">'
             f'<Text textAlign="CENTER" fontSize="250" '
             f'foregroundColor="#8CF0B8" foregroundMode="STROKE" '
             f'foregroundStrokeWidth="10" fontFamily="Inter Semi Bold,Inter" '
             f'text="NIGHT"/></Positioned>')
    # 副标题上做套色错位：深绿实心 + 亮绿实心错开 7px，字号小、笔画粗，错位感最明显
    b.append(txt("夜潮夜跑团 · 2026 夏", 120, 672, 960, None, 52, "#1E7A4F",
                 W600, align="CENTER"))
    b.append(txt("夜潮夜跑团 · 2026 夏", 113, 665, 960, None, 52, "#8CF0B8",
                 W600, align="CENTER"))
    b.append(txt("每周三 · 19:30 · 东湖环线 8km", 120, 764, 960, None, 34,
                 "#4ADE80", align="CENTER"))
    b.append(rect(120, 838, 960, 2, "#1E4436"))
    rows = [("周 三", "19:30", "东湖环线 8 km", "领队：周 珩"),
            ("周 六", "06:30", "滨江线 12 km", "领队：陈 禾"),
            ("备 选", "周日 19:30", "城西 6 km 慢跑", "领队：M. Ito")]
    y = 884
    for a, b2, c, d in rows:
        b.append(txt(a, 120, y, 180, None, 26, "#8CF0B8", W600))
        b.append(txt(b2, 320, y, 220, None, 24, INK))
        b.append(txt(c, 560, y, 320, None, 24, INK))
        b.append(txt(d, 900, y, 180, None, 22, "#2F5A45", align="END"))
        y += 56
    b.append(rect(120, 1064, 960, 1, "#16261F"))
    b.append(txt("队服背面：空心字为单色丝印，主标题只描边不填充；"
                 "副标题做 7px 套色错位", 120, 1078, 960, None, 22, "#3E7A5C"))
    footer(b, 80, H - 60, 1040, "队服背面设计稿；姓名与路线为示例")
    return canvas(W, H, "".join(b), "#101B16")


# ══════════════ 03 径向渐变 → 潮汐预报
def c03():
    """真实场景：海滨城市的每日潮汐预报卡。

    手法：`gradientType="RADIAL"` 把每小时潮位映射成从中心向外的半径，
    半径越长潮越高，渐变把高潮与低潮自然分开。

    渐变 Container 是不透明的，必须画在**所有数据之前**——首版把它 append 在
    最后，840×840 的方块把标题、24 个潮位点、页脚全盖住了。
    """

    W, H = 1200, 900
    b = [rect(0, 0, W, H, "#071A22")]
    b.append(rect(0, 0, W, 172, "#0B2430"))
    b.append(txt("潮汐预报", 64, 36, 500, None, 26, "#5FD3E8"))
    b.append(txt("2026-07-18 · 望月", 64, 80, 700, None, 46, INK, W600))
    b.append(txt("高潮 21:07 · 4.2 m", 700, 46, 436, None, 30, "#5FD3E8",
                 align="END"))
    b.append(txt("低潮 15:22 · 1.1 m", 700, 96, 436, None, 26, "#4A7F93",
                 align="END"))

    CX, CY = 430, 524
    hours = [i * 0.5 for i in range(24)]
    levels = [1.6, 1.9, 2.3, 2.7, 3.1, 3.5, 3.9, 4.2, 4.1, 3.8, 3.4, 3.0,
              2.6, 2.2, 1.7, 1.4, 1.1, 1.2, 1.5, 1.9, 2.4, 2.9, 2.5, 2.0]
    # ① 先铺径向柔光底。它是不透明的，必须画在**所有数据之前**。
    #    gradientCenter 只能给对齐常量，所以把 Container 缩到正好盖住极坐标区再摆位。
    b.append('<Positioned left="130" top="224" width="600" height="600">'
             '<Container width="600" height="600" gradientType="RADIAL" '
             'gradientColors="#9BE8F5,#5FD3E8,#1E6C86" '
             'gradientStops="0,0.22,1" gradientCenter="CENTER" '
             'gradientRadius="0.72" gradientFocal="CENTER" '
             'gradientFocalRadius="0.22"/></Positioned>')
    b.append(circle(CX, CY, 274, "#5FD3E81A"))
    # ② 再画基准圈与小时刻度
    for rr in (112, 186, 260):
        b.append(circle(CX, CY, rr * 2, None, border=f"1 SOLID #0B243055"))
    for k in range(0, 24, 2):
        a = (k / 24) * math.tau - math.pi / 2
        b.append(segment(CX + 118 * math.sin(a), CY - 118 * math.cos(a),
                         CX + 274 * math.sin(a), CY - 274 * math.cos(a),
                         "#0B243088", 1))
        b.append(txt(f"{k:02d}", CX + 292 * math.sin(a) - 26,
                     CY - 292 * math.cos(a) - 13, 52, None, 18, "#7FB6C9",
                     align="CENTER"))
    # ③ 最后才是 24 个潮位点
    for h, lv in zip(hours, levels):
        a = (h / 24) * math.tau - math.pi / 2
        r = 90 + 160 * (lv / 4.2)
        x, y = CX + r * math.sin(a), CY - r * math.cos(a)
        hi = lv >= 3.5
        b.append(circle(x, y, 30, "#071A22"))
        b.append(circle(x, y, 26, "#9BE8F5" if hi else "#0B4A5C"))
    b.append(circle(CX, CY, 90, "#071A22"))
    b.append(circle(CX, CY, 90, None, border="2 SOLID #9BE8F5"))
    b.append(txt("潮位", CX - 86, CY - 40, 172, None, 24, "#9BE8F5", W600,
                 align="CENTER"))
    b.append(txt("1.1 – 4.2 m", CX - 86, CY + 4, 172, None, 18, "#5FD3E8",
                 align="CENTER"))

    # ④ 右侧逐时表：条 x=970 宽 100（最长到 1070），值右对齐 1082–1160，互不重叠
    X0 = 860
    b.append(txt("时刻", X0, 224, 110, None, 20, "#7FB6C9", W600))
    b.append(txt("潮位", X0 + 110, 224, 100, None, 20, "#7FB6C9", W600))
    b.append(txt("m", X0 + 218, 224, 78, None, 20, "#7FB6C9", W600,
                 align="END"))
    b.append(rect(X0, 250, 300, 1, "#1E4A5C"))
    for i, (h, lv) in enumerate(zip(hours, levels)):
        y = 262 + i * 24
        hi = lv >= 3.5
        b.append(txt(f"{h:04.1f}", X0, y, 110, None, 18, INK))
        b.append(rect(X0 + 110, y + 6, 100, 9, "#0B4A5C", 5))
        b.append(rect(X0 + 110, y + 6, 100 * lv / 4.2, 9,
                      "#5FD3E8" if hi else "#1E6C86", 5))
        b.append(txt(f"{lv:.1f}", X0 + 218, y, 78, None, 18,
                     "#5FD3E8" if hi else "#7FB6C9", align="END"))
    # 宽度只能给 300px（X0=860 到画布右缘），超过就被静默裁掉，故文案要短
    b.append(txt("青色 = 高潮 ≥ 3.5 m", X0, 840, 300, None, 17, "#5FD3E8"))
    footer(b, 64, H - 44, 700, "预报为示例；潮位数据非实时")
    return canvas(W, H, "".join(b), "#071A22")


def c04():
    """真实场景：独立厂牌的唱片封套（内页）。

    手法：`gradientType="SWEEP"` 画**扇形色盘**，再叠同心圆环模拟唱片沟槽。
    扇形渐变在其它标签上很难用到，这里正好对应黑胶旋转的视觉隐喻。
    """
    W, H = 1000, 1000
    b = [rect(0, 0, W, H, "#0E0E12")]
    b.append('<Positioned left="0" top="0" width="1000" height="1000">'
             '<Container width="1000" height="1000" gradientType="SWEEP" '
             'gradientColors="#FF3B6B,#FFB03B,#4ADE80,#3BA7FF,#9B6BFF,#FF3B6B" '
             'gradientStartAngle="0" gradientEndAngle="6.2832" '
             'gradientCenter="CENTER" gradientTileMode="CLAMP"/>'
             '</Positioned>')
    # 首版压了 #0E0E1244 的暗层，把扇形渐变压成灰扑扑的粉彩 → 减到 1A
    b.append(rect(0, 0, 1000, 1000, "#0E0E121A"))
    # SWEEP 的 gradientCenter 只能给对齐常量，所以唱片中心必须与画布正中重合
    for i in range(26):
        rr = 110 + i * 13
        b.append(circle(500, 500, rr * 2, None, border="1 SOLID #FFFFFF33"))
    b.append(circle(500, 500, 182, "#0E0E12"))
    b.append(circle(500, 500, 182, None, border="3 SOLID #FFFFFF88"))
    b.append(circle(500, 500, 22, "#FFFFFF33"))
    b.append(txt("SLOW", 380, 466, 240, None, 44, INK, W600, align="CENTER"))
    b.append(txt("ROTATION", 372, 518, 256, None, 22, "#9AA0AA", align="CENTER"))
    b.append(txt("厂牌 夜潮唱片", 80, 76, 500, None, 24, "#1A1A1E"))
    b.append(txt("慢转 · 33⅓", 80, 812, 600, None, 54, INK, W600))
    b.append(txt("NT-017 · 2026 夏", 80, 878, 600, None, 26, "#1A1A1EF0"))
    b.append(txt("12 吋 · 透明橙胶", 640, 880, 280, None, 22, "#1A1A1ED0",
                 align="END"))
    b.append(rect(80, 928, 840, 1, "#1A1A1E33"))
    b.append(txt("封套设计稿；厂牌与编号为示例", 80, 938, 840, None, 17, "#1A1A1EA6"))
    return canvas(W, H, "".join(b), "#0E0E12")


def c05():
    """真实场景：天气 App 的「降水强度」浮层卡。

    手法：`ImageFiltered` 对**同一份 DSL 里真实存在的底层图元**做高斯模糊。
    那些图元必须是滤镜的**子节点**——首版把它们放在滤镜外面，滤镜里只裹了一个
    全透明 Container，结果什么都没模糊。

    同时记录两条纯排版边界：数值列宽度不够会被静默裁字；
    卡片内元素排到卡片底边之外会挂出去。
    """

    W, H = 720, 1400
    b = [rect(0, 0, W, H, "#1B2A45")]
    # ① 背景 26 个圆必须是 ImageFiltered 的**子节点**。
    #    首版把它们放在滤镜外面，而滤镜里只裹了一个全透明 Container，
    #    结果什么都没模糊——这是「滤镜只作用于自身子树」的又一例。
    bg = "".join(circle(40 + (i * 137) % 700, 30 + (i * 211) % 1200,
                        60 + (i % 5) * 70,
                        ["#2E4470", "#38527F", "#243A5E"][i % 3])
                 for i in range(26))
    b.append('<Positioned left="0" top="0" width="720" height="1400">'
             '<ImageFiltered sigmaX="26" sigmaY="26" tileMode="CLAMP">'
             f'<Stack fit="EXPAND">{bg}</Stack>'
             '</ImageFiltered></Positioned>')

    b.append(rect(40, 80, 640, 312, "#0E1A2ECC", 24))
    b.append(txt("降水强度", 72, 112, 400, None, 26, "#8FB3E8"))
    b.append(txt("中雨", 72, 156, 400, None, 64, INK, W600))
    b.append(txt("未来一小时 4.2 mm", 72, 246, 400, None, 28, "#8FB3E8"))
    b.append(txt("接下来 12 小时", 72, 288, 400, None, 22, "#8FB3E8"))
    for i in range(12):
        h = 16 + int(40 * math.sin(i / 12 * math.pi) * (1 - i / 18))
        b.append(rect(72 + i * 50, 358 - h, 30, h, "#4C8DA8", 6))

    b.append(rect(40, 424, 640, 420, "#0E1A2ECC", 24))
    b.append(txt("分区预报", 72, 460, 400, None, 26, "#8FB3E8"))
    zones = [("城东", 68, "#4C8DA8"), ("城西", 42, "#3B6E85"),
             ("江北", 25, "#2E5570"), ("临港", 81, "#E2683C"),
             ("老城", 37, "#3B6E85"), ("开发区", 12, "#24455C")]
    for i, (nm, mm, col) in enumerate(zones):
        y = 512 + i * 52
        b.append(txt(nm, 72, y, 160, None, 24, INK))
        b.append(rect(240, y + 8, 296, 14, "#1E3350", 7))
        b.append(rect(240, y + 8, 296 * mm / 100, 14, col, 7))
        b.append(txt(f"{mm} mm", 552, y, 96, None, 22, "#8FB3E8", align="END"))

    b.append(rect(40, 880, 640, 300, "#0E1A2ECC", 24))
    b.append(txt("出门带伞", 72, 916, 500, None, 40, INK, W600))
    b.append(txt("降水将在 14:20 前后达到峰值，之后逐步减弱。",
                 72, 976, 576, None, 26, "#8FB3E8"))
    b.append(txt("全天累计 11.8 mm", 72, 1022, 576, None, 26, "#8FB3E8"))
    b.append(rect(72, 1080, 576, 66, "#4C8DA8", 33))
    b.append(txt("查看逐小时", 72, 1100, 576, None, 26, INK, W600,
                 align="CENTER"))
    footer(b, 40, H - 84, 640, "界面稿；降水量为示例数据")
    return canvas(W, H, "".join(b), "#1B2A45")
def c06():
    """真实场景：独立书店海报的丝网印刷套色校样。

    手法：`ColorFiltered` + Skia `blendMode="MULTIPLY"` 模拟**油墨叠印**，
    交叠处自然变深。blendMode 是在**滤镜自身边界内**与背板混合的，
    所以整块版区都会上墨——这恰好等于丝印的整版上墨。

    版内图元一律用相对坐标，两个版本各自装进自己的 Positioned；
    用画布绝对坐标会二次偏移。
    """

    W, H = 1000, 1300
    b = [rect(0, 0, W, H, "#F2EDE2")]
    b.append(txt("丝网印刷套色校样", 60, 50, 600, None, 24, "#8A7F6B"))
    b.append(txt("两层叠印会变暗", 640, 52, 300, None, 22, "#B0573A",
                 align="END"))
    # 版区内的图元一律用**相对版区左上角**的坐标，两个版本各自装进自己的 Positioned；
    # 首版用的是画布绝对坐标再套一层 Positioned，等于偏移了两次。
    PW, PH = 880, 360
    plate = []
    # 五个色块
    for _i in range(5):
        plate.append(rect(50 + _i * 160, 196, 120, 74, "CURRENT", 12))
    # 大字：y 78–256，与色块 196–270 在 196–256 交叠
    plate.append(txt("重叠", 200, 78, 480, None, 130, "CURRENT", W600,
                     align="CENTER"))
    for _k, (nm, col) in enumerate((("第一版 · 墨蓝", "#2C4A7C"),
                                   ("第二版 · 朱红", "#D0462E"))):
        py = 168 + _k * 440
        b.append(txt(nm, 60, py - 48, 300, None, 24, col, W600))
        inner = "".join(x.replace("CURRENT", col) for x in plate)
        head = (f'<Positioned left="60" top="{py}" width="{PW}" height="{PH}">'
                f'<Stack fit="EXPAND">{inner}</Stack></Positioned>')
        if _k == 0:
            b.append(head)
        else:
            # MULTIPLY 只作用于版区内的图元；版区外的画布底不受影响
            b.append(f'<Positioned left="60" top="{py}" width="{PW}" height="{PH}">'
                     f'<ColorFiltered color="#D0462E" blendMode="MULTIPLY">'
                     f'<Stack fit="EXPAND">{inner}</Stack>'
                     f'</ColorFiltered></Positioned>')
        b.append(rect(60, py + PH + 12, PW, 1, "#D8D0C0"))
    # 880px 盒子在 22px 字号下约装 36 个全角字；原一行写了 40 个，
    # **溢出被静默裁掉**（图上停在「…与背板混合，所」）。拆两行。
    b.append(txt("上：单版墨蓝。下：朱红整版以 MULTIPLY 叠上去——滤镜在自身边界内与背板",
                 60, 1006, 880, None, 22, "#8A7F6B"))
    b.append(txt("混合，所以满版上墨；文字与色块的交叠处叠了两层，颜色最深。",
                 60, 1038, 880, None, 22, "#8A7F6B"))
    # 色标：把「叠了几层」直接标出来
    b.append(rect(60, 1108, 880, 1, "#D8D0C0"))
    for sx, col, lab in ((60, "#D0462E", "单层 = 一版墨"),
                         (300, "#8A2418", "两层 = 文字与色块交叠"),
                         (600, "#D9A79C", "满版 = 背板 × 墨")):
        b.append(rect(sx, 1128, 44, 44, col, 6))
        b.append(txt(lab, sx + 56, 1138, 230, None, 20, "#8A7F6B"))
    footer(b, 60, H - 50, 880, "校样稿；配色为示例")
    return canvas(W, H, "".join(b), "#F2EDE2")



    # 版区内的图元一律用**相对版区左上角**的坐标，两个版本各自装进自己的 Positioned；
    # 首版用的是画布绝对坐标再套一层 Positioned，等于偏移了两次。
    PW, PH = 880, 360
    plate = []
    # 五个色块
    for _i in range(5):
        plate.append(rect(50 + _i * 160, 196, 120, 74, "CURRENT", 12))
    # 大字：y 78–256，与色块 196–270 在 196–256 交叠
    plate.append(txt("重叠", 200, 78, 480, None, 130, "CURRENT", W600,
                     align="CENTER"))
    for _k, (nm, col) in enumerate((("第一版 · 墨蓝", "#2C4A7C"),
                                   ("第二版 · 朱红", "#D0462E"))):
        py = 168 + _k * 440
        b.append(txt(nm, 60, py - 48, 300, None, 24, col, W600))
        inner = "".join(x.replace("CURRENT", col) for x in plate)
        head = (f'<Positioned left="60" top="{py}" width="{PW}" height="{PH}">'
                f'<Stack fit="EXPAND">{inner}</Stack></Positioned>')
        if _k == 0:
            b.append(head)
        else:
            # MULTIPLY 只作用于版区内的图元；版区外的画布底不受影响
            b.append(f'<Positioned left="60" top="{py}" width="{PW}" height="{PH}">'
                     f'<ColorFiltered color="#D0462E" blendMode="MULTIPLY">'
                     f'<Stack fit="EXPAND">{inner}</Stack>'
                     f'</ColorFiltered></Positioned>')
        b.append(rect(60, py + PH + 12, PW, 1, "#D8D0C0"))
def c07():
    """真实场景：住宅方案的日照分析图（平面）。

    手法：用 `Transform` 的 2D 旋转把**投影带**绕楼体中心摆成四个真实太阳
    方位角（135°/157.5°/202.5°/225°），影长按等效楼高 30 m 与冬至日高度角
    （18°/30°/30°/18°）换算。

    平面日照图里入射光线与投影**共线**，都沿太阳反方向；
    首版把日照条以圆心为原点向两侧摆，结果被楼体整个盖住，等于没做。
    """

    W, H = 1200, 900
    b = [rect(0, 0, W, H, "#F7F5F0")]
    b.append(txt("日照分析", 64, 40, 500, None, 28, "#8A6D3B"))
    b.append(txt("冬至日 · 北纬 31.2°", 64, 84, 700, None, 46, "#2B2119", W600))
    b.append(txt("冬至正午太阳高度 35.4°", 760, 50, 376, None, 24, "#8A6D3B",
                 align="END"))

    GX, GY, R = 800, 520, 310
    b.append(circle(GX, GY, R * 2, None, border="1 SOLID #DED8CB"))
    b.append(circle(GX, GY, 232, None, border="1 SOLID #E4DED2"))

    # 罗盘：北在上、南在下（平面日照图惯例）
    # textAlign 只有 START/CENTER/END/JUSTIFY/LEFT/RIGHT，是水平对齐；
    # 没有 MIDDLE。这里给 66px 的盒子 + CENTER，盒子的 x/y 手工居中。
    for lbl, bx, by in (("北", GX - 33, GY - R - 43),
                        ("南", GX - 33, GY + R - 19),
                        ("东", GX + R - 21, GY - 13),
                        ("西", GX - R - 99, GY - 13)):
        b.append(txt(lbl, bx, by, 66, None, 22, "#A8937A", align="CENTER"))
    # 太阳方位扇面（正南 ±40°）
    for _i in range(17):
        _a = math.radians(-40 + _i * 5)
        b.append(segment(GX + 232 * math.sin(_a), GY - 232 * math.cos(_a),
                         GX + R * math.sin(_a), GY - R * math.cos(_a),
                         "#E6E0D2", 1))

    # 时刻 → (方位角, 高度角, 比例影长m)。影长 = 等效楼高 30m / tan(高度角)。
    hours = [("09:00", 135.0, 18.0, 276), ("11:00", 157.5, 30.0, 156),
             ("13:00", 202.5, 30.0, 156), ("15:00", 225.0, 18.0, 276)]
    for lbl, az, alt, shl in hours:
        th = math.radians(az)
        ux, uy = -math.sin(th), math.cos(th)   # 太阳反方向 = 投影方向
        # 入射射线在 **−u 侧**（太阳所在的一侧），投影在 +u 侧。
        # 首版两边都画在 +u，射线被后画的投影带整段盖住，图上完全看不到。
        b.append(segment(GX - 300 * ux, GY - 300 * uy,
                         GX - 148 * ux, GY - 148 * uy, "#E8A33B", 3))
        # 投影带：从楼体外缘 bd 起、沿 u 延伸 shl。
        # 角度要传 az+90：matrix 把盒子局部 x 轴映到 (cosθ, sinθ)，
        # 要落在 u=(-sin az, cos az) 上必须 θ=az+90；首版传 az，差了 90°，
        # 图上投影带与入射光线互相垂直。
        bd = 148.0
        ccx, ccy = GX + (bd + shl / 2) * ux, GY + (bd + shl / 2) * uy
        b.append(f'<Positioned left="{ccx - shl / 2:.1f}" top="{ccy - 9:.1f}" '
                 f'width="{shl:.1f}" height="18">'
                 f'<Transform matrix="({_mat(az + 90):s})" alignment="CENTER">'
                 f'<Container width="{shl:.1f}" height="18" color="#B8C4D0" '
                 f'opacity="0.85"/></Transform></Positioned>')
        # 时刻标签挂在入射射线的末端（−u 方向 r=300），跟着射线走而不是投影带
        b.append(txt(lbl, GX - 300 * ux - 48, GY - 300 * uy - 13, 96, None,
                     21, "#8A6D3B", align="CENTER"))

    # 楼体（旋转 15° 的矩形）
    b.append(f'<Positioned left="{GX - 130:.1f}" top="{GY - 60:.1f}" '
             f'width="260" height="120">'
             f'<Transform matrix="({_mat(15):s})" alignment="CENTER">'
             f'<Container width="260" height="120" color="#3A4A5E" '
             f'borderRadius="6"/></Transform></Positioned>')
    for _i in range(4):
        b.append(rect(GX - 96 + _i * 52, GY - 36, 32, 72, "#5A6C84", 4))
    b.append(txt("拟建 12 层住宅", GX - 130, GY + 82, 260, None, 22, "#2B2119",
                 align="CENTER"))
    b.append(txt("橙色 = 入射阳光　灰蓝 = 投影", GX - 160, GY + 114, 320, None,
                 19, "#A8937A", align="CENTER"))

    facts = [("正午太阳高度", "35.4°"), ("日出 / 日落", "07:02 / 17:14"),
             ("最低日照时数", "3.8 h"), ("受影响住户", "4 户 101–104")]
    for i, (k, v) in enumerate(facts):
        y = 196 + i * 62
        b.append(txt(k, 64, y, 300, None, 24, "#8A6D3B"))
        b.append(txt(v, 64, y + 28, 300, None, 26, "#2B2119", W600))
    b.append(rect(64, 452, 340, 2, "#DED8CB"))
    b.append(txt("影长按等效楼高 30 m 与冬至日", 64, 472, 340, None, 22,
                 "#8A6D3B"))
    b.append(txt("高度角换算，比例示意。", 64, 502, 340, None, 22, "#8A6D3B"))
    # 300px 的盒子在 22px 字号下只装得下约 13 个全角字，原先一行写完 18 个字
    # 会被**静默裁掉**末尾（渲染出来是「…需复核平」）。拆成两行。
    b.append(txt("西侧 2–4 层午后日照不足，", 64, 552, 300, None, 22, "#B0573A"))
    b.append(txt("需复核平面。", 64, 582, 300, None, 22, "#B0573A"))
    footer(b, 64, H - 60, 1072, "分析图为示意；非真实工程计算结果")
    return canvas(W, H, "".join(b), "#F7F5F0")


# ══════════════ 08 ClipPath 曲线徽章 → 城市骑行路线章
def c08():
    """真实场景：共享单车系统的「本周骑行成就」印章。

    手法：`ClipPath` 用**带 Q/C 命令的曲线轮廓 + EVEN_ODD** 挖出花瓣形章面，
    再在章面上叠一周七天的骑行柱。曲线轮廓是 DSL 里唯一能画非圆角路径的地方。
    """
    W, H = 1000, 1000
    b = [rect(0, 0, W, H, "#0F1C17")]
    b.append(rect(56, 56, 888, 888, None, 20, border="2 SOLID #4ADE80"))
    b.append(txt("本周骑行成就", 120, 108, 760, None, 40, INK, W600))
    b.append(txt("SHARED BIKE · 第 32 周", 120, 162, 760, None, 22, "#3E7A5C"))
    days = [("一", 8.4), ("二", 12.1), ("三", 6.7), ("四", 15.3),
            ("五", 21.8), ("六", 34.2), ("日", 18.5)]
    bx, bw, base = 130, 92, 720
    for i, (d, km) in enumerate(days):
        h = km * 8.0        # 首版最高柱到 y≈310，穿过了右上角的章面
        col = "#4ADE80" if i != 5 else "#E8B93B"
        x = bx + i * (bw + 14)
        b.append(rect(x, base - h, bw, h, col, 10))
        b.append(txt(f"{km:.1f}", x - 12, base - h - 32, bw + 24, None, 22,
                     col, W600, align="CENTER"))
        b.append(txt(d, x - 12, base + 14, bw + 24, None, 24, "#6FA07F",
                     align="CENTER"))
    b.append(rect(120, base + 2, 760, 2, "#2A4A38"))
    b.append(txt("合计 117.0 km · 比上周多 22%", 120, base + 62, 760, None, 26,
                 "#4ADE80"))
    b.append(txt("最长一骑：周五 21.8 km", 120, base + 104, 760, None, 24,
                 "#6FA07F"))
    # 花瓣形章面：曲线轮廓 + 偶奇填充挖四个小瓣
    b.append(f'<Positioned left="640" top="120" width="300" height="300">'
             f'<ClipPath path="M0 0 H100 V100 H0 Z '
             f'M50 8 Q64 30 50 50 Q36 30 50 8 Z '
             f'M92 50 Q70 64 50 50 Q70 36 92 50 Z '
             f'M50 92 Q36 70 50 50 Q64 70 50 92 Z '
             f'M8 50 Q30 36 50 50 Q30 64 8 50 Z" '
             f'viewBox="0 0 100 100" fit="CONTAIN" fillRule="EVEN_ODD">'
             f'<Container color="#4ADE8033" borderRadius="16"/>'
             f'</ClipPath></Positioned>')
    b.append(txt("4", 700, 186, 180, None, 120, "#4ADE80", W600,
                 align="CENTER"))
    b.append(txt("天达标", 700, 316, 180, None, 26, "#6FA07F", align="CENTER"))
    footer(b, 96, 880, 808, "成就章为设计稿；里程为示例")
    return canvas(W, H, "".join(b), "#0F1C17")


# ══════════════ 09 高密度嵌套布局 → 演出技术清单
def c09():
    """真实场景：剧场演出当晚的**技术提示表**（提示单）。

    手法：把同一套「状态条 + 标签 + 数值」组件塞进**6 行 × 4 列的高密度表格**，
    每一格还要再嵌一层进度条。这是检验组件在最小尺寸下是否还成立的极端用例。
    """
    W, H = 1400, 900
    b = [rect(0, 0, W, H, "#F4F2ED")]
    b.append(rect(0, 0, W, 156, "#1A1A1E"))
    b.append(txt("技术提示单", 56, 34, 500, None, 26, "#E8B93B"))
    b.append(txt("第七幕《潮汐》 · 演出当晚 18:40", 56, 76, 900, None, 44,
                 "#F5F2EA", W600))
    b.append(txt("场次 2026-07-18 19:30 · 剧场 二号厅", 820, 54, 524, None, 24,
                 "#9A968C", align="END"))
    b.append(txt("提示单版本 v3 · 已同步至各岗位", 820, 98, 524, None, 22,
                 "#9A968C", align="END"))

    items = [
        ("灯光", "LX 1–24", "面光 6 台", 92, "#E8B93B", "就绪"),
        ("灯光", "LX 30–42", "染色 12 台", 78, "#E8B93B", "就绪"),
        ("音响", "PA L/R", "主扩 4 只", 100, "#5FD3E8", "就绪"),
        ("音响", "PA Sub", "超低 2 只", 64, "#5FD3E8", "待调"),
        ("道具", "PROP 1–6", "换景车 6 件", 88, "#8FD46A", "就绪"),
        ("视频", "LED", "主屏 12×4m", 95, "#B08CF0", "就绪"),
    ]
    heads = ["组别", "位号", "内容", "完成度", "状态"]
    xs = [56, 200, 380, 640, 960]
    for i, hd in enumerate(heads):
        b.append(txt(hd, xs[i], 190, 300, None, 22, "#8A857A", W600))
    b.append(rect(56, 222, 1288, 2, "#1A1A1E"))
    for i, (grp, addr, what, pct, col, st) in enumerate(items):
        y = 242 + i * 74
        b.append(rect(56, y, 1288, 62, "#FFFFFF", 8, border="1 SOLID #E2DED4"))
        b.append(rect(56, y, 6, 62, col, 3))
        b.append(txt(grp, xs[0] + 18, y + 18, 130, None, 22, INKD, W600))
        b.append(txt(addr, xs[1] + 18, y + 18, 160, None, 22, "#4A463E"))
        b.append(txt(what, xs[2] + 18, y + 18, 240, None, 22, "#4A463E"))
        b.append(rect(xs[3], y + 24, 230, 14, "#E8E4DA", 7))
        b.append(rect(xs[3], y + 24, 230 * pct / 100, 14, col, 7))
        # 百分比独占 880–944；徽章从 960 起，两者不再相交（否则会被后画的
        # 徽章切掉数字，图上显示成「9:」）
        b.append(txt(f"{pct}%", xs[3] + 240, y + 18, 64, None, 22, col))
        ok = st == "就绪"
        b.append(rect(xs[4], y + 16, 110, 32, ("#E8F2E4" if ok else "#FBEEE0"), 16))
        b.append(txt(st, xs[4], y + 22, 110, None, 20, "#4A7A32" if ok else "#A85A28",
                     W600, align="CENTER"))
        b.append(txt(f"岗位：{'灯光组' if grp == '灯光' else grp + '组'}",
                     xs[4] + 126, y + 20, 230, None, 20, "#8A857A"))
    b.append(rect(56, 700, 1288, 92, "#1A1A1E", 10))
    b.append(txt("唯一未就绪：PA Sub 超低 2 只，声学组 18:55 前完成调音",
                 84, 722, 900, None, 26, "#E8B93B", W600))
    b.append(txt("其余 5 项已就绪", 1000, 726, 316, None, 24, "#9A968C",
                 align="END"))
    footer(b, 56, H - 62, 1288, "提示单为示例；位号与场次非真实演出")
    return canvas(W, H, "".join(b), "#F4F2ED")


# ══════════════ 10 文字立体描边 → 书店展陈主视觉
def c10():
    """真实场景：独立书店「年度十佳书单」展陈主视觉。

    手法：同一句话用**四层描边**（不同粗细、不同透明度）叠出层次，
    再用 `Transform` 把最底层整体旋转 6°，做出丝网印刷的套版错位。
    纯 DSL，不需要任何后处理。
    """
    W, H = 1200, 900
    b = [rect(0, 0, W, H, "#1A1A1E")]
    b.append(rect(0, 0, W, H, None, 0))
    for k, (col, sw, op, rot, dx, dy) in enumerate([
            ("#3E2A46", 26, 0.55, 6, -14, 10),
            ("#7A2E4E", 16, 0.62, 4, -7, 6),
            ("#C24A3A", 8, 0.74, 2, -3, 3),
            ("#E8B93B", 3, 1.00, 0, 0, 0)]):
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        m = (f"{c:.5f},{s:.5f},0,0,{-s:.5f},{c:.5f},0,0,0,0,1,0,0,0,0,1")
        b.append(f'<Positioned left="{60 + dx}" top="{300 + dy}" width="1080" '
                 f'height="280">'
                 f'<Transform matrix="({m})" alignment="CENTER">'
                 f'<Text textAlign="CENTER" fontSize="140" foregroundColor="{col}" '
                 f'foregroundMode="STROKE" foregroundStrokeWidth="{sw}" '
                 f'opacity="{op}" fontFamily="Inter Semi Bold,Inter,Noto Sans CJK SC" '
                 f'text="年度十佳"/></Transform></Positioned>')
    b.append(txt("年度十佳", 60, 396, 1080, None, 140, "#E8B93B", W600,
                 align="CENTER"))
    b.append(txt("INDIE BOOKSHOP · ANNUAL LIST", 60, 596, 1080, None, 28,
                 "#9A8F7A", align="CENTER"))
    books = [("01", "潮汐表"), ("02", "夜班公交"), ("03", "旧物志"),
             ("04", "铁皮屋顶"), ("05", "慢跑指南"), ("06", "苔与砖")]
    for i, (no, nm) in enumerate(books):
        x = 110 + (i % 6) * 168
        b.append(rect(x, 672, 132, 100, None, 8, border="1 SOLID #4A4438"))
        b.append(txt(no, x + 14, 686, 60, None, 22, "#9A8F7A"))
        b.append(txt(nm, x + 14, 726, 110, None, 22, "#F5F2EA"))
    b.append(txt("7 月 1 日 – 8 月 31 日 · 二楼文学区", 60, 810, 1080, None, 24,
                 "#C4BCA8"))
    footer(b, 60, H - 62, 1080, "展陈稿；书名与店名为示例")
    return canvas(W, H, "".join(b), "#1A1A1E")


CASES = [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10]
SIZES = [(1000, 1400), (1200, 1200), (1200, 900), (1000, 1000), (720, 1400),
         (1000, 1300), (1200, 900), (1000, 1000), (1400, 900), (1200, 900)]


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    idx = range(10) if which == "all" else [int(which) - 1]
    for i in idx:
        p = DRAFTS / f"b03-{i + 1:02d}-{ver}.snapshot"
        p.write_text(CASES[i](), encoding="utf-8")
        print(f"-> {p.name}  {SIZES[i][0]}x{SIZES[i][1]}  {p.stat().st_size}B")


if __name__ == "__main__":
    main()