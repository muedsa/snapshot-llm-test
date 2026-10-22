# -*- coding: utf-8 -*-
"""A17 driver: emit 4 standalone examples + 4 handbook pages + manifest.

Outputs land in tmp/run-20261011-01/A17/gen/ first (draft stage); final
copies move to outputs/run-20261011-01/A17/ only after visual approval.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from a17_defs import (OUT, TMP, CORE_PREFIX, core_lines, print_plan,
                      standalone_text)          # noqa: E402
from a17_pages import build_page                # noqa: E402

GEN = TMP / "gen"
GEN.mkdir(parents=True, exist_ok=True)


def main():
    manifest = {"examples": [], "pages": []}
    for n in ("01", "02", "03", "04"):
        text = standalone_text(n)
        p = GEN / f"example-{n}.snapshot"
        p.write_text(text, encoding="utf-8")
        plan = print_plan(n)
        assert 8 <= plan["source_count"] <= 18, (n, plan["source_count"])
        segs = [{"line_start": a, "line_end": b,
                 "verbatim": plan["lines"][a - 1:b]} for a, b in plan["segments"]]
        manifest["examples"].append({
            "example_id": f"example-{n}",
            "dsl_path": f"tmp/run-20261011-01/A17/gen/example-{n}.snapshot",
            "total_lines": len(plan["lines"]),
            "core_prefix": CORE_PREFIX,
            "core_line_count": len(core_lines(n)),
            "printed_segments": segs,
            "printed_source_count": plan["source_count"],
            "display_count": plan["display_count"],
            "display_lines": [{"kind": k, "text": t}
                              for k, t in plan["display"]],
        })
        print(f"example-{n}: {len(plan['lines'])} lines, core "
              f"{len(core_lines(n))}, printed {plan['source_count']} "
              f"(display {plan['display_count']}), segs "
              f"{plan['segments']}")

    for n in (1, 2, 3, 4):
        body, stats = build_page(n)
        (GEN / f"handbook-{n:02d}.snapshot").write_text(body, encoding="utf-8")
        manifest["pages"].append({
            "page": f"handbook-{n:02d}",
            "dsl_path": f"tmp/run-20261011-01/A17/gen/handbook-{n:02d}.snapshot",
            "body_elements": stats["body"],
            "printed_code_lines": stats["code"],
            "marker_lines": stats["markers"],
            "code_card_end": stats["card_end"],
            "content_bottom": stats["last_bottom"],
        })
        print(f"handbook-{n:02d}: body {stats['body']}, code "
              f"{stats['code']}, markers {stats['markers']}, card_end "
              f"{stats['card_end']}, bottom {stats['last_bottom']}")

    (GEN / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    total_code = sum(p["printed_code_lines"] for p in manifest["pages"])
    total_body = sum(p["body_elements"] for p in manifest["pages"])
    print(f"TOTAL printed code lines: {total_code} (>=20 required)")
    print(f"TOTAL body elements: {total_body} (>=24 required)")
    assert total_code >= 20
    assert total_body >= 24
    print("manifest written:", GEN / "manifest.json")


if __name__ == "__main__":
    main()
