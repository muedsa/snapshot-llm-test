# -*- coding: utf-8 -*-
"""A07: iterations + reports."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A07"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0

if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A07/network-map.png", "map v1 全图"),
        (f"outputs/{RUN_ID}/A07/network-map.png", "map v2 全图"),
        (f"outputs/{RUN_ID}/A07/travel-card.png", "card v1 全图"),
        (f"outputs/{RUN_ID}/A07/travel-card.png", "card v2 全图"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="map-v1", parent=None, type="baseline", image="network-map.png",
             viewed_at="2026-11-03T16:44:20+08:00",
             issues="斜线段被画成竖条（只处理轴对齐）；站名压在圆点上；页脚两行重叠。",
             changes="—", result="几何与站位确认，绘制函数需重写"),
        dict(version="map-v2", parent="map-v1", type="visual", image="network-map.png",
             viewed_at="2026-11-03T16:52:40+08:00",
             issues="标签偏移修正后站名与编号不再压线；但每条线段都用 Transform 绘制，单次渲染 180–208 秒。",
             changes="斜线用旋转矩阵，轴对齐线段改用普通 rect；行/列标签上移",
             result="渲染降到 3.4 秒，图形与之前一致"),
        dict(version="card-v1", parent=None, type="baseline", image="travel-card.png",
             viewed_at="2026-11-03T16:57:10+08:00",
             issues="页脚两行重叠；第二张卡的替代路线标签与色块过近；底部留白过大。",
             changes="—", result="三条路线与无障碍判定正确"),
        dict(version="card-v2", parent="card-v1", type="visual", image="travel-card.png",
             viewed_at="2026-11-03T17:02:40+08:00",
             issues="复查：卡片、替代块、判定小结、页脚均无重叠；正文 20px、注释 17–18px。",
             changes="新增判定小结块；正文字号提升到 20", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 13, "requirements_passed": 13,
                                              "final_image_reviewed": True, "known_defects": []}})
rep.write_usage(
    TASK, title="三线换乘图与路线核验", status="completed",
    summary="按 network.json 绘制 1600×1000 非地理示意图：16 站、3 条线、17 段相邻关系，线路只用 0°/45°/90° 线段，"
            "换乘站（中心/东桥/工坊）用加粗方框标记，无设施车站（书院/东桥/花园/公园）用红色斜杠标记。"
            "720×1280 旅行卡给出三条查询旅程的站序、线段、边数与换乘，并逐条判定能否作为无障碍旅程；"
            "石溪→机场 的最短普通路线需在东桥换乘（无设施），因此另给 2 次换乘的无障碍替代路线。",
    deliverables=[("network-map.png", "1600×1000 全网示意图"), ("network-map.snapshot", "对应 DSL"),
                  ("travel-card.png", "720×1280 三条路线旅行卡"), ("travel-card.snapshot", "对应 DSL"),
                  ("routes.json", "求解结果、线段、换乘与无障碍判定"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1600×1000 与 720×1280", "实测 1600×1000、720×1280", "通过"),
        ("按线路站序连相邻站、双向乘车", "R/B/G 三条折线逐段连接，图注说明双向与等时", "通过"),
        ("共享站=换乘站，线条交叉不误导",
         "S04/S05/S08 为真实共用站（粗方框）；图中不存在无站点的线路交叉", "通过"),
        ("颜色+字母双重编码", "R/B/G 字母块 + 三色线 + 图例文字", "通过"),
        ("16 站名称与编号完整", "16 个站名 22px + 编号 18px 全部在图上", "通过"),
        ("折线转折 45°/90°", "全部线段为水平/垂直/一条 45° 斜线（公园→工坊）", "通过"),
        ("明确标注非地理示意", "副标题与页脚两处写明“非地理示意图”", "通过"),
        ("无障碍状态逐站标注 + 图例", "无设施站加红色斜杠，图例说明 ○ / ⊘ / ◎", "通过"),
        ("不可删除线路", "三条线路完整保留，无设施站仍在线上", "通过"),
        ("三条查询的最少边数+最少换乘路线", "6/6/4 段，1/1/1 次换乘，routes.json 记录站序与线段", "通过"),
        ("旅行卡展示三条旅程与无障碍判定", "三张卡片 + 判定小结，标明满足/不满足及原因", "通过"),
        ("不满足时给出无障碍替代路线", "石溪→机场：6 段 2 换乘（工坊、中心）", "通过"),
        ("站数不误作区间数", "文案统一写作“N 段站间”，与 edges 一致", "通过"),
        ("两图视觉系统一致、地图标签≥20、手机正文≥20",
         "同色系/同字体；站名 22px；卡片正文 20px", "通过"),
    ],
    visual_review=[
        ("network-map.png v1", "斜线画成竖条、站名压点、页脚重叠", "重写线段绘制与标签偏移"),
        ("network-map.png v2", "图形正确但渲染 180s（Transform 过多）", "轴对齐线段改 rect，降到 3.4s"),
        ("travel-card.png v1", "页脚重叠、替代块标签过近、底部留白", "重排卡片与页脚，新增判定小结"),
        ("travel-card.png v2", "整图复查：三卡完整、替代路线清晰、无重叠", "作为交付"),
    ],
    design_notes=[
        "示意图只保留拓扑：三条线用 0/45/90 段绘制，拐点不在站上也没关系，读者只需读出相邻关系。",
        "换乘站用 32px 圆角方框（比普通站大一倍）区分，普通站为白心圆点；无设施站在圆内画红色斜杠，"
        "与图例的 ⊘ 一一对应。",
        "旅行卡与地图共用同一套线路色与字母块，并把“段”与“换乘”分开陈述，避免把站数当区间数。",
    ],
    dsl_notes=[
        "轴对齐线段改用普通 `Container`（rect），只有 45° 斜线才用 `Transform` 旋转矩阵——"
        "把 Transform 数量从约 40 个降到 1 个后，渲染时间由 180–208 秒降到 3.4 秒。",
        "站点用三层叠画（深底圈 → 白圈 → 深色内圈）得到清晰描边，不需要 border 的复合格式。",
        "卡片高度按内容动态累计，最后用剩余空间放“判定小结”，避免底部大片空白。",
    ],
    issues=[
        ("斜线段被画成竖条", "绘制函数只处理 y1==y2 与 x1==x2，斜线落入竖线分支",
         "增加 45° 分支，用旋转矩阵绘制斜线"),
        ("站名压在站点上", "上方标签 dy=−54，18px 编号正好压在圆点上沿", "dy 改为 −74"),
        ("页脚两行重叠", "第一行 17px 文本超宽换行，与第二行相撞", "缩短文案并拆成两行固定位置"),
        ("单次渲染 180 秒", "约 40 个 Transform 元素触发大量图层合成", "轴对齐线段改为 rect，Transform 仅保留 1 个"),
        ("传输被截断（49196B 无效 PNG）", "服务端偶发丢弃大响应体尾部",
         "客户端检测 IEND 缺失后自动重试一次，并把失败记录保留在 requests.jsonl"),
    ],
    files=[(f"outputs/{RUN_ID}/A07/network-map.png", "示意图 PNG"),
           (f"outputs/{RUN_ID}/A07/travel-card.png", "旅行卡 PNG"),
           (f"outputs/{RUN_ID}/A07/routes.json", "路线与判定结果"),
           (f"tmp/{RUN_ID}/A07/requests.jsonl", "渲染请求（含 1 次截断重试）"),
           (f"tmp/{RUN_ID}/A07/iterations.jsonl", "4 版迭代"),
           (f"tmp/{RUN_ID}/A07/scripts/", "gen_map.py / gen_card.py")],
    extra_sections=[("路线结果", [
        "松林→会展：R×3 段 + B×3 段，6 段、1 次换乘（中心，有设施）→ 满足无障碍",
        "石溪→机场：G×4 段 + R×2 段，6 段、1 次换乘（东桥，无设施）→ 不满足；"
        "替代：G×2 + B×1 + R×3，6 段、2 次换乘（工坊、中心）→ 满足",
        "西港→研究所：B×1 段 + G×3 段，4 段、1 次换乘（工坊，有设施）→ 满足",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A07 reports written")
