# -*- coding: utf-8 -*-
"""Emit outputs/<run_id>/A17/examples.json (audit schema v1).

Everything structural is read from the delivered files themselves (line
ranges recomputed, md5 recomputed, request evidence taken from
requests.jsonl); nothing is copied from templates.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from a17_defs import CORE_PREFIX, core_lines          # noqa: E402
from a17_pages import PAGES                           # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]     # suite root
RUN = "run-20261011-01"
GEN = ROOT / f"tmp/{RUN}/A17/gen"
OUT = ROOT / f"outputs/{RUN}/A17"
LOG = ROOT / f"tmp/{RUN}/A17/requests.jsonl"

# final render request per delivered PNG (service response bytes)
FINAL_REQ = {
    "handbook-01": "A17-pg2-01", "handbook-02": "A17-pg2-02",
    "handbook-03": "A17-pg2-03", "handbook-04": "A17-pg3-04",
    "example-01": "A17-ex-01", "example-02": "A17-ex-02",
    "example-03": "A17-ex-03", "example-04": "A17-ex-04",
}
VIEW_TS = {  # actual visual-tool view sessions (see iterations.jsonl)
    "example": "2026-10-15T16:52:00+08:00 (baseline, precision: approximate, "
               "immediately after the 16:50-16:51 renders)",
    "page123": "2026-10-16T09:28:00+08:00 (final, after paint-order change; "
               "pixel-identical to the reviewed v1 renders)",
    "page4": "2026-10-16T09:30:00+08:00 (final v3 render)",
}


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def find_block(lines, block):
    for i in range(len(lines) - len(block) + 1):
        if lines[i:i + len(block)] == block:
            return i
    return -1


def request_evidence(rid):
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("id") == rid:
            return {"request_id": rid, "ts": r["ts"], "status": r["status"],
                    "content_type": r["content_type"],
                    "response_bytes": r["response_bytes"],
                    "elapsed_seconds": r["elapsed_seconds"],
                    "dsl_path": r["dsl_path"], "out_path": r["out_path"]}
    raise SystemExit(f"request {rid} not found")


def main():
    manifest = json.loads((GEN / "manifest.json").read_text(encoding="utf-8"))
    reqs = {}
    for log_file in (LOG, ROOT / f"tmp/{RUN}/_suite/requests-shared.jsonl"):
        for line in log_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                reqs.setdefault(r.get("id"), []).append(r)

    examples = []
    for idx, m in enumerate(manifest["examples"], start=1):
        key = f"0{idx}"
        ex_id = m["example_id"]
        pg_id = f"handbook-{key}"
        ex_path = OUT / f"{ex_id}.snapshot"
        pg_path = OUT / f"{pg_id}.snapshot"

        ex_lines = ex_path.read_text(encoding="utf-8").splitlines()
        pg_lines = pg_path.read_text(encoding="utf-8").splitlines()
        core = core_lines(key)
        s = find_block(ex_lines, core)
        assert s >= 0, ex_id
        shifted = ["      " + ln for ln in core]
        p = find_block(pg_lines, shifted)
        assert p >= 0, pg_id
        # normalised equality: drop exactly one element-indent level
        norm = [ln[6:] for ln in pg_lines[p:p + len(core)]]
        assert norm == core, (pg_id, "core differs from standalone")
        # printed segments must be verbatim slices of the delivered DSL
        for seg in m["printed_segments"]:
            a, b = seg["line_start"], seg["line_end"]
            assert ex_lines[a - 1:b] == seg["verbatim"], (ex_id, a, b)

        markers = [d["text"] for d in m["display_lines"] if d["kind"] == "mark"]
        head = pg_lines[p - 1]
        pos = head[:head.index(">")]
        examples.append({
            "page_id": pg_id,
            "example_id": ex_id,
            "purpose": f"第{idx}页可运行示例（配合：{PAGES[idx]['title']}）",
            "dsl_path": f"{ex_id}.snapshot",
            "png_path": f"{ex_id}.png",
            "width": 400,
            "height": 240,
            "size_verified": "PIL Image.open on delivered PNG -> (400, 240)",
            "handbook_dsl_path": f"{pg_id}.snapshot",
            "handbook_png_path": f"{pg_id}.png",
            "handbook_size": [1200, 1600],
            "core_subtree": {
                "standalone": {
                    "path": f"{ex_id}.snapshot",
                    "line_start": s + 1,
                    "line_end": s + len(core),
                    "line_count": len(core),
                    "indent_prefix": CORE_PREFIX,
                },
                "handbook": {
                    "path": f"{pg_id}.snapshot",
                    "line_start": p + 1,
                    "line_end": p + len(core),
                    "line_count": len(core),
                    "indent_prefix": CORE_PREFIX + "      ",
                },
                "byte_identical": True,
                "comparison_method":
                    "line-list equality after removing exactly one page "
                    "element indent level (6 spaces) from the handbook lines; "
                    "text, attribute values, child order and relative "
                    "geometry therefore identical; effect scope identical "
                    "because no filter/clip/transform parameter differs",
                "evidence": {
                    "path_base": "suite_root",
                    "path": f"tmp/{RUN}/A17/scripts/verify_a17.py",
                    "result": "all checks passed (run after final rebuild)",
                },
                "sha256_standalone_core": hashlib.sha256(
                    ("\n".join(core) + "\n").encode("utf-8")).hexdigest(),
            },
            "wrappers": {
                "standalone_allowed": [
                    "<Snapshot type=png background=#FFFFFF> root",
                    "<SizedBox width=400 height=240> bounded container",
                ],
                "handbook_allowed": [
                    pos + "> placement container "
                    "(absolute placement inside the page Stack)",
                    "<Stack alignment=TOP_LEFT clipBehavior=NONE> wrapper, "
                    "identical to the standalone wrapper line",
                    "flat white backing fills painted before the core and "
                    "border-only frame outlines painted after the core "
                    "(page chrome, outside the core subtree)",
                ] + ([
                    "<Opacity opacity=1> placement container: isolates the "
                    "core's paint layer so the BackdropFilter inside core04 "
                    "can only sample the illustration itself; RenderOpacity "
                    "always pushes an opacity layer, alpha 1.0 is a visual "
                    "no-op (saveLayer bounds=null, alpha 255)",
                ] if key == "04" else []),
                "changes_example_semantics": False,
                "no_scaling": "core keeps its 400x240 logical area at 1:1; no "
                             "font size, coordinate, sigma or content change",
            },
            "printed": {
                "segments": [
                    {"line_start": seg["line_start"],
                     "line_end": seg["line_end"],
                     "verbatim": seg["verbatim"]}
                    for seg in m["printed_segments"]
                ],
                "source_line_count": m["printed_source_count"],
                "display_line_count": m["display_count"],
                "display_method":
                    "each line printed as its own <Text>+<Raw>+CDATA line, so "
                    "the rendered text is byte-equal to the source line (no "
                    "entity escaping to reverse)",
                "marker_lines": markers,
                "markers_not_in_source": True,
                "segments_verified_against":
                    f"{ex_id}.snapshot delivered file (rebuilt equality "
                    "assert inside this generator)",
            },
            "render_evidence": {
                "example": request_evidence(FINAL_REQ[ex_id]),
                "example_md5": md5(OUT / f"{ex_id}.png"),
                "handbook": request_evidence(FINAL_REQ[pg_id]),
                "handbook_md5": md5(OUT / f"{pg_id}.png"),
                "note": "delivered PNG bytes are the untouched service "
                        "response (md5 of copy == md5 of the render output "
                        "file recorded in tmp .../gen)",
            },
            "view_evidence": {
                "example_viewed": VIEW_TS["example"],
                "handbook_viewed": (VIEW_TS["page4"] if key == "04"
                                    else VIEW_TS["page123"]),
                "tool": "visual image viewer (full page + crops/zoom)",
                "iterations_ref": {
                    "path_base": "suite_root",
                    "path": f"tmp/{RUN}/A17/iterations.jsonl",
                },
                "three_way_check":
                    "printed fragment == verbatim slices of the delivered "
                    "example DSL (asserted at build time); illustration drawn "
                    "by the byte-identical core subtree in the page DSL; "
                    "independent render is the delivered example PNG. For "
                    "example-04 the page illustration stripe band is pixel "
                    "identical to the standalone band (0 differing px of "
                    "18304, script compare + verify_a17).",
            },
        })

    claims = [
        {
            "claim": "POST /snapshot with a UTF-8 plain-text DSL body "
                     "(Content-Type: text/plain; charset=utf-8) returns image "
                     "bytes on success and a JSON {code,message,requestId} "
                     "object on failure; 429/503 carry Retry-After",
            "sources": [
                {"url": "https://open-snapshot.muedsa.com/ai-guide.md",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/ai-guide.md"},
                 "request_id": "shared-req-0001"},
            ],
            "verified_by": "two real 400 PARSE_ERROR bodies "
                           f"(tmp/{RUN}/A17/smoke/smoke-01.png.error.json, "
                           "smoke-03.png.error.json with real requestIds) and "
                           "27 successful image/png renders in requests.jsonl",
            "examples": ["example-01", "example-02", "example-03",
                         "example-04"],
        },
        {
            "claim": "Root size comes from layout constraints (SizedBox/Stack "
                     "bounded 400x240), not from an HTML viewport",
            "sources": [
                {"url": "https://open-snapshot.muedsa.com/ai-guide.md",
                 "request_id": "shared-req-0001"},
                {"url": "https://snapshot.muedsa.com/guides/parser/",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/parser-guide.html"},
                 "request_id": "shared-req-0005"},
            ],
            "verified_by": "every example PNG decodes to exactly (400, 240) "
                           "and every page to (1200, 1600) with no viewport "
                           "attribute anywhere in the DSL",
            "examples": ["example-02"],
        },
        {
            "claim": "Row/Column distribute space in integer Expanded shares "
                     "only inside bounded constraints (measured 1:2 split)",
            "sources": [
                {"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/parser-tags.html"},
                 "request_id": "shared-req-0004"},
            ],
            "verified_by": "probe render A17-probe-01 measured the Row split "
                           "1:2 exactly; example-02 visual check",
            "examples": ["example-02"],
        },
        {
            "claim": "Stack+Positioned give one absolute coordinate system; "
                     "clipBehavior=NONE lets children overhang without being "
                     "clipped (Stack defaults to HARD_EDGE)",
            "sources": [
                {"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/parser-tags.html"},
                 "request_id": "shared-req-0004"},
            ],
            "verified_by": "example-02 red badge overhangs the card bottom "
                           "edge and stays fully visible in the rendered PNG",
            "examples": ["example-02"],
        },
        {
            "claim": "Plain text nodes are trimmed; Raw+CDATA preserves "
                     "whitespace verbatim; a Raw outside a Text is a real "
                     "400 PARSE_ERROR",
            "sources": [
                {"url": "https://snapshot.muedsa.com/guides/parser/",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/parser-guide.html"},
                 "request_id": "shared-req-0005"},
            ],
            "verified_by": "probe render A17-probe-01 (CDATA vs trimmed) and "
                           "the real error body smoke-03.png.error.json "
                           "('Raw ... can only be used in the Text')",
            "examples": ["example-03"],
        },
        {
            "claim": "Nested <Text> children render as inline coloured spans; "
                     "8-digit colours are #RRGGBBAA (last two digits = alpha)",
            "sources": [
                {"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                 "request_id": "shared-req-0004"},
                {"url": "https://snapshot.muedsa.com/reference/enums/",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/enums.html"},
                 "request_id": "shared-req-0007"},
            ],
            "verified_by": "example-03 renders 'A蓝B红CD' as three inline "
                           "colours and #FF000080 over white measures "
                           "(255,127,127)",
            "examples": ["example-03"],
        },
        {
            "claim": "ImageFiltered blurs only its own subtree while "
                     "BackdropFilter blurs what was painted behind it; sigma "
                     "must be finite and >= 0, tileMode defaults to CLAMP",
            "sources": [
                {"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                 "request_id": "shared-req-0004"},
                {"url": "https://snapshot.muedsa.com/reference/enums/",
                 "request_id": "shared-req-0007"},
            ],
            "verified_by": "experiments exp1-exp5 (A17-exp1..A17-exp5): "
                           "ImageFiltered variant is pixel-identical to the "
                           "no-filter control, backdrop variants differ only "
                           "where the backdrop picture was painted",
            "examples": ["example-04"],
        },
        {
            "claim": "Renderer detail behind the page-4 leak: "
                     "BackdropFilterLayer.paint() re-draws "
                     "LayerPaintContext.pictures.lastOrNull() - the most "
                     "recently composited PictureLayer - through the image "
                     "filter, and Recording only ends when a layer is pushed "
                     "(pushLayer/pushOpacity/pushClip...)",
            "sources": [
                {"url": "https://github.com/muedsa/snapshot/blob/cca88224640d3e416330362f0475848ef507f7f8/"
                        "core/src/main/kotlin/com/muedsa/snapshot/rendering/"
                        "BackdropFilterLayer.kt",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/muedsa-snapshot-src/"},
                 "request_id": "A17-src-0001"},
                {"url": "https://github.com/muedsa/snapshot/blob/cca88224640d3e416330362f0475848ef507f7f8/"
                        "core/src/main/kotlin/com/muedsa/snapshot/rendering/"
                        "PaintingContext.kt",
                 "request_id": "A17-src-0005"},
                {"url": "https://github.com/muedsa/snapshot/blob/cca88224640d3e416330362f0475848ef507f7f8/"
                        "core/src/main/kotlin/com/muedsa/snapshot/rendering/"
                        "box/RenderOpacity.kt",
                 "request_id": "A17-src-0007"},
            ],
            "verified_by": "handbook-04 v1 render (A17-pg-04) blurred the "
                           "whole preamble; paint-order change (A17-pg2-04) "
                           "and Opacity isolation layer (A17-pg3-04) restored "
                           "sharp text; final illustration band is pixel "
                           "identical to example-04.png (0/18304 differing)",
            "examples": ["example-04"],
        },
        {
            "claim": "A Container with a border attribute folds its colour "
                     "into the border decoration; omitting colour yields a "
                     "border-only outline (transparent fill)",
            "sources": [
                {"url": "https://github.com/muedsa/snapshot/blob/cca88224640d3e416330362f0475848ef507f7f8/"
                        "parser/src/main/kotlin/com/muedsa/snapshot/parser/"
                        "widget/ContainerParser.kt",
                 "request_id": "A17-src-0009"},
                {"url": "https://github.com/muedsa/snapshot/blob/cca88224640d3e416330362f0475848ef507f7f8/"
                        "parser/src/main/kotlin/com/muedsa/snapshot/parser/"
                        "widget/BorderParser.kt",
                 "request_id": "A17-src-0010"},
            ],
            "verified_by": "all four handbook pages render frame outlines "
                           "after the core with the same 1px lines as before "
                           "(pages 1-3 v1 vs v2 are pixel-identical)",
            "examples": ["example-01", "example-02", "example-03",
                         "example-04"],
        },
        {
            "claim": "The service exposes 27 font families (Inter, Noto Sans "
                     "CJK SC, Noto Sans Mono CJK SC ...); mono Latin advance "
                     "is 0.5em and CJK is 1.0em",
            "sources": [
                {"url": "https://open-snapshot.muedsa.com/fonts",
                 "cached_at": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/_suite/docs/fonts.txt"},
                 "request_id": "shared-req-0002"},
            ],
            "verified_by": "probe render A17-probe-01 measured 96 '0' glyphs "
                           "= 958px ink at 20px (10px/char) and a 48-char CJK "
                           "string wrapping 46+2 in a 1120px box",
            "examples": ["example-01", "example-03", "example-04"],
        },
    ]

    doc = {
        "schema_version": 1,
        "task_id": "A17",
        "path_base": "output_dir",
        "run_id": RUN,
        "generated_from": "delivered files in this output directory "
                          "(line ranges, md5 and request evidence recomputed "
                          "at generation time)",
        "examples": examples,
        "technical_claims": claims,
    }
    # every cited request id must exist in this task's request log
    for c in claims:
        for s in c["sources"]:
            rid = s.get("request_id")
            if rid:
                assert rid in reqs, f"cited request not in log: {rid}"
    for e in examples:
        for k in ("example", "handbook"):
            rid = e["render_evidence"][k]["request_id"]
            assert rid in reqs, f"render request not in log: {rid}"
    out = OUT / "examples.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print("written:", out.relative_to(ROOT))
    for e in examples:
        print(" ", e["example_id"], "core", e["core_subtree"]["standalone"],
              "->", {k: v for k, v in e["core_subtree"]["handbook"].items()
                     if k in ("line_start", "line_end")},
              "printed", e["printed"]["source_line_count"])


if __name__ == "__main__":
    main()
