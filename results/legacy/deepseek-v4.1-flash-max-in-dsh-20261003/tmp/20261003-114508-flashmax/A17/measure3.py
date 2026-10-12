from PIL import Image
im = Image.open(r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\probe-size.png").convert("RGB")
px=im.load(); W,H=im.size
def bbox(x0,x1,y0,y1):
    L=T=R=B=None
    for x in range(x0,x1):
        for y in range(y0,y1):
            p=px[x,y]
            if p[0]<120 and p[1]<120 and p[2]<120:
                if L is None or x<L: L=x
                if R is None or x>R: R=x
                if T is None or y<T: T=y
                if B is None or y>B: B=y
    return (L,T,R,B)
for i in range(5):
    y=30+i*90
    b=bbox(200,900,y-10,y+70)
    print(i, "H-strip bbox", b, "x-span", (b[2]-b[0]+1) if b[0] is not None else None, "cap-height", (b[3]-b[1]+1) if b[0] is not None else None)
print("size",W,H)