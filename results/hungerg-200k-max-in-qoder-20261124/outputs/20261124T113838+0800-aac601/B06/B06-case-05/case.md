# B06-case-05 · What Should I Do First?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'A chronological deadline list hides dependencies and effort, so equal urgency can conceal very different next steps. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'outline': {'due': '2026-12-02', 'weight': 20, 'effort_hours': 3, 'unlocks': ['draft']}, 'draft': {'due': '2026-12-05', 'weight': 30, 'effort_hours': 6, 'unlocks': ['peer_review']}, 'peer_review': {'due': '2026-12-08', 'weight': 10, 'effort_hours': 2, 'unlocks': ['final']}, 'final': {'due': '2026-12-12', 'weight': 40, 'effort_hours': 5}}, 'arithmetic': 'Weights sum to 100%; planned effort sums to 16 hours.', 'limitations': 'Course, dates, weights, and effort estimates are fictional. Effort is a planning estimate, not measured productivity.'}
- 受众：A university student juggling interdependent assignments
- 使用环境：Portrait study-planning poster and phone companion
- 用户目标：See which assignment unlocks others, estimate effort, and choose a realistic next action before the nearest deadline.
- 尺寸：1400×1800

## 场景与视觉选择

A dependency river from outline to final, with deadline gates and effort stones; the nearest actionable step is highlighted without implying that all tasks are equal-sized.

## 实际自检

Outline→Draft→Peer review→Final依赖完整；Dec 02/05/08/12、20/30/10/40%和3/6/2/5小时准确，总计100%与16小时；START HERE符合依赖逻辑。

查看时间：2026-11-24T18:23:16.115+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `9529289d7fdaa4519f0256d29f6d2b1ad90d1b94f2b54dbeb8b2c40cd4b10ed5`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-05-C1：Outline unlocks draft, draft unlocks peer review, and peer review unlocks final; the path is complete.；检查方法：Trace all dependency arrows and compare with demo_values.；结果：通过。
- B06-05-C2：Dates, weights, and effort estimates are accurate, sum correctly, and are labelled fictional/estimated.；检查方法：Recompute 100% and 16 hours and inspect all qualifiers.；结果：通过。
- B06-05-C3：The recommended next action follows dependency logic and is not simply the task with the largest grade weight.；检查方法：Inspect the highlighted start point and explanation.；结果：通过。
- B06-05-C4：Arrows, gates, dates, and effort labels remain readable with no crossing or clipped text.；检查方法：Review full PNG, 50% thumbnail, and crops around each gate.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
