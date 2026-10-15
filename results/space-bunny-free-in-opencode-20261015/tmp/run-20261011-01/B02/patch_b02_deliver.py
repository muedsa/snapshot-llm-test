#!/usr/bin/env python
# 一次性修补 B02 deliver：touchpoint-map 里的「旅程阶段 → 用例」映射
# 原来用嵌套 json 往返求值，语法过于复杂且难维护，改成直接查表。
# 启动基准：总任务根 (suite_root)。用法：python patch_b02_deliver.py
from pathlib import Path

p = Path(__file__).with_name("deliver_b02.py")
s = p.read_text(encoding="utf-8")

start = s.index('    tm = {\n        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",\n        "project": "旧物仓 · 邻里共享",')
end = s.index('    (ROOT / f"{OUTD}/touchpoint-map.json").write_text(')
new = '''    STAGES = [
        ("还没听说过", ["case-08"], "社区公告栏上的开放日单张"),
        ("路过了，想知道这是什么", ["case-01"], "街角门头"),
        ("想了解能借什么", ["case-04", "case-05"], "工具墙目录与 App 详情"),
        ("准备加入", ["case-02", "case-03"], "借阅证与前台规则立牌"),
        ("正在借", ["case-05"], "App 里的借阅与到期"),
        ("要还了", ["case-09"], "归还检查单"),
        ("被提醒", ["case-06"], "逾期推送"),
        ("坏了", ["case-07"], "维修台挂签"),
        ("来帮忙", ["case-10"], "志愿者排班板"),
    ]
    tps = []
    for it in items:
        tps.append({
            "id": it["id"], "title": it["title"], "touchpoint": it["touchpoint"],
            "user_context": it["user_context"], "user_question": it["user_question"],
            "size": it["size"], "min_body_font_px": it["min_body_font_px"],
            "signature_decision": it["signature_decision"],
            "png": it["png"], "dsl": it["dsl"],
            "journey_stages": [st for st, ids, _ in STAGES if it["id"] in ids],
        })
    tm = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "project": "旧物仓 · 邻里共享",
        "journey_stages": [{"stage": st, "cases": ids, "why": why}
                           for st, ids, why in STAGES],
        "touchpoints": tps,
        "coverage_check": {
            "cases": len(items),
            "distinct_situations": len({it["user_context"] for it in items}),
            "note": "十个情境互不重复；同一情境下的多件（想了解 = case-04 墙 + "
                    "case-05 App）是不同媒介与观看距离，不是同一张海报的两种配色。",
        },
    }
'''
s = s[:start] + new + s[end:]
s = s.replace('    stages = "\\n".join(f\'| {st} | {"、".join(ids)} | {why} |\'\n'
              '                       for st, ids, why in tm["journey_stages"])',
              '    stages = "\\n".join(f\'| {j["stage"]} | {"、".join(j["cases"])} | '
              '{j["why"]} |\'\n                       for j in tm["journey_stages"])')
p.write_text(s, encoding="utf-8")
print("patched")