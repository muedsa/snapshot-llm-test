"""Measure the advance width of the mono body font at 20px, and the line pitch.

Two rows of the same 60-character string, printed at a known left edge and known
tops, let us read both the per-character advance (ink extent / 60) and the real
line pitch from the served PNG.
"""
import sys
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_DIR / "_suite" / "scripts"))

from snap import C, Container, Positioned, Snapshot, Stack, Text, num  # noqa: E402

S = "0123456789abcdefghijklmnopqrstuvwx" * 2 + "AB"
MONO = "Noto Sans Mono CJK SC"

doc = Snapshot(
    Stack(C(width="700", height="200", color="#FFFFFF"),
          Positioned(Text(S, fontSize="20", color="#000000", fontFamily=MONO),
                     left="20", top="20"),
          Positioned(Text(S, fontSize="20", color="#000000", fontFamily=MONO),
                     left="20", top="120"),
          alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
    background="#FFFFFF", type="png")

out = RUN_DIR / "A17" / "probe-mono.snapshot"
out.write_text(doc.render() + "\n", encoding="utf-8")
print(f"chars={len(S)} written {out.relative_to(RUN_DIR.parent.parent)}")
