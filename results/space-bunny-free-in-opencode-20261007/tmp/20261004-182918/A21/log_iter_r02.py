# -*- coding: utf-8 -*-
"""Iteration trail for A21 round-02 (requirement change on top of round-01)."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

snapkit.configure("A21", os.path.join(S.OUT_ROOT, "A21"), os.path.join(S.TMP_ROOT, "A21"))

V = "A21-r%s-v%02d"

ENTRIES = [
    ("02", 1, None, "baseline",
     "round-02/launch-portrait.snapshot", "round-02/launch-portrait.png",
     None,
     "first round-02 render: long title as two 52px lines in the portrait and "
     "three 48px lines in the wide, sponsor + free-entry added, hero mark "
     "rescaled; the inherited audit still mis-attributed glyph pixels between "
     "neighbouring title lines, so the report was not trustworthy yet",
     "no visual sign-off in this version",
     "superseded by v02 once the audit tool was corrected", False),
    ("02", 2, 1, "requirement-change",
     "round-02/launch-portrait.snapshot", "round-02/launch-portrait.png",
     "2026-10-05T04:31:00+08:00",
     "opened both round-02 images. Two real defects and one tooling defect: "
     "(a) the brand kicker read as 叠光Layerlight because the gap between the two "
     "kicker texts was only 7px; (b) the portrait had a 200px hole between the "
     "hero mark and the kicker; (c) the audit reported false escapes for the "
     "title because it attributed each line's glyph pixels to whichever box it "
     "scanned first, and its bbox was taken from the last scan row instead of "
     "the global min/max",
     "kicker gap 7px -> 21px (x 155->169 portrait, 159->173 wide); portrait hero "
     "mark 340 -> 360 and moved down 12px; audit rewritten so every changed "
     "pixel is attributed to the nearest declared ink box, the bbox is a real "
     "min/max, a 6px anti-aliasing fringe tolerance is declared explicitly, and "
     "a pairwise measured-ink overlap check was added",
     "re-rendered and re-audited: 0 ink violations, 0 unattributed pixels, "
     "0 pairwise text collisions, reserved bands still empty, worst contrast "
     "5.15:1", True),
    ("02", 3, 2, "visual",
     "round-02/launch-wide.snapshot", "round-02/launch-wide.png",
     "2026-10-05T04:36:00+08:00",
     "final round-02 review of both assets at full size plus 1.5x crops of the "
     "portrait title block and the three-row info card",
     "no further change needed",
     "accepted round-02: title 2 lines @52px (portrait) and 3 lines @48px "
     "(wide), both >=48 and <=3 lines; widest title line leaves 136px (portrait) "
     "and 90px (wide) of horizontal slack in its column; all five round-01 "
     "strings plus the two new strings present in both images", True),
]


def main():
    for rnd, n, parent, kind, dsl, img, viewed, obs, chg, cmp_, complete in ENTRIES:
        snapkit.log_iteration(
            version=V % (rnd, n),
            parent=None if parent is None else V % ("01", 6),
            kind=kind, dsl_file=os.path.join("outputs", RUN, "A21", dsl),
            image_file=os.path.join("outputs", RUN, "A21", img),
            viewed_at=viewed, observed=obs, changes=chg, compared=cmp_,
            complete=complete,
            note="round-02 of the preloaded three round brief")
        print("logged", V % (rnd, n), kind, "complete=%s" % complete)


if __name__ == "__main__":
    main()