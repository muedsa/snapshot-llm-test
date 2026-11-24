from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B04"
run = sk.init_suite()[0]
plan = json.loads((Path(__file__).parent / "plan-v001.json").read_text(encoding="utf-8"))
versions = {f"B04-case-{i:02d}": "v001" for i in range(1, 11)}
versions.update({"B04-case-01": "v002", "B04-case-05": "v002"})
observations = {
"B04-case-01": "区域与街区两种尺度清楚；白天1–7°F、夜晚2–5°F及美国综述限定准确。地图内白色说明文字落在芥末黄底上，对比度不足；等高线、范围标签和页脚完整。",
"B04-case-02": "五条因果路径与中心城市结构完整， conceptual note明确。天气与地理卡片下缘贴近页脚分隔线，压缩底部留白，需要上移。",
"B04-case-03": "表面与空气的观测位置、用途和限制清楚；没有固定换算或虚构数值。上下分区、人物、文字与页脚均完整可读。",
"B04-case-04": "街道剖面、遮阴、蒸散、材料和几何信息完整。蒸散说明写成‘并带热’，与来源含义相反；蓝色箭头穿过该说明文字，需要改字并避让。",
"B04-case-05": "夜间储热释放与暖夜风险表达完整，没有伪造小时曲线。三条放热带及箭头进入右侧说明卡，遮挡卡片边缘和内部留白，需要缩短并避让。",
"B04-case-06": "暴露、可达、脆弱性三类问题区分清楚。两条路线被中央说明卡遮断，无法连续追踪到目的地；右侧来源文字过长。",
"B04-case-07": "96°F、65% RH、121°F准确转录；遮阴轻风、最多约15°F且非固定加值、WBGT与HeatRisk边界均清楚。三组数字、假设卡和页脚无裁剪。",
"B04-case-08": "四种策略的机制、适用场景、维护约束和协同效益逐列对齐；明确不设总分。建筑剖面符号可辨，各列文字无溢出。",
"B04-case-09": "虚构演示标识清楚；五个规划节点连接遮阴、铺装、屋顶、休息和测量。轴线、路线、说明卡和底部问题栏无遮挡。",
"B04-case-10": "六步清单覆盖目标、地点时间、数据类型、协议、元数据和行动；空气与表面限制明确。编号、正文、提醒和来源均完整可读。",
}
for case in plan["cases"]:
    cid = case["id"]
    version = versions[cid]
    image = Path(__file__).parent / "versions" / f"{cid}-{version}" / "final-01.png"
    failed = cid in {"B04-case-01", "B04-case-02", "B04-case-04", "B04-case-05", "B04-case-06"}
    ck.record_view(TASK, case, image, version, observations[cid],
                   "首轮未修改；已确认问题留待v002修复" if failed else "首版满足全部可观察标准，无需制造无意义迭代",
                   "完整查看服务原图后的基线判断", not failed, "baseline")
for cid, version, reason in [
    ("B04-case-01", "v001", "HTTP 400：pill的Container直接包含Positioned，违反Stack父级约束；未取得图片。"),
    ("B04-case-05", "v001", "HTTP 400：gradientBegin使用不支持的LEFT；未取得图片。"),
]:
    case = next(c for c in plan["cases"] if c["id"] == cid)
    ck.record_view(TASK, case, Path(__file__).parent / "versions" / f"{cid}-{version}" / "final.snapshot", version,
                   reason, "v002修正容器子级结构" if cid.endswith("01") else "v002改用CENTER_LEFT/CENTER_RIGHT",
                   "语法修复，不属于视觉迭代", False, "syntax-fix")
ck.log_tool(TASK, "Read image", "逐张完整查看十件真实服务PNG并记录基线观察",
            [f"tmp/{run}/B04/versions/{cid}-{versions[cid]}/final-01.png" for cid in versions],
            [f"tmp/{run}/B04/iterations.jsonl"], list(versions), "十件均已实际查看；五件发现需修复问题")
print(json.dumps({"baseline_views": 10, "syntax_fixes": 2, "needs_revision": 5}))
