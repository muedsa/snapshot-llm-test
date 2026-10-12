# A17 技术来源与可运行例

# A17 第 1、2 页实际来源草案

读取方式：本次生产实际读取同 run 的原响应缓存，沿用既有 HTTP 请求，不重复记请求。缓存 URL 与原请求见 shared-document-read-v001.json。技术规则限定 Parser DSL / 当前服务；未把框架的 HTTP 建议映射写成当前服务契约。

| 关键结论 | 实际读取页面与缓存 | 手册 / 可运行例 |
|---|---|---|
| POST /snapshot；UTF-8 text/plain 请求体，非 JSON；成功为对应格式二进制 | https://open-snapshot.muedsa.com/ai-guide.md；../_suite/shared-doc-000001-response.txt。另核 https://open-snapshot.muedsa.com/openapi.yaml；../_suite/shared-doc-000006-readable.txt 的 /snapshot | handbook-01；example-01（此次实际 HTTP 200 image/png） |
| type=png/jpg/webp，扩展名匹配；须先查 HTTP 状态与 Content-Type | 上述指南的生成 DSL/错误处理与 OpenAPI 的响应；https://snapshot.muedsa.com/reference/parser-tags/ Snapshot 属性；../_suite/shared-doc-000004-readable.txt | handbook-01 完整 17 行；example-01 |
| 常规错误含 code、message、requestId；400/401/413；429 或部分503参考 Retry-After；X-Request-Id关联 | 指南错误处理；OpenAPI BadRequest、Unauthorized、413、429、503 与 headers。429 契约可 text/plain，因此先检查状态/类型，页中仅称“常规错误JSON” | handbook-01 下方两卡；错误字段为文档说明，未为此制造失败请求 |
| errorImage=png 默认不使用；解析错误图的 HTTP 状态仍为400 | 指南错误处理；OpenAPI /snapshot errorImage 参数与 BadRequest | handbook-01 右下卡；非示例代码 |
| 根 Snapshot/单根Widget；尺寸由布局决定，非HTML；有限且非零根图 | https://snapshot.muedsa.com/guides/parser/；../_suite/shared-doc-000003-readable.txt；https://snapshot.muedsa.com/guides/layout/；../_suite/shared-doc-000005-readable.txt；Parser tags Snapshot/Container | handbook-01/02；两个例均实际400×240 |
| Row/Column分别水平/垂直Flex；有界主轴才能计算Expanded剩余空间；Expanded是Flex直属子节点且TIGHT | Layout 的 Flex布局；Parser tags 的 Row/Column、Expanded/Flexible | handbook-02；example-02 根Container400×240、padding16、Column直接Expanded，再Row直接Expanded flex2/1 |
| Positioned直属Stack/IndexedStack；同轴left/right/width最多两项，纵向同理；Stack默认HARD_EDGE | Layout的Stack/Positioned；Parser tags 的 Stack、Positioned | handbook-02；example-02 完整代码第27–47行Stack及两个定位子项，印刷节选6–23行明确省略其余 |
| Parser文本trim，Raw保留空白；代码印刷用Raw/CDATA避免特殊字符被解为标签 | Parser的文本特殊字符与Parser tags 的 Text/Raw | 页面code由共享scaffold真实Raw/CDATA；example-01/02文字用Raw（更多说明归第3页） |
| 实际可用字体 Inter、Noto Sans CJK SC、DejaVu Sans Mono | https://open-snapshot.muedsa.com/fonts；../_suite/shared-fonts-000001-readable.txt，原字体响应为text/plain | 所有页面；代码20px DejaVu Sans Mono，正文24px及以上 |

每条例子的印刷区间、exact root Widget SHA、真实响应文件及实际查看ID见 example-mapping-final-v002.json。表中相对缓存路径由 A17目录解析到 ../_suite；发布合并时应保留指向真实共享缓存的绝对或正确相对路径。

## 第 1 页 v002 修订核对

- 原常规错误/HTTP描述保留。当前服务 OpenAPI 实际缓存 `D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-readable.txt` 第 80–92 行 `/snapshot` 的 `errorImage` 参数明确：解析失败时可返回 `image/png`，HTTP 状态仍为400；第 454–492 行 BadRequest进一步说明只有解析错误走高亮PNG。页1右下卡与当前服务契约一致，无须修改。
- 字号修订：example-01 第二个 Text 由20→24；独立完整17行、印刷完整17行及教学页直接根Widget同步更新。最终映射为 `example-mapping-final-v002.json`，01使用v002，02沿用已核v001。实际前后查看与完成的两次视觉迭代见 `producer-visual-review-v002.json`。


# 第3、4页实际阅读来源与技术映射

以下均在本次生产实际读取已有成功请求的缓存；复用不计新HTTP。完整原请求、响应和URL保持原任务归属。

- guide: [官方页](https://open-snapshot.muedsa.com/ai-guide.md)；原请求 shared-doc-000001；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\_suite\shared-doc-000001-response.txt；SHA-256 2b94151bdfa47e485de3d2412222f5b7fae5bf8b93592aeec586c5dcc1e813aa。
- parser: [官方页](https://snapshot.muedsa.com/guides/parser/)；原请求 shared-doc-000003；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\_suite\shared-doc-000003-readable.txt；SHA-256 a9f94fa732898c34591b711e1a97cf13ba208d29ca5c15c268ff90ad475e2b9f。
- parser-tags: [官方页](https://snapshot.muedsa.com/reference/parser-tags/)；原请求 shared-doc-000004；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\_suite\shared-doc-000004-readable.txt；SHA-256 821a9b55b3a2d1498faff3468ef45178a62fff2a2c11f422b7e872975706832c。
- fonts: [官方页](https://open-snapshot.muedsa.com/fonts)；原请求 shared-fonts-000001；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\_suite\shared-fonts-000001-readable.txt；SHA-256 cfa8a284dd8fe8e93167fdb9c8f1b10591571e5a9ae09538942dfc4b7e368569。
- text: [官方页](https://snapshot.muedsa.com/widgets/text/text/)；原请求 A11-request-000001；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A11\requests\A11-request-000001\readable.txt；SHA-256 20ca2df0ecc9515ac90502b06ac17c7cdc82a0aeb12d72564459a852d151e863。
- rich-text: [官方页](https://snapshot.muedsa.com/widgets/text/rich-text/)；原请求 A11-request-000002；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A11\requests\A11-request-000002\readable.txt；SHA-256 db0d620b88f2d98ccc29df64be0e4f606c42402868f88022f6843c8c41fd70a0。
- backdrop-filter: [官方页](https://snapshot.muedsa.com/widgets/painting/backdrop-filter/)；原请求 shared-request-000001；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\_suite\requests\shared-request-000001\readable.txt；SHA-256 6ad83eedba79a83d0e0b5b501a7a9f1e992a57bc0e6a79503398c0fa6568bfda。
- image-filtered: [官方页](https://snapshot.muedsa.com/widgets/painting/image-filtered/)；原请求 A10-request-000002；实际读取缓存 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A10\requests\A10-request-000002\readable.txt；SHA-256 b6f413059e5300bd2a9a5df672f8012cb5b57302338db97932ee5bfd748dcee8。

每条关键结论：

- 03-raw（第3页，example-03.snapshot，真实源行 5、6、7、8）：普通Text原始文本trim；Raw保留首尾空白/换行，只能在最外层Text行内树中。 来源 parser、parser-tags。
- 03-cdata（第3页，example-03.snapshot，真实源行 7）：CDATA用于字面< >；Parser不做HTML实体解码，&lt;原样保留。 来源 parser。
- 03-rich（第3页，example-03.snapshot，真实源行 10、11、12、13、14、15、16、17）：Parser嵌套Text是行内Span，并继承未覆盖样式；只最外层Text控制段落。 来源 parser-tags、text、rich-text。text/rich-text官方页介绍Kotlin接口；类DOM Parser的支持与属性以parser-tags的Text段落为直接依据，不声称存在RichText标签。
- 03-alpha（第3页，example-03.snapshot，真实源行 20、21、23、24）：#RRGGBBAA采用尾部alpha：FF不透明；80为128/255，当前Parser不能沿用旧AARRGGBB。 来源 guide、parser-tags。 验证：同题真实PNG红块采样；见final-pixel-check-v001.json。
- 03-fonts（第3页，example-03.snapshot，真实源行 5、10）：Inter、DejaVu Sans Mono、Noto Sans CJK SC是本服务真实字体列表中的字体。 来源 fonts、guide、text。
- 04-inputs（第4页，example-04.snapshot，真实源行 114、122、137、197）：BackdropFilter读取背后已绘制内容，前景子Widget不属于背景过滤输入；ImageFiltered以自身子树为输入。 来源 backdrop-filter、image-filtered、parser-tags。 验证：独立实际图左前景SHARP/深条清晰，右相同文本/条同blur3。
- 04-scope（第4页，example-04.snapshot，真实源行 113、114、136、137）：Parser两滤镜标签仅高斯模糊；用sigmaX/Y有限非负值，外层ClipRect限制背景读取/模糊显示区。 来源 parser-tags、backdrop-filter、image-filtered。
- 04-paint-order（第4页，example-04.snapshot，真实源行 17、65、113、114）：先画条纹后画BackdropFilter，滤镜才能读取已有背景；Clip在外层，文字前景仍清晰。 来源 backdrop-filter、parser-tags。 验证：独立完整源码里两个180×176背景先于后面的滤镜层，遵循已验证A10构造。
- 04-status（第4页，example-04.snapshot）：查看前先查状态/Content-Type和PNG签名；失败响应保留，不能JSON冒充PNG。 来源 guide。 验证：所有生产render-result.json有真实200/image/png/400×240或1200×1600，原响应未后处理。
- 04-reproduce（第4页，example-04.snapshot）：以同名完整snapshot和原PNG交付，记录固定字体、响应头/requestId及真实查看修改比较以便复现。 来源 guide、text。 验证：服务调用输入/response-headers/render-result及views/iterations；交付规范是本任务工作流要求，固定字体建议来自Text官方页。

代码印刷16个真实源行/页；源码行号在页内显示，跳过的行明确省略。完整源与省略行列表在 examples-final-draft-v001.json。所有插图为同一完整根Widget直接嵌入，未使用Image、资产或最终图后处理。


## 最终交付映射

正式[examples.json](examples.json)对应最终四例、完整源路径、精确印刷源行与省略行、真实请求及root查看ID；草案与历史均保留在本题临时目录。第1页示例v002、第2页v001、第3/4页示例v002；手册分别v002/v001/v003/v003。来源缓存的相对文字路径以临时A17目录为基准；以下提供可从正式输出使用的实际缓存链接。

- [shared-doc-000001-response.txt](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt)
- [shared-doc-000003-readable.txt](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000003-readable.txt)
- [shared-doc-000004-readable.txt](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt)
- [shared-doc-000005-readable.txt](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000005-readable.txt)
- [shared-doc-000006-readable.txt](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000006-readable.txt)
- [shared-fonts-000001-readable.txt](../../../tmp/20261002-204314-6f31/_suite/shared-fonts-000001-readable.txt)
