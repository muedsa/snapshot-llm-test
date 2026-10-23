"""case-02 阳台七日 · 灌溉窗口与露点（1080×1350 手机竖屏）。

视觉系统：VPD（水汽压亏缺）七日折线 + 一条阈值决策线 + 每日决策图元 + 风速条形。
  判断规则被画进图里而不是只给结论：
      降雨概率 ≥ 70 %        → 让天浇
      VPD ≥ 0.9 kPa 且 风 ≥ 12 km/h → 晨浇（蒸腾强，趁上午浇足）
      其余                   → 傍晚浇（蒸腾弱，避开中午蒸发）
  VPD 由 Magnus-Tetens 近似式算出，不查表：
      es(T) = 0.6108·exp(17.27·T / (T + 237.3))  kPa
      VPD   = es(日平均温) − es(露点)
  每盆水量 = 盆径cm³ × 0.0006 L × (VPD / 3.0)^0.8 × 耐旱系数

关于阈值：0.9 kPa 不是引用某个标准的数值，而是为本例数据范围选的设计参数
（在 22 °C 时相当于相对湿度约 66 %，见门禁 case-02-10 的复算）。
阈值与最近的实测值之间留了 ≥ 0.05 kPa 的间距（门禁 case-02-09），
避免看起来像是照着数据反推出来的线。

数据全部为自拟演示数据：气象值与植物清单都是为展示判据而设，
非真实气象站点、非真实阳台、不宣称实际部署。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1080, 1350
MIN_FS = 15

# ------------------------------------------------------------------ 版面与颜色
BG = "#ECF3EE"
PANEL = "#FFFFFF"
PANEL2 = "#F4F8F5"
GHOST = "#EDF5F1"
INK = "#0F2A22"
INK2 = "#435E52"
INK3 = "#6B8378"
RULE = "#E2EBE5"
GRID = "#EEF5F0"

WATER = "#0E8AA8"      # VPD 曲线
WIND = "#6E858C"      # 风速条形（中性灰，不与任何状态色抢色）
WIND_TICK = "#1F323C"  # 风速阈值竖线

MORN = "#0E8AA8"       # 晨浇
EVE = "#C87A12"        # 傍晚浇
NO = "#2F4450"         # 不浇 / 让天浇

VPD_LINE = 0.9         # 蒸腾强度低/高分界 kPa
WIND_LINE = 12.0       # 强风分界 km/h
RAIN_LINE = 70.0       # 降雨概率分界 %

PX, PW = 60, 960
PLOT_X, PLOT_W = 126, 856
PLOT_TOP, PLOT_BOT = 366, 502
VPD_MAX, WIND_MAX = 1.2, 20.0
BAR_SPAN = 90.0        # 风速条形满标度宽度


def es(t: float) -> float:
    """饱和水汽压 kPa，Magnus-Tetens 近似式。"""
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))


def vpd(tmin: float, tmax: float, td: float) -> float:
    """水汽压亏缺：日平均温的饱和水汽压减露点对应的实际水汽压。"""
    return es((tmin + tmax) / 2.0) - es(td)


def rh_at(t: float, v: float) -> float:
    """给定温度与 VPD，反解相对湿度百分比。"""
    return (es(t) - v) / es(t) * 100.0


def decide(v: float, wind: float, rain: float) -> str:
    """浇水判据：单一规则，图上直接可读。"""
    if rain >= RAIN_LINE:
        return "rain"
    return "morn" if (v >= VPD_LINE and wind >= WIND_LINE) else "eve"


# ------------------------------------------------------------------ 自拟演示数据
# (日期, 星期, 最低温, 最高温, 露点, 风速 km/h, 降雨概率 %, 降雨 mm)
WEEK = [
    ("10-22", "四", 14, 26, 11, 15, 15, 0),
    ("10-23", "五", 15, 27, 12, 17, 10, 0),
    ("10-24", "六", 13, 19, 13, 8, 35, 0),
    ("10-25", "日", 14, 21, 15, 7, 55, 3),
    ("10-26", "一", 14, 18, 15, 12, 75, 18),
    ("10-27", "二", 13, 17, 14, 10, 80, 26),
    ("10-28", "三", 15, 24, 14, 16, 15, 0),
]

# 自拟盆栽：(名称, 盆径 cm, 耐旱系数)
PLANTS = [
    ("罗勒", 16, 1.0), ("番茄", 28, 1.0), ("辣椒", 20, 1.0),
    ("薄荷", 14, 0.7), ("迷迭香", 18, 0.45), ("黄瓜", 24, 1.0),
    ("生菜", 15, 0.7), ("多肉", 12, 0.45),
]


def weekly() -> list:
    out = []
    for i, (date, wk, tmin, tmax, td, wind, rain, mm) in enumerate(WEEK):
        v = vpd(tmin, tmax, td)
        out.append({"i": i, "date": date, "wk": wk, "tmin": tmin, "tmax": tmax,
                    "td": td, "wind": wind, "rain": rain, "mm": mm, "vpd": v,
                    "state": decide(v, wind, rain)})
    return out


def litres(day_vpd: float, dia: float, hardy: float) -> float:
    return dia ** 3 * 0.0006 * (day_vpd / 3.0) ** 0.8 * hardy


# ------------------------------------------------------------------ 每日决策图元
def g_drop(d, cx, y0, col):
    """水滴：上圆下尖。"""
    d.circle(cx, y0 + 9, 9, col, step=1, owner="glyph-drop")
    d.fill([(cx - 7, y0 + 13), (cx + 7, y0 + 13), (cx, y0 + 23)], col,
           step=1, owner="glyph-drop")


def g_sunset(d, cx, y0, col):
    """傍晚：地平线 + 下沉的半日轮。"""
    d.rect(cx - 11, y0 + 18, 22, 2, col, owner="glyph-dusk")
    d.arc(cx, y0 + 17, 5, 11, math.pi, math.tau, col, step=1,
          owner="glyph-dusk")


def g_cloud(d, cx, y0, col):
    """让天浇：雨云。"""
    d.circle(cx - 7, y0 + 9, 6, col, step=1, owner="glyph-rain")
    d.circle(cx + 1, y0 + 7, 7, col, step=1, owner="glyph-rain")
    d.circle(cx + 8, y0 + 10, 5, col, step=1, owner="glyph-rain")
    d.rect(cx - 13, y0 + 9, 24, 6, col, owner="glyph-rain")
    for k in range(3):
        x0 = cx - 8 + k * 8
        d.stroke([(x0, y0 + 18), (x0 - 2, y0 + 23)], col, width=2, step=1,
                 owner="glyph-rain")


GLYPH = {"morn": (g_drop, MORN), "eve": (g_sunset, EVE),
         "rain": (g_cloud, NO)}

# 状态 → (图上的动作名, 颜色)
META = {"morn": ("晨浇", MORN), "eve": ("傍晚浇", EVE), "rain": ("让天浇", NO)}


def py(v: float) -> float:
    return PLOT_BOT - v / VPD_MAX * (PLOT_BOT - PLOT_TOP)


def cx_of(i: int) -> float:
    return PLOT_X + (i + 0.5) * (PLOT_W / 7.0)


# ------------------------------------------------------------------ 版面
def build() -> tuple:
    d = K.Doc(W, H, BG)
    gates: list = []
    D = weekly()

    # ------------------------------------------------ 页头
    d.rect(0, 0, W, 118, PANEL)
    d.rect(0, 116, W, 2, WATER)
    d.text(PX, 26, "阳台七日 · 灌溉窗口与露点", 30, INK, bold=True)
    d.text(PX, 70, "七日水汽压亏缺 VPD 与浇水窗口 · 判据印在图上", 15, INK3)
    d.text_r(PX + PW, 26, "折光 · 十张日常　02 / 10", 15, INK3)
    d.text_r(PX + PW, 50, "自拟演示数据", 15, INK3)

    n_morn = sum(1 for x in D if x["state"] == "morn")
    n_eve = sum(1 for x in D if x["state"] == "eve")
    n_rain = sum(1 for x in D if x["state"] == "rain")
    n_act = n_morn + n_eve
    act_days = [i for i in range(len(D)) if D[i]["state"] != "rain"]
    tot = sum(litres(D[i]["vpd"], p[1], p[2]) for i in act_days for p in PLANTS)
    tiles = [("本周行动", "%d 天" % n_act, INK), ("晨浇", "%d 天" % n_morn, MORN),
             ("傍晚浇", "%d 天" % n_eve, EVE), ("不浇", "%d 天" % n_rain, INK2),
             ("七日总水量", "%.1f L" % round(tot, 1), INK)]
    for i, (lb, val, col) in enumerate(tiles):
        tx = PX + i * 192
        d.rect(tx, 136, 184, 64, PANEL, radius=12)
        d.text_c(tx + 92, 144, val, 22, col, bold=True)
        d.text_c(tx + 92, 176, lb, 15, INK3)

    # ------------------------------------------------ 七日图
    cy0, ch = 218, 418
    d.rect(PX, cy0, PW, ch, PANEL, radius=16)
    d.text(PX + 22, cy0 + 20, "七日水汽压亏缺 VPD", 22, INK, bold=True)
    d.text_r(PX + PW - 22, cy0 + 24, "VPD = es(日均温) − es(露点)　kPa", 15,
             INK3)

    for g in (0.0, 0.3, 0.6, 0.9, 1.2):
        d.line_h(PLOT_X, PLOT_X + PLOT_W, py(g), GRID)

    # 今日列的浅色底
    d.rect(cx_of(0) - PLOT_W / 14, PLOT_TOP - 4, PLOT_W / 7,
           610 - (PLOT_TOP - 4), GHOST, owner="today")

    # 决策线：高于它且风够，才进晨浇
    d.line_h(PLOT_X, PLOT_X + PLOT_W, py(VPD_LINE), EVE, w=2)
    d.text_r(PX + PW - 22, py(VPD_LINE) - 26, "高于此且风 ≥ %g → 晨浇" % WIND_LINE,
             15, EVE, bold=True)

    # VPD 折线与面积
    pts = [(cx_of(x["i"]), py(x["vpd"])) for x in D]
    d.fill([(PLOT_X, PLOT_BOT)] + pts + [(PLOT_X + PLOT_W, PLOT_BOT)],
           "#0E8AA824", step=1, owner="vpd-area")
    d.stroke(pts, WATER, width=3, step=1, owner="vpd-line")
    for p in pts:
        d.circle(p[0], p[1], 6, PANEL, step=1, owner="vpd-dot")
        d.circle(p[0], p[1], 4, WATER, step=1, owner="vpd-dot")

    d.line_v(PLOT_X, PLOT_TOP, PLOT_BOT, RULE, w=1)
    d.line_v(PLOT_X + PLOT_W, PLOT_TOP, PLOT_BOT, RULE, w=1)
    d.line_h(PLOT_X, PLOT_X + PLOT_W, PLOT_BOT, RULE, w=2)
    for g in (0.0, 0.3, 0.6, 0.9, 1.2):
        d.text_r(PLOT_X - 8, py(g) - 8, ("%.1f" % g).rstrip("0").rstrip("."),
                 15, INK3)

    # 每列：VPD 值 / 决策图元 / 日期 / 风速条形
    d.text_r(PLOT_X - 8, 592, "风 km/h", 15, INK3)
    for x in D:
        cx = cx_of(x["i"])
        d.text_c(cx, 518, "%.2f" % x["vpd"], 17, INK2, bold=True)
        gf, gc = GLYPH[x["state"]]
        gf(d, cx, 540, gc)
        d.text_c(cx, 570, "%s 周%s" % (x["date"], x["wk"]), 15, INK3)
        bx = cx - BAR_SPAN / 2
        d.rect(bx, 596, BAR_SPAN, 8, PANEL2, radius=4, owner="wind-track")
        d.rect(bx, 596, BAR_SPAN * x["wind"] / WIND_MAX, 8, WIND, radius=4,
               owner="wind-bar")
        d.line_v(bx + BAR_SPAN * WIND_LINE / WIND_MAX, 592, 608, WIND_TICK,
                 w=1)

    d.text(PX + 22, 616,
           "蓝线 = VPD kPa　·　橙线 = 决策线 %.1f kPa　·　下方条形 = 风速 "
           "km/h（竖线为 %g km/h）" % (VPD_LINE, WIND_LINE), 15, INK3)

    # ------------------------------------------------ 今日决定
    dc0, dh = 652, 150
    t0 = D[0]
    t_name, t_col = META[t0["state"]]
    d.rect(PX, dc0, PW, dh, PANEL, radius=16)
    d.rect(PX, dc0, 6, dh, t_col, radius=3)
    d.text(PX + 26, dc0 + 20, "今日 · %s 周%s" % (t0["date"], t0["wk"]),
           24, INK, bold=True)
    d.text(PX + 26, dc0 + 58,
           "%g→%g °C · 露点 %g °C · 风 %g km/h · 降雨概率 %g%%"
           % (t0["tmin"], t0["tmax"], t0["td"], t0["wind"], t0["rain"]), 16,
           INK2)
    d.text_r(PX + PW - 26, dc0 + 20, "%s · VPD %.2f kPa" % (t_name, t0["vpd"]),
             24, t_col, bold=True)
    d.text_r(PX + PW - 26, dc0 + 58, "共 %d 盆 · 合计 %.2f L"
             % (len(PLANTS), sum(litres(t0["vpd"], p[1], p[2]) for p in PLANTS)),
             16, INK2)
    d.rect(PX + 26, dc0 + 96, PW - 52, 38, PANEL2, radius=8)
    d.text(PX + 40, dc0 + 104,
           "判据：VPD %.2f / %.1f kPa · 风 %g / %g km/h · 降雨 %g / %g%% → %s"
           % (t0["vpd"], VPD_LINE, t0["wind"], int(WIND_LINE), t0["rain"],
              int(RAIN_LINE), t_name), 15, INK2, bold=True)

    # ------------------------------------------------ 八盆水量
    ly0, lh = 818, 328
    d.rect(PX, ly0, PW, lh, PANEL, radius=16)
    d.text(PX + 22, ly0 + 20, "八盆今日水量（%s）" % D[0]["date"], 22, INK,
           bold=True)
    d.text_r(PX + PW - 22, ly0 + 26, "V = 盆径³ × 0.0006 × (VPD ÷ 3)^0.8 × 耐旱",
             15, INK3)

    today_lit = [(nm, dia, hd, litres(D[0]["vpd"], dia, hd))
                 for nm, dia, hd in PLANTS]
    mx_lit = max(v for _, _, _, v in today_lit)
    by = ly0 + 60
    for nm, dia, hd, v in today_lit:
        d.text(PX + 22, by, nm, 18, INK, bold=True)
        d.text(PX + 104, by + 3, "%g cm" % dia, 15, INK3)
        d.text(PX + 190, by + 3, "耐旱 %g" % hd, 15, INK3)
        bx, bw = PX + 320, 400
        d.rect(bx, by + 6, bw, 12, PANEL2, radius=6, owner="lit-track")
        d.rect(bx, by + 6, bw * v / mx_lit, 12, WATER, radius=6,
               owner="lit-bar")
        d.text_r(PX + PW - 22, by + 1, "%.2f L" % v, 17, INK, bold=True)
        by += 30

    d.line_h(PX + 22, PX + PW - 22, by + 4, RULE)
    d.text(PX + 22, by + 14, "合计", 18, INK, bold=True)
    d.text_r(PX + PW - 22, by + 14, "%.2f L" % sum(
        v for _, _, _, v in today_lit), 19, MORN, bold=True)

    # ------------------------------------------------ 判据
    ry0, rh = 1162, 138
    d.rect(PX, ry0, PW, rh, PANEL, radius=16)
    d.text(PX + 22, ry0 + 18, "判据", 22, INK, bold=True)
    rows = [("降雨概率 ≥ %g%%" % RAIN_LINE, "让天浇", NO),
            ("VPD ≥ %.1f kPa 且 风 ≥ %g km/h" % (VPD_LINE, WIND_LINE), "晨浇",
             MORN),
            ("其余", "傍晚浇", EVE)]
    yy = ry0 + 58
    for cond, act, col in rows:
        d.rect(PX + 22, yy + 4, 12, 12, col, radius=6)
        d.text(PX + 44, yy, cond, 16, INK2)
        d.text_r(PX + PW - 22, yy, act, 17, col, bold=True)
        yy += 28

    # ------------------------------------------------ 页脚
    d.text(PX, 1306,
           "气象值、植物清单与水量系数均为自拟演示数据，非真实气象站点；"
           "阈值为本例数据范围选定的设计参数，不构成种植建议。", 15, INK3)
    d.text_r(PX + PW, 1330,
             "es(T) = 0.6108 × exp(17.27 × T ÷ (T + 237.3))　kPa", 15, INK3)

    # ------------------------------------------------ 专项门禁
    shown = {x["i"]: round(x["vpd"], 2) for x in D}
    K.gate(gates, "case-02-01", "图上 VPD 值与 Magnus-Tetens 公式复算一致",
           all(abs(shown[x["i"]] - x["vpd"]) < 0.005 for x in D),
           " ".join("%s=%.3f" % (x["date"], x["vpd"]) for x in D))
    K.gate(gates, "case-02-02", "状态由单一判据唯一确定（雨水优先，"
                                "再比 VPD 与风）",
           all(x["state"] == decide(x["vpd"], x["wind"], x["rain"]) for x in D),
           " ".join(x["state"] for x in D))
    K.gate(gates, "case-02-03", "三档都被数据走到（晨2 / 傍晚3 / 不浇2），"
                                "今日为晨浇",
           (n_morn, n_eve, n_rain) == (2, 3, 2) and D[0]["state"] == "morn",
           "morn=%d eve=%d rain=%d" % (n_morn, n_eve, n_rain))
    K.gate(gates, "case-02-04", "今日每盆水量与七日总水量均由公式复算",
           abs(sum(v for _, _, _, v in today_lit)
               - sum(litres(D[0]["vpd"], p[1], p[2]) for p in PLANTS)) < 1e-9
           and abs(tot - sum(litres(D[i]["vpd"], p[1], p[2])
                             for i in act_days for p in PLANTS)) < 1e-9,
           "今日=%.2f L 七日=%.1f L" % (sum(v for _, _, _, v in today_lit),
                                        tot))
    K.gate(gates, "case-02-05", "水量随盆径单调不减（同耐旱系数）",
           litres(D[0]["vpd"], 16, 1.0) <= litres(D[0]["vpd"], 28, 1.0),
           "%.3f → %.3f" % (litres(D[0]["vpd"], 16, 1.0),
                            litres(D[0]["vpd"], 28, 1.0)))
    dry_i = max(range(len(D)), key=lambda i: D[i]["vpd"])
    wet_i = min(range(len(D)), key=lambda i: D[i]["vpd"])
    K.gate(gates, "case-02-06", "水量随 VPD 单调递增（越干浇得越多）",
           litres(D[dry_i]["vpd"], 28, 1.0) > litres(D[wet_i]["vpd"], 28, 1.0),
           "干日 %.2f → %.3f L；湿日 %.2f → %.3f L"
           % (D[dry_i]["vpd"], litres(D[dry_i]["vpd"], 28, 1.0),
              D[wet_i]["vpd"], litres(D[wet_i]["vpd"], 28, 1.0)))
    K.gate(gates, "case-02-07", "三档行动色与白色面板对比 ≥ 3.0",
           all(K.contrast(c, PANEL) >= 3.0 for c in (MORN, EVE, NO)),
           " ".join("%.1f" % K.contrast(c, PANEL) for c in (MORN, EVE, NO)))
    K.gate(gates, "case-02-08", "三档行动都以文字标签印刷（不只靠颜色）",
           all(act in [t["text"] for t in d.texts] for _, act, _ in rows), "")
    K.gate(gates, "case-02-09", "阈值与最近数据点间隔 ≥ 0.05 kPa（不是照数据反推）",
           all(abs(x["vpd"] - VPD_LINE) >= 0.05 for x in D),
           "最近 %.3f" % min(abs(x["vpd"] - VPD_LINE) for x in D))
    K.gate(gates, "case-02-10", "页脚/正文关于 22 °C 对应相对湿度约 66 % 的说法"
                                "可复算",
           abs(rh_at(22.0, VPD_LINE) - 66.0) <= 1.5,
           "%.1f%%" % rh_at(22.0, VPD_LINE))
    K.gate(gates, "case-02-11", "纵轴 0-%g kPa 单调映射，右轴条形 0-%g km/h 单调"
           % (VPD_MAX, WIND_MAX),
           all(py(a) > py(b) for a, b in ((0.0, 0.3), (0.3, 0.9), (0.9, 1.2)))
           and BAR_SPAN * 8 / WIND_MAX < BAR_SPAN * 17 / WIND_MAX, "")
    K.check_palette("case-02", [(MORN, EVE), (MORN, NO), (EVE, NO)], gates,
                    min_deutan=12.0, min_tritan=10.0, min_normal=18.0)
    gates = K.dry_run(d, "case-02", MIN_FS, gates)
    return d, gates, "首版：VPD 折线 + 决策线 + 每日决策图元 + 风速条形"


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc, gates, note = build()
    print("VPD 复算:", " ".join("%s=%.3f" % (x["date"], x["vpd"])
                                for x in weekly()))
    print("状态:", " ".join(x["state"] for x in weekly()))
    print("22 °C 下 VPD 0.9 对应相对湿度: %.1f%%" % rh_at(22.0, VPD_LINE))
    print("今日八盆:", " ".join(
        "%s=%.2f" % (nm, round(litres(weekly()[0]["vpd"], dia, hd), 2))
        for nm, dia, hd in PLANTS),
        "合计=%.2f L" % sum(litres(weekly()[0]["vpd"], p[1], p[2])
                            for p in PLANTS))
    # 先落盘再断言：失败的门禁轮次也要留下证据，不能因为 assert 抛错就丢掉。
    print("gates=%s" % K.save_gates("case-02", gates, note))
    K.assert_gates(gates, "case-02")
    if "--dry" in sys.argv:
        return 0
    st = doc.stats()
    print("parts=%d texts=%d shapes=%d dsl=%d" % (st["parts"], st["texts"],
                                                   st["shapes"],
                                                   len(doc.build())))
    rec = K.render_case("case-02", doc, "case-02-balcony-vpd",
                        "渲染 case-02 阳台七日灌溉窗口与露点", attempt_note=note)
    print("status=%s bytes=%s parts=%d ms=%s"
          % (rec["http_status"], rec.get("png_bytes"), rec["parts"],
             rec.get("elapsed_ms")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
