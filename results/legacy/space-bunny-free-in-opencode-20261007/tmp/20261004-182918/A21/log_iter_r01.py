# -*- coding: utf-8 -*-
"""Log the real render/view iteration trail for A21 into iterations.jsonl.

Every entry below corresponds to a render that actually happened (see
requests.jsonl for the HTTP trace) and to an image that was really opened with
the read tool, or to an audit/parse failure that was really observed.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "A21")
TMP = os.path.join(S.TMP_ROOT, "A21")
snapkit.configure("A21", OUT, TMP)

V = "A21-r%s-v%02d"

ENTRIES = [
    # (round, version, parent, kind, dsl, image, viewed_at, observed, changes, compared, complete)
    ("01", 1, None, "baseline",
     "preview/probe-metrics.snapshot", "preview/probe-metrics.png",
     "2026-10-05T03:47:00+08:00",
     "first probe failed with 400 PARSE_ERROR (a 7 digit hex colour "
     "#6D4AFFF); after fixing it the render succeeded but the ink scan window "
     "was taller than the row pitch, so every measured width was contaminated "
     "by the neighbouring row",
     "row pitch changed to size*2.05+34 and the scan window to size*1.75, "
     "re-rendered (requests A21-req-005 fail, A21-req-006/007 ok)",
     "accepted: per string ink widths/heights/offsets are now clean, and the "
     "shape probe proved Transform rotation, LINEAR/RADIAL gradients, "
     "borderRadius rings, opacity, dashed runs and BOLD_ITALIC all work",
     False),
    ("01", 2, 1, "alternative",
     "preview/probe-display.snapshot", "preview/probe-display.png",
     None,
     "the display face Inter Black is wider than Inter BOLD, so the round-01 "
     "title lockup box came out 15px too narrow (measured 332 vs declared 317)",
     "measured the whole copy set a second time in Inter Black and gave the "
     "metric table a font dimension (request A21-req-012)",
     "Layerlight@64 = 330px in Inter Black vs 316px in Inter BOLD; title box "
     "widened accordingly", False),
    ("01", 3, 2, "baseline",
     "round-01/launch-portrait.snapshot", "round-01/launch-portrait.png",
     None,
     "the composition rendered but the audit pipeline itself was still broken "
     "(float range error, then chip/pill edges counted as glyph escape), so "
     "the image was not yet reviewed visually",
     "rewrote the audit to diff the final PNG against a text-free render of "
     "the identical composition, which isolates glyph coverage exactly",
     "audits became trustworthy; the image was then opened and reviewed",
     False),
    ("01", 4, 3, "visual",
     "round-01/launch-portrait.snapshot", "round-01/launch-portrait.png",
     "2026-10-05T03:52:00+08:00",
     "brand mark read as one teal blob: the light beam covered the plates, the "
     "aura was a hard edged disc, and the 44px header mark was a teal lozenge",
     "aura radial gradient reversed to centre-opaque -> edge-transparent and "
     "grown to 1.72x; beam thickness 0.115 -> 0.05 of the mark box; plate "
     "fills made more opaque; spark moved inboard (0.78/0.175) and made "
     "smaller; portrait mark 340 -> 380 and re-laid out; wide mark re-centred",
     "improved but the beam was still a slab: reviewed the image and the DSL "
     "together and found the root cause in the next iteration", True),
    ("01", 5, 4, "visual",
     "round-01/launch-portrait.snapshot", "round-01/launch-portrait.png",
     "2026-10-05T04:04:00+08:00",
     "sampled the PNG: the mint beam occupied 256 raster rows where the "
     "geometry predicted 142, although the DSL said Container 402.8 x 19. "
     "Root cause: <Positioned width height> hands tight constraints to the "
     "Transform subtree and a Container inside tight constraints is stretched "
     "to them, so the beam became the rotated bounding box 389 x 143",
     "the beam Positioned now uses the un-rotated bar size (402.8 x 19) so the "
     "Container keeps its own size and only the paint is rotated; the wide "
     "asset was recomposed into header / title+mark / full width fact strip so "
     "the banner no longer has an empty bottom third",
     "accepted: the mark now reads as three stacked light plates + a light "
     "streak + a glowing point at 380px and at 44px, and both assets pass the "
     "ink, reserved-band and contrast audits", True),
    ("01", 6, 5, "visual",
     "round-01/launch-wide.snapshot", "round-01/launch-wide.png",
     "2026-10-05T04:09:00+08:00",
     "final round-01 review of both assets at full size plus 1.6x crops of the "
     "44px header mark and the 380px hero mark",
     "no further change needed",
     "accepted round-01: 0 ink violations, 0 reserved-band pixels, worst "
     "measured contrast 5.15:1 (white on the ONLINE LAUNCH chip), smallest "
     "font size 24px", True),
]


def main():
    for rnd, n, parent, kind, dsl, img, viewed, obs, chg, cmp_, complete in ENTRIES:
        vid = V % (rnd, n)
        snapkit.log_iteration(
            version=vid,
            parent=None if parent is None else V % ("01", parent),
            kind=kind, dsl_file=os.path.join("outputs", RUN, "A21", dsl),
            image_file=os.path.join("outputs", RUN, "A21", img),
            viewed_at=viewed, observed=obs, changes=chg, compared=cmp_,
            complete=complete,
            note="round-01 of the preloaded three round brief")
        print("logged", vid, kind, "complete=%s" % complete)


if __name__ == "__main__":
    main()