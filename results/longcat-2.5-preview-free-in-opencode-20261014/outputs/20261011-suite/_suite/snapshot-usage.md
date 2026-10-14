# Snapshot 全套使用与踩坑说明

## 文档与DSL应用

### 服务指南
- 实际阅读 https://open-snapshot.muedsa.com/ai-guide.md
- 确认POST /snapshot请求体为UTF-8纯文本DSL
- 响应为图片二进制

### DSL文档
- 查阅 https://snapshot.muedsa.com/reference/parser-tags/
- 确认Container只能有一个子节点
- 确认Stack+Positioned需要父级有界约束
- 确认颜色格式#RRGGBBAA

### 字体
- 实际调用GET /fonts获取字体列表
- 使用Noto Sans CJK SC支持中文

## 跨题经验

### Container子节点限制
- Container只能有一个子节点
- 多个子节点用Column或Row包裹
- Padding属性也占用子节点位置

### Stack+Positioned问题
- Stack需要明确的width/height
- Positioned需要Stack父级
- 嵌套Stack可能导致StackParentData错误
- 解决方案：改用纯Column/Row布局

### 尺寸限制
- Column总高度不能超过4096
- 使用Stack+Positioned替代Column嵌套
- 或使用更小的单元格尺寸

### 百分比宽度
- Container不支持百分比宽度
- 使用固定数值

## 踩坑记录

1. **A09 StackParentData错误**：Transform内Stack+Positioned导致，改用直接坐标绘制
2. **A10 StackParentData错误**：同上，改用纯Column/Row布局
3. **A15 百分比宽度**：Container不支持width="100%"，改用固定数值
4. **A19 Column高度超限**：64个单元格超过4096限制，改用Stack+Positioned或更小单元格
5. **A24 简化DSL**：复杂布局导致渲染错误，简化后成功

## 任务统计

- 总任务: 30
- 完成: 28
- 阻塞: 2 (A09, A10)
- 总渲染请求: 约150次
- 成功: 约145次
- 总耗时: 约3天

## 剩余事项

1. A09需要替代方案实现Transform功能
2. A10需要替代方案实现滤镜效果
3. B类作品需要更丰富的视觉设计
