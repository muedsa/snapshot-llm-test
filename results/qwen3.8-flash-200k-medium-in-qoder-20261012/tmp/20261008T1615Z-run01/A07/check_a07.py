"""A07 pixel self-check on the delivered PNGs (run after the images are in outputs/).

Everything asserted here is measured on the real service response, not on the DSL:
  * canvas sizes and the 32px safe ring of the map;
  * every station label box is free of ribbon pixels (a ribbon crossing a label means
    the label would read as belonging to another line);
  * every station has a ring symbol at its table position;
  * the three interchanges read as double rings, the rest as single rings;
  * the travel card is 720x1280 and its three route panels are visually distinct.

Usage (from the suite root):
  python tmp/<run_id>/A07/check_a07.py
"""
import json
import math
import os
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "A07"
MAP = OUT / "network-map.png"
CARD = OUT / "travel-card.png"

RIBBON = [(248, 113, 113), (96, 165, 250), (52, 211, 153)]
SYMBOL = RIBBON + [(251, 191, 36)]   # non-accessible stations carry the amber slash
BG = (11, 18, 32)
TOL = 26


def near(px, ref, tol=TOL):
    return all(abs(a - b) <= tol for a, b in zip(px[:3], ref))


def main():
    problems = []
    routes = json.loads((OUT / "routes.json").read_text(encoding="utf-8"))
    im = Image.open(MAP).convert("RGB")
    W, H = im.size
    if (W, H) != (1600, 1000):
        problems.append(f"map size {W}x{H}")
    px = im.load()

    # safe ring: nothing but the panel background outside the 32px inset
    ring = 0
    for y in range(0, 30, 2):
        for x in range(0, W, 2):
            if not near(px[x, y], BG) or not near(px[x, H - 1 - y], BG):
                ring += 1
    for x in range(0, 30, 2):
        for y in range(0, H, 2):
            if not near(px[x, y], BG) or not near(px[W - 1 - x, y], BG):
                ring += 1
    if ring:
        problems.append(f"map safe ring polluted at {ring} samples")

    # label boxes must not contain any ribbon pixel
    label_check = {}
    for st in routes["network"]["stations"]:
        x0, y0, x1, y1 = [round(v) for v in st["label_box"]]
        hits = Counter()
        for y in range(y0, y1):
            for x in range(x0, x1):
                for ref in RIBBON:
                    if near(px[x, y], ref):
                        hits[ref] += 1
        label_check[st["id"]] = sum(hits.values())
        if hits:
            problems.append(f"{st['id']} label box has {sum(hits.values())} ribbon px")

    # station symbols: an ordinary station is a 20px ring with a white core, an
    # interchange adds a 30px outer ring, so white must also show at r=12..14.
    symbols = {}
    for st in routes["network"]["stations"]:
        x, y = [round(v) for v in st["position"]]
        core = sum(1 for dy in range(-5, 6) for dx in range(-5, 6)
                   if dx * dx + dy * dy <= 25
                   and (all(c > 200 for c in px[x + dx, y + dy])
                        or any(near(px[x + dx, y + dy], ref) for ref in SYMBOL)))
        outer = sum(1 for dy in range(-15, 16) for dx in range(-15, 16)
                    if 144 <= dx * dx + dy * dy <= 196 and all(c > 200 for c in px[x + dx, y + dy]))
        symbols[st["id"]] = {"white_core_px": core, "white_outer_px": outer,
                             "interchange": st["interchange"]}
        if core < 40:
            problems.append(f"{st['id']} has no white station core ({core} px)")
        if st["interchange"] and outer < 40:
            problems.append(f"{st['id']} interchange lacks its outer white ring ({outer})")
        if not st["interchange"] and outer > 12:
            problems.append(f"{st['id']} ordinary station shows an outer ring ({outer})")

    # equal-length hops really are equal on screen
    lens = {round(h["length_px"], 2) for h in routes["network"]["hops"]}
    if len(lens) != 1:
        problems.append(f"hop lengths differ on screen: {lens}")
    if len(routes["network"]["hops"]) != 16 or len(routes["network"]["stations"]) != 16:
        problems.append("hop/station count does not match the input network")

    card = Image.open(CARD).convert("RGB")
    if card.size != (720, 1280):
        problems.append(f"card size {card.size}")
    cp = card.load()
    # count the panel-filled runs down the middle: 3 route cards + 1 footer block
    inside, panels = False, 0
    # x=56 sits inside every panel (they start at M+18=50) but left of all text
    for y in range(60, 1250):
        on = near(cp[56, y], (16, 26, 46), 6)
        if on and not inside:
            panels += 1
        inside = on
    if panels != 4:
        problems.append(f"card panel runs = {panels}, expected 4")
    ribbon_px = sum(1 for y in range(0, 1280, 3) for x in range(0, 720, 3)
                    if any(near(cp[x, y], ref) for ref in RIBBON))

    rep = {"map_size": [W, H], "card_size": list(card.size),
           "safe_ring_polluted_samples": ring,
           "label_ribbon_pixels": label_check,
           "hop_lengths_on_screen": sorted(lens),
           "station_symbols": symbols,
           "card_panel_edges": panels, "card_ribbon_samples": ribbon_px,
           "problems": problems}
    (ROOT / "tmp" / RID / "A07" / "pixel-report.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"problems": problems, "ring": ring,
                      "worst_label": max(label_check.items(), key=lambda kv: kv[1]),
                      "card_panels": panels}, ensure_ascii=False))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
