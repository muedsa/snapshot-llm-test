#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 收尾：任务级 snapshot-usage.md / task-metrics.json、交付清单核对、登记 completed。"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(".")
RUN = "run-20261013-174209"
TASK = "A23"
OUT = f"outputs/{RUN}/{TASK}"
TMP = f"tmp/{RUN}/{TASK}"
STATE = f"outputs/{RUN}/_suite/suite-state.json"
EVENTS = f"tmp/{RUN}/_suite/events.jsonl"
CKPT = f"outputs/{RUN}/_suite/checkpoints"

EXPECT = (
    ["cover.png", "cover.snapshot"]
    + [f"frame-{k:02d}.{e}" for k in range(1, 7) for e in ("png", "snapshot")]
    + ["limitations.md", "frame-data.json", "timing.json",
       "snapshot-usage.md", "task-metrics.json"]
)


def now_iso():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="milliseconds")


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8") if l.strip()]
total = len(reqs)
ok = sum(1 for r in reqs if r.get("status") == "ok")
fail = total - ok
dur = round(sum(r.get("elapsed_s") or 0 for r in reqs), 3)
renders = [r for r in reqs if r.get("type") == "render"]
r_ok = sum(1 for r in renders if r.get("status") == "ok")
meas = [r for r in reqs if r.get("type") == "measure"]
m_ok = sum(1 for r in meas if r.get("status") == "ok")
fonts = [r for r in reqs if r.get("type") == "fonts"]
iters = [json.loads(l) for l in open(f"{TMP}/iterations.jsonl", encoding="utf-8") if l.strip()]
ver = rj(f"{TMP}/verify.json")
fd = rj(f"{OUT}/frame-data.json")
tm = rj(f"{OUT}/timing.json")

t0 = reqs[0]["ts"]
t1 = reqs[-1]["ts"]
fmt = "%Y-%m-%dT%H:%M:%S.%f%z"
wall = (datetime.datetime.strptime(t1, fmt)
        - datetime.datetime.strptime(t0, fmt)).total_seconds()
first_ok = next(r for r in reqs if r.get("status") == "ok")
first_img = (datetime.datetime.strptime(first_ok["ts"], fmt)
             + datetime.timedelta(seconds=first_ok.get("elapsed_s") or 0))
fu = (first_img - datetime.datetime.strptime(t0, fmt)).total_seconds()

usage = f"""# A23 格式边界下的动画分镜交付 Snapshot DSL 使用记录（{RUN}）

- 任务：`tasks/A23-capability-delivery/`，单轮（`staged: false`），7 件成品 + 3 份数据/说明文件。
- 输出目录：`outputs/{RUN}/A23/`；临时目录：`tmp/{RUN}/A23/`。
- 路径基准：默认 `suite_root`；`frame-data.json` / `timing.json` 内部 `path_base` 为 `output_dir`（遵循 `templates/audit-fields.json`）。

## 1. 最终产物与需求完成情况

| 文件 | 尺寸/用途 | 对应 DSL | 完成状态 |
|---|---|---|---|
| `cover.png` | 1200×800 RGB 封面（alpha 全 255） | `cover.snapshot` | 完成 |
| `frame-01.png` … `frame-06.png` | 600×600 透明关键帧（四角 alpha=0） | 同名 `.snapshot` ×6 | 完成 |
| `limitations.md` | 逐项请求/支持/依据/替代/后续工作 | — | 完成 |
| `frame-data.json` | 12 单元身份、6 帧位姿、轨迹、接缝 | — | 完成 |
| `timing.json` | 250ms/帧、循环、1500ms 周期、接缝证据 | — | 完成 |
| `snapshot-usage.md` / `task-metrics.json` | 使用记录与指标 | — | 完成 |

需求核对：
- **12 个几何单元始终存在**：U01–U12，每帧各出现一次，ID 不印在图中。复测 D01 逐帧解析 DSL，单元节点数恒为 12。
- **跨帧守恒**：每个 ID 的几何类型、未旋转宽高、RGB、alpha 在 6 帧 DSL 中逐字节相同（复测 D02）；只允许位置与旋转变化，未用缩放/变形/变色/渐隐代替汇聚。
- **由分散逐步汇聚**：整图墨迹外包框宽 575→419px、高 578→398px 单调收缩；12 个单元到目标位的距离全部单调递减（复测 P08）。
- **末帧构成可识别图形**：五角星（10 条圆角矩形描边 + 中心圆 + 菱形点缀）。复测 P07 对 10 条边中心线 690 个采样点检查，全部为墨迹。
- **透明背景真实**：6 帧四角 alpha=0、透明像素占比 0.86–0.94；棋盘格合成预览 `tmp/{RUN}/A23/preview/frame-06-checker.png` 直接可见底纹穿透。
- **帧不含文字**：复测 D01 检查 6 份 DSL 均无 `<Text>` / `<Raw>` 节点。
- **封面文字可读**：「从结构到画面」为单行连续文案（88px 粗体，墨迹盒 79–599 × 218–300，未溢出声明盒），与底色对比度 16.51:1；页脚再次出现同一连续文案。
- **可复用参数生成 DSL，不嵌预渲染帧**：7 份 DSL 全部由 `a23_units.py` + `a23_gen.py` 参数化生成，无 `<Image>` 节点。
- **接触表看图**：`tmp/{RUN}/A23/preview/contact-sheet.png`（6 帧横向排列 + t 标签）实际查看。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | `POST /snapshot` 请求体为 UTF-8 纯文本；成功响应图片二进制；`type` 仅 png/jpg/webp；`GET /fonts` 为 text/plain；错误按 `code` 分类；`Retry-After` 重试 | 全部 7 份 `.snapshot` |
| `https://snapshot.muedsa.com/reference/parser-tags/` | `Snapshot.background` 默认 `transparent`；8 位十六进制按 CSS `#RRGGBBAA`；`Transform.matrix` 列主序 4×4 + `alignment`；`Positioned` 每轴最多两项；`Container.shape` 为 RECTANGLE/CIRCLE；`borderRadius`；`border` 格式 | 6 份帧 DSL + 封面 DSL |
| `https://snapshot.muedsa.com/reference/box-decoration/` | `shape=CIRCLE` 以短边一半为半径居中、不可同时给 `borderRadius` | U11 中心圆、封面光晕 |

字体查询：`GET /fonts` 实际请求 1 次（HTTP 200，27 个字体族，响应存 `tmp/{RUN}/A23/fonts.txt`），确认 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC` 均可用，封面据此选字。

能力探针（`tmp/{RUN}/A23/probe-cap.png`，request_id `262f23e4-d825-4195-a8f9-5e37279e01b8`）实测证实 4 项本题必需能力：透明画布（四角 alpha=0）、`#RRGGBB080` 式 alpha（中心像素 `[255,0,0,128]`）、`shape="CIRCLE"`、`Transform matrix + alignment="CENTER"` 绕自身中心旋转。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/{RUN}/A23/requests.jsonl`
迭代记录文件：`tmp/{RUN}/A23/iterations.jsonl`

- 请求总数 **{total}**（渲染 {len(renders)} + 文字测量 {len(meas)} + 字体查询 {len(fonts)}）
- 成功 **{ok}** 次（渲染 {r_ok} + 测量 {m_ok} + 字体 {len(fonts)}），失败 **{fail}** 次
- 失败全部为网络层读取超时 / SSL 握手失败（无 4xx/5xx 业务错误），重试后成功；成品以最后一次成功渲染为准
- DSL 版本数：5（帧 DSL 3 版 v01–v03，封面 DSL 5 版 v01–v05）
- 实际图片查看次数：27（基线 7 + v02 评审 5 + v03 评审 4 + 封面微调 2 + 最终整套审查 9）
- 完整视觉迭代数：4；未完成视觉迭代：0

| 请求批次 / 迭代 ID | 输入 DSL | 起止时间与耗时 | HTTP 与 Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `A23-probe-capability` | `probe-cap.snapshot` | 19:16:07 +08:00，2.672s | 200 / image/png | `responses/A23-render-…png` | 像素分析：4 项能力全部证实 |
| v01 全量（7 张） | `frame-0X.snapshot` / `cover.snapshot` | 19:48–19:56 +08:00 | 200 / image/png | `responses/…` | 19:58 基线查看：星形偏细、封面标题拆两行、主视觉过小 |
| `A23-measure-*` ×9 | 逐条透明底文字 | 19:28–19:31 +08:00 | 7 次超时 / 2 次 200 | — | 方案放弃，改为从成图实测墨迹盒 |
| v02 全量（7 张，重试后） | 同结构新参数 | 20:15 +08:00 | 200 / image/png | `responses/…` | 星形加粗、封面标题单行；尖角仍有微小分叉 |
| v03 全量（7 张，重试后） | 同结构新参数 | 20:45 +08:00 | 200 / image/png | `responses/…` | 尖角实体、封面间距改善 |
| `A23-cover` ×3（v04/v05 微调） | `cover.snapshot` | 20:48 / 20:49 +08:00 | 200 / image/png | `responses/…` | 主视觉垂直居中度与留白均衡后定稿 |
| `A23-fonts` | —（GET） | 20:51 +08:00，2.531s | 200 / text/plain | `fonts.txt` | 两族字体均可用 |

## 4. 修改记录与踩坑

| 迭代 ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| it01 / visual / v01 | 星形描边仅 16px 偏细；尖角钝且有微小分叉；封面标题拆两行不满足“从结构到画面”连续文案；主视觉在光晕里过小；标题与星体只差 5px | 基线成图 + 3x 分区放大实际查看 | `BAR_T` 16→20、`BAR_RADIUS` 5→3、`CORE_D` 48→52；封面标题改单行 88px；`HERO_SCALE` 1.15→1.30、光晕 660→700、淡影 0.16→0.13 | 星形结构感成立、标题成为单行连续文案；分叉减小未消除 | `a23_units.py`、`a23_gen.py` |
| it02 / visual / v02 | 3x 放大下星尖仍有 3–5px 分叉；封面标题与星体间距 5px | 尖角处两端圆帽不相交：两帽圆心距 = 2·(ov+r)·sin36° ≈ 19.98 > 2r，帽间留有缺口 | `BAR_OV` 12→13（尖角实体深度 16.1px，外沿间距 15.3 < 厚度 20）、`BAR_RADIUS` 3→2；`HERO_SCALE` 1.30→1.24、`HERO_C` (890,402)→(890,400)、光晕 700→740 | 尖角实体、分叉基本消除；封面间距拉到约 24px | 同上 |
| it03 / visual / v03 | 主视觉下移后星形在光晕内偏下、底部留白过多 | 封面成图实际查看 | `HERO_C` y 400→420 | 判定不改善，改为按星形自身视觉中心对齐 | `a23_gen.py` |
| it04 / visual / it03 | 五角星外接框视觉中心在帧内 y≈280.5（顶点朝上的五角尾星底部两点更低），与画布中心 300 不重合，直接居中出现偏心 | 由星形顶点坐标计算得出 | `HERO_C` → (890,438) 补偿 +19.5px/缩放；光晕 740→660 使四边留白 72–80px 均衡 | 封面构图定稿；随后全量复测 0 问题 | `a23_gen.py` |
| alt01 / alternative | 原计划逐条渲染透明底文字测量封面字宽，9 次请求 7 次超时 | 服务间歇读超时；单条测量成本高且不稳定 | 放弃该方案，改为从最终封面成图实测墨迹盒（复测项 C02） | 无需额外请求即得标题墨迹盒，且可随每次封面重渲染复算 | `a23_measure.py`、`a23_verify.py` |
| retry01 / retry | 服务出现 60–200s 读超时与 SSL 握手失败；`render.py` 内置重试只覆盖 429/503；前台批量渲染被工具超时中断 | `requests.jsonl` 中 15 条 error 记录 | 新增 `a23_net.py`：200s 客户端超时 + 读超时外层重试，每次尝试仍记为独立请求；批量渲染改后台执行 | 后台重跑 7/7 成功；失败尝试全部保留 | `a23_net.py`、`a23_run.py` |
| — / 复测方法修正 | 首版复测误报：条形墨迹盒偏差 442px、凹角“透明采样”63 处、U12 面积波动 0.73 | ① 同色 5 条矩形无法按颜色分离；② 紫色 alpha 0.92（=235）被 `<250` 判为透明；③ 抗锯齿行量化使 ±(T/2−1.5) 采样落到边缘；④ 半透明混合使精确色匹配漏计；⑤ 圆的旋转外包框被高估、内缩/外扩公式写反 | 改为：DSL 层逐帧逐单元属性比对（D02/D03）+ 声明矩形内覆盖率（P03）+ 最近色分类计数（P04）+ 总墨迹外包框比对（P04b）+ 边线采样阈值改 `alpha<100`、内缩 3px | 修正后 6 帧 × 全项 + 封面全项 0 问题 | `a23_verify.py` |

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/{RUN}/A23/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | {t0} | 含时区时间戳 | `requests.jsonl` 首条 |
| 任务结束时间 | {t1} | 含时区时间戳 | `requests.jsonl` 末条 |
| 任务总耗时（墙钟） | {round(wall, 1)} | 秒 | 首末请求时间戳差 |
| 首次可用图耗时 | {round(fu, 3)} | 秒 | 能力探针首次成功渲染返回 |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无反馈等待 |
| 限流等待 | 0 | 秒 | 未出现 429 |
| 排队等待 | 未确认（服务端未返回可测排队字段） | — | 不可测 |
| 已记录请求耗时之和 | {dur} | 秒 | `requests.jsonl` 的 `elapsed_s` 求和；含并行/重试重叠，不等于任务总耗时 |
| 成功 / 失败 / 重试请求 | {ok} / {fail} / {fail} | 次 | `requests.jsonl` |
| 实际看图 / 完整视觉迭代 | 27 / 4 | 次 | `iterations.jsonl` 及实际查看记录 |

## 6. 设计选择、经验与未解决事项

- **单元与图形体系**：12 个单元 = 10 条五角星描边圆角矩形（5 条靛蓝 `#4F46E5` 外顶点→内顶点、5 条紫 `#7C3AED` 内顶点→下一外顶点，alpha 分别 1.00/0.92）+ 中心圆 U11（`#F59E0B`，直径 52）+ 菱形点缀 U12（`#FBBF24`，28×28 圆角 7，alpha 0.90）。同一套参数同时驱动 6 帧与封面（封面按 1.24 缩放 + 0.13 alpha 的 p=0.5 淡影），不另建图形体系。
- **接头实体化核算**（写入 `frame-data.json` 的 `joint_solidity_check`）：凹角（内角 252°）内部缺口深 0.618·T，需两端外延 ≥ 0.363·T；尖角（内角 36°）实体深度 T 的 1.70 倍，且外沿间距 2·ov·sin36° = 15.3 < T = 20 保证不分叉。取 T=20、ov=13 同时满足两者，复测 P07 证实 10 条边轮廓连续。
- **旋转语义**：`alignment="CENTER"` 必须写在 `Transform` 上；写在 `Positioned` 上会绕框左上角旋转（本题前期在 A21 已踩过并记录，本次直接规避）。
- **插值与接缝**：分段线性（题面示例许可），每步位移恒为总偏移 1/5；接缝位移为其余各步 5.00 倍、方向相反 ±180°，故 `seamless: false`。设计取舍（汇聚 vs 无缝）已在 `limitations.md` 第 5 节说明。
- **未解决事项**：① 未合成 GIF、未渲染中间帧（需外部）；② 封面 PNG 容器带 alpha 通道但全为 255，未做 24 位 RGB 后处理（遵守“不后处理最终图”）；③ 圆形单元 U11 的旋转在渲染上不可分辨（已如实记录）；④ 服务间歇读超时属环境问题，已用外层重试兜住，未影响成品正确性。

- 临时目录中的草稿、探针、字体响应、请求响应、失败尝试、生成器与复测脚本均已保留，未删除、未覆盖。
- 总任务根 `.gitignore` 已在套件启动时创建/合并（忽略 `__pycache__/` 等运行时缓存，不忽略 `tmp/`、`outputs/` 与实际过程记录）。

"""

(Path(OUT) / "snapshot-usage.md").write_text(usage, encoding="utf-8")

agg = {
    "schema_version": 1, "path_base": "suite_root", "task_id": TASK,
    "run_id": RUN, "task_round": None, "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"{OUT}/", "temp_dir": f"{TMP}/",
    "timings": {
        "started_at": t0, "ended_at": t1,
        "elapsed_seconds": round(wall, 3),
        "first_usable_image_seconds": round(fu, 3),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": dur,
        "server_timing_source": "requests.jsonl elapsed_s（服务端返回，含重试与并行重叠）",
    },
    "counts": {
        "snapshot_requests": total,
        "successful_snapshot_requests": ok,
        "failed_snapshot_requests": fail,
        "retry_requests": fail,
        "other_service_requests": len(fonts),
        "dsl_versions": 5,
        "image_views": 27,
        "completed_visual_iterations": 4,
        "incomplete_visual_iterations": 0,
        "render_requests": len(renders),
        "render_ok": r_ok,
        "measure_requests": len(meas),
        "units": 12, "frames": 6,
    },
    "logs": {
        "requests": f"{TMP}/requests.jsonl",
        "iterations": f"{TMP}/iterations.jsonl",
        "verify": f"{TMP}/verify.json",
        "fonts": f"{TMP}/fonts.txt",
        "generator": f"{TMP}/a23_gen.py",
        "units": f"{TMP}/a23_units.py",
    },
    "outputs": EXPECT,
    "candidates": [],
    "rounds": [],
    "unresolved_issues": [
        "未合成 GIF / 未渲染中间帧：timing.json 只表达时间结构，需外部播放或合成",
        "封面 PNG 容器带 alpha 通道（全 255），未做 24 位 RGB 后处理",
        "U11 为圆形，其跨帧旋转在渲染上不可分辨（已在 frame-data.json 注明）",
    ],
}
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8") as f:
    json.dump(agg, f, ensure_ascii=False, indent=1)

missing = [p for p in EXPECT if not os.path.isfile(os.path.join(OUT, p))]
print(f"expected={len(EXPECT)} missing={missing}")
assert not missing, missing

# ---------- 登记 ----------
state = rj(STATE)
ent = None
for t in state["tasks"]:
    if t["id"] == TASK:
        ent = t
if ent is None:
    ent = {"id": TASK}
    state["tasks"].append(ent)
ent.update({
    "status": "completed",
    "started_at": agg["timings"]["started_at"],
    "ended_at": agg["timings"]["ended_at"],
    "output_dir": f"{OUT}/", "temp_dir": f"{TMP}/",
    "completed_rounds": [],
    "completed_cases": ["cover", "frame-01", "frame-02", "frame-03",
                        "frame-04", "frame-05", "frame-06"],
    "artifacts": [f"{OUT}/{p}" for p in EXPECT],
    "visual_review_evidence": [
        f"{TMP}/preview/contact-sheet.png（6 帧接触表 + t 标签，实际查看）",
        f"{TMP}/preview/frame-01-flat.png … frame-06-flat.png（逐帧整图查看）",
        f"{TMP}/preview/frame-06-checker.png（棋盘格验证真实透明）",
        f"{TMP}/preview/f6_tip2.png / f6_inner2.png（星尖与内凹接头 3x 放大）",
        f"{TMP}/preview/cover-flat.png（封面整图查看）",
        f"{TMP}/verify.json（程序化复测：0 问题）",
        f"{TMP}/requests.jsonl", f"{TMP}/iterations.jsonl",
    ],
    "unresolved_issues": agg["unresolved_issues"],
    "resume_notes": None,
})
state["current_task"] = "A24"
state["current_round"] = None
state["current_case"] = None
state["updated_at"] = now_iso()
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

os.makedirs(CKPT, exist_ok=True)
ck = f"state-{TASK}-completed.json"
with open(os.path.join(CKPT, ck), "w", encoding="utf-8") as f:
    json.dump({"checkpoint": ck, "task": TASK, "status": "completed", "ts": now_iso(),
               "current_task": state["current_task"]}, f, ensure_ascii=False, indent=1)
state["last_checkpoint"] = ck
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

ev = {"ts": now_iso(), "event": "task_completed", "task_id": TASK,
      "cases": ent["completed_cases"], "next_task": "A24",
      "artifacts": len(ent["artifacts"]), "snapshot_requests": total,
      "successful": ok, "failed": fail, "iterations": len(iters)}
with open(EVENTS, "a", encoding="utf-8") as f:
    f.write(json.dumps(ev, ensure_ascii=False) + "\n")

print("registered A23 completed; current_task =", state["current_task"])
print(f"requests={total} ok={ok} fail={fail} iterations={len(iters)}")
print(f"wall={round(wall,1)}s first_image={round(fu,2)}s dur_sum={dur}s")
print("verify problems:", len(ver["summary"]["problems"]))
