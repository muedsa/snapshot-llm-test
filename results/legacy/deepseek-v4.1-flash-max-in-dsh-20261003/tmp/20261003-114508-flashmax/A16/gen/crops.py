from PIL import Image, ImageDraw
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A16-visual-data-forensics\inputs\flawed-report.png"
im = Image.open(p).convert("RGB")
crops = {"legend": (640, 160, 1220, 230), "q1bars": (200, 380, 400, 600),
         "axis": (90, 270, 260, 600), "title": (40, 30, 900, 140)}
for name, box in crops.items():
    c = im.crop(box)
    s = 2 if (box[2]-box[0]) < 500 else 1.6
    c = c.resize((int(c.width*s), int(c.height*s)), Image.LANCZOS)
    d = ImageDraw.Draw(c)
    c.save(rf"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A16\flawed-{name}.png")
    print(name, box, c.size)
