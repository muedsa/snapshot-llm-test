"""B05 构件：枝安产品界面骨架 + 树形/风险图形。

只用已探针确认的能力：Stack/Positioned/Container/Text/Transform，borderRadius 画圆，
Transform 矩阵画斜线（dslkit.Doc.line），无矢量 path。所有文本走 TextFit 闸门。

十件共用同一套数据（tmp/<run>/B05/research/*.json，由 b05data.py 生成）与同一套
品牌语言：树皮墨底 / 纸面米白 / 主绿 / 警示橙 / 处置红 / 数据青。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03",
           ROOT / "tmp" / RID / "B05"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from dslkit import Doc, TextFit  # noqa: E402
import b03kit as K  # noqa: E402

BARK = "#15120F"
GROUND = "#101713"
GROUND2 = "#182219"
PAPER = "#F4EFE6"
CARD = "#FFFDF8"
INK = "#211D19"
LEAF = "#3E7C4B"
LEAF_D = "#2A5735"
AMBER = "#D9752B"
RUST = "#C8402F"
TEAL = "#3E8E96"
MIST = "#8C9488"
LINE = "#DCD3C4"
SANS = "Inter,Noto Sans CJK SC"
SERIF = "Noto Serif CJK SC"
MONO = "Noto Sans Mono CJK SC"

BAND_COLOR = {"立即处置": RUST, "限期处置": AMBER, "观察期": "#B98A16", "正常": LEAF}

PAL_LIGHT = {"t0": INK, "t1": "#4A4A44", "t2": "#767062", "axis": "#9AA1AD",
             "grid": "#E7E0D2", "card": CARD, "card2": "#F7F3EA",
             "border": "#DED6C6", "leaf": LEAF, "amber": AMBER, "rust": RUST,
             "teal": TEAL, "mist": MIST, "line": LINE}
PAL_DARK = {"t0": "#F2EEE4", "t1": "#BFC6BB", "t2": "#8C9488", "axis": "#5C665C",
            "grid": "#243028", "card": GROUND2, "card2": "#131C16",
            "border": "#2C3A2F", "leaf": "#6FB47F", "amber": "#E89A4E",
            "rust": "#E46A55", "teal": "#66C0C6", "mist": "#7F8A80",
            "line": "#2C3A2F"}

_n = K.n


def doc(w, h, ground="light"):
    if ground == "light":
        return Doc(w, h, bg=PAPER, font=SANS, palette=PAL_LIGHT), TextFit()
    return Doc(w, h, bg=GROUND, font=SANS, palette=PAL_DARK), TextFit()


def data():
    res = ROOT / "tmp" / RID / "B05" / "research"
    return json.load(open(res / "stats.json", encoding="utf-8"))


def trees():
    res = ROOT / "tmp" / RID / "B05" / "research"
    return json.load(open(res / "trees.json", encoding="utf-8"))


def tree(tid):
    for t in trees()["trees"]:
        if t["id"] == tid:
            return t
    raise KeyError(tid)


def fmt(v, digits=0):
    return ("{:,." + str(digits) + "f}").format(v)


# ---------- 文本 ----------
def tlab(d, tf, tag, x, y, w, h, s, size, color=None, lines=1, font=None, **kw):
    K.tlab(d, tf, tag, x, y, w, h, s, size, color or d.P["t0"], lines=lines,
           font=font or d.font, **kw)


def mono(d, tf, tag, x, y, w, h, s, size, color=None, lines=1, **kw):
    tlab(d, tf, tag, x, y, w, h, s, size, color, lines=lines, font=MONO, **kw)


def num(d, tf, tag, x, y, w, h, s, size, color=None, align="END", **kw):
    """等宽大数字：用 CDATA 保证减号/斜杠不被解析器吞掉，右对齐。"""
    tlab(d, tf, tag, x, y, w, h, s, size, color, font=MONO, align=align, **kw)


# ---------- 界面骨架 ----------
def phone(d, tf, tag, x, y, w, h, title="", app_h=88, time="09:20"):
    """手机外框 + 状态栏：左侧时间、右侧信号与电量（电量条按真实剩余比例画）。"""
    d.rect(x, y, w, h, d.P["card2"], radius=44)
    panel(d, x + 10, y + 10, w - 20, h - 20, d.P["card"], radius=36,
          border="1 SOLID " + d.P["border"])
    inx, inw = x + 10, w - 20
    mono(d, tf, tag + "-time", inx + 34, y + 26, 90, 26, time, 17, d.P["t0"])
    for i, bh in enumerate([9, 13, 17, 21]):
        d.rect(inx + inw - 150 + i * 12, y + 42 - bh, 7, bh, d.P["t2"], radius=2)
    outline_rect(d, inx + inw - 92, y + 28, 34, 18, d.P["t2"], radius=4)
    d.rect(inx + inw - 89, y + 31, 22, 12, d.P["leaf"], radius=2)
    if title:
        tlab(d, tf, tag + "-title", inx + 120, y + 22, inw - 300, 34, title,
             19, d.P["t1"], align="CENTER")
    return y + app_h


def appbar(d, tf, tag, x, y, w, title, sub=None, back=True, action=None):
    if back:
        d.line(x + 34, y + 34, x + 20, y + 48, 4, d.P["t1"])
        d.line(x + 20, y + 48, x + 34, y + 62, 4, d.P["t1"])
    tlab(d, tf, tag + "-t", x + (58 if back else 0), y + 26, w - 200, 40, title,
         26, d.P["t0"], style="BOLD")
    if sub:
        tlab(d, tf, tag + "-s", x + (58 if back else 0), y + 66, w - 200, 26, sub,
             15, d.P["t2"])
    if action:
        chip(d, tf, tag + "-a", x + w - 140, y + 30, 130, 44, action,
             d.P["card"], d.P["leaf"], radius=22)


def tabbar(d, tf, tag, x, y, w, items, active=0, h=104):
    d.rect(x, y, w, h, d.P["card2"])
    d.rect(x, y, w, 2, d.P["border"])
    n = len(items)
    cw = w / n
    for i, it in enumerate(items):
        cx = x + cw * i + cw / 2
        col = d.P["leaf"] if i == active else d.P["t2"]
        glyph(d, tf, tag + "-g%d" % i, cx - 16, y + 22, it[1], col)
        tlab(d, tf, tag + "-l%d" % i, cx - cw / 2 + 6, y + 58, cw - 12, 26, it[0],
             15, col, align="CENTER")


GLYPH = {"tree": "树", "grid": "格", "bell": "铃", "me": "我", "list": "单",
         "map": "图", "chart": "表"}


def glyph(d, tf, tag, x, y, kind, color):
    """极简图标：全部由圆/矩形拼，件内说明其含义（不是装饰）。"""
    if kind == "tree":
        disc(d, x + 16, y + 12, 12, color)
        d.rect(x + 14, y + 22, 4, 14, color)
    elif kind == "grid":
        for i in range(4):
            d.rect(x + (i % 2) * 15, y + (i // 2) * 15, 12, 12, color, radius=3)
    elif kind == "bell":
        disc(d, x + 15, y + 12, 12, color)
        d.rect(x + 6, y + 22, 18, 6, color, radius=3)
    elif kind == "me":
        disc(d, x + 15, y + 9, 8, color)
        d.rect(x + 3, y + 19, 24, 14, color, radius=7)
    elif kind == "list":
        for i in range(3):
            d.rect(x, y + i * 10, 28, 4, color, radius=2)
    elif kind == "map":
        outline_rect(d, x, y, 28, 28, color, radius=4, thick=3)
        disc(d, x + 14, y + 14, 5, color)
    else:
        for i, hh in enumerate([10, 18, 6, 14]):
            d.rect(x + i * 8, y + 26 - hh, 6, hh, color, radius=2)


def field(d, tf, tag, x, y, w, label, value, hint=None, filled=True, h=76,
          unit=None, tone=None):
    """表单字段：标签 + 值 + 可选单位/提示。"""
    tlab(d, tf, tag + "-l", x, y, w, 24, label, 15, d.P["t2"])
    panel(d, x, y + 28, w, h - 34, d.P["card2"], radius=12,
          border="1 SOLID " + (tone or d.P["border"]))
    if filled:
        tlab(d, tf, tag + "-v", x + 18, y + 30, w - (110 if unit else 36), h - 38,
             value, 20, tone or d.P["t0"])
    else:
        tlab(d, tf, tag + "-v", x + 18, y + 30, w - 36, h - 38, value, 20, d.P["t2"])
    if unit:
        tlab(d, tf, tag + "-u", x + w - 104, y + 30, 88, h - 38, unit, 16,
             d.P["t2"], align="END")
    if hint:
        tlab(d, tf, tag + "-h", x, y + h + 2, w, 24, hint, 14, d.P["t2"])


def chip(d, tf, tag, x, y, w, h, s, fg, bg, radius=None, border=None, size=16):
    d.pos(x, y, w, h, d.box(w, h, color=bg, radius=radius if radius is not None
                            else h / 2,
                            inner=d.text(s, fg, size, "BOLD", align="CENTER"),
                            align="CENTER", border=border))


def band_chip(d, tf, tag, x, y, band, w=150, h=42, size=17):
    col = BAND_COLOR[band]
    d.rect(x, y, w, h, col, radius=h / 2)
    tlab(d, tf, tag, x, y, w, h, band, size, "#FFFFFF", align="CENTER")


def kv(d, tf, tag, x, y, w, label, value, size=18, unit=None, color=None, h=44):
    tlab(d, tf, tag + "-l", x, y, w * 0.46, h, label, size - 2, d.P["t2"])
    mono(d, tf, tag + "-v", x + w * 0.44, y, w * 0.4, h, str(value), size + 2,
         color or d.P["t0"], align="END")
    if unit:
        tlab(d, tf, tag + "-u", x + w * 0.86, y, w * 0.14, h, unit, size - 3,
             d.P["t2"])


def card(d, tf, tag, x, y, w, h, title=None, sub=None, radius=18, pad=22):
    panel(d, x, y, w, h, d.P["card"], radius=radius,
          border="1 SOLID " + d.P["border"])
    if title:
        tlab(d, tf, tag + "-t", x + pad, y + 18, w - pad * 2, 30, title, 19,
             d.P["t0"], style="BOLD")
    if sub:
        tlab(d, tf, tag + "-s", x + pad, y + 50, w - pad * 2, 26, sub, 14, d.P["t2"])
    return x + pad, y + (86 if title else 20), w - pad * 2


def hbar(d, tf, tag, x, y, w, h, frac, color, bg=None, radius=None):
    frac = max(0.0, min(1.0, frac))
    r = radius if radius is not None else h / 2
    d.rect(x, y, w, h, bg or d.P["grid"], radius=r)
    if frac > 0:
        d.rect(x, y, max(h, w * frac), h, color, radius=r)


def timeline(d, tf, tag, x, y, w, steps, color=None, dot=13, lab_h=54):
    """横向流程条：steps=[(时间, 名称, 说明)]"""
    n = len(steps)
    col = color or d.P["leaf"]
    seg = w / max(1, n - 1)
    d.rect(x, y + 20, w, 4, d.P["border"])
    for i, (t_, name, note) in enumerate(steps):
        cx = x + seg * i
        d.dot(cx, y + 22, dot, col if i < n - 1 else d.P["amber"])
        mono(d, tf, tag + "-t%d" % i, cx - 62, y, 124, 22, t_, 13, d.P["t2"],
             align="CENTER")
        tlab(d, tf, tag + "-n%d" % i, cx - seg / 2 + 4, y + 34, seg - 8, 26, name,
             15, d.P["t0"], align="CENTER")
        tlab(d, tf, tag + "-d%d" % i, cx - seg / 2 + 4, y + 60, seg - 8, lab_h, note,
             13, d.P["t2"], lines=3, align="CENTER", valign="TOP")


def note_band(d, tf, tag, x, y, w, lines, size=14, h=None):
    hh = h if h else 22 + len(lines) * (size * 1.5 + 6)
    panel(d, x, y, w, hh, d.P["card2"], radius=14,
          border="1 SOLID " + d.P["border"])
    yy = y + 12
    for i, ln in enumerate(lines):
        tlab(d, tf, tag + "-%d" % i, x + 20, yy, w - 40, size * 1.5 + 4, ln, size,
             d.P["t2"], lines=2, valign="TOP")
        yy += size * 1.5 + 4 + (size * 1.5 if len(ln) > w / (size * 1.02) else 0)
    return y + hh


def coltable(d, tf, tag, x, y, w, cols, rows, row_h=40, head_h=34, size=16,
             head_size=15, zebra=True):
    """列定义统一的表：cols=[(label, width, align)]，表头与数值共用同一盒。"""
    tot = sum(c[1] for c in cols)
    if tot != w:
        cols = [c if i else (c[0], c[1] + (w - tot), c[2])
                for i, c in enumerate(cols)]
    xs, acc = [], x
    for _, cw, _ in cols:
        xs.append((acc, cw))
        acc += cw
    d.rect(x, y, w, head_h, d.P["grid"])
    for (cx, cw), (lab, _, al) in zip(xs, cols):
        tlab(d, tf, tag + "-h" + lab, cx + 10, y, cw - 20, head_h, lab, head_size,
             d.P["t1"], align=al)
    for r, row in enumerate(rows):
        ry = y + head_h + r * row_h
        if zebra and r % 2:
            d.rect(x, ry, w, row_h, d.P["card2"])
        for (cx, cw), (lab, _, al), val in zip(xs, cols, row):
            col = None
            if isinstance(val, tuple):
                val, col = val
            mono(d, tf, "%s-r%d-%s" % (tag, r, lab), cx + 10, ry, cw - 20, row_h,
                 str(val), size, col or d.P["t0"], align=al)
    return y + head_h + len(rows) * row_h


# ---------- 树与几何 ----------
def tree_glyph(d, cx, cy, height_px, crown_r, trunk_w, tilt_deg=0.0,
               crown="#3E7C4B", trunk="#6B4A2A", roots=False, lean_dir=1):
    """树：冠幅圆盘 + 主干矩形；倾斜时整株绕根部旋转，冠盘落在旋转后的端点。"""
    if abs(tilt_deg) < 0.05:
        d.rect(cx - trunk_w / 2, cy - height_px, trunk_w, height_px, trunk)
        disc(d, cx, cy - height_px, crown_r, crown)
    else:
        rad = math.radians(tilt_deg) * lean_dir
        co, si = math.cos(rad), math.sin(rad)
        d.pos(cx - trunk_w / 2, cy - height_px, trunk_w, height_px,
              '<Transform matrix="(%s)" alignment="BOTTOM_LEFT">'
              % ("%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1" % (co, si, -si, co))
              + d.box(trunk_w, height_px, color=trunk) + "</Transform>")
        disc(d, cx + math.sin(rad) * height_px, cy - math.cos(rad) * height_px,
               crown_r, crown)
    if roots:
        for off in [-1.6, -0.8, 0.8, 1.6]:
            d.rect(cx + off * trunk_w - 4, cy - 2, 8 + abs(off) * 3, 5, trunk,
                   radius=2)


def disc(d, cx, cy, r, color):
    d.rect(cx - r, cy - r, 2 * r, 2 * r, color, radius=r)


def panel(d, x, y, w, h, fill, radius=None, border=None):
    """带描边的填充盒。"""
    d.pos(x, y, w, h, d.box(w, h, color=fill, radius=radius, border=border))


def outline_rect(d, x, y, w, h, color, radius=None, thick=2):
    """只画描边的盒子（Container border，无填充）。"""
    d.pos(x, y, w, h, d.box(w, h, radius=radius,
                            border="%d SOLID %s" % (thick, color)))


def disc_outline(d, cx, cy, r, thick, color):
    disc(d, cx, cy, r + thick, color)
    disc(d, cx, cy, r, d.bg)


def angle_arc(d, tf, tag, cx, cy, r, deg, color, label=None, steps=26):
    """从竖直方向偏转 deg 的扇形指示（扫描线段近似圆弧）。"""
    for i in range(steps + 1):
        a = math.radians(deg * i / steps)
        x = cx + r * math.sin(a)
        y = cy - r * math.cos(a)
        d.dot(x, y, 5 if i == steps else 3, color)
    d.line(cx, cy, cx, cy - r, 2, d.P["t2"])
    if label:
        mono(d, tf, tag, cx + r * math.sin(math.radians(deg)) + 10,
             cy - r * math.cos(math.radians(deg)) - 12, 120, 26, label, 15, color)


def section(d, tf, tag, x, y, w, idx, title, sub=None, color=None):
    col = color or d.P["leaf"]
    d.rect(x, y + 4, 6, 30, col)
    tlab(d, tf, tag + "-t", x + 20, y, w - 260, 34, "%s %s" % (idx, title), 21,
         d.P["t0"], style="BOLD")
    if sub:
        tlab(d, tf, tag + "-s", x + 20, y + 36, w - 260, 26, sub, 14, d.P["t2"])
    return y + (72 if sub else 46)


def credit(d, tf, tag, x, y, w, lines, size=13):
    for i, ln in enumerate(lines):
        tlab(d, tf, "%s-%d" % (tag, i), x, y + i * (size * 1.5 + 3), w,
             size * 1.5 + 3, ln, size, d.P["t2"], lines=2, valign="TOP")
    return y + len(lines) * (size * 1.5 + 3)
