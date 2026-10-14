import json
from pathlib import Path

OUTPUT_DIR = Path('outputs/20261011-suite/B02')
TEMP_DIR = Path('tmp/20261011-suite/B02')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

BRAND = "FitFlow"
TAGLINE = "让运动成为生活"

cases = [
    {"id": "case-01", "title": "品牌主视觉海报", "size": [1080, 1350], "content": {"type": "poster", "text": "FitFlow 健身工作室"}},
    {"id": "case-02", "title": "课程表卡片", "size": [1200, 800], "content": {"type": "schedule", "sessions": ["瑜伽 09:00", "搏击 14:00", "普拉提 19:00"]}},
    {"id": "case-03", "title": "教练介绍页", "size": [800, 1200], "content": {"type": "profile", "coach": "林川", "specialty": "力量训练"}},
    {"id": "case-04", "title": "会员卡设计", "size": [850, 500], "content": {"type": "card", "tier": "年卡会员", "price": "¥2,999"}},
    {"id": "case-05", "title": "社交媒体宣传图", "size": [1080, 1080], "content": {"type": "social", "text": "新用户首月免费"}},
    {"id": "case-06", "title": "营养指南信息图", "size": [800, 1200], "content": {"type": "infographic", "tips": ["蛋白质", "碳水化合物", "水分"]}},
    {"id": "case-07", "title": "活动邀请卡", "size": [1200, 800], "content": {"type": "invite", "event": "开业庆典", "date": "2026.11.07"}},
    {"id": "case-08", "title": "移动端仪表盘", "size": [375, 667], "content": {"type": "dashboard", "stats": [("本周课时", "12"), ("卡路里", "2,850")]}},
    {"id": "case-09", "title": "签到二维码卡片", "size": [600, 400], "content": {"type": "checkin", "text": "扫码签到"}},
    {"id": "case-10", "title": "月度报告封面", "size": [1200, 900], "content": {"type": "report", "month": "2026年10月", "summary": "本月新增会员128人"}},
]

for case in cases:
    cid = case["id"]
    title = case["title"]
    w, h = case["size"]
    content = case["content"]

    dsl_parts = []
    dsl_parts.append(f'<Snapshot type="png" width="{w}" height="{h}" background="#0F172A">')
    dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{h}" width="{w}">')

    # Header
    dsl_parts.append(f'    <Container height="100" padding="(32,32)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{BRAND}" color="#FFFFFF" fontSize="36" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="{TAGLINE}" color="#10B981" fontSize="18"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Content
    dsl_parts.append(f'    <Container height="{h-200}" padding="(32,32)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{title}" color="#FFFFFF" fontSize="28" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <SizedBox height="16"/>')

    if content["type"] == "poster":
        dsl_parts.append(f'        <Text text="{content["text"]}" color="#FFFFFF" fontSize="32" fontStyle="BOLD"/>')
    elif content["type"] == "schedule":
        for s in content["sessions"]:
            dsl_parts.append(f'        <Text text="{s}" color="#FFFFFF" fontSize="22"/>')
    elif content["type"] == "profile":
        dsl_parts.append(f'        <Text text="教练：{content["coach"]}" color="#FFFFFF" fontSize="24"/>')
        dsl_parts.append(f'        <Text text="专长：{content["specialty"]}" color="#10B981" fontSize="20"/>')
    elif content["type"] == "card":
        dsl_parts.append(f'        <Text text="{content["tier"]}" color="#F59E0B" fontSize="28" fontStyle="BOLD"/>')
        dsl_parts.append(f'        <Text text="{content["price"]}" color="#FFFFFF" fontSize="24"/>')
    elif content["type"] == "social":
        dsl_parts.append(f'        <Text text="{content["text"]}" color="#10B981" fontSize="32" fontStyle="BOLD"/>')
    elif content["type"] == "infographic":
        for tip in content["tips"]:
            dsl_parts.append(f'        <Text text="• {tip}" color="#FFFFFF" fontSize="22"/>')
    elif content["type"] == "invite":
        dsl_parts.append(f'        <Text text="{content["event"]}" color="#F59E0B" fontSize="32" fontStyle="BOLD"/>')
        dsl_parts.append(f'        <Text text="{content["date"]}" color="#FFFFFF" fontSize="24"/>')
    elif content["type"] == "dashboard":
        for label, value in content["stats"]:
            dsl_parts.append(f'        <Text text="{label}：{value}" color="#FFFFFF" fontSize="20"/>')
    elif content["type"] == "checkin":
        dsl_parts.append(f'        <Text text="{content["text"]}" color="#10B981" fontSize="28" fontStyle="BOLD"/>')
    elif content["type"] == "report":
        dsl_parts.append(f'        <Text text="{content["month"]}" color="#F59E0B" fontSize="28" fontStyle="BOLD"/>')
        dsl_parts.append(f'        <Text text="{content["summary"]}" color="#FFFFFF" fontSize="20"/>')

    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    dsl_parts.append('  </Column>')
    dsl_parts.append('</Snapshot>')

    dsl = '\n'.join(dsl_parts)

    case_dir = OUTPUT_DIR / cid
    case_dir.mkdir(parents=True, exist_ok=True)
    temp_case_dir = TEMP_DIR / cid
    temp_case_dir.mkdir(parents=True, exist_ok=True)

    with open(temp_case_dir / 'final.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)

    case_md = f"""# {title}
## 触点：{content["type"]}
## 品牌：{BRAND}
"""
    with open(case_dir / 'case.md', 'w', encoding='utf-8') as f:
        f.write(case_md)

print(f"Generated {len(cases)} B02 cases")

portfolio = {
    "schema_version": 1,
    "task_id": "B02",
    "path_base": "output_dir",
    "brand": BRAND,
    "cases": [{"id": c["id"], "title": c["title"], "size": c["size"]} for c in cases]
}
with open(OUTPUT_DIR / 'portfolio.json', 'w', encoding='utf-8') as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=2)
print("Saved portfolio.json")
