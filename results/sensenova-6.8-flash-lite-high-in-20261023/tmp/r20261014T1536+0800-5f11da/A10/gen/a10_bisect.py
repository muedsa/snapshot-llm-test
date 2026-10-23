"""A10 构件二分：逐个试渲染六个新构件，找出哪个让渲染挂住。

整份六格探针（含全部滤镜）连续三次 420s 读响应超时，而极简 smoke 只要 2.4s，
说明问题在某个具体构件上。这里每次只测一个构件，短超时、只试一次，
逐个并行跑，互不阻塞。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_bisect.py all [timeout]
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_bisect.py <variant> [timeout]

variant: stack-attrs | opacity | imgfilter | colorfilter | backdropfilter | clipoval
`all` 用线程池并发各发一次请求，挂住的构件不会拖慢其余构件。
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

STRIPES = (C.rect(0.0, 0.0, 26.0, 160.0, "#1E293B")
           + C.rect(50.0, 0.0, 26.0, 160.0, "#1E293B")
           + C.rect(94.0, 0.0, 26.0, 160.0, "#1E293B")
           + C.rect(138.0, 0.0, 26.0, 160.0, "#1E293B")
           + C.rect(182.0, 0.0, 26.0, 160.0, "#1E293B")
           + C.rect(226.0, 0.0, 26.0, 160.0, "#1E293B")
           + C.rect(270.0, 0.0, 26.0, 160.0, "#1E293B"))

CARD = (C.rect(20.0, 20.0, 200.0, 120.0, "#B3FFFFFF", radius=16.0)
        + C.rect(40.0, 60.0, 90.0, 30.0, "#1E293B", radius=6.0)
        + C.rect(170.0, 70.0, 30.0, 30.0, "#B91C1C", radius=15.0))


def wrap(title, body) -> str:
    return ('<Snapshot type="png" background="#F8FAFC">'
            '<Container width="360" height="240">'
            + C.stack(C.rect(0.0, 0.0, 320.0, 240.0, "#FFFFFF"),
                      C.rect(0.0, 0.0, 320.0, 1.0, "#CBD5E1"),
                      body,
                      C.txt(0.0, 214.0, 320.0, 24.0, title, 18.0,
                            color="#475569", align="CENTER"))
            + "</Container></Snapshot>")


VARIANTS = {
    "stack-attrs": ("Stack 是否接受 width/height 属性",
                    wrap("stack width/height",
                         C.stack(C.rect(0.0, 0.0, 320.0, 160.0, "#FFFFFF"),
                                 STRIPES, CARD, w=320.0, h=160.0))),
    "opacity": ("Opacity 是否把子树压平后统一变淡",
                wrap("Opacity 0.5",
                     C.rect(0.0, 0.0, 320.0, 160.0, "#FFFFFF")
                     + '<Opacity opacity="0.5">'
                     + C.stack(C.rect(40.0, 40.0, 160.0, 120.0, "#FF0000"),
                               C.rect(120.0, 80.0, 160.0, 120.0, "#0000FF"),
                               w=320.0, h=160.0)
                     + "</Opacity>")),
    "imgfilter": ("ImageFiltered 是否做子树高斯模糊",
                  wrap("ImageFiltered sigma=6",
                       C.rect(0.0, 0.0, 320.0, 160.0, "#FFFFFF")
                       + '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
                       + C.stack(STRIPES, CARD, w=320.0, h=160.0)
                       + "</ImageFiltered>")),
    "colorfilter": ("ColorFiltered MULTIPLY 是否对子树着色",
                    wrap("ColorFiltered MULTIPLY",
                         C.rect(0.0, 0.0, 320.0, 160.0, "#FFFFFF")
                         + '<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">'
                         + C.stack(STRIPES, CARD, w=320.0, h=160.0)
                         + "</ColorFiltered>")),
    "backdropfilter": ("BackdropFilter 是否只模糊背后内容",
                       wrap("BackdropFilter sigma=6",
                            C.rect(0.0, 0.0, 320.0, 160.0, "#FFFFFF") + STRIPES
                            + C.pos(20.0, 20.0, 200.0, 120.0,
                                    '<ClipRRect borderRadius="16" clipBehavior="ANTI_ALIAS">'
                                    + '<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP">'
                                    + C.container(200.0, 120.0)
                                    + "</BackdropFilter></ClipRRect>")
                            + CARD)),
    "clipoval": ("ClipOval 是否按子盒内切圆裁剪",
                 wrap("ClipOval",
                      C.rect(0.0, 0.0, 320.0, 160.0, "#FFFFFF")
                      + C.pos(60.0, 30.0, 200.0, 100.0,
                              '<ClipOval clipBehavior="ANTI_ALIAS">'
                              + C.pos(0.0, 0.0, 200.0, 100.0,
                                      STRIPES + CARD)
                              + "</ClipOval>"))),
}


def one(name: str, timeout: int) -> dict:
    desc, dsl = VARIANTS[name]
    res = CL.render("A10", dsl, "bisect-" + name, kind="probe",
                    purpose="构件二分：" + desc,
                    timeout=timeout, attempts=1, dsl_name="bisect-" + name + ".snapshot")
    log = res["log"] or {}
    out = {"variant": name, "status": res["status"],
           "elapsed_ms": log.get("elapsed_ms"),
           "bytes": len(res["body"]) if res["body"] else None,
           "error": log.get("error"), "request_id": res["request_id"]}
    if res["status"] == 200 and res["body"]:
        p = S.task_dirs("A10")[1] / "preview" / ("bisect-" + name + ".png")
        p.write_bytes(res["body"])
        out["preview"] = S.rel(p)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2 or (sys.argv[1] != "all" and sys.argv[1] not in VARIANTS):
        print(__doc__)
        print("variants:", ", ".join(VARIANTS))
        return 1
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 75
    if sys.argv[1] == "all":
        # 六个构件并发各发一次，避免逐个串行时挂住的构件拖满全部时间
        import concurrent.futures
        import json
        names = [k for k in VARIANTS]
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as ex:
            results = list(ex.map(lambda n: one(n, timeout), names))
        tmp = S.task_dirs("A10")[1]
        (tmp / "bisect-results.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        for r in results:
            print("%-15s status=%-4s %8s ms  %s" % (
                r["variant"], r["status"], r["elapsed_ms"],
                (r["error"] or "")[:60]))
        return 0
    r = one(sys.argv[1], timeout)
    print(r)
    return 0 if r["status"] == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
