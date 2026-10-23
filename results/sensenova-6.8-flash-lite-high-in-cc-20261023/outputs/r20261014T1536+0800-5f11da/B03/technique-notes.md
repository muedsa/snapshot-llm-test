# B03 技法笔记

## 1. 星图技法（Star Atlas）

### 核心算法
```python
# 背景星生成
for _ in range(300):
    x = random.randint(0, W)
    y = random.randint(0, H)
    size = random.choice([1, 1.5, 2, 2.5, 3])
    doc.circle(x, y, size, "#FFFFFF", step=1)

# 星座连线
constellation_points = [(x1, y1), (x2, y2), ...]
doc.stroke(constellation_points, "#4DABF7", width=2, step=2)
```

### 关键参数
- 背景星数量：300
- 星大小：1-3px
- 星座连线宽度：2px

---

## 2. 数据马赛克技法（Data Mosaic）

### 高斯密度模型
```python
def density_at(col, row):
    # 多个高斯中心叠加
    density = 1.0 * exp(-((col-cx1)**2 + (row-cy1)**2) / 80)
    density += 0.7 * exp(-((col-cx2)**2 + (row-cy2)**2) / 60)
    density += 0.8 * exp(-((col-cx3)**2 + (row-cy3)**2) / 70)
    return density
```

### 关键参数
- 网格：40×30
- 高斯中心：3个
- 颜色梯度：6级

---

## 3. 波形合成技法（Wave Synthesis）

### 正弦波叠加
```python
for w in range(6):
    for x in range(0, W, 15):
        y = center_y + amplitude[w] * sin(freq[w] * x + phase[w])
        points.append((x, y))
    doc.fill(polygon, color + "4D", step=3)
```

### 关键参数
- 波形数：6
- 频率范围：0.015-0.5
- 振幅范围：20-120px
- 采样步长：15px

---

## 4. 极坐标玫瑰技法（Polar Rose）

### 扇形多边形
```python
polygon = [(cx, cy), (x1, y1)]
for i in range(arc_steps):
    angle = start + span * (i / steps)
    polygon.append((cx + r * cos(angle), cy + r * sin(angle)))
polygon.append((x2, y2))
doc.fill(polygon, color, step=3)
```

### 关键参数
- 类别数：7
- 最大半径：450px
- 弧线步长：max(10, span*50)

---

## 5. 分形树技法（Fractal Tree）

### 递归算法
```python
def fractal_tree(x, y, length, angle, depth, max_depth, branches):
    if depth > max_depth or length < 2:
        return
    x2 = x + length * cos(angle)
    y2 = y + length * sin(angle)
    doc.stroke([(x, y), (x2, y2)], color, width, step=5)
    fractal_tree(x2, y2, length*ratio, angle-angle_step, depth+1, ...)
    fractal_tree(x2, y2, length*ratio, angle+angle_step, depth+1, ...)
```

### 关键参数
- 最大深度：7
- 分叉角度：23° (0.4 rad)
- 衰减比例：0.72
- 线段步长：5

---

## 6. 万花筒技法（Kaleidoscope）

### 旋转对称
```python
for seg in range(8):
    angle = seg * (360 / 8)
    rad = math.radians(angle)
    # 三角形
    tri_pts = [
        (cx + r * cos(rad), cy + r * sin(rad)),
        (cx + r2 * cos(rad + 0.5), cy + r2 * sin(rad + 0.5)),
        (cx + r2 * cos(rad - 0.5), cy + r2 * sin(rad - 0.5)),
    ]
    doc.fill(tri_pts, color + "66", step=3)
```

### 关键参数
- 对称数：8
- 几何层级：4种（三角形、菱形、圆点、装饰圆）
- 颜色数：8

---

## 7. 粒子网络技法（Particle Network）

### 距离衰减连线
```python
for n1 in nodes:
    for n2 in nodes:
        dist = sqrt((n1.x-n2.x)**2 + (n1.y-n2.y)**2)
        if dist < threshold:
            alpha = max(20, 60 - dist * 0.3)
            doc.stroke([(n1.x,n1.y), (n2.x,n2.y)], color + alpha, width=1, step=3)
```

### 关键参数
- 节点数：60（4集群×15）
- 集群内阈值：120px
- 集群间阈值：200px
- 节点大小：8-14px

---

## 8. 时间螺旋技法（Time Spiral）

### 极坐标螺旋
```python
for i in range(num_turns * points_per_turn):
    t = i / (num_turns * points_per_turn)
    angle = t * num_turns * 2 * pi
    r = 80 + t * 450
    x = cx + r * cos(angle)
    y = cy + r * sin(angle)
    points.append((x, y))
```

### 关键参数
- 螺旋圈数：8
- 每圈点数：40
- 初始半径：80px
- 最大半径：530px

---

## 9. 等高线地图技法（Contour Map）

### 高度场生成
```python
def height_at(col, row):
    x = col / cols
    y = row / rows
    h = 0.5 * exp(-((x-0.3)**2 + (y-0.4)**2) / 0.04)
    h += 0.7 * exp(-((x-0.7)**2 + (y-0.6)**2) / 0.03)
    h += 0.4 * exp(-((x-0.5)**2 + (y-0.2)**2) / 0.02)
    return h
```

### 关键参数
- 网格：40×30
- 等高线级别：10级
- 山峰数：4个高斯中心

---

## 10. 极简信息卡技法（Minimal Infocard）

### 字体层级
```python
# 城市名：48px粗体
doc.text(x, y, "上海", 48, "#FFFFFF", bold=True)
# 温度：120px粗体
doc.text_c(cx, cy, "18°", 120, "#FFFFFF", bold=True)
# 详情：32px粗体彩色
doc.text_c(cx, cy, "14°", 32, "#4DABF7", bold=True)
# 标签：14px灰色
doc.text_c(cx, cy, "最低", 14, "#666688")
```

### 关键参数
- 字体层级：4级（12px→48px）
- 颜色数：4种（蓝、红、绿、黄）
- 留白比例：约60%

---

## 通用技巧

### 透明度控制
- **rect**: `opacity` 参数（0-1）
- **circle/fill/stroke**: hex alpha 后缀（如 `#FF6B6B66`）
- **必须clamp**: `min(1.0, opacity_value)`

### Parts数量控制
- **step参数**：step=1生成最多parts，step=3-5减少
- **采样点**：减少points数量
- **递归深度**：控制分形树深度

### 文字重叠预防
```python
# 计算文字高度
pitch = fs * 1.2
# 下一个文字y必须 > 当前y + pitch
next_y = current_y + pitch + gap
```
