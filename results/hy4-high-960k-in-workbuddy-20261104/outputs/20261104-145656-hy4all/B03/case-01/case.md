# case-01 · 潮汐 · 当代艺术展海报

## 场景

- 受众：美术馆观众与社交媒体浏览者
- 使用环境：展馆入口竖版印刷海报 / 手机竖屏推送
- 使用者要完成的事：快速识别展名、档期、地点并被氛围吸引到馆
- 尺寸：900 × 1300

## 内容

- 内容来源：自拟品牌与展讯（虚构演示）
- 主要信息：见最终图中标题、说明、数值区与脚注。

## 视觉选择

- 视觉主张：以模糊月晕与多层贝塞尔波浪构成潮汐节律，标题压在浪上形成纵深
- 独到手法：ImageFiltered 高斯模糊辉光 + RADIAL 渐变月盘 + 5 层 8 位透明 ClipPath 贝塞尔波浪 + 富文本混排
- 实际使用能力：Snapshot/Stack/Positioned/Container/gradientType=LINEAR,RADIAL/ImageFiltered/Opacity/ClipPath(C 曲线,#RRGGBBAA)/Text 嵌套 + Raw + WidgetSpan/富文本

## 素材情况

纯 DSL 构造，无外部图片素材；品牌、数值与文案为自拟演示内容。

## 实际自检

打开 `outputs/<run_id>/B03/case-01/final.png` 实际逐区查看。v1 首版底部最浅青色波浪上的浅蓝白文字（票价/主办/网址/右栏）对比不足；v3 改为深墨色 #0A3A52 后清晰。最终逐区查看：深蓝渐变夜空与星点、ImageFiltered 模糊月晕、RADIAL 渐变月盘、5 层 8 位透明贝塞尔波浪、大标题「潮 汐」、副标与英文、日期场馆票价策展、富文本说明全部完整，标题压在波浪上仍清晰，无裁切、重叠或遮挡。通过。

- 尺寸（PNG IHDR 实测）：900 × 1300
- 实际渲染请求 ID：B03-final-21774-0, B03-final-1528-0
- 完成标准：case-01-C1、case-01-C2、case-01-C3、case-01-C4 全部 passed（见 portfolio.json 的 criterion_results）
- 素材：纯 DSL，无外部素材；品牌与数值为自拟演示内容。


