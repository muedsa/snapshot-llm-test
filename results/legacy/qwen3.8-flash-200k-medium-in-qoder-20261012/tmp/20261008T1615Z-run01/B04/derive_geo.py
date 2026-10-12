"""件-08 数据准备：224 个食甚点的地理散布，以及"中国经度带"的口径化清点。

输入：research/catalog.json（NASA Catalog of Solar Eclipses 2001–2100 的 224 行）
输出：research/geo.json
所有计数都是本脚本现场算出；"中国经度带""境内方框"的边界在下面显式定义，
换边界数字就变，因此同时给出敏感性。
"""
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
RES = ROOT / "tmp" / RID / "B04" / "research"

# 中国大陆领土经度约 73.5°E–135.1°E，纬度约 3.9°N–53.6°N（本脚本按整数带取 73–135 / 4–54）
LON_LO, LON_HI = 73, 135
LAT_LO, LAT_HI = 4, 54


def brief(r):
    return {"date": r["date"], "type": r["type"], "lat": r["lat"], "lon": r["lon"],
            "width_km": r["path_width_km"], "dur_s": r["central_duration_s"],
            "gamma": r["gamma"], "saros": r["saros"]}


def main():
    rows = json.load(open(RES / "catalog.json", encoding="utf-8"))["rows"]
    pts = [r for r in rows if r.get("parsed")]
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "path_base": "suite_root",
           "source": "research/catalog.json（NASA 21 世纪目录 224 行，食甚点经纬度为目录原值）",
           "definitions": {
               "china_lon_band": "%d°E–%d°E（只按经度，不限纬度）" % (LON_LO, LON_HI),
               "china_box": "%d°E–%d°E 且 %d°N–%d°N（近似中国领土包围盒）"
                            % (LON_LO, LON_HI, LAT_LO, LAT_HI)},
           "n_rows": len(rows), "n_points": len(pts)}

    def in_band(r):
        return LON_LO <= r["lon"] <= LON_HI

    def in_box(r):
        return in_band(r) and LAT_LO <= r["lat"] <= LAT_HI

    band = [r for r in pts if in_band(r)]
    box = [r for r in pts if in_box(r)]
    out["type_counts_all"] = dict(Counter(r["type"] for r in pts))
    out["band_n"] = len(band)
    out["band_types"] = dict(Counter(r["type"] for r in band))
    out["box_n"] = len(box)
    out["box_types"] = dict(Counter(r["type"] for r in box))
    out["band_points"] = [brief(r) for r in sorted(band, key=lambda r: r["date"])]
    out["box_points"] = [brief(r) for r in sorted(box, key=lambda r: r["date"])]
    # 边界敏感性：把经度带收紧/放宽 5°，看计数怎么变
    out["band_sensitivity"] = {
        "%d-%d" % (LON_LO - 5, LON_HI + 5): len([r for r in pts if LON_LO - 5 <= r["lon"] <= LON_HI + 5]),
        "%d-%d" % (LON_LO, LON_HI): len(band),
        "%d-%d" % (LON_LO + 5, LON_HI - 5): len([r for r in pts if LON_LO + 5 <= r["lon"] <= LON_HI - 5]),
        "%d-%d" % (LON_LO + 10, LON_HI): len([r for r in pts if LON_LO + 10 <= r["lon"] <= LON_HI])}
    # 经度 24 箱（每 15°）× 类型；纬度 12 箱（每 15°）× 类型
    lonb = []
    for i in range(24):
        lo, hi = -180 + 15 * i, -180 + 15 * (i + 1)
        sel = [r for r in pts if lo <= r["lon"] < hi]
        lonb.append({"lo": lo, "hi": hi, "n": len(sel),
                     "T": len([r for r in sel if r["type"] == "T"]),
                     "A": len([r for r in sel if r["type"] == "A"]),
                     "H": len([r for r in sel if r["type"] == "H"]),
                     "P": len([r for r in sel if r["type"] == "P"])})
    latb = []
    for i in range(12):
        lo, hi = -90 + 15 * i, -90 + 15 * (i + 1)
        sel = [r for r in pts if lo <= r["lat"] < hi]
        latb.append({"lo": lo, "hi": hi, "n": len(sel),
                     "T": len([r for r in sel if r["type"] == "T"]),
                     "A": len([r for r in sel if r["type"] == "A"]),
                     "H": len([r for r in sel if r["type"] == "H"]),
                     "P": len([r for r in sel if r["type"] == "P"])})
    out["lon_bins_15"] = lonb
    out["lat_bins_15"] = latb
    out["lon_minmax"] = [min(r["lon"] for r in pts), max(r["lon"] for r in pts)]
    out["lat_minmax"] = [min(r["lat"] for r in pts), max(r["lat"] for r in pts)]
    out["abs_lat"] = {
        "le_23_44": len([r for r in pts if abs(r["lat"]) <= 23]),
        "le_40": len([r for r in pts if abs(r["lat"]) <= 40]),
        "le_60": len([r for r in pts if abs(r["lat"]) <= 60]),
        "gt_60": len([r for r in pts if abs(r["lat"]) > 60])}
    # 每 10° 经度里"落在带内的全食"，用于说明 7 次全食的年份分布
    out["band_total_by_decade"] = dict(sorted(Counter(
        "%ds" % (r["year"] // 10 * 10) for r in band if r["type"] == "T").items()))
    out["box_by_decade"] = dict(sorted(Counter(
        "%ds" % (r["year"] // 10 * 10) for r in box).items()))
    # 目录里纬度/经度都是整数度：量化误差 ±0.5°
    out["quantization_deg"] = 0.5
    # 与"食带是否穿过中国"不同的另一问：本表只有食甚点，路径覆盖需要逐条路径页
    o = RES / "geo.json"
    o.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("n=%d band=%d %s box=%d %s" % (len(pts), len(band), out["band_types"], len(box),
                                         out["box_types"]))
    print("band totals:", [(r["date"], r["lat"], r["lon"], r["path_width_km"],
                           r["central_duration_s"]) for r in band if r["type"] == "T"])
    print("box:", [(r["date"], r["type"], r["lat"], r["lon"]) for r in box])
    print("sens:", out["band_sensitivity"], "abs_lat:", out["abs_lat"])
    print("lon bins:", [(b["lo"], b["n"]) for b in lonb])
    print("lat bins:", [(b["lo"], b["n"]) for b in latb])


if __name__ == "__main__":
    main()
