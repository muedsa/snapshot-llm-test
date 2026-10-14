"""B02 shared data for the 水位线 community flood network.

One module owns every number the ten touchpoints print: station series, the four-level
action rule, the risk grid, shelters, tonight's roster and tasks, the supply cabinet and
the quarterly log. Each generator imports this, so a figure on the poster, the app, the
dispatch wall and the quarterly report can be cross-checked against one another.
All content is synthetic and labelled as such on the artefacts themselves.

Run:  python tmp/<run_id>/B02/data.py      # writes data-snapshot.json and prints checks
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B02"

ORG = "水位线"
ORG_EN = "TIDELINE · 社区内涝预警与互助网络"
CAMPAIGN = "雨前 20 分钟，知道该往哪走"
PHONE_STREET = "街道防汛值班 0731-8819-1234"
PHONE_CITY = "市应急 12350"
JOIN = "小程序「水位线」→ 输入门牌后 4 位绑定本社区"

# ---- thresholds (cm water level at the gauge) and the four action levels -------------
LEVELS = [
    {"code": 1, "name": "关注", "colour": "#2E7D5B", "ink": "#FFFFFF",
     "action": "留意推送，清理门口篦子，无需转移"},
    {"code": 2, "name": "警戒", "colour": "#1E88A8", "ink": "#FFFFFF",
     "action": "志愿者到岗，低层商户挡水板就位，车辆移出地下"},
    {"code": 3, "name": "紧急", "colour": "#E08A1E", "ink": "#1D2530",
     "action": "沿河 200 m 内一层人员撤到集合点，电梯停用，断电按预案"},
    {"code": 4, "name": "灾难", "colour": "#C6412F", "ink": "#FFFFFF",
     "action": "全部集合点开放，禁止返回，清点人数并上报失联"},
]
WARN_CM, CRIT_CM, DISASTER_CM = 42, 58, 74

STATIONS = [
    # id, name, gauge height today (cm), 24 h hourly series (cm), drainage capacity share
    ("W-01", "化纤厂家前", 63.5, None, 0.44),
    ("W-02", "南门桥下", 71.0, None, 0.31),
    ("W-03", "书院路口", 48.5, None, 0.58),
    ("W-04", "沿江北巷", 39.0, None, 0.66),
    ("W-05", "纺织厂排水口", 55.5, None, 0.37),
    ("W-06", "老码头闸口", 27.5, None, 0.72),
]


def series(seed: int, peak: float, hours: int = 24):
    """Deterministic rising-limb hydrograph ending at `peak` cm."""
    out = []
    for h in range(hours):
        t = h / (hours - 1)
        base = peak * (0.30 + 0.62 * t ** 1.9)
        ripple = 1.8 * math.sin((h + seed * 3) * 1.1) + 0.9 * math.sin((h + seed) * 2.7)
        out.append(round(max(2.0, base + ripple * (1 - 0.55 * t)), 1))
    out[-1] = round(peak, 1)
    return out


for i, (sid, name, now, _, drain) in enumerate(STATIONS):
    STATIONS[i] = (sid, name, now, series(i + 1, now), drain)


def classify(cm: float) -> int:
    return 4 if cm >= DISASTER_CM else 3 if cm >= CRIT_CM else 2 if cm >= WARN_CM else 1


def level_of(sid: str) -> int:
    for s in STATIONS:
        if s[0] == sid:
            return classify(s[2])
    raise KeyError(sid)


CURRENT_LEVEL = max(classify(s[2]) for s in STATIONS)
TOP_STATION = max(STATIONS, key=lambda s: s[2])

# ---- shelters -------------------------------------------------------------------------
SHELTERS = [
    # code, name, plan x, plan y (0..1), capacity, storey, open_now
    ("L-01", "实验小学门厅", 0.22, 0.30, 260, "2F", True),
    ("L-02", "江北文化站", 0.46, 0.18, 180, "2F", True),
    ("L-03", "老粮库广场", 0.63, 0.44, 420, "1F", True),
    ("L-04", "纺织厂俱乐部", 0.78, 0.26, 150, "2F", False),
    ("L-05", "南门高架平台", 0.40, 0.66, 300, "3F", True),
]
WALK_MIN = 8                        # minutes to reach a shelter at 80 m/min
SHELTER_RADIUS_M = WALK_MIN * 80
GATE = (0.30, 0.55)                 # the community entrance the poster measures from
DETOUR = 1.25                       # street network vs. straight line


def shelter_reach(code):
    """(metres, minutes) from the community gate, same numbers on every touchpoint."""
    _, _, fx, fy, cap, storey, opened = next(s for s in SHELTERS if s[0] == code)
    m = math.hypot((fx - GATE[0]) * KM_W * 1000, (fy - GATE[1]) * KM_H * 1000) * DETOUR
    return round(m / 10) * 10, round(m / 80)

# ---- risk grid ------------------------------------------------------------------------
NX, NY = 40, 25
KM_W, KM_H = 3.2, 2.0
RAIN_MM = 96.0                      # 3 h design storm used for the map
LOW_POINTS = [(0.24, 0.42, 1.00), (0.55, 0.30, 0.82), (0.70, 0.58, 0.66),
              (0.36, 0.72, 0.55), (0.86, 0.20, 0.40)]
CHANNEL = lambda x: 0.30 + 0.16 * math.sin(x * 5.1) + 0.10 * x      # river bank y(x)


def depth_factor(gx, gy):
    """How far below the drainage datum a cell sits, 0..1 (1 = lowest)."""
    e = 1.0 - 0.55 * math.exp(-((gx - 0.5) ** 2 + (gy - 0.9) ** 2) / 0.42)
    for cx, cy, amp in LOW_POINTS:
        e -= amp * 0.42 * math.exp(-(((gx - cx) ** 2) / 0.010 + ((gy - cy) ** 2) / 0.008))
    bank = CHANNEL(gx)
    e -= 0.30 * math.exp(-((gy - bank) ** 2) / 0.006)               # gully along the river
    return max(0.0, min(1.0, 1.0 - e))


def risk_value(gx, gy):
    """0..100 index = low-ness × rain ÷ drainage headroom."""
    low = depth_factor(gx, gy)
    head = 0.34 + 0.66 * (1 - abs(gx - 0.55))                       # pipe capacity falls off
    return 100.0 * min(1.0, (0.55 * low + 0.45 * low ** 0.7) * (RAIN_MM / 110.0) / head)


RISK_LEVELS = [(20, "低"), (40, "中"), (60, "较高"), (80, "高"), (1e9, "极高")]
RISK_COLOURS = ["#CFE0DC", "#9CC7B4", "#F0D9A2", "#E39B45", "#C6412F"]


def risk_class(v):
    for i, (hi, _) in enumerate(RISK_LEVELS):
        if v < hi:
            return i
    return len(RISK_LEVELS) - 1


def risk_grid():
    return [[risk_value((i + 0.5) / NX, (j + 0.5) / NY) for i in range(NX)] for j in range(NY)]


def risk_stats():
    g = [v for row in risk_grid() for v in row]
    hi = sum(1 for v in g if v >= 60) / len(g) * KM_W * KM_H
    return {"min": round(min(g), 1), "max": round(max(g), 1),
            "mean": round(sum(g) / len(g), 1), "area_high_km2": round(hi, 2),
            "cells": len(g)}


TRANSECT = ((0.06, 0.42), (0.96, 0.42))   # the A-B line drawn on the map


def transect(x0=TRANSECT[0][0], x1=TRANSECT[1][0], y=TRANSECT[0][1], n=48):
    return [(x, risk_value(x, y)) for x in
            [x0 + (x1 - x0) * k / n for k in range(n + 1)]]


# ---- pedestrian water-depth bands (street depth, NOT the gauge reading) -------------
PED = [(15, "可行", "#2E7D5B", "正常步行，注意井盖"),
       (30, "小心", "#1E88A8", "结伴慢行，避开下通道"),
       (50, "危险", "#E08A1E", "不进入；改走高处路线"),
       (999, "极危险", "#C6412F", "禁止通行，等待救援")]


def ped_band(cm):
    for hi, name, col, advice in PED:
        if cm < hi:
            return name, col, advice
    return PED[-1][1], PED[-1][2], PED[-1][3]


# ---- tonight: volunteers and tasks -----------------------------------------------------
ROLES = ["沙袋组", "转移组", "值守组", "上报核查组"]
VOLUNTEERS = []
_names = ("周敏 李国栋 陈艳 吴岸 张一鸣 赵磊 孙祺 钱雅 郑洪 冯三 褚卫 蒋涛 "
          "沈佳 韩雪 杨帆 朱桥 秦朗 尤溪").split()
for i, n in enumerate(_names):
    VOLUNTEERS.append({"name": n, "role": ROLES[i % 4],
                       "status": ("在岗" if i % 5 else "待命") if i < 14 else
                                 ("休息" if i % 2 else "离线"),
                       "since": f"{17 + i % 5:02d}:{(i * 7) % 60:02d}"})
ONLINE = [v for v in VOLUNTEERS if v["status"] in ("在岗", "待命")]
REGISTERED = 42

TASKS = [
    # id, type, place, priority, state, owner, eta_min
    ("T-41", "沙袋", "南门桥下 B 口", "紧急", "进行中", "李国栋", 12),
    ("T-42", "转移", "沿江北巷 12-18 号", "紧急", "进行中", "陈艳", 25),
    ("T-43", "值守", "W-02 水位站", "高", "进行中", "吴岸", 0),
    ("T-44", "上报核查", "书院路口 3 处积水", "高", "待接", None, 18),
    ("T-45", "物资", "L-03 物资柜开封", "中", "待接", None, 8),
    ("T-46", "转移", "老粮库一层 4 户", "紧急", "已完成", "张一鸣", 0),
    ("T-47", "排水", "纺织厂排水口清篦", "中", "已完成", "赵磊", 0),
    ("T-48", "上报核查", "L-05 平台人数清点", "高", "已完成", "孙祺", 0),
    ("T-49", "值守", "L-01 实验小学门厅", "中", "进行中", "钱雅", 0),
]
TASK_COUNTS = {k: sum(1 for t in TASKS if t[4] == k) for k in ("待接", "进行中", "已完成")}
OPEN_MIN = sum(t[6] for t in TASKS if t[4] != "已完成")

# ---- supply cabinet (case-08) ----------------------------------------------------------
SUPPLIES = [
    ("编织沙袋", "50 只", "2026-09-28", "OK"),
    ("挡水板（1.2 m）", "8 块", "2026-09-28", "OK"),
    ("潜水泵 220 V", "3 台", "2026-09-14", "待检电池"),
    ("救生绳 30 m", "4 条", "2026-09-28", "OK"),
    ("反光背心", "20 件", "2026-08-30", "缺 3 件"),
    ("应急灯", "12 支", "2026-09-28", "OK"),
    ("对讲机 433 MHz", "6 台", "2026-09-21", "1 台充电"),
    ("一次性雨衣", "60 件", "2026-09-28", "OK"),
    ("药品包", "4 套", "2026-07-05", "已过期，需更换"),
    ("名册与封条", "1 套", "2026-09-28", "OK"),
]
CABINET = "L-03 老粮库广场 · 03 号物资柜"

# ---- quarterly public report (case-09) -------------------------------------------------
MONTHS = ["7 月", "8 月", "9 月"]
QLOG = {
    "alerts_sent": [12, 31, 18],
    "drills": [2, 1, 3],
    "resident_reports": [46, 88, 57],
    "tasks_done": [38, 74, 51],
    "response_min_p50": [11.5, 9.2, 8.4],
    "response_min_p90": [26.0, 21.5, 19.2],
    "hours_volunteer": [126, 268, 173],
    "spend_wan": {"物资补充": 3.4, "培训与演练": 2.1, "设备维护": 1.6, "通信与平台": 0.9},
}
Q_TOTALS = {k: sum(v) for k, v in QLOG.items() if isinstance(v, list)}


def check():
    assert len(STATIONS) == 6 and all(len(s[3]) == 24 for s in STATIONS)
    assert CURRENT_LEVEL == 3, CURRENT_LEVEL   # 紧急级：最高站 71 cm，距灾难级 74 cm 还差 3 cm
    assert TOP_STATION[0] == "W-02" and CRIT_CM <= TOP_STATION[2] < DISASTER_CM
    assert sum(TASK_COUNTS.values()) == len(TASKS)
    assert len(ONLINE) == sum(1 for v in VOLUNTEERS if v["status"] in ("在岗", "待命"))
    assert Q_TOTALS["tasks_done"] == sum(QLOG["tasks_done"])
    st = risk_stats()
    assert 0 < st["min"] < st["max"] <= 100
    return {"current_level": CURRENT_LEVEL, "top_station": TOP_STATION[:3],
            "risk": st, "tasks": TASK_COUNTS, "online": len(ONLINE),
            "quarter": Q_TOTALS}


if __name__ == "__main__":
    snap = check()
    snap.update({
        "stations": [{"id": s[0], "name": s[1], "now_cm": s[2], "series_cm": s[3],
                      "drainage": s[4], "level": classify(s[2])} for s in STATIONS],
        "thresholds": {"warn_cm": WARN_CM, "crit_cm": CRIT_CM, "disaster_cm": DISASTER_CM},
        "levels": LEVELS, "shelters": SHELTERS,
        "volunteers": VOLUNTEERS, "tasks": [list(t) for t in TASKS],
        "supplies": [list(s) for s in SUPPLIES], "quarter": QLOG,
        "risk_levels": RISK_LEVELS, "risk_colours": RISK_COLOURS,
        "transect": [[round(x, 3), round(v, 1)] for x, v in transect()],
    })
    (TMP / "data-snapshot.json").write_text(json.dumps(snap, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    print(json.dumps({k: snap[k] for k in ("current_level", "risk", "tasks", "online",
                                           "quarter")}, ensure_ascii=False))
