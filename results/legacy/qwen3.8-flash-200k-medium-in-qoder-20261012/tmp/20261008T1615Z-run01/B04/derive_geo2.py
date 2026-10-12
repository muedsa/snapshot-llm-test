# -*- coding: utf-8 -*-
"""case-08 第二步：经度均匀性、γ-纬度关系、食甚点与 NASA 地域描述的一致性。
输入 research/catalog.json + sources/nasa-solar-basics.html，输出 research/geo2.json。
"""
import io
import json
import math
import re
import statistics

BASE = "tmp/20261008T1615Z-run01/B04"
CAT = f"{BASE}/research/catalog.json"
HTML = f"{BASE}/sources/nasa-solar-basics.html"
OUT = f"{BASE}/research/geo2.json"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
TYPE_LONG = {"Total": "T", "Annular": "A", "Hybrid": "H", "Partial": "P"}


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def main():
    rows = json.load(io.open(CAT, encoding="utf-8"))["rows"]
    text = io.open(HTML, encoding="utf-8", errors="replace").read()

    # --- NASA 十年表（2021-2030）解析：日期 / 类型 / 沙罗 / 食分 / 最长 / 地域文字
    regions = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip()
                 for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) < 7:
            continue
        m = re.match(r"^(\d{4}) (\w{3}) (\d{2})$", cells[0])
        if not m:
            continue
        iso = "%04d-%02d-%02d" % (int(m.group(1)), MONTHS[m.group(2)], int(m.group(3)))
        regions.append({
            "date": iso, "ge_ut": cells[1], "type_long": cells[2],
            "type": TYPE_LONG.get(cells[2], "?"), "saros": int(cells[3]),
            "magnitude": float(cells[4]), "duration_listed": cells[5],
            "region_text": " / ".join(x.strip() for x in cells[6].splitlines() if x.strip()),
        })
    by_date = {r["date"]: r for r in rows}
    matched, mismatched = [], []
    for r in regions:
        c = by_date.get(r["date"])
        if c is None:
            mismatched.append({"date": r["date"], "reason": "目录无此行"})
            continue
        ok = c["type"] == r["type"] and c["saros"] == r["saros"]
        item = dict(r)
        item.update({"cat_lat": c["lat"], "cat_lon": c["lon"], "cat_gamma": c["gamma"],
                     "cat_type": c["type"], "cat_saros": c["saros"],
                     "type_match": ok, "magnitude_diff": round(abs(c["magnitude"] - r["magnitude"]), 3)})
        matched.append(item)

    # --- 经度均匀性：15° 分箱卡方
    lon_bins = json.load(io.open(f"{BASE}/research/geo.json", encoding="utf-8"))["lon_bins_15"]
    exp = len(rows) / float(len(lon_bins))
    chi2 = sum((b["n"] - exp) ** 2 / exp for b in lon_bins)
    df = len(lon_bins) - 1
    lon_sorted = sorted(lon_bins, key=lambda b: -b["n"])

    # --- 分类型纬度带
    belts = [("|纬度|≤23.44 热带", lambda a: a <= 23.44),
             ("23.44–40 温带", lambda a: 23.44 < a <= 40),
             ("40–60 亚极带", lambda a: 40 < a <= 60),
             ("60–75 极圈外带", lambda a: 60 < a <= 75),
             ("|纬度|>75 极地", lambda a: a > 75)]
    per_type = {}
    for t in ["T", "A", "H", "P"]:
        sel = [r for r in rows if r["type"] == t]
        per_type[t] = {
            "n": len(sel),
            "lat_min": min(r["lat"] for r in sel), "lat_max": max(r["lat"] for r in sel),
            "abs_lat_min": min(abs(r["lat"]) for r in sel),
            "abs_lat_max": max(abs(r["lat"]) for r in sel),
            "gamma_min": min(r["gamma"] for r in sel), "gamma_max": max(r["gamma"] for r in sel),
            "lon_min": min(r["lon"] for r in sel), "lon_max": max(r["lon"] for r in sel),
            "belts": {name: sum(1 for r in sel if test(abs(r["lat"]))) for name, test in belts},
            "corr_gamma_lat": round(pearson([r["gamma"] for r in sel], [r["lat"] for r in sel]), 3)
            if len(sel) > 2 else None,
        }

    # --- γ 符号与纬度符号
    agree = sum(1 for r in rows if (r["gamma"] > 0) == (r["lat"] > 0))
    zero_lat = [r["date"] for r in rows if r["lat"] == 0]
    # 全部 P 的 |γ| 是否 >1
    ps = [r for r in rows if r["type"] == "P"]
    p_abs_gamma_gt1 = sum(1 for r in ps if abs(r["gamma"]) > 1.0)
    flagged = [r["date"] for r in rows if r["non_central_flag"] not in (None, "", "-")]

    # --- 月份 → 半球（P 类）
    def half(r):
        return "N" if r["lat"] > 0 else "S"
    season_p = {}
    for r in ps:
        key = "%02d" % r["month"]
        season_p.setdefault(key, {"N": 0, "S": 0})
        season_p[key][half(r)] += 1
    season_all = {}
    for r in rows:
        key = "%02d" % r["month"]
        season_all.setdefault(key, {"N": 0, "S": 0})
        season_all[key][half(r)] += 1

    # --- 半球计数
    hemi = {
        "lon_east": sum(1 for r in rows if r["lon"] >= 0),
        "lon_west": sum(1 for r in rows if r["lon"] < 0),
        "lat_north": sum(1 for r in rows if r["lat"] > 0),
        "lat_south": sum(1 for r in rows if r["lat"] < 0),
        "lat_zero": len(zero_lat),
    }

    # --- 中国经度带（73–135E）里的十年表成员
    band_dates = [r["date"] for r in rows if 73 <= r["lon"] <= 135]
    band_in_table = [m for m in matched if 73 <= m["cat_lon"] <= 135]

    # --- γ 与纬度异号的行
    dis = [{"date": r["date"], "type": r["type"], "lat": r["lat"], "lon": r["lon"],
            "gamma": r["gamma"], "flag": r["non_central_flag"], "qle": r["qle"]}
           for r in rows if (r["gamma"] > 0) != (r["lat"] > 0)]
    ps_lat = [abs(r["lat"]) for r in ps]
    central_polar = [{"date": r["date"], "type": r["type"], "lat": r["lat"], "lon": r["lon"],
                      "gamma": r["gamma"], "width_km": r["path_width_km"],
                      "dur_s": r["central_duration_s"]}
                     for r in rows if r["type"] in ("T", "A", "H") and abs(r["lat"]) > 75]
    band_rows = [r for r in rows if 73 <= r["lon"] <= 135]
    box_rows = [r for r in band_rows if 4 <= r["lat"] <= 54]
    band_out_box = [r for r in band_rows if r not in box_rows]
    band_abs_lat = {"le60": sum(1 for r in band_rows if abs(r["lat"]) <= 60),
                    "gt60": sum(1 for r in band_rows if abs(r["lat"]) > 60)}

    thr = max(abs(r["gamma"]) for r in rows if (r["gamma"] > 0) != (r["lat"] > 0))
    inside = [r for r in rows if abs(r["gamma"]) <= thr]
    outside = [r for r in rows if abs(r["gamma"]) > thr]
    edge_rows = [r["date"] for r in rows if r["lon"] % 15 == 0]
    quant_border_in = [(r["date"], r["lon"]) for r in band_rows if r["lon"] in (73, 135)]
    quant_border_out = [(r["date"], r["lon"]) for r in rows
                        if r["lon"] in (72, 136)]

    # --- 目录整数度 vs 路径页十进制度（件-05/07 用的同一批页面）
    pp = json.load(io.open(f"{BASE}/research/path-pages.json", encoding="utf-8"))
    xchk = []
    for key in ("nasa-path-2024", "nasa-path-2027"):
        g = pp[key]["derived"]["greatest_eclipse"]
        date = {"nasa-path-2024": "2024-04-08", "nasa-path-2027": "2027-08-02"}[key]
        c = by_date[date]
        xchk.append({"date": date, "catalog_lat": c["lat"], "page_lat": round(g["lat"], 3),
                     "dlat": round(abs(c["lat"] - g["lat"]), 3),
                     "catalog_lon": c["lon"], "page_lon": round(g["lon"], 3),
                     "dlon": round(abs(c["lon"] - g["lon"]), 3)})

    out = {
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "path_base": "suite_root",
        "source": "research/catalog.json（224 行）+ sources/nasa-solar-basics.html"
                  "（NASA 2021–2030 十年表，22 行地域文字）",
        "table_rows_parsed": len(regions),
        "table_years": [regions[0]["date"][:4], regions[-1]["date"][:4]] if regions else None,
        "regions_matched": matched,
        "regions_unmatched": mismatched,
        "lon_chi2": {"bins": len(lon_bins), "bin_deg": 15, "expected_per_bin": round(exp, 2),
                     "chi2": round(chi2, 2), "df": df,
                     "top3": [(b["lo"], b["n"]) for b in lon_sorted[:3]],
                     "bottom3": [(b["lo"], b["n"]) for b in lon_sorted[-3:]]},
        "per_type": per_type,
        "gamma_lat_sign_agree": {"n": len(rows), "agree": agree, "disagree": len(rows) - agree,
                                 "lat_zero_dates": zero_lat},
        "partial_abs_gamma_gt1": {"partial_rows": len(ps), "with_abs_gamma_gt1": p_abs_gamma_gt1,
                                  "non_central_flag_dates": flagged},
        "season_partial": season_p,
        "season_all": season_all,
        "hemisphere": hemi,
        "band_dates_n": len(band_dates),
        "band_in_decade_table": band_in_table,
        "sign_disagree_rows": dis,
        "partial_lat_bounds": {"n": len(ps), "abs_min": min(ps_lat), "abs_max": max(ps_lat)},
        "central_polar_rows": central_polar,
        "band_box": {"band_n": len(band_rows), "in_box_n": len(box_rows),
                     "outside_box_n": len(band_out_box),
                     "outside_types": {t: sum(1 for r in band_out_box if r["type"] == t)
                                       for t in ("T", "A", "H", "P")}, "abs_lat": band_abs_lat,
                     "in_box": [(r["date"], r["type"], r["lat"], r["lon"]) for r in box_rows]},
        "sign_rule_by_abs_gamma": {
            "threshold": round(thr, 4),
            "small_gamma_n": len(inside),
            "small_gamma_disagree": sum(1 for r in inside if (r["gamma"] > 0) != (r["lat"] > 0)),
            "large_gamma_n": len(outside),
            "large_gamma_disagree": sum(1 for r in outside if (r["gamma"] > 0) != (r["lat"] > 0)),
        },
        "lon_on_bin_edge_n": len(edge_rows),
        "quant_border": {"band_border_rows": quant_border_in,
                         "just_outside_rows": quant_border_out},
        "ge_coord_crosscheck": xchk,
    }
    json.dump(out, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("table rows %s years %s matched %s unmatched %s" % (
        len(regions), out["table_years"], len(matched), len(mismatched)))
    print("chi2 %.2f df %d expected %.2f top %s bottom %s" % (
        chi2, df, exp, out["lon_chi2"]["top3"], out["lon_chi2"]["bottom3"]))
    for t in ["T", "A", "H", "P"]:
        d = per_type[t]
        print(t, "n=%d lat %s..%s g %s..%s r(g,lat)=%s belts %s" % (
            d["n"], d["lat_min"], d["lat_max"], d["gamma_min"], d["gamma_max"],
            d["corr_gamma_lat"], list(d["belts"].values())))
    print("sign agree %d/%d  lat_zero %s" % (agree, len(rows), zero_lat))
    print("P |gamma|>1: %d/%d  flagged %s" % (p_abs_gamma_gt1, len(ps), flagged))
    print("hemi", hemi)
    print("season_p", sorted(season_p.items()))
    print("band_in_table", [(b["date"], b["type"], b["cat_lat"], b["cat_lon"],
                             b["region_text"][:60]) for b in band_in_table])
    print("mag diff max %.3f" % max(m["magnitude_diff"] for m in matched))
    print("disagree", [(d["date"], d["type"], d["lat"], d["gamma"], d["flag"], d["qle"]) for d in dis])
    print("P |lat| bounds", out["partial_lat_bounds"])
    print("central polar", [(c["date"], c["type"], c["lat"], c["lon"]) for c in central_polar])
    print("band_box", json.dumps(out["band_box"], ensure_ascii=False))
    print("sign_rule", json.dumps(out["sign_rule_by_abs_gamma"]), "lon_edge", len(edge_rows))
    print("polar gamma", [(c["date"], c["gamma"]) for c in central_polar])


if __name__ == "__main__":
    main()
