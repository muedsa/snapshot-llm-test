"""A07 共用绘图原语（network-map 与 travel-card 视觉系统一致）。

所有原语都由探针实测确认（见 a07_probe1..5 的像素级验证）：
  * 轴对齐段：Container 矩形 + borderRadius = lw/2
  * 45° 段：Container transform=mat(θ) + transformAlignment="TOP_LEFT"，
    Positioned 原点 = p1 + (sinθ·lw/2, -cosθ·lw/2)，盒宽 = hypot(dx,dy)
    → 探针 5 实测：远端 Δ ≤ 0.71px，垂直厚度 5.66..7.07（期望 ±7）
  * Stack 后画者在上 → 组装顺序：背景 → 线路 → 站标记 → 标签
  * ClipPath 挂在 Positioned 下会静默不填充；必须嵌在 Container 里（本题未使用）

用法：import a07_style as ST；所有函数返回 DSL 字符串片段。
"""

from __future__ import annotations

import math

FONT = 'fontFamily="Noto Sans CJK SC"'
LW = 14.0                     # 线宽（两图一致）

# 两图共用的视觉系统
BG = "#F8FAFC"
PANEL = "#FFFFFF"
PANEL_EDGE = "#E2E8F0"
INK = "#0F172A"
INK2 = "#475569"
INK3 = "#64748B"
ACC_YES = "#0F766E"           # 无障碍状态核（青）
ACC_NO = "#94A3B8"            # 无无障碍设施核（灰）
ACC_NO_TXT = "#B91C1B"
TRANSFER_RING = "#111827"
RULE_WARN = "#FFFBEB"
RULE_WARN_EDGE = "#F59E0B"
RULE_WARN_TXT = "#92400E"


def n(v: float) -> str:
    """坐标格式：去尾零，不写科学计数法。"""
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def mat(theta_deg: float) -> str:
    """列主序 4×4 flat 矩阵，16 个逗号分隔浮点，无空格。"""
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    return (f"({n(c)},{n(s)},0,0,{n(-s)},{n(c)},0,0,"
            f"0,0,1,0,0,0,0,1)")


def text_w(s: str, size: float) -> float:
    """CJK ≈ 1.02em，拉丁 ≈ 0.56em，空格 ≈ 0.30em 的宽度估算（用于居中与排布）。"""
    w = 0.0
    for ch in s:
        if ord(ch) < 0x2000:
            if ch == " ":
                w += 0.30
            elif ch in "iljI.,!:;|'\"()[]":
                w += 0.30
            else:
                w += 0.56
        else:
            w += 1.02
    return w * size


def box(px, py, w, h, color, radius=0, border=None) -> str:
    r = f' borderRadius="{n(radius)}"' if radius else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}" width="{n(w)}" '
            f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}" '
            f'color="{color}"{r}{b}></Container></Positioned>')


def txt(px, py, s, size=20, color=INK, bold=False) -> str:
    """左上角定位的文本。"""
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}"><Text text="{s}" '
            f'fontSize="{size}"{st} color="{color}" {FONT}></Text></Positioned>')


def _centered(px, py, w, h, s, size, color, bold=True) -> str:
    """在 (px,py,w,h) 的盒子内居中排一行文字（不裁切：盒子即文本容器）。"""
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}" width="{n(w)}" '
            f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}" '
            f'alignment="CENTER"><Text text="{s}" fontSize="{size}"{st} '
            f'color="{color}" {FONT}></Text></Container></Positioned>')


def txt_c(cx, cy, s, size=20, color=INK, bold=False, pad=None) -> str:
    """以 (cx,cy) 为中心的文本；pad 给足余量以免粗体字形被裁切。"""
    pad = size * 0.7 if pad is None else pad
    ww = text_w(s, size) + pad
    hh = size * 1.6
    return _centered(cx - ww / 2, cy - hh / 2, ww, hh, s, size, color, bold)


def pill(left, top, s, size=20, fg=INK, bg=PANEL, pad_x=14, pad_y=8,
         radius=None, border=None) -> str:
    """带底色与内边距的圆角标签；返回 (片段, 宽度, 高度)。"""
    w = text_w(s, size) + pad_x * 2
    h = size * 1.45 + pad_y * 2
    r = radius if radius is not None else h / 2
    b = f' border="{border}"' if border else ""
    return ((f'<Positioned left="{n(left)}" top="{n(top)}" width="{n(w)}" '
             f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}" '
             f'color="{bg}" borderRadius="{n(r)}"{b}></Container></Positioned>'
             + _centered(left, top, w, h, s, size, fg, True)), w, h)


def badge(cx, cy, s, color, d=30.0, fs=20, fg="#FFFFFF", radius=None) -> str:
    """圆形/圆角色块 + 居中白字（线路字母等）。"""
    r = radius if radius is not None else d * 0.3
    return (box(cx - d / 2, cy - d / 2, d, d, color, r)
            + _centered(cx - d / 2, cy - d / 2, d, d, s, fs, fg, True))


def tag(left, top, s, size=20, fg="#FFFFFF", bg=TRANSFER_RING) -> str:
    """圆角角标（查询编号等）：底色与文本容器同尺寸，避免裁切。"""
    w = text_w(s, size) * 1.3 + 18
    h = size * 1.5 + 8
    return (box(left, top, w, h, bg, min(h / 2, 11))
            + _centered(left, top, w, h, s, size, fg, True))


def hseg(x1, x2, cy, color, lw=LW) -> str:
    return box(min(x1, x2), cy - lw / 2, abs(x2 - x1), lw, color, lw / 2)


def vseg(y1, y2, cx, color, lw=LW) -> str:
    return box(cx - lw / 2, min(y1, y2), lw, abs(y2 - y1), color, lw / 2)


def seg(p1, p2, color, lw=LW) -> str:
    """任意 0°/45°/90° 段的统一入口。"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    if abs(dy) < 1e-9:
        return hseg(p1[0], p2[0], p1[1], color, lw)
    if abs(dx) < 1e-9:
        return vseg(p1[1], p2[1], p1[0], color, lw)
    return diag(p1, p2, color, lw)


def diag(p1, p2, color, lw=LW) -> str:
    """45° 段：中心线精确过 p1 与 p2（含圆头）。仅支持 |dx| == |dy|。"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    assert abs(abs(dx) - abs(dy)) < 1e-6, f"非 45° 段：{p1} → {p2}"
    theta = math.degrees(math.atan2(dy, dx))
    t = math.radians(theta)
    ox = p1[0] + math.sin(t) * lw / 2
    oy = p1[1] - math.cos(t) * lw / 2
    return (f'<Positioned left="{n(ox)}" top="{n(oy)}">'
            f'<Container width="{n(math.hypot(dx, dy))}" height="{n(lw)}" '
            f'color="{color}" borderRadius="{n(lw / 2)}" transform="{mat(theta)}" '
            f'transformAlignment="TOP_LEFT"></Container></Positioned>')


def marker(cx, cy, acc: bool, transfer: bool, ring_color: str,
           d=None, bd=None, inner=None) -> str:
    """车站标记：外圈（单线=线路色，换乘=深墨）+ 内核（青=无障碍，灰=无）。"""
    d = d or (34.0 if transfer else 26.0)
    bd = bd or (4.0 if transfer else 3.0)
    inner = inner or (15.0 if transfer else 13.0)
    col = ACC_YES if acc else ACC_NO
    return (box(cx - d / 2, cy - d / 2, d, d, PANEL, d / 2,
                f"{n(bd)} SOLID {ring_color}")
            + box(cx - inner / 2, cy - inner / 2, inner, inner, col, inner / 2))


def label_lines(sid, name, acc: bool):
    """站标签的两行文本与字号：编号+站名 20px，无障碍状态 20px。"""
    l1 = f"{sid} {name}"
    l2 = "无障碍" if acc else "无无障碍设施"
    return l1, l2


def label_line_rects(cx, cy, sid, name, acc: bool, side, nudge=0.0):
    """两行文本各自的矩形 [(left, top, w, h), (left, top, w, h)]。

    布局唯一来源：绘图与像素校验共用，避免两处各算一份。
    """
    l1, l2 = label_lines(sid, name, acc)
    w = max(text_w(l1, 20), text_w(l2, 20))
    h1, gap, h2 = 27.0, 3.0, 27.0
    total = h1 + gap + h2
    if side == "down":
        left, top = cx - w / 2 + nudge, cy + 26
    elif side == "up":
        left, top = cx - w / 2 + nudge, cy - 26 - total
    elif side == "right":
        left, top = cx + 26, cy - total / 2
    else:
        left, top = cx - 26 - w, cy - total / 2
    return [(left, top, text_w(l1, 20), h1),
            (left, top + h1 + gap, text_w(l2, 20), h2)]


def label(cx, cy, sid, name, acc: bool, side, nudge=0.0) -> str:
    """站标签两行：编号+站名与无障碍状态，均 20px（>= 20 的标签要求）。

    side ∈ up/down/left/right；nudge 为水平微调（避让线路）。
    """
    l1, l2 = label_lines(sid, name, acc)
    (l1x, l1y, w1, h1), (l2x, l2y, w2, h2) = label_line_rects(
        cx, cy, sid, name, acc, side, nudge)
    return (txt(l1x, l1y, l1, 20, INK, True)
            + txt(l2x, l2y, l2, 20,
                  ACC_YES if acc else ACC_NO_TXT, True))



def frame(px, py, w, h, color=PANEL, radius=14, border=None) -> str:
    return box(px, py, w, h, color, radius, border or f'1 SOLID {PANEL_EDGE}')


def canvas_open(w, h, bg=BG) -> list[str]:
    return ['<Snapshot background="%s" type="png">' % bg,
            f'<Container width="{n(w)}" height="{n(h)}" color="{bg}">',
            '<Stack fit="EXPAND" clipBehavior="NONE">']


def canvas_close() -> list[str]:
    return ['</Stack>', '</Container>', '</Snapshot>']
