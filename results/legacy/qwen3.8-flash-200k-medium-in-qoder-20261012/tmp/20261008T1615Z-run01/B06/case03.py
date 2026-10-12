"""件-03「月租不能比较」1600×1000 桌面对比页。

原始口径：租房 App 价格行只写"2780 元/月"。
换算：把押金方式、首期、中介费、物业费、免租期、水电、通勤时间成本全部折进 12 个月，
      得到"真实月均"与"签约当天一次拿出多少"。
行动：三套房按真实月均排序，并明确哪些数是我给的口径（时间单价 30 元/h）。

三套房与全部数字为 self_defined_demo（demo.json case03）。
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import b06kit as K  # noqa: E402

W, H = 1600, 1000
MX = 48
CW = W - 2 * MX


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case03"]
    units = sorted(c["units"], key=lambda u: u["real_month"])
    mx_total = max(u["total_year"] for u in units)
    face_q = sorted(c["units"], key=lambda u: u["rent"])[0]   # 列表页最便宜
    real_q = units[0]                                          # 真实月均最低
    swap = [u for u in units if u["id"] == face_q["id"]][0]
    act_agency = round(face_q["agency"] / 24.0)
    act_free15 = round(15.0 * face_q["rent"] / 365.0 / 12.0)
    act_sign = face_q["sign_out"] - (face_q["rent"] * 2 + face_q["agency"])

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 88, K.BASE)
    d.rect(0, 86, W, 2, P["line"])
    K.tlab(d, tf, "h-t", MX, 14, 700, 40, "月租不能比较", 32, P["t0"])
    K.tlab(d, tf, "h-s", MX, 56, 900, 24,
           "把押金、物业、水电、中介费和一段通勤一起折进 12 个月，再按真实月均排序", 15, P["t2"])
    K.chip(d, tf, "h-c1", W - 470, 20, 210, 44, "口径：12 个月", P["t1"], P["panel2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 244, 20, 196, 44, "演示数据", P["t2"], P["card2"],
           border="1 SOLID " + P["border"], size=15)

    # ---------- ① 原始口径 ----------
    K.section(d, tf, "s1", MX, 96, CW, "①", "价格行给你的只有这些",
              "列表页能看到的就这三项：月租、押金方式、单程通勤", P["teal"])
    tw = (CW - 2 * 16) / 3.0
    face_rank = dict((u["id"], i + 1)
                     for i, u in enumerate(sorted(c["units"], key=lambda u: u["rent"])))
    for i, u in enumerate(units):
        x = MX + i * (tw + 16)
        K.panel(d, x, 164, tw, 84, P["card"], radius=14,
                border="1 SOLID " + P["border"])
        K.mono(d, tf, "t%d-p" % i, x + 18, 174, 128, 42, "%s" % K.fmt(u["rent"]), 32,
               P["amber"])
        K.tlab(d, tf, "t%d-u" % i, x + 150, 188, 120, 26, "元/月", 15, P["t2"])
        K.tlab(d, tf, "t%d-n" % i, x + 18, 222, tw - 36, 24,
               "%s ｜ 押%d付%d ｜ 单程 %d min"
               % (u["name"], u["dep_n"], u["prepay_n"], u["commute"]),
               15, P["t1"])
        K.mono(d, tf, "t%d-k" % i, x + tw - 150, 176, 132, 24,
               "列表页 #%d" % face_rank[u["id"]], 14, P["t2"], align="END")
    y = 256

    # ---------- ② 换算：堆叠年成本 ----------
    K.section(d, tf, "s2", MX, y, CW, "②", "换算：12 个月真实负担堆叠",
              "条长按同一年金额比例；通勤段是机会成本不是现金；空心框是押金（占用，可退）",
              P["gold"])
    by = y + 72
    bx, bw = MX + 250, 880
    mx_dep = max(u["deposit"] for u in units)
    scale = bw / float(mx_total + mx_dep)
    RX = bx + bw + 132
    parts = [("房租", "rent_paid_y", P["teal"]), ("物业", "prop_y", P["gold"]),
             ("水电网络", "util_y", P["grass"]), ("中介费", "agency", P["violet"]),
             ("通勤时间", "commute_cost_y", P["coral"])]
    for i, u in enumerate(units):
        ry = by + i * 82
        K.tlab(d, tf, "b%d-n" % i, MX, ry + 6, 236, 26, u["name"], 16, P["t0"])
        K.mono(d, tf, "b%d-r" % i, MX, ry + 34, 236, 24, "月租 %s" % K.fmt(u["rent"]),
               14, P["t2"])
        d.rect(bx, ry, bw, 46, P["grid"], radius=6)
        cx = bx
        for lab, key, col in parts:
            v = u[key]
            if v <= 0:
                continue
            wseg = max(3.0, v * scale)
            d.rect(cx, ry, wseg, 46, col)
            if wseg > 78:
                K.mono(d, tf, "b%d-%s" % (i, key), cx + 6, ry + 12, wseg - 12, 24,
                       K.fmt(v), 13, "#10181C")
            cx += wseg
        K.mono(d, tf, "b%d-tot" % i, RX, ry + 2, W - MX - RX, 26,
               "年 %s" % K.fmt(u["total_year"]), 16, P["t0"], align="END")
        K.mono(d, tf, "b%d-mo" % i, RX, ry + 26, W - MX - RX, 20,
               "月均 %s ｜ 占月租 %.0f%%" % (K.fmt(u["real_month"]),
                                            u["ratio_to_rent"]),
               13, P["t2"], align="END")
        # 押金：占用，画成空心框挂在条尾
        dw = max(6.0, u["deposit"] * scale)
        K.outline_rect(d, cx + 10, ry + 8, dw, 30, P["mist"], radius=4, thick=2)
        K.mono(d, tf, "b%d-dep" % i, cx + 10, ry + 50, max(150.0, dw), 20,
               "押金 %s" % K.fmt(u["deposit"]), 12, P["mist"])
    ly = by + 3 * 82 + 4
    lx = bx
    for lab, _k, col in parts:
        d.rect(lx, ly + 4, 22, 14, col, radius=3)
        K.tlab(d, tf, "lg-" + lab, lx + 30, ly, 110, 22, lab, 14, P["t1"])
        lx += 30 + 22 + 88
    K.tlab(d, tf, "lg-dep", lx, ly, 240, 22, "＝押金（可退，占用）", 14, P["mist"])
    y = 610

    # ---------- ③ 明细 ----------
    K.section(d, tf, "s3", MX, y, CW, "③", "明细：哪一笔钱把顺序换了",
              "按真实月均从低到高排；最右两列是单程通勤分钟与折算年小时", P["grass"])
    ax, aw = W - MX - 760, 760
    K.panel(d, ax, y + 8, aw, 56, P["panel2"], radius=12,
            border="1 SOLID " + P["leaf"])
    K.tlab(d, tf, "act-0", ax + 16, y + 14, aw - 32, 22,
           "行动：三笔可谈的钱单独折回月钱（以列表页最便宜的 %s 为例）"
           % face_q["name"], 14, P["t0"])
    K.tlab(d, tf, "act-1", ax + 16, y + 38, aw - 32, 22,
           "中介费减半 ≈ 省 %s 元/月 ｜ 免租期 +15 天 ≈ 省 %s 元/月 ｜ "
           "改押 1 付 1 当天少拿 %s 元（不省月钱，只少占用）"
           % (K.fmt(act_agency), K.fmt(act_free15), K.fmt(act_sign)), 13, P["t1"])
    cols = [("房源", 300, "START"), ("月租", 110, "END"), ("签约一次拿出", 170, "END"),
            ("年实付", 150, "END"), ("真实月均", 150, "END"), ("占月租", 110, "END"),
            ("免租期", 110, "END"), ("单程通勤", 130, "END"), ("通勤年小时", 170, "END")]
    rows = []
    for u in units:
        rows.append([u["name"], K.fmt(u["rent"]), K.fmt(u["sign_out"]),
                     K.fmt(u["total_year"]),
                     (K.fmt(u["real_month"]), P["amber"]),
                     "%.0f%%" % u["ratio_to_rent"],
                     "%d 天" % u["free_days"], "%d min" % u["commute"],
                     "%.0f h" % u["commute_y_h"]])
    ty = K.coltable(d, tf, "tab", MX, y + 72, CW, cols, rows, row_h=40, head_h=34,
                    size=15, head_size=14)
    assert ty <= 848, ty

    # ---------- ④ 结论与口径 ----------
    lines = [
        "结论：列表页最便宜的 %s（%s 元/月）真实月均 %s 元，反而比列表页第二便宜的 %s"
        "（%s 元/月，真实月均 %s 元）每月贵 %s 元。"
        % (face_q["name"], K.fmt(face_q["rent"]), K.fmt(swap["real_month"]),
           real_q["name"], K.fmt(real_q["rent"]), K.fmt(real_q["real_month"]),
           K.fmt(swap["real_month"] - real_q["real_month"])),
        "排序会换：列表页上这两套差 %s 元，折进 12 个月后差 %s 元、方向反过来；"
        "签约当天先拿出的钱见上表「签约一次拿出」列，它和月租完全不成比例。"
        % (K.fmt(real_q["rent"] - face_q["rent"]),
           K.fmt(swap["real_month"] - real_q["real_month"])),
        "口径（我给的，不是行业标准）：通勤按 %d 元/h 计机会成本、每月 22 天往返、"
        "一年 365 天房租按免租期折算；押金不计入支出，只标为占用。" % c["time_value"],
    ]
    nb = K.note_band(d, tf, "c4", MX, ty + 14, CW, lines, size=14)
    assert nb + 8 + 26 <= H - 12, nb
    K.credit(d, tf, "credit", MX, nb + 8, CW, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py，seed=%s）｜三套房、租金、"
        "通勤与免租期均为虚构演示值，不构成任何租房建议。" % (RID, K.data()["seed"]),
    ], size=12)
    info = {"case": "03", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "order_by_real_month": [u["id"] for u in units],
            "real_month": [u["real_month"] for u in units],
            "face_rent": [u["rent"] for u in units],
            "cheapest_face": c["cheapest_face"], "costliest_real": c["costliest_real"],
            "gap": c["gap"],
            "action_demo": {"unit": face_q["id"], "agency_half_per_month": act_agency,
                            "free15_per_month": act_free15, "sign_delta": act_sign}}
    return d, tf, info
