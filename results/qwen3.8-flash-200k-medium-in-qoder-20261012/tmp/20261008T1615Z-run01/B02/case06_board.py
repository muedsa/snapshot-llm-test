"""B02 case-06 社区招募海报 1080x1620（A2，贴在菜鸟驿站门口）。

设计任务：路过的人只有 5 秒。所以海报只允许一次呼吸——一句价值、三个数字、
一个可以立刻扫/记下的入口；其余（会费、类目、Safety 101）是给停下来的人看的
第二层。估算类数字必须写清估算口径，不能把模型推的数当成年报里的真实计数。
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
BR = D["brand"]
RU = BR["rules"]
CATS = D["cats"]
W, H = 1080, 1620
M = 72
CW = W - 2 * M
OUT = root / "tmp" / rid / "B02" / "case-06"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")

tf = TextFit()
d = B.paper_doc(W, H, dark=False, noise=16, seed=23)
t0, t1, t2 = d.P["t0"], d.P["t1"], d.P["t2"]
INK, ORANGE = P["ink"], P["orange"]
SOFT = B.blend(P["ink"], 0.07, P["paper"])

# ---------------- 品牌行 ----------------
B.brand_mark(d, M + 26, 74, 26, color=ORANGE, ink=P["paper"], bg=P["paper"])
B.tlab(d, tf, "b-name", M + 66, 52, 320, 44, BR["name"], 34, INK, "BOLD")
B.tlab(d, tf, "b-en", M + 66, 96, 320, 22, BR["en"], 14, P["ink3"], None)
B.tlab(d, tf, "b-where", W - M - 420, 62, 420, 40, "社区工具馆 · 白鹤岭 / 望江驿两处取还",
       17, P["ink2"], None, align="END")
d.rect(M, 128, CW, 2, B.blend(P["ink"], 0.22, P["paper"]))

# ---------------- 主口号（5 秒层） ----------------
tag = BR["tagline"]  # 借一次，胜过买十次
l1, l2 = tag.split("，")
# 150px 下的中文全角逗号会糊成一坨墨块（v01 看图），两行口号之间已靠换行断开
B.tlab(d, tf, "hero1", M, 168, CW, 168, l1, 150, INK, "BOLD")
B.tlab(d, tf, "hero2", M, 340, CW, 168, l2, 150, ORANGE, "BOLD")
B.tlab(d, tf, "sub", M, 522, CW, 34,
       "把只用一次的工具留在馆里：年卡 ¥%d 起，无押金，借出不再收费。"
       % RU["member_fee"]["个人年卡"], 26, P["ink2"], None)

# ---------------- 三个数字（第二眼层） ----------------
y = 592
stats = [
    ("%d 件" % S["avoid_buy_total"], "少重复购买",
     "按各类目「一次性用途」比例从 %d 次借阅中折算，是估算不是销量" % S["total_loans"]),
    ("%.1f 吨" % (S["kg_saved_total"] / 1000.0), "少造的机器",
     "同一折算下按整机自重累计，不含配件与耗材"),
    ("%d 次" % S["total_loans"], "真实借出",
     "2025 全年借阅台账计数，%d 位会员人均 %.2f 次" % (S["members"], S["loans_per_member"])),
]
bw, gap = 296, 24
for i, (big, lab, note) in enumerate(stats):
    x = M + i * (bw + gap)
    d.rect(x, y, bw, 196, SOFT, radius=8)
    d.rect(x, y, bw, 5, ORANGE if i == 0 else B.blend(ORANGE, 0.35, P["paper"]))
    B.tlab(d, tf, "st%d" % i, x + 22, y + 26, bw - 44, 66, big, 56, INK, "BOLD",
           features="tnum")
    B.tlab(d, tf, "st%d-l" % i, x + 22, y + 100, bw - 44, 28, lab, 22, ORANGE, "BOLD")
    B.tlab(d, tf, "st%d-n" % i, x + 22, y + 132, bw - 44, 56, note, 14, P["ink3"], None,
           lines=3)

# ---------------- 怎么开始（左）+ 入口卡（右） ----------------
y = 838
LW = 604
B.section_head(d, M, y, LW, 1, "三步借到第一台机器", dark=False, size=24)
steps = [
    ("办卡", "白鹤岭馆服务台办理，%d 元一年；无押金。" % RU["member_fee"]["个人年卡"]),
    ("上 Safety 101", "借电动 / 气动工具前须先通过的一课，%d 分钟，在主馆公共工坊。"
     % RU["safety_101_min"]),
    ("借 %d 件 · 还 %d 天" % (RU["max_active"], RU["loan_days"]),
     "单次最多 %d 件、借期 %d 天，可续借一次 %d 天；逾期 ¥%g/件·天。"
     % (RU["max_active"], RU["loan_days"], RU["renew_days"], RU["late_fee_per_day"])),
]
sy = y + 46
for i, (h, b) in enumerate(steps):
    B.hex_chip(d, M + 15, sy + 17, 15, P["steel"], "%d" % (i + 1), size=15,
               ink=P["paper"])
    B.tlab(d, tf, "sp%d" % i, M + 42, sy, LW - 42, 30, h, 24, INK, "BOLD")
    B.tlab(d, tf, "sp%d-b" % i, M + 42, sy + 32, LW - 42, 26, b, 17, P["ink2"], None)
    sy += 66

# 会费三档
sy += 6
B.tlab(d, tf, "fee-h", M, sy, LW, 26, "会费（年缴，无押金）", 19, INK, "BOLD")
sy += 34
# 档位顺序按「先看到入门价」排，不按价格降序：v01 降序把 ¥260 摆在「年卡 ¥180 起」
# 这句话下面，自相矛盾
FEE_NOTE = {"个人年卡": "个人使用", "家庭年卡": "家庭共用", "志愿年卡(免费)": "志愿者"}
fees = ["个人年卡", "家庭年卡", "志愿年卡(免费)"]
for i, k in enumerate(fees):
    v = RU["member_fee"][k]
    d.rect(M, sy, LW, 44, B.blend(P["ink"], 0.045, P["paper"]), radius=6)
    B.tlab(d, tf, "fee%d-n" % i, M + 16, sy + 11, 300, 24,
           k.replace("(免费)", ""), 19, INK, "BOLD")
    B.tlab(d, tf, "fee%d-p" % i, M + 320, sy + 9, 150, 28,
           "¥%d" % v if v else "免费", 22, ORANGE, "BOLD", align="END",
           features="tnum")
    B.tlab(d, tf, "fee%d-d" % i, M + 484, sy + 14, LW - 500, 22, FEE_NOTE[k], 14,
           P["ink3"], None, align="END")
    sy += 48
B.tlab(d, tf, "fee-all", M, sy + 4, LW, 22,
       "三档均含：无押金 · 同时借出 %d 件 · 借出不再收费" % RU["max_active"], 15,
       P["ink2"], None)
sy += 34

# 入口卡：二维码 + 地址电话
QX, QY, QW = M + LW + 32, 838, CW - LW - 32
d.rect(QX, QY, QW, 428, B.blend(P["ink"], 0.9, P["paper"]), radius=10)
B.tlab(d, tf, "q-h", QX + 24, QY + 24, QW - 48, 30, "线上看馆", 24, P["paper"], "BOLD")
B.tlab(d, tf, "q-s", QX + 24, QY + 60, QW - 48, 24, "今天哪些工具在馆", 16,
       B.blend(P["white"], 0.62, P["dark"]), None)
B.tlab(d, tf, "q-s2", QX + 24, QY + 84, QW - 48, 24, "本周开放工坊报名", 16,
       B.blend(P["white"], 0.62, P["dark"]), None)
d.rect(QX + 24, QY + 118, QW - 48, 210, P["paper"], radius=6)
B.qr_placeholder(d, QX + (QW - 176) / 2, QY + 135, 176, "wrench-house-join",
                 fg=P["ink"], bg=P["paper"], n=21)
# 二维码是版面占位图形，标题就不能写「扫这里」——那会让读者以为扫了能到某处
B.tlab(d, tf, "q-note", QX + 24, QY + 338, QW - 48, 22, "占位图形，暂不可扫描", 13,
       B.blend(P["white"], 0.45, P["dark"]), None, align="CENTER")
B.tlab(d, tf, "q-tel", QX + 24, QY + 366, QW - 48, 26, "电话 %s" % BR["phone"], 18,
       P["paper"], "BOLD", features="tnum")
B.tlab(d, tf, "q-hrs", QX + 24, QY + 396, QW - 48, 22, "%s %s–%s"
       % (BR["hours"]["days"], BR["hours"]["open"], BR["hours"]["close"]), 14,
       B.blend(P["white"], 0.6, P["dark"]), None, features="tnum")

B.tlab(d, tf, "q-prog", QX + 4, QY + 442, QW, 22, "常设：%s · %s"
       % (BR["programs"][2], BR["programs"][3]), 14, P["ink3"], None)

# ---------------- 类目条（第三层） ----------------
# 位置由左右两栏的实际底边推出，不写死：v01 自查发现写死 1300 会与左栏会费块重叠
y = max(sy, QY + 428) + 34
assert y + 260 < H - 20, "底部放不下：类目条 + 页脚超出画布"
B.section_head(d, M, y, CW, 2, "馆内 9 类 %d 件工具" % len(D["tools"]), dark=False, size=24)
cy = y + 44
cw_ = (CW - 8 * 12) / 9.0
for i, c in enumerate(CATS):
    x = M + i * (cw_ + 12)
    col = B.cat_color(c["code"])
    d.rect(x, cy, cw_, 6, col)
    B.tlab(d, tf, "c%d" % i, x - 6, cy + 16, cw_ + 12, 40, c["name"], 15, INK, "BOLD",
           align="CENTER", lines=2)
    B.tlab(d, tf, "c%d-n" % i, x - 6, cy + 62, cw_ + 12, 24, "%d 件" % c["count"], 15,
           P["ink3"], None, align="CENTER", features="tnum")
    B.tlab(d, tf, "c%d-z" % i, x - 6, cy + 86, cw_ + 12, 22, "%s 区" % c["zone"],
           13, col, "BOLD", align="CENTER")

ay = cy + 118
B.tlab(d, tf, "addr", M, ay, CW, 26,
       "%s · %s · 周一%s" % (BR["sites"][0], BR["sites"][1], BR["hours"]["closed_note"]),
       17, P["ink2"], None)

B.footer(d, M, ay + 54, CW, "full")

dsl = d.dsl()
(OUT / ("case-06-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-06", len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
print("left col ends", round(sy), "qr ends", QY + 428, "footer ends", round(ay + 54 + 44),
      "of", H)
