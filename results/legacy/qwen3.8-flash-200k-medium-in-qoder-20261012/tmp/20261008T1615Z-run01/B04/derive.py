"""B04 第二层推算：把特辑正文要用的派生量集中算一次，写 research/derived.json。

只做两类事：
  1) 从已解析的 224 行账本再聚合（逐年食数、按十年×类型、极值日期）；
  2) 从 NASA 数据表常数推出几何量（本影长度随日地距离的变化、触地门槛、地表余量）。
每个数字都带 formula/inputs 字段，方便逐件复核与写进图注。
"""
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B04"
RES = TMP / "research"

stats = json.load(open(RES / "stats.json", encoding="utf-8"))
rows = json.load(open(RES / "catalog.json", encoding="utf-8"))["rows"]
C = stats["constants"]
G = stats["geometry"]

RS = C["solar_volumetric_radius_km"]
RM = C["lunar_equatorial_radius_km"]
RE = C["earth_equatorial_radius_km"]
D_SUN = {"mean": C["sun_mean_distance_km"],
         "min": C["sun_min_distance_10_6_km"] * 1e6,
         "max": C["sun_max_distance_10_6_km"] * 1e6}
D_MOON = {"perigee": C["lunar_perigee_10_6_km"] * 1e6,
          "mean": C["lunar_semimajor_axis_10_6_km"] * 1e6,
          "apogee": C["lunar_apogee_10_6_km"] * 1e6}

out = {"generated_at": datetime.now(timezone.utc).isoformat(),
       "path_base": "suite_root",
       "inputs_from": ["research/stats.json", "research/catalog.json"]}


def umbra_len(d_sun):
    return RM * d_sun / (RS - RM)


# ---------- 1. 本影长度与"够不够得着地面" ----------
umbral = {}
for k, d in D_SUN.items():
    L = umbra_len(d)
    umbral[k] = {"d_sun_km": d, "umbral_length_km": round(L),
                 "touch_threshold_moon_dist_km": round(L + RE)}
out["umbral_length_vs_sun_distance"] = umbral
out["umbral_formula"] = "L = r_moon * d_sun / (r_sun - r_moon)；门槛 = L + r_earth（月心到地心距离）"
out["umbral_half_angle_deg"] = round(
    math.degrees(math.atan((RS - RM) / D_SUN["mean"])), 4)

margins = {}
for k, dm in D_MOON.items():
    L = umbra_len(D_SUN["mean"])
    margins[k] = {"moon_dist_km": dm,
                  "margin_to_surface_km": round(L + RE - dm),
                  "reaches_ground": (L + RE - dm) > 0}
out["apex_margin_at_mean_sun"] = margins

# ---------- 2. 逐年食数（自己数，与页面正文对照） ----------
per_year = {}
for r in rows:
    per_year[r["year"]] = per_year.get(r["year"], 0) + 1
dist = {}
for y, n in per_year.items():
    dist[n] = dist.get(n, 0) + 1
out["years_by_eclipse_count"] = {str(k): v for k, v in sorted(dist.items())}
out["years_counted"] = len(per_year)
out["page_claim_years_by_eclipse_count"] = {"2": 82, "3": 12, "4": 6}
out["page_claim_source"] = "nasa-21cen-catalog.html 正文 'Number of Years with ... Eclipses'"
out["years_check_total_rows"] = sum(k * v for k, v in dist.items())

# ---------- 3. 按十年×类型（含 2100 年单独一行） ----------
dec_of = lambda y: "2100s" if y == 2100 else "%ds" % (y // 10 * 10)
by_dec = {}
for r in rows:
    by_dec.setdefault(dec_of(r["year"]), {}).setdefault(r["type"], 0)
    by_dec[dec_of(r["year"])][r["type"]] += 1
out["by_decade"] = by_dec
out["by_decade_source"] = "由 catalog.json 224 行自行聚合"

# ---------- 4. 中心线最长 / 环食最长 / 最宽路径的月份分布 ----------
def top(key, n, fields, types=None, shortest=False):
    xs = [r for r in rows if r.get(key) and (types is None or r["type"] in types)]
    xs.sort(key=(lambda r: r[key]) if shortest else (lambda r: -r[key]))
    return [{f: r[f] for f in fields} for r in xs[:n]]

out["top_total_duration"] = top("central_duration_s", 8,
                                ["date", "central_duration_s", "path_width_km",
                                 "saros", "month", "lat", "lon", "type"],
                                types=("T", "H"))
out["top_annular_duration"] = top("central_duration_s", 8,
                                  ["date", "central_duration_s", "month", "type"],
                                  types=("A",))
out["top_width"] = top("path_width_km", 6, ["date", "path_width_km", "type", "month"])
out["shortest_total_duration"] = top("central_duration_s", 5,
                                     ["date", "central_duration_s", "month", "type"],
                                     types=("T", "H"), shortest=True)
out["shortest_annular_duration"] = top("central_duration_s", 5,
                                       ["date", "central_duration_s", "month", "type"],
                                       types=("A",), shortest=True)
out["by_month_total"] = {}
for r in rows:
    if r["type"] in ("T", "H"):
        out["by_month_total"][r["month"]] = out["by_month_total"].get(r["month"], 0) + 1
out["by_month_all"] = {}
for r in rows:
    out["by_month_all"][r["month"]] = out["by_month_all"].get(r["month"], 0) + 1

# 全食/混合的本影时长中位数按月（用来检验"远日点附近的全食更长"是否只是口号）
by_m_dur = {}
for r in rows:
    if r["type"] in ("T", "H") and r.get("central_duration_s"):
        by_m_dur.setdefault(r["month"], []).append(r["central_duration_s"])
out["total_duration_median_by_month"] = {
    m: round(sorted(v)[len(v) // 2]) for m, v in sorted(by_m_dur.items())}
out["total_duration_median_all_s"] = round(
    sorted([x for v in by_m_dur.values() for x in v])[
        len([x for v in by_m_dur.values() for x in v]) // 2])

# 中心时长/宽度的覆盖率：图注里要如实说"只有多少行有值"
cov = {}
for t in ("T", "H", "A", "P"):
    sub = [r for r in rows if r["type"] == t]
    cov[t] = {"rows": len(sub),
              "with_duration": sum(1 for r in sub if r.get("central_duration_s")),
              "with_width": sum(1 for r in sub if r.get("path_width_km") is not None)}
out["field_coverage"] = cov

# ---------- 5. 月影速度：赤道上地面速度 ----------
out["shadow_speed"] = {    "eastward_kmph": G["shadow_ground_speed_kmph_equator_eastward"],
    "westward_kmph": G["shadow_ground_speed_kmph_equator_westward"],
    "surface_rotation_kms": G["surface_rotation_speed_kms"],
    "moon_orbital_kms": G["moon_orbital_speed_kms"],
    "formula": "v_ground = v_moon_along_track - v_surface_rotation（同向相消、反向相叠）"}

# ---------- 6. 沙罗步长与交点年 ----------
import re as _re
import html as _H


def page_text(fname):
    h = (TMP / "sources" / fname).read_text(encoding="utf-8", errors="ignore")
    h = _re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = _re.sub(r"(?s)<[^>]+>", " ", h)
    return _re.sub(r"\s+", " ", _H.unescape(h))


sp = page_text("nasa-saros-page.html")
months = {m.lower(): float(v) for m, v in
          _re.findall(r"(\w+) Month \([^)]*\)\s*=\s*([\d.]+)\s*days", sp)}
multiples = {m.lower(): (int(n), float(d)) for n, m, d in
             _re.findall(r"(\d+) (Synodic|Anomalistic|Draconic) Months = ([\d.]+) days", sp)}
out["saros_page"] = {"source": "nasa-saros-page.html",
                     "month_days": months, "multiples": multiples}

out["saros"] = {
    "observed_step_days": stats["saros_step_observed_days"],
    "canonical_days": G["saros_canonical_days"],
    "from_synodic_days": G["saros_days_from_synodic"],
    "eclipse_year_days": G["eclipse_year_days"],
    "series_count": stats["saros_series_count"],
    "members_hist": stats["saros_members_per_series_hist"]}

# 三条系列的台阶：相邻成员间隔天数、食甚点经纬、时长与带宽（全部来自已解析目录）
from datetime import date as _date


def ladder(series):
    xs = sorted([r for r in rows if r["saros"] == series], key=lambda r: r["date"])
    prev = None
    out_ = []
    for r in xs:
        dd = _date(r["year"], r["month"], r["day"])
        out_.append({"date": r["date"], "type": r["type"],
                     "gap_days": (dd - prev).days if prev else None,
                     "lon": r["lon"], "lat": r["lat"],
                     "duration_s": r["central_duration_s"],
                     "width_km": r["path_width_km"]})
        prev = dd
    return out_


out["saros_ladders"] = {s: ladder(s) for s in (139, 136, 127)}

# ---------- 7. ΔT：账本列 vs 路径页 ----------
out["delta_t"] = {
    "catalog_range_s": stats["delta_t_catalog_range_s"],
    "crosscheck": stats["crosscheck"]}

RES.joinpath("derived.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

print("umbral:", {k: v["umbral_length_km"] for k, v in umbral.items()},
      "| half-angle", out["umbral_half_angle_deg"])
print("margins:", {k: v["margin_to_surface_km"] for k, v in margins.items()})
print("years dist", out["years_by_eclipse_count"], "rows", out["years_check_total_rows"],
      "years", out["years_counted"])
print("decades", {k: sum(v.values()) for k, v in sorted(by_dec.items())})
print("top total", [(r["date"], r["central_duration_s"], r["month"]) for r in out["top_total_duration"][:4]])
print("total/hybrid by month", sorted(out["by_month_total"].items()))
