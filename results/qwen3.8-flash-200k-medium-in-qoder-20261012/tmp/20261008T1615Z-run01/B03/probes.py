"""B03 能力探针：一次验证一个文档读到但未在本题用过的能力。

每个探针是独立的小画布，失败互不影响；失败的原始响应留在 probe/requests/。
运行：python tmp/<run>/B03/probes.py            生成全部 probe/*.snapshot
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]          # suite root
sys.path.insert(0, str(root / "_suite" / "scripts")) if False else None
HERE = Path(__file__).parent
PROBE = HERE / "probe"

W, H = 520, 320


def snap(body, w=W, h=H, bg="#12151A"):
    return (f'<Snapshot background="{bg}" type="png">'
            f'<Container width="{w}" height="{h}">'
            f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">{body}</Container>'
            f'</Snapshot>\n')


def pos(x, y, w, h, inner):
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">{inner}</Positioned>'


def cap(x, y, s):
    return pos(x, y, 500, 26, f'<Text color="#8FA0B3" fontSize="17" '
                              f'fontFamily="Inter,Noto Sans CJK SC">{s}</Text>')


P = {}

# 01 透视项：列主序矩阵第 15 位（row2,col3）
P["01-perspective"] = snap(
    pos(30, 24, 440, 220,
        '<Container width="440" height="220" alignment="CENTER" '
        'transform="(1,0,0,0,0,1,0,0,0,0,1,0,0,0,-0.0016,1)" transformAlignment="CENTER">'
        '<Container width="380" height="180" color="#E8552B" borderRadius="12"/></Container>')
    + cap(30, 262, "01 perspective m[2][3] = -0.0016"))

# 02 斜切（非正交矩阵）
P["02-skew"] = snap(
    pos(60, 30, 340, 160,
        '<Container width="340" height="160" '
        'transform="(1,0,0,0,0.5,1,0,0,0,0,1,0,0,0,0,1)" transformAlignment="TOP_LEFT">'
        '<Container width="340" height="160" color="#2E5468"/></Container>')
    + cap(30, 262, "02 skew x-by 0.5 (m[1][0])"))

# 03 ClipPath：文档注册 38 标签中没有它（Kotlin API 才有）——预期失败
P["03-clippath"] = snap(
    pos(90, 40, 300, 200,
        '<ClipPath clipBehavior="ANTI_ALIAS">'
        '<Container width="300" height="200" color="#E0A526"/></ClipPath>')
    + cap(30, 262, "03 ClipPath tag (expect unknown-tag)"))

# 04 SWEEP 渐变 + MIRROR 平铺 + 部分角度
P["04-sweep-mirror"] = snap(
    pos(110, 20, 260, 260,
        '<Container width="260" height="260" borderRadius="130" '
        'gradientType="SWEEP" gradientColors="#C8552B,#12151A,#E0A526" '
        'gradientStops="0,0.5,1" gradientTileMode="MIRROR" '
        'gradientCenter="CENTER" gradientRadius="0.5" '
        'gradientStartAngle="0" gradientEndAngle="1.0" />')
    + cap(30, 292, "04 SWEEP 3 stops tileMode=MIRROR 0..1.0 rad"))

# 05 径向渐变焦点
P["05-radial-focal"] = snap(
    pos(30, 20, 460, 220,
        '<Container width="460" height="220" borderRadius="14" '
        'gradientType="RADIAL" gradientColors="#FFFFFF,#F2C14E,#B4432A,#1B1E22" '
        'gradientCenter="CENTER" gradientRadius="0.75" '
        'gradientFocal="TOP_LEFT" gradientFocalRadius="0.05" />')
    + cap(30, 262, "05 RADIAL + focal TOP_LEFT focalRadius .05"))

# 06 描边字（STROKE）
P["06-stroke-text"] = snap(
    pos(30, 40, 460, 130,
        '<Text fontSize="96" fontStyle="BOLD" fontFamily="Inter,Noto Sans CJK SC" '
        'foregroundColor="#F2EBDD" foregroundMode="STROKE" foregroundStrokeWidth="2.2" '
        '>OUTLINE</Text>')
    + cap(30, 262, "06 foregroundMode=STROKE (fill color absent)"))

# 07 装饰线样式与间距（目录引导线）
P["07-leader-dots"] = snap(
    "".join(pos(30, y, 460, 46,
                f'<Text fontSize="30" color="#F2EBDD" decoration="UNDERLINE" '
                f'decorationColor="{c}" decorationLineStyle="{st}" '
                f'decorationThickness="2.6" decorationGaps="2,7">标题 ··· 页码 {i + 1}</Text>')
            for i, (y, st, c) in enumerate([(40, "SOLID", "#E0A526"), (96, "DOTTED", "#E0A526"),
                                            (152, "DOUBLE", "#6E7F8D"), (208, "DASHED", "#6E7F8D")]))
    + cap(30, 280, "07 decorationLineStyle SOLID/DOTTED/DOUBLE/DASHED"))

# 08 WidgetSpan 行内图形
P["08-widget-span"] = snap(
    pos(30, 40, 470, 130,
        '<Text fontSize="30" color="#F2EBDD" fontFamily="Inter,Noto Sans CJK SC">'
        '取货<WidgetSpan alignment="MIDDLE">'
        '<Container width="34" height="34" color="#3F7A55" borderRadius="17"/></WidgetSpan>窗口，'
        '逾期<WidgetSpan alignment="BASELINE">'
        '<Container width="26" height="26" color="#A6382F" borderRadius="4"/></WidgetSpan>计费</Text>')
    + cap(30, 262, "08 WidgetSpan inline chips (MIDDLE / BASELINE)"))

# 09 Raw 保留空格与换行
P["09-raw-block"] = snap(
    pos(30, 30, 470, 220,
        '<Text fontSize="26" color="#9BE564" fontFamily="Consolas,monospace">'
        '<Raw>  ▁▂▃▄▅▆▇█\n ▁▂▄▆█▆▄▂\n█▇▅▃▂▃▅▇</Raw></Text>')
    + cap(30, 262, "09 Raw keeps spaces and \\n (monospace)"))

# 10 ColorFiltered 混合模式（一次 4 个常用名）
def blend_row(modes):
    cells = []
    for i, m in enumerate(modes):
        cells.append(pos(20 + i * 120, 40, 110, 180,
                         f'<ColorFiltered color="#C8552B" blendMode="{m}">'
                         '<Container width="110" height="180" '
                         'gradientType="LINEAR" gradientColors="#FFFFFF,#3A3A3A" '
                         'gradientBegin="TOP" gradientEnd="BOTTOM"/></ColorFiltered>'))
        cells.append(pos(20 + i * 120, 226, 110, 22,
                         f'<Text fontSize="15" color="#8FA0B3">{m}</Text>'))
    return "".join(cells)


P["10-blend-a"] = snap(blend_row(["MULTIPLY", "SCREEN", "OVERLAY", "HARD_LIGHT"])
                       + cap(20, 288, "10a MULTIPLY/SCREEN/OVERLAY/HARD_LIGHT"))
P["11-blend-b"] = snap(blend_row(["COLOR_DODGE", "EXCLUSION", "PLUS", "MODULATE"])
                       + cap(20, 288, "11b COLOR_DODGE/EXCLUSION/PLUS/MODULATE"))
P["12-blend-c"] = snap(blend_row(["HUE", "SATURATION", "LUMINOSITY", "COLOR"])
                       + cap(20, 288, "12c HUE/SATURATION/LUMINOSITY/COLOR"))

# 13 BackdropFilter 背景模糊（限幅在 ClipRRect）
P["13-backdrop"] = snap(
    pos(20, 20, 480, 230,
        '<Container width="480" height="230" '
        'gradientType="LINEAR" gradientColors="#C8552B,#2E5468" '
        'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/>')
    + pos(40, 120, 420, 60, '<Text fontSize="42" fontStyle="BOLD" color="#FFFFFF">背景字 BACKGROUND</Text>')
    + pos(150, 70, 220, 120,
          '<ClipRRect borderRadius="18" clipBehavior="ANTI_ALIAS">'
          '<BackdropFilter sigmaX="10" sigmaY="10">'
          '<Container width="220" height="120" color="#FFFFFF26"/></BackdropFilter></ClipRRect>')
    + cap(20, 268, "13 BackdropFilter sigma 10 inside ClipRRect"))

# 14 fontFeatures
P["14-font-features"] = snap(
    pos(30, 30, 460, 40, '<Text fontSize="30" color="#F2EBDD">0123456789 Ai To</Text>')
    + pos(30, 80, 460, 40, '<Text fontSize="30" color="#E0A526" fontFeatures="tnum">0123456789 Ai To</Text>')
    + pos(30, 130, 460, 40, '<Text fontSize="30" color="#E0A526" fontFeatures="lnum smcp">0123456789 Ai To</Text>')
    + pos(30, 180, 460, 40, '<Text fontSize="30" color="#6E7F8D" fontFeatures="-kern +liga">0123456789 Ai To</Text>')
    + cap(20, 262, "14 fontFeatures tnum / lnum smcp / -kern +liga"))

# 15 阴影 blurStyle OUTER / INNER + 多阴影
P["15-shadow-modes"] = snap(
    pos(30, 40, 200, 90, '<Container width="200" height="90" color="#F2EBDD" borderRadius="10" '
                         'boxShadow="0 10 18 0 #00000066 OUTER"/>')
    + pos(260, 40, 200, 90, '<Container width="200" height="90" color="#F2EBDD" borderRadius="10" '
                            'boxShadow="0 10 18 0 #00000066 INNER"/>')
    + pos(30, 160, 200, 90, '<Container width="200" height="90" color="#F2EBDD" borderRadius="10" '
                            'boxShadow="0 4 10 0 #00000055 NORMAL,0 1 3 0 #00000033 NORMAL"/>')
    + pos(260, 160, 200, 90, '<Container width="200" height="90" color="#22262B" borderRadius="10" '
                              'boxShadow="0 0 0 4 #E0A526"/>')
    + cap(20, 270, "15 blurStyle OUTER / INNER / 双层 / spread 环"))

# 16 Image dataUri + REPEAT_X 平铺
_px = ("iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAYAAACp8Z5+AAAAJklEQVR4nGNgYGbAn"
       "sKmQgaGRiYGZhZmBgZGRiYGAAAADPwCcQoBh6UAAAAASUVORK5CYII=")
P["16-repeat-tile"] = snap(
    pos(20, 30, 480, 100,
        f'<Image width="480" height="100" dataUri="data:image/png;base64,{_px}" '
        'repeat="REPEAT_X" scale="0.5" color="#E0A526" colorBlendMode="SRC_ATOP"/>')
    + cap(20, 262, "16 Image dataUri repeat=REPEAT_X scale=0.5 + color 叠色"))

# 17 IndexedStack 只绘制选中子节点
P["17-indexed-stack"] = snap(
    pos(60, 40, 400, 200,
        '<IndexedStack index="1" alignment="CENTER">'
        '<Container width="400" height="200" color="#3F7A55"/>'
        '<Container width="400" height="200" color="#A6382F"/>'
        '<Container width="400" height="200" color="#2E5468"/></IndexedStack>')
    + cap(20, 262, "17 IndexedStack index=1（应只见红色）"))

# 18 Text overflow=CLIP + maxLines + softWrap=false 单行硬截
P["18-text-overflow"] = snap(
    pos(30, 40, 200, 46, '<Text fontSize="30" color="#F2EBDD" maxLines="1" softWrap="false" '
                         'overflow="CLIP">这一段文字明显超出盒子宽度会被截断</Text>')
    + pos(30, 100, 200, 46, '<Text fontSize="30" color="#E0A526" maxLines="1" softWrap="false" '
                            'overflow="VISIBLE">这一段文字明显超出盒子宽度会被截断</Text>')
    + pos(30, 160, 200, 46, '<Text fontSize="30" color="#6E7F8D" maxLines="1" softWrap="false" '
                           'overflow="ELLIPSIS">这一段文字明显超出盒子宽度会被截断</Text>')
    + cap(20, 262, "18 overflow CLIP / VISIBLE / ELLIPSIS"))

# 19 letterSpacing + wordSpacing + height/topRatio
P["19-spacing-axes"] = snap(
    pos(30, 34, 460, 44, '<Text fontSize="30" color="#F2EBDD" letterSpacing="8">疏排 SPACED TYPE</Text>')
    + pos(30, 90, 460, 44, '<Text fontSize="30" color="#E0A526" wordSpacing="18">词距 三 个 词 语</Text>')
    + pos(30, 146, 460, 76, '<Text fontSize="26" color="#6E7F8D" height="2.1" maxLines="2">行高 2.1 的两行文字，用来观察 height 与 topRatio 的实际作用</Text>')
    + pos(30, 236, 460, 30, '<Text fontSize="18" color="#9AA5B1">topRatio 未设置 / height=2.1</Text>'))

# 20 strut 段落支撑（混排不同字号时基线不跳）
P["20-strut"] = snap(
    pos(30, 30, 470, 200,
        '<Text fontSize="24" color="#F2EBDD" strutEnabled="true" strutFontSize="24" strutHeight="1.2">'
        '大字<Text fontSize="54" color="#E0A526">54</Text>回到常规'
        '<Text fontSize="16" color="#6E7F8D">small</Text>结束</Text>')
    + cap(30, 262, "20 strut 混排：不同字号共基线不跳行"))

if __name__ == "__main__":
    PROBE.mkdir(exist_ok=True)
    for k, v in sorted(P.items()):
        (PROBE / f"probe-{k}.snapshot").write_text(v, encoding="utf-8")
    print("wrote", len(P), "probes")
