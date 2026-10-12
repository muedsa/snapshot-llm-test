# A15 · 复杂界面视觉复刻 — Snapshot 使用说明

- 任务：`tasks/A15-reference-reconstruction/`（TASK.md / AGENTS.md / task.json 已完整阅读）
- run_id：`20261008T1615Z-run01`
- 输出目录：`outputs/20261008T1615Z-run01/A15/`
- 临时目录：`tmp/20261008T1615Z-run01/A15/`
- 状态：completed（1/1 张为服务真实响应；34 个锚点全部落在 ±8px）

## 交付清单

| 文件 | 字节 | 渲染请求 ID | server-timing |
|---|---|---|---|
| `reconstructed.png` + `reconstructed.snapshot` | 见目录 | `A15-v09-final-20261009T022039Z` | `render;dur=281.7, total;dur=293.4` |
| `reconstruction-audit.json` | — | 34 锚点 + 8 平色 + 分区像素统计 + 图表/表格推导 | — |
| `comparison.md` | — | 三尺度观察 + 可测误差 + 残余差异 | — |

`reconstructed.snapshot` 与发送体逐字节一致（`tmp/…/A15/preview/requests/A15-v09-final-*.body.txt`
去掉 `POST` 行后的 DSL 本体）。九个草稿版本（v01–v08）的 PNG、请求体、响应头与原始响应字节都留在
`tmp/20261008T1615Z-run01/A15/preview/` 与 `outputs/20261008T1615Z-run01/A15/requests/`，未清理。

## 实际用到的文档与知识

来源均为本次运行真实取得、缓存在 `tmp/20261008T1615Z-run01/_suite/docs/` 的文件：

| 知识 | 来源 | 在本题的应用 |
|---|---|---|
| `<Positioned>` 必须是 `<Stack>` 直接子节点、`alignment="TOP_LEFT"`、`clipBehavior="NONE"` | `ai-guide.md`（`shared-doc-001`） | 生成的 20KB DSL 全程只用一层 Stack + Positioned，无嵌套违规 |
| Container 的 `borderRadius` 必须 ≥ 边框宽度，否则 HTTP 500 | `container.html`（`shared-doc-006`） | 1px SOLID 发丝边 + 12px 圆角；本题未触发过 500 |
| `boxShadow="X Y BLUR SPREAD COLOR TYPE"` 语法 | `painting.html`（`shared-doc-009`） | 先用于 v01 卡片阴影，量测发现参考无阴影后整体撤掉 |
| 文本 `fontFamily` / `fontStyle` / `letterSpacing` / `maxLines` / 对齐 | `text.html`（`shared-textdoc`） | `Inter + fontStyle="BOLD"`、字距 0.8–1.6、标题 `maxLines=1` |
| 服务实际字体清单 | `fonts.txt`（真实查询响应缓存） | 只选用清单里存在的 `Inter`、`Inter Medium`、`Inter Semi Bold`、`Noto Sans CJK SC` |
| `clipBehavior="CLIP"` 会 400 | 前一题的失败留痕 | 本题未再尝试该写法 |

## DSL 能力覆盖

- **布局**：`Stack` + 绝对 `Positioned`，卡片内文字用固定基线盒（墨迹框测量驱动 y 偏移）。
- **绘制**：`Container`（fill / borderRadius / border / boxShadow）、`circle`（导航点、动态点）、
  1px 实线（网格线、行分隔）。
- **文本**：三级字重（reg / Medium / Semi Bold）+ `Inter+BOLD` 组合，中英混排靠
  `Inter,Noto Sans CJK SC` 回退。
- **图表**：不是把数字贴上去，而是从测得的坐标轴反推：零线 y=549、1.2px/单位、柱宽 54、
  间距 101、刻度 0/30/60/90/120 ↔ y=549/513/477/441/405，六柱 54/72/63/90/81/108。
- **表格**：表头带 `#F3F6FB` r8 + 11px 字距标签；三行顺序 Atlas → Pulse → Orbit；状态编码
  `#E7EFFF`/`#245CE4`（In progress）、`#FFF3D7`/`#9D6613`（Review）、`#DCF5EC`/`#168267`（Done）。

## 跨题经验与踩坑

1. **量测必须同码双跑**：`measure_a15.py` 对参考图和重建图跑完全相同的阈值与窗口，误差数字才有意义；
   只给一侧调窗口会造出假达标（v03 扩锚点后 max 从 6 跳到 51 就是这种情况的暴露）。
2. **`doc.line()` 不适合发丝网格线**：Transform 旋转的 1px 矩形会横跨两个亚像素行，在整数 y 上
   留下 #F1F5F9 这类“差 2”的过渡行，既影响观感也让投影分割断行。发丝线一律用 `doc.rect(x, int(y), w, 1, c)`。
3. **阴影会污染一切自动量测**：投影让卡片的墨迹框向外扩，锚点表和分割都失真；先确认参考是否
   真的带阴影（本题没有），再决定要不要 `boxShadow`。
4. **数值检查看不出字重**：v03 起宽度/位置就全绿了，但 `Inter Semi Bold` 的笔画明显比参考细；
   只有 2× 放大裁条并排才暴露。字宽达标 ≠ 字体匹配。
5. **文字墨迹框受降部影响**：含 descender 的字符串（`Export report`）其墨迹中心低于盒子几何中心，
   需要按墨迹框而不是盒框做垂直校准（这里 −6px）。
6. **同字节重发是缓存命中，不是新渲染**：两次补丁脚本在 `write_text` 前 assert 失败，DSL 未变，
   随后的请求返回 `cache;desc=hit`（16.7ms）。这条如实留在 `requests.jsonl` 与迭代日志里，
   不计作一次视觉迭代，也不把它的响应当新版本证据。
7. **参考图只做观察**：`inputs/reference.png` 没有被嵌入 DSL，也没有裁块当素材；`content.json`
   仅用于消除文字歧义。整份 DSL 只有 Container / Text / 圆形几何，`reconstruction-audit.json`
   的 `method.no_reference_pixels_used` 记录了这一点。

## 遗留事项

- 参考字体身份不可确定，最终是“宽度与笔画都对得上”的近似，仍存 1–2px 墨迹宽度差。
- 侧栏工作区小卡圆角、卡片圆角的真实半径无法从单行 AA 像素测得，取近似值。
- 详见 `comparison.md` 第 4 节。
