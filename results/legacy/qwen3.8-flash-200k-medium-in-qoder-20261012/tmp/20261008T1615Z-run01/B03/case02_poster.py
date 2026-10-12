"""B03 case-02：「秋声」双日音乐节 Riso 双色海报（1080×1528）。

受众：街头行人（3 秒内决定扫码）＋印厂（核对双色分色与叠色色值）。
手法：程序化半调网点 + 显式叠印分色（探针 10b 的结论是 ColorFiltered 只过滤自身
子树，所以叠色必须按 A / B / A×B 三格自己算）＋ 描边英文字（探针 06）＋
DOTTED 引导线阵容表（探针 07）＋ 套准偏差示意。
所有面积率/网屏/时长由几何与名单数据换算，不手填。名单、地址、票价均为虚构演示数据。
"""
import hashlib
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, minutes      # noqa: E402
import b03kit as K                             # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1080, 1528
M = 54
PRINT_W_MM = 594.0                    # 宣布按 A1 宽度输出
PX_TO_MM = PRINT_W_MM / W
PAPER = "#F3EEE3"
INK_A = "#FF48B0"                     # 第一色：荧光粉（近似）
INK_B = "#0A3AA6"                     # 第二色：靛蓝（近似）


def mul_hex(a, b):
    """Riso 双色叠印的叠色＝两色乘算，色值由两支油墨换算而非手填。"""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(ca[i] * cb[i] / 255) for i in range(3))


INK_AB = mul_hex(INK_A, INK_B)

# ---------- 主视觉网格 ----------
AX, AY = M, 128
AW, AH = W - 2 * M, 520
COLS, ROWS = 38, 20
CW, CH = AW / COLS, AH / ROWS
CELL_MM = CW * PX_TO_MM
SUN_R_PX = 196                            # 日轮半径（像素），换算成 u/v 后是正圆
SUN_CU, SUN_CV = 0.60, 0.42               # v02 看图：半径 216 时日轮顶被网格上界切平
SUN_RU, SUN_RV = SUN_R_PX / AW, SUN_R_PX / AH
MIS_CELLS = 0.5                       # 套准偏差：半个网屏周期
DU, DV = MIS_CELLS / COLS, MIS_CELLS / ROWS


def sun_lum(u, v):
    t = ((u - SUN_CU) / SUN_RU) ** 2 + ((v - SUN_CV) / SUN_RV) ** 2
    if t <= 1.0:
        return 0.0
    if t <= 1.45:
        return (t - 1.0) / 0.45       # 日轮边缘羽化，避免硬切
    return 1.0


def wave_edge(u):
    e1 = 0.665 + 0.055 * math.sin(2 * math.pi * 1.6 * u + 0.5)
    e2 = e1 - 0.150 - 0.022 * math.sin(2 * math.pi * 3.3 * u + 1.9)
    return e1, e2


def refl_lum(u, v):
    """日轮在水面上的倒影（第一色）：以日轮中心为轴的竖带，越深越宽越淡，
    并被细波纹打断。v03 看图：海面下半部是一片满墨，读不出潮线音乐节的「水」。"""
    e1, _ = wave_edge(u)
    if v <= e1:
        return 1.0
    depth = v - e1
    half = 0.05 + 0.34 * depth
    x = abs(u - SUN_CU) / half
    if x >= 1.0:
        return 1.0
    cov = (1 - x ** 1.7) * max(0.0, 0.88 - depth * 0.95)
    cov *= 0.72 + 0.28 * math.sin(u * 46.0 + v * 12.0) ** 2
    return 1.0 - max(0.0, cov)


def sun_lum(u, v):
    t = ((u - SUN_CU) / SUN_RU) ** 2 + ((v - SUN_CV) / SUN_RV) ** 2
    if t <= 1.0:
        disc = 0.0
    elif t <= 1.45:
        disc = (t - 1.0) / 0.45        # 日轮边缘羽化，避免硬切
    else:
        disc = 1.0
    return min(disc, refl_lum(u, v))


def wave_lum(u, v):
    """v 向下增大：海面在波线以下，所以大 v 才是满墨（v01 把这条写反，海印到了天上）。"""
    e1, e2 = wave_edge(u)
    if v <= e2 - 0.02:
        return 1.0                    # 高空：不上靛蓝
    if v <= e2:
        return 1.0 - (v - (e2 - 0.02)) / 0.02 * 0.55
    if v <= e1:
        return 0.45                   # 回声涟漪带：55% 网点（v03 的 42% 读成散点噪声）
    if v <= e1 + 0.02:
        return 0.45 * (1 - (v - e1) / 0.02)
    # 海面：由近岸满墨向深处明显减淡。v05 看图，减淡不够时 #0A3AA6 与叠印
    # #0A1073 都是深色，倒影路径分不出来；留出纸白后 A×B 才成为可读的第三条色带。
    return 0.10 + 0.55 * (v - e1) / (1.0 - e1)


def lumA(u, v):
    return sun_lum(u - DU, v - DV)    # 第一色整体偏移＝套准偏差示意


def lumB(u, v):
    return wave_lum(u, v)


THRESH = 0.12
nA = nB = nAB = TOT = 0
for _r in range(ROWS):
    for _c in range(COLS - (1 if _r % 2 else 0)):        # 与 b03kit.overprint 的错格规则一致
        TOT += 1
        _u, _v = (_c + 0.5) / COLS, (_r + 0.5) / ROWS
        _ca = max(0.0, min(1.0, 1 - lumA(_u, _v)))
        _cb = max(0.0, min(1.0, 1 - lumB(_u, _v)))
        a, b = _ca > THRESH, _cb > THRESH
        if a and b:
            nAB += 1
        elif a:
            nA += 1
        elif b:
            nB += 1
DOTS = nA + nB + nAB
COV_A = (nA + nAB) / TOT
COV_B = (nB + nAB) / TOT
COV_AB = nAB / TOT
MIS_MM = MIS_CELLS * CW * PX_TO_MM

# ---------- 阵容数据（虚构） ----------
LINEUP = [
    ("潮汐台", "主舞台", [("银河清洁队", "24", "14:00", "14:45"), ("长夏乐队", "24", "15:40", "16:25"),
                          ("铁蔷薇", "25", "17:10", "17:55"), ("白鲸电台", "25", "18:40", "19:30")]),
    ("回声棚", "二号舞台", [("潮汐信", "24", "14:30", "15:15"), ("老式闪电", "25", "16:00", "16:45"),
                            ("空白磁带", "24", "17:30", "18:15"), ("苔藓计划", "25", "19:00", "19:50")]),
    ("码头仓", "电子舞台", [("拾光兄弟", "24", "15:00", "16:00"), ("玻璃气象", "25", "16:30", "17:30"),
                            ("南岸信号", "24", "18:00", "19:00"), ("夜莺合作社", "25", "20:30", "21:40")]),
]
ACTS = sum(len(a) for _, _, a in LINEUP)
ALL_ACTS = [a for _, _, acts in LINEUP for a in acts]
D1 = sum(1 for a in ALL_ACTS if a[1] == "24")
D2 = sum(1 for a in ALL_ACTS if a[1] == "25")
SPANS = []
for _, _, acts in LINEUP:
    s0 = min(minutes(a[2]) for a in acts)
    s1 = max(minutes(a[3]) for a in acts)
    SPANS.append((s0, s1, s1 - s0))
STAGE_MIN = sum(x[2] for x in SPANS)
FIRST = min(x[0] for x in SPANS)
LAST = max(x[1] for x in SPANS)


def hhmm(m):
    return "%02d:%02d" % (m // 60, m % 60)


def hm(m):
    return "%d时%02d分" % (m // 60, m % 60)


DAY1, DAY2 = "10.24", "10.25"
VENUE = "潮汐造船厂 · 三号船坞"
TICKETS = [("单日票", 280), ("双日票", 480), ("双日＋营地", 760)]

d = Doc(W, H, PAPER, font="Inter,Noto Sans CJK SC")
tf = TextFit()
d.font = "Inter,Noto Sans CJK SC"

# ---------- 页眉 ----------
K.tlab(d, tf, "hd-l", M, 60, AW * 0.5, 32, "AUTUMN SOUND FESTIVAL ’26",
       21, INK_A, style="BOLD", spacing=3.4)
K.tlab(d, tf, "hd-r", M + AW * 0.5, 60, AW * 0.5, 32,
       f"{DAY1} SAT — {DAY2} SUN · {VENUE.replace(' · ', '')}", 19, INK_B,
       align="END")
d.rect(M, 104, AW, 2, INK_B)

# ---------- 主视觉：双色叠印半调 ----------
K.overprint(d, AX, AY, AW, AH, lumA, lumB, COLS, ROWS,
            INK_A, INK_B, INK_AB, thresh=THRESH, stagger=True)
d.rect(AX, AY + AH + 4, AW, 3, INK_B)   # 版心下线：半调满墨场需要一条明确收边，否则像被裁断

# ---------- 主标题（Riso 套印错位：荧光粉副本先印，靛蓝正本压上） ----------
TITLE = "秋声"
TS = 190
TY = 676
K.tlab(d, tf, "t-ghost", M + 11, TY + 9, 470, 226, TITLE, TS, INK_A, style="BOLD")
K.tlab(d, tf, "t-main", M, TY, 470, 226, TITLE, TS, INK_B, style="BOLD")

RX0 = M + 470 + 26
RW0 = M + AW - RX0
K.tlab(d, tf, "y26", RX0, TY + 2, RW0, 84, "2026", 68, INK_A, style="BOLD",
       align="END")
K.outline(d, tf, "en", RX0, TY + 92, RW0, 54, "TWO-DAY", 46, INK_B,
          align="END", width=1.8)
K.tlab(d, tf, "dates", RX0, TY + 148, RW0, 36, f"{DAY1} — {DAY2} 两日连开",
       24, INK_B, align="END")
K.tlab(d, tf, "clock", RX0, TY + 186, RW0, 30,
       f"三舞台累计 {hm(STAGE_MIN)} · {hhmm(FIRST)}—{hhmm(LAST)}", 19, INK_A, align="END")

# ---------- 英文字幕条 ----------
EY = TY + 240
d.rect(M, EY, AW, 2, INK_A)
K.tlab(d, tf, "en2", M, EY + 12, AW, 50, "QIUSHENG MUSIC FESTIVAL",
       36, INK_A, style="BOLD", fg=INK_A, fg_mode="STROKE", fg_w=1.4, spacing=5)
DTEXT = (f"两日各 {D1} 组" if D1 == D2
         else f"{DAY1} {D1} 组 / {DAY2} {D2} 组")
K.tlab(d, tf, "lineup-hd", M, EY + 66, AW * 0.55, 30,
       f"{ACTS} 组艺人 · {len(LINEUP)} 舞台 · {DTEXT}", 21, INK_B, style="BOLD")
K.tlab(d, tf, "lineup-sub", M + AW * 0.55, EY + 66, AW * 0.45, 30,
       "时间前缀为演出日 · 名单为虚构演示数据", 19, "#8A8271", align="END")

# ---------- 阵容三栏（DOTTED 引导线） ----------
LY = EY + 108
col_w = (AW - 2 * 30) / 3
for i, (nm, role, acts) in enumerate(LINEUP):
    x = M + i * (col_w + 30)
    s0, s1, dur = SPANS[i]
    d.rect(x, LY, 4, 26, INK_A)
    K.tlab(d, tf, "st%d" % i, x + 14, LY, col_w - 14, 28, nm, 24, INK_B, style="BOLD")
    K.tlab(d, tf, "st%d-2" % i, x, LY + 32, col_w, 22,
           f"{role} {hhmm(s0)}—{hhmm(s1)} · {hm(dur)}", 17, "#8A8271")
    yy = LY + 64
    for a_nm, day, t0, t1 in acts:
        nw = min(col_w * 0.50, tf.w(a_nm, 21) + 8)
        K.tlab(d, tf, "act%d-%s" % (i, a_nm), x, yy, nw, 28, a_nm, 21, INK_B)
        tm = f"{day} {t0}–{t1}"
        tw = tf.w(tm, 18) / TextFit.SLACK + 8
        K.tlab(d, tf, "tm%d-%s" % (i, a_nm), x + col_w - tw, yy, tw, 28,
               tm, 18, "#5B5344", align="END")
        k, stop = x + nw + 6, x + col_w - tw - 10
        while k < stop:
            d.dot(k, yy + 13, 3, INK_A)
            k += 11
        yy += 31

# ---------- 下部：分色核对栏 + 抢票区 ----------
BY = 1240
LEFT_W = 560
K.tlab(d, tf, "sep-hd", M, BY, LEFT_W, 28, "双色分色核对（印厂用）", 22, INK_B,
       style="BOLD")
sw = (LEFT_W - 2 * 18) / 3
labels = [("A 荧光粉", INK_A, COV_A), ("A×B 叠印", INK_AB, COV_AB), ("B 靛蓝", INK_B, COV_B)]
for i, (lb, col, cov) in enumerate(labels):
    x = M + i * (sw + 18)
    d.rect(x, BY + 34, sw, 42, col)
    K.tlab(d, tf, "sw%d" % i, x, BY + 80, sw, 24,
           "%s %.1f%%" % (lb, cov * 100), 18, INK_B)
SEP = [
    ("网屏", f"{COLS} 列 × {ROWS} 行 · 点距 {CELL_MM:.1f} mm · 网点 {DOTS} 个"),
    ("叠色", f"{INK_A} × {INK_B} = {INK_AB}（{nAB} 格两色同落）"),
    ("口径", "面积率＝该色上墨格数 / 总格数，叠印格两色都计"),
    ("套准", f"示意偏差 {MIS_MM:.1f} mm · 幅面 {PRINT_W_MM:.0f}×{H * PX_TO_MM:.0f} mm"),
]
yy = BY + 112
for k, v in SEP:
    K.tlab(d, tf, "sep-%s" % k, M, yy, 80, 24, k, 18, INK_A, style="BOLD")
    K.tlab(d, tf, "sepv-%s" % k, M + 84, yy, LEFT_W - 84, 24, v, 18, "#5B5344")
    yy += 24
K.tlab(d, tf, "sep-note", M, yy, LEFT_W, 20,
       "网点为放大示意，付印网屏频率由印厂按设备重制。", 17, "#8A8271")

# 抢票区
TX0 = M + LEFT_W + 40
TW = W - M - TX0
QR_N, MOD = 21, 6
QR_PX = (QR_N - 1) * MOD
QX = W - M - QR_PX
QY = BY + 34
TK_W = TW - QR_PX - 30


def qr_matrix(seed="qiusheng-2026"):
    g = []
    for r in range(QR_N):
        hx = hashlib.md5(("%s-%02d" % (seed, r)).encode()).hexdigest()
        g.append([bool(int(hx[i], 16) & 1) for i in range(QR_N)])

    def finder(ox, oy):
        for r in range(-1, 8):
            for c in range(-1, 8):
                y, x = oy + r, ox + c
                if not (0 <= y < QR_N and 0 <= x < QR_N):
                    continue
                ring = r in (0, 6) or c in (0, 6)
                core = 2 <= r <= 4 and 2 <= c <= 4
                blank = r in (-1, 7) or c in (-1, 7)
                g[y][x] = (ring or core) and not blank
    finder(0, 0)
    finder(QR_N - 7, 0)
    finder(0, QR_N - 7)
    return g


for r, row in enumerate(qr_matrix()):
    for c, on in enumerate(row):
        if on:
            d.rect(QX + c * MOD, QY + r * MOD, MOD, MOD, INK_B)
K.tlab(d, tf, "qr-cta", QX - 40, QY + QR_PX + 8, QR_PX + 80, 26,
       "扫码抢票", 19, INK_B, style="BOLD", align="CENTER")
K.tlab(d, tf, "qr-lb", QX - 40, QY + QR_PX + 34, QR_PX + 80, 24,
       "示意码 · 不可扫描", 16, "#8A8271", align="CENTER")

K.tlab(d, tf, "tk-hd", TX0, BY, TK_W, 28, "票价（虚构）", 22, INK_B,
       style="BOLD")
yy2 = BY + 36
for nm, price in TICKETS:
    K.tlab(d, tf, "tk-%s" % nm, TX0, yy2, 110, 30, nm, 18, "#5B5344")
    K.tlab(d, tf, "tkp-%s" % nm, TX0 + 110, yy2, TK_W - 110, 30,
           K.money(price), 24, INK_A, style="BOLD", align="END")
    yy2 += 32
d.rect(TX0, yy2 + 4, TK_W, 2, INK_A)
K.tlab(d, tf, "tk-foot", TX0, yy2 + 12, TK_W, 26,
       "双日票含寄存", 17, "#8A8271")

# 四角套准标记
for (cx, cy) in ((26, 26), (W - 26, 26), (26, H - 26), (W - 26, H - 26)):
    d.dot(cx, cy, 17, INK_A)
    d.dot(cx, cy, 9, PAPER)
    d.line(cx - 11, cy + 2, cx + 15, cy + 2, 1, INK_B)
    d.line(cx + 2, cy - 11, cx + 2, cy + 15, 1, INK_B)

# ---------- 页脚 ----------
FY = H - 46
d.rect(M, FY - 12, AW, 2, INK_B)
K.tlab(d, tf, "foot", M, FY, AW * 0.58, 26,
       "虚构演示品牌 · 名单 / 地址 / 票价均为演示数据", 16, "#8A8271")
K.tlab(d, tf, "ver", M + AW * 0.58, FY, AW * 0.42, 26,
       f"B03 case-02 · {VER} · 1080×1528",
       16, "#8A8271", align="END")

assert LY + 64 + 4 * 31 <= BY, "阵容栏与下部核对栏重叠"
BOTTOMS = {"sep": yy + 20, "qr": QY + QR_PX + 58, "ticket": yy2 + 38}
assert max(BOTTOMS.values()) <= FY, "下部区块越出页脚线：%s" % BOTTOMS
print("bottoms", BOTTOMS, "FY", FY)

dsl = d.dsl()
out = ROOT / "tmp" / RID / "B03" / f"case02-{VER}.snapshot"
out.write_text(dsl, encoding="utf-8")
print(VER, "chars", len(dsl), "TextFit", tf.n, "problems", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
print("AB", INK_AB, "dots", DOTS, "A", nA, "B", nB, "AB", nAB,
      "covA %.3f covB %.3f covAB %.3f" % (COV_A, COV_B, COV_AB),
      "cell_mm %.1f mis %.1f" % (CELL_MM, MIS_MM),
      "acts", ACTS, "stage_min", STAGE_MIN, hhmm(FIRST), hhmm(LAST))
