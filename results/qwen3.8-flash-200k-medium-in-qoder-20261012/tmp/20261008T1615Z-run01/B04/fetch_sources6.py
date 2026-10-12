"""B04 research round 6: science.nasa.gov 的 eclipses 子站（件 09 的一手材料）。

round 5 里 eclipse.gsfc.nasa.gov 的 OH 页族只给出大食时刻、ΔT、星等、带宽等
概要，没有五个接触时刻；science.nasa.gov 的 /eclipses/ 页面确认了裸眼安全表述，
并从其链接清单里指出 safety / glossary / geometry / future-eclipses/eclipse-2024
四个子页——贝利珠、钻石环、接触点定义应当在 glossary，2024 的接触时刻清单
最可能在 eclipse-2024 专页。全部按真实响应记录，取不到就不写进来源。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
"""
import os
import sys
from pathlib import Path

TMP = Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B04"
sys.path.insert(0, str(TMP))
from fetch_sources2 import fetch  # noqa: E402

TARGETS = [
    ("nasa-science-safety", "https://science.nasa.gov/eclipses/safety/",
     "NASA Eclipse Viewing Safety page (eye protection rules, annular vs total)"),
    ("nasa-science-glossary", "https://science.nasa.gov/eclipses/glossary/",
     "NASA Eclipse Glossary (Baily's beads, diamond ring, contact definitions)"),
    ("nasa-science-geometry", "https://science.nasa.gov/eclipses/geometry/",
     "NASA Eclipse Geometry (umbra/penumbra cone and shadow sizes)"),
    ("nasa-science-2024", "https://science.nasa.gov/eclipses/future-eclipses/eclipse-2024/",
     "NASA 2024 Total Eclipse page (candidate for site-specific contact times)"),
]

if __name__ == "__main__":
    res = [fetch(k, u, n) for k, u, n in TARGETS]
    for r in res:
        print(r["request_id"], r["http_status"], r.get("response_bytes"), r["url"])
