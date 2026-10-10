#!/usr/bin/env python3
"""B01 - 十张真实场景的炫酷用例 DSL 生成器"""
import json
from pathlib import Path

output_dir = Path("outputs/20261008-a1b2c3/B01")
output_dir.mkdir(parents=True, exist_ok=True)

# 10个不同场景
cases = [
    {
        "id": "case-01",
        "title": "Neon Pulse 音乐节",
        "scenario": "2026年夏季音乐节宣传海报，吸引年轻观众",
        "width": 1200, "height": 1600,
        "bg": "#0F172A", "accent1": "#EC4899", "accent2": "#8B5CF6",
        "content": ["NEON PULSE", "2026.08.15-17", "上海 · 世博公园", "早鸟票 ¥299"]
    },
    {
        "id": "case-02",
        "title": "DataFlow 数据平台",
        "scenario": "企业级数据可视化平台产品发布",
        "width": 1440, "height": 900,
        "bg": "#0F172A", "accent1": "#3B82F6", "accent2": "#10B981",
        "content": ["DataFlow Analytics", "实时数据 · 智能决策", "企业级解决方案", "免费试用"]
    },
    {
        "id": "case-03",
        "title": "GreenLeaf 有机食品",
        "scenario": "有机食品品牌社交媒体宣传",
        "width": 1080, "height": 1080,
        "bg": "#F0FDF4", "accent1": "#16A34A", "accent2": "#F59E0B",
        "content": ["GreenLeaf", "从农场到餐桌", "100%有机认证", "新鲜直达"]
    },
    {
        "id": "case-04",
        "title": "CodeConf 2026",
        "scenario": "技术大会日程安排与宣传",
        "width": 1200, "height": 1800,
        "bg": "#0F172A", "accent1": "#06B6D4", "accent2": "#F59E0B",
        "content": ["CodeConf 2026", "2026.12.01-03", "北京 · 国家会议中心", "50+技术分享"]
    },
    {
        "id": "case-05",
        "title": "FitTrack 健身",
        "scenario": "健身应用数据追踪界面",
        "width": 390, "height": 844,
        "bg": "#0F172A", "accent1": "#EF4444", "accent2": "#F97316",
        "content": ["FitTrack", "今日运动", "跑步 5.2km", "消耗 320kcal"]
    },
    {
        "id": "case-06",
        "title": "EduLearn 在线课程",
        "scenario": "在线教育平台课程推广",
        "width": 1200, "height": 675,
        "bg": "#EFF6FF", "accent1": "#4F46E5", "accent2": "#06B6D4",
        "content": ["EduLearn", "掌握未来技能", "200+在线课程", "限时5折"]
    },
    {
        "id": "case-07",
        "title": "TravelNest 旅行",
        "scenario": "旅行规划应用目的地推荐",
        "width": 1080, "height": 1350,
        "bg": "#FFF7ED", "accent1": "#EA580C", "accent2": "#0EA5E9",
        "content": ["TravelNest", "探索日本", "东京 · 京都 · 大阪", "7日深度游"]
    },
    {
        "id": "case-08",
        "title": "CryptoWatch 行情",
        "scenario": "加密货币行情监控卡片",
        "width": 800, "height": 600,
        "bg": "#0F172A", "accent1": "#F59E0B", "accent2": "#10B981",
        "content": ["CryptoWatch", "BTC $67,432", "+2.4% 24h", "ETH $3,521"]
    },
    {
        "id": "case-09",
        "title": "ArtSpace 画廊",
        "scenario": "当代艺术展览宣传海报",
        "width": 1080, "height": 1920,
        "bg": "#FAFAFA", "accent1": "#18181B", "accent2": "#DC2626",
        "content": ["ArtSpace", "「之间」当代艺术展", "2026.11.01-30", "免费参观"]
    },
    {
        "id": "case-10",
        "title": "FoodieBox 外卖",
        "scenario": "外卖平台每日推荐卡片",
        "width": 750, "height": 1334,
        "bg": "#FFFBEB", "accent1": "#D97706", "accent2": "#DC2626",
        "content": ["FoodieBox", "今日推荐", "麻辣香锅套餐", "立减15元"]
    }
]

portfolio = []

for case in cases:
    case_dir = output_dir / case["id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    
    w = case["width"]
    h = case["height"]
    bg = case["bg"]
    a1 = case["accent1"]
    a2 = case["accent2"]
    
    lines = []
    lines.append(f'<Snapshot background="{bg}" type="png">')
    lines.append(f'  <Container width="{w}" height="{h}" padding="(48,48)">')
    lines.append(f'    <Column crossAxisAlignment="START">')
    lines.append(f'      <Text color="{a1}" fontSize="48" fontStyle="BOLD">{case["content"][0]}</Text>')
    lines.append(f'      <SizedBox height="24"/>')
    lines.append(f'      <Text color="{a2}" fontSize="32">{case["content"][1]}</Text>')
    lines.append(f'      <Text color="{a1}" fontSize="24">{case["content"][2]}</Text>')
    lines.append(f'      <Text color="{a2}" fontSize="24">{case["content"][3]}</Text>')
    lines.append(f'      <SizedBox height="48"/>')
    lines.append(f'      <Container width="{w-96}" height="200" background="{a1}33" borderRadius="12" border="2 SOLID {a1}">')
    lines.append(f'        <Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">')
    lines.append(f'          <Text color="{a1}" fontSize="36" fontStyle="BOLD">品牌图形</Text>')
    lines.append(f'        </Column>')
    lines.append(f'      </Container>')
    lines.append(f'    </Column>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    
    dsl = "\n".join(lines)
    with open(case_dir / "final.snapshot", "w", encoding="utf-8") as f:
        f.write(dsl)
    
    # 保存case.md
    case_md = f"""# {case['title']}

## 场景
{case['scenario']}

## 尺寸
{w}×{h}

## 内容
{chr(10).join('- ' + c for c in case['content'])}

## 视觉选择
- 主色：{a1}
- 辅色：{a2}
- 背景：{bg}
"""
    with open(case_dir / "case.md", "w", encoding="utf-8") as f:
        f.write(case_md)
    
    portfolio.append({
        "id": case["id"],
        "title": case["title"],
        "scenario": case["scenario"],
        "width": w,
        "height": h,
        "file": f"{case['id']}/final.png"
    })

# 保存portfolio.json
with open(output_dir / "portfolio.json", "w", encoding="utf-8") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)

print(f"Generated {len(cases)} cases")
