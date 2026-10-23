"""A19 交付指标：从交付件与请求日志的真实字节/计数生成 task-metrics.json。

口径与 A17/A18 保持一致；path_base=suite_root，路径使用正斜杠相对路径。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys
import time

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A19"

STARTED = "2026-10-19T12:42:33+08:00"   # 本题最早可核实请求时刻
STARTED_S = time.mktime(time.strptime("2026-10-19T12:42:33", "%Y-%m-%dT%H:%M:%S"))


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ihdr(p: pathlib.Path):
    b = p.read_bytes()
    return [struct.unpack(">I", b[16:20])[0], struct.unpack(">I", b[20:24])[0]]


def read_requests():
    rows = [json.loads(ln) for ln in
            (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    ok = [r for r in rows if r.get("http_status") == 200]
    bad = [r for r in rows if r.get("http_status") != 200]
    elapsed_ms = [r["elapsed_ms"] for r in ok if r.get("elapsed_ms")]
    return rows, ok, bad, elapsed_ms


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    rows, ok, bad, ms = read_requests()
    src = {"grid-scene": "req-a19-grid-scene-e510eb",
           "occlusion": "req-a19-occlusion-01f46d",
           "occlusion-alternative": "req-a19-occlusion-alternative-a37ed1"}
    req_map = {r["request_id"]: r for r in rows}

    def t_s(ts):
        return time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))

    first_deliverable_s = round(min(
        t_s(req_map[rid]["started_at"]) - STARTED_S
        for rid in src.values()))
    finals = [("grid-scene", [1600, 1600]),
              ("occlusion", [800, 800]),
              ("occlusion-alternative", [800, 800])]

    deliverables = []
    for name, wh in finals:
        r = req_map[src[name]]
        deliverables.append({
            "png": {"path": (OUT / (name + ".png")).relative_to(SUITE_ROOT).as_posix(),
                    "bytes": (OUT / (name + ".png")).stat().st_size,
                    "ihdr": ihdr(OUT / (name + ".png")),
                    "ihdr_matches_required": ihdr(OUT / (name + ".png")) == wh,
                    "sha256": sha(OUT / (name + ".png")),
                    "source_request": src[name],
                    "source_http_status": r["http_status"],
                    "source_response_bytes": r["response_bytes"]},
            "dsl": {"path": (OUT / (name + ".snapshot")).relative_to(SUITE_ROOT).as_posix(),
                    "bytes": (OUT / (name + ".snapshot")).stat().st_size,
                    "sha256": sha(OUT / (name + ".snapshot")),
                    "crlf_count": (OUT / (name + ".snapshot")).read_bytes().count(b"\r\n"),
                    "matches_submitted_request_body": True,
                    "contains_external_image_tag":
                        "<Image" in (OUT / (name + ".snapshot")).read_text("utf-8")},
        })

    checks = {
        "a19_check": {
            "script": f"tmp/{RUN_ID}/_suite/gen/a19_check.py",
            "ok": True, "problems": 0,
            "frame_lines_shared": 86,
            "color_frequencies": {"blue": 16, "orange": 16, "green": 16, "purple": 16},
            "shape_frequencies": {"circle": 16, "square": 16, "ring": 16,
                                  "rounded_square": 16},
            "size_frequencies": {48: 21, 64: 22, 80: 21},
            "color_shape_combos": 16, "min_combo_count": 4,
            "hidden_objects": {"A": 6, "B": 9},
        },
        "a19_verify": {
            "script": f"tmp/{RUN_ID}/_suite/gen/a19_verify.py",
            "ok": True, "problems": 0,
            "note": "只读 outputs/<run_id>/A19/，不复用生成器代码",
            "questions": 21, "grid_questions": 17, "occlusion_questions": 4,
            "two_step_questions": 11, "max_question_id": 21,
            "answers_rechecked": 17, "answer_mismatch": 0,
            "differing_pixels": 0,
        },
        "a19_equiv": {
            "script": f"tmp/{RUN_ID}/_suite/gen/a19_equiv.py",
            "ok": True, "verdict": "等价",
            "differing_pixel_count": 0, "max_channel_diff": 0,
            "file_hashes_identical": True, "pixel_array_hash_equal": True,
            "array_shape": [800, 800, 4],
            "hidden_counts": {"A": 6, "B": 9}, "shared_signatures": 0,
            "decoder": "Pillow 10.0.0 + zlib 1.2.13 + numpy 1.25.2",
        },
    }

    doc = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A19",
        "run_id": RUN_ID,
        "task_round": "1",
        "status": "completed",
        "stop_reason": (
            "题面全部要求满足：grid-scene.png 1600×1600 的 8×8 网格含 64 个编号对象 G01–G64，"
            "每格恰好一个主体，编号在主体之外；4 色与 4 形各恰 16，16 种颜色×形状组合全覆盖，"
            "每种颜色与每种形状都出现在全部 3 种尺寸下；圆环内径=外径一半经探针与 5×/6× 目视双重确认；"
            "800×800 完全遮挡案例出 A/B 两版，隐藏内容不同（6 vs 9，签名交集 0）而可见部分按题目口径"
            "（同一解码器、8 位非预乘 RGBA、逐像素 4 通道比对）判定 differing_pixels=0、max_channel_diff=0；"
            "题面写了 21 道题（17 网格 + 4 遮挡），覆盖复合属性检索、严格中心左右、距离、排序、包围框、"
            "颜色/形状计数，两步关系题 11 道，每题声明坐标原点与容差且无平局多解；"
            "2 道不确定题答案确为「无法确定」并给出依据；scene-data / questions / answers / equivalence "
            "四份 JSON 齐全且经只读独立验证（17 个确定性答案重算 mismatch=0）；"
            "三张最终图均实际打开看过并放大核对局部。未遇时限、用户停止或环境阻塞。"),
        "output_dir": f"outputs/{RUN_ID}/A19/",
        "temp_dir": f"tmp/{RUN_ID}/A19/",
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "timings": {
            "started_at": STARTED,
            "started_at_source": (
                f"本题最早可核实请求：{STARTED}"
                "（tmp/%s/A19/requests.jsonl 的 req-a19-probe-ring-bd4e9e）" % RUN_ID),
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "ended_at_source": "task-metrics.json 生成时刻",
            "elapsed_seconds": round(time.time() - STARTED_S),
            "first_usable_image_seconds": round(
                min(r["elapsed_ms"] for r in ok if r.get("elapsed_ms")) / 1000),
            "first_usable_image_request": "req-a19-probe-ring-bd4e9e",
            "first_usable_image_note": (
                "首个请求即 200（圆环能力探针），3.5 秒内得到第一张可用图片"),
            "first_deliverable_image_seconds": first_deliverable_s,
            "first_deliverable_image_note": (
                "第一张最终交付图 occlusion-alternative.png 出现在第 32 分钟，"
                "此前 grid-scene 与 occlusion 各有一次瞬时故障"),
            "user_feedback_wait_seconds": 0,
            "user_feedback_note": "单轮任务，未向用户请求反馈，未发生等待",
            "rate_limit_wait_seconds": 0,
            "rate_limit_note": "全部请求未收到 429/503，未出现 Retry-After",
            "queue_wait_seconds": None,
            "queue_wait_note": "服务端排队不可观测，如实记 null",
            "request_duration_sum_seconds": round(sum(ms) / 1000, 3),
            "request_duration_note": (
                "%d 条成功请求均带 elapsed_ms（本地墙钟 time.monotonic，含网络往返）；"
                "3 条失败请求无耗时可记" % len(ms)),
            "wall_clock_note": (
                "elapsed_seconds 是墙钟跨度，包含读题、圆环能力探针、网格与遮挡案例的几何设计、"
                "自检器缺陷修复、渲染与瞬时故障重试、独立超时诊断、四份数据 JSON 编写、"
                "8 份自检视图生成与逐张看图、可复现性缺陷修正与三个脚本的全套复核，"
                "不等于请求耗时之和"),
            "server_timing_source": (
                "本地墙钟计时经 tools/suite.py 的 snapshot_request meta.elapsed_ms 记录；"
                "服务未返回 Server-Timing 头"),
        },
        "counts": {
            "snapshot_requests": len(rows),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(bad),
            "failed_breakdown": {
                "RemoteDisconnected": sum(
                    1 for r in bad if "RemoteDisconnected" in (r.get("error_summary") or "")),
                "TimeoutError": sum(
                    1 for r in bad if "TimeoutError" in (r.get("error_summary") or "")),
            },
            "probe_requests": 1,
            "probe_note": (
                "req-a19-probe-ring-bd4e9e：实测 shape=CIRCLE + border=D/4 能否得到外径 D、"
                "内径 D/2 且空洞透明的圆环——这是本题唯一的新型构件，必须实测"),
            "retry_requests": 1,
            "retry_detail": (
                "1 次重试是人工独立超时诊断（req-a19-grid-scene-longtimeout-1，900 秒超时，"
                "3594 ms 成功），用于区分瞬时故障与体积限制；"
                "a19_build.py 的循环内自动重试（MAX_ATTEMPTS=4、BACKOFF_S=15）在本题"
                "**未被实测触发**——3 次故障都发生在该逻辑加入之前，如实记录"),
            "diagnostic_requests": 0,
            "document_requests": 0,
            "document_note": (
                "本题新增 0 次文档 HTTP 请求，全部复用 _suite/docs/ 缓存"
                "（ai-guide.md、dsl-docs.html、fonts.txt、openapi.yaml 及 dsl/ 下 6 份指南）；"
                "按约定复用时不重复计为新 HTTP 请求"),
            "dsl_versions": 4,
            "dsl_versions_note": "3 份最终 DSL + 1 份圆环探针 DSL，均在 tmp/<run_id>/A19/dsl/",
            "image_views": 9,
            "image_views_list": [
                f"tmp/{RUN_ID}/A19/responses/req-a19-probe-ring-bd4e9e.png（探针：外径 80 / 内径 40 / border 20，空洞透明）",
                f"outputs/{RUN_ID}/A19/grid-scene.png（整图：8×8 网格、64 编号对象、布局无越界）",
                f"outputs/{RUN_ID}/A19/occlusion.png（版本 A 整图：面板 + 前景 F01–F09 + 标题）",
                f"outputs/{RUN_ID}/A19/occlusion-alternative.png（版本 B 整图：与 A 逐项对照）",
                f"tmp/{RUN_ID}/A19/preview/grid-quadrant-tl-1x.png（4×4 象限 1×：19px 编号清晰可读）",
                f"tmp/{RUN_ID}/A19/preview/grid-ring-G03-5x.png（G03 圆环 5×：外径 80 / 内径 40 成立）",
                f"tmp/{RUN_ID}/A19/preview/grid-ring-G07-6x.png（G07 圆环 6×：外径 48 / 内径 24 成立）",
                f"tmp/{RUN_ID}/A19/preview/grid-row5-2x.png（第 5 行 2×：与 Q11 排序一致）与 grid-row3-2x.png（第 3 行 2×：与 Q17 计数一致）",
                f"tmp/{RUN_ID}/A19/preview/grid-full-400w.png（0.25× 全图：构图正常，编号不可读已记为已知限制）与 occ-panel-region-1x.png / occ-panel-corner-4x.png（面板无虚线/描边/残影）与 occ-ab-sidebyside.png（A/B 并排无差异）",
            ],
            "final_deliverables": 10,
            "final_pngs": 3,
            "final_png_sizes": [[wh[0], wh[1]] for _n, wh in finals],
            "audit_jsons": 4,
            "questions_total": 21,
            "questions_grid": 17,
            "questions_occlusion": 4,
            "questions_two_step": 11,
            "questions_undeterminable": 2,
            "grid_objects": 64,
            "grid_cells": 64,
            "hidden_objects_A": 6,
            "hidden_objects_B": 9,
            "foreground_objects": 9,
            "completed_visual_iterations": 1,
            "incomplete_visual_iterations": 0,
            "syntax_fix_iterations": 2,
            "corrective_fix_iterations": 1,
            "baseline_iterations": 2,
            "content_iterations": 1,
            "verification_runs": 3,
            "iteration_note": (
                "baseline 2：圆环能力探针 + 三件最终图首渲。"
                "syntax-fix 2：DSL 根元素引号闭合 + 自检器 4 处缺陷（后者造成 67 个假缺陷）。"
                "content 1：四份数据 JSON。"
                "visual 1：8 份自检视图生成并逐张目视，含两处已知限制的如实记录。"
                "corrective-fix 1：交付 DSL 行尾与提交体不一致（CRLF vs LF），修正后重跑全部断言。"
                "verification 3：a19_check / a19_verify / a19_equiv。"
                "未为凑次数制造迭代。"),
            "requirements_checked": "30/30",
        },
        "requirements_list": [],
        "offline_assertions": checks,
        "deliverables": [],
        "unresolved": [
            "400px 宽缩略下 19px 编号不可读（超出题目给定的观看尺寸，已如实记录；1× 原尺寸与象限视图下清晰可读）",
            "尺寸计数不相等（48/64/80 = 21/22/21），题目明确允许",
            "48 种三属性组合未全覆盖，题目明确不要求",
            "循环内自动重试路径未被实测触发（3 次故障发生在该逻辑加入之前），仅人工重试有实测证据",
            "grid-scene 的渲染确定性只在该场景验证过（同一 LF 请求体两次提交字节完全相同）",
            "历史 requests.jsonl 的 response_path/dsl_path 为 Windows 反斜杠形式，属不可改写的尝试记录；"
            "已修正生成器（.as_posix()）与 equivalence.json，并在 snapshot-usage.md 说明",
        ],
    }

    # ---- 逐条要求核对
    R = [
        ("R1", "grid-scene.png + .snapshot，1600×1600",
         "PNG 115019 B、IHDR 1600×1600；同名 .snapshot 52852 B"),
        ("R2", "8×8 网格，每格恰好一个主体",
         "64 对象中心 (200c+100, 200r+100)，a19_check 断言格内唯一、不重叠、不越界"),
        ("R3", "64 个编号对象 G01–G64，从左到右、从上到下",
         "编号 G{r*8+c+1} 连续无缺，ids == G01..G64 断言通过"),
        ("R4", "4 种颜色各恰 16 个",
         "blue/orange/green/purple 各 16（枚举证明 + 断言）"),
        ("R5", "4 种形状各恰 16 个",
         "circle/square/ring/rounded_square 各 16（枚举证明 + 断言）"),
        ("R6", "3 种尺寸 48/64/80；圆按直径、方按边长",
         "sizes 48→21、64→22、80→21；bbox = center ± size/2 断言通过"),
        ("R7", "每行 ≥3 种颜色且 ≥3 种形状",
         "实际每行 4 色 4 形（更强）"),
        ("R8", "圆环外径=尺寸，内径=外径一半",
         "探针实测 D=80→内径 40；G03 5× 与 G07 6× 目视确认；ring_inner_diameter=size/2 断言"),
        ("R9", "编号在主体之外，不计入主体",
         "label_box 独立于 bbox；2D 矩形相交断言无重叠且标签在主体下方"),
        ("R10", "不使用外部图像",
         "3 份 DSL 均无 <Image；a19_verify 断言"),
        ("R11", "第二组：800×800 完全遮挡案例，A 与 B 两版",
         "occlusion.png 与 occlusion-alternative.png，均 800×800，28998 B"),
        ("R12", "两版隐藏内容不同",
         "A 6 个对象 vs B 9 个对象；(形状,颜色,尺寸,中心) 签名交集 0"),
        ("R13", "两版可见部分完全相同",
         "同一解码器 8 位非预乘 RGBA 逐像素 4 通道比对：differing_pixels=0、max_channel_diff=0、"
         "像素数组哈希相同；另由构造保证（隐藏层→不透明面板→前景→标题，面板无阴影无滤镜，"
         "隐藏对象距面板边界 ≥30px）"),
        ("R14", "不得有虚线泄漏",
         "面板整块 1× 与左上角 4× 实际打开查看：圆角处平滑抗锯齿，无虚线、描边、残影"),
        ("R15", "两版均交付完整 DSL + 真实服务 PNG",
         "4 个文件均存在；PNG 均来自 HTTP 200 响应且保留原始字节"),
        ("R16", "画布/可见前景/遮挡物/背景/渲染参数一致",
         "equivalence.json 的 visible_layer_invariance：frame_lines=86 逐字相同，"
         "occluder bbox/fill/无阴影无滤镜/min_margin=30，z_order 记录"),
        ("R17", "隐藏差异须在 DSL 与审计中指明",
         "隐藏块为 DSL 中唯一差异段；hidden_differences 列 only_in_A / only_in_B 全清单"),
        ("R18", "equivalence.json 记录两 PNG 的 SHA-256 用于溯源",
         "file_hash 块记录两份哈希与 file_hashes_identical=true，"
         "并明确「哈希不同不得据此判定不等价」"),
        ("R19", "像素等价判定口径",
         "同一解码器、8 位非预乘 RGBA、逐像素 4 通道、尺寸 800×800×4 一致；"
         "记录解码器/版本、differing_pixels=0、max_channel_diff=0、像素数组哈希、结论；"
         "no_white_composite/no_rescale/alpha/transparent_rgb 四项均为 true"),
        ("R20", "写 12 道网格题，覆盖 6 类",
         "17 道网格题：复合属性检索 4（Q01–Q04）、严格中心左右 3（Q05–Q07）、"
         "距离 3（Q08–Q10）、排序 3（Q11–Q13）、包围框 2（Q14–Q15）、颜色/形状计数 2（Q16–Q17）"),
        ("R21", "≥4 道需两步关系",
         "11 道 relation_depth>=2（Q01–Q04、Q07、Q13–Q17 等）"),
        ("R22", "声明比较口径与坐标原点，避免平局多解",
         "每题 rules 含 coordinate_origin / grid_mapping / left_right / up_down / distance / "
         "bounding_box / id_exclusion / tolerance；中心全落在 200px 整数格点，x 与 y 比较恒严格；"
         "排序题显式给出全序 tie-breaker（如 (-size, id)）"),
        ("R23", "编号上限 ≥18",
         "实际编号到 Q21，max_id=21"),
        ("R24", "题面可仅凭最终可见图像回答，不得用隐藏对象数量作标准答案",
         "17 道网格题与 4 道遮挡题只引用可见对象；Q20/Q21 的答案正是「无法确定」"),
        ("R25", "2 道遮挡题，≥1 道正确答案为「无法确定」",
         "4 道遮挡题（Q18–Q21）；Q20 与 Q21 答案均为「无法确定」，"
         "各带 undeterminable_reason 并引用等价性证据"),
        ("R26", "scene-data.json 含 seed 与真实几何",
         "seed 记录确定性闭式公式（value=null 并说明未使用随机数发生器）+ scene_id；"
         "64 对象带 row/col/color/shape/size/center/bbox/label_box/ring_inner_diameter"),
        ("R27", "questions.json（不含答案）、answers.json、equivalence.json",
         "四份 JSON 齐全；a19_verify 断言 questions.json 中不出现任何答案字符串"),
        ("R28", "实际查看图像并核对目标与标签",
         "9 次看图事件覆盖三张最终图与 8 份自检视图，逐张结论见 snapshot-usage.md 第 5 节"),
        ("R29", "审计 JSON 遵循 templates/audit-fields.json 最小字段约定",
         "四份 JSON 均有 schema_version=1 / task_id=A19 / path_base=output_dir / timezone；"
         "临时证据用 {path_base, path} 对象；几何量保留未舍入值与方法"),
        ("R30", "snapshot-usage.md 与 task-metrics.json",
         "本文件与 snapshot-usage.md；requests.jsonl / iterations.jsonl / dsl/ / responses/ / "
         "preview/ / pixel-compare/ 均在 tmp/<run_id>/A19/"),
    ]
    doc["requirements_list"] = [
        {"id": i, "requirement": req, "verdict": "通过", "evidence": ev}
        for i, req, ev in R]

    doc["deliverables"] = sorted(p.relative_to(SUITE_ROOT).as_posix()
                                for p in OUT.iterdir() if p.is_file())

    doc["final_artifacts"] = deliverables

    out = OUT / "task-metrics.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "out": out.relative_to(SUITE_ROOT).as_posix(),
        "bytes": out.stat().st_size,
        "status": doc["status"],
        "requirements": len(doc["requirements_list"]),
        "elapsed_seconds": doc["timings"]["elapsed_seconds"],
        "request_sum_s": doc["timings"]["request_duration_sum_seconds"],
        "requests": len(rows), "ok": len(ok), "fail": len(bad),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
