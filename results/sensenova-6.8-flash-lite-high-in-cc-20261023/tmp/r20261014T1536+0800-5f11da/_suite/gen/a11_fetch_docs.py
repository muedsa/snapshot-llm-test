"""A11 新增文档查证：抓取 Parser 文本属性详解与文本布局参考。

A11 需要 textAlign / textWidthBasis / textHeight / fontFeatures(tnum) / Raw 嵌套等
文本细节，共享缓存里只有总表。这里实际请求并缓存，请求与响应头全部留痕。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a11_fetch_docs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RID = S.run_id()
DOC_ROOT = S.service_url().replace("open-snapshot", "snapshot") + "/reference/"
_, tmp = S.suite_dirs()
DEST = tmp / "docs" / "dsl"

PAGES = ["parser-text/", "text-layout/", "text-style/", "enums/"]

for page in PAGES:
    url = DOC_ROOT + page
    name = page.strip("/").replace("/", "-") + ".html"
    dest = DEST / name
    if dest.exists():
        print("cached", S.rel(dest))
        continue
    rec = S.fetch(url, "A11", dest, timeout=90)
    print("fetched %s -> HTTP %s (%d B)" % (url, rec["http_status"], rec["response_bytes"]))

# 从缓存的 parser-tags 索引确认没有遗漏的文本相关页面
idx = (DEST / "reference-parser-tags.html").read_text(encoding="utf-8", errors="replace")
links = sorted(set(re.findall(r'href="(/reference/[^"#]+)"', idx)))
print("text-related reference pages linked from parser-tags:")
for l in links:
    if any(k in l for k in ("text", "parser-text", "enums")):
        print("  ", l)
