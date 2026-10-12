"""B04 构件：手册骨架 + 天文几何画法。

只使用 B03/B04 已用探针确认过的 DSL 能力：Stack/Positioned/Container/Text/Transform，
无矢量 path（锥体、多边形一律扫描线矩形逼近），圆形用 borderRadius=半径。

用法（各 case 生成器）：

    import b04kit as B
    d, tf = B.doc(1600, 1200, ground="dark")
    B.tlab(...)  # 带 TextFit 闸门的文本
    B.cone(...)  # 扫描线填充

统计与数据：B.data() 读取 tmp/<run>/B04/research/ 下由 b04_research.py 产出的真实结果。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03",
           ROOT / "tmp" / RID / "B04"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from dslkit import Doc, TextFit  # noqa: E402
import b03kit as K  # noqa: E402

GROUND = "#080D1C"
GROUND2 = "#0C1327"
PAPER = "#EFE6D3"
PAPER2 = "#E3D7BE"
INK = "#171A1F"
EMBER = "#E1552B"
CYAN = "#5AB6C4"
CORONA = "#F6D27A"
MOON = "#C9D2DF"
DIM = "#7E8CA6"
DIMI = "#4A5570"
SANS = "Inter,Noto Sans CJK SC"
SERIF = "Noto Serif CJK SC"
MONO = "Noto Sans Mono CJK SC"

PAL_DARK = {"t0": PAPER, "t1": "#B9C4D8", "t2": DIM, "axis": DIMI, "grid": "#16203C",
            "card": GROUND2, "card2": "#101A31", "border": "#22304F",
            "ember": EMBER, "cyan": CYAN, "corona": CORONA, "moon": MOON}
PAL_PAPER = {"t0": INK, "t1": "#3B4250", "t2": "#6C7484", "axis": "#9AA1AD", "grid": "#D8CCB0",
             "card": PAPER2, "card2": "#EADDCA", "border": "#C8B896",
             "ember": "#C6421D", "cyan": "#2E7C88", "corona": "#B98A16", "moon": "#5C6674"}

_n = K.n


def doc(w, h, ground="dark"):
    """新画布。ground=dark 用深空底，paper 用手册纸底。"""
    pal = PAL_DARK if ground == "dark" else PAL_PAPER
    return Doc(w, h, bg=(GROUND if ground == "dark" else PAPER), font=SANS,
               palette=pal), TextFit()


def data():
    res = ROOT / "tmp" / RID / "B04" / "research"
    return (json.load(open(res / "stats.json", encoding="utf-8")),
            json.load(open(res / "catalog.json", encoding="utf-8"))["rows"])


def ddata():
    """derive.py 产出的派生量（本影长度、逐年分布、极值榜单等）。"""
    res = ROOT / "tmp" / RID / "B04" / "research"
    return json.load(open(res / "derived.json", encoding="utf-8"))


def km(v):
    return "{:,}".format(int(round(v)))


# ---------- 文本 ----------
def tlab(d, tf, tag, x, y, w, h, s, size, color=None, lines=1, font=None, **kw):
    K.tlab(d, tf, tag, x, y, w, h, s, size, color or d.P["t0"], lines=lines,
           font=font or d.font, **kw)


def mono(d, tf, tag, x, y, w, h, s, size, color=None, lines=1, **kw):
    tlab(d, tf, tag, x, y, w, h, s, size, color, lines=lines, font=MONO, **kw)


# ---------- 形状 ----------
def disc(d, cx, cy, r, color, opacity=None):
    d.rect(cx - r, cy - r, 2 * r, 2 * r, color, radius=r)


def ring(d, cx, cy, r, thick, color):
    d.rect(cx - r - thick, cy - r - thick, 2 * (r + thick), 2 * (r + thick), color,
           radius=r + thick)
    cut = d.bg
    d.rect(cx - r, cy - r, 2 * r, 2 * r, cut, radius=r)


def _edge_x(p, q, y):
    """scanline y 与线段 p-q 的交点 x（平行于 y 的边跳过）。"""
    if (p[1] - q[1]) == 0:
        return None
    t = (y - p[1]) / (q[1] - p[1])
    if t < 0 or t > 1:
        return None
    return p[0] + t * (q[0] - p[0])


def poly(d, pts, color, step=3.0):
    """凸/凹多边形填充：逐水平扫描线取最小/最大交点。服务无矢量 path。"""
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    y = y0
    n = 0
    while y < y1:
        xs = [x for e in range(len(pts))
              for x in [_edge_x(pts[e], pts[(e + 1) % len(pts)], y)] if x is not None]
        if len(xs) >= 2:
            a, b = min(xs), max(xs)
            if b - a > 0.4:
                d.rect(a, y, b - a, min(step, y1 - y) + 0.4, color)
                n += 1
        y += step
    return n


def cone(d, apex, base_c, base_r, color, step=3.0):
    """以 apex 为顶点、base_c 为底心（垂直底边）的等腰三角形＝锥体剖面板。"""
    ax, ay = apex
    bx, by = base_c
    return poly(d, [(ax, ay), (bx, by - base_r), (bx, by + base_r)], color, step)


def hrule(d, x, y, w, color, th=2):
    d.rect(x, y, w, th, color)


def vrule(d, x, y, h, color, th=2):
    d.rect(x, y, th, h, color)


def ticks(d, x, y, w, n_minor, color, major_every=5, major_h=12, minor_h=6, labels=None,
          tf=None, tag="", lsize=13, lcolor=None, label_dy=16):
    """沿水平轴的刻度（可选主刻度标注）。"""
    for i in range(n_minor + 1):
        xx = x + w * i / n_minor
        major = (i % major_every == 0)
        h = major_h if major else minor_h
        d.rect(xx, y, 1.6 if major else 1.0, h, color)
        if major and labels and i // major_every < len(labels) and tf is not None:
            tlab(d, tf, tag + "-tick%d" % i, xx - 30, y + h + label_dy, 60, lsize + 6,
                 labels[i // major_every], lsize, lcolor or color, align="CENTER")


# ---------- 手册骨架 ----------
def header(d, tf, tag, num, title, subtitle, kicker="月影手册", size=52, paper=False):
    fg = INK if paper else PAPER
    ac = EMBER
    mono(d, tf, tag + "-kick", 72, 44, 320, 22, "%s · %s" % (kicker, num), 17, ac)
    hrule(d, 72, 78, 150, ac, 3)
    tlab(d, tf, tag + "-title", 72, 96, d.W - 340, size + 16, title, size, fg,
         style="BOLD", font=SANS)
    tlab(d, tf, tag + "-sub", 72, 108 + size + 6, d.W - 340, 26, subtitle, 19,
         d.P["t1"])
    return fg


def footband(d, tf, tag, lines, size=13, paper=False, y=None):
    """页脚注带：来源、推算声明、图的局限。"""
    fg = d.P["t2"]
    y = y if y is not None else d.H - 24 - len(lines) * (size + 7)
    hrule(d, 72, y - 12, d.W - 144, d.P["border"], 1)
    for i, ln in enumerate(lines):
        tlab(d, tf, "%s-l%d" % (tag, i), 72, y + i * (size + 7), d.W - 144, size + 6,
             ln, size, fg, lines=1)
    return y


def datarow(d, tf, tag, x, y, w, label, value, size=16, unit=None, color=None,
            gap=None, h=None):
    """左标签 + 右数值的资料行（数字用等宽字体）。"""
    h = h or size + 10
    lab_w = gap if gap is not None else int(w * 0.52)
    tlab(d, tf, tag + "-l", x, y, lab_w, h, label, size, d.P["t1"])
    vw = w - lab_w - (34 if unit else 0)
    mono(d, tf, tag + "-v", x + lab_w, y, vw, h, value, size, color or d.P["t0"],
         align="END")
    if unit:
        tlab(d, tf, tag + "-u", x + w - 32, y, 32, h, unit, size - 3, d.P["t2"])
    return y + h


def keypanel(d, tf, tag, x, y, w, title, rows, row_h=34, size=16):
    """带标题的资料板：rows = [(label, value, unit?)]。"""
    tlab(d, tf, tag + "-t", x, y, w, 24, title, 18, d.P["t0"], style="BOLD")
    yy = y + 34
    for i, r in enumerate(rows):
        lab, val = r[0], r[1]
        unit = r[2] if len(r) > 2 else None
        col = r[3] if len(r) > 3 else None
        if lab.startswith("+"):
            hrule(d, x, yy - 4, w, d.P["border"], 1)
            lab = lab[1:]
        yy = datarow(d, tf, "%s-r%d" % (tag, i), x, yy, w, lab, val, size, unit, col)
    return yy


def hbars(d, tf, tag, x, y, w, rows, bh=26, gap=10, lab_w=118, vmax=None, fmt=None,
          color=None, size=15):
    """水平条形图：rows = [(label, value, color?)]，长度严格按 value/vmax 线性。"""
    vmax = vmax or max(r[1] for r in rows)
    n = 0
    for i, r in enumerate(rows):
        lab, val = r[0], r[1]
        col = r[2] if len(r) > 2 else (color or EMBER)
        yy = y + i * (bh + gap)
        tlab(d, tf, "%s-l%d" % (tag, i), x, yy, lab_w, bh, lab, size, d.P["t1"])
        bw = max(2.0, (w - lab_w - 96) * val / vmax)
        d.rect(x + lab_w, yy + 4, bw, bh - 8, col)
        txt = fmt(val) if fmt else str(val)
        mono(d, tf, "%s-v%d" % (tag, i), x + lab_w + bw + 10, yy, 86, bh, txt, size,
             d.P["t0"], align="START")
        n += 1
    return y + n * (bh + gap)
