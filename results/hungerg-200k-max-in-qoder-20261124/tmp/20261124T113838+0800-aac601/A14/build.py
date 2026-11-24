#!/usr/bin/env python3
"""A14 data-driven eight-card batch generator and deferred execution CLI.

Default `prepare` is offline. Later `render` requires A14 to be in_progress and
all previous tasks completed. Every service image must actually be opened with
Read and reviewed before `finalize`; a contact sheet is never substituted.
"""
from __future__ import annotations
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s
from PIL import Image

RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A14"
OUT, TEMP = s.task_dirs(RUN, TASK)
CARDS = json.loads((ROOT / "tasks/A14-content-stress-batch/inputs/cards.json").read_text(encoding="utf-8"))
FONT = "Noto Sans CJK SC"
assert FONT in (ROOT / "tmp" / RUN / "_suite/shared/fonts.txt").read_text(encoding="utf-8").splitlines()
C = {"paper": "#F5F7FC", "surface": "#FFFFFF", "ink": "#172033", "muted": "#59677D", "primary": "#3049A8", "line": "#D7DFEA"}
STATUS = {"开放": {"symbol": "●", "color": "#15803D", "bg": "#E8F5EC"},
          "满额": {"symbol": "■", "color": "#9A5B00", "bg": "#FFF3D9"},
          "候补": {"symbol": "◆", "color": "#3059A8", "bg": "#E9F0FF"},
          "取消": {"symbol": "×", "color": "#B42332", "bg": "#FDECEF"}}
SIZE = (1200, 630)


def text(value, size, color=C["ink"], bold=False, align="LEFT"):
    assert "]]>" not in value
    return (f'<Text fontFamily="{FONT}" fontSize="{size:g}" color="{color}" textAlign="{align}" '
            f'fontStyle="{"BOLD" if bold else "NORMAL"}" softWrap="true" height="1.2"><Raw><![CDATA[{value}]]></Raw></Text>')


def label(value, x, y, w, h, size, color=C["ink"], bold=False, align="LEFT"):
    return s.positioned(x, y, w, h, text(value, size, color, bold, align))


def units(value):
    total = 0
    for ch in value:
        if ch.isspace():
            total += 1
        elif ord(ch) > 127:
            total += 2
        else:
            total += 1
    return total


def wrap_preserving(value, width, size, max_lines):
    """Balance measured lines without dropping or altering source characters."""
    from functools import lru_cache

    limit = max(1, int(2 * width / size))
    connector_endings = set("的与和到及或")
    punctuation_endings = set("：，、。？！；—")

    @lru_cache(maxsize=None)
    def solve(start):
        if start == len(value):
            return 0.0, ()
        best = None
        for end in range(start + 1, len(value) + 1):
            piece = value[start:end]
            used = units(piece)
            if used > limit:
                break
            remaining = solve(end)
            if remaining is None:
                continue
            slack = limit - used
            cost = 100000.0 + slack * slack
            if end == len(value) and used < limit * .4:
                cost += (limit * .4 - used) ** 2 * 10
            if end < len(value):
                previous, following = value[end - 1], value[end]
                if previous in connector_endings:
                    cost += 3000
                if previous.isalnum() and following.isalnum() and previous.isascii() and following.isascii():
                    cost += 8000
                if previous in punctuation_endings:
                    cost -= 500
                if previous == "—" and following == "—":
                    cost += 8000
                if following in "—，。、？！；：）》”":
                    cost += 4000
            candidate = (cost + remaining[0], (piece,) + remaining[1])
            if best is None or candidate[0] < best[0]:
                best = candidate
        return best

    result = solve(0)
    assert result is not None and 1 <= len(result[1]) <= max_lines, f"content does not fit {max_lines} lines: {value}"
    wrapped = "\n".join(result[1])
    assert wrapped.replace("\n", "") == value
    return wrapped, len(result[1])


def title_plan(item):
    measure = units(item["title"])
    size = 56 if measure <= 28 else (50 if measure <= 52 else 46)
    actual, count = wrap_preserving(item["title"], 1120, size, 3)
    assert size >= 36 and count <= 3
    branch = "compact" if size == 56 else ("standard" if size == 50 else "long")
    return {"source": item["title"], "actual": actual, "font_size": size, "line_count": count,
            "branch": branch, "measured_units": measure, "box": [40, 154, 1160, 354]}


def build_card(item):
    plan = title_plan(item)
    speaker_actual, speaker_lines = wrap_preserving(item["speaker"], 720, 26, 2)
    status = STATUS[item["status"]]
    status_text = f'{status["symbol"]} {item["status"]}'
    children = [s.box(0, 0, 1200, 630, C["paper"]), s.box(0, 0, 18, 630, C["primary"]),
                s.box(40, 40, 8, 64, C["primary"], 4),
                label("Structure / Vision", 64, 38, 620, 36, 26, C["primary"], True),
                label("2026.11.07", 64, 82, 620, 32, 22, C["muted"]),
                s.box(940, 42, 220, 64, status["bg"], 16),
                label(status_text, 956, 54, 188, 38, 24, status["color"], True, "CENTER"),
                label(plan["actual"], 40, 154, 1120, 200, plan["font_size"], C["ink"], True),
                s.line(40, 374, 1160, 374, C["line"], 2),
                s.box(40, 408, 6, 86, status["color"], 3),
                label("讲者 / SPEAKER", 64, 402, 650, 30, 20, C["muted"], True),
                label(speaker_actual, 64, 438, 720, 68, 26, C["ink"], True),
                label("TIME", 872, 402, 288, 30, 20, C["muted"], True, "RIGHT"),
                label(item["time"], 872, 438, 288, 58, 40, C["primary"], True, "RIGHT")]
    if item["status"] == "取消":
        children.append(label("本场取消", 64, 532, 600, 34, 24, status["color"], True))
    dsl = s.snapshot(1200, 630, children, C["paper"])
    audit = {"id": item["id"], "png": f"card-{item['id']}.png", "dsl": f"card-{item['id']}.snapshot",
             "content": {**item, "title_actual": plan["actual"], "speaker_actual": speaker_actual,
                         "status_actual": status_text, "cancel_note": "本场取消" if item["status"] == "取消" else None},
             "title": {"font_size_px": plan["font_size"], "line_count": plan["line_count"], "box_px": plan["box"],
                       "branch": plan["branch"], "measured_units": plan["measured_units"], "max_lines": 3},
             "speaker": {"font_size_px": 26, "line_count": speaker_lines, "box_px": [64, 438, 784, 506], "max_lines": 2},
             "status": {"source": item["status"], "text": status_text, "symbol": status["symbol"], "color": status["color"],
                        "background": status["bg"], "badge_box_px": [940, 42, 1160, 106], "encoding": "color + symbol + exact status text"},
             "time": {"text": item["time"], "box_px": [872, 438, 1160, 496], "font_size_px": 40},
             "safe_margin_px": 40, "title_status_collision": False}
    return dsl, audit


def build_all():
    assert [x["id"] for x in CARDS] == [f"K{i:02d}" for i in range(1, 9)]
    result = []
    for item in CARDS:
        dsl, audit = build_card(item)
        root = ET.fromstring(dsl)
        assert not any(x.tag == "Image" for x in root.iter())
        assert "&lt;" not in dsl and "&gt;" not in dsl and "&amp;" not in dsl
        assert audit["title"]["font_size_px"] >= 36 and audit["title"]["line_count"] <= 3
        assert audit["speaker"]["font_size_px"] >= 22 and audit["speaker"]["line_count"] <= 2
        assert audit["status"]["badge_box_px"][3] < audit["title"]["box_px"][1]
        assert all(40 <= audit[k]["box_px"][0] and audit[k]["box_px"][2] <= 1160 for k in ("title", "speaker", "time"))
        result.append((item, dsl, audit))
    return result


def guard_execution():
    state = json.loads((ROOT / s.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [x["id"] for x in s.CATALOG["tasks"]]
    statuses = {x["id"]: x["status"] for x in state["tasks"]}
    assert all(statuses[x] == "completed" for x in order[:order.index(TASK)]), "strict task order: earlier tasks are incomplete"
    assert statuses[TASK] == "in_progress", "A14 must already be begun by the suite executor"


def active_version():
    p = TEMP / "active-version.json"
    return json.loads(p.read_text(encoding="utf-8"))["version"] if p.exists() else None


def render(version):
    guard_execution()
    for item, dsl, audit in build_all():
        stem = f"card-{item['id']}"
        image, record = s.render(RUN, TASK, dsl, stem, version, final=True, kind="baseline", case_id=item["id"])
        with Image.open(image) as im: assert im.size == SIZE and im.format == "PNG"
        print(stem, s.rel(image), record["http_status"])
    s.write_json(TEMP / "active-version.json", {"task_id": TASK, "version": version, "rendered_at": s.iso()})


def resolve_image(value):
    p = Path(value); p = (p if p.is_absolute() else ROOT / p).resolve()
    assert p.is_file() and TEMP.resolve() in p.parents
    return p


def review(stem, version, image, observed, changes, compared, accept, kind="baseline"):
    p = resolve_image(image)
    case_id = stem.removeprefix("card-")
    s.record_iteration(RUN, TASK, version, p, kind, observed, changes, compared, completed=accept, case_id=case_id)
    s.append_jsonl(TEMP / "reviews.jsonl", dict(stem=stem, version=version, image_path=s.rel(p), case_id=case_id, kind=kind,
                    observed=observed, changes=changes, compared=compared, accepted=accept, recorded_at=s.iso(), viewer="Read"))


def accepted(version):
    return {x["stem"]: x for x in s.read_jsonl(TEMP / "reviews.jsonl") if x["version"] == version and x["accepted"]}


def finalize():
    guard_execution(); version = active_version(); assert version
    current = accepted(version); built = build_all()
    stems = {f"card-{item['id']}" for item, _, _ in built}
    assert set(current) == stems, "every one of the eight current service images needs an accepted actual Read review"
    cards = []
    for item, dsl, audit in built:
        stem = f"card-{item['id']}"; source = resolve_image(current[stem]["image_path"])
        final = OUT / f"{stem}.png"; assert final.read_bytes() == source.read_bytes()
        with Image.open(final) as im: assert im.size == SIZE and im.format == "PNG"
        audit["review"] = current[stem]
        cards.append(audit)
    generation = {"script": {"path_base": "suite_root", "path": s.rel(Path(__file__).resolve())},
                  "data": {"path_base": "suite_root", "path": s.rel(ROOT / "tasks/A14-content-stress-batch/inputs/cards.json")},
                  "canvas_px": list(SIZE), "safe_margin_px": 40, "primary_color": C["primary"], "font_family": FONT,
                  "shared": {"brand": "Structure / Vision", "date": "2026.11.07", "title_box_px": [40, 154, 1160, 354], "status_box_px": [940, 42, 1160, 106]},
                  "branches": [{"condition": "measured title units <=28", "title_font_px": 56, "name": "compact"},
                               {"condition": "29..52 measured title units", "title_font_px": 50, "name": "standard"},
                               {"condition": ">52 measured title units", "title_font_px": 46, "name": "long"}],
                  "wrapping": "conservative units count each non-ASCII character as 2 and ASCII as 1; dynamic programming minimizes line slack, penalizes very short final lines, connector endings, split words and separated punctuation pairs; inserts newlines only; source recovered by removing newlines; <=3 title lines and <=2 speaker lines",
                  "status_system": STATUS, "per_item_hardcoded_edits": False}
    batch = {**s.audit_identity(TASK), "generation": generation, "cards": cards,
             "reviews": [{"id": item["id"], **current[f"card-{item['id']}"]} for item in CARDS],
             "checks": [{"check": "eight_complete_cards", "passed": True, "method": "K01-K08 from input; all title/speaker/time/status source strings retained; only wrapping newlines added"},
                        {"check": "font_and_lines", "passed": True, "method": "title 46/50/56px and <=3 lines; speaker 26px and <=2 lines"},
                        {"check": "status_and_cancel", "passed": True, "method": "color + symbol + exact text; K06 additionally displays 本场取消 with full title/time"},
                        {"check": "geometry", "passed": True, "method": "40px content margins; status badge bottom 106 < title top 154; no global scaling"},
                        {"check": "visual_review", "passed": True, "method": "eight individual accepted Read reviews; no contact-sheet substitution", "evidence": [current[x]["image_path"] for x in sorted(stems)]}]}
    s.write_json(OUT / "batch-audit.json", batch)
    files = [f"card-K{i:02d}.{ext}" for i in range(1, 9) for ext in ("png", "snapshot")] + ["batch-audit.json", "snapshot-usage.md", "task-metrics.json"]
    s.write_usage(RUN, TASK, "completed", [
        ("八张参数化生成", "通过；K01–K08全部从cards.json生成，1200×630；无逐条硬改输入；长度仅触发56/50/46px标题分支和换行。"),
        ("内容完整性", "通过；标题、讲者、时间、状态原文字保留；换行只插入不删字符；K04尖括号与&通过Raw/CDATA原样显示。"),
        ("排版约束", "通过；标题≥36且≤3行，讲者26且≤2行；标题与状态徽标分区不碰撞；内容安全边距40，无整图缩小。"),
        ("状态体系", "通过；颜色+符号+文字共同区分开放/满额/候补/取消；取消卡另显示本场取消且保留完整标题与时间。"),
        ("实际看图", "通过；八张当前版本服务原图逐一Read并记录observed/changes/compared；接触表未替代单图检查。"),
        ("视觉修复", "通过；v001实际查看发现K03末行单字级、K08弯引号宽度低估；改为非ASCII字符统一2单位、动态规划平衡换行并惩罚短末行/断词/标点拆对。v002八张重新查看，K03在冒号后换行、K07在破折号后换行、K08在冒号后换行，原文均未改。")],
        "统一靛蓝主色、左侧色条、顶部品牌/日期和右侧状态徽标。标题按测量长度选择三档字号并显式换行，讲者和时间使用独立底部网格。",
        "准备阶段离线验证8份DSL、文本恢复、字号/行数和安全几何。执行阶段逐张查看；任何缺陷都另存版本、重新渲染并重新查看该卡。", files)
    s.finish_task(RUN, TASK, files, [s.rel(TEMP / "iterations.jsonl"), s.rel(TEMP / "reviews.jsonl")], [], cases=[x["id"] for x in CARDS])
    print(json.dumps(s.metrics(RUN, TASK), ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest="command")
    sub.add_parser("prepare")
    r = sub.add_parser("render"); r.add_argument("--version", default="v001")
    v = sub.add_parser("review"); v.add_argument("--stem", required=True); v.add_argument("--version", required=True); v.add_argument("--image", required=True)
    v.add_argument("--kind", choices=("baseline", "visual", "requirement-change"), default="baseline")
    v.add_argument("--observed", required=True); v.add_argument("--changes", required=True); v.add_argument("--compared", required=True); v.add_argument("--accept", action="store_true")
    sub.add_parser("finalize"); a = p.parse_args(); cmd = a.command or "prepare"
    if cmd == "prepare":
        print(json.dumps({"task": TASK, "mode": "offline_prepare", "run_id": RUN, "cards": [{"id": x["id"], "title_font_px": x["title"]["font_size_px"], "title_lines": x["title"]["line_count"], "speaker_lines": x["speaker"]["line_count"], "branch": x["title"]["branch"]} for _, _, x in build_all()], "service_requests": 0, "state_changed": False}, ensure_ascii=False, indent=2))
    elif cmd == "render": render(a.version)
    elif cmd == "review": review(a.stem, a.version, a.image, a.observed, a.changes, a.compared, a.accept, a.kind)
    elif cmd == "finalize": finalize()


if __name__ == "__main__": main()
