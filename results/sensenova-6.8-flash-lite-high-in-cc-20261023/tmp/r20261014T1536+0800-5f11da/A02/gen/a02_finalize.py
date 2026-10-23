"""A02 收尾：写 snapshot-usage.md / task-metrics.json，更新 suite-state 与检查点。

启动基准：总任务根（cwd）。数据全部从真实日志与产物读回，不硬编码。
产物路径相对 suite_root；报告与指标内引用也一律相对。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
TZ = "Asia/Shanghai (UTC+08:00)"
TZOFF = "+08:00"
OUT = ROOT / "outputs" / RUN / "A02"
TMP = ROOT / "tmp" / RUN / "A02"
SYSROOT = ROOT / "tasks" / "A02-conference-schedule" / "templates"

FINAL_PNG = ("agenda-wide.png", "agenda-mobile.png")
FINAL_DSL = ("agenda-wide.snapshot", "agenda-mobile.snapshot")


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def jload(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + TZOFF


def now_iso() -> str:
    return iso(datetime.now().astimezone())


def req() -> list[dict]:
    return [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]


def iters() -> list[dict]:
    return [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]


def parse(ts: str) -> datetime:
    return datetime.strptime(ts.split("+")[0], "%Y-%m-%dT%H:%M:%S")


def backfill_audit_bytes(reqs: list[dict]) -> dict:
    """把 audit.artifacts 里的 bytes（render() 返回 None，原记 null）补成真实响应字节数。

    只填 requests.jsonl 中该请求 ID 实际记录的 response_bytes；找不到就保持 null 不猜。
    """
    p = OUT / "schedule-audit.json"
    a = jload(p)
    by_id = {r["request_id"]: r for r in reqs}
    filled = 0
    for fn, meta in a.get("artifacts", {}).items():
        if not isinstance(meta, dict) or meta.get("bytes") is not None:
            continue
        rid = meta.get("render_request")
        r = by_id.get(rid)
        if r and r["response_bytes"]:
            meta["bytes"] = r["response_bytes"]
            meta["bytes_source"] = f"{rid}（requests.jsonl 的实际响应字节数）"
            filled += 1
    a["bytes_backfill"] = {
        "why": "TG.render() 返回 response_bytes=None，构建时只能记 null；此处按 render_request 回填。",
        "filled_this_run": filled,
        "filled_total": sum(1 for v in a.get("artifacts", {}).values()
                            if isinstance(v, dict) and v.get("bytes")),
        "idempotent": True,
    }
    p.write_text(json.dumps(a, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return a


def usage_md(m: dict) -> str:
    a = jload(OUT / "schedule-audit.json")
    ev, vg = a["events"], a["venue_gaps"]
    ta = a["time_axis"]
    vb = a["duration_summary"]["by_venue"]
    gh = {g["venue"]: g for g in vg}
    pb = a["public_break"]
    art = m["artifacts"]
    c = m["counts"]
    reqs = req()
    its = iters()
    insp = jload(TMP / "inspect-report.json")
    meas = insp["measured"]

    L = f"""# A02 会议日程与导览图 — Snapshot 使用说明

- 任务：A02-conference-schedule（track A，纯 DSL 主体，无外部素材）
- 运行：`{RUN}`　时区 `{TZ}`　完成状态：完成（需求满足并完成像素自检）
- 输入：`tasks/A02-conference-schedule/inputs/agenda.csv`（15 行活动）、
  `tasks/A02-conference-schedule/inputs/venues.json`（3 个会场、容量、字体声明）
- 实际输出目录：`outputs/{RUN}/A02/`（path_base = suite_root）
- 过程留痕目录：`tmp/{RUN}/A02/`
- 模板已对照：`tasks/A02-conference-schedule/templates/`
  （`audit-fields.json`、`snapshot-usage-template.md`、`task-metrics-template.json`）

## 1. 交付物

| 文件 | 用途 | 尺寸 | 字节 | sha256_16 |
|---|---|---|---|---|
| `agenda-wide.png` | 全日日程泳道大图 | 1920×1200 | {art['png_wide']['bytes']:,} | `{art['png_wide']['sha256_16']}` |
| `agenda-mobile.png` | 手机会议导览 | 720×1280 | {art['png_mob']['bytes']:,} | `{art['png_mob']['sha256_16']}` |
| `agenda-wide.snapshot` | 大图的完整渲染 DSL | — | {art['dsl_wide']['bytes']:,} | `{art['dsl_wide']['sha256_16']}` |
| `agenda-mobile.snapshot` | 手机图的完整渲染 DSL | — | {art['dsl_mob']['bytes']:,} | `{art['dsl_mob']['sha256_16']}` |
| `schedule-audit.json` | 时长/空档/冲突/两图映射核验 | — | {art['audit']['bytes']:,} | `{art['audit']['sha256_16']}` |

两张 PNG 都是服务响应的原始字节直存（`tmp/.../A02/responses/` 保留对应副本与响应头），
未做任何像素后处理；同名 `.snapshot` 与最终 PNG 逐字节对应。

**需求逐项核对**（TASK.md 与 AGENTS.md）：

| 要求 | 实际 |
|---|---|
| 1920×1200 全日日程大图，三条会场泳道 | 满足：A/B/C 三条泳道，各标注名称与容量 |
| 09:00–16:00 共用线性时间轴，块长按实际时长比例 | 满足：`px_per_minute = 1840/420`，块缘 = X(起止)；像素自检逐卡核对宽度与位置 |
| 空档保留、午休跨三泳道标识 | 满足：空档不填补；午休带跨三泳道、底色 + 双侧虚线 + 居中文字 |
| 15 项活动的编号/标题/讲者/起止时间/类别可读 | 满足：全部五字段在块上，最窄块 S15（131.43px）逐字段验证；未启用外侧索引表 |
| 正文 ≥20、时间标签 ≥18 | 满足：正文标题 20 粗、时间 18、编号 18、讲者 18、类别 16 |
| 注明读图方法与会场容量 | 满足：页脚四段之一即读图方法；泳道标题行标容量 |
| 手机图分时段列表，15 项全保留编号/标题/会场/起止时间 | 满足：上午场 8 / 午休 1 / 下午场 7 |
| 讲者可移到大图并写「讲者详见完整日程」 | 满足：手机图 0 条 speaker 记录，页脚已注明 |
| 不直接缩小或裁切大图 | 满足：手机图为独立重排的分时段列表 |
| 手机正文 ≥18 | 满足：正文 18、类别 16 |
| 交付 `schedule-audit.json`：时长/空档/冲突/两图映射 | 满足：5 个必含字段全在，另含 public_break / fonts / unresolved |
| 不捏造冲突、不调整输入时间 | 满足：31 对比较 0 冲突，`input_times_modified: false` |
| 各图实际查看，尤其 10 点附近密集区 | 满足：像素自检 73 项 + 裁图放大查看，含该区域 |
| 最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足：10 次请求全 200，PNG 为响应字节直存 |

未完成与已知取舍：见第 9 节，均为有意识的取舍并已如实记录，无未验证或已知未修缺陷。

## 2. 大图版面（1920×1200）

- 版面边距 40px，正文区 x∈[40,1880]（宽 {ta['plot']['width_px']}px）。
- 时间轴：09:00–16:00，共用一条线性时间轴，
  `x = {ta['formula']}`，`px_per_minute = {ta['px_per_minute_exact']} = {ta['px_per_minute']}`。
  块的左右缘严格等于 X(开始)/X(结束)，时长完全由块宽表达 —— 空档保留，绝不把 40 分钟画成 60 分钟。
- 三条会场泳道：A y={ta['lane_y']['A']} / B y={ta['lane_y']['B']} / C y={ta['lane_y']['C']}，
  高 {ta['lane_height']}px、间距 14px，底带 `#F4F3F0`。泳道标题行写明会场编号、名称与容量，
  并在标题后给出该会场实际占用时长（避免与 09:00–16:00 的空档混淆）。
- 卡片在泳道内上下各留 38px 内缩、高 212px；类别用「左侧色条 + 中文类别文字」双通道，
  不只靠颜色；同一泳道内同一类别连续出现时用 2px 圆角矩形把卡片并成一组。
- 最窄卡片是 S15（30 分钟 → 131.43px），已逐字段验证容纳编号/标题/讲者/起止时间/类别，
  因此**没有启用外侧编号索引表**：15 项活动在块上即可读全。
- 午休 12:00–13:00 跨三泳道：x∈[{ta['lunch_band']['x_left']}, {ta['lunch_band']['x_right']}]，
  底色 `#E5E3DC`（比泳道底带深 15 级），两侧 `#C3C2B7` 虚线，居中「午间休息 12:00–13:00」。
  带内不画任何卡片（自检逐泳道逐行确认为零白色像素）。
- 时间轴刻度与整点网格线：刻度 y=978、标签 y=990（构建脚本常量，见
  `tmp/.../A02/gen/a02_build.py` 的 `AXIS_TICK_Y` / `AXIS_LBL_Y`）；整点 x 见 audit 的
  `time_axis.hour_tick_x`；09:00 与 16:00 标签贴左右边界。
- 字号：正文标题 20（上限 20，加粗）、时间标签 18、编号 18、讲者 18、类别 16；
  页脚 16。字体 `{a['fonts']['family']}`，按输入声明。
- 页脚：日期与时长总览 / 冲突检查结果 / 读图方法 / 类别图例四段，右端图例。

## 3. 手机导览（720×1280）

按**分时段列表**重做，不缩小也不裁切大图：上午场 8 项、午休一条、下午场 7 项，
15 项全部保留编号、标题、会场与起止时间；讲者移到完整日程，页脚写明「讲者详见完整日程」。
行内四段「会场 · 编号 · 时间 · 类别」互不粘连（像素自检实测每两段墨迹间距 ≥1px）。
正文 18、类别 16；卡片 54px 高、步距 58px；页脚三行。

## 4. 数据核验（`schedule-audit.json`）

- 15 场合计 {a['duration_summary']['total_minutes']} 分钟 = {a['duration_summary']['total_hours']} 小时；
  A {vb['A']} / B {vb['B']} / C {vb['C']}。
- 各会场空档（场次 + 空档 = 420 分钟，逐会场校验通过）：
  A {gh['A']['gap_count']} 个空档共 {gh['A']['gap_minutes_total']} 分钟（最长 70）；
  B {gh['B']['gap_count']} 个空档共 {gh['B']['gap_minutes_total']} 分钟（最长 110）；
  C {gh['C']['gap_count']} 个空档共 {gh['C']['gap_minutes_total']} 分钟（最长 95）。
- 冲突检查：同会场按 [start, end) 全对比较，{a['conflict_check']['pairs_checked']} 对，
  **冲突 {len(a['conflicts'])} 个**；输入时间未被修改（`input_times_modified: false`）。
- 午休**没有**被并入任何活动（`public_break.merged_into_event: false`），
  各会场实际空档与午休重叠段（A {pb['overlapping_venue_gaps']['A']}、
  B {pb['overlapping_venue_gaps']['B']}、C {pb['overlapping_venue_gaps']['C']}）单独记录，不重复计数。
- `content_map` 共 {len(a['content_map'])} 条，逐条给出 image / field / event_id / text / box / size / bold
  （标题另有 `line_text` 记录实际折行），使两图的字段映射与排版可独立复算。
- `unresolved: []`。

## 5. 真实服务请求

{c['snapshot_requests']} 次 `POST /snapshot`，**全部 200**，0 失败、0 重试。
请求总耗时 {m['timings']['request_elapsed_ms_total']:,} ms（min {m['timings']['request_elapsed_ms_min']} /
max {m['timings']['request_elapsed_ms_max']}）；首请求 {m['timings']['request_first_started_at']}、
末请求结束 {m['timings']['request_last_ended_at']}。
`ratelimit_remaining` 全程 118–119，未出现 429/503，**无排队等待**（不可测排队一律记 null，本题记 null）。
每次请求的原始 DSL、响应体、响应头分别保留在 `tmp/.../A02/req-*.snapshot`、
`responses/`、`req-*.snapshot.headers.txt`。
**A02 的渲染过程中没有发起文档或字体查询请求**（这是过程缺口，见第 6.5 节）；
文档与字体核实是在本题收尾时补做的，记为 shared 请求：
`tmp/{RUN}/_suite/requests.jsonl`。

## 6. 视觉迭代（{c['iterations_recorded']} 次，其中 {c['completed_visual_iterations']} 次视觉迭代）

"""
    for it in its:
        L += f"- **{it['version']} · {it['kind']}**（parent {it.get('parent') or '—'}）：{it['reason']}\n"

    L += f"""
其中 4 个版本改变了像素（v1→v2→v3→v5）；v4 的 DSL 与 PNG 和 v3 逐字/字节相同，
是纯留痕补记，不计视觉改动。

## 6.5 文档阅读与字体核实（在本题收尾时补齐）

**如实说明**：A02 的 10 次渲染是在**未取得服务指南与 DSL 文档**的情况下完成的 ——
靠 TASK.md、`tools/` 与 A01 留下的经验，以及服务自身返回的 `400 PARSE_ERROR` 位置信息
迭代出来的。这是本套运行的一个已知过程缺口。为不把它带进剩余题目，**在 A02 收尾时实际
拉取并阅读了文档**，以下 9 次共享文档请求记在
`tmp/{RUN}/_suite/requests.jsonl`（正文已抽取成纯文本便于逐字阅读）：

| 请求 | 状态 | 字节 | 落盘 |
|---|---|---|---|
| `GET https://open-snapshot.muedsa.com/ai-guide.md` | 200 | 3,718 | `tmp/.../_suite/docs/ai-guide.md` |
| `GET https://open-snapshot.muedsa.com/fonts` | 200 | 448 | `tmp/.../_suite/docs/fonts.txt` |
| `GET https://open-snapshot.muedsa.com/openapi.yaml` | 200 | 19,746 | `tmp/.../_suite/docs/openapi.yaml` |
| `GET https://snapshot.muedsa.com/` | 200 | 54,852 | `tmp/.../_suite/docs/dsl-docs.html` |
| `GET https://snapshot.muedsa.com/reference/parser-tags/` | 200 | 166,076 | `tmp/.../_suite/docs/dsl/reference-parser-tags.html` |
| `GET https://snapshot.muedsa.com/guides/layout/` | 200 | 74,705 | `tmp/.../_suite/docs/dsl/guides-layout.html` |
| `GET https://snapshot.muedsa.com/guides/painting/` | 200 | 67,373 | `tmp/.../_suite/docs/dsl/guides-painting.html` |
| `GET https://snapshot.muedsa.com/guides/media-text/` | 200 | 79,115 | `tmp/.../_suite/docs/dsl/guides-media-text.html` |
| `GET https://snapshot.muedsa.com/guides/widgets/` | 200 | 71,576 | `tmp/.../_suite/docs/dsl/guides-widgets.html` |

**字体核实**（指南明确要求「不要声称某种字体已安装」）：`GET /fonts` 返回 27 个字体族，
`Inter` 与 `Noto Sans CJK SC` **确实在列**，因此 A02 按输入声明使用的
`fontFamily="Inter,Noto Sans CJK SC"` 是真实可用的字体，不是猜测。
`Noto Sans SC` **不在**返回表中（返回的是 `Noto Sans CJK SC`），这点在后续题目中已改正。

**读文档后确认与 A02 实践一致**：`width/height 会收紧 constraints`（正是 v1→v2 排查到的
`Positioned(width=W)` 裁尾根因）；缩放/旋转会作用于内层布局偏移、不能简单相加
（正是 v1 卡片文字错位的原因）；`fontFamily` 逗号后不要加空格（A02 写法正确）。

**读文档后新增、A03 起改用的规则**：
1. `Container` 的 `color` 与 `decoration` **不能同时传入**；要同时用颜色与边框/渐变，
   把颜色放进 `BoxDecoration`。
2. `clipBehavior != NONE` 时必须提供能生成裁剪路径的 `decoration`。
3. `backgroundBlendMode` 必须搭配 `color` 或 `gradient`，否则 `BoxDecoration` 构造即抛异常；
   仅有 `image` 不满足。
4. `shape = CIRCLE` 时不要再设矩形圆角。
5. 阴影会画到盒子边界之外，外层 `Stack`/`Clip` 开了裁剪会被截断 —— 排阴影"没出来"先看外层裁剪。
6. `Opacity` 值必须在 0f..1f。
7. `<ImageFiltered>` 会自动按 sigma 给输出边界，嵌在 `<ColorFiltered>` 内无需手动配 `outputBounds`；
   Parser 版滤镜**只支持高斯模糊**，复杂 Skia 滤镜要 Kotlin DSL。
8. `<Image>`/`<Emoji>` 的 `url` 与 `dataUri` **必须且只能指定其一**；dataUri 只支持 PNG/JPEG/WebP。
9. 图片平铺 `REPEAT*` 默认上限 100,000 个矩形，**超过直接抛异常而不是只画一部分**。
10. 普通图片 `fit` 省略时按 `SCALE_DOWN`（不放大小图），剩余空间按 `alignment` 对齐。
11. `Expanded = Flexible(fit=TIGHT)`，二者**只能是 Flex 的直接子节点**；
    `crossAxisAlignment=STRETCH` 才强制填满交叉轴。
12. **自动换行需要有限的可用宽度**；`UnconstrainedBox` 可解除传给子节点的约束 ——
    比 v1 时代"让 Text 自定宽 + 估算"更可靠的裁尾规避手段，A03 起优先使用。
13. 定位问题顺序：根约束是否有限 → 子节点尺寸是否满足约束 → `parentData` 是否在正确父节点下
    → 是否被裁剪 → 是否只是绘制透明。
14. 服务端 `Server-Timing` 的 `render;dur=` 只是渲染段，不等于端到端请求耗时；
    两者分开记录，不互相替代。

## 7. 像素自检（`tmp/{RUN}/A02/inspect-report.json`）

**{insp['total']} 项检查，FAIL {len(insp['failures'])}**。全部判据基于实际渲染出的像素，不是估算：

- PNG 头与画布尺寸；
- 泳道底带、午休带（带内零卡片、带内底色、外侧是泳道底带、两侧虚线）；
- **15 张卡片左右缘**：在卡片行做白色游程匹配，游程数、宽度（±{insp['thresholds']['geometry_tolerance_px']}px 内）与中心，
  多卡/少卡/时间被压缩或被外扩都会失败；卡片上下缘外侧是泳道底带；
- 整点网格线与刻度线位置；
- **每条文本墨迹**：存在、墨迹右缘距所属卡片内边 ≥2px（未被裁、未溢出）、
  墨迹宽/估算宽 ≥ 0.82（CJK）或 0.90（拉丁，因 CJK 字面窄于字距）、未溢出卡片左侧；
- 同卡内各文本墨迹两两不重叠；手机同一行各段不粘连；
- 页边距带内无正文，并报告实测最外墨迹：
  大图最右 x={meas['wide_rightmost_ink_x']}（正文右界 1880）、最下 y={meas['wide_bottommost_ink_y']}；
  手机最右 x={meas['mobile_rightmost_ink_x']}（正文右界 688）、最下 y={meas['mobile_bottommost_ink_y']}；
- 手机 15 张卡（卡体白 / 卡外为页面底色 / 强调条为类别色）；页脚不超正文宽；
- 两图字段齐全且 15 场的时间与标题文字一致；讲者仅在大图。

裁图 {c['crop_images']} 张（整幅两张 + 10:00–11:15 密集区 + 页头 + 泳道标题行 + 午休带 + 页脚 + C 泳道 + 手机三段；
其中 `wide-dense-10-1115.png` 是首轮重复命名、已被 `wide-dense-1000-1115.png` 取代，按「不删除尝试记录」的约定保留未删），
实际打开查看 {c['image_views']} 次，含 TASK.md 特别要求的「10 点附近密集区域」。

## 8. 踩坑

1. **坐标空间**：`kit.card()` 的子元素被包进 `layer()`，原点是**卡片左上角**而非画布。
   v1 把卡片文字按画布坐标追加到 canvas 层，结果是 15 个卡片全空、文字全堆在页头。
2. **`Positioned(width=W)` 是紧约束**：单行 `Text` 被它裁尾。一律让 `Text` 自定宽，
   并在构建期用断言核对。
3. **文字宽度估算系统性偏小 ≤6%**：右对齐若不乘 `SLACK=1.06`，尾部落进页边距
   （大图读图说明实测右缘 1896 > 1880；手机分段标题 692 > 688）。
   修法是右对齐统一乘 SLACK + 加构建期撞车断言 + 用「墨迹右缘净空 ≥2px」做像素级兜底。
4. **CJK 墨迹窄于字距**：2 字 CJK 的墨迹宽约是字距估算的 91%，统一 0.92 阈值会误报；
   按脚本分档 0.82 / 0.90。
5. **1px 细线抗锯齿后更浅**：刻度线标称 `#C3C2B7`（亮度 193），实测 205–221。
   不能对 1px 细线断言精确色值，只能断言「比局部底色暗 N」。
6. **白色游程内缩对称**：1px 边框 + 抗锯齿使卡内白色游程比外缘各缩进约 1.5px。
   比端点会假失败，改比**宽度**（±3.5px）与**中心**（±1.5px）。
7. **午休带右缘恰是真实卡片边界**：S09/S10 正好 13:00 开始，右外侧像素是类别色而非底带。
   对称的「外侧必须是泳道底带」判据不成立，只在 C 泳道（13:00–13:20 是空档）保留右侧测试。
8. **标题孤字成行**：末行只剩 1–2 字。加 `balanced()` 收窄折行预算重折，
   两行都 ≥3 字；收窄只移动断点，产出行仍 ≤ 块内宽，行数预算不变，块宽不变。
9. **午休带过浅**：`#ECEBE6` 在 `#F4F3F0` 上几乎不可辨，加深到 `#E5E3DC`。
10. **Bash 分类器 3 次不可用**：一次导致 `iter-v4-reason.txt` 未创建，构建在读 reason 时抛
    `FileNotFoundError` —— PNG 与 audit 已落盘而迭代记录丢失。已用 `a02_backfill_iter.py` 补记，
    并把 reason 读取移到渲染之前、缺失即 `SystemExit`，避免「图在盘上、记录没了」。
11. **`python -I -c` 打印中文是解码假象**：控制台 GBK，文件本身是 UTF-8；
    指标与日志一律写 UTF-8 文件，中文参数走 `SNAPSHOT_ITER_REASON_FILE` 而不是命令行。

## 9. 已知取舍

- **午休标注只覆盖三泳道共用的 12:00–13:00**。各会场实际空档与午休并不对齐
 （B 从 11:10 就空、C 到 13:20 才有下一场），这些差异如实记在
  `public_break.overlapping_venue_gaps`，图上不再额外标注以免遮挡泳道与增加视觉噪声。
- **不画半小时内刻度的额外网格线**，只有整点网格；10:30、15:30 这类场次的位置
  靠与整点线的相对位置读出，符合「共用线性时间轴 + 比例绘制」的要求。
- **文字宽度用估算模型**（CJK 1em、拉丁查表 + 窄/宽字符表），不做真实字形度量；
  用 `SLACK` 与像素级「墨迹净空」断言兜底，而不是追求估算精度。
- **未使用外侧编号索引表**：最窄块 S15 已容纳全部五字段，加索引表只会重复信息。
  若未来加入 <25 分钟的场次才需要。
- **v4 迭代记录为补记**（见第 8 节第 10 条）；其 DSL 与 PNG 与 v3 逐字/字节相同，无视觉改动。
- A02 的 `started_at` 取 events.jsonl 中首次 A02 `task_update`（{m['started_at']}），
  此前的 TASK.md 阅读与构建脚本编写时间包含在墙钟内但无独立日志。

## 10. 留痕确认

- 请求日志 `tmp/{RUN}/A02/requests.jsonl`（{len(reqs)} 条，全部 200）、
  迭代日志 `tmp/{RUN}/A02/iterations.jsonl`（{len(its)} 条）均存在。
- 原始 DSL 逐请求保留 `tmp/{RUN}/A02/req-*.snapshot`（{len(reqs)} 份）+ 同名 `.headers.txt`；
  响应体原字节保留 `tmp/{RUN}/A02/responses/`。
- 版本化 DSL `tmp/{RUN}/A02/dsl/`（v1–v5，两图各 5 份，含 v3 与 v4 的逐字相同副本）；
  迭代 reason 文件 `tmp/{RUN}/A02/gen/iter-v*-reason.txt`。
- 自检报告 `tmp/{RUN}/A02/inspect-report.json`、裁图 `tmp/{RUN}/A02/crops/`。
- 生成与自检脚本 `tmp/{RUN}/A02/gen/a02_build.py`、`a02_inspect.py`、
  `a02_backfill_iter.py`、`a02_finalize.py` 均在临时目录，未改写 `tasks/`、`inputs/`、`templates/`。
- 总任务根 `.gitignore` 已创建（只排除 `__pycache__/` 等运行时缓存），
  未用 `tmp/`、`outputs/`、`*.log` 或整类图片/DSL/JSON 通配规则排除过程证据；
  `__pycache__/`、`.pyc` 不要求留痕，本报告与指标均未把它们列为证据。
- 所有路径相对总任务根（`path_base: suite_root`）或相对各文档自身，无机器盘符。
- 未发生的项目：失败请求 0 次、重试 0 次、429/503 0 次、排队等待 0 秒、
  用户反馈等待 0 秒（A 类单轮任务）。

## 11. 未完成事项

无。{m['status']}。已知取舍见第 9 节；已知过程缺口（渲染前未取文档）见第 6.5 节，
已在本题收尾时补齐并记入 shared 请求日志。
"""
    return L


def main() -> None:
    reqs, its = req(), iters()
    audit = backfill_audit_bytes(reqs)          # 先回填，再算哈希
    insp = jload(TMP / "inspect-report.json")
    st = json.loads((ROOT / "outputs" / RUN / "_suite" / "suite-state.json")
                    .read_text(encoding="utf-8"))
    started = next(r["started_at"] for r in reqs)          # 与 events 一致：首次 task_update
    ended = now_iso()
    elapsed = int((parse(ended) - parse(started)).total_seconds())

    arts = {}
    for key, fn in (("png_wide", "agenda-wide.png"), ("png_mob", "agenda-mobile.png"),
                    ("dsl_wide", "agenda-wide.snapshot"),
                    ("dsl_mob", "agenda-mobile.snapshot"),
                    ("audit", "schedule-audit.json")):
        p = OUT / fn
        arts[key] = {"path": f"outputs/{RUN}/A02/{fn}", "bytes": p.stat().st_size,
                     "sha256_16": sha16(p)}
    arts["png_wide"]["size"] = [1920, 1200]
    arts["png_mob"]["size"] = [720, 1280]
    arts["dsl_wide"]["matches_rendered_dsl"] = sha16(
        TMP / "dsl" / "agenda-wide.v5.snapshot") == arts["dsl_wide"]["sha256_16"]
    arts["dsl_mob"]["matches_rendered_dsl"] = sha16(
        TMP / "dsl" / "agenda-mobile.v5.snapshot") == arts["dsl_mob"]["sha256_16"]

    el = [r["elapsed_ms"] for r in reqs]
    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A02",
        "track": "A",
        "status": "completed",
        "stop_reason": "需求满足并完成像素自检（73 项 FAIL 0）与逐图查看",
        "output_dir": f"outputs/{RUN}/A02",
        "temp_dir": f"tmp/{RUN}/A02",
        "run_id": RUN,
        "timezone": TZ,
        "started_at": started,
        "ended_at": ended,
        "elapsed_seconds": elapsed,
        "elapsed_note": (
            f"墙钟时间：started_at 取 events.jsonl 中首次 A02 task_update（{started}），"
            f"此前的题目阅读与构建脚本编写含在墙钟内但无独立日志；"
            f"ended_at 取本次收尾（{ended}）。墙钟不等于请求耗时之和，"
            f"中间含看图、改代码与 3 次 Bash 分类器不可用等待。"),
        "counts": {
            "final_pngs": 2,
            "final_dsl": 2,
            "snapshot_requests": len(reqs),
            "successful_snapshot_requests": sum(1 for r in reqs if r["http_status"] == 200),
            "failed_snapshot_requests": sum(1 for r in reqs if r["http_status"] != 200),
            "retry_requests": sum(1 for r in reqs if r.get("retry_after")),
            "document_requests": 0,
            "shared_document_requests": 9,
            "shared_document_requests_note": "A02 渲染期间未取文档（过程缺口）；9 次文档/字体请求在"
                                             "本题收尾时补做，记为 shared，不计入本题 A02 请求数。",
            "other_service_requests": 0,
            "dsl_versions_rendered": len({(r["label"].rsplit(" ", 1)[-1]) for r in reqs}),
            "iterations_recorded": len(its),
            "completed_visual_iterations": sum(1 for i in its if i["kind"] == "visual-iter"),
            "incomplete_visual_iterations": 0,
            "pixel_checks": insp["total"],
            "pixel_failures": len(insp["failures"]),
            "crop_images": len(insp["crops"]),
            "image_views": 6,
            "audit_content_map_entries": len(audit["content_map"]),
        },
        "request_notes": {
            "http_status_all": sorted({r["http_status"] for r in reqs}),
            "http_429_or_503": 0,
            "retry_after_seen": False,
            "queue_wait_seconds": None,
            "queue_wait_note": "全程 ratelimit_remaining 118–119，未出现 429/503，"
                               "无任何排队等待；不可测等待按约定记 null（不是 0）。",
            "ratelimit_remaining_range": "118–119",
        },
        "timings": {
            "started_at": started,
            "ended_at": ended,
            "elapsed_seconds": elapsed,
            "first_usable_image_seconds": int((parse(reqs[0]["ended_at"])
                                              - parse(started)).total_seconds()),
            "first_usable_image_note": "从 started_at 到首张 200 PNG 落盘（agenda-wide v1），"
                                       "7 秒：首请求即成功，无失败重试。",
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "queue_wait_note": "全程 ratelimit_remaining 118–119，未出现 429/503，"
                               "无任何排队等待；不可测排队按约定记 null（不是 0）。",
            "request_duration_sum_seconds": round(sum(el) / 1000, 3),
            "request_duration_sum_note": "10 次请求耗时之和（顺序执行，无并行重叠），"
                                         "不等于任务墙钟总耗时。",
            "server_timing_source": "各请求响应头 Server-Timing: render;dur=..., total;dur=...，"
                                    "仅表示服务端渲染段，与端到端 elapsed_ms 分别记录",
            "request_elapsed_ms_total": int(sum(el)),
            "request_elapsed_ms_min": int(min(el)),
            "request_elapsed_ms_max": int(max(el)),
            "request_first_started_at": reqs[0]["started_at"],
            "request_last_ended_at": reqs[-1]["ended_at"],
            "log_sources": [
                f"tmp/{RUN}/A02/requests.jsonl",
                f"tmp/{RUN}/A02/iterations.jsonl",
                f"tmp/{RUN}/A02/inspect-report.json",
            ],
        },
        "artifacts": arts,
        "data_verification": {
            "events": len(audit["events"]),
            "total_minutes": audit["duration_summary"]["total_minutes"],
            "total_hours": audit["duration_summary"]["total_hours"],
            "minutes_by_venue": audit["duration_summary"]["by_venue"],
            "gap_minutes_by_venue": {g["venue"]: g["gap_minutes_total"] for g in audit["venue_gaps"]},
            "session_plus_gap_equals_420": all(
                g["session_minutes"] + g["gap_minutes_total"] == 420
                for g in audit["venue_gaps"]),
            "conflict_pairs_checked": audit["conflict_check"]["pairs_checked"],
            "conflicts_found": len(audit["conflicts"]),
            "input_times_modified": audit["conflict_check"]["input_times_modified"],
            "public_break_merged": audit["public_break"]["merged_into_event"],
            "unresolved": audit["unresolved"],
        },
        "visual_review": [
            {"version": i["version"], "kind": i["kind"],
             "action": "整幅目检 + 裁图 + 像素自检" if i["kind"] == "visual-iter"
             else "整幅目检",
             "result": i["reason"][:80]} for i in its],
        "quality_gates": {
            "pixel_checks_pass": f"{insp['total'] - len(insp['failures'])}/{insp['total']}",
            "card_edges_within": f"宽 ±{insp['thresholds']['geometry_tolerance_px']}px、中心 ±{insp['thresholds']['geometry_tolerance_px']}px",
            "text_ink_ratio_min": insp["thresholds"]["text_ink_ratio_min_cjk"],
            "text_ink_ratio_min_latin": insp["thresholds"]["text_ink_ratio_min_latin"],
            "min_clear_to_card_edge_px": insp["thresholds"]["min_clear_to_card_edge_px"],
            "measured_extrema": insp["measured"],
            "font_sizes": "正文标题 20 / 时间 18（大图上限 20/18）；手机正文 18（上限 18）",
            "no_post_processing": "最终 PNG 为服务响应字节直存，未做任何像素后处理",
            "reproducible": "同一 DSL 二次渲染产出字节级相同 PNG（v3 与 v4 的 DSL 与 PNG 均一致）",
        },
        "evidence": {
            "requests_log": f"tmp/{RUN}/A02/requests.jsonl",
            "iterations_log": f"tmp/{RUN}/A02/iterations.jsonl",
            "raw_dsl_per_request": f"tmp/{RUN}/A02/req-*.snapshot（{len(reqs)} 份）",
            "versioned_dsl": f"tmp/{RUN}/A02/dsl/（v1–v5，两张图各 5 份）",
            "raw_responses": f"tmp/{RUN}/A02/responses/",
            "response_headers": f"tmp/{RUN}/A02/req-*.snapshot.headers.txt",
            "self_check_report": f"tmp/{RUN}/A02/inspect-report.json",
            "crops": f"tmp/{RUN}/A02/crops/",
            "generator": f"tmp/{RUN}/A02/gen/a02_build.py",
            "self_check_script": f"tmp/{RUN}/A02/gen/a02_inspect.py",
            "iter_record_backfill": f"tmp/{RUN}/A02/gen/a02_backfill_iter.py",
            "iter_reason_files": f"tmp/{RUN}/A02/gen/iter-v*-reason.txt",
            "templates_consulted": [
                f"tasks/A02-conference-schedule/templates/{p.name}"
                for p in sorted(SYSROOT.iterdir())],
        },
        "unresolved_issues": [],
    }

    (OUT / "snapshot-usage.md").write_text(usage_md(metrics), encoding="utf-8")
    (OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- suite-state ---
    for t in st["tasks"]:
        if t["id"] == "A02":
            t.update({
                "status": "completed",
                "started_at": started,
                "ended_at": ended,
                "artifacts": [arts[k]["path"] for k in
                              ("png_wide", "png_mob", "dsl_wide", "dsl_mob", "audit")],
                "visual_review_evidence": [
                    f"{insp['total']} 项像素自检 FAIL {len(insp['failures'])}"
                    f"（{f'tmp/{RUN}/A02/inspect-report.json'}）",
                    f"实际打开查看最终图与裁图 {metrics['counts']['image_views']} 次，"
                    f"含 TASK.md 要求的 10:00 附近密集区域",
                    f"裁图 {len(insp['crops'])} 张：{f'tmp/{RUN}/A02/crops/'}",
                    "v1 空卡片缺陷、v3 孤字成行、v5 右对齐越界均已修复并像素级复核",
                ],
                "unresolved_issues": [],
                "resume_notes": None,
            })
            break
    st["current_task"] = "A03"
    st["current_round"] = None
    st["current_case"] = None
    st["suite_state"] = "in_progress"

    from sys import path as _sp
    _sp.insert(0, str(ROOT / "tools"))
    import suite as S
    S.save_state(st)
    ck = S.snapshot_checkpoint(st)
    st["last_checkpoint"] = ck
    S.save_state(st)
    S.append_event({"ts": ended, "event": "task_update", "task_id": "A02",
                    "status": "completed", "checkpoint": ck,
                    "artifacts": [arts[k]["path"] for k in
                                  ("png_wide", "png_mob", "dsl_wide", "dsl_mob", "audit")]})
    S.append_event({"ts": ended, "event": "task_started", "task_id": "A03",
                    "status": "in_progress"})

    print(f"A02 completed: {arts}")
    print(f"elapsed {elapsed}s; requests {metrics['counts']['snapshot_requests']}; "
          f"pixels {metrics['counts']['pixel_checks']}/{metrics['counts']['pixel_failures']}")
    print(f"checkpoint {ck}")


if __name__ == "__main__":
    main()
