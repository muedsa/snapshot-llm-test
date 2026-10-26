"""A15 参考图剩余墨迹测量：页脚/PRO卡文本/导航文字/按钮文字权重"""
from PIL import Image

im = Image.open('tasks/A15-reference-reconstruction/inputs/reference.png').convert('RGB')
px = im.load()
CARD = (35, 57, 84)


def ink_bbox(x0, x1, y0, y1, pred):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if pred(px[x, y])]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys), max(xs)-min(xs)+1, max(ys)-min(ys)+1)


def not_card(c):
    return abs(c[0]-CARD[0]) > 40 or abs(c[1]-CARD[1]) > 40 or abs(c[2]-CARD[2]) > 40


def navtext(c):
    # 导航未选中文字 (190,202,221) 及其 AA
    return 150 < c[0] < 235 and c[1] > 170 and c[2] > 200


print("footer:", ink_bbox(270, 700, 860, 890, lambda c: c[0] < 190 and c[2] < 200 and c[0] > 60))
print("PRO text:", ink_bbox(30, 195, 760, 790, not_card))
print("12 members:", ink_bbox(30, 195, 795, 820, not_card))
print("manage:", ink_bbox(30, 195, 820, 855, not_card))
print("nav Projects text:", ink_bbox(50, 200, 185, 212, navtext))
print("nav Analytics text:", ink_bbox(50, 200, 250, 276, navtext))
print("nav Settings text:", ink_bbox(50, 200, 314, 342, navtext))
print("nav Overview text:", ink_bbox(50, 200, 120, 160, lambda c: c[0] > 235 and c[1] > 235 and c[2] > 235))
# button text: white on blue
print("button text:", ink_bbox(1200, 1390, 48, 86, lambda c: c[0] > 240 and c[1] > 240 and c[2] > 240))
# button text stroke weight: count fully-white pixels vs AA
cnt_full = sum(1 for y in range(48, 86) for x in range(1200, 1390) if px[x, y][0] > 250 and px[x, y][1] > 250)
cnt_aa = sum(1 for y in range(48, 86) for x in range(1200, 1390) if 200 < px[x, y][0] <= 250)
print("button text full-white px:", cnt_full, "aa px:", cnt_aa)
# 对照：pill1 text (36,92,228) on (231,239,255)
# sidebar nav text color sample
print("nav text colors:", px[70, 199], px[90, 199], px[110, 199])
print("pro card text colors:", px[45, 774], px[60, 774], px[45, 808], px[45, 838])
