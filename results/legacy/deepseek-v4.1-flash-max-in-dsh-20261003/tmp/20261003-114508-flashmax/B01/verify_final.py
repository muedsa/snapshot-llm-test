import hashlib, os, sys
from PIL import Image
base_out = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B01"
base_tmp = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B01\render"
acc = ["c01-roast-profile.v3.png","c02-marathon-profile.v3.png","c03-vinyl-cover.v3.png",
       "c04-med-plan.v2.png","c05-lunar-calendar.v3.png","c06-leather-pattern.v3.png",
       "c07-vaccine-timeline.v2.png","c08-podcast-wave.v1.png","c09-approach-chart.v3.png",
       "c10-tea-wheel.v3.png"]
ok = True
for i, name in enumerate(acc, 1):
    p = os.path.join(base_out, "case-%02d" % i, "final.png")
    t = os.path.join(base_tmp, name)
    h1 = hashlib.sha256(open(p,"rb").read()).hexdigest()
    h2 = hashlib.sha256(open(t,"rb").read()).hexdigest()
    im = Image.open(p)
    same = "MATCH" if h1 == h2 else "DIFF"
    ok = ok and h1 == h2
    print("case-%02d  %s  %sx%s  %s  %s" % (i, os.path.basename(name), im.size[0], im.size[1], im.format, same))
print("ALL-MATCH", ok)