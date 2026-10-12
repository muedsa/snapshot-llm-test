"""B04 research round 4: 为件 09（什么时候可以裸眼看）补齐两类可查证材料。

需要 a) 一次真实日全食的五个接触时刻（半影 C1/C5、本影 C2/C4 与大食时刻），
b) 裸眼安全的权威表述与贝利珠/钻石环的定义。round 1-3 抓下的页面里没有这两类内容
（已对全部已存 HTML grep 过 contact / Baily / safety 并确认缺失，失败记录仍在
requests.jsonl 里），所以本题再抓一批候选页面。404 与超时同样如实入日志，
不计入已读来源。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import os
import sys
from pathlib import Path

TMP = Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B04"
sys.path.insert(0, str(TMP))
from fetch_sources2 import fetch  # noqa: E402  复用同一套请求日志格式

TARGETS = [
    ("nasa-mono-2024", "https://eclipse.gsfc.nasa.gov/SEmono/TSE2024/TSE2024.html",
     "NASA monograph: Total Solar Eclipse of 2024 Apr 08 (candidate for the 5 contact times)"),
    ("nasa-safe", "https://eclipse.gsfc.nasa.gov/safe.html",
     "NASA Eclipse Safety page (naked-eye rules during partial vs totality)"),
    ("nasa-solar-year", "https://eclipse.gsfc.nasa.gov/solar.html",
     "NASA Solar Eclipses landing page (per-year table with greatest eclipse times)"),
    ("nasa-glossary", "https://eclipse.gsfc.nasa.gov/glossary/glossary.html",
     "NASA Eclipse glossary (candidate for Baily's beads / diamond ring definitions)"),
    ("wiki-baily", "https://en.wikipedia.org/wiki/Baily%27s_beads",
     "Wikipedia: Baily's beads (mechanism, timing relative to C2/C3)"),
    ("wiki-eclipse-safety", "https://en.wikipedia.org/wiki/Solar_eclipse_safety",
     "Wikipedia: Solar eclipse safety (candidate page for eye-protection guidance)"),
]

if __name__ == "__main__":
    res = [fetch(k, u, n) for k, u, n in TARGETS]
    for r in res:
        print(r["request_id"], r["http_status"], r.get("response_bytes"), r["url"])
