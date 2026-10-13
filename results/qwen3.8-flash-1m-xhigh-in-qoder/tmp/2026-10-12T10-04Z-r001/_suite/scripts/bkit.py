"""Shared drawing kit for the B-track portfolios.

One Sheet class handles absolute placement on a canvas, measured text (so the service
never wraps what must stay on one line), SVG-style ClipPath polygons - including holes
drawn as reversed subpaths, because the parser ignores fillType and keeps non-zero
winding - rotation through Transform.matrix, and a layout self-check that reports every
overlapping or overflowing text run.

Capabilities below were probed against the live service, not assumed:
  ClipPath path="M ... L ... C ... Q ... A ... Z"  -> 200, correct pixels
  fillType="EVEN_ODD"                              -> silently ignored (use reversed ring)
  Container border thicker than borderRadius       -> 500 INTERNAL_ERROR (guarded below)
  Transform needs matrix + alignment; origin only parses as "(x,y)"
  BackdropFilter without an explicit clip re-composites the whole canvas opaquely
  A Stack whose children are all Positioned        -> 400 "Layout size is infinite"
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN", "2026-10-12T10-04Z-r001")
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import (C, Container, Node, Positioned, Snapshot, Stack, Transform,  # noqa: E402
                  matrix2d, num)

SANS, MONO, SERIF = "Noto Sans CJK SC", "Noto Sans Mono CJK SC", "Noto Serif CJK SC"
CJK_EM, LATIN_EM, MONO_EM, LINE_H = 1.0, 0.62, 0.52, 1.46
# bold advances measured wider than the plain em model on this service
BOLD_SLACK = 1.14


def tw(t, size, mono=False):
    return sum(size * (CJK_EM if ord(c) > 0x2E80 else (MONO_EM if mono else LATIN_EM))
               for c in t)


def tokens(text):
    out, cur = [], ""
    for ch in text:
        if ch.isascii() and not ch.isspace():
            cur += ch
        else:
            if cur:
                out.append(cur)
                cur = ""
            out.append(ch)
    if cur:
        out.append(cur)
    return out


def wrap(text, size, width, mono=False):
    rows, cur = [], ""
    for tk in tokens(text):
        if cur and tw(cur, size, mono) + tw(tk, size, mono) > width:
            if not tk.strip():
                rows.append(cur.rstrip())
                cur = ""
                continue
            rows.append(cur.rstrip())
            cur = tk.lstrip()
        else:
            cur += tk
    if cur.strip():
        rows.append(cur.rstrip())
    return rows


def f(x):
    return num(round(float(x), 3))


def fit(t, size, maxw, mono=False):
    """Truncate to maxw with a real ellipsis so the measured box matches what paints."""
    if tw(t, size, mono) <= maxw:
        return t
    while t and tw(t + "…", size, mono) > maxw:
        t = t[:-1]
    return t + "…"


class Sheet:
    def __init__(self, w, h, min_font=20, bg="#FFFFFF"):
        self.w, self.h, self.min_font, self.bg = w, h, min_font, bg
        self.nodes = [C(width=f(w), height=f(h), color=bg)]
        self.items = []
        self.panels = []
        self.truncated = []
        self.shapes = 0

    def panel(self, x, y, w, h):
        """Declare a card region; audit() then reports text spilling out of it."""
        self.panels.append([x, y, x + w, y + h])

    # ---------------------------------------------------------------- text
    def text(self, role, t, x, y, size, colour, *, font=SANS, bold=False,
             align="left", anchor=None, maxw=None):
        mono = font == MONO
        if maxw is not None:
            kept = fit(t, size, maxw, mono)
            if kept != t:
                self.truncated.append(t)
            t = kept
        w = tw(t, size, mono)
        if align == "right":
            x -= w
        elif align == "center":
            x -= w / 2
        a = {"fontSize": f(size), "color": colour, "fontFamily": font}
        if maxw is not None:
            a["overflow"] = "ELLIPSIS"
            a["maxLines"] = "1"
        if bold:
            a["fontStyle"] = "BOLD"
        self.nodes.append(Positioned(Node("Text", a, [], t), left=f(x), top=f(y),
                                     width=f(w * BOLD_SLACK + 10)))
        self.items.append({"role": role, "text": t,
                           "box": [round(x, 2), round(y, 2), round(x + w, 2),
                                   round(y + size * 1.06, 2)],
                           "font_size": size, "colour": colour, "font": font})
        return y + size * LINE_H

    def para(self, role, t, x, y, size, colour, width, *, font=SANS, bold=False,
             gap=4):
        """Wrapped paragraph; each line advances by the measured 1.46em pitch plus gap."""
        for ln in wrap(t, size, width, font == MONO):
            y = self.text(role, ln, x, y, size, colour, font=font, bold=bold) \
                + size * (LINE_H - 1.06) + gap
        return y - gap

    # ---------------------------------------------------------------- shapes
    def rect(self, x, y, w, h, colour, *, radius=None, shape=None, border=None,
             gradient=None, shadow=None):
        a = {"width": f(w), "height": f(h), "color": colour}
        if shape:
            a["shape"] = shape
        elif radius is not None:
            a["borderRadius"] = f(radius)
        if border:
            # live-service probe: border thicker than borderRadius -> 500 INTERNAL_ERROR
            bw = float(border.split()[0])
            if radius is not None and not shape and bw > float(radius):
                raise ValueError(f"border {bw} > borderRadius {radius}: service returns 500")
            a["border"] = border
        if gradient:
            a.update(gradient)
        if shadow:
            a["boxShadow"] = shadow
        self.nodes.append(Positioned(C(**a), left=f(x), top=f(y)))
        self.shapes += 1

    def path(self, x, y, w, h, d, colour, *, opacity=None):
        """Filled polygon: a coloured box clipped by an SVG-style path in its own box."""
        inner = C(width=f(w), height=f(h), color=colour)
        if opacity is not None:
            inner = Node("Opacity", {"opacity": f(opacity)}, [inner])
        clip = Node("ClipPath", {"path": d}, [inner])
        self.nodes.append(Positioned(clip, left=f(x), top=f(y), width=f(w),
                                     height=f(h)))
        self.shapes += 1

    def tri(self, x, y, w, h, colour, *, up=True):
        pts = (f"{x},{y + h} {x + w / 2},{y} {x + w},{y + h}" if up else
               f"{x},{y} {x + w},{y} {x + w / 2},{y + h}")
        a, b, c = pts.split()
        self.path(x, y, w, h, f"M {a} L {b} L {c} Z", colour)

    def donut_segment(self, cx, cy, r0, r1, a0, a1, colour, *, steps=36):
        """Annular sector from a0 to a1 (degrees, clockwise from 12 o'clock)."""
        def pt(r, ang):
            t = math.radians(ang - 90.0)
            return (cx + r * math.cos(t), cy + r * math.sin(t))
        n = max(2, int(abs(a1 - a0) / 360 * steps) + 1)
        outer = [pt(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
        inner = [pt(r0, a0 + (a1 - a0) * i / n) for i in range(n, -1, -1)]
        allp = outer + inner
        x0 = min(p[0] for p in allp)
        y0 = min(p[1] for p in allp)
        w = max(p[0] for p in allp) - x0
        h = max(p[1] for p in allp) - y0
        d = "M " + " L ".join(f"{f(p[0] - x0)} {f(p[1] - y0)}" for p in allp) + " Z"
        self.path(x0, y0, w, h, d, colour)

    def line(self, x0, y0, x1, y1, colour, weight=2.0, *, cap_round=False):
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            return
        rad = math.atan2(dy, dx)
        box_w, box_h = ln, weight
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        a = {"width": f(box_w), "height": f(box_h), "color": colour}
        if cap_round:
            a["borderRadius"] = f(weight / 2)
        tf = Transform(C(**a), matrix=matrix2d(math.cos(rad), math.sin(rad)),
                       alignment="CENTER")
        self.nodes.append(Positioned(tf, left=f(cx - box_w / 2), top=f(cy - box_h / 2),
                                     width=f(box_w), height=f(box_h)))
        self.shapes += 1

    def clip_line(self, x0, y0, x1, y1, colour, max_len, weight=2.0):
        """Line shortened to max_len so it never reaches a neighbour's box.

        Returns the x it actually stopped at, which is what the next element should
        start from. A full-width line between two measured text runs is the only safe
        way to fill the gap without the audit reporting an overlap.
        """
        need = math.hypot(x1 - x0, y1 - y0)
        if need > max_len:
            k = max_len / need
            x1, y1 = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        self.line(x0, y0, x1, y1, colour, weight)
        return x1

    def arrow(self, x0, y0, x1, y1, colour, weight=2.0, head=10.0):
        self.line(x0, y0, x1, y1, colour, weight)
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        for da in (150, -150):
            t = math.radians(ang + da)
            self.line(x1, y1, x1 + head * math.cos(t), y1 + head * math.sin(t),
                      colour, max(weight * 0.8, 1.5))

    def dot(self, cx, cy, r, colour, *, ring=None, ring_w=2):
        self.rect(cx - r, cy - r, 2 * r, 2 * r, colour, shape="CIRCLE")
        if ring:
            self.rect(cx - r - ring_w, cy - r - ring_w, 2 * (r + ring_w),
                      2 * (r + ring_w), "#00000000", border=f"{ring_w} SOLID {ring}",
                      shape="CIRCLE")

    def rotated(self, x, y, w, h, colour, deg, *, radius=None, shape=None):
        rad = math.radians(deg)
        tf = Transform(C(width=f(w), height=f(h), color=colour,
                         **({"borderRadius": f(radius)} if radius is not None else {}),
                         **({"shape": shape} if shape else {})),
                       matrix=matrix2d(math.cos(rad), math.sin(rad)),
                       alignment="CENTER")
        self.nodes.append(Positioned(tf, left=f(x), top=f(y), width=f(w), height=f(h)))
        self.shapes += 1

    # ---------------------------------------------------------------- compositing
    def glass(self, x, y, w, h, *, sigma=9.0, tint=None, radius=0.0,
              clip="ClipRRect", path=None):
        """Frosted panel. BackdropFilter MUST stay inside an explicit clip: an unclipped
        one re-composites the whole canvas and turns earlier translucency opaque
        (requests B03-p6-bottom-only vs B03-p6-clipped-backdrop)."""
        inner = C(width=f(w), height=f(h), color=tint or "#00000000")
        bd = Node("BackdropFilter", {"sigmaX": f(sigma), "sigmaY": f(sigma)}, [inner])
        if clip == "ClipPath":
            wrap = Node("ClipPath", {"path": path}, [bd])
        else:
            wrap = Node(clip, {"borderRadius": f(radius),
                               "clipBehavior": "ANTI_ALIAS"}, [bd])
        self.nodes.append(Positioned(wrap, left=f(x), top=f(y), width=f(w), height=f(h)))
        self.shapes += 1

    def filter_rect(self, x, y, w, h, colour, *, blend="MULTIPLY", tintColor=None,
                    sigma=None, radius=None):
        """Colour-shifted block: ColorFiltered over a filled box (bounded subtree)."""
        inner = C(width=f(w), height=f(h), color=colour,
                  **({"borderRadius": f(radius)} if radius is not None else {}))
        if sigma:
            inner = Node("ImageFiltered", {"sigmaX": f(sigma), "sigmaY": f(sigma)},
                         [inner])
        node = (Node("ColorFiltered", {"color": tintColor, "blendMode": blend}, [inner])
                if tintColor else inner)
        self.nodes.append(Positioned(node, left=f(x), top=f(y)))
        self.shapes += 1

    def rich(self, role, runs, x, y, *, size=24, colour="#111111", font=SANS,
             letterSpacing=None, height=None, shadow=None, features=None,
             align="left"):
        """One line of mixed-style spans; width is summed from the same em model the
        single-run text() uses, so nothing wraps or collides."""
        nodes, total = [], 0.0
        for t, ov in runs:
            s = ov.get("size", size)
            mono = ov.get("font", font) == MONO
            total += tw(t, s, mono)
            a = {"fontSize": f(s), "color": ov.get("colour", colour)}
            if ov.get("font", font) != font:
                a["fontFamily"] = ov["font"]
            if ov.get("bold"):
                a["fontStyle"] = "BOLD"
            if ov.get("decoration"):
                a["decoration"] = ov["decoration"]
            # Raw keeps the spaces a plain Text span would trim (Java trims U+3000 too),
            # and it does not inherit the parent's fontSize - so the style is copied in.
            if ov.get("raw"):
                nodes.append(Node("Raw", a, None, t))
            else:
                nodes.append(Node("Text", a, [], t))
        a = {}
        if letterSpacing:
            a["letterSpacing"] = f(letterSpacing)
            total += letterSpacing * max(len("".join(t for t, _ in runs)) - 1, 0)
        if height:
            a["height"] = f(height)
        if shadow:
            a["textShadow"] = shadow
        if features:
            a["fontFeatures"] = features
        drawn = total * BOLD_SLACK + 10
        if align == "right":
            x -= drawn
        elif align == "center":
            x -= drawn / 2
        self.nodes.append(Positioned(Node("Text", a, nodes), left=f(x), top=f(y)))
        self.items.append({"role": role, "text": "".join(t for t, _ in runs),
                           "box": [round(x, 2), round(y, 2),
                                   round(x + drawn, 2),
                                   round(y + size * 1.06, 2)],
                           "font_size": size, "colour": colour, "font": font})
        return y + size * LINE_H

    def shear(self, x, y, w, h, colour, *, kx=0.0, ky=0.0, radius=None, deg=None,
              sx=1.0, sy=1.0):
        """Affine box: column-major matrix (a,b,0,0 | c,d,0,0 | ...) so kx shears
        horizontally and ky vertically; deg rotates, sx/sy scale around CENTER."""
        rad = math.radians(deg or 0.0)
        co, si = math.cos(rad), math.sin(rad)
        a11 = co * sx - si * sy * kx
        a12 = si * sx + co * sy * kx
        a21 = -si * sy + co * ky
        a22 = co * sy + si * ky
        m = (f"({f(a11)},{f(a12)},0,0,{f(a21)},{f(a22)},0,0,0,0,1,0,0,0,0,1)")
        tf = Transform(C(width=f(w), height=f(h), color=colour,
                         **({"borderRadius": f(radius)} if radius is not None else {})),
                       matrix=m, alignment="CENTER")
        self.nodes.append(Positioned(tf, left=f(x), top=f(y), width=f(w), height=f(h)))
        self.shapes += 1

    # ---------------------------------------------------------------- output
    def elements(self):
        """Every node the parser will see, wrappers included."""
        def walk(n):
            return 1 + sum(walk(c) for c in n.children)
        return sum(walk(n) for n in self.nodes) + 3

    def finish(self):
        # the parser rejects documents over 4096 elements (request B03-probe-nodes4000);
        # procedural pieces must know before the service does
        if self.elements() > 4090:
            raise ValueError(f"{self.elements()} elements exceeds the 4096-element cap")
        return Snapshot(Stack(C(width=f(self.w), height=f(self.h)), *self.nodes),
                        background=self.bg, type="png")

    def dsl(self):
        return self.finish().render() + "\n"

    def audit(self, margin=8, ignore_roles=()):
        """Layout self-check. `ignore_roles` names roles that are decorative texture
        (watermarks, ghost glyphs) and may legitimately sit under real content."""
        items = [i for i in self.items if i["role"] not in ignore_roles]
        ov = [(x["text"], y["text"]) for i, x in enumerate(items)
              for y in items[i + 1:]
              if not (x["box"][2] <= y["box"][0] or y["box"][2] <= x["box"][0]
                      or x["box"][3] <= y["box"][1] or y["box"][3] <= x["box"][1])]
        out = [i["text"] for i in items
               if i["box"][0] < margin or i["box"][1] < margin
               or i["box"][2] > self.w - margin or i["box"][3] > self.h - margin]
        small = [i["text"] for i in items if i["font_size"] < self.min_font]
        spill = []
        for i in items:
            x0, y0, x1, y1 = i["box"]
            host = [p for p in self.panels
                    if p[0] <= x0 + 1 and p[1] <= y0 + 1 and x0 < p[2] and y0 < p[3]]
            if not host:
                continue
            px0, py0, px1, py1 = min(host, key=lambda p: (p[2] - p[0]) * (p[3] - p[1]))
            if x1 > px1 + 1 or y1 > py1 + 1:
                spill.append([i["text"], [round(x1, 1), round(y1, 1)],
                              [round(px1, 1), round(py1, 1)]])
        return {"size": [self.w, self.h], "texts": len(items),
                "decor_texts": len(self.items) - len(items),
                "shapes": self.shapes, "overlap_n": len(ov), "overlaps": ov[:6],
                "outside_n": len(out), "outside": out[:6],
                "spill_n": len(spill), "spill": spill[:6],
                "truncated_n": len(self.truncated), "truncated": self.truncated[:6],
                "below_min_font_n": len(small), "below_min_font": small[:6]}


def place(labels, min_gap=10):
    placed, prev = [], -1e9
    for text, x0, w in labels:
        x = max(x0, prev + min_gap)
        placed.append((text, x, w))
        prev = x + w
    return placed
