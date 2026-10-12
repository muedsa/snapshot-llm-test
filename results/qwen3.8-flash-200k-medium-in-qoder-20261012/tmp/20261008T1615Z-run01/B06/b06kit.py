"""B06 构件：日常信息"换算层"骨架 + 环形钟/瀑布/阶梯/方糖堆等图形。

沿用 B05 已验证的能力（Stack/Positioned/Container/Text/Transform、borderRadius 画圆、
line 画斜线），并新增本题探针确认的裁剪能力：ClipRect / ClipOval / ClipRRect
（见 tmp/<run>/_suite/docs/parser-tags.html.txt：解析器注册 38 个标签，
ClipPath 只在 Kotlin DSL 中，类 DOM 不可用，因此曲线仍以图元逼近并在件内注明）。
所有文本走 TextFit 闸门。

十件共用同一套演示数据（tmp/<run>/B06/research/demo.json，由 b06data.py 生成）与
同一套"换算层"语言：深墨蓝底 / 面板灰蓝 / 原口径灰 / 换算青 / 行动琥珀 / 警示珊瑚。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03",
           ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from dslkit import Doc, TextFit  # noqa: E402
import b03kit as K  # noqa: E402

BASE = "#0F1417"
PANEL = "#171F24"
PANEL2 = "#1E282E"
PAPER = "#F2F5F6"
CARD = "#FFFFFF"
MUTED = "#7C8A93"
CYAN = "#39C2C0"
GOLD = "#F2A73B"
CORAL = "#E8664F"
GRASS = "#5FBF8A"
VIOLET = "#9A8CD0"
TXT = "#E9EEF1"
SANS = "Inter,Noto Sans CJK SC"
SERIF = "Noto Serif CJK SC"
MONO = "Noto Sans Mono CJK SC"

PAL_LIGHT = {"t0": "#16202A", "t1": "#4A5A66", "t2": "#7C8A93", "axis": "#9AAAB4",
             "grid": "#E2E9EC", "card": CARD, "card2": "#F6F9FA",
             "border": "#D8E1E5", "leaf": GRASS, "amber": GOLD, "rust": CORAL,
             "teal": CYAN, "mist": MUTED, "line": "#D8E1E5",
             "panel": PANEL, "panel2": PANEL2, "ground": PAPER,
             "gold": GOLD, "coral": CORAL, "grass": GRASS, "cyan": CYAN,
             "violet": VIOLET}
PAL_DARK = {"t0": TXT, "t1": "#B6C4CC", "t2": MUTED, "axis": "#4E5F69",
            "grid": "#222E35", "card": PANEL, "card2": "#131B20",
            "border": "#2B3941", "leaf": "#6FD19B", "amber": GOLD,
            "rust": "#F0785F", "teal": CYAN, "mist": MUTED, "line": "#2B3941",
            "panel": PANEL, "panel2": PANEL2, "ground": BASE,
            "gold": GOLD, "coral": CORAL, "grass": GRASS, "cyan": CYAN,
            "violet": VIOLET}

_n = K.n


def doc(w, h, ground="light"):
    if ground == "light":
        return Doc(w, h, bg=PAPER, font=SANS, palette=PAL_LIGHT), TextFit()
    return Doc(w, h, bg=BASE, font=SANS, palette=PAL_DARK), TextFit()


def data():
    res = ROOT / "tmp" / RID / "B06" / "research"
    return json.load(open(res / "demo.json", encoding="utf-8"))


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


# ---------- B06 新增：裁剪与"换算"图形 ----------
def pos_raw(x, y, w, h, inner):
    """返回 Positioned 字符串但不落到根 Stack（裁剪层内部要自己组 Stack）。

    探针实测：`<ClipRect><Positioned/></ClipRect>` 会报
    `renderBox.parentData must be StackParentData`（HTTP 400 RENDER_ERROR）——
    裁剪标签不是 Stack，里面的 Positioned 必须再包一层 Stack。
    """
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">%s</Positioned>'
            % (_n(x), _n(y), _n(w), _n(h), inner))


def wrap(d, x, y, w, h, tag, attrs, inner):
    """在 Positioned 盒子里放一个裁剪/滤镜标签，内部包一层 Stack 再放内容。"""
    a = "".join(' %s="%s"' % (k, v) for k, v in attrs.items() if v is not None)
    body = "<Stack>%s</Stack>" % inner if "Positioned" in inner else inner
    d.pos(x, y, w, h, "<%s%s>%s</%s>" % (tag, a, body, tag))
    return y + h


def clip_rect(d, x, y, w, h, inner, clip="HARD_EDGE"):
    """ClipRect：把子内容裁到本盒子范围，做进度窗/瀑布断口。"""
    return wrap(d, x, y, w, h, "ClipRect", {"clipBehavior": clip}, inner)


def clip_oval(d, x, y, w, h, inner, clip="ANTI_ALIAS"):
    """ClipOval：椭圆裁剪，做半圆仪表与镜头式遮罩。"""
    return wrap(d, x, y, w, h, "ClipOval", {"clipBehavior": clip}, inner)


def half_disc(d, x, y, w, h, color, side="top", mask=None):
    """半圆盘（约定 h == w/2）：整盘 + 底色遮罩。

    探针实测 ClipRect 会把超尺寸子内容按底部对齐，裁出来是下半盘而不是上半盘，
    所以这里不依赖裁剪，改成可预测的遮罩画法；mask 必须传所在区域的底色。
    """
    r = w / 2.0
    disc(d, x + r, y + h, r, color)
    mg = mask if mask is not None else d.P["ground"]
    if side == "top":
        d.pos(x - 2, y + h, w + 4, h + 4, d.box(w + 4, h + 4, color=mg))
    else:
        d.pos(x - 2, y - 4, w + 4, h + 4, d.box(w + 4, h + 4, color=mg))
    return y + h


def pie_ring(d, cx, cy, r_out, r_in, a0, a1, color, steps=None):
    """圆环扇区：沿弧铺径向厚线段，段厚＝环宽 ×1.25，拼成实心带。

    服务类 DOM 解析器只有 ClipRect/ClipOval/ClipRRect，没有矢量 path，
    因此曲线与扇形一律图元逼近；交付件内需注明。步数按"弧长≈环宽"自动取，
    再密只会让 DSL 变大而看不出差别。
    """
    span = a1 - a0
    ring = max(2.0, r_out - r_in)
    rm = (r_out + r_in) / 2.0
    if steps is None:
        # 弦长取 0.5×环宽：再稀就会看成一块块方砖（探针 v04b 实测）
        step_deg = max(1.0, math.degrees(0.5 * ring / rm))
        steps = max(3, int(abs(span) / step_deg))
    for i in range(steps):
        t0, t1 = (a0 + span * i / steps, a0 + span * (i + 1) / steps)
        a, b = math.radians(t0), math.radians(t1)
        d.line(cx + rm * math.cos(a), cy + rm * math.sin(a),
               cx + rm * math.cos(b), cy + rm * math.sin(b), ring * 1.06, color)


def clock_ticks(d, cx, cy, r_out, r_in, every=15, color=None, major_every=60,
                major=None):
    """24 h 盘上的刻度：every 分钟一小格，major_every 一大格。"""
    color = color or d.P["axis"]
    major = major or d.P["t1"]
    m = 0
    while m <= 1440:
        ang = -90.0 + 360.0 * m / 1440.0
        big = (m % major_every == 0)
        r0 = r_in if big else r_in + (r_out - r_in) * 0.45
        a = math.radians(ang)
        d.line(cx + r0 * math.cos(a), cy + r0 * math.sin(a),
               cx + r_out * math.cos(a), cy + r_out * math.sin(a),
               3.0 if big else 1.5, major if big else color)
        m += every
    return r_out


def step_fn(d, tf, tag, x, y, w, h, segs, color, axis=None):
    """分段计费/阶梯价：segs = [(长度比例, 高度比例, 标签)]，返回底线 y。"""
    axis = axis or d.P["axis"]
    base = y + h
    d.line(x, base, x + w, base, 2, axis)
    cx = x
    for frac, hfrac, _lab in segs:
        sw = w * frac
        sh = h * hfrac
        d.rect(cx, base - sh, sw - 2, sh, color)
        cx += sw
    return base


def waterfall(d, tf, tag, x, y, w, rows, up, down, row_h=52, gap=10, size=15):
    """价格瀑布：rows = [(名称, 金额, 累计)]，up 加钱、down 减钱。"""
    cy = y
    for i, (name, amt, cum) in enumerate(rows):
        col = up if amt >= 0 else down
        d.rect(x, cy + 6, 6, row_h - 12, col)
        tlab(d, tf, tag + "-n%d" % i, x + 16, cy, w - 190, row_h, name, size, d.P["t0"])
        num(d, tf, tag + "-a%d" % i, x + w - 170, cy, 90, row_h,
            ("+" if amt >= 0 else "-") + fmt(abs(amt), 2), size + 1, col)
        num(d, tf, tag + "-c%d" % i, x + w - 74, cy, 74, row_h, fmt(cum, 2), size + 1,
            d.P["t1"])
        cy += row_h + gap
    return cy


def cube_stack(d, tf, tag, x, y_bottom, n, cube=22, gap=3, per_row=6, color=None,
               edge=None):
    """方糖堆：n 块按每行 per_row 堆叠，返回顶部 y。"""
    color = color or d.P["card2"]
    edge = edge or d.P["teal"]
    for i in range(n):
        r, c = divmod(i, per_row)
        bx = x + c * (cube + gap)
        by = y_bottom - (r + 1) * (cube + gap)
        d.rect(bx, by, cube, cube, color, radius=4)
        outline_rect(d, bx, by, cube, cube, edge, radius=4, thick=2)
        d.line(bx + 3, by + cube - 4, bx + cube - 4, by + 3, 1.5, edge)
    rows = (n + per_row - 1) // per_row
    return y_bottom - rows * (cube + gap)


def diverging_bar(d, tf, tag, x, y, w, zero_frac, value_frac, h, pos, neg,
                  radius=None):
    """以 zero_frac 为零点的发散条：value_frac 为正向右、为负向左。"""
    zx = x + w * zero_frac
    d.line(zx, y - 6, zx, y + h + 6, 2, d.P["axis"])
    if value_frac >= 0:
        d.rect(zx, y, max(2.0, w * value_frac), h, pos, radius=radius)
    else:
        d.rect(zx + w * value_frac, y, max(2.0, -w * value_frac), h, neg, radius=radius)
    return zx


def punch_card(d, tf, tag, x, y, w, h, r=13, color=None):
    """核对打孔卡：左缘一排圆孔，暗示可逐项打勾。"""
    color = color or d.P["border"]
    panel(d, x, y, w, h, d.P["card"], radius=14, border="2 SOLID " + d.P["border"])
    cy = y + 34
    while cy < y + h - 20:
        disc(d, x + 26, cy, r, color)
        cy += 46
    return y + h


def matrix(d, x, y, w, h, inner, rot=0.0, sx=1.0, sy=1.0, kx=0.0, tx=0.0, ty=0.0):
    """`<Transform matrix="(16 个列主序 Float)">`。

    已回查 parser-tags：`Transform.matrix` 要列主序 4×4、16 个有限 Float、外层带括号、
    逗号后不能有空格；平移在第 4 列（索引 12、13）。`alignment` 必须显式 TOP_LEFT，
    否则内容按盒子中心旋转（dslkit.Doc.line 同规则）。
    """
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    ux, uy = sx * c, sx * s
    vx, vy = sy * (kx * c - s), sy * (kx * s + c)
    col = ["%.6f" % ux, "%.6f" % uy, "0", "0",
           "%.6f" % vx, "%.6f" % vy, "0", "0",
           "0", "0", "1", "0",
           "%.6f" % tx, "%.6f" % ty, "0", "1"]
    seg = ('<Transform matrix="(%s)" alignment="TOP_LEFT">%s</Transform>'
           % (",".join(col), inner))
    d.pos(x, y, w, h, seg)
    return y + h
