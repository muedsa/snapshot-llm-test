# case-01 · 卷首 · 0.1 与 30%

## 场景与受众

- **定位**：特辑封面 / 展陈主视觉
- **受众**：站在展板前或翻开杂志跨页的普通读者；不预先知道什么是 pH。
- **观看环境**：1600×1000 横版。可直接投 1920×1080 屏、印 A4 横向跨页、或做 3 m 展板。
- **使用者要完成的事**：在 5 秒内接受「0.1 很小 / 30% 很大」这对矛盾，并知道后面九件会解释它。

## 内容依据

大气 CO2 端点为真实实测（NOAA GML 下载文件）。酸度换算数字出自 NOAA 两个页面。尺标横轴是 pH 7.00–8.20 的等宽对数段，几何真实，不是示意图。

## 视觉意图与手法

- **主要视觉主张**：用极端字号差制造认知张力，再用一把可以量的尺子把张力落地。
- **画面构成**：顶部 40% 是真实 Keeling 曲线剪影；中左是 196px 的「0.1」与同字号的「30%」；右侧一把把 8.20 与 8.07 画在同一把对数尺上的直尺；底部十格阅读顺序条。
- **实际用到的 DSL 能力**：Snapshot/Container/Stack/Positioned/Container/Text；rotate-free 折线（逐段 Transform 4×4 旋转矩形）；LINEAR 渐变背景；CIRCLE 形状；`shape="CIRCLE"` + `border`；Inter Black 作 fontFamily（非 fontStyle）。
- **素材**：无外部素材、无 `<Image>`，主体全部由 DSL 构造（`run-config.json` 的 asset_policy 为 `dsl_primary_with_supporting_assets`，本件未使用任何辅助素材）。

## 实际自检

| 检查项 | 实际值 | 结论 |
|---|---|---|
| 服务响应 | `POST https://open-snapshot.muedsa.com/snapshot` 200，`Content-Type: image/png`，PNG 原始字节落盘无后处理 | 通过 |
| 实际尺寸 | 1600 × 1000（自 `final.png` 读取），PNG 174707 字节 | 通过 |
| DSL 体积 | `final.snapshot` 69188 字节，标签计数 856（远低于 4096 元素上限）| 通过 |
| 渲染请求 | 本件 10 次尝试 / 5 次成功 / 5 次失败 | 见下 |
| `D.warnings()` | 最终一次构建无输出 | 通过 |
| 完成标准 | ①10% 的读者能在 5 秒内说出 0.1 与 30% 的关系；②曲线上两个端点可核对到 315.98 / 427.35；③尺上 8.20 与 8.07 的间距 ≈ 全尺的 1/9；④无文字溢出。 | 逐条已对照实际图核对 |

失败请求（均为 DSL 语法/语义错误，已按错误信息修正后重渲染）：

- `B04-req-017` HTTP 400 — {"code":"PARSE_ERROR","message":"Attr [borderRadius] can not be used with shape CIRCLE at position 45409 near:
- `B04-req-018` HTTP 400 — {"code":"PARSE_ERROR","message":"Attr [border] value is invalid: Failed requirement. at position 45288 near: t
- `B04-req-019` HTTP 400 — {"code":"PARSE_ERROR","message":"Attr [fontStyle] value is invalid: Unexpected font style BLACK at position 47
- `B04-req-020` HTTP 400 — {"code":"PARSE_ERROR","message":"Attr [fontStyle] value is invalid: Unexpected font style BLACK at position 47
- `B04-req-021` HTTP 400 — {"code":"PARSE_ERROR","message":"Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA at position 4824

## 实际看图与迭代记录

v1 曲线渲染成断续虚线且面积为空（根因见 snapshot-usage.md）；v2 曲线正确但 8.20/8.07 标签打架、右侧面板首行被压、页脚被截断；v3 排版正确但中下部大片空白；v4 补阅读顺序条后定稿。

- 成功渲染请求 ID：`B04-req-022`、`B04-req-023`、`B04-req-024`、`B04-req-025`、`B04-req-054`
- 最终一次渲染：`B04-req-054`（服务端 requestId 同值），耗时 3809 ms
- 本件 PNG 与 DSL 逐件实际用 read 工具打开看过，最终版另做了局部放大核对（放大图见 `tmp/20261004-182918/B04/crops/`）。

## 遗留 / 不足

「ppm · 年均」单位标签放在轴下方而非曲线旁；这一点在本图里仍然偏弱。
