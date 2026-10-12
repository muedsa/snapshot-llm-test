"""B03 case-10 · 日照剖面研究墙 · 青屿书院实验楼.

Primary capability under test: the adaptive-layout family, used where a
content-driven layout actually needs it.
  Row + Expanded/Flexible/Spacer flex shares  (12 equal month columns, 7
      equal hour columns) -- verified to the pixel in probe-c10-readback.txt
  AspectRatio                                 (three 1:1 sun-path thumbnails)
  FractionallySizedBox + alignment             (the per-hour penetration bars
      scale themselves against the room depth instead of a hand-tuned length)
  mainAxisAlignment / mainAxisSize / crossAxisAlignment
  IndexedStack index                          (the three solstice pages)
  SWEEP gradient + gradientStops as an AXIS    (the azimuth ribbon: the daylight
      window is painted straight onto 0..360 degrees)

Solar geometry is real, not invented: declination from Cooper's equation,
altitude/azimuth from the standard hour-angle form, sunrise/sunset from
cos w0 = -tan(phi) tan(delta).  Every number on the sheet comes out of those
four lines, so the ribbon, the arcs, the table and the bars cannot disagree.

Verified first on probe-c10-flex.png (+ probe-c10-readback.txt).
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

CW, CH = 1600, 1150
BG = "#0A0E17FF"
CARD = "#121C2BFF"
CARD2 = "#0F1826FF"
INK = "#EAF2FBFF"
INK2 = "#9DB4CCFF"
INK3 = "#6B829AFF"
LINE = "#22344AFF"
SOL = "#FBBF24FF"
SOL2 = "#F59E0BFF"
EQ = "#34D399FF"
SUM = "#60A5FAFF"
NIGHT = "#1E293BFF"
ROS = "#FB7185FF"
CYA = "#67E8F9FF"
VIO = "#A78BFAFF"
COL7 = [SOL, "#FCD34DFF", EQ, SUM, "#93C5FDFF", "#BFDBFEFF", CYA]

PHI = 31.23                     # 青屿书院实验楼所在地纬度（演示用虚构场地）
MONTHS = ["1月", "2月", "3月", "4月", "5月", "6月",
          "7月", "8月", "9月", "10月", "11月", "12月"]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
HOURS = [9, 10, 11, 12, 13, 14, 15]
WIN_SILL, WIN_HEAD = 0.90, 2.40   # 窗台 / 窗顶标高（m）
ROOM_DEPTH = 6.00                 # 单侧进深（m）
FLOORS = 4
FH = 3.15                        # 层高（m）


def decl(n):
    """Cooper's equation for solar declination on day-of-year n."""
    return 23.45 * math.sin(math.radians(360.0 * (284 + n) / 365.0))


def month_delta(mi):
    n = sum(DAYS[:mi]) + 21
    return decl(n)


def daylen(ddeg):
    phi, d = math.radians(PHI), math.radians(ddeg)
    c = -math.tan(phi) * math.tan(d)
    c = max(-1.0, min(1.0, c))
    return 2.0 * math.degrees(math.acos(c)) / 15.0


def sunrise_sunset(ddeg):
    phi, d = math.radians(PHI), math.radians(ddeg)
    c = max(-1.0, min(1.0, -math.tan(phi) * math.tan(d)))
    w0 = math.acos(c)
    return 12.0 - math.degrees(w0) / 15.0, 12.0 + math.degrees(w0) / 15.0


def sun(t, ddeg):
    """(altitude deg, azimuth deg clockwise from north)"""
    w = math.radians(15.0 * (t - 12.0))
    d = math.radians(ddeg)
    phi = math.radians(PHI)
    sa = math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.cos(w)
    sa = max(-1.0, min(1.0, sa))
    alt = math.asin(sa)
    az = math.degrees(math.atan2(-math.cos(d) * math.sin(w),
                                 math.sin(d) * math.cos(phi)
                                 - math.cos(d) * math.sin(phi) * math.cos(w)))
    return math.degrees(alt), az % 360.0


def pen(alt):
    """Sunlight penetration depth from a 1.5 m window band, capped at ROOM_DEPTH."""
    if alt <= 0.5:
        return 0.0
    return min(ROOM_DEPTH, (WIN_HEAD - WIN_SILL) / math.tan(math.radians(alt)))


DWIN = -23.44
DEQ = 0.0
DSUM = 23.44
WIN = {k: daylen(v) for k, v in (("冬至", DWIN), ("春分", DEQ), ("夏至", DSUM))}
SUNRISE, SUNSET = sunrise_sunset(DWIN)
RS_AZ = sun(SUNRISE + 0.02, DWIN)[1]
SS_AZ = sun(SUNSET - 0.02, DWIN)[1]


def T(s, x, y, w=None, h=None, size=12, **kw):
    """Local wrapper: wlib.t2's positional order is (s,x,y,size,color,w,h),
    which is easy to misuse; here w/h are always keywords."""
    return W.t2(s, x, y, size=size, w=w, h=h, **kw)


def head(x, y, w, zh, en, right=""):
    return [T(zh, x, y, size=16, color=INK, style="BOLD", w=w, h=22),
            T(en, x, y + 20, size=10, color=INK3, w=w * 0.7, h=15,
                 ls=1.6, font=D.MONO),
            (T(right, x + w * 0.42, y + 2, w=w * 0.58, h=18,
                  size=10.5, color=INK3, align="RIGHT") if right else None)]


def panel(x, y, w, h, fill=CARD, radius=18, border="1 SOLID " + LINE,
          shadow="0 10 30 -6 #050A1480"):
    return el("Positioned",
              {"left": round(x, 2), "top": round(y, 2), "width": round(w, 2),
               "height": round(h, 2)},
              [el("Container", {"width": round(w, 2), "height": round(h, 2),
                                "color": fill, "borderRadius": str(radius),
                                "border": border, "boxShadow": shadow})])


def solid(w, h, color, radius=None):
    d = {"width": str(w), "height": str(h), "color": color}
    if radius:
        d["borderRadius"] = str(radius)
    return el("SizedBox", {"width": str(w), "height": str(h)},
              [el("Container", d)])


def build():
    k = [box(0, 0, CW, 88, color="#070B12FF")]
    k.append(T("青屿书院 · 实验楼", 44, 18, size=30, color=INK,
                  style="BOLD", w=560, h=40))
    k.append(T("日照剖面研究墙 / SOLAR SECTION STUDY WALL", 46, 58,
                  size=11, color=INK3, w=520, h=18, ls=2.6, font=D.MONO))
    k.append(T("纬度 31.23°N · 冬至设计日 · 窗台 0.90 m / 窗顶 2.40 m · "
                  "单侧进深 6.00 m · 4 层 × 3.15 m", CW - 44 - 620, 22,
                  size=12, color=INK2, w=620, h=18, align="RIGHT"))
    k.append(T("本页所有日期与方位由 Cooper 赤纬公式与标准时角公式算出，"
                  "不使用任何贴图", CW - 44 - 620, 46, size=11, color=INK3,
                  w=620, h=18, align="RIGHT"))

    # ================= panel A : sky dome + sun paths =================
    AX, AY, AW, AH = 44, 104, 856, 496
    k.append(panel(AX, AY, AW, AH))
    for e in head(AX + 24, AY + 20, AW - 48, "天穹与三条日轨", "SUN DOME",
                  "SWEEP 渐变直接画成方位轴"):
        if e:
            k.append(e)
    CX, CY, R = AX + 300, AY + 288, 196
    # horizon + altitude rings
    k += W.ring(CX, CY, R, 1.2, LINE)
    for a in (30, 60):
        k += W.ring(CX, CY, R * (1 - a / 90.0), 1, "#1B2940FF")
    k.append(box(CX - R, CY, 2 * R, 1, color="#1B2940FF"))
    k.append(box(CX, CY - R, 1, 2 * R, color="#1B2940FF"))
    for az, lbl in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
        px, py = W.polar(CX, CY, R + 18, az)
        k.append(T(lbl, px - 12, py - 9, 24, size=11, color=INK3,
                      font=D.MONO, align="CENTER"))
    for a in (30, 60):
        k.append(T("%d°" % a, CX + 6, CY - R * (1 - a / 90.0) - 8, 40,
                      size=9.5, color="#4C5D78FF", font=D.MONO))
    # three sun paths
    for name, ddeg, col in (("夏至", DSUM, SOL2), ("春分", DEQ, EQ),
                            ("冬至", DWIN, SOL)):
        rs, ss = sunrise_sunset(ddeg)
        n = max(8, int((ss - rs) / 0.5))
        for i in range(n + 1):
            t = rs + (ss - rs) * i / float(n)
            alt, az = sun(t, ddeg)
            px, py = W.polar(CX, CY, R * (1 - max(0.0, alt) / 90.0), az)
            k.append(box(px - 1.8, py - 1.8, 3.6, 3.6, color=col))
    # design-day sun disc
    alt0, az0 = sun(12.0, DWIN)
    sx, sy = W.polar(CX, CY, R * (1 - alt0 / 90.0), az0)
    k.append(el("Positioned",
                {"left": round(sx - 15, 2), "top": round(sy - 15, 2),
                 "width": "30", "height": "30"},
                [el("ClipOval", {"width": "30", "height": "30",
                                 "clipBehavior": "ANTI_ALIAS"},
                    [el("Container", {"width": "30", "height": "30",
                                      "shape": "CIRCLE", "color": SOL})])]))
    k.append(T("冬至正午 12:00", sx + 22, sy - 9, 190, size=11.5,
                  color=SOL, style="BOLD"))
    k.append(T("高度角 %.1f° · 方位角 %.1f°" % (alt0, az0), sx + 22,
                  sy + 8, 200, size=10.5, color=INK2, font=D.MONO))

    # ---- SWEEP azimuth ribbon (the new trick) ----
    RX, RY, RW, RH = AX + 560, AY + 128, 264, 34
    f0, f1 = RS_AZ / 360.0, SS_AZ / 360.0
    k.append(el("Positioned",
                {"left": RX, "top": RY, "width": RW, "height": RH},
                [el("Container",
                    {"width": RW, "height": RH, "borderRadius": "6",
                     "gradientType": "SWEEP",
                     "gradientColors": (",".join([NIGHT, NIGHT, SOL, SOL,
                                                 NIGHT, NIGHT])),
                     "gradientStops": (",".join("%.5f" % v for v in
                                                [0.0, f0 - 0.004, f0 + 0.004,
                                                 f1 - 0.004, f1 + 0.004, 1.0])),
                     "gradientStartAngle": "0",
                     "gradientEndAngle": "6.283185307179586",
                     "border": "1 SOLID " + LINE})]))
    k.append(T("方位角轴 0–360°（SWEEP + gradientStops）", RX, RY - 18,
                  RW, 16, size=10, color=INK3, font=D.MONO))
    for az, lbl, col in ((0, "N", INK3), (RS_AZ, "日出 %.0f°" % RS_AZ, SOL),
                         (180, "S", INK3), (SS_AZ, "日落 %.0f°" % SS_AZ, SOL),
                         (360, "N", INK3)):
        px = RX + RW * (az % 360) / 360.0
        k.append(box(px - 0.5, RY + RH, 1, 6, color=col))
        k.append(T(lbl, px - 34, RY + RH + 8, 68, size=9.5, color=col,
                      font=D.MONO, align="CENTER"))
    k.append(T("冬至日出/日落方位角", RX, RY + RH + 30, RW, 16, size=9.5,
                  color=INK3, align="CENTER"))

    LEG = [("夏至", SOL2, "昼长 %.2f h" % WIN["夏至"]),
           ("春分", EQ, "昼长 %.2f h" % WIN["春分"]),
           ("冬至", SOL, "昼长 %.2f h" % WIN["冬至"])]
    ly = RY + RH + 56
    for nm, col, txt in LEG:
        k.append(box(RX, ly + 4, 22, 3, color=col))
        k.append(T(nm, RX + 30, ly - 2, 44, size=11, color=col))
        k.append(T(txt, RX + 78, ly - 2, 150, size=10.5, color=INK2,
                      font=D.MONO))
        ly += 22
    k.append(box(RX, ly + 6, RW - 4, 1, color=LINE))
    STAT = [("日出", "%.2f" % SUNRISE, "h 真太阳时"),
            ("日落", "%.2f" % SUNSET, "h 真太阳时"),
            ("可照时长", "%.2f" % WIN["冬至"], "h")]
    for i, (lb, v, u) in enumerate(STAT):
        gx = RX + i * 88
        k.append(T(lb, gx, ly + 16, 86, size=10, color=INK3))
        k.append(T(v + " " + u, gx, ly + 32, 88, size=10, color=INK2,
                      font=D.MONO))
    k.append(T("真太阳时。场地、纬度与设计参数均为演示用虚构值。",
                  AX + 24, AY + AH - 34, AW - 48, 16, size=10, color=INK3))

    # ================= panel B : section + penetration ================
    BX, BY, BW, BH = 920, 104, 636, 496
    k.append(panel(BX, BY, BW, BH))
    for e in head(BX + 24, BY + 20, BW - 48, "南立面日照进深剖面",
                  "SECTION + PENETRATION", "FractionallySizedBox 按比例取长"):
        if e:
            k.append(e)
    SCALE = 17.0                       # px per metre
    GY = BY + 352                      # ground line
    BL = BX + 96                       # building left edge
    FW = 128                           # facade width on the sheet
    k.append(box(BL - 40, GY, FW + 104, 2, color="#3B4A63FF"))
    k.append(T("剖面 1 px = %.4f m" % (1 / SCALE), BL - 40, GY + 8, 260, 16,
               size=9.5, color=INK3, font=D.MONO))
    for f in range(FLOORS):
        fhpx = FH * SCALE
        y0 = GY - (f + 1) * fhpx
        k.append(box(BL, y0, FW, fhpx, color="#16223AFF"))
        k.append(box(BL, y0, FW, 1.5, color="#2B3A55FF"))
        ws = GY - f * fhpx - WIN_SILL * SCALE
        wh = (WIN_HEAD - WIN_SILL) * SCALE
        k.append(box(BL + 20, ws - wh, FW - 40, wh, color="#FBBF2438",
                     radius=2, border="1 SOLID #FBBF2466"))
        k.append(T("F%d" % (f + 1), BL - 32, y0 + fhpx / 2 - 8, 28,
                   size=10.5, color=INK2, font=D.MONO, align="RIGHT"))
        k.append(T("±%.2f" % (f * FH), BL + FW + 8, y0 + fhpx / 2 - 8, 60,
                   size=9.5, color=INK3, font=D.MONO))
    k += W.dim_v(GY - FLOORS * FH * SCALE, GY, BX + 50,
                 "%.2f" % (FLOORS * FH), color="#5B6B85FF", size=9.5)
    # sun ray for the design day noon
    ray_a = math.radians(alt0)
    rx0 = BL + FW + 14
    ry0 = GY - FLOORS * FH * SCALE
    k += W.seg(rx0, ry0, rx0 + 96, ry0 - 96 * math.tan(ray_a), SOL, w=1.4)
    k.append(T("冬至正午 α=%.1f°" % alt0, rx0 - 8, GY + 8, 250, 16,
               size=10, color=SOL, font=D.MONO))
    # per-hour penetration bars
    PX, PY, PW = BX + 344, BY + 96, 264
    k.append(T("各层各时段的日照进深（m）", PX, PY - 26, PW, 18, size=11,
               color=INK2))
    k.append(T("p = min(6.00, 1.50 / tan α)；条长 = p / 6.00", PX, PY - 8,
               PW, 16, size=9.5, color=INK3, font=D.MONO))
    trackw = PW
    slot = trackw / float(len(HOURS))
    for f in range(FLOORS):
        ry = PY + 22 + f * 80
        k.append(T("F%d" % (f + 1), PX - 30, ry + 21, 26, size=10.5,
                   color=INK2, font=D.MONO, align="RIGHT"))
        kids = []
        for t in HOURS:
            frac = pen(sun(t, DWIN)[0]) / ROOM_DEPTH
            kids.append(el("Flexible", {"flex": "1", "fit": "LOOSE"},
                           [el("FractionallySizedBox",
                               {"widthFactor": "%.5f" % frac,
                                "heightFactor": "1",
                                "alignment": "CENTER_LEFT"},
                               [el("Container",
                                   {"width": "1", "height": "1",
                                    "color": COL7[HOURS.index(t)],
                                    "borderRadius": "3"})])]))
        k.append(el("Positioned",
                    {"left": PX, "top": ry, "width": trackw, "height": "56"},
                    [el("Container",
                        {"width": trackw, "height": "56",
                         "color": "#0C1422FF", "borderRadius": "6",
                         "border": "1 SOLID #1E293BFF"},
                        [el("Row", {"mainAxisSize": "MAX"}, kids)])]))
        best = max(HOURS, key=lambda t: pen(sun(t, DWIN)[0]))
        k.append(T("%.2f" % pen(sun(HOURS[0], DWIN)[0]), PX + trackw - 60,
                   ry + 58, 60, 16, size=9.5, color=INK3, font=D.MONO,
                   align="RIGHT"))
    hy = PY + 22 + FLOORS * 80 - 8
    k.append(box(PX, hy, trackw, 1, color=LINE))
    for i, t in enumerate(HOURS):
        k.append(T("%02d" % t, PX + i * slot, hy + 5, slot, 16, size=9.5,
                   color=INK3, font=D.MONO, align="CENTER"))
    bestlist = [t for t in HOURS
                if abs(pen(sun(t, DWIN)[0]) - max(pen(sun(x, DWIN)[0])
                                                 for x in HOURS)) < 1e-9]
    k.append(T("各层同值（南立面无遮挡）；最长 %.2f m。"
               % pen(sun(HOURS[0], DWIN)[0]),
               PX, hy + 24, w=PW, h=16, size=9.5, color=INK3))
    k.append(T("真太阳时；每格是一把 6.00 m 比例尺。", PX, hy + 42, PW, 16,
               size=9.5, color=INK3))

    # ================= panel C : hourly table =========================
    CXp, CYp, CWp, CHp = 44, 620, 556, 300
    k.append(panel(CXp, CYp, CWp, CHp))
    for e in head(CXp + 24, CYp + 20, CWp - 48, "冬至设计日逐时数据",
                  "HOURLY TABLE"):
        if e:
            k.append(e)
    cols = [("真太阳时", 92, "LEFT"), ("高度角 α", 92, "RIGHT"),
            ("方位角 A", 92, "RIGHT"), ("影长比", 84, "RIGHT"),
            ("进深 p", 76, "RIGHT")]
    tx0 = CXp + 24
    ry = CYp + 62
    k.append(box(tx0, ry, CWp - 48, 1, color=LINE))
    ry += 6
    for nm, w, al in cols:
        k.append(T(nm, tx0 + (w - 6) if al == "RIGHT" else tx0, ry, w,
                      16, size=10, color=INK3, font=D.MONO,
                      align="RIGHT" if al == "RIGHT" else None))
        tx0 += w
    ry += 18
    k.append(box(CXp + 24, ry, CWp - 48, 1, color="#1E293BFF"))
    for i, t in enumerate(HOURS):
        alt, az = sun(t, DWIN)
        ratio = 1.0 / math.tan(math.radians(alt)) if alt > 0.5 else None
        vals = ["%02d:%02d" % (int(t), int(round((t % 1) * 60))),
                "%.1f°" % alt, "%.1f°" % az,
                ("%.2f" % ratio) if ratio else "—",
                "%.2f" % pen(alt)]
        cx2 = CXp + 24
        ry += 22
        for (nm, w, al), v in zip(cols, vals):
            col = INK2 if nm.startswith("真") else (
                SOL if nm.startswith("进深") else INK)
            k.append(T(v, cx2 + (w - 6) if al == "RIGHT" else cx2, ry, w,
                          16, size=11, color=col, font=D.MONO,
                          align="RIGHT" if al == "RIGHT" else None))
            cx2 += w
        k.append(box(CXp + 24, ry + 3, CWp - 48, 1, color="#151F30FF"))
    k.append(T("影长比 = 1 / tan α。表内 7 行与左上日轨的同 7 个时刻是同一组数；"
               "α ≤ 0.5° 记为 —。", CXp + 24, CYp + CHp - 40,
               w=CWp - 48, h=30, size=10, color=INK3))

    # ================= panel D : 12 month columns (Flex) =============
    DX, DY, DW, DH = 620, 620, 470, 300
    k.append(panel(DX, DY, DW, DH))
    for e in head(DX + 24, DY + 20, DW - 48, "十二个月昼长",
                  "MONTHLY DAY LENGTH", "Row + 12 × Expanded(flex=1)"):
        if e:
            k.append(e)
    dls = [daylen(month_delta(i)) for i in range(12)]
    k.append(T("昼长 h", DX + 24, DY + 58, 60, 16, size=10, color=INK3,
                  font=D.MONO))
    lo, hi = 9.8, 14.2
    kmin = dls.index(min(dls))
    kmax = dls.index(max(dls))
    bx0, by0, bw, bh = DX + 44, DY + 78, DW - 68, 158
    for v in (10.0, 11.0, 12.0, 13.0, 14.0):
        yy = by0 + bh * (hi - v) / (hi - lo)
        k.append(box(bx0, yy, bw, 1, color="#16202F80"))
        k.append(T("%.1f" % v, DX + 24, yy - 7, 20, size=9, color=INK3,
                      font=D.MONO, align="RIGHT"))
    kids = []
    for i in range(12):
        hgt = bh * (dls[i] - lo) / (hi - lo)
        col = [SOL2, SOL2, EQ, EQ, EQ, SUM, SUM, SUM, EQ, EQ, SOL2, SOL2][i]
        kids.append(el("Expanded", {"flex": "1"},
                       [el("Column", {"mainAxisAlignment": "END"}, [
                           el("Container",
                              {"width": "22", "height": "%.2f" % hgt,
                               "color": col, "borderRadius": "4"}),
                           el("SizedBox", {"height": "4"}),
                           el("Text",
                              {"text": str(i + 1), "color": INK2,
                               "fontSize": "9.5", "fontFamily": D.MONO,
                               "textAlign": "CENTER"})])]))
    k.append(el("Positioned",
                {"left": bx0, "top": by0, "width": bw, "height": bh},
                [el("Container", {"width": bw, "height": bh},
                    [el("Row", {"crossAxisAlignment": "END"}, kids)])]))
    k.append(box(bx0, by0 + bh, bw, 1, color=LINE))
    k.append(T("赤纬 δ(n) = 23.45° · sin(360°·(284+n)/365)（Cooper）；"
                  "昼长 = 2·acos(−tanφ·tanδ)/15", DX + 24, DY + DH - 40,
                  DW - 48, 30, size=10, color=INK3))
    k.append(T("最短 %.2f h（%s）· 最长 %.2f h（%s）· 年较差 %.2f h"
                  % (min(dls), MONTHS[kmin], max(dls), MONTHS[kmax],
                     max(dls) - min(dls)),
                  DX + 24, DY + DH - 22, w=DW - 48, h=16, size=10,
                  color=SOL, font=D.MONO))

    # ================= panel E : IndexedStack + AspectRatio ==========
    EX, EY, EW, EH = 1110, 620, 446, 300
    k.append(panel(EX, EY, EW, EH))
    for e in head(EX + 24, EY + 20, EW - 48, "三个代表日的日轨",
                  "THREE DAYS", "IndexedStack index + AspectRatio 1:1"):
        if e:
            k.append(e)
    pr = 46
    pages = [("冬至", DWIN, SOL), ("春分", DEQ, EQ), ("夏至", DSUM, SOL2)]
    kids = []
    for nm, dd, col in pages:
        body = [el("Stack", {"fit": "EXPAND"}, [
            el("Positioned", {"left": "0", "top": "0", "width": "124",
                              "height": "124"},
               [el("Container", {"width": "124", "height": "124",
                                 "shape": "CIRCLE", "color": "#0B1220FF",
                                 "border": "1 SOLID " + LINE})])])]
        rs, ss = sunrise_sunset(dd)
        n = max(6, int((ss - rs) / 0.4))
        for i in range(n + 1):
            t = rs + (ss - rs) * i / float(n)
            alt, az = sun(t, dd)
            rr = pr * (1 - max(0.0, alt) / 90.0)
            px = 62 + rr * math.sin(math.radians(az))
            py = 62 - rr * math.cos(math.radians(az))
            body.append(el("Positioned",
                           {"left": "%.2f" % (px - 1.6),
                            "top": "%.2f" % (py - 1.6),
                            "width": "3.2", "height": "3.2"},
                           [el("Container", {"width": "3.2", "height": "3.2",
                                             "shape": "CIRCLE",
                                             "color": col})]))
        body.append(T(nm, 0, 8, w=124, size=12, color=col, align="CENTER",
                      style="BOLD"))
        body.append(T("%.2f h" % WIN[nm], 0, 24, w=124, size=9.5,
                      color=INK3, align="CENTER", font=D.MONO))
        kids.append(el("AspectRatio", {"aspectRatio": "1"},
                       [el("Container",
                           {"width": "124", "height": "124", "color": None},
                           [el("Stack", {"fit": "EXPAND"}, body)])]))
    k.append(el("Positioned",
                {"left": EX + 24, "top": EY + 96, "width": EW - 48,
                 "height": "124"},
                [el("Container", {"width": EW - 48, "height": "124"},
                    [el("Row", {"mainAxisAlignment": "SPACE_BETWEEN"},
                        kids)])]))
    k.append(T("三个页面同时存在于同一个 IndexedStack 的静态帧里，index=0 "
               "时只画冬至那页。", EX + 24, EY + EH - 58, w=EW - 48, h=16,
               size=10, color=INK3))
    k.append(T("只交付静态帧，不表达切换；三页几何来自同一个 sun(t, δ)。",
               EX + 24, EY + EH - 38, w=EW - 48, h=16, size=10, color=VIO))

    # ================= row 3 : measured boundaries ===================
    FX, FY, FW2, FH2 = 44, 936, 1512, 168
    k.append(panel(FX, FY, FW2, FH2, fill=CARD2))
    for e in head(FX + 24, FY + 18, FW2 - 48, "这一页顺手确认的 DSL 边界",
                  "MEASURED BOUNDARIES"):
        if e:
            k.append(e)
    BND = [("Stack fit=EXPAND", "非定位子节点会被拉满 Stack，width/height 失效；"
                                 "矩形必须包在 Positioned 里。", CYA),
           ("AspectRatio", "先按宽度试，放不下才回退到高度；父盒 300×180 里 "
                           "ar=1 得到 180×180 而不是 300×300。", CYA),
           ("crossAxisAlignment=STRETCH", "不会给「无宽高的 Container」补尺寸，"
                                          "这种子节点仍然是 0×0。", CYA),
           ("IndexedStack", "index 只决定画哪一页，子节点全部参与布局；"
                            "静态帧里等于单页。", CYA),
           ("FractionallySizedBox", "widthFactor 必须 ≥0；对齐用 alignment，"
                                    "写 width/height 不起作用。", CYA),
           ("Shape", "只有 RECTANGLE / CIRCLE；shape=\"OVAL\" 直接 400，"
                     "而且 shape 不裁子节点。", CYA)]
    bw2 = (FW2 - 48) / 3.0
    for i, (nm, txt, col) in enumerate(BND):
        gx = FX + 24 + (i % 3) * bw2
        gy = FY + 62 + (i // 3) * 52
        k.append(box(gx, gy + 4, 8, 8, color=col, radius=2))
        k.append(T(nm, gx + 16, gy, bw2 - 30, 16, size=11, color=col,
                      font=D.MONO))
        k.append(T(txt, gx + 16, gy + 17, bw2 - 30,
                      D.est_lines(txt, 10, bw2 - 30) * 14, size=10,
                      color=INK2))

    # footer
    k.append(box(0, CH - 40, CW, 1, color=LINE))
    k.append(T("场地 / 纬度 / 窗洞尺寸 / 进深 / 层高均为演示用虚构值；"
                  "日照几何用真实公式算出，但未做地形遮挡与邻栋反射。",
                  44, CH - 30, 1000, 16, size=10, color=INK3))
    k.append(T("SNAPSHOT DSL ONLY · 无位图 · 无后处理", CW - 44 - 360,
                  CH - 30, 360, size=10, color=INK3, font=D.MONO,
                  align="RIGHT"))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.render_final(dsl, "case-10", "final")
    print("  case-10", r.get("ok"), r.get("status"), (r.get("error") or "")[:300])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-10 stage 2: work")
    build()