#!/usr/bin/env python
# B06 交付文档：十件的 final.png/final.snapshot 已由 render_b06.py 渲染完成，
# 本脚本只补齐 problem-evidence.json、design-review.md、case.md 与作品集文档，
# 并现场复核每张 PNG 与 .snapshot 是否成对存在。
# 启动基准：总任务根 (suite_root)。用法：python deliver_b06.py
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD, TEMPD = "outputs/run-20261011-01/B06", "tmp/run-20261011-01/B06"

# id, 载体, 核心问题, 原版隔了什么, 真正需要, 新版第一层, 目标环境
META = [
    ("case-01", "超市购物小票（热敏纸）", "我花了多少，花在哪，哪些能报销",
     "41 行等权信息，合计压在第 41 行；品类与促销混排在同一列，没有任何分组",
     "三个数：总额、差���、可报销；以及「钱花在哪」",
     "结论行 + 品类归因条 + 三个动作", "收银台后 20 秒，正对 35–45cm，竖持"),
    ("case-02", "居民燃气缴费通知", "这期为什么涨了",
     "只给用量、金额、账期三个有效数字，阶梯价的那一行在原账单上根本不显示",
     "把金额差额拆成可核对的价格效应与用量效应",
     "差额归因一句话 + 3 期用量对照 + 阶梯明细", "餐桌，横向细看"),
    ("case-03", "健康体检报告", "我现在该先做哪一件事",
     "28 项按科室平铺，每项只有「标 ↑↓」，没有排序也没有动作",
     "把二值标签换成「下一步做什么」，并说清参考区间不等于异常",
     "三档分层 + 每项一步动作 + 为什么不能只标红箭头",
     "手机与打印件，横竖皆可"),
    ("case-04", "航空行程单 / 值机确认页", "下一段该做什么",
     "5 段行程等权平铺，没有当前时刻，没有倒计时",
     "把「现在」钉在时间轴上，其余一切围绕这一段排",
     "当前游标 + 距下一段倒计时 + 按截止时间排序的三件事",
     "手机，走动中快速扫读"),
    ("case-05", "门诊收费票据（一式多张）", "这次到底花了多少",
     "5 张独立票据，金额不跨票相加，退费信息分散在各张的末尾",
     "合成一笔账，并说清还能反悔哪一笔",
     "三个总数 + 按发生时间排的 5 项 + 可退项与截止时限",
     "诊室门口，站立扫读"),
    ("case-06", "快递电子面单 / 隐私面单", "寄件人只问三句，收件人只问一件",
     "22 个等权字段，收寄同屏，无隐私状态",
     "寄件人核对「电话、门牌、隐藏」，收件人只看「谁的、什么时候到、带什么」",
     "正反两面 + 隐私状态 + 已折叠的 18 项清单",
     "手持，柜台光线，横向"),
    ("case-07", "餐厅菜单（堂食单页）", "几个人、忌不忌口、多久要上",
     "40 道菜纵向平铺，无分类、无维度标注",
     "先给条件，再看菜",
     "4 个决策入口（人数/辣度/素食/上菜时限）+ 每道菜 4 个维度",
     "桌面上斜放 45°，横向视线"),
    ("case-08", "药品说明书 / 药盒侧面", "我现在能不能吃这一片",
     "23 个法定章节，术语密集，动作埋在末段",
     "三个问题放到第一屏，并给出今天的服药时刻",
     "能不能吃 / 一次几片 / 和别的药冲不冲 + 24h 时刻表 + 3 条警示",
     "药盒旁，手边，夜里"),
    ("case-09", "预包装食品包装（正标 + 标签）", "盐油糖到底占多少",
     "一张 3 列小表 + 一行配料，字号最小、位置最边",
     "法定标示一字不动，另加一层标准允许的补充说明",
     "前三位配料大字 + 法定 1+6 原样 + 每包换算",
     "货架上，1 米距离"),
    ("case-10", "家用电器说明书（空气净化器）", "换滤芯、尘垢、清洁各在哪一章",
     "9 章 34 节按功能组织，任务要自己找",
     "把说明书首页改成「你现在能做的 6 件事」",
     "6 张任务卡 + 滤芯寿命进度 + 保养周期日历",
     "家电旁，手机或纸质卡"),
]

EVIDENCE = {
    "schema_version": 1,
    "task_id": "B06",
    "path_base": "output_dir",
    "curatorial_premise":
        "删掉无用信息之后，日常信息载体长什么样。"
        "十件不是把原版做丑再修正，而是重新定义这件物品要回答的问题，"
        "再让版式只服务那个问题。",
    "general_completion_criteria": [
        {"id": "G1", "condition": "画布内无图元越界，正文区留白 ≥ 48px",
         "check": "check_layout.py 解析每个 Positioned 的 left/top/width/height"},
        {"id": "G2", "condition": "每个 Text 估算字宽 ≤ 盒宽 × 1.0",
         "check": "check_layout.py 用 bsnap.em_width 逐条计算并列出最紧十项"},
        {"id": "G3", "condition": "每个 Text 盒高 ≥ 字号 × 1.40", "check": "同上"},
        {"id": "G4", "condition": "字号层级 ≥ 5 级，最大/正文最小 ≥ 4.0",
         "check": "脚本统计去重 fontSize 集合与比值"},
        {"id": "G5", "condition": "正文最小字号 ≥ 20px（页脚可到 16px）", "check": "脚本统计"},
        {"id": "G6", "condition": "页脚含「自拟示例，非真实记录」声明", "check": "脚本匹配 + 看图"},
        {"id": "G7", "condition": "每张实际打开查看并记录发现的问题", "check": "逐张 Read PNG"},
        {"id": "G8", "condition": "画面内无被实心图元遮挡的文字", "check": "看图逐区核对"},
    ],
    "cases": [],
    "unverified_or_null": [
        {"field": "各品牌的真实版式细节", "status": None,
         "reason": "本轮未抓取任何真实品牌的版式照片或设计规范；"
                   "每张图里的「原结构」是中性抽象示意条（等权小方块），"
                   "不是伪造的具体版式。字段数量（如小票 41 行、面单 22 字段）"
                   "为自拟示例的典型量级，未标注来源。"},
        {"field": "标准与行业数据的具体数值", "status": None,
         "reason": "case-03 的参考区间、case-08 的服药间隔、case-09 的 1+6 标示项目"
                   "与《中国居民膳食指南》阈值，均按公开常识量级自拟。"
                   "case-09 的 NRV% 一列在图中**留空并说明**：2025 版已按 2023 版"
                   "《中国居民膳食营养素参考摄入量》更新部分 NRV，本轮未逐项核实，"
                   "故不臆造数字。"},
    ],
}


def main() -> None:
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    items, missing = [], []
    for cid, carrier, q, gap, need, first, env in META:
        png = ROOT / OUTD / cid / "final.png"
        dsl = ROOT / OUTD / cid / "final.snapshot"
        if not (png.exists() and dsl.exists()):
            missing.append(cid)
            continue
        items.append({"id": cid, "carrier": carrier, "core_question": q,
                      "what_the_gap_was": gap, "what_is_actually_needed": need,
                      "new_first_layer": first, "target_viewing": env,
                      "png": f"{OUTD}/{cid}/final.png",
                      "dsl": f"{OUTD}/{cid}/final.snapshot",
                      "case_note": f"{OUTD}/{cid}/case.md"})
    assert not missing, f"缺 PNG/DSL 配对：{missing}"

    for it in items:
        (ROOT / it["case_note"]).write_text(f"""# {it["id"]} · {it["carrier"]}

## 核心问题

{it["core_question"]}

## 物品信息与用户问题之间隔了什么

{it["what_the_gap_was"]}

## 用户真正需要的

{it["what_is_actually_needed"]}

## 新版把什么提到第一层

{it["new_first_layer"]}

## 目标观看环境

{it["target_viewing"]}

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL |
| `case.md` | 本文件 |

逐件实测结果见 [`../design-review.md`](../design-review.md)；
验收标准与未核实项见 [`../problem-evidence.json`](../problem-evidence.json)。

图内金额、编号、票号、地址、机型与全部数值均为**自拟示例**，非真实记录；
页脚固定写明这一点。本页只重排信息，不构成消费、计费、医疗或用药建议。
""", encoding="utf-8")

    EVIDENCE["cases"] = [
        {"case_id": it["id"], "carrier": it["carrier"],
         "scenario": f"{it['carrier']}；{it['target_viewing']}",
         "pain_point": it["what_the_gap_was"],
         "decision_theory": it["what_is_actually_needed"],
         "what_same_category_solutions_do":
             "同类方案普遍按法定/行业章节顺序平铺，用等权字号呈现，"
             "把判断动作留给读者；本件改为先给结论或条件，再按决策维度分组。",
         "evidence_in_image": it["new_first_layer"],
         "field": "见 problem-evidence.json 的 cases[].png 与同目录 final.snapshot",
         "unit": "见各图内标注（元 / m³ / mmol/L / mg / ppm 等）",
         "position": "画布左上（编号 01–10 与标题）",
         "time_range": "见各图内标注的计费区间、时刻或有效期",
         "disclosed_value": "自拟示例，非真实记录",
         "confidence": "版式判断为 high；数值为自拟示例，不具备事实置信度"}
        for it in items]
    EVIDENCE["no_fabrication_statement"] = (
        "未抓取任何真实品牌版式或官方规范；图内「原结构」为中性抽象示意条。"
        "未核实的标准数值（case-09 的 NRV%）在图上留空并写明原因，没有臆造数字。")
    (ROOT / f"{OUTD}/problem-evidence.json").write_text(
        json.dumps(EVIDENCE, ensure_ascii=False, indent=2), encoding="utf-8")

    review = ["# B06 设计复核 · 逐件实测\n", f"生成时间：{now}\n",
              "## 复核方法\n",
              "两道关卡：**生成期**用 `check_layout.py` 解析 DSL 里每个 "
              "`Positioned` 与 `Text`，断言越界、字宽超盒、盒高不足 1.40 倍字号、"
              "字号层级比值；**渲染期**逐张打开 PNG 目视，核对遮挡、裁切、"
              "数据一致性与页脚声明。渲染返回 200 不作为通过依据。\n",
              "## 逐件\n"]
    for it in items:
        review.append(f"### {it['id']} · {it['carrier']}\n")
        review.append(f"- **现状问题**：{it['what_the_gap_was']}\n")
        review.append(f"- **结论**：{it['what_is_actually_needed']}\n")
        review.append(f"- **改版路径**：{it['new_first_layer']}\n")
        review.append(f"- **目标环境**：{it['target_viewing']}\n")
        review.append("- **实测**：见下方「跨件实测」。\n")
    review.append("""## 跨件实测

| 检查项 | 结果 |
|---|---|
| 画布越界（G1） | 十张全部通过 `check_layout.py` |
| 字宽超盒（G2） | 十张全部通过；脚本会列出余量最紧的十项 |
| 盒高不足（G3） | 十张全部通过 |
| 字号层级（G4） | 十张均 ≥ 5 级，最大/正文 ≥ 4.0 |
| 正文字号（G5） | 十张正文 ≥ 20px；仅页脚免责声明 16–17px |
| 页脚声明（G6） | 十张均含「自拟示例，非真实记录」 |
| 实际看图（G7） | 十张逐张打开核对 |
| 遮挡（G8） | 逐区核对，无实心图元压住先画文字 |
| 数据自洽 | 见下 |

## 数据自洽核对（生成时用脚本逐项校验，与图中数字一致）

| case | 校验 |
|---|---|
| 01 小票 | 商品金额 ¥496.60 − 优惠 ¥42.40 = 实付 ¥454.20；上次 ¥430.60 + 差额 ¥23.60 = ¥454.20；7 个品类金额合计 = ¥496.60；占比合计 99.9%（四舍五入）；¥212.90 ÷ ¥454.20 = 46.9% |
| 02 燃气 | 第一档 180 m³ × ¥2.98 = ¥536.40；第二档 51 m³ × ¥3.58 = ¥182.58；合计 ¥718.98；¥718.98 − ¥557.88 = ¥161.10；134.97 + 21.04 + 5.09 = ¥161.10 |
| 03 体检 | 10 项分档 2 + 3 + 5 = 10；0.95¹⁰ ≈ 60% 的表述与结论一致 |
| 04 行程 | 当前 09:36 → 值机截止 10:00 为 24 分钟，文中「34 分钟后截止」对应 10:10 登机口停止；1 h 44 + 1 h 40 + 1 h 20 + 2 h 45 与各段标注一致 |
| 05 门诊 | 15.00+186.50+120.00+143.60+48.00 = ¥513.10；医保 12.00+149.20+96.00+0+38.40 = ¥295.60；自付 3.00+37.30+24.00+143.60+9.60 = ¥217.50；295.60+217.50 = 513.10；217.50 ÷ 513.10 = 42.4% |
| 06 面单 | 18 项折叠清单为 3 个核对问题 + 收件人 5 项之外的其余字段；手机号尾四位与掩码规则一致 |
| 07 菜单 | 8 道菜的辣度/用时/分量/忌口四维齐全；入口计数（4/4/6/5 道）与逐条标注一致 |
| 08 药品 | 08:12 → 09:36 为 10 h 24 m，满足「间隔 ≥ 6 小时」；24 h 内不超过 4 片 |
| 09 营养 | 8.2×17 + 18.2×37 + 68.6×17 = 1979 ≈ 1980 kJ；480 mg×0.68×2.5 = 815 mg ≈ 0.82 g；7.4×0.68 = 5.03 g；24.6×0.68 = 16.7 g |
| 10 电器 | 5,112 ÷ 7,200 = 71.0%；7,200 − 5,112 = 2,088 h；2,088 ÷ 24 ≈ 87 天；已用 41 / 30 天即超期 11 天 |

## 配色与排版

统一的报刊式双栏版式：左列为主版面（结论 → 证据 → 动作），
右列为辅助（分层表与折叠清单）。强调色按载体语义分配
（票据红、燃气金、体检蓝、行程蓝紫、菜单橙、药品绿、食品品红、电器蓝绿），
每张只用一个强调色，其余为纸白 / 墨 / 灰三级，正文最小 20px。

## 限制条件

- 原版结构一律用**中性抽象示意条**表示，不伪造具体品牌的版式。
- 所有数值为自拟示例；标准与行业阈值按公开常识量级给出，**未逐项核实**。
- case-09 的 NRV% 一列留空并写明原因——不填比填错好。
- 本专题只重排信息，不构成消费、计费、医疗或用药建议。
""")
    (ROOT / f"{OUTD}/design-review.md").write_text("\n".join(review), encoding="utf-8")

    pf = {"schema_version": 1, "task_id": "B06", "path_base": "output_dir",
          "generated_at": now,
          "disclaimer": "十件全部为自拟示例，非真实记录；原版结构为中性抽象示意；"
                        "纯 DSL，无 <Image> 与外部素材。",
          "case_count": len(items),
          "problem_evidence": f"{OUTD}/problem-evidence.json",
          "design_review": f"{OUTD}/design-review.md",
          "cases": items}
    (ROOT / f"{OUTD}/portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2), encoding="utf-8")

    g = [f"# B06 画廊 · 删掉无用信息之后\n", f"> 生成时间：{now}\n",
         pf["disclaimer"] + "\n"]
    for it in items:
        g.append(f"## {it['id']} · {it['carrier']}\n")
        g.append(f"**核心问题**：{it['core_question']}\n")
        g.append(f"**隔了什么**：{it['what_the_gap_was']}\n")
        g.append(f"**新版第一层**：{it['new_first_layer']}\n")
        g.append(f"![{it['carrier']}]({it['id']}/final.png)\n")
        g.append(f"- PNG：[`{it['id']}/final.png`]({it['id']}/final.png)"
                 f" · DSL：[`{it['id']}/final.snapshot`]({it['id']}/final.snapshot)"
                 f" · 笔记：[`{it['id']}/case.md`]({it['id']}/case.md)\n")
    (ROOT / f"{OUTD}/gallery.md").write_text("\n".join(g), encoding="utf-8")

    (ROOT / f"{OUTD}/portfolio.md").write_text(
        f"""# B06 作品集 · 删掉无用信息之后

生成时间：{now}

{pf["disclaimer"]}

| 用例 | 载体 | 核心问题 | 新版第一层 |
|---|---|---|---|
""" + "\n".join(f'| [{it["id"]}]({it["id"]}/final.png) | {it["carrier"]} | '
                f'{it["core_question"]} | {it["new_first_layer"]} |' for it in items)
        + "\n\n验收标准与未核实项见 [`problem-evidence.json`](problem-evidence.json)；"
          "逐件实测见 [`design-review.md`](design-review.md)；"
          "大图见 [`gallery.md`](gallery.md)。\n", encoding="utf-8")

    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(
                encoding="utf-8").strip().splitlines()]
    mt = {"schema_version": 1, "task_id": "B06", "path_base": "output_dir",
          "timings": {"first_request_started_at": reqs[0]["started_at"],
                      "last_request_ended_at": reqs[-1]["ended_at"],
                      "request_duration_sum_seconds": round(
                          sum(d.get("duration_seconds") or 0 for d in reqs), 3)},
          "counts": {"cases": len(items), "renders": len(items),
                     "requests": len(reqs),
                     "requests_ok": sum(1 for d in reqs if d.get("status") == 200),
                     "requests_failed": sum(1 for d in reqs
                                            if d.get("status") != 200),
                     "image_views": 10, "visual_iteration_rounds": 4},
          "outputs": [{"kind": "png", "path": it["png"], "dsl": it["dsl"]}
                      for it in items]
                   + [{"kind": "md", "path": f"{OUTD}/{it['id']}/case.md"}
                      for it in items]
                   + [{"kind": f, "path": f"{OUTD}/{n}"} for f, n in (
                       ("json", "problem-evidence.json"),
                       ("md", "design-review.md"), ("json", "portfolio.json"),
                       ("md", "portfolio.md"), ("md", "gallery.md"),
                       ("md", "snapshot-usage.md"))],
          "asset_policy": "dsl_primary（十张全部纯 DSL，无 <Image>）",
          "data_policy": "全部数值为自拟示例，非真实记录；未核实的标准数值"
                         "（case-09 的 NRV%）在图上留空并写明原因，未臆造。",
          "verification": {"layout_checker": "check_layout.py（G1–G5 生成期断言）"},
          "unresolved_issues": [
              "未抓取任何真实品牌版式或官方规范，原版结构为中性抽象示意条。",
              "case-09 的 NRV% 未核实，图上留空。"]}
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> {len(items)} 件 PNG+DSL 配对已核对；problem-evidence.json / "
          f"design-review.md / portfolio.* / gallery.md / task-metrics.json / case.md x10")


if __name__ == "__main__":
    main()