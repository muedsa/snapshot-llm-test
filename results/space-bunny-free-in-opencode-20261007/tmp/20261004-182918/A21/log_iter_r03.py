# -*- coding: utf-8 -*-
"""Iteration trail for A21 round-03 (light theme + contrast requirement)."""
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
    ("03", 1, None, "baseline",
     "round-03/launch-portrait.snapshot", "round-03/launch-portrait.png",
     None,
     "first light-theme render: full surface recomposition, English line added "
     "above the URL, 4-row card in the portrait and a two line third column in "
     "the wide bottom strip",
     "no visual sign-off in this version",
     "superseded by v02", False),
    ("03", 2, 1, "requirement-change",
     "round-03/launch-portrait.snapshot", "round-03/launch-portrait.png",
     "2026-10-05T04:52:00+08:00",
     "opened both round-03 images. The theme flip itself worked, but the brand "
     "mark lost presence: plate-base #D7CCFF and plate-mid #B7A2FF were too "
     "pale against the #FBFAFF page, so the two lower plates nearly dissolved "
     "and the mark stopped reading as the same six component graphic",
     "deepened the light-theme plates to #C9B6FF / #A78BFA and strengthened "
     "their borders to #6D4AFF80 / #5B2BE099 (dark-theme values untouched), then "
     "re-rendered both sizes",
     "accepted: at 1.7x zoom the three plates, the teal light streak and the "
     "white spark with its teal ring are all clearly separable on the light "
     "page, and the contrast audit is unchanged (worst 7.33:1 portrait, "
     "6.39:1 wide, every text >= 4.5:1)", True),
    ("03", 3, 2, "visual",
     "round-03/launch-wide.snapshot", "round-03/launch-wide.png",
     "2026-10-05T04:55:00+08:00",
     "final round-03 review: both assets at full size, plus a 1.7x crop of the "
     "light-theme mark and a 1.7x crop proving 'Clarity through structure' sits "
     "directly above the URL in the wide strip",
     "no further change needed",
     "accepted round-03: sponsor present in both, all round-02 copy present, "
     "Chinese title still 2 lines @52px (portrait) and 3 lines @48px (wide), "
     "English line 28px, reserved bands still empty, 0 ink violations, "
     "0 text collisions", True),
]


def main():
    for rnd, n, parent, kind, dsl, img, viewed, obs, chg, cmp_, complete in ENTRIES:
        snapkit.log_iteration(
            version=V % (rnd, n),
            parent=None if parent is None else V % ("02", 3),
            kind=kind, dsl_file=os.path.join("outputs", RUN, "A21", dsl),
            image_file=os.path.join("outputs", RUN, "A21", img),
            viewed_at=viewed, observed=obs, changes=chg, compared=cmp_,
            complete=complete,
            note="round-03 of the preloaded three round brief")
        print("logged", V % (rnd, n), kind, "complete=%s" % complete)


if __name__ == "__main__":
    main()