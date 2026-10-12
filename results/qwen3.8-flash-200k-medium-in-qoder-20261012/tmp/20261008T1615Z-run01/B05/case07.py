"""件-07 倾斜仪读数序列判读（1200×1600，平板，技术复核态）。

内容任务：复核员要判断的不是"现在几度"，而是"这条曲线是不是在加速、
报警规则是不是被触发、要不要维持立即处置"。所以主体是时序 + 规则命中 + 结论。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1200, 1600
MX = 48
CW = W - 2 * MX


def build():
    st = B.data()
    f = st["featured"]["tree"]
    series = st["featured"]["series"]
    last, prev = series[-1], series[-2]
    rates = [s["rate_deg_per_30d"] for s in series]
    jumps = [round(series[i]["tilt_deg"] - series[i - 1]["tilt_deg"], 2)
             for i in range(1, len(series))]
    rules = [
        ("T1", "末次读数 ≥ 6.0°", "%.1f°" % last["tilt_deg"],
         last["tilt_deg"] >= 6.0),
        ("T2", "连续两次增速 ≥ 0.30°/30 天",
         "最近两次 %.2f / %.2f" % (rates[-2], rates[-1]),
         rates[-1] >= 0.30 and rates[-2] >= 0.30),
        ("T3", "单次跳变 > 0.80°", "本月 %+.2f°" % jumps[-1], jumps[-1] > 0.80),
        ("T4", "≥15 节大风后未回落", "风 %.0f 节，前值 %.1f°" % (last["wind_kts"],
                                                                prev["tilt_deg"]),
         last["wind_kts"] >= 15 and last["tilt_deg"] > prev["tilt_deg"]),
        ("T5", "空洞 ≥30 % 且倾斜 ≥5°", "空洞 %d %% ｜ 倾斜 %.1f°" %
         (f["cavity_pct"], f["tilt_deg"]), f["cavity_pct"] >= 30 and
         f["tilt_deg"] >= 5.0),
    ]
    hit = sum(1 for r in rules if r[3])

    d, tf = B.doc(W, H, ground="light")
    # ---- 头部 ----
    B.tlab(d, tf, "h-t", MX, 40, 700, 46, "倾斜序列复核", 32, d.P["t0"], style="BOLD")
    B.num(d, tf, "h-id", W - MX - 300, 44, 300, 40, f["id"], 26, d.P["t0"])
    B.tlab(d, tf, "h-s", MX, 92, 800, 28, "%s ｜ %s ｜ 复核员 方明（技术科）" %
           (f["species"], f["road"]), 18, d.P["t2"])
    B.chip(d, tf, "h-band", W - MX - 300, 92, 300, 40, "现场判级：%s R=%d" %
           (f["band"], f["risk"]), "#FFFFFF", B.RUST, size=17)

    # ---- ① 时序主图 ----
    px, py, pw = B.card(d, tf, "ch", MX, 150, CW, 434)
    B.tlab(d, tf, "ch-t", px, py, 700, 30, "① 12 次月检读数（2025-11 → 2026-10）",
           21, d.P["t0"], style="BOLD")
    B.tlab(d, tf, "ch-s", px, py + 34, pw, 26, "纵轴倾角 0-10°；背景带是阈值分区，"
           "底部灰柱是当月最大风速", 15, d.P["t2"])
    ax, ay, aw, ah = px, py + 70, pw, 250
    for lo, hi, col in [(0, 4, "#F1ECE1"), (4, 6, "#FBEEDA"), (6, 10, "#F8E2DC")]:
        y1 = ay + ah - hi / 10.0 * ah
        d.rect(ax, y1, aw, (hi - lo) / 10.0 * ah, col)
    for gv in (0, 2, 4, 6, 8, 10):
        gy = ay + ah - gv / 10.0 * ah
        d.rect(ax, gy, aw, 1, d.P["line"])
        B.mono(d, tf, "gy%d" % gv, ax, gy - 12, 40, 22, "%d°" % gv, 14, d.P["t2"])
    n = len(series)
    xs = [ax + 46 + i * (aw - 60) / float(n - 1) for i in range(n)]
    ys = [ay + ah - s["tilt_deg"] / 10.0 * ah for s in series]
    for i in range(1, n):
        d.line(xs[i - 1], ys[i - 1], xs[i], ys[i], 4,
               B.RUST if series[i]["tilt_deg"] >= 6 else B.LEAF)
    for i, s in enumerate(series):
        col = B.RUST if s["tilt_deg"] >= 6 else B.LEAF
        B.disc(d, xs[i], ys[i], 7, col)
        B.disc(d, xs[i], ys[i], 3, "#FFFDF8")
        if i in (0, n - 3, n - 2, n - 1):
            d.rect(xs[i] - 33, ys[i] - 37, 66, 26, "#FFFDF8", radius=5)
            B.mono(d, tf, "cv%d" % i, xs[i] - 30, ys[i] - 34, 60, 24,
                   "%.1f°" % s["tilt_deg"], 15, col, align="CENTER")
        B.mono(d, tf, "cm%d" % i, xs[i] - 34, ay + ah + 6, 68, 22, s["month"][2:],
               13, d.P["t2"], align="CENTER")
        wh = s["wind_kts"] / 30.0 * 46
        d.rect(xs[i] - 12, ay + ah - wh, 24, wh, "#DCD3C4")
    d.line(ax + 46, ay + ah - 0.6 * ah, ax + aw - 14, ay + ah - 0.6 * ah, 3, B.RUST)
    B.tlab(d, tf, "thr", ax + 56, ay + ah - 0.6 * ah - 30, 200, 26,
           "6.0° 立即处置参考", 15, B.RUST)
    B.tlab(d, tf, "wind-l", px, ay + ah + 34, pw, 26,
           "灰柱＝当月最大风速（满格 30 节）；风速只作解释变量，不进风险分", 15,
           d.P["t2"])

    # ---- ② 增速 ----
    px, py, pw = B.card(d, tf, "rate", MX, 600, CW, 268)
    B.tlab(d, tf, "rt-t", px, py, 700, 30, "② 30 天增速与加速阈值", 21, d.P["t0"],
           style="BOLD")
    by = py + 44
    bh = 120
    d.rect(px, by + bh, pw, 2, d.P["line"])
    bw = (pw - 40) / float(n) - 8
    ty = by + bh - 0.30 / 0.60 * bh
    d.line(px, ty, px + pw, ty, 3, B.AMBER)
    for i, s in enumerate(series):
        x = px + i * (bw + 8)
        h = min(1.0, s["rate_deg_per_30d"] / 0.60) * bh
        col = B.RUST if s["rate_deg_per_30d"] >= 0.30 else "#C9C2B4"
        d.rect(x, by + bh - h, bw, h, col, radius=3)
        B.mono(d, tf, "rtm%d" % i, x - 6, by + bh + 8, bw + 12, 22, s["month"][5:],
               13, d.P["t2"], align="CENTER")
    d.rect(px + 200, ty - 33, 226, 28, "#FFFDF8", radius=5)
    B.tlab(d, tf, "rt-thr", px + 204, ty - 30, 220, 26, "0.30°/30 天阈值", 15,
           B.AMBER)
    B.tlab(d, tf, "rt-n", px, by + bh + 34, pw, 26,
           "前 8 个月稳定在 0.14°/30 天，近 4 个月抬到 0.36°；加速比"
           " %.1f 倍是这次报警的主因" % (rates[-1] / rates[0]), 15, d.P["t2"])

    # ---- ③ 规则命中 ----
    px, py, pw = B.card(d, tf, "ru", MX, 880, CW, 364)
    B.tlab(d, tf, "ru-t", px, py, 700, 30, "③ 报警规则命中（5 条中 %d 条）" % hit,
           21, d.P["t0"], style="BOLD")
    cols = [("规则", 56, "START"), ("条件", 470, "START"), ("本次取值", 300, "START"),
            ("判定", CW - 2 * MX - 886, "START")]
    rows = [[r[0], r[1], r[2], ("命中", B.RUST) if r[3] else ("未命中", d.P["t2"])]
            for r in rules]
    B.coltable(d, tf, "rut", px, py + 40, pw, cols, rows, row_h=42, head_h=34,
               size=17, head_size=15)
    B.tlab(d, tf, "ru-n", px, py + 40 + 34 + 5 * 42 + 4, pw, 28,
           "规则是硬编码的判定式，任一命中即进入「立即处置」候选；命中 3 条以上必须技术科复核签字。",
           16, d.P["t2"])

    # ---- ④ 结论 ----
    px, py, pw = B.card(d, tf, "cn", MX, 1256, CW, 244)
    B.tlab(d, tf, "cn-t", px, py, 700, 30, "④ 复核结论", 21, d.P["t0"], style="BOLD")
    opts = [("维持立即处置", True), ("降级为观察期", False), ("要求补测后再判", False)]
    for i, (t, on) in enumerate(opts):
        x = px + i * 200
        B.disc_outline(d, x + 12, py + 62, 11, 3, B.RUST if on else d.P["border"])
        if on:
            B.disc(d, x + 12, py + 62, 6, B.RUST)
        B.tlab(d, tf, "cn%d" % i, x + 34, py + 48, 170, 28, t, 17,
               d.P["t0"] if on else d.P["t2"])
    B.tlab(d, tf, "cn-r", px, py + 92, pw, 60,
           "依据：T1/T2/T3/T4/T5 全部命中；冠幅 9.4 m 且下游 12 m 内是公交站与停车位，"
           "撤围条件（连续两次 < 5.0°）在两个月内不可能满足。", 16, d.P["t1"],
           lines=2, valign="TOP")
    B.mono(d, tf, "cn-sign", px, py + 158, 520, 30,
           "复核意见提交：2026-10-11 11:05 ｜ 方明", 16, d.P["t2"])
    d.rect(px + pw - 260, py + 148, 260, 46, d.P["leaf"], radius=12)
    B.tlab(d, tf, "cn-btn", px + pw - 260, py + 158, 260, 30, "提交并回写工单", 18,
           "#FFFFFF", align="CENTER", style="BOLD")

    B.credit(d, tf, "foot", MX, 1528, CW, [
        "演示序列：12 个月读数由 b05data.py（固定种子 %d）生成，虚构；测斜仪读数按 ±0.2°"
        " 的仪器误差记录，本图未做多次测量的平均。" % st["seed"],
        "6.0° 参考线、0.30°/30 天加速阈值与 T1-T5 规则均为本产品自定判定口径，不是行业标准；"
        "风速仅作解释变量。未做真实用户验证。"], size=15)
    return d, tf, dict(case="case-07", kind="倾斜序列复核（平板，复核态）",
                       tree=f["id"], rules_hit=hit, rules_total=len(rules),
                       last_tilt=last["tilt_deg"])
