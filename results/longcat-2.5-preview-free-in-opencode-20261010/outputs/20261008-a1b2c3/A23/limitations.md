# 格式限制说明

## 请求：文字可编辑SVG
- 支持情况：不支持
- 依据：Snapshot DSL输出为位图PNG/JPEG/WebP，不支持SVG矢量输出
- 替代：交付PNG封面
- 后续工作：需要外部工具将PNG转换为SVG

## 请求：CMYK印刷稿
- 支持情况：不支持
- 依据：Snapshot DSL输出为RGB位图，不支持CMYK色彩空间
- 替代：交付RGB PNG
- 后续工作：需要外部工具将RGB转换为CMYK

## 请求：6帧透明GIF动画
- 支持情况：不支持
- 依据：Snapshot DSL输出为静态PNG，不支持GIF动画
- 替代：交付6张透明PNG关键帧 + timing.json
- 后续工作：需要外部工具将6帧合成为GIF

## 请求：PNG封面
- 支持情况：支持
- 依据：Snapshot DSL原生支持PNG输出
- 替代：已交付1200×800 RGB PNG封面
