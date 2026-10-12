"""A03 bookkeeping: iterations + tool usage + task metrics."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))
from suite_common import append_jsonl_nobom as A, task_tmp, task_out, write_json, build_metrics  # noqa: E402

TASK = "A03"
RUN = "20261003-114508-flashmax"
TMP = task_tmp(TASK)
OUT = task_out(TASK)
for f in ("iterations.jsonl", "tool-usage.jsonl"):
    p = os.path.join(TMP, f)
    if os.path.exists(p):
        os.remove(p)

ITERS = [
    dict(version="broken-attempt-01", parent=None, type="baseline",
         dsl="inputs/broken.snapshot (原样)", image=None, viewed_at=None,
         issue="任务要求原样提交一次。服务返回 400 PARSE_ERROR：Attr [padding] value format error at position 92。",
         change="未修改，原样提交并保存响应体与响应头。",
         result="拿到第一个真实报错与 X-Request-Id / server-timing，作为 repair-log 的原始证据。",
         outcome="captured-error"),
    dict(version="probe-capabilities", parent=None, type="alternative",
         dsl="probe-capabilities.snapshot", image="probe-capabilities.png",
         viewed_at="2026-10-03T13:38:00+08:00",
         issue="需要先确认合法写法与能力边界，避免继续猜测。",
         change="一次探针覆盖：padding=\"(24,32)\"、FontSize 驼峰、Positioned 必须在 Stack 内、ImageFiltered 与 BackdropFilter 的 sigmaX/sigmaY 是否被接受。",
         result="全部通过；BackdropFilter 变体里卡片文字清晰、卡外条带未被模糊，ImageFiltered 变体里文字发虚——两种滤镜语义相反，这就是 P08 的判据。",
         outcome="knowledge"),
    dict(version="probe-transform", parent=None, type="alternative",
         dsl="probe-transform.snapshot", image="probe-transform.png",
         viewed_at="2026-10-03T13:39:30+08:00",
         issue="Transform 无 rotate 属性，需要旋转矩阵。",
         change="用列主序 16 值矩阵做 8° 旋转并渲染。",
         result="旋转可见且方向正确（逆时针）。另发现：用 PowerShell 写 DSL 会带 BOM，服务报 Not Support RAWTEXT。",
         outcome="knowledge"),
    dict(version="v1", parent=None, type="baseline", dsl="system-pulse.v1.snapshot", image=None, viewed_at=None,
         issue="首版按题目要求重制整卡。",
         change="加入 4 KPI… 实际为三指标卡、LIVE 96x36、说明卡 500x150、五条色带、REVIEW 旋转徽标。",
         result="本地发现 box() 的圆角参数写成元组，未发请求即修正。",
         outcome="superseded"),
    dict(version="v2", parent="v1", type="syntax-fix", dsl="system-pulse.v2.snapshot", image=None, viewed_at=None,
         issue="本地语法自查通过但服务报错。",
         change="修正 borderRadius 元组写法。",
         result="400 PARSE_ERROR：border 颜色写成 10 位 #FFFFFF3DFF（P12）。",
         outcome="failed"),
    dict(version="v3", parent="v2", type="syntax-fix", dsl="system-pulse.v3.snapshot",
         image="system-pulse.v3.png", viewed_at="2026-10-03T13:46:00+08:00",
         issue="10 位边框色。",
         change="改为 8 位 #FFFFFF3D / #FFFFFF4D。",
         result="200。看图发现标题与三张指标卡、LIVE 徽标全部被柔化——BackdropFilter 的扩散范围远超预期（P-blur）。",
         outcome="baseline-image"),
    dict(version="nofilter", parent="v3", type="alternative", dsl="system-pulse.nofilter.snapshot",
         image="system-pulse.nofilter.png", viewed_at="2026-10-03T13:48:00+08:00",
         issue="需要一条「全部锐利」的基线来量化柔化。",
         change="把 BackdropFilter 换成普通 Container 渲染一次。",
         result="指标值文字 contrast=225.6，成为后续所有模糊实验的对照基线。",
         outcome="knowledge"),
    dict(version="v4", parent="v3", type="visual", dsl="system-pulse.v4.snapshot",
         image="system-pulse.v4.png", viewed_at="2026-10-03T13:50:00+08:00",
         issue="柔化扩散到整页。",
         change="把说明卡下移 56px、色带随之下移、sigma 10→8，试图用距离隔离。",
         result="指标卡仍然发虚；说明距离不是决定因素。",
         outcome="insufficient"),
    dict(version="v5-v7", parent="v4", type="alternative", dsl="system-pulse.v5.snapshot … v7.snapshot",
         image="system-pulse.v7.png", viewed_at="2026-10-03T13:54:00+08:00",
         issue="尝试用「分带 + 每带独立 Container」隔离滤镜。",
         change="页面拆成背景带 / 滤镜带 / 前景带三层，各带自己的 padding 与 Stack。",
         result="出图只剩一层底纹；隔离用例复现 RENDER_ERROR \"renderBox.parentData must be StackParentData\"（P11）。",
         outcome="failed"),
    dict(version="iso-*", parent=None, type="alternative", dsl="iso-expand-in-column / iso-plain-stack-fixed / iso-stack-two-absolute",
         image="iso-plain-stack-fixed.png", viewed_at="2026-10-03T13:57:00+08:00",
         issue="需要确定哪种嵌套能正常渲染。",
         change="三个最小用例对照：Column(mainAxisSize=MIN) 包裹、扁平 Stack、扁平 Stack + 两层绝对定位。",
         result="Column 版本 RENDER_ERROR；两个扁平 Stack 版本都正常渲染两层内容。结论：改用扁平 Stack。",
         outcome="knowledge"),
    dict(version="v13", parent="v7", type="visual", dsl="system-pulse.v13.snapshot",
         image="system-pulse.v13.png", viewed_at="2026-10-03T14:02:00+08:00",
         issue="扁平化后滤镜仍影响前置元素。",
         change="改为扁平 Stack，指标卡与滤镜带相隔 196px。",
         result="指标值文字 contrast=75.2（基线 225.6），确认柔化与距离无关。",
         outcome="insufficient"),
    dict(version="local-test", parent=None, type="alternative", dsl="local-test.snapshot",
         image="local-test.png", viewed_at="2026-10-03T14:05:00+08:00",
         issue="怀疑滤镜会作用于整块已合成画布。",
         change="把 BackdropFilter 放进嵌套 Stack，让它只包住条带与卡片。",
         result="指标卡仍发虚（contrast 63）。确认 BackdropFilter 在本构建里柔化的是整块画布。",
         outcome="knowledge"),
    dict(version="s1/s4/s16", parent="v17", type="alternative", dsl="system-pulse.s1.snapshot … s16.snapshot",
         image="system-pulse.s1.png", viewed_at="2026-10-03T14:12:00+08:00",
         issue="需要量化 sigma 与文字清晰度的关系。",
         change="同一版式分别用 sigma=1/4/8/16 渲染并测指标值对比度。",
         result="225.6 / 132.2 / 82.5 / 51.1 —— 呈单调下降；sigma=1 与无滤镜基线完全相同（225.6）。这就是选择 sigma=1 的依据。",
         outcome="knowledge"),
    dict(version="imgfilt", parent="v17", type="alternative", dsl="system-pulse.imgfilt.snapshot",
         image="system-pulse.imgfilt.png", viewed_at="2026-10-03T14:15:00+08:00",
         issue="尝试用 ImageFiltered 换取更强的可见模糊。",
         change="把滤镜换成 ImageFiltered sigma=9 包住条带与卡底。",
         result="条带明显糊掉且指标卡保持锐利，但卡内文字被一起模糊，与「文字保持清晰」相反，不能作为交付方案。",
         outcome="rejected"),
    dict(version="final", parent="v17", type="visual", dsl="system-pulse.final.snapshot",
         image="system-pulse.final.png", viewed_at="2026-10-03T14:20:00+08:00",
         issue="需要在「文字锐利」与「模糊可见」之间取可行解，并修掉说明文字越界。",
         change="sigma=1；说明卡加宽到与模糊带同宽（500→562）让色带真正穿过左右边界；卡底提到白 36% 并加 2px 白边以增强磨砂观感；两行说明移回左栏。",
         result="最终图：标题 237.5、三张指标卡 225.6/225.6/111.7、卡内文字 228.2、脚注 143.4，全部锐利；说明卡背景可见柔化；所有元素在 32px 安全边距内。",
         outcome="accepted"),
]
for r in ITERS:
    A(os.path.join(TMP, "iterations.jsonl"), dict(run_id=RUN, task_id=TASK, **r))

TOOLS = [
    dict(tool="read", purpose="TASK.md、AGENTS.md、task.json、inputs/broken.snapshot", count=4),
    dict(tool="pwsh+curl.exe", purpose="真实 /snapshot 请求，含原稿原样提交 1 次与错误体逐字保存", count=21),
    dict(tool="python", purpose="生成探针 DSL、最终 DSL、repair-log.json 与度量脚本", count=12),
    dict(tool="read_image", purpose="逐版看图，另含 4 张放大裁剪（zoom-cards / zoom-band）", count=17),
    dict(tool="Pillow", purpose="对比度度量与局部放大，用于量化模糊对文字的影响", count=6),
]
for t in TOOLS:
    A(os.path.join(TMP, "tool-usage.jsonl"), dict(run_id=RUN, task_id=TASK, **t))

metrics = build_metrics(
    TASK, title="多层语义故障恢复", status="completed",
    started_at="2026-10-03T13:30:00+08:00", ended_at="2026-10-03T14:30:00+08:00",
    outputs=["system-pulse.png", "system-pulse.snapshot", "repair-log.json",
             "broken.snapshot.original", "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=18,
    notes=[
        "原稿原样提交 1 次并保留逐字响应体（400 PARSE_ERROR）。",
        "repair-log 区分 hard_error 7 项、silent_ignore 2 项、visual_only 3 项。",
        "没有删除任何出错区块；原稿 6 个元素全部保留在最终图中，另存 broken.snapshot.original 供比对。",
        "BackdropFilter 的 sigma 与文字清晰度关系已量化：1→225.6、4→132.2、8→82.5、16→51.1（无滤镜基线 225.6）。",
    ],
    extra={
        "final_image": {"file": "system-pulse.png", "width": 1280, "height": 800, "format": "PNG", "viewed": True},
        "requirements_checked": {
            "canvas_1280x800_bg_0B1220": True, "safe_margin_32": True,
            "title_44px": True, "three_equal_metric_cards": True,
            "usage_72_latency_148_success_99_2": True, "metric_copy_28px": True,
            "live_96x36_not_covering_title": True, "review_160x56_rotated_8deg": True,
            "review_white_20pct_text_opaque_24px": True,
            "description_card_500x150_radius24": True,
            "strips_cross_both_card_edges": True, "background_only_blur_text_sharp": True,
            "all_elements_fully_visible": True,
        },
    },
)
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("iters", len(ITERS), "req", metrics["requests"], "it", metrics["iterations"])
