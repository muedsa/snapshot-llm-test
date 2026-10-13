"""B02 case-02 - 汛期四级行动 · 社区公告海报 (900x1350).

Touchpoint: the noticeboard at the mouth of the lane. A resident walking past, possibly an
older resident without a phone, has to leave knowing three things: what level it is now,
where the meeting point is, and who to call. Everything is set for 1-2 m reading: 26 px
floor, one idea per block, the level colour carrying the hierarchy.

Run:  python tmp/<run_id>/B02/case02_poster.py
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
W, H = 1000, 1500
M = 56
SID, NAME, NOW, SERIES, DRAIN = data.TOP_STATION


def climb():
    """Rate over the last three hours and the minutes left before the disaster mark."""
    rate = (SERIES[-1] - SERIES[-4]) / 3.0
    mins = (data.DISASTER_CM - NOW) / (rate / 60.0) if rate > 0 else None
    return round(rate, 1), (round(mins) if mins else None)


def build():
    rate, mins = climb()
    lv = data.LEVELS[data.CURRENT_LEVEL - 1]
    s = tide.sheet(W, H, min_font=26)
    tide.assert_contrast([(tide.PAPER, tide.INK, "ink band"), (tide.INK, tide.PAPER, "body")],
                         4.5)

    # ---- ink header band
    s.rect(0, 0, W, 186, tide.INK)
    tide.mark(s, M, 40, 64, tide.PAPER)
    s.text("wm", data.ORG, M + 88, 44, 34, tide.PAPER, bold=True)
    s.text("wm2", "TIDELINE · 江北街道", M + 88, 92, 26, "#9FB2BE", font=MONO)
    s.text("up", "2026-10-13 21:47 更新", W - M, 44, 26, tide.PAPER, align="right",
           font=MONO)
    s.text("up2", "沿河 6 站 · 每 5 分钟刷新", W - M, 80, 26, "#9FB2BE",
           align="right")
    tide.status_pill(s, M, 128, data.CURRENT_LEVEL, h=52, size=28,
                     extra=f"{NAME} {NOW:.0f} cm")

    # ---- hero line
    y = 222
    s.text("hero", f"现在：{NAME} {NOW:.0f} 厘米", M, y, 44, tide.INK, bold=True)
    hero2 = (f"涨速 {rate:+.1f} 厘米/小时 · 约 {mins} 分钟后到灾难级" if mins
             else "涨速趋缓，维持当前等级")
    assert tw(hero2, 28) <= W - 2 * M, tw(hero2, 28)
    s.text("hero2", hero2, M, y + 62, 28, tide.ALARM if mins and mins <= 30 else tide.INK_2)
    y += 118

    # ---- four levels
    s.text("h", "四级行动：现在该做什么", M, y, 30, tide.INK, bold=True)
    y += 46
    for lv in data.LEVELS:
        h = 80
        now = lv["code"] == data.CURRENT_LEVEL
        s.rect(M, y, W - 2 * M, h, lv["colour"] if now else tide.PANEL, radius=10)
        s.rect(M, y, 10, h, lv["colour"], radius=5)
        ink = lv["ink"] if now else tide.INK
        s.text("lc", f"{lv['code']} 级 · {lv['name']}", M + 28, y + 10, 28, ink, bold=True)
        s.text("la", lv["action"], M + 28, y + 44, 26, ink)
        if now:
            s.text("cn", "← 当前", W - M - 14, y + 12, 26, ink, align="right", bold=True)
        assert tw(lv["action"], 26) <= W - 2 * M - 44, lv
        y += h + 6

    # ---- meeting points table
    y += 10
    s.text("h2", "集合点：到了这里才算安全", M, y, 30, tide.INK, bold=True)
    y += 46
    cols = [M, M + 100, M + 430, M + 580, M + 680]
    for c, lab in zip(cols, ["编号", "集合点", "容量", "楼层", "步行"]):
        s.text("th", lab, c, y, 26, tide.INK_3, bold=True)
    y += 40
    s.line(M, y - 10, W - M, y - 10, tide.LINE, 1.5)
    for code, nm, fx, fy, cap, storey, opened in data.SHELTERS:
        dist, mins = data.shelter_reach(code)
        s.rect(M, y - 6, W - 2 * M, 46, tide.PANEL if opened else "#F0D9D5", radius=6)
        s.text("cd", code, cols[0] + 12, y + 4, 26, tide.INK, bold=True, font=MONO)
        s.text("nm", nm, cols[1], y + 4, 26, tide.INK)
        s.text("cp", f"{cap} 人", cols[2], y + 4, 26, tide.INK_2, font=MONO)
        s.text("st", storey, cols[3], y + 4, 26, tide.INK_2, font=MONO)
        s.text("wk", f"{dist / 1000:.1f} km · {mins} 分", cols[4], y + 4, 26,
               tide.INK_2 if opened else tide.ALARM, font=MONO)
        assert tw(nm, 26) <= cols[2] - cols[1] - 8, nm
        assert cols[4] + tw(f"{dist / 1000:.1f} km · {mins} 分", 26, True) <= W - M
        y += 48
    s.text("dir", "L-04 俱乐部今晚未开放（红底）；箭头与方向见小程序地图。", M, y + 6, 26,
           tide.INK_3)
    y += 54

    # ---- three things + contacts
    s.line(M, y, W - M, y, tide.LINE, 2)
    y += 20
    tips = ["走地下通道前先看在岗志愿者，水位过 30 厘米不进入。",
            "带身份证、常用药、手电筒，不需要带现金。",
            "到集合点后先向组长报人数，再领雨具。"]
    for i, t in enumerate(tips):
        assert tw(t, 26) <= W - 2 * M - 44, t
        s.text("num", f"{i + 1}", M, y, 30, tide.CYAN, bold=True, font=MONO)
        s.text("th", t, M + 44, y + 2, 26, tide.INK_2)
        y += 44
    y += 10
    s.rect(M, y, W - 2 * M, 112, tide.INK, radius=10)
    s.text("ph", data.PHONE_STREET, M + 24, y + 16, 28, tide.PAPER, bold=True, font=MONO)
    s.text("ph2", data.PHONE_CITY, M + 24, y + 60, 28, "#9FB2BE", bold=True, font=MONO)
    div = M + 24 + tw(data.PHONE_STREET, 28, True) + 28
    s.line(div, y + 16, div, y + 96, "#3A4C59", 1.5)
    jw = W - M - (div + 24) - 24
    for i, ln in enumerate(["小程序「水位线」→ 绑定本社区", "门牌后 4 位，只推你这一片。"]):
        assert tw(ln, 26) <= jw, (ln, tw(ln, 26))
        s.text("join", ln, div + 24, y + 18 + i * 44, 26, tide.PAPER)
    jend = y + 18 + 44 + 27.6
    assert jend - 15 <= y + 104, jend
    y += 132
    foot = "江北街道 6 个社区共用模板 · 第 12 期 · 虚构演示，数字为示例"
    assert tw(foot, 26) <= W - 2 * M, foot
    s.text("foot", foot, M, y, 26, tide.INK_3)
    assert y + 34 <= H - 20, y
    return s, {"station": {"id": SID, "name": NAME, "now_cm": NOW, "drainage": DRAIN},
               "rate_cm_per_h": rate, "minutes_to_disaster": mins,
               "current_level": data.CURRENT_LEVEL,
               "shelters": [list(x) for x in data.SHELTERS],
               "min_font": 26, "read_at": "1-2 m"}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case02.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case02-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
