# -*- coding: utf-8 -*-
"""查询可用字体，并从已缓存文档中提取参考链接。启动基准：总任务根。"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc
from pathlib import Path

cmd = sys.argv[1] if len(sys.argv) > 1 else "fonts"
if cmd == "fonts":
    sc.cmd_fonts("SHARED")
elif cmd == "links":
    raw = sc.suite_tmp() / "docs" / "parser-tags.raw"
    h = raw.read_text(encoding="utf-8")
    links = set(re.findall(r'href="(/(?:(?!http)[^"])+)"', h))
    for l in sorted(links):
        if any(k in l for k in ["text/", "text-", "reference", "painting", "parser-t"]):
            print(l)
