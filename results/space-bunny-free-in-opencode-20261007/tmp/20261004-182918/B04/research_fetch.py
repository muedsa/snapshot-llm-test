# B04 research fetcher: pulls real source documents through snapkit so every GET is logged.
import os, sys, json
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, state as S

TASK = "B04"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
os.makedirs(os.path.join(TMP, "research"), exist_ok=True)

TARGETS = [
    # service documentation (required reading, real GETs)
    ("https://open-snapshot.muedsa.com/ai-guide.md", "docs/ai-guide.md", "document"),
    ("https://snapshot.muedsa.com/", "docs/snapshot-doc-root.html", "document"),
    ("https://snapshot.muedsa.com/fonts", "docs/fonts.json", "font_list"),
    # research sources
    ("https://www.gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_mlo.txt",
     "research/gml-co2-annmean-mlo.txt", "research_data"),
    ("https://www.gml.noaa.gov/webdata/ccgg/trends/co2/co2_gr_growth.txt",
     "research/gml-co2-annual-growth.txt", "research_data"),
    ("https://www.pmel.noaa.gov/co2/story/What+is+Ocean+Acidification",
     "research/pmel-what-is-ocean-acidification.html", "research_source"),
    ("https://www.noaa.gov/education/resource-collections/ocean-coasts/ocean-acidification",
     "research/noaa-ocean-acidification.html", "research_source"),
    ("https://oceanacidification.noaa.gov/oa-indicators-explained/",
     "research/noaa-oa-indicators-explained.html", "research_source"),
    ("https://www.pmel.noaa.gov/co2/story/The+pH+Scale",
     "research/pmel-ph-scale.html", "research_source"),
    ("https://oceanacidification.noaa.gov/what-is-ocean-acidification/",
     "research/noaa-oa-what-is.html", "research_source"),
]

results = []
for url, name, kind in TARGETS:
    try:
        st, path = snapkit.fetch_doc(url, name, kind)
    except Exception as e:  # noqa: BLE001
        st, path = None, "%s: %s" % (type(e).__name__, e)
    results.append({"url": url, "status": st, "saved": path})
    print(st, url, "->", path)

with open(os.path.join(TMP, "research", "fetch-results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=2)
