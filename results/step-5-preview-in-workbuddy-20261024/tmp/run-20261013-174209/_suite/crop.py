"""裁剪放大局部以便目视检查。"""
import sys
from PIL import Image

src, dst, box, scale = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(",")], int(sys.argv[4])
im = Image.open(src)
c = im.crop((box[0], box[1], box[2], box[3]))
c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
c.save(dst)
print(dst, c.size)
