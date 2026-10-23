"""A08 渲染提交：按版本号提交 draft，落 tmp/ 预览 PNG 供实际看图。

用法：
  python -I tmp/<rid>/A08/gen/a08_render.py v1            # 首版预览，只留 tmp/
  python -I tmp/<rid>/A08/gen/a08_render.py v2 wayfinding  # 通过核验后落 outputs/

out_dsl 为 None 时只保留 tmp/ 里的预览，不写 outputs/（避免把未核验草稿当成品）。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import a08_build as B  # noqa: E402
import a08_io as IO  # noqa: E402

NAME = "wayfinding"


def main() -> int:
    version = sys.argv[1]
    final = len(sys.argv) > 2 and sys.argv[2] == NAME

    model = json.loads((HERE.parent / "model.json").read_text(encoding="utf-8"))
    dsl, layers = B.build(model)
    draft = HERE.parent / "draft.snapshot"
    draft.write_text(dsl, encoding="utf-8")
    print(f"DSL {len(dsl)} 字符 / {len(layers)} 图层 → {draft}")

    rec = IO.submit(
        dsl,
        label=f"A08 双路线导览图 {version}" + ("（交付版）" if final else "（预览）"),
        rid=f"req-a08-wayfinding-{version}",
        kind="render" if not final else "deliver",
        dsl_version=version,
        out_png=f"{NAME}.png" if final else None,
        out_dsl=f"{NAME}.snapshot" if final else None,
    )
    IO.save_iter({
        "task_id": "A08", "iteration": version,
        "label": rec["label"], "kind": rec["kind"],
        "request_id": rec["request_id"], "elapsed_ms": rec["elapsed_ms"],
        "http_status": rec["http_status"], "content_type": rec["content_type"],
        "response_bytes": rec["response_bytes"],
        "attempts": rec["attempts"],
        "started_at": rec["started_at"], "ended_at": rec["ended_at"],
        "timezone": rec["timezone"],
        "note": "首版渲染，待实际看图核验共享通道可读性、分岔/合流、门洞与地标文字遮挡",
    })

    rid = rec["request_id"]
    print(f"request_id={rid}  http={rec['http_status']}  "
          f"{rec['content_type']}  {rec['response_bytes']} bytes  "
          f"{rec['elapsed_ms']}ms  attempts={rec['attempts']}")
    if not rec["_ok"]:
        print("响应体（错误 JSON 原文）：")
        print(rec["_error_json"][:3000])
        return 1

    body = (HERE.parent / "responses" / f"{rid}.body").read_bytes()
    dst = HERE.parent / "preview" / f"{version}-{NAME}.png"
    dst.write_bytes(body)
    print(f"预览 → {dst}（{len(body)} bytes）")
    if final:
        print(f"交付 → outputs/<rid>/A08/{NAME}.png + {NAME}.snapshot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
