"""B01 case-05 · 台风路径与风暴潮预报会商图（1600×1200）。

受众：沿海防汛防台值班员（省/市气象台会商室大屏，站 3 米外读）；使用时刻：
会商刚结束，值班员要在 20 秒内回答「几点登陆、我的辖区几点起 10 级风、
撤离必须在几点前收队、哪几个站风暴潮超警戒」。
全部数字由一份路径表反算：登陆时刻/坐标、不确定锥半径、7/10/12 级风圈、
各城市起风时刻、沿岸站增水、撤离截止、受影响人口与回港船只，
改路径表任一数值整屏同步。台风编号/命名、增水系数、人口与船数为虚构演示数据，
海岸线与城市位置为示意简化（等距圆柱投影，标准纬线 22°N）。
"""
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

OUT = root / "tmp" / rid / "B01" / "case-05"
OUT.mkdir(parents=True, exist_ok=True)

# ================= 路径模型 =================
BASE = (10, 9, 8)          # 会商时刻 2026-10-09 08:00（月, 日, 时）
# (相对时刻 h, 经度, 纬度, 中心气压 hPa, 底层中心风速 m/s)
TRK = [(-24, 134.2, 15.0, 992, 25), (-18, 133.0, 15.8, 978, 30),
       (-12, 131.8, 16.7, 952, 38), (-6, 130.4, 17.7, 930, 46),
       (0, 128.9, 18.8, 918, 52), (6, 127.7, 19.8, 916, 52),
       (12, 126.4, 20.8, 922, 49), (18, 125.0, 21.8, 930, 45),
       (24, 123.4, 22.6, 940, 42), (30, 122.5, 23.6, 948, 39),
       (36, 121.5, 24.6, 955, 37), (42, 120.4, 25.5, 958, 36),
       (48, 119.3, 26.4, 964, 34), (54, 118.2, 27.4, 980, 27),
       (60, 117.3, 28.4, 992, 22), (66, 116.6, 29.2, 998, 18),
       (72, 116.0, 30.0, 1003, 15)]

COAST = [(122.0, 31.7), (121.9, 31.0), (121.5, 30.6), (121.3, 30.3),
         (121.9, 29.9), (121.7, 29.2), (121.2, 28.6), (120.9, 28.0),
         (120.4, 27.6), (120.0, 27.1), (119.7, 26.6), (119.4, 26.1),
         (119.0, 25.6), (118.6, 25.2), (118.1, 24.5), (117.5, 24.0),
         (117.0, 23.6), (116.4, 23.2), (115.8, 22.9), (115.0, 22.6),
         (114.3, 22.4), (113.6, 22.2), (113.0, 21.9), (112.4, 21.5)]
TAIWAN = [(122.0, 25.2), (121.9, 24.6), (121.6, 24.1), (121.0, 22.9),
          (120.5, 22.4), (120.2, 22.9), (120.0, 23.5), (120.2, 24.2),
          (120.7, 24.7), (121.5, 25.2), (122.0, 25.2)]
LUZON = [(120.3, 17.8), (120.7, 17.2), (121.4, 16.7), (121.7, 15.7),
         (121.3, 14.6), (120.5, 14.6), (120.0, 15.5), (119.9, 16.5),
         (120.3, 17.8)]


def lerp(a, b, f):
    return a + (b - a) * f


def at_h(h):
    """路径表按 1 小时线性插值 -> (lon, lat, p, v)"""
    hs = [t[0] for t in TRK]
    h = max(hs[0], min(hs[-1], h))
    for i in range(len(TRK) - 1):
        if hs[i] <= h <= hs[i + 1]:
            f = (h - hs[i]) / float(hs[i + 1] - hs[i])
            a, b = TRK[i], TRK[i + 1]
            return tuple(lerp(a[k], b[k], f) for k in (1, 2, 3, 4))
    return TRK[-1][1:]


def coast_lon_at(lat):
    for (lo1, la1), (lo2, la2) in zip(COAST, COAST[1:]):
        if (la1 - lat) * (la2 - lat) <= 0 and la1 != la2:
            return lerp(lo1, lo2, (lat - la1) / float(la2 - la1))
    return None


def unc_km(h):                      # 预报不确定性半径（经验增长）
    return 45.0 + 6.2 * max(0.0, h) + (18.0 if h < 0 else 0.0)


def radii_km(v):                    # 7/10/12 级风圈平均半径（低于该级则无此圈）
    s = max(0.42, (v / 52.0)) ** 0.5
    r = {7: max(120.0, 380 * s), 10: max(62.0, 180 * s), 12: max(30.0, 85 * s)}
    for lv in (7, 10, 12):
        if v < THRESH[lv]:
            r[lv] = 0.0
    r[12] = min(r[12], r[10] * 0.6, r[7] * 0.35)
    r[10] = min(r[10], r[7] * 0.55)
    return r


EYE = 22.0


def wind_at(dd, r, q, vctr):
    """与风圈半径严格一致的风速廓线：圈内必达该级下限，圈外单调衰减。"""
    if r[7] <= 0:
        return 0.0
    a = ASYM[q]
    pts = [(EYE, max(vctr, THRESH[12] if r[12] > 0 else THRESH[7]))]
    for lv in (12, 10, 7):
        if r[lv] > 0:
            pts.append((r[lv] * a, THRESH[lv]))
    pts.append((r[7] * a * 2.2, 0.0))
    if dd <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if dd <= x1:
            return y0 + (y1 - y0) * (dd - x0) / max(x1 - x0, 1.0)
    return 0.0


ASYM = {"NE": 1.18, "SE": 0.85, "SW": 0.78, "NW": 0.92}
THRESH = {7: 13.9, 10: 24.5, 12: 32.7}   # 各级风圈对应的风速下限 m/s


def quad(dlon, dlat):
    return (("N" if dlat >= 0 else "S") + ("E" if dlon >= 0 else "W"))


def dist_km(lo1, la1, lo2, la2):
    return math.hypot((lo2 - lo1) * 103.0, (la2 - la1) * 111.0)


# 登陆：逐小时找第一个落到海岸线以西的时刻
LF = None
for hh in range(-24, 73):
    lo, la, p, v = at_h(hh)
    cl = coast_lon_at(la)
    if cl is not None and lo < cl:
        LF = dict(h=hh, lon=lo, lat=la, p=p, v=v)
        break
assert LF, "路径未登陆，模型不成立"


def clock(h):
    m0, d0, h0 = BASE
    t = h0 + h                       # 日期进位必须含起始时刻，否则跨日少算一天
    d = d0 + t // 24
    m = m0
    while d > 31:
        d -= 31
        m += 1
    while d < 1:
        m -= 1
        d += 31
    return "%02d-%02d %02d:00" % (m, d, t % 24)


def short(h):
    return clock(h)[6:]


def grade_name(v):
    return ("超强台风" if v >= 51 else "强台风" if v >= 41.5 else "台风"
            if v >= 32.7 else "强热带风暴" if v >= 24.5 else "热带风暴")


def grade_lvl(v):
    """蒲福风力等级（0–17 级，下限 m/s）"""
    B = [0.0, 0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5,
         32.7, 37.0, 41.5, 46.2, 51.0, 56.1]
    lv = 0
    for i, b in enumerate(B):
        if v >= b:
            lv = i
    return lv


CITIES = [("温州", 120.70, 28.00, 968, 2.1e4), ("台州", 121.42, 28.66, 665, 1.6e4),
          ("宁波", 121.55, 29.87, 969, 2.4e4), ("舟山", 122.21, 30.01, 116, 1.9e4),
          ("上海", 121.47, 31.23, 2487, 0.6e4), ("宁德", 119.52, 26.65, 315, 1.4e4),
          ("福州", 119.30, 26.08, 842, 2.0e4), ("台北", 121.51, 25.04, 260, 0.2e4),
          ("厦门", 118.09, 24.48, 528, 0.7e4)]

IMP = []
for name, lo, la, pop_w, fleet in CITIES:
    hit = {7: None, 10: None, 12: None}
    best_v, best_h = 0.0, None
    for hh in range(-24, 73):
        tlo, tla, p, v = at_h(hh)
        dd = dist_km(lo, la, tlo, tla)
        q = quad(lo - tlo, la - tla)
        r = radii_km(v)
        for lv in (7, 10, 12):
            if hit[lv] is None and r[lv] > 0 and dd <= r[lv] * ASYM[q]:
                hit[lv] = hh
        vg = wind_at(dd, r, q, v)
        if vg > best_v:
            best_v, best_h = vg, hh
    lvl = grade_lvl(best_v)
    IMP.append(dict(name=name, lon=lo, lat=la, pop=pop_w, fleet=fleet, hit=hit,
                    vmax=best_v, lvl=lvl, vh=best_h,
                    gust=best_v * 1.28,
                    dmin=min(dist_km(lo, la, *at_h(x)[:2]) for x in range(-24, 73))))

AFFECT = [c for c in IMP if c["name"] != "台北"]   # 辖区（大陆沿海）影响条
T10 = [c for c in IMP if c["hit"][10] is not None]
EVAC_DEADLINE = LF["h"] - 12
AFFECT_POP = round(sum(c["pop"] * (0.35 if c["hit"][10] is not None else
                                  0.12 if c["hit"][7] is not None else 0.02)
                       for c in IMP))
FLEET_BACK = int(sum(c["fleet"] for c in T10) / 1000)
Worst = max(IMP, key=lambda c: c["vmax"])

# 沿岸站风暴潮增水：离路径最近距离线性衰减 × 岸段暴露系数
STN = [("沙埕港", 120.2, 27.3, 1.22), ("洞头站", 121.15, 27.83, 1.08),
       ("路桥码头", 121.5, 28.6, 1.00), ("镇海站", 121.7, 29.95, 1.30),
       ("沈家门", 122.3, 29.95, 1.18), ("马尾站", 119.45, 26.0, 1.12),
       ("厦门港", 118.1, 24.45, 0.95), ("基隆港", 121.75, 25.13, 0.90)]
SURGE = []
for name, lo, la, expo in STN:
    dmin = min(dist_km(lo, la, *at_h(x)[:2]) for x in range(-24, 73))
    cm = max(0.0, 330.0 - 1.30 * dmin) * expo
    SURGE.append((name, round(cm), dmin))
SURGE.sort(key=lambda s: -s[1])
ALARM = 150
OVER = [s for s in SURGE if s[1] >= ALARM]

# ================= 画布 =================
W, H = 1600, 1200
d = Doc(W, H, bg="#050B15", palette={
    "card": "#0A1220", "card2": "#0E1A2C", "border": "#1B2A41",
    "grid": "#152238", "axis": "#475569", "row": "#0D1728",
    "t0": "#F1F5F9", "t1": "#9FB2C8", "t2": "#64748B",
    "cyan": "#22D3EE", "amber": "#FBBF24", "green": "#34D399",
    "red": "#EF4444", "violet": "#A78BFA", "pink": "#F472B6",
    "ocean": "#0B1B30", "slate": "#64748B"})
P = d.P
tf = TextFit()
d.rect(0, 0, W, H, "#050B15")
K.radial_disc(d, 900, -420, 1200, ["#0C2138", "#050B15"], radius="0.55")

# ---------- 顶部 ----------
d.pos(0, 0, W, 118, d.box(W, 118, color="#08101C"))
d.line(0, 118, W, 118, 2, P["border"])
d.label(36, 22, 760, 40, "台风 2618「溟舟」路径与风暴潮会商图", P["t0"], 34, "BOLD")
d.label(36, 70, 900, 24,
        "会商时刻 2026-10-09 08:00 · 沿海防汛值班室大屏 · 编号/命名与人口船数为虚构演示数据，"
        "海岸线为示意简化", P["t2"], 17)
d.pos(1180, 18, 384, 62, d.box(384, 62, align="CENTER_RIGHT",
                              inner=K.T("距登陆 %d 小时" % LF["h"], d.font,
                                        color=P["amber"], fontSize=40,
                                        fontStyle="BOLD")))
d.label(1180, 82, 384, 22, "登陆 %s · %s %d 级" % (clock(LF["h"]),
       grade_name(LF["v"]), grade_lvl(LF["v"])), P["t1"], 17, align="END")

# ---------- 告警条 ----------
alert = ("预计 %s 于福鼎—苍南沿海登陆（%s）；%d 站风暴潮超警戒（最高 %d cm），"
         "%d 市进入 10 级风圈，建议 %s 前完成危险区转移。"
         % (clock(LF["h"]), grade_name(LF["v"]), len(OVER), SURGE[0][1],
            len(T10), clock(EVAC_DEADLINE)))
tf.check("c5-alert", alert, 20, 1440, 30)
d.pos(36, 130, W - 72, 52, d.box(W - 72, 52, radius=8,
      grad='gradientType="LINEAR" gradientColors="#7F1D1D,#450A0A,#7F1D1D" '
           'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"'))
d.pos(36, 130, 6, 52, d.box(6, 52, radius=3, color=P["red"]))
d.label(58, 141, W - 120, 30, alert, "#FEE2E2", 20, "BOLD")

# ================= 左：地图 =================
GX, GY, GW, GH = 36, 196, 1088, 956
K.card(d, GX, GY, GW, GH, "路径与风圈预报",
       "等距圆柱投影（标准纬线 22°N）· 空心圈为预报 · 阴影为 45+6.2h km 不确定性锥")
# 海面渐变（底部让出 120px 给辖区影响条）
PLX, PLY = GX + 16, GY + 96
PLW, PLH = GW - 32, GH - 112 - 120
LAT0, LAT1 = 14.6, 32.2                     # 覆盖 15°N 台风源区到 31.5°N 上海
KPP = (LAT1 - LAT0) * 111.0 / PLH           # km / px（横纵等比）
LONC = 125.0
LON0 = LONC - PLW * KPP / 103.0 / 2
LON1 = LON0 + PLW * KPP / 103.0


def px(lo, la):
    return (PLX + (lo - LON0) / (LON1 - LON0) * PLW,
            PLY + (LAT1 - la) / (LAT1 - LAT0) * PLH)


PLACED = []


def free(b, pad=4):
    for a in PLACED:
        if b[0] < a[0] + a[2] + pad and a[0] < b[0] + b[2] + pad \
                and b[1] < a[1] + a[3] + pad and a[1] < b[1] + b[3] + pad:
            return False
    return True


def box_of(x, y, w, h):
    PLACED.append((x, y, w, h))
    return (x, y, w, h)


def smart(x, y, w, h, s, size, col, offs, style=None, tag="c5", chip=False):
    """Place a map chip/label at the first candidate offset that stays inside
    the plot and clear of everything already placed. offs are preference-ordered
    (dx, dy) anchors: dx>0 starts at the anchor, dx<0 ends there, dx=0 centres."""
    def geom(dx, dy):
        al = "START" if dx > 0 else "END" if dx < 0 else "CENTER"
        lx = x + dx if al == "START" else x + dx - w if al == "END" else x + dx - w / 2.0
        return lx, y + dy, al

    pick = None
    for dx, dy in offs:
        g = geom(dx, dy)
        if free((g[0], g[1], w, h)) and PLX - 1 <= g[0] and g[0] + w <= PLX + PLW + 1 \
                and PLY - 1 <= g[1] and g[1] + h <= PLY + PLH + 1:
            pick = g
            break
    if pick is None:
        pick = geom(*offs[0])
    lx, ly, al = pick
    tf.check(tag, s, size, w - (14 if chip else 0), h)
    if chip and (abs(lx - x) > 30 or abs(ly - y) > 30):
        ex = lx if al == "END" else lx + w if al == "START" else lx + w / 2.0
        d.line(x, y, ex, ly + h / 2.0, 1, "#475569")
    if chip:
        at = {"color": col, "fontSize": size}
        if style:
            at["fontStyle"] = style
        d.pos(lx, ly, w, h, d.box(w, h, radius=5, color="#050B15D0",
                                  align={"START": "CENTER_LEFT", "END": "CENTER_RIGHT",
                                         "CENTER": "CENTER"}[al],
                                  inner=K.T(s, d.font, **at)))
    else:
        d.label(lx, ly, w, h, s, col, size, style, align=al)
    return box_of(lx, ly, w, h)


d.pos(PLX, PLY, PLW, PLH,
      d.box(PLW, PLH, radius=10,
            grad='gradientType="LINEAR" gradientColors="#0B1B30,#0A2036,#081426" '
                 'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"'))
print("km/px %.4f  plot %dx%d  lon %.1f..%.1f  lat %.1f..%.1f"
      % (KPP, PLW, PLH, LON0, LON1, LAT0, LAT1))

# 底部经度轴带（避免与岛屿轮廓叠字）
d.rect(PLX, PLY + PLH - 28, PLW, 28, "#07101FE6")
d.line(PLX, PLY + PLH - 28, PLX + PLW, PLY + PLH - 28, 1, P["border"])

# 经纬网
for lo in range(int(math.ceil(LON0 / 4) * 4), int(LON1), 4):
    x, _ = px(lo, LAT1)
    d.line(x, PLY, x, PLY + PLH, 1, P["grid"])
    d.label(x - 26, PLY + PLH - 22, 52, 18, "%d°E" % lo, P["t2"], 14,
            align="CENTER")
for la in range(15, 32, 3):
    _, y = px(LON0, la)
    d.line(PLX, y, PLX + PLW, y, 1, P["grid"])
    d.label(PLX + 6, y - 18, 40, 16, "%d°N" % la, P["t2"], 14)


def coast_pts(off=0.0):
    return [px(lo - off, la) for lo, la in COAST]


# 陆侧柔化带（向西偏移的三条低透明粗线）
for off, th, al in ((0.15, 22, 0.10), (0.55, 40, 0.07), (1.25, 66, 0.05)):
    K.polyline(d, coast_pts(off), th, K.hexa("#1E293B", al))
K.polyline(d, coast_pts(), 2.5, "#3B5070")
for poly in (TAIWAN, LUZON):
    pts = [px(a, b) for a, b in poly]
    ccx = sum(p[0] for p in pts) / len(pts)
    ccy = sum(p[1] for p in pts) / len(pts)
    inner = [(a + (ccx - a) * 0.18, b + (ccy - b) * 0.18) for a, b in pts]
    K.polyline(d, inner + inner[:1], 30, K.hexa("#1E293B", 0.6))
    K.polyline(d, pts + pts[:1], 2.5, "#3B5070")
for s, lo, la in [("东  海", 124.6, 29.8), ("台 湾 海 峡", 118.6, 23.4),
                  ("菲 律 宾 海", 132.4, 17.4), ("浙 江", 119.4, 29.2),
                  ("福 建", 117.0, 26.4), ("广 东", 113.4, 23.0),
                  ("台 湾", 120.9, 23.6), ("吕宋（菲）", 117.9, 16.4)]:
    x, y = px(lo, la)
    tf.check("c5-geo", s, 17, 180, 22)
    d.label(x - 90, y, 180, 22, s, "#43536B", 17, align="CENTER")
    tw = sum(17 if ch != " " else 5 for ch in s)
    box_of(x - tw / 2.0, y, tw, 22)

# 图例占位先登记，路径与城市标注自动避开
LGX, LGY = PLX + PLW - 300, PLY + 12
box_of(LGX - 12, LGY - 10, 306, 168)
# 台风符号与登陆点标记同样先占位
clo, cla, cp, cv = at_h(0)
cx0, cy0 = px(clo, cla)
lx0, ly0 = px(LF["lon"], LF["lat"])
box_of(cx0 - 30, cy0 - 30, 60, 60)
box_of(cx0 + 26, cy0 - 46, 300, 26)
box_of(lx0 - 13, ly0 - 13, 26, 26)
box_of(lx0 - 192, ly0 - 52, 172, 24)

# 不确定性锥（沿路径逐小时圆盘）
for hh in range(0, 73, 2):
    lo, la, p, v = at_h(hh)
    x, y = px(lo, la)
    r = unc_km(hh) / KPP
    d.pos(x - r, y - r, r * 2, r * 2,
          d.box(r * 2, r * 2, color="#22D3EE0A", radius=r))
# 锥轮廓
left, right = [], []
for hh in range(0, 73, 3):
    lo, la, p, v = at_h(hh)
    plo, pla = at_h(max(-24, hh - 1))[:2]
    nlo, nla = at_h(min(72, hh + 1))[:2]
    dx, dy = nlo - plo, nla - pla
    ln = math.hypot(dx, dy) or 1.0
    r = unc_km(hh) / KPP
    x, y = px(lo, la)
    left.append((x - dy / ln * r, y + dx / ln * r))
    right.append((x + dy / ln * r, y - dx / ln * r))
K.polyline(d, left, 1.5, K.hexa(P["cyan"], 0.45))
K.polyline(d, right, 1.5, K.hexa(P["cyan"], 0.45))

# 路径折线（按强度着色）
RAMP = ["#38BDF8", "#22D3EE", "#FBBF24", "#FB923C", "#EF4444", "#C084FC"]


def vcol(v):
    return K.lerp_colors(["#60A5FA", "#FBBF24", "#F97316", "#EF4444", "#C084FC"],
                         (v - 12.0) / 42.0)


for a, b in zip(TRK, TRK[1:]):
    x1, y1 = px(a[1], a[2])
    x2, y2 = px(b[1], b[2])
    d.line(x1, y1, x2, y2, 5, vcol(max(a[4], b[4])))
for i, (hh, lo, la, p, v) in enumerate(TRK):
    x, y = px(lo, la)
    r = 7 if hh % 12 == 0 else 4.5
    if hh <= 0:
        d.pos(x - r, y - r, r * 2, r * 2, d.box(r * 2, r * 2, color=vcol(v),
                                                radius=r))
    else:
        d.pos(x - r, y - r, r * 2, r * 2,
              d.box(r * 2, r * 2, radius=r, border="2 SOLID %s" % vcol(v),
                    color="#0B1B30"))
    if hh % 12 == 0 and hh != 0:
        if math.hypot(x - lx0, y - ly0) < 52:
            continue      # 登陆点附近由「预计登陆」标贴代表，避免叠字
        s = "%s · %d" % (short(hh), p)
        edge = x < PLX + 150
        cands = ([(14, -30), (14, 10), (0, -56), (40, -14), (40, 18), (-14, -30)]
                 if edge else
                 [(-14, -30), (-14, 10), (0, -56), (-40, -14), (-40, 18), (14, -30)])
        smart(x, y, 124, 22, s, 15, P["t1"], cands, tag="c5-trk", chip=True)

# 当前台风符号 + 风圈
R = radii_km(cv)
for lv, col in ((7, P["cyan"]), (10, P["amber"]), (12, P["red"])):
    if R[lv] <= 0:
        continue
    for q, (a0, a1) in {"NE": (-90, 0), "SE": (0, 90), "SW": (90, 180),
                        "NW": (180, 270)}.items():
        K.arc(d, cx0, cy0, R[lv] * ASYM[q] / KPP, a0, a1, 2,
              K.hexa(col, 0.85 if lv == 12 else 0.6), seg_deg=10)
K.glow(d, cx0, cy0, 24, "#EF4444", rings=6, a0=0.05)
for i, rr in ((0, 12), (1, 18)):
    K.arc(d, cx0, cy0, rr, -70 + i * 180, 80 + i * 180, 5, "#F8FAFC", seg_deg=8)
d.dot(cx0, cy0, 6, "#F8FAFC")
d.pos(cx0 + 26, cy0 - 46, 300, 26, d.box(300, 26, align="CENTER_LEFT",
      color="#050B15CC", radius=6,
      inner=K.T("08:00 当前位置 %.0f hPa / %.0f m/s" % (cp, cv), d.font,
                color=P["t0"], fontSize=17, fontStyle="BOLD")))
tf.check("c5-now", "08:00 当前位置 %.0f hPa / %.0f m/s" % (cp, cv), 17, 288, 26)
# 登陆点
d.pos(lx0 - 11, ly0 - 11, 22, 22, d.box(22, 22, radius=11, color="#0B1B30",
                                        border="3 SOLID %s" % P["violet"]))
d.line(lx0, ly0 - 24, lx0, ly0 + 24, 2, P["violet"])
d.line(lx0 - 24, ly0, lx0 + 24, ly0, 2, P["violet"])
lfs = "预计登陆 %s" % clock(LF["h"])
tf.check("c5-lf", lfs, 16, 172, 24)
d.pos(lx0 - 192, ly0 - 52, 172, 24, d.box(172, 24, radius=6, color="#050B15D8",
      border="1 SOLID %s" % K.hexa(P["violet"], 0.6),
      inner=K.T(lfs, d.font, color=P["violet"], fontSize=16, fontStyle="BOLD")))
d.line(lx0 - 22, ly0 - 30, lx0 - 8, ly0 - 12, 1.5, K.hexa(P["violet"], 0.8))
box_of(lx0 - 192, ly0 - 52, 172, 24)
# 城市
for c in IMP:
    x, y = px(c["lon"], c["lat"])
    col = P["red"] if c["hit"][12] is not None else P["amber"] if c["hit"][10] \
        is not None else P["green"]
    west = c["name"] in ("台北", "宁德", "福州", "舟山", "宁波")
    d.dot(x, y, 7, col)
    wd = 14 + 15 * len(c["name"]) + 6
    near = [(14, -26), (14, 6), (-14, -26), (-14, 6), (0, -52), (0, 32),
            (46, -14), (46, 18), (-46, -14), (-46, 18), (0, -80), (0, 60)]
    far = [(-14, -26), (-14, 6), (14, -26), (14, 6), (-46, -14), (-46, 18),
           (46, -14), (46, 18), (0, -52), (0, 32), (0, -80), (0, 60)]
    smart(x, y, wd, 22, c["name"], 15, P["t0"], far if west else near,
          tag="c5-city", style="BOLD", chip=True)

# 图例
d.pos(LGX - 12, LGY - 10, 306, 168, d.box(306, 168, color="#050B15D8", radius=8,
                                          border="1 SOLID %s" % P["border"]))
for i, (s, col) in enumerate([("热带风暴 / 强热带风暴", "#60A5FA"),
                              ("台风", "#FBBF24"), ("强台风及以上", "#EF4444")]):
    d.pos(LGX + 4, LGY + 4 + i * 24, 12, 12, d.box(12, 12, radius=6, color=col))
    d.label(LGX + 22, LGY + i * 24, 268, 20, s, P["t1"], 15)
d.line(LGX + 4, LGY + 78, LGX + 16, LGY + 78, 3, K.hexa(P["cyan"], 0.5))
d.label(LGX + 22, LGY + 68, 268, 20, "不确定性锥 / 预报路径", P["t1"], 15)
for i, lv in enumerate((7, 10, 12)):
    col = {7: P["cyan"], 10: P["amber"], 12: P["red"]}[lv]
    d.line(LGX + 4, LGY + 100 + i * 20, LGX + 16, LGY + 100 + i * 20, 2, col)
    s = "%d 级风圈（东北侧）%dkm" % (lv, R[lv] * ASYM["NE"])
    tf.check("c5-lg", s, 15, 268, 18)
    d.label(LGX + 22, LGY + 90 + i * 20, 268, 18, s, P["t1"], 15)

# 底部城市影响条
SBY = GY + GH - 116
d.line(PLX, SBY, PLX + PLW, SBY, 1, P["border"])
d.label(PLX, SBY + 8, 300, 20, "辖区影响（由风圈覆盖逐小时反算）", P["t0"], 16,
        "BOLD")
cw = PLW / 8.0
for i, c in enumerate(AFFECT[:8]):
    x = PLX + i * cw
    d.line(x, SBY + 34, x, GY + GH - 16, 1, "#15223855")
    d.label(x + 6, SBY + 36, cw - 12, 22, c["name"], P["t0"], 17, "BOLD")
    s7 = "7 级 %s" % (short(c["hit"][7]) if c["hit"][7] is not None else "未达")
    s10 = "10 级 %s" % (short(c["hit"][10]) if c["hit"][10] is not None else "未达")
    sl = "最大 %d 级风" % c["lvl"]
    for j, (s, col) in enumerate([(s7, P["green"] if c["hit"][7] is not None
                                   else P["t2"]),
                                  (s10, P["amber"] if c["hit"][10] is not None
                                   else P["t2"]),
                                  (sl, P["t1"] if c["lvl"] < 10 else P["red"])]):
        tf.check("c5-strip", s, 15, cw - 12, 20)
        d.label(x + 6, SBY + 60 + j * 20, cw - 12, 20, s, col, 15)

# ================= 右：剖面 / 风暴潮 / 决策 =================
RX, RY, RW = 1140, 196, 424
K.card(d, RX, RY, RW, 292, "强度时间剖面", "柱＝风速 m/s，线＝中心气压 hPa")
CX0, CY0, CW0, CH0 = RX + 20, RY + 92, RW - 40, 168
VMIN, VMAX, PMIN, PMAX = 0, 56, 890, 1010
for i, (hh, lo, la, p, v) in enumerate(TRK):
    bw = CW0 / float(len(TRK))
    x = CX0 + i * bw
    bh = CH0 * v / VMAX
    d.rect(x + 1.5, CY0 + CH0 - bh, bw - 3, bh, K.hexa(vcol(v), 0.85))
    yy = CY0 + CH0 - CH0 * (p - PMIN) / float(PMAX - PMIN)
    if i:
        pp = TRK[i - 1][3]
        d.line(x - bw / 2 + 1.5, CY0 + CH0 - CH0 * (pp - PMIN) / float(PMAX - PMIN),
               x + bw / 2 - 1.5, yy, 2, P["violet"])
    d.dot(x, yy, 4, P["violet"])
d.line(CX0, CY0 + CH0, CX0 + CW0, CY0 + CH0, 1, P["axis"])
for hh, s in [(-24, "-24h"), (0, "现在"), (24, "+24h"), (48, "+48h"), (72, "+72h")]:
    i = [t[0] for t in TRK].index(hh)
    x = CX0 + (i + 0.5) * CW0 / float(len(TRK))
    d.label(x - 30, CY0 + CH0 + 6, 60, 18, s, P["t2"], 14, align="CENTER")
surge_sub = "警戒 150 cm · 超警戒 %d 站 · 最高 %d cm" % (len(OVER), SURGE[0][1])
tf.check("c5-surge-sub", surge_sub, 17, RW - 40, 24)
K.card(d, RX, RY + 308, RW, 312, "沿岸风暴潮增水", surge_sub)
SX0, SY0 = RX + 20, RY + 400
BARX, BARW = SX0 + 156, 170
d.rect(SX0, SY0 - 4, RW - 40, 18, "#0E1A2C")
d.label(SX0, SY0 - 4, 150, 18, "站名 · 距最近路径", P["t2"], 14, "BOLD")
d.label(BARX + BARW + 6, SY0 - 4, 52, 18, "增水", P["t2"], 14, "BOLD", align="END")
sy = SY0 + 22
for name, cm, dm in SURGE:
    col = P["red"] if cm >= 250 else P["amber"] if cm >= ALARM else P["green"]
    s = "%s · %.0f km" % (name, dm)
    tf.check("c5-stn", s, 15, 150, 20)
    d.label(SX0, sy, 150, 20, s, P["t0"], 15)
    d.rect(BARX, sy + 3, BARW, 12, "#12203A", radius=3)
    d.rect(BARX, sy + 3, BARW * min(1.0, cm / 350.0), 12, col, radius=3)
    d.label(BARX + BARW + 6, sy, 52, 20, "%d" % cm, col, 16, "BOLD", align="END")
    sy += 23
d.line(BARX + BARW * ALARM / 350.0, SY0 - 10, BARX + BARW * ALARM / 350.0,
       sy + 2, 1.5, K.hexa(P["red"], 0.6))

KY = RY + 636
K.card(d, RX, KY, RW, 1152 - KY, "撤离与管控窗口", "登陆时刻前 12 h 为转移截止")
d.label(RX + 20, KY + 76, 220, 22, "危险区转移截止", P["t1"], 17)
d.label(RX + 20, KY + 100, RW - 40, 40, clock(EVAC_DEADLINE), P["red"], 32, "BOLD")
d.label(RX + 20, KY + 146, RW - 40, 22,
        "＝登陆（%s）前 12 h" % clock(LF["h"]), P["t2"], 15)
d.line(RX + 20, KY + 176, RX + RW - 20, KY + 176, 1, P["border"])
stats = [("最强影响", "%s %d 级" % (Worst["name"], Worst["lvl"]), P["amber"]),
         ("进 10 级风圈", "%d 市" % len(T10), P["red"]),
         ("受影响人口（演示）", "%d 万人" % AFFECT_POP, P["cyan"]),
         ("渔船回港（演示）", "%d 千艘" % FLEET_BACK, P["green"])]
for i, (lab, val, col) in enumerate(stats):
    x = RX + 20 + (i % 2) * ((RW - 40 + 12) / 2)
    y = KY + 186 + (i // 2) * 62
    wd = (RW - 40 - 12) / 2
    tf.check("c5-stat", val, 20, wd - 26, 24)
    d.rect(x, y, wd, 56, "#0D1728", radius=8)
    d.rect(x, y, 5, 56, col, radius=2)
    d.label(x + 16, y + 6, wd - 26, 20, lab, P["t1"], 15)
    d.label(x + 16, y + 27, wd - 26, 24, val, P["t0"], 20, "BOLD")

d.label(36, 1166, W - 72, 22,
        "复现：路径表 %d 点（-24h…+72h）→ 逐小时插值 → 登陆判定/风圈覆盖/增水衰减全部在脚本内反算；"
        "投影 1 px ≈ %.2f km。本图为演示数据，不用于真实防灾决策。"
        % (len(TRK), KPP), P["t2"], 15)

dsl = d.dsl()
(OUT / "case05.snapshot").write_text(dsl, encoding="utf-8")
print("bytes", len(dsl), "textfit", tf.n, tf.problems)
print("landfall", LF, "deadline", clock(EVAC_DEADLINE))
print("surge", SURGE, "over", len(OVER))
print("pop", AFFECT_POP, "fleet", FLEET_BACK, "T10", [c["name"] for c in T10])
for c in IMP:
    print(c["name"], c["hit"], c["lvl"], round(c["gust"], 1), round(c["dmin"]))
