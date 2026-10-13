"""Write A13's image-view and iteration evidence logs from the actual render history."""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A13"
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST).isoformat(timespec="seconds")


def stamp(name):
    return datetime.fromtimestamp((TMP / name).stat().st_mtime, CST).isoformat(
        timespec="seconds")


VIEWS = [
    ("v001", "view-v001-preview-a-on-paper.png", "full",
     "方向 A 预览（透明图合成到纸色上看）：两个 16 单位描边的圆角方框错位叠放，"
     "琥珀实心块压在前，左上悬一个墨点。层叠语义成立，但墨点与任何构件都不相接，像噪点"),
    ("v001", "view-v001-preview-b-on-paper.png", "full",
     "方向 B 预览：圆环 + 三条过心旋转弦 + 圆心。构图对称稳定，但读起来像齿轮/风扇，"
     "与“叠加”无关，圆心把三条弦的交点完全盖住"),
    ("v001", "v001-preview-a-compare.png", "thumbnail32",
     "A 的 512 缩到 128 与 32 并排：32px 下两条描边只剩约 1px，轮廓断裂成淡青与淡蓝的碎线，"
     "层序读不出来；量化为 1024 个像素里只有 57 个完全不透明"),
    ("v001", "v001-preview-b-compare.png", "thumbnail32",
     "B 的 32px 缩略：六向轮辐并成一团，环与弦糊在一起，只有外圈轮廓可辨"),
    ("v002", "v002-preview-a-compare.png", "thumbnail32",
     "改厚后：32px 里蓝块、青框（含框孔）、琥珀块与墨点都能分辨，完全不透明像素从 57 升到 158；"
     "128px 下框孔透出后层蓝边，层叠语义更直接。确定选 A 并进入应用件"),
    ("v003", "view-symbol-black-on-white.png", "full",
     "纯黑版：层序反了——后层给了 alpha 255、前层只有 150，于是最靠前的琥珀块变成最浅的灰，"
     "看起来像被压在后面。彩色版不受影响，但黑版必须靠 alpha 分层"),
    ("v004", "v004-view-symbol-black-on-white.png", "full",
     "alpha 递增改为后 160 / 中 208 / 前与圆点 255：上层永远比下层更实，"
     "前后关系与彩色版一致，框孔仍透出后层的浅灰"),
    ("v004", "v004-view-symbol-color-on-paper.png", "full",
     "彩色版复核：蓝后层、青框（孔内透出蓝边）、琥珀前块、墨点，四构件层次与负空间都清楚"),
    ("v005", "v005-brand-banner.png", "full",
     "横幅：图标在左、双语字标与主张在右，两条字标共用基线；"
     "v004 之前所有文字都被居中（label 默认 align=CENTER），现已左对齐到 x=368"),
    ("v005", "v005-launch-poster.png", "full",
     "海报：上 430px 深色带放反相图标 + OPEN BETA + 品牌行，下部纸面是大字标、主张、"
     "三行信息与 CTA 条。构图与横幅不同，不是横幅放大"),
    ("v005", "v005-32-both.png", "thumbnail32",
     "两个最终图标的 32px 实际尺寸（上排）与 8× 放大（下排）并排：轮廓、前后层与框内负空间"
     "在两版都保持；黑色版缩略后重采样像素仍全部为 RGB 0"),
    ("v005", "v005-symbol-color-32-actual.png", "actual32",
     "彩色图标按真实 32 像素查看（未放大）：可辨认为“两块实心 + 一个方框 + 一点”"),
    ("v005", "v005-symbol-black-32-actual.png", "actual32",
     "黑色图标按真实 32 像素查看（未放大）：轮廓与彩色版一致，深浅层序仍可分"),
]

ITERS = [
    ("v001", None, "baseline", ["A13-probe-alpha", "A13-render-v001-preview-a-a1",
                                "A13-render-v001-preview-b-a1"],
     "先用探针确认 `<Snapshot>` 省略 background 时服务真的返回 RGBA 透明"
     "（128×128 里 10210 个 alpha=0、122 个半透明）。两个方向的预览都出图。"
     "A 的墨点悬空；B 语义偏齿轮。32px 缩略量化出 A 的描边在缩小后崩解（57/1024 不透明）",
     "选定 A 方向；把 A 重构为“后层实心 + 中层 34 单位厚框 + 前层 132 单位实心块 + 圆点”，"
     "并把圆点移到中层框左下与描边相接；同时写 thumb.py 用预乘 alpha 的 Lanczos 做缩略"),
    ("v002", "v001", "visual", ["A13-render-v002-preview-a-a1"],
     "32px 缩略里不透明像素从 57 升到 158，层序与框孔都可辨；128px 下框孔透出后层蓝边。"
     "方向定稿，开始做四个应用件",
     "生成 symbol-color / symbol-black / brand-banner / launch-poster 四份 DSL；"
     "图标几何写成 scale-aware 的 symbol_A(cx, cy, s, palette)，横幅与海报按各自中心与比例重绘，"
     "不嵌入图标 PNG"),
    ("v003", "v002", "visual",
     ["A13-render-v003-symbol-color-a1", "A13-render-v003-symbol-black-a1",
      "A13-render-v003-brand-banner-a1", "A13-render-v003-launch-poster-a1"],
     "四件都出图。纯黑版层序反了：后层 alpha 255 最黑、前层 alpha 150 最浅，"
     "视觉上前后互换。横幅与海报的所有文字被居中而不是左对齐",
     "把黑版 alpha 改成随层序递增（160/208/255）；"
     "用 probe-align.snapshot 实测 START/LEFT/END/RIGHT/CENTER 五种 textAlign 都被正确解析，"
     "确认是 snap.label() 的默认 align=\"CENTER\" 造成，而不是解析器不认 LEFT"),
    ("v004", "v003", "visual",
     ["A13-render-v004-symbol-color-a1", "A13-render-v004-symbol-black-a1",
      "A13-render-v004-brand-banner-a1", "A13-render-v004-launch-poster-a1"],
     "黑版层序正确。横幅/海报仍是居中（本轮只改了黑版 alpha）",
     "在 A13 的 gen.py 里包一层 label()，默认 align=\"LEFT\"，"
     "需要右对齐的地方显式写 RIGHT；不改动共享的 snap.py，避免影响已交付题目"),
    ("v005", "v004", "final",
     ["A13-render-v005-brand-banner-a1", "A13-render-v005-launch-poster-a1",
      "A13-render-v005-symbol-color-a1", "A13-render-v005-symbol-black-a1"],
     "横幅与海报文字左对齐、字标共基线，四件全部正常。verify.py 实测："
     "两版图标均 RGBA 透明；纯黑版 70124 个 alpha>0 像素里违规 0 个、"
     "alpha>0 处只出现一种 RGB 取值 (0,0,0)、alpha 范围 1–255；"
     "两版支撑掩膜对称差 4 像素（0.006%，仅抗锯齿边缘）；"
     "横幅 44px / 海报 56px 外框内非背景像素 0；"
     "32px 缩略（预乘 Lanczos）后黑色版重采样像素违规仍为 0",
     "定稿：复制四件到 outputs/<run>/A13/，写 brand-system.json 与 rationale.md"
     "（正文 299 字符 / 231 个汉字，≤300）"),
]

views = []
for i, (ver, img, kind, note) in enumerate(VIEWS, 1):
    views.append({"view_id": f"A13-view-{i:02d}", "task_id": "A13", "dsl_version": ver,
                  "image": f"tmp/{RUN}/A13/{img}", "kind": kind, "note": note,
                  "tool": "Read (multimodal image view) + PIL composite/resize + numpy alpha scan",
                  "image_written_at": stamp(img), "logged_at": NOW,
                  "path_base": "suite_root"})

iters = []
for ver, parent, typ, reqs, observed, change in ITERS:
    iters.append({"version": ver, "parent": parent, "type": typ, "renders": reqs,
                  "viewed": True, "observed": observed, "change": change,
                  "ts": NOW, "path_base": "suite_root"})

(TMP / "image-views.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in views) + "\n", encoding="utf-8")
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(v, ensure_ascii=False) for v in iters) + "\n", encoding="utf-8")
print("views", len(views), "iterations", len(iters))
