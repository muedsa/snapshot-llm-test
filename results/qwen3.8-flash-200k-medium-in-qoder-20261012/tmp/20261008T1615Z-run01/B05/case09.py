"""件-09 雨后灾情快报（1440×2000，上报通报，灾后 6 h）。

内容任务：把"报上来多少"和"核实了多少"分开说清楚，并指出三个不能直接下结论的地方。
灾后快报最常见的造假是把上报数当灾情总数、把四个独立计数字段相加、把漏报当平安。
本件因此只报「已核实／待核实」两个口径，并把每千株上报数（按在册株数归一）与
末次上报距今放在一起，让"某街道很平静"这种判断必须经过归一化检查。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1440, 2000
MX = 56
CW = W - 2 * MX
GAP = 12


def build():
    st = B.data()
    inc = st["incidents"]
    ps = st["per_street"]
    od = st["orders"]
    code = {r["street"]: r["street_code"] for r in inc}
    for r in inc:
        r["pending"] = r["fallen"] - r["fallen_confirmed"]
        r["rate"] = 100.0 * r["fallen_confirmed"] / r["fallen"]
        r["per_k"] = 1000.0 * r["fallen"] / ps[r["street_code"]]["total"]
    T = {k: sum(r[k] for r in inc) for k in ("fallen", "fallen_confirmed", "pending",
                                             "branch", "wire", "blocked")}
    T["rate"] = 100.0 * T["fallen_confirmed"] / T["fallen"]
    T["per_k"] = 1000.0 * T["fallen"] / st["total"]
    rows = sorted(inc, key=lambda r: (r["rate"], r["per_k"]))
    worst = min(rows, key=lambda r: r["rate"])
    stale = [r for r in rows if r["hrs_since"] >= 6]
    yy = [r for r in rows if r["street_code"] == "YY"][0]
    dense = max(rows, key=lambda r: r["per_k"])

    d, tf = B.doc(W, H, ground="light")
    # ---- 报头 ----
    B.tlab(d, tf, "h-t", MX, 44, 700, 54, "行道树灾后情况快报", 38, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "h-s", MX, 106, 1000, 26,
           "汀州市园林绿化中心 · 应急值班室 ｜ 报送：市城运中心、各区园林绿化科", 16,
           d.P["t2"])
    B.tlab(d, tf, "h-p", MX, 136, 1000, 26,
           "过程：10 月 10 日 22:00 起强降雨，11 日 05:00 雨势减弱；全市 6 个街道 %s 株"
           "行道树在册" % B.fmt(st["total"]), 16, d.P["t2"])
    B.chip(d, tf, "h-c", W - MX - 250, 46, 250, 46, "第 3 期 · 灾后 6 h", "#FFFFFF",
           B.RUST, size=16)
    B.mono(d, tf, "h-cut", W - MX - 250, 102, 250, 24, "截止 2026-10-11 11:00", 14,
           d.P["t1"], align="CENTER")

    # ---- ① 摘要 + 六个计数 ----
    y1, h1 = 172, 260
    px, py, pw = B.card(d, tf, "a", MX, y1, CW, h1, "① 本期摘要（只报两个口径）",
                        "上报数是事件线索，核实数才是可上报的灾情")
    B.tlab(d, tf, "a-l1", px, py, pw, 28,
           "共上报倒伏 %d 起：现场已核实 %d 起、待核实 %d 起；另有断枝 %d 起、"
           "压线（涉电）%d 起、阻路 %d 起。" % (T["fallen"], T["fallen_confirmed"],
                                          T["pending"], T["branch"], T["wire"],
                                          T["blocked"]), 17, d.P["t1"])
    B.tlab(d, tf, "a-l2", px, py + 30, pw, 28,
           "倒伏、断枝、压线、阻路是四个独立计数字段，同一株树可同时计入两类，"
           "四数相加不等于受灾总数；待核实 30 起未做去重。", 17, d.P["t1"])
    stats = [("%d" % T["fallen"], "倒伏上报（起）", d.P["t0"]),
             ("%d" % T["fallen_confirmed"], "现场已核实（起）", B.LEAF),
             ("%d" % T["pending"], "待核实（起）", B.AMBER),
             ("%d" % T["branch"], "断枝（起）", d.P["t0"]),
             ("%d" % T["wire"], "压线涉电（起）", B.RUST),
             ("%d" % T["blocked"], "阻路（起）", B.RUST)]
    seg = pw / 6.0
    for i, (v, k, col) in enumerate(stats):
        x = px + i * seg
        if i:
            d.line(x - 12, py + 78, x - 12, py + 168, 1, d.P["border"])
        B.num(d, tf, "a-n%d" % i, x, py + 76, seg - 24, 44, v, 38, col, align="START")
        B.tlab(d, tf, "a-k%d" % i, x, py + 126, seg - 24, 26, k, 15, d.P["t2"])

    # ---- ② 分街道核实进度 ----
    y2, h2 = y1 + h1 + GAP, 504
    px, py, pw = B.card(d, tf, "b", MX, y2, CW, h2, "② 分街道核实进度（按核实率升序）",
                        "每千株上报＝倒伏上报 ÷ 该街道在册株数 × 1000，用来排除"
                        "「街道大小不同」的干扰")
    cols = [("街道", 170, "START"), ("在册株数", 110, "END"), ("倒伏上报", 110, "END"),
            ("已核实", 100, "END"), ("待核实", 100, "END"), ("核实率", 110, "END"),
            ("每千株上报", 130, "END"), ("断枝", 80, "END"), ("压线", 80, "END"),
            ("阻路", 80, "END"), ("末次上报", 120, "END")]
    trs = []
    for r in rows:
        c = r["rate"] < 60
        trs.append([r["street"], B.fmt(ps[code[r["street"]]]["total"]), r["fallen"],
                    r["fallen_confirmed"], (r["pending"], B.AMBER),
                    ("%.1f %%" % r["rate"], B.RUST if c else d.P["t0"]),
                    "%.1f" % r["per_k"], r["branch"],
                    (r["wire"], B.RUST if r["wire"] == 0 else d.P["t0"]), r["blocked"],
                    ("%d h" % r["hrs_since"], B.AMBER if r["hrs_since"] >= 6
                     else d.P["t0"])])
    trs.append(["全市合计", B.fmt(st["total"]), T["fallen"], T["fallen_confirmed"],
                T["pending"], "%.1f %%" % T["rate"], "%.1f" % T["per_k"], T["branch"],
                T["wire"], T["blocked"], "—"])
    ty = B.coltable(d, tf, "b", px, py, pw, cols, trs, row_h=40, head_h=36, size=16,
                    head_size=14)
    d.line(px, ty - 42, px + pw, ty - 42, 2, d.P["t1"])
    ny = ty + 18
    B.tlab(d, tf, "b-n1", px, ny, pw, 28,
           "核实率最低的是%s（%.1f %%），全市均值 %.1f %%；末次上报距今 6 h 的有 %s"
           "共 %d 个——不是「没有灾情」，是「还没报上来或没核」。"
           % (worst["street"], worst["rate"], T["rate"],
              "、".join(r["street"] for r in stale), len(stale)), 16, d.P["t1"])
    B.tlab(d, tf, "b-n2", px, ny + 30, pw, 28,
           "按每千株上报看，压力最大的是%s（%.1f 起/千株，在册仅 %d 株），"
           "与上报绝对数排序不一致。" % (dense["street"], dense["per_k"],
                                    ps[code[dense["street"]]]["total"]), 16, d.P["t1"])

    # ---- ③ 三处需要核对 ----
    y3, h3 = y2 + h2 + GAP, 420
    px, py, pw = B.card(d, tf, "c", MX, y3, CW, h3, "③ 三处不能直接下结论的地方",
                        "本快报把疑点写在正文里，而不是等上级问起再补")
    items = [
        (B.RUST, "%s疑似漏报" % worst["street"],
         ["在册 %s 株为全市最多（占 %.1f %%），倒伏上报只有 %d 起、每千株 %.1f 起，"
          "是全市均值的 1/%.1f；同时该街道已 %d 小时无新增上报。"
          % (B.fmt(ps[worst["street_code"]]["total"]),
             100.0 * ps[worst["street_code"]]["total"] / st["total"],
             worst["fallen"], worst["per_k"], T["per_k"] / worst["per_k"],
             worst["hrs_since"]),
          "处理：本期已发出催报，回查原始报修记录后在第 4 期给出结论；"
          "在结论前，不采用「全市灾情较轻」的表述。"]),
        (B.AMBER, "%s口径缺失" % yy["street"],
         ["阻路 %d 起为全市最高，压线登记却是 0 起；同一路段的断枝与压线通常伴生，"
          "判断为压线未单独登记（该街道报修表单没有这一栏）。" % yy["blocked"],
          "处理：要求补录后再核；全市压线 %d 起因此是下限，不是终数。"
          % T["wire"]]),
        (B.TEAL, "待核实 %d 起未去重" % T["pending"],
         ["待核实＝上报－已核实，其中可能包含同一株树被市民与班组重复上报。",
          "处理：核销前任何「全市倒伏 X 株」的说法都不成立；本快报只引用「已核实 %d "
          "起」作为可上报数字。" % T["fallen_confirmed"]])]
    iy = py
    for c, (col, title, lines) in enumerate(items):
        d.rect(px, iy + 2, 6, 30, col)
        B.tlab(d, tf, "c-t%d" % c, px + 20, iy, pw - 20, 30, title, 19, col,
               style="BOLD")
        for i, ln in enumerate(lines):
            B.tlab(d, tf, "c-%d-%d" % (c, i), px + 20, iy + 34 + i * 28, pw - 20, 26,
                   ln, 16, d.P["t1"])
        iy += 34 + len(lines) * 28 + 18

    # ---- ④ 处置力量与超时 ----
    y4, h4 = y3 + h3 + GAP, 326
    px, py, pw = B.card(d, tf, "e", MX, y4, CW, h4, "④ 处置力量与超时工单",
                        "工单口径与灾情口径不同，两数不可相减")
    B.tlab(d, tf, "e-o", px, py, pw, 28,
           "超时工单 %d 张（占全部 %s 张的 %.1f %%），其中「立即处置」类 %d 张"
           "尚未复查——这一项与本次降雨无关，是过程前就欠的账。"
           % (od["overdue"], B.fmt(od["total"]), 100.0 * od["overdue"] / od["total"],
              od["overdue_urgent"]), 17, B.RUST)
    by = py + 40
    crews = sorted(od["crew"].items(), key=lambda kv: -kv[1])
    cols4 = [B.LEAF, B.TEAL, B.AMBER, "#B98A16"]
    x = px
    for i, (name, n) in enumerate(crews):
        w = pw * n / od["total"]
        d.rect(x, by, w, 26, cols4[i])
        B.mono(d, tf, "e-v%d" % i, x + 8, by + 2, max(60, w - 16), 22, "%d" % n, 14,
               "#FFFFFF")
        x += w
    x = px
    for i, (name, n) in enumerate(crews):
        w = pw * n / od["total"]
        B.disc(d, x + 7, by + 44, 7, cols4[i])
        B.tlab(d, tf, "e-k%d" % i, x + 20, by + 32, max(150, w - 24), 26,
               "%s %d 张（%.1f %%）" % (name, n, 100.0 * n / od["total"]), 15,
               d.P["t2"])
        x += w
    nb = B.note_band(d, tf, "e-n", px, by + 70, pw, [
        "工单 %s 张按状态分布：待复核 %d ／ 已复核 %d ／ 已派单 %d ／ 作业中 %d ／ "
        "待复查 %d ／ 已归档 %d；四个班组合计承接 %s 张。"
        % (B.fmt(od["total"]), od["states"]["待复核"], od["states"]["已复核"],
           od["states"]["已派单"], od["states"]["作业中"], od["states"]["待复查"],
           od["states"]["已归档"], B.fmt(sum(od["crew"].values()))),
        "倒伏 %d 起与工单 %s 张不是同一口径：工单含断枝、压线、阻路与日常巡检开单，"
        "本快报不因倒伏数小于工单数而推断「处置及时」。" % (T["fallen"],
                                                    B.fmt(od["total"]))], size=15)

    # ---- ⑤ 下一步与时限 ----
    y5, h5 = y4 + h4 + GAP, 180
    px, py, pw = B.card(d, tf, "f", MX, y5, CW, h5, "⑤ 下一步与时限",
                        "时限由值班室自定，不是应急预案条文")
    nxt = [("12:00 前", "待核实 %d 起逐条电话或到场核销，核销率随第 4 期更新。"
            % T["pending"]),
           ("14:00 前", "%s催报回查、%s压线补录，两项结论由数据组给出。"
            % (worst["street"][:2], yy["street"][:2])),
           ("18:00", "第 4 期快报：压线供电回执、阻路清障进度。"
            )]
    seg = pw / 3.0
    for i, (t_, s) in enumerate(nxt):
        x = px + i * seg
        if i:
            d.line(x - 16, py, x - 16, py + 62, 1, d.P["border"])
        B.mono(d, tf, "f-t%d" % i, x, py, seg - 24, 24, t_, 16, B.RUST)
        B.tlab(d, tf, "f-s%d" % i, x, py + 28, seg - 24, 44, s, 15, d.P["t1"],
               lines=2, valign="TOP")

    ce = B.credit(d, tf, "foot", MX, y5 + h5 + GAP, CW, [
        "演示通报：汀州市、6 个街道名、全部灾情计数与工单数由 b05data.py"
        "（固定种子 %d）生成，不对应任何真实灾情或真实报送。" % st["seed"],
        "本页不引用风力等级：数据集中唯一的风速记录是件-07 的月检读数（17 节），"
        "它是巡检时点的抽样值、不是过程极大值，不足以支撑「台风级大风」的表述。",
        "本快报未做真实用户验证；报送对象、催报与核销时限为产品自定流程，"
        "不是应急预案条文，也不构成对任何单位的实际报送。"], size=13)
    # TextFit 只看单个文本盒，看不到纵向越界，这里补两条硬检查
    assert nb <= y4 + h4 - 22, ("④ 说明框溢出卡片", nb, y4 + h4 - 22)
    assert ce <= H - 8, ("页脚超出画布", ce, H)
    return d, tf, dict(case="case-09", kind="雨后灾情快报（上报通报）",
                       fallen=T["fallen"], confirmed=T["fallen_confirmed"],
                       pending=T["pending"], branch=T["branch"], wire=T["wire"],
                       blocked=T["blocked"], rate_pct=round(T["rate"], 1),
                       per_k=round(T["per_k"], 1), worst=worst["street"],
                       overdue=od["overdue"])
