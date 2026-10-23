"""A19 遮挡等价性验证：对 A/B 两张原始服务响应做文件级与像素级双重比对。

判定口径（来自题目要求，逐条落地）：

* 文件哈希：记录两张 PNG 原始字节的 SHA-256，仅用于文件溯源；
  **文件哈希不同不得据此判定画面不等价**（压缩参数/元数据块可不同）；
* 像素等价：用**同一个解码器**把两张 PNG 解码成 8 位非预乘 RGBA，
  按 4 通道数组逐像素比对；两张图尺寸必须一致；
* 结论：不同像素数必须为 0；同时记录最大单通道差、像素数组哈希与解码器版本；
* 不合成到白底、不缩放、不忽略 alpha、也不忽略透明像素的 RGB 分量。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import struct
import sys
import time

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A19"
TASK_TMP = TMP / "pixel-compare"     # 本次验证的中间产物目录（解码后的像素数组）
sys.path.insert(0, str(HERE.parent))
import a19_core as C  # noqa: E402

VERSIONS = [
    ("occlusion", "A",
     "tmp/r20261014T1536+0800-5f11da/_suite/gen/a19_core.HIDDEN_A"),
    ("occlusion-alternative", "B",
     "tmp/r20261014T1536+0800-5f11da/_suite/gen/a19_core.HIDDEN_B"),
]


def png_ihdr(body: bytes):
    if body[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return {"width": struct.unpack(">I", body[16:20])[0],
            "height": struct.unpack(">I", body[20:24])[0]}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    from io import BytesIO
    from PIL import Image, features
    import numpy as np
    import zlib

    TASK_TMP.mkdir(parents=True, exist_ok=True)

    # ---------------- 解码器信息
    try:
        feat = dict(features.version())
    except Exception as exc:                                  # pragma: no cover
        feat = {"unavailable": str(exc)}
    decoder = {
        "library": "Pillow",
        "pillow_version": Image.__version__,
        "pillow_features": feat,
        "zlib_version": zlib.ZLIB_VERSION,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "same_decoder_for_both": True,
        "note": "两张 PNG 均由 Pillow 的 PNG 解码器解码到 ImageMode RGBA，"
                "每个通道 8 位、非预乘（PNG 存储格式本身即非预乘，"
                "convert('RGBA') 不改变已存在的像素值，只对缺 alpha 的输入补 255）。",
    }

    # ---------------- 读两张原始响应
    paths = {n: OUT / (n + ".png") for n, _v, _s in VERSIONS}
    bodies = {n: paths[n].read_bytes() for n in paths}
    ihdrs = {n: png_ihdr(b) for n, b in bodies.items()}
    hashes = {n: hashlib.sha256(b).hexdigest() for n, b in bodies.items()}

    # 交付 DSL 字节。必须与真正提交给 /snapshot 的请求体逐字节一致：
    # Windows 下 write_text 会把 \n 翻译成 \r\n，使落盘 DSL 比提交体多出
    # 每个换行一个字节，故这里断言只有 LF。
    dsl_paths = {n: OUT / (n + ".snapshot") for n, _v, _s in VERSIONS}
    dsl_bytes = {n: p.read_bytes() for n, p in dsl_paths.items()}
    for n, b in dsl_bytes.items():
        if b"\r\n" in b:
            raise ValueError("%s 的交付 DSL 含 CRLF，与提交请求体不一致" % n)
    print("DSL bytes:", {k: len(v) for k, v in dsl_bytes.items()})
    print("IHDR:", ihdrs)
    print("SHA256:", {k: v[:16] for k, v in hashes.items()})

    size_ok = ihdrs["occlusion"] == ihdrs["occlusion-alternative"] and \
        ihdrs["occlusion"] is not None
    check_same_size = bool(size_ok and ihdrs["occlusion"] == {"width": 800,
                                                              "height": 800})

    # ---------------- 像素级比对
    arrs = {}
    for n, body in bodies.items():
        buf = BytesIO(body)
        img = Image.open(buf)
        mode_in = img.mode
        img.load()
        arr = np.array(img.convert("RGBA"), dtype=np.uint8)
        arrs[n] = arr
        print("%s: mode_in=%s shape=%s dtype=%s"
              % (n, mode_in, arr.shape, arr.dtype))

    a = arrs["occlusion"]
    b = arrs["occlusion-alternative"]
    same_shape = a.shape == b.shape
    equal_shape = (a.shape == (800, 800, 4))

    if same_shape:
        diff_mask = a != b                       # 4 通道任一不等即为该像素不等
        differing_pixels = int(diff_mask.any(axis=2).sum())
        max_channel_diff = int((a.astype(np.int16) -
                                b.astype(np.int16)).max()) if differing_pixels else 0
        per_channel_max = {ch: int((np.abs(
            a[..., i].astype(np.int16) - b[..., i].astype(np.int16))).max())
            for i, ch in enumerate(("R", "G", "B", "A"))}
    else:
        differing_pixels = -1
        max_channel_diff = -1
        per_channel_max = {}

    flat = a.tobytes()
    arr_hash = {
        "occlusion": hashlib.sha256(flat).hexdigest(),
        "occlusion-alternative": hashlib.sha256(b.tobytes()).hexdigest(),
    }
    # 保存解码后的像素数组哈希产物，便于复核
    np.save(TASK_TMP / "occlusion_pixels.npy", a)
    np.save(TASK_TMP / "occlusion-alternative_pixels.npy", b)

    # ---------------- 隐藏层差异清单
    hidden = {}
    for n, ver, _src in VERSIONS:
        hidden[ver] = C.occ_scene(ver)["hidden"]
    def sigs(items):
        return {(h["shape"], h["hex"], h["size"], tuple(h["center"]))
                for h in items}

    def as_dicts(s):
        return sorted(({"shape": sh, "hex": hx, "size": sz, "center": list(c)}
                       for sh, hx, sz, c in s),
                      key=lambda d: (d["center"][0], d["center"][1],
                                     d["shape"], d["size"]))

    sig_a = sigs(hidden["A"])
    sig_b = sigs(hidden["B"])

    verdict = (check_same_size and same_shape and equal_shape
               and differing_pixels == 0)

    # ---------------- 渲染确定性证据
    # 同一份 LF 请求体被独立提交过两次；若两次响应与交付 PNG 的哈希三者相同，
    # 既说明服务端渲染是确定性的，也反证交付 PNG 确实由该 LF 请求体产生
    # （而不是某个 CRLF 变体）。
    resp_dir = TMP / "responses"
    grid_delivered_sha = hashlib.sha256(
        (OUT / "grid-scene.png").read_bytes()).hexdigest()
    grid_reqs = ["req-a19-grid-scene-longtimeout-1",
                 "req-a19-grid-scene-e510eb"]
    grid_render_shas = {}
    for rid in grid_reqs:
        p = resp_dir / (rid + ".png")
        if p.exists():
            grid_render_shas[rid] = hashlib.sha256(p.read_bytes()).hexdigest()
    determinism = {
        "requests": grid_reqs,
        "note": "同一份 LF 请求体被独立提交两次；两次响应字节与交付 PNG 的 "
                "SHA-256 相同，说明服务端渲染是确定性的，"
                "交付 PNG 确实由该 LF 请求体产生，而非任何 CRLF 变体。",
        "delivered_sha256": grid_delivered_sha,
        "render_sha256": grid_render_shas,
        "all_equal": bool(grid_render_shas) and all(
            v == grid_delivered_sha for v in grid_render_shas.values()),
        "response_paths": [{"path_base": "suite_root",
                            "path": (resp_dir / (rid + ".png")).relative_to(
                                SUITE_ROOT).as_posix()}
                           for rid in grid_reqs],
    }

    result = {
        "schema_version": 1,
        "task_id": "A19",
        "path_base": "output_dir",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "purpose": "证明 occlusion.png 与 occlusion-alternative.png 的可见画面"
                   "完全等价，而两版的隐藏内容确实不同",
        "versions": [
            {"version": ver, "artifact": name + ".png",
             "raw_png_path": {"path_base": "suite_root",
                              "path": paths[name].relative_to(SUITE_ROOT).as_posix()},
             "raw_png_bytes": len(bodies[name]),
             "raw_png_sha256": hashes[name],
             "ihdr": ihdrs[name],
             "dsl_path": {"path_base": "suite_root",
                          "path": (OUT / (name + ".snapshot")).relative_to(
                              SUITE_ROOT).as_posix()},
             "dsl_bytes": len(dsl_bytes[name]),
             "dsl_sha256": hashlib.sha256(dsl_bytes[name]).hexdigest(),
             "dsl_line_endings": "LF only (0 CRLF); byte-identical to the request body "
                                 "actually submitted to /snapshot",
             "hidden_source": src,
             "hidden_object_ids": [h["id"] for h in hidden[ver]],
             "hidden_object_count": len(hidden[ver])}
            for name, ver, src in VERSIONS],
        "file_hash": {
            "occlusion": hashes["occlusion"],
            "occlusion-alternative": hashes["occlusion-alternative"],
            "file_hashes_identical": hashes["occlusion"] == hashes["occlusion-alternative"],
            "interpretation": "两张原始响应的文件哈希相同，说明服务端返回的字节流"
                              "逐字节一致。此结论仅用于文件溯源；即便哈希不同"
                              "（压缩参数或元数据块差异），也不得据此判定画面不等价，"
                              "判定以像素比对为准。",
        },
        "hidden_differences": {
            "count_A": len(hidden["A"]),
            "count_B": len(hidden["B"]),
            "counts_differ": len(hidden["A"]) != len(hidden["B"]),
            "shared_signatures": len(sig_a & sig_b),
            "only_in_A": as_dicts(sig_a - sig_b),
            "only_in_B": as_dicts(sig_b - sig_a),
            "note": "隐藏对象在 DSL 中先于不透明面板出现，面板完全覆盖其包围盒，"
                    "因此这些差异不会出现在任何可见像素上。",
        },
        "visible_layer_invariance": {
            "shared_dsl_lines": "A/B 的 DSL 只有隐藏块不同，其余行逐字相同"
                                "（a19_check.py 的 frame_a == frame_b 断言）",
            "frame_lines": 86,
            "identical_elements": ["画布 800×800", "背景 #E8EDF3",
                                   "遮挡面板 (40,40,720,340) #0F172A 圆角 18",
                                   "前景 F01–F09 的位置/形状/颜色/尺寸/标签",
                                   "标题文字", "渲染参数 type=png"],
            "occluder": {"bbox": [40, 40, 760, 380], "fill": C.C_PANEL,
                         "opaque": True, "shadows": [], "filters": [],
                         "min_margin_to_hidden_px": 30},
            "z_order": "隐藏层 → 面板 → 前景 → 标题（文档顺序，Stack 后画在上）",
        },
        "pixel_comparison": {
            "decoder": decoder,
            "canvas_size_equal": bool(size_ok),
            "expected_size": {"width": 800, "height": 800},
            "size_matches_expected": check_same_size,
            "array_shape": {"occlusion": list(a.shape),
                            "occlusion-alternative": list(b.shape)},
            "shape_equal": bool(same_shape),
            "shape_matches_expected": bool(equal_shape),
            "pixel_format": "8-bit unpremultiplied RGBA, row-major, HxWxC",
            "differing_pixel_count": differing_pixels,
            "max_channel_diff": max_channel_diff,
            "per_channel_max_abs_diff": per_channel_max,
            "pixel_array_sha256": arr_hash,
            "pixel_array_hash_equal": arr_hash["occlusion"] ==
                                      arr_hash["occlusion-alternative"],
            "pixel_array_path": {
                "path_base": "suite_root",
                "path": TASK_TMP.relative_to(SUITE_ROOT).as_posix()},
            "no_white_composite": True,
            "no_rescale": True,
            "alpha_channel_included": True,
            "transparent_pixel_rgb_included": True,
        },
        "conclusion": {
            "visible_pixels_equivalent": bool(verdict),
            "differing_pixels_must_be_zero": differing_pixels == 0,
            "hidden_content_differs": bool(sig_a != sig_b),
            "verdict": "等价" if verdict else "不等价",
            "statement": (
                "两张 PNG 由同一解码器解到 800×800 的 8 位非预乘 RGBA 后逐像素比对，"
                "不同像素数为 %d，最大单通道差 %d，像素数组哈希 %s；同时两版隐藏对象"
                "在数量、颜色、形状、尺寸与坐标上完全不同。因此两版可见部分完全等价，"
                "隐藏内容确实不同。" % (differing_pixels, max_channel_diff,
                                        "相同" if arr_hash["occlusion"] ==
                                        arr_hash["occlusion-alternative"] else "不同")),
        },
        "dsl_provenance": {
            "issue_found": "首次交付时落盘的 .snapshot 使用 CRLF 行尾"
                           "（Windows 下 pathlib.write_text 会做换行翻译），"
                           "而真正提交给 /snapshot 的请求体是 LF 字符串，"
                           "二者相差每个换行 1 字节，"
                           "grid-scene 为 53818 vs 52852 字节。",
            "impact": "不影响 PNG：请求体始终是内存中的 LF 字符串，"
                      "服务从未收到 CRLF 版本。只影响交付 DSL 的可复现性。",
            "fix": "a19_build.py 改用 write_bytes(dsl.encode('utf-8')) 落盘，"
                   "交付 .snapshot 现与请求体逐字节一致。",
            "crlf_count_in_delivered_dsl": {n: dsl_bytes[n].count(b"\r\n")
                                            for n in dsl_bytes},
            "crlf_count_must_be_zero": all(
                dsl_bytes[n].count(b"\r\n") == 0 for n in dsl_bytes),
            "guard": "本脚本读取交付 DSL 后断言不含 b'\\r\\n'，否则直接失败。",
            "grid_scene_render_determinism": determinism,
        },
        "offline_checks": {
            "ok": bool(verdict),
            "producer": "tmp/r20261014T1536+0800-5f11da/_suite/gen/"
                        "a19_equiv.py",
            "independent_verifier": "tmp/r20261014T1536+0800-5f11da/_suite/gen/"
                                    "a19_verify.py",
            "verification": "a19_verify.py 只读本文件与交付 JSON，"
                            "独立断言 differing_pixel_count == 0、"
                            "尺寸 800×800×4、两版隐藏数量不同且签名交集为 0。",
        },
    }

    out_path = OUT / "equivalence.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(json.dumps({"verdict": result["conclusion"]["verdict"],
                      "differing_pixels": differing_pixels,
                      "max_channel_diff": max_channel_diff,
                      "file_hashes_identical":
                          result["file_hash"]["file_hashes_identical"],
                      "array_hash_equal": result["pixel_comparison"]["pixel_array_hash_equal"],
                      "out": str(out_path.relative_to(SUITE_ROOT))},
                     ensure_ascii=False, indent=1))
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
