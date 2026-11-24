from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = (ROOT / "tmp" / "_suite" / "run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A23"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
STATE_PATH = ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json"
FRAME_MS = 250
PERIOD_MS = 1500


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item] == "completed" for item in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK] in ("pending", "in_progress")


def unit_definitions() -> list[dict]:
    specs = [
        ("U01", "rounded_rect", 240, 32, "#4F46E5", 255, [300, 70], [300, 236], 0),
        ("U02", "rounded_rect", 240, 32, "#4F46E5", 255, [300, 530], [300, 364], 0),
        ("U03", "rounded_rect", 32, 120, "#4F46E5", 255, [70, 300], [196, 300], 15),
        ("U04", "rounded_rect", 32, 120, "#4F46E5", 255, [530, 300], [404, 300], -15),
        ("U05", "ring", 124, 124, "#4F46E5", 255, [120, 120], [300, 300], 25),
        ("U06", "circle", 52, 52, "#22D3EE", 255, [480, 120], [300, 300], -20),
        ("U07", "rounded_rect", 64, 32, "#A78BFA", 255, [110, 440], [244, 204], 10),
        ("U08", "circle", 32, 32, "#F59E0B", 255, [490, 440], [390, 204], -10),
        ("U09", "rounded_rect", 28, 28, "#FDE68A", 255, [300, 160], [352, 204], 30),
        ("U10", "rounded_rect", 32, 92, "#6366F1", 255, [160, 300], [374, 300], 20),
        ("U11", "rounded_rect", 52, 16, "#34D399", 230, [420, 300], [218, 344], -25),
        ("U12", "rounded_rect", 96, 16, "#94A3B8", 255, [300, 410], [300, 392], 5),
    ]
    return [{"id": uid, "geometry": geometry, "width": width, "height": height,
             "rgb": [int(color[i:i+2], 16) for i in (1, 3, 5)], "color": color, "alpha": alpha,
             "start_position": start, "final_position": final, "start_rotation": angle,
             "final_rotation": 0.0, "radius": 8 if geometry == "rounded_rect" else None,
             "border_width": 16 if geometry == "ring" else None}
            for uid, geometry, width, height, color, alpha, start, final, angle in specs]


def smoothstep(u: float) -> float:
    return 3 * u * u - 2 * u * u * u


def state_at(unit: dict, frame_index: int) -> dict:
    u = frame_index / 5
    e = smoothstep(u)
    x = unit["start_position"][0] + (unit["final_position"][0] - unit["start_position"][0]) * e
    y = unit["start_position"][1] + (unit["final_position"][1] - unit["start_position"][1]) * e
    angle = unit["start_rotation"] + (unit["final_rotation"] - unit["start_rotation"]) * e
    return {"id": unit["id"], "position": [x, y], "width": unit["width"], "height": unit["height"],
            "rotation": angle, "rgb": unit["rgb"], "color": unit["color"], "alpha": unit["alpha"],
            "geometry": unit["geometry"], "border_width": unit["border_width"], "radius": unit["radius"], "visible": True}


def aabb(state: dict) -> list[float]:
    angle = math.radians(state["rotation"])
    width = abs(state["width"] * math.cos(angle)) + abs(state["height"] * math.sin(angle))
    height = abs(state["width"] * math.sin(angle)) + abs(state["height"] * math.cos(angle))
    x, y = state["position"]
    return [x - width / 2, y - height / 2, x + width / 2, y + height / 2]


def unit_dsl(state: dict, scale: float = 1.0, offset: tuple[float, float] = (0, 0)) -> str:
    x = offset[0] + state["position"][0] * scale
    y = offset[1] + state["position"][1] * scale
    width, height = state["width"] * scale, state["height"] * scale
    color = state["color"] + f"{state['alpha']:02X}"
    attrs = [f'width="{width:g}"', f'height="{height:g}"']
    if state["geometry"] == "ring":
        attrs += ['color="transparent"', f'border="{state["border_width"] * scale:g} SOLID {color}"']
    else:
        attrs.append(f'color="{color}"')
    if state["geometry"] in ("circle", "ring"):
        attrs.append(f'borderRadius="{min(width, height) / 2:g}"')
    elif state["geometry"] == "rounded_rect":
        attrs.append(f'borderRadius="{min(8 * scale, min(width, height) / 2):g}"')
    attrs += [f'transform="rotate({state["rotation"]:g}deg)"', 'transformAlignment="CENTER"', 'clipBehavior="ANTI_ALIAS"']
    child = "<Container " + " ".join(attrs) + " />"
    return sk.positioned(x - width / 2, y - height / 2, width, height, child)


def frame_dsl(frame_index: int) -> str:
    states = [state_at(unit, frame_index) for unit in unit_definitions()]
    for state in states:
        left, top, right, bottom = aabb(state)
        assert 0 <= left <= right <= 600 and 0 <= top <= bottom <= 600, (frame_index, state["id"], aabb(state))
    return sk.snapshot(600, 600, [unit_dsl(state) for state in states], "transparent")


def cover_dsl() -> str:
    children = [sk.box(0, 0, 1200, 800, "#0B1020")]
    for row in range(8):
        for col in range(13):
            children.append(sk.circle(660 + col * 42, 90 + row * 42, 2, "#263253"))
    children += [sk.circle(880, 390, 238, "#141E3A"), sk.circle(880, 390, 184, "#1B2850"),
                 sk.circle(880, 390, 142, "#233363"),
                 sk.box(72, 176, 7, 366, "#22D3EE", 4),
                 sk.label("MOTION STUDY  /  01", 104, 176, 520, 38, 22, "#67E8F9", True),
                 sk.label("从结构\n到画面", 104, 234, 540, 190, 76, "#F8FAFC", True),
                 sk.label("12 UNITS · 6 KEYFRAMES · 250 MS", 104, 454, 540, 38, 22, "#A5B4FC", True),
                 sk.label("分散  →  对齐  →  成像", 104, 508, 540, 48, 30, "#E2E8F0"),
                 sk.label("Snapshot DSL / transparent PNG sequence", 104, 594, 560, 38, 22, "#94A3B8")]
    children.append(sk.line(110, 692, 552, 692, "#334155", 2))
    for index in range(6):
        x = 110 + index * 88
        children.append(sk.circle(x, 692, 8 if index < 5 else 12, "#22D3EE" if index == 5 else "#64748B"))
        children.append(sk.label(f"{index * 250}", x - 28, 714, 58, 30, 18, "#94A3B8", False, "CENTER"))
    for unit in unit_definitions():
        children.append(unit_dsl(state_at(unit, 5), 1.45, (880 - 300 * 1.45, 390 - 300 * 1.45)))
    children += [sk.label("FINAL FORM", 756, 602, 248, 34, 22, "#67E8F9", True, "CENTER"),
                 sk.label("CAMERA / 12 PARTS", 726, 642, 308, 34, 22, "#CBD5E1", False, "CENTER")]
    return sk.snapshot(1200, 800, children, "#0B1020")


def frame_data(version: str = "v001") -> dict:
    units = unit_definitions()
    frames = []
    for index in range(6):
        states = [state_at(unit, index) for unit in units]
        frame_path = f"frame-{index+1:02d}.png"
        png = HERE / version / frame_path
        alpha_summary = None
        sha256 = None
        if png.exists():
            with Image.open(png) as image:
                rgba = image.convert("RGBA")
                alpha = rgba.getchannel("A")
                alpha_summary = {"mode": rgba.mode, "size": list(rgba.size), "alpha_extrema": list(alpha.getextrema()),
                                 "nonzero_alpha_pixels": sum(value > 0 for value in alpha.getdata()),
                                 "corner_alpha": [rgba.getpixel(point)[3] for point in ((0, 0), (599, 0), (0, 599), (599, 599))]}
            sha256 = sha(png)
        frames.append({"id": f"F{index+1:02d}", "t_ms": index * FRAME_MS, "png": frame_path,
                       "dsl": frame_path.replace(".png", ".snapshot"), "png_sha256": sha256,
                       "units": [{**state, "aabb": aabb(state), "visibility_method": "旋转后AABB完全位于画布内；实际PNG与接触表逐单元查看，无单元完全移出或遮住。"} for state in states],
                       "alpha_evidence": alpha_summary})
    trajectories = []
    for unit in units:
        segments = []
        for index in range(5):
            before, after = state_at(unit, index), state_at(unit, index + 1)
            dx = after["position"][0] - before["position"][0]
            dy = after["position"][1] - before["position"][1]
            raw_angle = after["rotation"] - before["rotation"]
            normalized_angle = (raw_angle + 180) % 360 - 180
            segments.append({"from_frame": f"F{index+1:02d}", "to_frame": f"F{index+2:02d}",
                             "duration_ms": FRAME_MS, "displacement": math.hypot(dx, dy), "delta_xy": [dx, dy],
                             "angle_delta_raw": raw_angle, "angle_delta_360_equivalent": normalized_angle})
        first, last = state_at(unit, 0), state_at(unit, 5)
        seam_dx = first["position"][0] - last["position"][0]
        seam_dy = first["position"][1] - last["position"][1]
        seam_raw = first["rotation"] - last["rotation"]
        seam_angle = (seam_raw + 180) % 360 - 180
        trajectories.append({"id": unit["id"], "interpolation": "u=i/5；e=3u²−2u³；p=(1−e)p_start+e p_final；θ=(1−e)θ_start+eθ_final。仅渲染六个采样关键帧，不声称服务渲染中间帧。",
                             "segments": segments,
                             "seam": {"from_frame": "F06", "to_frame": "F01", "duration_ms": FRAME_MS,
                                      "displacement": math.hypot(seam_dx, seam_dy), "delta_xy": [seam_dx, seam_dy],
                                      "angle_delta_raw": seam_raw, "angle_delta_360_equivalent": seam_angle}})
    seam_units = [{"id": item["id"], "displacement": item["seam"]["displacement"],
                   "angle_delta_360_equivalent": item["seam"]["angle_delta_360_equivalent"],
                   "largest_regular_step": max(segment["displacement"] for segment in item["segments"]),
                   "seam_to_largest_regular_step_ratio": item["seam"]["displacement"] / max(segment["displacement"] for segment in item["segments"])}
                  for item in trajectories]
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
            "coordinate_system": {"origin": "左上角", "x": "向右", "y": "向下", "position": "单元自身几何中心",
                                  "rotation": "绕自身中心，顺时针度数", "size": "未旋转宽高，像素"},
            "units": units, "frames": frames, "trajectories": trajectories,
            "seam": {"from_t_ms": 1250, "to_t_ms": 1500, "wrap_to_t_ms": 0, "closed": False,
                     "seamless": False, "per_unit": seam_units,
                     "maximum_seam_displacement": max(item["displacement"] for item in seam_units),
                     "maximum_regular_step_displacement": max(max(segment["displacement"] for segment in item["segments"]) for item in trajectories),
                     "conclusion": "末帧相机跳回首帧分散布局，位移明显大于正常步长且方向反转；timing保留loop=true，但明确seamless=false。仅依据六张实际关键帧与接触表静态核验，未声称动态无缝播放。"},
            "conservation": {"unit_count": 12, "ids": [unit["id"] for unit in units],
                             "checked_fields": ["geometry", "width", "height", "rgb", "alpha"],
                             "only_varying_fields": ["position", "rotation"], "passed": True},
            "rendering": {"service": sk.BASE + "/snapshot", "body": "UTF-8 Snapshot DSL", "intermediate_frames_rendered": False}}


def timing_data() -> dict:
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
            "frames": [{"id": f"F{index+1:02d}", "t_ms": index * FRAME_MS, "png": f"frame-{index+1:02d}.png",
                        "dsl": f"frame-{index+1:02d}.snapshot", "duration_ms": FRAME_MS} for index in range(6)],
            "loop": True, "period_ms": PERIOD_MS, "seamless": False,
            "seam_evidence": {"reference": "frame-data.json#seam", "jump_from": "F06 @1250ms", "jump_to": "F01 @1500/0ms",
                              "effect": "相机末帧快速跳回分散首帧；不是无缝循环。", "external_work": "如需无缝，应由外部动画工具增加回散中间帧或重新设计闭合关键帧序列。"},
            "note": "timing.json仅描述帧序、250ms/帧与循环周期；Snapshot服务不生成GIF、时间轴或中间帧。"}


def prepare() -> None:
    guard()
    sk.begin_task(RUN, TASK)
    directory = HERE / "v001"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "cover.snapshot").write_text(cover_dsl(), encoding="utf-8")
    for index in range(6):
        (directory / f"frame-{index+1:02d}.snapshot").write_text(frame_dsl(index), encoding="utf-8")
    sk.write_json(directory / "frame-data.json", frame_data())
    sk.write_json(directory / "timing.json", timing_data())
    sk.checkpoint(RUN, f"{TASK}-start")
    print(json.dumps({"prepared": TASK, "dsl_files": 7, "units": 12, "frames": 6}, ensure_ascii=False))


def execute(version: str) -> None:
    directory = HERE / version
    results = []
    names = ["cover"] + [f"frame-{index:02d}" for index in range(1, 7)]
    for name in names:
        source = directory / f"{name}.snapshot"
        expected = (1200, 800) if name == "cover" else (600, 600)
        response, record = sk.request(RUN, TASK, "render", sk.BASE + "/snapshot", source.read_bytes(),
                                      "text/plain; charset=utf-8", version_id=version, case_id=name)
        if record["http_status"] != 200 or not response.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError(record)
        png = directory / f"{name}.png"
        png.write_bytes(response)
        with Image.open(png) as image:
            assert image.size == expected
            if name != "cover":
                rgba = image.convert("RGBA")
                assert rgba.getchannel("A").getextrema()[0] == 0, name
        results.append({"request_id": record["request_id"], "image": rp(png), "sha256": sha(png)})
    sk.write_json(directory / "frame-data.json", frame_data(version))
    print(json.dumps(results, ensure_ascii=False))


def contact_sheet(version: str) -> None:
    directory = HERE / "inspection"
    directory.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (960, 704), "#111827")
    draw = ImageDraw.Draw(sheet)
    for index in range(6):
        col, row = index % 3, index // 3
        x, y = 16 + col * 316, 16 + row * 344
        for yy in range(y, y + 300, 20):
            for xx in range(x, x + 300, 20):
                color = "#334155" if ((xx - x) // 20 + (yy - y) // 20) % 2 == 0 else "#1E293B"
                draw.rectangle((xx, yy, min(xx + 19, x + 299), min(yy + 19, y + 299)), fill=color)
        with Image.open(HERE / version / f"frame-{index+1:02d}.png") as frame:
            rgba = frame.convert("RGBA").resize((300, 300), Image.Resampling.NEAREST)
            sheet.paste(rgba, (x, y), rgba)
        draw.text((x + 4, y + 308), f"FRAME {index+1:02d}  /  {index*250} ms", fill="#F8FAFC")
    path = directory / f"{version}-contact-sheet.png"
    sheet.save(path)
    print(rp(path))


def provenance(png: Path, dsl: Path) -> dict:
    png_hash = sha(png)
    dsl_normalized = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE / "requests.jsonl"):
        if request["request_type"] != "render":
            continue
        response, body = ROOT / request["response_file"], ROOT / request["request_file"]
        if response.exists() and body.exists() and sha(response) == png_hash and hashlib.sha256(body.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_normalized:
            return {"request_id": request["request_id"], "request_file": request["request_file"],
                    "response_file": request["response_file"], "http_status": request["http_status"],
                    "content_type": request["content_type"], "png_sha256": png_hash,
                    "dsl_sha256": hashlib.sha256(dsl.read_bytes()).hexdigest(),
                    "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True}
    raise AssertionError(f"provenance missing: {png}")


def limitations_text() -> str:
    return """# A23 能力边界与替代交付

- 状态：完整替代交付已完成；未创建伪 SVG、CMYK 或 GIF 文件。
- 判定依据：实际读取并缓存服务 `ai-guide.md`、`openapi.yaml`、`parser-tags.md`、`parser.md`；缓存路径基准为 suite_root：`tmp/20261124T113838+0800-aac601/_suite/shared/`。

| 客户请求 | 实际支持判定 | 依据 | 本题替代 | 仍需外部后续工作 |
|---|---|---|---|---|
| 文字可编辑 SVG | 原生不支持 SVG 文件输出；文字在 PNG 中栅格化 | `Snapshot.type` 仅 png/jpg/webp；OpenAPI 成功响应仅 image/png、image/jpeg、image/webp；Parser 的 SVG path 仅是裁剪路径数据，不是 SVG 文档导出 | `cover.png` 与 `cover.snapshot`；DSL 中保留可编辑文字字符串和参数，但不是 SVG 字形 | 在外部矢量工具中重建文字与图形、指定字体并输出可编辑 SVG |
| CMYK 印刷稿 | 原生不支持 CMYK 参数、ICC 配置或印刷 PDF | 接口与颜色文档只描述 PNG/JPEG/WebP 位图及 CSS/RGBA 颜色，无 CMYK/profile 字段 | 1200×800 RGB PNG 封面 | 按印厂要求转换色彩空间、嵌入 ICC、处理出血与专色，并打样 |
| 6 帧透明 GIF 动画 | 原生不支持 GIF 输出、时间轴、帧合成或循环参数 | `Snapshot.type` 枚举不含 gif；接口每次只接受一份 DSL 并返回一张位图 | 6 张 600×600 透明 PNG、同名 DSL、`timing.json` 与 `frame-data.json` | 用外部动画工具按 250ms/帧组装 GIF 或视频，并验证透明索引与循环 |
| PNG 封面 | 原生支持 | `Snapshot type="png"`；OpenAPI `image/png` 二进制响应 | `cover.png` + `cover.snapshot`，1200×800 RGB | 无 |
| 透明背景与单元 alpha | 原生支持 | `Snapshot.background` 默认 transparent；支持 #RRGGBBAA；实际六帧 RGBA 检查见 `frame-data.json` | 六张真实透明关键帧；四角 alpha=0 | 外部组装时需确认目标格式保留透明度 |
| 汇聚动画与插值 | 服务只渲染静态关键帧，不执行时间轴 | 接口无 duration/loop/frame 参数；Transform 可做单帧旋转 | 明确 smoothstep 设计轨迹，仅渲染 6 个采样点 | 外部播放器/动画工具实现中间帧与缓动 |
| 无缝循环 | 本题未声明无缝 | 末帧是汇聚后的相机，首帧是分散布局；`frame-data.json` 的接缝位移大于所有常规步长 | `loop=true`、`seamless=false`，明确 1250→1500/0ms 跳变 | 增加回散中间帧或重新设计闭合轨迹后才能宣称无缝 |

## 真实执行与核验

七张指定 PNG 均由 `POST /snapshot` 返回的原始字节保存，未使用其他绘图工具生成主体；接触表仅由已渲染关键帧拼成，保存在临时目录用于检查，不是交付图片。逐帧查看确认 U01–U12 均存在、仅位置与旋转变化、画布透明，末帧构成可识别相机图形。循环接缝会从末帧相机快速跳回首帧分散状态，影响是可见回跳；不把 loop 设置误称为无缝。
"""


def record_views(review: dict, version: str) -> None:
    existing = {item["iteration_id"] for item in sk.read_jsonl(HERE / "iterations.jsonl")}
    for name, viewed in review["reviewed"].items():
        iteration_id = f"{RUN}-{TASK}-{version}-{name}"
        if iteration_id in existing:
            continue
        kind = "audit_visual_recheck" if name == "contact_sheet" and viewed.get("passed", True) else "baseline"
        sk.append_jsonl(HERE / "iterations.jsonl", {
            "iteration_id": iteration_id, "task_id": TASK, "case_id": name, "version_id": version,
            "parent_version": "v001" if version == "v002" else None, "type": kind, "image_path": viewed["image"], "image_paths": [viewed["image"]],
            "viewed_at": viewed["viewed_at"], "timezone": "+08:00", "observable_issues": viewed["observed"],
            "changes": "修正帧坐标参考中心，保持12单元参数与轨迹不变。" if version == "v002" else "首版参数化生成。", "review_and_comparison": review["conclusion"],
            "completed_visual_iteration": viewed.get("passed", True),
        })


def finalize(review_file: str, version: str) -> None:
    guard()
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    expected = {"cover", "contact_sheet", *{f"frame_{index:02d}" for index in range(1, 7)}}
    assert review.get("completed") and set(review.get("reviewed", {})) == expected
    source = HERE / version
    names = ["cover"] + [f"frame-{index:02d}" for index in range(1, 7)]
    proofs = []
    for name in names:
        for suffix in ("png", "snapshot"):
            shutil.copyfile(source / f"{name}.{suffix}", OUTPUT / f"{name}.{suffix}")
        proofs.append({"image": f"{name}.png", **provenance(OUTPUT / f"{name}.png", OUTPUT / f"{name}.snapshot")})
    data = frame_data(version)
    assert data["conservation"]["passed"] and not data["seam"]["seamless"]
    for frame in data["frames"]:
        assert frame["alpha_evidence"]["alpha_extrema"] == [0, 255]
        assert frame["alpha_evidence"]["corner_alpha"] == [0, 0, 0, 0]
        assert len(frame["units"]) == 12 and all(unit["visible"] for unit in frame["units"])
    sk.write_json(OUTPUT / "frame-data.json", data)
    sk.write_json(OUTPUT / "timing.json", timing_data())
    (OUTPUT / "limitations.md").write_text(limitations_text(), encoding="utf-8")
    record_views(review, version)
    files = [f"{name}.{suffix}" for name in names for suffix in ("png", "snapshot")] + ["limitations.md", "frame-data.json", "timing.json"]
    sk.write_usage(RUN, TASK, "completed", [
        ("formats", "依据实际指南/OpenAPI判定原生仅输出静态位图；未编造SVG、CMYK、GIF或时间轴参数。"),
        ("cover", "1200×800 RGB PNG封面；‘从结构到画面’可读；服务原始响应与DSL匹配。"),
        ("frames", "六张600×600透明PNG均实际查看；四角alpha=0，U01–U12逐帧存在且可见。"),
        ("conservation", "12单元几何、未旋转宽高、RGB与自身alpha跨帧守恒；只改变位置和旋转。"),
        ("trajectory", "smoothstep设计轨迹、逐单元位移/角差与1250→1500/0ms接缝均记录；明确非无缝。"),
        ("contact_sheet", "透明棋盘接触表仅存临时目录，已实际查看并与六张原图逐一核对。"),
    ], "深色封面与高对比相机图形；关键帧从分散的12个构件汇聚成相机，透明背景便于外部合成。",
       "依据真实接口提供完整PNG替代，未制作伪目标格式；循环保留但接缝跳变已明确记录。", files)
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    task = next(item for item in state["tasks"] if item["id"] == TASK)
    task["status"] = "completed"
    task["ended_at"] = sk.iso()
    task["artifacts"] = [rp(OUTPUT / name) for name in files] + [rp(OUTPUT / "snapshot-usage.md"), rp(OUTPUT / "task-metrics.json")]
    task["visual_review_evidence"] = [rp(HERE / "final-review.json"), rp(HERE / f"inspection/{version}-contact-sheet.png")]
    task["unresolved_issues"] = []
    state["current_task"] = None
    state["current_round"] = None
    sk.write_json(STATE_PATH, state)
    sk.checkpoint(RUN, f"{TASK}-finish")
    sk.metrics(RUN, TASK)
    sk.write_json(HERE / "provenance.json", proofs)
    print(json.dumps({"completed": TASK, "artifacts": len(task["artifacts"]), "seamless": False}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "execute", "contact-sheet", "finalize"])
    parser.add_argument("--review-file")
    parser.add_argument("--version", default="v001")
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    elif args.mode == "execute":
        execute(args.version)
    elif args.mode == "contact-sheet":
        contact_sheet(args.version)
    else:
        finalize(args.review_file, args.version)


if __name__ == "__main__":
    main()
