"""A17 构建入口：生成 4 张手册页（1200x1600）+ 4 个独立示例（400x240），真实渲染并留痕。

用法：
  python -I a17_build.py            # 生成 DSL + 渲染到 tmp/<run_id>/A17/
  python -I a17_build.py --promote  # 额外把服务原始 PNG 与同名 .snapshot 落到 outputs/
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import shutil
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A17"
TASK_OUT = SUITE_ROOT / "outputs" / RUN_ID / "A17"

sys.path.insert(0, str(HERE.parent))
from a17_core import CORES, SEGMENTS                        # noqa: E402
from a17_page import page_dsl, printed_spec                 # noqa: E402

CODE_CAP = "印刷代码片段"
ILUS_CAP = "教学插图（本页 DSL 构件直接绘制）"

CONTENT = {
    1: dict(
        chapter="第 1 页 / 4  ·  Snapshot DSL 入门手册",
        title="服务调用契约：输入、输出与错误响应",
        intro="请求体是 UTF-8 编码的纯文本 DSL，Content-Type 用 "
              "text/plain; charset=utf-8；成功返回图片二进制，"
              "解析失败返回带 code、message、requestId 的 JSON。",
        keys=[
            ("#0EA5E9", "请求体是 UTF-8 纯文本，Content-Type: "
                         "text/plain; charset=utf-8，不是 JSON 端点。"),
            ("#10B981", "成功返回图片二进制，后缀要与实际编码一致；"
                         "失败返回 JSON，不要把错误 JSON 存成 .png。"),
            ("#F59E0B", "400 PARSE_ERROR 的 message 给出出错行列，"
                         "按行列修正后重发即可。"),
            ("#EF4444", "413 请求过大，401 认证失败，429 与部分 503 "
                         "按 Retry-After 重试。"),
            ("#7C3AED", "X-Request-Id 可关联服务端日志；curl 要用退出码、"
                         "HTTP 状态与 Content-Type 判断成功。"),
        ],
        purpose="第 1 页可运行示例：把请求、成功响应与错误响应的三条分支"
                "画成一张对照图，直观说明输入是文本、输出是二进制、"
                "失败是 JSON。"),
    2: dict(
        chapter="第 2 页 / 4  ·  Snapshot DSL 入门手册",
        title="画布尺寸由布局决定，有界布局与 Stack 定位",
        intro="根标签 Snapshot 本身不声明画布宽高；父节点向下传递 "
              "BoxConstraints，子节点在约束范围内选择自己的宽高，"
              "设置 width 或 height 就是在收紧约束。",
        keys=[
            ("#0EA5E9", "Row/Column 用 mainAxisAlignment 分主轴，"
                         "mainAxisSize 默认 MAX 撑满主轴。"),
            ("#6366F1", "Expanded 等价于 Flexible fit=TIGHT，"
                         "两者只能是 Flex 的直接子节点。"),
            ("#F59E0B", "交叉轴默认不撑满，只有 crossAxisAlignment=STRETCH "
                         "才强制填满交叉轴。"),
            ("#EC4899", "弹性分配只改变主轴约束；父级交叉轴无界时"
                         "不会凭空产生有限约束。"),
            ("#10B981", "Stack 先布局普通子节点（默认 TOP_LEFT），"
                         "再按 left/top/right/bottom 放 Positioned。"),
        ],
        purpose="第 2 页可运行示例：同一个有界容器里并排放 Row（STRETCH + "
                "Expanded + 固定宽度子项）与 Stack（left/top 与 right/bottom "
                "两种 Positioned 写法），对照主轴分配、交叉轴拉伸与定位。"),
    3: dict(
        chapter="第 3 页 / 4  ·  Snapshot DSL 入门手册",
        title="Raw、CDATA、富文本与尾部 alpha 的四个误解",
        intro="解析器不做 HTML 实体解码，实体写法不会被展开，"
              "尖括号要写进 CDATA 才能原样输出；Text 会 trim 首尾空白而 Raw 不 trim；"
              "8 位颜色的最后两位是透明度。",
        keys=[
            ("#0F172A", "解析器不做 HTML 实体解码，要印尖括号就得写 CDATA。"),
            ("#334155", "Text 会 trim 首尾空白，Raw 保留首尾空格与换行；"
                         "未设置字段继承祖先。"),
            ("#0EA5E9", "嵌套 Text 构成富文本，子 Span 只覆盖自己声明的"
                         "样式，其余继承父级。"),
            ("#F59E0B", "8 位颜色 #RRGGBBAA 的最后两位是透明度，"
                         "#38BDF880 约为 50% 透明。"),
            ("#7C3AED", "fontFamily 用英文逗号分隔且不逐项 trim，"
                         "逗号后加空格会保留前导空格。"),
        ],
        purpose="第 3 页可运行示例：三行对照——CDATA 内原样输出 a < b && b > a，"
                "Raw 保留首尾空格，深色底上并排 #38BDF8 与 #38BDF880 观察尾部 alpha。"),
    4: dict(
        chapter="第 4 页 / 4  ·  Snapshot DSL 入门手册",
        title="背景滤镜、子树滤镜、视觉自检与可复现交付",
        intro="Opacity、ColorFiltered、ImageFiltered 作用在子树结果上；"
              "BackdropFilter 只模糊已经绘制在其背后的内容，背后是纯色时"
              "看不出效果，通常要用 ClipRRect 限定区域。",
        keys=[
            ("#0EA5E9", "ImageFiltered 对子树结果做滤镜，"
                         "会自动按 sigma 提供模糊输出边界。"),
            ("#7C3AED", "ColorFiltered 在绘制边界可确定时限定作用范围，"
                         "合法溢出与阴影都包含在内。"),
            ("#F59E0B", "BackdropFilter 背后必须有已绘制内容，"
                         "并用 ClipRRect 限定区域才看得见。"),
            ("#10B981", "自检顺序：布局数值断言 > 像素采样 > Golden > "
                         "Artifact；Artifact 不是断言。"),
            ("#EF4444", "可复现：固定字体与颜色空间，网络图片先转本地资源，"
                         "不把时间与随机数写入图像。"),
        ],
        purpose="第 4 页可运行示例：上层毛玻璃面板叠在彩色纹理上验证 "
                "BackdropFilter，下层并排 ImageFiltered 模糊与 ColorFiltered "
                "MULTIPLY，右侧卡片提示像素采样的取样位置。"),
}

FILES = {
    1: ("handbook-01", "example-01", 1200, 1600, 400, 240),
    2: ("handbook-02", "example-02", 1200, 1600, 400, 240),
    3: ("handbook-03", "example-03", 1200, 1600, 400, 240),
    4: ("handbook-04", "example-04", 1200, 1600, 400, 240),
}


def build_dsls() -> dict:
    """返回 {文件名: (dsl 文本, 宽, 高, 用途说明)}。"""
    from a17_core import independent_dsl
    out = {}
    for page in range(1, 5):
        hb, ex, _, _, _, _ = FILES[page]
        c = CONTENT[page]
        out[hb] = (page_dsl(page, c["chapter"], c["title"], c["intro"],
                            CODE_CAP, ILUS_CAP, c["keys"]), 1200, 1600,
                   "手册第 %d 页" % page)
        out[ex] = (independent_dsl(page), 400, 240, c["purpose"])
    return out


def render_one(dsl, label, rid):
    import suite as S
    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    try:
        status, body, meta = S.snapshot_request("A17", dsl, label, timeout=240)
        err = S.error_summary(body) if status != 200 else None
    except (TimeoutError, ConnectionError, http.client.HTTPException) as exc:
        status, body = 0, None
        err = f"{type(exc).__name__}: {exc}"
        meta = {"status": 0, "content_type": None, "elapsed_ms": None}
    return status, body, meta, started, err, rid


def main() -> int:
    promote = "--promote" in sys.argv
    os.environ.setdefault("SNAPSHOT_RUN_ID", RUN_ID)
    os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(SUITE_ROOT))
    sys.path.insert(0, str(SUITE_ROOT / "tools"))

    dsl_dir = TASK_TMP / "dsl"
    resp_dir = TASK_TMP / "responses"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    resp_dir.mkdir(parents=True, exist_ok=True)

    dsls = build_dsls()
    results = []
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    for name, (dsl, w, h, purpose) in dsls.items():
        if only and name not in only:
            continue
        dsl_path = dsl_dir / (name + ".snapshot")
        dsl_path.write_text(dsl, encoding="utf-8")
        rid = "req-a17-%s-%s" % (name, uuid.uuid4().hex[:6])
        status, body, meta, started, err, _ = render_one(dsl, name, rid)
        kind = ".png" if status == 200 else ".error.json"
        resp_path = resp_dir / (rid + kind)
        resp_path.write_bytes(body or b"")
        rec = {"request_id": rid, "task_id": "A17", "kind": "render",
               "purpose": purpose, "dsl_path": str(dsl_path.relative_to(SUITE_ROOT)),
               "started_at": started, "ended_at": meta.get("ended_at"),
               "timezone": "Asia/Shanghai (UTC+08:00)",
               "expected_size": {"width": w, "height": h},
               "elapsed_ms": meta.get("elapsed_ms"),
               "elapsed_ms_source": "本地墙钟 time.monotonic（含网络往返）",
               "http_status": status, "content_type": meta.get("content_type"),
               "response_bytes": len(body) if body else 0,
               "response_path": str(resp_path.relative_to(SUITE_ROOT)),
               "error_summary": err}
        import suite as S
        S.log_request("A17", rec)
        results.append(dict(name=name, width=w, height=h, status=status,
                            bytes=len(body) if body else 0,
                            elapsed_ms=meta.get("elapsed_ms"),
                            response=str(resp_path.relative_to(SUITE_ROOT)),
                            dsl=str(dsl_path.relative_to(SUITE_ROOT)),
                            error=err))
        print(json.dumps({"name": name, "status": status,
                          "bytes": rec["response_bytes"],
                          "elapsed_ms": rec["elapsed_ms"]}, ensure_ascii=False))

        if promote and status == 200:
            TASK_OUT.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(resp_path, TASK_OUT / (name + ".png"))
            shutil.copyfile(dsl_path, TASK_OUT / (name + ".snapshot"))

    manifest = TASK_TMP / "build-manifest.json"
    manifest.write_text(json.dumps(
        {"run_id": RUN_ID, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
         "timezone": "Asia/Shanghai (UTC+08:00)",
         "printed_spec": {str(p): printed_spec(p) for p in (1, 2, 3, 4)},
         "core_line_counts": {str(p): len(CORES[p].split("\n"))
                              for p in (1, 2, 3, 4)},
         "core_segments": {str(p): [list(x) for x in SEGMENTS[p]]
                           for p in (1, 2, 3, 4)},
         "requests": results},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest.relative_to(SUITE_ROOT)),
                      "all_ok": (not only)
                      and bool(results)
                      and all(r["status"] == 200 for r in results)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
