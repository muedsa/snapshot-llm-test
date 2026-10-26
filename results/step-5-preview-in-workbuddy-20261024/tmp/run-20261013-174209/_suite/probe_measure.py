"""探针：确认文本测量工具与 CJK 数字混排宽度。"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "_suite"))
import textmeasure as TM  # noqa: E402

for t in ["918,624 元", "11.15%", "2026-09", "A", "万元", "0", "12,345,678", "净收入"]:
    for style in ["NORMAL", "BOLD"]:
        r = TM.measure(t, 20, "Noto Sans CJK SC", style)
        print(f"{t!r:20} {style:6} -> {r['width']}x{r['height']}")
r = TM.measure("Mono 918,624", 20, "Noto Sans Mono CJK SC")
print("mono ->", r["width"], r["height"])
r = TM.measure("Inter 918,624", 20, "Inter")
print("inter ->", r["width"], r["height"])
