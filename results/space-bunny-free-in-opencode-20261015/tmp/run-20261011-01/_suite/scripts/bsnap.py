#!/usr/bin/env python
# B 类共用绘图工具：把本套实测过的服务行为固化成一个小工具库。
# 启动基准：总任务根 (suite_root)。
#
# 【本服务实测结论，改动前先读 capability-corrections.md】
# 1) textAlign 的合法枚举是**大写**：START / CENTER / END / JUSTIFY（另有 LEFT/RIGHT）。
#    小写一律 400。默认值就是 START，所以不写 textAlign 即为左对齐。
# 2) 超出 Text 盒子的文字会被**静默裁掉**仍返回 200。盒宽/盒高必须留足余量。
#    24px 字的行高约 31px，一行文本的盒子至少给 34px。
# 3) Positioned 必须是 Stack 的直接子节点，且不能没有子节点。
# 4) ClipPath / ClipRect / ClipRRect / Transform / Image 全部可用；
#    真正不支持的是 Path / Polygon 这类独立标签。
# 5) 根 Container 不给 color 即为真实透明背景。
# 6) Transform.matrix 是列主序 4×4、16 个有限 Float、外层带括号且值间无空格。
from __future__ import annotations

import math

FONT = "Inter,Noto Sans CJK SC"
W600, W500, W400 = "Inter Semi Bold", "Inter Medium", "Inter"

# 深色底为主的调色板
BG = "#0A0F1E"
PANEL = "#121B2E"
PANEL2 = "#18233B"
LINE = "#26324C"
INK = "#F2F6FC"
SUB = "#9AA9BF"
DIM = "#667C99"
SERIES = ["#4C8DFF", "#22C7A9", "#F5A524", "#F45B8C", "#9B6BFF", "#35C4E8"]

# ---- 字宽系数（A14 实测标定，用于判断文字放不放得下）
_EM = {" ": 0.28, ".": 0.40, ",": 0.40, "-": 0.56, "/": 0.40, ":": 0.42,
       "%": 0.90, "(": 0.40, ")": 0.40, "+": 0.70, "·": 1.00, "–": 1.00,
       "→": 1.00, "←": 1.00, "—": 1.00, "×": 0.60, "°": 0.60, "%": 0.90}
_UP = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_LO = set("abcdefghijklmnopqrstuvwxyz")
_DIG = set("0123456789")


def em_width(s: str, size: float) -> float:
    """实测字宽系数估算：CJK 1.0em，空格 0.28，大写 0.70，小写 0.60，数字 0.53。"""
    w = 0.0
    for ch in s:
        if ch == " ":
            w += 0.28
        elif ch in _EM:
            w += _EM[ch]
        elif ord(ch) > 0x2E80:
            w += 1.0
        elif ch in _DIG:
            w += 0.53
        elif ch in _UP:
            w += 0.70
        elif ch in _LO:
            w += 0.60
        else:
            w += 0.56
    return w * size


def wrap(text: str, size: float, width: float):
    """按实测字宽切行；收尾标点悬挂到上行，避免独占一行被裁。"""
    tokens, buf = [], ""
    for ch in text:
        if ord(ch) > 0x2E80 or ch == " ":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    lines, cur, cw = [], "", 0.0
    for tk in tokens:
        w = em_width(tk, size)
        if cur and cw + w > width:
            lines.append(cur)
            cur, cw = tk, w
        else:
            cur += tk
            cw += w
    if cur:
        lines.append(cur)
    hang = "。，、；：？！」』）】"
    merged = []
    for ln in lines:
        if merged and ln and ln[0] in hang:
            merged[-1] += ln[0]
            ln = ln[1:]
            if not ln:
                continue
        merged.append(ln)
    return merged


def rect(x, y, w, h, color, radius=0, border=None, shadow=None):
    c = "" if color is None else f' color="{color}"'
    b = f' border="{border}"' if border else ""
    s = f' boxShadow="{shadow}"' if shadow else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}"{c} borderRadius="{radius}"{b}{s}/>'
            f'</Positioned>')


def circle(cx, cy, d, color, border=None):
    b = f' border="{border}"' if border else ""
    c = "" if color is None else f' color="{color}"'
    return (f'<Positioned left="{cx - d / 2:.2f}" top="{cy - d / 2:.2f}" '
            f'width="{d:.2f}" height="{d:.2f}">'
            f'<Container width="{d:.2f}" height="{d:.2f}"{c} borderRadius="{d / 2}"{b}/>'
            f'</Positioned>')


def txt(t, x, y, w, h, size, color, weight=W500, align=None, lh=None, family=None):
    """文本。h 默认按字号给出安全行高（24px→34px），避免服务端裁掉下缘。

    family 为可选的字体族串；不传时保持原来的 "{weight},{FONT}" 行为
    （新增的是可选参数，对既有调用完全向后兼容）。
    """
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    hh = h if h is not None else max(28, int(size * 1.40))
    fam = family if family else f"{weight},{FONT}"
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{hh:.2f}">'
            f'<Text{a} fontSize="{size}" color="{color}" '
            f'fontFamily="{fam}" text={q}{t}{q}/></Positioned>')


def para(b, t, x, y, w, size, color, weight=W500, align=None, gap=6):
    """多行段落：自己排版、逐行输出，行数由代码决定。返回下一行 y。"""
    for ln in wrap(t, size, w - (em_width("M", size) if align else 0)):
        b.append(txt(ln, x, y, w, None, size, color, weight, align))
        y += int(size * 1.40) + gap
    return y


def bullets(b, items, x, y, w, size, color=INK, dot=None, gap=8, indent=22):
    dot = dot or SERIES[0]
    for it in items:
        lines = wrap(it, size, w - indent)
        b.append(rect(x + 2, y + int(size * 0.52), max(5, size // 5),
                      max(5, size // 5), dot, 3))
        for i, ln in enumerate(lines):
            b.append(txt(ln, x + indent, y, w - indent + 16, None, size, color))
            y += int(size * 1.40)
        y += gap
    return y


def line_h(size):
    return int(size * 1.40)


def fmt(v, nd=0):
    if nd == 0:
        return f"{v:,.0f}"
    return f"{v:,.{nd}f}"


def nice_max(v, step):
    """把 v 向上取整到 step 的整数倍。"""
    return math.ceil(v / step) * step


def segment(x0, y0, x1, y1, color, width=3, radius=None):
    """两点间的实线段。

    容器只有矩形，所以「线」= 一根绕自身中心旋转的长条：
    外层 Positioned 的盒子就是线段的包围盒（左上角 mx−L/2、my−w/2），
    Transform 的局部原点在 alignment="CENTER" 下正好落在盒子中心，
    纯旋转矩阵即可，不需要平移项。
    首版用「每个顶点画一个圆」代替线，渲染出来是一串点，不是线——教训记在这里。
    """
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.01:
        return circle(x0, y0, width, color)
    ang = math.degrees(math.atan2(dy, dx))
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    m = (f"{c:.6f},{s:.6f},0,0,"      # 第一列
         f"{-s:.6f},{c:.6f},0,0,"     # 第二列（屏幕坐标 y 向下 = 顺时针）
         f"0,0,1,0,"
         f"0,0,0,1")
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = f' borderRadius="{radius}"' if radius else ""
    return (f'<Positioned left="{mx - L / 2:.2f}" top="{my - width / 2:.2f}" '
            f'width="{L:.2f}" height="{width:.2f}">'
            f'<Transform matrix="({m})" alignment="CENTER">'
            f'<Container width="{L:.2f}" height="{width:.2f}" color="{color}"{r}/>'
            f'</Transform></Positioned>')


def polyline(points, color, width=3):
    return "".join(segment(points[i][0], points[i][1],
                            points[i + 1][0], points[i + 1][1], color, width)
                   for i in range(len(points) - 1))


def area_band(b, x0, x1, top, bottom, color, radius=0):
    b.append(rect(x0, top, x1 - x0, bottom - top, color, radius))


def vbars(b, x0, y0, y1, values, colors, slot_gap=6, radius=6,
          top_r=None, min_h=0.0):
    """一组竖条。返回每根条的 x 范围，供标注使用。"""
    n = len(values)
    slot = (x1 - x0) / n
    bw = slot - slot_gap
    out = []
    for i, v in enumerate(values):
        bx = x0 + slot * i + slot_gap / 2
        h = max(min_h, y1 - y0)
        b.append(rect(bx, y0, bw, h, colors[i % len(colors)],
                      top_r if top_r is not None else radius))
        out.append((bx, bx + bw))
    return out


def hbars(b, x0, y0, x1, values, colors, row_h, gap=8, radius=5, vmax=None):
    vmax = vmax or max(values) if values else 1
    out = []
    for i, v in enumerate(values):
        ry = y0 + i * (row_h + gap)
        w = (x1 - x0) * (v / vmax if vmax else 0)
        b.append(rect(x0, ry, max(3.0, w), row_h, colors[i % len(colors)], radius))
        out.append((x0, x0 + max(3.0, w), ry, ry + row_h))
    return out


def canvas(w, h, body, bg=BG):
    return (f'<Snapshot type="png">\n'
            f'<Container width="{w}" height="{h}" color="{bg}">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


def header(b, x, y, w, eyebrow, title, sub=None, color=INK, accent=None,
           title_size=46):
    accent = accent or SERIES[0]
    b.append(txt(eyebrow, x, y, w, None, 22, accent, W600))
    b.append(txt(title, x, y + 38, w, None, title_size, color, W600))
    yy = y + 38 + line_h(title_size) + 8
    if sub:
        b.append(txt(sub, x, yy, w, None, 22, SUB))
        yy += line_h(22) + 6
    return yy


def kpi_row(b, x, y, w, items, h=124, gap=14, label_size=20, value_size=30):
    """一排指标卡。items = [(标签, 值, 颜色, 副注|None), ...]

    纵向排布按字号算行高顺次下移，**不**用「底部对齐副注」那套写法：
    那样 30px 的数值会压到 18px 的副注上（首版 104px 高的卡片就是这样错的）。
    现在：标签 y+16 → 值 y+50 → 副注 y+h−30，默认 h=124 时三行互不相交。
    """
    n = len(items)
    cw = (w - gap * (n - 1)) / n
    for i, it in enumerate(items):
        label, value, col = it[0], it[1], it[2]
        sub = it[3] if len(it) > 3 else None
        cx = x + i * (cw + gap)
        b.append(rect(cx, y, cw, h, PANEL, 12))
        b.append(rect(cx, y, cw, 4, col, 2))
        b.append(txt(label, cx + 18, y + 16, cw - 36, None, label_size, SUB))
        b.append(txt(value, cx + 18, y + 16 + line_h(label_size) + 6, cw - 36, None,
                     value_size, col, W600))
        if sub:
            b.append(txt(sub, cx + 18, y + h - 30, cw - 36, None, label_size - 2, DIM))
    return y + h


def footer(b, x, y, w, note):
    b.append(rect(x, y + 6, w, 1, LINE, 0))
    b.append(txt(note, x, y + 16, w, None, 18, DIM))
    return y + 16 + line_h(18)