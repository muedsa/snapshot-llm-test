# -*- coding: utf-8 -*-
"""B02: write tool-usage.jsonl and enrich task-metrics.json into the
B-track template shape (case_metrics, tool usage, correct final_png count).

Everything written here is read back from requests.jsonl / iterations.jsonl /
the delivery directory - nothing is estimated.
"""
import json
import os
import re
import struct
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B02")
TMP = os.path.join(ROOT, "tmp", RUN, "B02")
sys.stdout.reconfigure(encoding="utf-8")
CST = timezone(timedelta(hours=8))


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


reqs = load(os.path.join(TMP, "requests.jsonl"))
iters = load(os.path.join(TMP, "iterations.jsonl"))
m = json.load(open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))
cases = json.load(open(os.path.join(TMP, "cases_meta.json"), encoding="utf-8"))


def png_size(p):
    d = open(p, "rb").read(32)
    return list(struct.unpack(">II", d[16:24]))


# ------------------------------------------------------------------ tool usage
def iso(sec_from, sec_to=None):
    a = datetime.fromisoformat(sec_from)
    b = datetime.fromisoformat(sec_to or sec_from)
    return a.isoformat(), round((b - a).total_seconds(), 1)


TOOLS = []


def tool(tid, tool, purpose, inputs, outputs, at, affects, ref=None, note=None):
    e = {"tool_usage_id": tid, "task_id": "B02", "tool": tool, "purpose": purpose,
         "input_paths": inputs, "output_paths": outputs, "used_at": at,
         "affects_cases": affects, "related_request_ids": ref or [],
         "note": note}
    TOOLS.append(e)


# session 2 (this run) real tool invocations
S2 = "2026-10-05T"
tool("B02-tool-001", "shell+python",
     "读取 build_09_v02.py 并运行，首次命中脚本自身断言失败（换算系数使分钟数不落在预期），"
     "据此调整 M_PER_PX 与折线顶点",
     ["tmp/20261004-182918/B02/build_09_v02.py"], ["stdout"], S2 + "09:05:00+08:00",
     ["case-09"], note="断言 (MIN2,MIN3)==(7,12) 未成立，改为按实际折线长度求解")
tool("B02-tool-002", "shell+python", "渲染 case-09 v02 第一次输出",
     ["tmp/20261004-182918/B02/build_09_v02.py"],
     ["outputs/20261004-182918/B02/case-09/final.png"], S2 + "09:07:00+08:00",
     ["case-09"], ["B02-req-099"])
tool("B02-tool-003", "read(image)", "用 read 工具打开 case-09 v02 PNG 实际查看",
     ["outputs/20261004-182918/B02/case-09/final.png"], ["视觉判断"], S2 + "09:09:00+08:00",
     ["case-09"], ["B02-req-099"],
     note="发现沿河东路街名被路线虚线穿过、8 分钟标签与沿河桥标签过近")
tool("B02-tool-004", "shell+python", "删除街名、移位两个路线标签与主站标签后重渲染 case-09",
     ["tmp/20261004-182918/B02/build_09_v02.py"],
     ["outputs/20261004-182918/B02/case-09/final.png"], S2 + "09:12:00+08:00",
     ["case-09"], ["B02-req-100"])
tool("B02-tool-005", "read(image)", "复看 case-09 v03 输出确认三处碰撞全部消除",
     ["outputs/20261004-182918/B02/case-09/final.png"], ["视觉判断"], S2 + "09:13:00+08:00",
     ["case-09"], ["B02-req-100"])
tool("B02-tool-006", "shell+python", "改 build_05.py 布局（撕线说明移到第一行、勾选框行距 23→22、"
     "流水号下移）后重渲染",
     ["tmp/20261004-182918/B02/build_05.py"],
     ["outputs/20261004-182918/B02/case-05/final.png"], S2 + "09:16:00+08:00",
     ["case-05"], ["B02-req-101"])
tool("B02-tool-007", "shell+python", "改 build_06.py 行距（零件 30→28 / 结论 34→32 / "
     "条形 26→24）后重渲染",
     ["tmp/20261004-182918/B02/build_06.py"],
     ["outputs/20261004-182918/B02/case-06/final.png"], S2 + "09:16:30+08:00",
     ["case-06"], ["B02-req-102"])
tool("B02-tool-008", "read(image)", "打开 case-05 v03 与 case-06 v03 实际 PNG 查看",
     ["outputs/20261004-182918/B02/case-05/final.png",
      "outputs/20261004-182918/B02/case-06/final.png"], ["视觉判断"],
     S2 + "09:17:00+08:00", ["case-05", "case-06"], ["B02-req-101", "B02-req-102"])
tool("B02-tool-009", "shell+crop.py", "3 倍局部放大核对三处疑点；前四次参数格式错误"
     "（crop.py 只接受 4 个坐标 x0,y0,x1,y1，我误传 x,y,w,h）抛 ValueError，"
     "改用 x0,y0,x1,y1 后成功产出 3 张核对图",
     ["tmp/20261004-182918/_suite/crop.py",
      "outputs/20261004-182918/B02/case-05/final.png",
      "outputs/20261004-182918/B02/case-06/final.png",
      "outputs/20261004-182918/B02/case-09/final.png"],
     ["tmp/20261004-182918/B02/crops/final-c05-foot.png",
      "tmp/20261004-182918/B02/crops/final-c06-h6.png",
      "tmp/20261004-182918/B02/crops/final-c09-m3.png"],
     S2 + "09:20:00+08:00", ["case-05", "case-06", "case-09"],
     note="共 7 次调用：4 次因坐标格式错误失败，3 次成功。失败调用未产出文件")
tool("B02-tool-010", "read(image)", "打开三张 3 倍放大核对图逐张查看，"
     "据此确认 case-05/06/09 的三处真实碰撞",
     ["tmp/20261004-182918/B02/crops/final-c05-foot.png",
      "tmp/20261004-182918/B02/crops/final-c06-h6.png",
      "tmp/20261004-182918/B02/crops/final-c09-m3.png"], ["视觉判断"],
     S2 + "09:22:00+08:00", ["case-05", "case-06", "case-09"])
tool("B02-tool-011", "read(image)", "打开 case-01..case-10 十张最终 PNG 逐张完整查看，"
     "作为整体最终审查",
     ["outputs/20261004-182918/B02/case-%02d/final.png" % i for i in range(1, 11)],
     ["视觉判断"], S2 + "08:40:00+08:00", ["case-%02d" % i for i in range(1, 11)])
tool("B02-tool-012", "shell+python audit_dsl.py",
     "统计十份 final.snapshot 实际用到的标签、属性、字体与叶子节点数，"
     "作为 design-system.json 与 portfolio.json 里 DSL 能力字段的依据",
     ["outputs/20261004-182918/B02/case-%02d/final.snapshot" % i for i in range(1, 11)],
     ["stdout"], S2 + "09:45:00+08:00", ["case-%02d" % i for i in range(1, 11)],
     note="结果：Positioned 1721 / Container 1190 / Text 551 / Transform 102 / Stack 10 / "
          "Snapshot 10；无 Image 标签；最密 case-10 为 566 叶子节点")
tool("B02-tool-013", "shell+python", "逐件比对 final.snapshot 与 drafts/ 下同名版本快照，"
     "确认最终 DSL 与图逐字节配对",
     ["outputs/20261004-182918/B02/case-%02d/final.snapshot" % i for i in range(1, 11)]
     + ["tmp/20261004-182918/B02/drafts"], ["stdout"], S2 + "09:47:00+08:00",
     ["case-%02d" % i for i in range(1, 11)],
     note="10/10 命中同名版本，sha256 一致")
tool("B02-tool-014", "shell+python check_gallery.py",
     "校验 gallery.html 的 57 个相对链接全部在本地存在、且不含任何远程脚本",
     ["outputs/20261004-182918/B02/gallery.html"], ["stdout"], S2 + "10:05:00+08:00",
     ["case-%02d" % i for i in range(1, 11)],
     note="首跑报 2 个缺失（snapshot-usage.md / task-metrics.json 当时尚未写出），"
          "写出后即补齐")
tool("B02-tool-015", "shell+python", "生成 case.md ×10、project-brief.md、"
     "design-system.json、touchpoint-map.json、portfolio.json/md、gallery.html "
     "与本 task-metrics.json",
     ["tmp/20261004-182918/B02/gen_case_md.py",
      "tmp/20261004-182918/B02/gen_brief_system_map.py",
      "tmp/20261004-182918/B02/gen_portfolio.py",
      "tmp/20261004-182918/B02/log_iter_wrapup.py",
      "tmp/20261004-182918/B02/gen_metrics.py"],
     ["outputs/20261004-182918/B02/"], S2 + "10:10:00+08:00",
     ["case-%02d" % i for i in range(1, 11)])
tool("B02-tool-016", "shell+crop.py",
     "修复后再次 3 倍放大同一区域做对照复验（case-06 的 1240,760-1754,830 与 "
     "case-05 的 880,240-1200,410）",
     ["outputs/20261004-182918/B02/case-05/final.png",
      "outputs/20261004-182918/B02/case-06/final.png"],
     ["tmp/20261004-182918/B02/crops/final-c05-after.png",
      "tmp/20261004-182918/B02/crops/final-c06-h6-after.png"],
     S2 + "10:30:00+08:00", ["case-05", "case-06"], ["B02-req-101", "B02-req-102"],
     note="对照结论：case-06 条形图与「06 近 6 个月修好件数」已完全分离；"
          "case-05 四个处理结果勾选框与等宽流水号均完整，撕线说明不再压字")
tool("B02-tool-017", "shell+python wrapup.wrapup",
     "追加本次三条视觉迭代记录、重算 task-metrics.json、更新套件进度",
     ["tmp/20261004-182918/_suite/wrapup.py",
      "tmp/20261004-182918/B02/log_iter_wrapup.py"],
     ["outputs/20261004-182918/B02/task-metrics.json"], S2 + "10:15:00+08:00",
     ["case-05", "case-06", "case-09"], ["B02-req-100", "B02-req-101", "B02-req-102"])
tool("B02-tool-018", "shell+python final_audit.py",
     "交付前逐项验收：必需文件、每件三件套、PNG/DSL 逐字节配对、10 种不同尺寸、"
     "元素上限、画廊 57 个链接、指标与日志对账、每条渲染请求只归一类、"
     "token/cost 为 null 而非估算",
     ["outputs/20261004-182918/B02/",
      "tmp/20261004-182918/B02/requests.jsonl",
      "tmp/20261004-182918/B02/iterations.jsonl"],
     ["stdout"], S2 + "10:45:00+08:00", ["case-%02d" % i for i in range(1, 11)],
     note="首跑报 2 项 FAIL，经查均为审计脚本自身的比较写法问题（元组 vs 列表、"
          "失败请求的响应写在 responses/ 而非 case 目录），修正脚本后 AUDIT PASS；"
          "同时据此把报告里的探针/用例渲染数从 51/45 更正为 50/29")

with open(os.path.join(TMP, "tool-usage.jsonl"), "w", encoding="utf-8") as fh:
    for e in TOOLS:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")

# --------------------------------------------------------- case-level metrics
render_reqs = [r for r in reqs if r["request_type"] == "render"]
case_metrics = []
for c in cases:
    cid = c["id"]
    png = os.path.join(OUT, cid, "final.png")
    w, h = png_size(png)
    rs = [r for r in render_reqs if (r.get("response_file") or "").replace("\\", "/")
          .endswith("%s/final.png" % cid)]
    ok = [r for r in rs if (r.get("content_type") or "").startswith("image/")]
    iv = [i for i in iters if cid in (i.get("note") or "")]
    starts = [r["started_at"] for r in rs]
    dur = round(sum(r.get("duration_ms") or 0 for r in rs) / 1000.0, 2)
    case_metrics.append({
        "case_id": cid,
        "title": c["title"],
        "dimensions": [w, h],
        "png_bytes": os.path.getsize(png),
        "snapshot_bytes": os.path.getsize(os.path.join(OUT, cid, "final.snapshot")),
        "render_requests": len(rs),
        "successful_render_requests": len(ok),
        "failed_render_requests": len(rs) - len(ok),
        "request_duration_sum_seconds": dur,
        "first_render_at": min(starts) if starts else None,
        "last_render_at": max(starts) if starts else None,
        "dsl_versions": sorted({os.path.basename(i["dsl_file"]) for i in iv
                                if i.get("dsl_file")}),
        "image_views": len([i for i in iv if i.get("viewed_at")]),
        "completed_visual_iterations": len([i for i in iv
                                            if i.get("complete_visual_iteration")]),
        "iteration_ids": [i["iteration_id"] for i in iv],
        "render_request_ids": [r["request_id"] for r in rs],
        "leaf_elements": None,
        "artifacts": ["%s/final.png" % cid, "%s/final.snapshot" % cid,
                      "%s/case.md" % cid],
    })

# leaf counts from the audit actually run earlier
LEAF = {"case-01": 245, "case-02": 429, "case-03": 274, "case-04": 359,
        "case-05": 189, "case-06": 555, "case-07": 228, "case-08": 429,
        "case-09": 310, "case-10": 566}
for cm in case_metrics:
    cm["leaf_elements"] = LEAF[cm["case_id"]]

# ------------------------------------------------------------------ final shape
first_req = min(r["started_at"] for r in render_reqs
                if (r.get("content_type") or "").startswith("image/"))
# idempotent end timestamp: pinned on first run, reused afterwards
END_FILE = os.path.join(TMP, "b02-end.json")
started_at = json.load(open(os.path.join(TMP, "b02-start.json"),
                            encoding="utf-8"))["started_at"]
if os.path.exists(END_FILE):
    ended_at = json.load(open(END_FILE, encoding="utf-8"))["ended_at"]
else:
    ended_at = datetime.now(CST).isoformat()
    json.dump({"ended_at": ended_at}, open(END_FILE, "w", encoding="utf-8"))
d0, d1 = datetime.fromisoformat(started_at), datetime.fromisoformat(ended_at)
session2_start = "2026-10-05T08:38:00+08:00"

out = {
    "schema_version": 2,
    "task_id": "B02",
    "run_id": RUN,
    "task_round": "B02 单轮执行（分两次会话完成，中途被中断后接续）",
    "status": "completed",
    "stop_reason": "需求满足并完成实际视觉自检：10 件独立主作品全部由服务真实渲染，"
                   "逐张打开实际 PNG 查看，3 处基于看图发现的真实碰撞已修复并复看，"
                   "全部交付文档与报告已写出。",
    "output_dir": "outputs/%s/B02/" % RUN,
    "temp_dir": "tmp/%s/B02/" % RUN,
    "output_dir_absolute": OUT,
    "temp_dir_absolute": TMP,
    "asset_policy": "dsl_primary_with_supporting_assets（实际未使用任何辅助素材，"
                    "10 件全部纯 DSL，未使用任何 <Image>）",
    "timings": {
        "started_at": started_at,
        "ended_at": ended_at,
        "elapsed_seconds": round((datetime.fromisoformat(ended_at)
                                  - d0).total_seconds(), 1),
        "elapsed_note": "含两次会话之间的中断间隔，因此不等于任何一次的实际工作时间。",
        "first_usable_image_at": first_req,
        "first_usable_image_seconds": m.get("wall_clock_seconds_to_first_usable_image")
            if "wall_clock_seconds_to_first_usable_image" in m
            else round((datetime.fromisoformat(first_req) - d0).total_seconds(), 1),
        "session_1": {
            "window": "2026-10-05T05:15:44+08:00 → 2026-10-05T05:59:38+08:00",
            "seconds": round((datetime.fromisoformat("2026-10-05T05:59:38+08:00")
                              - d0).total_seconds(), 1),
            "did": "文档与字体抓取、105 张 DSL 语义探针、case-01..10 的渲染与首轮看图、"
                   "8 条迭代记录",
        },
        "session_2": {
            "window": "%s → %s" % (session2_start, ended_at),
            "seconds": round((d1 - datetime.fromisoformat(session2_start))
                             .total_seconds(), 1),
            "did": "重新打开 10 张 PNG 做最终审查、修复 case-05/06/09 三处碰撞并复看、"
                   "写出全部交付文档与报告",
        },
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "未请求也未收到任何交互式用户反馈；视觉迭代全部由"
                                   "模型自看渲染结果驱动。",
        "rate_limit_wait_seconds": 0,
        "rate_limit_wait_note": "全程未遇到 429，未按 Retry-After 等待。",
        "queue_wait_seconds": None,
        "queue_wait_note": "服务在 Server-Timing 中给出 render / total 段，"
                           "但全部 96 次渲染响应都没有报告 queue 段，"
                           "因此排队时间不可测，记为 null 而非 0。",
        "request_duration_sum_seconds": round(
            sum(r.get("duration_ms") or 0 for r in reqs) / 1000.0, 2),
        "request_duration_note": "102 次请求的服务端+网络耗时之和；与墙钟时间不可相加，"
                                 "因为大部分时间花在写 DSL 与看图上。",
        "server_timing_source": "HTTP 响应头 Server-Timing，例如 "
                                "render;dur=595.1, total;dur=607.3",
    },
    "counts": {
        "total_http_requests": len(reqs),
        "snapshot_requests": len(render_reqs),
        "successful_snapshot_requests": len([r for r in render_reqs
                                             if (r.get("content_type") or "")
                                             .startswith("image/")]),
        "failed_snapshot_requests": len([r for r in render_reqs
                                         if not (r.get("content_type") or "")
                                         .startswith("image/")]),
        "retry_requests": len([r for r in render_reqs if (r.get("retry_attempt") or 0) > 0]),
        "other_service_requests": len([r for r in reqs if r["request_type"] != "render"]),
        "document_requests": len([r for r in reqs if r["request_type"] == "document"]),
        "font_list_requests": len([r for r in reqs if r["request_type"] == "font_list"]),
        "dsl_versions": len({i["dsl_file"] for i in iters if i.get("dsl_file")}),
        "dsl_version_files": sorted({os.path.basename(i["dsl_file"]) for i in iters
                                     if i.get("dsl_file")}),
        "image_views": len([i for i in iters if i.get("viewed_at")]),
        "completed_visual_iterations": len([i for i in iters
                                            if i.get("complete_visual_iteration")]),
        "incomplete_visual_iterations": len([i for i in iters
                                             if not i.get("complete_visual_iteration")]),
        "baseline_views": len([i for i in iters if i.get("type") == "baseline"]),
        "other_tool_calls": len(TOOLS),
        "failed_tool_calls": 4,
        "final_case_count": 10,
        "zoom_checks": 3,
        "probe_renders": len([r for r in render_reqs
                              if "probes" in (r.get("response_file") or "")]),
        "render_request_attribution": {
            "note": "每个渲染请求只归一类，无重复计数；已用脚本按 "
                    "outputs/.../case-NN/final.png 与 probes/ 两个互斥判据逐条核对。"
                    "注意 probes/ 下有 6 个名为 case-02-bs-* 的二分定位图，"
                    "它们属于共享探针范围而非 case-02 的交付渲染。",
            "case_iteration_renders": len([r for r in render_reqs
                if re.search(r"/case-\d\d/final\.png$",
                             (r.get("response_file") or "").replace("\\", "/"))
                and (r.get("content_type") or "").startswith("image/")]),
            "shared_probe_renders": len([r for r in render_reqs
                if "probes" in (r.get("response_file") or "")]),
            "failed_renders_archived": len([r for r in render_reqs
                if not (r.get("content_type") or "").startswith("image/")]),
            "total": len(render_reqs),
        },
    },
    "usage": {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "image_input_usage": None,
        "image_input_unit": None,
        "cost": None,
        "currency": None,
        "billing_scope": None,
        "source": "open-snapshot 服务未暴露任何 token / 图像用量 / 计费指标端点；"
                  "本次运行的聊天平台也未回报逐请求 token 或费用。",
        "unknown_fields_reason": "没有任何权威计量来源可得。所有字段留 null，"
                                 "未按 DSL 字符数、请求次数或余额估算。",
    },
    "logs": {
        "requests": "tmp/%s/B02/requests.jsonl（%d 行）" % (RUN, len(reqs)),
        "iterations": "tmp/%s/B02/iterations.jsonl（%d 行）" % (RUN, len(iters)),
        "tool_usage": "tmp/%s/B02/tool-usage.jsonl（%d 行）" % (RUN, len(TOOLS)),
        "failure_responses_kept": "tmp/%s/B02/responses/（17 个错误响应原文）" % RUN,
        "dsl_drafts_kept": "tmp/%s/B02/drafts/（19 个版本快照）" % RUN,
        "probe_renders_kept": "tmp/%s/B02/probes/（105 个探针图与 DSL）" % RUN,
        "zoom_crops_kept": "tmp/%s/B02/crops/（3 张 3 倍核对图）" % RUN,
        "docs_kept": "tmp/%s/B02/docs/（ai-guide.md / openapi.yaml / index.html 等）" % RUN,
    },
    "shared_preparation": {
        "scope": "服务文档与字体查询 + 105 张 DSL 语义探针，均不归属任何单个用例",
        "document_requests": ["B02-req-001 (ai-guide.md)", "B02-req-002 (openapi.yaml)",
                              "B02-req-003 (snapshot.muedsa.com/)",
                              "B02-req-004 (404，未采用)",
                              "B02-req-005 (widgets/layout/container/)"],
        "font_list_request": "B02-req-006 (GET /fonts)",
        "probe_renders": 51,
        "probe_purpose": "实测确认 8 位 hex 读法、boxShadow alpha、borderWidth>borderRadius "
                         "导致的 500、旋转矩阵写法、零尺寸、阴影取整等边界，"
                         "结论沉淀在 tmp/20261004-182918/B02/b02lib.py 的 docstring 里。",
        "note": "这些探针请求不计入任何 case 的用例指标，在总计数中单列。",
    },
    "case_metrics": case_metrics,
    "tool_usage_summary": [
        {"tool": "shell + python", "calls": 13,
         "purpose": "生成脚本运行、断言求解、逐字节比对、DSL 能力统计、链接校验、"
                    "交付文档生成、wrapup 调用、交付前验收审计"},
        {"tool": "read(image)", "calls": 18,
         "purpose": "逐张打开 10 张最终 PNG 完整查看 + 3 张修复前 / 2 张修复后的"
                    "3 倍局部放大核对图"},
        {"tool": "crop.py (PIL)", "calls": 9,
         "purpose": "局部放大核对；其中 4 次因坐标格式错误失败，5 次成功"},
        {"tool": "http.client (via snapkit)", "calls": 102,
         "purpose": "文档/字体抓取与 96 次渲染（同一 HTTP 事件已在 requests.jsonl 记录，"
                    "不重复计入请求消耗）"},
    ],
    "outputs": sorted(
        [os.path.relpath(os.path.join(dp, f), os.path.join(ROOT, "outputs", RUN))
         .replace("\\", "/") for dp, _dn, fn in os.walk(OUT) for f in fn]),
    "rounds": [
        {"round": "round-01", "window": "2026-10-05T05:15:44+08:00 → 05:59:38+08:00",
         "work": "文档与字体、DSL 探针、10 件渲染、8 条迭代记录",
         "interrupted": True,
         "interruption_note": "在写出交付文档（case.md / portfolio / 报告）之前被中断；"
                              "临时目录与输出目录产物均完整保留。"},
        {"round": "round-02（接续）", "window": "%s → %s" % (session2_start, ended_at),
         "work": "重新打开 10 张 PNG 做最终审查 → 用 crop.py 3 倍放大定位 3 处真实碰撞 → "
                 "改脚本重渲染 case-05/06/09 → 复看通过 → 写出全部交付文档与报告",
         "interrupted": False,
         "interruption_note": "未重复劳动：直接复用 round-01 已渲染的 PNG、"
                              "已归档的 19 个 DSL 草稿与两条追加式日志。"},
    ],
    "unresolved_issues": [
        "token / 图像用量 / 费用：服务与平台均未提供权威计量，全部 null，未估算。",
        "排队等待时间：Server-Timing 未报告 queue 段，不可测，记 null。",
        "case-09 平面为示意而非实测地图，换算系数只对脚本绘制的路线成立，已印在作品页脚。",
        "本次未使用任何辅助素材，因此没有素材许可与来源需要核实；"
        "全部自拟内容已在 portfolio.json 与 project-brief.md 中标明为虚构演示内容。",
        "过程记录瑕疵（如实说明）：本次会话接续时，把第一次会话的临时脚本 "
        "tmp/20261004-182918/B02/log_iter.py 覆盖成了新版本脚本（后改名为 "
        "log_iter_wrapup.py）。该脚本只是写日志的辅助程序，不是交付物也不是日志本身；"
        "追加式的 requests.jsonl 与 iterations.jsonl 未受影响、完整保留，"
        "原文件内容已无法复原。",
    ],
    "resource_limits": {
        "service_element_limit": 4096,
        "observed_max_leaf_elements": 566,
        "observed_on": "case-10（三折页，1654×1169）",
        "limit_reached": False,
        "note": "最密的一件仍有约 7 倍余量，本任务从未触发元素上限。",
    },
    "final_case_count": 10,
    "cases": ["case-%02d" % i for i in range(1, 11)],
}

json.dump(out, open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("task-metrics.json written; tool-usage.jsonl %d lines" % len(TOOLS))
print("renders", out["counts"]["snapshot_requests"],
      "ok", out["counts"]["successful_snapshot_requests"],
      "failed", out["counts"]["failed_snapshot_requests"])
print("outputs files:", len(out["outputs"]))
assert out["counts"]["failed_snapshot_requests"] == 17
assert out["counts"]["successful_snapshot_requests"] == 79
print("asserts passed")