"""case-04《食季：一年两趟的门》1920x1080。

把 224 行日食表与 228 行月食表合成 452 个事件，按日期聚类出 211 个食季，
量出季内间隔（半个朔望月）、季间间隔（半个食年）与食年本身，
再用页面里的回归年/交点月/恒星月反推交点退行周期。
数据来自 tmp/<run>/B04/research/seasons.json（derive_seasons.py 生成）。
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B04"))
import b04kit as B  # noqa: E402

SOL = {"T": "日全", "A": "日环", "P": "日偏", "H": "日混"}
LUN = {"T": "月全", "P": "月偏", "N": "月半"}


def evname(ev):
    return (SOL if ev["body"] == "S" else LUN)[ev["type"]]


def dt(s):
    y, m, dd = [int(v) for v in s.split("-")]
    return date(y, m, dd)


def seasons_file():
    p = ROOT / "tmp" / RID / "B04" / "research" / "seasons.json"
    return json.loads(p.read_text(encoding="utf-8"))


def build():
    sv = seasons_file()
    mg, so = sv["merged"], sv["solar_only"]
    pl = sv["page_literals"]
    nr = sv["node_regression"]
    d, tf = B.doc(1920, 1080, "dark")
    B.header(d, tf, "h", "04", "食季：一年两趟的门",
             "日食不会单独来——把日食和月食合起来数，就能从表里量出食年的长度", size=40)

    # ---------- ① 2024–2027 实测时间轴 ----------
    y1 = 196
    B.tlab(d, tf, "p1-t", 72, y1, 900, 26, "① 四个年头里的 8 个食季", 21, d.P["t0"],
           style="BOLD")
    lx = 1300
    d.dot(lx + 6, y1 + 13, 9, d.P["ember"])
    B.tlab(d, tf, "p1-lg1", lx + 18, y1 + 3, 134, 20, "日食（全/环/偏）", 14,
           d.P["t1"], lines=1)
    d.dot(lx + 160, y1 + 13, 7, d.P["cyan"])
    B.tlab(d, tf, "p1-lg2", lx + 172, y1 + 3, 134, 20, "月食（全/偏/半影）", 14,
           d.P["t1"], lines=1)
    B.hrule(d, lx + 314, y1 + 7, 16, d.P["corona"], 2)
    B.hrule(d, lx + 314, y1 + 17, 16, d.P["corona"], 2)
    B.tlab(d, tf, "p1-lg3", lx + 338, y1 + 3, 190, 20, "黄线＝食季首尾跨度", 14,
           d.P["t1"], lines=1)
    t0, t1 = date(2024, 1, 1), date(2027, 12, 31)
    span = (t1 - t0).days
    X = lambda day: 72 + (day - t0).days / float(span) * 1776
    band_y, band_h = 300, 36
    d.rect(72, band_y - 8, 1776, band_h + 16, d.P["card"])
    for y in (2024, 2025, 2026, 2027):
        x = X(date(y, 1, 1))
        B.vrule(d, x, band_y - 8, band_h + 16, d.P["border"], 1)
        B.vrule(d, x, band_y + band_h + 16, 8, d.P["t2"], 1)
        B.mono(d, tf, "p1-y%d" % y, x + 6, band_y + band_h + 26, 80, 20, str(y), 14,
               d.P["t2"])
    B.vrule(d, X(t1), band_y - 8, band_h + 16, d.P["border"], 1)
    B.hrule(d, 72, band_y + band_h + 16, 1776, d.P["border"], 1)
    se = sv["seasons_2024_2027"]
    centers = []
    for i, s in enumerate(se):
        a, b = dt(s["start"]), dt(s["end"])
        x0, x1 = X(a), X(b)
        w = max(8.0, x1 - x0)
        d.rect(x0, band_y, w, band_h, d.P["card2"])
        B.hrule(d, x0, band_y - 3, w, d.P["corona"], 2)
        B.hrule(d, x0, band_y + band_h + 1, w, d.P["corona"], 2)
        B.vrule(d, (x0 + x1) / 2.0, band_y - 14, 8, d.P["t2"], 1)
        centers.append((x0 + x1) / 2.0)
        for ev in s["events"]:
            e = dt(ev["date"])
            col = d.P["ember"] if ev["body"] == "S" else d.P["cyan"]
            d.dot(X(e) + 3, band_y + band_h / 2.0, 9 if ev["body"] == "S" else 7, col)
        lab = "·".join(evname(ev) for ev in s["events"])
        B.tlab(d, tf, "p1-s%d-l" % i, (x0 + x1) / 2.0 - 104, band_y - 40, 208, 20, lab,
               13, d.P["t1"], align="CENTER", lines=1)
        B.mono(d, tf, "p1-s%d-d" % i, (x0 + x1) / 2.0 - 104, band_y + band_h + 4, 208,
               18, "%s→%s · %d 天" % (s["start"][5:], s["end"][5:], s["width_days"]),
               12, d.P["t2"], align="CENTER", lines=1)
    for i in range(len(centers) - 1):
        gap = (dt(se[i + 1]["start"]) - dt(se[i]["end"])).days
        B.mono(d, tf, "p1-g%d" % i, (centers[i] + centers[i + 1]) / 2.0 - 60,
               band_y - 40, 120, 20, "相隔 %d 天" % gap, 12, d.P["corona"],
               align="CENTER")
    B.tlab(d, tf, "p1-note", 72, band_y + band_h + 54, 1776, 24,
           "季内两次食相隔 %d–%d 天（半个朔望月，页面值 %.2f÷2=%.2f 天）；"
           "季与季首尾相隔 %d–%d 天（季中心相隔中位 %d 天）。上下两条黄线＝该季首末事件的跨度。" % (
               mg["intra_gap_days"]["min"], mg["intra_gap_days"]["max"],
               pl["moon_synodic_period_days"], pl["moon_synodic_period_days"] / 2,
               min((dt(se[i + 1]["start"]) - dt(se[i]["end"])).days
                   for i in range(len(se) - 1)),
               max((dt(se[i + 1]["start"]) - dt(se[i]["end"])).days
                   for i in range(len(se) - 1)),
               mg["inter_gap_days"]["median"]), 15, d.P["t1"], lines=1)

    # ---------- ② 两个间隔分布 + 常数板 ----------
    y2 = 470
    B.tlab(d, tf, "p2-t", 72, y2, 560, 24, "② 季内：相邻两食相隔几天", 19, d.P["t0"],
           style="BOLD")
    ih = mg["intra_gap_days"]["hist"]
    B.hbars(d, tf, "p2a", 72, y2 + 34, 548,
            [("%s 天" % k, v, d.P["ember"] if k == "15" else d.P["cyan"])
             for k, v in sorted(ih.items(), key=lambda kv: int(kv[0]))],
            bh=26, gap=10, lab_w=76, fmt=lambda v: "%d 次" % v, size=15)
    B.tlab(d, tf, "p2a-n", 72, y2 + 34 + 3 * 36 + 4, 548, 40,
           "241 个季内间隔全部落在 14–16 天：食季里的两次食一定是一新月一满月。",
           13, d.P["t2"], lines=2)

    B.tlab(d, tf, "p2-t2", 660, y2, 560, 24, "② 季间：两季中心相隔", 19, d.P["t0"],
           style="BOLD")
    bins = {int(k): v for k, v in mg["inter_gap_days"]["bins_5d"].items()}
    B.hbars(d, tf, "p2b", 660, y2 + 34, 548,
            [("%d–%d" % (k, k + 4), v,
              d.P["corona"] if k == 175 else d.P["moon"]) for k, v in sorted(bins.items())],
            bh=20, gap=7, lab_w=88, vmax=130, fmt=lambda v: "%d 对" % v, size=14)
    B.tlab(d, tf, "p2b-n", 660, y2 + 34 + 6 * 27 + 4, 548, 40,
           "210 对相邻季：半个食年实测 %.2f 天，比半年（%.1f 天）短 %.1f 天。" % (
               mg["half_eclipse_year_days"], pl["tropical_year_days"] / 2,
               pl["tropical_year_days"] / 2 - mg["half_eclipse_year_days"]),
           13, d.P["t2"], lines=2)

    B.keypanel(d, tf, "p2k", 1250, y2, 598, "页面常数（原文取值）",
               [("回归年", "%.3f" % pl["tropical_year_days"], "天"),
                ("朔望月", "%.2f" % pl["moon_synodic_period_days"], "天"),
                ("恒星月（月球公转周期）", "%.4f" % pl["moon_revolution_period_days"], "天"),
                ("交点月（节点到节点）", "%.6f" % pl["draconic_month_days"], "天"),
                ("食年（本题实测）", "%.2f ± %.2f" % (mg["eclipse_year_days"],
                                                 mg["eclipse_year_std"]), "天")],
               row_h=28, size=15)

    # ---------- ③ 食年 vs 回归年 / 漂移阶梯 / 每年季数 ----------
    y3 = 700
    B.tlab(d, tf, "p3-t", 72, y3, 560, 24, "③ 一年为什么装不下两趟", 19, d.P["t0"],
           style="BOLD")
    lo, hi = 300.0, 400.0
    bx, bw = 200, 420
    XX = lambda v: bx + (v - lo) / (hi - lo) * bw
    rows = [("食年（实测）", mg["eclipse_year_days"], "ember"),
            ("回归年（页面）", pl["tropical_year_days"], "cyan")]
    for i, (lab, v, col) in enumerate(rows):
        yy = y3 + 36 + i * 34
        B.tlab(d, tf, "p3-l%d" % i, 72, yy, 124, 22, lab, 13, d.P["t1"], lines=1)
        d.rect(bx, yy + 4, XX(v) - bx, 18, d.P[col])
        B.mono(d, tf, "p3-v%d" % i, XX(v) + 8, yy, 110, 22, "%.2f d" % v, 14,
               d.P["t0"])
    dxa, dxb = XX(mg["eclipse_year_days"]), XX(pl["tropical_year_days"])
    B.hrule(d, dxa, y3 + 112, dxb - dxa, d.P["corona"], 5)
    B.vrule(d, dxa, y3 + 104, 16, d.P["corona"], 1)
    B.vrule(d, dxb, y3 + 104, 16, d.P["corona"], 1)
    B.mono(d, tf, "p3-dl", (dxa + dxb) / 2.0 - 70, y3 + 128, 140, 20,
           "差 %.2f 天" % -sv["eclipse_year_vs_tropical_year_days"], 13,
           d.P["corona"], align="CENTER")
    B.tlab(d, tf, "p3-diff", bx, y3 + 156, 520, 44,
           "食季每年比日历提前这么多回到同一个月，"
           "约 %.1f 年绕完一整圈。" % nr["from_measured_eclipse_year_years"],
           13, d.P["t2"], lines=2)

    B.tlab(d, tf, "p3-t2", 660, y3, 560, 24, "③ 首季中心落在一年中的哪天", 19,
           d.P["t0"], style="BOLD")
    dr = sv["first_season_center_2001_2025"]
    gx0, gw = 712, 490
    top, hh = y3 + 40, 112
    base = top + hh
    B.hrule(d, gx0, base, gw, d.P["border"], 1)
    for mm, doy, nm in ((1, 1, "1 月"), (4, 91, "4 月"),
                        (7, 182, "7 月"), (10, 274, "10 月")):
        gy = top + (doy - 1) / 365.0 * hh
        B.hrule(d, gx0, gy, gw, d.P["grid"], 1)
        B.tlab(d, tf, "p3-m%d" % mm, 660, gy - 9, 46, 18, nm, 12, d.P["t2"], lines=1)
    step = gw / max(1, len(dr) - 1)
    for i, r in enumerate(dr):
        x = gx0 + i * step
        y = top + (r["doy"] - 1) / 365.0 * hh
        col = d.P["ember"] if r["doy"] < 60 else d.P["cyan"]
        B.vrule(d, x, y, base - y, col, 1)
        d.dot(x, y, 5, col)
        if r["year"] in (2001, 2010, 2020):
            B.mono(d, tf, "p3-w%d" % r["year"], x - 26, base + 8, 52, 18,
                   str(r["year"]), 12, d.P["corona"], align="CENTER")
    B.mono(d, tf, "p3-x1", gx0 + gw - 52, base + 8, 52, 18, "2025", 12, d.P["t2"],
           align="END")
    B.tlab(d, tf, "p3-note2", 660, base + 34, 548, 40,
           "橙点＝年初（食季在 1 月报到）。2001→2010→2020 三次回到 1 月初，"
           "间隔正好 9–10 年：阶梯每年轻一点，绕一圈约 18.6 年。",
           12, d.P["t2"], lines=2)

    B.keypanel(d, tf, "p3k", 1250, y3, 598, "一个世纪里的食季清点",
               [("食季总数（日＋月）", str(mg["season_count"]), "个"),
                ("每季 1 / 2 / 3 个事件", " / ".join(str(v) for k, v in
                                                sorted(mg["events_per_season_hist"].items())),
                 "季"),
                ("一年两季 / 三季", "%d / %d" % (mg["seasons_per_year_hist"]["2"],
                                            mg["seasons_per_year_hist"]["3"]), "年"),
                ("三季年份", "/".join(str(y) for y in
                                mg["years_with_three_seasons"][:4]) + " …", None),
                ("交点退行周期（两条路）", "%.2f / %.2f" % (
                    nr["from_measured_eclipse_year_years"],
                    nr["from_draconic_and_sidereal_years"]), "年")],
               row_h=28, size=15)

    B.footband(d, tf, "f", [
        "来源：NASA Catalog of Solar Eclipses 2001–2100（224 行）与 Catalog of Lunar "
        "Eclipses 2001–2100（228 行，本题新抓并逐行解析，类型计数 85/57/86 与页面自述一致）。",
        "推算：食季由 452 个日期按“相邻 ≤ 40 天”聚类；食年 %.2f 天、退行周期 %.2f 年均为实测反推，"
        "未引用任何未取得原文的常数（Wikipedia 两个候选页面请求超时，已记入 requests.jsonl 且不作为来源）。"
        % (mg["eclipse_year_days"], nr["from_measured_eclipse_year_years"]),
        "口径：季宽用“季内首末事件之差”表示（实测 %d–%d 天），不是天文学上严格的食季边界定义；"
        "2001 年初与 2100 年末的季被世纪截断，故有 1 个单事件季。"
        % (mg["season_width_days"]["min"], mg["season_width_days"]["max"]),
    ], size=13)

    info = {"title": "食季：一年两趟的门", "size": [1920, 1080],
            "kind": "时间轴＋分布＋实测常数",
            "events_used": sv["inputs"]["merged_events"],
            "seasons": mg["season_count"],
            "eclipse_year_measured_days": mg["eclipse_year_days"],
            "eclipse_year_std": mg["eclipse_year_std"],
            "node_regression_years": [nr["from_measured_eclipse_year_years"],
                                      nr["from_draconic_and_sidereal_years"]],
            "seasons_2024_2027": len(se)}
    return d, tf, info
