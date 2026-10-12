"""B04 research round 5: 换 URL 族再取件 09 需要的接触时刻与安全表述。

round 4 的三条 NASA 猜测 URL 全 404，三条 Wikipedia 请求全部连不上（443 超时，
en.wikipedia.org 在本环境不可达，见 requests.jsonl）。因此件 09 只用 NASA
eclipse 站点的真实页面：solar.html 的链接清单里指出逐年"Occurrence Highlights"
页族 OH/OH<year>.html 与"Key to Solar Eclipse Path Tables"(SEplot/SEplotkey.html)，
两者都比 404 的 SEmono 页族更可能给出五个接触时刻。
science.nasa.gov 作为安全表述的候选一并试取；取不到就退回到路径表实测口径。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import os
import sys
from pathlib import Path

TMP = Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B04"
sys.path.insert(0, str(TMP))
from fetch_sources2 import fetch  # noqa: E402

TARGETS = [
    ("nasa-oh-2024", "https://eclipse.gsfc.nasa.gov/OH/OH2024.html",
     "NASA Occurrence Highlights 2024 (candidate for C1..C5 contact times of 2024-04-08)"),
    ("nasa-oh-2027", "https://eclipse.gsfc.nasa.gov/OH/OH2027.html",
     "NASA Occurrence Highlights 2027 (candidate for contact times of 2027-08-02)"),
    ("nasa-plotkey", "https://eclipse.gsfc.nasa.gov/SEplot/SEplotkey.html",
     "NASA Key to Solar Eclipse Path Tables (column meanings of the 2024/2027 path tables)"),
    ("nasa-science-eclipses", "https://science.nasa.gov/eclipses/",
     "NASA Science eclipses hub (candidate for eye-safety guidance)"),
    ("nasa-science-eclipse-types", "https://science.nasa.gov/eclipses/types/",
     "NASA Science eclipse types (candidate for Baily beads / diamond ring wording)"),
]

if __name__ == "__main__":
    res = [fetch(k, u, n) for k, u, n in TARGETS]
    print("fetched %d/%d" % (sum(1 for r in res if r["http_status"] == 200), len(res)))
