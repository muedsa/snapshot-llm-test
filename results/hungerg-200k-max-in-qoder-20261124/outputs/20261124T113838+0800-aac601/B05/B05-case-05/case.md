# B05-case-05 · 漏服了，先别加倍

- 状态：completed
- 品牌与数据：{'name': '同频', 'english_name': 'CAREFOLD', 'status': 'invented_concept_demo', 'patient': {'name': '林建国', 'age': 72, 'allergy': '青霉素（演示记录）'}, 'caregiver': {'name': '林岚', 'relationship': '女儿', 'role': '主要协调人'}, 'handoff_caregiver': {'name': '林澄', 'relationship': '儿子', 'role': '今晚接手'}, 'demo_date': '2026-11-24', 'medications': [{'id': 'M01', 'name': 'Amlodipine', 'strength': '5 mg', 'purpose': '血压（演示）', 'schedule': '每日 08:00 · 1片', 'times_per_day': 1, 'quantity': 22, 'color': '#D06D4B', 'shape': 'round', 'days_remaining': 22.0}, {'id': 'M02', 'name': 'Metformin', 'strength': '500 mg', 'purpose': '血糖（演示）', 'schedule': '每日 08:00 / 18:00 · 各1片', 'times_per_day': 2, 'quantity': 40, 'color': '#42776B', 'shape': 'long', 'days_remaining': 20.0}, {'id': 'M03', 'name': 'Atorvastatin', 'strength': '20 mg', 'purpose': '血脂（演示）', 'schedule': '每日 21:00 · 1片', 'times_per_day': 1, 'quantity': 18, 'color': '#D3AA47', 'shape': 'round', 'days_remaining': 18.0}, {'id': 'M04', 'name': 'Omeprazole', 'strength': '20 mg', 'purpose': '胃部症状（演示）', 'schedule': '每日 08:00 · 1片', 'times_per_day': 1, 'quantity': 12, 'color': '#607CA5', 'shape': 'round', 'days_remaining': 12.0}, {'id': 'M05', 'name': 'Vitamin D3', 'strength': '1000 IU', 'purpose': '补充剂（演示）', 'schedule': '每日 08:00 · 1粒', 'times_per_day': 1, 'quantity': 30, 'color': '#8B719B', 'shape': 'capsule', 'days_remaining': 30.0}], 'boundaries': ['不自动判断是否补服、加倍或停药', '剂量变更须由医生或药师确认', '所有人物、药品库存与记录均为演示，不构成医疗建议', '未进行真实用户研究或临床验证']}
- 受众：承担家庭用药协调的成年家属与愿意参与记录的长者
- 使用环境：父亲09:40发现早晨一片未确认，女儿远程协助
- 用户目标：记录情况并联系药师，不自动建议补服
- 尺寸：390×844

## 场景与视觉选择

异常状态手机页；警示色只用于下一步动作，保留时间线和联系人

## 实际自检

09:40家属报告明确不是医生诊断；不自行加倍、不自动补服，联系药师和通知女儿的结果说明完整。

查看时间：2026-11-24T17:49:22.122+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `c9446c14c1acbca7be0ab3524f07ceacef986910e09cd4ae9abbd4769f0a2277`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B05-05-C1：明确不自动加倍、不自动补服；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。
- B05-05-C2：记录Metformin 08:00未确认和09:40报告一致；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。
- B05-05-C3：联系药师与通知女儿操作有合理结果说明；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
