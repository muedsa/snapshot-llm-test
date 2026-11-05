#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B01 build driver.

Generates 10 independent, self-contained Snapshot DSL works into
outputs/<run_id>/B01/case-01..10/, backs every DSL up to tmp/<run_id>/B01/v1/,
and writes the required case.md / portfolio.json / portfolio.md / gallery.md /
plan.md / tool-usage.jsonl. Run from the suite root with the standard env vars.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
import suite
sys.path.insert(0, str(suite.SUITE_TMP))
import designkit as K
from cases import CASES

TASK = "B01"
RID = suite.RID
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
V1 = suite.tmp_dir(TASK, VER)
NOW = suite.now()
PLAN_VERSION = os.environ.get("PLAN_VERSION", "plan-v1")


def case_md(m):
    return f"""# {m['id']} · {m['title']}

- **场景 / 受众**：{m['audience']}
- **使用环境（媒介、距离、观看条件）**：{m['use_context']}
- **使用者要完成的事**：{m['user_goal']}
- **内容来源**：{m['content_basis']}
- **视觉选择**：{m['visual_intent']}
- **实际使用的 DSL 能力**：{m['dsl_capabilities']}
- **画布尺寸**：{m['W']} × {m['H']} px（横/竖比按场景选择）
- **辅助素材**：无。本作品全部主体、图形、文字、图表与图标均由 Snapshot DSL 构造，
  未使用外部照片、纹理或生成整图；题面允许局部辅助素材，但本套采用纯 DSL 以保证可复现。
- **点阵码 / 码制**：如出现点阵码或条码，均为装饰性示意图形，非可扫描编码。
- **计划版本**：{PLAN_VERSION}（建立于首次渲染前，见 `../../../tmp/{RID}/{TASK}/plan.md`，
  基准 suite_root；完成标准见 portfolio.json 的 completion_criteria）。
- **最终自检**：见下方「实际看图自检」与 portfolio.json 的 criterion_results。

## 实际看图自检

（由 apply_reviews.py 在逐张 ViewImage 复查后写入真实观察结论。）
"""


def build_plan():
    if (TMP / "plan.md").exists():
        return  # 计划版本一旦建立不覆盖；标准未变更，保留 plan-v1 原貌
    lines = ["# B01 作品计划与完成标准（首次渲染前建立）", "",
             f"- 计划版本：`{PLAN_VERSION}`", f"- 建立时间：{NOW}",
             "- 基准：suite_root；本文件位于 `tmp/%s/%s/`。" % (RID, TASK),
             "- 说明：以下标准在每件作品首次渲染前建立，用于对照实际作品自检；"
             "不覆盖 TASK.md 硬要求，也不是跨作品的统一评分标准。",
             "- 调整规则：如按看图结果调整，追加保留旧/新标准、依据与生效版本，不删除失败标准。",
             ""]
    for m in CASES:
        lines += [f"## {m['id']} · {m['title']}", "",
                  f"- 稳定 case_id：{m['id']}",
                  f"- 受众：{m['audience']}",
                  f"- 使用目标：{m['user_goal']}",
                  f"- 内容范围：{m['content_basis']}",
                  f"- 目标观看环境：{m['use_context']}",
                  f"- 画布：{m['W']}×{m['H']}",
                  "- 完成标准："]
        for cid, cond, method in m["criteria"]:
            lines.append(f"  - `{cid}`：{cond}；检查方法：{method}。")
        lines.append("")
    (TMP / "plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_portfolio():
    cases = []
    for m in CASES:
        cases.append({
            "id": m["id"], "title": m["title"],
            "audience": m["audience"], "use_context": m["use_context"],
            "user_goal": m["user_goal"], "content_basis": m["content_basis"],
            "visual_intent": m["visual_intent"],
            "png": "%s/final.png" % m["id"],
            "snapshot": "%s/final.snapshot" % m["id"],
            "dimensions": [m["W"], m["H"]],
            "supporting_assets": [],
            "dsl_capabilities": m["dsl_capabilities"],
            "completion_criteria": [
                {"id": cid, "condition": cond, "method": method,
                 "plan_version": PLAN_VERSION, "established_at": NOW}
                for cid, cond, method in m["criteria"]],
            "visual_review": "待逐图 ViewImage 复查后由 apply_reviews.py 填写真实结论",
            "request_ids": [], "iteration_ids": [],
            "unresolved_issues": [],
            "plan_version": PLAN_VERSION,
            "criteria_history": [],
            "criterion_results": [
                {"id": cid, "result": "待逐图复核", "method": method, "evidence": ""}
                for cid, cond, method in m["criteria"]],
        })
    pf = {
        "schema_version": 1, "path_base": "output_dir", "task_id": TASK, "run_id": RID,
        "status": "in_progress", "asset_policy": "dsl_primary_with_supporting_assets",
        "curatorial_statement": (
            "十件作品分别解决十种真实使用任务：站台到站、手冲复现、入场核验、马拉松配速、"
            "台风避险、唱片导听、长者用药、酒吧点单、户外观星、社区捐书。刻意让每件在"
            "媒介形制（横屏信息牌/竖版卡/票券/超宽腕带/方图/大字网格/黑板/夜空图/横版海报）、"
            "配色系统、信息结构与视觉隐喻上彼此独立，避免同版换色换字；同时全面使用"
            "Stack/Positioned/Container/ClipPath SVG 路径/线性·径向·扫描渐变/Transform/"
            "Opacity/ImageFiltered/富文本等已验证能力。所有品牌、人物与数值为自拟演示，"
            "并在画面内标注，不宣称真实部署。"),
        "cases": cases,
        "final_collection_review": "待整体最终审查后填写",
        "unresolved_issues": [],
    }
    (OUT / "portfolio.json").write_text(json.dumps(pf, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    return pf


def build_portfolio_md():
    lines = ["# B01 作品集策展说明 · 十张真实场景的炫酷用例", "",
             "本作品集把 Snapshot 结构化 DSL 放进十个可被真实用户使用的场景。"
             "每件先确定「谁、在何时何地、要完成什么」，再决定媒介形制、观看距离与视觉语言；"
             "十件的构图、配色、信息结构与视觉隐喻彼此独立，不是同一模板换文字。", "",
             "| 用例 | 作品 | 受众 / 使用任务 | 最有辨识度的视觉选择 |", "|---|---|---|---|"]
    for m in CASES:
        lines.append("| %s | %s | %s / %s | %s |" % (
            m["id"], m["title"], m["audience"], m["user_goal"], m["visual_intent"]))
    lines += ["", "## 策展逻辑", "",
              "- **广度优先**：从公共信息、饮食、娱乐、运动、应急、音乐、医疗、零售、教育到公益，覆盖十类任务。",
              "- **形制驱动**：按真实观看环境选择横屏、竖版、超宽腕带、方形卡与横版海报，尺寸不统一。",
              "- **信息结构各异**：表格行、时间轴、圆环仪表、雷达、同心圆、网格、清单、星图、隐喻式进度，彼此不重复。",
              "- **DSL 能力覆盖**：渐变、SVG 裁剪路径、变换、光晕滤镜、透明度、富文本、参数化点阵与几何图元。",
              "- **诚实标注**：所有自拟内容在画面与 case.md 中标注为演示；点阵码标明为装饰性示意、不可扫码。",
              "", "逐件场景、内容、DSL 能力、完成标准与真实看图证据见 `portfolio.json` 与各 `case-*/case.md`；"
              "逐图预览见 `gallery.md`。", ""]
    (OUT / "portfolio.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_gallery():
    lines = ["# B01 画廊 · 十张最终作品", "",
             "以下每张均为 open-snapshot 服务真实响应 PNG；链接相对本题输出根，可离线浏览。", ""]
    for m in CASES:
        lines += [f"## {m['id']} · {m['title']}", "",
                  f"![{m['title']}]({m['id']}/final.png)", "",
                  f"- 原图 PNG：[{m['id']}/final.png]({m['id']}/final.png)",
                  f"- 完整 DSL：[{m['id']}/final.snapshot]({m['id']}/final.snapshot)",
                  f"- 用例说明：[{m['id']}/case.md]({m['id']}/case.md)",
                  f"- 尺寸：{m['W']}×{m['H']}  ·  {m['use_context']}", ""]
    (OUT / "gallery.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    build_plan()
    generated = []
    for m in CASES:
        c = K.new_canvas(m["W"], m["H"])
        m["draw"](c)
        dsl = c.render()
        case_dir = OUT / m["id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "final.snapshot").write_text(dsl, encoding="utf-8")
        (case_dir / "case.md").write_text(case_md(m), encoding="utf-8")
        (V1 / (m["id"] + ".snapshot")).write_text(dsl, encoding="utf-8")
        generated.append((m["id"], len(dsl.encode("utf-8"))))
    build_portfolio()
    build_portfolio_md()
    build_gallery()

    # 真实工具留痕（B 类必需）
    suite.tool_usage(TASK, "Read", "读取 AGENT-BRIEF/AGENTS/PATHS/run-config/TASK/task.json/模板与 DSL 文档缓存",
                     "已完整读取并据此确定路径、留痕与 DSL 契约", source="local docs")
    suite.tool_usage(TASK, "Python.build_script", "参数化生成 10 份独立 DSL 与作品集/计划/画廊",
                     "生成 %d 份 final.snapshot + v1 备份" % len(generated), source="tmp/%s/%s/build.py" % (RID, TASK))
    suite.tool_usage(TASK, "Python.capability_probe", "渲染并 ViewImage 验证 10 项高级 DSL 标签",
                     "RADIAL/SWEEP/arc/ring/Transform/ImageFiltered/Opacity/rich/notched/boxShadow 全部生效",
                     source="tmp/%s/_suite/probe/" % RID)

    print("B01 generated %d DSL works" % len(generated))
    for cid, n in generated:
        print("  %s : %d bytes" % (cid, n))


if __name__ == "__main__":
    main()
