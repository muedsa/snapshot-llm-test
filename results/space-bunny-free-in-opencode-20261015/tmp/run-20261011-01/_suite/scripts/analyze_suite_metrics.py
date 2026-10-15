import json

d = json.load(open("outputs/run-20261011-01/_suite/task-metrics.json", encoding="utf-8"))
pt = d["per_task"]

def g(c, *keys):
    for k in keys:
        if k in c:
            return c[k]
    return None

S1 = [t for t in pt if "snapshot_requests" in t["counts"]]
S2 = [t for t in pt if "requests" in t["counts"]]
S0 = [t for t in pt if not t["counts"]]
print("S1", len(S1), [t["id"] for t in S1])
print("S2", len(S2), [t["id"] for t in S2])
print("S0", len(S0), [t["id"] for t in S0])

def tot(rows, *keys):
    return sum(g(t["counts"], *keys) or 0 for t in rows)

for label, rows in [("S1(A01-A20)", S1), ("S2(A23,A24,B01-B06)", S2)]:
    print(f"\n{label}")
    print("  images", sum(t["images"] for t in rows))
    print("  requests", tot(rows, "snapshot_requests", "requests"))
    print("  ok", tot(rows, "successful_snapshot_requests", "requests_ok"))
    print("  failed", tot(rows, "failed_snapshot_requests", "requests_failed"))
    print("  views", tot(rows, "image_views"))
    print("  retry", tot(rows, "retry_requests"))
    print("  other_service", tot(rows, "other_service_requests"))
    print("  dsl_versions", tot(rows, "dsl_versions"))
    print("  iters", tot(rows, "completed_visual_iterations", "visual_iteration_rounds"))
    print("  incomplete_iters", tot(rows, "incomplete_visual_iterations"))
    print("  renders", tot(rows, "renders"), "cases", tot(rows, "cases"))

print("\nGRAND (28 rows): requests", tot(S1+S2,"snapshot_requests","requests"),
      "ok", tot(S1+S2,"successful_snapshot_requests","requests_ok"),
      "failed", tot(S1+S2,"failed_snapshot_requests","requests_failed"),
      "views", tot(S1+S2,"image_views"), "images", sum(t["images"] for t in pt))
print("declared", d["totals"])

trackA = [t for t in pt if t["id"].startswith("A")]
trackB = [t for t in pt if t["id"].startswith("B")]
print("\nTrackA images", sum(t["images"] for t in trackA), "req", tot(trackA,"snapshot_requests","requests"),
      "ok", tot(trackA,"successful_snapshot_requests","requests_ok"), "views", tot(trackA,"image_views"))
print("TrackB images", sum(t["images"] for t in trackB), "req", tot(trackB,"snapshot_requests","requests"),
      "ok", tot(trackB,"successful_snapshot_requests","requests_ok"), "views", tot(trackB,"image_views"),
      "cases", tot(trackB,"cases"))

print("\n--- view-basis keys ---")
name_variants = {}
for t in S1:
    for k in ("image_views_from_iterations_log", "image_views_from_iteration_log", "image_views_raw"):
        if k in t["counts"]:
            name_variants.setdefault(k, []).append((t["id"], t["counts"][k], t["counts"]["image_views"]))
for k, v in name_variants.items():
    print(f"  {k}: n={len(v)} ids={[x[0] for x in v]} sum_raw={sum(x[1] for x in v)} sum_field={sum(x[2] for x in v)}")
det = [(t["id"], len(t["counts"]["image_views_detail"]), t["counts"]["image_views"]) for t in S1 if "image_views_detail" in t["counts"]]
print("  detail rows:", det)
print("  detail mismatch:", [x for x in det if x[1] != x[2]])
no_basis = [t["id"] for t in S1 if "image_views_detail" not in t["counts"] and "image_views_note" not in t["counts"]
            and "image_views_basis" not in t["counts"]]
print("  S1 tasks with no view basis:", no_basis)

print("\n--- drafts kept ---")
for t in S1:
    if "dsl_draft_files" in t["counts"]:
        print(f"  {t['id']}: files={len(t['counts']['dsl_draft_files'])} dsl_versions={t['counts']['dsl_versions']}")

print("\n--- rates ---")
rows = []
for t in pt:
    req = g(t["counts"], "snapshot_requests", "requests")
    ok = g(t["counts"], "successful_snapshot_requests", "requests_ok")
    if not req:
        continue
    rows.append((t["id"], t["images"], req, ok, ok/req, req/t["images"], t["counts"].get("image_views", 0)))
for r in sorted(rows, key=lambda x: x[4])[:8]:
    print(f"  lowest ok-rate {r[0]}: {r[3]}/{r[2]} = {r[4]*100:.1f}%")
for r in sorted(rows, key=lambda x: -x[5])[:8]:
    print(f"  req/img {r[0]}: {r[5]:.1f} (imgs={r[1]}, req={r[2]})")
tot_req = sum(r[2] for r in rows); tot_ok = sum(r[3] for r in rows); tot_fail = sum(r[2]-r[3] for r in rows)
print(f"  overall ok-rate {tot_ok}/{tot_req} = {tot_ok/tot_req*100:.1f}%; failed {tot_fail}")
fails = sorted(((r[0], r[2]-r[3]) for r in rows), key=lambda x: -x[1])
print("  failed concentration:", fails[:6], "top3 share",
      f"{sum(x[1] for x in fails[:3])/tot_fail*100:.1f}%")
print("  zero-failure tasks:", [r[0] for r in rows if r[2] == r[3]])
print("  top request share:", sorted(((r[0], r[2]) for r in rows), key=lambda x: -x[1])[:8],
      f"= {sum(x[1] for x in sorted(((r[2]) for r in rows), reverse=True)[:8])/tot_req*100:.1f}% of {tot_req}")
print("  declared ok-rate", f"{d['totals']['requests_ok']/d['totals']['requests']*100:.1f}%")

print("\n--- B04 web retrievals ---")
b04 = next(t for t in pt if t["id"] == "B04")["counts"]
print(" ", b04["web_retrievals"], b04["web_retrievals_ok"], b04["web_retrievals_failed"])
print("\n--- A21/A22 images vs counts ---")
for t in S0:
    print(" ", t["id"], "images", t["images"], "counts", t["counts"])
