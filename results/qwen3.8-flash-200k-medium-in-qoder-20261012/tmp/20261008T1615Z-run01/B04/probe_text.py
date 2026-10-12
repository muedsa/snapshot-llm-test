"""把本轮新增的 science.nasa.gov 页面转成纯文本存到 probe/，方便逐段核对原文。

只读已抓取的真实响应文件（sources/*.html），不访问网络；probe/*.txt 是研究过程
留痕，不进入任何成品图。
"""
import io
import os
import re
from pathlib import Path

TMP = Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B04"
SRC = TMP / "sources"
PROBE = TMP / "probe"
ENTITIES = [(b"&#8217;", b"'"), (b"&#8216;", b"'"), (b"&#8211;", b"-"), (b"&#8212;", b"--"),
            (b"&#8220;", b'"'), (b"&#8221;", b'"'), (b"&#8230;", b"..."),
            (b"&#176;", b"deg"), (b"&#180;", b"m"), (b"&amp;", b"&"), (b"&nbsp;", b" "),
            (b"&#8217;", b"'")]
FILES = ["nasa-science-safety", "nasa-science-glossary", "nasa-science-geometry",
         "nasa-science-2024", "nasa-science-eclipses", "nasa-science-eclipse-types",
         "nasa-oh-2024", "nasa-oh-2027", "nasa-plotkey"]

for key in FILES:
    raw = SRC.joinpath(key + ".html").read_bytes()
    for a, b in ENTITIES:
        raw = raw.replace(a, b)
    raw = re.sub(rb"<script.*?</script>", b"", raw, flags=re.S)
    raw = re.sub(rb"<style.*?</style>", b"", raw, flags=re.S)
    txt = re.sub(rb"<[^>]+>", b"\n", raw).decode("utf-8", "replace")
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    out = PROBE / (key + ".txt")
    out.write_text("\n".join(lines), encoding="utf-8")
    print("%-28s %6d lines -> %s" % (key, len(lines), os.path.relpath(out, TMP)))
