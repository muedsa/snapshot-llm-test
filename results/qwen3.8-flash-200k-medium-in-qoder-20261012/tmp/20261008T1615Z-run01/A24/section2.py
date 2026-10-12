# ---------------------------------------------------------------- 决策简报
W2, H2 = 1200, 1600
d2 = Doc(W2, H2, bg=None)
d2.P.update({"card": "#0C1730", "card2": "#0A1428", "border": "#1C2C4A"})
Q = d2.P
board_shell(d2, W2, H2, None, "发布日决策简报 · 2026-11-07",
            [("达成 %d 分钟 / 下界 %d 分钟" % (MS, BOUNDS["lower_bound_overall"]), Q["t1"], 24),
             ("完成 %s · 截止 16:00" % clock(MS), Q["amber"], 24)])

STATS = [("完成时间", clock(MS), "开工后 %d 分钟" % MS, Q["amber"]),
         ("剩余缓冲", "%d 分钟" % BUFFER, "占窗口 %.1f%%" % (100.0 * BUFFER / WINDOW), Q["green"]),
         ("总工作量", "%d 分钟" % BOUNDS["total_work_min"],
          "设计%d·工程%d" % (LOAD["design"], LOAD["engineering"]), Q["cyan"]),
         ("达成/下界", "%d / %d" % (MS, BOUNDS["lower_bound_overall"]),
          "穷举最优·多5分钟", Q["violet"])]
sw = (1120 - 3 * 16) / 4
for k, (lab, big, sub, col) in enumerate(STATS):
    bx = 40 + k * (sw + 16)
    d2.pos(bx, 150, sw, 116, d2.card(sw, 116, color=Q["card"], radius=12))
    d2.label(bx + 16, 162, sw - 32, 30, lab, Q["t2"], 24)
    d2.label(bx + 16, 192, sw - 32, 46, big, col, 34, "BOLD")
    d2.label(bx + 16, 238, sw - 32, 30, sub, Q["t1"], 24)
    tf.check("stat%d" % k, big, 34, sw - 32, 46)
    tf.check("statb%d" % k, sub, 24, sw - 32, 30)

# 依赖概览
LAYER = {"R01": 0, "R02": 0, "R03": 1, "R04": 1, "R05": 1, "R06": 2, "R07": 2,
         "R08": 3, "R09": 3, "R10": 4, "R11": 4, "R12": 5}
DEPS = {i: ROWS[i]["depends"] for i in ROWS}
CP = set()
for a, b in zip(BOUNDS["critical_path"].split("->"), BOUNDS["critical_path"].split("->")[1:]):
    CP.add((a, b))
BY_LAYER = {}
for i, L in LAYER.items():
    BY_LAYER.setdefault(L, []).append(i)
CY2, CH2 = 276, 440
d2.pos(40, CY2, 1120, CH2, d2.card(1120, CH2, color=Q["card2"], radius=14))
d2.label(58, CY2 + 14, 620, 32, "依赖概览（按编号索引，左→右为先决层次）", Q["t0"], 28, "BOLD")
d2.label(700, CY2 + 16, 440, 30, "青＝design 绿＝engineering", Q["t1"], 24, "END")
d2.label(58, CY2 + 48, 1084, 30,
         "琥珀粗边＝关键路径 %d 分钟 · 琥珀点＝可任选团队的柔性任务（R05→engineering，R09/R12→design）"
         % BOUNDS["critical_path_no_resource_min"], Q["amber"], 24)
NW2, NH2 = 118, 44
colw = 1120.0 / 6
NODE = {}
for L, ids in sorted(BY_LAYER.items()):
    cx = 40 + colw * L + colw / 2
    for s, i in enumerate(ids):
        ny = CY2 + 92 + s * 118
        NODE[i] = (cx, ny)
        d2.pos(cx - NW2 / 2, ny, NW2, NH2,
               d2.box(NW2, NH2, color=TEAM_COLOR[ROWS[i]["team"]], radius=9,
                      align="CENTER", inner=d2.text(i, "#06111F", 24, "BOLD")))
        if len(ROWS[i]["options"]) > 1:
            d2.dot(cx + NW2 / 2 - 2, ny + 2, 14, Q["amber"])
        tf.check("node" + i, ROWS[i]["label"], 24, 176, 30)
        d2.label(cx - 88, ny + NH2 + 2, 176, 30, ROWS[i]["label"], Q["t1"], 24, "CENTER")
        d2.label(cx - 88, ny + NH2 + 30, 176, 26, span(ROWS[i]), Q["t2"], 24, "CENTER")
for i, ps in DEPS.items():
    for p in ps:
        hot = (p, i) in CP
        d2.line(NODE[p][0] + NW2 / 2, NODE[p][1] + NH2 / 2,
                NODE[i][0] - NW2 / 2, NODE[i][1] + NH2 / 2,
                4 if hot else 2, Q["amber"] if hot else "#2A3F63")

# 排程依据
RAT = [
    ("规则口径", "design 与 engineering 各只有一个团队，同团队串行、不可抢占；teams 列两项的"
                 "任务任选其一执行，不占用两个团队；12 项任务按 inputs 原时长完整执行，先决未"
                 "完成不得开始，检查环节没有删减，团队切换不额外计时。"),
    ("求解方法", "枚举 3 个柔性任务的 8 种团队分配 × 两团队各自所有与先决相容的内部顺序，共 "
                 "112 组顺序对（其中 48 组会形成跨团队循环等待、不存在可行排程，跳过后继续），"
                 "每组顺序都取半主动排程：能开工就立刻开工。任何可行排程都隐含一组团队顺序，"
                 "半主动化只会更早，所以这次穷举覆盖全局最优。"),
    ("下界差距", "忽略资源的关键路径 %d 分钟（%s），总工时 %d ÷ 2 团队 = %d，资源无关下界取 %d。"
                 "达成 %d 比下界多 5 分钟：R05 的 30 分钟无论给哪一队，都会把 R07 或 R08 至少"
                 "推后 5 分钟，因此 %d 在本实例不可达——只声明可复核的穷举最优，不夸大结论。"
                 % (BOUNDS["critical_path_no_resource_min"], BOUNDS["critical_path"],
                    BOUNDS["total_work_min"], BOUNDS["lower_bound_work_div_teams"],
                    BOUNDS["lower_bound_overall"], MS, BOUNDS["lower_bound_overall"])),
]
CY3, CH3 = 726, 440
d2.pos(40, CY3, 1120, CH3, d2.card(1120, CH3, color=Q["card"], radius=14))
d2.label(58, CY3 + 14, 500, 32, "排程依据", Q["t0"], 28, "BOLD")
yy = CY3 + 60
for t, body in RAT:
    bw = 1160 - 180 - 20
    nl = tf.lines(body, 24, bw)
    tf.check("rat" + t, body, 24, bw, nl * 34)
    d2.label(58, yy, 118, 30, t, Q["cyan"], 24, "BOLD")
    d2.pos(180, yy - 2, bw, nl * 34,
           d2.box(bw, nl * 34, inner=d2.text(body, Q["t1"], 24, height=34),
                  align="TOP_LEFT"))
    yy += nl * 34 + 14

# 三风险 / 对策
CY4, CH4 = 1176, 344
d2.pos(40, CY4, 1120, CH4, d2.card(1120, CH4, color=Q["card2"], radius=14))
d2.label(58, CY4 + 12, 900, 32, "三风险与对策（inputs/release.json）", Q["t0"], 28, "BOLD")
ry = CY4 + 54
for r in RISKS:
    tk = r["task"]
    d2.pos(58, ry, 100, 40, d2.box(100, 40, color="#4A1D26", radius=8, align="CENTER",
                                   inner=d2.text(r["id"], Q["red"], 24, "BOLD")))
    ttl = "%s %s · %s" % (tk, ROWS[tk]["label"], r["impact"])
    tf.check("risk" + r["id"], ttl, 24, 900, 30)
    d2.label(170, ry + 4, 900, 30, ttl, Q["t0"], 24, "BOLD")
    mit = "对策：" + r["mitigation"]
    tf.check("mit" + r["id"], mit, 24, 900, 30)
    d2.label(170, ry + 38, 900, 30, mit, Q["t1"], 24)
    d2.label(170, ry + 66, 900, 26, "落在 %s，本排程后仍有 %d 分钟缓冲" %
             (span(ROWS[tk]), BUFFER), Q["green"], 24)
    ry += 92
d2.label(40, 1530, 1120, 30, "数据来源 inputs/release.json · 明细 schedule.json / "
         "schedule-audit.json", Q["t2"], 24)
BOARD2 = d2.dsl()
