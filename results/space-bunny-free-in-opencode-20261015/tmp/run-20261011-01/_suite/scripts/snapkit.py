#!/usr/bin/env python
"""snapkit — Snapshot 类 DOM DSL 的构造库（纯字符串生成，无外部绘图）。

路径基准：模块本身不含机器路径；由调用方以相对 suite_root 的路径读写。

设计要点（来自 https://snapshot.muedsa.com/ 实测）：
  * `Stack` 不支持 width/height，必须用 SizedBox 包住并设 `fit="EXPAND"`。
  * 精确坐标一律用 `Positioned`（left/top/width/height，叠加在 SizedBox 坐标系内）。
  * 柱值标签放在柱顶之上，负值放柱底之下，避免与坐标轴/月份标签重叠。
  * 表格数字列用 SizedBox 固定宽 + `textAlign="RIGHT"` 对齐。
  * 中文必须显式 fontFamily（Noto Sans/Serif CJK SC）。
  * 解析器无 ClipPath/多边形，所有图形由 Container/ClipOval/ClipRRect/渐变拼装。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence

# ---------------------------------------------------------------- 基础工具

def esc(text) -> str:
    """XML 文本转义。"""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt_int(v) -> str:
    return f"{int(round(float(v))):,}"


def fmt_num(v, digits: int = 2) -> str:
    return f"{float(v):,.{digits}f}"


def fmt_pct(v, digits: int = 2) -> str:
    return f"{float(v) * 100:.{digits}f}%"


def wan(yuan) -> float:
    """元 -> 万元。"""
    return float(yuan) / 10000.0


def attrs(**kw) -> str:
    """把关键字参数转成属性串；None 值跳过。顺序按传入顺序。"""
    parts = []
    for k, v in kw.items():
        if v is None:
            continue
        parts.append(f'{k}="{esc(v)}"')
    return (" " + " ".join(parts)) if parts else ""


def indent(text: str, level: int = 1) -> str:
    pad = "  " * level
    return "\n".join(pad + line for line in text.splitlines())


# ---------------------------------------------------------------- 颜色/字体

class C:
    """常用配色（CSS 写法，8 位为 #RRGGBBAA）。"""

    INK = "#0F172A"
    INK2 = "#1E293B"
    SLATE = "#334155"
    MUTED = "#64748B"
    FAINT = "#94A3B8"
    LINE = "#E2E8F0"
    GRID = "#EEF2F7"
    PAPER = "#FFFFFF"
    CANVAS = "#F1F5F9"
    BLUE = "#2563EB"
    BLUE_L = "#DBEAFE"
    CYAN = "#0891B2"
    GREEN = "#059669"
    GREEN_L = "#D1FAE5"
    AMBER = "#D97706"
    AMBER_B = "#F59E0B"
    RED = "#DC2626"
    ROSE = "#E11D48"
    VIOLET = "#7C3AED"
    INDIGO = "#4F46E5"
    PINK = "#DB2777"


# 字体族（来自服务 GET /fonts 实际返回，共 27 个）
F_SANS = "Noto Sans CJK SC"
F_SERIF = "Noto Serif CJK SC"
F_MONO = "Noto Sans Mono CJK SC"
F_LATIN = "Inter"
F_LATIN_SB = "Inter Semi Bold"
F_LATIN_BK = "Inter Black"
F_LATIN_MD = "Inter Medium"
F_LATIN_LT = "Inter Light"
F_LATIN_EB = "Inter Extra Bold"
F_DEJA = "DejaVu Sans"
F_DEJA_MONO = "DejaVu Sans Mono"
# 拉丁粗体 + 中文回退（逗号两侧不加空格：解析器不会 trim 每个字体名）
F_HEAD = f"{F_LATIN_SB},{F_SANS}"
F_BODY = f"{F_SANS}"
F_NUM = f"{F_LATIN_MD},{F_SANS}"
F_MONO_SANS = f"{F_DEJA_MONO},{F_SANS}"


# ---------------------------------------------------------------- 线性比例

@dataclass
class Scale:
    """值 -> 像素的线性映射（像素 y 向下增长）。"""

    vmin: float
    vmax: float
    ptop: float
    pbottom: float
    clamp: bool = False

    def y(self, v: float) -> float:
        span = self.vmax - self.vmin
        if span == 0:
            return (self.ptop + self.pbottom) / 2.0
        t = (float(v) - self.vmin) / span
        if self.clamp:
            t = min(1.0, max(0.0, t))
        return self.pbottom - t * (self.pbottom - self.ptop)

    def h(self, v: float) -> float:
        """值 -> 以零线为基的高度（正值向上，负值向下）。"""
        return self.ptop - self.y(v)

    def x(self, i: int, n: int, left: float, width: float, pad_ratio: float = 0.0) -> float:
        """第 i 个（共 n 个）在 [left, left+width] 内的槽中心 x。"""
        usable = width * (1 - 2 * pad_ratio)
        slot = usable / max(1, n)
        return left + usable * pad_ratio + slot * (i + 0.5)


def nice_ticks(vmin: float, vmax: float, target: int = 5, zero_base: bool = True):
    """返回 (tick 值列表, 轴下界, 轴上界)，刻度取 1/2/2.5/5×10^k 的整齐值。

    zero_base=True  -> 轴从 0 起（柱图必须如此）
    zero_base=False -> 轴包住 [vmin,vmax]（比率类折线图可用，但必须显式标注非零起点）
    """
    if vmax == vmin:
        vmax = vmin + (abs(vmin) * 0.1 if vmin else 1.0)
    raw = (vmax - vmin) / max(1, target)
    if raw <= 0:
        raw = abs(vmax) or 1.0
    exp = math.floor(math.log10(raw))
    mag = 10.0 ** exp
    step = 10.0 * mag
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if raw <= step * 1.0000001:
            break
    if zero_base:
        lo = 0.0 if vmin >= 0 else step * math.floor(vmin / step)
    else:
        lo = step * math.floor(vmin / step)
    hi = lo
    guard = 0
    while hi < vmax and guard < 1000:
        hi += step
        guard += 1
    ticks, t = [], lo
    while t <= hi + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    return ticks, lo, hi


# ---------------------------------------------------------------- 原子构件

def text(value, *, size=20, color=C.INK, family=F_BODY, weight=None, align=None,
         width=None, height=None, style=None, spacing=None, line_height=None,
         max_lines=None, decoration=None, decoration_color=None,
         decoration_thickness=None, shadow=None, x=None, y=None, left=None, top=None,
         extra=None) -> str:
    """一个 Text。x/y 与 left/top 互斥：给出后外包一层 Positioned。"""
    kw = {
        "fontSize": size,
        "color": color,
        "fontFamily": family,
        "fontStyle": style,
        "textAlign": align,
        "letterSpacing": spacing,
        "height": line_height,
        "maxLines": max_lines,
        "decoration": decoration,
        "decorationColor": decoration_color,
        "decorationThickness": decoration_thickness,
        "textShadow": shadow,
    }
    # 注意：Text 的 `text` 属性与子文本内容同时存在会重复渲染（v1 实测）。
    # 这里只用子文本内容。
    inner = f"<Text{attrs(**kw)}>{esc(value)}</Text>"
    if left is None and top is None:
        return inner
    lx = left if left is not None else x
    ly = top if top is not None else y
    return f"<Positioned{attrs(left=lx, top=ly, width=width, height=height)}>{inner}</Positioned>"


def box(w=None, h=None, *, color=None, radius=None, border=None, left=None, top=None,
        shadow=None, gradient=None, stops=None, gtype=None, gbegin=None, gend=None,
        clip=None, opacity=None, extra=None, as_positioned=False, alignment=None,
        pad=None, border_sides=None) -> str:
    """一个 Container；as_positioned=True 时外包 Positioned。"""
    kw = {
        "width": w, "height": h, "color": color,
        "borderRadius": radius, "boxShadow": shadow,
        "gradientType": gtype, "gradientColors": gradient, "gradientStops": stops,
        "gradientBegin": gbegin, "gradientEnd": gend,
        "clipBehavior": clip, "alignment": alignment, "padding": pad,
    }
    if border:
        kw["border"] = border
    if border_sides:
        kw.update(border_sides)
    if extra:
        kw.update(extra)
    inner = f"<Container{attrs(**kw)}/>"
    if as_positioned or left is not None or top is not None:
        return f"<Positioned{attrs(left=left, top=top, width=w, height=h)}>{inner}</Positioned>"
    return inner


def hline(w, *, color=C.LINE, thickness=1, left=None, top=None, radius=None) -> str:
    return box(w, thickness, color=color, radius=radius, left=left, top=top)


def vline(h, *, color=C.LINE, thickness=1, left=None, top=None) -> str:
    return box(thickness, h, color=color, left=left, top=top)


def dot(d, *, color=C.BLUE, left=None, top=None, ring=None, ring_w=3) -> str:
    """圆点：ClipOval 包裹实心方块（解析器无圆形 Container）。"""
    if ring:
        inner = f'<ClipRRect borderRadius="{d / 2}" clipBehavior="ANTI_ALIAS">{box(d, d, color=color)}</ClipRRect>'
        node = f"<Container{attrs(width=d + 2 * ring_w, height=d + 2 * ring_w, color=ring, borderRadius=(d + 2 * ring_w) / 2, alignment='CENTER')}>{inner}</Container>"
    else:
        node = f'<ClipOval><Container{attrs(width=d, height=d, color=color)}/></ClipOval>'
    if left is None and top is None:
        return node
    return f"<Positioned{attrs(left=left, top=top)}>{node}</Positioned>"


def ring(d, thickness, color, *, left=None, top=None, arc=None) -> str:
    """圆环 = 外圆裁剪 + 反色内圆（Sweep 渐变可做弧段，见 sweep_arc）。"""
    node = (
        f'<ClipOval><Container{attrs(width=d, height=d, color=color)}/></ClipOval>'
    )
    if left is None and top is None:
        return node
    return f"<Positioned{attrs(left=left, top=top)}>{node}</Positioned>"


def sweep_arc(d, start_deg: float, sweep_deg: float, colors: Sequence[str],
              *, stops=None, left=None, top=None, background="#FFFFFF") -> str:
    """SWEEP 渐变裁出圆环弧段（起始角自 12 点方向顺时针，单位度）。

    解析器没有 path/arc，故用 SWEEP 渐变填充整圆盘 + 反色内圆挖空来近似圆环。
    background 必须是弧段下方实际可见的背景色。
    """
    import math

    start = math.radians(start_deg)
    end = math.radians(start_deg + max(sweep_deg, 0.01))
    grad_cols = list(colors) if colors else [C.LINE]
    grad_stops = list(stops) if stops else [
        round(i / max(1, len(grad_cols) - 1), 6) for i in range(len(grad_cols))
    ]
    disk = (
        f'<Container width="{d}" height="{d}" gradientType="SWEEP" '
        f'gradientColors="{esc(",".join(grad_cols))}" '
        f'gradientStops="{esc(",".join(str(s) for s in grad_stops))}" '
        f'gradientStartAngle="{start:.5f}" gradientEndAngle="{end:.5f}"/>'
    )
    inner = d * 0.62
    node = (
        f'<ClipOval>{disk}</ClipOval>'
        f'<Positioned left="{(d - inner) / 2:.2f}" top="{(d - inner) / 2:.2f}">'
        f'<ClipOval><Container width="{inner:.2f}" height="{inner:.2f}" color="{background}"/></ClipOval>'
        f"</Positioned>"
    )
    if left is None and top is None:
        return f'<Container width="{d}" height="{d}">{node}</Container>'
    return f"<Positioned{attrs(left=left, top=top)}><Container width=\"{d}\" height=\"{d}\">{node}</Container></Positioned>"


def legend(items: Sequence[tuple], *, left=0, top=0, size=17, gap=26,
           color=C.SLATE, swatch=14, shape="rect") -> str:
    """图例：items = [(颜色, 文字[, 形状])]，形状 rect/line/dot。"""
    parts = []
    for it in items:
        col = it[0]
        label = it[1]
        sh = it[2] if len(it) > 2 else shape
        if sh == "line":
            mark = box(swatch + 12, 4, color=col, radius=2)
        elif sh == "dot":
            mark = dot(swatch, color=col)
        else:
            mark = f'<Container width="{swatch}" height="{swatch}" color="{col}" borderRadius="3"/>'
        parts.append(
            f'<Row crossAxisAlignment="CENTER">{mark}'
            f'<SizedBox width="8" />{text(label, size=size, color=color, family=F_BODY)}</Row>'
        )
    if len(parts) > 1:
        inner = f'<Column mainAxisAlignment="START">{parts[0]}'
        for p in parts[1:]:
            inner += f'<SizedBox height="{gap}" />{p}'
        inner += "</Column>"
    else:
        inner = f'<Column mainAxisAlignment="START">{parts[0]}</Column>'
    return f"<Positioned{attrs(left=left, top=top)}>{inner}</Positioned>"


# ---------------------------------------------------------------- 图表：竖向柱图

def vbar_chart(labels: Sequence[str],
               series: Sequence[tuple],
               *,
               width=760, height=320,
               plot_left=64, plot_right=18, plot_top=34, plot_bottom=44,
               value_fmt=lambda v: fmt_int(v),
               axis_fmt=lambda v: fmt_int(v),
               show_values=True,
               value_size=15,
               label_size=17,
               tick_size=16,
               tick_target=5,
               force_zero=True,
               axis_title=None,
               bar_gap=6,
               unit_note=None) -> str:
    """竖向（可分组）柱图。

    series: [(名字, 颜色, [值...]), ...]
    返回 `<Container width height>...<Stack fit="EXPAND">...</Stack></Container>`。
    数值标签置于柱顶之上 / 负柱之下，保证不压坐标轴与月份标签。
    """
    n = len(labels)
    m = len(series)
    all_vals = [v for _, _, vals in series for v in vals]
    vmin_raw, vmax_raw = min(all_vals), max(all_vals)
    if force_zero:
        vmin_raw = min(0.0, vmin_raw)
        vmax_raw = max(0.0, vmax_raw)
    ticks, lo, hi = nice_ticks(vmin_raw, vmax_raw, tick_target)
    # 顶部至少留出 12% 余量，保证数值标签有位置
    if hi <= vmax_raw:
        hi = hi + (hi - lo) * 0.12
        ticks, lo, hi = nice_ticks(lo, hi, tick_target)
    ptop = plot_top
    pbot = height - plot_bottom
    sc = Scale(lo, hi, ptop, pbot)

    inner = []
    # 网格线 + y 轴刻度
    for t in ticks:
        y = round(sc.y(t), 2)
        if y < ptop - 1 or y > pbot + 1:
            continue
        is_zero = abs(t) < 1e-9
        inner.append(hline(width - plot_left - plot_right,
                           color="#CBD5E1" if is_zero else C.GRID,
                           thickness=1.6 if is_zero else 1,
                           left=plot_left, top=y - (0.8 if is_zero else 0.5)))
        lbl = axis_fmt(t)
        wpx = max(30, 11.5 * len(lbl) + 6)
        inner.append(text(lbl, size=tick_size, color=C.FAINT, family=F_NUM,
                          align="RIGHT", left=plot_left - wpx - 8, top=y - tick_size / 2 - 1,
                          width=wpx, height=tick_size + 6))

    pw = width - plot_left - plot_right
    slot = pw / max(1, n)
    group_w = slot * 0.62
    bw = (group_w - bar_gap * (m - 1)) / m if m else 0

    for i in range(n):
        cx = plot_left + slot * (i + 0.5)
        gx = cx - group_w / 2
        for j, (name, col, vals) in enumerate(series):
            v = vals[i]
            x = gx + j * (bw + bar_gap)
            yv = sc.y(v)
            zero_y = sc.y(0.0)
            top_y = min(yv, zero_y)
            bh = abs(zero_y - yv)
            if bh < 0.6:
                bh = 1.2
            extra = ({"borderRadiusTopLeft": 4, "borderRadiusTopRight": 4}
                     if (bh > 6 and v >= 0) else None)
            if bh > 6 and v < 0:
                extra = {"borderRadiusBottomLeft": 4, "borderRadiusBottomRight": 4}
            inner.append(box(round(bw, 2), round(bh, 2), color=col,
                            left=round(x, 2), top=round(top_y, 2), extra=extra))
            if show_values and bw >= 20:
                lbl = value_fmt(v)
                tw = max(34, 9.8 * len(lbl) + 10)
                if v >= 0:
                    ly = top_y - value_size - 7
                else:
                    ly = top_y + bh + 3
                ly = min(max(ly, 1.0), height - value_size - 7)
                inner.append(text(lbl, size=value_size, color=C.SLATE, family=F_NUM,
                                  align="CENTER",
                                  left=clamp_label(x + bw / 2 - tw / 2, tw, width),
                                  top=round(ly, 2), width=tw, height=value_size + 6))

    # 月份标签
    for i, lb in enumerate(labels):
        cx = plot_left + slot * (i + 0.5)
        tw = min(slot - 4, len(str(lb)) * (label_size * 0.58) + 12)
        inner.append(text(lb, size=label_size, color=C.SLATE, family=F_NUM, align="CENTER",
                          left=clamp_label(cx - tw / 2, tw, width),
                          top=round(pbot + 10, 2), width=tw, height=label_size + 6))

    if axis_title:
        inner.append(text(axis_title, size=15, color=C.FAINT, family=F_BODY,
                          left=plot_left - 56, top=2))
    if unit_note:
        inner.append(text(unit_note, size=15, color=C.FAINT, family=F_BODY,
                          align="RIGHT", left=width - plot_right - 190, top=2,
                          width=190, height=20))

    stack = f'<Stack fit="EXPAND">{"".join(inner)}</Stack>'
    return f'<Container width="{width}" height="{height}">{stack}</Container>'


# ---------------------------------------------------------------- 图表：折线

def vline_chart(labels: Sequence[str],
                series: Sequence[tuple],
                *,
                width=520, height=300,
                plot_left=58, plot_right=20, plot_top=30, plot_bottom=42,
                value_fmt=lambda v: fmt_num(v, 2),
                axis_fmt=lambda v: fmt_num(v, 1),
                tick_target=4,
                show_values=True,
                value_size=14,
                label_size=17,
                tick_size=16,
                ref_badge="left",
                markers="dot",
                area=False,
                area_alpha="#2563EB26",
                line_w=2.8,
                zero_base=False,
                y_min=None, y_max=None,
                ref_lines=(),
                unit_note=None) -> str:
    """折线 / 面积图。

    series: [(名字, 颜色, [值...], 点样式?)]，点样式 dot / sq / none。
    zero_base=False 时轴不强制从 0 起——调用方必须用 unit_note 显式标注非零起点。
    ref_lines: [(值, 颜色, 文案)]，画贯穿的参考线（用于总体均值等）。
    """
    n = len(labels)
    vals_all = [v for _, _, vs, *_ in series for v in vs]
    vmin = min(vals_all) if y_min is None else y_min
    vmax = max(vals_all) if y_max is None else y_max
    ticks, lo, hi = nice_ticks(vmin, vmax, tick_target, zero_base=zero_base)
    ptop, pbot = plot_top, height - plot_bottom
    sc = Scale(lo, hi, ptop, pbot)
    pw = width - plot_left - plot_right
    step = pw / max(1, n - 1) if n > 1 else 0

    inner = []
    for t in ticks:
        y = round(sc.y(t), 2)
        if y < ptop - 1 or y > pbot + 1:
            continue
        inner.append(hline(pw, color=C.GRID, thickness=1, left=plot_left, top=y))
        lbl = axis_fmt(t)
        wpx = max(30, 10.5 * len(lbl) + 6)
        inner.append(text(lbl, size=tick_size, color=C.FAINT, family=F_NUM, align="RIGHT",
                          left=plot_left - wpx - 8, top=y - tick_size / 2 - 1,
                          width=wpx, height=tick_size + 6))

    # 参考线（画在数据线下方）
    for rv, rcol, rlabel in ref_lines:
        y = sc.y(rv)
        if ptop - 2 <= y <= pbot + 2:
            n_dash = 26
            seg = pw / n_dash
            for k in range(n_dash):
                inner.append(box(seg * 0.55, 2, color=rcol, radius=1,
                                 left=round(plot_left + k * seg, 2), top=round(y - 1, 2)))
            if rlabel and ref_badge != "none":
                lw = max(56, 13 * len(rlabel) + 14)
                bx = plot_left + 4 if ref_badge == "left" else plot_left + pw - lw - 2
                inner.append(f'<Positioned left="{round(bx, 2)}" top="{round(y - 19, 2)}" '
                             f'width="{lw}" height="18">'
                             f'<Container width="{lw}" height="18" color="{rcol}" borderRadius="4" alignment="CENTER">'
                             f'<Text fontSize="12" color="#FFFFFF" fontFamily="{F_BODY}">{esc(rlabel)}</Text>'
                             f'</Container></Positioned>')

    # 面积：自轴底(lo)填充到折线，用旋转矩形段近似斜边不可靠，故按列竖条填充
    for item in series:
        name, col, vs = item[0], item[1], item[2]
        P = [(plot_left + step * i, sc.y(v)) for i, v in enumerate(vs)]
        base_y = pbot
        if area:
            cols = []
            for i, (x, y) in enumerate(P):
                top_y = min(y, base_y)
                wpx = max(3.0, step * 0.86)
                cols.append(box(round(wpx, 2), round(base_y - top_y, 2), color=area_alpha,
                                left=round(x - wpx / 2, 2), top=round(top_y, 2)))
            # 这些已经是 Positioned，直接并入外层 Stack（不能塞进 Container）
            inner.extend(cols)
        # 折线段：绕段中点旋转的细矩形
        for i in range(len(P) - 1):
            x1, y1 = P[i]
            x2, y2 = P[i + 1]
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length < 0.01:
                continue
            # 屏幕坐标 y 向下：单位向量 (1,0) 应映到 (dx/len, dy/len)，
            # 即旋转角 θ = +atan2(dy, dx)（不要再取负号）。
            ang = math.degrees(math.atan2(dy, dx))
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            seg_w = length + line_w
            m = rot_matrix(ang)
            inner.append(
                f'<Positioned left="{round(cx - seg_w / 2, 2)}" top="{round(cy - line_w / 2, 2)}">'
                f'<Transform matrix="{m}" alignment="CENTER">'
                f'<Container width="{round(seg_w, 2)}" height="{line_w}" '
                f'color="{col}" borderRadius="{line_w / 2}"/></Transform></Positioned>'
            )
        mk = item[3] if len(item) > 3 else "dot"
        if markers and mk == "dot":
            for (x, y) in P:
                inner.append(dot(line_w * 2 + 5, color=C.PAPER, left=round(x - (line_w * 2 + 5) / 2, 2),
                                 top=round(y - (line_w * 2 + 5) / 2, 2), ring=col, ring_w=line_w))
        elif mk == "sq":
            for (x, y) in P:
                inner.append(box(10, 10, color=col, radius=2, left=round(x - 5, 2), top=round(y - 5, 2)))
        if show_values:
            for i, (x, y) in enumerate(P):
                lbl = value_fmt(vs[i])
                tw = max(34, 10.0 * len(lbl) + 12)
                inner.append(text(lbl, size=value_size, color=col, family=F_NUM, align="CENTER",
                                  left=clamp_label(x - tw / 2, tw, width),
                                  top=round(min(max(y - value_size - 11, 1), height - value_size - 8), 2),
                                  width=tw, height=value_size + 6))

    for i, lb in enumerate(labels):
        cx = plot_left + step * i
        # 标签框宽度取「槽位宽」与「实际字宽」的较小值，避免相邻标签互相压盖
        tw = min(max(48, step + 14), len(str(lb)) * 9.4 + 12)
        inner.append(text(lb, size=label_size, color=C.SLATE, family=F_NUM, align="CENTER",
                          left=clamp_label(cx - tw / 2, tw, width),
                          top=round(pbot + 9, 2), width=tw, height=label_size + 6))

    if unit_note:
        inner.append(text(unit_note, size=14, color=C.FAINT, family=F_BODY, align="RIGHT",
                          left=width - plot_right - 210, top=1, width=210, height=18))

    return f'<Container width="{width}" height="{height}"><Stack fit="EXPAND">{"".join(inner)}</Stack></Container>'

def rot_matrix(deg: float) -> str:
    """2D 旋转矩阵（列主序 4x4）。配合 Transform 的 alignment="CENTER" 绕子节点中心旋转。

    矩阵为 [[c,-s],[s,c]]：把 (1,0) 映到 (cosθ, sinθ)。屏幕坐标 y 向下，
    因此 θ = +degrees(atan2(dy, dx)) 即可让线段正确指向下一点。
    """
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"


def est_lines(text_value: str, width_px: float, font_size: float) -> int:
    """估算换行后的行数：CJK/全角按 1.0em，其余按 0.56em。

    用于在生成 DSL 时按真实文本量预留高度，避免「按固定行数排版」导致区块互相重叠。
    仅为布局估算，最终以实际渲染后的看图结果为准。
    """
    em = 0.0
    for ch in str(text_value):
        o = ord(ch)
        if o > 0x2E80 or ch in "，。、；：？！（）【】—…":
            em += 1.0
        else:
            em += 0.56
    per_line = max(1.0, width_px / max(1.0, font_size))
    return max(1, int(math.ceil(em / per_line - 1e-9)))


def est_block_height(text_value: str, width_px: float, font_size: float,
                     line_height: float = 1.45, head_size: float | None = None,
                     pad: float = 12.0) -> float:
    """带小标题的文本块所需高度（用于自上而下顺排，避免重叠）。"""
    n = est_lines(text_value, width_px, font_size)
    head = (head_size + 8) if head_size else 0.0
    return head + pad + n * font_size * line_height


def clamp_label(left: float, tw: float, total_w: float, pad: float = 1.0) -> float:
    """把标签框夹在画布内，避免首/末标签被裁切。"""
    lo = pad
    hi = total_w - tw - pad
    if hi < lo:
        return max(0.0, (total_w - tw) / 2.0)
    return min(max(left, lo), hi)


def hlegend(items: Sequence[tuple], *, left=0, top=0, size=17, gap=28,
            color=C.SLATE, swatch=13, shape="rect", total_w=None) -> str:
    """横向图例：items = [(颜色, 文字[, 形状])]。"""
    parts = []
    for k, it in enumerate(items):
        col, label = it[0], it[1]
        sh = it[2] if len(it) > 2 else shape
        if sh == "line":
            mark = box(swatch + 12, 4, color=col, radius=2)
        elif sh == "dot":
            mark = dot(swatch, color=col)
        else:
            mark = f'<Container width="{swatch}" height="{swatch}" color="{col}" borderRadius="3"/>'
        if k:
            parts.append(f'<SizedBox width="{gap}" />')
        parts.append(
            f'<Row crossAxisAlignment="CENTER">{mark}'
            f'<SizedBox width="7" />{text(label, size=size, color=color, family=F_BODY)}</Row>'
        )
    row = f'<Row crossAxisAlignment="CENTER">{"".join(parts)}</Row>'
    if total_w:
        # 在 total_w 宽度内右对齐（注意返回的是 Row，可安全嵌进 Positioned/Row）
        return (f'<Row mainAxisAlignment="END" crossAxisAlignment="CENTER">{row}</Row>')
    return f"<Positioned{attrs(left=left, top=top)}>{row}</Positioned>"


# ---------------------------------------------------------------- 图表：横向条

def hbar_chart(labels: Sequence[str], values: Sequence[float], *,
               width=520, height=260, color=C.BLUE, label_w=118,
               plot_left=None, plot_right=78, row_gap=13, value_fmt=lambda v: fmt_int(v),
               bar_h=22, axis_max=None, highlight=None, hl_color=None,
               track="#E2E8F0", axis_note=None) -> str:
    """横向条形图（含轨道底色与行标签）。"""
    pl = plot_left if plot_left is not None else label_w
    pw = width - pl - plot_right
    vmax = axis_max if axis_max is not None else max(values) if values else 1
    vmax = vmax or 1
    n = len(values)
    row_h = bar_h
    total_h = n * row_h + (n - 1) * row_gap
    y0 = max(6, (height - total_h) / 2)
    inner = []
    for i, (lb, v) in enumerate(zip(labels, values)):
        y = y0 + i * (row_h + row_gap)
        bw = max(2.0, pw * (v / vmax))
        col = (hl_color or C.AMBER_B) if (highlight is not None and i == highlight) else color
        inner.append(box(pw, row_h, color=track, radius=5, left=pl, top=round(y, 2)))
        inner.append(box(round(bw, 2), row_h, color=col, radius=5, left=pl, top=round(y, 2)))
        inner.append(text(lb, size=16, color=C.SLATE, family=F_BODY, align="RIGHT",
                          left=0, top=round(y + (row_h - 20) / 2, 2), width=pl - 12, height=22))
        lbl = value_fmt(v)
        tw = plot_right - 10
        inner.append(text(lbl, size=16, color=C.INK2, family=F_NUM, align="LEFT",
                          left=pl + pw + 8, top=round(y + (row_h - 20) / 2, 2), width=tw, height=22))
    if axis_note:
        inner.append(text(axis_note, size=14, color=C.FAINT, family=F_BODY,
                          align="RIGHT", left=0, top=height - 18, width=width, height=18))
    return f'<Container width="{width}" height="{height}"><Stack fit="EXPAND">{"".join(inner)}</Stack></Container>'


# ---------------------------------------------------------------- 表格

@dataclass
class Col:
    key: str
    title: str
    width: float
    align: str = "RIGHT"
    color: str | None = None
    family: str | None = None


def table(columns: Sequence[Col], rows: Sequence[dict], *,
          x=0, y=0, row_h=38, head_h=42, size=19, head_size=18,
          zebra=True, zebra_color="#F8FAFC", head_bg="#EFF6FF",
          head_color="#1E3A8A", grid=True, grid_color="#E2E8F0",
          pad=12, cell_color=None, emphasis=None,
          emphasis_color="#FFFFFF", emphasis_bg=None,
          first_col_align="LEFT") -> str:
    """表格：固定列宽 + 单元格 textAlign 对齐，保证数字列严格右对齐。"""
    total_w = sum(c.width for c in columns) + pad * 2
    total_h = head_h + row_h * len(rows)
    parts = []
    parts.append(box(total_w, total_h, color=C.PAPER, radius=10, left=x, top=y))
    parts.append(box(total_w, head_h, color=head_bg, radius=10, left=x, top=y))
    # 头部下边框
    parts.append(box(total_w, 1.4, color="#BFDBFE", left=x, top=round(y + head_h, 2)))

    cx = x + pad
    for c in columns:
        al = first_col_align if c is columns[0] else c.align
        parts.append(text(c.title, size=head_size, color=head_color,
                          family=F_HEAD if al == "LEFT" else (F_NUM),
                          align=al, left=round(cx, 2), top=round(y + (head_h - head_size - 6) / 2, 2),
                          width=round(c.width, 2), height=head_size + 10))
        cx += c.width

    for r, row in enumerate(rows):
        ry = y + head_h + r * row_h
        if zebra and r % 2 == 1:
            parts.append(box(total_w, row_h, color=zebra_color, left=x, top=round(ry, 2)))
        if grid and r > 0:
            parts.append(box(total_w, 1, color=grid_color, left=x, top=round(ry, 2)))
        if emphasis is not None and r in (emphasis if isinstance(emphasis, (list, tuple, set)) else {emphasis}):
            parts.append(box(total_w, row_h, color=emphasis_bg or "#DBEAFE",
                             left=x, top=round(ry, 2)))
        cx = x + pad
        for c in columns:
            val = row.get(c.key, "")
            al = first_col_align if c is columns[0] else c.align
            fam = c.family or (F_HEAD if al == "LEFT" else F_NUM)
            col = (emphasis_color if (emphasis is not None and r in (emphasis if isinstance(emphasis, (list, tuple, set)) else {emphasis})) else None) \
                or c.color or (cell_color or C.INK2)
            if c is columns[0] and emphasis is not None and r in (emphasis if isinstance(emphasis, (list, tuple, set)) else {emphasis}):
                fam = F_HEAD
            parts.append(text(val, size=size, color=col, family=fam, align=al,
                              left=round(cx, 2), top=round(ry + (row_h - size - 6) / 2, 2),
                              width=round(c.width, 2), height=size + 10))
            cx += c.width
    return (f'<Container width="{total_w}" height="{total_h}">'
            f'<Stack fit="EXPAND">{"".join(parts)}</Stack></Container>')


# ---------------------------------------------------------------- KPI 卡片

def kpi_card(label, value, *, unit=None, sub=None, accent=C.BLUE,
             w=330, h=148, x=None, y=None, value_size=42, label_size=17,
             sub_size=16, bg=C.PAPER, value_color=C.INK, icon=None,
             value_family=F_HEAD, label_color=C.MUTED, border=True) -> str:
    """KPI 卡片：左侧强调条 + 标签 / 大数字 / 说明（自上而下排布，互不重叠）。"""
    inner = []
    inner.append(box(6, h - 28, color=accent, radius=3, left=0, top=14))
    inner.append(f'<Positioned left="26" top="16" width="{w - 40}" height="{label_size + 10}">'
                 f'{text(label, size=label_size, color=label_color, family=F_BODY)}</Positioned>')
    value_top = 16 + label_size + 10
    unit_node = ""
    if unit:
        # Text 子文本会被 trim，不能用前导空格制造间距，改用 SizedBox
        unit_node = '<SizedBox width="8" />' + text(unit, size=19, color=C.MUTED, family=F_BODY)
    inner.append(f'<Positioned left="26" top="{value_top}" width="{w - 40}" height="{value_size + 12}">'
                 f'<Row crossAxisAlignment="END">'
                 f'{text(value, size=value_size, color=value_color, family=value_family)}'
                 f'{unit_node}'
                 f"</Row></Positioned>")
    if sub:
        sub_top = value_top + value_size + 12
        inner.append(f'<Positioned left="26" top="{sub_top}" width="{w - 40}" height="{sub_size + 8}">'
                     f'{text(sub, size=sub_size, color=C.FAINT, family=F_BODY)}</Positioned>')
    if icon:
        inner.append(f'<Positioned right="16" top="16" width="34" height="34">{icon}</Positioned>')
    body = "".join(inner)
    container = f'<Container width="{w}" height="{h}" color="{bg}" borderRadius="12"' \
               + (' border="1 SOLID #E2E8F0"' if border else "") \
               + f'><Stack fit="EXPAND">{body}</Stack></Container>'
    if x is not None or y is not None:
        return f"<Positioned{attrs(left=x, top=y)}>{container}</Positioned>"
    return container


# ---------------------------------------------------------------- 版式工具

def card(w, h, *, x=None, y=None, bg=C.PAPER, radius=14, border="1 SOLID #E2E8F0",
         padding=None, shadow=None) -> str:
    kw = {"width": w, "height": h, "color": bg, "borderRadius": radius, "border": border, "boxShadow": shadow}
    node = f"<Container{attrs(**kw)}/>"
    if x is not None or y is not None:
        return f"<Positioned{attrs(left=x, top=y)}>{node}</Positioned>"
    return node


def header(w, title, subtitle=None, *, h=76, bg=C.PAPER, accent=C.BLUE,
           title_size=27, sub_size=16, y=None) -> str:
    inner = [
        box(6, h - 30, color=accent, radius=3, left=26, top=15),
        f'<Positioned left="48" top="{18 if not subtitle else 14}" width="{w - 260}" height="34">'
        f'{text(title, size=title_size, color=C.INK, family=F_HEAD)}</Positioned>',
    ]
    if subtitle:
        inner.append(
            f'<Positioned left="48" top="{18 + title_size + 6}" width="{w - 260}" height="24">'
            f'{text(subtitle, size=sub_size, color=C.MUTED, family=F_BODY)}</Positioned>')
    stamp = f'<Positioned right="26" top="{h / 2 - 17}" width="220" height="34">' \
            f'<Container width="220" height="34" color="#F1F5F9" borderRadius="17" alignment="CENTER">' \
            f'{text("Northstar · 内部经营口径", size=15, color=C.MUTED, family=F_BODY)}</Container></Positioned>'
    inner.append(stamp)
    return f'<Container width="{w}" height="{h}" color="{bg}"><Stack fit="EXPAND">{"".join(inner)}</Stack></Container>'


def caption(w, txt, *, y=0, size=16, color=C.FAINT, align="LEFT", x=0) -> str:
    return text(txt, size=size, color=color, family=F_BODY, align=align,
                left=x, top=y, width=w, height=size + 8)


def wrapped(w, txt, *, size=19, color=C.INK2, family=F_BODY, line_height=1.55,
            x=None, y=None, align="LEFT", max_lines=None) -> str:
    kw = {"fontSize": size, "color": color, "fontFamily": family,
          "height": line_height, "textAlign": align, "softWrap": "true"}
    if max_lines is not None:
        kw["maxLines"] = max_lines
        kw["overflow"] = "CLIP"
    node = f"<Text{attrs(**kw)}>{esc(txt)}</Text>"
    if x is not None or y is not None:
        return f"<Positioned{attrs(left=x, top=y, width=w)}>{node}</Positioned>"
    return node


def bullet(x, y, w, idx, txt, *, size=18, color=C.INK2, badge=C.BLUE_L, badge_color=C.BLUE,
           badge_size=26, line_height=1.5) -> str:
    return (
        f'<Positioned left="{x}" top="{y}" width="{badge_size}" height="{badge_size}">'
        f'<Container width="{badge_size}" height="{badge_size}" color="{badge}" borderRadius="{badge_size / 2}" alignment="CENTER">'
        f'<Text fontSize="{int(size * 0.82)}" color="{badge_color}" fontFamily="{F_HEAD}" fontStyle="BOLD">{idx}</Text>'
        f"</Container></Positioned>"
        f'<Positioned left="{x + badge_size + 10}" top="{y + 1}" width="{w - badge_size - 10}" height="90">'
        f'{wrapped(w - badge_size - 10, txt, size=size, color=color, line_height=line_height)}</Positioned>'
    )


def note_strip(w, h, txt, *, bg="#EFF6FF", color="#1E3A8A", accent=C.BLUE,
               size=19, family=F_BODY, x=None, y=None, lines=1,
               line_height=1.5) -> str:
    """说明条：左侧强调竖条 + 正文（默认顶部对齐，按行数预留高度，避免末行被裁）。

    行高估算：每行约 size * line_height 像素；调用方应传 h >= 20 + lines*size*line_height。
    """
    parts = [
        f'<Positioned left="0" top="0" width="6" height="{h}"><Container width="6" height="{h}" color="{accent}" borderRadius="3"/></Positioned>',
        f'<Positioned left="22" top="10" width="{w - 40}" height="{h - 18}">'
        f"{wrapped(w - 40, txt, size=size, color=color, family=family, line_height=line_height)}</Positioned>",
    ]
    node = f'<Container width="{w}" height="{h}" color="{bg}" borderRadius="10"><Stack fit="EXPAND">{"".join(parts)}</Stack></Container>'
    if x is not None or y is not None:
        return f"<Positioned{attrs(left=x, top=y)}>{node}</Positioned>"
    return node


def divider(w, *, y=0, x=0, color=C.LINE, thickness=1) -> str:
    return box(w, thickness, color=color, left=x, top=y)


def tag(label, *, bg=C.BLUE_L, color=C.BLUE, size=15, pad=10, h=24) -> str:
    return f'<Container width="{len(label) * (size * 0.92) + pad * 2}" height="{h}" color="{bg}" borderRadius="{h / 2}" alignment="CENTER">' \
           f'<Text fontSize="{size}" color="{color}" fontFamily="{F_BODY}">{esc(label)}</Text></Container>'