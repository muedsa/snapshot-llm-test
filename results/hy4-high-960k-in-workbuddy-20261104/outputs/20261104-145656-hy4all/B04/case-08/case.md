# case-08 · 卫星与环 · 数量极不平均

## 场景

- 受众：科普读者
- 使用环境：科普读物 / 展板
- 使用者要完成的事：读出卫星数、环系统与磁场的分布差异
- 尺寸：1600 × 1000

## 内容

- 内容来源：S1 表 Number of Moons、Ring System?、Global Magnetic Field? 行；S2 IAU 口径；合计为编辑求和
- 关联 claim_id：C18, C19, C20, C21, C28（逐条定位、口径与 basis_type 见 `sources.json`）
- 本图所有事实/数值主张均已分配 claim_id；编辑计算与解释已单独标注。

## 视觉选择

- 视觉主张：同一线性刻度的卫星条 + 环/磁场图标，突出 3 颗 vs 413 颗
- 独到手法：线性渐变条 + 椭圆环图标（borderRadius）+ 磁场色点 + 富文本结论
- 实际使用能力：gradientType=LINEAR/Container(borderRadius 环)/circle/text/rich Raw

## 素材情况

纯 DSL 构造，无外部图片素材；无演示数据。

## 实际自检

打开 `outputs/<run_id>/B04/case-08/final.png` 实际逐区查看。首版即达标。逐区查看：8 行卫星条 0/0/1/2/95/274/28/16（前两颗标「无」）、后四颗椭圆环图标、磁场绿点与「无全球磁场」文字、内 3 颗 / 外 413 颗结论、IAU 确认数与 2025-03-18 快照口径脚注完整。地球与火星的细条是 0–274 线性刻度下的真实表现，未夸大。通过。

- 尺寸（PNG IHDR 实测）：1600 × 1000
- 实际渲染请求 ID：B04-final-63043-0
- 关联 claim_id：C18, C19, C20, C21, C28（逐条定位见 sources.json）
- 完成标准：case-08-C1、case-08-C2、case-08-C3、case-08-C4 全部 passed（见 portfolio.json 的 criterion_results）
- 数据一致性：verify_data.py 从研究存档复算 17 项全部通过，图中数值未被改动；编辑计算与来源观点已分别标注。

