"""Shared Snapshot DSL builder helpers.

Import from a per-task generator after putting this file's directory on sys.path:

    import sys, os
    from pathlib import Path
    root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    rid = os.environ["SNAPSHOT_RUN_ID"]
    sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
    from dslkit import Doc

All coordinates are canvas-absolute; `doc.origin(x, y)` returns a small object whose
pos/rect/label methods add that offset, so chart internals can be written relative
to their own card without the coordinate-base bug seen in A01.
"""
import math


def n(v):
    return f"{round(float(v), 2):g}"


def esc(s):
    s = str(s)
    # parser does no entity decoding: '<'/'>' inside Text need CDATA (docs/parser)
    return f"<![CDATA[{s}]]>" if ("<" in s or ">" in s) else s


class TextFit:
    """Pre-render text-fit gate. Snapshot clips text to its box with no ellipsis,
    so a box that is too small silently loses glyphs. Measure before emitting DSL.

    Advance widths are calibrated against A04/A05/A06 pixel measurements; `SLACK`
    exists because the estimate matched the renderer almost exactly but a box sized
    to the estimate still clipped (A06 v02 legend).
    """

    SLACK = 0.96
    PITCH = 1.45          # line pitch ~= fontSize x 1.45

    def __init__(self):
        self.problems = []
        self.n = 0

    def w(self, s, size):
        t = 0.0
        for c in s:
            o = ord(c)
            if c == " ":
                t += size * 0.30
            elif c == "\u2212":
                t += size * 0.62
            elif o >= 0x2E80 or 0x2190 <= o <= 0x24FF or 0x25A0 <= o <= 0x25FF \
                    or c in "·＝—°／→×":
                # CJK plus the "ambiguous width" blocks: enclosed digits ①②③,
                # arrows and geometric shapes all render full-width (A07 legend clip).
                t += size * 1.02
            elif c.isdigit() or c.isalpha():
                t += size * 0.58
            else:
                t += size * 0.50
        return t

    def wrap(self, s, size, bw):
        out, cur, cur_w = [], "", 0.0
        for c in s:
            cw = self.w(c, size)
            if cur and cur_w + cw > bw:
                out.append(cur)
                cur, cur_w = c, cw
            else:
                cur += c
                cur_w += cw
        return out + [cur]

    def lines(self, s, size, bw):
        return len(self.wrap(s, size, bw * self.SLACK))

    def need(self, s, size, bw):
        nl = self.lines(s, size, bw)
        return nl, size + (nl - 1) * self.PITCH * size

    def check(self, tag, s, size, bw, bh, lines=1):
        self.n += 1
        nl, need_h = self.need(s, size, bw)
        if need_h > bh or nl > lines + 1:
            self.problems.append(
                f"{tag}: {s[:26]} {nl}line est "
                f"{self.w(s, size):.0f}x{need_h:.0f} > box {bw:.0f}x{bh}")


class Origin:
    def __init__(self, doc, dx, dy):
        self.doc = doc
        self.dx = dx
        self.dy = dy

    def pos(self, x, y, w, h, inner):
        self.doc.pos(self.dx + x, self.dy + y, w, h, inner)

    def rect(self, x, y, w, h, color, radius=None):
        self.doc.rect(self.dx + x, self.dy + y, w, h, color, radius)

    def label(self, x, y, w, h, s, *a, **kw):
        self.doc.label(self.dx + x, self.dy + y, w, h, s, *a, **kw)

    def chip(self, x, y, w, h, s, color, bg, size=18, radius=None):
        self.doc.chip(self.dx + x, self.dy + y, w, h, s, color, bg, size, radius)

    def dot(self, x, y, d_, color):
        self.doc.dot(self.dx + x, self.dy + y, d_, color)

    def line(self, x1, y1, x2, y2, thickness, color, radius=None):
        self.doc.line(self.dx + x1, self.dy + y1, self.dx + x2, self.dy + y2,
                      thickness, color, radius)


class Doc:
    def __init__(self, w, h, bg="#060B18", font="Inter,Noto Sans CJK SC",
                 palette=None):
        self.W, self.H = w, h
        self.bg = bg
        self.font = font
        self.parts = []
        self.P = {
            "card": "#121E38", "card2": "#0E1830", "border": "#1E2E4F",
            "grid": "#1E2E4F", "axis": "#3A4C70", "row": "#0F1A31",
            "t0": "#F1F5F9", "t1": "#A9B8D0", "t2": "#7A8AA6",
            "cyan": "#38BDF8", "amber": "#FBBF24", "green": "#34D399",
            "red": "#F87171", "violet": "#A78BFA", "teal": "#2DD4BF",
            "pink": "#F472B6", "blue": "#60A5FA", "lime": "#A3E635",
            "orange": "#FB923C", "slate": "#94A3B8",
        }
        if palette:
            self.P.update(palette)

    # ---------- primitives ----------
    def text(self, s, color=None, size=20, style=None, align=None, maxlines=None,
             height=None, spacing=None, bg=None, shadow=None, decoration=None,
             features=None):
        color = color or self.P["t0"]
        a = f'color="{color}" fontSize="{size}" fontFamily="{self.font}"'
        if style:
            a += f' fontStyle="{style}"'
        if align:
            a += f' textAlign="{align}"'
        if maxlines:
            a += f' maxLines="{maxlines}"'
        if height:
            a += f' height="{height}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        if bg:
            a += f' backgroundColor="{bg}"'
        if shadow:
            a += f' textShadow="{shadow}"'
        if decoration:
            a += f' decoration="{decoration}"'
        if features:
            a += f' fontFeatures="{features}"'
        return f"<Text {a}>{esc(s)}</Text>"

    def box(self, w=None, h=None, color=None, radius=None, border=None, align=None,
            pad=None, inner=None, shadow=None, grad=None, margin=None, clip=None,
            minw=None, maxw=None, minh=None, maxh=None):
        a = ""
        if w is not None:
            a += f' width="{n(w)}"'
        if h is not None:
            a += f' height="{n(h)}"'
        if minw is not None:
            a += f' minWidth="{n(minw)}"'
        if maxw is not None:
            a += f' maxWidth="{n(maxw)}"'
        if minh is not None:
            a += f' minHeight="{n(minh)}"'
        if maxh is not None:
            a += f' maxHeight="{n(maxh)}"'
        if color:
            a += f' color="{color}"'
        if grad:
            a += f' {grad}'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        if align:
            a += f' alignment="{align}"'
        if pad:
            a += f' padding="{pad}"'
        if margin:
            a += f' margin="{margin}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        if clip:
            a += f' clipBehavior="{clip}"'
        a = a.strip()
        return f"<Container {a}>{inner}</Container>" if inner else f"<Container {a}/>"

    def spacer(self, w, h):
        return self.box(w, h)

    def card(self, w, h, inner=None, pad=None, align=None, color=None, radius=14,
             border=None, shadow=None):
        return self.box(w, h, color=color or self.P["card"], radius=radius,
                        border=border or f"1 SOLID {self.P['border']}",
                        inner=inner, pad=pad, align=align, shadow=shadow)

    def col(self, children, align="START", main="START"):
        return (f'<Column crossAxisAlignment="{align}" mainAxisAlignment="{main}">'
                + "".join(children) + "</Column>")

    def row(self, children, align="CENTER", main="START"):
        return (f'<Row crossAxisAlignment="{align}" mainAxisAlignment="{main}">'
                + "".join(children) + "</Row>")

    def exp(self, inner, flex=1):
        return f'<Expanded flex="{flex}">{inner}</Expanded>'

    # ---------- placement ----------
    def pos(self, x, y, w, h, inner):
        self.parts.append(f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
                          f'height="{n(h)}">{inner}</Positioned>')

    def rect(self, x, y, w, h, color, radius=None):
        self.pos(x, y, w, h, self.box(w, h, color=color, radius=radius))

    def label(self, x, y, w, h, s, color=None, size=20, style=None, align="START",
              valign="MIDDLE", **kw):
        ta = None if align == "START" else align
        va = {"START": "LEFT", "END": "RIGHT", "CENTER": "CENTER"}[align]
        vpos = {"TOP": "TOP", "MIDDLE": "CENTER", "BOTTOM": "BOTTOM"}[valign]
        if vpos == "TOP":
            va = "TOP_" + va if va != "CENTER" else "TOP_CENTER"
        elif vpos == "BOTTOM":
            va = "BOTTOM_" + va if va != "CENTER" else "BOTTOM_CENTER"
        elif va == "LEFT":
            va = "CENTER_LEFT"
        elif va == "RIGHT":
            va = "CENTER_RIGHT"
        self.pos(x, y, w, h, self.box(w, h, inner=self.text(s, color, size, style,
                                                            **kw), align=va))

    def origin(self, x, y):
        return Origin(self, x, y)

    # ---------- geometry helpers ----------
    def line(self, x1, y1, x2, y2, thickness, color, radius=None):
        """rotated rect segment; alignment must be explicit TOP_LEFT (A05 probe)"""
        ln = math.hypot(x2 - x1, y2 - y1)
        if ln == 0:
            return
        co, si = (x2 - x1) / ln, (y2 - y1) / ln
        seg = (f'<Transform matrix="({co:.6f},{si:.6f},0,0,{-si:.6f},{co:.6f},0,0,'
               f'0,0,1,0,0,0,0,1)" alignment="TOP_LEFT">'
               + self.box(ln, thickness, color=color, radius=radius) + "</Transform>")
        self.pos(x1, y1 - thickness / 2, ln, thickness, seg)

    def dot(self, x, y, d, color):
        self.pos(x - d / 2, y - d / 2, d, d, self.box(d, d, color=color, radius=d / 2))

    def chip(self, x, y, w, h, s, color, bg, size=18, radius=None):
        self.pos(x, y, w, h, self.box(w, h, color=bg, radius=radius if radius is not None else h / 2,
                                      inner=self.text(s, color, size, "BOLD", align="CENTER"),
                                      align="CENTER"))

    # ---------- assembly ----------
    def stack(self, children=None, bg_grad=None):
        body = []
        if bg_grad:
            body.append(f'<Container width="{n(self.W)}" height="{n(self.H)}" {bg_grad}/>')
        body.extend(children if children is not None else self.parts)
        return (f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                + "".join(body) + "</Stack>")

    def dsl(self, bg_grad=None):
        return (f'<Snapshot background="{self.bg}" type="png">'
                f'<Container width="{n(self.W)}" height="{n(self.H)}">'
                + self.stack(bg_grad=bg_grad) + "</Container></Snapshot>")


GRAD_NIGHT = ('gradientType="LINEAR" gradientColors="#060B18,#0C1730,#060B18" '
              'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"')
GRAD_LIGHT = ('gradientType="LINEAR" gradientColors="#F8FAFC,#EEF2F8,#F8FAFC" '
              'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"')


def minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)
