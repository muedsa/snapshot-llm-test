"""B02 case-03 - 潮水位 · App 实时预警页 (390x844, 手机竖屏).

Touchpoint: the phone screen a resident opens at 21:47 in a dark flat. Everything is sized
for 30 cm viewing on a 390 pt canvas: a 11-14 px UI scale is legitimate here (and is the
only place in the ecosystem that uses it), while the one number that decides what they do
next is set at 64 px. Same station, same thresholds, same forecast as the poster.

Run:  python tmp/<run_id>/B02/case03_app.py
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
W, H = 390, 844
M = 16
SID, NAME, NOW, SERIES, DRAIN = data.TOP_STATION
CARD = "#FFFFFF"


def rate_and_eta():
    r = (SERIES[-1] - SERIES[-4]) / 3.0
    return round(r, 1), round((data.DISASTER_CM - NOW) / (r / 60.0))


def build():
    rate, eta = rate_and_eta()
    lv = data.LEVELS[data.CURRENT_LEVEL - 1]
    s = tide.sheet(W, H, min_font=11)
    tide.assert_contrast([(tide.INK, CARD, "ink on card"), (tide.INK_3, CARD, "meta on card"),
                          (lv["ink"], lv["colour"], "level banner text")], 4.5)
    s.rect(0, 0, W, H, tide.PAPER)

    # ---- status bar
    s.text("clock", "21:47", M, 8, 13, tide.INK, bold=True, font=MONO)
    for i, hgt in enumerate((5, 8, 11, 14)):
        s.rect(W - 74 + i * 5, 20 - hgt, 3, hgt, tide.INK)
    s.rect(W - 46, 10, 22, 11, "#00000000", border="1.5 SOLID " + tide.INK, radius=3)
    s.rect(W - 44, 12, 15, 7, tide.INK, radius=2)
    s.rect(W - 23, 13, 2, 5, tide.INK)

    # ---- app header
    y = 34
    tide.mark(s, M, y, 26, tide.INK)
    s.text("wm", "水位线", M + 36, y + 3, 17, tide.INK, bold=True)
    s.text("loc", "江北 · 书院社区", W - M - 34, y + 5, 12, tide.INK_3, align="right")
    s.dot(W - M - 12, y + 12, 9, "#00000000", ring=tide.INK_3, ring_w=1.5)
    s.text("bell", "!", W - M - 12, y + 6, 12, tide.INK_3, align="center", bold=True)
    y += 38

    # ---- level banner
    s.rect(M, y, W - 2 * M, 56, lv["colour"], radius=12)
    s.text("lb", f"{lv['code']} 级 · {lv['name']}", M + 14, y + 10, 22, lv["ink"], bold=True)
    s.text("lb2", f"21:47 更新 · 沿河 6 站", M + 14, y + 36, 12, lv["ink"])
    s.text("lb3", f"{SID}", W - M - 14, y + 14, 14, lv["ink"], align="right", font=MONO)
    y += 68

    # ---- hero reading
    s.text("hk", "门口水位", M + 2, y, 12, tide.INK_3)
    s.text("hv", f"{NOW:.0f}", M + 2, y + 16, 64, tide.INK, bold=True, font=MONO)
    hvw = tw(f"{NOW:.0f}", 64, True)
    s.text("hu", "cm", M + 8 + hvw, y + 46, 18, tide.INK_3, font=MONO)
    s.text("hr", f"涨速 {rate:+.1f} cm/h", W - M, y + 20, 15, tide.ALARM, align="right",
           bold=True, font=MONO)
    s.text("he", f"约 {eta} 分钟后到灾难级", W - M, y + 42, 12, tide.INK_2, align="right")
    y += 92

    # ---- 24 h chart card
    s.rect(M, y, W - 2 * M, 142, CARD, radius=12, border=f"1 SOLID {tide.LINE}")
    s.text("ck", "过去 24 小时 · 厘米", M + 12, y + 10, 12, tide.INK_3)
    gx, gy, gw, gh = M + 12, y + 30, W - 2 * M - 24, 76
    lo, hi = 30, 80
    for cm, col, lab in ((data.WARN_CM, tide.CYAN, "警戒"), (data.CRIT_CM, tide.SAND, "紧急"),
                         (data.DISASTER_CM, tide.ALARM, "灾难")):
        yy = gy + gh - gh * (cm - lo) / (hi - lo)
        s.line(gx, yy, gx + gw, yy, col, 1.2)
        s.text("cl", lab, gx + 4, yy - 15, 11, col)
    pts = [(gx + gw * i / (len(SERIES) - 1), gy + gh - gh * (v - lo) / (hi - lo))
           for i, v in enumerate(SERIES)]
    body = [(gx, gy + gh)] + pts + [(gx + gw, gy + gh)]
    d = "M " + " L ".join(f"{p[0] - gx:.1f} {p[1] - gy:.1f}" for p in body) + " Z"
    s.path(gx, gy, gw, gh, d, tide.WATER, opacity=0.25)
    for a, b in zip(pts, pts[1:]):
        s.line(a[0], a[1], b[0], b[1], tide.WATER, 2)
    s.dot(pts[-1][0], pts[-1][1], 4, tide.ALARM)
    for i, lab in enumerate(("00:00", "06:00", "12:00", "18:00", "24:00")):
        s.text("cx", lab, gx + gw * i / 4, gy + gh + 8, 11, tide.INK_3,
               align="center" if 0 < i < 4 else ("left" if i == 0 else "right"), font=MONO)
    y += 152

    # ---- action card
    s.rect(M, y, W - 2 * M, 118, "#FBF3E4", radius=12, border=f"1.5 SOLID {tide.SAND}")
    s.text("ak", "现在该做", M + 12, y + 10, 12, tide.SAND, bold=True)
    ey = s.para("av", lv["action"], M + 12, y + 28, 15, tide.INK, width=W - 2 * M - 24)
    s.text("as", "· 需要帮助按下方「呼叫组长」；断电由物业执行", M + 12, ey + 4, 11,
           tide.INK_2)
    assert ey + 4 + 12 <= y + 114, ey
    y += 130

    # ---- nearest shelter row
    code, nm, fx, fy, cap, storey, opened = min(
        data.SHELTERS, key=lambda t: data.shelter_reach(t[0])[0])
    dist, mins = data.shelter_reach(code)
    s.rect(M, y, W - 2 * M, 58, CARD, radius=12, border=f"1 SOLID {tide.LINE}")
    s.dot(M + 28, y + 29, 12, tide.SAFE)
    s.text("sc", code.split("-")[1], M + 28, y + 23, 11, tide.PAPER, align="center",
           bold=True, font=MONO)
    s.text("sn", f"最近集合点 {code} {nm}", M + 48, y + 12, 14, tide.INK, bold=True)
    s.text("sd", f"{dist / 1000:.1f} km · 步行 {mins} 分钟 · {cap} 人 · {storey}",
           M + 48, y + 32, 11, tide.INK_3)
    tide.chevrons(s, W - M - 22, y + 20, 12, tide.INK_3, n=2, step=0.7, weight=1.6)
    y += 70

    # ---- three tiles
    tiles = [("上报积水", "#E7EEF5", tide.CYAN), ("物资柜", "#EAF1EC", tide.SAFE),
             ("呼叫组长", "#F6EAE8", tide.ALARM)]
    twd = (W - 2 * M - 2 * 10) / 3
    for i, (lab, bg, col) in enumerate(tiles):
        x = M + i * (twd + 10)
        s.rect(x, y, twd, 62, bg, radius=12)
        s.rect(x + 12, y + 12, 16, 16, col, radius=4)
        s.text("tl", lab, x + 12, y + 36, 12, tide.INK, bold=True)
        assert tw(lab, 12) <= twd - 20, lab
    y += 62
    s.text("tk", "今晚社区任务", M + 2, y, 12, tide.INK_3, bold=True)
    s.text("ts", f"待接 {data.TASK_COUNTS['待接']} · 进行中 {data.TASK_COUNTS['进行中']} · "
                 f"已完成 {data.TASK_COUNTS['已完成']}", W - M, y, 11, tide.INK_3,
           align="right")
    y += 20
    for tid, kind, place, prio, state, owner, eta in [x for x in data.TASKS
                                                      if x[4] == "待接"][:2]:
        s.rect(M, y, W - 2 * M, 34, CARD, radius=8, border=f"1 SOLID {tide.LINE}")
        s.rect(M + 10, y + 10, 14, 14, tide.SAND if prio == "高" else tide.CYAN, radius=4)
        s.text("ti", f"{tid} {kind} · {place}", M + 32, y + 9, 12, tide.INK)
        s.text("te", f"{eta} 分", W - M - 10, y + 9, 11, tide.INK_3, align="right",
               font=MONO)
        assert tw(f"{tid} {kind} · {place}", 12) <= W - 2 * M - 78, tid
        y += 40
    y += 4
    s.text("demo", "演示界面：站点、水位与社区均为虚构示例。", W / 2, y, 11, tide.INK_3,
           align="center")
    y += 22

    # ---- tab bar
    s.rect(0, H - 58, W, 58, CARD, border=f"1 SOLID {tide.LINE}")
    tabs = ["首页", "地图", "上报", "我的"]
    for i, lab in enumerate(tabs):
        cx = W * (i + 0.5) / 4
        on = i == 0
        s.rect(cx - 9, H - 46, 18, 14, tide.INK if on else tide.INK_3, radius=3)
        s.text("tb", lab, cx, H - 26, 11, tide.INK if on else tide.INK_3, align="center")
    assert y <= H - 66, y
    return s, {"station": SID, "now_cm": NOW, "rate_cm_per_h": rate, "eta_min": eta,
               "level": lv, "nearest_shelter": [code, nm, dist, mins, cap, storey],
               "series": SERIES, "canvas": [W, H], "min_font": 11,
               "read_at": "30 cm 手机竖屏"}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case03.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case03-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=8), ensure_ascii=False))
