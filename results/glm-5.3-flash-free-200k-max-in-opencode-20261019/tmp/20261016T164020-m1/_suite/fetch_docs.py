# -*- coding: utf-8 -*-
"""批量下载 Snapshot DSL 文档：保存原始响应到 docs 缓存并逐条记录请求。
启动基准：总任务根（SNAPSHOT_TASK_ROOT 默认 '.')。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

PAGES = [
    "https://snapshot.muedsa.com/llms.txt",
    "https://snapshot.muedsa.com/sitemap.xml",
    "https://snapshot.muedsa.com/guides/overview/",
    "https://snapshot.muedsa.com/guides/quickstart/",
    "https://snapshot.muedsa.com/guides/parser/",
    "https://snapshot.muedsa.com/guides/layout/",
    "https://snapshot.muedsa.com/guides/widgets/",
    "https://snapshot.muedsa.com/guides/painting/",
    "https://snapshot.muedsa.com/guides/media-text/",
    "https://snapshot.muedsa.com/guides/concepts/",
    "https://snapshot.muedsa.com/guides/rendering/",
    "https://snapshot.muedsa.com/guides/examples/",
    "https://snapshot.muedsa.com/reference/parser-tags/",
]

for url in PAGES:
    name = url.rstrip("/").rsplit("/", 1)[-1] or "index"
    if name == "snapshot.muedsa.com":
        name = "root"
    out = sc.suite_tmp() / "docs" / f"{name}.raw"
    st, ct, data, rec = sc.fetch_url("SHARED", "document", url, out, timeout=60)
    print(f"{st} {len(data or b''):>8} {ct} {name}")
