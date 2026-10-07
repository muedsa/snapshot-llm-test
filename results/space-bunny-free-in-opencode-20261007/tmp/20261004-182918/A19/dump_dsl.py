import sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = ROOT + r"\outputs\20261004-182918\A19"
import json
sc = json.load(open(OUT + r"\scene-data.json", encoding="utf-8"))
d = open(OUT + r"\grid-scene.snapshot", encoding="utf-8").read()
by = {o["id"]: o for o in sc["objects"]}


def num(v):
    return str(v) if isinstance(v, str) else str(round(v, 2))


HEX = {"blue": "#2563EB", "orange": "#EA580C", "green": "#16A34A", "purple": "#7C3AED"}
for oid in ("G02", "G03", "G05"):
    o = by[oid]
    bb, s = o["bbox"], o["size"]
    print(oid, o["shape"], s, o["color"], "size type", type(s).__name__,
          "xmin", bb["x_min"], type(bb["x_min"]).__name__)
    head = ('<Positioned left="%s" top="%s" width="%s" height="%s">\n'
            % (num(bb["x_min"]), num(bb["y_min"]), num(s), num(s)))
    i = d.find(head)
    print("  head:", head.strip(), "-> idx", i)
    if i >= 0:
        print("  ", repr(d[i:i + 170]))
print("ring border frags:", {w: d.count('border="%s SOLID' % w) for w in (12.0, 16.0, 20.0)})
