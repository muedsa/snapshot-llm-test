# -*- coding: utf-8 -*-
"""One-shot wording fixes for build_c07.py (kept as a traceable patch step)."""
import io

P = "build_c07.py"
s = io.open(P, encoding="utf-8").read()
REPL = [
    ("门槛上方 1 元是最便宜的一格，", "门槛那一格最便宜，"),
    ("跨过去之后每一分都按原价走", "一旦跨过去，多花的每一分都按原价走"),
    ("绿色圈 = 最优凑单点：比上一格便宜，", "绿色圈 = 最优凑单点：门槛那一格本身最便宜，"),
]
for a, b in REPL:
    if a not in s:
        raise SystemExit("NOT FOUND: %r" % a)
    s = s.replace(a, b)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched", P)