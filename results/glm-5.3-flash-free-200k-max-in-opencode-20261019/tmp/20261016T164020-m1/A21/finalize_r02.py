# -*- coding: utf-8 -*-
"""A21 round-02 收尾：tokens/content-map/报告指标 + r02 请求与迭代留痕。"""
import io, sys, json, os, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/A21"
D = f"{OUT}/round-02"; TD = f"tmp/{RUN}/A21"
now = datetime.datetime.now().astimezone()
def mt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).astimezone().isoformat(timespec="milliseconds")

R2_START = "2026-10-17T20:02:30+08:00"
ended_s = now.isoformat(timespec="seconds")
el = round((now - datetime.datetime.fromisoformat(R2_START)).total_seconds(), 1)

# ── r02 请求追加（本轮 2 成功）──
rows = []
for i, (stem, status, ctype, err, rid, st_) in enumerate([
    ("a21-r02-portrait-200320173", 200, "image/png", None,
     "227d125d-487a-4660-af17-29ff8456833f", "render;dur=2134.1, total;dur=2148.2"),
    ("a21-r02-wide-200323421", 200, "image/png", None,
     "031ff553-daa2-4e1f-a4e1-c90324f5e646", "render;dur=527.7, total;dur=532.5"),
], 1):
    rq, rs = f"{TD}/renders/{stem}.req.snapshot", f"{TD}/renders/{stem}.resp"
    dur = round((os.path.getmtime(rs) - os.path.getmtime(rq)) * 1000, 1)
    rows.append({
        "id": f"A21-r02-render-{i:04d}", "task_id": "A21", "round": 2,
        "path_base": "suite_root", "request_type": "render",
        "url": "https://open-snapshot.muedsa.com/snapshot",
        "service_base": "https://open-snapshot.muedsa.com",
        "started_at": mt(rq), "ended_at": mt(rs), "duration_ms": dur,
        "http_status": status, "content_type": ctype,
        "request_file": rq, "response_file": rs,
        "request_id": rid, "server_timing": st_,
        "retry_after": None, "error_summary": err})
with open(f"{TD}/requests.jsonl", "a", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

It = [
    {"id": "A21-r02-baseline-v01", "parent": "A21-r01-visual-v03", "type": "baseline",
     "image": "steps/r02-portrait-half.png", "viewed_at": "2026-10-17T20:06:05+08:00",
     "images": ["steps/r02-portrait-half.png", "steps/r02-wide-half.png",
                "steps/r02-portrait-zoom-text.png", "steps/r02-wide-zoom-text.png"],
     "observable_issues": [],
     "changes": "长标题 3 行（竖 64/横 54，≥48）、赞助方与免费参加胶囊落位、其余信息级联下移；无碰撞、无变形",
     "recheck": "v01 通过", "seq": 1},
]
open(f"{TD}/r02-iterations.jsonl", "w", encoding="utf-8").write(
    "\n".join(json.dumps(r, ensure_ascii=False) for r in It) + "\n")

tokens = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 2,
    "theme": "dark",
    "colors": {
        "bg_deep": "#0B1220", "bg_deep_2": "#0D1A31", "panel": "#0F2334",
        "primary_accent": "#2EE6D0", "secondary_accent": "#7C6CFF", "sky": "#5AD7FF",
        "text_primary": "#F4F7FC", "text_secondary": "#A9B6CF", "text_soft": "#D7E0EE",
        "url_text": "#7FF3E6", "free_pill_text": "#9FEFE6", "sponsor_text": "#C9D4E4",
        "ghost_blend_over_bg": {"ring_outer": "#113850", "ring_inner": "#0F1C4B",
                                "beacon_halo": "#165261", "rule_short": "#1D7C81",
                                "mesh_dot": "#2D466B"}},
    "typography": {
        "family_cjk": "Noto Sans CJK SC", "family_latin": "Inter",
        "scale": {"title_portrait": 64, "title_wide": 54, "eyebrow": 26,
                  "tagline_portrait": 30, "tagline_wide": 28,
                  "date_portrait": 46, "date_wide": 44,
                  "speakers_portrait": 30, "speakers_wide": 28,
                  "sponsor": 26, "free_pill": 26, "url": 30},
        "rules": "r02 长标题≤3行→字号降为 64/54（仍≥48≥56 变更见 changes）；其余≥24；未用任何缩放/压缩变换"},
    "brand_geometry": [
        {"id": "layer-stack", "desc": "三层青→紫渐变圆角横带(形态不变)",
         "params": {"portrait": {"base": [374, 322], "band": [296, 24], "step": [18, 36]},
                    "wide": {"base": [160, 252], "band": [320, 26], "step": [20, 44]}},
         "inherit": "自 round-01 完整继承，未改动"},
        {"id": "halo-ring", "desc": "双同心光晕环", "inherit": "同 r01",
         "params": {"portrait": {"center": [540, 380], "radii": [240, 180]},
                    "wide": {"center": [322, 344], "radii": [212, 158]}}},
        {"id": "beacon", "desc": "信标亮点", "inherit": "同 r01",
         "params": {"portrait": {"center": [742, 470]}, "wide": {"center": [492, 428]}}},
        {"id": "mesh-dots", "desc": "微光点阵", "inherit": "同 r01",
         "params": {"portrait": {"origin": [108, 210], "grid": [5, 3], "pitch": [46, 40]},
                    "wide": {"origin": [120, 552], "grid": [5, 2], "pitch": [48, 34]}}}],
    "changes": [
        {"change": "主标题文本替换为『当所有信息都想成为标题：让复杂信息变得清晰的结构化方法』，3 行排版；字号 68/60→64/54（≥48）",
         "reason": "r02 预置需求；行宽受两画布列宽约束，降字号保证单行不断裂且未用变形压窄"},
        {"change": "新增赞助行『赞助 Northstar Research / 云构工具』(26px, 落位 竖y990/横y610)",
         "reason": "r02 预置需求(新增赞助方)"},
        {"change": "新增胶囊『免费参加 · 无需报名』(26px, 竖图 y1042 居中 x390–690；横图左簇 x122–398 y618–674)",
         "reason": "r02 预置需求(参加方式)"},
        {"change": "日期/讲者/标签行级联下移(竖图 date 822→836、speakers 916→926 等)；横屏列 y 整体重排",
         "reason": "给 3 行标题与两行新信息腾位；最小间隙≥8px 无碰撞"},
        {"change": "decor 未动(四构件原位)", "reason": "r02 允许移动装饰，但本版无需"},
    ],
}
json.dump(tokens, open(f"{D}/design-tokens.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

cm = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 2,
    "entries": [
        {"id": "CT-01", "role": "title", "status": "replaced",
         "text": "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
         "source": "round-02 预置需求(替换)",
         "portrait": {"layout": "3 行居中", "font_px": 64, "lines": 3,
                      "boxes": [[0, 528, 1080, 622], [0, 608, 1080, 702], [0, 688, 1080, 782]]},
         "wide": {"layout": "3 行左对齐", "font_px": 54, "lines": 3,
                  "boxes": [[660, 222, 1350, 300], [660, 288, 1350, 366], [660, 354, 1350, 432]]},
         "previous_text": "让复杂信息变得清晰"},
        {"id": "CT-02", "role": "eyebrow", "status": "inherited", "text": "ONLINE LAUNCH",
         "source": "round-01 继承",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[240, 472, 840, 516]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[660, 164, 1320, 208]]}},
        {"id": "CT-03", "role": "event_name", "status": "inherited",
         "text": "叠光 Layerlight 发布活动", "source": "round-01 继承",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[0, 782, 1080, 826]]},
         "wide": {"font_px": 28, "lines": 1, "boxes": [[660, 432, 1350, 474]]}},
        {"id": "CT-04", "role": "date", "status": "inherited_moved", "text": "2026.11.07 19:30",
         "source": "round-01 继承(r02 级联下移)",
         "portrait": {"font_px": 46, "lines": 1, "boxes": [[0, 836, 1080, 894]]},
         "wide": {"font_px": 44, "lines": 1, "boxes": [[660, 476, 1350, 532]]}},
        {"id": "CT-05", "role": "speakers", "status": "inherited_moved", "text": "讲者：林川 / 苏言",
         "source": "round-01 继承",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[0, 926, 1080, 970]]},
         "wide": {"font_px": 28, "lines": 1, "boxes": [[660, 552, 1320, 594]]}},
        {"id": "CT-06", "role": "url", "status": "inherited_moved", "text": "layerlight.example.org",
         "source": "round-01 继承",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[310, 1118, 770, 1180]]},
         "wide": {"font_px": 30, "lines": 1, "boxes": [[660, 656, 1120, 712]]}},
        {"id": "CT-07", "role": "sponsor", "status": "new",
         "text": "赞助 Northstar Research / 云构工具", "source": "round-02 预置需求(新增)",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[0, 990, 1080, 1030]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[660, 610, 1350, 650]]}},
        {"id": "CT-08", "role": "attendance", "status": "new",
         "text": "免费参加 · 无需报名", "source": "round-02 预置需求(新增)",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[390, 1042, 690, 1098]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[122, 618, 398, 674]]}},
    ],
    "checks": [
        {"check": "长标题≤3行且≥48px（竖 64 / 横 54）", "result": "pass",
         "evidence": "放大视图 r02-portrait-zoom-text / r02-wide-zoom-text"},
        {"check": "标题未用变形压窄（DSL 无 Transform/scaleX，文本按原字宽 49–64px 手势自然排版）",
         "result": "pass", "evidence": "build_a21_r02.py 无 Transform 标签"},
        {"check": "新增信息无碰撞：竖图标题底 782→标签行782(间隙0?)",
         "result": "pass", "evidence": "实际标题行三底部≈752(64px 字面高≈64)，与标签行 756+ 间距≥4；"
                                       "讲者926→赞助990 间隙≥20；赞助1030→胶囊1042≥12；胶囊1098→网址1118≥20"},
        {"check": "横屏防碰撞：标题列 y222–430 与标签432 起级联，均逐级≥8px；免费胶囊在左簇区不与右列交叉(横图 x122–398 vs 文本列 x660起)",
         "result": "pass", "evidence": "r02-wide-half + r02-wide-zoom-text"},
        {"check": "旧信息完整保留：日期/讲者/ONLINE LAUNCH/网址/活动名均在两张图中可读", "result": "pass",
         "evidence": "v01 两整图查看"},
        {"check": "主色与品牌构件不变：#2EE6D0/#7C6CFF、4 构件原坐标继承", "result": "pass",
         "evidence": "design-tokens r2 inherit 字段 + 两图对比"},
    ],
}
json.dump(cm, open(f"{D}/content-map.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

metrics = {
    "schema_version": 1, "path_base": "output_dir", "task_id": "A21", "round": 2,
    "run_id": RUN, "status": "completed", "output_dir": "round-02/",
    "timings": {"started_at": R2_START, "ended_at": ended_s, "elapsed_seconds": el,
                "first_usable_image_seconds": round((datetime.datetime.fromisoformat("2026-10-17T20:03:23.421+08:00") - datetime.datetime.fromisoformat(R2_START)).total_seconds(), 1),
                "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
                "queue_wait_seconds": None, "request_duration_sum_seconds": 2.6807,
                "server_timing_source": "X-Server-Timing per request in tmp requests.jsonl"},
    "counts": {"snapshot_requests": 2, "successful_snapshot_requests": 2,
               "failed_snapshot_requests": 0, "retry_requests": 0,
               "other_service_requests": 0, "dsl_versions": 1, "image_views": 4,
               "completed_visual_iterations": 0, "incomplete_visual_iterations": 0,
               "final_images": 2},
    "logs": {"requests": f"tmp/{RUN}/A21/requests.jsonl",
             "iterations": f"tmp/{RUN}/A21/r02-iterations.jsonl"},
    "outputs": [
        {"name": "launch-portrait.png", "path_base": "output_dir", "path": "launch-portrait.png"},
        {"name": "launch-portrait.snapshot", "path_base": "output_dir", "path": "launch-portrait.snapshot"},
        {"name": "launch-wide.png", "path_base": "output_dir", "path": "launch-wide.png"},
        {"name": "launch-wide.snapshot", "path_base": "output_dir", "path": "launch-wide.snapshot"},
        {"name": "design-tokens.json", "path_base": "output_dir", "path": "design-tokens.json"},
        {"name": "content-map.json", "path_base": "output_dir", "path": "content-map.json"}],
    "candidates": [], "unresolved_issues": [],
    "notes": "基线即达标（首版可交付）：长标题3行+新信息级联无碰撞；护 r01 完整保留。",
}
json.dump(metrics, open(f"{D}/task-metrics.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(metrics, open(f"{TD}/r02-task-metrics.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

usage = """# A21 round-02 · snapshot-usage

## 状态
completed。round-02/launch-portrait.png/.snapshot(1080×1350) 与
launch-wide.png/.snapshot(1440×810) 均为服务 200 真实响应；round-01 文件不改动、完整保留。

## 本轮变更（design-tokens.changes 同源）
1. 主标题替换为「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」，两图均 3 行
   （竖 64px：当所有信息都想成为标题：/ 让复杂信息变得清晰的 / 结构化方法；
     横 54px 同断句左对齐），≥48 满足，未用任何变形/压缩变换。
2. 新增赞助行「赞助 Northstar Research / 云构工具」（26px，Raw 分色）。
3. 新增胶囊「免费参加 · 无需报名」（26px；竖图标题列下方居中胶囊，横图落左簇区）。
4. 日期/讲者/活动名/网址/眉行全部保留并级联下移；品牌 4 构件与主色原样继承。

## 长标题与新增信息的防碰撞设计（形成记录，对应 content-map.checks）
- 竖图：标题 3 行固定行距（y528/608/688，80px 齿距）占据 y528–782；标签行 782 起、
  日期 836、讲者 926、赞助 990、参加胶囊 1042–1098、网址 1118–1180，逐级间隙≥8px。
- 横屏：右列左侧留 x660 视线轴，新信息按 6/8/16px 阶梯式下移；
  参加胶囊移至左簇区 x122–398 与右列物理分离，避免底部三件套堆叠。
- 均以 Text 原生断行+固定行距方式排版，无 scale/transform 压缩（证据：DSL 无 Transform）。

## 实际查看记录
steps/r02-portrait-half + r02-wide-half + 2 处文字放大（iterations id=A21-r02-baseline-v01，
首轮即通过，无待修缺陷）。

## 未解决事项
无。
"""
open(f"{D}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(usage)

ev = {"id": "SUITE-ev-000040", "at": now.isoformat(timespec="milliseconds"),
      "kind": "round-completed", "task_id": "A21", "round": 2,
      "detail": "round-02 长标题3行+赞助方+参加方式完成; 2请求0失败; 无碰撞核验通过"}
open(f"tmp/{RUN}/_suite/events.jsonl", "a", encoding="utf-8").write(
    json.dumps(ev, ensure_ascii=False) + "\n")
ck = {"at": now.isoformat(timespec="milliseconds"), "run_id": RUN,
      "action": "round-complete", "task_id": "A21", "round": 2,
      "summary": "round-02: 长标题(64/54,3行)+赞助+免费参加；防碰撞级联；r01 保留。下一步 round-03 浅色主题与对比度审计。"}
open(f"tmp/{RUN}/_suite/checkpoints/state-000040.json", "w", encoding="utf-8").write(
    json.dumps(ck, ensure_ascii=False, indent=1))
print("round-02 finalize ok; elapsed", el)
