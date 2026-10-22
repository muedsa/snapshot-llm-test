# -*- coding: utf-8 -*-
"""Render no-BackdropFilter variants of the real artifacts and diff them
against the originals to map the exact leak region."""
import pathlib
import subprocess
import sys

from PIL import Image, ImageChops

TMP = pathlib.Path("tmp/run-20261011-01/A17")
HELPER = pathlib.Path("tmp/run-20261011-01/_suite/scripts/snap_render.py")
LOG = TMP / "requests.jsonl"
VAR = TMP / "variants"
VAR.mkdir(parents=True, exist_ok=True)

TARGETS = {
    "probe": TMP / "scripts/probe.snapshot",
    "example-04": TMP / "gen/example-04.snapshot",
    "handbook-04": TMP / "gen/handbook-04.snapshot",
}


def strip_backdrop(text):
    lines = text.splitlines()
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        if "<BackdropFilter" in lines[i]:
            # find enclosing Positioned open (scan back in `out`)
            while out and "<Positioned" not in out[-1]:
                out.pop()
            out.pop()  # the Positioned open line
            # skip until </BackdropFilter>, then its </Positioned>
            while "</BackdropFilter" not in lines[i]:
                i += 1
            i += 1  # skip </BackdropFilter ...>
            if "</Positioned" in lines[i]:
                i += 1
            removed += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out) + "\n", removed


def main():
    for name, src in TARGETS.items():
        text = src.read_text(encoding="utf-8")
        variant, n = strip_backdrop(text)
        assert n == 1, f"{name}: removed {n} BackdropFilters"
        v_dsl = VAR / f"{name}-nobf.snapshot"
        v_dsl.write_text(variant, encoding="utf-8")
        v_png = VAR / f"{name}-nobf.png"
        r = subprocess.run(
            [sys.executable, str(HELPER), "--dsl", str(v_dsl), "--out", str(v_png),
             "--log", str(LOG), "--rid", f"A17-nobf-{name}"],
            capture_output=True, text=True)
        print(name, (r.stdout.strip().splitlines() or [""])[-1][:220])
        if r.returncode != 0:
            print(r.stderr[-800:])
            continue
        orig_png = (TMP / "scripts/probe.png" if name == "probe"
                    else TMP / "gen" / f"{name}.png")
        a = Image.open(orig_png).convert("RGB")
        b = Image.open(v_png).convert("RGB")
        diff = ImageChops.difference(a, b)
        bbox = diff.getbbox()
        print(f"  diff bbox (leak region incl. panel itself): {bbox}")
        # Classify: panel bounds for reference
        if name == "probe":
            panel = (560, 222, 740, 258)
        else:
            # core panel at (56,28,150,34); page: + (76, 382)
            off = (76, 382) if name == "handbook-04" else (0, 0)
            panel = (56 + off[0], 28 + off[1], 56 + off[0] + 150,
                     28 + off[1] + 34)
        print(f"  panel bounds (expected small diff): {panel}")
        # sample diff intensity at a few landmark points
        px = diff.load()
        W, H = a.size
        big = []
        step = 4 if W > 800 else 2
        for y in range(0, H, 8):
            for x in range(0, W, 8):
                d = px[x, y]
                if max(d) > 20:
                    big.append((x, y, max(d)))
        print(f"  points with diff>20: {len(big)}; first/last:",
              big[:3], big[-3:] if big else None)


if __name__ == "__main__":
    main()
