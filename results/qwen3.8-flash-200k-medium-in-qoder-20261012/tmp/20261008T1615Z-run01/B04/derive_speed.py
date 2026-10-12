"""件-07 数据准备：把两条食带路径页的逐点表变成"沿轨距离—影速"序列，并做两个独立算法的对账。

输入：research/path-pages.json（parse_path.py 从 NASA 2024/2027 路径页解析出的中央线表）
      research/derived.json（NASA 事实页常数：月球轨道速度、地表自转、本影几何）
输出：research/speed.json
所有沿轨量都是本题脚本自算（页面没有给影速），属"我的推算"级。
"""
import json
import math
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
RES = ROOT / "tmp" / RID / "B04" / "research"
STEP_S = 120.0


def haversine(a, b):
    la1, lo1, la2, lo2 = [math.radians(v) for v in (a[0], a[1], b[0], b[1])]
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def secs(hhmmss):
    parts = str(hhmmss).split(":")
    v = int(parts[0]) * 3600 + float(parts[1]) * 60
    return v + float(parts[2]) if len(parts) > 2 else v


def pearson(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pts)
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return round(num / den, 3) if den else None


def main():
    pp = json.load(open(RES / "path-pages.json", encoding="utf-8"))
    dv = json.load(open(RES / "derived.json", encoding="utf-8"))
    ss = dv["shadow_speed"]
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "path_base": "suite_root",
           "source": "research/path-pages.json（NASA 2024/2027 路径页中央线表）",
           "method": "相邻中央线点大圆距离 ÷ 120 秒＝该段影速；带宽 ÷ 该点时长＝另一个独立影速估计；"
                     "沿轨 8 等分给剖面；影速 × 时长 ÷ 带宽＝本影脚印的沿轨长宽比",
           "constants": ss,
           "ref_east_kms": round(ss["eastward_kmph"] / 3.6 / 1000.0, 4),
           "ref_west_kms": round(ss["westward_kmph"] / 3.6 / 1000.0, 4)}

    tracks = {}
    for key in ("nasa-path-2024", "nasa-path-2027"):
        rows = [r for r in pp[key]["rows"] if not r.get("is_limits")]
        segs = []
        cum = 0.0
        for a, b in zip(rows, rows[1:]):
            dd = haversine(a["central"], b["central"])
            cum += dd
            segs.append({"from": a["time"], "to": b["time"], "km": round(dd, 1),
                         "kms": round(dd / STEP_S, 3), "at_km": round(cum, 1),
                         "lat": round((a["central"][0] + b["central"][0]) / 2.0, 2)})
        pts = []
        run = 0.0
        for r in rows:
            if r is not rows[0]:
                run += haversine(rows[rows.index(r) - 1]["central"], r["central"])
            imp = (r["width_km"] / r["duration_s"]) if (r.get("width_km") and r.get("duration_s")) else None
            pts.append({"time": r["time"], "km": round(run, 1), "lat": round(r["central"][0], 2),
                        "lon": round(r["central"][1], 2), "width_km": r.get("width_km"),
                        "dur_s": r.get("duration_s"), "implied_kms": round(imp, 3) if imp else None})
        kms = [s["kms"] for s in segs]
        imp = [p["implied_kms"] for p in pts if p["implied_kms"]]
        mid = slice(6, -6)
        # 沿轨 8 等分剖面：影速、纬度、宽度÷时长，以及" footprint 沿轨长度 ÷ 带宽"
        prof = []
        for i in range(8):
            sel = [s for s in segs if cum * i / 8.0 <= s["at_km"] < cum * (i + 1) / 8.0]
            psel = [p for p in pts if cum * i / 8.0 <= p["km"] < cum * (i + 1) / 8.0
                    and p["implied_kms"]]
            if not sel:
                continue
            v = statistics.mean([s["kms"] for s in sel])
            im = statistics.mean([p["implied_kms"] for p in psel]) if psel else None
            dur = statistics.mean([p["dur_s"] for p in psel if p["dur_s"]]) if psel else None
            wid = statistics.mean([p["width_km"] for p in psel if p["width_km"]]) if psel else None
            prof.append({"bin": i, "at_frac": round((i + 0.5) / 8.0, 3),
                         "kms": round(v, 3), "lat": round(statistics.mean([s["lat"] for s in sel]), 2),
                         "implied_kms": round(im, 3) if im else None,
                         "ratio": round(im / v, 3) if im else None,
                         "extent_km": round(v * dur, 0) if dur else None,
                         "width_km": round(wid, 0) if wid else None,
                         "aspect": round(v * dur / wid, 2) if (dur and wid) else None})
        band = kms[mid]
        tracks[key] = {
            "label": pp[key]["label"], "rows": len(rows), "segments": segs, "points": pts,
            "total_km": round(cum, 1),
            "mean_kms": round(cum / (len(segs) * STEP_S), 3),
            "median_kms": round(statistics.median(kms), 3),
            "min_seg": min(segs, key=lambda s: s["kms"]), "max_seg": max(segs, key=lambda s: s["kms"]),
            "mid_mean_kms": round(statistics.mean(kms[mid]), 3),
            "mid_min_kms": min(kms[mid]), "mid_max_kms": max(kms[mid]),
            "implied_mean_kms": round(statistics.mean(imp), 3),
            "implied_mid_mean_kms": round(statistics.mean(imp[6:-6]), 3),
            "lat_range": [round(min(p["lat"] for p in pts), 2), round(max(p["lat"] for p in pts), 2)],
            "corr_speed_lat": pearson([(s["lat"], s["kms"]) for s in segs]),
            "corr_seg_vs_implied": pearson([(p["implied_kms"], s["kms"]) for p, s in
                                            zip(pts[1:-1], segs)][0:min(len(pts) - 2, len(segs))]),
            "profile": prof,
            "mid_in_band": len([v for v in band if out["ref_east_kms"] <= v <= out["ref_west_kms"]]),
            "mid_above_band": len([v for v in band if v > out["ref_west_kms"]]),
            "mid_below_band": len([v for v in band if v < out["ref_east_kms"]]),
            "mid_n": len(band),
        }
    out["tracks"] = tracks

    # 自转分量随纬度：v = v_eq * cos(lat)
    out["rotation_vs_lat"] = [{"lat": la, "kms": round(ss["surface_rotation_kms"] * math.cos(
        math.radians(la)), 3)} for la in range(0, 91, 5)]

    o = RES / "speed.json"
    o.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, t in tracks.items():
        print("%s rows=%d total=%.0f km mean=%.3f med=%.3f mid=%.3f[%.3f-%.3f] min=%.3f@%s max=%.3f@%s"
              % (k, t["rows"], t["total_km"], t["mean_kms"], t["median_kms"], t["mid_mean_kms"],
                 t["mid_min_kms"], t["mid_max_kms"], t["min_seg"]["kms"], t["min_seg"]["from"],
                 t["max_seg"]["kms"], t["max_seg"]["from"]))
        print("   implied mean=%.3f mid=%.3f | corr(seg,lat)=%s corr(seg,implied)=%s lat %s"
              % (t["implied_mean_kms"], t["implied_mid_mean_kms"], t["corr_speed_lat"],
                 t["corr_seg_vs_implied"], t["lat_range"]))
        print("   band(%.3f-%.3f): in %d/%d above %d below %d"
              % (out["ref_east_kms"], out["ref_west_kms"], t["mid_in_band"], t["mid_n"],
                 t["mid_above_band"], t["mid_below_band"]))
        print("   profile:", " ".join("%.2f@%+.0f(r%s/a%s)" % (p["kms"], p["lat"], p["ratio"],
                                                               p["aspect"]) for p in t["profile"]))
    print("ref east/west km/s:", out["ref_east_kms"], out["ref_west_kms"])


if __name__ == "__main__":
    main()
