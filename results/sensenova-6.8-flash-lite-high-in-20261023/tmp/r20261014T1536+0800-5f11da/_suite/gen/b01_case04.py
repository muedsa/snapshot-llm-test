"""case-04 雪线一日 · 山区徒步窗口预报（1080×1500 山门口海报）。

视觉系统：一张「海拔 × 时间」图，画面上方的斜楔就是积雪与冰区。
  纵轴 = 海拔，真实米制 1700–3200 m
  横轴 = 一日时间 06:00–20:00
  斜线 = 雪线，2400 m 起、每小时下降 25 m
  雪线以上被填成浅蓝楔形 —— 那就是雪与冰所在的地方
  徒步轨迹按它相对雪线的位置分段着色：
      雪线以下（任何时间）→ 中性灰，无雪，碎石 / 草甸
      雪线以上 · 软化前   → 蓝，冰面致密，需要冰爪
      雪线以上 · 软化后   → 橙红，冰层软化、碎石松动，高风险
  「哪段危险」不是被标注出来的，而是轨迹几何上落进了楔子的那一段。

入雪线 / 出雪线时刻不是手填的：用 0.001 h 步长扫一遍 (轨迹 − 雪线) 的符号变化，
再用二分法收敛到微小时刻，门禁里另用解析式复算一次做交叉验证。

数据为自拟示例：路线、剖面、雪线下降速率、软化时刻都是为讲解判据而设，
非真实地形、非真实预报，不构成登山建议。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1080, 1500
MIN_FS = 17

BG = "#EEF2F5"
PANEL = "#FFFFFF"
PANEL2 = "#F5F8FA"
WEDGE = "#DCEAF4"
INK = "#14202B"
INK2 = "#3E5261"
INK3 = "#6E8492"
RULE = "#DDE6EC"
GRID = "#ECF2F6"
REFLINE = "#A9C0CE"

ROCK = "#4E3A1E"   # 雪线以下：无雪（土褐，与蓝/橙三对 ΔE 全部 ≥ 20）
ICE = "#1B7A9E"    # 雪线以上 · 冰面致密
RISK = "#C2410C"   # 雪线以上 · 冰层软化

# ------------------------------------------------------------------ 路线与雪线
# (自 06:00 起的小时数, 海拔 m, 点名)
CPS = [
    (0.0, 1820, "起点营地"),
    (1.5, 2080, "林线上沿"),
    (3.0, 2360, "碎石坡下沿"),
    (4.5, 2700, "冰斗口"),
    (5.75, 2980, "冰塔林"),
    (7.0, 3140, "垭口"),
    (8.5, 2880, "下撤 · 冰斗"),
    (10.75, 2260, "碎石坡下沿"),
    (14.0, 1820, "回到营地"),
]
# 每段水平距离 km（沿坡，不是水平投影）
SEGS_KM = [1.6, 1.8, 2.0, 1.6, 0.9, 1.8, 3.6, 2.3]
SNOW0 = 2400.0     # 06:00 的雪线高度 m
SNOW_DROP = 25.0   # 每小时下降 m/h
SOFT_T = 8.0       # 14:00 冰层开始软化
T_END = 14.0       # 20:00

E_MIN, E_MAX = 1700.0, 3200.0
PLOT_X, PLOT_W = 168.0, 792.0
PLOT_TOP, PLOT_BOT = 372.0, 826.0
PX, PW = 60.0, 960.0


def elev_at(t: float) -> float:
    """按控制点线性插值求某时刻的计划海拔。"""
    if t <= CPS[0][0]:
        return float(CPS[0][1])
    if t >= CPS[-1][0]:
        return float(CPS[-1][1])
    for i in range(len(CPS) - 1):
        t0, e0, _ = CPS[i]
        t1, e1, _ = CPS[i + 1]
        if t <= t1:
            return e0 + (e1 - e0) * (t - t0) / (t1 - t0)
    return float(CPS[-1][1])


def snow_at(t: float) -> float:
    return SNOW0 - SNOW_DROP * t


def diff_at(t: float) -> float:
    return elev_at(t) - snow_at(t)


def find_crossings(step: float = 0.001) -> list:
    """扫 (轨迹 − 雪线) 的符号变化，再用二分法收敛。"""
    out = []
    prev = diff_at(0.0)
    t = step
    while t < T_END:
        cur = diff_at(t)
        if (prev <= 0 < cur) or (prev >= 0 > cur):
            a, b = t - step, t
            for _ in range(60):
                m = (a + b) / 2.0
                if diff_at(a) * diff_at(m) <= 0.0:
                    b = m
                else:
                    a = m
            out.append((a + b) / 2.0)
        prev = cur
        t += step
    return out


def analytic_cross(t0: float, e0: float, t1: float, e1: float) -> float:
    """该线段与雪线交点的解析解。

    轨迹 e0 + k(t − t0)，雪线 SNOW0 − SNOW_DROP·t，联立解出 t。
    只用于门禁里和二分法结果对账，不参与绘制。
    """
    k = (e1 - e0) / (t1 - t0)
    return (SNOW0 - e0 + k * t0) / (k + SNOW_DROP)


def clock(t: float) -> str:
    total = int(round(6 * 60 + t * 60))
    h, m = divmod(total, 60)
    return "%d:%02d" % (h, m)


def dur(h: float) -> str:
    total = int(round(h * 60))
    hh, mm = divmod(total, 60)
    return "%d h %02d min" % (hh, mm)


def px(t: float) -> float:
    return PLOT_X + (t / T_END) * PLOT_W


def py(e: float) -> float:
    return PLOT_BOT - (e - E_MIN) / (E_MAX - E_MIN) * (PLOT_BOT - PLOT_TOP)


def build() -> tuple:
    d = K.Doc(W, H, BG)
    gates: list = []
    t_cross = find_crossings()
    t_in, t_out = t_cross[0], t_cross[-1]
    e_in, e_out = elev_at(t_in), elev_at(t_out)
    e_summit = max(e for _, e, _ in CPS)
    t_summit = [t for t, e, _ in CPS if e == e_summit][0]
    km_up = sum(km for (t0, e0, _), (t1, e1, _), km
                in zip(CPS, CPS[1:], SEGS_KM) if e1 >= e0)
    km_down = sum(km for (t0, e0, _), (t1, e1, _), km
                  in zip(CPS, CPS[1:], SEGS_KM) if e1 < e0)
    km_all = sum(SEGS_KM)
    net_up = e_summit - CPS[0][1]
    margin = SOFT_T - t_summit
    soft_len = t_out - SOFT_T
    below_len = t_in + (T_END - t_out)

    # ------------------------------------------------ 页头
    d.rect(0, 0, W, 124, PANEL)
    d.rect(0, 122, W, 2, ICE)
    d.text(PX, 24, "雪线一日 · 山区徒步窗口预报", 30, INK, bold=True)
    d.text(PX, 68, "纵轴海拔 · 横轴一日时间 · 阴影是积雪与冰区", 17, INK3)
    d.text_r(PX + PW, 26, "折光 · 十张日常　04 / 10", 17, INK3)
    d.text_r(PX + PW, 52, "自拟示例路线与预报", 17, INK3)

    # ------------------------------------------------ KPI
    tiles = [("最高点", "%g m" % e_summit, "%s 抵达垭口" % clock(t_summit), INK),
             ("净爬升", "+%g m" % net_up, "全程 %.1f km" % km_all, INK),
             ("雪线内", dur(t_out - t_in), "%s – %s" % (clock(t_in), clock(t_out)),
              ICE),
             ("高风险窗口", dur(soft_len), "%s – %s" % (clock(SOFT_T),
                                                        clock(t_out)), RISK)]
    for i, (lb, val, sub, col) in enumerate(tiles):
        tx = PX + i * 244
        d.rect(tx, 144, 228, 84, PANEL, radius=14)
        d.text_c(tx + 114, 152, val, 28, col, bold=True)
        d.text_c(tx + 114, 186, lb, 17, INK3)
        d.text_c(tx + 114, 208, sub, 17, INK3)

    # ------------------------------------------------ 主图
    c0, ch = 250, 650
    d.rect(PX, c0, PW, ch, PANEL, radius=18)
    d.text(PX + 22, c0 + 20, "海拔 × 时间", 22, INK, bold=True)
    d.text_r(PX + PW - 22, c0 + 26, "雪线 %.0f m 起，每小时降 %.0f m"
             % (SNOW0, SNOW_DROP), 17, INK3)

    # 三条事件竖线的顶部标签
    events = [(t_in, "入雪线", "装冰爪", ROCK),
              (SOFT_T, "冰层软化", "冰面变软", RISK),
              (t_out, "出雪线", "卸冰爪", ROCK)]
    for t, name, sub, col in events:
        cx = px(t)
        d.text_c(cx, c0 + 58, "%s %s" % (clock(t), name), 17, col, bold=True)
        d.text_c(cx, c0 + 82, sub, 17, INK3)

    # 网格
    for g in (2000, 2300, 2600, 2900):
        d.line_h(PLOT_X, PLOT_X + PLOT_W, py(g), GRID, w=1)
    # 积雪与冰楔
    d.fill([(PLOT_X, PLOT_TOP), (PLOT_X + PLOT_W, PLOT_TOP),
            (PLOT_X + PLOT_W, py(snow_at(T_END))), (PLOT_X, py(snow_at(0.0)))],
           WEDGE, step=1, owner="wedge")
    # 雪线
    d.stroke([(PLOT_X, py(snow_at(0.0))), (PLOT_X + PLOT_W, py(snow_at(T_END)))],
             INK2, width=2, step=1, owner="snowline")
    d.text(PLOT_X + 10, py(snow_at(0.0)) - 26, "雪线", 17, INK2, bold=True)

    # 纵轴
    d.line_v(PLOT_X, PLOT_TOP, PLOT_BOT, RULE, w=1)
    d.line_v(PLOT_X + PLOT_W, PLOT_TOP, PLOT_BOT, RULE, w=1)
    d.line_h(PLOT_X, PLOT_X + PLOT_W, PLOT_BOT, RULE, w=2)
    for g in (1700, 2000, 2300, 2600, 2900, 3200):
        d.text_r(PLOT_X - 10, py(g) - 8, "%g" % g, 17, INK3)
    d.text_r(PLOT_X - 10, PLOT_TOP - 30, "m", 17, INK3)

    # 事件竖线
    for t, name, sub, col in events:
        d.line_v(px(t), PLOT_TOP, PLOT_BOT, REFLINE, w=1)

    # 轨迹：按状态分三段画
    runs = [(0.0, t_in, ROCK), (t_in, SOFT_T, ICE),
            (SOFT_T, t_out, RISK), (t_out, T_END, ROCK)]
    for a, b, col in runs:
        pts = []
        if a > CPS[0][0]:
            pts.append((px(a), py(elev_at(a))))
        for tt, e, _n in CPS:
            if a < tt < b:
                pts.append((px(tt), py(e)))
        pts.append((px(b), py(elev_at(b))))
        d.stroke(pts, col, width=5, step=2, owner="trace")

    # 控制点
    for i, (t, e, name) in enumerate(CPS):
        d.rect(px(t) - 13, py(e) - 13, 26, 26, PANEL, radius=13,
               border="3 SOLID #FFFFFF", owner="cp")
        d.text_c(px(t), py(e) - 10, "%d" % (i + 1), 17, INK, bold=True)
    d.text_r(px(t_summit) - 20, py(e_summit) - 9, "垭口 %g m" % e_summit, 17,
             INK, bold=True)

    # 横轴
    for k in range(8):
        d.text_c(px(k * 2), PLOT_BOT + 22, "%02d:00" % (6 + k * 2), 17, INK3)
    d.text(PX + 22, PLOT_BOT + 50,
           "轨迹 = 计划日程（9 个控制点线性插值）　·　阴影 = 积雪与冰区", 17,
           INK3)

    # ------------------------------------------------ 三段状态
    s0, sh = 920, 152
    d.rect(PX, s0, PW, sh, PANEL, radius=18)
    d.text(PX + 22, s0 + 20, "三段状态 · 时刻由雪线与软化时刻算出", 20, INK,
           bold=True)
    rows = [(ROCK, "雪线以下 · 无雪", "%s–%s、%s–%s"
             % (clock(0.0), clock(t_in), clock(t_out), clock(T_END)),
             dur(below_len)),
            (ICE, "雪线以上 · 冰面致密", "%s–%s" % (clock(t_in), clock(SOFT_T)),
             dur(SOFT_T - t_in)),
            (RISK, "雪线以上 · 冰层软化", "%s–%s" % (clock(SOFT_T), clock(t_out)),
             dur(soft_len))]
    yy = s0 + 62
    for col, nm, win, dd in rows:
        d.rect(PX + 22, yy + 1, 14, 14, col, radius=7)
        d.text(PX + 50, yy, nm, 17, INK, bold=True)
        d.text_r(PX + PW - 210, yy, win, 17, INK2)
        d.text_r(PX + PW - 22, yy, dd, 17, col, bold=True)
        yy += 34

    # ------------------------------------------------ 关键节点
    k0, kh = 1094, 298
    d.rect(PX, k0, PW, kh, PANEL, radius=18)
    d.text(PX + 22, k0 + 20, "关键节点 · 这些时刻是算出来的，不是估的", 20, INK,
           bold=True)
    d.text_r(PX + PW - 22, k0 + 26, "余量 %s" % dur(margin), 17, RISK,
             bold=True)
    nodes = [("06:00", "出发 · 起点营地，雪线以下", "%g m" % CPS[0][1], INK),
             (clock(t_in), "入雪线 · 装冰爪", "%g m" % round(e_in), ICE),
             (clock(t_summit), "垭口 · 全程最高点", "%g m" % e_summit, INK),
             (clock(SOFT_T), "冰层开始软化 · 必须已下撤", "—", RISK),
             (clock(t_out), "出雪线 · 卸冰爪", "%g m" % round(e_out), ICE),
             (clock(T_END), "回到营地", "%g m" % CPS[-1][1], INK)]
    yy = k0 + 62
    for tm, desc, el, col in nodes:
        d.rect(PX + 22, yy + 3, 8, 20, col, radius=4)
        d.text(PX + 44, yy, tm, 19, INK, bold=True)
        d.text(PX + 124, yy + 1, desc, 17, INK2)
        d.text_r(PX + PW - 22, yy + 1, el, 17, INK3)
        if tm != clock(T_END):
            d.line_h(PX + 22, PX + PW - 22, yy + 32, RULE, w=1)
        yy += 40

    # ------------------------------------------------ 页脚
    d.text(PX, 1414,
           "判据：雪线以上 + 14:00 之后 = 高风险。若余量用尽（14:00 才下撤），"
           "下撤全程 %s 都在软化区。" % dur(soft_len), 17, INK2, bold=True)
    d.text(PX, 1442,
           "路线、剖面、雪线下降速率与软化时刻均为自拟示例，非真实地形与真实预报，"
           "不构成登山建议。", 17, INK3)
    d.text_r(PX + PW, 1468, "示意日 2026-10-22 · 出图 2026-10-22", 17, INK3)

    # ------------------------------------------------ 专项门禁
    # 自定义门禁用 -cNN 命名空间，避免与 dry_run 的 -01..-06 撞号。
    K.gate(gates, "case-04-c01", "控制点时间严格递增、海拔单峰（垭口唯一最高）",
           all(CPS[i][0] < CPS[i + 1][0] for i in range(len(CPS) - 1))
           and sum(1 for _t, e, _n in CPS if e == e_summit) == 1
           and e_summit == max(e for _t, e, _n in CPS),
           "峰值 %g m @ %s" % (e_summit, clock(t_summit)))
    snow_ok = all(abs(snow_at(t) - (SNOW0 - SNOW_DROP * t)) < 1e-9
                  for t in (0.0, 3.5, 7.0, 11.0, 14.0))
    K.gate(gates, "case-04-c02", "雪线 = 2400 − 25·t，全时段复算一致", snow_ok,
           "%.0f → %.0f m" % (snow_at(0.0), snow_at(T_END)))
    K.gate(gates, "case-04-c03", "恰好两次穿越雪线，一上一下、起点与终点都在雪线以下",
           len(t_cross) == 2 and diff_at(0.0) < 0
           and all(abs(diff_at(t)) < 0.5 for t in t_cross)
           and diff_at(t_out + 0.1) < 0,
           "入 %s / 出 %s" % (clock(t_in), clock(t_out)))
    t_in_a = analytic_cross(CPS[1][0], CPS[1][1], CPS[2][0], CPS[2][1])
    t_out_a = analytic_cross(CPS[-2][0], CPS[-2][1], CPS[-1][0], CPS[-1][1])
    K.gate(gates, "case-04-c04", "二分法求得的穿越时刻与解析解一致（差 < 1 秒）",
           abs(t_in - t_in_a) < 1e-3 and abs(t_out - t_out_a) < 1e-3,
           "入 %s vs %s · 出 %s vs %s" % (clock(t_in), clock(t_in_a),
                                          clock(t_out), clock(t_out_a)))
    K.gate(gates, "case-04-c05", "穿越点海拔与雪线高度重合（差 < 1 m）",
           abs(e_in - snow_at(t_in)) < 1.0 and abs(e_out - snow_at(t_out)) < 1.0,
           "入 %.1f vs %.1f · 出 %.1f vs %.1f"
           % (e_in, snow_at(t_in), e_out, snow_at(t_out)))
    tot = below_len + (SOFT_T - t_in) + soft_len
    K.gate(gates, "case-04-c06", "三段时长相加 = 全程 %s" % dur(T_END),
           abs(tot - T_END) < 1e-9, "%s = %.4f h" % (dur(tot), tot))
    K.gate(gates, "case-04-c07", "雪线内（入线到出线）全程在雪线以上",
           all(diff_at(t) > 0 for t in
               (t_in + 0.05, 5.0, 7.0, SOFT_T, 10.0, t_out - 0.05)),
           "min diff %.1f m"
           % min(diff_at(t) for t in (t_in + 0.05, 5.0, 7.0, SOFT_T, 10.0,
                                      t_out - 0.05)))
    K.gate(gates, "case-04-c08", "距离合计 %.1f km = 上行 %.1f + 下行 %.1f"
           % (km_all, km_up, km_down),
           abs(km_all - (km_up + km_down)) < 1e-9
           and abs(km_all - 15.6) < 1e-9
           and abs(km_up - 7.9) < 1e-9 and abs(km_down - 7.7) < 1e-9,
           "%.1f = %.1f + %.1f" % (km_all, km_up, km_down))
    K.gate(gates, "case-04-c09", "净爬升 = 最高点 − 起点 = %g m" % net_up,
           abs(net_up - (e_summit - CPS[0][1])) < 1e-9
           and abs(net_up - 1320) < 1e-9, "%g m" % net_up)
    K.gate(gates, "case-04-c10", "到顶余量 = 软化时刻 − 到顶时刻 = %s，为正"
           % dur(margin),
           margin > 0 and abs(margin - 1.0) < 1e-9, "%s" % dur(margin))
    K.gate(gates, "case-04-c11", "高风险窗口 = 出雪线 − 软化时刻 = %s" % dur(soft_len),
           abs(soft_len - (t_out_a - SOFT_T)) < 1e-3, "%s" % dur(soft_len))
    K.gate(gates, "case-04-c12", "三档状态色与白色面板对比 ≥ 4.5",
           all(K.contrast(c, PANEL) >= 4.5 for c in (ROCK, ICE, RISK)),
           " ".join("%s=%.2f" % (c, K.contrast(c, PANEL))
                    for c in (ROCK, ICE, RISK)))
    K.gate(gates, "case-04-c13", "三档状态色在积雪楔上图形对比 ≥ 3.0",
           all(K.contrast(c, WEDGE) >= 3.0 for c in (ROCK, ICE, RISK)),
           " ".join("%s=%.2f" % (c, K.contrast(c, WEDGE))
                    for c in (ROCK, ICE, RISK)))
    K.gate(gates, "case-04-c14", "三档状态都以文字名 + 时刻区间印刷（不只靠颜色）",
           all(nm in [x["text"] for x in d.texts] for _c, nm, _w, _dd in rows)
           and all(win in [x["text"] for x in d.texts]
                   for _c, nm, win, _dd in rows), "")
    K.check_palette("case-04", [(ROCK, ICE), (ROCK, RISK), (ICE, RISK)], gates,
                    min_deutan=20.0, min_tritan=20.0, min_normal=22.0)
    gates = K.dry_run(d, "case-04", MIN_FS, gates)
    return d, gates, "首版：海拔×时间 + 积雪冰楔 + 三段状态轨迹"


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc, gates, note = build()
    print("gates=%s" % K.save_gates("case-04", gates, note))
    K.assert_gates(gates, "case-04")
    if "--dry" in sys.argv:
        return 0
    st = doc.stats()
    print("parts=%d texts=%d shapes=%d dsl=%d" % (st["parts"], st["texts"],
                                                   st["shapes"],
                                                   len(doc.build())))
    rec = K.render_case("case-04", doc, "case-04-snowline-day",
                        "渲染 case-04 雪线一日徒步窗口预报", attempt_note=note)
    print("status=%s bytes=%s parts=%d ms=%s"
          % (rec["http_status"], rec.get("png_bytes"), rec["parts"],
             rec.get("elapsed_ms")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
