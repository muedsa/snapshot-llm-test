"""B04 case-04: 行星质量比较（Planetary Mass Comparison）
用对数尺度展示八大行星的质量，突出木星和土星的巨大质量。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（质量单位：10^24 kg）
planets = [
    ("Mercury", "水星", 0.330, "#B8860B"),
    ("Venus", "金星", 4.87, "#FF8C00"),
    ("Earth", "地球", 5.97, "#4169E1"),
    ("Mars", "火星", 0.642, "#CD5C5C"),
    ("Jupiter", "木星", 1898, "#DEB887"),
    ("Saturn", "土星", 568, "#F4A460"),
    ("Uranus", "天王星", 86.8, "#87CEEB"),
    ("Neptune", "海王星", 102, "#4169E1"),
]

# ============================================================ 标题
doc.text(80, 40, "行星质量比较 · PLANETARY MASS COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星质量可视化（对数尺度）· Mass Comparison on Log Scale", 16, "#8888aa", owner="subtitle")

# ============================================================ 绘制质量球
# 使用对数尺度：r = 20 * log10(mass + 1) + 10
cx_start = 200
cy_start = 300

for i, (name, name_cn, mass, color) in enumerate(planets):
    row = i // 4
    col = i % 4
    cx = cx_start + col * 280
    cy = cy_start + row * 400

    # 球体半径（对数尺度）
    r = 20 * math.log10(mass + 1) + 15
    r = max(10, min(80, r))

    # 光晕
    doc.rect(cx - r - 5, cy - r - 5, (r + 5) * 2, (r + 5) * 2, color, radius=r + 5, opacity=0.2)

    # 主球体
    doc.rect(cx - r, cy - r, r * 2, r * 2, color, radius=r, opacity=0.8)

    # 名称
    doc.text_c(cx, cy + r + 20, name_cn, 18, color, bold=True, owner="name")

    # 质量值
    doc.text_c(cx, cy + r + 48, f"{mass} × 10²⁴ kg", 14, "#CCCCCC", owner="mass")

    # 地球倍数
    earth_ratio = mass / 5.97
    if earth_ratio >= 100:
        ratio_str = f"{int(earth_ratio)}× 地球"
    elif earth_ratio >= 1:
        ratio_str = f"{earth_ratio:.1f}× 地球"
    else:
        ratio_str = f"{earth_ratio:.2f}× 地球"
    doc.text_c(cx, cy + r + 72, ratio_str, 12, "#8888aa", owner="ratio")

# ============================================================ 说明
doc.line_h(80, W - 80, H - 150, "#333355", 1)
doc.text(80, H - 130, "木星质量是地球的318倍，是其他七颗行星总和的2.5倍", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 105, "土星质量是地球的95倍，但密度仅为地球的0.124倍", 14, "#CCCCCC", owner="fact2")
doc.text(80, H - 80, "水星质量仅为地球的0.055倍，是质量最小的行星", 14, "#CCCCCC", owner="fact3")
doc.text_r(W - 80, H - 80, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 55, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-04", 12, [], max_parts=9000)
K.save_gates("case-04", gates, "初始版本")
K.assert_gates(gates, "case-04")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-04", doc, "行星质量比较", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
