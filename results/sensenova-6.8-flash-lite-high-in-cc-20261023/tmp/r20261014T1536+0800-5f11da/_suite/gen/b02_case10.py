"""B02 case-10: 新工人引导卡 (New Worker Welcome Card)
540x720, dark theme, onboarding welcome card for new workers.
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
AMBER_D   = "#D97706"
GREEN     = "#10B981"
GREEN_L   = "#34D399"
CYAN      = "#06B6D4"
ROSE      = "#FB7185"
ROSE_L    = "#FDA4AF"

W, H = 540, 720
doc = K.Doc(W, H, NIGHT)

# ============================================================ 背景光晕
for i in range(8, 0, -1):
    doc.rect(W - i * 60, -i * 30, i * 120, i * 60,
             AMBER, radius=i * 60, opacity=0.03 * i)

# ============================================================ 欢迎标题
doc.text(48, 28, "欢迎加入", 22, SLATE, owner="welcome")
doc.text(48, 56, "夜光驿站", 36, AMBER, bold=True, owner="brand_title")

# 右上角：卡片编号
doc.text_r(W - 48, 28, "NO.2026-0848", 10, MUTED, owner="card_no")

# 分割线
doc.line_h(48, W - 48, 104, NIGHT_LGT, 1)

# ============================================================ 介绍区
intro_y = 118
doc.text(48, intro_y, "什么是夜光驿站？", 15, WHITE, bold=True, owner="intro_title")
doc.text(48, intro_y + 22, "我们是城市夜班工作者的 24 小时互助驿站。", 11, SLATE, owner="intro_desc1")
doc.text(48, intro_y + 36, "提供休息、热食、健康检查和社区支持。", 11, SLATE, owner="intro_desc2")
doc.text(48, intro_y + 50, "夜班路上，你不再孤单。", 11, AMBER, bold=True, owner="intro_slogan")

# ============================================================ 服务概览
service_y = intro_y + 70  # 188
doc.text(48, service_y, "驿站服务", 15, WHITE, bold=True, owner="service_title")

services = [
    ("休息区", "24 小时开放 · 沙发 · 热水", AMBER),
    ("免费热食", "夜宵 · 早餐 · 免费供应", GREEN),
    ("健康站", "血压仪 · 急救包 · 心理咨询", CYAN),
    ("社区支持", "公告栏 · 互助信息 · 志愿者", ROSE),
]

for i, (name, desc, color) in enumerate(services):
    sy = service_y + 22 + i * 36
    doc.rect(48, sy, 4, 28, color, radius=0)
    doc.text(64, sy, name, 12, WHITE, bold=True, owner="svc_name")
    doc.text(64, sy + 16, desc, 10, SLATE, owner="svc_desc")

# 分割线
doc.line_h(48, W - 48, service_y + 22 + 4 * 36, NIGHT_LGT, 1)

# ============================================================ 最近驿站
station_y = service_y + 22 + 4 * 36 + 14
doc.text(48, station_y, "最近驿站", 15, WHITE, bold=True, owner="station_title")
doc.text(48, station_y + 22, "人民医院南站", 14, AMBER, bold=True, owner="station_name")
doc.text_r(W - 48, station_y + 22, "500 米", 13, WHITE, bold=True, owner="station_dist")
doc.text(48, station_y + 44, "人民路 128 号", 11, SLATE, owner="station_addr")
doc.text(48, station_y + 58, "24 小时开放 · 当前营业中", 11, GREEN, bold=True, owner="station_hours")

# 分割线
doc.line_h(48, W - 48, station_y + 76, NIGHT_LGT, 1)

# ============================================================ 紧急联系
emergency_y = station_y + 90
doc.text(48, emergency_y, "紧急联系", 15, WHITE, bold=True, owner="emergency_title")
doc.text(48, emergency_y + 22, "夜班支援热线", 11, SLATE, owner="emergency_label")
doc.text(48, emergency_y + 36, "400-888-0000", 20, AMBER, bold=True, owner="emergency_phone")

# ============================================================ 底部品牌条
doc.rect(0, H - 50, W, 50, AMBER, radius=0, opacity=0.1)
doc.text_c(W // 2, H - 38, "夜里有光 · 路有驿站", 13, AMBER, bold=True, owner="footer_slogan")
doc.text_c(W // 2, H - 18, "www.yeguang-yizhan.com", 10, AMBER_L, owner="footer_url")

# ============================================================ 底部光晕装饰
for i in range(5, 0, -1):
    doc.rect(0, H - i * 10, W, 10, AMBER, radius=5, opacity=0.03 * i)

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-10", 10, [], max_parts=9000)
K.save_gates("case-10", gates, "初始版本")
K.assert_gates(gates, "case-10")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-10", doc, "新工人引导卡", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
