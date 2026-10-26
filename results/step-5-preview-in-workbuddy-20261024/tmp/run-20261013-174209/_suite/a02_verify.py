"""A02 交付自检：核对时间比例几何、内容完整性与文件配对。"""
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A02"
TASK_DIR = ROOT / "tasks" / "A02-conference-schedule"

audit = json.loads((OUT / "schedule-audit.json").read_text(encoding="utf-8"))
wide = (OUT / "agenda-wide.snapshot").read_text(encoding="utf-8")
mobile = (OUT / "agenda-mobile.snapshot").read_text(encoding="utf-8")

with (TASK_DIR / "inputs" / "agenda.csv").open(encoding="utf-8", newline="") as fh:
    src = list(csv.DictReader(fh))

checks = []


def chk(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})


chk("event_count_15", len(audit["events"]) == 15, str(len(audit["events"])))
chk("audit_identity", audit["schema_version"] == 1 and audit["task_id"] == "A02"
    and audit["path_base"] == "output_dir")
chk("timezone", audit["time_axis"]["timezone"] == "Asia/Shanghai")
chk("axis_window", audit["time_axis"]["start"] == "09:00" and audit["time_axis"]["end"] == "16:00")
chk("proportional", audit["time_axis"]["proportional_block_length"] is True)
chk("times_unmodified", audit["time_axis"]["input_times_unmodified"] is True)

# 起止时间与输入一致
for s, a in zip(src, audit["events"]):
    chk(f"time_{s['id']}", s["start"] == a["start"] and s["end"] == a["end"],
        f"{a['start']}-{a['end']}")
    chk(f"minutes_{s['id']}", a["minutes"] == int(s["end"][:2]) * 60 + int(s["end"][3:])
        - int(s["start"][:2]) * 60 - int(s["start"][3:]))

starts = {e["id"]: int(e["start"][:2]) * 60 + int(e["start"][3:]) for e in audit["events"]}
durs = {e["id"]: e["minutes"] for e in audit["events"]}
boxes = {c["event"]: c["wide"]["block_px_box"] for c in audit["content_map"]}

# 大图像素盒与时长成比例（audit 中记录值保留 1 位小数，容差取 0.5px 舍入 + 1e-6）
PX0 = audit["time_axis"]["px_start"]
PPM = audit["time_axis"]["px_per_minute"]
max_w_err = max(abs((boxes[k][2] - boxes[k][0]) - durs[k] * PPM) for k in boxes)
chk("block_width_proportional", max_w_err <= 0.5 + 1e-6,
    f"px_per_min={PPM:.6f} max_width_err={max_w_err:.4f}")
max_x_err = max(abs(boxes[k][0] - (PX0 + (starts[k] - 540) * PPM)) for k in boxes)
chk("block_x_proportional", max_x_err <= 0.5 + 1e-6,
    f"max_x_err={max_x_err:.4f}")
chk("zero_start_blocks", all(abs(boxes[k][0] - PX0) <= 0.5 + 1e-6
                             for k in boxes if starts[k] == 540),
    str([k for k in boxes if starts[k] == 540]))

# 无冲突且未捏造
chk("conflicts_empty", audit["conflicts"] == [])
chk("conflict_count_zero", audit["conflict_check"]["conflict_count"] == 0)

# 空档保留
chk("gaps_recorded", len(audit["venue_gaps"]) > 0, str(len(audit["venue_gaps"])))
chk("lunch_recorded", any(g["kind"] == "common_lunch" for g in audit["venue_gaps"]))

# 大图内容完整
for e in src:
    chk(f"wide_has[{e['id']}]", e["id"] in wide)
    chk(f"wide_title[{e['id']}]", e["title"] in wide)
    chk(f"wide_time[{e['id']}]", e["start"] in wide and e["end"] in wide)
    chk(f"wide_speaker[{e['id']}]", e["speaker"] in wide)
    chk(f"mobile_has[{e['id']}]", e["id"] in mobile)
    chk(f"mobile_title[{e['id']}]", e["title"] in mobile)
    chk(f"mobile_venue[{e['id']}]", e["venue"] in mobile)
    chk(f"mobile_time[{e['id']}]", e["start"] in mobile and e["end"] in mobile)

# 讲者在手机图外移说明
chk("mobile_speaker_note", "讲者详见完整日程" in mobile)
# 午休未合并
chk("lunch_in_wide", "公共午休 12:00–13:00" in wide)
chk("lunch_in_mobile", "公共午休 12:00–13:00" in mobile)
# 容量
for v, cap in (("A", 320), ("B", 80), ("C", 160)):
    chk(f"capacity_{v}", str(cap) in wide, f"{cap}")
    chk(f"venue_label_{v}", f"{v} 会场" in wide)
# 读图方法
chk("how_to_read", "读图方法" in wide)
# 类别标签
for cat, label in json.loads((TASK_DIR / "inputs" / "venues.json").read_text(encoding="utf-8"))["categories"].items():
    chk(f"category_{cat}", label in wide)
# 文件配对
for base in ["agenda-wide", "agenda-mobile"]:
    p = OUT / f"{base}.png"
    chk(f"png_{base}", p.exists() and p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n")
    s = OUT / f"{base}.snapshot"
    chk(f"snap_{base}", s.exists() and "<Snapshot" in s.read_text(encoding="utf-8"))
chk("no_external_image", "<Image" not in wide and "<Image" not in mobile
    and "dataUri" not in wide and "dataUri" not in mobile)
chk("no_hardcoded_path", not re.search(r"[A-Za-z]:\\\\", wide + mobile))
chk("content_map_covers_all", len(audit["content_map"]) == 15)

fails = [c for c in checks if not c["passed"]]
print(json.dumps({"total": len(checks), "failed": len(fails), "failures": fails[:20]},
                 ensure_ascii=False, indent=2))
