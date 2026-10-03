"""Shared Snapshot DSL builder for the whole suite.

Every helper here encodes a fact that was established by measurement, so the same mistakes
are not re-introduced per task:

  * borderRadius only accepts a single number; per-corner values need the
    borderRadiusTopLeft / TopRight / BottomLeft / BottomRight attributes.
  * alignments (RE-MEASURED with a Pillow probe on a real response, see
    tmp/<run>/_suite/shared/entity-center-probe.png): CENTER really is the two-axis centre
    of the box, not bottom-centre. Measured ink rows for a 20px label in a 60px box:
    CENTER -> 162..176 inside 140..200 (centred), BOTTOM_CENTER -> 260..275 inside 220..280
    (5px above the bottom). An earlier note in this file claiming CENTER == (0.5,1) was
    wrong; it is corrected here.
  * A Text inside a width-constrained Container WRAPS when it does not fit; give the box
    the real single-line width or the text will reflow into the row below.
  * Transform origin is TOP_LEFT and the matrix is column-major.
  * Only one root child is allowed under <Snapshot>.
  * **The parser does NOT decode XML entities.** A literal "A &amp; B" in the source renders
    on the canvas as the five characters "&amp;". Verified on a real 200 response
    (shared/entity-center-probe.png). So never escape. The documented way to print the
    characters `<`, `&`, `>` themselves is **CDATA**, verified on a real 200 response
    (shared/cdata-probe.png):
        plain text node -> "&" and ">" print verbatim, "<" is a hard 400 TAG_OPEN
        <![CDATA[A < B & C > D]]> -> prints exactly A < B & C > D
        <Text><Raw><![CDATA[...]]></Raw></Text> -> also preserves runs of spaces
    ("Raw" is only legal inside Text, not directly inside Positioned.) text_cdata() below
    picks the right form automatically.
  * **One document is capped at 4096 elements**; the service answers
    400 RENDER_ERROR "Document contains more than 4096 elements". Elements are counted per
    TAG, so <Transform><Container/></Transform> costs 2 and a "line count" badly
    under-counts. element_count() below measures it and finish() refuses to emit a document
    that is over budget, because that request would only be wasted.
  * Advance widths below were re-calibrated by a sibling workstream against a real render
    (A11, two probes): mono is exactly 0.5000 em/char, NOT 0.60. The old 0.60 constant put a
    19px spread across a right-aligned column of amounts; the calibrated table brings it to
    1px. Prefer the measured table.
"""
from __future__ import annotations

import math
import re

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# --- advance widths, in em per character -----------------------------------------------
MONO_ADVANCE = 0.5000    # Noto Sans Mono CJK SC, measured: exactly 0.5 em per char
CJK_ADVANCE = 0.9952     # Noto Sans CJK SC, Han / kana
LATIN_ADVANCE = 0.5641   # legacy fallback for characters not in the measured table
LINE_HEIGHT = 1.30       # px per px of font size

# Noto Sans CJK SC per-class advances, measured.
CJK_ADVANCE_TABLE = {
    "han": 0.9952, "upper": 0.6106, "lower": 0.5769,
    "digit": 0.5385, "space": 0.5641, "period": 0.2692,
}


def _advance(ch: str, size: float, mono: bool) -> float:
    if mono:
        return size * MONO_ADVANCE
    o = ord(ch)
    if o > 0x2E80:                       # Han, kana, full-width forms
        return size * CJK_ADVANCE_TABLE["han"]
    if ch == " ":
        return size * CJK_ADVANCE_TABLE["space"]
    if ch in ".。,":
        return size * CJK_ADVANCE_TABLE["period"]
    if ch.isdigit():
        return size * CJK_ADVANCE_TABLE["digit"]
    if ch.isupper():
        return size * CJK_ADVANCE_TABLE["upper"]
    return size * CJK_ADVANCE_TABLE["lower"]


ELEMENT_CAP = 4096
ELEMENT_BUDGET = 3900    # refuse to render above this; leaves headroom for the root tags

_TAG_RE = re.compile(r"<[A-Za-z]")


def element_count(dsl: str) -> int:
    """Count elements the way the service does: one per tag, self-closing included."""
    return len(_TAG_RE.findall(dsl))


def text_width(s: str, size: float, mono: bool = False) -> float:
    """Approximate rendered width using the measured advances."""
    return sum(_advance(ch, size, mono) for ch in s)


def cdata(s: str) -> str:
    """Wrap in CDATA so the characters < & > print verbatim."""
    return f"<![CDATA[{s}]]>" if any(c in s for c in "<&>") else s


def text_width(s: str, size: float, mono: bool = False) -> float:
    """Approximate rendered width using the measured advances."""
    t = 0.0
    for ch in s:
        if mono:
            t += size * MONO_ADVANCE
        elif ord(ch) > 0x2E80:
            t += size * CJK_ADVANCE
        else:
            t += size * LATIN_ADVANCE
    return t


def fit(s: str, size: float, maxw: float) -> str:
    if text_width(s, size) <= maxw:
        return s
    out = ""
    for ch in s:
        if text_width(out + ch + "…", size) > maxw:
            break
        out += ch
    return out + "…"


class Doc:
    def __init__(self, width: int, height: int, background: str = "transparent",
                 container: bool = True, pad: int | None = None):
        self.w, self.h = width, height
        self.p = [f'<Snapshot background="{background}" type="png">']
        if container:
            pad_attr = f' padding="{pad}"' if pad else ""
            self.p.append(f'<Container width="{width}" height="{height}"{pad_attr}>')
            self.p.append('<Stack alignment="TOP_LEFT" fit="EXPAND">')
        self._container = container

    # ---------------------------------------------------------------- primitives
    def raw(self, s: str) -> "Doc":
        self.p.append(s)
        return self

    def box(self, x, y, w, h, color, radius=None, border=None, shadow=None,
            tl=None, tr=None, bl=None, br=None) -> "Doc":
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        if radius is not None:
            if isinstance(radius, (int, float)):
                a += f' borderRadius="{radius}"'
            else:
                side, val = radius
                if side == "top":
                    a += f' borderRadiusTopLeft="{val}" borderRadiusTopRight="{val}"'
                elif side == "bottom":
                    a += f' borderRadiusBottomLeft="{val}" borderRadiusBottomRight="{val}"'
                elif side == "left":
                    a += f' borderRadiusTopLeft="{val}" borderRadiusBottomLeft="{val}"'
                elif side == "right":
                    a += f' borderRadiusTopRight="{val}" borderRadiusBottomRight="{val}"'
                else:
                    a += (f' borderRadiusTopLeft="{val}" borderRadiusBottomLeft="{val}" '
                          f'borderRadiusTopRight="{val}" borderRadiusBottomRight="{val}"')
        for n, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
            if v:
                a += f' borderRadius{n}="{v}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def left_bar(self, x, y, w, h, color, radius=0) -> "Doc":
        """Vertical accent bar with rounded left corners only."""
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        if radius:
            a += f' borderRadiusTopLeft="{radius}" borderRadiusBottomLeft="{radius}"'
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, w=None,
             align="CENTER_LEFT", spacing=None, escape=False, raw=False) -> "Doc":
        """Draw one line of text.

        escape defaults to FALSE because the parser does not decode entities: escaping an
        ampersand would paint the literal characters "&amp;".
          * raw=False (default): a plain text node. "&" and ">" print verbatim; a bare "<"
            is a hard 400, so it is wrapped in CDATA automatically.
          * raw=True: wraps the payload in <Raw><![CDATA[...]]></Raw>, which additionally
            preserves runs of spaces. Use it for code listings and columns that rely on
            literal multiple spaces.
        """
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        if escape:
            body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        elif raw:
            body = f"<Raw><![CDATA[{s}]]></Raw>"
        else:
            body = cdata(s)
        if w:
            self.p.append(f'<Positioned left="{x}" top="{y}" width="{w}">'
                          f'<Container alignment="{align}"><Text {a}>{body}</Text>'
                          f'</Container></Positioned>')
        else:
            self.p.append(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')
        return self

    def seg(self, x0, y0, x1, y1, color, th) -> "Doc":
        """Rotated bar whose centre is the midpoint of the two points.

        The 4x4 matrix is column-major, so the 2x2 rotation lives in positions 1-4
        (m00, m01, m10, m11) and the translation in positions 13-14. A pure translation
        matrix (1,0,0,0,0,1,...) does NOT rotate -- measured with tmp/.../A18/t-seg.png.
        """
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        m11, m12 = math.cos(ang), math.sin(ang)
        m21, m22 = -m12, m11
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        tx = mx - m11 * (length / 2) - m21 * (th / 2)
        ty = my - m12 * (length / 2) - m22 * (th / 2)
        mat = (f"({m11:.6f},{m12:.6f},0,0,{m21:.6f},{m22:.6f},0,0,0,0,1,0,"
               f"{tx:.3f},{ty:.3f},0,1)")
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'<Container width="{length:.2f}" height="{th}" color="{color}" '
                      f'borderRadius="{th/2}"/></Transform></Positioned>')
        return self

    def rotated(self, x, y, w, h, color, degrees, radius=None, border=None,
                inner: str = "") -> "Doc":
        """Box rotated about its own centre by `degrees` counter-clockwise."""
        ang = math.radians(degrees)
        m11, m12 = math.cos(ang), -math.sin(ang)
        m21, m22 = -m12, m11
        # local top-left so the rotated box's centre lands on (x + w/2, y + h/2)
        cx, cy = x + w / 2, y + h / 2
        tx = cx - m11 * (w / 2) - m21 * (h / 2)
        ty = cy - m12 * (w / 2) - m22 * (h / 2)
        mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        if radius:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        body = f'<Container alignment="CENTER">{inner}</Container>' if inner else ""
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">{a}>'
                      f'{body}</Container></Transform></Positioned>')
        return self

    def backdrop(self, x, y, inner: str, sigma=1) -> "Doc":
        """BackdropFilter wrapper. NOTE: in this service build the filter softens the whole
        canvas composited so far, with reach proportional to sigma, so keep sigma small
        (<=1) whenever any other text must stay sharp."""
        self.p.append(f'<Positioned left="{x}" top="{y}">'
                      f'<BackdropFilter sigmaX="{sigma}" sigmaY="{sigma}">'
                      f'<Stack alignment="TOP_LEFT">{inner}</Stack>'
                      f'</BackdropFilter></Positioned>')
        return self

    # ---------------------------------------------------------------- output
    def stats(self) -> dict:
        dsl = "\n".join(self.p)
        n = element_count(dsl)
        return {"elements": n, "cap": ELEMENT_CAP, "budget": ELEMENT_BUDGET,
                "over_budget": n > ELEMENT_BUDGET, "chars": len(dsl)}

    def finish(self, allow_over_budget: bool = False) -> str:
        if self._container:
            self.p += ['</Stack>', '</Container>']
        self.p.append('</Snapshot>')
        dsl = "\n".join(self.p) + "\n"
        n = element_count(dsl)
        if n > ELEMENT_BUDGET and not allow_over_budget:
            raise SystemExit(
                f"document has {n} elements, over the {ELEMENT_BUDGET} budget "
                f"(service cap {ELEMENT_CAP}); simplify the drawing or pass "
                f"allow_over_budget=True if you really mean to try")
        return dsl
