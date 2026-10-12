import os, json, glob, hashlib, struct, re, datetime

ROOT = "outputs/20261008T1615Z-run01"
RUN = "20261008T1615Z-run01"
CAT = json.load(open("catalog.json", encoding="utf-8"))
ORDER = CAT["task_order"]
TITLE = {t["id"]: t["title"] for t in CAT["tasks"]}
MINIMG = {t["id"]: t.get("minimum_final_pngs") for t in CAT["tasks"]}
DIR = {t["id"]: t.get("directory") for t in CAT["tasks"]}


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None, False
    w, h = struct.unpack(">II", head[16:24])
    color = head[25]
    return w, h, color == 6


def rd(p):
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def iso(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- per task ----------
tasks = {}
for tid in ORDER:
    d = os.path.join(ROOT, tid)
    m = json.load(open(os.path.join(d, "task-metrics.json"), encoding="utf-8"))
    c = m.get("counts") or {}
    ti = m.get("timings") or {}
    imgs = []
    for p in sorted(glob.glob(os.path.join(d, "**", "*.png"), recursive=True)):
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        b = os.path.basename(rel)
        if "preview" in b or b.startswith("zoom") or "crop" in b or b.startswith("probe-") or rel.startswith(tid + "/probe/"):
            continue
        if not os.path.exists(p[:-4] + ".snapshot"):
            continue
        w, h, rgba = png_size(p)
        snap = p[:-4] + ".snapshot"
        imgs.append({
            "rel": rel,
            "png": rel,
            "snapshot": rel[:-4] + ".snapshot",
            "width": w,
            "height": h,
            "rgba": rgba,
            "png_bytes": os.path.getsize(p),
            "png_md5": md5(p),
            "snapshot_bytes": os.path.getsize(snap),
            "snapshot_md5": md5(snap),
            "report": ("../" + rel.rsplit("/", 1)[0] + "/case.md") if "/case-" in rel else None,
        })
    # evidence span from logs
    recs = rd(os.path.join("tmp", RUN, tid, "requests.jsonl")) + rd(os.path.join("tmp", RUN, tid, "iterations.jsonl"))
    stamps = sorted([iso(r.get("started_at") or r.get("recorded_at")) for r in recs if (r.get("started_at") or r.get("recorded_at")) and iso(r.get("started_at") or r.get("recorded_at"))])
    span = None
    gaps = []
    if len(stamps) >= 2:
        span = round((stamps[-1] - stamps[0]).total_seconds(), 1)
        prev = stamps[0]
        for s in stamps[1:]:
            g = (s - prev).total_seconds()
            if g > 300:
                gaps.append({"from": prev.isoformat(), "to": s.isoformat(), "seconds": round(g, 1)})
            prev = s
    tasks[tid] = {
        "id": tid,
        "title": TITLE[tid],
        "catalog_directory": DIR[tid],
        "minimum_final_pngs": MINIMG[tid],
        "status": m.get("status"),
        "stop_reason": m.get("stop_reason"),
        "final_images": len(imgs),
        "images": imgs,
        "counts": c,
        "timings": ti,
        "recomputed_evidence_span_seconds": span,
        "recomputed_idle_gaps_over_300s": gaps,
        "started_at": ti.get("started_at") or ti.get("task_started_at"),
        "ended_at": ti.get("ended_at") or ti.get("task_ended_at"),
        "output_dir": "outputs/%s/%s/" % (RUN, tid),
        "temp_dir": "tmp/%s/%s/" % (RUN, tid),
        "closeout": [f for f in ["snapshot-usage.md", "task-metrics.json", "gallery.md", "portfolio.md", "portfolio.json", "design-review.md", "problem-evidence.json", "asset-sources.json"]
                     if os.path.exists(os.path.join(d, f))],
    }

shared = rd(os.path.join("tmp", RUN, "_suite", "requests.jsonl"))
shared_doc = [r for r in shared if str(r.get("kind", "")).lower() in ("doc", "docs", "document", "guide")]
suite_recs = list(shared)
for tid in ORDER:
    suite_recs += rd(os.path.join("tmp", RUN, tid, "requests.jsonl")) + rd(os.path.join("tmp", RUN, tid, "iterations.jsonl"))
allstamps = sorted([iso(r.get("started_at") or r.get("recorded_at")) for r in suite_recs if (r.get("started_at") or r.get("recorded_at")) and iso(r.get("started_at") or r.get("recorded_at"))])

summary = {
    "run_id": RUN,
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "suite_wall_clock_started_at": iso(min([t["started_at"] for t in tasks.values() if t["started_at"]])).isoformat() if any(t["started_at"] for t in tasks.values()) else None,
    "suite_evidence_first": allstamps[0].isoformat() if allstamps else None,
    "suite_evidence_last": allstamps[-1].isoformat() if allstamps else None,
    "suite_evidence_span_seconds": round((allstamps[-1] - allstamps[0]).total_seconds(), 1) if len(allstamps) > 1 else None,
    "suite_idle_gaps_over_300s": [
        {"from": a.isoformat(), "to": b.isoformat(), "seconds": round((b - a).total_seconds(), 1)}
        for a, b in zip(allstamps, allstamps[1:]) if (b - a).total_seconds() > 300
    ],
    "shared_requests": len(shared),
    "shared_doc_requests": len(shared_doc),
    "tasks": tasks,
}
total_imgs = sum(t["final_images"] for t in tasks.values())
summary["totals"] = {
    "tasks": len(tasks),
    "final_images": total_imgs,
    "minimum_required": sum(v for v in MINIMG.values() if v),
    "snapshot_requests": sum((t["counts"].get("snapshot_requests") or 0) for t in tasks.values()),
    "successful_snapshot_requests": sum((t["counts"].get("successful_snapshot_requests") or 0) for t in tasks.values()),
    "failed_snapshot_requests": sum((t["counts"].get("failed_snapshot_requests") or 0) for t in tasks.values()),
    "image_views": sum((t["counts"].get("image_views") or 0) for t in tasks.values()),
    "completed_visual_iterations": sum((t["counts"].get("completed_visual_iterations") or 0) for t in tasks.values()),
    "dsl_versions": sum((t["counts"].get("dsl_versions") or 0) for t in tasks.values()),
}
out = os.path.join("tmp", RUN, "_suite", "suite-facts.json")
json.dump(summary, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", out)
print("total final images:", total_imgs)
for tid in ORDER:
    t = tasks[tid]
    print("%s status=%-11s imgs=%d/%s views=%s viter=%s req=%s span=%s gaps>%ds=%d" % (
        tid, t["status"], t["final_images"], MINIMG[tid],
        t["counts"].get("image_views"), t["counts"].get("completed_visual_iterations"),
        t["counts"].get("snapshot_requests"), t["recomputed_evidence_span_seconds"],
        300, len(t["recomputed_idle_gaps_over_300s"])))
print("suite idle gaps>300s:", len(summary["suite_idle_gaps_over_300s"]))
