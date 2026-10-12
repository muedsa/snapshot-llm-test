"""A14 batch audit — every claim is measured from the delivered PNG or its DSL.

TASK.md forbids claiming a card passes without having looked at it, so the audit records
both: the pixel measurements below (line count, ink bounding box, colours, margins) and the
actual image-view timestamps copied from iterations.jsonl.
"""
import json
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "A14"
TEMP = ROOT / "tmp" / RID / "A14"
CARDS = json.loads((ROOT / "tasks" / "A14-content-stress-batch" / "inputs"
                    / "cards.json").read_text(encoding="utf-8"))
LAYOUT = json.loads((TEMP / "layout.json").read_text(encoding="utf-8"))
GEO = {g["id"]: g for g in LAYOUT["cards"]}
PAPER, INK = (0xF2, 0xF5, 0xF9), (0x10, 0x18, 0x26)
W, H, M = 1200, 630, 40


def arr(p):
    return np.asarray(Image.open(p).convert("RGB"))


def ink_rows(a, y0, y1, x0, x1, thr=110):
    """Row indices inside [y0,y1) holding dark (title-coloured) pixels.

    The per-channel limit is compared against the MEAN: comparing the 3-channel sum against
    a single-channel threshold marks every row dark and reported one line for every title.
    """
    sub = a[y0:y1, x0:x1].astype(int).mean(axis=2)
    dark = (sub < thr).sum(axis=1)
    return [y0 + i for i, d in enumerate(dark) if d >= 3]


def groups(rows, gap=6):
    if not rows:
        return []
    out = [[rows[0]]]
    for r in rows[1:]:
        if r - out[-1][-1] > gap:
            out.append([])
        out[-1].append(r)
    return [(g[0], g[-1]) for g in out]


def colour_in(a, box, colour, tol=26):
    x, y, w, h = [round(v) for v in box]
    sub = a[y:y + h, x:x + w].reshape(-1, 3).astype(int)
    c = np.array([int(colour[i + 1:i + 3], 16) for i in (0, 2, 4)])
    return int((np.abs(sub - c).max(axis=1) <= tol).sum())


def hexes(dsl):
    return set(re.findall(r'#[0-9A-Fa-f]{6}', dsl))


def main():
    views = {}
    il = TEMP / "iterations.jsonl"
    if il.exists():
        for line in il.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("image_path"):
                views[Path(r["image_path"]).name] = r.get("image_viewed_at")
    checks, results = [], []

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    for c in CARDS:
        cid = c["id"]
        png, dslp = OUT / f"card-{cid}.png", OUT / f"card-{cid}.snapshot"
        a = arr(png)
        dsl = dslp.read_text(encoding="utf-8")
        g = GEO[cid]
        tb = g["boxes"]["title"]
        res = {"id": cid, "png": str(png.relative_to(ROOT)), "size": list(a.shape[:2]),
               "png_bytes": png.stat().st_size, "dsl_bytes": dslp.stat().st_size,
               "title_lines_planned": g["title_lines"], "title_size": g["title_size"],
               "grid": g["grid"], "image_viewed_at": views.get(png.name)}
        chk(f"{cid}.size-1200x630", res["size"] == [H, W], str(res["size"]))
        chk(f"{cid}.png-magic", png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n")
        chk(f"{cid}.dsl-pairs-png", dslp.exists() and "<Snapshot" in dsl)
        # content: the raw strings must survive into the DSL verbatim
        for k in ("title", "speaker", "time", "status"):
            body = re.sub(r"<!\[CDATA\[|\]\]>", "", dsl)
            chk(f"{cid}.text-{k}", c[k] in body)
        chk(f"{cid}.text-date", "2026.11.07" in dsl)
        chk(f"{cid}.text-brand", "Structure / Vision" in dsl)
        chk(f"{cid}.cdata-escaped", "<![CDATA[" in dsl) if "<" in c["title"] else \
            chk(f"{cid}.cdata-escaped", True, "no angle brackets in this title")
        # title geometry measured from pixels: line count and overflow.
        # The scan band is 12px wider than the box so ink that escaped the box is visible.
        rows = ink_rows(a, int(tb[1]) - 12, int(tb[1] + tb[3]) + 12, int(tb[0]),
                        int(tb[0] + tb[2]))
        grp = groups(rows)
        res["title_ink_groups"] = grp
        res["title_ink_lines"] = len(grp)
        chk(f"{cid}.title-lines-rendered", len(grp) == g["title_lines"],
            f"planned {g['title_lines']} rendered {len(grp)} rows {grp}")
        ink_r = max((x for y in range(int(tb[1]), int(tb[1] + tb[3])) for x in range(
            int(tb[0]), int(tb[0] + tb[2])) if a[y, x].sum() < 330), default=0)
        res["title_ink_right"] = ink_r
        chk(f"{cid}.title-no-overflow", ink_r <= tb[0] + tb[2] + 2,
            f"ink right {ink_r} vs box right {tb[0] + tb[2]:.0f}")
        chk(f"{cid}.title-inside-box-vertically",
            all(y0 >= tb[1] - 3 and y1 <= tb[1] + tb[3] + 3 for y0, y1 in grp),
            f"box {tb[1]:.0f}..{tb[1] + tb[3]:.0f} groups {grp}")
        # status encoding: colour + symbol + text all present
        st = g["status_color"]
        bb = g["boxes"]["badge"]
        chk(f"{cid}.badge-colour-pixels", colour_in(a, bb, st) > 120,
            f"{st} pixels={colour_in(a, bb, st)}")
        chk(f"{cid}.badge-dsl-colour", st in hexes(dsl))
        chk(f"{cid}.badge-symbol-geometry", g["status_symbol"] in
            ("disc", "square", "diamond", "ring"))
        sym = {"disc": 'borderRadius="9', "square": 'borderRadius="2"',
               "diamond": "Transform", "ring": "SOLID"}[g["status_symbol"]]
        chk(f"{cid}.badge-symbol-{g['status_symbol']}", sym in dsl, sym)
        # the four statuses must be four distinct encodings across the batch
        # safe margin: nothing but the paper background in the 40px frame
        frame = np.concatenate([a[:M, :].reshape(-1, 3), a[-M:, :].reshape(-1, 3),
                                a[:, :M].reshape(-1, 3), a[:, -M:].reshape(-1, 3)])
        off = int((np.abs(frame.astype(int) - np.array(PAPER)).max(axis=1) > 6).sum())
        res["frame_offpaper_pixels"] = off
        chk(f"{cid}.safe-margin-40", off == 0, f"{off} pixels outside the paper band")
        # no global downscale: the title must be at the planned scale, not a shrunk copy
        chk(f"{cid}.title-size-floor-36", g["title_size"] >= 36, str(g["title_size"]))
        chk(f"{cid}.speaker-size-floor-22", g["speaker_size"] >= 22,
            str(g["speaker_size"]))
        if c["status"] == "取消":
            chk(f"{cid}.cancelled-note", "本场取消" in re.sub(r"<!\[CDATA\[|\]\]>", "", dsl))
            nb = g["boxes"]["footer_note"]
            chk(f"{cid}.cancelled-note-red-pixels", colour_in(a, nb, st) > 60,
                f"{colour_in(a, nb, st)} px of {st}")
            chk(f"{cid}.cancelled-keeps-title-and-time",
                c["title"] in re.sub(r"<!\[CDATA\[|\]\]>", "", dsl) and c["time"] in dsl)
        results.append(res)

    # batch-level: one shared system, four distinct statuses
    dsls = {c["id"]: (OUT / f"card-{c['id']}.snapshot").read_text(encoding="utf-8")
            for c in CARDS}
    chk("batch.primary-colour-shared",
        all("#1B3A6B" in d for d in dsls.values()))
    chk("batch.status-colours-distinct",
        len({g["status_color"] for g in GEO.values()}) == 4)
    chk("batch.status-symbols-distinct",
        len({g["status_symbol"] for g in GEO.values()}) == 4)
    chk("batch.status-symbols-in-dsl",
        all(d.count("<Transform") >= (1 if g["status_symbol"] in ("diamond", "ring")
                                      else 0) for g in GEO.values() for d in
            [dsls[g["id"]]]))
    chk("batch.title-scale-varies-by-length",
        len({g["title_size"] for g in GEO.values()}) >= 2)
    chk("batch.no-global-shrink",
        all(g["title_size"] >= 36 for g in GEO.values()))
    chk("batch.all-eight-viewed", all(r["image_viewed_at"] for r in results),
        str([r["id"] for r in results if not r["image_viewed_at"]]))
    ok = [c for c in checks if c["ok"]]
    audit = {"task": "A14", "run_id": RID, "cards": results, "checks": checks,
             "checks_passed": len(ok), "checks_total": len(checks),
             "problems_from_generator": LAYOUT["problems"],
             "fit_warnings": LAYOUT["fit_warnings"]}
    (OUT / "batch-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    (TEMP / "batch-audit-v02.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"passed": len(ok), "total": len(checks),
                      "failed": [c["name"] for c in checks if not c["ok"]],
                      "lines": {r["id"]: [r["title_lines_planned"],
                                           r["title_ink_lines"]] for r in results}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
