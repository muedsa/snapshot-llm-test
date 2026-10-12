"""B01 能力探针 2：验证 RADIAL/SWEEP 渐变、描边文字、行内 WidgetSpan/Emoji、
fontFeatures、Container 裁剪、BackdropFilter 混合、Border/DecoratedBox、Image 平铺。

Run from suite root:
  python tmp/<run_id>/B01/probe_capabilities2.py
"""
import base64
import io
import os
from pathlib import Path

from PIL import Image, ImageDraw

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "B01"
(TMP / "probe").mkdir(parents=True, exist_ok=True)

F = 'fontFamily="Inter,Noto Sans CJK SC"'
BG = "#0A1120"
P = {"t0": "#F1F5F9", "t1": "#A9B8D0", "cyan": "#38BDF8", "amber": "#FBBF24",
     "green": "#34D399", "red": "#F87171", "violet": "#A78BFA", "pink": "#F472B6"}
PW, PH = 296, 330


def ps(x, y, w, h, inner):
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            + inner + "</Positioned>")


def box(w, h, **a):
    inner = a.pop("inner", None)
    at = "".join(f' {k}="{v}"' for k, v in a.items())
    if inner is None:
        return f'<Container width="{w}" height="{h}"{at}/>'
    return f'<Container width="{w}" height="{h}"{at}>' + inner + "</Container>"


def txt(s, color=None, size=22, style=None, **a):
    at = f'color="{color or P["t0"]}" fontSize="{size}" {F}'
    if style:
        at += f' fontStyle="{style}"'
    for k, v in a.items():
        at += f' {k}="{v}"'
    return f"<Text {at}>{s}</Text>"


def stack(kids, w=PW, h=PH, clip="NONE"):
    if not isinstance(kids, (list, tuple)):
        kids = [kids]
    return (f'<Stack width="{w}" height="{h}" alignment="TOP_LEFT" '
            f'clipBehavior="{clip}">' + "".join(kids) + "</Stack>")


def panel(i, title, note, inner):
    c, r = i % 5, i // 5
    x, y = 24 + c * 332, 24 + r * 500
    return (
        ps(x, y, 320, 460, box(320, 460, color="#111C33",
                               border="1 SOLID #23345A", borderRadius=14))
        + ps(x + 14, y + 10, 292, 30,
             box(292, 30, alignment="CENTER_LEFT",
                 inner=txt(title, size=20, style="BOLD")))
        + ps(x + 12, y + 46, PW, PH, inner)
        + ps(x + 14, y + 386, 292, 64,
             box(292, 64, alignment="TOP_LEFT",
                 inner=txt(note, color=P["t1"], size=16, maxLines=4))))


parts = []

# 1 RADIAL：gradientRadius 用 0~1 比例（探针 1 用像素值 110 导致整块纯色）
parts.append(panel(0, "1 RADIAL radius=0.5", "半径是比例不是像素；默认 CENTER / 0.5",
                   stack([ps(38, 55, 220, 220,
                             box(220, 220, borderRadius=110,
                                 gradientType="RADIAL",
                                 gradientColors="#FBBF24,#B45309,#0A1120",
                                 gradientRadius="0.5"))])))

# 2 RADIAL + 焦点（聚光灯）
parts.append(panel(1, "2 RADIAL + gradientFocal", "显式设半径时必须同时给焦点半径",
                   stack([ps(38, 55, 220, 220,
                             box(220, 220, borderRadius=110,
                                 gradientType="RADIAL",
                                 gradientColors="#38BDF8,#0A1120",
                                 gradientCenter="CENTER", gradientRadius="0.9",
                                 gradientFocal="TOP_LEFT",
                                 gradientFocalRadius="0.05"))])))

# 3 SWEEP 扫描渐变（做环形进度/雷达）
parts.append(panel(2, "3 SWEEP 扫描渐变", "startAngle/endAngle 弧度，默认 0~2pi",
                   stack([ps(38, 55, 220, 220,
                             box(220, 220, borderRadius=110,
                                 gradientType="SWEEP",
                                 gradientColors="#38BDF8,#34D399,#FBBF24,#F472B6,"
                                                "#A78BFA,#38BDF8",
                                 gradientCenter="CENTER",
                                 gradientStartAngle="0",
                                 gradientEndAngle="6.2832")),
                        ps(118, 135, 60, 60, box(60, 60, color="#111C33",
                                                 borderRadius=30))])))

# 4 描边文字
parts.append(panel(3, "4 文字前景 STROKE", "foregroundColor 是其他 foreground* 的前提",
                   stack([
                       ps(0, 30, PW, 70, box(PW, 70, alignment="CENTER",
                                             inner=txt("镂空描边", size=52,
                                                       style="BOLD",
                                                       foregroundColor=P["cyan"],
                                                       foregroundMode="STROKE",
                                                       foregroundStrokeWidth="3"))),
                       ps(0, 160, PW, 70, box(PW, 70, alignment="CENTER",
                                              inner=txt("描边加填充", size=44,
                                                        style="BOLD",
                                                        color="#111C33",
                                                        foregroundColor=P["amber"],
                                                        foregroundMode="STROKE_AND_FILL",
                                                        foregroundStrokeWidth="2")))])))

# 5 WidgetSpan + Emoji（行内图片）
def icon_b64():
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((2, 2, 30, 30), fill="#FBBF24")
    dr.polygon([(16, 7), (21, 18), (11, 18)], fill="#0A1120")
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


EMO = "data:image/png;base64," + icon_b64()
parts.append(panel(4, "5 WidgetSpan + Emoji", "行内占位盒 / 行内图片，可设 baseline",
                   stack([
                       ps(0, 20, PW, 120, box(PW, 120, alignment="TOP_LEFT",
                           inner=('<Text color="%s" fontSize="24" %s>行内小控件'
                                  '<WidgetSpan alignment="MIDDLE" width="40" '
                                  'height="24"><Container width="40" height="24" '
                                  'color="#34D399" borderRadius="12" '
                                  'alignment="CENTER"><Text color="#06111F" '
                                  'fontSize="14" %s>ON</Text></Container></WidgetSpan>'
                                  "之后的文字</Text>") % (P["t0"], F, F))),
                       ps(0, 170, PW, 90, box(PW, 90, alignment="TOP_LEFT",
                           inner=('<Text color="%s" fontSize="26" %s>图标 '
                                  '<Emoji dataUri="%s" width="30" height="30"/>'
                                  " 与文字同排</Text>") % (P["t1"], F, EMO)))])))

# 6 fontFeatures + Raw 保留空格
parts.append(panel(5, "6 fontFeatures + Raw", "tnum 等宽数字；Raw 不 trim 首尾空格",
                   stack([
                       ps(0, 20, PW, 40, box(PW, 40, alignment="CENTER_LEFT",
                                             inner=txt("1234567890 比例字体",
                                                       size=24))),
                       ps(0, 66, PW, 40, box(PW, 40, alignment="CENTER_LEFT",
                                             inner=txt("1234567890 tnum=2",
                                                       size=24,
                                                       fontFeatures="tnum=2"))),
                       ps(0, 118, PW, 40, box(PW, 40, alignment="CENTER_LEFT",
                                              inner=txt("SMALL CAPS smcp=2",
                                                        size=24,
                                                        fontFeatures="smcp=2"))),
                       ps(0, 170, PW, 60, box(PW, 60, alignment="TOP_LEFT",
                           inner=('<Text color="%s" fontSize="22" %s>'
                                  '<Raw color="%s" fontSize="22" %s>'
                                  "  首尾空格保留  </Raw>尾</Text>")
                           % (P["t0"], F, P["green"], F)))])))

# 7 Container clipBehavior（需背景装饰，纯色不够）
parts.append(panel(6, "7 Container clipBehavior", "clipBehavior 非 NONE 需要渐变/边框等作裁剪路径",
                   stack([
                       ps(38, 40, 220, 220,
                          box(220, 220, borderRadius=24, clipBehavior="ANTI_ALIAS",
                              gradientType="LINEAR",
                              gradientColors="#0EA5E9,#8B5CF6",
                              gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT",
                              inner=box(320, 90, color="#FBBF24",
                                        transform="(0.8660,0.5000,0,0,-0.5000,0.8660,"
                                                  "0,0,0,0,1,0,0,0,0,1)",
                                        transformAlignment="CENTER")))])))

# 8 BackdropFilter + blendMode
parts.append(panel(7, "8 BackdropFilter blendMode", "毛玻璃可叠加 Skia 混合模式",
                   stack([
                       ps(0, 0, PW, PH, box(PW, PH, borderRadius=10,
                                            gradientType="LINEAR",
                                            gradientColors="#F472B6,#0EA5E9",
                                            gradientBegin="TOP_CENTER",
                                            gradientEnd="BOTTOM_CENTER")),
                       ps(20, 30, 60, 260, box(60, 260, color="#FFFFFF")),
                       ps(120, 30, 150, 130,
                          '<ClipRRect borderRadius="16">'
                          '<BackdropFilter sigmaX="14" sigmaY="14" '
                          'blendMode="COLOR" tileMode="CLAMP">'
                          + box(150, 130, color="#00000022")
                          + "</BackdropFilter></ClipRRect>"),
                       ps(120, 180, 150, 130,
                          '<ClipRRect borderRadius="16">'
                          '<BackdropFilter sigmaX="14" sigmaY="14" '
                          'blendMode="SCREEN" tileMode="CLAMP">'
                          + box(150, 130, color="#00000022")
                          + "</BackdropFilter></ClipRRect>")])))

# 9 Border / DecoratedBox / ColoredBox 独立标签
parts.append(panel(8, "9 Border/DecoratedBox", "三个绘制装饰标签，最多一个子节点",
                   stack([
                       ps(20, 30, 250, 70,
                          '<Border border="4 SOLID #38BDF8" borderRadius="14" '
                          'gradientType="LINEAR" gradientColors="#38BDF8,#F472B6" '
                          'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT">'
                          + box(242, 62, color="#0E1830", borderRadius=10,
                                alignment="CENTER",
                                inner=txt("渐变 Border", size=22))
                          + "</Border>"),
                       ps(20, 130, 250, 70,
                          '<DecoratedBox position="FOREGROUND" color="#121E38" '
                          'borderRadius="12" boxShadow="0 6 16 0 #00000088 NORMAL">'
                          + box(250, 70, alignment="CENTER",
                                inner=txt("FOREGROUND 装饰", size=22))
                          + "</DecoratedBox>"),
                       ps(20, 230, 250, 60,
                          '<ColoredBox color="#34D39922">'
                          + box(250, 60, alignment="CENTER",
                                inner=txt("ColoredBox", size=22))
                          + "</ColoredBox>")])))

# 10 Image repeat / fit / colorBlendMode
def tile_b64():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.line((0, 16, 16, 0), fill="#FFFFFF55", width=3)
    dr.ellipse((5, 5, 11, 11), outline="#FFFFFF88")
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


TILE = "data:image/png;base64," + tile_b64()
parts.append(panel(9, "10 Image repeat/blend", "repeat 平铺 + colorBlendMode 着色",
                   stack([
                       ps(10, 20, 276, 130,
                          f'<Image dataUri="{TILE}" width="276" height="130" '
                          'fit="NONE" repeat="REPEAT" color="#38BDF8" '
                          'colorBlendMode="MULTIPLY"/>'),
                       ps(10, 165, 130, 130,
                          f'<Image dataUri="{TILE}" width="130" height="130" '
                          'fit="CONTAIN" scale="3"/>'),
                       ps(150, 165, 136, 130,
                          f'<Image dataUri="{TILE}" width="136" height="130" '
                          'fit="COVER" color="#F472B6" colorBlendMode="SRC_ATOP" '
                          'opacity="0.8"/>')])))

dsl = (f'<Snapshot background="{BG}" type="png">'
       f'<Container width="1680" height="1024">'
       + f'<Stack width="1680" height="1024" alignment="TOP_LEFT" '
         f'clipBehavior="NONE">{"".join(parts)}</Stack>'
       + "</Container></Snapshot>")
out = TMP / "probe" / "caps2.snapshot"
out.write_text(dsl, encoding="utf-8")
print(out, len(dsl), "bytes")
