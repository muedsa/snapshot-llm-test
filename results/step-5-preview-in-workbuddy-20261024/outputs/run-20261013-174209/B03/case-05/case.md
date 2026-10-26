# case · 05 · 自适应信息亭界面设计稿

- 画布：1920×1080（16:10 设计稿纸）
- 受众：园区触摸屏信息亭的界面设计评审者
- 使用场景：同一信息架构在三种屏宽下的呈现（设计提案稿）
- 使用目标：证明一套 Flex 结构在 1000/480/260 三档宽度均成立
- 主导手法：Flex 弹性布局（Row/Column/Expanded/Flexible/Spacer + SPACE_BETWEEN/AROUND/EVENLY + crossAxisAlignment=STRETCH）+ AspectRatio / FractionallySizedBox / ConstrainedBox 约束构件
- 视觉主张：三台信息亭并列 + 注释卡片 + 主轴分布点阵对比 + 约束构件的像素标注
- 内容依据：鹭洲湿地公园触摸屏信息亭 V2 设计稿（虚构项目演示）；磁贴内容取自 B02 规范数据
- 最终版本：case-05-v02（request_id 4adb21e0-3a1f-4ce0-bbb7-38ed6972b475，耗时 2.969s，DSL 24364B）

## 完成标准与实际结果

### C05-1 三种宽度布局全部成立且磁贴数随宽度变化
- 实际结果：已达成
- 检查方法与证据：view-zoom：宽 1000 一行四磁贴 / 中 480 2×2 / 窄 260 纵排；pixel：各磁贴边界与 Column flex 分配（620-60-29-3×10=501）一致

### C05-2 约束构件按标注渲染：AspectRatio/FSB/ConstrainedBox
- 实际结果：已达成
- 检查方法与证据：pixel：AspectRatio 2.5 → 150×60；FSB .55×.6 → 橙块 121×36 居中；ConstrainedBox → 240×40（v02 修复：紧约束父级下 maxWidth 失效，改 Align 松约束父级，probe5 实证）

### C05-3 主轴分布点阵对比可见：三种 SPACE_* 分布直观可辨
- 实际结果：已达成
- 检查方法与证据：view-zoom：注释卡三点阵（BETWEEN/AROUND/EVENLY）间距差异清晰

### C05-4 全部尺寸为像素浮点（服务端不接受百分比）
- 实际结果：已达成
- 检查方法与证据：dsl：v01 的 width="100%" 等 7 处 PARSE_ERROR 后全部改 px；dsl_check 矩阵/实体/标签换行复检 0 问题

## 渲染与迭代记录

- 渲染请求：17 次（成功 2，失败 15，均经自检拦截/参数修复/重试后成功）
- 版本链：v01 → v02（最终 v02）
- 迭代要点：v01 渲染前拦截 7 处百分比尺寸；v02 修 ConstrainedBox 紧约束失效（probe5 实证）
- [B03-c05-i01] syntax-fix：Positioned/Container 使用百分比尺寸（width="100%"等 7 处）——全部探测与 B02 用例从未实证百分比，服务端 PARSE_ERROR：属性值无效 [width] 元素 <Positioned>（offse…
- [B03-c05-i02] visual-defect：注释区 C ConstrainedBox 演示条渲染为 476px 通栏而非标签所述 maxWidth 240 —— 紧约束父级（Positioned 476×34）与 maxWidth=240 合并后 minWidth>maxWidth …
- 实际看图：整图、宽屏磁推行、中屏 2×2、窄屏纵排、注释卡 A/B/C、主轴点阵对比
- 字节核对：final.png 与服务响应 MD5 一致（75a466e61e31…）；final.snapshot 完整自包含（8264bfe948da…）

## 未解决问题

无
