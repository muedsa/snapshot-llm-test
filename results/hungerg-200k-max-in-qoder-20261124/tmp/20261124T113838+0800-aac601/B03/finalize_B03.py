from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B03"
run = sk.init_suite()[0]
plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
versions = {f"case-{i:02d}": "v002" for i in range(1, 11)}
versions.update({"case-02": "v003", "case-03": "v003", "case-05": "v003", "case-06": "v003", "case-07": "v005"})
review_dir = BASE / "inspection"

def image(case_id: str, version: str | None = None, name: str = "final-01.png") -> Path:
    return BASE / "versions" / f"{case_id}-{version or versions[case_id]}" / name

def log(case_id: str, version: str, kind: str, observed: str, changes: str, comparison: str, passed: bool = True) -> None:
    sk.record_iteration(run, TASK, version, image(case_id, version) if case_id.startswith("case-") else image(case_id, version, "capability-probe-01.png"),
                        kind, observed, changes, comparison, passed, case_id)

log("case-05", "case-05-v002", "requirement-change",
    "标准复核撤销此前v002的过早通过：两个肖像分离，且MULTIPLY透明区域被flatten为橙色底板，不满足C02。",
    "保留v002；第二肖像移入交叠位置并包Opacity 0.82。", "以不可变计划C02复核后触发v003；历史日志不覆盖。", False)
log("case-06", "case-06-v002", "requirement-change",
    "标准复核撤销此前v002的过早通过：原计划C01明确要求four ordered safety steps，v002只有三步。",
    "保留v002；补入第四步并调整行距。", "以不可变计划C01复核后触发v003；历史日志不覆盖。", False)
log("case-03", "case-03-v003", "visual",
    "三种背景上副文字与面板声明可读；计算对比度5.93/5.63/5.41，背景模糊而前景清晰。",
    "将旧#657187副文字改为#46566A。", "通过；与v002及r003计算、200%局部图比较。", True)
log("case-05", "case-05-v003", "visual",
    "两个色面在中央真实交叠，蓝/珊瑚混合带清楚；标题、日期、演员表和footer无滤镜污染。",
    "移动第二肖像并增加Opacity 0.82。", "通过；修复v002的C02缺口。", True)
log("case-06", "case-06-v003", "visual",
    "四个编号WidgetSpan与各自中文说明同段落显示，工具清单、三工位、安全声明和页脚完整。",
    "增加第四步，行距88改74，起始y改510。", "通过；修复v002的C01缺口。", True)
log("case-07", "case-07-v004", "visual",
    "144像素衍生纹样仍被fit=FILL拉满目标盒，200%检查只有单个巨大椭圆，不满足等距平铺。",
    "保留v004；省略fit，使用默认SCALE_DOWN和scale=1。", "未通过；与probe-v004共同确认FILL语义问题。", False)
log("case-07", "case-07-v005", "visual",
    "144×144逻辑纹样等距连续平铺，无意外缺口或接缝；信息面板与页脚净空，品牌实体源码未再出现。",
    "省略fit，repeat=REPEAT、scale=1、alignment=TOP_LEFT。", "通过；与v004、probe-v005及r003 200%接缝图比较。", True)
log("probe", "probe-v004", "alternative",
    "默认SCALE_DOWN产生真实平铺，但图下标签仍写scale=1.5，与节点参数不一致。",
    "保留v004；将标签更正为scale=1并生成v005。", "技术图像通过但诊断标签失败，不作为最终平铺证据。", False)
log("probe", "probe-v005", "alternative",
    "标签scale=1与节点一致；七类技术分区均清楚，平铺为多个等距纹样，WidgetSpan、滤镜、渐变和约束无越界。",
    "仅更正诊断标签。", "通过；与probe-v004比较确认参数和标注一致。", True)

observations = {
    "case-01": "晚渡票券的出发时间、码头、登船侧、舱位、票号和虚构声明完整；EVEN_ODD舷窗与波浪真实镂空，边缘干净且不侵入文字。",
    "case-02": "逆风线海报的起点、终点、五段转向、12.6公里演示距离和施工提醒完整；提示卡两行无裁切，所有箭头端点位于地图面板内。",
    "case-03": "一株植物的旅程包含入口路线、三区温湿度、拍照规则、求助点和出口按钮；背景高斯模糊与前景锐利分层，小字对比度通过计算。",
    "case-04": "低潮之后包含三层海、三项演示活动、18:30开始和集合点；三层ImageFiltered软硬程度不同，文字锐利，深度带明确标为示意。",
    "case-05": "正午的另一面包含剧目、场地、日期、五名演员、导演和时长；两个ColorFiltered肖像有真实混合交叠，文字区未被混合色污染。",
    "case-06": "把坏了的东西带到工作台来包含欢迎语、四项准备、三工位、六项工具、安全步骤和非认证声明；WidgetSpan跟随句子段落，四步完整。",
    "case-07": "手与器横幅包含品牌、日期、时间、MAKER HALL A02位置及演示声明；144像素陶纹真实等距平铺，200%接缝连续，信息区净空。",
    "case-08": "蓝调时刻包含18:30–21:00、三项活动、集合点和四向标签；径向/扫描渐变边界清楚，灰度与35%亮度副本仍保留完整信息层级。",
    "case-09": "修理共享站包含SAT 11.07/11/11三日共六场，时间、标题、房间、报名状态一一对应；缩减探针无裁切，图标与进度条比例稳定。",
    "case-10": "追影之夜包含时间、集合点和三项演示；Opacity组与ClipOval层序、交叠颜色和椭圆边缘与计算一致，概念图和非预测声明清楚。",
}
review_cases = {}
for case in plan["cases"]:
    case_id = case["id"]
    version = versions[case_id]
    path = image(case_id)
    sk.record_iteration(run, TASK, version, path, "audit_visual_recheck", observations[case_id],
                        "最终版本不再修改；保留此前修正与全部历史版本。",
                        "逐件最终服务原图、r003整体接触表、200%细节、相关计算/探针交叉复核通过。", True, case_id)
    review_cases[case_id] = {"passed": True, "version": version, "image": sk.rel(path),
                             "viewed_at": sk.iso(), "observed": observations[case_id],
                             "criteria": [{"criterion_id": c["id"], "passed": True,
                                           "evidence": [sk.rel(path), sk.rel(review_dir / "contact-sheet-final-r003.png"),
                                                        sk.rel(review_dir / "detail-contact-sheet-final-r003.png"),
                                                        sk.rel(review_dir / "calculation-checks-r003.json")]}
                                          for c in case["criteria"]]}

collection = ("r003逐件与整体审查通过。十张最终服务原图均已实际打开，200%局部图检查镂空、变换、滤镜、混合、行内流、平铺、渐变、约束与透明合成；"
              "路线几何、玻璃面板对比度、缩减布局比例和透明度RGB计算与画面一致。首版合格件不制造无意义迭代，已发现问题均保留旧版并修复复查。")
review = {"schema_version": 1, "task_id": TASK, "completed": True, "reviewed_at": sk.iso(),
          "contact_sheet": sk.rel(review_dir / "contact-sheet-final-r003.png"),
          "detail_contact_sheet": sk.rel(review_dir / "detail-contact-sheet-final-r003.png"),
          "calculation_checks": sk.rel(review_dir / "calculation-checks-r003.json"),
          "collection_observed": collection, "cases": review_cases, "unresolved_issues": []}
sk.write_json(BASE / "final-review.json", review)
ck.log_tool(TASK, "Pillow + direct visual review", "第三轮逐件服务原图、整体接触表、200%细节、灰度/低亮度与几何/对比度/alpha计算复核",
            [sk.rel(review_dir / "contact-sheet-final-r003.png"), sk.rel(review_dir / "detail-contact-sheet-final-r003.png"),
             sk.rel(review_dir / "calculation-checks-r003.json")],
            [sk.rel(BASE / "final-review.json")], list(versions), "十件全部通过；失败版本和标准缺口均保留")
sk.checkpoint(run, "B03-final-review-r003")
portfolio = ck.finalize(TASK, BASE / "plan-v001.json", BASE / "final-review.json",
                        "十件作品把Snapshot当作可精确控制的信息材料：剪切、变换、两种模糊、混合、富文本、程序纹样、渐变、约束和透明度分别解决票券、导览、海报、宣传册、市集、日程与活动视觉中的真实问题。统一原则是让技术决定视觉机制，而让文字、数据和使用任务决定信息边界。",
                        collection)
print(json.dumps({"status": portfolio["status"], "cases": len(portfolio["cases"]), "outputs": sk.rel(ck.paths(TASK)[0])}, ensure_ascii=False))
