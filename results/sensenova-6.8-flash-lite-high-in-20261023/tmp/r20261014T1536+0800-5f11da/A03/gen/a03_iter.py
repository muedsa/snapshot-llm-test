"""A03 步骤 8：写出 iterations.jsonl（追加式，不覆盖已存在的基线记录）。

每条记录含：版本 ID、父版本、类型、改动、观察、图像查看下界时间、再查看比较结果。
查看时间只记录真实下界（该响应的结束时间）——没有精确时刻，不编造。

启动基准：总任务根（cwd）。
用法：python a03_iter.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402

TZ = "Asia/Shanghai (UTC+08:00)"
RUN = "r20261014T1536+0800-5f11da"
PREV = f"tmp/{RUN}/A03/preview"
FINAL = f"outputs/{RUN}/A03/system-pulse.png"
VIEW_NOTE = ("未记录精确查看时刻；viewed_not_before 取该响应的结束时间，是真实下界")


def rec(version, parent, kind, req, status, label, change, observed,
        viewed_after=None, image=None, compared=None, note=None) -> dict:
    r = {"version": version, "parent": parent, "type": kind, "label": label,
         "request_id": req, "http_status": status,
         "change": change, "observed": observed,
         "task_id": "A03", "timezone": TZ}
    if image:
        r["image_view"] = {
            "image": image, "viewed": True,
            "viewed_not_before": viewed_after, "note": VIEW_NOTE}
    if compared is not None:
        r["re_view_compare"] = compared
    if note:
        r["note"] = note
    return r


def build() -> list[dict]:
    rows = [
        {
            "version": "v0-original", "parent": None, "type": "baseline",
            "label": "A03 迁移后失效原稿",
            "reason": "原样提交，一字不改，取得服务真实报错（TASK.md 要求的基线）。",
            "request_id": "req-a03-original-0001", "http_status": 400,
            "error_summary": ('PARSE_ERROR Attr [padding] value format error at position 91 '
                              'near: ="png">\\n  <Container padding="24 32" '
                              'borderRadius="24">'),
            "response_body": f"tmp/{RUN}/A03/responses/req-a03-original-0001.body",
            "images": [],
            "note": "失败响应保留，不落输出目录；不把错误 JSON 保存成最终图片。"
                    "服务 requestId=3b6c7fab-dc3e-4326-ab19-de2927c4b508，"
                    "Server-Timing total;dur=289.7。",
            "task_id": "A03", "timezone": TZ,
        },
        rec("p1", "v0-original", "syntax-fix", "req-a03-probe-p1", 400,
            "单点语法修复 1/5：padding 格式",
            '只把 padding="24 32" 改成 padding="(24,32)"，其余一字不改',
            '仍是 400 PARSE_ERROR，但错误位置变了：Attr [matrix] must not be null at '
            'position 466 near: "<Spacer flex=\\"1\\"/>\\n      <Transform rotate=\\"-8\\">"。'
            "说明 padding 是解析器遇到的第一个错误，修好后才轮到 Transform。"),

        rec("p2", "v0-original", "syntax-fix", "req-a03-probe-p2", 400,
            "单点语法修复 2/5：Snapshot 的 width/height",
            "只移除 <Snapshot> 上不存在的 width/height（画布尺寸改由根 Container 给出）",
            '仍是 400，同一个 Attr [matrix] 错误（position 440，相对 p1 左移 26 字节 = '
            '被删字符数）。证明 <Snapshot width/height> 被静默忽略，不是报错源。'),

        rec("p3", "v0-original", "syntax-fix", "req-a03-probe-p3", 400,
            "单点语法修复 3/5：kebab 属性名",
            "只把 font-size 改成 fontSize（属性名大小写敏感）",
            '仍是 400，同一个 Attr [matrix] 错误（position 439）。'
            "证明 kebab 属性名被静默忽略。"),

        rec("p4", "v0-original", "syntax-fix", "req-a03-probe-p4", 400,
            "单点语法修复 4/5：Positioned 的父级",
            '只把 <Positioned right="20"> 包进 <Stack fit="EXPAND">'
            "（Positioned 必须是 Stack 的直接子节点）",
            '仍是 400，同一个 Attr [matrix] 错误（position 467，相对原稿右移 28 字节 = '
            "新增的 Stack 标签）。"),

        rec("p5", "v0-original", "syntax-fix", "req-a03-probe-p5", 400,
            "单点语法修复 5/5：Transform 的 rotate",
            '只移除 <Transform> 上不存在的 rotate 属性，改成裸 <Transform>',
            '仍是 400，错误信息变成 "Attr [matrix] must not be null" near: '
            '<Transform><Container width="1"。五处单点修复全部收敛到同一个 Transform：'
            "rotate 属性不存在，而 matrix 是必填。"),

        rec("probe2-q1", "v0-original", "syntax-fix", "req-a03-probe2-q1", 400,
            "matrix 首次填写（缺外层括号）",
            "把 rotate=\"-8\" 换成 16 个矩阵值但不加外层括号",
            '400 PARSE_ERROR "Attr [matrix] value format error"。矩阵值本身正确'
            "（列主序、θ=-8°），错误原因是外层括号缺失。文档原文：外层必须有括号且值之间不能有空格。",
            note="同批 q2/q3 两次提交在读取响应阶段超时（TimeoutError），没有 HTTP 响应、"
                 "也没有写入 requests.jsonl。这是本题留痕中的真实缺口，"
                 "已在 task-metrics.json 的 unresolved_issues 列出，不补造记录。"),

        rec("probe3-p6", "v0-original", "syntax-fix", "req-a03-probe3-p6", 200,
            "5 项语法全修（自造嵌套错误）",
            "同时修 padding、Snapshot width/height、fontSize、Positioned 包 Stack、"
            "Transform matrix 带括号",
            "返回 200 + PNG，但画面只有标题。复查 DSL 后发现我替换 <Snapshot> 起始标签时"
            "多加了一个外层 <Container> 却漏了对应的 </Container>——这是我引入的错误，"
            "不是原稿缺陷。",
            viewed_after="2026-10-15T00:11:02+08:00", image=f"{PREV}/probe3-p6.png",
            compared="只渲染出标题；不能当干净基线，改用 probe4-p7 重做。"),

        rec("probe3-s1", None, "alternative", "req-a03-probe3-s1", 200,
            "备选方案验证：只模糊卡内背景的结构",
            "<Positioned><ClipRRect borderRadius=\"24\"><BackdropFilter sigmaX=\"10\" "
            "sigmaY=\"10\" tileMode=\"CLAMP\"><Container color=\"transparent\"/>"
            "</BackdropFilter></ClipRRect></Positioned>，卡体填充与文字作为滤镜之后的"
            "独立 Positioned 兄弟节点",
            "卡外细条锐利、卡内为平滑模糊渐变、文字清晰。结构成立。",
            viewed_after="2026-10-15T00:11:04+08:00", image=f"{PREV}/probe3-s1.png",
            compared="作为 v2 的模糊结构依据。"),

        rec("probe3-s2", None, "alternative", "req-a03-probe3-s2", 200,
            "对照组：把文字放进 BackdropFilter 子节点内",
            "唯一差别是文字写在 <BackdropFilter> 内部而非外部",
            "文字仍然清晰。结论：BackdropFilter 只模糊它之前绘制的图层，从不模糊自己的子树；"
            "原稿用 <ImageFiltered> 才会把整棵子树（含文字）一起模糊——这正是原稿"
            "「文字被糊掉」的机制。",
            viewed_after="2026-10-15T00:11:06+08:00", image=f"{PREV}/probe3-s2.png",
            compared="据此把说明卡拆成 细条 → BackdropFilter → 卡体填充 → 文字 四层。"),

        rec("probe4-p7", "v0-original", "syntax-fix", "req-a03-probe4-p7", 200,
            "干净的语法-only 修复（零结构改动）",
            "只改 5 处语法项（padding 括号、去掉 Snapshot width/height 并给根 Container "
            "尺寸、fontSize、Positioned 包 Stack、Transform matrix 带括号），"
            "不新增或移动任何节点",
            "服务返回 200 和正常 PNG，但画面里只有标题。",
            viewed_after="2026-10-15T00:18:04+08:00", image=f"{PREV}/probe4-p7.png",
            compared="修好全部显式语法错误后仍有大面积内容缺失——进入 TASK.md 要求的"
                     "「未生效属性 / 画布尺寸 / 有界布局」排查。"),

        rec("probe4-p8", "probe4-p7", "syntax-fix", "req-a03-probe4-p8", 200,
            'p7 加 debug="true" 查看布局盒子',
            '只在 <Snapshot> 上加 debug="true"',
            "布局调试层里只有两个盒子：根容器与标题。<Row> 及其之后的所有兄弟节点没有"
            "进入布局树。（该版本服务端渲染耗时 2595ms，明显高于其他版本。）",
            viewed_after="2026-10-15T00:18:07+08:00", image=f"{PREV}/probe4-p8.png",
            compared="把「内容消失」从猜测变成可定位的事实：Column 的第二个子节点起被丢弃。"),

        rec("probe5-layout", None, "alternative", "req-a03-probe5-layout", 200,
            "有界布局二分定位（一图四象限）",
            "把可疑结构拆成 T1 Row+Expanded、T2 Row+Stack+Positioned、T3 Row+Container、"
            "T4 Spacer+Transform+ImageFiltered 四格对照，每格固定 576×336 容器",
            "T1：Expanded flex=1 覆盖子节点固定尺寸——width=\"360\" 的灰块被拉满 576，"
            "原稿「三个等宽」不成立。T2：Row > Stack(fit=EXPAND) > Positioned > Text "
            "什么都不渲染，这是原稿整棵子树消失的机制。T3：Row > Container 正常。"
            "T4：#33FFFFFF 渲染成不透明青色，#FFFFFF44 实测为白色 26.7%。",
            viewed_after="2026-10-15T00:32:26+08:00", image=f"{PREV}/probe5-layout.png",
            compared="第一次尝试在读取阶段超时（300s），重试成功，attempts=2。",
            note="另存 T1 与 T4 的放大裁图 probe5-T1-zoom.png、probe5-T4-zoom.png 用于确认细节；"
                 "两次裁图均由真实渲染响应裁剪而来，未用于输出。"),

        rec("v1", "probe4-p7", "visual", "req-a03-v1-preview", 200,
            "首个完整设计版本",
            "按题目重新构造全部元素：根 Container 1280×800 + padding=(32,32)、44 号标题、"
            "96×36 LIVE、三个 384 宽指标卡、500×150 圆角 24 说明卡 + 5 条彩色细条 + "
            "BackdropFilter、160×56 逆时针 8° REVIEW",
            "整体构图正确，但几何整体右下偏移 32px：内容外接框 [64,74,1279,773]，"
            "右余量 0（贴住画布边缘），第三张指标卡与 REVIEW 都溢出 32px 安全边距。",
            viewed_after="2026-10-15T00:18:11+08:00", image=f"{PREV}/v1.png",
            compared="根 Container 的 padding 把 Stack 原点平移了 (+32,+32)，而所有 "
                     "<Positioned> 写的是画布绝对坐标——漏减了 32。这是我引入的缺陷 V-1，"
                     "不是原稿问题。像素证据见 tmp/<run_id>/A03/v1-inspect.json。"),

        rec("v2", "v1", "visual", "req-a03-v2-preview", 200,
            "视觉迭代 1：修正坐标系偏移",
            "所有布局常量改为画布绝对坐标，<Positioned> 值统一经 L()/T() 减去安全边距 32；"
            "REVIEW 卡体改用 #FFFFFF33（白色 alpha=20%，alpha 在十六进制末两位）",
            "内容外接框 [32,42,1247,735]，安全边距余量 left=32 top=42 right=32 bottom=64，"
            "min=32，全部在安全区内。",
            viewed_after="2026-10-15T00:21:50+08:00", image=f"{PREV}/v2.png",
            compared="与 v1 逐项对比后全部通过：三卡等宽 384（max_width_delta=0）、间距 32；"
                     "LIVE 实测 96×36 位于 x1152..1247，标题右边界 x322，不遮挡；"
                     "说明卡实测 500×150（边框行 446/595、边框列 390/889）；"
                     "细条 x250..1029，越过卡两侧边界各 140px；"
                     "卡外单步亮度跳变均值 173.77 vs 卡内 10.48（比值 16.59），"
                     "证明只模糊卡内背景；文字笔画最大跳变 172.09 远大于卡内背景，"
                     "证明文字保持清晰；REVIEW 外接框 164×76（预期旋转外接框 167×78，"
                     "差值来自圆角与抗锯齿）、方向 counterclockwise、完全可见且在安全区内；"
                     "卡体众数 [58,64,76] 与白色 20% 理论值 [60,65,77] 通道差 ≤2。"
                     "证据见 tmp/<run_id>/A03/v2-inspect.json 与 alpha-check.json。"),

        rec("v2", "v2", "retry", "req-a03-v2-final", 200,
            "最终交付提交（同一 DSL 重提交，无内容变更）",
            "DSL 与 v2-preview 完全相同，只是把真实响应写入输出目录为 "
            "system-pulse.png / system-pulse.snapshot",
            "200 image/png 48526 B，与 preview 同字节数。已实际打开最终 PNG 复核。",
            viewed_after="2026-10-15T01:00:48+08:00", image=FINAL,
            compared="最终图逐项满足题面要求；不是一次视觉迭代（无内容改动）。"),
    ]
    return rows


def main() -> None:
    out, tmp = IO.dirs()
    p = tmp / "iterations.jsonl"
    prev = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if p.exists() else []
    incoming = {r["version"] for r in build()}
    keep = [l for l in prev if json.loads(l)["version"] not in incoming]
    rows = keep + [json.dumps(r, ensure_ascii=False) for r in build()]
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"写入 {p}：{len(rows)} 条")
    for l in rows:
        r = json.loads(l)
        print(f"  {r['type']:11s} {r['version']:14s} <- {r['parent']} | "
              f"{r['request_id']} | HTTP {r['http_status']}")


if __name__ == "__main__":
    main()
