# 继续执行说明（run-20261011-01）

生成时间：本次会话结束时。本文件是**恢复入口**：新的运行从
`outputs/run-20261011-01/_suite/suite-state.json` 与
`tmp/run-20261011-01/_suite/checkpoints/state-000027.json` 继续，
沿用同一个 run_id，**不要新建 run_id，也不要覆盖已完成题的产物**。

## 当前进度

| 项 | 值 |
|---|---|
| 已完成 | 25 / 30（A01–A24、B01） |
| 待完成 | B02、B03、B04、B05、B06 |
| 已交付最终 PNG | 76 张（每张都有同名 `.snapshot`） |
| 最新检查点 | `tmp/run-20261011-01/_suite/checkpoints/state-000027.json` |
| `suite-state.json` 的 `current_task` | `B02` |

## 下一题怎么做

```
python tmp/run-20261011-01/_suite/scripts/suite_state.py start B02
```

然后读 `tasks/B02-one-client-ten-touchpoints/TASK.md`，
按总 `AGENTS.md` 的目录与留痕约定，用
`outputs/run-20261011-01/B02/` 与 `tmp/run-20261011-01/B02/`。

B01 已经把可复用的部分准备好了：

- 共用绘图工具：`tmp/run-20261011-01/_suite/scripts/bsnap.py`
  （`rect` / `txt` / `wrap` / `bullets` / `segment` / `polyline` / `header` /
  `kpi_row` / `footer` / `em_width`）
- 共享字体：Inter / Inter Semi Bold / Inter Medium + Noto Sans CJK SC
  （`tmp/run-20261011-01/_suite/fonts-list.txt`）
- 渲染：`python tmp/run-20261011-01/_suite/scripts/snapshot_render.py --task <ID> --version <v> --dsl <rel> --out <rel png> --log tmp/run-20261011-01/<ID>/requests.jsonl --responses-dir tmp/run-20261011-01/<ID>/responses`
  （**没有** `--timeout` 参数；务必校验返回的 PNG 字节长度，
  偶发 200 + 0 字节要重试）
- 交付模板参考：`tmp/run-20261011-01/B01/deliver_b01.py`（十件 + 作品集文档）
  与 `tmp/run-20261011-01/A24/deliver_a24.py`（三图 + 交叉一致性核验）

## B 类的硬性要求

- 每题**至少 10 件独立完整作品**，不能把前一题的作品重复计数。
- 每件都要在输出根的 `case-01/` … `case-10/` 下交付
  `final.png`、`final.snapshot`、`case.md`。
- 作品集层面还要交 `portfolio.json`、`portfolio.md`、`gallery.md`、
  `snapshot-usage.md`、`task-metrics.json`。
- 总资产政策是 `dsl_primary_with_supporting_assets`：
  主体必须由 DSL 画，**DSL 内不要出现 `<Image>`**（B01 十件全部纯 DSL）。
- 自拟场景与数据时必须写明「自拟、非真实客户作品」，每张图页脚也要写。

## 全套收尾（30/30 之后）

`outputs/run-20261011-01/_suite/` 必须有 `run-config.json` 里
`suite_required_artifacts` 列出的全部文件：

1. `index.md` — 30 题状态、产物入口、实际输出与临时路径
2. `gallery.md` — **逐张**列出所有最终图片（A21/A22 的三个轮次也要全列），
   每张给 Markdown 图片预览 + 原 PNG 链接 + 对应 `.snapshot` 链接，
   链接相对 `_suite/` 目录
3. `snapshot-usage.md` — 全套文档/DSL/工具应用、跨题经验、踩坑与更正、总审查
4. `task-metrics.json` — 全套起止与各题请求/迭代/看图/作品数
5. `suite-state.json` — 每题状态都要有实际证据

然后执行 `python tmp/run-20261011-01/_suite/scripts/suite_state.py artifacts`。

## 两条必须带进后续的更正

见 `tmp/run-20261011-01/_suite/capability-corrections.md`：

1. **`textAlign` 可用，枚举必须大写**（`START`/`CENTER`/`END`/`JUSTIFY`/
   `LEFT`/`RIGHT`）。此前记录「该属性不可用」是错的，原因是只用小写试过。
2. **`ClipPath` 是合法标签**（`path`/`viewBox`/`fit`/`fillRule`/`clipBehavior`）。

## 另外几条已经踩实的行为

- `Transform.matrix` 是**列主序 4×4、16 个**有限 Float，外层带括号、值间无空格；
  写 17 个值直接 400。
- 文字超出 `Text` 盒子会被**静默裁掉**仍返回 200。盒宽要留余量，
  盒高至少 `字号 × 1.40`。多行段落自己排版逐行输出，别依赖服务端换行。
- `Positioned` 必须是 `Stack` 的直接子节点，且不能没有子节点。
- 根 `Container` 不给 `color` 即为真实透明背景。
- 颜色必须是合法的 CSS 写法（`#RGB`/`#RRGGBB`/`#RRGGBBAA` 或函数），
  `"0A"` 这种两位裸值会 400。
- 24px 字的行高约 31px；`bsnap.kpi_row` 已按「标签 → 值 → 副注」顺次排布，
  默认卡高 124，不要为了压高度改回底部对齐。