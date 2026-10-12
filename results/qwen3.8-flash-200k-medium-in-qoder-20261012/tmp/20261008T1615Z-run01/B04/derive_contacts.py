"""B04 件 09 的推导：把"能裸眼看多久"变成可核对的算术。

输入都是本机已抓取的真实页面（不联网）：
  research/path-pages.json  —— 2024/2027 路径表 100/104 行 + 大食/最长两行原文
  probe/nasa-oh-*.txt       —— NASA Occurrence Highlights 摘要（食分 m、ΔT、带宽…）
  research/catalog.json     —— 21 世纪目录 224 行（含 magnitude 与 central_duration_s）

核心关系（本脚本自己算，不用任何外部"结论"）：设太阳视半径 r_s、月球视半径
m·r_s，观测者在中心线上，月球相对太阳的角速度取为常数 ω。
  初亏→食既：中心距从 (r_s+m·r_s) 变到 (m·r_s−r_s)，位移 2·r_s  →  t1 = 2r_s/ω
  食既→生光（全食）：位移 2(m−1)r_s                        →  D = 2(m−1)r_s/ω
  生光→复圆：同 t1
于是 t1 = D/(m−1)，整场 C1→C4 = D·(m+1)/(m−1)，裸眼安全占比
  D / [D·(m+1)/(m−1)] = (m−1)/(m+1)          ——只跟食分有关，ω 消掉了。
m≤1（偏食/环食）时该式为 0 或负，对应 NASA 安全页"偏食与环食永远不安全"。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import io
import json
import math
import os
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

TMP = Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B04"
OUT = TMP / "research" / "contacts.json"

OH = {"2024-04-08": "probe/nasa-oh-2024.txt", "2027-08-02": "probe/nasa-oh-2027.txt"}
OHKEYS = ["Greatest Eclipse (TD)", "Greatest Eclipse (UT)", "Delta T", "Eclipse Magnitude",
          "Gamma", "Central Duration", "Path Width", "Greatest Eclipse Point", "Sun Altitude",
          "Saros Series"]


def hhmm_to_s(t):
    h, m = t.split(":")
    return int(h) * 3600 + int(m) * 60


def hms_to_s(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def dur_to_s(s):
    mm, sfrac = s.split("m")
    return int(mm) * 60 + float(sfrac.rstrip("s"))


def hour_angle_deg(alt_deg, az_deg, lat_deg):
    """由路径表里公布的太阳高度/方位反推时角（不需要赤纬）。
    方位自正北起算、向东为正；H 用 atan2 消掉赤纬，负值=太阳在子午线以东（上午）。"""
    a = math.radians(alt_deg)
    A = math.radians(az_deg)
    p = math.radians(lat_deg)
    y = -math.cos(a) * math.sin(A)
    x = math.sin(a) * math.cos(p) - math.cos(a) * math.cos(A) * math.sin(p)
    return math.degrees(math.atan2(y, x))


def parse_oh(path, date):
    lines = io.open(TMP / path, encoding="utf-8").read().split("\n")
    head = "Total Solar Eclipse of %s" % ("April 8" if date == "2024-04-08" else "August 2")
    i = lines.index(head)
    out = {}
    for l in lines[i + 1:i + 14]:
        if ":" not in l:
            continue
        k, v = [x.strip() for x in l.split(":", 1)]
        if k in OHKEYS:
            out[k] = v
    return out


def timeline(m, dur_s, ge_ut):
    half = dur_s / (m - 1.0)
    span = 2 * half + dur_s
    ut = ge_ut
    def fmt(sec):
        sec = sec % 86400
        return "%02d:%02d:%05.2f" % (sec // 3600, (sec % 3600) // 60, sec % 60)
    c1 = fmt(ut - half - dur_s / 2.0)
    c2 = fmt(ut - dur_s / 2.0)
    gm = fmt(ut)
    c3 = fmt(ut + dur_s / 2.0)
    c4 = fmt(ut + half + dur_s / 2.0)
    return {"magnitude": m, "totality_s": round(dur_s, 1),
            "half_partial_s": round(half, 1), "half_partial_min": round(half / 60.0, 1),
            "event_span_s": round(span, 1), "event_span_hms":
            "%dh%02dm%02ds" % (span // 3600, (span % 3600) // 60, span % 60),
            "safe_pct": round(100.0 * (m - 1.0) / (m + 1.0), 3),
            "safe_fraction_formula": "(m-1)/(m+1)",
            "contacts": [
                {"cn": "初亏", "en": "C1 first contact (penumbra)", "ut": c1, "offset_s": round(-half - dur_s / 2.0, 1)},
                {"cn": "食既", "en": "C2 totality begins", "ut": c2, "offset_s": round(-dur_s / 2.0, 1)},
                {"cn": "食甚", "en": "greatest eclipse (not a contact)", "ut": gm, "offset_s": 0.0},
                {"cn": "生光", "en": "C3 totality ends", "ut": c3, "offset_s": round(dur_s / 2.0, 1)},
                {"cn": "复圆", "en": "C4 fourth contact (penumbra)", "ut": c4, "offset_s": round(half + dur_s / 2.0, 1)}]}


def track(rows):
    timed = [r for r in rows if not r["is_limits"]]
    durs = [r["duration_s"] for r in rows]
    widths = [r["width_km"] for r in rows]
    ratios = [r["diameter_ratio"] for r in rows]
    alts = [r["sun_alt"] for r in rows]
    speed = [r["width_km"] / r["duration_s"] for r in rows]      # 本影横向速度 km/s
    return {"table_rows": len(rows), "timed_rows": len(timed),
            "first_listed_time": (rows[0]["time"] if rows[0]["is_limits"] else rows[0]["time"]),
            "first_timed_time": timed[0]["time"], "last_timed_time": timed[-1]["time"],
            "listed_span_min": (hhmm_to_s(timed[-1]["time"]) - hhmm_to_s(timed[0]["time"])) / 60.0,
            "limits_first_duration_s": rows[0]["duration_s"],
            "limits_last_duration_s": rows[-1]["duration_s"],
            "duration_s_min": min(durs), "duration_s_max": max(durs),
            "duration_s_median": round(statistics.median(durs), 1),
            "width_km_min": min(widths), "width_km_max": max(widths),
            "ratio_min": min(ratios), "ratio_max": max(ratios),
            "sun_alt_min": min(alts), "sun_alt_max": max(alts),
            "rows_sun_alt_gt_0": sum(1 for a in alts if a > 0),
            "transverse_speed_km_s_min": round(min(speed), 3),
            "transverse_speed_km_s_median": round(statistics.median(speed), 3),
            "transverse_speed_km_s_max": round(max(speed), 3),
            "speed_first_row": round(rows[0]["width_km"] / rows[0]["duration_s"], 3),
            "speed_at_max_duration_row": round(max(rows, key=lambda r: r["duration_s"])["width_km"]
                                               / max(rows, key=lambda r: r["duration_s"])["duration_s"], 3)}


def off_axis(width_km, dur_s, r_ratio=0.5):
    """垂直于食带方向偏离中心线 d 之后的剩余窗口：本影截面按圆处理，
    弦长 = 2*sqrt(R^2-d^2)，窗口按同比例缩水。"""
    R = width_km / 2.0
    grid = []
    for f in [0, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.0]:
        grid.append({"d_km": round(f * R, 1), "frac_of_half_width": f,
                     "remaining_s": round(dur_s * max(0.0, (1 - f * f) ** 0.5), 1)})
    def solve(target_s):
        f = (1 - (target_s / dur_s) ** 2) ** 0.5
        return round(f * R, 1)
    return {"half_width_km": round(R, 1), "center_duration_s": dur_s,
            "grid": grid, "d_km_for_60s": solve(60.0), "d_km_for_10s": solve(10.0),
            "model_note": "把本影在地面的横截面当作直径=带宽的圆，窗口正比于该圆在偏离 d 处的弦长"}


def main():
    pp = json.load(io.open(TMP / "research" / "path-pages.json", encoding="utf-8"))
    cat = json.load(io.open(TMP / "research" / "catalog.json", encoding="utf-8"))["rows"]
    dates = {"nasa-path-2024": "2024-04-08", "nasa-path-2027": "2027-08-02"}

    eclipses = {}
    for key, date in dates.items():
        blk = pp[key]
        d = blk["derived"]
        ge = d["greatest_eclipse"]
        ge_ut = hhmm_to_s(ge["time_ut"][:5]) + float(ge["time_ut"][6:])
        oh = parse_oh(OH[date], date)
        m_oh = float(oh["Eclipse Magnitude"])
        tl_path = timeline(m_oh, ge["duration_s"], ge_ut)
        tl_path["source_duration"] = "path page greatest-eclipse line (%s s)" % ge["duration_s"]
        tl_gd = timeline(m_oh, d["greatest_duration"]["duration_s"],
                         hhmm_to_s(d["greatest_duration"]["time_ut"][:5]) + float(d["greatest_duration"]["time_ut"][6:]))
        # 用目录里的整数食分再算一遍，看结论对食分多敏感
        catrow = [r for r in cat if r["date"] == date][0]
        tl_cat = timeline(catrow["magnitude"], catrow["central_duration_s"], ge_ut)
        tds = (hhmm_to_s(oh["Greatest Eclipse (TD)"][:5]) + float(oh["Greatest Eclipse (TD)"][6:])) - ge_ut
        # 地方真太阳时：经度每 1° 对应 4 分钟（东正西负），与大食时刻的 UT 相加
        lon = ge["lon"]
        off_min = lon * 4.0
        local = ["%02d:%02d:%04.1f" % (((hms_to_s(c["ut"]) + int(round(off_min * 60))) % 86400) // 3600,
                                       (((hms_to_s(c["ut"]) + int(round(off_min * 60))) % 86400) % 3600) // 60,
                                       ((hms_to_s(c["ut"]) + int(round(off_min * 60))) % 86400) % 60)
                 for c in tl_path["contacts"]]
        H = hour_angle_deg(ge["sun_alt"], ge["sun_azm"], ge["lat"])      # 度，负=上午
        # 表格里的 alt/az 只给到 0.1°，把 ±0.05° 的舍入盒扫一遍看 H 有多稳
        spread = max(abs(hour_angle_deg(ge["sun_alt"] + da, ge["sun_azm"] + dz, ge["lat"]) - H)
                     for da in (-0.05, 0, 0.05) for dz in (-0.05, 0, 0.05))
        lat_at_ge = (ge_ut + off_min * 60.0) % 86400.0
        lat_from_sun = 12 * 3600 + H * 240.0                              # 1° 时角 = 4 分钟
        eclipses[date] = {
            "path_source": blk["source_file"], "oh_source": OH[date],
            "oh_summary": oh,
            "catalog_row": {"magnitude": catrow["magnitude"], "type": catrow["type"],
                            "central_duration_s": catrow["central_duration_s"],
                            "path_width_km": catrow["path_width_km"], "gamma": catrow["gamma"],
                            "lat": catrow["lat"], "lon": catrow["lon"], "greatest_td": catrow["greatest_td"]},
            "magnitude_diff_catalog_vs_oh": round(abs(catrow["magnitude"] - m_oh), 5),
            "duration_diff_path_vs_catalog_s": round(ge["duration_s"] - catrow["central_duration_s"], 1),
            "deltat": {"oh_stated_s": float(oh["Delta T"].rstrip(" s")),
                       "implied_by_path_minus_oh_TD_s": round(tds, 1),
                       "path_page_note_delta_t_s": d["delta_t_page_s"]},
            "site_timeline_at_greatest_eclipse": tl_path,
            "local_apparent_time": {"longitude_deg": round(lon, 3),
                                    "offset_from_ut_min": round(off_min, 1),
                                    "rule": "1° 经度 = 4 分钟，东经为正",
                                    "contacts_local_apparent": local},
            "sun_position_check": {"hour_angle_deg_from_published_alt_az": round(H, 3),
                                   "lat_at_greatest_eclipse_from_longitude_s": round(lat_at_ge, 1),
                                   "lat_at_greatest_eclipse_from_sun_position_s": round(lat_from_sun, 1),
                                   "difference_min": round((lat_at_ge - lat_from_sun) / 60.0, 2),
                                   "H_rounding_spread_deg": round(spread, 3),
                                   "H_rounding_spread_as_time_min": round(spread * 4.0, 2),
                                   "note": "两条独立路径（经度 vs 公布的高度/方位角）算出的地方真太阳时应基本吻合"},
            "site_timeline_at_greatest_duration": tl_gd,
            "site_timeline_from_catalog_rounding": tl_cat,
            "track": track(blk["rows"]),
            "off_axis_at_greatest_eclipse": off_axis(ge["width_km"], ge["duration_s"]),
        }

    # 全目录：安全占比只依赖食分
    rows = []
    for r in cat:
        m = r["magnitude"]
        pct = 100.0 * (m - 1.0) / (m + 1.0) if m > 1.0 else 0.0
        span = (r["central_duration_s"] * (m + 1.0) / (m - 1.0)) if (m > 1.0 and r["central_duration_s"]) else None
        rows.append({"date": r["date"], "type": r["type"], "magnitude": m,
                     "totality_s": r["central_duration_s"], "safe_pct": round(pct, 3),
                     "event_span_s": round(span, 1) if span else None,
                     "event_span_min": round(span / 60.0, 1) if span else None})
    has = [x for x in rows if x["safe_pct"] > 0]
    no = [x for x in rows if x["safe_pct"] <= 0]
    pcts = [x["safe_pct"] for x in has]
    by_type = {}
    for t in "TAHP":
        sub = [x for x in rows if x["type"] == t]
        by_type[t] = {"n": len(sub), "with_window": sum(1 for x in sub if x["safe_pct"] > 0),
                      "pct_min": round(min([x["safe_pct"] for x in sub]), 3) if sub else None,
                      "pct_max": round(max([x["safe_pct"] for x in sub]), 3) if sub else None,
                      "pct_median": round(statistics.median([x["safe_pct"] for x in sub]), 3) if sub else None}
    bins = [0, 0.25, 0.5, 1, 2, 3, 5]
    hist = []
    for i, lo in enumerate(bins):
        hi = bins[i + 1] if i + 1 < len(bins) else 100.0
        hist.append({"label": "%.2f-%.2f%%" % (lo, hi),
                     "n": sum(1 for p in pcts if lo <= p < hi)})
    spans = [x["event_span_s"] for x in has if x["event_span_s"]]
    res = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path_base": "suite_root",
        "model": ("中心线上的观测者；太阳视半径 r_s，月球视半径 m*r_s，相对角速度视为常数。"
                  "初亏->食既 = 食甚两侧各 D/(m-1)；整场 = D*(m+1)/(m-1)；安全占比 = (m-1)/(m+1)。"
                  "占比与 ω 无关，绝对时刻依赖常数角速度假设。"),
        "eclipses": eclipses,
        "catalog_2021_2100": {
            "n_rows": len(rows), "n_with_safe_window": len(has), "n_no_safe_window": len(no),
            "m_gt_1_but_no_central_duration": sum(1 for x in has if not x["event_span_s"]),
            "no_window_types": {t: sum(1 for x in no if x["type"] == t) for t in "TAHP"},
            "safe_pct_min": round(min(pcts), 3), "safe_pct_max": round(max(pcts), 3),
            "safe_pct_median": round(statistics.median(pcts), 3),
            "pct_below_1pct": sum(1 for p in pcts if p < 1.0),
            "event_span_min_median": round(statistics.median(spans) / 60.0, 1),
            "event_span_min_max": round(max(spans) / 60.0, 1),
            "by_type": by_type, "histogram": hist,
            "top5": sorted(has, key=lambda x: -x["safe_pct"])[:5],
            "bottom5": sorted(has, key=lambda x: x["safe_pct"])[:5],
            "rows": rows},
        "caveats": [
            "NASA 的食分 m 是地心（geocentric）比值，观测者的=topocentric 比值略有差异；这里直接用它做盘径几何，误差进入窗口长度。",
            "常数相对角速度假设：整场时长（复圆-初亏）是推算值；安全占比 (m-1)/(m+1) 只依赖食分。",
            "混合食（H）在同一条路径上不同时段的 m 会跨过 1，用目录里大食时刻的单一 m 代表整场是简化。",
            "贝利珠/钻石环的持续秒数：NASA glossary 只说 few seconds，本套材料没有可读出的秒数，故图上不写具体数字。",
            "path 页大食时刻与 OH 页 TD/UT 之差与 OH 自报 ΔT 不相等，见各食 deltat 字段。"],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", os.path.relpath(OUT, TMP))
    for date, e in eclipses.items():
        t = e["site_timeline_at_greatest_eclipse"]
        print("%s m=%.5f tot=%.1fs span=%s safe=%.2f%% | half-partial %.1f min"
              % (date, t["magnitude"], t["totality_s"], t["event_span_hms"], t["safe_pct"], t["half_partial_min"]))
        print("   contacts:", "  ".join("%s %s" % (c["cn"], c["ut"]) for c in t["contacts"]))
    c = res["catalog_2021_2100"]
    print("catalog: %d/%d rows have a naked-eye window; pct median %.2f max %.2f; below 1%%: %d"
          % (c["n_with_safe_window"], c["n_rows"], c["safe_pct_median"], c["safe_pct_max"], c["pct_below_1pct"]))
    print("by_type:", json.dumps(c["by_type"], ensure_ascii=False))
    print("hist:", c["histogram"])
    print("deltat 2024:", eclipses["2024-04-08"]["deltat"], "2027:", eclipses["2027-08-02"]["deltat"])


if __name__ == "__main__":
    main()
