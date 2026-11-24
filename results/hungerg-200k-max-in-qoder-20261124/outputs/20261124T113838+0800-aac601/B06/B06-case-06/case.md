# B06-case-06 · Is This Kind of Damage Covered?

- 状态：completed
- 品牌与数据：{'problem_evidence': "Policy wording is organized by legal sections rather than the user's event; exclusions and conditions are hard to connect to a real scenario. Design hypothesis only.", 'type': 'fictional demonstration', 'demo_values': {'event': 'Burst pipe damages kitchen floor', 'relevant_section': 'Section 4: Sudden accidental water escape', 'exclusion_to_check': 'Gradual leakage exclusion', 'documents': ['photos', 'plumber report', 'receipts'], 'outcome': 'Needs adjuster review; no coverage decision is claimed.'}, 'limitations': 'Policy language and scenario are fictional and simplified. The artwork must state that it is not legal advice or a real coverage determination.'}
- 受众：A policyholder trying to understand a home-insurance scenario before calling support
- 使用环境：Portrait decision guide beside a fictional policy summary
- 用户目标：Follow a scenario from event description to relevant policy section, exclusions, documentation, and the next question to ask.
- 尺寸：1300×1700

## 场景与视觉选择

A branching scenario tree that narrows from event to policy section to exclusion check, ending in a document checklist rather than a false yes/no verdict.

## 实际自检

爆管事件连接到Section 4、渐进渗漏排除项、三类证明和需理算员审查；未作赔付/拒赔判断，虚构政策与非法律建议警示显著。

查看时间：2026-11-24T18:23:16.129+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `b86fa78751ee6ffa2e2b39fc08ec904f63ecc220d62792051b7e55322447f3d1`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-06-C1：The scenario, relevant section, exclusion check, documents, and next step form one traceable path.；检查方法：Trace the tree from event to outcome and compare with demo_values.；结果：通过。
- B06-06-C2：The outcome does not say covered or denied; it says needs adjuster review and explains why.；检查方法：Inspect the terminal node and all outcome wording.；结果：通过。
- B06-06-C3：Fictional-policy and not-legal-advice notices are visible and readable.；检查方法：Inspect the top/bottom notices and case metadata.；结果：通过。
- B06-06-C4：Branches, labels, and checklist items do not overlap or imply missing policy facts.；检查方法：Inspect full PNG and crops around every branch and the terminal node.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
