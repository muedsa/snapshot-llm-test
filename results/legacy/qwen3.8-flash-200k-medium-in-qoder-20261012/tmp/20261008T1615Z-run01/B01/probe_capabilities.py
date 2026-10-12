"""B01 能力探针：一次请求验证 10 项整套里尚未实际用过的 DSL 能力。

Run from suite root:
  python tmp/<run_id>/B01/probe_capabilities.py
写 tmp/<run_id>/B01/probe/caps.snapshot（渲染由 render.py 完成）。
"""
import base64
import io
import os
from pathlib import Path

from PIL import Image

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "B01"
(TMP / "probe").mkdir(parents=True, exist_ok=True)

F = 'fontFamily="Inter,Noto Sans CJK SC"'
BG = "#0A1120"
P = {"t0": "#F1F5F9", "t1": "#A9B8D0", "cyan": "#38BDF8", "amber": "#FBBF24",
     "green": "#34D399", "red": "#F87171", "violet": "#A78BFA", "pink": "#F472B6"}
PW, PH = 296, 330          # 每格内容区


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


def col(kids):
    return ('<Column crossAxisAlignment="START" mainAxisAlignment="START">'
            + "".join(kids) + "</Column>")


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

# 1 毛玻璃：ClipRRect + BackdropFilter
parts.append(panel(0, "1 ClipRRect+BackdropFilter",
                   "背景必须先有内容才见效；裁剪限定模糊区域",
                   stack([
                       ps(0, 0, PW, PH, box(PW, PH, borderRadius=10,
                                            gradientType="LINEAR",
                                            gradientColors="#0EA5E9,#8B5CF6,#F472B6",
                                            gradientBegin="TOP_LEFT",
                                            gradientEnd="BOTTOM_RIGHT")),
                       ps(48, 65, 200, 200, box(200, 200, color="#FBBF24",
                                                borderRadius=100)),
                       ps(33, 90, 230, 150,
                          '<ClipRRect borderRadius="22" clipBehavior="ANTI_ALIAS">'
                          '<BackdropFilter sigmaX="18" sigmaY="18" tileMode="CLAMP">'
                          + box(230, 150, color="#FFFFFF33")
                          + "</BackdropFilter></ClipRRect>"),
                       ps(33, 90, 230, 150,
                          box(230, 150, border="2 SOLID #FFFFFFAA", borderRadius=22,
                              alignment="CENTER",
                              inner=txt("毛玻璃卡片", size=24, style="BOLD")))])))

# 2 子树高斯模糊（ImageFiltered）
bars = [box(240, 40, color="#38BDF8"), box(180, 40, color="#34D399"),
        box(120, 40, color="#F472B6")]
parts.append(panel(1, "2 ImageFiltered 子树模糊",
                   "高斯模糊作用于子树；下方同组色条作为不模糊对照",
                   stack([
                       ps(28, 20, 240, 150,
                          '<ImageFiltered sigmaX="9" sigmaY="9" tileMode="CLAMP">'
                          + col(bars) + "</ImageFiltered>"),
                       ps(28, 200, 240, 150, col(bars))])))

# 3 ClipOval + RADIAL 渐变
parts.append(panel(2, "3 ClipOval + RADIAL",
                   "椭圆裁剪默认 ANTI_ALIAS；RADIAL 需 gradientRadius",
                   stack([
                       ps(38, 55, 220, 220,
                          '<ClipOval clipBehavior="ANTI_ALIAS">'
                          + box(220, 220, gradientType="RADIAL",
                                gradientColors="#FBBF24,#B45309,#0A1120",
                                gradientRadius="110")
                          + "</ClipOval>")])))

# 4 ColorFiltered
parts.append(panel(3, "4 ColorFiltered MULTIPLY",
                   "color + Skia blendMode，作用于子树着色",
                   stack([
                       ps(0, 0, PW, PH,
                          '<ColorFiltered color="#F87171" blendMode="MULTIPLY">'
                          + stack([ps(cx * 148, cy * 165, 140, 150,
                                      box(140, 150, color=c))
                                   for cy, row in enumerate((("#38BDF8", "#F1F5F9"),
                                                             ("#34D399", "#FBBF24")))
                                   for cx, c in enumerate(row)])
                          + "</ColorFiltered>")])))

# 5 textShadow 多条
parts.append(panel(4, "5 textShadow 多阴影",
                   "x y [blur] [color]，逗号分隔可叠多条",
                   stack([
                       ps(0, 0, PW, PH, box(PW, PH, alignment="CENTER",
                                            inner=txt("霓虹标题", size=56,
                                                      style="BOLD",
                                                      textShadow="4 5 0 #0EA5E9AA,"
                                                                 "-4 -3 0 " + P["pink"]
                                                                 + "66,0 0 14 #FFFFFF55")))])))

# 6 boxShadow
parts.append(panel(5, "6 boxShadow 阴影",
                   "自定义 x y blur spread color style，或内置 ELEVATION_n",
                   stack([
                       ps(38, 30, 220, 90,
                          box(220, 90, color="#F8FAFC", borderRadius=12,
                              boxShadow="0 10 24 0 #000000AA NORMAL",
                              alignment="CENTER",
                              inner=txt("自定义阴影", color="#0A1120", style="BOLD"))),
                       ps(38, 200, 220, 90,
                          box(220, 90, color="#F8FAFC", borderRadius=12,
                              boxShadow="ELEVATION_16", alignment="CENTER",
                              inner=txt("ELEVATION_16", color="#0A1120",
                                        style="BOLD")))])))

# 7 Container transform（矩阵）
parts.append(panel(6, "7 Container transform",
                   "16 值列主序矩阵 + transformAlignment=CENTER",
                   stack([
                       ps(48, 105, 200, 120,
                          box(200, 120, color="#A78BFA", borderRadius=10,
                              transform="(0.9397,0.3420,0,0,-0.3420,0.9397,0,0,"
                                        "0,0,1,0,0,0,0,1)",
                              transformAlignment="CENTER",
                              inner=box(200, 120, alignment="CENTER",
                                        inner=txt("旋转 20 度", color="#0A1120",
                                                  style="BOLD"))))])))


def tiny_png_b64():
    im = Image.new("RGBA", (24, 24))
    for y in range(24):
        for x in range(24):
            im.putpixel((x, y), (20 + x * 9, 60 + y * 7, 140, 255))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


# 8 Image dataUri
b64 = tiny_png_b64()
parts.append(panel(7, "8 Image dataUri",
                   "仅 PNG/JPEG/WebP Base64，建树期解码，不走网络",
                   stack([
                       ps(48, 65, 200, 200,
                          f'<Image dataUri="data:image/png;base64,{b64}" '
                          'width="200" height="200" fit="FILL"/>')])))

# 9 overflow / letterSpacing / maxLines / height
parts.append(panel(8, "9 letterSpacing + overflow",
                   "ELLIPSIS 是否生效；maxLines 与 height 行高同时给出",
                   stack([
                       ps(0, 10, PW, 40,
                          box(PW, 40, alignment="CENTER_LEFT",
                              inner=txt("这是一段明显超出容器宽度的中文文字",
                                        size=24, letterSpacing="6",
                                        overflow="ELLIPSIS"))),
                       ps(0, 70, PW, 120,
                          box(PW, 120, alignment="TOP_LEFT",
                              inner=txt("第二格验证 maxLines 与 height 行高同时"
                                        "给出时的段落表现，看看是否会裁掉第三行，"
                                        "还是按两行省略。", color=P["t1"], size=22,
                                        maxLines=2, height="1.35",
                                        overflow="ELLIPSIS"))),
                       ps(0, 210, PW, 60,
                          box(PW, 60, alignment="TOP_LEFT",
                              inner=txt("WORD SPACING SIX", size=24,
                                        wordSpacing="6",
                                        decoration="LINE_THROUGH",
                                        decorationColor=P["cyan"])))])))

# 10 嵌套 Text（富文本）
parts.append(panel(9, "10 Text 嵌套子 Text",
                   "行内不同字号/颜色/背景/decoration 的富文本",
                   stack([
                       ps(0, 10, PW, 120,
                          box(PW, 120, alignment="TOP_LEFT",
                              inner=('<Text color="%s" fontSize="26" %s>主色文字'
                                      '<Text color="%s" fontSize="34" fontStyle="BOLD">'
                                      "强调段</Text>回到主色"
                                      '<Text color="#06111F" fontSize="22" '
                                      'backgroundColor="%s"> 高亮标签 </Text>'
                                      "</Text>") % (P["t0"], F, P["amber"],
                                                    P["green"]))),
                       ps(0, 170, PW, 80,
                          box(PW, 80, alignment="TOP_LEFT",
                              inner=('<Text color="%s" fontSize="22" %s>装饰线 '
                                      '<Text color="%s" %s decoration="UNDERLINE">'
                                      "下划线</Text>"
                                      '<Text color="%s" %s decoration="LINE_THROUGH">'
                                      "删除线</Text></Text>")
                              % (P["t1"], F, P["cyan"], F, P["red"], F)))])))

body = "".join(parts)
dsl = (f'<Snapshot background="{BG}" type="png">'
       f'<Container width="1680" height="1024">'
       + f'<Stack width="1680" height="1024" alignment="TOP_LEFT" '
         f'clipBehavior="NONE">{body}</Stack>'
       + "</Container></Snapshot>")
out = TMP / "probe" / "caps.snapshot"
out.write_text(dsl, encoding="utf-8")
print(out, len(dsl), "bytes")
