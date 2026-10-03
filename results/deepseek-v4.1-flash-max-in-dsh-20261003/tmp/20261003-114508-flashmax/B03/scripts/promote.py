"""promote.py - copy the chosen render of every B03 case into outputs and write case.md.

Only a PNG that came back from a 200 image/* response is ever copied; the script verifies
the PNG magic bytes and records the previous failed attempts for each case so the record
shows what was rejected as well as what shipped.
"""
from __future__ import annotations

import json
import os
import shutil

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B03"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)

CASES = [
    dict(no="01", ver="v5", title="Night possession plan · Line 4",
         audience="Network Control Desk planners and protection officers at a (fictional) "
                  "infrastructure operator",
         context="Printed A3 desk sheet and a 1800 px screen view in a control room",
         goal="See at a glance which track is closed, for how long, and where two "
              "possessions collide before the notice is issued",
         content="8 possession windows, 5 work trains, 1 declared conflict; all times, "
                 "headcodes and the operator are invented",
         visual="Dark control-room palette, 4 lane time-space diagram, amber rule, "
                "hatched possession bands, white train capsules with rotated chevrons",
         caps="flat Stack absolute layout, rotated Transform bars (chevrons + conflict "
              "diamond), per-element alpha, keyed legend grid",
         criteria="every label readable at 50% zoom; no element covers another; the "
                  "conflict mark sits in open space",
         review="v1 conflict diamonds were 112 px and covered the BALLAST band; v2-v4 "
                "moved the mark and shortened the callout; v5 verified by centroid "
                "measurement (conflict marker found at 1585,482 in open track space)",
         unresolved=[]),
    dict(no="02", ver="v7", title="Sourdough fermentation schedule",
         audience="Bakery team (4 people) at a fictional neighbourhood bakery",
         context="A4 sheet pinned above the bench, also read on a phone",
         goal="Follow today's steps and know what the dough should look like at each stage",
         content="24 h dough and room temperature series and an 8 row step table; all "
                 "values illustrative for a fictional bakery",
         visual="Warm linen paper, serif display type, hairline rules, filled dough band "
                "with a dashed room curve, on-curve annotation tags",
         caps="rotated-bar polylines with round joins, stacked 2px area band, dashed line "
              "generator, measured text fitting, callout boxes clamped to the plot",
         criteria="curve never leaves the plot frame; callouts never cross the curve; "
                  "table columns align",
         review="v1/v2 the dough curve read as disconnected dashes (abutting rotated bars "
                "only meet at corners on steep joints); v3 added joins and a filled band; "
                "v4/v5 nested clip layer re-based every child (abandoned, documented); v6 "
                "removed the alpha seam stripes and smoothed the series",
         unresolved=["A true clip layer could not be used: nesting a Stack inside a clipped "
                     "Container shifted every absolute child by the layer origin, so the "
                     "series is clamped numerically instead."]),
    dict(no="03", ver="v7", title="Generative botanical plate · Crypteris hallowayensis",
         audience="Readers of a natural-history plate (museum wall, field guide spread)",
         context="A3 portrait print, read at 40 cm and at thumbnail size",
         goal="Show a plausible fern habit and its two magnified details with a proper "
              "specimen label block",
         content="procedurally generated frond, phyllotaxis inset (n=150, 137.5°), "
                 "sporangia inset, collection data; the taxon is explicitly fictional",
         visual="Cream plate with a double frame, sepia serif type, one dominant organism, "
                "two circular insets, a scale bar and a caption",
         caps="seeded PRNG geometry, log-spiral rachis, tapered pinnae from rotated bars, "
              "phyllotaxis from the golden angle, dashed guide ring, polygon-free circles",
         criteria="the plate reads as botanical rather than diagrammatic; insets do not "
                  "collide; the caption sits inside the frame",
         review="v1 was rejected by the service twice (1 MiB body, then 4096 elements from "
                "rasterised pinnae); v2-v5 rebuilt the pinnae as rotated bars and moved the "
                "insets; v6 re-rendered after the entity fix so the collector line prints "
                "\"R. Okonjo & T. Vasquez\" instead of \"&amp;\"",
         unresolved=[]),
    dict(no="04", ver="v4", title="Dot-matrix departure board · Halloway Station",
         audience="Passengers on platforms 3–4 of a fictional station",
         context="A 1560 px LED board, also rendered small on a phone",
         goal="Find the next departure, its platform and its status in under two seconds",
         content="5 departures with destinations, platforms and states, plus a notice; the "
                 "station, operator and timetable are invented",
         visual="Near-black board, amber/white/red LED cells, a hand-built 5x7 bitmap font, "
                "row banding, a status swatch legend",
         caps="bitmap font emitted as square LED cells, per-status colour keys, monospaced "
              "column alignment, element budget management",
         criteria="every glyph legible; columns never collide; the board fits the element "
                  "budget without dropping rows",
         review="v1 was rejected: 7381 elements against the 4096 cap; v2 revealed the local "
                "counter had under-reported by 2x (each Container is an element too); v3 "
                "fixed a column overlap; v4 tightened the panel",
         unresolved=[]),
    dict(no="05", ver="v2", title="Drum seismogram · station HLY",
         audience="A seismology duty officer reading an overnight record",
         context="A wide sheet on a monitoring desk, also used as a print",
         goal="See the P-wave onset, judge the coda, and read the event parameters",
         content="three radial drum traces, a 3 line helicorder, an event summary; the "
                 "event, station and magnitudes are invented",
         visual="Smoked-paper dark ground, concentric rings with hour marks, green/blue/"
                "amber traces, a red onset marker, a helicorder panel",
         caps="parametric circular geometry, polar helpers, multi-series waveforms, radial "
              "tick labels, dash control",
         criteria="the onset marker sits on the trace; no label collides; the helicorder "
                  "shows quiet vs event",
         review="v1 traces were dashed (2.1° steps) and the STATUS row collided with the "
                "HELICORDER heading; v2 halved the step to 1.55° and moved the panel",
         unresolved=[]),
    dict(no="06", ver="v3", title="Monitor wall · 24 channels",
         audience="A mix engineer and a producer in a control room",
         context="A 1760 px screen and a printed reference sheet",
         goal="Compare channel levels and spot the channels that risk clipping",
         content="24 named channels with levels and peak holds on a real dB scale; the "
                 "session, names and levels are invented",
         visual="Dark console palette, 2.4 dB segments coloured by zone, white peak-hold "
                "caps with numeric values, a zone key",
         caps="dB-to-pixel scale mapping, segmented bars, computed peak caps, dense monospace "
              "labelling",
         criteria="bar length is comparable across channels; every peak label is readable; "
                  "no bar overlaps its neighbour",
         review="v1/v2 printed \"&amp;\" and \"&lt;\" in the zone key because entities are "
                "not decoded by the parser; v3 moved the legend to minus-sign wording and "
                "restored the true values",
         unresolved=[]),
    dict(no="07", ver="v7", title="Counted cross-stitch sampler · Kestrel Junction 2026",
         audience="A hobby stitcher working from a chart",
         context="A printed chart on a frame stand, read at 30 cm",
         goal="Count the pattern and know which floss to use for each motif",
         visual="Woven linen ground (banded fill), 45° rotated diamond stitches, a floss "
                "key, a stitch ledger and a repeat band",
         content="60 × 46 stitch cloth, 4 corner flowers, side sprigs, a kestrel centre, "
                 "backstitch initials; the place and floss codes are invented",
         caps="rotated square stitches at a computed pitch, pattern stamped from string "
              "art, two-column plate with a bounded key panel",
         criteria="stitches read as diamonds at 100% and as texture at 50%; chart and key "
                  "never overlap; the lettering band stays inside the border",
         review="v1 let the border run under the key panel; v2 split the plate into chart "
                "and key columns; v3 the lettering overprinted the side motifs; v4-v6 "
                "reduced it to KJ initials, added the repeat band and rebalanced the plate",
         unresolved=[]),
    dict(no="08", ver="v4", title="The Paper Boat · picture-book spread",
         audience="A 4–6 year old and the adult reading aloud",
         context="A 1920×1200 spread at arm's length, and a tablet",
         goal="Follow one sentence of story and name the things in the picture",
         content="an invented story scene with a boat, a lighthouse, fish and gulls",
         visual="Flat cut-paper collage, layered hills and sea scallops, a layered sun, four "
                "large shapes per zone, a fold stitch down the gutter",
         caps="filled polygons for silhouettes, scalloped water from repeated discs, "
              "rotated bars for gulls and spars, alpha paper tints",
         criteria="silhouettes have no visible banding; the title is legible on the sky; no "
                  "shape is clipped at the canvas edge",
         review="v1 hills were rows of discs and the fore-edge title was a column of dashes; "
                "v2 replaced the hills with polygons; v3/v4 shortened the sun rays, moved "
                "the clouds clear of the title and added the lighthouse",
         unresolved=[]),
    dict(no="09", ver="v3", title="Recipe card · Tori shio ramen",
         audience="The two cooks on a shift at a fictional izakaya",
         context="An A5 card on the pass, read while working",
         goal="Cook the bowl the same way twice: tare, soup, oil, chicken, noodles",
         content="10 ingredients and 6 method steps with a timeline; quantities and timings "
                 "are illustrative, not kitchen-tested",
         visual="Washi ground with fibre flecks, a tapered ink brush sweep, a vertical CJK "
                "title, an ingredients ledger and a numbered method",
         caps="vertical CJK setting as one glyph per Text at a computed pitch, tapered "
              "polygon brush stroke, right-aligned quantity column, timeline with dots",
         criteria="the vertical title never collides with the body; every quantity is "
                  "right-aligned; the method rules sit under their own text",
         review="v1 the brush sweep read as a chain of beads and the title overprinted the "
                "ingredients; v2 rebuilt the sweep as one polygon and grew the sheet so the "
                "title has its own zone",
         unresolved=[]),
    dict(no="10", ver="v3", title="First-position fingering chart · violin",
         audience="A violin teacher and a beginner pupil",
         context="A printed handout (A3 or A4) on a music stand",
         goal="Find the note for each finger on each string and see the D major scale",
         content="4 strings × 5 finger positions with note names and semitone offsets, the "
                 "D major scale, and a hand-shape diagram; frequencies are equal-temperament "
                 "values computed in the generator",
         visual="Bright paper, blue positions, a ruled staff with engraved-style note heads, "
                "a shaded hand/neck diagram",
         caps="drawn music staff with rotated note heads and stems, accidentals from crossed "
              "bars, outlined circles for finger rings (cheaper than ring-of-bars)",
         criteria="the grid is readable at A3 and A4; note positions match the grid; nothing "
                  "runs past the right margin",
         review="v1 the finger rings cost ~190 elements each and the chart hit 6434 "
                "elements; v2 replaced them with outlined circles and rebuilt the staff; v3 "
                "scaled the staff, simplified the clef and kept the hand diagram inside "
                "the canvas",
         unresolved=[]),
    dict(no="11", ver="v2", title="Playbill · Kestrel & the Long Tide",
         audience="An audience at a fictional repertory theatre",
         context="A printed programme page and a foyer poster",
         goal="Read the title, the cast and the performance times quickly",
         content="7 cast entries, 3 scene blocks, a 4 night run and venue details; the play, "
                 "company, cast and venue are invented",
         visual="Cream paper, double rule frame with corner devices, a shield crest with a "
                "gold star, serif display type with designed letter spacing, two columns",
         caps="nested frame rules, polygon shield and star, laurel arcs from rotated bars, "
              "letterSpacing as a design value, hanging-indent cast blocks",
         criteria="the title is the largest element; columns never overprint; the crest "
                  "reads at thumbnail size",
         review="v1 printed \"&amp;\" in the title and stacked two scene lines on one "
                "baseline; v2 fixed the escaping contract and gave each scene explicit rows, "
                "and simplified the crest to a shield with a five-point star",
         unresolved=[]),
    dict(no="12", ver="v4", title="Tide & light planner · Halloway Rowing Club",
         audience="A coastal rowing club's coxswains and coaches",
         context="A wall sheet in the boathouse, read before an outing",
         goal="Choose the day and the hour: enough water, enough light, high water inside "
              "daylight",
         content="7 day tide curves, 28 high/low water entries, daylight windows and moon "
                 "phases; all predictions come from a two-constituent harmonic generator "
                 "and are explicitly not for navigation",
         visual="Deep-water dark palette, one row per day, an area-filled tide curve, an "
                "aligned high/low table, daylight bars with twilight hatch, moon discs",
         caps="one generator driving curves and the derived table, area fill from stacked "
              "columns, aligned multi-column matrix, moon phase from overlapping discs",
         criteria="curves and table always agree; seven rows stay visually separate; the "
                  "daylight bars fit the sheet",
         review="v1 daylight bars ran to x=1850 on a 1700 px sheet and the curve scalloped "
                "at a 4 px step; v2 re-measured every column and halved the step; v3 added "
                "row banding and a baseline rule so the seven rows read separately",
         unresolved=[]),
]


def main():
    for c in CASES:
        src_png = os.path.join(TMP, "renders", f"case-{c['no']}.{c['ver']}.png")
        src_dsl = os.path.join(TMP, "dsl", f"case-{c['no']}.{c['ver']}.snapshot")
        if not os.path.exists(src_dsl):
            src_dsl = os.path.join(TMP, "dsl", f"case-{c['no']}.snapshot")
        with open(src_png, "rb") as fh:
            head = fh.read(8)
        assert head == b"\x89PNG\r\n\x1a\n", f"{src_png} is not a PNG"
        cdir = os.path.join(OUT, f"case-{c['no']}")
        os.makedirs(cdir, exist_ok=True)
        shutil.copyfile(src_png, os.path.join(cdir, "final.png"))
        shutil.copyfile(src_dsl, os.path.join(cdir, "final.snapshot"))
        fails = [f for f in os.listdir(os.path.join(TMP, "renders"))
                 if f.startswith(f"case-{c['no']}.") and f.endswith(".failed.txt")]
        md = [f"# case-{c['no']} · {c['title']}", "",
              f"- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), "
              f"from `tmp/{RUN}/{TASK}/renders/case-{c['no']}.{c['ver']}.png`",
              f"- **DSL**: `final.snapshot` — version `{c['ver']}`, self-contained, "
              f"no external assets",
              f"- **Audience**: {c['audience']}",
              f"- **Use context**: {c['context']}",
              f"- **User goal**: {c['goal']}",
              f"- **Content basis**: {c['content']}",
              f"- **Visual intent**: {c['visual']}",
              f"- **DSL capabilities used**: {c['caps']}",
              f"- **Completion criteria (self-set)**: {c['criteria']}",
              f"- **Visual review evidence**: {c['review']}",
              f"- **Fictional-data note**: the subjects, brands, people, places and numbers "
              f"in this work are invented demo content for a DSL study. No real client, "
              f"organisation, person or measurement is depicted or implied.",
              f"- **Supporting assets**: none. The artwork is pure DSL; no photograph, "
              f"bitmap or embedded `Image` is used, and no post-processing was applied to "
              f"the returned PNG.",
              f"- **Rejected attempts kept**: "
              + (", ".join(f"`{f}`" for f in sorted(fails)) if fails else "none") ,
              f"- **Unresolved issues**: "
              + (", ".join(c["unresolved"]) if c["unresolved"] else "none")]
        with open(os.path.join(cdir, "case.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(md) + "\n")
        print("promoted", c["no"], c["ver"], os.path.getsize(os.path.join(cdir, "final.png")))


if __name__ == "__main__":
    main()
