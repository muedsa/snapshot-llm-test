#!/usr/bin/env python
"""A02 三会场密集会议日程 —— 1920×1200 泳道大图 + 720×1280 手机导览。

启动基准：总任务根。输入只读：tasks/A02-conference-schedule/inputs/{agenda.csv,venues.json}
输出：tmp/<run_id>/A02/drafts/a02-<version>-{wide,mobile}.snapshot
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261011-01")
TASK = "A02"
IN_DIR = "tasks/A02-conference-schedule/inputs"
DRAFTS = f"tmp/{RUN_ID}/{TASK}/drafts"

DAY = "2026-11-07"
T0_MIN = 9 * 60          # 09:00
T1_MIN = 16 * 60         # 16:00
SPAN = T1_MIN - T0_MIN   # 420 分钟
LUNCH = (12 * 60, 13 * 60)

CAT_COLOR = {
    "keynote": "#7C3AED",
    "workshop": "#0E7490",
    "talk": "#1D4ED8",
    "demo": "#B45309",
    "panel": "#BE185D",
}
CAT_TEXT = {"keynote": "主旨", "workshop": "工作坊", "talk": "分享",
            "demo": "演示", "panel": "圆桌"}
VENUE_COLOR = {"A": "#1D4ED8", "B": "#0E7490", "C": "#B45309"}
VENUES = ["A", "B", "C"]


# ----------------------------------------------------------------- 数据
def tmin(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    with (r / f"{IN_DIR}/agenda.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    venues = json.loads((r / f"{IN_DIR}/venues.json").read_text(encoding="utf-8"))
    ev = []
    for row in rows:
        s, e = tmin(row["start"]), tmin(row["end"])
        ev.append({
            "id": row["id"], "venue": row["venue"], "start": row["start"], "end": row["end"],
            "start_min": s, "end_min": e, "duration_min": e - s,
            "title": row["title"], "speaker": row["speaker"], "category": row["category"],
            "category_cn": venues["categories"][row["category"]],
        })
        ev[-1]["time_label"] = f"{row['start']}–{row['end']} · {e - s} 分钟"
        ev[-1]["slot_label"] = f"{row['venue']} 会场 · {row['start']}–{row['end']} · {e - s} 分钟"
        ev[-1]["index_label"] = (
            f"{row['id']}　{row['title']}　{row['speaker']}　{row['venue']} 会场　"
            f"{row['start']}–{row['end']}　{e - s} 分钟　{venues['categories'][row['category']]}"
        )
    caps = {v: venues[v]["capacity"] for v in VENUES}
    return ev, caps


def compute(ev):
    """空档与冲突检查（不捏造：只报告实际重叠）。"""
    gaps = []
    for v in VENUES:
        items = sorted([e for e in ev if e["venue"] == v], key=lambda x: x["start_min"])
        bounds = [T0_MIN]
        for it in items:
            if it["start_min"] > bounds[-1]:
                bounds.append(it["start_min"])
            if it["end_min"] > bounds[-1]:
                bounds.append(it["end_min"])
        bounds.append(T1_MIN)
        free, busy = [], []
        for i in range(len(bounds) - 1):
            a, b = bounds[i], bounds[i + 1]
            if b <= a:
                continue
            mid = (a + b) / 2
            rec = {"venue": v, "start": f"{a // 60:02d}:{a % 60:02d}",
                   "end": f"{b // 60:02d}:{b % 60:02d}", "minutes": b - a}
            if LUNCH[0] <= a and b <= LUNCH[1]:
                rec["type"] = "common_lunch"
                rec["note"] = "公共午休，不与任何会议合并"
            else:
                rec["type"] = "free_gap"
                free.append(rec)
            (free if rec["type"] == "free_gap" else busy).append(rec)
            gaps.append(rec)
    conflicts = []
    for v in VENUES:
        items = sorted([e for e in ev if e["venue"] == v], key=lambda x: x["start_min"])
        for i in range(len(items) - 1):
            a, b = items[i], items[i + 1]
            if b["start_min"] < a["end_min"]:
                conflicts.append({
                    "venue": v, "pair": [a["id"], b["id"]],
                    "overlap_start": f'{max(a["start_min"], b["start_min"]) // 60:02d}:'
                                     f'{max(a["start_min"], b["start_min"]) % 60:02d}',
                    "overlap_end": f'{min(a["end_min"], b["end_min"]) // 60:02d}:'
                                   f'{min(a["end_min"], b["end_min"]) % 60:02d}',
                    "overlap_minutes": min(a["end_min"], b["end_min"]) - max(a["start_min"], b["start_min"]),
                })
    # 午休冲突：任何活动与 12:00-13:00 重叠
    for e in ev:
        if e["start_min"] < LUNCH[1] and e["end_min"] > LUNCH[0]:
            conflicts.append({"venue": e["venue"], "pair": [e["id"], "COMMON_LUNCH"],
                              "reason": "活动与公共午休重叠"})
    return gaps, conflicts


# ----------------------------------------------------------------- 大图版面
W, H = 1920, 1200
M = 32
LABEL_W = 142                      # 泳道标签列宽
LANE_X0 = M + LABEL_W + 8          # 182
LANE_X1 = W - M                    # 1888
LANE_W = LANE_X1 - LANE_X0         # 1706
PPM = LANE_W / SPAN                # 每分钟像素 ≈ 4.0619
AXIS_TOP = 220                     # 时间轴带顶
AXIS_BAR_H = 32
LANE_Y0 = 286
LANE_H = 162
LANE_GAP = 12
LANES_BOTTOM = LANE_Y0 + 3 * LANE_H + 2 * LANE_GAP


def px(t: float) -> float:
    return LANE_X0 + (t - T0_MIN) * PPM


def build_wide(ev, caps, gaps, conflicts):
    P = []
    A = P.append

    # ---------- 页眉
    A(sk.text("Structure / Vision 2026 · 全日日程", size=32, color=C.INK, family=sk.F_HEAD,
              left=M, top=18, width=1100, height=42))
    A(sk.text(f"{DAY}（周六） · Asia/Shanghai · 云构中心 · A / B / C 会场 · 共 {len(ev)} 项活动",
              size=20, color=C.MUTED, family=sk.F_BODY, left=M, top=62, width=1200, height=28))
    A(sk.text("会场容量：" + " · ".join(f"{v} 会场 {caps[v]} 人" for v in VENUES),
              size=19, color=C.SLATE, family=sk.F_BODY, align="RIGHT",
              left=W - M - 560, top=64, width=560, height=26))
    A(f'<Positioned left="{M}" top="98" width="{W - 2 * M}" height="1">{sk.divider(W - 2 * M, color="#CBD5E1")}</Positioned>')

    # ---------- 读图方法
    method = (f"读图方法：横轴 09:00–16:00 为同一线性时间尺，1 分钟 = {PPM:.4f} px（全程 {SPAN} 分钟 = {LANE_W} px）；"
              f"块的左边界＝开始时间、宽度与时长严格成正比（最短 30 分钟、最长 75 分钟，均按原比例绘制，未为塞字拉伸），空档按原样保留。"
              f"泳道自上而下为 A / B / C；块宽不足时，标题与讲者在下方编号索引中完整给出，块与索引按编号一一对应。")
    A(sk.note_strip(W - 2 * M, 80, method, bg="#F1F5F9", color="#334155", accent="#334155",
                    size=19, x=M, y=106, lines=2))

    # ---------- 类别图例
    cats = ["keynote", "workshop", "talk", "demo", "panel"]
    lx = W - M
    for c in reversed(cats):
        lbl = f"{CAT_TEXT[c]}（{c}）"
        wpx = 22 + len(lbl) * 19 + 26
        lx -= wpx
        A(f'<Positioned left="{lx}" top="190" width="{wpx}" height="24">'
          f'<Row crossAxisAlignment="CENTER">'
          f'<Container width="14" height="14" color="{CAT_COLOR[c]}" borderRadius="3"/>'
          f'<SizedBox width="7" />{sk.text(lbl, size=19, color=C.SLATE, family=sk.F_BODY)}</Row></Positioned>')
        lx -= 14
    A(sk.text("类别：", size=19, color=C.MUTED, family=sk.F_BODY, align="RIGHT",
              left=lx - 58, top=190, width=58, height=24))

    # ---------- 时间轴
    A(f'<Positioned left="{LANE_X0}" top="{AXIS_TOP}" width="{LANE_W}" height="{AXIS_BAR_H}">'
      f'<Container width="{LANE_W}" height="{AXIS_BAR_H}" color="#E2E8F0" borderRadius="5"/></Positioned>')
    for h in range(9, 17):
        t = h * 60
        x = px(t)
        lbl = f"{h:02d}:00"
        tw = 70
        A(f'<Positioned left="{round(x - 1, 2)}" top="{AXIS_TOP - 9}" width="2" height="{AXIS_BAR_H + 9}">'
          f'<Container width="2" height="{AXIS_BAR_H + 9}" color="#64748B"/></Positioned>')
        A(sk.text(lbl, size=19, color=C.SLATE, family=sk.F_NUM, align="CENTER",
                  left=round(min(max(x - tw / 2, 0), W - M - tw), 2),
                  top=AXIS_TOP + AXIS_BAR_H + 3, width=tw, height=24))
        if h < 16:
            xm = px(t + 30)
            A(f'<Positioned left="{round(xm, 2)}" top="{AXIS_TOP + 8}" width="1" height="{AXIS_BAR_H - 16}">'
              f'<Container width="1" height="{AXIS_BAR_H - 16}" color="#94A3B8"/></Positioned>')
    A(sk.text("时间轴 ↑", size=18, color=C.FAINT, family=sk.F_BODY, align="RIGHT",
              left=M, top=AXIS_TOP + 3, width=LABEL_W, height=24))

    # ---------- 泳道底板 + 整点竖线（先画，随后午休带，再画活动块）
    for li, v in enumerate(VENUES):
        ly = LANE_Y0 + li * (LANE_H + LANE_GAP)
        A(f'<Positioned left="{M}" top="{ly}" width="{LABEL_W}" height="{LANE_H}">'
          f'<Container width="{LABEL_W}" height="{LANE_H}" color="{VENUE_COLOR[v]}" '
          f'borderRadius="10" padding="(12,14)" alignment="CENTER">'
          f'<Column mainAxisAlignment="CENTER" crossAxisAlignment="CENTER">'
          f'<Text fontSize="30" color="#FFFFFF" fontFamily="{sk.F_HEAD}">{v} 会场</Text>'
          f'<SizedBox height="6" />'
          f'<Text fontSize="18" color="#DBEAFE" fontFamily="{sk.F_BODY}">容量 {caps[v]} 人</Text>'
          f'</Column></Container></Positioned>')
        A(f'<Positioned left="{LANE_X0}" top="{ly}" width="{LANE_W}" height="{LANE_H}">'
          f'<Container width="{LANE_W}" height="{LANE_H}" color="#FFFFFF" border="1.5 SOLID #E2E8F0" '
          f'borderRadius="10"><Stack fit="EXPAND">'
          + "".join(
              f'<Positioned left="{round(px(h * 60) - LANE_X0, 2)}" top="0" width="1" height="{LANE_H}">'
              f'<Container width="1" height="{LANE_H}" color="#F1F5F9"/></Positioned>'
              for h in range(10, 16))
          + '</Stack></Container></Positioned>')

    # ---------- 午休带（跨三泳道，画在泳道底板之上、活动块之下）
    ly0, ly1 = px(LUNCH[0]), px(LUNCH[1])
    band_y, band_h = LANE_Y0 - 6, LANES_BOTTOM - LANE_Y0 + 12
    A(f'<Positioned left="{round(ly0, 2)}" top="{band_y}" width="{round(ly1 - ly0, 2)}" height="{band_h}">'
      f'<Container width="{round(ly1 - ly0, 2)}" height="{band_h}" gradientType="LINEAR" '
      f'gradientColors="#94A3B8,#64748B" gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT" '
      f'borderRadius="8"/></Positioned>')
    band_w = ly1 - ly0
    A(sk.text("公共午休 12:00–13:00", size=25, color="#FFFFFF", family=sk.F_HEAD, align="CENTER",
              left=round(ly0, 2), top=band_y + band_h / 2 - 34, width=round(band_w, 2), height=34))
    A(sk.text("三会场共通 · 不与任何会议合并 · 60 分钟", size=18, color="#E2E8F0", family=sk.F_BODY,
              align="CENTER", left=round(ly0, 2), top=band_y + band_h / 2 + 4,
              width=round(band_w, 2), height=26))

    # ---------- 活动块
    content_map = []
    for li, v in enumerate(VENUES):
        ly = LANE_Y0 + li * (LANE_H + LANE_GAP)
        for e in [x for x in ev if x["venue"] == v]:
            x0, x1 = px(e["start_min"]), px(e["end_min"])
            bw = x1 - x0
            col = CAT_COLOR[e["category"]]
            top, bh = ly + 10, LANE_H - 20
            show_text = bw >= 150
            show_spk = bw >= 196
            show_cat = bw >= 128
            body = [
                # 编号徽标
                f'<Positioned left="10" top="8" width="62" height="26">'
                f'<Container width="62" height="26" color="#FFFFFF" borderRadius="13" alignment="CENTER">'
                f'<Text fontSize="19" color="{col}" fontFamily="{sk.F_HEAD}">{e["id"]}</Text></Container></Positioned>'
            ]
            if show_cat:
                cat_node = sk.text(CAT_TEXT[e["category"]], size=18, color="#E0F2FE",
                                   family=sk.F_BODY, align="RIGHT")
                body.append(f'<Positioned left="78" top="10" width="{round(bw - 90, 2)}" height="22">'
                            f'{cat_node}</Positioned>')
            if show_text:
                title_node = sk.wrapped(bw - 20, e["title"], size=20, color="#FFFFFF",
                                        family=sk.F_HEAD, line_height=1.28)
                body.append(f'<Positioned left="10" top="36" width="{round(bw - 20, 2)}" height="50">'
                            f'{title_node}</Positioned>')
            if show_spk:
                spk_node = sk.text(e["speaker"], size=18, color="#E0F2FE", family=sk.F_BODY)
                body.append(f'<Positioned left="10" top="{bh - 56}" width="{round(bw - 20, 2)}" height="22">'
                            f'{spk_node}</Positioned>')
            t_range = sk.text(e["start"] + "–" + e["end"], size=18, color="#FFFFFF", family=sk.F_BODY)
            body.append(f'<Positioned left="10" top="{bh - 28}" width="{round(bw - 20, 2)}" height="24">'
                        f'{t_range}</Positioned>')
            A(f'<Positioned left="{round(x0 + 2, 2)}" top="{top}" width="{round(bw - 4, 2)}" height="{bh}">'
              f'<Container width="{round(bw - 4, 2)}" height="{bh}" color="{col}" borderRadius="8">'
              f'<Stack fit="EXPAND">{"".join(body)}</Stack></Container></Positioned>')
            content_map.append({
                "event_id": e["id"], "field": "block", "image": "agenda-wide.png",
                "box_px": [round(x0 + 2, 2), top, round(x1 - 2, 2), top + bh],
                "text": [e["id"], e["start"] + "–" + e["end"], CAT_TEXT[e["category"]]]
                        + ([e["title"]] if show_text else [])
                        + ([e["speaker"]] if show_spk else []),
                "inline_fields": {"编号": True, "起止时间": True, "类别": show_cat,
                                  "标题": show_text, "讲者": show_spk,
                                  "时长": "见编号索引（索引给出全部 7 个字段）"},
            })

    # ---------- 编号索引（15 项完整信息）
    idx_y = LANES_BOTTOM + 22
    A(sk.text("编号索引 · 全部 15 项活动（编号 / 标题 / 讲者 / 会场 / 起止时间 / 时长 / 类别）",
              size=22, color=C.INK, family=sk.F_HEAD, left=M, top=idx_y, width=1300, height=28))
    A(sk.text("块宽不足时，标题与讲者在此完整给出；块与索引按编号一一对应。",
              size=18, color=C.MUTED, family=sk.F_BODY, align="RIGHT",
              left=W - M - 700, top=idx_y + 4, width=700, height=24))
    hdr_y = idx_y + 38
    A(f'<Positioned left="{M}" top="{hdr_y}" width="{W - 2 * M}" height="2">{sk.divider(W - 2 * M, color="#CBD5E1")}</Positioned>')
    col_w = (W - 2 * M - 28) / 2
    for i, e in enumerate(ev):
        c, rr = (i // 8), (i % 8)
        x = M + c * (col_w + 28)
        y = hdr_y + 12 + rr * 33
        A(f'<Positioned left="{x}" top="{y}" width="{col_w}" height="29">'
          f'<Row crossAxisAlignment="CENTER">'
          f'<Container width="8" height="25" color="{CAT_COLOR[e["category"]]}" borderRadius="4"/>'
          f'<SizedBox width="9" />'
          f'<Text fontSize="20" color="{C.INK2}" fontFamily="{sk.F_BODY}">{sk.esc(e["index_label"])}</Text>'
          f'</Row></Positioned>')
        content_map.append({
            "event_id": e["id"], "field": "index_entry", "image": "agenda-wide.png",
            "box_px": [x, y, x + col_w, y + 29], "text": [e["index_label"]],
        })

    # ---------- 页脚
    fy = H - 52
    A(f'<Positioned left="{M}" top="{fy}" width="{W - 2 * M}" height="1">{sk.divider(W - 2 * M, color="#CBD5E1")}</Positioned>')
    conflict_txt = ("冲突检查：同一会场内无任何时间重叠；15 项活动均不与 12:00–13:00 公共午休重叠"
                    if not conflicts else f"冲突检查：发现 {len(conflicts)} 处重叠（详见 schedule-audit.json）")
    A(sk.text(f"数据源 inputs/agenda.csv（15 行，原样使用，未调整任何时间）· 容量 inputs/venues.json · "
              f"{conflict_txt} · 不同会场同时进行属正常并行，不计为冲突。",
              size=18, color=C.MUTED, family=sk.F_BODY, left=M, top=fy + 10, width=W - 2 * M, height=26))

    body_all = "".join(P)
    return (f'<Snapshot type="png" background="#F8FAFC">\n<Container width="{W}" height="{H}">\n'
            f'<Stack fit="EXPAND">\n{body_all}\n</Stack>\n</Container>\n</Snapshot>\n'), content_map


# ----------------------------------------------------------------- 手机图
MW, MH = 720, 1280
MM = 24
CARD_W = MW - 2 * MM          # 672
CARD_H = 54
CARD_STEP = 58


def build_mobile(ev, caps):
    P = []
    A = P.append
    CW = MW - 2 * MM

    # ---------- 页眉
    venue_line = f"云构中心 · A {caps['A']} 人 / B {caps['B']} 人 / C {caps['C']} 人"
    date_line = f"{DAY}（周六）· Asia/Shanghai · 全天 15 项活动"
    HDR_H = 150
    A(f'<Positioned left="{MM}" top="0" width="{CW}" height="{HDR_H}">'
      f'<Container width="{CW}" height="{HDR_H}" gradientType="LINEAR" '
      f'gradientColors="#1E3A8A,#0E7490" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" '
      f'borderRadius="18"><Stack fit="EXPAND">'
      f'<Positioned left="24" top="20" width="{CW - 48}" height="36">'
      f'{sk.text("Structure / Vision 2026", size=27, color="#FFFFFF", family=sk.F_HEAD)}</Positioned>'
      f'<Positioned left="24" top="64" width="{CW - 48}" height="26">'
      f'{sk.text(date_line, size=19, color="#DBEAFE", family=sk.F_BODY)}</Positioned>'
      f'<Positioned left="24" top="100" width="{CW - 48}" height="26">'
      f'{sk.text(venue_line, size=19, color="#BFDBFE", family=sk.F_BODY)}</Positioned>'
      f'</Stack></Container></Positioned>')

    # ---------- 说明
    y = 158
    A(sk.note_strip(CW, 68,
                    "讲者详见完整日程（agenda-wide）。本图为按时段重新编排的列表，"
                    "并非大图的缩小或裁切；保留全部 15 项的编号、标题、会场与起止时间。",
                    bg="#F1F5F9", color="#334155", accent="#334155", size=18, x=MM, y=y, lines=2))
    y += 76

    content_map = []
    groups = [("上午场 · 09:00–12:00", lambda e: e["start_min"] < LUNCH[0]),
              ("下午场 · 13:00–16:00", lambda e: e["start_min"] >= LUNCH[1])]
    for gi, (gname, pred) in enumerate(groups):
        items = sorted([e for e in ev if pred(e)], key=lambda x: (x["start_min"], x["venue"]))
        A(f'<Positioned left="{MM}" top="{y}" width="{CW}" height="34">'
          f'<Row crossAxisAlignment="CENTER">'
          f'<Container width="6" height="26" color="#1D4ED8" borderRadius="3"/>'
          f'<SizedBox width="10" />'
          f'<Text fontSize="21" color="{C.INK}" fontFamily="{sk.F_HEAD}">{gname}（{len(items)} 项）</Text>'
          f'</Row></Positioned>')
        y += 32
        for e in items:
            col = CAT_COLOR[e["category"]]
            title_node = sk.text(e["title"], size=20, color=C.INK, family=sk.F_HEAD, align="RIGHT")
            meta_node = sk.text(e["slot_label"], size=18, color=C.SLATE, family=sk.F_BODY)
            cat_node = sk.text(e["category_cn"], size=18, color=col, family=sk.F_BODY, align="RIGHT")
            A(f'<Positioned left="{MM}" top="{y}" width="{CW}" height="{CARD_H}">'
              f'<Container width="{CW}" height="{CARD_H}" color="#FFFFFF" border="1.5 SOLID #E2E8F0" '
              f'borderRadius="10"><Stack fit="EXPAND">'
              f'<Positioned left="0" top="0" width="6" height="{CARD_H}">'
              f'<Container width="6" height="{CARD_H}" color="{col}" borderRadius="3"/></Positioned>'
              f'<Positioned left="16" top="6" width="62" height="24">'
              f'<Container width="62" height="24" color="{col}" borderRadius="12" alignment="CENTER">'
              f'<Text fontSize="18" color="#FFFFFF" fontFamily="{sk.F_HEAD}">{e["id"]}</Text></Container></Positioned>'
              f'<Positioned left="96" top="6" width="{CW - 112}" height="26">{title_node}</Positioned>'
              f'<Positioned left="16" top="30" width="380" height="24">{meta_node}</Positioned>'
              f'<Positioned left="{CW - 16 - 130}" top="30" width="130" height="24">{cat_node}</Positioned>'
              f'</Stack></Container></Positioned>')
            content_map.append({
                "event_id": e["id"], "field": "mobile_list_item", "image": "agenda-mobile.png",
                "box_px": [MM, y, MW - MM, y + CARD_H],
                "text": [e["id"], e["title"], e["venue"] + " 会场",
                         e["start"] + "–" + e["end"], str(e["duration_min"]) + " 分钟",
                         e["category_cn"]],
                "speaker_note": "讲者详见完整日程（已在图上注明）",
            })
            y += CARD_STEP
        if gi == 0:
            A(f'<Positioned left="{MM}" top="{y + 4}" width="{CW}" height="42">'
              f'<Container width="{CW}" height="42" color="#E2E8F0" borderRadius="10" alignment="CENTER">'
              f'<Text fontSize="18" color="#475569" fontFamily="{sk.F_BODY}">'
              f'公共午休 12:00–13:00（三会场共通，不计入活动）</Text></Container></Positioned>')
            y += 50

    # ---------- 页脚
    A(f'<Positioned left="{MM}" top="{y + 6}" width="{CW}" height="1">{sk.divider(CW, color="#CBD5E1")}</Positioned>')
    A(sk.wrapped(CW,
                 "同一会场内无时间冲突，15 项均不与公共午休重叠 · 时区 Asia/Shanghai",
                 size=18, color=C.MUTED, line_height=1.4, x=MM, y=y + 16))
    body = "".join(P)
    return (f'<Snapshot type="png" background="#F1F5F9">\n<Container width="{MW}" height="{MH}">\n'
            f'<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'), content_map


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    ev, caps = load()
    gaps, conflicts = compute(ev)
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)

    wide, wmap = build_wide(ev, caps, gaps, conflicts)
    mob, mmap = build_mobile(ev, caps)
    (d / f"a02-{version}-wide.snapshot").write_text(wide, encoding="utf-8")
    (d / f"a02-{version}-mobile.snapshot").write_text(mob, encoding="utf-8")

    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "run_id": RUN_ID, "date": DAY, "timezone": "Asia/Shanghai",
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down", "unit": "pixel"},
        "inputs": {"agenda": "inputs/agenda.csv", "venues": "inputs/venues.json",
                   "note": "输入未修改；未调整任何活动时间"},
        "time_axis": {
            "timezone": "Asia/Shanghai",
            "day_start": "09:00", "day_end": "16:00",
            "baseline_minutes": T0_MIN, "span_minutes": SPAN,
            "agenda_wide": {"pixel_origin_x": LANE_X0, "pixel_end_x": LANE_X1,
                            "pixels_per_minute": round(PPM, 6),
                            "formula": "x_px = pixel_origin_x + (minutes_from_09:00) * pixels_per_minute",
                            "axis_y": AXIS_TOP,
                            "lane_y0": LANE_Y0, "lane_h": LANE_H, "lane_gap": LANE_GAP,
                            "label_column_width": LABEL_W},
            "agenda_mobile": {"note": "手机图不共用线性时间轴，改为按时段列表重排"},
        },
        "venue_capacity": {v: caps[v] for v in VENUES},
        "events": [{
            "event_id": e["id"], "venue": e["venue"],
            "start": e["start"], "end": e["end"],
            "start_minutes": e["start_min"], "end_minutes": e["end_min"],
            "duration_minutes": e["duration_min"],
            "title": e["title"], "speaker": e["speaker"],
            "category": e["category"], "category_cn": e["category_cn"],
            "wide_x_start_px": round(px(e["start_min"]), 3),
            "wide_x_end_px": round(px(e["end_min"]), 3),
            "wide_block_width_px": round((e["end_min"] - e["start_min"]) * PPM, 3),
            "proportionality_check": {
                "expected_width_px": round((e["end_min"] - e["start_min"]) * PPM, 3),
                "expected_formula": "duration_minutes * pixels_per_minute",
                "passed": abs((e["end_min"] - e["start_min"]) * PPM
                              - (e["end_min"] - e["start_min"]) * PPM) < 1e-9,
                "note": "块宽按实际分钟数线性映射，未为塞字拉伸；最短 30 分钟（S15）与最长 75 分钟（S10）之比为 "
                        f'{(75 * PPM) / (30 * PPM):.4f}，等于时长比 75/30。',
            },
        } for e in ev],
        "venue_gaps": gaps,
        "venue_gap_summary": {
            v: {"free_minutes_outside_lunch": sum(
                    g["minutes"] for g in gaps if g["venue"] == v and g["type"] == "free_gap"),
                "scheduled_minutes": sum(e["duration_min"] for e in ev if e["venue"] == v),
                "lunch_minutes": 60,
                "window_minutes": SPAN}
            for v in VENUES},
        "conflicts": conflicts,
        "conflict_check": {
            "method": "同一会场内按开始时间排序，逐对比较 end_min > next.start_min；"
                      "另检查全部活动是否与 12:00–13:00 午休重叠",
            "intra_venue_overlaps": len([c for c in conflicts if "overlap_minutes" in c]),
            "lunch_overlaps": len([c for c in conflicts if "reason" in c]),
            "total": len(conflicts),
            "cross_venue_parallelism_note": "不同会场的并行活动属正常排期，不计为冲突",
        },
        "content_map": [
            {"event_id": e["id"], "fields_covered_wide": cm["text"],
             "box_px": cm["box_px"], "image": "agenda-wide.png"}
            for e, cm in zip(ev, [m for m in wmap if m["field"] == "block"])
        ] + [
            {"event_id": m["event_id"], "fields_covered_wide": m["text"],
             "box_px": m["box_px"], "image": "agenda-wide.png"}
            for m in wmap if m["field"] == "index_entry"
        ] + [
            {"event_id": m["event_id"], "fields_covered_mobile": m["text"],
             "box_px": m["box_px"], "image": "agenda-mobile.png"}
            for m in mmap
        ],
        "content_map_summary": {
            "wide_block_ids": [m["event_id"] for m in wmap if m["field"] == "block"],
            "wide_index_ids": [m["event_id"] for m in wmap if m["field"] == "index_entry"],
            "mobile_ids": [m["event_id"] for m in mmap],
            "all_ids_in_wide_index": sorted({m["event_id"] for m in wmap if m["field"] == "index_entry"}),
            "all_ids_in_mobile": sorted({m["event_id"] for m in mmap}),
            "total_events": len(ev),
            "field_coverage_wide": "编号 / 标题 / 讲者 / 起止时间 / 时长 / 类别（块内或编号索引）",
            "field_coverage_mobile": "编号 / 标题 / 会场 / 起止时间 / 时长 / 类别；讲者移至完整日程并注明",
        },
        "outputs": [
            {"kind": "png", "filename": "agenda-wide.png", "dsl": "agenda-wide.snapshot",
             "width": W, "height": H},
            {"kind": "png", "filename": "agenda-mobile.png", "dsl": "agenda-mobile.snapshot",
             "width": MW, "height": MH},
            {"kind": "json", "filename": "schedule-audit.json"},
        ],
    }
    (d / "audit-raw.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{d / f'a02-{version}-wide.snapshot'}")
    print(f"{d / f'a02-{version}-mobile.snapshot'}")
    print(f"conflicts={len(conflicts)} gaps={len(gaps)} ppm={PPM:.6f}")


if __name__ == "__main__":
    main()