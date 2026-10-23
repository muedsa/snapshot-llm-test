"""A20 渲染像素核验：把交付 PNG 的实际像素与 label-layout.json 的几何逐项对上。

动机：审计只能证明「模型自洽」，无法证明「服务真的按模型画出来」。本脚本只读
交付 PNG 的实际像素，逐个点核：
  * 点圆圆心像素是否为点圆颜色（Top-3 为 TOP3 色，其余为 DISC 色）
  * 标签底板内侧像素是否为底板填充色（且与 Top-3 归属一致）
  * 三段引导折线的中段像素是否为引导线颜色
  * 主图框内空白处是否为主图框填充色、画布角落是否为背景色
任一不通过即整体退出码 1；结果写入 tmp/<run>/A20/pixel-verify.json。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A20"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"

BG = (0x0B, 0x12, 0x20)
FRAME_FILL = (0x0F, 0x1B, 0x2D)
DISC = (0x38, 0xBD, 0xF8)
TOP3 = (0xF5, 0x9E, 0x0B)
PLATE = (0x17, 0x26, 0x3B)
PLATE_TOP3 = (0x3A, 0x2A, 0x0E)
LEADER = (0x7C, 0x9B, 0xB8)
TOL = 12          # sRGB 分量容差：抗锯齿边缘与 PNG 编码舍入


def close(p, want) -> bool:
    return all(abs(a - b) <= TOL for a, b in zip(p, want))


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    from PIL import Image

    png_path = OUT / "annotated-map.png"
    body = png_path.read_bytes()
    w, h = struct.unpack(">II", body[16:24])
    img = Image.open(png_path).convert("RGB")
    px = img.load()
    model = json.loads((TMP / "layout_model.json").read_text(encoding="utf-8"))

    def sample(x, y) -> tuple:
        x, y = int(round(x)), int(round(y))
        return px[max(0, min(w - 1, x)), max(0, min(h - 1, y))]

    checks: list[dict] = []
    fails: list[dict] = []

    def rec(tag, x, y, want, tol=TOL):
        got = sample(x, y)
        ok = all(abs(a - b) <= tol for a, b in zip(got, want))
        checks.append({"tag": tag, "sample": [int(x), int(y)],
                       "want": list(want), "got": list(got), "ok": ok})
        if not ok:
            fails.append(checks[-1])

    # 1) 点圆圆心
    for lab in model["labels"]:
        cx, cy = lab["anchor"]["x"], lab["anchor"]["y"]
        want = TOP3 if lab["highlighted"] else DISC
        rec("disc:%s" % lab["id"], cx, cy, want)

    # 2) 标签底板内侧（取右边距 3 px、垂直居中，避开左侧文字墨迹与圆角）
    for lab in model["labels"]:
        b = lab["label_box"]
        bw = b[2] - b[0]
        want = PLATE_TOP3 if lab["highlighted"] else PLATE
        rec("plate:%s" % lab["id"], b[0] + bw - 3, (b[1] + b[3]) / 2.0, want)

    # 3) 引导折线三段（取各段矩形中心）
    for lab in model["labels"]:
        for i, seg in enumerate(lab["leader_segments_rendered"], 1):
            r = seg["rect"]
            rec("leader:%s:seg%d" % (lab["id"], i),
                (r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0, LEADER)

    # 4) 画布与主图框背景
    f = model["frame"]
    rec("bg:corner", 8, 8, BG)
    rec("bg:corner", w - 9, h - 9, BG)
    rec("frame_fill:empty", f["left"] + 6, f["top"] + f["height"] - 30,
        FRAME_FILL)

    # 5) Top-3 归属互斥性：非 Top-3 的点圆不得出现 Top-3 色
    for lab in model["labels"]:
        if lab["highlighted"]:
            continue
        cx, cy = lab["anchor"]["x"], lab["anchor"]["y"]
        got = sample(cx, cy)
        ok = not close(got, TOP3)
        checks.append({"tag": "non_top3_not_amber:%s" % lab["id"],
                       "sample": [int(cx), int(cy)],
                       "got": list(got), "ok": ok})
        if not ok:
            fails.append(checks[-1])

    ok = not fails
    doc = {
        "schema_version": 1, "task_id": "A20", "path_base": "output_dir",
        "run_id": RUN_ID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "purpose": ("把交付 PNG 的实际像素与 label-layout.json 的几何逐项比对，"
                    "证明服务端确实按模型绘制（审计只能证明模型自洽）"),
        "source_png": {"path": "outputs/%s/A20/annotated-map.png" % RUN_ID,
                       "width": w, "height": h},
        "srgb_channel_tolerance": TOL,
        "sampling": {"disc": "圆心像素",
                     "plate": "底板右内 3 px、垂直居中（避开文字墨迹与圆角）",
                     "leader": "各 1 px 段矩形几何中心",
                     "background": "画布角落与主图框内空白处"},
        "check_count": len(checks),
        "fail_count": len(fails),
        "failed": fails,
        "verdict": "通过" if ok else "不通过",
    }
    (TMP / "pixel-verify.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print("checks:", len(checks), "failures:", len(fails),
          "verdict:", doc["verdict"])
    if fails:
        for f_ in fails:
            print("  FAIL", f_)
        return 1
    print("disc/plate/leader/background 像素全部与模型一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
