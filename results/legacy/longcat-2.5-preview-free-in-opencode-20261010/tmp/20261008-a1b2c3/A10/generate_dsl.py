#!/usr/bin/env python3
"""A10 - 透明合成与滤镜语义实验板 DSL 生成器"""
import json
from pathlib import Path

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_RED = "#FF0000"
COLOR_BLUE = "#0000FF"
COLOR_FILTER = "#F6B94A"

# 网格参数
cols = 3
rows = 2
cell_w = 320
cell_h = 240
gap = 32
grid_w = cols * cell_w + (cols - 1) * gap
grid_h = rows * cell_h + (rows - 1) * gap
offset_x = (1440 - grid_w) // 2
offset_y = 100

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1440" height="1100" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Container width="1392" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">看到差异，才能说用对了</Text>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 实验板 -->')
lines.append(f'      <Container width="{grid_w}" height="{grid_h}" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
lines.append(f'        <Stack>')

# 实验①：红蓝重叠的矩形分别设置50%alpha
x1 = offset_x
y1 = offset_y
lines.append(f'          <!-- 实验① -->')
lines.append(f'          <Positioned left="{x1}" top="{y1}" width="{cell_w}" height="{cell_h}">')
lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF">')
lines.append(f'              <Text color="#000000" fontSize="14" fontStyle="BOLD">① 50% alpha</Text>')
lines.append(f'              <Positioned left="40" top="40" width="160" height="120">')
lines.append(f'                <Container width="160" height="120" color="#FF000080"/>')
lines.append(f'              </Positioned>')
lines.append(f'              <Positioned left="120" top="80" width="160" height="120">')
lines.append(f'                <Container width="160" height="120" color="#0000FF80"/>')
lines.append(f'              </Positioned>')
lines.append(f'            </Container>')
lines.append(f'          </Positioned>')

# 实验②：同样的两个不透明矩形放在Opacity(0.5)组内
x2 = offset_x + cell_w + gap
y2 = offset_y
lines.append(f'          <!-- 实验② -->')
lines.append(f'          <Positioned left="{x2}" top="{y2}" width="{cell_w}" height="{cell_h}">')
lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF">')
lines.append(f'              <Text color="#000000" fontSize="14" fontStyle="BOLD">② Opacity(0.5)</Text>')
lines.append(f'              <Opacity opacity="0.5">')
lines.append(f'                <Positioned left="40" top="40" width="160" height="120">')
lines.append(f'                  <Container width="160" height="120" color="#FF0000"/>')
lines.append(f'                </Positioned>')
lines.append(f'                <Positioned left="120" top="80" width="160" height="120">')
lines.append(f'                  <Container width="160" height="120" color="#0000FF"/>')
lines.append(f'                </Positioned>')
lines.append(f'              </Opacity>')
lines.append(f'            </Container>')
lines.append(f'          </Positioned>')

# 实验③：带锐利条纹背景的圆角卡，仅背景模糊
x3 = offset_x + 2 * (cell_w + gap)
y3 = offset_y
lines.append(f'          <!-- 实验③ -->')
lines.append(f'          <Positioned left="{x3}" top="{y3}" width="{cell_w}" height="{cell_h}">')
lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF">')
lines.append(f'              <Text color="#000000" fontSize="14" fontStyle="BOLD">③ 仅背景模糊</Text>')
lines.append(f'              <BackdropFilter sigmaX="6" sigmaY="6">')
lines.append(f'                <ClipRRect borderRadius="20">')
lines.append(f'                  <Container width="240" height="160" color="#FFFFFF">')
lines.append(f'                    <Text color="#000000" fontSize="24" fontStyle="BOLD" textAlign="CENTER">SHARP / BLUR</Text>')
lines.append(f'                  </Container>')
lines.append(f'                </ClipRRect>')
lines.append(f'              </BackdropFilter>')
lines.append(f'            </Container>')
lines.append(f'          </Positioned>')

# 实验④：相同条纹，把卡内文字与形状一起子树模糊
x4 = offset_x
y4 = offset_y + cell_h + gap
lines.append(f'          <!-- 实验④ -->')
lines.append(f'          <Positioned left="{x4}" top="{y4}" width="{cell_w}" height="{cell_h}">')
lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF">')
lines.append(f'              <Text color="#000000" fontSize="14" fontStyle="BOLD">④ 子树模糊</Text>')
lines.append(f'              <ImageFiltered sigmaX="6" sigmaY="6">')
lines.append(f'                <ClipRRect borderRadius="20">')
lines.append(f'                  <Container width="240" height="160" color="#FFFFFF">')
lines.append(f'                    <Text color="#000000" fontSize="24" fontStyle="BOLD" textAlign="CENTER">SHARP / BLUR</Text>')
lines.append(f'                  </Container>')
lines.append(f'                </ClipRRect>')
lines.append(f'              </ImageFiltered>')
lines.append(f'            </Container>')
lines.append(f'          </Positioned>')

# 实验⑤：先ColorFiltered(MULTIPLY)后子树高斯模糊
x5 = offset_x + cell_w + gap
y5 = offset_y + cell_h + gap
lines.append(f'          <!-- 实验⑤ -->')
lines.append(f'          <Positioned left="{x5}" top="{y5}" width="{cell_w}" height="{cell_h}">')
lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF">')
lines.append(f'              <Text color="#000000" fontSize="14" fontStyle="BOLD">⑤ MULTIPLY+模糊</Text>')
lines.append(f'              <ColorFiltered color="#F6B94A" blendMode="MULTIPLY">')
lines.append(f'                <ImageFiltered sigmaX="6" sigmaY="6">')
lines.append(f'                  <Container width="240" height="160" color="#FFFFFF">')
lines.append(f'                    <Positioned left="20" top="20" width="80" height="80">')
lines.append(f'                      <Container width="80" height="80" color="#333333"/>')
lines.append(f'                    </Positioned>')
lines.append(f'                    <Positioned left="120" top="60" width="80" height="80">')
lines.append(f'                      <Container width="80" height="80" color="#666666"/>')
lines.append(f'                    </Positioned>')
lines.append(f'                  </Container>')
lines.append(f'                </ImageFiltered>')
lines.append(f'              </ColorFiltered>')
lines.append(f'            </Container>')
lines.append(f'          </Positioned>')

# 实验⑥：同样的⑤效果再限定于圆形裁剪区域
x6 = offset_x + 2 * (cell_w + gap)
y6 = offset_y + cell_h + gap
lines.append(f'          <!-- 实验⑥ -->')
lines.append(f'          <Positioned left="{x6}" top="{y6}" width="{cell_w}" height="{cell_h}">')
lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF">')
lines.append(f'              <Text color="#000000" fontSize="14" fontStyle="BOLD">⑥ 圆形裁剪</Text>')
lines.append(f'              <ClipOval>')
lines.append(f'                <ColorFiltered color="#F6B94A" blendMode="MULTIPLY">')
lines.append(f'                  <ImageFiltered sigmaX="6" sigmaY="6">')
lines.append(f'                    <Container width="240" height="160" color="#FFFFFF">')
lines.append(f'                      <Positioned left="20" top="20" width="80" height="80">')
lines.append(f'                        <Container width="80" height="80" color="#333333"/>')
lines.append(f'                      </Positioned>')
lines.append(f'                      <Positioned left="120" top="60" width="80" height="80">')
lines.append(f'                        <Container width="80" height="80" color="#666666"/>')
lines.append(f'                      </Positioned>')
lines.append(f'                    </Container>')
lines.append(f'                  </ImageFiltered>')
lines.append(f'                </ColorFiltered>')
lines.append(f'              </ClipOval>')
lines.append(f'            </Container>')
lines.append(f'          </Positioned>')

lines.append(f'        </Stack>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <!-- 说明 -->')
lines.append(f'      <Container width="1392" height="60" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="12">① 50% alpha：红蓝矩形分别设置50%透明度，重叠处呈现混合色</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="12">② Opacity(0.5)：不透明矩形放在0.5透明度的组内，整体变淡</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="12">③ 仅背景模糊：BackdropFilter只模糊背景，文字保持清晰</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="12">④ 子树模糊：ImageFiltered模糊整个子树，包括文字</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="12">⑤ MULTIPLY+模糊：先颜色混合再高斯模糊</Text>')
lines.append(f'        <Text color="{TEXT_SECONDARY}" fontSize="12">⑥ 圆形裁剪：效果限定在圆形区域内</Text>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)

output_dir = Path("outputs/20261008-a1b2c3/A10")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "compositing-lab.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

# 保存composite-audit.json
audit = {
    "experiments": {
        "1": {"name": "50% alpha", "description": "红蓝矩形分别设置50%透明度"},
        "2": {"name": "Opacity(0.5)", "description": "不透明矩形放在0.5透明度的组内"},
        "3": {"name": "仅背景模糊", "description": "BackdropFilter只模糊背景"},
        "4": {"name": "子树模糊", "description": "ImageFiltered模糊整个子树"},
        "5": {"name": "MULTIPLY+模糊", "description": "先颜色混合再高斯模糊"},
        "6": {"name": "圆形裁剪", "description": "效果限定在圆形区域内"}
    },
    "sampling_point": {"x": 180, "y": 100},
    "expected_colors": {
        "1": "重叠处呈现红蓝混合色（50% alpha混合）",
        "2": "整体变淡（0.5透明度）"
    }
}

with open(output_dir / "composite-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

print(f"DSL generated: {len(dsl)} chars")
