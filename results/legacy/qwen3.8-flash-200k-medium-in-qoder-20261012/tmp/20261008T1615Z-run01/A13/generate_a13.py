"""A13 final generator: symbol (colour + black), banner, poster, 32px checks, brand-system.

The chosen direction is A (translation) with the round-2 refinements: stroke 0.070 S and an
amber "light" node, both decided by looking at the sheets in preview/sheets/.

The banner and the poster re-enter the same `icon()` call — TASK.md forbids embedding the
rendered icon PNG, so the mark is regenerated from the identical geometry rule at each size.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "A13"))
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
import plan_a13 as P  # noqa: E402
from dslkit import TextFit, n  # noqa: E402

TEMP = ROOT / "tmp" / RID / "A13"
PREVIEW = TEMP / "preview"
PL = P.PALETTE

# ---- the decisions taken from the previews -------------------------------------------
P.A["stroke"] = 0.070
NODE = "#F59E0B"
DIRECTION = "A"


def symbol(size, variant):
    doc = P.Doc(size, size, bg="transparent", font=P.FONT)
    S = size / (1 + 2 * P.CLEAR_SPACE)
    P.icon(doc, size / 2, size / 2, S, DIRECTION, variant, node_color=NODE)
    return doc


def ghost_layers(doc, cx, cy, side, stroke, ops=(0.22, 0.18, 0.14), clip=None):
    """The mark's own offset rule, drawn thin and dim: structure, not decoration.

    v01 used the full 7 % stroke at large scale and the result was three heavy bands across
    the type, so the motif keeps the same diagonal vector but drops to a hairline.

    `clip=(w, h)` puts the group inside a ClipRect: on the poster the ghosts' bottom edges ran
    straight through the OPEN BETA line, and stopping the group above the headline is a
    composition fix rather than a transparency compromise on the motif itself.
    """
    cols = (PL["blue"], PL["green"], PL["red"])
    parts = []
    for i, c in enumerate(cols):
        gx = cx + (i - 1) * 0.17 * side
        gy = cy - (i - 1) * 0.17 * side
        inner = doc.box(side, side, radius=0.12 * side,
                        border=f"{n(stroke)} SOLID {c}")
        seg = (f'<Positioned left="{n(gx - side / 2)}" top="{n(gy - side / 2)}" '
               f'width="{n(side)}" height="{n(side)}">'
               f'<Opacity opacity="{ops[i]}">{inner}</Opacity></Positioned>')
        if clip is None:
            doc.pos(gx - side / 2, gy - side / 2, side, side,
                    f'<Opacity opacity="{ops[i]}">{inner}</Opacity>')
        else:
            parts.append(seg)
    if parts:
        cw, ch = clip
        # ClipRect has no size of its own: it clips to its layout bounds, which the outer
        # Positioned supplies, and it takes a single child, hence the inner Stack.
        # Stack.clipBehavior rejects CLIP (PARSE_ERROR: "No enum constant ...ClipBehavior.CLIP")
        # and needs a decoration to build a path at all, so clipping is left to ClipRect.
        doc.pos(0, 0, cw, ch,
                f'<ClipRect><Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                f'{"".join(parts)}</Stack></ClipRect>')


def banner():
    W, H = 1200, 400
    doc = P.Doc(W, H, bg=PL["paper"], font=P.FONT)
    fit = TextFit()
    S = 220
    # the mark's own clear space (0.30 S) is a rule, not a suggestion: v02 used a 56px edge
    # margin and a 64px gap to the wordmark, both below 0.30*220 = 66, so the mark was
    # crowding the very edge it is supposed to breathe against
    m = round(P.CLEAR_SPACE * S)
    # the right half is not empty space: the same offset rule bleeds off the edge so the
    # banner is composed from the mark rather than from a mark glued to text
    ghost_layers(doc, W - 150, H / 2, 340, 6)
    P.icon(doc, m + S / 2, H / 2, S, DIRECTION, "color", node_color=NODE)
    x = m + S + m
    # wordmark: CJK name and latin name on one line, sized so the pair ends before the
    # right margin; the tagline sits under a three-segment rule in the layer colours
    doc.label(x, 96, 160, 96, "叠光", PL["ink"], 76, "BOLD")
    lw = fit.w("Layerlight", 40)
    doc.label(x + 176, 118, round(lw / 0.96) + 4, 60, "Layerlight", PL["ink2"], 40,
              None, spacing=1.5)
    seg = [PL["blue"], PL["green"], PL["red"]]
    for i, c in enumerate(seg):
        doc.rect(x + i * 84, 214, 76, 5, c, radius=2.5)
    doc.label(x, 240, 620, 44, "把复杂信息，组织成清晰画面", PL["ink2"], 30)
    fit.check("banner-tagline", "把复杂信息，组织成清晰画面", 30, 620, 44)
    fit.check("banner-latin", "Layerlight", 40, round(lw / 0.96) + 4, 60)
    return doc, fit


def poster():
    W, H = 1080, 1350
    doc = P.Doc(W, H, bg=PL["night"], font=P.FONT)
    fit = TextFit()
    m = 72
    ghost_layers(doc, W / 2, 360, 780, 4, ops=(0.30, 0.24, 0.18), clip=(W, 660))
    # the mark, at the optical centre of the upper half
    S = 430
    P.icon(doc, W / 2, 360, S, DIRECTION, "color", node_color=NODE)
    doc.label(0, 690, W, 118, "OPEN BETA", PL["onNight"], 96, "BOLD", align="CENTER",
              spacing=6)
    # one panel carries the release block: v01 let these five lines float down the page
    # with uneven gaps, which read as leftover space rather than as a footer
    doc.pos(m, 850, W - 2 * m, 350, doc.box(W - 2 * m, 350, color=PL["night2"], radius=28))
    doc.label(0, 886, W, 52, "叠光 Layerlight", PL["onNight"], 40, "BOLD", align="CENTER")
    doc.label(0, 946, W, 40, "把复杂信息，组织成清晰画面", PL["onNightDim"], 28,
              align="CENTER")
    doc.line(W / 2 - 130, 1012, W / 2 + 130, 1012, 2, "#2A3A55")
    doc.label(0, 1032, W, 52, "2026.11.07 · ONLINE", PL["onNight"], 34, None,
              align="CENTER", spacing=2)
    # three layer chips repeat the palette rule, and the light node closes the row
    for i, c in enumerate((PL["blue"], PL["green"], PL["red"])):
        doc.rect(W / 2 - 74 + i * 46, 1146, 32, 6, c, radius=6 / 2)
    doc.rect(W / 2 - 74 + 3 * 46, 1140, 18, 18, NODE, radius=4)
    doc.label(0, 1240, W, 40, "layerlight.example.org", PL["onNightDim"], 28,
              align="CENTER", spacing=1)
    for s, size in (("OPEN BETA", 96), ("叠光 Layerlight", 40),
                    ("把复杂信息，组织成清晰画面", 28), ("2026.11.07 · ONLINE", 34),
                    ("layerlight.example.org", 28)):
        fit.check("poster", s, size, W - 2 * m, 200)
    return doc, fit


def geom_sig(dsl):
    """Geometry fingerprint: every positional attribute with the colours removed.

    TASK.md requires the colour and black symbols to be geometrically the same mark, so
    this compares the two DSLs on shape alone instead of eyeballing them.
    """
    return re.findall(r'(left|top|width|height|borderRadius|matrix|opacity)="([^"]*)"',
                      re.sub(r'#[0-9A-Fa-f]{3,8}', '', dsl))


def emit(name, doc, out_dir, subdir=""):
    """Write the DSL where it is rendered from, plus a working copy in the temp directory
    (A12 convention: the generator's own output stays next to the logs)."""
    d = out_dir
    if subdir:
        d = out_dir / subdir
        d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.snapshot").write_text(doc.dsl(), encoding="utf-8")
    if d != TEMP:
        (TEMP / f"{name}.snapshot").write_text(doc.dsl(), encoding="utf-8")


def main():
    OUT = ROOT / "outputs" / RID / "A13"
    OUT.mkdir(parents=True, exist_ok=True)
    docs = {"symbol-color": symbol(512, "color"), "symbol-black": symbol(512, "black"),
            "brand-banner": banner()[0], "launch-poster": poster()[0],
            "check-32-base": symbol(32, "color")}
    # small-size optical correction: same ratios, thicker stroke (documented in
    # brand-system.json); it is a check preview, not a deliverable
    P.A["stroke"] = 0.085
    docs["check-32-tuned"] = symbol(32, "color")
    P.A["stroke"] = 0.070
    report = {}
    for name, doc in docs.items():
        emit(name, doc, OUT if not name.startswith("check") else PREVIEW)
        dsl = doc.dsl()
        report[name] = {"bytes": len(dsl), "positioned": dsl.count("<Positioned"),
                        "text": dsl.count("<Text ")}
    sc = (OUT / "symbol-color.snapshot").read_text(encoding="utf-8")
    sb = (OUT / "symbol-black.snapshot").read_text(encoding="utf-8")
    report["geometry_identical"] = geom_sig(sc) == geom_sig(sb)
    report["banner_fit_problems"] = banner()[1].problems
    report["poster_fit_problems"] = poster()[1].problems
    report["black_colours_used"] = sorted(set(re.findall(r'color="([^"]+)"', sb)))
    (TEMP / "gen-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
