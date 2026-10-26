# -*- coding: utf-8 -*-
"""A12 probe: measure text widths for mobile fit."""
import os
import sys
from pathlib import Path

os.environ["SNAPSHOT_TASK_ROOT"] = "."
os.environ["SNAPSHOT_RUN_ID"] = "run-20261013-174209"
sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import textmeasure as TM  # noqa: E402

texts = [
    ("Structure / Vision", 40, "BOLD"),
    ("Structure / Vision", 34, "BOLD"),
    ("Structure / Vision", 30, "BOLD"),
    ("让模型从读懂文档到完成作品", 20, "NORMAL"),
    ("免费参加 · 扫码方式详见官网", 18, "BOLD"),
    ("免费参加 · 扫码方式详见官网", 16, "BOLD"),
    ("structure.example.org", 16, "NORMAL"),
    ("structure.example.org", 14, "NORMAL"),
    ("云构中心 · ONLINE", 16, "NORMAL"),
    ("09:00–16:00", 16, "NORMAL"),
    ("2026.11.07", 16, "NORMAL"),
]
for t, size, style in texts:
    r = TM.measure(t, size, "Noto Sans CJK SC", style)
    print(f"{t!r} @{size}px {style}: {r['width']}px")
print()
print("mobile available hero width:", 360 - 16 * 2 - 20 * 2)
print("mobile card width:", (360 - 16 * 2 - 0) )
print("tablet available:", 768 - 64)
print("desktop available:", 1440 - 64)
print("stage available:", 1920 - 64)
