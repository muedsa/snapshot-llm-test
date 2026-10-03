import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
import importlib
import build_a23 as B  # noqa: E402

frames = B.unit_frames()
pos = [[(u["x"], u["y"]) for u in fr["units"]] for fr in frames]
print("scales", [round(f["scale"], 5) for f in frames])


def step(a, b):
    return [round(math.hypot(pos[b][i][0] - pos[a][i][0], pos[b][i][1] - pos[a][i][1]), 4)
            for i in range(12)]


s01 = step(0, 1)
s56 = step(5, 0)
print("1->2", s01)
print("6->1", s56)
print("diff", [round(abs(a - b), 4) for a, b in zip(s01, s56)])
