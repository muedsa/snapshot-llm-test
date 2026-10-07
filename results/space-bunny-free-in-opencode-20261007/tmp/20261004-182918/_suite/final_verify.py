import io, os, json, glob
from PIL import Image

B = r"outputs\20261004-182918\_suite"
print("=== _suite deliverable encoding ===")
for f in ("index.md", "gallery.md", "snapshot-usage.md", "task-metrics.json", "suite-state.json"):
    p = os.path.join(B, f)
    d = open(p, "rb").read()
    try:
        d.decode("utf-8")
        enc = "utf-8 ok"
    except Exception as e:
        enc = "BAD: " + str(e)
    print("%-20s %8d bytes  %s" % (f, len(d), enc))

idx = io.open(os.path.join(B, "index.md"), encoding="utf-8").read()
rows = [l for l in idx.splitlines() if l.startswith("| `")]
print("\nindex.md table rows      :", len(rows))
print("index.md image links     :", sum(l.count("](") for l in rows))

print("\n=== every final PNG is a real, readable PNG with a same-name DSL ===")
root = r"outputs\20261004-182918"
tot = ok = 0
bad = []
for d, _, fs in os.walk(root):
    for f in sorted(fs):
        if not f.lower().endswith(".png"):
            continue
        tot += 1
        ap = os.path.join(d, f)
        try:
            with Image.open(ap) as im:
                im.load()
            ok += 1
        except Exception as e:
            bad.append((ap, str(e)))
        if not os.path.exists(ap.rsplit(".", 1)[0] + ".snapshot"):
            bad.append((ap, "no .snapshot"))
print("pngs:", tot, " decoded ok:", ok, " problems:", bad or "none")

print("\n=== per-task: declared vs actual, and .snapshot pairing ===")
cat = json.load(open("catalog.json", encoding="utf-8"))
mism = []
for spec in cat["tasks"]:
    tid = spec["id"]
    out = os.path.join(root, tid)
    n = sum(1 for d, _, fs in os.walk(out) for f in fs if f.lower().endswith(".png"))
    ds = sum(1 for d, _, fs in os.walk(out) for f in fs if f.lower().endswith(".snapshot"))
    if n < spec["minimum_final_pngs"] or ds < n:
        mism.append((tid, n, ds, spec["minimum_final_pngs"]))
print("tasks below minimum or short on DSL:", mism or "none")
