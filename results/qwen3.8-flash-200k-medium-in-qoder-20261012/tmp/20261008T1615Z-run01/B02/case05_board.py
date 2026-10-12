"""B02 case-05 手机推送与到期提醒 750x1624（iOS 锁屏 + 通知中心）。

设计任务：逾期这件事只有在小屏幕上被看见才会真的被处理。锁屏是用户唯一
一定会看到的界面，所以这张图的重点不是「好看」，而是通知文案在三行内
把「哪件、欠几天、多少钱、下一步能点什么」说完，并且诚实标出续借已经用尽。
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
W, H = 750, 1624
OUT = root / "tmp" / rid / "B02" / "case-05"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")
TODAY = datetime.date.fromisoformat(RU["today"])
WK = "一二三四五六日"[TODAY.weekday()]
HD = D["brand"]["hours"]
LATE = [l for l in AL if l["overdue_days"]][0]
OK = [l for l in AL if not l["overdue_days"]]

tf = TextFit()
d = B.paper_doc(W, H, dark=True, noise=0)
# 锁屏底：满幅方块噪点在 750px 宽上像压缩残骸（v01 看图），换成极窄的竖向渐变壁纸
B.gradient_bands(d, W, H, "#1D2024", "#101215", band=20)
t0, t1, t2 = d.P["t0"], d.P["t1"], d.P["t2"]
CARD = B.blend(P["white"], 0.085, P["dark"])
CARD2 = B.blend(P["white"], 0.05, P["dark"])
EDGE = B.blend(P["white"], 0.16, P["dark"])

# ---------------- 状态栏 ----------------
B.tlab(d, tf, "st-time", 40, 34, 120, 30, "09:41", 22, t0, "BOLD", features="tnum")
for i in range(4):
    d.rect(W - 200 + i * 12, 52 - (6 + i * 4), 8, 6 + i * 4, t1)
B.tlab(d, tf, "st-net", W - 150, 36, 44, 24, "5G", 17, t1, "BOLD")
d.rect(W - 96, 38, 46, 22, B.blend(P["white"], 0.28, P["dark"]), radius=6)
d.rect(W - 92, 42, 30, 14, B.lighten(P["green"], 0.30), radius=4)
d.rect(W - 48, 44, 4, 10, B.blend(P["white"], 0.28, P["dark"]))

# ---------------- 时钟 ----------------
B.tlab(d, tf, "clock", 40, 118, 670, 116, "09:41", 108, t0, "BOLD",
       align="CENTER", features="tnum")
B.tlab(d, tf, "date", 40, 240, 670, 34, "%d月%d日 星期%s" % (TODAY.month, TODAY.day, WK),
       24, t1, None, align="CENTER")
B.tlab(d, tf, "lock", 40, 286, 670, 24, "Face ID 解锁后即可查看全部在借", 15, t2,
       None, align="CENTER")


def icon(x, y, s=46):
    d.rect(x, y, s, s, B.lighten(P["orange"], 0.12), radius=s * 0.24)
    B.brand_mark(d, x + s / 2, y + s / 2, s * 0.30, color=P["ink"],
                 ink=P["ink"], bg=B.lighten(P["orange"], 0.12))


def card(x, y, w, h, bg=None):
    d.rect(x, y, w, h, bg or CARD, radius=26)
    # 高光细线必须按圆角内缩：v02 放大后能看到线头伸出圆角外，像一条悬空的边
    d.rect(x + 26, y, w - 52, 1, B.blend(P["white"], 0.10, P["dark"]))


# ---------------- 通知 1：逾期（展开） ----------------
y = 344
card(30, y, 690, 404)
icon(56, y + 26)
B.tlab(d, tf, "n1-app", 116, y + 30, 300, 26, "扳手屋", 20, t1, "BOLD")
B.tlab(d, tf, "n1-time", 400, y + 32, 294, 24, "现在 · 推送", 15, t2, None,
       align="END")
B.tlab(d, tf, "n1-title", 56, y + 92, 618, 40, "角磨机已逾期 %d 天"
       % LATE["overdue_days"], 32, B.lighten(P["red"], 0.34), "BOLD")
B.tlab(d, tf, "n1-body", 56, y + 140, 618, 30,
       "应还 %s · 逾期费 ¥%g/件·天 × %d 天 = 应计 ¥%g"
       % (B.date_cn(LATE["due"]), RU["late_fee_per_day"], LATE["overdue_days"],
          LATE["late_fee"]), 20, t0, None, features="tnum")
B.tlab(d, tf, "n1-body2", 56, y + 174, 618, 28,
       "额度 %d/%d 件已满 · %s" % (len(AL), RU["max_active"], LATE["note"]),
       17, t2, None, features="tnum")
# 两个动作：一个可用、一个诚实标灰
bx = 56
d.rect(bx, y + 214, 300, 52, B.lighten(P["green"], 0.16), radius=26)
B.tlab(d, tf, "n1-a1", bx, y + 226, 300, 28, "查看归还时间窗", 20, P["paper"],
       "BOLD", align="CENTER")
bx = 374
d.rect(bx, y + 214, 300, 52, CARD2, radius=26)
B.tlab(d, tf, "n1-a2", bx, y + 226, 300, 28, "续借（本件已用尽）", 18,
       B.blend(P["white"], 0.26, P["dark"]), None, align="CENTER")
# v01 在这里画了一条横穿整颗按钮的删除线，线头伸出圆角外，读成渲染故障；
# 不可用的 iOS 惯例是只把文字压暗，不划线。
# 展开的时间窗
d.rect(56, y + 288, 618, 1, d.P["line"])
B.tlab(d, tf, "n1-win", 56, y + 300, 618, 26, "归还时间窗", 17, t1, "BOLD")
B.tlab(d, tf, "n1-win1", 56, y + 328, 618, 26, "%s %s–%s（%s）"
       % (HD["days"], HD["open"], HD["close"], HD["closed_note"]), 17, t2, None)
B.tlab(d, tf, "n1-win2", 56, y + 356, 618, 26, "%s · 另一个取还点：%s"
       % (RU["return_point"], D["brand"]["sites"][1]), 17, t2, None)

# ---------------- 通知 2/3：到期提醒 ----------------
y = 768
for i, l in enumerate(OK):
    card(30, y, 690, 116, CARD if i == 0 else CARD2)
    icon(56, y + 20, 40)
    B.tlab(d, tf, "n%d-app" % i, 110, y + 22, 320, 24, "扳手屋 · 到期提醒", 16, t1,
           None)
    B.tlab(d, tf, "n%d-time" % i, 430, y + 22, 264, 24, "%d 小时前" % (i + 3), 14,
           t2, None, align="END")
    B.tlab(d, tf, "n%d-title" % i, 110, y + 52, 584, 28,
           "%s 还有 %d 天应还（%s）" % (l["name"], l["days_left"], B.date_md(l["due"])),
           21, t0, "BOLD")
    B.tlab(d, tf, "n%d-body" % i, 110, y + 82, 584, 24,
           "可续借一次至 %s · 编号 %s" % (B.date_md(l["due_after_renew"]), l["tool"]),
           15, t2, None, features="tnum")
    y += 132

# ---------------- 通知 4：活动 ----------------
card(30, y, 690, 116, CARD2)
icon(56, y + 20, 40)
B.tlab(d, tf, "n4-app", 110, y + 22, 320, 24, "扳手屋 · 本周活动", 16, t1, None)
B.tlab(d, tf, "n4-time", 430, y + 22, 264, 24, "昨天 18:02", 14, t2, None,
       align="END")
B.tlab(d, tf, "n4-title", 110, y + 52, 584, 28, "%s：%s"
       % (D["brand"]["programs"][0].split(" · ")[0], D["brand"]["programs"][0].split(" · ")[1]),
       21, t0, "BOLD")
B.tlab(d, tf, "n4-body", 110, y + 82, 584, 24, "带上坏掉的家电，馆内公共工坊见 · "
       "常设还有：%s" % D["brand"]["programs"][1], 15, t2, None)
y += 148

# ---------------- 在借清单 ----------------
B.tlab(d, tf, "list-h", 40, y, 400, 28, "在借 %d 件 · 额度已满" % len(AL), 20, t0,
       "BOLD")
B.tlab(d, tf, "list-h2", 40, y + 30, 670, 24, "下拉通知中心可查看全部 · 点编号可跳到架位",
       15, t2, None)
y += 64
for i, l in enumerate(AL):
    late = l["overdue_days"] > 0
    d.rect(40, y, 670, 62, CARD2, radius=16)
    col = B.lighten(P["red"], 0.34) if late else B.cat_color(l["cat"], dark=True)
    d.rect(40, y, 5, 62, col)
    B.tlab(d, tf, "li%d" % i, 62, y + 8, 300, 26, l["name"], 19, t0, "BOLD")
    B.tlab(d, tf, "li%d-id" % i, 62, y + 34, 300, 22, l["tool"], 13, t2, None,
           features="tnum")
    B.tlab(d, tf, "li%d-d" % i, 360, y + 8, 330, 26,
           "逾期 %d 天" % l["overdue_days"] if late else "还剩 %d 天" % l["days_left"],
           17, col if late else t1, "BOLD" if late else None, align="END",
           features="tnum")
    B.tlab(d, tf, "li%d-e" % i, 360, y + 34, 330, 22,
           "应还 %s · %s" % (l["due"], "¥%g" % l["late_fee"] if late else "无欠费"),
           13, t2, None, align="END", features="tnum")
    y += 72
y += 10
# v01 写过「逾期中只有你这一件」——全馆 overdue_loans 是 %d 件，属于编造，删掉。
B.tlab(d, tf, "tip", 40, y, 670, 26, "今天全馆 %d 件在借、%d 件可借；归还角磨机后你的额度可恢复 1 件。"
       % (S["in_borrow_now"], S["available_now"]), 15, t2, None, features="tnum")

# ---------------- 底部 ----------------
d.rect(W / 2 - 74, H - 44, 148, 6, B.blend(P["white"], 0.5, P["dark"]), radius=3)
B.footer(d, 40, H - 108, 670, "micro", dark=True)
B.tlab(d, tf, "fiction", 40, H - 82, 670, 22, D["brand"]["fiction_notice"], 12,
       B.blend(P["white"], 0.34, P["dark"]), None, align="CENTER")

dsl = d.dsl()
(OUT / ("case-05-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-05", len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
print("last y =", round(y + 26), "of", H)
