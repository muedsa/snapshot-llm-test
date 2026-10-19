# -*- coding: utf-8 -*-
"""第二批文档：文本属性详解、枚举、渐变、阴影、边框、FAQ等。启动基准：总任务根。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

PAGES = [
    "https://snapshot.muedsa.com/reference/parser-text/",
    "https://snapshot.muedsa.com/reference/enums/",
    "https://snapshot.muedsa.com/reference/gradients/",
    "https://snapshot.muedsa.com/reference/box-shadow/",
    "https://snapshot.muedsa.com/reference/borders/",
    "https://snapshot.muedsa.com/reference/box-decoration/",
    "https://snapshot.muedsa.com/reference/text-layout/",
    "https://snapshot.muedsa.com/reference/text-style/",
    "https://snapshot.muedsa.com/reference/parser-errors/",
    "https://snapshot.muedsa.com/reference/faq/",
    "https://snapshot.muedsa.com/guides/visual-reference/",
]
for url in PAGES:
    name = url.rstrip("/").rsplit("/", 1)[-1]
    out = sc.suite_tmp() / "docs" / f"{name}.raw"
    st, ct, data, rec = sc.fetch_url("SHARED", "document", url, out, timeout=60)
    print(f"{st} {len(data or b''):>8} {name}")
