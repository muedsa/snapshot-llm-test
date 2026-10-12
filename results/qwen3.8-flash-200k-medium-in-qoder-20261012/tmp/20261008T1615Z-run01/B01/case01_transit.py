"""B01 case-01 · 城市轨道交通「夜归模式」站台信息屏（1920×1080）。

受众：晚归通勤者；使用时刻：站台上 5 分钟内决定换乘方案与是否赶得上末班。
数据全部由本文件内的行车间隔/首班车等待/末班时刻推导，保证倒计时与表格一致。
品牌与线路为虚构演示（见 portfolio.json 的 fictional 标记）。
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit, GRAD_NIGHT, minutes  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-01"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
NOW = "22:47"
now = minutes(NOW)

LINES = {
    "L1": dict(cn="长江线", col="#38BDF8",
               dirs=[("东岭", 3, 13, "23:12", 1, ""), ("西江渡", 8, 15, "23:05", 2, "")]),
    "L2": dict(cn="云谷线", col="#FBBF24",
               dirs=[("纺织城", 6, 12, "22:58", 3, "限速")]),
    "L3": dict(cn="老城线", col="#34D399",
               dirs=[("机场", 14, 18, "23:30", 4, "")]),
    "L4": dict(cn="机场快线", col="#A78BFA",
               dirs=[("长滩", 11, 16, "23:45", 5, "直达")]),
}

# 到站表：由首班等待 + 间隔推到末班为止，再按等待排序取前 10
arrivals = []
for lid, L in LINES.items():
    for term, first, iv, last, plat, note in L["dirs"]:
        lm = minutes(last)
        w, seq = first, 231
        col = []
        while now + w <= lm:
            col.append(w)
            w += iv
        for i, wd in enumerate(col):
            arrivals.append(dict(line=lid, term=term, wait=wd, plat=plat,
                                 note=note, last=(i == len(col) - 1),
                                 arr="%02d:%02d" % ((now + wd) // 60 % 24,
                                                    (now + wd) % 60),
                                 tid="%s%d" % (term[0], 2300 + seq + i * 7)))
arrivals.sort(key=lambda r: r["wait"])
arrivals = arrivals[:10]

d = Doc(W, H, bg="#060B18")
P = d.P
tf = TextFit()

# ---------- 背景 ----------
d.rect(0, 0, W, H, "#060B18")
K.radial_disc(d, 1450, -320, 900, ["#0EA5E9", "#0A1120"], radius="0.62")
K.radial_disc(d, -260, 700, 760, ["#7C3AED", "#0A1120"], radius="0.6")

# ---------- 顶部 ----------
d.pos(0, 0, W, 96, d.box(W, 96, color="#0B1428"))
d.line(0, 96, W, 96, 2, "#1E2E4F")
d.rect(40, 22, 44, 52, "#38BDF8", radius=10)
d.label(40, 22, 44, 52, "滨", "#06111F", 32, "BOLD", align="CENTER")
d.label(100, 18, 620, 34, "滨江市域轨道交通 · 夜归模式", P["t0"], 28, "BOLD")
d.label(100, 54, 620, 26, "Binjiang Metro · Night Return Mode（虚构演示品牌）",
        P["t2"], 19)
d.label(760, 20, 200, 30, "当前车站", P["t2"], 20)
d.label(760, 50, 320, 40, "滨江中心", P["cyan"], 34, "BOLD")
d.label(1120, 20, 300, 30, "本站换乘", P["t2"], 20)
d.label(1120, 50, 300, 36, "1 号线 · 3 号线", P["t1"], 26, "BOLD")
d.label(1450, 14, 430, 34, "现在 " + NOW, P["t0"], 30, "BOLD", align="END")
d.label(1450, 50, 430, 26, "10 月 9 日 周五 · 小雨 14℃ · 站台湿度 82%",
        P["t2"], 19, align="END")

# ---------- 左：线网图 ----------
MX, MY, MW, MH = 32, 116, 968, 644
d.pos(MX, MY, MW, MH, d.box(MW, MH, color="#0E1830", radius=16,
                            border="1 SOLID %s" % P["border"]))
d.label(MX + 24, MY + 16, 500, 30, "线网与末班方向", P["t0"], 24, "BOLD")
d.label(MX + 24, MY + 46, 560, 24, "圆点＝车站 · 双环＝换乘站 · 实心白环＝当前位置",
        P["t2"], 18)

o = d.origin(MX + 44, MY + 84)
SY = 0.86  # 纵向压缩，避免最南端车站压到图例行


def m(pts):
    return [(n_, x, round(y * SY)) for n_, x, y in pts]


ST = {
    "L1": m([("西江渡", 60, 290), ("老街", 190, 290), ("滨江中心", 320, 290),
             ("人民广场", 450, 290), ("港口", 580, 290), ("高新园", 710, 290),
             ("东岭", 840, 290)]),
    "L2": m([("云谷北", 190, 60), ("云谷", 190, 175), ("老街", 190, 290),
             ("纺织城", 190, 405)]),
    "L3": m([("西山", 60, 60), ("云谷", 190, 175), ("滨江中心", 320, 290),
             ("盐仓", 450, 405), ("机场", 580, 520)]),
    "L4": m([("会展中心", 450, 60), ("灯塔", 515, 175), ("港口", 580, 290),
             ("临港", 710, 405), ("长滩", 840, 520)]),
}
XFER = {("190", "249"), ("320", "249"), ("580", "249"), ("190", "150")}
for lid, pts in ST.items():
    col = LINES[lid]["col"]
    K.polyline(d, [(o.dx + x, o.dy + y) for _, x, y in pts], 9, col)
for lid, pts in ST.items():
    col = LINES[lid]["col"]
    for name, x, y in pts:
        key = (str(x), str(y))
        if key in XFER:
            continue
        o.dot(x, y, 16, "#0E1830")
        o.dot(x, y, 10, col)
        if name in ("西江渡", "东岭", "纺织城", "机场", "长滩", "西山", "会展中心",
                    "盐仓", "临港"):
            o.label(x - 70, y - 34, 140, 26, name, P["t1"], 19, align="CENTER")
for name, x, y in [("云谷", 190, 150), ("老街", 190, 249), ("滨江中心", 320, 249),
                   ("港口", 580, 249)]:
    o.pos(x - 13, y - 13, 26, 26,
          d.box(26, 26, color="#0E1830", radius=13, border="3 SOLID #FFFFFF"))
    o.label(x - 74, y + 16, 148, 26, name, P["t0"], 20, "BOLD", align="CENTER")
# 当前位置：琥珀环 + 光晕
o.dot(320, 249, 44, "#FBBF2422")
o.pos(320 - 24, 249 - 24, 48, 48,
      d.box(48, 48, color=None, radius=24, border="3 SOLID #FBBF24"))
o.label(320 - 90, 249 - 70, 180, 28, "你在这里", "#FBBF24", 20, "BOLD",
        align="CENTER")
# 终点站末班时刻（与底部卡片同源）
LASTLAB = [("西江渡", 60, 249, "23:05"), ("东岭", 840, 249, "23:12"),
           ("纺织城", 190, 348, "22:58"), ("机场", 580, 447, "23:30"),
           ("长滩", 840, 447, "23:45")]
for name, x, y, hh in LASTLAB:
    o.label(x - 70, y + 26, 140, 24, "末班 " + hh, P["t2"], 18, align="CENTER")

# 图例
lx = MX + 24
for lid in ("L1", "L2", "L3", "L4"):
    L = LINES[lid]
    d.rect(lx, MY + MH - 40, 26, 12, L["col"], radius=6)
    lab = "%s %s" % (lid, L["cn"])
    d.label(lx + 36, MY + MH - 48, 170, 28, lab, P["t1"], 20)
    lx += 36 + tf.w(lab, 20) + 34

# ---------- 右：到站表 ----------
BX, BY, BW, BH = 1032, 116, 856, 644
d.pos(BX, BY, BW, BH, d.box(BW, BH, color="#0E1830", radius=16,
                            border="1 SOLID %s" % P["border"]))
d.label(BX + 24, BY + 16, 500, 30, "本站到站 · 未来 45 分钟", P["t0"], 24, "BOLD")
d.label(BX + 24, BY + 46, 600, 24, "等待时间由行车间隔与末班时刻推导", P["t2"], 18)

rows, cc, notes = [], [], []
for r in arrivals:
    L = LINES[r["line"]]
    rows.append(["%s %s" % (r["line"], L["cn"]), r["tid"], "往 " + r["term"],
                 "%d 分" % r["wait"], r["arr"], "%d 号台" % r["plat"],
                 "末班" if r["last"] else (r["note"] or "正点")])
    cc.append([L["col"], P["t0"], P["t0"], P["t0"], P["t1"], P["t1"],
               "#F87171" if r["last"] else (P["amber"] if r["note"] else P["green"])])
K.table(d, BX + 24, BY + 84, [168, 96, 150, 78, 78, 96, 116], 46, rows,
        header=["线路", "车次", "方向", "等待", "到站", "站台", "状态"],
        fs=[20, 20, 21, 22, 20, 20, 20],
        aligns=["START", "START", "START", "END", "END", "END", "END"],
        cell_colors=cc, header_color=P["t2"], pad=8)
tf.check("c1-table-dir", "往 纺织城", 21, 150 - 16, 30)
for r in arrivals:
    tf.check("c1-note", r["note"] or "正点", 20, 116 - 16, 28)

# ---------- 底部：四线末班倒计时 ----------
CY, CH = 784, 184
cw = (W - 64 - 3 * 24) / 4
for i, lid in enumerate(("L1", "L2", "L3", "L4")):
    L = LINES[lid]
    x = 32 + i * (cw + 24)
    d.pos(x, CY, cw, CH, d.box(cw, CH, color="#121E38", radius=16,
                               border="1 SOLID %s" % P["border"],
                               shadow="0 10 24 0 #000000AA NORMAL"))
    d.rect(x, CY, 6, CH, L["col"])
    d.label(x + 26, CY + 18, 120, 30, lid, P["t0"], 26, "BOLD")
    d.label(x + 26, CY + 50, 220, 26, L["cn"], P["t1"], 20)
    term, first, iv, last, plat, note = L["dirs"][0]
    rem = minutes(last) - now
    urgent = rem <= 15
    d.label(x + 26, CY + 86, 300, 26, "末班 往 %s" % term, P["t2"], 19)
    d.label(x + 26, CY + 112, 300, 34, last, P["t0"], 30, "BOLD")
    lab = "剩 %d 分钟" % rem
    d.label(x + cw - 224, CY + 88, 200, 30, lab,
            "#F87171" if urgent else "#34D399", 26, "BOLD", align="END")
    tf.check("c1-count-%s" % lid, lab, 26, 200, 30)
    d.label(x + cw - 224, CY + 122, 200, 26,
            "间隔 %d 分钟" % iv, P["t2"], 19, align="END")
    if note:
        d.chip(x + 26, CY + 146, 190, 30, note, "#06111F", L["col"], 18, radius=8)
    else:
        d.label(x + 26, CY + 148, 300, 26, "运营正常", P["green"], 19)

# ---------- 底部提示条 ----------
d.pos(32, 992, W - 64, 56, d.box(W - 64, 56, color="#241A0B", radius=12,
                                 border="1 SOLID #FBBF2455"))
d.rect(56, 1010, 20, 20, "#FBBF24", radius=4)
msg = ("2 号线 云谷—老街 区段 22:30 起信号升级限速，行车间隔 8 → 12 分钟；"
       "4 号线为直达车，跳停 灯塔、临港。往纺织城末班 22:58（剩 %d 分），"
       "请优先在 3 号台候车。" % (minutes("22:58") - now))
d.label(92, 1000, W - 160, 40, msg, "#FDE68A", 21, align="START")
tf.check("c1-alert", msg, 21, W - 160, 40, lines=1)

dsl = d.dsl(bg_grad=None)
(OUT / "case01.snapshot").write_text(dsl, encoding="utf-8")
print("bytes", len(dsl), "· textfit", tf.n, "problems", tf.problems)
print("arrivals", [(a["line"], a["term"], a["wait"], a["last"]) for a in arrivals])
