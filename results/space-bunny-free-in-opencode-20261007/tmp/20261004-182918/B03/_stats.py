import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "B03")
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "B03")

reqs = [json.loads(l) for l in io.open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") if l.strip()]
render = [r for r in reqs if r["request_type"] == "render"]
ok = [r for r in render if (r.get("content_type") or "").startswith("image/")]
bad = [r for r in render if r not in ok]
print("render requests:", len(render), "ok:", len(ok), "failed:", len(bad))
for r in bad:
    print("  FAIL", r["request_id"], r["http_status"], (r.get("error_summary") or "")[:110])
print("sum duration s:", round(sum(r.get("duration_ms") or 0 for r in reqs)/1000.0, 2))
print("first:", reqs[0]["started_at"], "last:", reqs[-1]["ended_at"])
# per-case finals
from PIL import Image
for i in range(1, 11):
    d = os.path.join(OUT, "case-%02d" % i)
    png = os.path.join(d, "final.png")
    snap = os.path.join(d, "final.snapshot")
    if not os.path.exists(png):
        print("case-%02d MISSING" % i); continue
    im = Image.open(png)
    s = io.open(snap, encoding="utf-8").read()
    els = len(re.findall(r"<[A-Z][A-Za-z]*[ />]", s))
    print("case-%02d %s %dx%d png=%dB snap=%dB els=%d" % (
        i, im.mode, im.width, im.height, os.path.getsize(png),
        os.path.getsize(snap), els))