"""Build + render driver for A21.

Usage:
  python a21_run.py --round 1 --format portrait --version v001 --kind baseline
  python a21_run.py --round 3 --format portrait --version v001 --kind baseline --mode notext

The DSL is written under tmp/<run>/A21/dsl/r<round>/ and the PNG under
tmp/<run>/A21/renders/r<round>/.  Rendering goes through the shared
snapshot_client.py (curl transport) so requests.jsonl is appended there.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A21" / "scripts"))

import a21_build  # noqa: E402
import snapshot_client as sc  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--format", required=True, choices=["portrait", "wide"])
    ap.add_argument("--version", required=True)
    ap.add_argument("--kind", default="baseline")
    ap.add_argument("--mode", default="text", choices=["text", "notext"])
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    task_tmp = ROOT / "tmp" / RUN / "A21"
    canvas = a21_build.LAYOUTS[args.round](args.format)
    dsl_text = canvas.dsl(args.mode)
    tag = f"r{args.round}-{args.format}-{args.version}" + ("-notext" if args.mode == "notext" else "")
    dsl_dir = task_tmp / "dsl" / f"r{args.round}"
    dsl_path = dsl_dir / f"{tag}.snapshot"
    meta_path = dsl_dir / f"{tag}.runs.json"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    dsl_path.write_text(dsl_text, encoding="utf-8")
    meta = {
        "round": args.round, "format": args.format, "version": args.version,
        "mode": args.mode, "theme": canvas.pal["theme"],
        "canvas": {"width": canvas.w, "height": canvas.h},
        "dsl": dsl_path.relative_to(ROOT).as_posix(),
        "runs": canvas.runs,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"DSL {dsl_path.relative_to(ROOT).as_posix()} ({len(dsl_text)} chars, "
          f"{len(canvas.runs)} runs)")
    if args.no_render:
        return 0

    out_dir = task_tmp / "renders" / f"r{args.round}"
    out_png = out_dir / f"{tag}.png"
    rec = sc.render_text(dsl_text, "A21", f"launch-{args.format}", tag, out_png,
                         args.kind, dsl_path)
    print(json.dumps({k: rec.get(k) for k in ("id", "http_status", "content_type",
                                              "request_id", "duration_ms", "bytes",
                                              "pixels", "error", "response_file")},
                     ensure_ascii=False, indent=2))
    return 0 if rec.get("http_status") == 200 else 2


if __name__ == "__main__":
    raise SystemExit(main())
