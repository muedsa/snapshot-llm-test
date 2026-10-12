"""Probe: how does a rotated Container inside Positioned actually paint?

Three variants of the same segment (box 40,160) -> (160,40) in a 200x200 canvas, so the
ink geometry tells which alignment Transform uses. Answers the question before A05 draws
~30 data-polyline segments.
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, n  # noqa: E402

import math

d = Doc(660, 220, bg="#0B1220")
dx1, dy1, dx2, dy2 = 40.0, 180.0, 160.0, 40.0
ln = math.hypot(dx2 - dx1, dy2 - dy1)
co, si = (dx2 - dx1) / ln, (dy2 - dy1) / ln
ang = math.atan2(dy2 - dy1, dx2 - dx1)
mat = f"({co:.6f},{si:.6f},0,0,{-si:.6f},{co:.6f},0,0,0,0,1,0,0,0,0,1)"

panels = []
for i, (label_, inner) in enumerate([
    ("A: Transform default alignment",
     f'<Transform matrix="{mat}">' + d.box(ln, 4, color="#38BDF8") + "</Transform>"),
    ("B: alignment TOP_LEFT",
     f'<Transform matrix="{mat}" alignment="TOP_LEFT">' + d.box(ln, 4, color="#34D399")
     + "</Transform>"),
    ("C: alignment CENTER",
     f'<Transform matrix="{mat}" alignment="CENTER">' + d.box(ln, 4, color="#FBBF24")
     + "</Transform>"),
]):
    ox = i * 220
    panels.append(d.box(200, 200, color="#131D31", radius=8, border="1 SOLID #2B3C5C",
                        align="TOP_CENTER", inner=d.text(label_, "#94A3B8", 18)))
    panels.append(f'<Positioned left="{n(ox + 10)}" top="10" width="200" height="200">'
                  f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                  f'<Positioned left="{n(dx1)}" top="{n(dy1 - 2)}" width="{n(ln)}" height="4">'
                  f'{inner}</Positioned></Stack></Positioned>')
    # reference dots at the two endpoints
    panels.append(f'<Positioned left="{n(ox + 10 + dx1 - 3)}" top="{n(dy1 - 3)}" '
                  f'width="6" height="6">{d.box(6, 6, color="#F1F5F9", radius=3)}</Positioned>')
    panels.append(f'<Positioned left="{n(ox + 10 + dx2 - 3)}" top="{n(dy2 - 3)}" '
                  f'width="6" height="6">{d.box(6, 6, color="#F1F5F9", radius=3)}</Positioned>')

dsl = (f'<Snapshot background="#0B1220" type="png">'
       f'<Container width="660" height="220" color="#0B1220">'
       f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + "".join(panels) +
       "</Stack></Container></Snapshot>")
out = ROOT / "tmp" / RID / "A05" / "probe"
out.mkdir(parents=True, exist_ok=True)
(out / "diagonal.snapshot").write_text(dsl, encoding="utf-8")
print("wrote", out / "diagonal.snapshot", len(dsl), "chars; ln =", round(ln, 3))
