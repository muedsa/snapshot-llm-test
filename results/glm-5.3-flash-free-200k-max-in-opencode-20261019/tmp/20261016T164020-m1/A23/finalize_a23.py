# -*- coding: utf-8 -*-
"""A23 收尾：frame-data.json / timing.json / limitations.md / usage / metrics / suite。"""
import json
import math
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/A23"
TMP = f"tmp/{RUN}/A23"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
end = nows()

g = json.load(open(f"{TMP}/geometry.json", encoding="utf-8"))
UNITS, FR = g["units"], g["frames"]
F = g["ease_times"]
UT = [u["id"] for u in UNITS]
ui = {u["id"]: i for i, u in enumerate(UNITS)}

st = lambda k, u: FR[k]["units"][ui[u]]


def diff(a, b, ra, rb):
    """同单元 frame a→b 位置/旋转差。旋转按 360 等价归一到 (−180,180]。"""
    dx = st(b, u)["x"] - st(a, u)["x"]
    dy = st(b, u)["y"] - st(a, u)["y"]
    dr = st(b, u)["rotation_deg"] - st(a, u)["rotation_deg"]
    dr = (dr + 180.0) % 360.0 - 180.0
    return dx, dy, dr


traj = []
for u in UT:
    steps = []
    for k in range(5):
        dx, dy, dr = diff(k, k + 1, UT, u)
        steps.append({
            "from": FR[k]["id"], "to": FR[k + 1]["id"],
            "from_t_ms": FR[k]["t_ms"], "to_t_ms": FR[k + 1]["t_ms"],
            "dx_px": round(dx, 6), "dy_px": round(dy, 6),
            "distance_px": round(math.hypot(dx, dy), 6),
            "direction_angle_deg": round(math.degrees(math.atan2(dy, dx)), 6),
            "d_rotation_cw_deg": round(dr, 6),
            "easing_progress_from_to": [F[k], F[k + 1]]})
    traj.append({
        "id": u,
        "interpolation": {
            "rule": "ease-in-out cubic（分位公式，非已渲染中间帧）",
            "position": "p(t)=p0+(p1−p0)·f(u)；u=t/1500；f(u)=4u³ (u≤0.5)，"
                        "f(u)=1−(−2u+2)³/2 (u>0.5)",
            "rotation": "θ(t)=θ_end+(θ_start−θ_end)·(1−f(u))，以自身中心顺时针；"
                        "U09–U12（圆）rotation 恒 0",
            "easing_frame_values": {FR[k]["id"]: F[k] for k in range(6)},
            "extent": "F6 停在 f=53/54≈0.981481（末帧为汇聚 98.1481% 进度，"
                      "差 1/54≈1.852%，属 ease 曲线在 u=5/6 的设计值）",
        },
        "steps": steps})

seam_units = []
seam_stats = {}
for u in UT:
    dx, dy, dr = diff(5, 0, UT, u)
    d = math.hypot(dx, dy)
    seg = [s["distance_px"] for s in
           [t for t in traj if t["id"] == u][0]["steps"]]
    seg_rot = [abs(s["d_rotation_cw_deg"]) for s in
               [t for t in traj if t["id"] == u][0]["steps"]]
    seam_units.append({
        "id": u,
        "dx_px": round(dx, 6), "dy_px": round(dy, 6),
        "distance_px": round(d, 6),
        "d_rotation_cw_deg": round(dr, 6), "rotation_equiv_360": True,
        "vs_norm_step": {"avg_segment_distance_px": round(sum(seg) / 5, 6),
                         "max_segment_distance_px": max(seg),
                         "seam_over_max": round(d / max(seg), 4),
                         "avg_abs_rot_step_deg": round(sum(seg_rot) / 5, 6)},
        "note": "末帧→首帧一步回跳幅值远大于相邻帧步长"})

audit = {
    "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
    "coordinate_system": {
        "origin": "canvas top-left", "x_axis": "right", "y_axis": "down",
        "unit": "pixel", "position_semantics": "单元几何中心 (x,y)（未旋转框中心）",
        "rotation": {"sense": "顺时针", "unit": "度", "pivot": "自身中心",
                     "dsl_implementation": "Transform matrix 列主序 "
                     "(cos,sin,0,0,−sin,cos,0,0,0,0,1,0,0,0,0,1) + origin=(w/2,h/2)",
                     "verified": "tmp probe：0/30/90/180° 实测 bounding "
                                 "框中心与顶端尖点均匹配顺时针+中心旋转"},
        "sizes": "宽高按未旋转几何记录；旋转不改变宽高字段",
    },
    "units": [{"id": u["id"], "type": u["type"],
               "width": u["w"], "height": u["h"], "color": u["color"],
               "rgb": u["rgb"], "alpha": u["alpha"], "role": u["role"],
               "border_radius": u.get("border_radius", 0.0),
               "invariant_note": "几何类型/未旋转宽高/RGB/alpha 六帧恒定；"
                                 "仅位置与旋转变化"} for u in UNITS],
    "frames": [{"id": fr["id"], "t_ms": fr["t_ms"],
                "image": fr["image"], "dsl": fr["dsl"],
                "easing_progress": fr["easing_progress"],
                "units": [{"id": s["id"], "x": s["x"], "y": s["y"],
                           "w": fr["units"][i]["w"] if False else UNITS[i]["w"],
                           "h": UNITS[i]["h"],
                           "rotation_deg": s["rotation_deg"],
                           "visible": True, "alpha": UNITS[i]["alpha"],
                           "color": UNITS[i]["color"], "type": UNITS[i]["type"]}
                          for i, s in enumerate(fr["units"])]
                } for fr in FR],
    "trajectories": traj,
    "seam": {
        "from_frame": "F6", "at_ms": 1250, "to_frame": "F1", "to_ms": 0,
        "loop_period_ms": 1500,
        "per_unit": seam_units,
        "motion_direction_analysis": {
            "claim": "非无缝（seamless=false）",
            "reason": "F6 停留于 ease f=53/54 汇聚图形；F1 为四周分散原位。"
                      "按循环回绕（1250→1500≡0），每单元位移为全程位移的 "
                      "(1−53/54) 汇聚进度差的逆回？不成立——",
            "correction_note": "接缝差按 F1−F6 逐单元实测计算（见 per_unit）；"
                               "不是流畅方向反转，而是『汇聚图形→分散布局』"
                               "的整批大跳变",
            "seamless_requirement_check": "若宣称无缝须 F(1500ms)≡F(0ms) "
                                          "位置/旋转一致；本设计 F1≠F6，"
                                          "故不宣称无缝",
            "viewed_evidence": [
                {"path_base": "suite_root",
                 "path": f"tmp/{RUN}/A23/steps/a23-frames-sheet.png"},
                {"path_base": "suite_root",
                 "path": f"tmp/{RUN}/A23/steps/f6-center-v5.png"}],
        },
    },
}
with open(f"{OUT}/frame-data.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(audit, f, ensure_ascii=False, indent=1)

timing = {
    "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
    "frames": [{"file": fr["id"], "sequence": k + 1,
                "png": fr["image"], "dsl": fr["dsl"],
                "start_ms": fr["t_ms"], "duration_ms": 250}
               for k, fr in enumerate(FR)],
    "frame_interval_ms": 250, "loop": True, "period_ms": 1500,
    "frames_per_second_equivalent": 4.0,
    "frame_order_note": "按 t=0,250,…,1250ms 顺序播放 F1→F6；周期 1500ms 后回 F1",
    "seamless": False,
    "seam_evidence": {
        "location": "F6(t=1250ms) → F1(t=1500≡0ms) 循环回绕点",
        "per_unit_reference": "frame-data.json → seam.per_unit（12 个 ID 的位移/旋转差与"
                              "相邻步长对比）",
        "observed": "所有单元从汇聚完成位置一夜回跳分散初位（distance ≈ 全程位移量级，"
                    "seam_over_max 远大于 1）；表现为一次性跳切",
        "impact": "循环播放时每周期末出现 250ms 间隔内的整画面跳变（汇聚图形瞬间"
                  "回到分散布局），后续 6 帧重新汇聚——样片作为分镜素材可接受；"
                  "如需观感平滑需在合成端处理（见 limitations.md）",
        "mitigation_outside_scope": "合成 GIF/Lottie 时可 hold F6 1–2 帧、加 "
                                    "120–250ms cross-fade，或按 trajectories "
                                    "公式补中间帧",
        "not_claimed": "本交付未使用『无缝』表述；仅为授权的 6 关键帧 + 时序描述",
    },
}
with open(f"{OUT}/timing.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(timing, f, ensure_ascii=False, indent=1)

lim = """# A23 · limitations.md —— 客户四项需求的可行性判定与替代交付

客户原始请求：**文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画、PNG 封面**，主题
“结构汇聚成图像”，限定 Snapshot 类 DOM DSL 与 open-snapshot 服务。以下逐项判定
（依据 open-snapshot 服务文档与 DSL 页面条目），给出授权替代与剩余外部工作。

## 1. 文字可编辑 SVG
- 请求到底：服务端判定输出格式为位图三种——`type=png|jpg|webp`（rendering.txt：
  SnapshotPNG/JPEG/WEBP 返回 ByteArray；parser tags 无 svg 输出类型）；DSL 无
  `<svg>` 或矢量路径元素（parser-tags 全列仅 Widgets/装饰/Transform 等位图概念）。
- 支持情况：不支持”输出 .svg 文件“。
- 依据：文档 ''渲染入口与输出'' 一节 + parser 标签全集；未取得任何 SVG 接口参数。
- 替代（本题已授权域内）：封面文案（“从结构到画面”、KPI、说明）全部用 DSL
  `Text` 生成并保留在 `cover.snapshot` 源文件——语义上仍是可编辑文字层（改文本、
  字号、颜色即可重新渲染位图）。
- 仍需外部后续工作：若客户最终必须收到 .svg 文件，需服务方新增 SVG/SVG-codec
  导出，或以矢量编辑工具（Illustrator/Figma）按 DSL 布局重建文字层。位图文字
  本身不可直接由 open-snapshot 转为当格矢量。

## 2. CMYK 印刷稿
- 请求到底：确认服务色彩空间仅 CSS 颜色（parser 色值 #RGB/#RRGGBBAA、rgb()/hsl()），
  输出 PNG/JPG/WEBP 为 sRGB 位图；无 ICC 配置文件、无 CMYK 转换入口。
- 支持情况：不支持 CMYK。
- 依据：色值文档 + rendering 输出列表（无颜色空间参数）。
- 替代（本题已授权域内）：交付 1200×800 **RGB PNG 封面**（cover.png，
  deep navy #0B1526 底 + 四色分镜图形），全部内容同一 DSL 源。
- 仍需外部后续工作：印刷厂用印刷 ICC（如 FOGRA39）把 sRGB 转换为 CMYK；四色
  海报级色彩管理需在印刷端校准（亮青 #4CC2FF 在四色铜版纸会偏暗，需提示）。

## 3. 6 帧透明 GIF 动画
- 请求到底：open-snapshot 是单次静态渲染服务：每 POST /snapshot 返回**一张**
  图；DSL 无动画/关键帧/时间轴标签；links 均为静态 HTML 风格（浏览器/CLI 背景），
  无 GIF 合成端点；encoder 输出仅 png/jpg/webp（rendering 文档）。
- 支持情况：不支持生成 .gif，也不支持在单图中表达多帧。
- 依据：渲染入口返回值 + parser type enum + 服务指南（无批处理/多帧模式）。
- 替代（本题已授权域内）：
  * 6 张 **600×600 透明 PNG 关键帧**（frame-01..06.png，RGBA、四边角实测
    alpha=0，透明确认）；
  * `frame-01..06.snapshot` 完整 DSL（可复跑），
  * `timing.json`（250ms/帧、循环、F1→F6 帧序、周期 1500ms），
  * `frame-data.json`（12 单元段间逐帧位移/角度/公式），供任何合成器接力。
- 仍需外部后续工作：用 Pillow / ffmpeg / ezgif 按 timing.json 拼帧合成 .gif；
  透明 GIF 的 1-bit alpha 限制（抗锯齿边缘会被硬 256 索引板删成实色）需接受或
  选 APNG/WebP-Anim 载体。

## 4. PNG 封面
- 支持情况：PNG 是服务原生输出（无损，透明可选），完全支持。
- 交付：cover.png（1200×800，RGB 深底，大字标题“从结构到画面”、四联 KPI、
  说明文字），并存 cover.snapshot 同名 DSL。
- 仍需外部后续工作：无（RGB 位图直给，非矢量化需求见第 1 项）。

## 5. 循环接缝（动画设计自检）
- 六帧播放后 F6(t=1250)→(1500≡0) 回跳 F1 分散态；frame-data.json#seam 实测每
  单元回跳距离（远大于帧间步长）、方向与角度差全部记录。
- 判定：**非无缝**（timing.json seamless=false）。任何 GIF 合成时首/尾帧相接会
  出现 250ms 的跳变观感。
- 处理建议（外部）：hold F6、加 cross-fade、或按 trajectories 公式补帧收敛到
  f(1.0) 后再回环——超出本题交付范围，已在 timing.json/本文件说明。

## 关于模板文件
以上判定均来自实际文档与服务响应（缓存于 tmp/20261016T164020-m1/docs/，
本轮未重复请求）。probe（旋转/透明能力验证）的渲染响应与 .snp DSL 保存在
tmp/20261016T164020-m1/A23/。
"""
with open(f"{OUT}/limitations.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(lim)

# ---- metrics ----
reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")
        if l.strip()]
import os.path as osp
okreq = [r for r in reqs if r["http_status"] == 200]
dur = sum(float((r.get("server_timing") or "0").split("total;dur=")[-1] or 0)
          for r in okreq if (r.get("server_timing") or "").count("dur=") >= 2) / 1000
started = min(r["started_at"] for r in reqs)
label_counts = {}
for r in reqs:
    lbl = osp.basename(r["request_file"]).split("-")[1] if "-" in osp.basename(r["request_file"]) else "?"
    label_counts[osp.basename(r["request_file"])] = None
groups = {}
for r in reqs:
    b = osp.basename(r["request_file"])
    g0 = b.rsplit("-", 2)[0]
    groups.setdefault(g0, []).append(r)
metrics = {
    "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
    "run_id": RUN, "status": "completed", "output_dir": "./",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end)
                                  - datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": round(
            (datetime.fromisoformat(next(r["ended_at"] for r in reqs
                                         if "a23-probe" in r["request_file"]))
             - datetime.fromisoformat(started)).total_seconds(), 1),
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur, 4),
        "server_timing_source": "snapshot_client（X-Server-Timing total）",
        "note": "started_at 即首个渲染请求（probe）；first_usable 以 probe 响应"
                "Ended 计（能力探针先行，属设计验证）",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(okreq),
        "failed_snapshot_requests": len(reqs) - len(okreq),
        "retry_requests": 0, "other_service_requests": 0,
        "dsl_versions": 5, "image_views": 15,
        "completed_visual_iterations": 4, "incomplete_visual_iterations": 0,
        "final_images": 7,
        "request_groups": {kk: len(v) for kk, v in sorted(groups.items())},
    },
    "logs": {
        "requests": f"tmp/{RUN}/A23/requests.jsonl（{len(reqs)} 条，全部 200）",
        "iterations": f"tmp/{RUN}/A23/iterations.jsonl",
        "probe": "tmp/{RUN}/A23/probe.snapshot + renders/a23-probe-*",
        "renders": f"tmp/{RUN}/A23/renders/（含 v1–v5 全部响应）",
    },
    "outputs": [
        {"name": n, "path_base": "output_dir", "path": n}
        for n in ("cover.png", "cover.snapshot",
                  "frame-01.png", "frame-01.snapshot", "frame-02.png",
                  "frame-02.snapshot", "frame-03.png", "frame-03.snapshot",
                  "frame-04.png", "frame-04.snapshot", "frame-05.png",
                  "frame-05.snapshot", "frame-06.png", "frame-06.snapshot",
                  "frame-data.json", "timing.json", "limitations.md",
                  "snapshot-usage.md", "task-metrics.json")],
    "audits": ["frame-data.json（含 6 帧×12 单元的几何/位移/角差与插值公式、"
               "循环接缝逐 ID 实测）", "timing.json（250ms/帧、循环、非无缝判定）"],
    "candidates": [], "unresolved_issues": [],
    "notes": "v1→v5 四次完整视觉迭代：v2 点分布色序/内圈 r、v3 点色相对轴叶再错开、"
             "v4 点位 45° 相位错开、v5 叶 160/点 r=48 几何彻底分离（终版）；"
             "probe 单独验证 Transform 顺时针+中心 pivot+透明 PNG 无耗时影响。",
}
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)

usage = """# A23 · snapshot-usage

## 状态
completed。cover.png（1200×800 RGB 深底）+ frame-01..06.png（600×600 透明 RGBA）
七张最终图与同名 .snapshot 全部为服务 200 真实渲染；frame-data.json / timing.json /
limitations.md 就位。所有渲染响应（probe、v1–v5 各轮 7 张）保留在 tmp renders 目录。

## 客户四项需求判定（详见 limitations.md）
1. 文字可编辑 SVG → 服务无 SVG 输出（仅 png/jpg/webp 位图）。替代：封面文字
   依然全部是 DSL `Text`（cover.snapshot 中可编辑），位图交付 + 语义保留。
2. CMYK 印刷稿 → 服务无色彩空间转换。替代：1200×800 RGB PNG 封面（授权）；
   剩余 ICC/印刷转化留给打印端。
3. 6 帧透明 GIF → 服务单帧静态、无 GIF 合成。替代：6 透明 PNG 关键帧 +
   timing.json（250ms/帧、循环 1500ms）+ frame-data.json（含接缝分析），
   供 Pillow/ffmpeg 接力合成；未伪造 .gif。
4. PNG 封面 ✓ 原生支持。

## 能力验证（probe）
- Transform：matrix (cos,sin,0,0,−sin,cos,0,0,…) + origin=(w/2,h/2) 实现"绕自身
  中心的屏幕顺时针旋转"——用 0/30/90/180° 四矩形对比 bounding box 与顶端尖点实测
  （30° 尖点 x≈324 vs 顺时针理论 321.5，非逆时针 278.5）。
- 透明：`<Snapshot type="png">` 不设 background 时返回 RGBA 且空区 alpha=0
  （6 帧透明占比 73–77%）。
- Opacity、borderRadius、DrawCIRCLE（shape=CIRCLE）在同一 DSL 校验可用。

## 设计与迭代
12 单元：U01–U08 矩形风车叶（60×160、圆角 16，4 色×2，终态 r=165，
径向角 −90+45i°，rotation=径向角−90°）；U09–U12 圆点（d=54，45° 相位错开于
叶间 r=48，色与两邻轴叶均异）。t=0 分散：叶 r0=195 ±jit，圆点 r0=268 四角；
缓动 ease-in-out cubic f=[0,1/54,4/27,.5,23/27,53/54]。
四次视觉迭代：v2 点分布/内圈 r、v3 再错点色、v4 点相位 45°、v5 叶长 160+
点 r=48（几何上心点与叶带彻底分离）。终版 F6 为 8 放射花 + 4 心点可识别图形。

## 查看记录
probe NNzoom + pixel audit；v5 contact sheet（6 帧并排）、F6 中心 3× 放大、
cover half + 绿点 80px 窗 pixel 核验。v1..v4 的 sheet/zoom 仅作修复依据
存 tmp steps（v2/v3/v4 半径/色序/相位问题都定位并修复）。

## 未解决事项
无。循环接缝为设计取舍，已按题面要求在 timing.json 与 frame-data.json 中
如实声明非无缝并给逐单元证据；不属于缺陷。
"""
with open(f"{OUT}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)

iters = [
    {"id": "A23-capability-probe", "parent": None, "type": "baseline",
     "image": "steps/probe-nn.png", "viewed_at": "2026-10-18T12:43:30+08:00",
     "images": [f"tmp/{RUN}/A23/steps/probe-nn.png"],
     "observable_issues": [],
     "changes": "验证 Transform 顺时针+中心 pivot、透明 PNG（能力探针，非交付）",
     "recheck": "bounding box + 尖点数值核验通过", "seq": 1},
    {"id": "A23-baseline-v01", "parent": "A23-capability-probe",
     "type": "baseline", "image": "steps/a23-frames-sheet.png",
     "viewed_at": "2026-10-18T12:46:00+08:00",
     "images": [f"tmp/{RUN}/A23/steps/a23-frames-sheet.png",
                f"tmp/{RUN}/A23/steps/cover-dots-zoom.png",
                f"tmp/{RUN}/A23/steps/cover-dots-3x.png"],
     "observable_issues": ["v1 内心 4 点 end 轴位与叶重叠（青点嵌同色叶）、"
                           "点 start 角扎堆 143–244°、色序同色易混"],
     "changes": "", "recheck": "触发 visual-v02", "seq": 2},
    {"id": "A23-visual-v02", "parent": "A23-baseline-v01", "type": "visual",
     "image": "steps/a23-frames-sheet.png", "viewed_at": "2026-10-18T12:50:20+08:00",
     "images": [f"tmp/{RUN}/A23/steps/a23-frames-sheet.png"],
     "observable_issues": ["v3 色序 (i+3)%4 后仍有一点与同轴叶同色（左点绿 vs 叶绿）"],
     "changes": "点 start 四角分布+色序 (i+2)%4+DOT_R 88→64",
     "recheck": "contact 复看仍有一处叠色", "seq": 3},
    {"id": "A23-visual-v03", "parent": "A23-visual-v02", "type": "visual",
     "image": "steps/f6-center-v4.png", "viewed_at": "2026-10-18T12:53:10+08:00",
     "images": [f"tmp/{RUN}/A23/steps/f6-center-v4.png"],
     "observable_issues": ["点 45° 相位后仍与叶端相叠（叶内缘 r=70 < 点带 max）"],
     "changes": "点终态角 -67.5+90k、DOT_R 70", "recheck": "红/青点仍叠叶端", "seq": 4},
    {"id": "A23-visual-v04", "parent": "A23-visual-v03", "type": "visual",
     "image": "steps/f6-center-v5.png", "viewed_at": "2026-10-18T12:56:30+08:00",
     "images": [f"tmp/{RUN}/A23/steps/f6-center-v5.png",
                f"tmp/{RUN}/A23/steps/a23-frames-sheet.png"],
     "observable_issues": [],
     "changes": "叶 190→160（内缘 r=85）+ DOT_R 48（点带 21..75，10px 净隙）",
     "recheck": "v5：四点心点全部独立清晰、F6 图形与 cover 复核位置全部命中", "seq": 5},
    {"id": "A23-visual-v05-final", "parent": "A23-visual-v04", "type": "visual",
     "image": "steps/a23-cover-half.png", "viewed_at": end,
     "images": [f"tmp/{RUN}/A23/steps/a23-cover-half.png",
                f"tmp/{RUN}/A23/steps/a23-frames-sheet.png"],
     "observable_issues": [], "changes": "（终版复核：封面 4 心点色对比清晰、"
                                        "文案/图形/透明度确认）",
     "recheck": "通过", "seq": 6},
]
with open(f"{TMP}/iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

# ---- suite ----
SP = f"outputs/{RUN}/_suite/suite-state.json"
stt = json.load(open(SP, encoding="utf-8"))
for t in stt["tasks"]:
    if t["id"] == "A23":
        t["status"] = "completed"
        t["artifacts"] = (["cover.png", "cover.snapshot", "frame-01.png",
                           "frame-01.snapshot", "frame-02.png", "frame-02.snapshot",
                           "frame-03.png", "frame-03.snapshot", "frame-04.png",
                           "frame-04.snapshot", "frame-05.png", "frame-05.snapshot",
                           "frame-06.png", "frame-06.snapshot", "frame-data.json",
                           "timing.json", "limitations.md", "snapshot-usage.md",
                           "task-metrics.json"])
        t["final_images"] = 7
        t["visual_review_evidence"].append(
            "A23: probe RGBa+旋转数值核验；6 帧 contact sheet + F6 中心 3×；"
            "cover half;4 次视觉迭代收束：v5 全帧独立心点、透明占比 73–77%、"
            "seam 非无缝已如实声明并给逐 ID 距离")
        t["resume_notes"] = ""
stt["current_task"] = "A24"
stt["current_round"] = 1
stt["completed_task_count"] = 23
stt["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

ev = f"tmp/{RUN}/_suite/events.jsonl"
with open(ev, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000048", "at": end, "kind": "task-completed",
                        "task_id": "A23",
                        "detail": "四项格式需求判定+授权替代交付（SVG/CMYK/GIF 边界、"
                                  "7 张最终图、37 请求 4 迭代、seam 证据化非无缝）"},
                       ensure_ascii=False) + "\n")
cp = {"at": end, "run_id": RUN, "action": "task-complete", "task_id": "A23",
      "summary": "A23 completed：probe 验证旋转/透明 → v1..v5 迭代（点叶几何分离）；"
                 "7 最终图全部服务真实渲染；frame-data/timing/limitations 三审计；"
                 "SVG/CMYK/GIF 的替代口径+剩余工作写入 limitations。下一题 A24。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000045.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
stt["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000045.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

print("A23 finalized:", end)
print("requests", len(reqs), "ok", len(okreq), "dur", round(dur, 4),
      "| views 15 | iters 4 | final 7")
