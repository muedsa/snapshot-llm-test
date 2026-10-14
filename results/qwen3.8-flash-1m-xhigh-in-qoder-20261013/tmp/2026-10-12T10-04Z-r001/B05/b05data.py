"""B05 data layer - one source of truth for the whole product suite.

"药盒" is a household medicine-shelf manager. Every screen in the special reads from this
module: the same five medicines, the same three family members, the same dates. Numbers on
the screens (days of supply left, expiry buckets, adherence, refill lead time) are derived
here, never typed per screen, so the suite cannot contradict itself.

Run: python tmp/<run_id>/B05/b05data.py     (writes data.json and prints a summary)
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B05"

TODAY = date(2026, 10, 13)          # the day the suite was laid out
HOUSEHOLD = "望云里 7 号楼 3 单元 502"

PEOPLE = [
    {"id": "gm", "name": "周秀兰", "rel": "母亲", "age": 78, "initial": "周",
     "note": "视力弱，字号需 ≥22pt"},
    {"id": "me", "name": "周成", "rel": "本人", "age": 47, "initial": "成",
     "note": "管理员，负责补货与录入"},
    {"id": "da", "name": "周雨桐", "rel": "女儿", "age": 12, "initial": "桐",
     "note": "仅哮喘按需用药"},
]

# pack: total tablets/syrup ml at purchase; per_dose: amount taken per dose
# doses: list of clock times per day (empty = 按需)
MEDS = [
    {"id": "M1", "name": "苯磺酸氨氯地平片", "short": "降压药", "who": "gm",
     "form": "片", "pack": 28, "per_dose": 1, "doses": ["08:00"],
     "bought": date(2026, 9, 20), "expiry": date(2027, 4, 30),
     "rx": "H 市一院 心内科", "refill_days": 7, "storage": "常温避光",
     "note": "不可自行停药（医嘱原文见病历）"},
    {"id": "M2", "name": "二甲双胍缓释片", "short": "降糖药", "who": "gm",
     "form": "片", "pack": 60, "per_dose": 1, "doses": ["08:00", "20:00"],
     "bought": date(2026, 9, 28), "expiry": date(2026, 11, 2),
     "rx": "H 市一院 内分泌", "refill_days": 10, "storage": "常温干燥",
     "note": "随餐服"},
    {"id": "M3", "name": "阿托伐他汀钙片", "short": "降脂药", "who": "gm",
     "form": "片", "pack": 30, "per_dose": 1, "doses": ["22:00"],
     "bought": date(2026, 8, 15), "expiry": date(2026, 10, 20),
     "rx": "H 市一院 心内科", "refill_days": 7, "storage": "常温避光",
     "note": "复查时医生评估是否继续"},
    {"id": "M4", "name": "布地奈德福莫特罗吸入剂", "short": "哮喘按需", "who": "da",
     "form": "吸", "pack": 60, "per_dose": 1, "doses": [],
     "bought": date(2026, 6, 3), "expiry": date(2027, 1, 15),
     "rx": "儿童医院 呼吸科", "refill_days": 14, "storage": "常温，勿冻",
     "note": "按需使用，剂量由发作决定 → 剩余量靠手动记数"},
    {"id": "M5", "name": "维生素 D 滴剂", "short": "补充剂", "who": "me",
     "form": "滴", "pack": 400, "per_dose": 1, "doses": ["12:30"],
     "bought": date(2026, 10, 8), "expiry": date(2028, 3, 31),
     "rx": "自购（非处方）", "refill_days": 5, "storage": "避光，开封后 3 个月",
     "note": "开封日 2026-10-08 → 以开封期限制为准"},
]
# taken / missed log for the last 14 days, per (med, day) -> status
TAKEN = {"M1": 14, "M2": 25, "M3": 13, "M4": 0, "M5": 4}
DOSE_COUNT = {m["id"]: max(len(m["doses"]), 1) for m in MEDS}
SCHEDULED_14 = {m["id"]: 14 * DOSE_COUNT[m["id"]] for m in MEDS}

# remaining units, as counted at the last inventory sweep (2026-10-12 21:40)
REMAIN = {"M1": 5, "M2": 26, "M3": 3, "M4": 41, "M5": 372}


def days_supply(m):
    per_day = DOSE_COUNT[m["id"]] * m["per_dose"]
    if not m["doses"]:
        return None                      # 按需：无法用天数估计
    return REMAIN[m["id"]] / per_day


def expiry_bucket(m):
    d = (m["expiry"] - TODAY).days
    opened = m.get("opened_limit")
    if d < 0:
        return "已过期", d
    if d <= 7:
        return "7 天内", d
    if d <= 30:
        return "30 天内", d
    if d <= 90:
        return "90 天内", d
    return "充足", d


def derive():
    out = []
    for m in MEDS:
        ds = days_supply(m)
        label, dleft = expiry_bucket(m)
        # 开封后期限（滴剂）：以开封日 + 90 天为更紧的限制
        eff_expiry, eff_label, eff_days = m["expiry"], label, dleft
        if m["id"] == "M5":
            opened_end = date(2026, 10, 8) + timedelta(days=90)
            od = (opened_end - TODAY).days
            if od < dleft:
                eff_expiry, eff_days, eff_label = opened_end, od, "开封期 90 天内"
        row = dict(m)
        row.update({
            "bought_iso": m["bought"].isoformat(),
            "expiry_iso": m["expiry"].isoformat(),
            "eff_expiry_iso": eff_expiry.isoformat(),
            "eff_label": eff_label, "eff_days": eff_days,
            "printed_expiry_days": dleft, "printed_bucket": label,
            "expiry_days": expiry_bucket({"expiry": eff_expiry})[1],
            "expiry_bucket": expiry_bucket({"expiry": eff_expiry})[0],
            "remaining": REMAIN[m["id"]], "doses_per_day": DOSE_COUNT[m["id"]],
            "days_supply": None if ds is None else round(ds, 1),
            "runs_out": None if ds is None else
            (TODAY + timedelta(days=int(ds))).isoformat(),
            "need_refill": bool(ds is not None and ds <= m["refill_days"] + 3),
            "adherence_14": (round(100 * TAKEN[m["id"]] / SCHEDULED_14[m["id"]], 1)
                             if SCHEDULED_14[m["id"]] and m["doses"] else None),
        })
        row["expiry"] = m["expiry"].isoformat()
        out.append(row)
    return out


def today_schedule():
    """Every dose slot for today, with status taken/missed/upcoming."""
    slots = []
    for m in MEDS:
        for t in m["doses"]:
            hh, mm = (int(x) for x in t.split(":"))
            done = (hh * 60 + mm) <= (TODAY.hour if False else 21 * 60 + 40)
            slots.append({"time": t, "med": m["name"], "short": m["short"],
                          "who": m["who"], "amount": f"{m['per_dose']} {m['form']}",
                          "state": "已服" if done else "待服"})
    slots.sort(key=lambda s: s["time"])
    return slots


def day_grid():
    """14-day taken/missed log per medicine, oldest cell first.

    Fills from the newest day backwards until the 14-day taken count is used up, so a
    medicine with a partial day shows one amber cell and the misses sit at the far end
    of the window - the same window the quoted adherence rate covers.
    """
    days = [(TODAY - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    grid = {}
    for m in MEDS:
        if not m["doses"]:
            continue
        n = DOSE_COUNT[m["id"]]
        left = TAKEN[m["id"]]
        cells = []
        for _ in range(14):
            take = min(n, left)
            left -= take
            cells.append(["取"] * take + ["漏"] * (n - take))
        cells.reverse()
        assert sum(c.count("取") for c in cells) == TAKEN[m["id"]]
        grid[m["id"]] = cells
    return days, grid




ROWS = derive()
DAYS, GRID = day_grid()
DATA = {
    "today": TODAY.isoformat(), "household": HOUSEHOLD,
    "people": PEOPLE, "meds": ROWS, "schedule_today": today_schedule(),
    "days14": DAYS, "grid14": GRID,
    "summary": {
        "items": len(ROWS),
        "expiring_7": [r["id"] for r in ROWS if 0 <= r["expiry_days"] <= 7],
        "expiring_30": [r["id"] for r in ROWS if 7 < r["expiry_days"] <= 30],
        "expiring_90": [r["id"] for r in ROWS if 30 < r["expiry_days"] <= 90],
        "safe": [r["id"] for r in ROWS if r["expiry_days"] > 90],
        "need_refill": [r["id"] for r in ROWS if r["need_refill"]],
        "as_needed": [r["id"] for r in ROWS if not r["doses"]],
    },
}
assert (sorted(DATA["summary"]["expiring_7"] + DATA["summary"]["expiring_30"]
              + DATA["summary"]["expiring_90"] + DATA["summary"]["safe"]) ==
        sorted([r["id"] for r in ROWS]))
assert DATA["summary"]["expiring_7"] == ["M3"]
assert DATA["summary"]["need_refill"] == ["M1", "M2", "M3"]
# the opened-bottle rule, not the printed date, is what the buckets follow
assert [r["id"] for r in ROWS if r["expiry_bucket"] == "90 天内"] == ["M5"]
assert [r for r in ROWS if r["id"] == "M5"][0]["expiry_days"] == 85
# per-person statistics, aggregated from the same 14-day log the grids come from, so
# no screen can quote a rate the medicine rows do not add up to
PER_PERSON = {}
for p in PEOPLE:
    rows = [r for r in ROWS if r["who"] == p["id"]]
    sched = [r for r in rows if r["doses"]]
    got = sum(TAKEN[r["id"]] for r in sched)
    need = sum(SCHEDULED_14[r["id"]] for r in sched)
    PER_PERSON[p["id"]] = {"scheduled_meds": len(sched),
                           "as_needed_meds": len(rows) - len(sched),
                           "taken_14": got, "due_14": need,
                           "missed_14": need - got,
                           "adherence_14": round(100 * got / need, 1) if need else None}
DATA["per_person"] = PER_PERSON
DATA["week_days"] = DAYS[-7:]
DATA["week_grid"] = {k: [r[i] for i in range(7, 14)] for k, r in
                        GRID.items()}

gm = PER_PERSON["gm"]
assert gm["taken_14"] == sum(TAKEN[i] for i in ("M1", "M2", "M3"))
assert gm["due_14"] == sum(SCHEDULED_14[i] for i in ("M1", "M2", "M3"))
assert gm["missed_14"] == gm["due_14"] - gm["taken_14"]
assert PER_PERSON["da"]["adherence_14"] is None and PER_PERSON["da"]["due_14"] == 0

(TMP / "data.json").write_text(
    json.dumps(DATA, ensure_ascii=False, indent=2, default=str),
    encoding="utf-8")
for r in ROWS:
    print(f"{r['id']} {r['short']:8s} 余{r['remaining']:>4} "
          f"可服{str(r['days_supply']):>6}天 效期{r['expiry_days']:>4}天"
          f"({r['expiry_bucket']}) 依从{r['adherence_14']}")
print("today slots:", len(DATA["schedule_today"]), "week days:", len(DAYS))
