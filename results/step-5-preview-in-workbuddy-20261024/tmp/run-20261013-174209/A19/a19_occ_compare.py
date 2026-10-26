"""遮挡 A/B 两版像素等价比较 + 遮挡有效性验证。"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "outputs" / "run-20261013-174209" / "A19"
TMP = ROOT / "tmp" / "run-20261013-174209" / "A19"

A = OUT / "occlusion.png"
B = OUT / "occlusion-alternative.png"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


a_img = Image.open(A)
b_img = Image.open(B)
cmp_rec = {
    "decoder": f"Pillow {PIL.__version__}（Image.open 默认解码器）",
    "decoder_mode": ("RGBA，8 位未预乘；服务返回 RGBA，四通道全部参与比较；"
                     "不合成到白底、不缩放、不忽略透明通道或透明像素的 RGB"),
    "same_size": a_img.size == b_img.size,
    "size_a": list(a_img.size),
    "size_b": list(b_img.size),
}
a_arr = np.asarray(a_img.convert("RGBA"))
b_arr = np.asarray(b_img.convert("RGBA"))
cmp_rec["same_array_shape"] = bool(a_arr.shape == b_arr.shape)
cmp_rec["dtype"] = str(a_arr.dtype)
diff_mask = np.any(a_arr != b_arr, axis=2)
diff_px = int(diff_mask.sum())
max_ch = int(np.abs(a_arr.astype(int) - b_arr.astype(int)).max()) if diff_px else 0
cmp_rec["different_pixels"] = diff_px
cmp_rec["max_channel_diff"] = max_ch
cmp_rec["array_hash_a"] = hashlib.sha256(a_arr.tobytes()).hexdigest()
cmp_rec["array_hash_b"] = hashlib.sha256(b_arr.tobytes()).hexdigest()
cmp_rec["array_hash_equal"] = cmp_rec["array_hash_a"] == cmp_rec["array_hash_b"]
cmp_rec["verdict"] = ("pixel_equivalent"
                      if (diff_px == 0 and cmp_rec["same_size"]
                          and cmp_rec["array_hash_equal"]
                          and cmp_rec["same_array_shape"])
                      else "not_equivalent")
print(json.dumps({k: v for k, v in cmp_rec.items() if not k.startswith("array_hash")},
                 ensure_ascii=False, indent=1))
print("array_hash_a:", cmp_rec["array_hash_a"][:24], "...")
print("array_hash_b:", cmp_rec["array_hash_b"][:24], "...")
print("file sha256 A:", sha256_file(A))
print("file sha256 B:", sha256_file(B))

# ---------- 遮挡有效性：矩形区域内必须完全等于遮挡物颜色 ----------
OCC = (400, 220, 760, 580)
sub_a = a_arr[OCC[1]:OCC[3], OCC[0]:OCC[2], :3]
occ_col = np.array([15, 23, 42])
inside_a = int((np.abs(sub_a.astype(int) - occ_col).max(axis=2) > 2).sum())
sub_b = b_arr[OCC[1]:OCC[3], OCC[0]:OCC[2], :3]
inside_b = int((np.abs(sub_b.astype(int) - occ_col).max(axis=2) > 2).sum())
alpha_ok = int((a_arr[..., 3] != 255).sum()) + int((b_arr[..., 3] != 255).sum())
print(f"遮挡矩形内非遮挡色像素: A={inside_a} B={inside_b}（应为 0，即隐藏内容零泄漏）")
print(f"遮挡矩形面积: {sub_a.shape[0]}x{sub_a.shape[1]} = {sub_a.shape[0] * sub_a.shape[1]} px")
print(f"非 255 的 alpha 像素总数: {alpha_ok}")

(TMP / "occ-compare.json").write_text(json.dumps(
    {"comparison": cmp_rec,
     "file_sha256": {"occlusion.png": sha256_file(A),
                     "occlusion-alternative.png": sha256_file(B)},
     "occluder_interior_noncolor_px": {"A": inside_a, "B": inside_b}},
    ensure_ascii=False, indent=1), encoding="utf-8")
print("saved tmp/run-20261013-174209/A19/occ-compare.json")
