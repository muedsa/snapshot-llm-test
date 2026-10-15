#!/usr/bin/env python
"""A18 探针二：Path 多边形节点 vs 嵌套圆角方块「芯片」节点。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
D = BASE / "tmp/run-20261011-01/A18/drafts"
R = "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"

CASES = {
    "p-d-path": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="60" top="40" width="120" height="120">
<Path d="M60,4 L116,32 L116,88 L60,116 L4,88 L4,32 Z" fill="#1D4ED8"/>
</Positioned>
<Positioned left="220" top="40" width="120" height="120">
<Polygon points="60,4 116,32 116,88 60,116 4,88 4,32" fill="#EA7C2D"/>
</Positioned>
<Positioned left="40" top="190" width="320" height="30">
<Text fontSize="16" color="#0F172A" fontFamily="Inter" text="Path / Polygon hexagon"/>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    "p-e-chip": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="40" top="40" width="96" height="96">
<Container width="96" height="96" color="#1D3ED8" borderRadius="22"/>
</Positioned>
<Positioned left="58" top="58" width="60" height="60">
<Container width="60" height="60" color="#0B1736" borderRadius="14" border="3 SOLID #7DA7F5"/>
</Container>
<Positioned left="220" top="46" width="112" height="72">
<Container width="112" height="72" color="#1D3ED8" borderRadius="20"/>
</Positioned>
<Positioned left="242" top="61" width="68" height="42">
<Container width="68" height="42" color="#0B1736" borderRadius="12" border="3 SOLID #7DA7F5"/>
</Positioned>
<Positioned left="40" top="190" width="320" height="30">
<Text fontSize="16" color="#0F172A" fontFamily="Inter" text="nested rounded-square chip"/>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
}


def main() -> None:
    D.mkdir(parents=True, exist_ok=True)
    for name, dsl in CASES.items():
        p = D / f"{name}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, R, "--task", "A18", "--version", name, "--dsl", p.as_posix(),
             "--out", f"tmp/run-20261011-01/A18/preview/{name}.png",
             "--log", "tmp/run-20261011-01/A18/requests.jsonl",
             "--responses-dir", "tmp/run-20261011-01/A18/responses"],
            capture_output=True, text=True, encoding="utf-8")
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
        ok = '"ok": true' in last
        print(f"[{name}] ok={ok} {'' if ok else last[:200]}")


if __name__ == "__main__":
    main()