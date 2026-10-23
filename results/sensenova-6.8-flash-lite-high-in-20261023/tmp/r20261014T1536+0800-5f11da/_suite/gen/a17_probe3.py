"""A17 语法探针 3：修正探针 2 的设计错误后确认 <BackdropFilter> 可见效果。

探针 2 结论是「看不到毛玻璃」，但原因不是构造无效，而是探针自身设计错误：
ClipRRect 面板被放在 x=440..576，而那里的背后内容全是白色画布，
纯色被模糊后仍是纯色，所以完全看不出效果。
这里让毛玻璃面板真正覆盖住后面的彩色图形与文字，才能观察到模糊。

依据：guides-painting「透明度与颜色滤镜」——
  BackdropFilter 对已经绘制在当前内容背后的区域应用滤镜；
  只有在其背后已经有内容时才有可见效果。
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
            <Container width="600" height="300" color="#FFFFFF" borderRadius="10"
                       border="1 SOLID #CBD5E1"/>
            <Positioned left="24" top="52" width="552" height="64">
                <Row width="552" height="64" mainAxisAlignment="SPACE_BETWEEN">
                    <Container width="66" height="64" color="#FB923C" borderRadius="8"/>
                    <Container width="66" height="64" color="#38BDF8" borderRadius="8"/>
                    <Container width="66" height="64" color="#10B981" borderRadius="8"/>
                    <Container width="66" height="64" color="#8B5CF6" borderRadius="8"/>
                    <Container width="66" height="64" color="#EC4899" borderRadius="8"/>
                    <Container width="66" height="64" color="#F59E0B" borderRadius="8"/>
                </Row>
            </Positioned>
            <Positioned left="24" top="132" width="552" height="26">
                <Container width="552" height="26" alignment="CENTER">
                    <Text fontFamily="DejaVu Sans Mono" fontSize="15" color="#334155"
                          text="AB CD EF GH IJ KL MN OP QR ST"/>
                </Container>
            </Positioned>
            <Positioned left="200" top="26" width="200" height="150">
                <ClipRRect borderRadius="14">
                    <BackdropFilter sigmaX="9" sigmaY="9" tileMode="CLAMP">
                        <Container width="200" height="150" color="#FFFFFF66"/>
                    </BackdropFilter>
                </ClipRRect>
            </Positioned>
            <Positioned left="200" top="186" width="200" height="24">
                <Container width="200" height="24" alignment="CENTER">
                    <Text fontFamily="Inter" fontSize="13" color="#334155"
                          text="BackdropFilter sigma=9"/>
                </Container>
            </Positioned>
            <Positioned left="24" top="186" width="168" height="24">
                <Container width="168" height="24" alignment="CENTER">
                    <Text fontFamily="Noto Sans CJK SC,Inter" fontSize="13"
                          color="#334155" text="未加滤镜（清晰）"/>
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

    dsl_path = TMP_DIR / "dsl" / "probe-backdrop2.snapshot"
    resp_dir = TMP_DIR / "responses"
    dsl_path.parent.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(PROBE, encoding="utf-8")

    rid = "req-a17-probe3-%s" % uuid.uuid4().hex[:6]
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A17", PROBE, "probe-backdrop2",
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
        "purpose": "A17 语法探针 3：修正探针 2 的排版错误（面板须真正覆盖背后内容），"
                   "确认 BackdropFilter 的毛玻璃效果可见且范围受 ClipRRect 限定",
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
