# A21 双尺寸发布物 Snapshot DSL 使用记录（run-20261013-174209）

- 任务：`tasks/A21-brand-launch-kit/`，三轮（round-01 / round-02 / round-03），
  每轮两件成品：竖版 `1080x1350` 与横版 `1440x810`。
- 渲染服务：Snapshot DSL（真实 HTTP 渲染）。全部请求记录见
  `tmp/run-20261013-174209/A21/requests.jsonl`：共 **32** 次渲染请求，
  **29** 次成功、**3** 次失败；失败均为读取超时
  （`TimeoutError: The read operation timed out`），重试后均成功，
  成品一律以该尺寸**最后一次成功渲染**为准。
- 累计渲染耗时 309.283s（服务端 `elapsed_s` 求和，含失败等待）。

## 通用 DSL 结构

- 画布：竖版 `1080x1350`、横版 `1440x810`；根结构
  `Snapshot type="png" background="#..."` -> `Container` 定尺 ->
  `Stack fit="EXPAND" clipBehavior="NONE"`，其余全部 `Positioned` 绝对定位。
  根只能有一个子节点；不给显式尺寸会报 `Layout size is infinite`。
- 主题：round-01 / round-02 深色（页面 `#0B1020`、卡片 `#151B2E`）；
  round-03 浅色（页面 `#F6F7FB`、卡片 `#FFFFFF`、卡片边线 `#D7DCEA`）。
  令牌见各轮 `design-tokens.json`。
- 半透明色用 8 位十六进制 `#RRGGBBAA`（alpha 在末两位）。
- 斜光束用 `Transform matrix="(列主序 4x4)"`，且 **Transform 必须是 Positioned
  的直接子节点**；`alignment="CENTER"` 必须写在 Transform 上
  （写在 Positioned 上会绕框左上角旋转，整条光束偏移约半个长度）。
- 徽标 5 构件：C1 外环（`CIRCLE` + `border`）、C2 中盘（`CIRCLE`，α=0.50）、
  C3 内核（`CIRCLE`，α=0.95）、C4 层纹三条（圆角矩形，长度递减、等距）、
  C5 斜光束（旋转薄矩，α=0.50）。
- 字体：中文 `Noto Sans CJK SC`；拉丁 `Inter` 系列
  （字重用 `Inter Black` / `Inter Semi Bold` 字体族名切换）。
- 元信息卡高按行数计算：`20 + Σ(size*1.5 + 14) - 14 + 20`。
  竖版 154（R1）→196（R2+）；横版 164（R1）→200（R2+）。

## 分轮渲染记录

| 轮次 | 成品 | 请求数 | 成功 | 失败 | 主题 | 主标题 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| round-01 | portrait / wide | 12 | 12 | 0 | dark | 88px 1 行 | 首版 + 光束定位/字标净空共 4 轮迭代 |
| round-02 | portrait / wide | 9 | 7 | 2 | dark | 56px 3 行 | 26 字长标题 + 免费参加 pill + 赞助方；后修横版卡高 |
| round-03 | portrait / wide | 10 | 9 | 1 | light | 56px 3 行 | 主题反转 + 英语短句 + 对比度审计（含 2 次去文字辅助渲染 ×2 批） |

各轮逐次尝试（含失败重试的 request_id、耗时、错误）见各轮 `snapshot-usage.md`。

## 第三轮对比度审计用法（重点）

- 普通文字与实际合成背景的对比度阈值 4.5:1。
- **不按名义背景色估算**：pill / 卡片 / 分隔线下的文字，其真实背景由
  去文字辅助渲染图（`tmp/run-20261013-174209/A21/r3-portrait-notext.png`、
  `r3-wide-notext.png`）在同像素处取色得到。
- 文字本体取终版图中与名义色相差 ≤12 的核心字形像素（排除抗锯齿边缘），
  按 WCAG 相对亮度公式逐像素计算，**取全段最小值**作为该段文字的最差位置对比度。
- 结果：两图各 12 段文字、共 24 段全部通过，最低 **7.382:1**，最高 17.853:1。
  明细见 `round-03/contrast-audit.json`（含公式、辅助渲染证据与 request_id、
  每段最差位置样本、视觉回归说明）。

## 实际看图与迭代

- 迭代记录：`tmp/run-20261013-174209/A21/iterations.jsonl`（it01–it08）。
- 关键实测结论：
  1. 光束整体偏移 -> calibration 渲染证明 `Transform` 绕 `Positioned` 框左上角旋转，
     `alignment="CENTER"` 必须写在 `Transform` 上（it02 -> it03）。
  2. 字标字形墨迹超出声明文字盒约 1px -> 页眉按徽标真实包围盒定位、字标下移 2px、
     净空带改按内容边界外扩 10px 口径核验（it03）。
  3. 半透明元素落盘色 = 名义色按 alpha 合成到下层实际背景，按名义色精确比色会失败
     （it06，对比度审计改用辅助渲染取真实背景）。
  4. 横版元信息卡卡高写死导致第三行文字探出卡片底边 -> 卡高改按行数计算，
     并新增复测第 9 项 `card_text_clearance`（it07 -> it08）。
- 成图与分区放大均逐张实际查看：整图 + 页眉（徽标/字标/pill）+ 元信息卡 +
  英雄徽标 + 右栏网址区。
