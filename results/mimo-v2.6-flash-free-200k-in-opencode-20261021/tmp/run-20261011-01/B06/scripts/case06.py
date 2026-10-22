# -*- coding: utf-8 -*-
"""B06 case-06 · 70% 不是 70% 的时间 — 降水概率解读

Problem: 看到「降水概率 70%」就把它读成"会下 70% 的时间 / 雨有 70% 大 /
70% 的地方下雨"，于是带不带伞全凭错的直觉。
Redesign: 先给逐字定义（SRC-01），再用 100 格阵列把概率画成"格数"，
最后把三类常见误读与原文口径逐条对照。

真实锚点: SRC-01 维基百科「降水概率」条目 (CC BY-SA 4.0)，
定义与"与降水时间、降雨量、降雨面积无关"逐字引自该条目。
数据边界: 天气数值 70% 为自拟演示数据。
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, emit, seg, text, tw_slot

W, H = 780, 1688
BG = "#E9F1F9"
PANEL = "#FFFFFF"
BORD = "#CBDCEA"
INK = "#123247"
MUT = "#5A7789"
FAINT = "#8AA2B2"
BLUE = "#2F80C0"
DEEP = "#1B5E8F"
RED = "#C7442E"
GREEN = "#2E8B57"
FILLED = "#2F80C0"
EMPTY = "#F4F8FC"
L = 46
CW = W - 2 * L
CML, CMR = L + 24, L + CW - 24          # 70 .. 710
INNER = CMR - CML                        # 640

POP = 70                                 # 演示天气页显示的降水概率

# ---------------- real anchor: SRC-01 ---------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "research", "SRC-01-precipitation-probability.txt")
src = io.open(SRC, encoding="utf-8").read()

QUOTE = "預報區域在36小時內，出現0.01mm或以上降水的機率。"
EXCLUDE_SENT = "和降水時間、降雨量、降雨面積無關"

MISREADS = [
    "「70% 的时间在下雨」",
    "「雨量有 70% 那么大」",
    "「70% 的地方在下雨」",
]
FIXES = [
    "与降水时间无关：定义只说 36 小时内是否出现降水",
    "与降雨量无关：门槛只是 0.01mm 或以上是否达到",
    "与降雨面积无关：说的是预报区域出现降水的机率",
]

# ---------------- C1 · definition verbatim from SRC-01 ----------------------
assert QUOTE in src, "定义不是 SRC-01 原文"
assert EXCLUDE_SENT in src, "排除句不是 SRC-01 原文"
for elem in ("預報區域", "36小時內", "0.01mm或以上"):
    assert elem in QUOTE, "C1 定义缺要素: %s" % elem
assert "CC BY-SA 4.0" in src, "授权信息缺失"

# ---------------- C3 · the three misreadings are exactly the three excluded --
for trad, simp in (("降水時間", "与降水时间无关"),
                   ("降雨量", "与降雨量无关"),
                   ("降雨面積", "与降雨面积无关")):
    assert trad in src, "SRC-01 未提及 %s" % trad
    assert any(simp in f for f in FIXES), "C3 未纠正 %s" % simp
assert len(FIXES) == len(MISREADS) == 3

# ---------------- C2 · the 100-cell array -----------------------------------
CELL, GAP = 46, 8
GRID_N = 10
assert GRID_N * GRID_N == 100
assert 0 <= POP <= 100
FILLED_CELLS = POP                       # 着色格数 == 概率数值
CELLS = [(c, r, (r * GRID_N + c) < FILLED_CELLS)
         for r in range(GRID_N) for c in range(GRID_N)]
assert len(CELLS) == 100
assert sum(1 for _c, _r, f in CELLS if f) == POP
# row-major so the count is legible: exactly the first POP//10 rows are full
assert all(not f for c, r, f in CELLS if r >= POP // 10 and (r * 10 + c) >= POP)

# ---------------- C4 · content audit: never convert PoP to time or amount ----
TEXTS = []                               # every string that reaches the canvas


def T(x, y, w, h, s, size, color, *a, **k):
    TEXTS.append(s)
    return text(x, y, w, h, s, size, color, *a, **k)


B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(box(CML, 44, 196, 36, BLUE, radius=18))
B.append(T(CML, 51, 196, 30, "出门前 · 天气解读", 18, "#FFFFFF", align="CENTER"))
B.append(T(CML, 92, 640, 66, "「%d%% 不是 %d%% 的时间」" % (POP, POP), 44, INK,
           bold=True))
B.append(T(CML, 162, 640, 36, "降水概率的正确读法 · 天气数值为演示数据", 21, MUT))

# ---------------- P1 definition --------------------------------------------
PY1, PH1 = 212, 216
B.append(box(L, PY1, CW, PH1, PANEL, radius=18, border=BORD, border_w=2))
B.append(box(L, PY1, 6, PH1, BLUE, radius=3))
B.append(T(CML, PY1 + 16, 640, 34, "定义：三个要素缺一不可（原文照录）", 24, INK,
           bold=True))
B.append(T(CML, PY1 + 56, 640, 34, "「%s」" % QUOTE, 19, BLUE))
CHIPS = [("01 · 对象", "预报区域"), ("02 · 时间", "36 小时内"),
         ("03 · 门槛", "0.01mm 或以上")]
CHIPW = (INNER - 24) // 3               # 205
for i, (lab, val) in enumerate(CHIPS):
    cx = CML + i * (CHIPW + 12)
    assert tw_slot(val, 20) <= CHIPW - 28, "chip 过宽: %s" % val
    B.append(box(cx, PY1 + 100, CHIPW, 88, "#F0F6FB", radius=12, border=BLUE,
                 border_w=2))
    B.append(T(cx + 14, PY1 + 114, CHIPW - 28, 24, lab, 15, MUT, font="Inter"))
    B.append(T(cx + 14, PY1 + 144, CHIPW - 28, 32, val, 20, DEEP, bold=True))

# ---------------- P2 the 100-cell array ------------------------------------
PY2, PH2 = 444, 698
B.append(box(L, PY2, CW, PH2, PANEL, radius=18, border=BORD, border_w=2))
B.append(box(L, PY2, 6, PH2, BLUE, radius=3))
B.append(T(CML, PY2 + 16, 640, 34, "把 %d%% 画成 100 格" % POP, 24, INK, bold=True))
B.append(T(CML, PY2 + 54, 640, 30, "着色格数 = 概率数值，不是时长也不是雨量", 19, MUT))
GSPAN = GRID_N * CELL + (GRID_N - 1) * GAP          # 532
GX0 = CML + (INNER - GSPAN) // 2                     # 124
GY0 = PY2 + 102                                      # 546
for c, r, f in CELLS:
    x = GX0 + c * (CELL + GAP)
    y = GY0 + r * (CELL + GAP)
    B.append(box(x, y, CELL, CELL, FILLED if f else EMPTY, radius=6,
                 border=BORD, border_w=2))
assert GY0 + GSPAN == 1078
B.append(T(CML, PY2 + 650, 640, 34,
           "%d / 100 格着色 = 降水概率 %d%%" % (POP, POP), 24, DEEP, bold=True,
           align="CENTER"))
assert PY2 + 650 + 34 <= PY2 + PH2, "P2 越界"

# ---------------- P3 three misreadings -------------------------------------
PY3, PH3 = 1158, 344
B.append(box(L, PY3, CW, PH3, PANEL, radius=18, border=BORD, border_w=2))
B.append(box(L, PY3, 6, PH3, RED, radius=3))
B.append(T(CML, PY3 + 14, 640, 34, "三种常见误读，逐条对照", 24, INK, bold=True))
for i, (bad, good) in enumerate(zip(MISREADS, FIXES)):
    ry = PY3 + 56 + i * 94
    assert tw_slot(bad, 19) <= 560, "误读行过宽"
    assert tw_slot(good, 17) <= 560, "纠正行过宽: %s" % good
    B.append(box(CML, ry + 4, 66, 30, RED, radius=8))
    B.append(T(CML, ry + 9, 66, 26, "误读", 17, "#FFFFFF", align="CENTER"))
    B.append(T(148, ry + 4, 560, 30, bad, 19, RED))
    B.append(box(CML, ry + 44, 66, 30, GREEN, radius=8))
    B.append(T(CML, ry + 49, 66, 26, "纠正", 17, "#FFFFFF", align="CENTER"))
    B.append(T(148, ry + 44, 560, 34, good, 17, INK))
assert PY3 + 56 + 2 * 94 + 86 <= PY3 + PH3, "P3 越界"

# ---------------- P4 sources / boundaries ----------------------------------
PY4, PH4 = 1518, 148
B.append(box(L, PY4, CW, PH4, "#F2F8FC", radius=18, border=BORD, border_w=2))
B.append(T(CML, PY4 + 14, 640, 30, "出处与边界", 21, DEEP, bold=True))
FOOT = [
    "· 定义逐字引自 SRC-01（维基百科·降水概率，CC BY-SA 4.0）",
    "· 天气数值为演示数据；不把概率换算成时长或雨量",
    "· 出行请以当地气象部门最新预报为准",
]
for k, n in enumerate(FOOT):
    assert tw_slot(n, 17) <= INNER, "footer too wide: %s" % n
    B.append(T(CML, PY4 + 52 + k * 30, 640, 30, n, 17, MUT))

end = PY4 + PH4
assert end <= H, "内容超出画布: %d > %d" % (end, H)

# ---------------- C4 · audit every string that reaches the canvas -----------
misread_hits = [t for t in TEXTS if t in MISREADS]
assert len(misread_hits) == 3, "误读句缺失或重复: %s" % misread_hits
assert sum(1 for t in TEXTS if t in FIXES) == 3, "纠正句缺失"
FORBIDDEN = ["会下多久", "会下多长", "持续时间", "雨量达", "雨量为",
             "面积达", "下雨了", "的時間", "時間占"]
for t in TEXTS:
    for bad in FORBIDDEN:
        assert bad not in t, "C4 出现时长/雨量换算: %r in %r" % (bad, t)
# any line that pairs a percentage with time/amount/area must be an explicit
# misreading or an explicit negation
for t in TEXTS:
    if "%" not in t:
        continue
    pairs = any(k in t for k in ("时间", "雨量", "地方"))
    if not pairs:
        continue
    assert t in MISREADS or "不是" in t, "C4 疑似换算: %r" % t
_NEG = ("不是", "不把", "不等于", "无关", "不代表")
assert not any("概率" in t and "时长" in t
               and not any(n in t for n in _NEG) for t in TEXTS)
assert not any("概率" in t and "雨量" in t
               and not any(n in t for n in _NEG) for t in TEXTS)

print("SRC-01 引文核对通过；100 格中着色 %d 格；三类误读/纠正齐备"
      % sum(1 for _c, _r, f in CELLS if f))
print("layout ends at %d / %d  (%d px spare)" % (end, H, H - end))
print("C4 内容审查通过：%d 条渲染文本无时长/雨量/面积换算" % len(TEXTS))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(HERE, "..", "drafts", "case-06-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-06 %s written" % VER)
