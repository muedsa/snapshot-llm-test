"""B03 case-07：徒步手册·环线剖面字符画（1600×1000）。

受众与情境：徒步者在出发前一晚摊开手册，要判断「爬升集中在哪几公里、哪段最陡、
哪里还能补水、来回要多久」，据此决定几点出发、带多少水。

独到手法：整幅海拔剖面用**等宽块字符的密度**画——█ 是路面，▓▒░ 是随深度变暗的
山体填充，天空是最暗的 ░，所以「字符浓淡＝海拔高低」本身就是图例。
探针 probe-block 实测：同一字号下空格前进宽 9.0px、块字符 15.0px（0.833em），
混用会被剪切成斜的，因此每一行按颜色切成若干连续段分别定位，段内全是块字符。

里程、高程、坡度、耗时、补水点全部由 waypoints 表算出（见同目录 data.json）；
环线闭合用 assert 校验「累计上升＝累计下降」。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, n                      # noqa: E402
import b03kit as K                                       # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1600, 1000
BG, SKIN, LINE = "#10161C", "#1A222B", "#2A3540"
INK, SOFT, DIM = "#E8E2D4", "#9AA5B1", "#5E6A78"
AMBER, TEAL, VERM, BLUE = "#E0A526", "#6FA8A0", "#C8552B", "#7C9BC4"
MONO = "IBM Plex Mono,Courier New,monospace"
M = 60

# 探针 probe-adv 像素实测：fontSize=20 时 40 个 █ 连续铺满 479px，
# 即前进宽 = 0.60em（12px），空格与块字符同宽；此前 probe-block 的 0.833em 结论作废。
CELL_EM = 0.60
FS = 20.0                       # 字符字号
ADV = FS * CELL_EM              # 单元格宽
CELLS = 116                     # 横向单元数（116×12px ≈ 1392px 画幅）
ROWS = 24                       # 纵向单元数
X0, Y0 = 60.0, 210.0
CH_W, CH_H = CELLS * ADV, ROWS * FS
E_LO, E_HI = 640.0, 1620.0    # 绘图高程窗（峰顶上方留天空，谷底下方留岩体）
M_PER_ROW = (E_HI - E_LO) / (ROWS - 1)

# (公里, 高程m, 地名, 类型)  类型：start/view/water/summit/way/end
WPTS = [(0.0, 720, "云谷停车场", "start"), (1.1, 768, "溪口凉亭", "water"),
        (2.3, 892, "竹林台", "way"), (3.4, 1046, "好汉坡脚", "way"),
        (4.2, 1288, "风垭口", "view"), (4.9, 1240, "松杉界", "water"),
        (5.8, 1372, "老庙遗址", "way"), (6.6, 1480, "云顶峰", "summit"),
        (7.4, 1402, "北坡风口", "view"), (8.5, 1216, "杜鹃灌丛", "view"),
        (9.6, 1024, "石门关", "way"), (10.7, 902, "梯田观景", "water"),
        (11.8, 794, "溪畔栈道", "way"), (12.6, 720, "回到停车场", "end")]
DIST = WPTS[-1][0]
KM_PER_CELL = DIST / (CELLS - 1)
V_EXAG = (KM_PER_CELL * 1000 / ADV) / (M_PER_ROW / FS)   # 剖面垂直放大倍数
ELEV = [w[1] for w in WPTS]
RISE = sum(max(0, b[1] - a[1]) for a, b in zip(WPTS, WPTS[1:]))
FALL = sum(max(0, a[1] - b[1]) for a, b in zip(WPTS, WPTS[1:]))
E_MAX, E_MIN = max(ELEV), min(ELEV)
# 分段：把 14 个点并成 6 段，用于手册的分段表
SEG_DEF = [("云谷 → 竹林台", 0, 2), ("竹林台 → 风垭口", 2, 4), ("风垭口 → 老庙遗址", 4, 6),
           ("老庙遗址 → 云顶峰", 6, 7), ("云顶峰 → 石门关", 7, 10),
           ("石门关 → 停车场", 10, 13)]
SEGS = []
for name, i, j in SEG_DEF:
    km = WPTS[j][0] - WPTS[i][0]
    dz = WPTS[j][1] - WPTS[i][1]
    up = sum(max(0, b[1] - a[1]) for a, b in zip(WPTS[i:j], WPTS[i + 1:j + 1]))
    down = sum(max(0, a[1] - b[1]) for a, b in zip(WPTS[i:j], WPTS[i + 1:j + 1]))
    SEGS.append({"name": name, "i": i, "j": j, "km": km, "dz": dz, "up": up,
                 "down": down,
                 "grade": up / (km * 1000) * 100,
                 "hrs": km / 4.0 + up / 600.0 + down / 900.0})
STEEPEST = max(SEGS, key=lambda s: s["grade"])
NAISMITH = sum(s["hrs"] for s in SEGS)
REST_MIN = 30
TOTAL_MIN = NAISMITH * 60 + REST_MIN
WATER = [w for w in WPTS if w[3] == "water"]
VIEWS = [w for w in WPTS if w[3] == "view"]
LAST_WATER_KM = WATER[-1][0]
assert abs(RISE - FALL) < 1, f"环线不闭合：上升 {RISE} 下降 {FALL}"
assert len(WPTS) == 14 and round(DIST, 1) == 12.6


def elev_at(km):
    """按相邻航点线性插值出任意公里数的高程。"""
    for a, b in zip(WPTS, WPTS[1:]):
        if a[0] <= km <= b[0]:
            t = 0 if b[0] == a[0] else (km - a[0]) / (b[0] - a[0])
            return a[1] + (b[1] - a[1]) * t
    return WPTS[-1][1]


PROFILE = [(i * DIST / (CELLS - 1), elev_at(i * DIST / (CELLS - 1))) for i in range(CELLS)]
row_of = lambda e: int(round((E_HI - e) / (E_HI - E_LO) * (ROWS - 1)))
GRID = [[None] * CELLS for _ in range(ROWS)]
for c, (_km, e) in enumerate(PROFILE):
    s = row_of(e)
    for r in range(ROWS):
        if r < s:
            GRID[r][c] = ("░", "#161D25")                      # 天空
        elif r == s:
            GRID[r][c] = ("█", AMBER)                          # 路面
        elif r <= s + 3:
            GRID[r][c] = ("▓", "#7E6220")
        elif r <= s + 9:
            GRID[r][c] = ("▒", "#4E4327")
        else:
            GRID[r][c] = ("░", "#2C2A22")
SURF = [row_of(e) for _k, e in PROFILE]
_pmax = max(e for _k, e in PROFILE)
_pmin = min(e for _k, e in PROFILE)
assert min(SURF) == row_of(_pmax) and max(SURF) == row_of(_pmin)
assert _pmax <= E_MAX and _pmin >= E_MIN, "采样没有夹住航点极值"
assert row_of(_pmax) >= 2 and row_of(_pmin) <= ROWS - 3, "峰顶/谷底没有留出天空与岩体"

tf = TextFit()
d = Doc(W, H, bg=BG, font="Inter,Noto Sans CJK SC")
d.rect(0, 0, W, H, BG)
d.rect(X0 - 14, Y0 - 14, CH_W + 28, CH_H + 28, SKIN, radius=6)

# ---------- 高程网格线（先画，字符压在网格线之上） ----------
for e in range(700, 1501, 100):
    yy = Y0 + row_of(e) * FS + FS / 2
    d.line(X0 - 14, yy, X0 + CH_W + 14, yy, 1, LINE)
    K.tlab(d, tf, f"ey{e}", 8, yy - 9, 48, 18, f"{e}", 14, DIM, align="END", font=MONO)

# ---------- 字符画网格：每行按颜色连续段分别定位 ----------
for r in range(ROWS):
    c = 0
    while c < CELLS:
        ch, col = GRID[r][c]
        k = c
        while k < CELLS and GRID[r][k] == (ch, col):
            k += 1
        run = ch * (k - c)
        d.pos(X0 + c * ADV, Y0 + r * FS, (k - c) * ADV + 12, FS * 1.16,
              f'<Text fontSize="{n(FS)}" color="{col}" fontFamily="{MONO}" '
              f'height="1.0" softWrap="false"><Raw>{run}</Raw></Text>')
        c = k

# ---------- 真实插值剖面线（盖在字符网格上，补回阶梯缺口） ----------
def true_y(e):
    return Y0 + (E_HI - e) / (E_HI - E_LO) * (ROWS - 1) * FS + FS / 2


def x_of(km):
    """公里数 → 像素 x，与字符单元中心同一套映射（第 c 格中心 = X0 + c*ADV + ADV/2）。"""
    return X0 + km / DIST * (CELLS - 1) * ADV + ADV / 2


PTS = [(X0 + c * ADV + ADV / 2, true_y(e)) for c, (_k, e) in enumerate(PROFILE)]
for (x1, y1), (x2, y2) in zip(PTS, PTS[1:]):
    d.line(x1, y1, x2, y2, 1.6, "#F2ECDD")

# ---------- 公里轴 ----------
for km in range(0, 14, 2):
    xx = x_of(km)
    d.line(xx, Y0 + CH_H + 14, xx, Y0 + CH_H + 22, 1.5, DIM)
    K.tlab(d, tf, f"kx{km}", xx - 26, Y0 + CH_H + 24, 52, 20, f"{km}km", 14, SOFT,
           align="CENTER", font=MONO)

# ---------- 航点标记 ----------
MARK = {"start": ("起", TEAL), "end": ("终", TEAL), "water": ("水", BLUE),
        "view": ("景", VERM), "summit": ("顶", AMBER), "way": ("", SOFT)}
for km, e, nm, kind in WPTS:
    if kind == "way":
        continue
    cx = x_of(km)
    cy = true_y(e)
    lab, col = MARK[kind]
    d.line(cx, cy - 22, cx, cy - 4, 1.5, col)
    d.dot(cx, cy, 5, "#10161C")
    d.dot(cx, cy - 28, 12, col)
    K.tlab(d, tf, f"mk-{nm}", cx - 30, cy - 48, 60, 18, lab, 12, col, align="CENTER",
           style="BOLD")
    if cx - 46 < X0 - 8:          # 最左侧航点：名字标签改左对齐，避免压住高程轴数字
        K.tlab(d, tf, f"mn-{nm}", cx - 8, cy - 68, 110, 20, nm, 13, SOFT)
    else:
        K.tlab(d, tf, f"mn-{nm}", cx - 46, cy - 68, 92, 20, nm, 13, SOFT,
               align="CENTER")

# ---------- 天空留白处的两段括注 ----------
YB = Y0 + 24


def bracket(tag, x1, x2, col, txt, sub):
    d.line(x1, YB, x2, YB, 1.6, col)
    d.line(x1, YB, x1, YB + 9, 1.6, col)
    d.line(x2, YB, x2, YB + 9, 1.6, col)
    K.tlab(d, tf, f"bt-{tag}", (x1 + x2) / 2 - 90, YB - 22, 180, 20, txt, 14, col,
           align="CENTER", style="BOLD")
    K.tlab(d, tf, f"bs-{tag}", (x1 + x2) / 2 - 130, YB + 12, 260, 18, sub, 12, DIM,
           align="CENTER")


b1 = x_of(WPTS[STEEPEST["i"]][0])
b2 = x_of(WPTS[STEEPEST["j"]][0])
bracket("steepest", b1, b2, VERM, f"最陡 {STEEPEST['grade']:.1f}%",
        f"{STEEPEST['up']:.0f}m 爬升 / {STEEPEST['km']:.1f}km")
d1 = x_of(LAST_WATER_KM)
d2 = x_of(DIST)
bracket("dry", d1, d2, BLUE, f"无水 {DIST - LAST_WATER_KM:.1f} km",
        f"{LAST_WATER_KM} km 之后到终点")

# ---------- 标题与关键数字 ----------
K.tlab(d, tf, "title", X0, 30, 700, 46, "云谷环线 · 剖面字符画", 36, INK, style="BOLD",
       spacing=2)
K.tlab(d, tf, "sub", X0, 78, 700, 24, "CLOUD VALLEY LOOP · 12.6 km 闭合环线 · "
                                      "出发前夜读图版", 16, SOFT, spacing=2)
KPI = [("累计上升", f"{RISE:.0f} m"), ("最高 / 最低", f"{E_MAX} / {E_MIN} m"),
       ("预计耗时", f"{TOTAL_MIN / 60:.1f} h 含 {REST_MIN} 分休息"),
       ("最陡段", f"{STEEPEST['name']} {STEEPEST['grade']:.1f}%"),
       ("补水点", f"{len(WATER)} 处 · 最后 {LAST_WATER_KM} km")]
for i, (k, v) in enumerate(KPI):
    x = X0 + i * 292
    d.rect(x, 112, 280, 52, SKIN, radius=6)
    K.tlab(d, tf, f"kl{i}", x + 14, 118, 252, 20, k, 14, DIM)
    K.tlab(d, tf, f"kv{i}", x + 14, 138, 252, 24, v, 18, INK, font=MONO)

# ---------- 分段表 ----------
TY = Y0 + CH_H + 78
K.tlab(d, tf, "seg-hd", X0, TY - 26, 300, 24, "分段数据（由航点表算出）", 17, SOFT,
       style="BOLD")
HEADS = [("路段", 300, "START"), ("里程", 92, "END"), ("上升", 84, "END"),
         ("下降", 84, "END"), ("平均坡", 96, "END"), ("预计", 84, "END")]
cx = X0
for h, wd, al in HEADS:
    K.tlab(d, tf, f"sh-{h}", cx, TY, wd, 22, h, 14, DIM, align=al)
    cx += wd + 12
yy = TY + 26
for i, s in enumerate(SEGS):
    vals = [(s["name"], 300, "START", 15, INK),
            (f"{s['km']:.1f} km", 92, "END", 15, SOFT, MONO),
            (f"+{s['up']:.0f} m" if s["up"] else "0 m", 84, "END", 15, AMBER, MONO),
            (f"−{s['down']:.0f} m" if s["down"] else "0 m", 84, "END", 15, TEAL, MONO),
            (f"{s['grade']:.1f}%", 96, "END", 15,
             VERM if s is STEEPEST else SOFT, MONO),
            (f"{s['hrs']:.1f} h", 84, "END", 15, SOFT, MONO)]
    cx = X0
    for v in vals:
        wd, al = v[1], v[2]
        K.tlab(d, tf, f"sv{i}-{cx}", cx, yy, wd, 22, v[0], v[3], v[4], align=al,
               font=v[5] if len(v) > 5 else None)
        cx += wd + 12
    d.line(X0, yy + 20, X0 + sum(w + 12 for _h, w, _a in HEADS) - 12, yy + 20, 1, LINE)
    yy += 22

# ---------- 图例与提示 ----------
LX = X0 + 980
K.tlab(d, tf, "lg-hd", LX, TY - 26, 340, 24, "字符密度＝海拔", 17, SOFT, style="BOLD")
LEG = [("█", AMBER, f"路面 · 每格 {KM_PER_CELL * 1000:.0f}m 水平 / {M_PER_ROW:.0f}m 垂直"),
       ("▓", "#7E6220", "表层 0–3 格"), ("▒", "#4E4327", "深层 4–9 格"),
       ("░", "#2C2A22", "岩体底部"), ("░", "#161D25", "天空（高于路面处）"),
       ("", "#F2ECDD", "真实插值剖面线（未经字符量化）")]
for i, (ch, col, txt) in enumerate(LEG):
    ly = TY + i * 20
    d.rect(LX, ly + 1, 54, 18, "#0C1116", radius=3)
    if ch:
        d.pos(LX + 3, ly, 54, 22, f'<Text fontSize="16" color="{col}" '
                                 f'fontFamily="{MONO}" softWrap="false">'
                                 f'<Raw>{ch * 4}</Raw></Text>')
    else:
        d.line(LX + 4, ly + 10, LX + 50, ly + 10, 1.8, col)
    K.tlab(d, tf, f"lg{i}", LX + 64, ly, 400, 22, txt, 14, SOFT)
K.tlab(d, tf, "tip0", LX, TY + 124, 460, 22,
       f"剖面纵向放大 {V_EXAG:.1f} 倍（水平 {KM_PER_CELL * 1000 / ADV:.1f}m/px，"
       f"垂直 {M_PER_ROW / FS:.1f}m/px）", 13, DIM)
K.tlab(d, tf, "tip1", LX, TY + 146, 460, 22,
       f"标记：起/终＝停车场 · 水＝可补水 {len(WATER)} 处 · 景＝视点 · 顶＝{E_MAX}m",
       13, DIM)
K.tlab(d, tf, "tip2", LX, TY + 168, 460, 22,
       f"最后补水 {LAST_WATER_KM} km，之后 {DIST - LAST_WATER_KM:.1f} km 无水源；"
       f"行进 {NAISMITH:.1f} h 至少带 1.5 L。", 13, DIM)

K.tlab(d, tf, "foot", X0, H - 34, 700, 22, "云谷环线 · 徒步手册演示数据（航点为虚构）",
       13, DIM)
K.tlab(d, tf, "foot-r", W - 60 - 420, H - 34, 420, 22,
       f"Snapshot DSL · {W}×{H} · {VER}", 13, DIM, align="END", font=MONO)
assert LX + 62 + 400 <= W - 40, LX
assert TY + 190 <= H - 40, TY
assert Y0 + CH_H + 44 <= TY - 26, (Y0 + CH_H, TY)

out = d.dsl()
tmp = ROOT / "tmp" / RID / "B03"
(tmp / f"case07-{VER}.snapshot").write_text(out, encoding="utf-8")
odata = ROOT / "outputs" / RID / "B03" / "case-07"
odata.mkdir(parents=True, exist_ok=True)
(odata / "data.json").write_text(json.dumps({
    "note": "虚构演示数据：路线、地名、高程均为示例；剖面由航点线性插值生成，"
            "耗时用 Naismith 修正式（平路 4km/h + 每 600m 上升 1h + 每 900m 下降 1h）算出。",
    "grid": {"cells": CELLS, "rows": ROWS, "font_size": FS,
             "cell_advance_px": round(ADV, 2),
             "cell_em": CELL_EM,
             "per_cell": {"km": round(KM_PER_CELL, 3), "m": round(M_PER_ROW, 1)},
             "vertical_exaggeration": round(V_EXAG, 2),
             "advance_source": "探针 B03-probe-adv-20261010T111632Z 像素实测："
                              "fontSize=20 时 40 个 █ 连续铺满 479px → 前进宽 12.0px=0.60em，"
                              "块字符墨迹高 24px=1.2em；此前 probe-block 的 0.833em 结论作废"},
    "waypoints": [{"km": w[0], "elev_m": w[1], "name": w[2], "kind": w[3],
                   "row": row_of(w[1]), "profile_row": SURF[round(w[0] / DIST * (CELLS - 1))]}
                  for w in WPTS],
    "totals": {"distance_km": DIST, "rise_m": RISE, "fall_m": FALL,
               "max_m": E_MAX, "min_m": E_MIN, "segments": len(SEGS),
               "walking_hours": round(NAISMITH, 2), "rest_minutes": REST_MIN,
               "total_minutes": round(TOTAL_MIN),
               "steepest_segment": {"name": STEEPEST["name"],
                                    "grade_pct": round(STEEPEST["grade"], 2)},
               "water_points": [w[2] for w in WATER],
               "viewpoints": [w[2] for w in VIEWS],
               "last_water_km": LAST_WATER_KM,
               "dry_stretch_km": round(DIST - LAST_WATER_KM, 1)},
    "segments": [{"name": s["name"], "km": round(s["km"], 2), "up_m": s["up"],
                  "down_m": s["down"], "net_m": s["dz"],
                  "avg_grade_pct": round(s["grade"], 2),
                  "hours": round(s["hrs"], 2)} for s in SEGS],
    "profile_rows": SURF,
    "render": {"canvas": [W, H], "version": VER, "dsl_chars": len(out),
               "image_nodes": out.count("<Image"),
               "raw_text_runs": out.count("<Raw>")},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{VER} chars {len(out)} runs {out.count('<Raw>')} TextFit {tf.n} "
      f"problems {len(tf.problems)} Image {out.count('<Image')}")
for p in tf.problems:
    print("  !", p)
print(f"adv {ADV:.2f} chart {CH_W:.0f}x{CH_H:.0f} TY {TY:.0f} block_bottom {TY + 190:.0f}")
print(f"rise {RISE} fall {FALL} segs {len(SEGS)} steepest {STEEPEST['name']} "
      f"{STEEPEST['grade']:.1f}% walk {NAISMITH:.2f}h total {TOTAL_MIN:.0f}min")
print("surf", min(SURF), max(SURF), "elev@6.6", elev_at(6.6))
