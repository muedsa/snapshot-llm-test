"""Suite-level final review: artifacts present, gallery complete, links resolve."""
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
OUT = ROOT / "outputs" / RUN
SUITE = OUT / "_suite"
CAT = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
CFG = json.loads((ROOT / "run-config.json").read_text(encoding="utf-8"))
STATE = json.loads((SUITE / "suite-state.json").read_text(encoding="utf-8"))
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 1. required suite artifacts
for n in CFG["suite_required_artifacts"]:
    check((SUITE / n).exists(), f"missing suite artifact {n}")

# 2. every PNG under outputs/ is paired with a .snapshot of the same stem
pngs = [p for p in OUT.rglob("*.png") if "_suite" not in p.parts]
for p in pngs:
    check(p.with_suffix(".snapshot").exists(),
          f"{p.relative_to(OUT).as_posix()} has no same-stem .snapshot")

# 3. gallery covers every final image and its links resolve
gal = (SUITE / "gallery.md").read_text(encoding="utf-8")
previews = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", gal)
check(len(previews) == len(pngs),
      f"gallery previews {len(previews)} != final images {len(pngs)}")
for alt, link in previews:
    check((SUITE / link).exists(), f"broken gallery preview link {link}")
for m in re.finditer(r"\]\(([^)#][^)]*)\)", gal):
    link = m.group(1)
    check((SUITE / link).exists() or link.startswith("http"),
          f"broken gallery link {link}")
check(all(alt.strip() for alt, _ in previews), "gallery has an empty alt caption")

# 4. index covers all 30 tasks with a status and both roots
idx = (SUITE / "index.md").read_text(encoding="utf-8")
for tid in CAT["task_order"]:
    check(f"| {tid} |" in idx, f"index missing task row {tid}")
    check(f"outputs/{RUN}/{tid}/" in idx or f"tmp/{RUN}/{tid}/" in idx,
          f"index missing paths for {tid}")
for m in re.finditer(r"\]\(([^)#][^)]*)\)", idx):
    link = m.group(1)
    check((SUITE / link).exists() or link.startswith("http"),
          f"broken index link {link}")

# 5. per-task required outputs
for tid in CAT["task_order"]:
    d = OUT / tid
    spec = next(t for t in CAT["tasks"] if t["id"] == tid)
    n = len(list(d.rglob("*.png")))
    check(n >= spec["minimum_final_pngs"],
          f"{tid} has {n} images, requires {spec['minimum_final_pngs']}")
    check((d / "task-metrics.json").exists(), f"{tid} missing task-metrics.json")
    check((d / "snapshot-usage.md").exists(), f"{tid} missing snapshot-usage.md")
    if tid.startswith("B"):
        for f2 in ("portfolio.json", "portfolio.md", "gallery.md"):
            check((d / f2).exists(), f"{tid} missing {f2}")

# 6. metrics agree with the files on disk
m = json.loads((SUITE / "task-metrics.json").read_text(encoding="utf-8"))
check(m["final_images_total"] == len(pngs),
      f"metrics images {m['final_images_total']} != disk {len(pngs)}")
check(m["status"] == "completed" and m["tasks_completed"] == 30, "suite status")
check(m["window"]["task_window_union_seconds"] > 0
      and m["window"]["idle_between_windows_seconds"] >= 0, "time accounting present")

# 7. suite state: no task left pending, artifacts recorded
st = {t["id"]: t for t in STATE["tasks"]}
for tid in CAT["task_order"]:
    check(st[tid]["status"] == "completed", f"{tid} status {st[tid]['status']}")
    check(bool(st[tid]["artifacts"]) or bool(st[tid]["visual_review_evidence"]),
          f"{tid} has no recorded artifacts or evidence")
for a in ["index.md", "gallery.md", "snapshot-usage.md", "task-metrics.json",
          "suite-state.json"]:
    hit = [v for v in STATE.get("suite_artifacts", []) if str(v).endswith(a)] \
        if isinstance(STATE.get("suite_artifacts"), list) else []
    check(bool(hit), f"suite_artifacts missing {a}")

# 8. root .gitignore exists and does not exclude evidence
gi_lines = [l.strip() for l in (ROOT / ".gitignore").read_text(encoding="utf-8")
            .splitlines() if l.strip() and not l.strip().startswith("#")]
gi = " ".join(gi_lines)
for bad in ["outputs/", "tmp/", "*.png", "*.snapshot", "*.log"]:
    check(bad not in gi_lines, f".gitignore excludes evidence with {bad}")
for want in ["__pycache__/", "*.pyc", ".pytest_cache/"]:
    check(want in gi_lines, f".gitignore missing cache rule {want}")

print("suite review:", len(fails), "failures;", len(pngs), "final images")
for f in fails:
    print("  -", f)
raise SystemExit(1 if fails else 0)
