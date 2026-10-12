"""Check every task's declared deliverables against what is on disk (A and B tracks)."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
CAT = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))


def spec_of(task):
    for d in os.listdir(os.path.join(ROOT, "tasks")):
        if d.startswith(task["id"] + "-"):
            return json.load(open(os.path.join(ROOT, "tasks", d, "task.json"),
                                  encoding="utf-8"))
    raise KeyError(task["id"])


def png_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size, im.format
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


rows = []
total_png = 0
for task in CAT["tasks"]:
    tid = task["id"]
    spec = spec_of(task)
    out = os.path.join(ROOT, "outputs", RUN, tid)
    tmp = os.path.join(ROOT, "tmp", RUN, tid)
    need = task.get("minimum_final_pngs", 0)
    min_cases = task.get("minimum_independent_cases", 0)
    problems = []
    found = 0

    if "case_artifacts" in spec:                      # B track: per-case folders
        cases = sorted([d for d in os.listdir(out)
                        if os.path.isdir(os.path.join(out, d))
                        and not d.startswith("_")]) if os.path.isdir(out) else []
        if len(cases) < max(min_cases, need):
            problems.append("only %d case dirs, need %d" % (len(cases), max(min_cases, need)))
        for c in cases:
            for art in spec["case_artifacts"]:
                p = os.path.join(out, c, art)
                if not os.path.exists(p):
                    problems.append("MISSING %s/%s" % (c, art))
                elif art.endswith(".png"):
                    found += 1
                    size, fmt = png_size(p)
                    if fmt != "PNG":
                        problems.append("FORMAT %s/%s is %s" % (c, art, fmt))
        for art in spec["case_artifacts"]:
            if art.endswith(".png"):
                total = sum(1 for c in cases
                            if os.path.exists(os.path.join(out, c, art)))
                if total != len(cases):
                    problems.append("not every case has %s" % art)
        for fn in spec.get("common_outputs", []) + spec.get("additional_outputs", []):
            if not os.path.exists(os.path.join(out, fn)):
                problems.append("MISSING %s" % fn)
        for lf in spec.get("log_files", []):
            if not os.path.exists(os.path.join(tmp, lf)):
                problems.append("MISSING log %s" % lf)
        got = found
    else:                                             # A track
        for r in spec.get("required_outputs", []):
            p = os.path.join(out, r["filename"])
            if not os.path.exists(p):
                problems.append("MISSING %s" % r["filename"])
                continue
            found += 1
            size, fmt = png_size(p)
            if size and tuple(size) != (r["width"], r["height"]):
                problems.append("SIZE %s got %s want %s" % (r["filename"], size,
                                                           (r["width"], r["height"])))
            if fmt != "PNG":
                problems.append("FORMAT %s is %s" % (r["filename"], fmt))
            dsl = p.rsplit(".", 1)[0] + ".snapshot"
            if not os.path.exists(dsl):
                problems.append("MISSING dsl for %s" % r["filename"])
            elif "<Snapshot" not in open(dsl, encoding="utf-8").read(200):
                problems.append("BAD dsl head for %s" % r["filename"])
        for fn in spec.get("additional_outputs", []) + spec.get("common_outputs", []):
            if not os.path.exists(os.path.join(out, fn)):
                problems.append("MISSING %s" % fn)
        got = found
    total_png += got
    rows.append((tid, need, got, problems))

print("%-5s %6s %6s  %s" % ("task", "need", "got", "problems"))
bad = 0
for tid, need, got, problems in rows:
    if problems or got < need:
        bad += 1
    print("%-5s %6d %6d  %s" % (tid, need, got, "; ".join(problems)[:220] if problems else "ok"))
print()
print("tasks with problems:", bad, "/", len(rows))
print("delivered PNGs:", total_png, "| suite minimum:", CAT["minimum_final_pngs"])
on_disk = 0
for t in CAT["tasks"]:
    d = os.path.join(ROOT, "outputs", RUN, t["id"])
    for base, _, files in os.walk(d):
        on_disk += sum(1 for f in files if f.lower().endswith(".png"))
print("total PNG files anywhere under outputs/<run>/<task>/:", on_disk)
sys.exit(0)
