# A23 交付能力与限制

依据实际成功取得并缓存的 service guide、OpenAPI、Parser 标签参考和 fonts；本次仅复用，新增 HTTP 为0。结论范围为当前公开类 DOM DSL 与 open-snapshot HTTP 契约，未测试未记录参数，不代表所有底层 Kotlin/Skia 扩展能力。七张真实服务PNG与对应完整DSL已生成；root实际打开全部原图和接触表，六帧alpha检查通过。

| 请求 | 当前文档化原生支持 | 已授权交付／替代 | 外部后续 |
|---|---|---|---|
| 文字可编辑 SVG | 契约未提供：当前公开类 DOM DSL 与 HTTP 输出契约未提供 SVG 导出；PNG 内文字为像素，不能称为可编辑 SVG。 | 1200×800 PNG 封面与完整 cover.snapshot，保留源码中的可修改 Text/Raw。 | 如仍需 SVG，需在独立矢量工具或另一导出流程中重建几何与可编辑 text 节点、确认字体可用性；本次不矢量化、不伪造 .svg。 |
| CMYK 印刷稿 | 契约未提供：当前公开 DSL/HTTP 契约未暴露 CMYK、印刷 ICC、输出色分离或软打样参数；只能如实交 RGB 家族栅格 PNG。 | RGB/RGBA PNG 封面和原始 DSL；颜色模型、是否有 alpha 与 ICC metadata 以实际 PNG 检查为准，不宣称特定嵌入配置。 | 如仍需印刷稿，需在外部颜色管理流程中按印厂给定 ICC profile 转换、检查总墨量/黑版/打样，并确认分辨率、出血与交付格式；本任务不执行转换。 |
| 6 帧透明 GIF 动画 | 契约未提供：GIF 不在 Snapshot 根 type 枚举或 HTTP 成功图片 MIME 中；没有原生多帧 GIF 导出约定。 | 6 张 600×600 透明 PNG 关键帧，各有完整 .snapshot；timing.json 按250ms/帧、循环与帧序交付。 | 如仍需 GIF，可在外部使用这六张真实 PNG 和 timing.json 合成，处理调色板量化、GIF 透明索引及帧处置；需重新验证循环首尾和边缘。此处只交素材与时间说明。 |
| 透明 PNG 关键帧（已授权替代） | 支持：PNG 格式和透明画布/颜色 alpha 在实际文档中明确支持。 | frame-01…frame-06.png，尺寸600×600；主体始终为同12个单元，动画帧无文字。 | 文件本身无需额外导出；如进入外部动画流程须保留 alpha。 |
| 动画时间轴、原生播放、无缝循环 | 契约未提供：本接口公开静态场景标签与静态图片字节导出；未提供动画/timeline/frame 标签或播放控制属性。 | 参数化生成六个独立场景，frame-data.json 保存各单元 ID/颜色/尺寸/六次位置；timing.json 是外部播放器读取的顺序/250ms/循环说明。 | 外部播放器或合成器才能把静帧按时序展示为动画；若六帧首尾不连续，timing 明示循环回跳，不能宣称无缝。 |
| PNG 封面 | 支持：PNG 原生格式受支持；Text/Raw 可在封面绘制指定文案。 | 1200×800 RGB PNG 封面，主体与文字都由类 DOM DSL 构造，同时保存完整 cover.snapshot。 | 普通 PNG 交付无需后续；编辑文字需更改 DSL 并再次渲染，不能在已有 PNG 内编辑 text 节点。 |

## 文字可编辑 SVG

输出枚举 png/jpg/webp、成功响应 MIME 无 image/svg+xml；Text 支持修改 DSL 内容，并不使已编码的 PNG 文字可编辑。

依据：guide-type: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L27; openapi-response-mime: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt L116–128; parser-text-source-editable: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1

未测试未记录的格式参数，也不将 Kotlin 扩展或其他服务能力当成本任务接口能力。

## CMYK 印刷稿

已文档化的颜色是 CSS RGB/HSL/alpha，Snapshot 根参数只有 background/debug/type；输出契约没有 CMYK 或 ICC 输入。仅把后缀换成印刷格式不能证明 CMYK。

依据：guide-css-alpha: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L29; parser-rgb-and-supported-color-syntax: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1; parser-snapshot-contract: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1; openapi-response-mime: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt L116–128

这是公开接口缺少原生印刷工作流的结论；没有据文档缺失断言底层图形库永远无法转换 CMYK。

## 6 帧透明 GIF 动画

每次 snapshot() 编码一个当前 Widget 场景为 PNG/JPEG/WebP 字节，文档没有 GIF 编码、帧时长、循环或 disposal 配置。

依据：guide-type: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L27; openapi-response-mime: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt L116–128; parser-single-static-encoding: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000003-readable.txt L1; parser-snapshot-contract: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1

不把 timing.json 称为 GIF 文件，不生成空壳目标格式；文档未承诺 WebP 动画，亦不以 webp 输出冒充 GIF。

## 透明 PNG 关键帧（已授权替代）

Snapshot background 默认 transparent，可显式 background="transparent"；#RRGGBBAA 的 AA 在末两位。几何之外不绘制不透明背景。

依据：guide-type: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L27; guide-css-alpha: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L29; parser-snapshot-contract: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1; parser-transparent-color: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1

原始响应已核验：六帧RGBA PNG均600×600，透明像素至少331188/frame、alpha范围0..255；另有逐帧与接触表真实看图，不能只依据.png后缀。

## 动画时间轴、原生播放、无缝循环

38个注册标签是布局、绘制、文字、图像等静态树能力。未知属性可能被忽略，不能靠 invented duration/loop/frame 参数实现实际动画。

依据：parser-registered-tags: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1; parser-snapshot-contract: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1; parser-single-static-encoding: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000003-readable.txt L1; openapi-one-binary-result: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt L105–106

最终末帧需形成可识别图形；这依赖设计与真实看图，而不是通过单个接口产生动画。

## PNG 封面

公开接口成功返回 PNG 二进制；Text/Raw 与真实 fonts 缓存可用于“从结构到画面”。

依据：guide-formats: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L3; guide-type: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt L27; openapi-response-mime: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt L116–128; parser-text-source-editable: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt L1; fonts-inter: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-fonts-000001-readable.txt L1; fonts-noto-sans-cjk-sc: D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-fonts-000001-readable.txt L11

不宣称某个 ICC profile、印刷色域或可编辑 vector text。

## 已确认的执行边界

覆盖图与六帧主体、文字和几何均须由 DSL 构造，不嵌入预渲染帧；12个单元始终存在、颜色/数量/尺度一致，轨迹连续、末帧图形可辨识。封面指定文字“从结构到画面”，六帧没有文字。

timing.json 应保留 frame-01→frame-06 顺序、每帧250ms（周期1500ms）及循环设置；若最后一帧返回第一帧位置不同，明确说明会跳变，并记录实际首尾位移，不宣称无缝。是否满足以最终 frame-data 和实际图片为准。

PNG 透明有文档支持，但最终必须检查原始响应 PNG 的 alpha；RGB 封面不等同 CMYK 印刷。完整 .snapshot 是可修改源码，已编码 PNG 的文字不是可编辑 SVG text。

共享请求原记录：shared-doc-000001、000003、000004、000006、shared-fonts-000001，均为已有200响应。本次新增文档请求/渲染/看图均0，不在后题重复计为新HTTP。

具体引文、单行 parser 缓存的字符定位、SHA256、支持范围与待验项见 limitations-draft-v001.json；文档证据已完成；最终几何/字节链独立补审另存。

## 实际交付与播放边界

封面1200×800使用RGB色值绘制，原服务PNG IHDR颜色类型为6（RGBA），不转换服务字节；alpha以原始像素检查为准。六个透明帧使用同12个48×48青绿方块，六张静帧本身不含动画。frame-data提供连续smoothstep运动提案；timing按每帧250ms保持、周期1500ms、无限循环，6→1最大单位位移234.8297px并明确硬回跳，非无缝。未创建GIF/SVG/CMYK冒名文件。
