"""A17 语法探针 2：确认 <BackdropFilter> 的可见效果与作用范围。

探针 1 中 BackdropFilter 后面的内容是大块纯色，纯色被模糊后仍是纯色，
看不出模糊。这里在背景加入多条细线与若干小块，才能看到"背后已绘制内容
被模糊"的实际效果，并确认它只影响该子树之后的已绘制内容。

依据：guides-painting「透明度与颜色滤镜」——
  BackdropFilter 对已经绘制在当前内容背后的区域应用滤镜；
  只有在其背后已经有内容时才有可见效果，通常需要 ClipRect 或 ClipRRect 限定区域。
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

PROBE = '''<Snapshot type="png" background="#F8FAFC">
    <Container width="600" height="300">
        <Stack width="600" height="300" fit="EXPAND" clipBehavior="NONE">
            <Container width="600" height="300" color="#FFFFFF"
                       borderRadius="10" border="1 SOLID #CBD5E1"/>
            <Positioned left="24" top="24" width="150" height="40">
                <Container color="#FB923C" borderRadius="6"/>
            </Positioned>
            <Positioned left="24" top="76" width="150" height="40">
                <Container color="#38BDF8" borderRadius="6"/>
            </Positioned>
            <Positioned left="24" top="128" width="150" height="40">
                <Container color="#10B981" borderRadius="6"/>
            </Positioned>
            <Positioned left="24" top="180" width="150" height="40">
                <Container color="#8B5CF6" borderRadius="6"/>
            </Positioned>
            <Positioned left="200" top="30" width="376" height="240">
                <Row>
                    <Container width="240" height="240" color="#FFFFFF"/>
                    <ClipRRect borderRadius="10">
                        <BackdropFilter sigmaX="7" sigmaY="7" tileMode="CLAMP">
                            <Container width="136" height="240" color="#FFFFFF55"/>
                        </BackdropFilter>
                    </ClipRRect>
                </Row>
            </Positioned>
            <Positioned left="24" top="234" width="150" height="30">
                <Container width="150" height="30" alignment="CENTER">
                    <Text fontFamily="Noto Sans CJK SC,Inter" fontSize="12"
                          color="#334155" text="未加滤镜（清晰）"/>
                </Container>
            </Positioned>
            <Positioned left="404" top="234" width="136" height="30">
                <Container width="136" height="30" alignment="CENTER">
                    <Text fontFamily="Inter" fontSize="12" color="#334155"
                          text="BackdropFilter sigma=7"/>
                </Container>
            </Positioned>
        </Stack>
    </Container>
</Snapshot>'''


def main() -> int:
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S  # noqa: E402

    dsl_path = TMP_DIR / "dsl" / "probe-backdrop.snapshot"
    resp_dir = TMP_DIR / "responses"
    resp_dir.mkdir(parents=True, exist_ok=True)
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(PROBE, encoding="utf-8")

    rid = "req-a17-probe2-%s" % uuid.uuid4().hex[:6]
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A17", PROBE, "probe-backdrop",
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
        "purpose": "A17 语法探针 2：在纹理化背景上验证 BackdropFilter 的可见"
                   "模糊效果与作用范围（探针 1 背景为纯色，看不出模糊）",
        "dsl_path": S.rel(dsl_path),
        "started_at": started, "ended_at": meta.get("ended_at"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
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
