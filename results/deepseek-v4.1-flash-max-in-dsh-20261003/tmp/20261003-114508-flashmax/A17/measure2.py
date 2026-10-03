from PIL import Image
im = Image.open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-adv.png").convert("RGB")
px = im.load()
W,H = im.size
def bbox(x0,x1,y0,y1):
    L=T=None;R=B=None
    for x in range(x0,x1):
        for y in range(y0,y1):
            p=px[x,y]
            if p[0]<120 and p[1]<120 and p[2]<120:
                if L is None or x<L: L=x
                if R is None or x>R: R=x
                if T is None or y<T: T=y
                if B is None or y>B: B=y
    return (L,T,R,B)
print("H row0:", bbox(440,470,10,70))
print("X row0:", bbox(1020,1060,10,70))
print("A row0:", bbox(90,135,10,70))
print("row labels area:", bbox(0,100,10,70))
# glyph 8 row0 at origin 1000
print("8 row0:", bbox(995,1015,10,70))
print("image size", W,H)