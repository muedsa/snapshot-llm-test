from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B01"
TEMP = ROOT / "tmp/20261124T113838+0800-aac601" / TASK

OBSERVED = {
    "case-01": "完整查看1080×1440原图：主题、英文副题、展期、开放时间、地点、票价与预约按钮齐全；橙色日轮、拱门和轨道均在安全区，未裁切或遮挡文字。",
    "case-02": "完整查看1600×1000原图：九个街区温度、38.1°C西岸热斑、12%树冠率、+4.3°C均值差与三项行动一致；图例、地图和右侧面板无重叠。热斑颜色按31–38°C五档映射，属演示数据。",
    "case-03": "完整查看1200×1200原图：收入12400、支出9760、结余2640、储蓄率21.3%及五类金额准确，横条按4200最大值比例绘制。v001发现本周可支配额错误，v002修正为(2640−240)/4=600。",
    "case-04": "完整查看1080×1440原图：两人份、六类食材与0–20分钟四步顺序完整；圆盘位于正文安全区之外，步骤编号、时间和操作说明无遮挡。",
    "case-05": "完整查看1600×1000原图：蓝、橙、绿三条线路、中央/绿线换乘、机场快线服务时间与三个方案完整。v002将运营时间分为两行，中央与中央换乘标签移到线路下方，博物馆标签不再重叠。",
    "case-06": "完整查看1200×1200原图：艺人、专辑名、六首曲目、STEREO/06 TRACKS/2026完整；唱片圆、斜切标签与文字分区清楚，未遮挡标题或曲目。",
    "case-07": "完整查看1600×1000原图：当前位置、出口A/B、两条连续绿色路线、集合点、集合步骤与禁乘电梯规则完整；路线位于主走廊并连接两个出口，房间标签可读，已声明为演示示意。",
    "case-08": "完整查看1600×1000原图：水星/金星/地球/火星顺序及88/225/365/687天正确，明确标注非真实比例。v001比较符号被显示为字面实体，v002使用全角小于号后正确显示。",
    "case-09": "完整查看1080×1440原图：六种蔬菜的价格、单位、现货/剩3斤/售罄状态、时间、布袋优惠与演示声明完整；价格列对齐，状态标签未遮盖品名。",
    "case-10": "完整查看1080×1440原图：日期、时间地点、三条议题、四个时段、讲者、票价与报名入口完整；三列网格对齐，长讲者名与议题未截断，非真实售票声明清楚。",
}

ISSUES = {
    "case-03": "本周可支配额显示¥660，与(2640−240)/4=600不符。",
    "case-05": "右上运营时间截断；中央、博物馆与中央换乘标签互相重叠。",
    "case-08": "读图方法中的小于号显示为字面“&lt;”。",
}


def contact() -> None:
    images = []
    for index in range(1, 11):
        case_id = f"case-{index:02d}"
        version = "v002" if case_id in ISSUES else "v001"
        images.append((case_id, TEMP / "versions" / f"{case_id}-{version}" / "final-01.png"))
    print(sk.rel(ck.contact_sheet(TASK, images, "final-contact-sheet.png")))


def reviews() -> None:
    review_cases = {}
    for index in range(1, 11):
        case_id = f"case-{index:02d}"
        case = next(item for item in json.loads((TEMP / "plan-v001.json").read_text(encoding="utf-8"))["cases"] if item["id"] == case_id)
        v1 = TEMP / "versions" / f"{case_id}-v001" / "final-01.png"
        issue = ISSUES.get(case_id)
        if issue:
            ck.record_view(TASK, case, v1, "v001", issue, "尚未修改；保留v001作为问题证据。", "已实际打开完整v001并定位问题。", False, "baseline")
            v2 = TEMP / "versions" / f"{case_id}-v002" / "final-01.png"
            ck.record_view(TASK, case, v2, "v002", "修正后未发现影响交付的缺陷。", "按v001实际问题修正，未改变预置验收标准。", "再次打开完整v002，与v001逐项比较。", True, "visual")
            version, final_image = "v002", v2
        else:
            ck.record_view(TASK, case, v1, "v001", "未发现影响交付的缺陷。", "首轮合格，不制造无意义迭代。", "已实际打开完整v001并核对内容、几何与目标尺寸可读性。", True, "baseline")
            version, final_image = "v001", v1
        review_cases[case_id] = {"passed": True, "version": version, "image": sk.rel(final_image), "viewed_at": sk.iso(), "observed": OBSERVED[case_id]}
    sheet = TEMP / "inspection" / "final-contact-sheet.png"
    ck.record_view(TASK, {"id": "collection"}, sheet, "final", "十件横竖方版构图具有明确媒介差异，未发现仅换色/换字的版式复用；三件修正已进入最终集合。", "无。", "接触表作为整体预览，不替代此前十张最终服务原图的逐件查看。", True, "baseline")
    review = {"completed": True, "reviewed_at": sk.iso(), "contact_sheet": sk.rel(sheet), "cases": review_cases}
    sk.write_json(TEMP / "final-review.json", review)
    ck.log_tool(TASK, "Python direct visual review", "记录十张最终原图、三张修正图和接触表的真实查看结论", [sk.rel(TEMP / "final-review.json")], [], list(OBSERVED) + ["collection"], "13次逐件查看与1次整体查看均已记录")
    print(sk.rel(TEMP / "final-review.json"))


if __name__ == "__main__":
    {"contact": contact, "reviews": reviews}[sys.argv[1]]()
