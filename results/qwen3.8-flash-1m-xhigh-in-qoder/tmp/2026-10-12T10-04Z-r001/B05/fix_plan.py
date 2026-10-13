"""Make work-plan.json valid JSON and record where the delivered screens deviated.

The plan was drafted as a Python literal (implicit string concatenation), which is not
JSON. It is parsed with ast.literal_eval and re-emitted unchanged in meaning: the
criteria written before the first render stay exactly as they were, and the deviations
are appended as a separate, clearly-labelled section.
"""
import ast
import json
from pathlib import Path

fp = Path(__file__).resolve().parent / "work-plan.json"
raw = fp.read_text(encoding="utf-8")
i = raw.index("{")
body = (raw[i:].replace(': true', ': True').replace(': false', ': False')
            .replace(': null', ': None'))
plan = ast.literal_eval(body)
plan["_preamble"] = (
    "本计划写于第一张画面渲染之前（文件创建于 2026-10-13 07:07:33），验收标准在此固定，"
    "后续修改不得暗中降低标准。原文件头注释：\n"
    + raw[:i].replace('"""', "").strip())
plan["deviations_logged_after_delivery"] = [
    {"plan": "case-06 冰箱贴 560×320", "actual": "680×320",
     "reason": "560px 下「服用者 / 药名+剂量 / 时间 / 效期徽章」四列无法在 ≥18px 下"
               "同时容纳（徽章需 128px）；加宽画布而不是缩小字号，保持 1 米可读",
     "standard_changed": "未降低：字号与列间距要求保持"},
    {"plan": "case-07 显示 7×n 服药格", "actual": "14 天格（14 列 × 3 行）",
     "reason": "屏上引用的依从率是 14 天窗口，7 天格里全是绿格却写「漏 4 次」，"
               "自相矛盾；改为与统计同窗口后红/黄格真实出现",
     "standard_changed": "提高：格值与统计必须同源"},
    {"plan": "case-08 清单含批号占位", "actual": "批号/生产厂家/医保编码集中列为「未采集字段」",
     "reason": "逐行空占位会让打印件看起来数据完整但缺项，集中声明更诚实",
     "standard_changed": "未降低"},
    {"plan": "case-10 标注依据等级", "actual": "改为「未查证权威清单」的显式声明",
     "reason": "「依据等级」暗示做过查证，实际没有；改为直接说明未查证",
     "standard_changed": "提高：不暗示未做过的研究"},
]
fp.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
json.loads(fp.read_text(encoding="utf-8"))
print("work-plan.json is now valid JSON with", len(plan["cases"]), "cases and",
      len(plan["deviations_logged_after_delivery"]), "logged deviations")
