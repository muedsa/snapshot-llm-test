"""补齐 A08 的迭代留痕：前 4 条请求记录只带了统一的占位 note，
这里追加一条 reconciliation 记录，为 v1/v2/v3/交付版分别写明类型、父版本、
可观察问题、改动、复查结果，并记录像素核验工具的三轮判据重写（未改 DSL）。

append-only：不修改已存在的记录行。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import suite as S  # noqa: E402

TASK = "A08"

S.log_iteration(TASK, {
    "task_id": TASK,
    "iteration": "reconcile-1",
    "kind": "records_reconciled",
    "reconciles": ["v1", "v2", "v3", "req-a08-wayfinding-v3-1"],
    "reason": "前 4 条 iterations.jsonl 只带了统一的占位 note（a08_render.py 的 save_iter 写死了同一句话），"
              "缺少类型、父版本、可观察问题与复查结果；此处追加补记，不改写已存在的行",
    "timeline": [
        {
            "version": "v1", "parent": None, "type": "baseline",
            "request_id": "req-a08-wayfinding-v1",
            "image": "tmp/r20261014T1536+0800-5f11da/A08/preview/v1-wayfinding.png",
            "views": "整图 + 4 张局部（conv-exit、labels、r2card、shared-entry）",
            "observed": "R2 橙色虚线形状不规则，不是规整短横；白色方向箭头偏窄",
            "dsl_stats": "72 个橙色填充块，其中 69 个为退化形（含零长重复顶点）；白色三角箭头 1 个",
            "change": "无（基线）",
        },
        {
            "version": "v2", "parent": "v1", "type": "visual",
            "request_id": "req-a08-wayfinding-v2",
            "image": "tmp/r20261014T1536+0800-5f11da/A08/preview/v2-wayfinding.png",
            "views": "整图 + 10 张局部（route1、route2、row2-C、scale、shared1、shared2、"
                     "arrow-corner、arrow-corner-20-2、arrow-row12-r1、arrow-row2-1）",
            "observed": "路线结构、文字与卡片已正确；但 47 段虚线被渲染成尖端朝外的三角形",
            "cause": "虚线路径里混入了零长重叠段：M134 652 L134 652 L134 652 L158 644 L158 660 "
                     "L134 652 … 实际只剩 3 个不同顶点，是三角形而非 24x16 矩形",
            "change": "把 R2 描边拆成「带宽多边形」与「逐段虚线矩形」两组独立几何；"
                      "a08_geom.dash_polys() 按弧长区间切段",
            "verify": "未修好：46 个橙色退化形仍在",
        },
        {
            "version": "v3", "parent": "v2", "type": "visual",
            "request_id": "req-a08-wayfinding-v3",
            "image": "tmp/r20261014T1536+0800-5f11da/A08/preview/v3-wayfinding.png",
            "views": "整图 + 5 张局部（diverge、converge、row2-dashes、shared1-row13、"
                     "shared1-col3-badge）",
            "observed": "虚线为规整的 24x16 短横，转角处不断口；箭头落在虚线段内，方向清晰",
            "change": "band() 与 segment_band() 跳过零长重叠段，避免法向量塌成 (0,0)；"
                      "虚线周期设为 40 px = 1 格，使接缝落在格心；"
                      "ARROW_F 由 0.5 改为 0.24，使箭头占弧位 5.1-18.6 完全落在 24 px 虚线内"
                      "（f=0.5 时占 15.25-29.5，跨越虚线/间隙分界线，白箭头会渗进白间隙而消失）",
            "verify": "47/47 段虚线为 4 顶点 24x16 矩形，退化形 0 个；"
                      "geom-check.json 25/25；像素核验 288/288 符合预期、不符 0 处；"
                      "32/32 个未覆盖箭头方向正确",
        },
        {
            "version": "v3（交付版）", "parent": "v3", "type": "deliver",
            "request_id": "req-a08-wayfinding-v3-1",
            "image": "outputs/r20261014T1536+0800-5f11da/A08/wayfinding.png",
            "views": "整图",
            "observed": "与 v3 预览完全一致",
            "change": "无 DSL 改动；同一 DSL 的第 4 次请求（request_id 自动去重）",
            "verify": "cmp 验证交付 PNG 与 v3 预览、原始响应体三者逐字节一致（325 926 字节）",
        },
    ],
    "verifier_rework": {
        "note": "以下三次判据重写没有改动 DSL 或重新渲染，属校验器修正，不计入视觉迭代",
        "rounds": [
            {
                "from": "点探针（尖内/尖外、期望颜色按段号与「共享」标签推定）",
                "to": "多边形包含关系 + 固定弧位",
                "why": "① Python round() 是银行家舍入，round(647.5)=648，探针落到相邻行；"
                       "② 6x13.5 px 箭头在尖端附近形内深度 < 0.5 px，单点判据必然误判；"
                       "③ 格心正好是虚线与间隙的分界线（周期 40 = 格宽），在那里取样测的是"
                       "栅格化的边处理；④ 转角 miter 合法覆盖「几何上属于另一路线」的点，"
                       "按标签推定会假失败",
            },
            {
                "from": "正向三角 vs 反向三角的面积相关性（收缩后比较）",
                "to": "白色权重剖面（底边 2px 权重 vs 尖端 2px 权重）",
                "why": "两个互为镜像的三角向各自内心收缩时大面积重叠：6x13.5 箭头内切半径仅 "
                       "2.407，EDGE_IN=0.6 收缩到 0.75 倍后轴向约 78% 重叠，正好复现 rev≈0.82，"
                       "判据不具区分力",
                "result": "重写后 32/32 通过；底边权重最低 8.9、尖端权重最高 2.1，差 ≥ 6.8",
            },
        ],
        "tools": ["tmp/_probe2.py", "tmp/_probe3.py", "tmp/_probe4.py",
                  "tmp/_dsl_diff.py",
                  "tmp/r20261014T1536+0800-5f11da/A08/gen/a08_pixels.py"],
        "decisive_evidence": "tmp/_probe3.py 的 1 px ASCII 色图证明 v3 渲染本来就是对的，"
                            "首轮「R1 箭头 0/17」是测试工具错、不是渲染缺陷",
    },
})
print("已追加 reconcile-1 迭代记录")
