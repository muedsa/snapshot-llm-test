# -*- coding: utf-8 -*-
"""件-08《食甚点的地理》：224 个食甚点投到等距经纬网格，配经度/纬度分箱、
中国经度带账本、与 NASA 十年表地域文字的逐条对齐。1600×800 深空底。

数据全部来自 research/catalog.json（224 行目录）、research/geo.json、
research/geo2.json（本件现场推算，脚本 derive_geo.py / derive_geo2.py）。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B04"))
import b04kit as B  # noqa: E402

MONO = B.MONO
EMBER, CYAN, CORONA = B.EMBER, B.CYAN, B.CORONA
W, H = 1600, 800

K = 1.5
MX0, MX1 = 112, 652
MY0, MY1 = 212, 482
BAND_LO, BAND_HI = 73, 135
BOX_S, BOX_N = 4, 54
BORDER = "#1B2A4A"

BX0, BX1 = 672, 960
CX0, CX1 = 1000, 1528


def load(name):
    return json.loads((ROOT / "tmp" / RID / "B04" / "research" / name).read_text(encoding="utf-8"))


def px(lon):
    return MX0 + (lon + 180) * K


def py(lat):
    return MY1 - (lat + 90) * K


def build():
    d, tf = B.doc(W, H)
    rows = B.data()[1]
    geo, geo2 = load("geo.json"), load("geo2.json")
    band = geo["band_points"]
    chi = geo2["lon_chi2"]
    pt = geo2["per_type"]
    rule = geo2["sign_rule_by_abs_gamma"]
    nasa = geo2["regions_matched"]
    tc = {"T": EMBER, "A": CYAN, "H": CORONA, "P": d.P["t2"]}

    B.header(d, tf, "hd", "件 08", "食甚点的地理",
             "224 个食甚点投到同一张经纬网格：经度近乎均匀，纬度强烈分带")

    # ---------------- ① 等距经纬网格 ----------------
    B.tlab(d, tf, "p1-t", 72, 190, 580, 22,
           "① 224 个食甚点·等距网格（虚线＝回归线/极圈）", 16, d.P["t0"], style="BOLD")
    d.rect(MX0, MY0, MX1 - MX0, MY1 - MY0, "#101A31")
    d.rect(px(BAND_LO), MY0, px(BAND_HI) - px(BAND_LO), MY1 - MY0, BORDER)
    for lon in range(-180, 181, 30):
        d.rect(px(lon), MY0, 1, MY1 - MY0, d.P["grid"])
    for lat in range(-90, 91, 30):
        d.rect(MX0, py(lat), MX1 - MX0, 1, d.P["axis"] if lat == 0 else d.P["grid"])
    for lat, col in [(23.44, CORONA), (-23.44, CORONA), (66.56, CYAN), (-66.56, CYAN)]:
        x = MX0
        while x < MX1 - 4:
            d.rect(x, py(lat), 5, 1, col)
            x += 10
    d.rect(px(BAND_LO), py(BOX_N), px(BAND_HI) - px(BAND_LO), 1, EMBER)
    d.rect(px(BAND_LO), py(BOX_S), px(BAND_HI) - px(BAND_LO), 1, EMBER)
    d.rect(px(BAND_LO), py(BOX_N), 1, py(BOX_S) - py(BOX_N), EMBER)
    d.rect(px(BAND_HI), py(BOX_N), 1, py(BOX_S) - py(BOX_N), EMBER)

    polar = {(r["date"]): r for r in geo2["central_polar_rows"]}
    for t in ["P", "A", "H", "T"]:
        r0 = 1.7 if t == "P" else 2.6
        for r in rows:
            if r["type"] != t:
                continue
            B.disc(d, px(r["lon"]), py(r["lat"]), r0, tc[t])
            if r["date"] in polar:
                B.ring(d, px(r["lon"]), py(r["lat"]), r0 + 2.2, 1.1, d.P["t1"])
    B.tlab(d, tf, "p1-band", px(BAND_LO) - 8, MY0 - 15, 118, 13, "73–135°E 带",
           11, EMBER, align="CENTER")
    for lat in (-60, -30, 0, 30, 60):
        B.mono(d, tf, "p1-la%+d" % lat, 72, py(lat) - 6, 34, 13, "%+d°" % lat,
               11, d.P["t2"], align="END")

    for dt, tag in [("2024-04-08", "24"), ("2027-08-02", "27")]:
        r = [x for x in rows if x["date"] == dt][0]
        cxp, cyp = px(r["lon"]), py(r["lat"])
        d.rect(cxp - 8, cyp, 16, 1.4, d.P["t0"])
        d.rect(cxp, cyp - 8, 1.4, 16, d.P["t0"])
        B.mono(d, tf, "p1-x" + tag, cxp + 9, cyp - 19, 22, 13, tag, 10, d.P["t0"])

    # 图例
    ly = 490
    lx = MX0
    for lab, t in [("全食 T", "T"), ("环食 A", "A"), ("混合 H", "H"), ("偏食 P", "P")]:
        B.disc(d, lx + 4, ly + 6, 2.6, tc[t])
        B.tlab(d, tf, "p1-lg-%s" % t, lx + 12, ly, 44, 14, lab, 10.5, d.P["t1"])
        lx += 56
    B.ring(d, lx + 4, ly + 6, 4.6, 1.1, d.P["t1"])
    B.tlab(d, tf, "p1-lg-r", lx + 12, ly, 50, 14, "空圈>75°", 10, d.P["t1"])
    lx += 64
    d.rect(lx, ly + 6, 12, 1.2, d.P["t0"])
    d.rect(lx + 5.4, ly + 1, 1.2, 12, d.P["t0"])
    B.tlab(d, tf, "p1-lg-x", lx + 18, ly, 60, 14, "2024/2027", 10, d.P["t1"])
    lx += 84
    d.rect(lx, ly + 1, 20, 1, EMBER)
    d.rect(lx, ly + 11, 20, 1, EMBER)
    d.rect(lx, ly + 1, 1, 11, EMBER)
    d.rect(lx + 20, ly + 1, 1, 11, EMBER)
    B.tlab(d, tf, "p1-lg-b", lx + 26, ly, 66, 14, "框 4–54°N", 10, d.P["t1"])

    # ---------------- ② 经度分箱 ----------------
    YB, YTOP = 640, 545
    sc = (YB - YTOP) / 14.0
    B.tlab(d, tf, "p2-t", 112, 508, 380, 20,
           "② 经度方向：15°×24 箱，期望每箱 %.2f" % chi["expected_per_bin"],
           15, d.P["t0"], style="BOLD")
    B.tlab(d, tf, "p2-r", MX1 - 96, 508, 96, 20, "卡方 %.2f" % chi["chi2"], 13,
           EMBER, align="END")
    for b in geo["lon_bins_15"]:
        x0, w0 = px(b["lo"]) + 1.5, 15 * K - 4
        y = YB
        for t in ["P", "H", "A", "T"]:
            if not b[t]:
                continue
            hh = b[t] * sc
            d.rect(x0, y - hh, w0, hh, tc[t])
            y -= hh
        if b["n"]:
            B.mono(d, tf, "p2-n%d" % b["lo"], x0 - 3, y - 15, w0 + 6, 12,
                   str(b["n"]), 10, d.P["t1"], align="CENTER")
    ye = YB - chi["expected_per_bin"] * sc
    x = MX0
    while x < MX1:
        d.rect(x, ye, 6, 1, d.P["t2"])
        x += 11
    for lon in range(-180, 181, 60):
        B.mono(d, tf, "p2-x%+d" % lon, px(lon) - 30, 644, 60, 14, "%+d°" % lon,
               11, d.P["t2"], align="CENTER")
    B.tlab(d, tf, "p2-note", MX0, 662, 540, 14,
           "最高 14（−105–−90、150–165）／最低 3（105–120°E）；df=23",
           11, d.P["t2"])

    # ---------------- ③ 纬度分箱 ----------------
    B.tlab(d, tf, "p3-t", BX0, 190, 288, 22, "③ 纬度方向：15°×12 箱·与①同纵轴",
           15, d.P["t0"], style="BOLD")
    lsc = 240 / 56.0
    for i, b in enumerate(geo["lat_bins_15"]):
        ytop = MY0 + i * (15 * K)
        y = ytop + 3
        for t in ["T", "A", "H", "P"]:
            if not b[t]:
                continue
            ww = b[t] * lsc
            d.rect(BX0 + 2, y, ww, 4.2, tc[t])
            y += 4.6
        if b["n"]:
            B.mono(d, tf, "p3-n%d" % i, BX0 + 2 + b["n"] * lsc + 4, ytop + 4, 30, 13,
                   str(b["n"]), 11, d.P["t1"], align="START")
    for lat in (-60, 0, 60):
        d.rect(MX1 + 2, py(lat), BX0 - MX1 - 2, 1, d.P["grid"])

    # 五个纬度带 × 类型
    belts = list(pt["T"]["belts"].items())
    SHORT = ["≤23.44°", "23.44–40°", "40–60°", "60–75°", ">75°"]
    B.tlab(d, tf, "p4-t", BX0, 498, 288, 22, "五个纬度带的类型构成", 14,
           d.P["t0"], style="BOLD")
    cols = [BX0, BX0 + 128, BX0 + 166, BX0 + 204, BX0 + 242, BX0 + 280]
    B.mono(d, tf, "p4-h", BX0, 522, 120, 16, "纬度带", 11, d.P["t2"])
    for j, t in enumerate(["T", "A", "H", "P"]):
        B.mono(d, tf, "p4-hh%d" % j, cols[j + 1] - 26, 522, 26, 16, t, 11, tc[t],
               align="END")
    B.mono(d, tf, "p4-hs", cols[5] - 26, 522, 26, 16, "合计", 11, d.P["t2"], align="END")
    for i, (name, _f) in enumerate(belts):
        y = 540 + i * 17
        cnts = {t: pt[t]["belts"][name] for t in ("T", "A", "H", "P")}
        tot = sum(cnts.values())
        B.mono(d, tf, "p4-l%d" % i, BX0, y, 122, 16, SHORT[i], 11, d.P["t1"])
        for j, t in enumerate(["T", "A", "H", "P"]):
            B.mono(d, tf, "p4-c%d-%s" % (i, t), cols[j + 1] - 26, y, 26, 16,
                   str(cnts[t]), 11, tc[t] if cnts[t] else d.P["grid"], align="END")
        B.mono(d, tf, "p4-s%d" % i, cols[5] - 26, y, 26, 16, str(tot), 11, d.P["t0"],
               align="END")
    B.tlab(d, tf, "p4-n2", BX0, 626, 288, 34,
           "偏食那一列 0/0/0/77/0：77 个点全在 61–72° 带内，"
           "一个都不进热带、温带或极帽。", 11, d.P["t2"], lines=2)

    # ---------------- ④ 中国经度带账本 ----------------
    B.tlab(d, tf, "p5-t", CX0, 200, 528, 22,
           "④ 73–135°E 带内的 29 个食甚点", 15, d.P["t0"], style="BOLD")
    hdr = [("日期", 0, 64, "START"), ("型", 66, 14, "START"), ("纬,经", 90, 44, "START"),
           ("最长", 132, 40, "END"), ("带宽", 178, 46, "END")]
    for j, (h, dx, w0, al) in enumerate(hdr):
        B.tlab(d, tf, "p5-h%d" % j, CX0 + dx, 224, w0, 15, h, 10, d.P["t2"], align=al)
    d.rect(CX0, 241, 528, 1, d.P["border"])
    d.rect(CX0 + 256, 246, 1, 224, d.P["grid"])
    for i, r in enumerate(band):
        cx0 = CX0 + (i // 15) * 264
        y = 244 + (i % 15) * 15
        B.mono(d, tf, "p5-d%d" % i, cx0, y, 64, 15, r["date"], 10, d.P["t1"])
        B.disc(d, cx0 + 68, y + 6, 2.4, tc[r["type"]])
        B.mono(d, tf, "p5-t%d" % i, cx0 + 74, y, 12, 15, r["type"], 10, tc[r["type"]])
        B.mono(d, tf, "p5-c%d" % i, cx0 + 90, y, 62, 15,
               "%+d,%+d" % (r["lat"], r["lon"]), 10, d.P["t0"])
        dur = "%ds" % int(r["dur_s"]) if r["dur_s"] else "—"
        wid = "%dkm" % r["width_km"] if r["width_km"] else "—"
        B.mono(d, tf, "p5-u%d" % i, cx0 + 132, y, 40, 15, dur, 10,
               d.P["t0"] if r["dur_s"] else d.P["grid"], align="END")
        B.mono(d, tf, "p5-w%d" % i, cx0 + 178, y, 46, 15, wid, 10,
               d.P["t0"] if r["width_km"] else d.P["grid"], align="END")
    B.tlab(d, tf, "p5-s1", CX0, 476, 528, 18,
           "构成：全食 5 · 环食 12 · 混合 2 · 偏食 10＝29（判据只是食甚点经度）",
           12, d.P["t1"])
    B.tlab(d, tf, "p5-s2", CX0, 498, 528, 18,
           "其中|纬度|>60° 有 16 个（10 个偏食全在内）；4–54°N 盒内只 5 个",
           12, d.P["t1"])

    # ---------------- ⑤ 规律 ----------------
    B.tlab(d, tf, "p6-t", CX0, 524, 528, 20, "⑤ 从这 224 个点里量出来的三条",
           14, d.P["t0"], style="BOLD")
    thr = "%g" % rule["threshold"]
    lines = [
        "经度：卡方 %.2f／df 23，与均匀分布分不开" % chi["chi2"],
        "纬度：偏食 77/77 落在 61–72°，中心食可达 −87…81°",
        "符号：|γ|>%s 的 %d 行全对；≤%s 的 %d 行错 %d 个，全在 5–8/11–12 月" % (
            thr, rule["large_gamma_n"], thr, rule["small_gamma_n"],
            rule["small_gamma_disagree"]),
    ]
    for i, ln in enumerate(lines):
        B.tlab(d, tf, "p6-l%d" % i, CX0, 548 + i * 19, 528, 17, ln, 12, d.P["t1"])

    # ---------------- ⑥ NASA 十年表对齐 ----------------
    B.tlab(d, tf, "p7-t", CX0, 608, 528, 18,
           "⑥ 与 NASA 十年表 %d 行地域文字逐条对齐" % len(nasa), 13,
           d.P["t0"], style="BOLD")
    nl = [
        "日期 22/22 对上：类型、沙罗全同，食分最大差 %.3f" % max(
            m["magnitude_diff"] for m in nasa),
        "带内节选 2028-07-22 →“Total: Australia, N. Z.”",
        "2030-06-01 →“…n. China, Japan”；偏食行写的是可见区",
    ]
    for i, ln in enumerate(nl):
        B.mono(d, tf, "p7-l%d" % i, CX0, 630 + i * 19, 528, 16, ln, 11, d.P["t1"])

    B.footband(d, tf, "fb", [
        "来源：NASA 21 世纪日食目录 224 行逐行解析（nasa-21cen-catalog.html）；食甚点经纬度、γ、类型、带宽、最长均为目录原值，坐标粒度 1°。",
        "地域描述：NASA 2021–2030 十年表 nasa-solar-basics.html 的 22 行，按日期与目录连接；带内 5 行原文节选如上。",
        "推算：分箱、卡方、纬度带交叉表、|γ| 分组符号一致率、经度带/包围盒计数由 derive_geo.py、derive_geo2.py 现场算出，存 research/geo.json、geo2.json。",
        "限制：本图只画食甚点，不画食带；“食带是否穿过某地”不能由食甚点经纬度判断（2070-04-11 恰在 135°E 边界，量化 ±0.5° 可使其进出）。",
    ], size=12)

    info = {"chi2": chi["chi2"], "band": geo["band_n"], "n": len(rows)}
    return d, tf, info
