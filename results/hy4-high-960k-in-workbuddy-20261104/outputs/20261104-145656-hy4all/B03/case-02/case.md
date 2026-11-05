# case-02 · ORIGIN · 杯测风味轮

## 场景

- 受众：精品咖啡店杯测培训学员与吧台工作人员
- 使用环境：吧台挂图 / 培训手册单页 / 平板
- 使用者要完成的事：按色相定位风味主类目并核对该类子风味
- 尺寸：1200 × 1200

## 内容

- 内容来源：编辑整理的通用杯测类目（非 SCA 官方标准表）
- 主要信息：见最终图中标题、说明、数值区与脚注。

## 视觉选择

- 视觉主张：以扫描渐变色轮承载八大类目，极坐标排布标签，中心留出品读说明
- 独到手法：SWEEP 扫描渐变圆盘 + 极坐标程序化标签与刻度 + RADIAL 中心 + Transform 旋转印章
- 实际使用能力：gradientType=SWEEP(gradientStartAngle/EndAngle)/RADIAL/ClipPath/line/Transform(matrix,alignment)/circle/rich Text

## 素材情况

纯 DSL 构造，无外部图片素材；品牌、数值与文案为自拟演示内容。

## 实际自检

打开 `outputs/<run_id>/B03/case-02/final.png` 实际逐区查看。v1 首版 8 个类目的英文名与子风味在明亮 SWEEP 色轮上偏淡；v3 为每个标签加 #160E0878 深色半透明底板后全部清晰。最终逐区查看：SWEEP 多色扇形色轮、中心 ORIGIN 与说明、8 组带底板标签（中文/英文/子风味）、24 条辐射刻度、右下倾斜 CUPPING LAB 印章、底部读法说明完整，标签之间不重叠、无裁切。通过。

- 尺寸（PNG IHDR 实测）：1200 × 1200
- 实际渲染请求 ID：B03-final-27797-0, B03-final-11293-0
- 完成标准：case-02-C1、case-02-C2、case-02-C3、case-02-C4 全部 passed（见 portfolio.json 的 criterion_results）
- 素材：纯 DSL，无外部素材；品牌与数值为自拟演示内容。


