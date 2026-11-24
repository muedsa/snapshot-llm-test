from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

RUN_ID = "20261124T113838+0800-aac601"
TASK = "A02"
CATEGORY_COLORS = {
    "keynote": ("#7C3AED", "#F1EBFF"),
    "workshop": ("#0369A1", "#E6F4FB"),
    "talk": ("#047857", "#E7F6EF"),
    "demo": ("#B45309", "#FFF3DE"),
    "panel": ("#BE185D", "#FCEAF3"),
}


def minute(value: str) -> int:
    h, m = map(int, value.split(":"))
    return h * 60 + m


def load_rows():
    task_dir = s.ROOT / "tasks" / "A02-conference-schedule"
    with (task_dir / "inputs" / "agenda.csv").open(encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    venues = json.loads((task_dir / "inputs" / "venues.json").read_text(encoding="utf-8"))
    rows = []
    for item in raw:
        row = dict(item)
        row["start_min"] = minute(item["start"])
        row["end_min"] = minute(item["end"])
        row["duration"] = row["end_min"] - row["start_min"]
        assert row["duration"] > 0
        rows.append(row)
    assert len(rows) == 15 and len({r["id"] for r in rows}) == 15
    return rows, venues


def build_wide(rows, venues):
    c = []
    # Header and category key.
    c.append(s.label("STRUCTURE / VISION 2026", 40, 28, 800, 28, 18, "#52627A", True))
    c.append(s.label("三会场 · 全日会议日程", 40, 62, 1100, 58, 46, "#13233A", True))
    c.append(s.label("2026.11.07  ·  云构中心 · A / B / C 会场  ·  Asia/Shanghai", 40, 128, 1180, 34, 23, "#52627A"))
    c.append(s.label("块宽严格按实际起止时间绘制；空白即无活动。短块信息在块内与底部编号索引双重可读。", 40, 176, 1480, 34, 21, "#52627A"))
    for i, key in enumerate(CATEGORY_COLORS):
        x = 1140 + (i % 3) * 242
        y = 30 + (i // 3) * 42
        dark, light = CATEGORY_COLORS[key]
        c.append(s.box(x, y + 5, 18, 18, dark, 4))
        c.append(s.label(venues["categories"][key], x + 28, y, 170, 30, 20, "#344257"))

    axis_x, axis_w = 220, 1655
    scale = axis_w / 420
    lane_y = {"A": 280, "B": 476, "C": 672}
    lane_h = 176
    # Axis and lane surfaces.
    c.append(s.line(axis_x, 255, axis_x + axis_w, 255, "#8FA0B5", 2))
    for t in range(0, 421, 30):
        x = axis_x + t * scale
        c.append(s.line(x, 250, x, 842, "#DCE4ED", 1))
        hh, mm = divmod(540 + t, 60)
        c.append(s.label(f"{hh:02d}:{mm:02d}", x - 40, 218, 80, 30, 18, "#52627A", t % 60 == 0, "CENTER"))
    for venue in "ABC":
        y = lane_y[venue]
        c.append(s.box(axis_x, y, axis_w, lane_h, "#F8FAFC", 10, "#DCE4ED"))
        c.append(s.box(40, y, 158, lane_h, "#132B3A", 10))
        c.append(s.label(f"{venue} 会场", 54, y + 28, 130, 36, 27, "#FFFFFF", True))
        c.append(s.label(f'{venues[venue]["capacity"]} 席', 54, y + 78, 130, 30, 21, "#A7E3D1", True))
        c.append(s.label("容量", 54, y + 116, 130, 26, 18, "#C5D5E1"))
    # Shared lunch overlays the otherwise empty 12:00–13:00 slice across all lanes.
    lunch_x = axis_x + 180 * scale
    lunch_w = 60 * scale
    c.append(s.box(lunch_x, lane_y["A"], lunch_w, 568, "#FFF0C9", 0))
    c.append(s.line(lunch_x, lane_y["A"], lunch_x, 840, "#D69A2D", 2))
    c.append(s.line(lunch_x + lunch_w, lane_y["A"], lunch_x + lunch_w, 840, "#D69A2D", 2))
    c.append(s.label("公共午休", lunch_x, 467, lunch_w, 32, 21, "#8A5410", True, "CENTER"))
    c.append(s.label("12:00–13:00", lunch_x, 509, lunch_w, 30, 18, "#8A5410", True, "CENTER"))
    c.append(s.label("三会场同步", lunch_x, 551, lunch_w, 28, 18, "#8A5410", False, "CENTER"))
    c.append(s.line(axis_x, lane_y["B"] - 22, axis_x + axis_w, lane_y["B"] - 22, "#FFFFFF", 12))
    c.append(s.line(axis_x, lane_y["C"] - 22, axis_x + axis_w, lane_y["C"] - 22, "#FFFFFF", 12))

    content_map = []
    for r in rows:
        x = axis_x + (r["start_min"] - 540) * scale
        w = r["duration"] * scale
        y = lane_y[r["venue"]] + 14
        h = 148
        dark, light = CATEGORY_COLORS[r["category"]]
        # Precise proportional blocks; text is deliberately repeated in the bottom index.
        c.append(s.box(x + 1.5, y, w - 3, h, light, 8, dark))
        c.append(s.box(x + 1.5, y, 5, h, dark, 2))
        ix, iw = x + 11, w - 18
        c.append(s.label(r["id"], ix, y + 4, iw, 24, 20, dark, True))
        c.append(s.label(f'{r["start"]}–{r["end"]}', ix, y + 28, iw, 24, 18, dark, True))
        c.append(s.label(r["title"], ix, y + 54, iw, 46, 20, "#172033", True))
        c.append(s.label(r["speaker"], ix, y + 102, iw, 24, 20, "#344257"))
        c.append(s.label(venues["categories"][r["category"]], ix, y + 128, iw, 20, 20, dark, True))
        content_map.append({
            "id": r["id"], "fields": {
                "number": {"image": "agenda-wide.png", "text": r["id"], "box": [x + 11, y + 4, x + w - 7, y + 28]},
                "time": {"image": "agenda-wide.png", "text": f'{r["start"]}–{r["end"]}', "box": [x + 11, y + 28, x + w - 7, y + 52]},
                "title": {"image": "agenda-wide.png", "text": r["title"], "box": [x + 11, y + 54, x + w - 7, y + 100]},
                "speaker": {"image": "agenda-wide.png", "text": r["speaker"], "box": [x + 11, y + 102, x + w - 7, y + 126]},
                "category": {"image": "agenda-wide.png", "text": venues["categories"][r["category"]], "box": [x + 11, y + 128, x + w - 7, y + 148]},
            },
            "event_box": [x + 1.5, y, x + w - 1.5, y + h],
            "mapping": f'x={axis_x}+({r["start_min"]}-540)*{scale}; width={r["duration"]}*{scale}',
        })

    # Numbered index provides a larger reading path for every event.
    c.append(s.box(40, 868, 1840, 270, "#FFFFFF", 14, "#DCE4ED"))
    c.append(s.label("编号索引  /  与上方时间块一一对应", 64, 884, 900, 32, 23, "#13233A", True))
    c.append(s.label("读图：先沿会场泳道定位时间，再按编号核对完整标题。", 1110, 887, 744, 28, 18, "#52627A", False, "RIGHT"))
    for i, r in enumerate(rows):
        col, row = divmod(i, 5)
        x = 64 + col * 600
        y = 928 + row * 39
        dark, _ = CATEGORY_COLORS[r["category"]]
        c.append(s.label(r["id"], x, y, 52, 28, 20, dark, True))
        c.append(s.label(r["title"], x + 56, y, 350, 28, 20, "#172033", True))
        c.append(s.label(f'{r["venue"]} · {r["start"]}–{r["end"]}', x + 410, y, 176, 28, 18, "#52627A", False, "RIGHT"))
        content_map[i]["index_box"] = [x, y, x + 586, y + 30]
    c.append(s.label("公共午休独立保留，不计入 15 项活动。时间轴 09:00–16:00，共 420 分钟；所有时间均为 Asia/Shanghai。", 40, 1160, 1840, 28, 18, "#52627A"))
    return s.snapshot(1920, 1200, c), content_map, {"origin": [axis_x, 255], "pixels_per_minute": scale, "start_minute": 540, "end_minute": 960}


def build_mobile(rows, venues):
    c = []
    c.append(s.box(0, 0, 720, 150, "#132B3A"))
    c.append(s.label("STRUCTURE / VISION 2026", 24, 18, 672, 26, 18, "#A7E3D1", True))
    c.append(s.label("全日会议导览", 24, 48, 672, 42, 34, "#FFFFFF", True))
    c.append(s.label("2026.11.07 · 云构中心 · Asia/Shanghai", 24, 100, 672, 28, 18, "#D4E2EB"))
    ordered = sorted(rows, key=lambda r: (r["start_min"], r["id"]))
    morning = [r for r in ordered if r["start_min"] < 720]
    afternoon = [r for r in ordered if r["start_min"] >= 720]
    assert len(morning) == 8 and len(afternoon) == 7
    c.append(s.label("上午  /  按开始时间排序", 24, 165, 672, 28, 20, "#52627A", True))
    content_map = []
    y = 201
    for idx, r in enumerate(ordered):
        if idx == 8:
            c.append(s.box(24, y, 672, 46, "#FFF0C9", 8, "#E8C577"))
            c.append(s.label("12:00–13:00  公共午休 · 三会场同步", 40, y + 9, 640, 28, 20, "#8A5410", True))
            y += 58
            c.append(s.label("下午  /  按开始时间排序", 24, y, 672, 28, 20, "#52627A", True))
            y += 36
        dark, light = CATEGORY_COLORS[r["category"]]
        c.append(s.box(24, y, 672, 58, "#FFFFFF", 8, "#DCE4ED"))
        c.append(s.box(24, y, 64, 58, dark, 8))
        c.append(s.label(r["id"], 24, y + 15, 64, 28, 20, "#FFFFFF", True, "CENTER"))
        c.append(s.label(r["title"], 102, y + 6, 420, 28, 20, "#172033", True))
        c.append(s.label(f'{r["venue"]} 会场  ·  {r["start"]}–{r["end"]}', 102, y + 33, 380, 24, 18, dark, True))
        c.append(s.label(venues["categories"][r["category"]], 510, y + 33, 170, 24, 18, "#52627A", False, "RIGHT"))
        content_map.append({
            "id": r["id"], "fields": {
                "number": {"image": "agenda-mobile.png", "text": r["id"], "box": [24, y + 15, 88, y + 43]},
                "title": {"image": "agenda-mobile.png", "text": r["title"], "box": [102, y + 6, 522, y + 34]},
                "venue_time": {"image": "agenda-mobile.png", "text": f'{r["venue"]} 会场  ·  {r["start"]}–{r["end"]}', "box": [102, y + 33, 482, y + 57]},
                "category": {"image": "agenda-mobile.png", "text": venues["categories"][r["category"]], "box": [510, y + 33, 680, y + 57]},
            },
            "event_box": [24, y, 696, y + 58],
        })
        y += 62
    assert y <= 1230, y
    c.append(s.label("讲者详见完整日程", 24, y + 4, 300, 28, 20, "#132B3A", True))
    c.append(s.label("A 320席 · B 80席 · C 160席", 326, y + 5, 370, 26, 18, "#52627A", False, "RIGHT"))
    return s.snapshot(720, 1280, c), content_map


def audit(rows, venues, wide_map, mobile_map, axis):
    events = [{"id": r["id"], "venue": r["venue"], "start": r["start"], "end": r["end"], "duration_minutes": r["duration"], "title": r["title"], "speaker": r["speaker"], "category": r["category"]} for r in rows]
    venue_gaps = []
    conflicts = []
    for venue in "ABC":
        vr = sorted([r for r in rows if r["venue"] == venue], key=lambda r: r["start_min"])
        cursor = 540
        for r in vr:
            assert r["start_min"] >= 720 or r["end_min"] <= 720, "Event crosses public lunch"
            if r["start_min"] > cursor:
                venue_gaps.append({"venue": venue, "start_minute": cursor, "end_minute": r["start_min"], "start": f"{cursor//60:02d}:{cursor%60:02d}", "end": f"{r['start_min']//60:02d}:{r['start_min']%60:02d}", "duration_minutes": r["start_min"] - cursor, "type": "free_gap"})
            if r["start_min"] < cursor:
                conflicts.append({"venue": venue, "first": cursor, "second": r["id"], "overlap": [r["start_min"], cursor]})
            cursor = max(cursor, r["end_min"])
        if cursor < 960:
            venue_gaps.append({"venue": venue, "start_minute": cursor, "end_minute": 960, "start": f"{cursor//60:02d}:{cursor%60:02d}", "end": "16:00", "duration_minutes": 960 - cursor, "type": "free_gap"})
        venue_gaps.append({"venue": venue, "start": "12:00", "end": "13:00", "start_minute": 720, "end_minute": 780, "duration_minutes": 60, "type": "public_lunch"})
    # Explicit pair check is independent of the sweep above.
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            if a["venue"] == b["venue"] and max(a["start_min"], b["start_min"]) < min(a["end_min"], b["end_min"]):
                conflicts.append({"venue": a["venue"], "events": [a["id"], b["id"]], "interval": [max(a["start_min"], b["start_min"]), min(a["end_min"], b["end_min"])]})
    assert conflicts == []
    result = s.audit_identity(TASK)
    result.update({
        "source_files": ["inputs/agenda.csv", "inputs/venues.json"],
        "event_count": 15,
        "public_lunch": {"start": "12:00", "end": "13:00", "duration_minutes": 60, "venues": ["A", "B", "C"], "counted_as_event": False},
        "events": events,
        "venue_gaps": venue_gaps,
        "conflicts": conflicts,
        "conflict_check": {"method": "同会场区间两两比较 max(start)<min(end)，并独立扫描排序区间", "passed": True, "input_times_modified": False},
        "content_map": wide_map + mobile_map,
        "time_axis": {"timezone": "Asia/Shanghai", "date": "2026-11-07", "start": "09:00", "end": "16:00", "start_minute": 540, "end_minute": 960, "duration_minutes": 420, "image": "agenda-wide.png", "pixel_origin": axis["origin"], "pixels_per_minute": axis["pixels_per_minute"], "coordinate_system": "canvas top-left origin; x right, y down; pixels", "mapping": "x=220+(minute-540)*1655/420; width=(end-start)*1655/420"},
        "venue_capacity": {v: venues[v]["capacity"] for v in "ABC"},
        "visual_evidence": {"requests_log": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/{TASK}/requests.jsonl"}, "iterations_log": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/{TASK}/iterations.jsonl"}},
    })
    return result


def main():
    s.begin_task(RUN_ID, TASK)
    rows, venues = load_rows()
    wide, wide_map, axis = build_wide(rows, venues)
    mobile, mobile_map = build_mobile(rows, venues)
    output, temp = s.task_dirs(RUN_ID, TASK)
    s.write_json(output / "schedule-audit.json", audit(rows, venues, wide_map, mobile_map, axis))
    s.write_json(temp / "computed-input.json", {"events": rows, "axis": axis, "venues": venues})
    images = []
    for stem, dsl in (("agenda-wide", wide), ("agenda-mobile", mobile)):
        image, record = s.render(RUN_ID, TASK, dsl, stem, "v001", final=False, kind="baseline")
        s.write_json(temp / f"{stem}-baseline-response.json", record)
        images.append(image)
        print(image)
    print(json.dumps({"wide_pixels_per_minute": axis["pixels_per_minute"], "mobile_count": len(mobile_map), "conflicts": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
