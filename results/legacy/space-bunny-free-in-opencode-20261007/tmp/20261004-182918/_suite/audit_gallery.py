"""Audit the suite Markdown gallery against run-config's suite_required_artifacts."""
import io, json, os, re, sys

sys.path.insert(0, r"tmp\20261004-182918\_suite")
import state as S

BASE = S.SUITE_OUT
REQ = json.load(open("run-config.json", encoding="utf-8"))["suite_required_artifacts"]
CAT = json.load(open("catalog.json", encoding="utf-8"))

print("run-config suite_required_artifacts:", REQ)
missing = [a for a in REQ if not os.path.exists(os.path.join(BASE, a))]
print("missing required artifacts       :", missing or "none")
print()

g = io.open(os.path.join(BASE, "gallery.md"), encoding="utf-8").read()
print("=== gallery.md ===")
print("bytes                 :", len(g.encode("utf-8")))
previews = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", g)
print("md image previews      :", len(previews))
all_links = re.findall(r"\]\(([^)]+)\)", g)
print("total md links         :", len(all_links))
png_links = [l for l in all_links if l.endswith(".png")]
dsl_links = [l for l in all_links if l.endswith(".snapshot")]
print("png links              :", len(png_links), "(unique %d)" % len(set(png_links)))
print("snapshot links         :", len(dsl_links), "(unique %d)" % len(set(dsl_links)))
print("remote refs            :", len([l for l in all_links if re.match(r"(https?:|//|data:)", l)]))

targets = sorted(t for t in set(all_links) if not t.startswith("#"))
broken = []
for t in targets:
    p = os.path.normpath(os.path.join(BASE, t.replace("/", os.sep)))
    if not os.path.exists(p):
        broken.append(t)
print("unique targets         :", len(targets))
print("broken targets         :", broken or "none")
print()

# every delivered PNG must be previewed exactly once
disc = {}
for d, _, fs in os.walk(S.OUT_ROOT):
    for f in fs:
        if f.lower().endswith(".png"):
            disc[os.path.normpath(os.path.join(d, f))] = None
previewed = set()
for _cap, link in previews:
    previewed.add(os.path.normpath(os.path.join(BASE, link.replace("/", os.sep))))
print("PNGs on disk           :", len(disc))
print("PNGs previewed in md   :", len(previewed))
print("PNGs missing from md   :", sorted(set(disc) - previewed) or "none")
print("md previews with no PNG:", sorted(previewed - set(disc)) or "none")
print()

# per-task coverage vs catalog minimum
print("=== per-task coverage in gallery.md ===")
bad = []
for spec in CAT["tasks"]:
    tid = spec["id"]
    on_disk = sum(1 for d, _, fs in os.walk(os.path.join(S.OUT_ROOT, tid))
                  for f in fs if f.lower().endswith(".png"))
    in_md = len([l for l in png_links if ("/%s/" % tid) in l]) // 2  # preview + 原图 link
    flag = "" if in_md == on_disk else "  <-- MISMATCH"
    if flag:
        bad.append(tid)
    print("  %s  disk %2d  md %2d  min %2d%s" % (tid, on_disk, in_md, spec["minimum_final_pngs"], flag))
print("tasks with coverage mismatch:", bad or "none")
print()

# required per-image elements: title heading, preview, png link, dsl link
print("=== per-image completeness ===")
blocks = re.split(r"\n#### ", g)[1:]
incomplete = []
for b in blocks:
    head = b.split("\n", 1)[0].strip()
    if "![" not in b or ".png)" not in b or ".snapshot)" not in b or not head:
        incomplete.append(head or "<empty>")
print("#### blocks            :", len(blocks))
print("blocks missing a part  :", incomplete or "none")
print()

print("=== index.md -> gallery.md ===")
idx = io.open(os.path.join(BASE, "index.md"), encoding="utf-8").read()
print("links gallery.md       :", idx.count("](gallery.md)"))
print("mentions gallery.html  :", idx.count("gallery.html"))
