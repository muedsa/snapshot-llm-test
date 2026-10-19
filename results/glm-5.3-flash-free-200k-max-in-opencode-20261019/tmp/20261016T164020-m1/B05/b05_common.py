# -*- coding: utf-8 -*-
"""B05《轮值》组件库——与 B04 同底层的已验证 DSL 写法，附加产品界面构件。

家族色里：
  Inter 字体（num / 纯 ASCII 文本）只放 ASCII；范围 `-`，± 用 `+/-`，
  ¥ 一律写进 CJK 字体（txt），金额 presented as「1,260 元」。
  文本中不出现裸 `<` `&`（服务解析边界，B04 踩坑）。
"""
import os
import math
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
BASE = TASK_ROOT / "outputs" / RUN / "B05"
CJK = "Noto Sans CJK SC"
NUM = "Inter"

CASES = []

# —— 昼夜色语 ——
NAVY = "#0F2440"        # 深夜底
PANEL = "#182F4E"       # 深夜卡
LINE_D = "#26466B"      # 深夜线
TXG = "#F2F6FA"
TXGS = "#9DB2C8"
PAPER = "#F6F2E9"       # 米白底
CARD = "#FFFFFF"
LINE_L = "#DDD5C4"
INK = "#202830"
SUB = "#76808B"
DIM = "#9AA5B0"

GREEN = "#4BAE8C"
AMBER = "#E5A54B"
CORAL = "#E06A57"
GRAY = "#98A2AC"

# —— 成员色码（全刊一致）——
M_BIG = "#5BB7C8"    # 王桁（大哥）
M_MID = "#E06A57"    # 王樾（二哥）
M_YNG = "#E5A54B"    # 王杳（小妹，远程）
M_AIDE = "#8FAE8B"   # 周阿姨（白班帮手）
MEMBERS = [("王桁", M_BIG, "主班"),
           ("王樾", M_MID, "副班"),
           ("王杳", M_YNG, "远程"),
           ("周阿姨", M_AIDE, "白班")]


def case(mark, w, h):
    def deco(fn):
        CASES.append((mark, w, h, fn))
        return fn
    return deco


def fnum(v):
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def rect(s, x, y, w, h, color, radius=0, border=None):
    a = (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(w)}" '
         f'height="{fnum(h)}"><Container width="{fnum(w)}" height="{fnum(h)}"')
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    s.append(a + " /></Positioned>")


def txt(s, x, y, content, size, color, bold=False, family=CJK, align=None,
        box_w=None):
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    if align:
        sty += f' textAlign="{align}"'
    sty += ">"
    if box_w is not None:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}" '
                 f'width="{fnum(box_w)}">{sty}{content}</Text></Positioned>')
    else:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}">{sty}'
                 f'{content}</Text></Positioned>')


def num(s, x, y, content, size, color, bold=False, align=None, box_w=None):
    txt(s, x, y, content, size, color, bold=bold, family=NUM, align=align,
        box_w=box_w)


def wrap_dsl(w, h, body, bg):
    return (f'<Snapshot background="{bg}" type="png">\n<Stack>\n'
            f'<SizedBox width="{w}" height="{h}" />\n' + "\n".join(body) +
            "\n</Stack>\n</Snapshot>\n")


def hill_rows(s, cx, cy, rx, ry, color, step=1):
    rows = int(2 * ry / step)
    for i in range(rows):
        yc = -ry + (i + 0.5) * step
        t = yc / ry
        hw = rx * math.sqrt(max(0.0, 1.0 - t * t))
        if hw > 0.4:
            rect(s, cx - hw, cy + yc, 2 * hw, step, color)


def sample_curve(s, x0, y0, w, h, fn, color, step=1):
    for px in range(0, int(w), step):
        t = px / max(w - 1, 1)
        f = max(0.0, min(1.0, fn(t)))
        ph = f * h
        rect(s, x0 + px, y0 + h - ph, step, max(ph, 1), color)


def poly_rows(s, pts, color, step=1):
    ysmin = min(p[1] for p in pts)
    ysmax = max(p[1] for p in pts)
    edges = [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    y = ysmin
    while y < ysmax:
        yc = y + 0.5
        xs = []
        for (x1, y1), (x2, y2) in edges:
            if (y1 <= yc) != (y2 <= yc):
                t = (yc - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        if len(xs) >= 2:
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                w_seg = xs[k + 1] - xs[k]
                if w_seg > 0.2:
                    rect(s, xs[k], y, w_seg, step, color)
        y += step


def transform_str(m00, m01, m10, m11):
    return (f'({fnum(m00)},{fnum(m01)},0,0,{fnum(m10)},{fnum(m11)},0,0,'
            f'0,0,1,0,0,0,0,1)')


def rot_text(s, cx, cy, content, size, color, deg, bold=False, family=CJK):
    a = math.radians(deg)
    m = transform_str(math.cos(a), math.sin(a), -math.sin(a), math.cos(a))
    bold_attr = ' fontStyle="BOLD"' if bold else ""
    box = max(size * len(content) * 1.15, size * 1.5)
    h = size * 1.6
    s.append(f'<Positioned left="{fnum(cx - box / 2)}" top="{fnum(cy - h / 2)}" '
             f'width="{fnum(box)}" height="{fnum(h)}">'
             f'<Transform matrix="{m}" origin="({fnum(box / 2)},'
             f'{fnum(h / 2)})">'
             f'<Container width="{fnum(box)}" height="{fnum(h)}" '
             f'color="#00000000">'
             f'<Text fontSize="{fnum(size)}" color="{color}" '
             f'fontFamily="{family}"{bold_attr} '
             f'textAlign="CENTER">{content}</Text></Container>'
             f'</Transform></Positioned>')


def line_thick(s, x0, y0, x1, y1, w, color, step=1):
    dx = x1 - x0
    dy = y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    nx = -dy / ln * w / 2
    ny = dx / ln * w / 2
    pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
           (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
    poly_rows(s, pts, color, step)


def stadium(s, cx, cy, length, thick, deg, color):
    a = math.radians(deg)
    m = transform_str(math.cos(a), math.sin(a), -math.sin(a), math.cos(a))
    lw, lh = length, thick
    s.append(f'<Positioned left="{fnum(cx - lw / 2)}" top="{fnum(cy - lh / 2)}" '
             f'width="{fnum(lw)}" height="{fnum(lh)}">'
             f'<Transform matrix="{m}" origin="({fnum(lw / 2)},'
             f'{fnum(lh / 2)})"><Container width="{fnum(lw)}" '
             f'height="{fnum(lh)}" color="{color}" '
             f'borderRadius="{fnum(lh / 2)}" /></Transform></Positioned>')


# ===================== 产品界面构件 =====================

def statusbar(s, w, color, time_str="18:42"):
    """手机顶部简洁状态条：时间 + 电量/信号。"""
    num(s, 28, 14, time_str, 17, color, bold=True)
    # 信号 4 根递减柱
    for i in range(4):
        bh = 6 + i * 3
        rect(s, w - 108 + i * 8, 30 - bh, 5, bh, color)
    # 电池（透明描边 + 电量块，深浅底都成立）
    rect(s, w - 62, 17, 34, 16, "#00000000", 4, border=f'1 SOLID {color}')
    rect(s, w - 59, 20, int(30 * 0.72), 10, color)
    rect(s, w - 26, 21, 3, 8, color)


def app_top(s, w, title, sub, dark=False, y=56, accent=GREEN, tag=None):
    """屏头：状态灯柱 + 大标 + 副标。"""
    rect(s, 20, y, 4, 64, accent)
    txt(s, 36, y + 2, title, 34, TXG if dark else INK, bold=True)
    txt(s, 36, y + 48, sub, 22, TXGS if dark else SUB)
    if tag:
        pill(s, w - 20 - len(tag) * 15 - 32, y + 8, tag, accent,
             dark=dark)


def pill(s, x, y, label, accent, dark=False, size=18):
    """小圆角标签。"""
    wlab = size * len(label) + 26
    fill = ("#00000000") if False else ("#1B3A5E" if dark else "#EFE8D8")
    fg = accent
    rect(s, x, y, wlab, size + 14, fill, size + 14,
         border=f'1.4 SOLID {accent}')
    txt(s, x, y + 7, label, size, fg, bold=True, align="CENTER", box_w=wlab)


def lamp(s, x, y, color, r=7):
    hill_rows(s, x, y, r, r, color, 1)


def person(s, x, y, name, color, tag, dark=False, size=24):
    """成员行：色环头像（首字）+ 名 + 角色词。"""
    d = 30
    rect(s, x, y, d, d, color, d / 2)
    txt(s, x, y + 4, name[0], 17, "#FFFFFF", bold=True, align="CENTER",
        box_w=d)
    txt(s, x + 42, y - 2, name, size, TXG if dark else INK, bold=True)
    txt(s, x + 42, y + size + 6, tag, 18, TXGS if dark else SUB)


def task_row(s, x, y, w, label, state, who=None, time_str=None, size=23):
    """待办行：状态环 + 标签 + 右侧时间/成员胶囊（右列互斥，防重叠）。"""
    col = {"done": GREEN, "doing": AMBER, "missed": CORAL, "todo": GRAY}[state]
    if state == "done":
        rect(s, x, y + 6, 24, 24, col, 12)
        rect(s, x + 6, y + 12, 11, 4.5, "#FFFFFF", 1)
        rect(s, x + 9, y + 15, 4.5, 8, "#FFFFFF", 2)
    elif state == "missed":
        rect(s, x, y + 6, 24, 24, "#00000000", 12,
             border=f'2 SOLID {CORAL}')
        line_thick(s, x + 6.5, y + 12.5, x + 17.5, y + 23.5, 2.2, CORAL)
    else:
        rect(s, x, y + 6, 24, 24, "#00000000", 12,
             border=f'2 SOLID {AMBER if state == "doing" else GRAY}')
        if state == "doing":
            rect(s, x + 7, y + 13, 10, 10, AMBER, 5)
    rx = x + w
    if time_str and not who:  # 时间与成员胶囊二选一，同占右列
        num(s, rx - 66, y + 8, time_str, 17, SUB, align="RIGHT", box_w=66)
        rx -= 76
    if who:
        asize = size - 6
        cw = asize * len(who) + 28
        rect(s, rx - cw, y + 4, cw, asize + 20, "#00000000",
             (asize + 20) / 2, border=f'1.3 SOLID {who_color(who)}')
        txt(s, rx - cw, y + 9, who, asize, who_color(who), bold=True,
            align="CENTER", box_w=cw)
        rx -= cw + 10
    lab_w = max(rx - (x + 34) - 6, 40)
    lab_col = GRAY if state == "done" else INK
    txt(s, x + 34, y + 8, label, size, lab_col, box_w=lab_w)


def who_color(name):
    for n, c, _t in MEMBERS:
        if n in name:
            return c
    return GRAY


def foot(s, w, h, dark=True, note="演示数据 · 虚构人物 · 仅示意照护协调",
         brand="轮值 LUNZHI"):
    bg = NAVY if dark else "#EAE2D0"
    fg = "#8AA3BC" if dark else "#8B8474"
    rect(s, 0, h - 54, w, 54, bg)
    rect(s, 0, h - 54, w, 1.5, LINE_D if dark else LINE_L)
    txt(s, 24, h - 36, brand + " · " + note, 16, fg)


def card(s, x, y, w, h, dark=False, accent=None, r=14):
    fill = PANEL if dark else CARD
    border = f'1 SOLID {LINE_D if dark else LINE_L}'
    if accent:
        border = f'1.5 SOLID {accent}'
    rect(s, x, y, w, h, fill, r, border)


def seg_bar(s, x, y, w, h, segs):
    """水平分段条 segs=[(color, frac), ...]，按比例铺满。"""
    cx = x
    for col, fr in segs:
        seg = max(2, w * fr)
        rect(s, cx, y, seg, h, col)
        cx += seg


def dot_text(s, x, y, dot_color, text, size, color, bold=False, dot_r=6,
             family=None):
    lamp(s, x + dot_r, y + size * 0.75, dot_color, dot_r)
    txt(s, x + dot_r * 2 + 12, y, text, size, color, bold=bold,
        family=family if family else CJK)
