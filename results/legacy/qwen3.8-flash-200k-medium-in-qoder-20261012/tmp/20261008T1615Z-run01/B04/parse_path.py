"""解析 NASA 食带路径页（SEpath）的中央线表 → research/path-pages.json。

页面每两分钟给出一行：北界/南界/中央线经纬度、日月直径比、太阳高度与方位、
带宽（km）与中央线全食时长。首末两行是 "Limits"（影轴进出地球），
个别行的某条界用 "-" 占位。这里逐行取出并派生：沿轨长度、平均影速、
各量的极值位置，供 case-05（档案页）与 case-07（影速）使用。
"""
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
SRC = ROOT / "tmp" / RID / "B04" / "sources"
OUT = ROOT / "tmp" / RID / "B04" / "research"

PAIR = re.compile(r"(\d{2,3})\s+(\d{2}\.\d)\s*([NS])\s+(\d{2,3})\s+(\d{2}\.\d)\s*([EW])")
TAIL = re.compile(r"(?P<ratio>\d\.\d{3})\s+(?P<alt>\d{1,2}|-)\s+(?P<azm>\d{1,3}|-)\s+"
                  r"(?P<width>\d{2,3})\s+(?P<dur>\d{1,2})m(?P<dur_s>\d{2}\.\d)s")
HEAD = re.compile(r"^(?P<t>\d{2}:\d{2}|Limits)\b")


def dms_to_deg(deg, minutes, hemi):
    v = int(deg) + float(minutes) / 60.0
    return v if hemi in "NE" else -v


def haversine(a, b):
    la1, lo1, la2, lo2 = [math.radians(v) for v in (a[0], a[1], b[0], b[1])]
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def parse(page):
    raw = (SRC / page).read_text(encoding="utf-8", errors="replace")
    txt = re.sub(r"<[^>]+>", "\n", re.sub(r"<(script|style).*?</\1>", " ", raw,
                                          flags=re.S | re.I))
    lines = [l.rstrip() for l in txt.split("\n")]
    rows = []
    for line in lines:
        s = " ".join(line.split())
        m = HEAD.match(s)
        if not m:
            continue
        tail = TAIL.search(s)
        pairs = PAIR.findall(s)
        if not pairs or not tail:
            continue
        body = s[:tail.start()]
        latlon = [(dms_to_deg(d, mn, h), dms_to_deg(dd, mm, hh)) for d, mn, h, dd, mm, hh in pairs]
        dashed = "-" in body[m.end():] if len(latlon) < 3 else False
        if len(latlon) == 3:
            n, so, c = latlon
        elif len(latlon) == 2 and dashed:      # 北界缺失（影轴转向、北界不再与地面相交）
            n, so, c = None, latlon[0], latlon[1]
        elif len(latlon) == 2:                 # 南界缺失
            n, so, c = latlon[0], None, latlon[1]
        else:
            continue
        g = tail.groupdict()
        t = m.group("t")
        rows.append({
            "time": t, "is_limits": t == "Limits",
            "north": n, "south": so, "central": c,
            "diameter_ratio": float(g["ratio"]),
            "sun_alt": None if g["alt"] == "-" else int(g["alt"]),
            "sun_azm": None if g["azm"] == "-" else int(g["azm"]),
            "width_km": int(g["width"]),
            "duration_s": int(g["dur"]) * 60 + float(g["dur_s"]),
        })
    return rows


def derive(rows, ge, gd, delta_t):
    times = [r["time"] for r in rows if not r["is_limits"]]
    t0 = datetime.strptime(times[0], "%H:%M")
    t1 = datetime.strptime(times[-1], "%H:%M")
    minutes = (t1 - t0).total_seconds() / 60.0 + 2          # 末行再走一格
    seg = [(haversine(a["central"], b["central"]), a["time"], b["time"])
           for a, b in zip(rows, rows[1:])]
    length = sum(s[0] for s in seg)
    durs = [(r["duration_s"], r["time"], r["central"]) for r in rows]
    widths = [(r["width_km"], r["time"]) for r in rows]
    ratios = [(r["diameter_ratio"], r["time"]) for r in rows]
    alts = [(r["sun_alt"], r["time"]) for r in rows if r["sun_alt"] is not None]
    lats = [r["central"][0] for r in rows]
    lons = [r["central"][1] for r in rows]
    return {
        "table_rows": len(rows), "first_row_time": rows[0]["time"],
        "last_row_time": rows[-1]["time"],
        "central_line_points": len(rows),
        "central_line_step_minutes": 2,
        "track_minutes_listed": round(minutes, 1),
        "track_length_km_listed_steps": round(length, 1),
        "mean_shadow_speed_km_s": round(length / (minutes * 60.0), 3),
        "max_duration": {"duration_s": max(durs)[0], "time": max(durs)[1],
                         "central": max(durs)[2]},
        "min_duration": {"duration_s": min(durs)[0], "time": min(durs)[1]},
        "max_width_km": max(widths)[0], "max_width_time": max(widths)[1],
        "max_ratio": max(ratios)[0], "max_ratio_time": max(ratios)[1],
        "max_sun_alt": max(alts)[0], "max_sun_alt_time": max(alts)[1],
        "central_lat_range": [min(lats), max(lats)],
        "central_lon_range": [min(lons), max(lons)],
        "greatest_eclipse": ge, "greatest_duration": gd, "delta_t_page_s": delta_t,
    }


GE = re.compile(r"Greatest Eclipse\s*:\s*(?P<body>Time =.*?Central Duration =\s*\d+m[\d.]+s)")
GD = re.compile(r"Greatest Duration\s*:\s*(?P<body>Time =.*?Central Duration =\s*\d+m[\d.]+s)")
FIELDS = re.compile(r"Time =\s*(?P<time>[\d:.]+)\s*UT.*?"
                    r"Lat =\s*(?P<lat>\d+)(?:&#176;|°)?\s*(?P<latm>[\d.]+)(?:&#39;|′|')?\s*(?P<latH>[NS]).*?"
                    r"Long =\s*(?P<lon>\d+)(?:&#176;|°)?\s*(?P<lonm>[\d.]+)(?:&#39;|′|')?\s*(?P<lonH>[EW]).*?"
                    r"Sun Altitude =\s*(?P<alt>[\d.]+).*?Path Width =\s*(?P<width>[\d.]+)\s*km.*?"
                    r"Sun Azimuth =\s*(?P<azm>[\d.]+).*?Central Duration =\s*"
                    r"(?P<dur>\d+)m(?P<ds>[\d.]+)s", re.S)
DT = re.compile(r"a value of\s*&Delta;T\s*=\s*(?P<v>[\d.]+)\s*seconds", re.S)
SAROS = re.compile(r"Saros\s+(\d+)\s+Table")


def block(rx, raw, tag):
    m = rx.search(raw.replace("\n", " "))
    if not m:
        return None
    f = FIELDS.search(m.group("body"))
    if not f:
        return None
    g = f.groupdict()
    lat = int(g["lat"]) + float(g["latm"]) / 60.0
    lon = int(g["lon"]) + float(g["lonm"]) / 60.0
    return {"tag": tag, "time_ut": g["time"],
            "lat": lat if g["latH"] == "N" else -lat,
            "lon": lon if g["lonH"] == "E" else -lon,
            "lat_hemi": g["latH"], "lon_hemi": g["lonH"],
            "sun_alt": float(g["alt"]), "sun_azm": float(g["azm"]),
            "width_km": float(g["width"]),
            "duration_s": int(g["dur"]) * 60 + float(g["ds"])}


def grab(rx, s):
    m = rx.search(s)
    return m.group(0) if m else None


def main():
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "path_base": "suite_root",
           "source_dir": "tmp/%s/B04/sources" % RID,
           "method": "正则逐行解析中央线表；沿轨长度为相邻中央线点的大圆距离累加（每 2 分钟一点）"}
    pages = {"nasa-path-2024": "SE2024Apr08Tpath.html", "nasa-path-2027": "SE2027Aug02Tpath.html"}
    for key, label in pages.items():
        raw = (SRC / (key + ".html")).read_text(encoding="utf-8", errors="replace")
        rows = parse(key + ".html")
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw))
        ge, gd = block(GE, plain, "greatest_eclipse"), block(GD, plain, "greatest_duration")
        dt = DT.search(plain)
        d = derive(rows, ge, gd, float(dt.group("v")) if dt else None)
        out[key] = {"label": label, "source_file": "sources/%s.html" % key, "rows": rows,
                    "derived": d,
                    "saros_link": SAROS.search(plain).group(1) if SAROS.search(plain) else None,
                    "verbatim": {"greatest_eclipse": grab(GE, plain),
                                 "greatest_duration": grab(GD, plain),
                                 "delta_t_sentence": plain[max(0, dt.start() - 150):dt.end() + 1]
                                 if dt else None}}
    o = OUT / "path-pages.json"
    o.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for k in pages:
        dd = out[k]["derived"]
        print(k, "rows=%d" % dd["table_rows"], "len=%.0f km" % dd["track_length_km_listed_steps"],
              "v=%.3f km/s" % dd["mean_shadow_speed_km_s"], "dT", dd["delta_t_page_s"],
              "GE", dd["greatest_eclipse"], "GD", dd["greatest_duration"])


if __name__ == "__main__":
    main()
