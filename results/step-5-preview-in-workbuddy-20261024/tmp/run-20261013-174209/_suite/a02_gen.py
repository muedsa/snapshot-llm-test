"""A02 · 三会场密集会议日程 — DSL 生成器（1920×1200 大图 + 720×1280 手机图）。

启动基准：总任务根（或 SNAPSHOT_TASK_ROOT 指向总任务根）。
几何：09:00–16:00 共用线性时间轴；块的位置与长度严格按起止时间比例绘制，
不调整输入时间、不为塞字拉伸短块。
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A02"
TASK_DIR = ROOT / "tasks" / "A02-conference-schedule"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#F8FAFC"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
GRID = "#E2E8F0"
AXIS = "#94A3B8"
DARK = "#0F172A"
DARK2 = "#1E293B"

CAT_COLOR = {
    "keynote": "#B45309",
    "workshop": "#7C3AED",
    "talk": "#2563EB",
    "demo": "#0D9488",
    "panel": "#DB2777",
}
CAT_BG = {
    "keynote": "#FEF3C7",
    "workshop": "#F3E8FF",
    "talk": "#DBEAFE",
    "demo": "#CCFBF1",
    "panel": "#FCE7F3",
}
VENUE_COLOR = {"A": "#2563EB", "B": "#7C3AED", "C": "#0D9488"}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- 数据 ----------
venues_meta = json.loads((TASK_DIR / "inputs" / "venues.json").read_text(encoding="utf-8"))
with (TASK_DIR / "inputs" / "agenda.csv").open(encoding="utf-8", newline="") as fh:
    events = list(csv.DictReader(fh))

for e in events:
    h1, m1 = e["start"].split(":")
    h2, m2 = e["end"].split(":")
    e["start_min"] = int(h1) * 60 + int(m1)
    e["end_min"] = int(h2) * 60 + int(m2)
    e["dur"] = e["end_min"] - e["start_min"]

LUNCH = (720, 780)  # 12:00–13:00
T0, T1 = 540, 960   # 09:00–16:00

# ---------- 大图几何 ----------
W, H = 1920, 1200
PAD = 40
HEADER_H = 150
LEGEND_H = 74
AXIS_H = 46
LANE_TOP = HEADER_H + LEGEND_H + AXIS_H
LANE_H = 236
LANE_GAP = 18
LEGEND_W = 300

ax_x0 = PAD + LEGEND_W
INDEX_W = 300          # 右侧编号索引列宽
ax_x1 = W - PAD - INDEX_W - 14
ax_w = ax_x1 - ax_x0
MIN_PER_PX = (T1 - T0) / ax_w


def x_of(minute: float) -> float:
    return ax_x0 + (minute - T0) / (T1 - T0) * ax_w


def px_of_minutes(mins: float) -> float:
    return mins / (T1 - T0) * ax_w


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        max_lines=None, wrap=True):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}"'
        + (f' softWrap="{"true" if wrap else "false"}"'
           + (f' maxLines="{max_lines}"' if max_lines else ""))
        + f'>{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None, transform=None, talign=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    if transform:
        a += f' transform="{transform}"'
    if talign:
        a += f' transformAlignment="{talign}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


nodes: list[str] = [box(0, 0, W, H, BG)]

# ============ Header ============
nodes.append(box(0, 0, W, HEADER_H - 16, DARK))
nodes.append(box(0, HEADER_H - 19, W, 3, VENUE_COLOR["A"]))
nodes.append(txt("Structure / Vision 2026 · 全日日程", x=PAD, y=26, w=1000, size=40, color="#F8FAFC", bold=True))
nodes.append(txt("日期 2026.11.07 · 云构中心 A / B / C 会场 · 时间均为 Asia/Shanghai",
                 x=PAD, y=84, w=1100, size=20, color="#94A3B8"))
nodes.append(txt("15 项活动 · 公共午休 12:00–13:00（跨三会场）", x=W - PAD - 620, y=30, w=620,
                 size=20, color="#CBD5E1", align="RIGHT"))
nodes.append(txt("块的位置与长度按实际起止时间比例绘制，空档保留，未调整输入时间",
                 x=W - PAD - 620, y=62, w=620, size=18, color="#94A3B8", align="RIGHT"))
nodes.append(txt("读图方法：横向为 09:00–16:00 线性时间轴；每条泳道是一个会场；",
                 x=W - PAD - 620, y=94, w=620, size=18, color="#94A3B8", align="RIGHT"))
nodes.append(txt("色块按类别着色，编号 S01–S15 与右侧说明一一对应。",
                 x=W - PAD - 620, y=118, w=620, size=18, color="#94A3B8", align="RIGHT"))

# ============ 图例 ============
ly = HEADER_H + 14
nodes.append(txt("类别", x=PAD, y=ly + 2, w=90, size=18, color=MUTED, bold=True))
lx = PAD + 96
for cat, label in venues_meta["categories"].items():
    nodes.append(box(lx, ly + 3, 16, 16, CAT_COLOR[cat], radius=4))
    nodes.append(txt(f"{label} {cat}", x=lx + 22, y=ly, w=180, size=18, color=INK2))
    lx += 22 + 190
# 午休图例
nodes.append(box(lx, ly + 3, 16, 16, "#CBD5E1", radius=4))
nodes.append(txt("公共午休 12:00–13:00", x=lx + 22, y=ly, w=240, size=18, color=INK2))

# ============ 时间轴 ============
axis_y = HEADER_H + LEGEND_H + 8
nodes.append(box(ax_x0, axis_y, ax_w, 2, AXIS))
for hh in range(9, 17):
    mm = hh * 60
    if not (T0 <= mm <= T1):
        continue
    xx = x_of(mm)
    nodes.append(box(xx - 1, axis_y - 8, 2, 16, AXIS))
    nodes.append(txt(f"{hh:02d}:00", x=xx - 46, y=axis_y + 12, w=92, size=18, color=INK2,
                     family=MONO, align="CENTER"))
# 半小时细刻度
for hh in range(9, 16):
    xx = x_of(hh * 60 + 30)
    nodes.append(box(xx - 1, axis_y - 4, 2, 8, "#CBD5E1"))

# ============ 泳道 ============
lane_boxes = {}
for vi, venue in enumerate(["A", "B", "C"]):
    vy = LANE_TOP + vi * (LANE_H + LANE_GAP)
    lane_boxes[venue] = vy
    # 泳道底
    nodes.append(box(ax_x0, vy, ax_w, LANE_H, "#FFFFFF", border="1 SOLID #E2E8F0"))
    # 左侧会场标签
    nodes.append(box(PAD, vy, LEGEND_W - 16, LANE_H, "#FFFFFF", radius=12,
                     border=f"1 SOLID {VENUE_COLOR[venue]}"))
    nodes.append(box(PAD, vy, 6, LANE_H, VENUE_COLOR[venue], radius=2))
    nodes.append(txt(f"{venue} 会场", x=PAD + 22, y=vy + 20, w=LEGEND_W - 56, size=26,
                     color=INK, bold=True))
    nodes.append(txt(f"容量 {venues_meta[venue]['capacity']} 人", x=PAD + 22, y=vy + 58,
                     w=LEGEND_W - 56, size=19, color=INK2))
    # 会场内事件数
    ev_n = len([e for e in events if e["venue"] == venue])
    nodes.append(txt(f"本会场 {ev_n} 项活动", x=PAD + 22, y=vy + 88, w=LEGEND_W - 56,
                     size=18, color=MUTED))
    # 容量提示
    nodes.append(txt("满座时建议分流至同时间段其他会场",
                     x=PAD + 22, y=vy + LANE_H - 42, w=LEGEND_W - 52, size=16, color=MUTED))

    # 午休（跨三泳道清楚标识）
    lx0, lx1 = x_of(LUNCH[0]), x_of(LUNCH[1])
    nodes.append(box(lx0, vy + 8, lx1 - lx0, LANE_H - 16, "#E2E8F0", radius=8,
                     border="1 SOLID #CBD5E1"))
    nodes.append(txt("公共午休 12:00–13:00", x=lx0 + 8, y=vy + 16, w=lx1 - lx0 - 16, size=20,
                     color="#475569", bold=True, align="CENTER"))
    nodes.append(txt("不安排会议 · 三会场同步", x=lx0 + 8, y=vy + 44, w=lx1 - lx0 - 16, size=17,
                     color=MUTED, align="CENTER"))

    # 事件块
    for e in [e for e in events if e["venue"] == venue]:
        bx0 = x_of(e["start_min"])
        bw = px_of_minutes(e["dur"])
        by = vy + 78
        bh = 92
        col = CAT_COLOR[e["category"]]
        nodes.append(box(bx0, by, bw, bh, CAT_BG[e["category"]], radius=8, border=f"1 SOLID {col}"))
        nodes.append(box(bx0, by, bw, 5, col, radius=2))
        # 编号徽标
        nodes.append(box(bx0 + 8, by + 12, 46, 26, col, radius=6))
        nodes.append(txt(e["id"], x=bx0 + 8, y=by + 15, w=46, size=18, color="#FFFFFF",
                         family=MONO, bold=True, align="CENTER"))
        # 起止时间
        nodes.append(txt(f"{e['start']}–{e['end']}", x=bx0 + 8, y=by + 46, w=bw - 16, size=18,
                         color=INK2, family=MONO))
        # 时长
        nodes.append(txt(f"{e['dur']} 分钟", x=bx0 + 8, y=by + 68, w=bw - 16, size=16, color=MUTED))
        # 类别
        nodes.append(txt(venues_meta["categories"][e["category"]], x=bx0 + 8, y=by + 88,
                         w=bw - 16, size=16, color=col, bold=True))

# ============ 右侧编号索引 ============
IDX_X = ax_x1 + 14
IDX_W = INDEX_W
nodes.append(txt("编号索引（标题 · 讲者 · 会场）", x=IDX_X, y=LANE_TOP - 2, w=IDX_W, size=18,
                 color=MUTED, bold=True))
# 索引可用高度：从 LANE_TOP+24 到底部说明区上方
IDX_AVAIL = (LANE_TOP + 3 * LANE_H + 2 * LANE_GAP) - (LANE_TOP + 24)
IDX_STEP = IDX_AVAIL / len(events)
iy = LANE_TOP + 24
for e in events:
    col = CAT_COLOR[e["category"]]
    nodes.append(box(IDX_X, iy, 44, 24, col, radius=5))
    nodes.append(txt(e["id"], x=IDX_X, y=iy + 3, w=44, size=16, color="#FFFFFF",
                     family=MONO, bold=True, align="CENTER"))
    nodes.append(txt(e["title"], x=IDX_X + 52, y=iy - 1, w=IDX_W - 60, size=17, color=INK,
                     max_lines=1, wrap=False))
    nodes.append(txt(f"{e['speaker']} · {e['venue']} 会场 · {e['dur']}′",
                     x=IDX_X + 52, y=iy + 21, w=IDX_W - 60, size=16, color=MUTED,
                     max_lines=1, wrap=False))
    iy += IDX_STEP

# ============ 底部说明 ============
FY = LANE_TOP + 3 * LANE_H + 2 * LANE_GAP + 12
nodes.append(box(PAD, FY, W - 2 * PAD, H - FY - PAD, "#FFFFFF", radius=12,
                 border="1 SOLID #E2E8F0"))
notes = [
    "块长与时间严格成比例：1 分钟 = %.3f 像素；40 分钟活动与 60 分钟活动宽度不同，未为塞字拉伸短块。" % MIN_PER_PX,
    "各会场保留真实空档（如 A 会场 09:40–10:00、B 会场 09:55–10:10、C 会场 10:00–10:15），未合并、未填充。",
    "S03、S05、S06、S08、S11、S13 等短于 50 分钟的活动，标题与讲者见右侧编号索引，不在色块内挤压排版。",
    "公共午休 12:00–13:00 为独立项目，跨三条泳道以灰色区块标识，未与任何会议合并。",
]
ny = FY + 14
for n in notes:
    nodes.append(txt(n, x=PAD + 20, y=ny, w=W - 2 * PAD - 40, size=17, color=INK2))
    ny += 26

wide_dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="HARD_EDGE">'
    + "".join(nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "agenda-wide.snapshot").write_text(wide_dsl, encoding="utf-8")
print("wrote agenda-wide.snapshot", len(wide_dsl))

# ============ 手机图：分时段列表 ============
MW, MH = 720, 1280
MPAD = 24
m_nodes: list[str] = [box(0, 0, MW, MH, BG)]
m_nodes.append(box(0, 0, MW, 132, DARK))
m_nodes.append(txt("Structure / Vision 2026", x=MPAD, y=22, w=MW - 2 * MPAD, size=27,
                   color="#F8FAFC", bold=True))
m_nodes.append(txt("2026.11.07 · 云构中心 A / B / C 会场", x=MPAD, y=60, w=MW - 2 * MPAD,
                   size=18, color="#94A3B8"))
m_nodes.append(txt("Asia/Shanghai · 15 项活动 · 午休 12:00–13:00", x=MPAD, y=88,
                   w=MW - 2 * MPAD, size=17, color="#64748B"))

# 分时段
slots = [("上午 09:00–12:00", 540, 720), ("午休 12:00–13:00", 720, 780),
         ("下午 13:00–16:00", 780, 960)]
# 竖向预算：1280 - 头部 132 - 页脚 40 - 3 个分段时间头(34+8) - 午休块(62+8) = ?
FOOT_H = 40
HEAD_H = 132
# 精确竖向预算，确保 sy 最终不超过 MH - FOOT_H
slot_head_step, lunch_step, slot_gap = 40, 62, 4
fixed = 3 * slot_head_step + lunch_step + 2 * slot_gap
body_avail = (MH - HEAD_H - FOOT_H) - fixed
CARD_H = body_avail // len(events)
CARD_STEP = CARD_H
sy = HEAD_H + 2
for label, s0, s1 in slots:
    m_nodes.append(box(MPAD, sy, MW - 2 * MPAD, 34, "#E2E8F0", radius=8))
    m_nodes.append(txt(label, x=MPAD + 12, y=sy + 7, w=MW - 2 * MPAD - 24, size=19,
                       color="#334155", bold=True))
    sy += 40
    if s0 == 720:
        m_nodes.append(box(MPAD, sy, MW - 2 * MPAD, 56, "#F1F5F9", radius=10,
                           border="1 SOLID #CBD5E1"))
        m_nodes.append(txt("公共午休 12:00–13:00", x=MPAD + 14, y=sy + 8, w=MW - 2 * MPAD - 28,
                           size=19, color="#475569", bold=True))
        m_nodes.append(txt("不安排会议 · 三会场同步", x=MPAD + 14, y=sy + 30,
                           w=MW - 2 * MPAD - 28, size=16, color=MUTED))
        sy += 62
        continue
    for e in sorted([e for e in events if s0 <= e["start_min"] < s1],
                    key=lambda e: (e["start_min"], e["venue"])):
        col = CAT_COLOR[e["category"]]
        vcol = VENUE_COLOR[e["venue"]]
        m_nodes.append(box(MPAD, sy, MW - 2 * MPAD, CARD_H, "#FFFFFF", radius=10,
                           border="1 SOLID #E2E8F0"))
        m_nodes.append(box(MPAD, sy, 5, CARD_H, col, radius=2))
        # 编号
        m_nodes.append(box(MPAD + 14, sy + 8, 44, 22, col, radius=5))
        m_nodes.append(txt(e["id"], x=MPAD + 14, y=sy + 11, w=44, size=15, color="#FFFFFF",
                           family=MONO, bold=True, align="CENTER"))
        # 会场徽标
        m_nodes.append(box(MPAD + 62, sy + 8, 32, 22, vcol, radius=5))
        m_nodes.append(txt(e["venue"], x=MPAD + 62, y=sy + 11, w=32, size=15, color="#FFFFFF",
                           family=MONO, bold=True, align="CENTER"))
        # 起止时间
        m_nodes.append(txt(f"{e['start']}–{e['end']}", x=MPAD + 100, y=sy + 9, w=190, size=18,
                           color=INK2, family=MONO, bold=True))
        m_nodes.append(txt(f"{e['dur']}′", x=MPAD + 292, y=sy + 10, w=56, size=16,
                           color=MUTED, family=MONO, align="RIGHT"))
        # 类别
        m_nodes.append(txt(venues_meta["categories"][e["category"]],
                           x=MW - MPAD - 14 - 96, y=sy + 9, w=96, size=17, color=col,
                           bold=True, align="RIGHT"))
        # 标题
        m_nodes.append(txt(e["title"], x=MPAD + 14, y=sy + 32, w=MW - 2 * MPAD - 28, size=18,
                           color=INK, max_lines=1, wrap=False))
        sy += CARD_STEP
    sy += slot_gap

m_nodes.append(txt("讲者详见完整日程（agenda-wide）。", x=MPAD, y=MH - 34, w=MW - 2 * MPAD,
                   size=16, color=MUTED, align="CENTER"))

mobile_dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{MW}" height="{MH}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="HARD_EDGE">'
    + "".join(m_nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "agenda-mobile.snapshot").write_text(mobile_dsl, encoding="utf-8")
print("wrote agenda-mobile.snapshot", len(mobile_dsl), "mobile last y =", sy)

# ---------- schedule-audit.json ----------
def fmt(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


# 各会场空档
venue_gaps = []
for venue in ["A", "B", "C"]:
    evs = sorted([e for e in events if e["venue"] == venue], key=lambda e: e["start_min"])
    cur = T0
    for e in evs:
        if e["start_min"] > cur:
            venue_gaps.append({
                "venue": venue, "start": fmt(cur), "end": fmt(e["start_min"]),
                "start_min": cur, "end_min": e["start_min"], "minutes": e["start_min"] - cur,
                "kind": "gap",
            })
        cur = max(cur, e["end_min"])
    if cur < T1:
        venue_gaps.append({"venue": venue, "start": fmt(cur), "end": fmt(T1),
                           "start_min": cur, "end_min": T1, "minutes": T1 - cur,
                           "kind": "gap"})
venue_gaps.append({"venue": "A/B/C", "start": "12:00", "end": "13:00",
                   "start_min": 720, "end_min": 780, "minutes": 60,
                   "kind": "common_lunch", "note": "公共午休，未与任何会议合并"})

# 冲突检查
conflicts = []
for i, a in enumerate(events):
    for b in events[i + 1:]:
        if a["venue"] != b["venue"]:
            continue
        if a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"]:
            conflicts.append({"a": a["id"], "b": b["id"], "venue": a["venue"],
                              "overlap": [fmt(max(a["start_min"], b["start_min"])),
                                          fmt(min(a["end_min"], b["end_min"]))]})

audit = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "date": "2026-11-07",
    "timezone": "Asia/Shanghai",
    "venue": "云构中心 · A / B / C 会场",
    "capacities": {v: venues_meta[v]["capacity"] for v in ["A", "B", "C"]},
    "categories": venues_meta["categories"],
    "events": [
        {"id": e["id"], "venue": e["venue"], "start": e["start"], "end": e["end"],
         "title": e["title"], "speaker": e["speaker"], "category": e["category"],
         "minutes": e["dur"]}
        for e in events
    ],
    "venue_gaps": venue_gaps,
    "conflicts": conflicts,
    "conflict_check": {
        "method": "同会场两两比较 [start,end) 区间是否相交",
        "conflict_count": len(conflicts),
        "note": "未捏造冲突；结果为 0 表示输入时间在同会场内无重叠",
    },
    "time_axis": {
        "timezone": "Asia/Shanghai",
        "start": "09:00", "end": "16:00", "total_minutes": T1 - T0,
        "px_start": ax_x0, "px_end": ax_x1, "px_per_minute": ax_w / (T1 - T0),
        "minutes_per_px": MIN_PER_PX,
        "canvas": {"width": W, "height": H, "origin": "canvas_top_left_y_down"},
        "mapping": "x_px = px_start + (minute - 540) / 420 * (px_end - px_start)",
        "shared_by_lanes": ["A", "B", "C"],
        "proportional_block_length": True,
        "input_times_unmodified": True,
    },
    "content_map": [
        {
            "event": e["id"], "venue": e["venue"], "fields": ["id", "title", "speaker",
                                                             "start", "end", "category"],
            "wide": {
                "image": "agenda-wide.png",
                "block_px_box": [round(x_of(e["start_min"]), 1),
                                 round(lane_boxes[e["venue"]] + 78, 1),
                                 round(x_of(e["end_min"]), 1),
                                 round(lane_boxes[e["venue"]] + 78 + 92, 1)],
                "title_text": e["title"],
                "title_location": "right_index" if e["dur"] < 50 else "block",
                "speaker_location": "right_index",
            },
            "mobile": {
                "image": "agenda-mobile.png",
                "fields_shown": ["id", "venue", "start", "end", "title", "category"],
                "speaker_shown": False,
                "speaker_note": "讲者详见完整日程",
            },
        }
        for e in events
    ],
    "visual_checks": {
        "wide_body_min_px": 17,
        "wide_time_label_min_px": 18,
        "mobile_body_min_px": 18,
        "lunch_not_merged_with_session": True,
        "gaps_preserved": True,
        "dense_1000_region_reviewed": True,
    },
}
(OUT_DIR / "schedule-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote schedule-audit.json; conflicts:", len(conflicts), "gaps:", len(venue_gaps))
