"""A03 步骤 0：原样提交 inputs/broken.snapshot，保存请求、错误响应与响应头。

TASK.md 要求：「先原样提交一次真实服务并保存响应」。
原稿一字不改（含错误属性），服务返回的 400 PARSE_ERROR 位置信息是判定
「真实报错 vs 静默忽略 vs 只视觉暴露」的唯一权威依据。

启动基准：总任务根（cwd）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I 不加脚本目录
import a03_io as IO  # noqa: E402
import suite as S  # noqa: E402

SRC = IO.ROOT / "tasks" / "A03-semantic-debugging" / "inputs" / "broken.snapshot"


def main() -> None:
    out, tmp = IO.dirs()
    dsl = SRC.read_text(encoding="utf-8")          # 原样，不修改
    (tmp / "inputs-copy").mkdir(parents=True, exist_ok=True)
    (tmp / "inputs-copy" / "broken.snapshot").write_text(dsl, encoding="utf-8")

    rec = IO.submit(
        dsl,
        label="A03 原稿原样提交（修复前基线）",
        rid="req-a03-original-0001",
        out_png=None,                              # 失败响应不落输出目录
        kind="render",
        dsl_version="v0-original",
    )
    print(json.dumps({k: rec[k] for k in
                      ("request_id", "http_status", "content_type",
                       "response_bytes", "elapsed_ms", "server_timing")},
                     ensure_ascii=True, indent=1))
    # 错误响应原文写到 UTF-8 文件（控制台 GBK 会乱码，用 Read 工具看）
    (tmp / "original-error.json").write_text(rec["_error_json"] or "",
                                             encoding="utf-8")
    print("error written to", S.rel(tmp / "original-error.json"))

    IO.save_iter({
        "kind": "baseline",
        "version": "v0-original",
        "parent": None,
        "label": "A03 迁移后失效原稿",
        "reason": "原样提交，一字不改，取得服务真实报错。",
        "request_id": rec["request_id"],
        "http_status": rec["http_status"],
        "error_summary": rec["error_summary"],
        "response_body": rec["response_path"],
        "images": [],
        "note": "失败响应保留，不落输出目录；不把错误 JSON 保存成最终图片",
        "task_id": "A03",
        "timezone": S.TZ_NAME,
    })


if __name__ == "__main__":
    main()
