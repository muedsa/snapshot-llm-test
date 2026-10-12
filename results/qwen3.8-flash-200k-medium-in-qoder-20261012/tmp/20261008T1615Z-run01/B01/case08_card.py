"""B01 case-08 · 集换式卡牌 Boss 卡（1000×1400，5:7 标准卡比例）。

受众：桌游玩家在对手亮出这张首领时，只有几秒钟判断"现在打还是先破盾"。
所以卡面必须一眼给出费用/攻防/循环，同时把技能排程、机制、克制倍率和掉落期望
写清楚。全部派生数字（循环伤害、每回合排程、平均伤害、DPS、击破回合、掉落期望、
克制倍率条）都由下面的技能表与掉落表反算，改任一数字整张卡同步。
卡名、数值、扩展编号与掉落均为虚构演示数据。
"""
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit, n  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-08"
OUT.mkdir(parents=True, exist_ok=True)

# ==================== 卡牌数据（虚构） ====================
NAME = "渊环首领 · 盐蚀之壳"
LATIN = "SHELL OF THE BRINE RING"
SUBTITLE = "第三幕 · 首领遭遇 · 永恒（需被封印）"
COST = 7
ATK, DEF, HP = 6, 9, 42
RARITY = "传说"
ELEMENTS = "盐 · 渊 · 环"
SET_INFO = "深渊环鸣扩展 042/120 · 第 3 版"
ILLUS = "图 / 何见山    文 / 沈知远"

# (名, 费用, 伤害, 附加, 冷却回合, 说明)  —— 冷却 0 = 常驻
SKILLS = [
    ("盐柱", 2, 7, "禁锢 1 回合", 2,
     "升起盐柱：对相邻 2 格造成 7 点盐蚀伤害，并禁锢其中 1 个目标 1 回合。"),
    ("渊涌", 5, 14, "全场 · 自损 3", 6,
     "开闸引渊水：对全场所有敌方单位造成 14 点伤害，自身失去 3 点耐久。"),
    ("环鸣", 1, 3, "推离 1 格", 0,
     "以壳震水：对直线 3 格造成 3 点伤害并把目标推离 1 格，每回合限一次。"),
    ("触须抽打", 1, 2, "可重复", 0,
     "甩出壳内触须：对 1 格造成 2 点伤害，同一回合内可反复使用直到行动点耗尽。"),
    ("回环", 3, 0, "自愈 6 · 护甲 +2", 4,
     "闭合外壳：恢复 6 点耐久并获得 2 点护甲，护甲持续 2 回合。"),
]
ONCE_PER_TURN = {"环鸣"}
AP = COST + 1                 # 首领每回合行动点
ARMOR, REGEN, RING = 2, 1, 1  # 回合开始：护甲磨损、耐久再生、环能蓄力
BREAK_MUL = 1.5               # 破盾后受伤倍率

COUNTERS = [("火系 · 熔锤", 1.5), ("盐蚀免疫 · 石工", 0.5), ("常规近战", 1.0),
            ("盐蚀反弹 · 蚀壳", 0.0)]
DROPS = [("盐蚀碎片", 100.0, 3), ("环纹硬壳", 62.0, 1), ("渊水珠", 18.0, 1),
         ("首领印记 · 叁", 8.0, 1)]
FLAVOR = ("它不守门，它就是门。环每转一次，港外的滩涂就少一寸；"
          "老渔民说，退潮之后能听见壳里有人在数账。")

# ==================== 反算派生量 ====================
COOLS = [s[4] for s in SKILLS if s[4]]
CYCLE = max(COOLS) + 1        # 最长冷却 + 1 回合 = 完整循环


def schedule():
    """按"伤害/行动点"效率贪心排程，返回循环内每回合可造成的主动伤害。"""
    out = []
    for r in range(CYCLE):
        ap, dmg = AP, 0
        for nm, cost, dd, _x, cd, _d in sorted(
                [s for s in SKILLS if s[2] > 0],
                key=lambda s: (-s[2] / float(s[1]), -s[2])):
            if cd and r % (cd + 1) != 0:
                continue
            if nm in ONCE_PER_TURN:
                if ap >= cost:
                    dmg += dd
                    ap -= cost
                continue
            while ap >= cost:
                dmg += dd
                ap -= cost
                if cd:
                    break
        out.append(dmg)
    return out


SCHED = schedule()
CYCLE_DMG = sum(SCHED)
AVG_DMG = CYCLE_DMG / float(CYCLE)
PEAK_TURN = max(SCHED)
PLAYER_DMG, PLAYER_HP = 8, 30   # 基准对手：每回合 8 点输出、30 点耐久
TURNS_KILL = math.ceil(HP / float(PLAYER_DMG))
TURNS_KILL_BREAK = math.ceil(HP / float(PLAYER_DMG * BREAK_MUL))
TURNS_SURVIVE = math.ceil(PLAYER_HP / AVG_DMG)
EXPECT_ITEMS = sum(p / 100.0 * q for _n, p, q in DROPS)
EXPECT_RARE = sum(p / 100.0 * q for _n, p, q in DROPS if p < 25)
BEST = max(COUNTERS, key=lambda c: c[1])
WORST = min((c for c in COUNTERS if c[1] > 0), key=lambda c: c[1])

# ==================== 画布 ====================
W, H = 1100, 1540
GOLD = "#C9A227"
CY = "#7FDCEC"
d = Doc(W, H, bg="#050D16",
        palette={"t0": "#E9E2D0", "t1": "#B5C4D4", "t2": "#7E8FA1",
                 "card": "#101F31", "cell": "#0C1928", "deep": "#08131F",
                 "border": "#2A4362", "gold": GOLD, "cyan": CY,
                 "red": "#B4442C", "green": "#8FE0A8"})
P = d.P
tf = TextFit()
tag = "c8"
M = 26
IW = W - 2 * M - 40          # 内区宽
IX = M + 20                  # 内区左


def L(x, y, w, h, s, size, col=None, style=None, align="START", valign="MIDDLE",
      **kw):
    tf.check(tag, s, size, w, h)
    d.label(x, y, w, h, s, col or P["t0"], size, style, align=align,
            valign=valign, **kw)


def R(xr, y, w, h, s, size, col=None, style=None, **kw):
    """右对齐：x 传右边界，内部换算成左边界（L 的 x 永远是左边缘）。"""
    L(xr - w, y, w, h, s, size, col, style, align="END", **kw)


def fr(dd, x, y, w, h, radius, border):
    """Doc.rect 不支持 border，描边要走 Container+box。"""
    dd.pos(x, y, w, h, dd.box(w, h, radius=radius, border=border))


def panel(y, h, fill="#0C1928", border="#22374F", radius=12, x=IX, w=IW):
    # 分栏面板必须显式传 w，否则后一块会整幅盖掉前一块的文字
    assert x >= IX - 0.01 and x + w <= IX + IW + 0.01, (x, w)
    d.rect(x, y, w, h, fill, radius=radius)
    if border:
        fr(d, x, y, w, h, radius, "1 SOLID %s" % border)


# ==================== 卡框与报头 ====================
d.rect(M, M, W - 2 * M, H - 2 * M, "#101F31", radius=26)
fr(d, M, M, W - 2 * M, H - 2 * M, 26, "3 SOLID %s" % GOLD)
fr(d, M + 9, M + 9, W - 2 * M - 18, H - 2 * M - 18, 19, "1 SOLID #2A4362")

d.pos(46, 46, 94, 94, d.box(94, 94, color="#0B2233", radius=47, align="CENTER",
                            inner=K.T(str(COST), d.font, color=GOLD,
                                      fontSize=52, fontStyle="BOLD")))
d.pos(46, 46, 94, 94, d.box(94, 94, radius=47, border="2 SOLID %s" % GOLD))
L(46, 142, 94, 20, "费用", 14, P["t2"], align="CENTER", valign="TOP")

L(156, 50, 560, 38, NAME, 32, P["t0"], "BOLD", valign="TOP")
L(156, 92, 560, 24, LATIN, 16, "#8FA6BD", valign="TOP", spacing=3)
L(156, 120, 620, 22, SUBTITLE, 15, P["t2"], valign="TOP")
d.pos(W - 46 - 92, 50, 92, 32, d.box(92, 32, color=K.hexa(GOLD, 0.16),
                                     radius=16, align="CENTER",
                                     inner=K.T(RARITY, d.font, color=GOLD,
                                               fontSize=17,
                                               fontStyle="BOLD")))
R(W - 46 - 104, 56, 300, 22, SET_INFO, 14, P["t2"], valign="TOP")
R(W - 46 - 104, 82, 300, 22, "%s 属性 · %d 环循环" % (ELEMENTS, CYCLE), 14,
  P["t1"], valign="TOP")

# ==================== 卡面插画 ====================
def art(sd, w, h):
    sd.pos(0, 0, w, h, sd.box(w, h, grad=(
        'gradientType="RADIAL" gradientColors="#123A52,#0A1C2C,#050D16" '
        'gradientRadius="0.92"')))
    cx, cy = w * 0.5, h * 0.60
    for mx, my, ms, ma in [(0.06, 0.16, 3, .30), (0.13, 0.34, 2, .22),
                           (0.20, 0.10, 2, .26), (0.27, 0.44, 3, .18),
                           (0.34, 0.22, 2, .24), (0.41, 0.08, 3, .20),
                           (0.58, 0.12, 2, .24), (0.65, 0.30, 3, .18),
                           (0.72, 0.14, 2, .26), (0.79, 0.40, 3, .20),
                           (0.86, 0.20, 2, .24), (0.93, 0.36, 3, .18),
                           (0.97, 0.10, 2, .22), (0.03, 0.42, 2, .16),
                           (0.47, 0.30, 2, .16), (0.53, 0.44, 2, .14)]:
        sd.rect(mx * w, my * h, ms, ms, K.hexa("#BFE6F2", ma), radius=1)
    for i in range(7):                        # 渊水同心环
        rr = 30 + i * 24
        fr(sd, cx - rr, cy - rr, rr * 2, rr * 2, rr,
           "1 SOLID %s" % K.hexa(CY, 0.22 - i * 0.026))
    ground = h * 0.87
    # 卤水滩：低对比横向条带 + 半沉的圆丘，避免任何“图表条”观感
    for i, (fy, fh, col, a) in enumerate([
            (0.700, 0.055, "#1B3049", 0.55), (0.755, 0.045, "#16293F", 0.60),
            (0.800, 0.050, "#122336", 0.65), (0.850, 0.030, "#0E1D2D", 0.70)]):
        sd.rect(0, fy * h, w, fh * h, K.hexa(col, a))
    for mx, mw, mh, a in [(0.085, 150, 26, 0.55), (0.205, 96, 17, 0.48),
                          (0.288, 62, 11, 0.42), (0.712, 70, 12, 0.42),
                          (0.800, 104, 19, 0.48), (0.928, 158, 27, 0.55)]:
        sd.rect(mx * w - mw / 2, ground - mh, mw, mh * 2.2,
                K.hexa("#0B1725", a), radius=mh)
    sd.rect(0, ground - 1, w, 1, K.hexa("#7FDCEC", 0.12))
    for sx, sw2, sh2 in [(0.038, 13, 44), (0.128, 9, 30), (0.245, 7, 20),
                         (0.755, 7, 22), (0.872, 10, 32),
                         (0.962, 14, 46)]:      # 近景盐柱：暗剪影、只给受光侧棱
        sd.rect(sx * w - sw2 / 2, ground - sh2, sw2, sh2 + 6,
                K.hexa("#0A1624", 0.92))
        sd.rect(sx * w - sw2 / 2, ground - sh2, 1.6, sh2 + 6,
                K.hexa("#4E7A96", 0.42))
        sd.rect(sx * w - sw2 / 2 - 3, ground - 2, sw2 + 6, 4,
                K.hexa("#0A1624", 0.9), radius=2)
    for i, (ry, rw2, ra) in enumerate([(0.895, 0.42, 0.16), (0.912, 0.30, 0.13),
                                       (0.930, 0.50, 0.11), (0.950, 0.24,
                                                             0.09)]):
        sd.rect(w * (0.5 - rw2 / 2) + (i % 2) * 40, ry * h, w * rw2, 1.5,
                K.hexa("#7FDCEC", ra), radius=1)
    for gx, gy, gs in [(0.098, 0.842, 3), (0.212, 0.858, 3), (0.796, 0.856, 3),
                       (0.918, 0.840, 3), (0.288, 0.868, 2)]:   # 盐粒反光
        sd.rect(gx * w - gs / 2, gy * h - gs / 2, gs, gs,
                K.hexa("#E9F2FA", 0.50), radius=1)
    for rr, col in [(98, "#1C3550"), (76, "#27425F"), (54, "#33526F")]:
        sd.rect(cx - rr, cy - rr, rr * 2, rr * 2, col, radius=rr)
    fr(sd, cx - 98, cy - 98, 196, 196, 98, "2 SOLID %s" % GOLD)
    K.glow(sd, cx, cy - 28, 118, GOLD, rings=8, a0=0.05)
    for rr, a in [(84, 0.34), (68, 0.30), (52, 0.26)]:   # 壳内同心生长环
        fr(sd, cx - rr, cy - rr, rr * 2, rr * 2, rr,
           "1 SOLID %s" % K.hexa("#0A1A2B", a))
    for i, ex in enumerate((-54, -27, 0, 27, 54)):   # 壳眼
        sd.rect(cx + ex - 6, cy - 36 - (i % 2) * 13, 12, 12, "#F2E4B8",
                radius=6)
    sd.rect(cx - 17, cy - 17, 34, 34, K.hexa(CY, 0.92), radius=17)
    sd.rect(cx - 8, cy - 8, 16, 16, "#FFFFFF", radius=8)
    sd.rect(0, h * 0.87, w, h * 0.13, K.hexa("#050D16", 0.7))
    for i in range(11):                        # 倒影
        wd = 150 - i * 12
        sd.rect(cx - wd / 2 + (i % 3) * 7, h * 0.88 + i * 3.2, wd, 2,
                K.hexa(CY, 0.28 - i * 0.022), radius=1)


AH = 272
AY = 168
sd = Doc(IW, AH, palette=P)
art(sd, IW, AH)
d.pos(IX, AY, IW, AH,
      '<ClipRRect borderRadius="16" clipBehavior="ANTI_ALIAS"><Container '
      'width="%s" height="%s"><Stack alignment="TOP_LEFT" clipBehavior="NONE">'
      '%s</Stack></Container></ClipRRect>' % (n(IW), n(AH), "".join(sd.parts)))
d.pos(IX, AY, IW, AH, d.box(IW, AH, radius=16, border="1 SOLID #2A4362"))
L(IX + 14, AY + AH - 30, 380, 20, ILLUS, 13, "#9FB4C9", valign="TOP")

# ==================== 数值条 ====================
Y = AY + AH + 14
stats = [("攻击", str(ATK), GOLD), ("防御", str(DEF), CY),
         ("耐久", str(HP), P["green"]), ("护甲", str(ARMOR), "#C9D6E4"),
         ("行动点", str(AP), P["t0"])]
sw = (IW - 4 * 10) / 5.0
for i, (k, v, col) in enumerate(stats):
    x = IX + i * (sw + 10)
    panel(Y, 66, x=x, w=sw)
    L(x, Y + 8, sw, 20, k, 14, P["t2"], align="CENTER", valign="TOP")
    L(x, Y + 30, sw, 30, v, 24, col, "BOLD", align="CENTER", valign="TOP")
Y += 78

# 回合开始结算 + 循环伤害排程
panel(Y, 78)
L(IX + 14, Y + 8, 260, 20, "回合开始结算", 14, P["t2"], valign="TOP")
for i, (lab, note) in enumerate([("+%d 耐久" % REGEN, "再生"),
                                 ("−1 护甲", "磨损至 0 破盾"),
                                 ("+%d 环能" % RING, "3 层可被封印")]):
    x = IX + 14 + i * 128
    d.rect(x, Y + 38, 6, 6, GOLD, radius=3)
    L(x + 12, Y + 30, 60, 20, lab, 15, P["t0"], valign="TOP")
    L(x + 12, Y + 52, 116, 18, note, 13, P["t2"], valign="TOP")
sx0 = IX + 420
L(sx0, Y + 8, 300, 20, "循环伤害排程（%d 回合 · 共 %d 点）" % (CYCLE, CYCLE_DMG),
  14, P["t2"], valign="TOP")
maxs = max(SCHED)
bw = (IX + IW - 14 - sx0 - (CYCLE - 1) * 6) / float(CYCLE)
for i, dd in enumerate(SCHED):
    bh = max(3, 38 * dd / float(maxs))
    x = sx0 + i * (bw + 6)
    d.rect(x, Y + 66 - bh, bw, bh, GOLD if dd == maxs else "#4A6076", radius=3)
    L(x, Y + 28, bw, 16, str(dd), 12, P["t1"], align="CENTER", valign="TOP")
Y += 90

# ==================== 技能表 ====================
L(IX, Y, 200, 24, "技能组", 19, P["t0"], "BOLD", valign="TOP")
R(IX + IW, Y + 2, 420, 22, "按伤害/行动点效率贪心排程", 14, P["t2"],
  valign="TOP")
d.line(IX, Y + 30, IX + IW, Y + 30, 1, P["border"])
Y += 40
SH = 72
for i, (nm, cost, dd, extra, cd, desc) in enumerate(SKILLS):
    panel(Y, SH, fill=P["deep"] if i % 2 else "#0C1928", border=None)
    d.rect(IX, Y, 3, SH, GOLD if cd == 0 else "#3A5670")
    L(IX + 16, Y + 8, 150, 24, nm, 19, GOLD, "BOLD", valign="TOP")
    L(IX + 16, Y + 36, 210, 20, extra, 14, P["t2"], valign="TOP")
    x = IX + 236
    L(x, Y + 8, 70, 24, "%d 费" % cost, 16, P["t0"], align="CENTER",
      valign="TOP")
    L(x + 74, Y + 8, 62, 24, ("%d" % dd) if dd else "—", 19,
      "#FF8A6B" if dd else P["green"], "BOLD", align="CENTER", valign="TOP")
    L(x + 140, Y + 10, 90, 22, ("冷却 %d" % cd) if cd else "常驻", 14,
      P["t1"], valign="TOP")
    R(IX + IW - 14, Y + 10, 120, 22,
      "%.1f 伤/点" % (dd / float(cost)) if cost and dd else "不适用", 14,
      P["t2"], valign="TOP")
    tf.check(tag, desc, 15, IW - 250, 22)
    d.pos(IX + 236, Y + 40, IW - 250, 22,
          d.box(IW - 250, 22, align="TOP_LEFT",
                inner=K.T(desc, d.font, color="#93A6B8", fontSize=15,
                          maxLines=1, overflow="ELLIPSIS")))
    Y += SH + 6
Y += 6

# ==================== 机制 / 克制 ====================
half = (IW - 14) / 2.0
MH = 172
panel(Y, MH)
L(IX + 14, Y + 10, 200, 22, "机制", 17, P["t0"], "BOLD", valign="TOP")
mech = [("破盾", "护甲归零后 2 回合内受到伤害 ×%.1f。" % BREAK_MUL),
        ("蚀壳", "受到近战伤害反弹 3 点，盐蚀伤害不触发反弹。"),
        ("环印", "每被终极技能命中一次环印 +1，满 3 层直接封印。")]
my = Y + 40
for k, v in mech:
    d.rect(IX + 14, my + 6, 6, 6, GOLD, radius=3)
    L(IX + 28, my, 52, 20, k, 15, GOLD, "BOLD", valign="TOP")
    tf.check(tag, v, 14, int(half) - 100, 20)
    L(IX + 82, my, int(half) - 100, 20, v, 14, "#9FB4C9", valign="TOP")
    my += 24
L(IX + 14, Y + MH - 30, int(half) - 28, 20,
  "基准对手 %d 点输出：常规 %d 回合击破 · 破盾窗口 %d 回合" % (
      PLAYER_DMG, TURNS_KILL, TURNS_KILL_BREAK), 13, P["t2"], valign="TOP")

panel(Y, MH, x=IX + half + 14, w=half)
L(IX + half + 28, Y + 10, 240, 22, "克制与伤害倍率", 17, P["t0"], "BOLD",
  valign="TOP")
cyy = Y + 40
maxm = max(c[1] for c in COUNTERS)
for nm, mm in COUNTERS:
    L(IX + half + 28, cyy, 150, 20, nm, 14, "#9FB4C9", valign="TOP")
    track = int(half) - 280
    bx0 = IX + half + 190
    d.rect(bx0, cyy + 4, track, 12, "#16283D", radius=6)
    if mm:
        d.rect(bx0, cyy + 4, max(4, int(track * mm / maxm)), 12,
               P["red"] if mm > 1 else (CY if mm < 1 else "#4A6076"), radius=6)
    R(IX + 2 * half + 14 - 14, cyy, 56, 20, ("×%.1f" % mm) if mm else "免疫",
      14, P["t0"], "BOLD", valign="TOP")
    cyy += 26
L(IX + half + 28, Y + MH - 30, int(half) - 28, 20,
  "最优 %(0)s ×%(1).1f ｜ 最差 %(2)s ×%(3).1f" % {
      "0": BEST[0], "1": BEST[1], "2": WORST[0], "3": WORST[1]},
  13, P["t2"], valign="TOP")
Y += MH + 12

# ==================== 掉落表 ====================
DH = 112
panel(Y, DH)
L(IX + 14, Y + 10, 200, 22, "掉落表", 17, P["t0"], "BOLD", valign="TOP")
R(IX + IW - 14, Y + 12, 420, 20,
  "期望 %.2f 件/场 · 稀有期望 %.3f 件" % (EXPECT_ITEMS, EXPECT_RARE), 14,
  P["t2"], valign="TOP")
dw = (IW - 28) / float(len(DROPS))
for i, (nm, p_, q) in enumerate(DROPS):
    x = IX + 14 + i * dw
    L(x, Y + 38, int(dw) - 12, 20, nm, 15,
      CY if p_ < 25 else P["t0"], valign="TOP")
    L(x, Y + 58, int(dw) - 12, 18, "%.0f%% × %d" % (p_, q), 13, P["t1"],
      valign="TOP")
    tr = int(dw) - 12
    d.rect(x, Y + DH - 30, tr, 12, "#16283D", radius=6)
    d.rect(x, Y + DH - 30, max(6, int(tr * p_ / 100.0)), 12,
           K.hexa(CY if p_ < 25 else GOLD, 0.62), radius=6)
Y += DH + 12

# ==================== 风味与页脚 ====================
FH = 84
d.pos(IX, Y, IW, FH, d.box(IW, FH, align="TOP_LEFT",
                           inner=K.T("「%s」——%s" % (FLAVOR, "青螺港口述"),
                                     d.font, color="#A8BACB", fontSize=16,
                                     height=1.62, maxLines=3)))
tf.check(tag, "「%s」——%s" % (FLAVOR, "青螺港口述"), 16, IW, FH, lines=3)
Y += FH
d.line(IX, Y, IX + IW, Y, 1, P["border"])
L(IX, Y + 10, IW - 300, 20,
  "循环总伤 %d · 回合均伤 %.1f · 峰值 %d · 对手 30 点耐久可活 %d 回合" % (
      CYCLE_DMG, AVG_DMG, PEAK_TURN, TURNS_SURVIVE), 14, P["t1"], valign="TOP")
R(IX + IW, Y + 10, 290, 20, "%s" % SET_INFO.split(" · ")[0], 14, P["t2"],
  valign="TOP")
L(IX, Y + 32, IW, 18,
  "数值为虚构演示数据；排程与掉落期望由本卡技能表、掉落表反算，改任一数字整卡同步。",
  13, "#5E7186", valign="TOP")
BOTTOM = Y + 50

dsl = d.dsl()
(OUT / "case08.snapshot").write_text(dsl, encoding="utf-8")
print("canvas %dx%d bottom %d slack %d bytes %d textfit %d %s" % (
    W, H, BOTTOM, H - M - BOTTOM, len(dsl), tf.n, tf.problems[:6]))
print("cycle %d sched %s total %d avg %.2f peak %d survive %d" % (
    CYCLE, SCHED, CYCLE_DMG, AVG_DMG, PEAK_TURN, TURNS_SURVIVE))
print("kill armor %d break %d  drops expect %.2f rare %.3f" % (
    TURNS_KILL, TURNS_KILL_BREAK, EXPECT_ITEMS, EXPECT_RARE))
