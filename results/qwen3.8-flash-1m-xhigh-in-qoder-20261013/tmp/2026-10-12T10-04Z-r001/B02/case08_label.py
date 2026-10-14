"""B02 case-08 - 社区物资柜 · 封条清单贴纸 (600x400, 印 100x67 mm).

Touchpoint: the laminated sticker on the inside of a supply cabinet door, read at 30 cm in
a dim shelter. Ten items, their quantity, the last inspection and what is short - the
cabinet keeper signs the seal, the volunteer ticks what they take. Type is small because
the medium is small: 18 px is 3 mm of cap height on the printed label, which is the floor
for this distance.

Run:  python tmp/<run_id>/B02/case08_label.py
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
W, H = 600, 400
MM_PX = 6.0                    # 600 px = 100 mm


def status_col(st):
    return tide.SAFE if st == "OK" else (tide.ALARM if "过期" in st else tide.SAND)


def build():
    s = tide.sheet(W, H, min_font=18)
    tide.assert_contrast([(tide.INK, "#FFFFFF", "ink on white"),
                          (tide.INK_2, tide.PANEL, "body on panel")], 4.5)
    s.rect(0, 0, W, H, "#FFFFFF")
    s.rect(0, 0, W, 56, tide.INK)
    tide.mark(s, 12, 10, 36, tide.PAPER)
    s.text("ti", "物资柜封条清单", 58, 16, 24, tide.PAPER, bold=True)
    s.text("cd", data.CABINET, W - 12, 20, 18, "#9FB2BE", align="right", font=MONO)

    col_w = (W - 24 - 12) / 2
    row_h = 23
    y0 = 68
    for i, (name, qty, checked, st) in enumerate(data.SUPPLIES):
        col, row = i // 5, i % 5
        x = 12 + col * (col_w + 12)
        y = y0 + row * row_h
        s.rect(x, y, col_w, row_h - 4, tide.PANEL if row % 2 == 0 else "#F2EEE4", radius=4)
        s.text("n", name, x + 8, y + 2, 18, tide.INK)
        s.text("q", qty, x + col_w - 78, y + 2, 18, tide.INK_2, font=MONO)
        s.rect(x + col_w - 22, y + 4, 14, 12, status_col(st), radius=3)
        assert tw(name, 18) <= col_w - 96, name
        assert tw(qty, 18, True) <= 70, qty
    y = y0 + 5 * row_h + 4
    s.line(12, y, W - 12, y, tide.LINE, 1.2)
    y += 6
    need = [x for x in data.SUPPLIES if x[3] != "OK"]
    y = s.para("al", "待处理 " + str(len(need)) + " 项："
               + " · ".join(f"{n}（{st}）" for n, q, c, st in need),
               12, y, 18, tide.ALARM, width=W - 24) + 4
    y = s.para("ck", f"最近检查 {max(x[2] for x in data.SUPPLIES)} · 每周一仓管复检；"
                     "取用后在小程序「物资柜」登记。（虚构演示：柜号与数量均为示例）",
               12, y, 18, tide.INK_2, width=W - 24) + 6
    s.rect(12, y, W - 24, 40, "#FFFFFF", radius=6, border=f"1.5 SOLID {tide.INK}")
    s.rect(12, y, 92, 40, tide.SAND, radius=6)
    s.text("sl", "封条", 58, y + 11, 20, tide.INK, align="center", bold=True)
    seal = "开封人：＿＿＿＿ 时间：＿＿＿＿ 编号：TL-03-＿＿"
    s.text("sg", seal, 116, y + 11, 18, tide.INK_2)
    assert tw(seal, 18) <= W - 24 - 116 - 8, tw(seal, 18)
    assert y + 19 <= H - 8, y
    return s, {"items": [list(x) for x in data.SUPPLIES],
               "attention": [[n, st] for n, q, c, st in need],
               "last_check": max(x[2] for x in data.SUPPLIES),
               "print_size_mm": [round(W / MM_PX), round(H / MM_PX)],
               "min_font_px": 18, "min_font_mm": round(18 / MM_PX, 2)}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case08.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case08-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=8), ensure_ascii=False))
