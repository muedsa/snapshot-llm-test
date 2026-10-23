"""A17 语法探针 4：在 CDATA 里印出 CDATA 本身（]]> 截断问题的解法验证）。

手册第 3 页的印刷代码块要原样印出这一行：
    <Text ...><![CDATA[a < b && b > a]]></Text>
而印刷块本身必须用 CDATA 包裹（解析器不做 HTML 实体解码，&lt; 会变成字面 &lt;）。
CDATA 内的字面 ]]> 会提前结束外层 CDATA，标准解法是拆成两段 CDATA：
    <![CDATA[...a < b && b > a]]]]><![CDATA[>]]></Text>
即 ]]]]> = 「]]」 + 「]]>」，两段 CDATA 的文本按顺序拼接后得到 ]]>。
本探针验证相邻 CDATA 文本片段是否按序拼接、还原结果是否与原文逐字一致。
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

# 期望逐字印出的代码（含 ]]> ）
TARGET = '''<Text fontFamily="Inter" fontSize="13"
      color="#7DD3FC"><![CDATA[a < b && b > a]]></Text>
<Raw>   keep spaces   </Raw>'''


PROBE = '''<Snapshot type="png" background="#F8FAFC">
    <Container width="820" height="240">
        <Container width="820" height="240" color="#0F172A" borderRadius="10"
                   border="1 SOLID #334155" padding="(16,20)" alignment="TOP_LEFT">
            <Text fontFamily="DejaVu Sans Mono" fontSize="15" color="#E2E8F0"
                  height="1.5"><Raw><![CDATA[<Text fontFamily="Inter" fontSize="13"
      color="#7DD3FC"><![CDATA[a < b && b > a]]]]><![CDATA[></Text>
<Raw>   keep spaces   </Raw>]]></Raw></Text>
        </Container>
    </Container>
</Snapshot>'''


def main() -> int:
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S  # noqa: E402

    dsl_path = TMP_DIR / "dsl" / "probe-cdata-print.snapshot"
    resp_dir = TMP_DIR / "responses"
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(PROBE, encoding="utf-8")

    rid = "req-a17-probe4-%s" % uuid.uuid4().hex[:6]
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A17", PROBE, "probe-cdata-print",
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
        "purpose": "A17 语法探针 4：验证「在 CDATA 里印出 CDATA」的两段 CDATA 拆分"
                   "写法能否逐字还原含 ]]> 的代码文本",
        "dsl_path": S.rel(dsl_path),
        "started_at": started, "ended_at": meta.get("ended_at"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "expected_printed_text": TARGET,
        "elapsed_ms": meta.get("elapsed_ms"),
        "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
        "http_status": status,
        "content_type": meta.get("content_type"),
        "response_bytes": len(body) if body else 0,
        "response_path": S.rel(resp_path),
        "error_summary": err,
    })
    print(json.dumps({"status": status, "bytes": len(body) if body else 0,
                      "response": S.rel(resp_path), "error": err,
                      "elapsed_ms": meta.get("elapsed_ms")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
