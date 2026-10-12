"""件-07《月影扫过地面的速度》1200x1200。

手册常数说：月球轨道速度 1.022 km/s 减去赤道自转 0.465 km/s＝影轴在地面上
以 0.557 km/s（2005 km/h）东移；反向相叠则是 1.487 km/s（5354 km/h）。
本页用两条真实食带的中央线逐点表把这句话摊开：沿轨实测多少、两个独立算法
是否相符、纬度到底起不起作用。
数据：research/speed.json（derive_speed.py 从 path-pages.json 实算）
＋ research/derived.json（NASA 事实页常数）。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B04"))
import b04kit as B  # noqa: E402

W, H = 1200, 1200
MX, RX = 72, 1128


def jload(name):
    return json.loads((ROOT / "tmp" / RID / "B04" / "research" / name).read_text(encoding="utf-8"))


def build():
    sp = jload("speed.json")
    tr24, tr27 = sp["tracks"]["nasa-path-2024"], sp["tracks"]["nasa-path-2027"]
    cst = sp["constants"]
    lo, hi = sp["ref_east_kms"], sp["ref_west_kms"]
    d, tf = B.doc(W, H, "dark")
    B.header(d, tf, "h", "07", "月影扫过地面的速度",
             "两条真实食带的沿轨实测：中段 0.67–1.71 km/s，两端掠入时冲到 8.5 km/s", size=40)

    # ================= ① 速度合成 =================
    y1 = 194
    B.tlab(d, tf, "p1-t", MX, y1, 900, 24, "① 先把常数合成出来（单位 km/s，正射且路径正东西）",
           18, d.P["t0"], style="BOLD")
    rows = [("月球轨道速度", cst["moon_orbital_kms"], d.P["moon"]),
            ("赤道地表自转", cst["surface_rotation_kms"], d.P["cyan"]),
            ("同向相消＝下限", lo, d.P["ember"]),
            ("反向相叠＝上限", hi, d.P["corona"])]
    yb = B.hbars(d, tf, "p1", MX, y1 + 30, RX - MX, rows, bh=19, gap=5, lab_w=176,
                 vmax=1.6, fmt=lambda v: "%.3f" % v, size=14)
    B.tlab(d, tf, "p1-n", MX, yb + 2, RX - MX, 20,
           "0.557 km/s＝2005 km/h，1.487 km/s＝5354 km/h：地表在影轴下方同向自转，影追上观察者前先减掉这一段。",
           13, d.P["t1"])

    # ================= ② 沿轨实测剖面 =================
    y2 = yb + 34
    B.tlab(d, tf, "p2-t", MX, y2, 500, 24, "② 实测：相邻中央线点距离 ÷ 120 秒", 18,
           d.P["t0"], style="BOLD")
    for i, (key, tr, col) in enumerate((("24", tr24, "ember"), ("27", tr27, "cyan"))):
        lx = MX + 520 + i * 200
        B.disc(d, lx + 5, y2 + 11, 5, d.P[col])
        B.mono(d, tf, "p2-lg%s" % key, lx + 15, y2 + 2, 190, 18,
               "%s（%d 段）" % ("2024-04-08" if key == "24" else "2027-08-02",
                                len(tr["segments"])), 12, d.P["t1"])
    px0, px1 = MX + 40, RX - 16
    pyb, pyt = y2 + 172, y2 + 44
    vmin, vmax = 0.5, 9.0

    def yof(v):
        return pyb - math.log(v / vmin) / math.log(vmax / vmin) * (pyb - pyt)

    d.rect(px0, yof(hi), px1 - px0, yof(lo) - yof(hi), "#101A31")
    for c in (0.5, 1.0, 2.0, 4.0, 8.0):
        yy = yof(c)
        d.rect(px0, yy, px1 - px0, 1, d.P["grid"])
        B.mono(d, tf, "p2-g%g" % c, MX - 34, yy - 7, 68, 15, "%g" % c, 11, d.P["t2"], align="END")
    for v, col, lab, dy in ((hi, d.P["corona"], "合成上限 %.3f" % hi, 4),
                            (lo, d.P["ember"], "合成下限 %.3f" % lo, -19)):
        yy = yof(v)
        d.rect(px0, yy, px1 - px0, 1.5, col)
        B.mono(d, tf, "p2-ref%d" % v, px0 + 10, yy + dy, 130, 15, lab, 11, col)
    d.rect(px0, pyb, px1 - px0, 1.5, d.P["axis"])
    for key, tr, col in (("27", tr27, "cyan"), ("24", tr24, "ember")):
        pts = [(px0 + p["at_frac"] * (px1 - px0), yof(p["kms"])) for p in tr["profile"]]
        for a, b in zip(pts, pts[1:]):
            d.line(a[0], a[1], b[0], b[1], 2.2, d.P[col])
        for x, y in pts:
            d.dot(x, y, 6.5, d.P[col])
    for i in (0, 1, 2, 3, 4):
        xx = px0 + (px1 - px0) * i / 4.0
        d.rect(xx, pyb + 2, 1, 6, d.P["axis"])
        B.mono(d, tf, "p2-x%d" % i, xx - 24, pyb + 11, 48, 15, "%d%%" % (i * 25), 11,
               d.P["t2"], align="CENTER")
    for si, (key, tr, col) in enumerate((("24", tr24, "ember"), ("27", tr27, "cyan"))):
        B.mono(d, tf, "p2-h%s" % key, 76, pyb + 34 + si * 17, 34, 15,
               "2024" if key == "24" else "2027", 10, d.P[col], align="END")
        for p in tr["profile"]:
            x = px0 + p["at_frac"] * (px1 - px0)
            B.mono(d, tf, "p2-v%s%d" % (key, p["bin"]), x - 26, pyb + 34 + si * 17, 52, 15,
                   "%.2f" % p["kms"], 10, d.P[col], align="CENTER")
    B.tlab(d, tf, "p2-n", MX, pyb + 72, RX - MX, 18,
           "下面两行＝各段影速均值（km/s）；横轴＝沿轨位置（占路径全长的百分比），纵轴对数；"
           "两条路径全长 %s km 与 %s km" % (B.km(tr24["total_km"]), B.km(tr27["total_km"])),
           12, d.P["t2"], align="CENTER")
    y3 = pyb + 96

    # ================= ③ 两法对账 =================
    B.tlab(d, tf, "p3-t", MX, y3, 960, 24, "③ 对账：宽度 ÷ 时长 只在脚印接近圆时才等于影速", 18,
           d.P["t0"], style="BOLD")
    B.tlab(d, tf, "p3-s", MX, y3 + 26, RX - MX, 20,
           "长宽比＝沿轨影速 × 该段时长 ÷ 该段带宽。≈1 两法相符；远大于 1 说明本影脚印被斜切拉长，宽度÷时长会低估影速。",
           12, d.P["t1"])
    gy = y3 + 52
    base, gph = gy + 100, 92.0
    for gi, (key, tr, col) in enumerate((("24", tr24, "ember"), ("27", tr27, "cyan"))):
        gx0 = MX + gi * ((RX - MX) / 2.0 + 16)
        gw = (RX - MX) / 2.0 - 40
        slot = gw / 8.0
        bw = slot - 14
        yref = base - 1.0 / 6.0 * gph
        d.rect(gx0, yref, gw, 1, d.P["axis"])
        if gi == 0:
            B.mono(d, tf, "p3-r%s" % key, gx0 - 42, yref - 8, 38, 14, "=1.0", 10, d.P["t2"],
                   align="END")
        d.rect(gx0, base, gw, 1.5, d.P["border"])
        for i, p in enumerate(tr["profile"]):
            x = gx0 + slot * i + 7
            hh = min(p["aspect"], 6.0) / 6.0 * gph
            d.rect(x, base - hh, bw, hh, d.P[col])
            B.mono(d, tf, "p3-v%s%d" % (key, i), x - 5, base - hh - 15, bw + 10, 14,
                   "%.1f" % p["aspect"], 10, d.P["t0"], align="CENTER")
            B.mono(d, tf, "p3-x%s%d" % (key, i), x - 5, base + 5, bw + 10, 13,
                   str(i + 1), 10, d.P["t2"], align="CENTER")
        B.mono(d, tf, "p3-tt%s" % key, gx0, base + 22, gw, 17,
               "%s：首段 %.2f → 中段 %.2f → 末段 %.2f"
               % ("2024" if key == "24" else "2027", tr["profile"][0]["aspect"],
                  tr["profile"][4]["aspect"], tr["profile"][7]["aspect"]),
               12, d.P[col])
    y4 = base + 48

    # ================= ④ 纬度 vs 实测相关 + 关键数 =================
    B.tlab(d, tf, "p4-t", MX, y4, 400, 24, "④ 纬度起多大作用", 18, d.P["t0"], style="BOLD")
    ax0, ax1 = MX + 36, MX + 400
    ayt, ayb = y4 + 50, y4 + 150
    d.rect(ax0, ayb, ax1 - ax0, 1.5, d.P["axis"])
    d.rect(ax0, ayt, 1.5, ayb - ayt, d.P["axis"])
    pts = [(ax0 + p["lat"] / 90.0 * (ax1 - ax0), ayb - p["kms"] / 0.5 * (ayb - ayt))
           for p in sp["rotation_vs_lat"]]
    for a, b in zip(pts, pts[1:]):
        d.line(a[0], a[1], b[0], b[1], 2.5, d.P["moon"])
    for la in (0, 30, 60, 90):
        xx = ax0 + la / 90.0 * (ax1 - ax0)
        d.rect(xx, ayb + 2, 1, 6, d.P["axis"])
        B.mono(d, tf, "p4-x%d" % la, xx - 20, ayb + 10, 44, 15, "%d°" % la, 11, d.P["t2"],
               align="CENTER")
    for vv in (0.2, 0.4):
        yy = ayb - vv / 0.5 * (ayb - ayt)
        d.rect(ax0, yy, ax1 - ax0, 1, d.P["grid"])
        B.mono(d, tf, "p4-y%.1f" % vv, ax0 - 40, yy - 7, 34, 15, "%.1f" % vv, 10, d.P["t2"],
               align="END")
    B.mono(d, tf, "p4-u", ax0, ayt - 20, 400, 16, "自转分量 km/s（纵 0–0.5，横 纬度 0–90°）",
           11, d.P["t2"])
    B.tlab(d, tf, "p4-n", ax0, ayb + 32, 376, 68,
           "自转分量只按 cos φ 变化（赤道 0.465、两极 0）。但实测影速与纬度的相关却是负的："
           "2024 −0.07、2027 −0.30。主导是掠入程度（沿轨位置），不是纬度。",
           12, d.P["t1"], lines=4)
    ky = B.keypanel(d, tf, "p4-k", MX + 440, y4 + 22, RX - (MX + 440), "本页实测的关键数",
                    [("中段实测区间（两条合并）", "%.3f–%.3f" % (
                         min(tr24["mid_min_kms"], tr27["mid_min_kms"]),
                         max(tr24["mid_max_kms"], tr27["mid_max_kms"])), "km/s", d.P["t0"]),
                     ("中段平均 2024/2027", "%.3f / %.3f" % (tr24["mid_mean_kms"], tr27["mid_mean_kms"]),
                      "km/s"),
                     ("落在合成带内", "%d/%d · %d/%d" % (tr24["mid_in_band"], tr24["mid_n"],
                                                        tr27["mid_in_band"], tr27["mid_n"]), "段"),
                     ("高出上限 1.487", "%d · %d" % (tr24["mid_above_band"], tr27["mid_above_band"]), "段"),
                     ("低于下限 0.557", "%d · %d" % (tr24["mid_below_band"], tr27["mid_below_band"]), "段"),
                     ("单段最大（掠入端）", "%.2f / %.2f" % (tr24["max_seg"]["kms"], tr27["max_seg"]["kms"]),
                      "km/s", d.P["ember"]),
                     ("两法相关系数", "%.2f / %.2f" % (tr24["corr_seg_vs_implied"],
                                                       tr27["corr_seg_vs_implied"]))], size=15)

    B.footband(d, tf, "f", [
        "来源：NASA 两条日食路径页中央线表（SE2024Apr08Tpath 98 行、SE2027Aug02Tpath 102 行，2 分钟间隔的经纬度、带宽与中心食时长）。",
        "常数：月球平均轨道速度 1.022 km/s（nasa-moon-fact.html）；赤道半径 6378.137 km、恒星日 23.9345 h（nasa-earth-fact.html）算出地表 0.465 km/s。",
        "推算：沿轨距离、影速、宽度÷时长、脚印长宽比与合成带全部由 derive_speed.py 实算，NASA 页面本身不给影速。",
        "限制：2 分钟采样只能给段平均，首末段接近掠入畸变最强（单段最大 8.50 km/s）；长宽比是几何解释，不是严格的球面矢量反解。",
    ], size=12)

    info = {
        "case": "07", "title": "月影扫过地面的速度", "width": W, "height": H,
        "points_2024": tr24["rows"], "segments_2024": len(tr24["segments"]),
        "points_2027": tr27["rows"], "segments_2027": len(tr27["segments"]),
        "total_km_2024": tr24["total_km"], "total_km_2027": tr27["total_km"],
        "band_kms": [lo, hi], "band_kmph": [cst["eastward_kmph"], cst["westward_kmph"]],
        "mid_min": min(tr24["mid_min_kms"], tr27["mid_min_kms"]),
        "mid_max": max(tr24["mid_max_kms"], tr27["mid_max_kms"]),
        "mid_mean": [tr24["mid_mean_kms"], tr27["mid_mean_kms"]],
        "band_in": [tr24["mid_in_band"], tr27["mid_in_band"]],
        "band_above": [tr24["mid_above_band"], tr27["mid_above_band"]],
        "max_seg": [tr24["max_seg"], tr27["max_seg"]],
        "corr_speed_lat": [tr24["corr_speed_lat"], tr27["corr_speed_lat"]],
        "corr_seg_vs_implied": [tr24["corr_seg_vs_implied"], tr27["corr_seg_vs_implied"]],
        "aspect_first_mid_last": [[tr24["profile"][0]["aspect"], tr24["profile"][4]["aspect"],
                                   tr24["profile"][7]["aspect"]],
                                  [tr27["profile"][0]["aspect"], tr27["profile"][4]["aspect"],
                                   tr27["profile"][7]["aspect"]]],
        "profile_bins": 8,
    }
    return d, tf, info
