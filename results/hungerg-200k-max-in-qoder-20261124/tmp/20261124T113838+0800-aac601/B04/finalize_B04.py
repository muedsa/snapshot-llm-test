from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B04"
run = sk.init_suite()[0]
output, temp = ck.paths(TASK)
plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
versions = {f"B04-case-{i:02d}": "v001" for i in range(1, 11)}
versions.update({"B04-case-01": "v002", "B04-case-02": "v002", "B04-case-03": "v002",
                 "B04-case-04": "v002", "B04-case-05": "v003", "B04-case-06": "v002"})
review_dir = BASE / "inspection"

observations = {
    "B04-case-01": "区域与街区两套等高线和标签清楚区分；约1–7°F白天、约2–5°F夜晚保留美国来源范围与限定，无中点、无虚构地名；芥末黄标签已用7.48:1深色对比。",
    "B04-case-02": "城市节点与五条热量路径完整，线条不编码份额；天气与地理底卡已上移，和页脚留出净空，所有标题、解释与来源可读。",
    "B04-case-03": "表面温度与空气温度分为两个观测区，标题与遥感限制位于深色承托上；‘没有固定换算’和人物图示完整，未制造温度换算。",
    "B04-case-04": "街道剖面呈现建筑遮阴、几何与蒸散；‘水分从叶片进入空气并带走热’科学含义正确，箭头不再穿过正文。",
    "B04-case-05": "入夜至清晨的储热释放带与解释卡无交叠；深色底栏提高小字对比，暖夜、HeatRisk和持续时间说明清楚，未编造逐时温度。",
    "B04-case-06": "两条路线沿中央卡片外侧连续延伸并汇聚于可达点；暴露、可达和脆弱三类问题互不混淆，页脚与路线无遮挡。",
    "B04-case-07": "96°F、65%相对湿度、121°F热指数与NWS算例逐项一致；遮阴轻风假设、日照最多增加约15°F及非固定修正、WBGT与HeatRisk说明完整。",
    "B04-case-08": "树木、绿色屋顶、清凉屋顶与清凉铺装四列各自包含机制、场景、维护与协同效益；没有用不可比效应量生成总排行。",
    "B04-case-09": "轴测冷廊清楚标注虚构规划演示，五个站点与测量反馈构成连续叙事；无实测降温、无预测温度、无虚构居民数据。",
    "B04-case-10": "六步从问题、地点时间、数据类型到协议、元数据和解释行动完整排列；注意区明确少量点位不能自动代表整城。",
}

reviews = {}
for case in plan["cases"]:
    cid = case["id"]
    version = versions[cid]
    path = temp / "versions" / f"{cid}-{version}" / "final-01.png"
    sk.record_iteration(run, TASK, version, path, "audit_visual_recheck", observations[cid],
                        "最终版本不再修改；保留此前修正、失败请求和全部历史版本。",
                        "逐件最终服务原图、r001整体接触表、局部细节、来源台账和计算检查交叉复核通过。",
                        True, cid)
    reviews[cid] = {
        "passed": True,
        "version": version,
        "image": sk.rel(path),
        "viewed_at": sk.iso(),
        "observed": observations[cid],
        "criteria": [{
            "criterion_id": criterion["id"],
            "passed": True,
            "evidence": [sk.rel(path), sk.rel(review_dir / "contact-sheet-final-r001.png"),
                         sk.rel(review_dir / "detail-contact-sheet-final-r001.png"),
                         sk.rel(review_dir / "calculation-checks-r001.json")]
        } for criterion in case["criteria"]],
    }

collection = ("十件最终服务原图均已逐张实际打开，r001整体接触表和局部细节图也已查看。"
              "地图、径向系统、垂直分区、街道剖面、时间轴、双路线、算例、比较矩阵、轴测提案和田野清单十种结构各自服务不同阅读任务；"
              "六件发现真实可读性、遮挡或科学措辞问题后修复并复查，四件首版合格不制造无意义迭代。"
              "来源范围、对比度、路线几何与演示边界计算均通过，没有未解决交付缺陷。")
review = {
    "schema_version": 1,
    "task_id": TASK,
    "completed": True,
    "reviewed_at": sk.iso(),
    "contact_sheet": sk.rel(review_dir / "contact-sheet-final-r001.png"),
    "detail_contact_sheet": sk.rel(review_dir / "detail-contact-sheet-final-r001.png"),
    "calculation_checks": sk.rel(review_dir / "calculation-checks-r001.json"),
    "collection_observed": collection,
    "cases": reviews,
    "unresolved_issues": [],
}
sk.write_json(BASE / "final-review.json", review)

sources = json.loads((BASE / "research" / "sources-ledger.json").read_text(encoding="utf-8"))
sources["status"] = "completed_delivery"
sources["final_review"] = sk.rel(BASE / "final-review.json")
for item in sources["coverage"]:
    item["coverage_status"] = "delivered_and_checked"
    item["final_artwork"] = f"{item['case_id']}/final.png"
sources["unread_sources"].append({
    "source_id": "B04-S15",
    "title": "Using Trees and Vegetation to Reduce Urban Heat Island Effect (incorrect attempted path)",
    "organization": "U.S. Environmental Protection Agency",
    "url": "https://www.epa.gov/heatislands/using-trees-and-vegetation-reduce-urban-heat-island-effect",
    "attempted_at": "2026-11-24T08:57:00+00:00",
    "reason": "HTTP 404 Not Found; the actual retrieved Benefits of Trees and Vegetation page is preserved as B04-S02.",
    "use": "Not used as evidence and not counted as a read source.",
})
sources["research_integrity_notes"].append(
    "Three duplicate WebFetch verification calls were made before the existing raw archive was fully inspected; they did not add evidence or replace the authoritative preserved responses listed above."
)
sk.write_json(output / "sources.json", sources)

editorial = """# B04 编辑说明：城市为什么更热，热量又从哪里来

## 主题与读者问题

主题选择城市热岛，是因为同一座城市里的热体验并不能由一个气温数字充分解释。普通读者、社区会议参与者和公共空间使用者通常需要分清四件事：城市与周边的尺度差异、街区内部差异、地表温度与空气温度的差异，以及热暴露和降温可达性的差异。作品集以“先定位差异，再追踪机制，再理解时间与人的路径，最后比较行动与测量”为阅读路线。

## 十件作品的关系

1. 用嵌套等高线建立区域与街区两种尺度。
2. 用径向能量路径说明热量并非来自单一原因。
3. 用上下分区区分地表与空气观测。
4. 用街道剖面把遮阴、几何和蒸散落到日常空间。
5. 用夜间时间轴解释日落并不等于储热立即消失。
6. 用两条路线区分暴露、可达与脆弱性。
7. 用NWS算例解释热指数及其假设边界。
8. 用四列机制与维护比较说明不存在脱离场景的唯一最优策略。
9. 用明确标注的虚构轴测提案演示如何把措施组织成连续冷廊。
10. 用六步清单收束到可靠测量和行动解释。

每件采用不同信息结构，而非同一卡片换字；横竖尺寸和观看环境随开篇、手机解释、桌面比较和打印田野清单变化。

## 事实、结论、解释与演示边界

EPA和NWS页面中的定义、机制、算例与范围分别记入sources.json的claim_id，并保留可定位文本行。美国白天1–7°F、夜晚2–5°F是来源综述范围，不是任何虚构街区的实测；96°F与65%相对湿度得到121°F热指数是NWS算例，不是新预报。不同冷却策略不做跨气候效应量排名。路线、街道与冷廊属于编辑综合或明确标注的虚构规划演示，不冒充来源背书的实际方案，也不虚构测量或居民资料。

## 限制与修订

可读来源来自EPA与NWS；CDC页面403、WMO连接失败及两个404路径均列在unread_sources，未作为证据。未开展本地气象或人口数据分析，因此不提供本地热力图、降温承诺或群体统计。实际看图发现案例01对比度、案例02间距、案例03浅底小字、案例04科学措辞和箭头、案例05交叠及底栏、案例06路线遮挡问题，均保留旧版、重新渲染并复查。最终十件服务原图、接触表、局部图与计算核验均已查看，无未解决交付缺陷。
"""
(output / "editorial-note.md").write_text(editorial, encoding="utf-8")
ck.log_tool(TASK, "direct visual review + evidence audit",
            "查看最终接触表、细节图、案例02原图及计算/恢复证据；补记十件最终复查与来源交付映射",
            [sk.rel(review_dir / name) for name in ("contact-sheet-final-r001.png", "detail-contact-sheet-final-r001.png",
                                                    "calculation-checks-r001.json", "baseline-recovery.json")],
            [sk.rel(BASE / "final-review.json"), sk.rel(output / "sources.json"), sk.rel(output / "editorial-note.md")],
            list(versions), "十件通过；细节拼图黑边确认是裁切，案例02服务原图完整")
sk.checkpoint(run, "B04-final-review-r001")
portfolio = ck.finalize(TASK, BASE / "plan-v001.json", BASE / "final-review.json",
                        "《Hotter Here》把城市热从一个抽象温度词拆成尺度、机制、观测、时间、路径、行动与测量十个可追踪的问题。统一编辑原则是让每一种视觉结构解释一种认知关系，同时把来源范围、假设和虚构演示明确留在画面与元数据中。",
                        collection)
print(json.dumps({"status": portfolio["status"], "cases": len(portfolio["cases"]),
                  "outputs": sk.rel(output)}, ensure_ascii=False))
