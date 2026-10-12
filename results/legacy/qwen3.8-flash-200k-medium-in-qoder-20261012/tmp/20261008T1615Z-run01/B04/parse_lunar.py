"""B04 研究层 3b：解析 NASA《Catalog of Lunar Eclipses: 2001 to 2100》的 228 行月食表。

页面来自 round 3 抓取（nasa-lecat5-2001-2100.html，HTTP 200，78,017 字节，见 requests.jsonl）。
月食与日食同属一套食季，只有把两边合起来才能"量出"食季窗口与食年，
所以件 04 需要这张表。

Run from the suite root with SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID set.
输出：tmp/<run>/B04/research/lunar.json
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B04"
MON = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

ROW = re.compile(
    r"(\d{5})\s+(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{2})\s+"
    r"(\d{2}:\d{2}:\d{2})\s+(\d{2,3})\s+(\d{2,4})\s+(\d{1,3})\s+([NPT])([+\-a-z]?)\s+([a-z+-]{2,3})\s+"
    r"(-?\d\.\d{4})\s+(-?\d\.\d{4})")


def main():
    html = (B / "sources" / "nasa-lecat5-2001-2100.html").read_text(
        encoding="utf-8", errors="replace")
    txt = re.sub(r"<[^>]+>", " ", html)
    txt = re.sub(r"[ \t]+", " ", txt)
    rows, seen = [], set()
    for m in ROW.finditer(txt):
        cat = m.group(1)
        if cat in seen:
            continue
        seen.add(cat)
        rows.append({
            "catalog_number": int(cat),
            "date": "%s-%02d-%02d" % (m.group(2), MON[m.group(3)], int(m.group(4))),
            "greatest_ut": m.group(5),
            "delta_t_catalog_s": int(m.group(6)),
            "lunation": int(m.group(7)),
            "saros": int(m.group(8)),
            "type": m.group(9),
            "type_class": m.group(9) + m.group(10),
            "qse": m.group(11),
            "gamma": float(m.group(12)),
            "umbral_magnitude": float(m.group(13)),
        })
    page = re.sub(r"<[^>]+>", " ", html)
    claim = dict(re.findall(r"Number of Years with (\d) Eclipses:\s*(\d+)", page))
    counts = {}
    for r in rows:
        counts[r["type"]] = counts.get(r["type"], 0) + 1
    per_year = {}
    for r in rows:
        per_year[r["date"][:4]] = per_year.get(r["date"][:4], 0) + 1
    by_n = {}
    for v in per_year.values():
        by_n[v] = by_n.get(v, 0) + 1
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path_base": "suite_root",
        "source_file": "sources/nasa-lecat5-2001-2100.html",
        "rows": rows,
        "row_count": len(rows),
        "type_counts": counts,
        "page_type_table": {"N": 86, "P": 57, "T": 85, "all": 228},
        "years_by_eclipse_count_parsed": {str(k): v for k, v in sorted(by_n.items())},
        "years_by_eclipse_count_page": {k: int(v) for k, v in sorted(claim.items())},
        "years_covered": len(per_year),
        "reconciles": len(rows) == 228 and counts == {"T": 85, "P": 57, "N": 86},
    }
    (B / "research" / "lunar.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("rows %d | types %s | 年数 %d | 每年计数(解析) %s | 页面自述 %s" % (
        len(rows), counts, len(per_year), out["years_by_eclipse_count_parsed"],
        out["years_by_eclipse_count_page"]))


if __name__ == "__main__":
    main()
