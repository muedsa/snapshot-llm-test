"""B02 case-04 借出小票 720x1560（80mm 热敏纸）。

设计任务：服务台打完递出来的那张纸。它不是收据那么简单的东西——它要在一张
会被塞进口袋的纸上，把「你手上这三件分别什么时候该还、哪一件已经欠费、
下次来该怎么处理」讲清楚。所以是窄栏 + 虚线分段 + 等宽数字，没有彩色。
"""
import datetime
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
S = D["summary"]
M = D["member"]
RU = D["brand"]["rules"]
AL = D["active_loans"]
CATS = {c["code"]: c for c in D["cats"]}
W, H = 720, 1560
X, CW = 48, 624
OUT = root / "tmp" / rid / "B02" / "case-04"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")
TODAY = datetime.date.fromisoformat(RU["today"])
DOCNO = "R%s-%s" % (TODAY.strftime("%Y%m%d"), M["id"][-4:])
PAPER = "#FFFDF8"

tf = TextFit()
d = B.paper_doc(W, H, noise=16, seed=31)
# 热敏纸没有牛皮纸颗粒：盖一层极浅的纸白，只保留上下撕孔
d.rect(0, 0, W, H, B.blend(P["ink"], 0.012, PAPER))
for yy in (14, H - 14):
    for i in range(int(CW / 14)):
        d.rect(X + i * 14, yy, 4, 4, B.blend(P["ink"], 0.22, PAPER))

ink, ink2, ink3 = P["ink"], P["ink2"], P["ink3"]
y = 46
B.brand_mark(d, W / 2, y + 26, 26, bg=PAPER)
B.tlab(d, tf, "h1", X, y + 62, CW, 34, D["brand"]["name"], 28, ink, "BOLD",
       align="CENTER")
B.tlab(d, tf, "h2", X, y + 100, CW, 24, "%s · 服务台"
       % D["brand"]["sites"][0].split("（")[0], 15, ink2, None, align="CENTER")
B.tlab(d, tf, "h3", X, y + 124, CW, 22, "在借清单与费用告知单", 13, ink3, None,
       align="CENTER")
y += 168
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 16
for k, v in (("打印时间", RU["today"]), ("单据号", DOCNO),
             ("会员", "%s · %s" % (M["id"], M["name"])),
             ("卡种", "%s · %d 人共用 · 额度 %d 件"
              % (M["card"], M["household"], RU["max_active"]))):
    B.tlab(d, tf, "kv-%s" % k, X, y, 130, 22, k, 14, ink3, None)
    B.tlab(d, tf, "kv-%s-v" % k, X + 128, y, CW - 128, 22, v, 15, ink, "BOLD",
           features="tnum")
    y += 26
y += 6
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 20
B.tlab(d, tf, "items-h", X, y, CW, 22, "在借 %d 件" % len(AL), 14, ink, "BOLD")
B.tlab(d, tf, "items-h2", X, y, CW, 22, "应还日期在右 · 逾期按件计", 12, ink3, None,
       align="END")
y += 32
for i, l in enumerate(AL):
    late = l["overdue_days"] > 0
    B.hex_chip(d, X + 14, y + 16, 14, B.cat_color(l["cat"]), "%s" % CATS[l["cat"]]["zone"],
               size=12, bg=PAPER)
    B.tlab(d, tf, "it%d-name" % i, X + 38, y, 360, 26, l["name"], 19, ink, "BOLD")
    B.tlab(d, tf, "it%d-id" % i, X + 38, y + 26, 360, 22, l["tool"], 13, ink3, None,
           features="tnum")
    B.tlab(d, tf, "it%d-due" % i, X + 400, y, 224, 24,
           "应还 %s" % l["due"], 15, ink if not late else P["red"], "BOLD",
           align="END", features="tnum")
    st = ("逾期 %d 天 · ¥%g" % (l["overdue_days"], l["late_fee"])) if late else \
         ("还剩 %d 天" % l["days_left"])
    B.tlab(d, tf, "it%d-st" % i, X + 400, y + 26, 224, 22, st, 13,
           P["red"] if late else ink3, None, align="END", features="tnum")
    B.tlab(d, tf, "it%d-out" % i, X + 400, y + 46, 224, 20,
           "借出 %s" % l["out"], 11, ink3, None, align="END", features="tnum")
    if l["renewed"]:
        B.tlab(d, tf, "it%d-rn" % i, X + 38, y + 50, 360, 20,
               l["note"], 11, P["red"], None)
    else:
        B.tlab(d, tf, "it%d-rn" % i, X + 38, y + 50, 360, 20,
               "可续借一次至 %s" % l["due_after_renew"], 11, ink3, None,
               features="tnum")
    y += 82
    if i < len(AL) - 1:
        B.dash_line(d, X, y, CW, B.blend(ink, 0.22, PAPER), seg=4, gap=6)
        y += 14
y += 4
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 18
for k, v, c in (("押金", "¥%d（本馆不收押金）" % RU["deposit"], ink2),
                ("借出费用", "¥0 · 借出不另收费", ink2),
                ("逾期应计", "¥%g（%g 元/件·天 × %d 天 × 1 件）" % (
                    sum(l["late_fee"] for l in AL), RU["late_fee_per_day"],
                    max(l["overdue_days"] for l in AL)), P["red"])):
    B.tlab(d, tf, "fee-%s" % k, X, y, 200, 22, k, 14, ink3, None)
    B.tlab(d, tf, "fee-%s-v" % k, X, y, CW, 22, v, 15, c, None, align="END",
           features="tnum")
    y += 28
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 20
B.tlab(d, tf, "total-k", X, y + 14, 200, 26, "本次应缴", 16, ink, "BOLD")
B.tlab(d, tf, "total-v", X, y, CW, 56, "¥%g" % sum(l["late_fee"] for l in AL), 46,
       P["red"], "BOLD", align="END", features="tnum")
y += 76
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 22
B.tlab(d, tf, "notice-h", X, y, CW, 24, "下次到馆前请知道", 15, ink, "BOLD")
y += 30
notices = [
    "逾期费 ¥%g/件·天，从应还次日算起；归还没清前不能续借。" % RU["late_fee_per_day"],
    "逾期满 %d 天，本卡借出权限暂停，需在服务台办理恢复。" % RU["suspend_days"],
    "续借每件一次（+%d 天）：馆内刷卡、触摸屏或电话办理。" % RU["renew_days"],
    "%s，营业时间内投入即可，不必等工作人员。" % RU["return_point"],
    "借电动/气动工具须先通过 Safety 101（%d 分钟）；本人 %s。"
    % (RU["safety_101_min"], M["safety_101"]),
    "%s；损坏不要自行拆解，带回馆内登记。" % RU["repair_by"],
]
for i, n in enumerate(notices):
    d.rect(X + 2, y + 8, 6, 6, ink3)
    B.tlab(d, tf, "nt%d" % i, X + 20, y, CW - 20, 22, n, 14, ink2, None)
    y += 26
y += 10
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 20
# 还期时间轴：把三件的借出/应还画在同一条日期轴上，逾期段用红色
d0 = min(datetime.date.fromisoformat(l["out"]) for l in AL)
d1 = max(datetime.date.fromisoformat(l["due_after_renew"]) for l in AL)
span = (d1 - d0).days or 1
AX, AW = X + 96, CW - 96 - 12
def px(dt):
    return AX + (dt - d0).days / float(span) * AW
B.tlab(d, tf, "tl-h", X, y - 2, 92, 22, "还期时间轴", 13, ink, "BOLD")
for i, l in enumerate(AL):
    ry = y + 24 + i * 36
    o = datetime.date.fromisoformat(l["out"])
    u = datetime.date.fromisoformat(l["due"])
    e = datetime.date.fromisoformat(l["due_after_renew"])
    col = B.cat_color(l["cat"])
    d.rect(AX, ry + 6, AW, 1, B.blend(ink, 0.18, PAPER))
    d.rect(px(o), ry + 4, max(2.0, px(u) - px(o)), 6, col, radius=3)
    if l["overdue_days"]:
        d.rect(px(u), ry + 4, max(2.0, px(TODAY) - px(u)), 6, P["red"], radius=3)
    d.rect(px(e) - 1, ry - 2, 2, 18, B.blend(ink, 0.55, PAPER))
    B.tlab(d, tf, "tl%d" % i, X, ry - 2, 90, 20, l["name"], 12, ink2, None)
    B.tlab(d, tf, "tl%d-d" % i, px(u) - 40, ry + 16, 90, 18,
           B.date_md(l["due"]), 11, P["red"] if l["overdue_days"] else ink3, None,
           features="tnum")
td = px(TODAY)
for i in range(int((td - AX) / 8)):
    d.rect(AX + i * 8, y + 20, 3, 3, ink)
B.tlab(d, tf, "tl-today", td - 24, y + 124, 60, 20, "今天", 11, ink, "BOLD")
B.tlab(d, tf, "tl-end", AX + AW - 76, y + 124, 76, 20, B.date_md(d1.isoformat()),
       11, ink3, None, align="END", features="tnum")
y += 146
B.dash_line(d, X, y, CW, B.blend(ink, 0.45, PAPER))
y += 20
B.barcode(d, X, y, 300, 52, DOCNO, ink)
B.tlab(d, tf, "bc", X, y + 58, 300, 20, DOCNO, 12, ink3, None, features="tnum")
B.qr_placeholder(d, X + 474, y, 150, DOCNO, fg=ink, bg=PAPER)
B.tlab(d, tf, "qr", X + 330, y + 8, 136, 60, "扫码查看电子回单（占位图，不指向真实地址）",
       12, ink3, None, lines=3)
y += 150 + 16
B.tlab(d, tf, "stat", X, y, CW, 22, "2025 全年借出 %s 次 · 现在在借 %d 件 · 累计避免 %d 件重复购买"
       % (S["total_loans"], S["in_borrow_now"], S["avoid_buy_total"]),
       13, ink2, None, align="CENTER", features="tnum")
y += 30
B.footer(d, X, y, CW, "receipt", align="CENTER")
B.tlab(d, tf, "fiction", X, y + 26, CW, 20, D["brand"]["fiction_notice"], 11, ink3,
       None, align="CENTER")

dsl = d.dsl()
(OUT / ("case-04-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-04", len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
print("last y =", y + 46, "of", H)
