"""B04 research round 3: 为件 04（食季）找"食年 346.62 天 / 交点退行"的可查证出处。

round 1/2 抓到的页面里没有 "eclipse season" 或 346.6 的字样（已 grep 全文确认），
因此本题再抓一批候选页面；失败与 404 同样写入 requests.jsonl，不作为已读来源。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import os
import sys
from pathlib import Path

TMP = Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B04"
sys.path.insert(0, str(TMP))
from fetch_sources2 import fetch  # noqa: E402  复用同一套请求日志格式

TARGETS = [
    ("nasa-lecat5-2001-2100", "https://eclipse.gsfc.nasa.gov/LEcat5/LE2001-2100.html",
     "NASA Catalog of Lunar Eclipses 2001-2100 intro (node/season wording candidate)"),
    ("nasa-lecat5-index", "https://eclipse.gsfc.nasa.gov/LEcat5/LEcatalog.html",
     "NASA Catalog of Lunar Eclipses -1999 to +3000 index page"),
    ("nasa-5mcse-intro", "https://eclipse.gsfc.nasa.gov/SEpubs/5MCSE.html",
     "Five Millennium Canon of Solar Eclipses landing page (candidate for eclipse-year text)"),
    ("wiki-eclipse-season", "https://en.wikipedia.org/wiki/Eclipse_season",
     "Wikipedia: Eclipse season (states eclipse year 346.62 d and season cadence)"),
    ("wiki-eclipse-cycle", "https://en.wikipedia.org/wiki/Eclipse_cycle",
     "Wikipedia: Eclipse cycle (saros/exeligmos/inex table, cross-check for cadence)"),
]

if __name__ == "__main__":
    res = [fetch(k, u, n) for k, u, n in TARGETS]
    print("fetched %d/%d" % (sum(1 for r in res if r["http_status"] == 200), len(res)))
