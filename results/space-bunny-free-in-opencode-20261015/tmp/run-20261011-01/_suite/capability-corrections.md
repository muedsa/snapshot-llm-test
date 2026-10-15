# 能力更正记录（run-20261011-01）

本文件记录**在本次全套执行过程中被推翻的早期结论**。
推翻必须有可复跑的证据，证据文件一并列出。

path_base = suite_root

---

## 更正 1 · `textAlign` 可用，枚举必须大写

| | |
|---|---|
| 此前记录 | `textAlign` 任何取值都返回 400，该属性在本服务不可用；所有对齐改用实测字宽系数计算坐标 |
| 更正后 | `textAlign` 是合法属性，合法取值为**大写**枚举 `START`、`CENTER`、`END`、`JUSTIFY`，另有 `LEFT`、`RIGHT`；默认值 `START` |
| 出错原因 | 只用小写取值（`left`/`right`/`center`）试探，得到 400 后直接下了「属性不可用」的结论，没有回头核对官方参考的属性表 |
| 证据 | `tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json`（10 个候选取值逐个渲染，6 个大写值返回 200，4 个小写值返回 `Attr [textAlign] value is invalid`） |
| 复跑方式 | `python tmp/run-20261011-01/_suite/scripts/probe_textalign.py` |
| 官方依据 | https://snapshot.muedsa.com/reference/parser-tags/ 的 `Text` 属性表列出 `textAlign`，默认 `START` / `LTR` |
| 影响到的已交付产物 | A14、A22 的报告文字已更正；两题的图本身仍正确（数字列经整屏查看对齐无误），改用 `textAlign="END"` 可由段落排版保证对齐，属可改进项 |

## 更正 2 · `ClipPath` 是合法标签

| | |
|---|---|
| 此前记录 | `ClipPath` 不是有效的 DSL 标签 |
| 更正后 | `ClipPath` 是解析器注册的 39 个标签之一，接受 SVG `d` 属性语法，以及 `viewBox`、`fit`、`fillRule`、`clipBehavior`；另有 `ClipRect`/`ClipOval`/`ClipRRect` |
| 出错原因 | 与更正 1 同源——早期凭印象记下的标签清单没有逐条对照官方总表 |
| 证据 | 同一份探针里的 `clippath-basic`（`path="M0 0 H100 V100 H0 Z"` + `viewBox` + `fit="CONTAIN"`）返回 `ok: true` |
| 官方依据 | https://snapshot.muedsa.com/reference/parser-tags/ 的标签总表与 `ClipPath` 属性表 |
| 影响到的已交付产物 | A23 的 `limitations.md` 已按更正后的结论写；A23 本身未用到路径，12 个单元一律用 `Container` + `borderRadius` |

---

## 仍然成立的服务行为（勿再重复踩）

| 行为 | 说明 |
|---|---|
| 输出格式只有三种 | `Snapshot` 的 `type` 只有 `png` / `jpg` / `webp`，没有 SVG、没有 CMYK、没有动图 |
| 一次请求一张图 | 没有多帧、动画、时间轴参数 |
| `Positioned` 的约束 | 必须是 `Stack` 或 `IndexedStack` 的直接子节点；无子节点会返回 400 |
| `Transform.matrix` | 列主序 4×4，必须 16 个有限 Float，外层带括号且值之间不能有空格 |
| 透明背景 | 根 `Container` 不给 `color`（或 `Snapshot` 用默认的 `background="transparent"`）即为真实透明 |
| 文字溢出会被静默裁剪 | 盒子太窄时服务端仍返回 200，但字符被切掉；字宽余量要给足 |
| 偶发 200 + 0 字节 | 渲染循环必须校验 PNG 字节长度并重试，不能只看状态码 |
| `borderRadius` 必须大于 `border` 宽度 | 否则 `BoxDecoration` 构造失败 |