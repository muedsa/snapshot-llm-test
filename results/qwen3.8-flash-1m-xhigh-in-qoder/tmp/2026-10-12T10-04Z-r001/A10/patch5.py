"""A10 patch 5: ③'s sharp text layer lost its area offset.

card_front() stopped adding CARD_X/CARD_Y in patch 4, so the SHARP column was emitted
at canvas (40, 86) instead of the card position in area ③.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
p = ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
old = '        *card_front(CARD_X, CARD_Y, "SHARP")[1:],'
assert s.count(old) == 1
p.write_text(s.replace(old, '        *card_front(ox + CARD_X, oy + CARD_Y, "SHARP")[1:],'),
             encoding="utf-8")
print("patched 5")
