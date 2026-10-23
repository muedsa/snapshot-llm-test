"""A20 探针：一次请求实测三件事，为标签盒定尺寸提供真实依据。

1. 24 个候选标签串（"{id} {name} {value}"）在 fontSize=20、
   fontFamily="Noto Sans CJK SC,Inter" 下的真实墨迹外接矩形（宽高与上下偏移）；
2. 细 <Container>（2px 宽 / 2px 高）能否作为轴线渲染，以及它的实际像素范围；
3. 直径 12 与 8 的圆盘、以及「底板 + 文本」组合的实际像素范围。

测量口径：深底 #0B1220 上绘制白/浅色元素，按行带取非背景像素的最小外接矩形。
结果用于给每个标签底板上留水平内边距，标签盒在审计中即为底板矩形。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"
TASK_INPUT = SUITE_ROOT / "tasks" / "A20-dense-annotation" / "inputs" / "markers.json"

FONT = "Noto Sans CJK SC,Inter"
BG = "#0B1220"
INK = "#F8FAFC"
W, H = 1600, 1300
ROW_H = 52
TEXT_LEFT = 30
TOP0 = 16

PROBES_X = 900          # 右侧原语区左边界


def markers():
    return json.loads(TASK_INPUT.read_text(encoding="utf-8"))


def build_dsl(marks):
    L = ['<Snapshot type="png" background="%s">' % BG,
         '  <Container width="%d" height="%d">' % (W, H),
         '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
         % (W, H)]
    for i, m in enumerate(marks):
        top = TOP0 + i * ROW_H
        txt = "%s %s %s" % (m["id"], m["name"], m["value"])
        L.append('      <Positioned left="%d" top="%d" width="%d" height="%d">'
                 % (TEXT_LEFT, top, 700, ROW_H - 6))
        L.append('        <Text fontFamily="%s" fontSize="20" color="%s" text="%s"/>'
                 % (FONT, INK, txt))
        L.append('      </Positioned>')

    # 竖直细线：2 x 200
    L.append('      <Positioned left="%d" top="60" width="2" height="200">'
             % PROBES_X)
    L.append('        <Container width="2" height="200" color="%s"/>' % INK)
    L.append('      </Positioned>')
    # 水平细线：200 x 2
    L.append('      <Positioned left="%d" top="300" width="200" height="2">'
             % PROBES_X)
    L.append('        <Container width="200" height="2" color="%s"/>' % INK)
    L.append('      </Positioned>')
    # 直径 12 圆盘
    L.append('      <Positioned left="900" top="360" width="12" height="12">')
    L.append('        <Container width="12" height="12" shape="CIRCLE" color="%s"/>'
             % INK)
    L.append('      </Positioned>')
    # 直径 8 圆盘
    L.append('      <Positioned left="930" top="362" width="8" height="8">')
    L.append('        <Container width="8" height="8" shape="CIRCLE" color="%s"/>'
             % INK)
    L.append('      </Positioned>')
    # 底板 + 文本
    L.append('      <Positioned left="900" top="420" width="220" height="40">')
    L.append('        <Container width="220" height="40" color="#1E3A8A" '
             'borderRadius="6">')
    L.append('          <Text fontFamily="%s" fontSize="20" color="%s" '
             'text="M23 研究所 90" />' % (FONT, INK))
    L.append('        </Container>')
    L.append('      </Positioned>')
    # 1px 细线（最细）
    L.append('      <Positioned left="900" top="500" width="1" height="160">')
    L.append('        <Container width="1" height="160" color="%s"/>' % INK)
    L.append('      </Positioned>')
    L.append('      <Positioned left="920" top="500" width="160" height="1">')
    L.append('        <Container width="160" height="1" color="%s"/>' % INK)
    L.append('      </Positioned>')
    # 圆角 4 的 3px 线（引导线候选：圆角端点更自然）
    L.append('      <Positioned left="900" top="700" width="3" height="120">')
    L.append('        <Container width="3" height="120" color="#38BDF8" '
             'borderRadius="1">')
    L.append('        </Container>')
    L.append('      </Positioned>')
    L.append('    </Stack>')
    L.append('  </Container>')
    L.append('</Snapshot>')
    return "\n".join(L) + "\n"


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    os_environ = __import__("os").environ
    os_environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os_environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))
    import suite as S

    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "responses").mkdir(parents=True, exist_ok=True)

    dsl = build_dsl(markers())
    rid = "req-a20-probe-metrics-%s" % uuid.uuid4().hex[:6]
    dsl_path = TMP / "dsl" / "probe-metrics.snapshot"
    dsl_path.write_bytes(dsl.encode("utf-8"))

    import http.client
    status = body = None
    meta = {}
    err = None
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A20", dsl, "probe-metrics",
                                                timeout=300)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        err = "%s: %s" % (type(exc).__name__, exc)

    rec = {"request_id": rid, "task_id": "A20", "kind": "probe",
           "attempt": 1, "retry_reason": None,
           "purpose": "实测 fontSize=20 标签墨迹尺寸、细容器作直线、圆盘与底板渲染",
           "dsl_path": dsl_path.relative_to(SUITE_ROOT).as_posix(),
           "started_at": started,
           "ended_at": meta.get("ended_at"),
           "timezone": "Asia/Shanghai (UTC+08:00)",
           "expected_size": {"width": W, "height": H},
           "png_size": None, "dsl_bytes": len(dsl.encode("utf-8")),
           "elapsed_ms": meta.get("elapsed_ms"),
           "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
           "http_status": status, "content_type": meta.get("content_type"),
           "response_bytes": len(body) if body else 0,
           "response_path": None,
           "error_summary": err}

    if status == 200 and body:
        rp = TMP / "responses" / (rid + ".png")
        rp.write_bytes(body)
        rec["response_path"] = rp.relative_to(SUITE_ROOT).as_posix()
        rec["png_size"] = list(struct.unpack(">II", body[16:24]))
    else:
        rp = TMP / "responses" / (rid + ".error.json")
        rp.write_text(json.dumps({"error": err}, ensure_ascii=False),
                      encoding="utf-8")
        rec["response_path"] = rp.relative_to(SUITE_ROOT).as_posix()

    S.log_request("A20", rec)
    print("status=%s bytes=%s size=%s err=%s" % (status, len(body) if body else 0,
                                                 rec["png_size"], err))

    if status != 200 or not body:
        return 1

    from PIL import Image
    from io import BytesIO
    import numpy as np
    img = Image.open(BytesIO(body)).convert("RGB")
    a = np.array(img)
    bg = np.array(Image.new("RGB", (1, 1), BG).getpixel((0, 0)), dtype=np.int16)
    mask = (np.abs(a.astype(np.int16) - bg).sum(axis=2) > 30)

    out = {"request_id": rid, "font": FONT, "font_size": 20, "rows": []}
    for i, m in enumerate(markers()):
        top = TOP0 + i * ROW_H
        band = mask[top - 3:top + ROW_H, 0:PROBES_X - 20]
        ys, xs = np.where(band)
        if len(xs) == 0:
            out["rows"].append({"i": i, "text": None, "ink": None})
            continue
        ink = {"x0": int(xs.min()) + 0, "x1": int(xs.max()) + 0,
               "y0": int(ys.min()) + (top - 3), "y1": int(ys.max()) + (top - 3),
               "w": int(xs.max() - xs.min() + 1),
               "h": int(ys.max() - ys.min() + 1)}
        out["rows"].append({"i": i, "id": m["id"],
                            "text": "%s %s %s" % (m["id"], m["name"], m["value"]),
                            "positioned_left": TEXT_LEFT, "positioned_top": top,
                            "ink": ink})

    def rect(x0, y0, x1, y1):
        sub = mask[y0:y1 + 1, x0:x1 + 1]
        ys2, xs2 = np.where(sub)
        if len(xs2) == 0:
            return None
        return {"x0": int(xs2.min()) + x0, "x1": int(xs2.max()) + x0,
                "y0": int(ys2.min()) + y0, "y1": int(ys2.max()) + y0,
                "w": int(xs2.max() - xs2.min() + 1),
                "h": int(ys2.max() - ys2.min() + 1)}

    out["primitives"] = {
        "vline_2x200": {"positioned": [PROBES_X, 60, 2, 200],
                        "ink": rect(PROBES_X - 6, 54, PROBES_X + 8, 266)},
        "hline_200x2": {"positioned": [PROBES_X, 300, 200, 2],
                        "ink": rect(PROBES_X - 6, 294, PROBES_X + 206, 306)},
        "disc12": {"positioned": [900, 360, 12, 12],
                   "ink": rect(894, 354, 918, 378)},
        "disc8": {"positioned": [930, 362, 8, 8],
                  "ink": rect(924, 356, 944, 376)},
        "plate_with_text": {"positioned": [900, 420, 220, 40],
                            "ink": rect(894, 414, 1126, 466)},
        "vline_1x160": {"positioned": [900, 500, 1, 160],
                        "ink": rect(896, 496, 906, 664)},
        "hline_160x1": {"positioned": [920, 500, 160, 1],
                        "ink": rect(916, 496, 1086, 506)},
        "vline_3x120_r1": {"positioned": [900, 700, 3, 120],
                           "ink": rect(896, 696, 906, 824)},
    }

    report = TMP / "probe-metrics-report.json"
    report.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print("rows measured:", len(out["rows"]))
    print("report:", report.relative_to(SUITE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
