import math
from pathlib import Path

# Layout
W, H = 1440, 1100
CELL_W, CELL_H = 320, 240
GAP = 32
COLS, ROWS = 3, 2
TITLE_H = 60
MARGIN_X = (W - (COLS * CELL_W + (COLS-1) * GAP)) // 2
MARGIN_Y = TITLE_H + 20

def cell_pos(col, row):
    x = MARGIN_X + col * (CELL_W + GAP)
    y = MARGIN_Y + row * (CELL_H + GAP)
    return x, y

# Colors
BG = "#F8FAFC"
CELL_BG = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Title
dsl_parts.append(f'    <Container height="{TITLE_H}" padding="(0,24)">')
dsl_parts.append(f'      <Text text="看到差异，才能说用对了" color="{TEXT_DARK}" fontSize="24" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')

experiments = [
    ("①", "红蓝50%alpha重叠", "红#FF000080+蓝#0000FF80"),
    ("②", "不透明红蓝+Opacity(0.5)", "组opacity=0.5"),
    ("③", "背景模糊", "仅背景模糊sigma=6"),
    ("④", "子树模糊", "文字+形状+背景模糊"),
    ("⑤", "MULTIPLY+模糊", "滤色#F6B94A+sigma=6"),
    ("⑥", "MULTIPLY+模糊+圆形裁剪", "圆心(160,120)半径100"),
]

for idx, (num, title, desc) in enumerate(experiments):
    col = idx % COLS
    row = idx // COLS
    x, y = cell_pos(col, row)
    
    dsl_parts.append(f'    <Positioned left="{x}" top="{y}" width="{CELL_W}" height="{CELL_H}">')
    dsl_parts.append(f'      <Container width="{CELL_W}" height="{CELL_H}" color="{CELL_BG}" border="1 SOLID {BORDER}" borderRadius="8">')
    dsl_parts.append(f'        <Stack>')
    # Label
    dsl_parts.append(f'          <Positioned left="0" top="0" width="{CELL_W}" height="30">')
    dsl_parts.append(f'            <Column crossAxisAlignment="START">')
    dsl_parts.append(f'              <Text text="{num} {title}" color="{TEXT_DARK}" fontSize="16" fontStyle="BOLD"/>')
    dsl_parts.append(f'            </Column>')
    dsl_parts.append(f'          </Positioned>')
    # Content area
    dsl_parts.append(f'          <Positioned left="0" top="30" width="{CELL_W}" height="{CELL_H-30}">')
    dsl_parts.append(f'            <Column crossAxisAlignment="START">')
    dsl_parts.append(f'              <Text text="{desc}" color="{TEXT_MED}" fontSize="14"/>')
    if idx == 0:
        dsl_parts.append(f'              <Text text="红(40,40,160,120) 蓝(120,80,160,120)" color="{TEXT_MED}" fontSize="12"/>')
        dsl_parts.append(f'              <Text text="采样点(180,100): 理论RGB=(64,64,128)" color="{TEXT_DARK}" fontSize="12"/>')
    elif idx == 1:
        dsl_parts.append(f'              <Text text="红(40,40,160,120) 蓝(120,80,160,120)" color="{TEXT_MED}" fontSize="12"/>')
        dsl_parts.append(f'              <Text text="采样点(180,100): 理论RGB=(128,128,255)" color="{TEXT_DARK}" fontSize="12"/>')
    elif idx == 2:
        dsl_parts.append(f'              <Text text="条纹背景+圆角卡(40,40,240,160)" color="{TEXT_MED}" fontSize="12"/>')
        dsl_parts.append(f'              <Text text="卡内文字SHARP/BLUR清晰" color="{TEXT_DARK}" fontSize="12"/>')
    elif idx == 3:
        dsl_parts.append(f'              <Text text="条纹背景+圆角卡(40,40,240,160)" color="{TEXT_MED}" fontSize="12"/>')
        dsl_parts.append(f'              <Text text="卡内文字SHARP/BLUR模糊" color="{TEXT_DARK}" fontSize="12"/>')
    elif idx == 4:
        dsl_parts.append(f'              <Text text="滤色#F6B94A+高斯模糊sigma=6" color="{TEXT_MED}" fontSize="12"/>')
        dsl_parts.append(f'              <Text text="含透明间隙+深色矩形+阴影" color="{TEXT_DARK}" fontSize="12"/>')
    elif idx == 5:
        dsl_parts.append(f'              <Text text="滤色#F6B94A+模糊+圆形裁剪" color="{TEXT_MED}" fontSize="12"/>')
        dsl_parts.append(f'              <Text text="圆心(160,120)半径100" color="{TEXT_DARK}" fontSize="12"/>')
    dsl_parts.append(f'            </Column>')
    dsl_parts.append(f'          </Positioned>')
    dsl_parts.append(f'        </Stack>')
    dsl_parts.append(f'      </Container>')
    dsl_parts.append(f'    </Positioned>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A10/compositing-lab.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')

# Save audit JSON
import json
audit = {
    "schema_version": 1,
    "task_id": "A10",
    "path_base": "output_dir",
    "experiments": [
        {"id": "①", "title": "红蓝50%alpha重叠", "sample_point": [180, 100], "theoretical_rgb": [64, 64, 128]},
        {"id": "②", "title": "不透明红蓝+Opacity(0.5)", "sample_point": [180, 100], "theoretical_rgb": [128, 128, 255]},
        {"id": "③", "title": "背景模糊", "sigma": 6},
        {"id": "④", "title": "子树模糊", "sigma": 6},
        {"id": "⑤", "title": "MULTIPLY+模糊", "filter_color": "#F6B94A", "sigma": 6},
        {"id": "⑥", "title": "MULTIPLY+模糊+圆形裁剪", "filter_color": "#F6B94A", "sigma": 6, "clip_center": [160, 120], "clip_radius": 100}
    ]
}

output_dir = Path('outputs/20261011-suite/A10')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'composite-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved composite-audit.json')
