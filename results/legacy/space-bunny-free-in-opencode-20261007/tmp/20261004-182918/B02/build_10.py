# -*- coding: utf-8 -*-
"""B02 case-10 - 三折页《借还须知》, 1654x1169 (A4 landscape, 4 panels).

Touchpoint: handed across the counter at the moment of sign-up, then folded into a
pocket and re-read at the pickup cabinet a week later. Task: answer "can I take it,
for how long, what happens if I'm late" without needing a member of staff.

Format decision: 4 panels of 413.5 px each. Panel 1 is the cover and the price
(the only thing you must remember), panels 2-4 are the rules, in the order the
questions actually arrive: how to take it out, how to bring it back, when the place
is open. Fold lines are drawn as dashed rules because the DSL has no dashed border
(verified against the service guide), and each panel carries its own footer so a
folded panel is still identifiable.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402
import data as DA  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 1654, 1169
PW = W / 4.0
PAD = 34
k = []
k.append(D.box(0, 0, W, H, color=G.WHITE))
k.append(D.box(0, 0, PW, H, color=G.IRON_D))

# fold lines (dashed: the DSL has no dashed border)
for i in (1, 2, 3):
    fx = PW * i
    for yy in range(0, H, 22):
        k.append(D.box(fx, yy, 1.5, 12, color="#C9C1AFB0"))

# ================================================================ panel 1 cover
X = PAD
k.append(D.text_el("百工社", x=X, y=44, w=240, h=56, size=42, color=G.WHITE,
                   font=G.FONT_CJK, style="BOLD", ls=2.4, max_lines=1))
k.append(D.text_el("BAIGONG TOOL LIBRARY", x=X, y=104, w=300, h=20, size=12,
                   color=G.BRASS, font=G.FONT, ls=1.6, max_lines=1))
k.append(D.box(X, 140, 80, 4, color=G.RUST))
k.append(D.text_el("借还须知", x=X - 2, y=176, w=PW - 2 * PAD, h=92, size=68,
                   color=G.WHITE, font=G.FONT_CJK, style="BOLD", ls=3, max_lines=1))
k.append(D.text_el("把该买一次的，变成借一次。", x=X, y=278, w=PW - 2 * PAD, h=34,
                   size=19, color="#A9BDCCFF", font=G.FONT_CJK, max_lines=1))

k.append(D.text_el("会 员 费", x=X, y=352, w=200, h=22, size=14, color=G.BRASS,
                   font=G.FONT_CJK, ls=2, max_lines=1))
k.append(D.text_el("¥10", x=X - 4, y=378, w=180, h=76, size=60, color=G.WHITE,
                   font=G.FONT, style="BOLD", max_lines=1))
k.append(D.text_el("每月，或 ¥90 一年", x=X + 176, y=414, w=200, h=24, size=16,
                   color="#8FA6B7FF", font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("免押金　·　不收年费之外的钱", x=X, y=458, w=PW - 2 * PAD, h=24,
                   size=15, color=G.BRASS, font=G.FONT_CJK, style="BOLD",
                   max_lines=1))

k.append(D.hline(X, PW - PAD, 506, "#3C5872FF", 1))
k.append(D.text_el("本月主推", x=X, y=522, w=200, h=24, size=15, color=G.BRASS,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
PROMO = [("手持电钻 12V", "T-0412"), ("人字梯 2.4m", "T-0704"),
         ("激光测距仪", "T-0301"), ("台式缝纫机", "T-0915")]
py = 558
for nm, tid in PROMO:
    k.append(G.dot(X + 7, py + 8, 5, G.BRASS))
    k.append(D.text_el(nm, x=X + 22, y=py - 1, w=200, h=22, size=16,
                       color="#D8CFBEFF", font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(tid, x=PW - PAD - 90, y=py + 1, w=90, h=20, size=13,
                       color="#7E93A6FF", font=G.FONT_MONO, align="RIGHT",
                       max_lines=1))
    py += 30
k.append(D.text_el("在库 %d 件 · 编号 T-0001 至 T-1240" % DA.IN_STOCK, x=X, y=py + 8,
                   w=PW - 2 * PAD, h=22, size=14, color="#8FA6B7FF",
                   font=G.FONT_CJK, max_lines=1))

k.append(D.box(X, H - 132, PW - 2 * PAD, 1, color="#3C5872FF"))
k.append(D.text_el("沿河路 12 号 · 新华里街道社区服务中心 1 层", x=X, y=H - 116,
                   w=PW - 2 * PAD, h=44, size=14, color="#A9BDCCFF",
                   font=G.FONT_CJK, max_lines=2))
k.append(D.text_el(DA.TEL, x=X, y=H - 62, w=PW - 2 * PAD, h=30, size=22,
                   color=G.BRASS, font=G.FONT_MONO, style="BOLD", max_lines=1))

# ================================================================ panel 2 borrow
def panel_head(pi, idx, title, sub):
    x = PW * pi + PAD
    y = 44
    k.append(D.text_el(idx, x=x, y=y, w=60, h=26, size=15, color=G.RUST,
                       font=G.FONT_MONO, style="BOLD", ls=1.4, max_lines=1))
    k.append(D.text_el(title, x=x, y=y + 30, w=PW - 2 * PAD, h=56, size=42,
                       color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(sub, x=x, y=y + 92, w=PW - 2 * PAD, h=24, size=15,
                       color=G.MUTE, font=G.FONT_CJK, max_lines=1))
    k.append(D.hline(x, x + PW - 2 * PAD, y + 128, G.LINE2, 1))
    return y + 150


def steps(x, y, items, *, num_color=G.RUST, size=17, sub_size=14, pitch=None):
    for i, (t, s) in enumerate(items):
        k.append(D.text_el("%02d" % (i + 1), x=x, y=y, w=44, h=24, size=13,
                           color=num_color, font=G.FONT_MONO, style="BOLD",
                           max_lines=1))
        k.append(D.text_el(t, x=x + 44, y=y - 2, w=PW - 2 * PAD - 44, h=24, size=size,
                           color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
        k.append(D.text_el(s, x=x + 44, y=y + 24, w=PW - 2 * PAD - 44, h=40,
                           size=sub_size, color=G.MUTE, font=G.FONT_CJK,
                           max_lines=2))
        y += pitch or 62
    return y


def bullets(x, y, items, *, color=G.PINE, size=15, pitch=32):
    for t in items:
        k.append(G.dot(x + 7, y + 9, 5, color))
        k.append(D.text_el(t, x=x + 24, y=y - 1, w=PW - 2 * PAD - 24, h=24,
                           size=size, color=G.INK2, font=G.FONT_CJK, max_lines=1))
        y += pitch
    return y


x2 = PW * 1 + PAD
y2 = panel_head(1, "P2", "怎么借", "五步，全程不超过十分钟")
y2 = steps(x2, y2, [
    ("带上这张纸，到主站", "自助柜与宿舍区站点不办卡"),
    ("报会员号或手机尾号", "新会员先填一张表，2 分钟"),
    ("看工具墙上的标签", "绿=在架可借　琥珀=校中　锈红=已借出"),
    ("扫码开门，取走工具", "当场拍照留档，不需要押金"),
    ("核对期限，签退", "默认 7 天，可在柜上改"),
])
k.append(D.box(x2, y2 + 6, PW - 2 * PAD, 118, color=G.PINE_L, radius=4))
k.append(D.text_el("借期怎么算", x=x2 + 16, y=y2 + 20, w=200, h=24, size=15,
                   color=G.PINE, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("普通工具 7 天，可再续 7 天一次。", x=x2 + 16, y=y2 + 48,
                   w=PW - 2 * PAD - 32, h=24, size=14, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("登高与电气类 3 天，且须年满 18 周岁。", x=x2 + 16, y=y2 + 74,
                   w=PW - 2 * PAD - 32, h=24, size=14, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("第 52 场修理夜后：到期日顺延 7 天。", x=x2 + 16, y=y2 + 100,
                   w=PW - 2 * PAD - 32, h=24, size=14, color=G.RUST,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
y2b = y2 + 148
k.append(D.text_el("不收押金，但要说清三件事", x=x2, y=y2b, w=PW - 2 * PAD, h=24,
                   size=15, color=G.INK, font=G.FONT_CJK, style="BOLD",
                   max_lines=1))
bullets(x2, y2b + 30, ["工具是谁的、你会用它做什么", "家里有没有梯子或工作台",
                       "怎么联系到你（电话或门牌）"])

# ================================================================ panel 3 return
x3 = PW * 2 + PAD
y3 = panel_head(2, "P3", "怎么还", "三个地方都能还")
y3 = steps(x3, y3, [
    ("原路还回同一个柜", "24 小时自助，最晚 21:00"),
    ("清洁后再还", "泥、油、胶带请先擦掉"),
    ("坏的也还", "贴一张纸说明现象即可"),
], pitch=72)
k.append(D.box(x3, y3 + 4, PW - 2 * PAD, 140, color=G.RUST_L, radius=4))
k.append(D.text_el("逾期待还", x=x3 + 16, y=y3 + 18, w=200, h=24, size=15,
                   color=G.RUST, font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("¥1 / 天，直接计入下月借用额度。", x=x3 + 16, y=y3 + 46,
                   w=PW - 2 * PAD - 32, h=24, size=14, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("连续逾期待还 14 天，暂停借用 1 个月。", x=x3 + 16, y=y3 + 72,
                   w=PW - 2 * PAD - 32, h=24, size=14, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("全年逾期待还仅 %d 件次，占借出 %.1f%%。"
                   % (DA.OVERDUE, DA.OVERDUE_RATE * 100),
                   x=x3 + 16, y=y3 + 98, w=PW - 2 * PAD - 32, h=24, size=14,
                   color=G.RUST, font=G.FONT_CJK, style="BOLD", max_lines=1))
y3b = y3 + 168
k.append(D.text_el("弄丢了怎么办", x=x3, y=y3b, w=PW - 2 * PAD, h=24, size=15,
                   color=G.INK, font=G.FONT_CJK, style="BOLD", max_lines=1))
bullets(x3, y3b + 30, ["立刻打电话，说明最后一次见到的位置",
                       "按购置价分摊，不按零售价",
                       "人找不到也没关系，先登记"], color=G.INK2)

# ================================================================ panel 4 open
x4 = PW * 3 + PAD
y4 = panel_head(3, "P4", "什么时候来", "三个点，三种时间")
for i, (nm, ad, hr, gl) in enumerate(DA.PICKUPS):
    yy = y4 + i * 92
    k.append(D.box(x4, yy, 6, 76, color=[G.IRON, G.BRASS, G.PINE][i]))
    k.append(D.text_el(nm, x=x4 + 18, y=yy, w=200, h=26, size=18, color=G.INK,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(ad, x=x4 + 18, y=yy + 28, w=PW - 2 * PAD - 18, h=22, size=13,
                       color=G.INK2, font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(hr, x=x4 + 18, y=yy + 50, w=PW - 2 * PAD - 18, h=22, size=13,
                       color=[G.IRON, G.BRASS, G.PINE][i], font=G.FONT_CJK,
                       style="BOLD", max_lines=1))
y4b = y4 + 3 * 92 + 16
k.append(D.hline(x4, x4 + PW - 2 * PAD, y4b, G.LINE2, 1))
k.append(D.text_el("每周三 19:00-21:30 修理夜", x=x4, y=y4b + 16, w=PW - 2 * PAD,
                   h=26, size=17, color=G.INK, font=G.FONT_CJK, style="BOLD",
                   max_lines=1))
k.append(D.text_el("带坏掉的来，不用预约，来了排号。修不好的当场登记原因。",
                   x=x4, y=y4b + 46, w=PW - 2 * PAD, h=44, size=14, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=2))
k.append(D.text_el("每月两期新手课　6-12 人一节", x=x4, y=y4b + 96, w=PW - 2 * PAD,
                   h=26, size=17, color=G.INK, font=G.FONT_CJK, style="BOLD",
                   max_lines=1))
k.append(D.text_el("从换灯泡一路学到修自行车，材料费自负。", x=x4, y=y4b + 124,
                   w=PW - 2 * PAD, h=24, size=14, color=G.MUTE, font=G.FONT_CJK,
                   max_lines=1))

# panel footers
for pi in range(1, 4):
    fx = PW * pi + PAD
    fy = H - 74
    k.append(D.hline(fx, fx + PW - 2 * PAD, fy, G.LINE, 1))
    k.append(D.text_el("百工社 · 借还须知 第 %d / 4 折" % (pi + 1), x=fx, y=fy + 14,
                       w=PW - 2 * PAD, h=20, size=11, color=G.FAINT,
                       font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(DA.SITE_SHORT, x=fx, y=fy + 14, w=PW - 2 * PAD, h=20,
                       size=11, color=G.FAINT, font=G.FONT_CJK, align="RIGHT",
                       max_lines=1))

dsl = G.snapshot(k, W, H, bg=G.WHITE)
G.show(dsl, "case-10 tri-fold leaflet 1654x1169")

with open(os.path.join(TMP, "drafts", "case-10.v01.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-10")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
