import hashlib, os
from PIL import Image
O = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B02"
T = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B02\render"
acc = ["t01-season-poster.v3.png","t02-sowing-calendar.v3.png","t03-seed-label.v3.png",
       "t04-plot-map.v3.png","t05-shift-board.v1.png","t06-member-card.v1.png",
       "t07-market-board.v2.png","t08-kids-workshop.v2.png","t09-harvest-log.v3.png",
       "t10-impact-report.v3.png"]
ok = True
for i, n in enumerate(acc, 1):
    p = os.path.join(O, "case-%02d" % i, "final.png"); t = os.path.join(T, n)
    a = hashlib.sha256(open(p,"rb").read()).hexdigest()
    b = hashlib.sha256(open(t,"rb").read()).hexdigest()
    im = Image.open(p); ok = ok and a == b
    print("case-%02d %-26s %sx%-4d %s" % (i, n, im.size[0], im.size[1], "MATCH" if a==b else "DIFF"))
print("ALL-MATCH", ok)