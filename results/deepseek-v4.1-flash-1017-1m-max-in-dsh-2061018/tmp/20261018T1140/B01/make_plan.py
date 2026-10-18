import json
from pathlib import Path

run = "20261018T1140"
p = Path(f"tmp/{run}/B01/plan.json")
p.parent.mkdir(parents=True, exist_ok=True)
cases = [
    ("case-01", "夜班交接板", "ICU 夜班护士与接班医生", "病房站 27 寸横屏，03:00 交接", "5 分钟内看清 4 位病人的风险、待办与升级联系人", "自拟演示病例，非真实患者", "深色临床仪表 + 红色风险带"),
    ("case-02", "深时：地质展海报", "自然博物馆公众观众", "地铁灯箱/入口海报，1.5m 观看", "记住展名、时间、地点并愿意进入展厅", "自拟展览；地质年代为科普性演示", "巨型字体 + 地层色带"),
    ("case-03", "社区防洪疏散图", "河畔社区居民", "楼道/社区中心 A2 张贴，紧急时快速阅读", "找到自家分区、最近集合点与安全路线", "自拟社区网格与演练数据", "高对比色块 + 粗路线"),
    ("case-04", "盐与光：书店夜谈", "独立书店读者", "书店橱窗/社交媒体竖版", "知道作者、时间、主题并扫码报名", "自拟书店活动与作者", "衬线大字 + 暖橙纸张"),
    ("case-05", "咖啡批次卡", "精品咖啡烘焙师与门店顾客", "吧台卡片/包装插页，手持阅读", "理解产地、处理法、海拔与烘焙曲线", "自拟批次数据", "数据网格 + 烘焙曲线"),
    ("case-06", "无障碍换乘指南", "轮椅使用者与行动不便乘客", "车站竖版海报/手机长图", "判断电梯、坡道、宽闸机与替代路线", "自拟车站；设施名称为演示", "步骤化路线 + 明确图标"),
    ("case-07", "播种日历", "城市阳台种植者", "种子包装背面/冰箱贴，竖版", "按月份安排 6 种作物的播种/移栽/收获", "自拟温带气候示例", "12 月网格 + 作物色带"),
    ("case-08", "维修咖啡馆排期", "社区居民与志愿者", "社区中心横版海报/群聊图", "知道带什么、去哪桌、几点到", "自拟活动与志愿者", "桌号色块 + 时间轴"),
    ("case-09", "观星夜目标卡", "天文社团与初学者", "打印 A5/手机竖版，红光环境", "在 20:00–23:00 找到 5 个目标", "自拟观测活动；方位为演示", "星图 + 方位环"),
    ("case-10", "气候风险田图", "社区规划者与农户", "工作坊 A3 横版/桌面", "比较热/涝/风风险并选择行动", "自拟区域评分，非官方预警", "风险矩阵 + 行动卡"),
]
plan = {"schema_version": 1, "task_id": "B01", "run_id": run, "version": "plan-v001",
        "created_at": "2026-10-18T14:20:00+08:00", "path_base": "suite_root",
        "scope": "10 independent real-world visual pieces", "asset_policy": "dsl_only", "cases": []}
for cid, title, aud, ctx, goal, basis, vis in cases:
    plan["cases"].append({
        "id": cid, "title": title, "audience": aud, "use_context": ctx, "user_goal": goal,
        "content_basis": basis, "visual_intent": vis, "dimensions": None,
        "criteria": [
            {"id": f"{cid}-C1", "observable": "主标题、关键行动信息在目标尺寸可读", "method": "全图 + 局部查看"},
            {"id": f"{cid}-C2", "observable": "信息层级清楚，无遮挡/裁切/溢出", "method": "全图检查"},
            {"id": f"{cid}-C3", "observable": "内容与场景自洽，数据/单位不矛盾", "method": "对照 case.md 与图中数字"},
            {"id": f"{cid}-C4", "observable": "DSL 自包含，最终 PNG 为真实服务响应", "method": "检查 requests.jsonl 与同名 .snapshot"},
        ],
        "criteria_version": f"{cid}-v1", "criteria_time": "2026-10-18T14:20:00+08:00",
    })
p.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
print("B01 plan", len(plan["cases"]))
