"""B02 case-03: 夜班通行证 (Night Shift Pass)
540x900, dark theme, personal identity card with health status.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_kit as K

# ============================================================ 颜色
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
RED       = "#EF4444"

W, H = 540, 900
doc = K.Doc(W, H, NIGHT)

# ============================================================ 背景光晕
# 右上角柔和光晕
for i in range(8, 0, -1):
    doc.rect(W - i * 60, -60, i * 120, 180,
             AMBER, radius=i * 60, opacity=0.03 * i)

# ============================================================ 顶部品牌区
brand_y = 32
# 品牌标志：小光晕
logo_r = 20
doc.rect(48 - logo_r, brand_y + 4, logo_r * 2, logo_r * 2,
         AMBER, radius=logo_r, opacity=0.2)
doc.rect(48 - 12, brand_y + 12, 24, 24, AMBER, radius=12)
doc.rect(44, brand_y + 14, 8, 20, WHITE, radius=4)
doc.rect(40, brand_y + 20, 16, 8, WHITE, radius=4)

doc.text(84, brand_y, "夜光驿站", 24, WHITE, bold=True, owner="brand")
doc.text(84, brand_y + 32, "夜班通行证", 14, AMBER, bold=True, owner="sub_brand")

# 右上角：卡片编号
doc.text_r(W - 48, brand_y + 8, "NO.2026-0847", 12, MUTED, owner="card_no")
doc.text_r(W - 48, brand_y + 26, "2026-10-23", 12, MUTED, owner="card_date")

# 分割线
doc.line_h(48, W - 48, brand_y + 52, NIGHT_LGT, 1)

# ============================================================ 头像区域
avatar_y = brand_y + 72
avatar_r = 48
avatar_cx = 96
avatar_cy = avatar_y + 48

# 头像外圈光晕
doc.rect(avatar_cx - avatar_r - 10, avatar_cy - avatar_r - 10,
         (avatar_r + 10) * 2, (avatar_r + 10) * 2,
         AMBER, radius=avatar_r + 10, opacity=0.15)

# 头像圆底
doc.rect(avatar_cx - avatar_r, avatar_cy - avatar_r,
         avatar_r * 2, avatar_r * 2,
         AMBER, radius=avatar_r, opacity=0.3)

# 头像占位： initials
doc.text_c(avatar_cx, avatar_cy - 14, "李", 32, AMBER_L, bold=True, owner="avatar_name")

# 工号
doc.text_c(avatar_cx, avatar_cy + 26, "工号 0847", 14, AMBER, bold=True, owner="avatar_id")

# ============================================================ 个人信息区
info_x = 180
info_y = avatar_y

# 姓名
doc.text(info_x, info_y, "李建国", 28, WHITE, bold=True, owner="name")

# 岗位
doc.text(info_x, info_y + 38, "夜班护士 · 重症监护室", 16, SLATE, owner="position")

# 所属站点
doc.text(info_x, info_y + 62, "所属站点：人民医院南站", 14, MUTED, owner="station")

# ============================================================ 健康状态卡片
health_y = avatar_y + 110

# 健康状态标题
doc.text(48, health_y, "健康状态", 18, WHITE, bold=True, owner="health_title")

# 健康状态：良好
status_y = health_y + 32
doc.rect(48, status_y, 210, 44, GREEN, radius=8, opacity=0.15)
doc.rect(58, status_y + 14, 16, 16, GREEN, radius=8)
doc.text(84, status_y + 10, "状态：良好", 16, GREEN_L, bold=True, owner="health_status")

# 体温
temp_y = status_y + 56
doc.rect(48, temp_y, 210, 44, NIGHT_MID, radius=8)
doc.text(60, temp_y + 10, "体温", 14, SLATE, owner="temp_label")
doc.text_r(248, temp_y + 8, "36.5°C", 18, GREEN_L, bold=True, owner="temp_value")

# 血压
bp_y = temp_y + 56
doc.rect(48, bp_y, 210, 44, NIGHT_MID, radius=8)
doc.text(60, bp_y + 10, "血压", 14, SLATE, owner="bp_label")
doc.text_r(248, bp_y + 8, "118/76", 18, WHITE, bold=True, owner="bp_value")

# ============================================================ 右侧紧急联系人
ec_x = 280
ec_y = health_y + 32

# 紧急联系人标题
doc.text(ec_x, health_y, "紧急联系", 18, WHITE, bold=True, owner="ec_title")

# 紧急联系人 1
ec1_y = health_y + 32
doc.rect(ec_x, ec1_y, 210, 44, ROSE, radius=8, opacity=0.15)
doc.text(ec_x + 12, ec1_y + 10, "爱人  王芳", 16, ROSE_L, bold=True, owner="ec1_name")

# 紧急联系人 2
ec2_y = ec1_y + 56
doc.rect(ec_x, ec2_y, 210, 44, ROSE, radius=8, opacity=0.10)
doc.text(ec_x + 12, ec2_y + 10, "姐姐  李红梅", 16, ROSE_L, bold=True, owner="ec2_name")

# 紧急联系人电话
ec_phone_y = ec2_y + 56
doc.text(ec_x, ec_phone_y, "紧急电话", 14, SLATE, owner="ec_phone_label")
doc.text(ec_x, ec_phone_y + 22, "400-888-0000", 22, AMBER, bold=True, owner="ec_phone_value")

# ============================================================ 分割线
doc.line_h(48, W - 48, bp_y + 80, NIGHT_LGT, 1)

# ============================================================ 底部信息
bottom_y = bp_y + 100

# 过敏信息
doc.text(48, bottom_y, "过敏信息", 16, WHITE, bold=True, owner="allergy_title")
doc.text(48, bottom_y + 26, "青霉素 · 海鲜 · 花生", 16, RED, owner="allergy_data")

# 血型
blood_y = bottom_y + 56
doc.text(48, blood_y, "血型", 16, WHITE, bold=True, owner="blood_title")
doc.text(48, blood_y + 26, "O 型", 28, RED, bold=True, owner="blood_value")

# 右侧：紧急说明
doc.text(280, bottom_y, "紧急说明", 16, WHITE, bold=True, owner="emergency_title")
doc.text(280, bottom_y + 26, "夜班期间如遇不适，", 14, SLATE, owner="emergency_desc1")
doc.text(280, bottom_y + 48, "请联系站点健康站", 14, SLATE, owner="emergency_desc2")
doc.text(280, bottom_y + 70, "或拨打支援热线", 14, SLATE, owner="emergency_desc3")

# ============================================================ 底部条
doc.rect(0, H - 80, W, 80, AMBER, radius=0, opacity=0.1)
doc.text_c(W // 2, H - 64, "夜里有光 · 路有驿站", 18, AMBER, bold=True, owner="slogan")
doc.text_c(W // 2, H - 36, "www.yeguang-yizhan.com", 12, AMBER_L, owner="url")

# 底部光晕装饰
for i in range(5, 0, -1):
    doc.rect(0, H - i * 15, W, 15, AMBER, radius=8, opacity=0.04 * i)

# ============================================================ 干跑门禁
# 数字卡片作品，最小字号放宽到 12px（目标观看距离 0.3-0.5 米）
gates = K.dry_run(doc, "case-03", 12, [], max_parts=9000)
K.save_gates("case-03", gates, "初始版本")
K.assert_gates(gates, "case-03")

# ============================================================ 渲染
stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print(f"Canvas: {W}x{H}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-03", doc, "夜班通行证", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))