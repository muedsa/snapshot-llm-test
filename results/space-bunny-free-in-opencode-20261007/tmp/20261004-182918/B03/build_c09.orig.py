"""B03 case-09 · 版本说明 · 发行单页 (release sheet).

Primary capability under test: the typography / rich-text frontier.
  foregroundMode=STROKE (hollow display numerals), textShadow (multi),
  decorationLineStyle SOLID/DOTTED/DOUBLE/WAVY + decorationGaps,
  fontFeatures (only ss01/ss02 do anything, only on Inter),
  letterSpacing, nested <Text> spans, <WidgetSpan> inline chips,
  <Raw> (indentation + newlines), CDATA (angle brackets / quotes / &),
  maxLines + overflow=ELLIPSIS, textAlign START/CENTER/END.

Everything the piece claims was verified first on probe-c09a/b/c/e/f/g in
tmp/20261004-182918/B03/probes/. Two attributes turned out to be unusable and
are reported instead of faked: Text height= and strutLeading (both render an
EMPTY paragraph with HTTP 200).

Scene: the printable release sheet a maintainer posts with anvilplot 3.14.0.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

CW, CH = 1500, 1090
PAPER = "#F7F7F2FF"
INK = "#101318FF"
INK2 = "#3D4654FF"
INK3 = "#6B7482FF"
HAIR = "#D8D8D0FF"
BAND = "#0B0B0FFF"
VIO = "#6D28D9FF"
CYA = "#0E7490FF"
AMB = "#B45309FF"
ROS = "#BE123CFF"
GRN = "#15803DFF"

CHIP = {
    "BREAKING": (ROS, "#FCE7EDFF"),
    "DEPRECATED": (AMB, "#FEF3C7FF"),
    "FIXED": (GRN, "#DCFCE7FF"),
    "ADDED": (CYA, "#CFFAFEFF"),
}

CHANGES = [
    ("BREAKING", "tight_layout() 改为返回 None 并就地应用",
     "旧调用 `fig.tight_layout()` 之后再 `fig.subplots_adjust()` 的代码不再需要。"),
    ("BREAKING", "移除 anvilplot.contrib.mpl 兼容层",
     "统一入口为 anvilplot.mpl；contrib 命名空间在本版直接抛 ImportError。"),
    ("DEPRECATED", "Style(font=...) 改名为 font_family",
     "旧参数在 3.14 仍可用但会打 DeprecationWarning，4.0 移除。"),
    ("ADDED", "colorbar(discrete=True) 离散色标",
     "按分箱渲染刻度与边界线，支持 BoundaryNorm 的自定义分箱。"),
    ("ADDED", "read() 支持 glob 通配符批量读入",
     "anvilplot.read('data/*.parquet') 返回按文件名排序的 Series 列表。"),
    ("ADDED", "export(transparent=True) 输出带 alpha 的 SVG",
     "背景矩形不再写入，CSS 里可直接叠色。"),
    ("FIXED", "savefig() 接受 pathlib.Path",
     "Windows 下不再抛 AttributeError: 'PosixPath' object has no attribute 'endswith'。"),
    ("FIXED", "对数轴刻度密度提高",
     "scale='log' 的主刻度从 1 个数量级变成 3 个，长序列不再挤成一条线。"),
    ("FIXED", "中文图例缺字回退",
     "font_family 里第一个字体缺字时按顺序回退，最后回退 Noto Sans CJK SC。"),
    ("FIXED", "layout='constrained' 裁掉图例",
     "图例 bbox 被纳入 constrained 布局的求解，右上角不再被切。"),
    ("FIXED", "空序列不再抛 IndexError",
     "Series.plot() 在长度 0 时画一条空轴并给出 warning。"),
    ("DEPRECATED", "annotate(arrowprops='->') 字符串简写",
     "改为 arrowprops=dict(arrowstyle='->')；字符串形式将在 4.0 报错。"),
]

DIFF_OLD = (
    "fig, ax = anvilplot.subplots()\n"
    "ax.plot(xs, ys, \"r--\", lw=2)\n"
    "ax.set_title(\"潮位 2026-10-05\")\n"
    "fig.savefig(\"out/series.png\")"
)
DIFF_NEW = (
    "fig, ax = anvilplot.subplots(figsize=(8, 4.5), dpi=144)\n"
    "ax.plot(xs, ys, color=\"#BE123C\", lw=2, ls=(0, (5, 2)))\n"
    "ax.set_title(\"潮位\", font_family=\"Inter,Noto Sans CJK SC\")\n"
    "fig.export(\"out/series.svg\", transparent=True)"
)
TYPED = (
    "from anvilplot import Plot, Series\n"
    "def overlay(xs: list[float], ys: list[float]) -> Plot:\n"
    "    # 同时给上下界，避免 & 与 < 直接写在属性里\n"
    "    assert len(xs) == len(ys) and xs\n"
    "    return Plot().line(xs, ys).band(\"p10\", \"p90\")"
)

PY = ["3.10", "3.11", "3.12", "3.13", "3.14"]
PLAT = [("Linux x86_64", ["支持"] * 5),
        ("macOS arm64", ["支持", "支持", "支持", "支持", "支持"]),
        ("Windows", ["部分", "部分", "支持", "支持", "支持"]),
        ("Pyodide 0.26", ["—", "—", "—", "部分", "支持"])]
PLAT_COLOR = {"支持": GRN, "部分": AMB, "—": INK3}

TIMELINE = [("3.10.0", "2024-11-12", "首个带 colormap 的稳定版"),
            ("3.11.0", "2025-03-04", "引入 facet"),
            ("3.12.0", "2025-07-22", "Arrow 标注 API"),
            ("3.13.0", "2026-02-10", "constrained 布局"),
            ("3.14.0", "2026-09-28", "本版：叠印色标 + SVG alpha")]

STATS = [("6 个月下载量", "1,284,930"), ("贡献者", "47"),
         ("关闭 issue", "312"), ("平均响应", "31 h")]

DECO = [("SOLID", "本版修改的 API 签名", VIO, "SOLID", None, 2.6),
        ("WAVY", "已废弃，4.0 将删除", AMB, "WAVY", None, 2.0),
        ("DOTTED", "已排期，尚未发布", CYA, "DOTTED", "2 3", 2.4),
        ("DOUBLE", "已在本版删除", ROS, "DOUBLE", None, 2.0)]

SUMMARY = ("本版把 colormap 的多色标合成改成真正的减色叠印：ColorFiltered 的 "
           "color 与节点自身像素相乘，而不是与背景相乘，因此同一版矩阵在 "
           "C×M 与 M×C 两个方向上必然一致。除此之外没有引入新的破坏性变更，"
           "仅有两项弃用与七项修复。发布说明与迁移片段由维护者手写，"
           "本页所有数值均为演示用虚构数据。")


def chip_span(label, size=11):
    fg, bg = CHIP[label]
    w = len(label) * size * 0.605 + 14
    return el("WidgetSpan", {"alignment": "MIDDLE"},
              [el("Container",
                  {"width": round(w, 2), "height": "20", "color": bg,
                   "borderRadius": "5", "alignment": "CENTER"},
                  [el("Text", {"text": label, "color": fg,
                               "fontSize": str(size), "fontFamily": D.MONO,
                               "fontStyle": "BOLD"})])]), w


def panel(x, y, w, h, fill="#FFFFFFFF", border="1 SOLID " + HAIR, radius=14):
    return el("Positioned",
              {"left": round(x, 2), "top": round(y, 2), "width": round(w, 2),
               "height": round(h, 2)},
              [el("Container", {"width": round(w, 2), "height": round(h, 2),
                                "color": fill, "borderRadius": str(radius),
                                "border": border})])


def head(x, y, w, zh, en, rule=True):
    out = [W.t2(zh, x, y, size=15, color=INK, style="BOLD", w=w, h=22),
           W.t2(en, x, y + 21, size=10.5, color=INK3, w=w, h=16, ls=1.8,
                font=D.MONO)]
    if rule:
        out.append(box(x, y + 42, w, 1, color=HAIR))
    return out


def build():
    k = [box(0, 0, CW, 196, color=BAND)]

    # ---- masthead ------------------------------------------------------
    k.append(W.t2("ANVILPLOT", 48, 40, size=58, color="#FFFFFFFF",
                  style="BOLD", w=760, h=78, ls=5))
    k.append(W.t2("RELEASE NOTES · 发行说明单页", 50, 124, size=13,
                  color="#9CA3AFFF", w=520, h=20, ls=4.2, font=D.MONO))

    # giant hollow version, slashed zero via fontFeatures="ss02"
    k.append(el("Positioned",
                {"left": "700", "top": "18", "width": "420", "height": "150"},
                [el("Text",
                    {"color": "#FFFFFFFF", "fontSize": "116",
                     "fontFamily": "Inter", "fontStyle": "BOLD",
                     "fontFeatures": "ss02", "letterSpacing": "-2",
                     "foregroundMode": "STROKE", "foregroundColor": "#FFFFFFFF",
                     "foregroundStrokeWidth": "2.1",
                     "foregroundStrokeJoin": "ROUND",
                     "textShadow": "0 6 26 #6D28D966,-2 0 0 #0E7490AA"},
                    [D.cdata("3.14.0")])]))
    k.append(W.t2("v3.14.0 · 2026-09-28 · MIT · PyPI", 706, 162, size=13,
                  color="#A78BFAFF", w=460, h=20, font=D.MONO, ls=1.2))

    pill = "pip install anvilplot==3.14.0"
    pw = len(pill) * 14 * 0.605 + 28
    k.append(el("Positioned",
                {"left": round(CW - 48 - pw, 2), "top": "54", "width": round(pw, 2),
                 "height": "38"},
                [el("Container", {"width": round(pw, 2), "height": "38",
                                  "color": "#18181BFF",
                                  "borderRadius": "19",
                                  "border": "1 SOLID #3F3F46FF",
                                  "alignment": "CENTER"},
                    [el("Text", {"text": pill, "color": "#A1A1AAFF",
                                 "fontSize": "14",
                                 "fontFamily": D.MONO})])]))
    k.append(W.t2("pip / conda / npm 三个通道同时发布", CW - 48 - pw, 104,
                  size=11, color="#71717AFF", w=pw + 40, h=18, align="RIGHT"))
    k.append(W.t2("本页 100% 尺寸阅读，最小字号 10 px", 48, 158, size=11,
                  color="#52525BFF", w=600, h=18))

    # ---- body ----------------------------------------------------------
    AX, AW = 48, 470
    BX, BW = 550, 470
    CX, CWID = 1052, 400

    # column A : changelog with inline WidgetSpan chips
    k += head(AX, 224, AW, "变更清单", "CHANGELOG · 12 ENTRIES")
    y = 286
    for kind, title, note in CHANGES:
        chip, cw = chip_span(kind)
        k.append(el("Positioned",
                    {"left": AX, "top": y, "width": AW, "height": "24"},
                    [el("Text",
                        {"color": INK, "fontSize": "13", "fontFamily": D.UI},
                        [chip,
                         el("Text", {"fontFamily": D.MONO, "color": INK2},
                            [D.cdata("  ") + D.cdata(title)])])]))
        k.append(W.t2(note, AX + 14, y + 21, size=10.5, color=INK3, w=AW - 14,
                      h=D.est_lines(note, 10.5, AW - 14) * 14))
        k.append(box(AX, y + 43, AW, 1, color="#ECECE6FF"))
        y += 50

    # column B : migration diff + typed sample + decoration legend
    k += head(BX, 224, BW, "迁移片段", "MIGRATION · RAW + CDATA")
    k.append(panel(BX, 286, BW, 202, fill="#0B0B0FFF", border=None))
    k.append(W.t2("3.13 → 3.14 最小改动", BX + 16, 296, size=11,
                  color="#A1A1AAFF", w=240, h=16, font=D.MONO))
    k.append(el("Positioned",
                {"left": BX + 16, "top": "316", "width": BW - 48, "height": "80"},
                [el("Text", {"color": "#F87171FF", "fontSize": "11",
                             "fontFamily": D.MONO},
                    [el("Raw", {}, [D.cdata(DIFF_OLD)])])]))
    k.append(el("Positioned",
                {"left": BX + 16, "top": "318", "width": "16", "height": "16"},
                [el("Text", {"text": "−", "color": "#F87171FF",
                             "fontSize": "13", "fontFamily": D.MONO})]))
    k.append(el("Positioned",
                {"left": BX + 34, "top": "402", "width": BW - 66, "height": "80"},
                [el("Text", {"color": "#4ADE80FF", "fontSize": "11",
                             "fontFamily": D.MONO},
                    [el("Raw", {}, [D.cdata(DIFF_NEW)])])]))
    k.append(el("Positioned",
                {"left": BX + 16, "top": "404", "width": "16", "height": "16"},
                [el("Text", {"text": "+", "color": "#4ADE80FF",
                             "fontSize": "13", "fontFamily": D.MONO})]))

    k.append(panel(BX, 500, BW, 160, fill="#FFFFFF00",
                   border="1 SOLID " + HAIR))
    k.append(W.t2("类型标注（CDATA 处理 < > & 与引号）", BX + 16, 510, size=11,
                  color=INK2, w=BW - 32, h=16, font=D.MONO))
    k.append(el("Positioned",
                {"left": BX + 16, "top": "532", "width": BW - 32, "height": "114"},
                [el("Text", {"color": INK2, "fontSize": "10.5",
                             "fontFamily": D.MONO},
                    [el("Raw", {}, [D.cdata(TYPED)])])]))

    k.append(panel(BX, 672, BW, 216, fill="#FFFFFF00",
                   border="1 SOLID " + HAIR))
    k.append(W.t2("装饰线语义", BX + 16, 682, size=11, color=INK2, w=BW - 32,
                  h=16, font=D.MONO))
    k.append(W.t2("decoration + decorationLineStyle + decorationThickness"
                  "（+ decorationGaps）", BX + 16, 700, size=10.5, color=INK3,
                  w=BW - 32, h=16))
    dy = 722
    for name, note, col, style, gaps, th in DECO:
        k.append(W.t2(name, BX + 18, dy, size=11.5, color=col, w=110, h=18,
                      font=D.MONO))
        k.append(el("Positioned",
                    {"left": BX + 132, "top": dy - 2, "width": "170",
                     "height": "26"},
                    [el("Text",
                        {"color": INK, "fontSize": "14",
                         "fontFamily": D.MONO,
                         "decoration": "UNDERLINE",
                         "decorationColor": col,
                         "decorationLineStyle": style,
                         "decorationThickness": str(th),
                         **({"decorationGaps": gaps} if gaps else {})},
                        [D.cdata("fig.subplots()")])]))
        k.append(W.t2(note, BX + 314, dy + 1, size=11, color=INK2, w=140,
                      h=34))
        dy += 36
    k.append(W.t2("decorationGaps=\"2 3\" 让 DOTTED 变成真点线。", BX + 18,
                  dy + 4, size=10.5, color=INK3, w=BW - 36, h=16))

    # column C : compatibility matrix, timeline, stats
    k += head(CX, 224, CWID, "兼容性", "SUPPORT MATRIX")
    gy = 288
    labw = 138
    colw = (CWID - labw) / 5.0
    k.append(W.t2("Python", CX, gy, size=10, color=INK3, w=labw, h=14,
                  font=D.MONO))
    for j, v in enumerate(PY):
        k.append(el("Positioned",
                    {"left": round(CX + labw + colw * j, 2), "top": gy,
                     "width": round(colw, 2), "height": "16"},
                    [el("Text", {"text": v, "color": INK2, "fontSize": "10.5",
                                 "fontFamily": "Inter", "fontFeatures": "ss02",
                                 "textAlign": "CENTER"})]))
    k.append(box(CX, gy + 22, CWID, 1, color=HAIR))
    for i, (plat, vals) in enumerate(PLAT):
        ry = gy + 32 + i * 30
        k.append(W.t2(plat, CX, ry, size=11.5, color=INK, w=labw - 4, h=18))
        for j, v in enumerate(vals):
            k.append(el("Positioned",
                        {"left": round(CX + labw + colw * j, 2), "top": ry,
                         "width": round(colw, 2), "height": "18"},
                        [el("Text", {"text": v,
                                     "color": PLAT_COLOR[v],
                                     "fontSize": "10.5",
                                     "fontFamily": D.UI,
                                     "textAlign": "CENTER"})]))
        k.append(box(CX, ry + 22, CWID, 1, color="#ECECE6FF"))
    k.append(W.t2("“部分”= 已知缺字 / 无 GPU 加速；Pyodide 只支持 WebGL 导出。",
                  CX, gy + 32 + 4 * 30 + 8, size=10.5, color=INK3, w=CWID,
                  h=16))

    k += head(CX, 480, CWID, "发行节奏", "RELEASE CADENCE")
    ty = 544
    k.append(box(CX + 6, ty, 1, 5 * 34, color=HAIR))
    for i, (v, date, note) in enumerate(TIMELINE):
        ry = ty + i * 34
        cur = i == len(TIMELINE) - 1
        col = VIO if cur else INK3
        k.append(el("Positioned",
                    {"left": CX, "top": round(ry + 4, 2), "width": "13",
                     "height": "13"},
                    [el("Container", {"width": "13", "height": "13",
                                      "shape": "CIRCLE",
                                      "color": col if cur else "#D8D8D0FF"})]))
        k.append(el("Positioned",
                    {"left": CX + 22, "top": round(ry, 2), "width": "92",
                     "height": "20"},
                    [el("Text", {"text": v, "color": INK if cur else INK2,
                                 "fontSize": "12.5", "fontFamily": "Inter",
                                 "fontFeatures": "ss02",
                                 "fontStyle": "BOLD" if cur else "NORMAL"})]))
        k.append(W.t2(date, CX + 118, ry + 2, size=10.5, color=INK3, w=90,
                      h=16, font=D.MONO))
        k.append(W.t2(note, CX + 22, ry + 16, size=10.5,
                      color=VIO if cur else INK3, w=CWID - 30, h=16))

    k += head(CX, 730, CWID, "本版数字", "BY THE NUMBERS")
    sy = 792
    for i, (lab, val) in enumerate(STATS):
        gxx = CX + (i % 2) * (CWID / 2.0)
        gyy = sy + (i // 2) * 50
        k.append(W.t2(lab, gxx, gyy, size=10.5, color=INK3, w=CWID / 2 - 14,
                      h=16))
        k.append(W.t2(val, gxx, gyy + 17, size=23, color=INK, w=CWID / 2 - 14,
                      h=30, style="BOLD", font="Inter", features="ss02"))

    # ---- summary band --------------------------------------------------
    k.append(box(0, 900, CW, 128, color="#EDEDE6FF"))
    k.append(W.t2("摘要", 48, 918, size=11, color=VIO, w=120, h=16, ls=2,
                  font=D.MONO))
    k.append(W.t2(SUMMARY, 48, 940, size=12.5, color=INK2, w=1010,
                  h=D.est_lines(SUMMARY, 12.5, 1010) * 18))
    k.append(panel(1088, 916, 364, 96, fill="#FFFFFF00",
                   border="1 SOLID " + HAIR))
    k.append(W.t2("已知问题", 1104, 928, size=10.5, color=AMB, w=200, h=16,
                  font=D.MONO))
    k.append(W.t2("3.14.1 会在 10 月中旬修掉 savefig 对 Path 的第二次回归；"
                  "已开 issue #2311。", 1104, 950, size=11.5, color=INK2,
                  w=332, h=48))

    # ---- footer --------------------------------------------------------
    k.append(box(0, CH - 52, CW, 1, color=HAIR))
    k.append(W.t2("本页只用了 Snapshot DSL：文字、版式、色块、描边字、"
                  "空心版本号、行内 chip 与代码块全部由 DSL 构造，"
                  "没有任何位图或后处理。", 48, CH - 40, size=10.5, color=INK3,
                  w=1000, h=16))
    k.append(W.t2("数据为演示用虚构值 · anvilplot 非真实项目 · "
                  "2026-09-28", CW - 48 - 420, CH - 40, size=10.5,
                  color=INK3, w=420, h=16, align="RIGHT", font=D.MONO))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=PAPER)
    r = W.P.render_final(dsl, "case-09", "final")
    print("  case-09", r.get("ok"), r.get("status"), (r.get("error") or "")[:300])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-09 stage 2: work")
    build()