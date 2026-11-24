#!/usr/bin/env python3
"""A13 brand-system generator and evidence-driven deferred execution CLI.

Offline `prepare` is the default. Later workflow: begin A11/A12/A13 in suite
order, render two transparent previews, actually Read both, review/select one,
render finals, Read all finals, create 32px previews, Read the native-size
comparison, then finalize. No review is inferred or pre-filled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s
from PIL import Image, ImageChops, ImageDraw, __version__ as PIL_VERSION

RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A13"
OUT, TEMP = s.task_dirs(RUN, TASK)
FONT = "Noto Sans CJK SC"
assert FONT in (ROOT / "tmp" / RUN / "_suite/shared/fonts.txt").read_text(encoding="utf-8").splitlines()
PALETTE = {"indigo": "#3049A8", "teal": "#18A999", "amber": "#F2B84B", "paper": "#F5F7FC", "ink": "#172033", "white": "#FFFFFF", "black": "#000000", "muted": "#59677D", "line": "#D7DFEA"}
FINAL_SIZES = {"symbol-color": (512, 512), "symbol-black": (512, 512), "brand-banner": (1200, 400), "launch-poster": (1080, 1350)}
PREVIEWS = ("preview-diagonal", "preview-concentric")


def txt(value, size, color=PALETTE["ink"], bold=False, align="LEFT"):
    assert "]]>" not in value
    return (f'<Text fontFamily="{FONT}" fontSize="{size:g}" color="{color}" textAlign="{align}" '
            f'fontStyle="{"BOLD" if bold else "NORMAL"}" softWrap="true" height="1.2"><Raw><![CDATA[{value}]]></Raw></Text>')


def label(value, x, y, w, h, size, color=PALETTE["ink"], bold=False, align="LEFT"):
    return s.positioned(x, y, w, h, txt(value, size, color, bold, align))


def rounded_ring_path(size, inset):
    def contour(q):
        r = q * .22
        return (f"M {r:g} 0 H {q-r:g} Q {q:g} 0 {q:g} {r:g} V {q-r:g} "
                f"Q {q:g} {q:g} {q-r:g} {q:g} H {r:g} Q 0 {q:g} 0 {q-r:g} "
                f"V {r:g} Q 0 0 {r:g} 0 Z")
    return contour(size) + " " + contour(size - 2 * inset)


def ring(size, x, y, color):
    inset = size * .09
    path = rounded_ring_path(size, inset)
    child = (f'<ClipPath path="{path}" viewBox="0 0 {size:g} {size:g}" fit="FILL" '
             f'fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS"><Container width="{size:g}" height="{size:g}" color="{color}" /></ClipPath>')
    return s.positioned(x, y, size, size, child)


def geometry(direction="concentric", black=False):
    colors = [PALETTE["black"]] * 3 if black else [PALETTE["indigo"], PALETTE["teal"], PALETTE["amber"]]
    if direction == "concentric":
        params = [(340, 86, 86), (240, 136, 136), (140, 186, 186)]
    elif direction == "diagonal":
        params = [(300, 106, 106), (252, 136, 136), (204, 166, 166)]
    else:
        raise AssertionError(direction)
    return [ring(size, x, y, color) for (size, x, y), color in zip(params, colors)], params


def symbol(direction="concentric", black=False):
    nodes, _ = geometry(direction, black)
    return s.snapshot(512, 512, nodes, "transparent")


def preview_a():
    return symbol("diagonal")


def preview_b():
    return symbol("concentric")


def app_icon(x, y, size, direction="concentric", black=False):
    # Regenerate every ring at application scale from shared geometry rules;
    # no rendered symbol PNG or Image element is embedded.
    _, params = geometry(direction, black)
    scale = size / 512
    colors = [PALETTE["black"]] * 3 if black else [PALETTE["indigo"], PALETTE["teal"], PALETTE["amber"]]
    nodes = [ring(base_size * scale, bx * scale, by * scale, color)
             for (base_size, bx, by), color in zip(params, colors)]
    return s.positioned(x, y, size, size, f'<Stack clipBehavior="NONE">{"".join(nodes)}</Stack>')


def banner(direction="concentric"):
    children = [s.box(0, 0, 1200, 400, PALETTE["paper"]), s.box(0, 0, 18, 400, PALETTE["indigo"]),
                app_icon(72, 80, 240, direction), label("叠光 Layerlight", 368, 92, 740, 72, 52, PALETTE["ink"], True),
                label("把复杂信息，组织成清晰画面", 368, 188, 740, 64, 34, PALETTE["muted"]),
                s.line(368, 294, 1080, 294, PALETTE["line"], 2),
                label("STRUCTURED VISUAL TOOLS", 368, 316, 712, 32, 20, PALETTE["indigo"], True)]
    return s.snapshot(1200, 400, children, PALETTE["paper"])


def poster(direction="concentric"):
    children = [s.box(0, 0, 1080, 1350, PALETTE["indigo"]), s.box(0, 0, 20, 1350, PALETTE["teal"]),
                s.box(648, 0, 432, 1350, "#263B87"),
                app_icon(704, 154, 280, direction), label("叠光 Layerlight", 72, 116, 540, 76, 48, PALETTE["white"], True),
                label("把复杂信息，组织成清晰画面", 72, 236, 540, 156, 36, PALETTE["white"], True),
                label("信息在叠加中保持清晰。", 72, 432, 520, 60, 28, "#D9E2FF"),
                s.line(72, 548, 600, 548, "#7182C6", 2),
                label("2026.11.07 · ONLINE", 72, 602, 540, 58, 34, PALETTE["white"], True),
                s.box(72, 716, 292, 76, PALETTE["amber"], 14),
                label("OPEN BETA", 94, 733, 248, 42, 28, PALETTE["ink"], True),
                label("layerlight.example.org", 72, 1178, 936, 50, 28, PALETTE["white"], True),
                label("LAYER BY LAYER · CLARITY BY DESIGN", 72, 1250, 936, 32, 20, "#D9E2FF", True)]
    return s.snapshot(1080, 1350, children, PALETTE["indigo"])


def build_finals(direction="concentric"):
    return {"symbol-color": symbol(direction, False), "symbol-black": symbol(direction, True),
            "brand-banner": banner(direction), "launch-poster": poster(direction)}


def validate_dsls():
    for name, dsl in [("preview-diagonal", preview_a()), ("preview-concentric", preview_b()),
                      *build_finals("diagonal").items(), *build_finals("concentric").items()]:
        root = ET.fromstring(dsl)
        assert root.tag == "Snapshot" and not any(e.tag == "Image" for e in root.iter())
    assert preview_a() != preview_b()
    for direction in ("diagonal", "concentric"):
        color_dsl, black_dsl = symbol(direction, False), symbol(direction, True)
        for color in (PALETTE["indigo"], PALETTE["teal"], PALETTE["amber"]):
            color_dsl = color_dsl.replace(f'color="{color}"', 'color="#000000"')
        assert color_dsl == black_dsl


def guard_execution():
    state = json.loads((ROOT / s.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [x["id"] for x in s.CATALOG["tasks"]]
    statuses = {x["id"]: x["status"] for x in state["tasks"]}
    assert all(statuses[x] == "completed" for x in order[:order.index(TASK)]), "strict task order: earlier tasks are incomplete"
    assert statuses[TASK] == "in_progress", "A13 must already be begun by the suite executor"


def load_json(name, default=None):
    p = TEMP / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def active_version():
    return (load_json("active-version.json") or {}).get("version")


def render_previews(version):
    guard_execution()
    for stem, dsl in zip(PREVIEWS, (preview_a(), preview_b())):
        image, record = s.render(RUN, TASK, dsl, stem, version, final=False, kind="alternative")
        with Image.open(image) as im: assert im.size == (512, 512) and im.format == "PNG"
        print(stem, s.rel(image), record["http_status"])
    s.write_json(TEMP / "active-version.json", {"task_id": TASK, "version": version, "stage": "previews", "rendered_at": s.iso()})


def reviews(version, accepted_only=True):
    values = [x for x in s.read_jsonl(TEMP / "reviews.jsonl") if x["version"] == version and (x["accepted"] or not accepted_only)]
    return {x["stem"]: x for x in values if x["accepted"] or not accepted_only}


def select(direction, version, observed):
    assert direction in ("concentric", "diagonal")
    current = reviews(version)
    assert set(PREVIEWS) <= set(current), "actually Read and accept both geometric-direction previews before selecting"
    s.write_json(TEMP / "selection.json", {"direction": direction, "preview_version": version, "selected_at": s.iso(),
                "basis": observed, "evidence": [current[x]["image_path"] for x in PREVIEWS]})


def render_finals(version):
    guard_execution(); selection = load_json("selection.json"); assert selection, "select a preview direction first"
    assert set(PREVIEWS) <= set(reviews(selection["preview_version"])), "both previews need accepted Read reviews"
    # Both directions remain valid refinements; selection is based on the two
    # actual preview reviews, not hardcoded before they are viewed.
    for stem, dsl in build_finals(selection["direction"]).items():
        image, record = s.render(RUN, TASK, dsl, stem, version, final=True, kind="baseline")
        with Image.open(image) as im: assert im.size == FINAL_SIZES[stem] and im.format == "PNG"
        print(stem, s.rel(image), record["http_status"])
    s.write_json(TEMP / "active-version.json", {"task_id": TASK, "version": version, "stage": "finals", "rendered_at": s.iso()})


def resolve_image(value):
    p = Path(value); p = (p if p.is_absolute() else ROOT / p).resolve()
    assert p.is_file() and TEMP.resolve() in p.parents
    return p


def review(stem, version, image, kind, observed, changes, compared, accept):
    p = resolve_image(image)
    s.record_iteration(RUN, TASK, version, p, kind, observed, changes, compared, completed=accept)
    s.append_jsonl(TEMP / "reviews.jsonl", dict(stem=stem, version=version, image_path=s.rel(p), kind=kind,
                    observed=observed, changes=changes, compared=compared, accepted=accept, recorded_at=s.iso(), viewer="Read"))


def decode_rgba(path):
    with Image.open(path) as im:
        im.load()
        original_mode = im.mode
        rgba = im.convert("RGBA")
        assert original_mode in ("RGBA", "LA", "P", "RGB"), f"unexpected source mode {original_mode}"
        return rgba, original_mode


def black_check(path):
    im, mode = decode_rgba(path)
    pixels = list(im.getdata())
    visible = [p for p in pixels if p[3] > 0]
    violations = sum(1 for p in visible if p[:3] != (0, 0, 0))
    alphas = [p[3] for p in pixels]
    return {"decoder": f"Pillow {PIL_VERSION} Image.open().convert('RGBA'); 8-bit unpremultiplied RGBA",
            "source_mode": mode, "size_px": list(im.size), "checked_pixels": len(pixels), "visible_pixels": len(visible),
            "alpha_min": min(alphas), "alpha_max": max(alphas), "alpha_zero_pixels": sum(a == 0 for a in alphas),
            "nonzero_rgb_where_alpha_positive": violations, "passed": violations == 0 and bool(visible),
            "method": "every decoded pixel with alpha>0 must have R=G=B=0; alpha=0 RGB ignored"}


def premultiplied_lanczos(im, size=(32, 32)):
    """Resample RGB in premultiplied space, then restore unpremultiplied RGBA."""
    w, h = im.size
    data = list(im.convert("RGBA").getdata())
    channels = []
    for channel in range(4):
        plane = Image.new("F", (w, h))
        values = []
        for r, g, b, a in data:
            alpha = a / 255.0
            values.append((r / 255.0 * alpha) if channel < 3 else alpha)
        plane.putdata(values)
        channels.append(plane.resize(size, Image.Resampling.LANCZOS))
    out = Image.new("RGBA", size)
    restored = []
    for y in range(size[1]):
        for x in range(size[0]):
            a = max(0.0, min(1.0, channels[3].getpixel((x, y))))
            rgb = []
            for channel in range(3):
                premul = channels[channel].getpixel((x, y))
                value = 0.0 if a <= 1e-12 else max(0.0, min(1.0, premul / a))
                rgb.append(int(round(value * 255)))
            restored.append((*rgb, int(round(a * 255))))
    out.putdata(restored)
    return out


def thumbnails(version):
    assert active_version() == version and load_json("active-version.json")["stage"] == "finals"
    color, _ = decode_rgba(OUT / "symbol-color.png")
    black, _ = decode_rgba(OUT / "symbol-black.png")
    assert color.size == black.size == (512, 512)
    assert ImageChops.difference(color.getchannel("A"), black.getchannel("A")).getbbox() is None, "color/black alpha geometry differs"
    check = black_check(OUT / "symbol-black.png"); assert check["passed"], check
    directory = TEMP / "small-size" / f"{version}-{s.now().strftime('%Y%m%dT%H%M%S%f')}"
    directory.mkdir(parents=True, exist_ok=False)
    paths = {}
    for stem, im in (("symbol-color", color), ("symbol-black", black)):
        small = premultiplied_lanczos(im)
        p32 = directory / f"{stem}-32.png"; small.save(p32)
        p8 = directory / f"{stem}-32-nearest-8x.png"; small.resize((256, 256), Image.Resampling.NEAREST).save(p8)
        paths[stem] = {"preview_32": s.rel(p32), "supplementary_8x": s.rel(p8)}
    native = Image.new("RGBA", (384, 112), PALETTE["paper"])
    draw = ImageDraw.Draw(native)
    native.alpha_composite(premultiplied_lanczos(color), (32, 40))
    native.alpha_composite(premultiplied_lanczos(black), (208, 40))
    draw.text((32, 16), "COLOR · native 32×32", fill=PALETTE["ink"])
    draw.text((208, 16), "BLACK · native 32×32", fill=PALETTE["ink"])
    native_path = directory / "small-size-native.png"; native.save(native_path)
    meta = {"version": version, "tool": f"Pillow {PIL_VERSION}", "algorithm": "premultiply RGBA float; resize each premultiplied channel with LANCZOS to 32x32; divide RGB by resampled alpha; round to 8-bit; alpha=0 RGB ignored",
            "parameters": {"source": "service PNG decoded to unpremultiplied RGBA", "target_px": [32, 32], "filter": "LANCZOS", "background_for_native_review": PALETTE["paper"], "supplementary_scale": "8x nearest neighbor only; not used instead of native review"},
            "paths": paths, "native_comparison": s.rel(native_path), "black_check": check,
            "alpha_mask_sha256": hashlib.sha256(color.getchannel("A").tobytes()).hexdigest(),
            "geometry_equal": True, "created_at": s.iso()}
    s.write_json(directory / "thumbnail-metadata.json", meta)
    s.write_json(TEMP / "active-thumbnails.json", {"version": version, "directory": s.rel(directory), "metadata": s.rel(directory / "thumbnail-metadata.json")})
    print(json.dumps(meta, ensure_ascii=False, indent=2))


def finalize():
    guard_execution(); version = active_version(); assert version
    current = reviews(version)
    required = set(FINAL_SIZES) | {"small-size-native"}
    assert required <= set(current), "all four finals and the native 32px comparison need accepted Read reviews"
    thumb = load_json("active-thumbnails.json"); assert thumb and thumb["version"] == version
    meta = json.loads((ROOT / thumb["metadata"]).read_text(encoding="utf-8"))
    black = black_check(OUT / "symbol-black.png"); assert black["passed"]
    color, _ = decode_rgba(OUT / "symbol-color.png"); black_im, _ = decode_rgba(OUT / "symbol-black.png")
    assert ImageChops.difference(color.getchannel("A"), black_im.getchannel("A")).getbbox() is None
    for stem in FINAL_SIZES:
        source = resolve_image(current[stem]["image_path"]); final = OUT / f"{stem}.png"
        assert final.read_bytes() == source.read_bytes()
        with Image.open(final) as im: assert im.size == FINAL_SIZES[stem] and im.format == "PNG"
    validate_dsls()
    selection = load_json("selection.json"); assert selection
    direction = selection["direction"]
    relationship = ("three concentric rounded-square rings, common center (256,256)" if direction == "concentric"
                    else "three rounded-square rings offset diagonally by 30px per layer")
    clear_space = min(min(x, y, 512 - x - size, 512 - y - size) for size, x, y in geometry(direction)[1])
    components = []
    _, params = geometry(direction)
    for i, ((size, x, y), color_name) in enumerate(zip(params, ("indigo", "teal", "amber")), 1):
        components.append({"id": f"L{i}", "mother_form": "rounded-square ring", "instance": i,
                           "parameters_px": {"size": size, "position": [x, y], "inset": size * .09, "corner_radius": size * .1804, "fill": PALETTE[color_name]},
                           "dsl_positioning": f"Positioned left={x} top={y} width={size} height={size}; ClipPath EVEN_ODD outer contour minus equal-direction inner contour",
                           "combination_and_negative_space": f"three independent {direction} rounded-square ring instances; each inner contour is a transparent hole; no clipped fragments",
                           "counting_rationale": "one independently recognizable mother-form instance; path/container wrappers do not add instances"})
    applications = [{"file": "symbol-color.png", "size_px": [512, 512], "icon_mapping": {"position": [0, 0], "size": 512, "scale": 1}},
                    {"file": "symbol-black.png", "size_px": [512, 512], "icon_mapping": {"position": [0, 0], "size": 512, "scale": 1, "fills": "#000000"}},
                    {"file": "brand-banner.png", "size_px": [1200, 400], "icon_mapping": {"position": [72, 80], "size": 240, "scale": 240 / 512}},
                    {"file": "launch-poster.png", "size_px": [1080, 1350], "icon_mapping": {"position": [704, 154], "size": 280, "scale": 280 / 512}}]
    system = {**s.audit_identity(TASK), "brand": {"name": "叠光 / Layerlight", "concept": "信息叠加后仍然清晰"},
              "colors": PALETTE, "geometry": {"base": "512×512 transparent square; origin top-left", "relationship": relationship, "negative_space": "EVEN_ODD inner contours; transparent holes and gaps remain unfilled", "instance_count": 3, "count_limit": 6},
              "components": components, "clear_space": {"minimum_px": clear_space, "basis": "minimum distance from every selected ring bounding box to the 512px canvas edges", "applications": "same proportion preserved by shared scale"},
              "applications": applications, "black_check": {**black, "evidence": {"path_base": "suite_root", "path": s.rel(OUT / "symbol-black.png")}},
              "small_size_review": {**meta, "native_review": current["small-size-native"], "passed": True,
                                    "method": "Read native 32×32 comparison on the same light background; optional 8x nearest-neighbor view is supplementary"},
              "preview_selection": load_json("selection.json"), "visual_reviews": [{"file": f"{x}.png", **current[x]} for x in FINAL_SIZES]}
    basis = selection["basis"][:80]
    rationale = ("两个预览分别采用斜向错层与同心圆角框：前者强调逐层叠加的方向，后者用三层清晰孔隙强调信息归整。"
                 f"实际查看两张透明预览后，选择{'同心' if direction == 'concentric' else '斜向错层'}方案，依据为：{basis}。"
                 "最终仅保留三个独立圆角环母形，以EVEN_ODD内轮廓生成透明孔洞；彩色与黑版共享全部几何参数。"
                 "32×32检查采用预乘alpha Lanczos再恢复未预乘RGBA，并在同一浅色底上按原尺寸查看。"
                 "黑版逐像素检查alpha>0时RGB均为0。横幅与海报直接复用同一DSL几何规则，不嵌入图标PNG。")
    assert len(rationale) <= 300
    s.write_json(OUT / "brand-system.json", system); (OUT / "rationale.md").write_text(rationale + "\n", encoding="utf-8")
    files = [f"{stem}.{ext}" for stem in FINAL_SIZES for ext in ("png", "snapshot")] + ["brand-system.json", "rationale.md", "snapshot-usage.md", "task-metrics.json"]
    s.write_usage(RUN, TASK, "completed", [
        ("标志系统", f"通过；选择{direction}方案，三个圆角环母形，≤6；EVEN_ODD负空间规则、比例、留白和应用映射写入brand-system.json。"),
        ("透明与黑版", "通过；两图标RGBA透明；alpha掩码完全一致；黑版逐像素验证所有alpha>0的RGB=(0,0,0)，含抗锯齿边缘。"),
        ("小尺寸", "通过；Pillow预乘alpha Lanczos生成两张32×32预览，恢复未预乘RGBA；Read同一浅色底原尺寸比较，另保留8x补充预览。"),
        ("应用", "通过；横幅与海报由共享DSL几何直接重建，无Image嵌入；海报为独立深色纵向构图，所有指定文案完整。"),
        ("预览选择与实际看图", "通过；两个不同几何方向均实际Read后选择；四张最终服务原图与32px比较均逐项查看。")],
        f"叠光以三个圆角环表达信息分层而不互相遮挡，采用{direction}几何方向。靛蓝、青绿、琥珀由外至内形成层级，透明孔洞保留关键负空间；黑版只换填充色，不改变几何。",
        "准备阶段离线比较两种几何DSL并验证彩色/黑色除填充色外完全一致。执行阶段先查看两个方向再选择；若实际预览暴露缺陷，另存版本并重新选择，不覆盖旧尝试。", files)
    s.finish_task(RUN, TASK, files, [s.rel(TEMP / "iterations.jsonl"), s.rel(TEMP / "reviews.jsonl"), s.rel(TEMP / "selection.json"), thumb["metadata"]], [])
    print(json.dumps(s.metrics(RUN, TASK), ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest="command")
    sub.add_parser("prepare")
    r = sub.add_parser("render"); r.add_argument("--version", default="v001"); r.add_argument("--previews", action="store_true"); r.add_argument("--finals", action="store_true")
    sel = sub.add_parser("select"); sel.add_argument("--direction", choices=("concentric", "diagonal"), required=True); sel.add_argument("--version", required=True); sel.add_argument("--observed", required=True)
    th = sub.add_parser("thumbnails"); th.add_argument("--version", required=True)
    v = sub.add_parser("review"); v.add_argument("--stem", required=True); v.add_argument("--version", required=True); v.add_argument("--image", required=True)
    v.add_argument("--kind", choices=("alternative", "baseline", "requirement-change", "audit_visual_recheck"), default="baseline")
    v.add_argument("--observed", required=True); v.add_argument("--changes", required=True); v.add_argument("--compared", required=True); v.add_argument("--accept", action="store_true")
    sub.add_parser("finalize"); a = p.parse_args(); cmd = a.command or "prepare"
    if cmd == "prepare":
        validate_dsls()
        print(json.dumps({"task": TASK, "mode": "offline_prepare", "run_id": RUN, "preview_directions": list(PREVIEWS), "final_mother_form_instances": 3, "finals": FINAL_SIZES, "black_geometry_identical_except_fill": True, "service_requests": 0, "state_changed": False}, ensure_ascii=False, indent=2))
    elif cmd == "render":
        assert a.previews != a.finals, "choose exactly --previews or --finals"
        render_previews(a.version) if a.previews else render_finals(a.version)
    elif cmd == "select": select(a.direction, a.version, a.observed)
    elif cmd == "thumbnails": thumbnails(a.version)
    elif cmd == "review": review(a.stem, a.version, a.image, a.kind, a.observed, a.changes, a.compared, a.accept)
    elif cmd == "finalize": finalize()


if __name__ == "__main__": main()
