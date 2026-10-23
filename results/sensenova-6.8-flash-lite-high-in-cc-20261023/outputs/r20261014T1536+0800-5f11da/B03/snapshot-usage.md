# B03 Snapshot 使用报告

## 文档与DSL阅读

### 实际阅读文档
- **服务指南**: https://open-snapshot.muedsa.com/ai-guide.md
- **DSL文档**: https://snapshot.muedsa.com/
- **B01/B02经验复用**: 已验证的b01_kit工具函数和渲染流程

### 实际使用的DSL能力
1. **基础形状**: rect, circle, text, text_c, text_r, line_h, line_v, stroke, fill
2. **透明度控制**: rect opacity参数（0-1），hex alpha后缀（如#FF6B6B66）
3. **圆角**: rect radius参数
4. **多边形填充**: fill(pts, color, step=3)
5. **路径描边**: stroke([(x1,y1), (x2,y2)], color, width, step)
6. **文本测量**: tw(s, fs) 宽度计算，pitch(fs) 高度计算
7. **对比度检查**: contrast(a, b) 辅助函数

## 跨题经验与踩坑

### 经验总结
1. **parts数量控制**: 
   - stroke/fill的step参数至关重要，step=1会生成过多parts
   - 大图形用step=3-5，小图形用step=1-2
   - 递归算法（分形树）需要严格控制深度和步长

2. **透明度控制**:
   - rect支持opacity参数（0-1）
   - circle/fill/stroke不支持opacity，需用hex alpha后缀
   - opacity值必须clamp到[0,1]，超过1.0会HTTP 400

3. **文字重叠预防**:
   - pitch(fs) = fs * 1.2 是文字bbox高度
   - 下一个文字y坐标必须 > 前一个y + pitch
   - 多行文字需要计算总高度

4. **几何计算**:
   - 极坐标：x = cx + r * cos(angle), y = cy + r * sin(angle)
   - 扇形多边形：圆心 + 弧线点 + 扇形顶点
   - 递归分形：depth * 0.72衰减，23°分叉

### 踩坑记录
1. **case-02**: opacity = 0.3 + density * 0.7 可能超过1.0 → clamp到min(1.0, ...)
2. **case-03**: 58531 parts > 9000 → 改用fill多边形，step=3
3. **case-05**: 32654 parts > 9000 → 减少深度到7，step=5
4. **case-08**: "2026"×"年度规划"重叠 → 调整y坐标
5. **case-10**: "18°"×"晴间多云"重叠 → 调整y坐标从+140到+152

## 总审查与剩余事项

### 总审查
- **10件作品全部渲染成功**，HTTP 200
- **60个门禁全部通过**（6/6 per case）
- **所有PNG与响应体一致**
- **所有DSL已保存为.snapshot文件**

### 剩余事项
- 无已知缺陷
- 所有数据为演示数据，已标注
- 坐标为示意性定位，非精确科学数据
