# -*- coding: utf-8 -*-
"""B02 共享设计系统 · 叠光共享工具房（演示品牌）。

真实设计系统约定（十件作品都遵守）：
- 双底色模式：触点标识/印刷件（入口铭牌、守则海报、帮助立牌、报备小条、
  工具身份牌中打印面）用 paper 纸色系；看板/预约/屏幕件用 navy 深色系。
- 字号阶梯：display 64 / h1 40 / h2 30 / body 24 / small 20 / micro 18（仅印刷件）。
- 组件：diamond_wave 装饰带 / pill / bar_row / step_chips / gauge(▲) / 卡片栅格。
- 圆角统一 14（屏）/ 10（印）；品牌名与演示声明每件出现。
"""
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
BASE = TASK_ROOT / "outputs" / RUN / "B02"
CJK = "Noto Sans CJK SC"
NUM = "Inter"

# ---- 色板（design-system.json 同源） ----
NEAVY = "#0B1B33"      # 深藏青底（屏）
NEAVY2 = "#13284A"     # 卡片底（屏）
NEAVY3 = "#1B355F"     # 斑马次行（屏）
Paper = "#F4ECDC"      # 纸底（印）
Paper2 = "#FAF5EA"     # 纸面卡（印）
Charcoal = "#2A2A35"   # 墨色（印）
AMBER = "#FFC154"      # 品牌主强调（两族共用）
MIST = "#7FA9D9"       # 辅助蓝（屏）
TEAL2 = "#3ECFA5"      # 好状态（屏）
CORAL = "#F08080"      # 坏状态（两族）
INKMUTE = "#8A8FA3"    # 屏灰色字
PAPERMUTE = "#6E6A5E"  # 纸灰字
DANGER = "#D64550"

TOOLS = ["电钻", "缝纫机", "3D 打印", "自行车维修台", "木工台", "激光测距"]


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


def wrap_dsl(w, h, body, bg):
    return (f'<Snapshot background="{bg}" type="png">\n<Stack>\n'
            f'<SizedBox width="{w}" height="{h}" />\n' + "\n".join(body) +
            "\n</Stack>\n</Snapshot>\n")


def diamond_wave(s, x0, x1, y, band, color):
    """连续 45° 菱形装饰带（本设计系统的品牌条纹）。"""
    d = band * 0.66
    x = x0
    while x + d < x1:
        rot = ('<Transform matrix="(0.707107,-0.707107,0,0,0.707107,0.707107,'
               '0,0,0,0,1,0,0,0,0,1)" '
               f'origin="({fnum(d / 2)},{fnum(d / 2)})">')
        inner = (f'<Container width="{fnum(d)}" height="{fnum(d)}" '
                 f'color="{color}" />')
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y + band / 2 - d / 2)}" '
                 f'width="{fnum(d)}" height="{fnum(d)}">{rot}{inner}'
                 f'</Transform></Positioned>')
        x += d * 1.5


def pill(s, x, y, w, h, color, label, fsize, fcolor, bold=True, font=CJK,
         radius=None):
    rect(s, x, y, w, h, color, radius if radius is not None else h / 2)
    txt(s, x, y + (h - fsize - 2) / 2, label, fsize, fcolor, bold=bold,
        family=font, align="CENTER", box_w=w)


def bar_row(s, x, y, w_full, frac, h, color, track):
    rect(s, x, y, w_full, h, track, h / 2)
    if frac > 0:
        rect(s, x, y, max(w_full * frac, 8), h, color, h / 2)


def gauge(s, x, y, r, level, val_text, unit):
    """▲ 字块 gauge：level 0..5；下挂数值与单位。"""
    ch = "▲"
    fill = {0: NEAVY3, 1: CORAL, 2: TEAL2, 3: TEAL2, 4: AMBER, 5: AMBER}.get(
        max(level, 0))
    for i in range(5):
        col = fill if i < level else NEAVY3
        txt(s, x + i * (r * 0.36), y, ch, r * 0.34, col, family=CJK)
    txt(s, x, y + r * 0.34, f"{val_text} {unit}", r * 0.24, MIST)


def step_chips(s, x, y, items, done, w_each, h=64, dark=True, gap=12):
    """步骤链：已完成=琥珀底深字；当前=薄雾蓝顶条；未到=深条。"""
    for i, it in enumerate(items):
        done_i = i < done
        cur = i == done
        if done_i:
            rect(s, x, y, w_each, h, AMBER, 12)
            rect(s, x, y, w_each, 6, Charcoal, 12)
            txt(s, x, y + 26, it, 22, NEAVY, bold=True, align="CENTER",
                box_w=w_each)
        else:
            rect(s, x, y, w_each, h, NEAVY3 if dark else Paper2, 12)
            rect(s, x, y, w_each, 6, MIST if cur else "#12213D", 12)
            txt(s, x, y + 26, it, 22, "#D9E6F7" if dark else "#3D3C46",
                bold=cur, align="CENTER", box_w=w_each)
        x += w_each + gap


def brand_corner(s, x, y, dark=True):
    """小品牌角标：锤形几何记号 + 双语名。"""
    bg2 = AMBER
    rect(s, x, y, 46, 46, bg2, 12)
    rect(s, x + 10, y + 12, 18, 8, NEAVY, 2)          # 锤头
    rect(s, x + 16, y + 20, 8, 18, NEAVY, 3)          # 柄
    rect(s, x + 24, y + 12, 12, 8, NEAVY, 2)
    txt(s, x + 58, y + 2, "TOOL NEST", 20, NEAVY if dark else "#0E1B2E",
        bold=True, family=NUM)
    txt(s, x + 58, y + 26, "叠光共享工具房", 18, PAPERMUTE if dark else MIST)


def footer_note(s, x, y, w, text, dark=True):
    txt(s, x, y, text, 18, PAPERMUTE if dark else INKMUTE, box_w=w)


def demo_tag(s, x, y, dark=True):
    pill(s, x, y, 200, 40, Paper2 if dark else NEAVY2,
         "演示品牌 · 非真实运营", 16, PAPERMUTE if dark else INKMUTE, bold=False,
         radius=8)


def hline(s, x0, x1, y, color, ht=2):
    rect(s, x0, y, x1 - x0, ht, color)


CASES = []


def case(mark, w, h):
    def deco(fn):
        CASES.append((mark, w, h, fn))
        return fn
    return deco
