# -*- coding: utf-8 -*-
"""B05 水线 Waterline — single source of truth for the shared product world.

Everything cross-screen consistent lives here: the city, the water points
(name/depth/trend/risk), the REAL rainfall-warning anchor, the DEMO depth-risk
rule, vehicle clearance, routes, personas, timestamps. Case scripts import this
so no screen can contradict another. Generation-time assertions guarantee the
geometry/semantics are internally consistent before any DSL is emitted.

Real vs demo (per AGENTS.md): the 暴雨预警信号 grade text is REAL (CMA standard,
SRC-01). Everything else — city name, point names, depths, sensors, vehicles,
reports — is FICTIONAL demo content, marked as such in portfolio/case.md.
"""
import datetime

# ---------------- REAL anchor (CMA, SRC-01) ----------------
# 暴雨预警信号四级 (blue/yellow/orange/red). We are under ORANGE right now.
RAIN_WARN = {
    "grade": "橙色",
    "grade_en": "ORANGE",
    "real_text": "3小时内降雨量将达50毫米以上，或已达50毫米以上且降雨可能持续",
    "source": "中国气象局《暴雨预警信号》标准（真实）",
}
RAIN_WARN_ALL = [
    ("蓝色", "12小时降雨量将达50毫米以上"),
    ("黄色", "6小时降雨量将达50毫米以上"),
    ("橙色", "3小时降雨量将达50毫米以上"),
    ("红色", "3小时降雨量将达100毫米以上"),
]

# ---------------- fictional world ----------------
CITY = "云州市"
CITY_EN = "YUNZHOU"
NOW = "08:15"
# The whole suite runs on Wed 2026-10-21 (+08:00), which is also plan-v1's
# established_at and a weekday (asserted below). cases 06/07/08 render the
# Chinese form directly, so keep one ISO value + one CN rendering to stop the
# screens from disagreeing about what day it is.
NOW_DATE = "2026-10-21"
NOW_DATE_CN = "10月21日"
NOW_DATE_WEEKDAY = "周三"
USER = "林岚"
DISTRICTS = ["滨江区", "城南区", "高新区"]


def _weekday(dstr):
    y, m, d = [int(x) for x in dstr.split("-")]
    return datetime.date(y, m, d).weekday()   # 0=Mon


# ---------------- DEMO depth-risk rule (product's own, NOT a real standard) ----
# depth in cm -> (label, level 0..3, hex color). Consistent across every screen.
RISK_BANDS = [
    (0.0, 10.0, "可通行", 0, "#12B886"),
    (10.0, 20.0, "谨慎", 1, "#2E86DE"),
    (20.0, 30.0, "建议绕行", 2, "#F2A93B"),
    (30.0, 999.0, "禁止通行", 3, "#E4572E"),
]
RISK_DEMO_NOTE = "演示风险分级规则（产品自定，非官方标准）"


def risk_of(depth_cm):
    """Return (label, level, color) for a water depth in cm."""
    for lo, hi, label, level, color in RISK_BANDS:
        if lo <= depth_cm < hi:
            return label, level, color
    raise AssertionError("depth %r out of band" % depth_cm)


def risk_color(depth_cm):
    return risk_of(depth_cm)[2]


def risk_label(depth_cm):
    return risk_of(depth_cm)[0]


# pedestrian thresholds differ (demo rule) — used in rider/pedestrian mode
PED_BANDS = [
    (0.0, 5.0, "可通行", 0, "#12B886"),
    (5.0, 10.0, "注意", 1, "#2E86DE"),
    (10.0, 999.0, "建议绕行", 2, "#F2A93B"),
]


def ped_risk_of(depth_cm):
    for lo, hi, label, level, color in PED_BANDS:
        if lo <= depth_cm < hi:
            return label, level, color
    raise AssertionError("ped depth %r" % depth_cm)


# ---------------- water points (consistent world) ----------------
# id, name, district, depth_cm, trend('rising'/'steady'/'falling'),
# updated_at, sensor_id, crowd_count
POINTS = [
    ("P1", "滨江路下穿隧道", "滨江区", 32.0, "rising", "08:12", "WL-BJ-001", 4),
    ("P2", "城南大道涵洞", "城南区", 22.0, "steady", "08:10", "WL-CN-014", 2),
    ("P3", "高新桥下", "高新区", 15.0, "rising", "08:13", "WL-GX-007", 3),
    ("P4", "解放路地道", "滨江区", 8.0, "falling", "08:11", "WL-BJ-023", 1),
    ("P5", "江畔公园低洼", "滨江区", 12.0, "rising", "08:09", "WL-BJ-041", 2),
    ("P6", "站前广场地下通道", "城南区", 26.0, "rising", "08:14", "WL-CN-002", 5),
]
PMAP = {p[0]: p for p in POINTS}
HERO = "P1"          # 滨江路下穿隧道 32cm — the through-line across screens

TREND_TXT = {"rising": "上升", "steady": "持平", "falling": "下降"}
TREND_ARROW = {"rising": "↑", "steady": "→", "falling": "↓"}


def pt(pid):
    return PMAP[pid]


def depth(pid):
    return PMAP[pid][3]


def pname(pid):
    return PMAP[pid][1]


def pdistrict(pid):
    return PMAP[pid][2]


def ptrend(pid):
    return PMAP[pid][4]


def ptime(pid):
    return PMAP[pid][5]


def psensor(pid):
    return PMAP[pid][6]


def pcrowd(pid):
    return PMAP[pid][7]


def prisk(pid):
    return risk_of(depth(pid))


# counts used consistently on overview / command screens
def n_blocked():
    return sum(1 for p in POINTS if prisk(p[0])[1] >= 3)


def n_detour():
    return sum(1 for p in POINTS if prisk(p[0])[1] == 2)


def n_caution():
    return sum(1 for p in POINTS if prisk(p[0])[1] == 1)


def n_open():
    return sum(1 for p in POINTS if prisk(p[0])[1] == 0)


# ---------------- vehicle clearance (demo) ----------------
# user's sedan min ground clearance in mm. Passable iff depth < clearance.
CAR_CLEAR_MM = 140
CAR_NAME = "私家车 · 最小离地间隙 140mm"


def car_passable(depth_cm):
    """demo rule: a car clears water shallower than its ground clearance."""
    return depth_cm * 10.0 < CAR_CLEAR_MM


# ---------------- routes for navigation screen ----------------
# (name, min, crosses point ids, reason)
ROUTES = [
    ("最短路线", 12, ["P1", "P4"], "经滨江路下穿隧道（禁止通行）"),
    ("避水路线", 17, ["P3", "P4"], "绕行高新桥下与解放路地道"),
    ("地面辅路", 21, ["P5"], "全程地面，涉江畔公园低洼"),
]
ROUTE_RECO = 1        # index of recommended = 避水路线


# ---------------- personas ----------------
PERSONAS = {
    "commuter": ("林岚", "通勤族 · 滨江CBD 上班"),
    "rider": ("阿杰", "外卖骑手 · 电动车"),
    "operator": ("运维员 · 城南排水班组", "城市排水值守"),
    "commander": ("应急指挥席", "市级防汛值守"),
}


# ---------------- weekly report data (case-10) ----------------
WEEK = {
    "detours": 5,
    "saved_min": 40,
    "reports": 3,
    "adopted": 2,
    "points_covered": 6,
    "longest_block_min": 28,
    "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    # rain mm per day (demo), used for a bar sparkline
    "rain_mm": [6, 18, 42, 55, 31, 12, 4],
    "avoided": [0, 1, 2, 1, 1, 0, 0],   # detours per day
}

# ---------------- crowd reports (case-07 / case-08) ----------------
REPORT = {
    "point": "P6",                 # 站前广场地下通道
    "reporter": USER,
    "est_depth": 26.0,
    "ref": "水面接近台阶第二级（参考：台阶高约15cm）",
    "confidence": 0.8,
    "status": "待复核",
    "submitted": "08:07",
}
MOD_QUEUE = [
    ("#1042", "站前广场地下通道", 26.0, "待复核", "08:07", 0.8),
    ("#1041", "滨江路下穿隧道", 31.5, "已采纳", "07:58", 0.9),
    ("#1039", "江畔公园低洼", 12.0, "已采纳", "07:41", 0.7),
    ("#1037", "解放路地道", 6.5, "已驳回", "07:30", 0.4),
]

# ---------------- alert push cards (case-06) ----------------
ALERTS = [
    ("橙色预警", "云州市气象台 08:00 发布", "3小时内降雨量将达50毫米以上", "real"),
    ("滨江路下穿隧道 禁止通行", "水深 32cm · 仍在上升 · 08:12", "建议立即改走解放路地道", "point"),
    ("你的避水路线已生成", "较最短路线 +5 分钟，避开 1 处禁止通行", "查看路线", "route"),
]

# ---------------- operations (case-08) ----------------
OPS = {
    "sensors_online": 46,
    "sensors_total": 52,
    "pump_stations": [("滨江1号泵站", "运行", 88), ("城南2号泵站", "运行", 64),
                      ("高新泵站", "检修", 0)],
    "incidents_open": 3,
    "staff_on_duty": 12,
}

# ---------------- command wall (case-09) ----------------
ESCALATION = [
    ("08:00", "市气象台发布暴雨橙色预警", "自动"),
    ("08:06", "滨江路下穿隧道 禁止通行", "系统"),
    ("08:09", "调派城南排水班组前往 P6", "指挥席"),
    ("08:14", "站前广场地下通道 水位仍上升", "系统"),
]


# ---------------- generation-time consistency assertions ----------------
def _check():
    # risk mapping sanity
    assert risk_of(32.0)[1] == 3 and risk_of(32.0)[0] == "禁止通行"
    assert risk_of(22.0)[1] == 2 and risk_of(22.0)[0] == "建议绕行"
    assert risk_of(15.0)[1] == 1 and risk_of(15.0)[0] == "谨慎"
    assert risk_of(8.0)[1] == 0 and risk_of(8.0)[0] == "可通行"
    assert risk_color(32.0) == "#E4572E"
    # pedestrian mapping
    assert ped_risk_of(26.0)[0] == "建议绕行"
    assert ped_risk_of(6.0)[0] == "注意"
    # hero point is the forbidden underpass, used across screens
    assert HERO == "P1" and depth("P1") == 32.0
    assert prisk("P1")[1] == 3
    # vehicle clearance: 32cm not passable, 8cm passable, 12cm passable (12<14)
    assert car_passable(32.0) is False
    assert car_passable(8.0) is True
    assert car_passable(12.0) is True
    assert car_passable(15.0) is False      # 15cm > 14cm clearance
    # counts add up to total points
    total = len(POINTS)
    assert n_blocked() + n_detour() + n_caution() + n_open() == total
    # trends are valid
    for p in POINTS:
        assert p[4] in TREND_TXT
    # recommended route avoids the forbidden point
    reco = ROUTES[ROUTE_RECO]
    assert "P1" not in reco[2], "recommended route must avoid the blocked point"
    # recommended route is the middle time option (sane demo)
    assert ROUTES[0][1] < reco[1] < ROUTES[2][1]
    # now is a weekday (commute scenario)
    wd = _weekday(NOW_DATE)
    assert wd <= 4, "commute scenario should be a weekday, got %r" % wd
    # week data lengths
    assert len(WEEK["rain_mm"]) == 7 and len(WEEK["avoided"]) == 7
    assert WEEK["adopted"] <= WEEK["reports"]
    # ops sensors consistent
    assert OPS["sensors_online"] <= OPS["sensors_total"]
    # moderation queue depths consistent with world for known points
    modmap = {m[1]: m for m in MOD_QUEUE}
    assert abs(modmap["滨江路下穿隧道"][2] - depth("P1")) < 1.0   # ~31.5 vs 32
    assert abs(modmap["江畔公园低洼"][2] - depth("P5")) < 1.0
    print("b05_data consistency checks: ALL PASS")


_check()
