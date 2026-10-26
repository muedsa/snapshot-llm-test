"""A19 遮挡场景生成器：A/B 两版（隐藏内容不同、可见部分完全相同）。

设计要点：
  - 画布 800x800，背景 #F1F5F9（两版一致）；
  - 遮挡物为轴对齐不透明矩形 [400,220,760,580]，无边框/无阴影/无滤镜/无透明度，
    且矩形边缘无抗锯齿（实测），因此其覆盖区域内像素与下层无关；
  - 隐藏对象全部在矩形内且距边缘 >=22px，其一切绘制影响（含抗锯齿边缘）
    都被矩形完全覆盖；隐藏对象不带 ID 标签（避免泄漏数量）；
  - 可见前景 V01-V06 与标签两版逐字节相同；
  - 两版 DSL 仅"隐藏内容"块不同。
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A19"
OUT = ROOT / "outputs" / RUN_ID / "A19"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

W = H = 800
BG = "#F1F5F9"
OCC_RECT = [400, 220, 760, 580]        # left,top,right,bottom
OCC_FILL = "#0F172A"
FAM = "Noto Sans CJK SC"
ID_INK = "#64748B"

C_BLUE, C_ORANGE, C_GREEN, C_PURPLE = "#2563EB", "#EA580C", "#16A34A", "#9333EA"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def circle(cx, cy, d, color):
    return (f'<Positioned left="{cx - d / 2:.2f}" top="{cy - d / 2:.2f}" width="{d}" height="{d}">'
            f'<Container width="{d}" height="{d}" color="{color}" shape="CIRCLE"/></Positioned>')


def square(cx, cy, s, color):
    return (f'<Positioned left="{cx - s / 2:.2f}" top="{cy - s / 2:.2f}" width="{s}" height="{s}">'
            f'<Container width="{s}" height="{s}" color="{color}"/></Positioned>')


def rrect(cx, cy, s, color, r=12):
    return (f'<Positioned left="{cx - s / 2:.2f}" top="{cy - s / 2:.2f}" width="{s}" height="{s}">'
            f'<Container width="{s}" height="{s}" color="{color}" borderRadius="{r}"/></Positioned>')


def ring(cx, cy, outer, color):
    bw = outer // 4
    return (f'<Positioned left="{cx - outer / 2:.2f}" top="{cy - outer / 2:.2f}" '
            f'width="{outer}" height="{outer}">'
            f'<Container width="{outer}" height="{outer}" color="transparent" '
            f'shape="CIRCLE" border="{bw} SOLID {color}"/></Positioned>')


def label(text, cx, top):
    return (f'<Positioned left="{cx - 32:.2f}" top="{top:.2f}" width="64" height="28">'
            f'<Container color="transparent" alignment="TOP_LEFT">'
            f'<Text fontSize="20" fontFamily="{FAM}" fontStyle="NORMAL" '
            f'color="{ID_INK}" textAlign="LEFT" softWrap="false" maxLines="1">'
            f'{esc(text)}</Text></Container></Positioned>')


# ---------- 可见前景（两版完全一致） ----------
VISIBLE = [
    ("V01", circle(160, 180, 64, C_BLUE), 64, "circle", 160, 180, 64),
    ("V02", square(640, 120, 56, C_ORANGE), 56, "square", 640, 120, 56),
    ("V03", ring(180, 560, 72, C_GREEN), 72, "ring", 180, 560, 72),
    ("V04", rrect(300, 680, 80, C_PURPLE), 80, "rounded-square", 300, 680, 80),
    ("V05", circle(660, 680, 60, C_ORANGE), 60, "circle", 660, 680, 60),
    ("V06", square(120, 380, 48, C_GREEN), 48, "square", 120, 380, 48),
]
VISIBLE_LABELS = [
    ("V01", 160, 180 - 64 / 2 - 30),
    ("V02", 640, 120 - 56 / 2 - 30),
    ("V03", 180, 560 - 72 / 2 - 30),
    ("V04", 300, 680 - 80 / 2 - 30),
    ("V05", 660, 680 - 60 / 2 - 30),
    ("V06", 120, 380 - 48 / 2 - 30),
]

# ---------- 隐藏内容（版本相关；全部在遮挡矩形内） ----------
HIDDEN_A = [
    {"id": "H01", "desc": "橙色圆，中心 (580,400)，直径 80", "node": circle(580, 400, 80, C_ORANGE),
     "shape": "circle", "size": 80, "center": [580, 400], "color": "orange"},
]
HIDDEN_B = [
    {"id": "H01", "desc": "绿色方，中心 (520,320)，边长 48", "node": square(520, 320, 48, C_GREEN),
     "shape": "square", "size": 48, "center": [520, 320], "color": "green"},
    {"id": "H02", "desc": "紫色圆环，中心 (640,470)，外径 64", "node": ring(640, 470, 64, C_PURPLE),
     "shape": "ring", "size": 64, "center": [640, 470], "color": "purple"},
    {"id": "H03", "desc": "蓝色圆，中心 (580,530)，直径 56", "node": circle(580, 530, 56, C_BLUE),
     "shape": "circle", "size": 56, "center": [580, 530], "color": "blue"},
]

OCCLUDER = (f'<Positioned left="{OCC_RECT[0]}" top="{OCC_RECT[1]}" '
            f'width="{OCC_RECT[2] - OCC_RECT[0]}" height="{OCC_RECT[3] - OCC_RECT[1]}">'
            f'<Container width="{OCC_RECT[2] - OCC_RECT[0]}" '
            f'height="{OCC_RECT[3] - OCC_RECT[1]}" color="{OCC_FILL}"/></Positioned>')


def build_dsl(hidden: list[dict], version: str) -> str:
    nodes = []
    nodes.append("<!-- 隐藏内容（被遮挡物完全覆盖；不同版本此处不同） -->")
    for h in hidden:
        nodes.append(h["node"])
    nodes.append("<!-- 可见前景（两版逐字节相同） -->")
    for _, node, *_ in VISIBLE:
        nodes.append(node)
    for vid, cx, top in VISIBLE_LABELS:
        nodes.append(label(vid, cx, top))
    nodes.append("<!-- 遮挡物：不透明轴对齐矩形，无边框/阴影/滤镜 -->")
    nodes.append(OCCLUDER)
    return (f'<Snapshot type="png" background="{BG}">'
            f'<Container width="{W}" height="{H}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + "\n".join(nodes) + "</Stack></Container></Snapshot>")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    log = Log(ROOT, RUN_ID, "A19")
    results = {}

    for version, hidden, name in (("A", HIDDEN_A, "occlusion"),
                                  ("B", HIDDEN_B, "occlusion-alternative")):
        dsl = build_dsl(hidden, version)
        dsl_path = TMP / f"{name}.snapshot"
        dsl_path.write_text(dsl, encoding="utf-8")
        out_png = OUT / f"{name}.png"
        r = render(dsl_path, out_png, ROOT, log, label=f"A19-{name}")
        rec = r["record"]
        print(f"[{version}] {name}: status={rec['status']} http={rec['http_status']} "
              f"request_id={rec.get('request_id')} elapsed={rec.get('elapsed_s')}s")
        if rec["status"] != "ok":
            print(f"[{version}] FAILED:", rec.get("error"))
            sys.exit(1)
        (OUT / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
        results[version] = {"dsl": dsl_path, "png": out_png, "hidden": hidden}

    # ---------- 像素等价比较 ----------
    import PIL
    a_img = Image.open(results["A"]["png"])
    b_img = Image.open(results["B"]["png"])
    cmp_rec = {
        "decoder": f"Pillow {PIL.__version__}（Image.open，默认解码器）",
        "decoder_mode": "RGBA（8 位未预乘；服务返回 RGBA，alpha 通道参与比较，不合成白底、不缩放）",
        "same_size": a_img.size == b_img.size,
        "size_a": list(a_img.size), "size_b": list(b_img.size),
    }
    a_arr = np.asarray(a_img.convert("RGBA"))
    b_arr = np.asarray(b_img.convert("RGBA"))
    same_shape = a_arr.shape == b_arr.shape
    cmp_rec["same_array_shape"] = bool(same_shape)
    diff_mask = np.any(a_arr != b_arr, axis=2)
    diff_px = int(diff_mask.sum())
    if diff_px:
        max_ch = int(np.abs(a_arr.astype(int) - b_arr.astype(int)).max())
        ys, xs = np.nonzero(diff_mask)
        first = [int(xs[k]) for k in range(min(5, len(xs)))] + \
                [int(ys[k]) for k in range(min(5, len(xs)))]
        cmp_rec["diff_examples_xy"] = first
    else:
        max_ch = 0
        cmp_rec["diff_examples_xy"] = []
    cmp_rec["different_pixels"] = diff_px
    cmp_rec["max_channel_diff"] = max_ch
    cmp_rec["array_hash_a"] = hashlib.sha256(a_arr.tobytes()).hexdigest()
    cmp_rec["array_hash_b"] = hashlib.sha256(b_arr.tobytes()).hexdigest()
    cmp_rec["array_hash_equal"] = cmp_rec["array_hash_a"] == cmp_rec["array_hash_b"]
    cmp_rec["verdict"] = ("pixel_equivalent" if (diff_px == 0 and same_shape
                                                 and cmp_rec["array_hash_equal"]
                                                 and cmp_rec["same_size"])
                          else "not_equivalent")
    print(f"[compare] same_size={cmp_rec['same_size']} diff_px={diff_px} "
          f"max_ch={max_ch} array_hash_equal={cmp_rec['array_hash_equal']} "
          f"verdict={cmp_rec['verdict']}")

    # 文件级 SHA-256（留痕用；不同压缩/元数据不据此判等价）
    file_hashes = {v: sha256_file(results[v]["png"]) for v in ("A", "B")}
    print(f"[sha256] A={file_hashes['A'][:16]}... B={file_hashes['B'][:16]}... equal={file_hashes['A']==file_hashes['B']}")

    (TMP / "occ-compare.json").write_text(
        json.dumps({"comparison": cmp_rec, "file_sha256": file_hashes}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("[done] occlusion A/B rendered and compared")


if __name__ == "__main__":
    main()
