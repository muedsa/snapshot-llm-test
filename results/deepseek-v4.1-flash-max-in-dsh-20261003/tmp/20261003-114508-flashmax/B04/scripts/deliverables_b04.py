"""deliverables_b04.py - sources.json, editorial-note.md, portfolio, gallery, metrics, logs."""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B04"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(TMP, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
import promote_b04 as P  # noqa: E402
import suite_common as sc  # noqa: E402
from PIL import Image  # noqa: E402

CASES = P.CASES
reqs = sc.read_jsonl(os.path.join(TMP, "requests.jsonl"))
state = json.load(open(os.path.join(ROOT, "outputs", RUN, "_suite", "suite-state.json"),
                       encoding="utf-8"))
b04 = next(t for t in state["tasks"] if t["id"] == "B04")

# ---------------------------------------------------------------- sources.json
SOURCES = [
    dict(id="S1", role="primary data",
         title="NASA Ozone Watch — Annual Records (Antarctic)",
         publisher="NASA Goddard Space Flight Center",
         url="https://ozonewatch.gsfc.nasa.gov/meteorology/annual_data.html",
         accessed_at="2026-10-03T14:40:00+08:00", http_status=200,
         retrieved="full annual table",
         used_by=["case-02", "case-03", "case-04"],
         what_it_gives="Maximum daily ozone-hole area (million km2) and minimum daily column "
                       "ozone (DU) for 1979-2025 with the dates they occurred, plus the "
                       "07 Sep - 13 Oct mean area and 21 Sep - 16 Oct mean minimum. The page "
                       "states there are no data for 1995 and asks users to credit 'NASA "
                       "Ozone Watch'.",
         credit_line="credit: NASA Ozone Watch",
         notes="Transcribed to tmp/.../B04/scripts/ozone.py; all derived statistics are "
               "computed from that transcription."),
    dict(id="S2", role="definition and mechanism",
         title="NASA Ozone Watch — What is the Ozone Hole?",
         publisher="NASA Goddard Space Flight Center",
         url="https://ozonewatch.gsfc.nasa.gov/facts/hole_SH.html",
         accessed_at="2026-10-03T14:42:00+08:00", http_status=200, retrieved="full page",
         used_by=["case-01", "case-03", "case-04", "case-05"],
         what_it_gives="The 220 DU threshold used to define the hole and why it is used "
                       "(values below it were not observed before 1979 and are known from "
                       "aircraft campaigns to result from chlorine- and bromine-catalysed "
                       "loss); the polar vortex, polar stratospheric cloud and catalytic "
                       "destruction mechanism.",
         credit_line="credit: NASA Ozone Watch", notes=""),
    dict(id="S3", role="context",
         title="NASA Ozone Watch — What is Ozone?",
         publisher="NASA Goddard Space Flight Center",
         url="https://ozonewatch.gsfc.nasa.gov/facts/SH.html",
         accessed_at="2026-10-03T14:43:00+08:00", http_status=200, retrieved="full page",
         used_by=["case-01", "case-05"],
         what_it_gives="90% of atmospheric ozone sits between about 10 and 50 km; total mass "
                       "about 3 billion tonnes = 0.00006% of the atmosphere; peak "
                       "concentration near 32 km; ozone screens all UV-C, most UV-B and only "
                       "about half of UV-A.",
         credit_line="credit: NASA Ozone Watch", notes=""),
    dict(id="S4", role="treaty outcomes and benefits",
         title="Facts and figures on ozone protection",
         publisher="UN Environment Programme, Ozone Secretariat",
         url="https://ozone.unep.org/facts-and-figures-ozone-protection",
         accessed_at="2026-10-03T14:46:00+08:00", http_status=200, retrieved="full page",
         used_by=["case-02", "case-06", "case-08", "case-09"],
         what_it_gives="198 Parties; nearly 100 controlled ODSs; 99% of ODSs phased out "
                       "(about 1.8 million ODP tonnes); return to 1980 column-ozone values "
                       "around 2066 (Antarctic), 2045 (Arctic), 2040 (60N-60S); upper-"
                       "stratosphere ozone +1.5-2.2% per decade at mid-latitudes and lower "
                       "tropical stratosphere -1-2% per decade (2000-2020); 135 Gt CO2-eq "
                       "avoided 1990-2010; 0.5-1 C avoided warming by mid-century; UV-B up to "
                       "a factor of five without the Protocol; UV index +10-20% below 50 "
                       "degrees latitude, +25% at the southern tip of South America, over "
                       "+100% at the South Pole in spring; US EPA figures of 443 million skin "
                       "cancer cases, 2.3 million deaths and 63 million cataract cases "
                       "prevented for people born 1890-2100; Multilateral Fund contributions "
                       "near US$5.1 billion as of May 2023; US$1.8 trillion health benefits "
                       "and about US$460 billion avoided damage 1987-2060; average warming "
                       "impact of 22 widely used HFCs about 2,500 times CO2; Kigali phases "
                       "down 18 HFCs by more than 80% in CO2-equivalent and avoids 0.3-0.5 C "
                       "by 2100.",
         credit_line="source: UNEP Ozone Secretariat",
         notes="The health and economic figures are that page's presentation of US EPA "
               "modelling and of cumulative benefit estimates; the sheets label them as "
               "modelled estimates."),
    dict(id="S5", role="peer-reviewed assessment",
         title="Scientific Assessment of Ozone Depletion: 2022 — Executive Summary",
         publisher="WMO/UNEP Scientific Assessment Panel, GAW Report No. 278 (hosted by NOAA "
                   "Chemical Sciences Laboratory)",
         url="https://www.csl.noaa.gov/assessments/ozone/2022/executivesummary/",
         accessed_at="2026-10-03T14:49:00+08:00", http_status=200,
         retrieved="executive summary and highlights",
         used_by=["case-02", "case-06", "case-07", "case-08", "case-10"],
         what_it_gives="Near-global (60S-60N) total column ozone +0.3% per decade over "
                       "1996-2020 with a 2-sigma uncertainty of at least +/-0.3; SH "
                       "mid-latitudes +0.8 +/- 0.7; NH mid-latitudes 0.0 +/- 0.7; tropics "
                       "+0.2 +/- 0.3; present-day column ozone still about 2%, 4% and 5% "
                       "below the 1964-1980 average for near-global, NH and SH mid-latitudes; "
                       "Antarctic springtime return to 1980 values about 2065, possibly about "
                       "2050 under low climate-mitigation scenarios; Arctic about 2045; NH "
                       "about 2035; near-global about 2040; unreported CFC-11 production over "
                       "2012-2019 estimated to delay polar return by up to 3 years and global "
                       "return by about 1 year; the CFC-11 / CFC-12 / other unexplained "
                       "emission findings; lower-stratosphere recovery not robust; observing "
                       "network gaps; dichloromethane depleting about 1 DU of annually "
                       "averaged global column ozone at current levels; a 3% N2O cut raising "
                       "global column ozone by about 0.5 DU; stratospheric aerosol injection "
                       "risks; HFC radiative forcing 0.044 W m-2 in 2020; HFC emissions in "
                       "2050 0.9-1.0 Gt CO2-eq/yr with Kigali versus 4.0-5.3 without; and the "
                       "chronology table ES-1 of policy decisions.",
         credit_line="source: WMO/UNEP Scientific Assessment of Ozone Depletion 2022",
         notes="The single most important source in this issue: the trend statements, the "
               "recovery years, the CFC-11 delay and the open-questions list all come from "
               "it."),
    dict(id="S6", role="treaty facts",
         title="The Kigali Amendment: An overview",
         publisher="UNEP Ozone Secretariat",
         url="https://ozone.unep.org/kigali-amendment-overview",
         accessed_at="2026-10-03T14:47:00+08:00", http_status=200, retrieved="full page",
         used_by=["case-06"],
         what_it_gives="Adopted 2016 and in force 1 January 2019; HFCs were about 2% of "
                       "global greenhouse-gas emissions and growing at over 10% per year "
                       "without controls; global HFC use expected to fall 80-85% by 2047; up "
                       "to 0.5 C avoided by 2100, potentially about 1 C with energy-"
                       "efficiency gains; more than 170 countries had ratified as of the "
                       "page (dated February 2026).",
         credit_line="source: UNEP Ozone Secretariat",
         notes="S4 (dated October 2024) says the Kigali Amendment had been ratified by over "
               "160 parties; S6 (February 2026) says more than 170. Where the two differ the "
               "sheet quotes the more recent page and gives its date."),
]

by_case = {}
for c in CASES:
    ids = [s.strip() for s in c["src"].split(",")]
    by_case[f"case-{c['no']}"] = {
        "sources": ids,
        "claims": c["data"],
        "illustrative_or_modelled": c["illus"],
        "credit_on_sheet": "yes — every work names its sources in the footer strip",
    }

sources = {
    "schema_version": 1,
    "task_id": TASK,
    "run_id": RUN,
    "topic": "The Antarctic ozone hole: what the 47-year record actually shows",
    "researched_on": "2026-10-03",
    "research_window": {"first_access": "2026-10-03T14:40:00+08:00",
                        "last_access": "2026-10-03T14:49:00+08:00"},
    "reader_question": "Is the ozone layer really recovering, and how would anyone know?",
    "sources": SOURCES,
    "per_work_citations": by_case,
    "not_used_and_why": [
        "No NOAA measurement-level CFC-11 emissions series was obtained, so case-07 quotes "
        "only the assessment's stated delays and plots no curve. It says so on the sheet.",
        "No monthly or daily ozone series was obtained, so nothing in this issue draws a "
        "within-season curve; the documented August-October cycle appears only as a labelled "
        "schematic in case-05's mechanism panels.",
        "No 2026 value is used: the NASA table ends at 2025 and its page was last updated "
        "2025-10-20.",
    ],
    "fictional_elements": [
        "Editorial furniture only: the masthead 'STRATOSPHERE REVIEW', 'ISSUE 07 · 2026' and "
        "'edited by R. Okonjo-Vale'. These are invented and are declared in "
        "editorial-note.md.",
        "No data, quotation, figure, name of a real person, or institutional claim on any "
        "sheet is invented.",
    ],
    "verification_method": "Every number printed on a B04 sheet is either (a) transcribed "
                           "from one of the six sources into scripts/ozone.py, (b) computed "
                           "from that transcription by the generator, or (c) a published "
                           "estimate quoted with its source and labelled as an estimate. "
                           "Derived quantities are labelled 'derived' on the artwork.",
}
sc.write_json(os.path.join(OUT, "sources.json"), sources)

# ---------------------------------------------------------------- editorial note
note = f"""# editorial-note.md — why this subject, and how it was edited

**Special issue title (invented furniture):** *Stratosphere Review · Issue 07 · 2026*
**Subject:** the Antarctic ozone hole, told through the published record rather than
through the usual "good news" summary.
**Reader:** an interested non-specialist who has heard that the ozone layer is recovering
and wants to know how anyone can tell — and what is still unresolved.

## Why this subject

It is the one large environmental problem with a measured before, a measured during, and a
measured after. The data is published annually by NASA, the trend statements are
peer-reviewed every four years, and the policy chronology is short enough to put on one
sheet. That combination lets a visual special do something a summary cannot: show the
reader the actual numbers, the actual uncertainty, and the gap between "the growth
stopped" and "the problem is over".

## The narrative route through the ten works

1. **What the hole is** — the definition first, because every later number depends on a
   threshold (220 DU) rather than on a picture.
2. **The 47-year record** — the headline series: it grew, it stopped growing around 2000,
   and it has been flat-with-noise since.
3. **Depth** — the same record through the other published metric, which does *not* peak in
   the same year as the area.
4. **One hole per year** — the calendar, to show that the season never moved and only the
   size did.
5. **Four stages** — the mechanism, so the calendar is not just a pattern.
6. **The treaty rail** — what was actually agreed, in the assessment's own chronology.
7. **The rogue emitter** — the CFC-11 episode, which is the strongest evidence that the
   monitoring *is* the enforcement.
8. **The climate side-effect** — what the treaty did about warming as a by-product, with
   the counterfactual named.
9. **The health ledger** — the largest and softest numbers in the issue, labelled as
   modelled estimates.
10. **What is still open** — six items the 2022 assessment does not settle, so the issue
    cannot be read as a completion notice.

## Editorial rules applied to every sheet

- **Provenance is on the artwork, not only in the metadata.** Every work carries a footer
  naming the sources it used and what was computed rather than measured.
- **Derived quantities are labelled.** The depth bars in work 03 are 220 DU minus a
  published minimum; the five-year means in works 02 and 03 are computed here. Both say so.
- **Schematic is not data.** Works 01 and 05 contain labelled schematics. Their captions
  and footers state that no measured value is plotted.
- **Estimates are called estimates.** Works 08 and 09 print published modelled estimates
  and label them as such at the same size as the figures.
- **No figure was improved for effect.** Where a source gives a range (0.5–1 °C, 0.3–0.5 °C,
  1.5–2.2% per decade), the range is printed rather than a midpoint.
- **What could not be verified is stated.** Work 07 prints a box headed "what this sheet
  does not show", naming the data it would have needed.

## Declared fictional elements

The masthead name, the issue number and the editor byline are invented cover furniture for
a study exercise. Nothing else on any sheet is invented: no data point, no quotation, no
measurement, no institutional claim and no person's name.

## Limitations of this issue

- Only six sources were read, all of them secondary compilations or assessment summaries;
  the underlying satellite and ground-station data were not analysed.
- The issue covers the Antarctic record only. The Arctic is mentioned only where the
  sources compare the two.
- Two works carry numbers sourced from a Secretariat page dated October 2024 (the party
  counts); a more recent Secretariat page differs on the Kigali count, and both are recorded
  in `sources.json`.
"""
with open(os.path.join(OUT, "editorial-note.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(note)

# ---------------------------------------------------------------- portfolio
def dims(no):
    with Image.open(os.path.join(OUT, f"case-{no}", "final.png")) as im:
        return [im.width, im.height]


cases = []
for c in CASES:
    ids = [r["request_id"] for r in reqs
           if (r.get("request_file") or "").replace("\\", "/").endswith(
               f"case-{c['no']}.snapshot")]
    cases.append({
        "id": f"case-{c['no']}",
        "title": c["title"],
        "figure": f"FIG. {c['fig']}",
        "audience": "Interested general reader and science-literate professional",
        "use_context": "A ten-page visual special: screen at full width and print at A3",
        "user_goal": c["q"],
        "content_basis": c["data"],
        "visual_intent": c["struct"],
        "png": f"case-{c['no']}/final.png",
        "snapshot": f"case-{c['no']}/final.snapshot",
        "case_md": f"case-{c['no']}/case.md",
        "dimensions": dims(c["no"]),
        "dsl_capabilities": "flat absolute Stack layout, rotated-bar geometry, area fills, "
                            "computed scales, measured text fitting, source footer strip",
        "completion_criteria": "every printed figure traceable to a cited source or labelled "
                               "derived/illustrative; no label collision or clipping; the "
                               "chart scale honest (no truncated axes)",
        "visual_review": c["review"],
        "request_ids": ids,
        "iteration_ids": [f"B04-IT-{i:03d}" for i in range(1, 30)
                          if i in []] or [c["ver"]],
        "supporting_assets": [],
        "sources": [s.strip() for s in c["src"].split(",")],
        "illustrative_or_modelled": c["illus"],
        "unresolved_issues": [],
    })

portfolio = {
    "schema_version": 1,
    "task_id": TASK,
    "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets (creative track) — no supporting "
                    "assets were used; every work is pure DSL",
    "curatorial_statement":
        "Ten works about one real subject, edited so that each answers a different question a "
        "reader would actually ask: what counts as the hole, did it stop growing, how deep is "
        "it, did the season move, why there, what was agreed, what happens when a banned gas "
        "comes back, what did it do for the climate, what did it prevent, and what is still "
        "open. The style is deliberately unified — one masthead, one palette family, one "
        "source-footer convention — because this is a single issue of one publication, and "
        "the independence that matters here is independence of question and of chart form, "
        "not of look. The ten structures are: annotated cross-section, column chart with a "
        "treaty rail, plumb-line depth chart on an inverted axis, calendar strip matrix, "
        "four-panel process strip, alternating chronology, case file, paired-claim ledger, "
        "cost/benefit ledger with big-number panels, and an uncertainty ledger.",
    "case_field_guide": {
        "sources": "ids resolved in sources.json",
        "illustrative_or_modelled": "what on this sheet is not a measurement",
        "visual_review": "what was seen and changed after looking at the render",
    },
    "cases": cases,
    "final_collection_review":
        "Reviewed all ten at full size and as a contact sheet. Every figure printed was "
        "checked against scripts/ozone.py or the source notes in research/ before the sheet "
        "was accepted. Defects found and fixed after looking: a broken radial calendar "
        "(case-04 v1), a picket-fence polyline (case-03 v1-v2), a masthead standfirst "
        "overprinted by the kicker (case-02 v1, shared helper fix), a clipped list label "
        "(case-02 v2), annotation boxes over the header (case-02 v1), unit labels colliding "
        "with their values (case-06 v1), benefit labels running off the canvas (case-09 "
        "v1-v2), implied-but-meaningless bar scales (case-08 v1) and two half-empty canvases "
        "(case-06, case-07). Known limits: only six secondary sources were read, the Arctic "
        "is covered only where the sources compare it, and the CFC-11 episode is reported "
        "without its emissions series.",
    "unresolved_issues": [
        "No measurement-level CFC-11 series was obtained, so that episode is reported "
        "qualitatively with only the assessment's delay estimates as numbers.",
        "The Kigali party count differs between two Secretariat pages (over 160 as of "
        "October 2024; more than 170 as of February 2026); the newer figure is printed and "
        "the discrepancy is recorded in sources.json.",
        "Arctic ozone is covered only where the sources compare it with the Antarctic; no "
        "Arctic-specific chart is drawn.",
    ],
}
sc.write_json(os.path.join(OUT, "portfolio.json"), portfolio)

# ---------------------------------------------------------------- gallery
cards = []
for c in cases:
    w, h = c["dimensions"]
    cards.append(f"""  <figure class="card">
    <a href="{c['png']}"><img src="{c['png']}" alt="{c['title']}" loading="lazy"></a>
    <figcaption>
      <h2>{c['figure']} · {c['title']}</h2>
      <p class="meta">{w}×{h} · {c['visual_intent']}</p>
      <p class="who"><strong>Question</strong> {c['user_goal']}</p>
      <p class="src"><strong>Sources</strong> {', '.join(c['sources'])}</p>
      <p class="mod"><strong>Not measured</strong> {c['illustrative_or_modelled']}</p>
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
<title>B04 · The Antarctic ozone hole — 10 works</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:#0B1226; color:#E9EFF9;
         font:16px/1.55 ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif; }}
  header {{ padding:40px 32px 24px; border-bottom:1px solid #25375F; }}
  h1 {{ margin:0 0 8px; font-size:30px; }}
  header p {{ margin:4px 0; color:#9FB0CC; max-width:110ch; }}
  .rule {{ color:#7C6BF0; font-weight:700; }}
  main {{ display:grid; gap:28px; padding:32px;
          grid-template-columns:repeat(auto-fill,minmax(460px,1fr)); }}
  .card {{ margin:0; background:#16264A; border:1px solid #25375F; border-radius:14px;
           overflow:hidden; display:flex; flex-direction:column; }}
  .card img {{ display:block; width:100%; height:auto; background:#0B1226;
               border-bottom:1px solid #25375F; }}
  figcaption {{ padding:16px 18px 20px; }}
  h2 {{ margin:0 0 6px; font-size:17px; }}
  .meta {{ margin:0 0 10px; color:#38BDF8; font:13px/1.4 ui-monospace,Menlo,Consolas,monospace; }}
  .who, .src, .mod {{ margin:3px 0; color:#B9C7DE; font-size:13.5px; }}
  .mod {{ color:#F5A524; }}
  .links {{ margin:12px 0 0; font:13px ui-monospace,Menlo,Consolas,monospace; }}
  a {{ color:#7C6BF0; }}
  footer {{ padding:8px 32px 48px; color:#8FA0BC; font-size:13px; }}
</style>
</head>
<body>
<header>
  <h1>B04 · The Antarctic ozone hole: what the 47-year record actually shows</h1>
  <p><span class="rule">STRATOSPHERE REVIEW · ISSUE 07 · 2026</span> — a ten-work visual
     special. Every image is the raw bytes of a live 200 <code>image/png</code> response
     rendered from the linked <code>.snapshot</code>; no embedded bitmaps, no
     post-processing.</p>
  <p>Every number printed on these sheets is transcribed from a cited source or computed
     from it. Sources are named in each sheet's footer and recorded in full in
     <a href="sources.json">sources.json</a>; modelled and illustrative elements are
     labelled on the artwork itself. The masthead name, issue number and editor byline are
     the only invented elements, declared in <a href="editorial-note.md">editorial-note.md</a>.</p>
</header>
<main>
{chr(10).join(cards)}
</main>
<footer>10 works · relative links only, no remote scripts · generated by
  scripts/deliverables_b04.py</footer>
</body>
</html>
"""
with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(html)

# ---------------------------------------------------------------- metrics
req = sc.count_requests(TASK)
metrics = sc.build_metrics(
    TASK, title="自主研究一个真实主题并制作十件视觉特辑", status="completed",
    started_at=b04["started_at"], ended_at=b04["ended_at"] or sc.now(),
    outputs=["portfolio.json", "portfolio.md", "gallery.html", "sources.json",
             "editorial-note.md", "snapshot-usage.md", "task-metrics.json"] +
            [f"case-{c['no']}/final.png" for c in CASES] +
            [f"case-{c['no']}/final.snapshot" for c in CASES] +
            [f"case-{c['no']}/case.md" for c in CASES],
    cases=[{"id": f"case-{c['no']}", "title": c["title"], "version": c["ver"],
            "requests": len([r for r in reqs if (r.get("request_file") or "")
                             .replace("\\", "/").endswith(f"case-{c['no']}.snapshot")]),
            "dimensions": c["size"], "sources": c["src"]} for c in CASES],
    final_pngs=10, rounds=None,
    dsl_versions=len([f for f in os.listdir(os.path.join(TMP, "dsl"))
                      if f.endswith(".snapshot")]),
    notes=["Real research: six sources fetched and read (NASA Ozone Watch ×3, UNEP Ozone "
           "Secretariat ×2, WMO/UNEP 2022 assessment), all recorded in sources.json with "
           "access times and HTTP status.",
           "Every figure is sourced, computed from a source, or explicitly labelled as an "
           "estimate or schematic on the artwork.",
           "10 final works; each has a same-name complete DSL and raw service bytes."],
    extra={
        "final_case_count": 10,
        "shared_preparation": {
            "sources_read": 6,
            "note": "Research and the dataset transcription (scripts/ozone.py) are shared "
                    "across all ten works and are not counted as any single case's work.",
        },
        "research": {
            "sources": [s["id"] for s in SOURCES],
            "file": "outputs/%s/%s/sources.json" % (RUN, TASK),
            "accessed": "2026-10-03",
        },
        "limits_discovered": [
            "4096 elements per document (guarded locally before every render)",
            "1 MiB request body",
            "4096 px maximum render height",
            "XML entities are not decoded; `<` needs CDATA, `&` and `>` print verbatim",
        ],
    })
sc.write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("cases", len(cases), "requests", req["render_requests"],
      "success", req["render_success"], "failed", req["render_failed"])
