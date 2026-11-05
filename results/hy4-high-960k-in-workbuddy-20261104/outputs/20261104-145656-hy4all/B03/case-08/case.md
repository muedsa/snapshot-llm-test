# case-08 · 折光 · 建筑玻璃样板册页

## 场景

- 受众：建筑师与幕墙材料选型客户
- 使用环境：材料样板册单页 / 客户提案附页
- 使用者要完成的事：理解玻璃层叠的折射观感并读出材料参数
- 尺寸：1000 × 1400

## 内容

- 内容来源：自拟虚构品牌与参数
- 主要信息：见最终图中标题、说明、数值区与脚注。

## 视觉选择

- 视觉主张：四块倾斜半透明玻璃板叠影产生折射与色散，下方表格给出可核查参数
- 独到手法：Transform 旋转矩阵倾斜玻璃板 + gradientRotation 斜向高光 + 8 位半透明叠层 + 边缘色散线
- 实际使用能力：Transform(matrix)/gradientType=LINEAR(gradientRotation,#RRGGBBAA)/ImageFiltered/line(opacity)/ClipRRect 不适用→Container borderRadius/表格

## 素材情况

纯 DSL 构造，无外部图片素材；品牌、数值与文案为自拟演示内容。

## 实际自检

打开 `outputs/<run_id>/B03/case-08/final.png` 实际逐区查看。首版即达标，未作修改。最终逐区查看：4 块 Transform 倾斜的半透明玻璃板、gradientRotation 斜向高光、3 条色散细线、模糊阴影、「材料参数」4 行 8 字段表格、深色 ATELIER LUMEN 信息条与富文本说明全部清晰，浅底深字对比充分，无裁切或重叠。通过。

- 尺寸（PNG IHDR 实测）：1000 × 1400
- 实际渲染请求 ID：B03-final-56953-0, B03-final-43821-0
- 完成标准：case-08-C1、case-08-C2、case-08-C3、case-08-C4 全部 passed（见 portfolio.json 的 criterion_results）
- 素材：纯 DSL，无外部素材；品牌与数值为自拟演示内容。


