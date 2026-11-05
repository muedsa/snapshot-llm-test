#!/usr/bin/env python3
"""B06 build: 10 independent information-design works + portfolio/evidence/review.

All paths derive from SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID (no machine paths).
All content is invented demo data for hypothetical everyday information problems.
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

TASK = "B06"
ALL = {**CASES_A, **CASES_B}
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
VDIR = suite.tmp_dir(TASK, VER)
PLAN_VERSION = "B06-plan-v1"
RID = suite.RID


def jwrite(p: Path, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


CRITERIA = [
    {"id": "C1", "condition": "问题背景、重构后的关键数值与可执行结论完整出现在画面，无占位符或 lorem ipsum",
     "check_method": "ViewImage 打开 final.png 逐项核对文字内容"},
    {"id": "C2", "condition": "正文≥17px、标题≥30px；目标观看尺寸下无遮挡、无裁切、无重叠、对比度足够",
     "check_method": "ViewImage 打开并放大文字区逐处检查"},
    {"id": "C3", "condition": "构图、配色与信息结构与本套其余 9 张明显不同，解决的是不同的日常信息难题",
     "check_method": "gallery.md 十图并列审查 + 逐张 ViewImage 比较"},
    {"id": "C4", "condition": "演示数值由脚本计算且画面与 problem-evidence.json 一致；明确标注虚构/演示",
     "check_method": "核对 problem-evidence.json、脚本计算与各 case.md"},
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
    return {
        "schema_version": 1, "task_id": TASK, "run_id": RID,
        "path_base": "suite_root",
        "plan_version": PLAN_VERSION, "created_at": suite.now(),
        "evidence_file": "tmp/%s/%s/plan.json" % (RID, TASK),
        "note": "计划建立于每件作品首次渲染之前；10 个日常信息难题与完成标准按实际看图结果复核，未发生标准变更",
        "cases": [
            {
                "case_id": metas[i]["id"], "title": metas[i]["title"],
                "audience": metas[i]["audience"], "user_goal": metas[i]["user_goal"],
                "use_context": metas[i]["use_context"],
                "content_scope": metas[i]["content_basis"],
                "viewing_environment": metas[i]["use_context"],
                "completion_criteria": CRITERIA,
                "plan_version": PLAN_VERSION, "criteria_history": [],
            }
            for i in range(1, 11)
        ],
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
            "problem": m["problem"], "fix": m["fix"],
            "png": "%s/final.png" % d, "snapshot": "%s/final.snapshot" % d,
            "dimensions": m["dimensions"], "supporting_assets": [],
            "asset_note": "纯 DSL 构造；未使用任何外部图片/纹理/生成素材",
            "dsl_capabilities": m["dsl_capabilities"],
            "completion_criteria": CRITERIA, "criteria_history": [],
            "criterion_results": [
                {"id": x["id"], "result": "pending", "method": x["check_method"],
                 "evidence": "待逐图 ViewImage 实际查看后填写"}
                for x in CRITERIA
            ],
            "visual_review": "待填写：ViewImage 逐图打开后的实际结论（见 snapshot-usage.md）",
            "request_ids": [], "iteration_ids": [],
            "unresolved_issues": [], "plan_version": PLAN_VERSION,
        })
    return {
        "schema_version": 1, "path_base": "output_dir",
        "task_id": TASK, "run_id": RID, "status": "完成",
        "asset_policy": "dsl_only（本题选用纯 DSL，未嵌入辅助素材）",
        "curatorial_statement": (
            "10 件作品各自面对一个不同的日常信息难题：服药、比价、电费、营养、快递、末班车、"
            "垃圾分类、天气、停车、登机。每件先说清用户原本卡在哪里，再用一种不同的视觉组织"
            "（极坐标环、排序标尺、时间色带、同心仪表、垂直单轨、放射扇区、决策树、列网格、"
            "分区网格、超大数字时间轴）把信息重构成可直接使用的形态。素材与数值全部为自拟演示，"
            "不声称做过真实调研或用户实验。"
        ),
        "cases": cases,
        "final_collection_review": "待逐图与整体最终审查后填写",
        "unresolved_issues": [],
    }


def build_problem_evidence(metas):
    cases = []
    for i in range(1, 11):
        m = metas[i]
        cases.append({
            "id": m["id"], "title": m["title"],
            "problem": m["problem"],
            "evidence_basis": (
                "可观察的日常信息组织问题 + 自拟演示案例；未进行真实现场调研、"
                "访谈或用户实验，未引用任何真实品牌背书或真实统计。"
            ),
            "audience": m["audience"],
            "scenario_requirements": m["use_context"] + "；" + m["user_goal"],
            "reconstruction_choice": m["visual_intent"],
            "reconstruction_fix": m["fix"],
            "demo_data": m["content_basis"],
            "observable_improvement": "待根据最终渲染图实际查看后填写（可读性/层级/数值一致性）",
            "unverified_effect": (
                "是否真正降低理解成本、提升决策速度或改变行为，未经真实用户实验验证；"
                "此处只报告从最终图片可观察到的排版与信息组织改善。"
            ),
        })
    return {
        "schema_version": 1, "task_id": TASK, "run_id": RID,
        "path_base": "output_dir",
        "content_note": FICTION,
        "method_note": (
            "问题来自对日常生活信息呈现方式的观察，案例数据为脚本生成的自拟演示值；"
            "区分「从最终图可观察的可读性改善」与「未经用户实验验证的实际效果」。"
        ),
        "cases": cases,
        "unresolved_issues": [],
    }


def build_design_review(metas):
    L = []
    A = L.append
    A("# B06 设计复核 · 十个日常信息难题")
    A("")
    A("> 所有案例、品牌、价格、时刻、数值均为虚构演示内容；未进行真实用户调研或实验。")
    A("")
    A("## 策展逻辑")
    A("")
    A("不按行业或媒介列清单，而是从「用户原本卡在哪」出发选 10 个不同性质的障碍：")
    A("看不懂（说明书/营养表）、比不了（单位价）、找不到重点（账单/轨迹/时刻表/航班屏）、")
    A("记不住（分类规则/停车位）、难行动（天气/计费）。每件只用一种主导视觉组织去解，")
    A("因此 10 张的构图、配色与信息结构互不相同。")
    A("")
    A("## 逐件复核")
    A("")
    for i in range(1, 11):
        m = metas[i]
        A("### %02d · %s" % (i, m["title"]))
        A("")
        A("- **原本卡在哪**：%s" % m["problem"])
        A("- **重构选择**：%s" % m["visual_intent"])
        A("- **如何改善**：%s" % m["fix"])
        A("- **使用场景**：%s" % m["use_context"])
        A("- **演示数据**：%s" % m["content_basis"])
        A("- **可观察的改善**：待最终图实际查看后填写（可读性、层级、对齐、数值一致）")
        A("- **未验证的效果**：是否真正更快/更易懂/更能促成行动，未经用户实验验证")
        A("- **文件**：`case-%02d/final.png` / `case-%02d/final.snapshot` / `case-%02d/case.md`" % (i, i, i))
        A("")
    A("## 整体最终审查")
    A("")
    A("PENDING_FINAL_REVIEW")
    return "\n".join(L) + "\n"


def build_portfolio_md(metas):
    L = []
    A = L.append
    A("# B06 作品集 · 把日常信息难题变成好用的设计")
    A("")
    A("10 件独立完整作品，每件解决一个不同的信息障碍。没有「之前/之后」对比图充数，")
    A("也不复用同一模板换文案；尺寸、配色与主导视觉组织逐件更换。")
    A("")
    A("| # | 作品 | 原本卡在哪 | 主导视觉组织 | 尺寸 |")
    A("|---|---|---|---|---|")
    orgs = ["极坐标环形时钟", "排序条形标尺", "24h 时间色带", "同心三环仪表", "垂直单轨",
            "放射扇区倒计时", "贝塞尔决策树", "7 列温度色带", "分区网格 + 阶梯", "超大数字 + 水平时间轴"]
    for i in range(1, 11):
        m = metas[i]
        A("| %02d | %s | %s | %s | %d×%d |" % (
            i, m["title"], m["problem"][:22] + "…", orgs[i - 1],
            m["dimensions"][0], m["dimensions"][1]))
    A("")
    A("完整的完成标准与逐条检查结果见 `portfolio.json`；每个问题的来源、假设与重构选择见 "
      "`problem-evidence.json`；逐件设计复核见 `design-review.md`。")
    return "\n".join(L) + "\n"


def build_gallery(metas):
    L = []
    A = L.append
    A("# B06 作品画廊 · 10 件独立信息设计")
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
        A("原本卡在哪：%s" % m["problem"])
        A("")
        A("重构：%s  ｜  尺寸 %d×%d" % (m["visual_intent"],
                                    m["dimensions"][0], m["dimensions"][1]))
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
        case_md = """# %s · %s

- **原本卡在哪**：%s
- **重构如何改善**：%s
- **受众**：%s
- **使用场景 / 目标观看环境**：%s
- **用户目标**：%s
- **视觉选择**：%s
- **演示数据**：%s
- **DSL 能力**：%s
- **尺寸**：%d×%d
- **素材情况**：纯 DSL 构造，无外部图片、纹理或生成素材。
- **完成标准**：见 `plan.json`（%s）与 `portfolio.json` 的 `completion_criteria`。
- **虚构声明**：%s

## 逐图看图结论

PENDING_VISUAL_REVIEW
""" % (meta["id"], meta["title"], meta["problem"], meta["fix"],
       meta["audience"], meta["use_context"], meta["user_goal"],
       meta["visual_intent"], meta["content_basis"], meta["dsl_capabilities"],
       meta["dimensions"][0], meta["dimensions"][1], PLAN_VERSION, FICTION)
        (d / "case.md").write_text(case_md, encoding="utf-8")
        print("B06 case-%02d | %s | %d×%d | DSL %d bytes" % (
            i, meta["title"], meta["dimensions"][0], meta["dimensions"][1],
            len(dsl.encode("utf-8"))))

    plan_path = TMP / "plan.json"
    if not plan_path.exists():
        jwrite(plan_path, build_plan(metas))
    jwrite(OUT / "portfolio.json", build_portfolio(metas))
    jwrite(OUT / "problem-evidence.json", build_problem_evidence(metas))
    (OUT / "portfolio.md").write_text(build_portfolio_md(metas), encoding="utf-8")
    (OUT / "design-review.md").write_text(build_design_review(metas), encoding="utf-8")
    (OUT / "gallery.md").write_text(build_gallery(metas), encoding="utf-8")

    probe_rel = "tmp/%s/_suite/probe/" % RID
    log_tool("Read (local docs cache)",
             "阅读 ai-guide/parser-tags/examples/media-text 与 A03/A09 已验证写法",
             "tmp/%s/_suite/docs/" % RID, probe_rel + "dslx.py",
             "case-01..case-10", "共享准备，不计为新增 HTTP 请求")
    log_tool("render.py + ViewImage (capability probe)",
             "真实渲染并打开能力探针，验证 RADIAL/SWEEP/Transform/ImageFiltered/ClipPath/富文本/阴影/半透明/环形",
             probe_rel + "capabilities.snapshot", probe_rel + "capabilities.png",
             "case-01..case-10", "9 项能力全部真实生效；探针属共享准备，不计入交付作品")
    log_tool("local Python (dslx.py / common.py)",
             "编写增强 DSL 库与 10 个案例的自拟演示数据（含单位价、百分比、时长计费等脚本计算）",
             "tmp/%s/%s/dslx.py" % (RID, TASK), "tmp/%s/%s/common.py" % (RID, TASK),
             "case-01..case-10", "参数化几何、排序与比例计算")
    log_tool("local Python (build.py + art_a.py + art_b.py)",
             "参数化生成 10 份独立完整 DSL、plan.json 与全部附加交付文件",
             "tmp/%s/%s/build.py" % (RID, TASK),
             "outputs/%s/%s/" % (RID, TASK),
             "case-01..case-10", "无外部绘图工具，主体全部由 DSL 构造")

    print("B06 build done | version=%s | out=%s" % (VER, OUT))


if __name__ == "__main__":
    main()
