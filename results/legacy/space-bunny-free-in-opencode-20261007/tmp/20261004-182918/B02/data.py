# -*- coding: utf-8 -*-
"""B02 project data model - ONE source of truth for every touchpoint.

百工社 (BAIGONG) is a SELF-INVENTED but operationally realistic community tool
library / repair station. Every organisation, person, address, phone number and
figure below is fabricated demonstration content written for this design task.
No real org, person, quote, statistic or endorsement is referenced or claimed.
"""

ORG = "百工社"
ORG_EN = "BAIGONG"
FULL_EN = "XINHUALI NEIGHBOURHOOD TOOL LIBRARY"
SITE = "新华里街道社区服务中心 1 层"
ADDR1 = "沿河路 12 号"
ADDR2 = "新华里街道 · 沿河路 12 号 · 社区服务中心 1 层"
TEL = "0512-8873 4162"
SITE_SHORT = "bai-gong.org"

# ---------------------------------------------------------------- inventory
CATS = [
    # name, count, glyph, note
    ("手动工具", 412, "wrench", "螺丝 钳子 扳手"),
    ("电动工具", 176, "drill", "电钻 砂磨 热风"),
    ("家居装修", 143, "ruler", "腻子 滚筒 密封"),
    ("测量器具", 131, "tape", "卷尺 水平仪 测距"),
    ("木工", 118, "saw", "锯 刨 凿"),
    ("登高安全", 96, "ladder", "人字梯 安全带"),
    ("园艺", 96, "leaf", "枝剪 割草"),
    ("缝纫织补", 68, "sewing", "缝纫机 拷边机"),
]
assert sum(c[1] for c in CATS) == 1240

# shelf labels, two densities (case-03)
SHELF_DENSE = [
    ("T-0412", "手持电钻 12V", "电动工具", "可借", "pine"),
    ("T-0588", "斜口钳 200mm", "手动工具", "可借", "pine"),
    ("T-0301", "激光测距仪 40m", "测量器具", "校准中", "brass"),
    ("T-0704", "人字梯 2.4m", "登高安全", "已借出", "rust"),
    ("T-0915", "台式缝纫机", "缝纫织补", "可借", "pine"),
]
SHELF_BASIC = [
    ("T-0102", "钢丝钳 175mm", "可借", "pine"),
    ("T-0640", "手锯 450mm", "可借", "pine"),
    ("T-0733", "热风枪 2000W", "已借出", "rust"),
    ("T-0188", "水平尺 600mm", "可借", "pine"),
    ("T-0855", "枝剪 200mm", "待校验", "brass"),
    ("T-0266", "曲线锯 650W", "可借", "pine"),
    ("T-0470", "砂纸磨头套装", "可借", "pine"),
    ("T-0990", "梯垫防滑条", "在架", "pine"),
]

# ---------------------------------------------------------------- 2025 facts
YEAR = 2025
BORROWS = 18640
MEMBERS = 862
MEMBERS_SPLIT = [("年卡", 411), ("月卡", 300), ("社区义工证", 151)]
assert sum(m[1] for m in MEMBERS_SPLIT) == MEMBERS
IN_STOCK = 1240
LENDABLE = 1086
IN_REPAIR = 96
RETIRED = 58
assert LENDABLE + IN_REPAIR + RETIRED == IN_STOCK
AVG_DAYS = 6.2
OVERDUE = 412
OVERDUE_RATE = 0.022
SHELF_CLOCK = 5402          # 自助取还柜使用次数
SHELF_SHARE = 0.29
CLINIC_NIGHTS = 52
CLINIC_VISITS = 3180
CLINIC_FIXED = 2417
CLINIC_FAIL = [("修不好·缺零件", 245), ("需送外部专业维修", 132),
               ("已彻底损坏", 318), ("主人放弃·不值得修", 68)]
assert sum(f[1] for f in CLINIC_FAIL) == CLINIC_VISITS - CLINIC_FIXED
CLASS_N = 24
CLASS_VISITS = 612
VOLUNTEERS = 46
VOL_HOURS = 5904
SAVE_YUAN = 86.4            # 万元: 居民购置支出节省（估算口径见 project-brief）

MONTHLY = [("1月", 1180), ("2月", 902), ("3月", 1610), ("4月", 1520), ("5月", 1690),
           ("6月", 1450), ("7月", 1418), ("8月", 1380), ("9月", 1740), ("10月", 1860),
           ("11月", 1980), ("12月", 1910)]
assert sum(m[1] for m in MONTHLY) == BORROWS

# ---------------------------------------------------------------- places
PICKUPS = [
    ("主站", "沿河路 12 号 · 服务中心 1 层", "周二至周日 10:00-19:00", "scale"),
    ("小学自助柜", "新华里小学 西门外", "每日 07:00-21:00 扫码取还", "cart"),
    ("宿舍区站点", "纺机厂宿舍 7 号楼", "周六 14:00-17:00 志愿者值守", "shelf"),
]

# ---------------------------------------------------------------- card sample
CARD_NAME = "陈惠兰"
CARD_NO = "BG-2025-0873"
CARD_TIER = "年卡"
CARD_TIER_RULE = "年卡 · 每月 20 次 · 每次 7 天"
CARD_USED = 6
CARD_QUOTA = 20
CARD_EXP = "2026-09-30"
CARD_SINCE = "2021-04-18"

# ---------------------------------------------------------------- clinic night
CLINIC_TITLE = "修理夜 · 第 52 场"
CLINIC_DATE = "12 月 31 日 周三 19:00-21:30"
CLINIC_SHORT = "12 月 31 日 周三"
CLINIC_PLACE = "沿河路 12 号 一层 · 8 张工作台"
CLINIC_MENTOR = "王建国 · 志愿者编号 V-07 · 电工 / 自行车"
CLINIC_THEME = "灯具、电线与年关安全检查"
SLOTS_TOTAL = 8
SLOTS_LEFT = 3
CLINIC_ITEMS = [
    ("台灯忽明忽暗", "台灯 / 落地灯", "电气"),
    ("插线板发烫有味", "插线板 / 排插", "电气"),
    ("单车后闸失灵", "26 寸通勤车", "车行"),
    ("羽绒服拉链坏了", "衣物 · 拉链", "织补"),
]
# repair-night ledger, 6 months (units fixed)
LEDGER = [("7月", 186), ("8月", 199), ("9月", 214), ("10月", 231),
          ("11月", 228), ("12月", 217)]
LEDGER_FAIL = [("待零件", 34), ("报废", 6)]
HELP_SPECIALTIES = ["焊补", "水暖", "钟表", "键盘 / 家电板"]
TONIGHT_MIX = [("灯具", 4, "IRON"), ("自行车", 3, "BRASS"),
               ("插排线缆", 2, "PINE"), ("衣物织补", 1, "RUST")]

# ---------------------------------------------------------------- print tokens
NOTICE_TITLE = "工具义诊日"
NOTICE_SUB = "带上家里那把修不动的工具，我们一起修"
NOTICE_DATE = "1 月 11 日 周六 09:00-16:00"
NOTICE_SLOT = "先到先约 · 也可到现场候补"

# ---------------------------------------------------------------- overdue slip
SLIP_DAYS = 3
SLIP_BORROW = "12 月 24 日"
SLIP_DUE = "12 月 31 日"
SLIP_FEE = "¥1 / 天"
SLIP_TOOL = "T-0412 手持电钻 12V"

# ---------------------------------------------------------------- donation box
DONATE_OK = ["闲置五金", "完好电器", "儿童安全座椅", "缝纫机与配件", "园艺工具"]
DONATE_NO = ["带电未插电测试的插线板", "生锈到无法辨认的刀具",
             "容量超过 60L 的旧家具", "无说明书的高压清洗机"]
DONATE_MONTH = [("入库编号上架", 41, "PINE"), ("转送其他社区", 15, "BLUE"),
                ("还在评估", 6, "BRASS")]
DONATE_TOTAL = 62          # 41 + 15 + 6
assert sum(p[1] for p in DONATE_MONTH) == DONATE_TOTAL

VOLUNTEERS = [("王建国", "电工 / 自行车 · V-07", 620),
              ("李秀芳", "缝纫与织补 · V-12", 540),
              ("陈永康", "木工与家具 · V-03", 480),
              ("周敏", "水暖与五金 · V-21", 392)]
assert sum(v[2] for v in VOLUNTEERS) == 2032

# ---------------------------------------------------------------- report
REPORT_TITLE = "2025 年度透明报告"
REPORT_SUB = "百工社 · 新华里街道社区工具图书馆"
GOALS = [
    ("会员", "862 人", 862, 1000),
    ("可借工具", "1,086 件", 1086, 1240),
    ("修理夜修好率", "76.0%", 2417, 3180),
    ("工具准时归还率", "97.8%", 1 - OVERDUE_RATE, 1),
]
