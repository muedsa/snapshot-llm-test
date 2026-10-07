"""A18 wrap-up: log the real iteration sequence, build task-metrics.json, update suite state.

The iteration records below are the actual order in which renders were produced and
images were opened during this task. Nothing here is retro-fitted: every viewed_at
timestamp is the wall-clock time of the image read that actually happened.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A18"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import wrapup  # noqa: E402

STARTED = "2026-10-05T00:22:19+08:00"
FIRST_IMAGE = "2026-10-05T00:47:12+08:00"


def p(*a):
    return os.path.join(TMP, *a)


ITERS = [
    # version, parent, kind, dsl, image, viewed_at, observed, changes, complete
    ("A18-v01", None, "baseline",
     p("drafts", "v00-probe.snapshot"), p("preview", "probe01.png"),
     "2026-10-05T00:47:12+08:00",
     "DSL 能力探针：需确认 Container transform 旋转、径向渐变、粗描边圆环、36px 圆、"
     "等宽数字、中文与虚线是否按预期渲染。上一条渲染 A18-req-008 因根 Container 多子节点报 400。",
     "改为 D.snapshot([D.stack(kids, W, H)], ...) 结构，并把根 Stack 直接作为唯一子节点；"
     "探针内同时放置 0/90/180/270 度旋转细矩形、radial gradient、8px 描边圆环、四个 36px 圆、"
     "DejaVu Sans Mono / Noto Sans CJK SC / tnum=2 文本与虚线。",
     True),
    ("A18-v02", None, "baseline",
     p("drafts", "preview-concept-A.snapshot"), p("preview", "preview-concept-A.png"),
     "2026-10-05T01:05:40+08:00",
     "构图 A 首版（A18-req-010）：三幕骨架成立，但脚本几何断言报 act3 unit overlap "
     "min centre distance 0.00；肉眼看幕三是三行完全相同的图形，明显缺了每车道各自的单元位置。",
     "定位到 layout_A 里幕三的 spot 只按第一车道算了一次；改为按车道索引取位置的函数。",
     True),
    ("A18-v03", "A18-v02", "visual",
     p("preview", "preview-concept-A.snapshot"), p("preview", "preview-concept-A.png"),
     "2026-10-05T01:07:02+08:00",
     "重叠已修（act3 最小圆心距 70.77px）。新问题：径向光晕读成大块糊斑、幕三左右失衡且过疏、"
     "幕二下半部空、底部公式条明显偏左、端口减半几乎看不出来。",
     "本版只做重叠修复，几何与配色未动，作为后续视觉迭代的对照基线。",
     True),
    ("A18-v04", None, "alternative",
     p("drafts", "preview-concept-B.snapshot"), p("preview", "preview-concept-B.png"),
     "2026-10-05T01:12:44+08:00",
     "构图 B（轴向队列→压缩→三车道）完整 1600x1000 预览：幕一读成“排队”而非“中心吸引”；"
     "几何断言报 act2 有一条连线到某圆心仅 15.10px（<18+线半宽），会被判“线遮圆”。",
     "未修改，作为被弃用的备选留档；幕三的车道几何可用，稍后并入构图 A。",
     False),
    ("A18-v05", "A18-v03", "visual",
     p("preview", "preview-concept-A-v02.snapshot"), p("preview", "preview-concept-A-v02.png"),
     "2026-10-05T01:20:31+08:00",
     "光晕降透明度并收紧衰减后干净多了；但幕三仍显空、幕二下半部仍空、端口 44→22 的差别在整图上看不出、"
     "底部公式条偏左（起点写死 x=90，实际等宽步宽约 10.24px）。",
     "移植构图 B 的幕三车道几何：节点移到面板中心 +20（px+265），左右列外扩到 ∓78/∓130/∓182，"
     "错位量改为 ∓48/±24，车道间距 200→210；幕一环半径 158→196；光晕改三色三停靠点；"
     "端口加亮到 7px 厚；闲置节点移到面板下两角。",
     True),
    ("A18-v06", "A18-v05", "visual",
     p("preview", "preview-concept-A-v03.snapshot"), p("preview", "preview-concept-A-v03.png"),
     "2026-10-05T01:26:55+08:00",
     "幕三平衡了、公式条居中了；但幕一/幕二缺一条共同的参照界，幕二的“被压缩进来”只能靠对比两图推断，"
     "端口空槽在整图上仍偏弱。",
     "加入幕一/幕二共用的 R=232 虚线场界与幕三每节点 R=100 虚线小场界（101 段短矩形拼出，"
     "半径选择保证 |d-R|>18.6 不切到任何圆）；端口空槽改为描边空心槽；幕一环心下移到 PY+310；"
     "底部公式条按 DejaVu Sans Mono 0.6023em 实测步宽计算居中 x。",
     True),
    ("A18-v07", "A18-v06", "requirement-change",
     os.path.join(OUT, "three-act-story.snapshot"), os.path.join(OUT, "three-act-story.png"),
     "2026-10-05T01:35:20+08:00",
     "按 TASK.md 收口：三幕需要更明显的密度/光线差异，且第三幕台账要给出精确到一位小数的每节点负载。",
     "线宽 2.0/3.0/2.5 改为 1.8/3.4/2.4（拉开幕一稀疏与幕二致密的纹理差）；"
     "幕三台账 LOAD 25/23/27% 改为精确值 25.0/23.3/26.7%。",
     True),
    ("A18-v08", "A18-v07", "visual",
     p("preview", "preview-concept-A-v04.snapshot"), p("preview", "preview-concept-A-v04.png"),
     "2026-10-05T01:41:08+08:00",
     "像素自检发现节点壳 #1B2838 与面板渐变顶色 #17253D 只差 (4,3,5)，无法在像素上量出节点尺寸；"
     "肉眼看节点与面板对比也偏弱。",
     "节点壳改 #243447（活跃）/#16202E（闲置）、内核改 #0B1220，与面板拉开距离并更醒目。",
     True),
    ("A18-v09", "A18-v08", "visual",
     os.path.join(OUT, "three-act-story.snapshot"), os.path.join(OUT, "three-act-story.png"),
     "2026-10-05T01:45:37+08:00",
     "最终稿（DSL 与 v08 逐字节相同，服务端 Server-Timing 报 cache;desc=hit，字节一致 267044B）。"
     "整图查看：幕一稀疏辐射、幕二致密团块与更亮的暖光、幕三三车道，密度/构图/光线三层都不同；"
     "节点与面板已能分辨。",
     "以本版为交付；随后跑 verify_a18.py 做 33 项像素+DSL 复核，全部通过，并另看 400px 缩略确认三幕仍可读。",
     True),
]

ARTIFACTS = [
    "three-act-story.png",
    "three-act-story.snapshot",
    "story-audit.json",
    "rationale.md",
    "snapshot-usage.md",
    "task-metrics.json",
    "verification.json",
]

VISUAL = [
    "full-figure read of tmp/.../preview/probe01.png (DSL capability probe: rotated Container "
    "transform spokes at 0/90/180/270 deg, radial gradient, thick border ring, 36px discs, "
    "mono/CJK/tnum text, dashed rule)",
    "full-figure read of tmp/.../preview/preview-concept-A.png (concept A, act-3 overlap fixed)",
    "full-figure read of tmp/.../preview/preview-concept-B.png (rejected alternative composition)",
    "full-figure read of tmp/.../preview/preview-concept-A-v02.png",
    "3.0x zoom crop of the act-2 node in preview-concept-A-v02.png (ports + half intake)",
    "full-figure read of tmp/.../preview/preview-concept-A-v03.png",
    "3.0x zoom crop of the act-2 node in preview-concept-A-v03.png",
    "2.4x zoom crop of an act-3 lane in preview-concept-A-v03.png",
    "400px-wide thumbnail read of preview-concept-A-v03.png",
    "full-figure read of outputs/.../three-act-story.png (v07)",
    "full-figure read of outputs/.../three-act-story.png (final, v09)",
    "400px-wide thumbnail read of outputs/.../three-act-story.png",
]

UNRESOLVED = [
    "token / image-input usage / cost are unknown: the anonymous open-snapshot service exposes "
    "no billing or usage endpoint and the chat platform reported no per-request figures, so "
    "task-metrics.json keeps every usage field null instead of estimating",
    "rate-limit or queue wait is unknown (null): no successful response reported a queue segment "
    "in Server-Timing, so it is not recorded as 0",
    "TASK.md asks for act names + overall title only, but also for the conserved values to be "
    "shown on the figure; nodes and units carry zero text, and the extra elements are three rows "
    "of purely numeric instrument readouts per act plus one conservation formula line at the "
    "bottom - documented as a deliberate trade-off in snapshot-usage.md section 6",
    "node positions move between acts 1-2 (idle nodes in the lower corners) and act 3 (three "
    "lanes) so that 'each node receives 5 units of at least two colours' is countable at a "
    "glance; identity is carried by the 1/2/3 index marks in each node's top-left corner",
]

NOTES = ("1600x1000 three-act conserved-object narrative. 15 units x 3 acts, all 36px, load "
         "equivalent 45 pts conserved across acts (45=45+0 / 45=30+15 / 45=15+14+16, d=0/0/0). "
         "Concept A chosen over concept B after rendering both as real 1600x1000 previews. "
         "33 pixel+DSL verification checks in verification.json all pass.")


def main():
    ended = "2026-10-05T01:52:00+08:00"
    # iterations.jsonl is written by this script only; a previous run of it wrote the
    # same nine rows with a task start timestamp that disagreed with suite-state.json.
    # Those rows are replaced (not duplicated) so the log stays exactly one row per
    # real render/view pair.
    log = os.path.join(TMP, "iterations.jsonl")
    if os.path.exists(log):
        with open(log, encoding="utf-8") as fh:
            n = sum(1 for line in fh if line.strip())
        with open(log + ".superseded-first-run.jsonl", "w", encoding="utf-8") as fh:
            fh.write(open(log, encoding="utf-8").read())
        os.remove(log)
        print("rotated previous iterations log, %d rows -> .superseded-first-run.jsonl" % n)
    m = wrapup.wrapup(TASK, STARTED, FIRST_IMAGE, ended, ITERS, ARTIFACTS, VISUAL,
                      unresolved=UNRESOLVED, notes=NOTES, status="completed",
                      rounds=["round-01"], cases=[])
    print(json.dumps({k: m[k] for k in ("wall_clock_seconds_total", "counts", "failures")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()