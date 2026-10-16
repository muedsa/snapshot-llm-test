import json, math, os

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_DIR = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A20")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A20")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
CANVAS_W, CANVAS_H = 1600, 1100

MAP_LEFT, MAP_TOP = 280, 160
MAP_W, MAP_H = 1040, 760

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

with open(os.path.join(SUITE_ROOT, "tasks", "A20-dense-annotation", "inputs", "markers.json"), "r", encoding="utf-8") as f:
    markers = json.load(f)

def px_of(x): return MAP_LEFT + 10.4 * x
def py_of(y): return 920.0 - 7.6 * y

for m in markers:
    m["px"] = px_of(m["x"])
    m["py"] = py_of(m["y"])
    m["r"] = 6.0

DENSE_IDS = {"M06", "M08", "M09", "M10", "M11", "M12"}
for m in markers:
    if m["id"] in DENSE_IDS:
        m["r"] = 4.0

top3 = sorted(markers, key=lambda m: (-m["value"], m["id"]))[:3]
top3_ids = {m["id"] for m in top3}

FONT = "Noto Sans CJK SC,Inter"

LABEL_W, LABEL_H = 190, 45
LABEL_PAD = 8

label_assignments = [
    ("M03",  40,  190, "left"),
    ("M01",  40,  242, "left"),
    ("M02",  40,  294, "left"),
    ("M24",  40,  346, "left"),
    ("M14",  40,  398, "left"),
    ("M15",  40,  450, "left"),
    ("M16",  40,  502, "left"),
    ("M04", 1340,  180, "right"),
    ("M05", 1340,  232, "right"),
    ("M07", 1340,  284, "right"),
    ("M13", 1340,  336, "right"),
    ("M17", 1340,  388, "right"),
    ("M20", 1340,  440, "right"),
    ("M21", 1340,  492, "right"),
    ("M22", 1340,  544, "right"),
    ("M18", 1340,  596, "right"),
    ("M19", 1340,  648, "right"),
    ("M06", 1340,  700, "right"),
    ("M08", 1340,  752, "right"),
    ("M09", 1340,  804, "right"),
    ("M10", 1340,  856, "right"),
    ("M11", 1340,  908, "right"),
    ("M12", 1340,  960, "right"),
    ("M23", 1340, 1012, "right"),
]

label_map = {m["id"]: m for m in markers}
label_layout = []
for mid, lx, lty, side in label_assignments:
    m = label_map[mid]
    label_layout.append({
        "marker_id": mid,
        "name": m["name"],
        "value": m["value"],
        "logic_x": m["x"],
        "logic_y": m["y"],
        "anchor_px": round(m["px"], 3),
        "anchor_py": round(m["py"], 3),
        "anchor_r": m["r"],
        "label_box": [lx, lty, lx + LABEL_W, lty + LABEL_H],
        "label_side": side,
        "needs_leader": True,
    })

def point_on_circle(cx, cy, r, angle_deg):
    a = math.radians(angle_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)

def nearest_box_point(box, px, py):
    l, t, rb, b = box
    nx = max(l, min(px, rb))
    ny = max(t, min(py, b))
    return nx, ny

def leader_endpoints(m, box, side):
    cx, cy, r = m["px"], m["py"], m["r"]
    l, t, rb, b = box
    box_cx = (l + rb) / 2
    box_cy = (t + b) / 2
    dx = box_cx - cx
    dy = box_cy - cy
    angle = math.degrees(math.atan2(dy, dx))
    sx, sy = point_on_circle(cx, cy, r, angle)
    ex, ey = nearest_box_point(box, cx, cy)
    if l <= cx <= rb and t <= cy <= b:
        ex, ey = nearest_box_point(box, sx, sy)
    return (round(sx, 3), round(sy, 3)), (round(ex, 3), round(ey, 3))

for entry in label_layout:
    m = label_map[entry["marker_id"]]
    box = entry["label_box"]
    start, end = leader_endpoints(m, box, entry["label_side"])
    entry["leader_start"] = list(start)
    entry["leader_end"] = list(end)
    cx, cy = m["px"], m["py"]
    l, t, rb, b = box
    nx = max(l, min(cx, rb))
    ny = max(t, min(cy, n)) if False else max(t, min(cy, b))
    dist = math.hypot(cx - nx, cy - ny)
    entry["anchor_to_box_dist"] = round(dist, 3)

dsl_lines = []
dsl_lines.append('<Snapshot type="png">')
dsl_lines.append('  <SizedBox width="1600" height="1100">')
dsl_lines.append('    <Stack alignment="TOP_LEFT">')
dsl_lines.append('      <Container color="#FAFBFC" width="1600" height="1100"/>')

# 主图区边框
dsl_lines.append('      <Container color="#FFFFFF" border="1 SOLID #94A3B8" borderRadius="6" left="280" top="160" width="1040" height="760"/>')

# 坐标轴 - X轴底部
dsl_lines.append('      <Container color="#334155" left="280" top="919" width="1040" height="1"/>')
# 坐标轴 - Y轴左侧
dsl_lines.append('      <Container color="#334155" left="279" top="160" width="1" height="760"/>')

# X轴刻度 (0, 25, 50, 75, 100)
for vx in [0, 25, 50, 75, 100]:
    px = px_of(vx)
    dsl_lines.append('      <Container color="#334155" left="' + str(round(px-0.5,2)) + '" top="918" width="1" height="4"/>')
    dsl_lines.append('      <Text left="' + str(round(px-10,2)) + '" top="926" fontSize="14" fill="#64748B" fontFamily="' + FONT + '">' + str(vx) + '</Text>')

# Y轴刻度
for vy in [0, 25, 50, 75, 100]:
    py = py_of(vy)
    dsl_lines.append('      <Container color="#334155" left="278" top="' + str(round(py-0.5,2)) + '" width="4" height="1"/>')
    dsl_lines.append('      <Text left="225" top="' + str(round(py-7,2)) + '" fontSize="14" fill="#64748B" fontFamily="' + FONT + '" width="50" textAlign="RIGHT">' + str(vy) + '</Text>')

# 轴标题
dsl_lines.append('      <Text left="770" top="955" fontSize="16" fontStyle="BOLD" fill="#1F293B" fontFamily="' + FONT + '">X / Logic</Text>')
dsl_lines.append('      <Text left="8" top="535" fontSize="16" fontStyle="BOLD" fill="#1F293B" fontFamily="' + FONT + '">Y / Logic</Text>')
dsl_lines.append('      <Text left="1420" top="1055" fontSize="16" fontStyle="BOLD" fill="#1F293B" fontFamily="' + FONT + '">Unit: Index</Text>')

# 24个点
for m in markers:
    color = "#DC2626" if m["id"] in top3_ids else ("#EF4444" if m["id"] in DENSE_IDS else "#2563EB")
    diameter = m["r"] * 2
    left = m["px"] - m["r"]
    top = m["py"] - m["r"]
    dsl_lines.append('      <Container color="' + color + '" borderRadius="' + str(m["r"]) + '" left="' + str(round(left,2)) + '" top="' + str(round(top,2)) + '" width="' + str(diameter) + '" height="' + str(diameter) + '"/>')
    # 点编号
    if m["r"] >= 6:
        dsl_lines.append('      <Text left="' + str(round(m["px"]-4,2)) + '" top="' + str(round(m["py"]-6,2)) + '" fontSize="10" fill="#FFFFFF" fontStyle="BOLD" fontFamily="' + FONT + '">' + m["id"][1:] + '</Text>')
    else:
        dsl_lines.append('      <Text left="' + str(round(m["px"]-3,2)) + '" top="' + str(round(m["py"]-5,2)) + '" fontSize="8" fill="#FFFFFF" fontStyle="BOLD" fontFamily="' + FONT + '">' + m["id"][1:] + '</Text>')

# 引导线 - 阶梯式：水平段 + 垂直段
for entry in label_layout:
    sx, sy = entry["leader_start"]
    ex, ey = entry["leader_end"]
    side = entry["label_side"]
    # 从点出发，先水平到标签x边缘，再垂直到标签y边缘
    if side == "left":
        # 点在右，标签在左：从点左边缘水平到标签右边缘，再垂直
        mid_x = ex  # 标签盒右边缘
        # 水平段：从 sx 到 mid_x，y=sy
        if abs(sx - mid_x) > 1:
            x1 = min(sx, mid_x); x2 = max(sx, mid_x)
            dsl_lines.append('      <Container color="#94A3B8" left="' + str(round(x1,2)) + '" top="' + str(round(sy-0.5,2)) + '" width="' + str(round(x2-x1,2)) + '" height="1"/>')
        # 垂直段：在 mid_x 处，从 sy 到 ey
        if abs(sy - ey) > 1:
            y1 = min(sy, ey); y2 = max(sy, ey)
            dsl_lines.append('      <Container color="#94A3B8" left="' + str(round(mid_x-0.5,2)) + '" top="' + str(round(y1,2)) + '" width="1" height="' + str(round(y2-y1,2)) + '" />')
    else:
        # 点在左，标签在右：从点右边缘水平到标签左边缘，再垂直
        mid_x = ex  # 标签盒左边缘
        if abs(sx - mid_x) > 1:
            x1 = min(sx, mid_x); x2 = max(sx, mid_x)
            dsl_lines.append('      <Container color="#94A3B8" left="' + str(round(x1,2)) + '" top="' + str(round(sy-0.5,2)) + '" width="' + str(round(x2-x1,2)) + '" height="1"/>')
        if abs(sy - ey) > 1:
            y1 = min(sy, ey); y2 = max(sy, ey)
            dsl_lines.append('      <Container color="#94A3B8" left="' + str(round(mid_x-0.5,2)) + '" top="' + str(round(y1,2)) + '" width="1" height="' + str(round(y2-y1,2)) + '" />')

# 标签盒
for entry in label_layout:
    l, t, rb, b = entry["label_box"]
    mid = entry["marker_id"]
    m = label_map[mid]
    is_top3 = m["id"] in top3_ids
    box_color = "#FEF2F2" if is_top3 else "#FFFFFF"
    border_color = "#DC2626" if is_top3 else "#E2E8F0"
    dsl_lines.append('      <Container color="' + box_color + '" border="1 SOLID ' + border_color + '" borderRadius="6" left="' + str(l) + '" top="' + str(t) + '" width="190" height="45"/>')
    dsl_lines.append('      <Text left="' + str(l+LABEL_PAD) + '" top="' + str(t+LABEL_PAD+2) + '" fontSize="20" fill="#111827" fontStyle="BOLD" fontFamily="' + FONT + '">' + m["id"] + ' ' + m["name"] + '</Text>')
    vcolor = "#DC2626" if is_top3 else "#64748B"
    dsl_lines.append('      <Text left="' + str(l+LABEL_PAD) + '" top="' + str(t+LABEL_PAD+26) + '" fontSize="20" fill="' + vcolor + '" fontStyle="BOLD" fontFamily="' + FONT + '">' + str(m["value"]) + '</Text>')

# 标题
dsl_lines.append('      <Text left="40" top="35" fontSize="32" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">Map: 24 Points No Overlap Labels</Text>')
dsl_lines.append('      <Text left="40" top="70" fontSize="18" fill="#64748B" fontFamily="' + FONT + '">Map area 280,160 w1040 h760  ·  Point dia 12px (dense 8px)  ·  Unit: Index</Text>')

# 图例
legend_x = 40
legend_y = 1010
dsl_lines.append('      <Container color="#2563EB" borderRadius="6" left="' + str(legend_x) + '" top="' + str(legend_y-5) + '" width="12" height="12"/>')
dsl_lines.append('      <Text left="' + str(legend_x+18) + '" top="' + str(legend_y-2) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">Normal</Text>')
dsl_lines.append('      <Container color="#EF4444" borderRadius="4" left="' + str(legend_x+150) + '" top="' + str(legend_y-4) + '" width="8" height="8"/>')
dsl_lines.append('      <Text left="' + str(legend_x+162) + '" top="' + str(legend_y-2) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">Dense center (8px)</Text>')
dsl_lines.append('      <Container color="#DC2626" borderRadius="6" left="' + str(legend_x+320) + '" top="' + str(legend_y-5) + '" width="12" height="12"/>')
dsl_lines.append('      <Text left="' + str(legend_x+336) + '" top="' + str(legend_y-2) + '" fontSize="16" fill="#334155" fontFamily="' + FONT + '">Top3: M10(93)/M08(91)/M23(90)</Text>')

dsl_lines.append('    </Stack>')
dsl_lines.append('  </SizedBox>')
dsl_lines.append('</Snapshot>')

dsl = "\n".join(dsl_lines)
dsl_path = os.path.join(TEMP_DIR, "annotated-map.v1.snapshot")
with open(dsl_path, "w", encoding="utf-8") as f:
    f.write(dsl)
print("DSL written:", dsl_path, len(dsl), "chars")

label_layout_out = {
    "canvas": [CANVAS_W, CANVAS_H],
    "map_area": [MAP_LEFT, MAP_TOP, MAP_LEFT + MAP_W, MAP_TOP + MAP_H],
    "anchor_formula": "px = 280 + 10.4*x, py = 920 - 7.6*y",
    "point_diameter": {"default": 12, "dense_center": 8},
    "dense_center_ids": sorted(DENSE_IDS),
    "top3_ids": sorted(top3_ids),
    "label_box_size": [190, 45],
    "labels": label_layout,
}
with open(os.path.join(TEMP_DIR, "label-layout.json"), "w", encoding="utf-8") as f:
    json.dump(label_layout_out, f, ensure_ascii=False, indent=2)
print("label-layout.json written")
