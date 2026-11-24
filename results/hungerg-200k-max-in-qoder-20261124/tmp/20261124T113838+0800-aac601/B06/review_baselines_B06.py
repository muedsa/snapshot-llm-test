from __future__ import annotations
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
_, temp = ck.paths("B06")
observations = {
    "B06-case-01": "瀑布加法与三个行动问题可读；发现标题中的撇号被渲染成&#x27;，+$3和+$1标签被顶部摘要卡遮挡，右下总计边界也需扩大。首版不通过。",
    "B06-case-02": "先回答YES，再显示替代巴士、Market换乘和保留列车；闭合段、站点、+12分钟演示标记与三步说明均清楚，线路不穿字。首版符合标准。",
    "B06-case-03": "三组总额和一次性费用算术正确；发现$1,810与顶部说明距离过近，A/C的Parking薄段标签相互拥挤，50%视图不利。首版不通过。",
    "B06-case-04": "两包装价格、单位价和现金差额正确；发现标尺的A/B圆点被错误放在$2附近，而应在$6.00和$6.60；副标题末行仅剩expiry。首版不通过。",
    "B06-case-05": "START HERE明确指向Outline，四项依赖、权重20/30/10/40、工时3/6/2/5及截止日均可读，总计100%与16小时一致。首版符合标准。",
    "B06-case-06": "事件、Section 4、渐进渗漏排除项、三类证明和‘需理算员审查’边界完整；没有声称赔付或拒赔，连线可追踪。首版符合标准。",
    "B06-case-07": "维修$55/年和更换$97.50/年计算正确；发现 REPLACE 标签及算式与顶部保修免责声明在同一水平带重叠。首版不通过。",
    "B06-case-08": "六件物品的准备动作和去向完整，软袋与电池明确特殊投递；发现底部SORTING LOGIC与页脚线过近，需增加净空。首版不通过。",
    "B06-case-09": "四项议程在地图与列表间有颜色连接，受影响人群、决定和评论截止日完整；发现底部参与说明卡下沿压到页脚线。首版不通过。",
    "B06-case-10": "三个房间dBm读数、测试位置和三步诊断清楚；发现两层信号圈越过Living room房间边界，图示范围与房间墙线关系不准确。首版不通过。",
}
existing = sk.read_jsonl(temp / "iterations.jsonl")
recorded = []
for case in plan["cases"]:
    cid = case["id"]
    if any(e.get("case_id") == cid and e.get("version_id") == f"{cid}-v001"
           and e.get("observed") == observations[cid] for e in existing):
        continue
    path = temp / "versions" / f"{cid}-v001" / "final-01.png"
    passed = cid in {"B06-case-02", "B06-case-05", "B06-case-06"}
    iteration_id = ck.record_view("B06", case, path, "v001", observations[cid],
                                  "保留首版" if passed else "记录真实缺陷，下一步另存v002修正，不覆盖v001。",
                                  "逐张打开服务原图，对照v001预渲染标准；未使用接触表替代原图检查。",
                                  passed, "baseline")
    recorded.append(iteration_id)
print(json.dumps({"recorded_baseline_views": recorded, "passed": 3, "needs_revision": 7}, ensure_ascii=False))
