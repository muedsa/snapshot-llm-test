# -*- coding: utf-8 -*-
"""件-09《什么时候可以裸眼看》：把五个接触排到同一条时间尺度上，量出真正能摘掉眼镜的那一小段。

主体数字来自 research/contacts.json（derive_contacts.py 现场推算，输入为
research/path-pages.json 的路径表逐行值、probe/nasa-oh-2024/2027.txt 的食分与 ΔT、
research/catalog.json 的 224 行）。裸眼规则原文取自
sources/nasa-science-safety.html，贝利珠/钻石环/接触点定义取自
sources/nasa-science-glossary.html。1800×1100 深空底。
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
hrule, vrule = B.hrule, B.vrule
W, H = 1800, 1100
DANGER = "#5C2415"     # 偏食段＝必须戴镜
SAFE = "#2E7B86"       # 全食段外框
AX0, AX1 = 96, 1150


def load(name):
    return json.loads((ROOT / "tmp" / RID / "B04" / "research" / name).read_text(encoding="utf-8"))


def s_of(h):
    a, b, c = h.split(":")
    return int(a) * 3600 + int(b) * 60 + float(c)


def short(h):
    return h[:8]


def hhmm(sec):
    sec = sec % 86400
    return "%02d:%02d" % (sec // 3600, (sec % 3600) // 60)


def dur(sec):
    return "%dm%.1fs" % (int(sec) // 60, sec % 60)


def build():
    C = load("contacts.json")
    P = load("path-pages.json")
    e24, e27 = C["eclipses"]["2024-04-08"], C["eclipses"]["2027-08-02"]
    ge24 = P["nasa-path-2024"]["derived"]["greatest_eclipse"]
    ge27 = P["nasa-path-2027"]["derived"]["greatest_eclipse"]
    t24, t27 = e24["site_timeline_at_greatest_eclipse"], e27["site_timeline_at_greatest_eclipse"]
    k24, k27 = e24["track"], e27["track"]
    o24, o27 = e24["off_axis_at_greatest_eclipse"], e27["off_axis_at_greatest_eclipse"]
    cat = C["catalog_2021_2100"]
    nT, nH = cat["by_type"]["T"]["with_window"], cat["by_type"]["H"]["with_window"]
    xchk24, xchk27 = e24["sun_position_check"], e27["sun_position_check"]
    d, tf = B.doc(W, H)
    B.header(d, tf, "hd", "玖", "什么时候可以裸眼看",
             "2024-04-08 大食点那一个观测者：能摘眼镜的只有 %s，占整场食 %.2f%%"
             % (dur(t24["totality_s"]), t24["safe_pct"]))

    # ============ A · 同一条时间尺度 ============
    c1, c2, gex, c3, c4 = [s_of(x["ut"]) for x in t24["contacts"]]
    lo, hi = c1 - 300, c4 + 300
    span = hi - lo

    def tx(sec):
        return AX0 + (sec - lo) / span * (AX1 - AX0)

    BAR = 306
    B.tlab(d, tf, "a-t", 72, 198, 1090, 24,
           "A · 一条时间轴（横轴 UT，全图共用同一秒/像素比例）：暗红＝必须戴镜，青＝可裸眼",
           18, d.P["t0"], style="BOLD")
    marks = [("初亏", "C1 半影外切", EMBER), ("食既", "C2 本影内切", CYAN),
             ("食甚", "大食·非接触", CORONA), ("生光", "C3 本影内切", CYAN),
             ("复圆", "C4 半影外切", EMBER)]
    # 主带
    d.rect(tx(c1), BAR, tx(c2) - tx(c1), 40, DANGER)
    d.rect(tx(c3), BAR, tx(c4) - tx(c3), 40, DANGER)
    d.rect(tx(c2), BAR, tx(c3) - tx(c2), 40, SAFE)
    d.rect(tx(c2), BAR + 6, tx(c3) - tx(c2), 28, CYAN)
    hrule(d, tx(c1), BAR - 2, tx(c4) - tx(c1), d.P["border"], 1)
    hrule(d, tx(c1), BAR + 42, tx(c4) - tx(c1), d.P["border"], 1)
    B.mono(d, tf, "a-h1", tx((c1 + c2) / 2) - 120, BAR + 10, 240, 20,
           "偏食 %.1f 分 · 戴镜" % t24["half_partial_min"], 13, B.MOON, align="CENTER")
    B.mono(d, tf, "a-h2", tx((c3 + c4) / 2) - 120, BAR + 10, 240, 20,
           "偏食 %.1f 分 · 戴镜" % t24["half_partial_min"], 13, B.MOON, align="CENTER")
    # 首末接触：相隔 2h42m，标签靠在自己竖线的外侧（不让竖线穿过文字）
    for i in (0, 4):
        xx = tx(s_of(t24["contacts"][i]["ut"]))
        vrule(d, xx, 244, BAR - 244, marks[i][2], 1)
        lx, alg = (xx + 9, "START") if i == 0 else (xx - 169, "END")
        B.tlab(d, tf, "a-m%d" % i, lx, 246, 160, 20, marks[i][0], 16, d.P["t0"],
               align=alg, style="BOLD")
        B.mono(d, tf, "a-m%d-t" % i, lx, 268, 160, 18, short(t24["contacts"][i]["ut"]),
               14, marks[i][2], align=alg)
        B.mono(d, tf, "a-m%d-e" % i, lx, 286, 160, 16, marks[i][1], 11, d.P["t2"],
               align=alg)
    # 中间三个接触在这把尺上只相隔 13 px：错开三行，各拉一条折线指回自己的位置
    for i, ry, side, txt in [
        (1, 246, "END", "食既 %s（C2 本影内切）" % short(t24["contacts"][1]["ut"])),
        (3, 268, "START", "生光 %s（C3 本影内切）" % short(t24["contacts"][3]["ut"])),
        (2, 290, "END", "食甚 %s · 全食 %s · 占 %.2f%%"
         % (short(t24["contacts"][2]["ut"]), dur(t24["totality_s"]), t24["safe_pct"]))]:
        xx = tx(s_of(t24["contacts"][i]["ut"]))
        col = marks[i][2]
        wdt = 330
        if side == "END":
            ex = xx - 12
            B.mono(d, tf, "a-c%d" % i, ex - wdt, ry, wdt, 18, txt, 13, col, align="END")
            hrule(d, ex, ry + 9, xx - ex + 1, col, 1)
        else:
            ex = xx + 12
            B.mono(d, tf, "a-c%d" % i, ex, ry, wdt, 18, txt, 13, col, align="START")
            hrule(d, xx, ry + 9, ex - xx, col, 1)
        vrule(d, xx, ry + 9, BAR - ry - 9, col, 1)
    B.mono(d, tf, "a-px", 664, 232, 330, 18,
           "这把尺上 1 px ≈ %.1f s：青色带只有 %.0f px 宽"
           % ((hi - lo) / (AX1 - AX0), tx(c3) - tx(c2)), 12, d.P["t2"], align="START")
    # 刻度（30 分钟一格）
    first = ((lo // 1800) + 1) * 1800
    n = int((hi - first) // 1800) + 1
    for i in range(n):
        tv = first + i * 1800
        xx = tx(tv)
        vrule(d, xx, BAR + 44, 8, d.P["axis"], 1)
        B.mono(d, tf, "a-ax%d" % i, xx - 30, BAR + 56, 60, 20, hhmm(tv), 12, d.P["t2"], align="CENTER")

    # 2027 对照带：与 2024 同比例，按各自食甚对齐
    d1, d2, g2, d3, d4 = [s_of(x["ut"]) for x in t27["contacts"]]

    def tx2(sec):
        return tx(sec - g2 + gex)

    Y2 = 408
    B.tlab(d, tf, "a-27t", 72, Y2 - 26, 1090, 22,
           "同一比例下的 2027-08-02 大食点（初亏 %s → 复圆 %s UT，整场 %s）；两带按各自食甚对齐"
           % (short(t27["contacts"][0]["ut"]), short(t27["contacts"][4]["ut"]), t27["event_span_hms"]),
           14, d.P["t1"])
    d.rect(tx2(d1), Y2, tx2(d2) - tx2(d1), 20, DANGER)
    d.rect(tx2(d3), Y2, tx2(d4) - tx2(d3), 20, DANGER)
    d.rect(tx2(d2), Y2, tx2(d3) - tx2(d2), 20, SAFE)
    d.rect(tx2(d2), Y2 + 3, tx2(d3) - tx2(d2), 14, CYAN)
    B.mono(d, tf, "a-27s", tx2(d3) + 10, Y2 + 1, 420, 18,
           "裸眼段 %s · 占 %.2f%%" % (dur(t27["totality_s"]), t27["safe_pct"]), 13, CYAN, align="START")
    B.mono(d, tf, "a-27n", 72, Y2 + 26, 1090, 18,
           "食分只多 %.5f（%.5f→%.5f），裸眼段就长了 %s；占比从 %.2f%% 抬到 %.2f%%"
           % (t27["magnitude"] - t24["magnitude"], t24["magnitude"], t27["magnitude"],
              dur(t27["totality_s"] - t24["totality_s"]), t24["safe_pct"], t27["safe_pct"]),
           12, d.P["t2"], align="START")

    # ============ B · 五个接触的圆盘 ============
    BY0 = 476
    B.tlab(d, tf, "b-t", 72, BY0, 1090, 24,
           "B · 这五个时刻在天上分别是这样（月/日视半径比＝食分 m=%.5f）" % t24["magnitude"],
           18, d.P["t0"], style="BOLD")
    B.tlab(d, tf, "b-n", 72, BY0 + 24, 1090, 22,
           "黄盘＝光球，黑盘（灰边）＝月影，位置按外切/内切摆放；暗金细圈＝已被遮住的光球轮廓。月盘只比日盘大 %.3f 倍——“完全遮住”本就只有一线余地。"
           % t24["magnitude"], 13, d.P["t2"])
    RS = 28.0
    RM = RS * t24["magnitude"]
    cellw = 214
    bcy = BY0 + 98
    offs = [RS + RM, RM - RS, 0.0, -(RM - RS), -(RS + RM)]
    for i, ct in enumerate(t24["contacts"]):
        cx = 96 + i * cellw + cellw / 2
        B.disc(d, cx, bcy, RS, CORONA)
        B.disc(d, cx + offs[i], bcy, RM, "#0B1122")
        B.ring(d, cx + offs[i], bcy, RM, 1.2, B.MOON)
        if i in (1, 2, 3):      # 光球轮廓已被月影盖住，用暗金圈把它的位置留在图上
            B.ring(d, cx, bcy, RS, 1.0, "#7A6034")
        B.tlab(d, tf, "b-m%d" % i, cx - 96, bcy + RS + 14, 192, 20, marks[i][0], 15, d.P["t0"], align="CENTER", style="BOLD")
        B.mono(d, tf, "b-m%d-t" % i, cx - 96, bcy + RS + 34, 192, 18, short(ct["ut"]), 12,
               CYAN if i == 2 else d.P["t1"], align="CENTER")
        B.mono(d, tf, "b-m%d-s" % i, cx - 96, bcy + RS + 52, 192, 18,
               "可裸眼" if i == 2 else ("必须戴镜" if i in (0, 4) else "临界几秒"), 11,
               CYAN if i == 2 else EMBER, align="CENTER")

    # ============ C · 离轴曲线 ============
    CY0 = 686
    GX0, GX1, GY0, GY1 = 152, 560, 872, 736
    B.tlab(d, tf, "c-t", 72, CY0, 500, 24, "C · 离食带中心线越远，窗口缩水多快", 17, d.P["t0"], style="BOLD")
    xmax, ymax = 130.0, 400.0

    def gx(km_):
        return GX0 + km_ / xmax * (GX1 - GX0)

    def gy(sec):
        return GY0 - sec / ymax * (GY0 - GY1)

    for i in range(5):
        yv = ymax * i / 4
        hrule(d, GX0, gy(yv), GX1 - GX0, d.P["grid"], 1)
        B.mono(d, tf, "c-ly%d" % i, GX0 - 58, gy(yv) - 9, 52, 18, "%d" % yv, 11, d.P["t2"], align="END")
    for i, xv in enumerate([v for v in range(0, 141, 20) if v <= xmax]):
        vrule(d, gx(xv), GY0, 6, d.P["axis"], 1)
        B.mono(d, tf, "c-lx%d" % i, gx(xv) - 26, GY0 + 9, 52, 18, "%d" % xv, 11, d.P["t2"], align="CENTER")
    B.tlab(d, tf, "c-ax", GX0, GY0 + 28, GX1 - GX0, 20, "垂直于食带偏离中心线（km）", 12, d.P["t2"], align="CENTER")
    B.tlab(d, tf, "c-ay", 78, GY1 - 22, 200, 20, "剩余窗口（秒）", 12, d.P["t2"], align="START")
    for blk, col in [(o24, CYAN), (o27, CORONA)]:
        pts = []
        for k in range(0, 41):
            f = k / 40.0
            pts.append((gx(f * blk["half_width_km"]),
                        gy(blk["center_duration_s"] * (1 - f * f) ** 0.5)))
        for k in range(len(pts) - 1):
            (xa, ya), (xb, yb) = pts[k], pts[k + 1]
            nn = max(1, int(((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5 / 3.0))
            for m2 in range(nn):
                d.rect(xa + (xb - xa) * m2 / nn, ya + (yb - ya) * m2 / nn, 3.0, 3.0, col)
        vrule(d, gx(blk["half_width_km"]), GY1, GY0 - GY1, col, 1)
    B.mono(d, tf, "c-k24", 96, 924, 490, 16,
           "青 2024：半宽 %.1f km，中心 %.1f s，离轴 %.1f km 只剩 60 s"
           % (o24["half_width_km"], o24["center_duration_s"], o24["d_km_for_60s"]),
           11.5, CYAN, align="START")
    B.mono(d, tf, "c-k27", 96, 942, 490, 16,
           "金 2027：半宽 %.1f km，中心 %.1f s，离轴 %.1f km 只剩 60 s"
           % (o27["half_width_km"], o27["center_duration_s"], o27["d_km_for_60s"]),
           11.5, CORONA, align="START")
    B.mono(d, tf, "c-md", 96, 960, 490, 16,
           "模型：窗口∝直径＝带宽的圆在偏离 d 处的弦长（推算）", 11, d.P["t2"], align="START")

    # ============ D · 224 次里的窗口分布 ============
    DX0 = 640
    TW = AX1 - DX0
    B.tlab(d, tf, "d-t", DX0, CY0, TW, 24, "D · 2021–2100 那 224 次日食，几次允许裸眼",
           17, d.P["t0"], style="BOLD")
    n_has, n_no = cat["n_with_safe_window"], cat["n_no_safe_window"]
    bw = TW * n_has / 224.0
    d.rect(DX0, 716, bw, 26, SAFE)
    d.rect(DX0 + bw, 716, TW - bw, 26, DANGER)
    B.mono(d, tf, "d-a", DX0 + 6, 721, bw - 10, 18, "有 %d 次" % n_has, 13, B.PAPER, align="START")
    B.mono(d, tf, "d-b", DX0 + bw + 8, 721, TW - bw - 16, 18,
           "%d 次一秒都不能裸眼（环食 %d＋偏食 %d）"
           % (n_no, cat["by_type"]["A"]["n"], cat["by_type"]["P"]["n"]), 12, B.MOON, align="START")
    B.mono(d, tf, "d-c", DX0, 746, TW, 16,
           "有窗口的那 %d 次＝全食 %d + 混合 %d；混合食中位占比 %.2f%%"
           % (n_has, nT, nH, cat["by_type"]["H"]["pct_median"]), 11, d.P["t2"], align="START")
    hb = cat["histogram"][:6]
    hmax = max(x["n"] for x in hb)
    hbw = (TW - 40) / 6
    HY0, HMAXH = 872, 84
    for i, x in enumerate(hb):
        bh = (x["n"] / hmax) * HMAXH
        xx = DX0 + i * hbw
        d.rect(xx, HY0 - bh, hbw - 12, bh, CYAN if i >= 3 else SAFE)
        B.mono(d, tf, "d-h%d-n" % i, xx, HY0 - bh - 18, hbw - 8, 16, str(x["n"]), 11, d.P["t0"], align="START")
        B.mono(d, tf, "d-h%d-l" % i, xx, HY0 + 6, hbw - 6, 16, x["label"].replace("%", "").replace("-0.00", "0-"),
               10, d.P["t2"], align="START")
    B.tlab(d, tf, "d-hx", DX0, HY0 + 24, TW, 20, "裸眼占比区间（%）内的日食次数", 11, d.P["t2"], align="START")
    top, bot = cat["top5"][0], cat["bottom5"][0]
    B.mono(d, tf, "d-x1", DX0, 922, TW, 16,
           "最高 %s：%s m=%.4f，占 %.2f%%（全食 %.0f s／整场 %.1f 分）"
           % (top["date"], top["type"], top["magnitude"], top["safe_pct"], top["totality_s"], top["event_span_min"]),
           11, CYAN, align="START")
    B.mono(d, tf, "d-x2", DX0, 940, TW, 16,
           "最低 %s：H m=%.4f，占 %.2f%%（全食 %.0f s／整场 %.1f 分）"
           % (bot["date"], bot["magnitude"], bot["safe_pct"], bot["totality_s"], bot["event_span_min"]),
           11, EMBER, align="START")

    # ============ E · 事实分级 ============
    EX0, EX1 = 1190, 1728
    EW = EX1 - EX0
    B.tlab(d, tf, "e-t", EX0, 198, EW, 24, "E · 这张图上的每句话各自凭什么", 17, B.PAPER, style="BOLD")
    tiers = [
        ("A 级 · 已证实（页面原文）", CORONA, [
            "“Except during the brief total phase of a total solar",
            "eclipse, when the Moon completely blocks the Sun's bright",
            "face, it is not safe to look directly at the Sun without",
            "specialized eye protection.”（science.nasa.gov/eclipses/safety/）",
            "同页：偏食与环食 “never safe”；判据是“透过眼镜再也",
            "看不到太阳的任何部分”。glossary 里 BAILY'S BEADS＝",
            "全食前后阳光只从月缘山谷透出的几个亮点。",
        ]),
        ("B 级 · 来源结论（照页面数字，未改算）", CYAN, [
            "2024-04-08：m=%.5f，大食 %s UT，带宽 %.1f km，该处全食 %.1f s（路径页）"
            % (t24["magnitude"], short(t24["contacts"][2]["ut"]), ge24["width_km"], t24["totality_s"]),
            "2027-08-02：m=%.5f，大食 %s UT，带宽 %.1f km，该处全食 %.1f s（路径页）"
            % (t27["magnitude"], short(t27["contacts"][2]["ut"]), ge27["width_km"], t27["totality_s"]),
            "路径表 %d/%d 行：最长 %.1f–%.1f s，带宽 %d–%d km，比值 %.3f–%.3f"
            % (k24["table_rows"], k27["table_rows"], k24["duration_s_min"], k24["duration_s_max"],
               k24["width_km_min"], k24["width_km_max"], k24["ratio_min"], k24["ratio_max"]),
            "本影横向速度＝带宽/时长，%.2f–%.2f km/s（%d 行逐行相除）"
            % (k24["transverse_speed_km_s_min"], k24["transverse_speed_km_s_max"], k24["table_rows"]),
            "ΔT 三处不一：OH 页 %.1f s，路径页注 %.1f s，两页大食时刻之差推得 %.1f s"
            % (e24["deltat"]["oh_stated_s"], e24["deltat"]["path_page_note_delta_t_s"],
               e24["deltat"]["implied_by_path_minus_oh_TD_s"]),
        ]),
        ("C 级 · 我的推算（图上多数数字属于这级）", EMBER, [
            "位移关系：初亏→食既走完 2r☉，食既→生光走完 2(m−1)r☉，",
            "同一角速度相除得 t(偏食半段)=D/(m−1)，于是",
            "整场=D·(m+1)/(m−1)，裸眼占比=(m−1)/(m+1)——角速度消掉，",
            "占比只由食分决定；绝对时刻才依赖“匀速”这条假设。",
            "由此定出 %s 初亏、%s 复圆（NASA 两页都没给这两个数）。"
            % (short(t24["contacts"][0]["ut"]), short(t24["contacts"][4]["ut"])),
            "互检：按经度推的地方真太阳时 %s，与按页面公布的太阳"
            % e24["local_apparent_time"]["contacts_local_apparent"][2],
            "高度/方位反推的时角差 %.2f 分（2027 差 %.2f 分；alt/az 舍入"
            % (xchk24["difference_min"], xchk27["difference_min"]),
            "只带 %.2f 分，余量应来自食影轴并不经过大食点子午线）。"
            % xchk24["H_rounding_spread_as_time_min"],
            "C、D 两区的曲线与占比都是推算，不是 NASA 结论。",
        ]),
        ("D 级 · 未能取证 / 限制", d.P["t1"], [
            "贝利珠、钻石环各持续几秒：NASA 只写 few seconds，本套材料里",
            "没有可读出的秒数；按 A 区这把尺（1 px≈10 s）那几秒不到 1 px，",
            "画不出来，所以只在 B 区用“临界几秒”标位置，不编造宽度。",
            "m 取的是 NASA 公布的地心食分，站点上实际是该点的拓扑食分，",
            "差值直接进入窗口长度；圆盘按理想圆面处理，未计月缘地形。",
            "全图时间只用 UT 与地方真太阳时，不采用任何国家时区。",
        ]),
    ]
    yy = 226
    for ti, (title, col, lines) in enumerate(tiers):
        d.rect(EX0, yy + 5, 6, 6, col)
        B.tlab(d, tf, "e-h%d" % ti, EX0 + 14, yy, EW - 14, 22, title, 14, col, style="BOLD")
        yy += 24
        for j, ln in enumerate(lines):
            B.mono(d, tf, "e-%d-l%d" % (ti, j), EX0 + 14, yy + j * 18, EW - 20, 17, ln, 11.5, d.P["t1"], align="START")
        yy += len(lines) * 18 + 12

    # E 区底部：把结论写成可执行的三步（判据逐字取自安全页）
    hrule(d, EX0, 856, EW, d.P["border"], 1)
    B.tlab(d, tf, "e-k-t", EX0, 864, EW, 22, "把结论写成四步（判据照抄安全页）", 14, CORONA, style="BOLD")
    steps = [
        ("1", "初亏 → 食既：全程戴 ISO 12312-2 眼镜，本例 %.1f 分钟。" % t24["half_partial_min"], EMBER),
        ("2", "食既 → 生光：只有这 %s 可以裸眼；判据是“透过眼镜再也" % dur(t24["totality_s"]), CYAN),
        ("", "看不到太阳的任何部分”，不是“天黑了”。", CYAN),
        ("3", "生光之后：一见亮立即戴回，直到复圆（又是 %.1f 分钟）。" % t24["half_partial_min"], EMBER),
        ("4", "环食/偏食：没有第 2 步，任何时刻都不裸眼（224 次里 149 次）。", EMBER),
    ]
    for i, (num, ln, col) in enumerate(steps):
        yv = 892 + i * 17
        if num:
            d.rect(EX0, yv + 3, 12, 12, col)
            B.mono(d, tf, "e-k%s" % num, EX0 + 1, yv + 1, 11, 13, num, 10, B.GROUND, align="CENTER")
        B.mono(d, tf, "e-kl%d" % i, EX0 + 20, yv, EW - 24, 15, ln, 11, d.P["t1"], align="START")

    B.footband(d, tf, "fb", [
        "五个接触：食既/生光＝路径页大食行“Line Duration 04m28.1s”对 18:17:18.3 UT 前后平移；食甚＝该行时刻；初亏/复圆由 C 级公式推出，NASA 未公布大食点这两刻。",
        "来源（相对本题工作目录）：sources/nasa-path-2024·2027.html、nasa-oh-2024·2027.html、nasa-plotkey.html、nasa-science-{safety,glossary,eclipse-types}.html；逐行值见 research/path-pages.json。",
        "推算：derive_contacts.py → research/contacts.json（接触时刻、整场时长、占比、离轴曲线、ΔT 对照、时角互检、224 行分布）；本图只描述“大食点那一个观测者”，不是整条食带。",
        "声明：这是排版与算术，不是医疗建议；偏食与环食阶段一律需要 ISO 12312-2 滤片，判据以 NASA 安全页原文为准。",
    ], size=12)

    info = {"safe_pct": t24["safe_pct"], "n_has": n_has, "span": t24["event_span_hms"]}
    return d, tf, info
