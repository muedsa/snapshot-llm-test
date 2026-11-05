#!/usr/bin/env python3
"""A13 post-visual-review: fill real 32x32 observations and print stats."""
import json
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite  # noqa: E402

TASK = "A13"
out = suite.out_dir(TASK)
p = out / "brand-system.json"
bs = json.loads(p.read_text(encoding="utf-8"))

sr = bs["small_size_review"]
sr["viewed_at_actual_32px"] = True
sr["light_background"] = "#F4F7FC"
sr["observation"] = (
    "在同一浅色底 #F4F7FC 上以真实 32×32 原尺寸打开彩色与黑色两张缩略及并排对比图："
    "两版轮廓均可识别为错位叠层方块，中央透明方孔（关键负空间）在 32 像素仍清晰成孔，"
    "右上光点可见；两版形状一致。另用 8 倍 NEAREST 放大图辅助确认抗锯齿边缘平滑、"
    "无彩色残留与白边。原尺寸检查未被放大图替代。"
)
sr["viewed_files"] = [
    "tmp/20261104-145656-hy4all/A13/preview/symbol-color-32-on-light.png (32×32 原尺寸)",
    "tmp/20261104-145656-hy4all/A13/preview/symbol-black-32-on-light.png (32×32 原尺寸)",
    "tmp/20261104-145656-hy4all/A13/preview/thumbs-compare-32.png (同一浅底并排，均为 32×32 原尺寸)",
    "tmp/20261104-145656-hy4all/A13/preview/symbol-color-32-zoom8.png (8× 辅助)",
    "tmp/20261104-145656-hy4all/A13/preview/symbol-black-32-zoom8.png (8× 辅助)",
]
bs["final_image_review"] = [
    "outputs/20261104-145656-hy4all/A13/symbol-color.png — 浅底合成后打开，3 构件/负空间/色彩层次通过",
    "outputs/20261104-145656-hy4all/A13/symbol-black.png — 浅底合成后打开，纯黑且几何一致通过",
    "outputs/20261104-145656-hy4all/A13/brand-banner.png — 两条文案完整、图标同几何重绘",
    "outputs/20261104-145656-hy4all/A13/launch-poster.png — 五条文案完整、独立竖向构图",
    "tmp/20261104-145656-hy4all/A13/v0-previews/direction-A-on-light.png — 方向预览（入选）",
    "tmp/20261104-145656-hy4all/A13/v0-previews/direction-B-on-light.png — 方向预览（未选）",
]
bs["checks"] = [
    {"item": "透明背景", "observed": "两张 512 图标均为 RGBA，alpha 范围 0–255，背景 alpha=0", "verified": True},
    {"item": "纯黑图标 RGB=0", "observed": "解码未预乘 RGBA 后 alpha>0 的 128848 像素中违规 0 个，alpha 范围 0–255", "verified": True},
    {"item": "两图标几何相同", "observed": "不透明掩码 128213 像素逐像素一致；仅 12 个半透明边缘像素 alpha 差 ≤1（题面允许）", "verified": True},
    {"item": "构件数 ≤6", "observed": "P1/P2 两个带孔方环 + P3 光点 = 3；内孔为负空间不另计", "verified": True},
    {"item": "32×32 轮廓与负空间", "observed": "原尺寸浅底查看，中央方孔与阶梯轮廓在彩色/黑色两版均清晰", "verified": True},
    {"item": "跨应用同几何、不嵌 PNG", "observed": "横幅与海报均调用 draw_symbol 同一几何规则生成，四份 DSL 无 <Image>", "verified": True},
]
p.write_text(json.dumps(bs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

recs = suite.read_request_log(TASK)
att = [a for r in recs for a in r.get("attempts", [])]
times = [a["started_at"] for a in att]
ends = [a["ended_at"] for a in att]
print("checks:", len(bs["checks"]), "| small_size viewed:", sr["viewed_at_actual_32px"])
print("records=%d attempts=%d success=%d failed=%d retries=%d" % (
    len(recs), len(att), sum(1 for a in att if a["success"]),
    sum(1 for a in att if not a["success"]), sum(1 for a in att if a["attempt"] > 0)))
for r in recs:
    print("  ", r["label"], len(r["attempts"]), "attempts")
print("first_request_started_at:", min(times) if times else None)
print("last_request_ended_at:", max(ends) if ends else None)
