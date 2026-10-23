"""A10 按格二分：渲染指定的若干实验区，定位让整份六格探针挂住的那一格。

整份六格探针（含全部滤镜）连续三次 420s 读响应超时，而六个构件单独测都能
在 3s 内渲染完成，所以问题出在某格的构件组合上。这里逐格（或按子集）试渲染。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_subset.py all [timeout]
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_subset.py 1,2,3 [timeout]
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

BUILDERS = [C.cell_alpha_layers, C.cell_group_layers, C.cell_backdrop_layers,
            C.cell_subtree_layers, C.cell_multiply_layers, C.cell_clipped_layers]


def build(indices: list[int]) -> tuple[str, list[tuple]]:
    n = len(indices)
    cw = int(C.AREA_W * n + 8.0)
    ch = int(C.AREA_H + 20.0)
    layers, origins = [], []
    for k, i in enumerate(indices):
        ax = 10.0 + k * (C.AREA_W + 8.0)
        ay = 10.0
        origins.append((i, ax, ay))
        layers.append(C.area(ax, ay, BUILDERS[i - 1]()))
    dsl = ('<Snapshot type="png" background="#F8FAFC">'
           '<Container width="' + C.n(cw) + '" height="' + C.n(ch) + '">'
           + C.stack(*layers) + "</Container></Snapshot>")
    return dsl, origins, (cw, ch)


def one(spec: str, timeout: int) -> dict:
    idx = [int(s) for s in spec.split(",")]
    dsl, origins, size = build(idx)
    res = CL.render("A10", dsl, "subset-" + spec, kind="probe",
                    purpose="按格二分：实验区 " + spec + " 单独渲染，定位挂住的构件组合",
                    timeout=timeout, attempts=1, dsl_name="subset-" + spec + ".snapshot")
    log = res["log"] or {}
    out = {"spec": spec, "status": res["status"],
           "elapsed_ms": log.get("elapsed_ms"),
           "bytes": len(res["body"]) if res["body"] else None,
           "error": log.get("error"), "request_id": res["request_id"],
           "canvas": list(size)}
    if res["status"] == 200 and res["body"]:
        p = S.task_dirs("A10")[1] / "preview" / ("subset-" + spec + ".png")
        p.write_bytes(res["body"])
        out["preview"] = S.rel(p)
        out["origins"] = [[i, ox, ay] for i, ox, ay in origins]
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    spec = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    if spec == "all":
        specs = ["1", "2", "3", "4", "5", "6"]
    elif spec == "pairs":
        # 单格都能渲染，但六格一起会挂住：按两格一组找出会挂住的构件组合
        specs = ["3,4", "4,5", "5,6", "3,5", "1,6", "2,6"]
    else:
        specs = None
    if specs is not None:
        import concurrent.futures
        import datetime
        import json
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(specs)) as ex:
            results = list(ex.map(lambda s: one(s, timeout), specs))
        stamp = datetime.datetime.now().strftime("%H%M%S")
        (S.task_dirs("A10")[1] / ("subset-" + spec + "-" + stamp + "-results.json")
         ).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        for r in results:
            print("cells %-6s status=%-4s %8s ms  %s" % (
                r["spec"], r["status"], r["elapsed_ms"], (r["error"] or "")[:70]))
        return 0
    r = one(spec, timeout)
    print(r)
    return 0 if r["status"] == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
