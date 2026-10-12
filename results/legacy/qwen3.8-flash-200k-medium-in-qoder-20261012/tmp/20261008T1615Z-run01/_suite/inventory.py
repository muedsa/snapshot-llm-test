import os, glob

ROOT = "outputs/20261008T1615Z-run01"
rows = {}
for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.png"), recursive=True)):
    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
    rows.setdefault(rel.split("/")[0], []).append(rel)

tot = 0
for t in sorted(rows):
    print("==", t, len(rows[t]))
    for r in rows[t]:
        pair = r[:-4] + ".snapshot"
        mark = "" if os.path.exists(os.path.join(ROOT, pair)) else "  [NO-SNAPSHOT]"
        print("   ", r, mark)
    tot += len(rows[t])
print("TOTAL PNG", tot)
