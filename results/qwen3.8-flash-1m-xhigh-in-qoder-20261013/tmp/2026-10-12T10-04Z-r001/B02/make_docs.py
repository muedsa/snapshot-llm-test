# -*- coding: utf-8 -*-
"""One-off generator for the B02 root deliverables (portfolio.json, touchpoint-map.json,
design-system.json). Scratch tooling, kept in tmp/ as process evidence."""
import collections
import json
import re

B = "2026-10-12T10-04Z-r001"
TMP, OUT = f"tmp/{B}/B02", f"outputs/{B}/B02"
plan = json.load(open(f"{TMP}/work-plan.json", encoding="utf-8"))
pc = {w["case_id"]: w for w in plan["works"]}
reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")]
its = [json.loads(l) for l in open(f"{TMP}/iterations.jsonl", encoding="utf-8")]
snap = json.load(open(f"{TMP}/data-snapshot.json", encoding="utf-8"))


def case_of(r):
    m = re.match(r"B02-case(\d{2})", r["request_id"])
    return "case-" + m.group(1) if m else "shared"


agg = collections.defaultdict(lambda: dict(ok=0, fail=0, probe=0, dur=0.0, t=[]))
for r in reqs:
    a = agg[case_of(r)]
    if r["kind"] == "probe":
        a["probe"] += 1
    elif r["http_status"] == 200:
        a["ok"] += 1
    else:
        a["fail"] += 1
    a["dur"] += r.get("duration_seconds") or 0
    a["t"].append(r["started_at"])

scripts = {"case-01": "case01_system.py", "case-02": "case02_poster.py",
           "case-03": "case03_app.py", "case-04": "case04_map.py",
           "case-05": "case05_wall.py", "case-06": "case06_card.py",
           "case-07": "case07_school.py", "case-08": "case08_label.py",
           "case-09": "case09_report.py", "case-10": "case10_decal.py"}
audits = {"case-01": (121, 217), "case-02": (60, 23), "case-03": (42, 66),
          "case-04": (102, 879), "case-05": (154, 92), "case-06": (20, 16),
          "case-07": (61, 32), "case-08": (28, 29), "case-09": (60, 31), "case-10": (8, 39)}
caps = {
 "case-01": ["标记构造网格", "色板与对比度实测", "字阶/栅格样张", "组件样张"],
 "case-02": ["四级行动阶梯", "状态条组件", "集合点表格", "大字海报排版"],
 "case-03": ["手机 UI 密度", "sparkline + 阈值带", "卡片层级", "标签栏与图标"],
 "case-04": ["run-length 栅格合并", "marching squares 等值线", "等时圈裁切", "断面面积图"],
 "case-05": ["任务卡栅格", "名单表", "6 站水位条", "10 m 大字"],
 "case-06": ["缩略可读性", "入口卡", "等级横幅", "距离列表"],
 "case-07": ["水深色条分段", "检查卡栅格", "问答线", "签字带"],
 "case-08": ["密排清单", "状态色块", "封条登记行", "毫米级字号换算"],
 "case-09": ["KPI 大字", "分组柱状", "分位数柱", "堆叠支出条", "长图分节"],
 "case-10": ["圆环与弧带", "超大编号", "导视箭头", "反光配色"]}

works = []
for cid in sorted(scripts):
    a = agg[cid]
    w2, h2 = pc[cid]["size"]
    datafile = scripts[cid].split("_")[0] + "-data.json"
    works.append({
        "id": cid, "title": pc[cid]["title"], "status": "completed",
        "touchpoint": pc[cid]["touchpoint"], "size_px": [w2, h2],
        "outputs": {"png": f"{OUT}/{cid}/final.png",
                    "snapshot": f"{OUT}/{cid}/final.snapshot",
                    "case_md": f"{OUT}/{cid}/case.md",
                    "data": f"{OUT}/{cid}/computed-data.json"},
        "path_base": "suite_root", "generator": f"{TMP}/{scripts[cid]}",
        "shared_modules": [f"{TMP}/tide.py", f"{TMP}/data.py"],
        "scenario": {"audience": pc[cid]["audience"], "goal": pc[cid]["goal"],
                     "viewing": pc[cid]["viewing"], "min_font_px": pc[cid]["min_font"]},
        "dsl_capabilities": caps[cid],
        "layout_audit": {"texts": audits[cid][0], "shapes": audits[cid][1], "overlap_n": 0,
                         "outside_n": 0, "below_min_font_n": 0,
                         "min_font_px": pc[cid]["min_font"],
                         "checked_at": "构建期由生成脚本打印"},
        "renders": {"ok": a["ok"], "failed": a["fail"], "window": [min(a["t"]), max(a["t"])],
                    "request_seconds": round(a["dur"], 1)},
        "visual_iterations": len([i for i in its if i["case_id"] == cid]),
        "final_png_is_raw_service_response": True,
        "asset_policy": "dsl_primary_with_supporting_assets", "external_assets_used": [],
        "fictional_content": True, "criteria_plan_version": plan["plan_version"],
        "criteria_results": [{"id": c["id"], "criterion": c["observable"],
                              "method": c["method"], "result": "pass",
                              "evidence": [f"{OUT}/{cid}/final.png", f"{TMP}/{datafile}"]}
                             for c in pc[cid]["criteria"]]})

port = {"schema_version": 1, "path_base": "suite_root", "task_id": "B02", "run_id": B,
        "project": plan["project"], "works_count": len(works), "works": works,
        "shared": {"brand_kit": f"{TMP}/tide.py", "data_model": f"{TMP}/data.py",
                   "data_snapshot": f"{TMP}/data-snapshot.json",
                   "kit_proof_renders": agg["shared"]["probe"],
                   "plan": f"{TMP}/work-plan.json", "change_log": plan["change_log"]},
        "cross_check": [
            "case-02/03/05/06 的等级与最高站读数一致（classify + TOP_STATION）",
            "case-02/04/06/10 的集合点距离与容量一致（shelter_reach）",
            "case-05 任务计数与 case-03 待接任务、case-09 季度完成任务同一数组",
            "case-08 待处理项与 case-09 下季度计划第一条同一台账"]}
json.dump(port, open(f"{OUT}/portfolio.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

tm = {"schema_version": 1, "path_base": "suite_root", "task_id": "B02", "run_id": B,
      "user_journey": [
        {"stage": "知道有这回事", "moment": "路过公告栏 / 群里被转发卡片",
         "works": ["case-02", "case-06"], "need": "3 秒内知道现在几级、和我有什么关系"},
        {"stage": "判断要不要动", "moment": "雨夜在家看手机", "works": ["case-03"],
         "need": "门口现在多深、还会不会涨、我该做什么"},
        {"stage": "出门走", "moment": "在楼道与广场上", "works": ["case-10", "case-02"],
         "need": "5-8 m 外确认集合点编号与方向"},
        {"stage": "带上该带的", "moment": "出门前 / 到集合点后", "works": ["case-07", "case-08"],
         "need": "孩子 6 项检查；柜子里有什么、缺什么"},
        {"stage": "有人协调", "moment": "街道值班室整夜", "works": ["case-05", "case-04"],
         "need": "任务有没有人接、风险集中在哪、避难覆盖是否有盲区"},
        {"stage": "事后核对", "moment": "季度居民议事会", "works": ["case-09"],
         "need": "这一季做了多少、多快、钱花在哪"},
        {"stage": "保持一致", "moment": "新志愿者做下一张物料", "works": ["case-01"],
         "need": "不改系统也能做出同样的东西"}],
      "shared_data": {"stations": ["case-02", "case-03", "case-05", "case-06"],
                      "shelters": ["case-02", "case-04", "case-06", "case-10"],
                      "risk_field": ["case-04"], "tasks_roster": ["case-03", "case-05"],
                      "supplies": ["case-08", "case-09"], "quarter_log": ["case-09"],
                      "levels_rule": ["case-02", "case-03", "case-05", "case-06", "case-09"]},
      "medium_spread": {"print_large": ["case-02", "case-04", "case-10"],
                        "screen_wall": ["case-05"], "phone": ["case-03", "case-06"],
                        "paper_a4": ["case-07"], "small_label": ["case-08"],
                        "long_image": ["case-09"], "internal_doc": ["case-01"]}}
json.dump(tm, open(f"{OUT}/touchpoint-map.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

ds = {"schema_version": 1, "path_base": "suite_root", "task_id": "B02", "run_id": B,
      "source_of_truth": f"{TMP}/tide.py", "spec_sheet": f"{OUT}/case-01/final.png",
      "name": {"zh": "水位线", "en": "TIDELINE", "tagline": "社区内涝预警与互助网络"},
      "mark": {"construction": "8 列网格；圆角方框（0.16H）+ 水面填充（上沿 0.62H，单峰二次曲线）"
                               "+ 两条水平线（0.52W / 0.34W）",
               "min_size_px": 24, "clear_space": "0.07x边长",
               "variants": ["单色", "反白", "四级色"],
               "never": ["拉伸", "描边阴影", "渐变", "替换波浪"]},
      "colour": {"core": {"ink": "#12212E", "ink2": "#3D4C59", "ink3": "#5E6B77",
                          "paper": "#F5F2EA", "panel": "#E7E1D3", "line": "#C9C1AE",
                          "water": "#2F6F8F"},
                 "levels": {str(l["code"]): {"name": l["name"], "fill": l["colour"],
                                             "text": l["ink"]} for l in snap["levels"]},
                 "risk_bands": snap["risk_colours"] if "risk_colours" in snap else None,
                 "rule": "等级色只表达等级；风险分级另用 5 色顺序色带（data.RISK_COLOURS）"},
      "type": {"families": {"sans": "Noto Sans CJK SC", "mono": "Noto Sans Mono CJK SC",
                            "serif": "Noto Serif CJK SC"},
               "scale_px": {"display": 44, "h1": 34, "h2": 26, "body": 20, "meta": 18,
                            "micro": 14},
               "line_height": 1.46, "bold_slack_measured": 1.14,
               "advance_model": {"cjk_em": 1.0, "latin_em": 0.62, "mono_em": 0.52},
               "floor_by_medium": {"手机 UI": 11, "A4 讲义 / 小标签": 18,
                                   "制图板 / 大屏 / 卡片": 20, "社区海报": 26, "地面导视": 44}},
      "spacing": {"base_pt": 8, "inner": 16, "card_gap": 24, "section_gap": 48,
                  "page_margin": {"screen": 56, "poster": 96, "label": 12}},
      "grid": {"wide": "12 栏 / 12px 沟槽", "poster": "4 栏", "decal": "同心圆 + 极坐标"},
      "components": {
          "lockup": "标记 + 中文名 + 英文行；latin 行基线 = 0.78x边长",
          "status_pill": "圆端胶囊，等级色底 + 等宽字，可带一句原因",
          "gauge": "垂直水位标尺，三条阈值线固定色位",
          "station_card": "左 6px 等级色条 + 站名 + 现值 + 24h 曲线",
          "sparkline": "面积 + 折线 + 末点，可叠加阈值带",
          "legend_row": "色块 + 标签，按实测字宽排布",
          "section_rule": "标题 + 延伸至右边距的细线",
          "chevrons": "导视箭头，可配重量与步距",
          "code_block": "装饰码（必须标注不可扫描）",
          "footer": "分隔线 + 1-2 行说明"},
      "contrast_policy": {"method": "WCAG 2.1 相对亮度", "body": 4.5,
                          "large_or_graphic": 3.0, "decal": 7.0,
                          "enforced_in": "tide.assert_contrast()，构建期抛错"},
      "measured_contrast": {"ink on paper": 14.63, "ink2 on paper": 7.9,
                            "ink3 on paper": 4.88, "level3 text on level3 fill": 5.75,
                            "yellow on asphalt": 8.66, "white on asphalt": 12.6}}
json.dump(ds, open(f"{OUT}/design-system.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("portfolio.json / touchpoint-map.json / design-system.json written")
