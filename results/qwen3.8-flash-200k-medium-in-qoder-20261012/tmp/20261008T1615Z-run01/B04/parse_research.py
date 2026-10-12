"""B04 research layer: parse the fetched NASA catalogue table (2001-2100) into JSON,
derive the statistics every work uses, and cross-check two rows against the
independently fetched path pages (greatest-eclipse time, duration, width).

Run from the suite root. Inputs are the raw HTML already logged in requests.jsonl;
nothing here re-reads the network.
"""
import json, os, re, math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B04"
SRC = TMP / "sources"
RES = TMP / "research"
RES.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()

MONTHS = {m: i + 1 for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def text_of(fname):
    """HTML -> text, keeping anchor inner text and <pre> row order."""
    h = (SRC / fname).read_text(encoding="utf-8", errors="ignore")
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    import html as H
    return re.sub(r'[\s ]+', ' ', H.unescape(h))


def catalog_rows():
    """Rows are inside one <pre>. Split on the 5-digit catalogue number that starts each row."""
    h = (SRC / "nasa-21cen-catalog.html").read_text(encoding="utf-8", errors="ignore")
    pre = re.findall(r"(?s)<pre>(.*?)</pre>", h)
    body = max(pre, key=len)
    import html as H
    body = H.unescape(body)
    # anchor -> inner text only
    body = re.sub(r"(?s)<a[^>]*>(.*?)</a>", r"\1", body)
    body = re.sub(r"<[^>]+>", " ", body)
    starts = [m.start() for m in re.finditer(r"^\s*(\d{5})\s+(\d{4} [A-Z][a-z]{2} \d{2})\b",
                                             body, re.M)]
    rows = []
    for i, s in enumerate(starts):
        chunk = body[s:starts[i + 1] if i + 1 < len(starts) else len(body)]
        cells = " ".join(chunk.split())
        m = re.match(
            r"(\d{5}) (\d{4}) ([A-Z][a-z]{2}) (\d{2}) (\d{2}):(\d{2}):(\d{2}) "
            r"(-?\d+) (-?\d+) (\d+) ([TPAH]) (\S\S) ?(-?[\d.]+) ([\d.]+) "
            r"(\d{2})([NS]) (\d{2,3})([EW]) (\d+) (\d+|) (\d\d)m(\d\d)s(?:\.(\d))?",
            cells)
        if not m:
            rows.append({"raw": cells, "parsed": False})
            continue
        (num, y, mo, d, hh, mm, ss, dt, lun, saros, typ, qle, gamma, mag,
         lat, ns, lon, ew, alt, width, dur_m, dur_s, dur_t) = m.groups()
        rows.append({
            "parsed": True, "catalog_number": int(num),
            "date": "%s-%02d-%02d" % (y, MONTHS[mo], int(d)),
            "year": int(y), "month": MONTHS[mo], "day": int(d),
            "greatest_td": "%02d:%02d:%02d" % (int(hh), int(mm), int(ss)),
            "delta_t_s": int(dt), "lunation_number": int(lun), "saros": int(saros),
            "type": typ, "qle": qle, "gamma": float(gamma), "magnitude": float(mag),
            "lat": int(lat) * (1 if ns == "N" else -1), "lon": int(lon) * (1 if ew == "E" else -1),
            "sun_altitude_deg": int(alt),
            "path_width_km": int(width) if width else None,
            "central_duration_s": int(dur_m) * 60 + int(dur_s) + (int(dur_t) / 10 if dur_t else 0),
            "raw": cells,
        })
    return rows


def fact_constants():
    """Physical constants read literally from the fetched NASA fact sheets.
    Values are the printed numbers (comparison tables give Sun/Earth/Moon columns;
    we take the column named by the label context)."""
    def grab(fname, label, group=1, nth=0):
        t = text_of(fname)
        hits = list(re.finditer(re.escape(label) + r"[^\d\-]{0,40}([\d.,]+)", t))
        if not hits:
            return None
        v = hits[nth].group(1).replace(",", "").rstrip(".")
        try:
            return float(v)
        except ValueError:
            return None
    out = {
        "solar_volumetric_radius_km": grab("nasa-sun-fact.html", "Volumetric mean radius (km)"),
        "sun_mean_distance_10_6_km": grab("nasa-sun-fact.html", "Mean (10 6 km)"),
        "solar_apparent_diameter_arcsec": grab("nasa-sun-fact.html", "Apparent diameter"),
        "lunar_equatorial_radius_km": grab("nasa-moon-fact.html", "Equatorial radius (km)"),
        "lunar_semimajor_axis_10_6_km": grab("nasa-moon-fact.html", "Semimajor axis (10 6 km)"),
        "lunar_perigee_10_6_km": grab("nasa-moon-fact.html", "Perigee (10 6 km)"),
        "lunar_apogee_10_6_km": grab("nasa-moon-fact.html", "Apogee (10 6 km)"),
        "lunar_revolution_period_days": grab("nasa-moon-fact.html", "Revolution period (days)"),
        "lunar_synodic_period_days": grab("nasa-moon-fact.html", "Synodic period (days)"),
        "lunar_mean_orbital_velocity_kms": grab("nasa-moon-fact.html", "Mean orbital velocity (km/s)"),
        "lunar_apparent_diameter_arcsec": grab("nasa-moon-fact.html", "Apparent diameter"),
        "lunar_recession_cm_per_yr": grab("nasa-moon-fact.html", "Recession rate from Earth (cm/yr)"),
        "earth_equatorial_radius_km": grab("nasa-earth-fact.html", "Equatorial radius (km)"),
        "earth_sidereal_rotation_hours": grab("nasa-earth-fact.html", "Sidereal rotation period (hrs)"),
        "sun_earth_mean_distance_km": grab("nasa-sun-fact.html", "Mean (10 6 km)") * 1e6,
    }
    missing = [k for k, v in out.items() if v is None]
    assert not missing, "fact-sheet value missing: %s" % missing
    return out


def crosscheck(rows):
    """Validate parsed rows against the independently fetched 2024 / 2027 path pages."""
    checks = []
    for key, date, fields in [("nasa-path-2024", "2024-04-08", None),
                              ("nasa-path-2027", "2027-08-02", None)]:
        t = text_of(key + ".html")
        r = next(x for x in rows if x.get("date") == date)
        ut = re.search(r"Greatest Eclipse\s*:\s*Time\s*=\s*([\d:.]+)\s*UT", t)
        dur = re.search(r"Central Duration\s*=\s*(\d\d)m(\d\d\.\d)s", t)
        wid = re.search(r"Path Width\s*=\s*([\d.]+)\s*km", t)
        dtxt = ut.group(1) if ut else None
        # catalogue prints TD = UT + delta T
        if dtxt:
            h, mi, s = [int(float(x)) for x in dtxt.split(":")]
            td = (h * 3600 + mi * 60 + s + r["delta_t_s"]) % 86400
            td_str = "%02d:%02d:%02d" % (td // 3600, (td % 3600) // 60, td % 60)
        else:
            td_str = None
        checks.append({
            "date": date,
            "path_page_greatest_ut": dtxt,
            "catalog_greatest_td": r["greatest_td"],
            "delta_t_s": r["delta_t_s"],
            "ut_plus_deltat_equals_catalog_td": (td_str == r["greatest_td"]) if td_str else None,
            "path_page_central_duration_s":
                int(dur.group(1)) * 60 + float(dur.group(2)) if dur else None,
            "catalog_central_duration_s": r["central_duration_s"],
            "path_page_width_km": float(wid.group(1)) if wid else None,
            "catalog_width_km": r["path_width_km"],
        })
    return checks


def geometry(const):
    """Derived arithmetic from the fetched constants: apparent sizes, umbra cone length
    at perigee/apogee, and the shadow's ground speed. Nothing here is invented data."""
    rs, rm = const["solar_volumetric_radius_km"], const["lunar_equatorial_radius_km"]
    dsem = const["sun_earth_mean_distance_km"]
    dl, dp, da = (const["lunar_semimajor_axis_10_6_km"] * 1e6,
                  const["lunar_perigee_10_6_km"] * 1e6, const["lunar_apogee_10_6_km"] * 1e6)
    umbra = lambda d: d * rs and d * rm / (rs - rm)
    ang = lambda r, d: math.degrees(r / d) * 3600
    v_moon = const["lunar_mean_orbital_velocity_kms"]
    v_surf = 2 * math.pi * const["earth_equatorial_radius_km"] / (
        const["earth_sidereal_rotation_hours"] * 3600)
    return {
        "umbral_length_at_mean_km": round(dl * rm / (rs - rm)),
        "umbral_length_at_perigee_km": round(dp * rm / (rs - rm)),
        "umbral_length_at_apogee_km": round(da * rm / (rs - rm)),
        "solar_apparent_diameter_arcsec_computed": round(ang(rs, dsem)),
        "lunar_apparent_diameter_arcsec_computed": round(ang(rm, dl)),
        "sun_moon_apparent_ratio_mean": round(ang(rs, dsem) / ang(rm, dl), 4),
        "moon_orbital_speed_kms": v_moon,
        "equatorial_surface_speed_kms": round(v_surf, 4),
        "shadow_ground_speed_min_kms": round(v_moon - v_surf, 3),
        "shadow_ground_speed_min_kmph": round((v_moon - v_surf) * 3600),
        "shadow_ground_speed_west_to_east_kmph": round((v_moon + v_surf) * 3600),
        "saros_days": round(223 * const["lunar_synodic_period_days"], 4),
        "saros_definition": "223 synodic months = 6585.32 days = 18 years + 11 days + 8 hours "
                            "(the 8 hours shift the next eclipse ~120 degrees westward)",
        "eclipse_year_note": "the Sun returns to the same lunar node every 346.62 days "
                             "(node-to-node year), shorter than the calendar year",
        "recession_effect_note": "Moon recedes 3.8 cm/yr, so the umbral cone shortens 1.36 km/century",
    }


rows = catalog_rows()
good = [r for r in rows if r["parsed"]]
bad = [r for r in rows if not r["parsed"]]
const = fact_constants()
geo = geometry(const)
checks = crosscheck(good)

types = {}
for r in good:
    types[r["type"]] = types.get(r["type"], 0) + 1
decades = {}
for r in good:
    k = "%ds" % (r["year"] // 10 * 10)
    decades.setdefault(k, {"total": 0})
    decades[k][r["type"]] = decades[k].get(r["type"], 0) + 1
    decades[k]["total"] += 1
cen = [r for r in good if r["type"] == "T"]
ann = [r for r in good if r["type"] == "A"]
hyb = [r for r in good if r["type"] == "H"]
china = [r for r in good if 18 <= r["lat"] <= 54 and 73 <= r["lon"] <= 135]
dt_range = [min(r["delta_t_s"] for r in good), max(r["delta_t_s"] for r in good)]
dur_hist = {}
for r in cen:
    dur_hist.setdefault(r["central_duration_s"] // 60, 0)
    dur_hist[r["central_duration_s"] // 60] += 1

stats = {
    "generated_at": NOW, "path_base": "suite_root",
    "source": "tmp/%s/B04/sources/nasa-21cen-catalog.html" % RID,
    "rows_found": len(rows), "rows_parsed": len(good), "rows_unparsed": len(bad),
    "unparsed_raw": [b["raw"][:90] for b in bad],
    "count_by_type": types,
    "count_by_decade": decades,
    "longest_total": sorted(cen, key=lambda r: -r["central_duration_s"])[:4],
    "shortest_total": sorted(cen, key=lambda r: r["central_duration_s"])[:4],
    "longest_annular": sorted(ann, key=lambda r: -r["central_duration_s"])[:4],
    "hybrid_list": hyb,
    "saros_series_count": len({r["saros"] for r in good}),
    "saros_top": sorted(((s, sum(1 for r in good if r["saros"] == s))
                         for s in {r["saros"] for r in good}), key=lambda x: -x[1])[:6],
    "greatest_in_china_bbox": china,
    "delta_t_range_s": dt_range,
    "total_duration_hist_min": dict(sorted(dur_hist.items())),
    "max_path_width": max(good, key=lambda r: r["path_width_km"] or 0),
    "widest_partial_none": sum(1 for r in good if r["path_width_km"] is None),
    "constants": const, "geometry": geo, "crosscheck": checks,
}
json.dump({"rows": good, "unparsed": bad}, open(RES / "catalog.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(stats, open(RES / "stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rows %d parsed %d unparsed %d | types %s | saros series %d | china-bbox %d" % (
    len(rows), len(good), len(bad), types, stats["saros_series_count"], len(china)))
print("constants:", const)
print("geometry:", json.dumps(geo, ensure_ascii=False))
for c in checks:
    print("crosscheck", c["date"], "TD==UT+dT:", c["ut_plus_deltat_equals_catalog_td"],
          "dur", c["path_page_central_duration_s"], "vs", c["catalog_central_duration_s"],
          "| width", c["path_page_width_km"], "vs", c["catalog_width_km"])
print("longest total:", [(r["date"], r["central_duration_s"]) for r in stats["longest_total"]])
print("unparsed raw:", stats["unparsed_raw"][:5])
