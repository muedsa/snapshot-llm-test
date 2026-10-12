"""case-05《一次日食的档案页：2024-04-08》1240x1754。

把目录里的第 09561 行与 NASA 食带路径页的 100 行中央线表对起来看：
同一次全食在两个页面给出的时刻为什么差 3.4 秒、食带在地面上怎么走、
沿轨时长/带宽/直径比怎么变。数据来自 research/path-pages.json（parse_path.py）
与 research/catalog.json、research/derived.json。
"""
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B04"))
import b04kit as B  # noqa: E402

DATE = "2024-04-08"
MX, CW = 72, 1096


def jload(name):
    return json.loads((ROOT / "tmp" / RID / "B04" / "research" / name).read_text(encoding="utf-8"))


def haversine(a, b):
    la1, lo1, la2, lo2 = [math.radians(v) for v in (a[0], a[1], b[0], b[1])]
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def secs(hhmmss):
    parts = str(hhmmss).split(":")
    v = int(parts[0]) * 3600 + float(parts[1]) * 60
    return v + float(parts[2]) if len(parts) > 2 else v


def build():
    pp = jload("path-pages.json")["nasa-path-2024"]
    rows = pp["rows"]
    dv = pp["derived"]
    cat = [r for r in jload("catalog.json")["rows"] if r["date"] == DATE][0]
    xchk = [c for c in jload("derived.json")["delta_t"]["crosscheck"] if c["date"] == DATE][0]
    timed = [r for r in rows if not r["is_limits"]]
    segs = [(haversine(a["central"], b["central"]), b["time"])
            for a, b in zip(rows, rows[1:])]
    length = sum(s[0] for s in segs)
    step_v = [haversine(a["central"], b["central"]) / 120.0 for a, b in zip(timed, timed[1:])]
    d, tf = B.doc(1240, 1754, "dark")
    B.header(d, tf, "h", "05", "一次日食的档案页", "2024-04-08 全食：目录里的一行 ＋ 路径页的 100 行，"
             "对起来才知道差在哪", size=46)

    # ---------- ① 档案头 ----------
    y1 = 214
    B.tlab(d, tf, "p1-t", MX, y1, CW, 24, "① 档案头：目录第 09561 行原文", 19, d.P["t0"],
           style="BOLD")
    d.rect(MX, y1 + 32, CW, 40, d.P["card"])
    B.mono(d, tf, "p1-raw", MX + 12, y1 + 43, CW - 24, 20, cat["raw"], 14, d.P["t1"])
    cells = [("目录号", "%05d" % cat["catalog_number"], "ember"),
             ("类型", "全食 T", "ember"), ("沙罗系列", "%d" % cat["saros"], "cyan"),
             ("月龄", "%d" % cat["lunation"], "cyan"),
             ("γ / 食分", "%.4f / %.4f" % (cat["gamma"], cat["magnitude"]), "corona"),
             ("最长全食", "%d s" % cat["central_duration_s"], "corona")]
    cw = CW / float(len(cells))
    for i, (lab, val, col) in enumerate(cells):
        x = MX + i * cw
        B.vrule(d, x, y1 + 84, 56, d.P["border"], 1)
        B.tlab(d, tf, "p1-c%d-l" % i, x + 10, y1 + 90, cw - 20, 18, lab, 12, d.P["t2"],
               lines=1)
        B.mono(d, tf, "p1-c%d-v" % i, x + 10, y1 + 110, cw - 20, 26, val, 18, d.P[col])
    B.tlab(d, tf, "p1-n", MX, y1 + 146, CW, 20,
           "字段顺序：序号 日期 食甚 TD  ΔT  月龄 沙罗 类型 非中心标志 γ 食分 纬度 经度 太阳高度 带宽 最长时长。",
           13, d.P["t2"], lines=1)

    # ---------- ② 两个页面的时刻对账 ----------
    y2 = 400
    B.tlab(d, tf, "p2-t", MX, y2, CW, 24, "② 同一个瞬间，两条来路", 19, d.P["t0"],
           style="BOLD")
    routes = [("路径页", "%.1f s" % dv["delta_t_page_s"], xchk["path_page_greatest_ut"],
               "18:18:28.9", "ember"),
              ("目录页", "%d s" % cat["delta_t_catalog_s"], "18:17:15.0",
               cat["greatest_td"], "cyan")]
    for i, (src, dtv, ut, td, col) in enumerate(routes):
        yy = y2 + 36 + i * 34
        d.chip(MX, yy, 74, 24, src, d.P["t0"], d.P["card2"], size=13)
        B.mono(d, tf, "p2-a%d" % i, MX + 86, yy + 1, 210, 22, "%s UT" % ut, 15, d.P[col])
        B.mono(d, tf, "p2-b%d" % i, MX + 300, yy + 1, 130, 22, "ΔT = %s" % dtv, 15,
               d.P["t1"])
        B.mono(d, tf, "p2-c%d" % i, MX + 436, yy + 1, 150, 22, "→ %s TD" % td, 15,
               d.P["t0"])
    ax0, ax1 = MX + 620, MX + CW
    lo, hi = secs("18:17:14"), secs("18:17:20")
    XX = lambda s: ax0 + (s - lo) / (hi - lo) * (ax1 - ax0)
    B.hrule(d, ax0, y2 + 52, ax1 - ax0, d.P["border"], 1)
    for k in range(7):
        v = lo + k
        B.vrule(d, XX(v), y2 + 48, 8, d.P["t2"], 1)
        B.mono(d, tf, "p2-tk%d" % k, XX(v) - 22, y2 + 60, 44, 16, "%ds" % (14 + k), 11,
               d.P["t2"], align="CENTER")
    for i, (src, dtv, ut, td, col) in enumerate(routes):
        x = XX(secs(ut))
        B.vrule(d, x, y2 + 30, 22, d.P[col], 2)
        B.mono(d, tf, "p2-m%d" % i, x - 60, y2 + 12, 120, 16, ut, 12, d.P[col],
               align="CENTER")
    xa, xb = XX(secs(routes[1][2])), XX(secs(routes[0][2]))
    B.hrule(d, xa, y2 + 84, xb - xa, d.P["corona"], 4)
    B.mono(d, tf, "p2-diff", xa, y2 + 92, xb - xa + 200, 20,
           "UT 相差 %.1f 秒" % (secs(routes[0][2]) - secs(routes[1][2])), 13,
           d.P["corona"])
    B.tlab(d, tf, "p2-n", MX, y2 + 124, CW, 44,
           "两页的 TD 其实对得上：路径页 %s UT ＋ %.1f s ＝ 18:18:28.9，与目录 %s 只差 0.1 秒；"
           "对不上的是 ΔT——目录取 %d s、路径页取 %.1f s，差 %.1f 秒，于是反推的 UT 差了同样的 %.1f 秒。"
           "本世纪目录的 ΔT 列从 %d 到 %d 秒（整秒估值），路径页随预测附一个具体值。" % (
               xchk["path_page_greatest_ut"], dv["delta_t_page_s"], cat["greatest_td"],
               cat["delta_t_catalog_s"], dv["delta_t_page_s"],
               cat["delta_t_catalog_s"] - dv["delta_t_page_s"],
               cat["delta_t_catalog_s"] - dv["delta_t_page_s"],
               jload("derived.json")["delta_t"]["catalog_range_s"][0],
               jload("derived.json")["delta_t"]["catalog_range_s"][1]),
           13, d.P["t1"], lines=3)

    # ---------- ③ 食带轨迹 ----------
    y3 = 600
    B.tlab(d, tf, "p3-t", MX, y3, CW, 24, "③ 本影在地面上走过的 100 个点", 19, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "p3-lg0", 700, y3 + 2, 226, 20, "表内每 2 分钟一行", 12, d.P["t2"],
           align="END")
    d.line(940, y3 + 12, 958, y3 + 12, 2, d.P["corona"])
    B.tlab(d, tf, "p3-lg1", 964, y3 + 2, 52, 20, "中央线", 12, d.P["t2"], lines=1)
    d.line(1024, y3 + 12, 1042, y3 + 12, 2, d.P["ember"])
    B.tlab(d, tf, "p3-lg2", 1048, y3 + 2, 52, 20, "南北界", 12, d.P["t2"], lines=1)
    mx0, mx1 = MX, MX + CW
    my0, my1 = y3 + 34, y3 + 470
    lon_lo, lon_hi = -162.0, -16.0
    lat_lo, lat_hi = -12.0, 52.0
    PX = lambda lon: mx0 + (lon - lon_lo) / (lon_hi - lon_lo) * (mx1 - mx0)
    PY = lambda lat: my1 - (lat - lat_lo) / (lat_hi - lat_lo) * (my1 - my0)
    d.rect(mx0, my0, mx1 - mx0, my1 - my0, d.P["card"])
    for lon in range(-160, -15, 20):
        d.line(PX(lon), my0, PX(lon), my1, 1, d.P["grid"])
        B.mono(d, tf, "p3-x%d" % lon, PX(lon) - 30, my1 + 6, 60, 16, "%d°W" % -lon, 11,
               d.P["t2"], align="CENTER")
    for lat in range(-10, 51, 10):
        d.line(mx0, PY(lat), mx1, PY(lat), 1, d.P["grid"])
        B.mono(d, tf, "p3-y%d" % lat, mx0 - 44, PY(lat) - 8, 40, 16,
               "%d°N" % lat if lat >= 0 else "%d°S" % -lat, 11, d.P["t2"], align="END")
    both = [r for r in rows if r["north"] and r["south"]]
    for i in range(0, len(both) - 2, 2):
        a, b = both[i], both[i + 2]
        B.poly(d, [(PX(a["north"][1]), PY(a["north"][0])),
                   (PX(b["north"][1]), PY(b["north"][0])),
                   (PX(b["south"][1]), PY(b["south"][0])),
                   (PX(a["south"][1]), PY(a["south"][0]))], d.P["card2"], step=3.0)
    for key, col in (("north", "ember"), ("south", "ember"), ("central", "corona")):
        pts = [(PX(r[key][1]), PY(r[key][0])) for r in both[::2]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            d.line(x0, y0, x1, y1, 2 if key == "central" else 1.4, d.P[col])
    for r in both[::5]:
        d.dot(PX(r["central"][1]), PY(r["central"][0]), 4, d.P["t0"])
    for r in both:
        if r["time"] in ("17:00", "17:30", "18:00", "18:30", "19:00", "19:30"):
            B.mono(d, tf, "p3-tm%s" % r["time"].replace(":", ""),
                   PX(r["central"][1]) - 66, PY(r["central"][0]) - 22, 60, 16, r["time"],
                   11, d.P["t1"], align="END")
    ge, gd = dv["greatest_eclipse"], dv["greatest_duration"]
    for tag, p, col, dx, dy in (("ge", ge, "ember", -186, -30), ("gd", gd, "cyan", 14, 12)):
        x, y = PX(p["lon"]), PY(p["lat"])
        d.dot(x, y, 11, d.P[col])
        d.dot(x, y, 5, d.P["card"])
        B.mono(d, tf, "p3-%s" % tag, x + dx, y + dy, 176, 18,
               "%s %s UT" % ("食甚 GE" if tag == "ge" else "最长 GD", p["time_ut"]), 12,
               d.P[col])
    en, ex = rows[0]["central"], rows[-1]["central"]
    for tag, p, dy in (("in", en, 22), ("out", ex, -34)):
        x, y = PX(p[1]), PY(p[0])
        B.ring(d, x, y, 7, 1.6, d.P["t1"])
        B.mono(d, tf, "p3-%s" % tag, x - (168 if tag == "out" else 0), y + dy, 160, 18,
               "%s %.1f° %s" % ("影轴进入" if tag == "in" else "影轴离开", abs(p[0]),
                                "S" if p[0] < 0 else "N"), 12, d.P["t1"],
               align="END" if tag == "out" else "START")
    B.tlab(d, tf, "p3-n", MX, my1 + 28, CW, 40,
           "等经纬网格、不是地图投影：横向 %d° 经度、纵向 %d° 纬度，同一像素在两头代表的实地距离不同，"
           "带形因此被拉伸。宽度条带按页面给的南北界逐段填色（服务无矢量 path，用扫描线矩形拼）。" % (
               int(lon_hi - lon_lo), int(lat_hi - lat_lo)),
           12, d.P["t2"], lines=2)

    # ---------- ④ 沿轨三条剖面 ----------
    y4 = 1160
    B.tlab(d, tf, "p4-t", MX, y4, CW, 24, "④ 沿轨三个量怎么变", 19, d.P["t0"], style="BOLD")
    profs = [("全食时长（中央线）", [r["duration_s"] for r in rows], "ember", "%d s"),
             ("食带宽度", [r["width_km"] for r in rows], "cyan", "%d km"),
             ("月／日直径比", [r["diameter_ratio"] for r in rows], "corona", "%.3f")]
    for i, (lab, vals, col, fmt) in enumerate(profs):
        py0 = y4 + 34 + i * 96
        B.tlab(d, tf, "p4-l%d" % i, MX, py0, 210, 20, lab, 14, d.P["t1"], lines=1)
        gx0, gx1 = MX + 230, MX + CW
        gy0, gy1 = py0 - 6, py0 + 58
        v0, v1 = min(vals), max(vals)
        VX = lambda k: gx0 + k / float(len(vals) - 1) * (gx1 - gx0)
        VY = lambda v: gy1 - (v - v0) / (v1 - v0) * (gy1 - gy0)
        B.hrule(d, gx0, gy1 + 4, gx1 - gx0, d.P["border"], 1)
        pts = [(VX(k), VY(v)) for k, v in enumerate(vals)]
        for (x0, yy0), (x1, yy1) in zip(pts, pts[1:]):
            d.line(x0, yy0, x1, yy1, 2, d.P[col])
        ki, kj = vals.index(v0), vals.index(v1)
        B.mono(d, tf, "p4-min%d" % i, min(max(VX(ki) - 40, MX), MX + CW - 140), gy1 + 8,
               140, 16, "最小 " + (fmt % v0), 11, d.P["t2"])
        B.mono(d, tf, "p4-max%d" % i, min(max(VX(kj) - 90, MX), MX + CW - 140), gy0 - 14,
               140, 16, "最大 " + (fmt % v1), 11, d.P["t2"])
        d.line(VX(ki), gy1 + 4, VX(ki), gy0, 1, d.P["grid"])
        d.line(VX(kj), gy1 + 4, VX(kj), gy0, 1, d.P["grid"])
        kge = [k for k, r in enumerate(rows) if r["time"] == "18:18"][0]
        d.line(VX(kge), gy1 + 4, VX(kge), gy0 - 4, 1.6, d.P["t0"])
        B.mono(d, tf, "p4-ge%d" % i, VX(kge) + 4, gy0 - 14, 60, 16, "GE", 11, d.P["t0"])
    B.tlab(d, tf, "p4-n", MX, 1470, CW, 20,
           "横轴＝表内 100 行的先后（16:36 影轴进入 → 19:56 离开），白线＝食甚 GE 所在行。",
           12, d.P["t2"], lines=1)

    # ---------- ⑤ 沿轨的账 ----------
    y5 = 1506
    B.keypanel(d, tf, "p5k", MX, y5, 520, "沿轨的账（由 100 点现算）",
               [("相邻点大圆距离累加", format(int(round(length)), ","), "km"),
                ("表列时间跨度", "%d" % round((secs(timed[-1]["time"])
                                                - secs(timed[0]["time"])) / 60 + 2), "min"),
                ("平均影速", "%.3f" % (length / ((secs(timed[-1]["time"] + ".0")
                                              - secs(timed[0]["time"] + ".0")) + 120)), "km/s"),
                ("单步最快 / 最慢", "%.2f / %.2f" % (max(step_v), min(step_v)), "km/s"),
                ("单步中位", "%.3f" % sorted(step_v)[len(step_v) // 2], "km/s")],
               row_h=26, size=14)
    B.tlab(d, tf, "p5-n", MX + 548, y5 + 34, CW - 548, 140,
           "目录行与路径页在四个量上互相核对：最长时长 %d s（页 %.1f s）、带宽 %d km（页 %.1f km）、"
           "食甚点 %d°N %d°W（页 %.1f°N %.1f°W）、太阳高度 %d°（页 %.1f°）。"
           "差值都来自目录按整数记录、路径页给到小数，本题不挑好看的哪个。"
           "单步影速两端最大（16:40→16:42 那段 %.2f km/s、临出口 %.2f km/s）、"
           "中段最慢（18:10–18:16 只有 %.2f km/s），是影轴落地/升起处的几何拉伸，不是抄错。" % (
               cat["central_duration_s"], ge["duration_s"], cat["path_width_km"], ge["width_km"],
               cat["lat"], abs(cat["lon"]), ge["lat"], abs(ge["lon"]),
               cat["sun_altitude_deg"], ge["sun_alt"], max(step_v),
               haversine(timed[-2]["central"], timed[-1]["central"]) / 120.0, min(step_v)),
           13, d.P["t1"], lines=7)

    B.footband(d, tf, "f", [
        "来源：NASA Catalog of Solar Eclipses 2001–2100 第 09561 行（原文见 ①），"
        "与 Path of the Total Solar Eclipse of 2024 Apr 08（100 行中央线表 ＋ GE/GD 两段原文）。",
        "推算：沿轨长度、平均影速、单步极值由本题把相邻中央线点做大圆距离累加再除以 120 秒得到；"
        "ΔT 对账用两页各自的值，未引入第三方常数。",
        "限制：页面自述预测未计入月面山脉环形山（limb profile），南北界可能因此偏 1–3 km、"
        "时长偏 1–3 s；地名、时区与各地可见时刻不在本页数据内，本图只画坐标与量值。",
    ], size=12)

    info = {"title": "一次日食的档案页：2024-04-08", "size": [1240, 1754],
            "kind": "档案卡＋时刻对账＋食带轨迹＋沿轨剖面",
            "catalog_row": cat["raw"], "path_table_rows": len(rows),
            "track_length_km": round(length, 1),
            "mean_shadow_speed_km_s": round(length / ((secs(timed[-1]["time"] + ".0")
                                                       - secs(timed[0]["time"] + ".0")) + 120), 3),
            "step_speed_range": [round(min(step_v), 3), round(max(step_v), 3)],
            "deltat_discrepancy_s": cat["delta_t_catalog_s"] - dv["delta_t_page_s"]}
    return d, tf, info
