"""Independent recomputation used to audit B03 case-01 (tide + moon) and case-10 (day length).

Re-derives the numbers that are printed on the final PNGs, using the same
formulas as the build scripts but written out longhand, so the review can tell a
real arithmetic/geometry mismatch from a rounding artefact.
"""
import math

# ---------------------------------------------------------------- case-01 tide
CONST = [("M2", 1.15, 12.4206, 32.0), ("S2", 0.42, 12.0000, 58.0),
         ("N2", 0.24, 19.3413, 12.0), ("K1", 0.28, 23.9345, 210.0),
         ("O1", 0.19, 18.7693, 195.0), ("MS4", 0.10, 6.1033, 88.0)]
MSL = 2.05


def tide(h):
    v = MSL
    for _n, a, per, ph in CONST:
        v += a * math.cos(2 * math.pi * (h - ph / 15.0) / per)
    return v


S = [tide(i) for i in range(25)]
hi, lo = max(S), min(S)
print("case-01 tide  (hourly samples, same as build_c01)")
print("  high %.4f m @ %02d:00   low %.4f m @ %02d:00   range %.4f"
      % (hi, S.index(hi), lo, S.index(lo), hi - lo))
print("  tide @ NOW 09.45 = %.4f m" % tide(9.75))
print("  printed on png : 3.84 @15:00 / 0.39 @09:00 / range 3.46 / now 0.67")

# ---------------------------------------------------------------- case-01 moon
# Moon age and illuminated fraction from the mean elongation D (Meeus ch. 47
# low-precision series).  D = 0 at new moon, 180 at full moon.


def jd(y, m, d, h_ut):
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return (math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1))
            + d + b - 1524.5) + h_ut / 24.0


T = (jd(2026, 10, 5, 1.75) - 2451545.0) / 36525.0
D = (297.8501921 + 445267.1114034 * T - 0.0018819 * T ** 2) % 360.0
k = (1 - math.cos(math.radians(D))) / 2.0
age = D / 360.0 * 29.530588
phase = ("盈" if D < 90 else "上弦" if D < 135 else "盈凸" if D < 225
         else "满" if D < 270 else "亏凸" if D < 315 else "下弦" if D < 360 else "")
print("case-01 moon   (2026-10-05 09:45 +08:00 == 01:45 UTC)")
print("  mean elongation D = %.3f deg  ->  age %.2f d, illuminated %.4f (%.1f%%)"
      % (D, age, k, k * 100))
print("  named phase would be %s月 (%s), lit limb on the %s in the N hemisphere"
      % (phase, "waning" if D > 180 else "waxing", "left" if D > 180 else "right"))
print("  printed on png : 亏凸月 · 照亮 72%   (MOON_ILLUM = 0.72, hard-coded)")

# --------------------------------------------------------------- case-10 sun
PHI = 31.23
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def decl(n):
    return 23.45 * math.sin(math.radians(360.0 * (284 + n) / 365.0))


def daylen(ddeg):
    c = -math.tan(math.radians(PHI)) * math.tan(math.radians(ddeg))
    return 2.0 * math.degrees(math.acos(max(-1.0, min(1.0, c)))) / 15.0


dl = []
for mi in range(1, 13):
    dl.append((mi, sum(DAYS[:mi - 1]) + 21, daylen(decl(sum(DAYS[:mi - 1]) + 21))))
print("case-10 day length (Cooper, day-of-year = 21st of each month)")
print("  " + "  ".join("%d:%d:%.3f" % (mi, n, v) for mi, n, v in dl))
mn = min(dl, key=lambda r: r[2])
mx = max(dl, key=lambda r: r[2])
print("  min %.4f h (month %d)   max %.4f h (month %d)   range %.4f h"
      % (mn[2], mn[0], mx[2], mx[0], mx[2] - mn[2]))
print("  printed on png : 9.97 (12月) / 14.03 (6月) / 年较差 4.07")
