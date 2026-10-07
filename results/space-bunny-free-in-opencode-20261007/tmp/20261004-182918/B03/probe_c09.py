"""B03 case-09 capability probes: the typography / rich-text frontier.

Three grids, each cell changes exactly one thing.

  probe-c09a-fontfeat : fontFeatures x fontFamily  (does OpenType switching do
                        ANYTHING on the fonts this service actually has?)
  probe-c09b-paint    : foreground paint (FILL / STROKE / STROKE_AND_FILL),
                        stroke join/cap, textShadow, decoration*LineStyle +
                        decorationGaps, strut*, letterSpacing / wordSpacing /
                        height / topRatio
  probe-c09c-inline   : nested <Text> spans, <Raw> whitespace, <WidgetSpan>
                        placeholder alignment + baseline, CDATA vs plain text
                        attribute, multi-font families, maxLines/ELLIPSIS,
                        softWrap, textAlign, textDirection RTL

Enum discovery (probe_c09_enum.py) established the valid value sets used here:
  PaintStrokeCap   = BUTT | ROUND | SQUARE          (NO BEVEL)
  PaintStrokeJoin  = MITER | ROUND | BEVEL
  textHeightMode   = nothing I tried is accepted     (see technique-notes)
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
INK2 = "#9DB4CCFF"
INK3 = "#6B829AFF"
LINE = "#22344AFF"
AMBER = "#FBBF24FF"
CYAN = "#67E8F9FF"
ROSE = "#FB7185FF"
VIO = "#A78BFAFF"
GRN = "#34D399FF"
LIME = "#BEF264FF"


def tx(s, x, y, w, h, size=16, color=INK, font=D.UI, **extra):
    a = {"color": color, "fontSize": size, "fontFamily": font}
    a.update(extra)
    return el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                             "width": round(w, 2), "height": round(h, 2)},
              [el("Text", a, [D.cdata(s)])])


def head(cw, title, sub):
    return [tx(title, 40, 20, cw - 80, 30, size=21, color=INK, style="BOLD"),
            tx(sub, 40, 54, cw - 80, 20, size=12, color=INK2),
            tx("tmp/B03/probes/  ·  每格只改一处", 40, 76, cw - 80, 18,
               size=11, color=INK3, font=D.MONO)]


# ------------------------------------------------------------------ probe A
FEATS = ["(不写)", "tnum=1", "onum", "zero", "smcp", "ss01", "liga", "-liga",
         "kern", "-kern", "dlig", "calt", "frac", "sups", "ss02", "ss04"]
FONTS = ["Inter", "DejaVu Sans Mono", "DejaVu Serif"]
SAMPLE = "0123 abfi 3.14"


def probe_a():
    cw, ch = 1500, 820
    x0 = 246
    cwid, cpit = 148, 154
    hdr, rh = 22, 76
    y = 118
    k = head(cw, "PROBE c09a · fontFeatures × fontFamily",
             "官方文档说 fontFeatures 形如 “+liga -kern tnum=2 smcp[2:8]”。"
             "这里对 16 组特性 × 3 种字体逐格渲染，看服务里实际装的字体到底带不带这些特性。")
    for fnt in FONTS:
        fs = 14 if "Mono" in fnt else 17
        for grp in range(2):
            for j in range(8):
                f = FEATS[grp * 8 + j]
                x = x0 + j * cpit
                k.append(tx(f, x, y, cwid, 18, size=12,
                            color=AMBER if j == 0 else CYAN, font=D.MONO))
            yy = y + hdr
            for j in range(8):
                f = FEATS[grp * 8 + j]
                x = x0 + j * cpit
                k.append(D.box(x, yy, cwid, 62, color=PANEL, radius=10))
                extra = {} if f == "(不写)" else {"fontFeatures": f}
                k.append(tx(SAMPLE, x + 6, yy + 20, cwid - 12, 26, size=fs,
                            color=INK, font=fnt, **extra))
            y += hdr + rh
        k.append(tx(fnt, 40, y - rh + 8, 196, 24, size=13, color=VIO,
                    font=D.MONO))
        y += 12
    k.append(tx("读法：同一行内相邻格如果字形与宽度完全一致，说明该特性在这个字体上"
                "没有任何作用 —— Skia 找不到对应 OpenType 表就静默忽略，连错都不报。",
                40, y + 6, cw - 80, 20, size=12, color=INK2))
    k.append(tx("实测：16 组里只有 Inter 的 ss01 真的换了字形（见第 1 组第 6 格）；"
                "tnum / onum / zero / smcp / liga / kern 在这三种字体上全部无效。",
                40, y + 30, cw - 80, 20, size=12, color=LIME))
    k.append(tx("另：fontFeatures=\"zzzz\"（标签根本不存在）也被接受，"
                "见 probe-c09d-enum 的 accepted 列表 —— 与未知属性被静默忽略同一类问题。",
                40, y + 54, cw - 80, 20, size=12, color=ROSE))
    dsl = D.snapshot([D.stack(k, cw, ch)], cw, ch, bg=BG)
    res = W.P.probe(dsl, "c09a-fontfeat")
    print("  probe-c09a", res.get("ok"), res.get("status"),
          (res.get("error") or "")[:300])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return res


# ------------------------------------------------------------------ probe B
def probe_b():
    cw, ch = 1500, 1020
    x0, y0 = 40, 122
    cwid, cpit, chgt, rpit = 344, 360, 148, 166
    k = head(cw, "PROBE c09b · 前景画笔 / 阴影 / 装饰线 / strut",
             "每一格只改一个属性，其余完全相同；黄色说明文字是这一格实际写了什么。")

    def cell(i, label, nodes, note=""):
        cx = x0 + (i % 4) * cpit
        cy = y0 + (i // 4) * rpit
        out = [D.box(cx, cy, cwid, chgt, color=PANEL, radius=12),
               tx(label, cx + 12, cy + 8, cwid - 24, 17, size=11,
                  color=AMBER, font=D.MONO)]
        for nd in nodes:
            out.append(nd)
        if note:
            out.append(tx(note, cx + 12, cy + chgt - 20, cwid - 24, 16,
                          size=10, color=INK3))
        return out

    def at(i):
        return (x0 + (i % 4) * cpit + 12, y0 + (i // 4) * rpit + 30)

    def T(i, s, size=44, color=INK, h=56, **extra):
        x, y = at(i)
        return tx(s, x, y, cwid - 24, h, size=size, color=color,
                  font=D.UI, **extra)

    S = "Rel 3.14"
    k += cell(0, "默认 · 无前景画笔（= FILL）", [T(0, S)])
    k += cell(1, "foregroundMode=STROKE · strokeWidth=1.4",
              [T(1, S, foregroundMode="STROKE", foregroundColor=AMBER,
                 foregroundStrokeWidth="1.4")])
    k += cell(2, "STROKE · strokeWidth=3.2",
              [T(2, S, foregroundMode="STROKE", foregroundColor=CYAN,
                 foregroundStrokeWidth="3.2")])
    k += cell(3, "STROKE_AND_FILL · 描边色 ≠ 填充色",
              [T(3, S, foregroundMode="STROKE_AND_FILL", foregroundColor=ROSE,
                 foregroundStrokeWidth="2.2")])
    for j, (jm, col) in enumerate([("MITER", ROSE), ("ROUND", GRN),
                                   ("BEVEL", VIO)]):
        k += cell(4 + j, "foregroundStrokeJoin=%s" % jm,
                  [T(4 + j, "Wj AV 3.14", foregroundMode="STROKE",
                     foregroundColor=col, foregroundStrokeWidth="3",
                     foregroundStrokeJoin=jm)])
    for j, (cm, col) in enumerate([("BUTT", AMBER), ("ROUND", LIME),
                                   ("SQUARE", CYAN)]):
        i = 7 + j
        note = ("PaintStrokeCap 只有三值" if j == 0 else
                ("BEVEL 会被 400 拒绝" if j == 1 else
                 "与 Join 的取值集不对称"))
        k += cell(i, "foregroundStrokeCap=%s" % cm,
                  [T(i, "H I f", foregroundMode="STROKE", foregroundColor=col,
                     foregroundStrokeWidth="3", foregroundStrokeCap=cm,
                     foregroundAntiAlias="true")], note=note)
    k += cell(10, "backgroundColor 文本底色",
              [T(10, S, backgroundColor="#FACC1533")])
    k += cell(11, "textShadow 单条 “3 4 2 #000000AA”",
              [T(11, S, textShadow="3 4 2 #000000AA")])
    k += cell(12, "textShadow 双条（逗号分隔，含负偏移）",
              [T(12, S, textShadow="3 3 0 #F43F5EFF,-2 -2 0 #38BDF8FF")])
    k += cell(13, "UNDERLINE + DOTTED + decorationGaps 2 3",
              [T(13, "deprecated api()", decoration="UNDERLINE",
                 decorationColor=AMBER, decorationLineStyle="DOTTED",
                 decorationThickness="2", decorationGaps="2 3")])
    k += cell(14, "LINE_THROUGH + DOUBLE",
              [T(14, "removed in 4.0", decoration="LINE_THROUGH",
                 decorationColor=ROSE, decorationLineStyle="DOUBLE",
                 decorationThickness="2")])
    k += cell(15, "OVERLINE + WAVY",
              [T(15, "planned for 4.2", decoration="OVERLINE",
                 decorationColor=CYAN, decorationLineStyle="WAVY",
                 decorationThickness="2")])

    # row 4 : strut / spacing / line height
    i = 16
    x, y = at(i)
    strut = {"strutEnabled": "true", "strutHeight": "46", "strutLeading": "16",
             "strutFontSize": "22", "strutFontFamily": D.UI}
    k += cell(i, "strutHeight=46 strutLeading=16（两行）",
              [tx("strut 行一", x, y, cwid - 24, 26, size=22, **strut),
               tx("strut 行二", x, y + 44, cwid - 24, 26, size=22, **strut)],
              note="strut* 只作用于最外层 Text")
    i = 17
    x, y = at(i)
    k += cell(i, "letterSpacing -1.6 / +7",
              [tx("letterSpacing -1.6", x, y, cwid - 24, 26, size=22, ls=-1.6),
               tx("letterSpacing +7", x, y + 42, cwid - 24, 26, size=22,
                  ls=7)])
    i = 18
    x, y = at(i)
    k += cell(i, "wordSpacing 16 / height 18 vs 38（行高）",
              [tx("height=18 wordSpacing=16", x, y, cwid - 24, 20, size=17,
                  height="18", wordSpacing="16"),
               tx("height=38 wordSpacing=0", x, y + 52, cwid - 24, 40,
                  size=17, height="38", wordSpacing="0")],
              note="height=Text 行高，不是盒子高度")
    i = 19
    x, y = at(i)
    k += cell(i, "topRatio 0.62 / 1.0 与 overflow=FADE",
              [tx("topRatio 0.62", x, y, cwid - 24, 26, size=26,
                  topRatio="0.62"),
               tx("topRatio 1.0 · overflow=FADE", x, y + 44, cwid - 24, 26,
                  size=26, topRatio="1", overflow="FADE")],
              note="两行都被硬裁 → FADE 只是渐隐边缘")

    dsl = D.snapshot([D.stack(k, cw, ch)], cw, ch, bg=BG)
    res = W.P.probe(dsl, "c09b-paint")
    print("  probe-c09b", res.get("ok"), res.get("status"),
          (res.get("error") or "")[:300])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return res


# ------------------------------------------------------------------ probe C
def probe_c():
    cw, ch = 1500, 1010
    x0, y0 = 40, 122
    cwid, cpit, chgt, rpit = 456, 472, 158, 172
    k = head(cw, "PROBE c09c · 行内组合：嵌套 Text / Raw / WidgetSpan / CDATA",
             "官方文档：Text 可嵌套 Text、Raw、Emoji、WidgetSpan；"
             "普通文本节点会被 trim，Raw 不会；属性值不能含裸双引号且解析器不解码实体。")

    def cell(i, label, nodes, note=""):
        cx = x0 + (i % 3) * cpit
        cy = y0 + (i // 3) * rpit
        out = [D.box(cx, cy, cwid, chgt, color=PANEL, radius=12),
               tx(label, cx + 12, cy + 8, cwid - 24, 17, size=11,
                  color=AMBER, font=D.MONO)]
        for nd in nodes:
            out.append(nd)
        if note:
            out.append(tx(note, cx + 12, cy + chgt - 20, cwid - 24, 16,
                          size=10, color=INK3))
        return out

    def at(i):
        return (x0 + (i % 3) * cpit + 12, y0 + (i // 3) * rpit + 32)

    def nested(i, before, mid, after, size=22, w=None, h=34, **outer):
        a = {"color": INK2, "fontSize": size, "fontFamily": D.UI}
        a.update(outer)
        kids = [el("Text", {}, [D.cdata(before)]),
                el("Text", {"color": AMBER, "fontStyle": "BOLD"},
                   [D.cdata(mid)]),
                el("Text", {}, [D.cdata(after)])]
        x, y = at(i)
        return el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                                 "width": round(w or (cwid - 24), 2),
                                 "height": h},
                  [el("Text", a, kids)])

    k += cell(0, "嵌套 <Text>：子 span 继承未覆盖的样式",
              [nested(0, "版本 ", "v3.14.0", " 已发布")],
              note="外层 22 px 常规，子层只覆盖 color + fontStyle")
    k += cell(1, "跨行换行后的继承（框宽只有 190 px）",
              [nested(1, "release notes 中 ", "breaking change",
                      " 会自动折行并保持样式", w=190, h=84)],
              note="折行后第二行仍然保持子 span 的粗体高亮")
    x, y = at(2)
    code = ("def build():\n"
            "    # 这 4 个空格必须保留\n"
            "    return Row(\n"
            "        Expanded(flex: 2),\n"
            "        Spacer(),\n"
            "    )")
    k += cell(2, "<Raw>：保留首尾空格与换行",
              [el("Positioned",
                  {"left": round(x, 2), "top": round(y, 2),
                   "width": round(cwid - 24, 2), "height": "120"},
                  [el("Text", {"color": CYAN, "fontSize": "13",
                               "fontFamily": D.MONO},
                      [el("Raw", {}, [D.cdata(code)])])])],
              note="6 行代码块，缩进由 Raw 保住")
    x, y = at(3)
    k += cell(3, "Raw 的行内缩进 · 逐项隔离见 c09g",
              [tx("   Text   ", x, y, cwid - 24, 26, size=17, font=D.MONO),
               el("Positioned",
                  {"left": round(x, 2), "top": round(y + 30, 2),
                   "width": round(cwid - 24, 2), "height": "52"},
                  [el("Text", {"color": GRN, "fontSize": "17",
                               "fontFamily": D.MONO},
                      [el("Raw", {}, [D.cdata("level0 = 1\n"
                                              "    level1 = 2\n"
                                              "        level2 = 3")])])])],
              note="Text 属性会 trim；Raw 的换行与缩进都保留")
    for j, (lbl, al, hh, col, fs) in enumerate([
            ("MIDDLE", "MIDDLE", 30, GRN, "22"),
            ("BASELINE + IDEOGRAPHIC", "BASELINE", 36, VIO, "34"),
            ("TOP", "TOP", 34, LIME, "22")]):
        i = 4 + j
        x, y = at(i)
        a = {"color": INK2, "fontSize": fs, "fontFamily": D.UI}
        widget = el("Container",
                    {"width": "46", "height": str(hh), "color": col,
                     "borderRadius": "8", "border": "2 SOLID #0B1020FF",
                     "alignment": "CENTER"},
                    [el("Text", {"text": "%d" % (j + 1), "color": "#0B1020FF",
                                 "fontSize": "20", "fontFamily": D.MONO,
                                 "fontStyle": "BOLD"})])
        ws = {"alignment": al}
        if al == "BASELINE":
            ws["baseline"] = "IDEOGRAPHIC"
        kids = [el("Text", {}, [D.cdata("前言 ")]),
                el("WidgetSpan", ws, [widget]),
                el("Text", {}, [D.cdata(" 后记")])]
        k += cell(i, "WidgetSpan alignment=%s" % lbl,
                  [el("Positioned",
                      {"left": round(x, 2), "top": round(y, 2),
                       "width": round(cwid - 24, 2), "height": "70"},
                      [el("Text", a, kids)])],
                  note="占位盒固定 46 px 宽，高 %d px" % hh)
    x, y = at(7)
    k += cell(7, "CDATA 与普通 text= 属性（尖括号 / 引号 / &）",
              [el("Positioned",
                  {"left": round(x, 2), "top": round(y, 2),
                   "width": round(cwid - 24, 2), "height": "24"},
                  [el("Text", {"color": GRN, "fontSize": "16",
                               "fontFamily": D.MONO},
                      [D.cdata('CDATA: List<Widget> & "q"')])]),
               el("Positioned",
                  {"left": round(x, 2), "top": round(y + 30, 2),
                   "width": round(cwid - 24, 2), "height": "24"},
                  [el("Text", {"color": CYAN, "fontSize": "16",
                               "fontFamily": D.MONO,
                               "text": "attr : List<Widget> & plain"})]),
               el("Positioned",
                  {"left": round(x, 2), "top": round(y + 60, 2),
                   "width": round(cwid - 24, 2), "height": "24"},
                  [el("Text", {"color": ROSE, "fontSize": "15",
                               "fontFamily": D.MONO,
                               "text": "attr : a b -- 无引号版本"})])],
              note="含裸双引号的第三行会让整次渲染 400，见 technique-notes")
    x, y = at(8)
    k += cell(8, "fontFamily 列表：多字体字符串不逐项 trim",
              [el("Positioned",
                  {"left": round(x, 2), "top": round(y, 2),
                   "width": round(cwid - 24, 2), "height": "26"},
                  [el("Text", {"color": INK, "fontSize": "18",
                               "fontFamily": "Inter,Noto Sans CJK SC"},
                      [D.cdata("Inter, Noto Sans CJK SC")])]),
               tx("逗号后的前导空格会保留成真实空隙；文档建议写 “Inter,Noto Sans CJK SC”。",
                  x, y + 34, cwid - 24, 34, size=11, color=INK3)])
    x, y = at(9)
    long_s = "breaking changes are listed here with their migration notes inline"
    k += cell(9, "maxLines + overflow=ELLIPSIS · softWrap=false",
              [tx(long_s, x, y, cwid - 24, 44, size=17, max_lines=2,
                  overflow="ELLIPSIS"),
               tx(long_s, x, y + 54, cwid - 24, 44, size=17, wrap=False)],
              note="上：2 行 + 省略号  ·  下：softWrap=false 单行裁切")
    x, y = at(10)
    k += cell(10, "textAlign 四值 + textDirection=RTL",
              [tx("START 左", x, y, 200, 22, size=16),
               tx("CENTER 中", x, y + 26, 200, 22, size=16, align="CENTER"),
               tx("END 右", x, y + 52, 200, 22, size=16, align="END"),
               tx("RTL 版本 3.14", x + 216, y + 26, cwid - 240, 22, size=16,
                  textDirection="RTL")])
    x, y = at(11)
    k += cell(11, "fontHinting / subpixel / baselineMode",
              [tx("fontHinting=FULL（默认）", x, y, cwid - 24, 24, size=17,
                  fontHinting="FULL"),
               tx("fontHinting=NONE", x, y + 30, cwid - 24, 24, size=17,
                  fontHinting="NONE"),
               tx("subpixel=false + baselineMode=ALPHABETIC", x, y + 60,
                  cwid - 24, 24, size=17, subpixel="false",
                  baselineMode="ALPHABETIC")],
              note="fontEdging / textHeightMode 找不到任何可用取值，见 enum 探针")
    x, y = at(12)
    k += cell(12, "嵌套 span 的 textAlign 不生效（段落属性只在最外层）",
              [el("Positioned",
                  {"left": round(x, 2), "top": round(y, 2),
                   "width": round(cwid - 24, 2), "height": "26"},
                  [el("Text", {"color": INK2, "fontSize": "18",
                               "fontFamily": D.UI},
                      [el("Text", {}, [D.cdata("前缀 ")]),
                       el("Text", {"color": CYAN, "textAlign": "RIGHT"},
                          [D.cdata("这段不会自己右对齐")]),
                       el("Text", {}, [D.cdata(" 后缀")])])]),
               tx("外层没写 textAlign，段落按 START 排；子 span 的 textAlign 被忽略。",
                  x, y + 36, cwid - 24, 34, size=11, color=INK3)])

    dsl = D.snapshot([D.stack(k, cw, ch)], cw, ch, bg=BG)
    res = W.P.probe(dsl, "c09c-inline")
    print("  probe-c09c", res.get("ok"), res.get("status"),
          (res.get("error") or "")[:300])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return res


if __name__ == "__main__":
    print("== case-09 stage 1: capability probes")
    probe_a()
    probe_b()
    probe_c()