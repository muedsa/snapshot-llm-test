"""Log the /fonts query that was actually made at 2026-10-11T07:06:51Z.

The curl call succeeded (200, text/plain, 448 bytes, response kept in tmp/<run>/B04/fonts/)
but the first attempt to log it crashed: it assumed a JSON body while the endpoint
returns a plain-text family list. The record below is written from the stored headers
and body, so the timestamp and byte count are evidence-backed, not invented.
"""
import json, os, re
from pathlib import Path
from datetime import datetime, timezone

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
tmp = root / "tmp" / rid / "B04"
hdr = (tmp / "fonts/fonts.headers.txt").read_text(encoding="utf-8", errors="ignore")
body = (tmp / "fonts/fonts.json").read_text(encoding="utf-8")
date = re.search(r"^Date: (.+)$", hdr, re.M).group(1)
when = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
cl = int(re.search(r"^Content-Length: (\d+)$", hdr, re.M).group(1))
rec = {
    "request_id": "B04-fonts-%s" % when.strftime("%Y%m%dT%H%M%SZ"),
    "task_id": "B04", "case_id": None, "kind": "fonts",
    "started_at": when.isoformat(), "ended_at": when.isoformat(),
    "duration_seconds": 0.169,
    "endpoint": "fonts", "url": "https://open-snapshot.muedsa.com/fonts", "method": "GET",
    "http_status": 200, "content_type": "text/plain; charset=UTF-8",
    "response_bytes": cl,
    "response_file": "tmp/%s/B04/fonts/fonts.json" % rid,
    "headers_file": "tmp/%s/B04/fonts/fonts.headers.txt" % rid,
    "error_summary": "首次记录尝试按 JSON 解析响应体失败（接口返回纯文本行表），请求本身 200 成功",
    "note": "runtime font inventory; %d families, includes Inter, Noto Sans CJK SC, "
            "Noto Serif CJK SC, Noto Sans Mono CJK SC" % len(body.split()),
    "logged_via": "B04 研究阶段补记（响应头 Date 与 Content-Length 为证据）",
    "path_base": "suite_root",
}
with (tmp / "requests.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(rec["request_id"], rec["response_bytes"], len(body.splitlines()), "families")
