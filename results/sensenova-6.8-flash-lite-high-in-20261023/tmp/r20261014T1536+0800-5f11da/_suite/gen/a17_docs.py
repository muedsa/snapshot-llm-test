"""A17 生成 examples.json 与 task-metrics.json（不联网）。

examples.json 的印刷片段逐字取自 build-manifest.json 的 printed_spec；核心子树定位
由在交付 .snapshot 中查找核心子树文本的首末行号实测得到，不凭生成函数推断。
字段约定遵循 tasks/A17-documentation-handbook/templates/audit-fields.json。
"""
from __future__ import annotations

import collections
import datetime
import json
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A17"
TASK_OUT = SUITE_ROOT / "outputs" / RUN_ID / "A17"
TZ = "Asia/Shanghai (UTC+08:00)"
NAMES = ["handbook-01", "handbook-02", "handbook-03", "handbook-04",
         "example-01", "example-02", "example-03", "example-04"]

TITLES = {1: "服务调用契约：输入、输出与错误响应对照",
          2: "有界 Row/Column/Expanded 与 Stack 定位对照",
          3: "CDATA 原样输出、Raw 保留空白与尾部 alpha 对照",
          4: "BackdropFilter / ImageFiltered / ColorFiltered 对照"}

PURPOSE = {1: "把请求、成功响应与错误响应三条分支画成一张对照图，说明输入是文本、"
              "输出是二进制、失败是 JSON",
           2: "同一有界容器内并排放 Row（STRETCH + Expanded + 固定宽度子项）与 Stack"
              "（left/top 与 right/bottom 两种 Positioned 写法），对照主轴分配、"
              "交叉轴拉伸与定位",
           3: "三行对照：CDATA 内原样输出 a < b && b > a、RichText 局部 span、"
              "Raw 保留首尾空格、深色底上 #38BDF8 与 #38BDF880 的尾部 alpha 差异",
           4: "上层毛玻璃面板叠在彩色纹理上验证 BackdropFilter，下层并排 ImageFiltered "
              "模糊与 ColorFiltered MULTIPLY，右侧卡片标注像素采样位置"}

CLAIMS = [
    {"claim": "请求体是 UTF-8 编码的纯文本 DSL，Content-Type 用 text/plain; charset=utf-8，"
              "不是 JSON 端点",
     "evidence": [{"url": "https://open-snapshot.muedsa.com/ai-guide.md",
                   "request_id": "req-61b29698b623",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md",
                   "shared_or_task": "shared"},
                  {"note": "第 1 页示例把 Content-Type 文字直接画进深色调用条",
                   "example_id": "A17-E1"}]},
    {"claim": "成功返回图片二进制，后缀要与实际编码一致；失败返回带 code、message、"
              "requestId 的 JSON，不要把错误 JSON 存成 .png",
     "evidence": [{"url": "https://open-snapshot.muedsa.com/ai-guide.md",
                   "request_id": "req-61b29698b623",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md",
                   "shared_or_task": "shared"},
                  {"note": "示例内 200 image/png 与 PARSE_ERROR JSON 两个分支并排",
                   "example_id": "A17-E1"}]},
    {"claim": "400 PARSE_ERROR 的 message 给出出错行列，按行列修正后重发即可",
     "evidence": [{"url": "https://open-snapshot.muedsa.com/ai-guide.md",
                   "request_id": "req-61b29698b623",
                   "shared_or_task": "shared"},
                  {"note": "实测 req-a17-handbook-03-8730d7 报 "
                           "PARSE_ERROR Unexpected character ' ' in input state "
                           "[TAG_OPEN] at position 8064",
                   "request_id": "req-a17-handbook-03-8730d7",
                   "example_id": "A17-E3"}]},
    {"claim": "根标签 Snapshot 本身不声明画布宽高；父节点向下传递 BoxConstraints，"
              "设置 width/height 就是在收紧约束",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/layout/",
                   "request_id": "req-8233e63401ef",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-layout.html.md.txt",
                   "shared_or_task": "shared"},
                  {"note": "示例第一行标注 parent constraint 400 x 240, finite",
                   "example_id": "A17-E2"}]},
    {"claim": "Row/Column 用 mainAxisAlignment 分主轴；crossAxisAlignment=STRETCH 才填满"
              "交叉轴；Expanded 等价 Flexible fit=TIGHT，且只能是 Flex 的直接子节点",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/layout/",
                   "request_id": "req-8233e63401ef",
                   "shared_or_task": "shared"},
                  {"note": "示例中 Expanded flex=2 与 fixed 88 同排对照",
                   "example_id": "A17-E2"}]},
    {"claim": "Stack 先布局普通子节点（默认 TOP_LEFT），再按 left/top/right/bottom 放 "
              "Positioned；Positioned 必须是 Stack 的直接子节点",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/layout/",
                   "request_id": "req-8233e63401ef",
                   "shared_or_task": "shared"},
                  {"note": "实测 req-a17-handbook-03-edc061 报 PARSE_ERROR "
                           "Tag Positioned only can have one child",
                   "request_id": "req-a17-handbook-03-edc061",
                   "example_id": "A17-E2"}]},
    {"claim": "解析器不做 HTML 实体解码；文本要包含 < 或 > 必须写 CDATA",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/parser/",
                   "request_id": "req-a17-docs-parser-0948",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-parser.html.md.txt",
                   "quote": "解析器不做 HTML 实体解码。文本中要包含 < 或 > 时，使用 CDATA",
                   "section": "文本与 CDATA（缓存文件第 184–195 行）",
                   "shared_or_task": "task"},
                  {"note": "示例打印 CDATA + span: a < b && b > a",
                   "request_id": "req-a17-handbook-03-8730d7",
                   "example_id": "A17-E3"}]},
    {"claim": "Text 会 trim 首尾空白而 Raw 不 trim；未设置字段继承祖先",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/parser/",
                   "request_id": "req-a17-docs-parser-0948",
                   "shared_or_task": "task"},
                  {"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                   "request_id": "req-564b0093540f",
                   "shared_or_task": "shared"},
                  {"note": "示例中 <Raw>  keep spaces  </Raw> 保留前导空格",
                   "example_id": "A17-E3"}]},
    {"claim": "嵌套 Text 构成富文本，子 Span 只覆盖自己声明的样式，其余继承父级",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/media-text/",
                   "request_id": "req-66c9f3bfe175",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-media-text.html.md.txt",
                   "shared_or_task": "shared"},
                  {"note": "示例第一行深色面板里 'a < b && b > a' 单独换色加粗",
                   "example_id": "A17-E3"}]},
    {"claim": "8 位颜色 #RRGGBBAA 的最后两位是透明度，#38BDF880 约为 50% 透明",
     "evidence": [{"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                   "request_id": "req-564b0093540f",
                   "shared_or_task": "shared"},
                  {"url": "https://open-snapshot.muedsa.com/ai-guide.md",
                   "request_id": "req-61b29698b623",
                   "shared_or_task": "shared"},
                  {"note": "示例深色底上并排 #38BDF8 与 #38BDF880，右侧明显变暗",
                   "example_id": "A17-E3"}]},
    {"claim": "BackdropFilter 只模糊已经绘制在其背后的内容，背后是纯色时看不出效果，"
              "通常要用 ClipRRect 限定区域",
     "evidence": [{"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                   "request_id": "req-564b0093540f",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt",
                   "quote": "BackdropFilter sigmaX 、 sigmaY tileMode=\"CLAMP\" 、 "
                            "blendMode=\"SRC_OVER\"",
                   "shared_or_task": "shared"},
                  {"note": "探针 req-a17-probe-dd116f 用纯色背景看不出模糊，"
                           "req-a17-probe2-80cf1a 换成纹理背景后才可见",
                   "request_ids": ["req-a17-probe-dd116f", "req-a17-probe2-80cf1a"],
                   "example_id": "A17-E4"}]},
    {"claim": "ImageFiltered / ColorFiltered 作用在子树结果上；BlurTileMode 取值 "
              "CLAMP / REPEAT / MIRROR / DECAL",
     "evidence": [{"url": "https://snapshot.muedsa.com/reference/parser-tags/",
                   "request_id": "req-564b0093540f",
                   "shared_or_task": "shared"},
                  {"url": "https://snapshot.muedsa.com/guides/testing/",
                   "request_id": "req-a17-docs-testing-8297",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/enums.html.md.txt",
                   "quote": "FilterTileMode CLAMP 、 REPEAT 、 MIRROR 、 DECAL",
                   "shared_or_task": "a11",
                   "cache_note": "由 A11 取得并缓存，本题复用缓存，未重复发起 HTTP 请求"},
                  {"note": "示例下层并排 ImageFiltered 模糊块与 ColorFiltered MULTIPLY 块",
                   "example_id": "A17-E4"}]},
    {"claim": "服务实测约束：Container 与 Positioned 只允许一个子元素（否则 400 "
              "PARSE_ERROR）",
     "evidence": [{"note": "首版四页手册全部 400：req-a17-handbook-01-2d8a0e、"
                           "-02-abf31e、-03-edc061、-04-a7f169",
                   "request_ids": ["req-a17-handbook-01-2d8a0e",
                                   "req-a17-handbook-02-abf31e",
                                   "req-a17-handbook-03-edc061",
                                   "req-a17-handbook-04-a7f169"],
                   "example_id": "ALL"}]},
    {"claim": "服务实测约束：根 <Stack> 不能直接做 <Snapshot> 的子节点，拿到无限约束会报 "
              "RENDER_ERROR Layout size is infinite；必须外包一层显式尺寸的 Container",
     "evidence": [{"note": "req-a17-handbook-01..04 六次 RENDER_ERROR；"
                           "定位探针 P-A（外包 Container）200、P-B/P-C（旧根结构）400",
                   "request_ids": ["req-a17-probe-A-root-container-3889eb",
                                   "req-a17-probe-B-skeleton-e6fcdb",
                                   "req-a17-probe-C-codeblock-e9a400"],
                   "example_id": "ALL"}]},
    {"claim": "自检顺序：布局数值断言 > 像素采样 > Golden > Artifact；Artifact 不是断言；"
              "可复现需固定字体与颜色空间",
     "evidence": [{"url": "https://snapshot.muedsa.com/guides/testing/",
                   "request_id": "req-a17-docs-testing-8297",
                   "cache": "tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-testing.html.md.txt",
                   "shared_or_task": "task"},
                  {"note": "A17 自身按此顺序执行：a17_check.py 离线断言 → "
                           "PIL 像素采样 → 逐图人工查看",
                   "example_id": "A17-E4"}]},
]


VIEWS = [
    ("outputs/r20261014T1536+0800-5f11da/A17/handbook-01.png", "首轮逐图自检：版面、字号、代码块与插图对应"),
    ("outputs/r20261014T1536+0800-5f11da/A17/example-01.png", "首轮逐图自检：400×240 独立示例"),
    ("outputs/r20261014T1536+0800-5f11da/A17/handbook-02.png", "首轮逐图自检"),
    ("outputs/r20261014T1536+0800-5f11da/A17/example-02.png", "首轮逐图自检"),
    ("outputs/r20261014T1536+0800-5f11da/A17/handbook-03.png", "首轮逐图自检"),
    ("outputs/r20261014T1536+0800-5f11da/A17/example-03.png", "首轮逐图自检：尾部 alpha 差异可见"),
    ("outputs/r20261014T1536+0800-5f11da/A17/handbook-04.png", "首轮逐图自检：发现毛玻璃面板未覆盖两个源色块"),
    ("outputs/r20261014T1536+0800-5f11da/A17/example-04.png", "首轮逐图自检：同上"),
    ("tmp/r20261014T1536+0800-5f11da/A17/preview/hb4-illus.png", "2× 放大：确认缺陷位置"),
    ("tmp/r20261014T1536+0800-5f11da/A17/preview/ex4-glass.png", "3× 放大：确认面板左缘有未模糊的源色块与文字"),
    ("outputs/r20261014T1536+0800-5f11da/A17/example-04.png", "修复后复看：面板已完整覆盖两个色块"),
    ("tmp/r20261014T1536+0800-5f11da/A17/preview/hb4-glass.png", "修复后 3× 放大复看"),
    ("outputs/r20261014T1536+0800-5f11da/A17/handbook-04.png", "修复后复看：印刷代码与插图一致"),
]


def write_metrics(reqs):
    shared = [json.loads(l) for l in (SUITE_ROOT / "tmp" / RUN_ID / "_suite"
                                      / "requests.jsonl").read_text(encoding="utf-8")
              .splitlines() if l.strip()]
    a17_docs = [r for r in shared if str(r.get("request_id", "")).startswith("req-a17")]
    started_doc = a17_docs[0]["started_at"] if a17_docs else None
    started = min([r["started_at"] for r in reqs] + ([started_doc] if started_doc else []))
    ended = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    elapsed = int((datetime.datetime.now()
                   - datetime.datetime.fromisoformat(started.replace("+08:00", ""))).total_seconds())

    el = [r["elapsed_ms"] for r in reqs if r.get("elapsed_ms")]
    first200 = min((r for r in reqs if r["http_status"] == 200),
                   key=lambda r: r["started_at"])
    deliv = [r for r in reqs if r["http_status"] == 200
             and r["request_id"].startswith("req-a17-handbook-01-")]
    first_deliv = min(deliv, key=lambda r: r["started_at"]) if deliv else None
    net_fail = [r["request_id"] for r in reqs if r["http_status"] == 0]
    promo = json.loads((TASK_OUT / "promotion-manifest.json").read_text(encoding="utf-8"))
    def _dims(png_path):
        head = png_path.read_bytes()[:24]
        w, h = struct.unpack(">II", head[16:24])
        return w, h
    pair = {(p["name"],) + _dims(TASK_OUT / (p["name"] + ".png")) for p in promo["items"]}

    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A17",
        "run_id": RUN_ID,
        "task_round": "1",
        "status": "completed",
        "stop_reason": "题面全部要求满足：8 件指定交付（4 页手册 + 4 个 400×240 独立示例）"
                      "均为真实服务 200 响应、尺寸与字节经核验，印刷代码与运行代码同源，"
                      "逐图实际查看完成；未遇时限、用户停止或环境阻塞",
        "output_dir": "outputs/r20261014T1536+0800-5f11da/A17/",
        "temp_dir": "tmp/r20261014T1536+0800-5f11da/A17/",
        "timezone": TZ,
        "timings": {
            "started_at": started,
            "started_at_source": "本题最早可核实请求：%s（共享日志 _suite/requests.jsonl）" % started_doc,
            "ended_at": ended,
            "ended_at_source": "task-metrics.json 生成时刻",
            "elapsed_seconds": elapsed,
            "first_usable_image_seconds": int((datetime.datetime.fromisoformat(
                first200["started_at"].replace("+08:00", ""))
                - datetime.datetime.fromisoformat(started.replace("+08:00", ""))).total_seconds()),
            "first_usable_image_request": first200["request_id"],
            "first_usable_image_note": "首张可用图为语法探针 req-a17-probe-dd116f（200），"
                                       "用于确认构件契约，不是交付件",
            "first_deliverable_image_seconds": (int((datetime.datetime.fromisoformat(
                first_deliv["started_at"].replace("+08:00", ""))
                - datetime.datetime.fromisoformat(started.replace("+08:00", ""))).total_seconds())
                if first_deliv else None),
            "first_deliverable_image_request": (first_deliv["request_id"] if first_deliv else None),
            "user_feedback_wait_seconds": 0,
            "user_feedback_note": "单轮任务，未向用户请求反馈，未发生等待",
            "rate_limit_wait_seconds": 0,
            "rate_limit_note": "全部请求未收到 429/503，未出现 Retry-After；"
                               "4 次 status=0 是本地读超时或连接中断，不是限流",
            "queue_wait_seconds": None,
            "queue_wait_note": "服务端排队不可观测，如实记 null",
            "request_duration_sum_seconds": round(sum(el) / 1000, 3),
            "request_duration_note": "仅含 %d 条带 elapsed_ms 的请求（本地墙钟 time.monotonic，"
                                     "含网络往返）；%d 条 status=0 的超时请求 elapsed_ms 为 null，"
                                     "不可用落盘时间反推" % (len(el), len(net_fail)),
            "wall_clock_note": "elapsed_seconds 是墙钟跨度，包含文档阅读、探针、看图、"
                               "离线断言、写报告与等待本地分类器超时重试的时间，"
                               "不等于请求耗时之和",
            "server_timing_source": "本地墙钟计时经 tools/suite.py 的 snapshot_request meta.elapsed_ms "
                                    "记录；服务未返回 Server-Timing 头",
        },
        "counts": {
            "snapshot_requests": len([r for r in reqs if r["kind"] == "render"]),
            "successful_snapshot_requests": len([r for r in reqs
                                                 if r["kind"] == "render" and r["http_status"] == 200]),
            "failed_snapshot_requests": len([r for r in reqs
                                             if r["kind"] == "render" and r["http_status"] != 200]),
            "failed_breakdown": {
                "http_400": len([r for r in reqs if r["kind"] == "render" and r["http_status"] == 400]),
                "timeout_or_disconnect": len([r for r in reqs
                                              if r["kind"] == "render" and r["http_status"] == 0]),
            },
            "probe_requests": len([r for r in reqs if r["kind"] == "probe"]),
            "probe_note": "4 组根结构定位探针（P-A 外包 Container=200，P-B 骨架=400，"
                          "P-C 代码块=400，P-D 要点块=超时），把根因收敛到"
                          "「根 Stack 缺外层有界容器」",
            "retry_requests": len(net_fail),
            "retry_detail": "；".join(net_fail) + "；均为 status=0 的网络失败后重发同一 DSL",
            "other_service_requests": 2,
            "other_service_note": "本题新增 2 次文档请求（guides/parser、guides/testing），"
                                  "记录在共享日志。ai-guide.md、DSL 索引、fonts、openapi.yaml、"
                                  "guides/layout、guides/painting、guides/media-text、"
                                  "guides/widgets、reference/parser-tags 在共享准备阶段取得"
                                  "（_suite/requests.jsonl）；reference/parser-text、text-layout、"
                                  "text-style、enums 由 A11 取得（A11/requests.jsonl）；"
                                  "四份均缓存于 tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/，"
                                  "本题只复用缓存，按约定不重复计为新 HTTP 请求",
            "document_requests": 2,
            "dsl_versions": len([r for r in reqs if r["kind"] == "render"]),
            "dsl_versions_note": "每次渲染对应一份唯一 request_id 命名的 DSL，"
                                 "保留在 tmp/r20261014T1536+0800-5f11da/A17/dsl/",
            "image_views": len(VIEWS),
            "image_views_list": ["%s（%s）" % (p, n) for p, n in VIEWS],
            "image_views_note": "只统计本次记录到的查看事件。在此之前的上下文压缩前曾完成过一轮"
                                "等价的 8 件逐图核验，其确切时间戳不可恢复，故不计入本数",
            "final_deliverables": 8,
            "minimum_final_pngs": 8,
            "final_deliverable_sizes": sorted({(w, h) for _, w, h in pair}),
            "handbook_pages": 4,
            "independent_examples": 4,
            "completed_visual_iterations": 1,
            "incomplete_visual_iterations": 0,
            "syntax_fix_iterations": 3,
            "baseline_iterations": 1,
            "iteration_note": "baseline：4 组语法探针 + 首版 8 件渲染与首次看图。"
                              "syntax-fix 3 次：①Container 多子元素 → ②Positioned 多子元素与"
                              "属性值含 < → ③根 Stack 无限约束。visual 1 次：第 4 页毛玻璃面板"
                              "未覆盖源色块 → 加宽面板 → 重渲 → 像素采样与 3× 放大复核。"
                              "未为凑次数制造迭代",
            "requirements_checked": "20/20",
            "requirements_list": [
                {"id": "R1", "requirement": "阅读服务指南与相关官方 DSL 文档",
                 "verdict": "通过", "evidence": "15 次文档请求全部有日志与缓存，见 sources.md 第 1 节"},
                {"id": "R2", "requirement": "四张 1200×1600 教学页，主题分四页排布",
                 "verdict": "通过", "evidence": "handbook-01..04.png 经 IHDR 核验均为 1200×1600"},
                {"id": "R3", "requirement": "每页至少 8–18 行小型 DSL 示例代码",
                 "verdict": "通过", "evidence": "实际印刷行数 16/16/15/17，均在 8–18 内；a17_check.py 断言"},
                {"id": "R4", "requirement": "教学插图由同一页 DSL 构件直接画，不用 Image 嵌入预渲染整图",
                 "verdict": "通过", "evidence": "handbook-0d.snapshot 全文无 <Image 标签，插图=核心子树"},
                {"id": "R5", "requirement": "每页一例 400×240 完整示例 DSL + 独立真实渲染 PNG，共 4 例",
                 "verdict": "通过", "evidence": "example-01..04，IHDR 核验均为 400×240，均为服务 200 响应字节"},
                {"id": "R6", "requirement": "印刷代码与独立运行代码同源，不能两套",
                 "verdict": "通过", "evidence": "a17_check.py 逐字节比对：印刷片段 == 核心子树片段 == 独立 DSL 对应行"},
                {"id": "R7", "requirement": "根尺寸来自布局，避免描述为 HTML",
                 "verdict": "通过", "evidence": "第 2 页讲 BoxConstraints 收紧与 400×240 有界父容器，全文不出现 CSS/HTML 属性对照"},
                {"id": "R8", "requirement": "手册页只印关键 8–18 行，省略位置明确标识",
                 "verdict": "通过", "evidence": "省略提示共 12 行，逐条标注独立 DSL 的被省行号区间；不插入执行源码"},
                {"id": "R9", "requirement": "正文 ≥24px、代码 ≥24→≥20px、安全边距 48",
                 "verdict": "通过", "evidence": "BODY=24、CODE=20、MARGIN=48，a17_check.py 断言要点区底沿 ≤1552"},
                {"id": "R10", "requirement": "以页码/章节/短说明组织，正文不微缩",
                 "verdict": "通过", "evidence": "每页顶部「第 N 页 / 章节名 + 一句话导语」，正文最小 24px"},
                {"id": "R11", "requirement": "教学插图与独立示例的核心子树在文字、属性值、子节点顺序、"
                  "效果作用范围、相对几何上一致", "verdict": "通过",
                 "evidence": "同一 CORE 字符串逐字复用；a17_check.py 校验 handbook-0d 逐字包含 CORE"},
                {"id": "R12", "requirement": "允许差异仅限外层包装（Snapshot 根、有界容器、外框、平移），"
                  "且 1:1、不改字号/相对坐标/滤镜参数", "verdict": "通过",
                 "evidence": "a17_check.py 比对 illustration_frame(...) 与交付 DSL 逐字一致"},
                {"id": "R13", "requirement": "附 sources.md，每条关键技术结论指向实际阅读页面与例子",
                 "verdict": "通过", "evidence": "sources.md 15 条结论，各带 request_id、缓存路径与示例 ID"},
                {"id": "R14", "requirement": "附 examples.json，记录完整示例 DSL 路径、核心子树定位、"
                  "教学页对应定位、外层包装差异、印刷片段 1-based 行号与逐字原文、真实响应",
                 "verdict": "通过", "evidence": "examples.json 4 条 example 记录，"
                                        "行号与原文由文件内实测 index() 得出"},
                {"id": "R15", "requirement": "展示用 XML 转义可还原原文，省略号不插入执行源码",
                 "verdict": "通过", "evidence": "逐字原文存于 examples.json，转义还原后与 .snapshot 字节相同；"
                                        "省略提示为独立行"},
                {"id": "R16", "requirement": "印刷片段、教学插图、独立渲染三者都须核对",
                 "verdict": "通过", "evidence": "a17_check.py 三方比对 + a17_report.py 审计 + 逐图实际打开"},
                {"id": "R17", "requirement": "可共享生成函数，但不能只凭函数名声称一致",
                 "verdict": "通过", "evidence": "生成函数共享 CORE 字符串，一致性由文件字节比对与实测行号证明"},
                {"id": "R18", "requirement": "手册 4 页与 4 个示例都要实际查看",
                 "verdict": "通过", "evidence": "13 次记录在案的查看事件（含 2×/3× 放大），见 task-metrics.json"},
                {"id": "R19", "requirement": "所有指定最终 PNG 是服务真实响应且有同名 .snapshot",
                 "verdict": "通过", "evidence": "audit-trace.json pairing_ok=true，8/8 与 200 响应字节一致"},
                {"id": "R20", "requirement": "第 4 页覆盖背景滤镜/子树滤镜、视觉自检与可复现交付",
                 "verdict": "通过", "evidence": "BackdropFilter+ClipRRect、ImageFiltered、ColorFiltered、"
                                        "自检顺序与固定字体/颜色空间要点均在第 4 页正文与示例中"},
            ],
            "offline_checks": {
                "script": "tmp/r20261014T1536+0800-5f11da/_suite/gen/a17_check.py",
                "verdict": "ok=true",
                "rules": "印刷行数 8–18、行宽 ≤86、印刷片段逐字等于核心子树与独立 DSL、"
                         "省略提示行号不重不漏、Container 单孩子、属性值无 < 与 &、"
                         "Raw 无元素子节点、Positioned 父为 Stack、Expanded/Flexible 父为 Row/Column、"
                         "标签配对、教学页逐字包含核心子树、要点区不越过 1600-48",
            },
            "trace_audit": {
                "report": "tmp/r20261014T1536+0800-5f11da/A17/audit-trace.json",
                "pairing_ok": True,
            },
        },
        "logs": {
            "requests": "tmp/r20261014T1536+0800-5f11da/A17/requests.jsonl",
            "iterations": "tmp/r20261014T1536+0800-5f11da/A17/iterations.jsonl",
            "build_manifest": "tmp/r20261014T1536+0800-5f11da/A17/build-manifest.json",
            "trace_audit": "tmp/r20261014T1536+0800-5f11da/A17/audit-trace.json",
            "shared_doc_log": "tmp/r20261014T1536+0800-5f11da/_suite/requests.jsonl"
                              "（本题 2 次文档请求 req-a17-docs-parser-0948、"
                              "req-a17-docs-testing-8297 记录在此，见 A17-03）",
        },
        "outputs": [
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/handbook-0%d.png" % p,
             "role": "教学第 %d 页 1200×1600，服务返回的原始 PNG 字节，未做后处理" % p,
             "size_px": [1200, 1600], "bytes": None} for p in (1, 2, 3, 4)
        ] + [
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/handbook-0%d.snapshot" % p,
             "role": "第 %d 页完整 DSL" % p, "bytes": None} for p in (1, 2, 3, 4)
        ] + [
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/example-0%d.png" % p,
             "role": "第 %d 页可运行示例 400×240" % p,
             "size_px": [400, 240], "bytes": None} for p in (1, 2, 3, 4)
        ] + [
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/example-0%d.snapshot" % p,
             "role": "第 %d 页可运行示例完整 DSL" % p, "bytes": None} for p in (1, 2, 3, 4)
        ] + [
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/sources.md",
             "role": "每条关键技术结论 → 实际阅读的文档页与示例", "bytes": None},
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/examples.json",
             "role": "4 个完整示例、核心子树定位、印刷片段逐字原文与真实响应", "bytes": None},
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/snapshot-usage.md",
             "role": "使用报告", "bytes": None},
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/task-metrics.json",
             "role": "本题指标", "bytes": None},
            {"path": "outputs/r20261014T1536+0800-5f11da/A17/promotion-manifest.json",
             "role": "交付件来源 request_id 与字节级一致性记录", "bytes": None},
        ],
        "unresolved_issues": [
            {"id": "A17-01",
             "item": "1 次探针请求未写入 requests.jsonl",
             "detail": "定位根结构问题时首次运行 a17_probe.py 前未设置 SNAPSHOT_RUN_ID / "
                       "SNAPSHOT_TASK_ROOT，log_request 写盘失败抛出 FileNotFoundError；"
                       "该次请求产生了诊断 PNG "
                       "tmp/r20261014T1536+0800-5f11da/A17/responses/"
                       "req-a17-probe-A-root-container-b38ed6.png 但没有对应日志条目。"
                       "另有早期探针响应 probe4-crop-cdata.png 也无对应条目。"
                       "两处已在 audit-trace.json 的 orphan_response_files 中如实列出，不补造日志",
             "status": "已披露；生成脚本已修复（注入两个环境变量）"},
            {"id": "A17-02",
             "item": "build-manifest.json 只含最后一次调用的请求",
             "detail": "a17_build.py 每次运行覆盖 build-manifest.json，当前文件只记录"
                       "最后一次（example-04 重试）的 1 条请求。printed_spec、"
                       "core_line_counts、core_segments 是确定性重算结果，仍准确。"
                       "完整且只增不覆盖的渲染/探针历史在 requests.jsonl",
             "status": "已披露；完整记录以 requests.jsonl 为准"},
            {"id": "A17-03",
             "item": "A17 新增的 2 次文档请求记录在共享日志而非题内日志",
             "detail": "guides/parser（req-a17-docs-parser-0948）与 guides/testing"
                       "（req-a17-docs-testing-8297）通过 suite.log_request 记录到 "
                       "tmp/r20261014T1536+0800-5f11da/_suite/requests.jsonl，"
                       "而不是 tmp/r20261014T1536+0800-5f11da/A17/requests.jsonl；"
                       "因此题内 requests.jsonl 只有 46 条渲染/探针请求，"
                       "文档请求需到共享日志按 request_id 检索。"
                       "已确认 15 个文档请求全部有日志条目："
                       "9 条在 _suite/requests.jsonl（共享准备阶段）、"
                       "4 条在 tmp/r20261014T1536+0800-5f11da/A11/requests.jsonl"
                       "（req-7cc7ee4bc175 parser-text、req-7fd3c89fdf10 text-layout、"
                       "req-8e4ef03e2474 text-style、req-852e662461c5 enums）、"
                       "2 条为 A17 新增（同上两条）",
             "status": "已披露；不存在无日志的文档缓存文件"},
        ],
        "rounds": [],
    }
    (TASK_OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"started": started, "ended": ended, "elapsed_s": elapsed,
                      "first200": first200["request_id"],
                      "first_deliverable": first_deliv["request_id"] if first_deliv else None,
                      "render": metrics["counts"]["snapshot_requests"],
                      "probe": metrics["counts"]["probe_requests"],
                      "net_fail": net_fail}, ensure_ascii=False, indent=1))


def core_of(page: int) -> str:
    dsl = (TASK_OUT / ("example-0%d.snapshot" % page)).read_text(encoding="utf-8")
    lines = dsl.split("\n")
    return "\n".join(lines[2:-3])


def core_span(dsl_name: str, core_text: str):
    text = (TASK_OUT / (dsl_name + ".snapshot")).read_text(encoding="utf-8")
    pos = text.index(core_text)
    return [text[:pos].count("\n") + 1, text[:pos + len(core_text)].count("\n") + 1]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    man = json.loads((TASK_TMP / "build-manifest.json").read_text(encoding="utf-8"))
    promo = json.loads((TASK_OUT / "promotion-manifest.json").read_text(encoding="utf-8"))
    reqs = [json.loads(l) for l in (TASK_TMP / "requests.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
    delivered = {p["name"]: p["source_request_id"] for p in promo["items"]}

    examples = []
    for page in range(1, 5):
        spec = man["printed_spec"][str(page)]
        ex_name, hb_name = "example-0%d" % page, "handbook-0%d" % page
        core = core_of(page)
        rec = next(r for r in reqs if r["request_id"] == delivered[ex_name])
        hb_rec = next(r for r in reqs if r["request_id"] == delivered[hb_name])
        examples.append({
            "page_id": page,
            "example_id": "A17-E%d" % page,
            "title": TITLES[page],
            "purpose": PURPOSE[page],
            "paths": {
                "full_dsl": ex_name + ".snapshot",
                "rendered_png": ex_name + ".png",
                "handbook_page_png": hb_name + ".png",
                "handbook_page_dsl": hb_name + ".snapshot",
                "path_base": "output_dir",
            },
            "size_px": {"width": 400, "height": 240},
            "size_verified": {
                "method": "读取交付 PNG 的 IHDR（offset 16 起大端 32 位宽高）",
                "width": 400, "height": 240,
            },
            "core_subtree": {
                "core_line_count": len(core.split("\n")),
                "in_example_dsl_lines": core_span(ex_name, core),
                "in_handbook_dsl_lines": core_span(hb_name, core),
                "byte_identical_in_both": True,
                "location_method": "在两份交付 .snapshot 中查找同一核心子树文本，"
                                   "取其首行与末行的 1-based 行号",
            },
            "wrapper_differences": [
                "独立示例：Snapshot 根 + 400×240 Container + Stack 三层有界包装",
                "教学页：同一核心子树外包 424×264 描边外框，平移到版面居中位置",
                "差异仅限外层包装、平移与外框；核心子树的文字、属性值、子节点顺序、"
                "滤镜作用范围与相对几何均未改动",
                "核心子树在 400×240 逻辑区域内 1:1 展示，未改字号、相对坐标或滤镜参数",
            ],
            "printed_segments": spec["segments"],
            "printed_line_count": spec["printed_line_count"],
            "ellipsis_lines": spec["ellipsis_lines"],
            "line_range_note": "印刷行号以独立示例 %s.snapshot 为基准（1-based，可多段，"
                               "保持原顺序）；range_core_relative 是同一区间在核心子树内"
                               "的相对行号。省略提示为独立行，不插入实际执行源码" % ex_name,
            "response_evidence": {
                "request_id": delivered[ex_name],
                "http_status": rec["http_status"],
                "content_type": rec["content_type"],
                "response_bytes": rec["response_bytes"],
                "elapsed_ms": rec["elapsed_ms"],
                "response_path": {"path_base": "suite_root",
                                  "path": rec["response_path"].replace("\\", "/")},
                "handbook_page_request_id": delivered[hb_name],
                "handbook_page_elapsed_ms": hb_rec["elapsed_ms"],
                "png_byte_identical_to_service_response": True,
                "verified_at": promo["generated_at"],
            },
            "viewing_evidence": {
                "opened_with": "视觉工具 Read（逐图实际打开）",
                "example_viewed": True,
                "handbook_page_viewed": True,
                "zoom_crops": "tmp/r20261014T1536+0800-5f11da/A17/preview/",
                "note": "第 4 页另做 2×/3× 局部放大与 PIL 像素行采样，"
                        "确认毛玻璃面板内的模糊区域无未覆盖的源色块",
            },
        })

    examples_json = {
        "schema_version": 1,
        "task_id": "A17",
        "path_base": "output_dir",
        "run_id": RUN_ID,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": TZ,
        "example_count": 4,
        "examples": examples,
        "technical_claims": CLAIMS,
    }
    TASK_OUT.mkdir(parents=True, exist_ok=True)
    (TASK_OUT / "examples.json").write_text(
        json.dumps(examples_json, ensure_ascii=False, indent=1), encoding="utf-8")
    write_metrics(reqs)

    print(json.dumps({
        "examples": len(examples),
        "claims": len(CLAIMS),
        "core_spans": [(e["example_id"], e["core_subtree"]["in_example_dsl_lines"],
                        e["core_subtree"]["in_handbook_dsl_lines"]) for e in examples],
        "printed": [(e["example_id"], e["printed_line_count"],
                     len(e["printed_segments"]), len(e["ellipsis_lines"]))
                    for e in examples],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
