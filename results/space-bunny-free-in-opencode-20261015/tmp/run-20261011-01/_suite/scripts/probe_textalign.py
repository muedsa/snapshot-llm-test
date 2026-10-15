#!/usr/bin/env python
# 能力探针：确认 textAlign 的合法取值，以及 ClipPath 标签是否真的可用。
# 依据：https://snapshot.muedsa.com/reference/parser-tags/
# 文档写 textAlign 默认 START/LTR，但没说枚举；这里逐个试，**以服务真实响应为准**。
# 启动基准：总任务根 (suite_root)。用法：python probe_textalign.py
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
PROBE = ROOT / "tmp/run-20261011-01/_suite/probe"
PROBE.mkdir(parents=True, exist_ok=True)

CANDIDATES = ["START", "CENTER", "END", "JUSTIFY", "start", "center",
              "LEFT", "RIGHT", "left", "right"]
CLIP_PATHS = [
    ("clippath-basic", '<ClipPath path="M0 0 H100 V100 H0 Z" viewBox="0 0 100 100" fit="CONTAIN">'
                       '<Container color="#16A34A" /></ClipPath>'),
]


def render(name: str, body: str) -> dict:
    dsl = PROBE / f"{name}.snapshot"
    dsl.write_text(f'<Snapshot type="png">\n<Container width="240" height="120" color="#0F172A">'
                   f'{body}</Container>\n</Snapshot>\n', encoding="utf-8")
    cmd = [sys.executable,
           str(ROOT / "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"),
           "--task", "SHARED", "--version", name,
           "--dsl", str(dsl).replace("\\", "/"),
           "--out", f"tmp/run-20261011-01/_suite/probe/{name}.png",
           "--log", "tmp/run-20261011-01/_suite/requests.jsonl",
           "--responses-dir", "tmp/run-20261011-01/_suite/responses"]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(ROOT))
    out = (p.stdout or "").strip().splitlines()
    try:
        return json.loads(out[-1])
    except Exception:  # noqa: BLE001
        return {"ok": False, "error": (p.stdout or "") + (p.stderr or "")}


def msg_of(res: dict) -> str:
    rf = res.get("response_file") or ""
    if rf.endswith(".json"):
        try:
            return json.loads((ROOT / rf).read_text(encoding="utf-8")).get("message", "")
        except Exception:  # noqa: BLE001
            return ""
    return ""


def main() -> None:
    rows = []
    for v in CANDIDATES:
        body = f'<Stack fit="EXPAND"><Positioned left="0" top="0" width="240" height="120">' \
               f'<Text textAlign="{v}" fontSize="20" color="#F8FAFC" text="Align {v} 测试文本"/>' \
               f'</Positioned></Stack>'
        r = render(f"align-{v.lower()}", body)
        rows.append({"attr": "textAlign", "value": v, "ok": bool(r.get("ok")),
                     "status": r.get("status"), "message": msg_of(r)[:160]})
        print(f'textAlign="{v}" -> ok={r.get("ok")} {msg_of(r)[:90]}')

    for name, body in CLIP_PATHS:
        wrapped = f'<Stack fit="EXPAND"><Positioned left="20" top="20" width="200" height="80">' \
                  f'{body}</Positioned></Stack>'
        r = render(f"probe-{name}", wrapped)
        rows.append({"attr": "ClipPath", "value": name, "ok": bool(r.get("ok")),
                     "status": r.get("status"), "message": msg_of(r)[:160]})
        print(f'{name} -> ok={r.get("ok")} {msg_of(r)[:90]}')

    (PROBE / "textalign-clippath-probe.json").write_text(
        json.dumps({"source": "https://snapshot.muedsa.com/reference/parser-tags/",
                    "note": "文档列了 textAlign 属性且默认 START/LTR，但未列枚举；"
                            "以下取值为服务真实响应结果。",
                    "results": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n->", (PROBE / "textalign-clippath-probe.json").relative_to(ROOT))


if __name__ == "__main__":
    main()