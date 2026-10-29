# B04 · 作品集

《从文本到图片》是一组十页的开发者图鉴：把 Snapshot 从请求、解析、约束、文字、装饰、Flex、Stack、Transform、滤镜到错误处理串成一条可顺序阅读的视觉叙事。每页保持同一网格与配色，用一张自制示意图承担解释，不嵌入任何外部图片。

## 十件作品

### 01 · 请求：从文本到图片

- 受众：初次接入 Snapshot 的服务端开发者
- 场景：接入评审会的单页说明，或新成员入职资料
- 用户目标：十分钟内弄清请求体、成功响应与失败响应的类型
- 内容依据：ai-guide.md 的最小示例与错误处理；本套件真实 /snapshot 请求记录
- 视觉意图：从左到右的请求流程图：深色输入、品牌绿服务、赭色输出；留白给讲稿
- 尺寸：1200×1500
- 图片：`case-01/final.png`；DSL：`case-01/final.snapshot`

### 02 · 词法、元素树与组件树

- 受众：需要定位解析错误的框架维护者
- 场景：内部技术分享的解析流程页
- 用户目标：理解 tokenizer、Element 树、Widget 树到 RenderBox 的层次
- 内容依据：parser.md 的『进阶：处理流程』与『文本与 CDATA』；本轮实体显示问题的实际修复
- 视觉意图：三个标签 chip 汇聚到 Element/Widget 两棵树，再落到 Skia 画布
- 尺寸：1200×1500
- 图片：`case-02/final.png`；DSL：`case-02/final.snapshot`

### 03 · 约束与尺寸

- 受众：负责响应式布局的界面工程师
- 场景：布局调试手册的第一页
- 用户目标：记住约束向下传、尺寸向上回，以及有界主轴的前提
- 内容依据：parser-tags.md 的 Snapshot、Row 与 Column、约束与溢出
- 视觉意图：四层同心矩形表现约束逐层收缩，右侧三行短说明
- 尺寸：1200×1500
- 图片：`case-03/final.png`；DSL：`case-03/final.snapshot`

### 04 · 文字与字体度量

- 受众：品牌与字体工程师
- 场景：字体排印规范的插图页
- 用户目标：分清字号、行高、基线与降部，不把文字盒中心当基线
- 内容依据：parser-text.md 的字体与度量、基线与混排、平台与字体一致性
- 视觉意图：放大的 Ag 字形与 ascent/baseline/descent 三条度量线
- 尺寸：1200×1500
- 图片：`case-04/final.png`；DSL：`case-04/final.snapshot`

### 05 · 装饰：颜色、圆角与渐变

- 受众：视觉设计师
- 场景：设计系统颜色与装饰规范页
- 用户目标：掌握 #RRGGBBAA 的 alpha 位置与线性渐变参数
- 内容依据：parser-tags.md 的 Container、渐变属性表与示例
- 视觉意图：五枚圆角色样 + 一条三段线性渐变条，直接展示而非描述
- 尺寸：1200×1500
- 图片：`case-05/final.png`；DSL：`case-05/final.snapshot`

### 06 · Flex：剩余空间从哪来

- 受众：组件库作者
- 场景：布局组件说明页
- 用户目标：知道 flex 份额如何分配剩余空间、Spacer 为何不绘制
- 内容依据：parser-tags.md 的 Row 与 Column、Expanded/Flexible/Spacer
- 视觉意图：三条概念说明配一条 fixed 120 + flex 1 + flex 2 的分配条
- 尺寸：1200×1500
- 图片：`case-06/final.png`；DSL：`case-06/final.snapshot`

### 07 · Stack 与绝对定位

- 受众：仪表盘与画布式界面开发者
- 场景：固定画布布局入门页
- 用户目标：理解 Stack 的叠放顺序与 Positioned 的四边定位
- 内容依据：parser-tags.md 的 Stack、Positioned 与固定尺寸说明
- 视觉意图：两张错位色块展示层叠与固定画布，底部两行短注
- 尺寸：1200×1500
- 图片：`case-07/final.png`；DSL：`case-07/final.snapshot`

### 08 · Transform：矩阵而非角度

- 受众：动效与图形实验者
- 场景：变换 API 速查页
- 用户目标：记住 16 个列主序数字、origin 与不改变布局尺寸的语义
- 内容依据：parser-tags.md 的 Opacity 与 Transform
- 视觉意图：旋转 30° 的方块作为唯一主角，配矩阵与裁剪提示
- 尺寸：1200×1500
- 图片：`case-08/final.png`；DSL：`case-08/final.snapshot`

### 09 · 滤镜与裁剪的语义

- 受众：视觉特效设计师
- 场景：滤镜能力演示页
- 用户目标：区分 ImageFiltered 的子树模糊与 BackdropFilter 的背景模糊
- 内容依据：parser-tags.md 的 ColorFiltered/ImageFiltered/BackdropFilter 与 ClipRRect；本轮真实像素结果
- 视觉意图：同一条纹带的清晰、子树模糊、背景模糊三种状态并置
- 尺寸：1200×1500
- 图片：`case-09/final.png`；DSL：`case-09/final.snapshot`

### 10 · 错误、重试与可复现交付

- 受众：发布与 QA 工程师
- 场景：交付检查清单页
- 用户目标：按 code 分类处理错误，并把失败证据与最终图一起归档
- 内容依据：ai-guide.md 的错误处理；本套件失败响应的实际留档
- 视觉意图：深色终端风格错误 JSON，配三条处置说明
- 尺寸：1200×1500
- 图片：`case-10/final.png`；DSL：`case-10/final.snapshot`

