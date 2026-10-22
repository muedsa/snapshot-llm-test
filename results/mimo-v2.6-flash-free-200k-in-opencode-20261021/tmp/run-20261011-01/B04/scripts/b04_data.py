# -*- coding: utf-8 -*-
"""B04 single source of truth: NASA NSSDCA fact-sheet values + cross-checks.

Provenance:
  SRC-01 planetary fact sheet metric (updated 2025-03-18)
  SRC-02 moon fact sheet   (updated 2024-01-11)
  SRC-03 pluto fact sheet  (updated 2024-01-11)
Values transcribed verbatim into research/*.txt; this module re-states them
and enforces plan-v1a cross-checks (AM-1..AM-5) at generation time.

Body order for 10-column rows (as printed by SRC-01):
  MERCURY VENUS EARTH MOON MARS JUPITER SATURN URANUS NEPTUNE PLUTO
Rows whose MOON column carries * in the source are HELIOCENTRIC-invalid for
the Moon: distance/perihelion/aphelion/orbital period/velocity for MOON are
about the Earth (handled: moon_oe_* below, planets rows keep 0 for moon).
"""
import math
import os

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../B04

SRC = {
    "SRC-01": dict(
        title="Planetary Fact Sheet (Metric)",
        org="Dr. David R. Williams / NSSDCA, NASA Goddard Space Flight Center",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/",
        updated="2025-03-18",
        accessed="2026-10-20T21:05+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-01-planetary-factsheet-metric.txt",
    ),
    "SRC-02": dict(
        title="Moon Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html",
        updated="2024-01-11",
        accessed="2026-10-20T21:06+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-02-moon-factsheet.txt",
    ),
    "SRC-03": dict(
        title="Pluto Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/plutofact.html",
        updated="2024-01-11",
        accessed="2026-10-20T21:07+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-03-pluto-factsheet.txt",
    ),
    # --- plan-v1b source-base extension (all same author/site as SRC-01..03) ---
    "SRC-04": dict(
        title="Notes on the Fact Sheets",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/fact_notes.html",
        updated="2024-05-06",
        accessed="2026-10-20T21:40+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-04-fact-notes.txt",
    ),
    "SRC-05": dict(
        title="Venus Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/venusfact.html",
        updated="2024-01-11",
        accessed="2026-10-20T21:36+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-05-venus-factsheet.txt",
    ),
    "SRC-06": dict(
        title="Mercury Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/mercuryfact.html",
        updated="2024-01-11",
        accessed="2026-10-20T21:44+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-06-mercury-factsheet.txt",
    ),
    "SRC-07": dict(
        title="Mars Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html",
        updated="2025-05-19",
        accessed="2026-10-20T21:45+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-07-mars-factsheet.txt",
    ),
    "SRC-08": dict(
        title="Jupiter Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/jupiterfact.html",
        updated="2024-10-02",
        accessed="2026-10-20T21:37+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-08-jupiter-factsheet.txt",
    ),
    "SRC-09": dict(
        title="Saturn Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/saturnfact.html",
        updated="2025-03-18",
        accessed="2026-10-20T21:38+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-09-saturn-factsheet.txt",
    ),
    "SRC-10": dict(
        title="Uranus Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/uranusfact.html",
        updated="2024-10-02",
        accessed="2026-10-20T21:39+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-10-uranus-factsheet.txt",
    ),
    "SRC-11": dict(
        title="Neptune Fact Sheet",
        org="Dr. David R. Williams / NSSDCA, NASA GSFC",
        url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/neptunefact.html",
        updated="2024-10-03",
        accessed="2026-10-20T21:41+08:00",
        file="tmp/run-20261011-01/B04/research/SRC-11-neptune-factsheet.txt",
    ),
}

BODIES = ["mercury", "venus", "earth", "moon", "mars",
          "jupiter", "saturn", "uranus", "neptune", "pluto"]
ZH = {"mercury": "水星", "venus": "金星", "earth": "地球", "moon": "月球",
      "mars": "火星", "jupiter": "木星", "saturn": "土星", "uranus": "天王星",
      "neptune": "海王星", "pluto": "冥王星"}
IDX = {b: i for i, b in enumerate(BODIES)}

# --- SRC-01 verbatim rows (10 cols) ---
MASS_1E24 = dict(zip(BODIES, [0.330, 4.87, 5.97, 0.073, 0.642,
                              1898, 568, 86.8, 102, 0.0130]))
DIAM_KM = dict(zip(BODIES, [4879, 12104, 12756, 3475, 6792,
                            142984, 120536, 51118, 49528, 2376]))
DENS_KGM3 = dict(zip(BODIES, [5429, 5243, 5514, 3340, 3934,
                              1326, 687, 1270, 1638, 1850]))
GRAV_MS2 = dict(zip(BODIES, [3.7, 8.9, 9.8, 1.6, 3.7,
                             23.1, 9.0, 8.7, 11.0, 0.7]))
ESC_KMS = dict(zip(BODIES, [4.3, 10.4, 11.2, 2.4, 5.0,
                            59.5, 35.5, 21.3, 23.5, 1.3]))
ROT_H = dict(zip(BODIES, [1407.6, -5832.5, 23.9, 655.7, 24.6,
                          9.9, 10.7, -17.2, 16.1, -153.3]))
DAY_H = dict(zip(BODIES, [4222.6, 2802.0, 24.0, 708.7, 24.7,
                          9.9, 10.7, 17.2, 16.1, 153.3]))
# distance rows: moon's source cells are Earth-relative (*) -> None here
DIST_1E6 = dict(zip(BODIES, [57.9, 108.2, 149.6, None, 228.0,
                             778.5, 1432.0, 2867.0, 4515.0, 5906.4]))
PERI_1E6 = dict(zip(BODIES, [46.0, 107.5, 147.1, None, 206.7,
                             740.6, 1357.6, 2732.7, 4471.1, 4436.8]))
APHI_1E6 = dict(zip(BODIES, [69.8, 108.9, 152.1, None, 249.3,
                             816.4, 1506.5, 3001.4, 4558.9, 7375.9]))
ORPPER_D = dict(zip(BODIES, [88.0, 224.7, 365.2, None, 687.0,
                             4331, 10747, 30589, 59800, 90560]))
ORBVEL_KMS = dict(zip(BODIES, [47.4, 35.0, 29.8, None, 24.1,
                               13.1, 9.7, 6.8, 5.4, 4.7]))
INCL_DEG = dict(zip(BODIES, [7.0, 3.4, 0.0, 5.1, 1.8,
                             1.3, 2.5, 0.8, 1.8, 17.2]))
ECC = dict(zip(BODIES, [0.206, 0.007, 0.017, 0.055, 0.094,
                        0.049, 0.052, 0.047, 0.010, 0.244]))
OBLIQ_DEG = dict(zip(BODIES, [0.034, 177.4, 23.4, 6.7, 25.2,
                              3.1, 26.7, 97.8, 28.3, 119.5]))
TEMP_C = dict(zip(BODIES, [167, 464, 15, -20, -65,
                           -110, -140, -195, -200, -225]))
# pressure: giants are Unknown* in source (NOT zero)
PRESSURE = dict(zip(BODIES, [0.0, 92.0, 1.0, 0.0, 0.01,
                             None, None, None, None, 1e-5]))
MOONS = dict(zip(BODIES, [0, 0, 1, 0, 2, 95, 274, 28, 16, 5]))
RINGS = dict(zip(BODIES, [False, False, False, False, False,
                          True, True, True, True, False]))
MAGNET = dict(zip(BODIES, ["yes", "no", "yes", "no", "no",
                           "yes", "yes", "yes", "yes", "unknown"]))

PLANETS8 = ["mercury", "venus", "earth", "mars",
            "jupiter", "saturn", "uranus", "neptune"]
INNER4 = ["mercury", "venus", "earth", "mars"]
GIANTS4 = ["jupiter", "saturn", "uranus", "neptune"]

# --- SRC-02 verbatim (moon facts) ---
MOON_SRC02 = dict(mass_1e24=0.07346, earth_mass_1e24=5.9724, mass_ratio=0.0123,
                  mean_radius_km=1737.4, earth_mean_radius_km=6371.0,
                  radius_ratio=0.2727, eq_radius_km=1738.1,
                  earth_eq_radius_km=6378.1, eq_radius_ratio=0.2725,
                  dens=3344, dens_ratio=0.606, grav=1.62, grav_ratio=0.165,
                  esc=2.38, esc_ratio=0.213,
                  semimajor_1e6=0.3844, revol_d=27.3217, synodic_d=29.53,
                  rot_h=655.720, obliq=6.68, incl_ecliptic=5.145,
                  ecc=0.0549, recession_cm_yr=3.8,
                  blackbody_k=270.4, earth_blackbody_k=254.0,
                  solar_irr=1361.0, albedo=0.11)

# --- SRC-03 verbatim (pluto facts) ---
PLUTO_SRC03 = dict(mass_1e24=0.01303, radius_km=1188, dens=1854, grav=0.62,
                   esc=1.21, moons=5, semimajor_1e6=5869.656,
                   revol_d=90560, peri_1e6=4434.987, aphi_1e6=7304.326,
                   vel=4.64, incl=17.16, ecc=0.2444, rot_h=-153.2928,
                   day_h=153.2820, obliq=119.51,
                   discoverer="Clyde Tombaugh", discovered="1930-02-18",
                   pressure_microbar=13, temp_lo_k=24, temp_hi_k=38,
                   atm_n2=99.0, atm_ch4=0.5, atm_co=0.05,
                   solar_irr=0.873, earth_solar_irr=1361.0,
                   blackbody_k=37.5, opp_dist_1e6=5756.78, opp_mag=15.1,
                   charon_dist_km=19596, charon_period_d=6.3872,
                   charon_radius_km=606,
                   moons_orbit=[("Styx", 42413, 20.16, 10.5),
                                ("Nix", 48690, 24.85, None),
                                ("Kerberos", 57750, 32.17, None),
                                ("Hydra", 64721, 38.20, 62.0)])

# --- plan-v1b data from SRC-04..11 (definitions + per-body sheets) ---
# volumetric mean radius, km (SRC-05..07/08/09/10/11 rows; moon SRC-02;
# pluto SRC-03 "Mean Radius"; earth column of the sheets)
MEAN_R_KM = dict(mercury=2439.7, venus=6051.8, earth=6371.0, moon=1737.4,
                 mars=3389.5, jupiter=69911, saturn=58232, uranus=25362,
                 neptune=24622, pluto=1188)
# equatorial radius, km (same sheets)
EQ_R_KM = dict(mercury=2440.5, venus=6051.8, earth=6378.1, moon=1738.1,
               mars=3396.2, jupiter=71492, saturn=60268, uranus=25559,
               neptune=24764, pluto=1188)
# GM, sheet unit = 10^6 km^3/s^2 (moon derived per SRC-04: GM = g_mean*r_mean^2)
GM_M6 = dict(mercury=0.022032, venus=0.32486, earth=0.39860, moon=0.004890,
             mars=0.042828, jupiter=126.687, saturn=37.931, uranus=5.7940,
             neptune=6.8351, pluto=0.000870)
# convert: 10^6 km^3/s^2 -> m^3/s^2  (x 1e15)
def gm_m3s2(b):
    return GM_M6[b] * 1e15

# black-body temperature, K (sheets; earth col = 254.0, moon SRC-02 270.4)
BLACKBODY_K = dict(mercury=439.6, venus=226.6, earth=254.0, moon=270.4,
                   mars=209.8, jupiter=109.9, saturn=81.0, uranus=58.1,
                   neptune=46.6, pluto=37.5)
# solar irradiance at semimajor axis, W/m^2 (sheets; moon = earth orbit value)
SOLAR_IRR_WM2 = dict(mercury=9082.7, venus=2601.3, earth=1361.0, moon=1361.0,
                     mars=586.2, jupiter=50.26, saturn=14.82, uranus=3.69,
                     neptune=1.508, pluto=0.873)
# ellipticity/flattening (sheets; (a-c)/a) -- giants only asserted (sourced rows)
ELLIPTICITY = dict(mercury=0.0009, venus=0.0000, earth=0.00335, mars=0.00589,
                   jupiter=0.06487, saturn=0.09796, uranus=0.02293,
                   neptune=0.01708, pluto=0.0000)
# equatorial effective surface acceleration, m/s^2 (sheets' "acceleration eq.")
EQ_ACC_MS2 = dict(mercury=3.70, venus=8.87, earth=9.78, mars=3.69,
                  jupiter=23.12, saturn=8.96, uranus=8.69, neptune=11.00)
# giant-planet temperature defined at 1-bar level, K (sheets' "average_temperature")
GIANT_1BAR_K = dict(jupiter=165, saturn=134, uranus=76, neptune=72)
# sidereal orbital periods, days, exact values from per-body sheets (AM-11)
EXACT_ORP_D = dict(mercury=87.969, venus=224.701, earth=365.256, mars=686.980,
                   jupiter=4332.589, saturn=10755.699, uranus=30685.4,
                   neptune=60189.018)
# cross-table discrepancies to document (AM-11) -- locked so we never "harmonize"
XTABLE = dict(pluto_grav_src01=0.7, pluto_grav_src03=0.62,
              pluto_esc_src01=1.3, pluto_esc_src03=1.21,
              mars_temp_src01_C=-65, mars_temp_src07_K=214,
              earth_dens_src01=5514, earth_dens_sheets=5513,
              # pluto orbit rows: SRC-01 (2025-03) vs SRC-03 sheet (2024-01)
              pluto_peri_src01=4436.8, pluto_peri_src03=4434.987,
              pluto_aph_src01=7375.9, pluto_aph_src03=7304.326,
              pluto_a_src01=5906.4, pluto_a_src03=5869.656)


def a_check(cond, msg):
    """assertion helper: raises with the recomputed value in the message."""
    if not cond:
        raise AssertionError("B04-FACT-CHECK FAILED: " + msg)


# ---------------- plan-v1a cross-checks (run by each case as needed) --------

def ck_case01():
    """diameter scale facts (plan case-01)."""
    j_m = DIAM_KM["jupiter"] / float(DIAM_KM["mercury"])
    e_m = DIAM_KM["earth"] / float(DIAM_KM["moon"])
    a_check(abs(j_m - 29.3) < 0.1, "jupiter/mercury=%.3f expect~29.3" % j_m)
    a_check(abs(e_m - 3.67) < 0.02, "earth/moon=%.4f expect~3.67" % e_m)
    return dict(jup_mer=round(j_m, 2), ear_moon=round(e_m, 3))


def ck_case02():
    """log monotonicity + adjacent orbit gaps + pluto-neptune crossing."""
    seq = [DIST_1E6[b] for b in PLANETS8]
    a_check(all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)),
            "heliocentric distance not monotonic: %s" % seq)
    gaps = []
    for a, b in zip(PLANETS8, PLANETS8[1:]):
        g = PERI_1E6[b] - APHI_1E6[a]
        a_check(g > 0, "orbit overlap %s(aph %s) >= %s(peri %s)"
                % (a, APHI_1E6[a], b, PERI_1E6[b]))
        gaps.append(round(g, 1))
    a_check(PERI_1E6["pluto"] < APHI_1E6["neptune"],
            "pluto peri %s should be < neptune aphi %s (crossing)"
            % (PERI_1E6["pluto"], APHI_1E6["neptune"]))
    ratio = DIST_1E6["neptune"] / DIST_1E6["mercury"]
    a_check(abs(ratio - 78) < 1.5, "neptune/mercury=%.2f expect~78" % ratio)
    return dict(gaps=gaps, ratio=round(ratio, 1),
                crossing=(PERI_1E6["pluto"], APHI_1E6["neptune"]))


def ck_case03():
    """Kepler T^2/a^3 (AM-1 keeps plan range [0.96,1.04]) + v=2*pi*a/T."""
    a_e, t_e = DIST_1E6["earth"], ORPPER_D["earth"]
    rows = []
    for b in PLANETS8 + ["pluto"]:
        a, t = DIST_1E6[b], ORPPER_D[b]
        k = (t * t / (a * a * a)) / (t_e * t_e / (a_e * a_e * a_e))
        a_check(0.96 <= k <= 1.04, "%s T^2/a^3 ratio=%.4f outside [0.96,1.04]"
                % (b, k))
        # plan claim: rounded values inside [0.975, 1.002]
        a_check(0.975 <= round(k, 3) <= 1.002,
                "%s rounded k=%.3f outside plan band [0.975,1.002]" % (b, k))
        v = 2 * math.pi * a * 1e6 / (t * 86400.0)
        d = abs(v - ORBVEL_KMS[b]) / ORBVEL_KMS[b]
        a_check(d <= 0.03, "%s v calc=%.3f vs table %.1f dev=%.2f%%"
                % (b, v, ORBVEL_KMS[b], d * 100))
        rows.append((b, round(k, 3), round(v, 2), round(d * 100, 1)))
    # AM-11: SRC-01 rounded periods vs per-body-sheet exact periods (footnote)
    rounded = []
    for b in EXACT_ORP_D:
        d_p = (ORPPER_D[b] - EXACT_ORP_D[b]) / EXACT_ORP_D[b]
        rounded.append((b, ORPPER_D[b], EXACT_ORP_D[b], round(d_p * 100, 2)))
    nept = [r for r in rounded if r[0] == "neptune"][0]
    a_check(abs(nept[3] + 0.65) < 0.05,
            "neptune period rounding shift moved: %.2f%%" % nept[3])
    return dict(rows=rows, period_rounding=rounded)


def ck_sign_source():
    """AM-10: the retrograde-sign quote must exist in the saved SRC-04 file."""
    path = os.path.join(_HERE, "research", "SRC-04-fact-notes.txt")
    with open(path, "r", encoding="utf-8") as fh:
        txt = fh.read()
    a_check("indicates retrograde rotation." in txt,
            "SRC-04 retrograde quote missing from evidence file")
    a_check("had no atmosphere, but the same albedo" in txt,
            "SRC-04 black-body definition quote missing")
    a_check("Radius of a sphere with the same" in txt,
            "SRC-04 volumetric mean radius quote missing")
    a_check("not including the effects of rotation" in txt,
            "SRC-04 gravity definition quote missing")
    return "SRC-04 quotes verified in evidence file"


def ck_xtable():
    """AM-11: cross-table discrepancies locked (documented, never harmonized)."""
    a_check(XTABLE["pluto_grav_src01"] == GRAV_MS2["pluto"] == 0.7,
            "pluto gravity SRC-01 value drifted")
    a_check(XTABLE["pluto_grav_src03"] == PLUTO_SRC03["grav"] == 0.62,
            "pluto gravity SRC-03 value drifted")
    a_check(XTABLE["pluto_esc_src01"] == ESC_KMS["pluto"] == 1.3,
            "pluto escape SRC-01 value drifted")
    a_check(XTABLE["pluto_esc_src03"] == PLUTO_SRC03["esc"] == 1.21,
            "pluto escape SRC-03 value drifted")
    a_check(XTABLE["mars_temp_src01_C"] == TEMP_C["mars"] == -65,
            "mars temp SRC-01 drifted")
    a_check(XTABLE["mars_temp_src07_K"] == 214, "mars temp SRC-07 drifted")
    a_check(XTABLE["earth_dens_src01"] == DENS_KGM3["earth"] == 5514,
            "earth density SRC-01 drifted")
    a_check(XTABLE["earth_dens_sheets"] == 5513, "earth density sheets drifted")
    # pluto gravity discrepancy magnitude ~13% (0.7 vs 0.62)
    rel = (0.7 - 0.62) / 0.62
    a_check(abs(rel - 0.129) < 0.005, "pluto gravity gap moved: %.1f%%"
            % (rel * 100))
    # pluto orbital rows: SRC-01 vs SRC-03 sheet (epoch/vintage difference)
    a_check(XTABLE["pluto_peri_src01"] == PERI_1E6["pluto"] == 4436.8,
            "pluto perihelion SRC-01 drifted")
    a_check(abs(PLUTO_SRC03["peri_1e6"] - XTABLE["pluto_peri_src03"]) < 1e-9,
            "pluto perihelion SRC-03 drifted")
    a_check(XTABLE["pluto_aph_src01"] == APHI_1E6["pluto"] == 7375.9,
            "pluto aphelion SRC-01 drifted")
    a_check(abs(PLUTO_SRC03["aphi_1e6"] - XTABLE["pluto_aph_src03"]) < 1e-9,
            "pluto aphelion SRC-03 drifted")
    d_aph = (7375.9 - 7304.326) / 7304.326
    a_check(abs(d_aph - 0.00843) < 0.002,
            "pluto aphelion gap moved: %.2f%%" % (d_aph * 100))
    # both sources agree pluto perihelion < neptune aphelion (crossing fact)
    a_check(PERI_1E6["pluto"] < APHI_1E6["neptune"]
            and PLUTO_SRC03["peri_1e6"] < APHI_1E6["neptune"],
            "pluto-neptune crossing fact changed")
    return "5+3 cross-table discrepancies locked"


def solar_day_h(rot_h, orp_d):
    """AM-1 formula: 1/D = 1/|R| -/+ 1/P ; - prograde, + retrograde.
    P in hours; for the Moon P is the heliocentric year of the Earth-Moon
    system (SRC-01 year for earth) because day length follows sun direction."""
    if orp_d is None:
        raise ValueError("need explicit period")
    p = orp_d * 24.0
    inv = 1.0 / abs(rot_h)
    inv += (1.0 / p) if rot_h < 0 else -(1.0 / p)
    return 1.0 / inv


def ck_case04():
    """AM-1: solar day formula dev <=1% every row; Mercury 2yr claim; sign."""
    rows = {}
    for b in BODIES:
        p = ORPPER_D[b] if b != "moon" else 365.2  # AM-1 moon convention
        d = solar_day_h(ROT_H[b], p)
        dev = abs(d - DAY_H[b]) / DAY_H[b]
        a_check(dev <= 0.01, "%s solar day calc=%.1f vs table %.1f dev=%.2f%%"
                % (b, d, DAY_H[b], dev * 100))
        rows[b] = (round(d, 1), round(dev * 100, 2))
    # Mercury: solar day = 2 sidereal years = 3 rotations (3:2 resonance)
    mer_d = DAY_H["mercury"] / 24.0
    a_check(175.5 <= mer_d <= 176.5, "mercury day=%.2f d not ~176" % mer_d)
    a_check(abs(mer_d - 2 * ORPPER_D["mercury"]) < 1.0,
            "2*88=%.1f vs %.1f" % (2 * ORPPER_D["mercury"], mer_d))
    a_check(abs(mer_d - 3 * abs(ROT_H["mercury"]) / 24.0) < 0.5,
            "3*rot=%.2f vs %.2f" % (3 * abs(ROT_H["mercury"]) / 24.0, mer_d))
    # AM-2 sign semantics via internal consistency
    retro_d = solar_day_h(-abs(ROT_H["mercury"]), ORPPER_D["mercury"])
    a_check(abs(retro_d - DAY_H["mercury"]) / DAY_H["mercury"] > 0.5,
            "mercury as retrograde would fit? %.1f vs %.1f"
            % (retro_d, DAY_H["mercury"]))
    fwd = 1.0 / abs(ROT_H["venus"]) - 1.0 / (ORPPER_D["venus"] * 24.0)
    a_check(fwd < 0, "venus prograde formula should be negative (no solution)")
    return rows


def ck_case05():
    """AM-7: keep gR<=10% (secondary), add GM-based v<=1.5% (primary),
    plus SRC-01 gravity row == sheet equatorial effective accel cross-check."""
    out = {}
    for b in BODIES:
        g = GRAV_MS2[b]
        r = DIAM_KM[b] * 1000.0 / 2.0          # table diameter = equatorial-ish
        v = math.sqrt(2 * g * r) / 1000.0
        dev = abs(v - ESC_KMS[b]) / ESC_KMS[b]
        a_check(dev <= 0.10, "%s sqrt(2gR)=%.2f vs table %.1f dev=%.1f%%"
                % (b, v, ESC_KMS[b], dev * 100))
        # primary: v = sqrt(2GM/r) with sheet GM; pluto cross-table handled
        v2 = math.sqrt(2.0 * gm_m3s2(b) / r) / 1000.0
        ref = XTABLE["pluto_esc_src03"] if b == "pluto" else ESC_KMS[b]
        lim = 0.005 if b == "pluto" else 0.015
        dev2 = abs(v2 - ref) / ref
        a_check(dev2 <= lim, "%s sqrt(2GM/r)=%.3f vs %.2f dev=%.2f%% (lim %.1f%%)"
                % (b, v2, ref, dev2 * 100, lim * 100))
        out[b] = dict(gR=round(v, 2), gR_dev=round(dev * 100, 1),
                      gm=round(v2, 3), gm_dev=round(dev2 * 100, 2),
                      w60=round(60 * g / GRAV_MS2["earth"], 1))
    # AM-7: SRC-01 gravity row == sheet equatorial effective accel (giants)
    for b in GIANTS4:
        a_check(abs(GRAV_MS2[b] - EQ_ACC_MS2[b]) <= 0.05,
                "%s gravity row %.1f != sheet eq accel %.2f"
                % (b, GRAV_MS2[b], EQ_ACC_MS2[b]))
    # AM-11: pluto cross-table escape discrepancy locked at -6.9% (SRC-01 side)
    v_pl = math.sqrt(2.0 * gm_m3s2("pluto") / (DIAM_KM["pluto"] * 500.0)) / 1000.0
    d_pl = (v_pl - XTABLE["pluto_esc_src01"]) / XTABLE["pluto_esc_src01"]
    a_check(abs(d_pl + 0.069) < 0.005,
            "pluto GM-vs-SRC01 discrepancy moved: %.1f%%" % (d_pl * 100))
    return out


def ck_case06():
    """plan-v1b AM-8: temp order + black-body deltas + irradiance contrast."""
    order = sorted(BODIES, key=lambda b: -TEMP_C[b])
    expect = ["venus", "mercury", "earth", "moon", "mars",
              "jupiter", "saturn", "uranus", "neptune", "pluto"]
    a_check(order == expect, "temp order %s" % order)
    a_check(TEMP_C["venus"] - TEMP_C["mercury"] == 297, "venus-mercury=297")
    # black-body deltas: actual(surface, degC->K) - blackbody(K)
    delta = {}
    for b, c in (("mercury", 167), ("earth", 15), ("venus", 464)):
        k = c + 273.15
        delta[b] = round(k - BLACKBODY_K[b], 1)
    a_check(abs(delta["mercury"]) <= 2.0,
            "mercury delta=%.1f K expect ~0.4" % delta["mercury"])
    a_check(abs(delta["earth"] - 34.15) <= 0.5,
            "earth delta=%.2f K expect 34.15" % delta["earth"])
    a_check(abs(delta["venus"] - 510.55) <= 0.5,
            "venus delta=%.2f K expect 510.55" % delta["venus"])
    # C->K conversion cross-checks against sheet "average temperature"
    a_check(abs((167 + 273.15) - 440.0) <= 1.0, "mercury 167C vs sheet 440K")
    a_check(abs((464 + 273.15) - 737.0) <= 1.0, "venus 464C vs sheet 737K")
    # irradiance contrast: mercury receives 3.49x venus yet is 297C colder
    irr = SOLAR_IRR_WM2["mercury"] / SOLAR_IRR_WM2["venus"]
    a_check(abs(irr - 3.49) < 0.02, "mercury/venus irradiance=%.3f expect 3.49"
            % irr)
    # giants' temp row ~ their 1-bar temperature (AM-8 honesty note basis)
    bar = {}
    for b in GIANTS4:
        diff = abs((TEMP_C[b] + 273.15) - GIANT_1BAR_K[b])
        a_check(diff <= 3.0, "%s temp row %.1fK vs 1-bar %dK diff %.1f"
                % (b, TEMP_C[b] + 273.15, GIANT_1BAR_K[b], diff))
        bar[b] = round(diff, 1)
    return dict(order=order, delta=delta, irr=round(irr, 2),
                giant_1bar_diff=bar)


def ck_case07():
    """moon counts (total 421 per plan) + pluto satellite axes monotonic."""
    total = sum(MOONS[b] for b in BODIES)
    a_check(total == 421, "total moons=%d expect 421" % total)
    axes = [m[1] for m in PLUTO_SRC03["moons_orbit"]]
    a_check(all(axes[i] < axes[i + 1] for i in range(3)),
            "pluto moon axes not monotonic: %s" % axes)
    a_check(MOONS["saturn"] > MOONS["jupiter"],
            "saturn %d should exceed jupiter %d" % (MOONS["saturn"],
                                                    MOONS["jupiter"]))
    return dict(total=total, axes=axes)


def ck_case08():
    """AM-3 tiered cross-validation SRC-02 ratios vs SRC-01 rows."""
    out = {}
    # radius: SRC-01 diameter row = equatorial (earth 12756 = 2*6378.1),
    # so like-for-like cross-check uses SRC-02 equatorial-radius ratio 0.2725.
    # (vs SRC-02 mean ratio 0.2727 the diff is 0.102% -- equatorial/mean basis,
    #  documented as known source-basis difference, not a data conflict.)
    r = DIAM_KM["moon"] / float(DIAM_KM["earth"])
    eq_ratio = MOON_SRC02["eq_radius_km"] / MOON_SRC02["earth_eq_radius_km"]
    dev_r = abs(r - eq_ratio) / eq_ratio
    a_check(dev_r <= 0.001, "radius ratio cross=%.5f vs eq %.5f dev=%.3f%%"
            % (r, eq_ratio, dev_r * 100))
    r_mean = r
    dev_mean = abs(r_mean - MOON_SRC02["radius_ratio"]) / \
        MOON_SRC02["radius_ratio"]
    a_check(dev_mean <= 0.0015,
            "radius vs mean ratio dev=%.3f%% (<=0.15%% basis diff)"
            % (dev_mean * 100))
    d = DENS_KGM3["moon"] / float(DENS_KGM3["earth"])
    dev_d = abs(d - MOON_SRC02["dens_ratio"]) / MOON_SRC02["dens_ratio"]
    a_check(dev_d <= 0.001, "dens ratio cross=%.5f dev=%.3f%%"
            % (d, dev_d * 100))
    m = MASS_1E24["moon"] / MASS_1E24["earth"]
    dev_m = abs(m - MOON_SRC02["mass_ratio"]) / MOON_SRC02["mass_ratio"]
    a_check(dev_m <= 0.01, "mass ratio cross=%.5f dev=%.3f%% (<=1%% AM-3)"
            % (m, dev_m * 100))
    gv = GRAV_MS2["moon"] / GRAV_MS2["earth"]
    dev_g = abs(gv - MOON_SRC02["grav_ratio"]) / MOON_SRC02["grav_ratio"]
    a_check(dev_g <= 0.015, "grav ratio cross=%.5f dev=%.3f%% (<=1.5%% AM-3)"
            % (gv, dev_g * 100))
    ev = ESC_KMS["moon"] / ESC_KMS["earth"]
    dev_e = abs(ev - MOON_SRC02["esc_ratio"]) / MOON_SRC02["esc_ratio"]
    a_check(dev_e <= 0.01, "esc ratio cross=%.5f dev=%.3f%% (<=1%% AM-3)"
            % (ev, dev_e * 100))
    # distance facts (SRC-02 footnote: ~357,000-407,000 km course range)
    a_check(abs(MOON_SRC02["semimajor_1e6"] * 1e6 - 384400) < 100,
            "semimajor %.0f" % (MOON_SRC02["semimajor_1e6"] * 1e6))
    # recession: 3.8 cm/yr -> per century
    a_check(abs(MOON_SRC02["recession_cm_yr"] - 3.8) < 1e-9, "recession")
    return dict(radius_dev=round(dev_r * 100, 3),
                dens_dev=round(dev_d * 100, 3),
                mass_dev=round(dev_m * 100, 3),
                grav_dev=round(dev_g * 100, 3),
                esc_dev=round(dev_e * 100, 3))


def ck_case09():
    """pluto card numbers."""
    p = PLUTO_SRC03
    irr = p["solar_irr"] / p["earth_solar_irr"]
    a_check(abs(irr - 1.0 / 1560) < 1e-4,
            "solar irr ratio=%.6f vs 1/1560=%.6f" % (irr, 1.0 / 1560))
    ch = p["charon_radius_km"] / float(p["radius_km"])
    a_check(0.50 <= ch <= 0.52, "charon/pluto radius=%.3f" % ch)
    a_check(p["pressure_microbar"] < 100, "pressure %g microbar"
            % p["pressure_microbar"])
    a_check(p["temp_hi_k"] <= 40, "atmosphere T ceiling")
    return dict(irr=irr, irr_1over=int(round(1.0 / irr)),
                charon_ratio=round(ch, 3))


def ck_case10():
    """AM-9: primary density check with volumetric mean radius (all 10 <=1%);
    equatorial-sphere demo for giants with flattening-order assertion."""
    calc_mean, calc_eq = {}, {}
    for b in BODIES:
        m = MASS_1E24[b] * 1e24
        # primary: volumetric mean radius (per-body sheet, plan-v1b)
        r = MEAN_R_KM[b] * 1000.0
        rho = m / (4.0 / 3.0 * math.pi * r ** 3)
        dev = (rho - DENS_KGM3[b]) / float(DENS_KGM3[b])
        a_check(abs(dev) <= 0.01,
                "%s rho(mean r)=%.0f vs %d dev=%.2f%% (<=1%% AM-9)"
                % (b, rho, DENS_KGM3[b], dev * 100))
        calc_mean[b] = (round(rho), round(dev * 100, 2))
        # demo: equatorial sphere from table diameter (AM-9 contrast)
        r_eq = DIAM_KM[b] * 1000.0 / 2.0
        rho_eq = m / (4.0 / 3.0 * math.pi * r_eq ** 3)
        calc_eq[b] = (round(rho_eq),
                      round((rho_eq - DENS_KGM3[b]) / float(DENS_KGM3[b]) * 100, 1))
    # giants: table diameter == 2 x sheet equatorial radius (arithmetic, exact)
    for b in GIANTS4:
        a_check(abs(2 * EQ_R_KM[b] - DIAM_KM[b]) < 1,
                "%s 2*eq_r=%.0f != table diam %d" % (b, 2 * EQ_R_KM[b], DIAM_KM[b]))
    # giants: |equatorial-sphere dev| order matches flattening order (AM-9)
    flat_order = sorted(GIANTS4, key=lambda b: -ELLIPTICITY[b])
    dev_order = sorted(GIANTS4, key=lambda b: -abs(calc_eq[b][1]))
    a_check(flat_order == dev_order,
            "flattening order %s != equatorial-dev order %s"
            % (flat_order, dev_order))
    for b in GIANTS4:
        a_check(-10.0 < calc_eq[b][1] < -2.0,
                "%s equatorial-sphere dev %.1f%% outside 2-10%% low band"
                % (b, calc_eq[b][1]))
    # grouping gap (SRC-01 density row)
    tmin = min(DENS_KGM3[b] for b in ["mercury", "venus", "earth", "mars"])
    gmax = max(DENS_KGM3[b] for b in GIANTS4)
    a_check(tmin > gmax, "terrestrial min %d <= giant max %d" % (tmin, gmax))
    gap = [b for b in BODIES if gmax < DENS_KGM3[b] < tmin]
    a_check("pluto" in gap and "moon" in gap and len(gap) == 2,
            "gap should be exactly pluto+moon: %s" % gap)
    return dict(mean=calc_mean, eq=calc_eq, gap=gap, tmin=tmin, gmax=gmax,
                flat={b: ELLIPTICITY[b] for b in GIANTS4})


def ck_case11():
    """overview: distance-sorted + all four corner values present."""
    seq = [DIST_1E6[b] for b in PLANETS8]
    a_check(all(seq[i] < seq[i + 1] for i in range(7)), "sort broken")
    for b in PLANETS8:
        for row in (DIAM_KM, DIST_1E6, ORPPER_D, TEMP_C):
            a_check(row[b] is not None, "%s missing in a row" % b)
    return seq


def ck_all():
    res = {}
    res["case01"] = ck_case01()
    res["case02"] = ck_case02()
    res["case03"] = ck_case03()
    res["case04"] = ck_case04()
    res["case05"] = ck_case05()
    res["case06"] = ck_case06()
    res["case07"] = ck_case07()
    res["case08"] = ck_case08()
    res["case09"] = ck_case09()
    res["case10"] = ck_case10()
    res["case11"] = ck_case11()
    res["sign_source"] = ck_sign_source()
    res["xtable"] = ck_xtable()
    return res


if __name__ == "__main__":
    import json
    r = ck_all()
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    print("ALL B04 FACT CHECKS PASSED")
