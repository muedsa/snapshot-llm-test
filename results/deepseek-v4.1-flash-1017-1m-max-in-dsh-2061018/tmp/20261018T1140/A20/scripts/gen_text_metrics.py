"""Render a measurement strip with the 24 label strings at 20px.

Output: tmp/<run>/A20/dsl/text-metrics-v001.snapshot
The strip is one label per 36px row; a PIL pass measures the actual ink
extents so label boxes can be sized from the real renderer, not guesses.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN / "A20"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import Pos, SizedBox, Stack, T  # noqa: E402

FONT = "Inter,Noto Sans CJK SC"


def main() -> int:
    markers = json.loads(
        (ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json").read_text(encoding="utf-8"))
    W, ROWh = 900, 40
    H = ROWh * len(markers) + 20
    nodes = [SizedBox(W, H),
             Pos(0, 0, f'<Container width="{W}" height="{H}" color="#FFFFFF"/>')]
    for i, m in enumerate(markers):
        text = f'{m["id"]} {m["name"]} {m["value"]}'
        nodes.append(Pos(20, 10 + i * ROWh, T(text, size=20, color="#000000", family=FONT)))
    dsl = f'<Snapshot type="png" background="#FFFFFF">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    out = TMP / "dsl" / f"text-metrics-{sys.argv[1] if len(sys.argv) > 1 else 'v001'}.snapshot"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dsl, encoding="utf-8")
    (TMP / "text-metrics.json").write_text(json.dumps(
        {"canvas": [W, H], "row_height": ROWh, "font": FONT, "size": 20,
         "strings": [f'{m["id"]} {m["name"]} {m["value"]}' for m in markers]},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
