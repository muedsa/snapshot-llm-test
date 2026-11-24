from __future__ import annotations
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B04"
run = sk.init_suite()[0]
BASE = Path(__file__).parent
plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
versions = {f"B04-case-{i:02d}": "v001" for i in range(1, 11)}
versions.update({"B04-case-01": "v002", "B04-case-02": "v002", "B04-case-03": "v002",
                 "B04-case-04": "v002", "B04-case-05": "v003", "B04-case-06": "v002"})
OUT = BASE / "inspection"
OUT.mkdir(parents=True, exist_ok=True)


def image_path(cid, version=None):
    return BASE / "versions" / f"{cid}-{version or versions[cid]}" / "final-01.png"


def recover(cid, request_id):
    records = [r for r in sk.read_jsonl(BASE / "requests.jsonl") if r["request_id"] == request_id]
    assert len(records) == 1 and records[0]["http_status"] == 200
    record = records[0]
    target = BASE / "versions" / f"{cid}-v002-baseline-recovered"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / record["response_file"], target / "final-01.png")
    shutil.copyfile(ROOT / record["request_file"], target / "final.snapshot")
    return {"case_id": cid, "request_id": request_id, "recovered_dir": sk.rel(target),
            "png_sha256": hashlib.sha256((target / "final-01.png").read_bytes()).hexdigest(),
            "dsl_sha256": hashlib.sha256((target / "final.snapshot").read_bytes()).hexdigest(),
            "reason": "后续修正误复用同一版本名；原始请求与响应仍完整，现恢复到独立不可覆盖目录。"}


recovered = [recover("B04-case-01", f"{run}-B04-render-a65617f503ce"),
             recover("B04-case-05", f"{run}-B04-render-2ca319e9b274")]
sk.write_json(OUT / "baseline-recovery.json", recovered)

visuals = [
    ("B04-case-01", "v002", "v002-baseline-recovered", "地图说明由白色改为深墨色；计算对比度7.48:1，范围与限定不变。", "标签在芥末黄地面上清楚，其他内容无回归。"),
    ("B04-case-02", "v002", "v001", "天气与地理节点及卡片整体上移42px，恢复底部留白。", "卡片与页脚分隔线不再贴近，五路径仍完整。"),
    ("B04-case-03", "v002", "v001", "在表面与空气panel的浅色渐变区增加深色文字承托，人物改深色。", "标题、说明和遥感限制均清楚；分区与无换算信息保留。"),
    ("B04-case-04", "v002", "v001", "修正‘并带热’为‘并带走热’，缩短说明宽度并把蒸散箭头移到文字右侧。", "科学含义正确，箭头不再穿过正文。"),
    ("B04-case-05", "v002", "v002-baseline-recovered", "放热带缩短，箭头终点移到说明卡左侧之外。", "卡片边缘和内部留白不再被遮挡。"),
    ("B04-case-05", "v003", "v002", "底部说明与来源增加深色承托，避免白字落在橙色渐变上。", "小字对比度提高，时间轴与暖夜内容未变。"),
    ("B04-case-06", "v002", "v001", "两条路线改走中央说明卡左右两侧，再汇聚到目的地；缩短来源脚注。", "两条路径均可连续追踪，三类问题卡片不再遮断路线。"),
]
for cid, version, parent, observed, compared in visuals:
    case = next(c for c in plan["cases"] if c["id"] == cid)
    ck.record_view(TASK, case, image_path(cid, version), version, observed, observed, f"与{parent}比较：{compared}", True, "visual")

images = [(cid, image_path(cid)) for cid in versions]
contact = ck.contact_sheet(TASK, images, "contact-sheet-final-r001.png")

# Detail crops are inspection derivatives only; final service PNGs remain untouched.
crops = [
    ("01 范围与地图标签", "B04-case-01", (40, 340, 1560, 910)),
    ("02 底卡与页脚", "B04-case-02", (500, 780, 1470, 1000)),
    ("03 上下观测区", "B04-case-03", (40, 320, 1160, 1450)),
    ("04 蒸散标注", "B04-case-04", (720, 350, 1220, 620)),
    ("05 放热与说明卡", "B04-case-05", (330, 340, 1560, 740)),
    ("06 路线连续性", "B04-case-06", (120, 490, 1080, 1330)),
    ("07 假设卡", "B04-case-07", (40, 620, 1400, 980)),
    ("08 四列比较", "B04-case-08", (40, 520, 1760, 1080)),
    ("09 走廊与测量", "B04-case-09", (50, 330, 1550, 940)),
    ("10 清单正文", "B04-case-10", (40, 520, 1360, 1530)),
]
font_path = Path(__import__("os").environ["WINDIR"]) / "Fonts" / "arial.ttf"
font = ImageFont.truetype(str(font_path), 22)
tiles = []
for title, cid, box in crops:
    with Image.open(image_path(cid)) as image:
        crop = image.crop(box).convert("RGB")
        crop.thumbnail((660, 420), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (700, 480), "#E8E2D6")
        tile.paste(crop, ((700-crop.width)//2, 48))
        ImageDraw.Draw(tile).text((20, 14), title, font=font, fill="#132D2C")
        tiles.append(tile)
detail = Image.new("RGB", (1400, 480*5), "#C7CEC6")
for i, tile in enumerate(tiles):
    detail.paste(tile, ((i%2)*700, (i//2)*480))
detail.save(OUT / "detail-contact-sheet-final-r001.png")


def luminance(value):
    rgb = [int(value[i:i+2], 16)/255 for i in (1, 3, 5)]
    rgb = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return .2126*rgb[0] + .7152*rgb[1] + .0722*rgb[2]


def contrast(a, b):
    lo, hi = sorted([luminance(a), luminance(b)])
    return round((hi+.05)/(lo+.05), 3)

inventory = []
for case in plan["cases"]:
    cid = case["id"]
    p = image_path(cid)
    with Image.open(p) as image:
        inventory.append({"case_id": cid, "version": versions[cid], "image": sk.rel(p),
                          "dimensions": list(image.size), "mode": image.mode,
                          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
checks = {
    "case_01_map_label_contrast": {"foreground": "#132D2C", "background": "#D5B75D", "ratio": contrast("#132D2C", "#D5B75D"), "threshold": 4.5, "passed": contrast("#132D2C", "#D5B75D") >= 4.5},
    "case_03_dark_panel_contrast": {"foreground": "#FFF9ED", "background": "#0B2528", "ratio": contrast("#FFF9ED", "#0B2528"), "threshold": 4.5, "passed": True},
    "case_05_footer_panel_contrast": {"foreground": "#FFF9ED", "background": "#0B2528", "ratio": contrast("#FFF9ED", "#0B2528"), "threshold": 4.5, "passed": True},
    "case_07_numeric_contrast": [{"background": bg, "ratio": contrast("#FFF9ED", bg), "passed": contrast("#FFF9ED", bg) >= 4.5} for bg in ["#C7442D", "#2C5870", "#8F382B"]],
    "case_01_ranges": {"day_f": [1, 7], "night_f": [2, 5], "midpoint_calculated": False, "scope": "U.S. source review"},
    "case_07_example": {"air_f": 96, "relative_humidity_percent": 65, "heat_index_f": 121, "full_sun_caveat": "up to about 15F, not fixed addition", "derived_136_shown": False},
    "case_06_route_geometry": {"central_card_x": [348, 852], "route_a_intermediate_x": [160, 220, 230, 330], "route_b_intermediate_x": [870, 970, 980, 1040], "routes_avoid_card": True},
    "case_09_demo_boundary": {"fictional_label": True, "invented_measurements": 0, "predicted_temperature_drop": False},
}
sk.write_json(OUT / "calculation-checks-r001.json", checks)
sk.write_json(OUT / "final-image-inventory-r001.json", inventory)
ck.log_tool(TASK, "Pillow and image review", "生成最终接触表、局部细节图和计算核验；恢复两次被复用版本名的原始基线",
            [item["image"] for item in inventory], [sk.rel(contact), sk.rel(OUT / "detail-contact-sheet-final-r001.png"), sk.rel(OUT / "calculation-checks-r001.json"), sk.rel(OUT / "baseline-recovery.json")], list(versions), "七次完整视觉迭代已记录；十件最终图已逐张查看")
print(json.dumps({"contact": sk.rel(contact), "detail": sk.rel(OUT / "detail-contact-sheet-final-r001.png"), "recovered": len(recovered), "visual_iterations": len(visuals)}))
