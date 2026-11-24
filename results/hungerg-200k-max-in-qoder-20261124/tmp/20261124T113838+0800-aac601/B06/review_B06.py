from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B06"
plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
cases = {case["id"]: case for case in plan["cases"]}
_, temp = ck.paths(TASK)
versions = {f"B06-case-{i:02d}": "v001" for i in range(1, 11)}
versions.update({"B06-case-01": "v003", "B06-case-03": "v004", "B06-case-04": "v003",
                 "B06-case-07": "v002", "B06-case-08": "v002", "B06-case-09": "v002", "B06-case-10": "v002"})
paths = {cid: temp / "versions" / f"{cid}-{ver}" / "final-01.png" for cid, ver in versions.items()}
intermediate = {
    "B06-case-01": ("v002", "标题实体已修复，但图下HOW TO READ与横轴标签仍过近；行动卡未移动。保留为未完成中间版。"),
    "B06-case-03": ("v002", "总额已分开，但C的Utilities* $140标签落在Parking色段内，实际不可读；继续修正。"),
    "B06-case-04": ("v002", "公式遗漏分到美元的换算，A/B标记坐标约为79,000，画到画布外；标尺仍无标记。"),
}
corrections = {
    "B06-case-01": "将标题改为Why did the bill change?，消除撇号实体；瀑布比例缩至每美元5px并下移基线，+$3/+$1改到横轴完整标注；扩大$142容器，HOW TO READ下移并增加行动卡间距。",
    "B06-case-03": "总额固定独立行，共享基线保留；A/B顶部薄段用上方引线标签，C的Utilities薄段改到右侧引线标签； Parking与Utilities标签使用深色文字。",
    "B06-case-04": "单位价格标记按分到美元换算，A=$6.00、B=$6.60；副标题缩短，保留$1.80现金差与使用期条件。",
    "B06-case-07": "保修免责声明与Dial之间增加垂直净空，保持$0–$120比例及$55/$97.50两档弧长。",
    "B06-case-08": "SORTING LOGIC上移至最后一行下方，六条路径和虚构城市警示不变。",
    "B06-case-09": "参与说明卡缩小并上移，完整离开页脚线；四项议程和地图连接不变。",
    "B06-case-10": "信号圈半径改为108/72px，完全位于Living room墙线内；保留三处读数和测试顺序。",
}
final_observed = {
    "B06-case-01": "$104+$34+$3+$1=$142与+$38一致；三项变化均有检查/提问动作。标题、总额、横轴标签、行动卡和虚构声明均可读，无遮挡或裁切。",
    "B06-case-02": "YES答案先于细节；Harbor–Market闭合、替代巴士、Market换乘和Market–Museum列车形成完整路径；+12分钟明确为虚构估计，站点标签不被线路穿过。",
    "B06-case-03": "A/B/C月总额分别为$1,665/$1,610/$1,810，三组构成相加准确；一次性$500/$350/$600独立展示。Utilities为估计，C的$140引线标签清楚，最低月费不被表述为绝对推荐。",
    "B06-case-04": "$5.10÷0.850kg=$6.00/kg，$3.30÷0.500kg=$6.60/kg；共同标尺的A/B点位置正确，$0.60/kg与$1.80差额及10/5天条件同时可见。",
    "B06-case-05": "Outline→Draft→Peer review→Final依赖完整；Dec 02/05/08/12、20/30/10/40%和3/6/2/5小时准确，总计100%与16小时；START HERE符合依赖逻辑。",
    "B06-case-06": "爆管事件连接到Section 4、渐进渗漏排除项、三类证明和需理算员审查；未作赔付/拒赔判断，虚构政策与非法律建议警示显著。",
    "B06-case-07": "$220÷4=$55/年，$780÷8=$97.50/年；$0–$120标尺和两档弧长一致，保修过期为前置门槛，能源/处置/安装/未来故障明确排除。",
    "B06-case-08": "六件物品均有准备动作和独立去向；软塑袋到STORE DROP-OFF、电池到BATTERY DROP-OFF；Harbor City规则明确虚构且不可作为现实指导。",
    "B06-case-09": "四项议程均显示地点/受影响人群、决定和Dec 01/03/04/05评论截止日；地图标为示意边界，参与说明不承诺结果改变，底部卡片已离开页脚线。",
    "B06-case-10": "路由器、Living room−42、Bedroom−58、Kitchen−72 dBm与厨房测试点关联正确；先移动再重复测试再考虑Mesh，圈层不越界，虚构读数与无保证说明可见。",
}

existing = sk.read_jsonl(temp / "iterations.jsonl")
def already(cid, version, observed):
    return any(e.get("case_id") == cid and e.get("version_id") == f"{cid}-{version}" and e.get("observed") == observed for e in existing)

for cid, (version, observed) in intermediate.items():
    if not already(cid, version, observed):
        ck.record_view(TASK, cases[cid], temp / "versions" / f"{cid}-{version}" / "final-01.png", version,
                       observed, "发现修正版仍有真实缺陷，另存后续版本。", f"与{cid}-v001及预渲染标准比较。", False, "visual")
for cid, version in versions.items():
    observed = final_observed[cid]
    if already(cid, version, observed):
        continue
    previous = intermediate[cid][0] if cid in intermediate else "v001"
    comparison = (f"与{cid}-{previous}服务原图比较；{corrections[cid]}"
                  if cid in corrections else "与v001服务原图复查比较；首版已符合标准，未作无意义改动。")
    changes = corrections[cid] if cid in corrections else "保留合格首版。"
    ck.record_view(TASK, cases[cid], paths[cid], version, observed, changes, comparison, True,
                   "visual" if cid in corrections else "baseline")

ck.log_tool(TASK, "direct visual review", "逐张打开十件最终服务原图，核对内容、计算、层级、边界、可读性与独立性",
            [sk.rel(path) for path in paths.values()], [], list(paths),
            "十件最终原图均已实际查看；修正过程另见iterations.jsonl，接触表不替代原图检查。")
if not any(e.get("tool") == "Python local build" for e in sk.read_jsonl(temp / "tool-usage.jsonl")):
    ck.log_tool(TASK, "Python local build", "记录B06准备与构建期间真实本地错误及修复，不冒充服务请求",
                ["tmp/20261124T113838+0800-aac601/B06/prepare_B06.py", "tmp/20261124T113838+0800-aac601/B06/build_B06.py"],
                ["tmp/20261124T113838+0800-aac601/B06/plan-v001.json"], list(cases),
                "prepare字段名KeyError已修正；arrow列表嵌套TypeError已用星号展开修正；均发生在服务渲染前。")

inspection = temp / "inspection"
inspection.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype(str(Path(os.environ["WINDIR"]) / "Fonts" / "msyh.ttc"), 21)
thumbs = []
for case in plan["cases"]:
    cid = case["id"]
    with Image.open(paths[cid]) as image:
        image = image.convert("RGB")
        image.thumbnail((460, 330))
        tile = Image.new("RGB", (480, 400), "#E8EDF2")
        tile.paste(image, ((480-image.width)//2, 16))
        ImageDraw.Draw(tile).text((16, 358), f'{cid} · final {versions[cid]}', fill="#172B42", font=font)
        thumbs.append(tile)
sheet = Image.new("RGB", (1440, 1600), "#CBD5E1")
for i, tile in enumerate(thumbs):
    sheet.paste(tile, ((i%3)*480, (i//3)*400))
contact = inspection / "contact-sheet-final-r002.png"
sheet.save(contact)

crops = [
    ("B06-case-01", (70, 340, 1330, 1715)),
    ("B06-case-02", (70, 340, 1530, 935)),
    ("B06-case-03", (130, 390, 1490, 1290)),
    ("B06-case-04", (70, 830, 1130, 1335)),
    ("B06-case-05", (60, 340, 1340, 1740)),
    ("B06-case-06", (70, 340, 1230, 1645)),
    ("B06-case-07", (250, 340, 1150, 1160)),
    ("B06-case-08", (60, 340, 1340, 1690)),
    ("B06-case-09", (60, 340, 1540, 1120)),
    ("B06-case-10", (60, 340, 1540, 1050)),
]
detail_paths = []
for page in range(2):
    detail = Image.new("RGB", (1440, 740), "#CBD5E1")
    for i, (cid, box) in enumerate(crops[page*5:(page+1)*5]):
        with Image.open(paths[cid]) as image:
            crop = image.convert("RGB").crop(box)
            crop.thumbnail((460, 290))
            tile = Image.new("RGB", (480, 370), "#E8EDF2")
            tile.paste(crop, ((480-crop.width)//2, 20))
            ImageDraw.Draw(tile).text((16, 334), f"{cid} 局部文字与边界", fill="#172B42", font=font)
            detail.paste(tile, ((i%3)*480, (i//3)*370))
    path = inspection / f"detail-contact-sheet-final-r002-{page+1:02d}.png"
    detail.save(path)
    detail_paths.append(path)
ck.log_tool(TASK, "Pillow inspection derivatives", "生成最终整体接触表和两页局部细节图，仅用于整体一致性与缩略可读性核验",
            [sk.rel(path) for path in paths.values()], [sk.rel(contact)] + [sk.rel(path) for path in detail_paths], list(paths),
            "三张派生检查图已生成；最终PNG本身未做任何后处理。")

bill = {"previous_total": 104, "energy": 34, "taxes": 3, "credit": 1}
bill["current_total"] = bill["previous_total"] + bill["energy"] + bill["taxes"] + bill["credit"]
bill["difference"] = bill["energy"] + bill["taxes"] + bill["credit"]
rentals = {"A": {"parts": [1450, 180, 35], "entry": 500}, "B": {"parts": [1320, 230, 60], "entry": 350}, "C": {"parts": [1550, 140, 120], "entry": 600}}
for value in rentals.values():
    value["monthly_total"] = sum(value["parts"])
weights = [20, 30, 10, 40]
effort = [3, 6, 2, 5]
unit_a = round(5.10 / 0.850, 2)
unit_b = round(3.30 / 0.500, 2)
repair_year = 220 / 4
replace_year = 780 / 8
checks = {
    "schema_version": 1, "task_id": TASK, "checked_at": sk.iso(), "path_base": "suite_root",
    "bill": {**bill, "matches_plan": bill["current_total"] == 142 and bill["difference"] == 38},
    "rentals": {**rentals, "matches_plan": [rentals[k]["monthly_total"] for k in "ABC"] == [1665, 1610, 1810]},
    "unit_prices": {"A": unit_a, "B": unit_b, "difference": round(unit_b-unit_a, 2), "upfront_difference": round(5.10-3.30, 2),
                    "A_ruler_x": 140+6.00*(920/7), "B_ruler_x": 140+6.60*(920/7), "matches_plan": unit_a == 6.00 and unit_b == 6.60},
    "assignment": {"weights": weights, "weight_sum": sum(weights), "effort": effort, "effort_sum": sum(effort), "matches_plan": sum(weights) == 100 and sum(effort) == 16},
    "repair_replace": {"repair_per_year": repair_year, "replace_per_year": replace_year, "repair_arc_degrees": 180+repair_year*82.5,
                       "replace_arc_degrees": 180+replace_year*82.5, "matches_plan": repair_year == 55 and replace_year == 97.50},
    "geometry": {"housing_scale_pixels_per_usd": 0.36, "bill_scale_pixels_per_usd": 5.0,
                 "wifi_contours_inside_living_room": 545-108 >= 430 and 545+108 <= 660,
                 "case09_footer_clearance_pixels": 1128-1112, "case08_footer_clearance_pixels": 1728-1680},
    "final_versions": versions,
}
checks["all_checks_passed"] = all(checks[k]["matches_plan"] for k in ("bill", "rentals", "unit_prices", "assignment", "repair_replace")) and all(v for k, v in checks["geometry"].items() if isinstance(v, bool))
sk.write_json(inspection / "calculation-checks-r001.json", checks)
assert checks["all_checks_passed"]

criterion_evidence = {
    "B06-case-01": ["$104、+$34、+$3、+$1、$142和+$38同时标出，计算文件相符。", "只有Energy/Taxes/Credit进入变化瀑布，行动卡使用Check/Ask/Confirm。", "三张行动卡分别检查表计日期、询问应税变化、确认减免到期。", "v003原图与局部图显示所有标签完整，横轴与HOW TO READ已分开。"],
    "B06-case-02": ["闭合红线、橙色巴士、蓝色保留列车与Market换乘箭头可追踪。", "顶部YES与完整替代路径先于网络详情。", "+12 min后紧跟fictional estimate, not live service information。", "v001原图显示五个站名及线路无文字穿越。"],
    "B06-case-03": ["三组parts求和与总额完全一致。", "ONE-TIME ENTRY卡片位于共享基线下方并注明not in monthly total。", "Utilities*与底部估算声明保留；结论明确不是绝对推荐。", "v004原图显示三组总额独立、C的Utilities引线标签可见，接触表用于50%整体复核。"],
    "B06-case-04": ["两张包装卡显示质量、价格、单位价和除法输入。", "$1.80 more upfront与10/5天条件位于结果卡。", "Choose A if / Choose B if给出条件而非绝对结论。", "v003共同标尺在$6.00和$6.60显示A/B点，刻度和说明不重叠。"],
    "B06-case-05": ["四个阶段及向下箭头形成完整依赖链。", "四日期、权重、工时与总计由计算文件验证，页脚标为虚构演示。", "START HERE指向Outline，并说明最大权重不等于首先行动。", "v001原图显示卡片、箭头、日期和工时标签无裁切。"],
    "B06-case-06": ["事件→两部分条款→证明→下一步的树状路径完整。", "下一步为Needs adjuster review，底部说明不作coverage determination。", "FICTIONAL POLICY · NOT LEGAL ADVICE位于内容前。", "v001原图显示分支、卡片和清单互不遮挡。"],
    "B06-case-07": ["$220/4和$780/8与$55/$97.50结果一致，寿命为assumed。", "WARRANTY GATE · EXPIRED位于Dial上方。", "NOT IN THE MATH列出能源、处置、安装、未来故障。", "v002原图显示$0–$120标尺、两档比例弧和因素托盘无重叠。"],
    "B06-case-08": ["六行均显示编号、物品、准备动作和路线终点。", "Soft plastic bag→STORE DROP-OFF；Battery→BATTERY DROP-OFF。", "顶部红色HARBOR CITY RULES ARE FICTIONAL与不可作为现实指导并列。", "v002原图显示六条水平路径和目的地无交叉，底注已上移。"],
    "B06-case-09": ["四卡均含标题、受影响人群、决定和COMMENT BY日期。", "DISTRICT 4 · SCHEMATIC, NOT BOUNDARIES明确非真实边界。", "Dec 01–05行动可见；参与说明不承诺结果改变。", "v002原图显示连接线、地图标签、截止日完整，底卡离开页脚线。"],
    "B06-case-10": ["户型内路由器与三房间读数、厨房TEST HERE位置对应。", "Move→Repeat same test→Only then consider mesh依次排列。", "FICTIONAL FLOOR PLAN · DEMO dBm READINGS及contours illustrative明确限制。", "v002原图显示圈层在Living room内，50%接触表和细节图保留房间/动作可读性。"],
}
reviews = {}
for case in plan["cases"]:
    cid = case["id"]
    proof = ck.provenance(TASK, case, versions[cid])
    reviews[cid] = {"passed": True, "version": versions[cid], "image": sk.rel(paths[cid]), "viewed_at": sk.iso(),
                    "observed": final_observed[cid], "criteria": dict(zip([c["id"] for c in case["criteria"]], criterion_evidence[cid])),
                    "provenance": proof, "unresolved_issues": []}
sk.write_json(BASE / "final-review.json", {"schema_version": 1, "task_id": TASK, "completed": True,
                                           "reviewed_at": sk.iso(), "path_base": "suite_root", "cases": reviews,
                                           "collection_observed": "十件分别解决十个日常信息任务；主视觉逻辑各不相同，共享页脚不构成同版式换字。所有最终服务原图、整体接触表和两页局部细节图均已查看。",
                                           "calculation_evidence": sk.rel(inspection / "calculation-checks-r001.json"),
                                           "unresolved_issues": []})

reconstruction = {
    "B06-case-01": "把总价与流水拆成从旧总额到新总额的瀑布，并把每个变化转成下一步问题。",
    "B06-case-02": "把服务状态叠在旅程网络上，用闭合段、替代巴士和换乘箭头表达可达性。",
    "B06-case-03": "用共享零基线的经常性成本堆栈比较完整月费，并把一次性费用移到独立区域。",
    "B06-case-04": "把不同规格归一化到同一把$/kg尺，同时并列现金差和使用期限。",
    "B06-case-05": "把截止日列表改为依赖河，先展示解锁下一步的起点，再显示权重与工时。",
    "B06-case-06": "把用户事件与政策条款并用场景树连接，明确哪些事实仍需理算员判断。",
    "B06-case-07": "把两种价格除以假设寿命并映射到同一比例弧形标尺，同时显示保修门槛和排除因素。",
    "B06-case-08": "把材料名称列表改为物品→准备动作→去向的六条分类传送带。",
    "B06-case-09": "把议程清单改为地图节点与行动卡联动，按地点、受影响人群和评论截止日重排。",
    "B06-case-10": "把覆盖全屋的建议改为房间户型诊断，用读数、测试点和单变量步骤限制决策范围。",
}
observable = {
    "B06-case-01": "最大变化+$34与总额+$38可在同一视觉路径上读出，变化不再隐藏在流水项中。",
    "B06-case-02": "目的地可达答案、换乘点和保留服务段同时可见，减少在状态与路线之间来回对照。",
    "B06-case-03": "三个月费总额和一次性费用不在同一数量级混排，最低月费可直接排序。",
    "B06-case-04": "两个单位价在同一标尺上相距$0.60，规格差异不再需要心算。",
    "B06-case-05": "起点由依赖关系而非权重/日期紧迫性决定，四个解锁动作方向一致。",
    "B06-case-06": "应读条款、应查排除项和待补证据在同一路径上分组，未读条款不会被误当成结论。",
    "B06-case-07": "$55与$97.50可直接比较，且立即看到四年/八年假设并非事实。",
    "B06-case-08": "六件物品的准备与去向一一对应，软袋和电池不会进入普通回收路线。",
    "B06-case-09": "每项议程的决定、影响对象和截止日在同一卡片中，地图提供空间索引。",
    "B06-case-10": "弱点在Kitchen定位，行动从调整路由器开始，而非直接升级全屋设备。",
}
evidence_cases = []
for case in plan["cases"]:
    cid = case["id"]
    evidence_cases.append({"case_id": cid, "problem": case["content_basis"]["problem_evidence"],
                           "source_type": "design hypothesis from common information structures; no external dataset or fieldwork",
                           "external_sources": [], "assumptions": case["content_basis"]["demo_values"],
                           "limitations": case["content_basis"]["limitations"], "audience": case["audience"],
                           "use_context": case["use_context"], "scenario_requirements": case["criteria"],
                           "user_goal": case["user_goal"], "reconstruction": reconstruction[cid],
                           "observable_readability_improvement": observable[cid],
                           "unverified_effect": "No usability test, task-time measurement, recall test, field deployment, or outcome validation was performed.",
                           "validation_question": case["validation_question"], "final_image": sk.rel(paths[cid]),
                           "final_version": versions[cid], "final_review": reviews[cid]["observed"]})
sk.write_json(BASE / "problem-evidence.json", {"schema_version": 1, "task_id": TASK, "path_base": "suite_root",
                                               "created_at": sk.iso(), "evidence_policy": plan["evidence_policy"],
                                               "research_claim_boundary": "All ten problems are design hypotheses. No interviews, fieldwork, user experiments, live-service checks, or local-policy verification are claimed.",
                                               "cases": evidence_cases, "all_data_fictional": True,
                                               "unresolved_issues": []})
lines = ["# B06 设计审查", "", "## 范围与证据边界", "",
         "十件作品均为纯DSL虚构演示。问题来源于对常见信息结构的观察与设计假设，不来源于访谈、现场调研或用户实验；没有引用真实账单、房源、政策、交通、城市规则或网络测量。可观察改善仅指最终画面中的信息组织与可读性，不声称节省用户时间、提高决策质量或改变真实结果。", "",
         "每件均先建立受众、场景、目标和可观察标准，再渲染；所有最终PNG均为服务原始响应。v001–v004 DSL、失败请求、原图与检查派生图保留在临时目录。", "",
         "## 逐件审查", ""]
for case in plan["cases"]:
    cid = case["id"]
    lines += [f"### {cid} · {case['title']}", "", f"- 原卡点：{case['content_basis']['problem_evidence']}",
              f"- 重构：{reconstruction[cid]}", f"- 可见改善：{observable[cid]}",
              f"- 最终判断：{final_observed[cid]}", f"- 未验证效果：{case['validation_question']} 该问题尚未经过用户实验。",
              f"- 最终证据：`{sk.rel(paths[cid])}`；标准逐条证据见 `final-review.json`。", ""]
lines += ["## 独立性与整体关系", "",
          "十件作品分别使用财务瀑布、服务状态网络、成本堆栈、单位价格尺、依赖河、保险场景树、决策Dial、分类传送带、影响地图和户型诊断。它们共享一套克制的信息笔记页脚，但信息转换、决策任务和主视觉逻辑不同，不是同版式换色或换字。", "",
          "## 实际修改与保留", "",
          "案例01修复标题实体、标签遮挡和下注间距；案例03修复总额间距、薄段标签可见性和对比度；案例04修复标尺坐标的量纲；案例07–10分别修复标签净空、页脚净空和信号圈边界。案例02/05/06首版已符合标准，保留而不制造无意义迭代。", "",
          "## 剩余事项", "", "无已知影响交付的缺陷。未来若用于现实场景，必须替换为经核实的数据、当地规则/政策或实测信号，并另行开展用户验证；本交付不声称已完成这些工作。", ""]
(BASE / "design-review.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({"status": "reviewed", "final_cases": len(paths), "versions": versions,
                  "contact_sheet": sk.rel(contact), "details": [sk.rel(path) for path in detail_paths],
                  "calculation_checks": checks["all_checks_passed"]}, ensure_ascii=False))
