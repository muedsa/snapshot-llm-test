import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A18")
a = json.load(open(os.path.join(OUT, "story-audit.json"), encoding="utf-8"))
PW, PH, PY = 490, 840, 104
for act in a["acts"]:
    px0 = act["panel_origin"][0]
    ms, mn = [], []
    for u in act["units"]:
        x, y = u["center"]
        ms.append(min(x - px0 - 18, px0 + PW - x - 18))
        mn.append(min(y - PY - 18, PY + PH - y - 18))
    ns = []
    for n in act["nodes"]:
        x, y = n["center"]
        ns.append(min(x - px0 - 36, px0 + PW - x - 36, y - PY - 36, PY + PH - y - 36))
    print("act", act["act"], "min unit->panel h-margin %.1f v-margin %.1f  min node margin %.1f"
          % (min(ms), min(mn), min(ns)))