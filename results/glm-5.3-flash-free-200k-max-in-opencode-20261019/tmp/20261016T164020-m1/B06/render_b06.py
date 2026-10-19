# -*- coding: utf-8 -*-
"""B06 渲染驱动：调用共享 snapshot_client 渲染指定 case 版本并落 final.*。

用法：python render_b06.py <version> <case-XX> ...
version 如 v1；DSL 取 tmp/<run>/B06/dsl/case-XX.snapshot
（不存在时回退 case-XX_new.snapshot）。响应原始字节存
outputs/<run>/B06/case-XX/final.png，DSL 存 final.snapshot。
"""
import os
import shutil
import sys
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")

sys.path.insert(0, str(TASK_ROOT / "tmp" / RUN / "_suite"))
import snapshot_client as sc  # noqa: E402

ver = sys.argv[1]          # 如 "v1" 或 "_v2"（作 DSL 候选后缀）
tagv = ver.lstrip("_") or "v0"
cases = sys.argv[2:] or ["case-%02d" % i for i in range(1, 11)]

DSL_DIR = TASK_ROOT / "tmp" / RUN / "B06" / "dsl"
OUT = TASK_ROOT / "outputs" / RUN / "B06"

for cs in cases:
    if ver and ver != "v1":
        cands = [DSL_DIR / (cs + ver + ".snapshot"), DSL_DIR / (cs + ".snapshot"),
                 DSL_DIR / (cs + "_new.snapshot")]
    else:
        cands = [DSL_DIR / (cs + ".snapshot"), DSL_DIR / (cs + "_new.snapshot")]
    dp = next((p for p in cands if p.exists()), None)
    if dp is None:
        print(cs, ver, "NO_DSL")
        continue
    text = dp.read_text(encoding="utf-8")
    ok, info = sc.render_dsl("B06", text, "b06-%s-%s" % (cs, tagv), OUT / cs)
    dest_png = OUT / cs / "final.png"
    dest_dsl = OUT / cs / "final.snapshot"
    if ok:
        OUT.joinpath(cs).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(info["resp_file"], dest_png)
        shutil.copyfile(dp, dest_dsl)
    print(cs, ver, "ok" if ok else "FAIL", info.get("status"),
          info.get("bytes", info.get("error_body", info.get("error", ""))),
          "req=" + os.path.basename(info.get("req_file", "!")))
