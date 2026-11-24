# B05-case-09 · 取药后，再核对一次

- 状态：completed
- 品牌与数据：{'name': '同频', 'english_name': 'CAREFOLD', 'status': 'invented_concept_demo', 'patient': {'name': '林建国', 'age': 72, 'allergy': '青霉素（演示记录）'}, 'caregiver': {'name': '林岚', 'relationship': '女儿', 'role': '主要协调人'}, 'handoff_caregiver': {'name': '林澄', 'relationship': '儿子', 'role': '今晚接手'}, 'demo_date': '2026-11-24', 'medications': [{'id': 'M01', 'name': 'Amlodipine', 'strength': '5 mg', 'purpose': '血压（演示）', 'schedule': '每日 08:00 · 1片', 'times_per_day': 1, 'quantity': 22, 'color': '#D06D4B', 'shape': 'round', 'days_remaining': 22.0}, {'id': 'M02', 'name': 'Metformin', 'strength': '500 mg', 'purpose': '血糖（演示）', 'schedule': '每日 08:00 / 18:00 · 各1片', 'times_per_day': 2, 'quantity': 40, 'color': '#42776B', 'shape': 'long', 'days_remaining': 20.0}, {'id': 'M03', 'name': 'Atorvastatin', 'strength': '20 mg', 'purpose': '血脂（演示）', 'schedule': '每日 21:00 · 1片', 'times_per_day': 1, 'quantity': 18, 'color': '#D3AA47', 'shape': 'round', 'days_remaining': 18.0}, {'id': 'M04', 'name': 'Omeprazole', 'strength': '20 mg', 'purpose': '胃部症状（演示）', 'schedule': '每日 08:00 · 1片', 'times_per_day': 1, 'quantity': 12, 'color': '#607CA5', 'shape': 'round', 'days_remaining': 12.0}, {'id': 'M05', 'name': 'Vitamin D3', 'strength': '1000 IU', 'purpose': '补充剂（演示）', 'schedule': '每日 08:00 · 1粒', 'times_per_day': 1, 'quantity': 30, 'color': '#8B719B', 'shape': 'capsule', 'days_remaining': 30.0}], 'boundaries': ['不自动判断是否补服、加倍或停药', '剂量变更须由医生或药师确认', '所有人物、药品库存与记录均为演示，不构成医疗建议', '未进行真实用户研究或临床验证']}
- 受众：承担家庭用药协调的成年家属与愿意参与记录的长者
- 使用环境：儿子在药袋交付点核对演示药品
- 用户目标：比对取药清单、数量和待药师确认的标签差异
- 尺寸：390×844

## 场景与视觉选择

手机取药凭证与逐项勾选；凭证码为演示图形，异常状态不被绿色掩盖

## 实际自检

Metformin 500mg、40片与补药队列一致；演示凭证和药店明确非真实交易，标签差异待药师核对，不擅自改变服用方式。

查看时间：2026-11-24T17:49:22.169+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `8e83f45b5be62d54a83b8cd9383f2965fdb1a3de8a6fd032abf4388b4d69b114`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B05-09-C1：取药药品和数量与案例06补药队列一致；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。
- B05-09-C2：标签差异保留待确认，不擅自判断可以服用；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。
- B05-09-C3：演示凭证码和药店信息明确非真实交易；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
