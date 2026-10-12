"""B03 手法构件：把探针验证过的能力包成可复用函数。

用法（各 case 生成器里）：

    import sys, os
    from pathlib import Path
    root = Path(os.environ["SNAPSHOT_TASK_ROOT"]); rid = os.environ["SNAPSHOT_RUN_ID"]
    for p in (root / "tmp" / rid / "_suite" / "scripts", root / "tmp" / rid / "B03"):
        sys.path.insert(0, str(p))
    from dslkit import Doc, TextFit
    import b03kit as K

每个函数注明依赖的探针（probe/ 里有真实响应与看图证据）。未验证的效果不用。
"""
import math

INK = "#1B1E22"
PAPER = "#F2EBDD"
MONO = "Consolas,Noto Sans Mono CJK SC,monospace"


def n(v):
    return f"{round(float(v), 4):g}"


# ---------- 矩阵（探针 01c：透视项不生效，只用 2D 仿射 + 平移） ----------
def mul(m1, m2):
    a1, b1, e1, c1, d1, f1 = m1
    a2, b2, e2, c2, d2, f2 = m2
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2, a1 * e2 + b1 * f2 + e1,
            c1 * a2 + d1 * c2, c1 * b2 + d1 * d2, c1 * e2 + d1 * f2 + f1)


def ident():
    return (1, 0, 0, 0, 1, 0)


def translate(tx, ty):
    return (1, 0, tx, 0, 1, ty)


def scale(sx, sy=None):
    return (sx, 0, 0, 0, (sy if sy is not None else sx), 0)


def rotate(rad):
    c, s = math.cos(rad), math.sin(rad)
    return (c, -s, 0, s, c, 0)


def skew(x=0.0, y=0.0):
    return (1, math.tan(x), 0, math.tan(y), 1, 0)


def matrix_attr(m):
    """6 元仿射 -> 解析器接受的列主序 4x4（探针 02-skew 生效）。"""
    a, b, tx, c, d, ty = m
    return f"({n(a)},{n(c)},0,0,{n(b)},{n(d)},0,0,0,0,1,0,{n(tx)},{n(ty)},0,1)"


def basis(cu, cv, tx=0.0, ty=0.0):
    """两个屏幕方向向量 -> 矩阵元组。

    m=(a,b,tx,c,d,ty) 表示 [[a,b,tx],[c,d,ty]]：局部 x 轴落到 (a,c)，局部 y 轴落到
    (b,d)（探针 B03 probe-anchor-02 用 120×40 非方形实测，TOP_LEFT 锚点＝槽位左上角）。
    于是 basis(cu, cv) 让宽沿 cu、高沿 cv；直接写 (cu[0],cu[1],0,cv[0],cv[1],0)
    会得到转置的映射，轴测面就会错开一个缺口。
    """
    return (cu[0], cv[0], tx, cu[1], cv[1], ty)


def xform(d, x, y, w, h, m, inner, align="TOP_LEFT"):
    d.pos(x, y, w, h,
          f'<Container width="{n(w)}" height="{n(h)}" transform="{matrix_attr(m)}" '
          f'transformAlignment="{align}">{inner}</Container>')


# ---------- 文本：支持探针验证的全套属性 ----------
_ALIGN = {"START": "CENTER_LEFT", "CENTER": "CENTER", "END": "CENTER_RIGHT"}


def text_markup(s, size, color, font=None, style=None, align=None, shadow=None,
                deco=None, deco_color=None, deco_style=None, deco_th=None,
                deco_gaps=None, fg=None, fg_mode=None, fg_w=None, spacing=None,
                word_spacing=None, height=None, features=None, maxlines=None,
                overflow=None, soft_wrap=None, bg=None, strut=None):
    a = [f'fontSize="{size}"', f'color="{color}"']
    if font:
        a.append(f'fontFamily="{font}"')
    if style:
        a.append(f'fontStyle="{style}"')
    if align:
        a.append(f'textAlign="{align}"')
    if shadow:
        a.append(f'textShadow="{shadow}"')
    if deco:
        a.append(f'decoration="{deco}"')
        if deco_color:
            a.append(f'decorationColor="{deco_color}"')
        if deco_style:
            a.append(f'decorationLineStyle="{deco_style}"')
        if deco_th:
            a.append(f'decorationThickness="{deco_th}"')
        if deco_gaps:
            a.append(f'decorationGaps="{deco_gaps}"')
    if fg:
        a.append(f'foregroundColor="{fg}"')
        if fg_mode:
            a.append(f'foregroundMode="{fg_mode}"')
        if fg_w:
            a.append(f'foregroundStrokeWidth="{fg_w}"')
    if spacing:
        a.append(f'letterSpacing="{spacing}"')
    if word_spacing:
        a.append(f'wordSpacing="{word_spacing}"')
    if height:
        a.append(f'height="{height}"')
    if features:
        a.append(f'fontFeatures="{features}"')
    if maxlines:
        a.append(f'maxLines="{maxlines}"')
    if overflow:
        a.append(f'overflow="{overflow}"')
    if soft_wrap is not None:
        a.append(f'softWrap="{"true" if soft_wrap else "false"}"')
    if bg:
        a.append(f'backgroundColor="{bg}"')
    if strut:
        a.append('strutEnabled="true"')
        for k, v in strut.items():
            a.append(f'strut{k}{v}')
    return "<Text " + " ".join(a) + ">" + s + "</Text>"


def tbox(d, x, y, w, h, markup, align="START", valign="MIDDLE"):
    va = {"TOP": "TOP_", "MIDDLE": "", "BOTTOM": "BOTTOM_"}[valign]
    ha = {"START": "LEFT", "CENTER": "CENTER", "END": "RIGHT"}[align]
    if va == "TOP":
        al = "TOP_" + ("CENTER" if ha == "CENTER" else ha)
    elif va == "BOTTOM":
        al = "BOTTOM_" + ("CENTER" if ha == "CENTER" else ha)
    else:
        al = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}[ha]
    d.pos(x, y, w, h, f'<Container width="{n(w)}" height="{n(h)}" alignment="{al}">'
                      + markup + "</Container>")


def tlab(d, tf, tag, x, y, w, h, s, size, color, lines=1, **kw):
    """带 TextFit 闸门的文本（闸门只估算，真实结果仍以看图为准）。"""
    tf.check(tag, s, size, w, h, lines=lines)
    align = kw.pop("align", "START")
    valign = kw.pop("valign", "MIDDLE")
    font = kw.pop("font", getattr(d, "font", None))
    # 解析器不做实体解码：正文里的 < / > 会让整份 DSL 400（case-06 v03 的 222 字节错误体），
    # 必须走 CDATA；& 单独出现时按 &amp; 处理。
    if "<" in s or ">" in s:
        txt = f"<![CDATA[{s}]]>"
    else:
        txt = s.replace("&", "&amp;") if "&" in s else s
    tbox(d, x, y, w, h, text_markup(txt, size, color, font=font, **kw),
         align=align, valign=valign)


# ---------- 探针手法 ----------
def neon(d, tf, tag, x, y, w, h, s, size, core="#FFF3C4",
         glow=("#E0A526", "#C8552B", "#C8552B"), sigmas=(8, 22, 46),
         style="BOLD", font=None, align="START"):
    """多层 textShadow 辉光（探针 06b 下半：三层 blur 霓虹成立）。"""
    shadow = ",".join(f"0 0 {sg} {c}" for c, sg in zip(glow, sigmas))
    tlab(d, tf, tag, x, y, w, h, s, size, core, style=style, shadow=shadow,
         align=align, font=font)


def neon_if(d, x, y, w, h, s, size, core="#FFF6D8",
            glow=("#E0A526", "#FFE9A8"), sigmas=(26, 9), style="BOLD", font=None,
            align="START", tf=None, tag=None):
    """真·霓虹辉光：ImageFiltered 对整层文字做高斯模糊（探针 20a）。

    对比证据：case-01 v01 用三层 textShadow（sigma 52），大模糊被文字排版矩形
    裁成一块方形光板（qa-sign.png）；ImageFiltered 由解析器自动补
    blurImageFilterBounds，辉光按字形外扩且不被盒子截断。
    """
    def layer(color, sigma=None):
        inner = (f'<Container width="{n(w)}" height="{n(h)}" alignment="{_ALIGN[align]}">'
                 + text_markup(s, size, color, font=font, style=style) + "</Container>")
        if sigma:
            inner = f'<ImageFiltered sigmaX="{n(sigma)}" sigmaY="{n(sigma)}">{inner}</ImageFiltered>'
        d.pos(x, y, w, h, inner)

    for c, sg in zip(glow, sigmas):
        layer(c, sg)
    if tf is not None:
        tf.check(tag or "neon-if", s, size, w, h)
    layer(core)


def outline(d, tf, tag, x, y, w, h, s, size, stroke, fill=None, width=2.2,
            style="BOLD", align="START", font=None):
    """描边字（探针 06 / 06b：STROKE 与 STROKE_AND_FILL 成立）。"""
    tlab(d, tf, tag, x, y, w, h, s, size, fill or stroke, align=align, style=style,
         font=font, fg=stroke, fg_mode="STROKE_AND_FILL" if fill else "STROKE",
         fg_w=width)


def halftone(d, x, y, w, h, lum, cols, rows, color, max_r=None, min_r=0.35):
    """程序化半调网点：亮度越低点越大（配合 ColorFiltered 做双色叠印）。"""
    cw, ch = w / cols, h / rows
    max_r = max_r or min(cw, ch) / 2
    for r in range(rows):
        for c in range(cols):
            v = max(0.0, min(1.0, lum(c / max(1, cols - 1), r / max(1, rows - 1))))
            rad = max_r * math.sqrt(1 - v)
            if rad < min_r:
                continue
            d.dot(x + (c + .5) * cw, y + (r + .5) * ch, rad * 2, color)


def sweep_disc(d, x, y, size, colors, tile="REPEAT", span=math.pi / 4, stops=None,
               oval=True, start=0.0):
    """SWEEP 渐变 + 平铺（探针 04c；SWEEP 不接受 gradientRadius，见 04 的 400 响应）。

    start 为起始弧度；Flutter 的 sweep 从正 x 轴（3 点钟）顺时针扫，所以
    要让 0 落在 12 点钟就传 -pi/2（或等价的 3*pi/2，非负值更保险）。
    """
    st = f' gradientStops="{stops}"' if stops else ""
    d.pos(x, y, size, size,
          f'<Container width="{n(size)}" height="{n(size)}"'
          + (f' borderRadius="{n(size/2)}"' if oval else "")
          + f' gradientType="SWEEP" gradientColors="{",".join(colors)}"{st} '
            f'gradientTileMode="{tile}" gradientCenter="CENTER" '
            f'gradientStartAngle="{n(start)}" gradientEndAngle="{n(span)}"/>')


def polar_ticks(d, cx, cy, r0, r1, n_ticks, color, thick=2, every=1, minor_ratio=0.55):
    """极坐标刻度：逐根旋转矩形（dslkit.line 的 rotate 矩阵在 A/B 赛道已反复验证）。"""
    for i in range(n_ticks):
        a = -math.pi / 2 + i * 2 * math.pi / n_ticks
        major = (i % every == 0)
        rr = r1 if major else r0 + (r1 - r0) * minor_ratio
        d.line(cx + math.cos(a) * r0, cy + math.sin(a) * r0,
               cx + math.cos(a) * rr, cy + math.sin(a) * rr,
               thick if major else max(1, thick - 1), color)


def blend(d, x, y, w, h, color, mode, inner, radius=None):
    """ColorFiltered 叠色（探针 10b/11b/12b：12 种 Skia BlendMode 均可用）。"""
    d.pos(x, y, w, h,
          f'<ColorFiltered color="{color}" blendMode="{mode}">'
          f'<Container width="{n(w)}" height="{n(h)}"'
          + (f' borderRadius="{radius}"' if radius else "")
          + f'>{inner}</Container></ColorFiltered>')


def frost(d, x, y, w, h, sigma=10, tint="#FFFFFF26", radius=18, oval=False,
          border=None):
    """毛玻璃（探针 13：BackdropFilter 会模糊其下的文字与渐变）。"""
    clip = ('<ClipOval clipBehavior="ANTI_ALIAS">' if oval else
            f'<ClipRRect borderRadius="{radius}" clipBehavior="ANTI_ALIAS">')
    close = "</ClipOval>" if oval else "</ClipRRect>"
    inner = (f'<Container width="{n(w)}" height="{n(h)}" color="{tint}"'
             + ("" if oval else f' borderRadius="{radius}"')
             + (f' border="{border}"' if border else "") + "/>")
    d.pos(x, y, w, h, f'{clip}<BackdropFilter sigmaX="{sigma}" sigmaY="{sigma}">'
                      f'{inner}</BackdropFilter>{close}')


def overprint(d, x, y, w, h, lumA, lumB, cols, rows, inkA, inkB, inkAB,
              thresh=0.12, stagger=True):
    """Riso 双色叠印：同一网点网格上按两套亮度分派 A / B / A×B 三色。

    Flutter 的 ColorFiltered 只过滤子树自身像素、不与背景混合（探针 10b/11b/12b 的
    叠色都只作用于 inner 内），所以真叠印必须显式算交并：coverage=1-lum，两色都上墨
    的格子改画混合色（乘算），网点半径 ∝ sqrt(coverage)。stagger 让奇偶行错半格，
    近似丝网印的斜网纹。
    """
    cw, ch = w / cols, h / rows
    max_r = min(cw, ch) / 2
    for r in range(rows):
        off = (cw / 2) if (stagger and r % 2) else 0.0
        ncols = cols - (1 if off else 0)      # 错半格的行少画一列，边界不出现半个点
        for c in range(ncols):
            u = (c + 0.5) / cols
            v = (r + 0.5) / rows
            ca, cb = 1 - lumA(u, v), 1 - lumB(u, v)
            ca = max(0.0, min(1.0, ca))
            cb = max(0.0, min(1.0, cb))
            cx = x + (c + 0.5) * cw + off
            cy = y + (r + 0.5) * ch
            if cx > x + w:
                continue
            if ca > thresh and cb > thresh:
                rad = max_r * math.sqrt(min(1.0, max(ca, cb)))
                d.dot(cx, cy, rad * 2, inkAB)
            elif ca > thresh:
                d.dot(cx, cy, max_r * math.sqrt(ca) * 2, inkA)
            elif cb > thresh:
                d.dot(cx, cy, max_r * math.sqrt(cb) * 2, inkB)


def raw_block(d, x, y, w, h, lines, size, color, height=None, font=MONO):
    """Raw 保留空格与换行（探针 09：等宽块字符可作画）。"""
    hd = f' height="{height}"' if height else ""
    d.pos(x, y, w, h,
          f'<Text fontSize="{size}" color="{color}" fontFamily="{font}"{hd}>'
          f'<Raw>{chr(10).join(lines)}</Raw></Text>')


def leader_dots(d, x, y, w, title, page, size, color, dot_color, dot=3, pitch=12,
                title_w=None, page_w=130):
    """引导线方案 B：标题左、页码右，中间按固定间距画圆点（完全可控）。"""
    tw = title_w or w * 0.6
    tlab_plain = text_markup(title, size, color)
    tbox(d, x, y, tw, size * 1.6, tlab_plain)
    d.pos(x + w - page_w, y, page_w, size * 1.6,
          f'<Container width="{n(page_w)}" height="{n(size*1.6)}" alignment="CENTER_RIGHT">'
          + text_markup(page, size, color) + "</Container>")
    gap0, gap1 = x + tw + 8, x + w - page_w - 8
    k = gap0 + pitch / 2
    while k < gap1:
        d.dot(k, y + size * 0.82, dot, dot_color)
        k += pitch


def badge_span(letter, bg, fg="#FFFFFF", box=20, radius=4, font=13,
               align="BASELINE"):
    """行内角标：WidgetSpan 里放带 Text 的 Container（探针 wschip 成立）。"""
    return (f'<WidgetSpan alignment="{align}"><Container width="{box}" height="{box}" '
            f'borderRadius="{radius}" color="{bg}" alignment="CENTER">'
            f'<Text fontSize="{font}" color="{fg}" textAlign="CENTER">{letter}</Text>'
            f'</Container></WidgetSpan>')


def inline_runs(d, x, y, w, h, runs, size, color, font=None, align="START",
                valign="MIDDLE"):
    """行内混排：runs = [("t", 文本) | ("chip", 宽, 高, 色, 圆角, 对齐)
    | ("badge", 字母, 底色, 字色)]（探针 08 / wschip）。"""
    body = ""
    for r in runs:
        if r[0] == "t":
            body += r[1]
        elif r[0] == "badge":
            body += badge_span(r[1], r[2], r[3])
        else:
            _, cw, ch, cc, rad, al = r
            body += (f'<WidgetSpan alignment="{al}"><Container width="{cw}" '
                     f'height="{ch}" color="{cc}"'
                     + (f' borderRadius="{rad}"' if rad else "") + "/></WidgetSpan>")
    d.pos(x, y, w, h,
          f'<Container width="{n(w)}" height="{n(h)}" alignment="{_ALIGN[align]}">'
          + text_markup(body, size, color, font=font) + "</Container>")


def mix(c, tone):
    """按明度系数缩放单色（轴测三面受光差用），通道乘 tone 后截断到 0..255。"""
    h = c.lstrip("#")
    return "#" + "".join(f"{min(255, max(0, round(int(h[i:i+2], 16) * tone))):02X}"
                         for i in (0, 2, 4))


def pct(v, digits=1):
    return f"{v * 100:.{digits}f}%"


def money(v):
    return f"¥{v:,.0f}"


def rule_leader(d, x, y, w, h, style="DOTTED", color="#8A8F98", thick=2.0,
                gaps="2,7", size=20):
    """程序化引导线：DOTTED 圆点 / DASHED 短横 / DOUBLE 双细线 / SOLID 单线。

    不能用空白 Text 的装饰线：探针 l/m/f 证明纯空格 <Text> 一个像素都不画，
    而带 clipBehavior 的 <Container> 一律 400（探针 k/n/o/p，需背景装饰才能成裁剪路径）。
    所以这里按 gaps 给出的「线长,间隔」自己画几何节点，长度恰好等于 w。
    """
    mid = y + h / 2.0
    parts = [float(v) for v in str(gaps).split(",") if v.strip() != ""]
    a = parts[0] if parts else 2.0
    b = parts[1] if len(parts) > 1 else 7.0
    if style == "DOTTED":
        r = max(1.5, thick / 2.0)
        pitch = max(4.0, a + b)
        k = x + r
        while k <= x + w - r:
            d.dot(k, mid, r * 2, color)
            k += pitch
    elif style == "DASHED":
        dl, gl = max(4.0, a), max(2.0, b)
        k = 0.0
        while k < w:
            d.line(x + k, mid, x + min(k + dl, w), mid, thick, color)
            k += dl + gl
    elif style == "DOUBLE":
        off = max(2.0, thick)
        t = max(1.0, thick / 2.0)
        d.line(x, mid - off, x + w, mid - off, t, color)
        d.line(x, mid + off, x + w, mid + off, t, color)
    else:
        d.line(x, mid, x + w, mid, thick, color)
