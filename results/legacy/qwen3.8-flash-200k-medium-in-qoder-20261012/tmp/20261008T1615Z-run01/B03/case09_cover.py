"""B03 case-09：《裁》文化季刊封面（遮罩拼贴，1080×1440）。

受众与情境：报刊亭读者在一米外扫过封面，要在两秒内被主题抓住（一块由纸型本身
长出来的拼贴），走近后才读出特辑标题与要目，并判断这本讲「纸张尺寸」的杂志是否
值得一翻。

独到手法：拼贴不是装饰性色块，而是 **ISO 216 的裁半序列本身**——
A0 到 A6 七级每级沿长边裁半，方向按 下→右→上→左→下→右 走出风车螺旋，
所以每一块被遮罩裁出的窗口的**边界就是真实纸型的边界**；上级纸型露出的那半个
恰好是同级的另一半，画面因此可以逐块核算，而不是好看而已。

1. 七级窗口各自 ClipRRect 遮罩 + Container transform 旋转（0～±1.5°）故意错位，
   模拟多版套印的套准偏差；错位量写进 data.json 供核对。
2. 每个窗口是一整墙正文：按该级纸面尺寸算出行列数，再从 242 字本辑导语循环取样
   填满，字数＝cols×rows 可算；行内每三行改一次描边（foregroundMode=STROKE）与
   实心行混排，既是疏密纹理，也是本件要探的 STROKE/实心混排。
3. 字号随纸型递减（22/19/16/14/12/11/10），最大块 504 字、最小块 12 字，读者看到
   的是同一段文字在七种纸面上的密度差；每块先给本级标签让出一条横带，正文只在
   剩下的带子里排行列，所以标签压不到字（v06）。
4. √2 用 ClipOval 遮罩出的环（圆环＝ClipOval 裁掉同心内圆）作真尺规转移：单位
   正方形→对角线→以原点为心、对角线为半径的圆交 x 轴于 √2→过交点的垂线。图上
   半径与对角线是同一个长度，故作图本身无近似；页上另写清真正的误差来自取整。
5. 所有数字由计算给出：纸型由 A0 递推（⌊长边÷2⌋）并与标准表逐级 assert 比对；
   A0 面积 0.999949 m² 与定义值 1 m² 差 0.51 cm²；80 g/m² 克重（500 张 A4＝2.49 kg）；
   版面容量模型给出「纸面 16.03 倍 vs 版心 21.07 倍 vs 字数 21.54 倍」的可读结论。
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
from dslkit import Doc, TextFit, n                       # noqa: E402
import b03kit as K                                        # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1080, 1440
PAPER, INK, RED = "#F4EFE6", "#17150F", "#C2402A"
GRAY, LIGHT, DEEP = "#8C8577", "#E7DFD1", "#2B2620"
SANS = "Inter,Noto Sans CJK SC"
MONO = "IBM Plex Mono,Courier New,monospace"
M = 40
RAD = 6                       # 所有窗口共用同一圆角，拼贴才像一个模子出来的

# ---------------- 导语（正文墙的唯一字源） ----------------
PASSAGE = ("纸是有秩序的。一秒钟里你摸到过四次这种秩序：地铁票、药盒说明书、"
           "咖啡杯上的杯套、手里那张刚打印出来的合同。它们的长宽都约等于一点四一四，"
           "这不是巧合，是一九二二年写进德国工业标准的一条几何规定：把长边对折再对折，"
           "形状永远不变。于是一台复印机可以从容地把 A3 缩进 A4，一套书可以从 A4 拆到 A6，"
           "一张 A0 的纸恰好是一平方米——它是所有尺寸的母体，却几乎从不单独出现。"
           "我们把它拆开，摊平，按裁半的顺序排成一列，让每一级自己说明：纸的秩序是什么，"
           "以及这秩序替我们省下了多少犹豫。")
P_LEN = len(PASSAGE)

# ---------------- ISO 216：由 A0 递推 ----------------
PUB = {"A0": (841, 1189), "A1": (594, 841), "A2": (420, 594), "A3": (297, 420),
       "A4": (210, 297), "A5": (148, 210), "A6": (105, 148)}


def gen(n_seq):
    """ISO 216 定义式递推：新短边＝⌊上一级长边÷2⌋，新长边＝上一级短边。"""
    out, (w0, h0) = [], (841, 1189)
    for i in range(n_seq):
        if i:
            w0, h0 = h0 // 2, w0
        out.append((f"A{i}", w0, h0))
    return out


SIZES = gen(7)
for name, sw, sh in SIZES:
    assert (sw, sh) == PUB[name], (name, sw, sh, PUB[name])
ISO = {name: (sw, sh) for name, sw, sh in SIZES}

area_m2 = {k: (v[0] / 1000.0) * (v[1] / 1000.0) for k, v in ISO.items()}
gsm = 80.0
weight_g = {k: v * gsm for k, v in area_m2.items()}
A0_AREA, A4_AREA = area_m2["A0"], area_m2["A4"]
RATIO_ERR = ISO["A0"][1] - ISO["A0"][0] * math.sqrt(2)      # 1189-841√2 = -0.35 mm
RATIO_ERR_A4 = ISO["A4"][1] - ISO["A4"][0] * math.sqrt(2)   # 297-210√2 = +0.02 mm
RECT_ERR = ISO["A0"][1] / ISO["A0"][0] - math.sqrt(2)       # +0.00042
REAM_KG = 500 * weight_g["A4"] / 1000.0

# ---------------- 排版容量模型（假设写在页上） ----------------
MARGIN_MM, PT, PT_MM, LEAD = 20.0, 10.5, 0.3528, 1.6
CHAR_MM = PT * PT_MM
LINE_MM = CHAR_MM * LEAD


def cap(mm_w, mm_h):
    cols = int((mm_w - 2 * MARGIN_MM) // CHAR_MM)
    rows = int((mm_h - 2 * MARGIN_MM) // LINE_MM)
    return cols, rows, cols * rows


CAP = {k: cap(*ISO[k]) for k in ("A0", "A4")}
BODY_W = {k: ISO[k][0] - 2 * MARGIN_MM for k in ("A0", "A4")}
BODY_H = {k: ISO[k][1] - 2 * MARGIN_MM for k in ("A0", "A4")}
BODY_AREA = {k: BODY_W[k] * BODY_H[k] for k in ("A0", "A4")}
PAPER_RATIO = A0_AREA / A4_AREA
BODY_RATIO = BODY_AREA["A0"] / BODY_AREA["A4"]
CHAR_RATIO = CAP["A0"][2] / CAP["A4"][2]
DRIFT_MM = math.floor(BODY_W["A4"] / CHAR_MM) * CHAR_MM - BODY_W["A4"]
DRIFT_CHARS = DRIFT_MM / CHAR_MM

# ---------------- 拼贴几何 ----------------
CW, CH = 600, 790
S = min(CW / ISO["A0"][0], CH / ISO["A0"][1])
PX = {k: (v[0] * S, v[1] * S) for k, v in ISO.items()}
S0W, S0H = PX["A0"]
CX0, CY0 = M, 320.0
HALVES = ["下", "右", "上", "左", "下", "右"]
ROT = [0.0, -1.2, 0.9, -0.7, 1.5, -1.0, 0.7]
SIZES_PT = [22, 19, 16, 14, 12, 11, 10]
BGK = [INK, RED, LIGHT, "#9E3524", PAPER, DEEP, "#C7BFAF"]
FGK = [PAPER, PAPER, INK, PAPER, INK, "#D9CFBC", INK]
assert len(ROT) == len(SIZES) == len(BGK) == len(FGK) == len(SIZES_PT)


def sub_rect(i):
    """第 i 级窗口在父级窗口里占的那一半（风车顺序，裁的都是长边）。"""
    x, y, w, h = CX0, CY0, S0W, S0H
    for lv in range(1, i + 1):
        side = HALVES[lv - 1]
        if h >= w:                       # 竖幅：沿高（长边）裁半
            h = h / 2.0
            y += h if side == "下" else 0.0
        else:                            # 横幅：沿宽（长边）裁半
            w = w / 2.0
            x += w if side == "右" else 0.0
    return x, y, w, h


for i in range(7):
    x, y, w, h = sub_rect(i)
    pw, ph = PX[SIZES[i][0]]
    # 裁半后的纸面是同一张纸转了 90°，所以允许长短边互换；0.4px 差来自标准表的取整
    assert (abs(w - pw) < 0.6 and abs(h - ph) < 0.6) or \
        (abs(w - ph) < 0.6 and abs(h - pw) < 0.6), (i, w, h, pw, ph)
    assert CX0 - 12 <= x and x + w <= CX0 + CW + 12, (i, x, w)
    assert CY0 - 12 <= y and y + h <= CY0 + CH + 12, (i, y, h)


def metrics(idx):
    """窗口落位槽 + 该级字号（pad/pitch/adv 全由字号推出）。"""
    sx, sy, fw, fh = sub_rect(idx)
    size = SIZES_PT[idx]
    return sx, sy, fw, fh, size, size * 0.42, size * 1.5, size * 1.02


def wall(idx, tag):
    """一个窗口 = ClipRRect 遮罩 + 纯色底 + 整墙正文（每三行改一次描边）。

    绘制尺寸取**落位槽**而不是 ISO 表的长短边顺序：裁半后同一张纸转了 90°，
    文字仍按水平排，所以槽是横幅就画横幅（assert 已允许长短边互换）。
    标签先定位，正文再让出标签所在的那条横带，标签就不压在字上（v06）。
    """
    name = SIZES[idx][0]
    sx, sy, fw, fh, size, pad, pitch, adv = metrics(idx)
    top, bot = pad, fh - pad
    if tag is not None:
        _, ty, _, th0, _, c = tag
        if c in (0, 1):
            top = max(top, ty + th0 + 8 - sy)
        else:
            bot = min(bot, ty - 8 - sy)
    cols = int((fw - 2 * pad) // adv)
    rows = int((bot - top) // pitch)
    total = cols * rows
    assert rows >= 1, name
    pos = []
    for r in range(rows):
        seg = "".join(PASSAGE[(r * cols + j) % P_LEN] for j in range(cols))
        stroke = (r % 3 == 1)
        mk = K.text_markup(seg, size, FGK[idx], font=SANS,
                           **({"fg": FGK[idx], "fg_mode": "STROKE", "fg_w": 1.0}
                              if stroke else {}))
        yy = top + r * pitch
        pos.append(f'<Positioned left="{n(pad)}" top="{n(yy)}" '
                   f'width="{n(fw - 2*pad)}" height="{n(pitch)}">'
                   f'<Container width="{n(fw - 2*pad)}" height="{n(pitch)}" '
                   f'alignment="CENTER_LEFT">{mk}</Container></Positioned>')
    inner = (f'<ClipRRect borderRadius="{n(RAD)}" clipBehavior="ANTI_ALIAS">'
             f'<Container width="{n(fw)}" height="{n(fh)}" color="{BGK[idx]}">'
             f'<Stack alignment="TOP_LEFT">' + "".join(pos) + "</Stack></Container>"
             "</ClipRRect>")
    m = K.rotate(math.radians(ROT[idx]))
    x, y = sx, sy
    d.pos(x, y, fw, fh, f'<Container width="{n(fw)}" height="{n(fh)}" '
                        f'transform="{K.matrix_attr(m)}" transformAlignment="CENTER">'
                        f"{inner}</Container>")
    return cols, rows, total


d = Doc(W, H, bg=PAPER, font=SANS)
tf = TextFit()

# ---------- 底：纸张纹理与拼贴区底衬 ----------
for yy in range(0, H, 6):
    d.rect(0, yy, W, 1, "#EFE9DE")
d.rect(CX0 - 12, CY0 - 12, S0W + 24, S0H + 24, "#EAE3D6")

# ---------- 报头 40–290 ----------
K.outline(d, tf, "mast", M, 26, 150, 168, "裁", 130, INK, width=3.0)
K.tlab(d, tf, "mast-cn", M + 164, 40, 340, 34, "裁 · 文 化 季 刊", 26, INK,
       style="BOLD", height=1.0)
K.tlab(d, tf, "mast-en", M + 166, 78, 420, 22, "CAI CULTURE QUARTERLY", 17, GRAY,
       font=MONO)
K.tlab(d, tf, "mast-issue", M + 166, 108, 420, 22, "2026 秋季号 · 总第 037 期",
       17, INK, font=MONO)
K.tlab(d, tf, "hl-kicker", M + 166, 140, 420, 24, "特辑 / ISO 216", 19, RED,
       style="BOLD", font=MONO)
for j, (lab, val) in enumerate((("定价", "48.00 元"), ("邮发代号", "80-317"),
                                ("ISSN", "2026-0037"))):
    K.tlab(d, tf, f"mp-{j}", 700, 40 + j * 26, 158, 22, lab, 15, GRAY, font=MONO)
    K.tlab(d, tf, f"mv-{j}", 862, 40 + j * 26, 178, 22, val, 15, INK, font=MONO,
           align="END")
d.line(M, 186, 1040, 186, 2.4, INK)
d.line(M, 192, 1040, 192, 1.0, GRAY)
K.tlab(d, tf, "hl", M, 212, 500, 62, "一平方米的秩序", 56, INK, style="BOLD",
       height=1.0)
K.tlab(d, tf, "hl-sub", M + 504, 226, 496, 46, "——纸张如何规定了你手里的每一页",
       24, INK, height=1.0, align="END")
d.rect(1004, 280, 36, 6, RED)

# ---------- 拼贴（七级窗口）：先定标签，再画正文墙，最后压标签 ----------
def corner(x, y, w, h, tw, th, c):
    """0 左上 / 1 右上 / 2 左下 / 3 右下，距边 9px（留出旋转余量）。"""
    return (x + (9 if c in (0, 2) else w - tw - 9),
            y + (9 if c in (0, 1) else h - th - 9), tw, th)


def overlaps(a, b):
    return (a[0] < b[0] + b[2] and b[0] < a[0] + a[2]
            and a[1] < b[1] + b[3] and b[1] < a[1] + a[3])


# TAG[name] = (x, y, w, h, 是否双行, 角位)
TAG, PLACED = {}, []
for i in range(7):
    name = SIZES[i][0]
    x, y, w, h = sub_rect(i)
    # 标签放在本级**露出来的那一半**：子级占哪一半，标签就避开那一半的角。
    # 候选＝角位 × 纵向微调；先双行（含 mm 与克重），放不下退成单行；
    # 全部相撞就 assert 报错，绝不静默丢标签（case-08 同一手法）。
    side = HALVES[i] if i < 6 else "下"
    pref = {"下": 0, "右": 0, "上": 2, "左": 1}[side]
    order = [pref] + [c for c in range(4) if c != pref]
    pos = big = corner_used = None
    for th, tw2, big2 in ((50, min(214, max(64, w - 18)), True),
                          (20, max(34, min(120, w - 18)), False)):
        if th == 50 and tw2 < 150:
            continue
        for c in order:
            for dy in (0, 22, -22, 44, -44, 66):
                bx, by, _, _ = corner(x, y, w, h, tw2, th, c)
                r = (bx, by + dy, tw2, th)
                if r[1] < y + 4 or r[1] + th > y + h - 4:
                    continue
                if any(overlaps(r, q) for q in PLACED):
                    continue
                pos, big, corner_used = r, big2, c
                break
            if pos:
                break
        if pos:
            break
    assert pos, name
    PLACED.append(pos)
    TAG[name] = pos + (big, corner_used)

WALL = {}
for i in range(7):
    name = SIZES[i][0]
    WALL[name] = wall(i, TAG[name])

TAGS = []
for i in range(7):
    name = SIZES[i][0]
    tx, ty, tw0, th0, big, c = TAG[name]
    cols, rows, total = WALL[name]
    hh = 54 if big else 24
    # 浅色描边垫一层：深色板（A5 DEEP）上深色标签会糊成一片（v05 看图）
    d.pos(tx - 2, ty - 2, tw0 + 4, hh, f'<Container width="{n(tw0 + 4)}" '
          f'height="{hh}" borderRadius="5" color="{PAPER}"/>')
    d.pos(tx, ty, tw0, 26 if big else 20, f'<Container width="{n(tw0)}" '
          f'height="{26 if big else 20}" borderRadius="4" color="#12100CD9"/>')
    K.tlab(d, tf, f"tag-{name}", tx + 6, ty, tw0 - 12, 26 if big else 20,
           f"{name} {ISO[name][0]}×{ISO[name][1]} mm" if big
           else (f"{name} {total}字" if tw0 >= 64 else name),
           15 if big else 11, PAPER, font=MONO)
    if big:
        d.pos(tx, ty + 28, tw0, 22, f'<Container width="{n(tw0)}" height="22" '
                                    f'borderRadius="4" color="#12100CB3"/>')
        K.tlab(d, tf, f"tag2-{name}", tx + 6, ty + 28, tw0 - 12, 22,
               f"{cols}×{rows}＝{total} 字 · {weight_g[name]:.0f} g", 13, "#E7DFD1",
               font=MONO)
    TAGS.append((name, round(tx), round(ty), round(tw0), 50 if big else 20, big))

# ---------- 右栏 690–1040 ----------
RX, RW = 690, 350
RY = 300
K.tlab(d, tf, "col0", RX, RY, RW, 24, "开本表 / 由 A0 递推", 20, INK, style="BOLD")
d.line(RX, RY + 30, RX + RW, RY + 30, 1.6, INK)
HEAD = ("名", "宽×高 mm", "短边÷长边", "面积 m²", "80g")
HW = [34, 100, 92, 88, 36]
assert sum(HW) <= RW
yy = RY + 42
for j, hd in enumerate(HEAD):
    d.pos(RX + sum(HW[:j]), yy, HW[j], 20,
          f'<Container width="{HW[j]}" height="20" alignment="CENTER_LEFT">'
          + K.text_markup(hd, 12, GRAY, font=MONO) + "</Container>")
yy += 22
for r_i, (name, sw, sh) in enumerate(SIZES):
    row = (name, f"{sw}×{sh}", f"{sw/sh:.6f}", f"{area_m2[name]:.6f}",
           f"{weight_g[name]:.0f}")
    for j, val in enumerate(row):
        K.tlab(d, tf, f"tb{r_i}-{j}", RX + sum(HW[:j]), yy, HW[j] - 4, 20, val, 13,
               RED if r_i == 0 else INK, font=MONO)
    if r_i < 6:
        d.line(RX, yy + 21, RX + RW, yy + 21, 0.8, "#C9C1B2")
    yy += 22
TBL_END = yy
NOTE1 = ("递推：新短边＝⌊上一级长边÷2⌋，新长边＝上一级短边。七级与 ISO 216 标准表"
         f"逐级 assert 相等。A0＝841×1189 算得 {A0_AREA:.6f} m²，比定义的 1 m² 少 "
         f"{(1-A0_AREA)*1e4:.2f} cm²（{abs(A0_AREA-1)*100:.3f}%）。")
K.tlab(d, tf, "col1", RX, TBL_END + 8, RW, 62, NOTE1, 12, INK, lines=5,
       height=1.35, font=MONO)
yy = TBL_END + 72
K.outline(d, tf, "ratio", RX, yy, RW, 46, "1 : 1.414214", 34, INK, width=1.4,
          font=MONO)
yy += 52
NOTE2 = (f"841×√2＝{ISO['A0'][0]*math.sqrt(2):.2f} mm，标准取 {ISO['A0'][1]} mm，"
         f"舍去 {RATIO_ERR:.2f} mm；A4 则是 {ISO['A4'][0]}×√2＝"
         f"{ISO['A4'][0]*math.sqrt(2):.2f}→{ISO['A4'][1]}，进 {RATIO_ERR_A4:.2f} mm。"
         f"A0÷A4＝{PAPER_RATIO:.2f}，而 2⁴＝16。")
K.tlab(d, tf, "round", RX, yy, RW, 62, NOTE2, 12, INK, lines=5, height=1.35,
       font=MONO)
yy += 68

# √2 作图（ClipOval 遮罩出的圆环：半径＝对角线，交点即 √2）
K.tlab(d, tf, "con-t", RX, yy, RW, 22, "√2 的作图（ClipOval 圆环）", 15, INK,
       style="BOLD")
yy += 26
UNIT = 62.0
DIAG = UNIT * math.sqrt(2)
RING_T = 3.0
OX = RX + 92
OY = yy + DIAG + 26                       # 正方形底边＝x 轴
LX, LY = OX + UNIT, OY - UNIT
RD = 2 * DIAG                                # 圆环直径（半径＝对角线长）
ring = (f'<ClipOval clipBehavior="ANTI_ALIAS">'
        f'<Container width="{n(RD)}" height="{n(RD)}" color="{INK}">'
        f'<Stack alignment="TOP_LEFT"><Positioned left="{n(RING_T)}" '
        f'top="{n(RING_T)}" width="{n(RD - 2*RING_T)}" height="{n(RD - 2*RING_T)}">'
        f'<Container width="{n(RD - 2*RING_T)}" height="{n(RD - 2*RING_T)}" '
        f'color="{PAPER}" borderRadius="{n((RD-2*RING_T)/2)}"/></Positioned></Stack>'
        "</Container></ClipOval>")
# 圆环先画：环心的内圆是用底色填出来的，后画就会盖掉正方形与对角线（v05 的缺陷）
d.pos(OX - DIAG, OY - DIAG, RD, RD, ring)
d.rect(OX, OY - UNIT, UNIT, UNIT, "#EDE6D9")
for seg in ((OX, OY - UNIT, OX + UNIT, OY - UNIT), (OX + UNIT, OY - UNIT,
                                                    OX + UNIT, OY),
            (OX + UNIT, OY, OX, OY), (OX, OY, OX, OY - UNIT)):
    d.line(*seg[:2], *seg[2:], 1.8, INK)
d.line(OX, OY, LX, LY, 1.4, RED)             # 对角线，长度＝√2·UNIT
IX = OX + DIAG
d.line(OX - 8, OY, IX + 8, OY, 1.2, INK)
d.dot(IX, OY, 7, RED)
d.line(IX, OY, IX, OY - UNIT, 1.4, INK)
d.dot(OX, OY, 5, INK)
d.dot(LX, LY, 5, RED)
K.tlab(d, tf, "con-1", OX - 8, OY + 7, UNIT + 16, 18, "边长 1", 12, INK, font=MONO,
       align="CENTER")
K.tlab(d, tf, "con-2", IX + 10, OY + 7, 40, 18, "√2", 12, RED, font=MONO,
       align="START", height=1.0)
K.tlab(d, tf, "con-3", RX, OY + DIAG + 8, RW, 50,
       "弧心＝正方形原点，半径＝对角线，所以交点到原点的距离就是 √2 本身；半径与"
       "对角线是同一个长度，作图本身没有近似。", 12, GRAY, lines=3, height=1.3)
CON_END = OY + DIAG + 8 + 56
ARC_HIT = math.sqrt(DIAG ** 2 - 20.0 ** 2)   # 弧在轴上方 20 px 处的横距
NOTE4 = (f"误差来自取整而非几何：比值偏差 {RECT_ERR:+.6f} 使 A0 的 1189 mm 比 "
         f"841√2 短 {abs(RATIO_ERR):.2f} mm，A4 反过来进 {RATIO_ERR_A4:.2f} mm；"
         f"而 A4 版心宽 {BODY_W['A4']:.0f} mm 除以 {CHAR_MM:.3f} mm 得 {CAP['A4'][0]} "
         f"字余 {DRIFT_MM:.2f} mm（{DRIFT_CHARS:.1f} 个字宽），这截空白正是行宽要"
         f"回算的原因。")
K.tlab(d, tf, "con-6", RX, CON_END, RW, 74, NOTE4, 12, INK, lines=6, height=1.35,
       font=MONO)
RIGHT_END = CON_END + 74
assert RIGHT_END <= 1120, RIGHT_END
assert OX - DIAG >= RX - 14 and IX + 8 <= 1040, (OX - DIAG, IX + 8)
assert OY - DIAG >= yy + 24, (OY - DIAG, yy)

# ---------- 底部 1122–1440 ----------
BY = 1148
d.line(M, BY - 24, 1040, BY - 24, 2.4, INK)
K.tlab(d, tf, "toc-t", M, BY - 18, 220, 26, "本辑要目", 21, INK, style="BOLD")
K.tlab(d, tf, "toc-sub", M + 232, BY - 10, 320, 20, "（刊名、篇名与页码为设计示意）",
       12, GRAY, font=MONO)
TOC = [("一平方米的母体：A0 为什么恰好是一平方米", "04"),
       ("对折的形状不变：1:√2 的唯一性与它的舍入误差", "18"),
       ("从报纸到名片：B 系、C 系与信封的三级台阶", "36"),
       ("重迭克数：80 g/m² 换算成一张纸的重量", "52"),
       ("版心的算式：装订、页边与每行四十五个字", "70")]
ty = BY + 16
for t, pg in TOC:
    K.leader_dots(d, M, ty, 604, t, f"P {pg}", 19, INK, GRAY, dot=3, pitch=13,
                  title_w=520, page_w=84)
    ty += 34
TOC_END = ty
K.tlab(d, tf, "cap0", M, TOC_END + 2, 620, 20,
       f"每行字数＝版心宽÷{CHAR_MM:.3f} mm，行数＝版心高÷{LINE_MM:.3f} mm。",
       12, GRAY, font=MONO)

# 容量对比条
BAR_X, BAR_W0 = 700, 170
by = BY + 16
K.tlab(d, tf, "cap-t", BAR_X, by - 4, 340, 22, "A0 对 A4：纸面比 ≠ 版心比", 17,
       INK, style="BOLD")
by += 26
for lab, val, colr in (("纸面比", PAPER_RATIO, INK), ("版心比", BODY_RATIO, RED),
                       ("字数比", CHAR_RATIO, DEEP)):
    K.tlab(d, tf, f"cb-{lab}", BAR_X, by, 62, 20, lab, 14, INK)
    bw = BAR_W0 * val / BODY_RATIO
    d.rect(BAR_X + 66, by + 4, bw, 12, colr)
    K.tlab(d, tf, f"cv-{lab}", BAR_X + 66 + bw + 5, by, 58, 20, f"{val:.2f}", 13,
           INK, font=MONO)
    by += 27
NOTE5 = (f"A4 版面 {CAP['A4'][0]}×{CAP['A4'][1]}＝{CAP['A4'][2]:,} 字，"
         f"A0 版面 {CAP['A0'][0]}×{CAP['A0'][1]}＝{CAP['A0'][2]:,} 字；"
         f"边衬固定使版心比 {BODY_RATIO:.2f}＞纸面比 {PAPER_RATIO:.2f}；"
         f"500 张 A4（80 g）＝{REAM_KG:.2f} kg。")
K.tlab(d, tf, "cap-1", BAR_X, by + 4, 340, 56, NOTE5, 12, INK, lines=4,
       height=1.3, font=MONO)
CAP_END = by + 4 + 56

# 条码示意（放右下，容量块下方）
BCY = CAP_END + 8
seq = f"9{ISO['A0'][0]}{ISO['A0'][1]}{int(round(S*1000))}"
widths = []
for ch in seq:
    widths.extend([2 if int(ch) % 2 else 1, 1])
BCX = 700
cx = BCX
for i, wd in enumerate(widths):
    if i % 2 == 0:
        d.rect(cx, BCY, wd * 3.0, 34, INK)
    cx += wd * 3.0
K.tlab(d, tf, "bc-w", cx + 6, BCY + 6, 120, 24, "非可扫描编码", 12, GRAY,
       font=MONO)
K.tlab(d, tf, "bc-n", BCX, BCY + 36, cx - BCX, 16, seq, 11, INK, font=MONO,
       align="CENTER")
BARCODE_END = BCY + 34
assert cx + 126 <= 1040, cx
assert BARCODE_END <= 1384, BARCODE_END

# 页脚披露
K.tlab(d, tf, "foot-1", M, 1394, 640, 40,
       "开本尺寸、面积、克重、字数与 √2 作图为 ISO 216 与本页排版模型算出的真实数据；"
       "刊名、期号、代号与要目篇名为设计示意。", 12, DEEP, lines=2, height=1.3)
K.tlab(d, tf, "foot-2", 700, 1394, 340, 20,
       f"字源 {P_LEN} 字 · Snapshot DSL {W}×{H} {VER}", 12, GRAY, font=MONO,
       align="END")

out = d.dsl()
tmp = ROOT / "tmp" / RID / "B03"
(tmp / f"case09-{VER}.snapshot").write_text(out, encoding="utf-8")
odata = ROOT / "outputs" / RID / "B03" / "case-09"
odata.mkdir(parents=True, exist_ok=True)
(odata / "data.json").write_text(json.dumps({
    "ver": VER, "canvas": [W, H], "dsl_chars": len(out), "passage_chars": P_LEN,
    "iso216": [{"name": nm, "w_mm": a, "h_mm": b, "area_m2": round(area_m2[nm], 8),
                "weight_g_80gsm": round(weight_g[nm], 3),
                "px_at_scale": [round(PX[nm][0], 2), round(PX[nm][1], 2)],
                "rect_px": [round(v, 2) for v in sub_rect(i)],
                "wall": {"cols": WALL[nm][0], "rows": WALL[nm][1],
                         "chars": WALL[nm][2]},
                "rot_deg": ROT[i], "bg": BGK[i], "fg": FGK[i],
                "font_px": SIZES_PT[i],
                "tag": [t for t in TAGS if t[0] == nm][0][1:]}
               for i, (nm, a, b) in enumerate(SIZES)],
    "recursion": "new_short=floor(prev_long/2); new_long=prev_short（与标准表逐级 assert 相等）",
    "checks": {"table_match": True, "a0_area_m2": round(A0_AREA, 8),
               "a0_minus_definition_m2": round(A0_AREA - 1.0, 8),
               "ratio_sqrt2_err": round(RECT_ERR, 8),
               "rounding_err_a0_mm": round(RATIO_ERR, 4),
               "rounding_err_a4_mm": round(RATIO_ERR_A4, 4),
               "paper_area_ratio_a0_a4": round(PAPER_RATIO, 6),
               "body_ratio": round(BODY_RATIO, 6), "char_ratio": round(CHAR_RATIO, 6),
               "ream_kg_500": round(REAM_KG, 4),
               "construction_px_per_unit": round(UNIT, 3),
               "construction_arc_setback_px": round(DIAG - ARC_HIT, 3),
               "construction_unit_px": UNIT, "construction_radius_px": round(DIAG, 3)},
    "type_model": {"margin_mm": MARGIN_MM, "pt": PT, "pt_mm": PT_MM, "leading": LEAD,
                   "char_mm": round(CHAR_MM, 4), "line_mm": round(LINE_MM, 4),
                   "a4": {"cols": CAP["A4"][0], "rows": CAP["A4"][1],
                          "chars": CAP["A4"][2], "body_w_mm": BODY_W["A4"],
                          "body_h_mm": BODY_H["A4"]},
                   "a0": {"cols": CAP["A0"][0], "rows": CAP["A0"][1],
                          "chars": CAP["A0"][2], "body_w_mm": BODY_W["A0"],
                          "body_h_mm": BODY_H["A0"]},
                   "row_drift_mm": round(DRIFT_MM, 4),
                   "row_drift_chars": round(DRIFT_CHARS, 3)},
    "collage": {"scale_px_per_mm": round(S, 5), "origin": [CX0, CY0],
                "halves_sequence": HALVES, "radius_px": RAD},
    "fictional": ["刊名《裁》/CAI CULTURE QUARTERLY", "2026 秋季号·总第 037 期",
                  "定价 48.00 元", "邮发代号 80-317", "ISSN 2026-0037",
                  "五篇要目篇名与页码", "条码（非可扫描编码）"],
    "layout_ys": {"mast": [26, 298], "collage": [CY0, CY0 + CH], "right_col":
                  [RY, round(RIGHT_END, 1)], "bottom": [BY - 24, 1434]},
    "textfit": {"checked": tf.n, "problems": tf.problems},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{VER} chars {len(out)} TextFit {tf.n} problems {len(tf.problems)} "
      f"ClipRRect {out.count('<ClipRRect')} ClipOval {out.count('<ClipOval')} "
      f"transform {out.count('transform=')} STROKE {out.count('STROKE')} "
      f"pos {out.count('<Positioned')} nodes {len(d.parts)}")
for p in tf.problems:
    print("  !", p)
print("iso", SIZES)
print(f"S {S:.5f} px/mm  A0 {S0W:.1f}x{S0H:.1f}  a0_area {A0_AREA:.6f}")
print(f"round a0 {RATIO_ERR:+.3f} a4 {RATIO_ERR_A4:+.3f} rect_err {RECT_ERR:+.6f}")
print(f"paper {PAPER_RATIO:.3f} body {BODY_RATIO:.3f} chars {CHAR_RATIO:.3f} "
      f"drift {DRIFT_MM:.2f}mm/{DRIFT_CHARS:.2f}字 ream {REAM_KG:.2f}kg")
print("caps", WALL)
print("tags", TAGS)
print(f"tbl_end {TBL_END} right_end {RIGHT_END:.0f} con_end {CON_END:.0f} "
      f"toc_end {TOC_END:.0f} cap_end {CAP_END:.0f} barcode {BARCODE_END:.0f} cx {cx:.0f}")
