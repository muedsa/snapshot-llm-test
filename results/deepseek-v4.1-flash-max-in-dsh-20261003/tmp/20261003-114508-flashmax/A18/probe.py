import math, random, json, os
W, H = 1600, 1000
BLUE, ORANGE, GREY = "blue", "orange", "grey"
COLORS = {BLUE: "#2563EBFF", ORANGE: "#EA580CFF", GREY: "#94A3B8FF"}
colors = [BLUE]*5 + [ORANGE]*5 + [GREY]*5
print("panel geometry check")
for cols, gap, margin in [(3, 20, 32), (3, 24, 28)]:
    pw = (W - 2*margin - (cols-1)*gap)/cols
    print(f"  margin={margin} gap={gap} panel_w={pw}")
# node sizes
print("node diameter 44, unit diameter 36 -> min centre distance 36 (units) / 40 (unit-node)")