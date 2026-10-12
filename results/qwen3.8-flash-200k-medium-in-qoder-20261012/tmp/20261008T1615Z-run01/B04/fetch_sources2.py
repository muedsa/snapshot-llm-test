"""B04 research round 2: corrected NASA URLs (round 1's 404s are kept in the log),
plus parsing of the 21st-century catalogue table into machine-readable data.

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import json, os, re, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B04"
SRC = TMP / "sources"
LOG = TMP / "requests.jsonl"

TARGETS = [
    ("nasa-saros-page", "https://eclipse.gsfc.nasa.gov/SEsaros/SEsaros.html",
     "NASA: Solar Eclipse Periodicity and the Saros - definition of the Saros interval"),
    ("nasa-saros-139", "https://eclipse.gsfc.nasa.gov/SEsaros/SEsaros139.html",
     "Catalog of Solar Eclipses of Saros 139 (member list incl. 2024-04-08, 2044-04-25...)"),
    ("nasa-saros-136", "https://eclipse.gsfc.nasa.gov/SEsaros/SEsaros136.html",
     "Catalog of Solar Eclipses of Saros 136 (includes 2027-08-02, longest totality of century)"),
    ("nasa-path-2024", "https://eclipse.gsfc.nasa.gov/SEpath/SEpath2001/SE2024Apr08Tpath.html",
     "Path of Totality: Total Solar Eclipse of 2024 Apr 08 (contact times, duration, width)"),
    ("nasa-path-2027", "https://eclipse.gsfc.nasa.gov/SEpath/SEpath2001/SE2027Aug02Tpath.html",
     "Path of Totality: Total Solar Eclipse of 2027 Aug 02 (longest totality 21st century)"),
    ("nasa-deltat", "https://eclipse.gsfc.nasa.gov/SEcat5/deltat.html",
     "NASA: Delta T - historical value of the Earth's rotational deceleration"),
    ("nasa-atlas", "https://eclipse.gsfc.nasa.gov/SEatlas/SEatlas.html",
     "Atlas of Solar Eclipses - how the path maps are produced"),
    ("nasa-basics", "https://eclipse.gsfc.nasa.gov/Eclipse/basics.html",
     "NASA: Eclipses Basics - umbra/penumbra geometry and eclipse type definitions"),
    ("nasa-secentral", "https://eclipse.gsfc.nasa.gov/Eclipse/central.html",
     "NASA: Central, Non-central and Partial Solar Eclipses definitions"),
    ("nasa-magnitude", "https://eclipse.gsfc.nasa.gov/Eclipse/magnitude.html",
     "NASA: Magnitude of a Solar Eclipse definition"),
]


def log(rec):
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def fetch(key, url, note):
    out = SRC / (key + ".html")
    hdr = SRC / (key + ".headers.txt")
    started = datetime.now(timezone.utc)
    t0 = time.monotonic()
    cmd = ["curl", "-sS", "-L", "--fail-with-body", "-D", str(hdr), "-o", str(out),
           "-w", "%{http_code}\t%{content_type}\t%{size_download}",
           "--connect-timeout", "25", "--max-time", "180",
           "-A", "Mozilla/5.0 (X11; Linux x86_64) research-fetch", url]
    p = subprocess.run(cmd, capture_output=True, text=True)
    ended = datetime.now(timezone.utc)
    parts = (p.stdout or "").strip().split("\t")
    status = int(parts[0]) if parts and parts[0].isdigit() else 0
    rel = lambda q: str(q.relative_to(ROOT)).replace(os.sep, "/")
    rec = {"request_id": "B04-doc-%s-%s" % (key, started.strftime("%Y%m%dT%H%M%SZ")),
           "task_id": "B04", "case_id": None, "kind": "document",
           "started_at": started.isoformat(), "ended_at": ended.isoformat(),
           "duration_seconds": round(time.monotonic() - t0, 3),
           "endpoint": "/".join(url.split("/")[3:]), "url": url, "method": "GET",
           "http_status": status, "content_type": parts[1] if len(parts) > 1 else None,
           "response_bytes": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None,
           "request_file": rel(out), "response_file": rel(hdr), "raw_html": rel(out),
           "error_summary": None if status == 200 else (p.stderr or "")[:400],
           "note": note, "path_base": "suite_root"}
    log(rec)
    print("%-20s %s %8s" % (key, status, rec["response_bytes"]))
    return rec


if __name__ == "__main__":
    res = [fetch(k, u, n) for k, u, n in TARGETS]
    print("fetched %d/%d" % (sum(1 for r in res if r["http_status"] == 200), len(res)))
