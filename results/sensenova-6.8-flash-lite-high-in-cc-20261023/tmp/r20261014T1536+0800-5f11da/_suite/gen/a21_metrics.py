"""A21 单轮指标生成：round-NN/task-metrics.json。

用法：python a21_metrics.py <round>

统计一律从 requests.jsonl / iterations.jsonl / viewing-evidence.json 现算，
不手抄数字。注意 requests.jsonl 中 3 条能力探针记录的 round 字段为 null
（当时记录器尚未写入轮次元数据），本脚本按时间归属把它们并入第 1 轮统计，
并在 metrics 的 counting_notes 中如实说明。

另：requests.jsonl 里没有 delivered 映射（驱动脚本在 round-01 的 9 条请求全部
落盘之后才修好「先写 delivered 再落日志」，旧日志不回填）。请求与交付件的对应
关系改由 sha256 逐一比对得出，写在 delivery_map 里并注明推导方法。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A21"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A21"

NAMES = {"portrait": "launch-portrait", "wide": "launch-wide"}


def _server_timing_parts(ok_st) -> list:
    """取本轮 portrait / wide 首次成功渲染的 attempt 号与服务端自报值。

    返回顺序按调用处的格式串排列：(portrait 的 attempt, portrait 的
    server_timing, wide 的 server_timing)。调用处已有 %d 占位承接
    len(ok_st)，故本函数只补 3 个值。仅对 rnd != 1 的轮次被调用。
    """
    by_slug = {r.get("artifact"): r for r in ok_st}
    p = by_slug.get(NAMES["portrait"])
    w = by_slug.get(NAMES["wide"])
    if p is None or w is None:
        raise ValueError("本轮缺少 portrait 或 wide 的带 server_timing 的成功记录")
    return [p.get("attempt"), p.get("server_timing"), w.get("server_timing")]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def unresolved_issues(rnd: int) -> list:
    """各轮真实的未解决事项。按轮区分，不把其他轮的问题套到本轮。"""
    if rnd == 3:
        return [
            {
                "id": "a21-r3-u1",
                "issue": "round-03-changes.json 的第一版写成了 Python 风格的相邻字符串"
                         "字面量拼接，不是合法 JSON",
                "why": "生成时沿用了代码里的多行字符串拼接写法；a21_audit.py 用 "
                       "json.loads 读取时在 line 6 报 Expecting ',' delimiter",
                "impact": "design-tokens.json 一度无法生成；不影响任何已交付图片",
                "mitigation": "改为每个字段一个完整字符串后重新校验通过；"
                              "失败草稿原样留底于 "
                              "tmp/%s/A21/round-03-changes.attempt-01.invalid-json.json，"
                              "未删除" % RUN_ID,
                "status": "disclosed",
            },
            {
                "id": "a21-r3-u2",
                "issue": "修正版 round-03-changes.json 先被写到交付目录 "
                         "outputs/<run>/A21/ 下，与第 1、2 轮「变更说明放临时目录」"
                         "的约定不一致",
                "why": "改写时路径敲错；该文件是审计脚本的输入而非交付件，"
                       "round-03.md 的必需交付清单里没有它",
                "impact": "交付目录一度混入一个工作输入文件",
                "mitigation": "用 mv 移到 tmp/%s/A21/ 与 round-01/02-changes.json 同级，"
                              "交付目录现在只剩 round-01/、round-02/、round-03/ 三个"
                              "轮次目录；未使用删除命令" % RUN_ID,
                "status": "disclosed",
            },
            {
                "id": "a21-r3-u3",
                "issue": "本轮看图时间只记录到分钟级",
                "impact": "无法给出秒级看图时刻",
                "mitigation": "viewing-evidence.json 的 15 条事件逐条以 "
                              "viewed_at_precision 标明「minute-level（本次会话内实际打开）」",
                "status": "disclosed",
            },
            {
                "id": "a21-r3-u4",
                "issue": "横版外辉光半径的配置值与构造器实参一度不一致："
                         "cfg['halo_scale_wide'] = 2.7，而 build_wide_r3 里写死 2.75",
                "why": "第三轮先写死了构造器实参，再补配置项时只改了竖版；"
                       "配置项对横版是死值，读设计 token 的人会拿到错误数字",
                "impact": "不影响已交付的图像或 DSL，但影响设计 token 文档的可信度",
                "mitigation": "改为构造器统一读 cfg['halo_scale_wide'] 并把它设为 2.75；"
                              "随后重算两份 DSL 并与已交付 .snapshot 逐字节比对一致"
                              "（portrait 6373 B、wide 5401 B，内容 IDENTICAL），"
                              "证明该修正没有改动任何已交付字节",
                "status": "disclosed",
            },
        ]
    if rnd == 2:
        return [
            {
                "id": "a21-r2-u1",
                "issue": "launch-portrait 的前两次请求在读取响应阶段超时，未返回任何字节",
                "why": "attempt 1 挂起 924282 ms、attempt 2 挂起 417859 ms 后由 socket 读取"
                       "抛出 TimeoutError。DSL 已在提交前通过本地校验（6244 B、无非法属性），"
                       "第一轮用同样风格的构造器渲染正常，故判定为服务端瞬时停顿而非请求体问题；"
                       "suite.snapshot_request 的内部重试只覆盖 429/503 与 URLError，"
                       "不覆盖读取超时，所以挂起时间全额计入本轮",
                "impact": "本轮墙钟与 request_duration_sum_seconds 被 1342 s 的挂起拉长，"
                          "两者都不再是模型或设计时间的代理值；两次尝试无响应文件可留痕",
                "mitigation": "两次超时记录原样保留在 requests.jsonl（含 elapsed_ms 与错误类型），"
                              "attempt 3 按同一份 DSL 原样重发，14.2 s 成功交付；"
                              "不删除失败记录、不补造响应文件",
                "status": "disclosed",
            },
            {
                "id": "a21-r2-u2",
                "issue": "驱动脚本异常路径把 started_at 记为异常发生时刻，即请求结束时刻",
                "why": "a21_round.py 的 render() 在 except 分支用 S.now_iso() 填 started_at；"
                       "对超时记录而言这是结束时刻，真实起点只能由 started_at - elapsed_ms 还原",
                "impact": "直接取 requests.jsonl 的 started_at 最小值会把本轮起点算成 21:38:26，"
                          "比真实起点 21:22:58 晚 15 分 28 秒，墙钟会被系统性低估",
                "mitigation": "本脚本对 http_status 为 None 的记录改用 started_at - elapsed_ms "
                              "作为起点，并在 timings.started_at_correction 逐条列出；"
                              "驱动脚本本身未回改，旧日志不回填",
                "status": "disclosed",
            },
        ]
    if rnd != 1:
        return []
    return [
        {
            "id": "a21-r1-u1",
            "issue": "本轮 9 条 requests.jsonl 记录均无 delivered 字段",
            "why": "驱动脚本在 9 条日志全部落盘之后才修好「先写 delivered 映射"
                    "再落日志」；旧日志不回填，保留真实过程优先于日志整齐",
            "impact": "无法从日志字段直接读出「哪次请求产出了交付件」",
            "mitigation": "改由响应字节 sha256 与交付 PNG sha256 逐一比对得出，"
                          "见本文件 delivery_map；第 2、3 轮日志原生带 delivered",
            "status": "disclosed",
        },
        {
            "id": "a21-r1-u2",
            "issue": "交付目录中的 PNG 被同轮 v2 迭代原地覆盖，v1 字节不在交付目录",
            "impact": "查看 round-01/*.png 只看到 v2",
            "mitigation": "v1 的服务响应原始字节完整保留在 tmp/…/A21/responses/，"
                          "sha256 与最初记录的交付值一致（portrait "
                          "fe64da1a3410d9c5…、wide 62114c08523dad9f…）；"
                          "viewing-evidence.json 的 ev-a21-003/004 指向这些保留文件",
            "status": "disclosed",
        },
        {
            "id": "a21-r1-u3",
            "issue": "部分看图时间只能到分钟级",
            "impact": "无法给出秒级看图时刻",
            "mitigation": "viewing-evidence.json 逐条以 viewed_at_precision 标明精度",
            "status": "disclosed",
        },
    ]


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    rnd = int(sys.argv[1])
    rdir = OUT / ("round-%02d" % rnd)
    end = dt.datetime.now().astimezone()

    reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    if rnd == 1:
        rs = [r for r in reqs if r.get("round") == 1 or r.get("round") is None]
        round_field_note = ("requests.jsonl 中 3 条能力探针记录的 round 字段为 null"
                            "（记录器当时尚未写入轮次元数据），按时间归属并入第 1 轮统计")
    else:
        rs = [r for r in reqs if r.get("round") == rnd]
        round_field_note = "按 requests.jsonl 的 round 字段筛选"

    def ms(r):
        return r.get("elapsed_ms") or 0.0

    renders = [r for r in rs if r.get("kind") == "render"]
    ok = [r for r in rs if r.get("http_status") == 200]
    bad = [r for r in rs if r.get("http_status") != 200]
    # 同一 DSL 原样重发才计重试；本轮每次重交都改了 DSL 正文（语法修复）
    retry = sum(1 for r in rs if r.get("attempt", 1) > 1)
    # 每个 400 响应各对应一次「改正语法后重新提交」，探针与渲染一并计入
    syntax_fix = len([r for r in rs if r.get("http_status") == 400])

    iters = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    its = [i for i in iters if i.get("round") == rnd]
    visual_done = [i for i in its if i.get("type") == "visual"]
    viewing = json.loads((TMP / "viewing-evidence.json").read_text(encoding="utf-8"))
    evs = viewing["rounds"][str(rnd)]["image_open_events"]

    # ---- 交付映射：由 sha256 逐一比对得出 ----
    delivery = []
    for key, slug in NAMES.items():
        png = rdir / ("%s.png" % slug)
        dsl = rdir / ("%s.snapshot" % slug)
        phash, dhash = sha(png), sha(dsl)
        match = [r["request_id"] for r in rs
                 if r.get("response_sha256") == phash]
        delivery.append({
            "artifact": slug,
            "png": "round-%02d/%s.png" % (rnd, slug),
            "png_bytes": png.stat().st_size, "png_sha256": phash,
            "dsl": "round-%02d/%s.snapshot" % (rnd, slug),
            "dsl_bytes": dsl.stat().st_size, "dsl_sha256": dhash,
            "source_request_id": match[0] if match else None,
            "match_basis": "响应字节 sha256 与交付 PNG sha256 逐一比对",
        })

    def start_of(r):
        """驱动脚本异常路径把 started_at 记为异常发生时刻（即结束时刻）。

        对未返回响应的记录（http_status 为 None），真实起点只能用
        started_at - elapsed_ms 还原；有响应的记录 started_at 是服务端起点。
        例：attempt 1 的 started_at 21:38:26 减 924282 ms = 21:23:01，
        两者相差 924 s（15 分 24 秒），不是几十秒。
        """
        if r.get("http_status") is None:
            return dt.datetime.fromisoformat(r["started_at"]) - dt.timedelta(
                milliseconds=ms(r))
        return dt.datetime.fromisoformat(r["started_at"])

    started = min(start_of(r) for r in rs)
    started_correction = [
        {"request_id": r["request_id"], "attempt": r.get("attempt"),
         "logged_started_at": r["started_at"],
         "true_started_at": start_of(r).isoformat(timespec="seconds"),
         "elapsed_ms": ms(r)}
        for r in rs if r.get("http_status") is None]
    service_stall_s = round(sum(ms(r) for r in rs
                                if r.get("http_status") is None) / 1000, 3)
    valid_request_s = round((sum(ms(r) for r in rs) - service_stall_s * 1000)
                            / 1000, 3)
    # 成功且带服务端 server_timing 的记录，按顺序取各自的值
    ok_st = [r for r in rs
             if r.get("http_status") == 200 and r.get("server_timing")]

    def precise_end(r):
        """日志的时间戳只精确到整秒，用 elapsed_ms 还原亚秒精度。

        注意：绝对时刻的起点仍只精确到 1 秒（时间戳被向下截断），
        故 first_* 字段的不确定度为 ±1 s，不是小数位带来的精度。
        """
        return dt.datetime.fromisoformat(r["started_at"]) + dt.timedelta(
            milliseconds=r.get("elapsed_ms") or 0)

    probe1 = min((precise_end(r) for r in rs
                  if r.get("kind") == "probe" and r.get("http_status") == 200),
                 default=None)
    deliv1 = min((precise_end(r) for r in renders
                  if r.get("http_status") == 200), default=None)
    if probe1 is None:
        # 本轮无能力探针（第一轮已验证的能力结论直接复用，未重复提交探针请求），
        # 首次可打开图片只能取首次成功的渲染请求
        probe1 = deliv1
    first_usable_note = ("首次成功取得可打开图片（能力探针1）"
                         if any(r.get("kind") == "probe" for r in rs)
                         else "本轮未提交能力探针（复用第一轮已验证的渐变/Opacity/文本扩展"
                              "结论，不重复消耗请求），首次可打开图片取首次成功的渲染请求")
    dsl_versions = {slug: len({(r.get("response_sha256") or "")
                              for r in renders
                              if r.get("artifact") == slug
                              and r.get("http_status") == 200})
                    for slug in NAMES.values()}
    probe_versions = len({(r.get("response_sha256") or "") for r in rs
                          if r.get("kind") == "probe"
                          and r.get("http_status") == 200})

    # 墙钟终点取本文件生成时刻（本轮归档完成）。另外单独记录「最后一条在案的
    # 本轮活动」，便于把归档/记账尾段与真正的设计、看图、请求时间分开——
    # 这两段不可相加，也不能用后者冒充墙钟。
    activity_ends = []
    for i in its:
        if i.get("ended_at"):
            activity_ends.append(dt.datetime.fromisoformat(i["ended_at"]))
    for e in evs:
        if e.get("viewed_at"):
            activity_ends.append(dt.datetime.fromisoformat(e["viewed_at"]))
    for r in rs:
        if r.get("http_status") is not None:
            activity_ends.append(precise_end(r))
    last_activity = max(activity_ends) if activity_ends else None
    archive_tail_s = (round((end - last_activity).total_seconds(), 1)
                      if last_activity else None)

    # 对比度审计的数字一律从实际产物读回，不硬编码。
    ca_path = OUT / ("round-%02d" % rnd) / "contrast-audit.json"
    ca = json.loads(ca_path.read_text(encoding="utf-8")) \
        if ca_path.exists() else None
    if ca:
        ca_over = ca["overall"]
        ca_per = [{"image": im["image"], "png": im["png"],
                   "size": im["size"],
                   "n_text_segments": im["n_text_segments"],
                   "n_checked": im["n_checked"],
                   "n_samples_with_coordinates": len(im.get("samples", [])),
                   "minimum_contrast_across_all_text":
                       im["minimum_contrast_across_all_text"],
                   "minimum_contrast_unrounded":
                       im["minimum_contrast_across_all_text_unrounded"],
                   "worst_segment": im["worst_segment"],
                   "method_sanity_passed":
                       bool(im["method_sanity"].get("passes"))}
                  for im in ca["images"]]
        ca_block = {
            "audit_path": "outputs/%s/A21/round-%02d/contrast-audit.json"
                          % (RUN_ID, rnd),
            "threshold": ca["images"][0]["threshold"],
            "n_images_checked": ca_over["n_images_checked"],
            "n_images_not_checked": ca_over["n_images_not_checked"],
            "n_text_segments_checked": ca_over["n_text_segments_checked"],
            "n_text_segments_not_checked": ca_over["n_text_segments_not_checked"],
            "n_coordinate_samples": sum(len(im.get("samples", []))
                                        for im in ca["images"]),
            "global_minimum_contrast_unrounded":
                ca_over["global_minimum_contrast_unrounded"],
            "global_minimum_contrast": round(
                ca_over["global_minimum_contrast_unrounded"], 4),
            "all_plain_text_meets_threshold":
                ca_over["all_plain_text_meets_threshold"],
            "not_checked_items": ca_over["not_checked_items"],
            "per_image": ca_per,
            "method": "前景取 design-token 色，背景取去文字辅助渲染（同构造器、"
                      "Canvas.text(record_text=False)）的实测像素，在字形覆盖"
                      "区域内取最差对比度；逐段最差位置另附坐标、颜色、亮度与"
                      "未舍入计算过程。辅助渲染仅存临时目录。",
            "evidence_paths": ["tmp/%s/A21/backgrounds/" % RUN_ID,
                               "tmp/%s/A21/contrast-evidence/" % RUN_ID],
        }
    else:
        ca_block = None

    notes = [
        round_field_note,
        "初次生成与查看计为基线，不计为改进迭代；改进迭代必须是"
        "「实际看图 → 修改 → 重渲 → 再实际看图比较」的完整闭环",
        "image_views 按实际打开次数记录，不因是同一张图的不同视图（整图 / 放大裁切）"
        "而合并",
    ]
    if syntax_fix:
        notes.append(
            "syntax_fix_resubmits = %d，按 400 响应条数计（每条 400 都改正了 DSL 正文"
            "后重新提交），故不与 retry_requests 相加" % syntax_fix)
    elif retry:
        notes.append(
            "本轮无 400 响应，syntax_fix_resubmits = 0；两次失败均为服务端读取超时"
            "（未返回响应、无 PARSE_ERROR），按原样重发计 retry_requests = %d，"
            "两者不重叠" % retry)
    else:
        notes.append("本轮无 400 响应，syntax_fix_resubmits 与 retry_requests 均为 0")
    if started_correction:
        notes.append(
            "started_at 取本轮真实起点 %s：%d 条读取超时记录的 started_at 被驱动脚本"
            "记为异常发生时刻（即结束时刻），本脚本用 started_at - elapsed_ms 还原，"
            "逐条见 timings.started_at_correction"
            % (started.isoformat(timespec="seconds"), len(started_correction)))
    if service_stall_s:
        notes.append(
            "request_duration_sum_seconds 与墙钟都含 %d 次服务端读取超时的挂起"
            "（合计 %.0f s），这两项都不是模型或设计时间的代理值；"
            "挂起之外的有效请求耗时见 timings.service_stall_seconds"
            % (len(started_correction), service_stall_s))
    if rnd == 1:
        notes.append(
            "requests.jsonl 的 9 条 round-01 记录均无 delivered 字段（驱动脚本在"
            "这些日志落盘之后才修好「先写 delivered 映射再落日志」，旧日志不回填）；"
            "请求与交付件的对应改由 sha256 比对得出，见 delivery_map")
    else:
        notes.append(
            "本轮请求日志原生带 delivered 字段；delivery_map 仍以 sha256 逐一比对"
            "复核，双通道一致")
    if rnd == 3:
        notes.append(
            "本轮 %d 条快照请求分两种 kind：render 2 条产出交付 PNG（launch-portrait / "
            "launch-wide），render-aux 2 条只产出去文字辅助背景渲染（tmp/%s/A21/"
            "backgrounds/），为对比度审计量取每段文字下方的实际合成背景。"
            "render-aux 不产出任何交付件，不计入作品数，也不进 delivery_map" % (len(rs), RUN_ID))
        notes.append(
            "本轮 4 条请求全部一次成功（HTTP 200），无 429/503、无读取超时、无重试，"
            "故 retry_requests 与语法修复重提交均为 0")
        notes.append(
            "contrast-audit.json 覆盖两图 %d 段普通文字（竖版 %d 段、横版 %d 段），"
            "全部检查、无未检查项，最小对比度 %.4f（阈值 %.1f），"
            "另附 %d 处带实际坐标的样本；该结果由去文字辅助渲染的实测像素算出，"
            "不是主题 token 的推算，故本轮 counts 里不另设对比度相关的请求或迭代计数"
            % (ca_over["n_text_segments_checked"], ca_per[0]["n_text_segments"],
               ca_per[1]["n_text_segments"],
               ca_over["global_minimum_contrast_unrounded"],
               ca["images"][0]["threshold"],
               sum(len(im.get("samples", [])) for im in ca["images"])))

    doc = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A21",
        "run_id": RUN_ID,
        "task_round": rnd,
        "status": "completed",
        "stop_reason": "需求满足并完成视觉自检",
        "output_dir": "outputs/%s/A21/round-%02d" % (RUN_ID, rnd),
        "temp_dir": "tmp/%s/A21" % RUN_ID,
        "timings": {
            "started_at": started.isoformat(timespec="seconds"),
            "ended_at": end.isoformat(timespec="seconds"),
            "elapsed_seconds": round((end - started).total_seconds(), 1),
            "elapsed_note": (
                "墙钟时间，含设计、看图、审计与归档，也含本会话中段的"
                "上下文压缩与平台中断造成的停顿；因此远大于"
                "request_duration_sum_seconds，两者不可相加或互相替代"
                if rnd == 1 else (
                    "墙钟时间，含设计、无网络干跑、看图、审计与归档，也含 %d 次"
                    "服务端读取超时的挂起（合计 %.0f s）；因此远大于有效请求耗时，"
                    "两者不可相加或互相替代" % (len(started_correction),
                                                 service_stall_s)
                    if rnd == 2 else
                    "墙钟时间，含第 1 轮起的复用准备、色板与球位重排设计、"
                    "无网络干跑门、去文字辅助渲染、交付渲染、逐图看图、"
                    "对比度量测、审计与归档；因此远大于 request_duration_sum_seconds，"
                    "两者不可相加或互相替代")),
            "last_recorded_activity_at": (
                last_activity.isoformat(timespec="seconds") if last_activity else None),
            "archive_tail_seconds": archive_tail_s,
            "archive_tail_note": (
                "墙钟终点取本指标文件生成时刻（本轮归档完成）。在案的本轮活动——"
                "迭代记录的 ended_at、看图事件的 viewed_at、成功请求的结束时刻——"
                "止于 last_recorded_activity_at；两者之差 archive_tail_seconds 是"
                "归档与记账尾段，含写本报告与指标、必要的返工与调试。它是墙钟的"
                "一部分，不能扣掉，也不能用 request_duration_sum_seconds 或"
                "service_stall_seconds 替代墙钟"),
            "service_stall_seconds": service_stall_s,
            "service_stall_note": (
                "http_status 为 None 的 %d 条请求的 elapsed_ms 之和——服务端接受了连接"
                "但在返回响应体期间挂起，最后由 socket 读取超时终止。这段时间没有产出，"
                "也不是模型或设计的时间" % len(started_correction)),
            "started_at_correction_note": (
                ("requests.jsonl 的 started_at 被驱动脚本的异常路径写成异常发生时刻"
                 "（即请求结束时刻），故对本轮 %d 条未返回响应的记录，真实起点只能用"
                 "started_at - elapsed_ms 还原；本脚本已按此还原，逐条证据见"
                 "timings.started_at_correction。驱动脚本本身未回改，旧日志不回填"
                 % len(started_correction))
                if started_correction else
                ("本轮 %d 条请求全部返回了响应，started_at 均为服务端起点，无需还原；"
                 "本脚本只在 http_status 为 None 时才改用 started_at - elapsed_ms"
                 % len(started_correction))),
            "started_at_correction": (
                started_correction if started_correction else []),
            "first_usable_image_seconds": (
                round((probe1 - started).total_seconds(), 3)
                if probe1 else None),
            "first_usable_image_note": first_usable_note,
            "first_delivered_image_seconds": (
                round((deliv1 - started).total_seconds(), 1)
                if deliv1 else None),
            "first_delivered_image_note": (
                ("首次成功取得交付尺寸的成品图（%s v1）" % NAMES["portrait"])
                if rnd == 1 else
                ("首次成功取得交付尺寸的成品图（%s，attempt %d）"
                 % (NAMES["portrait"],
                    next(r["attempt"] for r in renders
                         if r.get("http_status") == 200
                         and r.get("artifact") == NAMES["portrait"])))),
            "user_feedback_wait_seconds": 0,
            "user_feedback_wait_note": "预置轮次模式，不等待外部反馈；第 2、3 轮需求"
                                        "文件在本题 rounds/ 内，前一轮归档后直接读取",
            "rate_limit_wait_seconds": 0,
            "rate_limit_wait_note": "本轮未出现 429/503",
            "queue_wait_seconds": None,
            "queue_wait_null_reason": "服务端不可观测排队，未取得该数据",
            "request_duration_sum_seconds": round(sum(ms(r) for r in rs) / 1000, 3),
            "request_duration_sum_note": (
                "本轮 %d 条快照请求的 elapsed_ms 之和，不等于任务总耗时；"
                "墙钟含看图与设计时间" % len(rs)
                if rnd == 1 else (
                    "本轮 %d 条快照请求的 elapsed_ms 之和，其中 %.0f s 是读取超时"
                    "挂起（无产出），扣掉后有效请求耗时为 %.3f s，占墙钟 %.1f%%，"
                    "其余是设计、无网络干跑、看图、审计与归档"
                    % (len(rs), service_stall_s, valid_request_s,
                       valid_request_s / round((end - started).total_seconds(), 1)
                       * 100)
                    if rnd == 2 else
                    "本轮 %d 条快照请求的 elapsed_ms 之和，其中 2 条是去文字辅助渲染"
                    "（仅为对比度审计量取文字下方的实际合成背景，不产出交付件）；"
                    "本轮无 429/503、无读取超时、无重试，4 条全部一次成功，"
                    "有效请求耗时 %.3f s，占墙钟 %.1f%%，其余是浅色主题重排设计、"
                    "9 项无网络干跑门、去文字辅助渲染构造、逐图看图、"
                    "逐段对比度量测、审计与归档"
                    % (len(rs), valid_request_s,
                       valid_request_s
                       / round((end - started).total_seconds(), 1) * 100))),
            "server_timing_source": (
                "requests.jsonl 的 server_timing 字段，"
                "如 v2 portrait 'render;dur=1339.4, total;dur=1343.4'"
                "（服务端自报，与本地墙钟分开记录）"
                if rnd == 1 else (
                    "requests.jsonl 的 server_timing 字段：本轮 %d 条成功记录"
                    "（含 2 条交付渲染与 2 条去文字辅助渲染）全部有服务端自报值，"
                    "如交付渲染 portrait attempt %d '%s'、wide '%s'；"
                    "服务端自报与本地墙钟分开记录"
                    % tuple([len(ok_st)] + _server_timing_parts(ok_st))
                    if rnd == 3 else
                    "requests.jsonl 的 server_timing 字段：%d 条成功记录均有服务端"
                    "自报值，如 portrait attempt %d '%s'、wide '%s'；"
                    "两次读取超时未返回响应，故无该字段。服务端自报与本地墙钟"
                    "分开记录"
                    % tuple([len(ok_st)] + _server_timing_parts(ok_st)))),
            "timestamp_precision": "requests.jsonl 的 started_at / ended_at 被截断到整秒，"
                                    "first_usable_image_seconds 与 first_delivered_image_seconds "
                                    "已用 elapsed_ms 还原亚秒分量；绝对起点仍只精确到 1 秒，"
                                    "故这两个字段的不确定度为 ±1 s",
        },
        "counts": {
            "snapshot_requests": len(rs),
            "snapshot_requests_by_kind": {
                "render": len([r for r in rs if r.get("kind") == "render"]),
                "render-aux": len([r for r in rs
                                   if r.get("kind") == "render-aux"]),
            },
            "snapshot_requests_by_kind_note": (
                "kind='render' 是交付渲染，产出交付目录里的 PNG 与 .snapshot；"
                "kind='render-aux' 是去文字辅助渲染，只为对比度审计量取文字下方的"
                "实际合成背景，其 PNG 与 DSL 只落在临时目录，不是作品、不进入"
                "交付清单。两类请求都是真实的服务请求，故总请求数包含它们，"
                "但交付件数、dsl_versions 与作品数只计 render"
                if any(r.get("kind") == "render-aux" for r in rs) else None),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(bad),
            "retry_requests": retry,
            "retry_note": (
                "同 DSL 原样重发次数。本轮每次重交都修改了 DSL 正文"
                "（语法修复），故为 0；语法修复另计"
                if syntax_fix else
                ("同 DSL 原样重发次数：本轮 %d 条请求全部一次成功（HTTP 200），"
                 "无失败、无需重发，故为 %d；不计入语法修复" % (len(rs), retry)
                 if rnd == 3 else
                 "同 DSL 原样重发次数：两次失败均为服务端读取超时（无 PARSE_ERROR、"
                 "无需改正文），按同一份 DSL 原样重发，故为 %d；不计入语法修复"
                 % retry)),
            "syntax_fix_resubmits": syntax_fix,
            "other_service_requests": 0,
            "other_service_note": "服务指南与 DSL 文档、fonts 查询在本轮之前已取得并"
                                  "缓存于 tmp/%s/_suite/docs/，本轮复用未新增 HTTP" % RUN_ID,
            "dsl_versions": sum(dsl_versions.values()) + probe_versions,
            "dsl_versions_breakdown": {"artifacts": dsl_versions,
                                       "probe": probe_versions},
            "image_views": len(evs),
            "completed_visual_iterations": len(visual_done),
            "incomplete_visual_iterations": 0,
        },
        "contrast_audit": ca_block,
        "counting_notes": notes,
        "delivery_map": delivery,
        "logs": {
            "round_changes": "tmp/%s/A21/round-%02d-changes.json" % (RUN_ID, rnd),
            "requests": "tmp/%s/A21/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A21/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A21/viewing-evidence.json" % RUN_ID,
            "preview_manifest": "tmp/%s/A21/preview/round-%02d/views-manifest.json"
                % (RUN_ID, rnd),
            **({"auxiliary_background_renders": "tmp/%s/A21/backgrounds/" % RUN_ID,
                "auxiliary_background_note":
                    "去文字辅助渲染的 PNG（launch-*.notext.png）与它们的 DSL "
                    "（tmp/%s/A21/dsl/r03-*.notext.*.snapshot）只落在临时目录，"
                    "不进入交付目录，也不是作品" % RUN_ID,
                "contrast_local_evidence": "tmp/%s/A21/contrast-evidence/" % RUN_ID,
                "contrast_local_evidence_note":
                    "tmp/%s/A21/contrast-evidence/ 下逐段文字的交付图局部与去文字"
                    "背景局部各一份，供人工复核对比度取样位置；这些局部图不进交付目录"
                    % RUN_ID,
                "dryrun_gate": "tmp/%s/A21/dsl/r03-*.dryrun.snapshot" % RUN_ID}),
        },
        "outputs": [
            "outputs/%s/A21/round-%02d/%s.png" % (RUN_ID, rnd, NAMES["portrait"]),
            "outputs/%s/A21/round-%02d/%s.snapshot" % (RUN_ID, rnd, NAMES["portrait"]),
            "outputs/%s/A21/round-%02d/%s.png" % (RUN_ID, rnd, NAMES["wide"]),
            "outputs/%s/A21/round-%02d/%s.snapshot" % (RUN_ID, rnd, NAMES["wide"]),
            "outputs/%s/A21/round-%02d/design-tokens.json" % (RUN_ID, rnd),
            "outputs/%s/A21/round-%02d/content-map.json" % (RUN_ID, rnd),
            *(["outputs/%s/A21/round-%02d/contrast-audit.json" % (RUN_ID, rnd)]
              if rnd == 3 else []),
            "outputs/%s/A21/round-%02d/snapshot-usage.md" % (RUN_ID, rnd),
            "outputs/%s/A21/round-%02d/task-metrics.json" % (RUN_ID, rnd),
        ],
        "iterations": [{"id": i["iteration_id"], "type": i["type"],
                        "variant": i.get("variant_tag"),
                        "status": i.get("status")} for i in its],
        "unresolved_issues": unresolved_issues(rnd),
    }
    p = rdir / "task-metrics.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", p.relative_to(SUITE_ROOT).as_posix())
    print("  reqs %d (ok %d / fail %d) | sum %.3fs | wall %.0fs"
          % (len(rs), len(ok), len(bad), sum(ms(r) for r in rs) / 1000,
             (end - started).total_seconds()))
    print("  images %d | views %d | visual iters %d | dsl versions %s"
          % (2, len(evs), len(visual_done), dsl_versions))
    print("  delivery match:", [(d["artifact"], d["source_request_id"])
                                for d in delivery])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
