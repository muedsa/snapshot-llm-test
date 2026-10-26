"""A15 参考图墨迹精确补测：标题/刻度/活动名/页脚/侧栏文本/KPI/月份"""
from PIL import Image

im = Image.open('tasks/A15-reference-reconstruction/inputs/reference.png').convert('RGB')
px = im.load()


def ink_bbox(x0, x1, y0, y1, t=150):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[x, y][0] < t]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys), max(xs)-min(xs)+1, max(ys)-min(ys)+1)


print("title:", ink_bbox(250, 700, 30, 80))
print("subtitle:", ink_bbox(270, 700, 80, 105, t=180))
# tick labels: exclude gridline rows (405,441,477,513,549) +-1
for lbl, yc in [("120", 402), ("90", 439), ("60", 474), ("30", 511), ("0", 546)]:
    b = ink_bbox(285, 345, yc-6, yc+7)
    print("tick", lbl, b)
# activity name1 (text only, exclude dot x<1070)
print("act name1:", ink_bbox(1070, 1260, 390, 415))
print("act name2:", ink_bbox(1070, 1260, 450, 475))
print("act name3:", ink_bbox(1070, 1260, 510, 535))
print("act time1:", ink_bbox(1070, 1200, 418, 438, t=180))
# footer
print("footer:", ink_bbox(260, 700, 860, 890, t=180))
# sidebar texts
print("NORTHSTAR:", ink_bbox(60, 220, 30, 60))
print("Overview white text:", ink_bbox(50, 200, 120, 160, t=200))
print("Projects text:", ink_bbox(50, 200, 185, 212, t=200))
print("Analytics text:", ink_bbox(50, 200, 250, 276, t=200))
print("Settings text:", ink_bbox(50, 200, 314, 342, t=200))
print("PRO WORKSPACE text:", ink_bbox(30, 195, 762, 786, t=150))
print("12 team members:", ink_bbox(30, 195, 795, 820, t=150))
print("Manage access:", ink_bbox(30, 195, 820, 855, t=150))
# KPI labels/values
print("K1 label:", ink_bbox(270, 610, 155, 176))
print("K2 label:", ink_bbox(650, 995, 155, 176))
print("K3 label:", ink_bbox(1035, 1380, 155, 176))
print("K1 value:", ink_bbox(270, 610, 195, 232))
print("K2 value:", ink_bbox(650, 995, 195, 232))
print("K3 value:", ink_bbox(1035, 1380, 195, 232))
print("K1 change:", ink_bbox(270, 610, 242, 262, t=180))
print("K2 change:", ink_bbox(650, 995, 242, 262, t=180))
print("K3 change:", ink_bbox(1035, 1380, 242, 262, t=180))
# months
for m, (x0, x1) in {"Apr": (360, 410), "May": (460, 510), "Jun": (560, 610),
                    "Jul": (665, 710), "Aug": (765, 810), "Sep": (865, 915)}.items():
    print("month", m, ink_bbox(x0, x1, 555, 580))
# button text
print("button text:", ink_bbox(1200, 1390, 48, 86, t=240))
# pill texts
print("pill1 text:", ink_bbox(1030, 1175, 729, 757, t=180))
print("pill2 text:", ink_bbox(1030, 1175, 764, 792, t=180))
print("pill3 text:", ink_bbox(1030, 1175, 799, 827, t=180))
# table header labels
print("hdr PROJECT:", ink_bbox(290, 400, 695, 712, t=150))
print("hdr OWNER:", ink_bbox(770, 900, 695, 712, t=150))
print("hdr STATUS:", ink_bbox(1020, 1160, 695, 712, t=150))
print("hdr DUE:", ink_bbox(1230, 1300, 695, 712, t=150))
# chart title / Apr-Sep / unit
print("chart title:", ink_bbox(280, 880, 330, 358))
print("Apr-Sep:", ink_bbox(880, 990, 330, 358))
print("unit:", ink_bbox(280, 360, 370, 392, t=180))
# activity title
print("act title:", ink_bbox(1040, 1260, 330, 360))
# table title
print("table title:", ink_bbox(280, 700, 640, 670))
# owner/due cells
print("owner1:", ink_bbox(770, 950, 730, 752, t=150))
print("owner2:", ink_bbox(770, 950, 766, 788, t=150))
print("owner3:", ink_bbox(770, 950, 801, 823, t=150))
print("due1:", ink_bbox(1230, 1390, 730, 752, t=150))
print("due2:", ink_bbox(1230, 1390, 766, 788, t=150))
print("due3:", ink_bbox(1230, 1390, 801, 823, t=150))
print("proj1:", ink_bbox(290, 650, 730, 755, t=150))
print("proj2:", ink_bbox(290, 650, 766, 790, t=150))
print("proj3:", ink_bbox(290, 650, 801, 825, t=150))
