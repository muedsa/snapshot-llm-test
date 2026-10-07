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
