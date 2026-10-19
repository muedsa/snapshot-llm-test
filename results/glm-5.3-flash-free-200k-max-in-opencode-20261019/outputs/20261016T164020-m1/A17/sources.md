# A17 · sources.md —— 关键结论与真实阅读来源

> 路径基准：`docs/*` 与 `outputs/*` 相对总任务根。缓存文件为本 run 前期/本任务实取得，任务内引用不重复计为新请求。
> 标注 ★ 者为本任务新增实发请求（另记录于 `examples.json.verification.doc_requests`）。

## 1. 调用契约（P1）
| 结论 | 来源 |
| --- | --- |
| POST /snapshot；请求体 = UTF-8 纯文本 XML；Content-Type: text/plain；响应 = 二进制 PNG；错误 JSON code/message/requestId；429/503 看 Retry-After | **★ ai-guide.md（实取，3718B）** `tmp/20261016T164020-m1/docs/ai-guide.txt`；另配 openapi.yaml 提示 |
| X-Request-Id / Server-Timing 可用于单请求追踪 | ai-guide.md + 本任务各渲染响应（renders/*.resp 头部记录） |
| GET /fonts 返回 text/plain 每行一个字体族 | ai-guide.md；套内缓存 `docs/fonts-list.txt`（Noto Sans Mono CJK SC 可用于代码印刷） |

## 2. 布局（P2）
| 结论 | 来源 |
| --- | --- |
| 画布尺寸由布局决定；Snapshot 自身不带宽高 | ai-guide.md（要点节）；`docs/layout.txt`（根出图仍需非零宽高） |
| BoxConstraints：父给约束、子报尺寸；Expanded 仅 Flex 直接子级有意义 | `docs/layout.txt`（父给约束、Flex 布局、Stack 定位三节） |
| Expanded flex=2:1 → 剩余宽度 2/3 与 1/3 分配 | **★ /widgets/layout/expanded/（404 一次后 200，56,627B）** `docs/expanded.txt` |
| Row/Column 主轴分布与交叉轴属性（mainAxisAlignment 等） | `docs/widgets.raw`（Row、Column 与 Flex 节） |

## 3. 文本（P3）
| 结论 | 来源 |
| --- | --- |
| 解析器无 HTML 实体解码；<、& 入 CDATA；文本按原始内容处理 | `docs/parser.txt`（处理流程；CDATA 节） |
| Raw 保留原空白；可与行内样式混排；装饰属性于子标签整体替换 | `docs/parser-text.txt`（完整示例：描边与装饰线；阴影与字体特性） |
| 行内样式 span 标签 = `<Raw>`（非 `<Span>`——首版 PARSE_ERROR 实证） | `docs/parser-tags.txt`（Raw = 行内多个·保留空白）+ 本任务 400 记录 |
| 8 位色 #RRGGBBAA 末两位 alpha | **★ ai-guide.md**；`example-03` 右块 40% 实证 |

## 4. 滤镜与交付（P4）
| 结论 | 来源 |
| --- | --- |
| BackdropFilter = 对背后已绘内容模糊（毛玻璃），背后须有内容；ImageFiltered = 子树结果整层模糊；均 sigmaX/sigmaY/tileMode | `docs/painting.txt`（透明度与颜色滤镜节） |
| ClipRRect borderRadius + clipBehavior=ANTI_ALIAS 限定滤镜区域 | 套内已验证先例：`outputs/20261016T164020-m1/A03/system-pulse.snapshot`、`A10/compositing-lab.snapshot` |
| 交付留痕：PNG+同名 .snapshot 成对、不后处理、整图+放大自检 | 总 AGENTS.md（目录与产物/留痕与过程统计）+ 本题 iterations 记录 |

## 5. 相对几何一致性（核心子树 1:1）
- 核心子树为示例文件 4..(n-2) 行（根 Stack 内全部定位子项），教学页嵌入的本地 Stack 中字符串逐字节相同（各页 `examples.json` 内 embed_md5 / embed_verbatim_match=true 为证）；
- 教学页包装差异仅两类（框背景 + 底色容器），已在每例 wrapper_diff 声明。
