"""A20 自检视图：为视觉复核生成裁切/缩放视图（临时预览，非交付件）。

TASK.md 要求：必须放大查看指定中心 6 点 M06/M08/M09/M10/M11/M12 及其引导线，
再查看整体。本脚本按实际渲染出的 PNG 生成这些视图，并记录每张视图对应的
原始图裁切框、缩放比与来源哈希，供 layout-audit.json 回填实际查看证据。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A20"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"
PREV = TMP / "preview"

CENTER6 = ["M06", "M08", "M09", "M10", "M11", "M12"]


def ihdr(body: bytes) -> tuple:
    return struct.unpack(">II", body[16:24])


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    from PIL import Image

    PREV.mkdir(parents=True, exist_ok=True)
    png = OUT / "annotated-map.png"
    body = png.read_bytes()
    src_sha = hashlib.sha256(body).hexdigest()
    w, h = ihdr(body)
    model = json.loads((TMP / "layout_model.json").read_text(encoding="utf-8"))
    labs = {l["id"]: l for l in model["labels"]}
    img = Image.open(png)

    views: list[dict] = []

    def make(name, box, scale, note, src_name="annotated-map.png"):
        b = [max(0, int(round(box[0]))), max(0, int(round(box[1]))),
             min(w, int(round(box[2]))), min(h, int(round(box[3])))]
        crop = img.crop(b)
        out = crop.resize((max(1, int(round(crop.width * scale))),
                           max(1, int(round(crop.height * scale)))),
                          Image.NEAREST)
        path = PREV / name
        out.save(path, format="PNG")
        views.append({"name": name,
                      "path": path.relative_to(SUITE_ROOT).as_posix(),
                      "source": {"path": "outputs/%s/A20/%s" % (RUN_ID, src_name),
                                 "sha256": src_sha},
                      "crop": b, "crop_size": [crop.width, crop.height],
                      "scale": scale, "out_size": [out.width, out.height],
                      "resample": "NEAREST（像素放大，不插值，便于核对 1px 描边）",
                      "note": note})
        print("%-26s %4dx%-4d crop=%s x%.1f"
              % (name, out.width, out.height, b, scale))
        return path

    def union(rects):
        x0 = min(r[0] for r in rects)
        y0 = min(r[1] for r in rects)
        x1 = max(r[2] for r in rects)
        y1 = max(r[3] for r in rects)
        return [x0, y0, x1, y1]

    # 1) 指定中心 6 点：各自「圆盘 ∪ 引导折线 ∪ 标签盒」的完整包围盒
    for sid in CENTER6:
        l = labs[sid]
        ax, ay = l["anchor"]["x"], l["anchor"]["y"]
        r = l["disc_diameter"] / 2.0
        rects = [[ax - r, ay - r, ax + r, ay + r], list(l["label_box"])]
        for p in l["leader_polyline"]:
            rects.append([p[0], p[1], p[0], p[1]])
        box = union(rects)
        pad = 14
        box = [box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad]
        scale = 2.0 if (box[2] - box[0]) * 2.5 > 1800 else 2.5
        make("view-%s-local.png" % sid, box, scale,
             "指定中心点 %s（%s，value=%s）：圆盘、三段正交引导线、标签盒整体；"
             "核对连接是否正确、描边是否压字、是否与邻近标签或点重叠"
             % (sid, l["name"], l["value"]))

    # 2) 中心 6 点共处一屏：核对 6 点两两不遮挡、引导线互不交叉
    c = [labs[s] for s in CENTER6]
    box = union([[l["anchor"]["x"] - 8, l["anchor"]["y"] - 8,
                  l["anchor"]["x"] + 8, l["anchor"]["y"] + 8] for l in c])
    box = [box[0] - 26, box[1] - 26, box[2] + 26, box[3] + 26]
    make("view-center6-group.png", box, 3.0,
         "指定中心 6 点（M06/M08/M09/M10/M11/M12）同框：核对点圆互不遮挡、"
         "相邻引导线走向可辨")

    # 3) 左右标签栏各自整体：核对盒间距、行序与折道
    for rail, tag in (("L", "left-rail"), ("R", "right-rail")):
        ids = model[("left_rail" if rail == "L" else "right_rail")]["ids"]
        box = union([labs[s]["label_box"] for s in ids])
        box = [box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10]
        make("view-%s.png" % tag, box, 2.0,
             "%s栏 24 点中的 %d 个标签盒整体：核对盒间距 ≥4 px、字号 ≥20、"
             "行序与锚点 y 一致" % (("左" if rail == "L" else "右"), len(ids)))

    # 4) 整图（原尺寸，供整体查看）与缩略（供快速扫读）
    make("view-whole-1x.png", [0, 0, w, h], 1.0,
         "整图 1:1（%dx%d）：核对坐标轴/范围/单位/前三高亮、主图框完整、"
         "无裁剪与遮挡" % (w, h))
    make("view-whole-05x.png", [0, 0, w, h], 0.5,
         "整图 0.5x 缩略：核对整体布局平衡与左右分栏层级")

    # 5) 底部图例与坐标轴刻度区：核对刻度数字未被引导线压字
    make("view-axis-x.png", [250, 900, 1240, 962], 2.0,
         "x 轴刻度与主图框下沿：核对刻度数字清晰、无引导线经过")
    make("view-axis-y.png", [226, 130, 300, 700], 2.0,
         "y 轴刻度列：核对左栏引导线收尾段与刻度数字之间的净距")
    make("view-legend.png", [280, 958, 1160, 1080], 2.0,
         "底部图例与说明：核对色样与文字说明一一对应、点径说明、单位「指数」、"
         "前三与交叉数声明")

    manifest = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "run_id": RUN_ID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "purpose": "视觉复核用临时预览；不属交付件，不替代真实服务渲染的交付 PNG",
        "source": {"path": "outputs/%s/A20/annotated-map.png" % RUN_ID,
                   "width": w, "height": h, "sha256": src_sha},
        "center6_required": CENTER6,
        "center6_views": [v for v in views if v["name"].startswith("view-M")],
        "whole_image_views": [v["name"] for v in views
                              if v["name"].startswith("view-whole")],
        "views": views,
        "view_count": len(views),
    }
    report = TMP / "views-manifest.json"
    report.write_text(json.dumps(manifest, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print("views:", len(views))
    print("manifest:", report.relative_to(SUITE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
