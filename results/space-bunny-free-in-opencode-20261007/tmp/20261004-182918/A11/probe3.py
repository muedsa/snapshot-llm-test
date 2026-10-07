"""A11 probe 3: pin down (a) span text with leading/trailing spaces,
(b) whitespace metrics at large size, (c) confusable glyph fidelity.

 Q1 nested <Text text=" / ">  (attribute form, not a trimmed text node)
 Q2 nested <Raw text=" / ">   (attribute form)
 Q3 outer Text with text= attribute holding the whole rich string (control)
 Q4 whitespace rig at 56px: 1 / 2 / 3 spaces after U+FF1A
 Q5 confusable glyphs at 56px: Inter / DejaVu Sans Mono / Noto Sans Mono CJK SC
      each with and without fontFeatures="zero"
 Q6 CDATA line with a literal ']]'-free backslash path, mono
 Q7 does a nested span keep internal double spaces?
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

W, H = 1200, 1200
kids = []
y = 16


def cap(t, yy=None):
    global y
    kids.append(D.el("Positioned", {"left": 16, "top": yy if yy is not None else y,
                                    "width": 1180},
                      [D.el("Text", {"color": "#B91C1CFF", "fontSize": 17,
                                     "fontFamily": "Inter"}, [D.cdata(t)])]))
    if yy is None:
        y += 22


def one(x, yy, w, inner):
    kids.append(D.el("Positioned", {"left": x, "top": yy, "width": w}, [inner]))


def put(x, yy, w, text, size=28, font="Inter,Noto Sans CJK SC", color="#111827FF", **kw):
    a = {"color": color, "fontSize": size, "fontFamily": font}
    a.update(kw)
    kids.append(D.el("Positioned", {"left": x, "top": yy, "width": w},
                     [D.el("Text", a, [D.cdata(text)])]))


UI = "Inter,Noto Sans CJK SC"

cap("Q1 nested span with text= attribute holding ' / '  (expect PAID / 已结算 on one line)")
one(16, y, 1100, D.el("Text", {"fontSize": 44, "fontFamily": UI}, [
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD", "text": "PAID"}),
    D.el("Text", {"color": "#94A3B8FF", "text": " / "}),
    D.el("Text", {"color": "#0F172AFF", "text": "已结算"}),
]))
y += 62

cap("Q2 nested <Raw text=\" / \"> attribute form")
one(16, y, 1100, D.el("Text", {"fontSize": 44, "fontFamily": UI}, [
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD", "text": "PAID"}),
    D.el("Raw", {"color": "#94A3B8FF", "text": " / "}),
    D.el("Text", {"color": "#0F172AFF", "text": "已结算"}),
]))
y += 62

cap("Q3 whole string as one CDATA text node (control, single colour)")
put(16, y, 1100, "PAID / 已结算", size=44)
y += 62

cap("Q4 whitespace rig at 56px: rows are 1 / 2 / 3 spaces after the colon")
for i, sp in enumerate([" ", "  ", "   "], start=1):
    put(16, y + (i - 1) * 0, 900, "批次：%sA  07" % sp, size=56, font=UI)
    y += 74
y += 10

cap("Q5 confusable glyphs 56px")
put(16, y, 900, "O0-I1-B8  O0-l1-B8  00-I1-B8", size=56, font="Inter")
y += 70
put(16, y, 900, "O0-I1-B8  O0-l1-B8  00-I1-B8", size=56, font="Inter",
    fontFeatures="zero")
y += 70
put(16, y, 900, "O0-I1-B8  O0-l1-B8  00-I1-B8", size=56, font="DejaVu Sans Mono")
y += 70
put(16, y, 900, "O0-I1-B8  O0-l1-B8  00-I1-B8", size=56, font="DejaVu Sans Mono",
    fontFeatures="zero")
y += 70
put(16, y, 900, "O0-I1-B8  O0-l1-B8  00-I1-B8", size=56,
    font="Noto Sans Mono CJK SC")
y += 70
put(16, y, 900, "O0-I1-B8  O0-l1-B8  00-I1-B8", size=56,
    font="Noto Sans Mono CJK SC", fontFeatures="zero")
y += 84

cap("Q6 mono literal line with backslashes and angle brackets")
put(16, y, 900, "Path: C:\\work\\cards\\v2", size=40,
    font="DejaVu Sans Mono,Noto Sans Mono CJK SC")
y += 54
put(16, y, 900, "A < B & C > D", size=40,
    font="DejaVu Sans Mono,Noto Sans Mono CJK SC")
y += 62

cap("Q7 nested span keeping internal double spaces (text= attribute)")
one(16, y, 1100, D.el("Text", {"fontSize": 40, "fontFamily": "DejaVu Sans Mono"}, [
    D.el("Text", {"color": "#111827FF", "text": "批次：  A  07"}),
]))
y += 58

cap("Q8 wordSpacing alternative for the slash span")
one(16, y, 1100, D.el("Text", {"fontSize": 44, "fontFamily": UI}, [
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD", "text": "PAID",
                  "wordSpacing": 13}),
    D.el("Text", {"color": "#94A3B8FF", "text": "/", "wordSpacing": 13}),
    D.el("Text", {"color": "#0F172AFF", "text": "已结算"}),
]))
y += 62

cap("Q9 mixed: outer CDATA prefix text node + nested spans (one source line)")
one(16, y, 1100, D.el("Text", {"fontSize": 40, "fontFamily": UI}, [
    D.cdata("状态"),
    D.el("Text", {"color": "#15803DFF", "fontStyle": "BOLD", "text": " PAID "}),
    D.el("Text", {"color": "#94A3B8FF", "text": "/"}),
    D.el("Text", {"color": "#0F172AFF", "text": " 已结算"}),
]))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
with open(os.path.join(TMP, "drafts", "probe-v03.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "probe-03.png", "probe-03.snapshot", final=False,
                   out_dir=os.path.join(TMP, "preview"))
print("render", r)
print("WARN", D.warnings())