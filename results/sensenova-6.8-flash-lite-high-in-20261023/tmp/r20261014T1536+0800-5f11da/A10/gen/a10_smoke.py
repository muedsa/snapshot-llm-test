"""A10 smoke：一次极简渲染，判断服务整体是否可用/变慢，与过滤镜子树无关。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_smoke.py [timeout_seconds]
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))

import a10_client as CL                     # noqa: E402
import a10_scenes as C                      # noqa: E402
import suite as S                           # noqa: E402

DSL = ('<Snapshot type="png" background="#FFFFFF">'
       '<Container width="200" height="120">'
       + C.stack(C.rect(0.0, 0.0, 200.0, 120.0, "#FFFFFF"),
                 C.rect(20.0, 30.0, 80.0, 60.0, "#FF0000"),
                 C.rect(100.0, 45.0, 80.0, 60.0, "#0000FF"))
       + "</Container></Snapshot>")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    res = CL.render("A10", DSL, "probe0-smoke", kind="probe",
                    purpose="服务可用性对照：极简无滤镜渲染，用于区分服务整体变慢与滤镜 DSL 变慢",
                    timeout=timeout, attempts=1, dsl_name="probe0-smoke.snapshot")
    print("status", res["status"],
          "elapsed_ms", (res["log"] or {}).get("elapsed_ms"),
          "bytes", len(res["body"]) if res["body"] else None,
          "error", (res["log"] or {}).get("error"))
    if res["status"] == 200 and res["body"]:
        p = S.task_dirs("A10")[1] / "preview" / "probe0-smoke.png"
        p.write_bytes(res["body"])
        print("saved", S.rel(p))
    return 0 if res["status"] == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
