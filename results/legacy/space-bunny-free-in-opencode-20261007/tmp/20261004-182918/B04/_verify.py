import io, os, re, json
from PIL import Image

OUT = r"outputs\20261004-182918\B04"
print("--- files ---")
for root, dirs, files in os.walk(OUT):
    for f in sorted(files):
        p = os.path.join(root, f)
        print("%-46s %9d" % (os.path.relpath(p, OUT).replace("\\", "/"),
                             os.path.getsize(p)))
print()
print("--- png / dsl pairing + dimensions ---")
for i in range(1, 11):
    c = "case-%02d" % i
    png = os.path.join(OUT, c, "final.png")
    dsl = os.path.join(OUT, c, "final.snapshot")
    im = Image.open(png)
    txt = io.open(dsl, encoding="utf-8").read()
    m = re.search(r'<Container width="(\d+)" height="(\d+)"', txt)
    same = im.size == (int(m.group(1)), int(m.group(2)))
    print("%s png=%dx%d dsl=%sx%s match=%s case.md=%s"
          % (c, im.size[0], im.size[1], m.group(1), m.group(2), same,
             os.path.exists(os.path.join(OUT, c, "case.md"))))
print()
g = io.open(os.path.join(OUT, "gallery.html"), encoding="utf-8").read()
links = re.findall(r'(?:href|src)="([^"]+)"', g)
links = [h for h in links if not h.startswith("#")]
missing = [h for h in links if not os.path.exists(os.path.join(OUT, h.split("#")[0]))]
print("gallery local links:", len(links), "| missing:", missing)
print("gallery remote refs:", re.findall(r'(?:src|href)="https?://[^"]+"', g))
print("gallery final.png refs:", len(re.findall(r"case-\d\d/final\.png", g)))
print("gallery final.snapshot refs:", len(re.findall(r"case-\d\d/final\.snapshot", g)))
print("gallery case.md refs:", len(re.findall(r"case-\d\d/case\.md", g)))
print("gallery <script> tags:", g.count("<script"))
pm = io.open(os.path.join(OUT, "portfolio.md"), encoding="utf-8").read()
print("portfolio.md case.md refs:", len(re.findall(r"case-\d\d/case\.md", pm)))
print("portfolio.md final.png refs:", len(re.findall(r"case-\d\d/final\.png", pm)))
P = json.load(io.open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
print("portfolio.json cases:", len(P["cases"]),
      "| unique dims:", len({tuple(c["dimensions"]) for c in P["cases"]}))
for c in P["cases"]:
    ok = os.path.exists(os.path.join(OUT, c["png"])) and \
        os.path.exists(os.path.join(OUT, c["snapshot"])) and \
        os.path.exists(os.path.join(OUT, c["case_note"]))
    if not ok:
        print("MISSING", c["id"])
print("all portfolio paths exist")
S = json.load(io.open(os.path.join(OUT, "sources.json"), encoding="utf-8"))
print("sources:", len(S["sources"]), "| per-case map:", len(S["per_case_source_map"]))
M = json.load(io.open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))
print("metrics: renders=%s ok=%s failed=%s retries=%s views=%s cases=%s"
      % (M["counts"]["render_requests"], M["counts"]["successful_render_requests"],
         M["counts"]["failed_render_requests"], M["counts"]["retry_requests"],
         M["counts"]["image_views"], M["final_case_count"]))
print("usage nulls:", {k: M["usage"][k] for k in
                       ("input_tokens", "output_tokens", "total_tokens", "cost")})
print("queue/rate-limit:", M["rate_limit_or_queue_wait_seconds"])
