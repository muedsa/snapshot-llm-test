"""B04 research layer (v2): parse the fetched NASA catalogue table (2001-2100) into JSON,
derive every statistic the works use, and cross-check two rows against the
independently fetched path pages (greatest-eclipse time, duration, width, delta T).

Run from the suite root. Inputs are the raw HTML already logged in requests.jsonl;
this script does not touch the network.
"""
import json, os, re, math, html as H
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B04"
SRC = TMP / "sources"
RES = TMP / "research"
RES.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()

MONTHS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def text_of(fname):
    h = (SRC / fname).read_text(encoding="utf-8", errors="ignore")
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return re.sub(r"[\s\xa0]+", " ", H.unescape(h))


def strip_tags(s):
    s = re.sub(r"(?s)<a[^>]*>(.*?)</a>", r"\1", s)
    return re.sub(r"(?s)<[^>]+>", " ", H.unescape(s))


def catalog_rows():
    """Positional token parse of the catalogue <pre> table.

    Columns (fixed order): number, date, TD of greatest eclipse, delta-T, lunation,
    Saros, type (a trailing 'n' marks a non-central eclipse), quick-look flag, gamma,
    magnitude, lat, long, sun altitude, path width, central duration.
    Partial rows simply stop after the altitude; non-central rows print '-' for width.
    """
    raw = (SRC / "nasa-21cen-catalog.html").read_text(encoding="utf-8", errors="ignore")
    body = chr(10).join(re.findall(r"(?s)<pre>(.*?)</pre>", raw))
    body = strip_tags(body)
    starts = [m.start() for m in re.finditer(
        r"(\d{5})\s+(\d{4} [A-Z][a-z]{2} \d{2})\s+\d{2}:\d{2}:\d{2}", body)]
    num = lambda s: None if s in ("-", "") else float(s)
    rows = []
    for i, s in enumerate(starts):
        tok = body[s:starts[i + 1] if i + 1 < len(starts) else len(body)].split()[:17]
        try:
            y, mo, d = int(tok[1]), MONTHS[tok[2]], int(tok[3])
            typ, nflag = tok[8][0], tok[8][1:]
            la, lo = re.match(r"(\d+)([NS])", tok[12]), re.match(r"(\d+)([EW])", tok[13])
            width = dur = None
            if len(tok) > 15 and re.fullmatch(r"\d+", tok[15]):
                width = float(tok[15])
            if len(tok) > 16 and re.fullmatch(r"\d+m[\d.]+s", tok[16]):
                mm, ss = re.match(r"(\d+)m([\d.]+)s", tok[16]).groups()
                dur = int(mm) * 60 + float(ss)
            row = {
                "parsed": True, "catalog_number": int(tok[0]),
                "date": "%s-%02d-%02d" % (y, mo, d), "year": y, "month": mo, "day": d,
                "greatest_td": tok[4], "delta_t_catalog_s": int(tok[5]),
                "lunation": int(tok[6]), "saros": int(tok[7]),
                "type": typ, "non_central_flag": nflag, "qle": tok[9],
                "gamma": float(tok[10]), "magnitude": float(tok[11]),
                "lat": int(la.group(1)) * (1 if la.group(2) == "N" else -1),
                "lon": int(lo.group(1)) * (1 if lo.group(2) == "E" else -1),
                "sun_altitude_deg": int(tok[14]),
                "path_width_km": int(width) if width is not None else None,
                "central_duration_s": dur, "raw": " ".join(tok),
            }
        except Exception as e:
            rows.append({"parsed": False, "raw": " ".join(tok), "error": repr(e)})
            continue
        rows.append(row)
    return rows


def fact_constants():
    """Physical numbers read literally from the fetched NASA fact sheets."""
    def grab(fname, label, nth=0):
        t = text_of(fname)
        hits = list(re.finditer(re.escape(label) + r"[^\d]{0,40}([\d.,]+)", t))
        if not hits:
            return None
        try:
            return float(hits[nth].group(1).replace(",", "").rstrip("."))
        except ValueError:
            return None
    out = {
        "solar_volumetric_radius_km": grab("nasa-sun-fact.html", "Volumetric mean radius (km)"),
        "sun_mean_distance_from_earth_10_6_km": grab("nasa-sun-fact.html", "Mean (10 6 km)"),
        "sun_min_distance_10_6_km": grab("nasa-sun-fact.html", "Minimum (10 6 km)"),
        "sun_max_distance_10_6_km": grab("nasa-sun-fact.html", "Maximum (10 6 km)"),
        "lunar_equatorial_radius_km": grab("nasa-moon-fact.html", "Equatorial radius (km)"),
        "lunar_semimajor_axis_10_6_km": grab("nasa-moon-fact.html", "Semimajor axis (10 6 km)"),
        "lunar_perigee_10_6_km": grab("nasa-moon-fact.html", "Perigee (10 6 km)"),
        "lunar_apogee_10_6_km": grab("nasa-moon-fact.html", "Apogee (10 6 km)"),
        "lunar_revolution_period_days": grab("nasa-moon-fact.html", "Revolution period (days)"),
        "lunar_synodic_period_days": grab("nasa-moon-fact.html", "Synodic period (days)"),
        "lunar_mean_orbital_velocity_kms": grab("nasa-moon-fact.html", "Mean orbital velocity (km/s)"),
        "lunar_apparent_diameter_arcsec": grab("nasa-moon-fact.html", "Apparent diameter"),
        "lunar_distance_at_opposition_km": grab("nasa-moon-fact.html", "Distance from Earth (equator, km)"),
        "lunar_recession_cm_per_yr": grab("nasa-moon-fact.html", "Recession rate from Earth (cm/yr)"),
        "lunar_orbit_inclination_ecliptic_deg": grab("nasa-moon-fact.html", "Inclination to ecliptic (deg)"),
        "earth_equatorial_radius_km": grab("nasa-earth-fact.html", "Equatorial radius (km)"),
        "earth_sidereal_rotation_hours": grab("nasa-earth-fact.html", "Sidereal rotation period (hrs)"),
    }
    missing = [k for k, v in out.items() if v is None]
    assert not missing, "fact-sheet value missing: %s" % missing
    out["sun_mean_distance_km"] = out["sun_mean_distance_from_earth_10_6_km"] * 1e6
    return out


def arcsec_diameter(radius_km, distance_km):
    return 2 * math.degrees(math.atan(radius_km / distance_km)) * 3600


def geometry(const):
    rs, rm = const["solar_volumetric_radius_km"], const["lunar_equatorial_radius_km"]
    dsun = const["sun_mean_distance_km"]
    dl = const["lunar_semimajor_axis_10_6_km"] * 1e6
    dp, da = const["lunar_perigee_10_6_km"] * 1e6, const["lunar_apogee_10_6_km"] * 1e6
    umbra = lambda sun_moon_dist: rm * sun_moon_dist / (rs - rm)
    L_mean = umbra(dsun)
    v_surf = 2 * math.pi * const["earth_equatorial_radius_km"] / (
        const["earth_sidereal_rotation_hours"] * 3600)
    v_moon = const["lunar_mean_orbital_velocity_kms"]
    return {
        "solar_apparent_diameter_arcsec_computed": round(arcsec_diameter(rs, dsun)),
        "lunar_apparent_diameter_arcsec_computed_mean": round(arcsec_diameter(rm, dl)),
        "lunar_apparent_diameter_arcsec_computed_opposition": round(
            arcsec_diameter(rm, const["lunar_distance_at_opposition_km"])),
        "fact_sheet_lunar_apparent_diameter_arcsec": const["lunar_apparent_diameter_arcsec"],
        "sun_moon_apparent_diameter_ratio_mean": round(
            arcsec_diameter(rs, dsun) / arcsec_diameter(rm, dl), 4),
        "umbral_length_from_moon_mean_km": round(L_mean),
        "moon_distance_mean_km": round(dl),
        "umbra_margin_at_perigee_km": round(L_mean - dp),
        "umbra_margin_at_mean_km": round(L_mean - dl),
        "umbra_margin_at_apogee_km": round(L_mean - da),
        "shadow_ground_speed_kms_equator_eastward": round(v_moon - v_surf, 4),
        "shadow_ground_speed_kmph_equator_eastward": round((v_moon - v_surf) * 3600),
        "shadow_ground_speed_kmph_equator_westward": round((v_moon + v_surf) * 3600),
        "surface_rotation_speed_kms": round(v_surf, 4),
        "moon_orbital_speed_kms": v_moon,
        "saros_days_from_synodic": round(223 * const["lunar_synodic_period_days"], 4),
        "saros_canonical_days": 6585.3211,
        "eclipse_year_days": 346.62,
        "recession_km_per_century": round(const["lunar_recession_cm_per_yr"] * 100 / 100.0, 3),
    }


def crosscheck(rows):
    """Compare two catalogue rows against the separately fetched path pages.

    The path pages print the instant in UT plus their own delta-T; the catalogue prints
    TD plus a delta-T column taken from a different polynomial. Both are recorded so the
    discrepancy is visible rather than smoothed away.
    """
    checks = []
    for key, date in [("nasa-path-2024", "2024-04-08"), ("nasa-path-2027", "2027-08-02")]:
        t = text_of(key + ".html")
        r = next(x for x in rows if x.get("date") == date)
        ut = re.search(r"Greatest Eclipse\s*:\s*Time\s*=\s*([\d:.]+)\s*UT", t)
        pdt = re.search(r"ΔT\s*=\s*([\d.]+)\s*seconds", t)
        dur = re.search(r"Central Duration\s*=\s*(\d\d)m(\d\d(?:\.\d)?)s", t)
        wid = re.search(r"Path Width\s*=\s*([\d.]+)\s*km", t)
        pos = re.search(r"Lat\s*=\s*(\d+)°([\d.]+)'([NS])\s*Long\s*=\s*(\d+)°([\d.]+)'([EW])", t)
        alt = re.search(r"Sun Altitude\s*=\s*([\d.]+)°", t)
        secs = None
        if ut:
            h, mi, s = ut.group(1).split(":")
            secs = int(h) * 3600 + int(mi) * 60 + float(s)
        fdt = float(pdt.group(1)) if pdt else None

        def to_td(offset):
            if secs is None or offset is None:
                return None
            v = secs + offset
            return "%02d:%02d:%02d" % (int(v // 3600) % 24, int(v % 3600 // 60), int(round(v % 60)))
        pdur = float(dur.group(1)) * 60 + float(dur.group(2)) if dur else None
        checks.append({
            "date": date, "source_path_page": key,
            "path_page_greatest_ut": ut.group(1) if ut else None,
            "path_page_delta_t_s": fdt, "catalog_delta_t_s": r["delta_t_catalog_s"],
            "catalog_delta_t_minus_path_delta_t_s": r["delta_t_catalog_s"] - fdt if fdt else None,
            "catalog_greatest_td": r["greatest_td"],
            "ut_plus_path_deltat_rounded": to_td(fdt),
            "td_reproduced_with_path_deltat": to_td(fdt) == r["greatest_td"],
            "ut_plus_catalog_deltat": to_td(r["delta_t_catalog_s"]),
            "path_page_central_duration_s": pdur,
            "catalog_central_duration_s": r["central_duration_s"],
            "duration_agrees_within_1_5s": None if pdur is None else abs(pdur - r["central_duration_s"]) <= 1.5,
            "path_page_width_km": float(wid.group(1)) if wid else None,
            "catalog_width_km": r["path_width_km"],
            "path_page_position_deg": (int(pos.group(1)) * (1 if pos.group(3) == "N" else -1),
                                       int(pos.group(4)) * (1 if pos.group(6) == "E" else -1)) if pos else None,
            "catalog_position_deg": (r["lat"], r["lon"]),
            "path_page_sun_altitude": float(alt.group(1)) if alt else None,
            "catalog_sun_altitude": r["sun_altitude_deg"],
            "catalog_saros": r["saros"], "catalog_gamma": r["gamma"],
            "catalog_magnitude": r["magnitude"], "catalog_lunation": r["lunation"],
        })
    return checks


rows = catalog_rows()
good = [r for r in rows if r["parsed"]]
bad = [r for r in rows if not r["parsed"]]
const = fact_constants()
geo = geometry(const)
checks = crosscheck(good)

types = Counter(r["type"] for r in good)
decades = {}
for r in good:
    k = "%d0s" % (r["year"] // 10)
    decades.setdefault(k, Counter())[r["type"]] += 1
cen = [r for r in good if r["type"] == "T" and r["central_duration_s"]]
ann = [r for r in good if r["type"] == "A" and r["central_duration_s"]]
hyb = [r for r in good if r["type"] == "H"]
par = [r for r in good if r["type"] == "P"]
band = [r for r in good if 73 <= r["lon"] <= 135]
band_th = [r for r in band if r["type"] in ("T", "H")]

sar = {}
for r in sorted(good, key=lambda x: x["date"]):
    sar.setdefault(r["saros"], []).append(r["date"])
spans = []
for s, ds in sar.items():
    for a, b in zip(ds, ds[1:]):
        ya, ma, x = map(int, a.split("-"))
        yb, mb, z = map(int, b.split("-"))
        spans.append((datetime(yb, mb, z) - datetime(ya, ma, x)).days)

stats = {
    "generated_at": NOW, "path_base": "suite_root",
    "catalogue_source": "tmp/%s/B04/sources/nasa-21cen-catalog.html" % RID,
    "rows_found": len(rows), "rows_parsed": len(good), "rows_unparsed": len(bad),
    "unparsed_raw": [b["raw"][:140] for b in bad],
    "count_by_type": dict(types),
    "count_by_decade": {k: dict(v) for k, v in sorted(decades.items())},
    "longest_total": [(r["date"], r["central_duration_s"], r["path_width_km"], r["saros"], r["lat"], r["lon"])
                      for r in sorted(cen, key=lambda r: -r["central_duration_s"])[:6]],
    "shortest_total": [(r["date"], r["central_duration_s"], r["path_width_km"])
                       for r in sorted(cen, key=lambda r: r["central_duration_s"])[:6]],
    "longest_annular": [(r["date"], r["central_duration_s"], r["path_width_km"], r["saros"])
                        for r in sorted(ann, key=lambda r: -r["central_duration_s"])[:6]],
    "hybrid_dates": [r["date"] for r in hyb],
    "partial_rows_without_width": sum(1 for r in par if r["path_width_km"] is None),
    "saros_series_count": len(sar),
    "saros_most_members": sorted(((s, len(v)) for s, v in sar.items()), key=lambda x: -x[1])[:6],
    "saros_step_observed_days": Counter(spans).most_common(4),
    "saros_members_per_series_hist": dict(sorted(Counter(len(v) for v in sar.values()).items())),
    "greatest_in_china_longitude_band": [(r["date"], r["type"], r["lat"], r["lon"], r["central_duration_s"])
                                         for r in band],
    "total_or_hybrid_in_china_band": [(r["date"], r["type"], r["lat"], r["lon"],
                                       r["central_duration_s"], r["path_width_km"]) for r in band_th],
    "delta_t_catalog_range_s": [min(r["delta_t_catalog_s"] for r in good),
                                max(r["delta_t_catalog_s"] for r in good)],
    "total_duration_hist_min": dict(sorted(Counter(int(r["central_duration_s"]) // 60 for r in cen).items())),
    "widest_path": [r["date"], r["path_width_km"], r["type"]],
    "gamma_extremes": [min(good, key=lambda r: r["gamma"])["date"], max(good, key=lambda r: r["gamma"])["date"]],
    "constants": const, "geometry": geo, "crosscheck": checks,
}
stats["widest_path"] = [max(good, key=lambda r: r["path_width_km"] or 0)["date"],
                        max(r["path_width_km"] or 0 for r in good),
                        max(good, key=lambda r: r["path_width_km"] or 0)["type"]]
stats["narrowest_central_path"] = [min((r for r in good if r["path_width_km"]), key=lambda r: r["path_width_km"])["date"],
                                   min(r["path_width_km"] for r in good if r["path_width_km"])]

json.dump({"rows": good, "unparsed": bad}, open(RES / "catalog.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(stats, open(RES / "stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rows found %d | parsed %d | unparsed %d" % (len(rows), len(good), len(bad)))
print("types", dict(types), "| series", stats["saros_series_count"], "| band", len(band),
      "| band T/H", len(band_th), "| dt range", stats["delta_t_catalog_range_s"])
print("saros step", stats["saros_step_observed_days"], "| members hist", stats["saros_members_per_series_hist"])
print("longest total", stats["longest_total"][:3])
print("longest annular", stats["longest_annular"][:3])
print("hybrids", stats["hybrid_dates"])
print("widest", stats["widest_path"], "narrowest", stats["narrowest_central_path"])
print("geometry", json.dumps(geo, ensure_ascii=False))
for c in checks:
    print("CHECK", c["date"], "td_reproduced", c["td_reproduced_with_path_deltat"], "dur", c["path_page_central_duration_s"],
          c["catalog_central_duration_s"], c["duration_agrees_within_1_5s"],
          "width", c["path_page_width_km"], c["catalog_width_km"],
          "dT", c["path_page_delta_t_s"], c["catalog_delta_t_s"],
          "pos", c["path_page_position_deg"], c["catalog_position_deg"],
          "alt", c["path_page_sun_altitude"], c["catalog_sun_altitude"])
print("unparsed sample", [b[:80] for b in stats["unparsed_raw"][:4]])
