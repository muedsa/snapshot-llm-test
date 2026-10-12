"""B02 case-01 门头与橱窗主画面 2400x900。

设计任务：店外 3 米、2 秒内读懂「这是一家可以借工具的店」，并带走三条硬规则。
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

W, H = 2400, 900
tf = TextFit()
P = B.P
S = B.summary()
CATS = B.DATA["cats"]
TOOLS_TOTAL = sum(c["count"] for c in CATS)
M = 90
d = B.paper_doc(W, H, noise=22)

# ---------- 左：标志 ----------
B.brand_mark(d, 390, 400, 235, bg=P["paper"])

# ---------- 中：店名与一句话定义 ----------
x0 = 760
B.tlab(d, tf, "brand", x0, 120, 900, 220, "扳手屋", 190, P["ink"], "BOLD", lines=1)
B.tlab(d, tf, "brand-en", x0 + 4, 352, 900, 44, "WRENCH HOUSE · TOOL LIBRARY", 32,
       P["orange"], "BOLD", features="tnum")
d.rect(x0, 412, 1120, 2, d.P["line"])
B.tlab(d, tf, "tagline", x0, 436, 1120, 76, "借一次，胜过买十次。", 54, P["ink"],
       "BOLD")
B.tlab(d, tf, "define", x0, 522, 1120, 34,
       "社区工具图书馆 · 馆藏 %d 件 · %d 大库区 · %d 位会员 · 全年借出 %s 次"
       % (TOOLS_TOTAL, len(CATS), S["members"], S["total_loans"]),
       26, P["ink2"], None)
RU = B.DATA["brand"]["rules"]
HD = B.DATA["brand"]["hours"]
MF = RU["member_fee"]
B.tlab(d, tf, "hours", x0, 566, 1120, 30,
       "开放时间 %s %s–%s（%s） · %s" % (HD["days"], HD["open"], HD["close"],
                                    HD["closed_note"], RU["return_point"]),
       22, P["ink3"], None)

# ---------- 右：三条硬规则 ----------
rx, rw = 1930, 380
rules = [
    ("¥%d" % MF["个人年卡"], "个人年费 / 家庭 ¥%d" % MF["家庭年卡"],
     "无押金 · 借出不另收费" if RU["deposit"] == 0 else "押金 ¥%d" % RU["deposit"],
     P["orange"]),
    ("%d 天" % RU["loan_days"], "标准借期 · 可续借 %d 天" % RU["renew_days"],
     "同时在借最多 %d 件" % RU["max_active"], P["steel"]),
    ("免费", "维修保养归馆方",
     "会员保养课 · Safety 101", P["green"]),
]
for i, (big, l1, l2, c) in enumerate(rules):
    y = 118 + i * 158
    d.rect(rx, y, 6, 130, c)
    B.hex_chip(d, rx + 46, y + 34, 22, c, "%d" % (i + 1), bg=P["paper"])
    B.tlab(d, tf, "rule%d-big" % i, rx + 78, y + 2, rw - 78, 62, big, 50, P["ink"],
           "BOLD", features="tnum")
    B.tlab(d, tf, "rule%d-l1" % i, rx + 78, y + 68, rw - 78, 30, l1, 22, c, "BOLD")
    B.tlab(d, tf, "rule%d-l2" % i, rx + 78, y + 100, rw - 78, 26, l2, 20, P["ink2"])

# ---------- 底部：馆藏类目刻度带（品牌结构语言：一切比例都用刻度尺） ----------
by, bh = 696, 26
bx, bw = M, W - 2 * M
acc = 0.0
for c in CATS:
    w = bw * c["count"] / TOOLS_TOTAL
    d.rect(bx + acc, by, w - 3, bh, B.cat_color(c["code"]), radius=3)
    acc += w
B.tlab(d, tf, "band-title", bx, by - 40, 520, 30,
       "馆藏构成 · 按件数", 22, P["ink"], "BOLD")
B.tlab(d, tf, "band-total", bx + bw - 300, by - 40, 300, 30,
       "%d 件 / %d 库区" % (TOOLS_TOTAL, len(CATS)), 22, P["ink3"], None, align="END",
       features="tnum")
acc = 0.0
for c in CATS:
    w = bw * c["count"] / TOOLS_TOTAL
    cx = bx + acc + w / 2
    d.rect(cx - 1, by + bh, 2, 12, d.P["line"])
    B.tlab(d, tf, "band-%s" % c["code"], cx - 62, by + bh + 14, 124, 22,
           c["name"], 17, P["ink2"], None, align="CENTER")
    B.tlab(d, tf, "band-%s-n" % c["code"], cx - 62, by + bh + 40, 124, 22,
           "%d 件" % c["count"], 17, P["ink3"], None, align="CENTER",
           features="tnum")
    acc += w

# ---------- 页脚 ----------
B.footer(d, M, H - 56, W - 2 * M, "full", dark=False)
d.rect(M, H - 72, W - 2 * M, 1, d.P["line"])

out = root / "tmp" / rid / "B02" / "case-01"
out.mkdir(parents=True, exist_ok=True)
dsl = d.dsl()
ver = os.environ.get("B02_VER", "v01")
(out / ("case-01-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print(out.name, len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:8]:
    print("  !", p)
