"""B02 case-07 工具使用安全须知 1080x3000（折叠说明书首页，借出前签字页）。

设计任务：这是一页真的会被读、也会被拿去追责的纸。读者是要借走角磨机的人，
他不想读，所以顺序必须是「先说清谁必须读 → 戴什么 → 绝对不许做什么 →
我借的这类要注意什么 → 签字」。禁令用编号而不是段落，因为出事时要能指认
「第 2 条」。全部条文来自 data.json 的 safety 块（馆方自定，非台账统计）。
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
SAF = D["safety"]
CATS = D["cats"]
W, H = 1080, 3000
M = 72
CW = W - 2 * M
OUT = root / "tmp" / rid / "B02" / "case-07"
OUT.mkdir(parents=True, exist_ok=True)
ver = os.environ.get("B02_VER", "v01")

tf = TextFit()
d = B.paper_doc(W, H, dark=False, noise=16, seed=61)
t0, t1, t2 = d.P["t0"], d.P["t1"], d.P["t2"]
INK, ORANGE, RED = P["ink"], P["orange"], P["red"]

# ---------------- 页眉 ----------------
d.rect(0, 0, W, 236, B.blend(P["ink"], 0.93, P["paper"]))
B.brand_mark(d, M + 30, 66, 30, color=ORANGE, ink=P["paper"],
             bg=B.blend(P["ink"], 0.93, P["paper"]))
B.tlab(d, tf, "h-brand", M + 74, 46, 420, 40, BR["name"] + " · 安全须知", 28,
       P["paper"], "BOLD")
B.tlab(d, tf, "h-title", M, 108, CW - 260, 76, "借走之前，先把这页读完", 46, P["paper"],
       "BOLD")
B.tlab(d, tf, "h-sub", M, 186, CW - 260, 30, "S2 类工具须先通过 Safety 101（%d 分钟）；"
       "本页随借出单一同签署" % RU["safety_101_min"], 18,
       B.blend(P["white"], 0.62, P["dark"]), None)
d.rect(W - M - 214, 46, 214, 92, B.blend(P["white"], 0.10, P["dark"]), radius=8)
B.tlab(d, tf, "h-doc", W - M - 200, 58, 186, 24, "WH-SAFETY-2026-01", 14,
       B.blend(P["white"], 0.7, P["dark"]), "BOLD", align="CENTER", features="tnum")
B.tlab(d, tf, "h-doc2", W - M - 200, 86, 186, 24, "生效 %s" % RU["today"], 14,
       B.blend(P["white"], 0.5, P["dark"]), None, align="CENTER", features="tnum")
B.tlab(d, tf, "h-doc3", W - M - 200, 112, 186, 22, "第 1 页 / 共 1 页", 12,
       B.blend(P["white"], 0.4, P["dark"]), None, align="CENTER")

y = 276

# ---------------- 分级 ----------------
B.section_head(d, M, y, CW, 1, "两类工具，两种要求", sub="按工具表分级", size=26)
y += 52
lw = (CW - 24) / 2.0
for i, lv in enumerate(("S1", "S2")):
    info = SAF["levels"][lv]
    x = M + i * (lw + 24)
    tone = P["green"] if lv == "S1" else ORANGE
    d.rect(x, y, lw, 132, B.blend(tone, 0.075, P["paper"]), radius=8)
    d.rect(x, y, 6, 132, tone)
    B.tlab(d, tf, "lv%d-k" % i, x + 24, y + 18, 90, 40, lv, 30, tone, "BOLD",
           features="tnum")
    B.tlab(d, tf, "lv%d-n" % i, x + 110, y + 24, lw - 240, 30, info["name"], 22, INK,
           "BOLD")
    B.tlab(d, tf, "lv%d-c" % i, x + lw - 210, y + 26, 186, 26,
           "馆藏 %d 件" % info["tools"], 16, P["ink2"], None, align="END",
           features="tnum")
    B.tlab(d, tf, "lv%d-t" % i, x + 24, y + 66, lw - 48, 54, info["note"], 16,
           P["ink2"], None, lines=2)
y += 168

# ---------------- PPE 清单 ----------------
B.section_head(d, M, y, CW, 2, "防护装备清单", sub="借出时向志愿者领取", size=26)
y += 52
d.rect(M, y, CW, 40, B.blend(INK, 0.06, P["paper"]))
PPE_COLS = (("装备", M + 46, 190), ("S1 类", M + 252, 118), ("S2 类", M + 382, 202),
            ("说明", M + 600, CW - 616))
for j, (h, xj, wj) in enumerate(PPE_COLS):
    B.tlab(d, tf, "ppe-h%d" % j, xj, y + 9, wj, 24, h, 16, P["ink2"], "BOLD")
y += 40
PPE_ICON = ["目", "尘", "耳", "手", "衣", "发"]
for i, row in enumerate(SAF["ppe"]):
    if i:
        d.rect(M, y, CW, 1, B.blend(INK, 0.10, P["paper"]))
    B.hex_chip(d, M + 20, y + 34, 16, B.blend(ORANGE, 0.16, P["paper"])
               if row["s2"] == "—" else ORANGE, PPE_ICON[i], size=14,
               ink=P["paper"] if row["s2"] != "—" else P["ink2"], bg=P["paper"])
    B.tlab(d, tf, "ppe%d" % i, M + 46, y + 20, 190, 28, row["item"], 19, INK, "BOLD")
    for j, (v, xj, wj) in enumerate(((row["s1"], M + 252, 118),
                                     (row["s2"], M + 382, 202))):
        force = v not in ("—", "按工况", "建议")
        B.tlab(d, tf, "ppe%d-%d" % (i, j), xj, y + 22, wj, 26, v, 16,
               RED if "强制" in v else (P["ink2"] if v != "—" else B.blend(INK, 0.3, P["paper"])),
               "BOLD" if force else None, features="tnum")
    B.tlab(d, tf, "ppe%d-n" % i, M + 600, y + 12, CW - 616, 46, row["note"], 15,
           P["ink3"], None, lines=2)
    y += 68
y += 22

# ---------------- 六条禁令 ----------------
B.section_head(d, M, y, CW, 3, "六条禁令", sub="出事时按条指认", size=26)
y += 52
for i, txt in enumerate(SAF["prohibitions"]):
    # 六条同等强制：v01 给 02/06 深红、其余浅红，读成「有轻重」，且交替底色像斑马纹
    d.rect(M, y, CW, 88, B.blend(RED, 0.05, P["paper"]), radius=6)
    d.rect(M, y, 6, 88, RED)
    B.tlab(d, tf, "pr%d-n" % i, M + 24, y + 22, 60, 44, "%02d" % (i + 1), 32, RED,
           "BOLD", features="tnum")
    B.tlab(d, tf, "pr%d" % i, M + 96, y + 16, CW - 120, 60, txt, 19, INK, None,
           lines=2)
    y += 98
y += 20

# ---------------- 类目注意 ----------------
B.section_head(d, M, y, CW, 4, "你借的这一类要注意什么", sub="9 类全覆盖", size=26)
y += 52
for i, c in enumerate(CATS):
    col = B.cat_color(c["code"])
    lv = "S2" if c["code"] in SAF["levels"]["S2"]["cats"] else "S1"
    d.rect(M, y, CW, 74, B.blend(INK, 0.03, P["paper"]), radius=6)
    d.rect(M, y, 6, 74, col)
    B.tlab(d, tf, "cn%d" % i, M + 24, y + 10, 220, 26,
           "%s %s 区" % (c["name"], c["zone"]), 19, INK, "BOLD")
    B.tlab(d, tf, "cn%d-l" % i, M + 24, y + 42, 220, 22,
           "%d 件 · %s" % (c["count"], lv), 14,
           ORANGE if lv == "S2" else P["ink3"], None, features="tnum")
    B.tlab(d, tf, "cn%d-t" % i, M + 262, y + 14, CW - 286, 50, SAF["cat_notes"][c["code"]],
           16, P["ink2"], None, lines=2)
    y += 84
y += 22

# ---------------- 签字栏 ----------------
SO = SAF["signoff"]
d.rect(M, y, CW, 300, B.blend(INK, 0.9, P["paper"]), radius=10)
B.tlab(d, tf, "so-t", M + 28, y + 24, CW - 56, 34, SO["title"], 24, P["paper"], "BOLD")
B.tlab(d, tf, "so-s", M + 28, y + 66, CW - 268, 60, SO["statement"], 16,
       B.blend(P["white"], 0.72, P["dark"]), None, lines=2)
fy = y + 140
fw = (CW - 56 - 24) / 2.0
for i, f in enumerate(SO["fields"]):
    x = M + 28 + (i % 2) * (fw + 24)
    yy = fy + (i // 2) * 78
    B.tlab(d, tf, "so-f%d" % i, x, yy, fw, 22, f, 15,
           B.blend(P["white"], 0.55, P["dark"]), None)
    d.line(x, yy + 52, x + fw, yy + 52, 2, B.blend(P["white"], 0.3, P["dark"]))
# 印章给右上留出的空位：正文宽度已收窄，印章下沿不再压到第一条签名线
B.stamp(d, W - M - 190, y + 60, 168, 92, "馆方见证", color=P["green"], deg=-7,
        size=20, dark=True, tf=tf)
y += 330

B.footer(d, M, y, CW, "short", note=BR["fiction_notice"])
y += 46
assert y < H, "内容超出画布：%d > %d" % (y, H)

dsl = d.dsl()
(OUT / ("case-07-%s.snapshot" % ver)).write_text(dsl, encoding="utf-8")
print("case-07", len(dsl), "textfit:", tf.n, "problems:", len(tf.problems))
for p in tf.problems[:14]:
    print("  !", p)
print("content ends", y, "of", H, "tail blank", H - y)
