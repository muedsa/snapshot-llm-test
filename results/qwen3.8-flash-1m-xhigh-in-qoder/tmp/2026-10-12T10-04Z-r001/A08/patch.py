"""A08 fixes: legible wall cells and full grid, taller bottom route cards with a
tightened sidebar, and a corrected shared-corridor computation."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A08/gen.py")
s = p.read_text(encoding="utf-8")

rep = [
    # ---- shared corridor runs were built with leaked loop variables
    ('''shared = [c for c in R1 if c in s2]
# split the shared cells into maximal runs along R1
runs, cur = [], []
for c in R1:
    if c in s2:
        cur.append(c)
    else:
        if len(cur) >= 2:
            runs.append(cur)
        cur = []
if len(cur) >= 2:
    runs.append(cur)
shared_runs = []
for run in runs:
    idx2 = [R2.index(c) for c in run if c in set(R2)]
    same_dir = len(idx2) > 1 and idx2 == sorted(idx2)
    shared_runs.append({
        "cells": [[x, y] for x, y in run if x in s2 and (x, y) in s2],
        "cell_count": len([c for c in run if c in s2]),
        "in_R1_direction": " → ".join(f"{c[0]},{c[1]}" for c in run),
        "in_R2_direction": " → ".join(
            f"{c[0]},{c[1]}" for c in [x for x in R2 if x in set(run)]),
        "same_travel_direction": same_dir,
    })''',
     '''shared_cells = [c for c in R1 if c in s2]
# split the shared cells into maximal runs along R1
runs, cur = [], []
for c in R1:
    if c in s2:
        cur.append(c)
    else:
        if len(cur) >= 2:
            runs.append(cur)
        cur = []
if len(cur) >= 2:
    runs.append(cur)
shared_runs = []
for run in runs:
    runset = set(run)
    order_in_r2 = [c for c in R2 if c in runset]
    idx2 = [R2.index(c) for c in run]
    shared_runs.append({
        "cells": [[x, y] for x, y in run],
        "cell_count": len(run),
        "steps_shared": len(run) - 1,
        "metres_shared": (len(run) - 1) * CELL_M,
        "in_R1_direction": " -> ".join(f"({c[0]},{c[1]})" for c in run),
        "in_R2_direction": " -> ".join(f"({c[0]},{c[1]})" for c in order_in_r2),
        "same_travel_direction": idx2 == sorted(idx2),
        "drawn_as": "R1 宽实线底 + R2 窄虚线叠于同一中心线，两条线各自可追踪",
    })'''),
    # ---- walls must be visible against the background
    ('WALL = "#0B1120"', 'WALL = "#141C2E"'),
    ('BG = "#0A101E"', 'BG = "#080D18"'),
    ('''        els.append(Positioned(C(width=num(CELL - 1), height=num(CELL - 1), color=fill),
                              left=num(OX + x * CELL), top=num(OY + y * CELL)))''',
     '''        els.append(Positioned(
            C(width=num(CELL - 1), height=num(CELL - 1), color=fill,
              border="1 SOLID #0A1220" if ch != "#" else "1 SOLID #1D2739"),
            left=num(OX + x * CELL), top=num(OY + y * CELL)))'''),
    # ---- drop the duplicate bottom axis caption that collided with the cards
    ('''els.append(label(OX + MAP_W / 2, OY + MAP_H + 36, "格坐标 x", 16, TXT_3, anchor="top",
                 align="CENTER", width=120, font=FONT))''', ''),
    # ---- bottom cards: taller, no overflow, caption moved clear below
    ("BY = OY + MAP_H + 66", "BY = 812"),
    ('''    els.append(card(x, BY, BW, 118, fill="#0E1830", radius=12))
    els.append(Positioned(C(width=num(BW - 2), height="4", color=col, borderRadius="2"),
                          left=num(x + 1), top=num(BY + 1)))''',
     '''    els.append(card(x, BY, BW, 150, fill="#0E1830", radius=12))
    els.append(Positioned(C(width=num(BW - 2), height="4", color=col, borderRadius="2"),
                          left=num(x + 1), top=num(BY + 1)))'''),
    ('''            Text(f"步数 {steps} 步　·　距离 {steps * CELL_M} 米　·　经过 {len(path)} 个格心",
                 color=col, fontSize="22", fontFamily=FONT, bold=True),
            Container(height="4"),
            Text("共享通道同样计入本路线的步数与米数。", color=TXT_3, fontSize="18",
                 fontFamily=FONT),''',
     '''            Text(f"步数 {steps} 步　·　距离 {steps * CELL_M} 米", color=col,
                 fontSize="22", fontFamily=FONT, bold=True),
            Container(height="6"),
            Text(f"经过 {len(path)} 个格心（步数 = 格心数 − 1）；共享通道的路程同样计入本路线。",
                 color=TXT_3, fontSize="18", fontFamily=FONT),'''),
    ('''els.append(label(OX, BY + 130,
                 f"S 入口 ({LM['S'][0]},{LM['S'][1]}) 起 · E 出口 ({LM['E'][0]},{LM['E'][1]}) 终；"
                 "只计格心之间的步，不计图外路程与参观停留。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=MAP_W, font=FONT))''',
     '''els.append(label(OX, BY + 164,
                 f"S 入口 ({LM['S'][0]},{LM['S'][1]}) 起 · E 出口 ({LM['E'][0]},{LM['E'][1]}) 终 · "
                 f"每格边长 {CELL_M} 米 · 只计格心之间的步，不计图外路程与参观停留 · "
                 "入馆段与离馆段为两条路线的共享通道",
                 18, TXT_3, anchor="left_top", align="LEFT", width=MAP_W, font=FONT))'''),
    # ---- sidebar: drop the long paragraph that overflowed the card
    ('''sy += 30
els.append(Positioned(
    Container(Text("共享通道上，R1 画成宽实线底、R2 画成窄虚线叠在其上，"
                   "两条线在入馆段与离馆段都能各自从 S 追到 E。",
                   color="#BFD6EE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(SW - 60)),
    left=num(SX + 20), top=num(sy)))''',
     '''sy += 30
els.append(Positioned(
    Container(Text("共享通道：R1 宽实线为底、R2 窄虚线叠在其上，两段均可各自从 S 追到 E。",
                   color="#BFD6EE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(SW - 56)),
    left=num(SX + 20), top=num(sy)))'''),
    ('''els.append(label(SX + 20, sy, "▶ ▼ ◀ ▲ 行进方向（每条线自己的颜色）", 18, TXT_2,
                 anchor="left_top", align="LEFT", width=SW - 40, font=FONT))
sy += 26''',
     '''els.append(label(SX + 20, sy, "▶▼◀▲ 行进方向", 18, TXT_2, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT))
sy += 26'''),
    ('''els.append(label(SX + 20, sy, "墙体 / 非通行区", 18, TXT_2, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT))
els.append(Positioned(C(width="18", height="18", color=WALL,
                        border="1 SOLID #33486F"), left=num(SX + 178), top=num(sy - 2)))''',
     '''els.append(label(SX + 20, sy, "墙体 / 非通行区", 18, TXT_2, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT))
els.append(Positioned(C(width="18", height="18", color=WALL,
                        border="1 SOLID #3A4A66"), left=num(SX + 178), top=num(sy - 2)))'''),
    ('''        "lateral_offset_px": 0,''', '''        "lateral_offset_px": 0,'''),
]

for a, b in rep:
    if a not in s:
        raise SystemExit("MISS: " + a[:90])
    s = s.replace(a, b)

p.write_text(s, encoding="utf-8")
print("patched", len(rep), "sites")
