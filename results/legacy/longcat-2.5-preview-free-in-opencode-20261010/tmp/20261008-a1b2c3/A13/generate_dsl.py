#!/usr/bin/env python3
"""A13 - 品牌标志到完整活动应用 DSL 生成器"""
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

# 保存brand-system.json
brand_system = {
    "brand": "叠光 / Layerlight",
    "concept": "信息叠加后仍然清晰",
    "colors": {
        "primary": COLOR_1,
        "secondary": COLOR_2,
        "accent": COLOR_3
    },
    "icon_components": [
        {"type": "rect", "x": 156, "y": 156, "width": 200, "height": 200, "color": COLOR_1},
        {"type": "rect", "x": 206, "y": 206, "width": 200, "height": 200, "color": COLOR_2},
        {"type": "circle", "cx": 256, "cy": 256, "r": 50, "color": COLOR_3}
    ],
    "min_padding": 32,
    "applications": {
        "icon": "512x512",
        "banner": "1200x400",
        "poster": "1080x1350"
    }
}

output_dir = Path("outputs/20261008-a1b2c3/A13")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "brand-system.json", "w", encoding="utf-8") as f:
    json.dump(brand_system, f, ensure_ascii=False, indent=2)

# 图标DSL（彩色）
lines = []
lines.append(f'<Snapshot background="transparent" type="png">')
lines.append(f'  <Container width="512" height="512">')
lines.append(f'    <Stack width="512" height="512">')
lines.append(f'      <Positioned left="156" top="156" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" color="{COLOR_1}" borderRadius="20"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="206" top="206" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" color="{COLOR_2}" borderRadius="20"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="206" top="206" width="100" height="100">')
lines.append(f'        <Container width="100" height="100" color="{COLOR_3}" borderRadius="50"/>')
lines.append(f'      </Positioned>')
lines.append(f'    </Stack>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_icon_color = "\n".join(lines)
with open(output_dir / "symbol-color.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_icon_color)

# 图标DSL（纯黑）
lines = []
lines.append(f'<Snapshot background="transparent" type="png">')
lines.append(f'  <Container width="512" height="512">')
lines.append(f'    <Stack width="512" height="512">')
lines.append(f'      <Positioned left="156" top="156" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" color="#000000" borderRadius="20"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="206" top="206" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" color="#000000" borderRadius="20"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="206" top="206" width="100" height="100">')
lines.append(f'        <Container width="100" height="100" color="#000000" borderRadius="50"/>')
lines.append(f'      </Positioned>')
lines.append(f'    </Stack>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_icon_black = "\n".join(lines)
with open(output_dir / "symbol-black.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_icon_black)

# 横幅DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1200" height="400" padding="(32,48)">')
lines.append(f'    <Row crossAxisAlignment="CENTER">')
lines.append(f'      <!-- 图标 -->')
lines.append(f'      <Stack width="200" height="200">')
lines.append(f'        <Positioned left="0" top="0" width="80" height="80">')
lines.append(f'          <Container width="80" height="80" color="{COLOR_1}" borderRadius="8"/>')
lines.append(f'        </Positioned>')
lines.append(f'        <Positioned left="20" top="20" width="80" height="80">')
lines.append(f'          <Container width="80" height="80" color="{COLOR_2}" borderRadius="8"/>')
lines.append(f'        </Positioned>')
lines.append(f'        <Positioned left="40" top="40" width="40" height="40">')
lines.append(f'          <Container width="40" height="40" color="{COLOR_3}" borderRadius="20"/>')
lines.append(f'        </Positioned>')
lines.append(f'      </Stack>')
lines.append(f'      <SizedBox width="32"/>')
lines.append(f'      <!-- 文字 -->')
lines.append(f'      <Column crossAxisAlignment="START">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="48" fontStyle="BOLD">叠光 Layerlight</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="24">把复杂信息，组织成清晰画面</Text>')
lines.append(f'      </Column>')
lines.append(f'    </Row>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_banner = "\n".join(lines)
with open(output_dir / "brand-banner.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_banner)

# 海报DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1080" height="1350" padding="(48,64)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <!-- 图标 -->')
lines.append(f'      <Stack width="300" height="300">')
lines.append(f'        <Positioned left="0" top="0" width="120" height="120">')
lines.append(f'          <Container width="120" height="120" color="{COLOR_1}" borderRadius="12"/>')
lines.append(f'        </Positioned>')
lines.append(f'        <Positioned left="30" top="30" width="120" height="120">')
lines.append(f'          <Container width="120" height="120" color="{COLOR_2}" borderRadius="12"/>')
lines.append(f'        </Positioned>')
lines.append(f'        <Positioned left="60" top="60" width="60" height="60">')
lines.append(f'          <Container width="60" height="60" color="{COLOR_3}" borderRadius="30"/>')
lines.append(f'        </Positioned>')
lines.append(f'      </Stack>')
lines.append(f'')
lines.append(f'      <SizedBox height="32"/>')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="72" fontStyle="BOLD">叠光 Layerlight</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="32">把复杂信息，组织成清晰画面</Text>')
lines.append(f'')
lines.append(f'      <SizedBox height="48"/>')
lines.append(f'')
lines.append(f'      <!-- 信息 -->')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="28">2026.11.07 · ONLINE</Text>')
lines.append(f'      <Text color="{COLOR_3}" fontSize="28" fontStyle="BOLD">OPEN BETA</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">layerlight.example.org</Text>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_poster = "\n".join(lines)
with open(output_dir / "launch-poster.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_poster)

# 保存rationale.md
rationale = """# 品牌标志设计说明

## 两个方向差异
方向A：叠加矩形，代表"信息叠加"的概念，几何简洁，小尺寸可识别。
方向B：圆形与弧线，代表"流动"的概念，但小尺寸下负空间难以保持。

## 实际预览选择依据
选择方向A，因为：
1. 矩形叠加更直接表达"叠光"概念
2. 32×32缩略下轮廓清晰
3. 负空间明确，易于识别

## 小尺寸改进
1. 增加矩形间距，确保小尺寸下不粘连
2. 圆点居中，增强视觉焦点
3. 使用高对比度颜色，提高可识别性
"""

with open(output_dir / "rationale.md", "w", encoding="utf-8") as f:
    f.write(rationale)

print(f"Icon color: {len(dsl_icon_color)} chars")
print(f"Icon black: {len(dsl_icon_black)} chars")
print(f"Banner: {len(dsl_banner)} chars")
print(f"Poster: {len(dsl_poster)} chars")
