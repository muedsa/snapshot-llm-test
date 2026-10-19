# -*- coding: utf-8 -*-
import io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "tmp/20261016T164020-m1/docs/"
for kw in ["sigmaX", "blendMode", "ColorFilter", "BackdropFilter", "ImageFiltered", "Opacity", "整体透明度"]:
    for f in sorted(glob.glob(BASE + "*.txt")):
        t = open(f, encoding="utf-8").read()
        n = t.count(kw)
        if n:
            print("%-18s %-28s x%d" % (kw, f.split("\\")[-1].replace(BASE, ""), n))
