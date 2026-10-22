# -*- coding: utf-8 -*-
"""B06 case-03 · 这个月为什么贵了 — 阶梯电费账单解剖

Problem: 账单只给「本月 366 度 / ¥199.62」，住户不知道钱花在哪一档、
是单价涨了还是自己用多了、还能再用多少。
Redesign: 把电价画成台阶，电费 = 台阶下的面积；两条竖线标出上月与本月
的用量，增量归因与离下一档的距离直接可见。

真实制度背景：居民生活用电阶梯电价（通常分三档）。SRC-03 抓取返回 404，
未取得正文，故档位电量与单价一律标注为示例演示数据，不作逐字引用。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, dash_line, emit, seg, text

W, H = 780, 1688
BG = "#0A1620"
L = 46
CW = W - 2 * L
CML, CMR = L + 24, L + CW - 24
INNER = CMR - CML

# ---------------- demo tier structure (示例档位 · 演示数据) ----------------
TIERS = [
    {"n": 1, "name": "第一档", "cap": 180, "price": 0.52, "tag": "基础档"},
    {"n": 2, "name": "第二档", "cap": 400, "price": 0.57, "tag": "抬高档"},
    {"n": 3, "name": "第三档", "cap": None, "price": 0.82, "tag": "高耗档"},
]
CUR, PREV = 366, 258


def split(total):
    """allocate `total` 度 across the three tiers, non-overlapping."""
    out, rem, lo = [], total, 0
    for t in TIERS:
        cap = t["cap"]
        span = (cap - lo) if cap is not None else None
        take = rem if span is None else min(rem, span)
        out.append((t, max(0, take)))
        rem -= max(0, take)
        lo = cap if cap is not None else lo
    assert rem == 0, "档位未覆盖全部用电量"
    return out


def money(total):
    rows = split(total)
    fees = [round(q * t["price"], 2) for t, q in rows]
    return rows, fees, round(sum(fees), 2)


cur_rows, cur_fees, cur_total = money(CUR)
prev_rows, prev_fees, prev_total = money(PREV)

# ---------------- assertions -----------------------------------------------
# C2 — tiers are disjoint and exhaustive
assert [q for _, q in cur_rows] == [180, 186, 0]
assert sum(q for _, q in cur_rows) == CUR == 180 + 186 + 0
assert [q for _, q in prev_rows] == [180, 78, 0]
assert sum(q for _, q in prev_rows) == PREV
# no tier band overlaps: each quota lies within its own band
lo = 0
for t, q in cur_rows:
    assert q == 0 or (t["cap"] is None or q <= t["cap"] - lo)
    lo = t["cap"] if t["cap"] is not None else lo

# C3 — per-tier fee = qty x price, and the tiers sum to the bill
assert cur_fees == [93.60, 106.02, 0.00], cur_fees
assert abs(cur_total - 199.62) < 1e-9, cur_total
assert prev_fees == [93.60, 44.46, 0.00], prev_fees
assert abs(prev_total - 138.06) < 1e-9, prev_total
assert abs(sum(cur_fees) - cur_total) < 1e-9
for (t, q), f in zip(cur_rows, cur_fees):
    assert abs(round(q * t["price"], 2) - f) < 1e-9

# C4 — the increase is fully attributed to one tier
d_qty = CUR - PREV
d_money = round(cur_total - prev_total, 2)
d_by_tier = [round((cq - pq) * t["price"], 2)
             for (t, cq), (_, pq) in zip(cur_rows, prev_rows)]
assert d_qty == 108
assert abs(d_money - 61.56) < 1e-9, d_money
assert d_by_tier == [0.0, 61.56, 0.0], d_by_tier
assert abs(sum(d_by_tier) - d_money) < 1e-9
# both months sit in the same tier band -> the rate did not change
assert cur_rows[1][0]["price"] == prev_rows[1][0]["price"]
room = TIERS[1]["cap"] - CUR
assert room == 34, room

B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(text(L, 38, 240, 40, "09:35", 27, "#E8F3FB", bold=True, font="Inter"))
B.append(box(640, 44, 26, 17, "#E8F3FB", radius=3))
B.append(box(672, 40, 15, 24, "#E8F3FB", radius=2))
B.append(box(696, 38, 40, 28, "#E8F3FB", radius=6))
B.append(box(737, 45, 4, 14, "#E8F3FB", radius=2))
B.append(text(L, 94, 640, 56, "这个月为什么贵了", 42, "#FFFFFF", bold=True))
B.append(text(L, 152, 640, 34, "阶梯电费账单解剖 · 居民生活用电", 23, "#6E93A8"))

# ---------------- hero strip ------------------------------------------------
HY, HH = 196, 100
STATS = [("366 度", "本月用电", "#FFFFFF"),
         ("¥199.62", "应缴电费", "#F2A93B"),
         ("+¥61.56", "比上月增加", "#FF7A5C")]
cw = (CW - 2 * 12) / 3.0
for i, (val, lab, col) in enumerate(STATS):
    x = L + i * (cw + 12)
    B.append(box(x, HY, cw, HH, "#10262F", radius=16, border="#1E4557",
                 border_w=2))
    B.append(text(x + 16, HY + 18, cw - 32, 44, val, 31, col, bold=True,
                  font="Inter"))
    B.append(text(x + 16, HY + 64, cw - 32, 28, lab, 17, "#6E93A8"))

# ---------------- chart: bill = area under the stepped price curve ---------
CY_, CH = 320, 420
B.append(box(L, CY_, CW, CH, "#10262F", radius=18, border="#1E4557",
             border_w=2))
B.append(text(CML, CY_ + 16, 500, 34, "电价台阶 · 阴影面积 = 电费", 25,
              "#FFFFFF", bold=True))
# legend
B.append(box(CML, CY_ + 58, 12, 12, "#F2A93B", radius=2))
B.append(text(CML + 18, CY_ + 54, 210, 26, "本月已用电 = 电费面积", 16, "#8FB4C7"))
B.append(box(CML + 232, CY_ + 54, 3, 20, "#4FD1C5", radius=1))
B.append(text(CML + 242, CY_ + 54, 150, 26, "上月 258 度", 16, "#4FD1C5"))
B.append(text(CML + 400, CY_ + 54, 240, 26, "┊ 第三档起点 400 度", 16, "#FF7A5C"))

PX0, PX1 = 118.0, 700.0
PY0, PY1 = CY_ + 98, CY_ + 316          # plot top / x-axis
X_MAX, P_MAX = 450.0, 1.00


def sx(deg):
    return PX0 + deg * (PX1 - PX0) / X_MAX


def sy(price):
    return PY1 - price * (PY1 - PY0) / P_MAX


# un-used structure drawn first, then the paid area on top
struct = [(0, 180, 0.52), (180, 400, 0.57), (400, X_MAX, 0.82)]
for a, b, p in struct:
    B.append(box(sx(a), sy(p), sx(b) - sx(a), PY1 - sy(p), "#16363F",
                 border="#2C4A63", border_w=2))

# this month's paid area (tier1 fully + tier2 partially)
fill = [(0, 180, 0.52, "#A9701F"), (180, CUR, 0.57, "#F2A93B")]
for a, b, p, col in fill:
    B.append(box(sx(a) + 1, sy(p), sx(b) - sx(a) - 2, PY1 - sy(p), col))

# x-axis
B.append(seg(PX0, PY1, PX1, PY1, 3, "#2C4A63"))
for deg in (0, 180, 400):
    B.append(seg(sx(deg), PY1, sx(deg), PY1 + 7, 3, "#2C4A63"))
    B.append(text(sx(deg) - 40, PY1 + 10, 80, 24, "%d 度" % deg, 16, "#6E93A8",
                  align="CENTER", font="Inter"))

# tier price labels (each on its own free band)
B.append(text(sx(0) + 12, sy(0.52) + 16, 240, 30, "第一档 0.52 元/度", 18,
              "#FFE0BE", bold=True))
B.append(text(sx(180) + 12, sy(0.57) + 16, 240, 30, "第二档 0.57 元/度", 18,
              "#1B2410", bold=True))
B.append(box(sx(370), PY0 + 2, 210, 30, "#10262F", radius=6))
B.append(text(sx(370), PY0 + 6, 210, 26, "第三档 0.82 元/度", 18, "#FF7A5C",
              bold=True, align="RIGHT"))

# month markers
for deg, lab, col, wid in ((PREV, "上月 258 度", "#4FD1C5", 120),
                           (CUR, "本月 366 度", "#FFD166", 120)):
    B.append(box(sx(deg) - 1.5, PY0, 3, PY1 - PY0, col))
    B.append(text(sx(deg) - wid / 2, PY1 + 42, wid, 26, lab, 16, col, bold=True,
                  align="CENTER"))
# third-tier threshold
B.append(dash_line(sx(400), PY0, sx(400), PY1, "#FF7A5C", dash=10, gap=7, thick=3))
B.append(text(sx(400) - 74, PY1 + 70, 148, 26, "第三档 400 度", 16, "#FF7A5C",
              bold=True, align="CENTER"))

assert PY1 + 96 < CY_ + CH, "chart labels 越出面板"

# ---------------- tier table ------------------------------------------------
TY_, TH = 760, 400
B.append(box(L, TY_, CW, TH, "#10262F", radius=18, border="#1E4557",
             border_w=2))
B.append(text(CML, TY_ + 16, 500, 34, "本月分档明细", 25, "#FFFFFF", bold=True))
B.append(text(CMR - 300, TY_ + 22, 300, 28, "示例档位 · 演示数据", 17, "#FF7A5C",
              align="RIGHT"))

HDR = TY_ + 62
B.append(box(CML, HDR - 6, INNER, 36, "#16363F", radius=8))
B.append(text(CML + 12, HDR, 180, 26, "档位", 18, "#8FB4C7"))
B.append(text(CML + 190, HDR, 130, 26, "用电(度)", 18, "#8FB4C7", align="RIGHT"))
B.append(text(CML + 330, HDR, 140, 26, "单价(元/度)", 18, "#8FB4C7",
              align="RIGHT"))
B.append(text(CML + 470, HDR, INNER - 470 - 12, 26, "小计(元)", 18, "#8FB4C7",
              align="RIGHT"))

ry = HDR + 56
for (t, q), f in zip(cur_rows, cur_fees):
    used = q > 0
    col = "#F2A93B" if used else "#4E6E88"
    B.append(text(CML + 12, ry, 190, 32, "%s %s" % (t["name"], t["tag"]), 21,
                  col if used else "#5E7E92", bold=used))
    B.append(text(CML + 190, ry, 130, 32, "%d" % q, 22, col if used else "#5E7E92",
                  align="RIGHT", font="Inter"))
    B.append(text(CML + 330, ry, 140, 32, "%.2f" % t["price"], 21, "#8FB4C7",
                  align="RIGHT", font="Inter"))
    B.append(text(CML + 470, ry, INNER - 470 - 12, 32,
                  "%.2f" % f, 22, col, bold=used, align="RIGHT", font="Inter"))
    B.append(seg(CML + 6, ry + 40, CMR - 6, ry + 40, 1, "#1B3B4A"))
    ry += 52

B.append(box(CML, ry + 6, INNER, 76, "#1B3B4A", radius=12))
B.append(text(CML + 16, ry + 20, 300, 30, "合计 366 度", 22, "#FFFFFF", bold=True))
B.append(text(CML + 16, ry + 52, 340, 26,
              "93.60 + 106.02 + 0.00", 17, "#8FB4C7", font="Inter"))
B.append(text(CML + 380, ry + 18, INNER - 396, 52, "¥199.62", 34, "#F2A93B",
              bold=True, align="RIGHT", font="Inter"))
assert ry + 88 < TY_ + TH, "表格越出面板"

# ---------------- insight: where the money went ----------------------------
IY, IH = 1180, 220
B.append(box(L, IY, CW, IH, "#10262F", radius=18, border="#F2A93B",
             border_w=2))
B.append(box(L, IY, 6, IH, "#F2A93B", radius=3))
B.append(text(CML, IY + 16, 620, 34, "涨价来自用量，不是单价", 25, "#F2A93B",
              bold=True))
B.append(text(CML, IY + 58, INNER, 30,
              "两个月都落在第二档（181–400 度），单价没变。", 20, "#DDEBF3"))
B.append(text(CML, IY + 94, INNER, 30,
              "多用的 108 度 × 0.57 元 = 61.56 元，即全部增量。", 20, "#DDEBF3"))
B.append(box(CML, IY + 136, INNER, 68, "#2A1B12", radius=12,
             border="#FF7A5C", border_w=2))
B.append(text(CML + 18, IY + 148, 600, 30, "距第三档还剩 34 度", 22, "#FF7A5C",
              bold=True))
B.append(text(CML + 18, IY + 180, 600, 24,
              "再用 34 度，超出部分单价跳到 0.82 元/度", 17, "#C9B9A8"))

# ---------------- boundaries / sources -------------------------------------
NY, NH = 1420, 240
B.append(box(L, NY, CW, NH, "#0E2A33", radius=18, border="#2F6E7E",
             border_w=2))
B.append(box(L, NY, 6, NH, "#2F6E7E", radius=3))
B.append(text(CML, NY + 14, 620, 34, "数据与来源边界", 24, "#7FD3C6", bold=True))
B.append(text(CML, NY + 56, INNER, 34,
              "· 制度背景：居民生活用电阶梯电价通常分三档", 19, "#DDEBF3"))
B.append(text(CML, NY + 96, INNER, 34,
              "· 三档电量 180/400 度与单价 0.52/0.57/0.82 元为示例演示，", 19,
              "#DDEBF3"))
B.append(text(CML, NY + 132, INNER, 34,
              "  不指向任何城市或供电公司现行方案", 19, "#DDEBF3"))
B.append(text(CML, NY + 172, INNER, 34,
              "· 原始条目 SRC-03 抓取返回 404，未取得正文，故不逐字引用", 19,
              "#DDEBF3"))
B.append(text(CML, NY + 208, INNER, 26,
              "· 用电量与金额均为自拟演示数据", 17, "#5E7E92"))

end = NY + NH
assert end <= H, "内容超出画布: %d > %d" % (end, H)
print("layout ends at %d / %d  (%d px spare)" % (end, H, H - end))
print("cur=%d度 ¥%.2f  prev=%d度 ¥%.2f  delta=%d度 ¥%.2f  room_to_t3=%d"
      % (CUR, cur_total, PREV, prev_total, d_qty, d_money, room))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-03-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-03 %s written" % VER)
