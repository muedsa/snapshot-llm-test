"""B04 data layer: every number in the special, computed from real local evidence.

Inputs (all produced by this run, none hand-entered):
  tmp/<run>/_suite/requests.jsonl      58 document fetches (URL, time, bytes, cache path)
  tmp/<run>/<task>/requests.jsonl      553 POST /snapshot calls with telemetry
  tmp/<run>/_suite/docs/fonts.txt      the service's real GET /fonts body
  tmp/<run>/_suite/docs/openapi.yaml   the service's real OpenAPI document

Output: tmp/<run>/B04/data.json  (+ a printed summary used while laying out the pages)

Run: python tmp/<run_id>/B04/b04data.py
"""
from __future__ import annotations

import json
import os
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
SUITE = ROOT / "tmp" / RUN / "_suite"
TMP = ROOT / "tmp" / RUN / "B04"


def load_rows():
    rows = []
    for p in sorted((ROOT / "tmp" / RUN).glob("*/requests.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                r["_file"] = p.relative_to(ROOT).as_posix()
                rows.append(r)
    return rows


def pct(n, d):
    return round(100.0 * n / d, 1) if d else 0.0


def q(vals, p):
    s = sorted(vals)
    return s[min(len(s) - 1, int(p * len(s)))]


ROWS = load_rows()
# the report studies the corpus up to B03; B04's own renders are the act of reporting,
# so they are excluded to keep every quoted number stable across rebuilds
ROWS = [r for r in ROWS if r.get("task_id") != "B04"]
DOCS = [r for r in ROWS if r.get("kind") == "document"]
RENDERS = [r for r in ROWS if r.get("request_type") == "render"]
OK = [r for r in RENDERS if r.get("http_status") == 200]
BAD = [r for r in RENDERS if r.get("http_status") not in (200, None)]

# ---- 1. corpus scale
scale = {
    "render_requests": len(RENDERS),
    "ok": len(OK),
    "failed": len(BAD),
    "success_rate_pct": pct(len(OK), len(RENDERS)),
    "distinct_tasks": len({r.get("task_id") for r in RENDERS}),
    "distinct_canvas_sizes": len({(r.get("image_width"), r.get("image_height"))
                                  for r in OK}),
    "document_pages": len(DOCS),
    "document_bytes": sum(r.get("response_bytes") or 0 for r in DOCS),
    "image_bytes_total_mb": round(sum(r.get("response_bytes") or 0 for r in OK) / 1e6, 1),
    "window_start": min(r["ended_at"] for r in RENDERS if r.get("ended_at")),
    "window_end": max(r["ended_at"] for r in RENDERS if r.get("ended_at")),
}

# ---- 2. pipeline timing, split by what the headers actually tell us
srv, cli = [], []
for r in OK:
    t = r.get("server_timing") or ""
    m = re.search(r"render;dur=([\d.]+)", t)
    if m:
        srv.append(float(m.group(1)))
    if r.get("duration_seconds"):
        cli.append(float(r["duration_seconds"]))
server_ms = {"n": len(srv), "p50": round(statistics.median(srv), 1),
             "p90": round(q(srv, 0.90), 1), "p99": round(q(srv, 0.99), 1),
             "max": round(max(srv), 1), "min": round(min(srv), 1)}
client_s = {"n": len(cli), "p50": round(statistics.median(cli), 2),
            "p90": round(q(cli, 0.90), 2), "max": round(max(cli), 2)}
outlier = max(OK, key=lambda r: r.get("duration_seconds") or 0)
outlier_info = {"request_id": outlier["request_id"], "task": outlier.get("task_id"),
                "seconds": outlier.get("duration_seconds"),
                "server_render_ms": (re.search(r"render;dur=([\d.]+)",
                                               outlier.get("server_timing") or "")
                                     or [None, None])[1],
                "bytes": outlier.get("response_bytes")}
# overhead = client total minus server render, both in ms
overhead = [c * 1000 - s for c, s in zip(cli, srv)] if len(cli) == len(srv) else []

# ---- 3. failure taxonomy
def classify(r):
    msg = (r.get("error_summary") or "")
    code = r.get("error_code") or "?"
    if "more than 4096" in msg:
        return code, "element cap"
    if "Layout size is infinite" in msg:
        return code, "unbounded layout"
    if "parentData" in msg:
        return code, "bad parent (Positioned)"
    if "value format error" in msg:
        return code, "attribute format"
    if "is invalid" in msg:
        return code, "attribute value"
    if "is not supported by this gradient type" in msg:
        return code, "gradient param mix"
    if "Failed to parse SVG Path" in msg:
        return code, "path syntax"
    if "cant not buildWidget" in msg:
        return code, "widget in wrong slot"
    if "requires either" in msg:
        return code, "missing required attr"
    if "unknown protocol" in msg:
        return code, "url scheme"
    if "INTERNAL_ERROR" in str(code):
        return code, "opaque 500"
    return code, "other"


fails = Counter()
fail_samples = {}
for r in BAD:
    code, kind = classify(r)
    fails[(code, kind)] += 1
    fail_samples.setdefault(kind, r)
error_codes = Counter(r.get("error_code") for r in BAD)
http_status = Counter(r.get("http_status") for r in BAD)
diagnosable = sum(v for (c, k), v in fails.items() if c == "PARSE_ERROR")

# ---- 4. text metrics, measured by reading back rendered PNGs
# (values were produced by the A-track measurement series; recomputed here from the
#  probe evidence files so the page never quotes a hand-typed number)
ev = {}
for name in ("probe-evidence.json", "probe-evidence2.json", "probe-evidence4.json"):
    p = ROOT / "tmp" / RUN / "B03" / name
    if p.exists():
        ev[name] = json.loads(p.read_text(encoding="utf-8"))
t2 = ev.get("probe-evidence2.json", {})
text_metrics = {
    "letterSpacing_6_delta_px": (t2.get("textab", {}).get("ls-6", [0, 0, 0])[2]
                                 - t2.get("textab", {}).get("ls-plain", [0, 0, 0])[2]),
    "wordSpacing_14_delta_px": (t2.get("textab", {}).get("ws-14", [0, 0, 0])[2]
                                - t2.get("textab", {}).get("ws-plain", [0, 0, 0])[2]),
    "tnum_delta_px": (t2.get("textab", {}).get("digits-tnum", [0, 0, 0])[2]
                      - t2.get("textab", {}).get("digits-plain", [0, 0, 0])[2]),
    "smcp_changed_px": ev.get("probe-evidence4.json", {}).get("smallcaps", {})
                       .get("changed_px"),
    "lineheight_1_0_pitch": ev.get("probe-evidence4.json", {}).get("lineheight", {})
                            .get("left_pitch"),
    "lineheight_2_4_pitch": ev.get("probe-evidence4.json", {}).get("lineheight", {})
                            .get("right_pitch"),
    "raw_gap_px": ev.get("probe-evidence4.json", {}).get("rawspan", {}),
}

# ---- 5. element budget: DSL bytes vs element count for the ten B03 works
budget = []
for cid in sorted((ROOT / "outputs" / RUN / "B03").glob("case-*")):
    snap = cid / "final.snapshot"
    if not snap.exists():
        continue
    txt = snap.read_text(encoding="utf-8")
    elements = len(re.findall(r"<[A-Za-z]", txt))
    png = cid / "final.png"
    budget.append({"case": cid.name, "elements": elements,
                   "dsl_kb": round(len(txt.encode("utf-8")) / 1024, 1),
                   "png_kb": round(png.stat().st_size / 1024, 1)})
cap_probe = next((r for r in RENDERS
                  if "more than 4096" in (r.get("error_summary") or "")), None)
largest_ok = max(budget, key=lambda b: b["elements"])

# ---- 6. gradient interpolation evidence (case-02 round trip)
grad = {"stop_hit": {"00:00": [11, 57, 84]}, "midtones_off": []}
g2 = t2.get("gradrot", {})

# ---- 7. fonts: the real GET /fonts body
fonts_raw = (SUITE / "docs" / "fonts.txt").read_text(encoding="utf-8")
# the endpoint returns a plain newline-separated list of family names, not JSON
font_list = [ln.strip() for ln in fonts_raw.splitlines() if ln.strip()]
font_families = sorted({re.sub(r" (Black|Extra Bold|Extra Light|Light|Medium|"
                               r"Semi Bold|Thin)$", "", n) for n in font_list})
fonts_meta = {"request_id": next((d["request_id"] for d in DOCS
                                  if d["url"].endswith("/fonts")), None),
              "bytes": next((d["response_bytes"] for d in DOCS
                             if d["url"].endswith("/fonts")), None),
              "accessed_at": next((d["ended_at"] for d in DOCS
                                   if d["url"].endswith("/fonts")), None),
              "raw_head": fonts_raw[:400]}

# ---- 8. cache behaviour
cache = Counter(r.get("x_snapshot_cache") for r in OK)
img_count = Counter(str(r.get("x_snapshot_image_count")) for r in OK)

EDGES = [0, 100, 200, 400, 600, 800, 1200, 1800, 2600, 3600, 6000]
HIST = [0] * (len(EDGES) - 1)
for v in srv:
    for i in range(len(EDGES) - 1):
        if EDGES[i] <= v < EDGES[i + 1]:
            HIST[i] += 1
            break
hit_rows = [r for r in OK if r.get("x_snapshot_cache") == "hit"]
hit_note = {
    "n": len(hit_rows),
    "with_render_timing": sum(1 for r in hit_rows
                              if "render;dur=" in (r.get("server_timing") or "")),
    "examples": [r["request_id"] for r in hit_rows[:4]],
}

DATA = {"scale": scale, "hist_edges": EDGES, "hist_counts": HIST,
        "hist_n": len(srv), "hit_note": hit_note, "server_ms": server_ms, "client_s": client_s,
        "outlier": outlier_info, "error_codes": dict(error_codes),
        "http_status": {str(k): v for k, v in http_status.items()},
        "failure_kinds": {k: v for (c, k), v in fails.items()},
        "failure_samples": {k: {"request_id": r["request_id"],
                                "status": r.get("http_status"),
                                "code": r.get("error_code"),
                                "summary": (r.get("error_summary") or "")[:160]}
                            for k, r in fail_samples.items()},
        "diagnosable_parse_errors": diagnosable,
        "text_metrics": text_metrics, "budget": budget,
        "element_cap_request": (cap_probe or {}).get("request_id"),
        "largest_work": largest_ok, "cache": dict(cache),
        "cache_hit_pct": pct(cache.get("hit", 0), len(OK)),
        "image_count_header": dict(img_count),
        "fonts": fonts_meta, "font_families": font_families,
        "docs": [{"request_id": d["request_id"], "url": d["url"],
                  "accessed_at": d["ended_at"], "bytes": d["response_bytes"],
                  "local": d["response_file"]} for d in DOCS],
        }
(TMP / "data.json").write_text(json.dumps(DATA, ensure_ascii=False, indent=2),
                               encoding="utf-8")
print(json.dumps({k: DATA[k] for k in
                  ("scale", "server_ms", "client_s", "error_codes", "failure_kinds",
                   "cache_hit_pct", "text_metrics", "largest_work")},
                 ensure_ascii=False, indent=1)[:2600])
print("font families:", len(font_families))
print("budget rows:", len(budget))
