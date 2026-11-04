# -*- coding: utf-8 -*-
"""A07 travel card v2 (720x1280) built from routes.json."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402

TASK = "A07"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
routes = json.loads((OUT / "routes.json").read_text(encoding="utf-8"))

BG = "#0B1220"
CARD = "#111C2E"
INK = "#EAF1FB"
INK2 = "#A7B6CC"
MUTED = "#6E8098"
LINE_C = "#22314A"
LC = {"R": "#F43F5E", "B": "#3B82F6", "G": "#10B981"}
LN = {"R": "红线", "B": "蓝线", "G": "绿线"}
OK = "#34D399"
BAD = "#FB7185"

W, H = 720, 1280
p: list[str] = []
p.append(K.rect(0, 0, W, 5, color="#F43F5E"))
p.append(K.text(32, 20, "旅行卡 · 三条旅程", size=30, color=INK, bold=True))
p.append(K.text(32, 60, "按“先最少站间边数、再最少换乘”求解；换乘 = 改变线路，首次上车不计。",
                width=656, size=18, color=INK2))
p.append(K.text(32, 86, "无障碍约束：起终点与换乘站必须有设施；可乘车通过无设施车站。",
                width=656, size=18, color=INK2))
p.append(K.rect(32, 118, W - 64, 1, color=LINE_C))

def chip(x, y, label, color, w=64, h=26, fg="#08101C", size=18):
    p.append(K.rect(x, y, w, h, color=color, radius=7))
    p.append(K.text(x, y + 3, label, width=w, size=size, color=fg, bold=True, align="CENTER"))

def draw_card(x, y, w, h, accent):
    p.append(K.rect(x, y, w, h, color=CARD, radius=16, border="1 SOLID #1E2C42"))
    p.append(K.rect(x, y, 4, h, color=accent, radius=2))

cursor = 138.0
for i, r in enumerate(routes["queries"], start=1):
    plain = r["plain"]
    alt = r.get("alternative")
    x = 32
    height = 218 if alt else 226
    accent = LC[plain["segments"][0]["line"]]
    draw_card(x, cursor, W - 64, height, accent)
    chip(x + 20, cursor + 16, f"旅程 {i}", "#1E2C42", w=82, fg=INK2, size=17)
    p.append(K.text(x + 116, cursor + 12, f"{r['from_name']} → {r['to_name']}", size=26,
                    color=INK, bold=True))
    sx = x + 20
    for seg in plain["segments"]:
        lid = seg["line"]
        chip(sx, cursor + 52, lid, LC[lid], w=34, h=26)
        p.append(K.text(sx + 38, cursor + 56, f"{LN[lid]} · {seg['stops']} 段", size=18, color=INK2))
        sx += 172
    p.append(K.text(x + 20, cursor + 88, " → ".join(plain["stations"]), width=W - 104, size=20,
                    color=INK2))
    tr = ("无换乘" if plain["transfers"] == 0
          else f"{plain['transfers']} 次换乘 · 换乘站 {'、'.join(plain['transfer_stations'])}")
    p.append(K.text(x + 20, cursor + 122, f"{plain['edges']} 段站间 · {tr}", width=W - 104, size=20,
                    color=INK, bold=True))
    if plain["accessible_ok"]:
        p.append(K.rect(x + 20, cursor + 156, 246, 30, color="#052E22", radius=8,
                        border=f"1 SOLID {OK}55"))
        p.append(K.text(x + 30, cursor + 159, "✓ 可作无障碍旅程", width=226, size=20, color=OK,
                        bold=True))
        p.append(K.text(x + 282, cursor + 162, "起终点与换乘站均有设施", width=W - 340, size=18,
                        color=MUTED))
    else:
        p.append(K.rect(x + 20, cursor + 156, 258, 30, color="#3B1220", radius=8,
                        border=f"1 SOLID {BAD}55"))
        p.append(K.text(x + 30, cursor + 159, "✕ 不可作无障碍旅程", width=238, size=20, color=BAD,
                        bold=True))
        p.append(K.text(x + 20, cursor + 192,
                        f"换乘站 {'、'.join(plain['blocking_stations'])} 无设施：可乘车通过，但不能在此换乘。",
                        width=W - 100, size=18, color=INK2))
        if alt:
            p.append(K.rect(x + 16, cursor + 224, W - 96, 1, color=LINE_C))
            p.append(K.text(x + 20, cursor + 234, "无障碍替代路线", size=19, color=OK, bold=True))
            ax = x + 210
            for seg in alt["segments"]:
                lid = seg["line"]
                chip(ax, cursor + 230, lid, LC[lid], w=30, h=24)
                p.append(K.text(ax + 34, cursor + 234, f"{seg['stops']} 段", size=17, color=INK2))
                ax += 104
            p.append(K.text(x + 20, cursor + 264, " → ".join(alt["stations"]), width=W - 104,
                            size=20, color=INK2))
            p.append(K.text(x + 20, cursor + 298,
                            f"{alt['edges']} 段站间 · {alt['transfers']} 次换乘 · "
                            f"换乘站 {'、'.join(alt['transfer_stations'])}", width=W - 104, size=20,
                            color=OK, bold=True))
            height = 344
    cursor += height + 16

# summary
sy = cursor
p.append(K.rect(32, sy, W - 64, 176, color="#0E1A2A", radius=14, border="1 SOLID #22314A"))
p.append(K.text(52, sy + 14, "判定小结", size=20, color=INK, bold=True))
rows = [
    ("旅程 1", "6 段 · 1 换乘（中心有设施）→ 满足"),
    ("旅程 2", "东桥无设施 → 不满足；改用 2 次换乘替代"),
    ("旅程 3", "4 段 · 1 换乘（工坊有设施）→ 满足"),
]
for i, (tag, text) in enumerate(rows):
    y = sy + 46 + i * 42
    p.append(K.text(52, y, tag, size=18, color=MUTED, bold=True))
    p.append(K.text(124, y, text, width=W - 160, size=20, color=INK2))

p.append(K.rect(32, 1210, W - 64, 1, color=LINE_C))
p.append(K.text(32, 1222, "16 站 · 17 段相邻区间 · 换乘站：中心（R↔B）、东桥（R↔G）、工坊（B↔G）。",
                width=W - 64, size=17, color=MUTED))
p.append(K.text(32, 1248, "完整站序、线段与判定证据见 routes.json。", width=W - 64, size=17, color=MUTED))

dsl = K.document(W, H, p, background=BG)
path = OUT / "travel-card.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "travel-card.png", "travel card v2: summary block")
print("card:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for x in warn:
    print(x)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "travel-card.png"))
