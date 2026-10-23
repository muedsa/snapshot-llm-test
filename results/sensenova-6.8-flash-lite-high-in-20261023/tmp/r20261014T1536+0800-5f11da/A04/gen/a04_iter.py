"""A04 迭代留痕：从 requests.jsonl 生成 iterations.jsonl。

request_id 在 5 次字体探针里是同一个（req-a04-probe-font），
所以按 requests.jsonl 的行序编号，不靠 request_id 去重。

查看时刻只记录真实下界 viewed_not_before（该请求的响应结束时间），
不编造精确查看时刻。

启动基准：总任务根（cwd）。用法：python a04_iter.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a04_io as IO  # noqa: E402

OUT, TMP = IO.dirs()
REQ = TMP / "requests.jsonl"

# (version, parent, type, 关联请求行号, reason, 是否看图, 自检报告, 备注)
# 关联请求行号按 requests.jsonl 行序（0 起）；None 表示本次迭代不发请求（只改脚本或改图后重跑自检）。
PLAN = [
    ("probe-font/1", None, "syntax-fix", 0,
     "首版探针：验证中文与符号字形。根标签误写成 <Container>，未包住 <Snapshot>。",
     False, None,
     "HTTP 400 PARSE_ERROR First tag must be 'Snapshot' at position 0。"),
    ("probe-font/2", "probe-font/1", "syntax-fix", 1,
     "补回 <Snapshot background= type=\"png\"> 根标签后仍 400：属性之间缺空格，"
     "fontFamily 与 textAlign 粘在一起。",
     False, None,
     "HTTP 400 PARSE_ERROR Unexpected character 't' in state [AFTER_ATTR_VALUE_QUOTED] "
     "at position 1494。结论：所有属性必须空格分隔。"),
    ("probe-font/3", "probe-font/2", "syntax-fix", 2,
     "空格补齐后 400：Container alignment 不接受 RIGHT。",
     False, None,
     "HTTP 400 PARSE_ERROR Attr [alignment] value format error at position 2115。"
     "结论：alignment 只收 Alignment 枚举名（CENTER / CENTER_RIGHT / BOTTOM_RIGHT …）。"),
    ("probe-font/4", "probe-font/3", "syntax-fix", 3,
     "alignment 改 CENTER_RIGHT 后 400：fontFeatures 写成 \"+tnum 2\"。",
     False, None,
     "HTTP 400 PARSE_ERROR Attr [fontFeatures] value is invalid: "
     "Can't parse FontFeature: 2 at position 3105。"
     "结论：feature tag 必须写成带等号的形式，不能用空格分隔。"),
    ("probe-font/5", "probe-font/4", "probe", 4,
     "四项语法全修后成功：确认 Noto Sans CJK SC 能渲染中文与 ①②③ Σ ÷ → − ↑ ↓ 「」＝ ≥ × ·，"
     "Noto Sans SC 未安装（不可用）。",
     True, None,
     "HTTP 200 image/png 128303 B。该探针的 response body 与草稿被后续 4 次同名请求覆盖，"
     "仅最后一次存活；4 次失败正文以 requests.jsonl 的 error_summary 完整保留。"),
    ("v1", "probe-font/5", "visual", 5,
     "首版完整信息图：标题区 + 数据小表 + 三张图 + 结论/限制两框。",
     True, "tmp/r20261014T1536+0800-5f11da/A04/inspect-v1.json",
     "看图发现结论区五行的墨迹贴住两框下缘与圆角弧：框内正文越出内框。"),
    ("v2", "v1", "visual", 6,
     "结论区垂直布局修正：行距改为 28px、起点上移，CON_H 留足 CJK 字形高度。",
     True, "tmp/r20261014T1536+0800-5f11da/A04/inspect-v2.json",
     "结论两框通过。构成注仍在图②面板下缘附近，余量不足。"),
    ("v3", "v2", "visual", 7,
     "构成注上移 6px（708 → 702）：面板②内框下缘在 735，18 号字墨迹比行盒低约 24px，"
     "放在 708 只剩 ~2px 余量。",
     True, "tmp/r20261014T1536+0800-5f11da/A04/inspect-v3.json",
     "13/13 项自检通过。"),
    ("v3", "v3", "verify", None,
     "自检器重写第 12 项：改用几何排除描边（border_zone）替代颜色阈值。",
     False, "tmp/r20261014T1536+0800-5f11da/A04/inspect-v3.json",
     "旧实现按亮度阈值排除装饰，青色 2px 边框 #0F766E 的最高通道 118 ≤ 0xC0 被当成正文，"
     "其圆角抗锯齿晕把墨迹外接框撑满整个面板，误报「上/下侧余量 0px」；"
     "红色边框 #DC2626 最高通道 220 不跨阈值，因此只漏报青色框。改为按圆角矩形几何排除后消除。"),
    ("v3", "v3", "verify", None,
     "自检器修正第 12 项的行带证据：原行带 [ly-3, 下一行行盒顶) 相邻交叠 3 行，"
     "注释却声称不交叠，属不成立的证据。",
     False, "tmp/r20261014T1536+0800-5f11da/A04/inspect-final-v2.json",
     "像素检查器无法把一条墨迹归属到某一行，故删除逐行外接框，"
     "改量每行墨迹像素数并断言行间存在密度低谷（第 13 项）。实测低谷 min_count=0（整行为白），"
     "结论框峰值 328、限制框 155。最终 14/14 通过。"),
    ("final-1", "v3", "final", 8,
     "同一 DSL 重提交写入输出目录，得到正式产物 conversion-story.png / .snapshot。",
     True, "tmp/r20261014T1536+0800-5f11da/A04/inspect-final-v2.json",
     "313099 B 与 v3 预览逐字节一致；实际打开最终图复核完成，14/14 项自检通过。"
     "该版产物随后被 final-2 替换（见下一轮）。"),
    ("v4", "v3", "requirement-change", 9,
     "交付前逐条回读题面，发现「正文≥22」未满足：恒等分解那行是结论区正文，"
     "却写成 20 号。改为 22 号，并把结论区五行整体上移 4px（CON_Y+58 → +54），"
     "给更大的字形留出框底余量。同时给自检器新增第 14 项：从最终 .snapshot 读出全部 "
     "fontSize 断言 ≥18，并用琥珀色那行的墨迹宽度反推字号，防止构造器再把它写回 20 号。",
     True, "tmp/r20261014T1536+0800-5f11da/A04/inspect-v4.json",
     "22 号时墨迹宽 798px（20 号实测 719px），墨迹高 23px；DSL 中字号集合 {18,19,20,22,38}，"
     "最小 18。15/15 项自检通过。"),
    ("final-2", "v4", "final", 10,
     "同一 DSL 重提交写入输出目录，用 v4 的产物替换 final-1。",
     True, "tmp/r20261014T1536+0800-5f11da/A04/inspect-final-v3.json",
     "314286 B 与 v4 预览逐字节一致（final-1 的 313099 B 版本被覆盖，"
     "其请求与响应记录仍在 requests.jsonl / responses/ 中保留）；实际打开最终图复核完成。"),
]


def main() -> int:
    reqs = [json.loads(l) for l in REQ.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    used = [t[3] for t in PLAN if t[3] is not None]
    assert sorted(used) == list(range(len(reqs))), \
        f"PLAN 请求行号 {sorted(used)} 与 requests.jsonl 的 {len(reqs)} 条不对齐"

    views = 0
    lines = []
    for ver, parent, typ, ri, reason, viewed, report, note in PLAN:
        rec = reqs[ri] if ri is not None else None
        if viewed:
            views += 1
        lines.append({
            "version": ver,
            "parent": parent,
            "type": typ,
            "label": rec["label"] if rec else "无请求：仅修改自检脚本或重跑自检",
            "reason": reason,
            "request_id": rec["request_id"] if rec else None,
            "request_index_in_log": (ri + 1) if ri is not None else None,
            "started_at": rec["started_at"] if rec else None,
            "ended_at": rec["ended_at"] if rec else None,
            "elapsed_ms": rec["elapsed_ms"] if rec else None,
            "http_status": rec["http_status"] if rec else None,
            "content_type": rec["content_type"] if rec else None,
            "response_bytes": rec["response_bytes"] if rec else None,
            "error_summary": rec["error_summary"] if rec else None,
            "request_path": rec["request_path"] if rec else None,
            "response_body": rec.get("response_path") if rec else None,
            "server_timing": rec["server_timing"] if rec else None,
            "images": ([rec.get("response_path")] if (rec and rec["http_status"] == 200)
                       else []),
            "viewed_not_before": rec["ended_at"] if (rec and viewed) else None,
            "check_report": report,
            "note": note,
            "task_id": "A04",
            "timezone": "Asia/Shanghai (UTC+08:00)",
        })

    dst = TMP / "iterations.jsonl"
    dst.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lines) + "\n",
                   encoding="utf-8")
    print(f"iterations.jsonl → {dst.relative_to(IO.ROOT)}（{len(lines)} 条，"
          f"看图 {views} 次）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
