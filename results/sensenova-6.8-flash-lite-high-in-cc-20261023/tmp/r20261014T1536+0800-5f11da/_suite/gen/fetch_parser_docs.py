"""A17 新增文档取得：/guides/parser/ 与 /guides/parser-text/ 未缓存页面。

用途：A17 第 3 页需要说明 Raw / CDATA / 富文本 / 8 位尾部 alpha 的真实规则，
现有缓存（reference-parser-tags、parser-text、guides-media-text）没有 CDATA 相关表述，
因此补取解析器指南页面并留痕（原始 HTML + 响应头 + requests.jsonl 一行）。

路径全部相对总任务根（path_base=suite_root），不写死机器盘符。
"""
from __future__ import annotations

import datetime
import html
import json
import pathlib
import re
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
SUITE_TMP = SUITE_ROOT / "tmp" / RUN_ID / "_suite"
DOCS = SUITE_TMP / "docs" / "dsl"
BASE = "https://snapshot.muedsa.com"
TZ = datetime.timezone(datetime.timedelta(hours=8))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

TARGETS = [
    ("/guides/parser/", "guides-parser.html", "A17 第3页：解析器总则与 CDATA/文本节点规则"),
    ("/guides/testing/", "guides-testing.html", "A17 第4页：视觉自检与可复现交付"),
]


def fetch(path: str) -> dict:
    """返回 status/headers/body/started_at/ended_at/elapsed_ms，全部真实测量。"""
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
    started_iso = datetime.datetime.now(TZ).replace(microsecond=0).isoformat()
    started = time.monotonic()
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = resp.read()
        headers = {k: v for k, v in resp.getheaders()}
        status = resp.status
    elapsed_ms = round((time.monotonic() - started) * 1000, 3)
    ended_iso = datetime.datetime.now(TZ).replace(microsecond=0).isoformat()
    return {"status": status, "headers": headers, "body": body,
            "started_at": started_iso, "ended_at": ended_iso,
            "elapsed_ms": elapsed_ms}


def to_md(raw: bytes) -> str:
    text = html.unescape(raw.decode("utf-8", errors="replace"))
    # 去掉脚本/样式后按块级标签切分，得到可读纯文本
    text = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"</(p|div|h[1-6]|li|tr|pre|section|blockquote)>", "\n", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def main() -> int:
    now = datetime.datetime.now(TZ).replace(microsecond=0).isoformat()
    rows = []
    for path, fname, purpose in TARGETS:
        r = fetch(path)
        status, headers, body = r["status"], r["headers"], r["body"]
        rel_html = f"tmp/{RUN_ID}/_suite/docs/dsl/{fname}"
        rel_h = f"{rel_html}.headers.txt"
        rel_md = f"{rel_html}.md.txt"
        (DOCS / fname).write_bytes(body)
        (DOCS / (fname + ".headers.txt")).write_text(
            "\n".join(f"{k}: {v}" for k, v in sorted(headers.items())) + "\n",
            encoding="utf-8")
        (DOCS / (fname + ".md.txt")).write_text(to_md(body), encoding="utf-8")
        rows.append({
            "ts": r["ended_at"],
            "timezone": "Asia/Shanghai (UTC+08:00)",
            "request_id": f"req-a17-docs-{path.strip('/').split('/')[-1] or 'root'}-{abs(hash(path)) % 10000:04d}",
            "owner": "shared",
            "task_id": "A17",
            "kind": "docs",
            "method": "GET",
            "url": BASE + path,
            "purpose": purpose,
            "status": status,
            "content_type": headers.get("Content-Type"),
            "bytes": len(body),
            "started_at": r["started_at"],
            "ended_at": r["ended_at"],
            "elapsed_ms": r["elapsed_ms"],
            "elapsed_ms_source": "本地墙钟 time.monotonic，含网络往返",
            "saved": [rel_html, rel_h, rel_md],
        })
    with (SUITE_TMP / "requests.jsonl").open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps([{"url": r["url"], "status": r["status"], "bytes": r["bytes"]}
                      for r in rows], ensure_ascii=False, indent=1))
    print("now:", now)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
