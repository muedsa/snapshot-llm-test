#!/usr/bin/env python
# 一次性补丁：把 case09 的路径带与港口行下移，避开 KPI 卡。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c9.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
subs = [
    ("r * 1.15)", "r * 1.00)"),
    ("(12, 444, ", "(12, 448, "), ("(24, 436, ", "(24, 444, "),
    ("(36, 430, ", "(36, 441, "), ("(48, 426, ", "(48, 438, "),
    ("(60, 434, ", "(60, 443, "), ("(72, 446, ", "(72, 449, "),
    ("rect(hx(hr), 300, 1, 250,", "rect(hx(hr), 336, 1, 206,"),
    ("hx(hr) - 40, 272, 80, None, 19, DIM,", "hx(hr) - 40, 548, 80, None, 19, DIM,"),
    ("PY, PITCH = 566, 44", "PY, PITCH = 600, 42"),
    ("footer(b, 72, H - 46, W - 144,", "footer(b, 72, H - 40, W - 144,"),
]
missing = []
for a, b in subs:
    if a not in s:
        missing.append(a)
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs))
if missing:
    print("MISSING:", missing)