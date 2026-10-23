"""从交付图中裁出局部放大图，用于目视复核文字与刻度（不修改交付 PNG）。

用 CROP_TAG 选择来源：final=最终交付图，v1-defect=修正前的留档副本。
输出目录随之区分，避免用旧图冒充最终图的查看证据。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PIL import Image

os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S           # noqa: E402

RID = S.run_id()
TAG = os.environ.get("CROP_TAG", "final")
SRC = (Path("outputs") / RID / "A09" / "transform-atlas.png" if TAG == "final"
       else Path("tmp") / RID / "A09" / "preview" / "atlas.v1-defect.png")
DST = Path("tmp") / RID / "A09" / "preview" / ("crops-final" if TAG == "final"
                                               else "crops-v1-defect")

CROPS = [
    ("note2-line", (30, 90, 920, 134), 2),
    ("note1-line", (30, 62, 920, 106), 2),
    ("label-T07-T08", (880, 484, 1452, 528), 2),
    ("label-T11-T12", (880, 766, 1452, 810), 2),
    ("legend-footer", (150, 1156, 1452, 1196), 2),
    ("stage-T11", (888, 828, 1044, 984), 3),
    ("stage-T10", (516, 838, 752, 976), 3),
    ("stage-T07-T08", (866, 520, 1400, 730), 2),
]


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    img = Image.open(SRC).convert("RGB")
    print("source", SRC, img.size)
    for name, box, scale in CROPS:
        c = img.crop(box)
        c = c.resize((c.width * scale, c.height * scale), Image.NEAREST)
        p = DST / (name + ".png")
        c.save(p)
        print("  ", name, box, "->", c.size, S.rel(p))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
