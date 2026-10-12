"""B04 research source retrieval: real HTTP fetch of the NASA eclipse catalogue pages,
raw bytes + headers kept, each request logged to tmp/<run>/B04/requests.jsonl.

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B04"
SRC = TMP / "sources"
SRC.mkdir(parents=True, exist_ok=True)
LOG = TMP / "requests.jsonl"

TARGETS = [
    ("nasa-5mc-catalog", "https://eclipse.gsfc.nasa.gov/SEcat5/SEcatalog.html",
     "Five Millennium Canon of Solar Eclipses - summary table by century"),
    ("nasa-21cen-catalog", "https://eclipse.gsfc.nasa.gov/SEcat5/SE2001-2100.html",
     "Solar Eclipses in the 21st Century (2001-2100): every eclipse, type, Saros, "
     "greatest-eclipse time, duration, path width, magnitude"),
    ("nasa-prediction", "https://eclipse.gsfc.nasa.gov/SEprediction/prediction.html",
     "rules used to calculate eclipse circumstances (delta T, magnitudes, durations)"),
    ("nasa-solar-basics", "https://eclipse.gsfc.nasa.gov/solar.html",
     "NASA Solar Eclipse Page - basics of umbra/penumbra and eclipse types"),
    ("nasa-2024-apr08-tOTAL", "https://eclipse.gsfc.nasa.gov/SEgoogle/SEgoogle2021/SE2024Apr08Tgoogle.html",
     "Path of the Total Solar Eclipse of 2024 Apr 08 (Google Earth / KML page)"),
    ("nasa-saros", "https://eclipse.gsfc.nasa.gov/Eclipse/sarosFAQ.html",
     "FAQ about the Saros cycle"),
    ("nasa-sun-fact", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html",
     "NASA Sun fact sheet - radius and other constants"),
    ("nasa-moon-fact", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html",
     "NASA Moon fact sheet - radius, mean distance, orbital constants"),
    ("nasa-earth-fact", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html",
     "NASA Earth fact sheet - radius, rotation period"),
    ("nasa-sepath", "https://eclipse.gsfc.nasa.gov/SEpath/SEpath2021/SE2027Aug02path.html",
     "Path of the Total Solar Eclipse of 2027 Aug 02 (longest totality of the century)"),
]


def log(rec):
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def fetch(idx, key, url, note):
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
    rec = {
        "request_id": "B04-doc-%s-%s" % (key, started.strftime("%Y%m%dT%H%M%SZ")),
        "task_id": "B04", "case_id": None, "kind": "document",
        "started_at": started.isoformat(), "ended_at": ended.isoformat(),
        "duration_seconds": round(time.monotonic() - t0, 3),
        "endpoint": "/".join(url.split("/")[3:]),
        "url": url, "method": "GET",
        "http_status": status,
        "content_type": parts[1] if len(parts) > 1 else None,
        "response_bytes": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None,
        "request_file": str(out.relative_to(ROOT)).replace(os.sep, "/"),
        "response_file": str(hdr.relative_to(ROOT)).replace(os.sep, "/"),
        "raw_html": str(out.relative_to(ROOT)).replace(os.sep, "/"),
        "error_summary": None if status == 200 else (p.stderr or "")[:400],
        "note": note, "path_base": "suite_root",
    }
    log(rec)
    print("%-24s %s %8s  %s" % (key, status, rec["response_bytes"], rec["duration_seconds"]))
    return rec


if __name__ == "__main__":
    res = [fetch(i, k, u, n) for i, (k, u, n) in enumerate(TARGETS)]
    ok = [r for r in res if r["http_status"] == 200]
    print("fetched %d/%d" % (len(ok), len(res)))
    sys.exit(0 if len(ok) >= 6 else 1)
