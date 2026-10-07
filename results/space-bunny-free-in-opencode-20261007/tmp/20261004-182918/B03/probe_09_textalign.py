"""Probe 09: exact semantics of textAlign=RIGHT inside a positioned box.

case-03 v1 showed two right-aligned labels ending ~24 px past the right edge
of their own Positioned box, while other right-aligned labels landed exactly.
This probe varies one thing at a time (parent type, Positioned width present,
font family) and measures where the ink actually ends.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wlib as W  # noqa: E402

D = W.D
el = W.el

Wc, Hc = 1240, 700
BG = "#FFFFFF"
k = [W.t2("PROBE 09 · textAlign=RIGHT 的实际落点", 40, 20, size=19,
          color="#0F172AFF", style="BOLD", w=800, h=26),
     W.t2("每行右侧的红线 = 该 Positioned 框的右边界；灰线 = 其父容器右边界。"
          "文字若压过红线，说明 width 没被采纳。", 40, 48, size=12,
          color="#475569FF", w=1100, h=18)]

CASES = []
PARENT_W = 420
BOX_L, BOX_W = 120, 200


def case(i, label, parent_dsl, note=""):
    """parent(kids_left_marker) -> returns the Container/Stack string"""
    y = 90 + i * 76
    frame = []
    # parent boundary (grey) and box boundary (red)
    frame.append(W.box(40, y, PARENT_W, 60, color="#F1F5F9FF", radius=8))
    frame.append(W.box(40 + PARENT_W, y - 4, 1.5, 68, color="#94A3B8FF"))
    frame.append(W.box(40 + BOX_L + BOX_W, y - 4, 1.5, 68, color="#EF4444FF"))
    frame.append(el("Positioned", {"left": "40", "top": str(y),
                                "width": str(PARENT_W), "height": "60"},
                       [parent_dsl]))
    frame.append(W.t2(label, 40, y + 62, size=11, color="#0F172AFF", w=460,
                      h=16))
    if note:
        frame.append(W.t2(note, 520, y + 62, size=10, color="#64748BFF",
                          w=680, h=14))
    k.extend(frame)


def txt(**kw):
    a = {"color": "#0F172AFF", "fontSize": "20", "fontFamily": D.MONO,
         "textAlign": "RIGHT", "text": "已拣 2"}
    a.update(kw)
    return el("Text", a)


def pos(children, w=BOX_W):
    return el("Positioned", {"left": str(BOX_L), "top": "10",
                             "width": str(w), "height": "40"}, [children])


case(0, "A Stack(EXPAND) + Positioned(width=200)", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"}, [pos(txt())])]),
    "parent 420, box 120..320")
case(1, "B Stack(EXPAND) + Positioned 无 width", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"},
        [el("Positioned", {"left": str(BOX_L), "top": "10", "height": "40"},
           [txt()])])]),
    "对照组：不写 width")
case(2, "C Stack(LOOSE) + Positioned(width=200)", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "LOOSE"}, [pos(txt())])]),
    "LOOSE 下 Stack 收缩")
case(3, "D Stack(EXPAND) + Positioned(right=40,width=200)", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"},
        [el("Positioned", {"right": "40", "top": "10", "width": "200",
                            "height": "40"}, [txt()])])]),
    "right 定位时是否同样丢 width")
case(4, "E Stack(EXPAND) + Positioned(width) + 兄弟节点", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"},
        [pos(txt()),
         el("Positioned", {"left": "0", "top": "0", "width": "8",
                           "height": "60"},
            [el("Container", {"width": "8", "height": "60",
                              "color": "#22C55EFF"})])])]),
    "多一个兄弟是否影响")
case(5, "F 同一位置换 Inter+Noto 字体", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"},
        [pos(txt(fontFamily=D.UI))])]),
    "字体回退是否影响右对齐")
case(6, "G 纯拉丁 DejaVu Sans Mono", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"},
        [pos(txt(text="23 / 41"))])]),
    "排除 CJK 宽度因素")
case(7, "H CJK 文本 + Inter,Noto Sans CJK SC", el(
    "Container", {"width": str(PARENT_W), "height": "60"},
    [el("Stack", {"fit": "EXPAND"},
        [pos(txt(text="需 6 箱", fontFamily=D.UI))])]),
    "同 F 但含中文与空格")

dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=BG)
r = W.P.probe(dsl, "p09-textalign-right")
print("probe09", r.get("ok"), r.get("status"), (r.get("error") or "")[:160])

if r.get("ok"):
    from PIL import Image
    im = Image.open(r["image"]).convert("RGB")
    px = im.load()
    for i in range(8):
        y = 90 + i * 76
        best = None
        for yy in range(y + 4, y + 56):
            for xx in range(60 + BOX_L, 60 + PARENT_W):
                p = px[xx, yy]
                if p[0] < 90 and p[1] < 90 and p[2] < 100:
                    if best is None or xx > best:
                        best = xx
        box_right = 40 + BOX_L + BOX_W
        par_right = 40 + PARENT_W
        tag = "?"
        if best is not None:
            if abs(best - box_right) <= 4:
                tag = "AT BOX RIGHT (correct)"
            elif abs(best - par_right) <= 8:
                tag = "AT PARENT RIGHT (width ignored)"
            else:
                tag = "other"
        print("  row %d ink_right=%s box_right=%d parent_right=%d -> %s"
              % (i, best, box_right, par_right, tag))