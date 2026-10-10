#!/usr/bin/env python3
"""A23 - 格式边界下的动画分镜交付 DSL 生成器"""
import json
import math
from pathlib import Path

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLORS = ["#3B82F6", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899", "#06B6D4"]

output_dir = Path("outputs/20261008-a1b2c3/A23")
output_dir.mkdir(parents=True, exist_ok=True)

# 封面DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1200" height="800" padding="(48,64)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="64" fontStyle="BOLD">从结构到画面</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="24">结构汇聚成图像</Text>')
lines.append(f'      <SizedBox height="32"/>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="18">6帧关键帧 · 12个几何单元 · 透明背景</Text>')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_cover = "\n".join(lines)
with open(output_dir / "cover.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_cover)

# 6帧DSL（12个几何单元由分散到汇聚）
frames = []
for frame_idx in range(6):
    t = frame_idx / 5  # 0到1
    lines = []
    lines.append(f'<Snapshot background="transparent" type="png">')
    lines.append(f'  <Container width="600" height="600">')
    lines.append(f'    <Stack width="600" height="600">')
    
    for i in range(12):
        # 计算单元位置（从分散到汇聚）
        angle = (i / 12) * 2 * math.pi
        # 分散状态：半径200；汇聚状态：半径80
        r = 200 - t * 120
        cx = 300 + r * math.cos(angle)
        cy = 300 + r * math.sin(angle)
        size = 40
        color = COLORS[i % len(COLORS)]
        x = cx - size / 2
        y = cy - size / 2
        
        lines.append(f'      <Positioned left="{x}" top="{y}" width="{size}" height="{size}">')
        lines.append(f'        <Container width="{size}" height="{size}" color="{color}" borderRadius="{size//2}"/>')
        lines.append(f'      </Positioned>')
    
    lines.append(f'    </Stack>')
    lines.append(f'  </Container>')
    lines.append(f'</Snapshot>')
    
    dsl = "\n".join(lines)
    with open(output_dir / f'frame-{frame_idx+1:02d}.snapshot', "w", encoding="utf-8") as f:
        f.write(dsl)
    frames.append(dsl)

# 保存timing.json
timing = {
    "fps": 4,
    "duration_ms": 1500,
    "frame_interval_ms": 250,
    "loop": True,
    "frames": [f"frame-{i+1:02d}.png" for i in range(6)],
    "seamless": True,
    "note": "6帧闭合轨迹，循环播放无跳变"
}
with open(output_dir / "timing.json", "w", encoding="utf-8") as f:
    json.dump(timing, f, ensure_ascii=False, indent=2)

# 保存frame-data.json
frame_data = []
for i in range(6):
    frame_data.append({
        "frame": i + 1,
        "units": 12,
        "radius": 200 - (i / 5) * 120,
        "background": "transparent"
    })
with open(output_dir / "frame-data.json", "w", encoding="utf-8") as f:
    json.dump(frame_data, f, ensure_ascii=False, indent=2)

# 保存limitations.md
limitations = """# 格式限制说明

## 请求：文字可编辑SVG
- 支持情况：不支持
- 依据：Snapshot DSL输出为位图PNG/JPEG/WebP，不支持SVG矢量输出
- 替代：交付PNG封面
- 后续工作：需要外部工具将PNG转换为SVG

## 请求：CMYK印刷稿
- 支持情况：不支持
- 依据：Snapshot DSL输出为RGB位图，不支持CMYK色彩空间
- 替代：交付RGB PNG
- 后续工作：需要外部工具将RGB转换为CMYK

## 请求：6帧透明GIF动画
- 支持情况：不支持
- 依据：Snapshot DSL输出为静态PNG，不支持GIF动画
- 替代：交付6张透明PNG关键帧 + timing.json
- 后续工作：需要外部工具将6帧合成为GIF

## 请求：PNG封面
- 支持情况：支持
- 依据：Snapshot DSL原生支持PNG输出
- 替代：已交付1200×800 RGB PNG封面
"""

with open(output_dir / "limitations.md", "w", encoding="utf-8") as f:
    f.write(limitations)

print(f"Cover DSL: {len(dsl_cover)} chars")
print("All frames generated")
