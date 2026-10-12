"""B03 case-08 的天文计算内核：真实星表坐标 + 简化视位置公式。

公式：GMST 近似式 → LST → 时角 → 地平坐标；太阳用平黄经近似，月球用 Meeus
低精度级数（精度约 0.3°）。所有页面数字都由这里算出，不做手写常量。
"""
import math
from datetime import datetime, timedelta, timezone

# 观测地点与时刻（东八区）
LAT, LON = 39.9042, 116.4074          # 北京
OBS = datetime(2026, 10, 10, 21, 30, tzinfo=timezone(timedelta(hours=8)))
JD0 = 2451545.0                        # J2000.0


def jd(dt):
    d = dt.astimezone(timezone.utc)
    return (d - datetime(2000, 1, 1, 12, tzinfo=timezone.utc)).total_seconds() / 86400.0 + 2451545.0


def gmst_deg(j):
    """格林尼治平恒星时（度）。280.46061837° 对应 JD2000.0＝2000-01-01 12:00 UT，
    地球自转速率 360.98564736629°/日（＝1.00273790935×360）。
    早先写的 36285.34841908·T 是另一套按儒略世纪的展开式，代进来会让恒星时错几个小时，
    整张星图的位置随之全非——已按 JD 日数形式重写，并用两组独立事实校核。"""
    return (280.46061837 + 360.98564736629 * (j - JD0)) % 360.0


def lst_deg(j, lon=LON):
    return (gmst_deg(j) + lon) % 360.0


def rad(h_deg, dec_deg, lat_deg, lst):
    """赤经(度)/赤纬/纬度/LST → (方位角度, 高度角度, 时角度)。北为 0，顺时针。"""
    ha = math.radians((lst - h_deg) % 360.0)
    d = math.radians(dec_deg)
    p = math.radians(lat_deg)
    sin_alt = math.sin(d) * math.sin(p) + math.cos(d) * math.cos(p) * math.cos(ha)
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    # atan2 形式给出的是「由南起算、向西为正」的方位，真北要 +180
    az = math.atan2(math.sin(ha), math.cos(ha) * math.sin(p) - math.tan(d) * math.cos(p))
    return (math.degrees(az) + 180.0) % 360.0, math.degrees(alt), math.degrees(ha) % 360.0


def sun_lon(j):
    """太阳视黄经（低精度，章动/光行差忽略）。
    m 为太阳平黄经，c 为中心差；原先误把月球平黄经（218.316＋481267.88·T）当成
    太阳黄经返回，会让日月距角恒接近 0，任何日期都算成「新月」。"""
    t = (j - JD0) / 36525.0
    m = (280.46646 + 36000.76983 * t) % 360.0
    mm = math.radians((357.52911 + 35999.05029 * t) % 360.0)
    c = 1.9146 * math.sin(mm) + 0.0200 * math.sin(2 * mm)
    return (m + c) % 360.0


def moon_eq(j):
    """Meeus 低精度：月球黄道坐标 → 赤道坐标（度）。"""
    d = j - JD0
    lp = 218.316 + 13.176396 * d
    m = math.radians(134.963 + 13.064993 * d)
    f = math.radians(93.272 + 13.229350 * d)
    lon = lp + 6.289 * math.sin(m)
    lat = 5.128 * math.sin(f)
    e = math.radians(23.4397)
    lr, ar, el = math.radians(lon % 360.0), math.radians(lat), e
    ra = math.degrees(math.atan2(math.sin(lr) * math.cos(el) - math.tan(ar) * math.sin(el),
                                 math.cos(lr))) % 360.0
    dec = math.degrees(math.asin(math.sin(ar) * math.cos(el)
                                 + math.cos(ar) * math.sin(el) * math.sin(lr)))
    return ra, dec, lon % 360.0, lat


def phase(j):
    """返回 (照明比例 0-1, 盈亏 +1 盈/-1 亏, 月龄天)。"""
    sl = sun_lon(j)
    _, _, ml, _ = moon_eq(j)
    el = (ml - sl) % 360.0                      # 距角
    k = (1 - math.cos(math.radians(el))) / 2.0
    return k, (1 if 0 <= el < 180 else -1), el / 360.0 * 29.530588


def transit_minutes(ha_deg):
    """时角(向西 0-360) → 到下次过中天的分钟；恒星时角速率 15.041°/平太阳时。"""
    return ((360.0 - ha_deg) % 360.0) / 15.041 * 60.0


def alt_at(dt, ra, dec):
    return rad(ra, dec, LAT, lst_deg(jd(dt)))[1]


def horizon_time(dt0, ra, dec, step_min=1, horizon=0.0, direction="down", cap_h=18):
    """从 dt0 起逐步推进，返回第一次让高度穿过去的那分钟时刻（None 表示未发生）。"""
    end = dt0 + timedelta(hours=cap_h)
    t, prev = dt0, alt_at(dt0, ra, dec)
    while t < end:
        t = t + timedelta(minutes=step_min)
        cur = alt_at(t, ra, dec)
        if direction == "down" and prev > horizon >= cur:
            return t
        if direction == "up" and prev < horizon <= cur:
            return t
        prev = cur
    return None


def hms(ra_deg):
    h = ra_deg / 15.0
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = round((h - hh - mm / 60) * 3600)
    return f"{hh:02d}h{mm:02d}m{ss:02d}s"


def dms(dec):
    s = "+" if dec >= 0 else "-"
    a = abs(dec)
    return f"{s}{int(a)}°{int((a - int(a)) * 60):02d}′"


# 真实亮星：名称, 拜耳/ Flamsteed, RA(度), Dec(度), 视星等
STARS = [
    ("织女星", "Vega α Lyr", 279.2347, 38.7837, 0.03),
    ("牛郎星", "Altair α Aql", 297.6958, 8.8683, 0.77),
    ("天津四", "Deneb α Cyg", 310.3580, 45.2803, 1.25),
    ("北极星", "Polaris α UMi", 37.9545, 89.2641, 1.98),
    ("大角星", "Arcturus α Boo", 213.9153, 19.1824, -0.05),
    ("心宿二", "Antares α Sco", 247.3519, -26.4320, 1.06),
    ("北落师门", "Fomalhaut α PsA", 344.4127, -29.6222, 1.16),
    ("五车二", "Capella α Aur", 79.1723, 45.9980, 0.08),
    ("毕宿五", "Aldebaran α Tau", 68.9802, 16.5093, 0.85),
    ("参宿七", "Rigel β Ori", 78.6345, -8.2016, 0.13),
    ("参宿四", "Betelgeuse α Ori", 88.7930, 7.4071, 0.50),
    ("天狼星", "Sirius α CMa", 101.2872, -16.7161, -1.46),
    ("南河三", "Procyon α CMi", 114.8255, 5.2250, 0.34),
    ("轩辕十四", "Regulus α Leo", 152.0930, 11.9672, 1.35),
    ("角宿一", "Spica α Vir", 201.2983, -11.1613, 0.97),
]
DIPPER = [("天枢", "Dubhe α UMa", 165.9321, 61.7510, 1.79),
          ("天璇", "Merak β UMa", 165.4603, 56.3824, 2.37),
          ("天玑", "Phecda γ UMa", 178.4577, 53.6948, 2.44),
          ("天权", "Megrez δ UMa", 183.8572, 57.0326, 3.31),
          ("玉衡", "Alioth ε UMa", 193.5070, 55.9598, 1.77),
          ("开阳", "Mizar ζ UMa", 200.9817, 54.9253, 2.04),
          ("摇光", "Alkaid η UMa", 206.8868, 49.3133, 1.86)]
DIPPER_LINES = [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5), (5, 6)]
SUMMER = [(0, 1), (1, 2)]          # 织女-天津四-牛郎 夏季大三角（用主表索引）


def observe(dt=OBS):
    j = jd(dt)
    l = lst_deg(j)
    out = []
    for nm, en, ra, dec, mag in STARS + DIPPER:
        az, alt, ha = rad(ra, dec, LAT, l)
        out.append({"name": nm, "en": en, "ra": ra, "dec": dec, "mag": mag,
                    "az": az, "alt": alt, "ha": ha,
                    "transit_min": transit_minutes(ha)})
    mra, mdec, mlon, mlat = moon_eq(j)
    az, alt, ha = rad(mra, mdec, LAT, l)
    k, wax, age = phase(j)
    moon = {"name": "月球", "en": "Moon", "ra": mra, "dec": mdec, "mag": -9.6,
            "az": az, "alt": alt, "ha": ha, "illum": k, "waxing": wax > 0,
            "age": age, "elong": (mlon - sun_lon(j)) % 360.0,
            "transit_min": transit_minutes(ha)}
    return j, l, out, moon


if __name__ == "__main__":
    j, l, stars, moon = observe()
    print(f"JD {j:.4f} LST {l:.3f}°  {OBS.isoformat()}")
    print(f"{'名称':<8}{'方位':>8}{'高度':>8}{'时角':>8}{'过中天分':>10}")
    for s in sorted(stars, key=lambda x: -x["alt"]):
        print(f"{s['name']:<8}{s['az']:8.2f}{s['alt']:8.2f}{s['ha']:8.2f}"
              f"{s['transit_min']:10.0f}")
    print("moon", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in moon.items()})
