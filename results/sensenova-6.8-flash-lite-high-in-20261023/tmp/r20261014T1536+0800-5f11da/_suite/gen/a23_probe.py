"""A23 定位探针：400 RENDER_ERROR "Layout size is infinite" 的增量二分。

一次只加一层，找出到底是哪一层触发的无限布局。所有响应原文保留在
tmp/<run_id>/A23/responses/ 下，失败的 JSON 也是证据。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
import snap_client as C  # noqa: E402
import suite as S  # noqa: E402

TASK = "A23"

PROBES = {
    "p1-stack": '''<Snapshot width="600" height="600" type="png" background="transparent">
  <Stack width="600" height="600" clipBehavior="NONE">
    <Positioned left="215.8" top="505.2" width="340" height="22">
      <Container width="340" height="22" color="#8FAF4E"/>
    </Positioned>
  </Stack>
</Snapshot>''',

    "p2-transform": '''<Snapshot width="600" height="600" type="png" background="transparent">
  <Stack width="600" height="600" clipBehavior="NONE">
    <Positioned left="300.8" top="338.47" width="170" height="140">
      <Transform matrix="(0.9659,-0.2588,0,0,0.2588,0.9659,0,0,0,0,1,0,-15.221,24.3848,0,1)">
        <Container width="170" height="140" color="#EFE3CB"/>
      </Transform>
    </Positioned>
  </Stack>
</Snapshot>''',

    "p3-triangle": '''<Snapshot width="600" height="600" type="png" background="transparent">
  <Stack width="600" height="600" clipBehavior="NONE">
    <Positioned left="275.8" top="203.53" width="220" height="96">
      <Transform matrix="(0.9063,0.4226,0,0,-0.4226,0.9063,0,0,0,0,1,0,30.5918,-41.9908,0,1)">
        <SizedBox width="220" height="96">
          <ClipPath path="M50 0 L100 100 L0 100 Z" viewBox="0 0 100 100" fit="FILL">
            <Container width="220" height="96" color="#B5462F"/>
          </ClipPath>
        </SizedBox>
      </Transform>
    </Positioned>
  </Stack>
</Snapshot>''',

    "p4-triangle-no-transform": '''<Snapshot width="600" height="600" type="png" background="transparent">
  <Stack width="600" height="600" clipBehavior="NONE">
    <Positioned left="275" top="203" width="220" height="96">
      <SizedBox width="220" height="96">
        <ClipPath path="M50 0 L100 100 L0 100 Z" viewBox="0 0 100 100" fit="FILL">
          <Container width="220" height="96" color="#B5462F"/>
        </ClipPath>
      </SizedBox>
    </Positioned>
  </Stack>
</Snapshot>''',

    "p5-triangle-sizedbox-outside": '''<Snapshot width="600" height="600" type="png" background="transparent">
  <Stack width="600" height="600" clipBehavior="NONE">
    <Positioned left="275" top="203" width="220" height="96">
      <ClipPath path="M50 0 L100 100 L0 100 Z" viewBox="0 0 100 100" fit="FILL">
        <Container width="220" height="96" color="#B5462F"/>
      </ClipPath>
    </Positioned>
  </Stack>
</Snapshot>''',

}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    results = {}
    for label, dsl in PROBES.items():
        r = C.render(TASK, dsl, label, kind="probe",
                     purpose="定位 Layout size is infinite", attempts=1)
        st = r["status"]
        err = (r["log"].get("error") or "")
        results[label] = {"status": st, "error": err, "bytes": len(r["body"]) if r["body"] else None}
        print("  %-28s status=%-4s %s" % (label, st, err[:90]))
    out_dir, tmp_dir = S.task_dirs(TASK)
    p = tmp_dir / "probe-layout.json"
    p.write_text(json.dumps(results, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n探针结果：", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
