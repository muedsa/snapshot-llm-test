"""探针：在 fontSize=20 下实测等宽块字符的前进宽与墨迹宽。

case-07 的字符网格按 0.833em（=16.66px）定位每一段，但渲染出来的行右端比预期短，
说明真实前进宽不是 16.66px。这里排 3/12/40 个 █ 与 ▓▒░ 各一行，用像素测量反推
「墨迹宽」和「前进宽」，再决定网格步长。
"""
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, n                                    # noqa: E402

tmp = ROOT / "tmp" / RID / "B03" / "probe"
tmp.mkdir(parents=True, exist_ok=True)
MONO = "IBM Plex Mono,Courier New,monospace"
FS = 20.0
W, H = 1200, 460
ROWS = [("blk3", "█" * 3), ("blk12", "█" * 12), ("blk40", "█" * 40),
        ("shd40", "▓" * 40), ("lit40", "▒" * 40), ("bck40", "░" * 40),
        ("mix40", "█ ▓▒░" * 8), ("sp40", " " * 40)]
d = Doc(W, H, bg="#10161C", font="Inter,Noto Sans CJK SC")
d.rect(0, 0, W, H, "#10161C")
for i, (name, txt) in enumerate(ROWS):
    y = 30 + i * 52
    d.label(40, y, 70, 24, name, "#9AA5B1", size=14)
    d.pos(120, y, 1000, 28,
          f'<Text fontSize="{n(FS)}" color="#E0A526" fontFamily="{MONO}" '
          f'softWrap="false" height="1.0"><Raw>{txt}</Raw></Text>')
    d.line(120, y - 4, 120, y + 30, 1, "#C8552B")
ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
p = tmp / f"probe-adv-{ts}.snapshot"
p.write_text(d.dsl(), encoding="utf-8")
print(p.name, len(d.dsl()))
