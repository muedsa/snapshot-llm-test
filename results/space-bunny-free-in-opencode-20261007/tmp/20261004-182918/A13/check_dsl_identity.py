# -*- coding: utf-8 -*-
"""A13: prove the delivered .snapshot files are exactly the DSL that produced
their PNG, and spot-check the geometry literals inside them."""
import hashlib
import io
import os
import re

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A13")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A13")


def h(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()[:16]


PAIRS = [("symbol-color.snapshot", "final-symbol-color.snapshot"),
         ("symbol-black.snapshot", "final-symbol-black.snapshot"),
         ("brand-banner.snapshot", "v11-banner.snapshot")]
for a, b in PAIRS:
    pa, pb = os.path.join(OUT, a), os.path.join(TMP, "drafts", b)
    same = h(pa) == h(pb)
    print("%-4s %-24s delivered=%s draft=%s" % ("SAME" if same else "DIFF", a,
                                                 h(pa), h(pb)))

poster = io.open(os.path.join(OUT, "launch-poster.snapshot"), encoding="utf-8").read()
for probe in ["top=\"700\"", "top=\"876\"", "top=\"958\"", "top=\"1032\"",
              "top=\"1048\"", "top=\"1078\"", "left=\"330.0\"", "left=\"84\"",
              "top=\"190.0\"", "top=\"1120.0\"", "top=\"93\""]:
    print("%-4s %s" % ("ok" if probe in poster else "MISS", probe))
print("poster chars:", len(poster))

banner = io.open(os.path.join(OUT, "brand-banner.snapshot"), encoding="utf-8").read()
print("banner required copy:", "叠光 Layerlight" in banner,
      "把复杂信息，组织成清晰画面" in banner)
print("banner per-corner radii:", len(re.findall(r"borderRadiusTopLeft", banner)))

for fn in ("symbol-color.snapshot", "symbol-black.snapshot"):
    t = io.open(os.path.join(OUT, fn), encoding="utf-8").read()
    rects = re.findall(r'width="([\d.]+)" height="([\d.]+)"', t)
    cols = re.findall(r'color="(#[0-9A-F]{8})"', t)
    print(fn, "rects:", rects, "colors:", sorted(set(cols)),
          "tag count:", len(re.findall(r"<Positioned", t)))