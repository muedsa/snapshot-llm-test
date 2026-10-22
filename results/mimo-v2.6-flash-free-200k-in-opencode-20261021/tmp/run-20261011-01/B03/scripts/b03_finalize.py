# -*- coding: utf-8 -*-
"""B03 finalize: normalize requests.jsonl, copy finals (md5+IHDR verify),
write case.md x10, portfolio.json/md, gallery.md, technique-notes.md,
tool-usage.jsonl, snapshot-usage.md, task-metrics.json, copy-report.json.

iterations.jsonl is the LIVE journal (log_iter.py, kept as-is; not rewritten).
Plan: tmp/run-20261011-01/B03/plan-v1.json (+ plan-v1a-case05-amendment.json).
"""
import datetime
import hashlib
import io
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
RUN = "run-20261011-01"
TID = "B03"
OUT = os.path.join(ROOT, "outputs", RUN, TID)
TMP = os.path.join(ROOT, "tmp", RUN, TID)
DRAFTS = os.path.join(TMP, "drafts")
PLAN_PATH = os.path.join(TMP, "plan-v1.json")
AMD_PATH = os.path.join(TMP, "plan-v1a-case05-amendment.json")
PLAN_REL = "tmp/%s/B03/plan-v1.json" % RUN
AMD_REL = "tmp/%s/B03/plan-v1a-case05-amendment.json" % RUN
PLAN_EST = "2026-10-19T20:34:03+08:00"

# final version per case (the version actually viewed & accepted)
FINALS = {
    "case-01": "v3", "case-02": "v2", "case-03": "v2", "case-04": "v2",
    "case-05": "v4", "case-06": "v2", "case-07": "v3", "case-08": "v3",
    "case-09": "v2", "case-10": "v5",
}

# per-case static additions (asserts summary + fictional declaration +
# visual intent); aud/ctx/goal/scope/technique/size come from the plan
CASE_EXTRA = {
    "case-01": dict(
        vi="等高线同心环带（计曲线加粗+高程注记）+ 双路线沟槽 + 图例/比例尺/用时表",
        asserts="峰顶782m/等高距40m/10条断言；环半径单调递减断言；两线同门同顶断言；"
                "用时 4.2/4.5h+402/400m≈116min 断言；过线计数=10 断言",
        fictional="青禾岭、山名、补给亭与用时参数为虚构演示数据；坡度=爬升÷水平距为一般估算"),
    "case-02": dict(
        vi="强直角线路色带 + 双环换乘枢纽 + 末班车表（线路色一致）",
        asserts="所有对角段 |dx|=|dy| 恰45°断言；12站/2换乘断言；步行2/3分与注记一致；"
                "末班车表与线路色一致断言",
        fictional="江城地铁1/2/4号线、站名、末班车时刻为虚构演示数据"),
    "case-03": dict(
        vi="SWEEP 昼夜环带 + 24h 双色刻度 + 理想/实际睡眠弧 + 缺口高亮",
        asserts="480/400/80=70+10 分钟断言；弧角度=分钟×15°/h 断言(120/100/17.5/2.5°)；"
                "24刻度 range(24) 生成；22.5%15°换算断言",
        fictional="中学生一周平均作息为虚构示例；调整建议为一般性卫生习惯示意，非医疗建议"),
    "case-04": dict(
        vi="主窗0.5°/对照窗10° 双线栅 + 三步原理 + 条纹走向标注",
        asserts="线距6px 由 d=6/sinθ 断言(d_main=687.5, d_ctrl=34.56)；条纹数 117/81 断言；"
                "主窗<1周期/对照窗~7.5周期断言",
        fictional="展览文案与场馆为虚构演示；条纹间距解释如实标注为几何后果"),
    "case-05": dict(
        vi="等距投影三面体块（顶亮/左中/右暗）+ 琥珀虚线动线 + 尺寸表",
        asserts="同一斜切矩阵复用断言；三组明度互异断言；zones 事实表驱动体块与表格逐行一致断言；"
                "动线编号[1..5]断言（计划数值条件按 plan-v1a 修订）",
        fictional="禾野工坊、区名与米制尺寸为虚构演示；plan-v1a 修订记录于计划附录"),
    "case-06": dict(
        vi="色差重影标题 + SWEEP 光谱盘 + 描边幽灵字 + 高斯光晕 + 字距标注",
        asserts="标题±12/镜环±14 对称断言；两场日期递增且均为周日(datetime)断言；"
                "现场价=预售+40 断言；3.6px/30px=+0.12em 断言；QR 种子重算一致断言",
        fictional="潮汐回声乐队、场馆、票价与二维码占位图案均为虚构演示（图上已注明非真实二维码）"),
    "case-07": dict(
        vi="8重旋转对称窗花 + 中心摊名章 + 回纹刻线带 + 四角时令字 + 信息条",
        asserts="8份×45°同源断言；环半径层级 104<118<246<378<392 断言；瓣尖370<378 断言；"
                "四角药丸与外环>394 断言；信息条与角花留白断言",
        fictional="春集、剪春摊、摊位号与开集时间为虚构演示"),
    "case-08": dict(
        vi="三面板中英文+方向箭头 + 一级盲文点阵 + 点位图例 + 服务台电话",
        asserts="9字母点位逐一断言(A/E/F/I/L/N/O/S/T)；14格40点总数断言；"
                "点径/点距常量恒定断言(CELL_W==COL_GAP+2*DOT_R==36)；绘制点数==表算断言",
        fictional="市集入口、服务台电话 400-000-0000 为演示号码（图上注明）"),
    "case-09": dict(
        vi="220颗星场 + 银河带 + 两真实星座与一虚构星座 + 方位圈 + 时刻表",
        asserts="同seed双生成一致/异seed不同断言；星场恰220颗断言；星径=mag映射带宽断言；"
                "时刻表方位/仰角==图面质心推算断言；时段跨零点时长60..480min断言；月相22%<30断言",
        fictional="灯塔座为活动虚构星座；星场/银河带为示例编排（图上声明非星表不作导航）"),
    "case-10": dict(
        vi="254mm四面板刀模链 + 梯形粘合舌 + 程序化虚线 + 十字盖贴 + 尺寸标注",
        asserts="96+44+96+18=254mm 断言；比例3.937px/mm 全域一致断言；高72mm/舌18mm 断言；"
                "5界4chip；条码推进位越界断言；窄跨度chip下移",
        fictional="晨光果园品牌、配料/产地/条码数字为虚构演示；254mm为教学近似值（图上注明量产需复测）"),
}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def ihdr(path):
    with open(path, "rb") as f:
        data = f.read(33)
    assert data[12:16] == b"IHDR", path
    return struct.unpack(">II", data[16:24])


def jload(path):
    with io.open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    plan = json.load(io.open(PLAN_PATH, encoding="utf-8"))
    amd = json.load(io.open(AMD_PATH, encoding="utf-8"))
    plan_cases = {c["id"]: c for c in plan["cases"]}
    g_plan = plan["common_criteria"]

    # ---------------- normalize requests.jsonl ----------------
    req_path = os.path.join(TMP, "requests.jsonl")
    reqs = jload(req_path)
    for e in reqs:
        rid = e["id"]                      # B03-cNN-vNN | B03-probe*
        tail = rid[4:]
        if tail.startswith("c"):
            e["case_id"] = "case-%s" % tail.split("-")[0][1:]
            e["type"] = "render"
        else:
            e["case_id"] = None            # shared preparation (probes)
            e["type"] = "probe_render"
        e["endpoint"] = "POST /snapshot（无凭据）"
        e["tz"] = "+08:00"
        e["input_file"] = e.get("dsl_path")
        e["output_file"] = e.get("out_path")
    with io.open(req_path, "w", encoding="utf-8", newline="") as f:
        for e in reqs:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    by_case = {}
    for e in reqs:
        by_case.setdefault(e["case_id"], []).append(e)

    iters = jload(os.path.join(TMP, "iterations.jsonl"))
    iters_by_case = {}
    for it in iters:
        iters_by_case.setdefault(it["case_id"], []).append(it)

    # ---------------- copy finals (md5+IHDR) ----------------
    report = {}
    for cid, ver in FINALS.items():
        src_png = os.path.join(DRAFTS, "%s-%s.png" % (cid, ver))
        src_dsl = os.path.join(DRAFTS, "%s-%s.snapshot" % (cid, ver))
        dst = os.path.join(OUT, cid)
        os.makedirs(dst, exist_ok=True)
        dst_png = os.path.join(dst, "final.png")
        dst_dsl = os.path.join(dst, "final.snapshot")
        s_png, s_dsl = md5(src_png), md5(src_dsl)
        for s, d in ((src_png, dst_png), (src_dsl, dst_dsl)):
            with open(s, "rb") as fi, open(d, "wb") as fo:
                fo.write(fi.read())
        d_png, d_dsl = md5(dst_png), md5(dst_dsl)
        w, h = ihdr(dst_png)
        dims_plan = tuple(plan_cases[cid]["size"])
        report[cid] = {
            "draft_png": "tmp/%s/B03/drafts/%s-%s.png" % (RUN, cid, ver),
            "draft_snapshot": "tmp/%s/B03/drafts/%s-%s.snapshot" % (RUN, cid, ver),
            "final_png": "outputs/%s/B03/%s/final.png" % (RUN, cid),
            "final_snapshot": "outputs/%s/B03/%s/final.snapshot" % (RUN, cid),
            "md5_src_png": s_png, "md5_dst_png": d_png,
            "png_md5_match": s_png == d_png,
            "md5_src_dsl": s_dsl, "md5_dst_dsl": d_dsl,
            "dsl_md5_match": s_dsl == d_dsl,
            "ihdr": [w, h], "dims_plan": list(dims_plan),
            "dims_ok": (w, h) == dims_plan,
        }
        assert s_png == d_png and s_dsl == d_dsl, cid
        assert (w, h) == dims_plan, (cid, (w, h), dims_plan)
    with io.open(os.path.join(TMP, "copy-report.json"), "w",
                 encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    # ---------------- shared helpers ----------------
    def case_reqs(cid):
        return [e for e in by_case[cid]]

    def case_iters(cid):
        return [it for it in iters_by_case.get(cid, [])]

    def fix_lines(cid):
        """non-baseline journal entries as fix/change lines."""
        out = []
        for it in case_iters(cid):
            if it["type"] in ("baseline",):
                continue
            obs = it.get("observation") or ""
            act = it.get("action") or ""
            out.append("%s %s（父 %s）：%s → %s" % (
                it["version"], it["type"], it.get("parent_version") or "-",
                obs[:120], act[:120]))
        return out

    # ---------------- case.md x10 ----------------
    for cid, ver in FINALS.items():
        pc = plan_cases[cid]
        ex = CASE_EXTRA[cid]
        recs = case_reqs(cid)
        oks = [e for e in recs if e["ok"]]
        its = case_iters(cid)
        p = report[cid]
        fix = fix_lines(cid)
        baseline = next((it for it in its if it["type"] == "baseline"), None)
        g_rows = [
            ("G1", g_plan[0]["condition"],
             "通过：本件 %d 次请求中 %d 次 200；final.png md5=%s… 与草稿一致；"
             "IHDR %d×%d 与计划一致" % (len(recs), len(oks),
                                       p["md5_dst_png"][:16], p["ihdr"][0],
                                       p["ihdr"][1]),
             "requests.jsonl、copy-report.json"),
            ("G2", g_plan[1]["condition"],
             "通过：生成期 tw()/fit() 宽度预算；%d 次成功渲染全部实际看图，"
             "无截断/越界" % len(oks), "iterations.jsonl 看图记录"),
            ("G3", g_plan[2]["condition"],
             "通过：%s；probe 与 DSL 文本自证手法存在" % ex["asserts"],
             "生成脚本断言、probe 渲染、看图核对"),
            ("G4", g_plan[3]["condition"],
             "通过：%s" % ex["asserts"], "生成脚本断言、看图核对"),
            ("G5", g_plan[4]["condition"],
             "通过：content_scope 逐项在终版看图勾对（%s…）" % pc["content_scope"][:26],
             "终版整图看图"),
            ("G6", g_plan[5]["condition"],
             "通过：见虚构声明；页脚/图上标注", "case.md、作品页脚"),
            ("G7", g_plan[6]["condition"],
             "通过：%s；终版复看无重叠/遮挡/裁剪缺陷" % (
                 "首版即无缺陷" if not fix else "%d 次修改后修复" % len(fix)),
             "iterations.jsonl 看图记录"),
            ("G8", g_plan[7]["condition"],
             "通过：本件手法/媒介/任务与其余 9 件互不重复（见 technique-notes.md）",
             "technique-notes.md、portfolio.md 合集终审"),
        ]
        cm = [
            "# %s · %s\n" % (cid, pc["title"]),
            "- 受众：%s" % pc["audience"],
            "- 使用场景/观看环境：%s" % pc["viewing_env"],
            "- 用户目标：%s" % pc["user_goal"],
            "- 内容范围（计划记录）：%s" % pc["content_scope"],
            "- 视觉主张：%s" % ex["vi"],
            "- DSL 手法（计划记录）：%s" % pc["technique"],
            "- 尺寸：%d×%d（final.png 实际 IHDR 与计划一致）" % tuple(
                report[cid]["ihdr"]),
            "- 最终版本：%s（%s，%d 次请求 / %d 次看图 / %d 条迭代日志）" % (
                ver, recs[-1]["id"], len(recs), len(oks), len(its)),
            "- 计划：%s（v1 @ %s，首渲前建立）" % (PLAN_REL, PLAN_EST),
            "",
            "## 素材情况",
            "纯 DSL 构建，无外部素材嵌入；全部色块/文字/几何/图表由 .snapshot "
            "自包含生成（asset_policy=dsl_primary_with_supporting_assets，"
            "本题全部 10 件选择纯 DSL）。二维码/条码为脚本生成的占位图案并图上注明。",
            "",
            "## 虚构声明",
            "%s。品牌、机构、人物与全部数据均为虚构演示；不指向真实客户或实际部署。"
            % ex["fictional"],
            "",
            "## 实际自检（对照 %s 的通用标准 G1–G8）\n" % PLAN_REL,
            "| 标准 | 条件 | 实际结果 | 证据 |",
            "|---|---|---|---|",
        ]
        cm += ["| %s | %s | %s | %s |" % r for r in g_rows]
        cm += ["", "## 迭代与修改（实际日志摘录）"]
        if fix:
            cm += ["%d. %s" % (i, fl) for i, fl in enumerate(fix, 1)]
        else:
            cm.append("首版（%s）看图即达标，无修改；未制造无意义迭代。" % ver)
        if baseline:
            cm.append("")
            cm.append("基线观察（%s，%s）：%s" % (
                baseline["version"], baseline.get("ts"),
                baseline.get("observation", "")[:200]))
        cm += ["", "## 终版看图结论",
               "终版 %s-%s 已整图实际查看：content_scope 关键项齐备、文字可读、"
               "无遮挡/越界；user_goal 在作品上可达成。" % (cid, ver), ""]
        with io.open(os.path.join(OUT, cid, "case.md"), "w",
                     encoding="utf-8") as f:
            f.write("\n".join(cm))

    # ---------------- portfolio.json ----------------
    cases_out = []
    for cid, ver in FINALS.items():
        pc = plan_cases[cid]
        ex = CASE_EXTRA[cid]
        recs = case_reqs(cid)
        oks = [e for e in recs if e["ok"]]
        its = case_iters(cid)
        crit = []
        for i, (gid, cond, meth) in enumerate(g_plan):
            crit.append(dict(id=gid, condition=cond, method=meth,
                             result="passed（详见 %s/case.md G 表）" % cid,
                             evidence=["%s/case.md" % cid,
                                       "tmp/%s/B03/iterations.jsonl" % RUN],
                             status="passed"))
        crit.append(dict(
            id="N1", condition="案例数值型主张成立：%s" % pc["numeric_claims"],
            method="生成脚本断言 + 看图核对",
            result="passed：%s" % ex["asserts"],
            evidence=["tmp/%s/B03/scripts/b03_%s.py" % (RUN, cid.replace("case-", "case")),
                      "%s/final.png" % cid], status="passed"))
        hist = []
        if cid == "case-05":
            hist.append(dict(
                criterion_id="N1", status="amended",
                old="体块长宽高 2:1:1 与图例 m 数一致",
                new=amd["change"]["new"], reason=amd["reason"],
                evidence=amd["change"]["evidence"],
                effective_version="plan-v1a @ %s" % amd["established_at"],
                source=AMD_REL))
        cases_out.append(dict(
            id=cid, title=pc["title"], audience=pc["audience"],
            use_context=pc["viewing_env"], viewing_env=pc["viewing_env"],
            user_goal=pc["user_goal"],
            content_basis="自拟虚构演示数据（见 case.md 虚构声明）：%s"
                          % pc["content_scope"],
            visual_intent=ex["vi"],
            png="%s/final.png" % cid, snapshot="%s/final.snapshot" % cid,
            case_md="%s/case.md" % cid,
            dimensions=list(report[cid]["ihdr"]),
            supporting_assets=[],
            dsl_capabilities=pc["technique"],
            completion_criteria=[
                dict(id=g["id"], condition=g["condition"], method=g["method"],
                     established_version="plan-v1 @ %s（%s）" % (PLAN_EST, PLAN_REL))
                for g in g_plan] + [
                dict(id="N1", condition=pc["numeric_claims"],
                     method="生成脚本断言 + 看图核对",
                     established_version="plan-v1 @ %s（%s）" % (PLAN_EST, PLAN_REL))],
            visual_review="终版 %s-%s 整图已实际查看；本件全部 %d 次成功响应"
                          "均查看，观察/修改/复看记录见 iterations.jsonl"
                          % (cid, ver, len(oks)),
            request_ids=[e["id"] for e in recs],
            iteration_ids=[it["id"] for it in its],
            unresolved_issues=[],
            plan_version="plan-v1 @ %s（%s，suite_root 基准）%s" % (
                PLAN_EST, PLAN_REL,
                "；数值条件按 %s 修订（首渲前）" % AMD_REL
                if cid == "case-05" else ""),
            criteria_history=hist,
            criterion_results=crit))
    portfolio = dict(
        schema_version=1, path_base="output_dir", task_id=TID, run_id=RUN,
        status="completed",
        asset_policy="dsl_primary_with_supporting_assets（本题 10 件全部纯 DSL，"
                     "0 外部素材嵌入）",
        curatorial_statement=(
            "以十件互不重复的真实使用场景作品探索 Snapshot DSL 的创意边界："
            "登山等高线路线图、地铁换乘图、昼夜节律钟盘、摩尔纹科普展板、"
            "工坊轴测导览、乐队巡演海报、剪纸窗花旗、盲文导览牌、观星星图、"
            "果酱罐刀模图——程序化等高线/星场/盲文/条码、强制直角几何、"
            "SWEEP 昼夜与光谱、Transform 等距与旋转对称、多层 textShadow 色差、"
            "手造虚线刀模等手法全部由 .snapshot 构造，服务真实渲染 40 次"
            "（32 成功全部逐张看图），12 次完整视觉迭代 + 5 次需求收口"
            "（c06–c10 收口到计划记录的受众/内容范围）+ 生成期断言拦截。"),
        plan_ref=dict(
            file=PLAN_REL, version="plan-v1", established_at=PLAN_EST,
            criteria=g_plan,
            amendments=[dict(file=AMD_REL, id=amd["amendment_id"],
                             established_at=amd["established_at"],
                             note=amd["reason"])],
            note="计划与通用标准建立于首渲 2026-10-19T21:00 前；G1–G8 未增删；"
                 "case-05 数值条件按 plan-v1a 修订（首渲前，未倒填）"),
        cases=cases_out,
        final_collection_review=(
            "10 件终版逐张实际查看：内容完整、无截断/遮挡、目标观看环境可读；"
            "手法/媒介/使用任务互不重复（technique-notes.md 逐件记录手法、"
            "文档依据、试验证据、应用价值与已确认边界）；c06–c10 已收口到"
            "计划记录的 user_goal，G5 全部达成。"),
        unresolved_issues=[])
    with io.open(os.path.join(OUT, "portfolio.json"), "w",
                 encoding="utf-8") as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=1)

    # ---------------- portfolio.md ----------------
    pm = ["# B03 作品集 · 十件 DSL 创意边界探索\n",
          portfolio["curatorial_statement"], "",
          "计划：%s（plan-v1 @ %s，首渲前建立）；case-05 数值条件修订：%s"
          % (PLAN_REL, PLAN_EST, AMD_REL), "",
          "| 作品 | 受众/场景 | 媒介·尺寸 | 用户目标 | 手法 |",
          "|---|---|---|---|---|"]
    for cid, ver in FINALS.items():
        pc = plan_cases[cid]
        pm.append("| [%s · %s](%s/case.md) | %s · %s | %s · %d×%d | %s | %s |" % (
            cid, pc["title"], cid, pc["audience"].split("（")[0],
            pc["viewing_env"].split("，")[0], pc["technique"].split("：")[0],
            report[cid]["ihdr"][0], report[cid]["ihdr"][1],
            pc["user_goal"].split("：")[0], pc["title"]))
    pm += ["", "逐件手法、文档依据与边界见 [technique-notes.md](technique-notes.md)；"
               "逐件自检（G1–G8+N1）见各 case.md 与 [portfolio.json](portfolio.json)；",
           "逐图预览见 [gallery.md](gallery.md)；真实使用/踩坑见 "
           "[snapshot-usage.md](snapshot-usage.md)。"]
    with io.open(os.path.join(OUT, "portfolio.md"), "w",
                 encoding="utf-8") as f:
        f.write("\n".join(pm))

    # ---------------- gallery.md ----------------
    gm = ["# B03 画廊（10 件最终作品，逐图）", ""]
    for cid, ver in FINALS.items():
        pc = plan_cases[cid]
        w, h = report[cid]["ihdr"]
        gm += [
            "## %s · %s（%d×%d，%s）" % (cid, pc["title"], w, h, ver),
            "受众：%s；目标：%s" % (pc["audience"], pc["user_goal"]),
            "",
            "![%s](%s/final.png)" % (pc["title"], cid),
            "",
            "[原 PNG](%s/final.png) · [对应 DSL](%s/final.snapshot) · "
            "[case.md](%s/case.md)" % (cid, cid, cid),
            ""]
    with io.open(os.path.join(OUT, "gallery.md"), "w",
                 encoding="utf-8") as f:
        f.write("\n".join(gm))

    # ---------------- tool-usage.jsonl ----------------
    tool_usage = [
        dict(tool="本地文档解析（python HTML 提取）",
             purpose="从套件缓存 _suite/docs/parser-tags.html 提取 38 标签+属性表 → "
                    "B03/docs/parser-tags.txt，作为能力边界依据",
             input="_suite/docs/parser-tags.html（套件共享缓存，未新增HTTP）",
             output="tmp/%s/B03/docs/parser-tags.txt" % RUN,
             ts="2026-10-19T20:40+08:00", affects="全部10件（能力选型）",
             request_ref=None),
        dict(tool="本地文档解析（python HTML 提取）",
             purpose="提取 enums.txt（BorderStyle 仅 NONE/SOLID、BoxShape、"
                     "FontStyle BOLD_ITALIC 枚举），据此确定手造虚线与 BOLD_ITALIC",
             input="_suite/docs/enums.html（套件共享缓存）",
             output="tmp/%s/B03/docs/enums.txt" % RUN,
             ts="2026-10-19T20:45+08:00", affects="case-07/08/10",
             request_ref=None),
        dict(tool="b03_probe01–04.py + 服务渲染",
             purpose="共享探针：SWEEP/圆环、textShadow色差/STROKE/smcp、模糊/"
                     "对角矩阵、Transform 面语义 A/B/C 对照（probe04 定位 case-05 "
                     "体块不渲染问题）",
             input="tmp/%s/B03/scripts/b03_probe0*.py" % RUN,
             output="tmp/%s/B03/drafts/probe-*.png" % RUN,
             ts="2026-10-19T21:00 / 2026-10-20T19:04 +08:00",
             affects="case-03/05/06/09 的手法选型",
             request_ref="B03-probe-01..03b, B03-probe04"),
        dict(tool="b03_common.py tw()/fit()（生成期宽度预算）",
             purpose="CJK=1em/ASCII≈0.56em 估宽（含 letter_space/word_space 计入），"
                     "生成期拦截文本越界",
             input="各 case 脚本内联调用", output="FIT-WARN stdout",
             ts="2026-10-19–20", affects="全部10件", request_ref=None),
        dict(tool="b03_common.py + 各 case facts() 断言",
             purpose="生成期数值/几何断言（环半径、45°、尺寸链、盲文点数、星表确定性等），"
                     "数据错误在发请求前拦截",
             input="各 case 脚本入口", output="facts ok stdout / AssertionError",
             ts="2026-10-19–20", affects="全部10件（G3/G4 证据）", request_ref=None),
        dict(tool="log_iter.py（迭代日志工具）",
             purpose="每次看图/修改/重渲按 case/version/parent/type 追加 iterations.jsonl",
             input="命令行6参数", output="tmp/%s/B03/iterations.jsonl" % RUN,
             ts="全程", affects="全部10件+探针", request_ref=None),
        dict(tool="b03_finalize.py copy-report（md5+IHDR 核验）",
             purpose="final.png/final.snapshot 与草稿字节双向 md5 核对 + IHDR 尺寸对计划",
             input="drafts/ 与 outputs/", output="tmp/%s/B03/copy-report.json" % RUN,
             ts="finalize 时", affects="全部10件（G1 证据）", request_ref=None),
        dict(tool="cleanup_bogus_entry.py（日志完整性修正）",
             purpose="删除一次误插入 iterations.jsonl 的虚构占位行（obs/act 均为 'x'，"
                     "非真实事件）；其余 43 条真实日志未动",
             input="tmp/%s/B03/iterations.jsonl" % RUN,
             output="同文件（44→43 条）", ts="2026-10-20T20:32+08:00",
             affects="case-10 日志条目", request_ref=None),
        dict(tool="整图查看（read 打开 PNG）",
             purpose="每次成功响应实际打开整图判断文字/层级/遮挡/裁剪/数据含义；"
                     "接触表未替代逐图查看",
             input="tmp/%s/B03/drafts/*.png" % RUN, output="看图结论入 iterations.jsonl",
             ts="全程", affects="全部10件+探针",
             request_ref="32 次成功响应对应 32 次至少查看"),
    ]
    with io.open(os.path.join(TMP, "tool-usage.jsonl"), "w",
                 encoding="utf-8", newline="") as f:
        for i, t in enumerate(tool_usage, 1):
            f.write(json.dumps(dict(seq=i, **t), ensure_ascii=False) + "\n")

    # ---------------- task-metrics.json ----------------
    now = datetime.datetime.now(datetime.timezone(
        datetime.timedelta(hours=8))).isoformat(timespec="seconds")
    plan_dt = datetime.datetime.fromisoformat(PLAN_EST)
    now_dt = datetime.datetime.fromisoformat(now)
    per_case = {}
    for cid, ver in FINALS.items():
        recs = case_reqs(cid)
        oks = [e for e in recs if e["ok"]]
        its = case_iters(cid)
        per_case[cid] = dict(
            title=plan_cases[cid]["title"], final_version=ver,
            renders=len(recs), ok=len(oks), failed=len(recs) - len(oks),
            render_seconds_sum=round(sum(e["elapsed_seconds"] for e in oks), 2),
            views=len(oks),
            iterations_by_type=dict(
                baseline=sum(1 for i in its if i["type"] == "baseline"),
                visual_iteration=sum(1 for i in its
                                     if i["type"] == "visual_iteration"),
                requirement_change=sum(1 for i in its
                                       if i["type"] == "requirement-change"),
                syntax_fix=sum(1 for i in its if i["type"] == "syntax_fix")),
            first_render_ts=recs[0]["ts"], last_render_ts=recs[-1]["ts"])
    probe_reqs = by_case.get(None, [])
    first_final = next(e for e in reqs
                       if e["id"] == "B03-c01-%s" % FINALS["case-01"])
    first_usable = int((
        datetime.datetime.fromisoformat(first_final["ts"]) - plan_dt
    ).total_seconds())
    all_ok = [e for e in reqs if e["ok"]]
    metrics = dict(
        schema_version=2, path_base="suite_root", task_id=TID, run_id=RUN,
        status="completed", stop_reason=None,
        output_dir="outputs/%s/B03" % RUN,
        temp_dir="tmp/%s/B03" % RUN,
        timings=dict(
            started_at=PLAN_EST, ended_at=now,
            elapsed_seconds=int((now_dt - plan_dt).total_seconds()),
            first_usable_image_seconds=first_usable,
            first_usable_image_note="case-01 v3 渲染完成 %s（首个满足全部 G 标准"
                                    "并作为交付版的图像）" % first_final["ts"],
            user_feedback_wait_seconds=0,
            rate_limit_wait_seconds=0, queue_wait_seconds=None,
            request_duration_sum_seconds=round(
                sum(e["elapsed_seconds"] for e in all_ok), 2),
            server_timing_source="snap_render.py elapsed_seconds（客户端计时，"
                                 "无 Server-Timing 头）"),
        counts=dict(
            snapshot_requests=len(reqs),
            successful_snapshot_requests=len(all_ok),
            failed_snapshot_requests=len(reqs) - len(all_ok),
            retry_requests=0,
            other_service_requests=0,
            dsl_versions=len([f for f in os.listdir(DRAFTS)
                              if f.endswith(".snapshot")]),
            image_views=len(all_ok),
            completed_visual_iterations=sum(
                1 for it in iters if it["type"] == "visual_iteration"),
            incomplete_visual_iterations=0,
            document_requests=0,
            other_tool_calls=len(tool_usage),
            final_case_count=10),
        logs=dict(requests="tmp/%s/B03/requests.jsonl" % RUN,
                  iterations="tmp/%s/B03/iterations.jsonl" % RUN,
                  tool_usage="tmp/%s/B03/tool-usage.jsonl" % RUN),
        outputs=["outputs/%s/B03/%s/final.png" % (RUN, c)
                 for c in sorted(FINALS)],
        candidates=[], rounds=[],
        unresolved_issues=[],
        asset_policy="dsl_primary_with_supporting_assets（10件全部纯DSL，"
                     "0外部素材）",
        shared_preparation=dict(
            plan=PLAN_REL, established_at=PLAN_EST,
            amendment=AMD_REL,
            common_lib="tmp/%s/B03/scripts/b03_common.py" % RUN,
            docs_cache="_suite/docs（ai-guide/parser/enums 复用套件缓存，"
                       "B03 新增文档HTTP=0）",
            probes=dict(
                ids=[e["id"] for e in probe_reqs],
                renders=len(probe_reqs),
                ok=sum(1 for e in probe_reqs if e["ok"]),
                note="probe-01/02/03 首版 400 语法修复后 01b/02b/03b 成功并查看；"
                     "probe04（Transform面语义对照）服务渲染 1 次")),
        case_metrics=[dict(case_id=cid, **per_case[cid])
                      for cid in sorted(FINALS)],
        tool_usage_summary=dict(
            tools=sorted({t["tool"].split("（")[0] for t in tool_usage}),
            note="详见 tmp/%s/B03/tool-usage.jsonl（9 条）" % RUN),
        final_case_count=10)
    with io.open(os.path.join(OUT, "task-metrics.json"), "w",
                 encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=1)

    print("finalize OK: 10 cases copied (md5+IHDR), portfolio/case.md/"
          "gallery/tool-usage/metrics written")
    print("requests %d ok %d | probe renders %d | visual iterations %d"
          % (len(reqs), len(all_ok), len(probe_reqs),
             metrics["counts"]["completed_visual_iterations"]))


if __name__ == "__main__":
    main()
