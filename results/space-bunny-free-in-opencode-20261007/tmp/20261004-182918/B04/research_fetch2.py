# B04: second round of real source fetches (primary literature / assessment reports).
import os, sys, json
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, state as S

TASK = "B04"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

TARGETS = [
    ("https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2019.00227/full",
     "research/bednarsek-2019-pteropod-thresholds.html", "research_source"),
    ("https://ipcc.ch/report/ar6/wg1/chapter/summary-for-policymakers/",
     "research/ipcc-ar6-wg1-spm.html", "research_source"),
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6901524/",
     "research/lee-2019-surface-ph-buffer-capacity.html", "research_source"),
    ("https://oceantoday.noaa.gov/oceanasalab_oceanacid/",
     "research/noaa-ocean-today-ocean-as-a-lab.html", "research_source"),
    ("https://www.gml.noaa.gov/ccgg/trends/data.html",
     "research/gml-trends-data.html", "research_source"),
]

results = []
for url, name, kind in TARGETS:
    try:
        st, path = snapkit.fetch_doc(url, name, kind)
    except Exception as e:  # noqa: BLE001
        st, path = None, "%s: %s" % (type(e).__name__, e)
    results.append({"url": url, "status": st, "saved": path})
    print(st, url, "->", path)

with open(os.path.join(TMP, "research", "fetch-results-2.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=2)
