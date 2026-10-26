#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 能力探针：一次渲染确认 4 项本题必需能力。

1) Snapshot 默认 background="transparent" 是否产出真实透明 PNG（角落 alpha=0）
2) 8 位十六进制 #RRGGBBAA 是否按 CSS 语义（alpha 在最后两位）生效
3) Container shape="CIRCLE"
4) Transform matrix + alignment="CENTER" 绕自身中心旋转
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))
from render import Log, render, suite_root, rel  # noqa: E402

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A23"
TMP.mkdir(parents=True, exist_ok=True)

import math

DSL = """<Snapshot type="png">
<Container width="240" height="240">
<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">
<Positioned left="20" top="20" width="120" height="40">
<Transform matrix="(0.8660254037844387,0.5000000000000001,0,0,-0.4999999999999999,0.8660254037844387,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">
<Container width="120" height="40" color="#FF000080" borderRadius="8"/>
</Transform></Positioned>
<Positioned left="120" top="90" width="80" height="80">
<Container width="80" height="80" color="#00FF00FF" shape="CIRCLE"/>
</Positioned>
<Positioned left="20" top="150" width="60" height="60">
<Transform matrix="(0.7071067811865476,0.7071067811865475,0,0,-0.7071067811865475,0.7071067811865476,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">
<Container width="60" height="60" color="#0000FFFF" borderRadius="6"/>
</Transform></Positioned>
</Stack>
</Container>
</Snapshot>
"""

if __name__ == "__main__":
    p = TMP / "probe-cap.snapshot"
    p.write_text(DSL, encoding="utf-8")
    log = Log(ROOT, RUN_ID, "A23")
    r = render(p, TMP / "probe-cap.png", ROOT, log, label="A23-probe-capability")
    rec = r["record"]
    print(json.dumps if False else "")
    print(f"status={rec['status']} http={rec['http_status']} ct={rec['content_type']} "
          f"req={rec['request_id']} elapsed={rec['elapsed_s']}s err={rec['error']}")
