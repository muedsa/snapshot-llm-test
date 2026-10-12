"""件-06《全食能有多长》1600x1000。

224 条目录里只有 144 条有中心食时长；本页把这份时长摊开看：
分布形状、全食/环食/混合食各自的上限与中位数、逐月上限的季节反向，
以及时长与食带宽度的关系（最宽的带并不最长）。
数据：research/duration.json（derive_duration.py 从 catalog.json 实算）
＋ research/derived.json（本影长度与门槛，来自 NASA 事实页常数）。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B04"))
import b04kit as B  # noqa: E402

MX = 72
W, H = 1600, 1000
RX = 1528


def jload(name):
    return json.loads((ROOT / "tmp" / RID / "B04" / "research" / name).read_text(encoding="utf-8"))


def ms(v):
    m, s = int(v // 60), int(round(v % 60))
    return "%dm%02ds" % (m, s)


def build():
    du = jload("duration.json")
    dv = jload("derived.json")
    g, hist, bm = du["groups"], du["histogram_60s"], du["by_month"]
    d, tf = B.doc(W, H, "dark")
    B.header(d, tf, "h", "06", "全食能有多长",
             "224 次日食里只有 144 条给出中心食时长：分布、上限、以及环食为什么能更长", size=44)

    # ================= ① 直方图 =================
    y0 = 200
    B.tlab(d, tf, "p1-t", MX, y0, 620, 26, "① 中心食时长分布（分箱 60 秒）", 19,
           d.P["t0"], style="BOLD")
    for i, (key, lab) in enumerate((("T", "全食 %d" % g["T"]["n"]),
                                    ("A", "环食 %d" % g["A"]["n"]),
                                    ("H", "混合 %d" % g["H"]["n"]))):
        lx = 700 + i * 86
        B.disc(d, lx + 6, y0 + 12, 5, d.P[{"T": "ember", "A": "cyan", "H": "corona"}[key]])
        B.mono(d, tf, "p1-lg%d" % i, lx + 16, y0 + 3, 70, 20, lab, 12, d.P["t1"])

    px0, px1 = 140, 950
    pyb, pyt = 400, 236
    slot = (px1 - px0) / 12.0
    vmax = 30
    sy = (pyb - pyt) / float(vmax)
    for c in (10, 20, 30):
        yy = pyb - c * sy
        d.rect(px0, yy, px1 - px0, 1, d.P["grid"])
        B.mono(d, tf, "p1-g%d" % c, px0 - 34, yy - 7, 28, 15, str(c), 11, d.P["t2"], align="END")
    B.mono(d, tf, "p1-g%d" % c, px0 - 34, yy - 7, 28, 15, str(c), 11, d.P["t2"], align="END")
    for i, b in enumerate(hist):
        bx = px0 + slot * i + 6
        bw = slot - 14
        ycur = pyb
        for key in ("T", "A", "H"):
            if b[key] == 0:
                continue
            hh = b[key] * sy
            d.rect(bx, ycur - hh, bw, hh, d.P[{"T": "ember", "A": "cyan", "H": "corona"}[key]])
            ycur -= hh
        if b["all"]:
            B.mono(d, tf, "p1-c%d" % i, bx, ycur - 17, bw, 15, str(b["all"]), 12, d.P["t0"],
                   align="CENTER")
        B.mono(d, tf, "p1-x%d" % i, px0 + slot * i - 12, pyb + 8, slot + 24, 15,
               str(b["lo"]), 11, d.P["t2"], align="CENTER")
    d.rect(px0, pyb + 1, px1 - px0, 1.5, d.P["axis"])
    B.tlab(d, tf, "p1-u", px0, pyb + 26, 320, 16, "横轴＝秒（食甚处的中心食时长），纵轴＝次数",
           11, d.P["t2"])
    B.tlab(d, tf, "p1-n", 470, pyb + 26, 480, 16,
           "混合食 7 次全在 0–120 秒；420 秒以上只剩环食（21 次）", 11, d.P["t1"], align="END")

    # ================= ② 上限与中位 =================
    qx = 1000
    B.tlab(d, tf, "p2-t", qx, y0, 300, 26, "② 上限与中位", 19, d.P["t0"], style="BOLD")
    rows = [("全食最长", g["T"]["max_s"], d.P["ember"]),
            ("环食最长", g["A"]["max_s"], d.P["cyan"]),
            ("全食中位", g["T"]["median_s"], "#5A6A86"),
            ("环食中位", g["A"]["median_s"], "#43506B"),
            ("混合最长", g["H"]["max_s"], d.P["corona"])]
    yb = B.hbars(d, tf, "p2-b", qx, y0 + 36, RX - qx, rows, bh=22, gap=7, lab_w=92,
                 vmax=700, fmt=ms, size=14)
    B.tlab(d, tf, "p2-n1", qx, yb + 10, RX - qx, 17,
           "本世纪 20 个最长的中心食全部是环食；全食的上限停在 6m39s。", 12, d.P["t1"])
    sh = du["shortest_overall"][0]
    B.tlab(d, tf, "p2-n2", qx, yb + 32, RX - qx, 17,
           "最短的中心食是 %s 的混合食：只全食 %s，食带宽 %d km。"
           % (sh["date"], ms(sh["dur_s"]), sh["width_km"]), 12, d.P["t1"])

    # ================= ③ 逐月上限 =================
    y2 = 448
    B.tlab(d, tf, "p3-t", MX, y2, 900, 26,
           "③ 各月的上限：上＝当月最长全食，下＝当月最长环食", 19, d.P["t0"], style="BOLD")
    B.tlab(d, tf, "p3-k", 1120, 492, RX - 1120, 20,
           "全食集中在 4–9 月，环食集中在 10–2 月", 12, d.P["t1"], align="END")
    axy = 552
    msy = 0.093
    d.rect(MX, axy, RX - MX, 1.5, d.P["axis"])
    d.rect(MX, axy - 360 * msy, RX - MX, 1, d.P["grid"])
    d.rect(MX, axy + 360 * msy, RX - MX, 1, d.P["grid"])
    B.mono(d, tf, "p3-g1", MX, axy - 360 * msy - 15, 40, 14, "360s", 10, d.P["t2"])
    B.mono(d, tf, "p3-g2", MX, axy + 360 * msy + 1, 40, 14, "360s", 10, d.P["t2"])
    mslot = (RX - MX - 60) / 12.0
    for m in range(1, 13):
        cx = MX + 60 + mslot * (m - 1) + mslot / 2.0
        rec = bm[str(m)]
        bw = 46
        if rec["T"]["max_s"]:
            hh = rec["T"]["max_s"] * msy
            d.rect(cx - bw / 2.0, axy - hh, bw, hh, d.P["ember"])
            B.mono(d, tf, "p3-t%d" % m, cx - 30, axy - hh - 15, 60, 14, ms(rec["T"]["max_s"]),
                   11, d.P["t1"], align="CENTER")
        else:
            d.rect(cx - bw / 2.0, axy - 3, bw, 2, d.P["border"])
            B.tlab(d, tf, "p3-t%d" % m, cx - 24, axy - 20, 48, 15, "无", 11, d.P["t2"],
                   align="CENTER")
        if rec["A"]["max_s"]:
            hh = rec["A"]["max_s"] * msy
            d.rect(cx - bw / 2.0, axy + 1, bw, hh, d.P["cyan"])
            B.mono(d, tf, "p3-a%d" % m, cx - 30, axy + hh + 2, 60, 14, ms(rec["A"]["max_s"]),
                   11, d.P["t1"], align="CENTER")
        B.tlab(d, tf, "p3-m%d" % m, cx - 24, axy + 80, 48, 16, "%d" % m, 13, d.P["t0"],
               align="CENTER")
    B.tlab(d, tf, "p3-md", RX - 66, axy + 80, 66, 16, "月份", 11, d.P["t2"], align="END")

    # ================= ④ 时长 × 带宽 =================
    y3 = 665
    B.tlab(d, tf, "p4-t", MX, y3, 700, 26, "④ 时长 × 食带宽度：最宽的带并不最长", 19,
           d.P["t0"], style="BOLD")
    sx0, sx1 = 140, 850
    syb, syt = 858, 712
    wx, dur_y = (sx1 - sx0) / 800.0, (syb - syt) / 700.0
    for wv in (200, 400, 600):
        d.rect(sx0 + wv * wx, syt, 1, syb - syt, d.P["grid"])
    for tv in (200, 400, 600):
        d.rect(sx0, syb - tv * dur_y, sx1 - sx0, 1, d.P["grid"])
    for p in du["scatter"]:
        cx, cy = sx0 + p["x"] * wx, syb - p["y"] * dur_y
        B.disc(d, cx, cy, 3.2, d.P[{"T": "ember", "A": "cyan", "H": "corona"}[p["t"]]])
    for p in du["widest"]["T"]:
        cx, cy = sx0 + p["width_km"] * wx, syb - p["dur_s"] * dur_y
        B.ring(d, cx, cy, 6.5, 1.5, "#EFE6D3")
    d.rect(sx0, syb + 1, sx1 - sx0, 1.5, d.P["axis"])
    d.rect(sx0 - 1, syt, 1.5, syb - syt, d.P["axis"])
    for wv in (0, 200, 400, 600):
        B.mono(d, tf, "p4-x%d" % wv, sx0 + wv * wx - 30, syb + 6, 60, 14, str(wv), 11,
               d.P["t2"], align="CENTER")
    for tv in (0, 200, 400, 600):
        B.mono(d, tf, "p4-y%d" % tv, sx0 - 36, syb - tv * dur_y - 7, 30, 14, str(tv), 11,
               d.P["t2"], align="END")
    B.mono(d, tf, "p4-xu", sx1 - 26, syb + 6, 26, 14, "km", 11, d.P["t2"])
    B.mono(d, tf, "p4-yu", sx0 - 40, syt - 17, 34, 14, "秒", 11, d.P["t2"])
    B.mono(d, tf, "p4-r1", sx1 - 200, syt + 26, 200, 16, "全食 r = %+.2f" % du["corr_T"]["r"],
           12, d.P["ember"], align="END")
    B.mono(d, tf, "p4-r2", sx1 - 200, syt + 44, 200, 16, "环食 r = %+.2f" % du["corr_A"]["r"],
           12, d.P["cyan"], align="END")
    B.tlab(d, tf, "p4-n", 444, y3 + 3, 406, 22,
           "白圈＝最宽的三次全食（781/732/559 km）＝157/193/157 秒", 12, d.P["t1"])

    # ================= ⑤ 门槛几何 =================
    gx = 900
    B.tlab(d, tf, "p5-t", gx, y3, RX - gx, 26, "⑤ 上限从何而来：影轴够不够得着地面", 19,
           d.P["t0"], style="BOLD")
    um, ap = dv["umbral_length_vs_sun_distance"], dv["apex_margin_at_mean_sun"]
    B.tlab(d, tf, "p5-a", gx, y3 + 27, RX - gx, 34,
           "本影长 L 随日地距离在 %s–%s km 间摆动 %s km；影轴要落地，月心距须不超过 "
           "L + r_earth = %s–%s km。" % (B.km(um["min"]["umbral_length_km"]),
                                        B.km(um["max"]["umbral_length_km"]),
                                        B.km(um["max"]["umbral_length_km"]
                                             - um["min"]["umbral_length_km"]),
                                        B.km(um["min"]["touch_threshold_moon_dist_km"]),
                                        B.km(um["max"]["touch_threshold_moon_dist_km"])),
           12, d.P["t1"], lines=2)
    B.tlab(d, tf, "p5-b", gx, 730, RX - gx, 17,
           "环食的上限来自伪本影：锥顶之后影子重新变宽，越远越宽，所以能到 11m08s。",
           12, d.P["corona"])
    ax0, ax1 = gx + 30, RX
    lo, hi = 358000.0, 408000.0
    kx = (ax1 - ax0) / (hi - lo) * 1000.0
    axy5 = 800

    def mx(dist):
        return ax0 + (dist - lo) / 1000.0 * kx

    d.rect(ax0, axy5, ax1 - ax0, 1.5, d.P["axis"])
    band_a, band_b = mx(um["min"]["touch_threshold_moon_dist_km"]), \
        mx(um["max"]["touch_threshold_moon_dist_km"])
    d.rect(band_a, 770, band_b - band_a, 30, "#1C2A4A")
    thr = mx(um["mean"]["touch_threshold_moon_dist_km"])
    B.vrule(d, thr, 768, 32, d.P["corona"], 1)
    B.mono(d, tf, "p5-thr", thr - 100, 750, 200, 14,
           "门槛带 %s–%s" % (B.km(um["min"]["touch_threshold_moon_dist_km"]),
                            B.km(um["max"]["touch_threshold_moon_dist_km"])), 10, d.P["corona"],
           align="CENTER")
    B.mono(d, tf, "p5-axu", gx, 776, 90, 14, "月心距 km", 10, d.P["t2"])
    B.mono(d, tf, "p5-ax0", ax0, axy5 + 6, 60, 14, B.km(lo), 10, d.P["t2"])
    B.mono(d, tf, "p5-ax1", RX - 60, axy5 + 6, 60, 14, B.km(hi), 10, d.P["t2"], align="END")
    marks = [("近地点", "perigee", "ember", "全食"), ("平均距", "mean", "cyan", "临界"),
             ("远地点", "apogee", "cyan", "环食")]
    for name, key, col, verdict in marks:
        mk = ap[key]
        cx = mx(mk["moon_dist_km"])
        B.disc(d, cx, axy5, 6, d.P[col])
        bx = min(max(cx - 65, ax0), RX - 130)
        mv = mk["margin_to_surface_km"]
        B.tlab(d, tf, "p5-%s-1" % key, bx, axy5 + 26, 130, 15,
               "%s·%s" % (name, verdict), 11, d.P[col], align="CENTER")
        B.mono(d, tf, "p5-%s-2" % key, bx, axy5 + 42, 130, 15, B.km(mk["moon_dist_km"]), 11,
               d.P["t0"], align="CENTER")
        B.mono(d, tf, "p5-%s-3" % key, bx, axy5 + 58, 130, 15,
               "%s%s km" % ("+" if mv > 0 else "−", B.km(abs(mv))), 11, d.P["t1"], align="CENTER")

    B.footband(d, tf, "f", [
        "来源：NASA Catalog of Solar Eclipses 2001–2100（224 行逐行解析）；日地距离、月心距范围、"
        "半径与本影常数取 NASA 太阳／地球／月球事实页；2024、2027 路径页用于时长交叉校验。",
        "推算：直方图、极值榜、逐月上限与相关系数由 derive_duration.py 从同一张表实算。"
        "144 条有中心食时长，77 条 P 与 3 条 t-（中心线不落地）不计入。",
        "解释：全食上限集中在 4–9 月、环食集中在 10–2 月，与本影长度随日地距离变化一致"
        "（近日点黄经 102.947°→ 太阳视黄经 282.9°，即 1 月初）。这条因果是我的推算。",
        "限制：服务无矢量 path，柱、点、白圈由矩形与扫描线逼近；分箱 60 秒是选定参数，只改变外观；"
        "表内时长是食甚处的上限值，食带内任意地点看到的都更短。",
    ], size=12)

    info = {"title": "全食能有多长", "size": [W, H],
            "kind": "直方图＋上限条＋逐月上限＋时长×带宽散点＋门槛几何",
            "rows_total": du["rows_total"], "rows_central": du["rows_central"],
            "groups": {k: g[k]["n"] for k in g},
            "max_total_s": g["T"]["max_s"], "max_annular_s": g["A"]["max_s"],
            "top20_types": du["top20_types"],
            "corr_T": du["corr_T"]["r"], "corr_A": du["corr_A"]["r"],
            "histogram_bin_s": 60}
    return d, tf, info
