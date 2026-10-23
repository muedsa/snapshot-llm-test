"""把 a02_finalize.py 报告正文里的 {TMP}（绝对路径）改成相对 suite_root 的写法。"""
from __future__ import annotations

from pathlib import Path

P = Path(__file__).with_name("a02_finalize.py")
t = P.read_text(encoding="utf-8")
n = t.count("{TMP}")
t = t.replace("{TMP}", "tmp/{RUN}/A02")
P.write_text(t, encoding="utf-8")
print("replaced", n, "occurrences of {TMP}")
