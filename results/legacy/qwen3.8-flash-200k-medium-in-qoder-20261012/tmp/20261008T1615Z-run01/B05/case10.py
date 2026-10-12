"""件-10 年度覆盖率与数据质量（1920×1080，决策会议投屏，年度态）。

内容任务：给决策者的不是一棵树的账，而是**这套数据能不能用**的账：缺什么、
谁没报、哪些数字能拿去排序、哪些只能参考、哪些不能对外发布。
这一件刻意回头审其他九件：全市冠幅面积用的是 0.72·D² 经验系数，而件-08 的
居民卡用 π(D/2)² 正投影，同一株树会得到两个数；认养承诺写"90 天内一次巡检"，
而全市 90 天覆盖率只有 24.9 %。这些矛盾不藏起来，就写在本件正文里。
1920×1080 是投屏硬约束（投影仪原生分辨率），不能像件-08 那样加长画布，
所以三块内容的高度全部由行高反推，页脚与卡片底边各留一条 assert。
"""
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1920, 1080
MX = 64
CW = W - 2 * MX
GAP = 12
LW = 1120
RW = CW - LW - GAP
AGE = [("<=", "90 天内", "<=90 天", B.LEAF), ("r2", "91-180 天", "91-180", B.TEAL),
       ("r3", "181-365 天", "181-365", B.AMBER), ("r4", "超过一年", ">365 天", B.RUST)]
PER_DAY = 40                    # 产品自定：巡检员人均 40 株/人·日
TARGET90 = 60.0                 # 产品自定年度目标


def build():
    st = B.data()
    ps, inc, ad = st["per_street"], st["incidents"], st["adoption"]
    od, tot = st["orders"], st["total"]
    hrs = {r["street"]: r["hrs_since"] for r in inc}
    ok = [r for r in ad if r["households"] >= 0]
    bad = [r for r in ad if r["households"] < 0][0]
    fallen = sum(r["fallen"] for r in inc)
    pending = sum(r["fallen"] - r["fallen_confirmed"] for r in inc)
    # 冠幅面积：数据集口径 0.72·D² vs 件-08 居民卡口径 π(D/2)²
    alt = sum(t["crown_m"] ** 2 * math.pi / 4 for t in B.trees()["trees"])
    f = st["featured"]["tree"]
    d2 = f["crown_m"] ** 2
    a_proj, a_emp = d2 * math.pi / 4, d2 * 0.72
    diff_pct = 100.0 * (a_proj - a_emp) / a_emp
    over365 = st["inspect_age"][">365 天"]

    d, tf = B.doc(W, H, ground="light")
    # ---- 报头 ----
    B.tlab(d, tf, "h-t", MX, 26, 900, 44, "行道树数据年度体检 · 2026", 32, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "h-s", MX, 72, 1250, 24,
           "园林绿化中心 · 数据组 ｜ 统计截至 %s ｜ 在册 %s 株 / %d 条路段 / %d 个街道"
           % (st["generated_at"][:16].replace("T", " "), B.fmt(tot), st["roads"],
              st["streets"]), 15, d.P["t2"])
    B.chip(d, tf, "h-c", W - MX - 440, 30, 440, 44,
           "结论：可用于内部排序，暂不可对外发布", "#FFFFFF", B.AMBER, size=16)
    B.tlab(d, tf, "h-r", W - MX - 440, 82, 440, 22,
           "本件同时复核前面九件产出的口径", 13, d.P["t2"], align="END")

    # ---- ① 四个可信度指标 ----
    y1, h1 = 116, 152
    kpi = [("90 天巡检覆盖率", "%.1f %%" % st["coverage_90d"],
            "目标 %.0f %%，还差 %.1f 个百分点" % (TARGET90, TARGET90 - st["coverage_90d"]),
            B.RUST),
           ("超过一年未巡检", "%s 株" % B.fmt(over365),
            "占在册 %.1f %%，风险分沿用去年值" % (100.0 * over365 / tot), B.RUST),
           ("待修字段异常", "4 项",
            "户数负值／压线零报／风速零值／上报未去重", B.AMBER),
           ("超时工单", "%d 张" % od["overdue"],
            "占 %s 张的 %.1f %%，含立即处置 %d 张"
            % (B.fmt(od["total"]), 100.0 * od["overdue"] / od["total"],
               od["overdue_urgent"]), B.AMBER)]
    seg = (CW - 3 * GAP) / 4.0
    for i, (k, v, sub, col) in enumerate(kpi):
        x = MX + i * (seg + GAP)
        px, py, pw = B.card(d, tf, "k%d" % i, x, y1, seg, h1)
        B.tlab(d, tf, "k-t%d" % i, px, py, pw, 22, k, 15, d.P["t2"])
        B.num(d, tf, "k-v%d" % i, px, py + 24, pw, 40, v, 36, col, align="START")
        B.tlab(d, tf, "k-s%d" % i, px, py + 68, pw, 42, sub, 13, d.P["t1"], lines=2,
               valign="TOP")

    # ---- ② 左：巡检时效账 ----
    y2, h2 = y1 + h1 + GAP, 400
    px, py, pw = B.card(d, tf, "a", MX, y2, LW, h2, "② 巡检时效：覆盖率的真实形状",
                        "四段互斥，求和等于在册 %s 株" % B.fmt(tot))
    x = px
    for tag, lab, key, col in AGE:
        n = st["inspect_age"][key]
        w = pw * n / tot
        d.rect(x, py, w, 40, col)
        if w > 150:
            B.mono(d, tf, "a-v" + tag, x + 12, py + 8, w - 24, 24,
                   "%s 株 / %.1f %%" % (B.fmt(n), 100.0 * n / tot), 15, "#FFFFFF")
        x += w
    ly = py + 52
    for i, (tag, lab, key, col) in enumerate(AGE):
        n = st["inspect_age"][key]
        B.disc(d, px + 8, ly + i * 28 + 12, 8, col)
        B.tlab(d, tf, "a-l%d" % i, px + 26, ly + i * 28, 150, 24, lab, 15, d.P["t1"])
        B.mono(d, tf, "a-c%d" % i, px + 180, ly + i * 28, 130, 24, "%s 株" % B.fmt(n),
               15, d.P["t2"])
        B.mono(d, tf, "a-p%d" % i, px + 300, ly + i * 28, 90, 24,
               "%.1f %%" % (100.0 * n / tot), 15, d.P["t2"], align="END")
    ny = ly + 4 * 28 + 10
    nb = B.note_band(d, tf, "a-n", px, ny, pw, [
        "认养承诺写「每 90 天内一次专业巡检」（件-08），但全市只有 %.1f %% 达标。"
        % st["coverage_90d"],
        "数据没把认养标记落到单株，因此算不出「认养树达标率」——这是字段缺失，不是巧合。",
        "365 天口径覆盖 %.1f %%（%s 株），即每 5 株约 1 株一年内没有任何实测更新。"
        % (st["coverage_365d"], B.fmt(tot - over365))], size=15)

    # ---- ③ 右：可信度分级 ----
    px, py, pw = B.card(d, tf, "b", MX + LW + GAP, y2, RW, h2, "③ 这些数字能不能用",
                        "绿＝可据以排序／橙＝引用须带口径／红＝暂不可对外")
    grades = [(B.LEAF, "风险分与四级分级",
               "%s 株全覆盖，字段完整、可复算" % B.fmt(tot)),
              (B.LEAF, "工单状态与超时",
               "6 个状态互斥，%s 张与班组合计一致" % B.fmt(od["total"])),
              (B.AMBER, "灾情上报 %d 起" % fallen,
               "未去重，其中 %d 起待核实（件-09）" % pending),
              (B.AMBER, "全市冠幅投影 %s m²" % B.fmt(st["crown_area_m2"]),
               "用经验系数 0.72·D²，与件-08 口径不一致"),
              (B.RUST, "分街道认养户数",
               "%s %d 户，现实中不可能" % (bad["street"], bad["households"])),
              (B.RUST, "认养树巡检达标率", "认养未落到单株，无法计算")]
    gy = py
    for i, (col, k, why) in enumerate(grades):
        d.rect(px, gy + 2, 6, 22, col)
        B.tlab(d, tf, "b-k%d" % i, px + 18, gy, pw - 18, 24, k, 15, d.P["t0"],
               style="BOLD")
        B.tlab(d, tf, "b-w%d" % i, px + 18, gy + 24, pw - 18, 22, why, 13, d.P["t2"])
        gy += 48

    # ---- ④ 左：谁没报；⑤ 右：补数计划 ----
    y3, h3 = y2 + h2 + GAP, 320
    px, py, pw = B.card(d, tf, "c", MX, y3, LW, h3, "④ 谁没报：六个街道的活跃度与异常",
                        "认养率＝已认养 ÷ 在册；末次上报为灾情快报口径（件-09）")
    issue = {"岩前街道": (B.RUST, "认养户数 %d 户，退回核对中" % bad["households"]),
             "梧桐街道": (B.AMBER, "有 %d 株认养树，全年 0 次认养活动记录"
                      % [r for r in ad if r["street"] == "梧桐街道"][0]["adopted"]),
             "云屿街道": (B.AMBER, "阻路 15 起却零压线，疑未单独登记"),
             "南门街道": (B.RUST, "在册最多（%s 株）仅报 4 起倒伏，6 h 静默"
                      % B.fmt(ps["NM"]["total"])),
             "白鹭街道": (B.AMBER, "认养率最高，但已 6 h 无上报"),
             "临江街道": (d.P["t0"], "字段完整，可作为口径基准")}
    rows = []
    for r in sorted(ad, key=lambda r: -r["adopted"] / r["trees"]):
        col, txt = issue[r["street"]]
        rows.append([r["street"], B.fmt(r["trees"]), "%d" % r["adopted"],
                     "%.1f %%" % (100.0 * r["adopted"] / r["trees"]),
                     "%d 次" % r["events"],
                     ("%d h" % hrs[r["street"]],
                      B.AMBER if hrs[r["street"]] >= 6 else d.P["t0"]),
                     (txt, col)])
    ct = B.coltable(d, tf, "c", px, py, pw,
                    [("街道", 150, "START"), ("在册", 90, "END"), ("认养", 80, "END"),
                     ("认养率", 90, "END"), ("活动", 80, "END"), ("末次上报", 100, "END"),
                     ("数据问题", 400, "START")],
                    rows, row_h=28, head_h=30, size=15, head_size=14)

    px, py, pw = B.card(d, tf, "e", MX + LW + GAP, y3, RW, h3, "⑤ 补数据的三笔账",
                        "按缺口排序，成本按人均 %d 株/人·日估算" % PER_DAY)
    plans = [("补 %s 株超一年未巡检的实测" % B.fmt(over365),
              "%.1f 人·日" % (over365 / float(PER_DAY)), "3 个班组 × 2 周"),
             ("把认养标记落到单株并回填", "3.0 人·日", "数据组，1 周"),
             ("灾情上报去重 + 云屿压线补录", "1.5 人·日", "值班室，3 天")]
    ey = py
    for i, (k, cost, who) in enumerate(plans):
        B.mono(d, tf, "e-i%d" % i, px, ey, 24, 24, "%d" % (i + 1), 15, B.LEAF)
        B.tlab(d, tf, "e-k%d" % i, px + 28, ey, pw - 178, 24, k, 15, d.P["t0"])
        B.tlab(d, tf, "e-c%d" % i, px + pw - 148, ey, 148, 24, cost, 15, B.AMBER,
               align="END")
        B.tlab(d, tf, "e-w%d" % i, px + 28, ey + 24, pw - 28, 22, who, 13, d.P["t2"])
        ey += 48
    B.tlab(d, tf, "e-n1", px, ey + 2, pw, 22,
           "同一株 %s 在两处得到两个面积：正投影 π(D/2)² = %.1f m²，"
           % (f["id"], a_proj), 13, d.P["t1"])
    en = ey + 46
    B.tlab(d, tf, "e-n2", px, ey + 24, pw, 22,
                "汇总口径 0.72·D² = %.1f m²；两式差 %.1f %%，全市合计 %s 与 %s m²。"
                % (a_emp, diff_pct, B.fmt(st["crown_area_m2"]), B.fmt(round(alt, 0))),
                13, d.P["t1"])

    ce = B.credit(d, tf, "foot", MX, y3 + h3 + 10, CW, [
        "演示数据：汀州市、6 个街道、3,725 株树、23 条路段与全部灾情／工单／认养计数由 "
        "b05data.py（固定种子 %d）生成，不对应任何真实市政系统。" % st["seed"],
        "「90 天覆盖率目标 %.0f %%」「人均 %d 株/人·日」「三笔补数成本」与可信度三色分级"
        "均为产品自定口径，不是行业标准；本件未做真实用户验证。" % (TARGET90, PER_DAY)],
        size=13)
    assert ce <= H - 6, ("页脚超出画布", ce, H)
    assert nb <= y2 + h2 - 22, ("② 左说明框溢出卡片", nb, y2 + h2 - 22)
    assert gy <= y2 + h2 - 22, ("③ 分级行溢出卡片", gy, y2 + h2 - 22)
    assert ct <= y3 + h3 - 22, ("④ 表格溢出卡片", ct, y3 + h3 - 22)
    assert en <= y3 + h3 - 22, ("⑤ 说明溢出卡片", en, y3 + h3 - 22)
    return d, tf, dict(case="case-10", kind="年度覆盖率与数据质量（决策投屏）",
                       cov90=st["coverage_90d"], cov365=st["coverage_365d"],
                       over365=over365, canopy=st["crown_area_m2"],
                       alt_canopy=round(alt, 0), diff_pct=round(diff_pct, 1),
                       anomaly=bad["households"], overdue=od["overdue"])
