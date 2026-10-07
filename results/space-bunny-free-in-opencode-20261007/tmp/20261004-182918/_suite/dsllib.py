"""Small helper layer for emitting Snapshot class-DOM DSL text.

Design goal: absolute pixel control. Charts, tables and dashboards are emitted as a
single Stack whose children are Positioned with explicit left/top/width/height, so
geometry in the DSL matches the computed geometry exactly.
"""
from __future__ import annotations

from xml.sax.saxutils import escape

LATIN = "Inter"
MONO = "DejaVu Sans Mono"
SERIF = "DejaVu Serif"
CJK = "Noto Sans CJK SC"
CJK_SERIF = "Noto Serif CJK SC"
UI = "Inter,Noto Sans CJK SC"          # latin first, CJK fallback
UI_SERIF = "DejaVu Serif,Noto Serif CJK SC"


def esc(v) -> str:
    s = str(v)
    return escape(s)


def _num(v):
    return str(v) if isinstance(v, str) else round(float(v), 2)


def attrs(d: dict) -> str:
    out = []
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, bool):
            v = "true" if v else "false"
        out.append(' %s="%s"' % (k, esc(v)))
    return "".join(out)


def el(tag: str, a: dict | None = None, children=None, text: str | None = None,
       indent: int = 0) -> str:
    pad = " " * indent
    a = dict(a or {})
    if text is not None:
        a.setdefault("text", text)
    body = "\n".join(children) if children else None
    head = "<%s%s" % (tag, attrs(a))
    if body is None:
        return pad + head + " />"
    return pad + head + ">\n" + body + "\n" + pad + "</%s>" % tag


def cdata(text: str) -> str:
    return "<![CDATA[%s]]>" % text.replace("]]>", "]]]]><![CDATA[>")


WARNINGS = []


def est_width(s: str, size: float) -> float:
    """Rough advance-width estimate: CJK/full-width ~1.0em, latin/digits ~0.55em."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E80 or o in (0x2018, 0x2019, 0x201C, 0x201D) or ch in "，。、：；！？（）《》“”·—…":
            w += size
        elif ch == " ":
            w += size * 0.28
        else:
            w += size * 0.55
    return w


def est_lines(s: str, size: float, box_w: float) -> int:
    if box_w <= 0:
        return 99
    return max(1, int(est_width(s, size) / box_w) + (1 if est_width(s, size) % box_w else 0))


def warnings() -> list:
    return list(WARNINGS)


def _check_fit(tag: str, s: str, size: float, w, h):
    if w is None:
        return
    lines = est_lines(s, size, w)
    capacity = 99 if h is None else max(1, int(h // (size * 1.18)))
    if lines > capacity:
        WARNINGS.append(
            "%s: text needs ~%d line(s) but box holds %d (w=%s h=%s size=%s) -> %r"
            % (tag, lines, capacity, w, h, size, s[:70]))


def text_el(s: str, *, x: float = 0, y: float = 0, w: float | None = None,
            h: float | None = None, color: str = "#0F172AFF", size: float = 20,
            font: str = UI, style: str | None = None, align: str | None = None,
            ls: float | None = None, word_spacing: float | None = None,
            max_lines: int | None = None, wrap: bool | None = None,
            decorate: str | None = None, deco_color: str | None = None,
            deco_thick: float | None = None, shadow: str | None = None,
            tag: str = "Positioned", baseline: str | None = None,
            features: str | None = None, bg: str | None = None,
            line_height: float | None = None, italic: bool | None = None,
            extra: dict | None = None) -> str:
    """Absolute-positioned Text. (x, y) is the top-left of the text box."""
    a = {"color": color, "fontSize": _num(size), "fontFamily": font}
    if style:
        a["fontStyle"] = style
    elif italic:
        a["fontStyle"] = "ITALIC"
    if align:
        a["textAlign"] = align
    if ls is not None:
        a["letterSpacing"] = _num(ls)
    if word_spacing is not None:
        a["wordSpacing"] = _num(word_spacing)
    if max_lines is not None:
        a["maxLines"] = max_lines
    if wrap is not None:
        a["softWrap"] = wrap
    if decorate:
        a["decoration"] = decorate
    if deco_color:
        a["decorationColor"] = deco_color
    if deco_thick is not None:
        a["decorationThickness"] = _num(deco_thick)
    if shadow:
        a["textShadow"] = shadow
    if baseline:
        a["baselineMode"] = baseline
    if features:
        a["fontFeatures"] = features
    if bg:
        a["backgroundColor"] = bg
    if line_height is not None:
        pass  # intentionally ignored: Text height below the wrapped height renders blank
    if extra:
        a.update(extra)
    _check_fit("text@%d,%d" % (x, y), s, float(size), w, h)
    raw = ("<" in s) or ("&" in s) or (">" in s)
    inner = el("Text", a, [cdata(s)] if raw else None, text=None if raw else s)
    pa = {"left": round(x, 2), "top": round(y, 2)}
    if w is not None:
        pa["width"] = round(w, 2)
    if h is not None:
        pa["height"] = round(h, 2)
    return el(tag, pa, [inner])


def box(x: float, y: float, w: float, h: float, *, color: str | None = None,
        radius: float | None = None, border: str | None = None,
        shadow: str | None = None, gradient: dict | None = None,
        children=None, tag: str = "Positioned", opacity: float | None = None,
        border_sides: dict | None = None, radii: dict | None = None,
        extra: dict | None = None, clip: str | None = None,
        bg_only: bool = False) -> str:
    """Absolutely positioned rectangle. `y` is the TOP edge.

    The service requires every Positioned node to carry a real child widget, so
    this helper always emits Positioned > Container(...).
    """
    W, H = round(w, 2), round(h, 2)
    pa = {"left": round(x, 2), "top": round(y, 2), "width": W, "height": H}
    dec = {}
    if color:
        dec["color"] = color
    if radius is not None:
        dec["borderRadius"] = _num(radius)
    if radii:
        for k, v in radii.items():
            dec["borderRadius" + k] = _num(v)
    if border:
        dec["border"] = border
    if border_sides:
        dec.update(border_sides)
    if shadow:
        dec["boxShadow"] = shadow
    if opacity is not None:
        dec["opacity"] = round(opacity, 4)
    if gradient:
        dec.update(gradient)
    if extra:
        dec.update(extra)

    kids = children or []
    if clip:
        clip_a = {"width": W, "height": H}
        if radius is not None:
            clip_a["borderRadius"] = _num(radius)
        if radii:
            for k, v in radii.items():
                clip_a["borderRadius" + k] = _num(v)
        if border:
            clip_a["border"] = border
        core = dict(clip_a)
        if color:
            core["color"] = color
        if shadow:
            core["boxShadow"] = shadow
        if extra:
            core.update(extra)
        if gradient:
            core.update(gradient)
        inner = el(clip, clip_a, [el("Container", core, kids)])
        return el(tag, pa, [inner])
    if kids:
        if bg_only:
            inner = el("Container", dict(dec, width=W, height=H), kids)
        elif dec:
            inner = el("Container", dict(dec, width=W, height=H), kids)
        else:
            return el(tag, pa, kids)
    else:
        inner = el("Container", dict(dec, width=W, height=H))
    return el(tag, pa, [inner])


def line(x0: float, y0: float, x1: float, y1: float, color: str, w: float = 1,
         dashed: bool = False) -> str:
    """Axis-aligned line. Only horizontal/vertical are supported by this helper."""
    if abs(y1 - y0) < 0.01:
        return box(x0, y0 - w / 2.0, abs(x1 - x0), w, color=color)
    return box(x0, y0, w, abs(y1 - y0), color=color)


def hline(x0: float, x1: float, y: float, color: str, w: float = 1) -> str:
    return box(min(x0, x1), y - w / 2.0, abs(x1 - x0), w, color=color)


def vline(x: float, y0: float, y1: float, color: str, w: float = 1) -> str:
    return box(x - w / 2.0, min(y0, y1), w, abs(y1 - y0), color=color)


def dashed(x0: float, x1: float, y: float, color: str, w: float = 1,
           dash: float = 7, gap: float = 5) -> str:
    """Horizontal dashed rule built from explicit segments (no CSS dash support)."""
    out = []
    x = min(x0, x1)
    end = max(x0, x1)
    while x < end:
        seg = min(dash, end - x)
        out.append(box(x, y - w / 2.0, seg, w, color=color))
        x += dash + gap
    return "\n".join(out)


def polygon(points, color: str, opacity: float = 1.0) -> str:
    """Filled polygon via Opacity+Transform is not available in the parser for
    arbitrary paths, so polygons are emitted as a Stack of thin scanline boxes.
    Only used for small, axis-friendly shapes (triangles, area fills)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ymin, ymax = min(ys), max(ys)
    rows = []
    steps = 72
    for i in range(steps):
        y = ymin + (ymax - ymin) * (i + 0.5) / steps
        xs_at = _scan_xs(points, y)
        if xs_at is None:
            continue
        rows.append(box(xs_at[0], y - (ymax - ymin) / steps / 2.0,
                        xs_at[1] - xs_at[0], (ymax - ymin) / steps + 0.6,
                        color=color))
    if not rows:
        return ""
    return "\n".join(rows)


def _scan_xs(points, y):
    xs = []
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            t = (y - y1) / (y2 - y1)
            xs.append(x1 + t * (x2 - x1))
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def stack(children, w: float | None = None, h: float | None = None,
          tag: str = "Container", extra: dict | None = None) -> str:
    a = dict(extra or {})
    if w is not None:
        a["width"] = round(w, 2)
    if h is not None:
        a["height"] = round(h, 2)
    inner = el("Stack", {"fit": "EXPAND"}, children)
    return el(tag, a, [inner])


def card(x, y, w, h, fill="#FFFFFFFF", radius=16, border="1 SOLID #E2E8F0FF",
         shadow="0 2 10 0 #0F172A0F", children=None, extra=None) -> str:
    return box(x, y, w, h, color=fill, radius=radius, border=border,
               shadow=shadow, children=children, extra=extra)


def fmt_int(v) -> str:
    return "{:,.0f}".format(v)


def fmt_money(v) -> str:
    return "{:,.0f}".format(v)


def fmt_wan(v) -> str:
    return "{:.2f}".format(v / 10000.0)


def pct(v, nd=2) -> str:
    return ("%." + str(nd) + "f%%") % (v * 100.0)


def snapshot(children, w, h, bg="#F1F5F9FF", type_="png") -> str:
    head = '<Snapshot type="%s" background="%s">' % (type_, bg)
    root = el("Container", {"width": w, "height": h}, children)
    return head + "\n" + root + "\n</Snapshot>\n"