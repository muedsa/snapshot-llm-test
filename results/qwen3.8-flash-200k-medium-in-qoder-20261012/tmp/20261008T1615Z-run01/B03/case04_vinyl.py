"""B03 case-04：唱片店本周黑胶选碟牌（1400×1400）。

受众：站在试听机前的顾客；情境：手里拿着两张碟，只有几十秒决定哪张上机。
用户要做的事：看懂一张碟「能不能听完、每首多长、值不值这个价」，然后按步骤试听。

独到手法：把「一首歌有多长」变成可以直接看见的弧长——外圈一格＝A 面的一首，
SWEEP 渐变用硬色标（gradientStops 成对）切出扇区，再用一片同心沟槽圆盘盖住圆心，
只留外圈 28 px 的扇区环（探针 04c + 05）。一圈＝A 面总时长，刻度按分钟等分，
所以顾客不用读数字就知道「A3 很短、A2 最长」。右栏每张碟配一条刻纹容量条：
占用＝该面时长 / 该制式经验上限，超上限的格子画成警示色。

曲目、价格、店名全部是虚构演示数据（见同目录 data.json）；容量上限是刻纹线性
速度对应的经验值，不是厂商规格。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, n           # noqa: E402
import b03kit as K                            # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1400, 1400
BG, PANEL, LINE = "#14171C", "#1C2128", "#2E3641"
INK, T1, T2 = "#F3EEE1", "#C7CBC6", "#8B93A1"
AMBER, VERM, TEAL = "#E0A526", "#C8552B", "#6FA8A0"
GROOVE_A, GROOVE_B, INK_DISC = "#2C333C", "#171B21", "#0E1116"

M = 44
CX, CY = 418.0, 552.0
R_RING, R_INNER, R_GROOVE, R_LABEL = 286.0, 258.0, 250.0, 92.0
R_T0, R_T1, R_LBL = 292.0, 308.0, 320.0
EXTENT = R_LBL + 42.0

# 制式经验上限（每面，秒）：刻纹越靠内圈线速度越低，所以上限是「音质还能接受」的经验值
CAP = {('12"', 33): 22 * 60, ('12"', 45): 14 * 60, ('7"', 45): 5 * 60}

# 曲目、价格、年份、厂牌均为虚构演示数据（同目录 data.json）
RECS = [
    dict(no="01", artist="林声远", title="夜航西飞", year=1974, label="Blue Harbour",
         genre="爵士钢琴", size='12"', rpm=33, price=380, tone=AMBER,
         A=[("夜航", 272), ("西飞", 378), ("灯塔", 185), ("季风", 344), ("返场", 140)],
         B=[("晨雾", 263), ("旧代码", 351), ("河面", 224), ("靠岸", 286)]),
    dict(no="02", artist="陈绿", title="潮汐练习", year=2021, label="海岸线唱片",
         genre="氛围电子", size='12"', rpm=33, price=520, tone=TEAL,
         A=[("退潮", 425), ("防波堤", 398), ("盐", 312)],
         B=[("夜潮", 486), ("涌", 402), ("平潮", 371), ("回湾", 181)]),
    dict(no="03", artist="The Wren", title="Third Avenue", year=1968, label="Northgate",
         genre="灵魂乐", size='12"', rpm=45, price=640, tone=VERM,
         A=[("Third Ave.", 148), ("Mojo", 132), ("Cold Love", 165), ("Sit Down", 121),
            ("Fly Home", 180), ("Encore", 92)],
         B=[("Blue Corner", 175), ("Maggie", 140), ("Run Round", 163), ("Bye Ave.", 124)]),
    dict(no="04", artist="苏眉", title="雪线", year=1989, label="云杉小社",
         genre="民谣", size='7"', rpm=45, price=180, tone="#9A8CB8",
         A=[("雪线", 238)],
         B=[("雪线 · 伴奏", 166)]),
]
FEAT = RECS[0]
FA = FEAT["A"]
RPM_TXT = f'{FEAT["size"]} {FEAT["rpm"]}⅓' if FEAT["rpm"] == 33 else f'{FEAT["size"]} {FEAT["rpm"]}'


def mmss(sec):
    return f"{sec // 60}:{sec % 60:02d}"


def hms(sec):
    h, rem = divmod(sec, 3600)
    return f"{h}:{rem // 60:02d}:{rem % 60:02d}"


def side_total(side):
    return sum(t[1] for t in side)


def n_tracks(rec):
    return len(rec["A"]) + len(rec["B"])


TOTAL_ALL = sum(side_total(r["A"]) + side_total(r["B"]) for r in RECS)
N_TRACKS = sum(n_tracks(r) for r in RECS)
N_SIDES = 2 * len(RECS)
AVG = TOTAL_ALL / N_TRACKS
PRICE_SUM = sum(r["price"] for r in RECS)
ALL_TRACKS = [(sec, tag, nm, r["no"], r["title"])
              for r in RECS for tag in ("A", "B") for nm, sec in r[tag]]
LONGEST = max(ALL_TRACKS)
SHORTEST = min(ALL_TRACKS)
OVER = [(r["no"], s, side_total(r[s]))
        for r in RECS for s in ("A", "B")
        if side_total(r[s]) > CAP[(r["size"], r["rpm"])]]

assert abs(sum(t[1] for t in FA) - side_total(FA)) < 1e-9 and len(FA) >= 2
assert N_SIDES == 8 and TOTAL_ALL > 0
assert EXTENT <= min(CX - M, W - 60 - CX, CY - 176, 918 - CY), "盘面标注越出左栏"

tf = TextFit()
d = Doc(W, H, bg=BG, palette={"ink": INK})
MONO = "IBM Plex Mono,Courier New,monospace"


def disc(cx, cy, r, color, radius=None):
    """同心圆盘（直径 2r，圆心对齐）。radius 默认＝r，即完整圆。"""
    d.pos(cx - r, cy - r, 2 * r, 2 * r,
          f'<Container width="{n(2 * r)}" height="{n(2 * r)}" '
          f'borderRadius="{n(radius if radius is not None else r)}" color="{color}"/>')


# ---------- 背景与页眉 ----------
d.rect(0, 0, W, H, BG)
d.rect(M, 0, 6, H, AMBER)
K.outline(d, tf, "hd-title", 78, 40, 400, 82, "本周试听", 66, AMBER, fill=INK, width=2.6)
K.tlab(d, tf, "hd-sub", 78, 122, 560, 26,
       "黑胶选碟牌 · 试听机 2 号位 · 10 月第 2 周", 19, T2)
K.tlab(d, tf, "hd-shop", 900, 46, 400, 34, "暗房唱片 / 城南仓", 26, INK,
       style="BOLD", align="END")
K.tlab(d, tf, "hd-meta", 900, 84, 400, 26,
       f"{len(RECS)} 张 · {N_SIDES} 面 · 合计 {hms(TOTAL_ALL)}", 19, T1, align="END")
K.tlab(d, tf, "hd-note", 900, 114, 400, 24, "标价含试听服务，售出不退", 16, T2, align="END")
d.line(M, 162, W - M, 162, 2, LINE)

# ---------- 外圈：A 面时长扇区环（SWEEP 硬色标） ----------
disc(CX, CY, R_RING + 3, "#3B444F")     # 盘边细 rim，让扇区环有明确外边界
SEG = [AMBER, "#D98A2B", VERM]
fracs, acc = [], 0.0
for name, sec in FA:
    fracs.append((acc, acc + sec / side_total(FA), name, sec))
    acc += sec / side_total(FA)
assert abs(fracs[-1][1] - 1.0) < 1e-9
stops = [v for f in fracs for v in (f[0], f[1])]
cols = [c for i, f in enumerate(fracs) for c in (SEG[i % len(SEG)],) * 2]
K.sweep_disc(d, CX - R_RING, CY - R_RING, 2 * R_RING, cols, tile="REPEAT",
             span=2 * math.pi, stops=",".join(f"{s:.5f}" for s in stops), start=3 * math.pi / 2)
disc(CX, CY, R_INNER, INK_DISC)

# 分钟刻度：一圈＝A 面总时长，故每格恰为 1 分钟
n_min = int(round(side_total(FA) / 60.0))
for i in range(n_min):
    a = -math.pi / 2 + i * 2 * math.pi / n_min
    major = i % 5 == 0
    r1 = R_T1 + (6 if major else 0)
    x0, y0 = CX + math.cos(a) * R_T0, CY + math.sin(a) * R_T0
    x1, y1 = CX + math.cos(a) * r1, CY + math.sin(a) * r1
    d.line(x0, y0, x1, y1, 3 if major else 1.6, T2 if major else "#5A6270")
# 曲目分界线（扇区之间）＋ 起播点（12 点钟）加粗
for f0, f1, name, sec in fracs:
    a = -math.pi / 2 + f0 * 2 * math.pi
    d.line(CX + math.cos(a) * (R_INNER - 4), CY + math.sin(a) * (R_INNER - 4),
           CX + math.cos(a) * (R_RING + 4), CY + math.sin(a) * (R_RING + 4),
           4 if abs(f0) < 1e-9 else 2, INK_DISC if abs(f0) < 1e-9 else "#0B0E12")

# 扇区标注：曲号 + 时长，落在扇区中线外
for i, (f0, f1, name, sec) in enumerate(fracs):
    a = -math.pi / 2 + (f0 + f1) / 2 * 2 * math.pi
    lx, ly = CX + math.cos(a) * R_LBL, CY + math.sin(a) * R_LBL
    K.tlab(d, tf, f"seg{i}", lx - 40, ly - 11, 80, 22,
           f"A{i + 1} {mmss(sec)}", 16, SEG[i % len(SEG)], align="CENTER", font=MONO)

# ---------- 盘面：同心沟槽 + 偏心高光 + 中心标 ----------
disc(CX, CY, R_GROOVE, GROOVE_B)
r, step = R_GROOVE - 2, 9.0
k = 0
while r > R_LABEL + 14:
    disc(CX, CY, r, GROOVE_A if k % 2 else "#1A1F26")
    r -= step
    k += 1
N_GROOVES = k
d.pos(CX - R_GROOVE, CY - R_GROOVE, 2 * R_GROOVE, 2 * R_GROOVE,
      f'<ClipOval clipBehavior="ANTI_ALIAS">'
      f'<Container width="{n(2 * R_GROOVE)}" height="{n(2 * R_GROOVE)}" '
      f'gradientType="RADIAL" gradientColors="#FFFFFF5C,#FFFFFF16,#FFFFFF00" '
      f'gradientCenter="CENTER" gradientRadius="0.9" gradientFocal="TOP_LEFT" '
      f'gradientFocalRadius="0.05"/></ClipOval>')
disc(CX, CY, R_LABEL, "#E8DFC6")
disc(CX, CY, R_LABEL - 4, "#EFE7D2")
# 中心标三行都避开圆心主轴孔（孔半径 7.5，故 ±14 px 内不放文本）
K.tlab(d, tf, "lab-side", CX - 62, CY - 64, 124, 20, f"A 面 {mmss(side_total(FA))}", 15,
       "#6A5C3C", align="CENTER", font=MONO)
K.tlab(d, tf, "lab-title", CX - 62, CY - 42, 124, 24, FEAT["title"], 18, "#2A2418",
       style="BOLD", align="CENTER")
K.tlab(d, tf, "lab-rpm", CX - 62, CY + 18, 124, 22, RPM_TXT, 15, "#5A4E33", align="CENTER")
disc(CX, CY, 7.5, INK_DISC)

K.tlab(d, tf, "zero", CX - 66, CY - R_LBL - 30, 132, 22, "0:00 起播", 15, AMBER,
       align="CENTER", font=MONO)
d.chip(M + 34, 176, 116, 28, "本周主打", "#2A2418", AMBER, size=17)
K.tlab(d, tf, "chip-link", M + 162, 176, 300, 28,
       f"01《{FEAT['title']}》A 面", 17, T1, font=MONO)
K.tlab(d, tf, "wheel-cap", M + 34, 902, 700, 24,
        f"外圈一圈＝A 面总时长 {mmss(side_total(FA))}，一格＝1 分钟；"
        f"扇区弧长∝单曲时长（{N_GROOVES} 圈沟槽仅示意）", 16, T2, align="CENTER")

# ---------- 右栏：四张碟 ----------
RX, RW = 800.0, 544.0
CARD_H, CARD_P = 176.0, 188.0
for i, rec in enumerate(RECS):
    no, art, ttl, yr = rec["no"], rec["artist"], rec["title"], rec["year"]
    lbl, gen, size, rpm = rec["label"], rec["genre"], rec["size"], rec["rpm"]
    price, tone, A, B = rec["price"], rec["tone"], rec["A"], rec["B"]
    cy0 = 176.0 + i * CARD_P
    d.pos(RX, cy0, RW, CARD_H,
          f'<Container width="{n(RW)}" height="{n(CARD_H)}" color="{PANEL}" '
          f'borderRadius="10" border="1 SOLID {LINE}"/>')
    d.rect(RX, cy0, 5, CARD_H, tone, radius=None)
    K.outline(d, tf, f"no{i}", RX + 22, cy0 + 14, 66, 46, no, 40, tone, width=2.0)
    K.tlab(d, tf, f"art{i}", RX + 96, cy0 + 16, 300, 30, art, 25, INK, style="BOLD")
    K.tlab(d, tf, f"pr{i}", RX + 404, cy0 + 14, 118, 34, K.money(price), 26, tone,
           style="BOLD", align="END", font=MONO)
    K.tlab(d, tf, f"ttl{i}", RX + 96, cy0 + 48, 426, 26, ttl, 20, T1)
    K.tlab(d, tf, f"meta{i}", RX + 96, cy0 + 74, 426, 24,
           f"{yr} · {lbl} · {gen} · {size} {rpm}⅓ 转" if rpm == 33
           else f"{yr} · {lbl} · {gen} · {size} {rpm} 转", 16, T2)
    for j, (tag, side) in enumerate((("A", A), ("B", B))):
        ry = cy0 + 104 + j * 30
        sec_t, cap = side_total(side), CAP[(size, rpm)]
        use = sec_t / cap
        K.tlab(d, tf, f"sd{tag}{i}", RX + 22, ry, 34, 22, tag, 17, T1, style="BOLD")
        bx, bw, bh = RX + 56, 230.0, 8.0
        d.rect(bx, ry + 6, bw, bh, "#262C34", radius=4)
        d.rect(bx, ry + 6, bw * min(1.0, use), bh, VERM if use > 1 else tone, radius=4)
        if use > 1:
            d.line(bx + bw, ry + 2, bx + bw, ry + 16, 3, "#FFD166")
        K.tlab(d, tf, f"st{tag}{i}", bx + bw + 10, ry, 140, 22,
               f"{mmss(sec_t)} / {mmss(cap)}", 16, T1, font=MONO)
        K.tlab(d, tf, f"pc{tag}{i}", RX + 444, ry, 78, 22,
               ("超 " + K.pct(use - 1)) if use > 1 else K.pct(use), 16,
               VERM if use > 1 else T2, align="END", font=MONO)
        assert abs(sum(s[1] for s in side) - sec_t) < 1e-9

# ---------- 中带：A 面清单 + 容量口径 ----------
BAND_T, BAND_B = 940.0, 1096.0
K.tlab(d, tf, "lg-hd", M + 34, BAND_T, 700, 26, "本周主打 A 面 · 时长、占比与起播时刻",
       19, INK, style="BOLD")
K.tlab(d, tf, "lg-col", 610, BAND_T + 1, 168, 24, "起播＝盘面分钟刻度", 15, T2, align="END")
acc_s = 0
for i, (name, sec) in enumerate(FA):
    ry = BAND_T + 32 + i * 26
    K.tlab(d, tf, f"lg{i}", M + 34, ry, 240, 24, f"A{i + 1} {name}", 18, T1)
    K.tlab(d, tf, f"lgd{i}", 320, ry, 92, 24, mmss(sec), 17, SEG[i % len(SEG)],
           align="END", font=MONO)
    K.tlab(d, tf, f"lgp{i}", 428, ry, 84, 24, K.pct(sec / side_total(FA)), 17, T2,
           align="END", font=MONO)
    K.tlab(d, tf, f"lgs{i}", 520, ry, 80, 24, mmss(acc_s), 17, T1, align="END", font=MONO)
    assert abs(sum(FA[k][1] for k in range(i)) - acc_s) < 1e-9
    acc_s += sec
assert acc_s == side_total(FA)

K.tlab(d, tf, "cp-hd", RX, BAND_T, 500, 26, "为什么有的面要标红：刻纹容量口径", 19, INK,
       style="BOLD")
rows = [('12" 33⅓', "≈22 分", "标准 LP，内圈仍保线速度"),
        ('12" 45', "≈14 分", "刻纹更宽、动态更好，装曲少"),
        ('7" 45', "≈5 分", "单曲盘，一般一面一首")]
for i, (fmt, cap, why) in enumerate(rows):
    ry = BAND_T + 34 + i * 30
    K.tlab(d, tf, f"cp{i}a", RX, ry, 118, 26, fmt, 18, T1, font=MONO)
    K.tlab(d, tf, f"cp{i}b", RX + 126, ry, 84, 26, cap, 18, AMBER, align="END", font=MONO)
    K.tlab(d, tf, f"cp{i}c", RX + 224, ry, 320, 26, why, 16, T2)
K.tlab(d, tf, "cp-foot", RX, BAND_T + 126, 544, 24,
       "上限为经验值（演示口径）；本页 1 面超出，试听时内圈细节会打折。", 15, T2)
assert BAND_T + 150 <= BAND_B

# ---------- 底带：试听步骤 ----------
ST_T = 1120.0
d.line(M, ST_T - 14, W - M, ST_T - 14, 2, LINE)
K.tlab(d, tf, "st-hd", M + 34, ST_T, 400, 26, "试听机 2 号位 · 四步", 19, INK, style="BOLD")
STEPS = [("1", "看封底曲目表", "先确认 A/B 面首数"),
         ("2", "取碟上机", "手不入内圈，落针前静音"),
         ("3", "听 A1 全曲", f"A1 {mmss(FA[0][1])}，够判断这张"),
         ("4", "留下或回架", "标价已含试听服务")]
sw = (W - 2 * M - 3 * 18) / 4
for i, (num, t1, t2) in enumerate(STEPS):
    sx = M + i * (sw + 18)
    d.rect(sx, ST_T + 34, sw, 116, PANEL, radius=10)
    disc(sx + 34, ST_T + 62, 16, AMBER)
    K.tlab(d, tf, f"sp{i}", sx + 18, ST_T + 48, 32, 28, num, 20, "#2A2418",
           style="BOLD", align="CENTER")
    K.tlab(d, tf, f"st{i}a", sx + 60, ST_T + 48, sw - 74, 28, t1, 19, INK, style="BOLD")
    K.tlab(d, tf, f"st{i}b", sx + 16, ST_T + 88, sw - 32, 52, t2, 16, T2, lines=2,
           valign="TOP")
    assert sx + sw <= W - M

# ---------- 汇总与页脚 ----------
SUM_Y = ST_T + 166
K.tlab(d, tf, "sum", M + 34, SUM_Y, 600, 26,
       f"本周 {len(RECS)} 张 / {N_SIDES} 面 / {N_TRACKS} 首 · "
       f"合计 {hms(TOTAL_ALL)} · 标价 {K.money(PRICE_SUM)}", 18, T1)
K.tlab(d, tf, "sum-m", 648, SUM_Y, 320, 26,
       f"单曲均长 {mmss(int(round(AVG)))} · 最长 {LONGEST[3]}-{LONGEST[1]} {mmss(LONGEST[0])}",
       18, T1)
K.tlab(d, tf, "sum-r", 980, SUM_Y, 320, 26,
       f"超出容量：{len(OVER)} 面（{OVER[0][0]} {OVER[0][1]} 面）" if OVER else "全部面在容量内",
       18, VERM if OVER else T2, align="END")
d.line(M, H - 64, W - M, H - 64, 2, LINE)
K.tlab(d, tf, "ft-l", M + 34, H - 52, 700, 24,
       "暗房唱片 · 本周选碟牌 · 曲目/价格/年份为虚构演示数据，容量为经验口径", 15, T2)
K.tlab(d, tf, "ft-r", 900, H - 52, 400, 24, "Snapshot DSL 纯文本渲染 · 1400×1400 · " + VER,
       15, T2, align="END", font=MONO)
assert SUM_Y + 30 <= H - 70
assert max(cy0 + CARD_H for cy0 in [176 + i * CARD_P for i in range(len(RECS))]) <= BAND_T - 8

out = d.dsl()
tmp = ROOT / "tmp" / RID / "B03"
(tmp / f"case04-{VER}.snapshot").write_text(out, encoding="utf-8")
odata = ROOT / "outputs" / RID / "B03" / "case-04"
odata.mkdir(parents=True, exist_ok=True)
(odata / "data.json").write_text(json.dumps({
    "note": "虚构演示数据：曲目时长、价格、年份、厂牌均非真实唱片目录；"
            "容量上限为刻纹线性速度对应的经验口径，不是厂商规格。",
    "unit": {"duration": "second", "price": "CNY"},
    "capacity_seconds_per_side": {f'{f} {r}转': c for (f, r), c in CAP.items()},
    "featured": {"no": FEAT["no"], "title": FEAT["title"], "side": "A",
                 "total_seconds": side_total(FA),
                 "tracks": [{"i": i + 1, "name": nm, "seconds": s,
                             "share": round(s / side_total(FA), 4),
                             "start_seconds": sum(x[1] for x in FA[:i])}
                            for i, (nm, s) in enumerate(FA)]},
    "records": [{"no": r["no"], "artist": r["artist"], "album": r["title"],
                 "year": r["year"], "label": r["label"], "genre": r["genre"],
                 "size": r["size"], "rpm": r["rpm"], "price": r["price"],
                 "sides": {k: [{"name": nm, "seconds": s} for nm, s in r[k]]
                           for k in ("A", "B")},
                 "capacity_seconds": CAP[(r["size"], r["rpm"])],
                 "A_used": round(side_total(r["A"]) / CAP[(r["size"], r["rpm"])], 4),
                 "B_used": round(side_total(r["B"]) / CAP[(r["size"], r["rpm"])], 4)}
                for r in RECS],
    "totals": {"records": len(RECS), "sides": N_SIDES, "tracks": N_TRACKS,
               "seconds": TOTAL_ALL, "avg_track_seconds": round(AVG, 1),
               "price_sum": PRICE_SUM,
               "over_capacity_sides": [{"no": o[0], "side": o[1], "seconds": o[2]} for o in OVER]},
    "render": {"canvas": [W, H], "version": VER, "dsl_chars": len(out),
               "groove_discs": N_GROOVES, "minute_ticks": n_min},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{VER} chars {len(out)} TextFit {tf.n} problems {len(tf.problems)}")
for p in tf.problems:
    print("  !", p)
print(f"wheel: segs {len(fracs)} ticks {n_min} grooves {N_GROOVES} "
      f"A {mmss(side_total(FA))} share_sum {fracs[-1][1]:.4f}")
print(f"totals: {len(RECS)} 张 {N_SIDES} 面 {N_TRACKS} 首 {hms(TOTAL_ALL)} "
      f"avg {mmss(int(round(AVG)))} price {PRICE_SUM} over {len(OVER)}")
