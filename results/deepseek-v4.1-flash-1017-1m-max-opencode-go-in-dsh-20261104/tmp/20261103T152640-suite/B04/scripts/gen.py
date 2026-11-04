# -*- coding: utf-8 -*-
"""B04: ten-piece editorial special on CJK/Latin mixed typesetting."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B04"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

PAPER, INK, DIM, RULE = "#FBFAF6", "#141414", "#6B7280", "#D9D3C6"
RED, BLUE = "#C8452D", "#1D4ED8"

def R(x, y, w, h, c, r=0, b=None):
    return K.rect(x, y, w, h, color=c, radius=r, border=b)

TXT = []
def T(page, key, x, y, s, w, size, c=INK, bold=False, align=None):
    TXT.append({"canvas": page, "key": key, "text": s, "box": [x, y, w], "size": size, "color": c})
    return K.text(x, y, s, width=w, size=size, color=c, bold=bold, align=align, label=key)

def page(no, kicker, title, sub, W, H, body, foot):
    p = [R(0, 0, W, H, PAPER)]
    p.append(R(0, 0, W, 8, INK))
    p.append(T(no, "kicker", 72, 56, kicker, 700, 20, RED, True))
    p.append(T(no, "title", 72, 88, title, W - 144, 46, INK, True))
    if sub:
        p.append(T(no, "sub", 72, 156, sub, W - 144, 21, DIM))
    p.append(R(72, 196, W - 144, 2, INK))
    p.extend(body)
    p.append(R(72, H - 92, W - 144, 1, RULE))
    p.append(T(no, "foot-l", 72, H - 76, foot, W - 320, 18, DIM))
    p.append(T(no, "foot-r", W - 260, H - 76, f"混排十讲 · {no}", 188, 18, DIM, align="RIGHT"))
    return K.document(W, H, p, background=PAPER)

# ---------------------------------------------------------------- case 1 cover
def c1():
    W, H = 1200, 1600
    p = [R(0, 0, W, H, PAPER)]
    p.append(R(72, 72, W - 144, 8, RED))
    p.append(T("case-01", "kicker", 72, 120, "视觉特辑 · 十讲", 600, 22, RED, True))
    p.append(T("case-01", "t1", 72, 190, "混排", 900, 150, INK, True))
    p.append(T("case-01", "t2", 72, 350, "为什么难", 900, 96, INK, True))
    p.append(R(72, 500, 200, 6, RED))
    p.append(T("case-01", "lead", 72, 546, "中文、日文与拉丁字母同处一行时，宽度、断行、", 1000, 24, INK))
    p.append(T("case-01", "lead2", 72, 584, "标点与数字的规则并不相同。这个特辑拆开十件事。", 1000, 24, INK))
    p.append(R(72, 700, W - 144, 2, RULE))
    items = ["六种默认宽度", "一个汉字一个方格", "四种断行风格", "行首禁则", "小假名的三档禁则",
             "全角空格", "中英混排断点", "数字与单位", "检查清单"]
    for i, it in enumerate(items):
        y = 740 + (i // 2) * 56
        x = 72 + (i % 2) * 520
        p.append(T("case-01", f"item-{i}", x, y, f"{i+2:02d}  {it}", 480, 24, INK))
    p.append(R(72, 1300, W - 144, 2, RULE))
    p.append(T("case-01", "src", 72, 1326,
               "依据：UAX #11 East Asian Width、UAX #14 Unicode Line Breaking Algorithm（Unicode 18.0.0）",
               1056, 18, DIM))
    p.append(T("case-01", "date", 72, 1362, "2026 · 编辑：本特辑作者", 700, 18, DIM))
    return K.document(W, H, p, background=PAPER)

# ---------------------------------------------------------------- case 2 width classes
def c2():
    W, H = 1200, 1500
    rows = [("W", "Wide", "汉字、假名、全角标点", "1 Em，竖排直立"),
            ("F", "Fullwidth", "全角 ASCII 兼容形（如 ！）", "1 Em"),
            ("H", "Halfwidth", "半角片假名等兼容形", "1/2 Em，竖排旋转"),
            ("Na", "Narrow", "ASCII 全部", "1/2 Em"),
            ("A", "Ambiguous", "希腊/西里尔、部分符号", "上下文决定，默认窄"),
            ("N", "Neutral", "其它（如天城文）", "按窄处理")]
    body = []
    for i, (code, name, ex, width) in enumerate(rows):
        y = 236 + i * 150
        body.append(R(72, y, W - 144, 130, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        body.append(T("case-02", f"code-{code}", 100, y + 22, code, 140, 40, RED, True))
        body.append(T("case-02", f"name-{code}", 250, y + 24, name, 300, 26, INK, True))
        body.append(T("case-02", f"ex-{code}", 250, y + 62, ex, 600, 20, DIM))
        body.append(T("case-02", f"w-{code}", 780, y + 44, width, 300, 22, INK, align="RIGHT"))
    body.append(T("case-02", "note", 72, 1160,
                  "六种默认值在具体操作时只解析成「窄」与「宽」两种结果。", 1056, 22, INK))
    body.append(T("case-02", "note2", 72, 1200,
                  "Ambiguous 在东亚上下文里可为宽，其余场景按窄处理。", 1056, 20, DIM))
    return page("02", "第 02 讲 · 宽度", "六种默认宽度，两种运行结果", "UAX #11 定义了六个取值；实现只关心最终是窄还是宽。",
                W, H, body, "来源：UAX #11 §3、§4（ED2–ED7）")

# ---------------------------------------------------------------- case 3 em box
def c3():
    W, H = 1200, 1400
    body = []
    body.append(R(300, 260, 300, 300, "#FFFFFF", 0, f"1 SOLID {INK}"))
    body.append(R(360, 320, 180, 180, "#F3E6D9", 0, f"1 SOLID {RED}"))
    body.append(T("case-03", "em", 360, 380, "永", 180, 90, INK, True, "CENTER"))
    body.append(T("case-03", "lbl-w", 620, 300, "宽字符：占 1 Em", 400, 24, INK, True))
    body.append(T("case-03", "lbl-w2", 620, 336, "等宽字体里就是一个方格", 460, 20, DIM))
    body.append(R(300, 640, 300, 160, "#FFFFFF", 0, f"1 SOLID {INK}"))
    body.append(R(300, 720, 160, 80, "#DDE7F5", 0, f"1 SOLID {BLUE}"))
    body.append(T("case-03", "half", 300, 736, "Ab", 160, 40, INK, True, "CENTER"))
    body.append(T("case-03", "lbl-h", 620, 660, "窄字符：占 1/2 Em", 400, 24, INK, True))
    body.append(T("case-03", "lbl-h2", 620, 696, "ASCII 属于 Narrow（Na）", 460, 20, DIM))
    body.append(R(72, 900, W - 144, 2, RULE))
    body.append(T("case-03", "p1", 72, 928, "UAX #11 把「Em」定义为东亚字体的单位宽度：标准字身是正方形。", 1056, 22, INK))
    body.append(T("case-03", "p2", 72, 966, "因此汉字的字身是 1 Em，拉丁字母在等宽字体里占 1/2 Em。", 1056, 22, INK))
    body.append(T("case-03", "p3", 72, 1016, "注意：这只是「默认宽度」，字体实际字面可能更小。", 1056, 20, DIM))
    body.append(T("case-03", "p4", 72, 1052, "左图为示意，不表示某个具体字体的字面率。", 1056, 18, DIM))
    return page("03", "第 03 讲 · Em", "一个汉字，一个方格", "宽窄的基准单位是 Em；它不是字体的实际墨迹宽度。",
                W, H, body, "来源：UAX #11 §1（Overview）、§5（Recommendations）")

# ---------------------------------------------------------------- case 4 line breaking styles
def c4():
    W, H = 1200, 1450
    body = []
    cols = [("Western", "空格与连字符决定断点", "The quick brown fox jumps over the lazy dog.", "只在这两处可断：词间空格、连字符"),
            ("East Asian", "任何位置都能断，除非被禁止", "这是一段中文，几乎每个字之间都可以断开。", "断点密到几乎每字一处"),
            ("South East Asian", "需要词法分析", "ภาษาไทยไม่ใช้ช่องว่าง", "没有空格，必须查词"),
            ("Brahmic", "按正字音节边界", "示例文字不在此展示", "需要字形簇知识")]
    for i, (name, desc, sample, note) in enumerate(cols):
        y = 236 + i * 270
        body.append(R(72, y, W - 144, 240, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        body.append(T("case-04", f"n-{i}", 100, y + 20, name, 500, 26, RED, True))
        body.append(T("case-04", f"d-{i}", 100, y + 58, desc, 900, 21, INK))
        body.append(T("case-04", f"s-{i}", 100, y + 96, sample, 900, 20, INK))
        body.append(T("case-04", f"o-{i}", 100, y + 136, note, 900, 19, DIM))
    body.append(T("case-04", "tail", 72, 1340,
                  "四种风格可以统一到同一套规则里，只是断点密度不同。", 1056, 22, INK))
    return page("04", "第 04 讲 · 断行", "四种断行风格", "混排之所以难，是因为同一行里可能同时出现两种风格。",
                W, H, body, "来源：UAX #14 §3.1（Determining Line Break Opportunities）")

# ---------------------------------------------------------------- case 5 kinsoku
def c5():
    W, H = 1200, 1400
    body = []
    body.append(T("case-05", "lead", 72, 236, "行首禁则：这些字符不能出现在一行的开头。", 1056, 24, INK, True))
    bad = [("CL", "、", "U+3001 IDEOGRAPHIC COMMA"), ("CL", "。", "U+3002 IDEOGRAPHIC FULL STOP"),
           ("CL", "，", "U+FF0C FULLWIDTH COMMA"), ("CP", "）", "U+FF09 FULLWIDTH RIGHT PARENTHESIS"),
           ("EX", "！", "U+FF01 FULLWIDTH EXCLAMATION MARK")]
    for i, (cls, ch, code) in enumerate(bad):
        y = 300 + i * 130
        body.append(R(72, y, 300, 110, "#FFFFFF", 8, f"1 SOLID {RULE}"))
        body.append(T("case-05", f"ch-{i}", 72, y + 24, ch, 300, 52, INK, True, "CENTER"))
        body.append(T("case-05", f"cls-{i}", 400, y + 20, cls, 160, 26, RED, True))
        body.append(T("case-05", f"code-{i}", 560, y + 26, code, 560, 20, DIM))
    body.append(R(72, 1000, W - 144, 2, RULE))
    body.append(T("case-05", "op", 72, 1028, "反向的一半：开引号与左括号不能落在行尾（OP 类）。", 1056, 22, INK))
    body.append(T("case-05", "op2", 72, 1066, "「（ 等开标点之后禁止断行，闭合标点之前禁止断行。", 1056, 20, DIM))
    body.append(T("case-05", "note", 72, 1120, "实际排版软件还会对连续标点做挤压，这部分不在 UAX 规范内。", 1056, 19, DIM))
    return page("05", "第 05 讲 · 禁则", "行首不能出现的字", "标点被单独分到另一行开头，是最容易被看见的排版错误。",
                W, H, body, "来源：UAX #14 Table 1（CL/CP/EX/OP 类）、§5.1 CL 小节")

# ---------------------------------------------------------------- case 6 CJ small kana
def c6():
    W, H = 1200, 1350
    body = []
    body.append(T("case-06", "lead", 72, 236,
                  "CJ 类：小假名与长音符。它们既可能被禁止行首，也可能允许。", 1056, 23, INK, True))
    body.append(R(72, 300, W - 144, 180, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    body.append(T("case-06", "chars", 100, 330, "ぁ ぃ ぅ ぇ ぉ ゃ ゅ ょ っ ー", 900, 46, INK))
    body.append(T("case-06", "chars2", 100, 400, "U+3041 起 · 小写平假名 · 片假名同理（U+30A1 起）", 900, 20, DIM))
    modes = [("strict", "把 CJ 当作 NS 处理", "行首禁止，最严格"),
             ("normal", "把 CJ 当作 ID 处理", "允许行首，书刊常用"),
             ("loose", "更少的禁则字符", "报纸短栏常用")]
    for i, (k, d, note) in enumerate(modes):
        y = 520 + i * 150
        body.append(R(72, y, W - 144, 130, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        body.append(T("case-06", f"m-{i}", 100, y + 20, k, 220, 26, RED, True))
        body.append(T("case-06", f"d-{i}", 320, y + 22, d, 500, 21, INK))
        body.append(T("case-06", f"o-{i}", 320, y + 60, note, 500, 19, DIM))
    body.append(T("case-06", "tail", 72, 1020,
                  "三档禁则集合大小不同：strict 最大、loose 最小。", 1056, 22, INK))
    body.append(T("case-06", "tail2", 72, 1060,
                  "原因之一是：禁则字符越多，越容易触发整行挤压对齐。", 1056, 20, DIM))
    return page("06", "第 06 讲 · 小假名", "同一类字，三种禁则", "CJ 是可裁定的类别，取决于你选 strict、normal 还是 loose。",
                W, H, body, "来源：UAX #14 §5.1 CJ 小节（CSS Text Level 3 的 strict/normal/loose）")

# ---------------------------------------------------------------- case 7 ideographic space
def c7():
    W, H = 1200, 1300
    body = []
    body.append(R(72, 240, 500, 200, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    body.append(T("case-07", "sp1", 72, 280, "A　B", 500, 60, INK, align="CENTER"))
    body.append(T("case-07", "sp1c", 72, 380, "U+3000 IDEOGRAPHIC SPACE", 500, 20, DIM, align="CENTER"))
    body.append(R(628, 240, 500, 200, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    body.append(T("case-07", "sp2", 628, 280, "A B", 500, 60, INK, align="CENTER"))
    body.append(T("case-07", "sp2c", 628, 380, "U+0020 SPACE", 500, 20, DIM, align="CENTER"))
    body.append(T("case-07", "h1", 72, 480, "两者的断行类不同", 1056, 24, INK, True))
    body.append(T("case-07", "p1", 72, 520, "U+3000 属于 BA（Break After）类，提供断点但不参与间接断行的判定。", 1056, 21, INK))
    body.append(T("case-07", "p2", 72, 556, "U+0020 属于 SP 类，是「间接断行」的判定依据。", 1056, 21, INK))
    body.append(R(72, 620, W - 144, 2, RULE))
    body.append(T("case-07", "p3", 72, 648, "对排版的实际影响：中文里用 U+3000 做段首缩进，不会像空格那样被挤压。", 1056, 21, INK))
    body.append(T("case-07", "p4", 72, 686, "如果用 U+0020 缩进，两端对齐时缩进会被拉宽。", 1056, 21, INK))
    body.append(T("case-07", "p5", 72, 740, "上排两图宽度相同，字距不同——这是两个不同码位，不是同一个空格。", 1056, 19, DIM))
    return page("07", "第 07 讲 · 空格", "两个空格不是同一个空格", "U+3000 与 U+0020 的断行行为不同，混用会出问题。",
                W, H, body, "来源：UAX #14 Table 1（BA/SP 类）、§5.1 BA 小节的 U+3000 条目")

# ---------------------------------------------------------------- case 8 mixed paragraph
def c8():
    W, H = 1200, 1350
    body = []
    body.append(T("case-08", "lead", 72, 236, "同一段话，两种处理：", 1056, 24, INK, True))
    body.append(R(72, 280, W - 144, 170, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    body.append(T("case-08", "a1", 100, 306, "本刊使用 Snapshot DSL 排版，", 900, 26, INK))
    body.append(T("case-08", "a2", 100, 348, "每行 24 字，字号 16。", 900, 26, INK))
    body.append(T("case-08", "a3", 100, 396, "↑ 空格处可断，汉字之间也可断", 900, 19, RED))
    body.append(R(72, 480, W - 144, 170, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    body.append(T("case-08", "b1", 100, 506, "本刊使用Snapshot DSL排版，", 900, 26, INK))
    body.append(T("case-08", "b2", 100, 548, "每行24字，字号16。", 900, 26, INK))
    body.append(T("case-08", "b3", 100, 596, "↑ 没有空格，断点只由汉字决定", 900, 19, RED))
    body.append(R(72, 700, W - 144, 2, RULE))
    body.append(T("case-08", "p1", 72, 728, "拉丁词内部不可断（AL 类），汉字之间几乎处处可断（ID 类）。", 1056, 21, INK))
    body.append(T("case-08", "p2", 72, 766, "混排时，行尾会出现「拉丁词被整体推到下一行」的空隙。", 1056, 21, INK))
    body.append(T("case-08", "p3", 72, 804, "这就是为什么中英混排的字距常常看起来不匀。", 1056, 21, INK))
    body.append(T("case-08", "p4", 72, 858, "两段文字内容相同，第二段靠汉字断行，第一段多了一个可断的空格。", 1056, 19, DIM))
    return page("08", "第 08 讲 · 混排", "一个空格，改变断点分布", "拉丁词是不可分的整体，汉字几乎处处可断。",
                W, H, body, "来源：UAX #14 Table 1（AL/ID 类）、§5.1 AL 小节")

# ---------------------------------------------------------------- case 9 numbers
def c9():
    W, H = 1200, 1300
    body = []
    body.append(T("case-09", "lead", 72, 236, "数字有自己的一套类：不要让它被拆开。", 1056, 24, INK, True))
    rows = [("NU", "数字", "0–9", "构成数字表达式，内部不当断"),
            ("IS", "中缀分隔", ". ,", "数字前后的断点被抑制"),
            ("PR", "前缀", "$ £ ¥", "不得在其后断开"),
            ("PO", "后缀", "% ¢", "不得在其前断开")]
    for i, (cls, name, ex, rule) in enumerate(rows):
        y = 300 + i * 140
        body.append(R(72, y, W - 144, 120, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        body.append(T("case-09", f"c-{i}", 100, y + 22, cls, 140, 30, RED, True))
        body.append(T("case-09", f"n-{i}", 260, y + 24, name, 260, 24, INK, True))
        body.append(T("case-09", f"e-{i}", 540, y + 26, ex, 200, 26, INK))
        body.append(T("case-09", f"r-{i}", 100, y + 72, rule, 900, 19, DIM))
    body.append(R(72, 900, W - 144, 2, RULE))
    body.append(T("case-09", "good", 72, 928, "正确：1,280 元　12.5%　¥399", 1056, 26, INK, True))
    body.append(T("case-09", "bad", 72, 980, "错误：把「1,280 元」断成「1,280」与「元」分处两行", 1056, 21, DIM))
    body.append(T("case-09", "note", 72, 1030, "数字后紧跟单位时，单位应与数字同处一行；这不属于 UAX 的强制规则，属于编辑规则。", 1056, 19, DIM))
    return page("09", "第 09 讲 · 数字", "别把千分位拆到两行", "NU/IS/PR/PO 四类共同保护数字表达式。",
                W, H, body, "来源：UAX #14 Table 1（Numeric Context 四类）")

# ---------------------------------------------------------------- case 10 checklist
def c10():
    W, H = 1200, 1500
    body = []
    checks = ["段首缩进用 U+3000，不用 U+0020",
              "闭合标点不落行首（、。，）",
              "开标点不落行尾（「（",
              "拉丁词内部不断行",
              "数字与单位不拆行",
              "千分位与百分号跟随数字",
              "中文与拉丁之间留 1/4 Em 空隙",
              "竖排时拉丁串整体旋转",
              "全角标点不做字距拉伸",
              "导出前逐行检查行首行尾"]
    for i, c in enumerate(checks):
        y = 236 + i * 96
        body.append(R(72, y, 44, 44, "#FFFFFF", 6, f"2 SOLID {INK}"))
        body.append(T("case-10", f"n-{i}", 136, y - 2, c, 940, 23, INK))
    body.append(R(72, 1220, W - 144, 2, RULE))
    body.append(T("case-10", "tail", 72, 1248,
                  "前六条来自 UAX #11/#14 的类别定义；后四条是排印实践，规范未强制。", 1056, 20, DIM))
    body.append(T("case-10", "tail2", 72, 1290,
                  "把它们分开标注，是为了不把编辑经验说成标准。", 1056, 20, DIM))
    return page("10", "第 10 讲 · 清单", "导出前逐条勾掉", "十条检查，前六条有规范依据，后四条是经验。",
                W, H, body, "来源：UAX #11、UAX #14 各节；经验条目已标注")

CASES = [
    ("case-01", "封面：混排为什么难", c1, (1200, 1600), "cover", "特辑封面"),
    ("case-02", "六种默认宽度，两种运行结果", c2, (1200, 1500), "chart", "宽度分类表"),
    ("case-03", "一个汉字，一个方格", c3, (1200, 1400), "diagram", "Em 示意"),
    ("case-04", "四种断行风格", c4, (1200, 1450), "chart", "断行风格对照"),
    ("case-05", "行首不能出现的字", c5, (1200, 1400), "chart", "行首禁则"),
    ("case-06", "同一类字，三种禁则", c6, (1200, 1350), "chart", "CJ 类三档"),
    ("case-07", "两个空格不是同一个空格", c7, (1200, 1300), "diagram", "U+3000 vs U+0020"),
    ("case-08", "一个空格，改变断点分布", c8, (1200, 1350), "diagram", "混排断点"),
    ("case-09", "别把千分位拆到两行", c9, (1200, 1300), "chart", "数字类"),
    ("case-10", "导出前逐条勾掉", c10, (1200, 1500), "checklist", "检查清单"),
]

logger = api.TaskLogger(TASK, TMP)
ONLY = os.environ.get("B04_ONLY", "").split(",") if os.environ.get("B04_ONLY") else None
meta = []
for cid, title, fn, size, kind, note in CASES:
    if ONLY and cid not in ONLY:
        continue
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    dsl = fn()
    (d / "final.snapshot").write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(d / "final.snapshot", d / "final.png", cid)
    ok = rec["http_status"] == 200 and api.measure_png(d / "final.png") == size
    print(f"{cid}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s ok={ok}")
    for w in warn:
        print("   ", w)
    meta.append({"case": cid, "title": title, "size": list(size), "kind": kind, "note": note,
                 "png": f"{cid}/final.png", "dsl": f"{cid}/final.snapshot",
                 "bytes": rec["response_bytes"]})
if not ONLY:
    api.write_json(TMP / "cases.json", meta)
    api.write_json(TMP / "texts.json", TXT)
print("rendered", len(meta))
