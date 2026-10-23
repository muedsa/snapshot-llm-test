"""B02 case-04: 紧急呼叫卡 (Emergency Call Card)
600x900, dark theme, wallet-sized emergency card.
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
RED       = "#EF4444"
RED_L     = "#FCA5A5"
GREEN     = "#10B981"
CYAN      = "#06B6D4"

W, H = 600, 900
doc = K.Doc(W, H, NIGHT)

# ============================================================ 背景
# 顶部红色警告光晕
for i in range(6, 0, -1):
    doc.rect(0, 0, W, i * 20, RED, radius=0, opacity=0.06 * i)

# ============================================================ 顶部警告条
# 红色警告条
doc.rect(0, 0, W, 80, RED, radius=0)

# 警告图标：感叹号
warn_cx, warn_cy = 60, 40
# 外圈
doc.rect(warn_cx - 24, warn_cy - 24, 48, 48, WHITE, radius=24)
# 感叹号竖线
doc.rect(warn_cx - 3, warn_cy - 12, 6, 16, RED, radius=3)
# 感叹号点
doc.rect(warn_cx - 3, warn_cy + 8, 6, 6, RED, radius=3)

# 警告文字
doc.text(100, 12, "紧急呼叫卡", 28, WHITE, bold=True, owner="warn_title")
doc.text(100, 46, "遇到危险时立即拨打", 16, WHITE, owner="warn_desc")

# ============================================================ 主要紧急电话区
phone_y = 110

# 主标题
doc.text(48, phone_y, "紧急联系电话", 22, WHITE, bold=True, owner="phone_title")

# 分割线
doc.line_h(48, W - 48, phone_y + 38, RED, 2)

# 电话 1: 夜班支援热线
tel1_y = phone_y + 56
doc.rect(48, tel1_y, W - 96, 68, RED, radius=12, opacity=0.15)
doc.rect(48, tel1_y, W - 96, 68, RED, radius=12, opacity=0.1, border="2 SOLID #EF4444")
# 电话图标
doc.rect(72, tel1_y + 22, 24, 24, RED, radius=12)
doc.rect(78, tel1_y + 26, 12, 16, WHITE, radius=2)
doc.rect(76, tel1_y + 32, 16, 4, WHITE, radius=2)
doc.text(112, tel1_y + 8, "夜班支援热线", 16, WHITE, bold=True, owner="tel1_label")
doc.text(112, tel1_y + 34, "400-888-0000", 32, RED, bold=True, owner="tel1_number")

# 电话 2: 最近驿站
tel2_y = tel1_y + 84
doc.rect(48, tel2_y, W - 96, 68, AMBER, radius=12, opacity=0.15)
doc.rect(48, tel2_y, W - 96, 68, AMBER, radius=12, opacity=0.1, border="2 SOLID #F59E0B")
# 站点图标
doc.rect(72, tel2_y + 22, 24, 24, AMBER, radius=12)
doc.rect(76, tel2_y + 26, 16, 16, WHITE, radius=2)
doc.rect(80, tel2_y + 28, 8, 12, AMBER, radius=2)
doc.text(112, tel2_y + 8, "最近驿站：人民医院南站", 16, WHITE, bold=True, owner="tel2_label")
doc.text(112, tel2_y + 34, "138-0012-3456", 32, AMBER, bold=True, owner="tel2_number")

# 电话 3: 急救
tel3_y = tel2_y + 84
doc.rect(48, tel3_y, W - 96, 68, GREEN, radius=12, opacity=0.15)
doc.rect(48, tel3_y, W - 96, 68, GREEN, radius=12, opacity=0.1, border="2 SOLID #10B981")
# 急救图标
doc.rect(72, tel3_y + 22, 24, 24, GREEN, radius=12)
doc.rect(78, tel3_y + 24, 12, 20, WHITE, radius=2)
doc.rect(74, tel3_y + 30, 20, 8, WHITE, radius=2)
doc.text(112, tel3_y + 8, "医疗急救", 16, WHITE, bold=True, owner="tel3_label")
doc.text(112, tel3_y + 34, "120", 32, GREEN, bold=True, owner="tel3_number")

# ============================================================ 分割线
doc.line_h(48, W - 48, tel3_y + 96, NIGHT_LGT, 1)

# ============================================================ 最近驿站信息
station_y = tel3_y + 116
doc.text(48, station_y, "最近驿站", 20, WHITE, bold=True, owner="station_title")

# 驿站名称
doc.text(48, station_y + 30, "人民医院南站", 20, AMBER, bold=True, owner="station_name")

# 距离
doc.text_r(W - 48, station_y + 30, "500 米", 18, WHITE, bold=True, owner="station_dist")

# 地址
doc.text(48, station_y + 60, "地址：人民路 128 号", 16, SLATE, owner="station_addr")

# 开放时间
doc.text(48, station_y + 84, "24 小时开放 · 当前营业中", 16, GREEN, bold=True, owner="station_hours")

# ============================================================ 分割线
doc.line_h(48, W - 48, station_y + 120, NIGHT_LGT, 1)

# ============================================================ 个人健康信息
info_y = station_y + 140
doc.text(48, info_y, "个人健康信息", 20, WHITE, bold=True, owner="info_title")

# 过敏信息
doc.text(48, info_y + 30, "过敏：", 18, WHITE, bold=True, owner="allergy_label")
doc.text(120, info_y + 30, "青霉素 · 海鲜 · 花生", 18, RED, owner="allergy_data")

# 血型
doc.text(48, info_y + 60, "血型：", 18, WHITE, bold=True, owner="blood_label")
doc.text(120, info_y + 60, "O 型", 20, RED, bold=True, owner="blood_data")

# 慢性病
doc.text(48, info_y + 90, "慢性病：", 18, WHITE, bold=True, owner="chronic_label")
doc.text(120, info_y + 90, "无", 18, WHITE, owner="chronic_data")

# ============================================================ 分割线
doc.line_h(48, W - 48, info_y + 126, NIGHT_LGT, 1)

# ============================================================ 紧急联系人
contact_y = info_y + 146
doc.text(48, contact_y, "紧急联系人", 20, WHITE, bold=True, owner="contact_title")

# 联系人 1
doc.text(48, contact_y + 30, "爱人  王芳", 18, WHITE, bold=True, owner="contact1_name")
doc.text_r(W - 48, contact_y + 30, "139-0012-3456", 18, AMBER, bold=True, owner="contact1_phone")

# 联系人 2
doc.text(48, contact_y + 60, "姐姐  李红梅", 18, WHITE, bold=True, owner="contact2_name")
doc.text_r(W - 48, contact_y + 60, "139-0012-7890", 18, AMBER, bold=True, owner="contact2_phone")

# ============================================================ 底部品牌条
doc.rect(0, H - 60, W, 60, AMBER, radius=0, opacity=0.1)
doc.text_c(W // 2, H - 44, "夜光驿站", 20, AMBER, bold=True, owner="footer_brand")
doc.text_c(W // 2, H - 20, "夜里有光 · 路有驿站", 14, AMBER_L, owner="footer_slogan")

# ============================================================ 右侧装饰光斑
for i in range(5, 0, -1):
    doc.rect(W - i * 30, H - i * 60, i * 60, i * 60, AMBER, radius=i * 30, opacity=0.04 * i)

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-04", 14, [], max_parts=9000)
K.save_gates("case-04", gates, "初始版本")
K.assert_gates(gates, "case-04")

# ============================================================ 渲染
stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print(f"Canvas: {W}x{H}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-04", doc, "紧急呼叫卡", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))