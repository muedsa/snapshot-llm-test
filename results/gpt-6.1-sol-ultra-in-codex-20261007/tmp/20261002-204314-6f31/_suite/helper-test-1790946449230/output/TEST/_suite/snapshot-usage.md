# Snapshot 全套实际使用报告

运行：TEST；生成时间：2026-10-02T13:07:29.291Z；配置：all；状态：in_progress。
当前题：无；轮次：无；用例：无。
实际输出目录：D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/helper-test-1790946449230/output/TEST。实际临时目录：D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/helper-test-1790946449230/temp/TEST。

状态数量：completed 1，in_progress 0，partial 0，blocked 0，pending 0。
已登记最终 PNG 1；独立创作用例 0；实际渲染请求 1（成功 1，失败 0）；文档请求 1；其他服务请求 0；完整视觉迭代 0；未完成视觉迭代 0；实际查看记录 1。

## 真实文档与 DSL 应用

下面的实际阅读/应用来自执行者保存的 shared-applications 记录；单纯取得文档响应不被当作已经阅读或应用。相同缓存跨题复用不新增 HTTP 请求。
尚无共享应用声明记录；已下载文档只能作为缓存证据列出。

## 缓存与真实请求证据

|范围|请求 ID|类型|HTTP|原始响应|
|---|---|---|---|---|

## 实际工具与方法

尚无实际辅助工具应用记录。

所有最终图片保留原服务 PNG 字节并与完整同名 .snapshot 配对；本报告生成器读取留痕，不代替执行者的实际图像查看。

## 逐题状态与产物

|任务|状态|最终图/独立用例|渲染成功/失败|DSL/看图|完整/未完视觉迭代|入口|
|---|---|---|---|---|---|---|
|A01|completed|1/0|1/0|1/1|0/0|[单题报告](../A01/snapshot-usage.md)|

## 可观察问题、修复与验证


真实失败响应：
- A01-request-000002 HTTP 400：{"code":"TEST_ONLY"}；[保留响应](../../../temp/TEST/A01/requests/A01-request-000002/response.json)。

## 三轮预置与复用范围

A21/A22按第一轮归档后再执行第二、第三轮。轮次需求可提前访问，此模式不声称隐藏反馈盲测。每轮图像、DSL、报告、指标与变化证据分别归档；总指标只累计各题顶层加 shared，轮次/用例明细不再次相加。

## 总审查与剩余事项

TEST FIXTURE ONLY; this is not actual visual inspection.

所有题状态均为 completed；是否全套可最终交付仍需总审查记录与实际视觉审查结论支持。

恢复检查点：[最新不可覆盖状态快照](../../../temp/TEST/_suite/checkpoints/state-000002.json)。恢复同一运行时沿用 TEST，核对实际产物与日志后从未完成处继续。

## 真实消耗与计量边界

总墙钟起点：2026-10-02T13:07:29.231Z；结束：仍在执行；当前墙钟 0.06 秒。
实际请求耗时之和（shared 加每题日志）：0.017675999999999994 秒；此值不等于总墙钟。
真实 token、图像输入计费与金额：null。原因：The tools/service did not provide actual model token, image input, or billing consumption for this run.
完整消费汇总：[task-metrics.json](task-metrics.json)。已下载缓存、测试夹具与仅复用文档不作为新真实服务请求累计。
