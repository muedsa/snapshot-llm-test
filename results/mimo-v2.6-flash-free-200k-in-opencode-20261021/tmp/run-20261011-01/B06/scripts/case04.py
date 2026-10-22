# -*- coding: utf-8 -*-
"""B06 case-04 · 箭头之外 — 检验报告的参考区间定位 (A4 1240x1754)

Problem: 化验单上只有 ↑↓，患者不知道偏离了多少、更不知道箭头≠诊断。
Redesign: 每一项画成一条"参考区间定位带"——带=参考区间，竖线=结果，
位置按数值等比落点（区间外也照常延伸），带外的彩色段长度=超出量。
于是"偏多少"变成可以量的长度，而不是一个箭头。

数据边界: 项目名与参考区间为常见检验项目的通用表述，数值均为自拟演示数据。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, emit, seg, text, tw_slot

W, H = 1240, 1754
BG = "#F7F6F1"          # paper
INK = "#1B2420"
MUT = "#5F6B64"
FAINT = "#8A948D"
CARD = "#FFFFFF"
BORD = "#DCD8CC"
TRACK = "#E6E3DA"
BAND = "#2F8F6B"
MARK = "#1B2420"
OKC = "#15803D"
LOWC = "#2563EB"
HIGHC = "#C2410C"
M = 70
INNER = W - 2 * M                       # 1100

# ---------------- demo lab data --------------------------------------------
# unit is stored ONCE and reused by every string that mentions a value (C4)
ITEMS = [
    {"cn": "血红蛋白",   "ab": "HGB",   "unit": "g/L",     "lo": 130.0, "hi": 175.0, "res": 118.0, "dp": 0},
    {"cn": "空腹血糖",   "ab": "GLU",   "unit": "mmol/L",  "lo": 3.9,   "hi": 6.1,   "res": 5.8,   "dp": 1},
    {"cn": "总胆固醇",   "ab": "TC",    "unit": "mmol/L",  "lo": 2.8,   "hi": 5.7,   "res": 5.9,   "dp": 1},
    {"cn": "谷丙转氨酶", "ab": "ALT",   "unit": "U/L",     "lo": 9.0,   "hi": 50.0,  "res": 46.0,  "dp": 0},
    {"cn": "尿酸",       "ab": "UA",    "unit": "μmol/L",  "lo": 208.0, "hi": 428.0, "res": 486.0, "dp": 0},
    {"cn": "血钾",       "ab": "K",     "unit": "mmol/L",  "lo": 3.5,   "hi": 5.3,   "res": 3.3,   "dp": 1},
    {"cn": "糖化血红蛋白", "ab": "HbA1c", "unit": "%",      "lo": 4.0,   "hi": 6.0,   "res": 5.6,   "dp": 1},
]

AXIS_PAD = 0.5        # band occupies the middle third of the axis on average


def fmt(v, dp):
    return ("%.*f" % (dp, v)) if dp else "%d" % int(round(v))


def setup(it):
    """axis (C2): every marker x is a linear map of its value."""
    lo, hi, res = it["lo"], it["hi"], it["res"]
    assert lo < hi, "参考区间上下限颠倒"
    span = hi - lo
    amin = max(0.0, lo - AXIS_PAD * span)
    amax = hi + AXIS_PAD * span
    assert amin <= res <= amax, "结果落在定位轴外"
    pos = lambda v: (v - amin) / (amax - amin)
    it.update(amin=amin, amax=amax, pos=pos,
              p_lo=pos(lo), p_hi=pos(hi), p_res=pos(res))
    it["status"] = "low" if res < lo else ("high" if res > hi else "ok")
    if it["status"] == "low":
        it["dev"] = round(lo - res, 6)
    elif it["status"] == "high":
        it["dev"] = round(res - hi, 6)
    else:
        it["dev"] = 0.0
    return it


for _it in ITEMS:
    setup(_it)

# ---------------- C1 / C2 / C3 / C4 assertions ------------------------------
for it in ITEMS:
    # C1 four elements: 项目名 / 结果 / 单位 / 参考区间
    assert it["cn"] and it["ab"] and it["unit"], "C1 缺项目要素"
    assert it["lo"] is not None and it["hi"] is not None and it["res"] is not None
    assert it["unit"], "C1 缺单位"

    # C2 marker position is proportional to value: the marker's offset from
    # the lower bound, measured as a fraction of the band, must equal the
    # value's offset from the lower bound, measured as a fraction of the span.
    span = it["hi"] - it["lo"]
    span_frac = (it["p_res"] - it["p_lo"]) / (it["p_hi"] - it["p_lo"])
    val_frac = (it["res"] - it["lo"]) / span
    assert abs(span_frac - val_frac) < 1e-12, "落点与数值不成正比"
    assert abs((it["p_hi"] - it["p_lo"]) - span / (it["amax"] - it["amin"])) < 1e-12
    assert it["amin"] < it["lo"] < it["hi"] < it["amax"]
    assert 0.0 <= it["p_res"] <= 1.0
    # a value beyond the band must land beyond the band (not be clamped into it)
    if it["status"] == "high":
        assert it["p_res"] > it["p_hi"], "偏高项未落在带外"
    elif it["status"] == "low":
        assert it["p_res"] < it["p_lo"], "偏低项未落在带外"
    else:
        assert it["p_lo"] <= it["p_res"] <= it["p_hi"], "正常项落点越界"

    # C3 deviation is stated against the nearest boundary, with unit
    if it["status"] != "ok":
        assert it["dev"] > 0, "异常项缺偏离幅度"
    else:
        assert it["dev"] == 0

    # C4 one unit string everywhere it appears
    rs = "%s %s" % (fmt(it["res"], it["dp"]), it["unit"])
    ref = "%s-%s %s" % (fmt(it["lo"], it["dp"]), fmt(it["hi"], it["dp"]), it["unit"])
    assert it["unit"] in rs and it["unit"] in ref, "C4 结果与参考区间单位不一致"
    if it["status"] != "ok":
        ds = "%s %s" % (fmt(it["dev"], it["dp"]), it["unit"])
        assert it["unit"] in ds, "C4 偏离幅度单位不一致"
        it["dev_str"] = ds
    it["res_str"] = rs
    it["ref_str"] = "参考 " + ref

assert len(ITEMS) == 7
assert sum(1 for i in ITEMS if i["status"] != "ok") == 4
assert sum(1 for i in ITEMS if i["status"] == "ok") == 3

B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(seg(M, 62, W - M, 62, 5, INK))
B.append(text(M, 92, 620, 66, "检验报告单", 50, INK, bold=True))
B.append(text(M, 164, 760, 42, "箭头之外 · 参考区间定位", 27, MUT))

B.append(box(W - M - 230, 84, 230, 78, "#FDF1EE", radius=10,
             border=HIGHC, border_w=3))
B.append(text(W - M - 230, 94, 230, 36, "演示数据", 27, HIGHC, bold=True,
              align="CENTER"))
B.append(text(W - M - 230, 132, 230, 28, "非真实报告", 19, HIGHC, align="CENTER"))

info = "姓名 演示样本 · 标本 静脉血 · 采集 2026-10-21 · 报告 演示医学检验所"
B.append(box(M, 220, INNER, 66, CARD, radius=10, border=BORD, border_w=2))
B.append(text(M + 24, 236, INNER - 48, 34, info, 21, INK))

# ---------------- legend ----------------------------------------------------
LGY, LGH = 306, 92
B.append(box(M, LGY, INNER, LGH, "#EDF6F1", radius=12, border=BAND, border_w=2))
lx, lw = M + 24, 180
B.append(box(lx, 340, lw, 22, TRACK, radius=11))
B.append(box(lx + 0.15 * lw, 340, 0.65 * lw, 22, BAND, radius=11))
B.append(box(lx + 0.86 * lw - 3, 330, 6, 42, MARK, radius=3))
B.append(text(300, 316, 872, 34, "带 = 参考区间（报告印制的正常范围） · 竖线 = 你的结果位置",
              21, INK))
B.append(text(300, 352, 872, 34,
              "带外彩色段 = 超出幅度，长度与超出量成正比；↑ ↓ = 偏高或偏低",
              20, MUT))

# ---------------- column header --------------------------------------------
HY = 414
B.append(text(M + 24, HY, 240, 30, "项目", 20, FAINT))
B.append(text(352, HY, 340, 30, "参考区间定位带", 20, FAINT))
B.append(text(850, HY, 296, 30, "结果 · 参考 · 偏离", 20, FAINT, align="RIGHT"))
B.append(seg(M, HY + 36, W - M, HY + 36, 2, BORD))

# ---------------- item rows -------------------------------------------------
SX0, SW = 352.0, 470.0        # strip block x / width
RX, RW = 850, 296             # right readout block
ROW0, PITCH, CH = 464, 140, 126

for i, it in enumerate(ITEMS):
    ry = ROW0 + i * PITCH
    st = it["status"]
    sc = {"ok": OKC, "low": LOWC, "high": HIGHC}[st]
    B.append(box(M, ry, INNER, CH, CARD, radius=12, border=BORD, border_w=2))
    B.append(box(M, ry, 6, CH, sc, radius=3))

    # four elements, left column
    B.append(text(M + 24, ry + 30, 250, 42, it["cn"], 30, INK, bold=True))
    B.append(text(M + 24, ry + 76, 250, 32, it["ab"], 20, MUT, font="Inter"))

    # strip
    B.append(box(SX0, ry + 56, SW, 26, TRACK, radius=13))
    bx0 = SX0 + it["p_lo"] * SW
    bw = (it["p_hi"] - it["p_lo"]) * SW
    B.append(box(bx0, ry + 56, bw, 26, BAND, radius=13))
    if st == "low":
        dx = SX0 + it["p_res"] * SW
        B.append(box(dx, ry + 56, bx0 - dx, 26, LOWC, radius=13))
    elif st == "high":
        dx = SX0 + it["p_hi"] * SW
        B.append(box(dx, ry + 56, SX0 + it["p_res"] * SW - dx, 26, HIGHC, radius=13))

    mx = SX0 + it["p_res"] * SW
    B.append(box(mx - 4, ry + 44, 8, 50, MARK, radius=4))
    B.append(text(mx - 60, ry + 8, 120, 36, fmt(it["res"], it["dp"]), 25, sc,
                  bold=True, align="CENTER", font="Inter"))

    # reference bounds under the band
    B.append(text(bx0, ry + 90, 110, 30, fmt(it["lo"], it["dp"]), 18, BAND,
                  font="Inter"))
    B.append(text(bx0 + bw - 110, ry + 90, 110, 30, fmt(it["hi"], it["dp"]), 18,
                  BAND, align="RIGHT", font="Inter"))

    # right readout
    B.append(text(RX, ry + 16, RW, 46, it["res_str"], 34, sc, bold=True,
                  align="RIGHT", font="Inter"))
    B.append(text(RX, ry + 62, RW, 30, it["ref_str"], 19, MUT, align="RIGHT",
                  font="Inter"))
    if st == "ok":
        dev_txt, dev_col = "在参考区间内", OKC
    else:
        arrow = "↑" if st == "high" else "↓"
        dev_txt = "偏离 %s %s" % (arrow, it["dev_str"])
        dev_col = sc
    B.append(text(RX, ry + 90, RW, 30, dev_txt, 19, dev_col, bold=True,
                  align="RIGHT", font="Inter"))

LAST = ROW0 + (len(ITEMS) - 1) * PITCH + CH
assert LAST == 1430, LAST

# ---------------- reading notes / boundaries --------------------------------
NY, NH = 1452, 214
B.append(box(M, NY, INNER, NH, CARD, radius=12, border=BORD, border_w=2))
B.append(box(M, NY, 6, NH, BAND, radius=3))
B.append(text(M + 24, NY + 14, 1052, 40, "读法与边界", 26, INK, bold=True))
NOTES = [
    "· 参考区间覆盖约 95% 健康人群：在区间外不等于有病，在区间内也不等于没病",
    "· ↑↓ 只表示与参考区间的关系，不等于诊断；是否异常须由医生结合症状与其他检查判断",
    "· 参考区间因检测方法、仪器与人群而异，以本报告实际印制的区间为准",
    "· 演示边界：项目名与参考区间为常见项目的通用表述，数值均为自拟，不代表真实报告",
]
for k, n in enumerate(NOTES):
    assert tw_slot(n, 20) <= 1052, "C5 notes line too wide: %s" % n
    B.append(text(M + 24, NY + 58 + k * 38, 1052, 34, n, 20,
                  INK if k < 3 else MUT))

footer = ("演示数据 · 本报告不代表任何真实检验结果，也不构成医疗建议 "
          "· 仅用于信息呈现方式的重新设计")
assert tw_slot(footer, 19) <= INNER, "footer too wide"
B.append(text(M, NY + NH + 14, INNER, 40, footer, 19, FAINT))

end = NY + NH + 14 + 40
assert end <= H, "内容超出画布: %d > %d" % (end, H)
print("layout ends at %d / %d  (%d px spare)" % (end, H, H - end))
for it in ITEMS:
    print("  %-7s %8s  band %-14s  p_lo=%.3f p_hi=%.3f p_res=%.3f  %s%s"
          % (it["ab"], it["res_str"], it["ref_str"][3:], it["p_lo"], it["p_hi"],
             it["p_res"], it["status"],
             "" if it["status"] == "ok" else " dev=" + it["dev_str"]))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-04-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-04 %s written" % VER)
