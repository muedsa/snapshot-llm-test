"""B02 case-09 工具档案卡 640x900（吊牌纸卡，贴在工具箱上）。

设计任务：读者是维修工和志愿者，他手里拿着这台机器，抬头看卡要能在 5 秒内回答
「这台能不能借出去、上一手发生了什么、下一次该谁管」。所以卡面第一优先是**状态**，
第二是**编号与库位**（要对得上货架），第三才是流水记录。
卡片顶部留穿绳孔，整张按吊牌比例排；记录用日期倒序，最近一条在最上面。
"""
import os
import sys
from datetime import date
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
W, H = 640, 900
M = 40
CW = W - 2 * M
OUT = root / "tmp" / rid / "B02" / "case-09"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")
TID = os.environ.get("B02_TOOL", "WH-EMT-008")

tool = [t for t in D["tools"] if t["id"] == TID][0]
led = D["ledger"]["tools"][TID]
state = tool["state"]
SC = B.STATE_COLOR[state]
tf = TextFit()
d = B.paper_doc(W, H, dark=False, noise=9, seed=29)
INK, ORANGE = P["ink"], P["orange"]

# ---------------- 卡面与穿绳孔 ----------------
d.rect(10, 10, W - 20, H - 20, P["white"], radius=26)
d.pos(10, 10, W - 20, H - 20, d.box(W - 20, H - 20, radius=26,
                                    border="2 SOLID %s" % B.blend(INK, 0.24, P["paper"])))
# 加强圈 + 孔
d.rect(W / 2 - 25, 25, 50, 50, B.blend(P["brass"], 0.82, P["white"]), radius=25)
d.rect(W / 2 - 25 + 5, 30, 40, 40, B.blend(P["brass"], 0.55, P["white"]), radius=20)
d.rect(W / 2 - 15, 35, 30, 30, B.blend(INK, 0.30, P["paper"]), radius=15)
d.rect(W / 2 - 14, 36, 28, 28, P["paper"], radius=14)

# ---------------- 抬头：编号与类目 ----------------
col = B.cat_color(tool["cat"])
B.tlab(d, tf, "t-cat", M, 92, 300, 22, "%s · %s 区" % (tool["cat_name"], tool["shelf"].split("-")[0]),
       15, col, "BOLD")
B.tlab(d, tf, "t-id", M, 116, CW, 40, tool["id"], 32, INK, "BOLD", features="tnum")
B.tlab(d, tf, "t-name", M, 160, CW - 150, 36, tool["name"], 26, INK, "BOLD")
B.tlab(d, tf, "t-shelf", W - M - 200, 124, 200, 28, "库位 %s" % tool["shelf"], 19,
       P["ink2"], "BOLD", align="END", features="tnum")

# ---------------- 状态横幅 ----------------
BY = 200
d.rect(M, BY, CW, 66, SC, radius=10)
B.tlab(d, tf, "s-k", M + 22, BY + 9, 240, 30, state, 23, P["white"], "BOLD")
_open = [r for r in led["rows"] if r["kind"] in ("报修", "停用")]
B.tlab(d, tf, "s-age", W - M - 220, BY + 13, 176, 22,
       "挂起 %d 天 · %s" % ((date.fromisoformat(RU["today"])
                             - date.fromisoformat(_open[0]["date"])).days,
                            _open[0]["date"][5:].replace("-", "."))
       if _open else "", 13, B.blend(P["white"], 0.94, SC), "BOLD", align="END",
       features="tnum")
B.tlab(d, tf, "s-n", M + 22, BY + 39, CW - 44, 22,
       "停止借出，等维修角排期；借出前须先解除本状态" if state == "维修中" else
       {"在馆": "可借，货架原位；借出后本卡随件移动",
        "在借": "已借出，本卡在架上留档",
        "报废待处理": "已停用，等待理事会处置，不得借出"}[state],
       13, B.blend(P["white"], 0.82, SC), None)

# ---------------- 身份表 ----------------
y = BY + 82
d.rect(M, y, CW, 1, B.blend(INK, 0.16, P["white"]))
y += 14
fields = [
    ("购入日期", B.date_cn(led["purchased"])),
    ("已服役", "%.1f 年" % led["age_years"]),
    ("台账登记价", B.money(tool["value"])),
    ("动力", tool["power"]),
    ("安全分级", "%s 级" % tool["safety_level"]),
    ("保养周期", "%d 天" % tool["service_days"]),
    ("2025 年借出", "%d 次" % led["loans_2025"]),
    ("下次保养", B.date_cn(tool["next_service"]) + ("（顺延）" if state == "维修中" else "")),
]
fw = (CW - 24) / 2.0
for i, (k, v) in enumerate(fields):
    x = M + (i % 2) * (fw + 24)
    yy = y + (i // 2) * 40
    B.tlab(d, tf, "f%d-k" % i, x, yy, fw, 18, k, 12, P["ink3"], None)
    B.tlab(d, tf, "f%d-v" % i, x, yy + 17, fw, 24, v, 17, INK, "BOLD", features="tnum")
    if i % 2 == 0:
        d.rect(x + fw + 10, yy, 1, 34, B.blend(INK, 0.10, P["white"]))
y += 4 * 40 + 4

# ---------------- 记录表 ----------------
d.rect(M, y, CW, 1, B.blend(INK, 0.16, P["white"]))
y += 14
rows = led["rows"][:5]
B.tlab(d, tf, "r-title", M, y, 200, 24, "维修与保养记录", 18, INK, "BOLD")
B.tlab(d, tf, "r-n", W - M - 220, y + 4, 220, 20,
       "共 %d 条，显示最近 %d 条" % (len(led["rows"]), len(rows)), 12, P["ink3"], None,
       align="END", features="tnum")
y += 30
d.rect(M, y, CW, 26, B.blend(INK, 0.06, P["white"]))
RCOLS = (("日期", M + 10, 88), ("类型", M + 104, 46), ("事项 / 经办", M + 156, CW - 166))
for j, (h_, xj, wj) in enumerate(RCOLS):
    B.tlab(d, tf, "rh%d" % j, xj, y + 5, wj, 18, h_, 12, P["ink2"], "BOLD")
y += 26
KIND_COLOR = {"购入": P["steel"], "保养": P["green"], "维修": ORANGE,
              "报修": P["red"], "停用": P["ink3"]}
for i, r in enumerate(rows):
    rh = 48
    yy = y + i * rh
    if i % 2 == 0:
        d.rect(M, yy, CW, rh, B.blend(INK, 0.025, P["white"]))
    B.tlab(d, tf, "r%d-d" % i, M + 10, yy + 8, 88, 20, r["date"].replace("-", "."), 13,
           P["ink2"], None, features="tnum")
    kc = KIND_COLOR[r["kind"]]
    d.rect(M + 104, yy + 7, 44, 20, B.blend(kc, 0.14, P["white"]), radius=10)
    B.tlab(d, tf, "r%d-k" % i, M + 104, yy + 9, 44, 18, r["kind"], 12, kc, "BOLD",
           align="CENTER")
    B.tlab(d, tf, "r%d-t" % i, M + 156, yy + 6, CW - 166, 24, r["text"], 13, INK, None,
           lines=2)
    B.tlab(d, tf, "r%d-w" % i, M + 156, yy + 30, CW - 166, 16, "经办：%s" % r["who"], 11,
           P["ink3"], None)
    d.rect(M, yy + rh - 1, CW, 1, B.blend(INK, 0.07, P["white"]))
y += len(rows) * 48 + 8

# ---------------- 底部 ----------------
d.rect(M, y, CW, 50, B.blend(P["steel"], 0.08, P["white"]), radius=8)
B.tlab(d, tf, "b-1", M + 16, y + 7, CW - 32, 20,
       "发现异常：当日交回服务台登记，不要自行拆修（安全须知禁令 06）。", 13, P["ink"], "BOLD")
B.tlab(d, tf, "b-2", M + 16, y + 28, CW - 32, 18,
       "维修角 %s 14:00–18:00 · 电话 %s · %s" % (BR["hours"]["days"], BR["phone"], RU["return_point"]),
       12, P["ink2"], None, features="tnum")
y += 62
B.footer(d, M, y, CW, "short", note="本卡明细为演示台账")
B.tlab(d, tf, "note", M, y + 20, CW, 34, D["ledger"]["note"], 10, P["ink3"], None,
       lines=2)
y += 46
assert y < H - 6, y

dsl = d.dsl()
(OUT / ("case-09-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-09", TID, len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:14]:
    print("  !", p)
print("content ends", y, "of", H)
