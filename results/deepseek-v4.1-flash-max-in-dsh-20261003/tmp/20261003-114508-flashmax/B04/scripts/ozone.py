"""ozone.py - the real dataset behind B04, transcribed from NASA Ozone Watch.

Source: NASA Ozone Watch, "Annual Records" (Antarctic),
https://ozonewatch.gsfc.nasa.gov/meteorology/annual_data.html, accessed 2026-10-03,
HTTP 200. Credited to "NASA Ozone Watch". The page states there are no data for 1995.

  max_area  = maximum DAILY ozone-hole area that year, million km2, and its date
  min_ozone = minimum DAILY Southern Hemisphere column ozone, Dobson Units, and its date
  mean_area = mean hole area over 07 September - 13 October, million km2
  mean_min  = mean minimum Southern Hemisphere ozone over 21 September - 16 October, DU

Everything derived in this module (ranks, means, deltas, the pre/post-2000 split) is
computed from these arrays; no figure is typed in twice.
"""
from __future__ import annotations

# (year, date of max, max daily area million km2, date of min, min daily ozone DU)
MAX_DAILY = [
    (1979, "17 Sep", 1.1, "17 Sep", 194), (1980, "21 Sep", 3.3, "16 Oct", 192),
    (1981, "10 Oct", 3.1, "10 Oct", 195), (1982, "02 Oct", 10.8, "02 Nov", 170),
    (1983, "17 Oct", 12.2, "06 Oct", 154), (1984, "24 Sep", 14.7, "03 Oct", 144),
    (1985, "03 Oct", 18.8, "24 Oct", 124), (1986, "06 Oct", 14.4, "06 Oct", 140),
    (1987, "29 Sep", 22.5, "05 Oct", 109), (1988, "20 Sep", 13.8, "30 Sep", 162),
    (1989, "03 Oct", 21.7, "07 Oct", 108), (1990, "19 Sep", 21.1, "05 Oct", 111),
    (1991, "04 Oct", 22.6, "06 Oct", 94), (1992, "27 Sep", 24.9, "11 Oct", 105),
    (1993, "19 Sep", 25.8, "25 Sep", 104), (1994, "30 Sep", 25.2, "30 Sep", 73),
    (1996, "07 Sep", 26.9, "05 Oct", 103), (1997, "27 Sep", 25.1, "24 Sep", 99),
    (1998, "19 Sep", 27.9, "06 Oct", 86), (1999, "15 Sep", 25.8, "29 Sep", 97),
    (2000, "09 Sep", 29.9, "29 Sep", 89), (2001, "17 Sep", 26.5, "22 Sep", 91),
    (2002, "19 Sep", 21.9, "20 Sep", 131), (2003, "24 Sep", 28.4, "26 Sep", 91),
    (2004, "22 Sep", 22.8, "04 Oct", 102), (2005, "11 Sep", 27.2, "30 Sep", 103),
    (2006, "24 Sep", 29.6, "08 Oct", 84), (2007, "13 Sep", 25.2, "24 Sep", 108),
    (2008, "12 Sep", 27.0, "04 Oct", 101), (2009, "17 Sep", 24.4, "26 Sep", 97),
    (2010, "25 Sep", 22.6, "01 Oct", 119), (2011, "12 Sep", 26.1, "08 Oct", 95),
    (2012, "22 Sep", 21.1, "01 Oct", 124), (2013, "16 Sep", 24.0, "29 Sep", 116),
    (2014, "11 Sep", 24.1, "30 Sep", 114), (2015, "02 Oct", 28.2, "04 Oct", 101),
    (2016, "28 Sep", 22.8, "01 Oct", 111), (2017, "11 Sep", 19.6, "09 Oct", 131),
    (2018, "20 Sep", 24.8, "11 Oct", 102), (2019, "08 Sep", 16.4, "02 Sep", 142),
    (2020, "20 Sep", 24.8, "06 Oct", 94), (2021, "07 Oct", 24.8, "07 Oct", 92),
    (2022, "05 Oct", 26.5, "01 Oct", 97), (2023, "21 Sep", 26.0, "03 Oct", 99),
    (2024, "28 Sep", 22.4, "05 Oct", 107), (2025, "09 Sep", 22.9, "25 Sep", 127),
]

# (year, mean area 07Sep-13Oct million km2, mean min ozone 21Sep-16Oct DU)
SEASON_MEAN = [
    (1979, 0.1, 225.0), (1980, 1.4, 203.0), (1981, 0.6, 209.5), (1982, 4.8, 185.0),
    (1983, 7.9, 172.9), (1984, 10.1, 163.6), (1985, 14.2, 146.5), (1986, 11.3, 157.8),
    (1987, 19.3, 123.0), (1988, 10.0, 171.0), (1989, 18.7, 127.0), (1990, 19.2, 124.2),
    (1991, 18.8, 119.0), (1992, 22.3, 114.3), (1993, 24.2, 112.6), (1994, 23.6, 92.3),
    (1996, 22.8, 108.8), (1997, 22.1, 108.8), (1998, 25.9, 98.8), (1999, 23.3, 102.9),
    (2000, 24.8, 98.7), (2001, 25.0, 100.9), (2002, 12.0, 157.4), (2003, 25.8, 108.7),
    (2004, 19.5, 123.5), (2005, 24.4, 113.8), (2006, 26.6, 98.4), (2007, 22.0, 116.2),
    (2008, 25.2, 114.0), (2009, 22.0, 107.9), (2010, 19.4, 128.5), (2011, 24.7, 106.5),
    (2012, 17.8, 139.3), (2013, 21.0, 132.7), (2014, 20.9, 128.6), (2015, 25.6, 117.2),
    (2016, 20.7, 123.2), (2017, 17.4, 141.8), (2018, 22.9, 111.8), (2019, 9.3, 167.0),
    (2020, 23.5, 102.6), (2021, 23.3, 103.3), (2022, 23.2, 112.5), (2023, 23.1, 115.2),
    (2024, 19.6, 121.0), (2025, 18.7, 138.3),
]

YEARS = [r[0] for r in MAX_DAILY]
AREA = {r[0]: r[2] for r in MAX_DAILY}
AREA_DATE = {r[0]: r[1] for r in MAX_DAILY}
MINO3 = {r[0]: r[4] for r in MAX_DAILY}
MINO3_DATE = {r[0]: r[3] for r in MAX_DAILY}
MEAN_AREA = {r[0]: r[1] for r in SEASON_MEAN}
MEAN_MIN = {r[0]: r[2] for r in SEASON_MEAN}

# ---- treaty events (UNEP Ozone Secretariat; see research/sources-draft.json S4/S6)
TREATY = [
    (1985, "Vienna Convention", "framework, no controls"),
    (1987, "Montreal Protocol", "CFCs and halons capped"),
    (1990, "London Amendment", "CFCs phased out by 2000"),
    (1992, "Copenhagen Amendment", "HCFCs, methyl bromide added"),
    (1997, "Montreal Amendment", "compliance procedure"),
    (1999, "Beijing Amendment", "bromochloromethane, HCFC production"),
    (2016, "Kigali Amendment", "18 HFCs phased down"),
]

# ---- published trend statements (WMO/UNEP 2022, S5) - not computed here
TCO_TRENDS = [  # (band, % per decade, 2-sigma, period)
    ("Near-global 60S-60N", 0.3, 0.3, "1996-2020"),
    ("SH mid-latitudes 35S-60S", 0.8, 0.7, "1996-2020"),
    ("NH mid-latitudes 35N-60N", 0.0, 0.7, "1996-2020"),
    ("Tropics 20S-20N", 0.2, 0.3, "1996-2020"),
    ("Upper stratosphere, mid-lat", 1.85, 0.35, "2000-2020"),
    ("Upper stratosphere, tropics", 1.35, 0.25, "2000-2020"),
    ("Lower stratosphere, tropics", -1.5, 1.0, "2000-2020"),
]
GAP_VS_1964_1980 = [("Near-global", -2), ("NH mid-latitudes", -4),
                    ("SH mid-latitudes", -5), ("Tropics", -1)]
RETURN_YEARS = [("Antarctic spring", 2065, "about 2065; possibly about 2050 under low "
                 "climate-mitigation scenarios"),
                ("Arctic spring", 2045, "about 2045"),
                ("NH mid-latitudes", 2035, "about 2035"),
                ("Near-global annual", 2040, "about 2040")]
CFC11_DELAY = {"polar_years": 3, "global_years": 1}


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def rolling(pairs, win=5):
    """Centred-ish trailing mean over the last `win` points (points, not years)."""
    out = []
    for i in range(len(pairs)):
        if i + 1 < win:
            out.append(None)
            continue
        out.append(mean(v for _, v in pairs[i + 1 - win:i + 1]))
    return out


def rank_desc(values):
    order = sorted(values.items(), key=lambda kv: -kv[1])
    return {y: i + 1 for i, (y, _) in enumerate(order)}


AREA_RANK = rank_desc(AREA)
MEAN_RANK = rank_desc(MEAN_AREA)
TOP5_AREA = sorted(AREA.items(), key=lambda kv: -kv[1])[:5]
BOTTOM5_AREA = sorted(AREA.items(), key=lambda kv: kv[1])[:5]
TOP5_MEAN = sorted(MEAN_AREA.items(), key=lambda kv: -kv[1])[:5]
EARLY = [AREA[y] for y in YEARS if y <= 1994]
LATE = [AREA[y] for y in YEARS if y >= 2001]
MEAN_1980S = mean(AREA[y] for y in YEARS if 1979 <= y <= 1989)
MEAN_1990S = mean(AREA[y] for y in YEARS if 1990 <= y <= 1999)
MEAN_2000S = mean(AREA[y] for y in YEARS if 2000 <= y <= 2009)
MEAN_2010S = mean(AREA[y] for y in YEARS if 2010 <= y <= 2019)
MEAN_2020S = mean(AREA[y] for y in YEARS if 2020 <= y <= 2025)
FIRST_20 = next(y for y in YEARS if AREA[y] >= 20)
FIRST_25 = next(y for y in YEARS if AREA[y] >= 25)
PEAK_YEAR = max(AREA, key=lambda y: AREA[y])
SMALLEST_2019 = AREA[2019]

if __name__ == "__main__":
    print("years", len(YEARS), YEARS[0], "-", YEARS[-1])
    print("peak", PEAK_YEAR, AREA[PEAK_YEAR])
    print("first >=20 Mm2:", FIRST_20, " first >=25:", FIRST_25)
    print("decade means", round(MEAN_1980S, 2), round(MEAN_1990S, 2),
          round(MEAN_2000S, 2), round(MEAN_2010S, 2), round(MEAN_2020S, 2))
    print("top5 area", TOP5_AREA)
    print("smallest5 area", BOTTOM5_AREA)
    print("top5 season mean", TOP5_MEAN)
    print("2019 area", SMALLEST_2019, "2025 area", AREA[2025],
          "min ozone 2025", MINO3[2025])
