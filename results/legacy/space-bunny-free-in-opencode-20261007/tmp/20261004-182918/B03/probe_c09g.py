"""B03 case-09 · Raw whitespace isolation.

probe-c09c cell 3 rendered NOTHING for `<Text><Raw>   Raw   </Raw></Text>` while
`<Text text="   Text   ">` rendered "Text" flush left. Cell 2 proved Raw keeps
inner indentation. So: which leading whitespace does Raw actually keep?
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el = D.el
BG = "#0B1020FF"
PANEL = "#131C2EFF"
INK = "#EAF2FBFF"
AMBER = "#FBBF24FF"
CYAN = "#67E8F9FF"
GRN = "#34D399FF"

CASES = [
    ("A · Text 属性形式，前导 3 空格 + 尾随 3 空格",
     lambda: el("Text", {"text": "   A   ", "color": INK, "fontSize": "18",
                         "fontFamily": D.MONO})),
    ("B · Text 内只有 Raw，整段带首尾空格",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Raw", {}, [D.cdata("   B   ")])])),
    ("C · Raw 首字符非空格",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Raw", {}, [D.cdata("x   C")])])),
    ("D · Raw 先换行再缩进",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Raw", {}, [D.cdata("  \n   D")])])),
    ("E · Raw 三行缩进递增",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Raw", {}, [D.cdata("line1\n    line2\n        line3")])])),
    ("F · Text>Raw 前后夹普通 Text",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Text", {}, [D.cdata("前")]),
                 el("Raw", {}, [D.cdata("   F   ")]),
                 el("Text", {}, [D.cdata("后")])])),
    ("G · Text 内嵌 <Text> 带前导空格",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Text", {}, [D.cdata("   G   ")])])),
    ("H · Raw 里用全角空格 U+3000",
     lambda: el("Text", {"color": INK, "fontSize": "18",
                         "fontFamily": D.MONO},
                [el("Raw", {}, [D.cdata("　　H　　")])])),
]

CW, CH = 1500, 760
X0, Y0 = 40, 96
CWID, CHGT, RPIT = 700, 150, 160


def build():
    k = [el("Positioned", {"left": "40", "top": "22", "width": "1400",
                           "height": "28"},
            [el("Text", {"text": "PROBE c09g · Raw 到底保留哪一种空白",
                         "color": INK, "fontSize": "20",
                         "fontFamily": D.UI, "fontStyle": "BOLD"})]),
           el("Positioned", {"left": "40", "top": "54", "width": "1400",
                             "height": "20"},
            [el("Text", {"text": "每格左侧有一条 1px 的青色竖线作为左对齐基准。",
                         "color": "#9DB4CCFF", "fontSize": "13",
                         "fontFamily": D.UI})])]
    for i, (label, mk) in enumerate(CASES):
        cx = X0 + (i % 2) * (CWID + 20)
        cy = Y0 + (i // 2) * RPIT
        k.append(el("Positioned",
                    {"left": str(cx), "top": str(cy), "width": str(CWID),
                     "height": str(CHGT)},
                    [el("Container", {"width": str(CWID), "height": str(CHGT),
                                      "color": PANEL, "borderRadius": "12"})]))
        k.append(el("Positioned",
                    {"left": str(cx + 12), "top": str(cy + 10),
                     "width": str(CWID - 24), "height": "18"},
                    [el("Text", {"text": label, "color": AMBER,
                                 "fontSize": "11", "fontFamily": D.MONO})]))
        k.append(el("Positioned",
                    {"left": str(cx + 12), "top": str(cy + 32), "width": "2",
                     "height": str(CHGT - 44)},
                    [el("Container", {"width": "2", "height": str(CHGT - 44),
                                      "color": CYAN})]))
        k.append(el("Positioned",
                    {"left": str(cx + 14), "top": str(cy + 40),
                     "width": str(CWID - 28), "height": str(CHGT - 56)},
                    [mk()]))
    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.probe(dsl, "c09g-rawspace")
    print("  probe-c09g", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:200])


if __name__ == "__main__":
    build()