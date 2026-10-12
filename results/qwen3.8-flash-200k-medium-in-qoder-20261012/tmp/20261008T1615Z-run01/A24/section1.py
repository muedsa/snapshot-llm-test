CY, CH = 112, 636                    # 主卡位置与高度
d.pos(32, CY, 1856, CH, d.card(1856, CH, color=P["card2"], radius=16))
PX0, PX1 = 32 + 170, 32 + 1830       # 绘图区绝对左右界
SC = (PX1 - PX0) / WINDOW            # px / min


def px(m):
    return PX0 + SC * m


AX_Y = CY + 14                       # 小时刻度
LT = CY + 40                         # 网格顶端
D_GAPY, D_YB, D_CA, D_CB = CY + 56, CY + 84, CY + 162, CY + 216
E_GAPY, E_YB, E_CA, E_CB = CY + 280, CY + 308, CY + 386, CY + 440
PB = CY + 498                        # 网格底端
BUF_Y, FIN_Y, LEG_Y = CY + 508, CY + 546, CY + 580
BH = 72

for m in range(0, WINDOW + 1, 30):
    major = m % 60 == 0
    d.line(px(m), LT, px(m), PB, 2 if major else 1,
           P["grid"] if not major else "#22375C")
    if major:
        d.label(px(m) - 40, AX_Y, 80, 26, clock(m), P["t1"], 22, align="CENTER")

LANES = {"design": (D_GAPY, D_YB, D_CA, D_CB),
         "engineering": (E_GAPY, E_YB, E_CA, E_CB)}
for tm, (gy, yb, ca, cb) in LANES.items():
    d.label(48, yb + 2, 116, 30, TEAM_CN[tm], TEAM_COLOR[tm], 26, "BOLD")
    d.label(48, yb + 34, 116, 24, tm, TEAM_COLOR[tm], 20)
    n_ = [i for i in ORDER if ROWS[i]["team"] == tm]
    d.label(48, yb + 60, 116, 24, "%d 项" % len(n_), P["t1"], 20)
    d.label(48, yb + 84, 116, 24, "%d min" % LOAD[tm], P["t1"], 20)
    d.rect(40, yb - 8, 4, 60 + 24, TEAM_COLOR[tm])

CAP = {("design", 0): D_CA, ("design", 1): D_CB,
       ("engineering", 0): E_CA, ("engineering", 1): E_CB}
placed = {}
for i in ORDER:
    r = ROWS[i]
    x0, x1 = px(r["start_min"]), px(r["end_min"])
    gy, yb, ca, cb = LANES[r["team"]]
    d.pos(x0, yb, x1 - x0, BH, d.box(x1 - x0, BH, color=TEAM_COLOR[r["team"]],
                                     radius=8, align="CENTER",
                                     inner=d.text(r["id"], "#06111F", 24, "BOLD")))
    if len(r["options"]) > 1:
        d.dot(x1 - 10, yb + 10, 12, "#FBBF24")
    if r["id"] in RISK_BY_TASK:
        d.dot(x0 + 10, yb + BH - 10, 12, "#F87171")
    row = placed.get(r["team"], 0)
    placed[r["team"]] = (row + 1) % 2
    cap_y = CAP[(r["team"], row)]
    bx = min(max(x0 - 12, PX0 - 6), PX1 - 214)
    tf.check(i, r["label"], 22, 210, 28)
    tf.check(i + "t", span(r) + " · %dmin" % r["minutes"], 20, 210, 24)
    d.label(bx, cap_y, 210, 28, r["label"], P["t0"], 22, "BOLD")
    d.label(bx, cap_y + 28, 210, 24, span(r) + " · %dmin" % r["minutes"], P["t1"], 20)
    d.line(x0 + (x1 - x0) / 2, yb + BH, x0 + (x1 - x0) / 2, cap_y - 2, 1, "#31496E")
    if (x1 - x0) >= 150:
        d.pos(x0, yb + BH - 26, x1 - x0, 24,
              d.box(x1 - x0, 24, inner=d.text(span(r), "#08131F", 20, "BOLD"),
                    align="CENTER"))

for tm, info in GAPS.items():
    gy, yb = LANES[tm][0], LANES[tm][1]
    for gp in info["gaps"]:
        a, b = px(gp["from_min"]), px(gp["to_min"])
        d.pos(a, yb, b - a, BH, d.box(b - a, BH, radius=6,
                                      border="2 SOLID %s" % P["gap"]))
        d.label(a - 24, gy, 124, 24, "%d min 空档" % gp["minutes"], P["slate"], 20)

# 缓冲带 + 完成/截止竖线
d.pos(px(MS), BUF_Y, px(WINDOW) - px(MS), 34,
      d.box(px(WINDOW) - px(MS), 34, color="#3A2E12", radius=8, align="CENTER",
            inner=d.text("剩余缓冲 %d 分钟（占窗口 %.1f%%）" %
                         (BUFFER, 100.0 * BUFFER / WINDOW), P["amber"], 22, "BOLD")))
d.line(px(MS), LT - 8, px(MS), BUF_Y + 34, 3, "#FBBF24")
d.line(px(WINDOW), LT - 8, px(WINDOW), BUF_Y + 34, 3, "#F87171")
d.label(px(MS) - 150, FIN_Y, 300, 26, "完成 %s（%d min）" % (clock(MS), MS),
        P["amber"], 22, align="CENTER")
d.label(px(WINDOW) - 270, FIN_Y, 260, 26, "截止 16:00", P["red"], 22, align="END")

lg = [("设计团队任务块", DESIGN), ("工程团队任务块", ENGIN),
      ("空档（等待依赖）", "#24395C"), ("柔性任务＝琥珀点", "#FBBF24"),
      ("风险任务＝红点", "#F87171")]
lx = 40
for k, (txt, col) in enumerate(lg):
    d.rect(lx, LEG_Y, 22, 22, col, radius=4)
    d.label(lx + 30, LEG_Y - 2, 260, 26, txt, P["t1"], 20)
    lx += 30 + tf.w(txt, 20) + 46

# 底部三栏说明
NOTES = [
    ("资源空档（与时间同尺度）", [
        "design 10:25–10:30 空 5 分钟：等 engineering 的 R05 才能开 R07。",
        "engineering 12:20–12:25 空 5 分钟：等 design 的 R09 才能开 R11。",
        "engineering 12:55–13:20 空 25 分钟：R12 要等 R10；三处空档合计 35 分钟。"]),
    ("柔性任务的取舍", [
        "R05 文案审校 → engineering，让 design 的关键路径不排队。",
        "R09 手机适配、R12 交付归档 → design。",
        "teams 列两项＝任选其一执行，不占两个团队；切换不计时、不缩时、不删检查环节。"]),
    ("下界与结论口径", [
        "忽略资源的关键路径 255 分钟：R01→R04→R07→R09→R10→R12。",
        "总工时 485 ÷ 2 = 243，资源无关下界取 255；穷举 8 种分配 × 112 组顺序对得 260。",
        "多出的 5 分钟来自 R05 必然推后 R07 或 R08；只称可复核的穷举最优，不夸大。"]),
]
NY, NH = 762, 286
nw = (1856 - 2 * 20) / 3
for k, (title, lines) in enumerate(NOTES):
    bx = 32 + k * (nw + 20)
    d.pos(bx, NY, nw, NH, d.card(nw, NH, color=P["card"], radius=12))
    d.label(bx + 18, NY + 14, nw - 36, 28, title, P["cyan"], 22, "BOLD")
    yy = NY + 48
    for ln in lines:
        nl, hh = para(d, bx + 18, yy, nw - 36, ln, P["t1"], 20)
        tf.check("note%d" % k, ln, 20, nw - 36, hh, lines=nl)
        yy += hh + 6
B1_NOTES_END = yy
BOARD1 = d.dsl()
