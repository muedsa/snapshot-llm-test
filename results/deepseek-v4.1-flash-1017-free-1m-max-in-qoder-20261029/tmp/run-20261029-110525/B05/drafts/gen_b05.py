#!/usr/bin/env python3
"""B05 余味 AFTERTASTE — ten product screens for a shared-food-rescue ledger."""
import json, math, os
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
OUT = SUITE / 'outputs' / RUN / 'B05'
TMP = SUITE / 'tmp' / RUN / 'B05'
DATA = json.loads((TMP / 'shared-data.json').read_text(encoding='utf-8'))

PAPER = "#F4EFE6"; INK = "#1B1A17"; LEAF = "#3E6B4F"; TOMATO = "#C4472E"
AMBER = "#D9A441"; SAGE = "#DDE5D8"; CARD = "#FFFDF8"; LINE = "#D8CFC0"
MUT = "#6E6A60"; DARK = "#141A17"; NIGHT = "#1B211D"

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def T(txt, size, color=INK, bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def Tm(txt, size, color=INK, bold=False, extra=""):
    return T(txt, size, color, bold, extra, "Noto Sans Mono CJK SC")
def t(x, y, txt, size, color=INK, bold=False, extra="", w=None):
    wd = f' width="{w}"' if w else ""
    return f'<Positioned left="{x}" top="{y}"{wd}>' + T(txt, size, color, bold, extra) + '</Positioned>'
def tm(x, y, txt, size, color=INK, bold=False, extra=""):
    return f'<Positioned left="{x}" top="{y}">' + Tm(txt, size, color, bold, extra) + '</Positioned>'
def row(x, y, w, children, main="SPACE_BETWEEN", cross="CENTER"):
    return f'<Positioned left="{x}" top="{y}" width="{w}"><Row mainAxisAlignment="{main}" crossAxisAlignment="{cross}">' + "".join(children) + '</Row></Positioned>'
def col(x, y, w, children):
    return f'<Positioned left="{x}" top="{y}" width="{w}"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + "".join(children) + '</Column></Positioned>'
def r(x, y, w, h, color, rad=0, border=None):
    b = f' border="{border}"' if border else ""
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{color}" borderRadius="{rad}"{b}/></Positioned>'
def card(x, y, w, h, color=CARD, rad=16, border="1 SOLID #D8CFC0"):
    return r(x, y, w, h, color, rad, border)
def line(x, y, w, color=LINE, h=1):
    return r(x, y, w, h, color)
def circle(x, y, d, color):
    return f'<Positioned left="{x}" top="{y}" width="{d}" height="{d}"><ClipOval><Container width="{d}" height="{d}" color="{color}"/></ClipOval></Positioned>'
def avatar(x, y, d, initial, bg=LEAF, fg="#FFFFFF"):
    return (f'<Positioned left="{x}" top="{y}" width="{d}" height="{d}"><ClipOval><Container width="{d}" height="{d}" color="{bg}" alignment="CENTER">'
            + T(initial, 13, fg, True) + '</Container></ClipOval></Positioned>')
def status(dark=False, time="18:42"):
    c = "#FFFFFF" if dark else INK
    b = []
    b.append(tm(20, 16, time, 11, c, True))
    for i in range(3):
        b.append(r(320 + i * 5, 26 - i * 3, 3, 3 + i * 3, c, 1))
    b.append(r(340, 20, 22, 11, "transparent", 3, f'1 SOLID {c}'))
    b.append(r(342, 22, 15, 7, c, 2))
    b.append(r(363, 24, 2, 4, c, 1))
    return "".join(b)
def homebar(dark=False):
    c = "#FFFFFF66" if dark else "#1B1A1755"
    return r(145, 832, 100, 4, c, 2)
def check(x, y, on=True, color=LEAF, d=20):
    if on:
        return (f'<Positioned left="{x}" top="{y}" width="{d}" height="{d}"><ClipOval><Container width="{d}" height="{d}" color="{color}" alignment="CENTER">'
                + f'<Container width="7" height="7" color="#FFFFFF" borderRadius="4"/>' + '</Container></ClipOval></Positioned>')
    return f'<Positioned left="{x}" top="{y}" width="{d}" height="{d}"><Container width="{d}" height="{d}" color="transparent" borderRadius="{d//2}" border="1.5 SOLID #B9B1A3"/></Positioned>'

def band(x, y, left, life, color=LEAF, cw=10, ch=18, gap=3, outline=None):
    W = 7 * cw + 6 * gap
    filled = 0 if (left is None or life in (None, 0)) else max(0, min(7, round(left / life * 7)))
    cells = [f'<Positioned left="0" top="0" width="{W}" height="{ch}"><Container width="{W}" height="{ch}" color="transparent"/></Positioned>']
    urgent = left is not None and left <= 0
    for i in range(7):
        xx = i * (cw + gap)
        if i < filled:
            cells.append(f'<Positioned left="{xx}" top="0" width="{cw}" height="{ch}"><Container width="{cw}" height="{ch}" color="{color}" borderRadius="1"/></Positioned>')
        elif urgent:
            cells.append(f'<Positioned left="{xx}" top="0" width="{cw}" height="{ch}"><Container width="{cw}" height="{ch}" color="#FFFDF8" borderRadius="1" border="0.8 SOLID #C4472E"/></Positioned>')
        else:
            cells.append(f'<Positioned left="{xx}" top="0" width="{cw}" height="{ch}"><Container width="{cw}" height="{ch}" color="transparent" borderRadius="1" border="0.8 SOLID #CFC6B7"/></Positioned>')
    if urgent:
        cells.append(f'<Positioned left="0" top="{ch+2}" width="{W}" height="2"><Container width="{W}" height="2" color="{TOMATO}" borderRadius="1"/></Positioned>')
    return f'<Positioned left="{x}" top="{y}"><Stack alignment="TOP_LEFT">' + "".join(cells) + '</Stack></Positioned>'

def chevron(x, y, color=INK, s=7):
    return (f'<Positioned left="{x}" top="{y}"><Stack alignment="TOP_LEFT">'
            + f'<Positioned left="0" top="0"><Transform matrix="(0.707107,0.707107,0,0,-0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)"><Container width="{s}" height="2" color="{color}" borderRadius="1"/></Transform></Positioned>'
            + f'<Positioned left="0" top="{s}"><Transform matrix="(0.707107,-0.707107,0,0,0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)"><Container width="{s}" height="2" color="{color}" borderRadius="1"/></Transform></Positioned>'
            + '</Stack></Positioned>')

def page(w, h, bg=PAPER):
    return f'<Snapshot background="{bg}" type="png"><Container width="{w}" height="{h}"><Stack alignment="TOP_LEFT"><Container width="{w}" height="{h}" color="{bg}"/>'
def end(): return '</Stack></Container></Snapshot>'

def write(cid, w, h, body):
    d = OUT / f"case-{cid:02d}"; d.mkdir(parents=True, exist_ok=True)
    dsl = page(w, h) + "".join(body) + end()
    (d / 'final.snapshot').write_text(dsl, encoding='utf-8')
    return dsl

# ---------- 01 home ----------
def c01():
    W, H = 390, 844
    b = [status(time="18:34"), homebar()]
    b.append(t(20, 46, "余味", 24, LEAF, True))
    b.append(t(76, 56, "AFTERTASTE", 8, "#8A8477", True, ' letterSpacing="2"'))
    b.append(r(276, 48, 94, 24, SAGE, 12))
    b.append(t(286, 53, "302 室 · 3 人", 10, LEAF, True))
    b.append(t(20, 92, "周四晚上好，阿岚", 12, MUT))
    b.append(t(20, 112, "今晚，先吃掉", 30, INK, True))
    b.append(t(20, 148, "这 3 样。", 30, INK, True))
    b.append(t(20, 194, "冰箱里有 3 样今晚到期。25 分钟能做完。", 12, MUT, w=340))
    b.append(card(20, 232, 350, 300))
    b.append(t(36, 250, "今晚到期 · 冷藏", 10, TOMATO, True, ' letterSpacing="1"'))
    rows = [("菠菜", "200g", 0, 2, "今天"), ("口蘑", "半盒 150g", 0, 2, "今天"), ("鸡胸", "300g", 1, 3, "明天")]
    for i, (name, amt, left, life, tag) in enumerate(rows):
        yy = 282 + i * 58
        b.append(t(36, yy, name, 18, INK, True))
        b.append(t(96, yy + 5, amt, 11, MUT))
        b.append(band(250, yy + 1, left, life, LEAF if left > 0 else "#C9C2B4", outline=(TOMATO if left == 0 else None)))
        b.append(t(250, yy + 23, tag, 9, TOMATO if left == 0 else MUT, left == 0))
        if i < 2:
            b.append(line(36, yy + 46, 300, "#EDE6DA"))
    b.append(r(36, 468, 318, 44, LEAF, 10))
    b.append(t(36, 481, "看今晚的菜  →", 14, "#FFFFFF", True, w=318, extra=' textAlign="CENTER"'))
    b.append(t(20, 552, "冰箱里还有 4 样", 13, INK, True))
    b.append(t(306, 553, "全部 →", 10, MUT))
    small = [("番茄", "4 天", 4, 7), ("酸奶", "5 天", 5, 7), ("吐司", "过期 1 天", -1, 4)]
    for i, (name, tag, left, life) in enumerate(small):
        x = 20 + i * 119
        b.append(card(x, 578, 111, 94, CARD, 12))
        b.append(t(x + 10, 588, name, 13, INK, True))
        b.append(band(x + 10, 610, left, life, AMBER if left > 0 else "#C9C2B4", cw=7, ch=12, gap=2, outline=(TOMATO if left <= 0 else None)))
        b.append(t(x + 10, 632, tag, 9, TOMATO if left <= 0 else MUT, left <= 0))
        b.append(t(x + 10, 650, "查看 →", 9, LEAF, True))
    b.append(card(20, 690, 350, 90, SAGE, 12, None))
    b.append(t(34, 703, "本周已救回 6 件 · 待处理 3 件", 12, LEAF, True))
    b.append(r(34, 726, 322, 6, "#FFFFFF88", 3))
    b.append(r(34, 726, 215, 6, LEAF, 3))
    b.append(t(34, 740, "比上周少浪费 1 件。周日看完整账本。", 9, MUT))
    b.append(t(290, 740, "账本 →", 9, LEAF, True))
    b.append(r(0, 786, 390, 58, CARD, 0))
    b.append(line(0, 786, 390, "#E6DED1"))
    nav = [("今晚", 0), ("冰箱", 1), ("菜谱", 2), ("账本", 3)]
    for label, i in nav:
        x = 34 + i * 92
        if i == 0:
            b.append(circle(x + 8, 799, 8, LEAF))
        else:
            b.append(f'<Positioned left="{x+2}" top="799" width="14" height="14"><Container width="14" height="14" color="transparent" borderRadius="7" border="1.5 SOLID #9C9588"/></Positioned>')
        b.append(t(x - 2, 818, label, 9, LEAF if i == 0 else MUT, i == 0))
    return b

# ---------- 02 receipt capture ----------
def c02():
    W, H = 390, 844
    b = [r(0, 0, 390, 500, DARK, 0)]
    b.append(status(True, "18:30"))
    b.append(t(20, 48, "把小票放进框里", 13, "#FFFFFF", True))
    b.append(t(20, 68, "青禾生鲜 · 10/28 19:06", 9, "#FFFFFF88"))
    for x, y, w, h in [(24, 96, 26, 2), (24, 96, 2, 26), (340, 96, 26, 2), (364, 96, 2, 26),
                       (24, 420, 26, 2), (24, 398, 2, 26), (340, 420, 26, 2), (364, 398, 2, 26)]:
        b.append(r(x, y, w, h, "#FFFFFF", 1))
    # abstract receipt inside frame
    b.append('<Positioned left="55" top="135"><Transform matrix="(0.99863,0.052336,0,0,-0.052336,0.99863,0,0,0,0,1,0,0,0,0,1)" origin="(140,160)"><Stack alignment="TOP_LEFT">'
             + r(0, 0, 280, 320, "#FFFDF8", 2)
             + t(18, 18, "青禾生鲜", 10, INK, True)
             + t(18, 34, "梧桐路店 · 2026.10.28 19:06", 6, MUT)
             + line(18, 54, 244, "#CFC6B7")
             + t(18, 66, "菠菜 200g", 8, INK) + tm(210, 66, "6.80", 8, INK)
             + t(18, 86, "口蘑 150g", 8, INK) + tm(210, 86, "5.20", 8, INK)
             + t(18, 106, "鸡胸 300g", 8, INK) + tm(204, 106, "12.90", 8, INK)
             + t(18, 126, "酸奶 2杯", 8, INK) + tm(210, 126, "9.90", 8, INK)
             + t(18, 146, "番茄 3个", 8, INK) + tm(210, 146, "7.40", 8, INK)
             + t(18, 166, "米 2kg", 8, INK) + tm(204, 166, "24.90", 8, INK)
             + t(18, 186, "小葱 1把", 8, INK) + tm(210, 186, "1.30", 8, INK)
             + line(18, 210, 244, "#CFC6B7")
             + t(18, 220, "合计", 8, INK, True) + tm(198, 220, "68.40", 9, INK, True)
             + t(18, 246, "谢谢惠顾", 7, MUT)
             + r(18, 270, 120, 7, "#D8CFC0", 1) + r(18, 282, 190, 7, "#E6DED1", 1)
             + '</Stack></Transform></Positioned>')
    b.append(t(20, 452, "小票已识别", 9, "#FFFFFFCC"))
    b.append(circle(336, 442, 30, "#FFFFFF22"))
    b.append(t(345, 450, "×", 16, "#FFFFFF"))
    # sheet
    b.append(r(0, 500, 390, 344, CARD, 0))
    b.append(r(170, 512, 50, 4, "#D8CFC0", 2))
    b.append(t(20, 532, "识别到 7 行 · 共 ¥68.40", 20, INK, True))
    b.append(t(20, 562, "青禾生鲜 · 10/28 19:06 · 仅显示需确认的 3 行", 9, MUT))
    rows = [("菠菜 200g", "¥6.80", "99%", LEAF), ("口蘑 150g", "¥5.20", "97%", LEAF), ("番茄 3 个", "¥7.40", "88%", AMBER)]
    for i, (name, price, conf, cc) in enumerate(rows):
        yy = 590 + i * 46
        b.append(r(20, yy, 350, 38, "#FFFFFF", 8, "1 SOLID #EDE6DA"))
        b.append(t(32, yy + 11, name, 12, INK, True))
        b.append(tm(132, yy + 12, price, 10, MUT))
        b.append(t(220, yy + 11, conf + " 置信", 9, cc, True))
        if i == 2:
            b.append(t(292, yy + 11, "补日期 →", 9, TOMATO, True))
    b.append(t(20, 730, "番茄：未识别保质期，已按 5 天估算", 9, MUT))
    b.append(r(20, 752, 350, 44, LEAF, 10))
    b.append(t(20, 765, "确认入库 7 样  →", 13, "#FFFFFF", True, w=350, extra=' textAlign="CENTER"'))
    b.append(t(20, 806, "可随时修改；坏掉的食物不会被算成已救回。", 9, MUT, w=350, extra=' textAlign="CENTER"'))
    b.append(homebar())
    return b

# ---------- 03 item ----------
def c03():
    W, H = 390, 844
    b = [status(time="18:58"), homebar()]
    b.append(t(20, 40, "←", 22, INK))
    b.append(t(44, 46, "返回", 10, MUT))
    b.append(t(322, 44, "•••", 14, MUT))
    b.append(t(20, 70, "冷藏 · 上层", 10, LEAF, True, ' letterSpacing="1"'))
    b.append(t(20, 90, "菠菜", 36, INK, True))
    b.append(t(118, 104, "200g", 18, MUT))
    b.append(t(20, 140, "阿岚 10/28 买 · ¥6.80", 10, MUT))
    # illustration
    b.append(r(20, 168, 350, 170, SAGE, 16))
    b.append('<Positioned left="120" top="184"><Transform matrix="(0.866025,0.5,0,0,-0.5,0.866025,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)"><ClipOval><Container width="34" height="102" color="#6E9278"/></ClipOval></Transform></Positioned>')
    b.append('<Positioned left="160" top="198"><Transform matrix="(0.939693,0.342020,0,0,-0.342020,0.939693,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)"><ClipOval><Container width="38" height="110" color="#527A5F"/></ClipOval></Transform></Positioned>')
    b.append('<Positioned left="200" top="190"><Transform matrix="(0.984808,-0.173648,0,0,0.173648,0.984808,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)"><ClipOval><Container width="32" height="98" color="#82A389"/></ClipOval></Transform></Positioned>')
    b.append('<Positioned left="157" top="240"><Transform matrix="(0.939693,0.342020,0,0,-0.342020,0.939693,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)"><Container width="82" height="4" color="#3E6B4F" borderRadius="2"/></Transform></Positioned>')
    b.append(t(20, 348, "余味条", 9, MUT, True, ' letterSpacing="1"'))
    b.append(band(20, 370, 0, 2, "#C9C2B4", cw=26, ch=30, gap=6))
    b.append(t(246, 372, "今晚", 14, TOMATO, True))
    b.append(t(246, 394, "最后一天", 10, TOMATO))
    b.append(t(20, 412, "保鲜期 2 天 · 按冷藏估算，不构成食品安全保证", 9, MUT))
    b.append(card(20, 440, 350, 92))
    b.append(t(34, 454, "怎么放", 11, LEAF, True))
    b.append(t(34, 476, "厨房纸包住，装保鲜袋，冷藏。", 12, INK))
    b.append(t(34, 498, "已经洗过？擦干再放，别带水。", 10, MUT))
    b.append(t(20, 552, "闻起来发黏或发酸，就别吃。", 12, TOMATO))
    b.append(r(20, 580, 198, 46, LEAF, 10))
    b.append(t(20, 594, "看今晚菜单", 13, "#FFFFFF", True, w=198, extra=' textAlign="CENTER"'))
    b.append(r(228, 580, 68, 46, CARD, 10, "1 SOLID #D8CFC0"))
    b.append(t(228, 594, "送人", 11, INK, w=68, extra=' textAlign="CENTER"'))
    b.append(r(306, 580, 64, 46, CARD, 10, "1 SOLID #D8CFC0"))
    b.append(t(306, 594, "堆肥", 11, INK, w=64, extra=' textAlign="CENTER"'))
    b.append(line(20, 646, 350, "#E6DED1"))
    b.append(t(20, 660, "同批还有", 9, MUT, True, ' letterSpacing="1"'))
    b.append(t(20, 682, "口蘑 半盒 150g", 13, INK, True))
    b.append(band(230, 686, 0, 2, "#C9C2B4", cw=8, ch=14, gap=2))
    b.append(t(308, 686, "今晚", 9, TOMATO, True))
    b.append(t(348, 684, "→", 12, MUT))
    b.append(t(20, 716, "阿岚买的 · 和菠菜同一天", 9, MUT))
    b.append(card(20, 744, 350, 62, "#F0E9DC", 10, None))
    b.append(t(34, 756, "今晚 18:50 已被小满认领", 10, LEAF, True))
    b.append(t(34, 776, "菠菜口蘑鸡肉烩饭 · 3 人份", 11, INK))
    return b

# ---------- 04 recipe tablet ----------
def c04():
    W, H = 1200, 900
    b = [r(0, 0, 320, 900, NIGHT, 0)]
    b.append(t(28, 30, "余味", 15, "#FFFFFF", True))
    b.append(t(28, 52, "厨房模式 · 302", 9, "#A9B8AC"))
    b.append(t(28, 92, "今晚的菜", 30, "#FFFFFF", True))
    b.append(t(28, 132, "周四 18:50 · 3 人份", 10, "#A9B8AC"))
    recipes = [
        ("菠菜口蘑鸡肉烩饭", "25 分钟 · 一锅", "3/3 临期", True),
        ("番茄鸡胸汤面", "20 分钟 · 需买面", "2/3 临期", False),
        ("酸奶吐司布丁", "15 分钟 · 先检查吐司", "2/2 临期", False),
    ]
    for i, (name, meta, cov, sel) in enumerate(recipes):
        y = 164 + i * 118
        if sel:
            b.append(r(24, y, 272, 104, CARD, 12))
            b.append(t(38, y + 14, "方案 A", 9, LEAF, True, ' letterSpacing="1"'))
            b.append(t(38, y + 34, name, 15, INK, True))
            b.append(t(38, y + 58, meta, 9, MUT))
            b.append(r(38, y + 76, 82, 20, SAGE, 10))
            b.append(t(46, y + 80, cov, 8, LEAF, True))
            b.append(t(250, y + 46, "→", 14, LEAF))
        else:
            b.append(r(24, y, 272, 104, "transparent", 12, "1 SOLID #3A4239"))
            b.append(t(38, y + 34, name, 15, "#FFFFFF", True))
            b.append(t(38, y + 58, meta, 9, "#A9B8AC"))
            b.append(t(38, y + 80, cov, 8, AMBER, True))
    b.append(line(24, 548, 272, "#3A4239"))
    b.append(t(28, 566, "临期覆盖", 9, "#A9B8AC", True, ' letterSpacing="1"'))
    b.append(tm(28, 584, "3/3", 50, "#FFFFFF", True))
    b.append(t(28, 648, "菠菜 · 口蘑 · 鸡胸", 10, "#FFFFFFCC"))
    b.append(t(28, 678, "小满已认领 · 19:05 到家", 9, AMBER, True))
    b.append(t(28, 700, "阿岚 19:10 带米回来", 9, "#A9B8AC"))
    b.append(t(28, 838, "厨房平板 · 屏幕常亮", 8, "#6F7F73"))
    # main
    b.append(t(360, 48, "方案 A · 一锅到底", 10, TOMATO, True, ' letterSpacing="1"'))
    b.append(t(360, 70, "菠菜口蘑鸡肉烩饭", 36, INK, True))
    b.append(t(360, 120, "25 分钟 · 3 人份 · 需要一口深锅", 12, MUT))
    b.append(r(982, 64, 178, 28, SAGE, 14))
    b.append(t(996, 71, "小满 已认领", 9, LEAF, True))
    b.append(t(1090, 70, "✓", 10, LEAF))
    # coverage
    b.append(card(360, 158, 500, 120))
    b.append(t(376, 172, "要用掉", 9, MUT, True, ' letterSpacing="1"'))
    covs = [("菠菜", 0, 2, "今晚"), ("口蘑", 0, 2, "今晚"), ("鸡胸", 1, 3, "明天")]
    for i, (name, left, life, tag) in enumerate(covs):
        x = 376 + i * 158
        b.append(t(x, 194, name, 13, INK, True))
        b.append(band(x, 214, left, life, "#C9C2B4" if left == 0 else LEAF, cw=8, ch=13, gap=2, outline=TOMATO if left == 0 else None))
        b.append(t(x, 234, tag, 8, TOMATO if left == 0 else MUT, left == 0))
    b.append(line(376, 250, 468, "#EDE6DA"))
    b.append(t(376, 257, "全部覆盖 · 无需额外采购", 9, LEAF, True))
    # right panel
    b.append(card(880, 158, 280, 330, "#F0E9DC", 14, None))
    b.append(t(896, 172, "家里已有", 9, MUT, True, ' letterSpacing="1"'))
    need = [("米 300g", "有"), ("蒜 2 瓣", "有"), ("酸奶 1 勺", "有"), ("盐 / 黑胡椒", "有")]
    for i, (name, have) in enumerate(need):
        y = 198 + i * 40
        b.append(t(896, y, name, 12, INK))
        b.append(t(1116, y + 1, have, 8, LEAF, True))
        if i < 3:
            b.append(line(896, y + 24, 248, "#E0D6C6"))
    b.append(t(896, 372, "不用再买，橱柜里都有。", 9, LEAF, True))
    b.append(t(896, 396, "替 换", 8, MUT, True, ' letterSpacing="1"'))
    b.append(t(896, 414, "不吃菠菜 → 换成小青菜", 9, MUT))
    b.append(t(896, 432, "不吃鸡胸 → 换成北豆腐", 9, MUT))
    # steps
    b.append(t(360, 306, "做法预览 · 共 6 步", 10, MUT, True, ' letterSpacing="1"'))
    steps = [("01", "洗菠菜，口蘑切片，鸡胸切小块。"), ("02", "鸡胸用盐和黑胡椒抓匀，中火煎到边缘金黄。"), ("03", "下口蘑炒软，再加菠菜和米翻匀。")]
    for i, (num, txt) in enumerate(steps):
        y = 332 + i * 56
        b.append(tm(360, y, num, 16, TOMATO, True))
        b.append(t(396, y + 1, txt, 12, INK, w=450))
    b.append(t(360, 500, "开始后逐步显示；手机可同步为灶台模式。", 9, MUT))
    b.append(r(360, 532, 300, 50, LEAF, 10))
    b.append(t(360, 547, "开始做 · 小满", 13, "#FFFFFF", True, w=300, extra=' textAlign="CENTER"'))
    b.append(r(676, 532, 110, 50, CARD, 10, "1 SOLID #D8CFC0"))
    b.append(t(676, 547, "换一道", 11, INK, w=110, extra=' textAlign="CENTER"'))
    # why card
    b.append(card(360, 612, 800, 130, SAGE, 14, None))
    b.append(t(376, 626, "为什么是它", 9, LEAF, True, ' letterSpacing="1"'))
    why = [("3/3", "临期食材全用掉"), ("25", "分钟一锅完成"), ("0", "额外采购")]
    for i, (num, label) in enumerate(why):
        x = 376 + i * 250
        b.append(tm(x, 648, num, 30, LEAF, True))
        b.append(t(x + 70, 660, label, 10, INK))
    b.append(t(360, 784, "小贴士：菠菜最后放，颜色更绿。", 9, MUT))
    b.append(t(360, 856, "余味 · 厨房模式 / 菜谱由库存与到期日生成", 8, "#8A8477"))
    return b

# ---------- 05 handoff ----------
def c05():
    W, H = 390, 844
    b = [status(time="19:02"), homebar()]
    b.append(t(20, 50, "今晚谁做？", 28, INK, True))
    b.append(t(20, 88, "302 室 · 周四 19:02", 10, MUT))
    b.append(card(20, 116, 350, 196))
    people = [("阿哲", "加班，不回来吃", "已告知", "#9C9588", MUT),
              ("小满", "已认领 · 3 人份", "19:05 到家", LEAF, LEAF),
              ("阿岚", "买米，19:10 到家", "路上", AMBER, MUT)]
    for i, (name, state, tag, av, tc) in enumerate(people):
        y = 132 + i * 60
        b.append(avatar(34, y, 34, name[-1], av))
        b.append(t(80, y + 2, name, 14, INK, True))
        b.append(t(80, y + 22, state, 11, tc, i == 1))
        b.append(t(300, y + 8, tag, 9, tc if i == 1 else MUT, i == 1))
        if i < 2:
            b.append(line(34, y + 48, 320, "#EDE6DA"))
    b.append(card(20, 330, 350, 198))
    b.append(t(34, 344, "今晚的时间线", 9, MUT, True, ' letterSpacing="1"'))
    msgs = [("18:12", "阿哲", "今晚加班，不回来吃", MUT), ("18:50", "小满", "我来做烩饭，三人份", INK), ("18:51", "阿岚", "我买米，19:10 到家", INK)]
    for i, (time, who, txt, tc) in enumerate(msgs):
        y = 370 + i * 34
        b.append(tm(34, y, time, 8, "#9C9588"))
        b.append(t(78, y - 1, who, 9, LEAF, True))
        b.append(t(112, y - 2, txt, 12, tc, w=238))
    b.append(r(34, 474, 322, 38, SAGE, 8))
    b.append(t(44, 486, "菜单已更新：消耗菠菜、口蘑、鸡胸", 9, LEAF, True))
    b.append(card(20, 544, 350, 48, "#F6EBD9", 10, None))
    b.append(t(34, 558, "如果改点外卖：3 样食材顺延 1 天，明晚优先。", 9, "#8A5A18"))
    b.append(r(20, 608, 214, 50, LEAF, 10))
    b.append(t(20, 623, "我来洗碗", 13, "#FFFFFF", True, w=214, extra=' textAlign="CENTER"'))
    b.append(r(246, 608, 124, 50, CARD, 10, "1 SOLID #D8CFC0"))
    b.append(t(246, 623, "改点外卖", 11, INK, w=124, extra=' textAlign="CENTER"'))
    b.append(t(20, 672, "做完拍照，账本自动记一笔。", 9, MUT))
    b.append(card(20, 696, 350, 108, NIGHT, 12, None))
    b.append(t(34, 710, "今晚菜单", 8, "#A9B8AC", True, ' letterSpacing="1"'))
    b.append(t(34, 728, "菠菜口蘑鸡肉烩饭", 16, "#FFFFFF", True))
    b.append(t(34, 754, "3 人份 · 25 分钟 · 已同步冰箱门卡", 9, "#A9B8AC"))
    b.append(r(286, 722, 70, 22, TOMATO, 11))
    b.append(t(286, 727, "3 样临期", 8, "#FFFFFF", True, w=70, extra=' textAlign="CENTER"'))
    b.append(t(34, 776, "19:05 小满到家后，门卡自动翻页。", 8, "#A9B8AC"))
    return b

# ---------- 06 e-ink ----------
def c06():
    W, H = 600, 800
    b = [r(0, 0, 600, 800, "#ECEBE6", 0)]
    b.append(r(0, 0, 7, 800, TOMATO, 0))
    b.append(t(28, 26, "302 冰箱", 11, INK, True, ' letterSpacing="1"'))
    b.append(t(430, 26, "19:05 更新", 10, MUT))
    b.append(r(552, 24, 22, 11, "transparent", 3, "1.5 SOLID #1B1A17"))
    b.append(r(554, 26, 14, 7, INK, 2))
    b.append(r(577, 28, 2, 3, INK, 1))
    b.append(line(28, 58, 544, INK, 2))
    b.append(tm(28, 78, "10.29", 20, INK, True))
    b.append(t(108, 84, "周四", 12, MUT))
    b.append(t(28, 126, "今晚吃", 54, INK, True))
    items = [("菠菜", "今天", 0, 2), ("口蘑", "今天", 0, 2), ("鸡胸", "明天", 1, 3)]
    for i, (name, tag, left, life) in enumerate(items):
        y = 216 + i * 58
        b.append(t(28, y, name, 36, INK, True))
        b.append(band(392, y + 8, left, life, "#C9C2B4" if left == 0 else INK, cw=14, ch=22, gap=4, outline=TOMATO if left == 0 else None))
        b.append(t(392, y + 36, tag, 10, TOMATO if left == 0 else MUT, left == 0))
    b.append(line(28, 402, 544, INK, 1))
    b.append(t(28, 424, "小满掌勺", 26, INK, True))
    b.append(t(28, 462, "25 分钟 · 3 人份", 14, MUT))
    b.append(t(28, 508, "打开冰箱前，先看一眼。", 14, INK))
    b.append(t(28, 556, "阿哲今晚不回来吃，留一份明早。", 11, MUT))
    b.append(line(28, 600, 544, "#B9B1A3", 1))
    b.append(t(28, 622, "每 10 分钟自动刷新", 9, MUT))
    b.append(t(28, 644, "下次更新 19:15 · 低功耗模式", 9, MUT))
    b.append(r(28, 704, 10, 10, TOMATO, 0))
    b.append(t(46, 700, "余味 · 冰箱门卡", 10, INK, True))
    b.append(t(46, 720, "让快过期的先被吃掉", 9, MUT))
    b.append(t(430, 720, "电量 86%", 9, MUT))
    return b

# ---------- 07 cooking ----------
def c07():
    W, H = 844, 390
    b = [r(0, 0, 844, 390, DARK, 0)]
    b.append(t(24, 18, "灶台模式", 9, "#A9B8AC", True, ' letterSpacing="2"'))
    b.append(t(700, 18, "第 3 步 / 6", 9, "#A9B8AC"))
    b.append(t(810, 14, "×", 18, "#A9B8AC"))
    b.append(tm(24, 52, "03", 50, AMBER, True))
    b.append(t(24, 116, "鸡肉下锅", 34, "#FFFFFF", True))
    b.append(t(24, 158, "鸡胸切小块，中火煎到边缘金黄。", 20, "#FFFFFF", w=470))
    b.append(t(24, 190, "不要频繁翻动，等它自己脱锅。", 12, "#A9B8AC", w=470))
    b.append(r(540, 44, 270, 214, "transparent", 14, "1 SOLID #3A4239"))
    b.append(t(560, 58, "计时", 9, "#A9B8AC", True, ' letterSpacing="1"'))
    b.append(tm(560, 78, "04:00", 50, "#FFFFFF", True))
    b.append(r(560, 146, 230, 6, "#3A4239", 3))
    b.append(r(560, 146, 153, 6, AMBER, 3))
    b.append(t(560, 164, "中火 · 4 分钟", 10, "#A9B8AC"))
    b.append(t(560, 190, "第 3 步计时中", 9, AMBER, True))
    b.append(t(560, 214, "湿手也能点：整屏可触", 9, "#6F7F73"))
    items = [("菠菜 已洗", True), ("口蘑 已切片", True), ("鸡胸 300g", False)]
    for i, (label, on) in enumerate(items):
        x = 24 + i * 196
        b.append(r(x, 252, 184, 42, "#1F2621", 10, "1 SOLID #3A4239"))
        b.append(check(x + 12, 263, on, "#5F8B6C" if on else AMBER, 18))
        b.append(t(x + 40, 263, label, 11, "#FFFFFF" if on else AMBER, on))
    b.append(r(632, 270, 188, 52, AMBER, 10))
    b.append(t(632, 285, "下一步  →", 13, INK, True, w=188, extra=' textAlign="CENTER"'))
    b.append(t(24, 332, "屏幕常亮 · 湿手可点 · 计时结束会震动", 8, "#6F7F73"))
    b.append(t(24, 352, "小满 · 302 厨房", 8, "#6F7F73"))
    b.append(t(640, 352, "共 6 步 · 预计 21 分钟", 8, "#6F7F73"))
    return b

# ---------- 08 weekly A4 ----------
def c08():
    W, H = 1240, 1754
    b = [r(0, 0, W, H, PAPER, 0)]
    b.append(t(80, 56, "余味 · 周账本", 11, LEAF, True, ' letterSpacing="2"'))
    b.append(t(80, 78, "第 44 周 · 10.26–11.01 · 截至周日 10:20", 10, MUT))
    b.append(t(1020, 56, "302 室 · 3 人", 10, MUT))
    b.append(t(80, 124, "这周，9 件食物", 36, INK, True))
    b.append(t(80, 168, "没有进垃圾桶。", 36, INK, True))
    b.append(t(80, 224, "还有 2 件没来得及。下周只买缺的。", 13, MUT))
    kpis = [("82%", "救回率", "9 / 11 件"), ("¥54.70", "救回价值", "按购买价"), ("¥12.30", "浪费金额", "2 件")]
    for i, (v, lab, note) in enumerate(kpis):
        x = 80 + i * 365
        b.append(card(x, 272, 340, 124, CARD, 12))
        b.append(t(x + 18, 288, lab, 9, MUT, True, ' letterSpacing="1"'))
        b.append(tm(x + 18, 306, v, 32, TOMATO if i == 2 else LEAF, True))
        b.append(t(x + 18, 362, note, 9, MUT))
    # ledgers
    b.append(line(80, 436, 1080, "#D8CFC0"))
    b.append(t(80, 456, "救回 9 件 · ¥54.70", 14, LEAF, True))
    b.append(t(740, 456, "没救回 2 件 · ¥12.30", 14, TOMATO, True))
    rescued = [("菠菜", 6.80), ("口蘑", 5.20), ("鸡胸", 12.90), ("西兰花", 6.90), ("香蕉", 5.60), ("豆腐", 3.50)]
    for i, (name, price) in enumerate(rescued):
        y = 494 + i * 40
        b.append(t(80, y, name, 13, INK))
        b.append(dotted(180, y + 15, 420))
        b.append(tm(610, y, f"{price:.2f}", 12, INK))
    b.append(t(80, 740, "另 3 件：小葱 1.30 · 青椒 3.20 · 牛奶 9.30", 9, MUT))
    b.append(t(740, 494, "吐司 4 片", 13, INK))
    b.append(tm(1040, 494, "8.50", 12, INK))
    b.append(t(740, 516, "原因：放在面包盒里忘了", 9, MUT))
    b.append(t(740, 544, "酸奶 1 杯", 13, INK))
    b.append(tm(1040, 544, "3.80", 12, INK))
    b.append(t(740, 566, "原因：开封后没喝完", 9, MUT))
    b.append(card(740, 602, 420, 92, "#F6EBD9", 10, None))
    b.append(t(756, 616, "浪费集中在周末前的叶菜与开封乳品。", 10, "#8A5A18", w=390))
    b.append(t(756, 646, "下周把“清冰箱”放到周三。", 10, "#8A5A18", True))
    b.append(t(740, 716, "重量估算：救回 2.1kg / 浪费 1.1kg", 9, MUT))
    b.append(t(740, 736, "CO₂e 估算：少排 5.3kg / 仍发生 2.8kg", 9, MUT))
    # week strip
    b.append(line(80, 800, 1080, "#E6DED1"))
    b.append(t(80, 816, "这一周", 9, MUT, True, ' letterSpacing="1"'))
    days = [("周一", "10.26", "牛奶"), ("周二", "10.27", "烩饭"), ("周三", "10.28", "豆腐"), ("周四", "10.29", "烩饭"), ("周五", "10.30", "香蕉"), ("周六", "10.31", "吐司浪费"), ("周日", "11.01", "账本")]
    b.append(line(80, 888, 1080, "#D8CFC0", 1))
    for i, (d, date, event) in enumerate(days):
        x = 80 + i * 154
        b.append(t(x, 844, d, 9, MUT, True))
        b.append(t(x, 862, date, 8, MUT))
        b.append(circle(x + 2, 884, 8, TOMATO if i == 5 else LEAF))
        b.append(t(x, 906, event, 9, TOMATO if i == 5 else INK, i == 5))
    # next actions
    b.append(t(80, 986, "下周动作", 11, LEAF, True, ' letterSpacing="1"'))
    acts = [("只买 5 样", "菠菜、西兰花、鸡胸、鸡蛋、酸奶；其余先清库存。"), ("周三清冰箱", "把叶菜与开封乳品排到最前。"), ("酸奶买 2 杯", "不再按促销囤 4 杯。")]
    for i, (head, body) in enumerate(acts):
        x = 80 + i * 365
        b.append(card(x, 1012, 340, 118, CARD, 12))
        b.append(t(x + 18, 1028, head, 15, INK, True))
        b.append(t(x + 18, 1056, body, 9, MUT, w=300))
        b.append(t(x + 18, 1102, "→", 11, LEAF))
    # summary quote
    b.append(card(80, 1170, 1080, 120, SAGE, 12, None))
    b.append(t(104, 1192, "“不是少买，是让已经买回来的先被看见。”", 16, LEAF, True))
    b.append(t(104, 1224, "账本不评价人，只记录库存发生了什么。", 10, MUT))
    # month context
    b.append(line(80, 1318, 1080, "#D8CFC0"))
    b.append(t(80, 1338, "本月至今 · 10.01–10.31", 11, LEAF, True, ' letterSpacing="1"'))
    b.append(t(80, 1362, "31 件救回 · ¥186.40 · 5 件浪费 ¥28.60", 10, MUT))
    weeks = [("第 1 周", "10.01–10.11", 6), ("第 2 周", "10.12–10.18", 8), ("第 3 周", "10.19–10.25", 8), ("第 4 周 · 本周", "10.26–11.01", 9)]
    for i, (lab, rng, n) in enumerate(weeks):
        x = 80 + i * 270
        b.append(t(x, 1398, lab, 9, MUT, True))
        b.append(t(x, 1416, rng, 8, MUT))
        b.append(r(x, 1440, 180, 60, "#EDE6DA", 4))
        hh = round(60 * n / 10)
        b.append(r(x, 1500 - hh, 180, hh, LEAF if i < 3 else AMBER, 4))
        b.append(tm(x, 1508, f"{n} 件", 9, INK, True))
    b.append(t(80, 1538, "四周合计 31 件 · 与本月底部小票口径一致。", 9, MUT))
    # method
    b.append(t(80, 1580, "口径", 9, MUT, True, ' letterSpacing="1"'))
    b.append(t(80, 1600, "金额按购买价计；重量按品类平均估值；CO₂e 按 2.5kg CO₂e / kg 食物估算。", 9, MUT, w=1000))
    b.append(t(80, 1622, "保质期为平台估算，不构成食品安全保证；食用前请自行检查。", 9, MUT, w=1000))
    b.append(t(80, 1640, "余味 AFTERTASTE · 302 室 · 2026.11.01", 8, "#8A8477"))
    b.append(t(1040, 1640, "01 / 01", 8, "#8A8477"))
    return b

# ---------- 09 grocery ----------
def c09():
    W, H = 390, 844
    b = [status(time="11:01"), homebar()]
    b.append(t(20, 50, "下周采购", 28, INK, True))
    b.append(t(20, 88, "周日 11.01 · 为 11.02–11.08 生成", 10, MUT))
    b.append(card(20, 112, 350, 96))
    b.append(t(34, 126, "预算 ¥90", 9, MUT, True, ' letterSpacing="1"'))
    b.append(tm(34, 144, "¥46.40", 24, LEAF, True))
    b.append(t(140, 152, "已选 / 预计", 9, MUT))
    b.append(r(34, 182, 322, 6, "#EDE6DA", 3))
    b.append(r(34, 182, 166, 6, LEAF, 3))
    b.append(t(264, 126, "只买缺的", 9, MUT, True))
    b.append(r(318, 124, 36, 18, LEAF, 9))
    b.append(circle(338, 127, 12, "#FFFFFF"))
    groups = [("蔬菜", [("菠菜 200g", 6.80, "周二烩饭", "buy"), ("西兰花 1 颗", 6.90, "周三烤蔬菜", "buy"), ("番茄 3 个", 7.40, "家里还有 2 个", "skip")]),
              ("蛋白", [("鸡胸 300g", 12.90, "周二烩饭", "buy"), ("鸡蛋 6 枚", 9.90, "早餐", "buy")]),
              ("乳品", [("酸奶 2 杯", 9.90, "家里还有 2 杯，只补 2 杯", "buy")])]
    y = 224
    for gi, (group, rows) in enumerate(groups):
        b.append(t(20, y, group, 9, MUT, True, ' letterSpacing="2"'))
        y += 22
        for name, price, why, state in rows:
            b.append(line(20, y, 350, "#EDE6DA"))
            if state == "buy":
                b.append(check(24, y + 14, True, LEAF, 20))
                b.append(t(56, y + 8, name, 13, INK, True))
                b.append(t(56, y + 28, why, 9, MUT, w=220))
                b.append(tm(296, y + 10, f"{price:.2f}", 11, INK))
                b.append(t(336, y + 30, "买", 8, LEAF, True))
            else:
                b.append(f'<Positioned left="24" top="{y+14}" width="20" height="20"><Container width="20" height="20" color="transparent" borderRadius="10" border="1.5 SOLID #CFC6B7"/></Positioned>')
                b.append(t(56, y + 8, name, 13, "#A39B8D", True))
                b.append(t(56, y + 28, why, 9, "#A39B8D", w=220))
                b.append(t(296, y + 10, "不买", 9, "#A39B8D", True))
            y += 54
        y += 10
    b.append(card(20, 642, 350, 90, SAGE, 12, None))
    b.append(t(34, 654, "已自动去掉 3 样", 10, LEAF, True))
    b.append(t(34, 674, "番茄 3 个 · 牛奶 1L · 米 2kg", 9, MUT))
    b.append(t(34, 694, "因为家里还有，或上周还没吃完。", 9, MUT))
    b.append(r(20, 746, 350, 44, LEAF, 10))
    b.append(t(20, 759, "加入购物袋 · ¥46.40", 13, "#FFFFFF", True, w=350, extra=' textAlign="CENTER"'))
    b.append(t(20, 802, "分享给阿哲 →", 10, LEAF, True, w=350, extra=' textAlign="CENTER"'))
    return b

def dotted(x, y, w, color="#C9C0B0"):
    out = []
    step = 8
    n = int(w // step)
    for i in range(n):
        out.append(r(x + i * step, y, 4, 2, color, 1))
    return "".join(out)

# ---------- 10 receipt ----------
def c10():
    W, H = 720, 1280
    b = [r(0, 0, W, H, NIGHT, 0)]
    b.append(r(48, 64, 624, 1150, "#FFFDF8", 2))
    # perforation
    for i in range(21):
        b.append(circle(54 + i * 30, 58, 14, NIGHT))
        b.append(circle(54 + i * 30, 1206, 14, NIGHT))
    b.append(t(90, 92, "余味  AFTERTASTE", 9, LEAF, True, ' letterSpacing="3"'))
    b.append(t(90, 116, "十月浪费小票", 30, INK, True))
    b.append(t(90, 158, "2026.10.01–10.31 · 302 室 · 3 人", 9, MUT))
    b.append(dotted(90, 190, 540))
    b.append(t(90, 206, "没救回 / 5 件", 11, TOMATO, True, ' letterSpacing="1"'))
    wasted = [("吐司 4 片", "8.50"), ("酸奶 1 杯", "3.80"), ("草莓 半盒", "12.90"), ("香菜 1 把", "1.60"), ("豆芽 1 袋", "1.80")]
    for i, (name, price) in enumerate(wasted):
        y = 234 + i * 34
        b.append(t(90, y, name, 13, INK))
        b.append(dotted(230, y + 13, 280))
        b.append(tm(530, y, price, 12, INK))
    b.append(line(90, 412, 540, "#E6DED1"))
    b.append(t(90, 424, "小计", 10, MUT))
    b.append(tm(470, 420, "¥28.60", 16, TOMATO, True))
    b.append(dotted(90, 456, 540))
    b.append(t(90, 472, "救回 / 31 件", 11, LEAF, True, ' letterSpacing="1"'))
    b.append(tm(90, 492, "¥186.40", 38, LEAF, True))
    b.append(t(90, 544, "8.6kg 食物 · 少排 21.6kg CO₂e（估算）", 9, MUT))
    # bars
    b.append(t(90, 584, "救回", 8, MUT))
    b.append(r(140, 584, 330, 12, LEAF, 6))
    b.append(t(90, 610, "浪费", 8, MUT))
    b.append(r(140, 610, 50, 12, TOMATO, 6))
    b.append(t(200, 610, "¥28.60", 8, MUT))
    b.append(t(90, 648, "浪费不是道德问题，", 16, INK, True))
    b.append(t(90, 674, "是库存问题。", 16, INK, True))
    b.append(t(90, 708, "下周只买缺的。", 10, LEAF, True))
    b.append(band(90, 736, 6, 7, LEAF, cw=16, ch=22, gap=4))
    b.append(t(248, 742, "十月最后一周：救回率 82%", 9, MUT))
    b.append(dotted(90, 790, 540))
    b.append(t(90, 804, "31 件里，有 9 件发生在最后一周。", 9, INK))
    b.append(t(90, 824, "没有记录的，不算救回。", 9, MUT))
    # barcode
    widths = [2, 4, 2, 6, 2, 3, 5, 2, 4, 2, 6, 3, 2, 5, 2, 4, 3, 2, 6, 2, 4, 3, 5, 2, 3, 4, 2, 6, 2, 3]
    x = 90
    for i, w in enumerate(widths):
        b.append(r(x, 884, w, 64, INK, 0))
        x += w + 5
    b.append(tm(90, 956, "DEMO-302-1026", 8, MUT))
    b.append(t(90, 976, "演示条码，不可扫描", 8, "#A39B8D"))
    b.append(dotted(90, 1010, 540))
    b.append(t(90, 1026, "打印于 10.31 21:10", 9, MUT))
    b.append(t(90, 1046, "贴在冰箱上，月底再看一次。", 9, INK))
    b.append(t(90, 1090, "余味 AFTERTASTE", 8, LEAF, True, ' letterSpacing="2"'))
    b.append(t(90, 1108, "让快过期的，先被吃掉。", 9, MUT))
    b.append(t(510, 1090, "10 / 10", 8, "#A39B8D"))
    return b

CASES = [(1, 390, 844, c01), (2, 390, 844, c02), (3, 390, 844, c03), (4, 1200, 900, c04),
         (5, 390, 844, c05), (6, 600, 800, c06), (7, 844, 390, c07), (8, 1240, 1754, c08),
         (9, 390, 844, c09), (10, 720, 1280, c10)]
for cid, w, h, fn in CASES:
    write(cid, w, h, fn())
print('B05 wrote', len(CASES), 'screens')
