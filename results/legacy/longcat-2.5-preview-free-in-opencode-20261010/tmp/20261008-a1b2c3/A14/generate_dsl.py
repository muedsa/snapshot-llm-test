#!/usr/bin/env python3
"""A14 - 八组文案压力测试与批量生成 DSL 生成器"""
import json
from pathlib import Path

# 数据
cards = [
    {"id": "K01", "title": "开始", "speaker": "林川", "status": "开放", "time": "09:00"},
    {"id": "K02", "title": "读文档，也要读懂布局约束", "speaker": "周禾 / 许宁", "status": "满额", "time": "09:40"},
    {"id": "K03", "title": "当所有信息都想成为标题：密集内容中的取舍与层级", "speaker": "顾行", "status": "候补", "time": "10:20"},
    {"id": "K04", "title": "A < B & C > D：不要把文本当成标签", "speaker": "苏言", "status": "开放", "time": "11:00"},  # XML special chars need escaping in DSL
    {"id": "K05", "title": "Color, Alpha & Contrast / 从颜色到可读性", "speaker": "孟澄", "status": "开放", "time": "13:00"},
    {"id": "K06", "title": "两张看似相同的图片，为什么不能证明语义相同？", "speaker": "许宁", "status": "取消", "time": "13:40"},
    {"id": "K07", "title": "把一次失败变成可复现记录——服务、字体、数据与视觉检查", "speaker": "Northstar Research · 林川", "status": "候补", "time": "14:20"},
    {"id": "K08", "title": "从\u201c已经请求成功\u201d到\u201c已经完成作品\u201d：模型工作能力的最后一公里", "speaker": "周禾", "status": "开放", "time": "15:00"}
]

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
STATUS_COLORS = {
    "开放": "#10B981",
    "满额": "#F59E0B",
    "候补": "#3B82F6",
    "取消": "#EF4444"
}

output_dir = Path("outputs/20261008-a1b2c3/A14")
output_dir.mkdir(parents=True, exist_ok=True)

# 生成8张卡
for card in cards:
    lines = []
    lines.append(f'<Snapshot background="{BG}" type="png">')
    lines.append(f'  <Container width="1200" height="630" padding="(40,40)">')
    lines.append(f'    <Column crossAxisAlignment="START">')
    lines.append(f'')
    lines.append(f'      <!-- 标题 -->')
    lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="36" fontStyle="BOLD">{card["title"]}</Text>')
    lines.append(f'')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'')
    lines.append(f'      <!-- 讲者 -->')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="22">{card["speaker"]}</Text>')
    lines.append(f'')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'')
    lines.append(f'      <!-- 信息 -->')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="18">2026.11.07 · {card["time"]}</Text>')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="18">Structure / Vision</Text>')
    lines.append(f'')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'')
    lines.append(f'      <!-- 状态 -->')
    status_color = STATUS_COLORS[card["status"]]
    lines.append(f'      <Container width="120" height="36" color="{status_color}" borderRadius="6" padding="(4,8)">')
    lines.append(f'        <Text color="#FFFFFF" fontSize="16" fontStyle="BOLD" textAlign="CENTER">{card["status"]}</Text>')
    lines.append(f'      </Container>')
    
    if card["status"] == "取消":
        lines.append(f'      <Text color="#EF4444" fontSize="16" fontStyle="BOLD">本场取消</Text>')
    
    lines.append(f'')
    lines.append(f'    </Column>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    
    dsl = "\n".join(lines)
    with open(output_dir / f'card-{card["id"]}.snapshot', "w", encoding="utf-8") as f:
        f.write(dsl)
    print(f'{card["id"]}: {len(dsl)} chars')

# 保存batch-audit.json
batch_audit = []
for card in cards:
    batch_audit.append({
        "id": card["id"],
        "title": card["title"],
        "speaker": card["speaker"],
        "status": card["status"],
        "time": card["time"],
        "title_font_size": 36,
        "speaker_font_size": 22,
        "viewed": False
    })

with open(output_dir / "batch-audit.json", "w", encoding="utf-8") as f:
    json.dump(batch_audit, f, ensure_ascii=False, indent=2)

print("All cards generated")
