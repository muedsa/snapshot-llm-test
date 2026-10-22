# -*- coding: utf-8 -*-
"""A17 filter-leak isolation experiments: 4 mini DSLs + auto profiling.

Each scene (400x300, white bg) contains, in paint order:
  T1  plain text (label "AAAA")            -- before filter
  R1  Row with 2 Expanded bars (blue|orange, boundary x=200)
  C1  plain Container purple (direct child of Positioned)
  T2  plain text (label "BBBB")            -- before filter
  F1  the treatment (filter or none)
Measure: T1/T2 stroke sharpness, Row outer/boundary ramps, C1 edge.
"""
import pathlib
import subprocess
import sys

from PIL import Image

TMP = pathlib.Path("tmp/run-20261011-01/A17")
HELPER = pathlib.Path("tmp/run-20261011-01/_suite/scripts/snap_render.py")
LOG = TMP / "requests.jsonl"
EXP = TMP / "experiments"
EXP.mkdir(parents=True, exist_ok=True)

HEAD = """<Snapshot type="png" background="#FFFFFF">
  <SizedBox width="400" height="300">
    <Stack alignment="TOP_LEFT" clipBehavior="NONE">
      <Positioned left="10" top="10" width="380" height="34">
        <Text fontSize="24" color="#000000" fontFamily="Noto Sans Mono CJK SC" text="AAAA0000BBBB0000"/>
      </Positioned>
      <Positioned left="10" top="60" width="380" height="50">
        <Row>
          <Expanded flex="1"><Container color="#2563EB" height="50"/></Expanded>
          <Expanded flex="1"><Container color="#F59E0B" height="50"/></Expanded>
        </Row>
      </Positioned>
      <Positioned left="10" top="140" width="120" height="60">
        <Container color="#7C3AED" borderRadius="8"/>
      </Positioned>
      <Positioned left="10" top="230" width="380" height="34">
        <Text fontSize="24" color="#000000" fontFamily="Noto Sans Mono CJK SC" text="ZZZZ1111YYYY1111"/>
      </Positioned>
"""
TAIL = """    </Stack>
  </SizedBox>
</Snapshot>
"""

TREATMENTS = {
    # exp1: nothing (baseline)
    "exp1": "",
    # exp2: BackdropFilter as direct child of root Stack (probe-like)
    "exp2": """      <Positioned left="200" top="140" width="80" height="30">
        <BackdropFilter sigmaX="6" sigmaY="6">
          <Container color="#FFFFFFB3" borderRadius="6"/>
        </BackdropFilter>
      </Positioned>
""",
    # exp3: BackdropFilter nested inside wrapper Positioned>Stack (page-like)
    "exp3": """      <Positioned left="0" top="130" width="400" height="80">
        <Stack alignment="TOP_LEFT" clipBehavior="NONE">
          <Positioned left="200" top="10" width="80" height="30">
            <BackdropFilter sigmaX="6" sigmaY="6">
              <Container color="#FFFFFFB3" borderRadius="6"/>
            </BackdropFilter>
          </Positioned>
        </Stack>
      </Positioned>
""",
    # exp4: ImageFiltered only (no BackdropFilter)
    "exp4": """      <Positioned left="200" top="140" width="80" height="30">
        <ImageFiltered sigmaX="6" sigmaY="6">
          <Container color="#7C3AED" borderRadius="6"/>
        </ImageFiltered>
      </Positioned>
""",
    # exp5: BackdropFilter with EXPLICIT sized child
    "exp5": """      <Positioned left="200" top="140" width="80" height="30">
        <BackdropFilter sigmaX="6" sigmaY="6">
          <Container color="#FFFFFFB3" width="80" height="30" borderRadius="6"/>
        </BackdropFilter>
      </Positioned>
""",
}


def prof(im, x0, x1, y, label):
    px = im.load()
    vals = [px[x, y][0] for x in range(x0, x1)]
    print(f"    {label}: y={y} x{x0}..{x1}: {vals}")


def vprof(im, y0, y1, x, label):
    px = im.load()
    vals = [px[x, y][0] for y in range(y0, y1)]
    print(f"    {label}: x={x} y{y0}..{y1}: {vals}")


def main(names):
    for name in names:
        dsl = EXP / f"{name}.snapshot"
        dsl.write_text(HEAD + TREATMENTS[name] + TAIL, encoding="utf-8")
        png = EXP / f"{name}.png"
        r = subprocess.run(
            [sys.executable, str(HELPER), "--dsl", str(dsl), "--out", str(png),
             "--log", str(LOG), "--rid", f"A17-{name}"],
            capture_output=True, text=True)
        print(name, (r.stdout.strip().splitlines() or [""])[-1][:200])
        if r.returncode != 0:
            print(r.stderr[-800:])
            continue
        im = Image.open(png).convert("RGB")
        print(f"  == {name} profiles")
        # T1 text stroke: 'A' first stroke near x=10..30, y=24 (glyph band 10..44)
        prof(im, 10, 34, 24, "T1 stroke A (expect dark 0-255 steps)")
        # Row outer left edge x=10, y=85
        prof(im, 2, 22, 85, "Row LEFT edge (expect x10)")
        # Row boundary x=10+190=200 (380/2=190 -> x200)
        prof(im, 190, 212, 85, "Row boundary (expect x200)")
        # plain container left edge x=10 y=170
        prof(im, 2, 22, 170, "C1 LEFT edge (expect x10)")
        # T2 text stroke
        prof(im, 10, 34, 244, "T2 stroke Z (expect dark 0-255 steps)")


if __name__ == "__main__":
    main(sys.argv[1:] or list(TREATMENTS))
