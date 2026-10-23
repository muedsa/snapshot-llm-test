"""A19 自检视图：为视觉复核生成裁切/缩放视图（均为临时预览，非交付件）。

用途：
* 放大网格局部，核对编号文字在目标观看尺寸下的可读性与圆环内径 = 外径一半；
* 裁出遮挡面板区域，核对没有任何虚线、描边、残影泄漏隐藏内容；
* A/B 并排，核对可见前景逐元素一致。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import time

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"
PREV = SUITE_ROOT / "tmp" / RUN_ID / "A19" / "preview"

sys.path.insert(0, str(HERE.parent))
import a19_core as C  # noqa: E402


def ihdr(body):
    return struct.unpack(">II", body[16:24])


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    from PIL import Image

    PREV.mkdir(parents=True, exist_ok=True)
    views = []

    def make(name, src, box, scale, note, pad=0):
        img = Image.open(OUT / (src + ".png"))
        if pad:
            b = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
        else:
            b = box
        crop = img.crop(b)
        resample = Image.NEAREST if scale >= 1 else Image.LANCZOS
        out = crop.resize((max(1, int(round(crop.width * scale))),
                           max(1, int(round(crop.height * scale)))),
                          resample)
        path = PREV / name
        out.save(path, format="PNG")
        views.append({"name": name,
                      "path": str(path.relative_to(SUITE_ROOT)),
                      "source": src + ".png",
                      "crop": list(b), "scale": scale,
                      "out_size": [out.width, out.height], "note": note})
        print("%-34s %s <- %s crop=%s x%s"
              % (name, out.size, src, b, scale))
        return path

    # 网格 2×2 象限（4×4 格），核对标签可读性与颜色/形状/尺寸分布
    make("grid-quadrant-tl-1x.png", "grid-scene", (0, 0, 800, 800), 1,
         "左上 4×4 格（G01–G32）原尺寸：核对编号可读性与三种尺寸的差异")

    # 圆环几何：G03 绿环 size=80，内径应为 40
    make("grid-ring-G03-5x.png", "grid-scene", (452, 52, 548, 148), 5,
         "G03 圆环放大 5 倍：外径 80、内径应为 40（border 20）")

    # 最小尺寸圆环：G07 绿环 size=48，内径应为 24
    make("grid-ring-G07-6x.png", "grid-scene",
         (1264, 64, 1336, 136), 6,
         "G07 圆环放大 6 倍：外径 48、内径应为 24（border 12）")

    # 第 5 行整行（Q11 排序题）
    make("grid-row5-2x.png", "grid-scene", (0, 800, 1600, 1000), 2,
         "第 5 行 G33–G40 放大 2 倍：核对 Q11 的尺寸顺序")

    # 第 3 行整行（Q17 计数题）
    make("grid-row3-2x.png", "grid-scene", (0, 400, 1600, 600), 2,
         "第 3 行 G17–G24 放大 2 倍：核对 Q17 的圆环与紫色计数")

    # 整图缩略，核对整体无遮挡/无越界
    make("grid-full-400w.png", "grid-scene", (0, 0, 1600, 1600), 0.25,
         "全图缩到宽 400（0.25x）：核对整体布局；此尺寸下编号文字已不可读，"
         "属已知限制，仅用于判断整体构图与分布")

    # 遮挡面板区域：核对无泄漏
    make("occ-panel-region-1x.png", "occlusion", (40, 40, 760, 380), 1,
         "遮挡面板整块：核对四边与圆角处都没有隐藏内容泄漏")
    make("occ-panel-corner-4x.png", "occlusion", (40, 40, 200, 200), 4,
         "面板左上角放大 4 倍：核对圆角处无虚线、无描边、无残影")

    # A/B 并排
    a = Image.open(OUT / "occlusion.png")
    b = Image.open(OUT / "occlusion-alternative.png")
    scale = 0.75
    wa, ha = int(a.width * scale), int(a.height * scale)
    a2 = a.resize((wa, ha), Image.NEAREST)
    b2 = b.resize((wa, ha), Image.NEAREST)
    canvas = Image.new("RGB", (wa * 2 + 24, ha + 44), "white")
    canvas.paste(a2, (0, 44))
    canvas.paste(b2, (wa + 24, 44))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(canvas)
    d.text((wa // 2 - 24, 16), "A", fill="#0F172A")
    d.text((wa + 24 + wa // 2 - 24, 16), "B", fill="#0F172A")
    path = PREV / "occ-ab-sidebyside.png"
    canvas.save(path, format="PNG")
    views.append({"name": "occ-ab-sidebyside.png",
                  "path": str(path.relative_to(SUITE_ROOT)),
                  "source": "occlusion.png + occlusion-alternative.png",
                  "crop": None, "scale": scale,
                  "out_size": [canvas.width, canvas.height],
                  "note": "两版可见画面并排：应看不出任何差异"})

    # 记录视图清单
    (PREV / "views-manifest.json").write_text(json.dumps(
        {"run_id": RUN_ID,
         "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
         "timezone": "Asia/Shanghai (UTC+08:00)",
         "note": "临时自检视图；交付件只有 outputs 下的 3 张最终图",
         "views": views}, ensure_ascii=False, indent=1), encoding="utf-8")

    # 打印交付图尺寸用于记录
    sizes = {n: ihdr((OUT / (n + ".png")).read_bytes())
             for n in ("grid-scene", "occlusion", "occlusion-alternative")}
    print("finals:", sizes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
