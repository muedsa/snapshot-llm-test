#!/usr/bin/env python3
"""Small helper library for building class-DOM Snapshot DSL documents.

Everything is placed absolutely with Stack + Positioned, so geometry is
explicit and reproducible. No machine-specific paths appear here.
"""
from __future__ import annotations
import html
import math

CN = "Noto Sans CJK SC"
LATIN = "Inter"
MONO = "Noto Sans Mono CJK SC"


def cdata(s: str) -> str:
    """Wrap text as CDATA; parser does not decode entities."""
    s = str(s)
    return "<![CDATA[" + s.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def attr(v: str) -> str:
    """Escape a value for use inside a double-quoted attribute."""
    return str(v).replace("&", "&amp;").replace('"', "&quot;")


class Canvas:
    def __init__(self, w: int, h: int, bg: str = "#FFFFFF", font: str = CN):
        self.w, self.h, self.bg, self.font = w, h, bg, font
        self.items: list[str] = []
        self._base = f'<Container width="{w}" height="{h}" />'

    # ---- low level -------------------------------------------------
    def add(self, left, top, width, height, inner: str):
        self.items.append(
            f'<Positioned left="{round(left,2)}" top="{round(top,2)}" '
            f'width="{round(width,2)}" height="{round(height,2)}">{inner}</Positioned>'
        )
        return self

    def raw(self, s: str):
        self.items.append(s)
        return self

    # ---- primitives ------------------------------------------------
    def rect(self, x, y, w, h, color, radius=0, border=None, shadow=None, opacity=None):
        a = [f'color="{color}"']
        if radius:
            a.append(f'borderRadius="{radius}"')
        if border:
            a.append(f'border="{attr(border)}"')
        if shadow:
            a.append(f'boxShadow="{attr(shadow)}"')
        inner = f'<Container {" ".join(a)} />'
        if opacity is not None:
            inner = f'<Opacity opacity="{opacity}">{inner}</Opacity>'
        return self.add(x, y, w, h, inner)

    def gradient(self, x, y, w, h, colors, radius=0, begin="TOP_LEFT", end="BOTTOM_RIGHT",
                 stops=None, border=None):
        a = ['gradientType="LINEAR"', f'gradientColors="{",".join(colors)}"',
             f'gradientBegin="{begin}"', f'gradientEnd="{end}"']
        if stops:
            a.append(f'gradientStops="{",".join(str(v) for v in stops)}"')
        if radius:
            a.append(f'borderRadius="{radius}"')
        if border:
            a.append(f'border="{attr(border)}"')
        return self.add(x, y, w, h, f'<Container {" ".join(a)} />')

    def circle(self, cx, cy, r, color, border=None, opacity=None):
        return self.rect(cx - r, cy - r, 2 * r, 2 * r, color, radius=r,
                         border=border, opacity=opacity)

    def ellipse(self, x, y, w, h, color, border=None):
        a = [f'color="{color}"', f'borderRadius="{min(w,h)/2}"']
        if border:
            a.append(f'border="{attr(border)}"')
        return self.add(x, y, w, h, f'<Container {" ".join(a)} />')

    def hline(self, x, y, w, thickness, color):
        return self.rect(x, y, w, thickness, color)

    def vline(self, x, y, h, thickness, color):
        return self.rect(x, y, thickness, h, color)

    def line(self, x1, y1, x2, y2, width, color, opacity=None):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * width / 2, dx / L * width / 2
        pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
               (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
        return self.poly(pts, color, opacity=opacity)

    def arrow_head(self, x, y, angle_deg, size, color, opacity=None):
        a = math.radians(angle_deg)
        p1 = (x, y)
        p2 = (x - size * math.cos(a - 0.42), y - size * math.sin(a - 0.42))
        p3 = (x - size * math.cos(a + 0.42), y - size * math.sin(a + 0.42))
        return self.poly([p1, p2, p3], color, opacity=opacity)

    def poly(self, points, color, opacity=None, extra_path=""):
        pts = " ".join(("M" if i == 0 else "L") + "%.2f %.2f" % (p[0], p[1])
                       for i, p in enumerate(points))
        path = pts + " Z " + extra_path
        inner = (f'<ClipPath path="{attr(path.strip())}" clipBehavior="ANTI_ALIAS">'
                 f'<Container width="{self.w}" height="{self.h}" color="{color}" />'
                 f'</ClipPath>')
        if opacity is not None:
            inner = f'<Opacity opacity="{opacity}">{inner}</Opacity>'
        return self.raw(inner)

    def path(self, d: str, color: str, opacity=None, viewbox=None, fit="FILL", fill_rule="NON_ZERO"):
        a = [f'path="{attr(d)}"', f'clipBehavior="ANTI_ALIAS"', f'fit="{fit}"', f'fillRule="{fill_rule}"']
        if viewbox:
            a.append(f'viewBox="{attr(viewbox)}"')
        inner = (f'<ClipPath {" ".join(a)}>'
                 f'<Container width="{self.w}" height="{self.h}" color="{color}" />'
                 f'</ClipPath>')
        if opacity is not None:
            inner = f'<Opacity opacity="{opacity}">{inner}</Opacity>'
        return self.raw(inner)

    def dashed_hline(self, x, y, w, thickness, color, dash=10, gap=7):
        p = x
        while p < x + w:
            self.rect(p, y, min(dash, x + w - p), thickness, color)
            p += dash + gap
        return self

    def dashed_vline(self, x, y, h, thickness, color, dash=10, gap=7):
        p = y
        while p < y + h:
            self.rect(x, p, thickness, min(dash, y + h - p), color)
            p += dash + gap
        return self

    def dashed_line(self, x1, y1, x2, y2, width, color, dash=10, gap=7):
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 1e-6:
            return self
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        p = 0.0
        while p < L:
            q = min(p + dash, L)
            self.line(x1 + ux * p, y1 + uy * p, x1 + ux * q, y1 + uy * q, width, color)
            p += dash + gap
        return self

    # ---- text ------------------------------------------------------
    def text(self, x, y, w, h, s, size=20, color="#111827", bold=False,
             align="LEFT", font=None, italic=False, opacity=None,
             spacing=None, max_lines=None):
        va = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}.get(align, "CENTER_LEFT")
        ta = {"LEFT": "LEFT", "CENTER": "CENTER", "RIGHT": "RIGHT"}.get(align, "LEFT")
        a = [f'fontFamily="{font or self.font}"', f'fontSize="{size}"', f'color="{color}"',
             f'textAlign="{ta}"', 'softWrap="true"']
        if bold or italic:
            a.append('fontStyle="%s"' % ("BOLD_ITALIC" if bold and italic else "BOLD" if bold else "ITALIC"))
        if spacing is not None:
            a.append(f'letterSpacing="{spacing}"')
        if max_lines:
            a.append(f'maxLines="{max_lines}" overflow="ELLIPSIS"')
        inner = (f'<Container width="{round(w,2)}" height="{round(h,2)}" alignment="{va}">'
                 f'<Text {" ".join(a)}>{cdata(s)}</Text></Container>')
        if opacity is not None:
            inner = f'<Opacity opacity="{opacity}">{inner}</Opacity>'
        return self.add(x, y, w, h, inner)

    def text_top(self, x, y, w, h, s, size=20, color="#111827", bold=False,
                 align="LEFT", font=None, italic=False, spacing=None, max_lines=None):
        va = {"LEFT": "TOP_LEFT", "CENTER": "TOP_CENTER", "RIGHT": "TOP_RIGHT"}.get(align, "TOP_LEFT")
        ta = {"LEFT": "LEFT", "CENTER": "CENTER", "RIGHT": "RIGHT"}.get(align, "LEFT")
        a = [f'fontFamily="{font or self.font}"', f'fontSize="{size}"', f'color="{color}"',
             f'textAlign="{ta}"']
        if bold or italic:
            a.append('fontStyle="%s"' % ("BOLD" if bold else "ITALIC"))
        if spacing is not None:
            a.append(f'letterSpacing="{spacing}"')
        if max_lines:
            a.append(f'maxLines="{max_lines}" overflow="ELLIPSIS"')
        inner = (f'<Container width="{round(w,2)}" height="{round(h,2)}" alignment="{va}">'
                 f'<Text {" ".join(a)}>{cdata(s)}</Text></Container>')
        return self.add(x, y, w, h, inner)

    def rich(self, x, y, w, h, spans, size=20, color="#111827", align="LEFT",
             font=None, bold=False):
        """spans: list of (text, color_or_None, bold_or_None)."""
        va = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}.get(align, "CENTER_LEFT")
        ta = {"LEFT": "LEFT", "CENTER": "CENTER", "RIGHT": "RIGHT"}.get(align, "LEFT")
        a = [f'fontFamily="{font or self.font}"', f'fontSize="{size}"', f'color="{color}"',
             f'textAlign="{ta}"']
        if bold:
            a.append('fontStyle="BOLD"')
        body = ""
        for s, c, b in spans:
            aa = []
            if c:
                aa.append(f'color="{c}"')
            if b:
                aa.append('fontStyle="BOLD"')
            body += f'<Text {" ".join(aa)}>{cdata(s)}</Text>'
        inner = (f'<Container width="{round(w,2)}" height="{round(h,2)}" alignment="{va}">'
                 f'<Text {" ".join(a)}>{body}</Text></Container>')
        return self.add(x, y, w, h, inner)

    # ---- chart helper ---------------------------------------------
    def bar(self, x, y, w, h, color, radius=0, border=None):
        return self.rect(x, y, w, max(h, 0.5), color, radius=radius, border=border)

    def render(self, pretty=True):
        body = "\n".join(self.items) if pretty else "".join(self.items)
        return (f'<Snapshot background="{self.bg}" type="png">\n'
                f'<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">\n'
                f'{self._base}\n{body}\n</Stack>\n</Snapshot>\n')
