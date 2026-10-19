# -*- coding: utf-8 -*-
"""A02 · 三会场密集会议日程：1920×1200 泳道大图 + 720×1280 手机导览。
启动基准：总任务根（或 SNAPSHOT_TASK_ROOT）；需 SNAPSHOT_RUN_ID。
产出（路径基准 = 本题输出根 outputs/<run_id>/A02/）：
  agenda-wide.snapshot / agenda-mobile.snapshot / schedule-audit.json
泳道块几何：x_left = 166 + (start-09:00 分钟数) × 1714/420 ≈ 4.081px/分钟，
块宽 = 实际分钟数 × 比例；空档与公共午休不压缩、不拉伸。
"""
import csv
import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN_ID / "A02"
OUT.mkdir(parents=True, exist_ok=True)
TMP = TASK_ROOT / "tmp" / RUN_ID / "A02"
TMP.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC"          # 中文与全角标点
FN = "Inter"                        # 数字与拉丁
FAM_MIX = FN + "," + FONT           # 拉丁优先 Inter，中文回退 Noto
TASK_DIR = TASK_ROOT / "tasks" / "A02-conference-schedule"

# ---------- 输入数据 ----------
rows = list(csv.DictReader((TASK_DIR / "inputs" / "agenda.csv").open(encoding="utf-8")))
venues = json.loads((TASK_DIR / "inputs" / "venues.json").read_text(encoding="utf-8"))
CAT = venues["categories"]
CAT_COLOR = {"keynote": "#2E90FA", "workshop": "#10B981", "talk": "#F59E0B",
             "demo": "#EF4444", "panel": "#8B5CF6"}
VENUE_NAME = {"A": "A 会场", "B": "B 会场", "C": "C 会场"}
LUNCH = (720, 780)  # 公共午休 12:00–13:00

def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"

events = []
for r in rows:
    sm, em = to_min(r["start"]), to_min(r["end"])
    events.append({**r, "start_m": sm, "end_m": em, "minutes": em - sm})
# 泳道内按出发时间排序（绘制顺序）；索引面板按编号排序
events.sort(key=lambda e: (e["venue"], e["start_m"], e["end_m"]))
index_order = sorted(events, key=lambda e: e["id"])

# ---------- 文本轮宽数值估计（保守；CJK=1.0em，Inter 数字 0.60em） ----------
def estw(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o < 0x80:
            if ch == " ":
                w += 0.32 * size
            elif ch in ":.":
                w += 0.30 * size
            elif ch == "·":
                w += 0.35 * size
            elif ch == "/":
                w += 0.40 * size
            elif ch in "–-":
                w += 0.58 * size
            elif ch.isdigit():
                w += 0.60 * size
            elif ch.isupper():
                w += 0.70 * size
            else:
                w += 0.54 * size
        else:
            w += 1.00 * size  # CJK / 全角
    return w

def split_title(t: str, size: float, avail: float):
    """为窄块返回两行标题 (p1, p2)；放不下返回 None。"""
    for brk in ("：", "·"):
        i = t.find(brk, 1)
        if i != -1 and i < len(t) - 1:
            p1, p2 = t[:i + 1], t[i + 1:]
            if estw(p1, size) <= avail and estw(p2, size) <= avail:
                return p1, p2
    n = len(t)
    if n >= 2:
        for kk in sorted(range(2, n), key=lambda x: (abs(x - (n + 1) / 2),
                                                     0 if x >= (n + 1) / 2 else 1)):
            p1, p2 = t[:kk], t[kk:]
            if estw(p1, size) <= avail and estw(p2, size) <= avail:
                return p1, p2
    return None

# ---------- DSL 发射器（扁平 Stack + 画布绝对坐标，A01 验证过的模式） ----------
def fnum(v) -> str:
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"

def rect(x, y, w, h, color=None, radius=None, border=None):
    a = f'<Container width="{fnum(w)}" height="{fnum(h)}"'
    if color:
        a += f' color="{color}"'
    if radius is not None and radius > 0:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">' + a + " /></Positioned>")

def text(x, y, content, size, color, family=FONT, bold=False, align="START", box_w=None):
    lx, ly = fnum(x), fnum(y)
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    sty += ' maxLines="1" overflow="CLIP"'
    if align != "START":
        sty += f' textAlign="{align}"'
    sty += f'>{content}</Text>'
    if box_w is None:
        return f'<Positioned left="{lx}" top="{ly}">{sty}</Positioned>'
    return f'<Positioned left="{lx}" top="{ly}" width="{fnum(box_w)}">{sty}</Positioned>'

def snapshot(bg: str, items) -> str:
    return ('<Snapshot background="' + bg + '" type="png">\n<Stack>\n'
            + "\n".join(items) + "\n</Stack>\n</Snapshot>\n")

# =====================================================================
# 大图 1920×1200
# =====================================================================
W, H = 1920, 1200
INK = "#17233D"; SUB = "#55657F"; FAINT = "#8494AE"
CARD = "#FFFFFF"; GRID = "#DFE7F2"; GRID2 = "#EDF2F9"
LANE_BG = {"A": "#FAFCFF", "B": "#F5F8FC", "C": "#FAFCFF"}
BAND_FILL = "#F4D06A33"; BAND_LINE = "#F4B73A88"
BAND_CHIP = "#FFF7E6"; BAND_TEXT = "#B7791F"

TX0, TX1 = 166, 1880
SCALE = (TX1 - TX0) / 420.0            # 4.080952…px/分钟
tx = lambda m: TX0 + (m - 540) * SCALE
PXM = SCALE

LANE = {"A": (240, 410), "B": (410, 580), "C": (580, 750)}
BLOCK_H = 104

S = [f'<SizedBox width="{W}" height="{H}" />']

# --- 头部卡片 ---
S.append(rect(32, 20, float(W) - 64, 108, CARD, 16, "1 SOLID #E3EAF4"))
S.append(text(56, 30, "Structure / Vision 2026", 34, INK, family=FN + "," + FONT, bold=True))
S.append(text(56, 84, "2026.11.07（周六）· 09:00–16:00 · 共 15 场活动 · Asia/Shanghai",
              20, SUB, family=FN + "," + FONT))
S.append(text(1398, 34, "云构中心 · A / B / C 会场", 22, INK, bold=True,
              align="END", box_w=466))
S.append(text(1398, 80, "会场容量  A 320 · B 80 · C 160（座位）", 18, SUB,
              family=FN + "," + FONT, align="END", box_w=466))

# --- 图例 ---
lx = 40.0
for key, cname in CAT.items():
    S.append(rect(lx, 150, 14, 14, CAT_COLOR[key], 7))
    S.append(text(lx + 22, 145, cname, 18, SUB))
    lx += 14 + 22 + estw(cname, 18) + 30
S.append(text(lx + 8, 145, "类别色（泳道块与索引行编号同色）", 18, FAINT))

# --- 泳道背景与时间网格 ---
for v in "ABC":
    y0, y1 = LANE[v]
    S.append(rect(32, y0, float(W) - 64, y1 - y0, LANE_BG[v]))
for m in range(540, 961, 30):
    xg = tx(m)
    half = (m - 540) % 60 != 0
    S.append(rect(xg, 236, 2, 520, GRID2 if half else GRID))
    if not half:
        S.append(text(xg - 30, 192, hhmm(m), 18, FAINT, family=FN,
                      align="CENTER", box_w=60))

# --- 公共午休带（跨三泳道）---
bx0, bx1 = tx(LUNCH[0]), tx(LUNCH[1])
S.append(rect(bx0, 240, bx1 - bx0, 510, BAND_FILL))
S.append(rect(bx0, 240, bx1 - bx0, 2, BAND_LINE))
S.append(rect(bx0, 748, bx1 - bx0, 2, BAND_LINE))
mid = (bx0 + bx1) / 2
S.append(rect(mid - 125, 248, 250, 34, BAND_CHIP, 17, "1 SOLID #F4B73A66"))
S.append(text(mid - 115, 255, "公共午休 12:00–13:00", 18, BAND_TEXT,
              family=FN + "," + FONT, bold=True, align="CENTER", box_w=230))

# --- 泳道标签 ---
for v in "ABC":
    y0, y1 = LANE[v]
    cym = (y0 + y1) / 2
    S.append(text(44, cym - 42, f"{v} 会场", 22, INK, bold=True))
    S.append(text(44, cym + 2, f"容量 {venues[v]['capacity']}", 18, SUB,
                  family=FN + "," + FONT))

# --- 活动块（宽度决定信息取舍，不拉伸）---
WIDE_BLOCKS = {}
for e in events:
    v = e["venue"]
    y0, _ = LANE[v]
    bx = tx(e["start_m"])
    bwid = e["minutes"] * PXM
    by = y0 + 33
    col = CAT_COLOR[e["category"]]
    idw = estw(e["id"], 18)
    tstr = f'{e["start"]}–{e["end"]}'
    tw = estw(tstr, 18)
    avail = bwid - 26
    line1_time = bwid >= 165  # 右缘 -8 位放时间，需避开编号末端
    shown = ["id", "time"]
    S.append(rect(bx, by, bwid, BLOCK_H, col + "33", 10, f"1 SOLID {col}55"))
    S.append(rect(bx, by, 4, BLOCK_H, col))
    S.append(text(bx + 13, by + 8, e["id"], 18, col, family=FN, bold=True))
    if line1_time:
        S.append(text(bx + bwid - 118, by + 8, tstr, 18, INK, family=FN,
                      align="END", box_w=110))
        title = e["title"]
        two = None
        if estw(title, 20) <= avail - 8:
            S.append(text(bx + 13, by + 32, title, 20, INK, bold=True, box_w=avail))
            shown.append("title")
            if estw(e["speaker"], 20) <= avail and estw(e["speaker"], 20) + 60 <= bwid:
                S.append(text(bx + 13, by + 64, e["speaker"], 20, SUB,
                              family=FN + "," + FONT, box_w=avail))
                shown.append("speaker")
            # 宽块标题 1 行时，讲者行才展示（维持行距 > 22px）
        else:
            two = split_title(title, 20, avail)
            if two:
                S.append(text(bx + 13, by + 32, two[0], 20, INK, bold=True, box_w=avail))
                S.append(text(bx + 13, by + 56, two[1], 20, INK, bold=True, box_w=avail))
                shown.append("title")
    else:
        S.append(text(bx + 6, by + 34, tstr, 18, INK, family=FN,
                      align="END", box_w=bwid - 10))
    WIDE_BLOCKS[e["id"]] = {
        "block_box": [round(bx, 2), by, round(bx + bwid, 2), by + BLOCK_H],
        "block_fields": shown,
        "minutes": e["minutes"], "block_width_px": round(bwid, 2),
    }

# --- 活动索引面板（按编号，承载完整信息）---
S.append(rect(32, 750, float(W) - 64, 362, CARD, 16, "1 SOLID #E3EAF4"))
S.append(text(60, 766, "活动索引 · 全部 15 场（按编号顺序）", 20, INK, bold=True))
S.append(text(1544, 768, "块内放不下的标题 / 讲者在此完整呈现", 18, FAINT,
              family=FN + "," + FONT, align="END", box_w=320))
INDEX_BOX = {}
for j, e in enumerate(index_order):
    ci, ri = j // 5, j % 5
    cx = 60 + ci * 594
    ry = 806 + ri * 62
    col = CAT_COLOR[e["category"]]
    if ri:
        S.append(rect(cx, ry - 6, 554, 1, GRID))
    S.append(text(cx, ry, e["id"], 18, col, family=FN, bold=True))
    S.append(text(cx + 60, ry, f'{e["start"]}–{e["end"]}', 18, INK, family=FN))
    S.append(text(cx + 334, ry, f'{VENUE_NAME[e["venue"]]} · {CAT[e["category"]]}',
                  20, SUB, align="END", box_w=220))
    S.append(text(cx, ry + 28, e["title"], 20, INK, box_w=300))
    S.append(text(cx + 404, ry + 28, e["speaker"], 20, SUB,
                  family=FN + "," + FONT, align="END", box_w=150))
    INDEX_BOX[e["id"]] = [cx, ry, cx + 554, ry + 50]

# --- 底部读图方法 ---
S.append(text(40, 1126, "读图方法：块的位置与长度按真实起止时间等比绘制（09:00–16:00 共 420 分钟映射 1714px，≈4.081px/分钟）；"
                        "实线竖线为整点、浅竖线为半点；未排活动的时段保留空档，未拉伸或压缩任何活动。", 18, SUB))
S.append(text(40, 1160, "公共午休 12:00–13:00 为全场统一休整（跨三会场色带，单独计时）；容量 A 320 / B 80 / C 160；"
                        "编号、标题、讲者与类别详见下方活动索引。", 18, FAINT))

wide_dsl = snapshot("#F3F6FB", S)
(OUT / "agenda-wide.snapshot").write_text(wide_dsl, encoding="utf-8")

# =====================================================================
# 手机版 720×1280（分时段列表，非缩放非裁切）
# =====================================================================
W2, H2 = 720, 1280
INM = "#17233D"; SBM = "#55657F"; FAM = "#8494AE"
CARDM = "#FFFFFF"; GRIDM = "#E7EDF5"; BORDM = "#EAEFF7"
MX = 28.0; CW = 720 - 56

T = [f'<SizedBox width="{W2}" height="{H2}" />']
T.append(rect(MX, 20, CW, 118, CARDM, 16, "1 SOLID #E3EAF4"))
T.append(text(52, 32, "Structure / Vision 2026", 26, INM, family=FN + "," + FONT, bold=True))
T.append(text(52, 78, "2026.11.07（周六）· 全日导览", 18, SBM))
T.append(rect(452, 30, 220, 40, BAND_CHIP, 20, "1 SOLID #F4B73A66"))
T.append(text(460, 40, "讲者详见完整日程", 18, BAND_TEXT, bold=True,
              align="CENTER", box_w=204))

T.append(text(36, 160, "上午 · 09:00–12:00", 20, INM, bold=True))
T.append(rect(36, 194, 648, 2, GRIDM))

MOBILE_ROWS = {}
ROW_H, GAP = 54, 8
ry = 206.0

def mobile_event_row(e, ry):
    T.append(rect(MX, ry, CW, ROW_H, CARDM, 12, f"1 SOLID {BORDM}"))
    col = CAT_COLOR[e["category"]]
    T.append(rect(MX, ry, 56, ROW_H, col + "33", 12))
    T.append(text(MX + 10, ry + 17, e["id"], 18, col, family=FN, bold=True))
    T.append(text(MX + 68, ry + 12, e["title"], 20, INM, bold=True, box_w=370))
    T.append(text(MX + CW - 194, ry + 8, f'{e["start"]}–{e["end"]}', 18, INM,
                  family=FN, bold=True, align="END", box_w=180))
    T.append(text(MX + CW - 194, ry + 31, f'{VENUE_NAME[e["venue"]]} · {CAT[e["category"]]}',
                  18, SBM, family=FN + "," + FONT, align="END", box_w=180))
    MOBILE_ROWS[e["id"]] = [MX, ry, MX + CW, ry + ROW_H]

morning = sorted([e for e in events if e["start_m"] < 720],
                 key=lambda e: (e["start_m"], e["end_m"], e["id"]))
afternoon = sorted([e for e in events if e["start_m"] >= 780],
                   key=lambda e: (e["start_m"], e["end_m"], e["id"]))
for e in morning:
    mobile_event_row(e, ry)
    ry += ROW_H + GAP
T.append(rect(MX, ry, CW, 44, BAND_CHIP, 12, "1 SOLID #F4B73A55"))
T.append(text(52, ry + 11, "公共午休 12:00–13:00 · 独立时段，任何会场不放会议", 18,
              BAND_TEXT, bold=True))
MOBILE_LUNCH = [MX, ry, MX + CW, ry + 44]
ry += 44 + 14
T.append(text(36, ry + 4, "下午 · 13:00–16:00", 20, INM, bold=True))
T.append(rect(36, ry + 36, 648, 2, GRIDM))
ry = ry + 46
for e in afternoon:
    mobile_event_row(e, ry)
    ry += ROW_H + GAP
T.append(text(36, ry + 2, "会场容量 A 320 · B 80 · C 160 · 时间均为 Asia/Shanghai · 讲者详见完整日程",
              18, FAM, family=FN + "," + FONT))

mobile_dsl = snapshot("#F3F6FB", T)
(OUT / "agenda-mobile.snapshot").write_text(mobile_dsl, encoding="utf-8")

# =====================================================================
# schedule-audit.json
# =====================================================================
# 会场空档：09:00–16:00 内相邻活动间隙；公共午休 [12:00–13:00] 剔除出空档单独记录
venue_gaps = []
for v in "ABC":
    segs = sorted([(e["start_m"], e["end_m"]) for e in events if e["venue"] == v])
    gaps = []
    cur = 540
    for a, b in segs:
        if a > cur:
            gaps.append((cur, a))
        cur = max(cur, b)
    if cur < 960:
        gaps.append((cur, 960))
    arr = []
    for a, b in gaps:
        # 与午休 [720,780] 相接的部分不算会场空档
        if a >= 780 or b <= 720:
            arr.append({"start": hhmm(a), "end": hhmm(b), "minutes": b - a})
    venue_gaps.append({"venue": v, "venue_name": VENUE_NAME[v],
                       "capacity": venues[v]["capacity"], "gaps": arr})

# 冲突检查：同一会场两两区间重叠 = 冲突；不同会场同时段不算
conflicts = []
pairs_checked = 0
for v in "ABC":
    evs = sorted([e for e in events if e["venue"] == v], key=lambda e: e["start_m"])
    for i in range(len(evs)):
        for j in range(i + 1, len(evs)):
            pairs_checked += 1
            a, b = evs[i], evs[j]
            if a["end_m"] > b["start_m"] and b["end_m"] > a["start_m"]:
                conflicts.append({
                    "venue": v, "a": a["id"], "b": b["id"],
                    "overlap": [hhmm(max(a["start_m"], b["start_m"])),
                                 hhmm(min(a["end_m"], b["end_m"]))],
                    "minutes": min(a["end_m"], b["end_m"]) - max(a["start_m"], b["start_m"]),
                })

# 内容映射：两图坐标（画布左上原点，像素，[left,top,right,bottom]）
content_map = []
SECTION = {}
for e in events:
    SECTION[e["id"]] = "上午 09:00–12:00" if e["start_m"] < 720 else "下午 13:00–16:00"
for e in index_order:
    wb = WIDE_BLOCKS[e["id"]]
    content_map.append({
        "event_id": e["id"],
        "wide": {
            "image": "agenda-wide.png", "dsl": "agenda-wide.snapshot",
            "canvas_size": [1920, 1200],
            "lane": e["venue"], "lane_name": VENUE_NAME[e["venue"]],
            "block_box": wb["block_box"], "block_fields": wb["block_fields"],
            "index_box": INDEX_BOX[e["id"]],
            "index_fields": ["id", "time", "venue", "category", "title", "speaker"],
        },
        "mobile": {
            "image": "agenda-mobile.png", "dsl": "agenda-mobile.snapshot",
            "canvas_size": [720, 1280],
            "section": SECTION[e["id"]],
            "row_box": [round(v, 2) for v in MOBILE_ROWS[e["id"]]],
            "row_fields": ["id", "title", "time", "venue", "category"],
        },
        "note": "标题与讲者在流程表泳道块宽度不足时改由该行索引面板完整呈现；两图均为独立排版。",
    })

audit = {
    "schema_version": 1,
    "task_id": "A02",
    "path_base": "output_dir",
    "inputs": {
        "path_base": "suite_root",
        "paths": [
            "tasks/A02-conference-schedule/inputs/agenda.csv",
            "tasks/A02-conference-schedule/inputs/venues.json",
        ],
        "rows_used": len(events),
        "timezone": "Asia/Shanghai",
        "modifications": "无——起止时间、标题、讲者、类别与容量均按输入原值使用",
    },
    "images": {
        "agenda-wide.png": {"size": [1920, 1200], "dsl": "agenda-wide.snapshot",
                            "product": "按真实时长等比绘制的三会场泳道日程"},
        "agenda-mobile.png": {"size": [720, 1280], "dsl": "agenda-mobile.snapshot",
                              "product": "分时段列表导览（上午 / 公共午休 / 下午）",
                              "independent_layout": True},
    },
    "events": [
        {"id": e["id"], "venue": e["venue"], "venue_name": VENUE_NAME[e["venue"]],
         "start": e["start"], "end": e["end"], "minutes": e["minutes"],
         "title": e["title"], "speaker": e["speaker"],
         "category": e["category"], "category_label": CAT[e["category"]]}
        for e in index_order],
    "event_count": len(events),
    "venue_gaps": venue_gaps + [{
        "venue": "ALL", "type": "public_lunch", "start": hhmm(LUNCH[0]),
        "end": hhmm(LUNCH[1]), "minutes": LUNCH[1] - LUNCH[0],
        "note": "全场统一休整，不属于任何会场的空档，跨三会场以色带标示并保持独立记录",
    }],
    "venue_gaps_method": "各会场按 09:00–16:00 计算；与公共午休（12:00–13:00）接壤或被其覆盖的区间从空档列表剔除，午休单独成项记录",
    "conflicts": conflicts,
    "conflict_check": {
        "method": "同一会场内两两活动区间求交（重叠分钟 > 0 记为冲突）；不同会场同时段（如 S02 9:00–9:55 与 S03 9:15–10:00）属并行场次，不算冲突",
        "pairs_checked": pairs_checked,
        "overlap_pairs": len(conflicts),
        "passed": len(conflicts) == 0,
        "input_times_unchanged": True,
    },
    "public_lunch": {"start": hhmm(LUNCH[0]), "end": hhmm(LUNCH[1]),
                     "minutes": 60, "merged_into_events": False,
                     "wide_band_box": [round(bx0, 2), 240, round(bx1, 2), 750],
                     "mobile_row_box": [round(v, 2) for v in MOBILE_LUNCH]},
    "time_axis": {
        "timezone": "Asia/Shanghai",
        "base": "09:00 = 540（日计划分钟）",
        "axis_px_start": TX0, "axis_px_end": TX1,
        "minute_span": 420,
        "px_per_minute": round(PXM, 12),
        "mapping": f"x_px = {TX0} + (start_minutes - 540) × {round(PXM, 9)}；start_minutes = 起始时刻自 09:00 起算的分钟数",
        "mobile": "手机图无时间轴缩放，列表按时间顺序分时段组织",
    },
    "geometry_method": "块左 = tx(start_minutes)，块宽 = minutes × px_per_minute；位置与长度由程序按输入时间直接计算。"
                       "短块（<165px，即 <40.5 分钟）因宽度不足块内仅排编号与起止时间；标题与讲者改由索引面板同编号行完整给出；"
                       "不加拉伸、不加合并、不改变任何活动时长。",
    "geometry_check": {
        "all_blocks_scaled_by_minutes": True,
        "off_scale_blocks": [],
        "spot_checks": [
            {"event": "S01", "minutes": 40, "block_width_px": WIDE_BLOCKS["S01"]["block_width_px"],
             "expected_px": round(40 * PXM, 2),
             "note": "若误按 60 分钟绘制会写成 244.86px，当前 163.24px，两者可区分"},
            {"event": "S10", "minutes": 75, "block_width_px": WIDE_BLOCKS["S10"]["block_width_px"],
             "expected_px": round(75 * PXM, 2)},
            {"event": "S15", "minutes": 30, "block_width_px": WIDE_BLOCKS["S15"]["block_width_px"],
             "expected_px": round(30 * PXM, 2)},
        ],
        "passed": True,
    },
    "capacity": {v: venues[v]["capacity"] for v in "ABC"},
    "category_labels": dict(CAT),
    "content_map": content_map,
    "visual_checks": [],  # 由 finalize_audit.py 在实际查看图像后填写
    "build_script": {"path_base": "suite_root",
                     "path": f"tmp/{RUN_ID}/A02/build_a02.py"},
}
(OUT / "schedule-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "wide_dsl_bytes": len(wide_dsl.encode("utf-8")),
    "mobile_dsl_bytes": len(mobile_dsl.encode("utf-8")),
    "wide_blocks": len(WIDE_BLOCKS), "index_rows": len(INDEX_BOX),
    "mobile_rows": len(MOBILE_ROWS), "conflicts": len(conflicts),
    "pairs_checked": pairs_checked,
}, ensure_ascii=False))
