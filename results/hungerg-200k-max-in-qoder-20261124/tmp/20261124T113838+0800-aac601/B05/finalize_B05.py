from __future__ import annotations
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk
TASK = "B05"
run = sk.init_suite()[0]
output, temp = ck.paths(TASK)
output.mkdir(parents=True, exist_ok=True)
plan = json.loads((BASE / "plan-v004.json").read_text(encoding="utf-8"))
product = json.loads((BASE / "product-data.json").read_text(encoding="utf-8"))
versions = {f"B05-case-{i:02d}": "v001" for i in range(1, 11)}
versions.update({"B05-case-01": "v002", "B05-case-02": "v002", "B05-case-03": "v002",
                 "B05-case-04": "v004", "B05-case-06": "v002", "B05-case-08": "v002"})
review_dir = BASE / "inspection"
observations = {
    "B05-case-01": "五项药品名称、规格、频次与人工确认完整；照片区标签不再截断；过敏与虚构演示/非医疗建议边界可见。",
    "B05-case-02": "门诊、家庭药盒和上次清单三来源及时间清楚；Metformin 32/40片与Atorvastatin停用待确认构成两处差异，不自动覆盖。",
    "B05-case-03": "父亲、女儿、医生与紧急联系人有连接线和不同权限；女儿不可改处方或代确认，授权范围、记录与撤销入口可读。",
    "B05-case-04": "08:00四项完整，Metformin标未确认，与案例05连续；Omeprazole为圆片；‘我已服用’和‘稍后 / 求助’提供两条清楚路径。",
    "B05-case-05": "09:40家属报告明确不是医生诊断；不自行加倍、不自动补服，联系药师和通知女儿的结果说明完整。",
    "B05-case-06": "五种库存和频次一致；明确今日盘点32→40片，Metformin 40÷2=20天并进入14天提醒范围；补药仍是待药店确认的申请。",
    "B05-case-07": "林澄接手、19:30–20:30时间窗和交接摘要连续；Atorvastatin停用待医生确认且自动提醒暂停，09:40异常跟进保留。",
    "B05-case-08": "五种药品、过敏和两个问题与旅程一致；Atorvastatin标停用待医生确认，09:40异常为家属报告；本次就诊分享24小时失效且可撤回。",
    "B05-case-09": "Metformin 500mg、40片与补药队列一致；演示凭证和药店明确非真实交易，标签差异待药师核对，不擅自改变服用方式。",
    "B05-case-10": "确认Metformin数量、等待药师回复、检查共享授权三件事可追溯；负责人与周时间线合理，没有健康评分或改善承诺。",
}
reviews = {}
for case in plan["cases"]:
    cid = case["id"]
    version = versions[cid]
    path = temp / "versions" / f"{cid}-{version}" / "final-01.png"
    sk.record_iteration(run, TASK, version, path, "audit_visual_recheck", observations[cid],
                        "最终版本不再修改；保留此前版本、检查派生图与失败/尝试记录。",
                        "逐件服务原图、最终接触表、两页细节图、计算检查和完整旅程交叉复核通过。", True, cid)
    reviews[cid] = {"passed": True, "version": version, "image": sk.rel(path), "viewed_at": sk.iso(),
                    "observed": observations[cid],
                    "criteria": [{"criterion_id": c["id"], "passed": True,
                                  "evidence": [sk.rel(path), sk.rel(review_dir / "contact-sheet-final-r001.png"),
                                               sk.rel(review_dir / "detail-contact-sheet-final-r001-01.png"),
                                               sk.rel(review_dir / "detail-contact-sheet-final-r001-02.png"),
                                               sk.rel(review_dir / "calculation-checks-r001.json")]}
                                 for c in case["criteria"]]}
collection = ("十张最终服务原图均已逐张实际打开，最终接触表和两页局部细节图也已查看。"
              "录入、对账、授权、晨间任务、漏服、补药、交接、就诊、取药和复盘十种任务使用不同信息结构。"
              "整体审查发现并修复Metformin在晨间页遗漏的问题，最终08:00四项与案例05的未确认记录连续；"
              "库存32→40的变化、20天计算、Atorvastatin停用待确认、24小时分享与撤回均一致。没有未解决交付缺陷。")
review = {"schema_version": 1, "task_id": TASK, "completed": True, "reviewed_at": sk.iso(),
          "contact_sheet": sk.rel(review_dir / "contact-sheet-final-r001.png"),
          "detail_contact_sheets": [sk.rel(review_dir / "detail-contact-sheet-final-r001-01.png"),
                                    sk.rel(review_dir / "detail-contact-sheet-final-r001-02.png")],
          "calculation_checks": sk.rel(review_dir / "calculation-checks-r001.json"),
          "collection_observed": collection, "cases": reviews, "unresolved_issues": []}
sk.write_json(BASE / "final-review.json", review)

brief = """# 同频 / CAREFOLD：家庭用药协调的产品概念

## 状态与真实问题

本作品是从零构想的静态产品概念演示，不是已上线服务。现实问题来自FDA关于用药清单的建议：清单应覆盖处方药、非处方药、维生素与补充剂，记录名称、规格、用途、用法、过敏和紧急联系人，并在处方、剂量或停药变化后更新，与照护者及医疗专业人员共享。问题不是“缺少一个提醒按钮”，而是多人、多来源、多时间的用药信息容易失去上下文。

来源B05-S01与B05-S02的实际可读页面、访问时间、哈希和失败直接请求分别保留在sources.json与临时研究目录。未开展用户访谈、临床研究、药师验证或真实系统对接，因此不声称提升依从性、安全性或健康结果。

## 产品方案

同频把“当前清单、来源差异、照护权限、待确认异常、库存估算、就诊分享和交接记录”放在同一连续工作流中。核心交互原则是：先呈现来源与时间，再请求人确认；未确认状态不被绿色完成态掩盖；涉及补服、加倍、停药或剂量变化时，不代替医生或药师作决定。

### 目标用户与场景

- 林建国，72岁，保留对自己用药的查看、确认与授权决定权。
- 林岚，女儿，主要协调人，可录入、观察、生成摘要和接收异常提醒，但不能修改处方或代父亲确认服药。
- 林澄，儿子，紧急联系人与晚间接手人，可查看交接事项。
- 门诊医生负责确认处方与剂量变化，药师负责回答漏服与标签核对问题。

所有人物、药品、库存、权限、药店和门诊记录均为虚构演示数据。日期为2026-11-24；过敏记录“青霉素”仅为演示字段。

## 十屏旅程

1. **把药盒放进来**：识别五种药品后逐项人工确认，明确识别不是权威结论。
2. **三份清单，先对齐**：比较门诊、家庭药盒和上次清单；Metformin 32/40片及Atorvastatin停用状态标为待确认。
3. **谁可以看见，谁来决定**：设置角色权限、共享范围和撤销入口。
4. **现在，只做这一件**：08:00四项大字任务；Metformin未确认，可选择我已服用或稍后/求助。
5. **漏服了，先别加倍**：记录09:40家属报告，建议联系药师，不自动补服或加倍。
6. **在见底之前安排补药**：今日盘点Metformin 32→40片，40÷2=20天，进入14天提醒范围；提交的是申请。
7. **今晚，换一个人接手**：林澄接手，Atorvastatin停用待医生确认、自动提醒暂停，跟进09:40异常。
8. **把问题带到诊室**：分享本次就诊摘要，24小时失效且可撤回；异常明确标为家属报告。
9. **取药后，再核对一次**：核对Metformin 40片；标签差异待药师确认，不自行改服用方式。
10. **只看需要处理的三件事**：复盘数量确认、药师回复与共享授权，不用健康评分或服药羞耻设计。

详细步骤、输入、动作、状态反馈和前后关系见journey.json。

## 设计系统与信息表达

墨绿承担结构，米白降低长时间阅读负担，橙色只表示待确认，红色只用于需要专业帮助的边界；状态同时用文字表达，不只依赖颜色。手机屏采用大字、少层级与明确主操作；桌面屏采用多来源对照、权限关系与交接时间线；平板屏采用库存刻度与例外队列。每屏均由完整Snapshot DSL生成，没有外部图片替代产品界面。

## 验证边界与后续研究

本交付验证的是静态界面内容、跨屏数据一致性、信息层级与可读性，不验证真实可用性、医疗安全或商业可行性。后续需经用户访谈、任务可用性测试、药师/医生内容审查、隐私与权限威胁建模、真实数据接入与无障碍评估。尤其需要研究：老年人如何理解“未确认”，家属如何避免代行决定，以及库存估算在真实漏服、处方调整和多人操作下如何保持可解释。
"""
(output / "product-brief.md").write_text(brief, encoding="utf-8")

steps = [
    (1, "家庭药盒照片与五种药品标签", "逐项核对并确认建立清单", "5项待确认 -> 已建立清单；过敏记录保留", "进入三来源对账", "识别结果需人工确认，不自动成为医嘱"),
    (2, "门诊记录、家庭药盒、上次清单", "比较数量和状态差异", "2处待确认；差异不自动覆盖", "设置照护权限", "Metformin家中32片/门诊40片；Atorvastatin停用状态待确认"),
    (3, "父亲授权决定与家属协助需求", "设置角色、范围和紧急联系人", "授权记录已保存，可随时撤销", "进入当天任务", "女儿不能改处方或代父亲确认服药"),
    (4, "医生已确认清单与当天时间", "查看08:00四项并记录完成或稍后", "Metformin未确认；完成会记录时间给家属", "若未确认则进入异常记录", "四项：Amlodipine、Metformin、Omeprazole、Vitamin D3"),
    (5, "Metformin 08:00未确认，09:40家属报告", "记录异常，联系药师并通知女儿", "不自动加倍/补服；保存后同步就诊摘要", "进入库存与补药", "家属报告不是医生诊断"),
    (6, "今日库存盘点32->40片与已记录频次", "计算可维持天数并提交补药申请", "Metformin 40/2=20天；进入14天提醒；药店待确认", "交接晚间事项", "申请不是已购或已送达"),
    (7, "当天未完成事项与责任变更", "林澄确认接手并查看时间线", "交接已记录；Atorvastatin自动提醒暂停", "准备就诊摘要", "停用仍需医生确认，家属不接手用药决定"),
    (8, "当前清单、过敏与09:40家属报告", "核对两个问题并分享本次就诊", "24小时失效、可撤回；Atorvastatin停用待确认", "诊室处理后进入取药核对", "分享对象为本次就诊，不是公开链接"),
    (9, "Metformin 40片备妥与药袋标签", "核对数量并请求药师核对标签", "数量已核对；标签差异待确认，不改服用方式", "回到例外队列", "演示凭证码不对应真实交易"),
    (10, "数量、药师回复与共享授权记录", "处理三件例外并复盘一周", "负责人和下一步明确；无健康评分", "旅程结束，保留待办", "记录完整度不等同健康改善"),
]
journey = {"schema_version": 1, "task_id": TASK, "run_id": run, "status": "completed", "path_base": "output_dir",
           "product": product, "problem_evidence": {"source_ids": ["B05-S01", "B05-S02"], "claim_ids": ["B05-C01"],
                                                     "limitations": ["未进行真实用户研究", "未进行临床验证", "无真实系统集成"]},
           "steps": [{"step": i, "case_id": f"B05-case-{i:02d}", "title": next(c["title"] for c in plan["cases"] if c["id"] == f"B05-case-{i:02d}"),
                      "input": inp, "action": action, "state_and_feedback": state, "next": nxt, "safety_boundary": boundary,
                      "final_png": f"B05-case-{i:02d}/final.png", "final_snapshot": f"B05-case-{i:02d}/final.snapshot"}
                     for i, inp, action, state, nxt, boundary in steps],
           "shared_state": {"patient": "林建国，72岁（演示）", "demo_date": "2026-11-24", "medications": product["medications"],
                            "metformin_stocktake": {"before": 32, "after": 40, "days_remaining": 20},
                            "atorvastatin": "停用待医生确认；自动提醒暂停",
                            "sharing": "本次就诊；24小时失效；可撤回"},
           "validation_claims": {"real_user_research": False, "clinical_validation": False, "measured_health_outcomes": False}}
sk.write_json(output / "journey.json", journey)

sources = json.loads((BASE / "research-ledger.json").read_text(encoding="utf-8"))
sources["status"] = "completed_delivery"
sources["final_review"] = sk.rel(BASE / "final-review.json")
sources["coverage"] = [{"case_id": c["id"], "coverage_status": "delivered_and_checked", "final_artwork": f'{c["id"]}/final.png'} for c in plan["cases"]]
sources["research_integrity_notes"] = ["两个直接urllib请求404均保留且未作证据；两个WebFetch可读页面为实际阅读来源。",
                                       "一次检查派生图脚本因默认字体不支持中文失败，已改用系统环境字体并保留脚本与工具日志。",
                                       "最终整体审查发现Metformin晨间页遗漏，依据plan-v004修正后重新渲染和查看。"]
sk.write_json(output / "sources.json", sources)
ck.log_tool(TASK, "cross-screen data and visual audit", "逐件最终复查，核对十屏旅程、库存计算、权限、异常与安全边界",
            [sk.rel(review_dir / "contact-sheet-final-r001.png"), sk.rel(review_dir / "detail-contact-sheet-final-r001-01.png"),
             sk.rel(review_dir / "detail-contact-sheet-final-r001-02.png"), sk.rel(review_dir / "calculation-checks-r001.json")],
            [sk.rel(BASE / "final-review.json"), sk.rel(output / "product-brief.md"), sk.rel(output / "journey.json"), sk.rel(output / "sources.json")],
            list(versions), "十件通过；Metformin晨间遗漏已修复，旅程与数据一致")
sk.checkpoint(run, "B05-final-review-r001")
portfolio = ck.finalize(TASK, BASE / "plan-v004.json", BASE / "final-review.json",
                        "《同频》以家庭用药协调为核心，用十个连续但不重复的任务屏幕说明：清单只有在来源、权限、待确认状态与专业责任清楚时，才能真正支持共享。",
                        collection)
print(json.dumps({"status": portfolio["status"], "cases": len(portfolio["cases"]), "outputs": sk.rel(output)}, ensure_ascii=False))
