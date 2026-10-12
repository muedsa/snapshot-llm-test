"""case-01《本影锥够不够得到地面》1600x1200。

一个问题：月球挡住太阳的那根尖锥，长度到底够不够落到地面上？
够着＝全食，差一点＝环食。用 NASA 三份数据表里的常数推出锥长，
再把它和月球的三个典型距离放在同一把 km 尺上比。
"""
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" /
                       os.environ["SNAPSHOT_RUN_ID"] / "B04"))
import b04kit as B  # noqa: E402


def build():
    stats, rows = B.data()
    dv = B.ddata()
    C, G, U = stats["constants"], stats["geometry"], dv["umbral_length_vs_sun_distance"]
    L_mean = U["mean"]["umbral_length_km"]
    thr = {k: U[k]["touch_threshold_moon_dist_km"] for k in U}
    mg = dv["apex_margin_at_mean_sun"]
    half_ang = dv["umbral_half_angle_deg"]

    d, tf = B.doc(1600, 1200, "dark")
    B.header(d, tf, "h", "01", "本影锥够不够得到地面",
             "挡住太阳的那根影子有多长，决定了地上的你看到的是全食还是一圈火环")

    # ---------- ① 月距尺 ----------
    P1 = "p1"
    B.tlab(d, tf, P1 + "-t", 72, 236, 900, 26, "① 月心到地心的距离（km）",
           21, d.P["t0"], style="BOLD")
    xa, xb = 100, 1400
    k0, k1 = 350000, 410000
    sx = (xb - xa) / (k1 - k0)
    X = lambda km_: xa + (km_ - k0) * sx
    yax = 400
    band_y0, band_y1 = 300, 414

    # 门槛带：日地距离在一年里变化，锥长跟着变，"够得着"的门槛也会移动
    b_left, b_right = min(thr.values()), max(thr.values())
    d.rect(X(b_left), band_y0, X(b_right) - X(b_left), band_y1 - band_y0, d.P["card2"])
    B.vrule(d, X(b_left), band_y0, band_y1 - band_y0, d.P["border"], 1)
    B.vrule(d, X(b_right), band_y0, band_y1 - band_y0, d.P["border"], 1)
    B.tlab(d, tf, P1 + "-band", X(b_left) + 8, 306, X(b_right) - X(b_left) - 16, 20,
            "门槛移动区间", 14, d.P["t2"])

    d.line(xa, yax, xb, yax, 2, d.P["t2"])
    B.ticks(d, xa, yax - 12, xb - xa, 12, d.P["t2"], major_every=2,
            major_h=12, minor_h=6, tf=tf, tag=P1 + "-tick", lsize=13,
            labels=[B.km(k) for k in range(k0, k1 + 1, 10000)], label_dy=14)

    # 三个典型月距（上方标注）
    mk = [("近地点", C["lunar_perigee_10_6_km"] * 1e6, d.P["cyan"]),
          ("平均", C["lunar_semimajor_axis_10_6_km"] * 1e6, d.P["t0"]),
          ("远地点", C["lunar_apogee_10_6_km"] * 1e6, d.P["t2"])]
    for i, (lab, kmv, col) in enumerate(mk):
        x = X(kmv)
        B.vrule(d, x, 292, yax - 292 + 12, col, 2)
        d.dot(x, yax, 9, col)
        B.tlab(d, tf, "%s-mk%d" % (P1, i), x - 78, 250, 156, 20, lab, 15, col,
               align="CENTER")
        B.mono(d, tf, "%s-mkv%d" % (P1, i), x - 78, 268, 156, 20, B.km(kmv), 15, col,
               align="CENTER")

    # 三条门槛线（下方标注）
    for i, (lab, kmv, col) in enumerate(
            [("", thr["min"], d.P["t2"]), ("", thr["mean"], d.P["ember"]),
             ("", thr["max"], d.P["t2"])]):
        x = X(kmv)
        B.vrule(d, x, yax, 24, col, 3 if i == 1 else 2)
        B.mono(d, tf, "%s-thv%d" % (P1, i), x - 60, yax + 48, 120, 20, B.km(kmv), 15,
               col, align="CENTER")
    B.tlab(d, tf, P1 + "-thr", 72, yax + 78, 1456, 22,
           "门槛 = 本影长度 + 地球半径，随日地距离在 %s–%s km 之间移动；"
           "平均日距下为 %s km（本影 %s + 地球半径 %s）。"
           % (B.km(b_left), B.km(b_right), B.km(thr["mean"]), B.km(L_mean),
              B.km(int(round(C["earth_equatorial_radius_km"])))),
           16, d.P["t1"], lines=1)
    B.tlab(d, tf, P1 + "-read", 72, yax + 104, 1456, 22,
           "月距落在门槛左侧 → 影子够得着地面（全食）；落在右侧 → 尖锥停在半空（环食）。"
           "平均月距 384,400 恰好在右侧 3,333 km 处，图上只有 16 px。",
           16, d.P["t1"], lines=1)
    # 3,333 km 太小，用引线把这段差拉出来指给读者
    xt, xm = X(thr["mean"]), X(mg["mean"]["moon_dist_km"])
    d.line(xt, 344, xm, 344, 1, d.P["corona"])
    d.line(xt, 344, xt, yax, 1, d.P["corona"])
    B.mono(d, tf, P1 + "-gap", xm + 12, 334, 190, 20, "差 3,333 km", 15, d.P["corona"],
           align="START")

    # ---------- ② 以"恰好触地"为 0 的余量条 ----------
    P2 = "p2"
    B.tlab(d, tf, P2 + "-t", 72, 566, 900, 26, "② 尖锥端口与地面的差距（km）",
           21, d.P["t0"], style="BOLD")
    x0, s2 = 600, 0.020
    top2, bot2 = 606, 962
    d.rect(x0, top2, 1000 - x0, bot2 - top2, d.P["card2"])
    B.tlab(d, tf, P2 + "-earth", x0 + 16, top2 + 10, 360, 22, "地球这一侧：尖端落在地下",
           15, d.P["t2"])
    B.vrule(d, x0, top2 - 14, bot2 - top2 + 28, d.P["corona"], 3)
    B.mono(d, tf, P2 + "-zero", x0 - 34, bot2 + 16, 68, 20, "0", 15, d.P["corona"],
           align="CENTER")
    for v in (-20000, -10000, 10000, 20000):
        xx = x0 + v * s2
        B.vrule(d, xx, bot2, 10, d.P["t2"], 1)
        B.mono(d, tf, "%s-tk%d" % (P2, v), xx - 46, bot2 + 16, 92, 20,
               ("+" if v > 0 else "−") + B.km(abs(v)), 14, d.P["t2"], align="CENTER")

    order = [("perigee", "近地点 363,300 km", d.P["ember"], "全食：本影砸在地面上"),
             ("mean", "平均距离 384,400 km", d.P["cyan"], "环食：差 3,333 km 没碰到"),
             ("apogee", "远地点 405,500 km", d.P["cyan"], "环食：差 24,433 km")]
    for i, (key, lab, col, verdict) in enumerate(order):
        y = 646 + i * 118
        m = mg[key]["margin_to_surface_km"]
        xa2 = x0 + m * s2
        sgn = 1 if m > 0 else -1
        B.tlab(d, tf, "%s-lb%d" % (P2, i), 72, y - 34, 300, 22, lab, 16, d.P["t0"],
               style="BOLD")
        # 从 0（地表）画到尖端所在处；三角形头＝影锥端口，只作符号不作比例
        d.rect(min(x0, xa2), y - 7, abs(xa2 - x0), 14, col)
        B.poly(d, [(xa2, y), (xa2 - 30 * sgn, y - 11), (xa2 - 30 * sgn, y + 11)],
               col, step=2.0)
        d.dot(xa2, y, 9, d.P["t0"])
        B.mono(d, tf, "%s-val%d" % (P2, i), 1012, y - 11, 118, 24,
               ("+" if m > 0 else "−") + B.km(abs(m)), 19, col, align="START")
        B.tlab(d, tf, "%s-vd%d" % (P2, i), 72, y + 26, 460, 20, verdict, 15, d.P["t1"])

    B.tlab(d, tf, P2 + "-note", 72, 1006, 1010, 22,
           "0 = 本影尖恰好落在地面上；条长与尖端位置按 km 线性，三角头只是符号。"
           "真实本影半角 %.3f°，在 ① 的尺度上肉眼不可见。"
           % half_ang, 15, d.P["t2"], lines=1)

    # ---------- 右栏：常数与判读 ----------
    RX, RW = 1140, 388
    B.keypanel(d, tf, "k1", RX, 566, RW, "算这根锥用到的数",
               [("太阳半径", B.km(C["solar_volumetric_radius_km"]), "km"),
                ("月球半径", "{:,.1f}".format(C["lunar_equatorial_radius_km"]), "km"),
                ("日地平均距离", B.km(C["sun_mean_distance_km"]), "km"),
                ("本影长度", B.km(L_mean), "km"),
                ("+ 地球半径＝门槛", B.km(thr["mean"]), "km"),
                ("本影半角", "%.3f" % half_ang, "°")],
               row_h=31, size=16)
    B.keypanel(d, tf, "k2", RX, 782, RW, "三个距离下的结论（相对地表）",
               [("近地点 363,300", "+17,767", "km", d.P["ember"]),
                ("平均 384,400", "−3,333", "km", d.P["cyan"]),
                ("远地点 405,500", "−24,433", "km", d.P["cyan"]),
                ("锥长随日地距离", "368,427–380,950", "km", d.P["t0"])],
               row_h=31, size=16)
    d.rect(RX, 952, RW, 74, d.P["card"])
    B.tlab(d, tf, "k3-a", RX + 16, 962, RW - 32, 48,
           "这只判断长度。真实某次是否接地，还要看当天实际月距、"
           "食甚时的地理纬度和海拔。", 14, d.P["t1"], lines=2)

    B.footband(d, tf, "f", [
        "数据来源：NASA Sun / Moon / Earth Fact Sheet（本机实际抓取，见 sources/）。"
        "锥长 L = r_月 × d_日 / (r_日 − r_月) 及其余量为本题推算，非 NASA 直接给出。",
        "比例声明：①② 的横向刻度均按 km 线性，未做任何对数或截断处理；"
        "② 的三角头与 ① 的圆点只是记号，不代表影锥的真实粗细。",
    ], size=13)

    info = {"title": "本影锥够不够得到地面", "size": [1600, 1200],
            "kind": "geometry/图解",
            "claims": ["umbral length 374,689 km", "threshold 381,067 km",
                       "margins +17,767 / -3,333 / -24,433 km",
                       "threshold band %d-%d km" % (min(thr.values()), max(thr.values()))],
            "derived_from": ["research/stats.json constants+geometry",
                             "research/derived.json"],
            "exaggeration": "无比例变形；② 的三角头为符号"}
    return d, tf, info
