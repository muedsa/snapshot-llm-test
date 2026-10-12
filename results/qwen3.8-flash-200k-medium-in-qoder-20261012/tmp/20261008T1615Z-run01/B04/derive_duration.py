"""件-06 数据准备：从 224 条目录行统计中心食持续时间分布、极值、逐月中位数与时长-带宽关系。

输入只有 research/catalog.json（NASA 2001-2100 目录页逐行解析结果）。
所有数字都是本题脚本自算，属"我的推算"级，件内须声明。
输出 research/duration.json。
"""
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
import os

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
RES = ROOT / "tmp" / RID / "B04" / "research"

TYPE_NAME = {"T": "全食", "A": "环食", "H": "混合食"}


def minutes(v):
    m = int(v // 60)
    return "%dm%02ds" % (m, int(round(v - 60 * m)))


def main():
    rows = json.load(open(RES / "catalog.json", encoding="utf-8"))["rows"]
    # 中心时长存在＝该食有本影/伪本影轴落地的中心食段；2 条有时长但表内宽度为空
    central = [r for r in rows if r["central_duration_s"]]
    pair = [r for r in central if r["path_width_km"]]
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "path_base": "suite_root",
           "source": "research/catalog.json（224 行）",
           "method": "按类型分组的直方图 / 逐月中位数 / 时长-带宽散点；bin=60s",
           "rows_total": len(rows), "rows_central": len(central),
           "rows_with_duration_and_width": len(pair),
           "rows_without_central": len(rows) - len(central),
           "central_only_no_width": [{"date": r["date"], "type": r["type"],
                                      "dur_s": r["central_duration_s"], "qle": r["qle"],
                                      "flag_note": "t-/-t：中心线不落地，表内无宽度"}
                                     for r in rows
                                     if r["type"] != "P" and not r["central_duration_s"]]}

    # 1) 直方图
    bins = []
    for lo in range(0, 720, 60):
        b = {"lo": lo, "hi": lo + 60, "label": "%d" % lo}
        for t in ("T", "A", "H"):
            b[t] = len([r for r in central if r["type"] == t and lo <= r["central_duration_s"] < lo + 60])
        b["all"] = b["T"] + b["A"] + b["H"]
        bins.append(b)
    out["histogram_60s"] = bins
    out["histogram_max_bin"] = max(b["all"] for b in bins)

    # 2) 分组统计
    groups = {}
    for t in ("T", "A", "H"):
        vals = [r["central_duration_s"] for r in central if r["type"] == t]
        groups[t] = {"name": TYPE_NAME[t], "n": len(vals), "min_s": min(vals), "max_s": max(vals),
                     "mean_s": round(statistics.mean(vals), 1),
                     "median_s": round(statistics.median(vals), 1),
                     "min_str": minutes(min(vals)), "max_str": minutes(max(vals)),
                     "median_str": minutes(statistics.median(vals))}
    out["groups"] = groups

    # 3) 极值榜单（附带宽、沙罗、月份、γ、食分）
    def brief(r):
        return {"date": r["date"], "type": r["type"], "dur_s": r["central_duration_s"],
                "dur_str": minutes(r["central_duration_s"]), "width_km": r["path_width_km"],
                "saros": r["saros"], "month": r["month"], "gamma": r["gamma"],
                "magnitude": r["magnitude"], "lat": r["lat"], "lon": r["lon"],
                "sun_alt": r["sun_altitude_deg"]}
    by_dur = sorted(central, key=lambda r: r["central_duration_s"])
    out["longest_overall"] = [brief(r) for r in by_dur[::-1][:8]]
    out["shortest_overall"] = [brief(r) for r in by_dur[:8]]
    out["longest_by_type"] = {t: [brief(r) for r in by_dur[::-1] if r["type"] == t][:3]
                              for t in ("T", "A")}
    out["shortest_by_type"] = {t: [brief(r) for r in by_dur if r["type"] == t][:3]
                               for t in ("T", "A")}

    # 4) 逐月：中位数与极值（全食 / 环食分开）
    months = {}
    for m in range(1, 13):
        rec = {"month": m}
        for t in ("T", "A"):
            vals = [r["central_duration_s"] for r in central if r["month"] == m and r["type"] == t]
            rec[t] = {"n": len(vals),
                      "median_s": round(statistics.median(vals), 1) if vals else None,
                      "max_s": max(vals) if vals else None}
        rec["n_all"] = rec["T"]["n"] + rec["A"]["n"] + len(
            [r for r in central if r["month"] == m and r["type"] == "H"])
        months[str(m)] = rec
    out["by_month"] = months
    out["month_note"] = "2 月没有中心食记录（仅 P/H），故逐月中位数有缺口"

    # 5) 时长 vs 带宽散点（用于说明"带宽决定可看时长"的相关性）
    out["scatter"] = [{"x": r["path_width_km"], "y": r["central_duration_s"], "t": r["type"],
                       "date": r["date"], "gamma": r["gamma"]} for r in pair]
    out["hybrids"] = [brief(r) for r in sorted(
        [r for r in central if r["type"] == "H"], key=lambda r: r["central_duration_s"])]
    out["widest"] = {t: [brief(r) for r in sorted(
        [r for r in pair if r["type"] == t], key=lambda r: -r["path_width_km"])[:3]]
        for t in ("T", "A")}
    for t in ("T", "A"):
        pts = [(r["path_width_km"], r["central_duration_s"]) for r in pair if r["type"] == t]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in pts)
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
        out["corr_%s" % t] = {"n": len(pts), "r": round(num / den, 3),
                              "slope_s_per_km": round(num / sum((x - mx) ** 2 for x in xs), 4)}

    # 6) 极值的月份分布（近日点/远日点线索）
    out["top_total_months"] = {str(m): len([r for r in by_dur[::-1][:20]
                                           if r["month"] == m and r["type"] == "T"])
                               for m in range(1, 13)}
    out["top_annular_months"] = {str(m): len([r for r in by_dur[::-1][:20]
                                             if r["month"] == m and r["type"] == "A"])
                                 for m in range(1, 13)}
    out["top20_types"] = {t: len([r for r in by_dur[::-1][:20] if r["type"] == t])
                          for t in ("T", "A", "H")}
    out["top10_total_months"] = sorted([r["month"] for r in by_dur[::-1]
                                        if r["type"] == "T"][:10])
    out["top10_annular_months"] = sorted([r["month"] for r in by_dur[::-1]
                                          if r["type"] == "A"][:10])

    o = RES / "duration.json"
    o.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("central rows=%d/%d" % (len(central), len(rows)))
    for t in ("T", "A", "H"):
        g = groups[t]
        print(t, "n=%d min=%s med=%s max=%s" % (g["n"], g["min_str"], g["median_str"], g["max_str"]))
    print("hist", [(b["lo"], b["T"], b["A"]) for b in bins if b["all"]])
    print("corr T", out["corr_T"], "corr A", out["corr_A"])
    print("topT months", {k: v for k, v in out["top_total_months"].items() if v})
    print("topA months", {k: v for k, v in out["top_annular_months"].items() if v})
    print("shortest", [(r["date"], r["type"], r["dur_s"]) for r in out["shortest_overall"][:5]])
    print("longest", [(r["date"], r["type"], r["dur_s"]) for r in out["longest_overall"][-5:]])


if __name__ == "__main__":
    main()
