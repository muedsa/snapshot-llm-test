"""Smoke-test the four bkit additions B03 relies on, before any artwork uses them."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, SANS, MONO, SERIF  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"

PALETTE = ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C",
           "#EF476F", "#FFD166", "#06D6A0", "#118AB2"]
s = Sheet(760, 560, bg="#101820")
s.rect(0, 0, 760, 560, "#101820")
for i in range(9):
    s.rect(20 + i * 82, 30, 62, 120, PALETTE[i], radius=6)
s.glass(20, 30, 700, 120, sigma=12, tint="#FFFFFF22", radius=18)
s.text("proof", "frosted band over nine bars", 30, 60, 30, "#FFFFFF")

s.rich("proof", [("Mixed ", {}), ("spans", {"colour": "#FFD166", "bold": True}),
                 ("  mono 0123", {"font": MONO, "size": 22}),
                 (" serif", {"font": SERIF, "size": 26})],
     20, 190, size=28, colour="#EAF2F8", shadow="3 3 2 #EF476F88")
s.rich("proof", [("letterSpacing tracking", {})], 20, 240, size=24, colour="#06D6A0",
       letterSpacing=6)
s.rich("proof", [("tabular", {}), ("  0123456789", {"font": MONO, "colour": "#FFD166"})],
     20, 285, size=24, colour="#EAF2F8", features="tnum")

s.shear(20, 340, 200, 60, "#EF476F", kx=0.3, radius=8)
s.shear(260, 340, 200, 60, "#FFD166", ky=0.25, radius=8)
s.shear(500, 340, 160, 60, "#06D6A0", deg=-18, radius=8)
s.text("proof", "shear kx / shear ky / rotate", 20, 420, 20, "#9FB1BF")

s.filter_rect(20, 460, 220, 60, "#FFFFFF", tintColor="#118AB2", blend="MULTIPLY",
              radius=8)
s.filter_rect(260, 460, 220, 60, "#FFFFFF", sigma=6, radius=8)
s.text("proof", "ColorFiltered MULTIPLY / ImageFiltered", 20, 530, 18, "#9FB1BF")

TMP.joinpath("kit-proof.snapshot").write_text(s.dsl() + "\n", encoding="utf-8")
print("audit:", s.audit())
print("items", len(s.items), "shapes", s.shapes)
