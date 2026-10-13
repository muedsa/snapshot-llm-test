"""B02 case-06 - 入汛提醒 · 微信服务卡与推文头图 (900x600).

Touchpoint: the card that gets forwarded into neighbourhood group chats. It has to survive
being seen at 220 px wide in a chat list and still say who this is, what level it is now,
and where to tap - so the mark, the level colour and the three entry names are the only
things that carry meaning at thumbnail size.

Run:  python tmp/<run_id>/B02/case06_card.py
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
W, H = 900, 600
ENTRIES = [("实时水位", "6 站每 5 分钟"), ("集合点导航", "含夜间开放状态"),
           ("上报积水", "拍照定位，5 分钟回执")]


def build():
    lv = data.LEVELS[data.CURRENT_LEVEL - 1]
    s = tide.sheet(W, H, min_font=20)
    tide.assert_contrast([(lv["ink"], lv["colour"], "banner text"),
                          (tide.INK, tide.PAPER, "ink on paper")], 4.5)
    s.rect(0, 0, W, H, tide.PAPER)
    s.rect(0, 0, W, 168, lv["colour"])
    tide.mark(s, 40, 40, 88, tide.PAPER)
    s.text("wm", data.ORG, 148, 48, 44, lv["ink"], bold=True)
    s.text("wm2", "TIDELINE · 江北街道", 148, 106, 24, lv["ink"])
    s.text("lv", f"{lv['code']} 级 · {lv['name']}", W - 40, 52, 40, lv["ink"], bold=True,
           align="right")
    s.text("lvt", f"21:47 · 最高 {data.TOP_STATION[2]:.0f} cm", W - 40, 108, 24,
           lv["ink"], align="right")

    s.text("camp", data.CAMPAIGN, 40, 200, 34, tide.INK, bold=True)
    s.text("sub", "雨前 20 分钟推送到手机；不用下载 App，小程序内绑定门牌即可。",
           40, 250, 24, tide.INK_2)
    ey = 300
    cw = (W - 80 - 2 * 18) / 3
    for i, (name, note) in enumerate(ENTRIES):
        x = 40 + i * (cw + 18)
        s.rect(x, ey, cw, 108, "#FFFFFF", radius=12, border=f"1.5 SOLID {tide.LINE}")
        s.rect(x + 16, ey + 16, 22, 22, tide.LEVEL_COLOUR[data.CURRENT_LEVEL], radius=6)
        s.text("en", name, x + 16, ey + 48, 26, tide.INK, bold=True)
        s.text("ee", note, x + 16, ey + 78, 20, tide.INK_3)
        assert tw(name, 26) <= cw - 32 and tw(note, 20) <= cw - 32, name
    s.line(40, 444, W - 40, 444, tide.LINE, 1.5)
    yy = 456
    for code, nm, fx, fy, cap, storey, opened in data.SHELTERS[:3]:
        dist, mins = data.shelter_reach(code)
        s.dot(52, yy + 12, 9, tide.SAFE if opened else tide.ALARM)
        s.text("sn", f"{code} {nm}", 70, yy, 22, tide.INK)
        s.text("sd", f"{dist / 1000:.1f} km · {mins} 分钟", W - 40, yy, 22, tide.INK_2,
               align="right", font=MONO)
        yy += 30
    s.text("more", f"另有 {len(data.SHELTERS) - 3} 处见小程序地图", 70, yy, 20, tide.INK_3)
    s.text("foot", "虚构演示项目：站点、社区与数字均为示例。", W - 40, H - 50, 20,
           tide.INK_3, align="right")
    return s, {"level": data.CURRENT_LEVEL, "entries": ENTRIES,
               "shelters": [[c[0], c[1], *data.shelter_reach(c[0])] for c in data.SHELTERS[:3]],
               "thumbnail_test_px": 220, "min_font": 20}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case06.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case06-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=24), ensure_ascii=False))
