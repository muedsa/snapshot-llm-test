"""A17 写 iterations.jsonl：版本 ID、父版本、类型、图像路径、可观察问题、具体改动、复查结果。

时间戳取自 requests.jsonl 中对应请求的 started_at，不手写。
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A17"
TZ = "Asia/Shanghai (UTC+08:00)"
NOW = "2026-10-19T11:05:00+08:00"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    reqs = {r["request_id"]: r for r in
            [json.loads(l) for l in (TASK_TMP / "requests.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]}

    def t(rid):
        return reqs[rid]["started_at"] if rid in reqs else None

    def e(rid):
        return reqs[rid]["ended_at"] if rid in reqs else None

    rows = [
        {"iteration_id": "a17-it-01", "parent": None, "type": "baseline",
         "started_at": t("req-a17-probe-dd116f"), "timezone": TZ,
         "versions": ["probe-constructs", "probe-backdrop", "probe-backdrop2",
                      "probe-cdata-print", "probe-column", "probe-flexchild"],
         "images_viewed": [
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe-dd116f.png",
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe2-80cf1a.png",
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe3-edc082.png",
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe4-eb9831.png",
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe5-1b734f.png",
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe6-5091d8.png"],
         "observed_problem": "6 组构件探针全部 200；BackdropFilter 在纯色背景上看不到模糊",
         "change": "确立构件契约：Raw+CDATA 多行代码、Text 直接 CDATA、Row/Expanded/STRETCH、"
                   "Column/Expanded、Stack/Positioned、ClipRRect+BackdropFilter、"
                   "ImageFiltered、ColorFiltered、8 位尾部 alpha、逗号分隔多字体、"
                   "行高与嵌套 Text/Raw；BackdropFilter 演示改为纹理背景",
         "recheck": "req-a17-probe2-80cf1a 在纹理背景上确认可见模糊后继续"},
        {"iteration_id": "a17-it-02", "parent": "a17-it-01", "type": "syntax-fix",
         "started_at": t("req-a17-handbook-01-2d8a0e"), "timezone": TZ,
         "versions": ["handbook-01 首版", "handbook-02 首版",
                      "handbook-03 首版", "handbook-04 首版"],
         "images_viewed": [],
         "observed_problem": "4 页全部 400 PARSE_ERROR「Tag Container only can have one child, "
                             "but get other Text」（-03 报的是 Positioned 同一契约）",
         "change": "把每个 Container / Positioned 收敛为单一子元素，"
                   "需要多个子元素时先包一层 Column 或 Stack",
         "recheck": "下一次渲染后 -02/-03/-04 报同一契约的残留，-01 转 RENDER_ERROR，"
                    "说明解析层已过第一关"},
        {"iteration_id": "a17-it-03", "parent": "a17-it-02", "type": "syntax-fix",
         "started_at": t("req-a17-handbook-03-8730d7"), "timezone": TZ,
         "versions": ["handbook-03 修订版"],
         "images_viewed": [],
         "observed_problem": "400 PARSE_ERROR Unexpected character ' ' in input state [TAG_OPEN] "
                             "at position 8064：要点正文里写了字面 <（如 'Text <Raw>'），"
                             "本服务不做 HTML 实体解码，'<' 在元素内容里被当作标签开头",
         "change": "要点与正文一律走 <Raw><![CDATA[...]]></Raw>，"
                   "分隔空格一并放进 CDATA；属性值禁止出现 < 与 &；"
                   "新增 a17_check.py 的静态规则在发请求前拦下同类问题",
         "recheck": "4 页均通过解析，转 RENDER_ERROR，进入根结构定位"},
        {"iteration_id": "a17-it-04", "parent": "a17-it-03", "type": "syntax-fix",
         "started_at": t("req-a17-probe-A-root-container-3889eb"), "timezone": TZ,
         "versions": ["probe-A-root-container", "probe-B-skeleton",
                      "probe-C-codeblock", "probe-D-keys",
                      "handbook-01..04 修订版"],
         "images_viewed": [
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe-A-root-container-3889eb.png",
             "tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe-A-root-container-b38ed6.png"],
         "observed_problem": "4 页 400 RENDER_ERROR「Layout size is infinite」；"
                             "4 个 400×240 独立示例却全部 200，说明核心子树可用，"
                             "问题只在手册页根结构",
         "change": "四组对照探针：P-A 根 Stack 外包显式尺寸 Container=200；"
                   "P-B 旧根结构只放骨架 Positioned=400；P-C 旧根结构 + 代码块=400；"
                   "P-D 旧根结构 + 要点块=超时。根因收敛为 <Stack> 直接做 <Snapshot> 的"
                   "子节点拿到无限约束、fit=EXPAND 触发 Layout size is infinite。"
                   "手册页改为 Snapshot > Container(1200×1600) > Stack",
         "recheck": "8 件一次渲染全部 200（handbook-04 遇超时后重发成功）"},
        {"iteration_id": "a17-it-05", "parent": "a17-it-04", "type": "visual",
         "started_at": e("req-a17-probe-D-keys-98bd1a"), "timezone": TZ,
         "versions": ["handbook-04 修订版2", "example-04 修订版2"],
         "images_viewed": [
             "outputs/r20261014T1536+0800-5f11da/A17/handbook-04.png（首版）",
             "outputs/r20261014T1536+0800-5f11da/A17/example-04.png（首版）",
             "tmp/r20261014T1536+0800-5f11da/A17/preview/hb4-illus.png（2×）",
             "tmp/r20261014T1536+0800-5f11da/A17/preview/ex4-glass.png（3×）",
             "outputs/r20261014T1536+0800-5f11da/A17/example-04.png（修订）",
             "tmp/r20261014T1536+0800-5f11da/A17/preview/hb4-glass.png（修订后 3×）",
             "outputs/r20261014T1536+0800-5f11da/A17/handbook-04.png（修订）"],
         "observed_problem": "第 4 页毛玻璃面板 136×92@(118,10) 太窄：PIL 像素采样显示面板左缘外"
                             "x=128 仍是未模糊的 (56,189,248) 源色块、x=120 是未模糊的 "
                             "(60,73,93) 标签文字，色块与文字一半在玻璃内一半在玻璃外，"
                             "作为「BackdropFilter + ClipRRect」的教学图会造成误读",
         "change": "仅改 2 行属性值（印刷行 30 与 33）：Positioned left=118 top=10 "
                   "width=136 height=92 → left=104 top=6 width=196 height=96；"
                   "内部 Container 同步 196×96。结构、子节点顺序、滤镜参数、印刷行数均不变",
         "recheck": "重渲后像素采样：面板内 x=120 已为模糊值 (227,246,254)、"
                    "标签行 y=110 最暗仅 (244,246,246)，两个源色块与整行标签均完整位于"
                    "玻璃区域内；3× 放大确认无未模糊的源色块边缘。"
                    "a17_check.py 复核 ok=true（印刷 17 行仍在 8–18 区间）"},
        {"iteration_id": "a17-it-06", "parent": "a17-it-04", "type": "retry",
         "started_at": t("req-a17-handbook-01-b9c0f6"), "timezone": TZ,
         "versions": ["重试：handbook-01", "重试：handbook-04", "重试：example-04"],
         "images_viewed": [],
         "observed_problem": "4 次请求 status=0：handbook-01-b9c0f6 读超时、"
                             "handbook-04-ad445e 读超时、probe-D-keys-98bd1a 读超时、"
                             "example-04-806a05 连接失败（均 elapsed_ms=null）",
         "change": "按真实响应重发同一 DSL，不修改内容；不把这些超时的等待时间计入渲染耗时",
         "recheck": "handbook-01 由 handbook-01-646467 补齐、handbook-04 由 c3a48d 与 5f859e "
                    "补齐、example-04 由 0f4e38 补齐；probe-D 未取得图像，"
                    "但该结论已由 P-A/P-B/P-C 三组互证"},
    ]
    with (TASK_TMP / "iterations.jsonl").open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"written": len(rows),
                      "file": str((TASK_TMP / "iterations.jsonl").relative_to(SUITE_ROOT))},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
