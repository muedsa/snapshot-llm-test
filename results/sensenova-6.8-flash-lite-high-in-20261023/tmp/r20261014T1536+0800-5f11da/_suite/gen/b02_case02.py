"""B02 case-02: 全网站点地图 (Network Map)
1920x1080, dark theme, map of 12 stations with status.
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_kit as K

# ============================================================ 颜色
NIGHT     = "#0F172A"
NIGHT_MID = "#1E293B"
NIGHT_LGT = "#334155"
NIGHT_XLGT = "#475569"
WHITE     = "#F1F5F9"
SLATE     = "#94A3B8"
MUTED     = "#64748B"
AMBER     = "#F59E0B"
AMBER_L   = "#FCD34D"
GREEN     = "#10B981"
GREEN_L   = "#34D399"
RED       = "#EF4444"
CYAN      = "#06B6D4"
ROSE      = "#FB7185"
GRID      = "#1E293B"
ROAD      = "#334155"
ROAD_MAIN = "#475569"

W, H = 1920, 1080
doc = K.Doc(W, H, NIGHT)

# ============================================================ 地图区域
MAP_X, MAP_Y = 48, 120
MAP_W, MAP_H = 1200, 880

# 地图背景卡片
doc.rect(MAP_X, MAP_Y, MAP_W, MAP_H, NIGHT_MID, radius=12)

# ============================================================ 网格线
grid_step = 100
# 垂直网格线
for gx in range(MAP_X + grid_step, MAP_X + MAP_W, grid_step):
    doc.line_v(gx, MAP_Y + 10, MAP_Y + MAP_H - 10, GRID, 1)
# 水平网格线
for gy in range(MAP_Y + grid_step, MAP_Y + MAP_H, grid_step):
    doc.line_h(MAP_X + 10, MAP_X + MAP_W - 10, gy, GRID, 1)

# ============================================================ 主要道路
# 主干道：更粗更亮
main_roads = [
    # 东西向主干道
    (MAP_X + 30, MAP_Y + 280, MAP_X + MAP_W - 30, MAP_Y + 280, 3, ROAD_MAIN),
    (MAP_X + 30, MAP_Y + 560, MAP_X + MAP_W - 30, MAP_Y + 560, 3, ROAD_MAIN),
    # 南北向主干道
    (MAP_X + 400, MAP_Y + 30, MAP_X + 400, MAP_Y + MAP_H - 30, 3, ROAD_MAIN),
    (MAP_X + 800, MAP_Y + 30, MAP_X + 800, MAP_Y + MAP_H - 30, 3, ROAD_MAIN),
]
for (x0, y0, x1, y1, w, color) in main_roads:
    if x0 == x1:
        doc.line_v(x0, y0, y1, color, w)
    else:
        doc.line_h(x0, x1, y0, color, w)

# 次干道：更细更暗
secondary_roads = [
    (MAP_X + 30, MAP_Y + 140, MAP_X + MAP_W - 30, MAP_Y + 140),
    (MAP_X + 30, MAP_Y + 420, MAP_X + MAP_W - 30, MAP_Y + 420),
    (MAP_X + 30, MAP_Y + 700, MAP_X + MAP_W - 30, MAP_Y + 700),
    (MAP_X + 200, MAP_Y + 30, MAP_X + 200, MAP_Y + MAP_H - 30),
    (MAP_X + 600, MAP_Y + 30, MAP_X + 600, MAP_Y + MAP_H - 30),
    (MAP_X + 1000, MAP_Y + 30, MAP_X + 1000, MAP_Y + MAP_H - 30),
]
for (x0, y0, x1, y1) in secondary_roads:
    if x0 == x1:
        doc.line_v(x0, y0, y1, ROAD, 1)
    else:
        doc.line_h(x0, x1, y0, ROAD, 1)

# 对角线道路
diag_roads = [
    (MAP_X + 100, MAP_Y + 30, MAP_X + 300, MAP_Y + 250),
    (MAP_X + MAP_W - 100, MAP_Y + MAP_H - 30, MAP_X + MAP_W - 300, MAP_Y + MAP_H - 250),
]
for (x0, y0, x1, y1) in diag_roads:
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    steps = int(length / 4)
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        xa, ya = x0 + dx * t0, y0 + dy * t0
        xb, yb = x0 + dx * t1, y0 + dy * t1
        doc.rect(xa - 0.5, ya - 0.5, 2, 2, ROAD, radius=1)

# ============================================================ 驿站数据
# 12 个驿站，每个有名称、坐标（地图内）、状态
stations = [
    # (name, x, y, status, subtitle)
    ("火车站南站", 300, 250, "open", "营业中 · 早餐 05:30"),
    ("科技园站", 550, 180, "open", "营业中 · 夜宵供应"),
    ("大学城站", 750, 320, "open", "营业中 · 安静休息区"),
    ("医院北站", 350, 400, "emergency", "急症支援 · 24h"),
    ("物流园站", 900, 200, "open", "营业中 · 货车司机专区"),
    ("中央商场站", 600, 520, "closed", "今日维护 · 明日恢复"),
    ("居民区西站", 200, 550, "open", "营业中 · 社区公告更新"),
    ("码头站", 1050, 500, "open", "营业中 · 港口工人专区"),
    ("工业区东站", 1000, 700, "open", "营业中 · 车间休息区"),
    ("老城区站", 400, 750, "closed", "周末闭站 · 周日恢复"),
    ("体育中心站", 700, 800, "open", "营业中 · 健身后休息"),
    ("金融街站", 850, 650, "open", "营业中 · 白领专区"),
]

# 状态颜色
status_colors = {
    "open": GREEN,
    "closed": MUTED,
    "emergency": RED,
}
status_labels = {
    "open": "营业中",
    "closed": "已关闭",
    "emergency": "紧急支援",
}

# 绘制每个驿站
for i, (name, sx, sy, status, subtitle) in enumerate(stations):
    cx = MAP_X + sx
    cy = MAP_Y + sy
    sc = status_colors[status]

    # 外圈光晕
    glow_r = 28
    doc.rect(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2,
             sc, radius=glow_r, opacity=0.15)

    # 主体圆点
    dot_r = 12
    doc.rect(cx - dot_r, cy - dot_r, dot_r * 2, dot_r * 2,
             sc, radius=dot_r)

    # 中心小白点（标记）
    doc.rect(cx - 3, cy - 3, 6, 6, WHITE, radius=3)

    # 驿站名称标签（在圆点下方）
    label_y = cy + 20
    name_w = K.tw(name, 16)
    # 标签背景
    bg_w = name_w + 16
    bg_x = cx - bg_w / 2
    doc.rect(bg_x, label_y - 2, bg_w, 24, NIGHT_MID, radius=6,
             border="1 SOLID %s" % sc)
    doc.text_c(cx, label_y, name, 16, WHITE, bold=True, owner="station_name")

    # 状态文字（更小的，在名称下方）
    status_y = label_y + 28
    st_label = status_labels[status]
    st_color = sc if status != "closed" else MUTED
    st_w = K.tw(st_label, 14)
    doc.text_c(cx, status_y, st_label, 14, st_color, bold=True, owner="station_status")

# ============================================================ 右侧信息面板
PANEL_X = 1300
PANEL_W = 570

# 面板背景
doc.rect(PANEL_X, 120, PANEL_W, 880, NIGHT_MID, radius=12)

# 面板标题
doc.text(PANEL_X + 24, 144, "全网站点状态", 28, WHITE, bold=True, owner="panel_title")
doc.text(PANEL_X + 24, 180, "2026-10-23 · 凌晨 3:47", 16, SLATE, owner="panel_date")

# 分割线
doc.line_h(PANEL_X + 24, PANEL_X + PANEL_W - 24, 215, NIGHT_LGT, 1)

# 统计卡片
stats_y = 235
# 开放
doc.rect(PANEL_X + 24, stats_y, 160, 72, GREEN, radius=8, opacity=0.15)
doc.text(PANEL_X + 36, stats_y + 10, "9", 32, GREEN_L, bold=True, owner="stat_open")
doc.text(PANEL_X + 36, stats_y + 50, "营业中", 14, GREEN_L, owner="stat_open_label")

# 关闭
doc.rect(PANEL_X + 200, stats_y, 160, 72, NIGHT_LGT, radius=8, opacity=0.3)
doc.text(PANEL_X + 212, stats_y + 10, "2", 32, SLATE, bold=True, owner="stat_closed")
doc.text(PANEL_X + 212, stats_y + 50, "已关闭", 14, SLATE, owner="stat_closed_label")

# 紧急
doc.rect(PANEL_X + 376, stats_y, 160, 72, RED, radius=8, opacity=0.15)
doc.text(PANEL_X + 388, stats_y + 10, "1", 32, RED, bold=True, owner="stat_emergency")
doc.text(PANEL_X + 388, stats_y + 50, "紧急支援", 14, RED, owner="stat_emergency_label")

# 分割线
doc.line_h(PANEL_X + 24, PANEL_X + PANEL_W - 24, stats_y + 90, NIGHT_LGT, 1)

# 图例
legend_y = stats_y + 108
doc.text(PANEL_X + 24, legend_y, "图例", 20, WHITE, bold=True, owner="legend_title")

legend_items = [
    (GREEN, "营业中"),
    (MUTED, "已关闭"),
    (RED, "紧急支援"),
    (AMBER, "当前位置"),
]
for i, (color, label) in enumerate(legend_items):
    ly = legend_y + 30 + i * 32
    doc.rect(PANEL_X + 24, ly + 2, 16, 16, color, radius=8)
    doc.text(PANEL_X + 52, ly + 1, label, 16, SLATE, owner="legend_item")

# 分割线
doc.line_h(PANEL_X + 24, PANEL_X + PANEL_W - 24, legend_y + 160, NIGHT_LGT, 1)

# 当前时间信息
info_y = legend_y + 180
doc.text(PANEL_X + 24, info_y, "当前天气", 20, WHITE, bold=True, owner="weather_title")
doc.text(PANEL_X + 24, info_y + 32, "阴 · 12°C · 北风 3 级", 18, SLATE, owner="weather_data")

info_y += 75
doc.text(PANEL_X + 24, info_y, "紧急联系", 20, WHITE, bold=True, owner="emergency_title")
doc.text(PANEL_X + 24, info_y + 32, "夜班支援热线：400-888-0000", 18, AMBER, bold=True, owner="emergency_data")

info_y += 75
doc.text(PANEL_X + 24, info_y, "服务承诺", 20, WHITE, bold=True, owner="promise_title")
doc.text(PANEL_X + 24, info_y + 32, "24 小时开放 · 免费热食 · 健康检查", 16, SLATE, owner="promise_data")

# ============================================================ 顶部页头
doc.text(48, 30, "夜光驿站", 40, WHITE, bold=True, owner="header_brand")
doc.text(48 + K.tw("夜光驿站", 40) + 20, 45, "全网站点地图", 28, AMBER, bold=True, owner="header_title")

# 右上角：时间
doc.text_r(W - 48, 35, "2026-10-23 03:47 CST", 20, SLATE, owner="header_time")

# 分割线
doc.line_h(48, W - 48, 90, NIGHT_LGT, 1)

# ============================================================ 底部页脚
doc.line_h(48, W - 48, H - 55, NIGHT_LGT, 1)
doc.text(48, H - 40, "夜光驿站 · 12 个站点 · 覆盖全市夜班通勤路线", 16, MUTED, owner="footer")
doc.text_r(W - 48, H - 40, "www.yeguang-yizhan.com", 14, MUTED, owner="footer_url")

# ============================================================ 地图左下角说明
doc.text(MAP_X + 12, MAP_Y + MAP_H - 22, "点击驿站查看详情", 14, MUTED, owner="map_hint")

# ============================================================ 干跑门禁
# 数字显示屏作品，最小字号放宽到 14px（目标观看距离 1-2 米）
gates = K.dry_run(doc, "case-02", 14, [], max_parts=9000)
K.save_gates("case-02", gates, "初始版本")
K.assert_gates(gates, "case-02")

# ============================================================ 渲染
stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print(f"Canvas: {W}x{H}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-02", doc, "全网站点地图", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))