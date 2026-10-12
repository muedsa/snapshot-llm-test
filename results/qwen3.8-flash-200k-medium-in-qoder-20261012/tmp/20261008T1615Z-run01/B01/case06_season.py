"""B01 case-06 · 手游赛季更新长图（1080×H，竖屏叙事 + 卡片流）。

受众：《深空回响》玩家，在公众号/社区群里竖着刷完，目标 90 秒内回答
「几点停服、新赛季有什么、我值不值得抽、零氪能不能满级通行证、哪些枪被砍了」。
全部数字来自本文件顶部的一份赛季数据表：天数、阶段划分、平衡改动百分比、
通行证满级所需天数、抽卡期望与花费、包体大小互相反算，改一处整图同步。
游戏名、干员、武器、数值、概率全部为虚构演示数据。
"""
import datetime as dt
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-06"
OUT.mkdir(parents=True, exist_ok=True)

# ==================== 赛季数据（唯一来源） ====================
GAME = "深空回响"
SEASON = "潮汐纪元"
CODE = "S7"
VERSION = "v3.7.0"
BUILD = "20261016.04"
START = dt.date(2026, 10, 16)
END = dt.date(2026, 12, 24)
DAYS = (END - START).days + 1
MAINT = ("10-16 04:00", "10-16 11:00", 7)          # 停服起 / 止 / 小时
PKG = {"Android": 3.42, "iOS": 3.61, "补丁包": 1.28}

PHASES = [
    (dt.date(2026, 10, 16), dt.date(2026, 10, 29), "潮汐开启",
     ["新干员「澜汐」实装", "限时副本·沉没剧场", "通行证前 20 级双倍"]),
    (dt.date(2026, 10, 30), dt.date(2026, 11, 12), "深渊回声",
     ["新干员「洛恩」实装", "团本「盐之王座」开放", "弦弓类武器平衡热修"]),
    (dt.date(2026, 11, 13), dt.date(2026, 11, 26), "盐粒风暴",
     ["新系统：天气影响弹道", "PVP 排位赛段重置", "旧赛季皮肤返场投票"]),
    (dt.date(2026, 11, 27), dt.date(2026, 12, 24), "长潮终幕",
     ["赛季结算与称号发放", "通行证末段奖励", "S8 预告直播 12-20 20:00"]),
]

ROSTER_AVG = {"hp": 9600, "atk": 1345, "def": 742}   # 现版本全干员均值
HEROES = [
    {"name": "澜汐", "role": "潮汐 · 控场", "rarity": "SSR", "hp": 8420,
     "atk": 1268, "def": 612, "cd": 18, "cost": 4,
     "skill": "涌潮领域", "note": "范围内敌方弹道偏移 6°，持续 5 s",
     "color": "#38BDF8"},
    {"name": "洛恩", "role": "铸潮 · 突击", "rarity": "SSR", "hp": 11240,
     "atk": 1584, "def": 884, "cd": 22, "cost": 6,
     "skill": "盐之重锤", "note": "命中后护盾 -35%，冷却期间自身减伤 20%",
     "color": "#FBBF24"},
]
STAT_MAX = {"hp": 12000, "atk": 1700, "def": 950}

# (对象, 指标, 旧值, 新值, 单位, 对玩家是否有利)
BALANCE = [
    ("弦弓「裂风」", "后坐力系数", 0.42, 0.36, "", True),
    ("弦弓「裂风」", "蓄力时间", 0.85, 0.72, "s", True),
    ("重装「壁垒-Ⅶ」", "护盾持续", 6.0, 4.5, "s", False),
    ("重装「壁垒-Ⅶ」", "展开耗氧", 24, 31, "", False),
    ("霰弹「盐鸦」", "有效射程", 12.5, 9.8, "m", False),
    ("霰弹「盐鸦」", "单发伤害", 26, 29, "", True),
    ("干员·柯尔", "被动回能", 3.0, 4.2, "/s", True),
    ("干员·薇拉", "闪避冷却", 9.0, 7.5, "s", True),
    ("干员·薇拉", "闪避无敌帧", 0.30, 0.22, "s", False),
    ("团本「盐之王座」", "Boss 血量", 100, 88, "%", True),
    ("天气系统", "暴雨弹道偏移", 0, 4.0, "°", False),
    ("赛季币", "周获取上限", 1200, 1500, "", True),
]

PASS = {"levels": 60, "xp_low": 1000, "low_to": 50, "xp_high": 1500,
        "daily": 4 * 120, "weekly": 5 * 600, "explore": 6000,
        "bonus_free": 0, "bonus_pass": 380, "bonus_season": 260}
PASS["total_xp"] = PASS["low_to"] * PASS["xp_low"] + \
    (PASS["levels"] - PASS["low_to"]) * PASS["xp_high"]
PASS["per_day"] = PASS["daily"] + PASS["weekly"] / 7.0

GACHA = {"ssr": 0.016, "sr": 0.134, "up": 0.008, "pity": 60,
         "pull_price": 160, "ten_discount": 0.95}


def pct(old, new):
    if old == 0:
        return None
    return (new - old) / old * 100.0


def tier_days(bonus):
    need = PASS["total_xp"] - PASS["explore"]
    return need / (PASS["per_day"] + bonus)


def expected_pulls(p, pity):
    """硬保底下的出货期望抽数（几何分布 + 第 pity 抽必出）。"""
    e = 0.0
    surv = 1.0
    for k in range(1, pity):
        e += k * p * surv
        surv *= (1 - p)
    e += pity * surv
    return e


EXP_PULLS = expected_pulls(GACHA["ssr"], GACHA["pity"])
EXP_COST = EXP_PULLS * GACHA["pull_price"]
P60 = 1 - (1 - GACHA["ssr"]) ** GACHA["pity"]
TEN_E = (GACHA["pull_price"] * 10 * GACHA["ten_discount"]) / GACHA["pull_price"]

# 派生量
PHASE_LEN = [(b - a).days + 1 for a, b, _, _ in PHASES]
BUFF = sum(1 for r in BALANCE if r[5])
NERF = len(BALANCE) - BUFF
T_FREE = tier_days(PASS["bonus_free"])
T_PASS = tier_days(PASS["bonus_pass"])
T_SEA = tier_days(PASS["bonus_pass"] + PASS["bonus_season"])

# ==================== 画布 ====================
W = 1080
M = 48
CW = W - 2 * M
PAL = {"card": "#0E1B2E", "card2": "#132640", "border": "#22405F",
       "row": "#0B1626", "t0": "#F2F7FF", "t1": "#A8C0DA", "t2": "#6E87A3",
       "cyan": "#38BDF8", "amber": "#FBBF24",
       "green": "#34D399", "red": "#FB7185", "violet": "#A78BFA",
       "teal": "#2DD4BF", "pink": "#F472B6", "blue": "#60A5FA"}
PAL["grid"] = "#1B3350"
d = Doc(W, 4000, bg="#050D18", palette=PAL)
tf = TextFit()
P = d.P
tag = "c6"


def L(x, y, w, h, s, size, col=None, style=None, align="START", valign="MIDDLE",
      **kw):
    tf.check(tag, s, size, w, h)
    d.label(x, y, w, h, s, col or P["t0"], size, style, align=align,
            valign=valign, **kw)


def chip(x, y, s, col, bg=None, size=17, pad=14, h=30, radius=None):
    wd = pad * 2 + tf.w(s, size)
    d.pos(x, y, wd, h, d.box(wd, h, color=bg or K.hexa(col, 0.16),
                             radius=radius if radius is not None else h / 2,
                             border="1 SOLID %s" % K.hexa(col, 0.5),
                             align="CENTER",
                             inner=K.T(s, d.font, color=col, fontSize=size,
                                       fontStyle="BOLD")))
    return wd


def header(y, no, title, sub):
    d.rect(M, y + 4, 7, 40, P["teal"], radius=3)
    L(M + 24, y, 620, 40, title, 29, P["t0"], "BOLD", valign="TOP")
    L(M + 24, y + 44, 780, 24, sub, 17, P["t2"], valign="TOP")
    L(W - M - 90, y + 4, 90, 34, no, 22, P["t2"], "BOLD", align="END")
    return y + 82


def card_bg(x, y, w, h, radius=16, color=None, border=None):
    d.pos(x, y, w, h, d.box(w, h, color=color or P["card"], radius=radius,
                            border=border if border is not None
                            else "1 SOLID %s" % P["border"]))


# ==================== 1. HERO ====================
HY = 470
d.pos(0, 0, W, HY + 120, d.box(W, HY + 120, grad=(
    'gradientType="LINEAR" gradientColors="#0A2340,#05121F,#0B1B33,#050D18" '
    'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"')))
K.radial_disc(d, W - 452, 8, 520, ["#38BDF8AA", "#1E6F9F55", "#050D1800"],
              radius="0.62")
K.sweep_disc(d, W - 168, 150, 132,
             ["#38BDF8", "#A78BFA", "#F472B6", "#FBBF24", "#34D399", "#38BDF8"],
             hole=0.72)
K.sweep_disc(d, W - 168, 150, 88,
             ["#FBBF24", "#F472B6", "#38BDF8", "#FBBF24"], hole=0.55)
L(M, 46, 700, 26, "%s %s · 赛季更新速览" % (GAME, CODE), 19, P["t1"],
  valign="TOP")
K.stroke(d, M - 6, 74, 900, 128, SEASON, 104, P["teal"], fill="#0A2340",
         sw=3, align="TOP_LEFT", spacing=2)
K.neon(d, M, 208, 900, 54, "LONG TIDE ERA", 34, color=P["t2"],
       shadow="0 0 14 #38BDF866", valign="TOP")
L(M, 258, CW, 26, "停服更新 %s → %s（%d 小时）· 赛季 %d 天 · 新干员 %d 名 · 平衡改动 %d 项"
  % (MAINT[0], MAINT[1], MAINT[2], DAYS, len(HEROES), len(BALANCE)),
  18, P["t1"], valign="TOP")
L(M, 288, CW, 26, "增强 %d 项 / 削弱 %d 项 · 通行证 %d 级 · 概率已公示"
  % (BUFF, NERF, PASS["levels"]), 18, P["t2"], valign="TOP")

# 毛玻璃 KPI 条（压在光晕上，验证 BackdropFilter 真实生效）
FY = 336
K.frosted(d, M, FY, CW, 112, radius=18, sigma=16, tint="#0B1B2E5C",
          border="#7DD3FC88")
KPIS = [("赛季天数", "%d" % DAYS, "天", P["cyan"]),
        ("新干员", "%d" % len(HEROES), "名", P["amber"]),
        ("平衡改动", "%d" % len(BALANCE), "项", P["violet"]),
        ("通行证", "%d" % PASS["levels"], "级", P["green"])]
kw = (CW - 3 * 1) / 4.0
for i, (t, v, u, c) in enumerate(KPIS):
    x = M + i * (CW / 4.0)
    L(x + 26, FY + 18, 200, 24, t, 17, P["t2"], valign="TOP")
    d.pos(x + 26, FY + 46, 240, 46, K.T(
        '<Text color="%s" fontSize="40" fontStyle="BOLD" fontFamily="%s">%s</Text>'
        '<Text color="#A8C0DA" fontSize="20" fontFamily="%s"> %s</Text>'
        % (c, d.font, v, d.font, u), d.font))
    if i:
        d.line(x, FY + 22, x, FY + 90, 1, "#7DD3FC44")
Y = HY + 40

# ==================== 2. 新干员 ====================
Y = header(Y, "01", "新干员 · 数值直读",
           "柱＝该属性占全干员最高值比例，右侧百分比＝与现版本均值差")
CH = 402
cw2 = (CW - 26) / 2.0
for i, hd in enumerate(HEROES):
    x = M + i * (cw2 + 26)
    card_bg(x, Y, cw2, CH, border="1 SOLID %s" % K.hexa(hd["color"], 0.45))
    K.radial_disc(d, x + cw2 - 150, Y - 40, 220,
                  [K.hexa(hd["color"], 0.55), "#0E1B2E00"], radius="0.55")
    L(x + 24, Y + 22, 240, 40, hd["name"], 34, P["t0"], "BOLD", valign="TOP")
    L(x + 24, Y + 68, 300, 24, hd["rarity"] + " · " + hd["role"], 18,
      hd["color"], valign="TOP")
    chip(x + cw2 - 118, Y + 24, " COST " + str(hd["cost"]), hd["color"], h=30)
    cy = Y + 106
    for key, lab in (("hp", "生命"), ("atk", "攻击"), ("def", "防御")):
        v = hd[key]
        ratio = v / float(STAT_MAX[key])
        diff = (v - ROSTER_AVG[key]) / float(ROSTER_AVG[key]) * 100.0
        L(x + 24, cy, 60, 22, lab, 17, P["t2"])
        bw = cw2 - 92 - 190
        d.rect(x + 92, cy + 6, bw, 12, P["row"], radius=6)
        d.rect(x + 92, cy + 6, bw * ratio, 12, hd["color"], radius=6)
        L(x + 92 + bw + 10, cy, 62, 22, "%+.0f%%" % diff, 15,
          P["green"] if diff >= 0 else P["red"], valign="TOP")
        L(x + cw2 - 24 - 66, cy, 66, 22, format(v, ","), 17, P["t0"],
          align="END", valign="TOP")
        cy += 38
    d.line(x + 24, cy + 2, x + cw2 - 24, cy + 2, 1, P["border"])
    L(x + 24, cy + 14, 300, 24, "技能「%s」" % hd["skill"], 19, P["t0"], "BOLD",
      valign="TOP")
    L(x + 24, cy + 44, cw2 - 48, 48, hd["note"], 17, P["t1"], valign="TOP",
      maxlines=2, height=1.35)
    d.rect(x + cw2 - 130, cy + 96, 106, 30, P["card2"], radius=15)
    L(x + cw2 - 130, cy + 96, 106, 30, "CD %ds" % hd["cd"], 16, hd["color"],
      align="CENTER")
Y += CH + 46

# ==================== 3. 平衡改动 ====================
Y = header(Y, "02", "平衡改动 · %d 项" % len(BALANCE),
           "箭头＝数值升降方向，颜色与文字＝对玩家的利弊；百分比由新旧值直接算出")
RH = 46
th = len(BALANCE) * RH + RH + 26
card_bg(M, Y, CW, th)
widths = [214, 176, 168, 108, 260]
heads = ["对象", "指标", "旧 → 新", "变化", "对局影响"]
cx = M + 18
for i, htxt in enumerate(heads):
    L(cx, Y + 16, widths[i] - 12, 24, htxt, 16, P["t2"], "BOLD",
      align="END" if i == 3 else "START", valign="TOP")
    cx += widths[i]
d.line(M + 18, Y + 44, M + CW - 18, Y + 44, 1, P["border"])
ry = Y + 50
for r, (obj, met, old, new, unit, good) in enumerate(BALANCE):
    if r % 2 == 0:
        d.rect(M + 12, ry, CW - 24, RH, P["row"], radius=8)
    cx = M + 18
    col = P["green"] if good else P["red"]
    L(cx, ry, widths[0] - 12, RH, obj, 17, P["t0"], valign="TOP"); cx += widths[0]
    L(cx, ry, widths[1] - 12, RH, met, 17, P["t1"], valign="TOP"); cx += widths[1]
    L(cx, ry, widths[2] - 12, RH, "%g%s → %g%s" % (old, unit, new, unit), 17,
      P["t0"], valign="TOP"); cx += widths[2]
    p = pct(old, new)
    txt = "新增" if old == 0 else "%+.1f%%" % p
    L(cx, ry, widths[3] - 12, RH, txt, 17, col, "BOLD", align="END",
      valign="TOP"); cx += widths[3]
    arrow = "＋" if p is None else ("↑" if p > 0 else "↓")
    word = "利好" if good else "削弱"
    pill = ('<WidgetSpan alignment="MIDDLE" width="28" height="22">'
            '<Container width="28" height="22" color="%s" borderRadius="11" '
            'alignment="CENTER"><Text color="#05131F" fontSize="15" '
            'fontFamily="%s">%s</Text></Container></WidgetSpan>'
            % (K.hexa(col, 0.92), d.font, arrow))
    tf.check(tag, " " + word, 17, widths[4] - 12 - 48, RH)
    d.pos(cx + 14, ry, widths[4] - 12 - 14, RH, d.box(
        widths[4] - 12 - 14, RH, align="CENTER_LEFT",
        inner=K.T(pill + " " + word, d.font, color=col, fontSize=17)))
    ry += RH
Y += th + 46

# ==================== 4. 通行证 ====================
Y = header(Y, "03", "赛季通行证 · 能不能满级",
           "三档玩家的满级天数由每日经验反算，全部要 ≤ 赛季 %d 天" % DAYS)
PH = 300
card_bg(M, Y, CW, PH)
K.sweep_disc(d, M + 150, Y + PH / 2.0, 108,
             ["#34D399", "#38BDF8", "#A78BFA", "#F472B6", "#FBBF24", "#34D399"],
             hole=0.66)
d.rect(M + 150 - 66, Y + PH / 2.0 - 66, 132, 132, P["card"], radius=66)
L(M + 150 - 66, Y + PH / 2.0 - 30, 132, 34, "%d 级" % PASS["levels"], 26,
  P["t0"], "BOLD", align="CENTER", valign="TOP")
L(M + 150 - 66, Y + PH / 2.0 + 6, 132, 22,
  "共 " + format(PASS["total_xp"], ",") + " 经验", 15, P["t2"],
  align="CENTER", valign="TOP")
tx = M + 300
tiers = [("零氪（日常+周常+探索）", PASS["per_day"] + PASS["bonus_free"], P["green"]),
         ("战令通行证（+%d/日）" % PASS["bonus_pass"],
          PASS["per_day"] + PASS["bonus_pass"], P["cyan"]),
         ("战令 + 赛季任务（+%d/日）" % (PASS["bonus_pass"] + PASS["bonus_season"]),
          PASS["per_day"] + PASS["bonus_pass"] + PASS["bonus_season"], P["amber"])]
L(tx, Y + 22, 600, 26, "满级所需天数（赛季共 %d 天）" % DAYS, 19, P["t0"],
  "BOLD", valign="TOP")
cy = Y + 62
for name, per, col in tiers:
    days = (PASS["total_xp"] - PASS["explore"]) / per
    L(tx, cy, 330, 24, name, 17, P["t1"])
    bw = (CW - (tx - M) - 210)
    d.rect(tx, cy + 30, bw, 14, P["row"], radius=7)
    d.rect(tx, cy + 30, bw * min(1.0, days / float(DAYS)), 14, col, radius=7)
    L(tx + bw + 14, cy + 24, 150, 26, "%d 天 / 余 %d 天" % (
        math.ceil(days), DAYS - math.ceil(days)), 17, col, "BOLD", align="END")
    cy += 62
L(tx, Y + PH - 44, CW - (tx - M) - 24, 24,
  "日常 4×120 ＋ 周常 5×600÷7 ＝ %.0f/日，探索 %s 为一次性"
  % (PASS["per_day"], format(PASS["explore"], ",")), 15, P["t2"],
  valign="BOTTOM")
Y += PH + 46

# ==================== 5. 概率公示 ====================
Y = header(Y, "04", "抽取概率公示",
           "硬保底 %d 抽；期望抽数按「前 %d 抽几何分布 + 第 %d 抽必出」逐抽求和"
           % (GACHA["pity"], GACHA["pity"] - 1, GACHA["pity"]))
GH = 386
card_bg(M, Y, CW, GH)
L(M + 26, Y + 22, 700, 26, "单次抽取概率构成（10 连必含 1 张 SR 及以上）",
  19, P["t0"], "BOLD", valign="TOP")
bx0, bwid, by, bh = M + 26, CW - 52, Y + 58, 40
comp = [("SSR 星潮", GACHA["ssr"], P["amber"]),
        ("SR 稀有", GACHA["sr"], P["violet"]),
        ("R 普通", 1 - GACHA["ssr"] - GACHA["sr"], P["slate"])]
cx = bx0
for name, p, col in comp:
    d.rect(cx, by, bwid * p, bh, col)
    cx += bwid * p
d.rect(bx0, by, bwid * GACHA["up"], bh, P["pink"])
d.line(bx0 + bwid * GACHA["up"], by, bx0 + bwid * GACHA["up"], by + bh, 1,
       "#FFFFFF")
d.line(bx0 + 4, by + bh, bx0 + 4, Y + 112, 1, P["border"])
L(bx0 + 12, Y + 104, 640, 22,
  "紫＋黄＝UP %.1f%% / SSR %.1f%%，真实比例下合计只有 %.0f px 宽"
  % (GACHA["up"] * 100, GACHA["ssr"] * 100, bwid * GACHA["ssr"]), 14, P["t2"], valign="TOP")
cy = Y + 134
for name, p, col in comp:
    d.dot(M + 34, cy + 11, 12, col)
    L(M + 50, cy, 220, 24, name, 17, P["t1"], valign="TOP")
    L(M + 270, cy, 90, 24, "%.1f%%" % (p * 100), 19, col, "BOLD", align="END",
      valign="TOP")
    L(M + 380, cy, 260, 24, "每 1000 抽约 %d 次" % round(p * 1000), 15, P["t2"],
      valign="TOP")
    cy += 30
d.line(M + 26, cy + 10, M + CW - 26, cy + 10, 1, P["border"])
facts = [("出货期望", "%.1f 抽" % EXP_PULLS, "含 %d 抽硬保底" % GACHA["pity"]),
         ("60 抽内出货", "%.1f%%" % (P60 * 100),
          "1 − (1 − p) 的 %d 次方" % GACHA["pity"]),
         ("期望花费", "%s 星声" % format(int(round(EXP_COST)), ","),
          "%.2f 抽 × %d" % (EXP_PULLS, GACHA["pull_price"])),
         ("十连折扣", "%.2f 折" % GACHA["ten_discount"],
          "%d 星声/10 抽" % round(TEN_E * GACHA["pull_price"]))]
fx = M + 26
for t, v, s in facts:
    fw = 224
    d.rect(fx, cy + 26, fw, 92, P["card2"], radius=12)
    L(fx + 16, cy + 38, fw - 32, 22, t, 15, P["t2"], valign="TOP")
    L(fx + 16, cy + 62, fw - 32, 30, v, 23, P["amber"], "BOLD", valign="TOP")
    L(fx + 16, cy + 94, fw - 32, 20, s, 13, P["t2"], valign="TOP")
    fx += fw + 12
L(M + 26, Y + GH - 26, CW - 52, 20,
  "以上概率为演示值；出货期望 = Σ k·p·(1−p)^(k−1) + %d·(1−p)^%d"
  % (GACHA["pity"], GACHA["pity"] - 1), 13, P["t2"], valign="TOP")
Y += GH + 46

# ==================== 6. 版本日历 ====================
Y = header(Y, "05", "赛季阶段与时间轴",
           "四段天数由起止日期反算，合计 %d 天 = 赛季总天数" % sum(PHASE_LEN))
XH = 286
card_bg(M, Y, CW, XH)
axis = Y + 104
tot = float(sum(PHASE_LEN))
x = M + 30
for i, ((a, b, name, items), ln) in enumerate(zip(PHASES, PHASE_LEN)):
    seg = (CW - 60) * ln / tot
    col = [P["cyan"], P["amber"], P["violet"], P["green"]][i]
    L(x + 2, axis - 46, seg - 10, 26, "P%d · %s" % (i + 1, name), 18, col,
      "BOLD", valign="TOP")
    d.rect(x, axis, seg - 4, 18, col, radius=9)
    L(x, axis, seg - 4, 18, "%d/%d–%d/%d · %d 天"
      % (a.month, a.day, b.month, b.day, ln), 12, "#05131F", "BOLD",
      align="CENTER")
    iy = axis + 34
    for it in items:
        d.dot(x + 8, iy + 11, 5, K.hexa(col, 0.8))
        L(x + 20, iy, seg - 26, 22, it, 14, P["t1"], valign="TOP")
        iy += 26
    x += seg
L(M + 30, Y + XH - 34, CW - 60, 22,
  "阶段划分只影响开放内容与双倍窗口，通行证经验获取全程一致"
  "（S8 预告 12-20 20:00 直播）", 15, P["t2"], valign="TOP")
Y += XH + 40

# ==================== 页脚 ====================
FH = 150
d.pos(0, Y, W, FH, d.box(W, FH, grad=(
    'gradientType="LINEAR" gradientColors="#050D18,#0A2340" '
    'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"')))
d.line(M, Y + 1, W - M, Y + 1, 1, P["border"])
L(M, Y + 22, 500, 26, "%s %s build %s" % (GAME, VERSION, BUILD), 18, P["t1"],
  "BOLD", valign="TOP")
L(M, Y + 52, 620, 24, "停服更新 %s–%s（%d 小时），更新后需重新下载资源"
  % (MAINT[0], MAINT[1], MAINT[2]), 16, P["t2"], valign="TOP")
L(M, Y + 80, 620, 24, "包体：Android %.2f GB / iOS %.2f GB / 补丁 %.2f GB"
  % (PKG["Android"], PKG["iOS"], PKG["补丁包"]), 16, P["t2"], valign="TOP")
L(M, Y + 108, 620, 24, "阶段 %s 天 · 通行证 %d 级 · 概率公示已完成备案（演示）"
  % (" / ".join(str(v) for v in PHASE_LEN), PASS["levels"]), 16, P["t2"],
  valign="TOP")
bx = W - M - 250
L(bx, Y + 26, 250, 22, "虚构演示数据", 16, P["amber"], "BOLD", align="END",
  valign="TOP")
L(bx, Y + 52, 250, 44, "游戏名、干员、武器、数值与概率均为\n脚本构造，非任何真实产品内容",
  14, P["t2"], align="END", valign="TOP", maxlines=2, height=1.4)
Y += FH

d.H = Y
H = int(math.ceil(Y))
doc = Doc(W, H, bg="#050D18", palette=PAL)
doc.parts = d.parts
dsl = doc.dsl()
(OUT / "case06.snapshot").write_text(dsl, encoding="utf-8")
import json;print("PROBLEMS", json.dumps(tf.problems, ensure_ascii=False))
print("canvas %dx%d  bytes %d  textfit %d %s" % (W, H, len(dsl), tf.n, tf.problems[:4]))
print("days %d phases %s sum %d" % (DAYS, PHASE_LEN, sum(PHASE_LEN)))
print("buff %d nerf %d  pass xp %d  tiers %.1f/%.1f/%.1f days"
      % (BUFF, NERF, PASS["total_xp"], T_FREE, T_PASS, T_SEA))
print("E[pulls] %.2f cost %.0f  P60 %.3f  r %.3f" % (EXP_PULLS, EXP_COST, P60, TEN_E))
for hd in HEROES:
    print(hd["name"], "hp%%=%.1f atk%%=%.1f def%%=%.1f" % (
        hd["hp"] / STAT_MAX["hp"] * 100, hd["atk"] / STAT_MAX["atk"] * 100,
        hd["def"] / STAT_MAX["def"] * 100))
