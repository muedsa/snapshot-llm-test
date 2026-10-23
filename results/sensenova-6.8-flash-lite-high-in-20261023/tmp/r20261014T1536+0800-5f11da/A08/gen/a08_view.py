"""把 model.json 的路线叠加回网格打印出来，供人工核对路径走向。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A08/gen/a08_view.py [R1|R2|both]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TASK = "A08"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    rid = os.environ["SNAPSHOT_RUN_ID"]
    m = json.loads(Path(f"tmp/{rid}/{TASK}/model.json").read_text(encoding="utf-8"))
    grid_path = Path(m["grid"]["source"])
    grid = [list(r) for r in grid_path.read_text(encoding="utf-8").splitlines()]
    W, H = m["grid"]["width"], m["grid"]["height"]
    which = sys.argv[1] if len(sys.argv) > 1 else "both"

    marks = {k: tuple(v) for k, v in m["marks"].items()}
    sets = {r["id"]: set(tuple(c) for c in r["cells"])
            for r in m["routes"].values()}
    shared = set(tuple(c) for c in m["shared_cells"])

    # 每格到起点的行进序号，用于标注方向
    order = {}
    for r in m["routes"].values():
        for i, c in enumerate(r["cells"]):
            order.setdefault(r["id"], {})[tuple(c)] = i

    for y in range(H):
        row = []
        for x in range(W):
            ch = grid[y][x]
            if ch == "#":
                row.append("▓")
                continue
            key = (x, y)
            r1, r2 = key in sets["R1"], key in sets["R2"]
            if r1 and r2:
                row.append("+" if which == "both" else
                           ("1" if which == "R1" else "2"))
            elif r1:
                row.append("1")
            elif r2:
                row.append("2")
            else:
                row.append(ch if ch in ".SEABCD" else "·")
        print(" ".join(row))
    print()

    for r in m["routes"].values():
        print(f"{r['id']} {r['name']}: 途经 {'→'.join(r['waypoints'])}"
              f"，格 {len(r['cells'])}，步 {r['step_count']}，米 {r['meters']}")
        for s in r["segments"]:
            print(f"   {s['from']}→{s['to']} {s['steps']} 步: "
                  f"{s['from_cell']}→{s['to_cell']}")
    print(f"\n共享 {len(shared)} 格，连续片段 {len(m['shared_corridors'])} 条")
    for i, c in enumerate(m["shared_corridors"], 1):
        print(f"   片段{i}: {c['length_steps']} 步（{len(c['cells'])} 格）"
              f" {c['cells'][0]}→{c['cells'][-1]}")
        print(f"        {c['cells']}")
    print("\n行进方向（每格在所属路线中的序号）：")
    for rid_, r in m["routes"].items():
        seq = []
        for i, c in enumerate(r["cells"]):
            x, y = c
            seq.append(f"{x},{y}#{i}")
        print(f"  {rid_}: " + " ".join(seq))
    return 0


if __name__ == "__main__":
    sys.exit(main())
