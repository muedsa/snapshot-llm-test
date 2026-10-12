"""A12 design tokens + the four-breakpoint layout rules, in one place.

content.json is the only source of copy. Every string that reaches a canvas is either
verbatim from inputs/content.json (provenance="input") or derived from it without adding
facts (provenance="derived", e.g. the card index "C1".."C6" and the "六项能力" kicker that
just counts the input cards). design-tokens.json is dumped straight from TOKENS/PALETTE so
the board and the token file cannot disagree.

The one rule carried over from A11: a Snapshot line box is 1.45 em, so every text box is
sized hh(size, lines) = round(size * 1.45 * lines) even though TextFit.need() would accept
h >= size for a single line.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A12"
TEMP = ROOT / "tmp" / RID / TASK
SRC = ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json"

content = json.loads(SRC.read_text(encoding="utf-8"))
cards = content["cards"]

# derived strings: computed from the input, no new facts, never a substitute for one
DERIVED_KICKER = f"六项能力 · 一场活动"          # counts len(cards)
assert len(cards) == 6, len(cards)

# ---------------------------------------------------------------- palette (shared) ----
PALETTE = {
    "paper": "#EEF2F7",
    "panel": "#FFFFFF",
    "hero": "#0F1B2D",
    "hero2": "#16263D",
    "ink": "#0F1B2D",
    "ink2": "#475569",
    "muted": "#64748B",
    "line": "#D7DFEA",
    "accent": "#1D4ED8",
    "accent2": "#3B82F6",
    "accentSoft": "#E4ECFB",
    "onHero": "#F8FAFC",
    "onHeroDim": "#9DB4D0",
    "onHeroAccent": "#93C5FD",
    "rule": "#C6D2E2",
}

# core decorative constructs, reused (and rearranged) at every breakpoint
CONSTRUCTS = ["heroPanel", "accentBar", "indexChip", "pill", "dotRow", "ruleLine"]

TYPE = {
    #            mobile tablet desktop stage
    "title":        [26, 48, 56, 72],
    "subtitle":     [16, 22, 26, 30],
    "meta":         [16, 20, 22, 26],
    "metaLabel":    [16, 20, 22, 26],
    "cta":          [16, 22, 24, 28],
    "website":      [16, 20, 22, 26],
    "cardTitle":    [18, 26, 28, 34],
    "cardDetail":   [16, 20, 22, 26],
    "cardIndex":    [16, 20, 22, 26],
    "kicker":       [16, 20, 22, 26],
}
FLOORS = {
    "mobile": {"body": 16, "cardTitle": 18},
    "tablet": {"body": 20, "title": 40},
    "desktop": {"body": 20, "title": 40},
    "stage": {"body": 20, "title": 40},
}

# ---------------------------------------------------------------- breakpoints ----------
BP = ["mobile", "tablet", "desktop", "stage"]
BREAKS = {
    "mobile":  {"canvas": [360, 800],  "margin": 16, "cols": 1, "cardGap": [6, 14],
                "pad": 10, "inner": 7, "heroPad": 12, "blockGap": 12, "accentBar": 4},
    "tablet":  {"canvas": [768, 1024], "margin": 32, "cols": 2, "cardGap": [20, 20],
                "pad": 20, "inner": 16, "heroPad": 28, "blockGap": 24, "accentBar": 6},
    "desktop": {"canvas": [1440, 900], "margin": 32, "cols": 3, "cardGap": [24, 20],
                "pad": 24, "inner": 18, "heroPad": 32, "blockGap": 26, "accentBar": 6},
    "stage":   {"canvas": [1920, 1080], "margin": 40, "cols": 3, "cardGap": [28, 24],
                "pad": 28, "inner": 20, "heroPad": 40, "blockGap": 30, "accentBar": 8},
}
# hero placement: 'stack' = hero band across the top; 'side' = hero in a left column.
# 1440x900 is only 900px tall, so a left-column hero leaves a ~300px vertical void beside
# a 3-row grid; stacking the band and going 3-up fills the canvas from the same tokens.
HERO_MODE = {"mobile": "stack", "tablet": "stack", "desktop": "stack", "stage": "stack"}

LINE = 1.45
# a box of exactly 1.45 em still cut the descenders of "structure.example.org" (A12 check:
# ink flush with the bottom row at 16pt and 22pt), so every text box gets 2px of allowance
DESCENDER = 2


def hh(size, lines=1):
    return round(size * LINE * lines) + DESCENDER


def tokens_doc():
    """design-tokens.json — colour / type / spacing / component rules, verbatim from above."""
    return {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": TASK,
        "run_id": RID,
        "source_content": "tasks/A12-responsive-system/inputs/content.json",
        "generated_by": "tmp/%s/A12/plan_a12.py (this table) + tmp/%s/A12/generate_a12.py "
                        "(layout engine that reads it)" % (RID, RID),
        "shared_across_all_breakpoints": {
            "palette": PALETTE,
            "line_height_factor": LINE,
            "font_families": {
                "display_and_body": "Inter,Noto Sans CJK SC",
                "index_and_website": "Noto Sans Mono CJK SC",
            },
            "core_constructs": CONSTRUCTS,
            "radii": {"panel": 18, "card": 14, "chip": 8, "pill": 999},
            "rule_thickness": 1,
            "accent_bar_role": "left edge of every card and the hero panel; identical hue "
                               "at every breakpoint, only its length/weight scales",
        },
        "type_scale_pt": TYPE,
        "type_floors": FLOORS,
        "breakpoints": {
            b: {
                "canvas": BREAKS[b]["canvas"],
                "safe_margin": BREAKS[b]["margin"],
                "card_columns": BREAKS[b]["cols"],
                "card_gap_xy": BREAKS[b]["cardGap"],
                "panel_padding": BREAKS[b]["pad"],
                "card_inner_padding": BREAKS[b]["inner"],
                "hero_padding": BREAKS[b]["heroPad"],
                "block_gap": BREAKS[b]["blockGap"],
                "accent_bar_width": BREAKS[b]["accentBar"],
                "hero_placement": HERO_MODE[b],
                "hero_width": "full content column (canvas - 2 x safe margin)",
            } for b in BP
        },
        "component_rules": {
            "card": "white panel, 1px #D7DFEA border, 14px radius, accent bar on the left "
                    "edge, mono index chip, title above detail; never truncated at any size",
            "hero": "dark #0F1B2D panel across the full content column at every breakpoint; "
                    "title, subtitle, the measured meta flow and the CTA pill; never a left "
                    "column (1440x900 is too short for one — see snapshot-usage.md §4)",
            "meta_flow": "date/time/place groups are laid out by measured width, not by a "
                         "per-breakpoint flag: they flow into one line while they fit and "
                         "wrap as a unit otherwise. Observed: 3 lines at 360, 2 at 768, "
                         "1 at 1440 and 1920",
            "cta": "pill with centred text; the input string is rendered as text, no QR "
                   "code is generated anywhere (no <Image> / no raster asset in any DSL). "
                   "When the meta flow is a single line and the pill still fits, the pill "
                   "joins that line and is vertically centred to the taller of the two "
                   "boxes (1440, 1920); otherwise it sits below the flow (360, 768)",
            "website": "mono line with a leading accent dot, pinned to the bottom of the "
                       "content column at every breakpoint",
            "rearrangement": "same constructs, different composition: 1 column at 360, "
                             "2x3 at 768, 3x2 at 1440 and 3x2 at 1920 — the rhythm "
                             "multiplier and the type scale carry the size difference",
        },
        "fidelity_rule": "every field of inputs/content.json appears on all four canvases "
                         "with its exact string; content-map.json records the box each one "
                         "occupies per canvas",
        "box_height_rule": "text boxes are sized round(fontSize * 1.45 * lines) + 2, not "
                           "fontSize, because the renderer's line box is 1.45 em (A11 "
                           "measured clipping at ratio 0.577 when h == fontSize), and the +2 "
                           "is the descender allowance A12 measured on the mono website line",
    }


if __name__ == "__main__":
    out = {"tokens": tokens_doc(), "content": content,
           "derived": {"kicker": "六项能力 · 一场活动",
                       "card_count": len(content["cards"])}}
    print(json.dumps(out["tokens"]["breakpoints"], ensure_ascii=False, indent=1))
