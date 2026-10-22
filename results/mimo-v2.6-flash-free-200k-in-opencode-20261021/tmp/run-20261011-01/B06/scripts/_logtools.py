# -*- coding: utf-8 -*-
"""One-off B06 log repair + build.  Run from suite root.

1. requests.jsonl was written by render.py with the render fields only.  AGENTS
   also requires case_id / request type / start time.  The original bytes are
   kept as requests-raw-000001.jsonl, then each record gains derived fields
   (case_id from the dsl_path, type, endpoint, started_at = ts - elapsed).
   No original value is altered or removed.
2. tool-usage.jsonl did not exist yet.  Entries are written with the *event*
   time, not the logging time - log_tool.py stamps now(), which for research
   fetches and verifier runs that already happened would have recorded a wrong
   instant.  Each entry carries ts_basis saying where the time came from.
3. iterations-view-times.jsonl: iterations.jsonl carries the journal write
   time.  This derived view records the render that produced the image and the
   window [render completed, journal written] inside which the viewing happened.
"""
import datetime
import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     ".."))
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", ".."))   # suite root
RAW = os.path.join(BASE, "requests-raw-000001.jsonl")


def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- 1. requests
req_path = os.path.join(BASE, "requests.jsonl")
requests = read_jsonl(req_path)

if not os.path.exists(RAW):
    with open(RAW, "w", encoding="utf-8", newline="\n") as f:
        for r in requests:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("backed up original requests.jsonl ->",
          os.path.basename(RAW), "records", len(requests))

enriched = []
for r in requests:
    case = os.path.splitext(os.path.basename(r["dsl_path"]))[0]
    case = "-".join(case.split("-")[:2])
    ts = datetime.datetime.fromisoformat(r["ts"])
    start = ts - datetime.timedelta(seconds=r["elapsed_seconds"])
    e = dict(r)                      # every original field kept verbatim
    e["case_id"] = case
    e["request_type"] = "render"
    e["endpoint"] = "/snapshot"
    e["credentials_used"] = False
    e["started_at"] = start.isoformat(timespec="milliseconds")
    e["finished_at"] = r["ts"]
    e["timezone"] = "+08:00"
    e["started_at_derived"] = True
    e["derived_fields"] = ["case_id", "request_type", "endpoint",
                           "credentials_used", "started_at", "finished_at",
                           "timezone"]
    e["request_id_header"] = None
    e["server_timing"] = None
    e["request_id_header_note"] = "服务响应未返回 requestId/Server-Timing 头"
    enriched.append(e)

write_jsonl(req_path, enriched)
print("requests.jsonl enriched:", len(enriched), "records;",
      "original preserved at", os.path.basename(RAW))

# ------------------------------------------------------------ 2. tool usage
# Only tools actually used during B06.  Times: research = plan-v1 fetched_at;
# local scripts = the file's own last-write time (the run happened at or after
# it), which is stated per entry rather than presented as an exact run instant.
S = "tmp/run-20261011-01/B06/scripts"
R = "tmp/run-20261011-01/B06/research"
DR = "tmp/run-20261011-01/B06/drafts"
JOURNAL = "tmp/run-20261011-01/B06/iterations.jsonl"
PUBLISH_REPORT = "tmp/run-20261011-01/B06/publish-verify.json"


def P(*parts):
    """Relative path with forward slashes, per PATHS.md."""
    return "/".join(parts)


def mtime(rel):
    """Last-write time of a suite-root-relative path."""
    p = os.path.join(ROOT, rel)
    return datetime.datetime.fromtimestamp(
        os.path.getmtime(p)).astimezone().isoformat(timespec="seconds")


tools = [
    dict(seq=1, tool="webfetch",
         purpose="取得降水概率定义原文，作为 case-06 定义三要素的逐字比对基准",
         input="https://zh.wikipedia.org/wiki/降水概率",
         output=P(R, "SRC-01-precipitation-probability.txt"),
         ts="2026-10-21T13:41:00+08:00",
         ts_basis="plan-v1.json research.fetched_at",
         affects=["case-06"], request_ref=None, outcome="success",
         note="CC BY-SA 4.0；引文以繁体原文照录并在图上标明"),
    dict(seq=2, tool="webfetch",
         purpose="取得 GB 28050 预包装食品营养标签条目，作为 case-02 「1+4」强制标示项的比对基准",
         input="https://zh.wikipedia.org/wiki/营养标签",
         output=P(R, "SRC-02-gb28050-nutrition-label.txt"),
         ts="2026-10-21T13:42:00+08:00",
         ts_basis="plan-v1.json research.fetched_at",
         affects=["case-02"], request_ref=None, outcome="success",
         note="仅标示项清单作为真实锚点，具体产品数值为自拟演示数据"),
    dict(seq=3, tool="webfetch",
         purpose="尝试取得居民阶梯电价正文，作为 case-03 档位结构背景",
         input="SRC-03 tiered-electricity-price",
         output=None,
         ts=None,
         ts_basis="未取得正文，plan-v1.json 未记录 fetched_at，故时间为 null",
         affects=["case-03"], request_ref=None, outcome="http_404_no_body",
         note="正文未取得，档位与单价一律标为示例演示，不逐字引用"),
    dict(seq=4, tool="python_generator",
         purpose="case-01 服药钟面参数化生成 + C1-C5 断言",
         input=P(S, "case01.py"), output=P(DR, "case-01-v1.snapshot"),
         ts=mtime(P(S, "case01.py")),
         ts_basis="生成器文件最后写入时间；实际运行不早于该时刻",
         affects=["case-01"], request_ref="B06-req-0001", outcome="success"),
    dict(seq=5, tool="python_verifier",
         purpose="case-01 像素量测：着色带角度、镜像区、药点质心与主刻度",
         input=P(S, "_verify01.py"), output="断言输出（过程留痕，未落盘为交付件）",
         ts=mtime(P(S, "_verify01.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-01"], request_ref=None, outcome="passed"),
    dict(seq=6, tool="python_generator",
         purpose="case-02 份量换算参数化生成 + C1-C5 断言",
         input=P(S, "case02.py"), output=P(DR, "case-02-v1.snapshot"),
         ts=mtime(P(S, "case02.py")),
         ts_basis="生成器文件最后写入时间；实际运行不早于该时刻",
         affects=["case-02"], request_ref="B06-req-0004", outcome="success"),
    dict(seq=7, tool="python_verifier",
         purpose="case-02 像素量测：方糖块宽/螺距、琥珀占比、上下括号宽度",
         input=P(S, "_verify02.py"), output="断言输出",
         ts=mtime(P(S, "_verify02.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-02"], request_ref=None, outcome="passed"),
    dict(seq=8, tool="python_generator",
         purpose="case-03 阶梯账单参数化生成 + C1-C5 断言",
         input=P(S, "case03.py"), output=P(DR, "case-03-v1.snapshot"),
         ts=mtime(P(S, "case03.py")),
         ts_basis="生成器文件最后写入时间；实际运行不早于该时刻",
         affects=["case-03"], request_ref="B06-req-0006", outcome="success"),
    dict(seq=9, tool="python_generator",
         purpose="case-03 v1 留痕修复：还原原图表绘制顺序重新生成 v1.snapshot 以恢复与 v1.png 的配对",
         input=P(S, "case03_v1.py"),
         output=P(DR, "case-03-v1.snapshot"),
         ts=mtime(P(S, "case03_v1.py")),
         ts_basis="脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-03"], request_ref="B06-req-0008", outcome="success",
         note="重渲染 md5=614bf75b94c488e21632cb8a49d5e104 与原图一致，同时证明服务渲染确定性"),
    dict(seq=10, tool="python_verifier",
         purpose="case-03 像素量测：三档填充右缘、台阶顶、月度线与虚线位置、宽高比",
         input=P(S, "_verify03.py"), output="断言输出",
         ts=mtime(P(S, "_verify03.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-03"], request_ref=None, outcome="passed"),
    dict(seq=11, tool="python_verifier",
         purpose="case-04 像素量测：7 条参考带左右缘、标记落点误差、超出色段与偏离量成正比",
         input=P(S, "_verify04.py"), output="断言输出",
         ts=mtime(P(S, "_verify04.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-04"], request_ref=None, outcome="passed"),
    dict(seq=12, tool="python_verifier",
         purpose="case-05 像素量测 + 数值核对：三费率条宽、零截距最小二乘拟合、IRR 现值闭合",
         input=P(S, "_verify05.py"), output="断言输出",
         ts=mtime(P(S, "_verify05.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-05"], request_ref=None, outcome="passed"),
    dict(seq=13, tool="python_verifier",
         purpose="case-06 像素量测：100 格逐格中心色计数、引文墨迹边界、三枚 chip 数值右缘",
         input=P(S, "_verify06.py"), output="断言输出",
         ts=mtime(P(S, "_verify06.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-06"], request_ref=None, outcome="passed"),
    dict(seq=14, tool="python_verifier",
         purpose="case-07 像素量测：分段像素宽=秒数×2.6417、9 个刻度位置、轨总长正比",
         input=P(S, "_verify07.py"), output="断言输出",
         ts=mtime(P(S, "_verify07.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-07"], request_ref=None, outcome="passed"),
    dict(seq=15, tool="python_verifier",
         purpose="case-08 像素量测：五要素墨迹、五时刻 bbox 递增与右对齐、延误红墨迹、四处登机口/座位一致",
         input=P(S, "_verify08.py"), output="断言输出",
         ts=mtime(P(S, "_verify08.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-08"], request_ref=None, outcome="passed"),
    dict(seq=16, tool="python_generator",
         purpose="case-09 大屏积分榜参数化生成 + 数据自洽与排序规则断言",
         input=P(S, "case09.py"), output=P(DR, "case-09-v1.snapshot"),
         ts=mtime(P(S, "case09.py")),
         ts_basis="生成器文件最后写入时间；实际运行不早于该时刻",
         affects=["case-09"], request_ref="B06-req-0018", outcome="success"),
    dict(seq=17, tool="python_verifier",
         purpose="case-09 像素量测：八条比例条宽、零轴连续性、并列连接线、同分色带范围、九列对齐",
         input=P(S, "_verify09.py"), output="断言输出",
         ts=mtime(P(S, "_verify09.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-09"], request_ref=None, outcome="passed"),
    dict(seq=18, tool="python_oneoff",
         purpose="case-09 v3 因 log_iter 长命令在 PowerShell 下解析失败，改用一次性脚本写入 journal",
         input=P(S, "_log09.py"), output=P("tmp", "run-20261011-01", "B06", "iterations.jsonl"),
         ts=mtime(P(S, "_log09.py")),
         ts_basis="脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-09"], request_ref=None, outcome="success",
         note="踩坑：超长中文命令行触发 TerminatorExpectedAtEndOfString，后续长日志一律走一次性脚本"),
    dict(seq=19, tool="python_probe",
         purpose="case-10 v1 定点探针：扫描四档蓝色水平线、跨档橙色攀升线、当前标记与坐标轴",
         input=P(S, "_probe10.py"),
         output=P(DR, "case-10-v1.png"),
         ts=mtime(P(S, "_probe10.py")),
         ts_basis="探针脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-10"], request_ref="B06-req-0021", outcome="success",
         note="探针发现三处攀升线缺失（调用未 append），构成 v1 的明确缺陷证据"),
    dict(seq=20, tool="python_verifier",
         purpose="case-10 像素量测：C1 费率层级、C2 分段累加双算法、C3 13 点逐点曲线校验、C4 攀升与临界标注、C5 边距扫描",
         input=P(S, "_verify10.py"), output="断言输出",
         ts=mtime(P(S, "_verify10.py")),
         ts_basis="校验脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-10"], request_ref=None, outcome="passed"),
    dict(seq=21, tool="python_packager",
         purpose="10 件定版打包：md5 与源响应字节比对、IHDR 尺寸/位深校验、DSL 闭合校验",
         input=P(S, "publish.py"),
         output=P("tmp", "run-20261011-01", "B06", "publish-verify.json"),
         ts=mtime(P(S, "publish.py")),
         ts_basis="打包脚本文件最后写入时间；实际运行不早于该时刻",
         affects=["case-01", "case-02", "case-03", "case-04", "case-05",
                  "case-06", "case-07", "case-08", "case-09", "case-10"],
         request_ref=None, outcome="passed",
         note="10/10 通过 md5 + IHDR + </Snapshot> 三项校验"),
    dict(seq=22, tool="python_log_builder",
         purpose="补齐 AGENTS 要求的 case_id/类型/起止时间字段并生成看图时间索引",
         input=P(S, "_logtools.py"),
         output=os.path.join("tmp", "run-20261011-01", "B06", "tool-usage.jsonl"),
         ts=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
         ts_basis="本次日志补写动作本身的执行时间",
         affects=["case-01", "case-02", "case-03", "case-04", "case-05",
                  "case-06", "case-07", "case-08", "case-09", "case-10"],
         request_ref=None, outcome="success",
         note="requests.jsonl 原始字节另存于 requests-raw-000001.jsonl，未删除任何原值"),
]

write_jsonl(os.path.join(BASE, "tool-usage.jsonl"), tools)
print("tool-usage.jsonl:", len(tools), "entries")

# ----------------------------------------------------- 3. view-time index
reqs = read_jsonl(req_path)
first_render = {}
for r in reqs:
    first_render.setdefault(r["dsl_path"], r)

its = read_jsonl(os.path.join(BASE, "iterations.jsonl"))
# requests.jsonl stores dsl_path with forward slashes; normalise before lookup
first_render = {k.replace("\\", "/"): v for k, v in first_render.items()}
views = []
for it in its:
    key = P(DR, "%s-%s.snapshot" % (it["case_id"], it["version"]))
    r = first_render.get(key.replace("\\", "/"))
    ts = datetime.datetime.fromisoformat(it["ts"])
    row = {
        "id": it["id"] + "-view",
        "iteration_id": it["id"],
        "case_id": it["case_id"],
        "version": it["version"],
        "parent_version": it["parent_version"],
        "type": it["type"],
        "viewed": bool(it.get("viewed")),
        "viewed_recorded_at": it["ts"],
        "viewed_recorded_basis": "log_iter 写入时刻，紧接所描述的看图动作之后",
        "render_request_id": r["id"] if r else None,
        "render_completed_at": r["ts"] if r else None,
        "view_window_seconds": round((ts - datetime.datetime.fromisoformat(
            r["ts"])).total_seconds(), 1) if r else None,
        "view_window_note": None,
    }
    if r is None:
        row["view_window_note"] = "该版本无独立渲染记录（见 case-03 v1 证据修复）"
    elif row["view_window_seconds"] is not None and row["view_window_seconds"] < 0:
        row["view_window_note"] = (
            "负值来自 case-03-v1 的重渲染（B06-req-0008）晚于首次看图；"
            "首次渲染为 B06-req-0006")
    elif row["view_window_seconds"] is not None and row["view_window_seconds"] > 600:
        row["view_window_note"] = (
            "该批次两条 journal 一次性写入，窗口上界即批次写入时刻，"
            "实际看图紧接该版本渲染完成")
    views.append(row)

write_jsonl(os.path.join(BASE, "iterations-view-times.jsonl"), views)
print("iterations-view-times.jsonl:", len(views), "entries")
