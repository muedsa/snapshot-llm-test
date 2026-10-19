# -*- coding: utf-8 -*-
"""B05 渲染驱动：调用共享 snapshot_client 渲染指定 case 版本并落 final.*。

用法：python render_b05.py <version> <case-XX> ...
version 如 v1；DSL 取 tmp/<run>/B05/dsl/case-XX.snapshot
（不存在时回退 case-XX_new.snapshot）。响应原始字节存
outputs/<run>/B05/case-XX/final.png，DSL 存 final.snapshot。
"""
import os
import shutil
import sys
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")

sys.path.insert(0, str(TASK_ROOT / "tmp" / RUN / "_suite"))
import snapshot_client as sc  # noqa: E402

ver = sys.argv[1]
cases = sys.argv[2:] or ["case-%02d" % i for i in range(1, 11)]

DSL_DIR = TASK_ROOT / "tmp" / RUN / "B05" / "dsl"
OUT = TASK_ROOT / "outputs" / RUN / "B05"

for cs in cases:
    dp = DSL_DIR / (cs + ".snapshot")
    if not dp.exists():
        dp = DSL_DIR / (cs + "_new.snapshot")
    text = dp.read_text(encoding="utf-8")
    ok, info = sc.render_dsl("B05", text, "b05-%s-%s" % (cs, ver), OUT / cs)
    dest_png = OUT / cs / "final.png"
    dest_dsl = OUT / cs / "final.snapshot"
    if ok:
        shutil.copyfile(info["resp_file"], dest_png)
        shutil.copyfile(dp, dest_dsl)
    print(cs, ver, "ok" if ok else "FAIL", info.get("status"),
          info.get("bytes", info.get("error_body", info.get("error", ""))),
          "req=" + os.path.basename(info.get("req_file", "!")))
