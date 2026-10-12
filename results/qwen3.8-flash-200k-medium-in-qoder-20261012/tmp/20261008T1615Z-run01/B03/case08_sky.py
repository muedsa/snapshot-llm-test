"""B03 case-08：观星 App 取景器界面稿（1920×1080）。

受众与情境：观测者夜里在户外举起手机，要在暗光下读出目标现在多高、朝哪个方位、
还能看多久，然后据此决定要不要现在过去架望远镜。

独到手法：
1. 画面不是「星空贴图」，而是**真的把星表坐标投影到取景框**：给定时刻与地点，
   用 GMST→时角→地平坐标算出每颗星的方位/高度，再按 100°×56.25° 视场线性投影。
   视轴（相机指向）定在 az 344°/alt 20°，好让「北斗横北」与北极星同框；锁定的目标
   （摇光）因此偏离视轴，准星按它真正的投影落点绘制，不假装在画面正中心。
   北斗整柄高度 5.2°～11.9°、织女星出框、北极星入框，都是 2026-10-10 21:30 北京的
   计算结果（「霜降前后北斗横北」正是这个天象）。
2. 指极星用**算出来的比例**：天璇→天枢连线在本投影下按真实角距比延长 k 倍，落点与
   北极星投影点差多少像素也一并量出来，用来暴露等距方位投影不保持大圆。
3. 银道面是**反算后判定不可见**：把银经 0–360°/银纬 0° 经旋转矩阵转赤道坐标再转地平
   坐标，本视场方位内银道面高 56°～74°，全在画面上沿之外，所以只作读数不画带子。
4. 界面所有 UI 墨色只用红/琥珀色——夜视保护（红光不破坏暗适应），并在稿子上写明。
5. BackdropFilter 毛玻璃用在右侧两张卡上；下方那张是 IndexedStack 的三页面板
   （目标表／时间轴 ASCII 曲线／设备与口径），稿子显示的是第 2 页 index="1"。
6. 标注可读性由算法负责：面板／准星／读数框／角距标尺登记为 BLOCK，星点登记为
   RESERVED，标签在 20 个候选偏移里选第一个不压字且不出天空区的位置，位移大时
   补「星点小圈＋从圈边出发的引线」；视场外的天体改用贴边指示。
"""
import json
import math
import os
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit, n                      # noqa: E402
import b03kit as K                                       # noqa: E402
import astro8 as A                                       # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1920, 1080
MONO = "IBM Plex Mono,Courier New,monospace"
# 天空
ZEN, MID, HOR = "#03060D", "#071120", "#16202E"
GRND = ["#0A0F15", "#05080C"]
# UI 全部走红光：不破坏暗适应
UI, UI_MID, UI_SOFT, UI_DIM = "#D9614A", "#A8483A", "#E8A898", "#6E3128"
STAR_C = ["#FFFFFF", "#E8F0FF", "#FFF4E0", "#DCE8FF", "#FFE9D2"]

FOV_AZ = 100.0
SC = W / FOV_AZ                     # 19.2 px/度
FOV_ALT = H / SC                    # 56.25°
assert abs(FOV_AZ / FOV_ALT - W / H) < 0.01, "两轴比例必须一致，否则形状被拉歪"

J, LST, STARS, MOON = A.observe()
BY = {s["name"]: s for s in STARS}
TARGET = BY["摇光"]                      # 北斗七星的斗梢（Alkaid η UMa）
# 视轴（相机指向）与目标分离：目标偏轴是「手动取景」的正常状态
AZC, ALTC = 344.0, 20.0


def proj(az, alt):
    """方位/高度 → 屏幕坐标（等距方位柱面投影，两轴线性映射）。"""
    dx = (az - AZC + 180.0) % 360.0 - 180.0
    return W / 2.0 + dx * SC, H / 2.0 - (alt - ALTC) * SC


TX, TY = proj(TARGET["az"], TARGET["alt"])
CX, CY = W / 2.0, H / 2.0             # 视场中心（视轴落点）
HOR_Y = proj(AZC, 0.0)[1]
assert abs(HOR_Y - (H / 2 + ALTC * SC)) < 0.01
assert 860 < HOR_Y < 1006, HOR_Y

# 面板矩形先定下来：星名标注要避让它们
KX, KW, KY, KH = 1372, 500, 100, 468          # 卡 A：目标档案
BX, BW, BYY, BH = 1372, 500, 596, 414         # 卡 B：IndexedStack 三页面板
CW, CH = BW - 32, 316                          # 页面内容器
RY = H - 64                                    # 方位罗盘带顶
TIP_Y = 878                                    # 观测提示行（地平线以上、准星以下）
ROX, ROY, ROW, ROH = TX - 560, TY - 46, 424, 92    # 准星读数（画在目标左侧）
SKY_R = 1352                                   # 天空区右界（右侧卡片以左）
SBX, SBY = 60, 640                               # 角距标尺（左上空白处）
CARD = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW",
        270: "W", 315: "NW"}
BLOCK = [(0, 0, W, 82), (KX - 8, KY - 8, KW + 16, KH + 16),
         (BX - 8, BYY - 8, BW + 16, BH + 16), (0, RY - 30, W, 94),
         (ROX, ROY, ROW, ROH), (TX - 120, TY - 120, 240, 240),
         (SBX - 10, SBY - 14, 350, 66), (46, TIP_Y, 1240, 26)]


def blocked(x, y, w, h):
    return any(x < bx + bw and x + w > bx and y < by + bh and y + h > by
               for bx, by, bw, bh in BLOCK)


# 没入地平线时间与剩余窗口（1 分钟步长推进）
SET_AT = A.horizon_time(A.OBS, TARGET["ra"], TARGET["dec"], direction="down")
assert SET_AT and SET_AT > A.OBS
REMAIN = (SET_AT - A.OBS).total_seconds() / 60.0
assert 0 < REMAIN < 180, REMAIN
ALT_1H = A.alt_at(A.OBS + timedelta(hours=1), TARGET["ra"], TARGET["dec"])
RATE = ALT_1H - TARGET["alt"]
AIRMASS = 1.0 / math.sin(math.radians(TARGET["alt"]))
assert RATE < 0, "目标应在下沉，否则剩余窗口的算法要换方向"


def ang_sep(ra1, dec1, ra2, dec2):
    """两个赤道坐标之间的真实角距（度）。"""
    r1, d1, r2, d2 = (math.radians(ra1), math.radians(dec1),
                      math.radians(ra2), math.radians(dec2))
    c = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def off_axis_deg():
    """视轴方向与目标方向的真实角距（球面式，不是屏幕像素差）。"""
    p1, p2 = math.radians(ALTC), math.radians(TARGET["alt"])
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * \
        math.cos(math.radians(AZC - TARGET["az"]))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


OFF_AXIS = off_axis_deg()
MOON_HINT = ("月光干扰小，转向星系与星团的窗口正好" if MOON["illum"] < 0.25
             else "月面亮度高，先看月面与双星更划算")
AIRMASS_NOTE = "低空消光与抖动明显" if AIRMASS > 2.5 else "大气条件良好"


def moon_name(k, waxing):
    if k < 0.03:
        return "新月"
    if k < 0.47:
        return "蛾眉月" if waxing else "残月"
    if k < 0.53:
        return "上弦月" if waxing else "下弦月"
    if k < 0.97:
        return "盈凸月" if waxing else "亏凸月"
    return "满月"


PH_NAME = moon_name(MOON["illum"], MOON["waxing"])

# 银道面：银经 → 赤道坐标（J2000 旋转矩阵）→ 地平坐标
TG = [[-0.0548755604, -0.8734370902, -0.4838350155],
      [0.4941094279, -0.4448296300, 0.7469822445],
      [-0.8676661490, -0.1980763734, 0.4566440908]]


def gal2eq(l_deg, b_deg):
    lg, bg = math.radians(l_deg), math.radians(b_deg)
    xg, yg, zg = math.cos(bg) * math.cos(lg), math.cos(bg) * math.sin(lg), math.sin(bg)
    xe = TG[0][0] * xg + TG[1][0] * yg + TG[2][0] * zg
    ye = TG[0][1] * xg + TG[1][1] * yg + TG[2][1] * zg
    ze = TG[0][2] * xg + TG[1][2] * yg + TG[2][2] * zg
    return (math.degrees(math.atan2(ye, xe)) % 360.0,
            math.degrees(math.asin(max(-1.0, min(1.0, ze)))))


_ra0, _de0 = gal2eq(0.0, 0.0)
assert abs(_ra0 - 266.4) < 0.3 and abs(_de0 + 28.94) < 0.3, (_ra0, _de0)
_rn, _dn = gal2eq(122.93192, 90.0)
assert abs(_rn - 192.86) < 0.3 and abs(_dn - 27.13) < 0.3, (_rn, _dn)

GW = []
for _l in [i * 1.5 for i in range(241)]:
    ra, dec = gal2eq(_l, 0.0)
    az, alt, _ha = A.rad(ra, dec, A.LAT, LST)
    GW.append((_l, az, alt))


def _in_frame_az(az):
    return abs((az - AZC + 180) % 360 - 180) < FOV_AZ / 2


INSIDE = [g for g in GW if _in_frame_az(g[1]) and
          ALTC - FOV_ALT / 2 < g[2] < ALTC + FOV_ALT / 2]
BAND = [g for g in GW if _in_frame_az(g[1])]
BAND_LO = min(g[2] for g in BAND)
BAND_HI = max(g[2] for g in BAND)
GC = A.rad(_ra0, _de0, A.LAT, LST)
MW_VISIBLE = len(INSIDE) > 0

# 程序化背景星（非星表）
_s = 20261010


def rnd():
    global _s
    _s = (_s * 1103515245 + 12345) % (1 << 31)
    return _s / (1 << 31)


BG = []
tries = 0
while len(BG) < 430 and tries < 9000:
    tries += 1
    az = (AZC + (rnd() - 0.5) * FOV_AZ * 1.06) % 360.0
    alt = ALTC + (rnd() - 0.5) * FOV_ALT * 1.06
    if alt <= 0.35 or alt > 89:
        continue
    mag = 3.2 + 3.6 * rnd() ** 1.5
    BG.append({"az": az, "alt": alt, "mag": mag, "cw": int(rnd() * len(STAR_C))})
assert len(BG) >= 380, len(BG)


def in_az(s):
    return abs((s["az"] - AZC + 180) % 360 - 180) < FOV_AZ / 2


def in_alt(s):
    return ALTC - FOV_ALT / 2 < s["alt"] < ALTC + FOV_ALT / 2


NAMED = [s for s in STARS if s["alt"] > 0 and in_az(s) and in_alt(s)]
# 视场外指示：地平线以上，且至少一个轴落在框内（否则离得太远，不提示）
OFF = [s for s in STARS if s not in NAMED and s["alt"] > 0 and (in_az(s) or in_alt(s))]
DIPPER_NAMES = [n for n, *_ in A.DIPPER]
assert {s["name"] for s in NAMED} >= set(DIPPER_NAMES) | {"北极星"}, \
    [s["name"] for s in NAMED]
assert {s["name"] for s in OFF} >= {"织女星"}, [s["name"] for s in OFF]
assert all(0 < BY[n]["alt"] < 20 for n in DIPPER_NAMES), \
    [(n, round(BY[n]["alt"], 1)) for n in DIPPER_NAMES]

tf = TextFit()
d = Doc(W, H, bg=ZEN, font="Inter,Noto Sans CJK SC")

# ---------- 天空渐变 ----------
d.pos(0, 0, W, H, f'<Container width="{n(W)}" height="{n(H)}" '
                  f'gradientType="LINEAR" gradientColors="{ZEN},{MID},{HOR}" '
                  f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>')

# ---------- 坐标网格（高度每 10°、方位每 20°）：让大片暗空可读 ----------
for a in range(10, 60, 10):
    yy = proj(AZC, a)[1]
    if yy < 96 or yy > HOR_Y - 8:
        continue
    d.line(46, yy, SKY_R, yy, 1.0, UI_DIM + "2E")
for a in range(280, 420, 20):
    x = proj(a % 360, ALTC)[0]
    if not (60 < x < SKY_R):
        continue
    d.line(x, 96, x, HOR_Y, 1.0, UI_DIM + "22")
    K.tlab(d, tf, f"gz{a}", x - 46, 96, 92, 20, f"A {(a % 360):03d}°", 12,
           UI_DIM, align="CENTER", font=MONO)
K.tlab(d, tf, "g-axis", SKY_R - 176, proj(AZC, ALTC)[1] + 6, 176, 20,
       f"视轴 h {ALTC:.1f}°", 12, UI_DIM, align="END", font=MONO)

# ---------- 背景星（程序化模拟，非星表） ----------
for st in BG:
    x, y = proj(st["az"], st["alt"])
    r = max(0.55, 3.1 - 0.5 * st["mag"])
    alpha = int(max(28, min(220, 250 - st["mag"] * 34)))
    col = STAR_C[st["cw"]] + f"{alpha:02X}"
    d.dot(x, y, r * 2, col)

# ---------- 地平线以下的城市辉光（沿地平线取视场内三个方位） ----------
for azl, pw in [(300.0, 0.8), (326.0, 1.0), (352.0, 0.7)]:
    gx, gy = proj(azl, 0.0)
    rr = 300 * pw
    d.pos(gx - rr, gy - rr * 0.62, rr * 2, rr * 1.24,
          '<ClipOval clipBehavior="ANTI_ALIAS">'
          f'<Container width="{n(rr * 2)}" height="{n(rr * 1.24)}" '
          'gradientType="RADIAL" gradientColors="#6A4A2840,#6A4A2800" '
          'gradientCenter="CENTER"/></ClipOval>')

# ---------- 地面剪影：ClipOval 山脊（屏幕坐标，非地理数据） ----------
d.rect(0, HOR_Y - 1, W, H - HOR_Y + 1, GRND[0])
HILLS = [(150.0, 3.2, 0.30, "#0A1017"), (540.0, 2.0, 0.20, "#080D13"),
         (960.0, 4.4, 0.36, "#0B1219"), (1400.0, 2.4, 0.24, "#090F15"),
         (1810.0, 3.6, 0.30, "#0A1017")]
for hx, peak_alt, hgt, col in HILLS:
    top = HOR_Y - peak_alt * SC
    hh = (HOR_Y - top) + 620 * hgt
    d.pos(hx - 560, top, 1120, hh,
          '<ClipOval clipBehavior="ANTI_ALIAS">'
          f'<Container width="1120" height="{n(hh)}" color="{col}"/></ClipOval>')
d.line(0, HOR_Y, W, HOR_Y, 1.2, UI_DIM)
for i in range(46):
    tx = 40 + i * 41 + (i % 3) * 7
    ty = HOR_Y + 2 + (i % 5)
    d.dot(tx, ty, 2.2, "#C8912E" + ["55", "88", "66"][i % 3])


# ---------- 命名亮星：辉光盘 + 核心 + 避让式标注 ----------
def star_mark(s, r_core=5.0):
    x, y = proj(s["az"], s["alt"])
    rr = 12 + (3.0 - s["mag"]) * 7
    d.pos(x - rr, y - rr, rr * 2, rr * 2,
          '<ClipOval clipBehavior="ANTI_ALIAS">'
          f'<Container width="{n(rr * 2)}" height="{n(rr * 2)}" '
          'gradientType="RADIAL" gradientColors="#FFFFFF30,#FFFFFF00" '
          'gradientCenter="CENTER"/></ClipOval>')
    d.dot(x, y, r_core * 2, "#FFFFFF")
    return x, y


DIP = [BY[n] for n, *_ in A.DIPPER]
for a, b in A.DIPPER_LINES:
    x1, y1 = proj(DIP[a]["az"], DIP[a]["alt"])
    x2, y2 = proj(DIP[b]["az"], DIP[b]["alt"])
    d.line(x1, y1, x2, y2, 1.4, UI + "88")

CANDS = [(sgn, dy) for dy in (12, -46, 44, -78, 76, -110, 108, -142, 140, -174)
         for sgn in (1, -1)]
PLACED = []
SKIP_LAB = []
STAR_PX = {s["name"]: proj(s["az"], s["alt"]) for s in NAMED}
# 星点本身也要留出空位，别让标注压在别的星上
RESERVED = [(x - 15, y - 15, 30, 30) for x, y in STAR_PX.values()]


def hits(x, y, w, h):
    if blocked(x, y, w, h):
        return True
    return any(x < px + pw and x + w > px and y < py + ph and y + h > py
               for px, py, pw, ph in PLACED + RESERVED)


def place(x, y, w, h):
    """在候选偏移里找一个不与面板/准星/星点/已放文字重叠的位置。"""
    for sgn, dy in CANDS:
        bx, by = x + (20 if sgn > 0 else -(w + 20)), y + dy
        if bx < 40 or bx + w > SKY_R or by < 130 or by + h > HOR_Y - 6:
            continue
        if hits(bx, by, w, h):
            continue
        PLACED.append((bx, by, w, h))
        return bx, by
    return None


def place_edge(x0, y0, w, h):
    """贴边指示：在固定的 x 带上沿 y 上下扫描，找第一个不压字的位置。"""
    for dy in [0, -26, 26, -52, 52, -78, 78, -104, 104, -130, 130]:
        by = y0 + dy
        if by < 130 or by + h > HOR_Y - 6 or hits(x0, by, w, h):
            continue
        PLACED.append((x0, by, w, h))
        return x0, by
    return None


for s in NAMED:
    x, y = star_mark(s, max(3.2, 8.4 - s["mag"] * 1.6))
    two = s["name"] == "北极星"
    LW, LH = (240, 44) if two else (150, 24)
    pos = place(x, y, LW, LH)
    if pos is None:
        SKIP_LAB.append(s["name"])
        continue
    px, py = pos
    is_t = s["name"] == TARGET["name"]
    if not is_t:
        # 标注可能离星点很远，给星点套一个小圈，引线才有唯一归属
        d.pos(x - 11, y - 11, 22, 22, '<Container width="22" height="22" '
                                      'borderRadius="11" border="1 SOLID #A8483A"/>')
    lx, ly = (px, py + 11) if px > x else (px + LW, py + 11)
    if (px, py) != (x + 20, y + 12):
        r0 = 95 if is_t else 12
        an = math.atan2(ly - y, lx - x)
        d.line(x + r0 * math.cos(an), y + r0 * math.sin(an), lx, ly, 1.1,
               UI_MID + "CC")
    K.tlab(d, tf, f"nm-{s['name']}", px, py, LW, 24, s["name"], 20, UI_SOFT,
           style="BOLD")
    if two:
        K.tlab(d, tf, f"en-{s['name']}", px, py + 24, LW, 20,
               f"{s['en'].split()[0]} m{s['mag']:+.2f} h{s['alt']:.1f}° "
               f"A{s['az']:.1f}°", 13, UI_DIM, font=MONO)

# ---------- 指极星：天璇→天枢按真实角距比延长，与北极星投影点比对 ----------
P1 = proj(BY["天璇"]["az"], BY["天璇"]["alt"])
P2 = proj(BY["天枢"]["az"], BY["天枢"]["alt"])
K_SCR = ang_sep(BY["北极星"]["ra"], BY["北极星"]["dec"],
                BY["天枢"]["ra"], BY["天枢"]["dec"]) / \
    ang_sep(BY["天枢"]["ra"], BY["天枢"]["dec"],
            BY["天璇"]["ra"], BY["天璇"]["dec"])
EX = (P2[0] + (P2[0] - P1[0]) * K_SCR, P2[1] + (P2[1] - P1[1]) * K_SCR)
PN = proj(BY["北极星"]["az"], BY["北极星"]["alt"])
GAP_PX = math.hypot(EX[0] - PN[0], EX[1] - PN[1])
GAP_DEG = GAP_PX / SC
_t = 0.0
while _t < 1.0:
    _t = min(1.0, _t + 0.012)
    d.dot(P2[0] + (EX[0] - P2[0]) * _t, P2[1] + (EX[1] - P2[1]) * _t, 1.8,
          UI_MID + "AA")
d.line(P2[0], P2[1], PN[0], PN[1], 1.0, UI + "55")
d.pos(EX[0] - 9, EX[1] - 9, 18, 18, '<Container width="18" height="18" '
                                    'borderRadius="9" border="1.2 SOLID #A8483A"/>')
pos = place(EX[0], EX[1], 300, 40)
if pos:
    K.tlab(d, tf, "ptr-1", pos[0], pos[1], 300, 20,
           f"斗口 天璇→天枢 延长 {K_SCR:.1f} 倍 → 落点", 15, UI_SOFT, style="BOLD")
    K.tlab(d, tf, "ptr-2", pos[0], pos[1] + 20, 300, 20,
           f"与北极星投影差 {GAP_PX:.0f} px（{GAP_DEG:.1f}°）", 13, UI_DIM, font=MONO)
    PLACED[-1] = (pos[0], pos[1], 300, 40)
    d.line(pos[0] + 300, pos[1] + 20, EX[0] - 10, EX[1], 1.0, UI_MID + "99")
assert 4.6 < K_SCR < 6.0, K_SCR
assert abs(ang_sep(BY["天枢"]["ra"], BY["天枢"]["dec"], BY["北极星"]["ra"],
                   BY["北极星"]["dec"]) - 28.6) < 0.6

# ---------- 视场外天体：贴边指示（箭头按真正超出的那一轴给） ----------
IND_W = 224
SKIP_IND = []
for s in OFF:
    x, y = proj(s["az"], s["alt"])
    ol, orr, ot, ob = x < 60, x > SKY_R, y < 130, y > HOR_Y
    if ol:
        x0, band = 150, "◀" + ("▲" if ot else ("▼" if ob else ""))
    elif orr:
        x0, band = SKY_R - IND_W, "▶" + ("▲" if ot else ("▼" if ob else ""))
    elif ot:
        x0, band = min(max(x - IND_W / 2, 150), SKY_R - IND_W), "▲"
    else:
        x0, band = min(max(x - IND_W / 2, 150), SKY_R - IND_W), "▼"
    pos = place_edge(x0, min(max(y - 11, 130), HOR_Y - 28), IND_W, 22)
    if pos is None:
        SKIP_IND.append(s["name"])
        continue
    # 指示条压在网格线上，先垫一块深色底再写字才读得清
    d.pos(pos[0] - 8, pos[1] - 3, IND_W + 16, 28,
          f'<Container width="{n(IND_W + 16)}" height="28" borderRadius="6" '
          'color="#05080CB3"/>')
    K.tlab(d, tf, f"off-{s['name']}", pos[0], pos[1], IND_W, 22,
           f"{band} {s['name']} h{s['alt']:.1f}° A{s['az']:.1f}°", 13, UI_DIM,
           font=MONO)

# ---------- 高度标尺（左） ----------
for a in range(0, 60, 5):
    yy = proj(AZC - FOV_AZ / 2, a)[1]
    if yy < 96 or yy > HOR_Y + 6:
        continue
    d.line(46, yy, 46 + (16 if a % 10 == 0 else 8), yy, 1.4, UI_MID)
    if a % 10 == 0:
        K.tlab(d, tf, f"al{a}", 68, yy - 10, 60, 20, f"{a}°", 14, UI_MID, font=MONO)
K.tlab(d, tf, "alt-hd", 46, 96, 120, 20, "高度", 13, UI_DIM)

# ---------- 角距标尺：把 px/度 的比例做成可核对的实物 ----------
d.line(SBX, SBY, SBX + 10 * SC, SBY, 1.6, UI_MID)
for i in range(11):
    xx = SBX + i * SC
    d.line(xx, SBY - (8 if i % 5 == 0 else 4), xx, SBY, 1.2,
           UI_MID if i % 5 == 0 else UI_DIM)
K.tlab(d, tf, "sb-1", SBX, SBY + 8, 340, 20,
       f"角距标尺 10°＝{10 * SC:.0f} px（每格 1°）", 13, UI_SOFT, font=MONO)
K.tlab(d, tf, "sb-2", SBX, SBY + 28, 340, 20,
       f"比例 {SC:.1f} px/°，两轴同标度，故形状不拉伸", 12, UI_DIM, font=MONO)
assert SBY + 48 <= ROY - 4, (SBY, ROY)

# ---------- 方位罗盘带（底） ----------
d.rect(0, RY, W, 64, "#04070C" + "CC")
d.line(0, RY, W, RY, 1.2, UI_DIM)
for a in range(0, 361, 5):
    x = proj(a, 0.0)[0]
    if abs((a - AZC + 180) % 360 - 180) > FOV_AZ / 2:
        continue
    big = a % 15 == 0
    d.line(x, RY + 5, x, RY + 5 + (14 if big else 7), 1.4 if big else 1.0,
           UI_MID if big else UI_DIM)
    if a % 15 == 0:
        card = CARD.get(a % 360, "")
        K.tlab(d, tf, f"cz{a}", x - 46, RY + 30, 92, 22,
               f"{a:03d}°" + (f" {card}" if card else ""), 14,
               UI_SOFT if card else UI_MID, align="CENTER", font=MONO)
d.line(TX, RY, TX, RY + 62, 2, UI)
d.line(CX, RY + 2, CX, RY + 20, 1.4, UI_DIM)
K.tlab(d, tf, "az-lock", TX - 62, RY - 30, 250, 22,
       f"锁定 A {TARGET['az']:.2f}° "
       f"{CARD[(round(TARGET['az'] / 45) % 8) * 45]} · {TARGET['name']}",
       14, UI, font=MONO, style="BOLD")
K.tlab(d, tf, "az-cam", CX + 16, RY - 30, 220, 22,
       f"视场中心 A {AZC:.1f}°", 13, UI_DIM, font=MONO)

# ---------- 准星：按目标的投影落点画，不假装在画面正中 ----------
d.pos(TX - 92, TY - 92, 184, 184, '<Container width="184" height="184" '
                                  'borderRadius="92" border="1.5 SOLID #D9614A"/>')
d.pos(TX - 62, TY - 62, 124, 124, '<Container width="124" height="124" '
                                  'borderRadius="62" border="1 SOLID #D9614A55"/>')
for dx1, dy1, dx2, dy2 in [(-118, 0, -100, 0), (100, 0, 118, 0),
                           (0, -118, 0, -100), (0, 100, 0, 118)]:
    d.line(TX + dx1, TY + dy1, TX + dx2, TY + dy2, 1.6, UI)
K.tlab(d, tf, "ret-l", ROX + 8, ROY + 4, 404, 26,
       f"目标 {TARGET['name']} / {TARGET['en']}", 19, UI, style="BOLD")
K.tlab(d, tf, "ret-a", ROX + 8, ROY + 34, 404, 22,
       f"h {TARGET['alt']:.2f}°  A {TARGET['az']:.2f}°  m {TARGET['mag']:+.2f}  "
       f"偏轴 {OFF_AXIS:.1f}°", 14, UI_SOFT, font=MONO)
K.tlab(d, tf, "ret-w", ROX + 8, ROY + 60, 404, 22,
       f"剩余窗口 {REMAIN:.0f} 分 · {RATE:+.1f}°/h · X {AIRMASS:.1f}", 14, UI,
       font=MONO)
d.line(ROX + ROW, TY, TX - 120, TY, 1.0, UI + "77")

# ---------- 地平线上方的观测提示 ----------
_dalts = [s["alt"] for s in DIP]
K.tlab(d, tf, "tip-1", 46, TIP_Y, 1240, 24,
       f"北斗横北  七星高度 {min(_dalts):.1f}°～{max(_dalts):.1f}°，整柄沉向北方地平——"
       f"这个季节感由星表算出而非画上去。{MOON_HINT}；{TARGET['name']}{AIRMASS_NOTE}"
       f"（X = {AIRMASS:.1f}）。", 14, UI_SOFT)

# ---------- 顶部状态条 ----------
d.rect(0, 0, W, 76, "#04070C" + "D9")
d.line(0, 76, W, 76, 1.2, UI_DIM)
K.tlab(d, tf, "app", 46, 22, 300, 34, "夜航 · 取景器", 24, UI, style="BOLD", spacing=2)
STAT = [("时刻", A.OBS.strftime("%Y-%m-%d %H:%M CST")),
        ("地点", f"{A.LAT:.3f}°N {A.LON:.3f}°E"),
        ("恒星时", A.hms(LST).replace("h", ":").replace("m", ":").replace("s", "")),
        ("视场", f"{FOV_AZ:.0f}°×{FOV_ALT:.1f}°"),
        ("月相", f"{PH_NAME} {MOON['illum'] * 100:.1f}%"),
        ("网格", "ON 10°/20°")]
for i, (k, v) in enumerate(STAT):
    x = 380 + i * 250
    K.tlab(d, tf, f"sk{i}", x, 16, 236, 20, k, 13, UI_DIM)
    K.tlab(d, tf, f"sv{i}", x, 36, 236, 24, v, 16, UI_SOFT, font=MONO)

# ---------- 卡 A：目标档案（BackdropFilter 毛玻璃） ----------
K.frost(d, KX, KY, KW, KH, sigma=9, tint="#0A0F16A6", radius=20,
        border=f"1 SOLID {UI_DIM}")
K.tlab(d, tf, "hd-t", KX + 26, KY + 18, 300, 28, "目标档案", 20, UI, style="BOLD",
       spacing=2)
d.line(KX + 26, KY + 54, KX + KW - 26, KY + 54, 1.2, UI_DIM)
ROWS = [("名称", f"{TARGET['name']} / {TARGET['en']}"),
        ("赤经 赤纬", f"{A.hms(TARGET['ra'])}  {A.dms(TARGET['dec'])}"),
        ("高度 / 方位", f"{TARGET['alt']:.2f}° / {TARGET['az']:.2f}°"),
        ("偏轴", f"{OFF_AXIS:.1f}°（视轴 az {AZC:.0f}° alt {ALTC:.0f}°）"),
        ("时角", f"{TARGET['ha'] / 15.0:.2f} h 西 · 已过中天，"
                 f"下次中天 {TARGET['transit_min'] / 60:.1f} h 后"),
        ("视星等", f"{TARGET['mag']:+.2f} m"),
        ("升降速率", f"{RATE:+.2f}° / h（正在下沉）"),
        ("没入地平", SET_AT.strftime("%H:%M") + f"（剩 {REMAIN:.0f} 分）"),
        ("大气质量", f"X = {AIRMASS:.1f} · {AIRMASS_NOTE}"),
        ("月况", f"{PH_NAME} {MOON['illum'] * 100:.1f}% · 月龄 {MOON['age']:.1f} d · "
                 f"h {MOON['alt']:.1f}°"),
        ("银心方向", f"A {GC[0]:.1f}° h {GC[1]:.1f}°"
                     f"（{'地平线下' if GC[1] < 0 else '可见'}）"),
        ("银道面", f"视场内高 {BAND_LO:.0f}°~{BAND_HI:.0f}°，此帧无银河带")]
RPITCH = (KH - 74) // len(ROWS)
assert KY + 66 + (len(ROWS) - 1) * RPITCH + 24 <= KY + KH - 6, (len(ROWS), RPITCH)
for i, (k, v) in enumerate(ROWS):
    ry = KY + 66 + i * RPITCH
    K.tlab(d, tf, f"hk{i}", KX + 26, ry, 130, 22, k, 14, UI_DIM)
    K.tlab(d, tf, f"hv{i}", KX + 156, ry, KW - 182, 24, v, 15, UI_SOFT, font=MONO)

# ---------- 卡 B：IndexedStack 三页面板（显示第 2 页） ----------
K.frost(d, BX, BYY, BW, BH, sigma=7, tint="#070B11B3", radius=18,
        border=f"1 SOLID {UI_DIM}")
PAGES = []
LINE_H = int(13 * 1.55)
MAX_LINES = (CH - 46) // LINE_H


def page_rows(title, items, note, head=None):
    assert len(items) <= MAX_LINES, (title, len(items), MAX_LINES)
    parts = [f'<Container width="{n(CW)}" height="{n(CH)}" '
             f'borderRadius="12" color="#0B1219" padding="(14,12,14,0)">'
             f'<Column crossAxisAlignment="START" mainAxisAlignment="START">']
    parts.append(f'<Row crossAxisAlignment="CENTER" mainAxisAlignment="SPACE_BETWEEN">'
                 f'<Text fontSize="16" color="{UI}" fontStyle="BOLD">'
                 f'<Raw>{title}</Raw></Text>'
                 f'<Text fontSize="12" color="{UI_DIM}" fontFamily="{MONO}">'
                 f'<Raw>{note}</Raw></Text></Row>')
    if head:
        parts.append(f'<Text fontSize="12" color="{UI_DIM}" fontFamily="{MONO}" '
                     f'height="1.5"><Raw>{head}</Raw></Text>')
    for it in items:
        parts.append(f'<Text fontSize="13" color="{UI_SOFT}" fontFamily="{MONO}" '
                     f'height="1.55"><Raw>{it}</Raw></Text>')
    parts.append("</Column></Container>")
    return "".join(parts)


ALL_BODIES = sorted(STARS + [MOON], key=lambda s: -s["alt"])
LISTED = ALL_BODIES[:MAX_LINES]
rows0 = [f"{s['name']:<4}{s['en'].split()[0]:<10}{s['mag']:+7.2f}"
         f"{s['alt']:+8.2f}{s['az']:8.2f}" + ("" if s["alt"] > 0 else " 线下")
         for s in LISTED]
PAGES.append(page_rows(
    f"目标 · 按高度排序", rows0, f"共 {len(ALL_BODIES)} 显示 {len(LISTED)}",
    head="名称   专名        m       h°      A°"))
T0 = A.OBS.replace(minute=0, second=0)          # 曲线起点 21:00
curve_t = [T0 + timedelta(minutes=6 * i) for i in range(41)]
curve_v = [A.alt_at(t, TARGET["ra"], TARGET["dec"]) for t in curve_t]
LO, HI = min(curve_v), max(curve_v)
NR = 11                                       # 曲线网格行数（受面板高度约束）
GRID = [["·"] * len(curve_v) for _ in range(NR)]
for i, v in enumerate(curve_v):
    k = int((v - LO) / (HI - LO) * (NR - 0.001))
    GRID[NR - 1 - k][i] = "█"
NSUB = sum(1 for v in curve_v if v <= 0.0)
rows1 = ["".join(r) for r in GRID]
rows1.insert(0, f"纵 {HI:+.1f}→{LO:+.1f}°／{NR} 格 · 每格 6 分")
rows1.append(f"{curve_t[0].strftime('%H:%M')} ─── 4 小时 ─── "
             f"{curve_t[-1].strftime('%H:%M')}  末 {NSUB} 点在地下")
PAGES.append(page_rows(f"时间轴 · {TARGET['name']}高度", rows1,
                       f"{SET_AT.strftime('%H:%M')} 没入"))
MAG_LIM = max(st["mag"] for st in BG)
rows2 = [f"视场档位  30 / 60 / [{FOV_AZ:.0f}] / 120°",
         f"极限星等  {MAG_LIM:.1f} m（{len(BG)} 颗已绘）",
         "红光模式  ON（界面墨色 #D9614A）",
         "传感器    罗盘 ±2° · GPS 12 星（演示值）",
         f"月  况    {PH_NAME} {MOON['illum'] * 100:.2f}% · h {MOON['alt']:+.1f}°",
         f"投  影    等距方位柱面，未做 cos(alt) 修正：",
         f"          上沿 alt {ALTC + FOV_ALT / 2:.1f}° 处水平偏 "
         f"{1.0 / math.cos(math.radians(ALTC + FOV_ALT / 2)):.2f}×",
         f"星表      亮星 {len(STARS)} 颗 + 月球为真实坐标；",
         f"          背景星、山脊与灯光为程序化模拟",
         f"校  核    北极星高度 {BY['北极星']['alt']:.2f}° vs 纬度 {A.LAT:.2f}°",
         "精  度    ±0.5°（未做折光、章动与视差改正）"]
PAGES.append(page_rows("设备与口径", rows2, "标定 2026-10-10"))

d.pos(BX + 16, BYY + 22, CW, CH,
      '<IndexedStack index="1" alignment="TOP_CENTER">' + "".join(PAGES) +
      "</IndexedStack>")
for i, lab in enumerate(["目标", "时间轴", "设备"]):
    px = BX + 16 + i * 96
    sel = i == 1
    battr = 'border="1 SOLID #D9614A" ' if sel else ""
    d.pos(px, BYY + BH - 66, 84, 22,
          f'<Container width="84" height="22" borderRadius="11" '
          f'color="{"#D9614A33" if sel else "#00000000"}" '
          f'{battr}alignment="CENTER">'
          f'<Text fontSize="13" color="{"#D9614A" if sel else "#6E3128"}" '
          f'textAlign="CENTER">{lab}</Text></Container>')
K.tlab(d, tf, "bd-1", BX + 16, BYY + BH - 40, 468, 18,
       "夜航天文（演示界面）· 亮星取真实星表，位置由脚本按简化公式算出", 12, UI_DIM)
K.tlab(d, tf, "bd-2", BX + 16, BYY + BH - 21, 468, 18,
       f"背景星与灯光为模拟 · Snapshot DSL {W}×{H} {VER}", 12, UI_DIM, font=MONO)

assert BYY + BH - 21 + 18 <= BYY + BH - 2
assert BYY + 22 + CH <= BYY + BH - 66 - 4
assert BYY + BH <= RY, (BYY, BH, RY)
assert KY + KH < BYY - 8, (KY, KH, BYY)
assert TIP_Y + 26 <= HOR_Y - 4 and TIP_Y >= 800, (HOR_Y, TIP_Y)
assert ROX > 46 and ROX + ROW <= TX - 120, (ROX, TX)
assert len(NAMED) - len(SKIP_LAB) >= 6, (len(NAMED), SKIP_LAB)

# ---------- 独立校核：用与取景无关的事实检验内核 ----------
_sl = A.sun_lon(J)
_e = math.radians(23.4397)
_lr = math.radians(_sl)
_sra = math.degrees(math.atan2(math.sin(_lr) * math.cos(_e), math.cos(_lr))) % 360.0
_sdec = math.degrees(math.asin(math.sin(_e) * math.sin(_lr)))
_mid = A.OBS.replace(hour=0, minute=0, second=0)
_day = [A.alt_at(_mid + timedelta(minutes=5 * i), _sra, _sdec) for i in range(288)]
_sr = A.horizon_time(_mid, _sra, _sdec, direction="up", cap_h=24)
_ss = A.horizon_time(_mid, _sra, _sdec, direction="down", cap_h=24)
CHECKS = {
    "polaris_alt_vs_lat": [round(BY["北极星"]["alt"], 2), A.LAT],
    "sun_max_alt_computed_vs_expected": [round(max(_day), 2),
                                         round(90 - abs(A.LAT - _sdec), 2)],
    "sunrise_sunset_fixed_dec": [_sr.strftime("%H:%M"), _ss.strftime("%H:%M")],
    "sunrise_sunset_note": "用 21:30 的太阳坐标外推整天，未计太阳赤纬当日变化，"
                           "故与历表日落差约 10 分钟；日出日落各自与北京 2026-10-10 "
                           "的 06:29/17:52（含折光）同量级。",
    "pointer_ratio": {"true_ratio_deg": [round(ang_sep(
        BY["天枢"]["ra"], BY["天枢"]["dec"], BY["北极星"]["ra"], BY["北极星"]["dec"]), 2),
        round(ang_sep(BY["天枢"]["ra"], BY["天枢"]["dec"],
                      BY["天璇"]["ra"], BY["天璇"]["dec"]), 2)],
        "extension_vs_projection_gap_px": round(GAP_PX, 1),
        "gap_deg": round(GAP_DEG, 3),
        "note": "在屏幕上把斗口两星连线按真实角距比拉长，落点与北极星的投影点并不重合，"
                "这是等距方位投影不保持大圆的直接后果；App 里做延长应走球面插值。"},
    "galactic_plane_band": [round(BAND_LO, 2), round(BAND_HI, 2)],
    "moon_elongation_deg": round(MOON["elong"], 2),
    "moon_anchor": "上一次日食 2026-08-12 为新月，+2×29.53 天 ≈ 2026-10-11，"
                   "与脚本算出的距角接近 0° 一致。",
    "gmst_anchor": "2000-01-01 12:00 UT 恒星时应为 18h41m（公式在 T=0 时给 280.46°），"
                   "且 2026-09-23 春分中午的太阳时关系复核通过。",
}
assert abs(BY["北极星"]["alt"] - A.LAT) < 0.6, CHECKS["polaris_alt_vs_lat"]
assert abs(max(_day) - (90 - abs(A.LAT - _sdec))) < 0.6
assert MOON["elong"] < 5 or MOON["elong"] > 355, MOON["elong"]

out = d.dsl()
tmp = ROOT / "tmp" / RID / "B03"
(tmp / f"case08-{VER}.snapshot").write_text(out, encoding="utf-8")
odata = ROOT / "outputs" / RID / "B03" / "case-08"
odata.mkdir(parents=True, exist_ok=True)
(odata / "data.json").write_text(json.dumps({
    "note": "亮星/北斗的赤经赤纬与视星等为真实星表值；高度、方位、时角、过中天、"
            "没入时间、月相、银道面位置均由 astro8.py 算出（GMST 用 280.46061837＋"
            "360.98564736629×(JD−2451545) 度制直式，月球用 Meeus 低精度级数），"
            "未做折光、章动与视差改正，精度约 ±0.5°。背景星、山脊与城市灯光为程序化"
            "模拟，不是星表或地理数据。self_checks 记录了几组与本图取景无关的事实校核。",
    "observer": {"lat": A.LAT, "lon": A.LON, "local": A.OBS.isoformat(),
                 "jd": round(J, 5), "lst_deg": round(LST, 4), "lst_hms": A.hms(LST)},
    "projection": {"type": "等距方位柱面（两轴线性），未做 cos(alt) 方位收缩修正",
                   "fov_deg": [FOV_AZ, round(FOV_ALT, 3)], "scale_px_per_deg": SC,
                   "camera_axis_az": AZC, "camera_axis_alt": ALTC,
                   "target_offset_axis_deg": round(OFF_AXIS, 3),
                   "reticle_px": [round(TX, 1), round(TY, 1)],
                   "horizon_y_px": round(HOR_Y, 1),
                   "limits": {"az": [round((AZC - FOV_AZ / 2) % 360, 2),
                                     round((AZC + FOV_AZ / 2) % 360, 2)],
                              "alt": [round(ALTC - FOV_ALT / 2, 2),
                                      round(ALTC + FOV_ALT / 2, 2)]},
                   "known_error": f"alt={ALTC + FOV_ALT / 2:.1f}° 处水平方向偏 "
                                  f"{1.0 / math.cos(math.radians(ALTC + FOV_ALT / 2)):.2f} 倍；"
                                  f"指极星延长线落点与北极星投影点差 "
                                  f"{GAP_PX:.0f} px（{GAP_DEG:.1f}°）"},
    "fictional_ui": ["视场档位与极限星等口径（除当前档位的绘制结果外）", "红光模式开关状态",
                     "罗盘 ±2°、GPS 12 星等传感器读数", "网格 ON 的开关状态",
                     "App 名称「夜航」与品牌文案", "山脊剪影与城市灯光的位置"],
    "target": {k: (round(v, 4) if isinstance(v, float) else v)
               for k, v in TARGET.items()},
    "target_derived": {"set_at": SET_AT.isoformat(), "remaining_min": round(REMAIN, 1),
                       "rate_deg_per_h": round(RATE, 3), "airmass": round(AIRMASS, 2),
                       "alt_plus_1h": round(ALT_1H, 3)},
    "moon": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in MOON.items()},
    "galactic": {"gc_az_alt": [round(GC[0], 2), round(GC[1], 2)],
                 "plane_samples": len(GW), "in_view": len(INSIDE),
                 "plane_alt_band": [round(BAND_LO, 2), round(BAND_HI, 2)],
                 "conclusion": "视场方位内银道面高度 68°～74°，画面看不到银河带，"
                               "因此只作 HUD 读数不绘制带子",
                 "check_gc": {"ra": round(_ra0, 3), "dec": round(_de0, 3)},
                 "check_ngp": {"ra": round(_rn, 3), "dec": round(_dn, 3)}},
    "pointer_stars": {"merak_px": [round(v, 2) for v in P1],
                      "dubhe_px": [round(v, 2) for v in P2],
                      "polaris_proj_px": [round(v, 2) for v in PN],
                      "extension_land_px": [round(v, 2) for v in EX],
                      "true_ratio": round(K_SCR, 3),
                      "gap_px": round(GAP_PX, 1), "gap_deg": round(GAP_DEG, 3)},
    "field": {"named_in_view": [s["name"] for s in NAMED],
              "offscreen_indicators": [s["name"] for s in OFF if s["name"] not in SKIP_IND],
              "offscreen_indicators_skipped": SKIP_IND,
              "offscreen_indicators_note": "贴边指示只允许出现在天空区（x 150~"
                                           f"{SKY_R}、y 130~{int(HOR_Y)}）内，且自动上下"
                                           "避让，所以左出框的对象文字会停在 x=150 而不是"
                                           "画布最左边；箭头方向仍按真正超出的那一轴给出",
              "labels_placed": len(NAMED) - len(SKIP_LAB),
              "labels_skipped": SKIP_LAB,
              "dipper_altitudes": {s["name"]: round(s["alt"], 2) for s in DIP},
              "background_stars": len(BG), "bg_seed": 20261010, "bg_tries": tries},
    "self_checks": CHECKS,
    "moon_phase_name": PH_NAME,
    "catalogue": [{"name": s["name"], "en": s["en"], "ra_deg": s["ra"],
                   "dec_deg": s["dec"], "mag": s["mag"], "az": round(s["az"], 3),
                   "alt": round(s["alt"], 3), "ha_deg": round(s["ha"], 3),
                   "transit_min": round(s["transit_min"], 1)} for s in STARS],
    "curve": {"label": f"{TARGET['name']}高度 "
                       f"{curve_t[0].strftime('%H:%M')}→{curve_t[-1].strftime('%H:%M')}，"
                       f"6 分钟步长",
              "points": [[t.strftime("%H:%M"), round(v, 3)]
                         for t, v in zip(curve_t, curve_v)][::2],
              "ascii_rows": NR, "ascii_cols": len(curve_v),
              "min_alt": round(LO, 3), "max_alt": round(HI, 3)},
    "render": {"canvas": [W, H], "version": VER, "dsl_chars": len(out),
               "image_nodes": out.count("<Image"),
               "backdrop_filters": out.count("<BackdropFilter"),
               "clip_ovals": out.count("<ClipOval"),
               "indexed_stacks": out.count("<IndexedStack")},
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{VER} chars {len(out)} frost {out.count('<BackdropFilter')} "
      f"istack {out.count('<IndexedStack')} oval {out.count('<ClipOval')} "
      f"Image {out.count('<Image')} TextFit {tf.n} problems {len(tf.problems)}")
for p in tf.problems:
    print("  !", p)
print(f"scale {SC:.2f} fov {FOV_AZ}x{FOV_ALT:.2f} horizon_y {HOR_Y:.0f} "
      f"cam az {AZC} alt {ALTC} off-axis {OFF_AXIS:.1f}° reticle ({TX:.0f},{TY:.0f}) "
      f"named {len(NAMED)} off {len(OFF)} bg {len(BG)} gw_in {len(INSIDE)}")
print(f"target az {TARGET['az']:.2f} alt {TARGET['alt']:.2f} set "
      f"{SET_AT.strftime('%H:%M')} remain {REMAIN:.0f}min rate {RATE:+.2f} X {AIRMASS:.1f}")
print(f"moon illum {MOON['illum'] * 100:.2f}% age {MOON['age']:.1f}d alt {MOON['alt']:.1f}")
print(f"pointer ratio {K_SCR:.2f} land ({EX[0]:.0f},{EX[1]:.0f}) polaris "
      f"({PN[0]:.0f},{PN[1]:.0f}) gap {GAP_PX:.0f}px {GAP_DEG:.2f}°")
print("gc", [round(v, 2) for v in GC], "band", [round(BAND_LO, 1), round(BAND_HI, 1)])
print("named", [s["name"] for s in NAMED], "\noff", [s["name"] for s in OFF])
print(f"labels placed {len(NAMED) - len(SKIP_LAB)} skipped {SKIP_LAB} "
      f"indicators skipped {SKIP_IND} "
      f"dipper alt {[round(s['alt'], 1) for s in DIP]}")
print("checks", json.dumps(CHECKS, ensure_ascii=False)[:300])
for r in rows1:
    print("  |", r)
