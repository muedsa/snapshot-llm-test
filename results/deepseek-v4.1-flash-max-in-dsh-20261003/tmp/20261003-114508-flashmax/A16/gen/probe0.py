from PIL import Image
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A16-visual-data-forensics\inputs\flawed-report.png"
im = Image.open(p).convert("RGB"); px = im.load()
for (x, y, tag) in [(250,500,"q1 blue?"),(310,520,"q1 orange?"),(900,200,"legend blue"),
                    (1090,200,"legend orange"),(430,500,"q2 blue"),(490,520,"q2 orange"),
                    (600,500,"q3 blue"),(660,520,"q3 orange"),(760,500,"q4 blue"),(830,520,"q4 orange")]:
    print(f"{tag:14s} ({x},{y}) #%02X%02X%02X" % px[x,y])
