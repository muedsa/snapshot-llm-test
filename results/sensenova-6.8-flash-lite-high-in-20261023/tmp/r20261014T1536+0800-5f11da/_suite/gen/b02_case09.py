"""B02 case-09: 季度运营报告 (Quarterly Impact Report)
1200x1697, dark theme, A4 impact report with data visualizations.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_kit as K

NIGHT     = "#0F172A"
NIGHT_MID = "#1E293B"
NIGHT_LGT = "#334155"
WHITE     = "#F1F5F9"
SLATE     = "#94A3B8"
MUTED     = "#64748B"
AMBER     = "#F59E0B"
AMBER_L   = "#FCD34D"
GREEN     = "#10B981"
GREEN_L   = "#34D399"
CYAN      = "#06B6D4"
CYAN_L    = "#67E8F9"
ROSE      = "#FB7185"
ROSE_L    = "#FDA4AF"
PURPLE    = "#8B5CF6"
PURPLE_L  = "#A78BFA"

W, H = 1200, 1697
doc = K.Doc(W, H, NIGHT)

# ============================================================ 顶部标题区
doc.text(48, 36, "夜光驿站", 36, WHITE, bold=True, owner="brand")
doc.text(48 + K.tw("夜光驿站", 36) + 24, 44, "季度运营报告", 28, AMBER, bold=True, owner="title")

# 日期
doc.text_r(W - 48, 40, "2026 Q3", 24, SLATE, bold=True, owner="quarter")
doc.text_r(W - 48, 72, "2026年7月 — 9月", 16, MUTED, owner="quarter_range")

# 分割线
doc.line_h(48, W - 48, 100, NIGHT_LGT, 1)

# ============================================================ 执行摘要
summary_y = 124
doc.text(48, summary_y, "执行摘要", 24, WHITE, bold=True, owner="exec_title")

doc.text(48, summary_y + 36, "本季度夜光驿站累计服务夜班工作者 48,200 人次，", 18, SLATE, owner="exec_desc1")
doc.text(48, summary_y + 62, "提供 28,500 份免费热食，健康检查覆盖 12,600 人次，", 18, SLATE, owner="exec_desc2")
doc.text(48, summary_y + 88, "志愿者累计贡献 3,200 小时。", 18, SLATE, owner="exec_desc3")

# ============================================================ 关键指标
kpi_y = summary_y + 128
doc.text(48, kpi_y, "关键指标", 24, WHITE, bold=True, owner="kpi_title")

kpis = [
    ("48,200", "服务人次", AMBER, "+15%"),
    ("28,500", "份热食", GREEN, "+22%"),
    ("12,600", "健康检查", CYAN, "+18%"),
    ("3,200", "志愿小时", ROSE, "+8%"),
]

for i, (val, label, color, change) in enumerate(kpis):
    kx = 48 + i * 280
    # 背景卡片
    doc.rect(kx, kpi_y + 36, 250, 90, color, radius=10, opacity=0.1)
    doc.rect(kx, kpi_y + 36, 250, 90, color, radius=10, opacity=0.1,
             border="1 SOLID %s" % color)
    # 数值
    doc.text(kx + 20, kpi_y + 44, val, 32, color, bold=True, owner="kpi_val")
    # 标签
    doc.text(kx + 20, kpi_y + 84, label, 16, SLATE, owner="kpi_label")
    # 变化标签
    change_w = K.tw(change, 12) + 16
    doc.rect(kx + 250 - 20 - change_w, kpi_y + 48, change_w, 20, color, radius=10, opacity=0.2)
    doc.text_c(kx + 250 - 20 - change_w / 2, kpi_y + 52, change, 12, color, bold=True, owner="kpi_change")

# ============================================================ 分割线
doc.line_h(48, W - 48, kpi_y + 148, NIGHT_LGT, 1)

# ============================================================ 月度趋势
trend_y = kpi_y + 172
doc.text(48, trend_y, "月度趋势", 24, WHITE, bold=True, owner="trend_title")

# 月度数据
months = ["7月", "8月", "9月"]
served = [14800, 15600, 17800]
meals = [8800, 9400, 10300]
max_month = 20000

chart_x, chart_y = 48, trend_y + 44
chart_w, chart_h = W - 96, 200

# 月份标签和柱状图
for i in range(3):
    # 服务人次
    mx = chart_x + i * (chart_w / 3) + 40
    mh = (served[i] / max_month) * chart_h
    doc.rect(mx, chart_y + chart_h - mh, 60, mh, AMBER, radius=6)
    # 热食数量
    mh2 = (meals[i] / max_month) * chart_h
    doc.rect(mx + 70, chart_y + chart_h - mh2, 60, mh2, GREEN, radius=6)
    # 月份标签
    doc.text_c(mx + 65, chart_y + chart_h + 12, months[i], 18, SLATE, bold=True, owner="month_label")
    # 数值
    doc.text_c(mx + 30, chart_y + chart_h - mh - 22, "%d" % served[i], 14, AMBER, bold=True, owner="trend_served")
    doc.text_c(mx + 100, chart_y + chart_h - mh2 - 22, "%d" % meals[i], 14, GREEN, bold=True, owner="trend_meals")

# 图例
legend_x = chart_x + chart_w - 200
doc.rect(legend_x, trend_y + 4, 16, 16, AMBER, radius=4)
doc.text(legend_x + 24, trend_y + 4, "服务人次", 16, SLATE, owner="legend_served")
doc.rect(legend_x + 130, trend_y + 4, 16, 16, GREEN, radius=4)
doc.text(legend_x + 154, trend_y + 4, "热食份数", 16, SLATE, owner="legend_meals")

# ============================================================ 分割线
doc.line_h(48, W - 48, trend_y + 280, NIGHT_LGT, 1)

# ============================================================ 站点贡献
station_y = trend_y + 304
doc.text(48, station_y, "站点贡献", 24, WHITE, bold=True, owner="station_title")

station_data = [
    ("人民医院南站", 12800, AMBER),
    ("物流园站", 9600, GREEN),
    ("大学城站", 8400, CYAN),
    ("科技城站", 7200, ROSE),
    ("工业区东站", 6000, PURPLE),
    ("其他站点", 4200, SLATE),
]

for i, (name, count, color) in enumerate(station_data):
    sy = station_y + 36 + i * 44
    # 排名
    doc.text(48, sy + 4, "%d" % (i + 1), 20, MUTED, bold=True, owner="rank")
    # 名称
    doc.text(88, sy, name, 18, WHITE, bold=True, owner="station_name")
    # 进度条背景
    bar_max_w = 400
    doc.rect(340, sy + 4, bar_max_w, 24, NIGHT_MID, radius=12)
    # 进度条
    bar_w = (count / 12800) * bar_max_w
    doc.rect(340, sy + 4, bar_w, 24, color, radius=12)
    # 数值
    doc.text_r(W - 48, sy, "%d 人次" % count, 18, color, bold=True, owner="station_count")

# ============================================================ 分割线
doc.line_h(48, W - 48, station_y + 36 + 6 * 44, NIGHT_LGT, 1)

# ============================================================ 故事摘要
story_y = station_y + 36 + 6 * 44 + 24
doc.text(48, story_y, "社区故事", 24, WHITE, bold=True, owner="story_title")

doc.text(48, story_y + 36, "「这是我在城市里最温暖的地方。凌晨 3 点，", 20, AMBER, bold=True, owner="story_quote1")
doc.text(48, story_y + 68, "知道有人在等我吃早餐。」", 20, AMBER, bold=True, owner="story_quote2")
doc.text(48, story_y + 104, "— 王师傅，物流司机 15 年", 16, SLATE, owner="story_author")

# ============================================================ 底部
doc.line_h(48, W - 48, H - 80, NIGHT_LGT, 1)
doc.text(48, H - 60, "夜光驿站 · 2026 Q3", 16, MUTED, owner="footer_brand")
doc.text_c(W // 2, H - 60, "夜里有光 · 路有驿站", 16, AMBER, bold=True, owner="footer_slogan")
doc.text_r(W - 48, H - 60, "www.yeguang-yizhan.com", 14, MUTED, owner="footer_url")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-09", 12, [], max_parts=9000)
K.save_gates("case-09", gates, "初始版本")
K.assert_gates(gates, "case-09")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-09", doc, "季度运营报告", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))