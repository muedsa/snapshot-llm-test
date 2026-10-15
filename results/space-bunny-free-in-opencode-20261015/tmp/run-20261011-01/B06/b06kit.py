#!/usr/bin/env python
# B06 共用视觉系统：把「十件日常信息载体重设计」统一成一套可复用的版式构件。
#
# 设计取向：十件都是**重新设计的实物信息载体**（纸、标签、单据、包装），
# 所以基底走暖白纸面而不是深色仪表盘；每件换一个强调色，
# 让十张在同一条作品集里彼此可区分，又共享同一套排版骨架。
#
# 排版安全（沿用本 run 已实测的服务行为，见 _suite/BRIEF-B.md 与 B03 technique-notes）：
#  - 文字超出 Text 盒子会被**静默裁掉仍返回 200**；本模块所有文本都先过 em_width 自检。
#  - 后画的实心图元会**盖住**先画的文字；约定：先铺满所有底色块，再画图形，最后画文字。
#  - Text 盒高至少字号 × 1.40。
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
from bsnap import (FONT, INK, W400, W500, W600, canvas, circle, em_width,  # noqa: E402
                   line_h, rect, segment, txt, wrap)

# ── 纸面调色板 ──────────────────────────────────────────────────────────
PAPER = "#F3F0E9"     # 纸底
CARD = "#FFFFFF"      # 卡片
SHADE = "#E8E3D9"     # 次级底块（示意区、灰条）
HAIR = "#D5CEC0"      # 发丝线
INKD = "#151A21"      # 正文墨色
MUTE = "#6C7483"      # 次级文字
FAINT = "#9BA2AE"     # 三级文字 / 脚注
COOL = "#2F7F6F"      # 正向色
WARM = "#C0502F"      # 负向 / 注意色

# 十件各自的强调色（保持彼此可区分）
ACCENTS = {
    1: "#D2452F", 2: "#B8791B", 3: "#2C6DBF", 4: "#6B52C7",
    5: "#128A82", 6: "#2A5FD6", 7: "#C25A2E", 8: "#2F8A4B",
    9: "#B23A6E", 10: "#3C6486",
}

_TIGHT: list[tuple[float, str, str]] = []   # (余量比, 说明, 文本) 渲染前累积


def tight(text: str, size: float, box_w: float, where: str) -> float:
    """记录并返回一个文本在盒子里的宽度余量比；余量为负即会被服务端裁切。"""
    ratio = box_w / max(1e-6, em_width(text, size))
    _TIGHT.append((ratio, f"{where} · {text[:26]}", f"{size}px / 盒宽 {box_w:.0f}"))
    return ratio


def tighten_reset() -> None:
    _TIGHT.clear()


def tighten_report(n: int = 8) -> list[tuple[float, str, str]]:
    return sorted(_TIGHT)[:n]


# ── 文本原语 ────────────────────────────────────────────────────────────
def t(txt_s: str, x, y, w, size, color=INKD, weight=W600, align=None, h=None):
    """全模块统一的文本入口：先量宽，再输出。盒高默认向上取整到字号 × 1.45。"""
    tight(txt_s, size, w, "text")
    return txt(txt_s, x, y, w, h if h is not None else math.ceil(size * 1.45),
               size, color, weight, align)


def tw(txt_s: str, size: float) -> float:
    return em_width(txt_s, size)


def fit_size(s: str, size: float, max_w: float, floor: float = 12.0,
             slack: float = 0.975) -> float:
    """单行文本缩字号直到放得下（用于长标题，宁可略小也不被裁）。"""
    while size > floor and em_width(s, size) > max_w * slack:
        size -= 0.5
    return size


def hw(text: str, size: float, width: float) -> list[str]:
    """带悬挂标点的换行，但保证**每一行都真的放得下**。

    bsnap.wrap 收尾标点悬挂时会把标点挂到上一行，那一行可能因此超出给定宽度；
    服务端对超宽文本是静默裁切的，所以这里再补一道复核：
    超宽的行把首字并回上一行，仍放不下就按字宽重新切。
    """
    out: list[str] = []
    for ln in wrap(text, size, width):
        while ln and em_width(ln, size) > width:
            head, tail = ln[0], ln[1:]
            if out and em_width(out[-1] + head, size) <= width:
                out[-1] += head
                ln = tail
                continue
            n = len(ln)
            while n > 1 and em_width(ln[:n], size) > width:
                n -= 1
            if n <= 0:
                break
            out.append(ln[:n])
            ln = ln[n:]
        if ln:
            out.append(ln)
    return out


def para(b: list, s: str, x, y, w, size, color=MUTE, weight=W400, gap=7):
    for ln in hw(s, size, w - 6):
        b.append(t(ln, x, y, w, size, color, weight))
        y += line_h(size) + gap
    return y


# ── 结构构件 ────────────────────────────────────────────────────────────
def sheet(w: int, h: int, accent: str, bg: str = PAPER) -> str:
    return canvas(w, h, "", bg)


def masthead(b: list, idx: int, w: int, carrier: str, title: str, claim: str,
             accent: str, y: int = 46) -> int:
    """页头：行号 + 载体标签 + 一句话命题。

    首版把载体名排在左边、套系名排在右边，载体名一长两者就压在一起（case-01 看图发现）。
    现在载体名做成**右对齐胶囊**，左边只留行号，两者在任何画布宽度下都不会重叠。
    """
    b.append(t(f"{idx:02d} / 10", 56, y, 200, 22, accent, W600))
    cwid = tw(carrier, 20) + 32
    cxx = w - 56 - cwid
    b.append(rect(cxx, y - 7, cwid, 34, SHADE, 6))
    b.append(t(carrier, cxx + 16, y, cwid - 32, 20, accent, W600))
    y += 40
    ts = fit_size(title, 40, w - 112)
    b.append(t(title, 56, y, w - 112, ts, INKD, W600))
    y += line_h(ts) + 12
    b.append(t(claim, 56, y, w - 112, 21, accent, W500))
    y += line_h(21) + 14
    b.append(rect(56, y, w - 112, 1, HAIR))
    return y + 18


def structbar(b: list, x: int, y: int, w: int, accent: str,
              before: tuple[str, str, int], after: list[tuple[str, str]],
              h: int = 158) -> int:
    """信息结构对照条。

    before = (标签, 说明文字, 抽象行数)   —— 原结构的**中性示意**，不做丑化处理
    after  = [(层名, 这层回答什么), ...]    —— 重设计后的分层

    左半用等长细线示意「一长串同权信息」，右半用色块示意「分层」。
    """
    lab_l, cap_l, nrows = before
    lw = int(w * 0.455)
    rw = int(w * 0.455)
    ax = x + lw + 18
    rx = x + w - rw

    # 左：原结构
    b.append(rect(x, y, lw, h, SHADE, 10))
    b.append(t(lab_l, x + 18, y + 14, lw - 36, 19, MUTE, W600))
    caps = fit_size(cap_l, 18, lw - 40, 13)
    b.append(t(cap_l, x + 18, y + 42, lw - 36, caps, FAINT, W500))
    cols, gap = 14, 10
    rows_n = (nrows + cols - 1) // cols
    colw = (lw - 36 - gap * (cols - 1)) / cols
    y0 = y + 72
    for i in range(nrows):
        c, r = i // rows_n, i % rows_n
        bx = x + 18 + c * (colw + gap)
        by = y0 + r * 7
        if by + 4 > y + h - 10:
            break
        wfrac = 0.62 + 0.30 * ((i * 7) % 5) / 4.0
        b.append(rect(bx, by, colw * wfrac, 4, "#C9C2B2", 2))

    # 箭头
    b.append(t("→", ax, y + h / 2 - 20, w - lw - rw - 36, 30, accent, W600, align="CENTER"))

    # 右：新结构
    b.append(rect(rx, y, rw, h, CARD, 10))
    b.append(rect(rx, y, rw, 4, accent, 2))
    b.append(t(after[0][0] and "新结构 · 分层", rx + 18, y + 14, rw - 36, 19, accent, W600))
    ay = y + 48
    for i, (name, ans) in enumerate(after):
        bh = 30
        b.append(rect(rx + 18, ay, rw - 36, bh, SHADE, 6))
        b.append(rect(rx + 18, ay, 4, bh, accent, 2))
        b.append(t(name, rx + 32, ay + 5, 150, 18, INKD, W600))
        s2 = fit_size(ans, 17, rw - 36 - 150 - 20, 11)
        b.append(t(ans, rx + 32 + 150, ay + 6, rw - 36 - 150 - 20, s2, MUTE, W500))
        ay += bh + 6
    return y + h


def section(b: list, x: int, y: int, w: int, no: str, name: str, accent: str,
            note: str | None = None) -> int:
    """分区标题：序号 + 名称 + 右侧注记。"""
    b.append(rect(x, y + 4, 4, 24, accent, 2))
    b.append(t(no, x + 16, y + 3, 46, 19, accent, W600))
    s = fit_size(name, 27, w - 16 - 60)
    b.append(t(name, x + 62, y, w - 16 - 60, s, INKD, W600))
    if note:
        ns = fit_size(note, 18, w * 0.44, 12)
        b.append(t(note, x + w - w * 0.44, y + 8, w * 0.44, ns, FAINT, W500, align="END"))
    return y + max(34, line_h(27))


def kicker(b: list, x: int, y: int, w: int, s: str, accent: str,
           size: int = 21, bg: str | None = None, lead: int = 78) -> int:
    """一句话结论条：新版版式的「第一层」永远是结论，不是过程。"""
    lines = hw(s, size, w - lead - 32)
    h = max(46, len(lines) * line_h(size) + max(0, len(lines) - 1) * 6 + 26)
    if bg:
        b.append(rect(x, y, w, h, bg, 8))
    b.append(rect(x, y, 4, h, accent, 2))
    b.append(t("结论", x + 18, y + (h - line_h(18)) / 2, 62, 18, accent, W600))
    yy = y + (h - len(lines) * line_h(size) - max(0, len(lines) - 1) * 6) / 2
    for ln in lines:
        b.append(t(ln, x + lead, yy, w - lead - 26, size, INKD, W600))
        yy += line_h(size) + 6
    return y + h


def pill(b: list, x: int, y: int, s: str, color: str, bg: str, size: int = 17,
         pad: int = 12, h: int = 30) -> int:
    w = tw(s, size) + pad * 2
    b.append(rect(x, y, w, h, bg, h / 2))
    b.append(t(s, x + pad, y + (h - line_h(size)) / 2, tw(s, size) + 4, size, color, W600))
    return x + w


def barrow(b: list, x: int, y: int, w: int, label: str, value: str, pct: float,
           color: str, lab_w: int = 190, val_w: int = 120, bh: int = 26,
           lab_size: int = 20, val_size: int = 20, sub: str | None = None,
           maxpct: float = 1.0) -> int:
    """一条：标签 / 比例条 / 数值。比例条按 maxpct 归一。"""
    b.append(t(label, x, y + (bh - line_h(lab_size)) / 2, lab_w, lab_size, INKD, W600))
    bx, bw = x + lab_w, w - lab_w - val_w
    b.append(rect(bx, y + (bh - 12) / 2, bw, 12, SHADE, 6))
    fw = max(6.0, bw * min(1.0, pct / maxpct))
    b.append(rect(bx, y + (bh - 12) / 2, fw, 12, color, 6))
    b.append(t(value, x + w - val_w, y + (bh - line_h(val_size)) / 2, val_w, val_size,
               color, W600, align="END"))
    ny = y + bh
    if sub:
        b.append(t(sub, bx, ny - 2, bw + val_w, 17, FAINT, W500))
        ny += line_h(17) - 4
    return ny


def rule(b: list, x: int, y: int, w: int, color: str = HAIR, h: int = 1) -> None:
    b.append(rect(x, y, w, h, color, 0))


def dot_scale(b: list, x: int, cy: int, n: int, filled: int, color: str,
              d: int = 11, gap: int = 6) -> int:
    """点阵量表（辣度、口味强度等 0–3）。返回结束 x。"""
    for i in range(n):
        c = color if i < filled else "#DED8CC"
        b.append(circle(x + d / 2 + i * (d + gap), cy, d, c))
    return x + n * (d + gap) - gap


def source_note(b: list, x: int, y: int, w: int, lines: list[str],
                size: int = 16, color: str = FAINT) -> int:
    """来源披露区：把「依据」和「未查证」都写进画面本身。"""
    yy = y
    for ln in lines:
        for sub in hw(ln, size, w - 8):
            b.append(t(sub, x, yy, w, size, color, W500))
            yy += line_h(size) + 3
    return yy


def footer(b: list, x: int, y: int, w: int, note: str, dark: bool = False) -> int:
    rule(b, x, y, w, "#3A4048" if dark else HAIR)
    yy = y + 14
    for ln in hw(note, 16, w - 8):
        b.append(t(ln, x, yy, w, 16, "#8A93A2" if dark else FAINT, W500))
        yy += line_h(16) + 4
    return yy


# ── 参考区间条（case-03 专用，但值得单独成件） ──────────────────────────
def range_bar(b: list, x: int, y: int, w: int, lo: float, hi: float,
              lo_lab: str, hi_lab: str, val: float, vmin: float, vmax: float,
              color: str) -> None:
    """把「正常区间」画成一条浅色带，异常区间加深，数值点用当前值定位。

    比例尺 vmin..vmax 覆盖【区间下沿、当前值、区间上沿】三者，超出部分按 1.6 倍外扩，
    所以「偏离多远」在画面上是**可量出来**的，而不是靠文字描述。
    """
    span = max(vmax - vmin, 1e-6)
    # 比例尺要同时装下「区间下沿、当前值、区间上沿」三者：先扩到含当前值的范围再留边
    lo2, hi2 = min(lo, val), max(hi, val)
    span = max(span, hi2 - lo2)
    pad = span * 0.30
    a, c = lo2 - pad, hi2 + pad

    def px(v: float) -> float:
        return x + (v - a) / (c - a) * w

    b.append(rect(x, y, w, 14, SHADE, 7))
    xl, xr = px(min(lo, hi)), px(max(lo, hi))
    b.append(rect(xl, y, xr - xl, 14, "#DCE3DC", 7))
    if val < lo:
        b.append(rect(x, y, max(2.0, xl - x), 14, "#E8C7BE", 7))
    elif val > hi:
        b.append(rect(xr, y, max(2.0, x + w - xr), 14, "#E8C7BE", 7))
    vx = px(val)
    b.append(rect(vx - 2, y - 5, 4, 24, color, 2))
    lab_w = min(120.0, w * 0.42)
    lx = min(max(x, xl - lab_w / 2), x + w - lab_w)
    rxx = min(max(x, xr - lab_w / 2), x + w - lab_w)
    b.append(t(lo_lab, lx, y + 20, lab_w, 15, FAINT, W500, align="CENTER"))
    b.append(t(hi_lab, rxx, y + 20, lab_w, 15, FAINT, W500, align="CENTER"))