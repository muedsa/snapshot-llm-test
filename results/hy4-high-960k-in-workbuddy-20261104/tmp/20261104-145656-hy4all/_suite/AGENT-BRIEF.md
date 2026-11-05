# 并行子代理执行简报（Snapshot 全套任务）

## 环境与路径（务必遵守，不写死机器路径）

- 总任务根：`D:/mine/test/hy4-high-960k-in-workbuddy`（运行时用 `SNAPSHOT_TASK_ROOT` 环境变量，默认当前目录）
- run_id：`20261104-145656-hy4all`（环境变量 `SNAPSHOT_RUN_ID`）
- 共享工具目录：环境变量 `TOOLS`（即 `tmp/20261104-145656-hy4all/_suite/tools/`）
- 服务：`https://open-snapshot.muedsa.com`，`POST /snapshot` 提交 UTF-8 纯文本 DSL，成功返回 `image/png` 原始字节。
- 所有记录中的本地路径必须相对总任务根（`path_base=suite_root`）或相对本题输出根（`output_dir`），**不得写绝对路径/盘符**。

启动每条 Bash 命令前设置：

```bash
cd "D:/mine/test/hy4-high-960k-in-workbuddy" && export SNAPSHOT_TASK_ROOT="$PWD" SNAPSHOT_RUN_ID="20261104-145656-hy4all" TOOLS="$PWD/tmp/20261104-145656-hy4all/_suite/tools" AGENT_NO_STATE=1
```

（`$PWD` 是运行时计算，不是写死路径；脚本和记录里保存相对路径。）

## 必读文档（已缓存，直接读本地）

- `tmp/20261104-145656-hy4all/_suite/docs/ai-guide.md`、`openapi.yaml`
- `tmp/20261104-145656-hy4all/_suite/docs/parser.md`、`parser-tags.md`、`parser-text.md`、`examples.md`、`fonts.md`、`media-text.md`
- 字体清单 `tmp/20261104-145656-hy4all/_suite/docs/fonts.txt`：中文用 `Noto Sans CJK SC`，拉丁/数字用 `Inter`，等宽用 `Noto Sans Mono CJK SC`，Emoji 回退 `Noto Color Emoji`。
- 每题目录：`tasks/<目录>/TASK.md`、`task.json`、`AGENTS.md`、`inputs/`、`templates/`。**必须逐题实际读取**。

## 已验证可复用的 DSL 构建库

`TOOLS/dsl.py` 提供 `Canvas` 类（`tmp/.../_suite/tools/dsl.py`），已在本套 A01–A06 真实服务验证：

```python
import sys, os
sys.path.insert(0, os.environ["TOOLS"])
from dsl import Canvas, LATIN
import suite
c = Canvas(1600, 1000, "#F4F7FC")   # 固定画布，Stack + Positioned 绝对布局
c.rect(x, y, w, h, color, radius=0, border="1 SOLID #CCCCCC", opacity=None)
c.gradient(x, y, w, h, ["#0B1B35", "#16386F"], radius=0)
c.circle(cx, cy, r, color)
c.line(x1, y1, x2, y2, width, color)          # ClipPath 多边形
c.poly([(x,y),...], color)
c.path(d, color, viewbox="0 0 100 100", fit="FILL")
c.arrow_head(x, y, angle_deg, size, color)
c.dashed_hline / dashed_vline / dashed_line
c.text(x, y, w, h, s, size=20, color="#111827", bold=False,
       align="LEFT|CENTER|RIGHT", font=None, max_lines=None)
c.text_top(...)
c.rich(x, y, w, h, spans, size, ...)
c.add(x, y, w, h, inner_xml)   # 原生 Positioned + 任意 DSL 片段
c.raw(xml)                     # 直接作为 Stack 子节点（如 ClipPath 全画布）
dsl = c.render()               # 完整 <Snapshot> 文本
```

要点：
- `Text` 内容必须用 CDATA（库已处理）；Parser 不解码 HTML 实体。
- 8 位颜色是 CSS `#RRGGBBAA`（透明度在最后两位）。
- `Transform.matrix` 必须是 16 个列主序浮点数，逗号分隔无空格；`alignment="CENTER"` 常用于绕中心旋转。
- `BackdropFilter` 在本服务实例**不产生可见模糊**（已实测），需要背景模糊时用 `ClipRRect + ImageFiltered` 作用于背景副本，文字放在滤镜之外。
- `Container` 的 `alignment="CENTER"` 才能稳定垂直居中文字；`Text` 没有 width/top/align 属性。
- `Positioned` 必须是 `Stack`/`IndexedStack` 的直接子节点。
- 所有主体、文字、图表、图标必须由 DSL 构造；A 类不得使用外部图片素材（题目自带的参考 PNG 只可观察，不可嵌入）。

## 每题标准流程

1. 读该题全部规范与输入，必要时用 Python 计算（数据、路径、几何）。
2. 在 `tmp/<run_id>/<TASK_ID>/build.py` 写生成脚本（路径用 `suite.ROOT` / 环境变量推导，不写死绝对路径）。
   脚本把最终 `.snapshot` 写入 `outputs/<run_id>/<TASK_ID>/`（含轮次子目录），并把同版 DSL 备份到 `tmp/<run_id>/<TASK_ID>/v1/`（迭代则 v2、v3…）。
   同时生成题目要求的附加 JSON/CSV 等交付文件到输出目录。
3. 渲染：`python "$TOOLS/render_all.py" <TASK_ID> --fresh --retries 2`。
   该脚本会为输出目录里每个 `.snapshot` 生成同名 `.png`（服务原始字节），并把请求记录写入 `tmp/<run_id>/<TASK_ID>/requests.jsonl`（轮次子目录各自一份）。
4. **必须用 ViewImage 工具实际打开每张最终 PNG**，检查内容/数据/几何/对齐/可读性/遮挡/裁切/图形效果。
   发现缺陷 → 改 build.py → 用 `BUILD_VERSION=v2` 重跑 → 重新渲染 → 再次打开复查。保留所有版本、失败响应、草稿，不覆盖旧尝试。
5. 用 `suite.iteration(...)` 写 `tmp/<run_id>/<TASK_ID>/iterations.jsonl`（基线 + 每次完整视觉迭代）。B 类另写 `tool-usage.jsonl`。
6. 写 `tmp/<run_id>/<TASK_ID>/finalize.json`（真实观察，不编造），字段参考已完成样例 `tmp/<run_id>/A01/finalize.json`；
   然后执行 `python "$TOOLS/finalize.py" "tmp/<run_id>/<TASK_ID>/finalize.json"`，它会生成
   `outputs/<run_id>/<TASK_ID>/snapshot-usage.md` 与 `task-metrics.json`。
   **`AGENT_NO_STATE=1` 已设置，finalize.py 不会改总进度状态**，请勿自行调用 `suite.task_start/task_done/checkpoint/event`。
7. 如题目有多轮（A21/A22）：先完成 round-01 并归档，再读 `tasks/<目录>/rounds/round-02.md`、`round-03.md` 依次完成，各轮独立子目录 `round-01/` `round-02/` `round-03/`，任务根另写累计 `snapshot-usage.md`、`task-metrics.json`（可用 finalize.py 的 spec 汇总，或在报告里说明）。
8. 最终自检：输出目录内每张指定 PNG 都有同名 `.snapshot`，PNG 文件头为真实 `89 50 4E 47`，附加文件齐全，报告与指标已生成。

## 交付硬性要求

- 所有指定最终 PNG 必须是服务真实响应，禁止用其他绘图工具生成整图后嵌入。
- 尺寸严格按题面；正文/脚注字号按题面要求；数据不得编造或修改输入。
- 多图任务逐图看图；B 类每题至少 10 件**独立完整**作品，不能复用前题成品充数。
- 保留全部过程证据：DSL 版本、请求/响应、错误、脚本、预览，不清理、不覆盖。
- 不要修改 `tasks/`、`templates/`、`outputs/<run_id>/_suite/suite-state.json`、事件/检查点文件。
- 不要创建 `.md` 文档到任务根（除每题输出目录里的 `snapshot-usage.md`）。

## 已完成题的参考实现

`tmp/<run_id>/A01/build.py`、`A02/`、`A03/`、`A04/`、`A05/`、`A06/` 及各自 `finalize.json`，
以及 `outputs/<run_id>/A01..A06/*.png|*.snapshot` 可直接参考布局与写法。

## 返回给主代理的内容

每题一行：`TASK_ID | 最终PNG数 | 附加文件 | 请求成功/失败 | 视觉迭代数 | 已知问题`，
并列出所有最终 PNG 的相对路径与所有附加交付文件路径。若某题真实阻塞，如实说明原因与已完成部分。
