# 子任务执行简报（供并行子代理阅读）

本文件只供执行本套任务的子代理阅读，不属于题库输入，不修改 `tasks/`。

## 0. 你的身份与目标

你在 `D:\workspaces\deepseek-v4.1-flash-max-in-dsh`（总任务根目录）里，代替主代理**真实完成**分配给你的
若干道题。**必须真实调用 open-snapshot 服务作图，并用 `read_image` 实际看图迭代**，不能只检查 XML 或
HTTP 200。所有产物落到统一目录，不要新建 run_id。

## 1. 固定路径与 ID

- 总根：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh`
- run_id：`20261003-114508-flashmax`
- 输出目录：`outputs/20261003-114508-flashmax/<TASK>/`（TASK 例如 `A09`）
- 临时目录：`tmp/20261003-114508-flashmax/<TASK>/`
- 题目输入：`tasks/<目录名>/`（如 `tasks/A09-transform-atlas/`）；先读该目录的 `TASK.md`、`AGENTS.md`、
  `task.json` 与 `inputs/`。**不要改写 `tasks/` 下任何文件。**
- 已完成任务的样板（强烈建议先看 A04/A07/A08 的产物与报告，照此标准交付）：
  `outputs/20261003-114508-flashmax/A08/`（`wayfinding.png`、`wayfinding.snapshot`、`paths.json`、
  `snapshot-usage.md`、`task-metrics.json`）。

## 2. 服务与工具（已实测，直接复用）

- 渲染接口：`POST https://open-snapshot.muedsa.com/snapshot`
  - 请求体 = **UTF-8 纯文本的 Snapshot DSL**，`Content-Type: text/plain; charset=utf-8`
  - 成功 = **PNG 原始字节**（HTTP 200）；失败 = JSON 错误体（HTTP 400 等），**必须用 `curl.exe --data-binary`
    才能读到错误正文**（`Invoke-WebRequest` 会丢掉错误体）
  - 相同 DSL 返回相同字节；`x-ratelimit-limit: 120`；目前未遇到 429
- 现成渲染脚本：`tmp/20261003-114508-flashmax/_suite/shared/render.ps1`
  - `. "tmp/20261003-114508-flashmax/_suite/shared/render.ps1"` 之后可用：
    - `Invoke-Snapshot -DslPath <dsl> -OutPath <png> -LogPath <requests.jsonl> -ReqPrefix "<TASK>-REQ" -Task "<TASK>" -Phase "<phase>"`
    - `Invoke-SnapshotText -DslText <字符串> ...`、`Get-SnapshotFonts`
  - 它会写 `requests.jsonl`（含 request_id/时间/耗时/状态/路径），并在失败时写 `<png>.failed.txt`
- 每题的请求 ID 前缀用 `<TASK>-REQ`，例如 `A09-REQ`；脚本用
  `tmp/.../_suite/shared/reqseq-<TASK>-REQ.txt` 存续号，请勿与其他题冲突。
- 记账工具：`tmp/20261003-114508-flashmax/_suite/shared/suite_common.py`
  （`append_jsonl_nobom`、`read_jsonl`、`count_requests`、`count_iterations`、`build_metrics`、
   `task_out`、`task_tmp`、`write_json`）；`suite_state.py`
  （`python suite_state.py start <TASK> --temp-dir ... --output-dir ...` 与
   `... done <TASK> --artifact "a,b,c" --evidence "..." --issue "..."`）。
- 写文件必须无 BOM：`[System.IO.File]::WriteAllText($p, $c, (New-Object System.Text.UTF8Encoding($false)))`。
  PowerShell 的 `Set-Content` 会带 BOM，导致服务报 `Not Support RAWTEXT: ` 于位置 0。
- 每次 `pwsh` 调用是全新进程，变量不保留。
- **不要用 Python 的 `assert` 输出里带 `\n`**，也不要用 PowerShell 字符串替换去拼多行 Python 代码——多次
  踩坑；要改代码请用编辑工具直接改文件。

## 3. Snapshot DSL 硬性知识（已实测，别再重新踩）

- 根标签 `<Snapshot background="#RRGGBBAA" type="png">`，**只允许一个根子节点**（通常是一个
  `Container` 包住 `Stack`）。
- 定位用 `<Positioned left=".." top="..">` 包住 `Container`；`Stack alignment="TOP_LEFT" fit="EXPAND"`。
- **不要在 `Column` 里放 `Positioned`**（会报 `renderBox.parentData must be StackParentData`）；
  `Column mainAxisSize="MIN"` 包定位层也会炸。用扁平的单层 `Stack` + 绝对坐标最稳。
- 颜色：`#RGB`、`#RRGGBB`、`#RRGGBBAA` 都可；**不要用 10 位**。
- `borderRadius` 只接受**单个数字**；四角不同要分别写
  `borderRadiusTopLeft/TopRight/BottomLeft/BottomRight`；`borderRadius="5 5 0 0"` 会报格式错。
- `padding`/`border` 等元组属性要写 `padding="(24,32)"`；`border="1 SOLID #CBD5E1FF"`。
- `Transform matrix` 是**列主序 4×4**，共 16 个数字，写法 `"(m00,m01,m10,m11,m20,m21,m30,m31,tx,ty,0,1)"`
  实际可用形式：`(a,b,c,d,e,f,g,h,i,j,k,l,tx,ty,0,1)`，其中旋转/缩放放在前 4 位（`m00 m01 m10 m11`），
  平移放第 13、14 位。**只有 `matrix` 属性，没有 `rotate` 属性。**
  画任意方向线段的最省事做法：先算长度 L 与角度，再让一个 `width=L height=th` 的圆角 `Container`
  在局部居中后旋转并平移到线段中点：
  ```
  m11,m12 = cos,sin ; m21,m22 = -sin,cos
  tx = mx - m11*(L/2) - m21*(th/2)
  ty = my - m12*(L/2) - m22*(th/2)
  matrix = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx},{ty},0,1)"  ← 这只对不旋转有效
  ```
  **注意：这条“单位矩阵 + 平移”写法无法旋转。** 要旋转必须把旋转放进前四位：
  `matrix=f"({m11},{m12},0,0,{m21},{m22},0,0,0,0,1,0,{tx},{ty},0,1)"`  —— A07/A08 用它画出了
  45° 线段与箭头三角，已验证可用。
- **文字宽度**：`<Text>` 若被放进带 `width` 的 `Container`，宽度不够会**换行**，看起来像压字或溢出。
  实测宽度：CJK ≈ 1.00×字号，等宽数字/字母 ≈ 0.60×字号（`Noto Sans Mono CJK SC`），拉丁 ≈ 0.55×字号；
  行高 ≈ 1.30×字号。排任何一行文字前先算宽度。
- `Text` 不能写在 `<Positioned>` 与 `Container` 之外的地方；用
  `<Positioned left=.. top=..><Text fontSize=.. color=.. fontFamily=.. fontStyle="BOLD|NORMAL">…</Text></Positioned>`，
  需要对齐时包一层 `<Container width=.. alignment="CENTER_RIGHT">`。
- 对齐常量语义：`CENTER` = 底部居中 `(0.5,1)`；`CENTER_LEFT` = 真正的左中。想“水平居中”请用
  `CENTER_LEFT` + `width` 容器，或自己算坐标。
- **`BackdropFilter` 会模糊整幅已合成画面**（不是只模糊自己子树），sigma 越大越糊；本构建实测
  sigma=1 是唯一不糊字的档位。`ImageFiltered` 只模糊自己子树（会把里面的字一起糊掉）。
- **解析器不解码 XML 实体**（实测：写 `&amp;`，画面上就是五个字符 `&amp;`）。所以**永远不要转义**。
  正确做法（用真实 200 响应验证，见 `tmp/<run>/_suite/shared/cdata-probe.png`）：
  - 普通文本节点里 `&` 与 `>` **可以原样写**；
  - 裸的 `<` 会直接 `400 TAG_OPEN`，必须写成 `<![CDATA[含 < 的文字]]>`；
  - 需要保留**连续空格**（代码清单、对列表格）时用
    `<Text><Raw><![CDATA[文字]]></Raw></Text>`；`Raw` 只能放在 `Text` 里，直接放在 `Positioned` 下会 400。
  共享 `dslkit.text()` 已经自动处理：默认按需加 CDATA，`raw=True` 时用 `Raw` 包裹。
- **单个文档上限 4096 个元素**，超过会返回
  `400 RENDER_ERROR: Document contains more than 4096 elements`。元素按**标签**计数，
  `<Transform><Container/></Transform>` 算 2 个，所以按 DSL 行数估算会严重低估。
  用 `len(re.findall(r"<[A-Za-z]", dsl))` 自查并控制在 ~3900 以内。
  最容易爆的是“用很多短线段拼圆环/圆弧”（约 6px 弧长消耗 2 个元素）——圆环可以用两个同心实心圆盘近似。
- **对齐常量**（用真实响应 + Pillow 实测更正）：`CENTER` 就是**盒子的两轴中心**，不是“底部居中”。
  60px 高的盒子里 20px 文字：`CENTER` 墨迹落在 162..176（盒子 140..200），
  `BOTTOM_CENTER` 落在 260..275（盒子 220..280，距底 5px）。早期笔记里写错的“CENTER = (0.5,1)”已作废。
- **文字宽度常量已重新标定**（另一路子任务用两次真实渲染探针测出，比早期估算准得多）：
  `Noto Sans Mono CJK SC` = **恰好 0.5000 em/字符**（不是 0.60！）；
  `Noto Sans CJK SC` = 汉字/假名 0.9952、大写 0.6106、小写 0.5769、数字 0.5385、
  空格 0.5641、句点 0.2692。用旧的 0.60 会让一列右对齐金额产生 19px 抖动，换成标定值后是 1px。
  共享 `dslkit.text_width()` 已内置这张表。
- **`border` 必须是 `"宽度 样式 颜色"` 三段**，例如 `border="1 SOLID #CBD5E1FF"`；
  写成 `border="#RRGGBB"` 会 400。
- **颜色必须是 3/6/8 位十六进制**；10 位会被拒。要做半透明就取 `col[:7] + alpha`，不要 `col + alpha`。
- **`Inter` 的粗体比拉丁估算宽约 18%**，右对齐标签容易被它悄悄挤到换行；拉丁文本用 Inter 时留足余量。
- 已验证可用的额外能力：渐变（`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors/Stops`）、
  `shape="CIRCLE"`、`ClipOval`/`ClipRRect`、`Opacity`、自定义 `boxShadow` 字符串、
  `borderTop` 覆盖、`letterSpacing`，以及**直接在 `Container` 上写 `transform="(matrix)"`**（不必套 `Transform`）。
  旋转矩阵形式 `(cos,sin,0,0,-sin,cos,0,0,0,0,1,0,tx,ty,0,1)` 已验证。
  **`ClipRRect` 确实能把 `BackdropFilter` 限制在圆角卡片内**（σ 可以到 6，外面依然锐利），
  这修正了早期“必须 σ≤1”的说法；`MULTIPLY` 也留在子树绘制范围内。
- 共享工具箱 `tmp/<run>/_suite/shared/dslkit.py` 已按上述结论修好：`text()` 默认不转义并按需 CDATA；
  `text(raw=True)` 保留空格；`finish()` 在超过 3900 元素时直接报错；`element_count(dsl)`、
  `Doc.stats()`、标定过的 `text_width()` 可用。
- 可用字体（`GET /fonts` 实测）：`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Noto Serif CJK SC`、
  `Noto Serif CJK JP`、`Inter`、`Inter Tight`、`DejaVu Sans`、`DejaVu Sans Mono`、`DejaVu Serif`、
  `Noto Color Emoji`。不要臆造其他字体名。
- **绘制顺序即图层顺序**：后画的盖住先画的。A08 就因为“墙块画在路线之后”导致路线被整段盖住，
  看起来是断开的横杠——排复杂图时务必先画背景、再画线条、最后画文字。

## 4. 交付要求（每题都要）

输出目录 `outputs/<run_id>/<TASK>/` 里必须有：

1. TASK.md「指定交付」表格里列出的**全部 PNG（必须真实 200 响应得到的原始字节，不后处理）**；
2. 每个 PNG 的**同名完整 `.snapshot`**（真实发出去的 DSL，UTF-8 无 BOM）；
3. TASK.md 要求的额外 JSON/CSV 等（如 `paths.json`、`geometry-audit.json`、`task-metrics.json`）；
4. `snapshot-usage.md`：完成状态、逐图自检、真实文档应用、设计选择、实际问题与修复、未解决事项、
   真实消耗（请求数/成功失败/DSL 版本/看图次数）；
5. `task-metrics.json`：用 `suite_common.build_metrics(...)` 生成，包含起止时间（带 `+08:00`）、
   wall clock、首次可用图耗时、请求统计、DSL 版本数、看图次数、迭代分类计数；
   **token / 图像输入 / 费用一律记 `null`**（平台不提供），不可测排队等待记 `null`，确认未发生才记 0。

临时目录 `tmp/<run_id>/<TASK>/` 里保留：所有 DSL 版本（`<名字>.v1.snapshot`、`v2`…）、每次渲染的 PNG、
失败响应、生成脚本、中间数据、`requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`。**不清理、不覆盖旧版本。**

## 5. 质量硬标准

- 最终图**必须真的用 `read_image` 打开逐项核对**；发现问题就改 DSL、重渲染、再看，直到通过。
  一次就合格就不必制造修改。
- 文字尺寸要求（每题 TASK.md 会写具体数字，如“正文≥22”“标签≥20”“格号≥16”）**必须逐项满足**，
  并在 `snapshot-usage.md` 的自检表里写出你**实际用的字号**。
- 不要出现：文字被裁切、文字互相压字、内容超出画布、图片与 `.snapshot` 不配套、把错误 JSON 存成 PNG。
- 所有数字（步数、距离、比例、统计量）都要由脚本真实算出并落进额外 JSON；不要手编。
- 视觉上用同一套设计语言：深色页头（`#0F172AFF`）、浅底（`#F1F5F9FF` 或 `#EEF2F7FF`）、白卡片 +
  `#E2E8F0` 描边 + 圆角、强调色 `#0E9F8FFF` / `#1D4ED8FF` / `#D92D20FF` / `#D97706FF`。

## 6. 完成后

1. 用 `suite_state.py done <TASK> --artifact "..." --evidence "..." --issue "..."` 标记进度；
2. 用 `reqseq-<TASK>-REQ.txt` 记录本題最大请求序号（例如 `echo 12 > ...`，无换行）；
3. 向我（主代理）汇报：**任务号、状态、输出/临时目录、最终文件清单、真实请求数与成功/失败数、
   DSL 版本数、看图次数、逐项需求满足情况、关键视觉修改、未解决事项**。汇报要短，不要贴大段代码。
