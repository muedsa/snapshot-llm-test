# -*- coding: utf-8 -*-
"""A16 wrap-up: log iterations, build task-metrics.json, update suite state."""
import json, os, sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

TASK = "A16"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8")
        if l.strip()]
renders = [r for r in reqs if r["request_type"] == "render"]
docs = [r for r in reqs if r["request_type"] == "document"]
started = reqs[0]["started_at"]
ended = reqs[-1]["ended_at"]
first_image = next(r["ended_at"] for r in renders
                   if (r.get("content_type") or "").startswith("image/"))

D = os.path.join(TMP, "drafts")
P = os.path.join(TMP, "preview")
draft = lambda n: os.path.join(D, "v%02d.snapshot" % n)
prev = lambda n: os.path.join(P, "a16-v%02d.png" % n)
final_png = os.path.join(OUT, "corrected-report.png")
final_dsl = os.path.join(OUT, "corrected-report.snapshot")
def rend_end(tag):
    """ISO time when the render whose DSL/response file carries `tag` finished."""
    for r in renders:
        if tag in os.path.basename(r.get("request_file") or "") or \
           tag in os.path.basename(r.get("response_file") or ""):
            return r["ended_at"]
    return None


iterations = [
    ("A16-v01", None, "baseline", draft(1), None, None,
     "首次 POST /snapshot 返回 400 PARSE_ERROR：Tag Container only can have one child "
     "(position 1160)。卡片 Container 直接放了多个 Positioned 子节点。",
     "记录失败响应，未产出图片；保留 responses/resp-A16-req-006-*.txt。", False),
    ("A16-v02", "A16-v01", "syntax-fix", draft(2), prev(2), rend_end("v02"),
     "改成 Panel=背景 Container + 全画布 Stack 后渲染成功，但用 read 打开图片发现："
     "三个卡片的内容整体被平移并裁切（图表标题出现在 y≈355 而非 182，图例被右边界切掉）。",
     "定位为嵌套 Stack 相对父容器原点重新定位子节点坐标；准备把 Stack 改为 (0,0) 全画布。", False),
    ("A16-v03", "A16-v02", "visual", draft(3), prev(3), rend_end("v03"),
     "把面板内容的 Stack 放到 (0,0) 全画布后布局正确。看图发现两个问题："
     "① 利润率行显示 0.2%/0.2%/0.2%/0.3%/0.3%（比值未乘 100）；"
     "② 轴单位“万元”与顶端刻度“200”上下挤在一起。",
     "利润率格式加 ×100；把“单位：万元”并入面板标题、去掉挤在轴旁的单位文本。", True),
    ("A16-v04", "A16-v03", "visual", draft(4), prev(4), rend_end("v04"),
     "利润率已正确显示 25.0/20.0/25.0/30.0/25.4%，单位不再重叠；看图发现面板标题下的 18px "
     "副标题“共同零起点…”与正文规格（≥22）有歧义。",
     "删除该 18px 副标题，把“共用零起点/同一比例尺”的说明移到页脚 18px 注记。", True),
    ("A16-v05", "A16-v04", "visual", draft(5), prev(5), rend_end("v05"),
     "版式干净、无重叠；放大 crops 检查后确认利润表末行墨迹距卡片下边界仅 3px，偏紧。",
     "利润表整体上移 4px（表头 676→672、下划线 706→702、数据行 716→712）。", True),
    ("A16-v06", "A16-v05", "visual", final_dsl, final_png, rend_end("corrected-report"),
     "最终图已用 read 打开查看，并用 verify_final.py 做像素级复验：16 项检查全部 PASS；"
     "整图与页首/图例/利润卡/提示卡/页脚 5 处放大图均已查看，无重叠、无截断。",
     "无进一步改动；corrected-report.png 为服务真实响应原始字节，"
     "corrected-report.snapshot 与之逐字节一致（17766 bytes）。", True),
]

artifacts = [
    {"file": rel(final_png), "role": "指定最终图 1280×900（服务真实响应，未后处理）"},
    {"file": rel(final_dsl), "role": "与最终 PNG 完全一致的完整 DSL"},
    {"file": rel(os.path.join(OUT, "findings.json")),
     "role": "10 条问题（含图片位置/现象/源数据核对/影响/修正/最终查看结果）+ 5 条不确定项"},
    {"file": rel(os.path.join(OUT, "corrected-data.json")),
     "role": "计算口径、轴定义（0–200 万元，1.42 px/万元）与 8 根柱的像素几何"},
    {"file": rel(os.path.join(OUT, "snapshot-usage.md")), "role": "自检与踩坑报告"},
    {"file": rel(os.path.join(OUT, "task-metrics.json")), "role": "请求/迭代/耗时指标"},
]

visual_evidence = [
    "read 打开 inputs/flawed-report.png 整图 + 2 处放大（zoom-profit-card.png、zoom-legend.png）",
    "read 打开 preview/a16-v02.png（发现卡片内容平移与图例裁切）",
    "read 打开 preview/a16-v03.png（发现利润率 0.2% 与单位/刻度拥挤）",
    "read 打开 preview/a16-v04.png（发现 18px 副标题的规格歧义）",
    "read 打开 preview/a16-v05.png（发现利润表末行偏紧）+ 3 处 crops 放大",
    "read 打开 outputs/20261004-182918/A16/corrected-report.png 整图",
    "read 打开最终图 3 处放大：crops/corrected-report-header.png / -legend.png / -footer.png",
    "verify_final.py 对最终 PNG 做像素级复验（verify-final.json，16/16 PASS）",
]

# idempotency guard: this script was accidentally executed twice, which appended a
# second identical copy of every iteration row. Keep only the first occurrence of
# each iteration_id so iterations.jsonl reflects the real history.
it_path = os.path.join(TMP, "iterations.jsonl")
if os.path.exists(it_path):
    rows = [json.loads(l) for l in open(it_path, encoding="utf-8") if l.strip()]
    seen, keep = set(), []
    for row in rows:
        iid = row.get("iteration_id")
        if iid in seen:
            continue
        seen.add(iid)
        keep.append(row)
    if len(keep) != len(rows):
        with open(it_path, "w", encoding="utf-8", newline="\n") as fh:
            for row in keep:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print("deduped iterations.jsonl: %d -> %d rows" % (len(rows), len(keep)))

UNRESOLVED = [
    "栅格化限制：1 px = 0.70 万元，柱顶亚像素测量与 DSL 计算位置最大偏差 0.56 px，"
    "像素级复验的数值分辨率即 ±0.4 万元，已在 findings.json 中写明。",
    "原稿柱底蓝 563 / 橙 564 的 1px 差、柱宽 64px 与 12px 组内间距无法判定是取整还是设计，"
    "已作为不确定项 U03 记录而非错误。",
    "平台未提供 token / 图像输入量 / 费用指标，task-metrics.json 相关字段一律 null。",
]
NOTES = ("A16 完成：先按像素测量诊断 flawed-report.png（轴截断、图例互换、柱高失真、Q3 利润算错、"
         "标题/副标题/提示卡指向错误季度），再用 source.csv 现算重制 1280×900 可信报告，"
         "并用 verify_final.py 做像素级复验（16/16 PASS）。")

if "--metrics-only" in sys.argv:
    # iterations were already logged by a previous run; only rebuild the metrics
    # and refresh the suite state without appending the rows a second time.
    import finalize, state as St
    m = finalize.build(TASK, started, first_image, ended)
    St.finish_task(TASK, "completed", artifacts=artifacts,
                   visual_evidence=visual_evidence, unresolved=UNRESOLVED,
                   notes=NOTES)
else:
    m = wrapup.wrapup(TASK, started, first_image, ended, iterations, artifacts,
                      visual_evidence, unresolved=UNRESOLVED, notes=NOTES)
print(json.dumps(m["counts"], ensure_ascii=False, indent=1))
print("wall_clock_seconds_total:", m["wall_clock_seconds_total"])
print("sum_of_request_durations_seconds:", m["sum_of_request_durations_seconds"])
print("failures:", m["failures"])
print("documents fetched:", [(d["url"], d["http_status"]) for d in docs])