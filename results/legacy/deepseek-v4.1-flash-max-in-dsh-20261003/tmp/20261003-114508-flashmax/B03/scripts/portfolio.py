"""portfolio.py - emit portfolio.json, portfolio.md, gallery.html and task-metrics.json.

Case facts are shared with promote.py's table by importing it, so the metadata cannot drift
from the files that were actually shipped.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B03"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(TMP, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
import promote  # noqa: E402
import suite_common as sc  # noqa: E402
from PIL import Image  # noqa: E402

CASES = promote.CASES
pres = json.load(open(os.path.join(TMP, "presentation.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(TMP, "presentation.json")) else {}

reqs = sc.read_jsonl(os.path.join(TMP, "requests.jsonl"))
iters = sc.read_jsonl(os.path.join(TMP, "iterations.jsonl"))


def dims(no):
    p = os.path.join(OUT, f"case-{no}", "final.png")
    with Image.open(p) as im:
        return [im.width, im.height]


def view_evidence(no):
    out = []
    for it in iters:
        if it.get("case") == f"case-{no}" and it.get("viewed_at"):
            out.append({"iteration": it["id"], "version": it["version"],
                        "viewed_at": it["viewed_at"], "observation": it["observation"][:220],
                        "files": it.get("files", [])})
    return out


def requests_for(no):
    ids = []
    for r in reqs:
        rf = (r.get("request_file") or "").replace("\\", "/")
        if rf.endswith(f"case-{no}.snapshot"):
            ids.append(r["request_id"])
    return ids


cases = []
for c in CASES:
    cases.append({
        "id": f"case-{c['no']}",
        "title": c["title"],
        "audience": c["audience"],
        "use_context": c["context"],
        "user_goal": c["goal"],
        "content_basis": c["content"],
        "visual_intent": c["visual"],
        "png": f"case-{c['no']}/final.png",
        "snapshot": f"case-{c['no']}/final.snapshot",
        "case_md": f"case-{c['no']}/case.md",
        "dimensions": dims(c["no"]),
        "dsl_capabilities": c["caps"],
        "completion_criteria": c["criteria"],
        "visual_review": c["review"],
        "review_evidence": view_evidence(c["no"]),
        "request_ids": requests_for(c["no"]),
        "iteration_ids": [i["id"] for i in iters if i.get("case") == f"case-{c['no']}"],
        "supporting_assets": [],
        "fictional_disclosure": "All subjects, brands, people, places, measurements and "
                                "prices in this work are invented demo content for a DSL "
                                "study; nothing depicts a real organisation or dataset.",
        "unresolved_issues": c["unresolved"],
    })

portfolio = {
    "schema_version": 1,
    "task_id": TASK,
    "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets (creative track) — no supporting "
                    "assets were used; every work is pure DSL",
    "curatorial_statement": (
        "Twelve finished pieces, each built around a different *structure* rather than a "
        "different colour scheme: a night-possession time-space grid, a fermentation day "
        "curve, a generative botanical plate, an LED departure board, a circular "
        "seismograph drum, a 24-channel meter wall, a cross-stitch chart, a picture-book "
        "spread, a washi recipe card, a hand-engraved fingering chart, an ornamental "
        "playbill and a weekly tide matrix. The set is a study of what becomes possible "
        "once three measured DSL facts are known: the exact Transform placement rule, an "
        "honest text-width model, and the service's element/body/height budgets. Each piece "
        "also had to survive being looked at, so every work in this set carries at least one "
        "documented visual correction."),
    "case_field_guide": {
        "id": "case-01..case-12",
        "request_ids": "every render that used this case's DSL, in order",
        "review_evidence": "iteration records that name a real image-view time",
    },
    "cases": cases,
    "final_collection_review": (
        "Twelve works reviewed at full size and as a contact sheet. Independence check: no "
        "two works share a layout skeleton, and the shared code is limited to primitives "
        "(text fitting, rotated bars, area fills, legends). Size range 1080x1520 to "
        "1920x1200; colour languages differ per work by design (control-room navy, linen "
        "paper, cream museum plate, black LED, smoked paper, console charcoal, woven flax, "
        "paper-collage brights, washi, white music paper, cream playbill, deep-water dark). "
        "Defects found and fixed in review are listed per case. Remaining known limits: a "
        "true clip layer is unusable with absolute positioning (see case-02 and "
        "technique-notes.md), and the element budget of 4096 caps generative density."),
    "unresolved_issues": [
        "Clip layers cannot be combined with absolute positioning in this build: nesting a "
        "Stack inside a clipped Container re-bases every child by the layer origin.",
        "The 4096-element cap limits procedurally dense sheets; workarounds are coarser "
        "scanlines and fewer motifs, which is a real constraint on generative density.",
        "Text inside a width-constrained Container still wraps rather than truncating, so "
        "every string is measured before placement by design.",
    ],
}

sc.write_json(os.path.join(OUT, "portfolio.json"), portfolio)

# ---------------------------------------------------------------- portfolio.md
md = ["# B03 · Twelve works exploring the Snapshot DSL creative frontier", "",
      f"Run `{RUN}` · task `{TASK}` · 12 independent finished works · pure DSL, no embedded "
      "images, no post-processing.", "",
      "Every `final.png` is the raw byte stream of a live HTTP 200 `image/png` response "
      "from `https://open-snapshot.muedsa.com/snapshot`; the matching `final.snapshot` is "
      "the exact text that produced it.", "",
      "## Curatorial logic", "",
      portfolio["curatorial_statement"], "",
      "## The works", "",
      "| # | Work | Structure | Size | DSL idea it proves |", "|---|---|---|---|---|"]
STRUCT = {
    "01": "time-space diagram (lanes × time)", "02": "single-day dual series + step table",
    "03": "specimen plate with two insets", "04": "character matrix / bitmap font",
    "05": "polar drum + helicorder", "06": "ranked bar matrix on a real dB scale",
    "07": "stitch chart with a key column", "08": "narrative spread (flat collage)",
    "09": "vertical CJK card with a timeline", "10": "music engraving + teaching grid",
    "11": "ornamental playbill", "12": "weekly multi-encoding matrix",
}
for c in cases:
    md.append(f"| {c['id'][-2:]} | {c['title']} | {STRUCT[c['id'][-2:]]} | "
              f"{c['dimensions'][0]}×{c['dimensions'][1]} | {c['dsl_capabilities'].split(',')[0]} |")
md += ["", "## How to read a work", "",
       "Each `case-NN/case.md` states audience, context, goal, content basis, visual intent, "
       "the DSL capabilities used, the completion criteria I set, the visual-review evidence, "
       "the rejected attempts kept in the temp directory, and any unresolved issue.", "",
       "## Fictional-content disclosure", "",
       "No work depicts a real client, organisation, dataset or measurement. Rail notices, "
       "bakery schedules, seismic events, sessions, samplers, recipes, plays, timetables and "
       "tide predictions are all invented demo content and are labelled as such on the sheet "
       "itself wherever a reader could mistake them for real data.", "",
       "## Review", "", portfolio["final_collection_review"], "",
       "## Known limits", ""]
for u in portfolio["unresolved_issues"]:
    md.append(f"- {u}")
with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(md) + "\n")

# ---------------------------------------------------------------- gallery.html
cards = []
for c in cases:
    w, h = c["dimensions"]
    cards.append(f"""  <figure class="card">
    <a href="{c['png']}"><img src="{c['png']}" alt="{c['title']}" loading="lazy"></a>
    <figcaption>
      <h2>{c['id']} · {c['title']}</h2>
      <p class="meta">{w}×{h} · {STRUCT[c['id'][-2:]]}</p>
      <p class="who"><strong>For</strong> {c['audience']}</p>
      <p class="who"><strong>Goal</strong> {c['user_goal']}</p>
      <p class="caps">{c['dsl_capabilities']}</p>
      <p class="links"><a href="{c['png']}">final.png</a> ·
         <a href="{c['snapshot']}">final.snapshot</a> ·
         <a href="{c['case_md']}">case.md</a></p>
    </figcaption>
  </figure>""")
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B03 · DSL creative frontier — 12 works</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:#0B1220; color:#E8EEF9;
         font:16px/1.55 ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif; }}
  header {{ padding:40px 32px 24px; border-bottom:1px solid #1E2C46; }}
  h1 {{ margin:0 0 8px; font-size:30px; letter-spacing:.2px; }}
  header p {{ margin:4px 0; color:#8FA3BF; max-width:110ch; }}
  main {{ display:grid; gap:28px; padding:32px;
          grid-template-columns:repeat(auto-fill,minmax(430px,1fr)); }}
  .card {{ margin:0; background:#0F172A; border:1px solid #1E2C46; border-radius:14px;
           overflow:hidden; display:flex; flex-direction:column; }}
  .card img {{ display:block; width:100%; height:auto; background:#070B14;
               border-bottom:1px solid #1E2C46; }}
  figcaption {{ padding:16px 18px 20px; }}
  h2 {{ margin:0 0 6px; font-size:17px; }}
  .meta {{ margin:0 0 10px; color:#7DD3FC; font:13px/1.4 ui-monospace,Menlo,Consolas,monospace; }}
  .who {{ margin:2px 0; color:#B9C7DA; font-size:14px; }}
  .caps {{ margin:10px 0 0; color:#8FA3BF; font-size:13px; }}
  .links {{ margin:12px 0 0; font:13px ui-monospace,Menlo,Consolas,monospace; }}
  a {{ color:#4FD1C5; }}
  footer {{ padding:8px 32px 48px; color:#7C8DA6; font-size:13px; }}
</style>
</head>
<body>
<header>
  <h1>B03 · Twelve works exploring the DSL creative frontier</h1>
  <p>Run {RUN}. Every image below is the raw bytes of a live 200 <code>image/png</code>
     response from the open-snapshot service, rendered from the linked
     <code>.snapshot</code> file. No photographs, no embedded bitmaps, no post-processing.</p>
  <p>All subjects, brands, people, places and numbers are invented demo content for a DSL
     study. Click any image to open it at full size.</p>
</header>
<main>
{chr(10).join(cards)}
</main>
<footer>12 independent works · relative links only · no remote scripts ·
  generated by scripts/portfolio.py</footer>
</body>
</html>
"""
with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(html)

# ---------------------------------------------------------------- metrics
req = sc.count_requests(TASK)
it = sc.count_iterations(TASK)
views = sum(1 for r in iters if r.get("viewed_at"))
kinds = {}
for r in iters:
    kinds[r.get("type", "?")] = kinds.get(r.get("type", "?"), 0) + 1
metrics = sc.build_metrics(
    TASK, title="用十件作品探索DSL的创意边界", status="completed",
    started_at="2026-10-03T12:51:26+08:00", ended_at="2026-10-03T13:15:24+08:00",
    outputs=["portfolio.json", "portfolio.md", "gallery.html", "technique-notes.md",
             "snapshot-usage.md", "task-metrics.json"] +
            [f"case-{c['no']}/final.png" for c in CASES] +
            [f"case-{c['no']}/final.snapshot" for c in CASES] +
            [f"case-{c['no']}/case.md" for c in CASES],
    cases=[{"id": f"case-{c['no']}", "title": c["title"], "version": c["ver"],
            "requests": len(requests_for(c["no"])), "dimensions": dims(c["no"])}
           for c in CASES],
    final_pngs=12, dsl_versions=len([f for f in os.listdir(os.path.join(TMP, "dsl"))
                                     if f.endswith(".snapshot")]),
    notes=["87 render requests, 8 of them rejected by the service and kept as evidence.",
           "12 final works; each has a same-name complete DSL.",
           "Probe renders are counted in the shared/other bucket of the same log."],
    extra={
        "final_case_count": 12,
        "image_views": views,
        "iteration_types": kinds,
        "presentation_dir": "outputs/%s/%s/case-01..case-12" % (RUN, TASK),
        "shared_preparation": {
            "requests": len([r for r in reqs if r["phase"] == "probe"]),
            "note": "12 probe requests produced the measured Transform rule, the text-width "
                    "model and the three service limits; they belong to no single case.",
        },
        "limits_discovered": [
            "request body max 1048576 bytes (413 REQUEST_TOO_LARGE)",
            "document max 4096 elements (400 RENDER_ERROR)",
            "render height max 4096 px (400 RENDER_ERROR)",
            "text width in a constrained Container wraps instead of truncating",
            "XML entities are NOT decoded; a bare & and > are accepted, < cannot be used",
            "a clipped Container re-bases absolute children by its own origin",
        ],
    })
sc.write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print(json.dumps({"cases": len(cases), "requests": req, "views": views,
                  "dsl_versions": metrics["dsl_versions"]}, ensure_ascii=False))
