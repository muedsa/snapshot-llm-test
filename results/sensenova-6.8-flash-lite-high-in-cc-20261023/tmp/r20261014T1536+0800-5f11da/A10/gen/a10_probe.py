"""A10 探针：一次渲染六格，量取 Opacity / BackdropFilter / ImageFiltered /
ColorFiltered / ClipOval 的真实语义，并从返回 PNG 直接采样 ①② 的重叠内部像素。

探针画布 996×508，布局与正式板的相对关系一致（3 列 × 2 行，格距 8），
采样像素坐标 = 区域原点 + 局部 (180,100)，0-indexed，未预乘 8 位 RGBA。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/A10/gen/a10_probe.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]                       # 仓库根（tools/ 所在）
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))

import a10_client as CL                     # noqa: E402
import a10_scenes as C                      # noqa: E402
import suite as S                           # noqa: E402
from PIL import Image                       # noqa: E402

OX, OY, GAP = 10.0, 10.0, 8.0
W = int(OX * 2 + 3 * C.AREA_W + 2 * GAP)
H = int(OY * 2 + 2 * C.AREA_H + GAP)
PURPOSE = ("量取 Opacity 是否把子树压平、BackdropFilter 是否只模糊背景、"
           "ImageFiltered/ColorFiltered 作用范围、ClipOval 裁剪形状，"
           "并采样 ①② 的重叠内部像素")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tmp_dir = S.task_dirs("A10")[1]
    (tmp_dir / "preview").mkdir(parents=True, exist_ok=True)

    origins = C.area_origins(OX, OY, GAP)
    dsl = ('<Snapshot type="png" background="#F1F5F9">'
           '<Container width="' + C.n(W) + '" height="' + C.n(H) + '">'
           + C.stack(C.all_areas(OX, OY, GAP))
           + "</Container></Snapshot>")

    res = CL.render("A10", dsl, "probe1-compositing", kind="probe",
                    purpose=PURPOSE, dsl_name="probe1-compositing.snapshot")
    print("request", res["request_id"], "status", res["status"])

    if res["status"] != 200 or not res["body"]:
        print(S.error_summary(res["status"] or 0, res["body"] or b""))
        return 1

    png = tmp_dir / "preview" / "probe1-compositing.png"
    png.write_bytes(res["body"])

    im = Image.open(png).convert("RGBA")
    print("decoded size", im.size)
    assert im.size == (W, H), (im.size, W, H)

    samples = {}
    for idx in (0, 1):
        ox, oy = origins[idx]
        px, py = ox + int(C.SAMPLE[0]), oy + int(C.SAMPLE[1])
        samples["area%d" % (idx + 1)] = {
            "area_origin_canvas": [ox, oy],
            "sample_local": [C.SAMPLE[0], C.SAMPLE[1]],
            "sample_canvas_pixel_0indexed": [px, py],
            "rgba_unpremultiplied": list(im.getpixel((px, py))),
        }
    extra = {
        "area0_bg_local_5_5": list(im.getpixel((origins[0][0] + 5, origins[0][1] + 5))),
        "area0_red_only_local_60_60":
            list(im.getpixel((origins[0][0] + 60, origins[0][1] + 60))),
        "area0_blue_only_local_240_180":
            list(im.getpixel((origins[0][0] + 240, origins[0][1] + 180))),
        "area1_red_only_local_60_60":
            list(im.getpixel((origins[1][0] + 60, origins[1][1] + 60))),
        "area1_blue_only_local_240_180":
            list(im.getpixel((origins[1][0] + 240, origins[1][1] + 180))),
        "area3_outside_circle_local_10_10":
            list(im.getpixel((origins[3][0] + 10, origins[3][1] + 10))),
        "area5_outside_circle_local_10_10":
            list(im.getpixel((origins[5][0] + 10, origins[5][1] + 10))),
        "area5_inside_circle_local_160_120":
            list(im.getpixel((origins[5][0] + 160, origins[5][1] + 120))),
        "area6_inside_circle_local_160_120":
            list(im.getpixel((origins[5][0] + 160, origins[5][1] + 120))),
    }
    out = {"probe": "a10-probe1", "request_id": res["request_id"],
           "canvas": [W, H], "areas": [{"index": i + 1, "origin": list(o)}
                                       for i, o in enumerate(origins)],
           "samples": samples, "extra": extra}
    (tmp_dir / "probe1-result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
