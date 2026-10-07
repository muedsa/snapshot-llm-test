"""Probe 04 (v2): text capabilities, laid out without collisions.

v1 overlapped badly so several readings were ambiguous. This version gives
every case its own row and keeps total height generous.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1560, 2100
k = []
Y = [40]


def sec(title, note=""):
    k.append(D.text_el(title, x=40, y=Y[0], size=15, color="#7DD3FCFF",
                       w=1000, h=22, style="BOLD"))
    if note:
        k.append(D.text_el(note, x=40, y=Y[0] + 22, size=11,
                           color="#64748BFF", w=1400, h=16))
    Y[0] += 46 if note else 28


def T(x, y, s, size=26, **kw):
    kw.setdefault("color", "#F8FAFCFF")
    ls = kw.get("ls", 0) or 0
    w = kw.pop("w", None) or (D.est_width(s, size) + ls * max(0, len(s) - 1) + 24)
    kw.setdefault("h", size * 1.5)
    k.append(D.text_el(s, x=x, y=y, size=size, w=w, **kw))


# ---------- 1. letterSpacing, measured against a predicted end rule ----------
sec("1 · letterSpacing + wordSpacing (rules mark the predicted text end x)")
S = "Hamburggefonstiv 123"
base_w = D.est_width(S, 26)
for ls in [-5, -2, 0, 2, 5, 10]:
    yy = Y[0]
    k.append(D.box(80, yy + 4, 2, 34, color="#475569FF"))
    T(120, yy, S, size=26, ls=ls)
    pred = 120 + base_w + ls * (len(S) - 1)
    k.append(D.box(pred, yy + 4, 2, 34, color="#F43F5EFF"))
    k.append(D.text_el("ls=%s   predicted end x=%.0f" % (ls, pred), x=900,
                       y=yy + 8, size=12, color="#94A3B8FF", w=340, h=16))
    Y[0] = yy + 40
T(120, Y[0], "one two three four", size=24, word_spacing=14)
k.append(D.text_el("wordSpacing=14 (compare next line)", x=900, y=Y[0] + 8,
                   size=12, color="#94A3B8FF", w=340, h=16))
Y[0] += 38
T(120, Y[0], "one two three four", size=24)
k.append(D.text_el("control, no wordSpacing", x=900, y=Y[0] + 8, size=12,
                   color="#94A3B8FF", w=340, h=16))
Y[0] += 48

# ---------- 2. fontFeatures ----------
sec("2 · fontFeatures on DejaVu Sans Mono (digits + 'fi') and Inter",
    "mono font so tnum/pnum effects are visible as glyph shape changes")
FEAT = ["NONE", "+tnum", "tnum=2", "+pnum", "+zero", "+frac", "+smcp",
        "smcp[2:8]", "-liga", "+liga", "-kern", "+dlig"]
for i, f in enumerate(FEAT):
    col, row = i % 3, i // 3
    x = 60 + col * 500
    yy = Y[0] + row * 62
    T(x, yy, "0123456789 fi", size=28, font=D.MONO, features=f)
    T(x + 300, yy + 6, "Sans 123", size=24, font=D.LATIN, features=f)
    k.append(D.text_el(f, x=x, y=yy + 36, size=11, color="#7DD3FCFF",
                       font=D.MONO, w=300, h=16))
Y[0] += ((len(FEAT) + 2) // 3) * 62 + 30

# ---------- 3. inline composition ----------
sec("3 · nested Text spans / WidgetSpan / Raw / CDATA")
y = Y[0]
k.append(D.el("Positioned", {"left": 60, "top": y, "width": 1400,
                             "height": 58},
              [D.el("Text", {"color": "#F8FAFCFF", "fontSize": 30,
                             "fontFamily": D.UI}, [
                  D.el("Text", {"text": "前置 "}),
                  D.el("Text", {"color": "#38BDF8FF", "fontSize": 30},
                       [D.cdata("嵌套 Span 变蓝")]),
                  D.el("Text", {"text": " 后置仍白"})])]))
k.append(D.text_el("nested Text span overrides colour, inherits the rest",
                   x=60, y=y + 62, size=11, color="#64748BFF", w=700, h=16))
y += 88
badge = D.el("ClipRRect", {"borderRadius": "6", "clipBehavior": "ANTI_ALIAS"},
             [D.el("Container", {"width": 86, "height": 26,
                                 "color": "#F59E0BFF"},
                   [D.el("Text", {"text": "v2.4", "fontSize": 14,
                                  "color": "#0B1020FF",
                                  "fontFamily": D.MONO})])])
k.append(D.el("Positioned", {"left": 60, "top": y, "width": 1400,
                             "height": 58},
              [D.el("Text", {"color": "#F8FAFCFF", "fontSize": 30,
                             "fontFamily": D.UI}, [
                  D.el("Text", {"text": "发布 "}),
                  D.el("WidgetSpan", {"alignment": "MIDDLE"}, [badge]),
                  D.el("Text", {"text": " 状态 "}),
                  D.el("WidgetSpan", {"alignment": "BASELINE",
                                      "baseline": "ALPHABETIC"},
                       [D.el("Container", {"width": 18, "height": 18,
                                           "color": "#34D399FF",
                                           "borderRadius": "3"})]),
                  D.el("Text", {"text": " 绿色块按基线对齐"})])]))
k.append(D.text_el("WidgetSpan: MIDDLE badge and BASELINE square inline",
                   x=60, y=y + 62, size=11, color="#64748BFF", w=700, h=16))
y += 88
k.append(D.el("Positioned", {"left": 60, "top": y, "width": 1400,
                             "height": 46},
              [D.el("Text", {"color": "#F8FAFCFF", "fontSize": 24,
                             "fontFamily": D.MONO}, [
                  D.el("Text", {"text": "Text:"}),
                  D.el("Text", {"text": "[ 压掉两端空白 ]"}),
                  D.el("Text", {"text": "   Raw:"}),
                  D.el("Raw", {}, [D.cdata("[  保留两端空白  ]")])])]))
k.append(D.text_el("plain Text trims; Raw keeps leading and trailing spaces",
                   x=60, y=y + 48, size=11, color="#64748BFF", w=700, h=16))
y += 76
k.append(D.el("Positioned", {"left": 60, "top": y, "width": 1400,
                             "height": 46},
              [D.el("Text", {"color": "#7DD3FCFF", "fontSize": 24,
                             "fontFamily": D.MONO},
                    [D.cdata("<Container color=#FF0000> & a < b > c")])]))
k.append(D.text_el("CDATA prints literal < > & (parser does not decode "
                   "entities)", x=60, y=y + 48, size=11, color="#64748BFF",
                   w=800, h=16))
Y[0] = y + 84

# ---------- 4. decoration / shadow / stroke text ----------
sec("4 · decoration, textShadow, foreground paint modes")
DECOS = [("UNDERLINE", None, None, None),
         ("LINE_THROUGH", "#F87171FF", 5, None),
         ("OVERLINE", "#34D399FF", 3, None),
         ("UNDERLINE", "#38BDF8FF", 3, "DOUBLE"),
         ("UNDERLINE", "#38BDF8FF", 3, "DOTTED"),
         ("UNDERLINE", "#38BDF8FF", 3, "DASHED"),
         ("UNDERLINE", "#38BDF8FF", 3, "WAVY")]
for i, (d, dc, dt, ls) in enumerate(DECOS):
    col, row = i % 2, i // 2
    x = 60 + col * 720
    yy = Y[0] + row * 76
    extra = {"decorationLineStyle": ls} if ls else {}
    T(x, yy, "装饰 %s" % d, size=30, decorate=d, deco_color=dc,
      deco_thick=dt, extra=extra)
    k.append(D.text_el("%s%s%s" % (d, " thick=%s" % dt if dt else "",
                                   " style=%s" % ls if ls else ""),
                       x=x + 380, y=yy + 10, size=11, color="#7DD3FCFF",
                       w=330, h=16))
Y[0] += ((len(DECOS) + 1) // 2) * 76 + 24
T(60, Y[0], "带阴影的标题", size=34,
  shadow="5 6 3 #000000CC,-3 2 #F59E0BCC")
k.append(D.text_el('textShadow="5 6 3 #000000CC,-3 2 #F59E0BCC"', x=520,
                   y=Y[0] + 10, size=11, color="#7DD3FCFF", w=500, h=16))
Y[0] += 56
T(60, Y[0], "OUTLINE", size=40, style="BOLD",
  extra={"foregroundColor": "#38BDF8FF", "foregroundMode": "STROKE",
         "foregroundStrokeWidth": 1.8, "foregroundAntiAlias": "true",
         "foregroundStrokeJoin": "ROUND", "foregroundStrokeCap": "ROUND"})
k.append(D.text_el("foregroundMode=STROKE strokeWidth=1.8 (hollow glyphs)",
                   x=520, y=Y[0] + 14, size=11, color="#7DD3FCFF", w=500,
                   h=16))
T(980, Y[0], "FILLED", size=40, style="BOLD",
  extra={"foregroundColor": "#F59E0BFF", "foregroundMode": "FILL"})
k.append(D.text_el("foregroundMode=FILL", x=980, y=Y[0] + 52, size=11,
                   color="#7DD3FCFF", w=300, h=16))
Y[0] += 84

# ---------- 5. paragraph behaviour ----------
sec("5 · paragraph: height vs maxLines vs overflow",
    "same 4-line CJK string in every cell; only the named attributes differ")
LONG = ("这段中文用于验证多行排版与截断行为。Snapshot 的 Text 在固定高度装不下时会静默丢弃"
        "溢出部分，而 maxLines 配合 overflow 才会出现省略号。这是第一行第二行第三行第四行。")
CASES = [
    ("h=30 (one line height)", dict(h=30)),
    ("no height attr (auto)", dict()),
    ("maxLines=2 overflow=ELLIPSIS", dict(max_lines=2,
                                         extra={"overflow": "ELLIPSIS"})),
    ("maxLines=2 overflow=CLIP", dict(max_lines=2)),
    ("maxLines=2 overflow=FADE", dict(max_lines=2,
                                       extra={"overflow": "FADE"})),
    ("softWrap=false", dict(extra={"softWrap": "false"})),
    ("lineHeight=1.9", dict(extra={"lineHeight": 1.9})),
    ("textAlign=CENTER", dict(align="CENTER")),
    ("textWidthBasis=LONGESTLINE", dict(extra={"textWidthBasis": "LONGESTLINE"})),
]
for i, (lab, kw) in enumerate(CASES):
    yy = Y[0] + i * 78
    kw = dict(kw)
    w = kw.pop("w", 700)
    h = kw.pop("h", None)
    k.append(D.el("Positioned", {"left": 60, "top": yy, "width": w,
                                 "height": h or 120},
                  [D.el("Text", dict({"color": "#F8FAFCFF", "fontSize": 22,
                                      "fontFamily": D.CJK}, **kw),
                        [D.cdata(LONG)])]))
    k.append(D.box(780, yy - 4, 700, (h or 120) + 4, color=None,
                   border="1 SOLID #334155FF"))
    k.append(D.text_el(lab, x=790, y=yy + 4, size=12, color="#7DD3FCFF",
                       w=680, h=18))
Y[0] += len(CASES) * 78 + 20

# ---------- 6. baseline / strut / style ----------
sec("6 · baselineMode, strut*, fontStyle, backgroundColor")
for i, bs in enumerate(["ALPHABETIC", "IDEOGRAPHIC"]):
    yy = Y[0] + i * 46
    T(60, yy, "基线 Baseline %s 汉字" % bs, size=26, baseline=bs,
      font=D.LATIN + "," + D.CJK)
    k.append(D.text_el("baselineMode=%s" % bs, x=620, y=yy + 8, size=11,
                       color="#7DD3FCFF", w=300, h=16))
Y[0] += 100
for i, st in enumerate(["NORMAL", "BOLD", "ITALIC", "BOLD_ITALIC"]):
    col, row = i % 2, i // 2
    x = 60 + col * 700
    yy = Y[0] + row * 50
    T(x, yy, "Style %s Handgloves" % st, size=28, style=st)
    k.append(D.text_el("fontStyle=%s" % st, x=x + 420, y=yy + 9, size=11,
                       color="#7DD3FCFF", w=300, h=16))
Y[0] += 110
yy = Y[0]
T(60, yy, "有 strut 的两行文字", size=26,
  extra={"strutEnabled": "true", "strutFontSize": 34, "strutHeight": 2.2})
k.append(D.text_el("strutFontSize=34 strutHeight=2.2", x=620, y=yy + 6,
                   size=11, color="#7DD3FCFF", w=400, h=16))
T(900, yy, "有 strut 的两行文字", size=26)
k.append(D.text_el("control: identical string, no strut", x=900, y=yy + 46,
                   size=11, color="#7DD3FCFF", w=400, h=16))
Y[0] = yy + 100
T(60, Y[0], "高亮背景文字", size=30, bg="#F59E0B44")
k.append(D.text_el("backgroundColor=#F59E0B44", x=620, y=Y[0] + 10, size=11,
                   color="#7DD3FCFF", w=400, h=16))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p04b-text")
print("probe04b", r.get("ok"), r.get("status"), r.get("error"))
for wn in D.warnings():
    print("WARN", wn)