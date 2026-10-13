"""B02 case-05 - 夜间调度板 · 任务与志愿者状态 (1920x1080 值班室大屏).

Touchpoint: the wall in the street duty room, read from ten metres while people are moving.
Type floor is 24 px, task cards are one decision each, and the six station bars at the
bottom repeat exactly what the poster and the app show, so nobody in the room is arguing
about which number is current.

Run:  python tmp/<run_id>/B02/case05_wall.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import data  # noqa: E402
import tide  # noqa: E402
from bkit import MONO, SANS, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B02"
W, H = 1920, 1080
PRIO = {"紧急": tide.ALARM, "高": tide.SAND, "中": tide.CYAN}
STATE = {"待接": tide.ALARM, "进行中": tide.SAND, "已完成": tide.SAFE}


def build():
    lv = data.LEVELS[data.CURRENT_LEVEL - 1]
    s = tide.sheet(W, H, min_font=24)
    tide.assert_contrast([(tide.PAPER, tide.INK, "paper on ink"),
                          (tide.INK, "#FFFFFF", "ink on card")], 4.5)
    s.rect(0, 0, W, H, tide.INK)

    # ---- header
    tide.lockup(s, 56, 40, 72, tide.PAPER, latin=False)
    s.text("title", "夜间调度板", 56 + 72 + 30 + tw(data.ORG, 72 * 0.52) + 40, 56, 44,
           tide.PAPER, bold=True)
    s.text("clock", "21:47 · 值班：江北街道", W - 56, 56, 30, "#9FB2BE", align="right",
           font=MONO)
    tide.status_pill(s, W - 56 - 470, 100, data.CURRENT_LEVEL, h=52, size=28,
                     extra=f"{data.TOP_STATION[1]} {data.TOP_STATION[2]:.0f} cm")
    s.line(56, 152, W - 56, 152, "#2C3B49", 2)

    # ---- task board
    s.text("bh", f"任务板 · 共 {len(data.TASKS)} 项", 56, 172, 30, tide.PAPER, bold=True)
    s.text("bh2", f"待接 {data.TASK_COUNTS['待接']} · 进行中 {data.TASK_COUNTS['进行中']} · "
                  f"已完成 {data.TASK_COUNTS['已完成']}", 56 + 300, 176, 26, "#9FB2BE",
           font=MONO)
    cols, rows = 3, 3
    cw, ch, gap = 366, 176, 16
    x0, y0 = 56, 220
    for i, (tid, kind, place, prio, state, owner, eta) in enumerate(data.TASKS):
        cx = x0 + (i % cols) * (cw + gap)
        cy = y0 + (i // cols) * (ch + gap)
        s.rect(cx, cy, cw, ch, "#FFFFFF", radius=14)
        s.rect(cx, cy, 12, ch, STATE[state], radius=6)
        s.text("ti", tid, cx + 30, cy + 18, 26, tide.INK_3, font=MONO)
        s.text("tp", prio, cx + cw - 30, cy + 18, 26, PRIO[prio], align="right", bold=True)
        s.text("tk", kind, cx + 30, cy + 56, 34, tide.INK, bold=True)
        s.text("tl", place, cx + 30, cy + 102, 26, tide.INK_2)
        s.text("tv", state, cx + 30, cy + 140, 28, STATE[state], bold=True)
        who = owner or "未认领"
        own = f"{who} · {eta} 分" if eta else who
        assert tw(state, 28) + 30 + tw(own, 24, True) <= cw - 30, own
        s.text("to", own, cx + cw - 30, cy + 142, 24, tide.INK_3,
               align="right", font=MONO)
        assert tw(place, 26) <= cw - 60, place
    assert y0 + rows * (ch + gap) <= 812, y0 + rows * (ch + gap)

    # ---- right: roster
    rx = x0 + cols * (cw + gap) + 24
    s.text("rh", f"志愿者 · 在线 {len(data.ONLINE)} / 登记 {data.REGISTERED}", rx, 172, 30,
           tide.PAPER, bold=True)
    yy = 220
    for v in data.VOLUNTEERS:
        col = {"在岗": tide.SAFE, "待命": tide.CYAN, "休息": "#9FB2BE",
               "离线": "#4A5A68"}[v["status"]]
        s.rect(rx, yy - 5, 604, 30, "#1B2A36" if v["status"] in ("在岗", "待命")
               else "#16232E", radius=6)
        s.dot(rx + 18, yy + 9, 6, col)
        s.text("vn", v["name"], rx + 36, yy - 1, 24, tide.PAPER)
        s.text("vr", v["role"], rx + 148, yy - 1, 24, "#9FB2BE")
        s.text("vs", v["status"], rx + 316, yy - 1, 24, col, bold=True)
        s.text("vt", v["since"], rx + 580, yy - 1, 24, "#7A8B98", align="right", font=MONO)
        yy += 32
    s.text("rn", f"今晚排班 {len(data.VOLUNTEERS)} 人 · 在线 {len(data.ONLINE)} 人 · "
                 f"登记 {data.REGISTERED} 人", rx, yy + 2, 24, "#7A8B98")
    assert yy <= 812, yy

    # ---- bottom: station bars
    s.line(56, 830, W - 56, 830, "#2C3B49", 2)
    s.text("sh", "沿河 6 站实时水位（厘米）", 56, 848, 28, tide.PAPER, bold=True)
    bw = (W - 112 - 5 * 22) / 6
    for i, (sid, name, now, ser, drain) in enumerate(data.STATIONS):
        x = 56 + i * (bw + 22)
        code = data.classify(now)
        col = tide.LEVEL_COLOUR[code]
        s.rect(x, 890, bw, 96, "#16232E", radius=10)
        frac = min(now, 90) / 90.0
        s.rect(x + 14, 946, (bw - 28) * frac, 22, col, radius=6)
        for cm in (data.WARN_CM, data.CRIT_CM, data.DISASTER_CM):
            tx = x + 14 + (bw - 28) * cm / 90.0
            s.line(tx, 940, tx, 974, "#9FB2BE", 1.5)
        s.text("sb", f"{sid} {name}", x + 14, 902, 24, tide.PAPER)
        s.text("sv", f"{now:.0f}", x + bw - 14, 900, 30, col, align="right", bold=True,
               font=MONO)
        s.text("st", f"{code} 级 · {tide.LEVEL_NAME[code]}", x + 14, 978 - 2, 24, col)
    s.text("foot", "演示数据：街道、站点、人名与任务均为虚构示例；大屏每 5 分钟由同一数据源刷新。",
           56, 1014, 24, "#7A8B98")
    return s, {"level": data.CURRENT_LEVEL, "tasks": [list(t) for t in data.TASKS],
               "task_counts": data.TASK_COUNTS, "online": len(data.ONLINE),
               "registered": data.REGISTERED,
               "stations": [{"id": x[0], "name": x[1], "cm": x[2], "level": data.classify(x[2])}
                            for x in data.STATIONS],
               "min_font": 24, "read_at": "10 m 值班室墙面"}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case05.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case05-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
