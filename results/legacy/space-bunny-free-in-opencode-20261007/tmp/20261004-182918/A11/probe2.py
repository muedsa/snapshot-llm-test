"""A11 probe 2: nested-span line breaking, font features, whitespace metrics.

 P1  nested spans written on ONE source line (no whitespace text nodes)
 P2  nested spans written across source lines (whitespace-only text nodes)
 P3  Raw only for the ' / ' span, one-line source
 P4  fontFeatures="zero" on DejaVu Sans Mono / Inter / Noto Sans Mono CJK SC
 P5  fontFeatures="tnum=2" + letterSpacing on money
 P6  softWrap=false on a literal line
 P7  whitespace metric rig: single vs double vs triple space, same prefix
 P8  full-width colon U+FF1A and ideographic space U+3000 rendering
 P9  long note wrapping with width only (no height)
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A11")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A11")
snapkit.configure("A11", OUT, TMP)

W, H = 1200, 1320
kids = []
y = 20


def cap(t):
    global y
    kids.append(D.el("Positioned", {"left": 24, "top": y, "width": 1150},
                      [D.el("Text", {"color": "#B91C1CFF", "fontSize": 18,
                                     "fontFamily": "Inter"}, [D.cdata(t)])]))
    y += 24


def put(x, yy, w, text, size=28, font="Inter,Noto Sans CJK SC", color="#111827FF", **kw):
    a = {"color": color, "fontSize": size, "fontFamily": font}
    a.update(kw)
    kids.append(D.el("Positioned", {"left": x, "top": yy, "width": w},
                     [D.el("Text", a, [D.cdata(text)])]))


def one(x, yy, w, inner, **kw):
    pa = {"left": x, "top": yy, "width": w}
    pa.update(kw)
    kids.append(D.el("Positioned", pa, [D.el("Text")] if False else [inner]))


cap("P1 nested spans, ONE source line (no whitespace text nodes), no Raw")
one(24, y, 1150, D.el("Text", {"fontSize": 44, "fontFamily": "Inter,Noto Sans CJK SC"}, [
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD"}, [D.cdata("PAID")]),
    D.el("Text", {"color": "#94A3B8FF"}, [D.cdata(" / ")]),
    D.el("Text", {"color": "#0F172AFF"}, [D.cdata("已结算")]),
]))
y += 66

cap("P2 same but source spans multiple lines (whitespace text nodes present)")
one(24, y, 1150, D.el("Text", {"fontSize": 44, "fontFamily": "Inter,Noto Sans CJK SC"}, [
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD"}, [D.cdata("PAID")]),
    D.el("Text", {"color": "#94A3B8FF"}, [D.cdata(" / ")]),
    D.el("Text", {"color": "#0F172AFF"}, [D.cdata("已结算")]),
]))
y += 66

cap("P3 Raw used for the ' / ' span, one source line")
one(24, y, 1150, D.el("Text", {"fontSize": 44, "fontFamily": "Inter,Noto Sans CJK SC"}, [
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD"}, [D.cdata("PAID")]),
    D.el("Raw", {"color": "#94A3B8FF"}, [D.cdata(" / ")]),
    D.el("Text", {"color": "#0F172AFF"}, [D.cdata("已结算")]),
]))
y += 66

cap("P4 fontFeatures=zero : O0-I1-B8 vs A<B&C>D")
put(24, y, 560, "O0-I1-B8  00-I1-B8  O0-l1-B8", font="DejaVu Sans Mono",
    fontFeatures="zero")
y += 44
put(24, y, 560, "O0-I1-B8  00-I1-B8  O0-l1-B8", font="Inter")
y += 44
put(24, y, 700, "O0-I1-B8  00-I1-B8", font="Noto Sans Mono CJK SC",
    fontFeatures="zero")
y += 50

cap("P4b without zero feature, for comparison")
put(24, y, 560, "O0-I1-B8  00-I1-B8  O0-l1-B8", font="DejaVu Sans Mono")
y += 44
put(24, y, 560, "O0-I1-B8  00-I1-B8  O0-l1-B8", font="Inter")
y += 52

cap("P5 tnum + letterSpacing on mono money, right aligned")
put(24, y, 300, "4,215.96", font="DejaVu Sans Mono", textAlign="RIGHT")
put(340, y, 300, "805.50", font="DejaVu Sans Mono", textAlign="RIGHT")
y += 44
put(24, y, 300, "4,215.96", font="DejaVu Sans Mono", textAlign="RIGHT",
    letterSpacing=1.5)
put(340, y, 300, "805.50", font="DejaVu Sans Mono", textAlign="RIGHT",
    letterSpacing=1.5)
y += 52

cap("P6 softWrap=false on literal line A < B & C > D in a 200px box")
put(24, y, 200, "A < B & C > D", softWrap="false")
y += 44
put(24, y, 200, "A < B & C > D")
y += 52

cap("P7 whitespace metric rig: 1 / 2 / 3 spaces after colon, and marker bars")
RIG = "批次： {} A  07"
for n, sp in enumerate([" ", "  ", "   "], start=1):
    put(24, y + n * 0, 700, RIG.format(sp), size=34,
        font="Inter,Noto Sans CJK SC")
    y += 46
y += 8

cap("P8 U+FF1A full width colon and U+3000 ideographic space")
put(24, y, 700, "A：　B  (FF1A then U+3000)")
y += 46

cap("P9 long note wrapping, width only, no height")
put(24, y, 620, "请核对订单编号、货品数量、单价与交付地址；任何修改应保留版本记录。")
y += 84

cap("P10 SKU column: softWrap=false keeps A<B&C>D on one line in a 150px box")
put(24, y, 150, "A<B&C>D", softWrap="false", font="DejaVu Sans Mono")
y += 46

cap("P11 digit/letter confusables in Inter vs DejaVu Sans Mono, big")
put(24, y, 560, "O0-I1-l1 B8", size=40, font="DejaVu Sans Mono")
y += 52

cap("P12 CDATA with trailing/leading content inside Raw at outermost Text")
one(24, y, 1150, D.el("Text", {"fontSize": 30, "fontFamily": "DejaVu Sans Mono"}, [
    D.el("Raw", {"color": "#111827FF"}, [D.cdata("  Path: C:\\work\\cards\\v2  ")]),
]))
y += 60

cap("P13 Outer Text with text= attribute AND nested spans mixed")
one(24, y, 1150, D.el("Text", {"fontSize": 36, "fontFamily": "Inter,Noto Sans CJK SC"}, [
    D.cdata("状态 "),
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD"}, [D.cdata("PAID")]),
    D.el("Raw", {"color": "#94A3B8FF"}, [D.cdata(" / ")]),
    D.el("Text", {"color": "#0F172AFF"}, [D.cdata("已结算")]),
]))
y += 66

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
with open(os.path.join(TMP, "drafts", "probe-v02.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

r = snapkit.render(dsl, "probe-02.png", "probe-02.snapshot", final=False,
                   out_dir=os.path.join(TMP, "preview"))
print("render", r)
print("WARN", D.warnings())