"""A24 三图生成：1920x1080 执行泳道 / 1200x1600 决策简报 / 720x1280 手机行动卡。

全部事实来自 solve.py 的 schedule.json + schedule-audit.json + inputs/release.json，
三图共用同一份数据构造，避免互相矛盾。文字宽度先用 TextFit 预估再发 DSL，
因为 Snapshot 对超框文字是静默裁切、没有省略号。
"""
import json
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
from dslkit import Doc, TextFit, GRAD_NIGHT, n  # noqa: E402

TMP = root / "tmp" / rid / "A24"
SCH = json.loads((TMP / "schedule.json").read_text(encoding="utf-8"))
AUD = json.loads((TMP / "schedule-audit.json").read_text(encoding="utf-8"))
ROWS = {r["id"]: r for r in SCH["schedule"]}
ORDER = [r["id"] for r in sorted(SCH["schedule"], key=lambda r: (r["start_min"], r["id"]))]
MS = SCH["makespan_minutes"]
WINDOW = SCH["window_minutes"]
BUFFER = SCH["buffer_minutes"]
LOAD = SCH["team_load_minutes"]
GAPS = AUD["checks"]["idle_windows"]
SEARCH = AUD["search"]
BOUNDS = AUD["bounds"]
RISKS = json.loads((root / "tasks" / "A24-release-plan-capstone" / "inputs" /
                    "release.json").read_text(encoding="utf-8"))["risks"]
RISK_BY_TASK = {r["task"]: r for r in RISKS}

BRAND = "叠光 · 发布演练"
DESIGN, ENGIN = "#38BDF8", "#34D399"
TEAM_COLOR = {"design": DESIGN, "engineering": ENGIN}
TEAM_CN = {"design": "设计", "engineering": "工程"}


def clock(m):
    t = 9 * 60 + m
    return "%02d:%02d" % (t // 60 % 24, t % 60)


def span(r):
    return "%s–%s" % (clock(r["start_min"]), clock(r["end_min"]))


tf = TextFit()


def para(dd, x, y, w, s, color, size):
    """多行段落：Snapshot 的 Text 按容器宽自动换行，但带 height= 时整段不渲染
    （A24 探针 probe/multiline.png 变体 A 空白、变体 B 用 maxLines 正常）。
    所以只发 maxLines，高度按行数预留。返回 (行数, 高度)。"""
    pitch = round(size * 1.45)
    nl = tf.lines(s, size, w)
    h = max(pitch, nl * pitch)
    dd.pos(x, y, w, h, dd.box(w, h, inner=dd.text(s, color, size,
                                                  maxlines=nl + 1),
                              align="TOP_LEFT"))
    return nl, h


# ---------------------------------------------------------------- 执行泳道
W, H = 1920, 1080
d = Doc(W, H)
d.P.update({"card": "#0C1730", "card2": "#0A1428", "border": "#1C2C4A",
            "grid": "#152540", "gap": "#24395C"})
P = d.P
CX, CW = 32, 1856                    # 主卡位置与宽度

def board_shell(d, w, h, title, sub, right_lines, sub_size=22):
    d.pos(0, 0, w, h, d.box(w, h, grad=GRAD_NIGHT))
    d.label(40, 26, 620, 50, BRAND, P["t0"], 40, "BOLD")
    d.label(40, 78, 900, 30, sub, P["cyan"], sub_size, "BOLD")
    for k, (txt, col, size) in enumerate(right_lines):
        d.label(w - 40 - 620, 24 + k * 30, 620, 28, txt, col, size, align="END")


# 顶部标题带
board_shell(d, W, H, None, "发布日执行泳道 · 12 项任务 · 两团队串行不可抢占 · 真实时间同尺度",
            [("开工 09:00 · 截止 16:00 · 窗口 %d 分钟" % WINDOW, P["t1"], 22),
             ("完成 %s · 达成 %d 分钟 · 剩余缓冲 %d 分钟" % (clock(MS), MS, BUFFER),
              P["amber"], 24)])

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
    bx = min(max(x0 - 12, PX0 - 6), PX1 - 232)
    # 说明框不得压过完成竖线（R12 的块尾正好贴着 13:20 线）
    if bx < px(MS) < bx + 232:
        bx = min(px(MS) + 10, PX1 - 232)
    tf.check(i, r["label"], 22, 232, 28)
    tf.check(i + "t", span(r) + " · %dmin" % r["minutes"], 20, 232, 24)
    d.label(bx, cap_y, 232, 28, r["label"], P["t0"], 22, "BOLD")
    d.label(bx, cap_y + 28, 232, 24, span(r) + " · %dmin" % r["minutes"], P["t1"], 20)
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
d.label(px(WINDOW) - 290, FIN_Y, 260, 26, "截止 16:00", P["red"], 22, align="END")

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
# ---------------------------------------------------------------- 决策简报
W2, H2 = 1200, 1600
d2 = Doc(W2, H2)
d2.P.update({"card": "#0C1730", "card2": "#0A1428", "border": "#1C2C4A"})
Q = d2.P
board_shell(d2, W2, H2, None, "发布日决策简报 · 2026-11-07",
            [("达成 %d 分钟 / 下界 %d 分钟" % (MS, BOUNDS["lower_bound_overall"]), Q["t1"], 24),
             ("完成 %s · 截止 16:00" % clock(MS), Q["amber"], 24)], sub_size=24)

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
CY2, CH2 = 276, 410
d2.pos(24, CY2, 1152, CH2, d2.card(1152, CH2, color=Q["card2"], radius=14))
d2.label(44, CY2 + 12, 640, 34, "依赖概览（按编号索引，左→右为先决层次）", Q["t0"], 28, "BOLD")
d2.label(704, CY2 + 16, 452, 30, "青＝design 绿＝engineering", Q["t1"], 24, align="END")
d2.label(44, CY2 + 48, 1112, 30,
         "琥珀粗边＝关键路径 %d 分钟 · 琥珀点＝柔性任务 R05 / R09 / R12（任选一个团队执行）"
         % BOUNDS["critical_path_no_resource_min"], Q["amber"], 24)
NW2, NH2 = 118, 44
colw = 1152.0 / 6
NODE = {}
for L, ids in sorted(BY_LAYER.items()):
    cx = 24 + colw * L + colw / 2
    for s, i in enumerate(ids):
        ny = CY2 + 92 + s * 108
        NODE[i] = (cx, ny)
        d2.pos(cx - NW2 / 2, ny, NW2, NH2,
               d2.box(NW2, NH2, color=TEAM_COLOR[ROWS[i]["team"]], radius=9,
                      align="CENTER", inner=d2.text(i, "#06111F", 24, "BOLD")))
        if len(ROWS[i]["options"]) > 1:
            d2.dot(cx + NW2 / 2 - 2, ny + 2, 14, Q["amber"])
        tf.check("node" + i, ROWS[i]["label"], 24, 186, 30)
        d2.label(cx - 93, ny + NH2 + 2, 186, 30, ROWS[i]["label"], Q["t1"], 24, align="CENTER")
        d2.label(cx - 93, ny + NH2 + 30, 186, 30, span(ROWS[i]), Q["t2"], 24, align="CENTER")
for i, ps in DEPS.items():
    for p in ps:
        hot = (p, i) in CP
        d2.line(NODE[p][0] + NW2 / 2, NODE[p][1] + NH2 / 2,
                NODE[i][0] - NW2 / 2, NODE[i][1] + NH2 / 2,
                4 if hot else 2, Q["amber"] if hot else "#2A3F63")

# 排程依据
RAT = [
    ("规则口径", "两团队各只有一个，同团队串行、不可抢占；teams 列两项＝任选其一执行；"
                 "12 项按 inputs 原时长完整执行，先决未完成不得开始，检查环节未删，"
                 "团队切换不额外计时。"),
    ("求解方法", "枚举 3 个柔性任务的 8 种分配 × 两团队各自与先决相容的内部顺序，共 112 组"
                 "顺序对（48 组跨团队循环等待、无可行排程，跳过），每组取半主动排程：能开工"
                 "就立刻开工。任何可行排程都隐含一组团队顺序，半主动化只会更早，故穷举覆盖"
                 "全局最优。"),
    ("下界差距", "关键路径 %d 分钟（%s），总工时 %d÷2=%d，下界取 %d；达成 %d 多 5 分钟："
                 "R05 的 30 分钟给哪一队都会把 R07 或 R08 推后至少 5 分钟，%d 在本实例不可达。"
                 % (BOUNDS["critical_path_no_resource_min"], BOUNDS["critical_path"],
                    BOUNDS["total_work_min"], BOUNDS["lower_bound_work_div_teams"],
                    BOUNDS["lower_bound_overall"], MS, BOUNDS["lower_bound_overall"])),
]
BW3 = 1160 - 180 - 20
PITCH24 = 35
RAT_NL = [tf.lines(b, 24, BW3) for _, b in RAT]
CY3 = 696
CH3 = 60 + sum(nl * PITCH24 + 14 for nl in RAT_NL) + 4
d2.pos(40, CY3, 1120, CH3, d2.card(1120, CH3, color=Q["card"], radius=14))
d2.label(58, CY3 + 12, 500, 34, "排程依据", Q["t0"], 28, "BOLD")
d2.label(420, CY3 + 18, 720, 30,
         "柔性分配 R05→工程 · R09/R12→设计 · 穷举最优 %d" % MS,
         Q["violet"], 24, align="END")
yy = CY3 + 60
for (t, body), nl in zip(RAT, RAT_NL):
    d2.label(58, yy, 118, 30, t, Q["cyan"], 24, "BOLD")
    nl2, hh = para(d2, 180, yy - 2, BW3, body, Q["t1"], 24)
    tf.check("rat" + t, body, 24, BW3, hh, lines=nl2)
    yy += max(nl * PITCH24, hh) + 14
B2_RAT_END = yy

# 三风险 / 对策
CY4 = CY3 + CH3 + 10
CH4 = 54 + 3 * 100 + 18
d2.pos(40, CY4, 1120, CH4, d2.card(1120, CH4, color=Q["card2"], radius=14))
d2.label(58, CY4 + 12, 900, 34, "三风险与对策（inputs/release.json）", Q["t0"], 28, "BOLD")
ry = CY4 + 54
for r in RISKS:
    tk = r["task"]
    d2.pos(58, ry, 100, 40, d2.box(100, 40, color="#4A1D26", radius=8, align="CENTER",
                                   inner=d2.text(r["id"], Q["red"], 24, "BOLD")))
    ttl = "%s %s · %s" % (tk, ROWS[tk]["label"], r["impact"])
    tf.check("risk" + r["id"], ttl, 24, 900, 30)
    d2.label(170, ry + 2, 900, 30, ttl, Q["t0"], 24, "BOLD")
    mit = "对策：" + r["mitigation"]
    tf.check("mit" + r["id"], mit, 24, 900, 30)
    d2.label(170, ry + 34, 900, 30, mit, Q["t1"], 24)
    d2.label(170, ry + 66, 900, 30, "落在 %s，本排程后仍有 %d 分钟缓冲" %
             (span(ROWS[tk]), BUFFER), Q["green"], 24)
    ry += 100
B2_FOOT = CY4 + CH4 + 10
d2.label(40, B2_FOOT, 1120, 30, "数据来源 inputs/release.json · 明细 schedule.json / "
         "schedule-audit.json", Q["t2"], 24)
BOARD2 = d2.dsl()

# ---------------------------------------------------------------- 手机行动卡
W3, H3 = 720, 1280
d3 = Doc(W3, H3)
d3.P.update({"card": "#0C1730", "card2": "#0A1428", "border": "#1C2C4A"})
R = d3.P
d3.pos(0, 0, W3, H3, d3.box(W3, H3, grad=GRAD_NIGHT))
d3.label(28, 26, 500, 40, BRAND, R["t0"], 34, "BOLD")
d3.label(28, 68, 500, 28, "发布日行动卡 · 按时间序 12 项", R["cyan"], 22, "BOLD")
d3.label(28, 98, 664, 26, "09:00 开工 → %s 完成 · 缓冲 %d 分钟 · 截止 16:00" % (clock(MS), BUFFER),
         R["amber"], 20)
y = 136
LW = 664
for i in ORDER:
    r = ROWS[i]
    rk = RISK_BY_TASK.get(i)
    hh = 98 if rk else 74
    d3.pos(28, y, LW, hh, d3.card(LW, hh, color=R["card"], radius=10,
                                  border="1 SOLID %s" % ("#5A2430" if rk else R["border"])))
    d3.rect(28, y, 6, hh, TEAM_COLOR[r["team"]])
    tf.check("c1" + i, "%s %s" % (i, r["label"]), 24, 400, 28)
    d3.label(48, y + 8, 420, 28, "%s  %s" % (i, r["label"]), R["t0"], 24, "BOLD")
    chip = TEAM_CN[r["team"]] + ("·柔性" if len(r["options"]) > 1 else "")
    cwid = tf.w(chip, 20) + 20
    d3.pos(28 + LW - cwid - 12, y + 10, cwid, 28,
           d3.box(cwid, 28, color="#12263E", radius=14, align="CENTER",
                  inner=d3.text(chip, TEAM_COLOR[r["team"]], 20, "BOLD"),
                  border="1 SOLID %s" % TEAM_COLOR[r["team"]]))
    dep = " · ".join(r["depends"]) if r["depends"] else "无先决"
    line2 = "%s · %d min · 依赖 %s" % (span(r), r["minutes"], dep)
    tf.check("c2" + i, line2, 20, LW - 40, 24)
    d3.label(48, y + 40, LW - 60, 24, line2, R["t1"], 20)
    if rk:
        txt = "%s %s → %s" % (rk["id"], rk["impact"], rk["mitigation"])
        tf.check("c3" + i, txt, 20, LW - 40, 26)
        d3.label(48, y + 66, LW - 60, 26, txt, R["red"], 20)
    y += hh + 6
d3.label(28, y + 2, LW, 26, "柔性任务 R05/R09/R12 只交给一个团队执行；同团队不并行、不抢占。",
         R["t2"], 20)
d3.label(28, y + 28, LW, 26, "关键路径 255 分钟：R01→R04→R07→R09→R10→R12（详见决策简报）",
         R["t2"], 20)
BOARD3 = d3.dsl()
CARD_BOTTOM = y + 54

# ---------------------------------------------------------------- 输出
facts = {
    "brand": BRAND,
    "start": SCH["start"], "deadline": SCH["deadline"], "window_minutes": WINDOW,
    "makespan_minutes": MS, "finish_clock": clock(MS), "buffer_minutes": BUFFER,
    "buffer_pct": round(100.0 * BUFFER / WINDOW, 1),
    "total_work_minutes": BOUNDS["total_work_min"],
    "critical_path_minutes": BOUNDS["critical_path_no_resource_min"],
    "critical_path": BOUNDS["critical_path"],
    "lower_bound_overall": BOUNDS["lower_bound_overall"],
    "lower_bound_work_div_teams": BOUNDS["lower_bound_work_div_teams"],
    "team_load_minutes": LOAD,
    "flexible_assignment": SCH["flexible_assignment"],
    "enumeration": {"team_order_pairs_evaluated": SEARCH["team_order_pairs_evaluated"],
                    "deadlocked_pairs_skipped": SEARCH["team_order_pairs_deadlocked"],
                    "flexible_team_assignments": SEARCH["flexible_team_assignments"]},
    "idle_gaps": GAPS,
    "risks": RISKS,
}
cmap = {
    "path_base": "suite_root",
    "brand": BRAND,
    "data_source": "tasks/A24-release-plan-capstone/inputs/release.json 经 solve.py 全枚举排程",
    "shared_facts": facts,
    "boards": {
        "execution-board": {
            "canvas": "1920x1080", "body_font_min": 20,
            "elements": [
                {"element": "任务块 R01–R12", "source": "schedule.json schedule[].start_min/end_min/team",
                 "value": {i: "%s %s %s" % (i, span(ROWS[i]), ROWS[i]["team"]) for i in ORDER}},
                {"element": "时间轴 09:00–16:00", "source": "release.json start/deadline",
                 "value": "同一尺度 %.4f px/分钟" % SC},
                {"element": "空档空心框", "source": "schedule-audit.json checks.idle_windows",
                 "value": {tm: GAPS[tm]["gaps"] for tm in GAPS}},
                {"element": "缓冲带+截止线", "source": "makespan/window",
                 "value": "剩余 %d 分钟（%.1f%%）" % (BUFFER, 100.0 * BUFFER / WINDOW)},
                {"element": "底部三栏说明", "source": "schedule/audit 文本",
                 "value": [t for t, _ in NOTES]},
            ],
        },
        "decision-brief": {
            "canvas": "1200x1600", "body_font_min": 24,
            "elements": [
                {"element": "四张统计卡", "source": "schedule.json / audit bounds",
                 "value": ["%s=%s" % (lab, big) for lab, big, _, _ in STATS]},
                {"element": "依赖概览层次", "source": "release.json depends",
                 "value": {str(k): v for k, v in BY_LAYER.items()}},
                {"element": "关键路径琥珀边", "source": "audit bounds.critical_path",
                 "value": sorted(CP)},
                {"element": "排程依据四段", "source": "audit search/bounds",
                 "value": [t for t, _ in RAT]},
                {"element": "三风险/对策", "source": "release.json risks",
                 "value": ["%s→%s %s" % (r["id"], r["task"], r["mitigation"]) for r in RISKS]},
            ],
        },
        "action-card": {
            "canvas": "720x1280", "body_font_min": 20,
            "elements": [
                {"element": "12 行任务（时间序）", "source": "schedule.json",
                 "value": ["%s|%s|%s|%s" % (i, ROWS[i]["team"], span(ROWS[i]),
                                            ROWS[i]["minutes"]) for i in ORDER]},
                {"element": "风险提醒行", "source": "release.json risks",
                 "value": {r["task"]: r["id"] + " " + r["impact"] for r in RISKS}},
                {"element": "页脚口径", "source": "audit",
                 "value": ["柔性任务单团队执行", "关键路径 " + BOUNDS["critical_path"]]},
            ],
        },
    },
    "cross_board_consistency": {
        "finish_time": clock(MS), "buffer": BUFFER, "makespan": MS,
        "lower_bound": BOUNDS["lower_bound_overall"],
        "critical_path": BOUNDS["critical_path"],
        "team_load": LOAD, "flexible_assignment": SCH["flexible_assignment"],
        "note": "三图的起止、团队、时长、缓冲与下界均取自同一 schedule.json/schedule-audit.json，"
                "数值与文字口径一致；执行图块宽=分钟×同一比例，简报与行动卡的时间字符串同源。",
    },
    "textfit": {"estimated_text": tf.n, "problems": tf.problems,
                "note": "TextFit 为本地预估闸门（CJK 1.02×字号），实际以渲染后看图为准。"},
    "dsl_facts_from_probes": {
        "multiline": "Text 带 height= 时整段不渲染（probe/multiline.png 变体 A 空白），"
                     "改用 maxLines 由容器宽自动换行；显式 \\n 亦可。",
        "label_height": "标签盒高需 ≥1.15×字号：24px 放进 height=26 的盒子上下沿被切，"
                        "24/28、24/30 正常；本脚本按该比例逐 Positioned 自检。",
        "background_none": 'background="None" 返回 400 PARSE_ERROR（unsupported CSS color）。',
        "doc_label_positional": "Doc.label 第 8 个位置参数是 style，align 必须用关键字，"
                                "否则产生 400 Attr [fontStyle] value is invalid。",
    },
}
out = root / "outputs" / rid / "A24"
out.mkdir(parents=True, exist_ok=True)
for name, body in (("execution-board", BOARD1), ("decision-brief", BOARD2),
                   ("action-card", BOARD3)):
    (TMP / (name + ".snapshot")).write_text(body, encoding="utf-8")
    (out / (name + ".snapshot")).write_text(body, encoding="utf-8")
(TMP / "content-map.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
(out / "content-map.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
print("px/min=%.4f 卡底部 y=%d/%d" % (SC, CARD_BOTTOM, H3))
print("简报纵向：依赖 %d..%d 依据 %d..%d 风险 %d..%d 页脚 %d..%d / %d"
      % (CY2, CY2 + CH2, CY3, CY3 + CH3, CY4, CY4 + CH4, B2_FOOT, B2_FOOT + 30, H2))
print("执行图：主卡 %d..%d 图例 %d 说明 %d..%d / %d" % (CY, CY + CH, LEG_Y, NY, B1_NOTES_END, H))
print("TextFit 检查 %d 条，问题 %d 条" % (tf.n, len(tf.problems)))
for p in tf.problems:
    print("  !", p)
import re  # noqa: E402
import math  # noqa: E402
# A24 实测：24px 文字放进 height=26 的标签盒会被切上下沿，24/28、24/30 正常，
# 22/26 正常。按 1.15×字号 作为最小盒高闸门，逐 Positioned 检查。
pat = re.compile(r'<Positioned[^>]*height="(\d+)"[^>]*>(.*?)</Positioned>', re.S)
for name in ("execution-board", "decision-brief", "action-card"):
    txt = (TMP / (name + ".snapshot")).read_text(encoding="utf-8")
    sizes = [int(x) for x in re.findall(r'fontSize="(\d+)"', txt)]
    tight = []
    for h_attr, body in pat.findall(txt):
        for s in re.findall(r'fontSize="(\d+)"', body):
            need = math.ceil(int(s) * 1.15)
            if int(h_attr) < need:
                tight.append((int(h_attr), int(s), need))
    print(name, len(txt), "bytes DSL · 字号 min/max =", min(sizes), max(sizes),
          "text 节点", len(sizes), "· 盒高不足", len(tight), tight[:6])
