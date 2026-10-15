#!/usr/bin/env python
# B05 共用设计系统：「霜标 FrostMark」十件界面的色板、层板、状态条与页脚。
# 启动基准：总任务根 (suite_root)。
#
# 【系统规则】见 tmp/run-20261011-01/B05/plan-v1.md，摘要：
#   R3 剩余天数分档：≤1 红 / 2–3 橙 / 4–7 霜青 / >7 灰蓝；冷冻读数用冰蓝。
#   R4 温度状态：正常苔绿 / 偏高琥珀 / 告警灼红。
#   R5 每页页脚固定一句免责。
#   R6 手机正文 ≥16px，横屏与纸面 ≥17px。
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B05"))
from bsnap import (LINE, W500, W600, canvas, circle, em_width, line_h,
                   polyline, rect, segment, txt, wrap)

import b05data as D

# ── 深色 App 底 + 纸面底两套
BG = "#0B1220"
PANEL = "#121C2E"
PANEL2 = "#1A2740"
HAIR = "#26374F"
INK = "#EEF3FA"
SUB = "#9FB0C6"
DIM = "#6B7F9B"

FROST = "#5EE0D2"      # 霜青：品牌主色
WARM = "#F5A524"       # 琥珀：2–3 天 / 温度偏高
DANGER = "#F2555A"     # 灼红：≤1 天 / 温度告警
SAFE = "#3FBF87"       # 苔绿：正常
ICE = "#7C9CFF"        # 冰蓝：冷冻
MUTED = "#7E8FAA"      # 灰蓝：>7 天

PAPER = "#FBF8F2"      # 纸面（开箱卡 / 档案页）
PAPER2 = "#EEE8DA"     # 纸面凹槽
KRAFT = "#E2D9C7"      # 牛皮纸桌面
INKD = "#1B2331"       # 纸面正文
SUBD = "#6A7385"       # 纸面次要
RULED = "#D9D1C0"      # 纸面分割线

FOOTER_NOTE = "霜标 FrostMark · 界面稿；数据为自拟示例，非真实家庭记录"

NAV = ["冰箱", "记录", "建议", "我的"]


def band(days: float) -> str:
    """R3：剩余天数 → 颜色。"""
    if days <= 1:
        return DANGER
    if days <= 3:
        return WARM
    if days <= 7:
        return FROST
    return MUTED


def day_text(days: int) -> str:
    if days >= 365:
        return "1 年+"
    return f"剩 {days} 天"


# ══════════════════════════ 手机共用构件 ══════════════════════════
PHONE_W = 720
PHONE_H = 1600
M = 26                      # 左右安全边距
CW = PHONE_W - 2 * M         # 664
NAV_TOP = 1448
BOTTOM_NOTE_Y = 1552         # 页脚免责那一行


def statusbar(b, time, w=PHONE_W, dark=True):
    """状态栏：真实时刻 + 信号 + 电池。"""
    fg = INK if dark else INKD
    weak = "#9AA3B2"
    b.append(txt(time, M, 15, 140, None, 19, fg, W600))
    bx = w - M - 78
    for i in range(4):
        hgt = 5 + i * 3
        b.append(rect(bx + i * 9, 33 - hgt, 6, hgt, fg if dark else weak, 2))
    b.append(rect(bx + 42, 15, 34, 17, None, 5, border=f'1 SOLID {fg if dark else weak}'))
    b.append(rect(bx + 48, 20, 22, 7, fg if dark else weak, 2))
    b.append(rect(bx + 77, 20, 3, 7, fg if dark else weak, 1))


def chevron(b, x, y, color, size=9, width=2.4):
    b.append(segment(x + size, y, x, y + size * 0.78, color, width))
    b.append(segment(x, y + size * 0.78, x + size, y + size * 1.56, color, width))


def appbar(b, y, title, sub=None, back=True, action=None,
           action_color=FROST, title_size=27, w=PHONE_W, dark=True):
    """App 栏：左侧返回、中央标题、右侧动作标签。返回下一行 y。"""
    fg = INK if dark else INKD
    tx = (M + 34) if back else M
    if back:
        chevron(b, M + 2, y + 14, SUB if dark else SUBD)
    b.append(txt(title, tx, y + 2, w - M - tx - 130, None, title_size, fg, W600))
    if sub:
        b.append(txt(sub, tx, y + 4 + line_h(title_size), w - M - tx - 130,
                     None, 17, DIM if dark else SUBD))
    if action:
        b.append(txt(action, w - M - 210, y + 10, 210, None, 18, action_color,
                     W600, align="END"))
    y2 = y + 2 + line_h(title_size)
    if sub:
        y2 += line_h(17) + 2
    return y2 + 10


def navbar(b, active, w=PHONE_W, h=PHONE_H, top=NAV_TOP):
    """底部四标签导航：冰箱 / 记录 / 建议 / 我的。"""
    b.append(rect(0, top, w, h - top, PANEL, 0))
    b.append(rect(0, top, w, 1, HAIR))
    n = len(NAV)
    cw = w / n
    for i, name in enumerate(NAV):
        cx = cw * (i + 0.5)
        on = (name == active)
        col = FROST if on else SUB
        if on:
            b.append(rect(cx - 30, top - 20, 60, 3, col, 2))
        ix, iy = cx, top + 36
        if name == "冰箱":
            b.append(rect(ix - 13, iy - 15, 26, 31, None, 4, border=f'2 SOLID {col}'))
            b.append(rect(ix - 13, iy - 4, 26, 1.6, col))
            b.append(rect(ix + 4, iy - 12, 2.4, 7, col, 1))
            b.append(rect(ix + 4, iy + 1, 2.4, 7, col, 1))
        elif name == "记录":
            for k in range(3):
                b.append(rect(ix - 12, iy - 12 + k * 10, 24, 4, col, 2))
                b.append(rect(ix - 18, iy - 11 + k * 10, 3.5, 3.5, col, 1.8))
        elif name == "建议":
            b.append(circle(ix, iy, 29, None, border=f'2 SOLID {col}'))
            b.append(segment(ix - 8, iy + 1, ix - 2, iy + 7, col, 2.6))
            b.append(segment(ix - 2, iy + 7, ix + 9, iy - 7, col, 2.6))
        else:
            b.append(circle(ix, iy - 8, 13, None, border=f'2 SOLID {col}'))
            b.append(rect(ix - 15, iy + 3, 30, 15, None, 7, border=f'2 SOLID {col}'))
        b.append(txt(name, cx - 50, top + 58, 100, None, 17, col,
                     W600 if on else W500, align="CENTER"))


def bottom_note(b, w=PHONE_W, y=BOTTOM_NOTE_Y, note=FOOTER_NOTE, color=DIM):
    b.append(rect(M, y, w - 2 * M, 1, HAIR))
    b.append(txt(note, M, y + 9, w - 2 * M, None, 16, color, align="CENTER"))


def footer(b, x, y, w, note=FOOTER_NOTE, color=DIM, line_color=HAIR, size=16):
    b.append(rect(x, y, w, 1, line_color))
    b.append(txt(note, x, y + 10, w, None, size, color))
    return y + 10 + line_h(size)


def btn(b, x, y, w, h, label, fill=FROST, ink="#06231F", size=20, radius=12,
        outline=None):
    if fill:
        b.append(rect(x, y, w, h, fill, radius))
        col = ink
    else:
        b.append(rect(x, y, w, h, None, radius, border=f'2 SOLID {outline}'))
        col = outline
    b.append(txt(label, x, y + (h - int(size * 1.4)) // 2, w, None, size, col,
                 W600, align="CENTER"))
    return y + h


# ══════════════════════════ 冰箱剖面（R1 层位 / R3 分档） ══════════════════════════
CHIP_W, CHIP_H, CHIP_GAP, CHIP_COLS = 100, 56, 8, 6
FRIDGE_X, FRIDGE_W, FRIDGE_PAD = 16, 688, 14


def food_chip(b, x, y, name, days, frozen=False):
    col = ICE if frozen else band(days)
    b.append(rect(x, y, CHIP_W, CHIP_H, PANEL2, 10))
    b.append(rect(x, y, CHIP_W, 4, col, 2))
    b.append(txt(name, x + 9, y + 10, CHIP_W - 16, None, 17, INK, W500))
    b.append(txt(day_text(days), x + 9, y + 31, CHIP_W - 16, None, 16, col))


def shelf_header(b, x, y, right_x, name, n, patch_no=None, temp=None,
                 temp_state=None):
    b.append(txt(name, x, y, 160, None, 20, INK, W600))
    nx = x + em_width(name, 20) + 12
    b.append(txt(f"{n} 件", nx, y + 4, 100, None, 16, DIM))
    nx += em_width(f"{n} 件", 16) + 14
    if patch_no:
        b.append(rect(nx, y - 1, 25, 25, FROST + "2E", 13, border=f'1 SOLID {FROST}77'))
        b.append(txt(str(patch_no), nx, y + 4, 25, None, 16, FROST, W600,
                     align="CENTER"))
    if temp is not None:
        col = {"正常": SAFE, "偏高": WARM, "告警": DANGER}[temp_state]
        # 首版把「正常」右对齐到 right_x，和层位右沿贴死——图上「常」字右边被切掉。
        # 现在状态字停在 right_x-34，给指示点留出 20px，文字与右沿之间始终有净空。
        b.append(txt(temp_state, right_x - 108, y + 5, 74, None, 16, DIM,
                     align="END"))
        b.append(txt(f"{temp:.1f} ℃", right_x - 232, y + 2, 118, None, 19, col,
                     W600, align="END"))
        b.append(circle(right_x - 14, y + 11, 10, col))


def group_label(b, x, y, w, name, liters, color):
    b.append(rect(x, y + 2, 3, 20, color, 2))
    b.append(txt(name, x + 12, y - 1, 160, None, 21, color, W600))
    b.append(txt(liters, x + w - 200, y + 3, 200, None, 17, DIM, align="END"))


def fridge_block(b, x, y, w, data, temps, hint_empty="空层位 · 放了什么记一笔",
                 radius=24, pad_top=16, pad_bottom=18):
    """两遍走：先量高，再画壳，最后画内容——避免渐变/实心块压住文字。"""
    # —— 第一遍：量高
    h = pad_top
    last_group = None
    for sh in D.SHELVES:
        grp = D.GROUP_OF[sh]
        if grp != last_group:
            h += 34
            last_group = grp
        h += 32
        n = len(data.get(sh, []))
        h += ((((n + CHIP_COLS - 1) // CHIP_COLS) * (CHIP_H + 10)) if n else 56)
        h += 10
    h -= 10
    h += pad_bottom
    b.append(rect(x, y, w, h, PANEL, radius, border=f'1 SOLID {HAIR}'))
    fridge_inner(b, x, y, w, h, data, temps, hint_empty)
    return y + h


def fridge_inner(b, x, y, w, h, data, temps, hint_empty):
    cx = x + FRIDGE_PAD
    cwid = w - 2 * FRIDGE_PAD
    right_x = x + w - FRIDGE_PAD
    chip_x = cx + 10
    inner_w = CHIP_COLS * CHIP_W + (CHIP_COLS - 1) * CHIP_GAP

    cy = y + 16
    last_group = None
    for sh in D.SHELVES:
        grp = D.GROUP_OF[sh]
        if grp != last_group:
            group_label(b, cx, cy, cwid, grp,
                        f"{D.COLD_L} L" if grp == "冷藏" else f"{D.FREEZE_L} L",
                        FROST if grp == "冷藏" else ICE)
            cy += 34
            last_group = grp
        its = data.get(sh, [])
        t = temps.get(sh)
        shelf_header(b, cx, cy, right_x, sh, len(its), D.PATCH_OF.get(sh),
                     t[0] if t else None, t[1] if t else None)
        cy += 32
        if its:
            for i in range(0, len(its), CHIP_COLS):
                for j, (nm, days) in enumerate(its[i:i + CHIP_COLS]):
                    food_chip(b, chip_x + j * (CHIP_W + CHIP_GAP), cy, nm, days,
                              frozen=(grp == "冷冻"))
                cy += CHIP_H + 10
        else:
            b.append(rect(chip_x, cy + 6, inner_w, 44, None, 10, border=f'1 SOLID {HAIR}'))
            b.append(txt(hint_empty, chip_x + 16, cy + 18, inner_w - 32, None, 17, DIM))
            cy += 56
        cy += 10
    return cy - 10 + 18


# ══════════════════════════ 通用小构件 ══════════════════════════
def patch_chip(b, x, y, no, shelf, temp, state, cw=214, ch=84, target=None):
    """三枚贴片读数卡（首页 / 告警 / 设置共用）。"""
    col = {"正常": SAFE, "偏高": WARM, "告警": DANGER}[state]
    b.append(rect(x, y, cw, ch, PANEL, 12))
    b.append(rect(x, y, cw, 3, col, 2))
    b.append(rect(x + 14, y + 16, 23, 23, FROST + "2E", 12, border=f'1 SOLID {FROST}66'))
    b.append(txt(str(no), x + 14, y + 21, 23, None, 15, FROST, W600, align="CENTER"))
    b.append(txt(shelf, x + 44, y + 21, cw - 58, None, 18, SUB))
    t = f"{temp:.1f}".replace("-", "−")
    b.append(txt(t, x + 14, y + 40, cw - 60, None, 27, col, W600))
    b.append(txt("℃", x + 14 + em_width(t, 27) + 3, y + 51, 40, None, 17, col))
    if target is not None:
        # 首版「目标 -18.0」只给 78px 盒宽，86px 的字被裁掉了尾部的「℃」，图上
        # 显示成「目标 4.0」。盒子给到 114 并去掉右侧指示点（顶部色条已经表意）。
        b.append(txt(f"目标 {target:.1f}".replace("-", "−"), x + cw - 128, y + 54,
                     114, None, 16, DIM, align="END"))


def patch_disc(b, cx, cy, d, no, lit=True, shell="#FFFFFF", shell_bd="#C9D2E0",
               inner="#F2F5F9"):
    """贴片实物（几何占位，非照片）：圆角方 + 中心指示点。"""
    b.append(rect(cx - d / 2, cy - d / 2, d, d, shell, d * 0.30,
                  border=f'2 SOLID {shell_bd}'))
    b.append(rect(cx - d / 2 + d * 0.09, cy - d / 2 + d * 0.09, d * 0.82, d * 0.82,
                  inner, d * 0.25))
    b.append(circle(cx, cy, d * 0.19, SAFE if lit else "#C4CCDA"))


def check_box(b, x, y, s=20, done=True, color=SAFE, off="#C9D2E0"):
    b.append(rect(x, y, s, s, None, 5, border=f'2 SOLID {color if done else off}'))
    if done:
        b.append(segment(x + 4, y + s / 2, x + s / 2 - 1, y + s - 5, color, 2.4))
        b.append(segment(x + s / 2 - 1, y + s - 5, x + s - 3, y + 4, color, 2.4))


def kv(b, x, y, k, v, kw=None, vw=280, size=18, kcolor=SUB, vcolor=INK,
       align=None, vweight=W600):
    if kw is None:
        kw = em_width(k, size) + 16
    b.append(txt(k, x, y, kw, None, size, kcolor))
    b.append(txt(v, x + kw, y, vw, None, size, vcolor, vweight, align=align))
    return y + line_h(size) + 10


def section(b, x, y, w, label, right=None, color=INK, size=20, rule=True,
            right_color=FROST):
    b.append(txt(label, x, y, w - 200, None, size, color, W600))
    if right:
        b.append(txt(right, x + w - 220, y + 2, 220, None, 17, right_color,
                     align="END"))
    yy = y + line_h(size) + (12 if rule else 8)
    if rule:
        b.append(rect(x, yy - 6, w, 1, HAIR))
    return yy


def para(b, t, x, y, w, size=17, color=SUB, lh=None, gap=2):
    lh = lh or int(size * 1.42)
    for ln in wrap(t, size, w):
        b.append(txt(ln, x, y, w, None, size, color))
        y += lh + gap
    return y


def note_card(b, x, y, w, text, accent=FROST, size=17, color=SUB, h=None,
              radius=12, fill=PANEL):
    lines = wrap(text, size, w - 36)
    hh = h or (len(lines) * (int(size * 1.42) + 2) + 30)
    b.append(rect(x, y, w, hh, fill, radius))
    b.append(rect(x, y + 10, 3, hh - 20, accent, 2))
    yy = y + 15
    for ln in lines:
        b.append(txt(ln, x + 18, yy, w - 36, None, size, color))
        yy += int(size * 1.42) + 2
    return y + hh


def assert_fit(y, bottom_limit, what):
    """G2：内容不得越过给定的下界。生成期就报错，不靠肉眼。"""
    if y > bottom_limit:
        raise AssertionError(f"[overflow] {what}: 内容到 {y:.0f} > 允许的 {bottom_limit}")
    return y
