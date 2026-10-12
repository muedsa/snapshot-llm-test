"""B02 case-10 库区分区导视 1200x800（铝板吊牌，货架通道尽头抬头看）。

设计任务：这是全套唯一一块**不指望你走近读**的版面。读者在通道口、离 3–10 米、
抬头一眼，只要确认「我要找的电动工具在这一区」。所以字母必须大到压倒一切，
其余信息按「先确认、再补充」的层级往下排；占比刻度与相邻区是给停在牌下的人看的。
生成器按库区字母参数化（B02_ZONE），本触点交付 A 区。
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
W, H = 1200, 800
M = 56
CW = W - 2 * M
OUT = root / "tmp" / rid / "B02" / "case-10"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")

_by_id = {t["id"]: t for t in D["tools"]}
ZONES = [{"code": c["code"], "name": c["name"], "zone": c["zone"],
          "count": c["count"], "share": c["share"], "names": c["names"]}
         for c in D["cats"]]
zi = [i for i, z in enumerate(ZONES) if z["zone"] == os.environ.get("B02_ZONE", "A")][0]
Z = ZONES[zi]
col = B.cat_color(Z["code"])
# 「在册」是台账件数，「在馆」才是此刻能借到的；吊牌上不能把两者混为一谈
SHELF = sum(1 for t in D["tools"] if t["cat"] == Z["code"] and t["state"] == "在馆")
tf = TextFit()
INK, ORANGE = P["ink"], P["orange"]

# ---------------- 铝板底 ----------------
d = B.paper_doc(W, H, dark=True, noise=0, seed=1)
B.gradient_bands(d, W, H, "#2A2F35", "#15181B", band=16)
d.pos(0, 0, W, H, d.box(W, H, radius=0, border="3 SOLID %s" % B.blend(P["brass"], 0.35, P["dark"])))

# ---------------- 顶栏 ----------------
B.brand_mark(d, M + 24, 62, 24, color=col, ink=P["paper"], bg="#22262B")
B.tlab(d, tf, "t-brand", M + 60, 44, 460, 30, "%s · %s" % (BR["name"], BR["sites"][0].split("（")[0]),
       22, B.blend(P["white"], 0.86, P["dark"]), "BOLD")
B.tlab(d, tf, "t-kind", W - M - 300, 40, 300, 26, "库区导视", 18,
       B.blend(P["white"], 0.55, P["dark"]), None, align="END")
B.tlab(d, tf, "t-kind2", W - M - 300, 66, 300, 22, "ZONE %s / %02d-%02d"
       % (Z["zone"], zi + 1, len(ZONES)), 13, B.blend(P["white"], 0.4, P["dark"]), None,
       align="END", features="tnum")
d.rect(M, 100, CW, 1, B.blend(P["white"], 0.16, P["dark"]))

# ---------------- 巨型字母 ----------------
LX, LY, LS = M, 150, 380
d.rect(LX, LY, 400, 400, B.blend(col, 0.10, "#1B1F23"), radius=18)
d.rect(LX, LY, 400, 9, col, radius=0)
d.rect(LX, LY + 7, 400, 2, B.blend(col, 0.45, "#1B1F23"), radius=0)
B.tlab(d, tf, "letter", LX, LY + 6, 400, 344, Z["zone"], 320, col, "BOLD", align="CENTER")
# 字母下方留一条独立铭牌，避免小字压在大字笔画上
d.rect(LX + 18, LY + 356, 400 - 36, 40, B.blend(col, 0.34, "#1B1F23"), radius=8)
B.tlab(d, tf, "letter-sub", LX + 18, LY + 365, 400 - 36, 26, "ZONE %s" % Z["zone"], 20,
       B.blend(P["white"], 0.72, P["dark"]), "BOLD", align="CENTER", features="tnum")

# ---------------- 右侧信息 ----------------
RX = M + 440
RW = W - M - RX
B.tlab(d, tf, "r-name", RX, 156, RW, 76, Z["name"], 60, P["paper"], "BOLD")
B.tlab(d, tf, "r-count", RX, 246, RW, 40,
       "在册 %d 件　·　此刻在馆 %d 件" % (Z["count"], SHELF), 24,
       B.blend(P["white"], 0.78, P["dark"]), None, features="tnum")

B.tlab(d, tf, "r-rul-k", RX, 300, RW, 24, "类目占比刻度", 15,
       B.blend(P["white"], 0.45, P["dark"]), None)
B.ruler(d, RX, 330, RW - 96, Z["share"], tone=col, h=22, ticks="full",
        label=B.pct(Z["share"]), dark=True, lw=86, ls=22)
B.tlab(d, tf, "r-rul-n", RX, 362, RW, 22,
       "刻度以全馆 %d 次借阅为 100%%，每格 10%%；本区实际占 %s。"
       % (S["total_loans"], B.pct(Z["share"])), 12, B.blend(P["white"], 0.4, P["dark"]),
       None)

# 相邻区
AY = 404
B.tlab(d, tf, "a-k", RX, AY, RW, 24, "相邻库区", 15, B.blend(P["white"], 0.45, P["dark"]),
       None)
adj = []
if zi == 0:
    adj.append(("←", "入口 · 服务台", None, BR["rules"]["return_point"]))
else:
    adj.append(("←", "%s %s" % (ZONES[zi - 1]["zone"], ZONES[zi - 1]["name"]),
                ZONES[zi - 1], "%d 件 · 沿主通道上一区" % ZONES[zi - 1]["count"]))
if zi == len(ZONES) - 1:
    adj.append(("→", "归还口 · 维修角", None, "本区为通道端点"))
else:
    adj.append(("→", "%s %s" % (ZONES[zi + 1]["zone"], ZONES[zi + 1]["name"]),
                ZONES[zi + 1], "%d 件 · 沿主通道下一区" % ZONES[zi + 1]["count"]))
for i, (ar, txt, z2, sub) in enumerate(adj):
    x = RX + i * (RW / 2.0)
    w2 = RW / 2.0 - 16
    d.rect(x, AY + 30, w2, 62, B.blend(P["white"], 0.06, P["dark"]), radius=10)
    B.tlab(d, tf, "a%d-ar" % i, x + 14, AY + 42, 40, 40, ar, 34,
           B.blend(P["white"], 0.9, P["dark"]), "BOLD")
    B.tlab(d, tf, "a%d-t" % i, x + 58, AY + 44, w2 - 74, 26, txt, 19, P["paper"], "BOLD")
    B.tlab(d, tf, "a%d-s" % i, x + 58, AY + 70, w2 - 74, 20, sub, 12,
           B.blend(P["white"], 0.45, P["dark"]), None, features="tnum")

# 本区常借
BY = 512
B.tlab(d, tf, "b-k", RX, BY, RW, 24, "本区最常借出（按 2025 年台账）", 15, B.blend(P["white"], 0.45, P["dark"]),
       None)
# 「本区最常借出」必须是真排名：按该类目内各机型（同型号各代合并）的年内借出次数取前四
_ml = {}
for l in D["loans_2025"]:
    t = _by_id[l["tool"]]
    if t["cat"] == Z["code"]:
        _ml[t["name"].split(" ")[0]] = _ml.get(t["name"].split(" ")[0], 0) + 1
top4 = sorted(_ml.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
for i, (nm, nloans) in enumerate(top4):
    x = RX + (i % 2) * (RW / 2.0)
    yy = BY + 30 + (i // 2) * 34
    d.rect(x, yy + 8, 8, 8, col, radius=2)
    B.tlab(d, tf, "b%d" % i, x + 18, yy, 130, 26, nm, 18,
           B.blend(P["white"], 0.88, P["dark"]), None)
    B.tlab(d, tf, "b%d-n" % i, x + 152, yy, 84, 26, "%d 次" % nloans, 17,
           B.blend(P["white"], 0.55, P["dark"]), None, align="END", features="tnum")
_spread = top4[0][1] - top4[-1][1]
B.tlab(d, tf, "b-note", RX, BY + 100, RW, 20,
       "前四名年内相差 %d 次，各机型保有量相同（均 8 件），名次只作找物参考。" % _spread,
       12, B.blend(P["white"], 0.4, P["dark"]), None)

# ---------------- 底部九区索引 ----------------
IY = 640
d.rect(M, IY, CW, 1, B.blend(P["white"], 0.16, P["dark"]))
B.tlab(d, tf, "i-k", M, IY + 12, 200, 22, "全馆九区", 14,
       B.blend(P["white"], 0.45, P["dark"]), None)
cw9 = (CW - 8 * 12) / 9.0
for i, z in enumerate(ZONES):
    x = M + i * (cw9 + 12)
    on = (i == zi)
    zc = B.cat_color(z["code"])
    d.rect(x, IY + 40, cw9, 78, B.blend(zc, 0.30, "#1B1F23") if on
           else B.blend(P["white"], 0.05, P["dark"]), radius=8)
    if on:
        d.rect(x, IY + 40, cw9, 4, zc, radius=2)
    B.tlab(d, tf, "i%d" % i, x, IY + 48, cw9, 28, z["zone"], 23,
           P["paper"] if on else B.blend(P["white"], 0.5, P["dark"]), "BOLD",
           align="CENTER")
    # 索引条要能独立回答「我要找的类目在哪个字母」，只留字母就成装饰了
    B.tlab(d, tf, "i%d-c" % i, x + 4, IY + 76, cw9 - 8, 18, z["name"], 12,
           B.blend(P["white"], 0.78 if on else 0.42, P["dark"]), None, align="CENTER")
    B.tlab(d, tf, "i%d-n" % i, x, IY + 94, cw9, 18, "%d 件" % z["count"], 11,
           B.blend(P["white"], 0.72 if on else 0.34, P["dark"]), None, align="CENTER",
           features="tnum")
B.footer(d, M, IY + 122, CW, "micro", dark=True, note="周二至周日 %s–%s · 本馆与全部数据为虚构演示内容" % (
    BR["hours"]["open"], BR["hours"]["close"]))
assert IY + 122 + 22 < H, IY

dsl = d.dsl()
(OUT / ("case-10-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-10 zone", Z["zone"], Z["name"], len(dsl), "textfit:", tf.n,
      "problems:", len(tf.problems))
for p in tf.problems[:14]:
    print("  !", p)
