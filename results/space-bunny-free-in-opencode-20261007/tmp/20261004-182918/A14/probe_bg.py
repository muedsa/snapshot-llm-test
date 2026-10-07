"""A14 diagnostic probe: why did the whole canvas paint flat #3E49E6?"""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
PDIR = os.path.join(TMP, "probe")

VARIANTS = {
    # A: single full-canvas paper gradient only
    "A": """<Snapshot type="png" background="#F7F5EFFF">
<Container width="1200" height="630">
<Stack fit="EXPAND">
<Positioned left="0" top="0" width="1200" height="630">
<Container width="1200" height="630" gradientType="LINEAR" gradientColors="#F7F5EFFF,#ECEADFFF" gradientBegin="(0,0)" gradientEnd="(0,630)" />
</Positioned>
<Positioned left="40" top="300" width="200" height="60">
<Text color="#14182EFF" fontSize="28" fontFamily="Inter" text="VARIANT A"/>
</Positioned>
</Stack>
</Container>
</Snapshot>""",
    # B: paper gradient + a 1200x6 accent gradient bar on top
    "B": """<Snapshot type="png" background="#F7F5EFFF">
<Container width="1200" height="630">
<Stack fit="EXPAND">
<Positioned left="0" top="0" width="1200" height="630">
<Container width="1200" height="630" gradientType="LINEAR" gradientColors="#F7F5EFFF,#ECEADFFF" gradientBegin="(0,0)" gradientEnd="(0,630)" />
</Positioned>
<Positioned left="0" top="0" width="1200" height="6">
<Container width="1200" height="6" gradientType="LINEAR" gradientColors="#3E49E6FF,#1B2382FF" gradientBegin="(0,0)" gradientEnd="(1200,0)" />
</Positioned>
<Positioned left="40" top="300" width="200" height="60">
<Text color="#14182EFF" fontSize="28" fontFamily="Inter" text="VARIANT B"/>
</Positioned>
</Stack>
</Container>
</Snapshot>""",
    # C: paper FLAT + accent gradient bar (isolates gradient on a short box)
    "C": """<Snapshot type="png" background="#F7F5EFFF">
<Container width="1200" height="630">
<Stack fit="EXPAND">
<Positioned left="0" top="0" width="1200" height="630">
<Container width="1200" height="630" color="#F7F5EFFF" />
</Positioned>
<Positioned left="0" top="0" width="1200" height="6">
<Container width="1200" height="6" gradientType="LINEAR" gradientColors="#3E49E6FF,#1B2382FF" gradientBegin="(0,0)" gradientEnd="(1200,0)" />
</Positioned>
<Positioned left="40" top="300" width="200" height="60">
<Text color="#14182EFF" fontSize="28" fontFamily="Inter" text="VARIANT C"/>
</Positioned>
</Stack>
</Container>
</Snapshot>""",
    # D: flat paper + flat colour accent bar (no gradient anywhere)
    "D": """<Snapshot type="png" background="#F7F5EFFF">
<Container width="1200" height="630">
<Stack fit="EXPAND">
<Positioned left="0" top="0" width="1200" height="630">
<Container width="1200" height="630" color="#F7F5EFFF" />
</Positioned>
<Positioned left="0" top="0" width="1200" height="6">
<Container width="1200" height="6" color="#3E49E6FF" />
</Positioned>
<Positioned left="40" top="300" width="200" height="60">
<Text color="#14182EFF" fontSize="28" fontFamily="Inter" text="VARIANT D"/>
</Positioned>
</Stack>
</Container>
</Snapshot>""",
    # E: many small gradient tiles (does one gradient hijack every other box?)
    "E": """<Snapshot type="png" background="#F7F5EFFF">
<Container width="1200" height="630">
<Stack fit="EXPAND">
<Positioned left="0" top="0" width="1200" height="630">
<Container width="1200" height="630" color="#F7F5EFFF" />
</Positioned>
<Positioned left="40" top="40" width="44" height="44">
<Container width="44" height="44" gradientType="LINEAR" gradientColors="#3E49E6FF,#1B2382FF" gradientBegin="(0,0)" gradientEnd="(44,44)" borderRadius="12" />
</Positioned>
<Positioned left="200" top="40" width="300" height="44">
<Container width="300" height="44" color="#0B7A4BFF" borderRadius="12" />
</Positioned>
<Positioned left="40" top="300" width="200" height="60">
<Text color="#14182EFF" fontSize="28" fontFamily="Inter" text="VARIANT E"/>
</Positioned>
</Stack>
</Container>
</Snapshot>""",
}


def sample(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    return {"size": im.size,
            "topleft": px[0, 0], "center": px[600, 315], "bar": px[600, 3],
            "belowbar": px[600, 20], "mark_a": px[60, 60], "green": px[300, 60],
            "bottomright": px[1199, 629]}


for k in sorted(VARIANTS):
    r = snapkit.render(VARIANTS[k], "diag-%s.png" % k, "diag-%s.snapshot" % k,
                       final=False, out_dir=PDIR)
    print("=== variant", k, "ok=%s" % r.get("ok"), r.get("status"))
    if not r.get("ok"):
        print("   ", (r.get("error") or "")[:300])
        continue
    print("   ", sample(r["image"]))
for w in D.warnings():
    print("WARN", w)