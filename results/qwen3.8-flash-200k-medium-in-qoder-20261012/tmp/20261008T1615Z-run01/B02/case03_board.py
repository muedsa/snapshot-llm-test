"""B02 case-03 馆内查询触摸屏 1920x1080（深色，站读 30 秒）。

设计任务：人到馆内要找一件工具在不在、在哪个架子。屏幕挂在过道边，
所以默认态就是「检索结果」而不是欢迎页：左边按库区筛，中间是命中列表，
右边是全馆实时库存。三块共用同一套类目色和刻度语言。
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
S = D["summary"]
RU = D["brand"]["rules"]
CATS = {c["code"]: c for c in D["cats"]}
PC = {c["code"]: c for c in S["per_cat"]}
W, H = 1920, 1080
OUT = root / "tmp" / rid / "B02" / "case-03"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")

QUERY = "钻"
HITS = [t for t in D["tools"] if QUERY in t["name"]]
HITS.sort(key=lambda t: t["id"])   # 按架位顺序：结果里同时出现三种状态
AVAIL = [t for t in HITS if t["state"] == "在馆"]

tf = TextFit()
d = B.paper_doc(W, H, dark=True, noise=20, seed=23)
t0, t1, t2 = d.P["t0"], d.P["t1"], d.P["t2"]

# ---------------- 顶栏 ----------------
B.brand_mark(d, 78, 62, 34, bg=P["dark"])
B.tlab(d, tf, "brand", 132, 30, 420, 44, "扳手屋 · 馆内查询", 30, t0, "BOLD")
B.tlab(d, tf, "brand2", 132, 76, 420, 22, "%s · 触摸屏 · 站着用"
       % D["brand"]["sites"][0].split("（")[0], 14, t2, None)
# 检索框
sx, sy, sw, sh = 600, 30, 640, 60
d.rect(sx, sy, sw, sh, B.blend(P["white"], 0.06, P["dark"]), radius=sh / 2)
B.hex_chip(d, sx + 34, sy + sh / 2, 15, P["orange"], "", ring=True,
           bg=B.blend(P["white"], 0.06, P["dark"]), dark=True)
B.tlab(d, tf, "q", sx + 60, sy + 14, 300, 34, "「%s」" % QUERY, 24, t0, "BOLD")
d.rect(sx + 60 + 62, sy + 16, 3, 28, B.lighten(P["orange"], 0.4))
B.tlab(d, tf, "q-hint", sx + 300, sy + 20, 320, 24, "也可以扫架位上的二维码", 14,
       t2, None)
B.tlab(d, tf, "top-right", 1280, 34, 600, 26, "%s · 在馆实时库存 每 5 分钟刷新"
       % B.date_cn(RU["today"]), 16, t1, None, align="END", features="tnum")
B.tlab(d, tf, "top-right2", 1280, 66, 600, 22, "登录：刷卡或扫码 · 未登录只能查不能借",
       13, t2, None, align="END")
d.rect(40, 108, W - 80, 1, d.P["line"])

# ---------------- 左：库区导航 ----------------
LX, LW = 40, 296
B.section_head(d, LX, 128, LW, 1, "按库区", "9 区 / 412 件", dark=True)
for i, c in enumerate(S["per_cat"]):
    y = 170 + i * 86
    col = B.cat_color(c["code"], dark=True)
    B.hex_chip(d, LX + 26, y + 22, 20, col, c["shelf_zone"], size=17, dark=True)
    B.tlab(d, tf, "nav%d" % i, LX + 58, y + 6, LW - 66, 30, c["name"], 21, t0,
           "BOLD")
    B.tlab(d, tf, "nav%d-n" % i, LX + 58, y + 38, LW - 66, 22,
           "%d 件 · 在借 %d" % (c["count"], c["tools_in_borrow"]), 14, t2, None,
           features="tnum")
    B.ruler(d, LX + 2, y + 66, LW - 4, c["tools_in_borrow"] / float(c["count"]),
            tone=col, h=6, ticks="compact", dark=True)

# ---------------- 中：检索结果 ----------------
CX, CW = 368, 872
B.tlab(d, tf, "res-h", CX, 128, CW - 200, 34, "检索「%s」· 命中 %d 件"
       % (QUERY, len(HITS)), 26, t0, "BOLD", features="tnum")
B.tlab(d, tf, "res-h2", CX, 168, CW, 24, "其中 %d 件现在可借 · 按架位顺序排列 · "
       "点状态可以只看可借" % len(AVAIL), 15, B.lighten(P["green"], 0.28), "BOLD")
cols = [("工具", 300), ("编号", 168), ("架位", 110), ("状态", 132), ("备注", 150)]
tx = CX
for name, w in cols:
    B.tlab(d, tf, "th-%s" % name, tx, 204, w, 22, name, 13, t2, "BOLD")
    tx += w
d.rect(CX, 230, CW, 1, d.P["line"])
for i, t in enumerate(HITS[:8]):
    y = 244 + i * 72
    if i % 2 == 0:
        d.rect(CX - 8, y - 8, CW + 8, 68, B.blend(P["white"], 0.035, P["dark"]))
    stc = {"在馆": P["green"], "在借": P["steel"], "维修中": P["greyblue"],
           "报废待处理": P["red"]}[t["state"]]
    stc = B.lighten(stc, 0.30)
    d.rect(CX, y + 2, 4, 44, B.cat_color(t["cat"], dark=True))
    B.tlab(d, tf, "r%d-name" % i, CX + 16, y, 290, 28, t["name"], 20, t0, "BOLD")
    B.tlab(d, tf, "r%d-cat" % i, CX + 16, y + 30, 290, 20,
           "%s · 安全等级 %s" % (t["cat_name"], t["safety_level"]), 13, t2, None)
    B.tlab(d, tf, "r%d-id" % i, CX + 300, y + 6, 168, 24, t["id"], 16, t1, None,
           features="tnum")
    B.tlab(d, tf, "r%d-zone" % i, CX + 468, y + 6, 100, 24, t["shelf"], 17, t1,
           None, features="tnum")
    B.pill(d, CX + 564, y + 2, 128, 34, t["state"], stc, 14, dark=True)
    note = ("可立即借出" if t["state"] == "在馆" else
            "下次保养 %s" % t["next_service"] if t["state"] == "维修中" else
            "已借出 · 可预约")
    B.tlab(d, tf, "r%d-note" % i, CX + 700, y + 8, 160, 24, note, 13, t2, None)
B.tlab(d, tf, "res-more", CX, 836, CW, 26, "还有 %d 件含「%s」· 点左侧库区可继续缩小范围"
       % (len(HITS) - 8, QUERY), 15, t2, None, features="tnum")
d.rect(CX, 872, CW, 1, d.P["line"])
# 借出三步
steps = [("查", "在架上扫码或问工作人员"), ("借", "服务台刷卡 · 一次最多 %d 件"
                                         % RU["max_active"]),
         ("还", "%s · 借期 %d 天" % (RU["return_point"], RU["loan_days"]))]
for i, (a, b) in enumerate(steps):
    x = CX + i * 300
    B.hex_chip(d, x + 22, 924, 22, P["orange"], "%d" % (i + 1), size=15, dark=True)
    B.tlab(d, tf, "step%d" % i, x + 54, 910, 240, 30, a, 22, t0, "BOLD")
    B.tlab(d, tf, "step%d-s" % i, x + 54, 942, 240, 40, b, 14, t1, None, lines=2)

# ---------------- 右：全馆实时 ----------------
RX, RW = 1272, 608
B.section_head(d, RX, 128, RW, 2, "全馆实时", "%d 件在册" % sum(c["count"] for c in D["cats"]),
              dark=True)
tiles = [("可借", S["available_now"], P["green"]), ("在借", S["in_borrow_now"], P["steel"]),
         ("维修中", S["in_repair_now"], P["greyblue"]),
         ("报废待处理", S["scrap_now"], P["red"])]
for i, (lab, val, col) in enumerate(tiles):
    x = RX + (i % 2) * 304
    y = 176 + (i // 2) * 116
    c = B.lighten(col, 0.30)
    d.rect(x, y, 288, 100, B.blend(c, 0.10, P["dark"]), radius=8)
    d.rect(x, y, 5, 100, c)
    B.tlab(d, tf, "tile%d-n" % i, x + 22, y + 10, 200, 56, "%d" % val, 44, t0,
           "BOLD", features="tnum")
    B.tlab(d, tf, "tile%d" % i, x + 22, y + 68, 240, 24, lab, 15, c, "BOLD")
# 库存构成条
tot = sum(c["count"] for c in D["cats"])
acc = 0.0
for st, col in (("在馆", P["green"]), ("在借", P["steel"]),
                ("维修中", P["greyblue"]), ("报废待处理", P["red"])):
    n = sum(1 for t in D["tools"] if t["state"] == st)
    w = RW * n / float(tot)
    d.rect(RX + acc, 418, max(2.0, w - 3), 18, B.lighten(col, 0.30), radius=4)
    acc += w
B.tlab(d, tf, "stock-note", RX, 446, RW, 22, "整条 = 全馆 %d 件；现在 %s 件可借，占 %s"
       % (tot, S["available_now"], B.pct(S["available_now"] / float(tot))), 14, t2,
       None, features="tnum")
B.section_head(d, RX, 492, RW, 3, "今年最热的库区", "按借出次数", dark=True)
top = sorted(S["per_cat"], key=lambda c: -c["loans_2025"])[:5]
mx = max(c["loans_2025"] for c in top)
for i, c in enumerate(top):
    y = 540 + i * 46
    B.tlab(d, tf, "hot%d" % i, RX, y, 150, 24, c["name"], 16, t1, None)
    B.ruler(d, RX + 158, y + 4, 300, c["loans_2025"] / float(mx),
            tone=B.cat_color(c["code"], dark=True), h=10, ticks="micro", dark=True)
    B.tlab(d, tf, "hot%d-n" % i, RX + 470, y, 130, 24, "%d 次" % c["loans_2025"], 15,
           t2, None, features="tnum")
B.section_head(d, RX, 786, RW, 4, "找不到？", "服务台代查", dark=True)
B.tlab(d, tf, "help", RX, 830, RW, 26, "报编号即可，工作人员从密集架取；"
       "锂电类当场配电池", 15, t1, None)
B.tlab(d, tf, "help2", RX, 860, RW, 24, "电话 %s · 逾期费 ¥%g/件·天 · 无押金"
       % (D["brand"]["phone"], RU["late_fee_per_day"]), 14, t2, None,
       features="tnum")
HD = D["brand"]["hours"]
for i, site in enumerate(D["brand"]["sites"]):
    B.hex_chip(d, RX + 12, 916 + i * 34, 9, P["steel"], "", ring=True,
               bg=P["dark"], dark=True)
    B.tlab(d, tf, "site%d" % i, RX + 30, 902 + i * 34, RW - 30, 26, site, 15, t1,
           None)
B.tlab(d, tf, "hours", RX, 984, RW, 24, "开放时间 %s %s–%s（%s）"
       % (HD["days"], HD["open"], HD["close"], HD["closed_note"]), 13, t2, None)

# ---------------- 页脚 ----------------
d.rect(40, H - 66, W - 80, 1, d.P["line"])
B.footer(d, 40, H - 52, W - 80, "short", dark=True)
B.tlab(d, tf, "foot-r", 1272, H - 52, 608, 24, "虚构演示界面 · 数据来自同一张馆藏表",
       12, B.blend(P["white"], 0.34, P["dark"]), None, align="END")

dsl = d.dsl()
(OUT / ("case-03-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-03", len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
