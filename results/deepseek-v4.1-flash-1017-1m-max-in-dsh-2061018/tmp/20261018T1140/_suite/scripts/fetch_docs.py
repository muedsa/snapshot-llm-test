"""Fetch Snapshot documentation pages into a local text corpus (concurrent, resumable).

Run from the suite root:
    python tmp/<run_id>/_suite/scripts/fetch_docs.py
Paths are resolved from SNAPSHOT_TASK_ROOT (default: current directory) and
SNAPSHOT_RUN_ID; nothing machine-specific is stored in the script.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://snapshot.muedsa.com"
SITEMAP = BASE + "/sitemap-0.xml"
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]


class TextExtractor(HTMLParser):
    SKIP = {"script", "style", "svg", "nav", "header", "footer", "aside", "template"}
    BLOCK = {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
             "pre", "blockquote", "table", "ul", "ol", "br", "dt", "dd"}
    HEAD = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### ", "h5": "##### ", "h6": "###### "}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0
        self.in_pre = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
            return
        if tag in ("pre", "code"):
            self.in_pre += 1
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag in self.HEAD:
            self.parts.append("\n" + self.HEAD[tag])

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in ("pre", "code") and self.in_pre:
            self.in_pre -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.in_pre:
            self.parts.append(data)
        else:
            self.parts.append(re.sub(r"\s+", " ", data))

    def text(self):
        raw = "".join(self.parts)
        lines = [ln.rstrip() for ln in raw.splitlines()]
        out = []
        blank = 0
        for ln in lines:
            ln = ln.strip()
            if not ln:
                blank += 1
                if blank > 1:
                    continue
            else:
                blank = 0
            out.append(ln)
        return "\n".join(out).strip()


def fetch(url: str, timeout=25, retries=2) -> tuple[bytes | None, dict, str | None]:
    last_err = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            req = Request(url, headers={"User-Agent": "snapshot-task-suite/docs-fetch"})
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                headers = {k.lower(): v for k, v in resp.headers.items()}
            return body, headers, None
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}: {exc}"
            time.sleep(1.5 * (attempt + 1))
    return None, {}, last_err


def main() -> int:
    root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
    run_id = os.environ.get("SNAPSHOT_RUN_ID")
    if not run_id:
        raise SystemExit("SNAPSHOT_RUN_ID is required")
    suite_tmp = root / "tmp" / run_id / "_suite"
    docs_dir = suite_tmp / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    log_path = suite_tmp / "requests.jsonl"

    sm_body, _, err = fetch(SITEMAP)
    if sm_body is None:
        raise SystemExit(f"cannot fetch sitemap: {err}")
    urls = re.findall(r"<loc>(.*?)</loc>", sm_body.decode("utf-8", "replace"))
    urls = [u for u in urls if "/playground/" not in u]
    if ONLY:
        urls = [u for u in urls if any(k in u for k in ONLY)]

    def work(url: str):
        rel = url.replace(BASE, "").strip("/") or "index"
        slug = rel.replace("/", "__") + ".md"
        target = docs_dir / slug
        if target.exists() and target.stat().st_size > 500:
            return {"url": url, "skipped": True}
        rid = f"shared-doc-{uuid.uuid4().hex[:10]}"
        t0 = time.time()
        body, headers, err = fetch(url)
        rec = {"id": rid, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "kind": "document",
               "url": url, "path_base": "suite_root"}
        if body is not None:
            parser = TextExtractor()
            parser.feed(body.decode("utf-8", "replace"))
            text = parser.text()
            target.write_text(f"<!-- source: {url} -->\n\n" + text + "\n", encoding="utf-8")
            rec.update({"http_status": 200, "content_type": headers.get("content-type"),
                        "duration_ms": round((time.time() - t0) * 1000), "bytes": len(body),
                        "saved": f"tmp/{run_id}/_suite/docs/{slug}"})
        else:
            rec.update({"http_status": None, "error": err,
                        "duration_ms": round((time.time() - t0) * 1000)})
        return rec

    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(work, u): u for u in urls}
        for fut in as_completed(futures):
            results.append(fut.result())
    ok = sum(1 for r in results if r.get("http_status") == 200)
    skip = sum(1 for r in results if r.get("skipped"))
    with log_path.open("a", encoding="utf-8") as fh:
        for rec in results:
            if not rec.get("skipped"):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (suite_tmp / "docs-manifest.json").write_text(
        json.dumps({"finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "page_count": len(results), "fetched": ok, "skipped": skip,
                    "pages": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"pages={len(results)} fetched={ok} skipped={skip}")
    fails = [r["url"] for r in results if r not in [] and r.get("http_status") is None]
    for u in fails:
        print("FAIL", u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
