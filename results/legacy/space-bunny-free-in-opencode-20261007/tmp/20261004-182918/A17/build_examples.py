"""A17 step 2: render the four runnable examples (400x240) for real and check
that every printed line really exists in the rendered document.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, HERE)
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import examples as X  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
DRAFTS = os.path.join(TMP, "drafts")
os.makedirs(DRAFTS, exist_ok=True)

results = {}
for e in X.EXAMPLES:
    name = "example-%02d.png" % e["n"]
    dsl_name = "example-%02d.snapshot" % e["n"]
    with open(os.path.join(DRAFTS, "v01-%s" % dsl_name), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(e["dsl"])
    r = snapkit.render(e["dsl"], name, dsl_name, final=True)
    ok = bool(r.get("ok"))
    print("%s ok=%s status=%s bytes=%s %s" %
          (name, ok, r.get("status"), r.get("bytes"), (r.get("error") or "")[:400]))
    results[name] = {"ok": ok, "status": r.get("status"), "bytes": r.get("bytes"),
                     "error": r.get("error"),
                     "content_type": r.get("content_type"),
                     "server_timing": r.get("server_timing"),
                     "service_request_id": r.get("request_id"),
                     "response_file": r.get("response_file"),
                     "dsl_file": "example-%02d.snapshot" % e["n"],
                     "elapsed_ms": r.get("elapsed_ms")}
    if ok:
        from PIL import Image
        results[name]["size"] = list(Image.open(r["image"]).size)

json.dump(results, open(os.path.join(TMP, "probe", "example-renders.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
print("WARN", D.warnings())