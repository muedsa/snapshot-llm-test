"""B04 case-02 · 基林曲线：一条被引用最多的实测曲线

受众：新闻编辑、科学记者、任何要在稿子里放一条 CO2 曲线的人。
使用场景：编辑部内部参考页，1600×1050 横向。
用户要完成的事：找到可直接引用的端点数值、确认曲线连续性与量纲、
  知道记录在哪里有真实缺口（2022 年火山喷发）。
手法：曲线与增量条形图全部由下载的 NOAA GML 文件解析而来，非示意图。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-02"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1600, 1050
ser = K.keeling_series()
kids = []
kids += K.water_bg(W, H, horizon=H * 0.22)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 84
kids.append(K.section_mark(2, M, 74, color=K.CYAN))
kids.append(D.text_el("基林曲线：一条被引用最多的实测曲线", x=M, y=110, size=40,
                      color=K.INK, font=K.DISPLAY, ls=-0.8))
kids.append(K.body("每一个点都是年平均值，干空气摩尔分数（ppm），"
                   "由 NOAA 全球监测实验室 Mauna Loa 观测站直接测得。"
                   "下方增量条是同一份文件逐年相减得到的，不是第二组数据。",
                   M, 172, 1060, size=17, color=K.INK_2))

# ============================================================ main chart ====
PL, PR = M, 1188
PT, PB = 320, 622
pmin, pmax = 310.0, 432.0


def cx(year):
    return PL + 56 + (year - ser[0][0]) / (ser[-1][0] - ser[0][0]) * (PR - PL - 56)


def cy(ppm):
    return PB - (ppm - pmin) / (pmax - pmin) * (PB - PT)


for gv in range(320, 433, 20):
    gy = cy(gv)
    kids.append(K.hline(PL, PR, gy, K.A(K.HAIR_2, "88"), 1))
    kids.append(K.mono(str(gv), PL - 6, gy - 8, size=12, color=K.INK_3, w=40,
                       align="RIGHT"))
for yr in range(1960, 2030, 10):
    tx = cx(yr)
    kids.append(K.vline(tx, PB, PB + 7, K.HAIR_2, 1))
    kids.append(K.mono(str(yr), tx - 30, PB + 14, size=12, color=K.INK_3, w=60,
                       align="CENTER"))

curve = [(cx(y), cy(p)) for y, p, _ in ser]
# flat-alpha fill: a stepped alpha per scanline was visible as hard banding.
kids.append(K.fade_area(curve, PB, K.A(K.AMBER, "33"), K.A(K.AMBER, "33")))
kids.append(K.polyline(curve, K.AMBER, 3.4))

# the documented hole in the record
gap_x0, gap_x1 = cx(2022.9), cx(2023.6)
kids.append(D.box(gap_x0, PT, gap_x1 - gap_x0, PB - PT,
                  color=K.A(K.CORAL, "2A")))
for gx_ in (gap_x0, gap_x1):
    kids.append(K.vline(gx_, PT, PB, K.A(K.CORAL, "B0"), 2))
kids.append(K.vline((gap_x0 + gap_x1) / 2, PT - 26, PT - 2, K.CORAL, 2))
kids.append(K.arrow_head((gap_x0 + gap_x1) / 2, PT - 2, 90, K.CORAL, 9))
kids.append(D.text_el("2022-11-29 火山喷发，观测暂停；12 月–2023-07-04",
                      x=gap_x1 - 470, y=PT - 76, size=12.5, color=K.CORAL,
                      font=D.UI, w=470, align="RIGHT"))
kids.append(D.text_el("改用 Maunakea 观测站数据，2023-07 恢复",
                      x=gap_x1 - 470, y=PT - 56, size=12.5, color=K.CORAL,
                      font=D.UI, w=470, align="RIGHT"))

for yr, pv, up in [(ser[0][0], ser[0][1], True), (ser[-1][0], ser[-1][1], False)]:
    mx, my = cx(yr), cy(pv)
    kids.append(K.circle(mx, my, 7.5, K.ABYSS, border=K.AMBER, bw=2))
    kids.append(K.circle(mx, my, 3, K.AMBER))
    dx = 12 if up else -52
    kids.append(K.mono("'%02d" % (yr % 100), mx + dx, my + (10 if up else -2),
                       size=13, color=K.AMBER))

# 400 ppm crossing, linear interpolation between adjacent annual means
for i in range(1, len(ser)):
    (y0, p0, _), (y1, p1, _) = ser[i - 1], ser[i]
    if p0 < 400.0 <= p1:
        t = (400.0 - p0) / (p1 - p0)
        hx, hyear = cx(y0 + t * (y1 - y0)), y0 + t * (y1 - y0)
        break
kids.append(K.vline(hx, cy(400) - 18, PB, K.A(K.MINT, "99"), 2))
kids.append(K.mono("400 ppm", hx + 9, PB + 14, size=12, color=K.MINT, w=90))
kids.append(K.mono("%.1f 年（插值）" % hyear, hx + 9, PB + 32, size=12,
                   color=K.MINT, w=170))

# ========================================================== readout panel ===
RX, RW = 1224, W - M - 1224
kids.append(K.panel(RX, PT - 24, RW, PB - PT + 24, fill=K.DEEP))
kids.append(K.kicker("端点读数 · 可直接引用", RX + 22, PT - 2, size=11,
                     color=K.CYAN, w=RW - 44))
rows = [("记录起点 1959", "%.2f" % ser[0][1], "ppm"),
        ("记录终点 2025", "%.2f" % ser[-1][1], "ppm"),
        ("66 年累计增幅", "%.2f" % (ser[-1][1] - ser[0][1]), "ppm"),
        ("相对增幅", "+%.1f%%" % ((ser[-1][1] / ser[0][1] - 1) * 100), ""),
        ("原始不确定度", "%.2f" % ser[0][2], "ppm")]
for i, (lab, val, unit) in enumerate(rows):
    yy = PT + 26 + i * 58
    kids.append(K.mono(lab, RX + 22, yy, size=11.5, color=K.INK_3, w=RW - 44))
    kids.append(K.mono(val, RX + 22, yy + 15, size=27, color=K.INK))
    if unit:
        kids.append(K.mono(unit, RX + 22 + D.est_width(val, 27) + 8, yy + 26,
                           size=13, color=K.INK_3))
    if i < len(rows) - 1:
        kids.append(K.hline(RX + 22, RX + RW - 22, yy + 45, K.A(K.HAIR, "AA"), 1))

# ======================================================== growth bars =======
GY0, GY1 = 736, 872
kids.append(K.hline(M, W - M, GY0 - 34, K.HAIR, 1))
kids.append(K.kicker("逐年增量 · 算自同一份文件 (ppm/yr)", M, GY0 - 12, size=12,
                     color=K.AMBER, w=520))
gr = [(ser[i][0], ser[i][1] - ser[i - 1][1]) for i in range(1, len(ser))]
gmax = max(v for _, v in gr)
bw = (W - M - M) / len(gr)


def gx(i):
    return M + i * bw


kids.append(K.hline(M, W - M, GY1, K.A(K.HAIR_2, "AA"), 1))
for i, (yr, v) in enumerate(gr):
    h = v / gmax * (GY1 - GY0 - 40)
    kids.append(D.box(gx(i) + 1.5, GY1 - h, bw - 3.0, h,
                      color=K.AMBER if yr < 2020 else K.CORAL, radius=1.5))
kids.append(K.mono("0", M - 42, GY1 - 6, size=11, color=K.INK_3, w=34,
                   align="RIGHT"))
kids.append(K.mono("%.2f" % gmax, W - M - 120, GY0 + 4, size=11,
                   color=K.INK_3, w=120, align="RIGHT"))
kids.append(K.mono("1958-03 由 C. D. Keeling 启动；1974-05 起 NOAA 平行测量至今",
                   M, GY1 + 20, size=12, color=K.INK_3, w=600))
kids.append(K.legend([("2020 前", K.AMBER), ("2020 后", K.CORAL)], W - M - 200,
                     GY1 + 16, size=12, gap=16))

# ============================================================== footer =====
note = ("数据文件 research/gml-co2-annmean-mlo.txt，由本任务真实 GET "
        "https://www.gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt 取得（HTTP 200）。"
        "记录说明来自 NOAA GML Trends 页：月度均值由日均值的样本平均得到，只采用「背景条件」时段，"
        "单位为干空气摩尔分数 ppm；2022-11-29 起 Mauna Loa 因火山喷发停测，"
        "2022-12 至 2023-07-04 改用 Maunakea 观测站（约 21 英里外）数据，2023-07 恢复。"
        "400 ppm 交点为本图在相邻两年年均值之间线性插值的估计，非官方公布值；"
        "逐年增量 = 后一年年均值 − 前一年年均值。")
kids.append(K.hline(M, W - M, H - 116, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 98, W - 2 * M, size=11, color=K.INK_3)
kids.append(src)
kids.append(K.kicker("B04 CASE-02 · 02 证据 / EVIDENCE", M, H - 32, size=11,
                     color=K.INK_3))

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
