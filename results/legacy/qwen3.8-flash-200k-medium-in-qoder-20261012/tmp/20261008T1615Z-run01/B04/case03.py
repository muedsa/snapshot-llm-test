"""case-03《沙罗：18 年 11 天的复读机》1200x2000。

同一根影子为什么会隔 18 年零 11 天再演一次，又为什么每次都差一点。
用目录里三条真实沙罗系列（139 上升 / 136 下降 / 127 谢幕）的逐次数据说话。
"""
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" /
                       os.environ["SNAPSHOT_RUN_ID"] / "B04"))
import b04kit as B  # noqa: E402

GROUPS = [(139, "成长中：全食越来越长", "ember"),
          (136, "巅峰后退场：全食越来越短", "cyan"),
          (127, "谢幕：本影滑向南极，时长跌到 98 s", "corona")]


def dms(days):
    d = int(days)
    h = int((days - d) * 24)
    m = int(((days - d) * 24 - h) * 60)
    return "%dd %02dh %02dm" % (d, h, m)


def build():
    stats, rows = B.data()
    dv = B.ddata()
    sp = dv["saros_page"]
    lad = dv["saros_ladders"]
    d, tf = B.doc(1200, 2000, "dark")
    B.header(d, tf, "h", "03", "沙罗：18 年 11 天的复读机",
             "同一根影子为什么会再演一次，又为什么每次都差一点", size=46)

    # ---------- ① 三条周期在同一点上相遇 ----------
    B.tlab(d, tf, "p1-t", 72, 222, 1000, 26, "① 三种月份，凑成同一个 6585 天",
           21, d.P["t0"], style="BOLD")
    mult = sp["multiples"]
    names = {"synodic": ("朔望月（新月到新月）", "ember"),
             "draconic": ("交点月（过升交点）", "cyan"),
             "anomalistic": ("近点月（近地点到近地点）", "corona")}
    lo, hi = 6585.0, 6585.6
    bx, bw = 340, 600
    X = lambda v: bx + (v - lo) / (hi - lo) * bw
    B.vrule(d, bx, 258, 168, d.P["t2"], 2)
    B.mono(d, tf, "p1-lo", bx - 4, 430, 90, 20, "6585.0", 14, d.P["t2"], align="START")
    B.mono(d, tf, "p1-hi", bx + bw - 86, 430, 90, 20, "6585.6", 14, d.P["t2"],
           align="END")
    for i, key in enumerate(("synodic", "draconic", "anomalistic")):
        n, days = mult[key]
        y = 268 + i * 52
        lab, col = names[key]
        B.mono(d, tf, "p1-n%d" % i, 72, y, 260, 22, "%d × %s" % (n, lab[:3]), 16,
               d.P[col])
        B.tlab(d, tf, "p1-l%d" % i, 72, y + 22, 260, 20, lab, 13, d.P["t2"])
        d.rect(bx, y + 4, X(days) - bx, 22, d.P[col])
        B.mono(d, tf, "p1-v%d" % i, X(days) + 10, y + 4, 130, 22,
               "%.4f d" % days, 15, d.P["t0"])
    B.tlab(d, tf, "p1-note", 72, 452, 1056, 24,
           "三条都落在 6585 天上下，但彼此差 0.04–0.22 天：复读不是复制，是近似。"
           "（数值取自 NASA 沙罗页原文，非本题推算）", 15, d.P["t1"], lines=1)

    # ---------- ② 三条系列的台阶 ----------
    B.tlab(d, tf, "p2-t", 72, 502, 1000, 26, "② 本世纪里的三次复读：逐次对比",
           21, d.P["t0"], style="BOLD")
    for j, (series, gnote, col) in enumerate(GROUPS):
        y = 544 + j * 232
        d.rect(72, y, 1056, 30, d.P["card"])
        B.mono(d, tf, "p2-g%d" % j, 82, y + 5, 150, 22, "Saros %d" % series, 17,
               d.P[col], style="BOLD")
        B.tlab(d, tf, "p2-gn%d" % j, 240, y + 6, 880, 22, gnote, 15, d.P["t2"])
        for k, m in enumerate(lad[str(series)]):
            yy = y + 38 + k * 31
            B.mono(d, tf, "p2-%d-%d-d" % (j, k), 82, yy, 116, 22, m["date"], 15,
                   d.P["t1"])
            B.mono(d, tf, "p2-%d-%d-g" % (j, k), 206, yy, 84, 22,
                   "+%d d" % m["gap_days"] if m["gap_days"] else "首次", 14,
                   d.P["t2"] if m["gap_days"] else d.P["t2"], align="END")
            lat, lon = m["lat"], m["lon"]
            B.mono(d, tf, "p2-%d-%d-p" % (j, k), 300, yy, 150, 22,
                   "%d°%s %d°%s" % (abs(lat), "N" if lat >= 0 else "S", abs(lon),
                                    "E" if lon >= 0 else "W"), 14, d.P["t2"])
            bwv = 300.0 * m["duration_s"] / 400.0
            d.rect(462, yy + 5, bwv, 12, d.P[col])
            B.mono(d, tf, "p2-%d-%d-t" % (j, k), 462 + bwv + 8, yy, 80, 22,
                   "%d s" % m["duration_s"], 15, d.P["t0"], align="START")
            B.mono(d, tf, "p2-%d-%d-w" % (j, k), 900, yy, 110, 22,
                   "%d km" % m["width_km"], 14, d.P["t2"], align="END")
        B.hrule(d, 72, y + 226, 1056, d.P["border"], 1)
    B.tlab(d, tf, "p2-note", 72, 1246, 1056, 24,
           "条形＝全食最长时长（同一比例，满格 400 s）；间隔一栏是本机把相邻两行日期相减所得。",
           14, d.P["t2"], lines=1)

    # ---------- ③ 每一次往西跳多少 ----------
    y3 = 1292
    B.tlab(d, tf, "p3-t", 72, y3, 1000, 26, "③ 复读为什么换了地方", 21, d.P["t0"],
           style="BOLD")
    steps = []
    mem = lad["139"]
    for a, b in zip(mem, mem[1:]):
        dl = b["lon"] - a["lon"]
        while dl > 180:
            dl -= 360
        while dl < -180:
            dl += 360
        steps.append(dl)
    extra = mult["synodic"][1] - 6585
    pred = extra * 360
    B.tlab(d, tf, "p3-why", 72, y3 + 34, 1056, 24,
           "一个沙罗 = 6585 天 %s，多出的 %.4f 天里地球又自转了 %.1f°，"
           "所以影迹每次向西跳 %.0f° 上下。" % (dms(mult["synodic"][1])[5:], extra,
                                        pred, pred), 16, d.P["t1"], lines=1)
    # Saros 139 的六个食甚点经度，落在 -180..180 的带上
    by0, bh0 = y3 + 78, 140
    d.rect(72, by0, 1056, bh0, d.P["card"])
    ax0, ax1 = 120, 1090
    LX = lambda lo: ax0 + (lo + 180) / 360.0 * (ax1 - ax0)
    d.line(ax0, by0 + 104, ax1, by0 + 104, 1.5, d.P["t2"])
    for v in (-180, -120, -60, 0, 60, 120, 180):
        B.vrule(d, LX(v), by0 + 98, 12, d.P["t2"], 1)
        B.mono(d, tf, "p3-tk%d" % v, LX(v) - 30, by0 + 114, 60, 20, "%d°" % v, 13,
               d.P["t2"], align="CENTER")
    for i, m in enumerate(mem):
        x = LX(m["lon"])
        y = by0 + 28 + i * 12
        d.dot(x, y, 10, d.P["ember"])
        flip = x + 132 > 72 + 1056
        B.mono(d, tf, "p3-m%d" % i, x - 132 if flip else x + 12, y - 9, 120, 18,
               "%s %+d°" % (m["date"][2:7], m["lon"]), 12, d.P["t1"],
               align="END" if flip else "START")
    B.tlab(d, tf, "p3-cap", 84, by0 + 6, 900, 18, "Saros 139 六次食甚点的经度（上→下按时间）",
           13, d.P["t2"])
    ly = by0 + bh0 + 22
    B.hbars(d, tf, "p3s", 72, ly, 560,
            [("%d→%d" % (i + 1, i + 2), abs(s), d.P["cyan"]) for i, s in enumerate(steps)],
            bh=20, gap=6, lab_w=64, vmax=130, fmt=lambda v: "%.0f°" % v, size=13)
    B.keypanel(d, tf, "p3k", 690, ly, 438, "西跳量核对",
               [("理论（0.3223 天 × 360°）", "%.1f°" % pred, None, d.P["corona"]),
                ("实测 5 步区间", "%0.0f° – %0.0f°" % (min(abs(s) for s in steps),
                                                max(abs(s) for s in steps)),
                 None, d.P["t0"]),
                ("日历上的间隔", "6585 d ×122 / 6586 d ×59", None, d.P["t1"])],
               row_h=28, size=15)
    B.tlab(d, tf, "p3-note", 72, ly + 5 * 26 + 6, 560, 24,
           "122/59 是把 224 行相邻同系列日期相减后数出来的。", 13, d.P["t2"], lines=1)

    # ---------- ④ 本世纪的沙罗户口 ----------
    y4 = 1700
    B.tlab(d, tf, "p4-t", 72, y4, 1000, 26, "④ 本世纪的 43 个系列", 21, d.P["t0"],
           style="BOLD")
    hist = stats["saros_members_per_series_hist"]
    B.keypanel(d, tf, "p4k", 72, y4 + 34, 480, "系列清点",
               [("出现过的沙罗系列", str(stats["saros_series_count"]), "个"),
                ("单系列最多成员", max(hist, key=lambda k: int(k)), "次"),
                ("有 6 次成员的系列", str(hist.get("6", 0)), "个"),
                ("系列内步长", "6585 / 6586", "天"),
                ("沙罗理论长度", "%.4f" % mult["synodic"][1], "天")],
               row_h=28, size=15)
    B.hbars(d, tf, "p4h", 600, y4 + 40, 528,
            [("%s 次" % k, hist[k], d.P["ember"] if k in ("5", "6") else d.P["t2"])
             for k in sorted(hist, key=int)],
            bh=18, gap=6, lab_w=70, fmt=lambda v: "%d 个系列" % v, size=14)

    B.footband(d, tf, "f", [
        "来源：NASA Five Millennium Canon 目录（224 行，本机解析）与 Saros 周期页"
        "（三种月份长度、三个倍数天数均为页面原文）。",
        "推算：相邻间隔、经度西跳量、6585/6586 出现次数由本题脚本从目录日期算出。",
        "口径：一个沙罗系列整体跨越约 12–13 个世纪，本世纪只见其一段；"
        "139 在上升、136 在下降、127 接近谢幕，是同一现象的不同阶段。",
    ], size=13)

    info = {"title": "沙罗：18 年 11 天的复读机", "size": [1200, 2000],
            "kind": "周期性/台阶对照",
            "series_shown": [139, 136, 127],
            "westward_steps_139": steps, "predicted_drift_deg": round(pred, 1),
            "observed_step_counts": stats["saros_step_observed_days"],
            "page_literals": sp["multiples"]}
    return d, tf, info
