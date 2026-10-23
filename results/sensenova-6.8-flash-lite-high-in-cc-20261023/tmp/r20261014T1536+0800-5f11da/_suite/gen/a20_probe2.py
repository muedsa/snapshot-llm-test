"""A20 探针 2：补齐排版所需的三类文字度量（1 次请求）。

1. 纯数字/单位串在 fontSize=20 下的墨迹宽度（坐标轴刻度、图例、轴标题）；
2. 大字号标题（fontSize=26）的墨迹宽高；
3. 「底板 Container + Text」组合中文字墨迹相对底板左上角的真实偏移
   —— 这是判定「标签盒 = 底板矩形」能否覆盖全部文字的唯一依据。

度量口径：第 3 项用颜色掩膜（只取接近白色的像素），避免底板像素混入；
其余项用与背景 #0B1220 的差异掩膜。
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

FONT = "Noto Sans CJK SC,Inter"
BG = "#0B1220"
TEXT = "#FFFFFF"
W, H = 1600, 1500
ROW_H = 56
TEXT_LEFT = 30
TOP0 = 20

# (标签, 字符串, 字号) —— 左侧文本区，x < 780
STRINGS = [
    ("digit_0", "0", 20),
    ("digit_20", "20", 20),
    ("digit_100", "100", 20),
    ("unit_zh", "value 单位：指数", 20),
    ("legend_top3", "TOP-3（按 value 降序）：M10 广场 93 / M08 中庭 91 / M23 研究所 90", 20),
    ("legend_rule", "引导线交叉 0 处（上限 3 处）", 20),
    ("legend_gap", "标签盒间距 ≥ 4px，点径 12px", 20),
    ("axis_x_title", "x 逻辑坐标 0-100", 20),
    ("axis_y_title", "y 逻辑坐标 0-100", 20),
    ("legend_scale", "点圆直径 12px；密集处无需缩小", 20),
    ("title_26", "二十四点位标注示意图", 26),
    ("subtitle_20", "24 个点，逻辑坐标 0-100，指数分布", 20),
]

# 底板内文字测试：(标签, 底板色, 文字, 字号, 宽, 高, x, y)
PLATES = [
    ("plate_normal", "#17263B", "M01 北港 41", 20, 240, 44, 820, 200),
    ("plate_top3", "#3A2A0E", "M10 广场 93", 20, 240, 44, 820, 300),
]


def build_dsl() -> str:
    L = ['<Snapshot type="png" background="%s">' % BG,
         '  <Container width="%d" height="%d">' % (W, H),
         '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
         % (W, H)]
    for i, (_tag, s, fs) in enumerate(STRINGS):
        top = TOP0 + i * ROW_H
        L.append('      <Positioned left="%d" top="%d" width="%d" height="%d">'
                 % (TEXT_LEFT, top, 740, ROW_H - 8))
        L.append('        <Text fontFamily="%s" fontSize="%d" color="%s" text="%s"/>'
                 % (FONT, fs, TEXT, s))
        L.append('      </Positioned>')
    for tag, pc, s, fs, pw, ph, px, py in PLATES:
        L.append('      <Positioned left="%d" top="%d" width="%d" height="%d">'
                 % (px, py, pw, ph))
        L.append('        <Container width="%d" height="%d" color="%s" borderRadius="4">'
                 % (pw, ph, pc))
        L.append('          <Text fontFamily="%s" fontSize="%d" color="%s" text="%s"/>'
                 % (FONT, fs, TEXT, s))
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

    dsl = build_dsl()
    rid = "req-a20-probe2-text-%s" % uuid.uuid4().hex[:6]
    dsl_path = TMP / "dsl" / "probe2-text.snapshot"
    dsl_path.write_bytes(dsl.encode("utf-8"))

    import http.client
    status = body = None
    meta = {}
    err = None
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A20", dsl, "probe2-text",
                                                timeout=300)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        err = "%s: %s" % (type(exc).__name__, exc)

    rec = {"request_id": rid, "task_id": "A20", "kind": "probe",
           "attempt": 1, "retry_reason": None,
           "purpose": "实测刻度数字/图例/标题墨迹宽度与底板内文字偏移",
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
    a = np.array(Image.open(BytesIO(body)).convert("RGB")).astype(np.int16)
    bg = np.array(Image.new("RGB", (1, 1), BG).getpixel((0, 0)), dtype=np.int16)
    mask_bg = np.abs(a - bg).sum(axis=2) > 30
    white = np.array(Image.new("RGB", (1, 1), TEXT).getpixel((0, 0)), dtype=np.int16)
    mask_w = np.abs(a - white).sum(axis=2) < 48

    def bbox(mask, y0, y1, x0, x1):
        sub = mask[y0:y1, x0:x1]
        ys, xs = np.where(sub)
        if len(xs) == 0:
            return None
        return {"x0": int(xs.min()) + x0, "x1": int(xs.max()) + x0,
                "y0": int(ys.min()) + y0, "y1": int(ys.max()) + y0,
                "w": int(xs.max() - xs.min() + 1),
                "h": int(ys.max() - ys.min() + 1)}

    out = {"request_id": rid, "font": FONT, "rows": [], "plates": []}
    for i, (tag, s, fs) in enumerate(STRINGS):
        top = TOP0 + i * ROW_H
        ink = bbox(mask_bg, top - 6, top + ROW_H, 0, 780)
        out["rows"].append({"tag": tag, "text": s, "font_size": fs,
                            "positioned_left": TEXT_LEFT, "positioned_top": top,
                            "ink": ink})
    for tag, pc, s, fs, pw, ph, px, py in PLATES:
        txt = bbox(mask_w, py - 4, py + ph + 4, px - 4, px + pw + 4)
        plate = bbox(mask_bg, py - 4, py + ph + 4, px - 4, px + pw + 4)
        out["plates"].append({"tag": tag, "text": s, "font_size": fs,
                              "plate_pos": [px, py, pw, ph], "plate_ink": plate,
                              "text_ink": txt,
                              "text_ink_left_minus_plate_x0":
                                  (txt["x0"] - px) if txt else None,
                              "text_ink_top_minus_plate_y0":
                                  (txt["y0"] - py) if txt else None})

    report = TMP / "probe2-text-report.json"
    report.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print("rows:", len(out["rows"]), "plates:", len(out["plates"]))
    print("report:", report.relative_to(SUITE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
