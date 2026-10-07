# A17 第3、4页生产交接

全部生产写入已结束；没有发布正式产物、改suite-state、写正式报告或指标。root可读取 final-candidates-v001.json 并在真实root看图/独立审查后发布。

- handbook-03: A17-v003-handbook-03, A17-request-000016, 1200×1600; service meta: D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A17\requests\A17-request-000016\render-result.json; producer views: A17-view-000046。
- handbook-04: A17-v003-handbook-04, A17-request-000015, 1200×1600; service meta: D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A17\requests\A17-request-000015\render-result.json; producer views: A17-view-000041。
- example-03: A17-v002-example-03, A17-request-000012, 400×240; service meta: D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A17\requests\A17-request-000012\render-result.json; producer views: A17-view-000038。
- example-04: A17-v002-example-04, A17-request-000014, 400×240; service meta: D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A17\requests\A17-request-000014\render-result.json; producer views: A17-view-000040。

入门手册统一64px边距；正文含示例说明全部至少24px，代码20px。每页印16个真源行（最大49ASCII视觉列），明确省略其他行。完整独立例与手册插图是相同根Widget，未用Image；最终每个400×240局部与独立例RGBA逐像素相同。

修订：04短源行说明修复裁切；03底部alpha说明和04例标题20→24px同步独立例/页；03源行范围改5–8、10–17、20–21、23–24，以准确标明第9行省略。初版和所有尝试原样保留。真实10次render全部200/image/png成功；6次完整视觉迭代；生产方真实20次查看；没有新文档HTTP（8份官方缓存已实际读）。旧local-command-failure-v001.json仍保留，非HTTP请求。未知token/费用null。

供root合并：examples-final-draft-v001.json（完整source/真行号/省略/服务响应/实际view/exactwidgetSHA）；sources-final-draft-v002.json + sources-final-draft-v001.md（每claim实际url/cache/原请求/页/例）；final-pixel-check-v001.json（最终RGBA一致和alpha采样）；producer-summary-v002.json（最终完整生产状态）。

文件完整性与像素比较只作为证据，内容通过依赖实际视图记录；正式总审查仍由root执行。
