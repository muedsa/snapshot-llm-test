"""A21 round-03 迭代记录追加（it-a21-008）。

iterations.jsonl 的既有 7 条记录是**单行 JSON**（一行一条），本脚本保持这一约定：
追加的记录也写成单行，且前面的行一律按原字节回写，不改写第一、二轮的既有记录。

本脚本可重复执行：已存在 it-a21-008 时只规范化其自身的行格式（若上次误写成
多行缩进 JSON，会把该条重新压回单行），内容不变。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
ROOT = HERE.parents[4]
A21TMP = ROOT / "tmp" / RUN_ID / "A21"
A21OUT = ROOT / "outputs" / RUN_ID / "A21"
R3 = A21OUT / "round-03"
JSONL = A21TMP / "iterations.jsonl"
MY_ID = "it-a21-008"


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_reqs():
    return [json.loads(l) for l in (A21TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]


def note_for(r: dict) -> str:
    """按请求类型给出对应的说明；render 与 render-aux 不是同一件事。"""
    if r.get("kind") == "render-aux":
        return (
            "去文字辅助渲染（同一构造器关掉 <Text> 输出），只为对比度审计量取文字"
            "下方的实际合成背景；不产出交付件、不进交付清单，返回字节 sha256 %s"
            % (r["aux_sha256"] or r["response_sha256"])[:8])
    return (
        "本轮交付渲染，一次成功；交付字节 sha256 %s"
        % r["response_sha256"][:8])


def build_record(reqs: list, r3ev: list) -> dict:
    renders = [r for r in reqs if r.get("kind") == "render"]
    auxes = [r for r in reqs if r.get("kind") == "render-aux"]
    span_end = max(dt.datetime.fromisoformat(e["viewed_at"]) for e in r3ev)
    span_start = min(dt.datetime.fromisoformat(r["started_at"]) for r in reqs)
    return {
        "iteration_id": MY_ID,
        "parent": "it-a21-007",
        "type": "baseline",
        "round": 3,
        "phase": "delivery",
        "spec_source": "tasks/A21-staged-launch-change/rounds/round-03.md",
        "requests": [
            {
                "request_id": r["request_id"],
                "attempt": r["attempt"],
                "kind": r.get("kind"),
                "artifact": r["artifact"],
                "started_at": r["started_at"],
                "elapsed_ms": r["elapsed_ms"],
                "http_status": r["http_status"],
                "server_timing": r.get("server_timing"),
                "note": note_for(r),
            } for r in sorted(reqs, key=lambda x: x["started_at"])
        ],
        "started_at": span_start.isoformat(timespec="seconds"),
        "started_at_note": "本轮 4 条请求全部返回了响应，started_at 即真实起点，"
                           "无需还原",
        "ended_at": max(e["viewed_at"] for e in r3ev),
        "ended_at_precision": "minute-level（取 viewing-evidence.json 中最晚的 "
                              "viewed_at；该时刻本身只记录到分钟）",
        "elapsed_note": (
            "墙钟 %.0f 秒（%s → %s，只覆盖在案活动；归档与记账尾段另记于 "
            "round-03/task-metrics.json 的 timings.archive_tail_seconds）。"
            "含浅色主题重排设计、无网络干跑门、2 条去文字辅助渲染、2 条交付渲染、"
            "15 次看图、逐段对比度量测；4 条服务请求合计仅 %.3f 秒"
            % ((span_end - span_start).total_seconds(), span_start.isoformat(
                timespec="seconds"), max(e["viewed_at"] for e in r3ev),
               sum(r["elapsed_ms"] for r in reqs) / 1000)),
        "image": {
            "path_base": "suite_root",
            "path": "outputs/%s/A21/round-03/launch-portrait.png" % RUN_ID,
            "size": [1080, 1350],
            "png_bytes": (R3 / "launch-portrait.png").stat().st_size,
            "png_sha256": sha(R3 / "launch-portrait.png"),
            "dsl": "outputs/%s/A21/round-03/launch-portrait.snapshot" % RUN_ID,
        },
        "image_wide": {
            "path_base": "suite_root",
            "path": "outputs/%s/A21/round-03/launch-wide.png" % RUN_ID,
            "size": [1440, 810],
            "png_bytes": (R3 / "launch-wide.png").stat().st_size,
            "png_sha256": sha(R3 / "launch-wide.png"),
            "dsl": "outputs/%s/A21/round-03/launch-wide.snapshot" % RUN_ID,
        },
        "auxiliary_renders": [
            {
                "request_id": r["request_id"],
                "png": r["aux_path"],
                "png_sha256": r["aux_sha256"],
                "note": "仅存临时目录，不进入交付清单，也不是作品",
            } for r in sorted(auxes, key=lambda x: x["started_at"])
        ],
        "viewed_at": r3ev[0]["viewed_at"],
        "viewed_at_precision": "minute-level；15 次打开事件的逐条时刻见 "
                               "viewing-evidence.json 的 round 3 块",
        "changes": [
            "主题：页面底 #060A18→#F5F8FC，牌子底 #0E1936→#FFFFFF；ink "
            "#F5F9FF→#0B1B33，muted #8FA3C2→#4A5A72，primary #5FE0FF→#0A6FA8，"
            "accent #FFC26B→#C2410C，primary_2 #1E86C8 不变——深底主题的近白与亮青"
            "在浅底上只有 1.06/1.55，必须整体换档而非个别调整",
            "叠层：取消主标题的青色 textShadow；发光球移到标题与信息栈之间的右列"
            "空区，外辉光半径 3.4r→2.7r（竖版）/2.75r（横版）；氛围 wash 由渐暗改为"
            "页面底到纯白的径向渐白（只会提亮底面，对深色文字只增不减对比度）",
            "文案：9 条全部保留并逐字符比对通过，无删减；新增英语短句 "
            "「Clarity through structure」于讲者与网址牌之间，竖版 28px、横版 26px",
            "版式：信息栈由 5 行扩为 6 行，赞助方与报名状态牌仍在网址牌之下，"
            "上下扩展空间仍 ≥70px；两尺寸、标题行数（3/2）与字号（66/52）不变",
            "取证：新增去文字辅助渲染 + 逐段对比度量测，产出 round-03/"
            "contrast-audit.json；辅助渲染与交付图除墨迹外逐通道最大差 12，"
            "证明只差在 <Text>",
            "生成脚本：a21_layouts.py 追加 default_cfg_r3 与 BUILDERS_R3（球位、"
            "辉光半径、色板、新增 clarity_en）；a21_audit.py 按轮次取色板并新增"
            "对比度块；新增 a21_contrast.py 与 a21_r3_aux.py",
        ],
        "pre_render_gate": "提交前先跑无网络干跑（a21_dryrun_r3.py）：构造 DSL → "
                           "断言合法 → 打印元素表 → 校验每行标题 advance 不超文本盒宽"
                           "（防折行）→ 校验文字墨迹与发光球实体净距 → 校验上下扩展"
                           "空间与最小字号 → 校验标题行数 ≤3 → 校验 9 条必需文案完整"
                           "（含本轮新增的 clarity_en）→ 校验交付 .snapshot 中 <Text> "
                           "无 transform/matrix → 校验品牌几何 6 项参数与第二轮一致。"
                           "9 项全部通过后才提交请求",
        "verified": "content-map.json 的 9 项检查全 passed，all_passed=true；"
                    "contrast-audit.json 覆盖两图 23 段普通文字（竖版 12、横版 11），"
                    "n_not_checked=0，最小对比度 4.8616（未舍入 4.861573385783012，"
                    "阈值 4.5），最差段为竖版 date #C2410C 对页面底 #F5F8FC；"
                    "两图各附 6 处带实际坐标的样本；交付字节 sha256 %s / %s"
                    % (sha(R3 / "launch-portrait.png")[:12],
                       sha(R3 / "launch-wide.png")[:12]),
        "viewing_outcome": "两图实际打开 15 次（整图 1:1 两次 + 放大裁切 11 次 + "
                           "2 次去文字辅助背景整图）；首版即通过，12 个预览视图中"
                           "没有发现需要返工的缺陷，故不追加视觉迭代记录，也不为凑"
                           "迭代而重渲",
        "remaining": "changes.json 第一版写成 Python 相邻字符串拼接、不是合法 JSON，"
                     "已留底修正；看图时刻只到分钟级；halo_scale 配置与实参曾不一致"
                     "（已修，交付字节未变）。详见 round-03/task-metrics.json 的 "
                     "unresolved_issues（a21-r3-u1..u4）",
        "status": "completed",
    }


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    reqs = [r for r in load_reqs() if r.get("round") == 3]
    if len(reqs) != 4:
        raise SystemExit("round-03 请求数应为 4，实际 %d" % len(reqs))
    view = json.loads((A21TMP / "viewing-evidence.json").read_text(
        encoding="utf-8"))
    r3ev = view["rounds"]["3"]["image_open_events"]

    raw = JSONL.read_text(encoding="utf-8") if JSONL.exists() else ""
    lines = raw.splitlines()

    # 既有可解析的单行记录按**原始行文本**保留，避免重新序列化带来的字节差异
    kept, malformed_at = [], None
    for i, l in enumerate(lines):
        if not l.strip():
            continue
        try:
            obj = json.loads(l)
        except json.JSONDecodeError:
            if malformed_at is None:
                malformed_at = i
            break
        if obj.get("iteration_id") == MY_ID:
            # 单行形式的本条记录已存在：内容以在案记录为准，不重写
            body = kept + [l]
            JSONL.write_text("\n".join(body) + "\n", encoding="utf-8")
            print("it-a21-008 已存在且是单行 JSON，未改动")
            return 0
        kept.append(l)
    if malformed_at is not None:
        # 尾部是被上一次误写成多行缩进 JSON 的本条记录。它是我几分钟前写下的、
        # 且 render 请求被错标为去文字辅助渲染，故重新按真实请求类型生成，
        # 只影响这一条；前面的行按原字节保留。
        tail = "\n".join(lines[malformed_at:]).strip()
        try:
            json.loads(tail)
        except json.JSONDecodeError:
            raise SystemExit(
                "iterations.jsonl 第 %d 行之后是既非单行、也非完整 JSON 的内容，"
                "无法安全处理；请人工检查" % (malformed_at + 1))
        verb = "重写（修正 render 请求被错标为辅助渲染的问题，并压回单行）"
    else:
        verb = "追加"

    rec = build_record(reqs, r3ev)
    body = kept + [json.dumps(rec, ensure_ascii=False)]
    JSONL.write_text("\n".join(body) + "\n", encoding="utf-8")

    # 回读校验：每一行都必须能被单独解析
    bad = 0
    for l in JSONL.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        try:
            json.loads(l)
        except json.JSONDecodeError:
            bad += 1
    if bad:
        raise SystemExit("回写后仍有 %d 行不是合法单行 JSON" % bad)

    print("%s it-a21-008（round 3, baseline, parent it-a21-007）" % verb)
    print("  记录 %d 条 | 请求 %d（render %d / render-aux %d）"
          % (len(body), len(reqs),
             len([r for r in reqs if r["kind"] == "render"]),
             len([r for r in reqs if r["kind"] == "render-aux"])))
    print("  看图 %d 次 | 起止 %s → %s"
          % (len(r3ev), rec["started_at"], rec["ended_at"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
