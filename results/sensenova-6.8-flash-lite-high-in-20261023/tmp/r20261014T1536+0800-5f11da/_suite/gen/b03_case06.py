"""B03 case-06: 万花筒（Kaleidoscope）- 对称图案设计
用对称重复的几何图形组成万花筒效果。
场景：艺术展览海报，展示对称美学。
技术：旋转对称，颜色渐变，几何重复。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 参数
cx, cy = W // 2, H // 2
num_segments = 8
colors = ["#FF6B6B", "#FFA94D", "#FFD93D", "#69DB7C", "#4DABF7", "#9775FA", "#F06595", "#63E6BE"]

# ============================================================ 背景光晕
for i in range(8, 0, -1):
    doc.rect(cx - i * 80, cy - i * 80, i * 160, i * 160,
             "#1a237e", radius=i * 80, opacity=0.02 * i)

# ============================================================ 绘制万花筒
# 每个段绘制一组形状
for seg in range(num_segments):
    angle = seg * (360 / num_segments)
    rad = math.radians(angle)
    color = colors[seg]

    # 三角形
    tri_r = 200
    tri_pts = [
        (cx + tri_r * math.cos(rad), cy + tri_r * math.sin(rad)),
        (cx + 150 * math.cos(rad + 0.5), cy + 150 * math.sin(rad + 0.5)),
        (cx + 150 * math.cos(rad - 0.5), cy + 150 * math.sin(rad - 0.5)),
    ]
    doc.fill(tri_pts, color + "66", step=3)

    # 菱形
    dia_r = 280
    dia_pts = [
        (cx + dia_r * math.cos(rad), cy + dia_r * math.sin(rad)),
        (cx + 120 * math.cos(rad + 0.8), cy + 120 * math.sin(rad + 0.8)),
        (cx + 180 * math.cos(rad), cy + 180 * math.sin(rad)),
        (cx + 120 * math.cos(rad - 0.8), cy + 120 * math.sin(rad - 0.8)),
    ]
    doc.fill(dia_pts, color + "44", step=3)

    # 圆点
    dot_r = 350
    doc.rect(cx + dot_r * math.cos(rad) - 15, cy + dot_r * math.sin(rad) - 15,
             30, 30, color, radius=15, opacity=0.7)

    # 小装饰圆
    for r in [100, 220, 320]:
        doc.rect(cx + r * math.cos(rad) - 8, cy + r * math.sin(rad) - 8,
                 16, 16, color, radius=8, opacity=0.5)

# ============================================================ 中心圆
doc.rect(cx - 50, cy - 50, 100, 100, "#1a1a3a", radius=50)
doc.rect(cx - 30, cy - 30, 60, 60, "#FFD700", radius=30, opacity=0.8)
doc.circle(cx, cy, 15, "#FFFFFF", step=1)

# ============================================================ 标题
doc.text(80, 40, "万花筒 · KALEIDOSCOPE", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "对称美学的无限变化 · Infinite Variations of Symmetry", 16, "#8888aa", owner="subtitle")

# ============================================================ 底部信息
doc.line_h(80, W - 80, H - 40, "#333355", 1)
doc.text(80, H - 30, "8重对称 · 无限变化", 14, "#8888aa", owner="info")
doc.text_r(W - 80, H - 30, "© 2026 艺术展览项目", 12, "#666688", owner="footer")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-06", 12, [], max_parts=9000)
K.save_gates("case-06", gates, "初始版本")
K.assert_gates(gates, "case-06")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-06", doc, "万花筒", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
