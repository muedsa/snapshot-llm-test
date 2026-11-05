#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 build driver — URBAN LOAM visual ecosystem (10 touchpoints)."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
import suite
sys.path.insert(0, str(suite.SUITE_TMP))
sys.path.insert(0, str(suite.tmp_dir("B02")))
import loam as L
import designkit as K
from cases import CASES

TASK = "B02"
RID = suite.RID
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
V1 = suite.tmp_dir(TASK, VER)
NOW = suite.now()
PLAN_VERSION = "plan-v1"


def case_md(m):
    return f"""# {m['id']} · {m['title']}

- **项目**：城市沃土 URBAN LOAM · 社区堆肥与屋顶菜园（自拟演示项目）
- **触点 / 媒介**：{m['touchpoint']}
- **受众**：{m['audience']}
- **观看环境**：{m['viewing']}
- **使用者要完成的事**：{m['user_goal']}
- **内容来源**：自拟品牌、人物、点位、数值与活动，均为虚构演示，不宣称真实部署
- **视觉选择**：{m['visual_intent']}
- **实际使用的 DSL 能力**：{m['dsl_capabilities']}
- **画布尺寸**：{m['W']} × {m['H']} px
- **复用设计系统**：`loam.py`（色板、字体、sprout 徽标、brand_header/brand_footer、chip/tag/card、soil_dots）
  —— 本件按自身密度与比例复用其中组件，验证不同媒介下的一致性。
- **辅助素材**：无。全部主体由 Snapshot DSL 构造，未使用外部图片；点阵码/条码为装饰性示意。
- **计划版本**：{PLAN_VERSION}（首次渲染前建立，见 `tmp/{RID}/B02/plan.md`）。
- **最终自检**：见下方「实际看图自检」与 `portfolio.json` 的 `criterion_results`。

## 实际看图自检

（由 apply_reviews.py 在逐张 ViewImage 复查后写入真实观察结论。）
"""


def build_plan():
    if (TMP / "plan.md").exists():
        return
    lines = ["# B02 作品计划与完成标准（首次渲染前建立）", "",
             f"- 计划版本：`{PLAN_VERSION}`", f"- 建立时间：{NOW}",
             "- 基准：suite_root；本文件位于 `tmp/%s/%s/`。" % (RID, TASK),
             "- 项目：城市沃土 URBAN LOAM（自拟演示项目），为同一项目构建 10 个触点的视觉生态。",
             "- 统一性要求：复用 loam.py 的色板/字体/sprout 徽标/页眉页脚/胶囊等组件；"
             "差异性要求：10 件解决不同内容、状态、媒介与使用任务，不是同一海报换色。",
             "- 调整规则：按看图结果调整标准时追加保留旧/新条件、依据与生效版本，不删除失败标准。", ""]
    for m in CASES:
        lines += [f"## {m['id']} · {m['title']}", "",
                  f"- 稳定 case_id：{m['id']}",
                  f"- 触点：{m['touchpoint']}",
                  f"- 受众：{m['audience']}",
                  f"- 使用目标：{m['user_goal']}",
                  f"- 目标观看环境：{m['viewing']}",
                  f"- 内容范围：自拟演示内容（品牌/人物/点位/数值）",
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
            "id": m["id"], "title": m["title"], "touchpoint": m["touchpoint"],
            "audience": m["audience"], "use_context": m["viewing"],
            "user_goal": m["user_goal"],
            "content_basis": "自拟演示项目：品牌、人物、点位、数值与活动均为虚构，不宣称真实部署",
            "visual_intent": m["visual_intent"],
            "png": "%s/final.png" % m["id"],
            "snapshot": "%s/final.snapshot" % m["id"],
            "dimensions": [m["W"], m["H"]],
            "supporting_assets": [],
            "dsl_capabilities": m["dsl_capabilities"],
            "reused_components": ["loam.sprout_mark", "loam.brand_header/brand_footer",
                                  "loam.chip/tag/card", "loam.soil_dots", "loam.palette"],
            "completion_criteria": [
                {"id": cid, "condition": cond, "method": method,
                 "plan_version": PLAN_VERSION, "established_at": NOW}
                for cid, cond, method in m["criteria"]],
            "visual_review": "待逐图 ViewImage 复查后由 apply_reviews.py 填写真实结论",
            "request_ids": [], "iteration_ids": [], "unresolved_issues": [],
            "plan_version": PLAN_VERSION, "criteria_history": [],
            "criterion_results": [
                {"id": cid, "result": "待逐图复核", "method": method, "evidence": ""}
                for cid, cond, method in m["criteria"]],
        })
    pf = {
        "schema_version": 1, "path_base": "output_dir", "task_id": TASK, "run_id": RID,
        "status": "in_progress", "asset_policy": "dsl_primary_with_supporting_assets",
        "curatorial_statement": (
            "为同一个自拟项目「城市沃土 URBAN LOAM 社区堆肥与屋顶菜园」构建 10 个触点的视觉生态："
            "从招募、导视、分类、身份、App、月度数据、活动日程、兑换、地图到种子包。"
            "十件共享 loam.py 的色板、字体、sprout 徽标、品牌页眉/页脚与胶囊组件，"
            "让人一眼看出是同一项目；同时让每件在媒介形制（竖版海报/长条立牌/横版指南/小横卡/"
            "手机竖屏/横版大屏/方板/横券/横版地图/小竖标签）、信息密度与观看距离上真正不同，"
            "解决各自的使用任务。所有内容在画面内标注为虚构演示。"),
        "cases": cases,
        "final_collection_review": "待整体最终审查后填写",
        "unresolved_issues": [],
    }
    (OUT / "portfolio.json").write_text(json.dumps(pf, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")


def build_portfolio_md():
    lines = ["# B02 作品集策展说明 · 城市沃土 URBAN LOAM", "",
             "**一个项目，十个触点。**「城市沃土」是一个把社区厨余就地堆肥、再用于屋顶菜园的"
             "自拟社区项目。本作品集不是十张不同颜色的海报，而是把同一个视觉系统放进用户"
             "真正会遇见它的十个地方：从第一次听说、找到投放点、判断能不能投、成为志愿者、"
             "日常用 App、看月度成效、参加工作坊、兑换蔬菜、查地图，到把种子带回家。", "",
             "| 触点 | 作品 | 受众 / 使用任务 | 最有辨识度的视觉选择 |", "|---|---|---|---|"]
    for m in CASES:
        lines.append("| %s | %s | %s / %s | %s |" % (
            m["id"], m["title"], m["audience"], m["user_goal"], m["visual_intent"]))
    lines += ["", "## 统一与差异", "",
              "- **统一**：森林绿 / 叶绿 / 陶土 / 奶油 / 琥珀色板；Noto Sans CJK SC + Inter + "
              "Noto Serif CJK SC 字体层级；由两片叶与种子构成的 sprout 徽标；"
              "品牌页眉与页脚；胶囊标签、卡片与土壤点阵底纹。",
              "- **差异**：十种媒介形制、十种尺寸（720×1400 到 1600×1000）、十种信息结构"
              "（标语 / 编号导视 / 双栏对照 / 身份卡 / 仪表盘 / 时间轴 / 票券 / 地图 / 标签）。",
              "- **复用组件压力测试**：sprout 徽标在 52px（App）到 236px（海报）之间复用；"
              "brand_header 在 1200–1600px 横版与 640px 小标签上分别验证；"
              "arc 进度环在 63% 积分环与堆肥去向环形图两种密度下复用。",
              "", "逐件场景、DSL 能力、完成标准与真实看图证据见 `portfolio.json` 与 "
              "`case-*/case.md`；项目问题见 `project-brief.md`，系统规则见 `design-system.json`，"
              "触点情境映射见 `touchpoint-map.json`；逐图预览见 `gallery.md`。", ""]
    (OUT / "portfolio.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_gallery():
    lines = ["# B02 画廊 · 城市沃土十个触点", "",
             "以下每张均为 open-snapshot 服务真实响应 PNG；链接相对本题输出根，可离线浏览。", ""]
    for m in CASES:
        lines += [f"## {m['id']} · {m['title']}", "",
                  f"![{m['title']}]({m['id']}/final.png)", "",
                  f"- 原图 PNG：[{m['id']}/final.png]({m['id']}/final.png)",
                  f"- 完整 DSL：[{m['id']}/final.snapshot]({m['id']}/final.snapshot)",
                  f"- 用例说明：[{m['id']}/case.md]({m['id']}/case.md)",
                  f"- 尺寸：{m['W']}×{m['H']}  ·  {m['viewing']}", ""]
    (OUT / "gallery.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_project_brief():
    (OUT / "project-brief.md").write_text("""# 项目说明 · 城市沃土 URBAN LOAM

> 自拟演示项目：品牌、人物、点位、数值与活动均为虚构，不宣称真实部署或实际环境效益。

## 要解决的问题

城市社区里，厨余通常被混投进生活垃圾，最终填埋或焚烧；而社区屋顶、边角绿地想种点
东西，却缺少稳定、便宜的土壤改良材料。同时，邻居之间缺少一个低门槛、能反复碰面的
共同事务。三件事其实是同一条断掉的循环：**厨余离开社区 → 土壤肥力外购 → 邻里没有协作理由**。

「城市沃土」把循环接回社区内：居民把沥干的水果皮、菜叶、咖啡渣投到巷口的堆肥点，
志愿者每周六带大家翻堆、测温、记录，腐熟的堆肥用于屋顶菜箱与社区绿化，收获的时令蔬菜
再按积分兑换回给参与者。种子图书馆把下一季的种植也留在社区里。

## 服务对象与运作方式

- **服务对象**：巷口社区约 1,200 户居民、沿街小餐饮、社区中心与一所小学。
- **运作方式**：6 个投放点日常开放；志愿者轮值协助分类；每周六上午集中翻堆与育苗；
  App 记录投放重量并累计积分；月度公示回收量、堆肥去向与覆盖情况；
  收获季以兑换券分享蔬菜；种子包在种子图书馆免费领取。
- **用户旅程**：听说（招募海报）→ 找到（导视立牌 / 地图）→ 会投（分类指南）→
  加入（会员卡）→ 日常用（App）→ 看见成效（数据简报）→ 深度参与（工作坊日程）→
  获得反馈（兑换券）→ 延续（种子包）。

## 十件作品各自解决什么

| 触点 | 用户在此要完成的事 | 为什么是这个媒介 |
|---|---|---|
| 招募海报 | 决定要不要加入 | 竖版主视觉，需要一句能停下来的话 |
| 导视立牌 | 找到 3 号投放点 | 行走中远距离扫视，编号与箭头优先 |
| 分类指南 | 3 秒判断能不能投 | 投放箱旁近距离，双栏对照最省时间 |
| 会员卡 | 出示身份、看积分 | 钱包里的小横卡，信息必须极简 |
| App 首页 | 看进度、快速操作 | 手机竖屏，仪表 + 快捷按钮 |
| 数据简报 | 理解月度成效 | 大屏/打印，密集图表与结论 |
| 工作坊日程 | 安排半天时间 | 方形板，纵向时间轴 |
| 兑换券 | 核验权益并兑换 | 横向券面，撕口与码制 |
| 投放点地图 | 找最近的点与路线 | 横版地图，节点 + 图例 |
| 种子包标签 | 正确播种 | 极小竖版包装，参数网格 |

## 视觉概念

两套隐喻叠在一起：**「土壤」**（森林绿、陶土、奶油、点阵颗粒）与**「生长」**
（由两片叶、一根茎、一粒种子构成的 sprout 徽标）。所有触点共享色板、字体层级、
徽标、品牌页眉页脚与胶囊组件，因此一眼能认出是同一个项目；但按各自观看距离
与信息密度重新组织版式，避免把同一张海报缩放十次。

## 诚实性说明

本项目为开放创作题的自拟案例。所有品牌名、人名、点位编号、投放量、积分、减碳换算、
活动时间与点阵码/条码均为虚构演示数据，画面内与 `case-*/case.md` 均已标注；
点阵码与条码是 DSL 参数化生成的装饰性示意图形，不是可扫描编码。
""", encoding="utf-8")


def build_design_system():
    ds = {
        "schema_version": 1, "path_base": "output_dir", "task_id": TASK, "run_id": RID,
        "project": "城市沃土 URBAN LOAM（自拟演示项目）",
        "source_module": "tmp/%s/B02/loam.py（相对 suite_root）" % RID,
        "note": "以下为 10 件作品中真正被代码引用并渲染的系统规则，不是提案。",
        "tokens": L.TOKENS,
        "components": {
            "sprout_mark": "圆角地块外框 + 茎 + 两片 ClipPath 叶形路径 + 种子点；"
                           "在 52/62/64/78/84/86/236 px 等尺寸复用",
            "brand_header": "浅底 RADIAL 或深底 LINEAR 渐变 + soil_dots + 徽标 + "
                            "kicker/标题/副标题/字标 + 琥珀 4px 分隔条 + 触点编号胶囊",
            "brand_footer": "68px 页脚带 + 琥珀顶条 + 品牌字标 + 演示声明 + TP-NN/2026 编号",
            "chip / tag / card / section / stat_pill": "圆角胶囊、描边标签、16px 圆角卡片、章节标题、统计胶囊",
            "leaf": "倾斜透镜形 SVG 路径（Q 曲线 + 坐标旋转），构成徽标与插画叶片",
            "soil_dots": "参数化点阵底纹，8 位 #RRGGBBAA 内联透明度，step 40–54",
        },
        "reusable_geometry": ["K.arc 环形进度/去向图", "K.qr_matrix 装饰点阵码",
                              "K.barcode 装饰条码", "K.notched_card SVG 凹口票券",
                              "K.wave_band 河道", "K.polyline 路线", "K.glow 当前位置光晕",
                              "K.linear/K.radial 渐变", "K.rot Transform 旋转全息块"],
        "density_ratios_tested": ["640×960 小竖标签", "700×1500 长条立牌",
                                   "720×1400 手机竖屏", "1000×620 小横卡",
                                   "1000×1500 竖版海报", "1200×1200 方板",
                                   "1280×640 横券", "1400×1000 横版指南",
                                   "1500×1000 横版地图", "1600×1000 横版大屏"],
        "type_scale_px": {"display": 62, "hero_number": 170, "header_title": 34,
                          "section": 24, "card_title": 25, "body": 18,
                          "caption": 14, "micro": 11},
        "rules": [
            "所有主体、文字、图形、图标由 Snapshot DSL 构造，不使用外部整图。",
            "深色载体用 CREAM 前景字，浅色载体用 INK；强调色只用于编号、数值与 CTA。",
            "每件必须出现 sprout 徽标或品牌字标之一，并用 brand_footer 或等价品牌行收尾。",
            "演示声明与「虚构/示例」标注为每件硬性内容，不可省略。",
            "装饰性码制必须在画面或 case.md 中注明不可扫描。",
        ],
    }
    (OUT / "design-system.json").write_text(json.dumps(ds, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")


def build_touchpoint_map():
    stages = ["认知", "寻址", "学习", "加入", "日常使用", "成效反馈",
              "深度参与", "收获反馈", "空间导航", "延续"]
    items = []
    for i, m in enumerate(CASES):
        items.append({
            "case_id": m["id"], "title": m["title"], "stage": stages[i],
            "touchpoint": m["touchpoint"], "audience": m["audience"],
            "user_situation": m["viewing"], "user_goal": m["user_goal"],
            "png": "%s/final.png" % m["id"],
            "snapshot": "%s/final.snapshot" % m["id"],
        })
    tm = {
        "schema_version": 1, "path_base": "output_dir", "task_id": TASK, "run_id": RID,
        "project": "城市沃土 URBAN LOAM（自拟演示项目）",
        "journey": "听说 → 找到 → 会投 → 加入 → 日常用 → 看成效 → 深度参与 → 得反馈 → 查地图 → 带种子回家",
        "touchpoints": items,
        "coverage_note": "10 个触点覆盖认知、寻址、学习、加入、日常使用、反馈、深度参与、"
                         "空间导航与延续；无两件解决同一使用任务。",
    }
    (OUT / "touchpoint-map.json").write_text(json.dumps(tm, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")


def main():
    build_plan()
    for m in CASES:
        c = K.new_canvas(m["W"], m["H"])
        m["draw"](c)
        dsl = c.render()
        case_dir = OUT / m["id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "final.snapshot").write_text(dsl, encoding="utf-8")
        (case_dir / "case.md").write_text(case_md(m), encoding="utf-8")
        (V1 / (m["id"] + ".snapshot")).write_text(dsl, encoding="utf-8")
        print("  %s : %d bytes" % (m["id"], len(dsl.encode("utf-8"))))
    build_portfolio()
    build_portfolio_md()
    build_gallery()
    build_project_brief()
    build_design_system()
    build_touchpoint_map()
    (OUT / "asset-sources.json").write_text(json.dumps({
        "path_base": "output_dir", "task_id": TASK, "run_id": RID,
        "asset_policy": "dsl_primary_with_supporting_assets",
        "supporting_assets_used": False,
        "statement": "10 件作品全部为纯 Snapshot DSL 构造，未下载或嵌入任何外部照片、纹理或生成整图。",
        "decorative_codes": "case-01 招募点阵码、case-08 兑换码、case-04/10 条码均为 DSL "
                            "参数化生成的装饰性示意图形，不是可扫描编码，已在画面/case.md 注明。",
        "external_sources": [],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    suite.tool_usage(TASK, "Read", "读取 AGENT-BRIEF/AGENTS/PATHS/run-config/TASK/task.json/模板与 DSL 文档缓存",
                     "已完整读取并据此确定路径、留痕与 DSL 契约", source="local docs")
    suite.tool_usage(TASK, "Python.build_script", "参数化生成 10 个触点的独立 DSL 与设计系统/项目说明/触点映射",
                     "生成 10 份 final.snapshot + v1 备份 + 7 个附加交付文件",
                     source="tmp/%s/%s/build.py" % (RID, TASK))
    suite.tool_usage(TASK, "Python.capability_probe", "渲染并 ViewImage 验证 10 项高级 DSL 标签",
                     "RADIAL/SWEEP/arc/ring/Transform/ImageFiltered/Opacity/rich/notched/boxShadow 全部生效",
                     source="tmp/%s/_suite/probe/" % RID)
    print("B02 generated %d DSL works" % len(CASES))


if __name__ == "__main__":
    main()
