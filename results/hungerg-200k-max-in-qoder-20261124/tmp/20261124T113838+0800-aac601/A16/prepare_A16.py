from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A16"
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

INPUT = ROOT / "tasks/A16-visual-data-forensics/inputs"
SOURCE = INPUT / "source.csv"
FLAWED = INPUT / "flawed-report.png"
ROWS = list(csv.DictReader(SOURCE.open(encoding="utf-8")))
DATA = []
for index, row in enumerate(ROWS):
    revenue = int(row["revenue_wan"])
    cost = int(row["cost_wan"])
    item = {"quarter": row["quarter"], "revenue": revenue, "cost": cost, "profit": revenue - cost}
    item["profit_margin_percent"] = round(item["profit"] / revenue * 100, 2)
    item["revenue_change"] = None if index == 0 else revenue - DATA[-1]["revenue"]
    item["cost_change"] = None if index == 0 else cost - DATA[-1]["cost"]
    item["profit_change"] = None if index == 0 else item["profit"] - DATA[-1]["profit"]
    DATA.append(item)

NAVY = "#18283F"
BLUE = "#245CE4"
ORANGE = "#E88E35"
GREEN = "#168267"
MUTED = "#63748F"
BORDER = "#DFE6F0"
GRID = "#E5E7EB"
BG = "#F4F7FB"
CARD = "#FFFFFF"
CHART_CARD = (56, 170, 824, 580)
PLOT = {"left": 90, "right": 772, "top": 108, "bottom": 450, "minimum": 0, "maximum": 200,
        "ticks": [0, 50, 100, 150, 200], "pixels_per_wan": 1.71}
CENTERS = [170, 340, 510, 680]
for quarter, center in zip(DATA, CENTERS):
    for series, offset, color in (("revenue", -61, BLUE), ("cost", 7, ORANGE)):
        left = center + offset
        top = PLOT["bottom"] - quarter[series] * PLOT["pixels_per_wan"]
        quarter[series + "_local_rect"] = [left, top, left + 54, PLOT["bottom"]]
        quarter[series + "_rect"] = [CHART_CARD[0] + left, CHART_CARD[1] + top,
                                     CHART_CARD[0] + left + 54, CHART_CARD[1] + PLOT["bottom"]]
        quarter[series + "_color"] = color

ANNOTATION_TEXTS = {"收入", "成本", "0", "50", "100", "150", "200", "季度", "收入", "成本", "利润",
                    "数据来源：source.csv · 利润=收入−成本 · 共同零起点"}
ANNOTATION_TEXTS.update(str(value) for item in DATA for value in (item["revenue"], item["cost"]))
ANNOTATION_TEXTS.update(f'利润 {item["profit"]}' for item in DATA)
ANNOTATION_TEXTS.update({"收入 180 − 成本 126", "结论"})

FINDINGS = [
    {"id": "F01", "category": "series_encoding", "image_location": "图表右上图例；四组柱顶标签",
     "observed_phenomenon": "图例把蓝色标为“成本”、橙色标为“收入”，但蓝色柱标签为 120/135/128/180，橙色为 90/108/96/126。",
     "source_data_check": "source.csv 的 revenue_wan=120/135/128/180，cost_wan=90/108/96/126；原图标签数值本身与 CSV 一致，但图例角色倒置。",
     "impact": "读者会把收入与成本读反，并误判利润和利润率。",
     "correction": "明确蓝色=收入、橙色=成本，图例、柱顶数值和明细表使用同一编码。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/flawed-chart-2x.png"}},
    {"id": "F02", "category": "axis_baseline", "image_location": "图表纵轴与全部柱体基线",
     "observed_phenomenon": "纵轴最低刻度为 100，八根柱都从 100 刻度所在基线起画，而不是金额零起点。",
     "source_data_check": "CSV 给出的是绝对金额（万元）；柱图比较绝对值时应从 0 起画，没有排除 0–100 的领域依据。",
     "impact": "截断基线夸大柱间差异，也使 90 万元成本在视觉上失去正确的零起点含义。",
     "correction": "改用共同零起点、0–200 万元轴和 50 万元刻度。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/flawed-chart-2x.png"}},
    {"id": "F03", "category": "narrative_conclusion", "image_location": "主标题与右下“重点观察·Q3”卡片",
     "observed_phenomenon": "标题称“Q3利润最高”，重点观察建议把资源集中到 Q3；同图明细却显示 Q4 利润 54 万元。",
     "source_data_check": "按 CSV 计算利润=收入−成本：Q1=30、Q2=27、Q3=32、Q4=54；Q4 严格最高。",
     "impact": "标题和资源建议指向错误季度，与图表及明细自相矛盾。",
     "correction": "标题、重点卡片和结论改为 Q4，并引用收入 180、成本 126、利润 54 万元。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/flawed-header-2x.png"}},
    {"id": "F04", "category": "trend_statement", "image_location": "主标题下方副标题",
     "observed_phenomenon": "副标题写“收入持续上升，全年保持增长”。",
     "source_data_check": "收入 Q2=135、Q3=128，环比减少 7 万元；只有 Q4=180 高于 Q3。",
     "impact": "趋势叙述与数据和柱图矛盾，掩盖 Q3 回落。",
     "correction": "改为“Q3 收入较 Q2 回落 7 万元；Q4 收入与利润均最高”。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/flawed-header-2x.png"}},
    {"id": "F05", "category": "arithmetic", "image_location": "下方“利润明细”的 Q3 单元格",
     "observed_phenomenon": "Q3 利润印为 42 万元。",
     "source_data_check": "CSV 的 Q3 收入 128、成本 96，因此利润=128−96=32 万元，不是 42。",
     "impact": "明细算术错误，并错误支撑 Q3 利润最高的叙事。",
     "correction": "Q3 利润改为 32 万元；四季度均直接由 CSV 计算。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/flawed-details-2x.png"}},
    {"id": "F06", "category": "plot_coverage", "image_location": "图表网格右端与 Q4 柱组",
     "observed_phenomenon": "六条水平网格线右端为 x≈899，而 Q4 蓝/橙柱分别位于 x=932–996、1008–1072，整组在轴网格覆盖范围之外。",
     "source_data_check": "Q4 收入 180、成本 126 是有效数据，不应因布局而失去上方和横向网格参照。",
     "impact": "Q4 数值缺少对应网格参照，图表阅读路径在最关键季度中断。",
     "correction": "重排四组等距柱，并把网格延伸到全部柱组右侧。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/measurement.json"}},
    {"id": "F07", "category": "bar_geometry", "image_location": "八根柱顶与纵轴刻度",
     "observed_phenomenon": "按原图 20 万元=54px 的网格比例反推，柱顶与标签普遍不符；例如 Q1 蓝柱顶对应约 155.56 万元而标签为 120，Q3 橙柱顶对应约 147.41 万元而标签为 96。",
     "source_data_check": "CSV 是唯一可信数值；八根柱的理论顶位应为 y=565−(标签值−100)×2.7。实测八根柱均偏离该位置。",
     "impact": "即使只读纵轴也会得到错误金额，柱高并未真实表达标签数值。",
     "correction": "八根柱均按 source.csv 数值和同一 1.71px/万元比例重新计算高度，不只改标签。",
     "evidence": {"path_base": "suite_root", "path": "tmp/20261124T113838+0800-aac601/A16/flawed-inspection/measurement.json"}},
]
UNCERTAINTIES = [
    {"id": "U01", "matter": "原图柱高失真和布局错位的生成原因", "reason": "输入不包含旧 DSL 或生成代码，无法确认是手工调整还是布局计算错误。",
     "needed_evidence": "若需归因，需要旧 DSL 或生成脚本；当前修正不依赖该原因，CSV 与可测图像已足以确认并修复问题。"}
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rp(path, base=ROOT):
    return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()


def cdata(value):
    return "<![CDATA[" + value.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def txt(value, size=22, color=NAVY, bold=False, align="LEFT"):
    style = "BOLD" if bold else "NORMAL"
    alignment = "" if align == "LEFT" else f' textAlign="{align}"'
    return f'<Text fontFamily="{sk.FONT}" fontSize="{size}" color="{color}" fontStyle="{style}"{alignment} maxLines="1"><Raw>{cdata(str(value))}</Raw></Text>'


def put(x, y, w, h, child):
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">{child}</Positioned>'


def box(x, y, w, h, color, radius=0, child=""):
    return put(x, y, w, h, f'<Container width="{w}" height="{h}" color="{color}" borderRadius="{radius}">{child}</Container>')


def line(x1, y1, x2, y2, color=GRID, thickness=1):
    import math
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    return put(x1, y1, length, thickness,
               f'<Container width="{length}" height="{thickness}" color="{color}" transform="rotate({angle}deg)" transformAlignment="CENTER_LEFT"/>')


def card(x, y, w, h, children):
    content = f'<Container width="{w}" height="{h}" color="{CARD}" border="1 {BORDER}" borderRadius="14"><Stack clipBehavior="NONE">{"".join(children)}</Stack></Container>'
    return put(x, y, w, h, content)


def generate():
    children = [box(0, 0, 1280, 900, BG),
                put(56, 38, 1120, 54, txt("季度复盘：Q4 收入与利润均最高", 38, NAVY, True)),
                put(56, 102, 1120, 36, txt("Q3 收入较 Q2 回落 7 万元；Q4 利润较 Q3 增加 22 万元", 24, MUTED)),
                box(56, 150, 92, 5, BLUE)]
    chart = [put(28, 22, 410, 34, txt("收入与成本（万元）", 22, NAVY, True)),
             box(548, 27, 18, 18, BLUE, 3), put(576, 21, 82, 30, txt("收入", 20, NAVY)),
             box(666, 27, 18, 18, ORANGE, 3), put(694, 21, 82, 30, txt("成本", 20, NAVY))]
    for tick in PLOT["ticks"]:
        y = PLOT["bottom"] - tick * PLOT["pixels_per_wan"]
        chart.append(line(PLOT["left"], y, PLOT["right"], y))
        chart.append(put(22, y - 14, 52, 28, txt(str(tick), 18, MUTED, align="RIGHT")))
    chart.append(line(PLOT["left"], PLOT["top"], PLOT["left"], PLOT["bottom"], MUTED, 2))
    for item, center in zip(DATA, CENTERS):
        for series in ("revenue", "cost"):
            left, top, right, bottom = item[series + "_local_rect"]
            color = item[series + "_color"]
            chart.append(box(left, top, right - left, bottom - top, color, 4))
            chart.append(put(left - 8, top - 28, 70, 26, txt(item[series], 18, color, True, "CENTER")))
        chart.append(put(center - 75, 468, 150, 32, txt(item["quarter"], 22, NAVY, True, "CENTER")))
        chart.append(put(center - 75, 504, 150, 28, txt(f'利润 {item["profit"]}', 20, GREEN, True, "CENTER")))
    children.append(card(*CHART_CARD, chart))

    focus = [put(24, 22, 272, 30, txt("重点观察", 22, MUTED, True)),
             put(24, 60, 272, 54, txt("Q4", 44, BLUE, True)),
             put(24, 122, 272, 38, txt("利润 54 万元", 26, GREEN, True)),
             put(24, 166, 272, 30, txt("收入 180 − 成本 126", 20, NAVY))]
    children.append(card(904, 170, 320, 220, focus))

    details = [put(24, 22, 272, 32, txt("季度明细 · 万元", 22, NAVY, True)),
               put(24, 70, 52, 26, txt("季度", 18, MUTED, True)),
               put(86, 70, 58, 26, txt("收入", 18, MUTED, True, "CENTER")),
               put(152, 70, 58, 26, txt("成本", 18, MUTED, True, "CENTER")),
               put(218, 70, 58, 26, txt("利润", 18, MUTED, True, "CENTER")),
               line(24, 104, 296, 104)]
    for index, item in enumerate(DATA):
        y = 118 + index * 48
        if item["quarter"] == "Q4":
            details.append(box(16, y - 8, 288, 42, "#EAF1FF", 8))
        color = BLUE if item["quarter"] == "Q4" else NAVY
        details.extend([put(24, y, 52, 30, txt(item["quarter"], 22, color, True)),
                        put(86, y, 58, 30, txt(item["revenue"], 22, color, item["quarter"] == "Q4", "CENTER")),
                        put(152, y, 58, 30, txt(item["cost"], 22, color, item["quarter"] == "Q4", "CENTER")),
                        put(218, y, 58, 30, txt(item["profit"], 22, GREEN, True, "CENTER"))])
    children.append(card(904, 410, 320, 340, details))

    children.extend([card(56, 774, 1168, 84, [
        put(24, 14, 64, 28, txt("结论", 18, MUTED, True)),
        put(100, 10, 1040, 34, txt("Q4 收入 180 万元、利润 54 万元，均为四季最高。", 24, NAVY, True)),
        put(100, 46, 1040, 30, txt("Q3 是唯一收入环比回落季度；Q4 利润较 Q3 增加 22 万元。", 22, MUTED))]),
        put(56, 872, 1168, 24, txt("数据来源：source.csv · 利润=收入−成本 · 共同零起点", 18, MUTED))])
    return sk.snapshot(1280, 900, children, BG)


def static_validate(dsl):
    errors = []
    root = ET.fromstring(dsl)
    if root.tag != "Snapshot":
        errors.append("root")
    texts = ["".join(element.itertext()) for element in root.iter("Text")]
    required = ["季度复盘：Q4 收入与利润均最高", "收入与成本（万元）", "Q4", "利润 54 万元", "季度明细 · 万元",
                "Q3 是唯一收入环比回落季度；Q4 利润较 Q3 增加 22 万元。", "数据来源：source.csv · 利润=收入−成本 · 共同零起点"]
    for value in required:
        if value not in texts:
            errors.append("missing text " + value)
    for item in DATA:
        for value in (item["quarter"], str(item["revenue"]), str(item["cost"]), str(item["profit"]), f'利润 {item["profit"]}'):
            if value not in texts:
                errors.append("missing data " + value)
    for element in root.iter("Text"):
        value = "".join(element.itertext())
        size = float(element.attrib["fontSize"])
        minimum = 18 if value in ANNOTATION_TEXTS else 22
        if size < minimum:
            errors.append(f"font size {value}={size}")
        if element.find("Raw") is None:
            errors.append("text not Raw " + value)
    if len(list(root.iter("Image"))):
        errors.append("external image")
    for item in DATA:
        for series in ("revenue", "cost"):
            rect = item[series + "_rect"]
            if abs(rect[3] - (CHART_CARD[1] + PLOT["bottom"])) > 1e-9:
                errors.append("nonzero baseline")
            if abs((rect[3] - rect[1]) - item[series] * PLOT["pixels_per_wan"]) > 1e-9:
                errors.append("bar height")
    if [item["profit"] for item in DATA] != [30, 27, 32, 54]:
        errors.append("profits")
    if max(DATA, key=lambda item: item["profit"])["quarter"] != "Q4":
        errors.append("focus quarter")
    return errors


def guard_execution():
    state = json.loads((ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[task_id] == "completed" for task_id in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK] in ("pending", "in_progress"), "A16 state"


def prepare():
    dsl = generate()
    errors = static_validate(dsl)
    (HERE / "corrected-report.snapshot").write_text(dsl, encoding="utf-8")
    sk.write_json(HERE / "preparation-manifest.json", {
        "task_id": TASK, "run_id": RUN, "mode": "preparation_only", "service_requests": 0,
        "source_sha256": sha(SOURCE), "flawed_sha256": sha(FLAWED), "data": DATA, "plot": PLOT,
        "findings": FINDINGS, "uncertainties": UNCERTAINTIES, "static_errors": errors,
    })
    if errors:
        raise SystemExit(json.dumps(errors, ensure_ascii=False))
    print(json.dumps({"prepared": rp(HERE), "profits": [item["profit"] for item in DATA], "static_errors": errors}, ensure_ascii=False))


def execute():
    guard_execution()
    sk.begin_task(RUN, TASK)
    version = f'v{len(list((HERE / "versions").glob("v*"))) + 1:03d}'
    image, record = sk.render(RUN, TASK, generate(), "corrected-report", version, False,
                              "baseline" if version == "v001" else "visual")
    sk.write_json(HERE / "versions" / version / "review-required.json", {
        "task_id": TASK, "version": version, "image_sha256": sha(image), "request_id": record["request_id"],
        "observed": "REPLACE after Read", "changes": "REPLACE", "compared": "flawed-report.png and source.csv",
        "completed": False,
    })
    print(json.dumps({"rendered": rp(image), "request_id": record["request_id"], "next": "Read actual PNG and inspection views"}, ensure_ascii=False))


def provenance(output):
    png = output / "corrected-report.png"
    dsl = output / "corrected-report.snapshot"
    png_hash = sha(png)
    dsl_hash = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for record in sk.read_jsonl(HERE / "requests.jsonl"):
        if record.get("request_type") != "render" or record.get("http_status") != 200:
            continue
        response = ROOT / record["response_file"]
        request = ROOT / record["request_file"]
        if response.is_file() and request.is_file() and sha(response) == png_hash and hashlib.sha256(request.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_hash:
            return {"request_id": record["request_id"], "request_file": record["request_file"], "response_file": record["response_file"],
                    "http_status": record["http_status"], "content_type": record["content_type"], "png_sha256": png_hash,
                    "dsl_sha256": sha(dsl), "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True}
    return None


def component_bbox(image, color, region):
    from PIL import Image
    im = Image.open(image).convert("RGBA") if not isinstance(image, Image.Image) else image
    target = tuple(bytes.fromhex(color.lstrip("#")))
    x0, y0, x1, y1 = region
    points = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if im.getpixel((x, y))[:3] == target]
    return [min(x for x, y in points), min(y for x, y in points), max(x for x, y in points) + 1, max(y for x, y in points) + 1] if points else None


def final_measurement(output, version):
    from PIL import Image
    image_path = Path(output) if Path(output).is_file() else Path(output) / "corrected-report.png"
    image = Image.open(image_path).convert("RGBA")
    if image.size != (1280, 900):
        raise ValueError("A16 size")
    bars = []
    for item in DATA:
        for series in ("revenue", "cost"):
            expected = item[series + "_rect"]
            region = (int(expected[0]) - 5, int(expected[1]) - 5, int(expected[2]) + 5, int(expected[3]) + 5)
            actual = component_bbox(image, item[series + "_color"], region)
            if actual is None:
                raise ValueError("missing bar " + item["quarter"] + series)
            diffs = [abs(x - y) for x, y in zip(actual, expected)]
            bars.append({"quarter": item["quarter"], "series": series, "value": item[series], "expected_rect": expected,
                         "measured_rect": actual, "component_errors": diffs, "max_abs_error": max(diffs),
                         "height": actual[3] - actual[1], "expected_height": expected[3] - expected[1]})
    grid = []
    for tick in PLOT["ticks"]:
        expected_y = CHART_CARD[1] + PLOT["bottom"] - tick * PLOT["pixels_per_wan"]
        rows = []
        grid_colors = {tuple(bytes.fromhex(GRID.lstrip("#"))), (242, 243, 245)}
        for y in range(round(expected_y) - 2, round(expected_y) + 3):
            xs = [x for x in range(CHART_CARD[0] + PLOT["left"] - 3, CHART_CARD[0] + PLOT["right"] + 4)
                  if image.getpixel((x, y))[:3] in grid_colors]
            if xs:
                rows.append((len(xs), y, min(xs), max(xs)))
        if not rows:
            raise ValueError("missing grid tick " + str(tick))
        count, y, left, right = max(rows)
        grid.append({"tick": tick, "expected_y": expected_y, "y": y, "left": left, "right": right, "visible_pixels": count})
    return {"size": [1280, 900], "bars": bars, "grid": grid,
            "all_bars_within_1px": all(item["max_abs_error"] <= 1 for item in bars),
            "common_zero_y": CHART_CARD[1] + PLOT["bottom"]}


def validate_final(output):
    errors = []
    dsl = (output / "corrected-report.snapshot").read_text(encoding="utf-8")
    errors.extend(static_validate(dsl))
    findings = json.loads((output / "findings.json").read_text(encoding="utf-8"))
    if findings.get("schema_version") != 1 or findings.get("task_id") != TASK or findings.get("path_base") != "output_dir":
        errors.append("findings header")
    if len(findings.get("findings", [])) != 7:
        errors.append("findings count")
    for item in findings.get("findings", []):
        for field in ("id", "category", "image_location", "observed_phenomenon", "source_data_check", "impact", "correction", "final_visual_result", "evidence"):
            if not item.get(field) or "pending" in str(item.get(field)).lower():
                errors.append("finding field " + item.get("id", "?") + " " + field)
    if not findings.get("uncertainties"):
        errors.append("uncertainty record")
    corrected = json.loads((output / "corrected-data.json").read_text(encoding="utf-8"))
    if [item["profit"] for item in corrected.get("quarters", [])] != [30, 27, 32, 54]:
        errors.append("corrected profits")
    if corrected.get("axes", {}).get("common_zero_y") != 620 or corrected.get("axes", {}).get("minimum") != 0:
        errors.append("axis definition")
    if len(corrected.get("axes", {}).get("bars", [])) != 8:
        errors.append("axis bars")
    if not corrected.get("provenance", {}).get("png_byte_identical_to_response"):
        errors.append("provenance")
    measurement = final_measurement(output, "final")
    if not measurement["all_bars_within_1px"]:
        errors.append("measured bar geometry")
    if not corrected.get("visual_review", {}).get("actually_viewed"):
        errors.append("final visual review")
    return errors


def review(version, review_file):
    output, _ = sk.task_dirs(RUN, TASK)
    data = json.loads(Path(review_file).read_text(encoding="utf-8"))
    source = HERE / "versions" / version
    image = source / "corrected-report-01.png"
    if data.get("task_id") != TASK or data.get("version") != version or data.get("image_sha256") != sha(image):
        raise SystemExit("review identity/hash mismatch")
    if "REPLACE" in data.get("observed", "") or not data.get("completed"):
        raise SystemExit("actual completed review required")
    sk.record_iteration(RUN, TASK, version, image, "baseline" if version == "v001" else "visual",
                        data["observed"], data["changes"], data["compared"], True)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(image, output / "corrected-report.png")
    shutil.copyfile(source / "corrected-report.snapshot", output / "corrected-report.snapshot")
    source_provenance = provenance(output)
    if source_provenance is None:
        raise SystemExit("service provenance mismatch")
    findings = json.loads(json.dumps(FINDINGS))
    for item in findings:
        item["final_visual_result"] = data["observed"]
    sk.write_json(output / "findings.json", {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "inputs": {"flawed_report": {"path_base": "suite_root", "path": rp(FLAWED)},
                   "source_csv": {"path_base": "suite_root", "path": rp(SOURCE)}},
        "method": "先实际查看原图，再以 source.csv 复算，并用原图像素/网格位置核对柱高；审美偏好未列为数值错误。",
        "findings": findings, "uncertainties": UNCERTAINTIES,
        "visual_review": {"actually_viewed": True, "final_image": "corrected-report.png", "observed": data["observed"]},
    })
    bars = []
    for item in DATA:
        for series in ("revenue", "cost"):
            rect = item[series + "_rect"]
            bars.append({"quarter": item["quarter"], "series": series, "value": item[series], "unit": "万元",
                         "canvas_rect": rect, "chart_local_rect": item[series + "_local_rect"],
                         "height_pixels": rect[3] - rect[1], "color": item[series + "_color"]})
    sk.write_json(output / "corrected-data.json", {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "source": {"path_base": "suite_root", "path": rp(SOURCE)}, "source_sha256": sha(SOURCE), "unit": "万元",
        "formula": "profit = revenue_wan - cost_wan", "quarters": DATA,
        "axes": {"coordinate_system": "canvas top-left pixels", "chart_card_origin": [CHART_CARD[0], CHART_CARD[1]],
                 "common_zero_y": CHART_CARD[1] + PLOT["bottom"], "minimum": 0, "maximum": 200,
                 "ticks": PLOT["ticks"], "pixels_per_wan": PLOT["pixels_per_wan"],
                 "formula": "top_y = chart_card_y + 450 - value * 1.71", "bars": bars},
        "conclusion": {"headline": "季度复盘：Q4 收入与利润均最高", "focus_quarter": "Q4",
                       "highest_revenue": {"quarter": "Q4", "field": "revenue_wan", "value": 180},
                       "highest_profit": {"quarter": "Q4", "field": "profit", "value": 54},
                       "q3_revenue_change_vs_q2": {"value": -7, "calculation": "128-135"},
                       "q4_profit_change_vs_q3": {"value": 22, "calculation": "54-32"},
                       "q4_profit_margin_percent": 30.0, "evidence": "Q4: 180-126=54; Q3 revenue: 128-135=-7; Q4 profit change: 54-32=22"},
        "visual_review": {"actually_viewed": True, "observed": data["observed"], "compared": data["compared"]},
        "provenance": source_provenance,
    })
    measurement = final_measurement(output, version)
    sk.write_json(HERE / "final-inspection" / version / "final-measurement.json", measurement)
    errors = validate_final(output)
    if errors:
        raise SystemExit("final validation failed: " + json.dumps(errors, ensure_ascii=False))
    sk.write_usage(RUN, TASK, "completed", [
        ("source calculation", "利润 30/27/32/54；Q4 收入 180、利润 54 均最高；Q3 收入环比 −7；Q4 利润环比 +22"),
        ("chart geometry", "八根柱共同零起点 y=620，0–200 万元，1.71px/万元；实测每柱分量误差≤1px"),
        ("findings", "7 项已确认问题分别记录位置、现象、CSV 核对、影响、修正和最终查看结果；生成原因不确定性单列"),
        ("visual review", data["observed"]),
        ("provenance", "最终 PNG 与成功服务响应字节相同，DSL 与提交 UTF-8 请求一致；无外部图像"),
    ], "四季分组柱使用同一零起点和比例；蓝色收入、橙色成本；Q4 由最高收入、最高利润和 30% 利润率共同论证。正文≥22、标注≥18。",
       data["changes"], [rp(path) for path in sorted(output.iterdir()) if path.is_file()])
    sk.metrics(RUN, TASK)
    artifacts = [rp(path) for path in sorted(output.iterdir()) if path.is_file()]
    sk.finish_task(RUN, TASK, artifacts, [rp(HERE / "iterations.jsonl"), rp(HERE / "final-inspection" / version / "final-measurement.json")], issues=[])
    sk.metrics(RUN, TASK)
    print(json.dumps({"completed": TASK, "artifacts": artifacts, "max_bar_error": max(item["max_abs_error"] for item in measurement["bars"])}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "validate", "execute", "review"])
    parser.add_argument("--version")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    elif args.mode == "execute":
        execute()
    elif args.mode == "review":
        review(args.version, args.review_file)
    else:
        print(json.dumps({"static_errors": static_validate((HERE / "corrected-report.snapshot").read_text(encoding="utf-8"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
