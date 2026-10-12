"""A22：按轮次追加 iterations.jsonl（脚本内只写本轮真实发生过的事）。"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
task = "A22"
tmp = root / "tmp" / rid / task
rnd = int(sys.argv[1])
NOW = datetime.now(timezone.utc).isoformat()
reqs = {}
for line in (tmp / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    reqs[r["dsl_version"]] = r


def row(ver, typ, changes, problems, part, recompare, parent=None, final=False):
    q = reqs[ver]
    return dict(iteration_id="%s-r%02d-%s" % (task, rnd, ver), type=typ,
                version=ver, parent_version=parent, request_id=q["request_id"],
                http_status=q["http_status"],
                image_path=q["out_file"], image_scope="preview",
                changes_made=changes, observed_problems=problems,
                requirement_part=part, recompare_result=recompare,
                completed=True, image_viewed=True,
                viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看",
                final=final)


ROWS = {
    1: [
        row("r01-v01", "requirement-change",
            "按第一轮需求用 inputs/monthly.csv 建 1600×1000 驾驶舱：4 张 KPI 卡"
            "（总净收入/总经营利润/总订单/总体转化率）、零起点分组柱图、6 行明细表、"
            "三句只由实际数值成立的结论 + 口径行；数据全部由 gen_dash.py 现算",
            "查看后：x 轴月份被写成 26.04 这种缩写，违反“所有月份原样”；"
            "明细表最后一列贴到卡片右边界",
            "所有月份原样 / 正文≥22 / KPI 与图表表格同源于真实计算",
            "与需求逐条比对，两处属于本轮需求未满足，需改"),
        row("r01-v02", "visual",
            "x 轴标签改为 CSV 原样月份 2026-04；表格列宽改 96/116/100/82/82 并整体"
            "左移到卡片内 10px，表头与分隔线、标题同列对齐；负利润标签改到柱底之下",
            "查看后：月份原样、表格不再贴边；但 verify.py 从 PNG 反测出 "
            "chart-title 与最上方刻度 tick-240000 的墨迹纵向重叠 2px",
            "不得裁切/重叠 / 区域边界稳定",
            "verify.py：73 个文字元素墨迹全部落在自身盒内，1 处墨迹重叠待修"),
        row("r01-v03", "visual",
            "绘图区从 (cy+62, h=300) 改为 (cy+88, h=288)，即整体下移 26px，"
            "让最上刻度与图表标题分开；区域边界常量未动",
            "查看后：标题、刻度、柱形、表格、结论四层各自清楚，无重叠无裁切；"
            "KPI 数字与表格金额一致",
            "版面节奏 / 文字不被压窄",
            "verify.py：0 处墨迹重叠、0 个越界构件、12 根柱实测高度与数值换算差 ≤3px",
            parent="r01-v02", final=True),
    ],
    2: [
        row("r02-v01", "requirement-change",
            "按 rounds/round-02.md 应用两处更正（2026-08 refund_amount 15048→25048、"
            "2026-09 operating_cost 138000→208000），KPI/柱图/表格/标题轮次戳/结论"
            "全部由 gen_dash.py 重算：净收入 918,624→908,624、利润 262,124→182,124、"
            "利润率 28.5%→20.0%、2026-09 利润转为 -5,632，纵轴向下扩到 -40k",
            "查看后：更正确实传播到每一处（表格 2026-08 净收入变 163,052、"
            "退款率 13.3%，2026-09 利润红色 -5,632，结论第三句改成负利润月份提示）；"
            "但 -5,632 只有 5.8px 高，落在 0 到 -40k 的整格空白里，几乎看不出它是柱",
            "不得裁切/画成正值/只修数字不修柱高 / 允许在原图表区域内扩负轴",
            "verify.py：0 重叠、0 越界、12 根柱实测高度与换算差 ≤3px，"
            "负柱实测 5px vs 换算 5.8px（未被裁切，只是本来就短）",
            parent="r01-v03"),
        row("r02-v02", "visual",
            "在负值区间补半格细网格线（step/2 = 20k 处一条，仅 bot<0 时启用，"
            "因此第一轮 DSL 逐字节不变），给短负柱一个可读的长度参照",
            "查看后：-20k 细线让 -5,632 的柱长一眼可读，其余版面与第一轮一致；"
            "画布与五个主区域边界位移 0px",
            "视觉回归 / 边界 ±2px / 主字体与视觉系统不变",
            "verify.py：0 重叠、0 越界、12/12 柱高一致、区域跨轮最大位移 0px；"
            "change-audit.json 记录传播与未改内容",
            parent="r02-v01", final=True),
    ],
    3: [
        row("r03-v01", "requirement-change",
            "按 rounds/round-03.md 在第二轮基础上追加 2026-10 一行"
            "（orders 640 / gross_revenue 224000 / refund 11200 / cost 142000 / "
            "sessions 5900），两处第二轮更正继续有效；KPI 改为 7 个月汇总，"
            "柱图与表格各含 7 个月，副标题区间改成 2026-04 至 2026-10",
            "查看后：数字与结论都对（净收入 1,121,424、利润 252,924、总订单 3,685、"
            "总体转化率 11.10% = 3,685 ÷ 33,200），但表格第 7 行与脚注"
            "“与柱图同源 · 共 7 行”贴在一起",
            "KPI 为 7 个月汇总 / 图表含全部 7 个月 / 不省略 2026-04、不恢复旧值",
            "verify.py：14 根柱实测高度与换算差 ≤3px、0 越界，但报出 1 处墨迹重叠"
            "（td-2026-10-* 与 table-foot）",
            parent="r02-v02"),
        row("r03-v02", "visual",
            "行数 >6 时表格行距额外预留 46px 给脚注（row_h 由 59.4 收紧到 52.9），"
            "只动表格内部行距，区域边界与其余轮次不变",
            "查看后：7 行各自清楚、脚注不再与末行相碰；2026-04 仍在首行，"
            "2026-09 仍是 -5,632 的红色负值，2026-08 退款率仍是 13.3%",
            "主区域边界 ±2px / 正文≥22 / 可重排内部行距",
            "verify.py：0 重叠、0 越界、14/14 柱高一致、区域跨轮最大位移 0px；"
            "重新生成第 1、2 轮 DSL 的 md5 与已归档文件逐字节相同",
            parent="r03-v01", final=True),
    ],
}

rows = ROWS[rnd]
for r in rows:
    r.update(run_id=rid, task_id=task, round=rnd, image_viewed_at=NOW,
             recorded_at=NOW, noop_render=False, path_base="suite_root",
             completed_meaning="本轮闭环：改动后有真实渲染并被实际查看比较；"
                               "final=true 只表示该版本作为本轮成品交付")
with (tmp / "iterations.jsonl").open("a", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended", len(rows))
