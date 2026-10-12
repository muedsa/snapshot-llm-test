"""B02 case-08 年度统计年报 1600x1200（PDF 首页，报送理事会/街道/捐赠者/媒体）。

设计任务：读者是拿预算和审计说话的人，所以这一页的第一要求不是好看，是**可复算**。
顺序：总量 → 时间分布 → 类目分布 → 机型 → 馆藏状态 → 估算效益 → 口径与不折算项。
最后一条放在最显眼的深色带里：年报里没写的数（会费收入、维修支出）比写出来的数
更容易被引用出去，必须自己先划清「台账算不出什么」。
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
for p in ("_suite/scripts", "B01", "B02"):
    sys.path.insert(0, str(root / "tmp" / rid / p))

from dslkit import TextFit  # noqa: E402
import b02kit as B  # noqa: E402

P = B.P
D = B.DATA
BR = D["brand"]
RU = BR["rules"]
S = D["summary"]
R = D["report"]
CATS = D["cats"]
W, H = 1600, 1200
M = 64
CW = W - 2 * M
LW = 900                      # 左栏：两张主图
RX = M + LW + 40              # 右栏：机型 / 状态 / 估算
RW = CW - LW - 40
OUT = root / "tmp" / rid / "B02" / "case-08"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")

tf = TextFit()
d = B.paper_doc(W, H, dark=False, noise=14, seed=83)
INK, ORANGE, RED = P["ink"], P["orange"], P["red"]
GRID = B.blend(INK, 0.10, P["paper"])

# ---------------- 页眉 ----------------
HB = 190
d.rect(0, 0, W, HB, B.blend(P["ink"], 0.93, P["paper"]))
B.brand_mark(d, M + 28, 58, 28, color=ORANGE, ink=P["paper"],
             bg=B.blend(P["ink"], 0.93, P["paper"]))
B.tlab(d, tf, "h-brand", M + 70, 38, 520, 36,
       "%s · %s" % (BR["name"], "年度统计年报"), 26, P["paper"], "BOLD")
B.tlab(d, tf, "h-title", M, 82, CW - 300, 58, "2025 年，工具去了哪里", 44,
       B.blend(P["white"], 0.94, P["dark"]), "BOLD")
B.tlab(d, tf, "h-sub", M, 148, CW - 300, 26,
       "报送：街道公共服务办公室 · 理事会 · 捐赠人 · 媒体　　统计期间 2025-01-01 至 2025-12-31",
       16, B.blend(P["white"], 0.6, P["dark"]), None)
d.rect(W - M - 236, 40, 236, 110, B.blend(P["white"], 0.10, P["dark"]), radius=8)
for i, (lab, val) in enumerate((("文号", "WH-AR-2025-01"), ("本页生成日", RU["today"]),
                                ("口径", "全年台账全量"))):
    B.tlab(d, tf, "h-doc%d" % i, W - M - 220, 52 + i * 32, 200, 24,
           "%s　%s" % (lab, val), 14 if i else 15,
           B.blend(P["white"], 0.78 - i * 0.12, P["dark"]),
           "BOLD" if i == 0 else None, align="CENTER", features="tnum")

# ---------------- KPI ----------------
KY = HB + 24
KH = 104
kw = (CW - 4 * 16) / 5.0
kpis = [
    ("%d" % S["total_loans"], "次借阅", "全年台账笔数，逐笔可查", ORANGE),
    ("%d" % S["members"], "名会员", "其中 %d 人在年内有借出记录" % R["active_members_with_loans"], P["steel"]),
    ("%.2f" % R["loans_per_tool"], "次/件·年", "%d 件馆藏的平均周转" % len(D["tools"]), P["steel"]),
    ("%d" % S["available_now"], "件可借", "另有 %d 在借 · %d 维修 · %d 报废"
     % (S["in_borrow_now"], S["in_repair_now"], S["scrap_now"]), P["green"]),
    (B.pct(S["overdue_rate"]), "逾期率", "%d 次，累计 %d 天"
     % (S["overdue_loans"], S["overdue_days_sum"]), RED),
]
for i, (v, u, note, tone) in enumerate(kpis):
    x = M + i * (kw + 16)
    d.rect(x, KY, kw, KH, P["white"], radius=8)
    d.rect(x, KY, kw, 3, tone)
    B.tlab(d, tf, "k%d-v" % i, x + 18, KY + 22, kw - 36, 46, v, 40, tone, "BOLD",
           features="tnum")
    B.tlab(d, tf, "k%d-u" % i, x + 18, KY + 68, kw - 36, 22, u, 15, INK, "BOLD")
    B.tlab(d, tf, "k%d-n" % i, x + 18, KY + 88, kw - 36, 20, note, 11, P["ink3"], None,
           features="tnum")

y = KY + KH + 24

# ---------------- 01 月度分布 ----------------
B.section_head(d, M, y, LW, 1, "月度借阅分布", sub="单位：次", size=24)
y += 46
CH = 186
GX = 40
cx0, cw0 = M + GX, LW - GX - 6
mx = max(m["loans"] for m in R["monthly"])
slot = cw0 / 12.0
bw = slot - 24
for g in (0, 100, 200, 300):
    yy = y + CH - CH * g / float(mx)
    d.rect(cx0, int(yy), cw0, 1, GRID if g else B.blend(INK, 0.34, P["paper"]))
    B.tlab(d, tf, "ax%d" % g, M, int(yy) - 8, GX - 8, 16, "%d" % g, 11, P["ink3"],
           None, align="END", features="tnum")
base = y + CH
for i, m in enumerate(R["monthly"]):
    x = cx0 + i * slot + 12
    hgt = int(round(CH * m["loans"] / float(mx)))
    peak = m["month"] == S["peak_month"]["month"]
    trough = m["month"] == R["trough_month"]["month"]
    d.rect(int(x), int(base - hgt), int(bw), hgt,
           ORANGE if peak else (B.blend(P["steel"], 0.42, P["paper"]) if trough
                                else B.blend(P["steel"], 0.82, P["paper"])))
    B.tlab(d, tf, "mo%d-v" % i, int(x) - 12, int(base - hgt) - 20, int(bw) + 24, 18,
           "%d" % m["loans"], 12, INK if peak else P["ink2"], "BOLD" if peak else None,
           align="CENTER", features="tnum")
    B.tlab(d, tf, "mo%d" % i, int(x) - 12, base + 6, int(bw) + 24, 18, "%d月" % m["month"],
           12, P["ink2"], "BOLD" if peak else None, align="CENTER", features="tnum")
B.tlab(d, tf, "mo-note", cx0, base + 28, cw0, 20,
       "峰值 %d月 %d 次、谷值 %d月 %d 次，相差 %.1f 倍；台账没有天气与节假日字段，本页不对峰谷作归因。"
       % (S["peak_month"]["month"], S["peak_month"]["loans"],
          R["trough_month"]["month"], R["trough_month"]["loans"],
          S["peak_month"]["loans"] / float(R["trough_month"]["loans"])),
       13, P["ink3"], None, features="tnum")
y = base + 58

# ---------------- 02 类目占比 ----------------
B.section_head(d, M, y, LW, 2, "类目借出占比", sub="9 类，合计 2946 次", size=24)
y += 46
rows = sorted(D["summary"]["per_cat"], key=lambda p: -p["loans_2025"])
mxs = max(p["loans_2025"] for p in rows)
BX, BW = M + 176, 470
for i, p in enumerate(rows):
    ry = y + i * 32
    if i % 2 == 0:
        d.rect(M, ry, LW, 28, B.blend(INK, 0.025, P["paper"]), radius=4)
    col = B.cat_color(p["code"])
    d.rect(M + 8, ry + 5, 4, 20, col)
    B.tlab(d, tf, "c%d" % i, M + 22, ry + 4, 148, 22, p["name"], 16, INK, "BOLD")
    d.rect(BX, ry + 8, BW, 14, B.blend(INK, 0.08, P["paper"]), radius=7)
    fw = int(BW * p["loans_2025"] / float(mxs))
    d.rect(BX, ry + 8, max(14, fw), 14, col, radius=7)
    B.tlab(d, tf, "c%d-n" % i, BX + BW + 10, ry + 2, 76, 22, "%d 次" % p["loans_2025"],
           15, P["ink2"], None, align="END", features="tnum")
    B.tlab(d, tf, "c%d-s" % i, BX + BW + 98, ry + 3, 150, 22,
           "占 %s · 逾期 %s" % (B.pct(p["share"]), B.pct(p["overdue_rate"])), 12,
           P["ink3"], None, align="END", features="tnum")
y += 9 * 32 + 14

# ---------------- 03 机型 Top ----------------
y0 = KY + KH + 24
B.section_head(d, RX, y0, RW, 3, "最常借出的机型", sub="Top 6", size=24)
ry = y0 + 46
tm = R["top_models"]
mxt = max(x["loans"] for x in tm)
TX, TW = RX + 132, RW - 132 - 96
for i, t in enumerate(tm):
    yy = ry + i * 30
    col = B.cat_color(t["cat"])
    B.tlab(d, tf, "t%d" % i, RX, yy + 2, 126, 22, t["name"], 15, INK, "BOLD")
    d.rect(TX, yy + 6, TW, 12, B.blend(INK, 0.08, P["paper"]), radius=6)
    d.rect(TX, yy + 6, max(12, int(TW * t["loans"] / float(mxt))), 12, col, radius=6)
    B.tlab(d, tf, "t%d-n" % i, TX + TW + 10, yy + 1, 86, 22, "%d 次" % t["loans"], 14,
           P["ink2"], None, align="END", features="tnum")
caveat = ("前六名同属电动工具 S2 类、各 8 台；最高 %d 次与最低 %d 次只差 %d 次（%.1f%%），"
          "落在随机波动范围内，本页不据此提出单一机型采购建议。"
          % (tm[0]["loans"], tm[-1]["loans"], tm[0]["loans"] - tm[-1]["loans"],
             (tm[0]["loans"] - tm[-1]["loans"]) / float(tm[0]["loans"]) * 100))
B.tlab(d, tf, "t-cav", RX, ry + 6 * 30 + 4, RW, 54, caveat, 12, P["ink3"], None, lines=3)

# ---------------- 04 馆藏状态 ----------------
ry = ry + 6 * 30 + 4 + 56
B.section_head(d, RX, ry, RW, 4, "馆藏状态", sub="%d 件" % len(D["tools"]), size=24)
ry += 46
order = ["在馆", "在借", "维修中", "报废待处理"]
tot = sum(R["states"].values())
sx = RX
d.rect(RX, ry, RW, 24, B.blend(INK, 0.08, P["paper"]))
for st in order:
    n_ = R["states"][st]
    wseg = int(RW * n_ / float(tot))
    d.rect(int(sx), ry, max(3, wseg), 24, B.STATE_COLOR[st])
    sx += wseg
    if st != order[-1]:
        d.rect(int(sx) - 1, ry, 2, 24, P["paper"])
ry += 34
for i, st in enumerate(order):
    n_ = R["states"][st]
    yy = ry + i * 24
    d.rect(RX, yy + 4, 12, 12, B.STATE_COLOR[st], radius=3)
    B.tlab(d, tf, "s%d" % i, RX + 22, yy, 120, 22, st, 14, INK, None)
    B.tlab(d, tf, "s%d-n" % i, RX + 150, yy, 90, 22, "%d 件" % n_, 14, P["ink2"], None,
           features="tnum")
    B.tlab(d, tf, "s%d-p" % i, RX + 240, yy, 70, 22, B.pct(n_ / float(tot)), 13,
           P["ink3"], None, features="tnum")
    if st == "报废待处理":
        B.tlab(d, tf, "s%d-x" % i, RX + 316, yy, RW - 316, 22, "已按程序待处置，不计入可借数",
               12, P["ink3"], None)

# ---------------- 05 估算效益 ----------------
ry = ry + 4 * 24 + 18
B.section_head(d, RX, ry, RW, 5, "估算效益（模型值）", sub="非成交记录", size=24)
ry += 46
est = [
    ("%d 件" % S["avoid_buy_total"], "避免重复购买：Σ 类目借出次数 × 该类一次性用途比例"),
    ("%.1f 吨" % (S["kg_saved_total"] / 1000.0), "减少用料：上述件数 × 同类单件用料"),
    ("¥%.1f 万" % (R["avoided_value_yuan"] / 10000.0),
     "折算少支出：上述件数 × 同类台账平均购置价"),
]
for i, (v, note) in enumerate(est):
    yy = ry + i * 36
    B.tlab(d, tf, "e%d-v" % i, RX, yy, 150, 26, v, 22, ORANGE, "BOLD", features="tnum")
    B.tlab(d, tf, "e%d-n" % i, RX + 156, yy + 2, RW - 156, 34, note, 12, P["ink3"], None,
           lines=2)

BODY_BOTTOM = max(y, ry + 3 * 36)
assert BODY_BOTTOM + 20 + 130 + 20 + 44 <= H, BODY_BOTTOM

# ---------------- 口径与不折算 ----------------
BY = BODY_BOTTOM + 20
BH = 130
d.rect(M, BY, CW, BH, B.blend(P["ink"], 0.93, P["paper"]), radius=10)
d.rect(M, BY, 6, BH, ORANGE, radius=3)
B.tlab(d, tf, "b-title", M + 26, BY + 16, 200, 26, "口径与边界", 20,
       B.blend(P["white"], 0.92, P["dark"]), "BOLD")
cols = [
    ("可复算", "本页全部数字来自同一张 2025 借阅台账（%d 笔）与馆藏工具表（%d 件），"
              "不含抽样、不含外推；类目占比与月度分布的分母都是 %d 次。"
     % (S["total_loans"], len(D["tools"]), S["total_loans"])),
    ("估算项", "05 组三个数是模型折算：件数按一次性用途比例、用料按同类单件重量、"
              "金额按同类台账平均购置价。它们不是采购发票，也不是销量。"),
    ("不折算", ["· 会费总收入：台账无 %d 人的卡型构成" % S["members"],
               "· 维修实际支出：无发票流水",
               "· 捐赠折算：无捐赠记录"]),
    ("唯一现金项", "逾期费 ¥%s = ¥%g/件·天 × %d 天，由台账逾期天数直接算出，可逐笔核对。"
     % (B.money(S["late_fee_yuan"]), RU["late_fee_per_day"], S["overdue_days_sum"])),
]
cw3 = (CW - 52 - 3 * 22) / 4.0
for i, (h_, t_) in enumerate(cols):
    x = M + 26 + i * (cw3 + 22)
    if i:
        d.rect(x - 11, BY + 18, 1, BH - 36, B.blend(P["white"], 0.14, P["dark"]))
    B.tlab(d, tf, "b%d-h" % i, x, BY + 48, cw3, 22, h_, 15, P["brass"], "BOLD")
    body = B.blend(P["white"], 0.66, P["dark"])
    if isinstance(t_, list):
        for k, line in enumerate(t_):
            B.tlab(d, tf, "b%d-%d" % (i, k), x, BY + 72 + k * 19, cw3, 18, line, 12,
                   body, None)
    else:
        B.tlab(d, tf, "b%d" % i, x, BY + 72, cw3, 50, t_, 12, body, None, lines=3)

B.footer(d, M, BY + BH + 20, CW, "full", note=BR["fiction_notice"])
assert BY + BH + 20 + 44 <= H, BY + BH + 20

dsl = d.dsl()
(OUT / ("case-08-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-08", len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:14]:
    print("  !", p)
print("left ends", y, "right ends", BODY_BOTTOM, "band", BY, "->", BY + BH, "of", H)
