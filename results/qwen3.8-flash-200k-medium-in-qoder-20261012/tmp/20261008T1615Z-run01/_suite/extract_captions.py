import os, re, json, glob, hashlib

ROOT = "outputs/20261008T1615Z-run01"

def pngs(task):
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, task, "**", "*.png"), recursive=True)):
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        b = os.path.basename(rel)
        if "preview" in b or b.startswith("zoom") or "crop" in b:
            continue
        out.append(rel)
    return out

def captions(task):
    path = os.path.join(ROOT, task, "snapshot-usage.md")
    text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    gpath = os.path.join(ROOT, task, "gallery.md")
    gt = open(gpath, encoding="utf-8").read() if os.path.exists(gpath) else ""
    heads = {}
    for m in re.finditer(r"^##\s*\d*[｜|]?\s*(case-\d+)\s*·\s*(.+?)（([^（）]*)）\s*$", gt, re.M):
        heads[m.group(1)] = m.group(2)
    for m in re.finditer(r"^##\s*\d*[｜|]?\s*(case-\d+)\s*·\s*(.+?)\s*$", gt, re.M):
        heads.setdefault(m.group(1), m.group(2))
    res = {}
    for rel in pngs(task):
        b = os.path.basename(rel)
        parent = rel.split("/")[1] if len(rel.split("/")) > 2 else ""
        cap = ""
        if parent.startswith("case-") and parent in heads:
            cap = heads[parent]
        if not cap:
            cands = []
            for line in text.splitlines():
                if "`" + b + "`" in line and line.strip().startswith("|"):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    cells = [c for c in cells if c and c != "`" + b + "`"]
                    if cells:
                        cands.append(" / ".join(cells))
            for c in cands:
                if len(c) >= 6:
                    cap = c
                    break
            if not cap and cands:
                cap = cands[0]
        res[rel] = cap
    return res

allc = {}
for t in sorted(os.listdir(ROOT)):
    if not os.path.isdir(os.path.join(ROOT, t)):
        continue
    for k, v in captions(t).items():
        allc[k] = v
for k in sorted(allc):
    print("%-52s | %s" % (k, allc[k][:110]))
print("TOTAL", len(allc))
json.dump(allc, open(os.path.join(ROOT, "..", "..", "tmp", "20261008T1615Z-run01", "_suite", "caption-candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
