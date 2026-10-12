"""Dry run: print the generated scene and probe candidate question sets."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a19_scene as A  # noqa: E402

objs = A.gen_objects()
print("centre x per col:", [A.centre_x_of_col(i) for i in range(8)])
print("centre y per row:", [A.centre_y_of_row(i) for i in range(8)])
by = {o["id"]: o for o in objs}
print("\nrow3 green:", [(o["id"], o["col"]) for o in objs
                        if o["row"] == 3 and o["color"] == "green"])
print("purple rings:", [o["id"] for o in objs if o["color"] == "purple" and o["shape"] == "ring"])
print("size80 orange:", [o["id"] for o in objs if o["size"] == 80 and o["color"] == "orange"])
print("G23:", {k: by["G23"][k] for k in ("row", "col", "shape", "size", "color", "center")})
print("rings:", [o["id"] for o in objs if o["shape"] == "ring"])

# probe distance candidates around G13
import math


def d(i, j):
    a, b = by[i]["center"], by[j]["center"]
    return round(math.hypot(a["x"] - b["x"], a["y"] - b["y"]), 2)


print("\n-- G13 distances --")
for i in ("G09", "G16", "G17", "G24", "G05", "G12", "G14", "G21", "G20", "G04", "G22", "G06"):
    print(i, by[i]["row"], by[i]["col"], d(i, "G13"))

print("\n-- ring distances to G37 --")
base = by["G37"]["center"]
print("G37", by["G37"]["row"], by["G37"]["col"])
for o in objs:
    if o["shape"] == "ring" and o["id"] != "G37":
        print(" ", o["id"], round(math.hypot(o["center"]["x"] - base["x"],
                                             o["center"]["y"] - base["y"]), 2))

print("\n-- candidate centre x sets (need unique max) --")
for cand in (("G12", "G45", "G33", "G60"), ("G04", "G37", "G12", "G52"), ("G07", "G19", "G12", "G13")):
    print(cand, {i: by[i]["center"]["x"] for i in cand})