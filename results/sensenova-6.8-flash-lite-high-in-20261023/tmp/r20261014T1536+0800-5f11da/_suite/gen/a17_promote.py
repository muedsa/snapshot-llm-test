"""A17 提升：把 tmp 里各交付件最新一次 200 的服务原始 PNG 与同名 .snapshot 复制进输出目录。

不重发请求、不做任何图像后处理（字节级原样复制）；失败响应不进输出目录。
生成 outputs/<run_id>/A17/promotion-manifest.json 记录每件来源的 request_id。
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import time

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A17"
TASK_OUT = SUITE_ROOT / "outputs" / RUN_ID / "A17"
sys.path.insert(0, str(HERE.parent))

from a17_build import FILES  # noqa: E402

NAMES = []
for _v in sorted(FILES.values(), key=lambda x: x[0]):
    NAMES += [_v[0], _v[1]]        # 每页两件：手册页 + 400x240 独立示例


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    resp_dir = TASK_TMP / "responses"
    dsl_dir = TASK_TMP / "dsl"
    TASK_OUT.mkdir(parents=True, exist_ok=True)

    records = []
    for name in NAMES:
        cands = sorted(resp_dir.glob("req-a17-%s-*.png" % name),
                       key=lambda p: p.stat().st_mtime)
        if not cands:
            print(json.dumps({"name": name, "promoted": False,
                              "reason": "无 200 响应"}, ensure_ascii=False))
            continue
        src = cands[-1]
        png_out = TASK_OUT / (name + ".png")
        dsl_out = TASK_OUT / (name + ".snapshot")
        shutil.copyfile(src, png_out)
        shutil.copyfile(dsl_dir / (name + ".snapshot"), dsl_out)
        rec = {"name": name, "promoted": True,
               "source_request_id": src.stem,
               "source_response": str(src.relative_to(SUITE_ROOT)),
               "output_png": str(png_out.relative_to(SUITE_ROOT)),
               "output_dsl": str(dsl_out.relative_to(SUITE_ROOT)),
               "png_bytes": src.stat().st_size,
               "copied_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
               "timezone": "Asia/Shanghai (UTC+08:00)"}
        records.append(rec)
        print(json.dumps({"name": name, "promoted": True, "bytes": rec["png_bytes"],
                          "from": rec["source_request_id"]}, ensure_ascii=False))

    manifest = TASK_OUT / "promotion-manifest.json"
    manifest.write_text(json.dumps(
        {"run_id": RUN_ID, "path_base": "suite_root",
         "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
         "timezone": "Asia/Shanghai (UTC+08:00)",
         "note": "服务原始 PNG 字节级复制，未做任何图像后处理；失败响应不进输出目录。",
         "items": records},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest.relative_to(SUITE_ROOT)),
                       "promoted": len(records), "expected": len(NAMES)},
                      ensure_ascii=False))
    return 0 if len(records) == len(NAMES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
