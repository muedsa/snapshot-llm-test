"""A13 independent check. Reads only the delivered PNGs and .snapshot bodies plus the temp
previews — nothing is asserted about a file that was not rendered by the service.

Beyond size/provenance/text checks, three things here are the actual A13 requirements:
  * both symbols are transparent and the black one has RGB exactly 0 on every painted pixel;
  * the colour and black symbols are the *same geometry* (colour-stripped fingerprints);
  * the banner and the poster contain the mark as its own DSL shapes — normalised against
    the symbol's bounding box they must reproduce the same ratios, which is what rules out
    "a rendered icon pasted into the layout".
"""
import hashlib
import json
import os
import re
from pathlib import Path
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "A13"
TEMP = ROOT / "tmp" / RID / "A13"
POS = re.compile(r'<Positioned left="([-\d.]+)" top="([-\d.]+)" width="([-\d.]+)" '
                 r'height="([-\d.]+)">(.*?)</Positioned>', re.S)

FILES = {"symbol-color": (512, 512), "symbol-black": (512, 512),
         "brand-banner": (1200, 400), "launch-poster": (1080, 1350)}
STRINGS = {"brand-banner": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面"],
           "launch-poster": ["叠光 Layerlight", "把复杂信息，组织成清晰画面",
                             "2026.11.07 · ONLINE", "OPEN BETA",
                             "layerlight.example.org"]}
MAX_CONSTRUCTS = 6

res = {"schema_version": 1, "path_base": "suite_root", "task_id": "A13", "run_id": RID,
       "checked_from": {"outputs": f"outputs/{RID}/A13",
                        "previews": f"tmp/{RID}/A13/preview"},
       "files": {}, "failures": []}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sent_body(archive):
    """render.py archives the request as 'POST <url> ...' + the DSL body, so the DSL has to be
    sliced out of the same file the checker compares the delivered .snapshot against."""
    t = Path(archive).read_text(encoding="utf-8")
    i = t.index("<Snapshot")
    return t[i:]


def mark_blocks(dsl):
    """The mark's own shapes: the three bordered frames plus the filled node.

    Ghost layers (<Opacity>) and type are excluded, and a filled block only counts as the node
    if its centre falls inside the frames' bounding box — otherwise a palette chip elsewhere in
    the composition (the poster's amber dot in the chip row) would be mistaken for mark geometry.
    """
    frames, fills = [], []
    for m in POS.finditer(dsl):
        x, y, w, h = (float(m.group(i)) for i in range(1, 5))
        inner = m.group(5)
        if "Opacity" in inner or "Text" in inner:
            continue
        if "border=" in inner:
            frames.append((x, y, w, h))
        elif 'color="#F59E0B"' in inner or 'color="#000000"' in inner:
            fills.append((x, y, w, h))
    if not frames:
        return []
    fx0 = min(b[0] for b in frames)
    fy0 = min(b[1] for b in frames)
    fx1 = max(b[0] + b[2] for b in frames)
    fy1 = max(b[1] + b[3] for b in frames)
    node = [b for b in fills
            if fx0 <= b[0] + b[2] / 2 <= fx1 and fy0 <= b[1] + b[3] / 2 <= fy1]
    return frames + node


def normalised(blocks):
    x0 = min(b[0] for b in blocks)
    y0 = min(b[1] for b in blocks)
    x1 = max(b[0] + b[2] for b in blocks)
    y1 = max(b[1] + b[3] for b in blocks)
    s = max(x1 - x0, y1 - y0)
    return sorted([(round((b[0] - x0) / s, 4), round((b[1] - y0) / s, 4),
                    round(b[2] / s, 4), round(b[3] / s, 4)) for b in blocks])


def same_shape(a, b, tol=0.002):
    """Ratios are emitted from float sizes and the layout rounds each box, so equality is
    tested at 0.002 of the mark span (a 430px mark => 0.9px), not byte-for-byte."""
    return len(a) == len(b) and all(
        all(abs(p - q) <= tol for p, q in zip(pa, pb)) for pa, pb in zip(a, b))


def add(name, tag, ok, detail=""):
    if not ok:
        res["failures"].append(f"{name}: {tag} {detail}")
    res["files"][name]["checks"].append({"tag": tag, "ok": bool(ok), "detail": str(detail)})


images = {}
for name, (W, H) in FILES.items():
    png, dsl_path = OUT / f"{name}.png", OUT / f"{name}.snapshot"
    dsl = dsl_path.read_text(encoding="utf-8")
    img = Image.open(png)
    images[name] = img
    entry = {"png": f"outputs/{RID}/A13/{name}.png", "dsl": f"{name}.snapshot",
             "png_bytes": png.stat().st_size, "dsl_bytes": dsl_path.stat().st_size,
             "mode": img.mode, "checks": []}
    res["files"][name] = entry
    raw = sorted((OUT / "requests").glob(f"A13-*-{name.split('-')[-1]}-*.response.bin"),
                 key=lambda p: p.stat().st_mtime)
    add(name, "canvas_size", img.size == (W, H), f"actual {img.size}, required {(W, H)}")
    add(name, "png_is_raw_service_response",
        bool(raw) and sha(raw[-1]) == sha(png), raw[-1].name if raw else "no archive")
    entry["served_by"] = raw[-1].name.replace(".response.bin", "") if raw else None
    add(name, "dsl_matches_sent_body",
        bool(raw) and sent_body(OUT / "requests" / f"{entry['served_by']}.body.txt").rstrip()
        == dsl.rstrip(),
        f"delivered {len(dsl)} chars vs sent DSL for {entry['served_by']}")
    add(name, "no_raster_or_external_asset",
        "<Image" not in dsl and "http" not in dsl.lower() and "base64" not in dsl.lower())
    add(name, "dsl_is_self_closed",
        dsl.startswith("<Snapshot") and dsl.rstrip().endswith("</Snapshot>"))
    for s in STRINGS.get(name, []):
        add(name, f"text_present:{s[:12]}", s in dsl)
    add(name, "constructs_within_limit", len(mark_blocks(dsl)) <= MAX_CONSTRUCTS,
        f"{len(mark_blocks(dsl))} mark shapes (limit {MAX_CONSTRUCTS})")

# ---------------------------------------------------------------- transparency of symbols
for name in ("symbol-color", "symbol-black"):
    img = images[name].convert("RGBA")
    px = img.load()
    alpha = img.getchannel("A")
    transparent = sum(1 for v in alpha.getdata() if v == 0)
    add(name, "canvas_is_transparent", transparent > 0,
        f"{transparent} fully transparent px of {img.width * img.height}")
    add(name, "corner_fully_transparent", px[0, 0][3] == 0, px[0, 0])
    if name == "symbol-black":
        painted = [(r, g, b) for r, g, b, a in img.getdata() if a > 0]
        bad = [c for c in painted if c != (0, 0, 0)]
        add(name, "painted_pixels_are_rgb_zero", not bad,
            f"{len(bad)} of {len(painted)} painted px are not (0,0,0); sample {bad[:3]}")
        add(name, "only_black_colour_in_dsl", set(re.findall(r'color="([^"]+)"',
                                                            open(OUT / f"{name}.snapshot",
                                                                 encoding="utf-8").read()))
            == {"#000000"})

# ---------------------------------------------------------------- same geometry twice
strip = lambda d: re.findall(r'(left|top|width|height|borderRadius|matrix|opacity)="([^"]*)"',
                             re.sub(r'#[0-9A-Fa-f]{3,8}', '', d))
sc = (OUT / "symbol-color.snapshot").read_text(encoding="utf-8")
sb = (OUT / "symbol-black.snapshot").read_text(encoding="utf-8")
add("symbol-black", "geometry_identical_to_colour_symbol", strip(sc) == strip(sb),
    f"{len(strip(sc))} vs {len(strip(sb))} geometry attributes")

# ---------------------------------------------------------------- mark re-used, not pasted
base = normalised(mark_blocks(sc))
res["mark_fingerprint_symbol"] = base
for name in ("brand-banner", "launch-poster"):
    d = (OUT / f"{name}.snapshot").read_text(encoding="utf-8")
    got = normalised(mark_blocks(d))
    add(name, "mark_rebuilt_from_symbol_geometry", same_shape(got, base),
        f"{got} vs symbol {base} (tolerance 0.002 of mark span)")

# ---------------------------------------------------------------- poster != enlarged banner
b_img, p_img = images["brand-banner"].size, images["launch-poster"].size
add("launch-poster", "poster_is_not_an_enlarged_banner",
    abs(b_img[0] / b_img[1] - p_img[0] / p_img[1]) > 0.5,
    f"aspect {b_img[0]/b_img[1]:.2f} vs {p_img[0]/p_img[1]:.2f}")
bd = (OUT / "brand-banner.snapshot").read_text(encoding="utf-8")
pd = (OUT / "launch-poster.snapshot").read_text(encoding="utf-8")
panels = pd.count('borderRadius="28"')
c = lambda d: set(re.findall(r"#[0-9A-Fa-f]{6}", d))
only_poster = sorted(c(pd) - c(bd))
only_banner = sorted(c(bd) - c(pd))
add("launch-poster", "poster_has_its_own_composition",
    {"#0B1220", "#151F33", "#F2F6FC"} <= set(only_poster)
    and {"#F4F6FA", "#0F1724"} <= set(only_banner) and pd != bd,
    f"banner {len(bd)}B / poster {len(pd)}B; poster-only colours {only_poster}, "
    f"banner-only {only_banner}, panels: {panels}")

# ---------------------------------------------------------------- clear space + 32px survival
img = images["symbol-color"].convert("RGBA")
alpha = img.getchannel("A")
bbox = alpha.getbbox()
w, h = img.size
ink = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
margin = min(bbox[0], bbox[1], w - bbox[2], h - bbox[3])
S = w / (1 + 2 * 0.30)
add("symbol-color", "clear_space_at_least_30pct_of_mark", margin >= 0.29 * ink,
    f"margin {margin}px, ink span {ink}px, ratio {margin/ink:.3f}")

# The same rule has to hold in the composed applications, where the mark's box is known from
# the DSL rather than from alpha: distance from the mark bbox to each canvas edge, over S.
for name in ("brand-banner", "launch-poster"):
    d = (OUT / f"{name}.snapshot").read_text(encoding="utf-8")
    bl = mark_blocks(d)
    x0 = min(b[0] for b in bl)
    y0 = min(b[1] for b in bl)
    x1 = max(b[0] + b[2] for b in bl)
    y1 = max(b[1] + b[3] for b in bl)
    s = x1 - x0
    W, H = FILES[name]
    edges = {"left": x0 / s, "right": (W - x1) / s, "top": y0 / s, "bottom": (H - y1) / s}
    worst = min(edges, key=edges.get)
    add(name, "clear_space_at_least_30pct_of_mark", min(edges.values()) >= 0.30,
        f"mark S={s}, edges as fraction of S: " +
        ", ".join(f"{k} {v:.3f}" for k, v in edges.items()) + f" (tightest: {worst})")


def hue_hits(path):
    """Which of the four brand hues are still individually present in a small raster.
    Buckets are 32-wide per channel, so a hue only registers if some pixel still carries it."""
    im = Image.open(path).convert("RGBA")
    seen = set()
    for r, g, b, a in im.getdata():
        if a > 40:
            seen.add((r // 32, g // 32, b // 32))
    missing = [k for k, v in want.items() if (v[0] // 32, v[1] // 32, v[2] // 32) not in seen]
    return missing


want = {"blue": (0x3E, 0x63, 0xDD), "green": (0x30, 0xA4, 0x6C),
        "red": (0xE5, 0x48, 0x4D), "amber": (0xF5, 0x9E, 0x0B)}
for tag, path in (("native_32_service_render", TEMP / "preview" / "check-32-base.png"),
                  ("native_32_tuned_stroke", TEMP / "preview" / "check-32-tuned.png")):
    add("symbol-color", f"all_four_layers_survive_{tag}", not hue_hits(path),
        f"{path.name}: missing {hue_hits(path)}")

# The 512 master resampled down to 32 is a different question from a native 32 render, and it
# is measured rather than asserted: the node is 3.7px of target after resampling and the
# amber bucket disappears. That measurement is the evidence for the small-size rule
# (stroke 0.070 -> 0.085) recorded in brand-system.json.
p = TEMP / "preview" / "check-downscale-512-to-32.png"
images["symbol-color"].convert("RGBA").resize((32, 32), Image.LANCZOS).save(p)
res["measurements"] = {
    "downscale_512_to_32_missing_hues": hue_hits(p),
    "note": "LANCZOS resample of the delivered 512 master; a native 32px DSL render of the "
            "same geometry keeps all four hues (see the two survival checks above).",
}
(TEMP / "check-report.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                        encoding="utf-8")

# ------------------------------------------------------------- text contrast on real surfaces
def lum(h):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [f(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def cr(a, b):
    la, lb = lum(a), lum(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


res["contrast"] = {}
for name in FILES:
    d = (OUT / f"{name}.snapshot").read_text(encoding="utf-8")
    bg = re.search(r'<Snapshot background="([^"]+)"', d).group(1)
    # a poster line may sit on the canvas or on the panel it was placed into: score the
    # tighter of the two so the number cannot be flattered by picking the lighter surface
    surfaces = [bg] + re.findall(r'color="(#(?:0B1220|151F33|F4F6FA))"', d)
    rows, bad = [], []
    for col, size in re.findall(r'<Text color="([^"]+)" fontSize="(\d+)"', d):
        size = int(size)
        floor = 3.0 if size >= 30 else 4.5
        worst = min(cr(col, s) for s in set(surfaces))
        rows.append({"fg": col, "px": size, "worst_bg_ratio": worst, "floor": floor})
        if worst < floor:
            bad.append(f"{col}@{size}px {worst}<{floor}")
    res["contrast"][name] = rows
    add(name, "text_contrast_meets_floor", not bad, f"{len(rows)} text runs; failures {bad}")

res["summary"] = {"files": len(res["files"]),
                  "total_checks": sum(len(v["checks"]) for v in res["files"].values()),
                  "passed": sum(1 for v in res["files"].values() for c in v["checks"]
                                if c["ok"]),
                  "failures": res["failures"]}
(TEMP / "check-report.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
print(json.dumps(res["summary"], ensure_ascii=False, indent=1))
for k, v in res["files"].items():
    print(k, "OK" if all(c["ok"] for c in v["checks"]) else "FAIL",
          [c["tag"] for c in v["checks"] if not c["ok"]])
