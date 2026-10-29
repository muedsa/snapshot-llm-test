# case-06 · 召回：我的盒子中招了吗？

- 受众：家庭冰箱前的消费者
- 使用场景：冰箱门 800×1100 卡
- 用户目标：核对自己的批号并知道下一步
- 内容依据：召回公告的批号/行动结构；品牌与批号为虚构
- 视觉意图：A1–A12 批号格，A7–A9 实心红；三步行动
- 尺寸：800×1100
- 主图：`final.png`；DSL：`final.snapshot`
- 最终请求：`daaacf826521`；累计请求 2（成功 2，失败 0）
- DSL 能力：批号网格、区间高亮、编号步骤、截止日期
- 计划版本：`tmp/run-20261029-110525/B06/plan-v1.md`（13:12）

## 自检与修改

- 首轮观察：首版只把区间端点 A7、A9 标红，A8 仍是白格，与“A7–A9 受影响”矛盾。
- 修改：A7、A8、A9 三格全部实心红。
- 实际查看：2 次；最后 13:17。

## 完成标准与结果

- `E1` 标题/开头在 3 秒内说清原来卡在哪、现在给什么答案 → PASS（首屏结论与标题）
- `E2` 所有数字与 data.json 一致；演示/非建议声明可见 → PASS（逐项复算与 data.json）
- `E3` 先结论、再依据、后细节；目标尺寸下正文 ≥12px（远距离媒介按比例放大） → PASS（viewed at 800×1100）
- `E4` 给出明确下一步（可以停/别跑/退掉/问这 5 句/投哪个桶） → PASS（结尾给出下一步）
- `E5` 无文字重叠、裁切、误遮；实际查看最终 PNG → PASS（viewed 2 times; last 13:17）
- `S06` A7、A8、A9 三格全部高亮；行动三步与退款截止日可见 → PASS（A7、A8、A9 三格全部高亮；行动三步与退款截止日可见）

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [portfolio.md](../portfolio.md)
- [problem-evidence.json](../problem-evidence.json)
- [design-review.md](../design-review.md)
