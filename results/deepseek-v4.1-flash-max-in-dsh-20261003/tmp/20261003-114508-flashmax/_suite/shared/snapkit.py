"""Snapshot DSL emitter + colour/contrast math shared by the A21-A24 generators.

Facts encoded here were measured against the live open-snapshot service:
  * the root <Snapshot> takes an optional background colour; "transparent" really does
    produce RGBA output with alpha=0 outside the drawn geometry (probe-alpha, A23);
  * <Transform matrix> is a column-major 4x4; rotation goes in the first four slots
    (m00 m01 m10 m11) and the translation in slots 13/14, and the transform origin is
    the document top-left, so a rotated child must be pre-translated to the point where
    its local top-left has to land;
  * borderRadius takes one number, per-corner values use borderRadiusTopLeft etc.;
  * a <Text> inside a width-constrained <Container> wraps, so every box that holds a
    single line is given a computed width.
"""
from __future__ import annotations

import math
import re


# --------------------------------------------------------------------------- colour
def parse_color(c: str) -> tuple:
    """#RGB / #RGBA / #RRGGBB / #RRGGBBAA -> (r, g, b, a) with a in 0..1."""
    s = c.lstrip("#")
    if len(s) == 3:
        r, g, b = (int(ch * 2, 16) for ch in s)
        return (r, g, b, 1.0)
    if len(s) == 4:
        r, g, b, a = (int(ch * 2, 16) for ch in s)
        return (r, g, b, a / 255)
    if len(s) == 6:
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 1.0)
    if len(s) == 8:
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), int(s[6:8], 16) / 255)
    raise ValueError(f"unsupported colour {c!r}")


def composite(top: str, bottom: str) -> tuple:
    """Source-over composite of two CSS colours -> opaque (r, g, b, 1.0)."""
    tr, tg, tb, ta = parse_color(top)
    br, bg, bb, ba = parse_color(bottom)
    a = ta + ba * (1 - ta)
    if a == 0:
        return (0, 0, 0, 0.0)
    return ((tr * ta + br * ba * (1 - ta)) / a,
            (tg * ta + bg * ba * (1 - ta)) / a,
            (tb * ta + bb * ba * (1 - ta)) / a,
            a)


def _lin(v: float) -> float:
    v = v / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = rgb[0], rgb[1], rgb[2]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(fg: str, bg: str) -> float:
    """WCAG 2.x contrast ratio of an opaque text colour over a (possibly layered) bg."""
    f = composite(fg, bg) if parse_color(fg)[3] < 1 else parse_color(fg)
    b = composite(bg, "#FFFFFFFF") if parse_color(bg)[3] < 1 else parse_color(bg)
    l1, l2 = luminance(f), luminance(b)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ----------------------------------------------------------------------------- text
CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
LINE_HEIGHT = 1.30

# Calibrated advances against a real render (measured by a sibling workstream):
#   Noto Sans Mono CJK SC : exactly 0.5000 em per character
#   Noto Sans CJK SC      : Han 0.9952, uppercase 0.6106, lowercase 0.5769,
#                           digit 0.5385, space 0.5641, period 0.2692
MONO_ADVANCE = 0.50
HAN_ADVANCE = 0.9952
UPPER_ADVANCE = 0.6106
LOWER_ADVANCE = 0.5769
DIGIT_ADVANCE = 0.5385
SPACE_ADVANCE = 0.5641
PERIOD_ADVANCE = 0.2692
# glyphs that advance wider than a plain Han ideograph (full-width middle dot etc.)
WIDE_PUNCT = "·・•　"
WIDE_PUNCT_ADVANCE = 1.08


def _latin_advance(ch: str) -> float:
    if ch.isdigit():
        return DIGIT_ADVANCE
    if "A" <= ch <= "Z":
        return UPPER_ADVANCE
    if "a" <= ch <= "z":
        return LOWER_ADVANCE
    if ch == " ":
        return SPACE_ADVANCE
    if ch in ".":
        return PERIOD_ADVANCE
    return UPPER_ADVANCE


def text_width(s: str, size: float, mono: bool = False) -> float:
    """Calibrated advance width of one line, in canvas pixels."""
    tot = 0.0
    for ch in s:
        if mono:
            tot += size * MONO_ADVANCE
        elif ord(ch) > 0x2E80:
            tot += size * (WIDE_PUNCT_ADVANCE if ch in WIDE_PUNCT else HAN_ADVANCE)
        else:
            tot += size * _latin_advance(ch)
    return tot


def assert_fits(s: str, size: float, maxw: float, tag: str, mono: bool = False) -> float:
    w = text_width(s, size, mono)
    if w > maxw:
        raise AssertionError(f"{tag}: {w:.1f}px > {maxw:.1f}px at {size}px :: {s!r}")
    return w


def esc(s: str, force_cdata: bool = False) -> str:
    """Wrap a text payload in CDATA only when the parser would mis-read it.

    Measured on the live service by the parent agent (cdata-probe.png, 200 OK):
      * in a plain text node `&` and `>` print verbatim;
      * a bare `<` is a hard 400 TAG_OPEN, but `<![CDATA[ A < B & C > D ]]>` prints
        exactly `A < B & C > D`;
      * entities are NOT decoded, so `&amp;` would paint the five literal characters.
    """
    if force_cdata or any(c in s for c in "<&>"):
        return f"<![CDATA[{s}]]>"
    return s


def scan_specials(s: str) -> list:
    """Offsets of raw & < > in a string."""
    return [m.start() for m in re.finditer(r"[&<>]", s)]


def text_nodes(dsl: str) -> list:
    """Text-node payloads of a document (markup angle brackets are not text)."""
    return re.findall(r">([^<]*)<", dsl)


def raw_text_nodes(dsl: str) -> list:
    """Text nodes that contain a raw & < or > outside any CDATA section."""
    stripped = re.sub(r"<!\[CDATA\[.*?\]\]>", "", dsl, flags=re.S)
    return [t for t in text_nodes(stripped) if t.strip() and scan_specials(t)]


def element_count(dsl: str) -> int:
    """Count of tags the parser will build. The service caps one document at 4096."""
    return len(re.findall(r"<[A-Za-z]", dsl))


MAX_ELEMENTS = 3900  # safety margin below the service's hard limit of 4096


# ------------------------------------------------------------------------------ doc
class Doc:
    def __init__(self, width: int, height: int, background: str = "transparent"):
        self.w, self.h = width, height
        self.p = [f'<Snapshot background="{background}" type="png">',
                  f'<Container width="{width}" height="{height}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']
        self.notes: list = []

    def raw(self, s: str) -> "Doc":
        self.p.append(s)
        return self

    def box(self, x, y, w, h, color, radius=None, border=None, tl=None, tr=None,
            bl=None, br=None, shadow=None, opacity=None) -> "Doc":
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if isinstance(radius, (int, float)):
            a += f' borderRadius="{radius}"'
        elif radius:
            side, val = radius
            m = {"top": ("TopLeft", "TopRight"), "bottom": ("BottomLeft", "BottomRight"),
                 "left": ("TopLeft", "BottomLeft"), "right": ("TopRight", "BottomRight")}
            for n in m[side]:
                a += f' borderRadius{n}="{val}"'
        for n, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
            if v is not None:
                a += f' borderRadius{n}="{v}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def circ(self, cx, cy, r, color) -> "Doc":
        return self.box(round(cx - r, 2), round(cy - r, 2), round(2 * r, 2), round(2 * r, 2),
                        color, radius=round(r, 2))

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, w=None,
             align="CENTER_LEFT", spacing=None, maxw=None, tag=None, mono=False,
             raw=False, preserve_spaces=False) -> "Doc":
        if maxw is not None:
            assert_fits(s, size, maxw, tag or s[:12], mono)
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        if raw or preserve_spaces:
            # <Raw> is only legal inside <Text>; it preserves runs of spaces exactly
            body = f"<Raw>{esc(s, force_cdata=True)}</Raw>"
        else:
            body = esc(s)
        if w:
            self.p.append(f'<Positioned left="{x}" top="{y}" width="{w}">'
                          f'<Container alignment="{align}"><Text {a}>{body}</Text>'
                          f'</Container></Positioned>')
        else:
            self.p.append(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')
        return self

    def rtext(self, right, y, s, size, color, weight="NORMAL", family=CJK, maxw=None,
              tag=None) -> "Doc":
        """Right-aligned single line whose right edge lands on `right`."""
        w = text_width(s, size)
        if maxw is not None:
            assert_fits(s, size, maxw, tag or s[:12])
        return self.text(round(right - w, 2), y, s, size, color, weight=weight, family=family)

    def ctext(self, center, y, s, size, color, weight="NORMAL", family=CJK) -> "Doc":
        w = text_width(s, size)
        return self.text(round(center - w / 2, 2), y, s, size, color, weight=weight,
                         family=family)

    def rot(self, x, y, w, h, color, deg, radius=None, border=None) -> "Doc":
        """Box of w x h whose *top-left* before rotation is (x, y), rotated by `deg`
        about its own centre (service transform origin is the document top-left)."""
        ang = math.radians(deg)
        m00, m01 = math.cos(ang), math.sin(ang)
        m10, m11 = -math.sin(ang), math.cos(ang)
        cx, cy = x + w / 2, y + h / 2
        tx = cx - m00 * (w / 2) - m10 * (h / 2)
        ty = cy - m01 * (w / 2) - m11 * (h / 2)
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        mat = f"({m00:.6f},{m01:.6f},0,0,{m10:.6f},{m11:.6f},0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">{a}/>'
                      f'</Transform></Positioned>')
        return self

    def seg(self, x0, y0, x1, y1, color, th, deg=0.0) -> "Doc":
        """Straight segment from (x0,y0) to (x1,y1) drawn as a rotated bar."""
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        # local top-left so that the bar centre sits on the segment midpoint
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ang = math.radians(deg)
        m00, m01 = math.cos(ang), math.sin(ang)
        m10, m11 = -math.sin(ang), math.cos(ang)
        tx = cx - m00 * (length / 2) - m10 * (th / 2)
        ty = cy - m01 * (length / 2) - m11 * (th / 2)
        mat = f"({m00:.6f},{m01:.6f},0,0,{m10:.6f},{m11:.6f},0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'<Container width="{length:.2f}" height="{th}" color="{color}" '
                      f'borderRadius="{th / 2}"/></Transform></Positioned>')
        return self

    def glyph(self, cx, cy, r, color, shape="CIRCLE", deg=0.0) -> "Doc":
        """One animation unit. Same helper for every frame so units stay identical."""
        if shape == "CIRCLE":
            return self.circ(cx, cy, r, color)
        if shape == "SQUARE":
            if deg:
                return self.rot(cx - r, cy - r, 2 * r, 2 * r, color, deg, radius=r * 0.22)
            return self.box(round(cx - r, 2), round(cy - r, 2), round(2 * r, 2),
                            round(2 * r, 2), color, radius=round(r * 0.22, 2))
        raise ValueError(shape)

    def finish(self) -> str:
        self.p += ['</Stack>', '</Container>', '</Snapshot>']
        dsl = "\n".join(self.p) + "\n"
        n = element_count(dsl)
        if n > MAX_ELEMENTS:
            raise AssertionError(
                f"document has {n} elements, the service rejects >4096 (RENDER_ERROR)")
        bad = raw_text_nodes(dsl)
        if bad:
            raise AssertionError(
                f"{len(bad)} text node(s) contain a bare </&/> outside CDATA (a bare < is a "
                f"hard 400 TAG_OPEN); first offender: {bad[0][:60]!r}")
        return dsl

    def stats(self) -> dict:
        dsl = "\n".join(self.p) + "\n"
        return {"elements": element_count(dsl),
                "text_nodes": len([t for t in text_nodes(dsl) if t.strip()]),
                "raw_text_nodes": len(raw_text_nodes(dsl)),
                "cdata_sections": dsl.count("<![CDATA[")}


def card(doc: Doc, x, y, w, h, radius=20, color="#FFFFFFFF", border="#E2E8F0FF",
         shadow="0 6 18 0 #0F172A26") -> None:
    doc.box(x, y, w, h, color, radius=radius, border=f"1 SOLID {border}", shadow=shadow)


# ------------------------------------------------------------------- overlap checks
def measure_boxes(items: list, left: float) -> list:
    """Turn the generators' `measured` list into text bounding boxes.

    `over` marks text drawn on a coloured chip; such an entry is skipped because the
    chip (not another text box) is what it must not collide with.
    """
    boxes = []
    for m in items:
        if m.get("over"):
            continue
        h = round(m["size"] * LINE_HEIGHT)
        boxes.append(dict(text=m["text"], x=left, y=m["y"], w=text_width(m["text"], m["size"]),
                          h=h, bottom=m["y"] + h))
    return boxes


def find_overlaps(items: list, left: float, pad: float = 0.0) -> list:
    boxes = measure_boxes(items, left)
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and
                    a["y"] < b["bottom"] + pad and b["y"] < a["bottom"] + pad):
                bad.append(f'OVERLAP "{a["text"][:18]}"({a["y"]}..{a["bottom"]}) vs '
                           f'"{b["text"][:18]}"({b["y"]}..{b["bottom"]})')
    return bad


def find_boxes_overlapping_rect(items: list, left: float, rect: tuple, pad: float = 0.0) -> list:
    """Text boxes that collide with a (x, y, w, h) rectangle such as a chip."""
    rx, ry, rw, rh = rect
    bad = []
    for b in measure_boxes(items, left):
        if (b["x"] < rx + rw and rx < b["x"] + b["w"] and
                b["y"] < ry + rh + pad and ry < b["bottom"] + pad):
            bad.append(f'CHIP-COLLISION "{b["text"][:18]}"({b["x"]},{b["y"]}) vs rect {rect}')
    return bad

