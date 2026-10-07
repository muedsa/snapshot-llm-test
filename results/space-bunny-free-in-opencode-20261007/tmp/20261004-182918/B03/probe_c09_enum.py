"""B03 case-09 · enum/format discovery probe (diagnostic).

The enums reference page does NOT list PaintStrokeCap / PaintStrokeJoin /
TextHeightMode, and probe-c09b already proved:
  * foregroundStrokeCap="BEVEL" -> 400 (no such constant)
  * a plain text="" attribute cannot carry a double quote
So every candidate is tried on its own tiny canvas; one 400 does not hide the
rest of the matrix. Success/failure text is drawn into the SAME canvas as the
sample, and the verdict is also printed here.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el = D.el
INK = "#EAF2FBFF"
INK2 = "#9DB4CCFF"
AMBER = "#FBBF24FF"
CYAN = "#67E8F9FF"
BG = "#0B1020FF"

SAMPLES = [
    ("cap-BUTT", {"foregroundStrokeCap": "BUTT"}),
    ("cap-ROUND", {"foregroundStrokeCap": "ROUND"}),
    ("cap-SQUARE", {"foregroundStrokeCap": "SQUARE"}),
    ("cap-BEVEL", {"foregroundStrokeCap": "BEVEL"}),
    ("join-MITER", {"foregroundStrokeJoin": "MITER"}),
    ("join-ROUND", {"foregroundStrokeJoin": "ROUND"}),
    ("join-BEVEL", {"foregroundStrokeJoin": "BEVEL"}),
    ("aa-true", {"foregroundAntiAlias": "true"}),
    ("aa-false", {"foregroundAntiAlias": "false"}),
    ("widthBasis-LONGESTLINE", {"textWidthBasis": "LONGESTLINE"}),
    ("heightMode-TIGHT", {"textHeightMode": "TIGHT"}),
    ("heightMode-ATLEAST", {"textHeightMode": "AT_LEAST"}),
    ("heightMode-EXACTLY", {"textHeightMode": "EXACTLY"}),
    ("heightMode-EXACT", {"textHeightMode": "EXACT"}),
    ("heightMode-AT_MOST", {"textHeightMode": "AT_MOST"}),
    ("heightMode-MIN", {"textHeightMode": "MIN"}),
    ("heightMode-MAX", {"textHeightMode": "MAX"}),
    ("heightMode-1", {"textHeightMode": "1"}),
    ("height-attr-18", {"height": "18"}),
    ("topRatio-0.8", {"topRatio": "0.8"}),
    ("overflow-FADE", {"overflow": "FADE"}),
    ("gaps-2-3", {"decoration": "UNDERLINE", "decorationLineStyle": "DOTTED",
                  "decorationGaps": "2 3"}),
    ("feat-range", {"fontFeatures": "smcp[2:8]"}),
    ("feat-tnum2", {"fontFeatures": "tnum=2"}),
    ("feat-plusss01", {"fontFeatures": "+ss01"}),
    ("feat-none", {"fontFeatures": "NONE"}),
    ("feat-bad", {"fontFeatures": "zzzz"}),
    ("feat-space-list", {"fontFeatures": "liga tnum=2 smcp"}),
    ("strut-forced", {"strutEnabled": "true", "strutHeightForced": "true",
                      "strutHeight": "34", "strutFontSize": "20",
                      "strutFontFamily": D.UI}),
    ("dir-RTL", {"textDirection": "RTL"}),
    ("valign-align", {"textAlign": "END"}),
    ("edging-Subpixel", {"fontEdging": "Subpixel"}),
    ("edging-Antialias", {"fontEdging": "Antialias"}),
    ("edging-ANALYTIC", {"fontEdging": "ANALYTIC"}),
    ("edging-ANTIALIAS", {"fontEdging": "ANTIALIAS"}),
    ("hinting-NONE", {"fontHinting": "NONE"}),
    ("hinting-FULL", {"fontHinting": "FULL"}),
    ("hinting-Normal", {"fontHinting": "Normal"}),
    ("subpixel-true", {"subpixel": "true"}),
]


def one(attrs, label, s="Rel 3.14 Wj"):
    a = {"color": INK, "fontSize": "34", "fontFamily": D.UI,
         "foregroundMode": "STROKE", "foregroundColor": CYAN,
         "foregroundStrokeWidth": "3"}
    a.update(attrs)
    inner = el("Text", a, [D.cdata(s)])
    body = [
        el("Container", {"width": 640, "height": 96, "color": "#131C2EFF",
                         "borderRadius": "12"},
           [el("Stack", {"fit": "EXPAND"},
               [el("Positioned", {"left": "14", "top": "10", "width": "612",
                                  "height": "18"},
                   [el("Text", {"text": label, "color": AMBER,
                                "fontSize": "12",
                                "fontFamily": D.MONO})]),
                el("Positioned", {"left": "14", "top": "36", "width": "612",
                                  "height": "50"},
                   [inner])])])]
    return D.snapshot([D.stack(body, 640, 96)], 640, 96, bg=BG)


if __name__ == "__main__":
    rows = []
    for label, attrs in SAMPLES:
        dsl = one(attrs, label)
        r = W.P.probe(dsl, "c09d-%s" % label)
        ok = r.get("ok")
        msg = "" if ok else (r.get("error") or "")[:150].replace("\n", " ")
        print("%-24s %s %s" % (label, "OK " if ok else "FAIL", msg))
        rows.append((label, ok, msg))
    print("\n--- summary ---")
    for label, ok, msg in rows:
        print("%-24s %s" % (label, "accepted" if ok else "rejected"))