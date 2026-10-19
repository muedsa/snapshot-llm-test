# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
STEPS = "tmp/20261016T164020-m1/A11/steps"
for f in sorted(os.listdir(STEPS)):
    if f.startswith("v2_"):
        src = os.path.join(STEPS, f)
        dst = os.path.join(STEPS, "v3_" + f[3:])
        os.replace(src, dst)
print("renamed:", sorted(os.listdir(STEPS)))
