# 首次可用图择取时序修复

已只读核验真实 A07 当前最终图与请求日志，证据：first-usable-order-evidence-000001.json。该次 supersession 后，countsFor 的最新 phone 位于数组首位，但其成功请求完成于2026-10-03T17:24:06.175Z，map 成功请求完成于17:19:33.033Z。因此按数组第0项选时间确有错误，会因为同路径替代作品保留Map插入顺序而忽略更早的当前最终图。

root授权后备份完整当前 suite.cjs 为 suite-first-usable-before-000001.cjs，仅修改 writeTaskMetrics 中 first 的择取：对每张当前最终图以 request_id 匹配真实成功请求，从具有已知有效 ended_at 的集合选最早时间；没有任何已知匹配时间返回null，不再使用 artifact 登记时间替代服务完成时间。

此修复按root指定范围采用“当前最终图中最早真实成功请求时间”，没有扩大成历史退役候选的首个可用时间、没有推断看图前是否可用，也没有估算未知时间或费用。首次时间字段继续由root正常刷新指标时计算；API与其他指标逻辑保持不变。

只执行 node --check，语法检查通过。本代理未执行 writeTaskMetrics、未写suite-state/历史检查点/真实指标，未读或执行后续题。
