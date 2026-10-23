"""B03 case-03: 波形合成（Wave Synthesis）- 音乐可视化
用多条正弦波叠加展示音频频谱，不同频率用不同颜色。
场景：音乐节海报，展示歌曲的频谱分析。
技术：程序化波形生成，频率叠加，颜色编码。
用fill绘制波形填充区域，控制parts数量。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1600, 900
doc = K.Doc(W, H, "#0a0a1a")

# ============================================================ 波形数据
num_waves = 6
wave_colors = ["#FF6B6B", "#FFA94D", "#69DB7C", "#4DABF7", "#9775FA", "#63E6BE"]
amplitudes = [120, 80, 60, 40, 30, 20]
frequencies = [0.015, 0.03, 0.06, 0.12, 0.25, 0.5]
phases = [0, 0.5, 1.0, 1.5, 2.0, 2.5]

# ============================================================ 背景光晕
for i in range(8, 0, -1):
    doc.rect(W // 2 - i * 100, H // 2 - i * 40, i * 200, i * 80,
             "#1a1a3a", radius=i * 40, opacity=0.02 * i)

# ============================================================ 绘制波形（用fill填充区域）
center_y = H // 2
step_x = 15  # 每15像素一个采样点

for w in range(num_waves):
    color = wave_colors[w]
    amp = amplitudes[w]
    freq = frequencies[w]
    phase = phases[w]

    # 生成波形路径
    wave_points = []
    for x in range(0, W + 1, step_x):
        y = center_y + amp * math.sin(freq * x + phase)
        wave_points.append((x, y))

    # 构建闭合多边形（波形上边界 + 基线返回）
    polygon = wave_points[:]
    polygon.extend([(W, center_y), (0, center_y)])

    # 用fill绘制波形区域，用半透明色模拟opacity
    doc.fill(polygon, color + "4D", step=3)  # 30% opacity via hex alpha

    # 在波峰添加光点
    for x in range(0, W, 50):
        y = center_y + amp * math.sin(freq * x + phase)
        if abs(math.sin(freq * x + phase)) > 0.8:
            doc.rect(x - 4, y - 4, 8, 8, color, radius=4, opacity=0.6)

# ============================================================ 频谱条
bar_start_y = H - 180
bar_height = 130
num_bars = 48
bar_width = W / num_bars - 2

for i in range(num_bars):
    x = i * (bar_width + 2)
    freq_factor = (i / num_bars) ** 1.5
    height = bar_height * (0.3 + 0.7 * (1 - freq_factor))
    height *= (0.7 + 0.3 * math.sin(i * 0.3 + 1))
    y = bar_start_y + bar_height - height
    color_idx = i // 8
    if color_idx >= len(wave_colors):
        color_idx = len(wave_colors) - 1
    doc.rect(x, y, bar_width, height, wave_colors[color_idx], radius=2, opacity=0.8)

# ============================================================ 标题
doc.text(80, 40, "波形合成 · WAVE SYNTHESIS", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "音频频谱可视化 · Audio Spectrum Visualization", 16, "#8888aa", owner="subtitle")

# ============================================================ 图例
legend_x = 1100
doc.text(legend_x, 40, "频率", 16, "#FFFFFF", bold=True, owner="legend_title")
for i, (color, label) in enumerate(zip(wave_colors[:4], ["低频", "中低频", "中高频", "高频"])):
    doc.rect(legend_x + i * 100, 70, 20, 4, color, radius=2)
    doc.text(legend_x + i * 100 + 25, 65, label, 12, "#CCCCCC", owner="freq_label")

# ============================================================ 底部信息
doc.text(80, H - 30, "采样率: 44.1kHz · 位深: 16bit", 12, "#666688", owner="audio_info")
doc.text_r(W - 80, H - 30, "© 2026 音乐可视化项目", 12, "#666688", owner="footer")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-03", 12, [], max_parts=9000)
K.save_gates("case-03", gates, "初始版本")
K.assert_gates(gates, "case-03")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-03", doc, "波形合成", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
