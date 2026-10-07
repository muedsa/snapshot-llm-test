# -*- coding: utf-8 -*-
"""A21 shared brand kit for the Layerlight (叠光) launch posters, rounds 01-03.

Everything the three rounds share lives here: the design token tables, the
5-6 component brand mark, the measured text metrics (measured from real service
renders, see tmp/A21/probe-metrics.json) and a layout recorder that emits both
the DSL and a machine-checkable description of every element.

The three build_*.py scripts only decide *composition*; the mark, the type
scale and the copy registry stay identical so that round-02/round-03 really are
edits of the round-01 work.
"""
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
SUITE = os.path.join(ROOT, "tmp", RUN, "_suite")
sys.path.insert(0, SUITE)
import dsllib as D  # noqa: E402

UI = "Inter,Noto Sans CJK SC"
DISPLAY = "Inter Black,Noto Sans CJK SC"

# --------------------------------------------------------------------------
# measured text metrics: key -> (ink_width, ink_height, ink_top_offset)
# source: tmp/20261004-182918/A21/probe-metrics.json (rendered by the real
# open-snapshot service, ink measured with PIL). dy/dh are exact for the
# string/size/style/letterSpacing combination in MEASURED_AT.
# --------------------------------------------------------------------------
MEASURED = {
    ("\u53e0\u5149", 108, "BOLD", 2, "UI"): (209, 103, 33),
    ("Layerlight", 64, "BOLD", 1, "UI"): (316, 63, 13),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 36, "NORMAL", 3, "UI"): (346, 34, 11),
    ("ONLINE LAUNCH", 24, "BOLD", 2, "UI"): (223, 18, 5),
    ("2026.11.07 19:30", 28, "BOLD", 0.5, "UI"): (237, 22, 6),
    ("\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00", 28, "NORMAL", 1, "UI"): (229, 28, 7),
    ("layerlight.example.org", 26, "BOLD", 0.5, "UI"): (295, 26, 5),
    ("Layerlight", 24, "BOLD", 2, "UI"): (135, 24, 4),
    ("\u8bb2\u8005", 24, "NORMAL", 1, "UI"): (47, 24, 7),
    ("2026.11.07", 28, "BOLD", 1, "UI"): (154, 22, 6),
    ("19:30", 28, "BOLD", 1, "UI"): (79, 22, 6),
    ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a", 52, "BOLD", 0, "UI"): (585, 50, 15),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 52, "BOLD", 0, "UI"): (776, 51, 14),
    ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a", 48, "BOLD", 0, "UI"): (540, 47, 14),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 48, "BOLD", 0, "UI"): (716, 47, 14),
    ("Northstar Research / \u4e91\u6784\u5de5\u5177", 26, "NORMAL", 0.5, "UI"): (377, 26, 7),
    ("Northstar Research / \u4e91\u6784\u5de5\u5177", 28, "NORMAL", 0.5, "UI"): (406, 28, 7),
    ("\u514d\u8d39\u53c2\u52a0 \u00b7 \u65e0\u9700\u62a5\u540d", 26, "NORMAL", 1, "UI"): (234, 26, 7),
    ("\u514d\u8d39\u53c2\u52a0 \u00b7 \u65e0\u9700\u62a5\u540d", 28, "NORMAL", 1, "UI"): (253, 28, 7),
    ("Clarity through structure", 26, "NORMAL", 1, "UI"): (322, 26, 5),
    ("Clarity through structure", 28, "NORMAL", 1, "UI"): (346, 27, 6),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 32, "NORMAL", 2, "UI"): (302, 32, 9),
    ("\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00", 30, "NORMAL", 1, "UI"): (244, 28, 10),
    ("2026.11.07 19:30", 30, "BOLD", 0.5, "UI"): (257, 23, 7),
    ("\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00", 26, "NORMAL", 1, "UI"): (212, 26, 7),
    ("layerlight.example.org", 28, "BOLD", 0.5, "UI"): (315, 28, 5),
    ("ONLINE LAUNCH", 26, "BOLD", 2, "UI"): (235, 19, 6),
    ("ONLINE LAUNCH", 26, "BOLD", 2, "DISPLAY"): (238, 19, 6),
    ("\u53e0\u5149", 108, "BOLD", 2, "DISPLAY"): (209, 103, 33),
    ("\u53e0\u5149", 96, "BOLD", 2, "DISPLAY"): (186, 92, 29),
    ("\u53e0\u5149", 32, "BOLD", 2, "DISPLAY"): (63, 32, 9),
    ("Layerlight", 64, "BOLD", 1, "DISPLAY"): (330, 64, 12),
    ("Layerlight", 60, "BOLD", 1, "DISPLAY"): (308, 60, 11),
    ("Layerlight", 24, "BOLD", 2, "DISPLAY"): (139, 24, 4),
    ("Layerlight", 32, "BOLD", 2, "DISPLAY"): (177, 32, 6),
    ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a", 52, "BOLD", 0, "DISPLAY"): (585, 50, 15),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 52, "BOLD", 0, "DISPLAY"): (776, 51, 14),
    ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a", 48, "BOLD", 0, "DISPLAY"): (540, 47, 14),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 48, "BOLD", 0, "DISPLAY"): (716, 47, 14),
    ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a", 56, "BOLD", 0, "DISPLAY"): (629, 54, 17),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 48, "BOLD", 0, "DISPLAY"): (429, 47, 14),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 52, "BOLD", 0, "DISPLAY"): (465, 50, 15),
    ("\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 46, "BOLD", 0, "DISPLAY"): (411, 45, 13),
    ("\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 48, "BOLD", 0, "DISPLAY"): (283, 47, 14),
    ("\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 52, "BOLD", 0, "DISPLAY"): (306, 51, 14),
    ("\u53e0\u5149 Layerlight", 32, "BOLD", 2, "DISPLAY"): (252, 35, 9),
    ("\u53e0\u5149", 44, "BOLD", 2, "DISPLAY"): (87, 42, 13),
    ("\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 52, "BOLD", 0, "DISPLAY"): (1397, 51, 14),
}

# per-character advance widths in em, calibrated on the probe render
_CJK = 1.00
_EM = {"U": 0.72, "L": 0.55, "d": 0.56, "s": 0.28, "/": 0.42, ".": 0.30,
       ":": 0.30, "-": 0.38, "\u00b7": 0.40}


def estimate(text, size, ls=0.0):
    w = 0.0
    for ch in text:
        o = ord(ch)
        if o > 0x2E80:
            w += _CJK * size
        elif ch == " ":
            w += _EM["s"] * size
        elif ch.isupper():
            w += _EM["U"] * size
        elif ch.isdigit():
            w += _EM["d"] * size
        else:
            w += _EM.get(ch, _EM["L"]) * size
    return w + ls * len(text)


def font_tag(font):
    return "DISPLAY" if (font or "").startswith("Inter Black") else "UI"


def metric(text, size, style="NORMAL", ls=0.0, font=None):
    """Return (ink_w, ink_h, ink_dy, box_w, source)."""
    m = MEASURED.get((text, size, style, ls, font_tag(font)))
    if m:
        iw, ih, dy = m
        return iw, ih, dy, iw + ls + 14, "measured"
    ew = estimate(text, size, ls)
    cjk = sum(1 for c in text if ord(c) > 0x2E80)
    if cjk >= len(text) * 0.6:
        ih = int(size * 0.97)
        dy = int(round(size * 0.29))
    else:
        ih = int(size * 0.95)
        dy = int(round(size * 0.21))
    if font_tag(font) == "DISPLAY":
        ew *= 1.05
    return int(round(ew)), ih, dy, int(round(ew)) + int(ls) + 16, "estimated"


# --------------------------------------------------------------------------
# design tokens
# --------------------------------------------------------------------------
def tokens(theme="dark"):
    base = {
        "brand": {
            "primary": "#6D4AFF",
            "primary_light": "#8E74FF",
            "primary_deep": "#3A1FB0",
        },
        "type_scale": {
            "display_cjk": {"size": 108, "style": "BOLD", "ls": 2, "font": DISPLAY,
                            "role": "main-title"},
            "display_latin": {"size": 64, "style": "BOLD", "ls": 1, "font": DISPLAY,
                              "role": "main-title"},
            "title_long": {"size": 52, "style": "BOLD", "ls": 0, "font": DISPLAY,
                           "role": "main-title"},
            "wordmark": {"size": 24, "style": "BOLD", "ls": 2, "font": DISPLAY,
                         "role": "brand-wordmark"},
            "kicker": {"size": 32, "style": "BOLD", "ls": 2, "font": DISPLAY,
                       "role": "brand-name"},
            "tagline": {"size": 36, "style": "NORMAL", "ls": 3, "font": UI,
                        "role": "tagline"},
            "info_value": {"size": 28, "style": "BOLD", "ls": 0.5, "font": UI,
                           "role": "info-value"},
            "info_body": {"size": 28, "style": "NORMAL", "ls": 1, "font": UI,
                          "role": "info-body"},
            "link": {"size": 26, "style": "BOLD", "ls": 0.5, "font": UI,
                     "role": "link"},
            "meta": {"size": 26, "style": "NORMAL", "ls": 1, "font": UI,
                     "role": "meta"},
            "micro": {"size": 24, "style": "BOLD", "ls": 2, "font": UI,
                      "role": "micro-label"},
        },
        "mark": {
            "components": 6,
            "normalized_box": 1.0,
            "plates": [
                {"id": "plate-base", "x": 0.00, "y": 0.50, "w": 0.74, "h": 0.30,
                 "radius": 0.085},
                {"id": "plate-mid", "x": 0.13, "y": 0.29, "w": 0.74, "h": 0.30,
                 "radius": 0.085},
                {"id": "plate-top", "x": 0.26, "y": 0.08, "w": 0.74, "h": 0.30,
                 "radius": 0.085},
            ],
            "beam": {"cx": 0.50, "cy": 0.42, "len": 1.06, "thickness": 0.05,
                     "angle_deg": 18},
            "spark": {"cx": 0.78, "cy": 0.175, "dot_r": 0.058, "ring_r": 0.10,
                      "ring_w": 0.016},
        },
    }
    if theme == "dark":
        base["surface"] = {
            "bg_top": "#0A0F24",
            "bg_bottom": "#141034",
            "panel": "#FFFFFF0F",
            "panel_border": "#FFFFFF24",
            "hairline": "#FFFFFF26",
            "ink": "#F5F4FF",
            "ink_muted": "#B7BEE0",
            "accent_ink": "#7FE9D6",
            "chip_fill": "#6D4AFF",
            "chip_ink": "#FFFFFF",
            "tick": "#4BE3C8",
            "plate_base": "#3A1FB0B3",
            "plate_base_border": "#6D4AFF66",
            "plate_mid": "#6D4AFF8C",
            "plate_mid_border": "#9C86FF8A",
            "beam": "#4BE3C8F2",
            "spark_dot": "#EAFFF9",
            "spark_ring": "#4BE3C8CC",
            "glow": "#6D4AFF59",
        }
    else:
        base["surface"] = {
            "bg_top": "#FBFAFF",
            "bg_bottom": "#EDE9FB",
            "panel": "#FFFFFF",
            "panel_border": "#6D4AFF33",
            "hairline": "#6D4AFF3D",
            "ink": "#1B1440",
            "ink_muted": "#4B4478",
            "accent_ink": "#5326E8",
            "chip_fill": "#5B2BE0",
            "chip_ink": "#FFFFFF",
            "tick": "#5326E8",
            "plate_base": "#C9B6FF",
            "plate_base_border": "#6D4AFF80",
            "plate_mid": "#A78BFA",
            "plate_mid_border": "#5B2BE099",
            "beam": "#0E9E86E6",
            "spark_dot": "#FFFFFF",
            "spark_ring": "#0E9E86",
            "glow": "#6D4AFF33",
        }
    return base


# --------------------------------------------------------------------------
# brand mark: exactly six components
# --------------------------------------------------------------------------
def rot_matrix(deg):
    th = math.radians(deg)
    a, b = math.cos(th), -math.sin(th)
    c, d = math.sin(th), math.cos(th)
    return "(%f,%f,0,0,%f,%f,0,0,0,0,1,0,0,0,0,1)" % (a, b, c, d)


def mark(x, y, s, sf, glow=True):
    """Return (dsl_list, component_rects). Six components, identical in shape
    across both sizes and all three rounds; only the palette changes."""
    m = tokens()["mark"]
    out = []
    rects = []
    if glow:
        g = s * 1.72
        out.append(D.box(x - (g - s) / 2.0, y - (g - s) / 2.0, g, g,
                         radius=g / 2.0,
                         gradient={"gradientType": "RADIAL",
                                   "gradientColors": sf["glow"] + "," + sf["glow"][:7] + "00",
                                   "gradientStops": "0,1"}))
        rects.append({"id": "aura", "kind": "decoration",
                      "rect": [round(x - (g - s) / 2.0, 1), round(y - (g - s) / 2.0, 1),
                               round(g, 1), round(g, 1)]})
    # components 1-3: the stacked light plates
    for i, p in enumerate(m["plates"]):
        px, py = x + p["x"] * s, y + p["y"] * s
        pw, ph, pr = p["w"] * s, p["h"] * s, p["radius"] * s
        if p["id"] == "plate-top":
            out.append(D.box(px, py, pw, ph, radius=pr,
                             gradient={"gradientType": "LINEAR",
                                       "gradientColors": "#8E74FF,#5B2BE0",
                                       "gradientBegin": "TOP_LEFT",
                                       "gradientEnd": "BOTTOM_RIGHT"},
                             shadow="0 10 30 0 #1B144026"))
        else:
            fill = sf["plate_base"] if p["id"] == "plate-base" else sf["plate_mid"]
            bd = (sf["plate_base_border"] if p["id"] == "plate-base"
                  else sf["plate_mid_border"])
            out.append(D.box(px, py, pw, ph, radius=pr, color=fill, border="1 SOLID " + bd))
        rects.append({"id": p["id"], "kind": "mark-component",
                      "rect": [round(px, 1), round(py, 1), round(pw, 1), round(ph, 1)]})
    # component 4: the light beam
    b = m["beam"]
    bl, bt = b["len"] * s, b["thickness"] * s
    bcx, bcy = x + b["cx"] * s, y + b["cy"] * s
    th = math.radians(b["angle_deg"])
    bw = bl * abs(math.cos(th)) + bt * abs(math.sin(th))
    bh = bl * abs(math.sin(th)) + bt * abs(math.cos(th))
    out.append(D.el("Positioned",
                    {"left": round(bcx - bl / 2.0, 2), "top": round(bcy - bt / 2.0, 2),
                     "width": round(bl, 2), "height": round(bt, 2)},
                    [D.el("Transform", {"matrix": rot_matrix(b["angle_deg"]),
                                        "origin": "(0,0)", "alignment": "CENTER"},
                          [D.el("Container", {"width": round(bl, 2),
                                              "height": round(bt, 2),
                                              "color": sf["beam"],
                                              "borderRadius": round(bt / 2.0, 2)})])]))
    # NOTE: the Positioned box must be exactly the un-rotated bar size. Any other
    # value would hand the inner Container tight constraints, and a Container
    # inside tight constraints is stretched to them, silently turning a 402x19
    # light streak into a 389x143 slab (measured on the real service).
    rects.append({"id": "beam", "kind": "mark-component",
                  "rect": [round(bcx - bw / 2.0, 1), round(bcy - bh / 2.0, 1),
                           round(bw, 1), round(bh, 1)]})
    # components 5-6: the spark and its ring
    k = m["spark"]
    dx, dy = x + k["cx"] * s, y + k["cy"] * s
    rd, rr = k["dot_r"] * s, k["ring_r"] * s
    out.append(D.box(dx - rd, dy - rd, 2 * rd, 2 * rd, radius=rd, color=sf["spark_dot"]))
    rects.append({"id": "spark-dot", "kind": "mark-component",
                  "rect": [round(dx - rd, 1), round(dy - rd, 1), round(2 * rd, 1),
                           round(2 * rd, 1)]})
    out.append(D.box(dx - rr, dy - rr, 2 * rr, 2 * rr, radius=rr,
                     border="%.1f SOLID %s" % (k["ring_w"] * s, sf["spark_ring"])))
    rects.append({"id": "spark-ring", "kind": "mark-component",
                  "rect": [round(dx - rr, 1), round(dy - rr, 1), round(2 * rr, 1),
                           round(2 * rr, 1)]})
    return out, rects


# --------------------------------------------------------------------------
# layout recorder
# --------------------------------------------------------------------------
class Layout(object):
    def __init__(self, w, h, bg_top, bg_bottom, sf):
        self.w = w
        self.h = h
        self.sf = sf
        self.bg = [D.box(0, 0, w, h,
                         gradient={"gradientType": "LINEAR",
                                   "gradientColors": bg_top + "," + bg_bottom,
                                   "gradientBegin": "TOP_CENTER",
                                   "gradientEnd": "BOTTOM_CENTER"})]
        self.mid = []
        self.decor = []
        self.tdsl = []
        self.texts = []
        self.shapes = []

    # -- decorative / structural shapes (recorded for the audit) -----------
    def rect(self, layer, x, y, w, h, **kw):
        sid = kw.pop("_id", "shape")
        self.mid.append(D.box(x, y, w, h, **kw))
        self.shapes.append({"id": sid, "layer": layer,
                            "rect": [round(x, 1), round(y, 1), round(w, 1), round(h, 1)]})

    # -- text ---------------------------------------------------------------
    def text(self, s, x, ink_top, size, *, style="NORMAL", ls=0.0, color=None,
             font=None, role="", key=None, bg_layers=None):
        """Place a single line so that its *ink top* lands on ink_top.

        The Positioned box carries no width: an unbounded max width makes
        soft-wrapping impossible, so a long string can never silently fold into
        a second line (the silent-failure mode documented in the DSL handbook).
        audit.ink_audit proves the rendered ink stays inside the declared box.
        """
        iw, ih, dy, bw, src = metric(s, size, style, ls, font)
        box_top = ink_top - dy
        box_h = ih + dy + 4
        if x + bw > self.w - 4:
            D.WARNINGS.append("text %r at x=%s needs ~%spx but only %spx of "
                              "canvas remain" % (s[:40], x, bw, self.w - x))
        self.tdsl.append(D.text_el(s, x=x, y=box_top, w=None, h=box_h,
                                  color=color or self.sf["ink"], size=size,
                                  font=font or UI, style=style, ls=ls))
        rec = {"id": key or ("%s-%d" % (role, len(self.texts) + 1)),
               "role": role, "text": s, "fontSize": size, "fontStyle": style,
               "letterSpacing": ls, "color": color or self.sf["ink"],
               "rect": [round(x, 1), round(box_top, 1), round(bw, 1), round(box_h, 1)],
               "ink": [round(x + 1, 1), round(ink_top, 1),
                       round(x + iw + ls, 1), round(ink_top + ih - 1, 1)],
               "ink_w": iw, "metric_source": src,
               "bg_layers": bg_layers or []}
        self.texts.append(rec)
        return rec

    def chip(self, s, x_right, y, size, *, padx=22, padh=24, style="BOLD", ls=2,
             fill=None, ink=None, role="", key=None, font=None):
        iw, ih, dy, bw, _ = metric(s, size, style, ls, font or UI)
        w = iw + ls + 2 * padx
        h = ih + dy + padh
        y = y
        self.mid.append(D.box(x_right - w, y, w, h, radius=h / 2.0,
                              color=fill or self.sf["chip_fill"]))
        self.shapes.append({"id": "chip-bg", "layer": "mid",
                            "rect": [round(x_right - w, 1), round(y, 1),
                                     round(w, 1), round(h, 1)]})
        ink_top = y + (h - ih) / 2.0
        rec = self.text(s, x_right - w + padx, ink_top, size, style=style, ls=ls,
                        color=ink or self.sf["chip_ink"], role=role, key=key,
                        font=font or UI)
        rec["chip_rect"] = [round(x_right - w, 1), round(y, 1), round(w, 1), round(h, 1)]
        return rec

    def rule(self, x0, x1, y, color=None, w=2, dashed=False):
        c = color or self.sf["hairline"]
        if dashed:
            self.mid.append(D.dashed(x0, x1, y, c, w, 14, 10))
        else:
            self.mid.append(D.hline(x0, x1, y, c, w))
        self.shapes.append({"id": "rule", "layer": "mid",
                            "rect": [round(x0, 1), round(y - w / 2.0, 1),
                                     round(x1 - x0, 1), round(w, 1)]})

    def tick(self, x, ink_top, size, color=None, role="row-tick"):
        h = size * 1.0
        self.mid.append(D.box(x, ink_top, 4, h, radius=2,
                              color=color or self.sf["tick"]))
        self.shapes.append({"id": role, "layer": "mid",
                            "rect": [round(x, 1), round(ink_top, 1), 4, round(h, 1)]})

    def bar(self, x, y, w, h, radius=2, color=None, _id="bar"):
        """Accent bar drawn *above* the mid layer (used for card edge accents)."""
        self.decor.append(D.box(x, y, w, h, radius=radius,
                              color=color or self.sf["tick"]))
        self.shapes.append({"id": _id, "layer": "top",
                            "rect": [round(x, 1), round(y, 1), round(w, 1),
                                     round(h, 1)]})

    def snapshot_dsl(self, include_text=True):
        """include_text=False renders the identical composition without any Text
        layer; diffing the two PNGs isolates the glyph coverage exactly, which is
        what the ink and contrast audits use."""
        layers = self.bg + self.mid + self.decor
        if include_text:
            layers = layers + self.tdsl
        body = "\n".join(layers)
        return ('<Snapshot type="png" background="%s">\n' % self.sf["bg_bottom"] +
                D.el("Container", {"width": self.w, "height": self.h},
                     [D.el("Stack", {"fit": "EXPAND"}, [body])]) + "\n</Snapshot>\n")


# --------------------------------------------------------------------------
# colour helpers (used by the contrast audit)
# --------------------------------------------------------------------------
def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def alpha_of(h):
    h = h.lstrip("#")
    if len(h) == 4:
        return int(h[3] * 2, 16) / 255.0
    if len(h) == 8:
        return int(h[6:8], 16) / 255.0
    return 1.0


def over(fg, bg, a=None):
    """Composite fg (with alpha a, or fg's own alpha) over an opaque bg."""
    f = hex2rgb(fg)
    a = alpha_of(fg) if a is None else a
    return tuple(round(f[i] * a + bg[i] * (1 - a)) for i in range(3))


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])


def contrast(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


# --------------------------------------------------------------------------
# copy registry (single source of truth for content-map.json)
# --------------------------------------------------------------------------
COPY = {
    "brand_cjk": "\u53e0\u5149",
    "brand_latin": "Layerlight",
    "tagline": "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670",
    "datetime": "2026.11.07 19:30",
    "speakers": "\u8bb2\u8005\uff1a\u6797\u5ddd / \u82cf\u8a00",
    "url": "layerlight.example.org",
    "online": "ONLINE LAUNCH",
    "sponsor": "Northstar Research / \u4e91\u6784\u5de5\u5177",
    "free": "\u514d\u8d39\u53c2\u52a0 \u00b7 \u65e0\u9700\u62a5\u540d",
    "clarity_en": "Clarity through structure",
    "long_title_a": "\u5f53\u6240\u6709\u4fe1\u606f\u90fd\u60f3\u6210\u4e3a\u6807\u9898\uff1a",
    "long_title_b": "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670\u7684\u7ed3\u6784\u5316\u65b9\u6cd5",
}