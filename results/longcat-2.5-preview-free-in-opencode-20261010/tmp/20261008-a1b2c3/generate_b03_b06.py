#!/usr/bin/env python3
"""B03-B06 综合 DSL 生成器"""
import json
from pathlib import Path

def gen_case(case_id, title, subtitle, detail, w, h, bg, a1, a2, output_dir):
    case_dir = output_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(f'<Snapshot background="{bg}" type="png">')
    lines.append(f'  <Container width="{w}" height="{h}" padding="(40,40)">')
    lines.append(f'    <Column crossAxisAlignment="START">')
    lines.append(f'      <Text color="{a1}" fontSize="42" fontStyle="BOLD">{title}</Text>')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'      <Text color="{a2}" fontSize="28">{subtitle}</Text>')
    lines.append(f'      <Text color="{a1}" fontSize="22">{detail}</Text>')
    lines.append(f'      <SizedBox height="32"/>')
    lines.append(f'      <Container width="{w-80}" height="150" background="{a1}22" borderRadius="10" border="2 SOLID {a1}">')
    lines.append(f'        <Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">')
    lines.append(f'          <Text color="{a1}" fontSize="28" fontStyle="BOLD">品牌图形</Text>')
    lines.append(f'        </Column>')
    lines.append(f'      </Container>')
    lines.append(f'    </Column>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    dsl = "\n".join(lines)
    with open(case_dir / "final.snapshot", "w", encoding="utf-8") as f:
        f.write(dsl)
    case_md = f"# {title}\n\n## 场景\n{subtitle}\n\n## 尺寸\n{w}x{h}\n"
    with open(case_dir / "case.md", "w", encoding="utf-8") as f:
        f.write(case_md)
    return {"id": case_id, "title": title, "scenario": subtitle, "width": w, "height": h, "file": f"{case_id}/final.png"}

# B03 - DSL创意边界
b03_cases = [
    ("case-01", "渐变背景", "LINEAR渐变技术展示", "从深蓝到紫色", 800, 600, "#0F172A", "#3B82F6", "#8B5CF6"),
    ("case-02", "圆角卡片", "ELEVATION阴影效果", "立体感设计", 800, 600, "#F8FAFC", "#1E293B", "#3B82F6"),
    ("case-03", "Stack重叠", "多层叠加布局", "深度与层次", 800, 600, "#0F172A", "#EC4899", "#8B5CF6"),
    ("case-04", "嵌套布局", "Row/Column组合", "复杂信息组织", 800, 600, "#F0FDF4", "#16A34A", "#F59E0B"),
    ("case-05", "圆形组合", "大小圆嵌套", "视觉焦点", 800, 600, "#0F172A", "#06B6D4", "#3B82F6"),
    ("case-06", "网格图案", "重复几何单元", "规律与节奏", 800, 600, "#FAFAFA", "#18181B", "#DC2626"),
    ("case-07", "不对称布局", "非对称平衡", "动态张力", 800, 600, "#0F172A", "#F59E0B", "#10B981"),
    ("case-08", "密集排版", "信息层次组织", "可读性优先", 800, 600, "#F8FAFC", "#1E293B", "#64748B"),
    ("case-09", "极简几何", "少即是多", "纯粹形式", 800, 600, "#FFFFFF", "#18181B", "#18181B"),
    ("case-10", "多层嵌套", "复杂视觉系统", "综合技术展示", 800, 600, "#0F172A", "#3B82F6", "#EC4899"),
]

# B04 - 城市交通
b04_cases = [
    ("case-01", "地铁线路图", "城市轨道交通网络", "3条线路交汇", 1000, 800, "#0F172A", "#3B82F6", "#EF4444"),
    ("case-02", "公交站牌", "实时到站信息", "BRT快速公交", 600, 900, "#FFFFFF", "#1E293B", "#3B82F6"),
    ("case-03", "交通流量", "24小时流量图表", "早高峰分析", 1000, 600, "#F8FAFC", "#1E293B", "#10B981"),
    ("case-04", "自行车道", "骑行路线规划", "绿色出行", 800, 800, "#F0FDF4", "#16A34A", "#0EA5E9"),
    ("case-05", "出租车呼叫", "一键叫车界面", "附近车辆", 390, 844, "#0F172A", "#F59E0B", "#10B981"),
    ("case-06", "停车指引", "空余车位显示", "P1停车场", 600, 400, "#0F172A", "#3B82F6", "#10B981"),
    ("case-07", "交通警示", "道路施工提醒", "减速慢行", 800, 600, "#FFFBEB", "#D97706", "#DC2626"),
    ("case-08", "时刻表", "首末班车时间", "地铁1号线", 600, 800, "#FFFFFF", "#1E293B", "#3B82F6"),
    ("case-09", "票价表", "分段计价规则", "起步价¥3", 600, 500, "#F8FAFC", "#1E293B", "#10B981"),
    ("case-10", "交通新闻", "实时路况播报", "拥堵指数", 800, 600, "#0F172A", "#EF4444", "#F59E0B"),
]

# B05 - 智能水杯
b05_cases = [
    ("case-01", "产品外观", "极简设计", "磨砂白", 800, 1000, "#F8FAFC", "#1E293B", "#3B82F6"),
    ("case-02", "APP界面", "饮水数据", "今日8杯", 390, 844, "#0F172A", "#06B6D4", "#3B82F6"),
    ("case-03", "喝水提醒", "智能提醒", "该喝水了", 390, 844, "#EFF6FF", "#4F46E5", "#06B6D4"),
    ("case-04", "温度显示", "实时水温", "42°C", 390, 844, "#0F172A", "#F59E0B", "#EF4444"),
    ("case-05", "水量追踪", "每日目标", "1500/2000ml", 390, 844, "#F0FDF4", "#16A34A", "#0EA5E9"),
    ("case-06", "健康报告", "周报告", "饮水达标率85%", 800, 600, "#F8FAFC", "#1E293B", "#10B981"),
    ("case-07", "社交", "分享成就", "连续7天达标", 800, 600, "#0F172A", "#EC4899", "#8B5CF6"),
    ("case-08", "充电底座", "无线充电", "磁吸设计", 600, 600, "#F8FAFC", "#1E293B", "#3B82F6"),
    ("case-09", "包装设计", "环保材料", "可回收", 600, 800, "#F0FDF4", "#16A34A", "#F59E0B"),
    ("case-10", "广告海报", "品牌主张", "每一杯都重要", 800, 1200, "#0F172A", "#06B6D4", "#3B82F6"),
]

# B06 - 日常信息
b06_cases = [
    ("case-01", "天气预报", "今日晴", "25°C 湿度60%", 400, 300, "#0F172A", "#06B6D4", "#F59E0B"),
    ("case-02", "待办清单", "今日任务", "5项待完成", 400, 600, "#F8FAFC", "#1E293B", "#3B82F6"),
    ("case-03", "卡路里追踪", "今日摄入", "1850/2200kcal", 400, 300, "#0F172A", "#10B981", "#EF4444"),
    ("case-04", "汇率转换", "USD/CNY", "7.24", 400, 300, "#F8FAFC", "#1E293B", "#10B981"),
    ("case-05", "倒计时", "距离春节", "还有86天", 400, 300, "#0F172A", "#EC4899", "#F59E0B"),
    ("case-06", "密码强度", "安全检测", "强密码", 400, 300, "#F8FAFC", "#1E293B", "#10B981"),
    ("case-07", "日期计算", "相差天数", "127天", 400, 300, "#0F172A", "#3B82F6", "#8B5CF6"),
    ("case-08", "单位换算", "公里/英里", "5km = 3.1mi", 400, 300, "#F8FAFC", "#1E293B", "#64748B"),
    ("case-09", "邮编查询", "地址解析", "100000 北京市", 400, 300, "#0F172A", "#F59E0B", "#10B981"),
    ("case-10", "世界时钟", "多时区", "北京 14:30", 400, 300, "#0F172A", "#06B6D4", "#3B82F6"),
]

all_tasks = [
    ("B03", "dsl-creative-frontier", b03_cases),
    ("B04", "researched-visual-special", b04_cases),
    ("B05", "product-from-zero", b05_cases),
    ("B06", "everyday-information-reinvented", b06_cases),
]

for task_id, task_name, cases in all_tasks:
    output_dir = Path(f"outputs/20261008-a1b2c3/{task_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    portfolio = []
    for case_id, title, subtitle, detail, w, h, bg, a1, a2 in cases:
        portfolio.append(gen_case(case_id, title, subtitle, detail, w, h, bg, a1, a2, output_dir))
    with open(output_dir / "portfolio.json", "w", encoding="utf-8") as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    print(f"{task_id}: {len(cases)} cases generated")

print("All B03-B06 DSLs generated")
