from PIL import Image
import numpy as np

for name in ["symbol-color.png","symbol-black.png"]:
    p = f"outputs/run-20261016/A13/{name}"
    im = Image.open(p).convert("RGBA")
    arr = np.array(im).astype(np.float32)          # (h,w,4)
    rgb = arr[...,:3]                              # (h,w,3)
    a = arr[...,3:4] / 255.0                       # (h,w,1)
    premul_rgb = rgb * a                           # (h,w,3)
    premul = np.concatenate([premul_rgb, arr[...,3:4]], axis=2).astype(np.uint8)
    premul_im = Image.fromarray(premul, "RGBA")
    small = premul_im.resize((32,32), Image.LANCZOS)
    sa = np.array(small).astype(np.float32)
    s_rgb = sa[...,:3]
    s_a = sa[...,3:4]
    eps = 1e-6
    unpremul_rgb = s_rgb / np.maximum(s_a/255.0, eps)
    unpremul_rgb = np.clip(unpremul_rgb, 0, 255)
    out = np.concatenate([unpremul_rgb, sa[...,3:4]], axis=2).astype(np.uint8)
    out_name = f"tmp/run-20261016/A13/{name.replace('.png','')}-32.png"
    Image.fromarray(out, "RGBA").save(out_name)
    print(f"saved {out_name} size {Image.open(out_name).size}")
