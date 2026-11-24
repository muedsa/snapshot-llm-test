from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_DIR = Path(__file__).resolve().parent / "sources"
RUN_DIR = Path(__file__).resolve().parents[1]
SUITE_ROOT = RUN_DIR.parents[1]

SOURCES = [
    {
        "source_id": "B04-S01",
        "title": "Heat Island Effect",
        "author_or_organization": "U.S. Environmental Protection Agency",
        "url": "https://www.epa.gov/heatislands",
    },
    {
        "source_id": "B04-S02",
        "title": "Benefits of Trees and Vegetation",
        "author_or_organization": "U.S. Environmental Protection Agency",
        "url": "https://www.epa.gov/heatislands/benefits-trees-and-vegetation",
    },
    {
        "source_id": "B04-S03",
        "title": "Using Green Roofs to Reduce Heat Islands",
        "author_or_organization": "U.S. Environmental Protection Agency",
        "url": "https://www.epa.gov/heatislands/using-green-roofs-reduce-heat-islands",
    },
    {
        "source_id": "B04-S04",
        "title": "Using Cool Roofs to Reduce Heat Islands",
        "author_or_organization": "U.S. Environmental Protection Agency",
        "url": "https://www.epa.gov/heatislands/using-cool-roofs-reduce-heat-islands",
    },
    {
        "source_id": "B04-S05",
        "title": "Using Cool Pavements to Reduce Heat Islands",
        "author_or_organization": "U.S. Environmental Protection Agency",
        "url": "https://www.epa.gov/heatislands/using-cool-pavements-reduce-heat-islands",
    },
    {
        "source_id": "B04-S06",
        "title": "Clinical Overview of Heat",
        "author_or_organization": "U.S. Centers for Disease Control and Prevention",
        "url": "https://www.cdc.gov/heat-health/hcp/clinical-overview/index.html",
    },
    {
        "source_id": "B04-S07",
        "title": "About Heat and Your Health",
        "author_or_organization": "U.S. Centers for Disease Control and Prevention",
        "url": "https://www.cdc.gov/heat-health/about/",
    },
    {
        "source_id": "B04-S08",
        "title": "Heat Cramps, Exhaustion, Stroke",
        "author_or_organization": "National Weather Service",
        "url": "https://www.weather.gov/safety/heat-illness",
    },
    {
        "source_id": "B04-S09",
        "title": "Heat Index",
        "author_or_organization": "National Weather Service",
        "url": "https://www.weather.gov/safety/heat-index",
    },
    {
        "source_id": "B04-S10",
        "title": "Urban heat island",
        "author_or_organization": "World Meteorological Organization",
        "url": "https://wmo.int/urban-heat-island",
    },
]

BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt",
    "figcaption", "figure", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header",
    "hr", "li", "main", "nav", "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul",
}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
        if not self.skip_depth and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        if not self.skip_depth and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts).replace("\r", "")
        lines = [" ".join(line.split()) for line in raw.split("\n")]
        nonempty = [line for line in lines if line]
        return "\n".join(nonempty) + "\n"


def rel(path: Path) -> str:
    return path.relative_to(SUITE_ROOT).as_posix()


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for source in SOURCES:
        sid = source["source_id"]
        slug = sid.lower().replace("-", "_")
        raw_path = SOURCE_DIR / f"{slug}.response.html"
        text_path = SOURCE_DIR / f"{slug}.txt"
        meta_path = SOURCE_DIR / f"{slug}.json"
        request = Request(source["url"], headers={"User-Agent": "B04-preparation/1.0 (+credible-source-cache)"})
        started = datetime.now(timezone.utc)
        record = dict(source)
        record["path_base"] = "suite_root"
        record["started_at"] = started.isoformat()
        try:
            with urlopen(request, timeout=45) as response:
                body = response.read()
                ended = datetime.now(timezone.utc)
                record.update({
                    "accessed_at": ended.isoformat(),
                    "http_status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "final_url": response.geturl(),
                    "response_headers": dict(response.headers.items()),
                    "response_bytes": len(body),
                    "response_sha256": hashlib.sha256(body).hexdigest(),
                    "elapsed_seconds": (ended - started).total_seconds(),
                    "raw_response": rel(raw_path),
                    "readable_text": rel(text_path),
                    "status": "fetched",
                })
                raw_path.write_bytes(body)
                if record["content_type"] and "html" in record["content_type"].lower():
                    text = TextExtractor()
                    text.feed(body.decode("utf-8", errors="replace"))
                    readable = text.text()
                    extraction = "stdlib_html_parser"
                else:
                    readable = body.decode("utf-8", errors="replace")
                    extraction = "utf8_decode"
                text_path.write_text(readable, encoding="utf-8")
                record["text_extraction"] = extraction
                record["text_sha256"] = hashlib.sha256(readable.encode("utf-8")).hexdigest()
        except Exception as exc:
            ended = datetime.now(timezone.utc)
            record.update({
                "accessed_at": ended.isoformat(),
                "http_status": None,
                "content_type": None,
                "elapsed_seconds": (ended - started).total_seconds(),
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            })
            text_path.write_text(f"FETCH FAILED\n{record['error']}\n", encoding="utf-8")
        meta_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.append(record)
        print(f"{sid}: {record['status']} {record.get('http_status')} {source['url']}")
    (SOURCE_DIR / "fetch-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
