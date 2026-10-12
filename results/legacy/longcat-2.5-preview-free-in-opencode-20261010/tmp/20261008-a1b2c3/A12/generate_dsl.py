#!/usr/bin/env python3
"""A12 - 四断点完整内容视觉系统 DSL 生成器"""
import json
from pathlib import Path

# 数据
content = {
    "title": "Structure / Vision",
    "subtitle": "让模型从读懂文档到完成作品",
    "date": "2026.11.07",
    "time": "09:00–16:00",
    "location": "云构中心 · ONLINE",
    "cta": "免费参加 · 扫码方式详见官网",
    "website": "structure.example.org",
    "cards": [
        {"id": "C1", "title": "文档阅读", "detail": "辨认支持的标签与属性"},
        {"id": "C2", "title": "数据核验", "detail": "让结论与分母保持一致"},
        {"id": "C3", "title": "布局构建", "detail": "组织密集信息与留白"},
        {"id": "C4", "title": "服务渲染", "detail": "记录真实响应与失败"},
        {"id": "C5", "title": "视觉迭代", "detail": "看图修改，再次验证"},
        {"id": "C6", "title": "可复现交付", "detail": "图片、DSL与过程留痕"}
    ]
}

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_ACCENT = "#3B82F6"

# 保存design-tokens.json
tokens = {
    "colors": {
        "background": BG,
        "card": CARD_BG,
        "border": CARD_BORDER,
        "text": TEXT_PRIMARY,
        "text_secondary": TEXT_SECONDARY,
        "accent": COLOR_ACCENT
    },
    "fonts": {
        "title": 40,
        "subtitle": 20,
        "body": 20,
        "card_title": 18,
        "card_detail": 16
    },
    "spacing": {
        "mobile": 16,
        "tablet": 32,
        "desktop": 32,
        "stage": 32
    }
}

output_dir = Path("outputs/20261008-a1b2c3/A12")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "design-tokens.json", "w", encoding="utf-8") as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)

# 生成四个尺寸的DSL
sizes = [
    ("mobile", 360, 800, 16, 1),
    ("tablet", 768, 1024, 32, 2),
    ("desktop", 1440, 900, 32, 3),
    ("stage", 1920, 1080, 32, 3)
]

for name, w, h, padding, cols in sizes:
    lines = []
    lines.append(f'<Snapshot background="{BG}" type="png">')
    lines.append(f'  <Container width="{w}" height="{h}" padding="({padding},{padding})">')
    lines.append(f'    <Column crossAxisAlignment="START">')
    lines.append(f'')
    lines.append(f'      <!-- 标题 -->')
    lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="40" fontStyle="BOLD">{content["title"]}</Text>')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="20">{content["subtitle"]}</Text>')
    lines.append(f'')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'')
    lines.append(f'      <!-- 信息 -->')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="16">{content["date"]} · {content["time"]}</Text>')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="16">{content["location"]}</Text>')
    lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="16">{content["website"]}</Text>')
    lines.append(f'')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'')
    lines.append(f'      <!-- CTA -->')
    lines.append(f'      <Container width="{w - 2*padding}" height="40" color="{COLOR_ACCENT}" borderRadius="8" padding="(8,12)">')
    lines.append(f'        <Text color="#FFFFFF" fontSize="16" fontStyle="BOLD" textAlign="CENTER">{content["cta"]}</Text>')
    lines.append(f'      </Container>')
    lines.append(f'')
    lines.append(f'      <SizedBox height="16"/>')
    lines.append(f'')
    lines.append(f'      <!-- 卡片 -->')
    
    if cols == 1:
        # 手机：单列
        for card in content["cards"]:
            lines.append(f'      <Container width="{w - 2*padding}" height="80" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(8,12)">')
            lines.append(f'        <Column crossAxisAlignment="START">')
            lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">{card["id"]} · {card["title"]}</Text>')
            lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="14">{card["detail"]}</Text>')
            lines.append(f'        </Column>')
            lines.append(f'      </Container>')
            lines.append(f'      <SizedBox height="8"/>')
    else:
        # 平板/桌面/大屏：多列
        card_w = (w - 2*padding - (cols - 1) * 16) // cols
        for i in range(0, len(content["cards"]), cols):
            lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
            for j in range(cols):
                if i + j < len(content["cards"]):
                    card = content["cards"][i + j]
                    lines.append(f'        <Container width="{card_w}" height="100" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(8,12)">')
                    lines.append(f'          <Column crossAxisAlignment="START">')
                    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">{card["id"]} · {card["title"]}</Text>')
                    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="14">{card["detail"]}</Text>')
                    lines.append(f'          </Column>')
                    lines.append(f'        </Container>')
                else:
                    lines.append(f'        <Container width="{card_w}" height="100"/>')
            lines.append(f'      </Row>')
            lines.append(f'      <SizedBox height="16"/>')
    
    lines.append(f'')
    lines.append(f'    </Column>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    
    dsl = "\n".join(lines)
    with open(output_dir / f"{name}.snapshot", "w", encoding="utf-8") as f:
        f.write(dsl)
    print(f"{name}: {len(dsl)} chars")

# 保存content-map.json
content_map = {}
for name, w, h, padding, cols in sizes:
    content_map[name] = {
        "size": {"width": w, "height": h},
        "padding": padding,
        "columns": cols,
        "title": {"text": content["title"], "position": "top"},
        "subtitle": {"text": content["subtitle"], "position": "top"},
        "cards": [{"id": c["id"], "title": c["title"], "detail": c["detail"]} for c in content["cards"]]
    }

with open(output_dir / "content-map.json", "w", encoding="utf-8") as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)

print("All DSLs generated")
