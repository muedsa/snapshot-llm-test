"""promote_b04.py - copy B04's finals into outputs and write each case.md."""
from __future__ import annotations

import json
import os
import shutil

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B04"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)

CASES = [
    dict(no="01", ver="v1", title="What the hole is", size=(1240, 1754), fig="01",
         q="What actually counts as the ozone hole?",
         struct="annotated atmospheric cross-section + definition panels",
         data="220 DU threshold, 90% of ozone between 10 and 50 km, 3 billion tonnes, "
              "peak near 32 km (NASA Ozone Watch)",
         illus="the cross-section profile, altitudes and vortex are labelled schematics",
         src="S2, S3",
         review="v1 accepted on first look; the only fix was making the masthead wrap its "
                "standfirst so the kicker could not be overprinted (shared helper change)"),
    dict(no="02", ver="v3", title="The 47-year record", size=(1900, 1180), fig="02",
         q="Did the hole stop growing?",
         struct="46-column chart with a five-year trailing mean and a treaty rail",
         data="maximum daily hole area for every year 1979-2025 from NASA Ozone Watch; "
              "5-year mean computed here; 2000-2025 mean as a reference rule",
         illus="none — every plotted value is published",
         src="S1, S4",
         review="v1 lost the end of its standfirst under the kicker and put the 2000 callout "
                "over the header; v2 moved it and fixed the clipped mean label; v3 moved the "
                "amber legend into the plot and stopped the 1995 tick colliding with the gap "
                "label"),
    dict(no="03", ver="v4", title="Depth", size=(1800, 1140), fig="03",
         q="How little ozone is left inside the hole?",
         struct="plumb lines hanging from the 220 DU threshold, inverted axis",
         data="annual minimum daily column ozone 1979-2025; bar length is 220 DU minus that "
              "value, computed here and labelled as derived",
         illus="none — inputs are published, the derived quantity is stated on the sheet",
         src="S1, S2",
         review="v1 and v2 plotted the raw minimum as a polyline, which read as a picket "
                "fence; v3 switched to the plumb-line encoding; v4 fixed the threshold label "
                "collision and drew the threshold rule after the bars so it stays visible"),
    dict(no="04", ver="v5", title="One hole per year", size=(1700, 1480), fig="04",
         q="Did the season move, or only the size?",
         struct="calendar strip: one row per year, marker at the peak date, bar for the peak "
                "area",
         data="published peak date and peak area for every year; the 07 Sep - 13 Oct "
              "averaging window named in the source table",
         illus="none in the plot",
         src="S1, S2",
         review="v1 was a radial calendar that failed on sight (arcs clustered in one "
                "quadrant, month spokes read as stray lines, the schematic profile looked "
                "like a caterpillar); v2 rebuilt it as a strip but overflowed the canvas and "
                "put the 1995 gap row on top of 1994; v3-v5 fixed the row model, restored "
                "the averaging band and gave the footer room"),
    dict(no="05", ver="v1", title="Four stages", size=(1880, 1080), fig="05",
         q="Why does this happen over one pole, in one season?",
         struct="four-panel process strip, identical geometry in every panel",
         data="the mechanism as described by NASA Ozone Watch; no measured values",
         illus="all four panels are labelled schematics; no temperature or count is data",
         src="S2, S3",
         review="v1 accepted; panels, chips and the Antarctic-versus-Arctic note read "
                "cleanly at full size"),
    dict(no="06", ver="v2", title="The treaty rail", size=(1880, 940), fig="06",
         q="What was actually agreed, and in what order?",
         struct="horizontal chronology with alternating decision cards + outcome strip",
         data="the eight policy decisions in the WMO/UNEP 2022 chronology table; outcome "
              "figures from the Ozone Secretariat",
         illus="none",
         src="S5, S4, S6",
         review="v1 had the unit label overlapping the value in two panel ('~100ODSs', "
                "'>80%') because the unit was positioned from a width estimate; v2 widened "
                "the gap in the shared panel helper and trimmed the canvas"),
    dict(no="07", ver="v2", title="The rogue emitter", size=(1360, 1310), fig="07",
         q="What happened when a banned gas stopped falling?",
         struct="case file: finding, cost, what it demonstrates, what is not shown",
         data="the 2022 assessment's own statements and its published delay estimates (up to "
              "3 years polar, about 1 year global)",
         illus="no series is plotted; the sheet says so explicitly",
         src="S5",
         review="v1 had a truncated note and a half-empty canvas; v2 shortened the note and "
                "cut the sheet height"),
    dict(no="08", ver="v2", title="The climate side-effect", size=(1840, 1120), fig="08",
         q="What did an ozone treaty do about warming?",
         struct="four paired claims with the counterfactual named beneath",
         data="0.5-1 C avoided by mid-century; 135 Gt CO2-eq avoided 1990-2010; Kigali "
              "0.3-0.5 C by 2100, about 1 C with efficiency",
         illus="all four are published estimates, labelled 'published estimate' on the sheet",
         src="S4, S5",
         review="v1 drew a fixed-length rule under each value, which implied a shared scale "
                "across degrees and gigatonnes; v2 removed it and used a labelled chip "
                "instead, and the sheet now states why no bar is drawn"),
    dict(no="09", ver="v3", title="The health ledger", size=(1600, 1150), fig="09",
         q="What is the treaty credited with preventing?",
         struct="ledger: three modelled health totals, then cost against benefit",
         data="US EPA modelling as reported by the Secretariat: 443 M skin-cancer cases, "
              "2.3 M deaths, 63 M cataracts; US$5.1 bn fund; US$1.8 tn and US$460 bn "
              "benefits",
         illus="every figure is a model result and the sheet says so in its own panel",
         src="S4",
         review="v1 let the benefit labels run off the right edge and left half the canvas "
                "empty; v2 shortened them; v3 narrowed the bars so the labels fit, and added "
                "the note that the cost bar is 2 px long at this scale"),
    dict(no="10", ver="v1", title="What is still open", size=(1840, 1180), fig="10",
         q="What does the assessment still not settle?",
         struct="six-item uncertainty ledger with editorial confidence chips",
         data="the 2022 assessment's own list of current scientific and policy challenges",
         illus="the confidence labels are this sheet's reading of the assessment's firmness; "
               "the sheet says so",
         src="S5",
         review="v1 accepted; the ledger, chips and closing statement read cleanly"),
]


def main():
    for c in CASES:
        png = os.path.join(TMP, "renders", f"case-{c['no']}.{c['ver']}.png")
        dsl = os.path.join(TMP, "dsl", f"case-{c['no']}.{c['ver']}.snapshot")
        with open(png, "rb") as fh:
            assert fh.read(8) == b"\x89PNG\r\n\x1a\n", png
        cdir = os.path.join(OUT, f"case-{c['no']}")
        os.makedirs(cdir, exist_ok=True)
        shutil.copyfile(png, os.path.join(cdir, "final.png"))
        shutil.copyfile(dsl, os.path.join(cdir, "final.snapshot"))
        fails = sorted(f for f in os.listdir(os.path.join(TMP, "renders"))
                       if f.startswith(f"case-{c['no']}.") and f.endswith(".failed.txt"))
        md = [
            f"# case-{c['no']} · {c['title']}", "",
            f"**Reader question this work answers**: {c['q']}", "",
            f"- **Final render**: `final.png`, raw bytes of a 200 `image/png` response, from "
            f"`tmp/{RUN}/{TASK}/renders/case-{c['no']}.{c['ver']}.png`",
            f"- **DSL**: `final.snapshot` — version `{c['ver']}`, complete and "
            f"self-contained, no embedded images",
            f"- **Structure**: {c['struct']}",
            f"- **Reported size**: {c['size'][0]}×{c['size'][1]} px",
            f"- **Data basis**: {c['data']}",
            f"- **Illustrative or modelled elements**: {c['illus']}",
            f"- **Sources cited on the sheet**: {c['src']} (full records in "
            f"`../sources.json`)",
            f"- **Visual review**: {c['review']}",
            f"- **Rejected attempts kept**: "
            + (", ".join(f"`{f}`" for f in fails) if fails else "none"),
            f"- **Fictional content**: the only invented elements are the special's "
            f"masthead name, issue number and editor byline, both declared in "
            f"`../editorial-note.md`. No data, quote or figure on this sheet is invented: "
            f"every number is either transcribed from the cited source or computed from it "
            f"in `scripts/ozone.py`, and derived quantities are labelled as derived.",
            f"- **Supporting assets**: none. The artwork is pure DSL.",
        ]
        with open(os.path.join(cdir, "case.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(md) + "\n")
        print("promoted", c["no"], c["ver"], os.path.getsize(os.path.join(cdir, "final.png")))


if __name__ == "__main__":
    main()
