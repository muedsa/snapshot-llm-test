#!/usr/bin/env python
"""B03 单件构建 + 渲染 + 提升。

用法（从总任务根启动）：
    python tmp/run-20261011-01/B03/run_case.py 1 v1
    python tmp/run-20261011-01/B03/run_case.py --all v1

流程：pieces/cNN.py 生成 DSL → 写临时 drafts → promote 到 case-NN/final.snapshot
      → 渲染 outputs/.../case-NN/final.png（校验字节长度，失败重试最多 5 次）
      → 写 case.md → 记录 iterations.jsonl（baseline 或 visual）
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B03"))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B03/pieces"))

import finalize_task as ft  # noqa: E402

TASK = "B03"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"


def render_retry(cid: str, ver: str, dsl_rel: str, attempts=5):
    last = None
    for a in range(1, attempts + 1):
        r = ft.render_final(TASK, cid, dsl_rel, "final.png", TEMPD,
                            is_retry=a > 1, subdir=cid)
        last = r
        p = ROOT / f"{OUTD}/{cid}/final.png"
        if r.get("ok") and p.exists() and p.stat().st_size > 0:
            return r, a
        time.sleep(min(12, 3 * a))
    return last, attempts


def run_case(n: int, ver: str, kind: str = "baseline", problems=None, changes=None):
    cid = f"case-{n:02d}"
    mod = importlib.import_module(f"c{n:02d}")
    importlib.reload(mod)
    dsl = mod.build()
    (ROOT / DRAFTS).mkdir(parents=True, exist_ok=True)
    draft_rel = f"{DRAFTS}/b03-{cid}-{ver}.snapshot"
    (ROOT / draft_rel).write_text(dsl, encoding="utf-8")

    dsl_out = ft.promote_dsl(TASK, draft_rel, f"{cid}/final.snapshot")
    r, att = render_retry(cid, ver, dsl_out)
    assert r and r.get("ok"), f"{cid} 渲染失败：{r}"
    size = ft.png_size(f"{OUTD}/{cid}/final.png")
    exp = (mod.W, mod.H)
    assert (size["width"], size["height"]) == exp, f"{cid} 尺寸不符 {size} != {exp}"
    # 注意 <ImageFiltered / <ImageEmojiSpan 也以 <Image 开头，必须用标签边界匹配
    assert not re.search(r"<Image[\s>/]", dsl), f"{cid} DSL 内出现 <Image> 标签"
    png_bytes = (ROOT / f"{OUTD}/{cid}/final.png").stat().st_size

    if getattr(mod, "case_note", None):
        (ROOT / f"{OUTD}/{cid}/case.md").write_text(mod.case_note(size), encoding="utf-8")

    ft.log(TASK, version=ver, parent=None if kind == "baseline" else f"{ver}-prev",
           kind=kind, image=f"{OUTD}/{cid}/final.png",
           problems=problems or [], changes=changes or [],
           comparison=f"渲染成功 {size['width']}×{size['height']}，PNG {png_bytes} 字节",
           extra={"case_id": cid, "attempts": att, "dsl": dsl_out, "draft": draft_rel})
    print(f"OK {cid} v{ver} {size['width']}x{size['height']} attempts={att} "
          f"png={png_bytes}B dsl={(ROOT / dsl_out).stat().st_size}B")
    return {"id": cid, "png": f"{OUTD}/{cid}/final.png", "dsl": dsl_out,
            "draft": draft_rel, "size": [size["width"], size["height"]]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case", type=int)
    ap.add_argument("ver")
    ap.add_argument("--kind", default="baseline")
    ap.add_argument("--problems", default="")
    ap.add_argument("--changes", default="")
    a = ap.parse_args()
    problems = [x for x in a.problems.split("|") if x] or None
    changes = [x for x in a.changes.split("|") if x] or None
    run_case(a.case, a.ver, a.kind, problems, changes)


if __name__ == "__main__":
    main()