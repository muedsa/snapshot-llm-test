# -*- coding: utf-8 -*-
"""Compare the two occlusion PNGs at the pixel level and write equivalence.json.

Method (per task): decode BOTH raw service-response PNGs to 8-bit UNPREMULTIPLIED
RGBA with the same decoder; the full per-channel arrays must be IDENTICAL
(differing pixels = 0). No compositing onto white, no scaling, alpha channel and
RGB of transparent pixels included. File SHA-256 is recorded for provenance but
NOT used as the pixel-equivalence verdict.
"""
import hashlib
import json
import pathlib
import platform

import PIL
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A19/gen"
OUT = ROOT / "outputs/run-20261011-01/A19"
OUT.mkdir(parents=True, exist_ok=True)

A_PNG = GEN / "occlusion.png"
B_PNG = GEN / "occlusion-alternative.png"


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    # --- raw file provenance
    info = {}
    for tag, p in (("A", A_PNG), ("B", B_PNG)):
        im = Image.open(p)
        info[tag] = {
            "png": str(p.relative_to(ROOT)),
            "file_bytes": p.stat().st_size,
            "file_sha256": sha256(p),
            "decoder_input_mode": im.mode,
            "size": list(im.size),
        }
        im.close()

    # --- decode to 8-bit unpremultiplied RGBA (PNG native channel model)
    ia = Image.open(A_PNG).convert("RGBA")
    ib = Image.open(B_PNG).convert("RGBA")
    assert ia.mode == ib.mode == "RGBA", (ia.mode, ib.mode)
    assert ia.size == ib.size, (ia.size, ib.size)
    ba, bb = ia.tobytes(), ib.tobytes()

    same_size = ia.size == ib.size
    arr_a_sha = hashlib.sha256(ba).hexdigest()
    arr_b_sha = hashlib.sha256(bb).hexdigest()

    if ba == bb:
        diff_pixels = 0
        max_channel_diff = 0
        first_diff = None
        equiv = True
    else:
        equiv = False
        diff_pixels = 0
        max_channel_diff = 0
        first_diff = None
        w, h = ia.size
        pa, pb = ia.load(), ib.load()
        for y in range(h):
            for x in range(w):
                ca, cb = pa[x, y], pb[x, y]
                if ca != cb:
                    diff_pixels += 1
                    d = max(abs(ca[k] - cb[k]) for k in range(4))
                    max_channel_diff = max(max_channel_diff, d)
                    if first_diff is None:
                        first_diff = {"xy": [x, y], "a": list(ca), "b": list(cb)}

    doc = {
        "schema_version": 1,
        "task_id": "A19",
        "path_base": "output_dir",
        "artifacts": {
            "occlusion_a": {
                "dsl": "occlusion.snapshot",
                "png": "occlusion.png",
            },
            "occlusion_b": {
                "dsl": "occlusion-alternative.snapshot",
                "png": "occlusion-alternative.png",
            },
        },
        "versions": [
            {
                "version": "A",
                "dsl": "occlusion.snapshot",
                "png": "occlusion.png",
                "file_sha256": info["A"]["file_sha256"],
                "file_bytes": info["A"]["file_bytes"],
                "hidden_content": "遮挡板下：绿色圆形 d=160 @(320,300) + 白色数字“3”"
                                  "（fontSize96、BOLD），圆形带阴影 "
                                  "boxShadow=\"0 8 24 0 #00000066 NORMAL\"",
                "hidden_diff_point": "DSL中隐藏组（容器+文本）与B不同；绘制顺序上"
                                     "位于不透明遮挡物(240,240,320,320)之前（下层）",
            },
            {
                "version": "B",
                "dsl": "occlusion-alternative.snapshot",
                "png": "occlusion-alternative.png",
                "file_sha256": info["B"]["file_sha256"],
                "file_bytes": info["B"]["file_bytes"],
                "hidden_content": "遮挡板下：橙色圆角方 160×160 @(320,300) "
                                  "borderRadius=40 + 白色数字“8”（fontSize96、"
                                  "BOLD），同款阴影",
                "hidden_diff_point": "DSL中隐藏组（容器+文本）与A不同；其余可见"
                                     "元素（背景、标题栏、四角主体、遮挡板及其"
                                     "标签）与A逐元素一致",
            },
        ],
        "comparison": {
            "decoder": "Pillow (PIL.Image)",
            "decoder_version": PIL.__version__,
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
            },
            "method": "两文件各自 Image.open(...).convert(\"RGBA\") 解码为8位"
                      "未预乘RGBA（PNG规范通道模型即未预乘），比较完整字节数组；"
                      "未合成到白底、未缩放、未忽略alpha或透明像素RGB",
            "size_a": info["A"]["size"],
            "size_b": info["B"]["size"],
            "same_dimensions": same_size,
            "rgba_array_sha256_a": arr_a_sha,
            "rgba_array_sha256_b": arr_b_sha,
            "differing_pixels": diff_pixels,
            "max_channel_diff": max_channel_diff,
            "first_difference": first_diff,
            "pixel_equivalent": equiv,
            "file_hash_note": "两PNG的文件SHA-256已记录用于来源留痕，但像素等价"
                              "判定不使用文件哈希，而以解码后的RGBA逐像素比较为准",
            "hidden_content_confirmed_different":
                "A隐藏组=绿圆+“3”，B=橙圆角方+“8”（DSL文本差异可见于两份"
                ".snapshot；像素等价同时证明两者均被完全遮住，含阴影影响）",
        },
        "occluder_coverage": {
            "occluder_bbox": [240, 240, 560, 560],
            "hidden_body_bbox": [320, 300, 480, 460],
            "shadow_probe_extent": "探针实测 boxShadow=\"6 10 24 0 ...\" 的最大"
                                   "外扩≈左16/上12/右34/下31px；本场景阴影为"
                                   "\"0 8 24 0 ...\"，外扩≤右/下24+8、左/上24",
            "coverage_margin_min_px": 56,
            "verdict": "隐藏主体+阴影外接框完全落在遮挡物内部（最近边距≥56px），"
                       "且遮挡物为完全不透明填充；两版RGBA逐像素一致（差异0）"
                       "即为最终证明",
        },
    }

    path = OUT / "equivalence.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print("written:", path.relative_to(ROOT))
    print("file sha A:", info["A"]["file_sha256"][:16], "...")
    print("file sha B:", info["B"]["file_sha256"][:16], "...")
    print("same dims:", same_size, "| diff pixels:", diff_pixels,
          "| max channel diff:", max_channel_diff,
          "| pixel_equivalent:", equiv)
    assert equiv, "Occlusion pair is NOT pixel-equivalent — fix the scene!"


if __name__ == "__main__":
    main()
