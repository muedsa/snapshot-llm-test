"""B03 case-09 · line-height diagnostic.

probe-c09b rendered three cells completely EMPTY even though the service
returned 200:
  * strutEnabled/strutHeight/strutLeading/strutFontSize
  * height="18"  (Text line height)
  * height="38"
while topRatio DID render. The handbook already records a "Text renders nothing
when the box is too short" trap; this isolates which attribute triggers it.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el = D.el
INK = "#111827FF"
INK2 = "#374151FF"
BG = "#E5E7EBFF"

CASES = [
    ("控制组 · 不给 height/strut", {}),
    ("height=18 fontSize=17", {"height": "18"}),
    ("height=26 fontSize=17", {"height": "26"}),
    ("height=40 fontSize=17", {"height": "40"}),
    ("height=60 fontSize=17", {"height": "60"}),
    ("strut 全套（无 height）", {"strutEnabled": "true", "strutHeight": "46",
                                "strutLeading": "16", "strutFontSize": "22",
                                "strutFontFamily": D.UI}),
    ("strutEnabled+strutFontSize", {"strutEnabled": "true",
                                    "strutFontSize": "22",
                                    "strutFontFamily": D.UI}),
    ("strutHeightForced=true", {"strutEnabled": "true",
                                "strutHeightForced": "true",
                                "strutHeight": "46", "strutFontSize": "22",
                                "strutFontFamily": D.UI}),
    ("height=18 + maxLines=1", {"height": "18", "maxLines": "1"}),
    ("height=18 + overflow=ELLIPSIS", {"height": "18",
                                       "overflow": "ELLIPSIS"}),
    ("wordSpacing=16 单独", {"wordSpacing": "16"}),
    ("topRatio=0.5", {"topRatio": "0.5"}),
    ("topRatio=1.4", {"topRatio": "1.4"}),
    ("height=18 + strutEnabled", {"height": "18", "strutEnabled": "true",
                                  "strutFontSize": "22"}),
    ("strutEnabled 单独", {"strutEnabled": "true"}),
    ("strutLeading=16 单独", {"strutLeading": "16"}),
    ("strutHeight=46 单独", {"strutHeight": "46"}),
    ("strutEnabled+strutHeight=46", {"strutEnabled": "true",
                                     "strutHeight": "46"}),
    ("strutHeight=46+strutLeading=0", {"strutHeight": "46",
                                       "strutLeading": "0"}),
    ("strutHeightOverridden=true", {"strutEnabled": "true",
                                    "strutHeightOverridden": "true",
                                    "strutHeight": "46"}),
    ("height=100（远大于字号）", {"height": "100"}),
]

CW, CH = 1480, 1480
COLS, CWID, CHGT, RPIT = 2, 700, 116, 128
X0, Y0 = 40, 108


def build():
    kids = [el("Positioned", {"left": "40", "top": "24", "width": "1400",
                             "height": "28"},
               [el("Text", {"text": "PROBE c09e · Text 的 height / strut / topRatio",
                            "color": "#111827FF", "fontSize": "20",
                            "fontFamily": D.UI, "fontStyle": "BOLD"})]),
              el("Positioned", {"left": "40", "top": "56", "width": "1400",
                               "height": "20"},
                 [el("Text", {"text": "每一格左侧先放一个 1.05em 的色条，"
                                      "再放同一个 Text（两行「行一 行二」）",
                              "color": "#374151FF", "fontSize": "13",
                              "fontFamily": D.UI})])]
    for i, (label, attrs) in enumerate(CASES):
        cx = X0 + (i % COLS) * (CWID + 20)
        cy = Y0 + (i // COLS) * RPIT
        kids.append(el("Positioned",
                       {"left": str(cx), "top": str(cy),
                        "width": str(CWID), "height": str(CHGT)},
                       [el("Container",
                           {"width": str(CWID), "height": str(CHGT),
                            "color": "#FFFFFFFF", "borderRadius": "12",
                            "border": "1 SOLID #D1D5DBFF"})]))
        kids.append(el("Positioned",
                       {"left": str(cx + 14), "top": str(cy + 10),
                        "width": str(CWID - 28), "height": "18"},
                       [el("Text", {"text": label, "color": "#B91C1CFF",
                                    "fontSize": "12",
                                    "fontFamily": D.MONO})]))
        base = {"color": INK2, "fontSize": "17", "fontFamily": D.UI}
        base.update(attrs)
        inner = el("Text", dict(base),
                   [el("Text", {}, [D.cdata("行一 ")]),
                    el("Text", {"color": "#2563EBFF"},
                       [D.cdata("行二 ")]),
                    el("Text", {}, [D.cdata("行三")])])
        kids.append(el("Positioned",
                       {"left": str(cx + 14), "top": str(cy + 34),
                        "width": str(CWID - 28), "height": "70"}, [inner]))
    dsl = D.snapshot([D.stack(kids, CW, CH)], CW, CH, bg=BG)
    r = W.P.probe(dsl, "c09e-lineheight")
    print("  probe-c09e", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:200])
    # second panel: Stack fit EXPAND stretches non-Positioned children
    k2 = [el("Positioned", {"left": "40", "top": "30", "width": "1400",
                            "height": "24"},
             [el("Text", {"text": "同一张 Stack 里，fit=EXPAND（上面那张）会给"
                                   "非 Positioned 子节点紧约束 → 它的 width/height 被忽略，"
                                   "整块被拉成满屏。fit=LOOSE（下面这张）才按自身尺寸画。",
                          "color": "#111827FF", "fontSize": "14",
                          "fontFamily": D.UI})])]
    for j, fit in enumerate(["EXPAND", "LOOSE", "PASSTHROUGH"]):
        yy = 90 + j * 130
        k2.append(el("Positioned", {"left": "60", "top": str(yy),
                                   "width": "460", "height": "110"},
                     [el("Stack", {"fit": fit, "alignment": "TOP_LEFT",
                                   "clipBehavior": "HARD_EDGE"},
                         [el("Container", {"width": "460", "height": "110",
                                           "color": "#FFFFFF00",
                                           "border": "2 SOLID #9CA3AFFF",
                                           "alignment": "BOTTOM_RIGHT"},
                             [el("Text", {"text": "Stack 460x110",
                                          "color": "#6B7280FF",
                                          "fontSize": "12",
                                          "fontFamily": D.MONO})]),
                          el("Container", {"width": "300", "height": "110",
                                           "color": "#DC2626FF"})])]))
        k2.append(el("Positioned", {"left": "560", "top": str(yy + 40),
                                    "width": "200", "height": "30"},
                     [el("Text", {"text": fit, "color": "#111827FF",
                                  "fontSize": "18",
                                  "fontFamily": D.MONO})]))
        k2.append(el("Positioned", {"left": "790", "top": str(yy + 40),
                                    "width": "660", "height": "30"},
                     [el("Text", {"text": "fit=%s → 红色非定位 Container(300x110)"
                                           " 实际尺寸见红色块" % fit,
                                  "color": "#111827FF", "fontSize": "13",
                                  "fontFamily": D.MONO})]))
    k2.append(el("Positioned", {"left": "60", "top": "470", "width": "1380",
                                "height": "22"},
                 [el("Text", {"text": "结论：Stack 自己也遵守「矩形要包在Positioned 里」"
                                       "这条约定 —— fit=EXPAND 会给非定位子节点紧约束，"
                                       "它的 width/height 被忽略并拉满 Stack。",
                              "color": "#B91C1CFF", "fontSize": "14",
                              "fontFamily": D.UI})]))
    dsl2 = D.snapshot([D.stack(k2, CW, 510)], CW, 510, bg="#F3F4F6FF")
    r2 = W.P.probe(dsl2, "c09f-stackfit")
    print("  probe-c09f", r2.get("ok"), r2.get("status"),
          (r2.get("error") or "")[:200])


if __name__ == "__main__":
    build()