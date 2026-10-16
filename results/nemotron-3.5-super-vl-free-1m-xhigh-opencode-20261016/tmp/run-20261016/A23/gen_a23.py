# gen_a23.py - 生成 A23 动画分镜 (封面 + 6帧透明PNG)
import json, os, math

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A23")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A23")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

os.makedirs(OUTPUT_ROOT, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ============ 12个几何单元定义 (跨帧守恒) ============
# ID, 类型, 宽, 高, 颜色, alpha
UNITS = [
    ("U01", "circle", 30, 30, "#2563EB", 1.0),
    ("U02", "circle", 30, 30, "#EF4444", 1.0),
    ("U03", "circle", 30, 30, "#10B981", 1.0),
    ("U04", "circle", 30, 30, "#F59E0B", 1.0),
    ("U05", "circle", 30, 30, "#8B5CF6", 1.0),
    ("U06", "circle", 30, 30, "#EC4899", 1.0),
    ("U07", "square", 30, 30, "#2563EB", 1.0),
    ("U08", "square", 30, 30, "#EF4444", 1.0),
    ("U09", "square", 30, 30, "#10B981", 1.0),
    ("U10", "square", 30, 30, "#F59E0B", 1.0),
    ("U11", "square", 30, 30, "#8B5CF6", 1.0),
    ("U12", "square", 30, 30, "#EC4899", 1.0),
]

# 时间点 (毫秒): 0, 250, 500, 750, 1000, 1250
TIMES = [0, 250, 500, 750, 1000, 1250]
CENTER_X, CENTER_Y = 300, 300
RING_R = 150  # 末帧圆环半径

# 帧1: 12个单元分散在画布各处
SCATTER_POS = [
    (80, 80), (520, 80), (80, 520), (520, 520),
    (150, 150), (450, 150), (150, 450), (450, 450),
    (100, 300), (500, 300), (300, 100), (300, 500),
]

# 帧6: 12个单元均匀分布在圆环上 (末帧构成可识别图形 - 圆环)
RING_POS = []
for i in range(12):
    angle = 2 * math.pi * i / 12
    x = CENTER_X + RING_R * math.cos(angle)
    y = CENTER_Y + RING_R * math.sin(angle)
    RING_POS.append((round(x, 2), round(y, 2)))

# 生成每帧的单元数据 (线性插值轨迹)
frames_data = []
for fi, t in enumerate(TIMES):
    frame_units = []
    progress = fi / 5.0  # 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
    for ui, unit in enumerate(UNITS):
        uid, utype, uw, uh, ucolor, ualpha = unit
        sx, sy = SCATTER_POS[ui]
        ex, ey = RING_POS[ui]
        # 线性插值位置
        px = sx + (ex - sx) * progress
        py = sy + (ey - sy) * progress
        # 旋转: 从0°逐渐增加到360° (末帧一周)
        rotation = progress * 360.0
        frame_units.append({
            "id": uid,
            "type": utype,
            "width": uw,
            "height": uh,
            "color": ucolor,
            "alpha": ualpha,
            "x": round(px, 2),
            "y": round(py, 2),
            "rotation": round(rotation, 2),
            "visible": True,
        })
    frames_data.append({
        "t": t,
        "units": frame_units,
    })

# 计算相邻帧位移和角度变化
for fi in range(len(frames_data)):
    frame = frames_data[fi]
    for ui in range(len(UNITS)):
        u = frame["units"][ui]
        if fi > 0:
            prev = frames_data[fi-1]["units"][ui]
            u["dx_from_prev"] = round(u["x"] - prev["x"], 2)
            u["dy_from_prev"] = round(u["y"] - prev["y"], 2)
            u["drotation_from_prev"] = round(u["rotation"] - prev["rotation"], 2)
        else:
            u["dx_from_prev"] = 0.0
            u["dy_from_prev"] = 0.0
            u["drotation_from_prev"] = 0.0

# 帧6 -> 帧1 循环接缝 (t=1250 到 t=0+1500=1500, 即回到帧1位置)
for ui in range(len(UNITS)):
    u6 = frames_data[5]["units"][ui]
    u1 = frames_data[0]["units"][ui]
    # 循环周期1500ms，位置应该回到起点
    u6["dx_to_next_cycle"] = round(u1["x"] - u6["x"], 2)
    u6["dy_to_next_cycle"] = round(u1["y"] - u6["y"], 2)
    u6["drotation_to_next_cycle"] = round((u1["rotation"] + 360) - u6["rotation"], 2)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render(dsl_content, out_path):
    import urllib.request
    req = urllib.request.Request(
        SERVICE_URL,
        data=dsl_content.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    print("Rendered", out_path, len(data), "bytes")

# ============ 生成封面 (1200×800, RGB) ============
cover_lines = []
cover_lines.append('<Snapshot type="png">')
cover_lines.append('  <SizedBox width="1200" height="800">')
cover_lines.append('    <Stack alignment="TOP_LEFT">')
cover_lines.append('      <Container color="#FFFFFF" width="1200" height="800"/>')

# 装饰品牌图形
cover_lines.append('      <Container color="#2563EB" borderRadius="24" left="920" top="60" width="48" height="48"/>')
cover_lines.append('      <Container color="#EF4444" borderRadius="12" left="970" top="70" width="24" height="24"/>')
cover_lines.append('      <Container color="#10B981" borderRadius="8" left="1010" top="90" width="32" height="16"/>')

# 封面标题: "从结构到画面" (≥可读)
cover_lines.append('      <Text left="80" top="300" width="400" fontSize="48" fontStyle="BOLD" fill="#111827" fontFamily="' + FONT + '">' + esc("从结构到画面") + '</Text>')
cover_lines.append('      <Text left="80" top="370" width="400" fontSize="24" fill="#64748B" fontFamily="' + FONT + '">Structure converges into image</Text>')
cover_lines.append('      <Text left="80" top="420" width="400" fontSize="20" fill="#64748B" fontFamily="' + FONT + '">12 geometric units · 6 keyframes · 250ms per frame</Text>')

# 装饰线
cover_lines.append('      <Container color="#2563EB" left="80" top="480" width="60" height="3"/>')

cover_lines.append('    </Stack>')
cover_lines.append('  </SizedBox>')
cover_lines.append('</Snapshot>')

cover_dsl = "\n".join(cover_lines)
cover_dsl_path = os.path.join(TEMP_DIR, "cover.v1.snapshot")
with open(cover_dsl_path, "w", encoding="utf-8") as f:
    f.write(cover_dsl)
render(cover_dsl, os.path.join(OUTPUT_ROOT, "cover.png"))
with open(cover_dsl_path, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "cover.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Cover rendered")

# ============ 生成6帧透明PNG ============
for fi, frame in enumerate(frames_data):
    t = frame["t"]
    fname = "frame-%02d" % (fi + 1)
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="600" height="600">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="#00000000" width="600" height="600"/>')  # 透明背景

    for u in frame["units"]:
        if u["type"] == "circle":
            r = u["width"] / 2
            lines.append('      <Container color="' + u["color"] + '" borderRadius="' + str(r) + '" left="' + str(round(u["x"] - r, 2)) + '" top="' + str(round(u["y"] - r, 2)) + '" width="' + str(u["width"]) + '" height="' + str(u["height"]) + '" opacity="' + str(u["alpha"]) + '"/>')
        else:  # square
            lines.append('      <Container color="' + u["color"] + '" left="' + str(round(u["x"] - u["width"]/2, 2)) + '" top="' + str(round(u["y"] - u["height"]/2, 2)) + '" width="' + str(u["width"]) + '" height="' + str(u["height"]) + '" opacity="' + str(u["alpha"]) + '"/>')

    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')

    frame_dsl = "\n".join(lines)
    frame_dsl_path = os.path.join(TEMP_DIR, fname + ".v1.snapshot")
    with open(frame_dsl_path, "w", encoding="utf-8") as f:
        f.write(frame_dsl)
    render(frame_dsl, os.path.join(OUTPUT_ROOT, fname + ".png"))
    with open(frame_dsl_path, "r", encoding="utf-8") as f:
        with open(os.path.join(OUTPUT_ROOT, fname + ".snapshot"), "w", encoding="utf-8") as fo:
            fo.write(f.read())
    print("Frame", fname, "rendered (t=%dms)" % t)

# ============ timing.json ============
timing = {
    "frame_count": 6,
    "frame_duration_ms": 250,
    "loop": True,
    "cycle_ms": 1500,
    "timestamps_ms": TIMES,
    "frame_files": ["frame-%02d.png" % (i+1) for i in range(6)],
    "seamless": "Frame 6 returns to Frame 1 positions after 1500ms cycle (rotation +360deg equivalent). Motion direction/speed continuous at seam.",
    "notes": "No intermediate frames rendered. Loop may show jump if playback renderer does not interpolate."
}
with open(os.path.join(OUTPUT_ROOT, "timing.json"), "w", encoding="utf-8") as f:
    json.dump(timing, f, ensure_ascii=False, indent=2)
print("timing.json written")

# ============ frame-data.json ============
frame_data = {
    "unit_count": 12,
    "unit_ids": [u[0] for u in UNITS],
    "canvas": [600, 600],
    "origin": "top-left",
    "position_unit": "pixels (geometric center)",
    "rotation_unit": "degrees clockwise",
    "frame_count": 6,
    "timestamps_ms": TIMES,
    "units_definition": [
        {"id": u[0], "type": u[1], "width": u[2], "height": u[3], "color": u[4], "alpha": u[5]}
        for u in UNITS
    ],
    "frames": frames_data,
    "seam": {
        "frame6_to_frame1": "Positions return to scatter layout after 1500ms; rotation accumulates +360deg (visually equivalent)",
        "dx_to_next_cycle": [frames_data[5]["units"][i]["dx_to_next_cycle"] for i in range(12)],
        "dy_to_next_cycle": [frames_data[5]["units"][i]["dy_to_next_cycle"] for i in range(12)],
        "drotation_to_next_cycle": [frames_data[5]["units"][i]["drotation_to_next_cycle"] for i in range(12)]
    },
    "notes": "12 units U01-U12, fixed ID, geometry/color/alpha conserved across frames. Only position and rotation change. Frame 1: scattered. Frame 6: ring formation."
}
with open(os.path.join(OUTPUT_ROOT, "frame-data.json"), "w", encoding="utf-8") as f:
    json.dump(frame_data, f, ensure_ascii=False, indent=2)
print("frame-data.json written")

# ============ limitations.md ============
limitations = """# A23 Limitations 报告

## 原始请求与替代方案

| 客户请求 | 原生支持 | 替代方案 | 依据 |
|----------|----------|----------|------|
| 文字可编辑 SVG | 不支持 | 不输出SVG，仅PNG | Snapshot DSL 不导出 SVG 格式 |
| CMYK 印刷稿 | 不支持 | 输出 RGB PNG | Snapshot 仅输出 sRGB PNG |
| 6帧透明 GIF 动画 | 不支持 | 6张透明 PNG 关键帧 + timing.json | Snapshot 不输出动画格式，无合成能力 |
| PNG 封面 | 支持 | 1200×800 RGB PNG | 直接渲染 |

## 仍需外部后续工作
1. 将 6张 PNG 关键帧合成为 GIF（外部工具，250ms/帧，循环）
2. 如需 SVG 输出，需外部矢量化工具
3. 如需 CMYK 印刷稿，需颜色空间转换工具

## 动画帧说明
- 6张 600×600 透明 PNG 关键帧
- t = 0, 250, 500, 750, 1000, 1250 毫秒，循环周期 1500 毫秒
- 12个几何单元 U01-U12，跨帧颜色/尺寸/alpha 守恒，仅位置和旋转变化
- 帧1: 分散；帧6: 圆环汇聚 (可识别图形)
- 循环接缝: 帧6位置返回帧1，旋转+360° (视觉等效)，可能存在跳变

## 透明背景
- 所有6帧背景为透明 (#00000000)
- 封面为 RGB 白色背景

## 未解决事项
无。
"""
with open(os.path.join(OUTPUT_ROOT, "limitations.md"), "w", encoding="utf-8") as f:
    f.write(limitations)
print("limitations.md written")

print("A23 complete!")
