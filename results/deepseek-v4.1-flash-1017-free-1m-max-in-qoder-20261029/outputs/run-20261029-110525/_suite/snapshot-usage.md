# 全套 Snapshot 使用说明

run `run-20261029-110525` · 30 题 · 124 张最终 PNG。

## 实际使用

- 服务：`https://open-snapshot.muedsa.com/snapshot`；请求体 UTF-8 文本 DSL，成功响应原始 PNG，失败为 JSON（code/message/requestId/diagnostic）。
- 共享文档 11 份，实际 HTTP 成功 11 次，耗时约 29.1 秒；缓存与哈希见 `tmp/run-20261029-110525/_suite/docs/`。
- 渲染器：`tmp/run-20261029-110525/_suite/scripts/render.js`（Node fetch、3 次重试、PNG IEND 校验、原始字节落盘、requests.jsonl 追加）。早期 Python/curl 在本机 TLS 下出现截断，已弃用。
- 像素/尺寸核验：Pillow 读取 PNG；几何/像素审计见各题 `*-audit.json`、`geometry-audit.json` 等。
- 生成脚本按自身位置定位 suite root；DSL、数据、日志与报告使用相对路径或目录环境变量。

## DSL 经验

- 解析器不解码 HTML 实体：文本中的 `<`、`&` 用 CDATA；不要依赖 `html.escape` 后的显示。
- 一个 `Positioned` 只能有一个子节点；多个元素先用 `Column`/`Row`/`Stack` 包好。
- 颜色是 `#RRGGBBAA`，alpha 在最后；`color`、`border`、`gradient` 合并到 BoxDecoration。
- `textAlign` 取值必须大写（LEFT/RIGHT/CENTER/JUSTIFY/START/END）。
- `Transform` 是 16 个列主序浮点数；`origin` 指定旋转中心；矩阵不改变布局尺寸。
- `ImageFiltered` 模糊子树，`BackdropFilter` 读取已绘制背景；两者都需要裁剪限定范围。
- 只由 Positioned 组成的 Stack 在透明描边/裁剪场景下可能不如实色格或实线下划线可靠；以实际 PNG 为准。
- 根画布尺寸来自根 Widget 的布局结果；坐标原点会因外层 Container 的 padding/定位而改变，卡片内元素用局部坐标，覆盖层放到页级 Stack。

## 跨题教训

- A 轨的复杂数据图必须先算后画：把锚点/比例写入计算文件，再用像素或坐标审计验证文字、柱、点没有压线。
- B 轨的开放作品要先写计划与完成标准，再渲染；看图后按实际缺陷修订，保留失败响应与旧版本。
- B05 产品组暴露了跨屏一致性风险：库存、时间线、金额、状态栏时间必须来自同一份 shared-data，修改一处要重渲染所有受影响页面。
- B06 信息重构组暴露了“图例顺序、表头列对齐、区间高亮、气泡标签”四类看似细小但会直接误导的内容错误。
- 失败响应是最有价值的调试材料：position/attributeName 能直接定位标签问题；不要删除 http400 原文。

## 根 .gitignore

- 路径：`.gitignore`（总任务根）。
- 规则：`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`。
- 未排除 `tmp/`、`outputs/`、`*.log`、图片/DSL/JSON；失败响应、草稿、日志、检查点均保留。已确认文件存在，且产物与过程证据未被忽略。

## 失败与重试

- 全卷快照请求 392 次，成功 309，失败 83，重试 45 次；失败原文均保留在各题临时目录或 case 目录。
- 常见失败：实体未解码、Positioned 多子节点、textAlign 小写、坐标越界/被裁剪、渐变/滤镜参数错误、TLS 截断。每次修复都重新渲染并实际看图。

## A21 / A22 三轮

- 三轮需求文件在运行前已可读；记录衡量预置需求的连续执行与回归，不声称隐藏反馈盲测。
- A21 三個 round 全部保留在 `outputs/run-20261029-110525/A21/round-01..03/`，每轮竖版/宽版各一张；路由与对比记录见题级 `rounds/` 与指标。
- A22 三個 round 的仪表盘全部保留；Round 2 包含负利润轴的修正，Round 3 为最终版。

## B 轨作品

- B01 十个真实世界展示、B02 一个客户十个触点、B03 DSL 创作前沿、B04 十页开发者图鉴、B05 余味 AFTERTASTE 十屏产品、B06 十件日常信息重构。
- 每题的 `portfolio.json` 逐件映射受众、场景、依据、DSL 能力、完成标准与实际检查证据；`gallery.md` 相对本题输出根可离线浏览。

## 最终审查

- 30 题全部 completed；最终 PNG 124 张，全部有同名 `.snapshot`；B 轨 60 件全部在各自 gallery 与总 gallery 中出现。
- 逐题报告、指标、日志存在；A21/A22 轮次齐全；B05/B06 附加文档齐全。
- 总 gallery 使用相对链接，复制整个 `outputs/run-20261029-110525/` 后仍可浏览；已逐条检查 gallery/index 链接，372 + 100 条本地链接无失效。

## 剩余事项

- 未做真实用户测试、无障碍审计、打印/硬件验证；B05/B06 的演示数据、碳排/营养/法律/医疗/分类规则均非真实依据。
- 服务无 Noto Serif CJK SC；全套统一使用 Noto Sans CJK SC。
- 个别题目（如 A01、B03）早期失败较多，已在题级 usage 中如实记录，未删除失败响应。