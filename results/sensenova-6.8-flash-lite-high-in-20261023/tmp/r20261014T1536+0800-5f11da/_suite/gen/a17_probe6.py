"""A17 语法探针 6：确认 Column 直接子节点 Row 不渲染的修法。

探针 5 与 example-01/02 的现象一致：Column 的第 1 个子节点渲染正常，
遇到「直接作为 Column 子节点的 Row」时该 Row 及其后所有兄弟都不再出现；
example-03 把 Row 包在一个有显式尺寸的 Container 里就正常。
这里并排放 5 组对照：
  V1 Column 直接子节点 Row（无宽度）      —— 复现失败
  V2 Column 直接子节点 Row（有宽度）      —— 宽度是否是解
  V3 Row 外包一层显式尺寸 Container       —— 包装是否是解
  V4 Column 直接子节点 Stack（对照组）    —— 只有 Row 有问题还是所有 Flex
  V5 Row(STRETCH) + Expanded + ColorFiltered + 裸 Container（复现 example-04 满屏紫）
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

CHIP_A = '<Container width="150" height="40" color="#0F172A" borderRadius="6"/>'
CHIP_C = '<Container width="150" height="40" color="#F1F5F9" borderRadius="6"/>'
ROW_NW = ('<Row height="46" crossAxisAlignment="STRETCH">\n'
          '    <Expanded><Container color="#0EA5E9" borderRadius="6"/></Expanded>\n'
          '    <SizedBox width="8"/>\n'
          '    <Expanded><Container color="#6366F1" borderRadius="6"/></Expanded>\n'
          '</Row>')
ROW_W = ('<Row width="150" height="46" crossAxisAlignment="STRETCH">\n'
         '    <Expanded><Container color="#0EA5E9" borderRadius="6"/></Expanded>\n'
         '    <SizedBox width="8"/>\n'
         '    <Expanded><Container color="#6366F1" borderRadius="6"/></Expanded>\n'
         '</Row>')


def col(body: str) -> str:
    return ('<Column width="150" height="200" crossAxisAlignment="STRETCH">\n'
            '    %s\n' % CHIP_A + '    %s\n' % body + '    %s\n' % CHIP_C +
            '</Column>')


PROBE = '''<Snapshot type="png" background="#FFFFFF">
    <Container width="900" height="360">
        <Stack width="900" height="360" fit="EXPAND" clipBehavior="NONE">
            <Positioned left="20" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="185" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="350" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="515" top="20" width="150" height="200">
%s</Positioned>
            <Positioned left="20" top="250" width="860" height="80">
                <Stack width="860" height="80" fit="EXPAND" clipBehavior="NONE">
                    <Container width="860" height="80" color="#F8FAFC"/>
                    <Positioned left="12" top="8" width="836" height="64">
                <Row width="836" height="64" crossAxisAlignment="STRETCH">
                    <Expanded><ColorFiltered color="#7C3AED" blendMode="MULTIPLY">
                        <Container width="128" height="56" color="#38BDF8"
                               borderRadius="8"/></ColorFiltered></Expanded>
                    <SizedBox width="12"/>
                    <Expanded><ImageFiltered sigmaX="5" sigmaY="5" tileMode="CLAMP">
                        <Container width="128" height="56" color="#38BDF8"
                               borderRadius="8"/></ImageFiltered></Expanded>
                    <SizedBox width="12"/>
                    <Container width="92" height="56" color="#FFFFFF"
                           borderRadius="8" border="1 SOLID #E2E8F0"
                           alignment="CENTER">
                        <Text fontFamily="Inter" fontSize="10" color="#334155"
                              text="sample interior"/></Container>
                </Row>
                    </Positioned>
                </Stack>
            </Positioned>
        </Stack>
    </Container>
</Snapshot>''' % (
    col(ROW_NW),
    col(ROW_W),
    col('<Container width="150" height="46">\n    %s\n</Container>' % ROW_NW),
    col('<Stack width="150" height="46">\n'
        '    <Container width="150" height="46" color="#0EA5E9" borderRadius="6"/>\n'
        '</Stack>'),
)


def main() -> int:
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S  # noqa: E402

    dsl_path = TMP_DIR / "dsl" / "probe-flexchild.snapshot"
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(PROBE, encoding="utf-8")

    rid = "req-a17-probe6-%s" % uuid.uuid4().hex[:6]
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    resp_dir = TMP_DIR / "responses"
    resp_dir.mkdir(parents=True, exist_ok=True)
    try:
        status, body, meta = S.snapshot_request("A17", PROBE, "probe-flexchild",
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
        "purpose": "A17 语法探针 6：确认 Column 直接子节点 Row 不渲染的修法"
                   "（宽度 / 外层 Container 包装 / Stack 对照），"
                   "并复现 example-04 满屏紫色",
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
