"""B03 case-07: 粒子网络（Particle Network）- 节点关系可视化
用节点和连线展示网络关系，不同颜色代表不同集群。
场景：社交网络分析、知识图谱、组织架构可视化。
技术：节点定位算法，距离衰减连线，集群着色。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1600, 1200
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 节点数据
random.seed(42)

# 4个集群，每个集群中心不同
clusters = [
    {"cx": 400, "cy": 400, "color": "#FF6B6B", "name": "技术团队"},
    {"cx": 1200, "cy": 400, "color": "#4DABF7", "name": "设计团队"},
    {"cx": 400, "cy": 900, "color": "#69DB7C", "name": "产品团队"},
    {"cx": 1200, "cy": 900, "color": "#FFD93D", "name": "运营团队"},
]

nodes = []
node_id = 0
for ci, c in enumerate(clusters):
    # 每个集群15个节点
    for i in range(15):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 150)
        x = c["cx"] + r * math.cos(angle)
        y = c["cy"] + r * math.sin(angle)
        size = random.choice([8, 10, 12, 14])
        nodes.append({"id": node_id, "x": x, "y": y, "size": size, "cluster": ci})
        node_id += 1

# ============================================================ 背景
for i in range(6, 0, -1):
    doc.rect(W // 2 - i * 100, H // 2 - i * 100, i * 200, i * 200,
             "#1a1a3a", radius=i * 100, opacity=0.02 * i)

# ============================================================ 绘制连线
# 集群内连线
for ci, c in enumerate(clusters):
    cluster_nodes = [n for n in nodes if n["cluster"] == ci]
    for i, n1 in enumerate(cluster_nodes):
        for n2 in cluster_nodes[i+1:]:
            dist = math.sqrt((n1["x"]-n2["x"])**2 + (n1["y"]-n2["y"])**2)
            if dist < 120:
                alpha = int(60 - dist * 0.3)
                alpha = max(20, min(60, alpha))
                color = c["color"] + format(alpha, '02x')
                doc.stroke([(n1["x"], n1["y"]), (n2["x"], n2["y"])], color, width=1, step=3)

# 集群间连线（少量）
for i, n1 in enumerate(nodes):
    for n2 in nodes[i+1:]:
        if n1["cluster"] != n2["cluster"]:
            dist = math.sqrt((n1["x"]-n2["x"])**2 + (n1["y"]-n2["y"])**2)
            if dist < 200:
                doc.stroke([(n1["x"], n1["y"]), (n2["x"], n2["y"])], "#66668888", width=1, step=5)

# ============================================================ 绘制节点
for n in nodes:
    c = clusters[n["cluster"]]
    # 光晕
    doc.rect(n["x"] - n["size"] - 4, n["y"] - n["size"] - 4,
             (n["size"] + 4) * 2, (n["size"] + 4) * 2,
             c["color"], radius=n["size"] + 4, opacity=0.2)
    # 主节点
    doc.rect(n["x"] - n["size"], n["y"] - n["size"],
             n["size"] * 2, n["size"] * 2,
             c["color"], radius=n["size"], opacity=0.8)

# ============================================================ 标题
doc.text(80, 40, "粒子网络 · PARTICLE NETWORK", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "知识图谱关系可视化 · Knowledge Graph Visualization", 16, "#8888aa", owner="subtitle")

# ============================================================ 图例
legend_x, legend_y = 1300, 40
doc.text(legend_x, legend_y, "集群", 14, "#FFFFFF", bold=True, owner="legend_title")
for i, c in enumerate(clusters):
    ly = legend_y + 25 + i * 28
    doc.rect(legend_x, ly, 14, 14, c["color"], radius=7, opacity=0.8)
    doc.text(legend_x + 22, ly - 1, f"{c['name']} (15)", 12, "#CCCCCC", owner="leg_item")

# ============================================================ 统计
stats_y = H - 50
doc.text(80, stats_y, f"节点: {len(nodes)} · 集群: 4 · 连接: 280+", 12, "#666688", owner="stats")
doc.text_r(W - 80, stats_y, "© 2026 知识图谱项目", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-07", 12, [], max_parts=9000)
K.save_gates("case-07", gates, "初始版本")
K.assert_gates(gates, "case-07")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-07", doc, "粒子网络", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
