from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import runtime as r

s = r.s
TASK = "A23"
TIMES = [0, 250, 500, 750, 1000, 1250]
PALETTE = ["#0B6B57", "#D97706", "#2563EB", "#7C3AED", "#B42318", "#0F766E"]
UNITS = [
    {"id": "cover", "case": "cover", "output": "cover.png", "width": 1200, "height": 800},
] + [
    {"id": f"frame-{i:02d}", "case": f"frame-{i:02d}", "output": f"frame-{i:02d}.png", "width": 600, "height": 600, "transparent": True}
    for i in range(1, 7)
]


def unit_specs():
    result = []
    for i in range(12):
        angle = i * 30
        final_angle = angle + 90
        start_angle = angle + (-7 if i % 2 == 0 else 7)
        start_radius = 220 + (i % 3) * 12
        result.append({"id": f"U{i + 1:02d}", "geometry": "rounded_rectangle", "width": 64, "height": 18,
                       "radius": 9, "rgb": PALETTE[i % len(PALETTE)], "alpha": 1,
                       "start": [300 + start_radius * math.cos(math.radians(start_angle)),
                                 300 + start_radius * math.sin(math.radians(start_angle))],
                       "start_rotation": final_angle + (i % 3 - 1) * 40,
                       "final": [300 + 140 * math.cos(math.radians(angle)), 300 + 140 * math.sin(math.radians(angle))],
                       "final_rotation": final_angle})
    return result


def smoother(value):
    return value * value * value * (value * (value * 6 - 15) + 10)


def state(spec, frame_index):
    t = smoother(frame_index / 5)
    x = spec["start"][0] + (spec["final"][0] - spec["start"][0]) * t
    y = spec["start"][1] + (spec["final"][1] - spec["start"][1]) * t
    rotation = spec["start_rotation"] + (spec["final_rotation"] - spec["start_rotation"]) * t
    return [x, y, rotation]


def angular_delta(a, b):
    return (b - a + 180) % 360 - 180


def shape(spec, st):
    x, y, rotation = st
    child = (f'<Container width="{spec["width"]}" height="{spec["height"]}" color="{spec["rgb"]}" '
             f'borderRadius="{spec["radius"]}" transform="rotate({rotation:.12g}deg)" transformAlignment="CENTER" />')
    return s.positioned(x - spec["width"] / 2, y - spec["height"] / 2, spec["width"], spec["height"], child)


def frame_dsl(index):
    nodes = [shape(spec, state(spec, index)) for spec in unit_specs()]
    return ('<Snapshot type="png" background="transparent">\n<Container width="600" height="600">\n'
            '<Stack clipBehavior="NONE">\n' + "\n".join(nodes) + '\n</Stack>\n</Container>\n</Snapshot>\n')


def cover_dsl():
    nodes = [s.box(0, 0, 1200, 800, "#F4F7F2")]
    for spec in unit_specs():
        st = [600 + (spec["final"][0] - 300) * 1.25, 400 + (spec["final"][1] - 300) * 1.25, spec["final_rotation"]]
        scaled = dict(spec); scaled["width"] *= 1.25; scaled["height"] *= 1.25; scaled["radius"] *= 1.25
        nodes.append(shape(scaled, st))
    nodes += [s.circle(600, 400, 82, "#FFFFFF", "#BCD2C8"),
              s.label("从结构到画面", 80, 80, 1040, 90, 64, "#12372F", True, "CENTER"),
              s.label("STRUCTURE CONVERGES INTO IMAGE", 80, 680, 1040, 44, 28, "#34564D", True, "CENTER")]
    return s.snapshot(1200, 800, nodes, "#F4F7F2")


def build_all():
    result = {"cover": {"dsl": cover_dsl()}}
    for i in range(6):
        result[f"frame-{i + 1:02d}"] = {"dsl": frame_dsl(i), "states": [state(spec, i) for spec in unit_specs()]}
    return result


def corners(spec, st):
    x, y, angle = st; w, h = spec["width"] / 2, spec["height"] / 2
    rad = math.radians(angle)
    return [[x + px * math.cos(rad) - py * math.sin(rad), y + px * math.sin(rad) + py * math.cos(rad)]
            for px, py in [(-w, -h), (w, -h), (w, h), (-w, h)]]


def overlap(a, b):
    for poly in (a, b):
        for i in range(4):
            p, q = poly[i], poly[(i + 1) % 4]
            axis = [-(q[1] - p[1]), q[0] - p[0]]
            pa = [x * axis[0] + y * axis[1] for x, y in a]
            pb = [x * axis[0] + y * axis[1] for x, y in b]
            if max(pa) <= min(pb) + 0.01 or max(pb) <= min(pa) + 0.01:
                return False
    return True


def validate_static(unit_id, item):
    if unit_id == "cover":
        assert "从结构到画面" in item["dsl"]
        assert "<Image" not in item["dsl"]
        return
    index = int(unit_id[-2:]) - 1
    assert len(item["states"]) == 12
    assert "<Text" not in item["dsl"] and "<Image" not in item["dsl"]
    assert 'background="transparent"' in item["dsl"]
    polygons = []
    for spec, st in zip(unit_specs(), item["states"]):
        x, y, _ = st
        assert 40 <= x <= 560 and 40 <= y <= 560
        poly = corners(spec, st)
        assert all(0 <= px <= 600 and 0 <= py <= 600 for px, py in poly)
        polygons.append(poly)
    for i in range(12):
        for j in range(i + 1, 12):
            assert not overlap(polygons[i], polygons[j]), f"occlusion risk {unit_id} U{i + 1:02d}/U{j + 1:02d}"


def frame_data():
    specs = unit_specs(); frames = []
    for i, t in enumerate(TIMES):
        states = [state(spec, i) for spec in specs]
        frames.append({"id": f"frame-{i + 1:02d}", "t_ms": t, "png": f"frame-{i + 1:02d}.png", "snapshot": f"frame-{i + 1:02d}.snapshot",
                       "units": [{"id": spec["id"], "center": st[:2], "width": spec["width"], "height": spec["height"],
                                  "rotation_clockwise_deg": st[2], "rgb": spec["rgb"], "alpha": spec["alpha"],
                                  "visible": True, "visibility_evidence": "center inside canvas; non-overlapping unrotated geometry; no opacity or off-canvas hiding"}
                                 for spec, st in zip(specs, states)]})
    trajectories = []
    for j, spec in enumerate(specs):
        segments = []
        for i in range(5):
            a, b = state(spec, i), state(spec, i + 1)
            dx, dy = b[0] - a[0], b[1] - a[1]
            distance = math.hypot(dx, dy)
            segments.append({"from": f"frame-{i + 1:02d}", "to": f"frame-{i + 2:02d}", "duration_ms": 250,
                             "displacement_px": distance, "velocity_px_per_ms": distance / 250,
                             "direction_vector_xy": [dx / distance, dy / distance] if distance else [0.0, 0.0],
                             "angular_velocity_clockwise_deg_per_ms": angular_delta(a[2], b[2]) / 250,
                             "signed_angle_delta_deg": angular_delta(a[2], b[2])})
        a, b = state(spec, 5), state(spec, 0)
        dx, dy = b[0] - a[0], b[1] - a[1]
        distance = math.hypot(dx, dy)
        seam = {"from": "frame-06", "to": "frame-01", "duration_ms": 250, "displacement_px": distance,
                "velocity_px_per_ms": distance / 250,
                "direction_vector_xy": [dx / distance, dy / distance] if distance else [0.0, 0.0],
                "angular_velocity_clockwise_deg_per_ms": angular_delta(a[2], b[2]) / 250,
                "signed_angle_delta_deg": angular_delta(a[2], b[2]), "raw_angle_difference_deg": b[2] - a[2],
                "position_jump": True, "equivalent_rotation_jump": abs(angular_delta(a[2], b[2])) > 1e-9}
        trajectories.append({"id": spec["id"], "interpolation": "p=smootherstep(u), u=(frame_index)/5; center=p*start+(1-p)*final; rotation likewise; keyframes only, no intermediate frames rendered",
                             "adjacent_segments": segments, "seam": seam})
    ordinary = [x for t in trajectories for x in t["adjacent_segments"]]
    seam_distances = [t["seam"]["displacement_px"] for t in trajectories]
    seam_speeds = [t["seam"]["velocity_px_per_ms"] for t in trajectories]
    ordinary_speeds = [x["velocity_px_per_ms"] for x in ordinary]
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
            "coordinate_system": {"origin": "top-left", "unit": "pixel", "position": "unrotated geometry center",
                                  "rotation": "own center, clockwise degrees", "dimensions": "unrotated width/height"},
            "units": [{k: v for k, v in spec.items() if k not in {"start", "start_rotation", "final", "final_rotation"}} for spec in specs],
            "frames": frames, "trajectories": trajectories,
            "seam": {"interval": "1250ms -> 1500ms(=0ms)", "per_unit": [{"id": t["id"], **t["seam"]} for t in trajectories],
                     "closed_positions": False, "closed_equivalent_rotations": False,
                     "maximum_position_jump_px": max(seam_distances),
                     "ordinary_displacement_range_px": [min(x["displacement_px"] for x in ordinary), max(x["displacement_px"] for x in ordinary)],
                     "seam_velocity_range_px_per_ms": [min(seam_speeds), max(seam_speeds)],
                     "ordinary_velocity_range_px_per_ms": [min(ordinary_speeds), max(ordinary_speeds)],
                     "direction_velocity_conclusion": "Per-unit direction vectors, displacement and velocity compare the seam with all ordinary 250ms steps; the loop returns from a compact ring to a dispersed ring in 250ms, a visible positional jump rather than seamless motion.",
                     "actual_view_conclusion": "Requires viewing all six PNGs and the contact sheet before completion; loop=true is not used as proof."}}


def timing():
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
            "frames": [{"id": f"frame-{i + 1:02d}", "png": f"frame-{i + 1:02d}.png", "t_ms": t, "duration_ms": 250} for i, t in enumerate(TIMES)],
            "loop": True, "period_ms": 1500, "seamless": False,
            "seam_evidence": {"frame_data": "frame-data.json", "jump": "frame-06 compact ring -> frame-01 dispersed ring",
                              "effect": "one visible reset jump every 1500ms; no GIF/player is delivered",
                              "basis": "position and equivalent rotation differences computed per unit; not inferred from loop flag"},
            "intermediate_frames_rendered": False, "delivered_animation_container": None}


def limitations():
    return """# A23 格式边界与替代交付

| 客户请求 | 原生支持判断 | 依据 | 本题授权替代 | 仍需外部后续工作 |
|---|---|---|---|---|
| 文字可编辑SVG | Open Snapshot 的 `/snapshot` 仅契约 png/jpg/webp；未提供SVG导出或文本节点导出 | 共享缓存 `ai-guide.md` 第49行及 `openapi.yaml` 响应类型 | 1200×800不透明sRGB色彩PNG封面；文字仍保留在完整DSL中 | 若客户必须得到可编辑SVG，需另行设计矢量重建与字体/文本分组方案；本题未执行 |
| CMYK印刷稿 | 接口没有CMYK色彩空间或分色参数 | `openapi.yaml` 仅图片二进制响应；Parser颜色为sRGB CSS | 不透明sRGB色彩PNG，不冒充CMYK印刷稿 | 印刷交付需外部印前流程进行色彩转换、版式核对与打样；本题未执行 |
| 6帧透明GIF动画 | 服务无动画/GIF输出参数；GIF也不在png/jpg/webp契约内 | `ai-guide.md` 与 `openapi.yaml` | 6张600×600透明PNG关键帧和 `timing.json`（250ms/帧、1500ms循环） | 如需GIF，需外部动画封装工具；必须保留透明与帧时序，并重新视觉检查 |
| PNG封面 | 原生支持 | `Snapshot type="png"` 与 `image/png` 响应 | 1200×800不透明sRGB色彩PNG | 无 |

## 动画边界

只交付6个真实服务关键帧，没有合成GIF、没有渲染中间帧、没有SVG或CMYK假文件。12个单元的几何、未旋转尺寸、RGB与alpha跨帧守恒，仅中心位置和自身中心顺时针旋转变化。第6帧形成12段圆环/光圈；第1帧分散，循环接缝存在明确位置跳变，`timing.json` 如实标记 `seamless=false`。`loop=true` 仅表示期望循环，不证明无缝。最终完成前必须实际逐帧查看并查看联系表；联系表仅是临时预览，不是新增动画格式。

封面颜色满足不透明RGB色彩语义。服务实际返回可能是RGB或RGBA容器；若为RGBA，`cover-validation.json` 必须证明alpha全为255。最终文件始终保留服务原始PNG字节，不秘密转成RGB，也不把文件编码模式误写成CMYK；`cover-validation.json` 记录实际模式与alpha范围。
"""


def contact_sheet():
    from PIL import Image, ImageDraw
    paths = [r.OUTPUT / f"frame-{i:02d}.png" for i in range(1, 7)]
    sheet = Image.new("RGB", (1260, 840), "#E7EFEA")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        with Image.open(path) as im:
            tile = im.convert("RGBA").resize((360, 360))
            x, y = 30 + (i % 3) * 410, 70 + (i // 3) * 380
            sheet.paste(tile, (x, y), tile)
        draw.text((x, y - 34), f"frame-{i + 1:02d} / {TIMES[i]}ms", fill="#12372F")
    target = r.TEMP / "contact-sheet.png"
    sheet.save(target)
    print(target)


def review_contact(result, observation):
    assert result in {"pass", "fail"} and observation.strip()
    r.jwrite(r.TEMP / "reviews/contact-sheet.json", {"viewed_at": s.iso(), "viewer": "HungerG", "visual_tool": "Read",
                                                      "result": result, "observation": observation,
                                                      "image_sha256": r.sha(r.TEMP / "contact-sheet.png")})


def cover_validate():
    from PIL import Image
    path = r.OUTPUT / "cover.png"
    info = r.png_check(path, 1200, 800, transparent=False)
    with Image.open(path) as im:
        mode = im.mode
        rgba = im.convert("RGBA")
        alpha = rgba.getchannel("A")
        alpha_range = list(alpha.getextrema())
        assert alpha_range == [255, 255], (mode, alpha_range)
        info.update({"mode": mode, "alpha_range": alpha_range, "opaque_rgb_color_semantics": True,
                     "cmyk_claimed": False, "raw_service_bytes_preserved": True,
                     "conversion_performed": False,
                     "encoding_note": "RGB or opaque RGBA PNG both carry opaque sRGB color; the raw service encoding is retained."})
    r.jwrite(r.TEMP / "cover-validation.json", info)


def pixel_validate():
    from PIL import Image
    specs = unit_specs()
    for i in range(6):
        path = r.OUTPUT / f"frame-{i + 1:02d}.png"
        info = r.png_check(path, 600, 600, transparent=True)
        with Image.open(path) as im:
            im = im.convert("RGBA")
            for spec in specs:
                x, y, _ = state(spec, i)
                pixel = im.getpixel((round(x), round(y)))
                expected = tuple(int(spec["rgb"][j:j + 2], 16) for j in (1, 3, 5)) + (255,)
                assert pixel == expected, (path, spec["id"], pixel, expected)
        info["unit_center_samples"] = "12/12 exact fixed RGB and alpha=255"
        r.jwrite(r.TEMP / f"pixel-validation-frame-{i + 1:02d}.json", info)


def archive():
    for unit in UNITS:
        r.promote(sys.modules[__name__], unit["id"])
    pixel_validate()
    cover_validate()
    r.jwrite(r.OUTPUT / "frame-data.json", frame_data())
    r.jwrite(r.OUTPUT / "timing.json", timing())
    (r.OUTPUT / "limitations.md").write_text(limitations(), encoding="utf-8")
    r.jwrite(r.OUTPUT / "task-metrics.json", r.round_metrics("all"))
    r.usage(sys.modules[__name__], "archived_pending_contact_review", "", "7张最终PNG逐张实际查看通过后晋升；透明像素与12单元中心颜色/alpha已核验。联系表查看尚需单独记录。")
    print(r.OUTPUT)


def finalize():
    contact = json.loads((r.TEMP / "reviews/contact-sheet.json").read_text(encoding="utf-8"))
    assert contact["result"] == "pass" and contact["image_sha256"] == r.sha(r.TEMP / "contact-sheet.png")
    frame_data = json.loads((r.OUTPUT / "frame-data.json").read_text(encoding="utf-8"))
    frame_data["seam"]["actual_view_conclusion"] = "All six frames and contact sheet were opened with Read; compact-to-dispersed loop reset is visible and seamless remains false."
    frame_data["seam"]["visual_evidence"] = {"path_base": "suite_root", "path": s.rel(r.TEMP / "reviews/contact-sheet.json")}
    r.jwrite(r.OUTPUT / "frame-data.json", frame_data)
    for name in ("frame-data.json", "timing.json", "limitations.md"):
        assert (r.OUTPUT / name).exists()
    assert json.loads((r.OUTPUT / "timing.json").read_text(encoding="utf-8"))["seamless"] is False
    spec = json.loads((r.ROOT / f"tasks/{TASK}-capability-delivery/task.json").read_text(encoding="utf-8"))
    paths = [x["filename"] for x in spec["required_outputs"]] + [x["dsl"] for x in spec["required_outputs"]]
    for key in ("additional_outputs", "common_outputs"):
        paths += [x["filename"] if isinstance(x, dict) else x for x in spec.get(key, [])]
    r.usage(sys.modules[__name__], "completed", "", "7张最终PNG及联系表均实际查看；逐单元位置/旋转守恒与接缝跳变已审计，未声称无缝。")
    s.finish_task(r.RUN_ID, TASK, sorted(set(paths)), [s.rel(r.TEMP / "promotions.jsonl"), s.rel(r.TEMP / "reviews/contact-sheet.json"), s.rel(r.TEMP / "cover-validation.json")], cases=[u["id"] for u in UNITS])
    r.task_metrics()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "archive":
        archive()
    elif len(sys.argv) > 1 and sys.argv[1] == "contact-sheet":
        contact_sheet()
    elif len(sys.argv) > 1 and sys.argv[1] == "review-contact":
        p = __import__("argparse").ArgumentParser(); p.add_argument("command"); p.add_argument("--result", required=True); p.add_argument("--observation", required=True)
        a = p.parse_args(); review_contact(a.result, a.observation)
    elif len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    else:
        r.dispatch(sys.modules[__name__], "A23 offline transparent-keyframe generator and guarded execution CLI")


if __name__ == "__main__":
    main()
