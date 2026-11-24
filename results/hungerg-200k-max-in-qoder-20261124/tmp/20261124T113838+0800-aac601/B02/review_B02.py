from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B02"
TEMP = ROOT / "tmp/20261124T113838+0800-aac601" / TASK
OBSERVED = {
    "case-01": "完整查看1080×1440海报：项目名、活动时间地点、四类维修、免费诊断与预约规则完整；巨型环形符号和底部信息不重叠。",
    "case-02": "完整查看1200×1600服务菜单：四类服务、示例、收费/时长和不接范围完整；编号、标题、说明与箭头逐行对齐。",
    "case-03": "完整查看1200×900凭证：预约号A017、日期时段、物品、维修师、地点与迟到规则完整；示意识别码与双栏信息无裁切。",
    "case-04": "完整查看720×1280手机提醒：今天10:30预约、携带物、签到、改期和地址完整。v001“明天见”与当天提醒矛盾，v002改为“一会儿见”并复查。",
    "case-05": "完整查看900×1200排队票：A017、当前A013、约20分钟和三条等待规则完整；票根孔位与内容分区正确。",
    "case-06": "完整查看1080×720会员卡：会员姓名、编号、有效期、三项权益和项目标识完整；横卡左右分区无遮挡。",
    "case-07": "完整查看1600×1000排班：四个时段、四岗位、志愿者、班次要点和14:00空档完整；网格与时间标签对齐，岗位色一致。",
    "case-08": "完整查看1600×1000库存：六类库存比例、阈值状态与补货量一致。v002补齐自行车内胎13件，并把规则改为“不高于上限35%”以匹配判定。",
    "case-09": "完整查看1600×1000影响报告：286件、412小时、1.8吨估算、68%现场修好及12个月数据完整；v002月度值之和精确等于286，柱高按数值比例。",
    "case-10": "完整查看1080×1350筹款海报：8640/12000元、72%进度、三项用途和捐赠行动完整；比例条和数字一致。",
}
ISSUES = {
    "case-04": "当天到店提醒的消息正文误写“明天见”，与今天10:30预约矛盾。",
    "case-08": "优先补货漏列自行车内胎13件；规则写“低于35%”但代码与图中35%也标为需补货。",
    "case-09": "仅展示六个月且合计150件，与年度286件缺乏完整对应。",
}


def contact() -> None:
    images = []
    for i in range(1, 11):
        cid = f"case-{i:02d}"
        version = "v002" if cid in ISSUES else "v001"
        images.append((cid, TEMP / "versions" / f"{cid}-{version}" / "final-01.png"))
    print(sk.rel(ck.contact_sheet(TASK, images, "final-contact-sheet.png")))


def reviews() -> None:
    plan = json.loads((TEMP / "plan-v001.json").read_text(encoding="utf-8"))
    result = {}
    for case in plan["cases"]:
        cid = case["id"]
        v1 = TEMP / "versions" / f"{cid}-v001" / "final-01.png"
        if cid in ISSUES:
            ck.record_view(TASK, case, v1, "v001", ISSUES[cid], "保留v001问题证据，尚未修改。", "实际打开完整v1并定位内容一致性/数据对应问题。", False, "baseline")
            v2 = TEMP / "versions" / f"{cid}-v002" / "final-01.png"
            ck.record_view(TASK, case, v2, "v002", "修正后未发现影响交付的缺陷。", "修正文案或补齐数据，未改变验收标准。", "再次打开完整v2并与v1比较。", True, "visual")
            version, image = "v002", v2
        else:
            ck.record_view(TASK, case, v1, "v001", "未发现影响交付的缺陷。", "首轮合格，不制造无意义迭代。", "实际打开完整v1并核对内容、系统规则、几何与可读性。", True, "baseline")
            version, image = "v001", v1
        result[cid] = {"passed": True, "version": version, "image": sk.rel(image), "viewed_at": sk.iso(), "observed": OBSERVED[cid]}
    sheet = TEMP / "inspection" / "final-contact-sheet.png"
    ck.record_view(TASK, {"id": "collection"}, sheet, "final", "十种触点共享品牌色彩、页眉和圆角规则，同时呈现海报、目录、凭证、手机消息、票根、会员卡、网格与数据板等不同媒介；复用组件在密度与比例变化下仍可读。", "无。", "接触表用于整体生态比较，不替代十张最终服务原图的逐件查看。", True, "baseline")
    sk.write_json(TEMP / "final-review.json", {"completed": True, "reviewed_at": sk.iso(), "contact_sheet": sk.rel(sheet), "cases": result})
    ck.log_tool(TASK, "Python direct visual review", "记录十张最终原图、三张修正图和接触表的真实查看结论", [sk.rel(TEMP / "final-review.json")], [], list(OBSERVED) + ["collection"], "13次逐件查看与1次整体查看均已记录")
    print(sk.rel(TEMP / "final-review.json"))


if __name__ == "__main__":
    {"contact": contact, "reviews": reviews}[sys.argv[1]]()
