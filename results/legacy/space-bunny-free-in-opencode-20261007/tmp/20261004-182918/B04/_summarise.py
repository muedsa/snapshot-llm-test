"""B04: summarise the real request log per case, so case.md / portfolio.json can
cite actual request ids, byte counts and image dimensions.
"""
import io
import json
import os
import re

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B04")
OUT = os.path.join(ROOT, "outputs", RUN, "B04")

reqs = [json.loads(l) for l in io.open(os.path.join(TMP, "requests.jsonl"),
                                        encoding="utf-8") if l.strip()]
renders = [r for r in reqs if r["request_type"] == "render"]
other = [r for r in reqs if r["request_type"] != "render"]

by_case = {}
for r in renders:
    rf = r.get("request_file") or ""
    m = re.search(r"[\\/]B04[\\/](case-\d\d)[\\/]", rf)
    if m:
        by_case.setdefault(m.group(1), []).append(r)

summary = {}
for case, rs in sorted(by_case.items()):
    ok = [r for r in rs if (r.get("content_type") or "").startswith("image/")]
    bad = [r for r in rs if r not in ok]
    png = os.path.join(OUT, case, "final.png")
    w, h = Image.open(png).size
    dsl = io.open(os.path.join(OUT, case, "final.snapshot"), encoding="utf-8").read()
    summary[case] = {
        "attempts": len(rs),
        "ok": len(ok),
        "failed": [{"request_id": r["request_id"], "http_status": r["http_status"],
                    "error": (r.get("error_summary") or "")[:160]}
                   for r in bad],
        "successful_request_ids": [r["request_id"] for r in ok],
        "final_request_id": ok[-1]["request_id"] if ok else None,
        "server_request_id": ok[-1].get("service_request_id") if ok else None,
        "bytes": os.path.getsize(png),
        "dimensions": [w, h],
        "dsl_bytes": len(dsl.encode("utf-8")),
        "element_tags": dsl.count("<Positioned") + dsl.count("<Container")
        + dsl.count("<Text"),
        "last_duration_ms": ok[-1]["duration_ms"] if ok else None,
    }

summary["_other_requests"] = [
    {"request_id": r["request_id"], "type": r["request_type"], "url": r["url"],
     "http_status": r["http_status"]} for r in other]
summary["_totals"] = {
    "render_attempts": len(renders),
    "render_ok": len([r for r in renders
                      if (r.get("content_type") or "").startswith("image/")]),
    "render_failed": len([r for r in renders
                          if not (r.get("content_type") or "").startswith("image/")]),
    "other_requests": len(other),
}

print(json.dumps(summary, ensure_ascii=False, indent=1))
with io.open(os.path.join(TMP, "render-summary.json"), "w",
             encoding="utf-8") as fh:
    fh.write(json.dumps(summary, ensure_ascii=False, indent=2))
