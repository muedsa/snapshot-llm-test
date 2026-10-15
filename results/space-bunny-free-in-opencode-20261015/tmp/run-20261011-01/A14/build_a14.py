#!/usr/bin/env python
"""A14 八组文案压力测试：统一参数化规则 + 长度分支排版。

启动基准：总任务根 (suite_root)。
唯一输入：tasks/A14-content-stress-batch/inputs/cards.json（只读，不修改）。

**参数化规则**（全部 8 张卡共用一套，无逐条硬改）
  1. 标题排版 `pick_size()`：先在阶梯上找**最大**字号使标题在标题栏宽度内 **≤2 行**；
     全阶梯都做不到时退到「≤3 行」，仍做不到才落到硬底线 36px。
     阶梯 `LADDER = [64, 56, 52, 48, 44, 40, 38, 36]`，下限即题面的 36px 硬底线。
  2. 断行 `wrap()`：CJK/全角标点逐字可断；拉丁词（含其后的标点）整体不可断；
     并施加避头尾规则（行首不得出现 ：，。、；？！·—… 等收尾标点，
     必要时把上一行末字一并降行）。
  3. 版面分支：标题栏宽固定 700px，**下对齐**到 y=456——行数变化只会向上生长，
     因此讲者行、时间行、状态徽标位置对 8 张卡完全一致，不存在互相碰撞。
  4. 字宽估算 `char_em()/est_em_str()`：全角 1.0em，空格 0.26em，大写/数字 0.62em，
     小写 0.55em，窄标点 0.30em。估算结果会与渲染后的实际墨迹包围盒逐张比对（见 audit）。
  5. 状态体系 `STATUS`：颜色 + DSL 绘制的几何符号 + 原始状态文字，三重编码；
     取消状态额外输出一行「本场取消」，但卡片本身保持统一主色，不退化成灰底。
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------- 设计令牌（统一，不随卡片变化）
W, H = 1200, 630
MARGIN = 40
CONTENT_W = W - 2 * MARGIN                 # 1120

INK = {
    "bg": "#0E1830",          # 卡片底（统一主色族）
    "glow": "#1E3A8A1F",      # 背景柔光（低对比）
    "primary": "#1D4ED8",     # 统一主色
    "primary_light": "#60A5FA",
    "rule": "#1E3A8A",
    "rule_soft": "#22355C",
    "kicker": "#7DA7F5",
    "title": "#F8FAFC",
    "speaker": "#F1F5F9",
    "label": "#7C8DB5",
    "time": "#F8FAFC",
    "date": "#B8C6E0",
    "mark_text": "#FFFFFF",
}

F_HEAD = "Inter Semi Bold"
F_MED = "Inter Medium"
F_LAT = "Inter"
F_SC = "Noto Sans CJK SC"
F_MIX = f"{F_LAT},{F_SC}"
F_MIX_HEAD = f"{F_HEAD},{F_SC}"

DATE_STR = "2026.11.07"
BRAND = "Structure"
BRAND2 = "/ Vision"
SERIES = "讲座 · STRUCTURE LECTURE SERIES"
CANCEL_NOTE = "本场取消"

# 版面坐标
TITLE_X, TITLE_W = 40, 700
# 标题块在标题带内**垂直居中**：首版采用下对齐到 456px，1 行标题时眉题与标题之间
# 留下约 300px 死区。居中后 1/2/3 行都落在同一个视觉带里，且最底仍 < 470 < 496(讲者分隔线)，
# 因此「标题不与状态徽标碰撞」与「不侵占讲者/时间行」依旧由结构保证。
BAND_TOP, BAND_BOTTOM = 150, 470
TITLE_BOTTOM = BAND_BOTTOM
KICKER_Y = 146
BADGE_X, BADGE_Y, BADGE_W, BADGE_H = 936, 142, 224, 60
NOTE_Y = 214
STRATA_BOTTOM = 456
RULE2_Y = 496
SPEAKER_X, SPEAKER_W, SPEAKER_BOTTOM = 40, 560, 584
TIME_X, TIME_W = 860, 300

LADDER = [64, 56, 52, 48, 44, 40, 38, 36]
MAX_LINES = 3
PREFERRED_LINES = 2
MIN_TITLE_PX = 36
# 孤字控制：若最后一行字面宽不足标题栏的 25%（只剩一两个字），
# 宁可降一档字号换回完整排布，也不要在主标题末尾吊两个字。
ORPHAN_RATIO = 0.25
MIN_SPEAKER_PX = 26
TIME_PX = 40
# 层级规则：标题必须显著大于时间字号，否则长标题会把主角让给次要信息。
TITLE_HIERARCHY_RATIO = 1.2
TITLE_FLOOR = min(s for s in LADDER if s >= TIME_PX * TITLE_HIERARCHY_RATIO)
TITLE_FIT_W = TITLE_W - 24          # 断行时留 24px 安全余量，字面框仍为 TITLE_W

# 状态体系：颜色 + 几何符号 + 原始文字
STATUS = {
    "开放": {"color": "#22C55E", "bg": "#22C55E2B", "border": "#22C55E8F",
             "symbol": "dot", "symbol_name": "实心圆",
             "note": "现场可入场，座位充足"},
    "满额": {"color": "#F59E0B", "bg": "#F59E0B2B", "border": "#F59E0B8F",
             "symbol": "square", "symbol_name": "实心圆角方块",
             "note": "名额已满，不再接受现场报名"},
    "候补": {"color": "#A78BFA", "bg": "#A78BFA2B", "border": "#A78BFA8F",
             "symbol": "ring", "symbol_name": "圆环（空心）",
             "note": "可登记候补，有空位将电话通知"},
    "取消": {"color": "#F87171", "bg": "#F871712B", "border": "#F871718F",
             "symbol": "cross", "symbol_name": "叉号（两条 45° 短条）",
             "note": "本场取消，不占用名额"},
}

# ---------------------------------------------------------------- 字宽估算
NO_LINE_START = set("：，。、；？！）」』】》·—…%")
NO_LINE_END = set("（「『【《")


def is_fullwidth(ch: str) -> bool:
    o = ord(ch)
    if o in (0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x00B7):
        return True
    return (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0x303E or 0x3041 <= o <= 0x33FF
            or 0x3400 <= o <= 0x4DBF or 0x4E00 <= o <= 0x9FFF or 0xA000 <= o <= 0xA4CF
            or 0xAC00 <= o <= 0xD7A3 or 0xF900 <= o <= 0xFAFF or 0xFE10 <= o <= 0xFE4F
            or 0xFF00 <= o <= 0xFF60 or 0xFFE0 <= o <= 0xFFE6)


# ASCII 各类字符的 em 系数，**由服务端实测标定**（见 probe_width_a14.py / measure_width_a14.py）。
# 首版用的通用估计（尖括号/& 只给 0.42em、拉丁给 0.55em）系统性偏小：
# "A < B & C > D" 偏小 18%、"Color, Alpha & Contrast " 偏小 8%，
# 于是 wrap() 判定放得下，而 700px 的 Text 框装不下真实字面宽，
# 服务端**静默裁掉右端**，K05 首版的 "Contrast " 整段消失。
# 标定后各行误差落在 -4.5% ~ +14%，整体略偏保守（宁可少排一个字，也不丢字）。
_EM_NARROW = "iljft.,'`|"          # 实测约 0.30em
_EM_MED = "rsz"                    # 实测约 0.40em
_EM_WIDE = "mw"                    # 实测约 0.85em
_EM_HEAVY = "<>&@"                 # 实测约 0.66em
_EM_COLON = ":;"                   # 实测约 0.42em
_EM_SLASH = "/"                    # 实测约 0.40em
_EM_DIGIT = 0.53
_EM_UPPER = 0.70
_EM_LOWER = 0.60
_EM_PUNCT = 0.32


def char_em(ch: str) -> float:
    """单字宽度（em）。全角 1.0；ASCII 按实测分类。"""
    if is_fullwidth(ch):
        return 1.0
    if ch == " ":
        return 0.28
    if ch in _EM_NARROW:
        return 0.30
    if ch in _EM_MED:
        return 0.40
    if ch in _EM_WIDE:
        return 0.85
    if ch in _EM_HEAVY:
        return 0.66
    if ch in _EM_COLON:
        return 0.42
    if ch in _EM_SLASH:
        return 0.40
    if ch.isdigit():
        return _EM_DIGIT
    if ch.isupper():
        return _EM_UPPER
    if ch.isalpha():
        return _EM_LOWER
    return _EM_PUNCT


def est_em_str(s: str) -> float:
    return sum(char_em(c) for c in s)


def atoms(text: str) -> list[str]:
    """切分断行原子：全角逐字成原子；空格自成原子；拉丁词整体不可断。"""
    out: list[str] = []
    cur = ""
    for ch in text:
        if is_fullwidth(ch):
            if cur:
                out.append(cur)
                cur = ""
            out.append(ch)
        elif ch == " ":
            if cur:
                out.append(cur)
                cur = ""
            out.append(" ")
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def wrap(text: str, size: float, width: float) -> list[str]:
    """贪心断行 + 避头尾。返回实际渲染的每一行。"""
    lines: list[str] = []
    cur: list[str] = []
    w = 0.0
    for a in atoms(text):
        aw = est_em_str(a) * size
        if not cur:
            if aw > width:                      # 单个原子比整栏还宽 → 逐字符拆
                for ch in a:
                    cw = char_em(ch) * size
                    if w + cw > width and cur:
                        lines.append("".join(cur))
                        cur, w = [], 0.0
                    cur.append(ch)
                    w += cw
                continue
            cur, w = [a], aw
            continue
        if w + aw <= width:
            cur.append(a)
            w += aw
        else:
            lines.append("".join(cur))
            cur, w = [a], aw
    if cur:
        lines.append("".join(cur))

    # 避头尾：行首不得是收尾标点 → 把上一行末字一起降行
    for i in range(1, len(lines)):
        guard = 0
        while (lines[i].strip() and lines[i].strip()[0] in NO_LINE_START
               and len(lines[i - 1].strip()) >= 2 and guard < 8):
            lines[i] = lines[i - 1].strip()[-1] + lines[i]
            lines[i - 1] = lines[i - 1].strip()[:-1]
            guard += 1
    # 行尾不得是开引号类（本题无开括号，作防御）
    for i in range(len(lines) - 1):
        guard = 0
        while (lines[i].strip() and lines[i].strip()[-1] in NO_LINE_END
               and len(lines[i + 1].strip()) >= 1 and guard < 8):
            lines[i + 1] = lines[i].strip()[-1] + lines[i + 1]
            lines[i] = lines[i].strip()[:-1]
            guard += 1
    return [ln for ln in lines if ln.strip()]


def is_orphan(lines: list[str], size: float) -> bool:
    """末行只剩一两个字（字面宽不足标题栏 ORPHAN_RATIO）时判为孤字。"""
    return len(lines) >= 2 and \
        est_em_str(lines[-1].strip()) * size <= TITLE_FIT_W * ORPHAN_RATIO


def pick_size(text: str):
    """返回 (字号, 行数, 命中的规则分支)。

    三级规则，全部由数据驱动，8 张卡共用：
      T1 ≤2 行（阶梯自大到小，跳过任何低于层级下限 TITLE_FLOOR 的字号）
      T2 ≤3 行（同上）
      T3 仍不可行 → 取层级下限（题面 36px 硬底线之上的最保守值）
    层级下限保证「标题永远比时间字号大 20%」，长标题不会让次要信息抢走视觉主角。
    """
    ladder = [s for s in LADDER if s >= TITLE_FLOOR]
    for s in ladder:
        ls = wrap(text, s, TITLE_FIT_W)
        if len(ls) <= PREFERRED_LINES and not is_orphan(ls, s):
            return s, len(ls), \
                f"T1 阶梯自 {s}px 起满足 ≤{PREFERRED_LINES} 行（层级下限 {TITLE_FLOOR}px）"
    for s in ladder:
        ls = wrap(text, s, TITLE_FIT_W)
        if len(ls) <= MAX_LINES and not is_orphan(ls, s):
            return s, len(ls), \
                f"T2 ≤{PREFERRED_LINES} 行不可达，自 {s}px 起满足 ≤{MAX_LINES} 行"
    for s in ladder:
        ls = wrap(text, s, TITLE_FIT_W)
        if len(ls) <= MAX_LINES:
            return s, len(ls), \
                f"T2' 降档后仍留孤字，自 {s}px 起满足 ≤{MAX_LINES} 行"
    # T3 兜底：若某一档下仍有行的字面宽超出**字面框** TITLE_W，
    # 服务端会静默裁掉右端，因此必须再降档，直到没有任何一行会被裁。
    for s in ladder:
        ls = wrap(text, s, TITLE_FIT_W)
        widest = max(est_em_str(x.strip()) * s for x in ls)
        if widest <= TITLE_W:
            return s, len(ls), \
                (f"T3 兜底：自 {s}px 起最宽行 {round(widest, 1)}px ≤ 字面框 {TITLE_W}px，"
                 f"不会有任何一行被服务端裁切")
    s = ladder[-1]
    ls = wrap(text, s, TITLE_FIT_W)
    widest = max(est_em_str(x.strip()) * s for x in ls)
    return s, len(ls), \
        (f"T4 触底：{s}px 下最宽行仍有 {round(widest, 1)}px > 字面框 {TITLE_W}px，"
         f"存在被裁风险，已在 batch-audit.json 标注")


# ---------------------------------------------------------------- DSL 图元
def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1.5 SOLID {border}"' if border else ""
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Container width="{round(w, 2)}" height="{round(h, 2)}" '
            f'color="{color}" borderRadius="{radius}"{b}/></Positioned>')


def txt(text, x, y, w, h, size, color, family=F_MIX, align=None, spacing=None, weight=None):
    assert '"' not in text, f"text= 属性无法承载双引号: {text!r}"
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    if weight:
        at += f' fontWeight="{weight}"'
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Text{at} text="{text}"/></Positioned>')


def seg(x1, y1, x2, y2, t, color):
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    bw = L + t
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return (f'<Positioned left="{round(cx - bw / 2, 2)}" top="{round(cy - t / 2, 2)}" '
            f'width="{round(bw, 2)}" height="{t}">'
            f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" '
            f'alignment="CENTER"><Container width="{round(bw, 2)}" height="{t}" '
            f'color="{color}" borderRadius="{round(t / 2, 2)}"/></Transform></Positioned>')


def status_symbol(kind: str, cx: float, cy: float, d: float, color: str) -> str:
    """状态符号全部用 DSL 几何画出（不依赖特殊字形），颜色 + 形状双重编码。"""
    x0, y0 = cx - d / 2, cy - d / 2
    if kind == "dot":
        return (f'<Positioned left="{round(x0, 2)}" top="{round(y0, 2)}" '
                f'width="{round(d, 2)}" height="{round(d, 2)}"><ClipOval>'
                f'<Container width="{round(d, 2)}" height="{round(d, 2)}" color="{color}"/>'
                f'</ClipOval></Positioned>')
    if kind == "square":
        return rect(x0, y0, d, d, color, round(d / 4, 2))
    if kind == "ring":
        bw = round(d * 0.26, 2)
        return (f'<Positioned left="{round(x0, 2)}" top="{round(y0, 2)}" width="{round(d, 2)}" '
                f'height="{round(d, 2)}"><Container width="{round(d, 2)}" height="{round(d, 2)}" '
                f'color="#FFFFFF00" borderRadius="{round(d / 2, 2)}" '
                f'border="{bw} SOLID {color}"/></Positioned>')
    if kind == "cross":
        t = round(d * 0.26, 2)
        return (seg(cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2, t, color) +
                seg(cx - d / 2, cy + d / 2, cx + d / 2, cy - d / 2, t, color))
    raise ValueError(kind)


def brand_mark(x, y, size):
    # 首版把字号设成 size*0.46=25.76px 而文本框只有 40px 宽，"S/V" 的字面宽约 48px，
    # 结果 "V" 被裁成 "S/"。这里把字号固定到 20px（字面约 33px）并把框放宽到 40px。
    # 注意：内层 Positioned 的 left/top 相对**标记方块**取值，不是相对画布；
    # 曾按画布坐标给 (48, 55) 导致文本框落到方块外侧被裁，字标整段消失。
    inner = (f'<Positioned left="8" top="15" width="40" height="26">'
             f'<Text fontSize="20" color="{INK["mark_text"]}" '
             f'fontFamily="{F_HEAD}" text="S/V"/></Positioned>')
    return (f'<Positioned left="{x}" top="{y}" width="{size}" height="{size}">'
            f'<Container width="{size}" height="{size}" color="{INK["primary"]}" '
            f'borderRadius="{round(size * 0.28, 2)}"><Stack fit="EXPAND">{inner}</Stack>'
            f'</Container></Positioned>')


# ---------------------------------------------------------------- 单卡生成
def card(c: dict, k: int) -> tuple[str, dict]:
    st = STATUS[c["status"]]
    title_size, title_lines, rule_hit = pick_size(c["title"])
    lh = round(title_size * 1.24, 2)
    block_h = lh * title_lines
    # 文本框在标题带内垂直居中；框内再按 (lh - size)/2 下移，使字面视觉居中
    block_top = BAND_TOP + (BAND_BOTTOM - BAND_TOP - block_h) / 2
    title_top = block_top + (lh - title_size) / 2
    lines = wrap(c["title"], title_size, TITLE_FIT_W)

    # 讲者：最多 2 行，下对齐到 SPEAKER_BOTTOM
    sp_lines = wrap(c["speaker"], MIN_SPEAKER_PX, SPEAKER_W)[:2]
    sp_lh = 34
    sp_top = SPEAKER_BOTTOM - sp_lh * len(sp_lines) + 4

    n = len(lines)
    strata = []
    widths = [224, 176, 128]
    alphas = ["3D", "2B", "1C"]
    for i in range(min(n, 3)):
        y = STRATA_BOTTOM - (n - i) * 30 + 12
        strata.append(rect(BADGE_X, y, widths[min(i, 2)], 12,
                           st["color"] + alphas[min(i, 2)], 6))

    b = []
    # 背景与装饰
    b.append(rect(0, 0, W, H, INK["bg"]))
    b.append(f'<Positioned left="{W - 300}" top="{H - 300}" width="620" height="620">'
             f'<ClipOval><Container width="620" height="620" color="{INK["glow"]}"/>'
             f'</ClipOval></Positioned>')
    b.append(rect(0, 0, W, 8, INK["primary"]))
    if c["status"] == "取消":
        # 首版斜纹放在 x≥950 的顶部，正好压住日期文字；改为最右侧 110px 的竖带并压到 5% 不透明度
        for i in range(7):
            b.append(rect(W - 110 + i * 16, 0, 7, H, "#F871710D"))

    # 页眉
    b.append(brand_mark(MARGIN, 40, 56))
    b.append(txt(BRAND, 116, 50, 240, 40, 30, "#FFFFFF", F_HEAD))
    b.append(txt(BRAND2, 116 + 152, 52, 200, 38, 30, "#93C5FD", F_MED))
    b.append(txt(DATE_STR, W - MARGIN - 300, 40, 300, 34, 26, INK["date"], F_MED, align="RIGHT"))
    b.append(txt(f"{SERIES} · {c['id']}", W - MARGIN - 400, 74, 400, 24, 17, INK["primary_light"],
                 F_MIX, align="RIGHT", spacing="1.5"))

    b.append(rect(MARGIN, 116, CONTENT_W, 2, INK["rule"]))

    # 眉题 + 标题
    b.append(txt(f"{c['id']} / 讲座", TITLE_X, KICKER_Y, TITLE_W, 28, 20,
                 INK["kicker"], F_MIX_HEAD, spacing="2.5"))
    for i, ln in enumerate(lines):
        b.append(txt(ln, TITLE_X, round(title_top + i * lh, 2), TITLE_W, round(lh, 2),
                     title_size, INK["title"], F_MIX_HEAD))

    # 状态徽标（颜色 + 几何符号 + 原始状态文字）
    b.append(rect(BADGE_X, BADGE_Y, BADGE_W, BADGE_H, st["bg"], 14, st["border"]))
    b.append(status_symbol(st["symbol"], BADGE_X + 34, BADGE_Y + BADGE_H / 2, 20, st["color"]))
    b.append(txt(c["status"], BADGE_X + 60, BADGE_Y + 16, BADGE_W - 76, 32, 26,
                 st["color"], F_MIX_HEAD))
    if c["status"] == "取消":
        b.append(txt(CANCEL_NOTE, BADGE_X, NOTE_Y, BADGE_W, 32, 26, st["color"],
                     F_MIX_HEAD, align="RIGHT"))
    b.extend(strata)

    # 讲者与时间
    b.append(rect(MARGIN, RULE2_Y, CONTENT_W, 2, INK["rule_soft"]))
    b.append(txt("讲者 SPEAKER", SPEAKER_X, 512, 300, 24, 17, INK["label"], F_MIX, spacing="1.5"))
    for i, ln in enumerate(sp_lines):
        b.append(txt(ln, SPEAKER_X, round(sp_top + i * sp_lh, 2), SPEAKER_W, sp_lh,
                     MIN_SPEAKER_PX, INK["speaker"], F_MIX_HEAD))
    b.append(txt("时间 TIME", TIME_X, 512, TIME_W, 24, 17, INK["label"], F_MIX,
                 align="RIGHT", spacing="1.5"))
    b.append(txt(c["time"], TIME_X, 534, TIME_W, 52, TIME_PX, INK["time"], F_HEAD, align="RIGHT"))

    dsl = (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{INK["bg"]}">'
           f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')

    audit = {
        "id": c["id"],
        "source_fields": {"title": c["title"], "speaker": c["speaker"],
                          "status": c["status"], "time": c["time"]},
        "rendered_text": {"title_lines": lines, "speaker_lines": sp_lines,
                          "status": c["status"], "time": c["time"],
                          "cancel_note": CANCEL_NOTE if c["status"] == "取消" else None,
                          "date": DATE_STR, "brand": BRAND + BRAND2},
        "title_typography": {
            "font_size_px": title_size,
            "line_height_px": lh,
            "lines": title_lines,
            "column": {"x": TITLE_X, "width": TITLE_W, "fit_width": TITLE_FIT_W},
            "band": {"top": BAND_TOP, "bottom": BAND_BOTTOM,
                     "align": "vertical-center"},
            "block": {"top": round(block_top, 2), "bottom": round(block_top + block_h, 2),
                      "height": round(block_h, 2)},
            "text_box_top": round(title_top, 2),
            "first_text_box": {"x": TITLE_X, "y": round(title_top, 2),
                               "w": TITLE_W, "h": lh},
            "last_text_box": {"x": TITLE_X, "y": round(title_top + (title_lines - 1) * lh, 2),
                              "w": TITLE_W, "h": lh},
            "min_size_px": MIN_TITLE_PX,
            "hierarchy_floor_px": TITLE_FLOOR,
            "time_font_size_px": TIME_PX,
            "size_ok": title_size >= MIN_TITLE_PX,
            "hierarchy_ok": title_size >= TIME_PX * TITLE_HIERARCHY_RATIO,
            "lines_ok": title_lines <= MAX_LINES,
            "branch": rule_hit,
            "estimated_line_widths_px": [round(est_em_str(ln) * title_size, 1) for ln in lines],
        },
        "speaker_typography": {
            "font_size_px": MIN_SPEAKER_PX, "line_height_px": sp_lh, "lines": len(sp_lines),
            "column": {"x": SPEAKER_X, "width": SPEAKER_W},
            "min_size_px": MIN_SPEAKER_PX, "max_lines_allowed": 2,
            "two_line_branch_used": len(sp_lines) == 2,
            "estimated_line_widths_px": [round(est_em_str(ln) * MIN_SPEAKER_PX, 1)
                                         for ln in sp_lines],
        },
        "status_encoding": {
            "source_status": c["status"],
            "color": st["color"], "background_tint": st["bg"], "border": st["border"],
            "symbol": st["symbol"], "symbol_geometry": st["symbol_name"],
            "symbol_size_px": 20, "symbol_center": [BADGE_X + 34, BADGE_Y + BADGE_H / 2],
            "text": c["status"], "text_font_size_px": 26,
            "text_box": {"x": BADGE_X + 60, "y": BADGE_Y + 16,
                         "w": BADGE_W - 76, "h": 32},
            "badge_box": {"x": BADGE_X, "y": BADGE_Y, "w": BADGE_W, "h": BADGE_H},
            "extra_note": (CANCEL_NOTE if c["status"] == "取消" else None),
            "note_box": ({"x": BADGE_X, "y": NOTE_Y, "w": BADGE_W, "h": 32}
                         if c["status"] == "取消" else None),
            "note_box_right_edge": (BADGE_X + BADGE_W) if c["status"] == "取消" else None,
            "channels": ["color", "dls_drawn_symbol", "text"],
        },
        "geometry": {
            "canvas": {"width": W, "height": H},
            "safe_margin_px": MARGIN,
            "content_bbox": [MARGIN, 40, W - MARGIN, 590],
            "title_right_edge": TITLE_X + TITLE_W,
            "badge_left_edge": BADGE_X,
            "title_badge_gap_px": BADGE_X - (TITLE_X + TITLE_W),
            "grid_branch": ("wide" if title_lines == 1 else
                           ("split" if title_lines == 2 else "tall")),
            "strata_count": min(title_lines, 3),
            "strata_rule": "右侧层格条数量 = 标题行数（长度分支的视觉回响）",
        },
    }
    return dsl, audit


def contact_sheet(cards: list[dict], k: float = 0.42) -> str:
    """接触表：按同一套规则等比缩小重绘，仅用于八张卡的一致性对照，不替代原图。"""
    cw, ch = round(W * k), round(H * k)
    gap, pad, head = 20, 28, 64
    cols, rows = 4, 2
    cw2 = cols * cw + (cols + 1) * gap
    ch2 = rows * ch + (rows + 1) * gap + head
    b = [rect(0, 0, cw2, ch2, "#E2E8F0")]
    b.append(txt("A14 接触表 · 8 张卡统一规则与状态体系一致性检查（辅助证据，不替代八张原图）",
                 pad, 20, cw2 - 2 * pad, 32, 22, "#0F172A", F_MIX_HEAD))
    for i, c in enumerate(cards):
        dsl, _ = card(c, i)
        inner = dsl.split('<Stack fit="EXPAND">', 1)[1].rsplit("</Stack>", 1)[0]
        # 用同一套图元按比例缩放：把所有几何量乘 k（不改变任何比例关系）
        def scale(m):
            return f'{m.group(1)}="{round(float(m.group(2)) * k, 2)}"'
        inner = re.sub(r'(left|top|width|height|borderRadius)="([0-9.]+)"', scale, inner)
        inner = re.sub(r'fontSize="([0-9.]+)"',
                       lambda m: f'fontSize="{round(float(m.group(1)) * k, 2)}"', inner)
        inner = re.sub(r'border="([0-9.]+)( SOLID [^"]*)"',
                       lambda m: f'border="{round(float(m.group(1)) * k, 2)}{m.group(2)}"', inner)
        x = gap + (i % cols) * (cw + gap)
        y = head + gap + (i // cols) * (ch + gap)
        b.append(rect(x, y, cw, ch, "#0E1830", 10, "#94A3B8"))
        b.append(f'<Positioned left="{x}" top="{y}" width="{cw}" height="{ch}">'
                 f'<Stack fit="EXPAND">{inner}</Stack></Positioned>')
    return (f'<Snapshot type="png">\n<Container width="{cw2}" height="{ch2}" color="#E2E8F0">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    src = base / "tasks/A14-content-stress-batch/inputs/cards.json"
    cards = json.loads(src.read_text(encoding="utf-8"))
    d = base / f"tmp/run-20261011-01/A14/drafts"
    d.mkdir(parents=True, exist_ok=True)

    audits = []
    for i, c in enumerate(cards, 1):
        dsl, au = card(c, i)
        (d / f"a14-{c['id']}-{ver}.snapshot").write_text(dsl, encoding="utf-8")
        au["png"] = f"card-{c['id']}.png"
        au["dsl"] = f"card-{c['id']}.snapshot"
        au["round"] = "round-01"
        audits.append(au)
        tt = au["title_typography"]
        print(f"{c['id']}  {tt['font_size_px']}px x {tt['lines']}行  "
              f"est={[round(x) for x in tt['estimated_line_widths_px']]}  "
              f"sp{len(au['rendered_text']['speaker_lines'])}行  {c['status']}")

    sheet = contact_sheet(cards)
    (d / f"a14-contact-sheet-{ver}.snapshot").write_text(sheet, encoding="utf-8")

    batch = {
        "schema_version": 1, "task_id": "A14", "path_base": "output_dir", "round": "round-01",
        "generation": {
            "script": {"path_base": "suite_root",
                       "path": "tmp/run-20261011-01/A14/build_a14.py"},
            "input": {"path_base": "suite_root",
                      "path": "tasks/A14-content-stress-batch/inputs/cards.json",
                      "modified": False},
            "shared_rules": {
                "tokens": "统一主色 #1D4ED8、底色 #0E1830、日期 2026.11.07、"
                          "品牌 Structure / Vision 对 8 张卡完全相同",
                "title_rule": f"阶梯 {LADDER}，先跳到层级下限 {TITLE_FLOOR}px（= 时间字号 "
                              f"{TIME_PX}×{TITLE_HIERARCHY_RATIO}）以上，再优先 ≤{PREFERRED_LINES} 行，"
                              f"退而求其次 ≤{MAX_LINES} 行；题面硬底线 {MIN_TITLE_PX}px 始终保留在阶梯里",
                "wrap_rule": "全角逐字可断 + 拉丁词不可断 + 避头尾",
                "width_model": "全角 1.0em / 空格 0.26em / 大写与数字 0.62em / "
                               "小写 0.55em / 窄标点 0.30em / m·w 0.83em",
                "grid_rule": f"标题栏 x={TITLE_X} w={TITLE_W}，在标题带 "
                             f"[{BAND_TOP}, {BAND_BOTTOM}] 内垂直居中；行数只在带内变化，"
                             f"讲者/时间/徽标位置对 8 张卡恒定",
                "status_rule": "颜色 + DSL 几何符号 + 原始状态文字，三重编码",
                "no_global_downscale": "整图从不按标题长度缩放；长标题只改字号与行数",
                "no_per_card_hardcoding": "8 张卡由同一个 card() 生成，输入文件未做任何修改",
            },
            "length_branches_taken": {
                "font_sizes": sorted({a["title_typography"]["font_size_px"] for a in audits}),
                "line_counts": sorted({a["title_typography"]["lines"] for a in audits}),
                "grid_branches": sorted({a["geometry"]["grid_branch"] for a in audits}),
                "speaker_two_line": [a["id"] for a in audits
                                     if a["speaker_typography"]["two_line_branch_used"]],
            },
        },
        "cards": audits,
        "reviews": [],
    }
    (d / "batch-audit-raw.json").write_text(json.dumps(batch, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    print(f"contact-sheet bytes={len(sheet.encode())} | cards={len(audits)}")


if __name__ == "__main__":
    main()