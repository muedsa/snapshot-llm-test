"""A17 语法探针 5：定位「Column 只渲染第一个子节点」的原因。

example-01 / example-02 实测：Column 内只出现第一个子节点，Row 与后面的
Container 都不见。这里并排放 4 组最小复现，逐一排除变量：
  A: Column + 3 个显式高度 Container，无 justifyContent/crossAxisAlignment
  B: 同 A + crossAxisAlignment="STRETCH"
  C: 同 A + mainAxisAlignment="SPACE_BETWEEN"
  D: 同 A + 两者都有（example-01 的实际组合）
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

COL = '''        <Column width="150" height="200" {attrs}>
            <Container height="40" color="#0F172A" borderRadius="6"/>
            <Row height="46" crossAxisAlignment="STRETCH">
                <Expanded><Container color="#0EA5E9" borderRadius="6"/></Expanded>
                <SizedBox width="8"/>
                <Expanded><Container color="#6366F1" borderRadius="6"/></Expanded>
            </Row>
            <Container height="40" color="#F1F5F9" borderRadius="6"/>
        </Column>'''


PROBE = '''<Snapshot type="png" background="#FFFFFF">
    <Container width="800" height="300">
        <Stack width="800" height="300" fit="EXPAND" clipBehavior="NONE">
            <Positioned left="20" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="190" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="360" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="530" top="20" width="150" height="200">
%s</Positioned>
        </Stack>
    </Container>
</Snapshot>''' % (
    COL.format(attrs=""),
    COL.format(attrs='crossAxisAlignment="STRETCH"'),
    COL.format(attrs='mainAxisAlignment="SPACE_BETWEEN"'),
    COL.format(attrs='mainAxisAlignment="SPACE_BETWEEN" '
                     'crossAxisAlignment="STRETCH"'),
)


def main() -> int:
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S  # noqa: E402

    dsl_path = TMP_DIR / "dsl" / "probe-column.snapshot"
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(PROBE, encoding="utf-8")

    rid = "req-a17-probe5-%s" % uuid.uuid4().hex[:6]
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    resp_dir = TMP_DIR / "responses"
    resp_dir.mkdir(parents=True, exist_ok=True)
    try:
        status, body, meta = S.snapshot_request("A17", PROBE, "probe-column",
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
        "purpose": "A17 语法探针 5：定位 Column 只渲染第一个子节点的原因"
                   "（对照 4 组 mainAxisAlignment / crossAxisAlignment 组合）",
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
