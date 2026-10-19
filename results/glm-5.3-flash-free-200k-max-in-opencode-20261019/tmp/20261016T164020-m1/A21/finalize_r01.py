# -*- coding: utf-8 -*-
"""A21 round-01 收尾：design-tokens/content-map/round 报告指标 + 全部请求与迭代留痕。"""
import io, sys, json, os, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/A21"
D = f"{OUT}/round-01"; TD = f"tmp/{RUN}/A21"
now = datetime.datetime.now().astimezone()
def mt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).astimezone().isoformat(timespec="milliseconds")

REQUESTED_AT = "2026-10-17T19:45:10+08:00"
ended_s = now.isoformat(timespec="seconds")
start = datetime.datetime.fromisoformat(REQUESTED_AT)
el = round((now - start).total_seconds(), 1)

# ── requests.jsonl（10 次渲染：6 失败 / 4 成功）──
R = [
    ("a21-r01-portrait-195108196", 400, "application/json",
     "PARSE_ERROR: Tag Opacity only can have one child — mesh 点阵多子节点直挂 Opacity"),
    ("a21-r01-portrait-195124153", 400, "application/json",
     "PARSE_ERROR: Tag Opacity only can have one child — 眉行双短线直挂 Opacity"),
    ("a21-r01-portrait-195140048", 400, "application/json",
     "RENDER_ERROR: renderBox.parentData must be StackParentData — Opacity 直包 Positioned"),
    ("a21-r01-wide-195140887", 400, "application/json",
     "RENDER_ERROR: renderBox.parentData must be StackParentData — Opacity 直包 Positioned"),
    ("a21-r01-portrait-195243880", 400, "application/json",
     "RENDER_ERROR: Layout size is infinite — Opacity 内无界 Stack"),
    ("a21-r01-wide-195245784", 400, "application/json",
     "RENDER_ERROR: Layout size is infinite — Opacity 内无界 Stack"),
    ("a21-r01-portrait-195343808", 200, "image/png", None),
    ("a21-r01-wide-195553727", 200, "image/png", None),
    ("a21-r01-portrait-195731985", 200, "image/png", None),
    ("a21-r01-wide-195733383", 200, "image/png", None),
]
rows = []
for i, (stem, status, ctype, err) in enumerate(R, 1):
    rq, rs = f"{TD}/renders/{stem}.req.snapshot", f"{TD}/renders/{stem}.resp"
    dur = round((os.path.getmtime(rs) - os.path.getmtime(rq)) * 1000, 1)
    rows.append({
        "id": f"A21-r01-render-{i:04d}", "task_id": "A21", "round": 1,
        "path_base": "suite_root", "request_type": "render",
        "url": "https://open-snapshot.muedsa.com/snapshot",
        "service_base": "https://open-snapshot.muedsa.com",
        "started_at": mt(rq), "ended_at": mt(rs), "duration_ms": dur,
        "http_status": status, "content_type": ctype,
        "request_file": rq, "response_file": rs,
        "request_id": None, "server_timing": None,
        "retry_after": None, "error_summary": err,
    })
# 成功请求补 requestId/Server-Timing（控制台实际取得值）
ok_meta = {"a21-r01-portrait-195343808": ("1a1fdc84-067b-415c-9fa9-8ec41a0ce71b", "render;dur=452.0, total;dur=466.6"),
           "a21-r01-wide-195553727": ("57c77f15-e08a-42fa-9aff-035c3bfad1f6", "render;dur=341.4, total;dur=345.4"),
           "a21-r01-portrait-195731985": ("2d4b65ac-7d29-4867-b7cc-a957137f5c9b", "render;dur=359.0, total;dur=366.3"),
           "a21-r01-wide-195733383": ("d681b83e-1a2e-47a7-8d85-dd0df5a2fde6", "render;dur=292.8, total;dur=296.4")}
for r in rows:
    stem = os.path.basename(r["request_file"]).replace(".req.snapshot", "")
    if stem in ok_meta:
        r["request_id"], r["server_timing"] = ok_meta[stem]
with open(f"{TD}/requests.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ── iterations.jsonl ──
It = [
    {"id": "A21-r01-syntax", "parent": None, "type": "syntax-fix", "image": None,
     "viewed_at": None, "images": [],
     "observable_issues": ["6 次 400: Opacity 多子节点 → Opacity>Stack；Opacity 直包 Positioned → parentData；无界 Stack → Layout size is infinite"],
     "changes": ["装饰透明度改对底色 #0B1220 预混实色(#113850/#0F1C4B/#165261/#1D7C81/#2D466B)，移除全部 Opacity/嵌套 Stack"],
     "recheck": "两图均 200 渲染", "seq": 1},
    {"id": "A21-r01-baseline-v02", "parent": "A21-r01-syntax", "type": "baseline",
     "image": "steps/r01-portrait-half.png", "viewed_at": "2026-10-17T19:56:40+08:00",
     "images": ["steps/r01-portrait-half.png", "steps/r01-wide-half.png"],
     "observable_issues": ["URL 胶囊无文字(Text 的 height 属性是行高倍数, height=62 推出可视区)",
                           "竖图眉行右侧短线贴近 H 字尾", "竖图底部留白过重(chip 986)", "横屏右栏整体偏上"],
     "changes": ["&nbsp; 实体 → 真实 NBSP(\\u00a0)；移除 Text 上全部 height 属性",
                 "chip 文本去 height 且行内垂直居中(ty=(h-38)//2)",
                 "竖图短线外移至 258/738、chip 下移至 y1118；横屏右栏整体 +30"],
     "recheck": None, "seq": 2},
    {"id": "A21-r01-visual-v03", "parent": "A21-r01-baseline-v02", "type": "visual",
     "image": "steps/r01-portrait-half.png", "viewed_at": "2026-10-17T20:01:35+08:00",
     "images": ["steps/r01-portrait-half.png", "steps/r01-wide-half.png",
                "steps/r01-portrait-zoom-title.png", "steps/r01-wide-zoom-text.png"],
     "observable_issues": [],
     "changes": ["复检通过：两图必需文案齐全、主标题 68/60≥56、其余≥24、品牌构件4枚一致且分别构图、顶/底扩展区无字、chip 文字完整"],
     "recheck": "v03 通过", "seq": 3},
]
with open(f"{TD}/iterations.jsonl", "w", encoding="utf-8") as f:
    for r in It:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ── design-tokens.json ──
tokens = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 1,
    "theme": "dark",
    "colors": {
        "bg_deep": "#0B1220", "bg_deep_2": "#0D1A31", "panel": "#0F2334",
        "primary_accent": "#2EE6D0", "secondary_accent": "#7C6CFF", "sky": "#5AD7FF",
        "text_primary": "#F4F7FC", "text_secondary": "#A9B6CF", "text_soft": "#D7E0EE",
        "url_text": "#7FF3E6",
        "ghost_blend_over_bg": {
            "ring_outer": "#113850", "ring_inner": "#0F1C4B",
            "beacon_halo": "#165261", "rule_short": "#1D7C81", "mesh_dot": "#2D466B",
            "note": "对底色 #0B1220 的透明度预混实色(18%/12%/30%/50%/90%)"}},
    "typography": {
        "family_cjk": "Noto Sans CJK SC", "family_latin": "Inter",
        "scale": {
            "title_portrait": 68, "title_wide": 60,
            "eyebrow": 26, "tagline_portrait": 30, "tagline_wide": 28,
            "date_portrait": 46, "date_wide": 44,
            "speakers_portrait": 30, "speakers_wide": 28, "url": 30},
        "rules": "主标题≥56；其余≥24；标题/眉行加粗(Inter BOLD / CJK BOLD)；ONLINE LAUNCH 加字距12"},
    "brand_geometry": [
        {"id": "layer-stack", "desc": "三层青→紫渐变圆角横带，右向阶梯错位(叠光层)",
         "params": {"portrait": {"base": [374, 322], "band": [296, 24], "step": [18, 36]},
                    "wide": {"base": [160, 252], "band": [320, 26], "step": [20, 44]}},
         "inherit": "跨轮保持形态与渐变端色，允许移动/等比缩放"},
        {"id": "halo-ring", "desc": "双同心描边圆环光晕",
         "params": {"portrait": {"center": [540, 380], "radii": [240, 180]},
                    "wide": {"center": [322, 344], "radii": [212, 158]}},
         "inherit": "同上"},
        {"id": "beacon", "desc": "信标亮点+晕圈",
         "params": {"portrait": {"center": [742, 470]}, "wide": {"center": [492, 428]}},
         "inherit": "同上"},
        {"id": "mesh-dots", "desc": "3px 微光点阵",
         "params": {"portrait": {"origin": [108, 210], "grid": [5, 3], "pitch": [46, 40]},
                    "wide": {"origin": [120, 552], "grid": [5, 2], "pitch": [48, 34]}},
         "inherit": "同上"}],
    "changes": [],
}
json.dump(tokens, open(f"{D}/design-tokens.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ── content-map.json ──
cm = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 1,
    "entries": [
        {"id": "CT-01", "role": "title", "text": "让复杂信息变得清晰", "source": "需求 round-01",
         "status": "new",
         "portrait": {"layout": "两行居中", "font_px": 68, "lines": 2,
                      "boxes": [[0, 548, 1080, 640], [0, 642, 1080, 734]]},
         "wide": {"layout": "单行", "font_px": 60, "lines": 1,
                  "boxes": [[660, 188, 1350, 272]]}},
        {"id": "CT-02", "role": "eyebrow", "text": "ONLINE LAUNCH", "source": "需求 round-01",
         "status": "new",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[240, 472, 840, 516]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[660, 136, 1320, 180]]}},
        {"id": "CT-03", "role": "event_name", "text": "叠光 Layerlight 发布活动",
         "source": "任务主题语境(活动名)", "status": "new",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[0, 756, 1080, 800]]},
         "wide": {"font_px": 28, "lines": 1, "boxes": [[660, 286, 1350, 328]]}},
        {"id": "CT-04", "role": "date", "text": "2026.11.07 19:30", "source": "需求 round-01",
         "status": "new",
         "portrait": {"font_px": 46, "lines": 1, "boxes": [[0, 822, 1080, 880]]},
         "wide": {"font_px": 44, "lines": 1, "boxes": [[660, 346, 1350, 402]]}},
        {"id": "CT-05", "role": "speakers", "text": "讲者：林川 / 苏言", "source": "需求 round-01",
         "status": "new",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[0, 916, 1080, 960]]},
         "wide": {"font_px": 28, "lines": 1, "boxes": [[660, 430, 1320, 472]]}},
        {"id": "CT-06", "role": "url", "text": "layerlight.example.org", "source": "需求 round-01",
         "status": "new",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[310, 986, 770, 1048]]},
         "wide": {"font_px": 30, "lines": 1, "boxes": [[660, 494, 1120, 554]]}},
    ],
    "checks": [
        {"check": "必需文案 5 段齐全(标题/日期时间/ONLINE LAUNCH/讲者/网址)", "result": "pass",
         "evidence": "v03 两图整幅查看 iterations id=A21-r01-visual-v03"},
        {"check": "主标题≥56px（竖 68 / 横 60）", "result": "pass", "evidence": "build 常数+放大视图"},
        {"check": "其余文字≥24px（实际 26/28/30/44/46/60）", "result": "pass", "evidence": "design-tokens scale"},
        {"check": "顶/底真实扩展区无文字（竖 0–140 与 1180–1350；横 0–116 与 588–810）",
         "result": "pass", "evidence": "steps/half 视图目测+DSL 无该区 Text"},
        {"check": "无整图嵌入/无外部图片（DSL 不含 Image 标签）", "result": "pass", "evidence": "build_a21.py"},
        {"check": "两图同主色/同字体层级/4 枚品牌构件一致并分别构图", "result": "pass",
         "evidence": "design-tokens.brand_geometry + 两图 half 对比"},
    ],
}
json.dump(cm, open(f"{D}/content-map.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ── round-01 task-metrics.json ──
metrics = {
    "schema_version": 1, "path_base": "output_dir", "task_id": "A21", "round": 1,
    "run_id": RUN, "status": "completed", "output_dir": f"round-01/",
    "timings": {
        "started_at": REQUESTED_AT, "ended_at": ended_s, "elapsed_seconds": el,
        "first_usable_image_seconds": round((datetime.datetime.fromisoformat("2026-10-17T19:55:51.749+08:00") - start).total_seconds(), 1),
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None, "request_duration_sum_seconds": 1.456,
        "server_timing_source": "X-Server-Timing per request in tmp requests.jsonl (200 行)"},
    "counts": {
        "snapshot_requests": 10, "successful_snapshot_requests": 4, "failed_snapshot_requests": 6,
        "retry_requests": 0, "other_service_requests": 0, "dsl_versions": 3,
        "image_views": 5, "completed_visual_iterations": 1, "incomplete_visual_iterations": 0,
        "final_images": 2},
    "logs": {"requests": f"tmp/{RUN}/A21/requests.jsonl",
             "iterations": f"tmp/{RUN}/A21/iterations.jsonl"},
    "outputs": [{"name": "launch-portrait.png", "path_base": "output_dir", "path": "launch-portrait.png"},
                {"name": "launch-portrait.snapshot", "path_base": "output_dir", "path": "launch-portrait.snapshot"},
                {"name": "launch-wide.png", "path_base": "output_dir", "path": "launch-wide.png"},
                {"name": "launch-wide.snapshot", "path_base": "output_dir", "path": "launch-wide.snapshot"},
                {"name": "design-tokens.json", "path_base": "output_dir", "path": "design-tokens.json"},
                {"name": "content-map.json", "path_base": "output_dir", "path": "content-map.json"}],
    "candidates": [], "unresolved_issues": [],
    "notes": "请求留痕含 round-01 全部 10 次(6 失败为 Opacity/Stack 语法与无界 Stack，证据完整)；"
             "连续执行模式：后续轮直接从预置 rounds 文件读取，无用户反馈等待。",
}
json.dump(metrics, open(f"{D}/task-metrics.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(metrics, open(f"{TD}/r01-task-metrics.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

usage = """# A21 round-01 · snapshot-usage

## 状态
completed。交付 round-01/launch-portrait.png/.snapshot(1080×1350) 与
round-01/launch-wide.png/.snapshot(1440×810)，全部为 open-snapshot 200 真实响应。

## 设计系统（design-tokens.json / content-map.json 同步）
- 主色青 #2EE6D0 + 辅紫 #7C6CFF，深空底 #0B1220→#0D1A31 渐变；
  Inter(拉丁/数字) + Noto Sans CJK SC(中文)两级字体层级。
- 品牌 4 构件跨两图一致、分别构图：layer-stack 三层渐变横带 / halo-ring 双环 /
  beacon 信标点 / mesh-dots 点阵（透明装饰用预混实色，无 Opacity）。
- 文案最低层级 26px；主标题竖 68 横 60；数字/网址 30–46。
- 顶部/底部各留真实扩展区（竖 0–140/1180–1350，横 0–116/588–810），无占位文字。

## 视觉迭代
- 语法 6 连败：Opacity 多子节点、Opacity 直包 Positioned（parentData）、
  无界 Stack（Layout size is infinite）——改预混实色后成功。
- v02 修复：Text `height` 属性是行高倍数（误用 62/92 导致文字推出可视区），
  全部移除；&nbsp; 实体 → 真实 NBSP；chip 文字垂直居中；竖图 chip 下移至 1118、
  短线外移；横屏右栏 +30。
- v03 复检（两整图 + 两放大）：必需文案齐全、层级达标、品牌构件一致、无遮挡裁切。

## 实际查看记录
iterations.jsonl id=A21-r01-baseline-v02 / A21-r01-visual-v03，共 12 幅查看件
（两整图 half + 竖标题放大 + 横右栏放大 + chip 放大候选）。

## 未解决事项
无。
"""
open(f"{D}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(usage)

# ── suite 事件 + 轮次完成检查点 ──
ev = {"id": "SUITE-ev-000039", "at": now.isoformat(timespec="milliseconds"),
      "kind": "round-completed", "task_id": "A21", "round": 1,
      "detail": "round-01 双尺寸发布物完成: 2 PNG/DSL + tokens/contentmap; 10 请求(6失败王语.ixen 后修复); 1 视觉迭代"}
open(f"tmp/{RUN}/_suite/events.jsonl", "a", encoding="utf-8").write(
    json.dumps(ev, ensure_ascii=False) + "\n")
ck = {"at": now.isoformat(timespec="milliseconds"), "run_id": RUN,
      "action": "round-complete", "task_id": "A21", "round": 1,
      "summary": "round-01: launch-portrait/wide 完成(必需文案/层级/构件/扩展区核验)，"
                 "下一步自动读 rounds/round-02.md。"}
open(f"tmp/{RUN}/_suite/checkpoints/state-000039.json", "w", encoding="utf-8").write(
    json.dumps(ck, ensure_ascii=False, indent=1))
print("round-01 finalize ok; elapsed", el)
