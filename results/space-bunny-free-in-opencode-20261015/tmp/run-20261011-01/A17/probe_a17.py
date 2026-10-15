#!/usr/bin/env python
"""A17 能力探针：确认四页示例要用到的构造在服务端真实可用。

逐个独立 DSL，一个失败不影响其它；失败的响应体保留在 responses/ 里。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
D = BASE / "tmp/run-20261011-01/A17/drafts"
RENDER = "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"

CASES = {
    # A: Container 无子节点 + Stack 混合子节点（示例 1 的骨架）
    "p-a-container-empty": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="24" top="24" width="352" height="192">
<Container width="352" height="192" color="#FFFFFF" borderRadius="12"/>
</Positioned>
<Positioned left="40" top="44" width="240" height="24">
<Text fontSize="17" color="#0F172A" text="请求：POST /render"/>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # B: Row + Expanded + Spacer（示例 2 的有界 Flex）
    "p-b-row-expanded": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Column mainAxisAlignment="CENTER" crossAxisAlignment="CENTER">
<Container width="360" height="72">
<Row mainAxisAlignment="START" crossAxisAlignment="CENTER">
<Expanded flex="2">
<Container width="360" height="72" color="#1D4ED8" borderRadius="10"/>
</Expanded>
<Expanded flex="1">
<Container width="360" height="72" color="#93C5FD" borderRadius="10"/>
</Expanded>
</Row>
</Container>
<Spacer/>
</Column>
</Container>
</Snapshot>
''',
    # C: Raw + CDATA + 嵌套 Text 富文本（示例 3）
    "p-c-raw-cdata": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="20" top="30" width="360" height="34">
<Text fontSize="20" color="#0F172A" fontFamily="Inter Semi Bold">
<Text color="#15803D">PAID</Text><Raw> </Raw><Text color="#94A3B8">/</Text><Raw> </Raw><Text color="#0F172A">已结算</Text>
</Text>
</Positioned>
<Positioned left="20" top="90" width="360" height="34">
<Text fontSize="20" color="#0F172A"><Raw><![CDATA[A < B & C > D]]></Raw></Text>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # D: ColorFiltered / ImageFiltered / BackdropFilter + ClipRRect（示例 4）
    "p-d-filters": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="20" top="24" width="120" height="120">
<ColorFiltered color="#1D4ED8" blendMode="MULTIPLY">
<Container width="120" height="120" color="#F97316" borderRadius="16"/>
</ColorFiltered>
</Positioned>
<Positioned left="160" top="24" width="120" height="120">
<ImageFiltered sigmaX="4" sigmaY="4" tileMode="CLAMP">
<Container width="120" height="120" color="#22C55E" borderRadius="16"/>
</ImageFiltered>
</Positioned>
<Positioned left="300" top="24" width="80" height="120">
<ClipRRect borderRadius="16" clipBehavior="ANTI_ALIAS">
<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP">
<Container width="80" height="120" color="#FFFFFF00"/>
</BackdropFilter>
</ClipRRect>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # E: Opacity 子树 vs 8 位尾部 alpha（#RRGGBBAA）
    "p-e-opacity-alpha": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
<Positioned left="20" top="30" width="120" height="120">
<Opacity opacity="0.35">
<Container width="120" height="120" color="#0F172A" borderRadius="16"/>
</Opacity>
</Positioned>
<Positioned left="160" top="30" width="120" height="120">
<Container width="120" height="120" color="#0F172A80" borderRadius="16"/>
</Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # E2: 负例——把 alpha 写成旧式 #AARRGGBB（#80 开头）应当报错或给出不同颜色
    "p-e2-wrong-alpha-order": '''<Snapshot type="png">
<Container width="400" height="240" color="#80F3F6FA">
<Stack fit="EXPAND">
<Positioned left="20" top="30" width="120" height="120">
<Container width="120" height="120" color="#800F172A" borderRadius="16"/>
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
        note = "" if ok else last[:230]
        print(f"[{name}] ok={ok} {note}")


if __name__ == "__main__":
    main()