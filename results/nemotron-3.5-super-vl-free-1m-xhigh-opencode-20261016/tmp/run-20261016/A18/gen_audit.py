import math, json

W, H = 1600, 1000
C_BLUE = "#2563EB"
C_ORANGE = "#F59E0B"
C_GRAY = "#9CA3AF"
C_NODE = "#1E293B"
DOT_R = 18
NODE_R = 22

def circle_points(cx, cy, r, n, start_angle=0):
    pts = []
    for i in range(n):
        ang = math.radians(start_angle + i * 360.0 / n)
        x = cx + r * math.cos(ang)
        y = cy - r * math.sin(ang)
        pts.append((round(x, 1), round(y, 1)))
    return pts

# Scene 1: center N02 at (266, 500), 15 units around radius 115
cx1, cy1 = 266, 500
s1 = circle_points(cx1, cy1, 115, 15)
c1 = ["#2563EB"]*5 + ["#F59E0B"]*5 + ["#9CA3AF"]*5

# Scene 2: center N02 at (796, 500), 15 units clustered radius 55-75
cx2, cy2 = 796, 500
s2 = circle_points(cx2, cy2, 55, 15)
colors2 = ["#2563EB"]*5 + ["#F59E0B"]*5 + ["#9CA3AF"]*5

# Scene 3: 3 nodes
cx3a, cy3a = 1180, 350
cx3b, cy3b = 1333, 500
cx3c, cy3c = 1480, 700
p3a = circle_points(cx3a, cy3a, 60, 5)
p3b = circle_points(cx3b, cy3b, 60, 5, start_angle=72)
p3c = circle_points(cx3c, cy3c, 60, 5, start_angle=0)
c3a = ["#2563EB", "#2563EB", "#2563EB", "#F59E0B", "#F59E0B"]
c3b = ["#2563EB", "#2563EB", "#F59E0B", "#F59E0B", "#9CA3AF"]
c3c = ["#F59E0B", "#9CA3AF", "#9CA3AF", "#9CA3AF", "#9CA3AF"]

all_units = []
for i, (px, py) in enumerate(s1):
    all_units.append({
        "id": f"U{i+1:02d}",
        "color": c1[i],
        "scene": 1,
        "position": [round(px, 1), round(py, 1)],
        "receiving_node": "N02"
    })
for i, (px, py) in enumerate(s2):
    all_units.append({
        "id": f"U{i+1:02d}",
        "color": colors2[i],
        "scene": 2,
        "position": [round(px, 1), round(py, 1)],
        "receiving_node": "N02"
    })
uid = 0
for pts, cols, nid in [(p3a, c3a, "N01"), (p3b, c3b, "N02"), (p3c, c3c, "N03")]:
    for i, (px, py) in enumerate(pts):
        uid += 1
        all_units.append({
            "id": f"U{uid:02d}",
            "color": cols[i],
            "scene": 3,
            "position": [round(px, 1), round(py, 1)],
            "receiving_node": nid
        })

audit = {
    "schema_version": 1,
    "task_id": "A18",
    "path_base": "output_dir",
    "canvas": {"width": W, "height": H},
    "units_meta": {
        "unit_count": 15,
        "unit_radius": DOT_R,
        "node_radius": NODE_R,
        "colors": {"blue": "#2563EB", "orange": "#F59E0B", "gray": "#9CA3AF"}
    },
    "nodes": [
        {"id": "N01", "color": "#1E293B", "radius": NODE_R, "positions": {"scene_1": [266, 500], "scene_2": [796, 500], "scene_3": [1180, 350]}},
        {"id": "N02", "color": "#1E293B", "radius": NODE_R, "positions": {"scene_1": [266, 500], "scene_2": [796, 500], "scene_3": [1333, 500]}},
        {"id": "N03", "color": "#1E293B", "radius": NODE_R, "positions": {"scene_1": [266, 500], "scene_2": [796, 500], "scene_3": [1480, 700]}}
    ],
    "units": all_units,
    "conclusion": {
        "summary": "第一幕15个单元围绕中心节点N02呈放射状分布，呈集中状态；第二幕同15个单元聚集于节点N02周围，形成过载；第三幕重新分配至3个节点，各节点承接5个单元且包含至少两种颜色。",
        "highlight": "第四幕/第三幕各节点负载均衡，每节点承载5个单元且颜色多样，体现负载重新分配。"
    }
}

with open("outputs/run-20261016/A18/story-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print("story-audit.json written with", len(all_units), "units")
