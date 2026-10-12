"""B04 研究层 3：从 224 行日食表 + 228 行月食表"量出"食季与食年（件 04 的数据底座）。

为什么不引用现成的"食年 346.62 天"：round 1~3 抓到的 NASA 页面里都没有
"eclipse season / 食年"字样（round 3 的两个 en.wikipedia.org 请求超时失败，已如实记在
requests.jsonl），所以本题改成实测——把两类食合起来按日期聚类，季中心间隔即半个食年，
隔一季的间隔即一个食年；再用抓取页面里确实存在的回归年 365.242 天、
恒星月 27.3217 天、交点月 27.212221 天反推交点退行周期，两条路径互相核对。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
输出：tmp/<run>/B04/research/seasons.json（v1 只含日食的版本留在 seasons-solar-only-v1.json）
"""
import json
import os
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B04"

SEASON_GAP = 40.0        # 季内最大间隔阈值（天）：季内 ≤ 30，季间 ≥ 147
TROPICAL_YEAR = 365.242  # nasa-earth-fact.html "Tropical orbit period (days)"
REVOLUTION = 27.3217     # nasa-moon-fact.html "Revolution period (days)"（恒星月）
SYNODIC_PAGE = 29.53     # nasa-moon-fact.html "Synodic period (days)"
DRACONIC = 27.212221     # nasa-saros-page.html "Draconic Month (node to node)"


def d(s):
    y, m, dd = [int(v) for v in s.split("-")]
    return date(y, m, dd)


def mean(xs):
    return sum(xs) / len(xs)


def cluster(events):
    """events: [(date_str, kind, type)] 已按日期排序 → 食季列表。"""
    groups, cur = [], [events[0]]
    for prev, e in zip(events, events[1:]):
        if (d(e[0]) - d(prev[0])).days <= SEASON_GAP:
            cur.append(e)
        else:
            groups.append(cur)
            cur = [e]
    groups.append(cur)
    seas = []
    for g in groups:
        first, last = d(g[0][0]), d(g[-1][0])
        center = first.toordinal() + (last.toordinal() - first.toordinal()) / 2.0
        seas.append({
            "start": g[0][0], "end": g[-1][0],
            "center_ord": center,
            "center_date": date.fromordinal(int(round(center))).isoformat(),
            "year": date.fromordinal(int(round(center))).year,
            "n": len(g),
            "pattern": "".join(k for _, k, _ in g),
            "types": "".join(t for _, _, t in g),
            "width_days": (last - first).days,
            "gaps_inside": [(d(b[0]) - d(a[0])).days for a, b in zip(g, g[1:])],
            "events": [{"date": x[0], "body": x[1], "type": x[2]} for x in g],
        })
    return seas


def stats_of(seas, label):
    intra = [g for s in seas for g in s["gaps_inside"]]
    between = [date.fromordinal(int(round(b["center_ord"]))).toordinal() -
               date.fromordinal(int(round(a["center_ord"]))).toordinal()
               for a, b in zip(seas, seas[1:])]
    same_node = [between[i] + between[i + 1] for i in range(len(between) - 1)]
    per_year = Counter(s["year"] for s in seas)
    sb = sorted(between)
    return {
        "label": label,
        "season_count": len(seas),
        "events_per_season_hist": dict(sorted(Counter(s["n"] for s in seas).items())),
        "pattern_hist": dict(Counter(s["pattern"] for s in seas).most_common(8)),
        "season_width_days": {"min": min(s["width_days"] for s in seas),
                              "max": max(s["width_days"] for s in seas),
                              "mean": round(mean([s["width_days"] for s in seas]), 2)},
        "intra_gap_days": {"count": len(intra), "min": min(intra), "max": max(intra),
                           "hist": dict(sorted(Counter(intra).items()))},
        "inter_gap_days": {"count": len(sb), "min": sb[0], "max": sb[-1],
                           "p25": sb[len(sb) // 4], "median": sb[len(sb) // 2],
                           "p75": sb[len(sb) * 3 // 4],
                           "bins_5d": dict(sorted(
                               Counter((v // 5) * 5 for v in sb).items()))},
        "half_eclipse_year_days": round(mean(between), 2),
        "eclipse_year_days": round(mean(same_node), 2),
        "eclipse_year_std": round((sum((x - mean(same_node)) ** 2 for x in same_node)
                                   / len(same_node)) ** 0.5, 2),
        "eclipse_year_range": [min(same_node), max(same_node)],
        "eclipse_year_samples": len(same_node),
        "seasons_per_year_hist": dict(sorted(Counter(per_year.values()).items())),
        "years_with_three_seasons": sorted(y for y, c in per_year.items() if c == 3),
    }


def main():
    sol = json.load(open(B / "research" / "catalog.json", encoding="utf-8"))["rows"]
    lunj = json.load(open(B / "research" / "lunar.json", encoding="utf-8"))
    lun = lunj["rows"]
    solar_events = sorted((r["date"], "S", r["type"]) for r in sol)
    lunar_events = sorted((r["date"], "L", r["type"]) for r in lun)
    merged = sorted(solar_events + lunar_events)   # noqa: F841  两表合流

    s_sol, s_all = cluster(solar_events), cluster(merged)
    st_sol, st_all = stats_of(s_sol, "solar only"), stats_of(s_all, "solar + lunar")
    ey = st_all["eclipse_year_days"]
    n_year = 1.0 / (1.0 / ey - 1.0 / TROPICAL_YEAR)
    n_month = 1.0 / (1.0 / DRACONIC - 1.0 / REVOLUTION)
    months = Counter(d(e[0]).month for e in merged)
    center_months = Counter(d(s["center_date"]).month for s in s_all)

    first_by_year = {}
    for s in s_all:
        if s["year"] not in first_by_year or s["center_ord"] < first_by_year[s["year"]]["center_ord"]:
            first_by_year[s["year"]] = s
    drift_rows = []
    for y in range(2001, 2026):
        s = first_by_year.get(y)
        if not s:
            continue
        cd = d(s["center_date"])
        drift_rows.append({"year": y, "center": s["center_date"],
                           "doy": (cd - date(y, 1, 1)).days + 1})

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path_base": "suite_root",
        "inputs": {
            "solar_rows": len(sol), "lunar_rows": len(lun), "merged_events": len(merged),
            "season_gap_threshold_days": SEASON_GAP,
            "method": "按日期排序后，相邻事件间隔 ≤ 40 天归入同一食季",
        },
        "page_literals": {
            "tropical_year_days": TROPICAL_YEAR,
            "moon_revolution_period_days": REVOLUTION,
            "moon_synodic_period_days": SYNODIC_PAGE,
            "draconic_month_days": DRACONIC,
            "sources": {
                "tropical_year_days": "nasa-earth-fact.html",
                "moon_revolution_period_days": "nasa-moon-fact.html",
                "moon_synodic_period_days": "nasa-moon-fact.html",
                "draconic_month_days": "nasa-saros-page.html",
            },
        },
        "lunar_reconciliation": {
            "rows_parsed": len(lun), "page_says": 228,
            "type_counts_parsed": dict(Counter(r["type"] for r in lun)),
            "type_counts_page": {"N": 86, "P": 57, "T": 85},
            "years_by_count_parsed": lunj["years_by_eclipse_count_parsed"],
            "years_by_count_page": lunj["years_by_eclipse_count_page"],
        },
        "solar_only": st_sol,
        "merged": st_all,
        "eclipse_year_vs_tropical_year_days": round(ey - TROPICAL_YEAR, 2),
        "node_regression": {
            "from_measured_eclipse_year_days": round(n_year),
            "from_measured_eclipse_year_years": round(n_year / TROPICAL_YEAR, 2),
            "from_draconic_and_sidereal_days": round(n_month),
            "from_draconic_and_sidereal_years": round(n_month / TROPICAL_YEAR, 2),
            "formula": "1/食年 = 1/回归年 + 1/退行周期；1/交点月 = 1/恒星月 + 1/退行周期",
        },
        "eclipses_by_month_merged": {str(k): months[k] for k in sorted(months)},
        "season_centers_by_month": {str(k): center_months[k] for k in sorted(center_months)},
        "first_season_center_2001_2025": drift_rows,
        "seasons_2024_2027": [
            {k: s[k] for k in ("start", "end", "n", "pattern", "types", "width_days",
                              "gaps_inside", "center_date", "events")}
            for s in s_all if 2024 <= s["year"] <= 2027],
        "seasons_all": [{k: s[k] for k in ("start", "end", "n", "pattern", "types",
                                          "width_days", "center_date")} for s in s_all],
    }
    (B / "research" / "seasons.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for k in ("solar_only", "merged"):
        s = out[k]
        print(k, {x: s[x] for x in ("season_count", "events_per_season_hist",
                                    "season_width_days", "inter_gap_days",
                                    "half_eclipse_year_days", "eclipse_year_days",
                                    "eclipse_year_std", "eclipse_year_range",
                                    "seasons_per_year_hist")})
        print("   intra:", s["intra_gap_days"], "pattern:", s["pattern_hist"])
    print("EY-TY", out["eclipse_year_vs_tropical_year_days"], "node", out["node_regression"])
    print("3-season years:", out["merged"]["years_with_three_seasons"])


if __name__ == "__main__":
    main()
