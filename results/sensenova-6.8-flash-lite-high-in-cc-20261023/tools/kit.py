"""跨题复用的视觉系统：调色板、字体栈、面板/KPI/图表/表格组件。

颜色依据 dataviz 方法学与其已验证的默认调色板
（scripts/validate_palette.py 六项检查全过，见 tmp/_suite/docs/palette-validation.txt）：
  - 分类色按固定顺序取用，绝不循环；
  - 单一数轴：金额与百分比必须分图，不共用混淆数轴；
  - 顺序色一色由浅到深；发散色蓝↔红 + 中性灰中点；
  - 状态色专供 good/warning/serious/critical，且不单独承载含义；
  - 文字用文字色，不用系列色；网格/轴线退到最弱。
静态 PNG 无悬停层，故对 <=4 个系列改用直接标注 + 图例双重编码。
"""

from __future__ import annotations

import math
import re

from dsl import (ALIGNMENTS, box, canvas, clip_path, el, layer, mix, opacity,
                 rounded_rect, rgba, text, text_width, at)  # noqa: F401

# --- 字体栈（/fonts 实际返回值，不臆造）-----------------------------------
FONT_SANS = "Inter,Noto Sans CJK SC"
FONT_SERIF = "Noto Serif CJK SC,Inter"
FONT_MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"
FAMILY = FONT_SANS

# --- 画布与留白 ------------------------------------------------------------
PAGE_W, PAGE_H = 1600, 1000
MARGIN = 40

# --- 调色板（浅色平面，全套统一）-----------------------------------------
INK = "#0B0B0B"
INK2 = "#52514E"
MUTED = "#898781"
SURFACE = "#FCFCFB"
PLANE = "#F9F9F7"
PANEL = "#FFFFFF"
GRID = "#E1E0D9"
AXIS = "#C3C2B7"
RING = "#0000001A"

SERIES = ["#2A78D6", "#EB6834", "#1BAF7A", "#EDA100", "#E87BA4", "#008300", "#6250D6", "#E34948"]
SEQ_BLUE = ["#CDE2FB", "#B7D3F6", "#9EC5F4", "#86B6EF", "#6DA7EC", "#5598E7",
            "#3987E5", "#2A78D6", "#256ABF", "#1C5CAB", "#184F95", "#104281", "#0D366B"]
DIVERGE = ("#2A78D6", "#F0EFEF", "#E34948")
GOOD, WARNING, SERIOUS, CRITICAL = "#0CA30C", "#FAB219", "#EC835A", "#D03B3B"
DELTA_UP, DELTA_DOWN = "#006300", "#D03B3B"

# 深色平面（海报/暗底作品用）
D_INK, D_INK2, D_MUTED = "#F0EFEC", "#C3C2B7", "#898781"
D_SURFACE, D_PLANE, D_PANEL = "#1A1A19", "#0D0D0D", "#232321"
D_GRID, D_AXIS = "#2C2C2A", "#383835"
D_SERIES = ["#3987E5", "#D95926", "#199E70", "#C98500", "#D55181", "#008300", "#9085E9", "#E66767"]

# --- 字号（题面要求正文≥20、脚注≥16，故所有字号不低于 16）----------------
FS_DISPLAY = 42
FS_H1 = 30
FS_H2 = 22
FS_LABEL = 18
FS_BODY = 20
FS_CAP = 16
FS_TICK = 16
FS_MIN = 16  # 全套下限：任何可见文字不小于 16px


def fmt_int(v) -> str:
    return f"{v:,.0f}"


def fmt_wan(v, dec=1) -> str:
    """元 -> 万元"""
    return f"{v / 10000:,.{dec}f}"


def fmt_pct(v, dec=2) -> str:
    """v 为小数比例（0.1234 -> 12.34%）"""
    return f"{v * 100:,.{dec}f}%"


def fmt_money(v) -> str:
    return f"¥{v:,.0f}"


# --- 基础文本盒 -----------------------------------------------------------
def txt(x, y, s, *, size=FS_BODY, color=INK, align=None, w=None, h=None,
        bold=False, family=FAMILY, wrap=None, max_lines=None, shadow=None,
        letter=None, valign=None, radius=None, bg=None, padding=None,
        overflow=None, direction="LTR", height_ratio=None, valign_box=False,
        decoration=None, dec_color=None, align_text=None) -> str:
    """绝对定位文本。w/h 给定则建定位盒；valign_box 时用容器对齐做垂直居中。"""
    t = text(s, size=size, color=color, family=family, bold=bold,
             soft_wrap=wrap if wrap is not None else (True if (w and "\n" in s) else False),
             max_lines=max_lines, shadow=shadow, letterSpacing=letter,
             overflow=overflow, textDirection=direction, height=height_ratio,
             decoration=decoration, decorationColor=dec_color, backgroundColor=bg,
             textAlign=align_text or align)
    if w is None and h is None:
        return at(x, y, t)
    # 左对齐单行文本：text_width 是估算，Positioned 的宽度是紧约束，估算偏小会把文本
    # 尾部裁掉。故左对齐单行文本给盒宽留 12% 余量（文本仍从盒左端起画，位置不变）；
    # 居中/右对齐与折行文本保持精确盒宽，居中算法与换行预算才成立。
    if (w is not None and "\n" not in s and align_text in (None, "LEFT")
            and wrap in (None, False)):
        w = w * 1.12
    if valign_box and valign:
        inner = box(t, alignment=valign)
        return at(x, y, inner, width=w, height=h)
    return at(x, y, t, width=w, height=h)


# 中文行首禁则（硬规则）：这些标点不能出现在行首。
_NO_LINE_START = set("，。、；：？！」』】〕〉〃…·%‰）")
# 中文行末禁则（硬规则）：这些字符不能留在行末。
_NO_LINE_END = set("（「『【〔〈〝({")
# 行首"不理想"：禁则标点之外再加闭括号/后引号。这类情况不是硬禁则，所以处理方式是
# "改到上一行的空格处断"，而不是强扭断点。
_LINE_START_BAD = _NO_LINE_START | set("）》」』】〕〉〃)")
# 拉丁/数字连体：整块不可断，避免把 "pp" 拆成 "p" / "p"。
_LATIN_RUN = re.compile(r"[A-Za-z0-9%.,+−\-]+")


def _atoms(s: str) -> list[str]:
    """切分成不可再断的原子：拉丁/数字连体整块，其余（CJK、全角标点）单字一块。"""
    out, i = [], 0
    while i < len(s):
        m = _LATIN_RUN.match(s, i)
        if m:
            out.append(m.group())
            i = m.end()
        else:
            out.append(s[i])
            i += 1
    return out


def wrap_text(s: str, size: float, max_w: float, bold: bool = False,
              line_height: float = 1.5, safety: float = 0.94) -> list[str]:
    """按像素宽度折行（原子为单位），用于精确预算垂直空间（每行 line_height em）。

    safety：text_width 对拉丁/数字/标点系统性偏小约 3-6%（实测校准），故按
    max_w*safety 做预算。否则我算出 1 行、渲染器按真实字宽折成 2 行，而外层盒高
    只留了 1 行，末行就被裁掉（A01 结论第 2 条尾部 "长靠流量，不靠效率。" 即如此）。

    断行优先级——每条都保证产出行仍 ≤ max_w*safety，行数预算不会被排版规则打破：
    1. 下一块放不下、且新行行首会是禁则标点或闭括号 → 改在 cur 最后一个空格处断
       （既不拆散 "pp"，也不让新行以 "）：" 开头）。
    2. 新行行首是硬禁则标点 → 断点前移，把 cur 末尾的原子与它同行。
    3. cur 末尾是开括号/前引号 → 行末禁则，随下一行下移。
    4. 否则正常断行；单个原子比整行还宽时才退回逐字符断。
    """
    max_w = max_w * safety
    lines, cur = [], ""
    for tok in re.split(r"(\s+)", s):
        if tok == "":
            continue
        if tok.isspace():
            if cur and text_width(cur + tok, size, bold) <= max_w:
                cur += tok
            else:
                lines.append(cur)
                cur = ""
            continue
        for atom in _atoms(tok):
            if not cur or text_width(cur + atom, size, bold) <= max_w:
                cur += atom
                continue
            # 4) 原子本身比整行还宽 → 逐字符拆
            if text_width(atom, size, bold) > max_w:
                for ch in atom:
                    if cur and text_width(cur + ch, size, bold) > max_w:
                        lines.append(cur)
                        cur = ch
                    else:
                        cur += ch
                continue
            # 1) 行首不理想 → 在 cur 的最后一个空格处断（空格不算入行内，避免尾随空白）
            if atom[0] in _LINE_START_BAD:
                sp = cur.rfind(" ")
                if sp >= len(cur) * 0.45 and \
                        text_width(cur[sp + 1:] + atom, size, bold) <= max_w:
                    lines.append(cur[:sp])
                    cur = cur[sp + 1:] + atom
                    continue
            # 2) 硬禁则 → 前移断点，挪走 cur 末尾的原子（整块，不拆拉丁词）
            if atom[0] in _NO_LINE_START:
                a2 = _atoms(cur)
                k = 0
                while k < len(a2) and a2[-1 - k] in _NO_LINE_START:
                    k += 1
                if k < len(a2):
                    tail = "".join(a2[-(k + 1):])
                    if text_width(tail + atom, size, bold) <= max_w:
                        lines.append(cur[:len(cur) - len(tail)])
                        cur = tail + atom
                        continue
            # 3) 行末禁则 → 开括号/前引号随下一行下移
            if cur[-1] in _NO_LINE_END:
                lines.append(cur[:-1])
                cur = cur[-1] + atom
                continue
            lines.append(cur)
            cur = atom
    if cur:
        lines.append(cur)
    return lines or [""]


def text_block(x, y, s, *, size=FS_CAP, color=INK2, max_w=None, bold=False,
               line_height=1.5, family=FAMILY, max_lines=None) -> str:
    """多行文本块：返回折行后的文本片段，调用方可用行数 × size × line_height 预算高度。"""
    if max_w:
        lines = wrap_text(s, size, max_w, bold)
    else:
        lines = [s]
    if max_lines:
        lines = lines[:max_lines]
    return txt(x, y, "\n".join(lines), size=size, color=color, bold=bold, family=family,
               w=max_w, height_ratio=line_height, max_lines=len(lines))


def text_block_height(s, size, max_w, bold=False, line_height=1.5) -> float:
    return len(wrap_text(s, size, max_w, bold)) * size * line_height


def vcenter(x, y, w, h, *children, align="CENTER") -> str:
    return at(x, y, box(*children, alignment=align), width=w, height=h)


# --- 卡片 / 面板 ----------------------------------------------------------
def card(x, y, w, h, *, radius=14, fill=PANEL, ring=RING, shadow=None,
         border=None, children=()) -> str:
    """卡片外壳。

    Container 最多一个子节点，且 Positioned 的父节点必须是 Stack：
    只要有 Positioned 子节点（或子节点多于一个）就套一层绝对定位 Stack。
    否则渲染报 RENDER_ERROR "renderBox.parentData must be StackParentData"。
    """
    if children and (len(children) > 1 or
                     any(isinstance(c, str) and c.startswith("<Positioned") for c in children)):
        children = (layer(w, h, *children),)
    return at(x, y, box(*children, width=w, height=h, color=fill, radius=radius,
                        border=border or f"1 SOLID {RING}", shadow=shadow), width=w, height=h)


def panel(x, y, w, h, *, title=None, subtitle=None, unit=None, accent=None,
          children=(), pad=20, title_size=FS_H2, body=INK, sub=INK2,
          body_pad=None) -> str:
    """标准图表面板：标题行（标题 + 右侧单位）+ 可选副标题 + 内容层。"""
    inner_w = w - 2 * pad
    kids = []
    ty = pad
    if title:
        th = title_size * 1.45
        # 标题/单位是单行左对齐文本，不能给紧约束宽度：text_width 是估算，
        # Positioned 的宽度是紧约束，估算偏小就会把末位字符裁掉。改由 Text 自定宽，
        # 标题与单位是否撞车在构建期用断言卡住（而不是渲染出看不见的截断）。
        uw = text_width(unit, FS_CAP) if unit else 0
        assert text_width(title, title_size, True) + uw + 16 <= inner_w, (title, unit, inner_w)
        row_kids = [at(0, 0, txt(0, 0, title, size=title_size, color=body, bold=True),
                       height=th)]
        if unit:
            row_kids.append(at(inner_w - uw, 3,
                               txt(0, 0, unit, size=FS_CAP, color=MUTED),
                               height=FS_CAP * 1.5))
        kids.append(at(pad, ty, layer(inner_w, th, *row_kids), width=inner_w, height=th))
        ty += th
        if subtitle:
            kids.append(at(pad, ty,
                           txt(0, 0, subtitle, size=FS_CAP, color=sub, w=inner_w, wrap=True),
                           width=inner_w, height=FS_CAP * 1.5))
            ty += FS_CAP * 1.5 + 2
        ty += 10
    else:
        ty += 4
    bp = body_pad if body_pad is not None else 0
    kids.append(at(pad + bp, ty, layer(inner_w - 2 * bp, h - ty - pad, *children),
                   width=inner_w - 2 * bp, height=h - ty - pad))
    return card(x, y, w, h, children=kids)


def kpi(x, y, w, h, *, label, value, unit=None, note=None, delta=None,
        delta_good=True, accent=None, radius=14, fill=PANEL, big=FS_DISPLAY,
        sub=None) -> str:
    """KPI 卡：标签 / 主数值 / 单位 / 环比 / 备注。

    强调条（x 14-18）与内容层（x 26 起，宽 w-44）分居卡片两侧，互不压字：条若与
    文本同起点（都从内容层 x=0 开始），¥ 与 ▲ 的首字符会被 4px 条压住。条落在
    radius 圆弧之外（圆弧只覆盖 x<14），不会溢到圆角之外。
    """
    accent = accent or SERIES[0]
    cw = w - 44
    kids = []
    # 标签/主数值/环比都是单行左对齐文本，不给紧约束宽度：Positioned 的宽度对 Text
    # 是紧约束，text_width 估算偏小 3% 就把末位字符裁掉一半（A01 的 "¥918,624" 丢失
    # 末位 "4"、"11.15%" 丢失 "%" 即因此）。让 Text 自定宽，行高仍按预算占位。
    ty = 18
    kids.append(at(0, ty, txt(0, 0, label, size=FS_LABEL, color=INK2), height=FS_LABEL * 1.4))
    ty += FS_LABEL * 1.55
    kids.append(at(0, ty, txt(0, 0, value, size=big, color=INK, bold=True, letter=0.0),
                   height=big * 1.25))
    if unit:
        # 主数值估算加 4% 余量再放单位，避免估算偏小造成单位与数值贴字。
        ux = text_width(value, big, True) * 1.04 + 8
        assert ux + text_width(unit, FS_LABEL) <= cw, (value, unit, w)
        kids.append(at(ux, ty + big * 0.62, txt(0, 0, unit, size=FS_LABEL, color=INK2),
                       height=FS_LABEL * 1.3))
    ty += big * 1.25 + 8
    if delta is not None:
        dc = DELTA_UP if delta_good else DELTA_DOWN
        arrow = "▲" if delta_good else "▼"
        d = f"{arrow} {delta}"
        kids.append(at(0, ty, txt(0, 0, d, size=FS_CAP, color=dc, bold=True),
                       height=FS_CAP * 1.4))
        ty += FS_CAP * 1.5
    if note:
        # 备注按卡宽折行；卡高 150 只容得下 1 行（18+27.9+50.5+8+24+24=152.4>150），
        # 超行在构建期暴露，而不是渲染出看不见的截断或越出卡片。
        _nl = len(wrap_text(note, FS_CAP, cw))
        assert _nl <= 1, (note, w, _nl)
        kids.append(at(0, ty, txt(0, 0, note, size=FS_CAP, color=MUTED,
                                  w=cw, wrap=True),
                        width=cw, height=FS_CAP * 1.5 + 2))
    return card(x, y, w, h, radius=radius, fill=fill, children=[
        at(14, 0, box(width=4, height=h, color=accent), width=4, height=h),
        at(26, 0, layer(cw, h, *kids), width=cw, height=h),
    ])


# --- 坐标轴系统 -----------------------------------------------------------
def axis_frame(x, y, w, h, *, y_lo, y_hi, y_ticks, x_labels, y_fmt=None,
               x_tick_w=None, grid=True, axis_color=AXIS, grid_color=GRID,
               tick_color=MUTED, tick_size=FS_TICK, y_pad_left=0, zero_line=True,
               x_size=None, x_align="CENTER", y_suffix=None, x_gap=None) -> str:
    """绘制网格、y 轴刻度、x 轴标签与基线。返回 DSL 片段列表。"""
    out = []
    y_fmt = y_fmt or (lambda v: f"{v:g}")
    inner_h = h
    def Y(v):
        return y + inner_h - (v - y_lo) / (y_hi - y_lo) * inner_h
    for t in y_ticks:
        yy = Y(t)
        if t != y_lo:
            out.append(at(x, yy, box(width=w, height=1, color=grid_color), width=w, height=1)
                       if grid else "")
        lbl = y_fmt(t)
        lw = text_width(lbl, tick_size)
        out.append(at(x - y_pad_left - lw - 8, yy - tick_size * 0.62,
                      txt(0, 0, lbl, size=tick_size, color=tick_color, align="RIGHT",
                          align_text="RIGHT", w=lw), width=lw, height=tick_size * 1.3))
    # 基线（零线）
    if y_lo <= 0 <= y_hi:
        zy = Y(0)
        out.append(at(x, zy, box(width=w, height=2, color=axis_color), width=w, height=2))
    else:
        out.append(at(x, y + inner_h - 1, box(width=w, height=2, color=axis_color),
                      width=w, height=2))
    n = len(x_labels)
    for i, lb in enumerate(x_labels):
        cx = x + (i + 0.5) / n * w
        tw = text_width(lb, x_size or tick_size)
        bw = tw * 1.2
        out.append(at(cx - bw / 2, y + inner_h + 10,
                      txt(0, 0, lb, size=x_size or tick_size, color=tick_color,
                          align_text="CENTER", w=bw), width=bw,
                      height=(x_size or tick_size) * 1.3))
    if y_suffix:
        out.append(at(x - y_pad_left, y - FS_LABEL * 1.6,
                      txt(0, 0, y_suffix, size=FS_CAP, color=tick_color),
                      width=text_width(y_suffix, FS_CAP), height=FS_CAP * 1.4))
    return [k for k in out if k]


def Y_MAP(y, h, y_lo, y_hi):
    return lambda v: y + h - (v - y_lo) / (y_hi - y_lo) * h


# --- 柱状图（共享零起点与比例）--------------------------------------------
def grouped_bars(x, y, w, h, *, series, x_labels, colors=None, y_lo=0, y_hi=None,
                 y_ticks=None, y_fmt=None, bar_w=None, group_gap=10, bar_gap=3,
                 direct_labels=True, label_size=None, label_offset=6,
                 round_top=4, radius_bottom=0, grid=True, value_fmt=None,
                 tick_size=FS_TICK, y_suffix=None, zero_line=True) -> str:
    """分组柱图。series=[(name, [v...]), ...]；柱底锚定零线，共享比例与零起点。"""
    allv = [v for _, vs in series for v in vs]
    if y_hi is None:
        top = max(allv)
        y_hi = nice_up(top * 1.12)
    if y_lo is None:
        y_lo = min(0, min(allv))
    if y_ticks is None:
        y_ticks = _ticks(y_lo, y_hi)
    y_map = Y_MAP(y, h, y_lo, y_hi)
    kids = axis_frame(x, y, w, h, y_lo=y_lo, y_hi=y_hi, y_ticks=y_ticks,
                      x_labels=x_labels, y_fmt=y_fmt, y_pad_left=0, grid=grid,
                      y_suffix=y_suffix, zero_line=zero_line, tick_size=tick_size)
    n_grp = len(x_labels)
    n_s = len(series)
    colors = colors or [SERIES[i] for i in range(n_s)]
    slot = w / n_grp
    inner = slot - group_gap
    bw = bar_w or min(inner / n_s - bar_gap, 46)
    total = bw * n_s + bar_gap * (n_s - 1)
    for gi in range(n_grp):
        gx = x + gi * slot + (slot - total) / 2
        for si, (name, vs) in enumerate(series):
            v = vs[gi]
            cx0 = gx + si * (bw + bar_gap)
            y0 = y_map(max(0, v) if v > 0 else 0)
            yz = y_map(0)
            top = y_map(v) if v > 0 else y_map(0)
            if v >= 0:
                hgt = max(2, yz - top)
                path = rounded_rect(cx0, top, bw, hgt, round_top) if hgt > round_top else \
                    rounded_rect(cx0, top, bw, hgt, min(2, hgt / 2))
                kids.append(at(cx0, top, clip_path(path, box(width=bw, height=hgt,
                                                              color=colors[si]),
                                                  viewBox=f"0 0 {bw:.2f} {hgt:.2f}",
                                                  fit="FILL"), width=bw, height=hgt))
            else:
                hgt = max(2, top - yz)
                path = rounded_rect(cx0, yz, bw, hgt, round_top)
                kids.append(at(cx0, yz, clip_path(path, box(width=bw, height=hgt,
                                                              color=colors[si]),
                                                  viewBox=f"0 0 {bw:.2f} {hgt:.2f}",
                                                  fit="FILL"), width=bw, height=hgt))
            if direct_labels and label_size:
                ls = label_size
                fmt = value_fmt or (lambda v: f"{v:,.0f}")
                lb = fmt(v)
                tw = text_width(lb, ls, True)
                bw2 = tw * 1.3
                lx = cx0 + bw / 2 - bw2 / 2
                ly = (top - ls * 1.35 - label_offset) if v >= 0 else (top + label_offset)
                kids.append(at(lx, ly, txt(0, 0, lb, size=ls, color=INK, bold=True,
                                           align_text="CENTER", w=bw2),
                               width=bw2, height=ls * 1.3))
    return layer(w + 160, h + 40, *kids)


def nice_up(v):
    if v <= 0:
        return 1
    mag = 10 ** math.floor(math.log10(v))
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if v <= m * mag:
            return m * mag
    return 10 * mag


def _ticks(lo, hi, count=5):
    if hi == lo:
        hi = lo + 1
    raw = (hi - lo) / count
    mag = 10 ** math.floor(math.log10(raw))
    step = next((m * mag for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10) if raw <= m * mag),
                10 * mag)
    out, v = [], math.floor(lo / step) * step
    while v <= hi + step * 1e-6:
        out.append(round(v, 10))
        v += step
    return out


# --- 图例 -----------------------------------------------------------------
def legend(x, y, items, *, size=FS_CAP, swatch=12, gap=22, color=MUTED,
           label_color=INK2, h=None) -> str:
    """items=[(label, color)]；返回绝对定位片段，总宽附在返回前。"""
    kids = []
    cx = 0.0
    for lb, c in items:
        tw = text_width(lb, size)
        kids.append(at(cx, 0, box(width=swatch, height=swatch, color=c, radius=3),
                       width=swatch, height=swatch))
        kids.append(at(cx + swatch + 7, 1, txt(0, 0, lb, size=size, color=label_color),
                       height=size * 1.35))
        cx += swatch + 7 + tw + gap
    hh = h if h else max(swatch, size * 1.4)
    return at(x, y, layer(cx - gap, hh, *kids), width=cx - gap, height=hh)


def legend_width(items, size=FS_CAP, swatch=12, gap=22) -> float:
    return sum(text_width(lb, size) + swatch + 7 for lb, _ in items) + gap * (len(items) - 1)


# --- 表格 -----------------------------------------------------------------
def table(x, y, *, cols, rows, col_x=None, row_h=38, head_h=40, head_size=FS_LABEL,
          body_size=FS_BODY, zebra=True, zebra_color="#F4F4F2", grid_line=GRID,
          head_bg=None, pad_x=14, accent=None) -> str:
    """cols=[(label, align, width)]; rows=[[cell,...]]（str 或 (str,color,bold)）。"""
    kids = []
    cy = 0
    if head_bg:
        total_w = sum(c[2] for c in cols)
        kids.append(at(0, 0, box(width=total_w, height=head_h, color=head_bg,
                                 radius=(10, 10, 0, 0)), width=total_w, height=head_h))
    for ci, (lb, al, cw) in enumerate(cols):
        tw = text_width(lb, head_size, True)
        bw = tw * 1.12                      # 估算余量：文本盒略宽于估算宽度
        col_l = (col_x[ci] if col_x else sum(c[2] for c in cols[:ci])) + pad_x
        col_r = (col_x[ci + 1] if col_x else sum(c[2] for c in cols[:ci + 1])) - pad_x
        tx = col_r - bw if al == "RIGHT" else (col_l if al == "LEFT" else (col_l + col_r - bw) / 2)
        kids.append(at(tx, cy + (head_h - head_size * 1.35) / 2,
                       txt(0, 0, lb, size=head_size, color=INK, bold=True,
                           align_text=al if al != "CENTER" else "CENTER", w=bw),
                       width=bw, height=head_size * 1.35))
    cy += head_h
    for ri, r in enumerate(rows):
        ry = cy + ri * row_h
        if zebra and ri % 2 == 1:
            kids.append(at(0, ry, box(width=sum(c[2] for c in cols), height=row_h,
                                       color=zebra_color),
                           width=sum(c[2] for c in cols), height=row_h))
        for ci, (lb, al, cw) in enumerate(cols):
            cell = r[ci]
            s, color, bold = (cell if isinstance(cell, tuple) else (str(cell), INK, False))
            s = str(s)
            tw = text_width(s, body_size, bold)
            bw = tw * 1.15
            col_l = (col_x[ci] if col_x else sum(c[2] for c in cols[:ci])) + pad_x
            col_r = (col_x[ci + 1] if col_x else sum(c[2] for c in cols[:ci + 1])) - pad_x
            tx = col_r - bw if al == "RIGHT" else (col_l if al == "LEFT" else (col_l + col_r - bw) / 2)
            kids.append(at(tx, ry + (row_h - body_size * 1.35) / 2,
                           txt(0, 0, s, size=body_size, color=color, bold=bold,
                               align_text=al if al != "CENTER" else "CENTER", w=bw),
                           width=bw, height=body_size * 1.35))
    total_h = head_h + len(rows) * row_h
    if grid_line:
        for ri in range(len(rows) + 1):
            yy = head_h + ri * row_h - (1 if ri == 0 else 0)
            kids.append(at(0, max(0, yy), box(width=sum(c[2] for c in cols), height=1,
                                              color=grid_line),
                           width=sum(c[2] for c in cols), height=1))
    return at(x, y, layer(sum(c[2] for c in cols), total_h, *kids),
              width=sum(c[2] for c in cols), height=total_h)


# --- 面积/折线（ClipPath 等宽填充）----------------------------------------
def polyline(points, thickness=2.5) -> str:
    from dsl import polyline_stroke
    return polyline_stroke(points, thickness)


def dash_h(x0, x1, y, *, dash=9, gap=7, t=1.6, color=AXIS) -> str:
    """水平虚线（ClipPath 多段细条）。用于参考线。"""
    parts = []
    cx = x0
    while cx < x1:
        seg = min(dash, x1 - cx)
        parts.append(f"M{cx:.2f} {y - t/2:.2f} H{cx + seg:.2f} V{y + t/2:.2f} H{cx:.2f} Z")
        cx += seg + gap
    return clip_path(" ".join(parts), box(width=x1, height=t, color=color),
                     viewBox=f"0 0 {x1:.2f} {t:.2f}", fit="FILL")


def line_chart(x, y, w, h, *, series, x_labels, y_lo=0, y_hi=None, y_ticks=None,
               y_fmt=None, grid=True, tick_size=FS_TICK, y_suffix=None,
               marker_r=5, labels_at=None, label_size=None, value_fmt=None,
               x_size=None, ref_lines=None, line_w=2.5) -> str:
    """多序列折线；ClipPath 生成等宽折线 + 标记点。ref_lines=[(value,label)] 画参考线。"""
    from dsl import rounded_rect
    allv = [v for _, vs in series for v in vs]
    if y_hi is None:
        y_hi = nice_up(max(allv) * 1.12)
    if y_lo is None:
        y_lo = min(0, min(allv))
    if y_ticks is None:
        y_ticks = _ticks(y_lo, y_hi)
    y_map = Y_MAP(y, h, y_lo, y_hi)
    kids = axis_frame(x, y, w, h, y_lo=y_lo, y_hi=y_hi, y_ticks=y_ticks,
                      x_labels=x_labels, y_fmt=y_fmt, grid=grid, y_suffix=y_suffix,
                      tick_size=tick_size, x_size=x_size)
    n = len(x_labels)
    colors = [SERIES[i] for i in range(len(series))]
    for val, lbl in (ref_lines or []):
        yy = y_map(val)
        kids.append(at(x, yy - 1, dash_h(0, w, 1, t=1.6, color=MUTED), width=w, height=2))
        lw_ = text_width(lbl, FS_CAP)
        kids.append(at(x + w - lw_ - 4, yy + 6, txt(0, 0, lbl, size=FS_CAP, color=INK2),
                       width=lw_, height=FS_CAP * 1.35))
    for si, (name, vs) in enumerate(series):
        pts = [(x + (i + 0.5) / n * w, y_map(v)) for i, v in enumerate(vs)]
        d = polyline(pts, line_w)
        vb = f"0 0 {w:.2f} {h:.2f}"
        kids.append(at(x, y, clip_path(d, box(width=w, height=h, color=colors[si]),
                                        viewBox=vb, fit="FILL"), width=w, height=h))
        for i, p in enumerate(pts):
            if labels_at is None or i in labels_at:
                kids.append(at(p[0] - marker_r, p[1] - marker_r,
                               clip_path(rounded_rect(0, 0, marker_r * 2,
                                                      marker_r * 2, marker_r),
                                         box(width=marker_r * 2, height=marker_r * 2,
                                             color=colors[si]),
                                         viewBox=f"0 0 {marker_r*2} {marker_r*2}",
                                         fit="FILL"),
                               width=marker_r * 2, height=marker_r * 2))
        if labels_at is not None and label_size and value_fmt:
            for i in labels_at:
                p = pts[i]
                lb = value_fmt(vs[i])
                tw = text_width(lb, label_size, True)
                kids.append(at(p[0] - tw / 2, p[1] - label_size * 1.4 - 8,
                               txt(0, 0, lb, size=label_size, color=INK, bold=True,
                                   align_text="CENTER", w=tw * 1.2),
                               width=tw * 1.2, height=label_size * 1.3))
    return layer(w + 160, h + 40, *kids)


# --- 环形图 ----------------------------------------------------------------
def donut(x, y, d, *, segments, hole=0.62, labels=None, label_size=FS_CAP,
          gap_deg=1.6, color=MUTED, label_color=INK2, ring=None) -> str:
    """segments=[(label, value, color)]；环形图 + 引出标注。"""
    from dsl import arc_path
    total = sum(v for _, v, _ in segments) or 1
    r1 = d / 2
    r0 = r1 * hole
    kids = []
    a = -90.0
    for i, (lb, v, c) in enumerate(segments):
        ang = v / total * 360
        a1 = a + ang
        path = arc_path(r1, r1, r0, r1, a + gap_deg / 2, a1 - gap_deg / 2)
        kids.append(at(0, 0, clip_path(path, box(width=d, height=d, color=c),
                                        viewBox=f"0 0 {d} {d}", fit="FILL"),
                      width=d, height=d))
        a = a1
    return at(x, y, layer(d, d, *kids), width=d, height=d)


# --- 页脚与注脚 ------------------------------------------------------------
def footer(x, y, w, s, *, size=FS_CAP, color=MUTED, lines=1, h=None) -> str:
    h = h or size * 1.5 * lines
    return at(x, y, txt(0, 0, s, size=size, color=color, w=w), width=w, height=h)


def divider(x, y, w, color=GRID, thickness=1) -> str:
    return at(x, y, box(width=w, height=thickness, color=color), width=w, height=thickness)


def pill(x, y, s, *, size=FS_CAP, color=INK, fill=None, pad=(8, 14), radius=None) -> str:
    tw = text_width(s, size, True)
    w = tw + pad[1] * 2
    h = size * 1.4 + pad[0] * 1.4
    r = radius if radius is not None else h / 2
    return at(x, y, box(layer(w, h, txt(pad[1] + 2, pad[0] * 0.7, s, size=size,
                                        color=color, bold=True)),
                        width=w, height=h, color=fill or RING, radius=r),
               width=w, height=h)


def badge_dot(x, y, c, d=10) -> str:
    return at(x, y, clip_path(rounded_rect(0, 0, d, d, d / 2),
                              box(width=d, height=d, color=c),
                              viewBox=f"0 0 {d} {d}", fit="FILL"), width=d, height=d)
