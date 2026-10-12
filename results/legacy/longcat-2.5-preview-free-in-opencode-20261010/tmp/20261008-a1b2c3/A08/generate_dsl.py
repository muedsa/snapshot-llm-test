#!/usr/bin/env python3
"""A08 - 网格导览与两条可走路线 DSL 生成器"""
import json
from pathlib import Path
from collections import deque

# 读取地图
floor_text = """##########################
#.......#........#.......#
#.S.....#........#.......#
#.......#...B....#.......#
#................#.......#
#.......#........#.......#
#...A...#........#....C..#
#.......#................#
#.......#........#.......#
###.########.#########.###
#.......#........#.......#
#.......#........#.......#
#................#.......#
#.......#...D....#.......#
#.......#................#
#.......#........#.....E.#
#.......#........#.......#
##########################"""

grid = [list(row) for row in floor_text.strip().split('\n')]
rows = len(grid)
cols = len(grid[0])

# 找到特殊位置
special = {}
for y in range(rows):
    for x in range(cols):
        c = grid[y][x]
        if c in 'SEABCD':
            special[c] = (x, y)

# BFS求最短路径
def bfs(start, end):
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return path
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visited:
                if grid[ny][nx] != '#':
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    
    return None

# 路线一：S→E
path1 = bfs(special['S'], special['E'])

# 路线二：S→B→D→E
path2a = bfs(special['S'], special['B'])
path2b = bfs(special['B'], special['D'])
path2c = bfs(special['D'], special['E'])
path2 = path2a + path2b[1:] + path2c[1:]

# 保存paths.json
paths_data = {
    "grid_size": {"cols": cols, "rows": rows},
    "cell_meters": 2,
    "path1": {
        "description": "S→E最短",
        "steps": len(path1) - 1,
        "meters": (len(path1) - 1) * 2,
        "path": path1
    },
    "path2": {
        "description": "S→B→D→E最短",
        "steps": len(path2) - 1,
        "meters": (len(path2) - 1) * 2,
        "path": path2,
        "segments": {
            "S→B": {"steps": len(path2a) - 1, "meters": (len(path2a) - 1) * 2},
            "B→D": {"steps": len(path2b) - 1, "meters": (len(path2b) - 1) * 2},
            "D→E": {"steps": len(path2c) - 1, "meters": (len(path2c) - 1) * 2}
        }
    },
    "special_positions": special
}

output_dir = Path("outputs/20261008-a1b2c3/A08")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "paths.json", "w", encoding="utf-8") as f:
    json.dump(paths_data, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_WALL = "#334155"
COLOR_PATH = "#1E293B"
COLOR_ROUTE1 = "#EF4444"
COLOR_ROUTE2 = "#3B82F6"
COLOR_SPECIAL = "#F59E0B"

# 网格参数
cell_size = 40
grid_width = cols * cell_size
grid_height = rows * cell_size
offset_x = 80
offset_y = 80

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1560" height="1080" padding="(20,24)">')
lines.append(f'    <Row crossAxisAlignment="START">')
lines.append(f'      <!-- 网格地图 -->')
lines.append(f'      <Container width="{grid_width + 100}" height="{grid_height + 100}" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(40,40)">')
lines.append(f'        <Stack>')

# 绘制网格
for y in range(rows):
    for x in range(cols):
        c = grid[y][x]
        px = offset_x + x * cell_size
        py = offset_y + y * cell_size
        if c == '#':
            lines.append(f'          <Positioned left="{px}" top="{py}" width="{cell_size}" height="{cell_size}">')
            lines.append(f'            <Container width="{cell_size}" height="{cell_size}" color="{COLOR_WALL}"/>')
            lines.append(f'          </Positioned>')
        else:
            lines.append(f'          <Positioned left="{px}" top="{py}" width="{cell_size}" height="{cell_size}">')
            lines.append(f'            <Container width="{cell_size}" height="{cell_size}" color="{COLOR_PATH}" border="1 SOLID {CARD_BORDER}"/>')
            lines.append(f'          </Positioned>')

# 绘制路线一（红色）
for i in range(len(path1) - 1):
    x1, y1 = path1[i]
    x2, y2 = path1[i + 1]
    px1 = offset_x + x1 * cell_size + cell_size // 2
    py1 = offset_y + y1 * cell_size + cell_size // 2
    px2 = offset_x + x2 * cell_size + cell_size // 2
    py2 = offset_y + y2 * cell_size + cell_size // 2
    lines.append(f'          <Positioned left="{px1}" top="{py1}" width="{abs(px2-px1) or 4}" height="{abs(py2-py1) or 4}">')
    lines.append(f'            <Container width="{abs(px2-px1) or 4}" height="{abs(py2-py1) or 4}" color="{COLOR_ROUTE1}"/>')
    lines.append(f'          </Positioned>')

# 绘制路线二（蓝色）
for i in range(len(path2) - 1):
    x1, y1 = path2[i]
    x2, y2 = path2[i + 1]
    px1 = offset_x + x1 * cell_size + cell_size // 2
    py1 = offset_y + y1 * cell_size + cell_size // 2
    px2 = offset_x + x2 * cell_size + cell_size // 2
    py2 = offset_y + y2 * cell_size + cell_size // 2
    lines.append(f'          <Positioned left="{px1}" top="{py1}" width="{abs(px2-px1) or 4}" height="{abs(py2-py1) or 4}">')
    lines.append(f'            <Container width="{abs(px2-px1) or 4}" height="{abs(py2-py1) or 4}" color="{COLOR_ROUTE2}"/>')
    lines.append(f'          </Positioned>')

# 绘制特殊位置
for c, (x, y) in special.items():
    px = offset_x + x * cell_size + cell_size // 2
    py = offset_y + y * cell_size + cell_size // 2
    lines.append(f'          <Positioned left="{px}" top="{py}" width="30" height="30">')
    lines.append(f'            <Container width="30" height="30" color="{COLOR_SPECIAL}" borderRadius="15">')
    lines.append(f'              <Text color="#000000" fontSize="16" fontStyle="BOLD" textAlign="CENTER">{c}</Text>')
    lines.append(f'            </Container>')
    lines.append(f'          </Positioned>')

lines.append(f'        </Stack>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <!-- 侧栏 -->')
lines.append(f'      <Container width="300" height="{grid_height + 100}" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(16,20)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">展馆导览</Text>')
lines.append(f'          <SizedBox height="12"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="14">路线一：S→E最短</Text>')
lines.append(f'          <Text color="{COLOR_ROUTE1}" fontSize="14">{len(path1)-1}步 · {(len(path1)-1)*2}米</Text>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="14">路线二：S→B→D→E最短</Text>')
lines.append(f'          <Text color="{COLOR_ROUTE2}" fontSize="14">{len(path2)-1}步 · {(len(path2)-1)*2}米</Text>')
lines.append(f'          <SizedBox height="12"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">图例：</Text>')
lines.append(f'          <Text color="{COLOR_ROUTE1}" fontSize="12">■ 路线一</Text>')
lines.append(f'          <Text color="{COLOR_ROUTE2}" fontSize="12">■ 路线二</Text>')
lines.append(f'          <Text color="{COLOR_SPECIAL}" fontSize="12">● 展区/出入口</Text>')
lines.append(f'          <SizedBox height="12"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">尺度：每格2米</Text>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">坐标：(x,y)从0开始</Text>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'    </Row>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "wayfinding.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
print(f"Path1: {len(path1)-1} steps, {(len(path1)-1)*2} meters")
print(f"Path2: {len(path2)-1} steps, {(len(path2)-1)*2} meters")
