#!/usr/bin/env python3
"""A21 - 第二轮 DSL 生成器"""
import json
from pathlib import Path

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_1 = "#3B82F6"
COLOR_2 = "#8B5CF6"
COLOR_3 = "#EC4899"

output_dir = Path("outputs/20261008-a1b2c3/A21/round-02")
output_dir.mkdir(parents=True, exist_ok=True)

def brand_symbol(scale=1.0):
    lines = []
    s = scale
    lines.append(f'          <Stack width="{int(120*s)}" height="{int(120*s)}">')
    lines.append(f'            <Positioned left="0" top="0" width="{int(80*s)}" height="{int(80*s)}">')
    lines.append(f'              <Container width="{int(80*s)}" height="{int(80*s)}" color="{COLOR_1}" borderRadius="{int(16*s)}"/>')
    lines.append(f'            </Positioned>')
    lines.append(f'            <Positioned left="{int(20*s)}" top="{int(20*s)}" width="{int(80*s)}" height="{int(80*s)}">')
    lines.append(f'              <Container width="{int(80*s)}" height="{int(80*s)}" color="{COLOR_2}" borderRadius="{int(16*s)}"/>')
    lines.append(f'            </Positioned>')
    lines.append(f'            <Positioned left="{int(40*s)}" top="{int(40*s)}" width="{int(40*s)}" height="{int(40*s)}">')
    lines.append(f'              <Container width="{int(40*s)}" height="{int(40*s)}" color="{COLOR_3}" borderRadius="{int(20*s)}"/>')
    lines.append(f'            </Positioned>')
    lines.append(f'          </Stack>')
    return lines

# 竖海报DSL (1080x1350)
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1080" height="1350" padding="(48,64)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <!-- 品牌图形 -->')
lines.extend(brand_symbol(0.8))
lines.append(f'      <SizedBox height="32"/>')
lines.append(f'      <!-- 主标题（最多3行） -->')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="56" fontStyle="BOLD">当所有信息都想成为标题：</Text>')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="56" fontStyle="BOLD">让复杂信息变得清晰的</Text>')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="56" fontStyle="BOLD">结构化方法</Text>')
lines.append(f'      <SizedBox height="24"/>')
lines.append(f'      <!-- 赞助方 -->')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">Northstar Research / 云构工具</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">免费参加 · 无需报名</Text>')
lines.append(f'      <SizedBox height="24"/>')
lines.append(f'      <!-- 信息 -->')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="28">2026.11.07 19:30</Text>')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="28">ONLINE LAUNCH</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">讲者：林川 / 苏言</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">layerlight.example.org</Text>')
lines.append(f'      <SizedBox height="48"/>')
lines.append(f'      <Container width="952" height="160" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}"/>')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_portrait = "\n".join(lines)
with open(output_dir / "launch-portrait.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_portrait)

# 横屏DSL (1440x810)
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1440" height="810" padding="(48,64)">')
lines.append(f'    <Row crossAxisAlignment="CENTER">')
lines.append(f'      <Column crossAxisAlignment="START">')
lines.extend(brand_symbol(1.0))
lines.append(f'        <SizedBox height="24"/>')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="56" fontStyle="BOLD">当所有信息都想成为标题：</Text>')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="56" fontStyle="BOLD">让复杂信息变得清晰的</Text>')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="56" fontStyle="BOLD">结构化方法</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="24">Northstar Research / 云构工具</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="24">免费参加 · 无需报名</Text>')
lines.append(f'      </Column>')
lines.append(f'      <SizedBox width="48"/>')
lines.append(f'      <Column crossAxisAlignment="START">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="32">2026.11.07 19:30</Text>')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="32">ONLINE LAUNCH</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="24">讲者：林川 / 苏言</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="24">layerlight.example.org</Text>')
lines.append(f'        <SizedBox height="32"/>')
lines.append(f'        <Container width="400" height="100" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}"/>')
lines.append(f'      </Column>')
lines.append(f'    </Row>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_wide = "\n".join(lines)
with open(output_dir / "launch-wide.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_wide)

# 保存design-tokens.json
tokens = {
    "colors": {"background": BG, "card": CARD_BG, "border": CARD_BORDER, "text": TEXT_PRIMARY, "text_secondary": TEXT_SECONDARY, "accent1": COLOR_1, "accent2": COLOR_2, "accent3": COLOR_3},
    "fonts": {"title": 56, "subtitle": 24, "body": 24},
    "brand_components": 6,
    "sponsors": "Northstar Research / 云构工具",
    "cta": "免费参加 · 无需报名"
}
with open(output_dir / "design-tokens.json", "w", encoding="utf-8") as f:
    json.dump(tokens, f, ensure_ascii=False, indent=2)

# 保存content-map.json
content_map = {
    "title": "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
    "date": "2026.11.07 19:30",
    "event": "ONLINE LAUNCH",
    "speakers": "讲者：林川 / 苏言",
    "website": "layerlight.example.org",
    "sponsors": "Northstar Research / 云构工具",
    "cta": "免费参加 · 无需报名"
}
with open(output_dir / "content-map.json", "w", encoding="utf-8") as f:
    json.dump(content_map, f, ensure_ascii=False, indent=2)

print(f"Round 2 Portrait DSL: {len(dsl_portrait)} chars")
print(f"Round 2 Wide DSL: {len(dsl_wide)} chars")
