"""核对题面、交付清单、轮次和审计字段说明；仅读取 task-suite。"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

PACK = Path(__file__).resolve().parents[1] / "task-suite"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path.name}: 无法读取JSON：{exc}") from exc


def relative_name(value):
    return (isinstance(value, str) and bool(value)
            and "\\" not in value and ":" not in value
            and not PureWindowsPath(value).drive
            and not PurePosixPath(value).is_absolute()
            and ".." not in PurePosixPath(value).parts
            and "." != value)


def local_file(base, name, context):
    require(relative_name(name), f"{context} 路径非法：{name}")
    path = (base / name).resolve()
    require(path.is_relative_to(base.resolve()) and path.is_file(),
            f"{context} 引用失效：{name}")
    return path


def output_names(spec, context):
    images = spec.get("required_outputs", [])
    require(isinstance(images, list), f"{context} 图片清单须为数组")
    paths = []
    for item in images:
        require(isinstance(item, dict) and
                {"filename", "dsl", "width", "height"} <= item.keys(),
                f"{context} 图片条目字段缺失")
        require(type(item["width"]) is int and type(item["height"]) is int
                and item["width"] > 0 and item["height"] > 0,
                f"{context} 图片尺寸无效")
        paths += [item["filename"], item["dsl"]]
    for key in ["additional_outputs", "common_outputs"]:
        values = spec.get(key)
        require(isinstance(values, list), f"{context} {key}须为数组")
        paths += values
    require(all(relative_name(p) for p in paths), f"{context} 输出路径非法")
    require(len(paths) == len(set(paths)), f"{context} 输出清单重复")
    return paths


def image_table(prose, context):
    entries = []
    for row in prose.splitlines():
        if not row.lstrip().startswith("|") or ".png" not in row:
            continue
        tokens = re.findall(r"`([^`]+)`", row)
        png = [v for v in tokens if v.endswith(".png")]
        dsl = [v for v in tokens if v.endswith(".snapshot")]
        size = re.search(r"(\d+)\s*×\s*(\d+)", row)
        require(len(png) == len(dsl) == 1 and size is not None,
                f"{context} 图片表行缺失PNG/DSL或尺寸")
        entries.append((png[0], dsl[0], int(size[1]), int(size[2])))
    return entries


def mentioned(prose, name):
    return re.search(r"(?<![A-Za-z0-9_./-])" + re.escape(name)
                     + r"(?![A-Za-z0-9_./-])", prose) is not None


def validate_suite(pack=PACK):
    pack = Path(pack)
    catalog = load(pack / "catalog.json")
    require(isinstance(catalog.get("tasks"), list), "catalog.tasks须为数组")
    expected = [f"A{i:02}" for i in range(1, 25)] + [f"B{i:02}" for i in range(1, 7)]
    require([t.get("id") for t in catalog["tasks"]] == expected,
            "目录任务身份或顺序不一致")
    round_count, artifact_count = 0, 0
    for entry in catalog["tasks"]:
        task = entry["id"]
        spec_path = local_file(pack, entry.get("task_spec"), task)
        folder = spec_path.parent
        prose_path = local_file(pack, entry.get("entry"), task)
        require(prose_path.parent == folder
                and (pack / entry["directory"]).resolve() == folder.resolve(),
                f"{task} 入口目录不一致")
        spec = load(spec_path)
        prose = prose_path.read_text(encoding="utf-8-sig")
        require(spec.get("id") == task and spec.get("title") == entry.get("title")
                and spec["title"] in prose, f"{task} 身份或标题不同步")
        prompt = spec.get("prompt")
        require(isinstance(prompt, str) and bool(prompt.strip())
                and prompt.strip() in prose, f"{task} prompt与Markdown不同步")
        output_names(spec, task)
        if task.startswith("A"):
            expected_table = [(x["filename"], x["dsl"], x["width"], x["height"])
                              for x in spec.get("required_outputs", [])]
            require(Counter(image_table(prose, task)) == Counter(expected_table),
                    f"{task} 图片交付表与JSON不一致")
            require(len(expected_table) == entry["minimum_final_pngs"],
                    f"{task} 图片数量与目录不一致")
            if not spec.get("rounds"):
                declaration = re.search(r"^额外文件：(.*)$", prose, re.MULTILINE)
                declared = (re.findall(r"`([^`]+)`", declaration[1].split("。", 1)[0])
                            if declaration else [])
                require(Counter(declared) == Counter(spec["additional_outputs"]),
                        f"{task} 额外交付声明与JSON不一致")
            else:
                declared = []
                for row in prose.splitlines():
                    if row.startswith("|"):
                        declared += [p for p in re.findall(r"`([^`]+)`", row)
                                     if p.endswith((".json", ".md"))]
                require(Counter(declared) == Counter(
                    spec["additional_outputs"] + spec["common_outputs"]),
                    f"{task} 多轮审计交付表与JSON不一致")
        else:
            require(spec.get("minimum_independent_cases") == entry.get("minimum_independent_cases") == 10,
                    f"{task} 独立用例数量不一致")
            require(spec.get("case_artifacts") == ["final.png", "final.snapshot", "case.md"],
                    f"{task} 用例交付清单不一致")
            require(all(mentioned(prose, p) for p in spec["case_artifacts"]),
                    f"{task} 用例文件未在Markdown声明")
            portfolio = load(local_file(folder, "templates/portfolio-template.json", task))
            guide = portfolio.get("case_field_guide", {})
            require(all(guide.get(key) for key in
                        ["plan_version", "completion_criteria", "criteria_history", "criterion_results"]),
                    f"{task} 完成标准模板不完整")
        for name in spec["additional_outputs"] + spec["common_outputs"]:
            require(mentioned(prose, name), f"{task} Markdown遗漏交付文件：{name}")
        rounds = spec.get("rounds", [])
        if rounds:
            require(task in {"A21", "A22"} and spec.get("output_path_base") == "output_dir",
                    f"{task} 多轮路径基准不明确")
            require([r.get("round") for r in rounds] == [1, 2, 3], f"{task} 轮次不完整")
            for rnd in rounds:
                rid = rnd["round"]
                prefix = f"round-{rid:02}"
                require(rnd.get("output_subdirectory") == prefix, f"{task} 轮次目录不匹配")
                path = local_file(folder, rnd.get("requirements_file"), f"{task} 第{rid}轮")
                require(path.read_text(encoding="utf-8-sig").strip(), f"{task} 轮次要求为空")
                names = output_names(rnd, f"{task} 第{rid}轮")
                require(all(p.startswith(prefix + "/") and p.count("round-") == 1 for p in names),
                        f"{task} 第{rid}轮交付缺少唯一轮次前缀")
                require(all(mentioned(path.read_text(encoding="utf-8-sig"), p) for p in names),
                        f"{task} 第{rid}轮Markdown遗漏交付文件")
                round_count += 1
            for key in ["required_outputs", "additional_outputs", "common_outputs"]:
                flattened = [v for r in rounds for v in r[key]]
                if key == "common_outputs":
                    flattened = ["snapshot-usage.md", "task-metrics.json"] + flattened
                require(spec[key] == flattened, f"{task} 顶层与轮次{key}不一致")
        required_json = {p for p in spec["additional_outputs"] if p.endswith(".json")}
        templates = spec.get("audit_templates", {})
        require(isinstance(templates, dict), f"{task} 审计模板映射须为对象")
        if task.startswith("A") or task == "B04":
            require(set(templates) == required_json, f"{task} 专用JSON字段说明覆盖不完整")
        else:
            require(set(templates) <= required_json, f"{task} 模板指向未声明的交付")
        grouped = {}
        for output, template in templates.items():
            path = local_file(folder, template, f"{task} 审计模板")
            require("](" + template + ")" in prose, f"{task} 题面未引用审计模板")
            grouped.setdefault(path, set()).add(Path(output).name)
        for path, outputs in grouped.items():
            guide = load(path)
            artifacts = guide.get("artifacts", {})
            require(isinstance(artifacts, dict) and set(artifacts) == outputs,
                    f"{task} 审计字段定义与交付不一致")
            require(guide.get("common_rules"), f"{task} 审计公共规则缺失")
            for name in outputs:
                fields = artifacts[name].get("required_fields", {})
                require(isinstance(fields, dict) and bool(fields)
                        and all(isinstance(k, str) and isinstance(v, str) and v.strip()
                                for k, v in fields.items()),
                        f"{task} {name}最小字段说明为空或无效")
        artifact_count += len(templates)
    return {"tasks": len(expected), "rounds": round_count,
            "json_artifact_paths": artifact_count}


if __name__ == "__main__":
    print(json.dumps({"status": "passed", **validate_suite()}, ensure_ascii=False))
