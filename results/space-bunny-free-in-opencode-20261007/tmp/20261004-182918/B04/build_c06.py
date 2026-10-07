"""B04 case-06 · 2100 年的分岔点在哪

受众：需要做排放路径判断的政策与产业分析读者。
使用场景：1600×1060 横版，政策简报插页、董事会材料附录。
用户要完成的事：看清「同一个今天」在不同排放路径下会走到哪里，
  并分辨哪些数字来自来源、哪些只是定性判断、哪些本图没有取到。
手法：pH 与 Ωarag 两张共享横轴的堆叠投影图（实线=观测锚点，虚线=模式投影）
  + 两组独立来源的情景对照 + 一张明确标出「未取」的情景表。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S
import okit as K

TASK, CASE = "B04", "case-06"
OUT = os.path.join(S.OUT_ROOT, TASK, CASE)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
S.set_current(TASK, case=CASE)

W, H = 1600, 1060
kids = []
kids += K.water_bg(W, H, warm=0.20, horizon=H * 0.50)
kids.append(K.grain(W, H, step=23, alpha="07"))

M = 84
kids.append(K.section_mark(6, M, 66, color=K.CYAN))
kids.append(K.kicker("B04 CASE-06 · 06 未来 / SCENARIO", W - M - 350, 68, size=11,
                     color=K.INK_3, w=350, align="RIGHT"))
kids.append(D.text_el("2100 年的分岔点在哪", x=M, y=100, size=42, color=K.INK,
                      font=K.DISPLAY, ls=-0.9))
kids.append(K.body("现在这个状态是所有情景共同的起点。分岔不是自然发生的，"
                   "它由接下来九十年的排放决定——下面每个端点都标注了来源。",
                   M, 162, 1180, size=18, color=K.INK_2))

X0, X1 = M + 96, M + 926


def fx(year):
    return X0 + (year - 1750) / 350.0 * (X1 - X0)


PLOTS = [
    dict(y0=258, y1=506, lo=7.55, hi=8.30, ticks=[7.6, 7.8, 8.0, 8.2],
         col=K.CYAN, name="表层 pH",
         obs=[(1750, 8.19), (2010, 8.07)],
         proj=[("SSP1-1.9", 8.06, K.MINT), ("SSP5-8.5", 7.68, K.CORAL)]),
    dict(y0=560, y1=808, lo=1.2, hi=3.8, ticks=[1.5, 2.0, 2.5, 3.0, 3.5],
         col=K.AMBER, name="表层 Ωarag",
         obs=[(1750, 3.6), (2010, 3.0)],
         proj=[("SSP1-1.9", 2.9, K.MINT), ("SSP5-8.5", 1.6, K.CORAL)]),
]

for pi, P in enumerate(PLOTS):
    y0, y1, lo, hi = P["y0"], P["y1"], P["lo"], P["hi"]

    def fy(v, y0=y0, y1=y1, lo=lo, hi=hi):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)

    for gv in P["ticks"]:
        gy = fy(gv)
        kids.append(K.hline(X0, X1, gy, K.A(K.HAIR_2, "88"), 1))
        kids.append(K.mono("%.1f" % gv, X0 - 62, gy - 8, size=12,
                           color=P["col"], w=54, align="RIGHT"))
    kids.append(K.kicker(P["name"], X0 - 62, y0 - 30, size=12, color=P["col"],
                         w=190, align="RIGHT"))
    kids.append(K.hline(X0, X1, y1, K.A(K.HAIR_2, "CC"), 2))
    kids.append(D.box(X0, y0, X1 - X0, y1 - y0, color=K.A(K.ABYSS, "40")))
    # observed spine
    kids.append(K.polyline([(fx(y), fy(v)) for y, v in P["obs"]], P["col"], 3.6))
    for y, v in P["obs"]:
        kids.append(K.circle(fx(y), fy(v), 5.5, P["col"]))
    # the corridor between the two sourced 2100 endpoints
    kids.append(D.polygon([(fx(2010), fy(P["obs"][1][1])),
                           (fx(2100), fy(P["proj"][0][1])),
                           (fx(2100), fy(P["proj"][1][1]))],
                          K.A(K.AMBER, "16")))
    # projections, dashed by construction: short dashes along the path
    for name, v210, col in P["proj"]:
        x_a, y_a = fx(2010), fy(P["obs"][1][1])
        x_b, y_b = fx(2100), fy(v210)
        steps = 26
        for i in range(0, steps, 2):
            ta, tb = i / steps, (i + 1) / steps
            kids.append(K.seg(x_a + (x_b - x_a) * ta, y_a + (y_b - y_a) * ta,
                              x_a + (x_b - x_a) * tb, y_a + (y_b - y_a) * tb,
                              K.A(col, "FF"), 3.0))
        kids.append(K.circle(x_b, y_b, 6, col))
        ly = y_b - 34 if pi == 0 else y_b + 14
        fmt = "%.2f" if pi == 0 else "%.1f"
        kids.append(K.mono("%s  →  %s" % (name, fmt % v210), x_b - 250, ly,
                           size=13, color=col, w=236, align="RIGHT"))
        if pi == 0:
            kids.append(D.text_el("低排放·高减缓", x=x_b - 250, y=ly + 18,
                              size=11.5, color=K.INK_3, font=D.UI, w=236,
                              align="RIGHT"))
        else:
            kids.append(D.text_el("高排放·低减缓", x=x_b - 250, y=ly + 18,
                              size=11.5, color=K.INK_3, font=D.UI, w=236,
                              align="RIGHT"))
    # endpoint values on the observed spine
    for j, (y, v) in enumerate(P["obs"]):
        ox = fx(y) + 12
        oy = fy(v) - (26 if j == 0 else 16)
        if j == 1:
            ox = fx(y) - 150
        kids.append(K.mono("%d · %.2f" % (y, v), ox, oy, size=12.5,
                           color=P["col"]))

# shared x axis
for yr in [1750, 1850, 1950, 2000, 2050, 2100]:
    tx = fx(yr)
    kids.append(K.vline(tx, PLOTS[1]["y1"], PLOTS[1]["y1"] + 8, K.HAIR_2, 1))
    kids.append(K.mono(str(yr), tx - 34, PLOTS[1]["y1"] + 16, size=11.5,
                       color=K.INK_3, w=68, align="CENTER"))
kids.append(K.mono("观测锚点 = 实线；模式投影 = 虚线（不是预测，也不是承诺）",
                   X0, PLOTS[1]["y1"] + 46, size=12.5, color=K.INK_3, w=700))

# ============================================================ right column ===
RX = M + 966
RW = W - M - RX
kids.append(K.panel(RX, 228, RW, 250, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("第二组独立对照 · IPCC SROCC", RX + 20, 246, size=11,
                     color=K.CYAN, w=RW - 40))
kids.append(K.body("SROCC 用 RCP 情景、报相对 2006–2015 的变化量，"
                   "与左边那组口径不同，不能相减，但方向一致。",
                   RX + 20, 274, RW - 40, size=12, color=K.INK_3))
for i, (sc, lo_, hi_, col, tail) in enumerate(
        [("RCP2.6", -0.036, -0.042, K.MINT, "SROCC：这一组「基本可避免」"),
         ("RCP8.5", -0.287, -0.290, K.CORAL, "SROCC：高纬度将变得「腐蚀性」")]):
    yy = 328 + i * 80
    kids.append(K.mono(sc, RX + 20, yy, size=15, color=col))
    kids.append(K.mono("2081–2100 ΔpH", RX + 20, yy + 20, size=11, color=K.INK_3))
    kids.append(K.num("%.3f ~ %.3f" % (lo_, hi_), RX + 20, yy + 34, size=20,
                      color=K.INK))
    kids.append(K.mono(tail, RX + 20, yy + 60, size=10.5, color=col))

kids.append(K.panel(RX, 494, RW, 314, fill=K.A(K.DEEP, "F2")))
kids.append(K.kicker("情景与本图取到的数字", RX + 20, 512, size=11, color=K.CYAN,
                     w=RW - 40))
SCEN = [("SSP1-1.9", "2100 pH 8.06 · Ωarag 2.9（较 2010 −2%）", K.MINT, "已取"),
        ("SSP2-4.5", "未取到可引用的 2100 端点", K.INK_3, "未取"),
        ("SSP3-7.0", "未取到可引用的 2100 端点", K.INK_3, "未取"),
        ("SSP5-8.5", "2100 pH 7.68 · Ωarag 1.6（较 2010 −47%）", K.CORAL, "已取")]
for i, (name, val, col, mark) in enumerate(SCEN):
    yy = 548 + i * 60
    kids.append(K.mono(name, RX + 20, yy, size=13, color=col))
    kids.append(K.mono(mark, RX + RW - 60, yy, size=11, color=col, w=40,
                       align="RIGHT"))
    kids.append(K.body(val, RX + 20, yy + 18, RW - 40, size=11.5,
                       color=K.INK_2))
    if i < 3:
        kids.append(K.hline(RX + 20, RX + RW - 20, yy + 48, K.A(K.HAIR, "99"), 1))

kids.append(K.panel(M, 876, X1 - M, 108, fill=K.A(K.DEEP, "D8")))
kids.append(K.kicker("读法", M + 20, 894, size=11, color=K.AMBER))
kids.append(K.body("实线只连接 1750 与 2010 两个被引用过的数值，中间没有年度数据——"
                   "这张图回答的是「端点在哪」，不是「路径长什么样」。"
                   "琥珀色走廊只表示两个端点之间的范围，不代表真实轨迹："
                   "CMIP6 各模式中间轨迹的差异远大于端点差异。",
                   M + 20, 916, X1 - M - 40, size=12.5, color=K.INK_2))

note = ("pH 与 Ωarag 端点（1750: 8.19 / 3.6；2010: 8.07 / 3.0；2100 SSP1-1.9: 8.06 / 2.9 即 −2%；"
        "2100 SSP5-8.5: 7.68 / 1.6 即 −47%）：Jiang et al. 2023, Global Surface Ocean Acidification "
        "Indicators From 1750 to 2100, JAMES（经检索结果摘要取得，未直接抓取全文）。"
        "SROCC 2081–2100 相对 2006–2015 的 ΔpH（RCP2.6 −0.036~−0.042；RCP8.5 −0.287~−0.29）"
        "与「基本可避免 / 变腐蚀性」的表述：IPCC SROCC 第 5 章（检索结果摘要）。"
        "SSP2-4.5 与 SSP3-7.0 的 2100 端点本任务没有取得可引用数值，图中标注为「未取」，未做插值。")
kids.append(K.hline(M, W - M, H - 62, K.HAIR, 1))
src, _ = K.source_note(note, M, H - 46, W - 2 * M, size=10.5, color=K.INK_3)
kids.append(src)

dsl = K.finish("\n".join(kids), W, H)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=OUT)
print("render", r.get("ok"), r.get("status"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
print("elements~", K.count_elements(dsl))
