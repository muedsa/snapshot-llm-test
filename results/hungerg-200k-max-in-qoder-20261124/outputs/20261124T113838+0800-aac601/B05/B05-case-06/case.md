# B05-case-06 · 在见底之前安排补药

- 状态：completed
- 品牌与数据：{'name': '同频', 'english_name': 'CAREFOLD', 'status': 'invented_concept_demo', 'patient': {'name': '林建国', 'age': 72, 'allergy': '青霉素（演示记录）'}, 'caregiver': {'name': '林岚', 'relationship': '女儿', 'role': '主要协调人'}, 'handoff_caregiver': {'name': '林澄', 'relationship': '儿子', 'role': '今晚接手'}, 'demo_date': '2026-11-24', 'medications': [{'id': 'M01', 'name': 'Amlodipine', 'strength': '5 mg', 'purpose': '血压（演示）', 'schedule': '每日 08:00 · 1片', 'times_per_day': 1, 'quantity': 22, 'color': '#D06D4B', 'shape': 'round', 'days_remaining': 22.0}, {'id': 'M02', 'name': 'Metformin', 'strength': '500 mg', 'purpose': '血糖（演示）', 'schedule': '每日 08:00 / 18:00 · 各1片', 'times_per_day': 2, 'quantity': 40, 'color': '#42776B', 'shape': 'long', 'days_remaining': 20.0}, {'id': 'M03', 'name': 'Atorvastatin', 'strength': '20 mg', 'purpose': '血脂（演示）', 'schedule': '每日 21:00 · 1片', 'times_per_day': 1, 'quantity': 18, 'color': '#D3AA47', 'shape': 'round', 'days_remaining': 18.0}, {'id': 'M04', 'name': 'Omeprazole', 'strength': '20 mg', 'purpose': '胃部症状（演示）', 'schedule': '每日 08:00 · 1片', 'times_per_day': 1, 'quantity': 12, 'color': '#607CA5', 'shape': 'round', 'days_remaining': 12.0}, {'id': 'M05', 'name': 'Vitamin D3', 'strength': '1000 IU', 'purpose': '补充剂（演示）', 'schedule': '每日 08:00 · 1粒', 'times_per_day': 1, 'quantity': 30, 'color': '#8B719B', 'shape': 'capsule', 'days_remaining': 30.0}], 'boundaries': ['不自动判断是否补服、加倍或停药', '剂量变更须由医生或药师确认', '所有人物、药品库存与记录均为演示，不构成医疗建议', '未进行真实用户研究或临床验证']}
- 受众：承担家庭用药协调的成年家属与愿意参与记录的长者
- 使用环境：女儿在平板查看库存并提交演示补药申请
- 用户目标：按每日用量估算见底日，核对后预约药店取药
- 尺寸：1024×768

## 场景与视觉选择

横向库存刻度与补药队列；数量、日数和处理状态用同一数据计算

## 实际自检

五种库存和频次一致；明确今日盘点32→40片，Metformin 40÷2=20天并进入14天提醒范围；补药仍是待药店确认的申请。

查看时间：2026-11-24T17:49:22.133+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `c787d5ee061b32ef937c73f3409e379389de16a3ce2ff192f543b9549cff0912`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B05-06-C1：五种库存与每日次数一致；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。
- B05-06-C2：Metformin 40片/每日2片=20天，处于14天提醒阈值；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。
- B05-06-C3：补药是申请而非已购或已送达，药店待确认；检查方法：打开最终服务原图，核对目标尺寸下的文字、状态、前后用例数据与操作反馈。；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
