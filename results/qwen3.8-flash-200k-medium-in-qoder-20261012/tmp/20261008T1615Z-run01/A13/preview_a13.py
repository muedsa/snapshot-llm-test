"""A13 preview emitter: the two alternative icon directions, each at 512 and at 32.

The 512 canvases are the real previews TASK.md asks for. The 32 canvases are rendered from
the *same* ratios rather than downscaled, so they test whether the geometry survives at the
small size instead of only testing the raster.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "A13"))
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
import plan_a13 as P  # noqa: E402

PREVIEW = ROOT / "tmp" / RID / "A13" / "preview"
PREVIEW.mkdir(parents=True, exist_ok=True)


def mark(direction, size, variant="color"):
    doc = P.Doc(size, size, bg="transparent", font=P.FONT)
    S = size / (1 + 2 * P.CLEAR_SPACE)      # mark box leaves the clear space at every size
    P.icon(doc, size / 2, size / 2, S, direction, variant)
    return doc.dsl()


out = {}
for d in ("A", "B"):
    for size, tag in ((512, "alt"), (32, "thumb")):
        name = f"{tag}-{d}-{size}"
        (PREVIEW / f"{name}.snapshot").write_text(mark(d, size), encoding="utf-8")
        out[name] = len(mark(d, size))
print(json.dumps(out))
