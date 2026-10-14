import json
from pathlib import Path

OUTPUT_DIR = Path('outputs/20261011-suite/B01')
TEMP_DIR = Path('tmp/20261011-suite/B01')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

cases = [
    {
        "id": "case-01",
        "title": "科技产品发布会海报",
        "size": [1080, 1350],
        "desc": "新品发布，吸引媒体与用户关注",
        "content": {
            "brand": "NovaTech",
            "product": "Quantum X1",
            "date": "2026.11.15",
            "venue": "上海科技中心",
            "slogan": "重新定义智能边界"
        }
    },
    {
        "id": "case-02",
        "title": "数据可视化仪表盘",
        "size": [1920, 1080],
        "desc": "实时业务数据监控",
        "content": {
            "brand": "DataFlow",
            "kpis": [("总收入", "¥2.8M"), ("订单", "12,450"), ("用户", "89K")],
            "chart": "月度趋势"
        }
    },
    {
        "id": "case-03",
        "title": "活动日程卡片",
        "size": [1200, 800],
        "desc": "会议日程安排一目了然",
        "content": {
            "brand": "TechSummit",
            "date": "2026.11.07",
            "sessions": ["09:00 开场", "10:30 主题演讲", "14:00 圆桌讨论"]
        }
    },
    {
        "id": "case-04",
        "title": "品牌标识系统",
        "size": [1000, 1000],
        "desc": "完整的品牌视觉识别",
        "content": {
            "brand": "Bloom",
            "tagline": "自然与科技的融合",
            "colors": ["#10B981", "#3B82F6", "#F59E0B"]
        }
    },
    {
        "id": "case-05",
        "title": "电商产品详情页",
        "size": [800, 1200],
        "desc": "产品展示与购买引导",
        "content": {
            "brand": "StyleHub",
            "product": "极简双肩包",
            "price": "¥399",
            "features": ["防水", "大容量", "人体工学"]
        }
    },
    {
        "id": "case-06",
        "title": "音乐活动海报",
        "size": [1080, 1350],
        "desc": "音乐节宣传吸引观众",
        "content": {
            "brand": "SoundWave",
            "artists": ["林川", "苏言", "周禾"],
            "date": "2026.12.01",
            "venue": "Live House"
        }
    },
    {
        "id": "case-07",
        "title": "房地产信息图",
        "size": [1200, 900],
        "desc": "楼盘信息与周边配套",
        "content": {
            "brand": "GreenLiving",
            "price": "¥15,000/㎡",
            "features": ["地铁", "学区", "公园"]
        }
    },
    {
        "id": "case-08",
        "title": "餐厅菜单卡片",
        "size": [800, 600],
        "desc": "精致菜单展示",
        "content": {
            "brand": "TasteLab",
            "dishes": ["招牌沙拉 ¥58", "牛排 ¥128", "甜点 ¥38"]
        }
    },
    {
        "id": "case-09",
        "title": "健身追踪报告",
        "size": [600, 800],
        "desc": "每周运动数据总结",
        "content": {
            "brand": "FitTrack",
            "stats": [("步数", "45,230"), ("卡路里", "2,850"), ("距离", "32km")]
        }
    },
    {
        "id": "case-10",
        "title": "旅行目的地指南",
        "size": [1080, 1350],
        "desc": "旅游攻略与景点推荐",
        "content": {
            "brand": "Wanderlust",
            "destination": "云南大理",
            "attractions": ["洱海", "古城", "苍山"]
        }
    }
]

for case in cases:
    cid = case["id"]
    title = case["title"]
    w, h = case["size"]
    content = case["content"]
    desc = case["desc"]

    dsl_parts = []
    dsl_parts.append(f'<Snapshot type="png" width="{w}" height="{h}" background="#0F172A">')
    dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{h}" width="{w}">')

    # Header
    dsl_parts.append(f'    <Container height="120" padding="(40,40)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{content.get("brand", "Brand")}" color="#FFFFFF" fontSize="40" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="{desc}" color="#94A3B8" fontSize="20"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Content
    dsl_parts.append(f'    <Container height="{h-240}" padding="(40,40)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')

    if "product" in content:
        dsl_parts.append(f'        <Text text="{content["product"]}" color="#FFFFFF" fontSize="36" fontStyle="BOLD"/>')
    if "slogan" in content:
        dsl_parts.append(f'        <Text text="{content["slogan"]}" color="#3B82F6" fontSize="24"/>')
    if "date" in content:
        dsl_parts.append(f'        <Text text="{content["date"]}" color="#CBD5E1" fontSize="24"/>')
    if "venue" in content:
        dsl_parts.append(f'        <Text text="{content["venue"]}" color="#CBD5E1" fontSize="24"/>')
    if "price" in content:
        dsl_parts.append(f'        <Text text="{content["price"]}" color="#F59E0B" fontSize="48" fontStyle="BOLD"/>')
    if "features" in content:
        for f in content["features"]:
            dsl_parts.append(f'        <Text text="• {f}" color="#FFFFFF" fontSize="20"/>')
    if "kpis" in content:
        for label, value in content["kpis"]:
            dsl_parts.append(f'        <Text text="{label}：{value}" color="#FFFFFF" fontSize="24"/>')
    if "sessions" in content:
        for s in content["sessions"]:
            dsl_parts.append(f'        <Text text="{s}" color="#FFFFFF" fontSize="22"/>')
    if "artists" in content:
        for a in content["artists"]:
            dsl_parts.append(f'        <Text text="{a}" color="#F59E0B" fontSize="28" fontStyle="BOLD"/>')
    if "dishes" in content:
        for d in content["dishes"]:
            dsl_parts.append(f'        <Text text="{d}" color="#FFFFFF" fontSize="22"/>')
    if "stats" in content:
        for label, value in content["stats"]:
            dsl_parts.append(f'        <Text text="{label}：{value}" color="#10B981" fontSize="24"/>')
    if "attractions" in content:
        for a in content["attractions"]:
            dsl_parts.append(f'        <Text text="• {a}" color="#FFFFFF" fontSize="22"/>')
    if "tagline" in content:
        dsl_parts.append(f'        <Text text="{content["tagline"]}" color="#10B981" fontSize="24"/>')
    if "destination" in content:
        dsl_parts.append(f'        <Text text="{content["destination"]}" color="#F59E0B" fontSize="32" fontStyle="BOLD"/>')

    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    dsl_parts.append('  </Column>')
    dsl_parts.append('</Snapshot>')

    dsl = '\n'.join(dsl_parts)

    # Create case directory
    case_dir = OUTPUT_DIR / cid
    case_dir.mkdir(parents=True, exist_ok=True)
    temp_case_dir = TEMP_DIR / cid
    temp_case_dir.mkdir(parents=True, exist_ok=True)

    # Save DSL
    with open(temp_case_dir / 'final.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)

    # Save case.md
    case_md = f"""# {title}

## 场景
{desc}

## 受众
真实用户

## 视觉选择
深色背景，强调色突出关键信息

## 内容
{json.dumps(content, ensure_ascii=False, indent=2)}
"""
    with open(case_dir / 'case.md', 'w', encoding='utf-8') as f:
        f.write(case_md)

print(f"Generated {len(cases)} B01 cases")

# Save portfolio.json
portfolio = {
    "schema_version": 1,
    "task_id": "B01",
    "path_base": "output_dir",
    "cases": [{"id": c["id"], "title": c["title"], "size": c["size"]} for c in cases]
}
with open(OUTPUT_DIR / 'portfolio.json', 'w', encoding='utf-8') as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)
print("Saved portfolio.json")
