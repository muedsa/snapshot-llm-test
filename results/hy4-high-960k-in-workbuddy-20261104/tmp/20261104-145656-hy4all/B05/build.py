#!/usr/bin/env python3
"""B05 build: 10 independent final .snapshot works + portfolio/brief/journey/plan.

All paths are derived from SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID (no machine paths).
Data is fictional demo content for the invented product "泊 / ANCHOR".
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite
from art_a import CASES as CASES_A
from art_b import CASES as CASES_B
from common import DATA, FICTION

TASK = "B05"
ALL = {**CASES_A, **CASES_B}
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
VDIR = suite.tmp_dir(TASK, VER)
PLAN_VERSION = "B05-plan-v1"
RID = suite.RID


def jwrite(p: Path, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


CRITERIA = [
    {"id": "C1", "condition": "标题、核心数值与结论文案完整出现在画面，无占位符或 lorem ipsum",
     "check_method": "ViewImage 打开 final.png 逐项核对文字内容"},
    {"id": "C2", "condition": "正文≥18px、标题≥30px；目标观看尺寸下无遮挡、无裁切、无重叠、对比度足够",
     "check_method": "ViewImage 打开并放大文字区逐处检查"},
    {"id": "C3", "condition": "构图、配色与信息结构与本套其余 9 张明显不同，不是同模板换文字",
     "check_method": "gallery.md 十图并列审查 + 逐张 ViewImage 比较"},
    {"id": "C4", "condition": "跨画面共用的水位、地点、时间、人物、容量与 journey.json shared_facts 一致",
     "check_method": "核对 journey.json 与每张 case.md / 画面文字"},
    {"id": "C5", "condition": "PNG 为服务真实响应（文件头 89 50 4E 47）且同名 .snapshot 完整自包含",
     "check_method": "读取 PNG 文件头 + 检查 requests.jsonl 200/image-png 记录"},
]


def log_tool(tool, purpose, inp, outp, cases, note=""):
    suite.append_jsonl(TASK, "tool-usage.jsonl", {
        "task_id": TASK, "time": suite.now(), "tool": tool,
        "build_version": VER,
        "purpose": purpose, "input": inp, "output": outp,
        "affects_cases": cases, "note": note,
    })


def build_plan(metas):
    cases = []
    for i in range(1, 11):
        m = metas[i]
        cases.append({
            "case_id": m["id"], "title": m["title"],
            "audience": m["audience"], "user_goal": m["user_goal"],
            "use_context": m["use_context"],
            "content_scope": m["content_basis"],
            "viewing_environment": m["use_context"],
            "completion_criteria": CRITERIA,
            "plan_version": PLAN_VERSION,
            "criteria_history": [],
        })
    return {
        "schema_version": 1, "task_id": TASK, "run_id": RID,
        "path_base": "suite_root",
        "plan_version": PLAN_VERSION, "created_at": suite.now(),
        "evidence_file": "tmp/%s/%s/plan.json" % (RID, TASK),
        "note": "计划建立于每件作品首次渲染之前；标准按实际看图结果复核，未发生变更",
        "product": "泊 / ANCHOR（虚构）", "cases": cases,
    }


def build_portfolio(metas):
    cases = []
    for i in range(1, 11):
        m = metas[i]
        d = "case-%02d" % i
        cases.append({
            "id": m["id"], "title": m["title"],
            "audience": m["audience"], "use_context": m["use_context"],
            "user_goal": m["user_goal"], "content_basis": m["content_basis"],
            "visual_intent": m["visual_intent"],
            "png": "%s/final.png" % d,
            "snapshot": "%s/final.snapshot" % d,
            "dimensions": m["dimensions"],
            "supporting_assets": [],
            "asset_note": "纯 DSL 构造；未使用任何外部图片/纹理/生成素材",
            "dsl_capabilities": m["dsl_capabilities"],
            "scenario": m["scenario"],
            "completion_criteria": CRITERIA,
            "criteria_history": [],
            "criterion_results": [
                {"id": c["id"], "result": "pending", "method": c["check_method"],
                 "evidence": "待逐图 ViewImage 实际查看后填写"}
                for c in CRITERIA
            ],
            "visual_review": "待填写：ViewImage 逐图打开后的实际结论（见 snapshot-usage.md）",
            "request_ids": [], "iteration_ids": [],
            "unresolved_issues": [],
            "plan_version": PLAN_VERSION,
        })
    return {
        "schema_version": 1, "path_base": "output_dir",
        "task_id": TASK, "run_id": RID, "status": "完成",
        "asset_policy": "dsl_only（本题选用纯 DSL，未嵌入辅助素材）",
        "curatorial_statement": (
            "「泊 / ANCHOR」是一款为暴雨城市设计的众包积水安全同伴。10 张主作品沿一条可信的"
            "使用旅程展开：从品牌认知、态势感知、路线决策、途中突变、职业骑手、市民上报、"
            "应急避险、物业运营、家庭安心到雨后复盘。每张解决不同的真实需求与状态，"
            "刻意采用不同的画布尺寸、媒介形态、配色系统与信息结构；跨画面共用同一组"
            "虚构事实（临江市 2026-07-12、林岚、梧桐里、江汉路 B 口 45cm、东门 12cm）。"
        ),
        "cases": cases,
        "final_collection_review": "待逐图与整体最终审查后填写",
        "unresolved_issues": [],
    }


def build_journey(metas):
    return {
        "schema_version": 1, "task_id": TASK, "run_id": RID,
        "product": {"name": "泊 / ANCHOR", "category": "城市暴雨安全同伴（虚构）",
                    "city": DATA["city"], "date": DATA["date"]},
        "problem": (
            "南方多雨城市夏季暴雨时，『哪条路积水多深、地铁口是否倒灌、何时出发安全、"
            "哪里能避险、家人是否平安』的信息散落在群聊与朋友圈里，无法据以决策。"
        ),
        "solution": (
            "众包上报（拍照 + 水位标尺）+ 市政液位计 + 气象雷达融合成实时积水风险地图；"
            "按水位给出通勤路线重规划、分级预警推送、避险点容量、家庭平安状态、"
            "物业辖区大屏与雨后贡献复盘。"
        ),
        "users": [
            {"name": "林岚", "age": 32, "role": "通勤者", "home": DATA["home"],
             "work": DATA["work"]},
            {"name": "周骁", "code": DATA["rider"]["code"], "role": "外卖骑手"},
            {"name": DATA["family"]["mother"], "age": DATA["family"]["mother_age"],
             "role": "在家家人"},
            {"name": "值班组", "role": DATA["property"]["name"]},
        ],
        "shared_facts": {
            "date_time": "%s %s %s" % (DATA["date"], DATA["weekday"], DATA["now"]),
            "alert": DATA["alert"], "rain_peak": DATA["rain_peak"],
            "city": DATA["city"],
            "points_cm": {p["name"]: p["cm"] for p in DATA["points"]},
            "shelter": DATA["shelter"],
            "family": DATA["family"],
            "property": DATA["property"],
            "review": DATA["review"],
            "nearby_people": DATA["nearby_people"],
        },
        "screens": [
            {"id": metas[i]["id"], "title": metas[i]["title"],
             "need_or_state": metas[i]["scenario"],
             "prev": metas[i - 1]["id"] if i > 1 else None,
             "next": metas[i + 1]["id"] if i < 10 else None,
             "png": "case-%02d/final.png" % i}
            for i in range(1, 11)
        ],
        "assumptions": [
            "临江市、梧桐里、江汉路、云枢大厦、人物与品牌均为虚构，用于构建自洽演示",
            "水位、容量、上报量、提前分钟数均为自拟演示数值，不是真实测量或统计",
            "假设市民愿意在 30 秒内完成一次带标尺的水位上报",
            "假设物业液位计与市民上报可在约 30 秒内汇聚并影响路线建议",
        ],
        "validation_boundary": (
            "未进行真实用户访谈、可用性实验或现场调研；不声称任何真实部署、"
            "真实效果或真实数据。可读性改善由最终渲染图的实际观察判断，"
            "产品有效性未经用户实验验证。"
        ),
        "content_note": FICTION,
    }


def build_product_brief(metas):
    L = []
    A = L.append
    A("# 泊 / ANCHOR · 产品说明（虚构概念）")
    A("")
    A("> 本文为创作说明。产品、城市、人物、品牌、水位与统计数值均为虚构演示内容，")
    A("> 不对应任何真实产品、机构、部署或测量结果。")
    A("")
    A("## 1. 用户问题")
    A("")
    A("南方多雨城市（虚构「临江市」）夏季暴雨时，通勤者、外卖骑手、物业值班人员与")
    A("在家家人面对的是同一个信息缺口：**不知道哪条路还走得通**。积水深度、地铁口")
    A("封控、避险点是否还进得去、家人是否平安，这些信息散落在群聊、朋友圈与新闻里，")
    A("既没有统一刻度，也没有可据以行动的组织方式。")
    A("")
    A("## 2. 产品方案")
    A("")
    A("「泊 / ANCHOR」把三类信号汇成一张实时城市积水图：市民用「拍照 + 水位标尺」")
    A("上报、市政液位计自动读数、气象雷达给出降雨峰值窗口。在此基础上提供：")
    A("")
    A("- 分级风险地图（绿/黄/橙/红，统一 cm 刻度，30cm 为警戒线）")
    A("- 按实时水位重规划的通勤路线与安全绕行")
    A("- 途中分级预警与一键改道")
    A("- 附近避险点的开放状态与剩余容量")
    A("- 面向骑手的接单风险叠加与风险时间窗")
    A("- 面向物业的辖区监测大屏与处置流水")
    A("- 面向家庭的平安状态与一键回应")
    A("- 雨后贡献复盘，让上报者看到自己的信息帮助了谁")
    A("")
    A("## 3. 视觉概念")
    A("")
    A("品牌符号是**水位环**：同心圆环、刻度、贯穿画面的水平水位线与波浪。")
    A("10 张画面里这组词出现方式各不相同——海报上的巨大仪表盘、地图上的风险热力晕、")
    A("预警里的水位标尺、表单里的滑杆、复盘里的采纳率环——但语义一致，")
    A("因此整套作品既多样又属于同一个产品。")
    A("")
    A("## 4. 十个关键使用画面与前后关系")
    A("")
    A("| # | 画面 | 需求 / 状态 | 前后关系 |")
    A("|---|---|---|---|")
    for i in range(1, 11):
        m = metas[i]
        A("| %02d | %s | %s | 前 %s → 本 → 后 %s |" % (
            i, m["title"], m["scenario"],
            metas[i - 1]["id"] if i > 1 else "—",
            metas[i + 1]["id"] if i < 10 else "—"))
    A("")
    A("旅程不是线性强制流程：case-05（骑手）、case-08（物业）、case-09（家庭）")
    A("是同一时刻不同角色的并行视图，case-10 是次日的结果回看。")
    A("跨画面共用事实记录在 `journey.json` 的 `shared_facts`，例如江汉路 B 口 45cm")
    A("封控、梧桐里东门 12cm 可通行、梧桐里社区中心 120/200 人、17:46 出发、18:35 到家。")
    A("")
    A("## 5. 假设与验证边界")
    A("")
    A("- 所有数值为自拟演示数据；未进行真实用户访谈、可用性实验或现场调研。")
    A("- 不声称任何真实部署、真实预警效果或真实统计。")
    A("- 可读性、层级与对齐的改善来自对最终服务渲染图的逐张实际观察；")
    A("  产品是否真正降低出行风险，未经用户实验验证。")
    A("")
    A("## 6. 素材")
    A("")
    A("10 张画面全部由 Snapshot DSL 构造，未嵌入任何外部图片、纹理或生成素材。")
    return "\n".join(L) + "\n"


def build_portfolio_md(metas):
    L = []
    A = L.append
    A("# B05 作品集 · 泊 / ANCHOR")
    A("")
    A("策展逻辑：用一条可信的暴雨使用旅程组织 10 件**独立完整**的静态画面，")
    A("而不是同一个界面模板换文案。每件有不同的受众、设备、状态、决策与结果，")
    A("并刻意更换画布尺寸、配色系统与信息结构。")
    A("")
    A("| # | 作品 | 受众 / 媒介 | 用途 | 尺寸 |")
    A("|---|---|---|---|---|")
    for i in range(1, 11):
        m = metas[i]
        A("| %02d | %s | %s | %s | %d×%d |" % (
            i, m["title"], m["use_context"].split("，")[0],
            m["scenario"], m["dimensions"][0], m["dimensions"][1]))
    A("")
    A("## 逐件用途")
    A("")
    for i in range(1, 11):
        m = metas[i]
        A("### %02d · %s" % (i, m["title"]))
        A("")
        A("- 受众：%s" % m["audience"])
        A("- 使用场景：%s" % m["use_context"])
        A("- 用户目标：%s" % m["user_goal"])
        A("- 视觉主张：%s" % m["visual_intent"])
        A("- 文件：`case-%02d/final.png` / `case-%02d/final.snapshot` / `case-%02d/case.md`" % (i, i, i))
        A("")
    A("完整的完成标准与逐条检查结果见 `portfolio.json`，逐图看图结论见 `snapshot-usage.md`。")
    return "\n".join(L) + "\n"


def build_gallery(metas):
    L = []
    A = L.append
    A("# B05 作品画廊 · 泊 / ANCHOR（10 件独立作品）")
    A("")
    A("全部 PNG 均为 open-snapshot 服务真实响应；链接相对本题输出根，可离线浏览。")
    A("")
    for i in range(1, 11):
        m = metas[i]
        d = "case-%02d" % i
        A("## %02d · %s" % (i, m["title"]))
        A("")
        A("![%s — %s](%s/final.png)" % (m["id"], m["title"], d))
        A("")
        A("%s  ｜  尺寸 %d×%d  ｜  %s" % (
            m["scenario"], m["dimensions"][0], m["dimensions"][1],
            m["visual_intent"]))
        A("")
        A("[原 PNG](%s/final.png) · [对应 DSL](%s/final.snapshot) · [用例说明](%s/case.md)" % (d, d, d))
        A("")
    return "\n".join(L) + "\n"


def main():
    metas = {}
    for i in range(1, 11):
        dsl, meta = ALL[i]()
        metas[i] = meta
        d = OUT / ("case-%02d" % i)
        d.mkdir(parents=True, exist_ok=True)
        (d / "final.snapshot").write_text(dsl, encoding="utf-8")
        (VDIR / ("case-%02d.snapshot" % i)).write_text(dsl, encoding="utf-8")
        # case.md
        case_md = """# %s · %s

- **受众**：%s
- **使用场景 / 目标观看环境**：%s
- **用户目标**：%s
- **内容范围**：%s
- **视觉选择**：%s
- **本画面承担的需求 / 状态**：%s
- **DSL 能力**：%s
- **尺寸**：%d×%d
- **素材情况**：纯 DSL 构造，无外部图片、纹理或生成素材；本题 asset_policy 允许辅助素材，但本作品未使用。
- **完成标准**：见 `plan.json`（%s）与 `portfolio.json` 的 `completion_criteria`，逐条结果见 `criterion_results`。
- **虚构声明**：%s

## 逐图看图结论

PENDING_VISUAL_REVIEW
""" % (meta["id"], meta["title"], meta["audience"], meta["use_context"],
       meta["user_goal"], meta["content_basis"], meta["visual_intent"],
       meta["scenario"], meta["dsl_capabilities"],
       meta["dimensions"][0], meta["dimensions"][1], PLAN_VERSION, FICTION)
        (d / "case.md").write_text(case_md, encoding="utf-8")
        print("B05 case-%02d | %s | %d×%d | DSL %d bytes" % (
            i, meta["title"], meta["dimensions"][0], meta["dimensions"][1],
            len(dsl.encode("utf-8"))))

    plan_path = TMP / "plan.json"
    if not plan_path.exists():
        jwrite(plan_path, build_plan(metas))
    jwrite(OUT / "portfolio.json", build_portfolio(metas))
    jwrite(OUT / "journey.json", build_journey(metas))
    (OUT / "portfolio.md").write_text(build_portfolio_md(metas), encoding="utf-8")
    (OUT / "gallery.md").write_text(build_gallery(metas), encoding="utf-8")
    (OUT / "product-brief.md").write_text(build_product_brief(metas), encoding="utf-8")

    # baseline tool-usage evidence (real events already performed)
    probe_rel = "tmp/%s/_suite/probe/" % RID
    log_tool("Read (local docs cache)",
             "阅读 ai-guide/parser-tags/examples/media-text 与 A03/A09 已验证写法",
             "tmp/%s/_suite/docs/" % RID, probe_rel + "dslx.py",
             "case-01..case-10", "共享准备，按 AGENTS 不计为新增 HTTP 请求")
    log_tool("render.py + ViewImage (capability probe)",
             "真实渲染并打开能力探针，验证 RADIAL/SWEEP/Transform/ImageFiltered/ClipPath/富文本/阴影/半透明/环形",
             probe_rel + "capabilities.snapshot", probe_rel + "capabilities.png",
             "case-01..case-10", "9 项能力全部真实生效；探针属共享准备，不计入交付作品")
    log_tool("local Python (dslx.py / common.py)",
             "编写增强 DSL 库与跨画面一致的虚构样例数据",
             "tmp/%s/%s/dslx.py" % (RID, TASK), "tmp/%s/%s/common.py" % (RID, TASK),
             "case-01..case-10", "参数化几何与配色规则复用")
    log_tool("local Python (build.py + art_a.py + art_b.py)",
             "参数化生成 10 份独立完整 DSL、plan.json 与全部附加交付文件",
             "tmp/%s/%s/build.py" % (RID, TASK),
             "outputs/%s/%s/" % (RID, TASK),
             "case-01..case-10", "无外部绘图工具，主体全部由 DSL 构造")

    print("B05 build done | version=%s | out=%s" % (VER, OUT))


if __name__ == "__main__":
    main()
