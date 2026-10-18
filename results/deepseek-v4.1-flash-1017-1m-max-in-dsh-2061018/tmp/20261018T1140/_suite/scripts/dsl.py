"""Small DSL construction library for the Snapshot task suite.

The library only emits the documented class-DOM syntax (see
tmp/<run_id>/_suite/docs/reference__parser-tags.md). It never talks to the
service itself; snapshot_client.py does the HTTP part.

Coordinates are pixels. Functions return strings; compose freely.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


# ---------------------------------------------------------------- primitives
def _attr_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return f"{v:.3f}".rstrip("0").rstrip(".")
    return str(v)


def attrs(**kw) -> str:
    out = []
    for k, v in kw.items():
        if v is None:
            continue
        key = k.rstrip("_").replace("__", "-")
        out.append(f'{key}="{_attr_value(v)}"')
    return (" " + " ".join(out)) if out else ""


def _clean_text(s: str) -> str:
    # The parser does not decode entities; avoid characters that would break tags.
    return (str(s).replace("&", "＆").replace("<", "‹").replace(">", "›"))


def el(tag: str, children: str | Sequence[str] | None = None, **kw) -> str:
    a = attrs(**kw)
    if children is None or children == "" or children == []:
        return f"<{tag}{a} />"
    if isinstance(children, (list, tuple)):
        children = "".join(children)
    return f"<{tag}{a}>{children}</{tag}>"


def T(text, size=14, color="#E2E8F0", weight=None, family="Inter,Noto Sans CJK SC",
      height=None, align=None, max_lines=None, overflow=None, spacing=None, **kw) -> str:
    style = {"fontSize": size, "color": color}
    if weight:
        style["fontStyle"] = weight
    if family:
        style["fontFamily"] = family
    if height is not None:
        style["height"] = height
    if align:
        style["textAlign"] = align
    if max_lines is not None:
        style["maxLines"] = max_lines
    if overflow:
        style["overflow"] = overflow
    if spacing is not None:
        style["letterSpacing"] = spacing
    style.update(kw)
    return el("Text", _clean_text(text), **style)


def Raw(text, **kw) -> str:
    return el("Raw", _clean_text(text), **kw)


def C(child: str = "", **kw) -> str:
    return el("Container", child, **kw)


def Col(children: Sequence[str], **kw) -> str:
    return el("Column", list(children), **kw)


def Row(children: Sequence[str], **kw) -> str:
    return el("Row", list(children), **kw)


def Stack(children: Sequence[str], **kw) -> str:
    return el("Stack", list(children), **kw)


def Pos(x=None, y=None, child: str = "", w=None, h=None, right=None, bottom=None) -> str:
    kw = {"left": x, "top": y, "width": w, "height": h, "right": right, "bottom": bottom}
    return el("Positioned", child, **kw)


def Box(w, h, color=None, child: str = "", **kw) -> str:
    if color is not None:
        kw["color"] = color
    return C(child=child, width=w, height=h, **kw)


def SizedBox(w=None, h=None) -> str:
    return el("SizedBox", width=w, height=h)


def Gap(h: int) -> str:
    return SizedBox(h=h)


def HGap(w: int) -> str:
    return SizedBox(w=w)


def Border_box(w, h, child="", color="#111A30", radius=14, border=None, **kw) -> str:
    args = {"width": w, "height": h, "color": color, "borderRadius": radius}
    if border:
        args["border"] = border
    args.update(kw)
    return C(child=child, **args)


def Circle(d, color, child="", **kw) -> str:
    return C(child=child, width=d, height=d, color=color, borderRadius=d / 2, **kw)


def Label(text, w, h, align="CENTER_LEFT", size=10, color="#7C8BA5",
          family="Inter,Noto Sans CJK SC", weight=None, **kw) -> str:
    """Fixed-size label box; alignment works because Align fills the box."""
    t = T(text, size=size, color=color, family=family, weight=weight, **kw)
    return C(width=w, height=h, child=el("Align", t, alignment=align))


# ------------------------------------------------------------------- charts
def nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    """Simple tick generator that keeps zero visible when the range includes it."""
    if lo == hi:
        hi = lo + 1
    span = hi - lo
    raw = span / max(count - 1, 1)
    mag = 10 ** __import__("math").floor(__import__("math").log10(raw))
    for mult in (1, 2, 2.5, 5, 10):
        step = mag * mult
        if step >= raw:
            break
    start = __import__("math").floor(lo / step) * step
    ticks = []
    v = start
    while v <= hi + step * 0.001:
        ticks.append(round(v, 6))
        v += step
    return ticks


def poly_path(points: Sequence[tuple[float, float]], close: bool = True) -> str:
    if not points:
        return ""
    parts = [f"M{points[0][0]:.2f} {points[0][1]:.2f}"]
    for x, y in points[1:]:
        parts.append(f"L{x:.2f} {y:.2f}")
    if close:
        parts.append("Z")
    return " ".join(parts)


def polygon(w: float, h: float, points: Sequence[tuple[float, float]], color: str,
            opacity: float | None = None, gradient: dict | None = None) -> str:
    """Filled polygon clipped to the exact box. Coordinates are local pixels."""
    inner = C(color=color, **(gradient or {}))
    clip = el("ClipPath", inner, path=poly_path(points), fillRule="NON_ZERO")
    body = el("SizedBox", clip, width=w, height=h)
    if opacity is not None:
        body = el("Opacity", body, opacity=opacity)
    return body


def line_ribbon(points: Sequence[tuple[float, float]], width: float = 2.0) -> str:
    """Build a closed polygon that traces a polyline with the given thickness."""
    import math
    if len(points) < 2:
        return poly_path(points)
    left, right = [], []
    for i, (x, y) in enumerate(points):
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln * width / 2, dx / ln * width / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return poly_path(left + list(reversed(right)))


def rect_path(x, y, w, h) -> str:
    return f"M{x:.2f} {y:.2f} L{x + w:.2f} {y:.2f} L{x + w:.2f} {y + h:.2f} L{x:.2f} {y + h:.2f} Z"


@dataclass
class Series:
    label: str
    color: str
    values: Sequence[float]


def bar_chart(width, height, categories, series: Sequence[Series], y_min, y_max, ticks,
              plot_left=56, plot_right=14, plot_top=18, plot_bottom=34,
              value_fmt=str, show_values=False, value_size=10, cat_size=10,
              axis_color="#26334D", grid_color="#1A2438", text_color="#7C8BA5",
              value_color=None, bar_gap=6, group_gap=18, radius=3,
              y_label=None, y_unit="", x_label=None, legend=None, legend_pos="top-right",
              zero_line=True, label_fmt=str, bar_max=None, tick_size=10,
              legend_size=10, highlight=None, highlight_color="#12233D") -> str:
    """Grouped bar chart built from positioned containers.

    Returns a fixed-size Stack. All series share one linear scale; bars are
    anchored at the zero baseline (or y_min if the domain excludes zero).
    """
    pw = width - plot_left - plot_right
    ph = height - plot_top - plot_bottom
    lo, hi = y_min, y_max
    span = hi - lo or 1

    def ypx(v):
        return plot_top + ph * (hi - v) / span

    layers = [SizedBox(w=width, h=height)]

    # grid + y labels
    for t in ticks:
        y = ypx(t)
        if lo < t < hi:
            layers.append(Pos(plot_left, y, Box(pw, 1, grid_color)))
        label = y_label(t) if y_label else label_fmt(t)
        layers.append(Pos(0, y - 8, Label(label, plot_left - 8, 16, align="CENTER_RIGHT", size=tick_size, color=text_color, family="Inter")))
    if highlight is not None and 0 <= highlight < len(categories):
        hx = plot_left + pw / len(categories) * highlight
        layers.append(Pos(hx + 2, plot_top, Box(pw / len(categories) - 4, ph, highlight_color, borderRadius=8)))
    axis_x = plot_left
    if zero_line and lo <= 0 <= hi:
        layers.append(Pos(axis_x, ypx(0), Box(1, ph, axis_color)))
    layers.append(Pos(axis_x, plot_top, Box(1, ph, axis_color)))
    layers.append(Pos(axis_x, plot_top + ph, Box(pw, 1, axis_color)))

    n = len(categories)
    group_w = pw / max(n, 1)
    k = len(series)
    bar_w = min(bar_max or 30, (group_w - group_gap - bar_gap * (k - 1)) / k)
    total_w = bar_w * k + bar_gap * (k - 1)
    for gi, cat in enumerate(categories):
        cx = plot_left + group_w * gi + group_w / 2
        start = cx - total_w / 2
        for si, s in enumerate(series):
            v = s.values[gi]
            y0, y1 = ypx(0 if lo <= 0 <= hi else lo), ypx(v)
            top, bottom = min(y0, y1), max(y0, y1)
            h = max(bottom - top, 1.5)
            layers.append(Pos(start + si * (bar_w + bar_gap), top,
                              Box(bar_w, h, s.color, borderRadius=radius)))
            if show_values:
                txt = value_fmt(v)
                layers.append(Pos(start + si * (bar_w + bar_gap) - 6, top - 15,
                                  Label(txt, bar_w + 12, 14, align="CENTER", size=value_size, color=value_color or s.color, family="Inter")))
        lx = min(max(plot_left + group_w * gi, 0), width - group_w)
        layers.append(Pos(lx, plot_top + ph + 8, Label(cat, group_w, 18, align="CENTER", size=cat_size, color=text_color)))
    if y_unit:
        layers.append(Pos(0, plot_top - 16, Box(plot_left + 40, 14, None,
                          T(y_unit, size=9, color=text_color, family="Inter,Noto Sans CJK SC"))))
    if legend is not None:
        legend = legend or [s.label for s in series]
        lx = plot_left
        if legend_pos == "top-right":
            lx = width - plot_right - sum(16 + len(l) * 7 for l in legend) - 12
        for i, lab in enumerate(legend):
            lw = 8
            layers.append(Pos(lx, 2, Box(lw, lw, series[i].color, borderRadius=2)))
            layers.append(Pos(lx + lw + 5, -3, Box(len(lab) * 7 + 10, 18, None,
                              T(lab, size=legend_size, color=text_color, family="Inter,Noto Sans CJK SC"))))
            lx += 18 + len(lab) * 7
    return Stack(layers, width=width, height=height)


def line_chart(width, height, categories, series: Sequence[Series], y_min, y_max, ticks,
               plot_left=46, plot_right=12, plot_top=16, plot_bottom=30,
               axis_color="#26334D", grid_color="#1A2438", text_color="#7C8BA5",
               area=False, area_alpha=0.16, line_width=2.2, dot=True, dot_r=2.6,
               label_fmt=str, y_label=None, y_unit="", legend=None,
               show_last=False, last_fmt=str, smooth=False, tick_size=10) -> str:
    pw = width - plot_left - plot_right
    ph = height - plot_top - plot_bottom
    lo, hi = y_min, y_max
    span = hi - lo or 1

    def ypx(v):
        return plot_top + ph * (hi - v) / span

    layers = [SizedBox(w=width, h=height)]
    for t in ticks:
        y = ypx(t)
        if lo < t < hi:
            layers.append(Pos(plot_left, y, Box(pw, 1, grid_color)))
        label = y_label(t) if y_label else label_fmt(t)
        layers.append(Pos(0, y - 8, Label(label, plot_left - 6, 16, align="CENTER_RIGHT", size=tick_size, color=text_color, family="Inter")))
    layers.append(Pos(plot_left, plot_top, Box(1, ph, axis_color)))
    layers.append(Pos(plot_left, plot_top + ph, Box(pw, 1, axis_color)))

    n = len(categories)
    step = pw / max(n - 1, 1)

    def xpx(i):
        return plot_left + step * i

    for s in series:
        pts = [(xpx(i), ypx(v)) for i, v in enumerate(s.values)]
        if area:
            area_pts = [(pts[0][0], ypx(lo))] + pts + [(pts[-1][0], ypx(lo))]
            layers.append(polygon(width, height, area_pts, s.color, opacity=area_alpha))
        layers.append(polygon(width, height, _ribbon_points(pts, line_width), s.color))
        if dot:
            for i, (x, y) in enumerate(pts):
                layers.append(Pos(x - dot_r, y - dot_r, Box(dot_r * 2, dot_r * 2, s.color, borderRadius=dot_r)))
    for i, cat in enumerate(categories):
        lx = min(max(xpx(i) - step / 2, 0), width - step)
        layers.append(Pos(lx, plot_top + ph + 8, Label(cat, step, 18, align="CENTER", size=10, color=text_color)))
    if show_last and series:
        s = series[0]
        x, y = xpx(len(s.values) - 1), ypx(s.values[-1])
        layers.append(Pos(x - 4, y - 5, Box(8, 8, "#0C1526", borderRadius=4)))
        layers.append(Pos(width - plot_right - 96, y - 24, Label(last_fmt(s.values[-1]), 92, 18,
                          align="CENTER_RIGHT", size=12, color=s.color, family="Inter")))
    if y_unit:
        layers.append(Pos(0, plot_top - 14, Box(plot_left + 40, 13, None,
                          T(y_unit, size=9, color=text_color))))
    return Stack(layers, width=width, height=height)


def _ribbon_points(points, width):
    import math
    if len(points) < 2:
        return points
    left, right = [], []
    for i, (x, y) in enumerate(points):
        if i == 0:
            dx, dy = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            dx, dy = x - points[i - 1][0], y - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln * width / 2, dx / ln * width / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return left + list(reversed(right))
