# -*- coding: utf-8 -*-
"""Persist the muedsa/snapshot source files read while diagnosing the
BackdropFilter leak (A17), as reproducible evidence.

Saves each file under tmp/<run_id>/_suite/docs/muedsa-snapshot-src/ with the
commit SHA it was read from, and appends document entries to the A17
requests.jsonl.  All timestamps are the real fetch times.
"""
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request

REPO = "muedsa/snapshot"
FILES = [
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/BackdropFilterLayer.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/LayerPaintContext.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/PictureLayer.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/OpacityLayer.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/PaintingContext.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/box/RenderBackdropFilter.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/box/RenderOpacity.kt",
    "core/src/main/kotlin/com/muedsa/snapshot/rendering/box/RenderTransform.kt",
    "parser/src/main/kotlin/com/muedsa/snapshot/parser/widget/ContainerParser.kt",
    "parser/src/main/kotlin/com/muedsa/snapshot/parser/widget/BorderParser.kt",
    "parser/src/main/kotlin/com/muedsa/snapshot/parser/widget/OpacityParser.kt",
]
ROOT = pathlib.Path(".")
DOCS = ROOT / "tmp/run-20261011-01/_suite/docs/muedsa-snapshot-src"
LOG = ROOT / "tmp/run-20261011-01/A17/requests.jsonl"


def now():
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(
        timespec="milliseconds")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "a17-source-cache"})
    t0 = now()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            status, ctype = r.status, r.headers.get("Content-Type")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        status, ctype = exc.code, exc.headers.get("Content-Type")
    return status, ctype, body, t0, now()


def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    status, ctype, body, t0, t1 = get(
        f"https://api.github.com/repos/{REPO}/commits?per_page=1")
    sha = json.loads(body)[0]["sha"]
    print("HEAD sha:", sha)
    index = {"repo": f"https://github.com/{REPO}", "commit": sha,
             "fetched_at": t1, "files": []}
    entries = [{
        "id": "A17-src-0000", "type": "document", "method": "GET",
        "url": f"https://api.github.com/repos/{REPO}/commits?per_page=1",
        "ts_start": t0, "ts_end": t1, "status": status,
        "content_type": ctype, "saved_to": None,
        "use": "resolve commit SHA for reproducible source citation",
        "commit": sha,
    }]
    n = 0
    seen = set()
    for path in FILES:
        if path in seen:
            continue
        seen.add(path)
        n += 1
        url = f"https://raw.githubusercontent.com/{REPO}/{sha}/{path}"
        status, ctype, body, t0, t1 = get(url)
        if status != 200:
            print("FAIL", status, path)
            continue
        name = path.replace("/", "__")
        out = DOCS / name
        out.write_bytes(body)
        rel = out.as_posix()
        index["files"].append({
            "path_in_repo": path, "url": url, "saved_to": rel,
            "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
            "fetched_at": t1,
        })
        entries.append({
            "id": f"A17-src-{n:04d}", "type": "document", "method": "GET",
            "url": url, "ts_start": t0, "ts_end": t1, "status": status,
            "content_type": ctype, "saved_to": rel, "bytes": len(body),
            "use": "A17 BackdropFilter leak root cause: layer/picture/filter "
                   "implementation and container/border/opacity parsing rules",
        })
        print("saved", name, len(body))
    (DOCS / "sources-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("logged", len(entries), "entries; index ->",
          (DOCS / "sources-index.json").as_posix())


if __name__ == "__main__":
    main()
