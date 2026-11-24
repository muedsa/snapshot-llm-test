# B06 设计审查

## 范围与证据边界

十件作品均为纯DSL虚构演示。问题来源于对常见信息结构的观察与设计假设，不来源于访谈、现场调研或用户实验；没有引用真实账单、房源、政策、交通、城市规则或网络测量。可观察改善仅指最终画面中的信息组织与可读性，不声称节省用户时间、提高决策质量或改变真实结果。

每件均先建立受众、场景、目标和可观察标准，再渲染；所有最终PNG均为服务原始响应。v001–v004 DSL、失败请求、原图与检查派生图保留在临时目录。

## 逐件审查

### B06-case-01 · Why Did This Month's Bill Change?

- 原卡点：A total and line items hide the bridge between last month and this month; design hypothesis only, no user study.
- 重构：把总价与流水拆成从旧总额到新总额的瀑布，并把每个变化转成下一步问题。
- 可见改善：最大变化+$34与总额+$38可在同一视觉路径上读出，变化不再隐藏在流水项中。
- 最终判断：$104+$34+$3+$1=$142与+$38一致；三项变化均有检查/提问动作。标题、总额、横轴标签、行动卡和虚构声明均可读，无遮挡或裁切。
- 未验证效果：Can a householder name the largest driver and the next useful question without reading the original statement? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-01-v003/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-02 · Can I Still Get There?

- 原卡点：A line diagram shows geography but not service state; a disruption list shows state but not journey consequence. Design hypothesis only.
- 重构：把服务状态叠在旅程网络上，用闭合段、替代巴士和换乘箭头表达可达性。
- 可见改善：目的地可达答案、换乘点和保留服务段同时可见，减少在状态与路线之间来回对照。
- 最终判断：YES答案先于细节；Harbor–Market闭合、替代巴士、Market换乘和Market–Museum列车形成完整路径；+12分钟明确为虚构估计，站点标签不被线路穿过。
- 未验证效果：Can a commuter identify the transfer point and remaining service within a few seconds? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-02-v001/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-03 · Which Home Is Actually Affordable?

- 原卡点：Listings separate rent, utilities, parking, laundry, and deposits, making the recurring total hard to compare. Design hypothesis only.
- 重构：用共享零基线的经常性成本堆栈比较完整月费，并把一次性费用移到独立区域。
- 可见改善：三个月费总额和一次性费用不在同一数量级混排，最低月费可直接排序。
- 最终判断：A/B/C月总额分别为$1,665/$1,610/$1,810，三组构成相加准确；一次性$500/$350/$600独立展示。Utilities为估计，C的$140引线标签清楚，最低月费不被表述为绝对推荐。
- 未验证效果：Can renters rank total monthly cost without accidentally counting deposits as monthly rent? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-03-v004/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-04 · The Better Price per Kilogram

- 原卡点：Pack sizes and promotion labels differ, so shoppers must normalize price and quantity mentally while also considering waste. Design hypothesis only.
- 重构：把不同规格归一化到同一把$/kg尺，同时并列现金差和使用期限。
- 可见改善：两个单位价在同一标尺上相距$0.60，规格差异不再需要心算。
- 最终判断：$5.10÷0.850kg=$6.00/kg，$3.30÷0.500kg=$6.60/kg；共同标尺的A/B点位置正确，$0.60/kg与$1.80差额及10/5天条件同时可见。
- 未验证效果：Can shoppers explain why the lower unit price may still be the wrong purchase for their household? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-04-v003/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-05 · What Should I Do First?

- 原卡点：A chronological deadline list hides dependencies and effort, so equal urgency can conceal very different next steps. Design hypothesis only.
- 重构：把截止日列表改为依赖河，先展示解锁下一步的起点，再显示权重与工时。
- 可见改善：起点由依赖关系而非权重/日期紧迫性决定，四个解锁动作方向一致。
- 最终判断：Outline→Draft→Peer review→Final依赖完整；Dec 02/05/08/12、20/30/10/40%和3/6/2/5小时准确，总计100%与16小时；START HERE符合依赖逻辑。
- 未验证效果：Can the student identify the first action and explain how it affects the final deadline? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-05-v001/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-06 · Is This Kind of Damage Covered?

- 原卡点：Policy wording is organized by legal sections rather than the user's event; exclusions and conditions are hard to connect to a real scenario. Design hypothesis only.
- 重构：把用户事件与政策条款并用场景树连接，明确哪些事实仍需理算员判断。
- 可见改善：应读条款、应查排除项和待补证据在同一路径上分组，未读条款不会被误当成结论。
- 最终判断：爆管事件连接到Section 4、渐进渗漏排除项、三类证明和需理算员审查；未作赔付/拒赔判断，虚构政策与非法律建议警示显著。
- 未验证效果：Can a reader identify which exclusion and documents matter without mistaking the guide for a coverage decision? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-06-v001/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-07 · Repair It or Replace It?

- 原卡点：Repair quotes and replacement prices are incomparable without remaining-life and warranty context. Design hypothesis only.
- 重构：把两种价格除以假设寿命并映射到同一比例弧形标尺，同时显示保修门槛和排除因素。
- 可见改善：$55与$97.50可直接比较，且立即看到四年/八年假设并非事实。
- 最终判断：$220÷4=$55/年，$780÷8=$97.50/年；$0–$120标尺和两档弧长一致，保修过期为前置门槛，能源/处置/安装/未来故障明确排除。
- 未验证效果：Can the reader state why repair looks cheaper under these assumptions and what could change that result? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-07-v002/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-08 · Where Does This Actually Go?

- 原卡点：Material symbols and accepted-item lists do not always explain condition, preparation, or special drop-off requirements. Design hypothesis only.
- 重构：把材料名称列表改为物品→准备动作→去向的六条分类传送带。
- 可见改善：六件物品的准备与去向一一对应，软袋和电池不会进入普通回收路线。
- 最终判断：六件物品均有准备动作和独立去向；软塑袋到STORE DROP-OFF、电池到BATTERY DROP-OFF；Harbor City规则明确虚构且不可作为现实指导。
- 未验证效果：Can residents correctly route the soft bag and battery without assuming all recyclable materials share one bin? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-08-v002/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-09 · What Decision Affects My Block?

- 原卡点：Agendas are ordered by procedure and department, not by who is affected or what action residents can take. Design hypothesis only.
- 重构：把议程清单改为地图节点与行动卡联动，按地点、受影响人群和评论截止日重排。
- 可见改善：每项议程的决定、影响对象和截止日在同一卡片中，地图提供空间索引。
- 最终判断：四项议程均显示地点/受影响人群、决定和Dec 01/03/04/05评论截止日；地图标为示意边界，参与说明不承诺结果改变，底部卡片已离开页脚线。
- 未验证效果：Can a resident identify one relevant item and its comment deadline without reading the full procedural agenda? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-09-v002/final-01.png`；标准逐条证据见 `final-review.json`。

### B06-case-10 · Fix the Room, Not the Whole House

- 原卡点：Router status pages report house-level connection health while users experience room-level dead zones. Design hypothesis only.
- 重构：把覆盖全屋的建议改为房间户型诊断，用读数、测试点和单变量步骤限制决策范围。
- 可见改善：弱点在Kitchen定位，行动从调整路由器开始，而非直接升级全屋设备。
- 最终判断：路由器、Living room−42、Bedroom−58、Kitchen−72 dBm与厨房测试点关联正确；先移动再重复测试再考虑Mesh，圈层不越界，虚构读数与无保证说明可见。
- 未验证效果：Can the householder identify the next test and avoid buying hardware before checking router placement? 该问题尚未经过用户实验。
- 最终证据：`tmp/20261124T113838+0800-aac601/B06/versions/B06-case-10-v002/final-01.png`；标准逐条证据见 `final-review.json`。

## 独立性与整体关系

十件作品分别使用财务瀑布、服务状态网络、成本堆栈、单位价格尺、依赖河、保险场景树、决策Dial、分类传送带、影响地图和户型诊断。它们共享一套克制的信息笔记页脚，但信息转换、决策任务和主视觉逻辑不同，不是同版式换色或换字。

## 实际修改与保留

案例01修复标题实体、标签遮挡和下注间距；案例03修复总额间距、薄段标签可见性和对比度；案例04修复标尺坐标的量纲；案例07–10分别修复标签净空、页脚净空和信号圈边界。案例02/05/06首版已符合标准，保留而不制造无意义迭代。

## 剩余事项

无已知影响交付的缺陷。未来若用于现实场景，必须替换为经核实的数据、当地规则/政策或实测信号，并另行开展用户验证；本交付不声称已完成这些工作。
