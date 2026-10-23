"""A17 语法探针 7：钉死「Column 子节点之后的兄弟不渲染」的触发条件与修法。

探针 6 的结果：
  V1/V2/V3  Column 直接子节点是 Row     -> Row 与其后的兄弟都不渲染
  V4        Column 直接子节点是 Stack   -> Stack 渲染，但其后的兄弟不渲染
  CORE3     Row 包在显式尺寸 Container 里 -> 三块全部渲染（已实测）
这里并排 8 组，全部 Column width=140 height=200 crossAxisAlignment=STRETCH，
每组的第 2 个位置放不同构件，观察第 2、3 个位置是否渲染：
  A [C, C, C]              基线
  B [C, C, Stack]          Stack 作为最后一个子节点
  C [C, Stack, C]          复现 V4
  D [C, Row, C]            复现 V1
  E [C, C, Row]            Row 作为最后一个子节点
  F [C, Container{Stack}, C]  外层包装 Stack 是否修复
  G [C, Container{Row}, C]    外层包装 Row 是否修复（CORE3 形态）
  H [Stack, C, C]          Stack 作为第一个子节点
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP_DIR = SUITE_ROOT / "tmp" / RUN_ID / "A17"

C_DARK = '<Container width="140" height="40" color="#0F172A" borderRadius="6"/>'
C_GRAY = '<Container width="140" height="40" color="#F1F5F9" borderRadius="6"/>'
STACK = ('<Stack width="140" height="46" fit="EXPAND">\n'
         '    <Container width="140" height="46" color="#0EA5E9" borderRadius="6"/>\n'
         '</Stack>')
ROW = ('<Row width="140" height="46" crossAxisAlignment="STRETCH">\n'
       '    <Expanded><Container color="#0EA5E9" borderRadius="6"/></Expanded>\n'
       '    <SizedBox width="8"/>\n'
       '    <Expanded><Container color="#6366F1" borderRadius="6"/></Expanded>\n'
       '</Row>')
STACK_W = ('<Container width="140" height="46">\n    %s\n</Container>' % STACK)
ROW_W = ('<Container width="140" height="46">\n    %s\n</Container>' % ROW)


def col(c1, c2, c3) -> str:
    return ('<Column width="140" height="200" crossAxisAlignment="STRETCH">\n'
            '    %s\n    %s\n    %s\n</Column>' % (c1, c2, c3))


GROUPS = [
    ("A", col(C_DARK, C_GRAY, C_DARK)),
    ("B", col(C_DARK, C_GRAY, STACK)),
    ("C", col(C_DARK, STACK, C_GRAY)),
    ("D", col(C_DARK, ROW, C_GRAY)),
    ("E", col(C_DARK, C_GRAY, ROW)),
    ("F", col(C_DARK, STACK_W, C_GRAY)),
    ("G", col(C_DARK, ROW_W, C_GRAY)),
    ("H", col(STACK, C_DARK, C_GRAY)),
]

parts = []
for i, (_tag, body) in enumerate(GROUPS):
    left = 20 + i * 150
    parts.append('            <Positioned left="%d" top="20" width="140" height="200">\n'
                 '%s\n            </Positioned>' % (left, body))

PROBE = '''<Snapshot type="png" background="#FFFFFF">
    <Container width="1340" height="260">
        <Stack width="1340" height="260" fit="EXPAND" clipBehavior="NONE">
%s
        </Stack>
    </Container>
</Snapshot>''' % "\n".join(parts)


def main() -> int:
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S  # noqa: E402

    dsl_path = TMP_DIR / "dsl" / "probe-flexorder.snapshot"
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(PROBE, encoding="utf-8")

    rid = "req-a17-probe7-%s" % uuid.uuid4().hex[:6]
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    resp_dir = TMP_DIR / "responses"
    resp_dir.mkdir(parents=True, exist_ok=True)
    try:
        status, body, meta = S.snapshot_request("A17", PROBE, "probe-flexorder",
                                                timeout=180)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        status, body = 0, None
        err = f"{type(exc).__name__}: {exc}"
        meta = {"status": 0, "content_type": None, "elapsed_ms": None}
    resp_path = resp_dir / (rid + (".png" if status == 200 else ".error.json"))
    resp_path.write_bytes(body or b"")
    S.log_request("A17", {
        "request_id": rid, "task_id": "A17", "kind": "render",
        "purpose": "A17 语法探针 7：钉死 Column 子节点顺序与构件类型对后续兄弟"
                   "渲染的影响，并验证外层 Container 包装的修法（8 组对照）",
        "dsl_path": S.rel(dsl_path),
        "started_at": started, "ended_at": meta.get("ended_at"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "elapsed_ms": meta.get("elapsed_ms"),
        "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
        "http_status": status, "content_type": meta.get("content_type"),
        "response_bytes": len(body) if body else 0,
        "response_path": S.rel(resp_path), "error_summary": err,
    })
    print(json.dumps({"status": status, "bytes": len(body) if body else 0,
                      "response": S.rel(resp_path), "error": err,
                      "elapsed_ms": meta.get("elapsed_ms")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
