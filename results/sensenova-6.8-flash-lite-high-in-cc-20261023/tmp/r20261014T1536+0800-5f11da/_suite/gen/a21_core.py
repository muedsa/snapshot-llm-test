"""A21 三轮共用核心：设计 token、品牌图形、版式构造与布局模型。

三轮复用同一套构造器，各轮通过 cfg 覆盖项（token、文案、几何）产生真实差异；
构造器同时产出 layout 模型（元素矩形与文字），供碰撞审计与 content-map.json 复用。

能力依据（均为本次实测，见 tmp/<run>/A21/responses/ 的 probe1/probe2）：
  - Container 支持 gradientType / gradientColors / gradientStops / gradientBegin /
    gradientEnd / gradientCenter / gradientRadius / gradientFocal /
    gradientFocalRadius、boxShadow、shape="CIRCLE"、borderRadius、border
  - <Opacity opacity="0..1"> 对子树生效
  - Container 的 transform 属性与 <Transform matrix origin alignment> 均可旋转
  - Text 支持 letterSpacing / height / maxLines / softWrap / textAlign /
    fontStyle / decoration / textShadow / 嵌套 Text 混色
约束依据（A13-A20 实测）：
  - <Rect>/<Circle>/<Line>/<Path> 不存在；文字写在 text 属性里
  - <Container>/<Positioned> 最多一个子节点；<Stack> 按文档顺序绘制，后者在上
  - 属性值不得含 < 与 &；括号只允许出现在 transform / matrix / origin
"""
from __future__ import annotations

FONT = "Noto Sans CJK SC,Inter"

# ---- 色板（三轮共用基线，各轮可覆盖）----
C = {
    "bg_deep": "#060A18",
    "bg_panel": "#0E1936",
    "rule": "#24385E",
    "primary": "#5FE0FF",
    "primary_2": "#1E86C8",
    "primary_3": "#0B2B4E",
    "glow": "#EAFDFF",
    "accent": "#FFC26B",
    "ink": "#F5F9FF",
    "muted": "#8FA3C2",
}

# 叠层板材：由暗到亮，(填充, 描边)
SHEETS = [
    ("#0E2440", "#2A4E74"),
    ("#134C79", "#2E86BE"),
    ("#1A6FA8", "#59C8EE"),
]


# ---------------------------------------------------------------- 基元


class Canvas:
    """累积 DSL 行与布局模型。"""

    def __init__(self, w: int, h: int, bg: str):
        self.w, self.h, self.bg = w, h, bg
        self.lines: list[str] = []
        self.layout: list[dict] = []

    def box(self, left, top, w, h, *, color=None, border=None, radius=None,
            shape=None, gradient=None, stops=None, begin=None, end=None,
            center=None, gradius=None, focal=None, fradius=None,
            shadow=None, transform=None, transform_align=None,
            opacity=None, kind="shape", role="", record=True, **extra):
        """一个 <Positioned><Container/> 组合。gradient 为颜色列表。"""
        attrs = ['width="%d"' % w, 'height="%d"' % h]
        if shape:
            attrs.append('shape="%s"' % shape)
        # 服务端实测：shape="CIRCLE" 与 borderRadius 互斥
        # （PARSE_ERROR "Attr [borderRadius] can not be used with shape CIRCLE"），
        # 圆形本身已等角，无需圆角属性。
        elif radius is not None:
            attrs.append('borderRadius="%d"' % radius)
        if color:
            attrs.append('color="%s"' % color)
        if border:
            attrs.append('border="%s"' % border)
        if shadow:
            attrs.append('boxShadow="%s"' % shadow)
        if gradient:
            attrs.append('gradientType="%s"' % gradient[0])
            attrs.append('gradientColors="%s"' % ",".join(gradient[1]))
            if gradient[2]:
                attrs.append('gradientStops="%s"' % ",".join(gradient[2]))
            if begin:
                attrs.append('gradientBegin="%s"' % begin)
            if end:
                attrs.append('gradientEnd="%s"' % end)
        if center:
            attrs.append('gradientCenter="%s"' % center)
        if gradius is not None:
            attrs.append('gradientRadius="%.2f"' % gradius)
        if focal:
            attrs.append('gradientFocal="%s"' % focal)
        if fradius is not None:
            attrs.append('gradientFocalRadius="%.2f"' % fradius)
        if transform:
            attrs.append('transform="%s"' % transform)
        if transform_align:
            attrs.append('transformAlignment="%s"' % transform_align)
        for k, v in extra.items():
            attrs.append('%s="%s"' % (k, v))

        body = "    <Container %s />" % " ".join(attrs)
        if opacity is not None:
            body = '    <Opacity opacity="%.2f">\n      <Container %s />\n    </Opacity>' \
                   % (opacity, " ".join(attrs))
        self.lines.append('  <Positioned left="%d" top="%d" width="%d" height="%d">'
                          % (left, top, w, h))
        self.lines.append(body)
        self.lines.append("  </Positioned>")
        if record:
            self.layout.append({
                "kind": kind, "role": role,
                "box": [left, top, left + w, top + h],
                "color": color, "opacity": opacity,
            })
        return self

    def text(self, left, top, w, h, text, size, *, color=None, role="",
             bold=False, spacing=None, align=None, soft_wrap=None,
             max_lines=None, line_h=None, shadow=None, deco=None,
             deco_color=None, kind="text", record=True, children=None,
             record_text=True):
        """一段绝对定位文本。children 为嵌套 span 列表 [(text,color,size,spacing)]。

        record_text=False 时不向 DSL 输出这个 <Text> 节点，但 layout 模型仍记录它
        （record=True 时）。这样可以用同一份构造器生成“去文字”的辅助图，用来量取
        文字下方的实际合成背景；layout 模型保持不变，坐标仍然对得上。
        """
        style = ['fontFamily="%s"' % FONT, 'fontSize="%d"' % size]
        if color:
            style.append('color="%s"' % color)
        if bold:
            style.append('fontStyle="BOLD"')
        if spacing is not None:
            style.append('letterSpacing="%d"' % spacing)
        if align:
            style.append('textAlign="%s"' % align)
        if soft_wrap is not None:
            style.append('softWrap="%s"' % ("true" if soft_wrap else "false"))
        if max_lines is not None:
            style.append('maxLines="%d"' % max_lines)
        if line_h is not None:
            style.append('height="%.2f"' % line_h)
        if shadow:
            style.append('textShadow="%s"' % shadow)
        if deco:
            style.append('decoration="%s"' % deco)
            if deco_color:
                style.append('decorationColor="%s"' % deco_color)

        if children:
            inner = "".join(
                '<Text text="%s" fontFamily="%s" fontSize="%d" color="%s"%s />'
                % (c[0], FONT, c[2], c[1],
                   ' letterSpacing="%d"' % c[3] if len(c) > 3 and c[3] else "")
                for c in children)
            body = "    <Text %s>%s</Text>" % (" ".join(style), inner)
        else:
            body = "    <Text text=\"%s\" %s />" % (text, " ".join(style))

        if record_text:
            self.lines.append('  <Positioned left="%d" top="%d" width="%d" height="%d">'
                              % (left, top, w, h))
            self.lines.append(body)
            self.lines.append("  </Positioned>")
        if record:
            self.layout.append({
                "kind": kind, "role": role, "text": text, "fontSize": size,
                "color": color, "box": [left, top, left + w, top + h],
                "bold": bold, "letterSpacing": spacing,
                "textAlign": align, "lines": 1,
            })
        return self

    def dsl(self) -> str:
        return "\n".join(
            ['<Snapshot type="png" background="%s">' % self.bg,
             '  <Container width="%d" height="%d">' % (self.w, self.h),
             '   <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
             % (self.w, self.h)]
            + self.lines
            + ["   </Stack>", "  </Container>", "</Snapshot>", ""])


def rot_matrix(deg: float) -> str:
    """列主序 4x4 旋转矩阵，服务端要求 (m0,...,m15) 带括号且不含空白。"""
    import math
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return "({:.6f},{:.6f},0,0,{:.6f},{:.6f},0,0,0,0,1,0,0,0,0,1)".format(
        c, s, -s, c)


# ---------------------------------------------------------------- 品牌图形


def draw_mark(cv: Canvas, left: int, top: int, size: int, *, sheets: int = 3,
              off_ratio: float = 0.17, core=True, ring=False,
              sheets_palette: list = None, core_color: str = None,
              core_shadow: str = "0 8 22 #5FE0FF66", ring_color: str = None):
    """叠层主标记：sheets 张板材沿右下方向偏移 + 亮核（+ 可选外环）。

    标记实际占位约为 size*(1+off_ratio*(sheets-1)) + 2px 描边，绘制时向右下溢出，
    因此 left/top 是最后（最亮）那张板材的左上角。

    第 3 轮改浅色主题时给 sheets_palette / core_color / core_shadow 一个覆盖项，
    使亮核与描边能在浅底上读出；默认值与前两轮完全一致，改动不影响旧轮输出。
    """
    pal = sheets_palette or SHEETS
    off = int(round(size * off_ratio))
    radius = int(round(size * 0.30))
    for i in range(sheets):
        col, brd = pal[min(i, len(pal) - 1)]
        cv.box(left + i * off, top + i * off, size, size,
               color=col, border="2 SOLID %s" % brd, radius=radius,
               kind="brand_sheet", role="light-sheet")
    if ring:
        cv.box(left - 14, top - 14, size + 28, size + 28,
               color=None, border="1 SOLID %s" % (ring_color or C["rule"]),
               radius=radius + 14, kind="brand_ring", role="hairline-rule")
    if core:
        cs = int(round(size * 0.40))
        pad = int(round((size - cs) / 2))
        fx = left + (sheets - 1) * off + pad
        fy = top + (sheets - 1) * off + pad
        cv.box(fx, fy, cs, cs, color=core_color or C["glow"],
               radius=int(round(cs * 0.34)), shadow=core_shadow,
               kind="brand_core", role="light-core")
    return cv


def draw_orb(cv: Canvas, center_x: int, center_y: int, radius: int, *,
             halo: bool = True, ring: bool = True, bands: list[dict] = None,
             halo_scale: float = 3.4, halo_stops: list = None,
             halo_gradius: float = 0.72, halo_opacity: float = 0.42,
             ring_color: str = None, ring_pad: int = 34,
             core_stops: list = None, core_gradius: float = 0.60,
             band_color: str = None):
    """发光球：居心径向渐变（实测立体效果最佳的参数），可选外辉光与外环。

    注意：加 gradientFocal 偏移会把亮点推出可见范围导致球体发平，故不使用 focal。
    第 3 轮浅色主题通过 halo_scale / *_stops / *_color 覆盖形状与色带：
    深底的辉光在浅底上会显成深色斑块，且 3.4r 的半径会让外辉光伸到左栏文字与
    网址牌区域，故浅底改用更收敛的半径与浅色带；默认值与前两轮逐字节一致。
    """
    d = radius * 2
    if halo:
        hd = int(radius * halo_scale)
        cv.box(center_x - hd // 2, center_y - hd // 2, hd, hd, shape="CIRCLE",
               gradient=("RADIAL", halo_stops or ["#1E86C8", "#08182C"], None),
               gradius=halo_gradius, opacity=halo_opacity,
               kind="orb_halo", role="light-orb")
    if ring:
        rd = d + ring_pad
        cv.box(center_x - rd // 2, center_y - rd // 2, rd, rd, shape="CIRCLE",
               color=None, border="1 SOLID %s" % (ring_color or C["primary_2"]),
               kind="orb_ring", role="hairline-rule")
    cv.box(center_x - radius, center_y - radius, d, d, shape="CIRCLE",
           gradient=("RADIAL",
                     core_stops or ["#A8F0FF", "#1E86C8", "#0B2B4E"], None),
           gradius=core_gradius, kind="orb_core", role="light-orb")
    for b in (bands or []):
        w = b["w"]
        cv.box(center_x - w // 2, center_y + b["dy"] - b["h"] // 2,
               w, b["h"], color=band_color or C["glow"], radius=b["h"] // 2,
               opacity=b["opacity"], transform=b.get("rot"),
               transform_align="CENTER", kind="band", role="light-band")
    return cv


def assert_dsl_wellformed(dsl: str) -> None:
    """提交前本地防呆：< 与 & 一律禁止；括号只对矩阵类属性放行。"""
    import re
    bad = re.findall(r'([A-Za-z][A-Za-z0-9]*)="[^"]*[<&][^"]*"', dsl)
    if bad:
        raise AssertionError("属性值含 < 或 &: %s" % bad[:3])
    for m in re.finditer(r'([A-Za-z][A-Za-z0-9]*)="([^"]*)"', dsl):
        if "(" in m.group(2) and m.group(1) not in ("transform", "matrix",
                                                     "origin"):
            raise AssertionError("属性 %s 含括号: %r" % (m.group(1),
                                                        m.group(2)[:60]))
    if "\r" in dsl:
        raise AssertionError("DSL 含 CRLF，须为 LF")
    assert len(dsl.encode("utf-8")) <= 1048576, "DSL 超过请求体上限"
