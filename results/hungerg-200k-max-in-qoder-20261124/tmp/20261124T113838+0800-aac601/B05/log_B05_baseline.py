from __future__ import annotations
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk
run = sk.init_suite()[0]
plan = json.loads((BASE / "plan-v002.json").read_text(encoding="utf-8"))
observed = {
    "B05-case-01": "五种药品完整显示在识别列表，但照片区域五个标签被截断为Amlodi/Metfor等；确认、过敏与免责声明可见。",
    "B05-case-02": "三栏来源、更新时间与两处差异清楚；Metformin 32/40片与Atorvastatin停用状态一致，未自动覆盖。",
    "B05-case-03": "三角色权限、不可修改处方和确认记录可读；关系卡片之间没有连接线，关系图概念表达偏弱。",
    "B05-case-04": "08:00三项药品与两个主操作可读；Omeprazole图标为胶囊但记录为1片，演示剂型需统一。",
    "B05-case-05": "09:40家属报告、不自动补服/加倍、联系药师和同步摘要完整，没有医疗判断。",
    "B05-case-06": "五种库存、每日次数和天数计算正确，20天进入14天阈值；但32→40片的盘点变化未解释。",
    "B05-case-07": "交接三方责任、时间线、停用提醒暂停与确认按钮可读；Atorvastatin待确认状态安全。",
    "B05-case-08": "五种药品、过敏、09:40异常、两个问题、24小时分享与撤回可见；Atorvastatin仍显示每日21:00，需改为停用待确认。",
    "B05-case-09": "演示凭证码、40片备妥、标签待药师核对与不更改服用方式完整；非真实交易声明清楚。",
    "B05-case-10": "三件例外与周时间线可读，负责人和来源可追溯；没有健康评分，时间范围一致。",
}
for case in plan["cases"]:
    cid = case["id"]
    path = BASE / "versions" / f"{cid}-v001" / "final-01.png"
    ck.record_view("B05", case, path, "v001", observed[cid], "首次渲染后实际查看；问题件保留v001并另版修正。", "基线", True, "baseline")
ck.log_tool("B05", "direct visual review", "逐张打开十张服务原图，核对文字、边界、状态与跨屏数据", [sk.rel(BASE / "versions" / f'{c["id"]}-v001' / "final-01.png") for c in plan["cases"]], [], [c["id"] for c in plan["cases"]], "十张基线已查看；五件需一致性或表达修正")
print("baseline views recorded: 10")
