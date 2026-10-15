#!/usr/bin/env python
"""A17 印刷可行性探针：单引号属性值 + CDATA（含 `]]>`）能否原样渲染代码行。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
D = BASE / "tmp/run-20261011-01/A17/drafts"
RENDER = "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"

CASES = {
    # 单引号属性值：内容含 " 与 &
    "p-f-single-quote": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="20" top="30" width="360" height="30">
<Text fontSize="16" color="#0F172A" fontFamily="DejaVu Sans Mono" text='<Positioned left="24" top="22"/>'/>
</Positioned>
<Positioned left="20" top="70" width="360" height="30">
<Text fontSize="16" color="#0F172A" fontFamily="DejaVu Sans Mono" text='A &amp; B &lt; C &gt; D'/>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # 单引号属性值 + 裸 & 与 <（不做实体转义）
    "p-g-single-quote-bare": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="20" top="30" width="360" height="30">
<Text fontSize="16" color="#0F172A" fontFamily="DejaVu Sans Mono" text='A < B & C > D'/>
</Positioned>
<Positioned left="20" top="70" width="360" height="30">
<Text fontSize="16" color="#0F172A" fontFamily="DejaVu Sans Mono" text='<Raw><![CDATA[x]]></Raw>'/>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # 负例：CDATA 内容里出现 `]]>` 应报错（确认这条边界）
    "p-h-cdata-early-close": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="20" top="30" width="360" height="30">
<Text fontSize="16" color="#0F172A" text='<Raw><![CDATA[a]]>b]]></Raw>'/>
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
            [sys.executable, RENDER, "--task", "A17", "--version", name,
             "--dsl", p.as_posix(),
             "--out", f"tmp/run-20261011-01/A17/preview/{name}.png",
             "--log", "tmp/run-20261011-01/A17/requests.jsonl",
             "--responses-dir", "tmp/run-20261011-01/A17/responses"],
            capture_output=True, text=True, encoding="utf-8")
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
        ok = '"ok": true' in last
        print(f"[{name}] ok={ok} {'' if ok else last[:220]}")


if __name__ == "__main__":
    main()