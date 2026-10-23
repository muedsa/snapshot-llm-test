"""case-03 金杯 · 手冲咖啡克重时间螺旋（1080×1440 吧台竖卡）。

视觉系统：一条等距螺旋把两个变量折成一条线。
  半径 = 累计注水克重（内圈 = 粉床，外圈 = 240 g 金标）
  转角 = 累计时间（顺时针，一圈多到 4:00 出杯）
  四个注水节点是螺旋上的四个圆点，编号 1-4 与下方明细表一一对应。

选等距螺旋（r 随克重线性）而不是指数螺旋的理由写在 plan.json 的
revision_log v2：指数半径会把中段（闷蒸到一段之间）压缩掉，
而那段恰恰是节奏最要紧的地方。

示例参数为常见手冲做法的演示值：15 g 粉、240 g 水、92 °C、四段注水、
总时 240 s。非某款豆子的真实冲煮单，不宣称实测。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1080, 1440
MIN_FS = 18

BG = "#17110D"
PANEL = "#221A14"
PANEL2 = "#2B211A"
DISC = "#33271D"
INK = "#F7EFE6"
INK2 = "#CDBBA8"
INK3 = "#9C8A78"
RULE = "#3A2E23"
TICK = "#8A6F4C"
GOLD = "#E8A33D"
GOLD2 = "#C07E1E"

# ------------------------------------------------------------------ 冲煮参数
T_TOTAL = 240.0          # 总时长 s
COFFEE = 15.0            # 粉 g
WATER_TOTAL = 240.0      # 水 g
RATIO = WATER_TOTAL / COFFEE

# (段名, 起秒, 止秒, 本段结束时的累计水量 g)
SEGS = [("闷蒸", 0, 45, 30), ("一段", 45, 105, 120),
        ("二段", 105, 165, 180), ("三段", 165, 240, 240)]

# ------------------------------------------------------------------ 螺旋几何
R_IN, R_OUT = 42.0, 264.0
CX, CY = 540.0, 640.0
THETA0 = -math.pi / 2
THETA_SPAN = 2.4 * math.pi
TICK_IN, TICK_OUT = 270.0, 278.0


def seg_list() -> list:
    """展开成 (段名, 起秒, 止秒, 起克, 止克)。"""
    out, prev = [], 0.0
    for name, t0, t1, m1 in SEGS:
        out.append((name, float(t0), float(t1), prev, float(m1)))
        prev = float(m1)
    return out


def mass_at(t: float, segs: list) -> float:
    """累计注水克重：段内线性。"""
    for _n, t0, t1, m0, m1 in segs:
        if t <= t1 + 1e-9:
            return m0 + (m1 - m0) * (t - t0) / (t1 - t0)
    return segs[-1][4]


def rad_of(m: float) -> float:
    return R_IN + (m / WATER_TOTAL) * (R_OUT - R_IN)


def ang_of(t: float) -> float:
    return THETA0 + (t / T_TOTAL) * THETA_SPAN


def pt_at(t: float, segs: list) -> tuple:
    m = mass_at(t, segs)
    a, r = ang_of(t), rad_of(m)
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def hhmm(s: float) -> str:
    m, sec = divmod(int(round(s)), 60)
    return "%02d:%02d" % (m, sec)


def build() -> tuple:
    d = K.Doc(W, H, BG)
    gates: list = []
    segs = seg_list()
    cps = [(name, t1, m1) for name, t0, t1, m0, m1 in segs]

    # ------------------------------------------------ 页头
    d.rect(0, 0, W, 130, PANEL)
    d.rect(0, 128, W, 2, GOLD)
    d.text(60, 28, "金杯 · 手冲咖啡克重时间螺旋", 30, INK, bold=True)
    d.text(60, 74, "半径 = 累计注水克重　·　转角 = 累计时间　·　顺时针",
           18, INK3)
    d.text_r(1020, 32, "折光 · 十张日常　03 / 10", 18, INK3)
    d.text_r(1020, 60, "自拟示例参数", 18, INK3)

    # ------------------------------------------------ 参数条
    tiles = [("粉", "%.0f g" % COFFEE, INK), ("水", "%.0f g" % WATER_TOTAL,
             GOLD), ("水粉比", "1 : %g" % RATIO, GOLD),
             ("总时", hhmm(T_TOTAL), INK)]
    for i, (lb, val, col) in enumerate(tiles):
        tx = 60 + i * 244
        d.rect(tx, 150, 228, 80, PANEL, radius=14)
        d.text_c(tx + 114, 158, val, 30, col, bold=True)
        d.text_c(tx + 114, 196, lb, 18, INK3)

    # ------------------------------------------------ 螺旋
    c0, ch = 250, 760
    d.rect(60, c0, 960, ch, PANEL, radius=18)
    d.text(82, c0 + 22, "克重 × 时间 螺旋", 22, INK, bold=True)
    d.text_r(998, c0 + 28, "外圈刻度每格 30 秒", 18, INK3)

    # 时间刻度（外圈）
    for k in range(9):
        t = k * 30
        a = ang_of(t)
        x0, y0 = CX + TICK_IN * math.cos(a), CY + TICK_IN * math.sin(a)
        x1, y1 = CX + TICK_OUT * math.cos(a), CY + TICK_OUT * math.sin(a)
        d.stroke([(x0, y0), (x1, y1)], TICK, width=2, step=1,
                 owner="tick")
    d.text_c(CX, 330, "%s 起冲" % hhmm(0.0), 18, INK3)

    # 粉床
    d.rect(CX - R_IN, CY - R_IN, 2 * R_IN, 2 * R_IN, DISC, radius=R_IN,
           owner="bed")
    d.text_c(CX, CY - 9, "粉 %.0f g" % COFFEE, 18, INK2, bold=True)

    # 螺旋本体
    pts = [pt_at(float(t), segs) for t in range(0, int(T_TOTAL) + 1, 3)]
    d.stroke(pts, GOLD, width=3, step=1, owner="spiral")

    # 四个注水节点
    for i, (name, t1, m1) in enumerate(cps):
        x, y = pt_at(float(t1), segs)
        r = 18.0 if i == len(cps) - 1 else 13.0
        d.rect(x - r, y - r, 2 * r, 2 * r, PANEL2, radius=r,
               border="3 SOLID #E8A33D", owner="node")
        d.text_c(x, y - 10, "%d" % (i + 1), 18, GOLD, bold=True)
    ex, ey = pt_at(T_TOTAL, segs)
    d.text(ex + 24, ey - 9, "%.0f g · %s 出杯" % (WATER_TOTAL, hhmm(T_TOTAL)),
           18, GOLD, bold=True)

    d.text(82, 956,
           "内圈 = 粉床　·　节点 1-4 为每段注水结束时的克重与时刻，"
           "与下方明细表一一对应", 18, INK3)

    # ------------------------------------------------ 明细表
    ly, lh = 1030, 300
    d.rect(60, ly, 960, lh, PANEL, radius=18)
    d.text(82, ly + 22, "四段注水", 22, INK, bold=True)
    d.text_r(998, ly + 28, "水 %.0f g ÷ 粉 %.0f g = 1 : %g"
             % (WATER_TOTAL, COFFEE, RATIO), 18, INK2)

    hdr = [("段", 138), ("时间窗", 312), ("本段水", None), ("累计", None),
           ("速率 g/s", None)]
    for s, hx in hdr:
        if hx is None:
            d.text_r({"本段水": 620, "累计": 776, "速率 g/s": 998}[s], ly + 74,
                     s, 18, INK3)
        else:
            d.text(hx, ly + 74, s, 18, INK3)

    by = ly + 114
    for i, (name, t0, t1, m0, m1) in enumerate(segs):
        dur = t1 - t0
        rate = (m1 - m0) / dur
        d.rect(110, by + 1, 24, 24, PANEL2, radius=12, border="2 SOLID #E8A33D",
               owner="row-node")
        d.text_c(122, by + 3, "%d" % (i + 1), 18, GOLD, bold=True)
        d.text(146, by, name, 18, INK, bold=True)
        d.text(312, by, "%s–%s" % (hhmm(t0), hhmm(t1)), 18, INK2)
        d.text_r(620, by, "%.0f g" % (m1 - m0), 18, INK2)
        d.text_r(776, by, "%.0f g" % m1, 18, INK2)
        d.text_r(998, by, "%.2f" % rate, 18, GOLD, bold=True)
        if i < len(segs) - 1:
            d.line_h(82, 998, by + 36, RULE, w=1)
        by += 40

    # ------------------------------------------------ 页脚
    d.text(60, 1350,
           "示例参数为常见手冲做法的演示值，非某款豆子的实测冲煮单；"
           "比例、克重与时间可按口味调整。", 18, INK3)
    d.text_r(1020, 1378, "示意时刻 07:40 · 出图 2026-10-22", 18, INK3)

    # ------------------------------------------------ 专项门禁
    tot_water = sum(m1 for _n, t0, t1, m0, m1 in segs) - sum(
        m0 for _n, t0, t1, m0, m1 in segs)
    tot_time = sum(t1 - t0 for _n, t0, t1, m0, m1 in segs)
    K.gate(gates, "case-03-c01", "四段水量合计 = 240 g", tot_water == WATER_TOTAL,
           "%.0f g" % tot_water)
    K.gate(gates, "case-03-c02", "四段时间合计 = 240 s", tot_time == T_TOTAL,
           "%.0f s" % tot_time)
    K.gate(gates, "case-03-c03", "水粉比 = 240 ÷ 15 = 16，图上印 1 : 16",
           RATIO == 16.0 and "1 : 16" in [t["text"] for t in d.texts],
           "1 : %g" % RATIO)
    cum_ok = all(m0 <= m1 for _n, t0, t1, m0, m1 in segs) \
        and segs[-1][4] == WATER_TOTAL
    K.gate(gates, "case-03-c04", "累计水量逐段单调不减且末段 = 240 g", cum_ok,
           " → ".join("%.0f" % m1 for _n, t0, t1, m0, m1 in segs))
    _rates = [round((m1 - m0) / (t1 - t0), 2) for _n, t0, t1, m0, m1 in segs]
    _printed = [t["text"] for t in d.texts]
    K.gate(gates, "case-03-c05", "每段速率 = 本段水量 ÷ 本段时长，与表上印刷值一致",
           all(("%.2f" % r) in _printed for r in _rates)
           and sum(m1 - m0 for _n, t0, t1, m0, m1 in segs) == WATER_TOTAL,
           " ".join("%.2f" % r for r in _rates)
           + " 水量合计 %.0f g" % sum(m1 - m0 for _n, t0, t1, m0, m1 in segs))
    K.gate(gates, "case-03-c06", "闷蒸水量 = 粉重的两倍（30 g = 2 × 15 g）",
           segs[0][4] == 2 * COFFEE, "%.0f g = 2 × %.0f g"
           % (segs[0][4], COFFEE))
    K.gate(gates, "case-03-c07", "半径映射单调，r(0) = %g，r(240) = %g"
           % (R_IN, R_OUT),
           rad_of(0.0) == R_IN and abs(rad_of(WATER_TOTAL) - R_OUT) < 1e-9,
           "%.1f → %.1f" % (rad_of(0.0), rad_of(WATER_TOTAL)))
    K.gate(gates, "case-03-c08", "转角映射单调，θ(0) = -π/2，θ(240) = 2.4π 偏移",
           ang_of(0.0) == THETA0
           and abs(ang_of(T_TOTAL) - (THETA0 + THETA_SPAN)) < 1e-9, "")
    ex2, ey2 = pt_at(T_TOTAL, segs)
    K.gate(gates, "case-03-c09", "螺旋采样端点落在金标半径上，与节点 4 重合",
           math.hypot(ex2 - CX, ey2 - CY) - R_OUT < 1e-9
           and (ex2, ey2) == pts[-1],
           "(%.1f, %.1f)" % (ex2, ey2))
    K.gate(gates, "case-03-c10", "节点编号 1-4 在螺旋与明细表中都印出",
           all(("%d" % (i + 1)) in [t["text"] for t in d.texts]
               for i in range(len(segs))), "")
    K.gate(gates, "case-03-c11", "强调金与面板对比 ≥ 4.5",
           K.contrast(GOLD, PANEL) >= 4.5,
           "%.2f" % K.contrast(GOLD, PANEL))
    K.gate(gates, "case-03-c12", "正文次级字与面板对比 ≥ 4.5",
           K.contrast(INK2, PANEL) >= 4.5, "%.2f" % K.contrast(INK2, PANEL))
    K.gate(gates, "case-03-c13", "外圈 30 秒刻度线在面板上可辨（图形对比 ≥ 3.0）",
           K.contrast(TICK, PANEL) >= 3.0, "%.2f" % K.contrast(TICK, PANEL))
    gates = K.dry_run(d, "case-03", MIN_FS, gates)
    return d, gates, "门禁第 3 轮：只改门禁 ID 命名空间为 -cNN，" \
                     "与 dry_run 的 -01..-06 不再撞号；DSL 与图形零改动"


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc, gates, note = build()
    segs = seg_list()
    print("段表:", " | ".join("%s %s-%s %d→%dg %.2f g/s"
                              % (n, hhmm(t0), hhmm(t1), m0, m1, (m1 - m0)
                                 / (t1 - t0))
                              for n, t0, t1, m0, m1 in segs))
    print("水粉比 1:%g  总时 %s" % (RATIO, hhmm(T_TOTAL)))
    print("节点:", " ".join("%.1f,%.1f" % pt_at(float(t1), segs)
                            for _n, t0, t1, m0, m1 in segs))
    # 先落盘再断言：失败的门禁轮次也要留下证据，不能因为 assert 抛错就丢掉。
    print("gates=%s" % K.save_gates("case-03", gates, note))
    K.assert_gates(gates, "case-03")
    if "--dry" in sys.argv:
        return 0
    st = doc.stats()
    print("parts=%d texts=%d shapes=%d dsl=%d" % (st["parts"], st["texts"],
                                                   st["shapes"],
                                                   len(doc.build())))
    rec = K.render_case("case-03", doc, "case-03-pour-spiral",
                        "渲染 case-03 手冲咖啡克重时间螺旋", attempt_note=note)
    print("status=%s bytes=%s parts=%d ms=%s"
          % (rec["http_status"], rec.get("png_bytes"), rec["parts"],
             rec.get("elapsed_ms")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
