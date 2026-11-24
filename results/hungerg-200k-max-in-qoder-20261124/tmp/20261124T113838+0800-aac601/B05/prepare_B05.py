from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from html import unescape

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B05"
run = sk.init_suite()[0]
sk.begin_task(run, TASK)
research_dir = BASE / "research"
research_dir.mkdir(parents=True, exist_ok=True)

source_specs = [
    ("B05-S01", "Create and Keep a Medication List for Your Health", "U.S. Food and Drug Administration",
     "https://www.fda.gov/consumers/consumer-updates/create-and-keep-medication-list-your-health",
     "b05_s01.webfetch.md", "2026-11-24T09:21:56.362Z", "2025-01-08"),
    ("B05-S02", "Think It Through: Managing the Benefits and Risks of Medicines", "U.S. Food and Drug Administration",
     "https://www.fda.gov/drugs/information-consumers-and-patients-drugs/think-it-through-managing-benefits-and-risks-medicines",
     "b05_s02.webfetch.md", "2026-11-24T09:21:54.658Z", "2018-06-18"),
]
sources = []
for sid, title, org, url, cache_name, fetched_at, updated in source_specs:
    cached = research_dir / cache_name
    assert cached.is_file(), cached
    readable = cached.read_bytes()
    evidence = {
        "readable_source": sk.rel(cached), "readable_sha256": hashlib.sha256(readable).hexdigest(),
        "access_method": "WebFetch readable page; local tool output copied into task research archive",
        "fetched_at": fetched_at,
        "note": "Direct urllib requests to FDA paths returned 404 and remain in requests.jsonl; these readable WebFetch results are the actual reviewed sources.",
    }
    sources.append({"source_id": sid, "title": title, "organization": org, "url": url,
                    "published_or_updated_at": updated, "date_type": "content_current_as_of",
                    "accessed_at": fetched_at, "access_status": "successful_readable_fetch", "http_status": None,
                    "access_evidence": evidence})

meds = [
    {"id": "M01", "name": "Amlodipine", "strength": "5 mg", "purpose": "血压（演示）", "schedule": "每日 08:00 · 1片", "times_per_day": 1, "quantity": 22, "color": "#D06D4B", "shape": "round"},
    {"id": "M02", "name": "Metformin", "strength": "500 mg", "purpose": "血糖（演示）", "schedule": "每日 08:00 / 18:00 · 各1片", "times_per_day": 2, "quantity": 40, "color": "#42776B", "shape": "long"},
    {"id": "M03", "name": "Atorvastatin", "strength": "20 mg", "purpose": "血脂（演示）", "schedule": "每日 21:00 · 1片", "times_per_day": 1, "quantity": 18, "color": "#D3AA47", "shape": "round"},
    {"id": "M04", "name": "Omeprazole", "strength": "20 mg", "purpose": "胃部症状（演示）", "schedule": "每日 08:00 · 1片", "times_per_day": 1, "quantity": 12, "color": "#607CA5", "shape": "round"},
    {"id": "M05", "name": "Vitamin D3", "strength": "1000 IU", "purpose": "补充剂（演示）", "schedule": "每日 08:00 · 1粒", "times_per_day": 1, "quantity": 30, "color": "#8B719B", "shape": "capsule"},
]
for med in meds:
    med["days_remaining"] = med["quantity"] / med["times_per_day"]

product = {
    "name": "同频", "english_name": "CAREFOLD", "status": "invented_concept_demo",
    "patient": {"name": "林建国", "age": 72, "allergy": "青霉素（演示记录）"},
    "caregiver": {"name": "林岚", "relationship": "女儿", "role": "主要协调人"},
    "handoff_caregiver": {"name": "林澄", "relationship": "儿子", "role": "今晚接手"},
    "demo_date": "2026-11-24", "medications": meds,
    "boundaries": ["不自动判断是否补服、加倍或停药", "剂量变更须由医生或药师确认", "所有人物、药品库存与记录均为演示，不构成医疗建议", "未进行真实用户研究或临床验证"],
}

cases_specs = [
    ("01", "把药盒放进来", "女儿在晚饭后首次为父亲建立清单", "用手机拍摄或手动录入五种药品，并在保存前逐项确认", [390, 844], "单一手机录入流；药品缩略图、识别置信与人工确认形成连续任务", ["五种药品名称、规格与频次完整且可核对", "识别结果明确需要人工确认，不假装权威", "过敏与‘非医疗建议’边界可见"]),
    ("02", "三份清单，先对齐", "女儿在桌面端比较门诊单、家庭药盒和上次清单", "找出两处差异，标记待医生确认而不是自动覆盖", [1440, 1000], "三栏对照工作台；差异高亮、来源时间与待确认动作占据主视觉", ["三份来源及更新时间可见", "Metformin数量与Atorvastatin停用状态两处差异一致", "没有自动作出临床判断，确认按钮指向专业人员"]),
    ("03", "谁可以看见，谁来决定", "父亲与女儿设置共享权限和紧急联系人", "让父亲保留决定权，同时授权女儿协调和接收提醒", [1200, 900], "权限关系图与角色卡片并置，突出授权、撤销和隐私边界", ["父亲、女儿和医生角色权限不同且可撤销", "女儿不能修改处方，紧急联系人功能明确", "同意记录与数据范围说明可读"]),
    ("04", "现在，只做这一件", "父亲早晨在手机上查看当天用药", "按大字号卡片完成08:00项目，需要时可选择稍后", [390, 844], "大字单任务手机界面；时间、三项药品和两个主操作直接可见", ["08:00三项与案例01清单一致", "已服用和稍后都有清楚反馈路径", "没有连续打卡压力或服药效果承诺"]),
    ("05", "漏服了，先别加倍", "父亲09:40发现早晨一片未确认，女儿远程协助", "记录情况并联系药师，不自动建议补服", [390, 844], "异常状态手机页；警示色只用于下一步动作，保留时间线和联系人", ["明确不自动加倍、不自动补服", "记录Metformin 08:00未确认和09:40报告一致", "联系药师与通知女儿操作有合理结果说明"]),
    ("06", "在见底之前安排补药", "女儿在平板查看库存并提交演示补药申请", "按每日用量估算见底日，核对后预约药店取药", [1024, 768], "横向库存刻度与补药队列；数量、日数和处理状态用同一数据计算", ["五种库存与每日次数一致", "Metformin 40片/每日2片=20天，处于14天提醒阈值", "补药是申请而非已购或已送达，药店待确认"]),
    ("07", "今晚，换一个人接手", "儿子在桌面端接管父亲晚间协调", "查看未完成事项、确认责任并记录交接摘要", [1440, 1000], "交接时间线与责任看板；过去记录和未来任务有清楚分界", ["林澄接手、21:00 Atorvastatin和09:40异常跟进保持连续", "交接双方确认与时间戳可见", "不把父亲用药决定转移给家属"]),
    ("08", "把问题带到诊室", "女儿与父亲在门诊前打开可分享摘要", "核对过敏、五种药品、两个待问问题和最近异常", [430, 932], "移动就诊卡；一屏分层显示摘要、异常和给医生的问题", ["五种药品、过敏和待问问题与全 journey 一致", "09:40异常被标为家属报告而非医生诊断", "分享对象、有效期和撤回入口明确"]),
    ("09", "取药后，再核对一次", "儿子在药袋交付点核对演示药品", "比对取药清单、数量和待药师确认的标签差异", [390, 844], "手机取药凭证与逐项勾选；凭证码为演示图形，异常状态不被绿色掩盖", ["取药药品和数量与案例06补药队列一致", "标签差异保留待确认，不擅自判断可以服用", "演示凭证码和药店信息明确非真实交易"]),
    ("10", "只看需要处理的三件事", "一周后女儿在平板做家庭照护复盘", "处理一项待问、一项补药和一次授权检查，不带服药羞耻评分", [1180, 820], "克制的例外队列与周时间线；突出三件可行动事项而非健康评分", ["三件例外能追溯至案例02/05/06/08", "记录完成状态和负责人合理", "没有把记录完整度等同健康改善或用户验证"]),
]

cases = []
for num, title, context, goal, dimensions, visual_intent, conditions in cases_specs:
    cid = f"B05-case-{num}"
    cases.append({
        "id": cid, "title": title, "audience": "承担家庭用药协调的成年家属与愿意参与记录的长者",
        "use_context": context, "user_goal": goal, "content_basis": product,
        "visual_intent": visual_intent, "dimensions": dimensions,
        "dsl_capabilities": ["Container", "Stack", "Row", "Column", "Positioned", "Text", "ClipPath", "ClipRRect", "Opacity", "LINEAR"],
        "criteria": [{"id": f"B05-{num}-C{i+1}", "condition": condition,
                      "method": "打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。"}
                     for i, condition in enumerate(conditions)],
        "journey_step": int(num), "previous_case": f"B05-case-{int(num)-1:02d}" if int(num) > 1 else None,
        "next_case": f"B05-case-{int(num)+1:02d}" if int(num) < 10 else None,
    })

plan_file = ck.prepare(TASK, cases, "v001", "pure_dsl_invented_product_demo")
(BASE / "product-data.json").write_text(json.dumps(product, ensure_ascii=False, indent=2), encoding="utf-8")
ledger = {
    "schema_version": 1, "task_id": TASK, "run_id": run, "status": "prepared", "path_base": "suite_root",
    "sources": sources,
    "claims": [
        {"claim_id": "B05-C01", "source_ids": ["B05-S01", "B05-S02"], "applies_to": [c["id"] for c in cases],
         "basis_type": "source_conclusion", "statement": " medication lists should include prescriptions, nonprescription medicines, vitamins and supplements; names, strengths, purpose, instructions, allergies and emergency contacts; lists should be updated and shared with caregivers and health professionals.",
         "locators": ["B05-S01 main text: list fields and review/update/share paragraphs", "B05-S02 main text: up-to-date written list, allergies, sharing and ability to take medicines"],
         "handling": "Product concept addresses this coordination need; screen content and usability are invented demonstrations, not validated outcomes."},
        {"claim_id": "B05-C02", "source_ids": [], "applies_to": [c["id"] for c in cases],
         "basis_type": "demonstration", "statement": "All people, medications, quantities, permissions, pharmacy and clinic records are fictional demo content.",
         "handling": "No claim of clinical appropriateness, diagnosis, real adoption or measured benefit."},
    ],
    "unread_sources": [
        {"source_id": "B05-X01", "title": "Create and Keep a Medication List for Your Health (direct urllib attempt)", "organization": "U.S. Food and Drug Administration",
         "url": "https://www.fda.gov/consumers/consumer-updates/create-and-keep-medication-list-your-health",
         "attempted_at": "2026-11-24T17:21:08.340+08:00", "http_status": 404,
         "reason": "Direct HTTP request returned 404. A later WebFetch readable result was successfully obtained and is preserved as B05-S01; this failed raw request is not evidence.",
         "use": "Not used as evidence."},
        {"source_id": "B05-X02", "title": "Drugs: Consumer Updates (direct urllib attempt)", "organization": "U.S. Food and Drug Administration",
         "url": "https://www.fda.gov/consumers/consumer-updates/drugs",
         "attempted_at": "2026-11-24T17:21:44.364+08:00", "http_status": 404,
         "reason": "Direct HTTP request returned 404 and no readable body was obtained.",
         "use": "Not used as evidence."}], "uncertainties": [
        {"id": "B05-U01", "issue": "No real user interviews, clinical study or live pharmacy integration were performed.", "handling": "Describe as concept validation pending; do not claim improved adherence or safety outcomes."},
        {"id": "B05-U02", "issue": "Medication regimens and stock counts are invented for interface consistency.", "handling": "Repeat demo disclaimer and never use screens as dosing guidance."},
    ],
}
sk.write_json(BASE / "research-ledger.json", ledger)
ck.log_tool(TASK, "WebFetch + Python evidence archive + planning",
            "读取FDA用药清单与用药风险管理页面，保存可读来源与访问证据；固定演示人物和十步旅程",
            [s["url"] for s in sources], [sk.rel(plan_file), sk.rel(BASE / "product-data.json"), sk.rel(BASE / "research-ledger.json")],
            [c["id"] for c in cases], "研究完成；无真实用户验证或外部医疗数据")
print(json.dumps({"task": TASK, "cases": len(cases), "sources": len(sources), "plan": sk.rel(plan_file)}, ensure_ascii=False))
