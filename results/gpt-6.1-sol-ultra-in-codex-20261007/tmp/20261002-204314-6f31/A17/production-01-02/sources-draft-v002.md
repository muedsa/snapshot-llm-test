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

每条例子的印刷区间、exact root Widget SHA、真实响应文件及实际查看ID见 example-mapping-final-v001.json。表中相对缓存路径由 A17目录解析到 ../_suite；发布合并时应保留指向真实共享缓存的绝对或正确相对路径。

## 第 1 页 v002 修订核对

- 原常规错误/HTTP描述保留。当前服务 OpenAPI 实际缓存 `D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-readable.txt` 第 80–92 行 `/snapshot` 的 `errorImage` 参数明确：解析失败时可返回 `image/png`，HTTP 状态仍为400；第 338–346 行 BadRequest进一步说明只有解析错误走高亮PNG。页1右下卡与当前服务契约一致，无须修改。
- 字号修订：example-01 第二个 Text 由20→24；独立完整17行、印刷完整17行及教学页直接根Widget同步更新。最终映射为 `example-mapping-final-v002.json`，01使用v002，02沿用已核v001。实际前后查看与完成的两次视觉迭代见 `producer-visual-review-v002.json`。
