# A19 · 构造可核验的视觉题场 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A19/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A19/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

构造 1600×1600 的 8×8 场景：64 个带编号对象，4 色 × 4 形 × 3 尺寸，16 种颜色×形状组合全覆盖，每色每形都出现 48/64/80 三档，每行至少 3 色 3 形。另做两组 800×800 遮挡场景：可见前景完全相同，遮挡物下方各藏一个不同对象，解码后逐像素比较 0 个不同像素。配 12 道网格题 + 2 道遮挡题，答案全部由几何数据计算。

| 文件 | 说明 |
|---|---|
| [grid-scene.png](grid-scene.png) | 1600×1600 网格场景 |
| [grid-scene.snapshot](grid-scene.snapshot) | 对应 DSL |
| [occlusion.png](occlusion.png) | 800×800 遮挡 A |
| [occlusion.snapshot](occlusion.snapshot) | 对应 DSL |
| [occlusion-alternative.png](occlusion-alternative.png) | 800×800 遮挡 B |
| [occlusion-alternative.snapshot](occlusion-alternative.snapshot) | 对应 DSL |
| [scene-data.json](scene-data.json) | 种子、频数、组合覆盖、逐行统计与几何 |
| [questions.json](questions.json) | 14 道题（不含答案） |
| [answers.json](answers.json) | 答案与方法 |
| [equivalence.json](equivalence.json) | 哈希与像素等价结论 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 1600×1600、8×8、64 个编号 | G01–G64 按行优先编号，ID 在主体外 | 通过 |
| 4 色 4 形 3 尺寸、各 16 个 | blue/orange/green/purple 各 16；circle/square/ring/rounded 各 16 | 通过 |
| 16 种颜色×形状全覆盖 | 16 / 16 | 通过 |
| 每色每形都出现三档尺寸 | per_color / per_shape 均为 [48,64,80] | 通过 |
| 每行 ≥3 色 ≥3 形 | rows[] 逐行记录 | 通过 |
| 圆环外径=尺寸、内径=一半 | ClipPath EVEN_ODD 双层圆，内径 r/2 | 通过 |
| 两遮挡版可见部分完全相同 | 解码 RGBA 逐像素 diff=0，maxch=0 | 通过 |
| 隐藏内容不同且被完全遮住 | A 红圆 110 / B 蓝方 118，均在遮挡框内 75px 余量 | 通过 |
| 12 道网格题 + 2 道遮挡题 | Q01–Q12、O01–O02，覆盖六类题型，5 道两步 | 通过 |
| 至少 1 题答案为无法确定 | O01 遮挡区内的黄色对象数量 → 无法确定 | 通过 |
| 编号 ≥18px | ID 字号 18px | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| grid-scene | 64 个对象、编号清晰、圆环有孔、三档尺寸可辨 | 作为交付 |
| occlusion | 遮挡框不透明，内部无任何形色泄漏 | 作为交付 |
| occlusion-alternative | 与 A 版逐像素一致 | 作为交付 |

## 4. 设计与排版决策

- 先构造满足约束的 (颜色,形状,尺寸) 池，再做行级校验洗牌，最后用断言保证每色/每形三档齐全。
- 遮挡题的核心不是画面，而是「可见像素必须完全一致」：隐藏对象比遮挡框小 150px 以上，且不带阴影或滤镜。
- 题目答案全部由 scene-data.json 的坐标与属性算出，避免出题人自己凭印象写答案。

## 5. DSL 能力与文档应用

- 圆环用 ClipPath + EVEN_ODD 双圆路径实现，外圆 r、内圆 r/2。
- 圆角方用 Container 的 borderRadius = 边长 × 0.22。
- 两版遮挡场景共用同一份可见前景与同一遮挡矩形，只替换被遮住的那一个 Container。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 圆环首版没有孔 | 两个同心圆叠画，内圆没有挖空 | 改用 EVEN_ODD 双圆路径裁剪 |
| 遮挡等价需要可验证 | 文件哈希受压缩影响不可靠 | 解码为 RGBA 数组后逐像素比较，记录 diff 与通道差 |
| 网格属性约束容易顾此失彼 | 随机洗牌可能让某行颜色不足 3 种 | 加 row_ok 校验循环与覆盖断言 |

## 等价性结论

- 两版 PNG 字节数均为 13605 / 13605，文件哈希相同 = True
- 解码 RGBA 后不同像素 0 个，最大通道差 0，判定像素等价 = True
- 题目 14 道（12 网格 + 2 遮挡），其中两步题 5 道
- 请求 3 次（成功 3），看图 3 次，墙钟 411.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A19/grid-scene.png` | 网格场景 |
| `outputs/20261103T152640-suite/A19/occlusion.png` | 遮挡 A |
| `outputs/20261103T152640-suite/A19/occlusion-alternative.png` | 遮挡 B |
| `outputs/20261103T152640-suite/A19/scene-data.json` | 场景数据 |
| `outputs/20261103T152640-suite/A19/questions.json` | 题目 |
| `outputs/20261103T152640-suite/A19/answers.json` | 答案 |
| `outputs/20261103T152640-suite/A19/equivalence.json` | 等价性 |
| `tmp/20261103T152640-suite/A19/geom.json` | 生成期几何 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
